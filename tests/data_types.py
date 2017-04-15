# -*- coding: utf-8 -*-
"""Tests for the data type definitions."""

import unittest

from dtfabric import data_types
from dtfabric import definitions

from tests import test_lib


# TODO: complete FormatDefinitionTest.
# TODO: complete StructureDefinitionTest.


class TestDataTypeDefinition(data_types.DataTypeDefinition):
  """Data type definition for testing."""

  def GetAttributedNames(self):
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

  def GetStructFormatString(self):
    """Retrieves the Python struct format string.

    Returns:
      str: format string as used by Python struct or None if format string
          cannot be determined.
    """
    return


class DataTypeDefinitionTest(test_lib.BaseTestCase):
  """Data type definition tests."""

  def testGetStructByteOrderString(self):
    """Tests the GetStructByteOrderString function."""
    data_type_definition = data_types.DataTypeDefinition(
        u'int32', aliases=[u'LONG', u'LONG32'],
        description=u'signed 32-bit integer')

    byte_order_string = data_type_definition.GetStructByteOrderString()
    self.assertEqual(byte_order_string, u'=')

    data_type_definition.byte_order = definitions.BYTE_ORDER_BIG_ENDIAN
    byte_order_string = data_type_definition.GetStructByteOrderString()
    self.assertEqual(byte_order_string, u'>')

    data_type_definition.byte_order = definitions.BYTE_ORDER_LITTLE_ENDIAN
    byte_order_string = data_type_definition.GetStructByteOrderString()
    self.assertEqual(byte_order_string, u'<')


class FixedSizeDataTypeDefinitionTest(test_lib.BaseTestCase):
  """Fixed-size data type definition tests."""

  def testInitialize(self):
    """Tests the __init__ function."""
    data_type_definition = data_types.FixedSizeDataTypeDefinition(
        u'int32', aliases=[u'LONG', u'LONG32'],
        description=u'signed 32-bit integer')
    self.assertIsNotNone(data_type_definition)

  def testGetAttributedNames(self):
    """Tests the GetAttributedNames function."""
    data_type_definition = data_types.FixedSizeDataTypeDefinition(
        u'int32', aliases=[u'LONG', u'LONG32'],
        description=u'signed 32-bit integer')

    attribute_names = data_type_definition.GetAttributedNames()
    self.assertEqual(attribute_names, [u'value'])

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

  def testGetStructFormatString(self):
    """Tests the GetStructFormatString function."""
    data_type_definition = data_types.BooleanDefinition(
        u'bool32', aliases=[u'BOOL'], description=u'boolean')

    struct_format_string = data_type_definition.GetStructFormatString()
    self.assertIsNone(struct_format_string)

    data_type_definition.size = 1
    struct_format_string = data_type_definition.GetStructFormatString()
    self.assertEqual(struct_format_string, u'B')

    data_type_definition.size = 2
    struct_format_string = data_type_definition.GetStructFormatString()
    self.assertEqual(struct_format_string, u'H')

    data_type_definition.size = 4
    struct_format_string = data_type_definition.GetStructFormatString()
    self.assertEqual(struct_format_string, u'I')


class CharacterDefinitionTest(test_lib.BaseTestCase):
  """character data type definition tests."""

  def testGetStructFormatString(self):
    """Tests the GetStructFormatString function."""
    data_type_definition = data_types.CharacterDefinition(
        u'char', aliases=[u'CHAR'], description=u'character')

    struct_format_string = data_type_definition.GetStructFormatString()
    self.assertIsNone(struct_format_string)

    data_type_definition.size = 1
    struct_format_string = data_type_definition.GetStructFormatString()
    self.assertEqual(struct_format_string, u'b')

    data_type_definition.size = 2
    struct_format_string = data_type_definition.GetStructFormatString()
    self.assertEqual(struct_format_string, u'h')

    data_type_definition.size = 4
    struct_format_string = data_type_definition.GetStructFormatString()
    self.assertEqual(struct_format_string, u'i')


