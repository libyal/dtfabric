# -*- coding: utf-8 -*-
"""Data type maps."""

from __future__ import unicode_literals
import abc
import copy
import uuid

from dtfabric import data_types
from dtfabric import definitions
from dtfabric import errors
from dtfabric import py2to3
from dtfabric.runtime import byte_operations
from dtfabric.runtime import runtime


# TODO: add FormatMap.


class DataTypeMapContext(object):
  """Data type map context.

  Attributes:
    byte_size (int): byte size.
    state (dict[str, object]): state values per name.
    values (dict[str, object]): values per name.
  """

  def __init__(self, values=None):
    """Initializes a data type map context.

    Args:
      values (dict[str, object]): values per name.
    """
    super(DataTypeMapContext, self).__init__()
    self.byte_size = None
    self.state = {}
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

  def GetByteSize(self):
    """Retrieves the byte size of the data type map.

    Returns:
      int: data type size in bytes or None if size cannot be determined.
    """
    if not self._data_type_definition:
      return None

    return self._data_type_definition.GetByteSize()

  def GetSizeHint(self, **unused_kwargs):
    """Retrieves a hint about the size.

    Returns:
      int: hint of the number of bytes needed from the byte stream or None.
    """
    return self.GetByteSize()

  @abc.abstractmethod
  def FoldByteStream(self, mapped_value, **unused_kwargs):
    """Folds the data type into a byte stream.

    Args:
      mapped_value (object): mapped value.

    Returns:
      bytes: byte stream.

    Raises:
      FoldingError: if the data type definition cannot be folded into
          the byte stream.
    """

  @abc.abstractmethod
  def MapByteStream(self, byte_stream, **unused_kwargs):
    """Maps the data type on a byte stream.

    Args:
      byte_stream (bytes): byte stream.

    Returns:
      object: mapped value.

    Raises:
      MappingError: if the data type definition cannot be mapped on
          the byte stream.
    """


class StorageDataTypeMap(DataTypeMap):
  """Storage data type map."""

  _BYTE_ORDER_STRINGS = {
      definitions.BYTE_ORDER_BIG_ENDIAN: '>',
      definitions.BYTE_ORDER_LITTLE_ENDIAN: '<',
      definitions.BYTE_ORDER_NATIVE: '='}

  def _CheckByteStreamSize(self, byte_stream, byte_offset, data_type_size):
    """Checks if the byte stream is large enough for the data type.

    Args:
      byte_stream (bytes): byte stream.
      byte_offset (int): offset into the byte stream where to start.
      data_type_size (int): data type size.

    Raises:
      ByteStreamTooSmallError: if the byte stream is too small.
      MappingError: if the size of the byte stream cannot be determined.
    """
    try:
      byte_stream_size = len(byte_stream)

    except Exception as exception:
      raise errors.MappingError(exception)

    if byte_stream_size - byte_offset < data_type_size:
      raise errors.ByteStreamTooSmallError(
          'Byte stream too small requested: {0:d} available: {1:d}'.format(
              data_type_size, byte_stream_size))

  def _GetByteStreamOperation(self):
    """Retrieves the byte stream operation.

    Returns:
      ByteStreamOperation: byte stream operation or None if unable to determine.
    """
    byte_order_string = self.GetStructByteOrderString()
    format_string = self.GetStructFormatString()
    if not format_string:
      return None

    format_string = ''.join([byte_order_string, format_string])
    return byte_operations.StructOperation(format_string)

  def GetStructByteOrderString(self):
    """Retrieves the Python struct format string.

    Returns:
      str: format string as used by Python struct or None if format string
          cannot be determined.
    """
    if not self._data_type_definition:
      return None

    return self._BYTE_ORDER_STRINGS.get(
        self._data_type_definition.byte_order, None)

  def GetStructFormatString(self):
    """Retrieves the Python struct format string.

    Returns:
      str: format string as used by Python struct or None if format string
          cannot be determined.
    """
    return None

  @abc.abstractmethod
  def FoldByteStream(self, mapped_value, **unused_kwargs):
    """Folds the data type into a byte stream.

    Args:
      mapped_value (object): mapped value.

    Returns:
      bytes: byte stream.

    Raises:
      FoldingError: if the data type definition cannot be folded into
          the byte stream.
    """

  @abc.abstractmethod
  def MapByteStream(self, byte_stream, **unused_kwargs):
    """Maps the data type on a byte stream.

    Args:
      byte_stream (bytes): byte stream.

    Returns:
      object: mapped value.

    Raises:
      MappingError: if the data type definition cannot be mapped on
          the byte stream.
    """


