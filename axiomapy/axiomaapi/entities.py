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


class EntitiesAPI:
    """Access api methods of entities using the active session

    """

    @staticmethod
    def get_entity_links(
        filter_results: str = None,
        top: int = None,
        skip: int = None,
        orderby: str = None,
        headers: dict = None,
        return_response: bool = False,
    ):
        """This method gets links to all the entities
        
        Args:
            filter_results: user can apply filters to the list
            top: returns top N number of elements
            skip: skips first N elements
            orderby: sorts in a particular order
            headers: Optional headers, if any needed (Correlation ID , Accept-Encoding)
            return_response: If set to true, the response will be returned

        Returns:
            Collection of sub-links to query entities
        """
        url = "/entities"
        params = odata_params(filter_results, top, skip, orderby)
        _logger.info(f"Getting from {url}")
        response = AxiomaSession.current._get(
            url, params=params, headers=headers, return_response=return_response
        )
        return response

    @staticmethod
    def get_entities(
        typeName1: str = "*",
        typeName2: str = "*",
        filter_results: str = None,
        top: int = None,
        skip: int = None,
        orderby: str = None,
        headers: dict = None,
        return_response: bool = False,
    ):
        """This method gets all the entities for the given type

        Args:
            typeName1: type name for entity
            typeName2: type name for entity
            filter_results: user can apply filters to the list
            top: returns top N number of elements
            skip: skips first N elements
            orderby: sorts in a particular order
            headers: Optional headers, if any needed (Correlation ID , Accept-Encoding)
            return_response: If set to true, the response will be returned

        Returns:
            Collection of entities
        """
        url = f"/entities/{typeName1}/{typeName2}"
        params = odata_params(filter_results, top, skip, orderby)
        _logger.info(f"Getting from {url}")
        response = AxiomaSession.current._get(
            url, params=params, headers=headers, return_response=return_response
        )
        return response

    @staticmethod
    def get_entity(
        id_: int,
        typeName1: str = "*",
        typeName2: str = "*",
        headers: dict = None,
        return_response: bool = False,
    ):
        """This method gets the entity with the given id

        Args:
            id_: id of entity
            typeName1: type of entity
            typeName2: type of entity
            headers:Optional headers, if any needed (Correlation ID , Accept-Encoding)
            return_response: If set to true, the response will be returned

        Returns:
            Returns model for entity
        """
        url = f"/entities/{typeName1}/{typeName2}/{id_}"
        _logger.info(f"Getting from {url}")
        response = AxiomaSession.current._get(
            url, headers=headers, return_response=return_response
        )
        return response

    @staticmethod
    def delete_entity(
        id_: int,
        typeName1: str = "*",
        typeName2: str = "*",
        headers: dict = None,
        return_response: bool = False,
    ):
        """This method deletes an entity. Underliers are not currently deleted

        Args:
            typeName1: type of entity
            typeName2: type of entity
            headers:Optional headers, if any needed (Correlation ID )
            return_response: If set to true, the response will be returned

        Returns:
            Success message once the entity is deleted. Code 204
        """
        url = f"/entities/{typeName1}/{typeName2}/{id_}"
        _logger.info(f"Putting to {url}")
        response = AxiomaSession.current._delete(
            url, headers=headers, return_response=return_response
        )
        return response
