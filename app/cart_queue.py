"""The cart_queue module provides the CartQueue class."""
import datetime
import time
import database
from meter import Meter

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
### type       cart type to play
### minute     target play time within each hour
### max_delta  maximum deviation from minute, in seconds
AUTOMATION_CARTS = [
    {
        "type": "StationID",
        "minute": 0,
        "max_delta": 300
    },
    {
        "type": "PSA",
        "minute": 15,
        "max_delta": 300
    },
    {
        "type": "StationID",
        "minute": 30,
        "max_delta": 300
    },
    {
        "type": "Underwriting",
        "minute": 30,
        "max_delta": 300
    },
    {
        "type": "PSA",
        "minute": 45,
        "max_delta": 300
    }
]

PLAYLIST_MIN_LENGTH = 10

def is_artist_is_list(cart, array):
    """Get whether the artist of a cart is in a list of carts.

    :param cart
    :param array
    """
    if cart is None:
        return True

    for item in array:
        if cart.issuer is item.issuer:
            return True

    return False

class CartQueue(object):
    """The CartQueue class is a queue that generates radio content.

    To generate content, the cart queue selects random playlists
    from the server-side API and inserts carts according
    to a configuration defined by AUTOMATION_CARTS.
    """

    # TODO: move to Automation?
    _meter = None

    _show_id = -1
    _queue = None
    _queue_played = None
    _update_callback = None
    _is_playing = False

    def __init__(self, master, update_callback):
        """Construct a cart queue.

        :param master: master Frame used for the meter
        :param update_callback: callback to update the UI
        """

        # get the saved show ID or a random new show ID
        self._show_id = database.restore_show_id()
        if self._show_id is -1:
            self._show_id = database.get_new_show_id(-1)

        # initialize the queue
        self._queue = []
        self._queue_played = []
        self._update_callback = update_callback

        # initialize the meter
        self._meter = Meter(master, METER_WIDTH, self._get_meter_data)
        self._meter.grid(row=1, column=0, columnspan=4)

    def get_queue(self):
        """Get the queue."""
        return self._queue

    def save(self):
        """Save the current show ID to a file."""
        database.save_show_id(self._show_id)

    def _enqueue(self):
        """Start the first track in the queue."""
        print time.asctime() + " :=: CartQueue :: Enqueuing " + self._queue[0].cart_id

        self._queue[0].start(self.transition)
        self._meter.start()

        database.log_cart(self._queue[0].cart_id)

    def _dequeue(self):
        """Stop and dequeue the first track in the queue."""
        if len(self._queue) > 0:
            print time.asctime() + " :=: CartQueue :: Dequeuing " + self._queue[0].cart_id

            # stop the cart
            self._queue[0].stop()
            self._meter.reset()

            # move the cart to the played list
            self._queue_played.append(self._queue.pop(0))

    def _gen_start_times(self, begin_index=0):
        """Set the start time of each item in the queue.

        This function is called when items are added to the Queue
        and when the queue is started after a stop.

        :param begin_index
        """
        start_time = datetime.datetime.now()

        for i in range(begin_index, len(self._queue)):
            if i > 0:
                prev = self._queue[i - 1]
                prev_length = datetime.timedelta(milliseconds=prev.get_meter_data()[1])
                start_time = prev.start_time + prev_length

            self._queue[i].start_time = start_time

    def add_tracks(self):
        """Append tracks to the queue.

        Previously, new playlists were retrieved by incrementing the
        current show ID, but incrementing is not guaranteed to yield
        a valid playlist and it leads to an infinite loop if no valid
        playlists are found up to the present, so now a random show ID
        is selected every time. Since shows are not scheduled according
        to genre continuity, selecting a random show every time has no
        less continuity than incrementing.
        """
        begin_index = len(self._queue)

        while len(self._queue) < PLAYLIST_MIN_LENGTH:
            # retrieve playlist from database
            self._show_id = database.get_new_show_id(self._show_id)
            playlist = database.get_playlist(self._show_id)

            # add each track whose artist isn't already in the queue or played list
            self._queue.extend([t for t in playlist if not is_artist_is_list(t, self._queue_played) and not is_artist_is_list(t, self._queue)])

            print time.asctime() + " :=: CartQueue :: Added tracks, length is " + (str)(len(self._queue))

        self._gen_start_times(begin_index)

    def _insert_carts(self):
        """Insert carts into the queue.

        This function is called when the queue is started and when the queue
        runs out of carts.
        """
        for entry in AUTOMATION_CARTS:
            self._insert_cart(entry["type"], entry["minute"], entry["max_delta"])

    def _insert_cart(self, cart_type, minute, max_delta):
        """Insert carts into the current hour according to a config entry.

        This function inserts carts as close as possible to the target
        start time, even if the target window is not met.

        :param cart_type
        :param minute
        :param max_delta
        """
        target = datetime.datetime.now().replace(minute=minute, second=0, microsecond=0)
        target_delta = datetime.timedelta(seconds=max_delta)

        # don't insert if the target window has already passed this hour
        if target + target_delta < datetime.datetime.now():
            return

        # don't insert if the queue has not reached the target window
        last = self._queue[len(self._queue) - 1]
        last_length = datetime.timedelta(milliseconds=last.get_meter_data()[1])

        if last.start_time + last_length < target - target_delta:
            return

        print time.asctime() + " :=: CartQueue :: Target insert time is " + (str)(target)

        # find the position in queue with the closest start time to target
        min_index = -1
        min_delta = None

        for i in range(0, len(self._queue)):
            delta = abs(target - self._queue[i].start_time)

            if min_delta is None or delta < min_delta:
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

        # insert cart into the queue
        cart = database.get_cart(cart_type)

        self._queue.insert(min_index, cart)
        self._gen_start_times(min_index)

    def _remove_carts(self):
        """Remove all carts from the queue.

        This function is called after a hard stop and before new carts
        are inserted. The queue must be cleared of carts after every
        stop because the start times may not meet the cart configuration
        when the queue is restarted.
        """
        self._queue = [cart for cart in self._queue if cart.cart_type not in CART_TYPES]

    def start(self):
        """Start the queue."""
        self._is_playing = True
        self._gen_start_times()
        self._insert_carts()
        self._enqueue()

        self._update_callback()

    def stop_soft(self):
        """Stop the queue at the end of the current track."""
        self._is_playing = False

    # TODO: stop_hard method

    def transition(self):
        """Transition to the next track.

        This function is called when a track ends or when the queue is stopped.
        """
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

    def _get_meter_data(self):
        """Get meter data for the first track in the queue."""
        if len(self._queue) > 0:
            return self._queue[0].get_meter_data()
        else:
            return None
