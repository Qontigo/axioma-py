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
from typing import List

from axiomapy.session import AxiomaSession
from axiomapy.utils import odata_params

_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())


class MarketDataSourcesAPI:
    """Access api methods of market data sources using the active session

    """

    @staticmethod
    def get_market_data_sources(
        filter_results: str = None,
        top: int = None,
        skip: int = None,
        orderby: str = None,
        return_response: bool = False,
    ):
        """This method returns a collection of available market data sources

        Args:
            filter_results:user can apply filter to the list
            top:returns top N number of elements
            skip:skips first N elements
            orderby:sorts in particular order
            return_response: If set to true, the response will be returned

        Returns:
            Collection of market data sources
        """
        url = "/market-data-sources"
        params = odata_params(filter_results, top, skip, orderby)
        _logger.info(f"Getting from {url}")
        response = AxiomaSession.current._get(
            url, params=params, return_response=return_response
        )
        return response

    @staticmethod
    def get_market_data_source(
        market_data_source_id: int,
        return_response: bool = False,
    ):
        """This method returns a single market data source based on the id provided

        Args:
            market_data_source_id:market data source id
            return_response: If set to true, the response will be returned

        Returns:
            Returns a market data source
        """
        url = f"/market-data-sources/{market_data_source_id}"
        _logger.info(f"Getting from {url}")
        response = AxiomaSession.current._get(
            url, return_response=return_response
        )
        return response


    @staticmethod
    def get_market_data_instrument_attributes_at_date(
        market_data_source_id: int,
        as_of_date: str,
        filter_results: str = None,
        top: int = None,
        skip: int = None,
        orderby: str = None,
        return_response: bool = False,
    ):
        """This method returns the instrument attributes for a given market data source on a date

        Args:
            market_data_source_id:market data source id for which instruments are requested
            as_of_date: date for the request
            filter_results: user can apply filter to the list
            top: returns top N number of elements
            skip: skips first N elements
            orderby: sorts in particular order
            return_response: If set to true, the response will be returned

        Returns:
            Returns instrument attributes
        """
        url = (
            f"/market-data-sources/{market_data_source_id}/"
            f"instrument-attributes/{as_of_date}"
        )
        params = odata_params(filter_results, top, skip, orderby)
        _logger.info(f"Getting from {url}")
        response = AxiomaSession.current._get(
            url, params=params, return_response=return_response
        )
        return response

    @staticmethod
    def patch_market_data_instrument_attributes(
        market_data_source_id: int,
        instrument_attributes_upsert: List[dict] = None,
        instrument_attributes_remove: List[dict] = None,
        return_response: bool = False,
    ):
        """This method upserts or removes the instrument attributes for a given market data source id

        Args:
            market_data_source_id:market data source id to be modified
            instrument_attributes_upsert:list of elements for upsert
            instrument_attributes_remove:list of elements to be deleted
            return_response: If set to true, the response will be returned

        Returns:
            Success message once the instrument attribute is modified.
        """
        url = f"/market-data-sources/{market_data_source_id}/instrument-attributes"
        if(instrument_attributes_upsert is None):
            instrument_attributes_upsert = []
        if(instrument_attributes_remove is None):
            instrument_attributes_remove = []
        _logger.info(f"Patching to {url}")
        instrument_attributes_patch = {
            "upsert": instrument_attributes_upsert,
            "remove": instrument_attributes_remove,
        }
        response = AxiomaSession.current._patch(
            url, instrument_attributes_patch, return_response=return_response
        )
        return response

    @staticmethod
    def get_market_data_instrument_scenarios_dates(
        market_data_source_id: int,
        return_response: bool = False,
    ):
        """This method returns the available instrument scenario dates for a given market data source id

        Args:
            market_data_source_id: market data source id
            return_response: If set to true, the response will be returned

        Returns:
            Collection of dates
        """
        url = f"/market-data-sources/{market_data_source_id}/instrument-scenarios"
        _logger.info(f"Getting from {url}")
        response = AxiomaSession.current._get(
            url, return_response=return_response
        )
        return response

    @staticmethod
    def get_market_data_instrument_scenarios_at_date(
        market_data_source_id: int,
        as_of_date: str,
        filter_results: str = None,
        top: int = None,
        skip: int = None,
        orderby: str = None,
        return_response: bool = False,
    ):
        """This method returns the instrument scenarios for a given market data source id and date

        Args:
            market_data_source_id: market data source id for instrument scenarios
            as_of_date: date for which instrument scenarios are requested
            filter_results:user can apply filter to the list
            top:returns top N number of elements
            skip:skips first N elements
            orderby:sorts in particular order
            return_response: If set to true, the response will be returned

        Returns:
            Instrument scenario for the given date and market data source
        """
        url = (
            f"/market-data-sources/{market_data_source_id}/"
            f"instrument-scenarios/{as_of_date}"
        )
        params = odata_params(filter_results, top, skip, orderby)
        _logger.info(f"Getting from {url}")
        response = AxiomaSession.current._get(
            url, params=params, return_response=return_response
        )
        return response

    @staticmethod
    def patch_market_data_instrument_scenarios_at_date(
        market_data_source_id: int,
        as_of_date: str,
        instrument_scenarios_upsert: List[dict] = None,
        instrument_scenarios_remove: List[dict] = None,
        return_response: bool = False,
    ):
        """This method upserts or deletes the instrument scenarios for a given market data source id and date.

        Args:
            market_data_source_id: market data source id
            as_of_date: date of request
            instrument_scenarios_upsert:list of elements for upsert
            instrument_scenarios_remove:list of elements to remove
            return_response: If set to true, the response will be returned

        Returns:
            Success message once the instrument scenario is updated
        """
        url = (
            f"/market-data-sources/{market_data_source_id}"
            f"/instrument-scenarios/{as_of_date}"
        )
        if(instrument_scenarios_upsert is None):
            instrument_scenarios_upsert = []
        if(instrument_scenarios_remove is None):
            instrument_scenarios_remove = []
        _logger.info(f"Patching to {url}")
        instrument_scenarios_patch = {
            "upsert": instrument_scenarios_upsert,
            "remove": instrument_scenarios_remove,
        }
        response = AxiomaSession.current._patch(
            url, instrument_scenarios_patch, return_response=return_response
        )
        return response
