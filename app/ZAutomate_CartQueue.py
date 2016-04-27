import datetime
import thread
import time
from ZAutomate_Meter import Meter
import ZAutomate_DBInterface as database

CART_TYPES = [
    'StationID',
    'PSA',
    'Underwriting'
]

### Specifies what type of cart configurations should be inserted into the play list.
### Tuple(cartType, minuteBreak, maxOffset).
### First entry is the combination of what we should do (StationID + PSA, etc).
### Second Entry determines when it should happen.
### Third entry states how much it can be offset from the time specified by second entry.
AUTOMATION_CARTS = [
    (['StationID'], 1, 300),
    (['StationID', 'PSA'], 15, 300),
    (['StationID', 'Underwriting'], 30, 300),
	(['StationID', 'PSA'], 45, 300)
]

PLAYLIST_MIN_LENGTH = 10

class CartQueue():

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

    ###ThreadRunning - Boolean Semaphore for thread stuff.
    ThreadRunning = False

    def __init__(self, master, width, uiu):
        # get the saved show ID or a random new show ID
        self.ShowID = database.restore_show_id()
        if self.ShowID is -1:
            self.ShowID = database.get_new_show_id(-1)

        self.Arr = []
        self.PlayedArr = []
        self.UIUpdate = uiu

        ###YATES_COMMENT: What/Where is MeterFeeder?
        ###YATES_ANSWER: It's a Function or Macro, defined at the bottom,
        ###                  it returns self.Arr[0].MeterFeeder();
        self.Meter = Meter(master, width - 10, self.MeterFeeder, self.Transition)
        self.Meter.grid(row=1, column=0, columnspan=4)

    def GetQueue(self):
        return self.Arr

    def Dequeue(self):
        if len(self.Arr) > 0:
            # stop the cart
            print self.timeStamp() + " :=: CQ :: Dequeue :: Stopping track " + self.Arr[0].PrintCart()
            self.Arr[0].Stop()

            # move the cart to the played list
            print self.timeStamp() + " :=: CQ :: Dequeue :: Dequeuing " + self.Arr[0].PrintCart()
            self.PlayedArr.append(self.Arr.pop(0))

            self.Meter.Reset()

    def Save(self):
        database.save_show_id(self.ShowID)

    def IsArtistInList(self, cart, array):
        if cart is None:
            return True

        for item in array:
            if cart.Issuer is item.Issuer:
                return True

        return False

    ### Retrieve playlists until the queue length is at least PLAYLIST_MIN_LENGTH
    def InitialFill(self):
        while len(self.Arr) < PLAYLIST_MIN_LENGTH:
            show = database.get_next_playlist(self.ShowID)
            self.ShowID = show["showID"]

            lenOld = len(self.Arr)
            self.Arr.extend(show["playlist"])
            self.GenStartTimes(lenOld)

            print self.timeStamp() + " :=: CartQueue :: InitialFill enqueued... new length is "+(str)(len(self.Arr))
        self.UIUpdate()

    ###YATES_COMMENT: Same as InitialFill, but also regenerates StartTimes,
    ###                    and calls InsertAllCarts before calling the UIUPdate callback
    def Refill(self):
        print self.timeStamp() + " :=: CQ :: Refill :: Trying to refill the cart"

        lenOld = len(self.Arr)

        while len(self.Arr) < PLAYLIST_MIN_LENGTH:
            show = database.get_next_playlist(self.ShowID)
            self.ShowID = show["showID"]

            # check whether the cart artist is already in the queue or played list
            for cart in show["playlist"]:
                if not self.IsArtistInList(cart, self.PlayedArr) and not self.IsArtistInList(cart, self.Arr):
                    self.Arr.append(cart)
                else:
                    print self.timeStamp() + " :=: CQ :: Refill :: Found duplicate artist: " + (str)(cart.Issuer)

        print self.timeStamp() + " :=: CQ :: Refill :: Refilled Carts, new CartQueue Length is " + (str)(len(self.Arr))

        self.GenStartTimes(lenOld - 1)
        self.PlayedArr = []
        self.InsertAllCarts()
        #thread.exit()
        ###YATES_COMMENT: InsertAllCarts exits the thread

    ### Transition to the next cart after a cart finishes.
    ### This function is called when a cart ends or when it is stopped.
    def Transition(self):
        # refill the queue if it is too short
        if len(self.Arr) < PLAYLIST_MIN_LENGTH:
            thread.start_new_thread(self.Refill, ())

        # add carts if there aren't any carts in the queue
        carts = [c for c in self.Arr if c.cartType in CART_TYPES]

        if len(carts) == 0:
            thread.start_new_thread(self.InsertAllCarts, ())

        self.Dequeue()

        # start the next track if the current track ended
        if self.KeepGoing is True:
            self.Start()

        # remove all carts if the queue was stopped
        else:
            print self.timeStamp() + " :=: CQ :: Transition :: Clearing out PSAs, Undewriting, StationIDs"
            self.ClearInsertedCarts()
            self.UIUpdate()

    ## called twice: once on stopping and once at InsertAllCarts
    def ClearInsertedCarts(self):
        print self.timeStamp() + " :=: CQ :: ClearInsertedCarts :: Entered Function"
        if self.Arr[0].IsPlaying():
            ctr = 1
        else:
            ctr = 0
        #self.Arr = [ cart for cart in self.Arr[1:len(self.Arr)] if cart.Type not in VALID_CART_TYPES]
        print self.timeStamp() + " :=: CQ :: ClearInsertedCarts :: Entering Loop"
        while ctr < len(self.Arr):
            ##print (str)(ctr) + " :: " + (str)(size)
            ##print (str)(ctr) + " :: " + self.Arr[ctr].Type + " :: " + self.Arr[ctr].Title
            print self.timeStamp() + " :=: CQ :: ClearInsertedCarts :: Loop :: Type is " + (str)(self.Arr[ctr].cartType)
            if self.Arr[ctr].cartType in VALID_CART_TYPES:
                print self.timeStamp() + " :=: \t\tDeleting "+(str)(ctr)
        #        #del self.Arr[ctr]
                self.Arr.pop(ctr)
            else:
                ctr += 1
        print self.timeStamp() + " :=: CQ :: ClearInsertedCarts :: Exited Function"

    ## Populate the TimeStruct inside each Cart. This is useful for PSA insertion, etc.
    ## Should be called when carts/songs are added to (or removed from?) playlist
    ## It is regenerated on every start and on every transition, which makes it accurate.
    ## It can be run to exclude the beginning of the Queue, with the beginIndex parameter
    def GenStartTimes(self, beginIndex=0):
        baseTime = time.localtime()

        for i in range(beginIndex, len(self.Arr)):
            ## for each cart after the first, compute the start time
            if i > 0:
                ## compute the start of current cart in seconds, then convert to time_struct
                prevStartTime = self.Arr[i - 1].GetStartTime()
                prevLength = self.Arr[i - 1].MeterFeeder()[1] / 1000
                startTime = time.mktime(prevStartTime) + prevLength
                baseTime = time.localtime(startTime)

            ## set the current cart's starting time
            self.Arr[i].SetStartTime(baseTime)

    ## Called as a new thread to insert carts
    def InsertAllCarts(self):
        ### Check Semaphore so we don't get deadlocks/livelocks.
        if self.ThreadRunning is True:
            ###YATES_COMMENT: For the record, this is horribly bad and why the application
            ###               Randomly exits from time to time.
            #thread.exit()
            return
        else:
            self.ThreadRunning = True

        ###Clear all the carts first.
        print self.timeStamp() + " :=: CQ :: InsertAllCarts :: Entered Function"
        self.ClearInsertedCarts()

        print self.timeStamp() + " :=: CQ :: InsertAllCarts :: Looping over Carts to insert"
        for entry in AUTOMATION_CARTS:
            self.InsertCart(entry[0], entry[1], entry[2])
        ###Update GUI
        self.UIUpdate()
        ###Unlock Semaphore
        self.ThreadRunning = False
        print self.timeStamp() + " :=: CQ :: InsertAllCarts :: Exiting Function"
        thread.exit()

    ## Make sure we meet the FCC station id rule (and our own rules!)
    ## This function works on a one-hour interval
    ## For multi-hour repetition (i.e. underwriting every 2 hours) -
    ## Have the php insertion script figure out which messages need to be played at, say, the 30:00 mark

    ## minuteBreak :: ex 30 for playing at/around 30:00 (minutes)
    ## maxOffset :: window announcement must fall in (seconds)

    ## THREADING :: This should be thread-safe, because we don't do anything with self.Arr[0]
    def InsertCart(self, cartTypes, minuteBreak, maxOffset, firstRun=True):
        print self.timeStamp() + " :=: CQ :: InsertCart :: Entered Function"

        ###YATES_COMMENT: This returns today:thisHour:00:00:00
        relevantInsertTime = datetime.datetime.now().replace(minute=0, second=0, microsecond=0)
        ###YATES_COMMENT: This adds the minutebreak (when we want to insert) to
        ###                    the relevantInsertTime.
        ###                    relevantInserTime = today:thisHouse:minuteBreak:00:00
        relevantInsertTime += datetime.timedelta(minutes=minuteBreak) #hours=1
        print self.timeStamp() + " :=: CQ :: InsertCart :: Optimal Insert Time is " + (str)(relevantInsertTime)

        ###YATES_COMMENT: This feels really funky.  It's entirely possible that we
        ###                    generate a relevantInsertTime and it's before now.
        ###                    For instance, it's 10:33, and we're working on the half-hour
        ###                    PSA-Station ID.  Cut the minutes.  10:00, add the minuteBreak
        ###                    and we get 10:30.  10:30 < 10:33.
        ###
        ###                    The confusing part is why we bump ahead an hour.  So from
        ###                    the above example, we're now at 11:30.  What happened between
        ###                    10:33 and 11:29.
        ###
        ###                    Iz think there's an assumption here that if we're already
        ###                    past the time, don't worry about this PSA until the next
        ###                    hour.
        ## Allows inserting carts after an hour change (start at :58. otherwise, would only do 60)
        timeThresholdVar = relevantInsertTime + datetime.timedelta(seconds=maxOffset)
        if timeThresholdVar < datetime.datetime.now():
            print self.timeStamp() + " :=: optimal insert time has already passed, scheduling for next hour"
            print self.timeStamp() + " =:= threshold = " + (str)(timeThresholdVar) + " < " + (str)(datetime.datetime.now())
            print self.timeStamp() + " :=: tzinfo: now(): " + (str)(datetime.datetime.now().tzinfo) + " and then " + (str)(timeThresholdVar.tzinfo)
            return

        insertionCounter = -1        ## array index at which to finally insert before
        bestDiffSoFar = -1    ## minimal time difference between the optimal and possible insertion points

        ## PATCH to make thread-safe: start with cart 1 - never touch 0!
        ###YATES_COMMENT: This loop finds the the cart (Song or cart) which has the
        ###                    closest start time to the start time of the cart (cart)
        ###                    which we would like to insert.
        for ctr in range(1, len(self.Arr)):
            cartStart = self.Arr[ctr].GetStartTime()
            if cartStart is None:
                print self.timeStamp() + " :=: CQ :: InsertCart :: Null Pointer Error :: InsertCart failed!"
                return
            relevantStartTime = datetime.datetime.fromtimestamp(time.mktime(cartStart))

            ###YATES_COMMENT: This line gives us the difference between where we want
            ###                    to insert the next cart and the starting time of the cart
            ###                    we're looking at.
            ###                    If relevantInsertTime > relevantStartTime, difference > 0
            ###                    So a value of 0...maxOffset would be acceptable, and we
            ###                    will insert it before the song we're currently looking at (Arr[ctr])

            ## this allows for the (documented) overflow behavior of timedelta when it is negative
            difference = relevantInsertTime - relevantStartTime
            ###YATES_COMMENT: If the difference in days is negative, that implies that
            ###                    relevantStartTime > relevantInsertTime, and the song comes after
            ###                    the relevantStartTime, but still possibly within the relevantStartTime +/- maxOffset
            ###
            ###                    If we do
            ###    datetime.timedelta(days=1) - ((relevantStartTime - relevantInsertTime) + datetime.timedelta(days=1))
            ###                    We'll get the positive number of minutes after the playtime that we want.
            ###                    If it's less than 5, this will work for appending instead of prepending.

            if difference.days is -1:
                difference = relevantStartTime - relevantInsertTime


            if difference.seconds < bestDiffSoFar or bestDiffSoFar is -1:
                insertionCounter = ctr
                bestDiffSoFar = difference.seconds
                ###YATES_COMMENT: This is a silly if statement.  It wont ever execute.
                ###                    It's a possibility that difference.seconds >= bestDiffSoFar,
                ###                    But initializing bestDiffSoFar = difference.seconds

                ###YATES_COMMENT: The intent of this if statement is to break out of
                ###                    the loop if we've gone past the "sweet" spot in the
                ###                    playlist.

                ###YATES_COMMENT: Example time:
                ###                    relevantInsertTime is :30:00.
                ###                    cart[1] :28:00 till :31:00
                ###                    difference is :02:00, < bestDiffSoFar
                ###                    bestDiffSoFar = :02:00
                ###
                ###                    cart[2] :31:00 till :33:00
                ###                    difference is :05:00 !< bestDiffSoFar
                ###
                ###                    So if we keep looking at songs, our difference
                ###                    will continue to get larger and larger.  No point
                ###                    in continuing to look further.
                ###                    I think this needs to be unindented by one tab
                ###                    so that it's not a possible effect of comparing
                ###                    the times.  Currently 99% sure it's dead code.
            if difference.seconds > bestDiffSoFar:
                break
        ###YATES_COMMENT: By checking the times this way, we're forcing ourselves
        ###                    to only allow adding of carts before
        print self.timeStamp() + " :=: CQ :: InsertCart :: Done searching through tracks"
        print self.timeStamp() + " :=: CQ :: InsertCart :: insertionCounter is " + (str)(insertionCounter)
        print self.timeStamp() + " :=: CQ :: InsertCart :: Current best track is: " + self.Arr[insertionCounter].PrintCart()

        offset = 0
