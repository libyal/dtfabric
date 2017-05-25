# -*- coding: utf-8 -*-
"""Data type definitions."""

import abc

from dtfabric import definitions

# TODO: BooleanDefinition allow to set false_value to None in definition.


class DataTypeDefinition(object):
  """Data type definition interface.

  Attributes:
    aliases (list[str]): aliases.
    byte_order (str): byte-order the data type.
    description (str): description.
    name (str): name.
    urls (list[str]): URLs.
  """

  TYPE_INDICATOR = None

  _IS_COMPOSITE = False

  def __init__(self, name, aliases=None, description=None, urls=None):
    """Initializes a data type definition.

    Args:
      name (str): name.
      aliases (Optional[list[str]]): aliases.
      description (Optional[str]): description.
      urls (Optional[list[str]]): URLs.
    """
    super(DataTypeDefinition, self).__init__()
    self.aliases = aliases or []
    self.description = description
    self.name = name
    self.urls = urls

  @abc.abstractmethod
  def GetByteSize(self):
    """Retrieves the byte size of the data type definition.

    Returns:
      int: data type size in bytes or None if size cannot be determined.
    """

  def IsComposite(self):
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

  def __init__(self, name, aliases=None, description=None, urls=None):
    """Initializes a storage data type definition.

    Args:
      name (str): name.
      aliases (Optional[list[str]]): aliases.
      description (Optional[str]): description.
      urls (Optional[list[str]]): URLs.
    """
    super(StorageDataTypeDefinition, self).__init__(
        name, aliases=aliases, description=description, urls=urls)
    self.byte_order = definitions.BYTE_ORDER_NATIVE

  @abc.abstractmethod
  def GetByteSize(self):
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

  def __init__(self, name, aliases=None, description=None, urls=None):
    """Initializes a fixed-size data type definition.

    Args:
      name (str): name.
      aliases (Optional[list[str]]): aliases.
      description (Optional[str]): description.
      urls (Optional[list[str]]): URLs.
    """
    super(FixedSizeDataTypeDefinition, self).__init__(
        name, aliases=aliases, description=description, urls=urls)
    self.size = definitions.SIZE_NATIVE
    self.units = u'bytes'

  def GetByteSize(self):
    """Retrieves the byte size of the data type definition.

    Returns:
      int: data type size in bytes or None if size cannot be determined.
    """
    if self.size != definitions.SIZE_NATIVE and self.units == u'bytes':
      return self.size


class BooleanDefinition(FixedSizeDataTypeDefinition):
  """Boolean data type definition.

  Attributes:
    false_value (int): value of False, None represents any value except that
      defined by true_value.
    true_value (int): value of True, None represents any value except that
      defined by false_value.
  """

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_BOOLEAN

  def __init__(self, name, aliases=None, description=None, urls=None):
    """Initializes a boolean data type definition.

    Args:
      name (str): name.
      aliases (Optional[list[str]]): aliases.
      description (Optional[str]): description.
      urls (Optional[list[str]]): URLs.
    """
    super(BooleanDefinition, self).__init__(
        name, aliases=aliases, description=description, urls=urls)
    self.false_value = 0
    self.true_value = None


class CharacterDefinition(FixedSizeDataTypeDefinition):
  """Character data type definition."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_CHARACTER


class FloatingPointDefinition(FixedSizeDataTypeDefinition):
  """Floating point data type definition."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_FLOATING_POINT


class IntegerDefinition(FixedSizeDataTypeDefinition):
  """Integer data type definition.

  Attributes:
    format (str): format of the data type.
  """

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_INTEGER

  def __init__(self, name, aliases=None, description=None, urls=None):
    """Initializes an integer data type definition.

    Args:
      name (str): name.
      aliases (Optional[list[str]]): aliases.
      description (Optional[str]): description.
      urls (Optional[list[str]]): URLs.
    """
    super(IntegerDefinition, self).__init__(
        name, aliases=aliases, description=description, urls=urls)
    self.format = definitions.FORMAT_SIGNED


