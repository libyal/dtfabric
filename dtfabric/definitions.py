# -*- coding: utf-8 -*-
"""Structure and type definitions."""

import abc


# TODO: complete EnumerationDefinition.
# TODO: complete FormatDefinition.
# TODO: complete SequenceStructureMemberDefinition.
# TODO: complete UnionStructureMemberDefinition.


BYTE_ORDER_BIG_ENDIAN = u'big-endian'
BYTE_ORDER_LITTLE_ENDIAN = u'little-endian'
BYTE_ORDER_MIDDLE_ENDIAN = u'middle-endian'
BYTE_ORDER_NATIVE = u'native'

BYTE_ORDERS = frozenset([
    BYTE_ORDER_BIG_ENDIAN,
    BYTE_ORDER_LITTLE_ENDIAN,
    BYTE_ORDER_NATIVE])

TYPE_INDICATOR_BOOLEAN = u'boolean'
TYPE_INDICATOR_CHARACTER = u'character'
TYPE_INDICATOR_ENUMERATION = u'enumeration'
TYPE_INDICATOR_FLOATING_POINT = u'floating-point'
TYPE_INDICATOR_FORMAT = u'format'
TYPE_INDICATOR_INTEGER = u'integer'
TYPE_INDICATOR_STRUCTURE = u'structure'
TYPE_INDICATOR_UUID = u'uuid'

TYPE_INDICATORS = frozenset([
    TYPE_INDICATOR_BOOLEAN,
    TYPE_INDICATOR_CHARACTER,
    TYPE_INDICATOR_ENUMERATION,
    TYPE_INDICATOR_FLOATING_POINT,
    TYPE_INDICATOR_FORMAT,
    TYPE_INDICATOR_INTEGER,
    TYPE_INDICATOR_STRUCTURE,
    TYPE_INDICATOR_UUID])


class DataTypeDefinition(object):
  """Data type definition interface.

  Attributes:
    aliases (list[str]): aliases.
    description (str): description.
    name (str): name.
    urls (list[str]): URLs.
  """

  TYPE_INDICATOR = None

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


class FixedSizeDataTypeDefinition(DataTypeDefinition):
  """Fixed-size data type definition.

  Attributes:
    byte_order (str): byte-order the data type.
    size (int|list[int]): size of the data type.
    units (str): units of the size of the data type.
  """

  _BYTE_ORDER_STRINGS = {
      BYTE_ORDER_BIG_ENDIAN: u'>',
      BYTE_ORDER_LITTLE_ENDIAN: u'<',
      BYTE_ORDER_NATIVE: u'='}

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
    self.byte_order = BYTE_ORDER_NATIVE
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

  def GetStructByteOrderString(self):
    """Retrieves the Python struct format string.

    Returns:
      str: format string as used by Python struct or None if format string
          cannot be determined.
    """
    return self._BYTE_ORDER_STRINGS.get(self.byte_order, None)

  @abc.abstractmethod
  def GetStructFormatString(self):
    """Retrieves the Python struct format string.

    Returns:
      str: format string as used by Python struct or None if format string
          cannot be determined.
    """


