# -*- coding: utf-8 -*-
"""The data type definition reader objects."""

import abc
import glob
import os
import yaml

from dtfabric import definitions
from dtfabric import errors


class DataTypeDefinitionsReader(object):
  """Data type definitions reader interface."""

  @abc.abstractmethod
  def ReadDefinitionFromDict(self, definitions_registry, definition_values):
    """Reads a data type definition from a dictionary.

    Args:
      definitions_registry (DataTypeDefinitionsRegistry): data type definitions
          registry.
      definition_values (dict[str, object]): definition values.

    Returns:
      DataTypeDefinition: data type definition or None.

    Raises:
      FormatError: if the definitions values are missing or if the format is
          incorrect.
    """


class DataTypeDefinitionsFileReader(DataTypeDefinitionsReader):
  """Data type definitions file reader interface."""

  _DATA_TYPE_CALLBACKS = {
      u'boolean': u'_ReadBooleanDataTypeDefinition',
      u'character': u'_ReadCharacterDataTypeDefinition',
      u'enumeration': u'_ReadEnumerationDataTypeDefinition',
      u'floating-point': u'_ReadFloatingPointDataTypeDefinition',
      u'integer': u'_ReadIntegerDataTypeDefinition',
      u'structure': u'_ReadStructureDataTypeDefinition',
      u'uuid': u'_ReadUUIDDataTypeDefinition',
  }

  def _ReadFixedSizeDataTypeDefinition(
      self, unused_definitions_registry, definition_values,
      data_type_definition_class, name):
    """Reads a fixed-size data type definition.

    Args:
      definitions_registry (DataTypeDefinitionsRegistry): data type definitions
          registry.
      definition_values (dict[str, object]): definition values.
      data_type_definition_class (str): data type definition class.
      name (str): name of the definition.

    Returns:
      FixedSizeDataTypeDefinition: fixed-size data type definition.

    Raises:
      FormatError: if the definitions values are missing or if the format is
          incorrect.
    """
    aliases = definition_values.get(u'aliases', None)
    description = definition_values.get(u'description', None)
    urls = definition_values.get(u'urls', None)

    definition_object = data_type_definition_class(
        name, aliases=aliases, description=description, urls=urls)

    attributes = definition_values.get(u'attributes')
    if attributes:
      definition_object.size = attributes.get(u'size', None)
      definition_object.units = attributes.get(u'units', u'bytes')

    return definition_object

  def _ReadBooleanDataTypeDefinition(
      self, definitions_registry, definition_values, name):
    """Reads a boolean data type definition.

    Args:
      definitions_registry (DataTypeDefinitionsRegistry): data type definitions
          registry.
      definition_values (dict[str, object]): definition values.
      name (str): name of the definition.

    Returns:
      BooleanDataTypeDefinition: boolean data type definition.
    """
    return self._ReadFixedSizeDataTypeDefinition(
        definitions_registry, definition_values,
        definitions.BooleanDefinition, name)

  def _ReadCharacterDataTypeDefinition(
      self, definitions_registry, definition_values, name):
    """Reads a character data type definition.

    Args:
      definitions_registry (DataTypeDefinitionsRegistry): data type definitions
          registry.
      definition_values (dict[str, object]): definition values.
      name (str): name of the definition.

    Returns:
      CharacterDataTypeDefinition: character data type definition.
    """
    return self._ReadFixedSizeDataTypeDefinition(
        definitions_registry, definition_values,
        definitions.CharacterDefinition, name)

  def _ReadEnumerationDataTypeDefinition(
      self, unused_definitions_registry, definition_values, name):
    """Reads an enumeration data type definition.

    Args:
      definitions_registry (DataTypeDefinitionsRegistry): data type definitions
          registry.
      definition_values (dict[str, object]): definition values.
      name (str): name of the definition.

    Returns:
      EnumerationDataTypeDefinition: enumeration data type definition.
    """
    aliases = definition_values.get(u'aliases', None)
    description = definition_values.get(u'description', None)
    urls = definition_values.get(u'urls', None)

    definition_object = definitions.EnumerationDefinition(
        name, aliases=aliases, description=description, urls=urls)

    # TODO: implement.

    return definition_object

  def _ReadFloatingPointDataTypeDefinition(
      self, definitions_registry, definition_values, name):
    """Reads a floating-point data type definition.

    Args:
      definitions_registry (DataTypeDefinitionsRegistry): data type definitions
          registry.
      definition_values (dict[str, object]): definition values.
      name (str): name of the definition.

    Returns:
      FloatingPointDefinition floating-point data type definition.
    """
    return self._ReadFixedSizeDataTypeDefinition(
        definitions_registry, definition_values,
        definitions.FloatingPointDefinition, name)

  def _ReadFormatDefinition(self, definition_values, name):
    """Reads a format definition.

    Args:
      definition_values (dict[str, object]): definition values.
      name (str): name of the definition.

    Returns:
      FormatDefinition: format definition.
    """
    description = definition_values.get(u'description', None)
    urls = definition_values.get(u'urls', None)

    definition_object = definitions.FormatDefinition(
        name, description=description, urls=urls)

    # TODO: implement.

    return definition_object

  def _ReadIntegerDataTypeDefinition(
      self, definitions_registry, definition_values, name):
    """Reads an integer data type definition.

    Args:
      definitions_registry (DataTypeDefinitionsRegistry): data type definitions
          registry.
      definition_values (dict[str, object]): definition values.
      name (str): name of the definition.

    Returns:
      IntegerDataTypeDefinition: integer data type definition.

    Raises:
      FormatError: if the definitions values are missing or if the format is
          incorrect.
    """
    definition_object = self._ReadFixedSizeDataTypeDefinition(
        definitions_registry, definition_values,
        definitions.IntegerDefinition, name)

    attributes = definition_values.get(u'attributes')
    if attributes:
      format_attribute = attributes.get(u'format', None)
      if format_attribute not in (u'signed', u'unsigned'):
        raise errors.FormatError(
            u'Unsupported format attribute: {0:s}'.format(format_attribute))

      definition_object.format = format_attribute

    return definition_object

  def _ReadStructureDataTypeDefinition(
      self, definitions_registry, definition_values, name):
    """Reads structure members definitions.

    Args:
      definitions_registry (DataTypeDefinitionsRegistry): data type definitions
          registry.
      definition_values (dict[str, object]): definition values.
      name (str): name of the definition.

    Returns:
      StructureDataTypeDefinition: structure data type definition.
    """
    aliases = definition_values.get(u'aliases', None)
    description = definition_values.get(u'description', None)
    urls = definition_values.get(u'urls', None)

    definition_object = definitions.StructureDataTypeDefinition(
        name, aliases=aliases, description=description, urls=urls)

    members = definition_values.get(u'members')
    if members:
      self._ReadStructureDataTypeDefinitionMembers(
          definitions_registry, members, definition_object)

    return definition_object

  def _ReadStructureDataTypeDefinitionMember(
      self, definitions_registry, definition_values):
    """Reads a structure data type definition member.

    Args:
      definitions_registry (DataTypeDefinitionsRegistry): data type definitions
          registry.
      definition_values (dict[str, object]): definition values.

    Returns:
      StructureMemberDefinition: structure attribute definition.

    Raises:
      FormatError: if the definitions values are missing or if the format is
          incorrect.
    """
    if not definition_values:
      raise errors.FormatError(u'Missing definition values.')

    name = definition_values.get(u'name', None)
    sequence = definition_values.get(u'sequence', None)
    union = definition_values.get(u'union', None)

    if not name and not sequence and not union:
      raise errors.FormatError(
          u'Invalid structure attribute definition missing name, sequence or '
          u'union.')

    if sequence:
      sequence_name = sequence.get(u'name', None)
      aliases = sequence.get(u'aliases', None)
      data_type = sequence.get(u'data_type', None)
      description = sequence.get(u'description', None)

      definition_object = definitions.SequenceStructureMemberDefinition(
          sequence_name, aliases=aliases, data_type=data_type,
          description=description)

    elif union:
      union_name = union.get(u'name', None)
      aliases = union.get(u'aliases', None)
      description = union.get(u'description', None)

      definition_object = definitions.UnionStructureMemberDefinition(
          union_name, aliases=aliases, description=description)

    else:
      aliases = definition_values.get(u'aliases', None)
      data_type = definition_values.get(u'data_type', None)
      description = definition_values.get(u'description', None)

      data_type_definition = definitions_registry.GetDefinitionByName(data_type)
      if not data_type_definition:
        raise errors.FormatError(
            u'Undefined data type: {0:s}.'.format(data_type))

      definition_object = definitions.StructureMemberDefinition(
          data_type_definition, name, aliases=aliases, data_type=data_type,
          description=description)

    return definition_object

  def _ReadStructureDataTypeDefinitionMembers(
      self, definitions_registry, definition_values, definition_object):
    """Reads structure data type definition members.

    Args:
      definitions_registry (DataTypeDefinitionsRegistry): data type definitions
          registry.
      definition_values (dict[str, object]): definition values.
      definition_object (DataTypeDefinition): data type definition.
    """
    for attribute in definition_values:
      structure_attribute = self._ReadStructureDataTypeDefinitionMember(
          definitions_registry, attribute)
      definition_object.members.append(structure_attribute)

  def _ReadUUIDDataTypeDefinition(
      self, definitions_registry, definition_values, name):
    """Reads an UUID data type definition.

    Args:
      definitions_registry (DataTypeDefinitionsRegistry): data type definitions
          registry.
      definition_values (dict[str, object]): definition values.
      name (str): name of the definition.

    Returns:
      UUIDDataTypeDefinition: UUID data type definition.
    """
    return self._ReadFixedSizeDataTypeDefinition(
        definitions_registry, definition_values,
        definitions.UUIDDefinition, name)

  def ReadDefinitionFromDict(self, definitions_registry, definition_values):
    """Reads a data type definition from a dictionary.

    Args:
      definitions_registry (DataTypeDefinitionsRegistry): data type definitions
          registry.
      definition_values (dict[str, object]): definition values.

    Returns:
      DataTypeDefinition: data type definition or None.

    Raises:
      FormatError: if the definitions values are missing or if the format is
          incorrect.
    """
    if not definition_values:
      raise errors.FormatError(u'Missing definition values.')

    name = definition_values.get(u'name', None)
    if not name:
      raise errors.FormatError(u'Invalid definition missing name.')

    type_indicator = definition_values.get(u'type', None)
    if not type_indicator:
      raise errors.FormatError(u'Invalid definition missing type.')

    if type_indicator == u'format':
      return self._ReadFormatDefinition(definition_values, name)

    data_type_callback = self._DATA_TYPE_CALLBACKS.get(type_indicator, None)
    if data_type_callback:
      data_type_callback = getattr(self, data_type_callback, None)
    if not data_type_callback:
      raise errors.FormatError(
          u'Unuspported data type definition: {0:s}.'.format(type_indicator))

    return data_type_callback(definitions_registry, definition_values, name)

  def ReadDirectory(self, definitions_registry, path, extension=None):
    """Reads data type definitions from a directory.

    This function does not recurse sub directories into the registry.

    Args:
      definitions_registry (DataTypeDefinitionsRegistry): data type definitions
          registry.
      path (str): path of the directory to read from.
      extension (Optional[str]): extension of the filenames to read.
    """
    if extension:
      glob_spec = os.path.join(path, u'*.{0:s}'.format(extension))
    else:
      glob_spec = os.path.join(path, u'*')

    for definition_file in glob.glob(glob_spec):
      self.ReadFile(definitions_registry, definition_file)

  def ReadFile(self, definitions_registry, path):
    """Reads data type definitions from a file into the registry.

    Args:
      definitions_registry (DataTypeDefinitionsRegistry): data type definitions
          registry.
      path (str): path of the file to read from.
    """
    with open(path, 'r') as file_object:
      self.ReadFileObject(definitions_registry, file_object)

  @abc.abstractmethod
  def ReadFileObject(self, definitions_registry, file_object):
    """Reads data type definitions from a file-like object into the registry.

    Args:
      definitions_registry (DataTypeDefinitionsRegistry): data type definitions
          registry.
      file_object (file): file-like object to read from.
    """


