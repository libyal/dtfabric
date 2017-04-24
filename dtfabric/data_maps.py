# -*- coding: utf-8 -*-
"""Data type maps."""

import abc
import uuid

from dtfabric import byte_operations
from dtfabric import data_types
from dtfabric import definitions
from dtfabric import errors
from dtfabric import py2to3
from dtfabric import runtime


# TODO: add ConstantMap.
# TODO: add EnumerationMap.
# TODO: add FormatMap.


class DataTypeMapContext(object):
  """Data type map context.

  Attributes:
    byte_size (int): byte size.
    values (dict[str, object]): values per name.
  """

  def __init__(self, values=None):
    """Initializes a data type map context.

    Args:
      values (dict[str, object]): values per name.
    """
    super(DataTypeMapContext, self).__init__()
    self.byte_size = None
    self.values = values or {}


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

    return byte_operations.StructOperation(format_string)

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

  def GetByteSize(self):
    """Retrieves the byte size of the data type map.

    Returns:
      int: data type size in bytes or None if size cannot be determined.
    """
    return self._data_type_definition.GetByteSize()

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
      map_byte_stream = self._LinearMapByteStream
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
      namespace = {}
      if context and context.values:
        namespace.update(context.values)
      # Make sure __builtins__ contains an empty dictionary.
      namespace[u'__builtins__'] = {}

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
      FormatError: if the element data type cannot be determed from the data
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

  def _LinearMapByteStream(self, byte_stream, context=None, **unused_kwargs):
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


class StreamMap(DataTypeMap):
  """Stream data type map."""

  def __init__(self, data_type_definition):
    """Initializes a data type map.

    Args:
      data_type_definition (DataTypeDefinition): data type definition.

    Raises:
      FormatError: if the data type map cannot be determed from the data
          type definition.
    """
    element_data_type_definition = self._GetElementDataTypeDefinition(
        data_type_definition)

    if element_data_type_definition.IsComposite():
      raise errors.FormatError(u'Unsupported composite element data type')

    super(StreamMap, self).__init__(data_type_definition)

  def _GetElementDataTypeDefinition(self, data_type_definition):
    """Retrieves the element data type definition.

    Args:
      data_type_definition (DataTypeDefinition): data type definition.

    Returns:
      DataTypeDefinition: element data type definition.

    Raises:
      FormatError: if the element data type cannot be determed from the data
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

  def MapByteStream(self, byte_stream, context=None, **kwargs):
    """Maps the data type on a byte stream.

    Args:
      byte_stream (bytes): byte stream.
      context (Optional[DataTypeMapContext]): data type map context.

    Returns:
      tuple[object, ...]: mapped values.

    Raises:
      MappingError: if the data type definition cannot be mapped on
          the byte stream.
    """
    try:
      byte_stream_size = len(byte_stream)

    except Exception as exception:
      raise errors.MappingError(exception)

    byte_size = self._data_type_definition.GetByteSize()

    if byte_stream_size < byte_size:
      raise errors.MappingError(
          u'Byte stream too small requested: {0:s} available: {1:d}'.format(
              byte_stream, byte_stream_size))

    if context:
      context.byte_size = byte_size

    return byte_stream[:byte_size]


class StructureMap(DataTypeMap):
  """Structure data type map."""

  def __init__(self, data_type_definition):
    """Initializes a structure data type map.

    Args:
      data_type_definition (DataTypeDefinition): data type definition.
    """
    structure_values_class = runtime.StructureValuesClassFactory.CreateClass(
        data_type_definition)

    data_type_map_cache = {}
    data_type_maps = self._GetMemberDataTypeMaps(
        data_type_definition, data_type_map_cache)

    if self._CheckCompositeMap(data_type_definition):
      map_byte_stream = self._CompositeMapByteStream
      operation = None
    else:
      map_byte_stream = self._LinearMapByteStream
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
          member_byte_order != definitions.BYTE_ORDER_NATIVE and
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

    subcontext = DataTypeMapContext(values={
        type(structure_values).__name__: structure_values})

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

    return byte_operations.StructOperation(format_string)

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

  def _LinearMapByteStream(self, byte_stream, context=None, **unused_kwargs):
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
      definitions.TYPE_INDICATOR_STREAM: StreamMap,
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
