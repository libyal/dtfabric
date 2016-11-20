#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Script to generate source based on dtFabric format definitions."""

from __future__ import print_function
import argparse
import glob
import logging
import os
import string
import sys

from dtfabric import definitions
from dtfabric import errors
from dtfabric import reader
from dtfabric import registry


class SourceFileGenerator(object):
  """Class that generates a source file."""

  def __init__(self):
    """Initialize a source file generator."""
    super(SourceFileGenerator, self).__init__()

  def _GenerateSection(
      self, template_filename, template_mappings, output_writer,
      output_filename, access_mode='wb'):
    """Generates a section from template filename.

    Args:
      template_filename (str): name of the template file.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      output_writer (OutputWriter): output writer.
      output_filename (str): name of the output file.
      access_mode (Optional[str]): output file access mode.
    """
    template_string = self._ReadTemplateFile(template_filename)

    try:
      output_data = template_string.substitute(template_mappings)

    except (KeyError, ValueError) as exception:
      logging.error(
          u'Unable to format template: {0:s} with error: {1:s}'.format(
              template_filename, exception))
      return

    output_writer.WriteFile(
        output_filename, output_data, access_mode=access_mode)

  def _ReadTemplateFile(self, filename):
    """Reads a template string from file.

    Args:
      filename (str): name of the file containing the template string.

    Returns:
      string.Template: template string.
    """
    file_object = open(filename, 'rb')
    file_data = file_object.read()
    file_object.close()
    return string.Template(file_data)


class SourceGenerator(object):
  """Class generates source based on dtFabric format definitions."""

  _DATA_TYPE_SIZES = {
      u'filetime': 8,
      u'guid': 16,
      u'int64': 8,
      u'int32': 4,
      u'int16': 2,
      u'int8': 1,
      u'uint64': 8,
      u'uint32': 4,
      u'uint16': 2,
      u'uint8': 1,
  }

  def __init__(self):
    """Initializes a source generator."""
    super(SourceGenerator, self).__init__()
    self._structure_definitions_registry = (
        registry.StructureDefinitionsRegistry())

  def _GenerateStruct(self, struct_definition, prefix):
    """Generates a struct.

    Args:
      prefix (str): prefix.
      struct_definition (StructDefinition): struct definition.

    Returns:
      list[str]: lines of output.

    Raises:
      RuntimeError: if the size of the data type is not defined.
    """
    struct_name = struct_definition.name
    if prefix:
      struct_name = u'{0:s}_{1:s}'.format(prefix, struct_name)
  
    lines = [
        u'typedef struct {0:s} {0:s}_t;'.format(struct_name),
        u'',
        u'struct {0:s}'.format(struct_name),
        u'{']

    last_index = len(struct_definition.attributes) - 1
    for index, struct_attribute_definition in enumerate(
        struct_definition.attributes):

      data_type = struct_attribute_definition.data_type
      data_type_size = self._DATA_TYPE_SIZES.get(data_type, None)
      name = struct_attribute_definition.name
      description = name.replace(u'_', u' ')

      if not data_type_size:
        raise RuntimeError(
            u'Size of data type: {0:s} not defined'.format(data_type))

      if data_type_size == 1:
        lines.extend([
            u'\t/* The {0:s}'.format(description),
            u'\t * Consists of {0:d} byte'.format(data_type_size),
            u'\t */',
            u'\tuint8_t {0:s};'.format(name)
        ])

      else:
        lines.extend([
            u'\t/* The {0:s}'.format(description),
            u'\t * Consists of {0:d} bytes'.format(data_type_size),
            u'\t */',
            u'\tuint8_t {0:s}[ {1:d} ];'.format(name, data_type_size)
        ])

      if index != last_index:
        lines.append(u'')

    lines.append(u'};')
 
    return lines

  def Generate(self, prefix):
    """Generates source from the definitions.

    Args:
      prefix (str): prefix.
    """
    for struct_definition in (
        self._structure_definitions_registry.GetDefinitions()):
      lines = self._GenerateStruct(struct_definition, prefix)

      lines.append(u'')
      print(u'\n'.join(lines))

  def ReadDefinitions(self, path):
    """Reads the definitions form file or directory.

    Args:
      path (str): path of the definition file or directory.
    """
    definitions_reader = reader.YAMLDefinitionsFileReader()

    if os.path.isdir(path):
      self._structure_definitions_registry.ReadFromDirectory(
          definitions_reader, path)
    else:
      self._structure_definitions_registry.ReadFromFile(
          definitions_reader, path)


def Main():
  """The main program function.

  Returns:
    bool: True if successful or False if not.
  """
  argument_parser = argparse.ArgumentParser(
      description=u'Generates source based on dtFabric format definitions.')

  argument_parser.add_argument(
      u'--prefix', dest=u'prefix', action=u'store', metavar=u'PREFIX',
      default=None, help=u'C code prefix.')

  argument_parser.add_argument(
      u'source', nargs=u'?', action=u'store', metavar=u'PATH', default=None,
      help=(
          u'path of the file or directory containing the dtFabric format '
          u'definitions.'))

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

  source_generator = SourceGenerator()

  try:
    source_generator.ReadDefinitions(options.source)
  except errors.FormatError as exception:
    print(u'Unable to read definitions with error: {0:s}'.format(exception))
    return False

  source_generator.Generate(options.prefix)
  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
