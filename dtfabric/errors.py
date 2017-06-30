# -*- coding: utf-8 -*-
"""The error objects."""

class Error(Exception):
  """The error interface."""


class ByteStreamTooSmallError(Error):
  """Error that is raised when the byte stream is too small."""


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
    # pylint: disable=super-init-not-called
    # Do not call initialize of the super class.
    self.name = name
    self.message = message


class FoldingError(Error):
  """Error that is raised when the definition cannot be folded."""


class FormatError(Error):
  """Error that is raised when the definition format is incorrect."""


class MappingError(Error):
  """Error that is raised when the definition cannot be mapped."""
