import thread
import time
import ao
import mad

AODEV = ao.AudioDevice(0)    ## GLOBAL

class Player():
    Path = None
    Length = 0        ## milliseconds
    Elapsed = 0       ## always in milliseconds!
    Madrsc = None

    Thread = None
    KeepGoing = False # may need a lock since stop and play_internal both write
    Devrsc = None

    def __init__(self, mad_file, filename):
        self.Madrsc = mad_file
        self.Length = self.Madrsc.total_time()
        self.FileName = filename

    def length(self):
        return self.Length

    def time_elapsed(self):
        return self.Madrsc.current_time()

    def set_next_song(self, path):
        self.Path = path

    def play_internal(self):
        try:
            while self.KeepGoing is True:
                buf = self.Madrsc.read()
                if buf is not None:
                    AODEV.play(buf, len(buf))
                else:
                    print time.asctime() + " :=: player_madao :: play_internal :: Buffer is empty"
                    break
        except:
            print time.asctime() + " :=: Player_madao :: play_internal :: Something went terribly terribly wrong."
            print time.asctime() + " :=: len(buf) = " + (str)(len(buf))

        if self.Callback is not None and self.KeepGoing is True:
            print time.asctime() + " :=: Player_Madao :: play_internal :: Executing callback"
            self.SeekToFront()
            self.KeepGoing = False
            self.Callback()

    def isplaying(self):
        return self.KeepGoing

    def play(self, callback=None):
        self.Callback = callback

        if self.isplaying():
            print time.asctime() + " :=: Player_madao :: play :: Tried to start, but already playing"
            return

        self.KeepGoing = True
        try:
            print time.asctime() + " :=: Player_madao :: play :: starting new play thread"
            self.Thread = thread.start_new_thread(self.play_internal, ( ) )
        except:
            print time.asctime() + " :=: Player_madao :: play :: Could not start new play thread"

    def stop(self):
        if not self.isplaying():
            print time.asctime() + " :=: Player :: stop :: Tried to stop, but not playing"
            return
        self.KeepGoing = False
        self.Callback = None

    def SeekToFront(self):
        del self.Madrsc
        try:
            self.Madrsc = mad.MadFile(self.FileName)
            self.Length = self.Madrsc.total_time()
        except IOError:
            print time.asctime() + " :=: Player_Madao :: SeekToFront :: IOError encountered!"
            print time.asctime() + " :=: Player_Madao :: SeekToFront :: Couldn't open file " + \
                  (str)(self.FileName) + "\nIn the immortal words of Zach," +\
                  "I hope you're debugging, Yates"
