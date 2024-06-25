"""
Copyright © 2022 Qontigo GmbH.
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied.  See the License for the
specific language governing permissions and limitations
under the License.


Based on the GS Quant toolkit
Copyright 2019 Goldman Sachs under Apache License 2.0
"""


import inspect
import logging
from collections.abc import Mapping
from configparser import ConfigParser
from enum import unique
from pathlib import Path
from typing import Optional
import posixpath
import backoff
import httpx

from axiomapy.axiomaexceptions import (
    AxiomaAuthenticationError,
    AxiomaAuthorizationError,
    AxiomaRequestError,
    AxiomaRequestStatusError,
    AxiomaRequestValidationError,
)

from axiomapy.context import BaseContext
from axiomapy.entitybase import EnumBase

_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())


API_VERSION = "v1"
DEFAULT_APP = "REST_API"

@unique
class APIType(EnumBase):
    REST = "REST"
    BULK = "BULK"
    CEB = "CEB"


@unique
class HttpMethods(EnumBase):
    GET = "GET"
    DELETE = "DELETE"
    POST = "POST"
    PATCH = "PATCH"
    PUT = "PUT"


_RELEVANT_RESPONSE_HEADERS = [
    "Location",
    "ETag",
    "Allow",
    "X-Correlation-ID",
    "Operation-Location",
]


class AxiomaResponse(Mapping):
    """A simple wrapper on the httpx response to make easy access to key methods and
    properties
    """

    def __init__(
        self, response: httpx.Response, streaming: bool = False
    ) -> "AxiomaResponse":
        self._response = response
        self._is_streaming = streaming
        self._res_json = None
        self._props = [
            p
            for p in dir(AxiomaResponse)
            if isinstance(getattr(AxiomaResponse, p), property)
        ]

    @property
    def headers(self) -> httpx.Headers:
        return self._response.headers

    def json(self) -> Optional[dict]:
        if (
            self._response.request.method
            in (HttpMethods.PATCH, HttpMethods.GET, HttpMethods.POST)
            and "APPLICATION/JSON"
            in self._response.headers.get("content-type", "").upper()
            and not self._is_streaming
            and self._res_json is None
        ):
            self._res_json = self._response.json()
        return self._res_json

    @property
    def text(self) -> str:
        return self._response.text

    @property
    def content(self) -> bytes:
        return self._response.content

    @property
    def status_code(self) -> int:
        return self._response.status_code

    @property
    def response(self) -> httpx.Response:
        return self._response

    @property
    def is_streaming(self) -> bool:
        return self._is_streaming

    def __getitem__(self, key):
        if key in self._props:
            return getattr(self, key)
        raise LookupError(f"{key} is not a property of the class")

    def __iter__(self):
        return iter(self._props)

    def __len__(self):
        return len(self.__dict__)

    def get(self, key, default=None):
        if key in self.__dict__:
            return self[key]
        return default

    def __enter__(self):
        return self.response

    def __exit__(self, exc_type, exc, tb):
        self.response.close()

    def close(self):
        self.response.close()

    def iter_bytes(self):
        return self.response.iter_bytes()

    def iter_lines(self):
        return self.response.iter_bytes()


class HttpxLoggingHooks:
    """Provides the default logging methods for the httpx event hooks"""

    def __init__(self, application_name: str):
        self.application_name = application_name

    def log_request(self, req: httpx.Request):
        """Perform logging of the pre-request object

        Arguments:
            request {[type]}: [description]
        """

        _logger.info(f"Request: {req.method} {req.url}")

        body = getattr(req, "body", None)

        msg = "\r\n".join(
            (
                f"Method: {req.method} to {req.url}",
                "Headers:",
                "\r\n".join("{}: {}".format(k, v) for k, v in req.headers.items()),
                "Body:",
                f"{body}",
            )
        )

        _logger.debug(msg)

    def log_response(self, response: httpx.Response):
        req = response.request

        if not (response.is_stream_consumed or response.is_closed):
            # streaming
            _logger.info(
                f"Response: {req.method} {req.url} returned: {response.status_code}"
                f" is streaming."
            )

            msg = "\r\n".join(
                (
                    "Response streaming",
                    f"Method: {req.method} to {req.url}",
                    f"Status: {response.status_code}",
                    "Headers:",
                    "\r\n".join(
                        "{}: {}".format(k, v) for k, v in response.headers.items()
                    ),
                )
            )

            _logger.debug(msg)
            return None

        _logger.info(
            f"Response: {req.method} {req.url} returned: {response.status_code}"
            f" in {response.elapsed.total_seconds()}s."
        )

        body = ""
        try:
            body = response.text
        except Exception:
            pass

        msg = "\r\n".join(
            (
                f"Response in {response.elapsed.total_seconds}s",
                f"Method: {req.method} to {req.url}",
                f"Status: {response.status_code}" "Headers:",
                "\r\n".join("{}: {}".format(k, v) for k, v in response.headers.items()),
                "Body:",
                f"{body}",
            )
        )

        _logger.debug(msg)


