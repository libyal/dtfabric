# -*- coding: utf-8 -*-
"""Tests for the data type definitions readers."""

import io
import unittest

from dtfabric import definitions
from dtfabric import errors
from dtfabric import reader
from dtfabric import registry

from tests import test_lib


class DataTypeDefinitionsFileReaderTest(test_lib.BaseTestCase):
  """Class to test the data type definitions reader."""

  # pylint: disable=protected-access

  def testReadPrimitiveDataTypeDefinition(self):
    """Tests the _ReadPrimitiveDataTypeDefinition function."""
    definition_values = {
        u'aliases': [u'LONG', u'LONG32'],
        u'attributes': {
            u'size': 4,
        },
        u'description': u'signed 32-bit integer',
    }

    definitions_registry = registry.DataTypeDefinitionsRegistry()
    definitions_reader = reader.DataTypeDefinitionsFileReader()

    data_type_definition = definitions_reader._ReadPrimitiveDataTypeDefinition(
        definitions_registry, definition_values, definitions.IntegerDefinition,
        u'int32')
    self.assertIsNotNone(data_type_definition)

  def testReadBooleanDataTypeDefinition(self):
    """Tests the _ReadBooleanDataTypeDefinition function."""
    definition_values = {
        u'aliases': [u'BOOL'],
        u'attributes': {
            u'size': 4,
        },
        u'description': u'boolean',
    }

    definitions_registry = registry.DataTypeDefinitionsRegistry()
    definitions_reader = reader.DataTypeDefinitionsFileReader()

    data_type_definition = definitions_reader._ReadBooleanDataTypeDefinition(
        definitions_registry, definition_values, u'bool')
    self.assertIsNotNone(data_type_definition)

  def testReadCharacterDataTypeDefinition(self):
    """Tests the _ReadCharacterDataTypeDefinition function."""
    definition_values = {
        u'aliases': [u'CHAR'],
        u'attributes': {
            u'size': 1,
        },
        u'description': u'character',
    }

    definitions_registry = registry.DataTypeDefinitionsRegistry()
    definitions_reader = reader.DataTypeDefinitionsFileReader()

    data_type_definition = definitions_reader._ReadCharacterDataTypeDefinition(
        definitions_registry, definition_values, u'char')
    self.assertIsNotNone(data_type_definition)

  def testReadEnumerationDataTypeDefinition(self):
    """Tests the _ReadEnumerationDataTypeDefinition function."""

    # TODO: implement.

  def testReadFormatDefinition(self):
    """Tests the _ReadFormatDefinition function."""

    # TODO: implement.

  def testReadIntegerDataTypeDefinition(self):
    """Tests the _ReadIntegerDataTypeDefinition function."""
    definition_values = {
        u'aliases': [u'LONG', u'LONG32'],
        u'attributes': {
            u'format': u'signed',
            u'size': 4,
        },
        u'description': u'signed 32-bit integer',
    }

    definitions_registry = registry.DataTypeDefinitionsRegistry()
    definitions_reader = reader.DataTypeDefinitionsFileReader()

    data_type_definition = definitions_reader._ReadIntegerDataTypeDefinition(
        definitions_registry, definition_values, u'int32')
    self.assertIsNotNone(data_type_definition)

    definition_values[u'attributes'][u'format'] = u'bogus'
    with self.assertRaises(errors.FormatError):
      definitions_reader._ReadIntegerDataTypeDefinition(
          definitions_registry, definition_values, u'int32')

  def testReadStructureDataTypeDefinition(self):
    """Tests the _ReadStructureDataTypeDefinition function."""

  # TODO: add test for _ReadStructureDataTypeDefinitionMember
  # TODO: add test for _ReadStructureDataTypeDefinitionMembers
  # TODO: add test for ReadDefinitionFromDict
  # TODO: add test for ReadDirectory
  # TODO: add test for ReadFile


