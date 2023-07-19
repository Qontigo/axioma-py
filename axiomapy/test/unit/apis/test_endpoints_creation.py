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
