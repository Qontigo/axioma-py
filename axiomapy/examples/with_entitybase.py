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
#!/usr/bin/env python
# coding: utf-8

# # CommonBase, EntityBase, TemplatedEntityBase, Enumbase and Collections
# 
# The following examples illustrate the functionality and usage of the base classes in constructing classes to represent API entities.
# Unless contributing to the package, this should be considered for information only and is not required to follow any other examples.
# 
# 
# ## Overview
# 
# The goal of the axioma-py package is to provide a set of classes and associated methods to facilitate working with the Axioma REST API.
# The intended benefits and goals of this package are:  
# * To provide a more intuitive interface for users less familiar with the API to increase usage.  
# * To allow developers to work with json/dict representations interchangeably with instances where more convenient.  
# * To improve the developer's and API user's experience.  
# * To reduce dependency on external documentation.  
# * To package more boiler plate code to reduce time to build applications.  
# * To include comprehensive examples and tutorials on usage. 
# * To include examples/art to help business users leverage the API or better understand its benefits. 
# * To be easy to collaborate on.  
# 
# 
# The core functional requirements of the package are: 
# * To have classes that capture the models of the API  
# * To provide supported nested models.   
# * To move from the class instances to the dict representations passed or returned by the API and vice-versa seamlessly.  
# * To support core user requirements such as cloning, updating, etc..  
# * To provide a developer experience consistent with the language requirements, e.g. snake casing/PEP8, etc.  
# 
# A series of 'abstract' base classes are used to provide this core functionality and should be sub-classed when creating an API model class.
# 
# 
# ## Architecture/Design
# 
# The sdk design has 4 distinct elements:  
# 1. Session: Manages all http requests to the remote app and triggers serialization/deserialization. Leverages requests Session and so can use existing connection pools, etc..   
# 2. Context Manager: manages switching sessions between contexts (i.e. with blocks).  
# 3. axiomapy: Interface to the RESTful API via the current Session  
# 4. Entities: All the data models and methods associated with working with the remote resources. Any actions on resource resources are handled by the axiomapy classes  
# 
# For functional usage of the session/context refer to: [with_axiomaapi](./with_axiomaapi.ipynb)  
# For functional usage axiomapy refer to: [with_sessions](./with_sessions.ipynb)
# 
# The remainder of this notebook considers the entities.
# 
# There are various base classes and there are code examples of each below:  
# * EnumBase - provides features for enumerations such as creation from strings, case-insensitivity etc.
# 
# * CommonBase - Represents serializable classes that are also cloneable.  
#     * Used for classes that do not need to initialize directly from a response but should serialize as part of a request.   
#     * For example, used as a base class in collections where the collection is initialized from an iterable of representations rather than directly.
# 
# * EntityBase(CommonBase) - apart from collections, all classes subclass this abstract class.  
#     * Provides methods to serialize to and from dict.  
#     * Provides methods to update/replace contents. 
#     * Provides dict-like methods (get, update) and property/attribute access instance\['property'\], instance.property.  
#     * Interrogates the subclass property's type hints to manage nested entities and special data types when serializing.  
#     * Handles translation between datamodel naming conventions (camel case) to python/PEP8 (snake case).  
# 
# * TemplatedEntityBase(EntityBase) - used to represent entities that are presented via templates.  
#     * Supports an explicit mapping between class properties and the data model (template). 
#     * Supports direct access to the content attributes from the upper level class.  
# 
# * EntityCollectionBase - a common base class for collections of entities arguably redundant.  
# 
# * EntitySequence(MutableSequence\[T\], EntityCollectionBase) - Represents a non-keyed/mapped set of entities e.g. Identifiers.  
# 
# * EntityMapping(MutableMapping\[str, T\], EntityCollectionBase) - Represents a dict like mapping of entities e.g. Portfolios.  
# 
# Collections of entities could be managed reasonable easily with a simple list/dict but this would not support class methods
# However, since their value is not as great as other base classes they attempt to work interchangeably with list/tuple etc.
# 