class YAMLDataTypeDefinitionsFileReaderTest(test_lib.BaseTestCase):
  """Class to test the YAML data type definitions reader."""

  # pylint: disable=protected-access

  # TODO: add test for ReadDirectory

  def testReadFileObjectBoolean(self):
    """Tests the ReadFileObject function of a boolean data type."""
    definitions_registry = registry.DataTypeDefinitionsRegistry()
    definitions_reader = reader.YAMLDataTypeDefinitionsFileReader()

    yaml_data = b'\n'.join([
        b'name: bool',
        b'type: boolean',
        b'attributes:',
        b'  size: 1',
        b'  units: bytes'])

    file_object = io.BytesIO(initial_bytes=yaml_data)

    definitions_reader.ReadFileObject(definitions_registry, file_object)
    self.assertEqual(len(definitions_registry._definitions), 1)

    data_type_definition = definitions_registry.GetDefinitionByName(u'bool')
    self.assertIsInstance(data_type_definition, definitions.BooleanDefinition)
    self.assertEqual(data_type_definition.name, u'bool')
    self.assertEqual(data_type_definition.size, 1)
    self.assertEqual(data_type_definition.units, u'bytes')

    byte_size = data_type_definition.GetByteSize()
    self.assertEqual(byte_size, 1)

  def testReadFileObjectCharacter(self):
    """Tests the ReadFileObject function of a character data type."""
    definitions_registry = registry.DataTypeDefinitionsRegistry()
    definitions_reader = reader.YAMLDataTypeDefinitionsFileReader()

    yaml_data = b'\n'.join([
        b'name: char',
        b'type: character',
        b'attributes:',
        b'  size: 1',
        b'  units: bytes'])

    file_object = io.BytesIO(initial_bytes=yaml_data)

    definitions_reader.ReadFileObject(definitions_registry, file_object)
    self.assertEqual(len(definitions_registry._definitions), 1)

    data_type_definition = definitions_registry.GetDefinitionByName(u'char')
    self.assertIsInstance(data_type_definition, definitions.CharacterDefinition)
    self.assertEqual(data_type_definition.name, u'char')
    self.assertEqual(data_type_definition.size, 1)
    self.assertEqual(data_type_definition.units, u'bytes')

    byte_size = data_type_definition.GetByteSize()
    self.assertEqual(byte_size, 1)

  def testReadFileObjectInteger(self):
    """Tests the ReadFileObject function of an integer data type."""
    definitions_registry = registry.DataTypeDefinitionsRegistry()
    definitions_reader = reader.YAMLDataTypeDefinitionsFileReader()

    yaml_data = b'\n'.join([
        b'name: int8',
        b'type: integer',
        b'attributes:',
        b'  format: signed',
        b'  size: 1',
        b'  units: bytes'])

    file_object = io.BytesIO(initial_bytes=yaml_data)

    definitions_reader.ReadFileObject(definitions_registry, file_object)
    self.assertEqual(len(definitions_registry._definitions), 1)

    data_type_definition = definitions_registry.GetDefinitionByName(u'int8')
    self.assertIsInstance(data_type_definition, definitions.IntegerDefinition)
    self.assertEqual(data_type_definition.name, u'int8')
    self.assertEqual(data_type_definition.format, u'signed')
    self.assertEqual(data_type_definition.size, 1)
    self.assertEqual(data_type_definition.units, u'bytes')

    byte_size = data_type_definition.GetByteSize()
    self.assertEqual(byte_size, 1)

    # TODO: test format error, for incorrect format attribute.
    # TODO: test format error, for incorrect size attribute.

  def testReadFileObjectMissingName(self):
    """Tests the ReadFileObject function with a missing name."""
    definitions_registry = registry.DataTypeDefinitionsRegistry()
    definitions_reader = reader.YAMLDataTypeDefinitionsFileReader()

    yaml_data = b'\n'.join([
        b'type: integer',
        b'attributes:',
        b'  format: signed',
        b'  size: 1',
        b'  units: bytes'])

    file_object = io.BytesIO(initial_bytes=yaml_data)

    with self.assertRaises(errors.FormatError):
      definitions_reader.ReadFileObject(definitions_registry, file_object)

  def testReadFileObjectMissingType(self):
    """Tests the ReadFileObject function with a missing type."""
    definitions_registry = registry.DataTypeDefinitionsRegistry()
    definitions_reader = reader.YAMLDataTypeDefinitionsFileReader()

    yaml_data = b'\n'.join([
        b'name: int8',
        b'attributes:',
        b'  format: signed',
        b'  size: 1',
        b'  units: bytes'])

    file_object = io.BytesIO(initial_bytes=yaml_data)

    with self.assertRaises(errors.FormatError):
      definitions_reader.ReadFileObject(definitions_registry, file_object)

  def testReadFileObjectStructure(self):
    """Tests the ReadFileObject function of a structure data type."""
    definitions_registry = registry.DataTypeDefinitionsRegistry()
    definitions_reader = reader.YAMLDataTypeDefinitionsFileReader()

    url = (
        b'https://msdn.microsoft.com/en-us/library/windows/desktop/'
        b'ms680365(v=vs.85).aspx')

    yaml_data = b'\n'.join([
        b'name: uint32',
        b'type: integer',
        b'attributes:',
        b'  format: unsigned',
        b'  size: 4',
        b'  units: bytes',
        b'---',
        b'name: directory_descriptor',
        b'aliases: [MINIDUMP_DIRECTORY]',
        b'type: structure',
        b'description: Minidump file header',
        b'urls: [\'{0:s}\']'.format(url),
        b'members:',
        b'- name: stream_type',
        b'  aliases: [StreamType]',
        b'  data_type: uint32',
        b'- name: location',
        b'  aliases: [Location]',
        b'  data_type: uint32'])

    file_object = io.BytesIO(initial_bytes=yaml_data)

    definitions_reader.ReadFileObject(definitions_registry, file_object)
    self.assertEqual(len(definitions_registry._definitions), 2)

    data_type_definition = definitions_registry.GetDefinitionByName(
        u'directory_descriptor')
    self.assertIsInstance(
        data_type_definition, definitions.StructureDataTypeDefinition)
    self.assertEqual(data_type_definition.name, u'directory_descriptor')
    self.assertEqual(data_type_definition.description, u'Minidump file header')
    self.assertEqual(data_type_definition.aliases, [u'MINIDUMP_DIRECTORY'])
    self.assertEqual(data_type_definition.urls, [url])

    self.assertEqual(len(data_type_definition.members), 2)

    structure_member_definition = data_type_definition.members[0]
    self.assertIsInstance(
        structure_member_definition, definitions.StructureMemberDefinition)
    self.assertEqual(structure_member_definition.name, u'stream_type')
    self.assertEqual(structure_member_definition.aliases, [u'StreamType'])
    self.assertEqual(structure_member_definition.data_type, u'uint32')

    byte_size = data_type_definition.GetByteSize()
    self.assertEqual(byte_size, 8)

  def testReadFileObjectStructureWithSequence(self):
    """Tests the ReadFileObject function of a structure with a sequence."""
    definitions_registry = registry.DataTypeDefinitionsRegistry()
    definitions_reader = reader.YAMLDataTypeDefinitionsFileReader()

    url = (
        b'https://msdn.microsoft.com/en-us/library/windows/desktop/'
        b'ms680384(v=vs.85).aspx')

    yaml_data = b'\n'.join([
        b'name: string',
        b'aliases: [MINIDUMP_STRING]',
        b'type: structure',
        b'description: Minidump 64-bit memory descriptor',
        b'urls: [\'{0:s}\']'.format(url),
        b'members:',
        b'- name: data_size',
        b'  aliases: [Length]',
        b'  data_type: uint32',
        b'- sequence:',
        b'    name: data',
        b'    aliases: [Buffer]',
        b'    data_type: uint16',
        b'    data_size: data_size'])

    file_object = io.BytesIO(initial_bytes=yaml_data)

    definitions_reader.ReadFileObject(definitions_registry, file_object)
    self.assertEqual(len(definitions_registry._definitions), 1)

    data_type_definition = definitions_registry.GetDefinitionByName(
        u'string')
    self.assertIsInstance(
        data_type_definition, definitions.StructureDataTypeDefinition)
    self.assertEqual(data_type_definition.name, u'string')
    self.assertEqual(
        data_type_definition.description, u'Minidump 64-bit memory descriptor')
    self.assertEqual(data_type_definition.aliases, [u'MINIDUMP_STRING'])
    self.assertEqual(data_type_definition.urls, [url])

    self.assertEqual(len(data_type_definition.members), 2)

    structure_member_definition = data_type_definition.members[1]
    self.assertIsInstance(
        structure_member_definition,
        definitions.SequenceStructureMemberDefinition)
    self.assertEqual(structure_member_definition.name, u'data')
    self.assertEqual(structure_member_definition.aliases, [u'Buffer'])
    self.assertEqual(structure_member_definition.data_type, u'uint16')

    byte_size = data_type_definition.GetByteSize()
    self.assertIsNone(byte_size)


if __name__ == '__main__':
  unittest.main()
