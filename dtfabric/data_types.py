# -*- coding: utf-8 -*-
"""Data type definitions."""

import abc
import collections
import typing

from typing import Dict, List, Optional, Union  # pylint: disable=unused-import

from dtfabric import definitions


class DataTypeDefinition(object):
  """Data type definition interface.

  Attributes:
    aliases (list[str]): aliases.
    byte_order (str): byte-order the data type.
    description (str): description.
    name (str): name.
    urls (list[str]): URLs.
  """

  # Note that redundant-returns-doc is broken for pylint 1.7.x for abstract
  # methods.
  # pylint: disable=redundant-returns-doc

  TYPE_INDICATOR: 'Union[str, None]' = None

  _IS_COMPOSITE: 'bool' = False

  def __init__(
      self, name: 'str', aliases: 'Optional[List[str]]' = None,
      description: 'Optional[str]' = None,
      urls: 'Optional[List[str]]' = None) -> 'None':
    """Initializes a data type definition.

    Args:
      name (str): name.
      aliases (Optional[list[str]]): aliases.
      description (Optional[str]): description.
      urls (Optional[list[str]]): URLs.
    """
    super(DataTypeDefinition, self).__init__()
    self.aliases: 'List[str]' = aliases or []
    self.description: 'Union[str, None]' = description
    self.name: 'str' = name
    self.urls: 'Union[List[str], None]' = urls

  @abc.abstractmethod
  def GetByteSize(self) -> 'Union[int, None]':
    """Retrieves the byte size of the data type definition.

    Returns:
      int: data type size in bytes or None if size cannot be determined.
    """

  def IsComposite(self) -> 'bool':
    """Determines if the data type is composite.

    A composite data type consists of other data types.

    Returns:
      bool: True if the data type is composite, False otherwise.
    """
    return self._IS_COMPOSITE


class StorageDataTypeDefinition(DataTypeDefinition):
  """Storage data type definition interface.

  Attributes:
    byte_order (str): byte-order the data type.
  """

  # Note that redundant-returns-doc is broken for pylint 1.7.x for abstract
  # methods.
  # pylint: disable=redundant-returns-doc

  def __init__(
      self, name: 'str', aliases: 'Optional[List[str]]' = None,
      description: 'Optional[str]' = None,
      urls: 'Optional[List[str]]' = None) -> 'None':
    """Initializes a storage data type definition.

    Args:
      name (str): name.
      aliases (Optional[list[str]]): aliases.
      description (Optional[str]): description.
      urls (Optional[list[str]]): URLs.
    """
    super(StorageDataTypeDefinition, self).__init__(
        name, aliases=aliases, description=description, urls=urls)
    self.byte_order: 'str' = definitions.BYTE_ORDER_NATIVE

  @abc.abstractmethod
  def GetByteSize(self) -> 'Union[int, None]':
    """Retrieves the byte size of the data type definition.

    Returns:
      int: data type size in bytes or None if size cannot be determined.
    """


class FixedSizeDataTypeDefinition(StorageDataTypeDefinition):
  """Fixed-size data type definition.

  Attributes:
    size (int|str): size of the data type or SIZE_NATIVE.
    units (str): units of the size of the data type.
  """

  def __init__(
      self, name: 'str', aliases: 'Optional[List[str]]' = None,
      description: 'Optional[str]' = None,
      urls: 'Optional[List[str]]' = None) -> 'None':
    """Initializes a fixed-size data type definition.

    Args:
      name (str): name.
      aliases (Optional[list[str]]): aliases.
      description (Optional[str]): description.
      urls (Optional[list[str]]): URLs.
    """
    super(FixedSizeDataTypeDefinition, self).__init__(
        name, aliases=aliases, description=description, urls=urls)
    self.size: 'Union[int, str]' = definitions.SIZE_NATIVE
    self.units: 'str' = 'bytes'

  def GetByteSize(self) -> 'Union[int, None]':
    """Retrieves the byte size of the data type definition.

    Returns:
      int: data type size in bytes or None if size cannot be determined.
    """
    if self.size == definitions.SIZE_NATIVE or self.units != 'bytes':
      return None

    return typing.cast('Union[int, None]', self.size)


