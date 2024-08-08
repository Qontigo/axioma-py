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
import json
from pathlib import Path


data_folder_path = Path(__file__).parent.joinpath("sample_data")


def load_from_path(path: Path) -> dict:
    with open(path) as d:
        data = json.load(d)
    return data


def info():
    print(f"Current working directory: {Path.cwd()}")
    print(f"Will open sample files in: {data_folder_path}")


def sample_portfolios():

    ptf_path = data_folder_path.joinpath("sample_portfolios.json")
    print(f"Looking for sample_portfolios.json at: {ptf_path}")
    return load_from_path(ptf_path)


def sample_positions():

    position_path = data_folder_path.joinpath("sample_positions.json")
    print(f"Looking for sample_positions.json at: {position_path}")
    return load_from_path(position_path)


def sample_otc():

    otc_path = data_folder_path.joinpath("sample_otc.json")
    print(f"Looking for sample_positions.json at: {otc_path}")

    return load_from_path(otc_path)


def sample_template():
    sample_template_path = data_folder_path.joinpath("sample_template.json")
    print(f"Looking for sample_positions.json at: {sample_template_path}")

    return load_from_path(sample_template_path)


def sample_perf_settings():
    sample_template_path = data_folder_path.joinpath("sample_performancesettings.json")
    print(f"Looking for sample_performancesettings.json at: {sample_template_path}")

    return load_from_path(sample_template_path)
