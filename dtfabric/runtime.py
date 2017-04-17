# -*- coding: utf-8 -*-
"""Run-time objects."""

try:
  import __builtin__ as builtins
except ImportError:
  import builtins

import abc
import keyword
import struct
import uuid

from dtfabric import data_types
from dtfabric import definitions
from dtfabric import errors
from dtfabric import py2to3


# TODO: add ConstantMap.
# TODO: add EnumerationMap.
# TODO: add FormatMap.
# TODO: complete SequenceMap.
# TODO: complete StructureMap.


class ByteStreamOperation(object):
  """Byte stream operation."""

  @abc.abstractmethod
  def ReadFrom(self, byte_stream):
    """Read values from a byte stream.

    Args:
      byte_stream (bytes): byte stream.

    Returns:
      tuple[object, ...]: values copies from the byte stream.
    """


class StructOperation(ByteStreamOperation):
  """Python struct-base byte stream operation."""

  def __init__(self, format_string):
    """Initializes a Python struct-base byte stream operation.

    Args:
      format_string (str): format string as used by Python struct.

    Raises:
      FormatError: if the struct operation cannot be determed from the data
          type definition.
    """
    try:
      struct_object = struct.Struct(format_string)
    except (TypeError, struct.error) as exception:
      raise errors.FormatError((
          u'Unable to create struct object from data type definition '
          u'with error: {0!s}').format(exception))

    super(StructOperation, self).__init__()
    self._struct = struct_object
    self._struct_format_string = format_string

  def ReadFrom(self, byte_stream):
    """Read values from a byte stream.

    Args:
      byte_stream (bytes): byte stream.

    Returns:
      tuple[object, ...]: values copies from the byte stream.

    Raises:
      IOError: if byte stream cannot be read.
    """
    try:
      return self._struct.unpack_from(byte_stream)
    except (TypeError, struct.error) as exception:
      raise IOError(u'Unable to read byte stream with error: {0!s}'.format(
          exception))


