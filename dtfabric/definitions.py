# -*- coding: utf-8 -*-
"""Structure and type definitions."""

import abc


class DataTypeDefinition(object):
  """Class that defines the data type definition interface.

  Attributes:
    aliases (list[str]): aliases.
    description (str): description.
    name (str): name.
    urls (list[str]): URLs.
  """

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
  def GetAttributedNames(self):
    """Determines the attribute (or field) names of the data type definition.

    Returns:
      list[str]: attribute names.
    """

  @abc.abstractmethod
  def GetByteSize(self):
    """Determines the byte size of the data type definition.

    Returns:
      int: data type size in bytes or None if size cannot be determined.
    """

  @abc.abstractmethod
  def GetStructFormatString(self):
    """Retrieves the Python struct format string.

    Returns:
      str: format string as used by Python struct or None if format string
          cannot be determined.
    """


class PrimitiveDataTypeDefinition(DataTypeDefinition):
  """Class that defines a primitive data type definition.

  Attributes:
    size (int|list[int]): size of the data type.
    units (str): units of the size of the data type.
  """

  def __init__(self, name, aliases=None, description=None, urls=None):
    """Initializes a primitive data type definition.

    Args:
      name (str): name.
      aliases (Optional[list[str]]): aliases.
      description (Optional[str]): description.
      urls (Optional[list[str]]): URLs.
    """
    super(PrimitiveDataTypeDefinition, self).__init__(
        name, aliases=aliases, description=description, urls=urls)
    self.size = None
    self.units = u'bytes'

  def GetAttributedNames(self):
    """Determines the attribute (or field) names of the data type definition.

    Returns:
      list[str]: attribute names.
    """
    return [u'value']

  def GetByteSize(self):
    """Determines the byte size of the data type definition.

    Returns:
      int: data type size in bytes or None if size cannot be determined.
    """
    if self.units == u'bytes':
      return self.size


class BooleanDefinition(PrimitiveDataTypeDefinition):
  """Class that defines a boolean data type definition."""


class CharacterDefinition(PrimitiveDataTypeDefinition):
  """Class that defines a character data type definition."""


class EnumerationDefinition(DataTypeDefinition):
  """Class that defines an enumeration data type definition."""


class FloatingPointDefinition(PrimitiveDataTypeDefinition):
  """Class that defines a floating point data type definition."""


class FormatDefinition(DataTypeDefinition):
  """Class that defines a format definition."""


class IntegerDefinition(PrimitiveDataTypeDefinition):
  """Class that defines an integer data type definition.

  Attributes:
    format (str): format of the data type.
  """

  # We use 'i' here instead of 'l' because 'l' behaves architecture dependent.

  _FORMAT_STRINGS_SIGNED = {
      1: u'b',
      2: u'h',
      4: u'i',
      8: u'q',
  }

  # We use 'I' here instead of 'L' because 'L' behaves architecture dependent.

  _FORMAT_STRINGS_UNSIGNED = {
      1: u'B',
      2: u'H',
      4: u'I',
      8: u'Q',
  }

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
    self.format = u'signed'

  def GetStructFormatString(self):
    """Retrieves the Python struct format string.

    Returns:
      str: format string as used by Python struct or None if format string
          cannot be determined.
    """
    if self.format == u'unsigned':
      return self._FORMAT_STRINGS_UNSIGNED.get(self.size, None)

    return self._FORMAT_STRINGS_SIGNED.get(self.size, None)


class StructureDataTypeDefinition(DataTypeDefinition):
  """Class that defines a structure data type definition.

  Attributes:
    members (list[object]): members.
  """

  def __init__(self, name, aliases=None, description=None, urls=None):
    """Initializes a data type definition.

    Args:
      name (str): name.
      aliases (Optional[list[str]]): aliases.
      description (Optional[str]): description.
      urls (Optional[list[str]]): URLs.
    """
    super(StructureDataTypeDefinition, self).__init__(
        name, aliases=aliases, description=description, urls=urls)
    self._size = None
    self.members = []

  def GetAttributedNames(self):
    """Determines the attribute (or field) names of the data type definition.

    Returns:
      list[str]: attribute names.
    """
    # TODO: implement.

  def GetByteSize(self):
    """Determines the byte size of the data type definition.

    Returns:
      int: data type size in bytes or None if size cannot be determined.
    """
    if self._size is None and self.members:
      self._size = 0
      for struct_member in self.members:
        struct_member_size = struct_member.GetByteSize()
        if struct_member_size is None:
          self._size = None
          break

        self._size += struct_member_size

    return self._size


class StructureMemberDefinition(object):
  """Class that defines a structure data type member definition.

  Attributes:
    aliases (list[str]): aliases.
    data_type (str): data type.
    description (str): description.
    name (str): name.
  """

  def __init__(self, name, aliases=None, data_type=None, description=None):
    """Initializes a structure member definition.

    Args:
      name (str): name.
      aliases (Optional[list[str]]): aliases.
      data_type (Optional[str]): data type.
      description (Optional[str]): description.
    """
    super(StructureMemberDefinition, self).__init__()
    self._data_type_definitions_registry = None
    self.aliases = aliases or []
    self.data_type = data_type
    self.description = description
    self.name = name

  def GetByteSize(self):
    """Determines the byte size of the data type definition.

    Returns:
      int: data type size in bytes or None if size cannot be determined.
    """
    data_type_definition = (
        self._data_type_definitions_registry.GetDefinitionByName(
            self.data_type))
    if not data_type_definition:
      return

    return data_type_definition.GetByteSize()

  def SetDataTypeDefinitionsRegistry(self, data_type_definitions_registry):
    """Sets the data type definitions registry.

    Args:
      data_type_definitions_registry (DataTypeDefinitionsRegistry): data type
          definitions registry.
    """
    self._data_type_definitions_registry = data_type_definitions_registry


class SequenceStructureMemberDefinition(StructureMemberDefinition):
  """Class that defines a sequence structure data type member definition.

  Attributes:
    data_size (int): data size.
    number_of_items (int): number of items.
  """

  def __init__(
      self, name, aliases=None, data_type=None, description=None):
    """Initializes a sequence structure data type member definition.

    Args:
      name (str): name.
      aliases (Optional[list[str]]): aliases.
      data_type (Optional[str]): data type.
      description (Optional[str]): description.
    """
    super(SequenceStructureMemberDefinition, self).__init__(
        name, aliases=aliases, data_type=data_type, description=description)
    self.data_size = None
    # TODO: add expression support.
    self.number_of_items = None

  def GetByteSize(self):
    """Determines the byte size of the data type definition.

    Returns:
      int: data type size in bytes or None if size cannot be determined.
    """
    if self.data_size:
      return self.data_size

    # TODO: implement size based on expression.
    # TODO: implement size based on data type x number of items.


class UnionStructureMemberDefinition(StructureMemberDefinition):
  """Class that defines an union structure data type member definition.

  Attributes:
    members (list[object]): members.
    name (str): name.
  """

  def __init__(
      self, name, aliases=None, data_size=None, data_type=None,
      description=None):
    """Initializes an union structure data type member definition.

    Args:
      name (str): name.
      aliases (Optional[list[str]]): aliases.
      data_size (Optional[int]): data size.
      data_type (Optional[str]): data type.
      description (Optional[str]): description.
    """
    super(UnionStructureMemberDefinition, self).__init__(
        name, aliases=aliases, data_type=data_type, description=description)
    self.members = []

  def GetByteSize(self):
    """Determines the byte size of the data type definition.

    Returns:
      int: data type size in bytes or None if size cannot be determined.
    """
    # TODO: implement size based on largest member.
