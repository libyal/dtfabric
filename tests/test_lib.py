# -*- coding: utf-8 -*-
"""Shared test case."""

import unittest


class BaseTestCase(unittest.TestCase):
  """The base test case."""

  # Show full diff results, part of TestCase so does not follow our naming
  # conventions.
  maxDiff = None
