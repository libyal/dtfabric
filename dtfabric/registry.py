# -*- coding: utf-8 -*-
"""The definitions registry."""


class DataTypeDefinitionsRegistry(object):
  """Class that implements a data type definitions registry."""

  def __init__(self):
    """Initializes a data type definitions registry."""
    super(DataTypeDefinitionsRegistry, self).__init__()
    self._aliases = {}
    self._definitions = {}

  def DeregisterDefinition(self, data_type_definition):
    """Deregisters a data type definition.

    The data type definitions are identified based on their lower case name.

    Args:
      data_type_definition (DataTypeDefinition): data type definition.

    Raises:
      KeyError: if a data type definition is not set for the corresponding
          name.
    """
    name = data_type_definition.name.lower()
    if name not in self._definitions:
      raise KeyError(u'Definition not set for name: {0:s}.'.format(
          data_type_definition.name))

    del self._definitions[name]

  def GetDefinitionByName(self, name):
    """Retrieves a specific data type definition by name.

    Args:
      name (str): name of the data type definition.

    Returns:
      DataTypeDefinition: data type definition or None if not available.
    """
    data_type_definition = None
    if name:
      data_type_definition = self._definitions.get(name.lower(), None)

    # TODO: query aliases.

    return data_type_definition

  def GetDefinitions(self):
    """Retrieves the data type definitions.

    Returns:
      list[DataTypeDefinition]: data type definitions.
    """
    return self._definitions.values()

  def RegisterDefinition(self, data_type_definition):
    """Registers a data type definition.

    The data type definitions are identified based on their lower case name.

    Args:
      data_type_definition (DataTypeDefinition): data type definitions.

    Raises:
      KeyError: if data type definition is already set for the corresponding
          name.
    """
    name = data_type_definition.name.lower()
    if name in self._definitions:
      raise KeyError(u'Definition already set for name: {0:s}.'.format(
          data_type_definition.name))

    for alias in data_type_definition.aliases:
      if alias in self._aliases:
        raise KeyError(u'Alias already set for name: {0:s}.'.format(alias))

    self._definitions[name] = data_type_definition
    self._aliases[data_type_definition.name] = name

    for alias in data_type_definition.aliases:
      self._aliases[alias] = name
