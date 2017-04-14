# -*- coding: utf-8 -*-
"""Run-time objects."""

import abc
import collections
import struct
import uuid

from dtfabric import definitions
from dtfabric import errors
from dtfabric import py2to3


# TODO: add ConstantMap.
# TODO: add EnumerationMap.
# TODO: add FormatMap.
# TODO: add SequenceMap.
# TODO: complete StructureMap.

class ByteStreamOperation(object):
  """Byte stream operation."""

  @abc.abstractmethod
  def ReadFrom(self, byte_stream):
    """Read values from a byte stream.

    Args:
      byte_stream (bytes): byte stream.

    Returns:
      tuple[object, ]: values copies from the byte stream.
    """


class StructOperation(ByteStreamOperation):
  """Python struct-base binary stream operation."""

  def __init__(self, format_string):
    """Initializes a Python struct-base binary stream operation.

    Args:
      format_string (str): format string as used by Python struct.

    Raises:
      FormatError: if struct format string cannot be determed from
          the data type definition.
    """
    try:
      struct_object = struct.Struct(format_string)
    except (TypeError, struct.error) as exception:
      raise errors.FormatError((
          u'Unable to create struct object from data type definition '
          u'with error: {0!s}').format(exception))

    super(StructOperation, self).__init__()
    self._struct = struct_object
    self._struct_format_string = format_string

  def ReadFrom(self, byte_stream):
    """Read values from a byte stream.

    Args:
      byte_stream (bytes): byte stream.

    Returns:
      tuple[object, ]: values copies from the byte stream.

    Raises:
      IOError: if byte stream cannot be read.
    """
    try:
      return self._struct.unpack_from(byte_stream)
    except (TypeError, struct.error) as exception:
      raise IOError(u'Unable to read byte stream with error: {0!s}'.format(
          exception))


class DataTypeMap(object):
  """Data type map."""

  def __init__(self, data_type_definition):
    """Initializes a data type map.

    Args:
      data_type_definition (DataTypeDefinition): data type definition.
    """
    super(DataTypeMap, self).__init__()
    self._data_type_definition = data_type_definition

  def GetByteSize(self):
    """Determines the byte size of the data type map.

    Returns:
      int: data map size in bytes or None if size cannot be determined.
    """
    return self._data_type_definition.GetByteSize()

  @abc.abstractmethod
  def MapByteStream(self, byte_stream):
    """Maps the data type on top of a byte stream.

    Args:
      byte_stream (bytes): byte stream.

    Returns:
      object: mapped value.

    Raises:
      MappingError: if the data type definition cannot be mapped on
          the byte stream.
    """


class FixedSizeDataTypeMap(DataTypeMap):
  """Fixed-size data type map."""

  def __init__(self, data_type_definition):
    """Initializes a data type map.

    Args:
      data_type_definition (DataTypeDefinition): data type definition.

    Raises:
      FormatError: if struct format string cannot be determed from
          the data type definition.
    """
    try:
      byte_order_string = data_type_definition.GetStructByteOrderString()
      format_string = data_type_definition.GetStructFormatString()
      format_string = u''.join([byte_order_string, format_string])
    except (AttributeError, TypeError) as exception:
      raise errors.FormatError((
          u'Unable to create struct object from data type definition '
          u'with error: {0!s}').format(exception))

    super(FixedSizeDataTypeMap, self).__init__(data_type_definition)
    self._operation = StructOperation(format_string)

  @abc.abstractmethod
  def MapByteStream(self, byte_stream):
    """Maps the data type on top of a byte stream.

    Args:
      byte_stream (bytes): byte stream.

    Returns:
      object: mapped value.

    Raises:
      MappingError: if the data type definition cannot be mapped on
          the byte stream.
    """


class BooleanMap(FixedSizeDataTypeMap):
  """Boolen data type map."""

  def __init__(self, data_type_definition):
    """Initializes a data type map.

    Args:
      data_type_definition (DataTypeDefinition): data type definition.

    Raises:
      FormatError: if struct format string cannot be determed from
          the data type definition.
    """
    if (data_type_definition.false_value is None and
        data_type_definition.true_value is None):
      raise errors.FormatError(
          u'Boolean data type has no True or False values.')

    super(BooleanMap, self).__init__(data_type_definition)

  def MapByteStream(self, byte_stream):
    """Maps the data type on top of a byte stream.

    Args:
      byte_stream (bytes): byte stream.

    Returns:
      bool: mapped value.

    Raises:
      MappingError: if the data type definition cannot be mapped on
          the byte stream.
    """
    try:
      struct_tuple = self._operation.ReadFrom(byte_stream)
      integer_value = int(*struct_tuple)

    except Exception as exception:
      raise errors.MappingError(exception)

    if self._data_type_definition.false_value == integer_value:
      return False

    if self._data_type_definition.true_value == integer_value:
      return True

    if self._data_type_definition.false_value is None:
      return False

    if self._data_type_definition.true_value is None:
      return True

    raise errors.MappingError(u'No matching True and False values')


