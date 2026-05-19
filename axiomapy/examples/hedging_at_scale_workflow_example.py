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

logging.basicConfig(
    level=logging.INFO, 
    format=r'%(asctime)s %(levelname)-8s %(message)s', 
    datefmt='%Y-%m-%d %H:%M:%S'
)


import time
import pandas as pd
from io import StringIO
import json
import re
import datetime
from axiomapy import AxiomaSession
from axiomapy.axiomaapi import AnalysesAPI, AnalysesRiskAPI, PortfoliosAPI, TemplatesAPI, utils, enums
from axiomapy.odatahelpers import oDataFilterHelper as od
from axiomapy import axiomaexceptions

def run_risk_decomp_report(unhedged_portfolio_id, position_date, data_partition, pricing_source, risk_settings="Default", risk_statistic="Default"):
    # Break down the portfolio to risk factors
    risk_decomp_json = {
        "name": "Risk Decomposition",
        "aggregationLevelDefinitions": [
            {
                "name": "Risk Type",
                "item": {
                    "templateName": "Risk Type",
                    "content": {}
                }
            },
            {
                "name": "Factor Type",
                "item": {
                    "templateName": "Factor Type",
                    "content": {}
                }
            },
            {
                "name": "Risk Factor",
                "item": {
                    "templateName": "Risk Factor",
                    "content": {}
                }
            }
        ],
        "statisticDefinitions": [
            {
                "name": "Risk Exposure (Portfolio)",
                "item": {
                    "templateName": "AxR-Risk Exposure (P-Shell)",
                    "content": {
                        "Description": "Parametric portfolio risk exposure using MAC Global resolution and expressed in monetary terms"
                    }
                }
            }
        ]
    }

    if risk_settings != "Default":
        risk_decomp_json["statisticDefinitions"][0]["item"]["content"]["RiskSettings"] = risk_settings
    if risk_settings != "Default":
        risk_decomp_json["statisticDefinitions"][0]["item"]["content"]["RiskStatistic"] = risk_statistic

    analysis_payload = {
        "analysisDate": position_date,
        "positionDate": position_date,
        "analysisDefinition": risk_decomp_json,
        "dataPartition": data_partition,
        "riskDataSource": pricing_source,
        "aggregationOptions": {
            "aggregate": "OnCompletion",
            "compute": "MissingOnly"
        },
        "showFactorModelNameAsRiskFactorPrefix": True
    }


    status, headers = utils.request_aggregation(analysis_payload, unhedged_portfolio_id, timelimit=3600)
    risk_decomp_df = utils.get_results_and_logs(request_id=int(headers.headers["location"].split("/")[-1]),
                                          stat=status.json()["status"])
    return risk_decomp_df

def run_breakeven_report(swaps_positions, position_date, data_partition, pricing_source):
    # Calculate the breakeven (swap) rate of the OTC swaps
    break_even_json = {
        "name": "Break-even rate",
        "aggregationLevelDefinitions": [
            {
                "name": "ClientId",
                "item": {
                    "templateName": "{DefaultTemplateFor_ViewReportingLevelOnPosition}",
                    "content": {
                        "AttributeName": "ClientId"
                    }
                }
            }
        ],
        "statisticDefinitions": [
            {
                "name": "Coverage",
                "item": {
                    "templateName": "AxR-Coverage"
                }
            },
            {
                "name": "breakeven",
                "item": {
                    "templateName": "AxR-Breakeven"
                }
            }
        ]
    }

    analysis_payload = {
        "portfolioName": "Swaps Portfolio",
        "analysisDate": position_date,
        "positionDate": position_date,
        "analysisDefinition": break_even_json,
        "dataPartition": data_partition,
        "riskDataSource": pricing_source,
        "aggregationOptions": {
            "aggregate": "OnCompletion",
            "compute": "MissingOnly"
        },
        "positions": swaps_positions
    }


    status, headers = utils.request_position_analytics(analysis_payload, timelimit=3600)
    break_even_df = utils.get_results_and_logs(request_id=int(headers.headers["location"].split("/")[-1]),
                                          stat=status.json()["status"])
    return break_even_df