class UUIDDefinition(FixedSizeDataTypeDefinition):
  """UUID (or GUID) data type definition."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_UUID

  _IS_COMPOSITE = True

  def __init__(self, name, aliases=None, description=None, urls=None):
    """Initializes an UUID data type definition.

    Args:
      name (str): name.
      aliases (Optional[list[str]]): aliases.
      description (Optional[str]): description.
      urls (Optional[list[str]]): URLs.
    """
    super(UUIDDefinition, self).__init__(
        name, aliases=aliases, description=description, urls=urls)
    self.size = 16


class ElementSequenceDataTypeDefinition(StorageDataTypeDefinition):
  """Element sequence data type definition.

  Attributes:
    elements_data_size (int): data size of the sequence elements.
    elements_data_size_expression (str): expression to determine the data
        size of the sequenc eelements.
    element_data_type (str): name of the sequence element data type.
    element_data_type_definition (DataTypeDefinition): sequence element
        data type definition.
    elements_terminator (int): element value that indicates the end-of-sequence.
    number_of_elements (int): number of sequence elements.
    number_of_elements_expression (str): expression to determine the number
        of sequence elements.
  """

  _IS_COMPOSITE = True

  def __init__(
      self, name, data_type_definition, aliases=None, data_type=None,
      description=None, urls=None):
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
    self.byte_order = getattr(
        data_type_definition, u'byte_order', definitions.BYTE_ORDER_NATIVE)
    self.elements_data_size = None
    self.elements_data_size_expression = None
    self.element_data_type = data_type
    self.element_data_type_definition = data_type_definition
    self.elements_terminator = None
    self.number_of_elements = None
    self.number_of_elements_expression = None

  def GetByteSize(self):
    """Retrieves the byte size of the data type definition.

    Returns:
      int: data type size in bytes or None if size cannot be determined.
    """
    if self.element_data_type_definition:
      if self.elements_data_size:
        return self.elements_data_size

      if self.number_of_elements:
        element_byte_size = self.element_data_type_definition.GetByteSize()
        if element_byte_size:
          return element_byte_size * self.number_of_elements


class SequenceDefinition(ElementSequenceDataTypeDefinition):
  """Sequence data type definition."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_SEQUENCE


class StreamDefinition(ElementSequenceDataTypeDefinition):
  """Stream data type definition."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_STREAM


class StringDefinition(ElementSequenceDataTypeDefinition):
  """String data type definition.

  Attributes:
    encoding (str): string encoding.
  """

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_STRING

  def __init__(
      self, name, data_type_definition, aliases=None, data_type=None,
      description=None, urls=None):
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
    self.encoding = u'ascii'


class DataTypeDefinitionWithMembers(StorageDataTypeDefinition):
  """Data type definition with members.

  Attributes:
    members (list[DataTypeDefinition]): members.
  """

  _IS_COMPOSITE = True

  def __init__(self, name, aliases=None, description=None, urls=None):
    """Initializes a data type definition.

    Args:
      name (str): name.
      aliases (Optional[list[str]]): aliases.
      description (Optional[str]): description.
      urls (Optional[list[str]]): URLs.
    """
    super(DataTypeDefinitionWithMembers, self).__init__(
        name, aliases=aliases, description=description, urls=urls)
    self._byte_size = None
    self.members = []

  def AddMemberDefinition(self, member_definition):
    """Adds a structure member definition.

    Args:
      member_definition (DataTypeDefinition): structure member data type
          definition.
    """
    self._byte_size = None
    self.members.append(member_definition)

  @abc.abstractmethod
  def GetByteSize(self):
    """Retrieves the byte size of the data type definition.

    Returns:
      int: data type size in bytes or None if size cannot be determined.
    """


class MemberDataTypeDefinition(StorageDataTypeDefinition):
  """Member data type definition.

  Attributes:
    member_data_type (str): member data type.
    member_data_type_definition (DataTypeDefinition): member data type
        definition.
  """

  def __init__(
      self, name, data_type_definition, aliases=None, data_type=None,
      description=None, urls=None):
    """Initializes a member data type definition.

    Args:
      name (str): name.
      data_type_definition (DataTypeDefinition): member data type definition.
      aliases (Optional[list[str]]): aliases.
      data_type (Optional[str]): member data type.
      description (Optional[str]): description.
      urls (Optional[list[str]]): URLs.
    """
    super(MemberDataTypeDefinition, self).__init__(
        name, aliases=aliases, description=description, urls=urls)
    self.byte_order = getattr(
        data_type_definition, u'byte_order', definitions.BYTE_ORDER_NATIVE)
    self.member_data_type = data_type
    self.member_data_type_definition = data_type_definition

  def GetByteSize(self):
    """Retrieves the byte size of the data type definition.

    Returns:
      int: data type size in bytes or None if size cannot be determined.
    """
    if self.member_data_type_definition:
      return self.member_data_type_definition.GetByteSize()

  def IsComposite(self):
    """Determines if the data type is composite.

    A composite data type consists of other data types.

    Returns:
      bool: True if the data type is composite, False otherwise.
    """
    return (self.member_data_type_definition and
            self.member_data_type_definition.IsComposite())


class StructureDefinition(DataTypeDefinitionWithMembers):
  """Structure data type definition."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_STRUCTURE

  def GetByteSize(self):
    """Retrieves the byte size of the data type definition.

    Returns:
      int: data type size in bytes or None if size cannot be determined.
    """
    if self._byte_size is None and self.members:
      self._byte_size = 0
      for member_definition in self.members:
        byte_size = member_definition.GetByteSize()
        if byte_size is None:
          self._byte_size = None
          break

        self._byte_size += byte_size

    return self._byte_size


