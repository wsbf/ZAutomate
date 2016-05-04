import thread
import time
import ao
import mad

AODEV = ao.AudioDevice(0)

class Player(object):
    _filename = None
    _madfile = None
    _length = 0          # milliseconds
    _is_playing = False  # may need a lock since stop and play_internal both write
    _callback = None

    def __init__(self, filename):
        self._filename = filename
        self.seek_to_front()

    def length(self):
        return self._length

    def time_elapsed(self):
        return self._madfile.current_time()

    def is_playing(self):
        return self._is_playing

    def seek_to_front(self):
        self._madfile = mad.MadFile(self._filename)
        self._length = self._madfile.total_time()

    def _play_internal(self):
        while self._is_playing is True:
            buf = self._madfile.read()
            if buf is not None:
                AODEV.play(buf, len(buf))
            else:
                print time.asctime() + " :=: Player_madao :: Buffer is empty"
                break

        if self._callback is not None and self._is_playing is True:
            self.seek_to_front()
            self._is_playing = False
            self._callback()

    def play(self, callback=None):
        if self.is_playing():
            print time.asctime() + " :=: Player_madao :: Tried to start, but already playing"
            return

        self._is_playing = True
        self._callback = callback
        thread.start_new_thread(self._play_internal, ())

    def stop(self):
        if not self.is_playing():
            print time.asctime() + " :=: Player_madao :: Tried to stop, but not playing"
            return

        self._is_playing = False
        self._callback = None
