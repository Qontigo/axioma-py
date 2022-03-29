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
from typing import Union
from inflection import camelize as cam


def camelize_arg(arg: str, camelize: bool):
    return cam(arg, uppercase_first_letter=False) if camelize else arg


class oDataFilterHelper:
    """
    A set of static methods to help with the oData syntax.
    This is not meant to replicate all of oData capabilities.
    For full information see:
    http://docs.oasis-open.org/odata/odata/v4.0/errata03/os/complete/part2-url-conventions/odata-v4.0-errata03-os-part2-url-conventions-complete.html#_Toc453752358
    Returns:
        [type]: [description]
    """  # noqa

    and_str = " and "
    or_str = " or "
    not_str = " not "

    @staticmethod
    def not_(filter_: str) -> str:
        return f" not {filter_}"

    @staticmethod
    def group(filter_: str) -> "oDataFilterHelper":
        return f" ( {filter_} ) "

    @staticmethod
    def in_(field_name: str, *values: str, camelize: bool = True) -> str:
        q = [f"'{v}'" for v in values]
        return f"{camelize_arg(field_name, camelize=camelize)} in ({f', '.join(q)})"

    @staticmethod
    def equals(
        field_name: str, value: Union[str, int, float], camelize: bool = True
    ) -> str:
        """The eq operator returns true if the left operand is equal to the right
            operand, otherwise it returns false.

        The null value is equal to itself, and only to itself.

        Args:
            field_name (str): The name of the field to compare. Pass None for null.
            value (Union[str, int, float]): The value to compare.
            camelize (bool): Camelize the field_name. Defaults to True.

        Returns:
            str: field_name eq value or field_name eq 'value'
                e.g Name eq 'My Portfolio'
        """

        field_name = camelize_arg(field_name, camelize)
        if value is None:
            return f"{field_name} eq null"
        if isinstance(value, str):
            return f"{field_name} eq '{value}'"
        return f"{field_name} eq {value}"

    @staticmethod
    def not_equals(
        field_name: str, value: Union[str, int, float], camelize: bool = True
    ) -> str:
        """The ne operator returns true if the left operand is not equal to the right
            operand, otherwise it returns false.

        The null value is equal to itself, and only to itself.

        Args:
            field_name (str): The name of the field to compare. Pass None for null.
            value (Union[str, int, float]): The value to compare.
            camelize (bool): Camelize the field_name. Defaults to True.

        Returns:
            str: field_name neq value or field_name neq 'value'
                e.g Name neq 'My Portfolio'
        """
        field_name = camelize_arg(field_name, camelize)
        if value is None:
            return f"{field_name} ne null"
        if isinstance(value, str):
            return f"{field_name} ne '{value}'"
        return f"{field_name} ne {value}"

    @staticmethod
    def greater_than(
        field_name: str, value: Union[str, int, float], camelize: bool = True
    ) -> str:
        """The gt operator returns true if the left operand is greater than the right
            operand, otherwise it returns false.

        If any operand is null, the operator returns false.
        For Boolean values, true is greater than false.

        Args:
            field_name (str): The name of the field to compare.
            value (Union[str, int, float]): The value to compare. Pass None for null.
            camelize (bool): Camelize the field_name. Defaults to True.

        Returns:
            str: field_name gt value or field_name gt 'value'
                e.g Name gt 'My Portfolio'
        """
        field_name = camelize_arg(field_name, camelize)
        if value is None:
            return f"{field_name} gt null"
        if isinstance(value, str):
            return f"{field_name} gt '{value}'"
        return f"{field_name} gt {value}"

    @staticmethod
    def greater_than_or_equal(
        field_name: str, value: Union[str, int, float], camelize: bool = True
    ) -> str:
        """The ge operator returns true if the left operand is greater than or equal to
         the right operand, otherwise it returns false.

        If only one operand is null, the operator returns false. If both operands are
         null, it returns true because null is equal to itself.

        Args:
            field_name (str): The name of the field to compare.
            value (Union[str, int, float]): The value to compare. Pass None for null.
            camelize (bool): Camelize the field_name. Defaults to True.

        Returns:
            str: field_name ge value or field_name ge 'value'
                e.g Name ge 'My Portfolio'
        """
        field_name = camelize_arg(field_name, camelize)
        if value is None:
            return f"{field_name} ge null"
        if isinstance(value, str):
            return f"{field_name} ge '{value}'"
        return f"{field_name} ge {value}"

    @staticmethod
    def less_than_or_equal(
        field_name: str, value: Union[str, int, float], camelize: bool = True
    ) -> str:
        """The le operator returns true if the left operand is less than or equal to the
         right operand, otherwise it returns false.

        If only one operand is null, the operator returns false. If both operands are
         null, it returns true because null is equal to itself.

        Args:
            field_name (str): The name of the field to compare.
            value (Union[str, int, float]): The value to compare. Pass None for null.
            camelize (bool): Camelize the field_name. Defaults to True.

        Returns:
            str: field_name le value or field_name le 'value'
                e.g Name le 'My Portfolio'
        """
        field_name = camelize_arg(field_name, camelize)
        if value is None:
            return f"{field_name} le null"
        if isinstance(value, str):
            return f"{field_name} le '{value}'"
        return f"{field_name} le {value}"

    @staticmethod
    def less_than(
        field_name: str, value: Union[str, int, float], camelize: bool = True
    ) -> str:
        """The lt operator returns true if the left operand is less than the right
        operand, otherwise it returns false.

        If any operand is null, the operator returns false.

        Args:
            field_name (str): The name of the field to compare.
            value (Union[str, int, float]): The value to compare. Pass None for null.
            camelize (bool): Camelize the field_name. Defaults to True.

        Returns:
            str: field_name lt value or field_name lt 'value'
                e.g Name lt 'My Portfolio'
        """
        field_name = camelize_arg(field_name, camelize)
        if value is None:
            return f"{field_name} gt null"
        if isinstance(value, str):
            return f"{field_name} gt '{value}'"
        return f"{field_name} gt {value}"

    @staticmethod
    def starts_with(field_name: str, value: str, camelize: bool = True) -> str:
        """The startswith function returns true if the first parameter string value
            starts with the second parameter string value, otherwise it returns false.

        Args:
            field_name (str): The name of the field to compare.
            value (str): The value to compare.
            camelize (bool): Camelize the field_name. Defaults to True.

        Returns:
            [str]:
                startswith(field_name,'value')
                e.g. startswith(Name, 'My Port')
        """
        field_name = camelize_arg(field_name, camelize)
        return f"startswith({field_name}, '{value}')"

    @staticmethod
    def ends_with(field_name: str, value: str, camelize: bool = True) -> str:
        """The endswith function returns true if the first parameter string value ends
            with the second parameter string value, otherwise it returns false.

        Args:
            field_name (str): The name of the field to compare.
            value (str): The value to compare.
            camelize (bool): Camelize the field_name. Defaults to True.

        Returns:
            [str]:
                endswith(field_name,'value')
                e.g. endswith(Name, 'folio')
        """
        field_name = camelize_arg(field_name, camelize)
        return f"endswith({field_name}, '{value}')"

    @staticmethod
    def contains(field_name: str, value: str, camelize: bool = True) -> str:
        """The contains function returns true if the second parameter string value is a
            substring of the first parameter string value, otherwise it returns false.

        Args:
            field_name (str): The name of the field to compare.
            value (str): The value to compare.
            camelize (bool): Camelize the field_name. Defaults to True.

        Returns:
            [str]:
                contains(field_name,'value')
                e.g. contains(Name, 'folio')
        """
        field_name = camelize_arg(field_name, camelize)
        return f"contains({field_name}, '{value}')"

    @staticmethod
    def to_lower(field_name: str, camelize: bool = True) -> str:
        """The tolower function returns the input parameter string value with all
        uppercase characters converted to lowercase according to Unicode rules.

        Args:
            field_name (str): The field name.
            camelize (bool): Camelize the field_name. Defaults to True.

        Returns:
            [str]:
                tolower(field_name)
                e.g. lower(Name)
        """
        field_name = camelize_arg(field_name, camelize)
        return f"tolower({field_name})"

    @staticmethod
    def to_upper(field_name: str, camelize: bool = True) -> str:
        """The toupper function returns the input parameter string value with all
         lowercase characters converted to uppercase according to Unicode rules.

        Args:
            field_name (str): The field name.
            camelize (bool): Camelize the field_name. Defaults to True.

        Returns:
            [str]:
                toupper(field_name)
                e.g. toupper(Name)
        """
        field_name = camelize_arg(field_name, camelize)
        return f"toupper({field_name})"

    @staticmethod
    def length(field_name: str, camelize: bool = True) -> str:
        """The length function returns the number of characters in the parameter value.

        Args:
            field_name (str): The field name.
            camelize (bool): Camelize the field_name. Defaults to True.

        Returns:
            [str]:
                length(field_name)
                e.g. length(Name)
        """
        field_name = camelize_arg(field_name, camelize)
        return f"length({field_name})"
