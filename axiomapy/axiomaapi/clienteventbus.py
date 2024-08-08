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

import logging
from axiomapy.session import AxiomaSession
from axiomapy.utils import odata_params
from axiomapy.odatahelpers import oDataFilterHelper as od

_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())


class ClientEventBusAPI:
    """Access to Axioma Client Event Bus endpoints using the active session
    """

    @staticmethod
    def get_events(return_response: bool = True):
        """The method is to get links to event resources

        Args:
            return_response: If set to true, the response will be returned.

        Returns:
            Collection of links. Status code 200
        """
        url = "/events"
        _logger.info(f"Get to {url}")
        response = AxiomaSession.current._get(
            url, return_response=return_response
        )
        return response

    @staticmethod
    def get_all_market_data(date: str,
                            sort_order: str = 'desc',
                            filter_results: str = None,
                            top: int = None,
                            skip: int = None,
                            orderby: str = None,
                            return_response: bool = True):
        """
        This function is used to fetch a collection of market data events

        Args:
            date: market data only after this date would be fetched
            sort_order: sorts the data as per eventTime and sort_order param, can be asc or desc
            filter_results: user can apply additional filters to the data list
            top: returns top N number of elements
            skip: skips first N elements
            orderby: sorts in particular order
            return_response: If set to true, the response will be returned

        Returns:
            list of market data events
        """
        filter_query = f"eventTime gt {date}T00:00:00.0000z"
        if filter_results is not None:
            filter_query= f"{filter_query}&{filter_results}"
        if orderby is not None:
            order_param = f"eventTime {sort_order}, {orderby}"
        else:
            order_param = f"eventTime {sort_order}"

        url = f"/events/market-data?$filter={filter_query}"
        _logger.info(f"Get to {url}")
        params = odata_params(o_top=top, o_skip=skip, o_orderby=order_param)
        response = AxiomaSession.current._get(
            url, params=params, return_response=return_response
        )
        return response

    @staticmethod
    def get_market_data(market_data_id: str,
                        return_response: bool = True):
        """
        This function is used to fetch a market data event

        Args:
            market_data_id: id of the market data event
            return_response: If set to true, the response will be returned

        Returns:
            Market data event as per the event id
        """
        url = f"/events/market-data/{market_data_id}"
        _logger.info(f"Get to {url}")
        response = AxiomaSession.current._get(
            url, return_response=return_response
        )
        return response