class BooleanDefinition(FixedSizeDataTypeDefinition):
  """Boolean data type definition.

  Attributes:
    false_value (int): value of False, None represents any value except that
      defined by true_value.
    true_value (int): value of True, None represents any value except that
      defined by false_value.
  """

  TYPE_INDICATOR: 'Union[str, None]' = definitions.TYPE_INDICATOR_BOOLEAN

  def __init__(
      self, name: 'str', aliases: 'Optional[List[str]]' = None,
      description: 'Optional[str]' = None, false_value: 'int' = 0,
      urls: 'Optional[List[str]]' = None) -> 'None':
    """Initializes a boolean data type definition.

    Args:
      name (str): name.
      aliases (Optional[list[str]]): aliases.
      description (Optional[str]): description.
      false_value (Optional[int]): value that represents false.
      urls (Optional[list[str]]): URLs.
    """
    super(BooleanDefinition, self).__init__(
        name, aliases=aliases, description=description, urls=urls)
    self.false_value: 'Union[int, None]' = false_value
    self.true_value: 'Union[int, None]' = None


class CharacterDefinition(FixedSizeDataTypeDefinition):
  """Character data type definition."""

  TYPE_INDICATOR: 'Union[str, None]' = definitions.TYPE_INDICATOR_CHARACTER


class FloatingPointDefinition(FixedSizeDataTypeDefinition):
  """Floating point data type definition."""

  TYPE_INDICATOR: 'Union[str, None]' = (
      definitions.TYPE_INDICATOR_FLOATING_POINT)


class IntegerDefinition(FixedSizeDataTypeDefinition):
  """Integer data type definition.

  Attributes:
    format (str): format of the data type.
    maximum_value (int): maximum allowed value of the integer data type.
    minimum_value (int): minimum allowed value of the integer data type.
  """

  TYPE_INDICATOR: 'Union[str, None]' = definitions.TYPE_INDICATOR_INTEGER

  def __init__(
      self, name: 'str', aliases: 'Optional[List[str]]' = None,
      description: 'Optional[str]' = None,
      maximum_value: 'Optional[int]' = None,
      minimum_value: 'Optional[int]' = None,
      urls: 'Optional[List[str]]' = None) -> 'None':
    """Initializes an integer data type definition.

    Args:
      name (str): name.
      aliases (Optional[list[str]]): aliases.
      description (Optional[str]): description.
      maximum_value (Optional[int]): maximum allowed value of the integer
          data type.
      minimum_value (Optional[int]): minimum allowed value of the integer
          data type.
      urls (Optional[list[str]]): URLs.
    """
    super(IntegerDefinition, self).__init__(
        name, aliases=aliases, description=description, urls=urls)
    self.format: 'str' = definitions.FORMAT_SIGNED
    self.maximum_value: 'Union[int, None]' = maximum_value
    self.minimum_value: 'Union[int, None]' = minimum_value


class UUIDDefinition(FixedSizeDataTypeDefinition):
  """UUID (or GUID) data type definition."""

  TYPE_INDICATOR: 'Union[str, None]' = definitions.TYPE_INDICATOR_UUID

  _IS_COMPOSITE: 'bool' = True

  def __init__(
      self, name: 'str', aliases: 'Optional[List[str]]' = None,
      description: 'Optional[str]' = None,
      urls: 'Optional[List[str]]' = None) -> 'None':
    """Initializes an UUID data type definition.

    Args:
      name (str): name.
      aliases (Optional[list[str]]): aliases.
      description (Optional[str]): description.
      urls (Optional[list[str]]): URLs.
    """
    super(UUIDDefinition, self).__init__(
        name, aliases=aliases, description=description, urls=urls)
    self.size: 'Union[int, str]' = 16


class PaddingDefinition(StorageDataTypeDefinition):
  """Padding data type definition.

  Attributes:
    alignment_size (int): alignment size.
  """

  # Note that redundant-returns-doc is broken for pylint 1.7.x for abstract
  # methods.
  # pylint: disable=redundant-returns-doc

  TYPE_INDICATOR: 'Union[str, None]' = definitions.TYPE_INDICATOR_PADDING

  def __init__(
      self, name: 'str', aliases: 'Optional[List[str]]' = None,
      alignment_size: 'Optional[int]' = None,
      description: 'Optional[str]' = None,
      urls: 'Optional[List[str]]' = None) -> 'None':
    """Initializes a padding data type definition.

    Args:
      name (str): name.
      aliases (Optional[list[str]]): aliases.
      alignment_size (Optional[int]): alignment size.
      description (Optional[str]): description.
      urls (Optional[list[str]]): URLs.
    """
    super(PaddingDefinition, self).__init__(
        name, aliases=aliases, description=description, urls=urls)
    self.alignment_size: 'Union[int, None]' = alignment_size

  def GetByteSize(self) -> 'Union[int, None]':
    """Retrieves the byte size of the data type definition.

    Returns:
      int: data type size in bytes or None if size cannot be determined.
    """
    return None


