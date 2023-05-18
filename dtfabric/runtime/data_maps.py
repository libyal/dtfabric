# -*- coding: utf-8 -*-
"""Data type maps."""

import abc
import ast
import copy
import uuid

from dtfabric import data_types
from dtfabric import decorators
from dtfabric import definitions
from dtfabric import errors
from dtfabric.runtime import byte_operations
from dtfabric.runtime import runtime


class DataTypeMapContext(object):
  """Data type map context.

  Attributes:
    byte_size (int): byte size.
    requested_size (int): requested size.
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
    self.requested_size = None
    self.state = {}
    self.values = values or {}


class DataTypeMapSizeHint(object):
  """Data type map size hint.

  Attributes:
    byte_size (int): byte size.
    is_complete (bool): True if the size is the complete size of the data type.
  """

  def __init__(self, byte_size, is_complete=False):
    """Initializes a data type map size hint.

    Args:
      byte_size (int): byte size.
      is_complete (optional[bool]): True if the size is the complete size of
          the data type.
    """
    super(DataTypeMapSizeHint, self).__init__()
    self.byte_size = byte_size
    self.is_complete = is_complete


class DataTypeMap(object):
  """Data type map."""

  _MAXIMUM_RECURSION_DEPTH = 10

  def __init__(self, data_type_definition):
    """Initializes a data type map.

    Args:
      data_type_definition (DataTypeDefinition): data type definition.

    Raises:
      FormatError: if the data type map cannot be determined from the data
          type definition.
    """
    super(DataTypeMap, self).__init__()
    self._data_type_definition = data_type_definition

  @property
  def name(self):
    """str: name of the data type definition or None if not available."""
    return getattr(self._data_type_definition, 'name', None)

  @decorators.deprecated
  def GetByteSize(self):
    """Retrieves the byte size of the data type map.

    This method is deprecated use GetSizeHint instead.

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
    if not self._data_type_definition:
      return None

    return self._data_type_definition.GetByteSize()

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
          f'Byte stream too small requested: {data_type_size:d} available: '
          f'{byte_stream_size:d}')

  def _GetByteStreamOperation(self):
    """Retrieves the byte stream operation.

    Returns:
      ByteStreamOperation: byte stream operation or None if unable to determine.
    """
    byte_order_string = self.GetStructByteOrderString()
    format_string = self.GetStructFormatString()  # pylint: disable=assignment-from-none
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

  def GetStructFormatString(self):  # pylint: disable=redundant-returns-doc
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

  def __init__(self, data_type_definition):
    """Initializes a primitive data type map.

    Args:
      data_type_definition (DataTypeDefinition): data type definition.
    """
    super(PrimitiveDataTypeMap, self).__init__(data_type_definition)
    self._operation = self._GetByteStreamOperation()

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
    try:
      value = self.FoldValue(mapped_value)
      return self._operation.WriteTo(tuple([value]))

    except Exception as exception:
      raise errors.FoldingError(
          f'Unable to write: {self._data_type_definition.name:s} to byte '
          f'stream with error: {exception!s}')

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

    if context:
      context.byte_size = None
      context.requested_size = data_type_size

    try:
      struct_tuple = self._operation.ReadFrom(byte_stream[byte_offset:])
      mapped_value = self.MapValue(*struct_tuple)

    except Exception as exception:
      raise errors.MappingError(
          f'Unable to read: {self._data_type_definition.name:s} from byte '
          f'stream at offset: {byte_offset:d} with error: {exception!s}')

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
  """Boolean data type map."""

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
      FormatError: if the data type map cannot be determined from the data
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
    return chr(value)


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

  def __init__(self, data_type_definition):
    """Initializes an UUID (or GUID) data type map.

    Args:
      data_type_definition (DataTypeDefinition): data type definition.
    """
    super(UUIDMap, self).__init__(data_type_definition)
    self._byte_order = data_type_definition.byte_order

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
    value = None

    try:
      if self._byte_order == definitions.BYTE_ORDER_BIG_ENDIAN:
        value = mapped_value.bytes
      elif self._byte_order == definitions.BYTE_ORDER_LITTLE_ENDIAN:
        value = mapped_value.bytes_le

    except Exception as exception:
      raise errors.FoldingError(
          f'Unable to write: {self._data_type_definition.name:s} to byte '
          f'stream with error: {exception!s}')

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

    if context:
      context.byte_size = None
      context.requested_size = data_type_size

    try:
      if self._byte_order == definitions.BYTE_ORDER_BIG_ENDIAN:
        mapped_value = uuid.UUID(
            bytes=byte_stream[byte_offset:byte_offset + 16])
      elif self._byte_order == definitions.BYTE_ORDER_LITTLE_ENDIAN:
        mapped_value = uuid.UUID(
            bytes_le=byte_stream[byte_offset:byte_offset + 16])

    except Exception as exception:
      raise errors.MappingError(
          f'Unable to read: {self._data_type_definition.name:s} from byte '
          f'stream at offset: {byte_offset:d} with error: {exception!s}')

    if context:
      context.byte_size = data_type_size

    return mapped_value


