# -*- coding: utf-8 -*-
"""Tests for the structure and type definitions."""

import unittest

from dtfabric import definitions

from tests import test_lib


# TODO: complete EnumerationDefinitionTest.
# TODO: complete FormatDefinitionTest.
# TODO: complete StructureDataTypeDefinitionTest.
# TODO: complete UnionStructureMemberDefinitionTest.


class TestDataTypeDefinition(definitions.DataTypeDefinition):
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
    data_type_definition = definitions.DataTypeDefinition(
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
    data_type_definition = definitions.FixedSizeDataTypeDefinition(
        u'int32', aliases=[u'LONG', u'LONG32'],
        description=u'signed 32-bit integer')
    self.assertIsNotNone(data_type_definition)

  def testGetAttributedNames(self):
    """Tests the GetAttributedNames function."""
    data_type_definition = definitions.FixedSizeDataTypeDefinition(
        u'int32', aliases=[u'LONG', u'LONG32'],
        description=u'signed 32-bit integer')

    attribute_names = data_type_definition.GetAttributedNames()
    self.assertEqual(attribute_names, [u'value'])

  def testGetByteSize(self):
    """Tests the GetByteSize function."""
    data_type_definition = definitions.FixedSizeDataTypeDefinition(
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
    data_type_definition = definitions.BooleanDefinition(
        u'bool32', aliases=[u'BOOL'], description=u'boolean')
    self.assertIsNotNone(data_type_definition)

  def testGetStructFormatString(self):
    """Tests the GetStructFormatString function."""
    data_type_definition = definitions.BooleanDefinition(
        u'bool32', aliases=[u'BOOL'], description=u'boolean')
    self.assertIsNotNone(data_type_definition)

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
    data_type_definition = definitions.CharacterDefinition(
        u'char', aliases=[u'CHAR'], description=u'character')
    self.assertIsNotNone(data_type_definition)

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


class EnumerationDefinitionTest(test_lib.BaseTestCase):
  """Enumeration data type definition tests."""

  def testGetStructFormatString(self):
    """Tests the GetStructFormatString function."""
    data_type_definition = definitions.EnumerationDefinition(
        u'enum', description=u'enumeration')
    self.assertIsNotNone(data_type_definition)

    struct_format_string = data_type_definition.GetStructFormatString()
    self.assertIsNone(struct_format_string)

    # TODO: implement


class FormatDefinitionTest(test_lib.BaseTestCase):
  """Data format definition tests."""

  def testGetStructFormatString(self):
    """Tests the GetStructFormatString function."""
    data_type_definition = definitions.FormatDefinition(
        u'format', description=u'data format')
    self.assertIsNotNone(data_type_definition)

    struct_format_string = data_type_definition.GetStructFormatString()
    self.assertIsNone(struct_format_string)

    # TODO: implement


class FloatingPointDefinitionTest(test_lib.BaseTestCase):
  """Floating-point data type definition tests."""

  def testGetStructFormatString(self):
    """Tests the GetStructFormatString function."""
    data_type_definition = definitions.FloatingPointDefinition(
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
    data_type_definition = definitions.IntegerDefinition(
        u'int32', aliases=[u'LONG', u'LONG32'],
        description=u'signed 32-bit integer')
    self.assertIsNotNone(data_type_definition)

  def testGetStructFormatString(self):
    """Tests the GetStructFormatString function."""
    data_type_definition = definitions.IntegerDefinition(
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


class StructureDataTypeDefinitionTest(test_lib.BaseTestCase):
  """Structure data type definition tests."""

  # pylint: disable=protected-access

  def testGetAttributedNames(self):
    """Tests the GetAttributedNames function."""
    data_type_definition = definitions.StructureDataTypeDefinition(
        u'my_struct_type', aliases=[u'MY_STRUCT_TYPE'],
        description=u'my structure type')

    attribute_names = data_type_definition.GetAttributedNames()
    self.assertEqual(attribute_names, [])

    definitions_file = self._GetTestFilePath([u'definitions', u'integers.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)
    member_data_type_definition = definitions_registry.GetDefinitionByName(
        u'int32')

    structure_member_definition = definitions.StructureMemberDefinition(
        member_data_type_definition, u'my_struct_member',
        aliases=[u'MY_STRUCT_MEMBER'], data_type=u'int32',
        description=u'my structure member')

    data_type_definition.AddMemberDefinition(structure_member_definition)

    attribute_names = data_type_definition.GetAttributedNames()
    self.assertEqual(attribute_names, [u'my_struct_member'])

  def testGetByteSize(self):
    """Tests the GetByteSize function."""
    data_type_definition = definitions.StructureDataTypeDefinition(
        u'my_struct_type', aliases=[u'MY_STRUCT_TYPE'],
        description=u'my structure type')

    byte_size = data_type_definition.GetByteSize()
    self.assertIsNone(byte_size)

    definitions_file = self._GetTestFilePath([u'definitions', u'integers.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)
    member_data_type_definition = definitions_registry.GetDefinitionByName(
        u'int32')

    structure_member_definition = definitions.StructureMemberDefinition(
        member_data_type_definition, u'my_struct_member',
        aliases=[u'MY_STRUCT_MEMBER'], data_type=u'int32',
        description=u'my structure member')

    data_type_definition.AddMemberDefinition(structure_member_definition)

    byte_size = data_type_definition.GetByteSize()
    self.assertEqual(byte_size, 4)

  def testGetStructFormatString(self):
    """Tests the GetStructFormatString function."""
    data_type_definition = definitions.StructureDataTypeDefinition(
        u'my_struct_type', aliases=[u'MY_STRUCT_TYPE'],
        description=u'my structure type')

    struct_format_string = data_type_definition.GetStructFormatString()
    self.assertIsNone(struct_format_string)

    definitions_file = self._GetTestFilePath([u'definitions', u'integers.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)
    member_data_type_definition = definitions_registry.GetDefinitionByName(
        u'int32')

    structure_member_definition = definitions.StructureMemberDefinition(
        member_data_type_definition, u'my_struct_member',
        aliases=[u'MY_STRUCT_MEMBER'], data_type=u'int32',
        description=u'my structure member')

    data_type_definition.AddMemberDefinition(structure_member_definition)

    struct_format_string = data_type_definition.GetStructFormatString()
    self.assertEqual(struct_format_string, u'i')

    # Test with member without a struct format string.

    data_type_definition = definitions.StructureDataTypeDefinition(
        u'my_struct_type', aliases=[u'MY_STRUCT_TYPE'],
        description=u'my structure type')

    member_data_type_definition = TestDataTypeDefinition(u'test')

    structure_member_definition = definitions.StructureMemberDefinition(
        member_data_type_definition, u'my_struct_member',
        aliases=[u'MY_STRUCT_MEMBER'], data_type=u'test',
        description=u'my structure member')

    data_type_definition.AddMemberDefinition(structure_member_definition)

    struct_format_string = data_type_definition.GetStructFormatString()
    self.assertIsNone(struct_format_string)


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

    structure_member_definition = definitions.StructureMemberDefinition(
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

    structure_member_definition = definitions.StructureMemberDefinition(
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

    structure_member_definition = definitions.StructureMemberDefinition(
        None, u'my_struct_member',
        aliases=[u'MY_STRUCT_MEMBER'], data_type=u'int32',
        description=u'my structure member')

    struct_format_string = structure_member_definition.GetStructFormatString()
    self.assertIsNone(struct_format_string)

    structure_member_definition._data_type_definition = (
        member_data_type_definition)
    struct_format_string = structure_member_definition.GetStructFormatString()
    self.assertEqual(struct_format_string, u'i')


class SequenceStructureMemberDefinitionTest(test_lib.BaseTestCase):
  """Sequence structure member definition tests."""

  def testInitialize(self):
    """Tests the __init__ function."""
    structure_member_definition = definitions.SequenceStructureMemberDefinition(
        u'my_struct_member', aliases=[u'MY_STRUCT_MEMBER'],
        data_type=u'int32', description=u'my sequence structure member')
    self.assertIsNotNone(structure_member_definition)

  def testGetByteSize(self):
    """Tests the GetByteSize function."""
    structure_member_definition = definitions.SequenceStructureMemberDefinition(
        u'my_struct_member', aliases=[u'MY_STRUCT_MEMBER'],
        data_type=u'int32', description=u'my sequence structure member')

    byte_size = structure_member_definition.GetByteSize()
    self.assertIsNone(byte_size)

    structure_member_definition.data_size = 4
    byte_size = structure_member_definition.GetByteSize()
    self.assertEqual(byte_size, 4)


class UnionStructureMemberDefinitionTest(test_lib.BaseTestCase):
  """Union structure member definition tests."""

  def testInitialize(self):
    """Tests the __init__ function."""
    structure_member_definition = definitions.UnionStructureMemberDefinition(
        u'my_struct_member', aliases=[u'MY_STRUCT_MEMBER'],
        data_type=u'int32', description=u'my union structure member')
    self.assertIsNotNone(structure_member_definition)

  def testGetByteSize(self):
    """Tests the GetByteSize function."""
    structure_member_definition = definitions.UnionStructureMemberDefinition(
        u'my_struct_member', aliases=[u'MY_STRUCT_MEMBER'],
        data_type=u'int32', description=u'my union structure member')

    byte_size = structure_member_definition.GetByteSize()
    self.assertIsNone(byte_size)

    # TODO: change test when code is implemented


class UUIDDefinitionTest(test_lib.BaseTestCase):
  """UUID data type definition tests."""

  def testInitialize(self):
    """Tests the __init__ function."""
    data_type_definition = definitions.UUIDDefinition(
        u'guid', aliases=[u'GUID'], description=u'GUID')
    self.assertIsNotNone(data_type_definition)

  def testGetStructFormatString(self):
    """Tests the GetStructFormatString function."""
    data_type_definition = definitions.UUIDDefinition(
        u'guid', aliases=[u'GUID'], description=u'GUID')
    self.assertIsNotNone(data_type_definition)

    struct_format_string = data_type_definition.GetStructFormatString()
    self.assertEqual(struct_format_string, u'IHH8B')


if __name__ == '__main__':
  unittest.main()
