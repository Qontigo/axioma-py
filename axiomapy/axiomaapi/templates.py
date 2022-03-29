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
from typing import List

from axiomapy.session import AxiomaSession
from axiomapy.utils import odata_params

_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())


class TemplatesAPI:
    """Access api methods of templates using the active session
    """

    @staticmethod
    def get_templates(
        filter_results: str = None,
        top: int = None,
        skip: int = None,
        orderby: str = None,
        return_response: bool = False,
    ):
        """The method lists all the templates available

        Args:
            filter_results:user can apply filter to the list
            top:returns top N number of elements
            skip:skips first N elements
            orderby:sorts in particular order
            return_response:If set to true, the response will be returned

        Returns:
            List of template links
        """
        url = "/templates"
        params = odata_params(filter_results, top, skip, orderby)
        _logger.info(f"Getting from {url}")
        response = AxiomaSession.current._get(
            url, params=params, return_response=return_response
        )
        return response

    @staticmethod
    def get_templates_by_type(
        typeName1: str = "any", headers: dict = None, return_response: bool = False,
    ):
        """The method fetches a template for a given type

        Args:
            typeName1:type of template that needs to be requested
            headers:additional headers, if any required by the request
            return_response: If set to true, the response will be returned

        Returns:
            The template of specified type
        """
        url = f"/templates/{typeName1}"
        _logger.info(f"Getting from {url}")
        response = AxiomaSession.current._get(
            url, headers=headers, return_response=return_response
        )
        return response

    @staticmethod
    def get_templates_by_type2(
        typeName1: str = "any",
        typeName2: str = "any",
        headers: dict = None,
        return_response: bool = False,
    ):
        """The method fetches templates for specified types

        Args:
            typeName1:type name for template
            typeName2:type name for template
            headers:additional headers, if any required by the request
            return_response:If set to true, the response will be returned

        Returns:
            The template of specified types
        """
        url = f"/templates/{typeName1}/{typeName2}"
        _logger.info(f"Getting from {url}")
        response = AxiomaSession.current._get(
            url, headers=headers, return_response=return_response
        )
        return response

    @staticmethod
    def get_entities(
        template_name: str,
        typeName1: str = "any",
        typeName2: str = "any",
        headers: dict = None,
        return_response: bool = False,
    ):
        """The method retrieves entities that fulfill the template

        Args:
            template_name:name of the template
            typeName1:type of template
            typeName2:type of template
            headers:additional headers, if any required by the request
            return_response:If set to true, the response will be returned

        Returns:
            The collection of entities that fulfills the criteria
        """
        url = f"/templates/{typeName1}/{typeName2}/{template_name}"
        _logger.info(f"Getting from {url}")
        response = AxiomaSession.current._get(
            url, headers=headers, return_response=return_response
        )
        return response

    @staticmethod
    def get_entity(
        id_: int,
        template_name: str,
        typeName1: str = "any",
        typeName2: str = "any",
        headers: dict = None,
        return_response: bool = False,
    ):
        """This method gets a particular entity that fulfills the template

        Args:
            id_:id of the entity
            template_name:name of template
            typeName1:type of template
            typeName2:type of template
            headers:additional headers, if any required by the request
            return_response:If set to true, the response will be returned

        Returns:
            link of entity that fulfills the criteria
        """
        url = f"/templates/{typeName1}/{typeName2}/{template_name}/{id_}"
        _logger.info(f"Getting from {url}")
        response = AxiomaSession.current._get(
            url, headers=headers, return_response=return_response
        )
        return response

    @staticmethod
    def post_entity(
        entity: dict,
        template_name: str,
        typeName1: str = "any",
        typeName2: str = "any",
        headers: dict = None,
        return_response: bool = False,
    ):
        """This method creates a new entity instance and its underliers using the template

        Args:
            entity:dictionary with entity details to be created
            template_name:name of template
            typeName1:type of template
            typeName2:type of template
            headers:additional headers, if any required by the request
            return_response:If set to true, the response will be returned

        Returns:
            Success message if the entity is created. Code 201
        """
        url = f"/templates/{typeName1}/{typeName2}/{template_name}"
        _logger.info(f"Posting to {url}")
        response = AxiomaSession.current._post(
            url, entity, headers=headers, return_response=return_response
        )
        return response

    @staticmethod
    def put_entity(
        entity: dict,
        id_: int,
        template_name: str,
        typeName1: str = "any",
        typeName2: str = "any",
        headers: dict = None,
        return_response: bool = False,
    ):
        """This method creates an entity using a predefined template.

        Args:
            entity:statistic to be created
            id_:id of entity
            template_name:name of template
            typeName1:type of template
            typeName2:type of template
            headers:additional headers, if any required by the request
            return_response:If set to true, the response will be returned

        Returns:
            Success message if the statistic is created. Code 201.
        """
        url = f"/templates/{typeName1}/{typeName2}/{template_name}/{id_}"
        _logger.info(f"Putting to {url}")
        response = AxiomaSession.current._put(
            url, entity, headers=headers, return_response=return_response
        )
        return response

    @staticmethod
    def delete_entity(
        id_: int,
        template_name: str,
        typeName1: str = "any",
        typeName2: str = "any",
        headers: dict = None,
        return_response: bool = False,
    ):
        """This method deletes an entity. This currently does not delete the underliers.

        Args:
            id_:id of the entity
            template_name:name of template
            typeName1:type of template
            typeName2:type of template
            headers:additional headers, if any required by the request
            return_response:If set to true, the response will be returned

        Returns:
            Success message if the entity is deleted. Code 204
        """
        url = f"/templates/{typeName1}/{typeName2}/{template_name}/{id_}"
        _logger.info(f"Deleting {url}")
        response = AxiomaSession.current._delete(
            url, headers=headers, return_response=return_response
        )
        return response

    @staticmethod
    def patch_entities(
        template_name: str,
        entities_upsert: List[dict] = None,
        entities_remove: List[dict] = None,
        typeName1: str = "any",
        typeName2: str = "any",
        import_settings: dict = None,
        parameters: dict = None,
        headers: dict = None,
        return_response: bool = False,
    ):
        """This method upserts or deletes using the template inputs

        Args:
            template_name:name of template
            entities_upsert:list of entities to upsert
            entities_remove:list of entities to be removed
            typeName1:type of template
            typeName2:type of template
            import_settings:settings to control the behavior when importing positions
            parameters:processEachItem: set to true/false to process each item one at a time or in batch
            headers:additional headers, if any, required for the request
            return_response:If set to true, the response will be returned

        Returns:
            Success message if the request is processed. Code 200
        """
        if(entities_upsert is None):
            entities_upsert =  []
        if(entities_remove is None):
            entities_remove = []
        url = f"/templates/{typeName1}/{typeName2}/{template_name}"
        _logger.info(f"Patching to {url}")
        entities_patch = {"upsert": entities_upsert, "remove": entities_remove}
        if import_settings is not None:
            entities_patch["importSettings"] = import_settings
        response = AxiomaSession.current._patch(
            url,
            entities_patch,
            headers=headers,
            parameters=parameters,
            return_response=return_response,
        )
        return response
