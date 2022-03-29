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
import unittest
from unittest.mock import patch

from axiomapy import AxiomaSession
from axiomapy.axiomaapi import PortfoliosAPI
from axiomapy.session import SimpleAuthSession


class TestPortfolioToAPIMocks(unittest.TestCase):
    @patch.object(SimpleAuthSession, "_authenticate", return_value=True)
    def setUp(self, mock_SimpleAuthSession):
        AxiomaSession.use_session("client_id", "u_name", "pwd", "http://test")

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

        get_portfolios_mock.assert_called_with(filter="name eq Test_portfolio_SH1")

        self.assertEqual(ptfs, sample_response)

    @patch.object(PortfoliosAPI, "get_portfolio")
    @patch.object(PortfoliosAPI, "get_portfolios")
    def test_get_portfolio(self, get_portfolios_mock, get_portfolio_mock):

        pos = {"name": "Test_portfolio"}

        resp_ptfs = PortfoliosAPI.post_portfolio(portfolio=pos)

        get_portfolios_mock.return_value = list(resp_ptfs)
        get_portfolio_mock.return_value = resp_ptfs

        ptf = PortfoliosAPI.get_portfolio(portfolio_id=5)

        get_portfolio_mock.assert_called_with(portfolio_id=5)

        self.assertEqual(ptf, resp_ptfs)


if __name__ == "__main__":
    unittest.main()
