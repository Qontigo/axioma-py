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


Based on the GS Quant toolkit
Copyright 2019 Goldman Sachs under Apache License 2.0
"""

import builtins
import copy
import keyword
from abc import ABC, abstractmethod
from collections import namedtuple
from datetime import date, datetime
from enum import Enum
from functools import wraps
from inspect import Parameter, signature
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    MutableMapping,
    MutableSequence,
    MutableSet,
    Tuple,
    Type,
    TypeVar,
    Union,
    get_type_hints,
)

import inflection
from typing_inspect import (
    get_args,
    get_origin,
    is_generic_type,
    is_optional_type,
    is_tuple_type,
    is_union_type,
)

from .utils import date_arg_fmt


class PropTypeEnums(Enum):
    EnumType = "EnumType"
    IterableEnumType = "IterableEnumType"
    CommonBaseType = "CommonBaseType"
    IterableCommonBaseType = "IterableCommonBaseType"
    DictOfCommonBase = "DictOfCommonBase"
    Date = "Date"
    DateTime = "DateTime"
    OtherType = "OtherType"


class EnumBase(str, Enum):
    """Base type for subclassing for any enumerations

    Arguments:
        str {[type]} -- Inherits from str so will support json serialization though
                        json.dumps(enum_thing, default=str) though enums should be
                        converted to value in the to_dict method...so could try removing
        Enum {[type]} --

    Returns:
        [type] -- [description]
    """

    @classmethod
    def _missing_(cls, name):
        for member in cls:
            if member.value.lower() == name.lower():
                return member


def get_enum_value(enum_type: Type, enum_value: Union[str, EnumBase]):
    """Gets instance of enum_type and allows None to be passed when
    creating instances from_dict() methods on entity base which initially
    sets values to None

    Arguments:
        enum_type {Type} -- [description]
        enum_value {Union[str, EnumBase]} -- [description]

    Returns:
        [type] -- [description]
    """
    if enum_value in (None, "None"):
        return None
    else:
        return enum_type(enum_value)


def none_or_instance(arg: Any, type_: Type):
    """Simple helper for use in property assignment, if the arg is none returns none, 
    else will create an instance of the type passed

    Args:
        arg (Any): argument to initialise type with
        type_ (Type): type to initialse if arg is none

    Returns:
        [type]: [description]
    """

    if arg is None:
        return None
    return type_(arg)


Prop_info = namedtuple("Prop_info", ["is_iterable", "is_entity", "is_enum"])


def _normalise_arg(argv: str) -> str:
    """appends '_' to a the arg if it is a keyword

    Args:
        argv (str): [description]

    Returns:
        str: [description]
    """
    if keyword.iskeyword(argv) or argv in dir(builtins):
        return argv + "_"
    else:
        return argv


_TFunc = TypeVar("_TFunc", bound=Callable[..., Any])


def do_not_clone(func: _TFunc) -> _TFunc:
    """A decorator to be used on properties that should be ignored when cloning

    Arguments:
        func {[type]} -- [description]

    Returns:
        [type] -- [description]
    """
    func.do_not_clone = True
    return func


def do_not_serialise(func: _TFunc) -> _TFunc:
    """A decorator to be used on properties that should be ignored when converting to
    dict

    Arguments:
        func {[type]} -- [description]

    Returns:
        [type] -- [description]
    """
    func.do_not_serialise = True
    return func


def camel_case_translate(f: _TFunc) -> _TFunc:
    """Allows method arguments to be passed as camel case when they are defined as
    snake_case

    Arguments:
        f {[type]} -- [description]

    Raises:
        ValueError: [description]

    Returns:
        [type] -- [description]
    """

    @wraps(f)
    def wrapper(*args, **kwargs):
        normalised_kwargs = {}
        for arg, value in kwargs.items():
            arg = _normalise_arg(arg)

            if not arg.isupper():
                snake_case_arg = inflection.underscore(arg)
                if snake_case_arg != arg:
                    if snake_case_arg in kwargs:
                        raise ValueError(
                            "{} and {} both specified".format(arg, snake_case_arg)
                        )

                    normalised_kwargs[snake_case_arg] = value
                else:
                    normalised_kwargs[arg] = value
            else:
                normalised_kwargs[arg] = value

        return f(*args, **normalised_kwargs)

    return wrapper


class CommonBase(ABC):
    @abstractmethod
    def clone(self, **kwargs):
        raise NotImplementedError("Class must implement method")

    @abstractmethod
    def to_dict(self, **kwargs) -> dict:
        raise NotImplementedError("Class must implement method")


S = TypeVar("S", bound="EntityBase")


class EntityBase(CommonBase):
    """The base class which all entities (anything that has a model) classes
    should subclass. Defines a series of methods to help build and manipulate entities.


    Arguments:
        ABC {[type]} -- [description]

    Returns:
        [type] -- [description]
    """

    __properties = set()

    def __init__(self: S, **kwargs) -> S:
        pass

    @classmethod
    def default_instance(cls: Type[S]) -> S:
        """
        Construct a default instance of this type
        """
        args = [
            k
            for k, v in signature(cls.__init__).parameters.items()
            if v.default == Parameter.empty
        ][1:]
        required = {a: None for a in args}
        return cls(**required)

    @classmethod
    def class_properties(cls) -> set:
        """Returns public properties of class

        Returns:
            set -- with properties
        """
        if not cls.__properties:
            s = set(
                i
                for i in dir(cls)
                if isinstance(getattr(cls, i), property) and not i.startswith("_")
            )
            cls.__properties = s
        return cls.__properties

    @classmethod
    def _translate_to_class_prop(cls, prop_name: str, reverse: bool = False) -> str:
        """ Performs translation of the prop_name from the model prop name to a name
        consistent with class props. If a class prop name style name is passed it
        returns the name unchanged. The class prop does not have to exist.

        Args:
            prop_name (str): the name to translate to a class prop name
            reverse (bool, optional): perform the reverse translation. Defaults to
            False.

        Returns:
            str: a name consistent with the class prop format (or model when reverse
            True)
        """
        if reverse:
            return inflection.camelize(prop_name, False)
        return inflection.underscore(prop_name)

    @classmethod
    def _get_prop_type(cls, prop) -> PropTypeEnums:
        """Check the return type of the class property so can call to_dict()
        where needed, checked in the following order
        (Any of the following can be wrapped in Optional)
        CommonBase
        EnumBase
        Dict[Any, CommonBase]
        Iterable[CommonBase], List[CommonBase], Tuple[CommonBase]
        Iterable[EnumBase], List[EnumBase], Tuple[EnumBase]

        Will not recognise generic iterables with multiple type args e.g.
        Mapping[x, CommonBase], these will return Other.

        Args:
            prop ([type]): [description]

        Returns:
            PropTypeEnums: [description]
        """
        return_hints = get_type_hints(getattr(cls, prop).fget).get("return")

        # no hints
        if return_hints is None:
            return PropTypeEnums.OtherType

        return_hints_adj = return_hints
        if is_optional_type(return_hints):
            # assume properties get return can only be None or max 1 other type
            # i.e. Optional[SomeType]
            return_hints_adj = get_args(return_hints)[0]

        # Union should not be used for a return type - this should be redundant
        if is_union_type(return_hints_adj):
            # don't think this should be met for a property of subclass of entity...
            return PropTypeEnums.OtherType

        # See if there are any args - if not can test type directly
        args = get_args(return_hints_adj)
        if not args:
            if issubclass(return_hints_adj, EnumBase):
                return PropTypeEnums.EnumType

            # prop has type common base
            if issubclass(return_hints_adj, CommonBase):
                return PropTypeEnums.CommonBaseType

            if issubclass(return_hints_adj, datetime):
                return PropTypeEnums.DateTime

            if issubclass(return_hints_adj, date):
                return PropTypeEnums.Date

            return PropTypeEnums.OtherType

        # Identify generics and tuple with args Dict[] and Iterable[] and tuple[]
        # (which includes List[] etc)
        if is_generic_type(return_hints_adj) or is_tuple_type(return_hints_adj):

            origin = get_origin(return_hints_adj)
            if args:
                arg = args[-1]
                # check arg is a class (e.g. a typevar from a generic)
                if not isinstance(arg, type):
                    return PropTypeEnums.OtherType
                if origin and issubclass(origin, Dict):
                    if issubclass(arg, CommonBase):
                        return PropTypeEnums.DictOfCommonBase
                elif origin and issubclass(origin, Iterable) and len(args) == 1:
                    if issubclass(arg, CommonBase):
                        return PropTypeEnums.IterableCommonBaseType
                    if issubclass(arg, EnumBase):
                        return PropTypeEnums.IterableEnumType

            return PropTypeEnums.OtherType

        return PropTypeEnums.OtherType

    @classmethod
    def __get_prop_type(cls, prop) -> Prop_info:
        """ TO DELETE """
        return_hints = get_type_hints(getattr(cls, prop).fget).get("return")
        is_iterable = False
        if is_optional_type(return_hints):
            # assume properties get return can only be None or max 1 other type
            return_hints = get_args(return_hints)[0]
        if is_union_type(return_hints):
            # don't think this should be met for a property of subclass of entity...
            return Prop_info(
                prop_type=None, is_iterable=False, is_entity=False, is_enum=False
            )
        is_enum = return_hints is not None and issubclass(return_hints, EnumBase)
        if is_generic_type(return_hints):
            # not necessarily iterable. might need to make iterable base class or
            # something or expose the generic type in the generics
            args = get_args(return_hints)
            if len(args) > 0:
                return_hints = get_args(return_hints)[0]
            is_iterable = issubclass(return_hints, Iterable)
        arg_tmp = get_args(return_hints)
        if arg_tmp:
            return_hints = arg_tmp[0]
        is_base = return_hints is not None and issubclass(return_hints, CommonBase)
        is_enum = return_hints is not None and issubclass(return_hints, EnumBase)
        return Prop_info(is_iterable=is_iterable, is_entity=is_base, is_enum=is_enum)

    def values(self):
        """Do not use

        Returns:
            [type]: [description]
        """

        return self.__dict__.values()

    def keys(self):
        """Do not use

        Returns:
            [type]: [description]
        """

        return self.__dict__.keys()

    def get(self, name, default=None):
        """Gets an attribute of the class by name

        Arguments:
            name {[type]} -- Attribute to return

        Keyword Arguments:
            default {[type]} -- value if not found (default: {None})

        Returns:
            [type] -- attribute value
        """
        return getattr(self, name, default)

    def _resolve_class_property(self, key: str) -> str:
        """given a property or attribute that may be in model format resolve it
        to a class property or attribute (if no prop or attribute exists the value is
        returned unchanged)

        Args:
            key (str): [description]

        Returns:
            str: [description]
        """
        cls_props = super().__getattribute__("class_properties")()
        inst_props = set(key for key in self.__dict__.keys())

        properties = cls_props.union(inst_props)
        snake_case_key = self._translate_to_class_prop(key)
        key_is_property = key in properties
        snake_case_key_is_property = snake_case_key in properties

        if snake_case_key_is_property and not key_is_property:
            return snake_case_key
        else:
            return key

    def __getattr__(self, key):
        class_key = self._resolve_class_property(key)
        return super().__getattribute__(class_key)

    def __setattr__(self, key, value):
        class_key = self._resolve_class_property(key)
        return super().__setattr__(class_key, value)

    def _delete_attribute(self, name):
        """

        Args:
            name ([type]): [description]
        """
        if name in self.keys():
            delattr(self, name)

    def __str__(self):
        return str(self.to_dict(translate=False, filter_none=False))

    def __repr__(self):
        return self.__str__()

    def __getitem__(self, name: str):
        return getattr(self, name)

    def __setitem__(self, name: str, val: Any):
        setattr(self, name, val)

    def __contains__(self, name: str):
        return name in self.__dict__

    def __len__(self):
        return len(self.__dict__)

    def __eq__(self, other):
        return type(self) == type(other) and all(
            self[p] == other[p] for p in self.class_properties()
        )

    def __hash__(self):
        return hash(str(self))

    def _to_dict_(
        self, cls_props, translate=True, filter_none=True, cloning=False
    ) -> dict:
        """ TO DELETE ******


        Args:
            cls_props (set): The set of props to serialse.
            camel_case (bool, optional): [description]. Defaults to True.
            filter_none (bool, optional): [description]. Defaults to True.
            cloning (bool, optional): [description]. Defaults to False.

        Returns:
            dict: [description]
        """

        cls_props_mask = set("_" + prop for prop in cls_props)
        instance_attr = set()  # set(key for key in self.__dict__.keys())
        as_dict = {}
        for att in cls_props.union(instance_attr - cls_props_mask):
            do_not_serialise = getattr(
                getattr(type(self), att).fget, "do_not_serialise", False
            )
            do_not_clone = getattr(getattr(type(self), att).fget, "do_not_clone", False)
            if not (do_not_serialise and not cloning) and not (
                cloning and do_not_clone
            ):
                att_value = getattr(self, att, None)
                att_value_dict = att_value
                if att_value is not None:
                    info: Prop_info
                    info = self._get_prop_type(att)

                    if info.is_enum:
                        att_value_dict = att_value.value
                    elif info.is_entity:
                        if info.is_iterable:
                            att_value_dict = []
                            for entity in att_value:
                                d = entity.to_dict(
                                    translate=translate,
                                    filter_none=filter_none,
                                    cloning=cloning,
                                )
                                if len(d) > 0:  # shouldn't really happen...
                                    att_value_dict.append(d)
                        else:
                            att_value_dict = att_value.to_dict(
                                translate=translate,
                                filter_none=filter_none,
                                cloning=cloning,
                            )
                            if len(att_value_dict) == 0:  # as above
                                continue

                if not (filter_none and att_value_dict is None):
                    as_dict[att] = att_value_dict
        # as_dict = { att:  for att in cls_props.union(instance_attr-cls_props_mask)}
        return as_dict

    def _to_dict(
        self, cls_props, translate=True, filter_none=True, cloning=False
    ) -> dict:
        """ For each property in this instance, return a dictionary representation
        that matches the corresponding data model.
        Where the property type hint is enumbase, get value. Where it is a subclass of
        entitybase or iterable of entitybase, call the to_dict method on the instances.


        Args:
            cls_props (set): The set of props to serialse.
            camel_case (bool, optional): [description]. Defaults to True.
            filter_none (bool, optional): [description]. Defaults to True.
            cloning (bool, optional): [description]. Defaults to False.

        Returns:
            dict: [description]
        """

        cls_props_mask = set("_" + prop for prop in cls_props)
        instance_attr = set()  # set(key for key in self.__dict__.keys())
        as_dict = {}
        for att in cls_props.union(instance_attr - cls_props_mask):
            do_not_serialise = getattr(
                getattr(type(self), att).fget, "do_not_serialise", False
            )
            do_not_clone = getattr(getattr(type(self), att).fget, "do_not_clone", False)
            if not (do_not_serialise and not cloning) and not (
                cloning and do_not_clone
            ):
                att_value = getattr(self, att, None)
                att_value_dict = att_value
                if att_value is not None:
                    prop_type: PropTypeEnums
                    prop_type = self._get_prop_type(att)

                    if prop_type == PropTypeEnums.EnumType:
                        att_value_dict = att_value.value
                    elif prop_type == PropTypeEnums.CommonBaseType:
                        att_value_dict = att_value.to_dict(
                            translate=translate,
                            filter_none=filter_none,
                            cloning=cloning,
                        )
                        if len(att_value_dict) == 0:  # as above
                            continue
                    elif prop_type == PropTypeEnums.IterableEnumType:
                        att_value_dict = []
                        for enum in att_value:
                            att_value_dict.append(enum.value)
                    elif prop_type == PropTypeEnums.IterableCommonBaseType:
                        att_value_dict = []
                        for entity in att_value:
                            d = entity.to_dict(
                                translate=translate,
                                filter_none=filter_none,
                                cloning=cloning,
                            )
                            if len(d) > 0:  # shouldn't really happen...
                                att_value_dict.append(d)
                    elif prop_type == PropTypeEnums.DictOfCommonBase:
                        att_value_dict = []
                        for entity in att_value.values():
                            d = entity.to_dict(
                                translate=translate,
                                filter_none=filter_none,
                                cloning=cloning,
                            )
                            if len(d) > 0:  # shouldn't really happen...
                                att_value_dict.append(d)
                    elif prop_type == PropTypeEnums.Date:
                        att_value_dict = date_arg_fmt(att_value, format="%Y-%m-%d")
                    elif prop_type == PropTypeEnums.DateTime:
                        att_value_dict = date_arg_fmt(
                            att_value, format="%Y-%m-%dT00:00:00"
                        )
                if not (filter_none and att_value_dict is None):
                    as_dict[att] = att_value_dict
        # as_dict = { att:  for att in cls_props.union(instance_attr-cls_props_mask)}
        return as_dict

    def to_dict(self, translate=True, filter_none=True, cloning=False) -> dict:
        """Return the entity as a dictionary

        Keyword Arguments:
            camel_case {bool} -- properties will be camel case (else snake case)
                                (default: {True})
            filter_none {bool} -- filter properties with value None (default: {True})

        Returns:
            [type] -- dict representation of entity
        """
        snake_case_dict = self._to_dict(
            cls_props=self.class_properties(),
            translate=translate,
            filter_none=filter_none,
            cloning=cloning,
        )

        snake_case_dict = {
            key: value
            for key, value in snake_case_dict.items()
            if not (filter_none and value is None)
        }
        if translate:
            # to do need to
            camel_case_dict = {
                inflection.camelize(key, False): value
                for key, value in snake_case_dict.items()
            }
            return camel_case_dict
        else:
            return snake_case_dict

    def overwrite(self, other: Union[dict, Type["EntityBase"]]) -> None:
        """Legacy, use replace method instead
        Update this instance properties with those passed in other
        this to be called update()
        Any items with a None value will be ignored.
        When a subclass of EntityBase is passed the entity will be converted to a
        dictionary before performing the update

        Arguments:
            other {Union[dict, Type[} -- the item to overwrite the current instance
            props with
        """
        self._update(other, True)

    def update(self, other: Union[dict, Type["EntityBase"]]) -> None:
        """Update this instance properties with those passed in other
        Any items with a None value will be ignored.
        When a subclass of EntityBase is passed the entity will be converted to a
        dictionary before performing the update

        Arguments:
            other {Union[dict, Type[} -- the item to overwrite the current instance
            props with
        """
        self._update(other, True)


    def _update(
        self, other: Union[dict, Type["EntityBase"]], ignore_none=False
    ) -> None:
        """Updates the caller with the passed argument.
        Any None values will be ignored if ignore_none is true.
        Does not check that types are same.
        Will skip properties that are on other but not on self.
        Will skip properties that do not have setter.

        Args:
            other (Union[dict, Type[): [description]
            ignore_none: will not update with any attributes that are none
        """

        # the class...?

        self_properties = self.class_properties()
        if isinstance(other, EntityBase):
            other_props = other.class_properties()
        else:
            other_props = other.keys()

        for p in other_props:
            v = other[p]
            if not (ignore_none and v is None):
                p_res = self._resolve_class_property(p)
                if p_res in self_properties:
                    if getattr(type(self), p_res).fset is not None:
                        setattr(self, p_res, v)

    def replace(self, other: Union[dict, Type["EntityBase"]]) -> None:
        """sets all properties as for the default instance then
        updates with properties from other.

        Args:
            other (Union[dict, Type[): [description]
        """
        default_instance = self.default_instance()
        self._update(default_instance)
        self.update(other)

    def clone(self: S, remove: List[str] = None, **kwargs) -> S:
        """Creates a clone of the current entity

        Keyword Arguments:
            remove {List[str]} -- properties to remove when cloning (default: {None})

        Returns:
            [EntityBase] -- [Returns a new instance of the current class]
        """
        if(remove is None):
            remove = []
        self_dict = self.to_dict(cloning=True)
        new = self.from_dict(self_dict)
        new._update(kwargs)
        for key in remove:
            new._delete_attribute(key)
        return new

    @classmethod
    def from_dict(cls: Type[S], definition: dict) -> S:
        """Create an instance of the class from the dictionary

        Arguments:
            definition {dict} -- dictionary to build the class instance from

        Returns:
            [type] -- class instance]
        """
        # make a copy so the input object is unchanged.
        def_copy = copy.deepcopy(definition)
        args = [
            k
            for k, v in signature(cls.__init__).parameters.items()
            if k not in ("kwargs", "_kwargs") and v.default == Parameter.empty
        ][1:]
        required = {}
        for arg in args:
            required[arg] = def_copy.pop(arg, None)
            required[arg] = def_copy.pop(arg, required[arg])
        instance = cls(**required)
        instance._update(def_copy)
        return instance

    @staticmethod
    def get_as_dict(obj: Union[dict, "EntityBase"]) -> dict:
        """Converts obj to dict if instance of current class type

        Arguments:
            obj {Union[dict, EntityBase]} -- [description]

        Returns:
            dict -- [description]
        """
        if isinstance(obj, EntityBase):
            return obj.to_dict()
        return obj

    @classmethod
    def get_as_instance(cls: Type[S], obj: Union[dict, "EntityBase"]) -> S:
        """If obj passed is dict will return an instance built from
        the dict otherwise returns obj

        Arguments:
            obj {Union[dict, EntityBase]} -- [description]
            cls {type} -- the type to build from the dictionary

        Returns:
            EntityBase -- instance or original arg
        """
        if isinstance(obj, dict):
            return cls.from_dict(obj)
        return obj


def get_as_dict(obj: Union[dict, CommonBase]) -> dict:
    """If obj has a to_dict() method (i.e. is a subclass of CommonBase) convert it to a
    dictionary
    otherwise return the arg

    Args:
        obj (Union[dict, CommonBase]): [description]

    Returns:
        dict: [description]
    """
    if isinstance(obj, CommonBase):
        return obj.to_dict()
    return obj


R = TypeVar("R", bound="TemplatedEntityBase")


class TemplatedEntityBase(EntityBase):
    """A base class for creating templated entities
    The two properties _TEMPLATE_NAME and _TEMPLATE_MAPPING should be set in the sub
    class. The _TEMPLATE_MAPPING should be a list of tuples listing the class properties
    that are part of the content section and the mapping between the model and the
    class props within the content property like
    [(model_prop_name, class_prop_name ), ..]

    """

    _TEMPLATE_NAME: str = ""
    _TEMPLATE_MAPPING: List[Tuple[str, str]] = []

    def __init__(self: R,) -> R:
        super().__init__()

    @property
    def template_name(self) -> str:
        """The template name associated with this class returns the class property

        Returns:
            [type]: [description]
        """
        return self._TEMPLATE_NAME

    @template_name.setter
    def template_name(self, template_name: str):
        """Do not use - required for the generic

        Args:
            template_name (str): [description]

        Raises:
            here: [description]
        """
        if template_name != self._TEMPLATE_NAME:
            raise ValueError(
                f"This class '{self.__class__.__name__}' is associated with "
                f"template '{self._TEMPLATE_NAME}' but a template name"
                f" of '{template_name}' is trying to be set."
            )

    @property
    def content(self) -> dict:
        """Get the content of the template instance (in class format).
        The content property is built from the sub properties identified
        in the _TEMPLATE_MAPPING prop.

        Returns:
            dict: A dictionary of the content attribute
        """
        content = {k[1]: self.get(k[1]) for k in self.get_content_map()}
        return content

    @content.setter
    def content(self, content: dict):
        """Sets the content properties (acts as a pass through the to properties ) by
        updating self with content

        Args:
            content (dict): [description]
        """
        self.update(content)

    @classmethod
    def get_content_map(cls) -> List[Tuple[str, str]]:
        """Return a list of tuples where each tuple contains the model prop name
        and class prop name within the content section.

        Returns:
            List[Tuple[str, str]]: [description]
        """
        return cls._TEMPLATE_MAPPING

    @classmethod
    def _get_content_class_key(cls, key: str) -> str:
        """Returns the class key for the content attribute corresponding to the
        key passed based on the _get_content_mapping if no mapping key is found returns
        key unchanged

        Args:
            key (str): key to apply

        Returns:
            Union[str, None]: relevant class attribute/property
        """
        content_map = cls.get_content_map()
        class_content_map = {i[1]: i for i in content_map}
        model_content_map = {i[0]: i for i in content_map}

        if key in class_content_map and key not in model_content_map:
            return key
        elif key in model_content_map:
            return model_content_map[key][1]
        else:
            return key

    def _resolve_class_property(self, key: str) -> str:
        """given a property or attribute that may be in model format, resolve it
        to a class property or attribute (if no prop or attribute exists the value is
        returned unchanged)

        Args:
            key (str): [description]

        Returns:
            str: [description]
        """
        content_key = self._get_content_class_key(key)
        return super()._resolve_class_property(content_key)

    def to_dict(self, translate=True, filter_none=True, cloning=False) -> dict:
        """Creates an instance of this class as a dictionary

        Returns:
            [dict]: the dictionary representation of this class as returned or passed to
            an analysis definition
        """
        all_cls_props = self.class_properties()
        class_dict = self._to_dict(
            cls_props=all_cls_props,
            translate=translate,
            filter_none=filter_none,
            cloning=cloning,
        )

        content_prop_mapping = self.get_content_map()

        content_dict = {}
        for prop in content_prop_mapping:
            if prop[1] in class_dict:
                if translate:
                    content_dict[prop[0]] = class_dict.pop(prop[1])
                else:
                    content_dict[prop[1]] = class_dict.pop(prop[1])

        if content_dict:
            class_dict["content"] = content_dict

        if translate:
            # to do need to
            translated_dict = {
                self._translate_to_class_prop(key, reverse=True): value
                for key, value in class_dict.items()
            }
            return translated_dict
        else:
            return class_dict


T = TypeVar("T", bound=EntityBase)


class EntityCollectionBase(CommonBase):
    def __init__(self):
        super().__init__()

    @abstractmethod
    def get_items(self) -> Iterable[T]:
        """Gets an iterable of the entities in the collection

        Returns:
            List[T]: [description]
        """
        raise NotImplementedError("get_items must be implmented in subclass")

    def clone(self):
        """Returns a new instance of the class where the underlying entities are also
        cloned

        Returns:
            [type]: cloned instance of self
        """
        return type(self)((item.clone() for item in self.get_items()))

    def to_dict(self, translate=True, filter_none=True, cloning=False) -> List[dict]:
        """Returns a list of the members converted to dict

        Returns:
            List[dict]: [description]
        """
        as_dict = [
            item.to_dict(translate=translate, filter_none=filter_none, cloning=cloning)
            for item in self.get_items()
        ]
        return as_dict

    def __str__(self):
        return str(self.to_dict(translate=False, filter_none=False))

    def __repr__(self):
        return self.__str__()


class EntitySequence(MutableSequence[T], EntityCollectionBase):
    """The base type for which a mutable sequence of entities should subclass
    e.g. Indentifiers
    Arguments:
        MutableSequence {[type]} -- [description]
    """

    def __init__(
        self,
        entity_iterable: Iterable[EntityBase] = None,
        member_type: Type = Type[EntityBase],
    ):
        """The base type for which a mutable sequence of entities should subclass
        e.g. Indentifiers

        Keyword Arguments:
            entity_iterable {Iterable[EntityBase]} -- iterable entities (default: {[]})
            member_type {Type} -- the type of the entity used in the subclass)
        """
        if(entity_iterable is None):
            entity_iterable = []
        self._member_cls = member_type
        self._elements = list(entity_iterable)

    def __len__(self):
        return len(self._elements)

    def __getitem__(self, index: int) -> EntityBase:
        return self._elements[index]

    def __iter__(self):
        return iter(self._elements)

    def __setitem__(self, index: int, value: Union[EntityBase, dict]) -> None:
        self._elements[index] = self._member_cls.get_as_instance(value)

    def __delitem__(self, index: int) -> None:
        del self._elements[index]

    def __eq__(self, other):
        return list(self) == list(other)

    def _get_as_iter(
        self, item: Union[Iterable[Any], dict, EntityBase]
    ) -> Iterable[Any]:
        if item is None:
            return []
        if isinstance(item, (dict, EntityBase)):
            return [item]
        return item

    def get_items(self):
        return self._elements

    def insert(self, index: int, value: Union[EntityBase, dict]):
        """Add to the sequency at the index

        Args:
            index (int): [description]
            value (Union[EntityBase, dict]): [description]
        """
        self._elements.insert(index, self._member_cls.get_as_instance(value))


class EntitySet(MutableSet[T], EntityCollectionBase):
    def __init__(
        self,
        element_iterable: Iterable[EntityBase] = None,
        removed_elements: Iterable[EntityBase] = None,
    ):
        if(element_iterable is None):
            element_iterable = []
        if(removed_elements is None):
            removed_elements = []
        self._elements = list(element_iterable)

    @abstractmethod
    def _element_eq_(self, value1, value2) -> bool:
        raise NotImplementedError

    def __iter__(self):
        return iter(self._elements)

    def __contains__(self, value: EntityBase):
        return any(self._element_eq_(element, value) for element in self._elements)

    def __len__(self):
        return len(self._elements)

    def get_items(self):
        return self._elements

    def add(self, value: EntityBase):
        """Add an entity to the set if it is not present

        Arguments:
            value {EntityBase} -- The entity to add to the set
        """
        if value not in self:
            self._elements.append(value)

    def union(self, other):
        return type(self)(other + self)

    def intersection(self, other):
        return type(self)(other & self)

    def difference(self, other):
        return type(self)(other - self)

    def discard(self, value: EntityBase):
        """Remove the item from the set

        Arguments:
            value {EntityBase} -- [description]
        """
        indices = [
            i
            for i in range(len(self._elements))
            if self._element_eq_(self._elements[i], value)
        ]
        for i in indices:
            self._elements.pop(i)

    def replace(self, value, add_if_missing=False):
        """Replace (remove existing and add new) the element in the set, optionally
        add if not present

        Arguments:
            value {[type]} -- Entity to replace

        Keyword Arguments:
            add_if_missing {bool} -- add() if not in set (default: {False})
        """
        if value in self or add_if_missing:
            self.discard(value)
            self.add(value)

    def update_entity(self, value):
        updates = [
            i.overwrite()
            for i in self._elements
            if self._element_eq_(self._elements[i], value)
        ]
        return updates[0] if len(updates) > 0 else None

    def update(self, entity_set):
        """Updates (overwrites) the underlying entity with this entity's properties

        Arguments:
            entity_set {[type]} -- the set to update from

        Raises:
            ValueError: sets must be of same type
        """
        if not type(self) is type(entity_set):
            raise ValueError(
                f"Set can only be updated with set of same type. \
                    This class {type(self)} cannot be updated with {type(entity_set)}"
            )
        results = [self.update_entity(item) for item in entity_set]
        return results


class EntityMapping(MutableMapping[str, T], EntityCollectionBase):
    """The base class for which a mapping (entities with a 'key') of entities should be
    subclassed from e.g. portfolios or positions.
    The mapping is subclassed to allow adding dict which converts to entities to the set

    Arguments:
        Mapping {[type]} -- [description]
    """

    def __init__(self, keys: Iterable[str], values: Iterable[T], member_type: Type[T]):

        self._member_cls = member_type
        self._removed_entities = dict()
        self._entities = dict(zip(keys, values))
        for v in values:
            self.add(v)

    # The next  methods are requirements of the ABC.
    def __getitem__(self, key: str):
        return self._entities[key]

    def __setitem__(self, key: str, value: T):
        self.add(value)

    def __iter__(self) -> str:

        # of an equals __eq__ method it iterates and looks for the 'keys' in
        return iter(self._entities)

    def __len__(self):
        return len(self._entities)

    # want to support delete
    def __delitem__(self, key: str):
        del self._entities[key]

    def get_items(self):
        return self._entities.values()

    def update(self, other: Union["EntityMapping[T]", Iterable[T]]):
        """Update the items in this mapping with those
        passed in the argument. Where an item exists by key
        it will be overwritten with the

        Arguments:
            other {[type]} -- [description]
        """
        if isinstance(other, EntityMapping):
            other_map = other
        else:
            other_map = self.__class__(other)
        for _, entity in other_map.items():
            self.add(entity)

    def pop(self, key, default=None) -> T:
        """Removes the matching item from the mapping
        and returns or returns default if the key is not in the mapping

        Arguments:
            key {[type]} -- item to return

        Keyword Arguments:
            default {[type]} -- value returned if key not found (default: {None})

        Returns:
            [type] -- matching item or default
        """
        return self._entities.pop(key, default)

    def get(self, key, default=None) -> T:
        """Get the item corresponding to the key or return the default if key not present

        Arguments:
            key {[type]} -- key to return mapped item

        Keyword Arguments:
            default {[type]} -- value returned if key not present (default: {None})

        Returns:
            [type] -- matching entity
        """
        return self._entities.get(key, default)

    @abstractmethod
    def _make_key(self, entity: Union[dict, T]) -> str:
        """Method to create an appropriate key from the given entity

        Arguments:
            entity {[type]} -- entity instance

        Raises:
            NotImplementedError: -- abstract
        """
        raise NotImplementedError

    def _prepare_key(self, input_key: Any) -> str:
        return input_key

    def add(self, entity: Union[dict, T]):
        """Adds the entity to the mapping. Where the entity exists it will be
        replaced with the entity.

        Arguments:
            entity {Union[dict, Portfolio]} -- item to add
        """
        p_entity = self._member_cls.get_as_instance(entity)
        key = self._make_key(p_entity)
        self._entities[key] = p_entity

    def clone(self) -> T:
        clones = [item.clone() for item in self._entities.values()]
        return type(self)(clones)

    def to_dict(self, translate=True, filter_none=True, cloning=False) -> List[dict]:
        as_dict = [
            item.to_dict(translate=translate, filter_none=filter_none, cloning=cloning)
            for item in self._entities.values()
        ]
        return as_dict

    def to_list(self) -> List[T]:
        """Returns the mapping values as a list

        Returns:
            List[T]: a list of the values (entities) in the mapping
        """
        return list(self.values())

    def keys(self,):
        return self._entities.keys()

    def values(self,):
        return self._entities.values()
