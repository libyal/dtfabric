# -*- coding: utf-8 -*-
"""The dtFabric run-time objects."""

import abc
import collections
import struct

from dtfabric import errors
from dtfabric import registry


# TODO: add BooleanMap.
# TODO: add CharacterMap.
# TODO: add EnumerationMap.
# TODO: add FormatMap.

class DataTypeMap(object):
  """Class that defines a data type map."""

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
      struct_object = struct.Struct(format_string)
    except (AttributeError, TypeError):
      raise errors.FormatError(
          u'Unable to create struct object from data type definition.')

    super(DataTypeMap, self).__init__()
    self._data_type_definition = data_type_definition
    self._struct = struct_object
    self._struct_format_string = format_string

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


class BooleanMap(DataTypeMap):
  """Class that defines a boolen map."""

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
      struct_tuple = self._struct.unpack_from(byte_stream)
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


class FloatingPointMap(DataTypeMap):
  """Class that defines a floating-point map."""

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
      struct_tuple = self._struct.unpack_from(byte_stream)
      return float(*struct_tuple)

    except Exception as exception:
      raise errors.MappingError(exception)


class IntegerMap(DataTypeMap):
  """Class that defines an integer map."""

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
      struct_tuple = self._struct.unpack_from(byte_stream)
      return int(*struct_tuple)

    except Exception as exception:
      raise errors.MappingError(exception)


class StructMap(DataTypeMap):
  """Class that defines a struct map."""

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

    for struct_member in self._structure_definition.members:
      member_format_string = self._GetStructureMemberFormatString(struct_member)

    struct_tuple = struct.unpack_from(format_string, byte_stream)

    for member in self._structure_definition.members:
      # TODO: implement.
      pass

    try:
      struct_tuple = self._struct.unpack_from(byte_stream)
      # pylint: disable=protected-access
      return self._named_tuple._make(struct_tuple)

    except Exception as exception:
      raise errors.MappingError(exception)
