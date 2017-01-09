# -*- coding: utf-8 -*-
"""The dtFabric run-time objects."""

import struct

from dtfabric import definitions
from dtfabric import errors
from dtfabric import registry


class DataFormatMap(object):
  """Class that defines a format map."""

  def __init__(self):
    """Initializes a data format map."""
    super(FormatMap, self).__init__()
    # TODO: implement.
    self._structure_definition = structure_definition
    self._structure_definitions_registry = (
        registry.DataTypeDefinitionsRegistry())


class DataTypeMap(object):
  """Class that defines a data type map.

  The data type map maps the data type definition onto binary data.
  """

  def __init__(self, data_type_definition):
    """Initializes a data type map.

    Args:
      data_type_definition (DataTypeDefinition): data type definition.
    """
    super(DataTypeMap, self).__init__()
    self._data_type_definition = data_type_definition
    self._struct = struct.Struct(format_definition)

  @classmethod
  def _GetStructFormatString(cls, data_type_definition):
    """Retrieves the Python struct format string.

    Args:
      data_type_definition (DataTypeDefinition): data type definition.

    Returns:
      str: format string as used by Python struct.

    Raises:
      FormatError: if the definitions values are missing or if the format is
          incorrect.
    """
    return data_type_definition.GetStructFormatString()


class StructMap(object):
  """Class that defines a structure map."""

  _FORMAT_STRINGS = b''

  def __init__(self, structure_definition):
    """Initializes a structure map.

    Args:
      structure_definition (StructureDefinition): structure definition.
    """
    super(StructMap, self).__init__()
    self._struct = struct.Struct(format_definition)
    self._structure_definition = structure_definition

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
