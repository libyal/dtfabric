# -*- coding: utf-8 -*-
"""Tests for the data type definitions readers."""

import io
import unittest

from dtfabric import errors
from dtfabric import reader


# TODO: add tests for DataTypeDefinitionsFileReader.


class YAMLDataTypeDefinitionsFileReaderTest(unittest.TestCase):
  """Class to test the YAML data type definitions reader."""

  def testReadFileObject(self):
    """Tests the ReadFileObject function."""
    definition_reader = reader.YAMLDataTypeDefinitionsFileReader()

    yaml_data = b'\n'.join([
        b'name: int8',
        b'type: integer',
        b'attributes:',
        b'- format: signed',
        b'  size: 1',
        b'  units: byte'])

    file_object = io.BytesIO(initial_bytes=yaml_data)

    definitions = list(definition_reader.ReadFileObject(file_object))
    self.assertEqual(len(definitions), 1)

  def testReadFileObjectMissingName(self):
    """Tests the ReadFileObject function with a missing name."""
    definition_reader = reader.YAMLDataTypeDefinitionsFileReader()

    yaml_data = b'\n'.join([
        b'type: integer',
        b'attributes:',
        b'- format: signed',
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
        b'- format: signed',
        b'  size: 1',
        b'  units: byte'])

    file_object = io.BytesIO(initial_bytes=yaml_data)

    with self.assertRaises(errors.FormatError):
      list(definition_reader.ReadFileObject(file_object))


if __name__ == '__main__':
  unittest.main()
