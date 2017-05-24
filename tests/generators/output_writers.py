# -*- coding: utf-8 -*-
"""Tests for the output writers."""

import unittest

from dtfabric.generators import output_writers

from tests import test_lib


class StdoutWriterTest(test_lib.BaseTestCase):
  """Stdout output writer tests."""

  def testInitialize(self):
    """Tests the __init__ function."""
    output_writer = output_writers.StdoutWriter()
    self.assertIsNotNone(output_writer)


if __name__ == '__main__':
  unittest.main()
