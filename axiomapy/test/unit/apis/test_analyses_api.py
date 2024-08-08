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
from axiomapy.axiomaapi import AnalysesAPI, AnalysesRiskAPI, AnalysesPerformanceAPI
from axiomapy.session import SimpleAuthSession
from axiomapy import AxiomaSession
from axiomapy.axiomaexceptions import AxiomaRequestValidationError

import unittest
from unittest.mock import patch, Mock, ANY, MagicMock

from httpx import Response, Request
import httpx


class TestAnalysesAPIMocker(unittest.TestCase):
    @patch.object(SimpleAuthSession, "_authenticate", return_value=True)
    def setUp(self, mock_SimpleAuthSession):
        AxiomaSession.use_session(username="u_name", password="pwd",
                                  domain="https://test")
        self.domain = "https://test/REST"

    @patch.object(httpx.Client, "build_request")
    def test_post_performance_analyses(self, mock_Request):
        p_id = 1234
        pa_dict = {
            "startDate": "2017-09-19",
            "endDate": "2017-09-21",
            "benchmark": {
                "lookup": [
                    {
                        "type": "Portfolio",
                        "value": "TestPortfolio"
                    }
                ]
            },
            "performanceAttributionSettingsName": "PASettingExample",
            "hierarchy": [
                {
                    "hierarchyLevelType": "ViewReportingLevelOnInstrument",
                    "attributeName": "Region",
                    "name": "Region",
                    "isAxiomaProvidedAttributeSource": "true"
                }
            ]
        }
        mock_response = Mock(spec=Response)
        mock_response.status_code = 202
        mock_response.headers = {}
        mock_request = Mock(spec=Request)
        mock_request.url = "https://mock_url"
        mock_request.method = "POST"
        mock_request.headers = {}
        mock_response.request = mock_request

        mock_Request.return_value = Request("POST", "https://mock_url")

        with patch.object(
                AxiomaSession.current._session,
                "send",
                return_value=Request(method="POST", url=self.domain),
        ) as mock_session_send:
            mock_session_send.return_value = mock_response

            pa_response = AnalysesPerformanceAPI.post_performance_analysis(p_id, pa_dict)
            url = (
                f"{self.domain}/api/{AxiomaSession.current.api_version}/analyses/performance/portfolios/{p_id}"
            )

            mock_Request.assert_called_with(method="POST", url=url, headers=ANY, json=pa_dict)
            self.assertEqual(pa_response.response.status_code, 202)
            self.assertEqual(url, "https://test/REST/api/v1/analyses/performance/portfolios/1234")
            self.assertIsInstance(pa_dict, dict)

    @patch.object(httpx.Client, "build_request")
    def test_post_missing_precompute(self, mock_Request):
        pa_dict = None
        p_id = 123
        mock_response = MagicMock()
        mock_response.status_code = 422
        mock_response.headers = {}
        mock_request = Mock(spec=Request)
        mock_request.url = "https://mock_url"
        mock_request.method = "POST"
        mock_response.request = mock_request

        mock_Request.return_value = Request("POST", "https://mock_url")

        with patch.object(
                AxiomaSession.current._session,
                "send",
                return_value=Request(method="POST", url=self.domain),
        ) as mock_session_send:
            mock_session_send.side_effect = AxiomaRequestValidationError("Validation Failed", 422, "Validation Failed",
                                                                         "Validation Failed", mock_response, {})
            with self.assertRaises(AxiomaRequestValidationError) as error:
                precompute_response = AnalysesPerformanceAPI.post_precompute(p_id, pa_dict)
                self.assertEqual(str(error.exception), "Validation Failed")
                self.assertEqual(precompute_response.response.status_code, 422)

    @patch.object(httpx.Client, "build_request")
    def test_get_analyses_status(self, mock_Request):
        request_id = 112
        mock_response = Mock(spec=Response)
        mock_response.status_code = 200
        mock_request = Mock(spec=Request)
        mock_request.url = "https://mock_url"
        mock_request.method = "GET"
        mock_response.request = mock_request
        mock_response.json.return_value = {
            "status": "Completed",
            "createdDate": "2018-01-31T01:02:03Z",
            "percentComplete": 100,
            "_links": {
                "self": {
                    "href": "/api/v1/analyses/12345567789/status"
                },
                "logs": {
                    "href": "/api/v1/analyses/12345567789/logs",
                    "title": "Log output for the analysis"
                },
                "results": {
                    "href": "/api/v1/analyses/12345567789",
                    "title": "The results of the analysis"
                }
            }
        }

        mock_Request.return_value = Request("GET", "https://mock_url")

        with patch.object(
                AxiomaSession.current._session,
                "send",
                return_value=Request(method="GET", url=self.domain),
        ) as mock_session_send:
            mock_session_send.return_value = mock_response
            status_response = AnalysesPerformanceAPI.get_status(request_id)
            url = (
                f"{self.domain}/api/{AxiomaSession.current.api_version}/analyses/performance/{request_id}/status"
            )

            mock_Request.assert_called_with(method="GET", url=url, headers=ANY)
            self.assertEqual(status_response.response.status_code, 200)
            self.assertEqual(url, "https://test/REST/api/v1/analyses/performance/112/status")
            self.assertIn(status_response.response.json.return_value['status'],
                          ["Unknown", "Created", "Submitted", "Running", "Completed", "Failed", "PostProcessingFailed"])

    @patch.object(httpx.Client, "build_request")
    def test_get_portfolio_request(self, mock_Request):
        request_id = 112
        mock_response = Mock(spec=Response)
        mock_response.status_code = 200
        mock_request = Mock(spec=Request)
        mock_request.url = "https://mock_url"
        mock_request.method = "GET"
        mock_response.request = mock_request
        mock_Request.return_value = Request("GET", "https://mock_url")

        with patch.object(
                AxiomaSession.current._session,
                "send",
                return_value=Request(method="GET", url=self.domain),
        ) as mock_session_send:
            mock_session_send.return_value = mock_response
            status_response = AnalysesRiskAPI.get_portfolio_request(request_id)
            url = (
                f"{self.domain}/api/{AxiomaSession.current.api_version}/analyses/risk/portfolios/{request_id}/request"
            )

            mock_Request.assert_called_with(method="GET", url=url, headers=ANY, params=ANY)
            self.assertEqual(status_response.response.status_code, 200)
            self.assertEqual(url, "https://test/REST/api/v1/analyses/risk/portfolios/112/request")

    @patch.object(httpx.Client, "build_request")
    def test_get_analyses(self, mock_Request):
        request_id = 112
        mock_response = Mock(spec=Response)
        mock_response.status_code = 200
        mock_request = Mock(spec=Request)
        mock_request.url = "https://mock_url"
        mock_request.method = "GET"
        mock_response.request = mock_request
        mock_Request.return_value = Request("GET", "https://mock_url")
        mock_response.json.return_value = {
            "tableSchema": {
                "columns": [
                    {
                        "name": "Category Name",
                        "dataType": "string",
                        "groupingColumn": "true"
                    },
                    {
                        "name": "ClientId",
                        "dataType": "string",
                        "groupingColumn": "true"
                    },
                    {
                        "name": "Coverage",
                        "dataType": "string"
                    },
                    {
                        "name": "Instrument Lookup",
                        "dataType": "string"
                    },
                    {
                        "name": "Quantity",
                        "dataType": "int"
                    },
                    {
                        "name": "Market Exposure",
                        "dataType": "double"
                    }
                ]
            },
            "rows": [
                [
                    "Total",
                    "",
                    "Covered(1)",
                    "Ticker = IBM US",
                    "1",
                    "180.0500030518"
                ],
                [
                    "Stock",
                    "",
                    "Covered(1)",
                    "Ticker=IBM US",
                    "1",
                    "180.0500030518"
                ]
            ]
        }

        with patch.object(
                AxiomaSession.current._session,
                "send",
                return_value=Request(method="GET", url=self.domain),
        ) as mock_session_send:
            mock_session_send.return_value = mock_response
            status_response = AnalysesAPI.get_analyses(request_id)
            url = (
                f"{self.domain}/api/{AxiomaSession.current.api_version}/analyses/{request_id}"
            )

            mock_Request.assert_called_with(method="GET", url=url, headers=ANY)
            self.assertEqual(status_response.response.status_code, 200)
            self.assertEqual(url, "https://test/REST/api/v1/analyses/112")
            self.assertIsInstance(status_response.response.json.return_value, dict)


if __name__ == "__main__":
    unittest.main()
