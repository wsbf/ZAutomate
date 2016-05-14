#!/usr/bin/env python

import sys
sys.path.insert(0, 'app')

import database

print database.get_carts()
