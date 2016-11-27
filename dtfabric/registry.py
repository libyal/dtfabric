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
    if name:
      return self._definitions.get(name.lower(), None)

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

  def ReadFromDirectory(self, definitions_reader, path, extension=u'yaml'):
    """Reads data type definitions into the registry from files in a directory.

    This function does not recurse sub directories.

    Args:
      structures_reader (DefinitionsReader): definitions reader.
      path (str): path of the directory to read from.
      extension (Optional[str]): extension of the filenames to read from
          the directory.

    Raises:
      KeyError: if a duplicate data type definition is encountered.
    """
    for data_type_definition in definitions_reader.ReadDirectory(
        path, extension=extension):
      self.RegisterDefinition(data_type_definition)

  def ReadFromFile(self, definitions_reader, filename):
    """Reads data type definitions into the registry from a file.

    Args:
      structures_reader (DefinitionsReader): definitions reader.
      filename (str): path of the file to read from.
    """
    for data_type_definition in definitions_reader.ReadFile(filename):
      self.RegisterDefinition(data_type_definition)

  def ReadFileObject(self, definitions_reader, file_object):
    """Reads data type definitions into the registry from a file-like object.

    Args:
      structures_reader (DefinitionsReader): definitions reader.
      file_object (file): file-like object to read from.
    """
    for data_type_definition in definitions_reader.ReadFileObject(file_object):
      self.RegisterDefinition(data_type_definition)
