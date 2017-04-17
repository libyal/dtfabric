# -*- coding: utf-8 -*-
"""The error objects."""


class Error(Exception):
  """The error interface."""


class DefinitionReaderError(Error):
  """Error that is raised by the definition reader.

  Attributes:
    name (str): name of the definition.
    message (str): error message.
  """

  def __init__(self, name, message):
    """Initializes an error.

    Args:
      name (str): name of the definition.
      message (str): error message.
    """
    # Do not call initialize of the super class.
    self.name = name
    self.message = message


class FormatError(Error):
  """Error that is raised when the definition format is incorrect."""


class MappingError(Error):
  """Error that is raised when the definition cannot be mapped."""