class ConstantDefinitionTest(test_lib.BaseTestCase):
  """Constant data type definition tests."""

  def testInitialize(self):
    """Tests the __init__ function."""
    data_type_definition = data_types.ConstantDefinition(
        u'const', description=u'contant')
    self.assertIsNotNone(data_type_definition)

  def testGetAttributedNames(self):
    """Tests the GetAttributedNames function."""
    data_type_definition = data_types.ConstantDefinition(
        u'const', description=u'contant')

    attribute_names = data_type_definition.GetAttributedNames()
    self.assertEqual(attribute_names, [u'constant'])

  def testGetByteSize(self):
    """Tests the GetByteSize function."""
    data_type_definition = data_types.ConstantDefinition(
        u'const', description=u'contant')

    byte_size = data_type_definition.GetByteSize()
    self.assertIsNone(byte_size)

  def testGetStructFormatString(self):
    """Tests the GetStructFormatString function."""
    data_type_definition = data_types.ConstantDefinition(
        u'const', description=u'contant')

    struct_format_string = data_type_definition.GetStructFormatString()
    self.assertIsNone(struct_format_string)


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

    data_type_definition.AddValue(u'enum_value', 5)

    with self.assertRaises(KeyError):
      data_type_definition.AddValue(u'enum_value', 5)

  def testGetStructFormatString(self):
    """Tests the GetStructFormatString function."""
    data_type_definition = data_types.EnumerationDefinition(
        u'enum', description=u'enumeration')

    struct_format_string = data_type_definition.GetStructFormatString()
    self.assertIsNone(struct_format_string)

    data_type_definition.size = 1
    struct_format_string = data_type_definition.GetStructFormatString()
    self.assertEqual(struct_format_string, u'B')

    data_type_definition.size = 2
    struct_format_string = data_type_definition.GetStructFormatString()
    self.assertEqual(struct_format_string, u'H')

    data_type_definition.size = 4
    struct_format_string = data_type_definition.GetStructFormatString()
    self.assertEqual(struct_format_string, u'I')


class FormatDefinitionTest(test_lib.BaseTestCase):
  """Data format definition tests."""

  def testGetAttributedNames(self):
    """Tests the GetAttributedNames function."""
    data_type_definition = data_types.FormatDefinition(
        u'format', description=u'data format')

    attribute_names = data_type_definition.GetAttributedNames()
    self.assertEqual(attribute_names, [])

    # TODO: implement

  def testGetByteSize(self):
    """Tests the GetByteSize function."""
    data_type_definition = data_types.FormatDefinition(
        u'format', description=u'data format')

    byte_size = data_type_definition.GetByteSize()
    self.assertIsNone(byte_size)

  def testGetStructFormatString(self):
    """Tests the GetStructFormatString function."""
    data_type_definition = data_types.FormatDefinition(
        u'format', description=u'data format')

    struct_format_string = data_type_definition.GetStructFormatString()
    self.assertIsNone(struct_format_string)


class FloatingPointDefinitionTest(test_lib.BaseTestCase):
  """Floating-point data type definition tests."""

  def testGetStructFormatString(self):
    """Tests the GetStructFormatString function."""
    data_type_definition = data_types.FloatingPointDefinition(
        u'float32', aliases=[u'float', u'FLOAT'],
        description=u'32-bit floating-point')

    struct_format_string = data_type_definition.GetStructFormatString()
    self.assertIsNone(struct_format_string)

    data_type_definition.size = 4
    struct_format_string = data_type_definition.GetStructFormatString()
    self.assertEqual(struct_format_string, u'f')

    data_type_definition.size = 8
    struct_format_string = data_type_definition.GetStructFormatString()
    self.assertEqual(struct_format_string, u'd')


