import thread
import time
from Tkinter import Canvas
from ZAutomate_Config import PLAYER_CLASS

METER_INTERVAL = 0.25

class Meter(Canvas):
    Value = 0

    GetDataFunc = None        ## called on every 'tick' of the Meter to get the next value
    TransitionFunc = None    ## called when the Meter reaches (about) 100%

    Thread = None
    KeepGoing = True

    Height = 135
    Width = 0

    ###YATES_COMMENT: getDataFunc is the function which provides the meter with
    ###                    the data necessary to update the meter.  The return type is
    ###                    a n-tuple (4?  6?) that contains the time info and artist info
    ###                    of the current track playing.  In ZA_Automation, it's the
    ###                    MeterFeeder() function.

    ###YATES_COMMENT:    transitionFunction is the "transition" function for the meter
    ###
    def __init__(self, master, width, getDataFunc, transitionFunc):
        ## the width passed in here is NOT to be used inside the canvas
        ###YATES_COMMENT:    Function pointers for... callbacks?
        self.GetDataFunc = getDataFunc
        self.TransitionFunc = transitionFunc

        ## formatting / graphical stuff
        MeterBG = '#000' # '#666'
        ###YATES_COMMENT: This is the font-color of the text displayed on the whole meter.
        Fill = '#33CCCC'
        HeadFont = ('Helvetica', 22, 'bold')
        SmallFont = ('Helvetica', 12)
        NumFont = ('Courier', 22, 'bold')

        ## parent class instantiation
        Canvas.__init__(self, master, bg=MeterBG, borderwidth='2', relief='groove',
            width=width, height=self.Height)

        self.Width = (int)(self.cget('width'))
        self.MeterX0 = 0
        self.MeterY0 = self.Height - 25
        self.MeterX1 = self.Width + 5
        self.MeterY1 = self.Height
        self.Height = self.MeterY1

        ##self.create_rectangle(1400, 0, self.Width+50, 100, fill='red')
        # x0 y0 x1 y1
        ##self.create_rectangle(0, 0, self.Width,100, fill='red')

        self._Title = self.create_text(10, 20, anchor='w', font=HeadFont, text='--', fill=Fill)

        self._Artist = self.create_text(self.Width, 20, anchor='e', font=HeadFont, text='--', fill=Fill)


        ###self._TopCtr = self.create_text(self.Width/2, 50, anchor='center', font=HeadFont, text='Ready', fill=Fill)

        self._PosLbl = self.create_text(10, 60, anchor='w', font=SmallFont, text='Position', fill=Fill)
        self._LenLbl = self.create_text(140, 60, anchor='w', font=SmallFont, text='Length', fill=Fill)
        self._CueLbl = self.create_text(270, 60, anchor='w', font=SmallFont, text='To Cue', fill=Fill)

        self._Position = self.create_text(10, 85, anchor='w', font=NumFont, text='0:00', fill=Fill)
        self._Length = self.create_text(140, 85, anchor='w', font=NumFont, text='0:00', fill=Fill)
        self._Cue = self.create_text(270, 85, anchor='w', font=NumFont, text='0:00', fill=Fill)

        # x0 y0 x1 y1
        ###YATES_COMMENT: This is the green label.  We create it across the width of the screen.
        self._BGBar = self.create_rectangle(self.MeterX0, self.MeterY0,
            self.MeterX1, self.MeterY1, fill='#008500', width=1)

        ###YATES_COMMENT: This is the red label.  We create a fraction
        self._Bar = self.create_rectangle(self.MeterX0, self.MeterY0,
            0, self.MeterY1, fill='#FF0000', width=1)

    def Start(self):
        self.KeepGoing = True
        try:
            self.Thread = thread.start_new_thread(self.CheckCallback, ())
        except:
            print "Meter :: Error :: Could not start thread!"

    def Change(self, fourtuple):
        ## fourtuple contains: position, length, title, issuer
        ## position and length are in milliseconds
        ###print "\t---CHANGING METER"


        if self.KeepGoing is True:
        #if int(fourtuple[0]) < 1000:
        #    pass
        #else:
            try:
                ###YATES_COMMENT: fourtuple[0] is time_elapsed
                ###                    fourtuple[1] is length
                ###                    Value = [0...1] percentage done with a song.
                value = (float)(fourtuple[0]) / (float)(fourtuple[1])

            except ZeroDivisionError:
                value = 0.0
                print "Meter :: ERROR :: Length is 0 on " + fourtuple[2] + " by " + fourtuple[3]

            position = (int)(fourtuple[0]) / 1000

            length = (int)(fourtuple[1]) / 1000
            cue = length - position
            if position > length:
                print "Meter :: Change :: Position: " + (str)(position) + " > " + (str)(length) + " :Length"
            if cue < 0:
                print "Meter :: Change :: Cue is less than 0!  Printing Debug Statements"
                print "(Time_Elapsed, Length, Title, Issuer, ID, Type)"
                print (str)(fourtuple)
            title = fourtuple[2]
            artist = fourtuple[3]

            ###self.itemconfigure(self._TopCtr, text=Array[0])
            self.itemconfigure(self._Position, text=self.SecsFormat(position))
            self.itemconfigure(self._Length, text=self.SecsFormat(length))


            self.itemconfigure(self._Cue, text=self.SecsFormat(cue))

            self.itemconfigure(self._Title, text=title)
            self.itemconfigure(self._Artist, text=artist)

            self.coords(self._Bar, self.MeterX0, self.MeterY0, int(self.Width * value), self.MeterY1)

    def CheckCallback(self):
        lastTimePosition = -1
        while self.KeepGoing is True:
