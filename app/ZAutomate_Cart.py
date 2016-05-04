import time
from ZAutomate_Player_snack import Player

class Cart(object):
    cart_id = None
    title = None
    issuer = None
    cart_type = None
    filename = None
    player = None

    TimeStart = None    # only used for queueing via ZA_Automation

    def __init__(self, cart_id, title, issuer, cart_type, filename):
        # TODO: mock ZAutoLib in development
        filename = "test/test.mp3"

        self.cart_id = cart_id
        self.title = title
        self.issuer = issuer
        self.cart_type = cart_type
        self.filename = filename

        try:
            self.player = Player(filename)
        except IOError:
            print time.asctime() + " :=: Cart :: could not load audio file " + filename

    def is_playable(self):
        return self.player is not None

    def is_playing(self):
        return self.player.is_playing()

    def seek_to_front(self):
        self.player.seek_to_front()

    def start(self, callback=None):
        print time.asctime() + " :=: Cart :: Start :: " + self.title + " - " + self.issuer
        self.player.play(callback)

    def stop(self):
        print time.asctime() + " :=: Cart :: Stop :: " + self.issuer + " - " + self.title
        self.player.stop()

    def MeterFeeder(self):
        return (self.player.time_elapsed(), self.player.length(), self.title, self.issuer, self.cart_id, self.cart_type)

    ###YATES_METHOD
    def PrintCart(self):
        return (str)(self.cart_id) + " - " + (str)(self.issuer) + " - " + (str)(self.title)

    # TODO: move start time code to CartQueue
    def SetStartTime(self, startTime):
        self.TimeStart = startTime

    def GetStartTime(self):
        return self.TimeStart

    def GetFmtStartTime(self):
        if self.TimeStart is not None:
            return time.strftime('%I:%M:%S %p', self.TimeStart)
        else:
            return '00:00:00'