class IntegerDefinitionTest(test_lib.BaseTestCase):
  """Integer data type definition tests."""

  def testInitialize(self):
    """Tests the __init__ function."""
    data_type_definition = data_types.IntegerDefinition(
        u'int32', aliases=[u'LONG', u'LONG32'],
        description=u'signed 32-bit integer')
    self.assertIsNotNone(data_type_definition)

  def testGetStructFormatString(self):
    """Tests the GetStructFormatString function."""
    data_type_definition = data_types.IntegerDefinition(
        u'int32', aliases=[u'LONG', u'LONG32'],
        description=u'signed 32-bit integer')

    struct_format_string = data_type_definition.GetStructFormatString()
    self.assertIsNone(struct_format_string)

    data_type_definition.format = u'signed'
    data_type_definition.size = 1
    struct_format_string = data_type_definition.GetStructFormatString()
    self.assertEqual(struct_format_string, u'b')

    data_type_definition.format = u'signed'
    data_type_definition.size = 2
    struct_format_string = data_type_definition.GetStructFormatString()
    self.assertEqual(struct_format_string, u'h')

    data_type_definition.format = u'signed'
    data_type_definition.size = 4
    struct_format_string = data_type_definition.GetStructFormatString()
    self.assertEqual(struct_format_string, u'i')

    data_type_definition.format = u'signed'
    data_type_definition.size = 8
    struct_format_string = data_type_definition.GetStructFormatString()
    self.assertEqual(struct_format_string, u'q')

    data_type_definition.format = u'unsigned'
    data_type_definition.size = 1
    struct_format_string = data_type_definition.GetStructFormatString()
    self.assertEqual(struct_format_string, u'B')

    data_type_definition.format = u'unsigned'
    data_type_definition.size = 2
    struct_format_string = data_type_definition.GetStructFormatString()
    self.assertEqual(struct_format_string, u'H')

    data_type_definition.format = u'unsigned'
    data_type_definition.size = 4
    struct_format_string = data_type_definition.GetStructFormatString()
    self.assertEqual(struct_format_string, u'I')

    data_type_definition.format = u'unsigned'
    data_type_definition.size = 8
    struct_format_string = data_type_definition.GetStructFormatString()
    self.assertEqual(struct_format_string, u'Q')


class SequenceDefinitionTest(test_lib.BaseTestCase):
  """Sequence data type definition tests."""

  def testInitialize(self):
    """Tests the __init__ function."""
    data_type_definition = data_types.SequenceDefinition(
        u'byte_stream', description=u'byte stream')
    self.assertIsNotNone(data_type_definition)

  def testGetAttributedNames(self):
    """Tests the GetAttributedNames function."""
    data_type_definition = data_types.SequenceDefinition(
        u'byte_stream', description=u'byte stream')

    attribute_names = data_type_definition.GetAttributedNames()
    self.assertEqual(attribute_names, [u'elements'])

  def testGetByteSize(self):
    """Tests the GetByteSize function."""
    data_type_definition = data_types.SequenceDefinition(
        u'byte_stream', description=u'byte stream')

    byte_size = data_type_definition.GetByteSize()
    self.assertIsNone(byte_size)

    element_data_type = data_types.IntegerDefinition(u'byte')
    element_data_type.format = definitions.FORMAT_UNSIGNED
    element_data_type.size = 1
    data_type_definition.element_data_type = element_data_type

    byte_size = data_type_definition.GetByteSize()
    self.assertIsNone(byte_size)

    data_type_definition.number_of_elements = 32
    byte_size = data_type_definition.GetByteSize()
    self.assertEqual(byte_size, 32)

  def testGetStructByteOrderString(self):
    """Tests the GetStructByteOrderString function."""
    data_type_definition = data_types.SequenceDefinition(
        u'byte_stream', description=u'byte stream')

    byte_order_string = data_type_definition.GetStructByteOrderString()
    self.assertIsNone(byte_order_string)

    element_data_type = data_types.IntegerDefinition(u'uint16le')
    element_data_type.byte_order = definitions.BYTE_ORDER_LITTLE_ENDIAN
    data_type_definition.element_data_type = element_data_type

    byte_order_string = data_type_definition.GetStructByteOrderString()
    self.assertEqual(byte_order_string, u'<')

  def testGetStructFormatString(self):
    """Tests the GetStructFormatString function."""
    data_type_definition = data_types.SequenceDefinition(
        u'byte_stream', description=u'byte stream')

    struct_format_string = data_type_definition.GetStructFormatString()
    self.assertIsNone(struct_format_string)

    element_data_type = data_types.IntegerDefinition(u'byte')
    element_data_type.format = definitions.FORMAT_UNSIGNED
    element_data_type.size = 1
    data_type_definition.element_data_type = element_data_type

    struct_format_string = data_type_definition.GetStructFormatString()
    self.assertIsNone(struct_format_string)

    data_type_definition.number_of_elements = 32
    struct_format_string = data_type_definition.GetStructFormatString()
    self.assertEqual(struct_format_string, u'32B')