def get_event_hooks(event_hooks: dict, async_fns: bool = False):
    hooks = {
        k: [f for f in v if inspect.iscoroutinefunction(f) == async_fns]
        for k, v in event_hooks.items()
    }
    return hooks

class AxiomaSession(BaseContext):
    """Session manager. Allows creation of a session, assignment of a session, and
    manages sessions through contexts. Wraps an httpx Client to manage aspects
    of the session. Single point of access to requests - any throttling/retry/logging
    etc can be implemented here.
    To get started call AxiomaSession.use_session(...)

    Args:
        BaseContext ([type]): [description]
    """

    __config = None

    def __init__(
        self,
        domain: str,
        proxy=None,
        certificates=None,
        api_type: str = APIType.REST,
        application_name: str = DEFAULT_APP,
        api_version: str = API_VERSION,
        event_hooks: dict = None,
        max_retries: int = 0,
        request_timeout: int = 300
    ):
        self.name = application_name
        self.event_hooks = event_hooks
        self.domain = domain if domain.endswith("/") else domain + "/"
        self.api_type = api_type
        self.api_version = api_version
        self.session_type = httpx.Client
        self._session = None
        self.proxy = proxy
        self.certificates = certificates
        self.max_retries = max_retries
        self.timeout = request_timeout


    @classmethod
    def get_session(
        cls,
        username: str,
        password: str,
        domain: str,
        client_id: str = "5ABB5D0748DF4E8EA733606B9268C3E5",
        proxy=None,
        certificates=None,
        api_type: str = APIType.REST,
        application_name: str = DEFAULT_APP,
        api_version: str = API_VERSION,
        event_hooks: dict = None,
        max_retries: int = 0,
        request_timeout: int = 300
    ) -> "AxiomaSession":
        """Gets an uninitialised session - you must call init() before this session
        can be used

        Arguments:
            client_id (str): The client id to use to create the session
            username (str): The username to create the session
            password (str): The password for the username to create the session
            domain (str): The domain of the api resources given an api url is
                            [domain][api_type][api_version][resources] or [domain][api_type]/connect/token
            api_type (str): The type of API (default is REST)
            proxy (dict|str): The proxy for the request (if required)
            max_retries (int) : Number of times to retry if request fails
            request_timeout (int) : Number of seconds till request is timed out

        Keyword Arguments:
            application_name (str): Optional label for this session
                                     (default: {DEFAULT_APP})
            api_version (str): Pass a value for the version such that
                            [domain][api_version][resources]  (default: {API_VERSION})
            event_hooks (dict): An optional set of methods to set as event hooks on
                            the httpx.Client. If none is passed an HttpxLogging hooks
                            instance is created and used to use no hooks pass {}
                            You can pass coroutines here for the async client. The set of
                            functions will be filtered and assigned accordingly.
        """
        if not isinstance(event_hooks, dict):
            hook_methods = HttpxLoggingHooks(application_name=application_name)
            event_hooks = {
                "request": [hook_methods.log_request],
                "response": [hook_methods.log_response],
            }

        return SimpleAuthSession(
            client_id,
            username,
            password,
            domain,
            proxy,
            certificates,
            api_type,
            application_name,
            api_version,
            event_hooks,
            max_retries,
            request_timeout
        )

    def init(self) -> None:
        """Initializes the http client and authenticates the session"""
        if not self._session:
            #self._session = self.session_type()
            if(self.certificates is not None and self.certificates != ''):
                self._session = httpx.Client(proxies=self.proxy, verify=self.certificates)
            else:
                self._session = self.session_type()
            self._is_authenticated = self._authenticate()
            if self._is_authenticated:
                if self.event_hooks is not None:
                    self._session.event_hooks = get_event_hooks(self.event_hooks)

    @classmethod
    def use_session(
        cls,
        username: str,
        password: str,
        domain: str,
        client_id: str = "5ABB5D0748DF4E8EA733606B9268C3E5",
        proxy=None,
        certificates=None,
        api_type: str = APIType.REST,
        application_name: str = DEFAULT_APP,
        api_version: str = API_VERSION,
        event_hooks: dict = None,
        max_retries: int = 0,
        request_timeout: int = 300
    ) -> None:
        """Gets a session, initializes it and uses as the current session ready to
        use sdk.
        Same as calling .get_session and then .init()

        Arguments:
            client_id (str): The client id to use to create the session.
            username (str): The username to create the session.
            password (str): The password for the username to create the session.
            domain (str): The domain of the api resources given an api url is
            [domain][api_version][resources] or [domain]/connect/token.
            proxy (dict|str): The proxy for the request (if required).
            max_retries (int) : Number of times to retry if request fails
            request_timeout (int) : Number of seconds till request is timed out
        Keyword Arguments:
            application_name (str): Optional label for this session.
                        (default: {DEFAULT_APP})
            api_version (str): Pass a value for the version such that
                        [domain][api_version][resources]  (default: {API_VERSION})
            event_hooks {dict}: An optional set of methods to set as event_hooks on
                            the httpx.Client. If none is passed a HttpxLogging hooks
                            instance is created and used to use no hooks pass {}
        """

        session = cls.get_session(
            client_id=client_id,
            username=username,
            password=password,
            domain=domain,
            proxy=proxy,
            certificates=certificates,
            api_type=api_type,
            application_name=application_name,
            api_version=api_version,
            event_hooks=event_hooks,
            max_retries=max_retries,
            request_timeout=request_timeout
        )
        session.init()
        cls.current = session

    @classmethod
    def _use_session(
        cls,
        host: str,
        path: str = "api/v1",
        user: str = "",
        passwd: str = "",
        proxy=None,
        grant_type="password",
        client_id="",
        protocol="http",
    ) -> None:
        """An alternative signature for .use_session to match axiomapy

        Calls AxiomaSession.use_session((
            client_id=client_id,
            username=user,
            password=passwd,
            domain=f"{ protocol}://{host}",
            api_version=path.split("/")[-1],
        )

        Args:
            host (str): [description]
            path (str, optional): [description]. Defaults to "api/v1".
            user (str, optional): [description]. Defaults to "".
            passwd (str, optional): [description]. Defaults to "".
            grant_type (str, optional): [description]. Defaults to "password".
            client_id (str, optional): [description]. Defaults to "".
            protocol (str, optional): [description]. Defaults to 'http'.
            proxy (dict|str): the proxy for the request (if required)
        """

        cls.use_session(
            client_id=client_id,
            username=user,
            password=passwd,
            proxy=proxy,
            domain=f"{ protocol}://{host}",
            api_version=path.split("/")[-1],
        )

    def __del__(self):
        self.close()

    def close(self):
        """Closes the underlying (sync) session and removes it."""

        if self._session:
            self._session.close()
            self._session = None

    def _on_enter(self):
        self.__close_on_exit = self._session is None
        if not self._session:
            self.init()

    def _on_exit(self, exc_type, exc_val, exc_tb):
        if self.__close_on_exit:
            self.close()
            self._session = None

    @classmethod
    def _config_for_environment(cls, environment="DEFAULT"):
        if cls.__config is None:
            cls.__config = ConfigParser()
            cls.__config.read(
                Path.joinpath(Path(inspect.getfile(cls)).parent, "config.ini")
            )

        return cls.__config[environment]

    def test(self) -> str:
        """Make a test call to the api $me endpoint

        Returns:
            str: text from response
        """
        print(f"Running Test on: {self.name}")
        url = f"{self.domain}{self.api_type}/api/{self.api_version}/$me"
        response = self._session.get(url)
        sub = {
            k: v
            for k, v in response.json().items()
            if k in ["userLogin", "userName", "email", "role", "lastSuccessfulLogin"]
        }
        print(f"Test completed: {str(sub)}")
        return response.json()

    def _prepare_request_args(
        self,
        method: HttpMethods,
        url: str,
        json: dict = None,
        data = None,
        params: dict = None,
        headers: dict = None,
    ):
        kwargs = {}
        req_headers = self._session.headers.copy()
        if headers:
            req_headers.update(headers)

        if method in [HttpMethods.POST, HttpMethods.PUT, HttpMethods.PATCH]:
            req_headers.update({"Content-Type": "application/json"})
        kwargs["headers"] = req_headers

        if json:
            kwargs["json"] = json

        if data:
            kwargs["data"] = data

        if params:
            kwargs["params"] = params

        full_url = url
        if not url.startswith(self.domain):
            full_url = full_url[1:] if full_url.startswith("/") else full_url
            if not full_url.startswith(f"api/{self.api_version}"):
                full_url = f"api/{self.api_version}/{full_url}"
            full_url = posixpath.join(self.domain, self.api_type, full_url)
        return full_url, kwargs

    def _prepare_response(
        self,
        response: httpx.Response,
        method: HttpMethods,
        cls: type,
        stream: bool,
        return_response: bool = False
    ):
        """A subset of the response object is returned or instances of types.
        The response will vary depending on the request type and the passed args.

        Args:
            method (HttpMethods): request method
            cls (type): type to create instances of from the response

        Returns:
            Any: [description]
        """

        if stream and False:
            return {
                "headers": response.headers,
                "iter_content": response.iter_bytes(),
                "iter_lines": response.iter_lines(),
                "status_code": response.status_code,
                "close": response.close,
            }

        if (method == HttpMethods.GET or method == HttpMethods.PATCH) and cls:
            res_json = response.json()
            items = res_json.get("items", None)
            if items is not None:
                return tuple(cls.from_dict(item) for item in items)
            else:
                return cls.from_dict(res_json)
        else:
            return AxiomaResponse(response=response, streaming=stream)

    def _handle_response_exception(
        self, response: httpx.Response, stream: bool = False
    ):
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            if stream:
                response.read()
            _logger.error(f"Response error: {response.status_code} - {response.text}")
            if response.status_code == 422:
                validation_error = response.json()
                raise AxiomaRequestValidationError(
                    message="Request failed validation - check validation errors",
                    content=response.text,
                    reason=response.reason_phrase,
                    status_code=response.status_code,
                    validation_error=validation_error,
                    response=response,
                ) from e
            else:
                raise AxiomaRequestStatusError(
                    message="Response error from request",
                    content=response.text,
                    reason=response.reason_phrase,
                    status_code=response.status_code,
                    response=response,
                ) from e

    def _authentication_failed(self, response: httpx.Response, try_auth: bool):
        if not try_auth:
            _logger.error(
                f"Authorization error: {response.status_code} - {response.text}"
            )
            if response.stream is not None:
                response.read()
            raise AxiomaAuthorizationError(
                status_code=response.status_code,
                reason=response.text,
                content=response.content,
            )
        _logger.warning(
            f"Authorization error: {response.status_code} - {response.text}"
            f" will try and authenticate and retry."
        )
        return self._authenticate()

    def retry_request(__make_request):
        def inner_function(*args, **kwargs):
            counter = 0
            while counter <= AxiomaSession.current.max_retries:
                response = __make_request(*args, **kwargs)
                if (response.status_code == 500 and
                        "/analyses/" not in args[2] and
                        AxiomaSession.current.api_type != "BULK"):
                    counter = counter + 1
                    _logger.info(f"Will Retry request if {counter} <= {AxiomaSession.current.max_retries} as specified by user")
                else:
                    return response
            return response

        return inner_function

    @retry_request
    def __make_request(
        self,
        method: HttpMethods,
        url: str,
        json: dict = None,
        data = None,
        params: dict = None,
        headers: dict = None,
        stream: bool = False,
        cls: type = None,
        try_auth: bool = True,
        return_response: bool = False
    ):
        """
        Wraps the requests method to log the request and log the response
        handle errors.

        Setting stream to True will ignore the cls argument and
        return the response object.

        Returns:
            requests response: the response object from making the request
        """

        url, kwargs = self._prepare_request_args(
            method=method, url=url, json=json, data=data, params=params, headers=headers
        )

        if stream and cls is not None:
            _logger.warning(
                "If the cls argument is not None the request will not be streamed"
            )
            stream = False

        try:
            req = self._session.build_request(method=method.value, url=url, **kwargs)
            response = self._session.send(request=req, stream=stream)
        except httpx.RequestError as e:
            _logger.error(f"Sending the request raised a request error: {e}")
            raise AxiomaRequestError(http_request_error=e) from e

        if response.status_code == 401:
            # Try logging in again in case session expired
            self._authentication_failed(response=response, try_auth=try_auth)

            return self.__make_request(
                method,
                str(req.url),
                params=params,
                json=json,
                headers=headers,
                cls=cls,
                try_auth=False,
            )

        self._handle_response_exception(response=response, stream=stream)

        if return_response:
            return response

        prepped_response = self._prepare_response(
            response=response,
            method=method,
            cls=cls,
            stream=stream,
            return_response=return_response,
        )

        return prepped_response

    def _get(
        self,
        url: str,
        params: dict = None,
        headers: dict = None,
        stream: bool = False,
        cls: type = None,
        return_response: bool = False,
    ):
        resp = self.__make_request(
            HttpMethods.GET,
            url,
            params=params,
            headers=headers,
            stream=stream,
            cls=cls,
            return_response=return_response,
        )
        return resp

    def _delete(
        self,
        url: str,
        params: dict = None,
        headers: dict = None,
        return_response: bool = False,
    ):
        resp = self.__make_request(
            HttpMethods.DELETE,
            url,
            params=params,
            headers=headers,
            return_response=return_response,
        )
        return resp

    def _post(
        self, url: str, json: dict, headers: dict = None, return_response: bool = False,
    ):
        resp = self.__make_request(
            HttpMethods.POST,
            url,
            json=json,
            headers=headers,
            return_response=return_response,
        )
        return resp

    def _put(
        self, url: str, json: dict, headers: dict = None, return_response: bool = False,
    ):
        resp = self.__make_request(
            HttpMethods.PUT,
            url,
            json=json,
            headers=headers,
            return_response=return_response,
        )
        return resp

    def _patch(
        self,
        url: str,
        json: dict = None,
        data = None,
        headers: dict = None,
        parameters: dict = None,
        cls: type = None,
        return_response: bool = False,
    ):
        resp = self.__make_request(
            HttpMethods.PATCH,
            url,
            json=json,
            data=data,
            headers=headers,
            params=parameters,
            cls=cls,
            return_response=return_response,
        )
        return resp

    def _authenticate(self):
        raise NotImplementedError("Must implement _authenticate")


