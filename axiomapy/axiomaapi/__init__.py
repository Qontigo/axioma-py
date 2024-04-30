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
from .analyses import AnalysesPerformanceAPI, AnalysesRiskAPI, AnalysesAPI
from .analysisdefinitions import AnalysisDefinitionAPI
from .batchdefinitions import BatchDefinitionsAPI
from .bulk import BulkAPI
from .entities import EntitiesAPI
from .enums import (
    AggregateOption,
    ComputeOption,
    DataPartition,
    FinishedStatuses,
    IdentifierType,
    QuantityType,
    Status,
)
from .marketdatasources import MarketDataSourcesAPI
from .metadata import MetaDataAPI
from .portfoliogroups import PortfolioGroupsAPI
from .portfolios import PortfoliosAPI
from .riskmodeldefinitions import RiskModelDefinitionsAPI
from .templates import TemplatesAPI
from .events import EventsAPI

__all__ = [
    "AnalysisDefinitionAPI",
    "PortfoliosAPI",
    "QuantityType",
    "AnalysesAPI",
    "IdentifierType",
    "TemplatesAPI",
    "EntitiesAPI",
    "AnalysesRiskAPI",
    "MetaDataAPI",
    "AggregateOption",
    "ComputeOption",
    "Status",
    "DataPartition",
    "FinishedStatuses",
    "Status",
    "QuantityType",
    "IdentifierType",
    "PortfolioGroupsAPI",
    "BatchDefinitionsAPI",
    "MarketDataSourcesAPI",
    "AnalysesPerformanceAPI",
    "RiskModelDefinitionsAPI",
    "BulkAPI",
    "EventsAPI"
]
