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
    KeepGoing = False ## does not need a lock; only one writer (self.stop)
    Devrsc = None

    def __init__(self, mad_file, filename):
        self.Madrsc = mad_file
        self.Length = self.Madrsc.total_time()
        self.FileName = filename
        pass

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
                    print self.timeStamp() + " :=: player_madao :: play_internal :: Tried to play, but buf is none"
                    break
        except:
            print self.timeStamp() + " :=: Player_madao :: play_internal :: Something went terribly terribly wrong."
            print self.timeStamp() + " :=: len(buf) = " + (str)(len(buf))

        if self.Callback is not None and self.KeepGoing is True:
            print self.timeStamp() + " :=: Player_Madao :: play_internal :: Executing callback"
            self.Callback()

    def isplaying(self):
        return self.KeepGoing

    def play(self, callback=None):
        if callback is None:
            print self.timeStamp() + " :=: Player_Madao :: Play :: callback is none"
        else:
            print self.timeStamp() + " :=: Player_Madao :: Play :: callback is not none"
        self.Callback = callback

        if self.isplaying():
            print self.timeStamp() + " :=: Player_madao :: play :: Tried to start, but already playing"
            return

        self.KeepGoing = True
        try:
            print self.timeStamp() + " :=: Player_madao :: play :: starting new play thread"
            self.Thread = thread.start_new_thread(self.play_internal, ( ) )
        except:
            print self.timeStamp() + " :=: Player_madao :: play :: Could not start new play thread"


    def stop(self):
        if not(self.isplaying()):
            print self.timeStamp() + " :=: Player :: stop :: Tried to stop, but not playing"
            return
        self.KeepGoing = False
        self.Callback = self.nothing

    def nothing(self):
        pass

    def SeekToFront(self):
        del self.Madrsc
        try:
            self.Madrsc = mad.MadFile(self.FileName)
            self.Length = self.Madrsc.total_time()
        except IOError:
            print self.timeStamp() + " :=: Player_Madao :: SeekToFront :: IOError encountered!"
            print self.timeStamp() + " :=: Player_Madao :: SeekToFront :: Couldn't open file " + \
                  (str)(self.FileName) + "\nIn the immortal words of Zach," +\
                  "I hope you're debugging, Yates"


    def timeStamp(self):
        return time.asctime(time.localtime(time.time()))
