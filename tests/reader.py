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
        'aliases': ['BOOL'],
        'attributes': {
            'size': 4,
        },
        'description': '32-bit boolean type',
    }

    definitions_registry = registry.DataTypeDefinitionsRegistry()
    definitions_reader = reader.DataTypeDefinitionsReader()

    data_type_definition = definitions_reader._ReadBooleanDataTypeDefinition(
        definitions_registry, definition_values, 'bool')
    self.assertIsNotNone(data_type_definition)
    self.assertIsInstance(data_type_definition, data_types.BooleanDefinition)

  def testReadCharacterDataTypeDefinition(self):
    """Tests the _ReadCharacterDataTypeDefinition function."""
    definition_values = {
        'aliases': ['CHAR'],
        'attributes': {
            'size': 1,
        },
        'description': '8-bit character type',
    }

    definitions_registry = registry.DataTypeDefinitionsRegistry()
    definitions_reader = reader.DataTypeDefinitionsReader()

    data_type_definition = definitions_reader._ReadCharacterDataTypeDefinition(
        definitions_registry, definition_values, 'char')
    self.assertIsNotNone(data_type_definition)
    self.assertIsInstance(data_type_definition, data_types.CharacterDefinition)

  def testReadConstantDataTypeDefinition(self):
    """Tests the _ReadConstantDataTypeDefinition function."""
    definition_values = {
        'aliases': ['AVRF_MAX_TRACES'],
        'description': (
            'Application verifier resource enumeration maximum number of '
            'back traces'),
        'value': 32,
    }

    definitions_registry = registry.DataTypeDefinitionsRegistry()
    definitions_reader = reader.DataTypeDefinitionsReader()

    data_type_definition = (
        definitions_reader._ReadConstantDataTypeDefinition(
            definitions_registry, definition_values, 'const'))
    self.assertIsNotNone(data_type_definition)
    self.assertIsInstance(data_type_definition, data_types.ConstantDefinition)

    # Test with missing value definition.
    del definition_values['value']

    with self.assertRaises(errors.DefinitionReaderError):
      definitions_reader._ReadConstantDataTypeDefinition(
          definitions_registry, definition_values, 'const')

  def testReadDataTypeDefinition(self):
    """Tests the _ReadDataTypeDefinition function."""
    definition_values = {
        'aliases': ['LONG', 'LONG32'],
        'description': 'signed 32-bit integer type',
    }

    definitions_registry = registry.DataTypeDefinitionsRegistry()
    definitions_reader = reader.DataTypeDefinitionsReader()

    data_type_definition = definitions_reader._ReadDataTypeDefinition(
        definitions_registry, definition_values, data_types.IntegerDefinition,
        'int32', definitions_reader._SUPPORTED_DEFINITION_VALUES_DATA_TYPE)
    self.assertIsNotNone(data_type_definition)
    self.assertIsInstance(data_type_definition, data_types.IntegerDefinition)

  def testReadDataTypeDefinitionWithMembers(self):
    """Tests the _ReadDataTypeDefinitionWithMembers function."""
    definition_values = {
        'aliases': ['POINT'],
        'attributes': {
            'byte_order': 'big-endian',
        },
        'description': 'Point in 3 dimensional space.',
        'members': [
            {'name': 'x', 'data_type': 'int32'},
            {'name': 'y', 'data_type': 'int32'},
            {'name': 'z', 'data_type': 'int32'}],
    }

    definitions_file = self._GetTestFilePath(['definitions', 'integers.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)
    definitions_reader = reader.DataTypeDefinitionsReader()

    definition_object = definitions_reader._ReadDataTypeDefinitionWithMembers(
        definitions_registry, definition_values, data_types.StructureDefinition,
        'point3d')
    self.assertIsNotNone(definition_object)

    # Test with incorrect byte order.
    definition_values['attributes']['byte_order'] = 'bogus'

    with self.assertRaises(errors.DefinitionReaderError):
      definitions_reader._ReadDataTypeDefinitionWithMembers(
          definitions_registry, definition_values,
          data_types.StructureDefinition, 'point3d')

    definition_values['attributes']['byte_order'] = 'big-endian'

  def testReadElementSequenceDataTypeDefinition(self):
    """Tests the _ReadElementSequenceDataTypeDefinition function."""
    definition_values = {
        'description': 'vector with 4 elements',
        'element_data_type': 'int32',
        'number_of_elements': 4,
    }

    definitions_file = self._GetTestFilePath(['definitions', 'integers.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)
    definitions_reader = reader.DataTypeDefinitionsReader()

    data_type_definition = (
        definitions_reader._ReadElementSequenceDataTypeDefinition(
            definitions_registry, definition_values,
            data_types.SequenceDefinition, 'vector4',
            definitions_reader._SUPPORTED_DEFINITION_VALUES_ELEMENTS_DATA_TYPE))
    self.assertIsNotNone(data_type_definition)
    self.assertIsInstance(data_type_definition, data_types.SequenceDefinition)

    # Test with attributes.
    definition_values['attributes'] = {}

    with self.assertRaises(errors.DefinitionReaderError):
      definitions_reader._ReadElementSequenceDataTypeDefinition(
          definitions_registry, definition_values,
          data_types.SequenceDefinition, 'vector4',
          definitions_reader._SUPPORTED_DEFINITION_VALUES_ELEMENTS_DATA_TYPE)

    definition_values['attributes'] = None

    # Test with undefined element data type.
    definition_values['element_data_type'] = 'bogus'

    with self.assertRaises(errors.DefinitionReaderError):
      definitions_reader._ReadElementSequenceDataTypeDefinition(
          definitions_registry, definition_values,
          data_types.SequenceDefinition, 'vector4',
          definitions_reader._SUPPORTED_DEFINITION_VALUES_ELEMENTS_DATA_TYPE)

    definition_values['element_data_type'] = 'int32'

    # Test with missing element data type definition.
    del definition_values['element_data_type']

    with self.assertRaises(errors.DefinitionReaderError):
      definitions_reader._ReadElementSequenceDataTypeDefinition(
          definitions_registry, definition_values,
          data_types.SequenceDefinition, 'vector4',
          definitions_reader._SUPPORTED_DEFINITION_VALUES_ELEMENTS_DATA_TYPE)

    definition_values['element_data_type'] = 'int32'

    # Test with missing number of elements definition.
    del definition_values['number_of_elements']

    with self.assertRaises(errors.DefinitionReaderError):
      definitions_reader._ReadElementSequenceDataTypeDefinition(
          definitions_registry, definition_values,
          data_types.SequenceDefinition, 'vector4',
          definitions_reader._SUPPORTED_DEFINITION_VALUES_ELEMENTS_DATA_TYPE)

    definition_values['number_of_elements'] = 4

    # Test with elements data size and number of elements definition set at
    # at the same time.
    definition_values['elements_data_size'] = 32

    with self.assertRaises(errors.DefinitionReaderError):
      definitions_reader._ReadElementSequenceDataTypeDefinition(
          definitions_registry, definition_values,
          data_types.SequenceDefinition, 'vector4',
          definitions_reader._SUPPORTED_DEFINITION_VALUES_ELEMENTS_DATA_TYPE)

    del definition_values['elements_data_size']

    # Test with unsupported attributes definition.
    definition_values['attributes'] = {'byte_order': 'little-endian'}

    with self.assertRaises(errors.DefinitionReaderError):
      definitions_reader._ReadElementSequenceDataTypeDefinition(
          definitions_registry, definition_values,
          data_types.SequenceDefinition, 'vector4',
          definitions_reader._SUPPORTED_DEFINITION_VALUES_ELEMENTS_DATA_TYPE)

    del definition_values['attributes']

    # Test with elements terminator.
    definition_values = {
        'description': 'vector with terminator',
        'element_data_type': 'int32',
        'elements_terminator': b'\xff\xff\xff\xff',
    }

    data_type_definition = (
        definitions_reader._ReadElementSequenceDataTypeDefinition(
            definitions_registry, definition_values,
            data_types.SequenceDefinition, 'vector4',
            definitions_reader._SUPPORTED_DEFINITION_VALUES_ELEMENTS_DATA_TYPE))
    self.assertIsNotNone(data_type_definition)
    self.assertIsInstance(data_type_definition, data_types.SequenceDefinition)

    # Test with (Unicode) string elements terminator.
    definition_values['elements_terminator'] = '\0'

    data_type_definition = (
        definitions_reader._ReadElementSequenceDataTypeDefinition(
            definitions_registry, definition_values,
            data_types.SequenceDefinition, 'vector4',
            definitions_reader._SUPPORTED_DEFINITION_VALUES_ELEMENTS_DATA_TYPE))
    self.assertIsNotNone(data_type_definition)
    self.assertIsInstance(data_type_definition, data_types.SequenceDefinition)

  def testReadEnumerationDataTypeDefinition(self):
    """Tests the _ReadEnumerationDataTypeDefinition function."""
    definition_values = {
        'description': 'Minidump object information type',
        'values': [
            {'description': 'No object-specific information available',
             'name': 'MiniHandleObjectInformationNone',
             'number': 0},
            {'description': 'Thread object information',
             'name': 'MiniThreadInformation1',
             'number': 1},
        ],
    }

    definitions_registry = registry.DataTypeDefinitionsRegistry()
    definitions_reader = reader.DataTypeDefinitionsReader()

    data_type_definition = (
        definitions_reader._ReadEnumerationDataTypeDefinition(
            definitions_registry, definition_values, 'enum'))
    self.assertIsNotNone(data_type_definition)
    self.assertIsInstance(
        data_type_definition, data_types.EnumerationDefinition)

    # Test with missing name in first enumeration value definition.
    del definition_values['values'][0]['name']

    with self.assertRaises(errors.DefinitionReaderError):
      definitions_reader._ReadEnumerationDataTypeDefinition(
          definitions_registry, definition_values, 'enum')

    definition_values['values'][0]['name'] = 'MiniHandleObjectInformationNone'

    # Test with missing name in successive enumeration value definition.
    del definition_values['values'][-1]['name']

    with self.assertRaises(errors.DefinitionReaderError):
      definitions_reader._ReadEnumerationDataTypeDefinition(
          definitions_registry, definition_values, 'enum')

    definition_values['values'][-1]['name'] = 'MiniThreadInformation1'

    # Test with missing value in enumeration number definition.
    del definition_values['values'][-1]['number']

    with self.assertRaises(errors.DefinitionReaderError):
      definitions_reader._ReadEnumerationDataTypeDefinition(
          definitions_registry, definition_values, 'enum')

    definition_values['values'][-1]['number'] = 1

    # Test with duplicate enumeration number definition.
    definition_values['values'].append({
        'description': 'Thread object information',
        'name': 'MiniThreadInformation1',
        'number': 1})

    with self.assertRaises(errors.DefinitionReaderError):
      definitions_reader._ReadEnumerationDataTypeDefinition(
          definitions_registry, definition_values, 'enum')

    del definition_values['values'][-1]

    # Test with missing enumeration values definitions.
    del definition_values['values']

    with self.assertRaises(errors.DefinitionReaderError):
      definitions_reader._ReadEnumerationDataTypeDefinition(
          definitions_registry, definition_values, 'enum')

  def testReadFixedSizeDataTypeDefinition(self):
    """Tests the _ReadFixedSizeDataTypeDefinition function."""
    definition_values = {
        'aliases': ['LONG', 'LONG32'],
        'attributes': {
            'byte_order': 'little-endian',
            'size': 4,
        },
        'description': 'signed 32-bit integer type',
    }

    definitions_registry = registry.DataTypeDefinitionsRegistry()
    definitions_reader = reader.DataTypeDefinitionsReader()

    data_type_definition = definitions_reader._ReadFixedSizeDataTypeDefinition(
        definitions_registry, definition_values, data_types.IntegerDefinition,
        'int32', definitions_reader._SUPPORTED_ATTRIBUTES_INTEGER)
    self.assertIsNotNone(data_type_definition)
    self.assertIsInstance(data_type_definition, data_types.IntegerDefinition)
    self.assertEqual(data_type_definition.size, 4)

    # Test with incorrect size.
    definition_values['attributes']['size'] = 'bogus'

    with self.assertRaises(errors.DefinitionReaderError):
      definitions_reader._ReadFixedSizeDataTypeDefinition(
          definitions_registry, definition_values, data_types.IntegerDefinition,
          'int32', definitions_reader._SUPPORTED_ATTRIBUTES_INTEGER)

    definition_values['attributes']['size'] = 4

  def testReadFloatingPointDataTypeDefinition(self):
    """Tests the _ReadFloatingPointDataTypeDefinition function."""
    definition_values = {
        'aliases': ['float', 'FLOAT'],
        'attributes': {
            'size': 4,
        },
        'description': '32-bit floating-point type',
    }

    definitions_registry = registry.DataTypeDefinitionsRegistry()
    definitions_reader = reader.DataTypeDefinitionsReader()

    data_type_definition = (
        definitions_reader._ReadFloatingPointDataTypeDefinition(
            definitions_registry, definition_values, 'float32'))
    self.assertIsNotNone(data_type_definition)
    self.assertIsInstance(
        data_type_definition, data_types.FloatingPointDefinition)

  def testReadFormatDataTypeDefinition(self):
    """Tests the _ReadFormatDataTypeDefinition function."""
    definition_values = {
        'description': 'Windows Shortcut (LNK) file format',
        'type': 'format',
        'layout': [
            'file_header',
        ],
    }

    definitions_registry = registry.DataTypeDefinitionsRegistry()
    definitions_reader = reader.DataTypeDefinitionsReader()

    data_type_definition = definitions_reader._ReadFormatDataTypeDefinition(
        definitions_registry, definition_values, 'lnk')
    self.assertIsNotNone(data_type_definition)
    self.assertIsInstance(data_type_definition, data_types.FormatDefinition)

  def testReadIntegerDataTypeDefinition(self):
    """Tests the _ReadIntegerDataTypeDefinition function."""
    definition_values = {
        'aliases': ['LONG', 'LONG32'],
        'attributes': {
            'format': 'signed',
            'size': 4,
        },
        'description': 'signed 32-bit integer type',
    }

    definitions_registry = registry.DataTypeDefinitionsRegistry()
    definitions_reader = reader.DataTypeDefinitionsReader()

    data_type_definition = definitions_reader._ReadIntegerDataTypeDefinition(
        definitions_registry, definition_values, 'int32')
    self.assertIsNotNone(data_type_definition)
    self.assertIsInstance(data_type_definition, data_types.IntegerDefinition)

    # Test with unsupported format attribute.
    definition_values['attributes']['format'] = 'bogus'

    with self.assertRaises(errors.DefinitionReaderError):
      definitions_reader._ReadIntegerDataTypeDefinition(
          definitions_registry, definition_values, 'int32')

    definition_values['attributes']['format'] = 'signed'

    # Test with unsupported size.
    definition_values['attributes']['size'] = 3

    with self.assertRaises(errors.DefinitionReaderError):
      definitions_reader._ReadIntegerDataTypeDefinition(
          definitions_registry, definition_values, 'int32')

    definition_values['attributes']['size'] = 4

  def testReadLayoutDataTypeDefinition(self):
    """Tests the _ReadLayoutDataTypeDefinition function."""
    definition_values = {
        'description': 'layout data type',
    }

    definitions_registry = registry.DataTypeDefinitionsRegistry()
    definitions_reader = reader.DataTypeDefinitionsReader()

    data_type_definition = definitions_reader._ReadLayoutDataTypeDefinition(
        definitions_registry, definition_values,
        data_types.FormatDefinition, 'format',
        definitions_reader._SUPPORTED_DEFINITION_VALUES_DATA_TYPE)
    self.assertIsNotNone(data_type_definition)
    self.assertIsInstance(data_type_definition, data_types.FormatDefinition)

  def testReadMemberDataTypeDefinitionMember(self):
    """Tests the _ReadMemberDataTypeDefinitionMember function."""
    definition_values = {'name': 'x', 'data_type': 'int32'}

    definition_object = data_types.StructureDefinition('point3d')

    definitions_file = self._GetTestFilePath(['definitions', 'integers.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)
    definitions_reader = reader.DataTypeDefinitionsReader()

    definitions_reader._ReadMemberDataTypeDefinitionMember(
        definitions_registry, definition_values, 'point3d')

    # TODO: implement.
    _ = definition_object

    # Test without definitions values.
    definition_values = {}

    with self.assertRaises(errors.DefinitionReaderError):
      definitions_reader._ReadMemberDataTypeDefinitionMember(
          definitions_registry, definition_values, 'point3d')

    # Test definitions values without name.
    definition_values = {'bogus': 'BOGUS'}

    with self.assertRaises(errors.DefinitionReaderError):
      definitions_reader._ReadMemberDataTypeDefinitionMember(
          definitions_registry, definition_values, 'point3d')

    # Test definitions values without data type and type.
    definition_values = {'name': 'x'}

    with self.assertRaises(errors.DefinitionReaderError):
      definitions_reader._ReadMemberDataTypeDefinitionMember(
          definitions_registry, definition_values, 'point3d')

    # Test definitions values with both data type and type.
    definition_values = {'name': 'x', 'data_type': 'int32', 'type': 'bogus'}

    with self.assertRaises(errors.DefinitionReaderError):
      definitions_reader._ReadMemberDataTypeDefinitionMember(
          definitions_registry, definition_values, 'point3d')

    # Test definitions values with unresolvable type.
    definition_values = {'name': 'x', 'type': 'bogus'}

    with self.assertRaises(errors.DefinitionReaderError):
      definitions_reader._ReadMemberDataTypeDefinitionMember(
          definitions_registry, definition_values, 'point3d')

  def testReadSemanticDataTypeDefinition(self):
    """Tests the _ReadSemanticDataTypeDefinition function."""
    definition_values = {
        'description': 'semantic data type',
    }

    definitions_registry = registry.DataTypeDefinitionsRegistry()
    definitions_reader = reader.DataTypeDefinitionsReader()

    data_type_definition = definitions_reader._ReadSemanticDataTypeDefinition(
        definitions_registry, definition_values,
        data_types.EnumerationDefinition, 'enum',
        definitions_reader._SUPPORTED_DEFINITION_VALUES_ENUMERATION)
    self.assertIsNotNone(data_type_definition)
    self.assertIsInstance(
        data_type_definition, data_types.EnumerationDefinition)

    # Test with attributes.
    definition_values['attributes'] = {}

    with self.assertRaises(errors.DefinitionReaderError):
      definitions_reader._ReadSemanticDataTypeDefinition(
          definitions_registry, definition_values,
          data_types.EnumerationDefinition, 'enum',
          definitions_reader._SUPPORTED_DEFINITION_VALUES_ENUMERATION)

    definition_values['attributes'] = None

  def testReadSequenceDataTypeDefinition(self):
    """Tests the _ReadSequenceDataTypeDefinition function."""
    definition_values = {
        'description': 'vector with 4 elements',
        'element_data_type': 'int32',
        'number_of_elements': 4,
    }

    definitions_file = self._GetTestFilePath(['definitions', 'integers.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)
    definitions_reader = reader.DataTypeDefinitionsReader()

    data_type_definition = (
        definitions_reader._ReadSequenceDataTypeDefinition(
            definitions_registry, definition_values, 'vector4'))
    self.assertIsNotNone(data_type_definition)
    self.assertIsInstance(data_type_definition, data_types.SequenceDefinition)

  def testReadStorageDataTypeDefinition(self):
    """Tests the _ReadStorageDataTypeDefinition function."""
    definition_values = {
        'aliases': ['LONG', 'LONG32'],
        'attributes': {
            'byte_order': 'little-endian',
        },
        'description': 'signed 32-bit integer type',
    }

    definitions_registry = registry.DataTypeDefinitionsRegistry()
    definitions_reader = reader.DataTypeDefinitionsReader()

    data_type_definition = definitions_reader._ReadStorageDataTypeDefinition(
        definitions_registry, definition_values, data_types.IntegerDefinition,
        'int32', definitions_reader._SUPPORTED_ATTRIBUTES_INTEGER)
    self.assertIsNotNone(data_type_definition)
    self.assertIsInstance(data_type_definition, data_types.IntegerDefinition)
    self.assertEqual(
        data_type_definition.byte_order, definitions.BYTE_ORDER_LITTLE_ENDIAN)

    # Test with incorrect byte-order.
    definition_values['attributes']['byte_order'] = 'bogus'

    with self.assertRaises(errors.DefinitionReaderError):
      definitions_reader._ReadStorageDataTypeDefinition(
          definitions_registry, definition_values, data_types.IntegerDefinition,
          'int32', definitions_reader._SUPPORTED_ATTRIBUTES_INTEGER)

    definition_values['attributes']['byte_order'] = 'little-endian'

  def testReadStreamDataTypeDefinition(self):
    """Tests the _ReadStreamDataTypeDefinition function."""
    definition_values = {
        'description': 'stream with 4 elements',
        'element_data_type': 'uint8',
        'number_of_elements': 4,
    }

    definitions_file = self._GetTestFilePath(['definitions', 'integers.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)
    definitions_reader = reader.DataTypeDefinitionsReader()

    data_type_definition = (
        definitions_reader._ReadStreamDataTypeDefinition(
            definitions_registry, definition_values, 'array4'))
    self.assertIsNotNone(data_type_definition)
    self.assertIsInstance(data_type_definition, data_types.StreamDefinition)

  def testReadStringDataTypeDefinition(self):
    """Tests the _ReadStringDataTypeDefinition function."""
    definition_values = {
        'description': 'string with 4 characters',
        'encoding': 'ascii',
        'element_data_type': 'char',
        'number_of_elements': 4,
    }

    definitions_file = self._GetTestFilePath([
        'definitions', 'characters.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)
    definitions_reader = reader.DataTypeDefinitionsReader()

    data_type_definition = (
        definitions_reader._ReadStringDataTypeDefinition(
            definitions_registry, definition_values, 'string4'))
    self.assertIsNotNone(data_type_definition)
    self.assertIsInstance(data_type_definition, data_types.StringDefinition)

    # Test definitions values without encoding.
    del definition_values['encoding']

    with self.assertRaises(errors.DefinitionReaderError):
      definitions_reader._ReadStringDataTypeDefinition(
          definitions_registry, definition_values, 'string4')

    definition_values['encoding'] = 'ascii'

  def testReadStructureDataTypeDefinition(self):
    """Tests the _ReadStructureDataTypeDefinition function."""
    definition_values = {
        'aliases': ['POINT'],
        'attributes': {
            'byte_order': 'big-endian',
        },
        'description': 'Point in 3 dimensional space.',
        'members': [
            {'name': 'x', 'data_type': 'int32'},
            {'name': 'y', 'data_type': 'int32'},
            {'name': 'z', 'data_type': 'int32'}],
    }

    definitions_file = self._GetTestFilePath(['definitions', 'integers.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)
    definitions_reader = reader.DataTypeDefinitionsReader()

    data_type_definition = (
        definitions_reader._ReadStructureDataTypeDefinition(
            definitions_registry, definition_values, 'point3d'))
    self.assertIsNotNone(data_type_definition)
    self.assertIsInstance(
        data_type_definition, data_types.StructureDefinition)
    self.assertEqual(
        data_type_definition.byte_order, definitions.BYTE_ORDER_BIG_ENDIAN)

    # Test with undefined data type.
    definition_values['members'][1]['data_type'] = 'bogus'

    with self.assertRaises(errors.DefinitionReaderError):
      definitions_reader._ReadStructureDataTypeDefinition(
          definitions_registry, definition_values, 'point3d')

    # Test with missing member definitions.
    del definition_values['members']

    with self.assertRaises(errors.DefinitionReaderError):
      definitions_reader._ReadStructureDataTypeDefinition(
          definitions_registry, definition_values, 'point3d')

  # TODO: add tests for _ReadStructureFamilyDataTypeDefinition
  # TODO: add tests for _ReadStructureGroupDataTypeDefinition

  def testReadUnionDataTypeDefinition(self):
    """Tests the _ReadUnionDataTypeDefinition function."""
    definition_values = {
        'members': [
            {'name': 'long', 'data_type': 'int32'},
            {'name': 'short', 'data_type': 'int16'}],
    }

    definitions_file = self._GetTestFilePath(['definitions', 'integers.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)
    definitions_reader = reader.DataTypeDefinitionsReader()

    data_type_definition = (
        definitions_reader._ReadStructureDataTypeDefinition(
            definitions_registry, definition_values, 'union'))
    self.assertIsNotNone(data_type_definition)
    self.assertIsInstance(
        data_type_definition, data_types.StructureDefinition)

    # Test with undefined data type.
    definition_values['members'][1]['data_type'] = 'bogus'

    with self.assertRaises(errors.DefinitionReaderError):
      definitions_reader._ReadStructureDataTypeDefinition(
          definitions_registry, definition_values, 'point3d')

    # Test with missing member definitions.
    del definition_values['members']

    with self.assertRaises(errors.DefinitionReaderError):
      definitions_reader._ReadStructureDataTypeDefinition(
          definitions_registry, definition_values, 'point3d')

  def testReadUUIDDataTypeDefinition(self):
    """Tests the _ReadUUIDDataTypeDefinition function."""
    definition_values = {
        'aliases': ['guid', 'GUID', 'UUID'],
        'attributes': {
            'byte_order': 'little-endian',
        },
        'description': (
            'Globally or Universal unique identifier (GUID or UUID) type'),
    }

    definitions_registry = registry.DataTypeDefinitionsRegistry()
    definitions_reader = reader.DataTypeDefinitionsReader()

    data_type_definition = definitions_reader._ReadUUIDDataTypeDefinition(
        definitions_registry, definition_values, 'uuid')
    self.assertIsNotNone(data_type_definition)
    self.assertIsInstance(data_type_definition, data_types.UUIDDefinition)

    # Test with unsupported size.
    definition_values['attributes']['size'] = 32

    with self.assertRaises(errors.DefinitionReaderError):
      definitions_reader._ReadUUIDDataTypeDefinition(
          definitions_registry, definition_values, 'uuid')



class DataTypeDefinitionsFileReaderTest(test_lib.BaseTestCase):
  """Data type definitions file reader tests."""

  # pylint: disable=protected-access

  def testReadDefinition(self):
    """Tests the _ReadDefinition function."""
    definition_values = {
        'aliases': ['LONG', 'LONG32'],
        'attributes': {
            'format': 'signed',
            'size': 4,
        },
        'description': 'signed 32-bit integer type',
        'name': 'int32',
        'type': 'integer',
    }

    definitions_registry = registry.DataTypeDefinitionsRegistry()
    definitions_reader = reader.DataTypeDefinitionsFileReader()

    data_type_definition = definitions_reader._ReadDefinition(
        definitions_registry, definition_values)
    self.assertIsNotNone(data_type_definition)
    self.assertIsInstance(data_type_definition, data_types.IntegerDefinition)

    with self.assertRaises(errors.DefinitionReaderError):
      definitions_reader._ReadDefinition(definitions_registry, None)

    definition_values['type'] = 'bogus'
    with self.assertRaises(errors.DefinitionReaderError):
      definitions_reader._ReadDefinition(
          definitions_registry, definition_values)

  def testReadFile(self):
    """Tests the ReadFile function."""
    definitions_file = self._GetTestFilePath(['definitions', 'integers.yaml'])
    self._SkipIfPathNotExists(definitions_file)

    definitions_registry = registry.DataTypeDefinitionsRegistry()
    definitions_reader = reader.DataTypeDefinitionsFileReader()

    definitions_reader.ReadFile(definitions_registry, definitions_file)


class YAMLDataTypeDefinitionsFileReaderTest(test_lib.BaseTestCase):
  """YAML data type definitions reader tests."""

  # pylint: disable=protected-access

  # TODO: add tests for _GetFormatErrorLocation

  def testReadFileObjectBoolean(self):
    """Tests the ReadFileObject function of a boolean data type."""
    definitions_registry = registry.DataTypeDefinitionsRegistry()
    definitions_reader = reader.YAMLDataTypeDefinitionsFileReader()

    definitions_file = self._GetTestFilePath(['boolean.yaml'])
    self._SkipIfPathNotExists(definitions_file)

    with open(definitions_file, 'rb') as file_object:
      definitions_reader.ReadFileObject(definitions_registry, file_object)

    self.assertEqual(len(definitions_registry._definitions), 1)

    data_type_definition = definitions_registry.GetDefinitionByName('bool')
    self.assertIsInstance(data_type_definition, data_types.BooleanDefinition)
    self.assertEqual(data_type_definition.name, 'bool')
    self.assertEqual(data_type_definition.size, 1)
    self.assertEqual(data_type_definition.units, 'bytes')

    byte_size = data_type_definition.GetByteSize()
    self.assertEqual(byte_size, 1)

  def testReadFileObjectCharacter(self):
    """Tests the ReadFileObject function of a character data type."""
    definitions_registry = registry.DataTypeDefinitionsRegistry()
    definitions_reader = reader.YAMLDataTypeDefinitionsFileReader()

    definitions_file = self._GetTestFilePath(['character.yaml'])
    self._SkipIfPathNotExists(definitions_file)

    with open(definitions_file, 'rb') as file_object:
      definitions_reader.ReadFileObject(definitions_registry, file_object)

    self.assertEqual(len(definitions_registry._definitions), 1)

    data_type_definition = definitions_registry.GetDefinitionByName('char')
    self.assertIsInstance(data_type_definition, data_types.CharacterDefinition)
    self.assertEqual(data_type_definition.name, 'char')
    self.assertEqual(data_type_definition.size, 1)
    self.assertEqual(data_type_definition.units, 'bytes')

    byte_size = data_type_definition.GetByteSize()
    self.assertEqual(byte_size, 1)

  def testReadFileObjectConstant(self):
    """Tests the ReadFileObject function of a constant data type."""
    definitions_registry = registry.DataTypeDefinitionsRegistry()
    definitions_reader = reader.YAMLDataTypeDefinitionsFileReader()

    definitions_file = self._GetTestFilePath(['constant.yaml'])
    self._SkipIfPathNotExists(definitions_file)

    with open(definitions_file, 'rb') as file_object:
      definitions_reader.ReadFileObject(definitions_registry, file_object)

    self.assertEqual(len(definitions_registry._definitions), 1)

    data_type_definition = definitions_registry.GetDefinitionByName(
        'maximum_number_of_back_traces')
    self.assertIsInstance(data_type_definition, data_types.ConstantDefinition)
    self.assertEqual(
        data_type_definition.name, 'maximum_number_of_back_traces')
    self.assertEqual(data_type_definition.value, 32)

  def testReadFileObjectEnumeration(self):
    """Tests the ReadFileObject function of an enumeration data type."""
    definitions_registry = registry.DataTypeDefinitionsRegistry()
    definitions_reader = reader.YAMLDataTypeDefinitionsFileReader()

    definitions_file = self._GetTestFilePath(['enumeration.yaml'])
    self._SkipIfPathNotExists(definitions_file)

    with open(definitions_file, 'rb') as file_object:
      definitions_reader.ReadFileObject(definitions_registry, file_object)

    self.assertEqual(len(definitions_registry._definitions), 1)

    data_type_definition = definitions_registry.GetDefinitionByName(
        'object_information_type')
    self.assertIsInstance(
        data_type_definition, data_types.EnumerationDefinition)
    self.assertEqual(data_type_definition.name, 'object_information_type')
    self.assertEqual(len(data_type_definition.values), 6)

    byte_size = data_type_definition.GetByteSize()
    self.assertIsNone(byte_size)

  def testReadFileObjectFloatingPoint(self):
    """Tests the ReadFileObject function of a floating-point data type."""
    definitions_registry = registry.DataTypeDefinitionsRegistry()
    definitions_reader = reader.YAMLDataTypeDefinitionsFileReader()

    definitions_file = self._GetTestFilePath(['floating-point.yaml'])
    self._SkipIfPathNotExists(definitions_file)

    with open(definitions_file, 'rb') as file_object:
      definitions_reader.ReadFileObject(definitions_registry, file_object)

    self.assertEqual(len(definitions_registry._definitions), 1)

    data_type_definition = definitions_registry.GetDefinitionByName('float32')
    self.assertIsInstance(
        data_type_definition, data_types.FloatingPointDefinition)
    self.assertEqual(data_type_definition.name, 'float32')
    self.assertEqual(
        data_type_definition.byte_order, definitions.BYTE_ORDER_LITTLE_ENDIAN)
    self.assertEqual(data_type_definition.size, 4)
    self.assertEqual(data_type_definition.units, 'bytes')

    byte_size = data_type_definition.GetByteSize()
    self.assertEqual(byte_size, 4)

  def testReadFileObjectInteger(self):
    """Tests the ReadFileObject function of an integer data type."""
    definitions_registry = registry.DataTypeDefinitionsRegistry()
    definitions_reader = reader.YAMLDataTypeDefinitionsFileReader()

    yaml_data = '\n'.join([
        'name: int32le',
        'type: integer',
        'attributes:',
        '  byte_order: little-endian',
        '  format: signed',
        '  size: 4',
        '  units: bytes']).encode('ascii')

    with io.BytesIO(initial_bytes=yaml_data) as file_object:
      definitions_reader.ReadFileObject(definitions_registry, file_object)

    data_type_definition = definitions_registry.GetDefinitionByName('int32le')
    self.assertIsInstance(data_type_definition, data_types.IntegerDefinition)
    self.assertEqual(data_type_definition.name, 'int32le')
    self.assertEqual(
        data_type_definition.byte_order, definitions.BYTE_ORDER_LITTLE_ENDIAN)
    self.assertEqual(data_type_definition.format, 'signed')
    self.assertEqual(data_type_definition.size, 4)
    self.assertEqual(data_type_definition.units, 'bytes')

    byte_size = data_type_definition.GetByteSize()
    self.assertEqual(byte_size, 4)

    yaml_data = '\n'.join([
        'name: int',
        'type: integer',
        'attributes:',
        '  format: signed']).encode('ascii')

    with io.BytesIO(initial_bytes=yaml_data) as file_object:
      definitions_reader.ReadFileObject(definitions_registry, file_object)

    data_type_definition = definitions_registry.GetDefinitionByName('int')

    byte_size = data_type_definition.GetByteSize()
    self.assertIsNone(byte_size)

    yaml_data = '\n'.join([
        'name: int32le',
        'type: integer',
        'attributes:',
        '  format: bogus',
        '  size: 4',
        '  units: bytes']).encode('ascii')

    with self.assertRaises(errors.FormatError):
      with io.BytesIO(initial_bytes=yaml_data) as file_object:
        definitions_reader.ReadFileObject(definitions_registry, file_object)

    yaml_data = '\n'.join([
        'name: int32le',
        'type: integer',
        'attributes:',
        '  format: signed',
        '  size: bogus',
        '  units: bytes']).encode('ascii')

    with self.assertRaises(errors.FormatError):
      with io.BytesIO(initial_bytes=yaml_data) as file_object:
        definitions_reader.ReadFileObject(definitions_registry, file_object)

  def testReadFileObjectMissingName(self):
    """Tests the ReadFileObject function with a missing name."""
    definitions_registry = registry.DataTypeDefinitionsRegistry()
    definitions_reader = reader.YAMLDataTypeDefinitionsFileReader()

    yaml_data = '\n'.join([
        'type: integer',
        'attributes:',
        '  format: signed',
        '  size: 1',
        '  units: bytes']).encode('ascii')

    file_object = io.BytesIO(initial_bytes=yaml_data)

    with self.assertRaises(errors.FormatError):
      definitions_reader.ReadFileObject(definitions_registry, file_object)

  def testReadFileObjectMissingType(self):
    """Tests the ReadFileObject function with a missing type."""
    definitions_registry = registry.DataTypeDefinitionsRegistry()
    definitions_reader = reader.YAMLDataTypeDefinitionsFileReader()

    yaml_data = '\n'.join([
        'name: int8',
        'attributes:',
        '  format: signed',
        '  size: 1',
        '  units: bytes']).encode('ascii')

    file_object = io.BytesIO(initial_bytes=yaml_data)

    with self.assertRaises(errors.FormatError):
      definitions_reader.ReadFileObject(definitions_registry, file_object)

    yaml_data = '\n'.join([
        'name: int8',
        'type: integer',
        'attributes:',
        '  format: signed',
        '  size: 1',
        '  units: bytes',
        '---',
        'name: int16',
        'attributes:',
        '  format: signed',
        '  size: 2',
        '  units: bytes']).encode('ascii')

    file_object = io.BytesIO(initial_bytes=yaml_data)

    with self.assertRaises(errors.FormatError):
      definitions_reader.ReadFileObject(definitions_registry, file_object)

  def testReadFileObjectPadding(self):
    """Tests the ReadFileObject function of a padding data type."""
    definitions_registry = registry.DataTypeDefinitionsRegistry()
    definitions_reader = reader.YAMLDataTypeDefinitionsFileReader()

    definitions_file = self._GetTestFilePath(['padding.yaml'])
    self._SkipIfPathNotExists(definitions_file)

    with open(definitions_file, 'rb') as file_object:
      with self.assertRaises(errors.FormatError):
        definitions_reader.ReadFileObject(definitions_registry, file_object)

  def testReadFileObjectSequence(self):
    """Tests the ReadFileObject function of a sequence data type."""
    definitions_registry = registry.DataTypeDefinitionsRegistry()
    definitions_reader = reader.YAMLDataTypeDefinitionsFileReader()

    definitions_file = self._GetTestFilePath(['sequence.yaml'])
    self._SkipIfPathNotExists(definitions_file)

    with open(definitions_file, 'rb') as file_object:
      definitions_reader.ReadFileObject(definitions_registry, file_object)

    self.assertEqual(len(definitions_registry._definitions), 3)

    data_type_definition = definitions_registry.GetDefinitionByName('vector4')
    self.assertIsInstance(data_type_definition, data_types.SequenceDefinition)
    self.assertEqual(data_type_definition.name, 'vector4')
    self.assertEqual(data_type_definition.description, '4-dimensional vector')
    self.assertEqual(data_type_definition.aliases, ['VECTOR'])
    self.assertEqual(data_type_definition.element_data_type, 'int32')
    self.assertIsNotNone(data_type_definition.element_data_type_definition)
    self.assertEqual(data_type_definition.number_of_elements, 4)

    byte_size = data_type_definition.GetByteSize()
    self.assertEqual(byte_size, 16)

    definitions_registry = registry.DataTypeDefinitionsRegistry()
    definitions_reader = reader.YAMLDataTypeDefinitionsFileReader()

    definitions_file = self._GetTestFilePath(['sequence_with_structure.yaml'])
    self._SkipIfPathNotExists(definitions_file)

    with self.assertRaises(errors.FormatError):
      with open(definitions_file, 'rb') as file_object:
        definitions_reader.ReadFileObject(definitions_registry, file_object)

  def testReadFileObjectStream(self):
    """Tests the ReadFileObject function of a stream data type."""
    definitions_registry = registry.DataTypeDefinitionsRegistry()
    definitions_reader = reader.YAMLDataTypeDefinitionsFileReader()

    definitions_file = self._GetTestFilePath(['stream.yaml'])
    self._SkipIfPathNotExists(definitions_file)

    with open(definitions_file, 'rb') as file_object:
      definitions_reader.ReadFileObject(definitions_registry, file_object)

    self.assertEqual(len(definitions_registry._definitions), 4)

    data_type_definition = definitions_registry.GetDefinitionByName(
        'utf16le_stream')
    self.assertIsInstance(data_type_definition, data_types.StreamDefinition)
    self.assertEqual(data_type_definition.name, 'utf16le_stream')
    self.assertEqual(
        data_type_definition.description, 'UTF-16 little-endian stream')
    self.assertEqual(data_type_definition.aliases, ['UTF16LE'])
    self.assertEqual(data_type_definition.element_data_type, 'wchar16')
    self.assertIsNotNone(data_type_definition.element_data_type_definition)
    self.assertEqual(data_type_definition.number_of_elements, 8)

    byte_size = data_type_definition.GetByteSize()
    self.assertEqual(byte_size, 16)

  def testReadFileObjectString(self):
    """Tests the ReadFileObject function of a string data type."""
    definitions_registry = registry.DataTypeDefinitionsRegistry()
    definitions_reader = reader.YAMLDataTypeDefinitionsFileReader()

    definitions_file = self._GetTestFilePath(['string.yaml'])
    self._SkipIfPathNotExists(definitions_file)

    with open(definitions_file, 'rb') as file_object:
      definitions_reader.ReadFileObject(definitions_registry, file_object)

    self.assertEqual(len(definitions_registry._definitions), 5)

    data_type_definition = definitions_registry.GetDefinitionByName(
        'utf8_string')
    self.assertIsInstance(data_type_definition, data_types.StringDefinition)
    self.assertEqual(data_type_definition.name, 'utf8_string')
    self.assertEqual(
        data_type_definition.description, 'UTF-8 string')
    self.assertEqual(data_type_definition.element_data_type, 'char')
    self.assertIsNotNone(data_type_definition.element_data_type_definition)
    self.assertEqual(data_type_definition.elements_terminator, b'\x00')
    self.assertEqual(data_type_definition.encoding, 'utf8')

    byte_size = data_type_definition.GetByteSize()
    self.assertIsNone(byte_size)

  def testReadFileObjectStructure(self):
    """Tests the ReadFileObject function of a structure data type."""
    definitions_registry = registry.DataTypeDefinitionsRegistry()
    definitions_reader = reader.YAMLDataTypeDefinitionsFileReader()

    definitions_file = self._GetTestFilePath(['structure.yaml'])
    self._SkipIfPathNotExists(definitions_file)

    with open(definitions_file, 'rb') as file_object:
      definitions_reader.ReadFileObject(definitions_registry, file_object)

    self.assertEqual(len(definitions_registry._definitions), 5)

    data_type_definition = definitions_registry.GetDefinitionByName('point3d')
    self.assertIsInstance(data_type_definition, data_types.StructureDefinition)
    self.assertEqual(data_type_definition.name, 'point3d')
    self.assertEqual(
        data_type_definition.description, 'Point in 3 dimensional space.')
    self.assertEqual(data_type_definition.aliases, ['POINT'])

    self.assertEqual(len(data_type_definition.members), 3)

    member_definition = data_type_definition.members[0]
    self.assertIsInstance(
        member_definition, data_types.MemberDataTypeDefinition)
    self.assertEqual(member_definition.name, 'x')
    self.assertEqual(member_definition.aliases, ['XCOORD'])
    self.assertEqual(member_definition.member_data_type, 'int32')
    self.assertIsNotNone(member_definition.member_data_type_definition)

    byte_size = data_type_definition.GetByteSize()
    self.assertEqual(byte_size, 12)

  def testReadFileObjectStructureWithSequence(self):
    """Tests the ReadFileObject function of a structure with a sequence."""
    definitions_registry = registry.DataTypeDefinitionsRegistry()
    definitions_reader = reader.YAMLDataTypeDefinitionsFileReader()

    definitions_file = self._GetTestFilePath(['structure.yaml'])
    self._SkipIfPathNotExists(definitions_file)

    with open(definitions_file, 'rb') as file_object:
      definitions_reader.ReadFileObject(definitions_registry, file_object)

    self.assertEqual(len(definitions_registry._definitions), 5)

    data_type_definition = definitions_registry.GetDefinitionByName('box3d')
    self.assertIsInstance(data_type_definition, data_types.StructureDefinition)
    self.assertEqual(data_type_definition.name, 'box3d')
    self.assertEqual(
        data_type_definition.description, 'Box in 3 dimensional space.')

    self.assertEqual(len(data_type_definition.members), 1)

    member_definition = data_type_definition.members[0]
    self.assertIsInstance(member_definition, data_types.SequenceDefinition)
    self.assertEqual(member_definition.name, 'triangles')
    self.assertEqual(member_definition.element_data_type, 'triangle3d')
    self.assertIsNotNone(member_definition.element_data_type_definition)

    byte_size = data_type_definition.GetByteSize()
    self.assertEqual(byte_size, 432)

  def testReadFileObjectStructureWithSequenceWithExpression(self):
    """Tests the ReadFileObject function of a structure with a sequence."""
    definitions_registry = registry.DataTypeDefinitionsRegistry()
    definitions_reader = reader.YAMLDataTypeDefinitionsFileReader()

    definitions_file = self._GetTestFilePath(['structure.yaml'])
    self._SkipIfPathNotExists(definitions_file)

    with open(definitions_file, 'rb') as file_object:
      definitions_reader.ReadFileObject(definitions_registry, file_object)

    self.assertEqual(len(definitions_registry._definitions), 5)

    data_type_definition = definitions_registry.GetDefinitionByName('sphere3d')
    self.assertIsInstance(data_type_definition, data_types.StructureDefinition)
    self.assertEqual(data_type_definition.name, 'sphere3d')
    self.assertEqual(
        data_type_definition.description, 'Sphere in 3 dimensional space.')

    self.assertEqual(len(data_type_definition.members), 2)

    member_definition = data_type_definition.members[1]
    self.assertIsInstance(member_definition, data_types.SequenceDefinition)
    self.assertEqual(member_definition.name, 'triangles')
    self.assertEqual(member_definition.element_data_type, 'triangle3d')
    self.assertIsNotNone(member_definition.element_data_type_definition)

    byte_size = data_type_definition.GetByteSize()
    self.assertIsNone(byte_size)

  def testReadFileObjectStructureWithCondition(self):
    """Tests the ReadFileObject function of a structure with condition."""
    definitions_registry = registry.DataTypeDefinitionsRegistry()
    definitions_reader = reader.YAMLDataTypeDefinitionsFileReader()

    definitions_file = self._GetTestFilePath(['structure_with_condition.yaml'])
    self._SkipIfPathNotExists(definitions_file)

    with open(definitions_file, 'rb') as file_object:
      definitions_reader.ReadFileObject(definitions_registry, file_object)

    self.assertEqual(len(definitions_registry._definitions), 3)

    data_type_definition = definitions_registry.GetDefinitionByName(
        'structure_with_condition')
    self.assertIsInstance(data_type_definition, data_types.StructureDefinition)
    self.assertEqual(data_type_definition.name, 'structure_with_condition')

    self.assertEqual(len(data_type_definition.members), 6)

    byte_size = data_type_definition.GetByteSize()
    self.assertIsNone(byte_size)

  def testReadFileObjectStructureWithPadding(self):
    """Tests the ReadFileObject function of a structure with padding."""
    definitions_registry = registry.DataTypeDefinitionsRegistry()
    definitions_reader = reader.YAMLDataTypeDefinitionsFileReader()

    definitions_file = self._GetTestFilePath(['structure_with_padding.yaml'])
    self._SkipIfPathNotExists(definitions_file)

    with open(definitions_file, 'rb') as file_object:
      definitions_reader.ReadFileObject(definitions_registry, file_object)

    self.assertEqual(len(definitions_registry._definitions), 4)

    data_type_definition = definitions_registry.GetDefinitionByName(
        'structure_with_padding')
    self.assertIsInstance(data_type_definition, data_types.StructureDefinition)
    self.assertEqual(data_type_definition.name, 'structure_with_padding')

    self.assertEqual(len(data_type_definition.members), 2)

    member_definition = data_type_definition.members[1]
    self.assertIsInstance(member_definition, data_types.PaddingDefinition)
    self.assertEqual(member_definition.name, 'padding')
    self.assertEqual(member_definition.alignment_size, 8)

    byte_size = data_type_definition.GetByteSize()
    self.assertEqual(byte_size, 8)

    # TODO: add test with composite structure with padding?

  def testReadFileObjectStructureWithSection(self):
    """Tests the ReadFileObject function of a structure with section."""
    definitions_registry = registry.DataTypeDefinitionsRegistry()
    definitions_reader = reader.YAMLDataTypeDefinitionsFileReader()

    definitions_file = self._GetTestFilePath(['structure_with_section.yaml'])
    self._SkipIfPathNotExists(definitions_file)

    with open(definitions_file, 'rb') as file_object:
      definitions_reader.ReadFileObject(definitions_registry, file_object)

    self.assertEqual(len(definitions_registry._definitions), 2)

    data_type_definition = definitions_registry.GetDefinitionByName('3dsphere')
    self.assertIsInstance(data_type_definition, data_types.StructureDefinition)
    self.assertEqual(data_type_definition.name, '3dsphere')

    self.assertEqual(len(data_type_definition.members), 4)
    self.assertEqual(len(data_type_definition.sections), 2)

    byte_size = data_type_definition.GetByteSize()
    self.assertEqual(byte_size, 16)

  def testReadFileObjectStructureWithUnion(self):
    """Tests the ReadFileObject function of a structure with an union."""
    definitions_registry = registry.DataTypeDefinitionsRegistry()
    definitions_reader = reader.YAMLDataTypeDefinitionsFileReader()

    definitions_file = self._GetTestFilePath(['structure_with_union.yaml'])
    self._SkipIfPathNotExists(definitions_file)

    with open(definitions_file, 'rb') as file_object:
      definitions_reader.ReadFileObject(definitions_registry, file_object)

    self.assertEqual(len(definitions_registry._definitions), 3)

    data_type_definition = definitions_registry.GetDefinitionByName(
        'intfloat32')
    self.assertIsInstance(data_type_definition, data_types.StructureDefinition)
    self.assertEqual(data_type_definition.name, 'intfloat32')

    self.assertEqual(len(data_type_definition.members), 1)

    member_definition = data_type_definition.members[0]
    self.assertIsInstance(member_definition, data_types.UnionDefinition)
    self.assertIsNone(member_definition.name)

    byte_size = data_type_definition.GetByteSize()
    self.assertEqual(byte_size, 4)

  def testReadFileObjectStructureWithValues(self):
    """Tests the ReadFileObject function of a structure with values."""
    definitions_registry = registry.DataTypeDefinitionsRegistry()
    definitions_reader = reader.YAMLDataTypeDefinitionsFileReader()

    definitions_file = self._GetTestFilePath(['structure_with_values.yaml'])
    self._SkipIfPathNotExists(definitions_file)

    with open(definitions_file, 'rb') as file_object:
      definitions_reader.ReadFileObject(definitions_registry, file_object)

    self.assertEqual(len(definitions_registry._definitions), 4)

    data_type_definition = definitions_registry.GetDefinitionByName(
        'structure_with_value')
    self.assertIsInstance(data_type_definition, data_types.StructureDefinition)
    self.assertEqual(data_type_definition.name, 'structure_with_value')

    self.assertEqual(len(data_type_definition.members), 3)

    byte_size = data_type_definition.GetByteSize()
    self.assertIsNone(byte_size)

    data_type_definition = definitions_registry.GetDefinitionByName(
        'structure_with_values')
    self.assertIsInstance(data_type_definition, data_types.StructureDefinition)
    self.assertEqual(data_type_definition.name, 'structure_with_values')

    self.assertEqual(len(data_type_definition.members), 2)

    byte_size = data_type_definition.GetByteSize()
    self.assertEqual(byte_size, 8)

  def testReadFileObjectStructureWithStringArray(self):
    """Tests the ReadFileObject function of a string array."""
    definitions_registry = registry.DataTypeDefinitionsRegistry()
    definitions_reader = reader.YAMLDataTypeDefinitionsFileReader()

    definitions_file = self._GetTestFilePath(['string_array.yaml'])
    self._SkipIfPathNotExists(definitions_file)

    with open(definitions_file, 'rb') as file_object:
      definitions_reader.ReadFileObject(definitions_registry, file_object)

    self.assertEqual(len(definitions_registry._definitions), 5)

    data_type_definition = definitions_registry.GetDefinitionByName(
        'string_array')
    self.assertIsInstance(data_type_definition, data_types.StructureDefinition)
    self.assertEqual(data_type_definition.name, 'string_array')

    self.assertEqual(len(data_type_definition.members), 2)

    byte_size = data_type_definition.GetByteSize()
    self.assertIsNone(byte_size)

  def testReadFileObjectStructureFamily(self):
    """Tests the ReadFileObject function of a structure family data type."""
    definitions_registry = registry.DataTypeDefinitionsRegistry()
    definitions_reader = reader.YAMLDataTypeDefinitionsFileReader()

    definitions_file = self._GetTestFilePath(['structure_family.yaml'])
    self._SkipIfPathNotExists(definitions_file)

    with open(definitions_file, 'rb') as file_object:
      definitions_reader.ReadFileObject(definitions_registry, file_object)

    self.assertEqual(len(definitions_registry._definitions), 8)

    data_type_definition = definitions_registry.GetDefinitionByName(
        'group_descriptor')
    self.assertIsInstance(
        data_type_definition, data_types.StructureFamilyDefinition)
    self.assertEqual(data_type_definition.name, 'group_descriptor')
    self.assertEqual(data_type_definition.description, 'Group descriptor')

    self.assertEqual(len(data_type_definition.members), 2)

    member_definition = data_type_definition.members[0]
    self.assertIsInstance(member_definition, data_types.StructureDefinition)
    self.assertEqual(member_definition.name, 'group_descriptor_ext2')

    byte_size = data_type_definition.GetByteSize()
    # TODO: determine the size of the largest family member.
    self.assertIsNone(byte_size)

  def testReadFileObjectStructureGroup(self):
    """Tests the ReadFileObject function of a structure group data type."""
    definitions_registry = registry.DataTypeDefinitionsRegistry()
    definitions_reader = reader.YAMLDataTypeDefinitionsFileReader()

    definitions_file = self._GetTestFilePath(['structure_group.yaml'])
    self._SkipIfPathNotExists(definitions_file)

    with open(definitions_file, 'rb') as file_object:
      definitions_reader.ReadFileObject(definitions_registry, file_object)

    self.assertEqual(len(definitions_registry._definitions), 9)

    data_type_definition = definitions_registry.GetDefinitionByName('bsm_token')
    self.assertIsInstance(
        data_type_definition, data_types.StructureGroupDefinition)
    self.assertEqual(data_type_definition.name, 'bsm_token')
    self.assertEqual(data_type_definition.description, 'BSM token')

    base_definition = data_type_definition.base
    self.assertIsInstance(base_definition, data_types.StructureDefinition)
    self.assertEqual(base_definition.name, 'bsm_token_base')

    self.assertEqual(data_type_definition.identifier, 'token_type')

    self.assertEqual(len(data_type_definition.members), 2)

    member_definition = data_type_definition.members[0]
    self.assertIsInstance(member_definition, data_types.StructureDefinition)
    self.assertEqual(member_definition.name, 'bsm_token_arg32')

  def testReadFileObjectUnion(self):
    """Tests the ReadFileObject function of an union data type."""
    definitions_registry = registry.DataTypeDefinitionsRegistry()
    definitions_reader = reader.YAMLDataTypeDefinitionsFileReader()

    definitions_file = self._GetTestFilePath(['union.yaml'])
    self._SkipIfPathNotExists(definitions_file)

    with open(definitions_file, 'rb') as file_object:
      definitions_reader.ReadFileObject(definitions_registry, file_object)

    self.assertEqual(len(definitions_registry._definitions), 3)

    data_type_definition = definitions_registry.GetDefinitionByName('union')
    self.assertIsInstance(data_type_definition, data_types.UnionDefinition)
    self.assertEqual(data_type_definition.name, 'union')

    self.assertEqual(len(data_type_definition.members), 2)

    member_definition = data_type_definition.members[0]
    self.assertIsInstance(
        member_definition, data_types.MemberDataTypeDefinition)
    self.assertEqual(member_definition.name, 'long')
    self.assertEqual(member_definition.member_data_type, 'int32')
    self.assertIsNotNone(member_definition.member_data_type_definition)

    byte_size = data_type_definition.GetByteSize()
    self.assertEqual(byte_size, 4)

  def testReadFileObjectUnionWithCondition(self):
    """Tests the ReadFileObject function of an union with condition."""
    definitions_registry = registry.DataTypeDefinitionsRegistry()
    definitions_reader = reader.YAMLDataTypeDefinitionsFileReader()

    definitions_file = self._GetTestFilePath(['union_with_condition.yaml'])
    self._SkipIfPathNotExists(definitions_file)

    with self.assertRaises(errors.FormatError):
      with open(definitions_file, 'rb') as file_object:
        definitions_reader.ReadFileObject(definitions_registry, file_object)

  def testReadFileObjectUUID(self):
    """Tests the ReadFileObject function of an UUID data type."""
    definitions_registry = registry.DataTypeDefinitionsRegistry()
    definitions_reader = reader.YAMLDataTypeDefinitionsFileReader()

    definitions_file = self._GetTestFilePath(['uuid.yaml'])
    self._SkipIfPathNotExists(definitions_file)

    with open(definitions_file, 'rb') as file_object:
      definitions_reader.ReadFileObject(definitions_registry, file_object)

    self.assertEqual(len(definitions_registry._definitions), 1)

    data_type_definition = definitions_registry.GetDefinitionByName('uuid')
    self.assertIsInstance(
        data_type_definition, data_types.UUIDDefinition)
    self.assertEqual(data_type_definition.name, 'uuid')
    self.assertEqual(
        data_type_definition.byte_order, definitions.BYTE_ORDER_LITTLE_ENDIAN)
    self.assertEqual(data_type_definition.size, 16)
    self.assertEqual(data_type_definition.units, 'bytes')

    byte_size = data_type_definition.GetByteSize()
    self.assertEqual(byte_size, 16)


if __name__ == '__main__':
  unittest.main()
