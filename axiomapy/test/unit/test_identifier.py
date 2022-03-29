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
import unittest

from axiomapy.instruments import Identifier, IdentifierType, Qualifier, QualifierList

from .data.test_identifier_cases import test_instance_equal_cases, test_lookups


class TestIdentifier(unittest.TestCase):
    identifier_instance = Identifier(
        value="Cheese",
        type_=IdentifierType.ClientGiven,
        qualifiers=QualifierList(
            [
                Qualifier(
                    type_="CountryCode", values=["US"], exclusive=False, required=True
                )
            ]
        ),
    )
    identifier_dict = {
        "value": "Cheese",
        "type": "ClientGiven",
        "qualifiers": [
            {
                "type": "CountryCode",
                "values": ["US"],
                "required": True,
                "exclusive": False,
            }
        ],
    }

    def setUp(self):
        # load the test data
        pass

    def test_lookup_to_identifier(self):
        for name, (a, b) in test_lookups.items():
            with self.subTest(name=name):
                from_lookup = Identifier.from_lookup_element(b)
                self.assertEqual(a, from_lookup)

    def test_identifier_to_lookup(self):
        for name, (a, b) in test_lookups.items():
            with self.subTest(name=name):
                to_lookup = a.to_lookup()
                self.assertEqual(to_lookup.lower(), b.lower())

    def test_default_instance(self):
        default_instance = Identifier.default_instance()
        self.assertEqual(default_instance, Identifier(value=None, type_=None))

    def test_clone_equal(self):
        ident = self.identifier_instance
        clone = ident.clone()
        self.assertEqual(ident, clone)

    def test_equal(self):
        for name, (a, b) in test_instance_equal_cases.items():
            with self.subTest(name=name):
                self.assertEqual(a, b)

    def test_to_dict(self):
        portfolio_dict = self.identifier_instance.to_dict()
        self.assertDictEqual(portfolio_dict, self.identifier_dict)

    def test_from_dict(self):
        identifier_dict = Identifier.from_dict(self.identifier_dict)
        identifier = self.identifier_instance
        self.assertEqual(identifier_dict, identifier)


if __name__ == "__main__":
    unittest.main()
