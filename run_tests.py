#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script to run the tests."""

import sys
import unittest

# Change PYTHONPATH to include dtFabric.
sys.path.insert(0, '.')


if __name__ == '__main__':
  print(f'Using Python version {sys.version!s}')

  fail_unless_has_test_file = '--fail-unless-has-test-file' in sys.argv
  setattr(unittest, 'fail_unless_has_test_file', fail_unless_has_test_file)
  if fail_unless_has_test_file:
    # Remove --fail-unless-has-test-file otherwise it will conflict with
    # the argparse tests.
    sys.argv.remove('--fail-unless-has-test-file')

  test_suite = unittest.TestLoader().discover('tests', pattern='*.py')
  test_results = unittest.TextTestRunner(verbosity=2).run(test_suite)
  if not test_results.wasSuccessful():
    sys.exit(1)
