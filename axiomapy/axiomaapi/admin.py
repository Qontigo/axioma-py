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

from axiomapy.utils import odata_params
from axiomapy.session import AxiomaSession

_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())

class AdminAPI:
    """Access admin api methods using the active session
    """

    @staticmethod
    def get_external_identities(filter_results: str = None,
        top: int = None,
        skip: int = None,
        orderby: str = None,
        return_response: bool = False):
        """The method lists the external identities

        Args:
            filter_results:user can apply filters to the list
            top:returns top N number of elements
            skip:skips first N elements
            orderby:sorts in particular order
            return_response: If set to true, the response will be returned

        Returns:
            A collection of external identities if the request succeeds. Code 200
        """
        url = "/admin/external-identities"
        _logger.info(f"Getting from {url}")
        params = odata_params(filter_results, top, skip, orderby)
        response = AxiomaSession.current._get(
            url, params=params, return_response=return_response
        )
        return response

    @staticmethod
    def get_external_identity(external_identity_id: int,
                               return_response: bool = False):
        """The method returns the external identity

        Args:
            external_identity_id: The id of the external identity that needs to be fetched
            return_response: If set to true, the response will be returned

        Returns:
            An external identity if the request succeeds. Code 200
        """
        url = f"/admin/external-identities/{external_identity_id}"
        _logger.info(f"Getting from {url}")
        response = AxiomaSession.current._get(
            url, return_response=return_response
        )
        return response

    @staticmethod
    def post_external_identity(external_identity: dict,
                                 return_response: bool = False):
        """The method creates a new external identity

        Args:
            external_identity: external identity json with the details to be created
            return_response: If set to true, the response will be returned

        Returns:
             Success message if the external identity is created. Status code 201
        """
        url = "/admin/external-identities"
        _logger.info(f"Posting to {url}")
        response = AxiomaSession.current._post(
            url, external_identity, return_response=return_response
        )
        return response

    @staticmethod
    def put_external_identity(external_identity_id: int,
                              external_identity: dict,
                              return_response: bool = False):
        """The method updates the existing external identity

        Args:
            external_identity_id: The id of the external identity that needs to be updated
            external_identity: external identity json with the updated details
            return_response: If set to true, the response will be returned

        Returns:
             Success message if the external identity is updated. Code 204
        """
        url = f"/admin/external-identities/{external_identity_id}"
        _logger.info(f"Sending Put to {url}")
        response = AxiomaSession.current._put(
            url, external_identity, return_response=return_response
        )
        return response

    @staticmethod
    def delete_external_identity(external_identity_id: int,
                                 return_response: bool = False):
        """The method deletes an existing external identity

        Args:
            external_identity_id: The id of the external identity that needs to be deleted
            return_response: If set to true, the response will be returned

        Returns:
             Success message if the external identity is deleted. Code 204
        """
        url = f"/admin/external-identities/{external_identity_id}"
        _logger.info(f"Delete using {url}")
        response = AxiomaSession.current._delete(
            url, return_response=return_response
        )
        return response