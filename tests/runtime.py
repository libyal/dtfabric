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

  def GetAttributedNames(self):
    """Determines the attribute (or field) names of the data type definition.

    Returns:
      list[str]: attribute names.
    """
    return [u'empty']

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


class FloatingPointMap(test_lib.BaseTestCase):
  """Class to test the floating-point map."""

  def testMapByteStream(self):
    """Tests the MapByteStream function."""
    definitions_file = os.path.join(
        u'data', u'definitions', u'floating-points.yaml')
    definitions_registry = CreateDefinitionRegistryFromFile(definitions_file)

    data_type_definition = definitions_registry.GetDefinitionByName(u'float32')
    data_type_map = runtime.FloatingPointMap(data_type_definition)

    float_value = data_type_map.MapByteStream(b'\xa4\x70\x45\x41')
    self.assertEqual(float_value, 12.34000015258789)

    data_type_definition = definitions_registry.GetDefinitionByName(u'float64')
    data_type_map = runtime.FloatingPointMap(data_type_definition)

    float_value = data_type_map.MapByteStream(
        b'\xae\x47\xe1\x7a\x14\xae\x28\x40')
    self.assertEqual(float_value, 12.34)

    with self.assertRaises(errors.MappingError):
      data_type_map.MapByteStream(b'\xa4\x70\x45\x41')


class IntegerMapTest(test_lib.BaseTestCase):
  """Class to test the integer map."""

  def testMapByteStream(self):
    """Tests the MapByteStream function."""
    definitions_file = os.path.join(u'data', u'definitions', u'integers.yaml')
    definitions_registry = CreateDefinitionRegistryFromFile(definitions_file)

    data_type_definition = definitions_registry.GetDefinitionByName(u'uint8')
    data_type_map = runtime.IntegerMap(data_type_definition)

    integer_value = data_type_map.MapByteStream(b'\x12')
    self.assertEqual(integer_value, 0x12)

    data_type_definition = definitions_registry.GetDefinitionByName(u'uint16')
    data_type_map = runtime.IntegerMap(data_type_definition)

    integer_value = data_type_map.MapByteStream(b'\x12\x34')
    self.assertEqual(integer_value, 0x3412)

    data_type_definition = definitions_registry.GetDefinitionByName(u'uint32')
    data_type_map = runtime.IntegerMap(data_type_definition)

    integer_value = data_type_map.MapByteStream(b'\x12\x34\x56\x78')
    self.assertEqual(integer_value, 0x78563412)

    data_type_definition = definitions_registry.GetDefinitionByName(u'uint64')
    data_type_map = runtime.IntegerMap(data_type_definition)

    integer_value = data_type_map.MapByteStream(
        b'\x12\x34\x56\x78\x9a\xbc\xde\xf0')
    self.assertEqual(integer_value, 0xf0debc9a78563412)

    with self.assertRaises(errors.MappingError):
      data_type_map.MapByteStream(b'\x12\x34\x56\x78')


class StructMapTest(test_lib.BaseTestCase):
  """Class to test the struct map."""

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
      data_type_map = runtime.StructMap(data_type_definition)
      data_type_map.MapByteStream(byte_stream)


if __name__ == '__main__':
  unittest.main()