def create_ir_hedges(risk_decomp_df, hedging_portfolio_name, hedging_portfolio_id, position_date):
    # Create constant maturity bonds for duration (USD and CHF GVT interest rate risk factors) hedging
    mask = (risk_decomp_df['RiskType'] == 'Risk Type : Interest Rate') & (
        risk_decomp_df['RiskFactor'].str.contains('USD.GVT|CHF.GVT', na=False))
    filtered_df = risk_decomp_df.loc[mask]
    unique_ir_risk_factors = filtered_df['RiskFactor'].unique().tolist()
    print("Interest Rate Risk Factors to hedge:")
    print(unique_ir_risk_factors)

    if unique_ir_risk_factors:
        hedging_positions_list = []
        for ir_risk_factor in unique_ir_risk_factors:
            left, right = ir_risk_factor.split(':')
            currency = left.strip().split('.')[1]
            match = re.match(r'(\d+)([A-Za-z]+)', right.strip())
            if not match:
                raise ValueError(f"Invalid tenor format: {right.strip()}")
            tenor = match.group(1)
            tenor_unit = match.group(2)

            tenor_unit_map = {"D": "Day", "W": "Week", "M": "Month", "Y": "Year"}

            zc_constant_maturity_bond = {
                "$type": "TemplatedRawDataInputs",
                "templateName": "{DefaultTemplateFor_Modeling_Of_Bond}",
                "content": {
                    "$type": "Modeling_Of_Bond",
                    "Name": f"Constant_Maturity_{currency}_{tenor}{tenor_unit}",
                    "termsAndConditions": {
                        "$type": "TemplatedRawDataInputs",
                        "templateName": "{DefaultTemplateFor_Bond}",
                        "content": {
                            "$type": "Bond",
                            "Name": f"Constant_Maturity_{currency}_{tenor}{tenor_unit}",
                            "reportingAttributes": {
                                "reportingAttributes": []
                            },
                            "accruingPeriodConvention": None,
                            "businessConventions": {
                                "businessDayConvention": "NoAdjustment",
                                "holidays": {
                                    "$type": "HolidaysDefinitions.NoHolidays"
                                }
                            },
                            "couponSchedule": {
                                "$type": "CouponSchedule.FixedTenor",
                                "fixedTenorFromAnalysisDate": {
                                    "numberOfUnits": tenor,
                                    "unit": tenor_unit_map[tenor_unit]
                                }
                            },
                            "currency": currency,
                            "dayCountConvention": "D30Y360US",
                            "exDividend": None,
                            "expectedMaturityDate": None,
                            "firstCouponStartAccruingDate": None,
                            "issueDate": None,
                            "issuerId": None,
                            "notional": 100,
                            "recoveryRate": {
                                "inScale": "Absolute",
                                "number": 0.4
                            },
                            "redemptionValue": 100,
                            "amountOutstandingHistory": None,
                            "couponSettlementConventions": {
                                "businessDayConvention": "NoAdjustment",
                                "holidays": {
                                    "$type": "HolidaysDefinitions.NoHolidays"
                                }
                            },
                            "extendedMaturityDate": None,
                            "isAmortizing": False,
                            "isFlatTrading": False,
                            "pIKTerms": None,
                            "priceTimeSeriesId": None,
                            "settlementPeriod": {
                                "numberOfUnits": 0,
                                "unit": "BusinessDay"
                            },
                            "sinkingSchedule": {
                                "rates": None,
                                "isFundingProvision": False,
                                "sinkingRatesScale": "Absolute"
                            },
                            "status": "None"
                        }
                    },
                    "modelingAssumptions": {
                        "$type": "TemplatedRawDataInputs",
                        "templateName": "{DefaultTemplateFor_Bond_ValuationThrough_SpotMarketExpectationsModel}",
                        "content": {
                            "$type": "Bond_ValuationThrough_SpotMarketExpectationsModel",
                            "Name": f"Constant_Maturity_{currency}_{tenor}{tenor_unit}",
                            "dealContext": {
                                "creditModels": None,
                                "isFXHedged": False,
                                "riskFreeCurves": [],
                                "discountCurves": [],
                                "cTDDiscountCurves": None,
                                "riskFreeReferenceDiscountCurves": None
                            },
                            "valuationMethod": None,
                            "calibrationMethods": {
                                "base": {
                                    "$type": "SpotMarketExpectationsModel.Calibrator",
                                    "interestRateCurveInterpolationMethod": "PieceWiseLinear",
                                    "ultimateForwardRate": None,
                                    "lastTenorOverride": None
                                },
                                "local": None,
                                "priceReconciliation": None
                            }
                        }
                    }
                }
            }

            r = TemplatesAPI.patch_entities(template_name="{DefaultTemplateFor_Modeling_Of_Bond}",
                                            entities_upsert=[zc_constant_maturity_bond])

            if r.status_code == 204:
                print(f"Constant_Maturity_{currency}_{tenor}{tenor_unit} Created")
                hedging_positions_list.append(f'Constant_Maturity_{currency}_{tenor}{tenor_unit}')
            else:
                print(
                    f"Error: Received status code {r.status_code} when creating Constant_Maturity_{currency}_{tenor}{tenor_unit}")
                exit()



    my_ir_hedges = []
    for cmb in hedging_positions_list:
        my_ir_hedges.append(
            {
                "clientId": cmb,
                "description": cmb,
                "identifiers": [
                    {
                        "type": "ClientGiven",
                        "value": cmb
                    }
                ],
                "quantity": {
                    "value": 1,
                    "scale": "NumberOfInstruments"
                }
            }
        )

    r = PortfoliosAPI.patch_positions(portfolio_id=hedging_portfolio_id,
                                      as_of_date=position_date,
                                      positions_upsert=my_ir_hedges,
                                      positions_remove=[])
    print(f'{hedging_portfolio_name} positions imported')

    return my_ir_hedges

