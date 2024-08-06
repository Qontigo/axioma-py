"""
Copyright © 2024 Axioma by SimCorp.
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

"""
class AxiomaError(Exception):
    """Base class for errors in this module"""

    def __init__(self, message=""):
        super().__init__(message)


class AxiomaValueError(AxiomaError):
    pass


class AxiomaLookupError(AxiomaError):
    pass


class AxiomaTypeError(AxiomaError):
    pass


class AxiomaRequestError(AxiomaError):
    def __init__(self, message="", http_request_error: Exception = None):
        super().__init__(message=message)
        self._cause = http_request_error

    @property
    def cause(self,) -> Exception:
        return self._cause

    def __str__(self):
        result = "Sending the request raised a HTTP request error:"
        if self.cause is not None:
            result = f"{result}\n{self.cause}"
        return result


class AxiomaRequestStatusError(AxiomaError):
    def __init__(self, message="", status_code=0, content="", reason="", response=None):
        super().__init__(message=message)
        self.status_code = status_code
        self.content = content
        self.reason = reason
        self.message = message
        self.response = response

    def __str__(self):
        prepend = "summary: {}\n".format(self.message)
        prepend = (
            "{}content: {}\n".format(prepend, self.content) if self.content else ""
        )
        result = "{}status: {}, message: {}".format(
            prepend, self.status_code, self.reason
        )
        return result

    @property
    def response(self,):
        return self._response

    @response.setter
    def response(self, value):
        self._response = value

    @property
    def status_code(self,):
        return self._status_code

    @status_code.setter
    def status_code(self, value):
        self._status_code = value

    @property
    def content(self,):
        return self._content

    @content.setter
    def content(self, value):
        self._content = value

    @property
    def reason(self,):
        return self._reason

    @reason.setter
    def reason(self, value):
        self._reason = value


class AxiomaRequestValidationError(AxiomaRequestStatusError):
    def __init__(
        self, message, status_code, content, reason, response, validation_error: dict
    ):
        super().__init__(
            message=message,
            status_code=status_code,
            content=content,
            reason=reason,
            response=response,
        )
        self.validation_error = validation_error

    @property
    def validation_error(self,):
        return self._validation_error

    @validation_error.setter
    def validation_error(self, value):
        self._validation_error = value


class AxiomaAuthenticationError(AxiomaRequestStatusError):
    pass


class AxiomaAuthorizationError(AxiomaRequestError):
    pass


class AxiomaUninitialisedError(AxiomaError):
    pass


class AxiomaPatchError(AxiomaError):
    def __init__(self, patch_response: dict):
        super().__init__(
            message="Errors were returned when patching. Check the patch response prop."
        )
        self._upsert = patch_response.get("upsert", [])
        self._remove = patch_response.get("remove", [])
        self._patch = patch_response

    @property
    def patch_response(self):
        return self._patch

    def __str__(self):
        result = "Upsert errors:{}\nRemove errors:{}".format(
            ",\n".join(self._upsert), ",\n".join(self._remove)
        )
        return result
