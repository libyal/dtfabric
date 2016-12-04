# -*- coding: utf-8 -*-
"""Structure and type definitions."""

import abc


class DataTypeDefinition(object):
  """Class that defines the data type definition interface.

  Attributes:
    aliases (list[str]): aliases.
    description (str): description.
    name (str): name.
  """

  def __init__(self, name, aliases=None, description=None):
    """Initializes a data type definition.

    Args:
      name (str): name.
      aliases (Optional[list[str]]): aliases.
      description (Optional[str]): description.
    """
    super(DataTypeDefinition, self).__init__()
    self.aliases = aliases or []
    self.description = description
    self.name = name

  @abc.abstractmethod
  def GetByteSize(self):
    """Determines the byte size of the data type definition.

    Returns:
      int: data type size in bytes or None if size cannot be determined.
    """


class IntegerDefinition(DataTypeDefinition):
  """Class that defines an integer data type definition.

  Attributes:
    format (str): format of the data type.
    size (int|list[int]): size of the data type.
    units (str): units of the size of the data type.
  """

  def __init__(self, name, aliases=None, description=None):
    """Initializes a data type definition.

    Args:
      name (str): name.
      aliases (Optional[list[str]]): aliases.
      description (Optional[str]): description.
    """
    super(IntegerDefinition, self).__init__(
        name, aliases=aliases, description=description)
    self.format = None
    self.size = None
    self.units = u'bytes'

  def GetByteSize(self):
    """Determines the byte size of the data type definition.

    Returns:
      int: data type size in bytes or None if size cannot be determined.
    """
    return self.size


class SequenceDefinition(object):
  """Class that defines a sequence definition.

  Attributes:
    number_of_items (int): number of items.
  """

  def __init__(self, number_of_items=None):
    """Initializes a sequence definition.

    Args:
      number_of_items (Optional[int]): number of items.
    """
    super(SequenceDefinition, self).__init__()
    self.number_of_items = number_of_items


class StructureDefinition(DataTypeDefinition):
  """Class that defines a structure data type definition.

  Attributes:
    aliases (list[str]): aliases.
    description (str): description.
    members (list[object]): members.
    name (str): name.
  """

  def __init__(self, name, aliases=None, description=None):
    """Initializes a data type definition.

    Args:
      name (str): name.
      aliases (Optional[list[str]]): aliases.
      description (Optional[str]): description.
    """
    super(StructureDefinition, self).__init__(
        name, aliases=aliases, description=description)
    self._size = None
    self.aliases = aliases or []
    self.description = description
    self.name = name
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


class UnionDefinition(object):
  """Class that defines an union definition.

  Attributes:
    members (list[object]): members.
    name (str): name.
  """

  def __init__(self, name=None):
    """Initializes an union definition.

    Args:
      name (Optional[str]): name.
    """
    super(UnionDefinition, self).__init__()
    self.members = []
    self.name = name
