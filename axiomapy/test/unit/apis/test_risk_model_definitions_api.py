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
from axiomapy.axiomaapi import RiskModelDefinitionsAPI
from axiomapy.session import SimpleAuthSession
from axiomapy import AxiomaSession

import unittest
from unittest.mock import patch, Mock, ANY
from httpx import Response, Request
import httpx


class TestRiskModelDefinitionsAPIMocker(unittest.TestCase):
    @patch.object(SimpleAuthSession, "_authenticate", return_value=True)
    def setUp(self, mock_SimpleAuthSession):
        AxiomaSession.use_session(username="u_name", password="pwd", domain="http://test")
        self.domain = "http://test/REST"

    @patch.object(httpx.Client, "build_request")
    def test_get_risk_model_definitions(self, mock_Request):
        mock_response = Mock(spec=Response)
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_request = Mock(spec=Request)
        mock_request.url = "http://mock_url"
        mock_response.request = mock_request

        mock_Request.return_value = Request("GET", "http://mock_url")

        with patch.object(
                AxiomaSession.current._session,
                "send",
                return_value=Request(method="GET", url=self.domain),
        ) as mock_session_send:
            mock_session_send.return_value = mock_response
            rmd = RiskModelDefinitionsAPI.get_risk_model_definitions()
            url = (
                f"{self.domain}/api/{AxiomaSession.current.api_version}/risk-model-definitions"
            )

            mock_Request.assert_called_with(method="GET", url=url, headers=ANY)
            self.assertEqual(rmd.response.status_code, 200)
            self.assertEqual(url, "http://test/REST/api/v1/risk-model-definitions")

    @patch.object(httpx.Client, "build_request")
    def test_get_risk_model_definition(self, mock_Request):
        risk_model_def_id = 123
        mock_response = Mock(spec=Response)
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_request = Mock(spec=Request)
        mock_request.url = "http://mock_url"
        mock_response.request = mock_request

        mock_Request.return_value = Request("GET", "http://mock_url")

        with patch.object(
                AxiomaSession.current._session,
                "send",
                return_value=Request(method="GET", url=self.domain),
        ) as mock_session_send:
            mock_session_send.return_value = mock_response
            rmd = RiskModelDefinitionsAPI.get_risk_model_definition(risk_model_def_id)
            url = (
                f"{self.domain}/api/{AxiomaSession.current.api_version}/risk-model-definitions/{risk_model_def_id}"
            )

            mock_Request.assert_called_with(method="GET", url=url, headers=ANY)
            self.assertEqual(rmd.response.status_code, 200)
            self.assertEqual(url, "http://test/REST/api/v1/risk-model-definitions/123")


if __name__ == "__main__":
    unittest.main()
