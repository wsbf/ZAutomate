#!/usr/bin/env python

"""Test suite for the database module."""
import sys
sys.path.insert(0, 'app')

import database

print database.get_new_show_id(-1)
print database.get_cart("PSA")
print database.get_cart("Underwriting")
print database.get_cart("StationID")
print database.get_cart("Promotion")
print database.get_playlist(25608)

print database.get_carts()

print database.search_library("mings")

# print database.log_cart()
