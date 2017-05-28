#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Script to generate source based on dtFabric format definitions."""

from __future__ import print_function
import argparse
import datetime
import logging
import os
import sys

from dtfabric import definitions
from dtfabric import errors
from dtfabric import reader
from dtfabric import registry
from dtfabric.generators import template_string


class SourceGenerator(object):
  """Generates source based on dtFabric format definitions."""

  _RUNTIME_STRUCTURE_HEADER_TEMPLATE_FILE = u'runtime_structure.h'
  _RUNTIME_STRUCTURE_SOURCE_TEMPLATE_FILE = u'runtime_structure.c'
  _STORED_STRUCTURE_HEADER_TEMPLATE_FILE = u'stored_structure.h'

  def __init__(self, templates_path, prefix=None):
    """Initializes a source generator.

    Args:
      templates_path (str): templates path.
      prefix (Optional[str]): prefix.
    """
    super(SourceGenerator, self).__init__()
    self._definitions_registry = registry.DataTypeDefinitionsRegistry()
    self._prefix = prefix
    self._templates_path = templates_path
    self._template_string_generator = template_string.TemplateStringGenerator()

  def _GenerateRuntimeStructureHeader(self, data_type_definition):
    """Generates a runtime structure header.

    Args:
      data_type_definition (DataTypeDefinition): structure data type definition.
    """
    template_mappings = self._GetTemplateMappings()

    if data_type_definition.description:
      structure_description = data_type_definition.description
    else:
      structure_description = data_type_definition.name

    structure_members = self._GetRuntimeStructureHeaderMembers(
        data_type_definition)

    library_name = u'lib{0:s}'.format(self._prefix)

    template_mappings[u'library_name'] = library_name
    template_mappings[u'library_name_upper_case'] = library_name.upper()

    template_mappings[u'structure_description'] = structure_description
    template_mappings[u'structure_members'] = structure_members
    template_mappings[u'structure_name'] = data_type_definition.name
    template_mappings[u'structure_name_upper_case'] = (
        data_type_definition.name.upper())

    template_filename = os.path.join(
        self._templates_path, self._RUNTIME_STRUCTURE_HEADER_TEMPLATE_FILE)

    output_data = self._template_string_generator.Generate(
        template_filename, template_mappings)

    if self._prefix:
      output_file = os.path.join(
          u'lib{0:s}'.format(self._prefix),
          u'lib{0:s}_{1:s}.h'.format(self._prefix, data_type_definition.name))
    else:
      output_file = self._RUNTIME_STRUCTURE_HEADER_TEMPLATE_FILE

    logging.info(u'Writing: {0:s}'.format(output_file))
    with open(output_file, 'wb') as file_object:
      file_object.write(output_data)

  def _GenerateRuntimeStructureSource(self, data_type_definition):
    """Generates a runtime structure source.

    Args:
      data_type_definition (DataTypeDefinition): structure data type definition.
    """
    template_mappings = self._GetTemplateMappings()

    if data_type_definition.description:
      structure_description = data_type_definition.description
    else:
      structure_description = data_type_definition.name

    structure_members_copy_from_byte_stream = (
        self._GetRuntimeStructureSourceMembersCopyFromByteStream(
            data_type_definition))

    structure_members_debug_print = (
        self._GetRuntimeStructureSourceMembersDebugPrint(
            data_type_definition))

    library_name = u'lib{0:s}'.format(self._prefix)

    template_mappings[u'library_name'] = library_name
    template_mappings[u'library_name_upper_case'] = library_name.upper()

    template_mappings[u'structure_description'] = structure_description
    template_mappings[u'structure_members_copy_from_byte_stream'] = (
        structure_members_copy_from_byte_stream)
    template_mappings[u'structure_members_debug_print'] = (
        structure_members_debug_print)
    template_mappings[u'structure_name'] = data_type_definition.name
    template_mappings[u'structure_name_upper_case'] = (
        data_type_definition.name.upper())

    template_filename = os.path.join(
        self._templates_path, self._RUNTIME_STRUCTURE_SOURCE_TEMPLATE_FILE)

    output_data = self._template_string_generator.Generate(
        template_filename, template_mappings)

    if self._prefix:
      output_file = os.path.join(
          u'lib{0:s}'.format(self._prefix),
          u'lib{0:s}_{1:s}.c'.format(self._prefix, data_type_definition.name))
    else:
      output_file = self._RUNTIME_STRUCTURE_SOURCE_TEMPLATE_FILE

    logging.info(u'Writing: {0:s}'.format(output_file))
    with open(output_file, 'wb') as file_object:
      file_object.write(output_data)

  def _GenerateStoredStructureHeader(self, data_type_definition):
    """Generates a stored structure header.

    Args:
      data_type_definition (DataTypeDefinition): structure data type definition.
    """
    format_definition = self._GetFormatDefinitions()

    template_mappings = self._GetTemplateMappings()

    if data_type_definition.description:
      structure_description = data_type_definition.description
    else:
      structure_description = data_type_definition.name

    if format_definition.description:
      structure_description = u'{0:s} of a {1:s}'.format(
          structure_description, format_definition.description)

    structure_members = self._GetStoredStructureHeaderMembers(
        data_type_definition)

    template_mappings[u'structure_description'] = structure_description
    template_mappings[u'structure_members'] = structure_members
    template_mappings[u'structure_name'] = data_type_definition.name
    template_mappings[u'structure_name_upper_case'] = (
        data_type_definition.name.upper())

    template_filename = os.path.join(
        self._templates_path, self._STORED_STRUCTURE_HEADER_TEMPLATE_FILE)

    output_data = self._template_string_generator.Generate(
        template_filename, template_mappings)

    if self._prefix:
      output_file = os.path.join(
          u'lib{0:s}'.format(self._prefix),
          u'{0:s}_{1:s}.h'.format(self._prefix, data_type_definition.name))
    else:
      output_file = self._STORED_STRUCTURE_HEADER_TEMPLATE_FILE

    logging.info(u'Writing: {0:s}'.format(output_file))
    with open(output_file, 'wb') as file_object:
      file_object.write(output_data)

  def _GetFormatDefinitions(self):
    """Retrieves the format definition.

    Returns:
      FormatDefinition: format definition.
    """
    # pylint: disable=protected-access

    if not self._definitions_registry._format_definitions:
      raise RuntimeError(u'Missing format definition.')

    if len(self._definitions_registry._format_definitions) > 1:
      raise RuntimeError(u'Unsupported multiple format definitions.')

    return self._definitions_registry.GetDefinitionByName(
        self._definitions_registry._format_definitions[0])

  def _GetRuntimeStructureHeaderMembers(self, data_type_definition):
    """Generates the member definitions of a runtime structure header.

    Args:
      data_type_definition (DataTypeDefinition): structure data type definition.

    Returns:
      str: member definitions of the runtime structure header.

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

      if member_definition.description:
        description = member_definition.description
      else:
        description = name.replace(u'_', u' ')

      description = u'{0:s}{1:s}'.format(
          description[0].upper(), description[1:])

      data_type = getattr(member_definition, u'member_data_type', None)
      if data_type:
        lines.extend([
            u'\t/* {0:s}'.format(description),
            u'\t */',
            u'\t{1:s} {0:s};'.format(name, data_type)
        ])

      else:
        lines.append(u'\t/* TODO: {1:s} {0:s} */'.format(name, data_type))

      if index != last_index:
        lines.append(u'')

    return u'\n'.join(lines)

  def _GetRuntimeStructureSourceMembersCopyFromByteStream(
      self, data_type_definition):
    """Generates the member definitions of a runtime structure source.

    Args:
      data_type_definition (DataTypeDefinition): structure data type definition.

    Returns:
      str: member definitions of the runtime structure source.

    Raises:
      RuntimeError: if the size of the data type is not defined.
    """
    lines = []

    prefix = self._prefix or u''

    last_index = len(data_type_definition.members) - 1
    for index, member_definition in enumerate(data_type_definition.members):
      name = member_definition.name

      data_type_size = member_definition.GetByteSize()
      if not data_type_size:
        raise RuntimeError(
            u'Size of structure member: {0:s} not defined'.format(name))

      if member_definition.description:
        description = member_definition.description
      else:
        description = name.replace(u'_', u' ')

      description = u'{0:s}{1:s}'.format(
          description[0].upper(), description[1:])

      data_type = getattr(member_definition, u'member_data_type', None)
      if data_type:
        lines.extend([
            u'\tbyte_stream_copy_to_{0:s}_little_endian('.format(data_type),
            u'\t ( ({0:s}_{1:s}_t *) data )->{2:s},'.format(
                prefix, data_type_definition.name, name),
            u'\t {0:s}->{1:s} );'.format(data_type_definition.name, name)
        ])

      else:
        lines.append(u'\t/* TODO: {1:s} {0:s} */'.format(name, data_type))

      if index != last_index:
        lines.append(u'')

    return u'\n'.join(lines)

  def _GetRuntimeStructureSourceMembersDebugPrint(self, data_type_definition):
    """Generates the member definitions of a runtime structure source.

    Args:
      data_type_definition (DataTypeDefinition): structure data type definition.

    Returns:
      str: member definitions of the runtime structure source.

    Raises:
      RuntimeError: if the size of the data type is not defined.
    """
    lines = []

    prefix = self._prefix or u''

    last_index = len(data_type_definition.members) - 1
    for index, member_definition in enumerate(data_type_definition.members):
      name = member_definition.name

      data_type_size = member_definition.GetByteSize()
      if not data_type_size:
        raise RuntimeError(
            u'Size of structure member: {0:s} not defined'.format(name))

      if member_definition.description:
        description = member_definition.description
      else:
        description = name.replace(u'_', u' ')

      data_type = getattr(member_definition, u'member_data_type', None)
      if data_type:
        printf_format_indicator = u'%" PRIu32 "'
        # TODO: detemine number of tabs for alignment.
        lines.extend([
            u'\t\tlibcnotify_printf(',
            u'\t\t "%s: {0:s}\\t: {1:s}\\n",'.format(
                description, printf_format_indicator),
            u'\t\t function,',
            u'\t\t {0:s}->{1:s} );'.format(data_type_definition.name, name)
        ])

      else:
        lines.append(u'\t\t/* TODO: {1:s} {0:s} */'.format(name, data_type))

      if index != last_index:
        lines.append(u'')

    return u'\n'.join(lines)

  def _GetStoredStructureHeaderMembers(self, data_type_definition):
    """Generates the member definitions of a stored structure header.

    Args:
      data_type_definition (DataTypeDefinition): structure data type definition.

    Returns:
      str: member definitions of the stored structure header.

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

      if member_definition.description:
        description = member_definition.description
      else:
        description = name.replace(u'_', u' ')

      description = u'{0:s}{1:s}'.format(
          description[0].upper(), description[1:])

      if data_type_size == 1:
        lines.extend([
            u'\t/* {0:s}'.format(description),
            u'\t * Consists of {0:d} byte'.format(data_type_size),
            u'\t */',
            u'\tuint8_t {0:s};'.format(name)
        ])

      else:
        lines.extend([
            u'\t/* {0:s}'.format(description),
            u'\t * Consists of {0:d} bytes'.format(data_type_size),
            u'\t */',
            u'\tuint8_t {0:s}[ {1:d} ];'.format(name, data_type_size)
        ])

      if index != last_index:
        lines.append(u'')

    return u'\n'.join(lines)

  def _GetTemplateMappings(self):
    """Retrieves the template mappings.

    Returns:
      dict[str, str]: template mappings.
    """
    format_definition = self._GetFormatDefinitions()

    template_mappings = {}

    authors = format_definition.metadata.get(u'authors', None)
    if authors:
      template_mappings[u'authors'] = u', '.join(authors)

    year = format_definition.metadata.get(u'year', None)
    if year:
      date = datetime.date.today()
      if year != date.year:
        copyright_years = u'{0:d}-{1:d}'.format(year, date.year)
      else:
        copyright_years = u'{0:d}'.format(year)

      template_mappings[u'copyright'] = copyright_years

    prefix = self._prefix or u''

    template_mappings[u'prefix'] = prefix
    template_mappings[u'prefix_upper_case'] = prefix.upper()

    return template_mappings

  def Generate(self):
    """Generates source code from the data type definitions."""
    for data_type_definition in self._definitions_registry.GetDefinitions():
      if data_type_definition.TYPE_INDICATOR != (
          definitions.TYPE_INDICATOR_STRUCTURE):
        continue

      self._GenerateRuntimeStructureHeader(data_type_definition)
      self._GenerateRuntimeStructureSource(data_type_definition)
      self._GenerateStoredStructureHeader(data_type_definition)

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
      u'--templates-path', u'--templates_path', dest=u'templates_path',
      action=u'store', metavar=u'PATH', default=None, help=(
          u'Path to the template files.'))

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

  templates_path = options.templates_path
  if not templates_path:
    templates_path = os.path.dirname(__file__)
    templates_path = os.path.dirname(templates_path)
    templates_path = os.path.join(templates_path, u'data')

  source_generator = SourceGenerator(templates_path, prefix=options.prefix)

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