class ElementSequenceDataTypeDefinition(StorageDataTypeDefinition):
  """Element sequence data type definition.

  Attributes:
    elements_data_size (int): data size of the sequence elements.
    elements_data_size_expression (str): expression to determine the data
        size of the sequence elements.
    element_data_type (str): name of the sequence element data type.
    element_data_type_definition (DataTypeDefinition): sequence element
        data type definition.
    elements_terminator (bytes|int): element value that indicates the
        end-of-sequence.
    number_of_elements (int): number of sequence elements.
    number_of_elements_expression (str): expression to determine the number
        of sequence elements.
  """

  _IS_COMPOSITE: 'bool' = True

  def __init__(
      self, name: 'str', data_type_definition: 'DataTypeDefinition',
      aliases: 'Optional[List[str]]' = None,
      data_type: 'Optional[str]' = None,
      description: 'Optional[str]' = None,
      urls: 'Optional[List[str]]' = None) -> 'None':
    """Initializes a sequence data type definition.

    Args:
      name (str): name.
      data_type_definition (DataTypeDefinition): sequence element data type
          definition.
      aliases (Optional[list[str]]): aliases.
      data_type (Optional[str]): name of the sequence element data type.
      description (Optional[str]): description.
      urls (Optional[list[str]]): URLs.
    """
    super(ElementSequenceDataTypeDefinition, self).__init__(
        name, aliases=aliases, description=description, urls=urls)
    self.byte_order: 'str' = getattr(
        data_type_definition, 'byte_order', definitions.BYTE_ORDER_NATIVE)
    self.elements_data_size: 'Union[int, None]' = None
    self.elements_data_size_expression: 'Union[str, None]' = None
    self.element_data_type: 'Union[str, None]' = data_type
    self.element_data_type_definition: 'DataTypeDefinition' = (
        data_type_definition)
    self.elements_terminator: 'Union[str, None]' = None
    self.number_of_elements: 'Union[int, None]' = None
    self.number_of_elements_expression: 'Union[str, None]' = None

  def GetByteSize(self) -> 'Union[int, None]':
    """Retrieves the byte size of the data type definition.

    Returns:
      int: data type size in bytes or None if size cannot be determined.
    """
    if not self.element_data_type_definition:
      return None

    if self.elements_data_size:
      return self.elements_data_size

    if not self.number_of_elements:
      return None

    element_byte_size = self.element_data_type_definition.GetByteSize()
    if not element_byte_size:
      return None

    return element_byte_size * self.number_of_elements


class SequenceDefinition(ElementSequenceDataTypeDefinition):
  """Sequence data type definition."""

  TYPE_INDICATOR: 'Union[str, None]' = definitions.TYPE_INDICATOR_SEQUENCE


class StreamDefinition(ElementSequenceDataTypeDefinition):
  """Stream data type definition."""

  TYPE_INDICATOR: 'Union[str, None]' = definitions.TYPE_INDICATOR_STREAM


class StringDefinition(ElementSequenceDataTypeDefinition):
  """String data type definition.

  Attributes:
    encoding (str): string encoding.
  """

  TYPE_INDICATOR: 'Union[str, None]' = definitions.TYPE_INDICATOR_STRING

  def __init__(
      self, name: 'str', data_type_definition: 'DataTypeDefinition',
      aliases: 'Optional[List[str]]' = None,
      data_type: 'Optional[str]' = None,
      description: 'Optional[str]' = None,
      urls: 'Optional[List[str]]' = None) -> 'None':
    """Initializes a string data type definition.

    Args:
      name (str): name.
      data_type_definition (DataTypeDefinition): string element data type
          definition.
      aliases (Optional[list[str]]): aliases.
      data_type (Optional[str]): name of the string element data type.
      description (Optional[str]): description.
      urls (Optional[list[str]]): URLs.
    """
    super(StringDefinition, self).__init__(
        name, data_type_definition, aliases=aliases, data_type=data_type,
        description=description, urls=urls)
    self.encoding: 'str' = 'ascii'


