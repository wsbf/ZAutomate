"""The player_vlc module provides the Player class.

This implementation of Player uses VLC in a separate process, although
it also uses libmad to retreive the length of the file. This implementation
seems to work, although it prints cryptic messages from time to time.
"""
import multiprocessing as mp
import os
import signal
import subprocess
import time

import mad

class Player(object):
    """The Player class provides an audio stream for a file."""
    _command = None
    _pid = None
    _length = 0
    _elapsed = 0
    _is_playing = False  # may need a lock
    _callback = None

    def __init__(self, filename):
        """Construct a Player.

        :param filename
        """
        self._command = ["/usr/bin/vlc", "--intf", "dummy", "--play-and-exit", filename]
        self._length = mad.MadFile(filename).total_time()

    def length(self):
        """Get the length of the audio stream in milliseconds."""
        return self._length

    def time_elapsed(self):
        """Get the elapsed time of the audio stream in milliseconds."""
        return self._elapsed

    def is_playing(self):
        """Get whether the audio stream is currently playing."""
        return self._is_playing

    def _play_internal(self):
        """Play the audio stream in a separate thread."""
        while self._is_playing:
            time.sleep(1.0)
            self._elapsed += 1000
            if self._elapsed >= self._length:
                break

        if not self._is_playing:
            os.kill(self._pid, signal.SIGKILL)

        if self._callback is not None and self._is_playing:
            self._is_playing = False
            self._callback()

    def play(self, callback=None):
        """Play the audio stream.

        :param callback: function to call if the stream finishes
        """
        if self._is_playing:
            print time.asctime() + " :=: Player_vlc :: Tried to start, but already playing"
            return

        self._pid = subprocess.Popen(self._command).pid
        self._is_playing = True
        self._callback = callback
        mp.Process(target=self._play_internal).start()

    def stop(self):
        """Stop the audio stream."""
        if not self._is_playing:
            print time.asctime() + " :=: Player_vlc :: Tried to stop, but not playing"
            return

        self._is_playing = False
        self._callback = None
