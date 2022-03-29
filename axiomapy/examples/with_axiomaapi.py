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

# # Axioma API Direct Access
# 
# 
# All API access is managed through a series of modules and classes using the active session.
# 
# In some cases, direct API access may be preferred or necessary.  
# The following examples show how to access the API classes and perform some actions on portfolios.
# 

# ## Imports
# 
# The axioma-py imports.
# Each 'section' of the API is available to import from the Axioma API package.



from axiomapy import AxiomaSession, AxiomaResponse
from axiomapy.axiomaapi import (
    PortfoliosAPI,
    AnalysesPerformanceAPI,
    AnalysesRiskAPI
)

# Some other imports



from pprint import pprint
from datetime import datetime, timedelta
import logging




import logging

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s %(levelname)-8s %(message)s', 
                    datefmt='%Y-%m-%d %H:%M:%S')


# ## Credentials and Creating an Active Session
# Load up some credentials to work with. There is a sample.credentials.json in the ./examples/credentials folder. Copy this file to credentials.json and update. Alternatively, skip the next set of code and set the credentials directly when creating the session:



from axiomapy.examples.load_credentials import get_user
user1 =  get_user('user1')




# If the credentials json is not used, enter credentials directly below:
AxiomaSession.use_session(user1['client_id'], user1['username'], user1['password'], user1['domain'], application_name='With analyses examples connection')
# Test the connection:
me = AxiomaSession.current.test()


# ## Get a List of Portfolios



portfolios_response = PortfoliosAPI.get_portfolios(top=10)


# The response object contains subsets of the original response.



print(f"Returned type is {type(portfolios_response)}")




pprint(portfolios_response.json())


# You can still access the original response.



original_response = portfolios_response.response


# However, the original response can be requested.



response = PortfoliosAPI.get_portfolios(top=10, return_response=True)

print(f"The returned type is {type(response)}")

print(f"Access the original request url info {response.request.url}")


### Performance Attribution Request

#A Performance Attribution request is used to analyze the performance of a portfolio over given dates.
#A prerequisite to the main PA task is to start a job to pre-calculate the analytics results that form the inputs to performance attribution.


precompute_param = {
    "asOfDate": "2021-03-31", 
    "benchmark": {"useNoBenchmark": True}, 
    "performanceAttributionSettingsId": 2136463,
    "computingBehavior":"MissingOnly"
}

analyses_test = AnalysesPerformanceAPI.post_precompute(portfolio_id=123330, precompute_parameters=precompute_param)


#Once the precompute task has run for all the dates for which the main PA task is to be performed, the PA task can be triggered.

#The PA task body accepts the start and end dates for a PA along with the Performance Attribution Settings ID.

pa_params = {
    "startDate": "2021-03-30", 
    "endDate": "2021-03-31",
    "benchmark": {"useNoBenchmark": True}, 
    "performanceAttributionSettingsId": 2136463,
    "computingBehavior":"MissingOnly"
}

#The header of the response to the request consists of the requestId, which can be used in additional requests.

pa_task = AnalysesPerformanceAPI.post_performance_analysis(portfolio_id=123330, analyses_parameters=pa_params)
requestId = int(pa_task.headers["location"].split("/")[-2])

#The status of the request and the logs can be attained using the request id:

status = AnalysesPerformanceAPI.get_status(request_id=requestId)
logs = AnalysesPerformanceAPI.get_logs(request_id=requestId)


## Risk Model Service

#The Risk Model Service is helpful in generating a risk model based on the exposures of a portfolio or list of instruments. 
#It can also be used to output factor returns for a given portfolio or list of instruments.


#Create a request with the desired parameters: portfolio or instruments, risk model definition, and statistic definition:

rms_parameters = {
  'portfolioId': 123442,
  'analysisDate': '2020-09-15',
  'riskModelDefinitionId': 3707082
}


#The header of the response to the request consists of the requestId, which is used in additional requests:

req = AnalysesRiskAPI.post_risk_model_request(risk_model_parameters=rms_parameters)
requestId = int(req.headers["location"].split("/")[-1])

#The status of the request can be fetched using the requestId. Once the request is completed the user can also access the logs for the same. 

status = AnalysesRiskAPI.get_risk_model_request_status(requestId)

logs = AnalysesRiskAPI.get_risk_model_logs(requestId)

#The user can get the results of the request using the requestId. The user can choose the results to be in raw format or refined by changing the parameter show_raw_results in the request.

results = AnalysesRiskAPI.get_risk_model_results(request_id=requestId, show_raw_results=False)