class DataTypeDefinitionWithMembers(StorageDataTypeDefinition):
  """Data type definition with members.

  Attributes:
    members (list[DataTypeDefinition]): member data type definitions.
    sections (list[MemberSectionDefinition]): member section definitions.
  """

  # Note that redundant-returns-doc is broken for pylint 1.7.x for abstract
  # methods.
  # pylint: disable=redundant-returns-doc

  _IS_COMPOSITE: 'bool' = True

  def __init__(
      self, name: 'str', aliases: 'Optional[List[str]]' = None,
      description: 'Optional[str]' = None,
      urls: 'Optional[List[str]]' = None) -> 'None':
    """Initializes a data type definition.

    Args:
      name (str): name.
      aliases (Optional[list[str]]): aliases.
      description (Optional[str]): description.
      urls (Optional[list[str]]): URLs.
    """
    super(DataTypeDefinitionWithMembers, self).__init__(
        name, aliases=aliases, description=description, urls=urls)
    self._byte_size: 'Union[int, None]' = None
    self._members_by_name: 'OrderedDict[str, DataTypeDefinition]' = (
        collections.OrderedDict())
    self.sections: 'List[MemberSectionDefinition]' = []

  @property
  def members(self) -> 'List[DataTypeDefinition]':
    """members (list[DataTypeDefinition]): member data type definitions."""
    return list(self._members_by_name.values())

  def AddMemberDefinition(
      self, member_definition: 'DataTypeDefinition') -> 'None':
    """Adds a member definition.

    Args:
      member_definition (DataTypeDefinition): member data type definition.

    Raises:
      KeyError: if a member with the name already exists.
    """
    if member_definition.name in self._members_by_name:
      raise KeyError('Member: {0:s} already set.'.format(
          member_definition.name))

    self._byte_size = None
    self._members_by_name[member_definition.name] = member_definition

    if self.sections:
      section_definition = self.sections[-1]
      section_definition.members.append(member_definition)

  def AddSectionDefinition(
      self, section_definition: 'MemberSectionDefinition') -> 'None':
    """Adds a section definition.

    Args:
      section_definition (MemberSectionDefinition): member section definition.
    """
    self.sections.append(section_definition)

  @abc.abstractmethod
  def GetByteSize(self) -> 'Union[int, None]':
    """Retrieves the byte size of the data type definition.

    Returns:
      int: data type size in bytes or None if size cannot be determined.
    """

  def GetMemberDefinitionByName(
      self, name: 'str') -> 'Union[int, DataTypeDefinition]':
    """Retrieve a specific member definition.

    Args:
      name (str): name of the member definition.

    Returns:
      DataTypeDefinition: member data type definition or None if not available.
    """
    return self._members_by_name.get(name, None)


class MemberDataTypeDefinition(StorageDataTypeDefinition):
  """Member data type definition.

  Attributes:
    condition (str): condition under which the data type applies.
    member_data_type (str): member data type.
    member_data_type_definition (DataTypeDefinition): member data type
        definition.
    values (list[int|str]): supported values.
  """

  def __init__(
      self, name: 'str', data_type_definition: 'DataTypeDefinition',
      aliases: 'Optional[List[str]]' = None, condition: 'Optional[str]' = None,
      data_type: 'Optional[str]' = None, description: 'Optional[str]' = None,
      urls: 'Optional[List[str]]' = None,
      values: 'Optional[List[Union[int, str]]]' = None) -> 'None':
    """Initializes a member data type definition.

    Args:
      name (str): name.
      data_type_definition (DataTypeDefinition): member data type definition.
      aliases (Optional[list[str]]): aliases.
      condition (Optional[str]): condition under which the member is considered
          present.
      data_type (Optional[str]): member data type.
      description (Optional[str]): description.
      urls (Optional[list[str]]): URLs.
      values (Optional[list[int|str]]): supported values
          defined.
    """
    super(MemberDataTypeDefinition, self).__init__(
        name, aliases=aliases, description=description, urls=urls)
    self.byte_order: 'str' = getattr(
        data_type_definition, 'byte_order', definitions.BYTE_ORDER_NATIVE)
    self.condition: 'Union[str, None]' = condition
    self.member_data_type: 'Union[str, None]' = data_type
    self.member_data_type_definition: 'DataTypeDefinition' = (
        data_type_definition)
    self.values: 'Union[List[Union[int, str]], None]' = values

  def GetByteSize(self) -> 'Union[int, None]':
    """Retrieves the byte size of the data type definition.

    Returns:
      int: data type size in bytes or None if size cannot be determined.
    """
    if self.condition or not self.member_data_type_definition:
      return None

    return self.member_data_type_definition.GetByteSize()

  def IsComposite(self) -> 'bool':
    """Determines if the data type is composite.

    A composite data type consists of other data types.

    Returns:
      bool: True if the data type is composite, False otherwise.
    """
    return bool(self.condition) or bool(
        self.member_data_type_definition and
        self.member_data_type_definition.IsComposite())