# ## EnumBase
# 
# Provides a common base for defining enumerations. Create a sample here for following examples.  
# The EnumBase class allows case insensitive initialization and will serialize to JSON (required for sending to requests) though this should not be required.



from axiomapy.entitybase import EnumBase

class SampleEnum(EnumBase):
    Value1 = "Value1"
    Value2 = "Value2"




enum = SampleEnum('Value1')
enum = SampleEnum('value1')
enum = SampleEnum('VALUE1')

# access the value
enum.value




# The enum class does not serialize to json. The EnumBase is a subclass of String, so it will serialize json.
# Since the enum will be identified and converted explicitly this should be unnecessary.
import json
test = {"value": enum}
str_test = json.dumps(test)
str_test


# ## EntityBase
# 
# Used in the representation of an API model.  
# Rules for subclassing:
# * The model is reflected by the properties.  
# * Type hints on the property help the class serialize properties correctly.
# * All access to the datamodel must be managed through the class properties.
# * All properties must be able to accept None (or the default value in the __init__ function if not None)
# * Decorators on the properties enable extra hints for serialization to be passed from the model class.
# 
# 
# Create a sample class with properties of various types with the exception of those of type common base:
# 



from axiomapy.entitybase import EntityBase, camel_case_translate, do_not_clone, do_not_serialise, get_enum_value
from axiomapy.utils import date_arg_fmt, date_arg_parse
from typing import Union, List
from datetime import datetime, date


sample_entity_dict = {
    "id":0,
    "date_field_str": "2020-05-10",
    "date_field_date":"2020-05-10",
    "date_field_datetime":"2020-05-10T00:00:00",
    "enum_field":"value1",
    "not_serialize_field":"Apples"

}


class SampleEntity(EntityBase):
    @camel_case_translate
    def __init__(
        self, 
        id_: int, 
        date_field_str: Union[datetime, str]=None,
        date_field_date: Union[datetime, date, str]=None,
        date_field_datetime: Union[datetime, str]=None,
        enum_field: Union[SampleEnum, str]=None,  
        not_serialize_field: str = None,
    ):
        super().__init__()
        self.id = id_
        self.date_field_str = date_field_str
        self.date_field_date = date_field_date
        self.date_field_datetime = date_field_datetime
        self.enum_field = enum_field
        self.not_serialize_field = not_serialize_field
    
    @property
    @do_not_clone
    def id(self) -> int:
        return self._id
    
    @id.setter
    def id(self, value: int):
        self._id = value

    @property
    def date_field_str(self) -> str:
        return self._date_field_str
    
    @date_field_str.setter
    def date_field_str(self, value: Union[datetime, str]):
        self._date_field_str = date_arg_fmt(value)

    @property
    def date_field_date(self) -> date:
        return self._date_field_date
    
    @date_field_date.setter
    def date_field_date(self, value: Union[datetime, date, str]):
        self._date_field_date = date_arg_parse(value, format="%Y-%m-%d") 

    @property
    def date_field_datetime(self) -> datetime:
        return self._date_field_datetime
    
    @date_field_datetime.setter
    def date_field_datetime(self, value: Union[datetime, str]):
        self._date_field_datetime = date_arg_parse(value, format="%Y-%m-%dT00:00:00")

    @property
    def enum_field(self) -> SampleEnum:
        return self._enum_field
    
    @enum_field.setter
    def enum_field(self, value: Union[SampleEnum, str]):
        self._enum_field = get_enum_value(SampleEnum, value)

    @property
    @do_not_serialise
    def not_serialize_field(self) -> str:
        return self._not_serialize_field
    
    @not_serialize_field.setter
    def not_serialize_field(self, value:str):
        self._not_serialize_field = value




# ### Using the samples
# 
# Create an instance directly. 
# Translation of args to the __init__ method is performed by the camel_case_translate wrapper.


# only required args:
new_sample = SampleEntity(100)
# some optional args:
another_sample = SampleEntity(50, date_field_str="2020-05-10", enum_field=SampleEnum.Value2)
# camel case args:
camel_case_sample = SampleEntity(50, enumField="value1", dateFieldDate=date.today())


