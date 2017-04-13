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
  """Data type definitions reader tests."""

  # pylint: disable=protected-access

  def testReadFixedSizeDataTypeDefinition(self):
    """Tests the _ReadFixedSizeDataTypeDefinition function."""
    definition_values = {
        u'aliases': [u'LONG', u'LONG32'],
        u'attributes': {
            u'byte_order': u'little-endian',
            u'size': 4,
        },
        u'description': u'signed 32-bit integer type',
    }

    definitions_registry = registry.DataTypeDefinitionsRegistry()
    definitions_reader = reader.DataTypeDefinitionsFileReader()

    data_type_definition = definitions_reader._ReadFixedSizeDataTypeDefinition(
        definitions_registry, definition_values, definitions.IntegerDefinition,
        u'int32')
    self.assertIsNotNone(data_type_definition)
    self.assertIsInstance(data_type_definition, definitions.IntegerDefinition)
    self.assertEqual(
        data_type_definition.byte_order, definitions.BYTE_ORDER_LITTLE_ENDIAN)
    self.assertEqual(data_type_definition.size, 4)

    # Test with incorrect byte-order.
    definition_values = {
        u'aliases': [u'LONG', u'LONG32'],
        u'attributes': {
            u'byte_order': u'bogus',
            u'size': 4,
        },
        u'description': u'signed 32-bit integer type',
    }

    definitions_registry = registry.DataTypeDefinitionsRegistry()
    definitions_reader = reader.DataTypeDefinitionsFileReader()

    with self.assertRaises(errors.FormatError):
      definitions_reader._ReadFixedSizeDataTypeDefinition(
          definitions_registry, definition_values, definitions.IntegerDefinition,
          u'int32')

  def testReadBooleanDataTypeDefinition(self):
    """Tests the _ReadBooleanDataTypeDefinition function."""
    definition_values = {
        u'aliases': [u'BOOL'],
        u'attributes': {
            u'size': 4,
        },
        u'description': u'32-bit boolean type',
    }

    definitions_registry = registry.DataTypeDefinitionsRegistry()
    definitions_reader = reader.DataTypeDefinitionsFileReader()

    data_type_definition = definitions_reader._ReadBooleanDataTypeDefinition(
        definitions_registry, definition_values, u'bool')
    self.assertIsNotNone(data_type_definition)
    self.assertIsInstance(data_type_definition, definitions.BooleanDefinition)

  def testReadCharacterDataTypeDefinition(self):
    """Tests the _ReadCharacterDataTypeDefinition function."""
    definition_values = {
        u'aliases': [u'CHAR'],
        u'attributes': {
            u'size': 1,
        },
        u'description': u'8-bit character type',
    }

    definitions_registry = registry.DataTypeDefinitionsRegistry()
    definitions_reader = reader.DataTypeDefinitionsFileReader()

    data_type_definition = definitions_reader._ReadCharacterDataTypeDefinition(
        definitions_registry, definition_values, u'char')
    self.assertIsNotNone(data_type_definition)
    self.assertIsInstance(data_type_definition, definitions.CharacterDefinition)

  def testReadEnumerationDataTypeDefinition(self):
    """Tests the _ReadEnumerationDataTypeDefinition function."""
    definition_values = {
        u'description': u'Minidump object information type',
        u'members': {
            u'description': u'No object-specific information available',
            u'name': u'MiniHandleObjectInformationNone',
            u'value': 0,
        },
    }

    definitions_registry = registry.DataTypeDefinitionsRegistry()
    definitions_reader = reader.DataTypeDefinitionsFileReader()

    data_type_definition = (
        definitions_reader._ReadEnumerationDataTypeDefinition(
            definitions_registry, definition_values, u'enum'))
    self.assertIsNotNone(data_type_definition)
    self.assertIsInstance(
        data_type_definition, definitions.EnumerationDefinition)

  def testReadFloatingPointDataTypeDefinition(self):
    """Tests the _ReadFloatingPointDataTypeDefinition function."""
    definition_values = {
        u'aliases': [u'float', u'FLOAT'],
        u'attributes': {
            u'size': 4,
        },
        u'description': u'32-bit floating-point type',
    }

    definitions_registry = registry.DataTypeDefinitionsRegistry()
    definitions_reader = reader.DataTypeDefinitionsFileReader()

    data_type_definition = (
        definitions_reader._ReadFloatingPointDataTypeDefinition(
            definitions_registry, definition_values, u'float32'))
    self.assertIsNotNone(data_type_definition)
    self.assertIsInstance(
        data_type_definition, definitions.FloatingPointDefinition)

  def testReadFormatDefinition(self):
    """Tests the _ReadFormatDefinition function."""
    definition_values = {
        u'description': u'Windows Shortcut (LNK) file format',
        u'type': u'format',
    }

    definitions_registry = registry.DataTypeDefinitionsRegistry()
    definitions_reader = reader.DataTypeDefinitionsFileReader()

    # TODO: implement.
    _ = definitions_registry

    data_type_definition = definitions_reader._ReadFormatDefinition(
        definition_values, u'lnk')
    self.assertIsNotNone(data_type_definition)
    self.assertIsInstance(data_type_definition, definitions.FormatDefinition)

  def testReadIntegerDataTypeDefinition(self):
    """Tests the _ReadIntegerDataTypeDefinition function."""
    definition_values = {
        u'aliases': [u'LONG', u'LONG32'],
        u'attributes': {
            u'format': u'signed',
            u'size': 4,
        },
        u'description': u'signed 32-bit integer type',
    }

    definitions_registry = registry.DataTypeDefinitionsRegistry()
    definitions_reader = reader.DataTypeDefinitionsFileReader()

    data_type_definition = definitions_reader._ReadIntegerDataTypeDefinition(
        definitions_registry, definition_values, u'int32')
    self.assertIsNotNone(data_type_definition)
    self.assertIsInstance(data_type_definition, definitions.IntegerDefinition)

    definition_values[u'attributes'][u'format'] = u'bogus'
    with self.assertRaises(errors.FormatError):
      definitions_reader._ReadIntegerDataTypeDefinition(
          definitions_registry, definition_values, u'int32')

  def testReadStructureDataTypeDefinition(self):
    """Tests the _ReadStructureDataTypeDefinition function."""

    # TODO: implement.

  # TODO: add test for _ReadStructureDataTypeDefinitionMember
  # TODO: add test for _ReadStructureDataTypeDefinitionMembers

  def testReadUUIDDataTypeDefinition(self):
    """Tests the _ReadUUIDDataTypeDefinition function."""
    definition_values = {
        u'aliases': [u'guid', u'GUID', u'UUID'],
        u'description': (
            u'Globally or Universal unique identifier (GUID or UUID) type'),
    }

    definitions_registry = registry.DataTypeDefinitionsRegistry()
    definitions_reader = reader.DataTypeDefinitionsFileReader()

    data_type_definition = definitions_reader._ReadCharacterDataTypeDefinition(
        definitions_registry, definition_values, u'char')
    self.assertIsNotNone(data_type_definition)
    self.assertIsInstance(data_type_definition, definitions.CharacterDefinition)

  def testReadDefinitionFromDict(self):
    """Tests the ReadDefinitionFromDict function."""
    definition_values = {
        u'aliases': [u'LONG', u'LONG32'],
        u'attributes': {
            u'format': u'signed',
            u'size': 4,
        },
        u'description': u'signed 32-bit integer type',
        u'name': u'int32',
        u'type': u'integer',
    }

    definitions_registry = registry.DataTypeDefinitionsRegistry()
    definitions_reader = reader.DataTypeDefinitionsFileReader()

    data_type_definition = definitions_reader.ReadDefinitionFromDict(
        definitions_registry, definition_values)
    self.assertIsNotNone(data_type_definition)
    self.assertIsInstance(data_type_definition, definitions.IntegerDefinition)

    with self.assertRaises(errors.FormatError):
      definitions_reader.ReadDefinitionFromDict(definitions_registry, None)

    definition_values[u'type'] = u'bogus'
    with self.assertRaises(errors.FormatError):
      definitions_reader.ReadDefinitionFromDict(
          definitions_registry, definition_values)

  def testReadDirectory(self):
    """Tests the ReadDirectory function."""
    definitions_directory = self._GetTestFilePath([u'definitions'])

    definitions_registry = registry.DataTypeDefinitionsRegistry()
    definitions_reader = reader.DataTypeDefinitionsFileReader()

    definitions_reader.ReadDirectory(
        definitions_registry, definitions_directory)

    definitions_reader.ReadDirectory(
        definitions_registry, definitions_directory, extension=u'yaml')

  def testReadFile(self):
    """Tests the ReadFile function."""
    definitions_file = self._GetTestFilePath([u'definitions', u'integers.yaml'])

    definitions_registry = registry.DataTypeDefinitionsRegistry()
    definitions_reader = reader.DataTypeDefinitionsFileReader()

    definitions_reader.ReadFile(definitions_registry, definitions_file)