###            print self.GetDataFunc()
###            print thread.get_ident()
            tple = self.GetDataFunc()
#            print "Meter :: CheckCallBack :: Tuple = " + (str)(tple)
            self.Change(tple)

            if PLAYER_CLASS is 'snack':
#                print lastTimePosition,
#                print " - ",
#                print tple[0],
#                print " - ",
#                print tple[1],
#                print " - ",
#                print tple[1] - tple[0]

                if lastTimePosition > tple[0] and tple[0] == 0.0:
#                    print "Meter :: COMPLETION CONDITION"

                    ## this lets the last sample(-ish) finish out
                    time.sleep(METER_INTERVAL)
                    lastTimePosition = -1
                    self.TransitionFunc()
#                    print "Meter :: Thread exiting"
                    thread.exit()
                else:
                    lastTimePosition = tple[0]
            time.sleep(METER_INTERVAL)

    def Reset(self):
###        print "Meter :: Resetting"
        #self.itemconfigure(self._Title, text='--' )
        #self.itemconfigure(self._Artist, text='--' )
        self.KeepGoing = False

        self.Value = 0
        self.itemconfigure(self._Position, text='0:00')
        self.itemconfigure(self._Length, text='0:00')
        self.itemconfigure(self._Cue, text='0:00')
        self.itemconfigure(self._Title, text='--')
        self.itemconfigure(self._Artist, text='--')
        self.coords(self._Bar, 0, self.MeterY0, 0, self.MeterY1)

    ## convert 180 seconds into 3:00
    def SecsFormat(self, secs):
        hours = 0
        minutes = 0
        seconds = 0

        if secs is None:
            return "Not Ready"
        while secs >= 3600:
            secs -= 3600
            hours += 1
        while secs >= 60:
            secs -= 60
            minutes += 1
        seconds = secs

        fmt = ""
        if hours is not 0:
            fmt += str(hours) + ":"
        if minutes < 10:
            fmt += "0"
        fmt += str(minutes) + ":"

        seconds = int(seconds)
        if seconds < 10:
            fmt += "0"
        fmt += str(seconds) + ""

        return fmt
