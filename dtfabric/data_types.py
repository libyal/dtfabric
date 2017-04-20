# -*- coding: utf-8 -*-
"""Data type definitions."""

import abc

from dtfabric import definitions

# TODO: BooleanDefinition allow to set false_value to None in definition.
# TODO: complete EnumerationDefinition.
# TODO: complete FormatDefinition.


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

  _BYTE_ORDER_STRINGS = {
      definitions.BYTE_ORDER_BIG_ENDIAN: u'>',
      definitions.BYTE_ORDER_LITTLE_ENDIAN: u'<',
      definitions.BYTE_ORDER_NATIVE: u'='}

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
    self.byte_order = definitions.BYTE_ORDER_NATIVE
    self.description = description
    self.name = name
    self.urls = urls

  @abc.abstractmethod
  def GetAttributeNames(self):
    """Determines the attribute (or field) names of the data type definition.

    Returns:
      list[str]: attribute names.
    """

  @abc.abstractmethod
  def GetByteSize(self):
    """Retrieves the byte size of the data type definition.

    Returns:
      int: data type size in bytes or None if size cannot be determined.
    """

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

  def IsComposite(self):
    """Determines if the data type is composite.

    A composite data type consists of other data types.

    Returns:
      bool: True if the data type is composite, False otherwise.
    """
    return self._IS_COMPOSITE


class FixedSizeDataTypeDefinition(DataTypeDefinition):
  """Fixed-size data type definition.

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

  def GetAttributeNames(self):
    """Determines the attribute (or field) names of the data type definition.

    Returns:
      list[str]: attribute names.
    """
    return [u'value']

  def GetByteSize(self):
    """Retrieves the byte size of the data type definition.

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
  """Boolean data type definition.

  Attributes:
    false_value (int): value of False, None represents any value except that
      defined by true_value.
    true_value (int): value of True, None represents any value except that
      defined by false_value.
  """

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_BOOLEAN

  # We use 'I' here instead of 'L' because 'L' behaves architecture dependent.

  _FORMAT_STRINGS_UNSIGNED = {
      1: u'B',
      2: u'H',
      4: u'I',
  }

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

  def GetStructFormatString(self):
    """Retrieves the Python struct format string.

    Returns:
      str: format string as used by Python struct or None if format string
          cannot be determined.
    """
    return self._FORMAT_STRINGS_UNSIGNED.get(self.size, None)


class CharacterDefinition(FixedSizeDataTypeDefinition):
  """Character data type definition."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_CHARACTER

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


class ConstantDefinition(DataTypeDefinition):
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

  def GetAttributeNames(self):
    """Determines the attribute (or field) names of the data type definition.

    Returns:
      list[str]: attribute names.
    """
    return [u'constant']

  def GetByteSize(self):
    """Retrieves the byte size of the data type definition.

    Returns:
      int: data type size in bytes or None if size cannot be determined.
    """
    return

  def GetStructFormatString(self):
    """Retrieves the Python struct format string.

    Returns:
      str: format string as used by Python struct or None if format string
          cannot be determined.
    """
    return


class EnumerationValue(object):
  """Enumeration value.

  Attributes:
    aliases (list[str]): aliases.
    description (str): description.
    name (str): name.
    value (int): value.
  """

  def __init__(self, name, value, aliases=None, description=None):
    """Initializes an enumeration value.

    Args:
      name (str): name.
      value (int): value.
      aliases (Optional[list[str]]): aliases.
      description (Optional[str]): description.
    """
    super(EnumerationValue, self).__init__()
    self.aliases = aliases or []
    self.description = description
    self.name = name
    self.value = value


class EnumerationDefinition(FixedSizeDataTypeDefinition):
  """Enumeration data type definition.

  Attributes:
    values_per_name (dict[str, EnumerationValue]): enumeration values per name.
    values(list[EnumerationValue]): enumeration values.
  """

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_ENUMERATION

  # We use 'I' here instead of 'L' because 'L' behaves architecture dependent.

  _FORMAT_STRINGS_UNSIGNED = {
      1: u'B',
      2: u'H',
      4: u'I',
  }

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
    self.values_per_name = {}

    # TODO: support lookup of enumeration value by alias.
    # TODO: support lookup of enumeration value by value.

  def AddValue(self, name, value, aliases=None, description=None):
    """Adds an enumeration value.

    Args:
      name (str): name.
      value (int): value.
      aliases (Optional[list[str]]): aliases.
      description (Optional[str]): description.

    Raises:
      KeyError: if the enumeration value already exists.
    """
    if name in self.values_per_name:
      raise KeyError(u'Value: {0:s} already exists.'.format(name))

    # TODO: check if aliases already exist.
    # TODO: check if value already exists.

    enumeration_value = EnumerationValue(
        name, value, aliases=aliases, description=description)

    self.values.append(enumeration_value)
    self.values_per_name[name] = enumeration_value

  def GetStructFormatString(self):
    """Retrieves the Python struct format string.

    Returns:
      str: format string as used by Python struct or None if format string
          cannot be determined.
    """
    return self._FORMAT_STRINGS_UNSIGNED.get(self.size, None)


class FloatingPointDefinition(FixedSizeDataTypeDefinition):
  """Floating point data type definition."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_FLOATING_POINT

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

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_FORMAT

  _IS_COMPOSITE = True

  def GetAttributeNames(self):
    """Determines the attribute (or field) names of the data type definition.

    Returns:
      list[str]: attribute names.
    """
    return []

  def GetByteSize(self):
    """Retrieves the byte size of the data type definition.

    Returns:
      int: data type size in bytes or None if size cannot be determined.
    """
    return

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

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_INTEGER

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
    self.format = definitions.FORMAT_SIGNED

  def GetStructFormatString(self):
    """Retrieves the Python struct format string.

    Returns:
      str: format string as used by Python struct or None if format string
          cannot be determined.
    """
    if self.format == definitions.FORMAT_UNSIGNED:
      return self._FORMAT_STRINGS_UNSIGNED.get(self.size, None)

    return self._FORMAT_STRINGS_SIGNED.get(self.size, None)


