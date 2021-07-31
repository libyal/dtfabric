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
      definitions.TYPE_INDICATOR_BOOLEAN: '_ReadBooleanDataTypeDefinition',
      definitions.TYPE_INDICATOR_CHARACTER: '_ReadCharacterDataTypeDefinition',
      definitions.TYPE_INDICATOR_CONSTANT: '_ReadConstantDataTypeDefinition',
      definitions.TYPE_INDICATOR_ENUMERATION: (
          '_ReadEnumerationDataTypeDefinition'),
      definitions.TYPE_INDICATOR_FLOATING_POINT: (
          '_ReadFloatingPointDataTypeDefinition'),
      definitions.TYPE_INDICATOR_FORMAT: '_ReadFormatDataTypeDefinition',
      definitions.TYPE_INDICATOR_INTEGER: '_ReadIntegerDataTypeDefinition',
      definitions.TYPE_INDICATOR_PADDING: '_ReadPaddingDataTypeDefinition',
      definitions.TYPE_INDICATOR_SEQUENCE: '_ReadSequenceDataTypeDefinition',
      definitions.TYPE_INDICATOR_STREAM: '_ReadStreamDataTypeDefinition',
      definitions.TYPE_INDICATOR_STRING: '_ReadStringDataTypeDefinition',
      definitions.TYPE_INDICATOR_STRUCTURE: '_ReadStructureDataTypeDefinition',
      definitions.TYPE_INDICATOR_STRUCTURE_FAMILY: (
          '_ReadStructureFamilyDataTypeDefinition'),
      definitions.TYPE_INDICATOR_STRUCTURE_GROUP: (
          '_ReadStructureGroupDataTypeDefinition'),
      definitions.TYPE_INDICATOR_UNION: '_ReadUnionDataTypeDefinition',
      definitions.TYPE_INDICATOR_UUID: '_ReadUUIDDataTypeDefinition',
  }

  _INTEGER_FORMAT_ATTRIBUTES = frozenset([
      definitions.FORMAT_SIGNED,
      definitions.FORMAT_UNSIGNED])

  _SUPPORTED_DEFINITION_VALUES_DATA_TYPE = set([
      'aliases', 'description', 'name', 'type', 'urls'])

  _SUPPORTED_DEFINITION_VALUES_MEMBER_DATA_TYPE = set([
      'aliases', 'condition', 'data_type', 'description', 'name', 'type',
      'value', 'values'])

  _SUPPORTED_DEFINITION_VALUES_STORAGE_DATA_TYPE = set([
      'attributes']).union(_SUPPORTED_DEFINITION_VALUES_DATA_TYPE)

  _SUPPORTED_DEFINITION_VALUES_STORAGE_DATA_TYPE_WITH_MEMBERS = set([
      'members']).union(_SUPPORTED_DEFINITION_VALUES_STORAGE_DATA_TYPE)

  _SUPPORTED_DEFINITION_VALUES_CONSTANT = set([
      'value']).union(_SUPPORTED_DEFINITION_VALUES_DATA_TYPE)

  _SUPPORTED_DEFINITION_VALUES_ENUMERATION = set([
      'values']).union(_SUPPORTED_DEFINITION_VALUES_DATA_TYPE)

  _SUPPORTED_DEFINITION_VALUES_ELEMENTS_DATA_TYPE = set([
      'element_data_type', 'elements_data_size', 'elements_terminator',
      'number_of_elements']).union(_SUPPORTED_DEFINITION_VALUES_DATA_TYPE)

  _SUPPORTED_DEFINITION_VALUES_ELEMENTS_MEMBER_DATA_TYPE = set([
      'element_data_type', 'elements_data_size', 'elements_terminator',
      'number_of_elements']).union(
          _SUPPORTED_DEFINITION_VALUES_MEMBER_DATA_TYPE)

  _SUPPORTED_DEFINITION_VALUES_FORMAT = set([
      'attributes', 'layout', 'metadata']).union(
          _SUPPORTED_DEFINITION_VALUES_DATA_TYPE)

  _SUPPORTED_DEFINITION_VALUES_PADDING = set([
      'alignment_size']).union(_SUPPORTED_DEFINITION_VALUES_MEMBER_DATA_TYPE)

  _SUPPORTED_DEFINITION_VALUES_STRING = set([
      'encoding']).union(_SUPPORTED_DEFINITION_VALUES_ELEMENTS_DATA_TYPE)

  _SUPPORTED_DEFINITION_VALUES_STRING_MEMBER = set([
      'encoding']).union(_SUPPORTED_DEFINITION_VALUES_ELEMENTS_MEMBER_DATA_TYPE)

  _SUPPORTED_DEFINITION_VALUES_STRUCTURE_FAMILY = set([
      'base', 'members']).union(_SUPPORTED_DEFINITION_VALUES_DATA_TYPE)

  _SUPPORTED_DEFINITION_VALUES_STRUCTURE_GROUP = set([
      'base', 'identifier', 'members']).union(
          _SUPPORTED_DEFINITION_VALUES_DATA_TYPE)

  _SUPPORTED_ATTRIBUTES_STORAGE_DATA_TYPE = set([
      'byte_order'])

  _SUPPORTED_ATTRIBUTES_FIXED_SIZE_DATA_TYPE = set([
      'size', 'units']).union(_SUPPORTED_ATTRIBUTES_STORAGE_DATA_TYPE)

  _SUPPORTED_ATTRIBUTES_BOOLEAN = set([
      'false_value', 'true_value']).union(
          _SUPPORTED_ATTRIBUTES_FIXED_SIZE_DATA_TYPE)

  _SUPPORTED_ATTRIBUTES_FORMAT = set([
      'byte_order'])

  _SUPPORTED_ATTRIBUTES_INTEGER = set([
      'format']).union(_SUPPORTED_ATTRIBUTES_FIXED_SIZE_DATA_TYPE)

  def _ReadBooleanDataTypeDefinition(
      self, definitions_registry, definition_values, definition_name,
      is_member=False):
    """Reads a boolean data type definition.

    Args:
      definitions_registry (DataTypeDefinitionsRegistry): data type definitions
          registry.
      definition_values (dict[str, object]): definition values.
      definition_name (str): name of the definition.
      is_member (Optional[bool]): True if the data type definition is a member
          data type definition.

    Returns:
      BooleanDataTypeDefinition: boolean data type definition.
    """
    return self._ReadFixedSizeDataTypeDefinition(
        definitions_registry, definition_values,
        data_types.BooleanDefinition, definition_name,
        self._SUPPORTED_ATTRIBUTES_BOOLEAN, is_member=is_member,
        supported_size_values=(1, 2, 4))

  def _ReadCharacterDataTypeDefinition(
      self, definitions_registry, definition_values, definition_name,
      is_member=False):
    """Reads a character data type definition.

    Args:
      definitions_registry (DataTypeDefinitionsRegistry): data type definitions
          registry.
      definition_values (dict[str, object]): definition values.
      definition_name (str): name of the definition.
      is_member (Optional[bool]): True if the data type definition is a member
          data type definition.

    Returns:
      CharacterDataTypeDefinition: character data type definition.
    """
    return self._ReadFixedSizeDataTypeDefinition(
        definitions_registry, definition_values,
        data_types.CharacterDefinition, definition_name,
        self._SUPPORTED_ATTRIBUTES_FIXED_SIZE_DATA_TYPE,
        is_member=is_member, supported_size_values=(1, 2, 4))

  def _ReadConstantDataTypeDefinition(
      self, definitions_registry, definition_values, definition_name,
      is_member=False):
    """Reads a constant data type definition.

    Args:
      definitions_registry (DataTypeDefinitionsRegistry): data type definitions
          registry.
      definition_values (dict[str, object]): definition values.
      definition_name (str): name of the definition.
      is_member (Optional[bool]): True if the data type definition is a member
          data type definition.

    Returns:
      ConstantDataTypeDefinition: constant data type definition.

    Raises:
      DefinitionReaderError: if the definitions values are missing or if
          the format is incorrect.
    """
    if is_member:
      error_message = 'data type not supported as member'
      raise errors.DefinitionReaderError(definition_name, error_message)

    value = definition_values.get('value', None)
    if value is None:
      error_message = 'missing value'
      raise errors.DefinitionReaderError(definition_name, error_message)

    definition_object = self._ReadSemanticDataTypeDefinition(
        definitions_registry, definition_values, data_types.ConstantDefinition,
        definition_name, self._SUPPORTED_DEFINITION_VALUES_CONSTANT)
    definition_object.value = value

    return definition_object

  # pylint: disable=unused-argument

  def _ReadDataTypeDefinition(
      self, definitions_registry, definition_values, data_type_definition_class,
      definition_name, supported_definition_values):
    """Reads a data type definition.

    Args:
      definitions_registry (DataTypeDefinitionsRegistry): data type definitions
          registry.
      definition_values (dict[str, object]): definition values.
      data_type_definition_class (str): data type definition class.
      definition_name (str): name of the definition.
      supported_definition_values (set[str]): names of the supported definition
          values.

    Returns:
      DataTypeDefinition: data type definition.

    Raises:
      DefinitionReaderError: if the definitions values are missing or if
          the format is incorrect.
    """
    unsupported_definition_values = set(definition_values.keys()).difference(
        supported_definition_values)
    if unsupported_definition_values:
      error_message = 'unsupported definition values: {0:s}'.format(
          ', '.join(unsupported_definition_values))
      raise errors.DefinitionReaderError(definition_name, error_message)

    aliases = definition_values.get('aliases', None)
    description = definition_values.get('description', None)
    urls = definition_values.get('urls', None)

    return data_type_definition_class(
        definition_name, aliases=aliases, description=description, urls=urls)

  def _ReadDataTypeDefinitionWithMembers(
      self, definitions_registry, definition_values,
      data_type_definition_class, definition_name, supports_conditions=False):
    """Reads a data type definition with members.

    Args:
      definitions_registry (DataTypeDefinitionsRegistry): data type definitions
          registry.
      definition_values (dict[str, object]): definition values.
      data_type_definition_class (str): data type definition class.
      definition_name (str): name of the definition.
      supports_conditions (Optional[bool]): True if conditions are supported
          by the data type definition.

    Returns:
      StringDefinition: string data type definition.

    Raises:
      DefinitionReaderError: if the definitions values are missing or if
          the format is incorrect.
    """
    members = definition_values.get('members', None)
    if not members:
      error_message = 'missing members'
      raise errors.DefinitionReaderError(definition_name, error_message)

    supported_definition_values = (
        self._SUPPORTED_DEFINITION_VALUES_STORAGE_DATA_TYPE_WITH_MEMBERS)
    definition_object = self._ReadDataTypeDefinition(
        definitions_registry, definition_values, data_type_definition_class,
        definition_name, supported_definition_values)

    attributes = definition_values.get('attributes', None)
    if attributes:
      unsupported_attributes = set(attributes.keys()).difference(
          self._SUPPORTED_ATTRIBUTES_STORAGE_DATA_TYPE)
      if unsupported_attributes:
        error_message = 'unsupported attributes: {0:s}'.format(
            ', '.join(unsupported_attributes))
        raise errors.DefinitionReaderError(definition_name, error_message)

      byte_order = attributes.get('byte_order', definitions.BYTE_ORDER_NATIVE)
      if byte_order not in definitions.BYTE_ORDERS:
        error_message = 'unsupported byte-order attribute: {0!s}'.format(
            byte_order)
        raise errors.DefinitionReaderError(definition_name, error_message)

      definition_object.byte_order = byte_order

    for member in members:
      section = member.get('section', None)
      if section:
        member_section_definition = data_types.MemberSectionDefinition(section)
        definition_object.AddSectionDefinition(member_section_definition)
      else:
        member_data_type_definition = self._ReadMemberDataTypeDefinitionMember(
            definitions_registry, member, definition_object.name,
            supports_conditions=supports_conditions)

        try:
          definition_object.AddMemberDefinition(member_data_type_definition)
        except KeyError as exception:
          error_message = '{0!s}'.format(exception)
          raise errors.DefinitionReaderError(definition_name, error_message)

    return definition_object

  def _ReadEnumerationDataTypeDefinition(
      self, definitions_registry, definition_values, definition_name,
      is_member=False):
    """Reads an enumeration data type definition.

    Args:
      definitions_registry (DataTypeDefinitionsRegistry): data type definitions
          registry.
      definition_values (dict[str, object]): definition values.
      definition_name (str): name of the definition.
      is_member (Optional[bool]): True if the data type definition is a member
          data type definition.

    Returns:
      EnumerationDataTypeDefinition: enumeration data type definition.

    Raises:
      DefinitionReaderError: if the definitions values are missing or if
          the format is incorrect.
    """
    if is_member:
      error_message = 'data type not supported as member'
      raise errors.DefinitionReaderError(definition_name, error_message)

    values = definition_values.get('values')
    if not values:
      error_message = 'missing values'
      raise errors.DefinitionReaderError(definition_name, error_message)

    definition_object = self._ReadSemanticDataTypeDefinition(
        definitions_registry, definition_values,
        data_types.EnumerationDefinition, definition_name,
        self._SUPPORTED_DEFINITION_VALUES_ENUMERATION)

    last_name = None
    for enumeration_value in values:
      aliases = enumeration_value.get('aliases', None)
      description = enumeration_value.get('description', None)
      name = enumeration_value.get('name', None)
      number = enumeration_value.get('number', None)

      if not name or number is None:
        if last_name:
          error_location = 'after: {0:s}'.format(last_name)
        else:
          error_location = 'at start'

        error_message = '{0:s} missing name or number'.format(error_location)
        raise errors.DefinitionReaderError(definition_name, error_message)

      try:
        definition_object.AddValue(
            name, number, aliases=aliases, description=description)
      except KeyError as exception:
        error_message = '{0!s}'.format(exception)
        raise errors.DefinitionReaderError(definition_name, error_message)

      last_name = name

    return definition_object

  def _ReadElementSequenceDataTypeDefinition(
      self, definitions_registry, definition_values,
      data_type_definition_class, definition_name, supported_definition_values):
    """Reads an element sequence data type definition.

    Args:
      definitions_registry (DataTypeDefinitionsRegistry): data type definitions
          registry.
      definition_values (dict[str, object]): definition values.
      data_type_definition_class (str): data type definition class.
      definition_name (str): name of the definition.
      supported_definition_values (set[str]): names of the supported definition
          values.

    Returns:
      SequenceDefinition: sequence data type definition.

    Raises:
      DefinitionReaderError: if the definitions values are missing or if
          the format is incorrect.
    """
    unsupported_definition_values = set(definition_values.keys()).difference(
        supported_definition_values)
    if unsupported_definition_values:
      error_message = 'unsupported definition values: {0:s}'.format(
          ', '.join(unsupported_definition_values))
      raise errors.DefinitionReaderError(definition_name, error_message)

    element_data_type = definition_values.get('element_data_type', None)
    if not element_data_type:
      error_message = 'missing element data type'
      raise errors.DefinitionReaderError(definition_name, error_message)

    elements_data_size = definition_values.get('elements_data_size', None)
    elements_terminator = definition_values.get('elements_terminator', None)
    number_of_elements = definition_values.get('number_of_elements', None)

    size_values = (elements_data_size, elements_terminator, number_of_elements)
    size_values = [value for value in size_values if value is not None]

    if not size_values:
      error_message = (
          'missing element data size, elements terminator and number of '
          'elements')
      raise errors.DefinitionReaderError(definition_name, error_message)

    if elements_data_size is not None and number_of_elements is not None:
      error_message = (
          'element data size and number of elements not allowed to be set '
          'at the same time')
      raise errors.DefinitionReaderError(definition_name, error_message)

    element_data_type_definition = definitions_registry.GetDefinitionByName(
        element_data_type)
    if not element_data_type_definition:
      error_message = 'undefined element data type: {0:s}.'.format(
          element_data_type)
      raise errors.DefinitionReaderError(definition_name, error_message)

    element_byte_size = element_data_type_definition.GetByteSize()
    element_type_indicator = element_data_type_definition.TYPE_INDICATOR
    if not element_byte_size and element_type_indicator != (
        definitions.TYPE_INDICATOR_STRING):
      error_message = (
          'unsupported variable size element data type: {0:s}'.format(
              element_data_type))
      raise errors.DefinitionReaderError(definition_name, error_message)

    aliases = definition_values.get('aliases', None)
    description = definition_values.get('description', None)
    urls = definition_values.get('urls', None)

    definition_object = data_type_definition_class(
        definition_name, element_data_type_definition, aliases=aliases,
        data_type=element_data_type, description=description, urls=urls)

    if elements_data_size is not None:
      try:
        definition_object.elements_data_size = int(elements_data_size)
      except ValueError:
        definition_object.elements_data_size_expression = elements_data_size

    elif number_of_elements is not None:
      try:
        definition_object.number_of_elements = int(number_of_elements)
      except ValueError:
        definition_object.number_of_elements_expression = number_of_elements

    if elements_terminator is not None:
      if isinstance(elements_terminator, str):
        elements_terminator = elements_terminator.encode('ascii')

      definition_object.elements_terminator = elements_terminator

    return definition_object

  def _ReadFixedSizeDataTypeDefinition(
      self, definitions_registry, definition_values, data_type_definition_class,
      definition_name, supported_attributes,
      default_size=definitions.SIZE_NATIVE, default_units='bytes',
      is_member=False, supported_size_values=None):
    """Reads a fixed-size data type definition.

    Args:
      definitions_registry (DataTypeDefinitionsRegistry): data type definitions
          registry.
      definition_values (dict[str, object]): definition values.
      data_type_definition_class (str): data type definition class.
      definition_name (str): name of the definition.
      supported_attributes (set[str]): names of the supported attributes.
      default_size (Optional[int]): default size.
      default_units (Optional[str]): default units.
      is_member (Optional[bool]): True if the data type definition is a member
          data type definition.
      supported_size_values (Optional[tuple[int]]): supported size values,
          or None if not set.

    Returns:
      FixedSizeDataTypeDefinition: fixed-size data type definition.

    Raises:
      DefinitionReaderError: if the definitions values are missing or if
          the format is incorrect.
    """
    definition_object = self._ReadStorageDataTypeDefinition(
        definitions_registry, definition_values, data_type_definition_class,
        definition_name, supported_attributes, is_member=is_member)

    attributes = definition_values.get('attributes', None)
    if attributes:
      size = attributes.get('size', default_size)
      if size != definitions.SIZE_NATIVE:
        try:
          int(size)
        except ValueError:
          error_message = 'unuspported size attribute: {0!s}'.format(size)
          raise errors.DefinitionReaderError(definition_name, error_message)

        if supported_size_values and size not in supported_size_values:
          error_message = 'unuspported size value: {0!s}'.format(size)
          raise errors.DefinitionReaderError(definition_name, error_message)

      definition_object.size = size
      definition_object.units = attributes.get('units', default_units)

    return definition_object

  def _ReadFloatingPointDataTypeDefinition(
      self, definitions_registry, definition_values, definition_name,
      is_member=False):
    """Reads a floating-point data type definition.

    Args:
      definitions_registry (DataTypeDefinitionsRegistry): data type definitions
          registry.
      definition_values (dict[str, object]): definition values.
      definition_name (str): name of the definition.
      is_member (Optional[bool]): True if the data type definition is a member
          data type definition.

    Returns:
      FloatingPointDefinition: floating-point data type definition.
    """
    return self._ReadFixedSizeDataTypeDefinition(
        definitions_registry, definition_values,
        data_types.FloatingPointDefinition, definition_name,
        self._SUPPORTED_ATTRIBUTES_FIXED_SIZE_DATA_TYPE,
        is_member=is_member, supported_size_values=(4, 8))

  def _ReadFormatDataTypeDefinition(
      self, definitions_registry, definition_values, definition_name,
      is_member=False):
    """Reads a format data type definition.

    Args:
      definitions_registry (DataTypeDefinitionsRegistry): data type definitions
          registry.
      definition_values (dict[str, object]): definition values.
      definition_name (str): name of the definition.
      is_member (Optional[bool]): True if the data type definition is a member
          data type definition.

    Returns:
      FormatDefinition: format definition.

    Raises:
      DefinitionReaderError: if the definitions values are missing or if
          the format is incorrect.
    """
    if is_member:
      error_message = 'data type not supported as member'
      raise errors.DefinitionReaderError(definition_name, error_message)

    definition_object = self._ReadLayoutDataTypeDefinition(
        definitions_registry, definition_values, data_types.FormatDefinition,
        definition_name, self._SUPPORTED_DEFINITION_VALUES_FORMAT)

    # TODO: disabled for now
    # layout = definition_values.get('layout', None)
    # if layout is None:
    #   error_message = 'missing layout'
    #   raise errors.DefinitionReaderError(definition_name, error_message)

    definition_object.metadata = definition_values.get('metadata', {})

    attributes = definition_values.get('attributes', None)
    if attributes:
      unsupported_attributes = set(attributes.keys()).difference(
          self._SUPPORTED_ATTRIBUTES_FORMAT)
      if unsupported_attributes:
        error_message = 'unsupported attributes: {0:s}'.format(
            ', '.join(unsupported_attributes))
        raise errors.DefinitionReaderError(definition_name, error_message)

      byte_order = attributes.get('byte_order', definitions.BYTE_ORDER_NATIVE)
      if byte_order not in definitions.BYTE_ORDERS:
        error_message = 'unsupported byte-order attribute: {0!s}'.format(
            byte_order)
        raise errors.DefinitionReaderError(definition_name, error_message)

      definition_object.byte_order = byte_order

    return definition_object

  def _ReadIntegerDataTypeDefinition(
      self, definitions_registry, definition_values, definition_name,
      is_member=False):
    """Reads an integer data type definition.

    Args:
      definitions_registry (DataTypeDefinitionsRegistry): data type definitions
          registry.
      definition_values (dict[str, object]): definition values.
      definition_name (str): name of the definition.
      is_member (Optional[bool]): True if the data type definition is a member
          data type definition.

    Returns:
      IntegerDataTypeDefinition: integer data type definition.

    Raises:
      DefinitionReaderError: if the definitions values are missing or if
          the format is incorrect.
    """
    definition_object = self._ReadFixedSizeDataTypeDefinition(
        definitions_registry, definition_values,
        data_types.IntegerDefinition, definition_name,
        self._SUPPORTED_ATTRIBUTES_INTEGER, is_member=is_member,
        supported_size_values=(1, 2, 4, 8))

    attributes = definition_values.get('attributes', None)
    if attributes:
      format_attribute = attributes.get('format', definitions.FORMAT_SIGNED)
      if format_attribute not in self._INTEGER_FORMAT_ATTRIBUTES:
        error_message = 'unsupported format attribute: {0!s}'.format(
            format_attribute)
        raise errors.DefinitionReaderError(definition_name, error_message)

      definition_object.format = format_attribute

    return definition_object

  def _ReadLayoutDataTypeDefinition(
      self, definitions_registry, definition_values, data_type_definition_class,
      definition_name, supported_definition_values):
    """Reads a layout data type definition.

    Args:
      definitions_registry (DataTypeDefinitionsRegistry): data type definitions
          registry.
      definition_values (dict[str, object]): definition values.
      data_type_definition_class (str): data type definition class.
      definition_name (str): name of the definition.
      supported_definition_values (set[str]): names of the supported definition
          values.

    Returns:
      LayoutDataTypeDefinition: layout data type definition.

    Raises:
      DefinitionReaderError: if the definitions values are missing or if
          the format is incorrect.
    """
    return self._ReadDataTypeDefinition(
        definitions_registry, definition_values, data_type_definition_class,
        definition_name, supported_definition_values)

  def _ReadMemberDataTypeDefinitionMember(
      self, definitions_registry, definition_values, definition_name,
      supports_conditions=False):
    """Reads a member data type definition.

    Args:
      definitions_registry (DataTypeDefinitionsRegistry): data type definitions
          registry.
      definition_values (dict[str, object]): definition values.
      definition_name (str): name of the definition.
      supports_conditions (Optional[bool]): True if conditions are supported
          by the data type definition.

    Returns:
      DataTypeDefinition: structure member data type definition.

    Raises:
      DefinitionReaderError: if the definitions values are missing or if
          the format is incorrect.
    """
    if not definition_values:
      error_message = 'invalid structure member missing definition values'
      raise errors.DefinitionReaderError(definition_name, error_message)

    name = definition_values.get('name', None)
    type_indicator = definition_values.get('type', None)

    if not name and type_indicator != definitions.TYPE_INDICATOR_UNION:
      error_message = 'invalid structure member missing name'
      raise errors.DefinitionReaderError(definition_name, error_message)

    # TODO: detect duplicate names.

    data_type = definition_values.get('data_type', None)

    type_values = (data_type, type_indicator)
    type_values = [value for value in type_values if value is not None]

    if not type_values:
      error_message = (
          'invalid structure member: {0:s} both data type and type are '
          'missing').format(name or '<NAMELESS>')
      raise errors.DefinitionReaderError(definition_name, error_message)

    if len(type_values) > 1:
      error_message = (
          'invalid structure member: {0:s} data type and type not allowed to '
          'be set at the same time').format(name or '<NAMELESS>')
      raise errors.DefinitionReaderError(definition_name, error_message)

    condition = definition_values.get('condition', None)
    if not supports_conditions and condition:
      error_message = (
          'invalid structure member: {0:s} unsupported condition').format(
              name or '<NAMELESS>')
      raise errors.DefinitionReaderError(definition_name, error_message)

    value = definition_values.get('value', None)
    values = definition_values.get('values', None)

    if None not in (value, values):
      error_message = (
          'invalid structure member: {0:s} value and values not allowed to '
          'be set at the same time').format(name or '<NAMELESS>')
      raise errors.DefinitionReaderError(definition_name, error_message)

    if value:
      values = [value]

    supported_values = None
    if values:
      supported_values = []
      for value in values:
        if isinstance(value, str):
          value = value.encode('ascii')

        supported_values.append(value)

    if type_indicator is not None:
      data_type_callback = self._DATA_TYPE_CALLBACKS.get(type_indicator, None)
      if data_type_callback:
        data_type_callback = getattr(self, data_type_callback, None)
      if not data_type_callback:
        error_message = 'unuspported data type definition: {0:s}.'.format(
            type_indicator)
        raise errors.DefinitionReaderError(name, error_message)

      try:
        data_type_definition = data_type_callback(
            definitions_registry, definition_values, name, is_member=True)
      except errors.DefinitionReaderError as exception:
        error_message = 'in: {0:s} {1:s}'.format(
            exception.name or '<NAMELESS>', exception.message)
        raise errors.DefinitionReaderError(definition_name, error_message)

      if condition or supported_values:
        definition_object = data_types.MemberDataTypeDefinition(
            name, data_type_definition, condition=condition,
            values=supported_values)
      else:
        definition_object = data_type_definition

    elif data_type is not None:
      data_type_definition = definitions_registry.GetDefinitionByName(
          data_type)
      if not data_type_definition:
        error_message = (
            'invalid structure member: {0:s} undefined data type: '
            '{1:s}').format(name or '<NAMELESS>', data_type)
        raise errors.DefinitionReaderError(definition_name, error_message)

      unsupported_definition_values = set(definition_values.keys()).difference(
          self._SUPPORTED_DEFINITION_VALUES_MEMBER_DATA_TYPE)
      if unsupported_definition_values:
        error_message = 'unsupported definition values: {0:s}'.format(
            ', '.join(unsupported_definition_values))
        raise errors.DefinitionReaderError(definition_name, error_message)

      aliases = definition_values.get('aliases', None)
      description = definition_values.get('description', None)

      definition_object = data_types.MemberDataTypeDefinition(
          name, data_type_definition, aliases=aliases, condition=condition,
          data_type=data_type, description=description, values=supported_values)

    return definition_object

  def _ReadPaddingDataTypeDefinition(
      self, definitions_registry, definition_values, definition_name,
      is_member=False):
    """Reads a padding data type definition.

    Args:
      definitions_registry (DataTypeDefinitionsRegistry): data type definitions
          registry.
      definition_values (dict[str, object]): definition values.
      definition_name (str): name of the definition.
      is_member (Optional[bool]): True if the data type definition is a member
          data type definition.

    Returns:
      PaddingtDefinition: padding definition.

    Raises:
      DefinitionReaderError: if the definitions values are missing or if
          the format is incorrect.
    """
    if not is_member:
      error_message = 'data type only supported as member'
      raise errors.DefinitionReaderError(definition_name, error_message)

    definition_object = self._ReadDataTypeDefinition(
        definitions_registry, definition_values, data_types.PaddingDefinition,
        definition_name, self._SUPPORTED_DEFINITION_VALUES_PADDING)

    alignment_size = definition_values.get('alignment_size', None)
    if not alignment_size:
      error_message = 'missing alignment_size'
      raise errors.DefinitionReaderError(definition_name, error_message)

    try:
      int(alignment_size)
    except ValueError:
      error_message = 'unuspported alignment size attribute: {0!s}'.format(
          alignment_size)
      raise errors.DefinitionReaderError(definition_name, error_message)

    if alignment_size not in (2, 4, 8, 16):
      error_message = 'unuspported alignment size value: {0!s}'.format(
          alignment_size)
      raise errors.DefinitionReaderError(definition_name, error_message)

    definition_object.alignment_size = alignment_size

    return definition_object

  def _ReadSemanticDataTypeDefinition(
      self, definitions_registry, definition_values, data_type_definition_class,
      definition_name, supported_definition_values):
    """Reads a semantic data type definition.

    Args:
      definitions_registry (DataTypeDefinitionsRegistry): data type definitions
          registry.
      definition_values (dict[str, object]): definition values.
      data_type_definition_class (str): data type definition class.
      definition_name (str): name of the definition.
      supported_definition_values (set[str]): names of the supported definition
          values.

    Returns:
      SemanticDataTypeDefinition: semantic data type definition.

    Raises:
      DefinitionReaderError: if the definitions values are missing or if
          the format is incorrect.
    """
    return self._ReadDataTypeDefinition(
        definitions_registry, definition_values, data_type_definition_class,
        definition_name, supported_definition_values)

  def _ReadSequenceDataTypeDefinition(
      self, definitions_registry, definition_values, definition_name,
      is_member=False):
    """Reads a sequence data type definition.

    Args:
      definitions_registry (DataTypeDefinitionsRegistry): data type definitions
          registry.
      definition_values (dict[str, object]): definition values.
      definition_name (str): name of the definition.
      is_member (Optional[bool]): True if the data type definition is a member
          data type definition.

    Returns:
      SequenceDefinition: sequence data type definition.

    Raises:
      DefinitionReaderError: if the definitions values are missing or if
          the format is incorrect.
    """
    if is_member:
      supported_definition_values = (
          self._SUPPORTED_DEFINITION_VALUES_ELEMENTS_MEMBER_DATA_TYPE)
    else:
      supported_definition_values = (
          self._SUPPORTED_DEFINITION_VALUES_ELEMENTS_DATA_TYPE)

    return self._ReadElementSequenceDataTypeDefinition(
        definitions_registry, definition_values, data_types.SequenceDefinition,
        definition_name, supported_definition_values)

  def _ReadStorageDataTypeDefinition(
      self, definitions_registry, definition_values, data_type_definition_class,
      definition_name, supported_attributes, is_member=False):
    """Reads a storage data type definition.

    Args:
      definitions_registry (DataTypeDefinitionsRegistry): data type definitions
          registry.
      definition_values (dict[str, object]): definition values.
      data_type_definition_class (str): data type definition class.
      definition_name (str): name of the definition.
      supported_attributes (set[str]): names of the supported attributes.
      is_member (Optional[bool]): True if the data type definition is a member
          data type definition.

    Returns:
      StorageDataTypeDefinition: storage data type definition.

    Raises:
      DefinitionReaderError: if the definitions values are missing or if
          the format is incorrect.
    """
    if is_member:
      supported_definition_values = (
          self._SUPPORTED_DEFINITION_VALUES_MEMBER_DATA_TYPE)
    else:
      supported_definition_values = (
          self._SUPPORTED_DEFINITION_VALUES_STORAGE_DATA_TYPE)

    definition_object = self._ReadDataTypeDefinition(
        definitions_registry, definition_values, data_type_definition_class,
        definition_name, supported_definition_values)

    attributes = definition_values.get('attributes', None)
    if attributes:
      unsupported_attributes = set(attributes.keys()).difference(
          supported_attributes)
      if unsupported_attributes:
        error_message = 'unsupported attributes: {0:s}'.format(
            ', '.join(unsupported_attributes))
        raise errors.DefinitionReaderError(definition_name, error_message)

      byte_order = attributes.get('byte_order', definitions.BYTE_ORDER_NATIVE)
      if byte_order not in definitions.BYTE_ORDERS:
        error_message = 'unsupported byte-order attribute: {0!s}'.format(
            byte_order)
        raise errors.DefinitionReaderError(definition_name, error_message)

      definition_object.byte_order = byte_order

    return definition_object

  def _ReadStreamDataTypeDefinition(
      self, definitions_registry, definition_values, definition_name,
      is_member=False):
    """Reads a stream data type definition.

    Args:
      definitions_registry (DataTypeDefinitionsRegistry): data type definitions
          registry.
      definition_values (dict[str, object]): definition values.
      definition_name (str): name of the definition.
      is_member (Optional[bool]): True if the data type definition is a member
          data type definition.

    Returns:
      StreamDefinition: stream data type definition.

    Raises:
      DefinitionReaderError: if the definitions values are missing or if
          the format is incorrect.
    """
    if is_member:
      supported_definition_values = (
          self._SUPPORTED_DEFINITION_VALUES_ELEMENTS_MEMBER_DATA_TYPE)
    else:
      supported_definition_values = (
          self._SUPPORTED_DEFINITION_VALUES_ELEMENTS_DATA_TYPE)

    return self._ReadElementSequenceDataTypeDefinition(
        definitions_registry, definition_values, data_types.StreamDefinition,
        definition_name, supported_definition_values)

  def _ReadStringDataTypeDefinition(
      self, definitions_registry, definition_values, definition_name,
      is_member=False):
    """Reads a string data type definition.

    Args:
      definitions_registry (DataTypeDefinitionsRegistry): data type definitions
          registry.
      definition_values (dict[str, object]): definition values.
      definition_name (str): name of the definition.
      is_member (Optional[bool]): True if the data type definition is a member
          data type definition.

    Returns:
      StringDefinition: string data type definition.

    Raises:
      DefinitionReaderError: if the definitions values are missing or if
          the format is incorrect.
    """
    if is_member:
      supported_definition_values = (
          self._SUPPORTED_DEFINITION_VALUES_STRING_MEMBER)
    else:
      supported_definition_values = self._SUPPORTED_DEFINITION_VALUES_STRING

    definition_object = self._ReadElementSequenceDataTypeDefinition(
        definitions_registry, definition_values, data_types.StringDefinition,
        definition_name, supported_definition_values)

    encoding = definition_values.get('encoding', None)
    if not encoding:
      error_message = 'missing encoding'
      raise errors.DefinitionReaderError(definition_name, error_message)

    definition_object.encoding = encoding

    return definition_object

  def _ReadStructureDataTypeDefinition(
      self, definitions_registry, definition_values, definition_name,
      is_member=False):
    """Reads a structure data type definition.

    Args:
      definitions_registry (DataTypeDefinitionsRegistry): data type definitions
          registry.
      definition_values (dict[str, object]): definition values.
      definition_name (str): name of the definition.
      is_member (Optional[bool]): True if the data type definition is a member
          data type definition.

    Returns:
      StructureDefinition: structure data type definition.

    Raises:
      DefinitionReaderError: if the definitions values are missing or if
          the format is incorrect.
    """
    if is_member:
      error_message = 'data type not supported as member'
      raise errors.DefinitionReaderError(definition_name, error_message)

    return self._ReadDataTypeDefinitionWithMembers(
        definitions_registry, definition_values, data_types.StructureDefinition,
        definition_name, supports_conditions=True)

  def _ReadStructureFamilyDataTypeDefinition(
      self, definitions_registry, definition_values, definition_name,
      is_member=False):
    """Reads a structure family data type definition.

    Args:
      definitions_registry (DataTypeDefinitionsRegistry): data type definitions
          registry.
      definition_values (dict[str, object]): definition values.
      definition_name (str): name of the definition.
      is_member (Optional[bool]): True if the data type definition is a member
          data type definition.

    Returns:
      StructureDefinition: structure data type definition.

    Raises:
      DefinitionReaderError: if the definitions values are missing or if
          the format is incorrect.
    """
    if is_member:
      error_message = 'data type not supported as member'
      raise errors.DefinitionReaderError(definition_name, error_message)

    unsupported_definition_values = set(definition_values.keys()).difference(
        self._SUPPORTED_DEFINITION_VALUES_STRUCTURE_FAMILY)
    if unsupported_definition_values:
      error_message = 'unsupported definition values: {0:s}'.format(
          ', '.join(unsupported_definition_values))
      raise errors.DefinitionReaderError(definition_name, error_message)

    base = definition_values.get('base', None)
    if not base:
      error_message = 'missing base'
      raise errors.DefinitionReaderError(definition_name, error_message)

    base_data_type_definition = definitions_registry.GetDefinitionByName(base)
    if not base_data_type_definition:
      error_message = 'undefined base: {0:s}.'.format(base)
      raise errors.DefinitionReaderError(definition_name, error_message)

    aliases = definition_values.get('aliases', None)
    description = definition_values.get('description', None)
    urls = definition_values.get('urls', None)

    definition_object = data_types.StructureFamilyDefinition(
        definition_name, base_data_type_definition, aliases=aliases,
        description=description, urls=urls)

    members = definition_values.get('members', None)
    if not members:
      error_message = 'missing members'
      raise errors.DefinitionReaderError(definition_name, error_message)

    for member in members:
      member_data_type_definition = definitions_registry.GetDefinitionByName(
          member)
      if not member_data_type_definition:
        error_message = 'undefined member: {0:s}.'.format(member)
        raise errors.DefinitionReaderError(definition_name, error_message)

      try:
        definition_object.AddMemberDefinition(member_data_type_definition)
      except KeyError as exception:
        error_message = '{0!s}'.format(exception)
        raise errors.DefinitionReaderError(definition_name, error_message)

    return definition_object

  def _ReadStructureGroupDataTypeDefinition(
      self, definitions_registry, definition_values, definition_name,
      is_member=False):
    """Reads a structure group data type definition.

    Args:
      definitions_registry (DataTypeDefinitionsRegistry): data type definitions
          registry.
      definition_values (dict[str, object]): definition values.
      definition_name (str): name of the definition.
      is_member (Optional[bool]): True if the data type definition is a member
          data type definition.

    Returns:
      StructureDefinition: structure data type definition.

    Raises:
      DefinitionReaderError: if the definitions values are missing or if
          the format is incorrect.
    """
    if is_member:
      error_message = 'data type not supported as member'
      raise errors.DefinitionReaderError(definition_name, error_message)

    unsupported_definition_values = set(definition_values.keys()).difference(
        self._SUPPORTED_DEFINITION_VALUES_STRUCTURE_GROUP)
    if unsupported_definition_values:
      error_message = 'unsupported definition values: {0:s}'.format(
          ', '.join(unsupported_definition_values))
      raise errors.DefinitionReaderError(definition_name, error_message)

    base = definition_values.get('base', None)
    if not base:
      error_message = 'missing base'
      raise errors.DefinitionReaderError(definition_name, error_message)

    base_data_type_definition = definitions_registry.GetDefinitionByName(base)
    if not base_data_type_definition:
      error_message = 'undefined base: {0:s}.'.format(base)
      raise errors.DefinitionReaderError(definition_name, error_message)

    identifier = definition_values.get('identifier', None)
    if not identifier:
      error_message = 'missing identifier'
      raise errors.DefinitionReaderError(definition_name, error_message)

    aliases = definition_values.get('aliases', None)
    description = definition_values.get('description', None)
    urls = definition_values.get('urls', None)

    definition_object = data_types.StructureGroupDefinition(
        definition_name, base_data_type_definition, identifier,
        aliases=aliases, description=description, urls=urls)

    members = definition_values.get('members', None)
    if not members:
      error_message = 'missing members'
      raise errors.DefinitionReaderError(definition_name, error_message)

    for member in members:
      member_data_type_definition = definitions_registry.GetDefinitionByName(
          member)
      if not member_data_type_definition:
        error_message = 'undefined member: {0:s}.'.format(member)
        raise errors.DefinitionReaderError(definition_name, error_message)

      member_names = [
          structure_member.name
          for structure_member in member_data_type_definition.members]

      if definition_object.identifier not in member_names:
        error_message = 'member: {0:s} has no identifier: {1:s}.'.format(
            member, definition_object.identifier)
        raise errors.DefinitionReaderError(definition_name, error_message)

      try:
        definition_object.AddMemberDefinition(member_data_type_definition)
      except KeyError as exception:
        error_message = '{0!s}'.format(exception)
        raise errors.DefinitionReaderError(definition_name, error_message)

    return definition_object

  def _ReadUnionDataTypeDefinition(
      self, definitions_registry, definition_values, definition_name,
      is_member=False):
    """Reads an union data type definition.

    Args:
      definitions_registry (DataTypeDefinitionsRegistry): data type definitions
          registry.
      definition_values (dict[str, object]): definition values.
      definition_name (str): name of the definition.
      is_member (Optional[bool]): True if the data type definition is a member
          data type definition.

    Returns:
      UnionDefinition: union data type definition.

    Raises:
      DefinitionReaderError: if the definitions values are missing or if
          the format is incorrect.
    """
    return self._ReadDataTypeDefinitionWithMembers(
        definitions_registry, definition_values, data_types.UnionDefinition,
        definition_name, supports_conditions=False)

  def _ReadUUIDDataTypeDefinition(
      self, definitions_registry, definition_values, definition_name,
      is_member=False):
    """Reads an UUID data type definition.

    Args:
      definitions_registry (DataTypeDefinitionsRegistry): data type definitions
          registry.
      definition_values (dict[str, object]): definition values.
      definition_name (str): name of the definition.
      is_member (Optional[bool]): True if the data type definition is a member
          data type definition.

    Returns:
      UUIDDataTypeDefinition: UUID data type definition.

    Raises:
      DefinitionReaderError: if the definitions values are missing or if
          the format is incorrect.
    """
    return self._ReadFixedSizeDataTypeDefinition(
        definitions_registry, definition_values,
        data_types.UUIDDefinition, definition_name,
        self._SUPPORTED_ATTRIBUTES_FIXED_SIZE_DATA_TYPE, default_size=16,
        is_member=is_member, supported_size_values=(16, ))


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
      error_message = 'missing definition values'
      raise errors.DefinitionReaderError(None, error_message)

    name = definition_values.get('name', None)
    if not name:
      error_message = 'missing name'
      raise errors.DefinitionReaderError(None, error_message)

    type_indicator = definition_values.get('type', None)
    if not type_indicator:
      error_message = 'invalid definition missing type'
      raise errors.DefinitionReaderError(name, error_message)

    data_type_callback = self._DATA_TYPE_CALLBACKS.get(type_indicator, None)
    if data_type_callback:
      data_type_callback = getattr(self, data_type_callback, None)
    if not data_type_callback:
      error_message = 'unuspported data type definition: {0:s}.'.format(
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
    name = yaml_definition.get('name', None)
    if name:
      error_location = 'in: {0:s}'.format(name or '<NAMELESS>')
    elif last_definition_object:
      error_location = 'after: {0:s}'.format(last_definition_object.name)
    else:
      error_location = 'at start'

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
          error_message = '{0:s} Missing definition object.'.format(
              error_location)
          raise errors.FormatError(error_message)

        definitions_registry.RegisterDefinition(definition_object)
        last_definition_object = definition_object

    except errors.DefinitionReaderError as exception:
      error_message = 'in: {0:s} {1:s}'.format(
          exception.name or '<NAMELESS>', exception.message)
      raise errors.FormatError(error_message)

    except (yaml.reader.ReaderError, yaml.scanner.ScannerError) as exception:
      error_location = self._GetFormatErrorLocation({}, last_definition_object)
      error_message = '{0:s} {1!s}'.format(error_location, exception)
      raise errors.FormatError(error_message)
