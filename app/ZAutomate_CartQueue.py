import datetime
import time
from ZAutomate_Meter import Meter
import ZAutomate_DBInterface as database

METER_WIDTH = 800

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
### types      array of cart types to play
### minute     target play time within each hour
### max_delta  maximum deviation from minute, in seconds
AUTOMATION_CARTS = [
    {
        "types": ["StationID"],
        "minute": 1,  # TODO: should this be 0?
        "max_delta": 300
    },
    {
        "types": ["StationID", "PSA"],
        "minute": 15,
        "max_delta": 300
    },
    {
        "types": ["StationID", "Underwriting"],
        "minute": 30,
        "max_delta": 300
    },
    {
        "types": ["StationID", "PSA"],
        "minute": 45,
        "max_delta": 300
    }
]

PLAYLIST_MIN_LENGTH = 10

class CartQueue(object):

    # TODO: move to Automation?
    _meter = None

    _show_id = -1
    _queue = None
    _queue_played = None
    _update_callback = None
    _is_playing = False

    def __init__(self, master, update_callback):
        # get the saved show ID or a random new show ID
        self._show_id = database.restore_show_id()
        if self._show_id is -1:
            self._show_id = database.get_new_show_id(-1)

        # initialize the queue
        self._queue = []
        self._queue_played = []
        self._update_callback = update_callback

        # initialize the meter
        self._meter = Meter(master, METER_WIDTH, self._get_meter_data, None)
        self._meter.grid(row=1, column=0, columnspan=4)

    def get_queue(self):
        return self._queue

    def save(self):
        database.save_show_id(self._show_id)

    def _enqueue(self):
        print time.asctime() + " :=: CartQueue :: Enqueuing " + self._queue[0].cart_id
        self._meter.start()
        self._queue[0].start(self.transition)
        database.log_cart(self._queue[0].cart_id)

    def _dequeue(self):
        if len(self._queue) > 0:
            print time.asctime() + " :=: CartQueue :: Dequeuing " + self._queue[0].cart_id

            # stop the cart
            self._queue[0].stop()
            self._meter.reset()

            # move the cart to the played list
            self._queue_played.append(self._queue.pop(0))

    def _is_artist_is_list(self, cart, array):
        if cart is None:
            return True

        for item in array:
            if cart.issuer is item.issuer:
                return True

        return False

    ## Generate start times for each item in the Queue
    ## This function is called when items are added to the queue and
    ## when the queue is started after a stop
    def _gen_start_times(self, begin_index=0):
        base_time = time.localtime()

        for i in range(begin_index, len(self._queue)):
            ## for each cart after the first, add the length of the previous
            ## track to produce the start time
            if i > 0:
                prev_start_time = self._queue[i - 1].start_time
                prev_length = self._queue[i - 1]._get_meter_data()[1] / 1000
                start_time = time.mktime(prev_start_time) + prev_length
                base_time = time.localtime(start_time)

            ## set the current cart's starting time
            self._queue[i].start_time = base_time

    def add_tracks(self):
        begin_index = len(self._queue)

        while len(self._queue) < PLAYLIST_MIN_LENGTH:
            # retrieve playlist from database
            show = database.get_next_playlist(self._show_id)
            self._show_id = show["showID"]

            # add each track whose artist isn't already in the queue or playlist list
            self._queue.extend([t for t in show["playlist"] if not self._is_artist_is_list(t, self._queue_played) and not self._is_artist_is_list(t, self._queue)])

            print time.asctime() + " :=: CartQueue :: Added tracks, length is " + (str)(len(self._queue))

        self._gen_start_times(begin_index)

    ## Insert carts into the queue.
    ## This function is called when the queue is started and when the queue
    ## runs out of carts.
    def _insert_carts(self):
        for entry in AUTOMATION_CARTS:
            self._insert_cart(entry["types"], entry["minute"], entry["max_delta"])

    ## Insert carts into the current hour according to a config entry.
    ## This function inserts carts as close as possible to the target start time,
    ## even if the target window is not met.
    def _insert_cart(self, types, minute, max_delta):
        target = datetime.datetime.now().replace(minute=minute, second=0, microsecond=0)

        ## don't insert if the window has already passed this hour
        if target + datetime.timedelta(seconds=max_delta) < datetime.datetime.now():
            return

        print time.asctime() + " :=: CartQueue :: Target insert time is " + (str)(target)

        ## find the position in queue with the closest start time to target
        min_index = -1
        min_delta = -1

        ## TODO: the head of the queue is ignored for multi-threading safety
        ##       however, it might be more prudent to use a lock
        for i in range(1, len(self._queue)):
            start_time = self._queue[i].start_time
            start_time = datetime.datetime.fromtimestamp(time.mktime(start_time))

            delta = abs(target - start_time)

            if min_delta is -1 or delta < min_delta:
                min_index = i
                min_delta = delta
            elif delta > min_delta:
                break

        print time.asctime() + " :=: CartQueue :: min_index is " + (str)(min_index)
        print time.asctime() + " :=: CartQueue :: min_delta is " + (str)(min_delta)

        if min_delta.seconds <= max_delta:
            print time.asctime() + " :=: CartQueue :: Carts inserted within target window"
        else:
            print time.asctime() + " :=: CartQueue :: Carts not inserted within target window"

        ## insert a cart of each type into the queue
        index = min_index
        for t in types:
            cart = database.get_cart(t)
            self._queue.insert(index, cart)
            index += 1
        self._gen_start_times(min_index)

    ## Remove all carts from the queue.
    ## This function is called after a hard stop and before new carts
    ## are inserted. The queue must be cleared at these times in order
    ## to ensure that carts are played at correct times.
    def _remove_carts(self):
        # TODO: this line is sufficient if current track is separated from queue
        # self._queue = [c for c in self._queue if cart.cart_type not in CART_TYPES]

        if self._queue[0].is_playing():
            i = 1
        else:
            i = 0

        while i < len(self._queue):
            if self._queue[i].cart_type in CART_TYPES:
                self._queue.pop(i)
            else:
                i += 1

    ### Start the front track in the queue.
    ### This function is called when Automation is started and after a track ends.
    def start(self):
        self._is_playing = True
        self._gen_start_times()
        self._insert_carts()
        self._enqueue()

        self._update_callback()

    def stop_soft(self):
        self._is_playing = False

    # TODO: stop_hard method
    ### Transition to the next cart after a cart finishes.
    ### This function is called when a cart ends or when it is stopped.
    def transition(self):
        self._dequeue()

        # refill the queue if it is too short
        if len(self._queue) < PLAYLIST_MIN_LENGTH:
            print time.asctime() + " :=: CartQueue :: Refilling the playlist"
            self.add_tracks()
            self._queue_played = []
            self._remove_carts()
            self._insert_carts()

        # add carts if there aren't any carts in the queue
        carts = [c for c in self._queue if c.cart_type in CART_TYPES]

        if len(carts) is 0:
            print time.asctime() + " :=: CartQueue :: Refilling carts"
            self._insert_carts()

        if self._is_playing is True:
            # start the next track if the current track ended
            self._enqueue()
        else:
            # remove all carts if the queue was stopped
            print time.asctime() + " :=: CartQueue :: Removing all carts"
            self._remove_carts()

        self._update_callback()

    ## passed to Meter on instantiation
    def _get_meter_data(self):
        if len(self._queue) > 0:
            return self._queue[0]._get_meter_data()
        else:
            return ("-:--", "-:--", "", "", "", "")
