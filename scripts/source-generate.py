#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Script to generate source based on dtFabric format definitions."""

from __future__ import print_function
import argparse
import logging
import os
import sys

from dtfabric import definitions
from dtfabric import errors
from dtfabric import reader
from dtfabric import registry
from dtfabric.generators import output_writers
from dtfabric.generators import template_string


class SourceGenerator(object):
  """Generates source based on dtFabric format definitions."""

  _DATA_TYPE_CALLBACKS = {
      definitions.TYPE_INDICATOR_STRUCTURE: u'_GenerateStructure',
  }

  def __init__(self, templates_path, prefix):
    """Initializes a source generator.

    Args:
      templates_path (str): templates path.
      prefix (str): prefix.
    """
    if prefix and not prefix.endswith(u'_'):
      prefix = u'{0:s}_'.format(prefix)
    else:
      prefix = prefix or u''

    super(SourceGenerator, self).__init__()
    self._definitions_registry = registry.DataTypeDefinitionsRegistry()
    self._prefix = prefix
    self._templates_path = templates_path
    self._template_string_generator = template_string.TemplateStringGenerator()

  def _GenerateStructure(self, data_type_definition):
    """Generates structure members.

    Args:
      data_type_definition (DataTypeDefinition): structure data type definition.

    Returns:
      list[str]: lines of output.

    Raises:
      RuntimeError: if the size of the data type is not defined.
    """
    lines = []

    last_index = len(data_type_definition.members) - 1
    for index, member_definition in enumerate(data_type_definition.members):
      name = member_definition.name

      data_type_size = member_definition.GetByteSize()
      if not data_type_size:
        raise RuntimeError(
            u'Size of structure member: {0:s} not defined'.format(name))

      description = name.replace(u'_', u' ')

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

  def Generate(self):
    """Generates source code from the data type definitions."""
    generator = template_string.TemplateStringGenerator()

    template_mappings = {
        u'authors': u'Joachim Metz <joachim.metz@gmail.com>',
        u'copyright': u'2016',
        u'prefix': self._prefix,
        u'prefix_upper_case': self._prefix.upper()}

    template_filename = os.path.join(self._templates_path, u'structure.h')

    output_writer = output_writers.StdoutWriter()

    for data_type_definition in self._definitions_registry.GetDefinitions():
      data_type_callback = self._DATA_TYPE_CALLBACKS.get(
          data_type_definition.TYPE_INDICATOR, None)
      if data_type_callback:
        data_type_callback = getattr(self, data_type_callback, None)
      if not data_type_callback:
        continue

      lines = data_type_callback(data_type_definition)

      template_mappings[u'structure_description'] = (
          data_type_definition.description)
      template_mappings[u'structure_members'] = u'\n'.join(lines)
      template_mappings[u'structure_name'] = data_type_definition.name
      template_mappings[u'structure_name_upper_case'] = (
          data_type_definition.name.upper())

      generator.Generate(template_filename, template_mappings, output_writer)

  def ReadDefinitions(self, path):
    """Reads the definitions form file or directory.

    Args:
      path (str): path of the definition file or directory.
    """
    definitions_reader = reader.YAMLDataTypeDefinitionsFileReader()
    definitions_reader.ReadFile(self._definitions_registry, path)


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
      help=u'name of the file containing the dtFabric format definitions.')

  options = argument_parser.parse_args()

  if not options.source:
    print(u'Source value is missing.')
    print(u'')
    argument_parser.print_help()
    print(u'')
    return False

  if not os.path.isfile(options.source):
    print(u'No such file: {0:s}'.format(options.source))
    print(u'')
    return False

  logging.basicConfig(
      level=logging.INFO, format=u'[%(levelname)s] %(message)s')

  # TODO: allow user to set templates path
  # TODO: detect templates path
  templates_path = os.path.join(u'data')

  source_generator = SourceGenerator(templates_path, options.prefix)

  try:
    source_generator.ReadDefinitions(options.source)
  except errors.FormatError as exception:
    print(u'Unable to read definitions with error: {0:s}'.format(exception))
    return False

  source_generator.Generate()

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
