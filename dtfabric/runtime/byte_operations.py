# -*- coding: utf-8 -*-
"""Byte stream operations."""

from __future__ import unicode_literals
import abc
import struct

from dtfabric import errors


class ByteStreamOperation(object):
  """Byte stream operation."""

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
      FormatError: if the struct operation cannot be determed from the data
          type definition.
    """
    try:
      struct_object = struct.Struct(format_string)
    except (TypeError, struct.error) as exception:
      raise errors.FormatError((
          'Unable to create struct object from data type definition '
          'with error: {0!s}').format(exception))

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
    """
    try:
      return self._struct.unpack_from(byte_stream)
    except (TypeError, struct.error) as exception:
      raise IOError('Unable to read byte stream with error: {0!s}'.format(
          exception))

  def WriteTo(self, values):
    """Writes values to a byte stream.

    Args:
      values (tuple[object, ...]): values to copy to the byte stream.

    Returns:
      bytes: byte stream.

    Raises:
      IOError: if byte stream cannot be written.
    """
    try:
      return self._struct.pack(*values)
    except (TypeError, struct.error) as exception:
      raise IOError('Unable to write stream with error: {0!s}'.format(
          exception))
