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
from typing import Union

_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())


class BulkAPI:
    """Perform bulk actions using the active session

    Returns:
        [type]: [description]
    """

    @staticmethod
    def patch_portfolios_payload(
        as_of_date: str,
            payload: Union[dict, bytes],
            headers: dict = None,
            return_response: bool = True
    ):
        """The method is to update multiple portfolios in a single request

        Args:
            as_of_date: date on which portfolios need to be updated
            payload: portfolios along with update/remove properties; can be dictionary or compressed
            headers: Optional headers, if any required (Content-Encoding for zip , Accept-Encoding)
            return_response: If set to true, the response will be returned.

        Returns:
            Success message if portfolios are updated. Status code 200
        """
        url = f"/positions/{as_of_date}"
        _logger.info(f"Patching to {url}")
        response = AxiomaSession.current._patch(
            url, payload, headers=headers, return_response=return_response
        )

        return response

    @staticmethod
    def post_rollover_positions(
            payload: dict,
            headers: dict = None,
            return_response: bool = True
    ):
        """The method performs the positions rollover of one or more portfolios via a single portfolio group or by multiple portfolios

        Args:
            payload: Portfolio names or portfolio group name for which the positions rollover is to be done along with rollOverToDate
            headers: Optional headers, if any required (Content-Encoding for zip , Accept-Encoding)
            return_response: If set to true, the response will be returned.

        Returns:
            Success message if portfolios are updated. Status code 200
        """
        url = f"/positions/rollover-requests"
        _logger.info(f"Posting to {url}")
        response = AxiomaSession.current._post(
            url, payload, headers=headers, return_response=return_response
        )

        return response