class ElementSequenceDataTypeMap(StorageDataTypeMap):
  """Element sequence data type map."""

  def __init__(self, data_type_definition):
    """Initializes a sequence data type map.

    Args:
      data_type_definition (DataTypeDefinition): data type definition.
    """
    super(ElementSequenceDataTypeMap, self).__init__(data_type_definition)
    self._element_data_type_map = None
    self._element_data_type_definition = None
    self._elements_data_size_expression = None
    self._number_of_elements_expression = None

    self._GetElementDataTypeMap(data_type_definition)

    if data_type_definition.elements_data_size_expression:
      expression_ast = ast.parse(
          data_type_definition.elements_data_size_expression, mode='eval')
      self._elements_data_size_expression = compile(
          expression_ast, '<string>', mode='eval')

    if data_type_definition.number_of_elements_expression:
      expression_ast = ast.parse(
          data_type_definition.number_of_elements_expression, mode='eval')
      self._number_of_elements_expression = compile(
          expression_ast, '<string>', mode='eval')

  def _CalculateElementsDataSize(self, context):
    """Calculates the elements data size.

    Args:
      context (Optional[DataTypeMapContext]): data type map context, used to
          determine the size hint.

    Returns:
      int: the elements data size or None if not available.
    """
    context_state = getattr(context, 'state', {})

    elements_data_size = context_state.get('elements_data_size', None)
    if elements_data_size:
      return elements_data_size

    if self._HasElementsDataSize():
      elements_data_size = self._EvaluateElementsDataSize(context)

    elif self._HasNumberOfElements():
      element_byte_size = self._element_data_type_definition.GetByteSize()
      if element_byte_size is not None:
        number_of_elements = context_state.get('number_of_elements', None)
        if number_of_elements is None:
          number_of_elements = self._EvaluateNumberOfElements(context)

        if number_of_elements is not None:
          elements_data_size = number_of_elements * element_byte_size

    return elements_data_size

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

    elif self._elements_data_size_expression:
      expression = self._elements_data_size_expression
      namespace = {}
      if context and context.values:
        namespace.update(context.values)
      # Make sure __builtins__ contains an empty dictionary.
      namespace['__builtins__'] = {}

      try:
        elements_data_size = eval(expression, namespace)  # pylint: disable=eval-used
      except Exception as exception:
        raise errors.MappingError(
            f'Unable to determine elements data size with error: {exception!s}')

    try:
      invalid_value = elements_data_size is None or elements_data_size < 0
    except TypeError:
      invalid_value = True

    if invalid_value:
      raise errors.MappingError(
          f'Invalid elements data size: {elements_data_size!s}')

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

    elif self._number_of_elements_expression:
      expression = self._number_of_elements_expression
      namespace = getattr(context, 'values', {})
      # Make sure __builtins__ contains an empty dictionary.
      namespace['__builtins__'] = {}

      try:
        number_of_elements = eval(expression, namespace)  # pylint: disable=eval-used
      except Exception as exception:
        raise errors.MappingError(
            f'Unable to determine number of elements with error: {exception!s}')

    try:
      invalid_value = number_of_elements is None or number_of_elements < 0
    except TypeError:
      invalid_value = True

    if invalid_value:
      raise errors.MappingError(
          f'Invalid number of elements: {number_of_elements!s}')

    return number_of_elements

  def _GetElementDataTypeDefinition(self, data_type_definition):
    """Retrieves the element data type definition.

    Args:
      data_type_definition (DataTypeDefinition): data type definition.

    Returns:
      DataTypeDefinition: element data type definition.

    Raises:
      FormatError: if the element data type cannot be determined from the data
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

  def _GetElementDataTypeMap(self, data_type_definition):
    """Retrieves the element data type map.

    Args:
      data_type_definition (DataTypeDefinition): data type definition.

    Raises:
      FormatError: if the data type map cannot be determined from the data
          type definition.
    """
    element_data_type_definition = self._GetElementDataTypeDefinition(
        data_type_definition)

    element_byte_order = element_data_type_definition.byte_order
    if (data_type_definition.byte_order != definitions.BYTE_ORDER_NATIVE and
        element_byte_order == definitions.BYTE_ORDER_NATIVE and
        not element_data_type_definition.IsComposite()):
      # Make a copy of the data type definition where byte-order can be
      # safely changed.
      element_data_type_definition = copy.copy(element_data_type_definition)
      element_data_type_definition.name = (
          f'_{data_type_definition.name:s}'
          f'_{element_data_type_definition.name:s}')
      element_data_type_definition.byte_order = data_type_definition.byte_order

    self._element_data_type_map = DataTypeMapFactory.CreateDataTypeMapByType(
        element_data_type_definition)
    self._element_data_type_definition = element_data_type_definition

  def _HasElementsDataSize(self):
    """Checks if the data type defines an elements data size.

    Returns:
      bool: True if the data types defines an elements data size.
    """
    return (
        self._data_type_definition.elements_data_size is not None or
        self._data_type_definition.elements_data_size_expression is not None)

  def _HasElementsTerminator(self):
    """Checks if the data type defines an elements terminator.

    Returns:
      bool: True if the data types defines an elements terminator.
    """
    return self._data_type_definition.elements_terminator is not None

  def _HasNumberOfElements(self):
    """Checks if the data type defines a number of elements.

    Returns:
      bool: True if the data types defines a number of elements.
    """
    return(
        self._data_type_definition.number_of_elements is not None or
        self._data_type_definition.number_of_elements_expression is not None)

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
    size_hint = getattr(context, 'byte_size', None)
    if size_hint is not None:
      return size_hint

    context_state = getattr(context, 'state', {})

    elements_data_size = context_state.get('elements_data_size', None)
    if elements_data_size:
      return elements_data_size

    if self._HasElementsDataSize():
      elements_data_size = self._data_type_definition.GetByteSize()
      if elements_data_size is None:
        try:
          elements_data_size = self._EvaluateElementsDataSize(context)
        except errors.MappingError:
          pass

    elif self._HasElementsTerminator():
      element_size_hint = self._element_data_type_definition.GetByteSize()
      if element_size_hint is None:
        subcontext = context_state.get('context', None)
        element_size_hint = self._element_data_type_map.GetSizeHint(
            context=subcontext)

      if element_size_hint is not None:
        elements_data_size = context_state.get('elements_data_offset', 0)
        elements_data_size += element_size_hint

    elif self._HasNumberOfElements():
      number_of_elements = context_state.get('number_of_elements', None)
      if number_of_elements is None:
        try:
          number_of_elements = self._EvaluateNumberOfElements(context)
        except errors.MappingError:
          pass

      if number_of_elements is not None:
        element_byte_size = self._element_data_type_definition.GetByteSize()
        if element_byte_size:
          elements_data_size = number_of_elements * element_byte_size
        else:
          subcontext = context_state.get('context', None)
          element_size_hint = self._element_data_type_map.GetSizeHint(
              context=subcontext)
          if element_size_hint is not None:
            elements_data_size = context_state.get('elements_data_offset', 0)
            elements_data_size += element_size_hint

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
      self, byte_stream, byte_offset=0, context=None, recursion_depth=0,
      **unused_kwargs):
    """Maps a sequence of composite data types on a byte stream.

    Args:
      byte_stream (bytes): byte stream.
      byte_offset (Optional[int]): offset into the byte stream where to start.
      context (Optional[DataTypeMapContext]): data type map context.
      recursion_depth (Optional[int]): recursion depth.

    Returns:
      tuple[object, ...]: mapped values.

    Raises:
      ByteStreamTooSmallError: if the byte stream is too small.
      MappingError: if the data type definition cannot be mapped on
          the byte stream.
    """
    if recursion_depth > self._MAXIMUM_RECURSION_DEPTH:
      raise errors.MappingError('At maximum recursion depth')

    elements_data_size = None
    elements_terminator = None
    number_of_elements = None

    if self._HasElementsDataSize():
      elements_data_size = self._EvaluateElementsDataSize(context)

      element_byte_size = self._element_data_type_definition.GetByteSize()
      if element_byte_size is not None:
        number_of_elements, _ = divmod(elements_data_size, element_byte_size)
      else:
        elements_terminator = (
            self._element_data_type_definition.elements_terminator)

    elif self._HasElementsTerminator():
      elements_terminator = self._data_type_definition.elements_terminator

    elif self._HasNumberOfElements():
      number_of_elements = self._EvaluateNumberOfElements(context)

    if elements_terminator is None and number_of_elements is None:
      raise errors.MappingError(
          'Unable to determine element terminator or number of elements')

    context_state = getattr(context, 'state', {})

    elements_data_offset = context_state.get('elements_data_offset', 0)
    element_index = context_state.get('element_index', 0)
    element_value = None
    mapped_values = context_state.get('mapped_values', [])
    subcontext = context_state.get('context', None)

    if not subcontext:
      subcontext = DataTypeMapContext()

    if context:
      context.byte_size = None

    try:
      while byte_stream[byte_offset:]:
        if (number_of_elements is not None and
            element_index == number_of_elements):
          break

        if (elements_data_size is not None and
            elements_data_offset >= elements_data_size):
          break

        element_value = self._element_data_type_map.MapByteStream(
            byte_stream, byte_offset=byte_offset, context=subcontext,
            recursion_depth=recursion_depth + 1)

        byte_offset += subcontext.byte_size
        elements_data_offset += subcontext.byte_size
        element_index += 1
        mapped_values.append(element_value)

        if (elements_terminator is not None and
            element_value == elements_terminator):
          break

    except errors.ByteStreamTooSmallError:
      context_state['context'] = subcontext
      context_state['element_index'] = element_index
      context_state['elements_data_offset'] = elements_data_offset
      context_state['elements_data_size'] = elements_data_size
      context_state['mapped_values'] = mapped_values
      context_state['number_of_elements'] = number_of_elements

      requested_size = byte_offset + (subcontext.requested_size or 0)
      byte_stream_size = len(byte_stream)
      raise errors.ByteStreamTooSmallError(
          f'Byte stream too small requested: {requested_size:d} available: '
          f'{byte_stream_size:d}')

    except Exception as exception:
      raise errors.MappingError(exception)

    if number_of_elements is not None and element_index != number_of_elements:
      context_state['context'] = subcontext
      context_state['element_index'] = element_index
      context_state['elements_data_offset'] = elements_data_offset
      context_state['elements_data_size'] = elements_data_size
      context_state['mapped_values'] = mapped_values
      context_state['number_of_elements'] = number_of_elements

      error_element_index = element_index - 1

      raise errors.ByteStreamTooSmallError(
          f'Unable to read: {self._data_type_definition.name:s} from byte '
          f'stream at offset: {byte_offset:d} with error: missing element: '
          f'{error_element_index:d}')

    if (elements_terminator is not None and
        element_value != elements_terminator and (
            elements_data_size is None or
            elements_data_offset < elements_data_size)):
      context_state['context'] = subcontext
      context_state['element_index'] = element_index
      context_state['elements_data_offset'] = elements_data_offset
      context_state['elements_data_size'] = elements_data_size
      context_state['mapped_values'] = mapped_values
      context_state['number_of_elements'] = number_of_elements

      raise errors.ByteStreamTooSmallError(
          f'Unable to read: {self._data_type_definition.name:s} from byte '
          f'stream at offset: {byte_offset:d} with error: unable to find '
          f'elements terminator')

    if context:
      context.byte_size = elements_data_offset
      context.state = {}

    return tuple(mapped_values)

  def _LinearFoldByteStream(self, mapped_value, **unused_kwargs):
    """Folds the data type into a byte stream.

    Args:
      mapped_value (object): mapped value.

    Returns:
      bytes: byte stream.

    Raises:
      FoldingError: if the data type definition cannot be folded into
          the byte stream.
    """
    try:
      return self._operation.WriteTo(mapped_value)

    except Exception as exception:
      raise errors.FoldingError(
          f'Unable to write: {self._data_type_definition.name:s} to byte '
          f'stream with error: {exception!s}')

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
      ByteStreamTooSmallError: if the byte stream is too small.
      MappingError: if the data type definition cannot be mapped on
          the byte stream.
    """
    context_state = getattr(context, 'state', {})

    elements_data_size = self._data_type_definition.GetByteSize()

    if context:
      context.byte_size = None
      context.requested_size = elements_data_size

    try:
      byte_stream_size = len(byte_stream)

    except Exception as exception:
      raise errors.MappingError(exception)

    if byte_stream_size - byte_offset < elements_data_size:
      context_state['elements_data_size'] = elements_data_size

      raise errors.ByteStreamTooSmallError(
          f'Byte stream too small requested: {elements_data_size:d} '
          f'available: {byte_stream_size:d}')

    try:
      struct_tuple = self._operation.ReadFrom(byte_stream[byte_offset:])
      mapped_values = map(self._element_data_type_map.MapValue, struct_tuple)

    except Exception as exception:
      raise errors.MappingError(
          f'Unable to read: {self._data_type_definition.name:s} from byte '
          f'stream at offset: {byte_offset:d} with error: {exception!s}')

    if context:
      context.byte_size = elements_data_size
      context.state = {}

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
      if element_byte_size is None:
        return None

      number_of_elements, _ = divmod(
          self._data_type_definition.elements_data_size, element_byte_size)

    elif self._data_type_definition.number_of_elements:
      number_of_elements = self._data_type_definition.number_of_elements

    format_string = self._element_data_type_map.GetStructFormatString()
    if not number_of_elements or not format_string:
      return None

    return f'{number_of_elements:d}{format_string:s}'

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
      FormatError: if the data type map cannot be determined from the data
          type definition.
    """
    super(StreamMap, self).__init__(data_type_definition)
    self._fold_byte_stream = None
    self._map_byte_stream = None

    if self._element_data_type_definition.IsComposite():
      raise errors.FormatError('Unsupported composite element data type')

  def FoldByteStream(self, mapped_value, context=None, **unused_kwargs):
    """Folds the data type into a byte stream.

    Args:
      mapped_value (object): mapped value.
      context (Optional[DataTypeMapContext]): data type map context.

    Returns:
      bytes: byte stream.

    Raises:
      FoldingError: if the data type definition cannot be folded into
          the byte stream.
    """
    elements_data_size = self._CalculateElementsDataSize(context)
    if elements_data_size is not None:
      if elements_data_size != len(mapped_value):
        raise errors.FoldingError(
            'Mismatch between elements data size and mapped value size')

    elif not self._HasElementsTerminator():
      raise errors.FoldingError('Unable to determine elements data size')

    else:
      elements_terminator = self._data_type_definition.elements_terminator
      elements_terminator_size = len(elements_terminator)
      if mapped_value[-elements_terminator_size:] != elements_terminator:
        mapped_value = b''.join([mapped_value, elements_terminator])

    return mapped_value

  def GetStructFormatString(self):
    """Retrieves the Python struct format string.

    Returns:
      str: format string as used by Python struct or None if format string
          cannot be determined.
    """
    byte_size = self._data_type_definition.GetByteSize()
    if not byte_size:
      return None

    return f'{byte_size:d}B'

  def MapByteStream(
      self, byte_stream, byte_offset=0, context=None, **unused_kwargs):
    """Maps the data type on a byte stream.

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
    context_state = getattr(context, 'state', {})

    elements_data_size = self._CalculateElementsDataSize(context)

    if context:
      context.byte_size = None
      context.requested_size = elements_data_size

    if elements_data_size is not None:
      try:
        byte_stream_size = len(byte_stream)

      except Exception as exception:
        raise errors.MappingError(exception)

      if byte_stream_size - byte_offset < elements_data_size:
        context_state['elements_data_size'] = elements_data_size

        raise errors.ByteStreamTooSmallError(
            f'Byte stream too small requested: {elements_data_size:d} '
            f'available: {byte_stream_size:d}')

    elif not self._HasElementsTerminator():
      raise errors.MappingError(
          'Unable to determine elements data size and missing elements '
          'terminator')

    else:
      element_byte_size = self._element_data_type_definition.GetByteSize()
      elements_data_offset = byte_offset
      next_elements_data_offset = elements_data_offset + element_byte_size

      elements_terminator = self._data_type_definition.elements_terminator
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
        context_state['elements_data_offset'] = (
            elements_data_offset - byte_offset)

        raise errors.ByteStreamTooSmallError(
            f'Unable to read: {self._data_type_definition.name:s} from byte '
            f'stream at offset: {byte_offset:d} with error: unable to find '
            f'elements terminator')

    if context:
      context.byte_size = elements_data_size
      context.state = {}

    return byte_stream[byte_offset:byte_offset + elements_data_size]


