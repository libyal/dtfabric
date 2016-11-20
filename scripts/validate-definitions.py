#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Script to validate dtFabric format definitions."""

from __future__ import print_function
import argparse
import glob
import logging
import os
import sys

from dtfabric import definitions
from dtfabric import errors
from dtfabric import reader
from dtfabric import registry


class DefinitionsValidator(object):
  """Class to define a dtFabric definitions validator."""

  def __init__(self):
    """Initializes a dtFabric definitions validator."""
    super(DefinitionsValidator, self).__init__()
    self._structure_definitions_registry = (
        registry.StructureDefinitionsRegistry())

  def CheckDirectory(self, path, extension=u'yaml'):
    """Validates definition files in a directory.

    Args:
      path (str): path of the definition file.
      extension (Optional[str]): extension of the filenames to read.

    Returns:
      bool: True if the directory contains valid definitions.
    """
    result = True

    if extension:
      glob_spec = os.path.join(path, u'*.{0:s}'.format(extension))
    else:
      glob_spec = os.path.join(path, u'*')

    for definition_file in glob.glob(glob_spec):
      if not self.CheckFile(definition_file):
        result = False

    return result

  def CheckFile(self, path):
    """Validates the definition in a file.

    Args:
      path (str): path of the definition file.

    Returns:
      bool: True if the file contains valid definitions.
    """
    definitions_reader = reader.YAMLDefinitionsFileReader()
    result = True

    try:
      for definition_object in definitions_reader.ReadFile(path):
        if isinstance(definition_object, definitions.StructureDefinition):
          try:
            self._structure_definitions_registry.RegisterDefinition(
                definition_object)

          except KeyError:
            logging.warning(
                u'Duplicate structure definition: {0:s} in file: {1:s}'.format(
                    definition_object.name, path))
            result = False

    except errors.FormatError as exception:
      logging.warning(
          u'Unable to validate file: {0:s} with error: {1:s}'.format(
              path, exception))
      result = False

    return result


def Main():
  """The main program function.

  Returns:
    bool: True if successful or False if not.
  """
  argument_parser = argparse.ArgumentParser(
      description=u'Validates dtFabric format definitions.')

  argument_parser.add_argument(
      u'source', nargs=u'?', action=u'store', metavar=u'PATH', default=None,
      help=(
          u'path of the file containing the dtFabric format definitions.'))

  options = argument_parser.parse_args()

  if not options.source:
    print(u'Source value is missing.')
    print(u'')
    argument_parser.print_help()
    print(u'')
    return False

  if not os.path.exists(options.source):
    print(u'No such file: {0:s}'.format(options.source))
    print(u'')
    return False

  logging.basicConfig(
      level=logging.INFO, format=u'[%(levelname)s] %(message)s')


  source_is_directory = os.path.isdir(options.source)

  validator = DefinitionsValidator()

  if source_is_directory:
    source_description = os.path.join(options.source, u'*.yaml')
  else:
    source_description = options.source

  print(u'Validating dtFabric definitions in: {0:s}'.format(source_description))
  if source_is_directory:
    result = validator.CheckDirectory(options.source)
  else:
    result = validator.CheckFile(options.source)

  if not result:
    print(u'FAILURE')
  else:
    print('SUCCESS')

  return result


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
