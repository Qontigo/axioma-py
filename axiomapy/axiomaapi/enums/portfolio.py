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
from enum import unique

from axiomapy.entitybase import EnumBase


@unique
class QuantityType(EnumBase):
    """Enum that provides options for the quantity scale for instrument positions.
    """

    NumberOfInstruments = "NumberOfInstruments"
    NotionalValue = "NotionalValue"
    AllocationPercent = "AllocationPercent"
    MarketValue = "MarketValue"
    DirtyMarketValue = "DirtyMarketValue"
    WeightAsPercent = "WeightAsPercent"
    OriginalNotional = "OriginalNotional"
    UnadjustedAssetCount = "UnadjustedAssetCount"
