# -*- coding: utf-8 -*-
"""Tests for the byte stream operations."""

from __future__ import unicode_literals

import unittest

from dtfabric import errors
from dtfabric.runtime import byte_operations

from tests import test_lib


class StructOperationTest(test_lib.BaseTestCase):
  """Python struct-base byte stream operation tests."""

  def testInitialize(self):
    """Tests the __init__ function."""
    byte_stream_operation = byte_operations.StructOperation('b')
    self.assertIsNotNone(byte_stream_operation)

    with self.assertRaises(errors.FormatError):
      byte_operations.StructOperation(None)

    with self.assertRaises(errors.FormatError):
      byte_operations.StructOperation('z')

  def testReadFrom(self):
    """Tests the ReadFrom function."""
    byte_stream_operation = byte_operations.StructOperation('i')

    value = byte_stream_operation.ReadFrom(b'\x12\x34\x56\x78')
    self.assertEqual(value, tuple([0x78563412]))

    with self.assertRaises(IOError):
      byte_stream_operation.ReadFrom(None)

    with self.assertRaises(IOError):
      byte_stream_operation.ReadFrom(b'\x12\x34\x56')

  def testWriteTo(self):
    """Tests the WriteTo function."""
    byte_stream_operation = byte_operations.StructOperation('i')

    byte_stream = byte_stream_operation.WriteTo(tuple([0x78563412]))
    self.assertEqual(byte_stream, b'\x12\x34\x56\x78')

    with self.assertRaises(IOError):
      byte_stream_operation.WriteTo(None)

    with self.assertRaises(IOError):
      byte_stream_operation.WriteTo(0x78563412)

    with self.assertRaises(IOError):
      byte_stream_operation.WriteTo(tuple([0x9078563412]))


if __name__ == '__main__':
  unittest.main()