#        print self.timeStamp() + " :=: CQ :: InsertCart :: Current best insert time is " + (str)(self.Arr[insertionCounter].getTimeStruct())
        if bestDiffSoFar <= maxOffset:
            ## this lets us remove the inserted carts upon stopping playback
            ## they will be readded (and start slots recalculated) on next start
            ## get Carts to insert

            for cType in cartTypes:
                cart = database.get_cart(cType)
                print self.timeStamp() + " :=: CQ :: InsertCart :: Inserting cart " + cart.Issuer + " - " + cart.Title + " at index " + (str)(insertionCounter+offset) + " with start time " + self.Arr[insertionCounter].GetFmtStartTime()
                # + " with start time: " + self.Arr[insertionCounter+offset].getTimeStruct()
                self.Arr.insert(insertionCounter+offset, cart)
                offset += 1
            self.GenStartTimes(insertionCounter)
            print self.timeStamp() + " :=: CQ :: InsertCart :: Exiting Function"
        else:
            print self.timeStamp() + " :=: CQ :: InsertCart :: Could not find a spot to insert carts"
            print self.timeStamp() + " :=: CQ :: InsertCart :: bestDiffSoFar = " + (str)(bestDiffSoFar)
            print self.timeStamp() + " :=: CQ :: InsertCart :: best cart star time = : " + self.Arr[ctr].GetFmtStartTime()
            for cType in cartTypes:
                cart = database.get_cart(cType)
                print self.timeStamp() + " :=: CQ :: InsertCart :: Inserting cart " + cart.Issuer + " - " + cart.Title + " at index " + (str)(insertionCounter+offset) + " with start time " + self.Arr[insertionCounter].GetFmtStartTime()
                # + " with start time: " + self.Arr[insertionCounter+offset].getTimeStruct()
                self.Arr.insert(insertionCounter+offset, cart)
                offset += 1
            self.GenStartTimes(insertionCounter)

            self.Arr[ctr].PrintCart()

    ###YATES_COMMENT: Function to start playing the first cart.     Maybe called
    ###                    by a module to start songs, or as a... callback? when the
    ###                    automation button in state "Stopped" is clicked.
    def Start(self, click=False):
        print self.timeStamp() + " :=: CQ :: Start :: Entered Function"
        self.KeepGoing = True

        if click is True:
            print self.timeStamp() + " :=: CQ :: Start :: Calling GenStartTimes()"
            self.GenStartTimes(0)

        try:
            self.Meter.Start()
            self.Arr[0].Start(self.Transition)
            database.log_cart(self.Arr[0].ID)

            print self.timeStamp() + " :=: \t" + self.Arr[0].Title + " by " + self.Arr[0].Issuer
        except IndexError:
            print self.timeStamp() + " :=: CQ :: Start :: ERROR :: Queue is empty!!!"
            return

        ###If called by button click, InsertAllCarts under a new thread.
        if click is True:
            print self.timeStamp() + " :=: CQ :: Start :: Starting new InsertAllCarts() Thread"
            thread.start_new_thread(self.InsertAllCarts, ())

        self.UIUpdate()

    def StopSoon(self):
        print self.timeStamp() + " :=: CQ :: StopSoon :: Slow stop registered"
        self.KeepGoing = False

    def IsPlaying(self):
        return self.Arr[0].IsPlaying()

    def IsStopping(self):
        return not self.KeepGoing

    ## passed to Meter on instantiation
    def MeterFeeder(self):
        if len(self.Arr) > 0:
            return self.Arr[0].MeterFeeder()
        else:
            return ("-:--", "-:--", "", "", "", "")

    def timeStamp(self):
        return time.asctime(time.localtime(time.time()))
