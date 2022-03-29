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
from axiomapy.instruments import Identifier, IdentifierType, Qualifier, QualifierList


test_instance_equal_cases = {
    "test1_translate": (
        Identifier(value="Id1", type="ClientGiven"),
        Identifier(value="Id1", type_="Clientgiven"),
    ),
    "test2_translate": (
        Identifier(value="Id1", type="clientgiven"),
        Identifier(value="Id1", type_=IdentifierType.ClientGiven),
    ),
    "test3_from_dict": (
        Identifier(
            value="Cheese",
            type_=IdentifierType.ClientGiven,
            qualifiers=QualifierList(
                [
                    Qualifier(
                        type_="CountryCode",
                        values=["US"],
                        exclusive=True,
                        required=True,
                    )
                ]
            ),
        ),
        Identifier.from_dict(
            {
                "value": "Cheese",
                "type": "ClientGiven",
                "qualifiers": [
                    {
                        "type": "CountryCode",
                        "values": ["US"],
                        "required": True,
                        "exclusive": True,
                    }
                ],
            }
        ),
    ),
    "test4_from_dict": (
        Identifier(
            value="Cheese",
            type_=IdentifierType.ClientGiven,
            qualifiers=QualifierList(
                [
                    Qualifier(
                        type_="CountryCode",
                        values=["US"],
                        exclusive=False,
                        required=True,
                    )
                ]
            ),
        ),
        Identifier(
            value="Cheese",
            type_=IdentifierType.ClientGiven,
            qualifiers=QualifierList(
                [
                    {
                        "type": "CountryCode",
                        "values": ["US"],
                        "required": True,
                        "exclusive": False,
                    }
                ]
            ),
        ),
    ),
    "test5_from_dict": (
        Identifier(
            value="Cheese",
            type_=IdentifierType.ClientGiven,
            qualifiers=QualifierList(
                [
                    Qualifier(
                        type_="CountryCode",
                        values=["US"],
                    )
                ]
            ),
        ),
        Identifier(
            value="Cheese",
            type_=IdentifierType.ClientGiven,
            qualifiers=QualifierList(
                [
                    {
                        "type": "CountryCode",
                        "values": ["US"],
                    }
                ]
            ),
        ),
    ),
}

test_lookups = {
    "test1_simple": (
        Identifier(type_="TICKER", value="XYZ"),
        "TICKER=XYZ",
    ),
    "test1_multiple": (
        Identifier(
            type_="TICKER",
            value="XYZ",
            qualifiers=[
                Qualifier(type_="CountryCode", values=["US", "UK"]),
                Qualifier(type_="modeling", values=["lookthru"], required=True),
            ],
        ),
        "Ticker=XYZ|Prefer(CountryCode)=US,UK|modeling=lookthru",
    ),
    "test1_required": (
        Identifier.from_dict(
            {
                "type": "Ticker",
                "value": "XYZ",
                "qualifiers": [
                    {"type": "CountryCode", "values": ["US", "UK"], "required": True}
                ],
            }
        ),
        "Ticker=XYZ|CountryCode=US,UK",
    ),
}
