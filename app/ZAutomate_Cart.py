import time
import urllib2
import mad
from ZAutomate_Config import PLAYER_CLASS, AUTOLOG

print "\t---Using Player "+PLAYER_CLASS+"---"
PlayerModule = __import__("ZAutomate_Player_"+PLAYER_CLASS)

# TODO: move to DBInterface
URL_LOG          = 'http://stream.wsbf.net/wizbif/zautomate_2.0/zautomate_log.php'

class Cart():
    Index = None
    ID = None
    Title = None
    Issuer = None
    cartType = None
    Filename = None

    Sound = None
    TimeStart = None    # only used for queueing via ZA_Automation

    def __init__(self, cid, title, issuer, ctype, filename):
        # TODO: mock ZAutoLib in development
        filename = "test/test.mp3"

        self.Filename = filename.strip()
        tempFile = None
        try:
            tempFile = mad.MadFile(filename)
        except IOError:
            print self.timeStamp() + " :=: Cart :: __init__ :: Error :: Mad.Madfile(" + (str)(filename) +") failed!"
        if tempFile is not None:
            self.Sound = PlayerModule.Player(tempFile, filename)
        else:
            self.Sound = None
        self.ID = cid
        self.Title = title.strip()
        self.Issuer = issuer.strip()
        self.cartType = ctype.strip()

    def SetTimeStruct(self, startTime):
        self.TimeStart = startTime

    def GetTimeStruct(self):
        return self.TimeStart

    def GetFmtTime(self):
        if self.TimeStart is not None:
            return time.strftime('%I:%M:%S %p', self.TimeStart)
        else:
            return '00:00:00'

    def Verify(self):
        #return os.path.isfile(self.Filename)
        return self.Sound is not None

    def __del__(self):
        ###self.Sound.destroy()
        ##print self.timeStamp() + " :=: Destructor for title: ",
        ##print self.Title
        pass

    def MeterFeeder(self):
        return (self.Sound.time_elapsed(), self.Sound.length(), self.Title, self.Issuer, self.ID, self.cartType)

    def Start(self, callback=None):
        print self.timeStamp() + " :=: Cart :: Start :: " + self.Title + " :: " + self.Issuer
        try:
            self.Sound.play(callback)
        except:
            print self.timeStamp() + " :=: Cart :: Start :: ERROR :: could not play the file " + self.Filename
            return

        if AUTOLOG:
            self.Logbook_Log(self.ID)

    # TODO: move this code to DBInterface and remove two-way dependency
    def Logbook_Log(self, cartID):
        ## id will be libcart primary key for non-song; for libtrack, it will be H199-4 (for example)
        urlUse = URL_LOG + "?cartid=" + str(cartID)
        print urlUse
        try:
            resource = urllib2.urlopen(urlUse)
            lines = resource.read().split("\n")
            for line in lines:
                print line
        except:
            print self.timeStamp() + " :=: Caught error: Could not access cart logger."

    def Stop(self):
        print self.timeStamp() + " :=: Cart :: Stop :: " + self.Issuer + " - " + self.Title
        self.Sound.stop()

    def IsPlaying(self):
        return self.Sound.isplaying()

    def DefaultEnd(self):
        pass

    ###YATES_METHOD
    def PrintCart(self):
        return (str)(self.ID) + " - " + (str)(self.Issuer) + " - " + (str)(self.Title)

    def SeekToFront(self):
        self.Sound.SeekToFront()

    def timeStamp(self):
        return time.asctime(time.localtime(time.time()))
