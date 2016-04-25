#!/usr/bin/env python

import sys
sys.path.insert(0, 'app')

from ZAutomate_DBInterface import DBInterface

db = DBInterface()

print db.CartMachine_Load()