class YAMLDataTypeDefinitionsFileReaderTest(test_lib.BaseTestCase):
  """YAML data type definitions reader tests."""

  # pylint: disable=protected-access

  def testReadDirectory(self):
    """Tests the ReadDirectory function."""
    definitions_directory = self._GetTestFilePath([u'definitions'])

    definitions_registry = registry.DataTypeDefinitionsRegistry()
    definitions_reader = reader.YAMLDataTypeDefinitionsFileReader()

    definitions_reader.ReadDirectory(
        definitions_registry, definitions_directory)

  def testReadFileObjectBoolean(self):
    """Tests the ReadFileObject function of a boolean data type."""
    definitions_registry = registry.DataTypeDefinitionsRegistry()
    definitions_reader = reader.YAMLDataTypeDefinitionsFileReader()

    yaml_data = u'\n'.join([
        u'name: bool',
        u'type: boolean',
        u'attributes:',
        u'  size: 1',
        u'  units: bytes']).encode(u'ascii')

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

    yaml_data = u'\n'.join([
        u'name: char',
        u'type: character',
        u'attributes:',
        u'  size: 1',
        u'  units: bytes']).encode(u'ascii')

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

    yaml_data = u'\n'.join([
        u'name: int32',
        u'type: integer',
        u'attributes:',
        u'  byte_order: little-endian',
        u'  format: signed',
        u'  size: 4',
        u'  units: bytes']).encode(u'ascii')

    file_object = io.BytesIO(initial_bytes=yaml_data)

    definitions_reader.ReadFileObject(definitions_registry, file_object)
    self.assertEqual(len(definitions_registry._definitions), 1)

    data_type_definition = definitions_registry.GetDefinitionByName(u'int32')
    self.assertIsInstance(data_type_definition, definitions.IntegerDefinition)
    self.assertEqual(data_type_definition.name, u'int32')
    self.assertEqual(
        data_type_definition.byte_order, definitions.BYTE_ORDER_LITTLE_ENDIAN)
    self.assertEqual(data_type_definition.format, u'signed')
    self.assertEqual(data_type_definition.size, 4)
    self.assertEqual(data_type_definition.units, u'bytes')

    byte_size = data_type_definition.GetByteSize()
    self.assertEqual(byte_size, 4)

    # TODO: test format error, for incorrect format attribute.
    # TODO: test format error, for incorrect size attribute.

  def testReadFileObjectMissingName(self):
    """Tests the ReadFileObject function with a missing name."""
    definitions_registry = registry.DataTypeDefinitionsRegistry()
    definitions_reader = reader.YAMLDataTypeDefinitionsFileReader()

    yaml_data = u'\n'.join([
        u'type: integer',
        u'attributes:',
        u'  format: signed',
        u'  size: 1',
        u'  units: bytes']).encode(u'ascii')

    file_object = io.BytesIO(initial_bytes=yaml_data)

    with self.assertRaises(errors.FormatError):
      definitions_reader.ReadFileObject(definitions_registry, file_object)

  def testReadFileObjectMissingType(self):
    """Tests the ReadFileObject function with a missing type."""
    definitions_registry = registry.DataTypeDefinitionsRegistry()
    definitions_reader = reader.YAMLDataTypeDefinitionsFileReader()

    yaml_data = u'\n'.join([
        u'name: int8',
        u'attributes:',
        u'  format: signed',
        u'  size: 1',
        u'  units: bytes']).encode(u'ascii')

    file_object = io.BytesIO(initial_bytes=yaml_data)

    with self.assertRaises(errors.FormatError):
      definitions_reader.ReadFileObject(definitions_registry, file_object)

    yaml_data = u'\n'.join([
        u'name: int8',
        u'type: integer',
        u'attributes:',
        u'  format: signed',
        u'  size: 1',
        u'  units: bytes',
        u'---',
        u'name: int16',
        u'attributes:',
        u'  format: signed',
        u'  size: 2',
        u'  units: bytes']).encode(u'ascii')

    file_object = io.BytesIO(initial_bytes=yaml_data)

    with self.assertRaises(errors.FormatError):
      definitions_reader.ReadFileObject(definitions_registry, file_object)

  def testReadFileObjectStructure(self):
    """Tests the ReadFileObject function of a structure data type."""
    definitions_registry = registry.DataTypeDefinitionsRegistry()
    definitions_reader = reader.YAMLDataTypeDefinitionsFileReader()

    url = (
        u'https://msdn.microsoft.com/en-us/library/windows/desktop/'
        u'ms680365(v=vs.85).aspx')

    yaml_data = u'\n'.join([
        u'name: uint32',
        u'type: integer',
        u'attributes:',
        u'  format: unsigned',
        u'  size: 4',
        u'  units: bytes',
        u'---',
        u'name: directory_descriptor',
        u'aliases: [MINIDUMP_DIRECTORY]',
        u'type: structure',
        u'description: Minidump file header',
        u'urls: [\'{0:s}\']'.format(url),
        u'members:',
        u'- name: stream_type',
        u'  aliases: [StreamType]',
        u'  data_type: uint32',
        u'- name: location',
        u'  aliases: [Location]',
        u'  data_type: uint32']).encode(u'ascii')

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
    definitions_file = self._GetTestFilePath([u'definitions', u'integers.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)
    self.assertEqual(len(definitions_registry._definitions), 8)

    definitions_reader = reader.YAMLDataTypeDefinitionsFileReader()

    url = (
        u'https://msdn.microsoft.com/en-us/library/windows/desktop/'
        u'ms680384(v=vs.85).aspx')

    yaml_data = u'\n'.join([
        u'name: string',
        u'aliases: [MINIDUMP_STRING]',
        u'type: structure',
        u'description: Minidump 64-bit memory descriptor',
        u'urls: [\'{0:s}\']'.format(url),
        u'members:',
        u'- name: data_size',
        u'  aliases: [Length]',
        u'  data_type: uint32',
        u'- sequence:',
        u'    name: data',
        u'    aliases: [Buffer]',
        u'    data_type: uint16',
        u'    data_size: data_size']).encode(u'ascii')

    file_object = io.BytesIO(initial_bytes=yaml_data)

    definitions_reader.ReadFileObject(definitions_registry, file_object)
    self.assertEqual(len(definitions_registry._definitions), 9)

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
