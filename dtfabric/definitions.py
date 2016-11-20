# -*- coding: utf-8 -*-
"""Structure and type definitions."""


class BaseDefinition(object):
  """Class that defines the definition interface."""


class StructureDefinition(BaseDefinition):
  """Class that defines a structure definition.

  Attributes:
    aliases (list[str]): aliases.
    attributes (list[object]): attributes.
    byte_order (str): byte_order.
    description (str): description.
    name (str): name.
  """

  def __init__(self, name, aliases=None, byte_order=None, description=None):
    """Initializes a structure definition.

    Args:
      name (str): name.
      aliases (Optional[list[str]]): aliases.
      byte_order (Optional[str]): byte order.
      description (Optional[str]): description.
    """
    super(StructureDefinition, self).__init__()
    self.aliases = aliases or []
    self.attributes = []
    self.byte_order = byte_order
    self.description = description
    self.name = name


class StructureAttributeDefinition(BaseDefinition):
  """Class that defines a structure attribute definition.

  Attributes:
    aliases (list[str]): aliases.
    data_type (str): data type.
    description (str): description.
    name (str): name.
  """

  def __init__(self, name, aliases=None, data_type=None, description=None):
    """Initializes a strucute attribute definition.

    Args:
      name (str): name.
      aliases (Optional[list[str]]): aliases.
      data_type (Optional[str]): data type.
      description (Optional[str]): description.
    """
    super(StructureAttributeDefinition, self).__init__()
    self.aliases = aliases or []
    self.data_type = data_type
    self.description = description
    self.name = name


class TypeDefinition(BaseDefinition):
  """Class that defines a type definition.

  Attributes:
    aliases (list[str]): aliases.
    data_type (str): data type.
    description (str): description.
    name (str): name.
  """

  def __init__(self, name, aliases=None, data_type=None, description=None):
    """Initializes a type definition.

    Args:
      name (str): name.
      aliases (Optional[list[str]]): aliases.
      data_type (Optional[str]): data type.
      description (Optional[str]): description.
    """
    super(TypeDefinition, self).__init__()
    self.aliases = aliases or []
    self.data_type = data_type
    self.description = description
    self.name = name
