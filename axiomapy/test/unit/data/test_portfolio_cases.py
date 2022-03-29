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
from axiomapy.portfolios import Portfolio
from axiomapy.axiomaapi import DataPartition


test_instance_equal_cases = {
    "test1_translate": (
        Portfolio(name="Portfolio1", defaultDataPartition="AxiomaUS"),
        Portfolio(name="Portfolio1", default_data_partition="AxiomaUS"),
    ),
    "test2_translate": (
        Portfolio(name="Portfolio1", default_data_partition="AxiomaUS"),
        Portfolio(name="Portfolio1", default_data_partition=DataPartition.AxiomaUS),
    ),
    "test3_from_dict": (
        Portfolio(
            name="Portfolio",
            long_name="long name",
            description="description",
            default_currency="USD",
        ),
        Portfolio.from_dict(
            {
                "name": "Portfolio",
                "longName": "long name",
                "description": "description",
                "defaultCurrency": "USD",
            }
        ),
    ),
    "test4_from_dict": (
        Portfolio(
            name="Portfolio",
            longName="long name",
            description="description",
            default_currency="USD",
        ),
        Portfolio.from_dict(
            {
                "name": "Portfolio",
                "longName": "long name",
                "description": "description",
                "defaultCurrency": "USD",
            }
        ),
    ),
    "test5_data_partition": (
        Portfolio.from_dict(
            {
                "name": "Portfolio",
                "long_name": "long name",
                "description": "description",
                "defaultDataPartition": "AxiomaUS",
            }
        ),
        Portfolio.from_dict(
            {
                "name": "Portfolio",
                "longName": "long name",
                "description": "description",
                "defaultDataPartition": DataPartition.AxiomaUS,
            }
        ),
    ),
}
