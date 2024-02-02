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

"""
import logging
from axiomapy.session import AxiomaSession
from axiomapy.utils import odata_params

_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())


class BatchDefinitionsAPI:
    """Access api methods of batch definitions using the active session

    """

    @staticmethod
    def get_batch_definitions(
        filter_results: str = None,
        top: int = None,
        skip: int = None,
        orderby: str = None,
        headers: dict = None,
        return_response: bool = False,
    ):
        """This method lists the batch definitions

        Args:
            filter_results: user can apply filter to the list
            top: returns top N number of elements
            skip: skips first N elements
            orderby: sorts in particular order
            headers: Optional headers if any needed (Correlation ID , Accept-Encoding)
            return_response: If set to true, the response will be returned

        Returns:
            Collection of batch definitions
        """
        url = "/batch-definitions"
        params = odata_params(filter_results, top, skip, orderby)
        _logger.info(f"Getting from {url}")
        response = AxiomaSession.current._get(
            url,
            params=params,
            return_response=return_response,
            headers=headers,
        )
        return response

    @staticmethod
    def get_batch_definition(
        batch_definition_id: str,
        headers: dict = None,
        return_response: bool = False,
    ):
        """This method returns a single batch definition based on id

        Args:
            batch_definition_id: d for batch definition
            headers: Optional headers if any needed
            return_response: If set to true, the response will be returned

        Returns:
            Single batch definition
        """
        url = f"/batch-definitions/{batch_definition_id}"
        _logger.info(f"Getting from {url}")
        response = AxiomaSession.current._get(
            url, return_response=return_response, headers=headers
        )
        return response
