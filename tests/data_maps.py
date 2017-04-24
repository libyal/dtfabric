# -*- coding: utf-8 -*-
"""Tests for the data type maps."""

import unittest
import uuid

from dtfabric import byte_operations
from dtfabric import data_types
from dtfabric import definitions
from dtfabric import errors
from dtfabric import data_maps

from tests import test_lib


class EmptyDataTypeDefinition(data_types.DataTypeDefinition):
  """Empty data type definition for testing."""

  def GetAttributeNames(self):
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


class TestDataTypeDefinition(data_types.DataTypeDefinition):
  """Data type definition for testing."""

  def GetAttributeNames(self):
    """Determines the attribute (or field) names of the data type definition.

    Returns:
      list[str]: attribute names.
    """
    return [u'value']

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


@test_lib.skipUnlessHasTestFile([u'integer.yaml'])
class DataTypeMapTest(test_lib.BaseTestCase):
  """Data type map tests."""

  # pylint: disable=protected-access

  def testGetByteStreamOperation(self):
    """Tests the _GetByteStreamOperation function."""
    definitions_file = self._GetTestFilePath([u'integer.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)

    data_type_definition = definitions_registry.GetDefinitionByName(u'int32le')
    data_type_map = data_maps.DataTypeMap(data_type_definition)
    operation = data_type_map._GetByteStreamOperation()
    self.assertIsNone(operation)

  def testGetByteSize(self):
    """Tests the GetByteSize function."""
    definitions_file = self._GetTestFilePath([u'integer.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)
    data_type_definition = definitions_registry.GetDefinitionByName(u'int32le')

    data_type_map = data_maps.DataTypeMap(data_type_definition)

    byte_size = data_type_map.GetByteSize()
    self.assertEqual(byte_size, 4)

  def testGetStructByteOrderString(self):
    """Tests the GetStructByteOrderString function."""
    definitions_file = self._GetTestFilePath([u'integer.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)

    data_type_definition = definitions_registry.GetDefinitionByName(u'int32')
    data_type_map = data_maps.DataTypeMap(data_type_definition)
    byte_order_string = data_type_map.GetStructByteOrderString()
    self.assertEqual(byte_order_string, u'=')

    data_type_definition = definitions_registry.GetDefinitionByName(u'int32be')
    data_type_map = data_maps.DataTypeMap(data_type_definition)
    byte_order_string = data_type_map.GetStructByteOrderString()
    self.assertEqual(byte_order_string, u'>')

    data_type_definition = definitions_registry.GetDefinitionByName(u'int32le')
    data_type_map = data_maps.DataTypeMap(data_type_definition)
    byte_order_string = data_type_map.GetStructByteOrderString()
    self.assertEqual(byte_order_string, u'<')

  def testGetStructFormatString(self):
    """Tests the GetStructFormatString function."""
    definitions_file = self._GetTestFilePath([u'integer.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)

    data_type_definition = definitions_registry.GetDefinitionByName(u'int32le')
    data_type_map = data_maps.DataTypeMap(data_type_definition)
    format_string = data_type_map.GetStructFormatString()
    self.assertIsNone(format_string)


@test_lib.skipUnlessHasTestFile([u'integer.yaml'])
class PrimitiveDataTypeMapTest(test_lib.BaseTestCase):
  """Primitive data type map tests."""

  def testMapByteStream(self):
    """Tests the MapByteStream function."""
    definitions_file = self._GetTestFilePath([u'integer.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)

    data_type_definition = definitions_registry.GetDefinitionByName(u'int32le')
    data_type_map = data_maps.PrimitiveDataTypeMap(data_type_definition)

    with self.assertRaises(errors.MappingError):
      data_type_map.MapByteStream(b'\x01\x00\x00\x00')

  def testMapValue(self):
    """Tests the MapValue function."""
    definitions_file = self._GetTestFilePath([u'integer.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)

    data_type_definition = definitions_registry.GetDefinitionByName(u'int32le')
    data_type_map = data_maps.PrimitiveDataTypeMap(data_type_definition)

    integer_value = data_type_map.MapValue(1)
    self.assertEqual(integer_value, 1)


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
      data_maps.BooleanMap(data_type_definition)

  def testGetStructFormatString(self):
    """Tests the GetStructFormatString function."""
    definitions_file = self._GetTestFilePath([u'definitions', u'booleans.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)

    data_type_definition = definitions_registry.GetDefinitionByName(u'bool8')
    data_type_map = data_maps.BooleanMap(data_type_definition)
    struct_format_string = data_type_map.GetStructFormatString()
    self.assertEqual(struct_format_string, u'B')

    data_type_definition = definitions_registry.GetDefinitionByName(u'bool16')
    data_type_map = data_maps.BooleanMap(data_type_definition)
    struct_format_string = data_type_map.GetStructFormatString()
    self.assertEqual(struct_format_string, u'H')

    data_type_definition = definitions_registry.GetDefinitionByName(u'bool32')
    data_type_map = data_maps.BooleanMap(data_type_definition)
    struct_format_string = data_type_map.GetStructFormatString()
    self.assertEqual(struct_format_string, u'I')

  def testMapByteStream(self):
    """Tests the MapByteStream function."""
    definitions_file = self._GetTestFilePath([u'definitions', u'booleans.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)

    data_type_definition = definitions_registry.GetDefinitionByName(u'bool8')
    data_type_definition.byte_order = definitions.BYTE_ORDER_LITTLE_ENDIAN
    data_type_map = data_maps.BooleanMap(data_type_definition)
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
    data_type_map = data_maps.BooleanMap(data_type_definition)

    bool_value = data_type_map.MapByteStream(b'\xff\xff')
    self.assertFalse(bool_value)

    bool_value = data_type_map.MapByteStream(b'\x01\x00')
    self.assertTrue(bool_value)

    data_type_definition = definitions_registry.GetDefinitionByName(u'bool32')
    data_type_definition.byte_order = definitions.BYTE_ORDER_LITTLE_ENDIAN
    data_type_definition.true_value = None
    data_type_map = data_maps.BooleanMap(data_type_definition)

    bool_value = data_type_map.MapByteStream(b'\x00\x00\x00\x00')
    self.assertFalse(bool_value)

    bool_value = data_type_map.MapByteStream(b'\xff\xff\xff\xff')
    self.assertTrue(bool_value)

    with self.assertRaises(errors.MappingError):
      data_type_map.MapByteStream(b'\x01\x00')


@test_lib.skipUnlessHasTestFile([u'definitions', u'characters.yaml'])
class CharacterMapTest(test_lib.BaseTestCase):
  """Character map tests."""

  def testGetStructFormatString(self):
    """Tests the GetStructFormatString function."""
    definitions_file = self._GetTestFilePath([
        u'definitions', u'characters.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)

    data_type_definition = definitions_registry.GetDefinitionByName(u'char')
    data_type_map = data_maps.CharacterMap(data_type_definition)
    struct_format_string = data_type_map.GetStructFormatString()
    self.assertEqual(struct_format_string, u'b')

    data_type_definition = definitions_registry.GetDefinitionByName(u'wchar16')
    data_type_map = data_maps.CharacterMap(data_type_definition)
    struct_format_string = data_type_map.GetStructFormatString()
    self.assertEqual(struct_format_string, u'h')

    data_type_definition = definitions_registry.GetDefinitionByName(u'wchar32')
    data_type_map = data_maps.CharacterMap(data_type_definition)
    struct_format_string = data_type_map.GetStructFormatString()
    self.assertEqual(struct_format_string, u'i')

  def testMapByteStream(self):
    """Tests the MapByteStream function."""
    definitions_file = self._GetTestFilePath([
        u'definitions', u'characters.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)

    data_type_definition = definitions_registry.GetDefinitionByName(u'char')
    data_type_definition.byte_order = definitions.BYTE_ORDER_LITTLE_ENDIAN
    data_type_map = data_maps.CharacterMap(data_type_definition)

    string_value = data_type_map.MapByteStream(b'\x41')
    self.assertEqual(string_value, u'A')

    data_type_definition = definitions_registry.GetDefinitionByName(u'wchar16')
    data_type_definition.byte_order = definitions.BYTE_ORDER_LITTLE_ENDIAN
    data_type_map = data_maps.CharacterMap(data_type_definition)

    string_value = data_type_map.MapByteStream(b'\xb6\x24')
    self.assertEqual(string_value, u'\u24b6')

    data_type_definition = definitions_registry.GetDefinitionByName(u'wchar32')
    data_type_definition.byte_order = definitions.BYTE_ORDER_LITTLE_ENDIAN
    data_type_map = data_maps.CharacterMap(data_type_definition)

    string_value = data_type_map.MapByteStream(b'\xb6\x24\x00\x00')
    self.assertEqual(string_value, u'\u24b6')

    with self.assertRaises(errors.MappingError):
      data_type_map.MapByteStream(b'\xb6\x24')


@test_lib.skipUnlessHasTestFile([u'definitions', u'floating-points.yaml'])
class FloatingPointMapTest(test_lib.BaseTestCase):
  """Floating-point map tests."""

  def testGetStructFormatString(self):
    """Tests the GetStructFormatString function."""
    definitions_file = self._GetTestFilePath([
        u'definitions', u'floating-points.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)

    data_type_definition = definitions_registry.GetDefinitionByName(u'float32')
    data_type_map = data_maps.FloatingPointMap(data_type_definition)
    struct_format_string = data_type_map.GetStructFormatString()
    self.assertEqual(struct_format_string, u'f')

    data_type_definition = definitions_registry.GetDefinitionByName(u'float64')
    data_type_map = data_maps.FloatingPointMap(data_type_definition)
    struct_format_string = data_type_map.GetStructFormatString()
    self.assertEqual(struct_format_string, u'd')

  def testMapByteStream(self):
    """Tests the MapByteStream function."""
    definitions_file = self._GetTestFilePath([
        u'definitions', u'floating-points.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)

    data_type_definition = definitions_registry.GetDefinitionByName(u'float32')
    data_type_definition.byte_order = definitions.BYTE_ORDER_LITTLE_ENDIAN
    data_type_map = data_maps.FloatingPointMap(data_type_definition)

    float_value = data_type_map.MapByteStream(b'\xa4\x70\x45\x41')
    self.assertEqual(float_value, 12.34000015258789)

    data_type_definition = definitions_registry.GetDefinitionByName(u'float64')
    data_type_definition.byte_order = definitions.BYTE_ORDER_LITTLE_ENDIAN
    data_type_map = data_maps.FloatingPointMap(data_type_definition)

    float_value = data_type_map.MapByteStream(
        b'\xae\x47\xe1\x7a\x14\xae\x28\x40')
    self.assertEqual(float_value, 12.34)

    with self.assertRaises(errors.MappingError):
      data_type_map.MapByteStream(b'\xa4\x70\x45\x41')


@test_lib.skipUnlessHasTestFile([u'definitions', u'integers.yaml'])
class IntegerMapTest(test_lib.BaseTestCase):
  """Integer map tests."""

  # pylint: disable=protected-access

  def testGetByteStreamOperation(self):
    """Tests the _GetByteStreamOperation function."""
    definitions_file = self._GetTestFilePath([u'integer.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)

    data_type_definition = definitions_registry.GetDefinitionByName(u'int32le')
    data_type_map = data_maps.IntegerMap(data_type_definition)
    operation = data_type_map._GetByteStreamOperation()
    self.assertIsInstance(operation, byte_operations.StructOperation)

  def testGetStructFormatString(self):
    """Tests the GetStructFormatString function."""
    definitions_file = self._GetTestFilePath([u'definitions', u'integers.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)

    data_type_definition = definitions_registry.GetDefinitionByName(u'int8')
    data_type_map = data_maps.IntegerMap(data_type_definition)
    struct_format_string = data_type_map.GetStructFormatString()
    self.assertEqual(struct_format_string, u'b')

    data_type_definition = definitions_registry.GetDefinitionByName(u'int16')
    data_type_map = data_maps.IntegerMap(data_type_definition)
    struct_format_string = data_type_map.GetStructFormatString()
    self.assertEqual(struct_format_string, u'h')

    data_type_definition = definitions_registry.GetDefinitionByName(u'int32')
    data_type_map = data_maps.IntegerMap(data_type_definition)
    struct_format_string = data_type_map.GetStructFormatString()
    self.assertEqual(struct_format_string, u'i')

    data_type_definition = definitions_registry.GetDefinitionByName(u'int64')
    data_type_map = data_maps.IntegerMap(data_type_definition)
    struct_format_string = data_type_map.GetStructFormatString()
    self.assertEqual(struct_format_string, u'q')

    data_type_definition = definitions_registry.GetDefinitionByName(u'uint8')
    data_type_map = data_maps.IntegerMap(data_type_definition)
    struct_format_string = data_type_map.GetStructFormatString()
    self.assertEqual(struct_format_string, u'B')

    data_type_definition = definitions_registry.GetDefinitionByName(u'uint16')
    data_type_map = data_maps.IntegerMap(data_type_definition)
    struct_format_string = data_type_map.GetStructFormatString()
    self.assertEqual(struct_format_string, u'H')

    data_type_definition = definitions_registry.GetDefinitionByName(u'uint32')
    data_type_map = data_maps.IntegerMap(data_type_definition)
    struct_format_string = data_type_map.GetStructFormatString()
    self.assertEqual(struct_format_string, u'I')

    data_type_definition = definitions_registry.GetDefinitionByName(u'uint64')
    data_type_map = data_maps.IntegerMap(data_type_definition)
    struct_format_string = data_type_map.GetStructFormatString()
    self.assertEqual(struct_format_string, u'Q')

  def testMapByteStream(self):
    """Tests the MapByteStream function."""
    definitions_file = self._GetTestFilePath([u'definitions', u'integers.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)

    data_type_definition = definitions_registry.GetDefinitionByName(u'uint8')
    data_type_definition.byte_order = definitions.BYTE_ORDER_LITTLE_ENDIAN
    data_type_map = data_maps.IntegerMap(data_type_definition)

    integer_value = data_type_map.MapByteStream(b'\x12')
    self.assertEqual(integer_value, 0x12)

    data_type_definition = definitions_registry.GetDefinitionByName(u'uint16')
    data_type_definition.byte_order = definitions.BYTE_ORDER_LITTLE_ENDIAN
    data_type_map = data_maps.IntegerMap(data_type_definition)

    integer_value = data_type_map.MapByteStream(b'\x12\x34')
    self.assertEqual(integer_value, 0x3412)

    data_type_definition = definitions_registry.GetDefinitionByName(u'uint32')
    data_type_definition.byte_order = definitions.BYTE_ORDER_LITTLE_ENDIAN
    data_type_map = data_maps.IntegerMap(data_type_definition)

    integer_value = data_type_map.MapByteStream(b'\x12\x34\x56\x78')
    self.assertEqual(integer_value, 0x78563412)

    data_type_definition = definitions_registry.GetDefinitionByName(u'uint32')
    data_type_definition.byte_order = definitions.BYTE_ORDER_BIG_ENDIAN
    data_type_map = data_maps.IntegerMap(data_type_definition)

    integer_value = data_type_map.MapByteStream(b'\x12\x34\x56\x78')
    self.assertEqual(integer_value, 0x12345678)

    data_type_definition = definitions_registry.GetDefinitionByName(u'uint64')
    data_type_definition.byte_order = definitions.BYTE_ORDER_LITTLE_ENDIAN
    data_type_map = data_maps.IntegerMap(data_type_definition)

    integer_value = data_type_map.MapByteStream(
        b'\x12\x34\x56\x78\x9a\xbc\xde\xf0')
    self.assertEqual(integer_value, 0xf0debc9a78563412)

    with self.assertRaises(errors.MappingError):
      data_type_map.MapByteStream(b'\x12\x34\x56\x78')


@test_lib.skipUnlessHasTestFile([u'sequence.yaml'])
class ElementSequenceDataTypeMapTest(test_lib.BaseTestCase):
  """Element sequence data type map tests."""

  # pylint: disable=protected-access

  def testInitialize(self):
    """Tests the __init__ function."""
    definitions_file = self._GetTestFilePath([u'sequence.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)
    data_type_definition = definitions_registry.GetDefinitionByName(u'vector4')

    data_type_map = data_maps.ElementSequenceDataTypeMap(data_type_definition)
    self.assertIsNotNone(data_type_map)

  # TODO: add tests for _EvaluateElementsDataSize.
  # TODO: add tests for _EvaluateNumberOfElements.

  def testGetElementDataTypeDefinition(self):
    """Tests the _GetElementDataTypeDefinition function."""
    definitions_file = self._GetTestFilePath([u'sequence.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)
    data_type_definition = definitions_registry.GetDefinitionByName(u'vector4')

    data_type_map = data_maps.ElementSequenceDataTypeMap(data_type_definition)

    element_data_type_definition = data_type_map._GetElementDataTypeDefinition(
        data_type_definition)
    self.assertIsNotNone(element_data_type_definition)

    with self.assertRaises(errors.FormatError):
      data_type_map._GetElementDataTypeDefinition(None)

    with self.assertRaises(errors.FormatError):
      data_type_definition = EmptyDataTypeDefinition(u'empty')
      data_type_map._GetElementDataTypeDefinition(data_type_definition)

  def testGetStructByteOrderString(self):
    """Tests the GetStructByteOrderString function."""
    definitions_file = self._GetTestFilePath([u'sequence.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)

    data_type_definition = definitions_registry.GetDefinitionByName(u'vector4')
    data_type_map = data_maps.ElementSequenceDataTypeMap(data_type_definition)
    byte_order_string = data_type_map.GetStructByteOrderString()
    self.assertEqual(byte_order_string, u'<')


@test_lib.skipUnlessHasTestFile([u'sequence.yaml'])
class SequenceMapTest(test_lib.BaseTestCase):
  """Sequence map tests."""

  # pylint: disable=protected-access

  def testInitialize(self):
    """Tests the __init__ function."""
    definitions_file = self._GetTestFilePath([u'sequence.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)
    data_type_definition = definitions_registry.GetDefinitionByName(u'vector4')

    data_type_map = data_maps.SequenceMap(data_type_definition)
    self.assertIsNotNone(data_type_map)

  def testGetStructFormatString(self):
    """Tests the GetStructFormatString function."""
    definitions_file = self._GetTestFilePath([u'sequence.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)

    data_type_definition = definitions_registry.GetDefinitionByName(u'vector4')
    data_type_map = data_maps.SequenceMap(data_type_definition)
    struct_format_string = data_type_map.GetStructFormatString()
    self.assertEqual(struct_format_string, u'4i')

    data_type_definition.elements_data_size = 16
    data_type_definition.number_of_elements = 0
    data_type_map = data_maps.SequenceMap(data_type_definition)
    struct_format_string = data_type_map.GetStructFormatString()
    self.assertEqual(struct_format_string, u'4i')

    data_type_definition.elements_data_size = 0
    data_type_definition.number_of_elements = 0
    data_type_map = data_maps.SequenceMap(data_type_definition)
    struct_format_string = data_type_map.GetStructFormatString()
    self.assertIsNone(struct_format_string)

  def testMapByteStream(self):
    """Tests the MapByteStream function."""
    definitions_file = self._GetTestFilePath([u'sequence.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)
    data_type_definition = definitions_registry.GetDefinitionByName(u'vector4')

    data_type_map = data_maps.SequenceMap(data_type_definition)

    sequence_value = data_type_map.MapByteStream(
        b'\x01\x00\x00\x00\x02\x00\x00\x00\x03\x00\x00\x00\x04\x00\x00\x00')
    self.assertEqual(sequence_value, (1, 2, 3, 4))

    with self.assertRaises(errors.MappingError):
      data_type_map.MapByteStream(None)

    with self.assertRaises(errors.MappingError):
      data_type_map.MapByteStream(b'\x12\x34\x56')


@test_lib.skipUnlessHasTestFile([u'stream.yaml'])
class StreamMapTest(test_lib.BaseTestCase):
  """Stream map tests."""

  # pylint: disable=protected-access

  def testInitialize(self):
    """Tests the __init__ function."""
    definitions_file = self._GetTestFilePath([u'stream.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)
    data_type_definition = definitions_registry.GetDefinitionByName(
        u'utf16le_stream')

    data_type_map = data_maps.StreamMap(data_type_definition)
    self.assertIsNotNone(data_type_map)

  def testGetStructFormatString(self):
    """Tests the GetStructFormatString function."""
    definitions_file = self._GetTestFilePath([u'stream.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)

    data_type_definition = definitions_registry.GetDefinitionByName(
        u'utf16le_stream')
    data_type_map = data_maps.StreamMap(data_type_definition)
    struct_format_string = data_type_map.GetStructFormatString()
    self.assertEqual(struct_format_string, u'16B')

    data_type_definition.elements_data_size = 16
    data_type_definition.number_of_elements = 0
    data_type_map = data_maps.StreamMap(data_type_definition)
    struct_format_string = data_type_map.GetStructFormatString()
    self.assertEqual(struct_format_string, u'16B')

    data_type_definition.elements_data_size = 0
    data_type_definition.number_of_elements = 0
    data_type_map = data_maps.StreamMap(data_type_definition)
    struct_format_string = data_type_map.GetStructFormatString()
    self.assertIsNone(struct_format_string)

  def testMapByteStream(self):
    """Tests the MapByteStream function."""
    definitions_file = self._GetTestFilePath([u'stream.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)
    data_type_definition = definitions_registry.GetDefinitionByName(
        u'utf16le_stream')

    data_type_map = data_maps.StreamMap(data_type_definition)

    stream_value = data_type_map.MapByteStream(u'dtFabric'.encode(u'utf-16-le'))
    self.assertEqual(stream_value, b'd\x00t\x00F\x00a\x00b\x00r\x00i\x00c\x00')

    with self.assertRaises(errors.MappingError):
      data_type_map.MapByteStream(None)

    with self.assertRaises(errors.MappingError):
      data_type_map.MapByteStream(b'\x12\x34\x56')


@test_lib.skipUnlessHasTestFile([u'string.yaml'])
class StringMapTest(test_lib.BaseTestCase):
  """String map tests."""

  def testGetStructFormatString(self):
    """Tests the GetStructFormatString function."""
    definitions_file = self._GetTestFilePath([u'string.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)

    data_type_definition = definitions_registry.GetDefinitionByName(
        u'utf16_string')
    data_type_map = data_maps.StreamMap(data_type_definition)
    struct_format_string = data_type_map.GetStructFormatString()
    self.assertEqual(struct_format_string, u'16B')

    data_type_definition.elements_data_size = 16
    data_type_definition.number_of_elements = 0
    data_type_map = data_maps.StringMap(data_type_definition)
    struct_format_string = data_type_map.GetStructFormatString()
    self.assertEqual(struct_format_string, u'16B')

    data_type_definition.elements_data_size = 0
    data_type_definition.number_of_elements = 0
    data_type_map = data_maps.StringMap(data_type_definition)
    struct_format_string = data_type_map.GetStructFormatString()
    self.assertIsNone(struct_format_string)

  def testMapByteStream(self):
    """Tests the MapByteStream function."""
    definitions_file = self._GetTestFilePath([u'string.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)
    data_type_definition = definitions_registry.GetDefinitionByName(
        u'utf16_string')

    data_type_map = data_maps.StringMap(data_type_definition)

    string_value = data_type_map.MapByteStream(u'dtFabric'.encode(u'utf-16-le'))
    self.assertEqual(string_value, u'dtFabric')

    with self.assertRaises(errors.MappingError):
      data_type_map.MapByteStream(None)

    with self.assertRaises(errors.MappingError):
      data_type_map.MapByteStream(b'\x12\x34\x56')


class StructureMapTest(test_lib.BaseTestCase):
  """Structure map tests."""

  # pylint: disable=protected-access

  @test_lib.skipUnlessHasTestFile([u'structure.yaml'])
  def testInitialize(self):
    """Tests the __init__ function."""
    definitions_file = self._GetTestFilePath([u'structure.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)

    data_type_definition = definitions_registry.GetDefinitionByName(u'point3d')
    data_type_map = data_maps.StructureMap(data_type_definition)
    self.assertIsNotNone(data_type_map)

  @test_lib.skipUnlessHasTestFile([u'structure.yaml'])
  def testCheckCompositeMap(self):
    """Tests the _CheckCompositeMap function."""
    definitions_file = self._GetTestFilePath([u'structure.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)

    data_type_definition = definitions_registry.GetDefinitionByName(u'point3d')
    data_type_map = data_maps.StructureMap(data_type_definition)

    result = data_type_map._CheckCompositeMap(data_type_definition)
    self.assertFalse(result)

    with self.assertRaises(errors.FormatError):
      data_type_map._CheckCompositeMap(None)

    with self.assertRaises(errors.FormatError):
      data_type_definition = EmptyDataTypeDefinition(u'empty')
      data_type_map._CheckCompositeMap(data_type_definition)

    data_type_definition = definitions_registry.GetDefinitionByName(
        u'triangle3d')
    data_type_map = data_maps.StructureMap(data_type_definition)

    result = data_type_map._CheckCompositeMap(data_type_definition)
    self.assertTrue(result)

    data_type_definition = definitions_registry.GetDefinitionByName(u'box3d')
    data_type_map = data_maps.StructureMap(data_type_definition)

    result = data_type_map._CheckCompositeMap(data_type_definition)
    self.assertTrue(result)

    data_type_definition = definitions_registry.GetDefinitionByName(
        u'sphere3d')
    data_type_map = data_maps.StructureMap(data_type_definition)

    result = data_type_map._CheckCompositeMap(data_type_definition)
    self.assertTrue(result)

  @test_lib.skipUnlessHasTestFile([u'structure.yaml'])
  def testGetMemberDataTypeMaps(self):
    """Tests the _GetMemberDataTypeMaps function."""
    definitions_file = self._GetTestFilePath([u'structure.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)
    data_type_definition = definitions_registry.GetDefinitionByName(u'point3d')

    data_type_map = data_maps.StructureMap(data_type_definition)

    members_data_type_maps = data_type_map._GetMemberDataTypeMaps(
        data_type_definition, {})
    self.assertIsNotNone(members_data_type_maps)

    with self.assertRaises(errors.FormatError):
      data_type_map._GetMemberDataTypeMaps(None, {})

    with self.assertRaises(errors.FormatError):
      data_type_definition = EmptyDataTypeDefinition(u'empty')
      data_type_map._GetMemberDataTypeMaps(data_type_definition, {})

  def testGetStructFormatString(self):
    """Tests the GetStructFormatString function."""
    definitions_file = self._GetTestFilePath([u'structure.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)

    data_type_definition = definitions_registry.GetDefinitionByName(u'point3d')
    data_type_map = data_maps.StructureMap(data_type_definition)
    struct_format_string = data_type_map.GetStructFormatString()
    self.assertEqual(struct_format_string, u'iii')

    # Test with member without a struct format string.

    data_type_definition = data_types.StructureDefinition(
        u'my_struct_type', aliases=[u'MY_STRUCT_TYPE'],
        description=u'my structure type')

    member_definition = TestDataTypeDefinition(u'test')

    structure_member_definition = data_types.StructureMemberDefinition(
        u'my_struct_member', member_definition, aliases=[u'MY_STRUCT_MEMBER'],
        data_type=u'test', description=u'my structure member')

    data_type_definition.AddMemberDefinition(structure_member_definition)

    data_type_map = data_maps.StructureMap(data_type_definition)
    struct_format_string = data_type_map.GetStructFormatString()
    self.assertIsNone(struct_format_string)

  @test_lib.skipUnlessHasTestFile([u'structure.yaml'])
  def testMapByteStream(self):
    """Tests the MapByteStream function."""
    definitions_file = self._GetTestFilePath([u'structure.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)

    data_type_definition = definitions_registry.GetDefinitionByName(u'point3d')
    data_type_map = data_maps.StructureMap(data_type_definition)

    byte_values = []
    for value in range(1, 4):
      byte_value_upper, byte_value_lower = divmod(value, 256)
      byte_values.extend([byte_value_lower, byte_value_upper, 0, 0])

    byte_stream = bytes(bytearray(byte_values))

    named_tuple = data_type_map.MapByteStream(byte_stream)
    self.assertEqual(named_tuple.x, 1)
    self.assertEqual(named_tuple.y, 2)
    self.assertEqual(named_tuple.z, 3)

    data_type_definition = definitions_registry.GetDefinitionByName(u'point3d')
    data_type_definition.byte_order = definitions.BYTE_ORDER_BIG_ENDIAN
    data_type_map = data_maps.StructureMap(data_type_definition)

    named_tuple = data_type_map.MapByteStream(byte_stream)
    self.assertEqual(named_tuple.x, 0x01000000)
    self.assertEqual(named_tuple.y, 0x02000000)
    self.assertEqual(named_tuple.z, 0x03000000)

  @test_lib.skipUnlessHasTestFile([u'structure.yaml'])
  def testMapByteStreamWithSequence(self):
    """Tests the MapByteStream function with a sequence."""
    definitions_file = self._GetTestFilePath([u'structure.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)

    data_type_definition = definitions_registry.GetDefinitionByName(u'box3d')
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

  @test_lib.skipUnlessHasTestFile([u'structure.yaml'])
  def testMapByteStreamWithSequenceWithExpression(self):
    """Tests the MapByteStream function with a sequence with expression."""
    definitions_file = self._GetTestFilePath([u'structure.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)

    data_type_definition = definitions_registry.GetDefinitionByName(u'sphere3d')
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

  @test_lib.skipUnlessHasTestFile([u'structure_with_sequence.yaml'])
  def testMapByteStreamWithSequenceWithExpression2(self):
    """Tests the MapByteStream function with a sequence with expression."""
    definitions_file = self._GetTestFilePath([u'structure_with_sequence.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)

    data_type_definition = definitions_registry.GetDefinitionByName(
        u'extension_block')
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

  @test_lib.skipUnlessHasTestFile([u'structure_with_stream.yaml'])
  def testMapByteStreamWithStream(self):
    """Tests the MapByteStream function with a stream."""
    definitions_file = self._GetTestFilePath([u'structure_with_stream.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)

    data_type_definition = definitions_registry.GetDefinitionByName(
        u'extension_block')
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

  @test_lib.skipUnlessHasTestFile([u'structure_with_string.yaml'])
  def testMapByteStreamWithString(self):
    """Tests the MapByteStream function with a string."""
    definitions_file = self._GetTestFilePath([u'structure_with_string.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)

    data_type_definition = definitions_registry.GetDefinitionByName(
        u'utf16_string')
    data_type_map = data_maps.StructureMap(data_type_definition)

    text_stream = u'dtFabric'.encode(u'utf-16-le')
    byte_stream = b''.join([
        bytes(bytearray([len(text_stream), 0])), text_stream])

    utf16_string = data_type_map.MapByteStream(byte_stream)
    self.assertEqual(utf16_string.size, len(text_stream))
    self.assertEqual(utf16_string.text, u'dtFabric')

    byte_stream = b''.join([bytes(bytearray([3, 0])), text_stream])

    with self.assertRaises(errors.MappingError):
      data_type_map.MapByteStream(byte_stream)


@test_lib.skipUnlessHasTestFile([u'uuid.yaml'])
class UUIDMapTest(test_lib.BaseTestCase):
  """UUID map tests."""

  def testGetStructFormatString(self):
    """Tests the GetStructFormatString function."""
    definitions_file = self._GetTestFilePath([u'uuid.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)

    data_type_definition = definitions_registry.GetDefinitionByName(u'uuid')
    data_type_map = data_maps.UUIDMap(data_type_definition)
    struct_format_string = data_type_map.GetStructFormatString()
    self.assertEqual(struct_format_string, u'IHH8B')

  def testMapByteStream(self):
    """Tests the MapByteStream function."""
    definitions_file = self._GetTestFilePath([u'uuid.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)

    data_type_definition = definitions_registry.GetDefinitionByName(u'uuid')
    data_type_definition.byte_order = definitions.BYTE_ORDER_LITTLE_ENDIAN
    data_type_map = data_maps.UUIDMap(data_type_definition)

    expected_uuid_value = uuid.UUID(u'{00021401-0000-0000-c000-000000000046}')
    uuid_value = data_type_map.MapByteStream(
        b'\x01\x14\x02\x00\x00\x00\x00\x00\xc0\x00\x00\x00\x00\x00\x00\x46')
    self.assertEqual(uuid_value, expected_uuid_value)


@test_lib.skipUnlessHasTestFile([u'integer.yaml'])
class DataTypeMapFactoryTest(test_lib.BaseTestCase):
  """Data type map factory tests."""

  def testCreateDataTypeMap(self):
    """Tests the CreateDataTypeMap function."""
    definitions_file = self._GetTestFilePath([u'integer.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)

    data_type_definition = EmptyDataTypeDefinition(u'empty')
    definitions_registry.RegisterDefinition(data_type_definition)

    factory = data_maps.DataTypeMapFactory(definitions_registry)

    data_type_map = factory.CreateDataTypeMap(u'int32le')
    self.assertIsNotNone(data_type_map)

    data_type_map = factory.CreateDataTypeMap(u'empty')
    self.assertIsNone(data_type_map)

    data_type_map = factory.CreateDataTypeMap(u'bogus')
    self.assertIsNone(data_type_map)

  def testCreateDataTypeMapByType(self):
    """Tests the CreateDataTypeMapByType function."""
    definitions_file = self._GetTestFilePath([u'integer.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)

    data_type_definition = definitions_registry.GetDefinitionByName(u'int32le')
    data_type_map = data_maps.DataTypeMapFactory.CreateDataTypeMapByType(
        data_type_definition)
    self.assertIsNotNone(data_type_map)

    data_type_definition = EmptyDataTypeDefinition(u'empty')
    data_type_map = data_maps.DataTypeMapFactory.CreateDataTypeMapByType(
        data_type_definition)
    self.assertIsNone(data_type_map)


if __name__ == '__main__':
  unittest.main()