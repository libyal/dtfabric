# -*- coding: utf-8 -*-
"""Structure and type definitions."""

import abc


# TODO: complete EnumerationDefinition.
# TODO: complete FormatDefinition.
# TODO: complete SequenceStructureMemberDefinition.
# TODO: complete UnionStructureMemberDefinition.

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


class FixedSizeDataTypeDefinition(DataTypeDefinition):
  """Class that defines a fixed-size data type definition.

  Attributes:
    size (int|list[int]): size of the data type.
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

  @abc.abstractmethod
  def GetStructFormatString(self):
    """Retrieves the Python struct format string.

    Returns:
      str: format string as used by Python struct or None if format string
          cannot be determined.
    """


class BooleanDefinition(FixedSizeDataTypeDefinition):
  """Class that defines a boolean data type definition.

  Attributes:
    false_value (int): value of False, None represents any value except that
      defined by true_value.
    true_value (int): value of True, None represents any value except that
      defined by false_value.
  """

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
  """Class that defines a character data type definition."""

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
  """Class that defines an enumeration data type definition."""

  def GetStructFormatString(self):
    """Retrieves the Python struct format string.

    Returns:
      str: format string as used by Python struct or None if format string
          cannot be determined.
    """
    return


class FloatingPointDefinition(FixedSizeDataTypeDefinition):
  """Class that defines a floating point data type definition."""

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
  """Class that defines a data format definition."""

  def GetStructFormatString(self):
    """Retrieves the Python struct format string.

    Returns:
      str: format string as used by Python struct or None if format string
          cannot be determined.
    """
    return


class IntegerDefinition(FixedSizeDataTypeDefinition):
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
          break

        member_format_strings.append(member_format_string)

      self._format_string = u''.join(member_format_strings)

    return self._format_string


class StructureMemberDefinition(object):
  """Class that defines a structure data type member definition.

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
  """Class that defines a sequence structure data type member definition.

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
  """Class that defines an UUID (or GUID) data type definition."""

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
    return u'IHH2B6B'
