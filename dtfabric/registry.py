# -*- coding: utf-8 -*-
"""The data type definitions registry."""

from __future__ import unicode_literals

from dtfabric import definitions


class DataTypeDefinitionsRegistry(object):
  """Data type definitions registry."""

  def __init__(self):
    """Initializes a data type definitions registry."""
    super(DataTypeDefinitionsRegistry, self).__init__()
    self._aliases = {}
    self._definitions = {}
    self._format_definitions = []

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
      raise KeyError('Definition not set for name: {0:s}.'.format(
          data_type_definition.name))

    del self._definitions[name]

  def GetDefinitionByName(self, name):
    """Retrieves a specific data type definition by name.

    Args:
      name (str): name of the data type definition.

    Returns:
      DataTypeDefinition: data type definition or None if not available.
    """
    lookup_name = name.lower()
    if lookup_name not in self._definitions:
      lookup_name = self._aliases.get(name, None)

    return self._definitions.get(lookup_name, None)

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
    name_lower = data_type_definition.name.lower()
    if name_lower in self._definitions:
      raise KeyError('Definition already set for name: {0:s}.'.format(
          data_type_definition.name))

    if data_type_definition.name in self._aliases:
      raise KeyError('Alias already set for name: {0:s}.'.format(
          data_type_definition.name))

    for alias in data_type_definition.aliases:
      if alias in self._aliases:
        raise KeyError('Alias already set for name: {0:s}.'.format(alias))

    self._definitions[name_lower] = data_type_definition

    for alias in data_type_definition.aliases:
      self._aliases[alias] = name_lower

    if data_type_definition.TYPE_INDICATOR == definitions.TYPE_INDICATOR_FORMAT:
      self._format_definitions.append(name_lower)
