# -*- coding: utf-8 -*-
"""Tests for the data type maps."""

from __future__ import unicode_literals

import unittest
import uuid

from dtfabric import data_types
from dtfabric import definitions
from dtfabric import errors
from dtfabric.runtime import byte_operations
from dtfabric.runtime import data_maps

from tests import test_lib


class EmptyDataTypeDefinition(data_types.DataTypeDefinition):
  """Empty data type definition for testing."""

  def GetByteSize(self):
    """Determines the byte size of the data type definition.

    Returns:
      int: data type size in bytes or None if size cannot be determined.
    """
    return


class TestDataTypeDefinition(data_types.DataTypeDefinition):
  """Data type definition for testing."""

  def GetByteSize(self):
    """Determines the byte size of the data type definition.

    Returns:
      int: data type size in bytes or None if size cannot be determined.
    """
    return


class DataTypeMapContextTest(test_lib.BaseTestCase):
  """Data type map context tests."""

  def testInitialize(self):
    """Tests the __init__ function."""
    data_type_map_context = data_maps.DataTypeMapContext()
    self.assertIsNotNone(data_type_map_context)


@test_lib.skipUnlessHasTestFile(['integer.yaml'])
class DataTypeMapTest(test_lib.BaseTestCase):
  """Data type map tests."""

  def testInitialize(self):
    """Tests the __init__ function."""
    definitions_file = self._GetTestFilePath(['integer.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)
    data_type_definition = definitions_registry.GetDefinitionByName('int32le')

    data_type_map = data_maps.DataTypeMap(data_type_definition)
    self.assertIsNotNone(data_type_map)

  def testGetByteSize(self):
    """Tests the GetByteSize function."""
    definitions_file = self._GetTestFilePath(['integer.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)
    data_type_definition = definitions_registry.GetDefinitionByName('int32le')

    data_type_map = data_maps.DataTypeMap(data_type_definition)

    byte_size = data_type_map.GetByteSize()
    self.assertEqual(byte_size, 4)

  def testGetSizeHint(self):
    """Tests the GetSizeHint function."""
    definitions_file = self._GetTestFilePath(['integer.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)
    data_type_definition = definitions_registry.GetDefinitionByName('int32le')

    data_type_map = data_maps.DataTypeMap(data_type_definition)

    size_hint = data_type_map.GetSizeHint()
    self.assertEqual(size_hint, 4)


@test_lib.skipUnlessHasTestFile(['integer.yaml'])
class StorageDataTypeMapTest(test_lib.BaseTestCase):
  """Storage data type map tests."""

  # pylint: disable=protected-access

  # TODO: add tests for _CheckByteStreamSize

  def testGetByteStreamOperation(self):
    """Tests the _GetByteStreamOperation function."""
    definitions_file = self._GetTestFilePath(['integer.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)

    data_type_definition = definitions_registry.GetDefinitionByName('int32le')
    data_type_map = data_maps.StorageDataTypeMap(data_type_definition)
    map_operation = data_type_map._GetByteStreamOperation()
    self.assertIsNone(map_operation)

  def testGetStructByteOrderString(self):
    """Tests the GetStructByteOrderString function."""
    definitions_file = self._GetTestFilePath(['integer.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)

    data_type_definition = definitions_registry.GetDefinitionByName('int32')
    data_type_map = data_maps.StorageDataTypeMap(data_type_definition)
    byte_order_string = data_type_map.GetStructByteOrderString()
    self.assertEqual(byte_order_string, '=')

    data_type_definition = definitions_registry.GetDefinitionByName('int32be')
    data_type_map = data_maps.StorageDataTypeMap(data_type_definition)
    byte_order_string = data_type_map.GetStructByteOrderString()
    self.assertEqual(byte_order_string, '>')

    data_type_definition = definitions_registry.GetDefinitionByName('int32le')
    data_type_map = data_maps.StorageDataTypeMap(data_type_definition)
    byte_order_string = data_type_map.GetStructByteOrderString()
    self.assertEqual(byte_order_string, '<')

  def testGetStructFormatString(self):
    """Tests the GetStructFormatString function."""
    definitions_file = self._GetTestFilePath(['integer.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)

    data_type_definition = definitions_registry.GetDefinitionByName('int32le')
    data_type_map = data_maps.StorageDataTypeMap(data_type_definition)
    format_string = data_type_map.GetStructFormatString()
    self.assertIsNone(format_string)


@test_lib.skipUnlessHasTestFile(['integer.yaml'])
class PrimitiveDataTypeMapTest(test_lib.BaseTestCase):
  """Primitive data type map tests."""

  def testFoldByteStream(self):
    """Tests the FoldByteStream function."""
    definitions_file = self._GetTestFilePath(['integer.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)

    data_type_definition = definitions_registry.GetDefinitionByName('int32le')
    data_type_map = data_maps.PrimitiveDataTypeMap(data_type_definition)

    with self.assertRaises(errors.FoldingError):
      data_type_map.FoldByteStream(1)

  def testFoldValue(self):
    """Tests the FoldValue function."""
    definitions_file = self._GetTestFilePath(['integer.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)

    data_type_definition = definitions_registry.GetDefinitionByName('int32le')
    data_type_map = data_maps.PrimitiveDataTypeMap(data_type_definition)

    integer_value = data_type_map.FoldValue(1)
    self.assertEqual(integer_value, 1)

  def testMapByteStream(self):
    """Tests the MapByteStream function."""
    definitions_file = self._GetTestFilePath(['integer.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)

    data_type_definition = definitions_registry.GetDefinitionByName('int32le')
    data_type_map = data_maps.PrimitiveDataTypeMap(data_type_definition)

    with self.assertRaises(errors.MappingError):
      data_type_map.MapByteStream(b'\x01\x00\x00\x00')

  def testMapValue(self):
    """Tests the MapValue function."""
    definitions_file = self._GetTestFilePath(['integer.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)

    data_type_definition = definitions_registry.GetDefinitionByName('int32le')
    data_type_map = data_maps.PrimitiveDataTypeMap(data_type_definition)

    integer_value = data_type_map.MapValue(1)
    self.assertEqual(integer_value, 1)


@test_lib.skipUnlessHasTestFile(['definitions', 'booleans.yaml'])
class BooleanMapTest(test_lib.BaseTestCase):
  """Boolean map tests."""

  def testInitialize(self):
    """Tests the __init__ function."""
    definitions_file = self._GetTestFilePath(['definitions', 'booleans.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)
    data_type_definition = definitions_registry.GetDefinitionByName('bool32')
    data_type_definition.byte_order = definitions.BYTE_ORDER_LITTLE_ENDIAN

    data_type_definition.false_value = None
    data_type_definition.true_value = None
    with self.assertRaises(errors.FormatError):
      data_maps.BooleanMap(data_type_definition)

  def testGetStructFormatString(self):
    """Tests the GetStructFormatString function."""
    definitions_file = self._GetTestFilePath(['definitions', 'booleans.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)

    data_type_definition = definitions_registry.GetDefinitionByName('bool8')
    data_type_map = data_maps.BooleanMap(data_type_definition)
    struct_format_string = data_type_map.GetStructFormatString()
    self.assertEqual(struct_format_string, 'B')

    data_type_definition = definitions_registry.GetDefinitionByName('bool16')
    data_type_map = data_maps.BooleanMap(data_type_definition)
    struct_format_string = data_type_map.GetStructFormatString()
    self.assertEqual(struct_format_string, 'H')

    data_type_definition = definitions_registry.GetDefinitionByName('bool32')
    data_type_map = data_maps.BooleanMap(data_type_definition)
    struct_format_string = data_type_map.GetStructFormatString()
    self.assertEqual(struct_format_string, 'I')

  def testFoldByteStream(self):
    """Tests the FoldByteStream function."""
    definitions_file = self._GetTestFilePath(['definitions', 'booleans.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)

    data_type_definition = definitions_registry.GetDefinitionByName('bool8')
    data_type_definition.byte_order = definitions.BYTE_ORDER_LITTLE_ENDIAN
    data_type_map = data_maps.BooleanMap(data_type_definition)
    data_type_definition.false_value = 0
    data_type_definition.true_value = 1

    byte_stream = data_type_map.FoldByteStream(False)
    self.assertEqual(byte_stream, b'\x00')

    byte_stream = data_type_map.FoldByteStream(True)
    self.assertEqual(byte_stream, b'\x01')

    with self.assertRaises(errors.FoldingError):
      data_type_map.FoldByteStream(None)

    data_type_definition = definitions_registry.GetDefinitionByName('bool16')
    data_type_definition.byte_order = definitions.BYTE_ORDER_LITTLE_ENDIAN
    data_type_definition.false_value = 0xffff
    data_type_definition.true_value = 1
    data_type_map = data_maps.BooleanMap(data_type_definition)

    byte_stream = data_type_map.FoldByteStream(False)
    self.assertEqual(byte_stream, b'\xff\xff')

    byte_stream = data_type_map.FoldByteStream(True)
    self.assertEqual(byte_stream, b'\x01\x00')

    data_type_definition = definitions_registry.GetDefinitionByName('bool32')
    data_type_definition.byte_order = definitions.BYTE_ORDER_LITTLE_ENDIAN
    data_type_definition.false_value = 0
    data_type_definition.true_value = None
    data_type_map = data_maps.BooleanMap(data_type_definition)

    byte_stream = data_type_map.FoldByteStream(False)
    self.assertEqual(byte_stream, b'\x00\x00\x00\x00')

    with self.assertRaises(errors.FoldingError):
      data_type_map.FoldByteStream(True)

  def testMapByteStream(self):
    """Tests the MapByteStream function."""
    definitions_file = self._GetTestFilePath(['definitions', 'booleans.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)

    data_type_definition = definitions_registry.GetDefinitionByName('bool8')
    data_type_definition.byte_order = definitions.BYTE_ORDER_LITTLE_ENDIAN
    data_type_map = data_maps.BooleanMap(data_type_definition)
    data_type_definition.true_value = 1

    bool_value = data_type_map.MapByteStream(b'\x00')
    self.assertFalse(bool_value)

    bool_value = data_type_map.MapByteStream(b'\x01')
    self.assertTrue(bool_value)

    with self.assertRaises(errors.MappingError):
      data_type_map.MapByteStream(b'\xff')

    data_type_definition = definitions_registry.GetDefinitionByName('bool16')
    data_type_definition.byte_order = definitions.BYTE_ORDER_LITTLE_ENDIAN
    data_type_definition.false_value = None
    data_type_definition.true_value = 1
    data_type_map = data_maps.BooleanMap(data_type_definition)

    bool_value = data_type_map.MapByteStream(b'\xff\xff')
    self.assertFalse(bool_value)

    bool_value = data_type_map.MapByteStream(b'\x01\x00')
    self.assertTrue(bool_value)

    data_type_definition = definitions_registry.GetDefinitionByName('bool32')
    data_type_definition.byte_order = definitions.BYTE_ORDER_LITTLE_ENDIAN
    data_type_definition.true_value = None
    data_type_map = data_maps.BooleanMap(data_type_definition)

    bool_value = data_type_map.MapByteStream(b'\x00\x00\x00\x00')
    self.assertFalse(bool_value)

    bool_value = data_type_map.MapByteStream(b'\xff\xff\xff\xff')
    self.assertTrue(bool_value)

    with self.assertRaises(errors.ByteStreamTooSmallError):
      data_type_map.MapByteStream(b'\x01\x00')


@test_lib.skipUnlessHasTestFile(['definitions', 'characters.yaml'])
class CharacterMapTest(test_lib.BaseTestCase):
  """Character map tests."""

  def testGetStructFormatString(self):
    """Tests the GetStructFormatString function."""
    definitions_file = self._GetTestFilePath([
        'definitions', 'characters.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)

    data_type_definition = definitions_registry.GetDefinitionByName('char')
    data_type_map = data_maps.CharacterMap(data_type_definition)
    struct_format_string = data_type_map.GetStructFormatString()
    self.assertEqual(struct_format_string, 'b')

    data_type_definition = definitions_registry.GetDefinitionByName('wchar16')
    data_type_map = data_maps.CharacterMap(data_type_definition)
    struct_format_string = data_type_map.GetStructFormatString()
    self.assertEqual(struct_format_string, 'h')

    data_type_definition = definitions_registry.GetDefinitionByName('wchar32')
    data_type_map = data_maps.CharacterMap(data_type_definition)
    struct_format_string = data_type_map.GetStructFormatString()
    self.assertEqual(struct_format_string, 'i')

  def testFoldByteStream(self):
    """Tests the FoldByteStream function."""
    definitions_file = self._GetTestFilePath([
        'definitions', 'characters.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)

    data_type_definition = definitions_registry.GetDefinitionByName('char')
    data_type_definition.byte_order = definitions.BYTE_ORDER_LITTLE_ENDIAN
    data_type_map = data_maps.CharacterMap(data_type_definition)

    byte_stream = data_type_map.FoldByteStream('A')
    self.assertEqual(byte_stream, b'\x41')

    data_type_definition = definitions_registry.GetDefinitionByName('wchar16')
    data_type_definition.byte_order = definitions.BYTE_ORDER_LITTLE_ENDIAN
    data_type_map = data_maps.CharacterMap(data_type_definition)

    byte_stream = data_type_map.FoldByteStream('\u24b6')
    self.assertEqual(byte_stream, b'\xb6\x24')

    data_type_definition = definitions_registry.GetDefinitionByName('wchar32')
    data_type_definition.byte_order = definitions.BYTE_ORDER_LITTLE_ENDIAN
    data_type_map = data_maps.CharacterMap(data_type_definition)

    byte_stream = data_type_map.FoldByteStream('\u24b6')
    self.assertEqual(byte_stream, b'\xb6\x24\x00\x00')

  def testMapByteStream(self):
    """Tests the MapByteStream function."""
    definitions_file = self._GetTestFilePath([
        'definitions', 'characters.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)

    data_type_definition = definitions_registry.GetDefinitionByName('char')
    data_type_definition.byte_order = definitions.BYTE_ORDER_LITTLE_ENDIAN
    data_type_map = data_maps.CharacterMap(data_type_definition)

    string_value = data_type_map.MapByteStream(b'\x41')
    self.assertEqual(string_value, 'A')

    data_type_definition = definitions_registry.GetDefinitionByName('wchar16')
    data_type_definition.byte_order = definitions.BYTE_ORDER_LITTLE_ENDIAN
    data_type_map = data_maps.CharacterMap(data_type_definition)

    string_value = data_type_map.MapByteStream(b'\xb6\x24')
    self.assertEqual(string_value, '\u24b6')

    data_type_definition = definitions_registry.GetDefinitionByName('wchar32')
    data_type_definition.byte_order = definitions.BYTE_ORDER_LITTLE_ENDIAN
    data_type_map = data_maps.CharacterMap(data_type_definition)

    string_value = data_type_map.MapByteStream(b'\xb6\x24\x00\x00')
    self.assertEqual(string_value, '\u24b6')

    with self.assertRaises(errors.ByteStreamTooSmallError):
      data_type_map.MapByteStream(b'\xb6\x24')


@test_lib.skipUnlessHasTestFile(['definitions', 'floating-points.yaml'])
class FloatingPointMapTest(test_lib.BaseTestCase):
  """Floating-point map tests."""

  def testGetStructFormatString(self):
    """Tests the GetStructFormatString function."""
    definitions_file = self._GetTestFilePath([
        'definitions', 'floating-points.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)

    data_type_definition = definitions_registry.GetDefinitionByName('float32')
    data_type_map = data_maps.FloatingPointMap(data_type_definition)
    struct_format_string = data_type_map.GetStructFormatString()
    self.assertEqual(struct_format_string, 'f')

    data_type_definition = definitions_registry.GetDefinitionByName('float64')
    data_type_map = data_maps.FloatingPointMap(data_type_definition)
    struct_format_string = data_type_map.GetStructFormatString()
    self.assertEqual(struct_format_string, 'd')

  def testFoldByteStream(self):
    """Tests the FoldByteStream function."""
    definitions_file = self._GetTestFilePath([
        'definitions', 'floating-points.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)

    data_type_definition = definitions_registry.GetDefinitionByName('float32')
    data_type_definition.byte_order = definitions.BYTE_ORDER_LITTLE_ENDIAN
    data_type_map = data_maps.FloatingPointMap(data_type_definition)

    byte_stream = data_type_map.FoldByteStream(12.34000015258789)
    self.assertEqual(byte_stream, b'\xa4\x70\x45\x41')

    data_type_definition = definitions_registry.GetDefinitionByName('float64')
    data_type_definition.byte_order = definitions.BYTE_ORDER_LITTLE_ENDIAN
    data_type_map = data_maps.FloatingPointMap(data_type_definition)

    byte_stream = data_type_map.FoldByteStream(12.34)
    self.assertEqual(byte_stream, b'\xae\x47\xe1\x7a\x14\xae\x28\x40')

  def testMapByteStream(self):
    """Tests the MapByteStream function."""
    definitions_file = self._GetTestFilePath([
        'definitions', 'floating-points.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)

    data_type_definition = definitions_registry.GetDefinitionByName('float32')
    data_type_definition.byte_order = definitions.BYTE_ORDER_LITTLE_ENDIAN
    data_type_map = data_maps.FloatingPointMap(data_type_definition)

    float_value = data_type_map.MapByteStream(b'\xa4\x70\x45\x41')
    self.assertEqual(float_value, 12.34000015258789)

    data_type_definition = definitions_registry.GetDefinitionByName('float64')
    data_type_definition.byte_order = definitions.BYTE_ORDER_LITTLE_ENDIAN
    data_type_map = data_maps.FloatingPointMap(data_type_definition)

    float_value = data_type_map.MapByteStream(
        b'\xae\x47\xe1\x7a\x14\xae\x28\x40')
    self.assertEqual(float_value, 12.34)

    with self.assertRaises(errors.ByteStreamTooSmallError):
      data_type_map.MapByteStream(b'\xa4\x70\x45\x41')


class IntegerMapTest(test_lib.BaseTestCase):
  """Integer map tests."""

  # pylint: disable=protected-access

  @test_lib.skipUnlessHasTestFile(['integer.yaml'])
  def testGetByteStreamOperation(self):
    """Tests the _GetByteStreamOperation function."""
    definitions_file = self._GetTestFilePath(['integer.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)

    data_type_definition = definitions_registry.GetDefinitionByName('int32le')
    data_type_map = data_maps.IntegerMap(data_type_definition)
    map_operation = data_type_map._GetByteStreamOperation()
    self.assertIsInstance(map_operation, byte_operations.StructOperation)

  @test_lib.skipUnlessHasTestFile(['definitions', 'integers.yaml'])
  def testGetStructFormatString(self):
    """Tests the GetStructFormatString function."""
    definitions_file = self._GetTestFilePath(['definitions', 'integers.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)

    data_type_definition = definitions_registry.GetDefinitionByName('int8')
    data_type_map = data_maps.IntegerMap(data_type_definition)
    struct_format_string = data_type_map.GetStructFormatString()
    self.assertEqual(struct_format_string, 'b')

    data_type_definition = definitions_registry.GetDefinitionByName('int16')
    data_type_map = data_maps.IntegerMap(data_type_definition)
    struct_format_string = data_type_map.GetStructFormatString()
    self.assertEqual(struct_format_string, 'h')

    data_type_definition = definitions_registry.GetDefinitionByName('int32')
    data_type_map = data_maps.IntegerMap(data_type_definition)
    struct_format_string = data_type_map.GetStructFormatString()
    self.assertEqual(struct_format_string, 'i')

    data_type_definition = definitions_registry.GetDefinitionByName('int64')
    data_type_map = data_maps.IntegerMap(data_type_definition)
    struct_format_string = data_type_map.GetStructFormatString()
    self.assertEqual(struct_format_string, 'q')

    data_type_definition = definitions_registry.GetDefinitionByName('uint8')
    data_type_map = data_maps.IntegerMap(data_type_definition)
    struct_format_string = data_type_map.GetStructFormatString()
    self.assertEqual(struct_format_string, 'B')

    data_type_definition = definitions_registry.GetDefinitionByName('uint16')
    data_type_map = data_maps.IntegerMap(data_type_definition)
    struct_format_string = data_type_map.GetStructFormatString()
    self.assertEqual(struct_format_string, 'H')

    data_type_definition = definitions_registry.GetDefinitionByName('uint32')
    data_type_map = data_maps.IntegerMap(data_type_definition)
    struct_format_string = data_type_map.GetStructFormatString()
    self.assertEqual(struct_format_string, 'I')

    data_type_definition = definitions_registry.GetDefinitionByName('uint64')
    data_type_map = data_maps.IntegerMap(data_type_definition)
    struct_format_string = data_type_map.GetStructFormatString()
    self.assertEqual(struct_format_string, 'Q')

  def testFoldByteStream(self):
    """Tests the FoldByteStream function."""
    definitions_file = self._GetTestFilePath(['definitions', 'integers.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)

    data_type_definition = definitions_registry.GetDefinitionByName('uint8')
    data_type_definition.byte_order = definitions.BYTE_ORDER_LITTLE_ENDIAN
    data_type_map = data_maps.IntegerMap(data_type_definition)

    byte_stream = data_type_map.FoldByteStream(0x12)
    self.assertEqual(byte_stream, b'\x12')

    data_type_definition = definitions_registry.GetDefinitionByName('uint16')
    data_type_definition.byte_order = definitions.BYTE_ORDER_LITTLE_ENDIAN
    data_type_map = data_maps.IntegerMap(data_type_definition)

    byte_stream = data_type_map.FoldByteStream(0x3412)
    self.assertEqual(byte_stream, b'\x12\x34')

    data_type_definition = definitions_registry.GetDefinitionByName('uint32')
    data_type_definition.byte_order = definitions.BYTE_ORDER_LITTLE_ENDIAN
    data_type_map = data_maps.IntegerMap(data_type_definition)

    byte_stream = data_type_map.FoldByteStream(0x78563412)
    self.assertEqual(byte_stream, b'\x12\x34\x56\x78')

    data_type_definition = definitions_registry.GetDefinitionByName('uint32')
    data_type_definition.byte_order = definitions.BYTE_ORDER_BIG_ENDIAN
    data_type_map = data_maps.IntegerMap(data_type_definition)

    byte_stream = data_type_map.FoldByteStream(0x12345678)
    self.assertEqual(byte_stream, b'\x12\x34\x56\x78')

    data_type_definition = definitions_registry.GetDefinitionByName('uint64')
    data_type_definition.byte_order = definitions.BYTE_ORDER_LITTLE_ENDIAN
    data_type_map = data_maps.IntegerMap(data_type_definition)

    byte_stream = data_type_map.FoldByteStream(0xf0debc9a78563412)
    self.assertEqual(byte_stream, b'\x12\x34\x56\x78\x9a\xbc\xde\xf0')

  @test_lib.skipUnlessHasTestFile(['definitions', 'integers.yaml'])
  def testMapByteStream(self):
    """Tests the MapByteStream function."""
    definitions_file = self._GetTestFilePath(['definitions', 'integers.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)

    data_type_definition = definitions_registry.GetDefinitionByName('uint8')
    data_type_definition.byte_order = definitions.BYTE_ORDER_LITTLE_ENDIAN
    data_type_map = data_maps.IntegerMap(data_type_definition)

    integer_value = data_type_map.MapByteStream(b'\x12')
    self.assertEqual(integer_value, 0x12)

    data_type_definition = definitions_registry.GetDefinitionByName('uint16')
    data_type_definition.byte_order = definitions.BYTE_ORDER_LITTLE_ENDIAN
    data_type_map = data_maps.IntegerMap(data_type_definition)

    integer_value = data_type_map.MapByteStream(b'\x12\x34')
    self.assertEqual(integer_value, 0x3412)

    data_type_definition = definitions_registry.GetDefinitionByName('uint32')
    data_type_definition.byte_order = definitions.BYTE_ORDER_LITTLE_ENDIAN
    data_type_map = data_maps.IntegerMap(data_type_definition)

    integer_value = data_type_map.MapByteStream(b'\x12\x34\x56\x78')
    self.assertEqual(integer_value, 0x78563412)

    data_type_definition = definitions_registry.GetDefinitionByName('uint32')
    data_type_definition.byte_order = definitions.BYTE_ORDER_BIG_ENDIAN
    data_type_map = data_maps.IntegerMap(data_type_definition)

    integer_value = data_type_map.MapByteStream(b'\x12\x34\x56\x78')
    self.assertEqual(integer_value, 0x12345678)

    data_type_definition = definitions_registry.GetDefinitionByName('uint64')
    data_type_definition.byte_order = definitions.BYTE_ORDER_LITTLE_ENDIAN
    data_type_map = data_maps.IntegerMap(data_type_definition)

    integer_value = data_type_map.MapByteStream(
        b'\x12\x34\x56\x78\x9a\xbc\xde\xf0')
    self.assertEqual(integer_value, 0xf0debc9a78563412)

    with self.assertRaises(errors.ByteStreamTooSmallError):
      data_type_map.MapByteStream(b'\x12\x34\x56\x78')


@test_lib.skipUnlessHasTestFile(['uuid.yaml'])
class UUIDMapTest(test_lib.BaseTestCase):
  """UUID map tests."""

  def testFoldByteStream(self):
    """Tests the FoldByteStream function."""
    definitions_file = self._GetTestFilePath(['uuid.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)

    data_type_definition = definitions_registry.GetDefinitionByName('uuid')
    data_type_definition.byte_order = definitions.BYTE_ORDER_LITTLE_ENDIAN
    data_type_map = data_maps.UUIDMap(data_type_definition)

    uuid_value = uuid.UUID('{00021401-0000-0000-c000-000000000046}')
    byte_stream = data_type_map.FoldByteStream(uuid_value)
    expected_byte_stream = (
        b'\x01\x14\x02\x00\x00\x00\x00\x00\xc0\x00\x00\x00\x00\x00\x00\x46')
    self.assertEqual(byte_stream, expected_byte_stream)

  def testMapByteStream(self):
    """Tests the MapByteStream function."""
    definitions_file = self._GetTestFilePath(['uuid.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)

    data_type_definition = definitions_registry.GetDefinitionByName('uuid')
    data_type_definition.byte_order = definitions.BYTE_ORDER_LITTLE_ENDIAN
    data_type_map = data_maps.UUIDMap(data_type_definition)

    expected_uuid_value = uuid.UUID('{00021401-0000-0000-c000-000000000046}')
    uuid_value = data_type_map.MapByteStream(
        b'\x01\x14\x02\x00\x00\x00\x00\x00\xc0\x00\x00\x00\x00\x00\x00\x46')
    self.assertEqual(uuid_value, expected_uuid_value)


@test_lib.skipUnlessHasTestFile(['sequence.yaml'])
class ElementSequenceDataTypeMapTest(test_lib.BaseTestCase):
  """Element sequence data type map tests."""

  # pylint: disable=protected-access

  def testInitialize(self):
    """Tests the __init__ function."""
    definitions_file = self._GetTestFilePath(['sequence.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)
    data_type_definition = definitions_registry.GetDefinitionByName('vector4')

    data_type_map = data_maps.ElementSequenceDataTypeMap(data_type_definition)
    self.assertIsNotNone(data_type_map)

  # TODO: add tests for _EvaluateElementsDataSize.
  # TODO: add tests for _EvaluateNumberOfElements.

  def testGetElementDataTypeDefinition(self):
    """Tests the _GetElementDataTypeDefinition function."""
    definitions_file = self._GetTestFilePath(['sequence.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)
    data_type_definition = definitions_registry.GetDefinitionByName('vector4')

    data_type_map = data_maps.ElementSequenceDataTypeMap(data_type_definition)

    element_data_type_definition = data_type_map._GetElementDataTypeDefinition(
        data_type_definition)
    self.assertIsNotNone(element_data_type_definition)

    with self.assertRaises(errors.FormatError):
      data_type_map._GetElementDataTypeDefinition(None)

    with self.assertRaises(errors.FormatError):
      data_type_definition = EmptyDataTypeDefinition('empty')
      data_type_map._GetElementDataTypeDefinition(data_type_definition)

  # TODO: add tests for GetSizeHint.

  def testGetStructByteOrderString(self):
    """Tests the GetStructByteOrderString function."""
    definitions_file = self._GetTestFilePath(['sequence.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)

    data_type_definition = definitions_registry.GetDefinitionByName('vector4')
    data_type_map = data_maps.ElementSequenceDataTypeMap(data_type_definition)
    byte_order_string = data_type_map.GetStructByteOrderString()
    self.assertEqual(byte_order_string, '<')


@test_lib.skipUnlessHasTestFile(['sequence.yaml'])
class SequenceMapTest(test_lib.BaseTestCase):
  """Sequence map tests."""

  # pylint: disable=protected-access

  def testInitialize(self):
    """Tests the __init__ function."""
    definitions_file = self._GetTestFilePath(['sequence.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)
    data_type_definition = definitions_registry.GetDefinitionByName('vector4')

    data_type_map = data_maps.SequenceMap(data_type_definition)
    self.assertIsNotNone(data_type_map)

  # TODO: add tests for _CompositeFoldByteStream.

  def testCompositeMapByteStream(self):
    """Tests the _CompositeMapByteStream function."""
    definitions_file = self._GetTestFilePath(['sequence.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)
    data_type_definition = definitions_registry.GetDefinitionByName(
        'triangle4')

    data_type_map = data_maps.SequenceMap(data_type_definition)

    byte_values = []
    for value in range(1, 13):
      byte_value_upper, byte_value_lower = divmod(value, 256)
      byte_values.extend([byte_value_lower, byte_value_upper, 0, 0])

    byte_stream = bytes(bytearray(byte_values))

    sequence_value = data_type_map._CompositeMapByteStream(byte_stream)
    self.assertEqual(
        sequence_value, ((1, 2, 3, 4), (5, 6, 7, 8), (9, 10, 11, 12)))

    with self.assertRaises(errors.MappingError):
      data_type_map._CompositeMapByteStream(None)

    with self.assertRaises(errors.ByteStreamTooSmallError):
      data_type_map._CompositeMapByteStream(b'\x12\x34\x56')

  def testLinearFoldByteStream(self):
    """Tests the _LinearFoldByteStream function."""
    definitions_file = self._GetTestFilePath(['sequence.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)
    data_type_definition = definitions_registry.GetDefinitionByName('vector4')

    data_type_map = data_maps.SequenceMap(data_type_definition)

    byte_stream = data_type_map._LinearFoldByteStream((1, 2, 3, 4))
    expected_sequence_value = (
        b'\x01\x00\x00\x00\x02\x00\x00\x00\x03\x00\x00\x00\x04\x00\x00\x00')
    self.assertEqual(byte_stream, expected_sequence_value)

  def testLinearMapByteStream(self):
    """Tests the _LinearMapByteStream function."""
    definitions_file = self._GetTestFilePath(['sequence.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)
    data_type_definition = definitions_registry.GetDefinitionByName('vector4')

    data_type_map = data_maps.SequenceMap(data_type_definition)

    sequence_value = data_type_map._LinearMapByteStream(
        b'\x01\x00\x00\x00\x02\x00\x00\x00\x03\x00\x00\x00\x04\x00\x00\x00')
    self.assertEqual(sequence_value, (1, 2, 3, 4))

    with self.assertRaises(errors.MappingError):
      data_type_map._LinearMapByteStream(None)

    with self.assertRaises(errors.ByteStreamTooSmallError):
      data_type_map._LinearMapByteStream(b'\x12\x34\x56')

  def testFoldByteStream(self):
    """Tests the FoldByteStream function."""
    definitions_file = self._GetTestFilePath(['sequence.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)
    data_type_definition = definitions_registry.GetDefinitionByName('vector4')

    data_type_map = data_maps.SequenceMap(data_type_definition)

    byte_stream = data_type_map.FoldByteStream((1, 2, 3, 4))
    expected_sequence_value = (
        b'\x01\x00\x00\x00\x02\x00\x00\x00\x03\x00\x00\x00\x04\x00\x00\x00')
    self.assertEqual(byte_stream, expected_sequence_value)

  def testGetStructFormatString(self):
    """Tests the GetStructFormatString function."""
    definitions_file = self._GetTestFilePath(['sequence.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)

    data_type_definition = definitions_registry.GetDefinitionByName('vector4')
    data_type_map = data_maps.SequenceMap(data_type_definition)
    struct_format_string = data_type_map.GetStructFormatString()
    self.assertEqual(struct_format_string, '4i')

    data_type_definition.elements_data_size = 16
    data_type_definition.number_of_elements = 0
    data_type_map = data_maps.SequenceMap(data_type_definition)
    struct_format_string = data_type_map.GetStructFormatString()
    self.assertEqual(struct_format_string, '4i')

    data_type_definition.elements_data_size = 0
    data_type_definition.number_of_elements = 0
    data_type_map = data_maps.SequenceMap(data_type_definition)
    struct_format_string = data_type_map.GetStructFormatString()
    self.assertIsNone(struct_format_string)

  def testMapByteStream(self):
    """Tests the MapByteStream function."""
    definitions_file = self._GetTestFilePath(['sequence.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)
    data_type_definition = definitions_registry.GetDefinitionByName('vector4')

    data_type_map = data_maps.SequenceMap(data_type_definition)

    sequence_value = data_type_map.MapByteStream(
        b'\x01\x00\x00\x00\x02\x00\x00\x00\x03\x00\x00\x00\x04\x00\x00\x00')
    self.assertEqual(sequence_value, (1, 2, 3, 4))


@test_lib.skipUnlessHasTestFile(['stream.yaml'])
class StreamMapTest(test_lib.BaseTestCase):
  """Stream map tests."""

  # pylint: disable=protected-access

  def testInitialize(self):
    """Tests the __init__ function."""
    definitions_file = self._GetTestFilePath(['stream.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)
    data_type_definition = definitions_registry.GetDefinitionByName(
        'utf16le_stream')

    data_type_map = data_maps.StreamMap(data_type_definition)
    self.assertIsNotNone(data_type_map)

  # TODO: add tests for _CompositeFoldByteStream.
  # TODO: add tests for _CompositeMapByteStream.
  # TODO: add tests for _LinearFoldByteStream.

  def testLinearMapByteStream(self):
    """Tests the _LinearMapByteStream function."""
    definitions_file = self._GetTestFilePath(['stream.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)
    data_type_definition = definitions_registry.GetDefinitionByName(
        'utf16le_stream')

    data_type_map = data_maps.StreamMap(data_type_definition)

    byte_stream = 'dtFabric'.encode('utf-16-le')
    stream_value = data_type_map._LinearMapByteStream(byte_stream)
    self.assertEqual(stream_value, b'd\x00t\x00F\x00a\x00b\x00r\x00i\x00c\x00')

    with self.assertRaises(errors.MappingError):
      data_type_map._LinearMapByteStream(None)

    with self.assertRaises(errors.ByteStreamTooSmallError):
      data_type_map._LinearMapByteStream(b'\x12\x34\x56')

  def testFoldByteStream(self):
    """Tests the FoldByteStream function."""
    definitions_file = self._GetTestFilePath(['stream.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)
    data_type_definition = definitions_registry.GetDefinitionByName(
        'utf16le_stream')

    data_type_map = data_maps.StreamMap(data_type_definition)

    exptected_byte_stream = b'd\x00t\x00F\x00a\x00b\x00r\x00i\x00c\x00'
    byte_stream = data_type_map.FoldByteStream(exptected_byte_stream)
    self.assertEqual(byte_stream, exptected_byte_stream)

  def testGetStructFormatString(self):
    """Tests the GetStructFormatString function."""
    definitions_file = self._GetTestFilePath(['stream.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)

    data_type_definition = definitions_registry.GetDefinitionByName(
        'utf16le_stream')
    data_type_map = data_maps.StreamMap(data_type_definition)
    struct_format_string = data_type_map.GetStructFormatString()
    self.assertEqual(struct_format_string, '16B')

    data_type_definition.elements_data_size = 16
    data_type_definition.number_of_elements = 0
    data_type_map = data_maps.StreamMap(data_type_definition)
    struct_format_string = data_type_map.GetStructFormatString()
    self.assertEqual(struct_format_string, '16B')

    data_type_definition.elements_data_size = 0
    data_type_definition.number_of_elements = 0
    data_type_map = data_maps.StreamMap(data_type_definition)
    struct_format_string = data_type_map.GetStructFormatString()
    self.assertIsNone(struct_format_string)

  def testMapByteStream(self):
    """Tests the MapByteStream function."""
    definitions_file = self._GetTestFilePath(['stream.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)
    data_type_definition = definitions_registry.GetDefinitionByName(
        'utf16le_stream')

    data_type_map = data_maps.StreamMap(data_type_definition)

    byte_stream = 'dtFabric'.encode('utf-16-le')
    stream_value = data_type_map.MapByteStream(byte_stream)
    self.assertEqual(stream_value, b'd\x00t\x00F\x00a\x00b\x00r\x00i\x00c\x00')


@test_lib.skipUnlessHasTestFile(['string.yaml'])
class StringMapTest(test_lib.BaseTestCase):
  """String map tests."""

  def testFoldByteStream(self):
    """Tests the FoldByteStream function."""
    definitions_file = self._GetTestFilePath(['string.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)

    data_type_definition = definitions_registry.GetDefinitionByName(
        'utf16_string')
    data_type_map = data_maps.StringMap(data_type_definition)

    expected_byte_stream = 'dtFabric'.encode('utf-16-le')
    byte_stream = data_type_map.FoldByteStream('dtFabric')
    self.assertEqual(byte_stream, expected_byte_stream)

  def testGetStructFormatString(self):
    """Tests the GetStructFormatString function."""
    definitions_file = self._GetTestFilePath(['string.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)

    data_type_definition = definitions_registry.GetDefinitionByName(
        'utf16_string')
    data_type_map = data_maps.StreamMap(data_type_definition)
    struct_format_string = data_type_map.GetStructFormatString()
    self.assertEqual(struct_format_string, '16B')

    data_type_definition.elements_data_size = 16
    data_type_definition.number_of_elements = 0
    data_type_map = data_maps.StringMap(data_type_definition)
    struct_format_string = data_type_map.GetStructFormatString()
    self.assertEqual(struct_format_string, '16B')

    data_type_definition.elements_data_size = 0
    data_type_definition.number_of_elements = 0
    data_type_map = data_maps.StringMap(data_type_definition)
    struct_format_string = data_type_map.GetStructFormatString()
    self.assertIsNone(struct_format_string)

  def testMapByteStream(self):
    """Tests the MapByteStream function."""
    definitions_file = self._GetTestFilePath(['string.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)

    data_type_definition = definitions_registry.GetDefinitionByName(
        'utf16_string')
    data_type_map = data_maps.StringMap(data_type_definition)

    byte_stream = 'dtFabric'.encode('utf-16-le')
    string_value = data_type_map.MapByteStream(byte_stream)
    self.assertEqual(string_value, 'dtFabric')

    with self.assertRaises(errors.MappingError):
      data_type_map.MapByteStream(None)

    with self.assertRaises(errors.ByteStreamTooSmallError):
      data_type_map.MapByteStream(b'\x12\x34\x56')

    data_type_definition = definitions_registry.GetDefinitionByName(
        'utf8_string')
    data_type_map = data_maps.StringMap(data_type_definition)

    byte_stream = 'dtFabric\x00and more'.encode('utf8')
    string_value = data_type_map.MapByteStream(byte_stream)
    self.assertEqual(string_value, 'dtFabric\x00')

    with self.assertRaises(errors.ByteStreamTooSmallError):
      data_type_map.MapByteStream(byte_stream[:7])


class StructureMapTest(test_lib.BaseTestCase):
  """Structure map tests."""

  # pylint: disable=protected-access

  @test_lib.skipUnlessHasTestFile(['structure.yaml'])
  def testInitialize(self):
    """Tests the __init__ function."""
    definitions_file = self._GetTestFilePath(['structure.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)

    data_type_definition = definitions_registry.GetDefinitionByName('point3d')
    data_type_map = data_maps.StructureMap(data_type_definition)
    self.assertIsNotNone(data_type_map)

  @test_lib.skipUnlessHasTestFile(['structure.yaml'])
  def testCheckCompositeMap(self):
    """Tests the _CheckCompositeMap function."""
    definitions_file = self._GetTestFilePath(['structure.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)

    data_type_definition = definitions_registry.GetDefinitionByName('point3d')
    data_type_map = data_maps.StructureMap(data_type_definition)

    result = data_type_map._CheckCompositeMap(data_type_definition)
    self.assertFalse(result)

    with self.assertRaises(errors.FormatError):
      data_type_map._CheckCompositeMap(None)

    with self.assertRaises(errors.FormatError):
      data_type_definition = EmptyDataTypeDefinition('empty')
      data_type_map._CheckCompositeMap(data_type_definition)

    data_type_definition = definitions_registry.GetDefinitionByName(
        'triangle3d')
    data_type_map = data_maps.StructureMap(data_type_definition)

    result = data_type_map._CheckCompositeMap(data_type_definition)
    self.assertTrue(result)

    data_type_definition = definitions_registry.GetDefinitionByName('box3d')
    data_type_map = data_maps.StructureMap(data_type_definition)

    result = data_type_map._CheckCompositeMap(data_type_definition)
    self.assertTrue(result)

    data_type_definition = definitions_registry.GetDefinitionByName(
        'sphere3d')
    data_type_map = data_maps.StructureMap(data_type_definition)

    result = data_type_map._CheckCompositeMap(data_type_definition)
    self.assertTrue(result)

  # TODO: add tests for _CompositeFoldByteStream.
  # TODO: add tests for _CompositeMapByteStream.

  @test_lib.skipUnlessHasTestFile(['structure.yaml'])
  def testGetAttributeNames(self):
    """Tests the _GetAttributeNames function."""
    definitions_file = self._GetTestFilePath(['structure.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)
    data_type_definition = definitions_registry.GetDefinitionByName('point3d')

    data_type_map = data_maps.StructureMap(data_type_definition)
    attribute_names = data_type_map._GetAttributeNames(data_type_definition)
    self.assertEqual(attribute_names, ['x', 'y', 'z'])

    with self.assertRaises(errors.FormatError):
      data_type_map._GetAttributeNames(None)

  @test_lib.skipUnlessHasTestFile(['structure.yaml'])
  def testGetMemberDataTypeMaps(self):
    """Tests the _GetMemberDataTypeMaps function."""
    definitions_file = self._GetTestFilePath(['structure.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)
    data_type_definition = definitions_registry.GetDefinitionByName('point3d')

    data_type_map = data_maps.StructureMap(data_type_definition)

    members_data_type_maps = data_type_map._GetMemberDataTypeMaps(
        data_type_definition, {})
    self.assertIsNotNone(members_data_type_maps)

    with self.assertRaises(errors.FormatError):
      data_type_map._GetMemberDataTypeMaps(None, {})

    with self.assertRaises(errors.FormatError):
      data_type_definition = EmptyDataTypeDefinition('empty')
      data_type_map._GetMemberDataTypeMaps(data_type_definition, {})

  @test_lib.skipUnlessHasTestFile(['structure.yaml'])
  def testLinearFoldByteStream(self):
    """Tests the _LinearFoldByteStream function."""
    definitions_file = self._GetTestFilePath(['structure.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)

    data_type_definition = definitions_registry.GetDefinitionByName('point3d')
    data_type_map = data_maps.StructureMap(data_type_definition)

    byte_values = []
    for value in range(1, 4):
      byte_value_upper, byte_value_lower = divmod(value, 256)
      byte_values.extend([byte_value_lower, byte_value_upper, 0, 0])

    point3d = data_type_map.CreateStructureValues(x=1, y=2, z=3)

    expected_byte_stream = bytes(bytearray(byte_values))
    byte_stream = data_type_map._LinearFoldByteStream(point3d)
    self.assertEqual(byte_stream, expected_byte_stream)

  @test_lib.skipUnlessHasTestFile(['structure.yaml'])
  def testLinearMapByteStream(self):
    """Tests the _LinearMapByteStream function."""
    definitions_file = self._GetTestFilePath(['structure.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)

    data_type_definition = definitions_registry.GetDefinitionByName('point3d')
    data_type_map = data_maps.StructureMap(data_type_definition)

    byte_values = []
    for value in range(1, 4):
      byte_value_upper, byte_value_lower = divmod(value, 256)
      byte_values.extend([byte_value_lower, byte_value_upper, 0, 0])

    byte_stream = bytes(bytearray(byte_values))

    point3d = data_type_map._LinearMapByteStream(byte_stream)
    self.assertEqual(point3d.x, 1)
    self.assertEqual(point3d.y, 2)
    self.assertEqual(point3d.z, 3)

    data_type_definition = definitions_registry.GetDefinitionByName('point3d')
    data_type_definition.byte_order = definitions.BYTE_ORDER_BIG_ENDIAN
    data_type_map = data_maps.StructureMap(data_type_definition)

    point3d = data_type_map._LinearMapByteStream(byte_stream)
    self.assertEqual(point3d.x, 0x01000000)
    self.assertEqual(point3d.y, 0x02000000)
    self.assertEqual(point3d.z, 0x03000000)

  # TODO: add tests for CreateStructureValues.

  def testGetStructFormatString(self):
    """Tests the GetStructFormatString function."""
    definitions_file = self._GetTestFilePath(['structure.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)

    data_type_definition = definitions_registry.GetDefinitionByName('point3d')
    data_type_map = data_maps.StructureMap(data_type_definition)
    struct_format_string = data_type_map.GetStructFormatString()
    self.assertEqual(struct_format_string, 'iii')

    # Test with member without a struct format string.

    data_type_definition = data_types.StructureDefinition(
        'my_struct_type', aliases=['MY_STRUCT_TYPE'],
        description='my structure type')

    member_definition = TestDataTypeDefinition('test')

    structure_member_definition = data_types.MemberDataTypeDefinition(
        'my_struct_member', member_definition, aliases=['MY_STRUCT_MEMBER'],
        data_type='test', description='my structure member')

    data_type_definition.AddMemberDefinition(structure_member_definition)

    data_type_map = data_maps.StructureMap(data_type_definition)
    struct_format_string = data_type_map.GetStructFormatString()
    self.assertIsNone(struct_format_string)

  @test_lib.skipUnlessHasTestFile(['structure.yaml'])
  def testMapByteStream(self):
    """Tests the MapByteStream function."""
    definitions_file = self._GetTestFilePath(['structure.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)

    data_type_definition = definitions_registry.GetDefinitionByName('point3d')
    data_type_map = data_maps.StructureMap(data_type_definition)

    byte_values = []
    for value in range(1, 4):
      byte_value_upper, byte_value_lower = divmod(value, 256)
      byte_values.extend([byte_value_lower, byte_value_upper, 0, 0])

    byte_stream = bytes(bytearray(byte_values))

    point3d = data_type_map.MapByteStream(byte_stream)
    self.assertEqual(point3d.x, 1)
    self.assertEqual(point3d.y, 2)
    self.assertEqual(point3d.z, 3)

    data_type_definition = definitions_registry.GetDefinitionByName('point3d')
    data_type_definition.byte_order = definitions.BYTE_ORDER_BIG_ENDIAN
    data_type_map = data_maps.StructureMap(data_type_definition)

    point3d = data_type_map.MapByteStream(byte_stream)
    self.assertEqual(point3d.x, 0x01000000)
    self.assertEqual(point3d.y, 0x02000000)
    self.assertEqual(point3d.z, 0x03000000)

  @test_lib.skipUnlessHasTestFile(['structure.yaml'])
  def testMapByteStreamWithSequence(self):
    """Tests the MapByteStream function with a sequence."""
    definitions_file = self._GetTestFilePath(['structure.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)

    data_type_definition = definitions_registry.GetDefinitionByName('box3d')
    data_type_map = data_maps.StructureMap(data_type_definition)

    byte_values = []
    for value in range(1, 433):
      byte_value_upper, byte_value_lower = divmod(value, 256)
      byte_values.extend([byte_value_lower, byte_value_upper, 0, 0])

    byte_stream = bytes(bytearray(byte_values))

    box = data_type_map.MapByteStream(byte_stream)
    self.assertEqual(box.triangles[0].a.x, 1)
    self.assertEqual(box.triangles[0].a.y, 2)
    self.assertEqual(box.triangles[0].a.z, 3)

  @test_lib.skipUnlessHasTestFile(['structure.yaml'])
  def testMapByteStreamWithSequenceWithExpression(self):
    """Tests the MapByteStream function with a sequence with expression."""
    definitions_file = self._GetTestFilePath(['structure.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)

    data_type_definition = definitions_registry.GetDefinitionByName('sphere3d')
    data_type_map = data_maps.StructureMap(data_type_definition)

    byte_values = [3, 0, 0, 0]
    for value in range(1, 113):
      byte_value_upper, byte_value_lower = divmod(value, 256)
      byte_values.extend([byte_value_lower, byte_value_upper, 0, 0])

    byte_stream = bytes(bytearray(byte_values))

    sphere = data_type_map.MapByteStream(byte_stream)
    self.assertEqual(sphere.number_of_triangles, 3)

    self.assertEqual(sphere.triangles[0].a.x, 1)
    self.assertEqual(sphere.triangles[0].a.y, 2)
    self.assertEqual(sphere.triangles[0].a.z, 3)

    self.assertEqual(sphere.triangles[0].b.x, 4)
    self.assertEqual(sphere.triangles[0].b.y, 5)
    self.assertEqual(sphere.triangles[0].b.z, 6)

    self.assertEqual(sphere.triangles[0].c.x, 7)
    self.assertEqual(sphere.triangles[0].c.y, 8)
    self.assertEqual(sphere.triangles[0].c.z, 9)

    self.assertEqual(sphere.triangles[2].c.x, 25)
    self.assertEqual(sphere.triangles[2].c.y, 26)
    self.assertEqual(sphere.triangles[2].c.z, 27)

    # Test incremental map.
    context = data_maps.DataTypeMapContext()

    with self.assertRaises(errors.ByteStreamTooSmallError):
      data_type_map.MapByteStream(byte_stream[:64], context=context)

    sphere = data_type_map.MapByteStream(byte_stream[64:], context=context)
    self.assertEqual(sphere.number_of_triangles, 3)

    self.assertEqual(sphere.triangles[0].a.x, 1)
    self.assertEqual(sphere.triangles[0].a.y, 2)
    self.assertEqual(sphere.triangles[0].a.z, 3)

    self.assertEqual(sphere.triangles[2].c.x, 25)
    self.assertEqual(sphere.triangles[2].c.y, 26)
    self.assertEqual(sphere.triangles[2].c.z, 27)

  @test_lib.skipUnlessHasTestFile(['structure_with_sequence.yaml'])
  def testMapByteStreamWithSequenceWithExpression2(self):
    """Tests the MapByteStream function with a sequence with expression."""
    definitions_file = self._GetTestFilePath(['structure_with_sequence.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)

    data_type_definition = definitions_registry.GetDefinitionByName(
        'extension_block')
    data_type_map = data_maps.StructureMap(data_type_definition)

    byte_values = [4, 1, 0, 0]
    for byte_value in range(0, 256):
      byte_values.extend([byte_value])

    byte_stream = bytes(bytearray(byte_values))

    extension_block = data_type_map.MapByteStream(byte_stream)
    self.assertEqual(extension_block.size, 260)
    self.assertEqual(extension_block.data[0], 0)
    self.assertEqual(extension_block.data[-1], 255)

    byte_values = [3, 0, 0, 0]
    for byte_value in range(0, 256):
      byte_values.extend([byte_value])

    byte_stream = bytes(bytearray(byte_values))

    with self.assertRaises(errors.MappingError):
      data_type_map.MapByteStream(byte_stream)

  @test_lib.skipUnlessHasTestFile(['structure_with_stream.yaml'])
  def testMapByteStreamWithStream(self):
    """Tests the MapByteStream function with a stream."""
    definitions_file = self._GetTestFilePath(['structure_with_stream.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)

    data_type_definition = definitions_registry.GetDefinitionByName(
        'extension_block')
    data_type_map = data_maps.StructureMap(data_type_definition)

    byte_values = [4, 1, 0, 0]
    for byte_value in range(0, 256):
      byte_values.extend([byte_value])

    byte_stream = bytes(bytearray(byte_values))

    extension_block = data_type_map.MapByteStream(byte_stream)
    self.assertEqual(extension_block.size, 260)
    self.assertEqual(extension_block.data, byte_stream[4:])

    byte_values = [3, 0, 0, 0]
    for byte_value in range(0, 256):
      byte_values.extend([byte_value])

    byte_stream = bytes(bytearray(byte_values))

    with self.assertRaises(errors.MappingError):
      data_type_map.MapByteStream(byte_stream)

  @test_lib.skipUnlessHasTestFile(['structure_with_string.yaml'])
  def testMapByteStreamWithString(self):
    """Tests the MapByteStream function with a string."""
    definitions_file = self._GetTestFilePath(['structure_with_string.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)

    data_type_definition = definitions_registry.GetDefinitionByName(
        'utf16_string')
    data_type_map = data_maps.StructureMap(data_type_definition)

    text_stream = 'dtFabric'.encode('utf-16-le')
    byte_stream = b''.join([
        bytes(bytearray([len(text_stream), 0])), text_stream])

    utf16_string = data_type_map.MapByteStream(byte_stream)
    self.assertEqual(utf16_string.size, len(text_stream))
    self.assertEqual(utf16_string.text, 'dtFabric')

    byte_stream = b''.join([bytes(bytearray([3, 0])), text_stream])

    with self.assertRaises(errors.MappingError):
      data_type_map.MapByteStream(byte_stream)

  @test_lib.skipUnlessHasTestFile(['structure_with_string.yaml'])
  def testGetSizeHint(self):
    """Tests the GetSizeHint function with a string."""
    definitions_file = self._GetTestFilePath(['structure_with_string.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)

    data_type_definition = definitions_registry.GetDefinitionByName(
        'utf16_string')
    data_type_map = data_maps.StructureMap(data_type_definition)

    context = data_maps.DataTypeMapContext()

    text_stream = 'dtFabric'.encode('utf-16-le')
    byte_stream = b''.join([
        bytes(bytearray([len(text_stream), 0])), text_stream])

    size_hint = data_type_map.GetSizeHint(context=context)
    self.assertEqual(size_hint, 2)

    with self.assertRaises(errors.ByteStreamTooSmallError):
      data_type_map.MapByteStream(byte_stream[:size_hint], context=context)

    size_hint = data_type_map.GetSizeHint(context=context)
    self.assertEqual(size_hint, 18)


@test_lib.skipUnlessHasTestFile(['constant.yaml'])
class SemanticDataTypeMapTest(test_lib.BaseTestCase):
  """Semantic datat type map tests."""

  def testFoldByteStream(self):
    """Tests the FoldByteStream function."""
    definitions_file = self._GetTestFilePath(['constant.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)

    data_type_definition = definitions_registry.GetDefinitionByName(
        'maximum_number_of_back_traces')
    data_type_map = data_maps.SemanticDataTypeMap(data_type_definition)

    with self.assertRaises(errors.FoldingError):
      data_type_map.FoldByteStream(1)

  def testMapByteStream(self):
    """Tests the MapByteStream function."""
    definitions_file = self._GetTestFilePath(['constant.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)

    data_type_definition = definitions_registry.GetDefinitionByName(
        'maximum_number_of_back_traces')
    data_type_map = data_maps.SemanticDataTypeMap(data_type_definition)

    with self.assertRaises(errors.MappingError):
      data_type_map.MapByteStream(b'\x01\x00\x00\x00')


class ConstantMapTest(test_lib.BaseTestCase):
  """Constant map tests."""


@test_lib.skipUnlessHasTestFile(['enumeration.yaml'])
class EnumerationMapTest(test_lib.BaseTestCase):
  """Enumeration map tests."""

  def testGetName(self):
    """Tests the GetName function."""
    definitions_file = self._GetTestFilePath(['enumeration.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)

    data_type_definition = definitions_registry.GetDefinitionByName(
        'object_information_type')
    data_type_definition.byte_order = definitions.BYTE_ORDER_LITTLE_ENDIAN
    data_type_map = data_maps.EnumerationMap(data_type_definition)

    name = data_type_map.GetName(2)
    self.assertEqual(name, 'MiniMutantInformation1')

    name = data_type_map.GetName(-1)
    self.assertIsNone(name)


@test_lib.skipUnlessHasTestFile(['integer.yaml'])
class DataTypeMapFactoryTest(test_lib.BaseTestCase):
  """Data type map factory tests."""

  def testCreateDataTypeMap(self):
    """Tests the CreateDataTypeMap function."""
    definitions_file = self._GetTestFilePath(['integer.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)

    data_type_definition = EmptyDataTypeDefinition('empty')
    definitions_registry.RegisterDefinition(data_type_definition)

    factory = data_maps.DataTypeMapFactory(definitions_registry)

    data_type_map = factory.CreateDataTypeMap('int32le')
    self.assertIsNotNone(data_type_map)

    data_type_map = factory.CreateDataTypeMap('empty')
    self.assertIsNone(data_type_map)

    data_type_map = factory.CreateDataTypeMap('bogus')
    self.assertIsNone(data_type_map)

  def testCreateDataTypeMapByType(self):
    """Tests the CreateDataTypeMapByType function."""
    definitions_file = self._GetTestFilePath(['integer.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)

    data_type_definition = definitions_registry.GetDefinitionByName('int32le')
    data_type_map = data_maps.DataTypeMapFactory.CreateDataTypeMapByType(
        data_type_definition)
    self.assertIsNotNone(data_type_map)

    data_type_definition = EmptyDataTypeDefinition('empty')
    data_type_map = data_maps.DataTypeMapFactory.CreateDataTypeMapByType(
        data_type_definition)
    self.assertIsNone(data_type_map)


if __name__ == '__main__':
  unittest.main()
