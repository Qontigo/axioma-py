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

_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())


class MetaDataAPI:
    """Access api methods of data templates using the active session

    """

    @staticmethod
    def get_templates(headers: dict = None, return_response: bool = False):
        """The method lists the templates that can be used for analysis definitions

        Args:
            headers:Optional headers, if any needed (Correlation ID , Accept-Encoding)
            return_response: If set to true, the response will be returned

        Returns:
            A collection of entity template summaries if the request succeeds. Code 200
        """
        url = "/metadata/templates"
        _logger.info(f"Getting from {url}")
        response = AxiomaSession.current._get(
            url, headers=headers, return_response=return_response
        )
        return response

    @staticmethod
    def get_template(
        template_name: str, headers: dict = None, return_response: bool = False
    ):
        """The method returns the template based on the template name

        Args:
            template_name: name of the template to be returned
            headers:Optional headers, if any needed (Correlation ID , Accept-Encoding)
            return_response: If set to true, the response will be returned

        Returns:
            The template based on the template name
        """
        url = f"/metadata/templates/{template_name}"
        _logger.info(f"Getting from {url}")
        response = AxiomaSession.current._get(
            url, headers=headers, return_response=return_response
        )
        return response

    @staticmethod
    def get_template_schema(
        template_name: str, headers: dict = None, return_response: bool = False
    ):
        """The method returns the schema in use for a particular template

        Args:
            template_name: name of template
            headers:
            return_response: If set to true, the response will be returned

        Returns:
            Schema of template
        """
        url = f"/metadata/templates/{template_name}/schema"
        _logger.info(f"Getting from {url}")
        response = AxiomaSession.current._get(
            url, headers=headers, return_response=return_response
        )
        return response