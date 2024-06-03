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
#!/usr/bin/env python
# coding: utf-8

# # Getting Started With axioma-py
# 
# While there are various examples that go into further details on specific topics, the 
# following guide is intended as a starting point to explore a few basic operations and
# gain some familiarity with the package.
# 

# ## Imports
# 
# 
# 
# ### Logging
# 
# The standard logging library is used to log from within the package. 
# In order to see the logging statements, you must add at least one handler.
# In this case we will just log to the stdout. The level will be info.
# The following statement sets the default config for the logging. 



import logging

logging.basicConfig(
    level=logging.INFO, 
    format=r'%(asctime)s %(levelname)-8s %(message)s', 
    datefmt='%Y-%m-%d %H:%M:%S'
)


# ### Other Common Imports
# 
# While you may leverage many packages in your projects, the following are used 
# here and in the examples.



from datetime import datetime, timedelta
from pprint import pprint
import pandas as pd
from io import StringIO

# ### Importing From axioma-py
# 
# The following shows some of the most common imports from axioma-py,
# however, not all will be explicitly needed.
# 
# At the root of the package there are some core classes, but always required is the 
# Session manager AxiomaSession.
# The AxiomaSession will handle connecting to the API and any http requests.
# 
# The package is organized much like Axioma's REST API. 
# 
# In general, the necessary enumerations and associated datamodel classes 
#  are accessed from the 'parent' package (e.g. Enums can be accessed from axiomapy.axiomaapi.enums)
# 
# A Side Note on Collections:
# Most server resources are returned as a set of items based on the oData filters.
# Mapping (when there is a unique key) or Sequence classes are available to represent 
# these sets. As an example, there is Portfolio and Portfolios.
# A list can be passed instead of a mapping/sequence class and a mapping/sequence where
# relevant. The advantage of the mapping classes is that they have methods to 
# help manage the set of underlying instances. However, they all offer a to_list() if you 
# prefer to work with a list if the items.
#  
#  
# 
# 



from axiomapy import AxiomaSession


# Portfolio-related Imports


#from axiomapy.portfolios import Portfolio, Portfolios, PortfolioPatchResponse
from axiomapy.axiomaapi import PortfolioGroupsAPI, PortfoliosAPI

# Imports related to running risk analyses on a portfolio or collection of positions
from axiomapy.axiomaapi import AnalysisDefinitionAPI, RiskModelDefinitionsAPI, AnalysesRiskAPI

# Other Imports related to getting templates and entities
from axiomapy.axiomaapi import MetaDataAPI, TemplatesAPI, EntitiesAPI
from axiomapy.odatahelpers import oDataFilterHelper as od
from axiomapy.axiomaapi import enums
from axiomapy import axiomaexceptions
from axiomapy.session import APIType

# ## Logging In
# 
# A session is created, authenticated and set as the current session
# used for any http requests made via the package.
# 
# Update the credentials and run the command below:


# For testing, load up some credentials
from axiomapy.examples.load_credentials import get_user
user1 = get_user('user1')


# Replace the user1['xx'] with your credentials
AxiomaSession.use_session(
    username=user1['username'],
    password=user1['password'],
    domain=user1['domain']
)

# The users can still pass client id, if they wish to use a specific client id
# replace the user1['xx'] with your credentials
AxiomaSession.use_session(
    username=user1['username'],
    password=user1['password'],
    domain=user1['domain'],
    client_id=user1['client_id']
)

# ## Find Portfolios Using oData Filters
# 
# Return the set of portfolios into a mapping collection (keyed on portfolio name).
# OData parameters can be used to control the set of portfolios returned.
# There are some helpers to assist with basic filter syntax.
# 
# Below, the first five portfolios are returned that have:
# * long_name contains "US" and does not start with "Test" and, 
# * the latest position date field is null (i.e. no positions are loaded) and,
# * default currency in the set "USD", "GBP" or default data partition is AxiomaUS
# 
# The helper will also camel-case field names by default.



# Create a set of filters using the helpers
filters = [
    od.contains("long_name", "US"),
    'and not',
    od.starts_with("longName", "Test"),
    'and',
    od.equals("latestPositionDate", None),
    'and (',
    od.in_("default_currency", "USD", "GBP"),
    'or',
    od.equals("defaultDataPartition", "AxiomaUS"),
    ")"
]

filter_ = " ".join(filters)

print(filter_)

ptfs = PortfoliosAPI.get_portfolios(filter_results=filter_, top=5)

# Show the names of the portfolios found
# print(ptfs.keys())
pprint(ptfs.json()["items"])


# ## Create a Portfolio and Check for a Portfolio by Portfolio Id

#Create a portfolio if it doesn't exist already:
test_portfolio = {
    "name": "Test_Portfolio",
    "longName": "My Test Portfolio",
    "defaultCurrency": "USD",
}

try:
    r = PortfoliosAPI.post_portfolio(portfolio=test_portfolio)
    pId = int(r.headers["location"].split("/")[-1])
except (axiomaexceptions.AxiomaRequestError, axiomaexceptions.AxiomaRequestValidationError, axiomaexceptions.AxiomaRequestStatusError):
    filters = [
        od.equals("name", "Test_Portfolio")
    ]
    filter_ = " ".join(filters)
    ptfs = PortfoliosAPI.get_portfolios(filter_results=filter_)
    pId = ptfs.json()['items'][0]['id']

    print (pId)

#Once the portfolio is created, check for the portfolio with portfolio id. If the portfolio already exists, you can directly query for it.

my_ptf = PortfoliosAPI.get_portfolio(portfolio_id=pId)


