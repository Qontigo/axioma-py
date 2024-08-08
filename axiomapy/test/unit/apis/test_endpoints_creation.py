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
import unittest
from axiomapy import AxiomaSession


class mock_headers():
    def __init__(self):
        self.headers = {"Content-Type": "application/json"}


class mock_session():
    def __init__(self, domain="https://qa.axioma.com/", api_type="rest",
                 api_version="v1"):
        self._session = mock_headers()
        self.domain = domain
        self.api_version = api_version
        self.api_type = api_type


class TestEndpointMocker(unittest.TestCase):
    def test_local_endpoint(self):
        session1 = mock_session(domain="https://localhost:8681/", api_type="")
        response = AxiomaSession._prepare_request_args(session1, 'GET',
                                                       '/api/v1/analyses/risk/portfolios')
        self.assertEqual(response[0],
                         'https://localhost:8681/api/v1/analyses/risk/portfolios')

    def test_qa_endpoint(self):
        session1 = mock_session(domain="https://qa.axioma.com/",
                                api_type="rest")
        response = AxiomaSession._prepare_request_args(session1, 'GET',
                                                       '/api/v1/analyses/risk/portfolios')
        self.assertEqual(response[0],
                         'https://qa.axioma.com/rest/api/v1/analyses/risk/portfolios')


if __name__ == "__main__":
    unittest.main()
