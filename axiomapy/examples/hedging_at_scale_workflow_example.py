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
from typing import Dict, List
from axiomapy import AxiomaSession
from axiomapy.axiomaapi import AnalysesAPI, AnalysesRiskAPI, PortfoliosAPI, TemplatesAPI, utils, enums
from axiomapy.odatahelpers import oDataFilterHelper as od
from axiomapy import axiomaexceptions

def get_results_and_logs(request_id: int, stat: str) -> pd.DataFrame:
    agg_logs = AnalysesAPI.get_analyses_log(request_id).json()

    if stat in 'Completed':
        res = AnalysesAPI.get_analyses(request_id=request_id, as_csv=True).text
        res_df = pd.read_csv(StringIO(res), delimiter=',')
    else:
        res_df = pd.DataFrame()
        print(json.dumps(agg_logs))
        print("A problem happened, check the logs file above")
    return res_df


def get_hedges_quantity(hedging_rule: str, unhedged_portfolio_id: int, hedging_portfolio_name: str, position_date: str, data_partition: str = "AxiomaUS", pricing_source: str = "Default", compute_option: str = "MissingOnly") -> pd.DataFrame:
    hedging_quantity_report = {
        "name": "Hedging Quantity Report",
        "aggregationLevelDefinitions": [
            {
                "name": "Currency",
                "item": {
                    "templateName": "{DefaultTemplateFor_ViewReportingLevelOnPosition}",
                    "content": {
                        "attributeName": "Currency",
                        "drilldown": None
                    }
                }
            },
            {
                "name": "ClientId",
                "item": {
                    "templateName": "{DefaultTemplateFor_ViewReportingLevelOnPosition}",
                    "content": {
                        "attributeName": "ClientId",
                        "drilldown": None
                    }
                }
            }
        ],
        "statisticDefinitions": [{
                "name": "Coverage",
                "item": {
                    "templateName": "AxR-Coverage",
                    "content": {
                        "Description": "Coverage stat indicating coverage at instrument level and portfolio level"
                    }
                }
            }]
    }

    stat_def = {
            "name": f"HEDGING ({hedging_rule})",
            "item": {
                "templateName": "AxR-Hedging Quantities",
                "content": {
                    "HedgingUniversePortfolio": f"Portfolio={hedging_portfolio_name}",
                    "RiskFactorReductionRule": hedging_rule
                }
            }
        }

    hedging_quantity_report["statisticDefinitions"].append(stat_def)

    analysis_payload = {
        "analysisDate": position_date,
        "positionDate": position_date,
        "analysisDefinition": None,
        "dataPartition": data_partition,
        "riskDataSource": pricing_source,
        "aggregationOptions": {
            "aggregate": "OnCompletion",
            "compute": compute_option
        },
        "showFactorModelNameAsRiskFactorPrefix": True
    }

    analysis_payload["analysisDefinition"] = hedging_quantity_report
    status, headers = utils.request_aggregation(analysis_payload, unhedged_portfolio_id, timelimit=3600)
    hedges_quantity_df = get_results_and_logs(request_id=int(headers.headers["location"].split("/")[-1]),
                                          stat=status.json()["status"])

    return hedges_quantity_df


def run_risk_decomp_report(unhedged_portfolio_id: int, position_date: str, data_partition: str, pricing_source: str, risk_settings: str = "Default", risk_statistic: str = "Default") -> pd.DataFrame:
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
    if risk_statistic != "Default":
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
    risk_decomp_df = get_results_and_logs(request_id=int(headers.headers["location"].split("/")[-1]),
                                          stat=status.json()["status"])
    return risk_decomp_df

def run_breakeven_report(swaps_positions: List[dict], position_date: str, data_partition: str, pricing_source: str) -> pd.DataFrame:
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
    break_even_df = get_results_and_logs(request_id=int(headers.headers["location"].split("/")[-1]),
                                          stat=status.json()["status"])
    return break_even_df


def create_ir_hedges(risk_decomp_df: pd.DataFrame, hedging_portfolio_name: str, hedging_portfolio_id: int, position_date: str) -> List[dict]:
    # Create constant maturity bonds for duration (GVT interest rate risk factors) hedging
    mask = (risk_decomp_df['RiskType'] == 'Risk Type : Interest Rate') & (
        risk_decomp_df['RiskFactor'].str.contains('GVT', na=False))
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

def create_ie_hedges(risk_decomp_df: pd.DataFrame, currency: str, hedging_portfolio_name: str, hedging_portfolio_id: int, position_date: str, data_partition: str = "AxiomaUS", pricing_source: str = "Default") -> List[dict]:
    def patch_zcils(ie_risk_factor: str, swap_rate_map: Dict[str, float]) -> str:
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

