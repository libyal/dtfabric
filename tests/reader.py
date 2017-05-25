# -*- coding: utf-8 -*-
"""Tests for the data type definitions readers."""

import io
import unittest

from dtfabric import data_types
from dtfabric import definitions
from dtfabric import errors
from dtfabric import reader
from dtfabric import registry

from tests import test_lib


# TODO: test errors, such as duplicate structure members.


class DataTypeDefinitionsReaderTest(test_lib.BaseTestCase):
  """Data type definitions reader tests."""

  # pylint: disable=protected-access

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
    definitions_reader = reader.DataTypeDefinitionsReader()

    data_type_definition = definitions_reader._ReadBooleanDataTypeDefinition(
        definitions_registry, definition_values, u'bool')
    self.assertIsNotNone(data_type_definition)
    self.assertIsInstance(data_type_definition, data_types.BooleanDefinition)

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
    definitions_reader = reader.DataTypeDefinitionsReader()

    data_type_definition = definitions_reader._ReadCharacterDataTypeDefinition(
        definitions_registry, definition_values, u'char')
    self.assertIsNotNone(data_type_definition)
    self.assertIsInstance(data_type_definition, data_types.CharacterDefinition)

  def testReadConstantDataTypeDefinition(self):
    """Tests the _ReadConstantDataTypeDefinition function."""
    definition_values = {
        u'aliases': [u'AVRF_MAX_TRACES'],
        u'description': (
            u'Application verifier resource enumeration maximum number of '
            u'back traces'),
        u'value': 32,
    }

    definitions_registry = registry.DataTypeDefinitionsRegistry()
    definitions_reader = reader.DataTypeDefinitionsReader()

    data_type_definition = (
        definitions_reader._ReadConstantDataTypeDefinition(
            definitions_registry, definition_values, u'const'))
    self.assertIsNotNone(data_type_definition)
    self.assertIsInstance(data_type_definition, data_types.ConstantDefinition)

    # Test with missing value definition.
    del definition_values[u'value']

    with self.assertRaises(errors.DefinitionReaderError):
      definitions_reader._ReadConstantDataTypeDefinition(
          definitions_registry, definition_values, u'const')

  def testReadDataTypeDefinition(self):
    """Tests the _ReadDataTypeDefinition function."""
    definition_values = {
        u'aliases': [u'LONG', u'LONG32'],
        u'description': u'signed 32-bit integer type',
    }

    definitions_registry = registry.DataTypeDefinitionsRegistry()
    definitions_reader = reader.DataTypeDefinitionsReader()

    data_type_definition = definitions_reader._ReadDataTypeDefinition(
        definitions_registry, definition_values, data_types.IntegerDefinition,
        u'int32')
    self.assertIsNotNone(data_type_definition)
    self.assertIsInstance(data_type_definition, data_types.IntegerDefinition)

  def testReadDataTypeDefinitionWithMembers(self):
    """Tests the _ReadDataTypeDefinitionWithMembers function."""
    definition_values = {
        u'aliases': [u'POINT'],
        u'attributes': {
            u'byte_order': u'big-endian',
        },
        u'description': u'Point in 3 dimensional space.',
        u'members': [
            {u'name': u'x', u'data_type': u'int32'},
            {u'name': u'y', u'data_type': u'int32'},
            {u'name': u'z', u'data_type': u'int32'}],
    }

    definitions_file = self._GetTestFilePath([u'definitions', u'integers.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)
    definitions_reader = reader.DataTypeDefinitionsReader()

    definition_object = definitions_reader._ReadDataTypeDefinitionWithMembers(
        definitions_registry, definition_values, data_types.StructureDefinition,
        u'point3d')
    self.assertIsNotNone(definition_object)

  @test_lib.skipUnlessHasTestFile([u'definitions', u'integers.yaml'])
  def testReadElementSequenceDataTypeDefinition(self):
    """Tests the _ReadElementSequenceDataTypeDefinition function."""
    definition_values = {
        u'description': u'vector with 4 elements',
        u'element_data_type': u'int32',
        u'number_of_elements': 4,
    }

    definitions_file = self._GetTestFilePath([u'definitions', u'integers.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)
    definitions_reader = reader.DataTypeDefinitionsReader()

    data_type_definition = (
        definitions_reader._ReadElementSequenceDataTypeDefinition(
            definitions_registry, definition_values,
            data_types.SequenceDefinition, u'vector4'))
    self.assertIsNotNone(data_type_definition)
    self.assertIsInstance(data_type_definition, data_types.SequenceDefinition)

    # Test with attributes.
    definition_values[u'attributes'] = {}

    with self.assertRaises(errors.DefinitionReaderError):
      definitions_reader._ReadElementSequenceDataTypeDefinition(
          definitions_registry, definition_values,
          data_types.SequenceDefinition, u'vector4')

    definition_values[u'attributes'] = None

    # Test with undefined element data type.
    definition_values[u'element_data_type'] = u'bogus'

    with self.assertRaises(errors.DefinitionReaderError):
      definitions_reader._ReadElementSequenceDataTypeDefinition(
          definitions_registry, definition_values,
          data_types.SequenceDefinition, u'vector4')

    definition_values[u'element_data_type'] = u'int32'

    # Test with missing element data type definition.
    del definition_values[u'element_data_type']

    with self.assertRaises(errors.DefinitionReaderError):
      definitions_reader._ReadElementSequenceDataTypeDefinition(
          definitions_registry, definition_values,
          data_types.SequenceDefinition, u'vector4')

    definition_values[u'element_data_type'] = u'int32'

    # Test with missing number of elements definition.
    del definition_values[u'number_of_elements']

    with self.assertRaises(errors.DefinitionReaderError):
      definitions_reader._ReadElementSequenceDataTypeDefinition(
          definitions_registry, definition_values,
          data_types.SequenceDefinition, u'vector4')

    definition_values[u'number_of_elements'] = 4

    # Test with unusuported attributes definition.
    definition_values[u'attributes'] = {u'byte_order': u'little-endian'}

    with self.assertRaises(errors.DefinitionReaderError):
      definitions_reader._ReadElementSequenceDataTypeDefinition(
          definitions_registry, definition_values,
          data_types.SequenceDefinition, u'vector4')

    del definition_values[u'attributes']

  def testReadEnumerationDataTypeDefinition(self):
    """Tests the _ReadEnumerationDataTypeDefinition function."""
    definition_values = {
        u'description': u'Minidump object information type',
        u'values': [
            {u'description': u'No object-specific information available',
             u'name': u'MiniHandleObjectInformationNone',
             u'number': 0},
            {u'description': u'Thread object information',
             u'name': u'MiniThreadInformation1',
             u'number': 1},
        ],
    }

    definitions_registry = registry.DataTypeDefinitionsRegistry()
    definitions_reader = reader.DataTypeDefinitionsReader()

    data_type_definition = (
        definitions_reader._ReadEnumerationDataTypeDefinition(
            definitions_registry, definition_values, u'enum'))
    self.assertIsNotNone(data_type_definition)
    self.assertIsInstance(
        data_type_definition, data_types.EnumerationDefinition)

    # Test with missing name in enumeration value definition.
    del definition_values[u'values'][-1][u'name']

    with self.assertRaises(errors.DefinitionReaderError):
      definitions_reader._ReadEnumerationDataTypeDefinition(
          definitions_registry, definition_values, u'enum')

    definition_values[u'values'][-1][u'name'] = u'MiniThreadInformation1'

    # Test with missing value in enumeration number definition.
    del definition_values[u'values'][-1][u'number']

    with self.assertRaises(errors.DefinitionReaderError):
      definitions_reader._ReadEnumerationDataTypeDefinition(
          definitions_registry, definition_values, u'enum')

    definition_values[u'values'][-1][u'number'] = 1

    # Test with duplicate enumeration number definition.
    definition_values[u'values'].append({
        u'description': u'Thread object information',
        u'name': u'MiniThreadInformation1',
        u'number': 1})

    with self.assertRaises(errors.DefinitionReaderError):
      definitions_reader._ReadEnumerationDataTypeDefinition(
          definitions_registry, definition_values, u'enum')

    del definition_values[u'values'][-1]

    # Test with missing enumeration values definitions.
    del definition_values[u'values']

    with self.assertRaises(errors.DefinitionReaderError):
      definitions_reader._ReadEnumerationDataTypeDefinition(
          definitions_registry, definition_values, u'enum')

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
    definitions_reader = reader.DataTypeDefinitionsReader()

    data_type_definition = definitions_reader._ReadFixedSizeDataTypeDefinition(
        definitions_registry, definition_values, data_types.IntegerDefinition,
        u'int32')
    self.assertIsNotNone(data_type_definition)
    self.assertIsInstance(data_type_definition, data_types.IntegerDefinition)
    self.assertEqual(data_type_definition.size, 4)

    # Test with incorrect size.
    definition_values[u'attributes'][u'size'] = u'bogus'

    with self.assertRaises(errors.DefinitionReaderError):
      definitions_reader._ReadFixedSizeDataTypeDefinition(
          definitions_registry, definition_values, data_types.IntegerDefinition,
          u'int32')

    definition_values[u'attributes'][u'size'] = 4

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
    definitions_reader = reader.DataTypeDefinitionsReader()

    data_type_definition = (
        definitions_reader._ReadFloatingPointDataTypeDefinition(
            definitions_registry, definition_values, u'float32'))
    self.assertIsNotNone(data_type_definition)
    self.assertIsInstance(
        data_type_definition, data_types.FloatingPointDefinition)

  def testReadFormatDataTypeDefinition(self):
    """Tests the _ReadFormatDataTypeDefinition function."""
    definition_values = {
        u'description': u'Windows Shortcut (LNK) file format',
        u'type': u'format',
    }

    definitions_registry = registry.DataTypeDefinitionsRegistry()
    definitions_reader = reader.DataTypeDefinitionsReader()

    data_type_definition = definitions_reader._ReadFormatDataTypeDefinition(
        definitions_registry, definition_values, u'lnk')
    self.assertIsNotNone(data_type_definition)
    self.assertIsInstance(data_type_definition, data_types.FormatDefinition)

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
    definitions_reader = reader.DataTypeDefinitionsReader()

    data_type_definition = definitions_reader._ReadIntegerDataTypeDefinition(
        definitions_registry, definition_values, u'int32')
    self.assertIsNotNone(data_type_definition)
    self.assertIsInstance(data_type_definition, data_types.IntegerDefinition)

    # Test with unsupported format attribute.
    definition_values[u'attributes'][u'format'] = u'bogus'

    with self.assertRaises(errors.DefinitionReaderError):
      definitions_reader._ReadIntegerDataTypeDefinition(
          definitions_registry, definition_values, u'int32')

  def testReadLayoutDataTypeDefinition(self):
    """Tests the _ReadLayoutDataTypeDefinition function."""
    definition_values = {
        u'description': u'layout data type',
        u'attributes': {
            u'byte_order': u'little-endian',
        },
    }

    definitions_registry = registry.DataTypeDefinitionsRegistry()
    definitions_reader = reader.DataTypeDefinitionsReader()

    data_type_definition = definitions_reader._ReadLayoutDataTypeDefinition(
        definitions_registry, definition_values,
        data_types.EnumerationDefinition, u'format')
    self.assertIsNotNone(data_type_definition)
    self.assertIsInstance(
        data_type_definition, data_types.EnumerationDefinition)

  @test_lib.skipUnlessHasTestFile([u'definitions', u'integers.yaml'])
  def testReadMemberDataTypeDefinitionMember(self):
    """Tests the _ReadMemberDataTypeDefinitionMember function."""
    definition_values = {u'name': u'x', u'data_type': u'int32'}

    definition_object = data_types.StructureDefinition(u'point3d')

    definitions_file = self._GetTestFilePath([u'definitions', u'integers.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)
    definitions_reader = reader.DataTypeDefinitionsReader()

    definitions_reader._ReadMemberDataTypeDefinitionMember(
        definitions_registry, definition_values, u'point3d')

    # TODO: implement.
    _ = definition_object

  def testReadSemanticDataTypeDefinition(self):
    """Tests the _ReadSemanticDataTypeDefinition function."""
    definition_values = {
        u'description': u'semantic data type',
    }

    definitions_registry = registry.DataTypeDefinitionsRegistry()
    definitions_reader = reader.DataTypeDefinitionsReader()

    data_type_definition = definitions_reader._ReadSemanticDataTypeDefinition(
        definitions_registry, definition_values,
        data_types.EnumerationDefinition, u'enum')
    self.assertIsNotNone(data_type_definition)
    self.assertIsInstance(
        data_type_definition, data_types.EnumerationDefinition)

    # Test with attributes.
    definition_values[u'attributes'] = {}

    with self.assertRaises(errors.DefinitionReaderError):
      definitions_reader._ReadSemanticDataTypeDefinition(
          definitions_registry, definition_values,
          data_types.EnumerationDefinition, u'enum')

    definition_values[u'attributes'] = None

  @test_lib.skipUnlessHasTestFile([u'definitions', u'integers.yaml'])
  def testReadSequenceDataTypeDefinition(self):
    """Tests the _ReadSequenceDataTypeDefinition function."""
    definition_values = {
        u'description': u'vector with 4 elements',
        u'element_data_type': u'int32',
        u'number_of_elements': 4,
    }

    definitions_file = self._GetTestFilePath([u'definitions', u'integers.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)
    definitions_reader = reader.DataTypeDefinitionsReader()

    data_type_definition = (
        definitions_reader._ReadSequenceDataTypeDefinition(
            definitions_registry, definition_values, u'vector4'))
    self.assertIsNotNone(data_type_definition)
    self.assertIsInstance(data_type_definition, data_types.SequenceDefinition)

  def testReadStorageDataTypeDefinition(self):
    """Tests the _ReadStorageDataTypeDefinition function."""
    definition_values = {
        u'aliases': [u'LONG', u'LONG32'],
        u'attributes': {
            u'byte_order': u'little-endian',
        },
        u'description': u'signed 32-bit integer type',
    }

    definitions_registry = registry.DataTypeDefinitionsRegistry()
    definitions_reader = reader.DataTypeDefinitionsReader()

    data_type_definition = definitions_reader._ReadStorageDataTypeDefinition(
        definitions_registry, definition_values, data_types.IntegerDefinition,
        u'int32')
    self.assertIsNotNone(data_type_definition)
    self.assertIsInstance(data_type_definition, data_types.IntegerDefinition)
    self.assertEqual(
        data_type_definition.byte_order, definitions.BYTE_ORDER_LITTLE_ENDIAN)

    # Test with incorrect byte-order.
    definition_values[u'attributes'][u'byte_order'] = u'bogus'

    with self.assertRaises(errors.DefinitionReaderError):
      definitions_reader._ReadStorageDataTypeDefinition(
          definitions_registry, definition_values, data_types.IntegerDefinition,
          u'int32')

    definition_values[u'attributes'][u'byte_order'] = u'little-endian'

  @test_lib.skipUnlessHasTestFile([u'definitions', u'integers.yaml'])
  def testReadStreamDataTypeDefinition(self):
    """Tests the _ReadStreamDataTypeDefinition function."""
    definition_values = {
        u'description': u'stream with 4 elements',
        u'element_data_type': u'uint8',
        u'number_of_elements': 4,
    }

    definitions_file = self._GetTestFilePath([u'definitions', u'integers.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)
    definitions_reader = reader.DataTypeDefinitionsReader()

    data_type_definition = (
        definitions_reader._ReadStreamDataTypeDefinition(
            definitions_registry, definition_values, u'array4'))
    self.assertIsNotNone(data_type_definition)
    self.assertIsInstance(data_type_definition, data_types.StreamDefinition)

  @test_lib.skipUnlessHasTestFile([u'definitions', u'characters.yaml'])
  def testReadStringDataTypeDefinition(self):
    """Tests the _ReadStringDataTypeDefinition function."""
    definition_values = {
        u'description': u'string with 4 characters',
        u'encoding': u'ascii',
        u'element_data_type': u'char',
        u'number_of_elements': 4,
    }

    definitions_file = self._GetTestFilePath([
        u'definitions', u'characters.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)
    definitions_reader = reader.DataTypeDefinitionsReader()

    data_type_definition = (
        definitions_reader._ReadStringDataTypeDefinition(
            definitions_registry, definition_values, u'string4'))
    self.assertIsNotNone(data_type_definition)
    self.assertIsInstance(data_type_definition, data_types.StringDefinition)

  @test_lib.skipUnlessHasTestFile([u'definitions', u'integers.yaml'])
  def testReadStructureDataTypeDefinition(self):
    """Tests the _ReadStructureDataTypeDefinition function."""
    definition_values = {
        u'aliases': [u'POINT'],
        u'attributes': {
            u'byte_order': u'big-endian',
        },
        u'description': u'Point in 3 dimensional space.',
        u'members': [
            {u'name': u'x', u'data_type': u'int32'},
            {u'name': u'y', u'data_type': u'int32'},
            {u'name': u'z', u'data_type': u'int32'}],
    }

    definitions_file = self._GetTestFilePath([u'definitions', u'integers.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)
    definitions_reader = reader.DataTypeDefinitionsReader()

    data_type_definition = (
        definitions_reader._ReadStructureDataTypeDefinition(
            definitions_registry, definition_values, u'point3d'))
    self.assertIsNotNone(data_type_definition)
    self.assertIsInstance(
        data_type_definition, data_types.StructureDefinition)
    self.assertEqual(
        data_type_definition.byte_order, definitions.BYTE_ORDER_BIG_ENDIAN)

    # Test with undefined data type.
    definition_values[u'members'][1][u'data_type'] = u'bogus'

    with self.assertRaises(errors.DefinitionReaderError):
      definitions_reader._ReadStructureDataTypeDefinition(
          definitions_registry, definition_values, u'point3d')

    # Test with missing member definitions.
    del definition_values[u'members']

    with self.assertRaises(errors.DefinitionReaderError):
      definitions_reader._ReadStructureDataTypeDefinition(
          definitions_registry, definition_values, u'point3d')

  @test_lib.skipUnlessHasTestFile([u'definitions', u'integers.yaml'])
  def testReadUnionDataTypeDefinition(self):
    """Tests the _ReadUnionDataTypeDefinition function."""
    definition_values = {
        u'members': [
            {u'name': u'long', u'data_type': u'int32'},
            {u'name': u'short', u'data_type': u'int16'}],
    }

    definitions_file = self._GetTestFilePath([u'definitions', u'integers.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)
    definitions_reader = reader.DataTypeDefinitionsReader()

    data_type_definition = (
        definitions_reader._ReadStructureDataTypeDefinition(
            definitions_registry, definition_values, u'union'))
    self.assertIsNotNone(data_type_definition)
    self.assertIsInstance(
        data_type_definition, data_types.StructureDefinition)

    # Test with undefined data type.
    definition_values[u'members'][1][u'data_type'] = u'bogus'

    with self.assertRaises(errors.DefinitionReaderError):
      definitions_reader._ReadStructureDataTypeDefinition(
          definitions_registry, definition_values, u'point3d')

    # Test with missing member definitions.
    del definition_values[u'members']

    with self.assertRaises(errors.DefinitionReaderError):
      definitions_reader._ReadStructureDataTypeDefinition(
          definitions_registry, definition_values, u'point3d')

  def testReadUUIDDataTypeDefinition(self):
    """Tests the _ReadUUIDDataTypeDefinition function."""
    definition_values = {
        u'aliases': [u'guid', u'GUID', u'UUID'],
        u'attributes': {
            u'byte_order': u'little-endian',
        },
        u'description': (
            u'Globally or Universal unique identifier (GUID or UUID) type'),
    }

    definitions_registry = registry.DataTypeDefinitionsRegistry()
    definitions_reader = reader.DataTypeDefinitionsReader()

    data_type_definition = definitions_reader._ReadUUIDDataTypeDefinition(
        definitions_registry, definition_values, u'uuid')
    self.assertIsNotNone(data_type_definition)
    self.assertIsInstance(data_type_definition, data_types.UUIDDefinition)

    # Test with unsupported size.
    definition_values[u'attributes'][u'size'] = 32

    with self.assertRaises(errors.DefinitionReaderError):
      definitions_reader._ReadUUIDDataTypeDefinition(
          definitions_registry, definition_values, u'uuid')



class DataTypeDefinitionsFileReaderTest(test_lib.BaseTestCase):
  """Data type definitions file reader tests."""

  # pylint: disable=protected-access

  def testReadDefinition(self):
    """Tests the _ReadDefinition function."""
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

    data_type_definition = definitions_reader._ReadDefinition(
        definitions_registry, definition_values)
    self.assertIsNotNone(data_type_definition)
    self.assertIsInstance(data_type_definition, data_types.IntegerDefinition)

    with self.assertRaises(errors.DefinitionReaderError):
      definitions_reader._ReadDefinition(definitions_registry, None)

    definition_values[u'type'] = u'bogus'
    with self.assertRaises(errors.DefinitionReaderError):
      definitions_reader._ReadDefinition(
          definitions_registry, definition_values)

  @test_lib.skipUnlessHasTestFile([u'definitions', u'integers.yaml'])
  def testReadFile(self):
    """Tests the ReadFile function."""
    definitions_file = self._GetTestFilePath([u'definitions', u'integers.yaml'])

    definitions_registry = registry.DataTypeDefinitionsRegistry()
    definitions_reader = reader.DataTypeDefinitionsFileReader()

    definitions_reader.ReadFile(definitions_registry, definitions_file)


class YAMLDataTypeDefinitionsFileReaderTest(test_lib.BaseTestCase):
  """YAML data type definitions reader tests."""

  # pylint: disable=protected-access

  @test_lib.skipUnlessHasTestFile([u'boolean.yaml'])
  def testReadFileObjectBoolean(self):
    """Tests the ReadFileObject function of a boolean data type."""
    definitions_registry = registry.DataTypeDefinitionsRegistry()
    definitions_reader = reader.YAMLDataTypeDefinitionsFileReader()

    definitions_file = self._GetTestFilePath([u'boolean.yaml'])
    with open(definitions_file, 'rb') as file_object:
      definitions_reader.ReadFileObject(definitions_registry, file_object)

    self.assertEqual(len(definitions_registry._definitions), 1)

    data_type_definition = definitions_registry.GetDefinitionByName(u'bool')
    self.assertIsInstance(data_type_definition, data_types.BooleanDefinition)
    self.assertEqual(data_type_definition.name, u'bool')
    self.assertEqual(data_type_definition.size, 1)
    self.assertEqual(data_type_definition.units, u'bytes')

    byte_size = data_type_definition.GetByteSize()
    self.assertEqual(byte_size, 1)

  @test_lib.skipUnlessHasTestFile([u'character.yaml'])
  def testReadFileObjectCharacter(self):
    """Tests the ReadFileObject function of a character data type."""
    definitions_registry = registry.DataTypeDefinitionsRegistry()
    definitions_reader = reader.YAMLDataTypeDefinitionsFileReader()

    definitions_file = self._GetTestFilePath([u'character.yaml'])
    with open(definitions_file, 'rb') as file_object:
      definitions_reader.ReadFileObject(definitions_registry, file_object)

    self.assertEqual(len(definitions_registry._definitions), 1)

    data_type_definition = definitions_registry.GetDefinitionByName(u'char')
    self.assertIsInstance(data_type_definition, data_types.CharacterDefinition)
    self.assertEqual(data_type_definition.name, u'char')
    self.assertEqual(data_type_definition.size, 1)
    self.assertEqual(data_type_definition.units, u'bytes')

    byte_size = data_type_definition.GetByteSize()
    self.assertEqual(byte_size, 1)

  @test_lib.skipUnlessHasTestFile([u'constant.yaml'])
  def testReadFileObjectConstant(self):
    """Tests the ReadFileObject function of a constant data type."""
    definitions_registry = registry.DataTypeDefinitionsRegistry()
    definitions_reader = reader.YAMLDataTypeDefinitionsFileReader()

    definitions_file = self._GetTestFilePath([u'constant.yaml'])
    with open(definitions_file, 'rb') as file_object:
      definitions_reader.ReadFileObject(definitions_registry, file_object)

    self.assertEqual(len(definitions_registry._definitions), 1)

    data_type_definition = definitions_registry.GetDefinitionByName(
        u'maximum_number_of_back_traces')
    self.assertIsInstance(data_type_definition, data_types.ConstantDefinition)
    self.assertEqual(
        data_type_definition.name, u'maximum_number_of_back_traces')
    self.assertEqual(data_type_definition.value, 32)

  @test_lib.skipUnlessHasTestFile([u'enumeration.yaml'])
  def testReadFileObjectEnumeration(self):
    """Tests the ReadFileObject function of an enumeration data type."""
    definitions_registry = registry.DataTypeDefinitionsRegistry()
    definitions_reader = reader.YAMLDataTypeDefinitionsFileReader()

    definitions_file = self._GetTestFilePath([u'enumeration.yaml'])
    with open(definitions_file, 'rb') as file_object:
      definitions_reader.ReadFileObject(definitions_registry, file_object)

    self.assertEqual(len(definitions_registry._definitions), 1)

    data_type_definition = definitions_registry.GetDefinitionByName(
        u'object_information_type')
    self.assertIsInstance(
        data_type_definition, data_types.EnumerationDefinition)
    self.assertEqual(data_type_definition.name, u'object_information_type')
    self.assertEqual(len(data_type_definition.values), 6)

    byte_size = data_type_definition.GetByteSize()
    self.assertIsNone(byte_size)

  @test_lib.skipUnlessHasTestFile([u'floating-point.yaml'])
  def testReadFileObjectFloatingPoint(self):
    """Tests the ReadFileObject function of a floating-point data type."""
    definitions_registry = registry.DataTypeDefinitionsRegistry()
    definitions_reader = reader.YAMLDataTypeDefinitionsFileReader()

    definitions_file = self._GetTestFilePath([u'floating-point.yaml'])
    with open(definitions_file, 'rb') as file_object:
      definitions_reader.ReadFileObject(definitions_registry, file_object)

    self.assertEqual(len(definitions_registry._definitions), 1)

    data_type_definition = definitions_registry.GetDefinitionByName(u'float32')
    self.assertIsInstance(
        data_type_definition, data_types.FloatingPointDefinition)
    self.assertEqual(data_type_definition.name, u'float32')
    self.assertEqual(
        data_type_definition.byte_order, definitions.BYTE_ORDER_LITTLE_ENDIAN)
    self.assertEqual(data_type_definition.size, 4)
    self.assertEqual(data_type_definition.units, u'bytes')

    byte_size = data_type_definition.GetByteSize()
    self.assertEqual(byte_size, 4)

  def testReadFileObjectInteger(self):
    """Tests the ReadFileObject function of an integer data type."""
    definitions_registry = registry.DataTypeDefinitionsRegistry()
    definitions_reader = reader.YAMLDataTypeDefinitionsFileReader()

    yaml_data = u'\n'.join([
        u'name: int32le',
        u'type: integer',
        u'attributes:',
        u'  byte_order: little-endian',
        u'  format: signed',
        u'  size: 4',
        u'  units: bytes']).encode(u'ascii')

    with io.BytesIO(initial_bytes=yaml_data) as file_object:
      definitions_reader.ReadFileObject(definitions_registry, file_object)

    data_type_definition = definitions_registry.GetDefinitionByName(u'int32le')
    self.assertIsInstance(data_type_definition, data_types.IntegerDefinition)
    self.assertEqual(data_type_definition.name, u'int32le')
    self.assertEqual(
        data_type_definition.byte_order, definitions.BYTE_ORDER_LITTLE_ENDIAN)
    self.assertEqual(data_type_definition.format, u'signed')
    self.assertEqual(data_type_definition.size, 4)
    self.assertEqual(data_type_definition.units, u'bytes')

    byte_size = data_type_definition.GetByteSize()
    self.assertEqual(byte_size, 4)

    yaml_data = u'\n'.join([
        u'name: int',
        u'type: integer',
        u'attributes:',
        u'  format: signed']).encode(u'ascii')

    with io.BytesIO(initial_bytes=yaml_data) as file_object:
      definitions_reader.ReadFileObject(definitions_registry, file_object)

    data_type_definition = definitions_registry.GetDefinitionByName(u'int')

    byte_size = data_type_definition.GetByteSize()
    self.assertIsNone(byte_size)

    yaml_data = u'\n'.join([
        u'name: int32le',
        u'type: integer',
        u'attributes:',
        u'  format: bogus',
        u'  size: 4',
        u'  units: bytes']).encode(u'ascii')

    with self.assertRaises(errors.FormatError):
      with io.BytesIO(initial_bytes=yaml_data) as file_object:
        definitions_reader.ReadFileObject(definitions_registry, file_object)

    yaml_data = u'\n'.join([
        u'name: int32le',
        u'type: integer',
        u'attributes:',
        u'  format: signed',
        u'  size: bogus',
        u'  units: bytes']).encode(u'ascii')

    with self.assertRaises(errors.FormatError):
      with io.BytesIO(initial_bytes=yaml_data) as file_object:
        definitions_reader.ReadFileObject(definitions_registry, file_object)

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

  @test_lib.skipUnlessHasTestFile([u'sequence.yaml'])
  def testReadFileObjectSequence(self):
    """Tests the ReadFileObject function of a sequence data type."""
    definitions_registry = registry.DataTypeDefinitionsRegistry()
    definitions_reader = reader.YAMLDataTypeDefinitionsFileReader()

    definitions_file = self._GetTestFilePath([u'sequence.yaml'])
    with open(definitions_file, 'rb') as file_object:
      definitions_reader.ReadFileObject(definitions_registry, file_object)

    self.assertEqual(len(definitions_registry._definitions), 3)

    data_type_definition = definitions_registry.GetDefinitionByName(u'vector4')
    self.assertIsInstance(data_type_definition, data_types.SequenceDefinition)
    self.assertEqual(data_type_definition.name, u'vector4')
    self.assertEqual(data_type_definition.description, u'4-dimensional vector')
    self.assertEqual(data_type_definition.aliases, [u'VECTOR'])
    self.assertEqual(data_type_definition.element_data_type, u'int32')
    self.assertIsNotNone(data_type_definition.element_data_type_definition)
    self.assertEqual(data_type_definition.number_of_elements, 4)

    byte_size = data_type_definition.GetByteSize()
    self.assertEqual(byte_size, 16)

  @test_lib.skipUnlessHasTestFile([u'stream.yaml'])
  def testReadFileObjectStream(self):
    """Tests the ReadFileObject function of a stream data type."""
    definitions_registry = registry.DataTypeDefinitionsRegistry()
    definitions_reader = reader.YAMLDataTypeDefinitionsFileReader()

    definitions_file = self._GetTestFilePath([u'stream.yaml'])
    with open(definitions_file, 'rb') as file_object:
      definitions_reader.ReadFileObject(definitions_registry, file_object)

    self.assertEqual(len(definitions_registry._definitions), 2)

    data_type_definition = definitions_registry.GetDefinitionByName(
        u'utf16le_stream')
    self.assertIsInstance(data_type_definition, data_types.StreamDefinition)
    self.assertEqual(data_type_definition.name, u'utf16le_stream')
    self.assertEqual(
        data_type_definition.description, u'UTF-16 little-endian stream')
    self.assertEqual(data_type_definition.aliases, [u'UTF16LE'])
    self.assertEqual(data_type_definition.element_data_type, u'wchar16')
    self.assertIsNotNone(data_type_definition.element_data_type_definition)
    self.assertEqual(data_type_definition.number_of_elements, 8)

    byte_size = data_type_definition.GetByteSize()
    self.assertEqual(byte_size, 16)

  @test_lib.skipUnlessHasTestFile([u'string.yaml'])
  def testReadFileObjectString(self):
    """Tests the ReadFileObject function of a string data type."""
    definitions_registry = registry.DataTypeDefinitionsRegistry()
    definitions_reader = reader.YAMLDataTypeDefinitionsFileReader()

    definitions_file = self._GetTestFilePath([u'string.yaml'])
    with open(definitions_file, 'rb') as file_object:
      definitions_reader.ReadFileObject(definitions_registry, file_object)

    self.assertEqual(len(definitions_registry._definitions), 4)

    data_type_definition = definitions_registry.GetDefinitionByName(
        u'utf8_string')
    self.assertIsInstance(data_type_definition, data_types.StringDefinition)
    self.assertEqual(data_type_definition.name, u'utf8_string')
    self.assertEqual(
        data_type_definition.description, u'UTF-8 string')
    self.assertEqual(data_type_definition.element_data_type, u'char')
    self.assertIsNotNone(data_type_definition.element_data_type_definition)
    self.assertEqual(data_type_definition.elements_terminator, '\x00')
    self.assertEqual(data_type_definition.encoding, u'utf8')

    byte_size = data_type_definition.GetByteSize()
    self.assertIsNone(byte_size)

  @test_lib.skipUnlessHasTestFile([u'structure.yaml'])
  def testReadFileObjectStructure(self):
    """Tests the ReadFileObject function of a structure data type."""
    definitions_registry = registry.DataTypeDefinitionsRegistry()
    definitions_reader = reader.YAMLDataTypeDefinitionsFileReader()

    definitions_file = self._GetTestFilePath([u'structure.yaml'])
    with open(definitions_file, 'rb') as file_object:
      definitions_reader.ReadFileObject(definitions_registry, file_object)

    self.assertEqual(len(definitions_registry._definitions), 5)

    data_type_definition = definitions_registry.GetDefinitionByName(u'point3d')
    self.assertIsInstance(data_type_definition, data_types.StructureDefinition)
    self.assertEqual(data_type_definition.name, u'point3d')
    self.assertEqual(
        data_type_definition.description, u'Point in 3 dimensional space.')
    self.assertEqual(data_type_definition.aliases, [u'POINT'])

    self.assertEqual(len(data_type_definition.members), 3)

    member_definition = data_type_definition.members[0]
    self.assertIsInstance(
        member_definition, data_types.MemberDataTypeDefinition)
    self.assertEqual(member_definition.name, u'x')
    self.assertEqual(member_definition.aliases, [u'XCOORD'])
    self.assertEqual(member_definition.member_data_type, u'int32')
    self.assertIsNotNone(member_definition.member_data_type_definition)

    byte_size = data_type_definition.GetByteSize()
    self.assertEqual(byte_size, 12)

  @test_lib.skipUnlessHasTestFile([u'structure.yaml'])
  def testReadFileObjectStructureWithSequence(self):
    """Tests the ReadFileObject function of a structure with a sequence."""
    definitions_registry = registry.DataTypeDefinitionsRegistry()
    definitions_reader = reader.YAMLDataTypeDefinitionsFileReader()

    definitions_file = self._GetTestFilePath([u'structure.yaml'])
    with open(definitions_file, 'rb') as file_object:
      definitions_reader.ReadFileObject(definitions_registry, file_object)

    self.assertEqual(len(definitions_registry._definitions), 5)

    data_type_definition = definitions_registry.GetDefinitionByName(u'box3d')
    self.assertIsInstance(data_type_definition, data_types.StructureDefinition)
    self.assertEqual(data_type_definition.name, u'box3d')
    self.assertEqual(
        data_type_definition.description, u'Box in 3 dimensional space.')

    self.assertEqual(len(data_type_definition.members), 1)

    member_definition = data_type_definition.members[0]
    self.assertIsInstance(member_definition, data_types.SequenceDefinition)
    self.assertEqual(member_definition.name, u'triangles')
    self.assertEqual(member_definition.element_data_type, u'triangle3d')
    self.assertIsNotNone(member_definition.element_data_type_definition)

    byte_size = data_type_definition.GetByteSize()
    self.assertEqual(byte_size, 432)

  @test_lib.skipUnlessHasTestFile([u'structure.yaml'])
  def testReadFileObjectStructureWithSequenceWithExpression(self):
    """Tests the ReadFileObject function of a structure with a sequence."""
    definitions_registry = registry.DataTypeDefinitionsRegistry()
    definitions_reader = reader.YAMLDataTypeDefinitionsFileReader()

    definitions_file = self._GetTestFilePath([u'structure.yaml'])
    with open(definitions_file, 'rb') as file_object:
      definitions_reader.ReadFileObject(definitions_registry, file_object)

    self.assertEqual(len(definitions_registry._definitions), 5)

    data_type_definition = definitions_registry.GetDefinitionByName(u'sphere3d')
    self.assertIsInstance(data_type_definition, data_types.StructureDefinition)
    self.assertEqual(data_type_definition.name, u'sphere3d')
    self.assertEqual(
        data_type_definition.description, u'Sphere in 3 dimensional space.')

    self.assertEqual(len(data_type_definition.members), 2)

    member_definition = data_type_definition.members[1]
    self.assertIsInstance(member_definition, data_types.SequenceDefinition)
    self.assertEqual(member_definition.name, u'triangles')
    self.assertEqual(member_definition.element_data_type, u'triangle3d')
    self.assertIsNotNone(member_definition.element_data_type_definition)

    byte_size = data_type_definition.GetByteSize()
    self.assertIsNone(byte_size)

  @test_lib.skipUnlessHasTestFile([u'structure_with_union.yaml'])
  def testReadFileObjectStructureWithUnion(self):
    """Tests the ReadFileObject function of a structure with an union."""
    definitions_registry = registry.DataTypeDefinitionsRegistry()
    definitions_reader = reader.YAMLDataTypeDefinitionsFileReader()

    definitions_file = self._GetTestFilePath([u'structure_with_union.yaml'])
    with open(definitions_file, 'rb') as file_object:
      definitions_reader.ReadFileObject(definitions_registry, file_object)

    self.assertEqual(len(definitions_registry._definitions), 3)

    data_type_definition = definitions_registry.GetDefinitionByName(
        u'intfloat32')
    self.assertIsInstance(data_type_definition, data_types.StructureDefinition)
    self.assertEqual(data_type_definition.name, u'intfloat32')

    self.assertEqual(len(data_type_definition.members), 1)

    member_definition = data_type_definition.members[0]
    self.assertIsInstance(member_definition, data_types.UnionDefinition)
    self.assertIsNone(member_definition.name)

    byte_size = data_type_definition.GetByteSize()
    self.assertEqual(byte_size, 4)

  @test_lib.skipUnlessHasTestFile([u'uuid.yaml'])
  def testReadFileObjectUUID(self):
    """Tests the ReadFileObject function of an UUID data type."""
    definitions_registry = registry.DataTypeDefinitionsRegistry()
    definitions_reader = reader.YAMLDataTypeDefinitionsFileReader()

    definitions_file = self._GetTestFilePath([u'uuid.yaml'])
    with open(definitions_file, 'rb') as file_object:
      definitions_reader.ReadFileObject(definitions_registry, file_object)

    self.assertEqual(len(definitions_registry._definitions), 1)

    data_type_definition = definitions_registry.GetDefinitionByName(u'uuid')
    self.assertIsInstance(
        data_type_definition, data_types.UUIDDefinition)
    self.assertEqual(data_type_definition.name, u'uuid')
    self.assertEqual(
        data_type_definition.byte_order, definitions.BYTE_ORDER_LITTLE_ENDIAN)
    self.assertEqual(data_type_definition.size, 16)
    self.assertEqual(data_type_definition.units, u'bytes')

    byte_size = data_type_definition.GetByteSize()
    self.assertEqual(byte_size, 16)


if __name__ == '__main__':
  unittest.main()
