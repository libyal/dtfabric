# -*- coding: utf-8 -*-
"""Tests for the data type definitions."""

import unittest

from dtfabric import data_types
from dtfabric import definitions

from tests import test_lib


class DataTypeDefinitionTest(test_lib.BaseTestCase):
  """Data type definition tests."""

  def testIsComposite(self):
    """Tests the IsComposite function."""
    data_type_definition = data_types.DataTypeDefinition(
        u'int32', aliases=[u'LONG', u'LONG32'],
        description=u'signed 32-bit integer')

    result = data_type_definition.IsComposite()
    self.assertFalse(result)


class StorageDataTypeDefinitionTest(test_lib.BaseTestCase):
  """Storage data type definition tests."""

  def testInitialize(self):
    """Tests the __init__ function."""
    data_type_definition = data_types.StorageDataTypeDefinition(
        u'int32', aliases=[u'LONG', u'LONG32'],
        description=u'signed 32-bit integer')
    self.assertIsNotNone(data_type_definition)


class FixedSizeDataTypeDefinitionTest(test_lib.BaseTestCase):
  """Fixed-size data type definition tests."""

  def testInitialize(self):
    """Tests the __init__ function."""
    data_type_definition = data_types.FixedSizeDataTypeDefinition(
        u'int32', aliases=[u'LONG', u'LONG32'],
        description=u'signed 32-bit integer')
    self.assertIsNotNone(data_type_definition)

  def testGetByteSize(self):
    """Tests the GetByteSize function."""
    data_type_definition = data_types.FixedSizeDataTypeDefinition(
        u'int32', aliases=[u'LONG', u'LONG32'],
        description=u'signed 32-bit integer')

    byte_size = data_type_definition.GetByteSize()
    self.assertIsNone(byte_size)

    data_type_definition.size = 4
    byte_size = data_type_definition.GetByteSize()
    self.assertEqual(byte_size, 4)


class BooleanDefinitionTest(test_lib.BaseTestCase):
  """Boolean data type definition tests."""

  def testInitialize(self):
    """Tests the __init__ function."""
    data_type_definition = data_types.BooleanDefinition(
        u'bool32', aliases=[u'BOOL'], description=u'boolean')
    self.assertIsNotNone(data_type_definition)


class CharacterDefinitionTest(test_lib.BaseTestCase):
  """Character data type definition tests."""


class FloatingPointDefinitionTest(test_lib.BaseTestCase):
  """Floating-point data type definition tests."""


class IntegerDefinitionTest(test_lib.BaseTestCase):
  """Integer data type definition tests."""

  def testInitialize(self):
    """Tests the __init__ function."""
    data_type_definition = data_types.IntegerDefinition(
        u'int32', aliases=[u'LONG', u'LONG32'],
        description=u'signed 32-bit integer')
    self.assertIsNotNone(data_type_definition)


class UUIDDefinitionTest(test_lib.BaseTestCase):
  """UUID data type definition tests."""

  def testInitialize(self):
    """Tests the __init__ function."""
    data_type_definition = data_types.UUIDDefinition(
        u'guid', aliases=[u'GUID'], description=u'GUID')
    self.assertIsNotNone(data_type_definition)

  def testIsComposite(self):
    """Tests the IsComposite function."""
    data_type_definition = data_types.UUIDDefinition(
        u'guid', aliases=[u'GUID'], description=u'GUID')

    result = data_type_definition.IsComposite()
    self.assertTrue(result)


class ElementSequenceDataTypeDefinitionTest(test_lib.BaseTestCase):
  """Element sequence data type definition tests."""

  def testInitialize(self):
    """Tests the __init__ function."""
    element_definition = data_types.IntegerDefinition(u'int32')
    data_type_definition = data_types.ElementSequenceDataTypeDefinition(
        u'offsets', element_definition, description=u'offsets array')
    self.assertIsNotNone(data_type_definition)

  def testGetByteSize(self):
    """Tests the GetByteSize function."""
    data_type_definition = data_types.ElementSequenceDataTypeDefinition(
        u'offsets', None, description=u'offsets array')

    byte_size = data_type_definition.GetByteSize()
    self.assertIsNone(byte_size)

    element_definition = data_types.IntegerDefinition(u'int32')
    element_definition.format = definitions.FORMAT_SIGNED
    element_definition.size = 4
    data_type_definition.element_data_type_definition = element_definition

    byte_size = data_type_definition.GetByteSize()
    self.assertIsNone(byte_size)

    data_type_definition.elements_data_size = 0
    data_type_definition.number_of_elements = 32
    byte_size = data_type_definition.GetByteSize()
    self.assertEqual(byte_size, 128)

    data_type_definition.elements_data_size = 128
    data_type_definition.number_of_elements = 0
    byte_size = data_type_definition.GetByteSize()
    self.assertEqual(byte_size, 128)


