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
from axiomapy.axiomaapi import PortfoliosAPI
from axiomapy.session import SimpleAuthSession
from axiomapy import AxiomaSession

import unittest
from unittest.mock import patch, Mock, ANY

from httpx import Response, Request
import httpx


class TestPortfolioAPIMocker(unittest.TestCase):
    @patch.object(SimpleAuthSession, "_authenticate", return_value=True)
    def setUp(self, mock_SimpleAuthSession):
        AxiomaSession.use_session(username="u_name", password="pwd",
                                  domain="http://test")
        self.domain = "http://test/REST"

    @patch.object(httpx.Client, "build_request")
    def test_get_portfolio(self, mock_Request):
        p_id = 1234
        mock_response = Mock(spec=Response)
        mock_response.json.return_value = {
            "id": p_id,
            "name": "USAssets",
            "longName": "USAssets Long Name",
            "description": "USAssets Description",
            "defaultCurrency": "USD",
            "defaultDataPartition": "Axioma",
            "riskDataSource": "Default",
            "defaultRiskModel": {"type": "Axioma", "name": "WW21AxiomaSH-S"},
            "benchmark": {
                "identifiers": [{"type": "PortfolioId", "value": "4567"}],
                "name": "Benchmark portfolio",
            },
            "attributes": {"CurrencyRisk": "Regular",
                           "OriginalCurrency": "USD"},
            "createdDate": "2018-12-31T23:59:59",
            "lastUpdatedDate": "2019-01-02T03:04:05",
            "lastUpdatedBy": "bob",
            "latestPositionDate": "2019-01-02",
            "_links": {
                "self": {"href": "/api/v1/portfolios/1234"},
                "benchmark": {
                    "href": "/api/v1/portfolios/1234/benchmark",
                    "title": "My Benchmark",
                },
                "positions": {"href": "/api/v1/portfolios/1234/positions"},
                "positions:latest": {
                    "href": "/api/v1/portfolios/1234/positions/2019-01-02",
                    "title": "The latest Positions for this Portfolio",
                },
                "analysis:aggregation": {
                    "href": "/api/v1/analyses/risk/portfolios/1234",
                    "method": "POST",
                    "title": "Portfolio-level Aggregation (single portfolio)",
                },
                "analysis:performance": {
                    "href": "/api/v1/analyses/performance/portfolios/1234",
                    "method": "POST",
                    "title": "Portfolio-level Performance Analysis (single portfolio)",
                },
            },
        }
        mock_response.status_code = 200
        mock_response.text = "Mock Text"
        mock_response.content = "Mock Content"
        mock_response.headers = {}
        mock_request = Mock(spec=Request)
        mock_request.url = "http://mock_url"
        mock_request.method = "Mock method"
        mock_request.headers = {}
        mock_response.elapsed = Mock(return_value=0)
        mock_response.request = mock_request

        mock_Request.return_value = Request("GET", "http://mock_url")

        with patch.object(
                AxiomaSession.current._session,
                "send",
                return_value=Request(method="GET", url=self.domain),
        ) as mock_session_send:
            mock_session_send.return_value = mock_response

            ptf = PortfoliosAPI.get_portfolio(1234)
            url = (
                f"{self.domain}/api/{AxiomaSession.current.api_version}/portfolios/{p_id}"
            )

            mock_Request.assert_called_with(method="GET", url=url, headers=ANY)
            self.assertEqual(ptf.response.status_code, 200)
            self.assertEqual(url, "http://test/REST/api/v1/portfolios/1234")

    @patch.object(PortfoliosAPI, "get_portfolios")
    def test_get_portfolios(self, get_portfolios_mock):
        sample_response = {
            "items": [
                {
                    "id": 123312,
                    "name": "Test_portfolio_SH1",
                    "description": "Test_portfolio_SH1",
                    "defaultDataPartition": "AxiomaUS",
                    "riskDataSource": "Default",
                    "latestPositionDate": "2020-01-03",
                }
            ],
            "count": 1,
            "total": 1,
            "_links": {
                "self": {
                    "href": "/api/v1/portfolios?$filter=contains(name, 'Test_portfolio_SH1')"
                },
                "item": {"href": "/api/v1/portfolios/{id}", "templated": True},
                "benchmark": {
                    "href": "/api/v1/portfolios/{id}/benchmark",
                    "templated": True,
                },
                "positions": {
                    "href": "/api/v1/portfolios/{id}/positions",
                    "templated": True,
                    "title": "List the dates for which the Portfolio has Positions",
                },
                "positions:latest": {
                    "href": "/api/v1/portfolios/{id}/positions/{latestPositionDate}",
                    "templated": True,
                    "title": "The latest Positions for the Portfolio",
                },
                "valuations": {
                    "href": "/api/v1/portfolios/{id}/valuations",
                    "templated": True,
                },
                "analysis:aggregation": {
                    "href": "/api/v1/analyses/risk/portfolios/{id}",
                    "templated": True,
                    "method": "POST",
                    "title": "Portfolio-level Aggregation (single portfolio)",
                },
                "analysis:performance": {
                    "href": "/api/v1/analyses/performance/portfolios/{id}",
                    "templated": True,
                    "method": "POST",
                    "title": "Portfolio-level Performance Analysis (single portfolio)",
                },
                "analysis:precompute-analytics": {
                    "href": "/api/v1/analyses/performance/portfolios/{id}/precompute-analytics",
                    "templated": True,
                    "method": "POST",
                    "title": "Portfolio-level Performance Analysis (single portfolio precompute-analytics)",
                },
            },
        }

        get_portfolios_mock.return_value = sample_response

        ptfs = PortfoliosAPI.get_portfolios(
            filter_results="name eq Test_portfolio_SH1")

        get_portfolios_mock.assert_called_with(
            filter_results="name eq Test_portfolio_SH1")

        self.assertEqual(ptfs, sample_response)


if __name__ == "__main__":
    unittest.main()
