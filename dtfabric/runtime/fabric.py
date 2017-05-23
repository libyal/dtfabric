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
      yaml_definition (str): YAML formatted data type definitions.
    """
    definitions_registry = registry.DataTypeDefinitionsRegistry()

    if yaml_definition:
      definitions_reader = reader.YAMLDataTypeDefinitionsFileReader()

      file_object = io.BytesIO(yaml_definition)
      definitions_reader.ReadFileObject(definitions_registry, file_object)

    super(DataTypeFabric, self).__init__(definitions_registry)
