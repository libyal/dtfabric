# -*- coding: utf-8 -*-
"""The data type definition reader objects."""

import abc
import glob
import os
import yaml

from dtfabric import data_types
from dtfabric import definitions
from dtfabric import errors


# TODO: complete _ReadFormatDefinition


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
      DefinitionReaderError: if the definitions values are missing or if
          the format is incorrect.
    """


class DataTypeDefinitionsFileReader(DataTypeDefinitionsReader):
  """Data type definitions file reader interface."""

  _DATA_TYPE_CALLBACKS = {
      definitions.TYPE_INDICATOR_BOOLEAN: u'_ReadBooleanDataTypeDefinition',
      definitions.TYPE_INDICATOR_CHARACTER: u'_ReadCharacterDataTypeDefinition',
      definitions.TYPE_INDICATOR_CONSTANT: u'_ReadConstantDataTypeDefinition',
      definitions.TYPE_INDICATOR_ENUMERATION: (
          u'_ReadEnumerationDataTypeDefinition'),
      definitions.TYPE_INDICATOR_FLOATING_POINT: (
          u'_ReadFloatingPointDataTypeDefinition'),
      definitions.TYPE_INDICATOR_INTEGER: u'_ReadIntegerDataTypeDefinition',
      definitions.TYPE_INDICATOR_SEQUENCE: u'_ReadSequenceDataTypeDefinition',
      definitions.TYPE_INDICATOR_STREAM: u'_ReadStreamDataTypeDefinition',
      definitions.TYPE_INDICATOR_STRING: u'_ReadStringDataTypeDefinition',
      definitions.TYPE_INDICATOR_STRUCTURE: u'_ReadStructureDataTypeDefinition',
      definitions.TYPE_INDICATOR_UUID: u'_ReadUUIDDataTypeDefinition',
  }

  _INTEGER_FORMAT_ATTRIBUTES = frozenset([
      definitions.FORMAT_SIGNED,
      definitions.FORMAT_UNSIGNED])

  def _ReadBooleanDataTypeDefinition(
      self, definitions_registry, definition_values, definition_name):
    """Reads a boolean data type definition.

    Args:
      definitions_registry (DataTypeDefinitionsRegistry): data type definitions
          registry.
      definition_values (dict[str, object]): definition values.
      definition_name (str): name of the definition.

    Returns:
      BooleanDataTypeDefinition: boolean data type definition.
    """
    return self._ReadFixedSizeDataTypeDefinition(
        definitions_registry, definition_values,
        data_types.BooleanDefinition, definition_name)

  def _ReadCharacterDataTypeDefinition(
      self, definitions_registry, definition_values, definition_name):
    """Reads a character data type definition.

    Args:
      definitions_registry (DataTypeDefinitionsRegistry): data type definitions
          registry.
      definition_values (dict[str, object]): definition values.
      definition_name (str): name of the definition.

    Returns:
      CharacterDataTypeDefinition: character data type definition.
    """
    return self._ReadFixedSizeDataTypeDefinition(
        definitions_registry, definition_values,
        data_types.CharacterDefinition, definition_name)

  def _ReadConstantDataTypeDefinition(
      self, unused_definitions_registry, definition_values, definition_name):
    """Reads a constant data type definition.

    Args:
      definitions_registry (DataTypeDefinitionsRegistry): data type definitions
          registry.
      definition_values (dict[str, object]): definition values.
      definition_name (str): name of the definition.

    Returns:
      ConstantDataTypeDefinition: constant data type definition.

    Raises:
      DefinitionReaderError: if the definitions values are missing or if
          the format is incorrect.
    """
    value = definition_values.get(u'value', None)
    if value is None:
      error_message = u'missing value'
      raise errors.DefinitionReaderError(definition_name, error_message)

    aliases = definition_values.get(u'aliases', None)
    description = definition_values.get(u'description', None)
    urls = definition_values.get(u'urls', None)

    definition_object = data_types.ConstantDefinition(
        definition_name, aliases=aliases, description=description, urls=urls)
    definition_object.value = value

    return definition_object

  def _ReadEnumerationDataTypeDefinition(
      self, definitions_registry, definition_values, definition_name):
    """Reads an enumeration data type definition.

    Args:
      definitions_registry (DataTypeDefinitionsRegistry): data type definitions
          registry.
      definition_values (dict[str, object]): definition values.
      definition_name (str): name of the definition.

    Returns:
      EnumerationDataTypeDefinition: enumeration data type definition.

    Raises:
      DefinitionReaderError: if the definitions values are missing or if
          the format is incorrect.
    """
    values = definition_values.get(u'values')
    if not values:
      error_message = u'missing values'
      raise errors.DefinitionReaderError(definition_name, error_message)

    definition_object = self._ReadFixedSizeDataTypeDefinition(
        definitions_registry, definition_values,
        data_types.EnumerationDefinition, definition_name)

    last_name = None
    for enumeration_value in values:
      aliases = enumeration_value.get(u'aliases', None)
      description = enumeration_value.get(u'description', None)
      name = enumeration_value.get(u'name', None)
      value = enumeration_value.get(u'value', None)

      if not name or value is None:
        if last_name:
          error_location = u'after: {0:s}'.format(last_name)
        else:
          error_location = u'at start'

        error_message = u'{0:s} missing name or value'.format(error_location)
        raise errors.DefinitionReaderError(definition_name, error_message)

      else:
        try:
          definition_object.AddValue(
              name, value, aliases=aliases, description=description)
        except KeyError:
          error_message = u'value: {0:s} already exists'.format(name)
          raise errors.DefinitionReaderError(definition_name, error_message)

      last_name = name

    return definition_object

  def _ReadElementSequenceDataTypeDefinition(
      self, definitions_registry, definition_values,
      data_type_definition_class, definition_name):
    """Reads an element sequence data type definition.

    Args:
      definitions_registry (DataTypeDefinitionsRegistry): data type definitions
          registry.
      definition_values (dict[str, object]): definition values.
      data_type_definition_class (str): data type definition class.
      definition_name (str): name of the definition.

    Returns:
      SequenceDefinition: sequence data type definition.

    Raises:
      DefinitionReaderError: if the definitions values are missing or if
          the format is incorrect.
    """
    attributes = definition_values.get(u'attributes')
    if attributes:
      error_message = u'attributes not supported by element sequence data type'
      raise errors.DefinitionReaderError(definition_name, error_message)

    element_data_type = definition_values.get(u'element_data_type', None)
    if not element_data_type:
      error_message = u'missing element data type'
      raise errors.DefinitionReaderError(definition_name, error_message)

    elements_data_size = definition_values.get(u'elements_data_size', None)
    elements_terminator = definition_values.get(u'elements_terminator', None)
    number_of_elements = definition_values.get(u'number_of_elements', None)

    size_values = filter(lambda value: value is not None, (
        elements_data_size, elements_terminator, number_of_elements))

    if not size_values:
      error_message = (
          u'missing element data size, elements terminator and number of '
          u'elements')
      raise errors.DefinitionReaderError(definition_name, error_message)

    if len(size_values) > 1:
      error_message = (
          u'element data size, elements terminator and number of elements '
          u'not allowed to be set at the same time')
      raise errors.DefinitionReaderError(definition_name, error_message)

    element_data_type_definition = definitions_registry.GetDefinitionByName(
        element_data_type)
    if not element_data_type_definition:
      error_message = u'undefined element data type: {0:s}.'.format(
          element_data_type)
      raise errors.DefinitionReaderError(definition_name, error_message)

    aliases = definition_values.get(u'aliases', None)
    description = definition_values.get(u'description', None)
    urls = definition_values.get(u'urls', None)

    definition_object = data_type_definition_class(
        definition_name, element_data_type_definition, aliases=aliases,
        data_type=element_data_type, description=description, urls=urls)

    if elements_data_size is not None:
      try:
        definition_object.elements_data_size = int(elements_data_size)
      except ValueError:
        definition_object.elements_data_size_expression = elements_data_size

    elif elements_terminator is not None:
      definition_object.elements_terminator = elements_terminator

    elif number_of_elements is not None:
      try:
        definition_object.number_of_elements = int(number_of_elements)
      except ValueError:
        definition_object.number_of_elements_expression = number_of_elements

    return definition_object

  def _ReadFixedSizeDataTypeDefinition(
      self, unused_definitions_registry, definition_values,
      data_type_definition_class, definition_name, default_size=None,
      default_units=u'bytes'):
    """Reads a fixed-size data type definition.

    Args:
      definitions_registry (DataTypeDefinitionsRegistry): data type definitions
          registry.
      definition_values (dict[str, object]): definition values.
      data_type_definition_class (str): data type definition class.
      definition_name (str): name of the definition.
      default_size (Optional[int]): default size.
      default_units (Optional[str]): default units.

    Returns:
      FixedSizeDataTypeDefinition: fixed-size data type definition.

    Raises:
      DefinitionReaderError: if the definitions values are missing or if
          the format is incorrect.
    """
    aliases = definition_values.get(u'aliases', None)
    description = definition_values.get(u'description', None)
    urls = definition_values.get(u'urls', None)

    definition_object = data_type_definition_class(
        definition_name, aliases=aliases, description=description, urls=urls)

    attributes = definition_values.get(u'attributes')
    if attributes:
      byte_order = attributes.get(u'byte_order', definitions.BYTE_ORDER_NATIVE)
      if byte_order not in definitions.BYTE_ORDERS:
        error_message = u'unsupported byte-order attribute: {0!s}'.format(
            byte_order)
        raise errors.DefinitionReaderError(definition_name, error_message)

      size = attributes.get(u'size', default_size)
      try:
        int(size)
      except ValueError:
        error_message = u'unuspported size attribute: {0!s}'.format(size)
        raise errors.DefinitionReaderError(definition_name, error_message)

      definition_object.byte_order = byte_order
      definition_object.size = size
      definition_object.units = attributes.get(u'units', default_units)

    return definition_object

  def _ReadFloatingPointDataTypeDefinition(
      self, definitions_registry, definition_values, definition_name):
    """Reads a floating-point data type definition.

    Args:
      definitions_registry (DataTypeDefinitionsRegistry): data type definitions
          registry.
      definition_values (dict[str, object]): definition values.
      definition_name (str): name of the definition.

    Returns:
      FloatingPointDefinition floating-point data type definition.
    """
    return self._ReadFixedSizeDataTypeDefinition(
        definitions_registry, definition_values,
        data_types.FloatingPointDefinition, definition_name)

  def _ReadFormatDefinition(self, definition_values, definition_name):
    """Reads a format definition.

    Args:
      definition_values (dict[str, object]): definition values.
      definition_name (str): name of the definition.

    Returns:
      FormatDefinition: format definition.
    """
    description = definition_values.get(u'description', None)
    urls = definition_values.get(u'urls', None)

    definition_object = data_types.FormatDefinition(
        definition_name, description=description, urls=urls)

    # TODO: implement.

    return definition_object

  def _ReadIntegerDataTypeDefinition(
      self, definitions_registry, definition_values, definition_name):
    """Reads an integer data type definition.

    Args:
      definitions_registry (DataTypeDefinitionsRegistry): data type definitions
          registry.
      definition_values (dict[str, object]): definition values.
      definition_name (str): name of the definition.

    Returns:
      IntegerDataTypeDefinition: integer data type definition.

    Raises:
      DefinitionReaderError: if the definitions values are missing or if
          the format is incorrect.
    """
    definition_object = self._ReadFixedSizeDataTypeDefinition(
        definitions_registry, definition_values,
        data_types.IntegerDefinition, definition_name)

    attributes = definition_values.get(u'attributes')
    if attributes:
      format_attribute = attributes.get(u'format', definitions.FORMAT_SIGNED)
      if format_attribute not in self._INTEGER_FORMAT_ATTRIBUTES:
        error_message = u'unsupported format attribute: {0!s}'.format(
            format_attribute)
        raise errors.DefinitionReaderError(definition_name, error_message)

      definition_object.format = format_attribute

    return definition_object

  def _ReadSequenceDataTypeDefinition(
      self, definitions_registry, definition_values, definition_name):
    """Reads a sequence data type definition.

    Args:
      definitions_registry (DataTypeDefinitionsRegistry): data type definitions
          registry.
      definition_values (dict[str, object]): definition values.
      definition_name (str): name of the definition.

    Returns:
      SequenceDefinition: sequence data type definition.

    Raises:
      DefinitionReaderError: if the definitions values are missing or if
          the format is incorrect.
    """
    return self._ReadElementSequenceDataTypeDefinition(
        definitions_registry, definition_values, data_types.SequenceDefinition,
        definition_name)

  def _ReadStreamDataTypeDefinition(
      self, definitions_registry, definition_values, definition_name):
    """Reads a stream data type definition.

    Args:
      definitions_registry (DataTypeDefinitionsRegistry): data type definitions
          registry.
      definition_values (dict[str, object]): definition values.
      definition_name (str): name of the definition.

    Returns:
      StreamDefinition: stream data type definition.

    Raises:
      DefinitionReaderError: if the definitions values are missing or if
          the format is incorrect.
    """
    return self._ReadElementSequenceDataTypeDefinition(
        definitions_registry, definition_values, data_types.StreamDefinition,
        definition_name)

  def _ReadStringDataTypeDefinition(
      self, definitions_registry, definition_values, definition_name):
    """Reads a string data type definition.

    Args:
      definitions_registry (DataTypeDefinitionsRegistry): data type definitions
          registry.
      definition_values (dict[str, object]): definition values.
      definition_name (str): name of the definition.

    Returns:
      StringDefinition: string data type definition.

    Raises:
      DefinitionReaderError: if the definitions values are missing or if
          the format is incorrect.
    """
    encoding = definition_values.get(u'encoding', None)
    if not encoding:
      error_message = u'missing encoding'
      raise errors.DefinitionReaderError(definition_name, error_message)

    definition_object = self._ReadElementSequenceDataTypeDefinition(
        definitions_registry, definition_values, data_types.StringDefinition,
        definition_name)
    definition_object.encoding = encoding

    return definition_object

  def _ReadStructureDataTypeDefinition(
      self, definitions_registry, definition_values, definition_name):
    """Reads a structure data type definition.

    Args:
      definitions_registry (DataTypeDefinitionsRegistry): data type definitions
          registry.
      definition_values (dict[str, object]): definition values.
      definition_name (str): name of the definition.

    Returns:
      StructureDefinition: structure data type definition.

    Raises:
      DefinitionReaderError: if the definitions values are missing or if
          the format is incorrect.
    """
    members = definition_values.get(u'members', None)
    if not members:
      error_message = u'missing members'
      raise errors.DefinitionReaderError(definition_name, error_message)

    aliases = definition_values.get(u'aliases', None)
    description = definition_values.get(u'description', None)
    urls = definition_values.get(u'urls', None)

    definition_object = data_types.StructureDefinition(
        definition_name, aliases=aliases, description=description, urls=urls)

    attributes = definition_values.get(u'attributes')
    if attributes:
      byte_order = attributes.get(u'byte_order', definitions.BYTE_ORDER_NATIVE)
      if byte_order not in definitions.BYTE_ORDERS:
        error_message = u'unsupported byte-order attribute: {0!s}'.format(
            byte_order)
        raise errors.DefinitionReaderError(definition_name, error_message)

      definition_object.byte_order = byte_order

    self._ReadStructureDataTypeDefinitionMembers(
        definitions_registry, members, definition_object)

    return definition_object

  def _ReadStructureDataTypeDefinitionMember(
      self, definitions_registry, definition_values, definition_name):
    """Reads a structure data type definition member.

    Args:
      definitions_registry (DataTypeDefinitionsRegistry): data type definitions
          registry.
      definition_values (dict[str, object]): definition values.
      definition_name (str): name of the definition.

    Returns:
      DataTypeDefinition: structure member data type definition.

    Raises:
      DefinitionReaderError: if the definitions values are missing or if
          the format is incorrect.
    """
    name = definition_values.get(u'name', None)
    if not name:
      error_message = u'invalid structure member missing name'
      raise errors.DefinitionReaderError(definition_name, error_message)

    if not definition_values:
      error_message = (
          u'invalid structure member: {0:s} missing definition values').format(
              name)
      raise errors.DefinitionReaderError(definition_name, error_message)

    data_type = definition_values.get(u'data_type', None)
    type_indicator = definition_values.get(u'type', None)

    type_values = filter(lambda value: value is not None, (
        data_type, type_indicator))

    if not type_values:
      error_message = (
          u'invalid structure member: {0:s} both data type and type are '
          u'missing').format(name)
      raise errors.DefinitionReaderError(definition_name, error_message)

    if len(type_values) > 1:
      error_message = (
          u'invalid structure member: {0:s} data type and type not allowed to '
          u'be set at the same time').format(name)
      raise errors.DefinitionReaderError(definition_name, error_message)

    if type_indicator is not None:
      definition_object = self.ReadDefinitionFromDict(
          definitions_registry, definition_values)

    if data_type is not None:
      data_type_definition = definitions_registry.GetDefinitionByName(
          data_type)
      if not data_type_definition:
        error_message = (
            u'invalid structure member: {0:s} undefined data type: '
            u'{1:s}').format(name, data_type)
        raise errors.DefinitionReaderError(definition_name, error_message)

      aliases = definition_values.get(u'aliases', None)
      description = definition_values.get(u'description', None)

      definition_object = data_types.StructureMemberDefinition(
          name, data_type_definition, aliases=aliases, data_type=data_type,
          description=description)

    return definition_object

  def _ReadStructureDataTypeDefinitionMembers(
      self, definitions_registry, definition_values, data_type_definition):
    """Reads structure data type definition members.

    Args:
      definitions_registry (DataTypeDefinitionsRegistry): data type definitions
          registry.
      definition_values (dict[str, object]): definition values.
      data_type_definition (DataTypeDefinition): data type definition.
    """
    for member in definition_values:
      structure_member = self._ReadStructureDataTypeDefinitionMember(
          definitions_registry, member, data_type_definition.name)
      data_type_definition.members.append(structure_member)

  def _ReadUUIDDataTypeDefinition(
      self, definitions_registry, definition_values, definition_name):
    """Reads an UUID data type definition.

    Args:
      definitions_registry (DataTypeDefinitionsRegistry): data type definitions
          registry.
      definition_values (dict[str, object]): definition values.
      definition_name (str): name of the definition.

    Returns:
      UUIDDataTypeDefinition: UUID data type definition.

    Raises:
      DefinitionReaderError: if the definitions values are missing or if
          the format is incorrect.
    """
    definition_object = self._ReadFixedSizeDataTypeDefinition(
        definitions_registry, definition_values,
        data_types.UUIDDefinition, definition_name, default_size=16)

    if definition_object.size != 16:
      error_message = u'unsupported size: {0:d}.'.format(definition_object.size)
      raise errors.DefinitionReaderError(definition_name, error_message)

    return definition_object

  def ReadDefinitionFromDict(self, definitions_registry, definition_values):
    """Reads a data type definition from a dictionary.

    Args:
      definitions_registry (DataTypeDefinitionsRegistry): data type definitions
          registry.
      definition_values (dict[str, object]): definition values.

    Returns:
      DataTypeDefinition: data type definition or None.

    Raises:
      DefinitionReaderError: if the definitions values are missing or if
          the format is incorrect.
    """
    if not definition_values:
      error_message = u'missing definition values'
      raise errors.DefinitionReaderError(None, error_message)

    name = definition_values.get(u'name', None)
    if not name:
      error_message = u'missing name'
      raise errors.DefinitionReaderError(None, error_message)

    type_indicator = definition_values.get(u'type', None)
    if not type_indicator:
      error_message = u'invalid definition missing type'
      raise errors.DefinitionReaderError(name, error_message)

    if type_indicator == u'format':
      return self._ReadFormatDefinition(definition_values, name)

    data_type_callback = self._DATA_TYPE_CALLBACKS.get(type_indicator, None)
    if data_type_callback:
      data_type_callback = getattr(self, data_type_callback, None)
    if not data_type_callback:
      error_message = u'unuspported data type definition: {0:s}.'.format(
          type_indicator)
      raise errors.DefinitionReaderError(name, error_message)

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
    error_location = None
    error_message = None
    for yaml_definition in yaml_generator:
      try:
        definition_object = self.ReadDefinitionFromDict(
            definitions_registry, yaml_definition)

      except errors.DefinitionReaderError as exception:
        definition_object = None
        if exception.name:
          error_location = u'In: {0:s}'.format(exception.name)
        error_message = u''.join(exception.message)

      if not definition_object:
        if not error_location:
          name = yaml_definition.get(u'name', None)
          if name:
            error_location = u'In: {0:s}'.format(name)
          elif last_definition_object:
            error_location = u'After: {0:s}'.format(last_definition_object.name)
          else:
            error_location = u'At start'

        if not error_message:
          error_message = u'Missing definition object.'

        error_message = u'{0:s} {1:s}'.format(error_location, error_message)
        raise errors.FormatError(error_message)

      definitions_registry.RegisterDefinition(definition_object)
      last_definition_object = definition_object
