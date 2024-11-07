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

import logging
from axiomapy import AxiomaSession
from axiomapy.axiomaapi import AdminAPI
from axiomapy.axiomaexceptions import AxiomaRequestStatusError

_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())


def map_external_identity(user_login, user_name, email,
                          return_response: bool = False):
    url = "/admin/users"
    _logger.info(f"Posting to from {url}")
    user_data = {"userLogin": user_login, "userName": user_name, "email": email}
    response = AxiomaSession.current._post(
        url, user_data, return_response=return_response
    )
    if response.status_code != 201:
        raise AxiomaRequestStatusError("Error creating user",
                                       status_code=response.status_code,
                                       response=response)

    external_id_data = {"subject": email, "identityProvider": "azuread", "email": email}
    exid_response = AdminAPI.post_external_identity(external_id_data)
    if exid_response.status_code != 201:
        raise AxiomaRequestStatusError("Error creating user",
                                       status_code=exid_response.status_code,
                                       response=exid_response)

    external_id = exid_response.headers['location'].split('/')[-1]

    url = f"/admin/users/{user_login}"
    user_data = {"userName": user_name, "email": email, "externalIdentityId": external_id}
    response = AxiomaSession.current._put(
        url, user_data, return_response=return_response
    )

    if response.status_code == 204:
        return "Success"