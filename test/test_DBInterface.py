#!/usr/bin/env python

import sys
sys.path.insert(0, 'app')

import ZAutomate_DBInterface as database

print database.get_carts()