class SimpleAuthSession(AxiomaSession):
    """An oauth session that provides the authentication mechanism for the underlying session.
    Created by the AxiomaSession based on the credentials provided.

    Args:
        AxiomaSession ([type]): [description]
    """

    def __init__(
        self,
        client_id: str,
        username: str,
        password: str,
        domain: str,
        proxy=None,
        certificates=None,
        api_type: str = APIType.REST,
        application_name: str = DEFAULT_APP,
        api_version: str = API_VERSION,
        event_hooks: dict = None,
        max_retries: int = 0,
        request_timeout: int = 300
    ):
        super().__init__(
            domain=domain,
            proxy=proxy,
            certificates=certificates,
            api_type=api_type,
            application_name=application_name,
            api_version=api_version,
            event_hooks=event_hooks,
        )

        env_config = self._config_for_environment()

        self.auth_url = f"{self.domain}{env_config['AUTH_PATH']}"
        self.grant_type = env_config["GRANT_TYPE"]
        self.auth_timeout = int(env_config["AUTH_TIMEOUT"])
        self.timeout = request_timeout
        self.__client_id = client_id
        self.username = username
        self.password = password
        self.proxy = proxy
        self.certificates = certificates
        self.max_retries = max_retries

    def _authenticate(self):
        credentials = {
            "grant_type": self.grant_type,
            "client_id": self.__client_id,
            "username": self.username,
            "password": self.password,
        }
        headers = {
            "accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        proxy = self.proxy
        certificates = self.certificates
        _logger.info("Preparing to authenticate:")

        with httpx.Client(proxies=proxy, verify=certificates, timeout=self.timeout) as client:
            response = client.post(self.auth_url, data=credentials, headers=headers)

        _logger.info(f"Sending authentication request to {self.auth_url}")

        if response.status_code != 200:
            _logger.error(
                f"Unable to authenticate: {response.status_code} - {response.text}"
            )

            raise AxiomaAuthenticationError(
                message="Response error from request. Note: The order of parameters were changed as part of axiomapy 1.77 release. Please refer to examples or Change log for additional details.",
                content=response.text,
                reason=response.reason_phrase,
                status_code=response.status_code,
                response=response,
            )

        response_json = response.json()
        access_token = response_json.get("access_token")
        _logger.info(
            "Successfully authenticated, setting access token to session headers."
        )

        auth_headers = {
            "Authorization": "Bearer " + access_token,
            "Content-Type": "application/json",
        }

        self._session.headers.update(auth_headers)
        self._session.timeout = httpx.Timeout(self.timeout)

        return True
