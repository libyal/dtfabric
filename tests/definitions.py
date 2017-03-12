# -*- coding: utf-8 -*-
"""Tests for the structure and type definitions."""

import unittest

from dtfabric import definitions

from tests import test_lib


class PrimitiveDataTypeDefinitionTest(test_lib.BaseTestCase):
  """Class to test the primitive data type definition."""

  def testInitialize(self):
    """Tests the initialize function."""
    data_type_definition = definitions.PrimitiveDataTypeDefinition(
        u'int32', aliases=[u'LONG', u'LONG32'],
        description=u'signed 32-bit integer')
    self.assertIsNotNone(data_type_definition)

  def testGetByteSize(self):
    """Tests the GetByteSize function."""
    data_type_definition = definitions.PrimitiveDataTypeDefinition(
        u'int32', aliases=[u'LONG', u'LONG32'],
        description=u'signed 32-bit integer')

    byte_size = data_type_definition.GetByteSize()
    self.assertIsNone(byte_size)

    data_type_definition.size = 4
    byte_size = data_type_definition.GetByteSize()
    self.assertEqual(byte_size, 4)


class BooleanDefinitionTest(test_lib.BaseTestCase):
  """Class to test the boolean data type definition."""

  def testInitialize(self):
    """Tests the initialize function."""
    data_type_definition = definitions.BooleanDefinition(
        u'bool', aliases=[u'BOOL'], description=u'boolean')
    self.assertIsNotNone(data_type_definition)


class CharacterDefinitionTest(test_lib.BaseTestCase):
  """Class to test the character data type definition."""

  def testInitialize(self):
    """Tests the initialize function."""
    data_type_definition = definitions.CharacterDefinition(
        u'char', aliases=[u'CHAR'], description=u'character')
    self.assertIsNotNone(data_type_definition)


class EnumerationDefinitionTest(test_lib.BaseTestCase):
  """Class to test the enumeration data type definition."""

  def testInitialize(self):
    """Tests the initialize function."""
    data_type_definition = definitions.EnumerationDefinition(
        u'enum', description=u'enumeration')
    self.assertIsNotNone(data_type_definition)


class FloatingPointDefinitionTest(test_lib.BaseTestCase):
  """Class to test the floating-point data type definition."""

  def testInitialize(self):
    """Tests the initialize function."""
    data_type_definition = definitions.FloatingPointDefinition(
        u'float', aliases=[u'FLOAT'], description=u'32-bit floating-point')
    self.assertIsNotNone(data_type_definition)


class IntegerDefinitionTest(test_lib.BaseTestCase):
  """Class to test the integer data type definition."""

  def testInitialize(self):
    """Tests the initialize function."""
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
  """Class to test the structure data type definition."""

  def testInitialize(self):
    """Tests the initialize function."""
    data_type_definition = definitions.StructureDataTypeDefinition(
        u'my_struct_type', aliases=[u'MY_STRUCT_TYPE'],
        description=u'my structure type')
    self.assertIsNotNone(data_type_definition)

  def testGetByteSize(self):
    """Tests the GetByteSize function."""
    data_type_definition = definitions.StructureDataTypeDefinition(
        u'my_struct_type', aliases=[u'MY_STRUCT_TYPE'],
        description=u'my structure type')

    byte_size = data_type_definition.GetByteSize()
    self.assertIsNone(byte_size)

    # TODO: test struct with members.

  # TODO: add SetDataTypeDefinitionsRegistry test.


class StructureMemberDefinitionTest(test_lib.BaseTestCase):
  """Class to test the structure member definition."""

  def testInitialize(self):
    """Tests the initialize function."""
    member_definition = definitions.StructureMemberDefinition(
        u'my_struct_member', aliases=[u'MY_STRUCT_MEMBER'],
        data_type=u'int32', description=u'my sequence structure member')
    self.assertIsNotNone(member_definition)

  def testGetByteSize(self):
    """Tests the GetByteSize function."""
    member_definition = definitions.SequenceStructureMemberDefinition(
        u'my_struct_member', aliases=[u'MY_STRUCT_MEMBER'],
        data_type=u'int32', description=u'my sequence structure member')

    byte_size = member_definition.GetByteSize()
    self.assertIsNone(byte_size)

    member_definition.data_size = 4
    byte_size = member_definition.GetByteSize()
    self.assertEqual(byte_size, 4)


class SequenceStructureMemberDefinitionTest(test_lib.BaseTestCase):
  """Class to test the sequence structure member definition."""

  def testInitialize(self):
    """Tests the initialize function."""
    member_definition = definitions.SequenceStructureMemberDefinition(
        u'my_struct_member', aliases=[u'MY_STRUCT_MEMBER'],
        data_type=u'int32', description=u'my sequence structure member')
    self.assertIsNotNone(member_definition)

  def testGetByteSize(self):
    """Tests the GetByteSize function."""
    member_definition = definitions.SequenceStructureMemberDefinition(
        u'my_struct_member', aliases=[u'MY_STRUCT_MEMBER'],
        data_type=u'int32', description=u'my sequence structure member')

    byte_size = member_definition.GetByteSize()
    self.assertIsNone(byte_size)

    member_definition.data_size = 4
    byte_size = member_definition.GetByteSize()
    self.assertEqual(byte_size, 4)


class UnionStructureMemberDefinitionTest(test_lib.BaseTestCase):
  """Class to test the union structure member definition."""

  def testInitialize(self):
    """Tests the initialize function."""
    member_definition = definitions.UnionStructureMemberDefinition(
        u'my_struct_member', aliases=[u'MY_STRUCT_MEMBER'],
        data_type=u'int32', description=u'my union structure member')
    self.assertIsNotNone(member_definition)

  def testGetByteSize(self):
    """Tests the GetByteSize function."""
    member_definition = definitions.UnionStructureMemberDefinition(
        u'my_struct_member', aliases=[u'MY_STRUCT_MEMBER'],
        data_type=u'int32', description=u'my union structure member')

    byte_size = member_definition.GetByteSize()
    self.assertIsNone(byte_size)

    # TODO: change test when code is implemented


if __name__ == '__main__':
  unittest.main()
