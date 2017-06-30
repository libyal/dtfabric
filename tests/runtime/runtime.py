# -*- coding: utf-8 -*-
"""Tests for the run-time object."""

from __future__ import unicode_literals

import unittest

from dtfabric.runtime import runtime

from tests import test_lib


class StructureValuesClassFactoryTest(test_lib.BaseTestCase):
  """Structure values class factory tests."""

  # pylint: disable=protected-access

  @test_lib.skipUnlessHasTestFile(['structure.yaml'])
  def testCreateClassTemplate(self):
    """Tests the _CreateClassTemplate function."""
    definitions_file = self._GetTestFilePath(['structure.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)

    data_type_definition = definitions_registry.GetDefinitionByName('point3d')

    class_template = runtime.StructureValuesClassFactory._CreateClassTemplate(
        data_type_definition)
    self.assertIsNotNone(class_template)

    # TODO: implement error conditions.

  def testIsIdentifier(self):
    """Tests the _IsIdentifier function."""
    result = runtime.StructureValuesClassFactory._IsIdentifier('valid')
    self.assertTrue(result)

    result = runtime.StructureValuesClassFactory._IsIdentifier('_valid')
    self.assertTrue(result)

    result = runtime.StructureValuesClassFactory._IsIdentifier('valid1')
    self.assertTrue(result)

    result = runtime.StructureValuesClassFactory._IsIdentifier('')
    self.assertFalse(result)

    result = runtime.StructureValuesClassFactory._IsIdentifier('0invalid')
    self.assertFalse(result)

    result = runtime.StructureValuesClassFactory._IsIdentifier('in-valid')
    self.assertFalse(result)

  def testValidateDataTypeDefinition(self):
    """Tests the _ValidateDataTypeDefinition function."""
    definitions_file = self._GetTestFilePath(['structure.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)

    data_type_definition = definitions_registry.GetDefinitionByName('point3d')

    runtime.StructureValuesClassFactory._ValidateDataTypeDefinition(
        data_type_definition)

    # TODO: implement error conditions.

  def testCreateClass(self):
    """Tests the CreateClass function."""
    definitions_file = self._GetTestFilePath(['structure.yaml'])
    definitions_registry = self._CreateDefinitionRegistryFromFile(
        definitions_file)

    data_type_definition = definitions_registry.GetDefinitionByName('point3d')

    structure_values_class = runtime.StructureValuesClassFactory.CreateClass(
        data_type_definition)
    self.assertIsNotNone(structure_values_class)


if __name__ == '__main__':
  unittest.main()
