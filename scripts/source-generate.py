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

  def GenerateStructureDefinitionFile(
      self, template_filename, template_mappings, output_writer):
    """Generates a structure definition file.

    Args:
      template_filename (str): path of the template file.
      template_mappings (dict[str, str]): template mappings, where the key
          maps to the name of a template variable.
      output_writer (OutputWriter): output writer.
    """
    template_string = self._ReadTemplateFile(template_filename)

    try:
      output_data = template_string.substitute(template_mappings)

    except (KeyError, ValueError) as exception:
      logging.error(
          u'Unable to format template: {0:s} with error: {1:s}'.format(
              template_filename, exception))
      return

    output_writer.WriteData(output_data)


class SourceGenerator(object):
  """Class that generates source based on dtFabric format definitions."""

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

  def _GenerateStructureMembers(self, struct_definition, prefix):
    """Generates structure members.

    Args:
      prefix (str): prefix.
      struct_definition (StructDefinition): struct definition.

    Returns:
      list[str]: lines of output.

    Raises:
      RuntimeError: if the size of the data type is not defined.
    """
    lines = []

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

    return lines

  def Generate(self, prefix):
    """Generates source from the definitions.

    Args:
      prefix (str): prefix.
    """
    if prefix and not prefix.endswith(u'_'):
      prefix = u'{0:s}_'.format(prefix)
    else:
      prefix = prefix or u''

    source_file_generator = SourceFileGenerator()

    template_mappings = {
        u'authors': u'Joachim Metz <joachim.metz@gmail.com>',
        u'copyright': u'2016',
        u'prefix': prefix,
        u'prefix_upper_case': prefix.upper()}

    template_filename = os.path.join(u'data', u'templates', u'structure.h')

    output_writer = StdoutWriter()

    for struct_definition in (
        self._structure_definitions_registry.GetDefinitions()):
      lines = self._GenerateStructureMembers(struct_definition, prefix)

      template_mappings[u'structure_description'] = struct_definition.description
      template_mappings[u'structure_members'] = u'\n'.join(lines)
      template_mappings[u'structure_name'] = struct_definition.name
      template_mappings[u'structure_name_upper_case'] = struct_definition.name.upper()

      source_file_generator.GenerateStructureDefinitionFile(
        template_filename, template_mappings, output_writer)

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


class StdoutWriter(object):
  """Class that defines a stdout output writer."""

  def Open(self):
    """Opens the output writer object.

    Returns:
      bool: True if successful or False if not.
    """
    return True

  def Close(self):
    """Closes the output writer object."""
    pass

  def WriteData(self, data):
    """Writes data to stdout.

    Args:
      data (bytes): data to write.
    """
    print(data.encode(u'utf8'))


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