# ## Create Some Positions
# 
# ### Define the Positions
# In this case we will just use a list of positions to update the portfolio.
# As can be seen below, any API defaults can be leveraged to avoid specifying all arguments (e.g. the default quantity type is Units).
# 



patch_position = [{"clientId": "514431",
                   "identifiers": [{"type": "ISIN", "value": "US5949181045"}, {"type": "Ticker", "value": "MSFT UN EQUITY"}],
                   "quantity": {"value": 6288458702.57133,
                                "scale": "MarketValue"},
                   "instrumentMapping": "Default"},
                  {"clientId": "514453",
                   "identifiers": [{"type": "ISIN", "value": "US0378331005"}, {"type": "Ticker", "value": "AAPL UN EQUITY"}],
                   "quantity": {"value": 32440128549.5337,
                                "scale": "MarketValue"},
                   "instrumentMapping": "Default"}]



# ### Add These Positions to the Portfolio
# 
# 
# First, check if there are positions. This is not necessary but it illustrates use of the AsOfDate type which can be compared with a date directly.
# 


date_to_load_positions = "2020-12-01"  # or can use the datetime type

# returns a list of PositionAsOfDate
position_dates_resp = PortfoliosAPI.get_position_dates(portfolio_id=pId)
position_dates = position_dates_resp.json()

# The position dates, which return a list of dates, allows direct comparison 
# with a date string or datetime.
print(
    f"The portfolio has positions on the date to load: {date_to_load_positions in [i['asOfDate'] for i in position_dates['items']]}"
)

if date_to_load_positions in [i['asOfDate'] for i in position_dates['items']]:
    PortfoliosAPI.delete_positions(portfolio_id=pId, as_of_date=date_to_load_positions)

patch = PortfoliosAPI.patch_positions(
    as_of_date=date_to_load_positions,
    portfolio_id=pId,
    positions_upsert=patch_position,
    positions_remove=[]
)

# The patch response makes it easier to identify errors and find the corresponding position records. 
# See  the AxiomaAPI Package documentation where the classes and methods are defined.


print(f"The patch request response: {patch.response}")


# Get the dates on which portfolio positions are defined.


position_dates = PortfoliosAPI.get_position_dates(portfolio_id=pId)
pprint(position_dates.json()["items"])


# ## Search for Views
# 
# A view can exist in a shared folder or be private. It can have a team property or an owner property but not both.
# 
# To find views, you can use a filter and a filter helper to assist with constructing the filter string.
# Of course, you can also create the view filter without the helper.

# All views in team Axioma Standard Views where name contains 'Coverage'
filters = [
    od.contains("name", "Coverage"),
    'and (',
    od.equals("team", "Axioma Standard Views"),
    ")"
]

filter_ = " ".join(filters)
definition_names = AnalysisDefinitionAPI.get_analysis_definitions(filter_results=filter_)

# Get top 5 results from the above filter
defs = AnalysisDefinitionAPI.get_analysis_definitions(filter_results=filter_, top=5)

defs.json()

analysis_id = defs.json()['items'][0]['id']



# ## Run a Risk Analysis
# 
# 
# Risk parameters are set to define the risk analysis task settings.
# 
# Any arguments not set (i.e., no value passed in the request) will use whatever the defaults are for those properties in the API. 
# Default values can be looked up in the online Swagger documentation for the Axioma API.



risk_param = {
    "analysisDate": date_to_load_positions,
    "positionDate": date_to_load_positions,
    "aggregationOptions": {
    "aggregate": "OnCompletion",
    "compute": enums.ComputeOption.MissingOnly
  },
    "analysisDefinition": {
    "id": analysis_id
  }
}


# ### Run a Portfolio Analysis
# 
# The request can be submitted using AnalysesRiskAPI.
# The response header will include the request id which can be used for further requests.


ra = AnalysesRiskAPI.post_portfolio_analyses(portfolio_id=pId,analyses_parameters=risk_param,return_response=True)

requestId = int(ra.headers["location"].split("/")[-1])

# Once the request is submitted, the user can check when the task is completed by requesting the status using the request id.

status = AnalysesRiskAPI.get_analyses_status(request_id=requestId)

# The analysis status is a type and has properties to be accessed.


status.status_code
status.content


# #### Access the Logs and Results


#The logs can be accessed in json format
logs = AnalysesRiskAPI.get_analyses_log(requestId)
print(logs.json())


#The results can be fetched in json format
results = AnalysesRiskAPI.get_analyses(requestId).json()
print(results)

#The results can also be fetched in csv format
results = AnalysesRiskAPI.get_analyses(requestId, as_csv=True).text
print(results)
df = pd.read_csv(StringIO(results), delimiter=',')


### Search for Entities

#To look for a particular entity, search using either the type of entity or using odata filters.

filters = [
    od.contains("name", "PA-MAC-Global-USD")
]

filter_ = " ".join(filters)

entities = EntitiesAPI.get_entities(typeName1='PerformanceAttributionSettings')

entities = EntitiesAPI.get_entities(typeName1='PerformanceAttributionSettings', filter_results=filters)

entities.json()['items']


# ## Clean Up
# 
# If desired, the user can delete the portfolio by passing the portfolio id as parameter to the request:

PortfoliosAPI.delete_portfolio(pId)


# Close the Session



AxiomaSession.current.close()


## Logging in for Bulk or CEB Session

#In order to create a session for Bulk flows, the user needs to pass BULK in the api type.
AxiomaSession.use_session(
    username=user1['username'],
    password=user1['password'],
    domain=user1['domain'],
    api_type="BULK"
)

#In order to create a session for CEB workflows, the user needs to pass CEB in the api type.
AxiomaSession.use_session(
    username=user1['username'],
    password=user1['password'],
    domain=user1['domain'],
    api_type=APIType.CEB
)

