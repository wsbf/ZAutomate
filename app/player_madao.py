"""The player_madao module provides the Player class.

This implementation of Player uses python wrappers for libmad and libao,
which provide interfaces to audio files and audio devices.
"""
import thread
import time
import ao
import mad

AODEV = ao.AudioDevice(0)

class Player(object):
    """The Player class provides an audio stream for a file."""
    _filename = None
    _madfile = None
    _is_playing = False  # may need a lock since stop and play_internal both write
    _callback = None

    def __init__(self, filename):
        """Construct a Player.

        :param filename
        """
        self._filename = filename
        self.reset()

    def length(self):
        """Get the length of the audio stream in milliseconds."""
        return self._madfile.total_time()

    def time_elapsed(self):
        """Get the elapsed time of the audio stream in milliseconds."""
        return self._madfile.current_time()

    def is_playing(self):
        """Get whether the audio stream is currently playing."""
        return self._is_playing

    def reset(self):
        """Reset the audio stream."""
        self._madfile = mad.MadFile(self._filename)

    def _play_internal(self):
        """Play the audio stream in a separate thread."""
        while self._is_playing:
            buf = self._madfile.read()
            if buf is not None:
                AODEV.play(buf, len(buf))
            else:
                print time.asctime() + " :=: Player_madao :: Buffer is empty"
                break

        if self._callback is not None and self._is_playing:
            self.reset()
            self._is_playing = False
            self._callback()

    def play(self, callback=None):
        """Play the audio stream.

        :param callback: function to call if the stream finishes
        """
        if self._is_playing:
            print time.asctime() + " :=: Player_madao :: Tried to start, but already playing"
            return

        self._is_playing = True
        self._callback = callback
        thread.start_new_thread(self._play_internal, ())

    def stop(self):
        """Stop the audio stream."""
        if not self._is_playing:
            print time.asctime() + " :=: Player_madao :: Tried to stop, but not playing"
            return

        self._is_playing = False
        self._callback = None