class MemberSectionDefinition(object):
  """Member section definition.

  Attributes:
    members (list[DataTypeDefinition]): member data type definitions of
        the section.
  """

  def __init__(self, name: 'str') -> 'None':
    """Initializes a member section definition.

    Args:
      name (str): name.
    """
    super(MemberSectionDefinition, self).__init__()
    self.name: 'str' = name
    self.members: 'List[DataTypeDefinition]' = []


class StructureDefinition(DataTypeDefinitionWithMembers):
  """Structure data type definition."""

  TYPE_INDICATOR: 'Union[str, None]' = definitions.TYPE_INDICATOR_STRUCTURE

  def GetByteSize(self) -> 'Union[int, None]':
    """Retrieves the byte size of the data type definition.

    Returns:
      int: data type size in bytes or None if size cannot be determined.
    """
    if self._byte_size is None and self._members_by_name:
      self._byte_size = 0
      for member_definition in self._members_by_name.values():
        if (not isinstance(member_definition, PaddingDefinition) or
            not member_definition.alignment_size):
          byte_size = member_definition.GetByteSize()
          if byte_size is None:
            self._byte_size = None
            break

        else:
          _, byte_size = divmod(
              self._byte_size, member_definition.alignment_size)
          if byte_size > 0:
            byte_size = member_definition.alignment_size - byte_size

        self._byte_size += byte_size

    return self._byte_size


class UnionDefinition(DataTypeDefinitionWithMembers):
  """Union data type definition."""

  TYPE_INDICATOR: 'Union[str, None]' = definitions.TYPE_INDICATOR_UNION

  def GetByteSize(self) -> 'Union[int, None]':
    """Retrieves the byte size of the data type definition.

    Returns:
      int: data type size in bytes or None if size cannot be determined.
    """
    if self._byte_size is None and self._members_by_name:
      self._byte_size = 0
      for member_definition in self._members_by_name.values():
        byte_size = member_definition.GetByteSize()
        if byte_size is None:
          self._byte_size = None
          break

        self._byte_size = max(self._byte_size, byte_size)

    return self._byte_size


class SemanticDataTypeDefinition(DataTypeDefinition):
  """Semantic data type definition interface.

  Attributes:
    byte_order (str): byte-order the data type.
  """

  # Note that redundant-returns-doc is broken for pylint 1.7.x for abstract
  # methods.
  # pylint: disable=redundant-returns-doc

  def GetByteSize(self) -> 'Union[int, None]':
    """Retrieves the byte size of the data type definition.

    Returns:
      int: data type size in bytes or None if size cannot be determined.
    """
    return None


class ConstantDefinition(SemanticDataTypeDefinition):
  """Constant data type definition.

  Attributes:
    value (int): constant value.
  """

  TYPE_INDICATOR: 'Union[str, None]' = definitions.TYPE_INDICATOR_CONSTANT

  def __init__(
      self, name: 'str', aliases: 'Optional[List[str]]' = None,
      description: 'Optional[str]' = None,
      urls: 'Optional[List[str]]' = None) -> 'None':
    """Initializes an enumeration data type definition.

    Args:
      name (str): name.
      aliases (Optional[list[str]]): aliases.
      description (Optional[str]): description.
      urls (Optional[list[str]]): URLs.
    """
    super(ConstantDefinition, self).__init__(
        name, aliases=aliases, description=description, urls=urls)
    self.value: 'Union[int, None]' = None


