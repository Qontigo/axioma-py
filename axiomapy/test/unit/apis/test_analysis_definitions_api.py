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
from axiomapy.axiomaapi import AnalysisDefinitionAPI
from axiomapy.session import SimpleAuthSession
from axiomapy import AxiomaSession

import unittest
from unittest.mock import patch, Mock, ANY, MagicMock
from axiomapy.odatahelpers import oDataFilterHelper as od
from httpx import Response, Request
import httpx
from axiomapy.axiomaexceptions import AxiomaRequestValidationError


class TestAnalysisDefinitionsAPIMocker(unittest.TestCase):
    @patch.object(SimpleAuthSession, "_authenticate", return_value=True)
    def setUp(self, mock_SimpleAuthSession):
        AxiomaSession.use_session(username="u_name", password="pwd", domain="http://test")
        self.domain = "http://test/REST"

    @patch.object(httpx.Client, "build_request")
    def test_get_analysis_definitions(self, mock_Request):
        mock_response = Mock(spec=Response)
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_request = Mock(spec=Request)
        mock_request.url = "http://mock_url"
        mock_request.method = "GET"
        mock_response.request = mock_request

        mock_Request.return_value = Request("GET", "http://mock_url")

        with patch.object(
                AxiomaSession.current._session,
                "send",
                return_value=Request(method="GET", url=self.domain),
        ) as mock_session_send:
            mock_session_send.return_value = mock_response

            filters = [
                od.contains("name", "MAC Global")
            ]
            filter_ = " ".join(filters)
            ad_response = AnalysisDefinitionAPI.get_analysis_definitions(filter_results=filter_)
            url = (
                f"{self.domain}/api/{AxiomaSession.current.api_version}/analysis-definitions"
            )

            mock_Request.assert_called_with(method="GET", url=url, headers=ANY,
                                            params={'$filter': "contains(name, 'MAC Global')"})
            self.assertEqual(ad_response.response.status_code, 200)
            self.assertEqual(url, "http://test/REST/api/v1/analysis-definitions")

    @patch.object(httpx.Client, "build_request")
    def test_get_analysis_definition(self, mock_Request):
        analysis_def_id = 123
        mock_response = Mock(spec=Response)
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_request = Mock(spec=Request)
        mock_request.url = "http://mock_url"
        mock_request.method = "GET"
        mock_response.request = mock_request

        mock_Request.return_value = Request("GET", "http://mock_url")

        with patch.object(
                AxiomaSession.current._session,
                "send",
                return_value=Request(method="GET", url=self.domain),
        ) as mock_session_send:
            mock_session_send.return_value = mock_response
            ad_response = AnalysisDefinitionAPI.get_analysis_definition(analysis_def_id)
            url = (
                f"{self.domain}/api/{AxiomaSession.current.api_version}/analysis-definitions/{analysis_def_id}"
            )
            mock_Request.assert_called_with(method="GET", url=url, headers=ANY)
            self.assertEqual(ad_response.response.status_code, 200)
            self.assertEqual(url, "http://test/REST/api/v1/analysis-definitions/123")

    @patch.object(httpx.Client, "build_request")
    def test_post_analysis_definition(self, mock_Request):

        analysis_def_dict = {
            "aggregationLevelDefinitions": [
                {
                    "name": "Client Id - All Levels",
                    "item": {
                        "templateName": "{DefaultTemplateFor_ViewReportingLevelInNestedPortfolio}",
                        "content": {
                            "attributeName": "ClientId.MaxDepth",
                            "nestedAttributeSource": "Position"
                        }
                    }
                }
            ],
            "name": "def1"
        }
        mock_response = Mock(spec=Response)
        mock_response.status_code = 201
        mock_response.headers = {}
        mock_request = Mock(spec=Request)
        mock_request.url = "http://mock_url"
        mock_request.method = "POST"
        mock_response.request = mock_request

        mock_Request.return_value = Request("POST", "http://mock_url")

        with patch.object(
                AxiomaSession.current._session,
                "send",
                return_value=Request(method="POST", url=self.domain),
        ) as mock_session_send:
            mock_session_send.return_value = mock_response
            ad_response = AnalysisDefinitionAPI.post_analysis_definition(analysis_def_dict)
            url = (
                f"{self.domain}/api/{AxiomaSession.current.api_version}/analysis-definitions"
            )
            mock_Request.assert_called_with(method="POST", url=url, headers=ANY, json=analysis_def_dict)
            self.assertEqual(ad_response.response.status_code, 201)
            self.assertEqual(url, "http://test/REST/api/v1/analysis-definitions")

    @patch.object(httpx.Client, "build_request")
    def test_post_analysis_definition1(self, mock_Request):

        analysis_def_dict = None
        mock_response = MagicMock()
        mock_response.status_code = 422
        mock_response.headers = {}
        mock_request = Mock(spec=Request)
        mock_request.url = "http://mock_url"
        mock_request.method = "POST"
        mock_response.request = mock_request

        mock_Request.return_value = Request("POST", "http://mock_url")

        with patch.object(
                AxiomaSession.current._session,
                "send",
                return_value=Request(method="POST", url=self.domain),
        ) as mock_session_send:
            mock_session_send.side_effect = AxiomaRequestValidationError("Validation Failed", 422, "Validation Failed",
                                                                         "Validation Failed", mock_response, {})
            with self.assertRaises(AxiomaRequestValidationError) as error:
                ad_response = AnalysisDefinitionAPI.post_analysis_definition(analysis_def_dict)
                self.assertEqual(str(error.exception), "Validation Failed")
                self.assertEqual(ad_response.response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