# Create an instance from a dict representation:

sample_from_dict = SampleEntity.from_dict(sample_entity_dict)



# Accessing Properties
# 
# Properties can be accessed via their camelCase or snake_case names.  
# They can also accessed as dictionary keys and also with the get() method.


print(f"new_sample has id: {new_sample.id}")
print(f"another_sample has date: {another_sample.date_field_str}")
print(f"another_sample date_field_str can also be accessed via dateFieldStr {another_sample.dateFieldStr}")
print(f"entities can be accessed in snakecase or camel case like a dict {another_sample['dateFieldStr']}"
      f" and with get method {another_sample.get('dateFieldStr')}")


# #### How the Accessor Methods Work
# 
# When getting or setting a property the class property is resolved using the _translate_to_class_prop() method.
# The translation is automatic, so the logic for translation exists on the base class.
# In the templatedEntity example the translation is class-specific.



print(f"date_field_datetime maps to prop: {SampleEntity._translate_to_class_prop('date_field_datetime')}")
print(f"dateFieldDatetime maps to prop: {EntityBase._translate_to_class_prop('dateFieldDatetime')}")


# ### Clone, Update, and Replace
# 
# #### Cloning
# 
# Cloning creates a new instance based on the object being cloned.
# A clone is performed by converting to and from a dict representation and updating from the source instance.



cloned_sample = sample_from_dict.clone()
print(f"The do_not_clone decorator on the id property means cloned_sample has an id of {cloned_sample.id}")
cloned_sample_2 = sample_from_dict.clone(enum_field="value2")
print(f"overrides can be applied when cloning, cloned_sample_2 has enum_field of {cloned_sample_2.enum_field}")


# #### Update 
# 
# Can update from a dict or from an instance. Works just like the dict method update.



print(f"cloned_sample.id before update {cloned_sample.id}")
cloned_sample.update({"id":100})
print(f"cloned_sample.id before update {cloned_sample.id}")
print("The full cloned_sample after update is:\n", cloned_sample_2)
cloned_sample_2.update(sample_from_dict)
print("The full cloned_sample_2 after update is:\n", cloned_sample_2)


# #### Replace
# 
# The replace method makes the calling instance the same as the argument entity.



cloned_sample_2.replace({"id":100})

print("After replacing the sample is:\n", cloned_sample_2)


# ### Serialization
# 
# Objects are serialized to a dict object which is valid to serialize to json (e.g., by requests)
# 
# Fields marked as do_not_serialize are ignored.
# 
# The to_dict() method has the following arguments:
# translate - output camelCase (otherwise snake_case)
# cloning - actions performed as part of cloning will check for do_not_clone decorator
# ignore_none - do not serialize properties with a value of None (i.e. those not set)



sample_to_serialize = SampleEntity.from_dict(sample_entity_dict)

print(sample_to_serialize.to_dict())
# for example, without translating:
print(sample_to_serialize.to_dict(translate=False))


# #### How Serialization Works
# 
# Only class properties are serialized. 
# Specific ways to treat properties are indicated by their return-type hints on the getter.
# Additional decorators add control.
# 
# There are a number of methods on the base class that show how the process works:



# Show the properties that can be considered for serialization:
class_props = SampleEntity.class_properties()
print(f"The set of properties are: {', '.join(class_props)}")


# The type of each property can be checked and then, based on its type, an action will be taken to prepare its value for serialization:

prop_type_enums = [f"prop: {prop} has type: {SampleEntity._get_prop_type(prop)}" for prop in class_props]

print(prop_type_enums)


# The following prop types are identified:
# * EnumType - will be converted as value.value
# * IterableEnumType - for each item converted as value.value
# * CommonBaseType - will call the to_dict() method
# * IterableCommonBaseType - for each item, will call the to_dict() method
# * DictOfCommonBase - for each item in values(), will call the to_dict() method
# * Date - will format to a str as yyyy-mm-dd using date_arg_fmt(value, format="%Y-%m-%d")
# * DateTime - will format to a str as yyyy-mm-ddT00:00:00 using date_arg_fmt(value, format="%Y-%m-%dT00:00:00")
# * OtherType - will return value unchanged

