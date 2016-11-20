# -*- coding: utf-8 -*-
"""The definition reader objects."""

import abc
import glob
import os
import yaml

from dtfabric import definitions
from dtfabric import errors


class BaseDefinitionsReader(object):
  """Class that defines the definitions reader interface."""

  @abc.abstractmethod
  def ReadDefinitionFromDict(self, definition_values):
    """Reads a structure or type definition from a dictionary.

    Args:
      definition_values (dict[str, object]): definition values.

    Returns:
      BaseDefinition: structure or type definition.

    Raises:
      FormatError: if the definitions values are missing or if the format is
          incorrect.
    """

class BaseDefinitionsFileReader(BaseDefinitionsReader):
  """Class that defines the definitions file reader interface."""

  def _ReadStructureAttribute(self, definition_values):
    """Reads a structure definition attribute.

    Args:
      definition_values (dict[str, object]): definition values.
      definition_object (BaseDefinition): structure or type definition.
      name (str): name of the definition.

    Returns:
      StructureAttributeDefinition: structure attribute definition.

    Raises:
      FormatError: if the definitions values are missing or if the format is
          incorrect.
    """
    if not definition_values:
      raise errors.FormatError(u'Missing definition values.')

    name = definition_values.get(u'name', None)
    if not name:
      raise errors.FormatError(
          u'Invalid structure attribute definition missing name.')

    aliases = definition_values.get(u'aliases', None)
    data_type = definition_values.get(u'data_type', None)
    description = definition_values.get(u'description', None)

    return definitions.StructureAttributeDefinition(
        name, aliases=aliases, data_type=data_type, description=description)

  def _ReadStructureAttributes(
      self, definition_values, definition_object, name):
    """Reads structure definition attributes.

    Args:
      definition_values (dict[str, object]): definition values.
      definition_object (BaseDefinition): structure or type definition.
      name (str): name of the definition.

    Raises:
      FormatError: if the definitions values are missing or if the format is
          incorrect.
    """
    attributes = definition_values.get(u'attributes')
    if not attributes:
      raise errors.FormatError(
          u'Invalid structure definition: {0:s} missing attributes.'.format(
              name))

    for attribute in attributes:
      structure_attribute = self._ReadStructureAttribute(attribute)
      definition_object.attributes.append(structure_attribute)

  def ReadDefinitionFromDict(self, definition_values):
    """Reads a structure or type definition from a dictionary.

    Args:
      definition_values (dict[str, object]): definition values.

    Returns:
      BaseDefinition: structure or type definition.

    Raises:
      FormatError: if the definitions values are missing or if the format is
          incorrect.
    """
    if not definition_values:
      raise errors.FormatError(u'Missing definition values.')

    name = definition_values.get(u'name', None)
    if not name:
      raise errors.FormatError(u'Invalid structure definition missing name.')

    description = definition_values.get(u'description', None)
    if not description:
      raise errors.FormatError(
          u'Invalid structure definition: {0:s} missing description.'.format(
              name))

    aliases = definition_values.get(u'aliases', None)
    byte_order = definition_values.get(u'byte_order', None)
    description = definition_values.get(u'description', None)

    definition_object = definitions.StructureDefinition(
        name, aliases=aliases, byte_order=byte_order, description=description)

    self._ReadStructureAttributes(definition_values, definition_object, name)

    return definition_object

  def ReadDirectory(self, path, extension=None):
    """Reads structure definitions from a directory.

    This function does not recurse sub directories.

    Args:
      path (str): path of the directory to read from.
      extension (Optional[str]): extension of the filenames to read.

    Yields:
      BaseDefinition: structure or type definition.
    """
    if extension:
      glob_spec = os.path.join(path, u'*.{0:s}'.format(extension))
    else:
      glob_spec = os.path.join(path, u'*')

    for definition_file in glob.glob(glob_spec):
      for definition_object in self.ReadFile(definition_file):
        yield definition_object

  def ReadFile(self, path):
    """Reads structure definitions from a file.

    Args:
      path (str): path of the file to read from.

    Yields:
      BaseDefinition: structure or type definition.
    """
    with open(path, 'r') as file_object:
      for definition_object in self.ReadFileObject(file_object):
        yield definition_object

  @abc.abstractmethod
  def ReadFileObject(self, file_object):
    """Reads structure definitions from a file-like object.

    Args:
      file_object (file): file-like object to read from.

    Yields:
      BaseDefinition: structure or type definition.
    """


class YAMLDefinitionsFileReader(BaseDefinitionsFileReader):
  """Class that implements the YAML definitions file reader."""

  def ReadFileObject(self, file_object):
    """Reads structure definitions from a file-like object.

    Args:
      file_object (file): file-like object to read from.

    Yields:
      BaseDefinition: structure or type definition.
    """
    yaml_generator = yaml.safe_load_all(file_object)

    last_definition_object = None
    for yaml_definition in yaml_generator:
      try:
        definition_object = self.ReadDefinitionFromDict(yaml_definition)

      except errors.FormatError as exception:
        if last_definition_object:
          error_location = u'After: {0:s}'.format(last_definition_object.name)
        else:
          error_location = u'At start'

        raise errors.FormatError(u'{0:s} {1:s}'.format(
            error_location, exception))

      yield definition_object
      last_definition_object = definition_object
