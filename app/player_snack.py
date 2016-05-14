"""The player_snack module provides the Player class.

This implementation of Player uses the tkSnack module to access the
audio stream. However, I have not been able to use it because the
tkSnack module does not seem to load correctly.
"""
import time
from Tkinter import Tk
import tkSnack

# TODO: provide reference to Tk root
root = Tk()
tkSnack.initializeSnack(root)

class Player(object):
    """The Player class provides an audio stream for a file."""
    _filename = None
    _snack = None
    _is_playing = False
    _callback = None

    def __init__(self, filename):
        """Construct a Player.

        :param filename
        """
        self._filename = filename
        self.reset()

    def length(self):
        """Get the length of the audio stream in milliseconds."""
        return self._snack.length(unit="SECONDS") * 1000

    def time_elapsed(self):
        """Get the elapsed time of the audio stream in milliseconds."""
        return tkSnack.audio.elapsedTime() * 1000

    def is_playing(self):
        """Get whether the audio stream is currently playing."""
        return self._is_playing

    def reset(self):
        """Reset the audio stream."""
        self._snack = tkSnack.Sound(load=self._filename)

    def play(self, callback=None):
        """Play the audio stream.

        :param callback: function to call if the stream finishes
        """
        if self._is_playing:
            print time.asctime() + " :=: Player_snack :: Tried to start, but already playing"
            return

        self._is_playing = True
        self._callback = callback
        self._snack.play(blocking=False, command=self._callback)

    def stop(self):
        """Stop the audio stream."""
        if not self._is_playing:
            print time.asctime() + " :=: Player_snack :: Tried to stop, but not playing"
            return

        self._is_playing = False
        self._callback = None
        self._snack.stop()

        self.reset()