class CharacterMap(FixedSizeDataTypeMap):
  """Character data type map."""

  def MapByteStream(self, byte_stream):
    """Maps the data type on top of a byte stream.

    Args:
      byte_stream (bytes): byte stream.

    Returns:
      str: mapped value.

    Raises:
      MappingError: if the data type definition cannot be mapped on
          the byte stream.
    """
    try:
      struct_tuple = self._operation.ReadFrom(byte_stream)
      return py2to3.UNICHR(*struct_tuple)

    except Exception as exception:
      raise errors.MappingError(exception)


class FloatingPointMap(FixedSizeDataTypeMap):
  """Floating-point data type map."""

  def MapByteStream(self, byte_stream):
    """Maps the data type on top of a byte stream.

    Args:
      byte_stream (bytes): byte stream.

    Returns:
      float: mapped value.

    Raises:
      MappingError: if the data type definition cannot be mapped on
          the byte stream.
    """
    try:
      struct_tuple = self._operation.ReadFrom(byte_stream)
      return float(*struct_tuple)

    except Exception as exception:
      raise errors.MappingError(exception)


class IntegerMap(FixedSizeDataTypeMap):
  """Integer data type map."""

  def MapByteStream(self, byte_stream):
    """Maps the data type on top of a byte stream.

    Args:
      byte_stream (bytes): byte stream.

    Returns:
      int: mapped value.

    Raises:
      MappingError: if the data type definition cannot be mapped on
          the byte stream.
    """
    try:
      struct_tuple = self._operation.ReadFrom(byte_stream)
      return int(*struct_tuple)

    except Exception as exception:
      raise errors.MappingError(exception)


class SequenceMap(DataTypeMap):
  """Sequence data type map."""

  def __init__(self, data_type_definition):
    """Initializes a sequence data type map.

    Args:
      data_type_definition (DataTypeDefinition): data type definition.

    Raises:
      FormatError: if struct format string cannot be determed from
          the data type definition.
    """
    super(SequenceMap, self).__init__(data_type_definition)
    # TODO: implement.

  def MapByteStream(self, byte_stream):
    """Maps the data type on top of a byte stream.

    Args:
      byte_stream (bytes): byte stream.

    Returns:
      collections.namedtuple: values mapped.

    Raises:
      MappingError: if the data type definition cannot be mapped on
          the byte stream.
    """
    # TODO: implement.
    return