class EnumerationValue(object):
  """Enumeration value.

  Attributes:
    aliases (list[str]): aliases.
    description (str): description.
    name (str): name.
    number (int): number.
  """

  def __init__(
      self, name: 'str', number: 'int',
      aliases: 'Optional[List[str]]' = None,
      description: 'Optional[str]' = None) -> 'None':
    """Initializes an enumeration value.

    Args:
      name (str): name.
      number (int): number.
      aliases (Optional[list[str]]): aliases.
      description (Optional[str]): description.
    """
    super(EnumerationValue, self).__init__()
    self.aliases: 'List[str]' = aliases or []
    self.description: 'Union[str, None]' = description
    self.name: 'str' = name
    self.number: 'int' = number


class EnumerationDefinition(SemanticDataTypeDefinition):
  """Enumeration data type definition.

  Attributes:
    values (list[EnumerationValue]): enumeration values.
    values_per_alias (dict[str, EnumerationValue]): enumeration values per
        alias.
    values_per_name (dict[str, EnumerationValue]): enumeration values per name.
    values_per_number (dict[int, EnumerationValue]): enumeration values per
        number.
  """

  TYPE_INDICATOR: 'Union[str, None]' = (
      definitions.TYPE_INDICATOR_ENUMERATION)

  def __init__(
      self, name: 'str', aliases: 'Optional[List[str]]' = None,
      description: 'Optional[str]' = None,
      urls: 'Optional[List[str]]' = None) -> 'None':
    """Initializes an enumeration data type definition.

    Args:
      name (str): name.
      aliases (Optional[list[str]]): aliases.
      description (Optional[str]): description.
      urls (Optional[list[str]]): URLs.
    """
    super(EnumerationDefinition, self).__init__(
        name, aliases=aliases, description=description, urls=urls)
    self.values: 'List[EnumerationValue]' = []
    self.values_per_alias: 'Dict[str, EnumerationValue]' = {}
    self.values_per_name: 'Dict[str, EnumerationValue]' = {}
    self.values_per_number: 'Dict[int, EnumerationValue]' = {}

  def AddValue(
      self, name: 'str', number: 'int', aliases: 'Optional[List[str]]' = None,
      description: 'Optional[str]' = None) -> 'None':
    """Adds an enumeration value.

    Args:
      name (str): name.
      number (int): number.
      aliases (Optional[list[str]]): aliases.
      description (Optional[str]): description.

    Raises:
      KeyError: if the enumeration value already exists.
    """
    if name in self.values_per_name:
      raise KeyError('Value with name: {0:s} already exists.'.format(name))

    if number in self.values_per_number:
      raise KeyError('Value with number: {0!s} already exists.'.format(number))

    for alias in aliases or []:
      if alias in self.values_per_alias:
        raise KeyError('Value with alias: {0:s} already exists.'.format(alias))

    enumeration_value = EnumerationValue(
        name, number, aliases=aliases, description=description)

    self.values.append(enumeration_value)
    self.values_per_name[name] = enumeration_value
    self.values_per_number[number] = enumeration_value

    for alias in aliases or []:
      self.values_per_alias[alias] = enumeration_value


class LayoutDataTypeDefinition(DataTypeDefinition):
  """Layout data type definition interface."""

  # Note that redundant-returns-doc is broken for pylint 1.7.x for abstract
  # methods.
  # pylint: disable=redundant-returns-doc

  _IS_COMPOSITE: 'bool' = True

  def GetByteSize(self) -> 'Union[int, None]':
    """Retrieves the byte size of the data type definition.

    Returns:
      int: data type size in bytes or None if size cannot be determined.
    """
    return None


class FormatDefinition(LayoutDataTypeDefinition):
  """Data format definition.

  Attributes:
    metadata (dict[str, object]): metadata.
  """

  TYPE_INDICATOR: 'Union[str, None]' = definitions.TYPE_INDICATOR_FORMAT

  def __init__(
      self, name: 'str', aliases: 'Optional[List[str]]' = None,
      description: 'Optional[str]' = None,
      urls: 'Optional[List[str]]' = None) -> 'None':
    """Initializes a format data type definition.

    Args:
      name (str): name.
      aliases (Optional[list[str]]): aliases.
      description (Optional[str]): description.
      urls (Optional[list[str]]): URLs.
    """
    super(FormatDefinition, self).__init__(
        name, aliases=aliases, description=description, urls=urls)
    self.metadata: 'Dict[str, object]' = {}


