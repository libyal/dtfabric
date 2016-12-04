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
    self._structure_definition = structure_definition
    self._structure_definitions_registry = (
        registry.DataTypeDefinitionsRegistry())


class StructMap(object):
  """Class that defines a structure map."""

  _FORMAT_STRINGS = b''

  def __init__(self, structure_definition):
    """Initializes a structure map.

    Args:
      structure_definition (StructureDefinition): structure definition.
    """
    super(StructMap, self).__init__()
    self._structure_definition = structure_definition

  def _GetStructureMemberFormatString(self, struct_member):
    """Retrieves the structure member format string.

    Args:
      struct_member (StructureMemberDefinition): structure member definition.

    Returns:
      str: format string as used by Python struct.
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