def create_ie_hedges(risk_decomp_df, currency, hedging_portfolio_name, hedging_portfolio_id, position_date, data_partition="AxiomaUS", pricing_source="Default"):
    def patch_zcils(ie_risk_factor, swap_rate_map):
        left, right = ie_risk_factor.split(':')
        currency = left.strip().split('.')[1]
        match = re.match(r'(\d+)([A-Za-z]+)', right.strip())
        if not match:
            raise ValueError(f"Invalid tenor format: {right.strip()}")
        tenor = match.group(1)
        tenor_unit = match.group(2)

        year_to_add = 0
        month_to_add = 0
        if tenor_unit == 'Y':
            year_to_add = int(tenor)
        elif tenor_unit == 'M':
            month_to_add = int(tenor)
        start = datetime.datetime.strptime(position_date, '%Y-%m-%d')
        end = start + pd.DateOffset(years=year_to_add, months=month_to_add)
        swap_name = f"ZC_Inflation_Swap_{currency}_{tenor}{tenor_unit}"

        zc_inflation_swap = {
        "templateName": "AxR-OTC-ZC Inflation Swap",
        "content": {
            "Name": swap_name,
            "currency": f"Currency={currency}",
            "inflation_lag": 2,
            "inflation_lag_unit": "Month",
            "inflation_market_convention": "UK",
            "inflation_index": "Ticker=UKRPI Index",
            "start_date": start.strftime('%Y-%m-%dT%H:%M:%S'),
            "maturity_date": end.strftime('%Y-%m-%dT%H:%M:%S'),
            "swap_rate": swap_rate_map.get(swap_name, 0.01)
        }
    }

        r = TemplatesAPI.patch_entities(template_name="{DefaultTemplateFor_Modeling_Of_ZeroCouponInflationSwap}",
                                        entities_upsert=[zc_inflation_swap])

        if r.status_code == 204:
            swap_name = f'ZC_Inflation_Swap_{currency}_{tenor}{tenor_unit}'
            print(f"{swap_name} Updated")
        else:
            print(
                f"Error: Received status code {r.status_code} when creating ZC_Inflation_Swap_{currency}_{tenor}{tenor_unit}")
            exit()

        return swap_name

    # Create zero coupon inflation swap for inflation (GBP.BEI risk factors) hedging
    mask = (risk_decomp_df['RiskType'] == 'Risk Type : Inflation') & (
        risk_decomp_df['RiskFactor'].str.contains(currency, na=False))
    filtered_df = risk_decomp_df.loc[mask]
    unique_ie_risk_factors = filtered_df['RiskFactor'].unique().tolist()
    print("Inflation Risk Factors to hedge:")
    print(unique_ie_risk_factors)

    if unique_ie_risk_factors:
        hedging_positions_list = []
        for ie_risk_factor in unique_ie_risk_factors:
            swap_name = patch_zcils(ie_risk_factor, {})
            hedging_positions_list.append(swap_name)

        my_ie_hedges = []
        for zcils in hedging_positions_list:
            my_ie_hedges.append(
                {
                    "clientId": zcils,
                    "description": zcils,
                    "identifiers": [
                        {
                            "type": "ClientGiven",
                            "value": zcils
                        }
                    ],
                    "quantity": {
                        "value": 1,
                        "scale": "NumberOfInstruments"
                    }
                }
            )

        r = PortfoliosAPI.patch_positions(portfolio_id=hedging_portfolio_id,
                                          as_of_date=position_date,
                                          positions_upsert=my_ie_hedges,
                                          positions_remove=[])
        print(f'{hedging_portfolio_name} positions imported')

        # Calculate the break-even (swap) rate so the PV of these swaps are 0 at initiation
        break_even_df = run_breakeven_report(my_ie_hedges, position_date, data_partition, pricing_source)
        swap_rate_map = break_even_df[break_even_df['ClientId'] != 'Total'].set_index('ClientId')['breakeven'].to_dict()

        for ie_risk_factor in unique_ie_risk_factors:
            swap_name = patch_zcils(ie_risk_factor, swap_rate_map)

        return my_ie_hedges