# ### Nested Entities
# 
# 
# When the prop type is associated with a common base, the entity of the property will itself be serialized.



class NestedEntity(EntityBase):
    def __init(
        self,
        inner_entity: Union[SampleEntity, dict] = None,
        list_of_entities: List[Union[SampleEntity, dict]] = None
    ):
        self.inner_entity = inner_entity
        self.list_of_entities = list_of_entities

    @property
    def inner_entity(self) -> SampleEntity:
        return self._inner_entity

    @inner_entity.setter
    def inner_entity(self, value: Union[SampleEntity, dict]):
        self._inner_entity = SampleEntity.get_as_instance(value)

    @property
    def list_of_entities(self) -> List[SampleEntity]:
        return self._list_of_entities

    @list_of_entities.setter
    def list_of_entities(self, values: Union[SampleEntity, dict]):
        if values is None:
            self._list_of_entities = None
        else:
            self._list_of_entities = [SampleEntity.get_as_instance(value) for value in values]





nested_entity_dict = {
    "inner_entity": {
            "id":0,
            "date_field_str": "2020-05-10",
            "date_field_date":"2020-05-10",
            "date_field_datetime":"2020-05-10T00:00:00",
            "enum_field":"value1",
            "not_serialize_field":"Apples"
    },
    "list_of_entities": [
        {
            "id":0,
            "date_field_str": "2020-05-10",
            "date_field_date":"2020-05-10",
            "date_field_datetime":"2020-05-10T00:00:00",
            "enum_field":"value1",
            "not_serialize_field":"Apples"
        }, 
        SampleEntity(id=5, not_serialize_field="Pears")
    ]
}






nested_entity1 = NestedEntity.from_dict(nested_entity_dict)

nested_entity2 = NestedEntity(
    inner_entity=SampleEntity(
        id=100, 
        date_field_str="2020-05-10"
    ), 
    list_of_entities = [
        SampleEntity(id=99, not_serialize_field="Cheese"),
        {"id": 5}
    ]
)




from pprint import pprint
print("The nested entities behave as any other entity e.g. translating")
pprint(nested_entity1.to_dict())


# ## TemplatedEntityBase
# 
# Entities that are accessible via templates need extra logic to work as a classed-based instances.
# Instruments and Stats (View column/levels) use this base class.  
# 
# The key challenges are:   
# The data model is user-definable and does not need to follow any naming standards or conventions.  
# Types have to be determined at run time: for example, view columns.  
# The properties of interest are nested in the 'content' property but this would introduce a cumbersome 'middle' layer data model.   
# 
# 
# The TemplatedEntityBase class subclasses the EntityBase but defines class attributes for the template name and type and a custom to_dict()  
# method to serialize the properties into a 'content' property.
# 
# 



from axiomapy.entitybase import TemplatedEntityBase
from typing import List, Tuple


class SampleTemplatedEntity(TemplatedEntityBase):
    """A base class for creating templated entities
    The two properties _TEMPLATE_NAME and _TEMPLATE_MAPPING should be set in the sub
    class. The _TEMPLATE_MAPPING should be a list of tuples listing the class properties
    that are part of the content section and the mapping between the model and the
    class props within the content property like
    [(model_prop_name, class_prop_name ), ..]

    """

    _TEMPLATE_NAME: str = "Some_Template"
    _TEMPLATE_MAPPING: List[Tuple[str, str]] = [
        ("Name", "name"),
        ("template prop name", "class_prop_name") 
    ]

    def __init__(self, name: str, class_prop_value: str):
        super().__init__()
        self.name = name
        self.class_prop_name = class_prop_value

    @property
    def class_prop_name(self,) -> str:
        return self._class_prop_name

    @class_prop_name.setter
    def class_prop_name(self, value: str):
        self._class_prop_name = value




entity_def = {
  "templateName": "Some_Template",
  "content": {
    "Name": "Instance Name",
    "template prop name": "prop value",
  }
}

