# -*- coding: utf-8 -*-
"""Output writers."""

from __future__ import print_function


class StdoutWriter(object):
  """Stdout output writer."""

  def Open(self):
    """Opens the output writer object.

    Returns:
      bool: True if successful or False if not.
    """
    return True

  def Close(self):
    """Closes the output writer object."""
    pass

  def WriteData(self, data):
    """Writes data to stdout.

    Args:
      data (bytes): data to write.
    """
    print(data.encode(u'utf8'))
