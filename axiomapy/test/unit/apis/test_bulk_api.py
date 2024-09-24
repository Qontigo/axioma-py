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
from axiomapy.axiomaapi import BulkAPI
from axiomapy.session import SimpleAuthSession
from axiomapy import AxiomaSession

import unittest
from unittest.mock import patch, Mock, ANY
from httpx import Response, Request
import httpx


class TestBulkAPIMocker(unittest.TestCase):
    @patch.object(SimpleAuthSession, "_authenticate", return_value=True)
    def setUp(self, mock_SimpleAuthSession):
        AxiomaSession.use_session(username="u_name", password="pwd", domain="https://test", api_type="BULK")
        self.domain = "https://test/BULK"

    @patch.object(httpx.Client, "build_request")
    def test_patch_portfolios(self, mock_Request):
        as_of_date = "2023-01-13"
        payload = {
            "description": "My set of portfolios",
            "portfolios": [
                {
                    "name": "TestPortfolio1",
                    "upsert": [
                        {
                            "clientId": "IBM",
                            "identifiers": [
                                {
                                    "type": "Ticker",
                                    "value": "MSFT"
                                }
                            ],
                            "description": "Creating  a position",
                            "Quantity": {
                                "value": 123,
                                "scale": "NumberOfInstruments"
                            },
                            "attributes": {
                                "Country Of Risk": "USA",
                                "Swap Tenor": "20Y"
                            }
                        },
                        {
                            "clientId": "MyApple",
                            "identifiers": [
                                {
                                    "type": "Ticker",
                                    "value": "APPL"
                                }
                            ],
                            "description": "Updating a position",
                            "Quantity": {
                                "value": 456,
                                "scale": "NumberOfInstruments"
                            }
                        }
                    ],
                    "remove": [
                        {
                            "clientId": "BHP123"
                        }
                    ]
                },
                {
                    "name": "TestPortfolio2",
                    "remove": [
                        {
                            "clientId": "BHP789"
                        }
                    ]
                }
            ]
        }
        mock_response = Mock(spec=Response)
        mock_response.status_code = 200
        mock_request = Mock(spec=Request)
        mock_request.url = "https://mock_url"
        mock_request.method = "PATCH"
        mock_response.request = mock_request

        mock_Request.return_value = Request("PATCH", "https://mock_url")

        with patch.object(
                AxiomaSession.current._session,
                "send",
                return_value=Request(method="PATCH", url=self.domain),
        ) as mock_session_send:
            mock_session_send.return_value = mock_response
            bulk_response = BulkAPI.patch_portfolios_payload(as_of_date=as_of_date, payload=payload)
            url = (
                f"{self.domain}/api/{AxiomaSession.current.api_version}/positions/{as_of_date}"
            )

            mock_Request.assert_called_with(method="PATCH", url=url, headers=ANY, json=payload)
            self.assertEqual(bulk_response.status_code, 200)
            self.assertEqual(url, "https://test/BULK/api/v1/positions/2023-01-13")

    @patch.object(httpx.Client, "build_request")
    def test_delete_positions(self, mock_Request):
        as_of_date = "2024-07-02"
        payload = {
            "description": "My set of portfolios",
            "portfolios": [
                "TestPortfolio1",
                "TestPortfolio2",
            ]
        }
        mock_response = Mock(spec=Response)
        mock_response.status_code = 200
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
            bulk_response = BulkAPI.delete_portfolios_payload(as_of_date=as_of_date, payload=payload)
            url = (
                f"{self.domain}/api/{AxiomaSession.current.api_version}/positions/{as_of_date}"
            )

            mock_Request.assert_called_with(method="DELETE", url=url, headers=ANY, json=payload)
            self.assertEqual(bulk_response.status_code, 200)
            self.assertEqual(url, f"https://test/BULK/api/v1/positions/{as_of_date}")


if __name__ == "__main__":
    unittest.main()
