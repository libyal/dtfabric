# -*- coding: utf-8 -*-
"""The dtFabric run-time objects."""

import collections
import struct

from dtfabric import errors
from dtfabric import registry


class DataTypeMap(object):
  """Class that defines a data type map.

  The data type map maps a data type definition onto binary data.
  """

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

    attribute_names = data_type_definition.GetAttributedNames()
    named_tuple = collections.namedtuple(
        data_type_definition.name, attribute_names)

    super(DataTypeMap, self).__init__()
    self._data_type_definition = data_type_definition
    self._named_tuple = named_tuple
    self._struct = struct_object
    self._struct_format_string = format_string

  def MapByteStream(self, byte_stream):
    """Maps the structure on top of a byte stream.

    Args:
      byte_stream (bytes): byte stream.

    Returns:
      collections.namedtuple: values mapped.

    Raises:
      MappingError: if the data type definition cannot be mapped on
          the byte stream.
    """
    try:
      struct_tuple = self._struct.unpack_from(byte_stream)
      # pylint: disable=protected-access
      return self._named_tuple._make(struct_tuple)

    except Exception as exception:
      raise errors.MappingError(exception)


class StructMap(DataTypeMap):
  """Class that defines a struct map.

  The struct map maps a structure type definition onto binary data.
  """

  def MapByteStream(self, byte_stream):
    """Maps the structure on top of a byte stream.

    Args:
      byte_stream (bytes): byte stream.

    Raises:
      IOError: if the structure map cannot be copied from the byte stream.
    """
    format_string = []

    for struct_member in self._structure_definition.members:
      member_format_string = self._GetStructureMemberFormatString(struct_member)

    struct_tuple = struct.unpack_from(format_string, byte_stream)

    for member in self._structure_definition.members:
      # TODO: implement.
      pass
