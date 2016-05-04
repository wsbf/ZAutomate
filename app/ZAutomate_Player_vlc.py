import os
import signal
import subprocess
import thread
import time

import mad

class Player(object):
    _command = None
    _pid = None
    _length = 0          # milliseconds
    _elapsed = 0         # milliseconds
    _is_playing = False  # may need a lock
    _callback = None

    def __init__(self, filename):
        self._command = ["/usr/bin/vlc", "--intf", "dummy", "--play-and-exit", filename]
        self._length = mad.MadFile(filename).total_time()

    def length(self):
        return self._length

    def time_elapsed(self):
        return self._elapsed

    def is_playing(self):
        return self._is_playing

    def _play_internal(self):
        while self._is_playing is True:
            time.sleep(1.0)
            self._elapsed += 1000
            if self._elapsed >= self._length:
                break

        if self._is_playing is False:
            os.kill(self._pid, signal.SIGKILL)

        if self._callback is not None and self._is_playing is True:
            self._is_playing = False
            self._callback()

    def play(self, callback=None):
        if self.is_playing():
            print time.asctime() + " :=: Player_vlc :: Tried to start, but already playing"
            return

        self._pid = subprocess.Popen(self._command).pid
        self._is_playing = True
        self._callback = callback
        thread.start_new_thread(self._play_internal, ())

    def stop(self):
        if not self.is_playing():
            print time.asctime() + " :=: Player_vlc :: Tried to stop, but not playing"
            return

        self._is_playing = False
        self._callback = None