class StructureMap(DataTypeMap):
  """Structure data type map."""

  def __init__(self, data_type_definition):
    """Initializes a structure data type map.

    Args:
      data_type_definition (DataTypeDefinition): data type definition.

    Raises:
      FormatError: if struct format string cannot be determed from
          the data type definition.
    """
    attribute_names = data_type_definition.GetAttributedNames()
    named_tuple = collections.namedtuple(
        data_type_definition.name, attribute_names)

    format_strings = self._GetStructFormatStrings(data_type_definition)
    grouped_format_strings = self._GroupFormatStrings(format_strings)

    super(StructureMap, self).__init__(data_type_definition)
    self._named_tuple = named_tuple
    self._operation = None

    if len(grouped_format_strings) == 1:
      self._operation = StructOperation(grouped_format_strings[0])

  # TODO: complete or remove
  def _GetStructFormatStringAndObject(self, data_type_definition):
    """Retrieves the struct format string and object.

    Args:
      data_type_definition (DataTypeDefinition): data type definition.

    Returns:
      tuple[str, struct.Struct]: format string as used by Python struct
          and Python struct object.

    Raises:
      FormatError: if struct format string cannot be determed from
          the data type definition.
    """
    format_strings = self._GetStructFormatStrings(data_type_definition)
    grouped_format_strings = self._GroupFormatStrings(format_strings)

    for format_string in grouped_format_strings:
      if isinstance(format_string, py2to3.STRING_TYPES):
        try:
          struct_object = struct.Struct(format_string)
        except (AttributeError, TypeError) as exception:
          raise errors.FormatError((
              u'Unable to create struct object from format string: {0:s}'
              u'with error: {1!s}').format(format_string, exception))

  def _GetStructFormatStrings(self, data_type_definition):
    """Retrieves the struct format strings.

    Args:
      data_type_definition (DataTypeDefinition): data type definition.

    Returns:
      list[str]: format strings as used by Python struct, where a instance of
          StructureMemberDefinition represents that the struct member has no
          format string.
    """
    byte_order_string = data_type_definition.GetStructByteOrderString()
    format_strings = [byte_order_string]

    for member in data_type_definition.members:
      format_string = member.GetStructFormatString()
      if not format_string:
        format_string = member

      format_strings.append(format_string)

    return format_strings

  def _GroupFormatStrings(self, format_strings):
    """Groups struct format strings.

    Args:
      format_strings (list[str]): format strings of the struct members, where
          an instance of StructureMemberDefinition represents that the struct
          member has no format string.

    Returns:
      list[str]: grouped format strings of the struct members, where an instance
          of StructureMemberDefinition represents that the struct member has no
          format string.
    """
    # TODO: handle byte order, since struct only allows a single byte order
    # definition for each format string.
    grouped_format_strings = []

    group_index = None
    for index, format_string in enumerate(format_strings):
      if isinstance(format_string, py2to3.STRING_TYPES):
        if group_index is None:
          group_index = index
        continue

      if group_index is not None:
        format_string_group = u''.join(format_strings[group_index:index])
        grouped_format_strings.append(format_string_group)
        group_index = None

      grouped_format_strings.append(format_string)

    if group_index is not None:
      index = len(format_strings)
      format_string_group = u''.join(format_strings[group_index:index])
      grouped_format_strings.append(format_string_group)

    return grouped_format_strings

  def MapByteStream(self, byte_stream):
    """Maps the data type on top of a byte stream.

    Args:
      byte_stream (bytes): byte stream.

    Returns:
      collections.namedtuple: values mapped.

    Raises:
      MappingError: if the data type definition cannot be mapped on
          the byte stream.
    """
    format_string = []

    try:
      struct_tuple = self._operation.ReadFrom(byte_stream)
      # pylint: disable=protected-access
      return self._named_tuple._make(struct_tuple)

    except Exception as exception:
      raise errors.MappingError(exception)


class UUIDMap(FixedSizeDataTypeMap):
  """UUID (or GUID) data type map."""

  def MapByteStream(self, byte_stream):
    """Maps the data type on top of a byte stream.

    Args:
      byte_stream (bytes): byte stream.

    Returns:
      uuid.UUID: mapped value.

    Raises:
      MappingError: if the data type definition cannot be mapped on
          the byte stream.
    """
    try:
      struct_tuple = self._operation.ReadFrom(byte_stream)
      uuid_string = (
          u'{{{0:08x}-{1:04x}-{2:04x}-{3:02x}{4:02x}-'
          u'{5:02x}{6:02x}{7:02x}{8:02x}{9:02x}{10:02x}}}').format(
              *struct_tuple)
      return uuid.UUID(uuid_string)

    except Exception as exception:
      raise errors.MappingError(exception)


class DataTypeMapFactory(object):
  """Factory for data type maps."""

  # TODO: add support for definitions.TYPE_INDICATOR_CONSTANT
  # TODO: add support for definitions.TYPE_INDICATOR_ENUMERATION
  # TODO: add support for definitions.TYPE_INDICATOR_FORMAT

  _MAP_PER_DEFINITION = {
      definitions.TYPE_INDICATOR_BOOLEAN: BooleanMap,
      definitions.TYPE_INDICATOR_CHARACTER: CharacterMap,
      definitions.TYPE_INDICATOR_FLOATING_POINT: FloatingPointMap,
      definitions.TYPE_INDICATOR_INTEGER: IntegerMap,
      definitions.TYPE_INDICATOR_SEQUENCE: SequenceMap,
      definitions.TYPE_INDICATOR_STRUCTURE: StructureMap,
      definitions.TYPE_INDICATOR_UUID: UUIDMap}

  def __init__(self, definitions_registry):
    """Initializes a data type maps factory.

    Args:
      definitions_registry (DataTypeDefinitionsRegistry): data type definitions
          registry.
    """
    super(DataTypeMapFactory, self).__init__()
    self._definitions_registry = definitions_registry

  def CreateDataTypeMap(self, definition_name):
    """Creates a specific data type map by name.

    Args:
      definition_name (str): name of the data type definition.

    Returns:
      DataTypeMape: data type map or None if the date type definition
          is not available.
    """
    data_type_definition = self._definitions_registry.GetDefinitionByName(
        definition_name)
    if not data_type_definition:
      return

    data_type_map = self._MAP_PER_DEFINITION.get(
        data_type_definition.TYPE_INDICATOR, None)
    if not data_type_map:
      return

    return data_type_map(data_type_definition)