class SequenceDefinition(DataTypeDefinition):
  """Sequence data type definition.

  Attributes:
    element_data_type (str): name of the sequence element data type.
    element_data_type_definition (DataTypeDefinition): sequence element
        data type definition.
    number_of_elements (int): number of elements.
    number_of_elements_expression (str): expression to determine number
        of elements.
  """

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_SEQUENCE

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
    super(SequenceDefinition, self).__init__(
        name, aliases=aliases, description=description, urls=urls)
    self.byte_order = getattr(
        data_type_definition, u'byte_order', definitions.BYTE_ORDER_NATIVE)
    self.element_data_type = data_type
    self.element_data_type_definition = data_type_definition
    self.number_of_elements = None
    self.number_of_elements_expression = None

  def GetAttributeNames(self):
    """Determines the attribute (or field) names of the data type definition.

    Returns:
      list[str]: attribute names.
    """
    return [u'elements']

  def GetByteSize(self):
    """Retrieves the byte size of the data type definition.

    Returns:
      int: data type size in bytes or None if size cannot be determined.
    """
    if not self.element_data_type_definition:
      return

    if self.number_of_elements:
      element_byte_size = self.element_data_type_definition.GetByteSize()
      if element_byte_size:
        return element_byte_size * self.number_of_elements

  def GetStructByteOrderString(self):
    """Retrieves the Python struct format string.

    Returns:
      str: format string as used by Python struct or None if format string
          cannot be determined.
    """
    if self.element_data_type_definition:
      return self.element_data_type_definition.GetStructByteOrderString()

  def GetStructFormatString(self):
    """Retrieves the Python struct format string.

    Returns:
      str: format string as used by Python struct or None if format string
          cannot be determined.
    """
    if not self.element_data_type_definition:
      return

    if self.number_of_elements:
      format_string = self.element_data_type_definition.GetStructFormatString()
      if format_string:
        return u'{0:d}{1:s}'.format(self.number_of_elements, format_string)


