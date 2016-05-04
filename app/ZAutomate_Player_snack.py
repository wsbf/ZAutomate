import time
from Tkinter import Tk
import tkSnack

# TODO: provide reference to Tk root
root = Tk()
tkSnack.initializeSnack(root)

class Player(object):
    _filename = None
    _snack = None
    _length = 0          # milliseconds
    _is_playing = False
    _callback = None

    def __init__(self, filename):
        self._filename = filename
        self.seek_to_front()

    def length(self):
        return self._length

    def time_elapsed(self):
        return tkSnack.audio.elapsedTime() * 1000

    def is_playing(self):
        return self._is_playing

    def seek_to_front(self):
        self._snack = tkSnack.Sound(load=self._filename)
        self._length = self._snack.length(unit='SECONDS') * 1000

    def play(self, callback=None):
        if self.is_playing():
            print time.asctime() + " :=: Player_snack :: Tried to start, but already playing"
            return

        self._is_playing = True
        self._callback = callback
        self._snack.play(blocking=False, command=self._callback)

    def stop(self):
        if not self.is_playing():
            print time.asctime() + " :=: Player_snack :: Tried to stop, but not playing"
            return

        self._is_playing = False
        self._callback = None
        self._snack.stop()

        self.seek_to_front()