def create_fx_hedges(currencies_list_to_hedge: List[str], portfolio_currency: str, hedging_portfolio_name: str, hedging_portfolio_id: int, position_date: str, data_partition: str = "AxiomaUS", pricing_source: str = "Default") -> List[dict]:
    def patch_fxforward(currency_to_hedge: str, portfolio_currency: str, fx_rate_map: Dict[str, float]) -> str:
        start = datetime.datetime.strptime(position_date, '%Y-%m-%d')
        end = start + pd.DateOffset(months=1)
        fx_forward_name = f"FX_Forward_{currency_to_hedge}{portfolio_currency}_{end.strftime('%Y-%m-%d')}"

        fx_forward = {
        "templateName": "AxR-OTC-FX Forward",
        "content": {
            "Name": fx_forward_name,
            "buy_currency": f"Currency={portfolio_currency}",
            "sell_currency": f"Currency={currency_to_hedge}",
            "maturity_date": end.strftime('%Y-%m-%dT%H:%M:%S'),
            "forward_rate": fx_rate_map.get(fx_forward_name, 1)
        }
    }

        r = TemplatesAPI.patch_entities(template_name="{DefaultTemplateFor_Modeling_Of_FXForward}",
                                        entities_upsert=[fx_forward])

        if r.status_code == 204:
            fx_forward_name = f"FX_Forward_{currency_to_hedge}{portfolio_currency}_{end.strftime('%Y-%m-%d')}"
            print(f"{fx_forward_name} Updated")
        else:
            print(
                f"Error: Received status code {r.status_code} when creating FX_Forward_{currency_to_hedge}{portfolio_currency}_{end.strftime('%Y-%m-%d')}")
            exit()

        return fx_forward_name

    # Create zero coupon inflation swap for inflation (GBP.BEI risk factors) hedging

    hedging_positions_list = []
    for currency_to_hedge in currencies_list_to_hedge:
        fx_forward_name = patch_fxforward(currency_to_hedge, portfolio_currency,{})
        hedging_positions_list.append(fx_forward_name)

    my_fx_hedges = []
    for fx_forward in hedging_positions_list:
        my_fx_hedges.append(
            {
                "clientId": fx_forward,
                "description": fx_forward,
                "identifiers": [
                    {
                        "type": "ClientGiven",
                        "value": fx_forward
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
                                      positions_upsert=my_fx_hedges,
                                      positions_remove=[])
    print(f'{hedging_portfolio_name} positions imported')

    # Calculate the fx forward rate so the PV of these forwards are 0 at initiation
    break_even_df = run_breakeven_report(my_fx_hedges, position_date, data_partition, pricing_source)
    fx_forward_rate_map = break_even_df[break_even_df['ClientId'] != 'Total'].set_index('ClientId')['breakeven'].to_dict()

    for currency_to_hedge in currencies_list_to_hedge:
        fx_forward_name = patch_fxforward(currency_to_hedge, portfolio_currency, fx_forward_rate_map)


    return my_fx_hedges

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

# Example hedging cases to hedge GVT factors for all currencies, GBP inflation factor or FX risk factors
# hedging_rule = "CONTAINS(#RiskFactorName,\"GVT\") | CONTAINS(#RiskFactorName,\"GB.GBP.BEI\") |
# hedging_rule = "CONTAINS(#RiskFactorName,\"GB.GBP.BEI\")"
hedging_rule = "CONTAINS(#RiskFactorName,\"Currency\")"

# Get the PortfolioId of the unhedged portfolio and make sure it has a default portfolio currency
try:
    response = PortfoliosAPI.get_portfolios(filter_results=od.equals("name", portfolio_name))
    portfolios_json = response.json()
    print(portfolios_json)
    unhedged_portfolio_id = portfolios_json['items'][0]['id']
    default_currency = portfolios_json['items'][0]['defaultCurrency']
    print(f"Unhedged PortfolioId: {unhedged_portfolio_id}, Portfolio Currency: {default_currency}")

except (KeyError, IndexError, TypeError):
    raise ValueError(
        f"Portfolio with name '{portfolio_name}' not found or the portfolio does not have a default currency.")

# Add some bonds to the unhedged portfolio for the example
patch_position = [{"clientId": "UKTI 0.625 22-Mar-2040",
                   "identifiers": [{"type": "ISIN", "value": "GB00B3LZBF68"}],
                   "quantity": {"value": 10000,
                                "scale": "NotionalValue"}},
                  {"clientId": "DOW 5.25 15-Nov-2041",
                   "identifiers": [{"type": "ISIN", "value": "US260543CE14"}],
                   "quantity": {"value": 10000,
                                "scale": "NotionalValue"}},
                   {"clientId": "SWISS 4 06-Jan-2049",
                    "identifiers": [{"type": "ISIN", "value": "CH0009755197"}],
                    "quantity": {"value": 10000,
                                 "scale": "NotionalValue"}}]
patch = PortfoliosAPI.patch_positions(
    as_of_date=position_date,
    portfolio_id=unhedged_portfolio_id,
    positions_upsert=patch_position,
    positions_remove=[]
)

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
    # my_ir_hedges = create_ir_hedges(risk_decomp_df, portfolio_name, hedging_portfolio_id, position_date)
    # my_hedges.extend(my_ir_hedges)

    # # Inflation hedging (GBP) example using zero coupon inflation swap with matching maturities to hedge GBP inflation risk factors
    # my_ie_hedges = create_ie_hedges(risk_decomp_df, 'GBP', portfolio_name, hedging_portfolio_id, position_date, data_partition, pricing_source)
    # my_hedges.extend(my_ie_hedges)
    # FX hedging (GBP, CHF) example using FX forward with 1 month maturity to hedge FX risk factors
    my_fx_hedges = create_fx_hedges(['GBP', 'CHF'], default_currency, portfolio_name, hedging_portfolio_id, position_date,  data_partition, pricing_source)
    my_hedges.extend(my_fx_hedges)

# Get the hedging instruments' quantity needed to hedge the risk factors
hedges_quantity_df = get_hedges_quantity(hedging_rule, unhedged_portfolio_id, hedging_portfolio_name, position_date, data_partition, pricing_source, "MissingOnly")

# Update the quantity of the hedging instruments
hedging_dict = {}

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
