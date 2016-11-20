# -*- coding: utf-8 -*-
"""The structure definitions registry."""


class StructureDefinitionsRegistry(object):
  """Class that implements a structure definitions registry."""

  def __init__(self):
    """Initializes a structure definitions registry."""
    super(StructureDefinitionsRegistry, self).__init__()
    self._structure_definitions = {}

  def DeregisterDefinition(self, structure_definition):
    """Deregisters a structure definition.

    The structure definitions are identified based on their lower case name.

    Args:
      structure_definition (StructureDefinition): structure definitions.

    Raises:
      KeyError: if a structure definition is not set for the corresponding
          name.
    """
    name = structure_definition.name.lower()
    if name not in self._structure_definitions:
      raise KeyError(u'Structure definition not set for name: {0:s}.'.format(
          structure_definition.name))

    del self._structure_definitions[name]

  def GetDefinitionByName(self, name):
    """Retrieves a specific structure definition by name.

    Args:
      name (str): name of the structure definition.

    Returns:
      StructureDefinition: structure definition or None if not available.
    """
    if name:
      return self._structure_definitions.get(name.lower(), None)

  def GetDefinitions(self):
    """Retrieves the structure definitions.

    Returns:
      list[StructureDefinition]: structure definitions.
    """
    return self._structure_definitions.values()

  def RegisterDefinition(self, structure_definition):
    """Registers a structure definition.

    The structure definitions are identified based on their lower case name.

    Args:
      structure_definition (StructureDefinition): structure definitions.

    Raises:
      KeyError: if structure definition is already set for the corresponding
          name.
    """
    name = structure_definition.name.lower()
    if name in self._structure_definitions:
      raise KeyError(
          u'Structure definition already set for name: {0:s}.'.format(
              structure_definition.name))

    self._structure_definitions[name] = structure_definition

  def ReadFromDirectory(self, definitions_reader, path, extension=u'yaml'):
    """Reads structure definitions into the registry from files in a directory.

    This function does not recurse sub directories.

    Args:
      structures_reader (DefinitionsReader): definitions reader.
      path (str): path of the directory to read from.
      extension (Optional[str]): extension of the filenames to read from
          the directory.

    Raises:
      KeyError: if a duplicate structure definition is encountered.
    """
    for structure_definition in definitions_reader.ReadDirectory(
        path, extension=extension):
      self.RegisterDefinition(structure_definition)

  def ReadFromFile(self, definitions_reader, filename):
    """Reads structure definitions into the registry from a file.

    Args:
      structures_reader (DefinitionsReader): definitions reader.
      filename (str): path of the file to read from.
    """
    for structure_definition in definitions_reader.ReadFile(filename):
      self.RegisterDefinition(structure_definition)

  def ReadFileObject(self, definitions_reader, file_object):
    """Reads structure definitions into the registry from a file-like object.

    Args:
      structures_reader (DefinitionsReader): definitions reader.
      file_object (file): file-like object to read from.
    """
    for structure_definition in definitions_reader.ReadFileObject(file_object):
      self.RegisterDefinition(structure_definition)
