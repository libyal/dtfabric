# -*- coding: utf-8 -*-
"""Tests for the run-time object."""

import os
import unittest

from dtfabric import reader
from dtfabric import registry
from dtfabric import runtime

from tests import test_lib


class DataTypeMapTest(test_lib.BaseTestCase):
  """Class to test the data type map."""

  # pylint: disable=protected-access

  def test_GetStructFormatString(self):
    """Tests the _GetStructFormatString function."""
    definitions_registry = registry.DataTypeDefinitionsRegistry()
    definitions_reader = reader.YAMLDataTypeDefinitionsFileReader()

    definitions_file = os.path.join(u'data', u'definitions', u'integers.yaml')
    with open(definitions_file, 'rb') as file_object:
      definitions_reader.ReadFileObject(definitions_registry, file_object)

    expected_format_strings = {
        u'int8': u'b',
        u'int16': u'h',
        u'int32': u'l',
        u'int64': u'q',
        u'uint8': u'B',
        u'uint16': u'H',
        u'uint32': u'L',
        u'uint64': u'Q'}

    format_strings = {}
    for definition_name in expected_format_strings.keys():
      data_type_definition = definitions_registry.GetDefinitionByName(
          definition_name)
      format_string = runtime.DataTypeMap._GetStructFormatString(
          data_type_definition)
      format_strings[definition_name] = format_string

    self.assertEqual(format_strings, expected_format_strings)

  def testMapByteStream(self):
    """Tests the MapByteStream function."""


if __name__ == '__main__':
  unittest.main()