class StructureValuesClassFactory(object):
  """Structure values class factory."""

  _CLASS_TEMPLATE = u'\n'.join([
      u'class {type_name:s}(object):',
      u'  """{type_description:s}.',
      u'',
      u'  Attributes:',
      u'{class_attributes_description:s}',
      u'  """',
      u'',
      u'  def __init__(self, {init_arguments:s}):',
      u'    """Initializes an instance of {type_name:s}."""',
      u'    super({type_name:s}, self).__init__()',
      u'{instance_attributes:s}',
      u''])

  _PYTHON_NATIVE_TYPES = {
      definitions.TYPE_INDICATOR_BOOLEAN: u'bool',
      definitions.TYPE_INDICATOR_CHARACTER: u'str',
      definitions.TYPE_INDICATOR_FLOATING_POINT: u'float',
      definitions.TYPE_INDICATOR_INTEGER: u'int',
      definitions.TYPE_INDICATOR_UUID: u'uuid.UUID'}

  @classmethod
  def _CreateClassTemplate(cls, data_type_definition):
    """Creates the class template.

    Args:
      data_type_definition (DataTypeDefinition): data type definition.

    Returns:
      str: class template.
    """
    type_name = data_type_definition.name

    type_description = data_type_definition.description or type_name
    while type_description.endswith(u'.'):
      type_description = type_description[:-1]

    class_attributes_description = []
    init_arguments = []
    instance_attributes = []

    for member_definition in data_type_definition.members:
      attribute_name = member_definition.name

      description = member_definition.description or attribute_name
      while description.endswith(u'.'):
        description = description[:-1]

      member_data_type = getattr(member_definition, u'member_data_type', u'')
      if isinstance(member_definition, data_types.StructureMemberDefinition):
        member_definition = member_definition.member_data_type_definition

      member_type_indicator = member_definition.TYPE_INDICATOR
      if member_type_indicator == definitions.TYPE_INDICATOR_SEQUENCE:
        element_type_indicator = member_definition.element_data_type
        member_type_indicator = u'tuple[{0:s}]'.format(element_type_indicator)
      else:
        member_type_indicator = cls._PYTHON_NATIVE_TYPES.get(
            member_type_indicator, member_data_type)

      argument = u'{0:s}=None'.format(attribute_name)

      definition = u'    self.{0:s} = {0:s}'.format(attribute_name)

      description = u'    {0:s} ({1:s}): {2:s}.'.format(
          attribute_name, member_type_indicator, description)

      class_attributes_description.append(description)
      init_arguments.append(argument)
      instance_attributes.append(definition)

    class_attributes_description = u'\n'.join(
        sorted(class_attributes_description))
    init_arguments = u', '.join(sorted(init_arguments))
    instance_attributes = u'\n'.join(sorted(instance_attributes))

    template_values = {
        u'class_attributes_description': class_attributes_description,
        u'init_arguments': init_arguments,
        u'instance_attributes': instance_attributes,
        u'type_description': type_description,
        u'type_name': type_name}

    return cls._CLASS_TEMPLATE.format(**template_values)

  @classmethod
  def _IsIdentifier(cls, string):
    """Checks if a string contains an identifier.

    Args:
      string (str): string to check.

    Returns:
      bool: True if the string contains an identifier, False otherwise.
    """
    return (
        string and not string[0].isdigit() and
        all(character.isalnum() or character == '_' for character in string))

  @classmethod
  def _ValidateDataTypeDefinition(cls, data_type_definition):
    """Validates the data type defintion.

    Args:
      data_type_definition (DataTypeDefinition): data type definition.

    Raises:
      ValueError: if the data type definition is not considered valid.
    """
    if not cls._IsIdentifier(data_type_definition.name):
      raise ValueError(
          u'Data type definition name: {0!s} not a valid identifier'.format(
              data_type_definition.name))

    if keyword.iskeyword(data_type_definition.name):
      raise ValueError(
          u'Data type definition name: {0!s} matches keyword'.format(
              data_type_definition.name))

    defined_attribute_names = set()

    for attribute_name in data_type_definition.GetAttributeNames():
      if not cls._IsIdentifier(attribute_name):
        raise ValueError(u'Attribute name: {0!s} not a valid identifier'.format(
            attribute_name))

      if attribute_name.startswith(u'_'):
        raise ValueError(u'Attribute name: {0!s} starts with underscore'.format(
            attribute_name))

      if keyword.iskeyword(attribute_name):
        raise ValueError(u'Attribute name: {0!s} matches keyword'.format(
            attribute_name))

      if attribute_name in defined_attribute_names:
        raise ValueError(u'Attribute name: {0!s} already defined'.format(
            attribute_name))

      defined_attribute_names.add(attribute_name)

  @classmethod
  def CreateClass(cls, data_type_definition):
    """Creates a new structure values class.

    Args:
      data_type_definition (DataTypeDefinition): data type definition.

    Returns:
      class: structure values class.
    """
    cls._ValidateDataTypeDefinition(data_type_definition)

    class_definition = cls._CreateClassTemplate(data_type_definition)

    namespace = {
        u'__builtins__' : {
            u'object': builtins.object,
            u'super': builtins.super},
        u'__name__': u'{0:s}'.format(data_type_definition.name)}

    exec(class_definition, namespace)  # pylint: disable=exec-used

    return namespace[data_type_definition.name]


class DataTypeMapContext(object):
  """Data type map context."""

  def __init__(self, value=None):
    """Initializes a data type map context.

    Args:
      value (object): value.
    """
    super(DataTypeMapContext, self).__init__()
    self.byte_size = None
    self.value = value



