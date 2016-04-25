import os
import signal
import time
import tkSnack

DEBUG_MUTE = False

class Player():
    Path = None
    Length = 0        ## milliseconds
    Elapsed = 0
    Snack = None
    KeepGoing = False
    Callback = None

    def __init__(self, root, filepath):
        self.Path = filepath
        tkSnack.initializeSnack(root)

        self.Snack = tkSnack.Sound(file=self.Path) ## can use load= instead
        self.Length = self.Snack.length(unit='SECONDS') * 1000

        if DEBUG_MUTE:
            tkSnack.audio.play_gain(0)

    def length(self):
        return self.Length

    def time_elapsed(self):
        #print "time elapsed: ",
        #print tkSnack.audio.elapsedTime()
        return tkSnack.audio.elapsedTime() * 1000 ### milliseconds!

        ### more for lulz than anything else, make the meter show a random time
        #import random
        #random.seed()
        #return random.randint(0, self.length())

    def isplaying(self):
        return self.KeepGoing

    def set_next_song(self, path):
        self.Path = path
## todo?
    def play_internal(self):

        while self.KeepGoing is True:
            time.sleep(1.0)
            self.Elapsed += 1000
            if self.Elapsed >= self.Length:
                break

        if self.KeepGoing is False:
            os.kill(self.Pid, signal.SIGKILL)

        if self.Callback is not None and self.KeepGoing is True:
            print "Player :: Executing callback"
            self.Callback()

        pass

    def play(self, callback=None):
###        print "\t Snack Playing"
        self.Callback = callback

        if(self.isplaying()):
            return

        self.KeepGoing = True
        try:
## todo
            self.Snack.play(blocking=False, command=self.Callback)
            #self.Thread = thread.start_new_thread(self.play_internal, ( ) )
        except:
            print "Player :: Could not start thread"
            pass

    def stop(self):
        if not(self.isplaying()):
            return
        self.KeepGoing = False
        self.Callback = self.nothing
        self.Snack.stop()
        self.Snack = tkSnack.Sound(file=self.Path)

    def nothing(self):
        print "NOTHING going on here ;-)"
        pass
