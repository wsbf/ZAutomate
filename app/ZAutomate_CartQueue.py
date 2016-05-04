import datetime
# import thread
import time
from ZAutomate_Meter import Meter
import ZAutomate_DBInterface as database

CART_TYPES = [
    'StationID',
    'PSA',
    'Underwriting'
]

### Configuration for when to play carts. The current configuration
### fulfills the current rules established by the FCC and WSBF:
### - 1 StationID at the top of every hour, +/- 5 minutes
### - 2 PSAs each hour
### - 1 Underwriting each hour
###
### types        array of cart types to play
### minuteBreak  target play time within each hour
### maxOffset    maximum deviation from minuteBreak, in seconds
AUTOMATION_CARTS = [
    {
        "types": ["StationID"],
        "minuteBreak": 1,  # TODO: should this be 0?
        "maxOffset": 300
    },
    {
        "types": ["StationID", "PSA"],
        "minuteBreak": 15,
        "maxOffset": 300
    },
    {
        "types": ["StationID", "Underwriting"],
        "minuteBreak": 30,
        "maxOffset": 300
    },
    {
        "types": ["StationID", "PSA"],
        "minuteBreak": 45,
        "maxOffset": 300
    }
]

PLAYLIST_MIN_LENGTH = 10

class CartQueue(object):

    ### current show ID
    ShowID = -1

    ###Cart Array - Treated like a Queue with Out-Front at index-0
    Arr = None
    PlayedArr = None

    # the _Meter class
    Meter = None

    ###UIUpdate - Function Pointer for callbacks to update UI with CartQueue info
    UIUpdate = None

    ###KeepGoing - Boolean Value for determining whether another Cart plays after
    ###                the current cart finishes.
    KeepGoing = False

    ### lock for the queue
    # QueueLock = None

    def __init__(self, master, width, uiu):
        # get the saved show ID or a random new show ID
        self.ShowID = database.restore_show_id()
        if self.ShowID is -1:
            self.ShowID = database.get_new_show_id(-1)

        self.Arr = []
        self.PlayedArr = []
        self.UIUpdate = uiu

        # self.QueueLock = thread.allocate_lock()

        ###YATES_COMMENT: What/Where is MeterFeeder?
        ###YATES_ANSWER: It's a Function or Macro, defined at the bottom,
        ###                  it returns self.Arr[0].MeterFeeder();
        self.Meter = Meter(master, width - 10, self.MeterFeeder, self.Transition)
        self.Meter.grid(row=1, column=0, columnspan=4)

    def GetQueue(self):
        return self.Arr

    def IsPlaying(self):
        return self.Arr[0].is_playing()

    def IsStopping(self):
        return not self.KeepGoing

    def Dequeue(self):
        if len(self.Arr) > 0:
            print time.asctime() + " :=: CQ :: Dequeue :: Dequeuing " + self.Arr[0].PrintCart()

            # stop the cart
            self.Arr[0].stop()
            self.Meter.Reset()

            # move the cart to the played list
            self.PlayedArr.append(self.Arr.pop(0))

    def Save(self):
        database.save_show_id(self.ShowID)

    def IsArtistInList(self, cart, array):
        if cart is None:
            return True

        for item in array:
            if cart.Issuer is item.Issuer:
                return True

        return False

    def AddTracks(self):
        beginIndex = len(self.Arr)

        while len(self.Arr) < PLAYLIST_MIN_LENGTH:
            # retrieve playlist from database
            show = database.get_next_playlist(self.ShowID)
            self.ShowID = show["showID"]

            # add each track whose artist isn't already in the queue or playlist list
            self.Arr.extend([t for t in show["playlist"] if not self.IsArtistInList(t, self.PlayedArr) and not self.IsArtistInList(t, self.Arr)])

            print time.asctime() + " :=: CartQueue :: Enqueued tracks, length is " + (str)(len(self.Arr))

        self.GenStartTimes(beginIndex)

    ## Refill the playlist with tracks
    ## This function also clears the played list and inserts carts.
    def Refill(self):
        # self.QueueLock.acquire()

        self.AddTracks()
        self.PlayedArr = []

        # self.QueueLock.release()
        self.InsertCarts()

        # InsertCarts() exits the thread
        # thread.exit()

    ### Transition to the next cart after a cart finishes.
    ### This function is called when a cart ends or when it is stopped.
    def Transition(self):
        self.Dequeue()

        # refill the queue if it is too short
        if len(self.Arr) < PLAYLIST_MIN_LENGTH:
            print time.asctime() + " :=: CQ :: Transition :: Refilling the playlist"
            # thread.start_new_thread(self.Refill, ())
            self.Refill()

        # add carts if there aren't any carts in the queue
        carts = [c for c in self.Arr if c.cart_type in CART_TYPES]

        if len(carts) is 0:
            print time.asctime() + " :=: CQ :: Transition :: Refilling carts"
            # thread.start_new_thread(self.InsertCarts, ())
            self.InsertCarts()

        if self.KeepGoing is True:
            # start the next track if the current track ended
            print time.asctime() + " :=: CQ :: Transition :: Starting the next track"
            self.Start()
        else:
            # remove all carts if the queue was stopped
            print time.asctime() + " :=: CQ :: Transition :: Removing all carts"
            self.RemoveCarts()
            self.UIUpdate()

    ## Remove all carts from the queue.
    ## This function is called after a hard stop and before new carts
    ## are inserted. The queue must be cleared at these times in order
    ## to ensure that carts are played at correct times.
    def RemoveCarts(self):
        # TODO: this line is sufficient if current track is separated from queue
        # self.Arr = [c for c in self.Arr if cart.cart_type not in CART_TYPES]

        if self.Arr[0].is_playing():
            i = 1
        else:
            i = 0

        while i < len(self.Arr):
            if self.Arr[i].cart_type in CART_TYPES:
                self.Arr.pop(i)
            else:
                i += 1

    ## Populate the TimeStruct inside each Cart. This is useful for PSA insertion, etc.
    ## Should be called when carts/songs are added to (or removed from?) playlist
    ## It is regenerated on every start and on every transition, which makes it accurate.
    ## It can be run to exclude the beginning of the Queue, with the beginIndex parameter
    def GenStartTimes(self, beginIndex=0):
        baseTime = time.localtime()

        for i in range(beginIndex, len(self.Arr)):
            ## for each cart after the first, add the length of the previous
            ## track to produce the start time
            if i > 0:
                prevStartTime = self.Arr[i - 1].GetStartTime()
                prevLength = self.Arr[i - 1].MeterFeeder()[1] / 1000
                startTime = time.mktime(prevStartTime) + prevLength
                baseTime = time.localtime(startTime)

            ## set the current cart's starting time
            self.Arr[i].SetStartTime(baseTime)

    ## Refresh the queue with new carts.
    ## This function is called when the queue is started and when the queue
    ## runs out of carts.
    def InsertCarts(self):
        # self.QueueLock.acquire()

        self.RemoveCarts()
        for entry in AUTOMATION_CARTS:
            self.InsertCart(entry["types"], entry["minuteBreak"], entry["maxOffset"])

        # self.QueueLock.release()
        # thread.exit()

    ## Insert carts into the current hour according to a config entry.
    ## This function inserts carts as close as possible to the target start time,
    ## even if the target window is not met.
    def InsertCart(self, types, minuteBreak, maxOffset):
        target = datetime.datetime.now().replace(minute=minuteBreak, second=0, microsecond=0)

        ## don't insert if the window has already passed this hour
        if target + datetime.timedelta(seconds=maxOffset) < datetime.datetime.now():
            return

        print time.asctime() + " :=: CQ :: InsertCart :: Target insert time is " + (str)(target)

        ## find the position in queue with the closest start time to target
        min_index = -1
        min_delta = -1

        ## TODO: the head of the queue is ignored for multi-threading safety
        ##       however, it might be more prudent to use a lock
        for i in range(1, len(self.Arr)):
            startTime = self.Arr[i].GetStartTime()
            startTime = datetime.datetime.fromtimestamp(time.mktime(startTime))

            delta = abs(target - startTime)

            if min_delta is -1 or delta < min_delta:
                min_index = i
                min_delta = delta
            elif delta > min_delta:
                break

        print time.asctime() + " :=: CQ :: InsertCart :: min_index is " + (str)(min_index)
        print time.asctime() + " :=: CQ :: InsertCart :: min_delta is " + (str)(min_delta)

        if min_delta.seconds <= maxOffset:
            print time.asctime() + " :=: CQ :: InsertCart :: Carts were inserted within target window"
        else:
            print time.asctime() + " :=: CQ :: InsertCart :: Could not insert carts within target window"

        ## insert a cart of each type into the queue
        index = min_index
        for t in types:
            cart = database.get_cart(t)
            self.Arr.insert(index, cart)
            index += 1
        self.GenStartTimes(min_index)

    ### Start the front track in the queue.
    ### This function is called when Automation is started and after a track ends.
    def Start(self, click=False):
        self.KeepGoing = True

        if click is True:
            self.GenStartTimes(0)
            # thread.start_new_thread(self.InsertCarts, ())
            self.InsertCarts()

        print time.asctime() + " :=: starting " + self.Arr[0].PrintCart()
        self.Meter.Start()
        self.Arr[0].start(self.Transition)
        database.log_cart(self.Arr[0].cart_id)

        self.UIUpdate()

    def StopSoon(self):
        self.KeepGoing = False

    ## passed to Meter on instantiation
    def MeterFeeder(self):
        if len(self.Arr) > 0:
            return self.Arr[0].MeterFeeder()
        else:
            return ("-:--", "-:--", "", "", "", "")
