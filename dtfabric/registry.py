# -*- coding: utf-8 -*-
"""The data type definitions registry."""

import typing

from typing import Dict, List, Union  # pylint: disable=unused-import

from dtfabric import definitions

if typing.TYPE_CHECKING:
  from dtfabric import data_types


class DataTypeDefinitionsRegistry(object):
  """Data type definitions registry."""

  def __init__(self) -> 'None':
    """Initializes a data type definitions registry."""
    super(DataTypeDefinitionsRegistry, self).__init__()
    self._aliases: 'Dict[str, str]' = {}
    self._definitions: 'Dict[str, data_types.DataTypeDefinition]' = {}
    self._format_definitions: 'List[str]' = []

  def DeregisterDefinition(
      self, data_type_definition: 'data_types.DataTypeDefinition') -> 'None':
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

  def GetDefinitionByName(
      self, name: 'str') -> 'Union[data_types.DataTypeDefinition, None]':
    """Retrieves a specific data type definition by name.

    Args:
      name (str): name of the data type definition.

    Returns:
      DataTypeDefinition: data type definition or None if not available.
    """
    lookup_name = name.lower()
    if lookup_name not in self._definitions:
      lookup_name = self._aliases.get(name, lookup_name)

    return self._definitions.get(lookup_name, None)

  def GetDefinitions(self) -> 'List[data_types.DataTypeDefinition]':
    """Retrieves the data type definitions.

    Returns:
      list[DataTypeDefinition]: data type definitions.
    """
    return list(self._definitions.values())

  def RegisterDefinition(
      self, data_type_definition: 'data_types.DataTypeDefinition') -> 'None':
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