# the content properties are passed through
entity = SampleTemplatedEntity.from_dict(entity_def)

# they can be accessed directly in either class or data model name
entity.class_prop_name = "another value"
entity['template prop name'] = "different value"

# can also access content
content = entity.content

# When serializing, the properties are hidden at the class level 
# and exposed under content.
entity.to_dict()


# As the templated entity defines the template and therefore the data model, an attempt to initialize with a different template name will fail.
# 



entity_def['templateName'] = "A different template name"
try:
    entity2 = SampleTemplatedEntity.from_dict(entity_def)
except ValueError as e:
    print(f"Exception:\n{e}")


# For the scope of instruments, the template type can be considered to be known via the user.
# In the case of view column stats, an unknown collection of stat templates may be associated with the view.
# Therefore, two distinct classes help create instances from dictionary. 
# * A generic stat exists in which the template name and content properties are set at run time. It allows property access but no intelligence.
# * A StatFactory is used to create a relevant instance based on the template name in the dict definition and will return a generic stat if required.
# 
# 
# 
# 

# ## Generic Collections - Mapping and List
# 
# Some of the models define collections of entities: Portfolios, Positions, StatisticDefintions, Identifiers etc.
# 
# While lists of entities are equally supported, having collection-type base classes offers the opportunity to add some contextual methods.
# The primary benefit is to provide a to_dict and clone method directly (rather than iterating and applying on each entity) subclasses of CommonBase.
# A secondary benefit is specifically for mapping-type collections to offer the ability to reflect the application's mapping logic.
# As an example, AnalysisDefinitions have keys on a tuple of name, owner and team. Portfolios have keys on Name.
# 
# (see also [https://docs.python.org/3/library/collections.abc.html])
# 
# Collections can receive dictionary or classes of the member instances.
# 
# 
# ### MutableSequence
# 
# Lists of entities that do not map to an identifier or a 'key'. Examples of these are Identifiers, Qualifiers.
# 
# 
# ### MutableMapping
# 
# A mapping (dict) type for entities that can be uniquely identified by some key e.g. Portfolios (name), AnalsysisDefinitions(name, owner, team), etc.. 
# The subclass defines how to create a unique key from the entity instance.
# 
# 



from axiomapy.entitybase import EntitySequence, EntityMapping
from typing import Union, Iterable




class SampleEntityList(EntitySequence[SampleEntity]):
    def __init__(self, entities: Iterable[Union[SampleEntity, dict]]=[]):
        super().__init__(
            (SampleEntity.get_as_instance(i) for i in self._get_as_iter(entities)),
            SampleEntity,
        )










class SampleEntityMapping(EntityMapping[SampleEntity]):
    def __init__(self, entities: Iterable[Union[SampleEntity, dict]]=[]):
        super().__init__(
            (self._make_key(i) for i in entities),
            (SampleEntity.get_as_instance(i) for i in entities),
            SampleEntity,
        )

    def _make_key(self, entity):
        return entity.get("id")


# ### Populating the collections  
# 
# The collections are populated from iterables of instances or dictionary representations.  
# In the example below, the mapping contains only two entries as it is keyed on the id and two entities have an id of 0.



sample_entities = [
    {
    "id":0,
    "date_field_str": "2020-05-10",
    "date_field_date":"2020-05-10",
    "date_field_datetime":"2020-05-10T00:00:00",
    "enum_field":"value1",
    "not_serialize_field":"Apples"

},
{
    "id":0,
    "date_field_str": "2020-05-10",
    "date_field_date":"2020-05-10",
    "date_field_datetime":"2020-05-10T00:00:00",
    "enum_field":"value1",
    "not_serialize_field":"Apples"

},
SampleEntity(id_=3)



]




list_of_entities = SampleEntityList(sample_entities)
print(f"There are {len(list_of_entities)} in the sequence.")

map_of_entities = SampleEntityMapping(sample_entities)
print(f"There are {len(map_of_entities)} in the sequence.")




pprint(map_of_entities.to_dict())