###################################################################################################################################################

from axiomapy.examples.load_credentials import get_user
user1 = get_user('user1')

AxiomaSession.use_session(
    username=user1['username'],
    password=user1['password'],
    domain=user1['domain'],
    client_id=user1['client_id']
)

portfolio_name = "Your Portfolio"
hedging_portfolio_name = f"{portfolio_name}_HEDGING"
hedged_portfolio_name = f"{portfolio_name}_HEDGED"
position_date = '2026-05-01'
data_partition = 'AxiomaUS'
pricing_source = 'Default'

# An example hedging case to hedge USD and CHF GVT factors, as well as GBP inflation factor
list_of_hedging_rules = ["OR(CONTAINS(#RiskFactorName,\"USD.GVT\"), CONTAINS(#RiskFactorName,\"CHF.GVT\"))", "CONTAINS(#RiskFactorName,\"GB.GBP.BEI\")"]

# Get the PortfolioId of the unhedged portfolio and make sure it has a default portfolio currency
try:
    response = PortfoliosAPI.get_portfolios(filter_results="contains(name, '" + portfolio_name + "')")
    portfolios_json = response.json()
    unhedged_portfolio_id = portfolios_json['items'][0]['id']
    default_currency = portfolios_json['items'][0]['defaultCurrency']
    print(f"Unhedged PortfolioId: {unhedged_portfolio_id}, Portfolio Currency: {default_currency}")

except (KeyError, IndexError, TypeError):
    raise ValueError(
        f"Portfolio with name '{portfolio_name}' not found or the portfolio does not have a default currency.")


# Create a portfolio which will contain the hedging universe
hedging_portfolio = {
    "name": hedging_portfolio_name,
    "longName": hedging_portfolio_name,
    "defaultCurrency": default_currency,
}

try:
    r = PortfoliosAPI.post_portfolio(portfolio=hedging_portfolio)
    hedging_portfolio_id = int(r.headers["location"].split("/")[-1])
except (axiomaexceptions.AxiomaRequestError, axiomaexceptions.AxiomaRequestValidationError,
        axiomaexceptions.AxiomaRequestStatusError):
    filters = [
        od.equals("name", f"{portfolio_name}_HEDGING")
    ]
    filter_ = " ".join(filters)
    ptfs = PortfoliosAPI.get_portfolios(filter_results=filter_)
    hedging_portfolio_id = ptfs.json()['items'][0]['id']