class StructureFamilyDefinition(LayoutDataTypeDefinition):
  """Structure family definition.

  Attributes:
    base (DataTypeDefinition): base data type definition.
    members (list[DataTypeDefinition]): member data type definitions.
  """

  TYPE_INDICATOR: 'Union[str, None]' = (
      definitions.TYPE_INDICATOR_STRUCTURE_FAMILY)

  def __init__(
      self, name: 'str', base_definition: 'StructureDefinition',
      aliases: 'Optional[List[str]]' = None,
      description: 'Optional[str]' = None,
      urls: 'Optional[List[str]]' = None) -> 'None':
    """Initializes a structure family data type definition.

    Args:
      name (str): name.
      base_definition (StructureDefinition): base data type definition.
      aliases (Optional[list[str]]): aliases.
      description (Optional[str]): description.
      urls (Optional[list[str]]): URLs.
    """
    super(StructureFamilyDefinition, self).__init__(
        name, aliases=aliases, description=description, urls=urls)
    self._members_by_name: 'OrderedDict[str, DataTypeDefinition]' = (
        collections.OrderedDict())
    self.base: 'Union[DataTypeDefinition, None]' = base_definition

  @property
  def members(self) -> 'List[DataTypeDefinition]':
    """members (list[DataTypeDefinition]): member data type definitions."""
    return list(self._members_by_name.values())

  def AddMemberDefinition(
      self, member_definition: 'StructureDefinition') -> 'None':
    """Adds a member definition.

    Args:
      member_definition (StructureDefinition): member data type definition.

    Raises:
      KeyError: if a member with the name already exists.
    """
    if member_definition.name in self._members_by_name:
      raise KeyError('Member: {0:s} already set.'.format(
          member_definition.name))

    self._members_by_name[member_definition.name] = member_definition

  def SetBaseDefinition(
      self, base_definition: 'StructureDefinition') -> 'None':
    """Sets a base definition.

    Args:
      base_definition (StructureDefinition): base data type definition.
    """
    self.base = base_definition


class StructureGroupDefinition(LayoutDataTypeDefinition):
  """Structure group definition.

  Attributes:
    base (DataTypeDefinition): base data type definition.
    identifier (str): name of the base structure member to identify the group
        members.
    members (list[DataTypeDefinition]): member data type definitions.
  """

  TYPE_INDICATOR: 'Union[str, None]' = (
      definitions.TYPE_INDICATOR_STRUCTURE_GROUP)

  def __init__(
      self, name: 'str', base_definition: 'StructureDefinition',
      identifier: 'str', aliases: 'Optional[List[str]]' = None,
      description: 'Optional[str]' = None,
      urls: 'Optional[List[str]]' = None) -> 'None':
    """Initializes a structure group data type definition.

    Args:
      name (str): name.
      base_definition (StructureDefinition): base data type definition.
      identifier (str): name of the base structure member to identify the group
          members.
      aliases (Optional[list[str]]): aliases.
      description (Optional[str]): description.
      urls (Optional[list[str]]): URLs.
    """
    super(StructureGroupDefinition, self).__init__(
        name, aliases=aliases, description=description, urls=urls)
    self._members_by_name: 'OrderedDict[str, DataTypeDefinition]' = (
        collections.OrderedDict())
    self.base: 'Union[DataTypeDefinition, None]' = base_definition
    self.identifier: 'Union[str, None]' = identifier

  @property
  def members(self) -> 'List[DataTypeDefinition]':
    """members (list[DataTypeDefinition]): member data type definitions."""
    return list(self._members_by_name.values())

  def AddMemberDefinition(
      self, member_definition: 'StructureDefinition') -> 'None':
    """Adds a member definition.

    Args:
      member_definition (StructureDefinition): member data type definition.

    Raises:
      KeyError: if a member with the name already exists.
    """
    if member_definition.name in self._members_by_name:
      raise KeyError('Member: {0:s} already set.'.format(
          member_definition.name))

    self._members_by_name[member_definition.name] = member_definition
