#!/usr/bin/env python

"""Test suite for the player_madao module."""
import sys
import time

sys.path.insert(0, 'app')
from player_madao import Player

if len(sys.argv) != 2:
    print "usage: test/test_player_madao.py [mp3-file]"
    sys.exit(1)

FILENAME = sys.argv[1]

def end_callback():
    print "Player finished."

player = Player(FILENAME)
player.play(end_callback)

while player.is_playing():
    print player.is_playing()
    time.sleep(1.0)
