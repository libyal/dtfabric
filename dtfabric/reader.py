# -*- coding: utf-8 -*-
"""The data type definition reader objects."""

import abc
import yaml

from dtfabric import data_types
from dtfabric import definitions
from dtfabric import errors


class DataTypeDefinitionsReader(object):
  """Data type definitions reader."""

  _DATA_TYPE_CALLBACKS = {
      definitions.TYPE_INDICATOR_BOOLEAN: u'_ReadBooleanDataTypeDefinition',
      definitions.TYPE_INDICATOR_CHARACTER: u'_ReadCharacterDataTypeDefinition',
      definitions.TYPE_INDICATOR_CONSTANT: u'_ReadConstantDataTypeDefinition',
      definitions.TYPE_INDICATOR_ENUMERATION: (
          u'_ReadEnumerationDataTypeDefinition'),
      definitions.TYPE_INDICATOR_FLOATING_POINT: (
          u'_ReadFloatingPointDataTypeDefinition'),
      definitions.TYPE_INDICATOR_INTEGER: u'_ReadIntegerDataTypeDefinition',
      definitions.TYPE_INDICATOR_FORMAT: u'_ReadFormatDataTypeDefinition',
      definitions.TYPE_INDICATOR_SEQUENCE: u'_ReadSequenceDataTypeDefinition',
      definitions.TYPE_INDICATOR_STREAM: u'_ReadStreamDataTypeDefinition',
      definitions.TYPE_INDICATOR_STRING: u'_ReadStringDataTypeDefinition',
      definitions.TYPE_INDICATOR_STRUCTURE: u'_ReadStructureDataTypeDefinition',
      definitions.TYPE_INDICATOR_UNION: u'_ReadUnionDataTypeDefinition',
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
      self, definitions_registry, definition_values, definition_name):
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

    definition_object = self._ReadSemanticDataTypeDefinition(
        definitions_registry, definition_values, data_types.ConstantDefinition,
        definition_name)
    definition_object.value = value

    return definition_object

  def _ReadDataTypeDefinition(
      self, unused_definitions_registry, definition_values,
      data_type_definition_class, definition_name):
    """Reads a data type definition.

    Args:
      definitions_registry (DataTypeDefinitionsRegistry): data type definitions
          registry.
      definition_values (dict[str, object]): definition values.
      data_type_definition_class (str): data type definition class.
      definition_name (str): name of the definition.

    Returns:
      DataTypeDefinition: data type definition.

    Raises:
      DefinitionReaderError: if the definitions values are missing or if
          the format is incorrect.
    """
    aliases = definition_values.get(u'aliases', None)
    description = definition_values.get(u'description', None)
    urls = definition_values.get(u'urls', None)

    return data_type_definition_class(
        definition_name, aliases=aliases, description=description, urls=urls)

  def _ReadDataTypeDefinitionWithMembers(
      self, definitions_registry, definition_values,
      data_type_definition_class, definition_name):
    """Reads a data type definition with members.

    Args:
      definitions_registry (DataTypeDefinitionsRegistry): data type definitions
          registry.
      definition_values (dict[str, object]): definition values.
      data_type_definition_class (str): data type definition class.
      definition_name (str): name of the definition.

    Returns:
      StringDefinition: string data type definition.

    Raises:
      DefinitionReaderError: if the definitions values are missing or if
          the format is incorrect.
    """
    members = definition_values.get(u'members', None)
    if not members:
      error_message = u'missing members'
      raise errors.DefinitionReaderError(definition_name, error_message)

    definition_object = self._ReadDataTypeDefinition(
        definitions_registry, definition_values, data_type_definition_class,
        definition_name)

    attributes = definition_values.get(u'attributes', None)
    if attributes:
      byte_order = attributes.get(u'byte_order', definitions.BYTE_ORDER_NATIVE)
      if byte_order not in definitions.BYTE_ORDERS:
        error_message = u'unsupported byte-order attribute: {0!s}'.format(
            byte_order)
        raise errors.DefinitionReaderError(definition_name, error_message)

      definition_object.byte_order = byte_order

    for member in members:
      member_data_type_definition = self._ReadMemberDataTypeDefinitionMember(
          definitions_registry, member, definition_object.name)
      definition_object.members.append(member_data_type_definition)

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

    definition_object = self._ReadSemanticDataTypeDefinition(
        definitions_registry, definition_values,
        data_types.EnumerationDefinition, definition_name)

    last_name = None
    for enumeration_value in values:
      aliases = enumeration_value.get(u'aliases', None)
      description = enumeration_value.get(u'description', None)
      name = enumeration_value.get(u'name', None)
      number = enumeration_value.get(u'number', None)

      if not name or number is None:
        if last_name:
          error_location = u'after: {0:s}'.format(last_name)
        else:
          error_location = u'at start'

        error_message = u'{0:s} missing name or number'.format(error_location)
        raise errors.DefinitionReaderError(definition_name, error_message)

      else:
        try:
          definition_object.AddValue(
              name, number, aliases=aliases, description=description)
        except KeyError as exception:
          error_message = u'{0!s}'.format(exception)
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
    attributes = definition_values.get(u'attributes', None)
    if attributes is not None:
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
      self, definitions_registry, definition_values, data_type_definition_class,
      definition_name, default_size=definitions.SIZE_NATIVE,
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
    definition_object = self._ReadStorageDataTypeDefinition(
        definitions_registry, definition_values, data_type_definition_class,
        definition_name)

    attributes = definition_values.get(u'attributes', None)
    if attributes:
      size = attributes.get(u'size', default_size)
      if size != definitions.SIZE_NATIVE:
        try:
          int(size)
        except ValueError:
          error_message = u'unuspported size attribute: {0!s}'.format(size)
          raise errors.DefinitionReaderError(definition_name, error_message)

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

  def _ReadFormatDataTypeDefinition(
      self, definitions_registry, definition_values, definition_name):
    """Reads a format data type definition.

    Args:
      definitions_registry (DataTypeDefinitionsRegistry): data type definitions
          registry.
      definition_values (dict[str, object]): definition values.
      definition_name (str): name of the definition.

    Returns:
      FormatDefinition: format definition.
    """
    definition_object = self._ReadLayoutDataTypeDefinition(
        definitions_registry, definition_values, data_types.FormatDefinition,
        definition_name)

    definition_object.metadata = definition_values.get(u'metadata', {})

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

    attributes = definition_values.get(u'attributes', None)
    if attributes:
      format_attribute = attributes.get(u'format', definitions.FORMAT_SIGNED)
      if format_attribute not in self._INTEGER_FORMAT_ATTRIBUTES:
        error_message = u'unsupported format attribute: {0!s}'.format(
            format_attribute)
        raise errors.DefinitionReaderError(definition_name, error_message)

      definition_object.format = format_attribute

    return definition_object

  def _ReadLayoutDataTypeDefinition(
      self, definitions_registry, definition_values, data_type_definition_class,
      definition_name):
    """Reads a layout data type definition.

    Args:
      definitions_registry (DataTypeDefinitionsRegistry): data type definitions
          registry.
      definition_values (dict[str, object]): definition values.
      data_type_definition_class (str): data type definition class.
      definition_name (str): name of the definition.

    Returns:
      LayoutDataTypeDefinition: layout data type definition.

    Raises:
      DefinitionReaderError: if the definitions values are missing or if
          the format is incorrect.
    """
    definition_object = self._ReadDataTypeDefinition(
        definitions_registry, definition_values, data_type_definition_class,
        definition_name)

    attributes = definition_values.get(u'attributes', None)
    if attributes is not None:
      byte_order = attributes.get(u'byte_order', definitions.BYTE_ORDER_NATIVE)
      if byte_order not in definitions.BYTE_ORDERS:
        error_message = u'unsupported byte-order attribute: {0!s}'.format(
            byte_order)
        raise errors.DefinitionReaderError(definition_name, error_message)

      definition_object.byte_order = byte_order

    return definition_object

  def _ReadMemberDataTypeDefinitionMember(
      self, definitions_registry, definition_values, definition_name):
    """Reads a member data type definition.

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
    if not definition_values:
      error_message = u'invalid structure member missing definition values'
      raise errors.DefinitionReaderError(definition_name, error_message)

    name = definition_values.get(u'name', None)
    type_indicator = definition_values.get(u'type', None)

    if not name and type_indicator != definitions.TYPE_INDICATOR_UNION:
      error_message = u'invalid structure member missing name'
      raise errors.DefinitionReaderError(definition_name, error_message)

    # TODO: detect duplicate names.

    data_type = definition_values.get(u'data_type', None)

    type_values = filter(lambda value: value is not None, (
        data_type, type_indicator))

    if not type_values:
      error_message = (
          u'invalid structure member: {0:s} both data type and type are '
          u'missing').format(name or u'<NAMELESS>')
      raise errors.DefinitionReaderError(definition_name, error_message)

    if len(type_values) > 1:
      error_message = (
          u'invalid structure member: {0:s} data type and type not allowed to '
          u'be set at the same time').format(name or u'<NAMELESS>')
      raise errors.DefinitionReaderError(definition_name, error_message)

    if type_indicator is not None:
      data_type_callback = self._DATA_TYPE_CALLBACKS.get(type_indicator, None)
      if data_type_callback:
        data_type_callback = getattr(self, data_type_callback, None)
      if not data_type_callback:
        error_message = u'unuspported data type definition: {0:s}.'.format(
            type_indicator)
        raise errors.DefinitionReaderError(name, error_message)

      try:
        definition_object = data_type_callback(
            definitions_registry, definition_values, name)
      except errors.DefinitionReaderError as exception:
        error_message = u'in: {0:s} {1:s}'.format(
            exception.name or u'<NAMELESS>', exception.message)
        raise errors.DefinitionReaderError(definition_name, error_message)

    if data_type is not None:
      data_type_definition = definitions_registry.GetDefinitionByName(
          data_type)
      if not data_type_definition:
        error_message = (
            u'invalid structure member: {0:s} undefined data type: '
            u'{1:s}').format(name or u'<NAMELESS>', data_type)
        raise errors.DefinitionReaderError(definition_name, error_message)

      aliases = definition_values.get(u'aliases', None)
      description = definition_values.get(u'description', None)

      definition_object = data_types.MemberDataTypeDefinition(
          name, data_type_definition, aliases=aliases, data_type=data_type,
          description=description)

    return definition_object

  def _ReadSemanticDataTypeDefinition(
      self, definitions_registry, definition_values, data_type_definition_class,
      definition_name):
    """Reads a semantic data type definition.

    Args:
      definitions_registry (DataTypeDefinitionsRegistry): data type definitions
          registry.
      definition_values (dict[str, object]): definition values.
      data_type_definition_class (str): data type definition class.
      definition_name (str): name of the definition.

    Returns:
      SemanticDataTypeDefinition: semantic data type definition.

    Raises:
      DefinitionReaderError: if the definitions values are missing or if
          the format is incorrect.
    """
    attributes = definition_values.get(u'attributes', None)
    if attributes is not None:
      error_message = u'attributes not supported by semantic data type'
      raise errors.DefinitionReaderError(definition_name, error_message)

    return self._ReadDataTypeDefinition(
        definitions_registry, definition_values, data_type_definition_class,
        definition_name)

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

  def _ReadStorageDataTypeDefinition(
      self, definitions_registry, definition_values, data_type_definition_class,
      definition_name):
    """Reads a storage data type definition.

    Args:
      definitions_registry (DataTypeDefinitionsRegistry): data type definitions
          registry.
      definition_values (dict[str, object]): definition values.
      data_type_definition_class (str): data type definition class.
      definition_name (str): name of the definition.

    Returns:
      StorageDataTypeDefinition: storage data type definition.

    Raises:
      DefinitionReaderError: if the definitions values are missing or if
          the format is incorrect.
    """
    definition_object = self._ReadDataTypeDefinition(
        definitions_registry, definition_values, data_type_definition_class,
        definition_name)

    attributes = definition_values.get(u'attributes', None)
    if attributes:
      byte_order = attributes.get(u'byte_order', definitions.BYTE_ORDER_NATIVE)
      if byte_order not in definitions.BYTE_ORDERS:
        error_message = u'unsupported byte-order attribute: {0!s}'.format(
            byte_order)
        raise errors.DefinitionReaderError(definition_name, error_message)

      definition_object.byte_order = byte_order

    return definition_object

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
    return self._ReadDataTypeDefinitionWithMembers(
        definitions_registry, definition_values, data_types.StructureDefinition,
        definition_name)

  def _ReadUnionDataTypeDefinition(
      self, definitions_registry, definition_values, definition_name):
    """Reads an union data type definition.

    Args:
      definitions_registry (DataTypeDefinitionsRegistry): data type definitions
          registry.
      definition_values (dict[str, object]): definition values.
      definition_name (str): name of the definition.

    Returns:
      UnionDefinition: union data type definition.

    Raises:
      DefinitionReaderError: if the definitions values are missing or if
          the format is incorrect.
    """
    return self._ReadDataTypeDefinitionWithMembers(
        definitions_registry, definition_values, data_types.UnionDefinition,
        definition_name)

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


class DataTypeDefinitionsFileReader(DataTypeDefinitionsReader):
  """Data type definitions file reader."""

  def _ReadDefinition(self, definitions_registry, definition_values):
    """Reads a data type definition.

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

    data_type_callback = self._DATA_TYPE_CALLBACKS.get(type_indicator, None)
    if data_type_callback:
      data_type_callback = getattr(self, data_type_callback, None)
    if not data_type_callback:
      error_message = u'unuspported data type definition: {0:s}.'.format(
          type_indicator)
      raise errors.DefinitionReaderError(name, error_message)

    return data_type_callback(definitions_registry, definition_values, name)

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
  """YAML data type definitions file reader.

  Attributes:
    dict[str, object]: metadata.
  """

  def __init__(self):
    """Initializes a YAML data type definitions file reader."""
    super(YAMLDataTypeDefinitionsFileReader, self).__init__()
    self.metadata = {}

  def _GetFormatErrorLocation(
      self, yaml_definition, last_definition_object):
    """Retrieves a format error location.

    Args:
      yaml_definition (dict[str, object]): current YAML definition.
      last_definition_object (DataTypeDefinition): previous data type
          definition.

    Returns:
      str: format error location.
    """
    name = yaml_definition.get(u'name', None)
    if name:
      error_location = u'in: {0:s}'.format(name or u'<NAMELESS>')
    elif last_definition_object:
      error_location = u'after: {0:s}'.format(last_definition_object.name)
    else:
      error_location = u'at start'

    return error_location

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
    last_definition_object = None
    error_location = None
    error_message = None

    try:
      yaml_generator = yaml.safe_load_all(file_object)

      for yaml_definition in yaml_generator:
        definition_object = self._ReadDefinition(
            definitions_registry, yaml_definition)
        if not definition_object:
          error_location = self._GetFormatErrorLocation(
              yaml_definition, last_definition_object)
          error_message = u'{0:s} Missing definition object.'.format(
              error_location)
          raise errors.FormatError(error_message)

        definitions_registry.RegisterDefinition(definition_object)
        last_definition_object = definition_object

    except errors.DefinitionReaderError as exception:
      error_message = u'in: {0:s} {1:s}'.format(
          exception.name or u'<NAMELESS>', exception.message)
      raise errors.FormatError(error_message)

    except (yaml.reader.ReaderError, yaml.scanner.ScannerError) as exception:
      error_location = self._GetFormatErrorLocation({}, last_definition_object)
      error_message = u'{0:s} {1!s}'.format(error_location, exception)
      raise errors.FormatError(error_message)