class DataTypeMap(object):
  """Data type map."""

  def __init__(self, data_type_definition):
    """Initializes a data type map.

    Args:
      data_type_definition (DataTypeDefinition): data type definition.

    Raises:
      FormatError: if the data type map cannot be determed from the data
          type definition.
    """
    super(DataTypeMap, self).__init__()
    self._data_type_definition = data_type_definition

  def _GetByteStreamOperation(self, data_type_definition):
    """Retrieves the byte stream operation.

    Args:
      data_type_definition (DataTypeDefinition): data type definition.

    Returns:
      ByteStreamOperation: byte stream operation or None if unable to determine.

    Raises:
      FormatError: if the byte stream operation cannot be determed from the
          data type definition.
    """
    byte_order_string = self._GetStructByteOrderString(data_type_definition)
    format_string = self._GetStructFormatString(data_type_definition)
    format_string = u''.join([byte_order_string, format_string])

    return StructOperation(format_string)

  def _GetStructByteOrderString(self, data_type_definition):
    """Retrieves the Python struct format string.

    Args:
      data_type_definition (DataTypeDefinition): data type definition.

    Returns:
      str: format string as used by Python struct or None if format string
          cannot be determined.

    Raises:
      FormatError: if the struct byte order string cannot be determed from
          the data type definition.
    """
    if not data_type_definition:
      raise errors.FormatError(u'Missing data type definition')

    error_string = u''

    try:
      byte_order_string = data_type_definition.GetStructByteOrderString()
    except (AttributeError, TypeError) as exception:
      byte_order_string = None
      error_string = u' with error: {0!s}'.format(exception)

    if not byte_order_string:
      raise errors.FormatError(
          u'Unable to determine byte order string{0:s}'.format(error_string))

    return byte_order_string

  def _GetStructFormatString(self, data_type_definition):
    """Retrieves the Python struct format string.

    Args:
      data_type_definition (DataTypeDefinition): data type definition.

    Returns:
      str: format string as used by Python struct or None if format string
          cannot be determined.

    Raises:
      FormatError: if the struct format string cannot be determed from
          the data type definition.
    """
    if not data_type_definition:
      raise errors.FormatError(u'Missing data type definition')

    error_string = u''

    try:
      format_string = data_type_definition.GetStructFormatString()
    except (AttributeError, TypeError) as exception:
      format_string = None
      error_string = u' with error: {0!s}'.format(exception)

    if not format_string:
      raise errors.FormatError(
          u'Unable to determine format string{0:s}'.format(error_string))

    return format_string

  @abc.abstractmethod
  def MapByteStream(self, byte_stream, context=None, **unused_kwargs):
    """Maps the data type on a byte stream.

    Args:
      byte_stream (bytes): byte stream.
      context (Optional[DataTypeMapContext]): data type map context.

    Returns:
      object: mapped value.

    Raises:
      MappingError: if the data type definition cannot be mapped on
          the byte stream.
    """


class PrimitiveDataTypeMap(DataTypeMap):
  """Primitive data type map."""

  def __init__(self, data_type_definition):
    """Initializes a data type map.

    Args:
      data_type_definition (DataTypeDefinition): data type definition.

    Raises:
      FormatError: if the data type map cannot be determed from the data
          type definition.
    """
    super(PrimitiveDataTypeMap, self).__init__(data_type_definition)
    self._operation = self._GetByteStreamOperation(data_type_definition)

  def MapByteStream(self, byte_stream, context=None, **unused_kwargs):
    """Maps the data type on a byte stream.

    Args:
      byte_stream (bytes): byte stream.
      context (Optional[DataTypeMapContext]): data type map context.

    Returns:
      object: mapped value.

    Raises:
      MappingError: if the data type definition cannot be mapped on
          the byte stream.
    """
    if context:
      context.byte_size = self._data_type_definition.GetByteSize()

    try:
      struct_tuple = self._operation.ReadFrom(byte_stream)
      return self.MapValue(*struct_tuple)

    except Exception as exception:
      raise errors.MappingError(exception)

  def MapValue(self, value):
    """Maps the data type on a value.

    Args:
      value (object): value.

    Returns:
      object: mapped value.

    Raises:
      ValueError: if the data type definition cannot be mapped on the value.
    """
    return value


