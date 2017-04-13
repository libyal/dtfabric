# -*- coding: utf-8 -*-
"""The dtFabric run-time objects."""

import abc
import collections
import struct
import uuid

from dtfabric import errors
from dtfabric import py2to3


# TODO: add EnumerationMap.
# TODO: add FormatMap.
# TODO: complete StructMap.

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
      format_string = data_type_definition.GetStructFormatString()
    except AttributeError as exception:
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


class StructMap(DataTypeMap):
  """Structure data type map."""

  def __init__(self, data_type_definition):
    """Initializes a data type map.

    Args:
      data_type_definition (DataTypeDefinition): data type definition.

    Raises:
      FormatError: if struct format string cannot be determed from
          the data type definition.
    """
    attribute_names = data_type_definition.GetAttributedNames()
    named_tuple = collections.namedtuple(
        data_type_definition.name, attribute_names)

    super(StructMap, self).__init__(data_type_definition)
    self._named_tuple = named_tuple

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
    format_strings = []

    for member in self._data_type_definition.members:
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
      uuid_string = u'{{{0:08x}-{1:04x}-{2:04x}-{3:04x}-{4:010x}}}'
      return uuid.UUID(uuid_string)

    except Exception as exception:
      raise errors.MappingError(exception)
