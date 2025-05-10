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

from axiomapy.session import AxiomaSession
from axiomapy.utils import odata_params

_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())


class RiskModelDefinitionsAPI:
    """Access api methods of risk model definitions using the active session

    """

    @staticmethod
    def get_risk_model_definitions(
        filter_results: str = None,
        top: int = None,
        skip: int = None,
        orderby: str = None,
        headers: dict = None,
        return_response: bool = False,
    ):
        """This method lists all the risk model definitions

        Args:
            filter_results:user can apply filter to the list
            top:returns top N number of elements
            skip:skips first N elements
            orderby:sorts in particular order
            headers:Optional headers if any needed (Correlation ID , Accept-Encoding)
            return_response: If set to true, the response will be returned

        Returns:
            Collection of Risk Model Definition summaries
        """
        url = "/risk-model-definitions"
        params = odata_params(filter_results, top, skip, orderby)
        _logger.info(f"Getting from {url}")
        response = AxiomaSession.current._get(
            url,
            params=params,
            headers=headers,
            return_response=return_response,
        )
        return response

    @staticmethod
    def get_risk_model_definition(
        risk_model_definition_id: str,
        headers: dict = None,
        return_response: bool = False,
    ):
        """This method retrieves a single risk model definition

        Args:
            risk_model_definition_id:requested risk model definition id
            headers: Optional headers if any needed (Correlation ID , Accept-Encoding)
            return_response: If set to true, the response will be returned

        Returns:
            Returns a single risk model definition
        """
        url = f"/risk-model-definitions/{risk_model_definition_id}"
        _logger.info(f"Getting from {url}")
        response = AxiomaSession.current._get(
            url, headers=headers, return_response=return_response
        )
        return response

    @staticmethod
    def post_risk_model_definition(
            entity: dict,
            headers: dict = None,
            return_response: bool = False,
    ):
        """This method creates a single risk model definition

        Args:
            entity: Dictionary with entity details to be created
            headers: Optional headers if any needed (Correlation ID , Accept-Encoding)
            return_response: If set to true, the response will be returned

        Returns:
            Success message if the entity is created. Code 201
        """
        url = f"/risk-model-definitions"
        _logger.info(f"Posting from {url}")
        response = AxiomaSession.current._post(
            url, entity, headers=headers, return_response=return_response
        )
        return response

    @staticmethod
    def put_risk_model_definition(
            entity: dict,
            risk_model_definition_id: str,
            headers: dict = None,
            return_response: bool = False,
    ):
        """This method replaces a single risk model definition

        Args:
            entity: Dictionary with entity details to replace
            headers: Optional headers if any needed (Correlation ID , Accept-Encoding)
            return_response: If set to true, the response will be returned

        Returns:
            Success message if the entity is created. Code 201
        """
        url = f"/risk-model-definitions/{risk_model_definition_id}"
        _logger.info(f"Putting from {url}")
        response = AxiomaSession.current._put(
            url, entity, headers=headers, return_response=return_response
        )
        return response
