# -*- coding: utf-8 -*-
"""Data type maps."""

import abc
import copy
import uuid

from dtfabric import byte_operations
from dtfabric import data_types
from dtfabric import definitions
from dtfabric import errors
from dtfabric import py2to3
from dtfabric import runtime


# TODO: add ConstantMap.
# TODO: complete EnumerationMap.
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

  _BYTE_ORDER_STRINGS = {
      definitions.BYTE_ORDER_BIG_ENDIAN: u'>',
      definitions.BYTE_ORDER_LITTLE_ENDIAN: u'<',
      definitions.BYTE_ORDER_NATIVE: u'='}

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

  def _GetByteStreamOperation(self):
    """Retrieves the byte stream operation.

    Returns:
      ByteStreamOperation: byte stream operation or None if unable to determine.
    """
    byte_order_string = self.GetStructByteOrderString()
    format_string = self.GetStructFormatString()
    if format_string:
      format_string = u''.join([byte_order_string, format_string])
      return byte_operations.StructOperation(format_string)

  def GetByteSize(self):
    """Retrieves the byte size of the data type map.

    Returns:
      int: data type size in bytes or None if size cannot be determined.
    """
    if self._data_type_definition:
      return self._data_type_definition.GetByteSize()

  def GetStructByteOrderString(self):
    """Retrieves the Python struct format string.

    Returns:
      str: format string as used by Python struct or None if format string
          cannot be determined.
    """
    if self._data_type_definition:
      return self._BYTE_ORDER_STRINGS.get(
          self._data_type_definition.byte_order, None)

  def GetStructFormatString(self):
    """Retrieves the Python struct format string.

    Returns:
      str: format string as used by Python struct or None if format string
          cannot be determined.
    """
    return

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
    """Initializes a primitive data type map.

    Args:
      data_type_definition (DataTypeDefinition): data type definition.
    """
    super(PrimitiveDataTypeMap, self).__init__(data_type_definition)
    self._operation = self._GetByteStreamOperation()

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

  # We use 'I' here instead of 'L' because 'L' behaves architecture dependent.

  _FORMAT_STRINGS_UNSIGNED = {
      1: u'B',
      2: u'H',
      4: u'I',
  }

  def __init__(self, data_type_definition):
    """Initializes a boolean data type map.

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

  def GetStructFormatString(self):
    """Retrieves the Python struct format string.

    Returns:
      str: format string as used by Python struct or None if format string
          cannot be determined.
    """
    return self._FORMAT_STRINGS_UNSIGNED.get(
        self._data_type_definition.size, None)

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

  # We use 'i' here instead of 'l' because 'l' behaves architecture dependent.

  _FORMAT_STRINGS = {
      1: u'b',
      2: u'h',
      4: u'i',
  }

  def GetStructFormatString(self):
    """Retrieves the Python struct format string.

    Returns:
      str: format string as used by Python struct or None if format string
          cannot be determined.
    """
    return self._FORMAT_STRINGS.get(
        self._data_type_definition.size, None)

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


class EnumerationMap(PrimitiveDataTypeMap):
  """Enumeration data type map."""

  # We use 'I' here instead of 'L' because 'L' behaves architecture dependent.

  _FORMAT_STRINGS_UNSIGNED = {
      1: u'B',
      2: u'H',
      4: u'I',
  }

  def GetStructFormatString(self):
    """Retrieves the Python struct format string.

    Returns:
      str: format string as used by Python struct or None if format string
          cannot be determined.
    """
    return self._FORMAT_STRINGS_UNSIGNED.get(
        self._data_type_definition.size, None)


class FloatingPointMap(PrimitiveDataTypeMap):
  """Floating-point data type map."""

  _FORMAT_STRINGS = {
      4: u'f',
      8: u'd',
  }

  def GetStructFormatString(self):
    """Retrieves the Python struct format string.

    Returns:
      str: format string as used by Python struct or None if format string
          cannot be determined.
    """
    return self._FORMAT_STRINGS.get(
        self._data_type_definition.size, None)


class IntegerMap(PrimitiveDataTypeMap):
  """Integer data type map."""

  # We use 'i' here instead of 'l' because 'l' behaves architecture dependent.

  _FORMAT_STRINGS_SIGNED = {
      1: u'b',
      2: u'h',
      4: u'i',
      8: u'q',
  }

  # We use 'I' here instead of 'L' because 'L' behaves architecture dependent.

  _FORMAT_STRINGS_UNSIGNED = {
      1: u'B',
      2: u'H',
      4: u'I',
      8: u'Q',
  }

  def GetStructFormatString(self):
    """Retrieves the Python struct format string.

    Returns:
      str: format string as used by Python struct or None if format string
          cannot be determined.
    """
    if self._data_type_definition.format == definitions.FORMAT_UNSIGNED:
      return self._FORMAT_STRINGS_UNSIGNED.get(
          self._data_type_definition.size, None)

    return self._FORMAT_STRINGS_SIGNED.get(
        self._data_type_definition.size, None)


class ElementSequenceDataTypeMap(DataTypeMap):
  """Element sequence data type map."""

  def __init__(self, data_type_definition):
    """Initializes a sequence data type map.

    Args:
      data_type_definition (DataTypeDefinition): data type definition.
    """
    element_data_type_definition = self._GetElementDataTypeDefinition(
        data_type_definition)

    super(ElementSequenceDataTypeMap, self).__init__(data_type_definition)
    self._element_data_type_map = DataTypeMapFactory.CreateDataTypeMapByType(
        element_data_type_definition)
    self._element_data_type_definition = element_data_type_definition

  def _EvaluateElementsDataSize(self, context):
    """Evaluates elements data size.

    Args:
      context (DataTypeMapContext): data type map context.

    Returns:
      int: elements data size.

    Raises:
      MappingError: if the elements data size cannot be determined.
    """
    elements_data_size = None
    if self._data_type_definition.elements_data_size:
      elements_data_size = self._data_type_definition.elements_data_size

    elif self._data_type_definition.elements_data_size_expression:
      expression = self._data_type_definition.elements_data_size_expression
      namespace = {}
      if context and context.values:
        namespace.update(context.values)
      # Make sure __builtins__ contains an empty dictionary.
      namespace[u'__builtins__'] = {}

      try:
        elements_data_size = eval(expression, namespace)  # pylint: disable=eval-used
      except Exception as exception:
        raise errors.MappingError(
            u'Unable to determine elements data size with error: {0!s}'.format(
                exception))

    if elements_data_size is None or elements_data_size < 0:
      raise errors.MappingError(
          u'Invalid elements data size: {0!s}'.format(elements_data_size))

    return elements_data_size

  def _EvaluateNumberOfElements(self, context):
    """Evaluates number of elements.

    Args:
      context (DataTypeMapContext): data type map context.

    Returns:
      int: number of elements.

    Raises:
      MappingError: if the number of elements cannot be determined.
    """
    number_of_elements = None
    if self._data_type_definition.number_of_elements:
      number_of_elements = self._data_type_definition.number_of_elements

    elif self._data_type_definition.number_of_elements_expression:
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

    if number_of_elements is None or number_of_elements < 0:
      raise errors.MappingError(
          u'Invalid number of elements: {0!s}'.format(number_of_elements))

    return number_of_elements

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

  def GetStructByteOrderString(self):
    """Retrieves the Python struct format string.

    Returns:
      str: format string as used by Python struct or None if format string
          cannot be determined.
    """
    if self._element_data_type_map:
      return self._element_data_type_map.GetStructByteOrderString()

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


class SequenceMap(ElementSequenceDataTypeMap):
  """Sequence data type map."""

  def __init__(self, data_type_definition):
    """Initializes a sequence data type map.

    Args:
      data_type_definition (DataTypeDefinition): data type definition.
    """
    super(SequenceMap, self).__init__(data_type_definition)
    self._map_byte_stream = None
    self._operation = None

    if (self._element_data_type_definition.IsComposite() or
        data_type_definition.elements_data_size_expression or
        data_type_definition.number_of_elements_expression):
      self._map_byte_stream = self._CompositeMapByteStream
    else:
      self._map_byte_stream = self._LinearMapByteStream
      self._operation = self._GetByteStreamOperation()

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
    number_of_elements = None
    if (self._data_type_definition.elements_data_size or
        self._data_type_definition.elements_data_size_expression):
      element_byte_size = self._element_data_type_definition.GetByteSize()
      elements_data_size = self._EvaluateElementsDataSize(context)
      number_of_elements, _ = divmod(elements_data_size, element_byte_size)

    elif (self._data_type_definition.number_of_elements or
          self._data_type_definition.number_of_elements_expression):
      number_of_elements = self._EvaluateNumberOfElements(context)

    if number_of_elements is None:
      raise errors.MappingError(u'Unable to determine number of elements')

    values = []

    subcontext = DataTypeMapContext()

    byte_stream_offset = 0
    for _ in range(number_of_elements):
      try:
        value = self._element_data_type_map.MapByteStream(
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
      return tuple(map(self._element_data_type_map.MapValue, struct_tuple))

    except Exception as exception:
      raise errors.MappingError(exception)

  def GetStructFormatString(self):
    """Retrieves the Python struct format string.

    Returns:
      str: format string as used by Python struct or None if format string
          cannot be determined.
    """
    if self._element_data_type_map:
      number_of_elements = None
      if self._data_type_definition.elements_data_size:
        element_byte_size = self._element_data_type_definition.GetByteSize()
        number_of_elements, _ = divmod(
            self._data_type_definition.elements_data_size, element_byte_size)
      elif self._data_type_definition.number_of_elements:
        number_of_elements = self._data_type_definition.number_of_elements

      format_string = self._element_data_type_map.GetStructFormatString()
      if number_of_elements and format_string:
        return u'{0:d}{1:s}'.format(number_of_elements, format_string)

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


class StreamMap(ElementSequenceDataTypeMap):
  """Stream data type map."""

  def __init__(self, data_type_definition):
    """Initializes a stream data type map.

    Args:
      data_type_definition (DataTypeDefinition): data type definition.

    Raises:
      FormatError: if the data type map cannot be determed from the data
          type definition.
    """
    super(StreamMap, self).__init__(data_type_definition)
    self._map_byte_stream = None

    if self._element_data_type_definition.IsComposite():
      raise errors.FormatError(u'Unsupported composite element data type')

    if (data_type_definition.elements_data_size_expression or
        data_type_definition.number_of_elements_expression):
      self._map_byte_stream = self._CompositeMapByteStream
    else:
      self._map_byte_stream = self._LinearMapByteStream

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
    elements_data_size = None
    if (self._data_type_definition.elements_data_size or
        self._data_type_definition.elements_data_size_expression):
      elements_data_size = self._EvaluateElementsDataSize(context)

    elif (self._data_type_definition.number_of_elements or
          self._data_type_definition.number_of_elements_expression):
      element_byte_size = self._element_data_type_definition.GetByteSize()
      number_of_elements = self._EvaluateNumberOfElements(context)
      elements_data_size = element_byte_size * number_of_elements

    if elements_data_size is None:
      raise errors.MappingError(u'Unable to determine elements data size')

    try:
      byte_stream_size = len(byte_stream)

    except Exception as exception:
      raise errors.MappingError(exception)

    if byte_stream_size < elements_data_size:
      raise errors.MappingError(
          u'Byte stream too small requested: {0:d} available: {1:d}'.format(
              elements_data_size, byte_stream_size))

    if context:
      context.byte_size = elements_data_size

    return byte_stream[:elements_data_size]

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
    elements_data_size = self._data_type_definition.GetByteSize()

    if elements_data_size is None:
      raise errors.MappingError(u'Unable to determine elements data size')

    try:
      byte_stream_size = len(byte_stream)

    except Exception as exception:
      raise errors.MappingError(exception)

    if byte_stream_size < elements_data_size:
      raise errors.MappingError(
          u'Byte stream too small requested: {0:d} available: {1:d}'.format(
              elements_data_size, byte_stream_size))

    if context:
      context.byte_size = elements_data_size

    return byte_stream[:elements_data_size]

  def GetStructFormatString(self):
    """Retrieves the Python struct format string.

    Returns:
      str: format string as used by Python struct or None if format string
          cannot be determined.
    """
    byte_size = self.GetByteSize()
    if byte_size:
      return u'{0:d}B'.format(byte_size)

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


class StringMap(StreamMap):
  """String data type map."""

  def MapByteStream(self, byte_stream, context=None, **kwargs):
    """Maps the data type on a byte stream.

    Args:
      byte_stream (bytes): byte stream.
      context (Optional[DataTypeMapContext]): data type map context.

    Returns:
      str: mapped values.

    Raises:
      MappingError: if the data type definition cannot be mapped on
          the byte stream.
    """
    byte_stream = super(StringMap, self).MapByteStream(
        byte_stream, context=context, **kwargs)

    try:
      return byte_stream.decode(self._data_type_definition.encoding)

    except Exception as exception:
      raise errors.MappingError(exception)


class StructureMap(DataTypeMap):
  """Structure data type map."""

  def __init__(self, data_type_definition):
    """Initializes a structure data type map.

    Args:
      data_type_definition (DataTypeDefinition): data type definition.
    """
    super(StructureMap, self).__init__(data_type_definition)
    self._attribute_names = data_type_definition.GetAttributeNames()
    self._data_type_map_cache = {}
    self._data_type_maps = self._GetMemberDataTypeMaps(
        data_type_definition, self._data_type_map_cache)
    self._format_string = None
    self._map_byte_stream = None
    self._operation = None
    self._structure_values_class = (
        runtime.StructureValuesClassFactory.CreateClass(
            data_type_definition))

    if self._CheckCompositeMap(data_type_definition):
      self._map_byte_stream = self._CompositeMapByteStream
    else:
      self._map_byte_stream = self._LinearMapByteStream
      self._operation = self._GetByteStreamOperation()

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

    is_composite_map = False
    last_member_byte_order = data_type_definition.byte_order

    for member_definition in members:
      if member_definition.IsComposite():
        is_composite_map = True
        break

      if (last_member_byte_order != definitions.BYTE_ORDER_NATIVE and
          member_definition.byte_order != definitions.BYTE_ORDER_NATIVE and
          last_member_byte_order != member_definition.byte_order):
        is_composite_map = True
        break

      last_member_byte_order = member_definition.byte_order

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
    for index, attribute_name in enumerate(self._attribute_names):
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

      if (data_type_definition.byte_order != definitions.BYTE_ORDER_NATIVE and
          member_definition.byte_order == definitions.BYTE_ORDER_NATIVE):
        # Make a copy of the data type definition where byte-order can be
        # safely changed.
        member_definition = copy.copy(member_definition)
        member_definition.name = u'{0:s}.{1:s}'.format(
            data_type_definition.name, member_definition.name)
        member_definition.byte_order = data_type_definition.byte_order

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

  def GetStructFormatString(self):
    """Retrieves the Python struct format string.

    Returns:
      str: format string as used by Python struct or None if format string
          cannot be determined.
    """
    if self._format_string is None and self._data_type_maps:
      format_strings = []
      for member_data_type_map in self._data_type_maps:
        if member_data_type_map is None:
          return

        member_format_string = member_data_type_map.GetStructFormatString()
        if member_format_string is None:
          return

        format_strings.append(member_format_string)

      self._format_string = u''.join(format_strings)

    return self._format_string

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
    """Initializes an UUID (or GUID) data type map.

    Args:
      data_type_definition (DataTypeDefinition): data type definition.
    """
    super(UUIDMap, self).__init__(data_type_definition)
    self._operation = self._GetByteStreamOperation()

  def GetStructFormatString(self):
    """Retrieves the Python struct format string.

    Returns:
      str: format string as used by Python struct or None if format string
          cannot be determined.
    """
    return u'IHH8B'

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
      definitions.TYPE_INDICATOR_STRING: StringMap,
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