class BooleanMap(PrimitiveDataTypeMap):
  """Boolen data type map."""

  def __init__(self, data_type_definition):
    """Initializes a data type map.

    Args:
      data_type_definition (DataTypeDefinition): data type definition.

    Raises:
      FormatError: if the data type map cannot be determed from the data
          type definition.
    """
    if (data_type_definition.false_value is None and
        data_type_definition.true_value is None):
      raise errors.FormatError(
          u'Boolean data type has no True or False values.')

    super(BooleanMap, self).__init__(data_type_definition)

  def MapValue(self, value):
    """Maps the data type on a value.

    Args:
      value (object): value.

    Returns:
      bool: mapped value.

    Raises:
      ValueError: if the data type definition cannot be mapped on the value.
    """
    if self._data_type_definition.false_value == value:
      return False

    if self._data_type_definition.true_value == value:
      return True

    if self._data_type_definition.false_value is None:
      return False

    if self._data_type_definition.true_value is None:
      return True

    raise ValueError(u'No matching True and False values')


class CharacterMap(PrimitiveDataTypeMap):
  """Character data type map."""

  def MapValue(self, value):
    """Maps the data type on a value.

    Args:
      value (object): value.

    Returns:
      str: mapped value.

    Raises:
      ValueError: if the data type definition cannot be mapped on the value.
    """
    return py2to3.UNICHR(value)


class FloatingPointMap(PrimitiveDataTypeMap):
  """Floating-point data type map."""


class IntegerMap(PrimitiveDataTypeMap):
  """Integer data type map."""


class SequenceMap(DataTypeMap):
  """Sequence data type map."""

  def __init__(self, data_type_definition):
    """Initializes a data type map.

    Args:
      data_type_definition (DataTypeDefinition): data type definition.
    """
    element_data_type_definition = self._GetElementDataTypeDefinition(
        data_type_definition)

    data_type_map = DataTypeMapFactory.CreateDataTypeMapByType(
        element_data_type_definition)

    if (element_data_type_definition.IsComposite() or
        data_type_definition.number_of_elements_expression):
      map_byte_stream = self._CompositeMapByteStream
      operation = None
    else:
      map_byte_stream = self._PrimitiveMapByteStream
      operation = self._GetByteStreamOperation(data_type_definition)

    super(SequenceMap, self).__init__(data_type_definition)
    self._data_type_map = data_type_map
    self._map_byte_stream = map_byte_stream
    self._operation = operation

  def _CompositeMapByteStream(self, byte_stream, context=None, **unused_kwargs):
    """Maps a sequence of composite data types on a byte stream.

    Args:
      byte_stream (bytes): byte stream.
      context (Optional[DataTypeMapContext]): data type map context.

    Returns:
      tuple[object, ...]: mapped values.

    Raises:
      MappingError: if the data type definition cannot be mapped on
          the byte stream.
    """
    if self._data_type_definition.number_of_elements:
      number_of_elements = self._data_type_definition.number_of_elements
    else:
      expression = self._data_type_definition.number_of_elements_expression
      namespace = {u'__builtins__' : {}}
      if context and context.value:
        namespace[type(context.value).__name__] = context.value

      try:
        number_of_elements = eval(expression, namespace)  # pylint: disable=eval-used
      except Exception as exception:
        raise errors.MappingError(
            u'Unable to determine number of elements with error: {0!s}'.format(
                exception))

    if number_of_elements < 0:
      raise errors.MappingError(
          u'Invalid number of elements: {0:d}'.format(number_of_elements))

    values = []

    subcontext = DataTypeMapContext()

    byte_stream_offset = 0
    for _ in range(number_of_elements):
      try:
        value = self._data_type_map.MapByteStream(
            byte_stream[byte_stream_offset:], context=subcontext)
        values.append(value)

      except Exception as exception:
        raise errors.MappingError((
            u'Unable to read byte stream at offset: {0:d} with error: '
            u'{1!s}').format(byte_stream_offset, exception))

      byte_stream_offset += subcontext.byte_size

    if context:
      context.byte_size = byte_stream_offset

    return tuple(values)

  def _GetElementDataTypeDefinition(self, data_type_definition):
    """Retrieves the element data type definition.

    Args:
      data_type_definition (DataTypeDefinition): data type definition.

    Returns:
      DataTypeDefinition: element data type definition.

    Raises:
      FormatError: if the data type map cannot be determed from the data
          type definition.
    """
    if not data_type_definition:
      raise errors.FormatError(u'Missing data type definition')

    element_data_type_definition = getattr(
        data_type_definition, u'element_data_type_definition', None)
    if not element_data_type_definition:
      raise errors.FormatError(
          u'Invalid data type definition missing element')

    return element_data_type_definition

  def _PrimitiveMapByteStream(self, byte_stream, context=None, **unused_kwargs):
    """Maps a data type sequence on a byte stream.

    Args:
      byte_stream (bytes): byte stream.
      context (Optional[DataTypeMapContext]): data type map context.

    Returns:
      tuple[object, ...]: mapped values.

    Raises:
      MappingError: if the data type definition cannot be mapped on
          the byte stream.
    """
    if context:
      context.byte_size = self._data_type_definition.GetByteSize()

    try:
      struct_tuple = self._operation.ReadFrom(byte_stream)
      return tuple(map(self._data_type_map.MapValue, struct_tuple))

    except Exception as exception:
      raise errors.MappingError(exception)

  def MapByteStream(self, byte_stream, **kwargs):
    """Maps the data type on a byte stream.

    Args:
      byte_stream (bytes): byte stream.

    Returns:
      tuple[object, ...]: mapped values.

    Raises:
      MappingError: if the data type definition cannot be mapped on
          the byte stream.
    """
    return self._map_byte_stream(byte_stream, **kwargs)


