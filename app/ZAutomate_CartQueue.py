import datetime
import thread
import time
from ZAutomate_Meter import Meter
from ZAutomate_DBInterface import DBInterface

VALID_CART_TYPES = [
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

### Automation will add to its playlist when there are this many or fewer tracks to go
PlistGenThreshold = 10
### How many prior carts to keep in the queue
PlistHistThreshold = 3

class CartQueue():

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

    Logger = None
    ###ThreadRunning - Boolean Semaphore for thread stuff.
    ThreadRunning = False

    def __init__(self, master, width, uiu):
        ###Instantiate new Array for Carts
        self.Arr = []
        self.PlayedArr = []
        ###Set UIUpdate Function pointer to passed callback function
        self.UIUpdate = uiu

        ###YATES_COMMENT: What/Where is PlistHistThreshold?
        ###YATES_ANSWER : ZAutomate_Config.py, currently set to 3;
        self.HistLimit = PlistHistThreshold # GLOBAL

        ###YATES_COMMENT: What/Where is MeterFeeder?
        ###YATES_ANSWER: It's a Function or Macro, defined at the bottom,
        ###                  it returns self.Arr[0].MeterFeeder();
        self.Meter = Meter(master,width-10, self.MeterFeeder, self.Transition)
        self.Meter.grid(row=1,column=0,columnspan=4)

    ###YATES_COMMENT: Extend takes an array of Carts and appends it to the end
    ###                    of self.Arr.  cartArr's type code must be the same as Arr's
    ###                    typecode.  Generates the timestamps for the start times
    ###                    after appending the array.
    def Extend(self, cartArr):
        lenOld = len(self.Arr)
        ###YATES_COMMENT: What does Array.extend(Array:cartArr) do?
        ###Documentation: http://docs.python.org/library/array.html#array.array.extend
        ###Append items from iterable to the end of the array.
        ###If iterable is another array, it must have exactly the same type code;
        ###if not, TypeError will be raised. If iterable is not an array,
        ###it must be iterable and its elements must be the right type to be appended to the array.
        try:
            self.Arr.extend(cartArr)
        except TypeError:
            print self.timeStamp() + " :=: CQ : Tried to extend Arr, parameter not of same type-code"
        print self.timeStamp() + " :=: CartQueue :: Extend :: Generating start times"
        self.GenStartTimes(lenOld)


    ###YATES_COMMENT: Dequeue's the 0th entry from the CartQueue::Arr array.
    ###                    Stops the cart first, then reset's the meter.
    def Dequeue(self):
        try:
            print self.timeStamp() + " :=: CQ :: Dequeue :: Stopping track " + self.Arr[0].PrintCart()
            self.Arr[0].Stop()
            print self.timeStamp() + " :=: CQ :: Dequeue :: Dequeuing " + self.Arr[0].PrintCart()
            self.PlayedArr.append(self.Arr.pop(0))
            self.Meter.Reset()
        except IndexError:
            print self.timeStamp() + " :=: Closing... queue was empty... I hope you're debugging, Zach..."
        print self.timeStamp() + " :=: CQ :: Dequeue :: Leaving Dequeue..."

    def IsCartInList(self, cartvar, Arr):
        result = 0
        #print self.timeStamp() + " :=: CQ :: IsCartInList :: Checking for cart " + (str)(cartvar.Issuer) + " - " + (str)(cartvar.Title)
        if cartvar == None:
            return 1
        for item in Arr:
            if( cartvar.Issuer == item.Issuer and
                 cartvar.Title == item.Title):
                print self.timeStamp() + " :=: CQ :: IsCartInList :: Found Artist " + (str)(cartvar.Issuer) + " - " + (str)(cartvar.Title)
                result = 1
                break
        return result

    def IsArtistInList(self, cartvar, Arr):
        result = 0
        #print self.timeStamp() + " :=: CQ :: IsArtistInList :: Checking for artist " + (str)(cartvar.Issuer)
        if cartvar == None:
            result = 1
        else:
            for item in Arr:
                if cartvar.Issuer == item.Issuer:
                    print self.timeStamp() + " :=: CQ :: IsArtistInList :: Found Artist " + (str)(cartvar.Issuer)
                    result = 1
                    break
        return result

    ###YATES_COMMENT: Loops PlistGenThreshold - len(self.arr) times, calling
    ###                    DBInterface().Get_Next_Playlist() and appending it to
    ###                    the type code Cart array self.arr.
    ###                    PlistGenThreshold can be found in ZAutomate_Config.py
    ###                    Set to 10 when I started.
    ###                    Calls the UIUpdate callback when done.
    def InitialFill(self):
        print self.timeStamp() + " :=: CartQueue :: InitialFill :: PlistGenThreshold = " + (str)(PlistGenThreshold)
        while len(self.Arr) < PlistGenThreshold:
            self.Extend(DBInterface().Get_Next_Playlist())
            print self.timeStamp() + " :=: CartQueue :: InitialFill enqueued... new length is "+(str)(len(self.Arr))
        self.UIUpdate()

    ###YATES_COMMENT: Same as InitialFill, but also regenerates StartTimes,
    ###                    and calls InsertAllCarts before calling the UIUPdate callback
    def Refill(self):
        print self.timeStamp() + " :=: CQ :: Refill :: Trying to refill the cart"
        lenOld = len(self.Arr)
        print self.timeStamp() + " :=: CQ :: Dequeue :: PlayedArr is " + self.PrintPlayedArr()
        while len(self.Arr) < PlistGenThreshold:
            refillList = DBInterface().Get_Next_Playlist()
##            self.Extend( DBInterface().Get_Next_Playlist() )
            for cart in refillList:
                ###Check to make sure the cart isn't already in Self.Arr, and hasn't been played in the
                ###Last fill session
                if self.IsCartInList(cart, self.PlayedArr) == 0 and self.IsCartInList(cart, self.Arr) == 0:
                    ###Check to see if the artist is already in the list.
                    if self.IsArtistInList(cart, self.Arr) == 0 and self.IsArtistInList(cart, self.PlayedArr) == 0:
                        self.Arr.append(cart)
                    else:
                        print self.timeStamp() + " :=: CQ :: Refill :: Checking for existing Artist :: found duplicate artist: " + (str)(cart.Issuer)
                else:
                    print self.timeStamp() + " :=: CQ :: Refill :: Checking for existing track :: found duplicate track: " + (str)(cart.Issuer) + " - " + (str)(cart.Title)
        print self.timeStamp() + " :=: CQ :: Refill :: Refilled Carts, new CartQueue Length is " + (str)(len(self.Arr))
        print self.timeStamp() + " :=: CQ :: Refill :: Calling GenStartTimes(" + (str)(lenOld) + ")"
        self.GenStartTimes(lenOld - 1)
        print self.timeStamp() + " :=: CQ :: Refill :: Removing Carts from PlayedList"
        self.PlayedArr = []
        print self.timeStamp() + " :=: CQ :: Refill :: Calling InsertAllCarts()"
        self.InsertAllCarts()
        #thread.exit()
        ###YATES_COMMENT: InsertAllCarts exits the thread

    # is a callback ONLY on end of Cart
    ###YATES_COMMENT: This is the transition function.  It's called, I believe,
    ###                    when the Start/Stopping/Stop button is pressed to stop automation
    ###                    or as a callback whenever a Cart finishes playing.
    def Transition(self):
        print self.timeStamp() + " :=: CQ :: Transition :: Began to transition"
        ###YATES_COMMENT: If queue is too small, start new thread to refill queue
        print self.timeStamp() + " :=: CQ :: Transition :: Checking for refilling everything..."
        if len(self.Arr) < PlistGenThreshold:
            print self.timeStamp() + " :=: CQ :: Transition :: Starting new Refill() thread"
            thread.start_new_thread(self.Refill, ( ) )
        print self.timeStamp() + " :=: CQ :: Transition :: Checking for refilling carts..."
        ###YATES_COMMENT: If we've got 0 carts, then our playlist was significantly longer
        ###               than an hour.  So lets refill some carts.
        if self.CountCartsInQueue() == 0:
           thread.start_new_thread(self.InsertAllCarts, ( ) )
        ###YATES_COMMENT: if self.KeepGoing is true, then we've just skipped a song.
        ###                    dequeue the front song (dequeue stops playing) and start
        ###                    the new front of queueue.
        print self.timeStamp() + " :=: CQ :: Transition :: Checking for keeping on keeping on..."
        if self.KeepGoing is True:
            print self.timeStamp() + " :=: CQ :: Transition :: Continuing"
            self.Dequeue()
            self.Start()
        ###YATES_COMMENT: If self.KeepGoing is not true, then we've done StopNow!.
        ###                    Remove the front of queue (stops the song from playing),
        ###                    Clear out all the inserted carts, update the UI
        else:
            print self.timeStamp() + " :=: CQ :: Transition :: Stopping and clearing out first cart"
            self.Dequeue()
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

    ###YATES_COMMENT: This is the first good comment I've seen.

    ## Populate the TimeStruct inside each Cart. This is useful for PSA insertion, etc.
    ## Should be called when carts/songs are added to (or removed from?) playlist
    ## It is regenerated on every start and on every transition, which makes it accurate.
    ## It can be run to exclude the beginning of the Queue, with the startNdx parameter
    def GenStartTimes(self, startNdx=0):
        print self.timeStamp() + " :=: CQ :: GenStartTimes :: Entered Function"

        ###YATES_COMMENT: This works well as long as startNdx=0.
        ###                    If startNdx > 0, we need to calculate the time offset
        ###                    to the trakc we're starting to generate times for.
        ###                    Something like...
        #  offsetStartTime = Arr[0].GetTimeStruct();
        ###    Nota Bene: Cart::GetTimeStruct() returns the starting time for song.
        #  if(startNdx > 0)
        #      for(int i = 1; i < startNdx; i++)
        #          offsetStartTime += self.Arr[i].GetTimeStruct
        #
        ## time_struct representing this instant - only used if startNdx is 0
        baseTime = time.localtime()

        ###YATES_COMMENT: Should ctr be initialized before this?  For clarity?

        ### Also, the second if statement seems a little clunky given that the loop
        ### should never iterate so that ctr >= len(self.Arr).
        for ctr in range(startNdx, len(self.Arr)):
            ## for the first cart in the queue, use the current time as the base (above)
            if ctr > 0:
                ## get the prior cart's start time_struct and length in seconds
                ###YATES_COMMENT: NOTA BENE: Cart::GetTimeStruct() returns start.
                lastCartStart = self.Arr[ctr-1].GetTimeStruct()
                ###YATES_COMMENT: NOTA BENE: MeterFeeder() returns a n-Tuple of the
                ###                    form ( time_elapsed(), length(), Title, Issuer, ID, Type )
                ###                    where Title is SongTitle, Issuer is Artist, ID is SongID, Type is Rotation Type
                ###                    for songs.
                lastCartSecs = self.Arr[ctr-1].MeterFeeder()[1] / 1000

                ## compute the start of current cart in seconds, then convert to time_struct
                ### YATES_COMMENT: http://docs.python.org/library/time.html#time.mktime
                ### This is the inverse function of localtime().
                ### Its argument is the struct_time
                ### It returns a floating point number, for compatibility with time().
                ### If the input value cannot be represented as a valid time,
                ### either OverflowError or ValueError will be raised
                ### (which depends on whether the invalid value is caught by Python or the underlying C libraries).
                ### The earliest date for which it can generate a time is platform-dependent.
                try:
                    newSecs = time.mktime(lastCartStart) + lastCartSecs
                except TypeError:
                    print self.timeStamp() + " :=: CQ :: GenStartTimes("+(str)(startNdx)+") :: TypeError Encountered"
                    print self.timeStamp() + " :=: CQ :: GenStartTimes("+(str)(startNdx)+") :: ctr-1 = " + (str)(ctr-1)
                    print self.timeStamp() + " :=: CQ :: GenStartTimes("+(str)(startNdx)+") :: lastCartStart = " + (str)(lastCartStart)
                    print self.timeStamp() + " :=: CQ :: GenStartTimes("+(str)(startNdx)+") :: lastCartSecs = " + (str)(lastCartSecs)
                    print self.timeStamp() + " :=: CQ :: GenStartTimes("+(str)(startNdx)+") :: self.Arr[ctr-1] = " + (str)(self.Arr[ctr-1])
                    print self.timeStamp() + " :=: CQ :: GenStartTimes("+(str)(startNdx)+") :: " + self.Arr[ctr-1].PrintCart()
                except IndexError:
                    print self.timeStamp() + " :=: CQ :: GenStartTimes("+(str)(startNdx)+") :: IndexError Encountered"
                    print self.timeStamp() + " :=: CQ :: GenStartTimes("+(str)(startNdx)+") :: ctr-1 = " + (str)(ctr-1)
                    print self.timeStamp() + " :=: CQ :: GenStartTimes("+(str)(startNdx)+") :: lastCartStart = " + (str)(lastCartStart)
                    print self.timeStamp() + " :=: CQ :: GenStartTimes("+(str)(startNdx)+") :: lastCartSecs = " + (str)(lastCartSecs)


                ###YATES_COMMENT: localtime returns the local time + parameter offset (seconds).
                ###                    returns local time if parameter is omitted or 0.
                baseTime = time.localtime(newSecs)

            ## set the current cart's starting time
            if (ctr) < len(self.Arr):
                self.Arr[ctr].SetTimeStruct(baseTime)
        print self.timeStamp() + " :=: CQ :: GenStartTimes :: Exiting function"

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
        relevantInsertTime = datetime.datetime.now().replace(minute=0,second=0, microsecond=0)
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
            cartStart = self.Arr[ctr].GetTimeStruct()
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
                cart = DBInterface().Cart_Request(cType)
                print self.timeStamp() + " :=: CQ :: InsertCart :: Inserting cart " + cart.Issuer + " - " + cart.Title + " at index " + (str)(insertionCounter+offset) + " with start time " + self.Arr[insertionCounter].GetFmtTime()
                # + " with start time: " + self.Arr[insertionCounter+offset].getTimeStruct()
                self.Arr.insert(insertionCounter+offset, cart)
                offset += 1
            self.GenStartTimes(insertionCounter)
            print self.timeStamp() + " :=: CQ :: InsertCart :: Exiting Function"
        else:
            print self.timeStamp() + " :=: CQ :: InsertCart :: Could not find a spot to insert carts"
            print self.timeStamp() + " :=: CQ :: InsertCart :: bestDiffSoFar = " + (str)(bestDiffSoFar)
            print self.timeStamp() + " :=: CQ :: InsertCart :: best cart star time = : " + self.Arr[ctr].GetFmtTime()
            for cType in cartTypes:
                cart = DBInterface().Cart_Request(cType)
                print self.timeStamp() + " :=: CQ :: InsertCart :: Inserting cart " + cart.Issuer + " - " + cart.Title + " at index " + (str)(insertionCounter+offset) + " with start time " + self.Arr[insertionCounter].GetFmtTime()
                # + " with start time: " + self.Arr[insertionCounter+offset].getTimeStruct()
                self.Arr.insert(insertionCounter+offset, cart)
                offset += 1
            self.GenStartTimes(insertionCounter)

            self.Arr[ctr].PrintCart()

    def Length(self):
        return len(self.Arr)

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
            DBInterface().Logbook_Log(self.Arr[0].ID)

            print self.timeStamp() + " :=: \t" + self.Arr[0].Title + " by " + self.Arr[0].Issuer
        except IndexError:
            print self.timeStamp() + " :=: CQ :: Start :: ERROR :: Queue is empty!!!"
            return

        ###If called by button click, InsertAllCarts under a new thread.
        if click is True:
            print self.timeStamp() + " :=: CQ :: Start :: Starting new InsertAllCarts() Thread"
            thread.start_new_thread(self.InsertAllCarts, ( ) )

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
        try:
            return self.Arr[0].MeterFeeder()
        except IndexError:
            print self.timeStamp() + " :=: Index out of bounds error, len(self.Arr) = " + (str)(len(self.Arr))

    ## called by Automation to fill up the playlist box
    def GetArray(self):
        ret = []
        for cart in self.Arr:
            ret.append( (cart.GetFmtTime(), cart.Title, cart.Issuer) )
        return ret

    ###YATES_METHOD
    def PrintPlayedArr(self):
        playedStr = ""
        for cart in self.PlayedArr:
            playedStr = playedStr + cart.PrintCart() + "\n"
        return playedStr

    def PrintArr(self):
        arrStr = ""
        for cart in self.Arr:
            arrStr = arrStr + cart.PrintCart() + "\n"
        return arrStr

    def timeStamp(self):
        return time.asctime(time.localtime(time.time()))

    def CountCartsInQueue(self):
        count = 0
        for ctr in range(1, len(self.Arr)):
            if self.Arr[ctr].cartType in VALID_CART_TYPES:
                count = count + 1
        return count
