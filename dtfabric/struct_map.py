# -*- coding: utf-8 -*-
"""Structure map implementation."""


class StructureMap(object):
  """Structure map.

  Attributes:
    aliases (list[str]): aliases.
    attributes (list[object]): attributes.
    byte_order (str): byte_order.
    description (str): description.
    name (str): name.
  """

  def __init__(self):
    """Initializes a structure map."""
    super(StructureMap, self).__init__()
    self.aliases = []
    self.attributes = []
    self.byte_order = None
    self.description = None
    self.name = None
