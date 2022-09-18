# -*- coding: utf-8 -*-
"""Byte stream operations."""

import abc
import struct

from dtfabric import errors


class ByteStreamOperation(object):
  """Byte stream operation."""

  # Note that redundant-returns-doc is broken for pylint 1.7.x for abstract
  # methods.
  # pylint: disable=redundant-returns-doc

  @abc.abstractmethod
  def ReadFrom(self, byte_stream):
    """Read values from a byte stream.

    Args:
      byte_stream (bytes): byte stream.

    Returns:
      tuple[object, ...]: values copies from the byte stream.
    """

  @abc.abstractmethod
  def WriteTo(self, values):
    """Writes values to a byte stream.

    Args:
      values (tuple[object, ...]): values to copy to the byte stream.

    Returns:
      bytes: byte stream.
    """


class StructOperation(ByteStreamOperation):
  """Python struct-base byte stream operation."""

  def __init__(self, format_string):
    """Initializes a Python struct-base byte stream operation.

    Args:
      format_string (str): format string as used by Python struct.

    Raises:
      FormatError: if the struct operation cannot be determined from the data
          type definition.
    """
    try:
      struct_object = struct.Struct(format_string)
    except (TypeError, struct.error) as exception:
      raise errors.FormatError(
          f'Unable to create struct object from data type definition '
          f'with error: {exception!s}')

    super(StructOperation, self).__init__()
    self._struct = struct_object
    self._struct_format_string = format_string

  def ReadFrom(self, byte_stream):
    """Read values from a byte stream.

    Args:
      byte_stream (bytes): byte stream.

    Returns:
      tuple[object, ...]: values copies from the byte stream.

    Raises:
      IOError: if byte stream cannot be read.
      OSError: if byte stream cannot be read.
    """
    try:
      return self._struct.unpack_from(byte_stream)
    except (TypeError, struct.error) as exception:
      raise IOError(f'Unable to read byte stream with error: {exception!s}')

  def WriteTo(self, values):
    """Writes values to a byte stream.

    Args:
      values (tuple[object, ...]): values to copy to the byte stream.

    Returns:
      bytes: byte stream.

    Raises:
      IOError: if byte stream cannot be written.
      OSError: if byte stream cannot be read.
    """
    try:
      return self._struct.pack(*values)
    except (TypeError, struct.error) as exception:
      raise IOError(f'Unable to write stream with error: {exception!s}')
