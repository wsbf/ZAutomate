import os, time, subprocess, signal, thread
##from ZAutomate_Config import *

import mad
## only uses mad to derive the length of the file

class Player():
    Path = None
    Length = 0            ## always in milliseconds!
    
    Elapsed = 0
    Pid = None
    
    Thread = None
    KeepGoing = False     ## does not need a lock; only one writer (self.stop)
    
    ## REQUIRES :: filepath is a regular file
    def __init__(self, filepath): 
        self.Exec = ['/usr/bin/vlc', '-I', 'dummy', '--play-and-exit']
        self.Path = filepath
        self.Exec.append(self.Path)
        
                
        mf = mad.MadFile(self.Path)
        self.Length = mf.total_time()
        
        pass
    
    def length(self):
        return self.Length
    
    def time_elapsed(self):
        return self.Elapsed
    
    #def set_next_song(self, path):
    #    self.Path = path
    
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
    
    def isplaying(self):
        return self.KeepGoing
    
    def play(self, callback=None):
        self.Callback = callback
        
        if self.isplaying():
            return
        
        self.KeepGoing = True
        try:
            #print "Player :: play thread starting"
            self.Pid = subprocess.Popen(self.Exec).pid
            self.Thread = thread.start_new_thread(self.play_internal, ( ) )
        except:
            print "Player :: Could not start thread"
        
        
    def stop(self):
        if not(self.isplaying()):
            return
        self.KeepGoing = False
        self.Callback = lambda: True