class UnionDefinition(DataTypeDefinitionWithMembers):
  """Union data type definition."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_UNION

  def GetByteSize(self):
    """Retrieves the byte size of the data type definition.

    Returns:
      int: data type size in bytes or None if size cannot be determined.
    """
    if self._byte_size is None and self.members:
      self._byte_size = 0
      for member_definition in self.members:
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

  def GetByteSize(self):
    """Retrieves the byte size of the data type definition.

    Returns:
      int: data type size in bytes or None if size cannot be determined.
    """
    return


class ConstantDefinition(SemanticDataTypeDefinition):
  """Constant data type definition.

  Attributes:
    value (int): constant value.
  """

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_CONSTANT

  def __init__(self, name, aliases=None, description=None, urls=None):
    """Initializes an enumeration data type definition.

    Args:
      name (str): name.
      aliases (Optional[list[str]]): aliases.
      description (Optional[str]): description.
      urls (Optional[list[str]]): URLs.
    """
    super(ConstantDefinition, self).__init__(
        name, aliases=aliases, description=description, urls=urls)
    self.value = None


class EnumerationValue(object):
  """Enumeration value.

  Attributes:
    aliases (list[str]): aliases.
    description (str): description.
    name (str): name.
    number (int): number.
  """

  def __init__(self, name, number, aliases=None, description=None):
    """Initializes an enumeration value.

    Args:
      name (str): name.
      number (int): number.
      aliases (Optional[list[str]]): aliases.
      description (Optional[str]): description.
    """
    super(EnumerationValue, self).__init__()
    self.aliases = aliases or []
    self.description = description
    self.name = name
    self.number = number


class EnumerationDefinition(SemanticDataTypeDefinition):
  """Enumeration data type definition.

  Attributes:
    values_per_alias (dict[str, EnumerationValue]): enumeration values per
        alias.
    values_per_name (dict[str, EnumerationValue]): enumeration values per name.
    values_per_number (dict[str, EnumerationValue]): enumeration values per
        number.
    values(list[EnumerationValue]): enumeration values.
  """

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_ENUMERATION

  def __init__(self, name, aliases=None, description=None, urls=None):
    """Initializes an enumeration data type definition.

    Args:
      name (str): name.
      aliases (Optional[list[str]]): aliases.
      description (Optional[str]): description.
      urls (Optional[list[str]]): URLs.
    """
    super(EnumerationDefinition, self).__init__(
        name, aliases=aliases, description=description, urls=urls)
    self.values = []
    self.values_per_alias = {}
    self.values_per_name = {}
    self.values_per_number = {}

  def AddValue(self, name, number, aliases=None, description=None):
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
      raise KeyError(u'Value with name: {0:s} already exists.'.format(name))

    if number in self.values_per_number:
      raise KeyError(u'Value with number: {0!s} already exists.'.format(number))

    for alias in aliases or []:
      if alias in self.values_per_alias:
        raise KeyError(u'Value with alias: {0:s} already exists.'.format(alias))

    enumeration_value = EnumerationValue(
        name, number, aliases=aliases, description=description)

    self.values.append(enumeration_value)
    self.values_per_name[name] = enumeration_value
    self.values_per_number[number] = enumeration_value

    for alias in aliases or []:
      self.values_per_alias[alias] = enumeration_value


class LayoutDataTypeDefinition(DataTypeDefinition):
  """Layout data type definition interface."""

  _IS_COMPOSITE = True

  def GetByteSize(self):
    """Retrieves the byte size of the data type definition.

    Returns:
      int: data type size in bytes or None if size cannot be determined.
    """
    return


class FormatDefinition(LayoutDataTypeDefinition):
  """Data format definition.

  Attributes:
    metadata (dict[str, object]): metadata.
  """

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_FORMAT

  def __init__(self, name, aliases=None, description=None, urls=None):
    """Initializes a format data type definition.

    Args:
      name (str): name.
      aliases (Optional[list[str]]): aliases.
      description (Optional[str]): description.
      urls (Optional[list[str]]): URLs.
    """
    super(FormatDefinition, self).__init__(
        name, aliases=aliases, description=description, urls=urls)
    self.metadata = {}
