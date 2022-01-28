# -*- coding: utf-8 -*-
"""dtFabric helper objects."""

import io

from dtfabric import reader
from dtfabric import registry
from dtfabric.runtime import data_maps


class DataTypeFabric(data_maps.DataTypeMapFactory):
  """Data type fabric."""

  def __init__(self, yaml_definition=None):
    """Initializes a data type fabric.

    Args:
      yaml_definition (bytes): UTF-8 and YAML formatted data type definitions.
    """
    definitions_registry = registry.DataTypeDefinitionsRegistry()

    if yaml_definition:
      definitions_reader = reader.YAMLDataTypeDefinitionsFileReader()

      file_object = io.BytesIO(yaml_definition)
      definitions_reader.ReadFileObject(definitions_registry, file_object)

    super(DataTypeFabric, self).__init__(definitions_registry)

  def GetDefinitionByName(
      self, name: 'str') -> 'Union[data_types.DataTypeDefinition, None]':
    """Retrieves a specific data type definition by name.

    Args:
      name (str): name of the data type definition.

    Returns:
      DataTypeDefinition: data type definition or None if not available.
    """
    return self._definitions_registry.GetDefinitionByName(name)