class StructureMap(DataTypeMap):
  """Structure data type map."""

  def __init__(self, data_type_definition):
    """Initializes a structure data type map.

    Args:
      data_type_definition (DataTypeDefinition): data type definition.
    """
    structure_values_class = StructureValuesClassFactory.CreateClass(
        data_type_definition)

    data_type_map_cache = {}
    data_type_maps = self._GetMemberDataTypeMaps(
        data_type_definition, data_type_map_cache)

    if self._CheckCompositeMap(data_type_definition):
      map_byte_stream = self._CompositeMapByteStream
      operation = None
    else:
      map_byte_stream = self._PrimitiveMapByteStream
      operation = self._GetByteStreamOperation(data_type_definition)

    super(StructureMap, self).__init__(data_type_definition)
    self._attribute_names = data_type_definition.GetAttributeNames()
    self._data_type_map_cache = data_type_map_cache
    self._data_type_maps = data_type_maps
    self._map_byte_stream = map_byte_stream
    self._operation = operation
    self._structure_values_class = structure_values_class

  def _CheckCompositeMap(self, data_type_definition):
    """Determines if the data type definition needs a composite map.

    Args:
      data_type_definition (DataTypeDefinition): structure data type definition.

    Returns:
      bool: True if a composite map is needed, False otherwise.

    Raises:
      FormatError: if a composite map is needed cannot be determed from the
          data type definition.
    """
    if not data_type_definition:
      raise errors.FormatError(u'Missing data type definition')

    members = getattr(data_type_definition, u'members', None)
    if not members:
      raise errors.FormatError(u'Invalid data type definition missing members')

    structure_byte_order = data_type_definition.byte_order

    is_composite_map = False
    last_member_byte_order = definitions.BYTE_ORDER_NATIVE

    for member_definition in members:
      if isinstance(member_definition, data_types.StructureMemberDefinition):
        member_definition = member_definition.member_data_type_definition

      if member_definition.IsComposite():
        is_composite_map = True
        continue

      member_byte_order = member_definition.byte_order
      if (structure_byte_order != definitions.BYTE_ORDER_NATIVE and
          structure_byte_order != member_byte_order):
        raise errors.FormatError((
            u'Contficting byte-order definitions in structure: {0:s} and '
            u'member: {1:s}').format(
                data_type_definition.name, member_definition.name))

      last_member_byte_order = member_byte_order

    return is_composite_map

  def _CompositeMapByteStream(self, byte_stream, context=None, **unused_kwargs):
    """Maps a sequence of composite data types on a byte stream.

    Args:
      byte_stream (bytes): byte stream.
      context (Optional[DataTypeMapContext]): data type map context.

    Returns:
      object: mapped value.

    Raises:
      MappingError: if the data type definition cannot be mapped on
          the byte stream.
    """
    structure_values = self._structure_values_class()

    subcontext = DataTypeMapContext(value=structure_values)

    byte_stream_offset = 0
    for index in range(len(self._attribute_names)):
      attribute_name = self._attribute_names[index]
      data_type_map = self._data_type_maps[index]

      try:
        value = data_type_map.MapByteStream(
            byte_stream[byte_stream_offset:], context=subcontext)
        setattr(structure_values, attribute_name, value)

      except Exception as exception:
        raise errors.MappingError((
            u'Unable to read byte stream at offset: {0:d} with error: '
            u'{1!s}').format(byte_stream_offset, exception))

      byte_stream_offset += subcontext.byte_size

    if context:
      context.byte_size = byte_stream_offset

    return structure_values

  def _GetByteStreamOperation(self, data_type_definition):
    """Retrieves the byte stream operation.

    Args:
      data_type_definition (DataTypeDefinition): data type definition.

    Returns:
      ByteStreamOperation: byte stream operation or None if unable to determine.

    Raises:
      FormatError: if the byte stream operation cannot be determed from the
          data type definition.
    """
    if not data_type_definition:
      raise errors.FormatError(u'Missing data type definition')

    members = getattr(data_type_definition, u'members', None)
    if not members:
      raise errors.FormatError(u'Invalid data type definition missing members')

    byte_order_string = self._GetStructByteOrderString(data_type_definition)
    format_string = u''.join([
        member_definition.GetStructFormatString()
        for member_definition in members])
    format_string = u''.join([byte_order_string, format_string])

    return StructOperation(format_string)

  def _GetMemberDataTypeMaps(self, data_type_definition, data_type_map_cache):
    """Retrieves the member data type maps.

    Args:
      data_type_definition (DataTypeDefinition): data type definition.
      data_type_map_cache (dict[str, DataTypeMap]): cached data type maps.

    Returns:
      list[DataTypeMap]: member data type maps.

    Raises:
      FormatError: if the data type maps cannot be determed from the data
          type definition.
    """
    if not data_type_definition:
      raise errors.FormatError(u'Missing data type definition')

    members = getattr(data_type_definition, u'members', None)
    if not members:
      raise errors.FormatError(u'Invalid data type definition missing members')

    data_type_maps = []

    for member_definition in members:
      if isinstance(member_definition, data_types.StructureMemberDefinition):
        member_definition = member_definition.member_data_type_definition

      if member_definition.name not in data_type_map_cache:
        data_type_map = DataTypeMapFactory.CreateDataTypeMapByType(
            member_definition)
        data_type_map_cache[member_definition.name] = data_type_map

      data_type_maps.append(data_type_map_cache[member_definition.name])

    return data_type_maps

  def _PrimitiveMapByteStream(self, byte_stream, context=None, **unused_kwargs):
    """Maps a data type sequence on a byte stream.

    Args:
      byte_stream (bytes): byte stream.
      context (Optional[DataTypeMapContext]): data type map context.

    Returns:
      object: mapped value.

    Raises:
      MappingError: if the data type definition cannot be mapped on
          the byte stream.
    """
    if context:
      context.byte_size = self._data_type_definition.GetByteSize()

    try:
      struct_tuple = self._operation.ReadFrom(byte_stream)
      values = [
          self._data_type_maps[index].MapValue(value)
          for index, value in enumerate(struct_tuple)]
      return self._structure_values_class(*values)

    except Exception as exception:
      raise errors.MappingError(exception)

  def MapByteStream(self, byte_stream, **kwargs):
    """Maps the data type on a byte stream.

    Args:
      byte_stream (bytes): byte stream.
      context (Optional[object]): context.

    Returns:
      object: mapped value.

    Raises:
      MappingError: if the data type definition cannot be mapped on
          the byte stream.
    """
    return self._map_byte_stream(byte_stream, **kwargs)


