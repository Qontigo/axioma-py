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
from axiomapy.axiomaapi import PortfolioGroupsAPI
from axiomapy.session import SimpleAuthSession
from axiomapy import AxiomaSession

import unittest
from unittest.mock import patch, Mock, ANY, MagicMock
from httpx import Response, Request
import httpx
from axiomapy.axiomaexceptions import AxiomaRequestValidationError


class TestPortfolioGroupsAPIMocker(unittest.TestCase):
    @patch.object(SimpleAuthSession, "_authenticate", return_value=True)
    def setUp(self, mock_SimpleAuthSession):
        AxiomaSession.use_session(username="u_name", password="pwd", domain="https://test")
        self.domain = "https://test/REST"

    @patch.object(httpx.Client, "build_request")
    def test_get_portfolio_groups(self, mock_Request):
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
            pg_response = PortfolioGroupsAPI.get_portfolio_groups()
            url = (
                f"{self.domain}/api/{AxiomaSession.current.api_version}/portfolio-groups"
            )

            mock_Request.assert_called_with(method="GET", url=url, headers=ANY)
            self.assertEqual(pg_response.response.status_code, 200)
            self.assertEqual(url, "https://test/REST/api/v1/portfolio-groups")

    @patch.object(httpx.Client, "build_request")
    def test_get_portfolio_group(self, mock_Request):
        portfolio_group_id = 123
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
            pg_response = PortfolioGroupsAPI.get_portfolio_group(portfolio_group_id)
            url = (
                f"{self.domain}/api/{AxiomaSession.current.api_version}/portfolio-groups/{portfolio_group_id}"
            )

            mock_Request.assert_called_with(method="GET", url=url, headers=ANY)
            self.assertEqual(pg_response.response.status_code, 200)
            self.assertEqual(url, "https://test/REST/api/v1/portfolio-groups/123")

    @patch.object(httpx.Client, "build_request")
    def test_put_portfolio_groups(self, mock_Request):
        portfolio_groups_dict = None
        pg_id = 123
        mock_response = MagicMock()
        mock_response.status_code = 422
        mock_response.headers = {}
        mock_request = Mock(spec=Request)
        mock_request.url = "https://mock_url"
        mock_request.method = "PUT"
        mock_response.request = mock_request

        mock_Request.return_value = Request("PUT", "https://mock_url")

        with patch.object(
                AxiomaSession.current._session,
                "send",
                return_value=Request(method="PUT", url=self.domain),
        ) as mock_session_send:
            mock_session_send.side_effect = AxiomaRequestValidationError("Validation Failed", 422, "Validation Failed",
                                                                         "Validation Failed", mock_response, {})
            with self.assertRaises(AxiomaRequestValidationError) as error:
                pg_response = PortfolioGroupsAPI.put_portfolio_group(pg_id, portfolio_groups_dict)
                self.assertEqual(str(error.exception), "Validation Failed")
                self.assertEqual(pg_response.response.status_code, 422)

    @patch.object(httpx.Client, "build_request")
    def test_delete_portfolio_group(self, mock_Request):
        portfolio_group_id = 123
        mock_response = Mock(spec=Response)
        mock_response.status_code = 204
        mock_request = Mock(spec=Request)
        mock_request.url = "https://mock_url"
        mock_request.method = "DELETE"
        mock_response.request = mock_request

        mock_Request.return_value = Request("DELETE", "https://mock_url")

        with patch.object(
                AxiomaSession.current._session,
                "send",
                return_value=Request(method="DELETE", url=self.domain),
        ) as mock_session_send:
            mock_session_send.return_value = mock_response
            pg_response = PortfolioGroupsAPI.delete_portfolio_group(portfolio_group_id)
            url = (
                f"{self.domain}/api/{AxiomaSession.current.api_version}/portfolio-groups/{portfolio_group_id}"
            )

            mock_Request.assert_called_with(method="DELETE", url=url, headers=ANY)
            self.assertEqual(pg_response.response.status_code, 204)
            self.assertEqual(url, "https://test/REST/api/v1/portfolio-groups/123")


if __name__ == "__main__":
    unittest.main()
