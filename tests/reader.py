# -*- coding: utf-8 -*-
"""Tests for the data type definitions readers."""

import io
import unittest

from dtfabric import definitions
from dtfabric import errors
from dtfabric import reader


# TODO: add tests for DataTypeDefinitionsFileReader.


class YAMLDataTypeDefinitionsFileReaderTest(unittest.TestCase):
  """Class to test the YAML data type definitions reader."""

  def testReadFileObjectInteger(self):
    """Tests the ReadFileObject function of an integer data type."""
    definition_reader = reader.YAMLDataTypeDefinitionsFileReader()

    yaml_data = b'\n'.join([
        b'name: int8',
        b'type: integer',
        b'attributes:',
        b'  format: signed',
        b'  size: 1',
        b'  units: byte'])

    file_object = io.BytesIO(initial_bytes=yaml_data)

    data_type_definitions = list(definition_reader.ReadFileObject(file_object))
    self.assertEqual(len(data_type_definitions), 1)

    data_type_definition = data_type_definitions[0]
    self.assertIsInstance(data_type_definition, definitions.IntegerDefinition)
    self.assertEqual(data_type_definition.name, u'int8')
    self.assertEqual(data_type_definition.size, 1)
    self.assertEqual(data_type_definition.units, u'byte')

  def testReadFileObjectMissingName(self):
    """Tests the ReadFileObject function with a missing name."""
    definition_reader = reader.YAMLDataTypeDefinitionsFileReader()

    yaml_data = b'\n'.join([
        b'type: integer',
        b'attributes:',
        b'  format: signed',
        b'  size: 1',
        b'  units: byte'])

    file_object = io.BytesIO(initial_bytes=yaml_data)

    with self.assertRaises(errors.FormatError):
      list(definition_reader.ReadFileObject(file_object))

  def testReadFileObjectMissingType(self):
    """Tests the ReadFileObject function with a missing type."""
    definition_reader = reader.YAMLDataTypeDefinitionsFileReader()

    yaml_data = b'\n'.join([
        b'name: int8',
        b'attributes:',
        b'  format: signed',
        b'  size: 1',
        b'  units: byte'])

    file_object = io.BytesIO(initial_bytes=yaml_data)

    with self.assertRaises(errors.FormatError):
      list(definition_reader.ReadFileObject(file_object))

  def testReadFileObjectStructure(self):
    """Tests the ReadFileObject function of a structure data type."""
    definition_reader = reader.YAMLDataTypeDefinitionsFileReader()

    yaml_data = b'\n'.join([
        b'name: directory_descriptor',
        b'aliases: [MINIDUMP_DIRECTORY]',
        b'type: structure',
        b'description: Minidump file header',
        (b'urls: [\'https://msdn.microsoft.com/en-us/library/windows/desktop/'
         b'ms680365(v=vs.85).aspx\']'),
        b'members:',
        b'- name: stream_type',
        b'  aliases: [StreamType]',
        b'  data_type: uint32',
        b'- name: location',
        b'  aliases: [Location]',
        b'  data_type: uint32'])

    file_object = io.BytesIO(initial_bytes=yaml_data)

    data_type_definitions = list(definition_reader.ReadFileObject(file_object))
    self.assertEqual(len(data_type_definitions), 1)


if __name__ == '__main__':
  unittest.main()