@test_lib.skipUnlessHasTestFile([u'definitions', u'integers.yaml'])
class StructureDefinitionTest(test_lib.BaseTestCase):
  """Structure data type definition tests."""

  # pylint: disable=protected-access

  def testGetAttributedNames(self):
    """Tests the GetAttributedNames function."""
    data_type_definition = data_types.StructureDefinition(
        u'my_struct_type', aliases=[u'MY_STRUCT_TYPE'],
        description=u'my structure type')

    attribute_names = data_type_definition.GetAttributedNames()
    self.assertEqual(attribute_names, [])

    definitions_file = self._GetTestFilePath([u'definitions', u'integers.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)
    member_data_type_definition = definitions_registry.GetDefinitionByName(
        u'int32')

    structure_member_definition = data_types.StructureMemberDefinition(
        member_data_type_definition, u'my_struct_member',
        aliases=[u'MY_STRUCT_MEMBER'], data_type=u'int32',
        description=u'my structure member')

    data_type_definition.AddMemberDefinition(structure_member_definition)

    attribute_names = data_type_definition.GetAttributedNames()
    self.assertEqual(attribute_names, [u'my_struct_member'])

  def testGetByteSize(self):
    """Tests the GetByteSize function."""
    data_type_definition = data_types.StructureDefinition(
        u'my_struct_type', aliases=[u'MY_STRUCT_TYPE'],
        description=u'my structure type')

    byte_size = data_type_definition.GetByteSize()
    self.assertIsNone(byte_size)

    definitions_file = self._GetTestFilePath([u'definitions', u'integers.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)
    member_data_type_definition = definitions_registry.GetDefinitionByName(
        u'int32')

    structure_member_definition = data_types.StructureMemberDefinition(
        member_data_type_definition, u'my_struct_member',
        aliases=[u'MY_STRUCT_MEMBER'], data_type=u'int32',
        description=u'my structure member')

    data_type_definition.AddMemberDefinition(structure_member_definition)

    byte_size = data_type_definition.GetByteSize()
    self.assertEqual(byte_size, 4)

  def testGetStructFormatString(self):
    """Tests the GetStructFormatString function."""
    data_type_definition = data_types.StructureDefinition(
        u'my_struct_type', aliases=[u'MY_STRUCT_TYPE'],
        description=u'my structure type')

    struct_format_string = data_type_definition.GetStructFormatString()
    self.assertIsNone(struct_format_string)

    definitions_file = self._GetTestFilePath([u'definitions', u'integers.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)
    member_data_type_definition = definitions_registry.GetDefinitionByName(
        u'int32')

    structure_member_definition = data_types.StructureMemberDefinition(
        member_data_type_definition, u'my_struct_member',
        aliases=[u'MY_STRUCT_MEMBER'], data_type=u'int32',
        description=u'my structure member')

    data_type_definition.AddMemberDefinition(structure_member_definition)

    struct_format_string = data_type_definition.GetStructFormatString()
    self.assertEqual(struct_format_string, u'i')

    # Test with member without a struct format string.

    data_type_definition = data_types.StructureDefinition(
        u'my_struct_type', aliases=[u'MY_STRUCT_TYPE'],
        description=u'my structure type')

    member_data_type_definition = TestDataTypeDefinition(u'test')

    structure_member_definition = data_types.StructureMemberDefinition(
        member_data_type_definition, u'my_struct_member',
        aliases=[u'MY_STRUCT_MEMBER'], data_type=u'test',
        description=u'my structure member')

    data_type_definition.AddMemberDefinition(structure_member_definition)

    struct_format_string = data_type_definition.GetStructFormatString()
    self.assertIsNone(struct_format_string)


@test_lib.skipUnlessHasTestFile([u'definitions', u'integers.yaml'])
class StructureMemberDefinitionTest(test_lib.BaseTestCase):
  """Structure member definition tests."""

  # pylint: disable=protected-access

  def testInitialize(self):
    """Tests the __init__ function."""
    definitions_file = self._GetTestFilePath([u'definitions', u'integers.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)
    member_data_type_definition = definitions_registry.GetDefinitionByName(
        u'int32')

    structure_member_definition = data_types.StructureMemberDefinition(
        member_data_type_definition, u'my_struct_member',
        aliases=[u'MY_STRUCT_MEMBER'], data_type=u'int32',
        description=u'my structure member')
    self.assertIsNotNone(structure_member_definition)

  def testGetByteSize(self):
    """Tests the GetByteSize function."""
    definitions_file = self._GetTestFilePath([u'definitions', u'integers.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)
    member_data_type_definition = definitions_registry.GetDefinitionByName(
        u'int32')

    structure_member_definition = data_types.StructureMemberDefinition(
        None, u'my_struct_member',
        aliases=[u'MY_STRUCT_MEMBER'], data_type=u'int32',
        description=u'my structure member')

    byte_size = structure_member_definition.GetByteSize()
    self.assertIsNone(byte_size)

    structure_member_definition._data_type_definition = (
        member_data_type_definition)
    byte_size = structure_member_definition.GetByteSize()
    self.assertEqual(byte_size, 4)

  def testGetStructFormatString(self):
    """Tests the GetStructFormatString function."""
    definitions_file = self._GetTestFilePath([u'definitions', u'integers.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)
    member_data_type_definition = definitions_registry.GetDefinitionByName(
        u'int32')

    structure_member_definition = data_types.StructureMemberDefinition(
        None, u'my_struct_member',
        aliases=[u'MY_STRUCT_MEMBER'], data_type=u'int32',
        description=u'my structure member')

    struct_format_string = structure_member_definition.GetStructFormatString()
    self.assertIsNone(struct_format_string)

    structure_member_definition._data_type_definition = (
        member_data_type_definition)
    struct_format_string = structure_member_definition.GetStructFormatString()
    self.assertEqual(struct_format_string, u'i')


class UUIDDefinitionTest(test_lib.BaseTestCase):
  """UUID data type definition tests."""

  def testInitialize(self):
    """Tests the __init__ function."""
    data_type_definition = data_types.UUIDDefinition(
        u'guid', aliases=[u'GUID'], description=u'GUID')
    self.assertIsNotNone(data_type_definition)

  def testGetStructFormatString(self):
    """Tests the GetStructFormatString function."""
    data_type_definition = data_types.UUIDDefinition(
        u'guid', aliases=[u'GUID'], description=u'GUID')

    struct_format_string = data_type_definition.GetStructFormatString()
    self.assertEqual(struct_format_string, u'IHH8B')


if __name__ == '__main__':
  unittest.main()