class SequenceDefinitionTest(test_lib.BaseTestCase):
  """Sequence data type definition tests."""


class StreamDefinitionTest(test_lib.BaseTestCase):
  """Stream data type definition tests."""


class StringDefinitionTest(test_lib.BaseTestCase):
  """String data type definition tests."""

  def testInitialize(self):
    """Tests the __init__ function."""
    element_definition = data_types.IntegerDefinition(u'wchar16')
    data_type_definition = data_types.StringDefinition(
        u'utf16', element_definition, description=u'UTF-16 formatted string')
    self.assertIsNotNone(data_type_definition)

  def testGetByteSize(self):
    """Tests the GetByteSize function."""
    data_type_definition = data_types.StringDefinition(
        u'utf16', None, description=u'UTF-16 formatted string')

    byte_size = data_type_definition.GetByteSize()
    self.assertIsNone(byte_size)

    element_definition = data_types.IntegerDefinition(u'wchar16')
    element_definition.format = definitions.FORMAT_SIGNED
    element_definition.size = 2
    data_type_definition.element_data_type_definition = element_definition

    byte_size = data_type_definition.GetByteSize()
    self.assertIsNone(byte_size)

    data_type_definition.number_of_elements = 32
    byte_size = data_type_definition.GetByteSize()
    self.assertEqual(byte_size, 64)

  def testIsComposite(self):
    """Tests the IsComposite function."""
    data_type_definition = data_types.StringDefinition(
        u'utf16', None, description=u'UTF-16 formatted string')

    result = data_type_definition.IsComposite()
    self.assertTrue(result)


class DataTypeDefinitionWithMembersTest(test_lib.BaseTestCase):
  """Data type definition with members tests."""

  # TODO: add tests for AddMemberDefinition