class StreamDefinition(DataTypeDefinition):
  """Stream data type definition.

  Attributes:
    element_data_type (str): name of the stream element data type.
    element_data_type_definition (DataTypeDefinition): stream element
        data type definition.
    number_of_elements (int): number of elements.
    number_of_elements_expression (str): expression to determine number
        of elements.
  """

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_STREAM

  _IS_COMPOSITE = True

  def __init__(
      self, name, data_type_definition, aliases=None, data_type=None,
      description=None, urls=None):
    """Initializes a stream data type definition.

    Args:
      name (str): name.
      data_type_definition (DataTypeDefinition): stream element data type
          definition.
      aliases (Optional[list[str]]): aliases.
      data_type (Optional[str]): name of the stream element data type.
      description (Optional[str]): description.
      urls (Optional[list[str]]): URLs.
    """
    super(StreamDefinition, self).__init__(
        name, aliases=aliases, description=description, urls=urls)
    self.byte_order = getattr(
        data_type_definition, u'byte_order', definitions.BYTE_ORDER_NATIVE)
    self.element_data_type = data_type
    self.element_data_type_definition = data_type_definition
    self.number_of_elements = None
    self.number_of_elements_expression = None

  def GetAttributeNames(self):
    """Determines the attribute (or field) names of the data type definition.

    Returns:
      list[str]: attribute names.
    """
    return [u'elements']

  def GetByteSize(self):
    """Retrieves the byte size of the data type definition.

    Returns:
      int: data type size in bytes or None if size cannot be determined.
    """
    if not self.element_data_type_definition:
      return

    if self.number_of_elements:
      element_byte_size = self.element_data_type_definition.GetByteSize()
      if element_byte_size:
        return element_byte_size * self.number_of_elements

  def GetStructByteOrderString(self):
    """Retrieves the Python struct format string.

    Returns:
      str: format string as used by Python struct or None if format string
          cannot be determined.
    """
    if self.element_data_type_definition:
      return self.element_data_type_definition.GetStructByteOrderString()

  def GetStructFormatString(self):
    """Retrieves the Python struct format string.

    Returns:
      str: format string as used by Python struct or None if format string
          cannot be determined.
    """
    if not self.element_data_type_definition:
      return

    if self.number_of_elements:
      format_string = self.element_data_type_definition.GetStructFormatString()
      if format_string:
        return u'{0:d}{1:s}'.format(self.number_of_elements, format_string)


class StructureDefinition(DataTypeDefinition):
  """Structure data type definition.

  Attributes:
    members (list[DataTypeDefinition]): members.
  """

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_STRUCTURE

  _IS_COMPOSITE = True

  def __init__(self, name, aliases=None, description=None, urls=None):
    """Initializes a data type definition.

    Args:
      name (str): name.
      aliases (Optional[list[str]]): aliases.
      description (Optional[str]): description.
      urls (Optional[list[str]]): URLs.
    """
    super(StructureDefinition, self).__init__(
        name, aliases=aliases, description=description, urls=urls)
    self._attribute_names = None
    self._byte_size = None
    self._format_string = None
    self.members = []

  def AddMemberDefinition(self, member_definition):
    """Adds structure member definition.

    Args:
      member_definition (DataTypeDefinition): structure member data type
          definition.
    """
    self._attribute_names = None
    self._byte_size = None
    self._format_string = None
    self.members.append(member_definition)

  def GetAttributeNames(self):
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


class StructureMemberDefinition(DataTypeDefinition):
  """Structure data type member definition.

  Attributes:
    member_data_type (str): structure member data type.
    member_data_type_definition (DataTypeDefinition): structure member
        data type definition.
  """

  def __init__(
      self, name, data_type_definition, aliases=None, data_type=None,
      description=None, urls=None):
    """Initializes a structure member definition.

    Args:
      name (str): name.
      data_type_definition (DataTypeDefinition): structure member data type
          definition.
      aliases (Optional[list[str]]): aliases.
      data_type (Optional[str]): structure member data type.
      description (Optional[str]): description.
      urls (Optional[list[str]]): URLs.
    """
    super(StructureMemberDefinition, self).__init__(
        name, aliases=aliases, description=description, urls=urls)
    self.byte_order = getattr(
        data_type_definition, u'byte_order', definitions.BYTE_ORDER_NATIVE)
    self.member_data_type = data_type
    self.member_data_type_definition = data_type_definition

  def GetAttributeNames(self):
    """Determines the attribute (or field) names of the data type definition.

    Returns:
      list[str]: attribute names.
    """
    if self.member_data_type_definition:
      return self.member_data_type_definition.GetAttributeNames()

  def GetByteSize(self):
    """Retrieves the byte size of the data type definition.

    Returns:
      int: data type size in bytes or None if size cannot be determined.
    """
    if self.member_data_type_definition:
      return self.member_data_type_definition.GetByteSize()

  def GetStructFormatString(self):
    """Retrieves the Python struct format string.

    Returns:
      str: format string as used by Python struct or None if format string
          cannot be determined.
    """
    if self.member_data_type_definition:
      return self.member_data_type_definition.GetStructFormatString()

  def IsComposite(self):
    """Determines if the data type is composite.

    A composite data type consists of other data types.

    Returns:
      bool: True if the data type is composite, False otherwise.
    """
    return (self.member_data_type_definition and
            self.member_data_type_definition.IsComposite())


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

  def GetStructFormatString(self):
    """Retrieves the Python struct format string.

    Returns:
      str: format string as used by Python struct or None if format string
          cannot be determined.
    """
    return u'IHH8B'
