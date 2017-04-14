# -*- coding: utf-8 -*-
"""Tests for the run-time object."""

import os
import unittest
import uuid

from dtfabric import data_types
from dtfabric import definitions
from dtfabric import errors
from dtfabric import runtime

from tests import test_lib


class EmptyDataTypeDefinition(data_types.DataTypeDefinition):
  """Empty data type definition for testing."""

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

  def GetStructByteOrderString(self):
    """Retrieves the Python struct format string.

    Returns:
      str: format string as used by Python struct or None if format string
          cannot be determined.
    """
    return

  def GetStructFormatString(self):
    """Retrieves the Python struct format string.

    Returns:
      str: format string as used by Python struct or None if format string
          cannot be determined.
    """
    return


class StructOperationTest(test_lib.BaseTestCase):
  """Python struct-base binary stream operation tests."""

  def testInitialize(self):
    """Tests the __init__ function."""
    byte_stream_operation = runtime.StructOperation(u'b')
    self.assertIsNotNone(byte_stream_operation)

    with self.assertRaises(errors.FormatError):
      runtime.StructOperation(None)

    with self.assertRaises(errors.FormatError):
      runtime.StructOperation(u'z')

  def testReadFrom(self):
    """Tests the ReadFrom function."""
    byte_stream_operation = runtime.StructOperation(u'i')

    struct_tuple = byte_stream_operation.ReadFrom(b'\x12\x34\x56\x78')
    self.assertEqual(struct_tuple, (0x78563412, ))

    with self.assertRaises(IOError):
      byte_stream_operation.ReadFrom(None)

    with self.assertRaises(IOError):
      byte_stream_operation.ReadFrom(b'\x12\x34\x56')


