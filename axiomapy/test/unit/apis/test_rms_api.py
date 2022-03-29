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
from axiomapy.odatahelpers import oDataFilterHelper as od
from httpx import Response, Request
import httpx


class TestRMSAPIMocker(unittest.TestCase):
    @patch.object(SimpleAuthSession, "_authenticate", return_value=True)
    def setUp(self, mock_SimpleAuthSession):
        AxiomaSession.use_session("client_id", "u_name", "pwd", "http://test")
        self.domain = "http://test/REST"

    @patch.object(httpx.Client, "build_request")
    def test_get_risk_model_definitions(self, mock_Request):

        mock_response = Mock(spec=Response)
        mock_response.json.return_value = {'items': [{'id': 3628785,
                            'name': 'DV Risk Model Analysis', 'team': ''},
              {'id': 3884970, 'name': 'DV Risk Model Analysis SH1', 'team': ''},
              {'id': 3709091, 'name': 'DV Risk Model Analysis v3', 'team': ''},
              {'id': 3895000, 'name': 'DV Risk Model Analysis S', 'team': ''},
              {'id': 3890846, 'name': 'DV Risk Model Analysis SH', 'team': ''},
              {'id': 3707082, 'name': 'DV Risk Model Analysis WW', 'team': ''},
              {'id': 3892087, 'name': 'DV Risk Model Analysis SH2', 'team': ''},
              {'id': 3696967, 'name': 'DV Risk Model Analysis v2', 'team': ''}],
                'count': 8,
                'total': 8,
                '_links': {'self': {'href': "/api/v1/risk-model-definitions?"
                                     "$filter=contains(name, 'DV Risk Model ')"},
          'item': {'href': '/api/v1/risk-model-definitions/{id}',
                   'templated': True}}}
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

            filters = [
                od.contains("name", "DV Risk Model")
            ]
            filter_ = " ".join(filters)
            ptf = RiskModelDefinitionsAPI.get_risk_model_definitions(
                filter_results=filter_)
            url = (
                f"{self.domain}/api/{AxiomaSession.current.api_version}/risk-model-definitions"
            )

            mock_Request.assert_called_with(method="GET", url=url, headers=ANY,
                                            params={'$filter': "contains(name, 'DV Risk Model')"})
            self.assertEqual(ptf.response.status_code, 200)
            self.assertEqual(url, "http://test/REST/api/v1/risk-model-definitions")

    @patch.object(httpx.Client, "build_request")
    def test_get_risk_model_definition(self, mock_Request):

        rms_id=123
        mock_response = Mock(spec=Response)
        mock_response.json.return_value = {'name': 'MAC Global',
         'riskModelSettings': {'type': 'macriskmodelsettings',
          'value': 'mac global'},
         'currency': 'usd',
         'riskDecomposition': [{'type': 'risktypedrilldownelem', 'value': 'risktype'},
          {'type': 'riskcomponentdrilldownelem', 'value': 'decomposition.factortypes'},
          {'type': 'riskfactordrilldownelem', 'value': 'riskfactor'}],
         'id': rms_id,
         'lastUpdatedDate': '2021-05-20T20:17:56.807',
         'lastUpdatedBy': 'axioma',
         'modelMatrixOutputAs': 'Standard',
         '_links': {'self': {'href': '/api/v1/risk-model-definitions/3726350'}}}
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


            ptf = RiskModelDefinitionsAPI.get_risk_model_definition(risk_model_definition_id=rms_id)
            url = (
                f"{self.domain}/api/{AxiomaSession.current.api_version}/risk-model-definitions/{rms_id}"
            )

            mock_Request.assert_called_with(method="GET", url=url, headers=ANY)
            self.assertEqual(ptf.response.status_code, 200)
            self.assertEqual(url, "http://test/REST/api/v1/risk-model-definitions/123")

if __name__ == "__main__":
    unittest.main()