class BooleanDefinition(FixedSizeDataTypeDefinition):
  """Boolean data type definition.

  Attributes:
    false_value (int): value of False, None represents any value except that
      defined by true_value.
    true_value (int): value of True, None represents any value except that
      defined by false_value.
  """

  TYPE_INDICATOR = TYPE_INDICATOR_BOOLEAN

  # We use 'I' here instead of 'L' because 'L' behaves architecture dependent.

  _FORMAT_STRINGS_UNSIGNED = {
      1: u'B',
      2: u'H',
      4: u'I',
  }

  def __init__(self, name, aliases=None, description=None, urls=None):
    """Initializes an integer data type definition.

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

  def GetStructFormatString(self):
    """Retrieves the Python struct format string.

    Returns:
      str: format string as used by Python struct or None if format string
          cannot be determined.
    """
    return self._FORMAT_STRINGS_UNSIGNED.get(self.size, None)


class CharacterDefinition(FixedSizeDataTypeDefinition):
  """Character data type definition."""

  TYPE_INDICATOR = TYPE_INDICATOR_CHARACTER

  # We use 'i' here instead of 'l' because 'l' behaves architecture dependent.

  _FORMAT_STRINGS = {
      1: u'b',
      2: u'h',
      4: u'i',
  }

  def GetStructFormatString(self):
    """Retrieves the Python struct format string.

    Returns:
      str: format string as used by Python struct or None if format string
          cannot be determined.
    """
    return self._FORMAT_STRINGS.get(self.size, None)


class EnumerationDefinition(FixedSizeDataTypeDefinition):
  """Enumeration data type definition."""

  TYPE_INDICATOR = TYPE_INDICATOR_ENUMERATION

  def GetStructFormatString(self):
    """Retrieves the Python struct format string.

    Returns:
      str: format string as used by Python struct or None if format string
          cannot be determined.
    """
    return


class FloatingPointDefinition(FixedSizeDataTypeDefinition):
  """Floating point data type definition."""

  TYPE_INDICATOR = TYPE_INDICATOR_FLOATING_POINT

  _FORMAT_STRINGS = {
      4: u'f',
      8: u'd',
  }

  def GetStructFormatString(self):
    """Retrieves the Python struct format string.

    Returns:
      str: format string as used by Python struct or None if format string
          cannot be determined.
    """
    return self._FORMAT_STRINGS.get(self.size, None)


class FormatDefinition(DataTypeDefinition):
  """Data format definition."""

  TYPE_INDICATOR = TYPE_INDICATOR_FORMAT

  def GetStructFormatString(self):
    """Retrieves the Python struct format string.

    Returns:
      str: format string as used by Python struct or None if format string
          cannot be determined.
    """
    return


class IntegerDefinition(FixedSizeDataTypeDefinition):
  """Integer data type definition.

  Attributes:
    format (str): format of the data type.
  """

  TYPE_INDICATOR = TYPE_INDICATOR_INTEGER

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
  """Structure data type definition.

  Attributes:
    members (list[object]): members.
  """

  TYPE_INDICATOR = TYPE_INDICATOR_STRUCTURE

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
    self._attribute_names = None
    self._byte_size = None
    self._format_string = None
    self.members = []

  def AddMemberDefinition(self, member_definition):
    """Adds structure member definition.

    Args:
      member_definition (StructureMemberDefinition): structure member
          definition.
    """
    self._attribute_names = None
    self._byte_size = None
    self._format_string = None
    self.members.append(member_definition)

  def GetAttributedNames(self):
    """Determines the attribute (or field) names of the data type definition.

    Returns:
      list[str]: attribute names.
    """
    if self._attribute_names is None:
      self._attribute_names = []
      for member_definition in self.members:
        self._attribute_names.append(member_definition.name)

    return self._attribute_names

  def GetByteSize(self):
    """Determines the byte size of the data type definition.

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

  def GetStructFormatString(self):
    """Retrieves the Python struct format string.

    Returns:
      str: format string as used by Python struct or None if format string
          cannot be determined.
    """
    if self._format_string is None and self.members:
      member_format_strings = []
      for member_definition in self.members:
        member_format_string = member_definition.GetStructFormatString()
        if member_format_string is None:
          return

        member_format_strings.append(member_format_string)

      self._format_string = u''.join(member_format_strings)

    return self._format_string


class StructureMemberDefinition(object):
  """Structure data type member definition.

  Attributes:
    aliases (list[str]): aliases.
    data_type (str): data type.
    description (str): description.
    name (str): name.
  """

  def __init__(
      self, data_type_definition, name, aliases=None, data_type=None,
      description=None):
    """Initializes a structure member definition.

    Args:
      data_type_definition (DataTypeDefinition): data type definition.
      name (str): name.
      aliases (Optional[list[str]]): aliases.
      data_type (Optional[str]): data type.
      description (Optional[str]): description.
    """
    super(StructureMemberDefinition, self).__init__()
    self._data_type_definition = data_type_definition
    self.aliases = aliases or []
    self.data_type = data_type
    self.description = description
    self.name = name

  def GetByteSize(self):
    """Determines the byte size of the data type definition.

    Returns:
      int: data type size in bytes or None if size cannot be determined.
    """
    if self._data_type_definition:
      return self._data_type_definition.GetByteSize()

  def GetStructFormatString(self):
    """Retrieves the Python struct format string.

    Returns:
      str: format string as used by Python struct or None if format string
          cannot be determined.
    """
    if self._data_type_definition:
      return self._data_type_definition.GetStructFormatString()


class SequenceStructureMemberDefinition(StructureMemberDefinition):
  """Sequence structure data type member definition.

  Attributes:
    data_size (int): data size.
    number_of_items (int): number of items.
  """

  def __init__(self, name, aliases=None, data_type=None, description=None):
    """Initializes a sequence structure data type member definition.

    Args:
      name (str): name.
      aliases (Optional[list[str]]): aliases.
      data_type (Optional[str]): data type.
      description (Optional[str]): description.
    """
    super(SequenceStructureMemberDefinition, self).__init__(
        None, name, aliases=aliases, data_type=data_type,
        description=description)
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
  """Union structure data type member definition.

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
        None, name, aliases=aliases, data_type=data_type,
        description=description)
    self.members = []

  def GetByteSize(self):
    """Determines the byte size of the data type definition.

    Returns:
      int: data type size in bytes or None if size cannot be determined.
    """
    # TODO: implement size based on largest member.


# TODO: revisit if this should this be a separate data type.

class UUIDDefinition(FixedSizeDataTypeDefinition):
  """UUID (or GUID) data type definition."""

  TYPE_INDICATOR = TYPE_INDICATOR_UUID

  def __init__(self, name, aliases=None, description=None, urls=None):
    """Initializes an integer data type definition.

    Args:
      name (str): name.
      aliases (Optional[list[str]]): aliases.
      description (Optional[str]): description.
      urls (Optional[list[str]]): URLs.
    """
    super(UUIDDefinition, self).__init__(
        name, aliases=aliases, description=description, urls=urls)
    self.size = 16

  def GetStructFormatString(self):
    """Retrieves the Python struct format string.

    Returns:
      str: format string as used by Python struct or None if format string
          cannot be determined.
    """
    return u'IHH8B'