class PaddingMap(DataTypeMap):
  """Padding data type map."""

  def _CalculatePaddingSize(self, byte_offset):
    """Calculates the padding size.

    Args:
      byte_offset (int): offset into the byte stream where to start.

    Returns:
      int: size of the padding in number of bytes.
    """
    alignment_size = self._data_type_definition.alignment_size

    _, byte_size = divmod(byte_offset, alignment_size)
    if byte_size > 0:
      byte_size = alignment_size - byte_size

    return byte_size

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
    return mapped_value

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

  def GetSizeHint(self, byte_offset=0, context=None, **unused_kwargs):
    """Retrieves a hint about the size.

    Args:
      byte_offset (Optional[int]): offset into the byte stream where to start.
      context (Optional[DataTypeMapContext]): data type map context, used to
          determine the size hint.

    Returns:
      int: hint of the number of bytes needed from the byte stream or None.
    """
    size_hint = getattr(context, 'byte_size', None)
    if size_hint is not None:
      return size_hint

    return self._CalculatePaddingSize(byte_offset)

  def GetStructFormatString(self):  # pylint: disable=redundant-returns-doc
    """Retrieves the Python struct format string.

    Returns:
      str: format string as used by Python struct or None if format string
          cannot be determined.
    """
    return None

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
      ByteStreamTooSmallError: if the byte stream is too small.
    """
    padding_size = self._CalculatePaddingSize(byte_offset)

    if context:
      context.byte_size = None
      context.requested_size = padding_size

    byte_stream_size = len(byte_stream)
    if byte_stream_size - byte_offset < padding_size:
      raise errors.ByteStreamTooSmallError(
          f'Byte stream too small requested: {padding_size:d} available: '
          f'{byte_stream_size:d}')

    mapped_value = byte_stream[byte_offset:byte_offset + padding_size]

    if context:
      context.byte_size = padding_size

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


class StringMap(StreamMap):
  """String data type map."""

  def FoldByteStream(self, mapped_value, **kwargs):  # pylint: disable=arguments-differ
    """Folds the data type into a byte stream.

    Args:
      mapped_value (object): mapped value.

    Returns:
      bytes: byte stream.

    Raises:
      FoldingError: if the data type definition cannot be folded into
          the byte stream.
    """
    try:
      byte_stream = mapped_value.encode(self._data_type_definition.encoding)

    except Exception as exception:
      raise errors.FoldingError(
          f'Unable to write: {self._data_type_definition.name:s} to byte '
          f'stream with error: {exception!s}')

    return super(StringMap, self).FoldByteStream(byte_stream, **kwargs)

  def MapByteStream(self, byte_stream, byte_offset=0, **kwargs):  # pylint: disable=arguments-differ
    """Maps the data type on a byte stream.

    Args:
      byte_stream (bytes): byte stream.
      byte_offset (Optional[int]): offset into the byte stream where to start.

    Returns:
      str: mapped values.

    Raises:
      ByteStreamTooSmallError: if the byte stream is too small.
      MappingError: if the data type definition cannot be mapped on
          the byte stream.
    """
    byte_stream = super(StringMap, self).MapByteStream(
        byte_stream, byte_offset=byte_offset, **kwargs)

    if self._HasElementsTerminator():
      # Remove the elements terminator and any trailing data from
      # the byte stream.
      elements_terminator = self._data_type_definition.elements_terminator
      elements_terminator_size = len(elements_terminator)

      byte_offset = 0
      byte_stream_size = len(byte_stream)

      while byte_offset < byte_stream_size:
        end_offset = byte_offset + elements_terminator_size
        if byte_stream[byte_offset:end_offset] == elements_terminator:
          break

        byte_offset += elements_terminator_size

      byte_stream = byte_stream[:byte_offset]

    try:
      return byte_stream.decode(self._data_type_definition.encoding)

    except Exception as exception:
      raise errors.MappingError(
          f'Unable to read: {self._data_type_definition.name:s} from byte '
          f'stream at offset: {byte_offset:d} with error: {exception!s}')


class StructureMap(StorageDataTypeMap):
  """Structure data type map."""

  def __init__(self, data_type_definition):
    """Initializes a structure data type map.

    Args:
      data_type_definition (DataTypeDefinition): data type definition.
    """
    super(StructureMap, self).__init__(data_type_definition)
    self._attribute_names = None
    self._data_type_maps = None
    self._fold_byte_stream = None
    self._format_string = None
    self._map_byte_stream = None
    self._number_of_attributes = None
    self._operation = None
    self._structure_values_class = (
        runtime.StructureValuesClassFactory.CreateClass(
            data_type_definition))

    self._GetMemberDataTypeMaps(data_type_definition)

    if self._CheckLinearMap(data_type_definition):
      self._fold_byte_stream = self._LinearFoldByteStream
      self._map_byte_stream = self._LinearMapByteStream
      self._operation = self._GetByteStreamOperation()
    else:
      self._fold_byte_stream = self._CompositeFoldByteStream
      self._map_byte_stream = self._CompositeMapByteStream

  def _CheckLinearMap(self, data_type_definition):
    """Determines if the data type definition supports using a linear map.

    Args:
      data_type_definition (DataTypeDefinition): structure data type definition.

    Returns:
      bool: True if a composite map is needed, False otherwise.

    Raises:
      FormatError: if a composite map is needed cannot be determined from the
          data type definition.
    """
    if not data_type_definition:
      raise errors.FormatError('Missing data type definition')

    members = getattr(data_type_definition, 'members', None)
    if not members:
      raise errors.FormatError('Invalid data type definition missing members')

    supports_linear_map = True
    last_member_byte_order = data_type_definition.byte_order

    for member_definition in members:
      if (member_definition.IsComposite() or
          isinstance(member_definition, data_types.PaddingDefinition)):
        supports_linear_map = False
        break

      if (last_member_byte_order != definitions.BYTE_ORDER_NATIVE and
          member_definition.byte_order != definitions.BYTE_ORDER_NATIVE and
          last_member_byte_order != member_definition.byte_order):
        supports_linear_map = False
        break

      last_member_byte_order = member_definition.byte_order

    return supports_linear_map

  def _CompositeFoldByteStream(
      self, mapped_value, context=None, **unused_kwargs):
    """Folds the data type into a byte stream.

    Args:
      mapped_value (object): mapped value.
      context (Optional[DataTypeMapContext]): data type map context.

    Returns:
      bytes: byte stream.

    Raises:
      FoldingError: if the data type definition cannot be folded into
          the byte stream.
    """
    context_state = getattr(context, 'state', {})

    attribute_index = context_state.get('attribute_index', 0)
    subcontext = context_state.get('context', None)

    if not subcontext:
      subcontext = DataTypeMapContext(values={
          type(mapped_value).__name__: mapped_value})

    data_attributes = []

    for attribute_index in range(attribute_index, self._number_of_attributes):
      attribute_name = self._attribute_names[attribute_index]
      data_type_map = self._data_type_maps[attribute_index]

      member_value = getattr(mapped_value, attribute_name, None)
      if data_type_map is None or member_value is None:
        continue

      member_data = data_type_map.FoldByteStream(
          member_value, context=subcontext)
      if member_data is None:
        return None

      data_attributes.append(member_data)

    if context:
      context.state = {}

    return b''.join(data_attributes)

  def _CompositeMapByteStream(
      self, byte_stream, byte_offset=0, context=None, recursion_depth=0,
      **unused_kwargs):
    """Maps a sequence of composite data types on a byte stream.

    Args:
      byte_stream (bytes): byte stream.
      byte_offset (Optional[int]): offset into the byte stream where to start.
      context (Optional[DataTypeMapContext]): data type map context.
      recursion_depth (Optional[int]): recursion depth.

    Returns:
      object: mapped value.

    Raises:
      ByteStreamTooSmallError: if the byte stream is too small.
      MappingError: if the data type definition cannot be mapped on
          the byte stream.
    """
    if recursion_depth > self._MAXIMUM_RECURSION_DEPTH:
      raise errors.MappingError('At maximum recursion depth')

    context_state = getattr(context, 'state', {})
    context_values = getattr(context, 'values', {})

    attribute_index = context_state.get('attribute_index', 0)
    mapped_values = context_state.get('mapped_values', None)
    subcontext = context_state.get('context', None)

    if not mapped_values:
      mapped_values = self._structure_values_class()
    if not subcontext:
      subcontext_values = {type(mapped_values).__name__: mapped_values}
      # Pass externally defined values.
      subcontext_values.update(context_values)
      subcontext = DataTypeMapContext(values=subcontext_values)

    if context:
      context.byte_size = None

    members_data_size = 0

    for attribute_index in range(attribute_index, self._number_of_attributes):
      attribute_name = self._attribute_names[attribute_index]
      data_type_map = self._data_type_maps[attribute_index]
      member_definition = self._data_type_definition.members[attribute_index]

      # TODO: pre-compile condition
      condition = getattr(member_definition, 'condition', None)
      if condition:
        namespace = dict(subcontext.values)
        # Make sure __builtins__ contains an empty dictionary.
        namespace['__builtins__'] = {}

        try:
          condition_result = eval(condition, namespace)  # pylint: disable=eval-used
        except Exception as exception:
          raise errors.MappingError(
              f'Unable to evaluate condition with error: {exception!s}')

        if not isinstance(condition_result, bool):
          raise errors.MappingError(
              'Condition does not result in a boolean value')

        if not condition_result:
          continue

      try:
        value = data_type_map.MapByteStream(
            byte_stream, byte_offset=byte_offset, context=subcontext,
            recursion_depth=recursion_depth + 1)
        setattr(mapped_values, attribute_name, value)

      except errors.ByteStreamTooSmallError:
        context_state['attribute_index'] = attribute_index
        context_state['context'] = subcontext
        context_state['mapped_values'] = mapped_values
        context_state['members_data_size'] = members_data_size

        requested_size = byte_offset + (subcontext.requested_size or 0)
        byte_stream_size = len(byte_stream)

        raise errors.ByteStreamTooSmallError(
            f'Byte stream too small requested: {requested_size:d} available: '
            f'{byte_stream_size:d}')

      except Exception as exception:
        raise errors.MappingError(exception)

      supported_values = getattr(member_definition, 'values', None)
      if supported_values and value not in supported_values:
        supported_values_string = ', '.join([
            f'{value!s}' for value in supported_values])
        raise errors.MappingError(
            f'Value: {value!s} not in supported values: '
            f'{supported_values_string:s}')

      byte_offset += subcontext.byte_size
      members_data_size += subcontext.byte_size

    if attribute_index != (self._number_of_attributes - 1):
      context_state['attribute_index'] = attribute_index
      context_state['context'] = subcontext
      context_state['mapped_values'] = mapped_values
      context_state['members_data_size'] = members_data_size

      raise errors.ByteStreamTooSmallError(
          f'Unable to read: {self._data_type_definition.name:s} from byte '
          f'stream at offset: {byte_offset:d} with error: missing attribute: '
          f'{attribute_index:d}')

    if context:
      context.byte_size = members_data_size
      context.state = {}

    return mapped_values

  def _GetMemberDataTypeMaps(self, data_type_definition):
    """Retrieves the member data type maps.

    Args:
      data_type_definition (DataTypeDefinition): data type definition.

    Raises:
      FormatError: if the data type maps cannot be determined from the data
          type definition.
    """
    if not data_type_definition:
      raise errors.FormatError('Missing data type definition')

    members = getattr(data_type_definition, 'members', None)
    if not members:
      raise errors.FormatError('Invalid data type definition missing members')

    self._attribute_names = []
    self._data_type_maps = []
    self._number_of_attributes = 0

    data_type_map_cache = {}
    members_data_size = 0
    for member_definition in members:
      member_name = member_definition.name

      if isinstance(member_definition, data_types.MemberDataTypeDefinition):
        member_definition = member_definition.member_data_type_definition

      if (data_type_definition.byte_order != definitions.BYTE_ORDER_NATIVE and
          member_definition.byte_order == definitions.BYTE_ORDER_NATIVE):
        # Make a copy of the data type definition where byte-order can be
        # safely changed.
        member_definition = copy.copy(member_definition)
        member_definition.name = (
            f'_{data_type_definition.name:s}_{member_definition.name:s}')
        member_definition.byte_order = data_type_definition.byte_order

      if member_definition.name not in data_type_map_cache:
        data_type_map = DataTypeMapFactory.CreateDataTypeMapByType(
            member_definition)
        data_type_map_cache[member_definition.name] = data_type_map

      data_type_map = data_type_map_cache[member_definition.name]
      if members_data_size is not None:
        byte_size = member_definition.GetByteSize()
        if byte_size is None:
          members_data_size = None
        else:
          members_data_size += byte_size

      self._attribute_names.append(member_name)
      self._data_type_maps.append(data_type_map)
      self._number_of_attributes += 1

  def _LinearFoldByteStream(self, mapped_value, **unused_kwargs):
    """Folds the data type into a byte stream.

    Args:
      mapped_value (object): mapped value.

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
      raise errors.FoldingError(
          f'Unable to write: {self._data_type_definition.name:s} to byte '
          f'stream with error: {exception!s}')

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
      ByteStreamTooSmallError: if the byte stream is too small.
      MappingError: if the data type definition cannot be mapped on
          the byte stream.
    """
    members_data_size = self._data_type_definition.GetByteSize()

    context_state = getattr(context, 'state', {})

    if context:
      context.byte_size = None
      context.requested_size = members_data_size

    try:
      byte_stream_size = len(byte_stream)

    except Exception as exception:
      raise errors.MappingError(exception)

    if byte_stream_size - byte_offset < members_data_size:
      context_state['attribute_index'] = self._number_of_attributes
      context_state['members_data_size'] = members_data_size

      raise errors.ByteStreamTooSmallError(
          f'Byte stream too small requested: {members_data_size:d} available: '
          f'{byte_stream_size:d}')

    try:
      struct_tuple = self._operation.ReadFrom(byte_stream[byte_offset:])
      struct_values = []
      for attribute_index, value in enumerate(struct_tuple):
        data_type_map = self._data_type_maps[attribute_index]
        member_definition = self._data_type_definition.members[attribute_index]

        value = data_type_map.MapValue(value)

        supported_values = getattr(member_definition, 'values', None)
        if supported_values and value not in supported_values:
          supported_values_string = ', '.join([
              f'{value!s}' for value in supported_values])
          raise errors.MappingError(
              f'Value: {value!s} not in supported values: '
              f'{supported_values_string:s}')

        struct_values.append(value)

      mapped_value = self._structure_values_class(*struct_values)

    except Exception as exception:
      raise errors.MappingError(
          f'Unable to read: {self._data_type_definition.name:s} from byte '
          f'stream at offset: {byte_offset:d} with error: {exception!s}')

    if context:
      context.byte_size = members_data_size
      context.state = {}

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
    size_hint = getattr(context, 'byte_size', None)
    if size_hint is not None:
      return size_hint

    context_state = getattr(context, 'state', {})

    attribute_index = context_state.get('attribute_index', 0)
    mapped_values = context_state.get('mapped_values', None)
    subcontext = context_state.get('context', None)

    if not mapped_values:
      mapped_values = self._structure_values_class()
    if not subcontext:
      subcontext_values = {type(mapped_values).__name__: mapped_values}
      subcontext = DataTypeMapContext(values=subcontext_values)

    size_hint = context_state.get('members_data_size', 0)
    for attribute_index in range(attribute_index, self._number_of_attributes):
      data_type_map = self._data_type_maps[attribute_index]
      attribute_size_hint = data_type_map.GetSizeHint(
          byte_offset=size_hint, context=subcontext)

      if attribute_size_hint is None:
        break

      size_hint += attribute_size_hint

      # A new subcontext is created to prevent the current state affecting
      # the size hint calculation of subsequent attributes.
      subcontext = DataTypeMapContext()

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

  def FoldByteStream(self, mapped_value, **unused_kwargs):  # pylint: disable=redundant-returns-doc
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
        f'Unable to fold {self._data_type_definition.TYPE_INDICATOR:s} data '
        f'type into byte stream')

  def MapByteStream(self, byte_stream, **unused_kwargs):  # pylint: disable=redundant-returns-doc
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
        f'Unable to map {self._data_type_definition.TYPE_INDICATOR:s} data '
        f'type to byte stream')


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


class LayoutDataTypeMap(DataTypeMap):
  """Layout data type map."""

  def FoldByteStream(self, mapped_value, **unused_kwargs):  # pylint: disable=redundant-returns-doc
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
        f'Unable to fold {self._data_type_definition.TYPE_INDICATOR:s} data '
        f'type into byte stream')

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


class FormatMap(LayoutDataTypeMap):
  """Format data type map."""

  @property
  def layout(self):
    """list[LayoutElementDefinition]: layout element definitions."""
    return getattr(self._data_type_definition, 'layout', [])

  def MapByteStream(self, byte_stream, **unused_kwargs):  # pylint: disable=redundant-returns-doc
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
        f'Unable to map {self._data_type_definition.TYPE_INDICATOR:s} data '
        f'type to byte stream')


class StructureGroupMap(LayoutDataTypeMap):
  """Structure group data type map."""

  def __init__(self, data_type_definition):
    """Initializes a data type map.

    Args:
      data_type_definition (DataTypeDefinition): data type definition.

    Raises:
      FormatError: if the data type map cannot be determined from the data
          type definition.
    """
    super(StructureGroupMap, self).__init__(data_type_definition)
    self._base_data_type_map = DataTypeMapFactory.CreateDataTypeMapByType(
        data_type_definition.base)
    self._data_type_maps = None

    self._GetMemberDataTypeMaps(data_type_definition)

  def _GetMemberDataTypeMaps(self, data_type_definition):
    """Retrieves the member data type maps.

    Args:
      data_type_definition (DataTypeDefinition): data type definition.

    Raises:
      FormatError: if the data type maps cannot be determined from the data
          type definition.
    """
    if not data_type_definition:
      raise errors.FormatError('Missing data type definition')

    members = getattr(data_type_definition, 'members', None)
    if not members:
      raise errors.FormatError('Invalid data type definition missing members')

    self._data_type_maps = {}

    for group_member_definition in members:
      struct_member_definition = (
          group_member_definition.GetMemberDefinitionByName(
              data_type_definition.identifier))

      if not struct_member_definition:
        raise errors.FormatError(
            f'No such member: {data_type_definition.identifier:s} of: '
            f'{group_member_definition.name:s}')

      if struct_member_definition.values is None:
        raise errors.FormatError(
            f'No values defined for member: '
            f'{data_type_definition.identifier:s} of: '
            f'{group_member_definition.name:s}')

      for value in struct_member_definition.values:
        if value in self._data_type_maps:
          raise errors.FormatError(
              f'Duplicate value: {value!s} for member: '
              f'{data_type_definition.identifier:s} of: '
              f'{group_member_definition.name:s}')

        data_type_map = DataTypeMapFactory.CreateDataTypeMapByType(
            group_member_definition)
        self._data_type_maps[value] = data_type_map

  @decorators.deprecated
  def GetByteSize(self):  # pylint: disable=redundant-returns-doc
    """Retrieves the byte size of the data type map.

    This method is deprecated use GetSizeHint instead.

    Returns:
      int: data type size in bytes or None if size cannot be determined.
    """
    return None

  def GetSizeHint(self, context=None, **kwargs):
    """Retrieves a hint about the size.

    Args:
      context (Optional[DataTypeMapContext]): data type map context, used to
          determine the size hint.

    Returns:
      int: hint of the number of bytes needed from the byte stream or None.
    """
    size_hint = getattr(context, 'byte_size', None)
    if size_hint is not None:
      return size_hint

    context_state = getattr(context, 'state', {})

    member_identifier = context_state.get('member_identifier', None)
    subcontext = context_state.get('context', None)

    if not subcontext:
      subcontext = DataTypeMapContext()

    member_data_type_map = self._data_type_maps.get(member_identifier, None)
    if member_data_type_map:
      return member_data_type_map.GetSizeHint(context=subcontext, **kwargs)

    return self._base_data_type_map.GetSizeHint(context=subcontext, **kwargs)

  def MapByteStream(self, byte_stream, context=None, **kwargs):
    """Maps the data type on a byte stream.

    Args:
      byte_stream (bytes): byte stream.
      context (Optional[DataTypeMapContext]): data type map context.

    Returns:
      object: mapped value.

    Raises:
      ByteStreamTooSmallError: if the byte stream is too small.
      MappingError: if the data type definition cannot be mapped on
          the byte stream.
    """
    context_state = getattr(context, 'state', {})

    member_identifier = context_state.get('member_identifier', None)
    if member_identifier is None:
      subcontext = DataTypeMapContext()
      mapped_base_value = self._base_data_type_map.MapByteStream(
          byte_stream, context=subcontext, **kwargs)

      member_identifier = getattr(
          mapped_base_value, self._data_type_definition.identifier, None)
      if member_identifier is None:
        raise errors.MappingError(
            f'Unable to determine value of '
            f'{self._data_type_definition.identifier:s}')

      context_state['member_identifier'] = member_identifier

    member_data_type_map = self._data_type_maps.get(member_identifier, None)
    if member_data_type_map is None:
      raise errors.MappingError(
          f'Missing member data type map for '
          f'{self._data_type_definition.identifier:s}: '
          f'{member_identifier!s}')

    subcontext = context_state.get('context', None)

    if not subcontext:
      subcontext = DataTypeMapContext()

    if context:
      context.byte_size = None

    try:
      value = member_data_type_map.MapByteStream(
          byte_stream, context=subcontext, **kwargs)

    except errors.ByteStreamTooSmallError as exception:
      context_state['context'] = subcontext
      raise exception

    except Exception as exception:
      raise errors.MappingError(exception)

    if context:
      context.byte_size = subcontext.byte_size
      context.state = {}

    return value


class DataTypeMapFactory(object):
  """Factory for data type maps."""

  # TODO: add support for definitions.TYPE_INDICATOR_FORMAT
  # TODO: add support for definitions.TYPE_INDICATOR_STRUCTURE_FAMILY

  _MAP_PER_DEFINITION = {
      definitions.TYPE_INDICATOR_BOOLEAN: BooleanMap,
      definitions.TYPE_INDICATOR_CHARACTER: CharacterMap,
      definitions.TYPE_INDICATOR_CONSTANT: ConstantMap,
      definitions.TYPE_INDICATOR_ENUMERATION: EnumerationMap,
      definitions.TYPE_INDICATOR_FLOATING_POINT: FloatingPointMap,
      definitions.TYPE_INDICATOR_FORMAT: FormatMap,
      definitions.TYPE_INDICATOR_INTEGER: IntegerMap,
      definitions.TYPE_INDICATOR_PADDING: PaddingMap,
      definitions.TYPE_INDICATOR_SEQUENCE: SequenceMap,
      definitions.TYPE_INDICATOR_STREAM: StreamMap,
      definitions.TYPE_INDICATOR_STRING: StringMap,
      definitions.TYPE_INDICATOR_STRUCTURE: StructureMap,
      definitions.TYPE_INDICATOR_STRUCTURE_GROUP: StructureGroupMap,
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
    data_type_map = None

    data_type_definition = self.GetDataTypeDefinition(definition_name)
    if data_type_definition:
      data_type_map = DataTypeMapFactory.CreateDataTypeMapByType(
          data_type_definition)

    return data_type_map

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

  def GetDataTypeDefinition(self, definition_name):
    """Retrieves a specific data type definition by name.

    Args:
      definition_name (str): name of the data type definition.

    Returns:
      DataTypeDefinition: data type definition or None if the date type
          definition is not available.
    """
    return self._definitions_registry.GetDefinitionByName(definition_name)
