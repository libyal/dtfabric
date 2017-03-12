# -*- coding: utf-8 -*-
"""Tests for the run-time object."""

import os
import unittest

from dtfabric import errors
from dtfabric import definitions
from dtfabric import reader
from dtfabric import registry
from dtfabric import runtime

from tests import test_lib


def CreateDefinitionRegistryFromFile(path):
  """Creates a data type definition registry from a file.

  Args:
    path (str): path to the data definition file.

  Returns:
    DataTypeDefinitionsRegistry: data type definition registry or None
        on error.
  """
  definitions_registry = registry.DataTypeDefinitionsRegistry()
  definitions_reader = reader.YAMLDataTypeDefinitionsFileReader()

  with open(path, 'rb') as file_object:
    definitions_reader.ReadFileObject(definitions_registry, file_object)

  return definitions_registry


class EmptytDataTypeDefinition(definitions.DataTypeDefinition):
  """Class that defines an empty data type definition for testing."""

  def GetByteSize(self):
    """Determines the byte size of the data type definition.

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


class DataTypeMapTest(test_lib.BaseTestCase):
  """Class to test the data type map."""

  # pylint: disable=protected-access

  def testInitialize(self):
    """Tests the initialize function."""
    definitions_file = os.path.join(u'data', u'definitions', u'integers.yaml')
    definitions_registry = CreateDefinitionRegistryFromFile(definitions_file)
    data_type_definition = definitions_registry.GetDefinitionByName(u'int32')

    data_type_map = runtime.DataTypeMap(data_type_definition)
    self.assertIsNotNone(data_type_map)

    with self.assertRaises(errors.FormatError):
      runtime.DataTypeMap(None)

    with self.assertRaises(errors.FormatError):
      data_type_definition = EmptytDataTypeDefinition(u'empty')
      runtime.DataTypeMap(data_type_definition)

  def testMapByteStream(self):
    """Tests the MapByteStream function."""
    definitions_file = os.path.join(u'data', u'definitions', u'integers.yaml')
    definitions_registry = CreateDefinitionRegistryFromFile(definitions_file)

    data_type_definition = definitions_registry.GetDefinitionByName(u'uint8')
    data_type_map = runtime.DataTypeMap(data_type_definition)

    named_tuple = data_type_map.MapByteStream(b'\x12')

    self.assertIsNotNone(named_tuple)
    self.assertEqual(named_tuple.value, 0x12)

    data_type_definition = definitions_registry.GetDefinitionByName(u'uint16')
    data_type_map = runtime.DataTypeMap(data_type_definition)

    named_tuple = data_type_map.MapByteStream(b'\x12\x34')

    self.assertIsNotNone(named_tuple)
    self.assertEqual(named_tuple.value, 0x3412)

    data_type_definition = definitions_registry.GetDefinitionByName(u'uint32')
    data_type_map = runtime.DataTypeMap(data_type_definition)

    named_tuple = data_type_map.MapByteStream(b'\x12\x34\x56\x78')

    self.assertIsNotNone(named_tuple)
    self.assertEqual(named_tuple.value, 0x78563412)

    data_type_definition = definitions_registry.GetDefinitionByName(u'uint64')
    data_type_map = runtime.DataTypeMap(data_type_definition)

    named_tuple = data_type_map.MapByteStream(
        b'\x12\x34\x56\x78\x9a\xbc\xde\xf0')

    self.assertIsNotNone(named_tuple)
    self.assertEqual(named_tuple.value, 0xf0debc9a78563412)

    with self.assertRaises(errors.MappingError):
      data_type_map.MapByteStream(b'\x12\x34\x56\x78')


class StrcutMapTest(test_lib.BaseTestCase):
  """Class to test the struct map."""

  # pylint: disable=protected-access

  @test_lib.skipUnlessHasTestFile([u'Notepad.lnk'])
  def testMapByteStream(self):
    """Tests the MapByteStream function."""
    definitions_file = os.path.join(u'data', u'definitions', u'lnk.yaml')
    definitions_registry = CreateDefinitionRegistryFromFile(definitions_file)
    data_type_definition = definitions_registry.GetDefinitionByName(
        u'file_header')

    path = self._GetTestFilePath([u'Notepad.lnk'])
    with open(path, 'rb') as file_object:
      byte_stream = file_object.read()

    # TODO: implement.
    with self.assertRaises(errors.FormatError):
      data_type_map = runtime.DataTypeMap(data_type_definition)


if __name__ == '__main__':
  unittest.main()
