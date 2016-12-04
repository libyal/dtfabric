# -*- coding: utf-8 -*-
"""Structure and type definitions."""

import abc


class DataTypeDefinition(object):
  """Class that defines the data type definition interface.

  Attributes:
    aliases (list[str]): aliases.
    description (str): description.
    name (str): name.
    urls (list[str]): URLs.
  """

  def __init__(self, name, aliases=None, description=None, urls=None):
    """Initializes a data type definition.

    Args:
      name (str): name.
      aliases (Optional[list[str]]): aliases.
      description (Optional[str]): description.
      urls (Optional[list[str]]): URLs.
    """
    super(DataTypeDefinition, self).__init__()
    self.aliases = aliases or []
    self.description = description
    self.name = name
    self.urls = urls

  @abc.abstractmethod
  def GetByteSize(self):
    """Determines the byte size of the data type definition.

    Returns:
      int: data type size in bytes or None if size cannot be determined.
    """


class PrimitiveDataTypeDefinition(DataTypeDefinition):
  """Class that defines a primitive data type definition.

  Attributes:
    size (int|list[int]): size of the data type.
    units (str): units of the size of the data type.
  """

  def __init__(self, name, aliases=None, description=None, urls=None):
    """Initializes a primitive data type definition.

    Args:
      name (str): name.
      aliases (Optional[list[str]]): aliases.
      description (Optional[str]): description.
      urls (Optional[list[str]]): URLs.
    """
    super(PrimitiveDataTypeDefinition, self).__init__(
        name, aliases=aliases, description=description, urls=urls)
    self.size = None
    self.units = u'bytes'

  def GetByteSize(self):
    """Determines the byte size of the data type definition.

    Returns:
      int: data type size in bytes or None if size cannot be determined.
    """
    if self.units == u'bytes':
      return self.size


class BooleanDefinition(PrimitiveDataTypeDefinition):
  """Class that defines a boolean data type definition."""


class CharacterDefinition(PrimitiveDataTypeDefinition):
  """Class that defines a character data type definition."""


class IntegerDefinition(PrimitiveDataTypeDefinition):
  """Class that defines an integer data type definition.

  Attributes:
    format (str): format of the data type.
  """

  def __init__(self, name, aliases=None, description=None, urls=None):
    """Initializes an integer data type definition.

    Args:
      name (str): name.
      aliases (Optional[list[str]]): aliases.
      description (Optional[str]): description.
      urls (Optional[list[str]]): URLs.
    """
    super(IntegerDefinition, self).__init__(
        name, aliases=aliases, description=description, urls=urls)
    self.format = None


class StructureDefinition(DataTypeDefinition):
  """Class that defines a structure data type definition.

  Attributes:
    members (list[object]): members.
  """

  def __init__(self, name, aliases=None, description=None, urls=None):
    """Initializes a data type definition.

    Args:
      name (str): name.
      aliases (Optional[list[str]]): aliases.
      description (Optional[str]): description.
      urls (Optional[list[str]]): URLs.
    """
    super(StructureDefinition, self).__init__(
        name, aliases=aliases, description=description, urls=urls)
    self._size = None
    self.members = []

  def GetByteSize(self):
    """Determines the byte size of the data type definition.

    Returns:
      int: data type size in bytes or None if size cannot be determined.
    """
    if self._size is None:
      self._size = 0
      for struct_member in self.members:
        struct_member_size = struct_member.GetSize()
        if self._structure_definition is None:
          self._size = None
          break

        self._size += struct_member_size

    return self._size


class StructureMemberDefinition(object):
  """Class that defines a structure data type member definition.

  Attributes:
    aliases (list[str]): aliases.
    data_type (str): data type.
    description (str): description.
    name (str): name.
  """

  def __init__(self, name, aliases=None, data_type=None, description=None):
    """Initializes a structure member definition.

    Args:
      name (str): name.
      aliases (Optional[list[str]]): aliases.
      data_type (Optional[str]): data type.
      description (Optional[str]): description.
    """
    super(StructureMemberDefinition, self).__init__()
    self.aliases = aliases or []
    self.data_type = data_type
    self.description = description
    self.name = name

  def GetByteSize(self):
    """Determines the byte size of the data type definition.

    Returns:
      int: data type size in bytes or None if size cannot be determined.
    """
    # TODO: implement size based on data type.


class SequenceStructureMemberDefinition(StructureMemberDefinition):
  """Class that defines a sequence structure data type member definition.

  Attributes:
    data_size (int): data size.
    number_of_items (int): number of items.
  """

  def __init__(
      self, name, aliases=None, data_type=None, description=None):
    """Initializes a sequence structure data type member definition.

    Args:
      name (str): name.
      aliases (Optional[list[str]]): aliases.
      data_type (Optional[str]): data type.
      description (Optional[str]): description.
    """
    super(SequenceStructureMemberDefinition, self).__init__(
        name, aliases=aliases, data_type=data_type, description=description)
    self.data_size = None
    # TODO: add expression support.
    self.number_of_items = None

  def GetByteSize(self):
    """Determines the byte size of the data type definition.

    Returns:
      int: data type size in bytes or None if size cannot be determined.
    """
    if self.data_size:
      return self.data_size

    # TODO: implement size based on expression.
    # TODO: implement size based on data type x number of items.


class UnionStructureMemberDefinition(StructureMemberDefinition):
  """Class that defines an union structure data type member definition.

  Attributes:
    members (list[object]): members.
    name (str): name.
  """

  def __init__(
      self, name, aliases=None, data_size=None, data_type=None,
      description=None):
    """Initializes an union structure data type member definition.

    Args:
      name (str): name.
      aliases (Optional[list[str]]): aliases.
      data_size (Optional[int]): data size.
      data_type (Optional[str]): data type.
      description (Optional[str]): description.
    """
    super(UnionStructureMemberDefinition, self).__init__(
        name, aliases=aliases, data_type=data_type, description=description)
    self.members = []

  def GetByteSize(self):
    """Determines the byte size of the data type definition.

    Returns:
      int: data type size in bytes or None if size cannot be determined.
    """
    # TODO: implement size based on largest member.
