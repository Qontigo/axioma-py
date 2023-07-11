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
import time

from axiomapy.axiomaapi import AnalysesAPI, AnalysesRiskAPI, enums


def request_model(data, timelimit=500):
    headers = AnalysesRiskAPI.post_risk_model_request(risk_model_parameters=data)
    requestId = int(headers.headers["location"].split("/")[-1])
    # Recursively checking the status of the risk model job
    itns = int(timelimit / 5)
    for idx in range(itns):
        status = AnalysesRiskAPI.get_risk_model_request_status(requestId)
        stat = status.json()["status"]
        print(stat)
        if stat.lower() in [
            enums.FinishedStatuses.Completed,
            enums.FinishedStatuses.Failed,
        ]:
            break
        time.sleep(5)
        print("Still waiting", idx * 5, "seconds")

    return stat, headers


def request_instrument_analytics(data, timelimit=500):
    headers = AnalysesRiskAPI.post_instrument_analyses(data)
    requestId = int(headers.headers["location"].split("/")[-1])

    # Recursively checking the status of the job
    itns = int(timelimit / 5)
    for idx in range(itns):
        status = AnalysesAPI.get_analyses_status(requestId)
        stat = status.json()["status"]
        print(stat)
        if stat.lower() in [
            enums.FinishedStatuses.Completed,
            enums.FinishedStatuses.Failed,
        ]:
            break
        time.sleep(5)
        print("Still waiting", idx * 5, "seconds")
    return stat, headers


def request_aggregation(data, portfolio_id, timelimit=500, polling_freq=5):
    headers = AnalysesRiskAPI.post_portfolio_analyses(
        analyses_parameters=data, portfolio_id=portfolio_id
    )
    requestId = int(headers.headers["location"].split("/")[-1])
    # Recursively checking the status of the job
    itns = int(timelimit / polling_freq)
    for idx in range(itns):
        status = AnalysesAPI.get_analyses_status(requestId)
        stat = status.json()["status"]
        print(stat)
        if stat.title() in [
            enums.FinishedStatuses.Completed,
            enums.FinishedStatuses.Failed,
        ]:
            break
        time.sleep(polling_freq)
        print("Still waiting", idx * polling_freq, "seconds")
    return status, headers