class PrimitiveDataTypeMap(StorageDataTypeMap):
  """Primitive data type map."""

  # pylint: disable=arguments-differ

  def __init__(self, data_type_definition):
    """Initializes a primitive data type map.

    Args:
      data_type_definition (DataTypeDefinition): data type definition.
    """
    super(PrimitiveDataTypeMap, self).__init__(data_type_definition)
    self._operation = self._GetByteStreamOperation()

  def FoldByteStream(self, mapped_value, byte_offset=0, **unused_kwargs):
    """Folds the data type into a byte stream.

    Args:
      mapped_value (object): mapped value.
      byte_offset (Optional[int]): offset into the byte stream where to start.

    Returns:
      bytes: byte stream.

    Raises:
      FoldingError: if the data type definition cannot be folded into
          the byte stream.
    """
    try:
      value = self.FoldValue(mapped_value)
      return self._operation.WriteTo(tuple([value]))

    except Exception as exception:
      error_string = (
          'Unable to write: {0:s} to byte stream at offset: {1:d} '
          'with error: {2!s}').format(
              self._data_type_definition.name, byte_offset, exception)
      raise errors.FoldingError(error_string)

  def FoldValue(self, value):
    """Folds the data type into a value.

    Args:
      value (object): value.

    Returns:
      object: folded value.

    Raises:
      ValueError: if the data type definition cannot be folded into the value.
    """
    return value

  def MapByteStream(
      self, byte_stream, byte_offset=0, context=None, **unused_kwargs):
    """Maps the data type on a byte stream.

    Args:
      byte_stream (bytes): byte stream.
      byte_offset (Optional[int]): offset into the byte stream where to start.
      context (Optional[DataTypeMapContext]): data type map context.

    Returns:
      object: mapped value.

    Raises:
      MappingError: if the data type definition cannot be mapped on
          the byte stream.
    """
    data_type_size = self._data_type_definition.GetByteSize()
    self._CheckByteStreamSize(byte_stream, byte_offset, data_type_size)

    try:
      struct_tuple = self._operation.ReadFrom(byte_stream[byte_offset:])
      mapped_value = self.MapValue(*struct_tuple)

    except Exception as exception:
      error_string = (
          'Unable to read: {0:s} from byte stream at offset: {1:d} '
          'with error: {2!s}').format(
              self._data_type_definition.name, byte_offset, exception)
      raise errors.MappingError(error_string)

    if context:
      context.byte_size = data_type_size

    return mapped_value

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
      1: 'B',
      2: 'H',
      4: 'I',
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
          'Boolean data type has no True or False values.')

    super(BooleanMap, self).__init__(data_type_definition)

  def GetStructFormatString(self):
    """Retrieves the Python struct format string.

    Returns:
      str: format string as used by Python struct or None if format string
          cannot be determined.
    """
    return self._FORMAT_STRINGS_UNSIGNED.get(
        self._data_type_definition.size, None)

  def FoldValue(self, value):
    """Folds the data type into a value.

    Args:
      value (object): value.

    Returns:
      object: folded value.

    Raises:
      ValueError: if the data type definition cannot be folded into the value.
    """
    if value is False and self._data_type_definition.false_value is not None:
      return self._data_type_definition.false_value

    if value is True and self._data_type_definition.true_value is not None:
      return self._data_type_definition.true_value

    raise ValueError('No matching True and False values')

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

    raise ValueError('No matching True and False values')