print(f"Hedging PortfolioId: {hedging_portfolio_id}")

r = PortfoliosAPI.delete_positions(portfolio_id=hedging_portfolio_id, as_of_date=position_date)
print(f'{hedging_portfolio_name} positions flushed')


# Create a portfolio which will combine the unhedged and hedging portfolio
hedged_portfolio = {
    "name": hedged_portfolio_name,
    "longName": hedged_portfolio_name,
    "defaultCurrency": default_currency,
}

try:
    r = PortfoliosAPI.post_portfolio(portfolio=hedged_portfolio)
    hedged_portfolio_id = int(r.headers["location"].split("/")[-1])
except (axiomaexceptions.AxiomaRequestError, axiomaexceptions.AxiomaRequestValidationError,
        axiomaexceptions.AxiomaRequestStatusError):
    filters = [
        od.equals("name", f"{portfolio_name}_HEDGED")
    ]
    filter_ = " ".join(filters)
    ptfs = PortfoliosAPI.get_portfolios(filter_results=filter_)
    hedged_portfolio_id = ptfs.json()['items'][0]['id']
print(f"Hedged PortfolioId: {hedged_portfolio_id}")

r = PortfoliosAPI.delete_positions(portfolio_id=hedged_portfolio_id, as_of_date=position_date)
print(f'{portfolio_name}_HEDGED positions flushed')

my_positions = [
    {
        "clientId": "Unhedged Portfolio",
        "description": portfolio_name,
        "identifiers": [
            {
                "type": "portfolio",
                "value": portfolio_name
            }
        ],
        "quantity": {
            "value": 1,
            "scale": "NumberOfInstruments"
        }
    },
    {
        "clientId": "Hedging Portfolio",
        "description": hedging_portfolio_name,
        "identifiers": [
            {
                "type": "portfolio",
                "value": hedging_portfolio_name
            }
        ],
        "quantity": {
            "value": 1,
            "scale": "NumberOfInstruments"
        }
    }
]

r = PortfoliosAPI.patch_positions(portfolio_id=hedged_portfolio_id,
                                  as_of_date=position_date,
                                  positions_upsert=my_positions,
                                  positions_remove=[])

risk_decomp_df = run_risk_decomp_report(unhedged_portfolio_id, position_date, data_partition, pricing_source, risk_settings="Default", risk_statistic="Default")

my_hedges = []
if not risk_decomp_df.empty:
    # Duration hedging example using constant maturity bonds with matching maturities to hedge GVT interest rate risk factors
    my_ir_hedges = create_ir_hedges(risk_decomp_df, portfolio_name, hedging_portfolio_id, position_date)
    my_hedges.extend(my_ir_hedges)
    # Inflation hedging (GBP) example using zero coupon inflation swap with matching maturities to hedge GBP inflation risk factors
    my_ie_hedges = create_ie_hedges(risk_decomp_df, 'GBP', portfolio_name, hedging_portfolio_id, position_date, data_partition, pricing_source)
    my_hedges.extend(my_ie_hedges)

# Get the hedging instruments' quantity needed to hedge the risk factors
hedges_quantity_df = utils.get_hedges_quantity(list_of_hedging_rules, unhedged_portfolio_id, hedging_portfolio_name, position_date, data_partition, pricing_source)

# Update the quantity of the hedging instruments
hedging_dict = {}
for hedging_rule in list_of_hedging_rules:
    hedging_results = hedges_quantity_df[f'HEDGING ({hedging_rule})'].iloc[0]
    for pair in hedging_results.split(';'):
        key, value = pair.split(':')
        hedging_dict[key.strip()] = float(value) * -1

    for hedge in my_hedges:
        client_id = hedge['clientId']
        if client_id in hedging_dict:
            hedge['quantity']['value'] = hedging_dict[client_id]

    r = PortfoliosAPI.patch_positions(portfolio_id=hedging_portfolio_id,
                                      as_of_date=position_date,
                                      positions_upsert=my_hedges,
                                      positions_remove=[])
    print(f'{hedging_portfolio_name} positions quantity updated')
