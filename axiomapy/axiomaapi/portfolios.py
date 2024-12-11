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


class PortfoliosAPI:
    """Access api methods of portfolios using the active session

    """

    @staticmethod
    def get_portfolios(
        filter_results: str = None,
        top: int = None,
        skip: int = None,
        orderby: str = None,
        return_response: bool = False,
    ):
        """This method is used to get the list of portfolios

        Args:
            filter_results:user can apply filters to the list
            top:returns top N number of elements
            skip:skips first N elements
            orderby:sorts in particular order
            return_response: If set to true, the response will be returned

        Returns:
            list of portfolios
        """
        url = "/portfolios"
        params = odata_params(filter_results, top, skip, orderby)
        _logger.info(f"Getting from {url}")
        response = AxiomaSession.current._get(
            url, params=params, return_response=return_response
        )
        return response

    @staticmethod
    def get_portfolio(
        portfolio_id: int, return_response: bool = False,
    ):
        """This method retrieves a portfolio

        Args:
            portfolio_id: The id of the portfolio that needs to be fetched
            return_response: If set to true, the response will be returned

        Returns:
            A single portfolio
        """
        url = f"/portfolios/{portfolio_id}"
        _logger.info(f"Getting from {url}")
        response = AxiomaSession.current._get(url, return_response=return_response)
        return response

    @staticmethod
    def post_portfolio(
        portfolio: dict, return_response: bool = False,
    ):
        """This method creates a new portfolio

        Args:
            portfolio: portfolio json with the details of portfolio to be created
            return_response: If set to true, the response will be returned

        Returns:
            Success message if the portfolio is created. Code 201.
        """
        url = "/portfolios"
        _logger.info(f"Posting to {url}")
        response = AxiomaSession.current._post(
            url, portfolio, return_response=return_response
        )
        return response

    @staticmethod
    def put_portfolio(
        portfolio_id: int, portfolio: dict, return_response: bool = False,
    ):
        """This method updates an existing portfolio with the provided data

        Args:
            portfolio_id:id of the portfolio
            portfolio:the updated portfolio
            return_response: If set to true, the response will be returned

        Returns:
            Success message if the portfolio is updated. Code 204
        """
        url = f"/portfolios/{portfolio_id}"
        _logger.info(f"Putting to {url}")
        response = AxiomaSession.current._put(
            url, portfolio, return_response=return_response
        )
        return response

    @staticmethod
    def delete_portfolio(
        portfolio_id: int, return_response: bool = False,
    ):
        """This method deletes an existing portfolio

        Args:
            portfolio_id: The id of the portfolio that you would like to delete
            
        Returns:
            Success message if the portfolio is deleted. Code 204

        """
        url = f"/portfolios/{portfolio_id}"
        _logger.info(f"Deleting at {url}")
        response = AxiomaSession.current._delete(url, return_response=return_response)
        return response

    @staticmethod
    def patch_portfolios(
        portfolios_upsert: List[dict] = None,
        portfolios_remove: List[dict] = None,
        return_response: bool = False,
    ):
        """This method is used to update, create, delete positions of a portfolio

        Args:
            portfolios_upsert: The positions that needs to be added to the portfolio
            portfolios_remove: The positions that needs to be removed from the portfolio
            return_response: If set to true, the response will be returned

        Returns:
            Success message of the portfolio is updated
        """
        if(portfolios_upsert is None):
            portfolios_upsert = []
        if (portfolios_remove is None):
            portfolios_remove = []
        url = "/portfolios"
        _logger.info(f"Patching to {url}")
        portfolios_patch = {"upsert": portfolios_upsert, "remove": portfolios_remove}
        response = AxiomaSession.current._patch(
            url, portfolios_patch, return_response=return_response
        )
        return response

    @staticmethod
    def get_position_dates(
        portfolio_id: int,
        start_date: str = None,
        end_date: str = None,
        return_response: bool = False,
    ):
        """This method is used to list dates for which there are positions for the portfolio, latest first

        Args:
            portfolio_id: Id of the portfolio
            start_date: beginning date to filter position dates
            end_date: last date to filter position dates
            return_response: If set to true, the response will be returned

        Returns:
            The dates for which the portfolio is available
        """
        filter_results = None
        if (start_date is not None):
            filter_results = f"asOfDate gt {start_date}"
        if (end_date is not None):
            if filter_results is None:
                filter_results = f"asOfDate lt {end_date}"
            else:
                filter_results = f"{filter_results} and asOfDate lt {end_date}"
        if filter_results is not None:
            url = f"/portfolios/{portfolio_id}/positions?$filter={filter_results}"
        else:
            url = f"/portfolios/{portfolio_id}/positions"
        _logger.info(f"Getting from {url}")
        response = AxiomaSession.current._get(url, return_response=return_response)
        return response

    @staticmethod
    def get_positions_at_date(
        portfolio_id: int,
        as_of_date: str,
        filter_results: str = None,
        top: int = None,
        skip: int = None,
        orderby: str = None,
        return_response: bool = False,
    ):
        """This method is used to list the positions of portfolio on a particular date

        Args:
            portfolio_id: The id of the portfolio for which composition is requested
            as_of_date: The date on which portfolio composition is requested
            filter_results: filters the response to include only the results that meet the criteria
            top: only includes top N results
            skip: Skips the first N results
            orderby: Sorts the results included in the response
            return_response: If set to true, the response will be returned

        Returns:
            Portfolio composition on the specified date
        """
        url = f"/portfolios/{portfolio_id}/positions/{as_of_date}"
        params = odata_params(filter_results, top, skip, orderby)
        _logger.info(f"Getting from {url}")
        response = AxiomaSession.current._get(
            url, params=params, return_response=return_response
        )
        return response

    @staticmethod
    def delete_positions(
        portfolio_id: int, as_of_date: str, return_response: bool = False,
    ):
        """This method is used to delete the portfolio entry on a particular date

        Args:
            portfolio_id: The identity of the portfolio
            as_of_date: The date on which portfolio composition needs to be deleted
            return_response: If set to true, the response will be returned

        Returns:
            Success message that the positions for the date are deleted
        """
        url = f"/portfolios/{portfolio_id}/positions/{as_of_date}"
        _logger.info(f"Deleting from {url}")
        response = AxiomaSession.current._delete(url, return_response=return_response)
        return response

    @staticmethod
    def post_position(
        portfolio_id: int,
        as_of_date: str,
        position: dict,
        return_response: bool = False,
    ):
        """The method is used to create a new position in the portfolio on the given date

        Args:
            portfolio_id:The id of the portfolio
            as_of_date:The date for which position needs to be created
            position:The position of the portfolio that needs to be created
            return_response:If set to true, the response will be returned

        Returns:
            Success message if the positions are created. Code 201.
        """
        url = f"/portfolios/{portfolio_id}/positions/{as_of_date}"
        _logger.info(f"Posting from {url}")
        response = AxiomaSession.current._post(
            url, position, return_response=return_response
        )
        return response

    @staticmethod
    def patch_positions(
        portfolio_id: int,
        as_of_date: str,
        positions_upsert: List[dict] = None,
        positions_remove: List[dict] = None,
        return_response: bool = False,
    ):
        """This method is used to patch the existing positions according to the supplied operations

        Args:
            portfolio_id:the id of the portfolio to update positions in
            as_of_date:The date of the positions
            positions_upsert:The positions that needs to be updated or created
            positions_remove:The positions that needs to be removed
            return_response:If set to true, the response will be returned

        Returns:
            If the positions are updated a success message is returned. Code 200
        """
        if(positions_upsert is None):
            positions_upsert = []
        if(positions_remove is None):
            positions_remove = []
        url = f"/portfolios/{portfolio_id}/positions/{as_of_date}"
        _logger.info(f"Patching from {url}")
        positions_patch = {"upsert": positions_upsert, "remove": positions_remove}
        response = AxiomaSession.current._patch(
            url, positions_patch, return_response=return_response
        )
        return response

    @staticmethod
    def rollover_request(
        portfolio_id: int,
        as_of_date: str,
        rollover_date: str,
        attributes: dict = None,
        return_response: bool = False,
    ):
        """ This method rolls over the positions from the as Of Date to the rollover date provided.

        Args:
            portfolio_id: The id of the portfolio
            as_of_date: The date from where the positions are to be copied
            rollover_date: The date to which the positions are to be copied
            attributes: The optional attributes to be added to all positions
            return_response: if set to true, the response will be returned

        Returns:
            Success message if positions are created. Code 201
        """
        if(attributes is None):
            attributes = {}
        url = f"/portfolios/{portfolio_id}/positions/{as_of_date}/rollover-requests"
        _logger.info(f"Posting to {url}")
        body = {"rollOverToDate": rollover_date, "attributes": attributes}
        response = AxiomaSession.current._post(url, body, return_response=return_response)
        return response

    @staticmethod
    def get_portfolio_benchmark(
        portfolio_id: str, return_response: bool = False,
    ):
        """This method returns the benchmark for the portfolio

        Args:
            portfolio_id:The id of the portfolio
            return_response: If set to true, the response will be returned

        Returns:
            The benchmark for the portfolio
        """
        url = f"/portfolios/{portfolio_id}/benchmark"
        _logger.info(f"Getting from {url}")
        response = AxiomaSession.current._get(url, return_response=return_response)
        return response

    @staticmethod
    def put_portfolio_benchmark(
        portfolio_id: int, benchmark: dict, return_response: bool = False,
    ):
        """This method sets the benchmark for the given portfolio

        Args:
            portfolio_id: The id of the portfolio
            benchmark:The benchmark to be set for the portfolio
            return_response: If set to true, the response will be returned

        Returns:
            Success message if the portfolio is updated with the benchmark. Code 204
        """
        url = f"/portfolios/{portfolio_id}/benchmark"
        _logger.info(f"Putting to {url}")
        response = AxiomaSession.current._put(
            url, benchmark, return_response=return_response
        )
        return response

    @staticmethod
    def delete_portfolio_benchmark(
        portfolio_id: int, return_response: bool = False,
    ):
        """This method deletes the benchmark from the portfolio

        Args:
            portfolio_id:The id of the portfolio
            return_response: If set to true, the response will be returned

        Returns:
            Success message when the benchmark is removed. Code 204
        """
        url = f"/portfolios/{portfolio_id}/benchmark"
        _logger.info(f"Deleting at {url}")
        response = AxiomaSession.current._delete(url, return_response=return_response)
        return response

    @staticmethod
    def get_portfolio_position(
        portfolio_id: int,
        as_of_date: str,
        position_id: int,
        return_response: bool = False,
    ):
        """The method is used to get a position in portfolio on a given date

        Args:
            portfolio_id:The id of the portfolio
            as_of_date:The date for which position needs to be created
            position_id:The position of the portfolio that needs to be fetched
            return_response:If set to true, the response will be returned

        Returns:
            Position as per the id. Code 201.
        """
        url = f"/portfolios/{portfolio_id}/positions/{as_of_date}/{position_id}"
        _logger.info(f"Get from {url}")
        response = AxiomaSession.current._get(
            url, return_response=return_response
        )
        return response

    @staticmethod
    def put_portfolio_position(
        portfolio_id: int,
        as_of_date: str,
        position_id: int,
        position: dict,
        return_response: bool = False,
    ):
        """The method replaces the portfolio position for the given date

        Args:
            portfolio_id: The id of the portfolio
            as_of_date: The date for which position needs to be updated
            position_id: The id of the position
            position: Updated position for the portfolio
            return_response: If set to true, the response will be returned

        Returns:
            Success message if the position is updated. Code 204
        """
        url = f"/portfolios/{portfolio_id}/positions/{as_of_date}/{position_id}"
        _logger.info(f"Put request at {url}")
        response = AxiomaSession.current._put(
            url, position, return_response=return_response
        )
        return response

    @staticmethod
    def delete_portfolio_position(
            portfolio_id: int,
            as_of_date: str,
            position_id: int,
            return_response: bool = False,
    ):
        """The method is used to delete a position in portfolio on a given date

        Args:
            portfolio_id: The id of the portfolio
            as_of_date: The date for which position needs to be created
            position_id: The position of the portfolio that needs to be deleted
            return_response: If set to true, the response will be returned

        Returns:
            Success message if position is deleted as per the id. Code 204.
        """
        url = f"/portfolios/{portfolio_id}/positions/{as_of_date}/{position_id}"
        _logger.info(f"Delete from {url}")
        response = AxiomaSession.current._delete(
            url, return_response=return_response
        )
        return response

    @staticmethod
    def get_valuation_dates(
        portfolio_id: int, return_response: bool = False,
    ):
        """This method lists the dates there are Valuations for the portfolio, latest first

        Args:
            portfolio_id: The id of the portfolio
            return_response: If set to true, the response will be returned

        Returns:
            The collection of the Valuations dates
        """
        url = f"/portfolios/{portfolio_id}/valuations"
        _logger.info(f"Getting from {url}")
        response = AxiomaSession.current._get(url, return_response=return_response)
        return response

    @staticmethod
    def get_valuation_at_date(
        portfolio_id: int,
        as_of_date: str,
        filter_results: str = None,
        top: int = None,
        skip: int = None,
        orderby: str = None,
        return_response: bool = False,
    ):
        """This method retrieves the portfolio valuation for a given date

        Args:
            portfolio_id: id of the portfolio
            as_of_date:The date for which valuation is requested
            filter_results: filters the response to include only the results that meet the criteria
            top:only includes top N results
            skip:Skips the first N results
            orderby:Sorts the results included in the response
            return_response: If set to true, the response will be returned

        Returns:
            The portfolio valuation for the specified date
        """
        url = f"/portfolios/{portfolio_id}/valuations/{as_of_date}"
        params = odata_params(filter_results, top, skip, orderby)
        _logger.info(f"Getting from {url}")
        response = AxiomaSession.current._get(
            url, params=params, return_response=return_response
        )
        return response

    @staticmethod
    def delete_valuation(
        portfolio_id: int, as_of_date: str, return_response: bool = False,
    ):
        """The method deletes the specified valuation from the portfolio for a given date

        Args:
            portfolio_id:id of the portfolio
            as_of_date:the date for which valuation needs to be deleted
            return_response: If set to true, the response will be returned

        Returns:
            Success message when the valuation is deleted. Code 204
        """
        url = f"/portfolios/{portfolio_id}/valuations/{as_of_date}"
        _logger.info(f"Deleting from {url}")
        response = AxiomaSession.current._delete(url, return_response=return_response)
        return response

    @staticmethod
    def post_valuation(
        portfolio_id: int,
        as_of_date: str,
        valuation: dict,
        return_response: bool = False,
    ):
        """The method creates or updates the portfolio valuation for the portfolio on the given date

        Args:
            portfolio_id:id of the portfolio
            as_of_date:the date for which valuation needs to be created or updated
            valuation:portfolio valuation
            return_response: If set to true, the response will be returned

        Returns:
            Success message if the valuation is created. Code 201
        """
        url = f"/portfolios/{portfolio_id}/valuations/{as_of_date}"
        _logger.info(f"Posting from {url}")
        response = AxiomaSession.current._post(
            url, valuation, return_response=return_response
        )
        return response

    @staticmethod
    def put_valuation(
        portfolio_id: int,
        as_of_date: str,
        valuation: dict,
        return_response: bool = False,
    ):
        """The method replaces or creates the portfolio valuation for the given date

        Args:
            portfolio_id:id of the portfolio
            as_of_date:the date for which valuation needs to be created or updated
            valuation:valuation of the portfolio
            return_response: If set to true, the response will be returned

        Returns:
            Success message if the valuation is updated. Code 204
        """
        url = f"/portfolios/{portfolio_id}/valuations/{as_of_date}"
        _logger.info(f"Put request at {url}")
        response = AxiomaSession.current._put(
            url, valuation, return_response=return_response
        )
        return response

    @staticmethod
    def patch_valuations(
        portfolio_id: int,
        as_of_date: str,
        valuations_upsert: List[dict] = None,
        valuations_remove: List[dict] = None,
        return_response: bool = False,
    ):
        """This method patches the existing collection of portfolio valuations according to the inputs

        Args:
            portfolio_id:id of the portfolio
            as_of_date:the date for which valuations are being patched
            valuations_upsert:valuations to be created or updated
            valuations_remove:the valuations that needs to be deleted
            return_response: If set to true, the response will be returned

        Returns:
            Success message if the valuations are patched. Code 200
        """
        if valuations_upsert is None:
            valuations_upsert = []
        if valuations_remove is None:
            valuations_remove = []

        url = f"/portfolios/{portfolio_id}/valuations"
        _logger.info(f"Patching from {url}")
        valuations_patch = {"upsert": valuations_upsert, "remove": valuations_remove}
        response = AxiomaSession.current._patch(
            url, valuations_patch, return_response=return_response
        )
        return response
