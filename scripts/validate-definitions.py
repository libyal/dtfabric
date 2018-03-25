#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
"""Script to validate dtFabric format definitions."""

from __future__ import print_function
from __future__ import unicode_literals
import argparse
import glob
import logging
import os
import sys

from dtfabric import errors
from dtfabric import reader
from dtfabric import registry


class DefinitionsValidator(object):
  """dtFabric definitions validator."""

  def CheckDirectory(self, path, extension='yaml'):
    """Validates definition files in a directory.

    Args:
      path (str): path of the definition file.
      extension (Optional[str]): extension of the filenames to read.

    Returns:
      bool: True if the directory contains valid definitions.
    """
    result = True

    if extension:
      glob_spec = os.path.join(path, '*.{0:s}'.format(extension))
    else:
      glob_spec = os.path.join(path, '*')

    for definition_file in sorted(glob.glob(glob_spec)):
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
    print('Checking: {0:s}'.format(path))

    definitions_registry = registry.DataTypeDefinitionsRegistry()
    definitions_reader = reader.YAMLDataTypeDefinitionsFileReader()
    result = False

    try:
      definitions_reader.ReadFile(definitions_registry, path)
      result = True

    except KeyError as exception:
      logging.warning((
          'Unable to register data type definition in file: {0:s} with '
          'error: {1:s}').format(path, exception))

    except errors.FormatError as exception:
      logging.warning(
          'Unable to validate file: {0:s} with error: {1:s}'.format(
              path, exception))

    return result


def Main():
  """The main program function.

  Returns:
    bool: True if successful or False if not.
  """
  argument_parser = argparse.ArgumentParser(
      description='Validates dtFabric format definitions.')

  argument_parser.add_argument(
      'source', nargs='?', action='store', metavar='PATH', default=None,
      help=(
          'path of the file or directory containing the dtFabric format '
          'definitions.'))

  options = argument_parser.parse_args()

  if not options.source:
    print('Source value is missing.')
    print('')
    argument_parser.print_help()
    print('')
    return False

  if not os.path.exists(options.source):
    print('No such file: {0:s}'.format(options.source))
    print('')
    return False

  logging.basicConfig(
      level=logging.INFO, format='[%(levelname)s] %(message)s')


  source_is_directory = os.path.isdir(options.source)

  validator = DefinitionsValidator()

  if source_is_directory:
    source_description = os.path.join(options.source, '*.yaml')
  else:
    source_description = options.source

  print('Validating dtFabric definitions in: {0:s}'.format(source_description))
  if source_is_directory:
    result = validator.CheckDirectory(options.source)
  else:
    result = validator.CheckFile(options.source)

  if not result:
    print('FAILURE')
  else:
    print('SUCCESS')

  return result


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
