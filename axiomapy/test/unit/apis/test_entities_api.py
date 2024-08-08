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
from axiomapy.axiomaapi import EntitiesAPI
from axiomapy.session import SimpleAuthSession
from axiomapy import AxiomaSession

import unittest
from unittest.mock import patch, Mock, ANY
from axiomapy.odatahelpers import oDataFilterHelper as od
from httpx import Response, Request
import httpx


class TestEntitiesAPIMocker(unittest.TestCase):
    @patch.object(SimpleAuthSession, "_authenticate", return_value=True)
    def setUp(self, mock_SimpleAuthSession):
        AxiomaSession.use_session(username="u_name", password="pwd", domain="https://test")
        self.domain = "https://test/REST"

    @patch.object(httpx.Client, "build_request")
    def test_get_entities(self, mock_Request):
        type_name = 'PerformanceAttributionSettings'
        mock_response = Mock(spec=Response)
        mock_response.json.return_value = {'items': [{'name': 'PA-MAC-Global-USD',
                                                      'refType': {type_name},
                                                      'namespace': 'PerformanceAttributionSettings',
                                                      'xmlCupboardId': 2136463,
                                                      'entityOwner': 'Axioma',
                                                      'entityOwnerType': 'NotPermissioned'},
                                                     {'name': 'PA-MAC-Global-USD-FI',
                                                      'refType': {type_name},
                                                      'namespace': 'PerformanceAttributionSettings',
                                                      'xmlCupboardId': 2136470,
                                                      'entityOwner': 'Axioma',
                                                      'entityOwnerType': 'NotPermissioned'},
                                                     {'name': 'PA-MAC-Global-USD-FI-v2',
                                                      'refType': {type_name},
                                                      'namespace': 'PerformanceAttributionSettings',
                                                      'xmlCupboardId': 3536394,
                                                      'entityOwner': 'Axioma',
                                                      'entityOwnerType': 'NotPermissioned'}],
                                           'count': 3,
                                           'total': 3,
                                           '_links': {'self': {
                                               'href': "/api/v1/entities/PerformanceAttributionSettings/*?$filter=contains(name, 'PA-MAC-Global-USD')"},
                                               'item': {
                                                   'href': '/api/v1/entities/PerformanceAttributionSettings/*/{id}',
                                                   'templated': True}}}
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

            type_name = 'PerformanceAttributionSettings'
            filters = [
                od.contains("name", "PA-MAC-Global-USD")
            ]
            filter_ = " ".join(filters)
            entities = EntitiesAPI.get_entities(typeName1=type_name, filter_results=filter_)
            url = (
                f"{self.domain}/api/{AxiomaSession.current.api_version}/entities/{type_name}/*"
            )

            mock_Request.assert_called_with(method="GET", url=url, headers=ANY,
                                            params={'$filter': "contains(name, 'PA-MAC-Global-USD')"})
            self.assertEqual(entities.response.status_code, 200)
            self.assertEqual(url, "https://test/REST/api/v1/entities/PerformanceAttributionSettings/*")


if __name__ == "__main__":
    unittest.main()
