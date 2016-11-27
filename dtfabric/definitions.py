# -*- coding: utf-8 -*-
"""Structure and type definitions."""


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
    self.units = None


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
    byte_order (str): byte_order.
    description (str): description.
    members (list[object]): members.
    name (str): name.
  """

  def __init__(self, name, aliases=None, byte_order=None, description=None):
    """Initializes a data type definition.

    Args:
      name (str): name.
      aliases (Optional[list[str]]): aliases.
      byte_order (Optional[str]): byte order.
      description (Optional[str]): description.
    """
    super(StructureDefinition, self).__init__(
        name, aliases=aliases, description=description)
    self.aliases = aliases or []
    self.byte_order = byte_order
    self.description = description
    self.name = name
    self.members = []


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