class UUIDMap(DataTypeMap):
  """UUID (or GUID) data type map."""

  def __init__(self, data_type_definition):
    """Initializes a data type map.

    Args:
      data_type_definition (DataTypeDefinition): data type definition.

    Raises:
      FormatError: if the data type map cannot be determed from the data
          type definition.
    """
    super(UUIDMap, self).__init__(data_type_definition)
    self._operation = self._GetByteStreamOperation(data_type_definition)

  def MapByteStream(self, byte_stream, context=None, **unused_kwargs):
    """Maps the data type on a byte stream.

    Args:
      byte_stream (bytes): byte stream.
      context (Optional[DataTypeMapContext]): data type map context.

    Returns:
      uuid.UUID: mapped value.

    Raises:
      MappingError: if the data type definition cannot be mapped on
          the byte stream.
    """
    if context:
      context.byte_size = self._data_type_definition.GetByteSize()

    try:
      struct_tuple = self._operation.ReadFrom(byte_stream)
      uuid_string = (
          u'{{{0:08x}-{1:04x}-{2:04x}-{3:02x}{4:02x}-'
          u'{5:02x}{6:02x}{7:02x}{8:02x}{9:02x}{10:02x}}}').format(
              *struct_tuple)
      return uuid.UUID(uuid_string)

    except Exception as exception:
      raise errors.MappingError(exception)