@test_lib.skipUnlessHasTestFile([u'integer.yaml'])
class DataTypeMapTest(test_lib.BaseTestCase):
  """Data type map tests."""

  # pylint: disable=protected-access

  def testGetStructByteOrderString(self):
    """Tests the _GetStructByteOrderString function."""
    definitions_file = self._GetTestFilePath([u'integer.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)
    data_type_definition = definitions_registry.GetDefinitionByName(u'int32le')

    data_type_map = runtime.DataTypeMap(data_type_definition)

    format_string = data_type_map._GetStructByteOrderString(
        data_type_definition)
    self.assertEqual(format_string, u'<')

    with self.assertRaises(errors.FormatError):
      data_type_definition = EmptyDataTypeDefinition(u'empty')
      data_type_map._GetStructByteOrderString(data_type_definition)

  def testGetStructFormatString(self):
    """Tests the _GetStructFormatString function."""
    definitions_file = self._GetTestFilePath([u'integer.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)
    data_type_definition = definitions_registry.GetDefinitionByName(u'int32le')

    data_type_map = runtime.DataTypeMap(data_type_definition)

    format_string = data_type_map._GetStructFormatString(data_type_definition)
    self.assertEqual(format_string, u'i')

    with self.assertRaises(errors.FormatError):
      data_type_definition = EmptyDataTypeDefinition(u'empty')
      data_type_map._GetStructFormatString(data_type_definition)

  def testGetByteSize(self):
    """Tests the GetByteSize function."""
    definitions_file = self._GetTestFilePath([u'integer.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)
    data_type_definition = definitions_registry.GetDefinitionByName(u'int32le')

    data_type_map = runtime.DataTypeMap(data_type_definition)

    byte_size = data_type_map.GetByteSize()
    self.assertEqual(byte_size, 4)


@test_lib.skipUnlessHasTestFile([u'integer.yaml'])
class FixedSizeDataTypeMapTest(test_lib.BaseTestCase):
  """Fixed-size data type map tests."""

  def testInitialize(self):
    """Tests the __init__ function."""
    definitions_file = self._GetTestFilePath([u'integer.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)
    data_type_definition = definitions_registry.GetDefinitionByName(u'int32le')

    data_type_map = runtime.FixedSizeDataTypeMap(data_type_definition)
    self.assertIsNotNone(data_type_map)

    with self.assertRaises(errors.FormatError):
      runtime.FixedSizeDataTypeMap(None)

    with self.assertRaises(errors.FormatError):
      data_type_definition = EmptyDataTypeDefinition(u'empty')
      runtime.FixedSizeDataTypeMap(data_type_definition)


@test_lib.skipUnlessHasTestFile([u'definitions', u'booleans.yaml'])
class BooleanMapTest(test_lib.BaseTestCase):
  """Boolean map tests."""

  def testInitialize(self):
    """Tests the __init__ function."""
    definitions_file = self._GetTestFilePath([u'definitions', u'booleans.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)
    data_type_definition = definitions_registry.GetDefinitionByName(u'bool32')
    data_type_definition.byte_order = definitions.BYTE_ORDER_LITTLE_ENDIAN

    data_type_definition.false_value = None
    data_type_definition.true_value = None
    with self.assertRaises(errors.FormatError):
      runtime.BooleanMap(data_type_definition)

  def testMapByteStream(self):
    """Tests the MapByteStream function."""
    definitions_file = self._GetTestFilePath([u'definitions', u'booleans.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)

    data_type_definition = definitions_registry.GetDefinitionByName(u'bool8')
    data_type_definition.byte_order = definitions.BYTE_ORDER_LITTLE_ENDIAN
    data_type_map = runtime.BooleanMap(data_type_definition)
    data_type_definition.true_value = 1

    bool_value = data_type_map.MapByteStream(b'\x00')
    self.assertFalse(bool_value)

    bool_value = data_type_map.MapByteStream(b'\x01')
    self.assertTrue(bool_value)

    with self.assertRaises(errors.MappingError):
      data_type_map.MapByteStream(b'\xff')

    data_type_definition = definitions_registry.GetDefinitionByName(u'bool16')
    data_type_definition.byte_order = definitions.BYTE_ORDER_LITTLE_ENDIAN
    data_type_definition.false_value = None
    data_type_definition.true_value = 1
    data_type_map = runtime.BooleanMap(data_type_definition)

    bool_value = data_type_map.MapByteStream(b'\xff\xff')
    self.assertFalse(bool_value)

    bool_value = data_type_map.MapByteStream(b'\x01\x00')
    self.assertTrue(bool_value)

    data_type_definition = definitions_registry.GetDefinitionByName(u'bool32')
    data_type_definition.byte_order = definitions.BYTE_ORDER_LITTLE_ENDIAN
    data_type_definition.true_value = None
    data_type_map = runtime.BooleanMap(data_type_definition)

    bool_value = data_type_map.MapByteStream(b'\x00\x00\x00\x00')
    self.assertFalse(bool_value)

    bool_value = data_type_map.MapByteStream(b'\xff\xff\xff\xff')
    self.assertTrue(bool_value)

    with self.assertRaises(errors.MappingError):
      data_type_map.MapByteStream(b'\x01\x00')


@test_lib.skipUnlessHasTestFile([u'definitions', u'characters.yaml'])
class CharacterMapTest(test_lib.BaseTestCase):
  """Character map tests."""

  def testMapByteStream(self):
    """Tests the MapByteStream function."""
    definitions_file = self._GetTestFilePath([
        u'definitions', u'characters.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)

    data_type_definition = definitions_registry.GetDefinitionByName(u'char')
    data_type_definition.byte_order = definitions.BYTE_ORDER_LITTLE_ENDIAN
    data_type_map = runtime.CharacterMap(data_type_definition)

    string_value = data_type_map.MapByteStream(b'\x41')
    self.assertEqual(string_value, u'A')

    data_type_definition = definitions_registry.GetDefinitionByName(u'wchar16')
    data_type_definition.byte_order = definitions.BYTE_ORDER_LITTLE_ENDIAN
    data_type_map = runtime.CharacterMap(data_type_definition)

    string_value = data_type_map.MapByteStream(b'\xb6\x24')
    self.assertEqual(string_value, u'\u24b6')

    data_type_definition = definitions_registry.GetDefinitionByName(u'wchar32')
    data_type_definition.byte_order = definitions.BYTE_ORDER_LITTLE_ENDIAN
    data_type_map = runtime.CharacterMap(data_type_definition)

    string_value = data_type_map.MapByteStream(b'\xb6\x24\x00\x00')
    self.assertEqual(string_value, u'\u24b6')

    with self.assertRaises(errors.MappingError):
      data_type_map.MapByteStream(b'\xb6\x24')


@test_lib.skipUnlessHasTestFile([u'definitions', u'floating-points.yaml'])
class FloatingPointMapTest(test_lib.BaseTestCase):
  """Floating-point map tests."""

  def testMapByteStream(self):
    """Tests the MapByteStream function."""
    definitions_file = self._GetTestFilePath([
        u'definitions', u'floating-points.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)

    data_type_definition = definitions_registry.GetDefinitionByName(u'float32')
    data_type_definition.byte_order = definitions.BYTE_ORDER_LITTLE_ENDIAN
    data_type_map = runtime.FloatingPointMap(data_type_definition)

    float_value = data_type_map.MapByteStream(b'\xa4\x70\x45\x41')
    self.assertEqual(float_value, 12.34000015258789)

    data_type_definition = definitions_registry.GetDefinitionByName(u'float64')
    data_type_definition.byte_order = definitions.BYTE_ORDER_LITTLE_ENDIAN
    data_type_map = runtime.FloatingPointMap(data_type_definition)

    float_value = data_type_map.MapByteStream(
        b'\xae\x47\xe1\x7a\x14\xae\x28\x40')
    self.assertEqual(float_value, 12.34)

    with self.assertRaises(errors.MappingError):
      data_type_map.MapByteStream(b'\xa4\x70\x45\x41')


@test_lib.skipUnlessHasTestFile([u'definitions', u'integers.yaml'])
class IntegerMapTest(test_lib.BaseTestCase):
  """Integer map tests."""

  def testMapByteStream(self):
    """Tests the MapByteStream function."""
    definitions_file = self._GetTestFilePath([u'definitions', u'integers.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)

    data_type_definition = definitions_registry.GetDefinitionByName(u'uint8')
    data_type_definition.byte_order = definitions.BYTE_ORDER_LITTLE_ENDIAN
    data_type_map = runtime.IntegerMap(data_type_definition)

    integer_value = data_type_map.MapByteStream(b'\x12')
    self.assertEqual(integer_value, 0x12)

    data_type_definition = definitions_registry.GetDefinitionByName(u'uint16')
    data_type_definition.byte_order = definitions.BYTE_ORDER_LITTLE_ENDIAN
    data_type_map = runtime.IntegerMap(data_type_definition)

    integer_value = data_type_map.MapByteStream(b'\x12\x34')
    self.assertEqual(integer_value, 0x3412)

    data_type_definition = definitions_registry.GetDefinitionByName(u'uint32')
    data_type_definition.byte_order = definitions.BYTE_ORDER_LITTLE_ENDIAN
    data_type_map = runtime.IntegerMap(data_type_definition)

    integer_value = data_type_map.MapByteStream(b'\x12\x34\x56\x78')
    self.assertEqual(integer_value, 0x78563412)

    data_type_definition = definitions_registry.GetDefinitionByName(u'uint32')
    data_type_definition.byte_order = definitions.BYTE_ORDER_BIG_ENDIAN
    data_type_map = runtime.IntegerMap(data_type_definition)

    integer_value = data_type_map.MapByteStream(b'\x12\x34\x56\x78')
    self.assertEqual(integer_value, 0x12345678)

    data_type_definition = definitions_registry.GetDefinitionByName(u'uint64')
    data_type_definition.byte_order = definitions.BYTE_ORDER_LITTLE_ENDIAN
    data_type_map = runtime.IntegerMap(data_type_definition)

    integer_value = data_type_map.MapByteStream(
        b'\x12\x34\x56\x78\x9a\xbc\xde\xf0')
    self.assertEqual(integer_value, 0xf0debc9a78563412)

    with self.assertRaises(errors.MappingError):
      data_type_map.MapByteStream(b'\x12\x34\x56\x78')


@test_lib.skipUnlessHasTestFile([u'sequence.yaml'])
class SequenceMapTest(test_lib.BaseTestCase):
  """Sequence map tests."""

  def testInitialize(self):
    """Tests the __init__ function."""
    definitions_file = self._GetTestFilePath([u'sequence.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)
    data_type_definition = definitions_registry.GetDefinitionByName(u'vector4')

    data_type_map = runtime.SequenceMap(data_type_definition)
    self.assertIsNotNone(data_type_map)

    with self.assertRaises(errors.FormatError):
      runtime.SequenceMap(None)

    with self.assertRaises(errors.FormatError):
      data_type_definition = EmptyDataTypeDefinition(u'empty')
      runtime.SequenceMap(data_type_definition)

  def testMapByteStream(self):
    """Tests the MapByteStream function."""
    definitions_file = self._GetTestFilePath([u'sequence.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)
    data_type_definition = definitions_registry.GetDefinitionByName(u'vector4')

    data_type_map = runtime.SequenceMap(data_type_definition)

    sequence_value = data_type_map.MapByteStream(
        b'\x01\x00\x00\x00\x02\x00\x00\x00\x03\x00\x00\x00\x04\x00\x00\x00')
    self.assertEqual(sequence_value, (1, 2, 3, 4))


@test_lib.skipUnlessHasTestFile([u'structure.yaml'])
class StructureMapTest(test_lib.BaseTestCase):
  """Structure map tests."""

  # pylint: disable=protected-access

  def testInitialize(self):
    """Tests the __init__ function."""
    definitions_file = self._GetTestFilePath([u'structure.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)

    data_type_definition = definitions_registry.GetDefinitionByName(u'point3d')
    data_type_map = runtime.StructureMap(data_type_definition)
    self.assertIsNotNone(data_type_map)

  # TODO: test _GetStructFormatStringAndObject

  def testGetStructFormatStrings(self):
    """Tests the _GetStructFormatStrings function."""
    definitions_file = self._GetTestFilePath([u'structure.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)

    data_type_definition = definitions_registry.GetDefinitionByName(u'point3d')
    data_type_map = runtime.StructureMap(data_type_definition)

    format_strings = data_type_map._GetStructFormatStrings(data_type_definition)
    self.assertEqual(format_strings, [u'=', u'i', u'i', u'i'])

    data_type_definition = definitions_registry.GetDefinitionByName(
        u'triangle3d')
    data_type_map = runtime.StructureMap(data_type_definition)

    format_strings = data_type_map._GetStructFormatStrings(data_type_definition)
    self.assertEqual(format_strings, [u'=', u'iii', u'iii', u'iii'])

  def testGroupFormatStrings(self):
    """Tests the _GroupFormatStrings function."""
    definitions_file = self._GetTestFilePath([u'structure.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)

    data_type_definition = definitions_registry.GetDefinitionByName(u'point3d')
    data_type_map = runtime.StructureMap(data_type_definition)

    format_strings = [u'a', u'b', None, u'c', None]
    expected_grouped_format_strings = [u'ab', None, u'c', None]

    grouped_format_strings = data_type_map._GroupFormatStrings(format_strings)
    self.assertEqual(grouped_format_strings, expected_grouped_format_strings)

    grouped_format_strings = data_type_map._GroupFormatStrings([])
    self.assertEqual(grouped_format_strings, [])

    grouped_format_strings = data_type_map._GroupFormatStrings([u'a'])
    self.assertEqual(grouped_format_strings, [u'a'])

    grouped_format_strings = data_type_map._GroupFormatStrings([None])
    self.assertEqual(grouped_format_strings, [None])

  @test_lib.skipUnlessHasTestFile([u'structure.yaml'])
  def testMapByteStream(self):
    """Tests the MapByteStream function."""
    definitions_file = self._GetTestFilePath([u'structure.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)

    data_type_definition = definitions_registry.GetDefinitionByName(u'point3d')
    data_type_map = runtime.StructureMap(data_type_definition)

    named_tuple = data_type_map.MapByteStream(
        b'\x01\x00\x00\x00\x02\x00\x00\x00\x03\x00\x00\x00')
    self.assertEqual(named_tuple.x, 1)
    self.assertEqual(named_tuple.y, 2)
    self.assertEqual(named_tuple.z, 3)


@test_lib.skipUnlessHasTestFile([u'uuid.yaml'])
class UUIDMapTest(test_lib.BaseTestCase):
  """UUID map tests."""

  def testMapByteStream(self):
    """Tests the MapByteStream function."""
    definitions_file = self._GetTestFilePath([u'uuid.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)

    data_type_definition = definitions_registry.GetDefinitionByName(u'uuid')
    data_type_definition.byte_order = definitions.BYTE_ORDER_LITTLE_ENDIAN
    data_type_map = runtime.UUIDMap(data_type_definition)

    expected_uuid_value = uuid.UUID(u'{00021401-0000-0000-c000-000000000046}')
    uuid_value = data_type_map.MapByteStream(
        b'\x01\x14\x02\x00\x00\x00\x00\x00\xc0\x00\x00\x00\x00\x00\x00\x46')
    self.assertEqual(uuid_value, expected_uuid_value)


class DataTypeMapFactoryTest(test_lib.BaseTestCase):
  """Data type map factory tests."""

  def testCreateDataTypeMap(self):
    """Tests the CreateDataTypeMap function."""
    definitions_file = os.path.join(u'data', u'definitions', u'core.yaml')
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)

    data_type_definition = EmptyDataTypeDefinition(u'empty')
    definitions_registry.RegisterDefinition(data_type_definition)

    factory = runtime.DataTypeMapFactory(definitions_registry)

    data_type_map = factory.CreateDataTypeMap(u'int32')
    self.assertIsNotNone(data_type_map)

    data_type_map = factory.CreateDataTypeMap(u'empty')
    self.assertIsNone(data_type_map)

    data_type_map = factory.CreateDataTypeMap(u'bogus')
    self.assertIsNone(data_type_map)


if __name__ == '__main__':
  unittest.main()
