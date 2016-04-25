#!/usr/bin/env python

import sys
sys.path.insert(0, 'app')

from ZAutomate_Gridder import Gridder

gridder = Gridder(8, 6)

print gridder.GridCorner((1, 1))
