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
from enum import unique

from axiomapy.entitybase import EnumBase


@unique
class Status(EnumBase):
    """Enum that provides options for the current status of an analysis request
    """

    Unknown = "Unknown"
    Created = "Created"
    Submitted = "Submitted"
    Running = "Running"
    Completed = "Completed"
    Failed = "Failed"
    PostProcessingFailed = "PostProcessingFailed"


@unique
class FinishedStatuses(EnumBase):
    """Enum that provides options for the status after the request is processed.
    """

    Completed = "Completed"
    Failed = "Failed"


@unique
class ComputeOption(EnumBase):
    """Enum to define computation options for a performance attribution task. Options control
        whether results will only be computed if missing, recomputed even if already computed,
        or used as stored, with no computation.
    """

    AsStored = "AsStored"
    MissingOnly = "MissingOnly"
    All = "All"


@unique
class AggregateOption(EnumBase):
    """Enum that provides options to control the aggregation process
    """

    OnCompletion = "OnCompletion"
    DoNotProcess = "DoNotProcess"


@unique
class HierarchyLevelType(EnumBase):
    """Enum that defines the possible hierarchy level types to be used in Performance attribution
    """

    ViewReportingLevelOnInstrument = "ViewReportingLevelOnInstrument"
    ViewReportingLevelOnPosition = "ViewReportingLevelOnPosition"
    ViewReportingLevelInNestedPortfolio = "ViewReportingLevelInNestedPortfolio"
    ViewReportingLevelOnAccount = "ViewReportingLevelOnAccount"
    ViewReportingLevelOnDerived = "ViewReportingLevelOnDerived"
    ViewReportingLevelAtPortfolioDepth = "ViewReportingLevelAtPortfolioDepth"