@test_lib.skipUnlessHasTestFile([u'structure.yaml'])
class MemberDataTypeDefinitionTest(test_lib.BaseTestCase):
  """Member data type definition tests."""

  # pylint: disable=protected-access

  def testInitialize(self):
    """Tests the __init__ function."""
    definitions_file = self._GetTestFilePath([u'structure.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)
    member_definition = definitions_registry.GetDefinitionByName(u'int32')

    data_type_definition = data_types.MemberDataTypeDefinition(
        u'my_struct_member', member_definition, aliases=[u'MY_STRUCT_MEMBER'],
        data_type=u'int32', description=u'my structure member')
    self.assertIsNotNone(data_type_definition)

  def testGetByteSize(self):
    """Tests the GetByteSize function."""
    definitions_file = self._GetTestFilePath([u'structure.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)
    member_definition = definitions_registry.GetDefinitionByName(u'int32')

    data_type_definition = data_types.MemberDataTypeDefinition(
        u'my_struct_member', None, aliases=[u'MY_STRUCT_MEMBER'],
        data_type=u'int32', description=u'my structure member')

    byte_size = data_type_definition.GetByteSize()
    self.assertIsNone(byte_size)

    data_type_definition.member_data_type_definition = member_definition
    byte_size = data_type_definition.GetByteSize()
    self.assertEqual(byte_size, 4)

  def testIsComposite(self):
    """Tests the IsComposite function."""
    definitions_file = self._GetTestFilePath([u'structure.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)
    member_definition = definitions_registry.GetDefinitionByName(u'int32')

    data_type_definition = data_types.MemberDataTypeDefinition(
        u'my_struct_member', None, aliases=[u'MY_STRUCT_MEMBER'],
        data_type=u'int32', description=u'my structure member')

    result = data_type_definition.IsComposite()
    self.assertIsNone(result)

    data_type_definition.member_data_type_definition = member_definition
    result = data_type_definition.IsComposite()
    self.assertFalse(result)


class StructureDefinitionTest(test_lib.BaseTestCase):
  """Structure data type definition tests."""

  @test_lib.skipUnlessHasTestFile([u'structure.yaml'])
  def testGetByteSize(self):
    """Tests the GetByteSize function."""
    data_type_definition = data_types.StructureDefinition(
        u'my_struct_type', aliases=[u'MY_STRUCT_TYPE'],
        description=u'my structure type')

    byte_size = data_type_definition.GetByteSize()
    self.assertIsNone(byte_size)

    definitions_file = self._GetTestFilePath([u'structure.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)
    member_definition = definitions_registry.GetDefinitionByName(u'int32')

    structure_member_definition = data_types.MemberDataTypeDefinition(
        u'my_struct_member', member_definition, aliases=[u'MY_STRUCT_MEMBER'],
        data_type=u'int32', description=u'my structure member')

    data_type_definition.AddMemberDefinition(structure_member_definition)

    byte_size = data_type_definition.GetByteSize()
    self.assertEqual(byte_size, 4)

  def testIsComposite(self):
    """Tests the IsComposite function."""
    data_type_definition = data_types.StructureDefinition(
        u'my_struct_type', aliases=[u'MY_STRUCT_TYPE'],
        description=u'my structure type')

    result = data_type_definition.IsComposite()
    self.assertTrue(result)


class UnionDefinitionTest(test_lib.BaseTestCase):
  """Union data type definition tests."""

  @test_lib.skipUnlessHasTestFile([u'union.yaml'])
  def testGetByteSize(self):
    """Tests the GetByteSize function."""
    data_type_definition = data_types.UnionDefinition(
        u'my_union_type', aliases=[u'MY_UNION_TYPE'],
        description=u'my union type')

    byte_size = data_type_definition.GetByteSize()
    self.assertIsNone(byte_size)

    definitions_file = self._GetTestFilePath([u'union.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)
    member_definition = definitions_registry.GetDefinitionByName(u'int32')

    union_member_definition = data_types.MemberDataTypeDefinition(
        u'my_union_member', member_definition, aliases=[u'MY_UNION_MEMBER'],
        data_type=u'int32', description=u'my union member')

    data_type_definition.AddMemberDefinition(union_member_definition)

    byte_size = data_type_definition.GetByteSize()
    self.assertEqual(byte_size, 4)

  def testIsComposite(self):
    """Tests the IsComposite function."""
    data_type_definition = data_types.UnionDefinition(
        u'my_union_type', aliases=[u'MY_UNION_TYPE'],
        description=u'my union type')

    result = data_type_definition.IsComposite()
    self.assertTrue(result)


class SemanticDataTypeDefinitionTest(test_lib.BaseTestCase):
  """Semantic data type definition tests."""

  def testGetByteSize(self):
    """Tests the GetByteSize function."""
    data_type_definition = data_types.SemanticDataTypeDefinition(
        u'enum', description=u'enumeration')

    byte_size = data_type_definition.GetByteSize()
    self.assertIsNone(byte_size)


class ConstantDefinitionTest(test_lib.BaseTestCase):
  """Constant data type definition tests."""

  def testInitialize(self):
    """Tests the __init__ function."""
    data_type_definition = data_types.ConstantDefinition(
        u'const', description=u'contant')
    self.assertIsNotNone(data_type_definition)


class EnumerationValueTest(test_lib.BaseTestCase):
  """Enumeration value tests."""

  def testInitialize(self):
    """Tests the __init__ function."""
    enumeration_value = data_types.EnumerationValue(u'enum_value', 5)
    self.assertIsNotNone(enumeration_value)


class EnumerationDefinitionTest(test_lib.BaseTestCase):
  """Enumeration data type definition tests."""

  def testInitialize(self):
    """Tests the __init__ function."""
    data_type_definition = data_types.EnumerationDefinition(
        u'enum', description=u'enumeration')
    self.assertIsNotNone(data_type_definition)

  def testAddValue(self):
    """Tests the AddValue function."""
    data_type_definition = data_types.EnumerationDefinition(
        u'enum', description=u'enumeration')

    data_type_definition.AddValue(u'enum_value', 5, aliases=[u'value5'])

    with self.assertRaises(KeyError):
      data_type_definition.AddValue(u'enum_value', 7, aliases=[u'value7'])

    with self.assertRaises(KeyError):
      data_type_definition.AddValue(u'myenum', 5, aliases=[u'value7'])

    with self.assertRaises(KeyError):
      data_type_definition.AddValue(u'myenum', 7, aliases=[u'value5'])


class LayoutDataTypeDefinitionTest(test_lib.BaseTestCase):
  """Layout data type definition tests."""

  def testGetByteSize(self):
    """Tests the GetByteSize function."""
    data_type_definition = data_types.LayoutDataTypeDefinition(
        u'format', description=u'data format')

    byte_size = data_type_definition.GetByteSize()
    self.assertIsNone(byte_size)


class FormatDefinitionTest(test_lib.BaseTestCase):
  """Data format definition tests."""

  def testGetByteSize(self):
    """Tests the GetByteSize function."""
    data_type_definition = data_types.FormatDefinition(
        u'format', description=u'data format')

    byte_size = data_type_definition.GetByteSize()
    self.assertIsNone(byte_size)

  def testIsComposite(self):
    """Tests the IsComposite function."""
    data_type_definition = data_types.FormatDefinition(
        u'format', description=u'data format')

    result = data_type_definition.IsComposite()
    self.assertTrue(result)


if __name__ == '__main__':
  unittest.main()