class DataTypeMapFactory(object):
  """Factory for data type maps."""

  # TODO: add support for definitions.TYPE_INDICATOR_CONSTANT
  # TODO: add support for definitions.TYPE_INDICATOR_ENUMERATION
  # TODO: add support for definitions.TYPE_INDICATOR_FORMAT

  _MAP_PER_DEFINITION = {
      definitions.TYPE_INDICATOR_BOOLEAN: BooleanMap,
      definitions.TYPE_INDICATOR_CHARACTER: CharacterMap,
      definitions.TYPE_INDICATOR_FLOATING_POINT: FloatingPointMap,
      definitions.TYPE_INDICATOR_INTEGER: IntegerMap,
      definitions.TYPE_INDICATOR_SEQUENCE: SequenceMap,
      definitions.TYPE_INDICATOR_STRUCTURE: StructureMap,
      definitions.TYPE_INDICATOR_UUID: UUIDMap}

  def __init__(self, definitions_registry):
    """Initializes a data type maps factory.

    Args:
      definitions_registry (DataTypeDefinitionsRegistry): data type definitions
          registry.
    """
    super(DataTypeMapFactory, self).__init__()
    self._definitions_registry = definitions_registry

  def CreateDataTypeMap(self, definition_name):
    """Creates a specific data type map by name.

    Args:
      definition_name (str): name of the data type definition.

    Returns:
      DataTypeMap: data type map or None if the date type definition
          is not available.
    """
    data_type_definition = self._definitions_registry.GetDefinitionByName(
        definition_name)
    if not data_type_definition:
      return

    return DataTypeMapFactory.CreateDataTypeMapByType(data_type_definition)

  @classmethod
  def CreateDataTypeMapByType(cls, data_type_definition):
    """Creates a specific data type map by type indicator.

    Args:
      data_type_definition (DataTypeDefinition): data type definition.

    Returns:
      DataTypeMap: data type map or None if the date type definition
          is not available.
    """
    data_type_map_class = cls._MAP_PER_DEFINITION.get(
        data_type_definition.TYPE_INDICATOR, None)
    if not data_type_map_class:
      return

    return data_type_map_class(data_type_definition)
