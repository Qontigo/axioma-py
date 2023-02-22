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
import logging
from axiomapy.session import AxiomaSession
from axiomapy.utils import odata_params

_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())


class PortfolioGroupsAPI:
    """Access api methods of portfolios using the active session

    """

    @staticmethod
    def get_portfolio_groups(
        filter_results: str = None,
        top: int = None,
        skip: int = None,
        orderby: str = None,
        return_response: bool = False,
    ):
        """This method lists the portfolio groups

        Args:
            filter_results: user can filter the response to include only those meeting the criteria
            top: returns top N number of elements
            skip: skips first N elements
            orderby: sorts the results included in the response
            return_response: If set to true, the response will be returned

        Returns:
            Collection of portfolio groups
        """
        url = "/portfolio-groups"
        params = odata_params(filter_results, top, skip, orderby)
        _logger.info(f"Getting from {url}")
        response = AxiomaSession.current._get(
            url, params=params, return_response=return_response
        )
        return response

    @staticmethod
    def get_portfolio_group(
        portfolio_group_id: int,
        return_response: bool = False,
    ):
        """This method fetches a particular portfolio group based on the id provided

        Args:
            portfolio_group_id: id of the portfolio group
            return_response: If set to true, the response will be returned

        Returns:
            Single portfolio group in response
        """
        url = f"/portfolio-groups/{portfolio_group_id}"
        _logger.info(f"Getting from {url}")
        response = AxiomaSession.current._get(
            url, return_response=return_response
        )
        return response

    @staticmethod
    def post_portfolio_group(
        portfolio: dict, return_response: bool = False,
    ):
        """This method creates a new portfolio group

        Args:
            portfolio: the parameters that represent the portfolio group
            return_response: If set to true, the response will be returned

        Returns:
            Success message if the portfolio group is created successfully. Code 201.
        """
        url = "/portfolio-groups"
        _logger.info(f"Posting to {url}")
        response = AxiomaSession.current._post(
            url, portfolio, return_response=return_response
        )
        return response

    @staticmethod
    def put_portfolio_group(
        portfolio_group_id: int,
        portfolio: dict,
        return_response: bool = False,
    ):
        """This method updates an existing portfolio group based on the portfolio group id provided

        Args:
            portfolio_group_id: id of the portfolio group
            portfolio: parameters for the updated portfolio group
            return_response: If set to true, the response will be returned

        Returns:
            Success message if the portfolio group is updated successfully. Code 204
        """
        url = f"/portfolio-groups/{portfolio_group_id}"
        _logger.info(f"Putting to {url}")
        response = AxiomaSession.current._put(
            url, portfolio, return_response=return_response
        )
        return response

    @staticmethod
    def delete_portfolio_group(
        portfolio_group_id: int, return_response: bool = False,
    ):
        """This method deletes a portfolio group based on the id provided

        Args:
            portfolio_group_id: portfolio group to be deleted
            return_response: If set to true, the response will be returned

        Returns:
            Success message if the portfolio group is deleted successfully. Code 204
        """
        url = f"/portfolio-groups/{portfolio_group_id}"
        _logger.info(f"Deleting at {url}")
        response = AxiomaSession.current._delete(url, return_response=return_response)
        return response

    @staticmethod
    def patch_portfolio_groups(portfolio_group_id: int,
                               portfolios_dict: dict,
                               return_response: bool = False):
        """This method patches a portfolio group based on the json provided

        Args:
            portfolio_group_id: portfolio group to be updated
            portfolios_dict: portfolios to upsert or remove from the portfolio group
            return_response: If set to true, the response will be returned

        Returns:
            Success message if the portfolio group is updated successfully. Code 204
        """
        url = f"/portfolio-groups/{portfolio_group_id}/portfolios"
        _logger.info(f"Patching portfolios at {url}")
        response = AxiomaSession.current._patch(url, portfolios_dict,
                                                return_response=return_response)
        return response