class YAMLDataTypeDefinitionsFileReader(DataTypeDefinitionsFileReader):
  """YAML data type definitions file reader."""

  def ReadDirectory(self, definitions_registry, path, extension=u'yaml'):
    """Reads data type definitions from a directory.

    This function does not recurse sub directories into the registry.

    Args:
      definitions_registry (DataTypeDefinitionsRegistry): data type definitions
          registry.
      path (str): path of the directory to read from.
      extension (Optional[str]): extension of the filenames to read.
    """
    super(YAMLDataTypeDefinitionsFileReader, self).ReadDirectory(
        definitions_registry, path, extension=extension)

  def ReadFileObject(self, definitions_registry, file_object):
    """Reads data type definitions from a file-like object into the registry.

    Args:
      definitions_registry (DataTypeDefinitionsRegistry): data type definitions
          registry.
      file_object (file): file-like object to read from.

    Raises:
      FormatError: if the definitions values are missing or if the format is
          incorrect.
    """
    yaml_generator = yaml.safe_load_all(file_object)

    last_definition_object = None
    error_message = None
    for yaml_definition in yaml_generator:
      try:
        definition_object = self.ReadDefinitionFromDict(
            definitions_registry, yaml_definition)

      except errors.FormatError as exception:
        definition_object = None
        error_message = u'{0!s}'.format(exception)

      if not definition_object:
        if last_definition_object:
          error_location = u'After: {0:s}'.format(last_definition_object.name)
        else:
          error_location = u'At start'

        if not error_message:
          error_message = u'Missing definition object.'

        error_message = u'{0:s}: {1:s}'.format(error_location, error_message)

        raise errors.FormatError(error_message)

      definitions_registry.RegisterDefinition(definition_object)
      last_definition_object = definition_object
