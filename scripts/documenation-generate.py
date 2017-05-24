#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Script to generate documenation based on dtFabric format definitions."""

from __future__ import print_function
import argparse
import logging
import os
import sys

from dtfabric import errors
from dtfabric import reader
from dtfabric import registry
from dtfabric.generators import output_writers
from dtfabric.generators import template_string


class AsciidocFormatDocumentGenerator(object):
  """Asciidoc format document generator."""

  _APPENDICES_TEMPLATE_FILE = u'appendices.asciidoc'
  _BODY_TEMPLATE_FILE = u'body.asciidoc'
  _PROLOGUE_TEMPLATE_FILE = u'prologue.asciidoc'

  def __init__(self, templates_path):
    """Initializes a generator.

    Args:
      templates_path (str): templates path.
    """
    super(AsciidocFormatDocumentGenerator, self).__init__()
    self._definitions_registry = registry.DataTypeDefinitionsRegistry()
    self._templates_path = templates_path
    self._template_string_generator = template_string.TemplateStringGenerator()

  def _GenerateAppendices(self, output_writer):
    """Generates appendices.

    Args:
      output_writer (OutputWriter): output writer.
    """
    template_mappings = {}

    template_filename = os.path.join(
        self._templates_path, self._APPENDICES_TEMPLATE_FILE)

    self._template_string_generator.Generate(
        template_filename, template_mappings, output_writer)

    # TODO: generate references
    # TODO: generate GFDL

  def _GenerateBody(self, output_writer):
    """Generates a body.

    Args:
      output_writer (OutputWriter): output writer.
    """
    template_mappings = {}

    template_filename = os.path.join(
        self._templates_path, self._BODY_TEMPLATE_FILE)

    self._template_string_generator.Generate(
        template_filename, template_mappings, output_writer)

    # TODO: generate overview
    # TODO: generate chapter per structure

  def _GeneratePrologue(self, output_writer):
    """Generates a prologue.

    Args:
      output_writer (OutputWriter): output writer.
    """
    template_mappings = {
        u'abstract': u'',
        u'authors': u'',
        u'copyright': u'',
        u'keywords': u'',
        u'subtitle': u'',
        u'summary': u'',
        u'title': u''}

    template_filename = os.path.join(
        self._templates_path, self._PROLOGUE_TEMPLATE_FILE)

    self._template_string_generator.Generate(
        template_filename, template_mappings, output_writer)

  def Generate(self):
    """Generates a format document."""
    output_writer = output_writers.StdoutWriter()

    self._GeneratePrologue(output_writer)
    self._GenerateBody(output_writer)
    self._GenerateAppendices(output_writer)

  def ReadDefinitions(self, path):
    """Reads the definitions form file or directory.

    Args:
      path (str): path of the definition file.
    """
    definitions_reader = reader.YAMLDataTypeDefinitionsFileReader()
    definitions_reader.ReadFile(self._definitions_registry, path)


def Main():
  """The main program function.

  Returns:
    bool: True if successful or False if not.
  """
  argument_parser = argparse.ArgumentParser(description=(
      u'Generates documentation based on dtFabric format definitions.'))

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
  templates_path = os.path.join(u'data', u'templates')

  source_generator = AsciidocFormatDocumentGenerator(templates_path)

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
