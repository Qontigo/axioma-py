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
from datetime import datetime
from typing import Optional, Union


def odata_params(
    o_filter: str = None, o_top: int = None, o_skip: int = None, o_orderby: str = None
) -> dict:
    """Helper function for building the odata parameters

    Arguments:
        filter {[type]} -- e.g. "contains(name, 'portfolio1')"
        top {[type]} -- e.g. 10
        skip {[type]} -- e.g. 10
        orderby {[type]} -- e.g. "name desc"
    """
    payload = {}
    if o_filter:
        payload["$filter"] = o_filter
    if o_top:
        payload["$top"] = o_top
    if o_skip:
        payload["$skip"] = o_skip
    if o_orderby:
        payload["$orderby"] = o_orderby
    return payload


def date_arg_fmt(
    date: Union[str, datetime], format: str = "%Y-%m-%d", in_format: str = None
) -> Optional[str]:
    """Returns a string representation of the date according to the format parameter.
    If None is passed, returns None.
    If a string is passed then date_arg_parse is called with in_format arg.

    Arguments:
        date {Union[str, datetime]} -- a string (with format given by in_format) or
        datetime

    Keyword Arguments:
        format {str} -- the returned format of the date as str (default: {"%Y-%m-%d"})
        in_format {str} -- if a string is passed the format used to parse to date; if
        in_format is not set the value for format will be used.
        (default: in_format)
    Returns:
        str -- date formatted according to format
    """
    if date is None:
        return date
    if not in_format:
        in_format = format
    out_datetime = date_arg_parse(date, in_format)
    out_date_str = out_datetime.strftime(format)
    return out_date_str


def date_arg_parse(
    date: Union[str, datetime], format: str = "%Y-%m-%d", as_date_type: bool = False
) -> Union[datetime]:
    """Returns string parsed to datetime using format. If a datetime is passed it is
    returned unchanged.

    Arguments:
        date {Union[str, datetime]} -- str to parse or datetime

    Keyword Arguments:
        format {str} -- format used to parse if string passed (default: {"%Y-%m-%d"})

    Returns:
        datetime -- parse datetime
    """
    out_datetime = date
    if isinstance(date, str):
        # check it is a date
        out_datetime = datetime.strptime(date, format)

        if as_date_type:
            out_datetime = out_datetime.date()
    return out_datetime


def location_from_header(headers: dict, header: str = "Location", position: int = -1):
    """Accesses the given header (Case-insensitive) and splits the value on '/' and
    returns the value at position

    Args:
        headers (dict): A dict or dict like of headers
        header (str, optional): The header name. Defaults to "Location".
        position (int, optional): The position to extract. Defaults to -1.
    """
    for h in headers.keys():
        if h.lower() == header.lower():
            value = headers[h].split("/")[position]
            return value
    raise LookupError(f"Could not find header {header} in passed headers object")
