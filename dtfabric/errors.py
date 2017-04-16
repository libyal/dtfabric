# -*- coding: utf-8 -*-
"""The error objects."""


class Error(Exception):
  """The error interface."""


class DefinitionReaderError(Error):
  """Error that is raised by the definition reader."""

  def __init__(self, name, *args):
    """Initializes an error.

    Args:
      name (str): name of the definition.
    """
    super(DefinitionReaderError, self).__init__(args)
    self.name = name


class FormatError(Error):
  """Error that is raised when the definition format is incorrect."""


class MappingError(Error):
  """Error that is raised when the definition cannot be mapped."""