class CharacterMap(PrimitiveDataTypeMap):
  """Character data type map."""

  # We use 'i' here instead of 'l' because 'l' behaves architecture dependent.

  _FORMAT_STRINGS = {
      1: 'b',
      2: 'h',
      4: 'i',
  }

  def GetStructFormatString(self):
    """Retrieves the Python struct format string.

    Returns:
      str: format string as used by Python struct or None if format string
          cannot be determined.
    """
    return self._FORMAT_STRINGS.get(
        self._data_type_definition.size, None)

  def FoldValue(self, value):
    """Folds the data type into a value.

    Args:
      value (object): value.

    Returns:
      object: folded value.

    Raises:
      ValueError: if the data type definition cannot be folded into the value.
    """
    return ord(value)

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

  _FORMAT_STRINGS = {
      4: 'f',
      8: 'd',
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
      1: 'b',
      2: 'h',
      4: 'i',
      8: 'q',
  }

  # We use 'I' here instead of 'L' because 'L' behaves architecture dependent.

  _FORMAT_STRINGS_UNSIGNED = {
      1: 'B',
      2: 'H',
      4: 'I',
      8: 'Q',
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


class UUIDMap(StorageDataTypeMap):
  """UUID (or GUID) data type map."""

  # pylint: disable=arguments-differ

  def __init__(self, data_type_definition):
    """Initializes an UUID (or GUID) data type map.

    Args:
      data_type_definition (DataTypeDefinition): data type definition.
    """
    super(UUIDMap, self).__init__(data_type_definition)
    self._byte_order = data_type_definition.byte_order

  def FoldByteStream(self, mapped_value, byte_offset=0, **unused_kwargs):
    """Folds the data type into a byte stream.

    Args:
      mapped_value (object): mapped value.
      byte_offset (Optional[int]): offset into the byte stream where to start.

    Returns:
      bytes: byte stream.

    Raises:
      FoldingError: if the data type definition cannot be folded into
          the byte stream.
    """
    value = None

    try:
      if self._byte_order == definitions.BYTE_ORDER_BIG_ENDIAN:
        value = mapped_value.bytes
      elif self._byte_order == definitions.BYTE_ORDER_LITTLE_ENDIAN:
        value = mapped_value.bytes_le

    except Exception as exception:
      error_string = (
          'Unable to write: {0:s} to byte stream at offset: {1:d} '
          'with error: {2!s}').format(
              self._data_type_definition.name, byte_offset, exception)
      raise errors.FoldingError(error_string)

    return value

  def MapByteStream(
      self, byte_stream, byte_offset=0, context=None, **unused_kwargs):
    """Maps the data type on a byte stream.

    Args:
      byte_stream (bytes): byte stream.
      byte_offset (Optional[int]): offset into the byte stream where to start.
      context (Optional[DataTypeMapContext]): data type map context.

    Returns:
      uuid.UUID: mapped value.

    Raises:
      MappingError: if the data type definition cannot be mapped on
          the byte stream.
    """
    data_type_size = self._data_type_definition.GetByteSize()
    self._CheckByteStreamSize(byte_stream, byte_offset, data_type_size)

    try:
      if self._byte_order == definitions.BYTE_ORDER_BIG_ENDIAN:
        mapped_value = uuid.UUID(
            bytes=byte_stream[byte_offset:byte_offset + 16])
      elif self._byte_order == definitions.BYTE_ORDER_LITTLE_ENDIAN:
        mapped_value = uuid.UUID(
            bytes_le=byte_stream[byte_offset:byte_offset + 16])

    except Exception as exception:
      error_string = (
          'Unable to read: {0:s} from byte stream at offset: {1:d} '
          'with error: {2!s}').format(
              self._data_type_definition.name, byte_offset, exception)
      raise errors.MappingError(error_string)

    if context:
      context.byte_size = data_type_size

    return mapped_value


class ElementSequenceDataTypeMap(StorageDataTypeMap):
  """Element sequence data type map."""

  # pylint: disable=arguments-differ

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
      namespace['__builtins__'] = {}

      try:
        elements_data_size = eval(expression, namespace)  # pylint: disable=eval-used
      except Exception as exception:
        raise errors.MappingError(
            'Unable to determine elements data size with error: {0!s}'.format(
                exception))

    if elements_data_size is None or elements_data_size < 0:
      raise errors.MappingError(
          'Invalid elements data size: {0!s}'.format(elements_data_size))

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
      namespace['__builtins__'] = {}

      try:
        number_of_elements = eval(expression, namespace)  # pylint: disable=eval-used
      except Exception as exception:
        raise errors.MappingError(
            'Unable to determine number of elements with error: {0!s}'.format(
                exception))

    if number_of_elements is None or number_of_elements < 0:
      raise errors.MappingError(
          'Invalid number of elements: {0!s}'.format(number_of_elements))

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
      raise errors.FormatError('Missing data type definition')

    element_data_type_definition = getattr(
        data_type_definition, 'element_data_type_definition', None)
    if not element_data_type_definition:
      raise errors.FormatError(
          'Invalid data type definition missing element')

    return element_data_type_definition

  @abc.abstractmethod
  def FoldByteStream(self, mapped_value, **unused_kwargs):
    """Folds the data type into a byte stream.

    Args:
      mapped_value (object): mapped value.

    Returns:
      bytes: byte stream.

    Raises:
      FoldingError: if the data type definition cannot be folded into
          the byte stream.
    """

  def GetSizeHint(self, context=None, **unused_kwargs):
    """Retrieves a hint about the size.

    Args:
      context (Optional[DataTypeMapContext]): data type map context, used to
          determine the size hint.

    Returns:
      int: hint of the number of bytes needed from the byte stream or None.
    """
    context_state = getattr(context, 'state', {})

    elements_data_size = self.GetByteSize()
    if elements_data_size:
      return elements_data_size

    if (self._data_type_definition.elements_data_size is not None or
        self._data_type_definition.elements_data_size_expression is not None):

      try:
        elements_data_size = self._EvaluateElementsDataSize(context)
      except errors.MappingError:
        pass

    elif self._data_type_definition.elements_terminator is not None:
      size_hints = context_state.get('size_hints', {})

      elements_data_size = size_hints.get(self._data_type_definition.name, 0)
      elements_data_size += self._element_data_type_definition.GetByteSize()

    elif (self._data_type_definition.number_of_elements is not None or
          self._data_type_definition.number_of_elements_expression is not None):
      element_byte_size = self._element_data_type_definition.GetByteSize()
      try:
        number_of_elements = self._EvaluateNumberOfElements(context)
        elements_data_size = number_of_elements * element_byte_size
      except errors.MappingError:
        pass

    return elements_data_size

  def GetStructByteOrderString(self):
    """Retrieves the Python struct format string.

    Returns:
      str: format string as used by Python struct or None if format string
          cannot be determined.
    """
    if not self._element_data_type_map:
      return None

    return self._element_data_type_map.GetStructByteOrderString()

  @abc.abstractmethod
  def MapByteStream(self, byte_stream, **unused_kwargs):
    """Maps the data type on a byte stream.

    Args:
      byte_stream (bytes): byte stream.

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
    self._fold_byte_stream = None
    self._map_byte_stream = None
    self._operation = None

    if (self._element_data_type_definition.IsComposite() or
        data_type_definition.elements_data_size_expression is not None or
        data_type_definition.elements_terminator is not None or
        data_type_definition.number_of_elements_expression is not None):
      self._fold_byte_stream = self._CompositeFoldByteStream
      self._map_byte_stream = self._CompositeMapByteStream
    else:
      self._fold_byte_stream = self._LinearFoldByteStream
      self._map_byte_stream = self._LinearMapByteStream
      self._operation = self._GetByteStreamOperation()

  def _CompositeFoldByteStream(
      self, mapped_value, byte_offset=0, **unused_kwargs):
    """Folds the data type into a byte stream.

    Args:
      mapped_value (object): mapped value.
      byte_offset (Optional[int]): offset into the byte stream where to start.

    Returns:
      bytes: byte stream.

    Raises:
      FoldingError: if the data type definition cannot be folded into
          the byte stream.
    """
    # TODO: implement.

  def _CompositeMapByteStream(
      self, byte_stream, byte_offset=0, context=None, **unused_kwargs):
    """Maps a sequence of composite data types on a byte stream.

    Args:
      byte_stream (bytes): byte stream.
      byte_offset (Optional[int]): offset into the byte stream where to start.
      context (Optional[DataTypeMapContext]): data type map context.

    Returns:
      tuple[object, ...]: mapped values.

    Raises:
      ByteStreamTooSmallError: if the byte stream is too small.
      MappingError: if the data type definition cannot be mapped on
          the byte stream.
    """
    elements_terminator = None
    number_of_elements = None

    if (self._data_type_definition.elements_data_size is not None or
        self._data_type_definition.elements_data_size_expression is not None):
      element_byte_size = self._element_data_type_definition.GetByteSize()
      elements_data_size = self._EvaluateElementsDataSize(context)
      number_of_elements, _ = divmod(elements_data_size, element_byte_size)

    elif self._data_type_definition.elements_terminator is not None:
      elements_terminator = self._data_type_definition.elements_terminator

    elif (self._data_type_definition.number_of_elements is not None or
          self._data_type_definition.number_of_elements_expression is not None):
      number_of_elements = self._EvaluateNumberOfElements(context)

    if elements_terminator is None and number_of_elements is None:
      raise errors.MappingError('Unable to determine number of elements')

    context_state = getattr(context, 'state', {})

    element_index = context_state.get('element_index', 0)
    element_value = None
    members_data_size = 0
    mapped_values = context_state.get('mapped_values', [])
    size_hints = context_state.get('size_hints', {})
    subcontext = context_state.get('context', None)

    if not subcontext:
      subcontext = DataTypeMapContext()

    try:
      while byte_stream[byte_offset:]:
        if (number_of_elements is not None and
            element_index == number_of_elements):
          break

        element_value = self._element_data_type_map.MapByteStream(
            byte_stream, byte_offset=byte_offset, context=subcontext)

        byte_offset += subcontext.byte_size
        members_data_size += subcontext.byte_size
        element_index += 1
        mapped_values.append(element_value)

        if (elements_terminator is not None and
            element_value == elements_terminator):
          break

    except errors.ByteStreamTooSmallError as exception:
      context_state['context'] = subcontext
      context_state['element_index'] = element_index
      context_state['mapped_values'] = mapped_values
      raise errors.ByteStreamTooSmallError(exception)

    except Exception as exception:
      raise errors.MappingError(exception)

    if number_of_elements is not None and element_index != number_of_elements:
      context_state['context'] = subcontext
      context_state['element_index'] = element_index
      context_state['mapped_values'] = mapped_values

      error_string = (
          'Unable to read: {0:s} from byte stream at offset: {1:d} '
          'with error: missing element: {2:d}').format(
              self._data_type_definition.name, byte_offset, element_index - 1)
      raise errors.ByteStreamTooSmallError(error_string)

    if elements_terminator is not None and element_value != elements_terminator:
      size_hints[self._data_type_definition.name] = (
          len(byte_stream) - byte_offset)

      context_state['context'] = subcontext
      context_state['mapped_values'] = mapped_values
      context_state['size_hints'] = size_hints

      error_string = (
          'Unable to read: {0:s} from byte stream at offset: {1:d} '
          'with error: unable to find elements terminator').format(
              self._data_type_definition.name, byte_offset)
      raise errors.ByteStreamTooSmallError(error_string)

    if context:
      context.byte_size = members_data_size
      context.state = {}

    return tuple(mapped_values)

  def _LinearFoldByteStream(self, mapped_value, byte_offset=0, **unused_kwargs):
    """Folds the data type into a byte stream.

    Args:
      mapped_value (object): mapped value.
      byte_offset (Optional[int]): offset into the byte stream where to start.

    Returns:
      bytes: byte stream.

    Raises:
      FoldingError: if the data type definition cannot be folded into
          the byte stream.
    """
    try:
      return self._operation.WriteTo(mapped_value)

    except Exception as exception:
      error_string = (
          'Unable to write: {0:s} to byte stream at offset: {1:d} '
          'with error: {2!s}').format(
              self._data_type_definition.name, byte_offset, exception)
      raise errors.FoldingError(error_string)

  def _LinearMapByteStream(
      self, byte_stream, byte_offset=0, context=None, **unused_kwargs):
    """Maps a data type sequence on a byte stream.

    Args:
      byte_stream (bytes): byte stream.
      byte_offset (Optional[int]): offset into the byte stream where to start.
      context (Optional[DataTypeMapContext]): data type map context.

    Returns:
      tuple[object, ...]: mapped values.

    Raises:
      MappingError: if the data type definition cannot be mapped on
          the byte stream.
    """
    elements_data_size = self._data_type_definition.GetByteSize()
    self._CheckByteStreamSize(byte_stream, byte_offset, elements_data_size)

    try:
      struct_tuple = self._operation.ReadFrom(byte_stream[byte_offset:])
      mapped_values = map(self._element_data_type_map.MapValue, struct_tuple)

    except Exception as exception:
      error_string = (
          'Unable to read: {0:s} from byte stream at offset: {1:d} '
          'with error: {2!s}').format(
              self._data_type_definition.name, byte_offset, exception)
      raise errors.MappingError(error_string)

    if context:
      context.byte_size = elements_data_size

    return tuple(mapped_values)

  def FoldByteStream(self, mapped_value, **kwargs):
    """Folds the data type into a byte stream.

    Args:
      mapped_value (object): mapped value.

    Returns:
      bytes: byte stream.

    Raises:
      FoldingError: if the data type definition cannot be folded into
          the byte stream.
    """
    return self._fold_byte_stream(mapped_value, **kwargs)

  def GetStructFormatString(self):
    """Retrieves the Python struct format string.

    Returns:
      str: format string as used by Python struct or None if format string
          cannot be determined.
    """
    if not self._element_data_type_map:
      return None

    number_of_elements = None
    if self._data_type_definition.elements_data_size:
      element_byte_size = self._element_data_type_definition.GetByteSize()
      number_of_elements, _ = divmod(
          self._data_type_definition.elements_data_size, element_byte_size)
    elif self._data_type_definition.number_of_elements:
      number_of_elements = self._data_type_definition.number_of_elements

    format_string = self._element_data_type_map.GetStructFormatString()
    if not number_of_elements or not format_string:
      return None

    return '{0:d}{1:s}'.format(number_of_elements, format_string)

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

  # pylint: disable=arguments-differ

  def __init__(self, data_type_definition):
    """Initializes a stream data type map.

    Args:
      data_type_definition (DataTypeDefinition): data type definition.

    Raises:
      FormatError: if the data type map cannot be determed from the data
          type definition.
    """
    super(StreamMap, self).__init__(data_type_definition)
    self._fold_byte_stream = None
    self._map_byte_stream = None

    if self._element_data_type_definition.IsComposite():
      raise errors.FormatError('Unsupported composite element data type')

    if (data_type_definition.elements_data_size_expression is not None or
        data_type_definition.elements_terminator is not None or
        data_type_definition.number_of_elements_expression is not None):
      self._fold_byte_stream = self._CompositeFoldByteStream
      self._map_byte_stream = self._CompositeMapByteStream
    else:
      self._fold_byte_stream = self._LinearFoldByteStream
      self._map_byte_stream = self._LinearMapByteStream

  def _CompositeFoldByteStream(
      self, mapped_value, byte_offset=0, **unused_kwargs):
    """Folds the data type into a byte stream.

    Args:
      mapped_value (object): mapped value.
      byte_offset (Optional[int]): offset into the byte stream where to start.

    Returns:
      bytes: byte stream.

    Raises:
      FoldingError: if the data type definition cannot be folded into
          the byte stream.
    """
    # TODO: implement.

  def _CompositeMapByteStream(
      self, byte_stream, byte_offset=0, context=None, **unused_kwargs):
    """Maps a sequence of composite data types on a byte stream.

    Args:
      byte_stream (bytes): byte stream.
      byte_offset (Optional[int]): offset into the byte stream where to start.
      context (Optional[DataTypeMapContext]): data type map context.

    Returns:
      tuple[object, ...]: mapped values.

    Raises:
      ByteStreamTooSmallError: if the byte stream is too small.
      MappingError: if the data type definition cannot be mapped on
          the byte stream.
    """
    # TODO: check byte stream size

    elements_data_size = None
    elements_terminator = None

    context_state = getattr(context, 'state', {})

    size_hints = context_state.get('size_hints', {})

    if (self._data_type_definition.elements_data_size is not None or
        self._data_type_definition.elements_data_size_expression is not None):
      elements_data_size = self._EvaluateElementsDataSize(context)

    elif self._data_type_definition.elements_terminator is not None:
      elements_terminator = self._data_type_definition.elements_terminator

    elif (self._data_type_definition.number_of_elements is not None or
          self._data_type_definition.number_of_elements_expression is not None):
      element_byte_size = self._element_data_type_definition.GetByteSize()
      number_of_elements = self._EvaluateNumberOfElements(context)
      elements_data_size = element_byte_size * number_of_elements

    if elements_terminator is None and elements_data_size is None:
      raise errors.MappingError('Unable to determine elements data size')

    if elements_data_size is not None:
      self._CheckByteStreamSize(byte_stream, byte_offset, elements_data_size)

    elif elements_terminator is not None:
      element_byte_size = self._element_data_type_definition.GetByteSize()
      elements_data_offset = byte_offset
      next_elements_data_offset = elements_data_offset + element_byte_size

      element_value = byte_stream[
          elements_data_offset:next_elements_data_offset]

      while byte_stream[elements_data_offset:]:
        elements_data_offset = next_elements_data_offset
        if element_value == elements_terminator:
          elements_data_size = elements_data_offset - byte_offset
          break

        next_elements_data_offset += element_byte_size
        element_value = byte_stream[
            elements_data_offset:next_elements_data_offset]

      if element_value != elements_terminator:
        size_hints[self._data_type_definition.name] = (
            len(byte_stream) - byte_offset)

        context_state['size_hints'] = size_hints

        error_string = (
            'Unable to read: {0:s} from byte stream at offset: {1:d} '
            'with error: unable to find elements terminator').format(
                self._data_type_definition.name, byte_offset)
        raise errors.ByteStreamTooSmallError(error_string)

    if context:
      context.byte_size = elements_data_size

    return byte_stream[byte_offset:byte_offset + elements_data_size]

  def _LinearFoldByteStream(self, mapped_value, byte_offset=0, **unused_kwargs):
    """Folds the data type into a byte stream.

    Args:
      mapped_value (object): mapped value.
      byte_offset (Optional[int]): offset into the byte stream where to start.

    Returns:
      bytes: byte stream.

    Raises:
      FoldingError: if the data type definition cannot be folded into
          the byte stream.
    """
    elements_data_size = self._data_type_definition.GetByteSize()
    if elements_data_size is None:
      raise errors.MappingError('Unable to determine elements data size')

    self._CheckByteStreamSize(mapped_value, byte_offset, elements_data_size)

    return mapped_value[byte_offset:byte_offset + elements_data_size]

  def _LinearMapByteStream(
      self, byte_stream, byte_offset=0, context=None, **unused_kwargs):
    """Maps a data type sequence on a byte stream.

    Args:
      byte_stream (bytes): byte stream.
      byte_offset (Optional[int]): offset into the byte stream where to start.
      context (Optional[DataTypeMapContext]): data type map context.

    Returns:
      tuple[object, ...]: mapped values.

    Raises:
      MappingError: if the data type definition cannot be mapped on
          the byte stream.
    """
    elements_data_size = self._data_type_definition.GetByteSize()
    if elements_data_size is None:
      raise errors.MappingError('Unable to determine elements data size')

    self._CheckByteStreamSize(byte_stream, byte_offset, elements_data_size)

    if context:
      context.byte_size = elements_data_size

    return byte_stream[byte_offset:byte_offset + elements_data_size]

  def FoldByteStream(self, mapped_value, **kwargs):
    """Folds the data type into a byte stream.

    Args:
      mapped_value (object): mapped value.

    Returns:
      bytes: byte stream.

    Raises:
      FoldingError: if the data type definition cannot be folded into
          the byte stream.
    """
    return self._fold_byte_stream(mapped_value, **kwargs)

  def GetStructFormatString(self):
    """Retrieves the Python struct format string.

    Returns:
      str: format string as used by Python struct or None if format string
          cannot be determined.
    """
    byte_size = self.GetByteSize()
    if not byte_size:
      return None

    return '{0:d}B'.format(byte_size)

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

  # pylint: disable=arguments-differ

  def FoldByteStream(self, mapped_value, byte_offset=0, **kwargs):
    """Folds the data type into a byte stream.

    Args:
      mapped_value (object): mapped value.
      byte_offset (Optional[int]): offset into the byte stream where to start.

    Returns:
      bytes: byte stream.

    Raises:
      FoldingError: if the data type definition cannot be folded into
          the byte stream.
    """
    try:
      byte_stream = mapped_value.encode(self._data_type_definition.encoding)

    except Exception as exception:
      error_string = (
          'Unable to write: {0:s} to byte stream at offset: {1:d} '
          'with error: {2!s}').format(
              self._data_type_definition.name, byte_offset, exception)
      raise errors.MappingError(error_string)

    return super(StringMap, self).FoldByteStream(
        byte_stream, byte_offset=byte_offset, **kwargs)

  def MapByteStream(self, byte_stream, byte_offset=0, **kwargs):
    """Maps the data type on a byte stream.

    Args:
      byte_stream (bytes): byte stream.
      byte_offset (Optional[int]): offset into the byte stream where to start.

    Returns:
      str: mapped values.

    Raises:
      MappingError: if the data type definition cannot be mapped on
          the byte stream.
    """
    byte_stream = super(StringMap, self).MapByteStream(
        byte_stream, byte_offset=byte_offset, **kwargs)

    try:
      return byte_stream.decode(self._data_type_definition.encoding)

    except Exception as exception:
      error_string = (
          'Unable to read: {0:s} from byte stream at offset: {1:d} '
          'with error: {2!s}').format(
              self._data_type_definition.name, byte_offset, exception)
      raise errors.MappingError(error_string)


class StructureMap(StorageDataTypeMap):
  """Structure data type map."""

  # pylint: disable=arguments-differ

  def __init__(self, data_type_definition):
    """Initializes a structure data type map.

    Args:
      data_type_definition (DataTypeDefinition): data type definition.
    """
    super(StructureMap, self).__init__(data_type_definition)
    self._attribute_names = self._GetAttributeNames(data_type_definition)
    self._data_type_map_cache = {}
    self._data_type_maps = self._GetMemberDataTypeMaps(
        data_type_definition, self._data_type_map_cache)
    self._fold_byte_stream = None
    self._format_string = None
    self._map_byte_stream = None
    self._number_of_attributes = len(self._attribute_names)
    self._operation = None
    self._structure_values_class = (
        runtime.StructureValuesClassFactory.CreateClass(
            data_type_definition))

    if self._CheckCompositeMap(data_type_definition):
      self._fold_byte_stream = self._CompositeFoldByteStream
      self._map_byte_stream = self._CompositeMapByteStream
    else:
      self._fold_byte_stream = self._LinearFoldByteStream
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
      raise errors.FormatError('Missing data type definition')

    members = getattr(data_type_definition, 'members', None)
    if not members:
      raise errors.FormatError('Invalid data type definition missing members')

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

  def _CompositeFoldByteStream(
      self, mapped_value, byte_offset=0, **unused_kwargs):
    """Folds the data type into a byte stream.

    Args:
      mapped_value (object): mapped value.
      byte_offset (Optional[int]): offset into the byte stream where to start.

    Returns:
      bytes: byte stream.

    Raises:
      FoldingError: if the data type definition cannot be folded into
          the byte stream.
    """
    # TODO: implement.

  def _CompositeMapByteStream(
      self, byte_stream, byte_offset=0, context=None, **unused_kwargs):
    """Maps a sequence of composite data types on a byte stream.

    Args:
      byte_stream (bytes): byte stream.
      byte_offset (Optional[int]): offset into the byte stream where to start.
      context (Optional[DataTypeMapContext]): data type map context.

    Returns:
      object: mapped value.

    Raises:
      MappingError: if the data type definition cannot be mapped on
          the byte stream.
    """
    context_state = getattr(context, 'state', {})

    attribute_index = context_state.get('attribute_index', 0)
    mapped_values = context_state.get('mapped_values', None)
    members_data_size = 0
    subcontext = context_state.get('context', None)

    if not mapped_values:
      mapped_values = self._structure_values_class()
    if not subcontext:
      subcontext = DataTypeMapContext(values={
          type(mapped_values).__name__: mapped_values})

    for attribute_index in range(attribute_index, self._number_of_attributes):
      attribute_name = self._attribute_names[attribute_index]
      data_type_map = self._data_type_maps[attribute_index]

      try:
        value = data_type_map.MapByteStream(
            byte_stream, byte_offset=byte_offset, context=subcontext)
        setattr(mapped_values, attribute_name, value)

      except errors.ByteStreamTooSmallError as exception:
        context_state['attribute_index'] = attribute_index
        context_state['context'] = subcontext
        context_state['mapped_values'] = mapped_values
        raise errors.ByteStreamTooSmallError(exception)

      except Exception as exception:
        raise errors.MappingError(exception)

      byte_offset += subcontext.byte_size
      members_data_size += subcontext.byte_size

    if attribute_index != (self._number_of_attributes - 1):
      context_state['attribute_index'] = attribute_index
      context_state['context'] = subcontext
      context_state['mapped_values'] = mapped_values

      error_string = (
          'Unable to read: {0:s} from byte stream at offset: {1:d} '
          'with error: missing attribute: {2:d}').format(
              self._data_type_definition.name, byte_offset, attribute_index)
      raise errors.ByteStreamTooSmallError(error_string)

    if context:
      context.byte_size = members_data_size
      context.state = {}

    return mapped_values

  def _GetAttributeNames(self, data_type_definition):
    """Determines the attribute (or field) names of the members.

    Args:
      data_type_definition (DataTypeDefinition): data type definition.

    Returns:
      list[str]: attribute names.

    Raises:
      FormatError: if the attribute names cannot be determed from the data
          type definition.
    """
    if not data_type_definition:
      raise errors.FormatError('Missing data type definition')

    attribute_names = []
    for member_definition in data_type_definition.members:
      attribute_names.append(member_definition.name)

    return attribute_names

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
      raise errors.FormatError('Missing data type definition')

    members = getattr(data_type_definition, 'members', None)
    if not members:
      raise errors.FormatError('Invalid data type definition missing members')

    data_type_maps = []

    for member_definition in members:
      if isinstance(member_definition, data_types.MemberDataTypeDefinition):
        member_definition = member_definition.member_data_type_definition

      if (data_type_definition.byte_order != definitions.BYTE_ORDER_NATIVE and
          member_definition.byte_order == definitions.BYTE_ORDER_NATIVE):
        # Make a copy of the data type definition where byte-order can be
        # safely changed.
        member_definition = copy.copy(member_definition)
        member_definition.name = '_{0:s}_{1:s}'.format(
            data_type_definition.name, member_definition.name)
        member_definition.byte_order = data_type_definition.byte_order

      if member_definition.name not in data_type_map_cache:
        data_type_map = DataTypeMapFactory.CreateDataTypeMapByType(
            member_definition)
        data_type_map_cache[member_definition.name] = data_type_map

      data_type_maps.append(data_type_map_cache[member_definition.name])

    return data_type_maps

  def _LinearFoldByteStream(self, mapped_value, byte_offset=0, **unused_kwargs):
    """Folds the data type into a byte stream.

    Args:
      mapped_value (object): mapped value.
      byte_offset (Optional[int]): offset into the byte stream where to start.

    Returns:
      bytes: byte stream.

    Raises:
      FoldingError: if the data type definition cannot be folded into
          the byte stream.
    """
    try:
      attribute_values = [
          getattr(mapped_value, attribute_name, None)
          for attribute_name in self._attribute_names]
      attribute_values = [
          value for value in attribute_values if value is not None]
      return self._operation.WriteTo(tuple(attribute_values))

    except Exception as exception:
      error_string = (
          'Unable to write: {0:s} to byte stream at offset: {1:d} '
          'with error: {2!s}').format(
              self._data_type_definition.name, byte_offset, exception)
      raise errors.FoldingError(error_string)

  def _LinearMapByteStream(
      self, byte_stream, byte_offset=0, context=None, **unused_kwargs):
    """Maps a data type sequence on a byte stream.

    Args:
      byte_stream (bytes): byte stream.
      byte_offset (Optional[int]): offset into the byte stream where to start.
      context (Optional[DataTypeMapContext]): data type map context.

    Returns:
      object: mapped value.

    Raises:
      MappingError: if the data type definition cannot be mapped on
          the byte stream.
    """
    members_data_size = self._data_type_definition.GetByteSize()
    self._CheckByteStreamSize(byte_stream, byte_offset, members_data_size)

    try:
      struct_tuple = self._operation.ReadFrom(byte_stream[byte_offset:])
      values = [
          self._data_type_maps[index].MapValue(value)
          for index, value in enumerate(struct_tuple)]
      mapped_value = self._structure_values_class(*values)

    except Exception as exception:
      error_string = (
          'Unable to read: {0:s} from byte stream at offset: {1:d} '
          'with error: {2!s}').format(
              self._data_type_definition.name, byte_offset, exception)
      raise errors.MappingError(error_string)

    if context:
      context.byte_size = members_data_size

    return mapped_value

  def CreateStructureValues(self, *args, **kwargs):
    """Creates a structure values object.

    Returns:
      object: structure values.
    """
    return self._structure_values_class(*args, **kwargs)

  def FoldByteStream(self, mapped_value, **kwargs):
    """Folds the data type into a byte stream.

    Args:
      mapped_value (object): mapped value.

    Returns:
      bytes: byte stream.

    Raises:
      FoldingError: if the data type definition cannot be folded into
          the byte stream.
    """
    return self._fold_byte_stream(mapped_value, **kwargs)

  def GetSizeHint(self, context=None, **unused_kwargs):
    """Retrieves a hint about the size.

    Args:
      context (Optional[DataTypeMapContext]): data type map context, used to
          determine the size hint.

    Returns:
      int: hint of the number of bytes needed from the byte stream or None.
    """
    context_state = getattr(context, 'state', {})

    subcontext = context_state.get('context', None)
    if not subcontext:
      mapped_values = context_state.get('mapped_values', None)
      subcontext = DataTypeMapContext(values={
          type(mapped_values).__name__: mapped_values})

    size_hint = 0
    for data_type_map in self._data_type_maps:
      data_type_size = data_type_map.GetSizeHint(context=subcontext)
      if data_type_size is None:
        break

      size_hint += data_type_size

    return size_hint

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
          return None

        member_format_string = member_data_type_map.GetStructFormatString()
        if member_format_string is None:
          return None

        format_strings.append(member_format_string)

      self._format_string = ''.join(format_strings)

    return self._format_string

  def MapByteStream(self, byte_stream, **kwargs):
    """Maps the data type on a byte stream.

    Args:
      byte_stream (bytes): byte stream.

    Returns:
      object: mapped value.

    Raises:
      MappingError: if the data type definition cannot be mapped on
          the byte stream.
    """
    return self._map_byte_stream(byte_stream, **kwargs)


class SemanticDataTypeMap(DataTypeMap):
  """Semantic data type map."""

  def FoldByteStream(self, mapped_value, **unused_kwargs):
    """Folds the data type into a byte stream.

    Args:
      mapped_value (object): mapped value.

    Returns:
      bytes: byte stream.

    Raises:
      FoldingError: if the data type definition cannot be folded into
          the byte stream.
    """
    raise errors.FoldingError(
        'Unable to fold {0:s} data type into byte stream'.format(
            self._data_type_definition.TYPE_INDICATOR))

  def MapByteStream(self, byte_stream, **unused_kwargs):
    """Maps the data type on a byte stream.

    Args:
      byte_stream (bytes): byte stream.

    Returns:
      object: mapped value.

    Raises:
      MappingError: if the data type definition cannot be mapped on
          the byte stream.
    """
    raise errors.MappingError(
        'Unable to map {0:s} data type to byte stream'.format(
            self._data_type_definition.TYPE_INDICATOR))


class ConstantMap(SemanticDataTypeMap):
  """Constant data type map."""


class EnumerationMap(SemanticDataTypeMap):
  """Enumeration data type map."""

  def GetName(self, number):
    """Retrieves the name of an enumeration value by number.

    Args:
      number (int): number.

    Returns:
      str: name of the enumeration value or None if no corresponding
          enumeration value was found.
    """
    value = self._data_type_definition.values_per_number.get(number, None)
    if not value:
      return None

    return value.name


class DataTypeMapFactory(object):
  """Factory for data type maps."""

  # TODO: add support for definitions.TYPE_INDICATOR_FORMAT

  _MAP_PER_DEFINITION = {
      definitions.TYPE_INDICATOR_BOOLEAN: BooleanMap,
      definitions.TYPE_INDICATOR_CHARACTER: CharacterMap,
      definitions.TYPE_INDICATOR_CONSTANT: ConstantMap,
      definitions.TYPE_INDICATOR_ENUMERATION: EnumerationMap,
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
      return None

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
      return None

    return data_type_map_class(data_type_definition)
