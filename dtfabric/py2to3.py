# -*- coding: utf-8 -*-
"""The Python 2 and 3 compatible definitions."""

import sys


if sys.version_info[0] < 3:
  UNICHR = unichr
else:
  UNICHR = chr
