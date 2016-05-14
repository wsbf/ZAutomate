"""The grid_obj module provides the GridObj class."""
import time
import Tkinter
from Tkinter import Frame, Canvas
import database

CART_WIDTH = 175
CART_HEIGHT = 75

COLOR_DEFAULT = "#DDDDDD"
COLOR_PLAYING = "#00FF00"
COLOR_READY = "#009999"
COLOR_TYPES_NEW = {
    "PSA": "#0099A3",
    "Underwriting": "#BF5FFF",
    "StationID": "#FF6600",
    "Promotion": "#888888",  # TODO: set Promotion color
    "R": "#888888",          # TODO: set Recently Reviewed color
    "N": "#FF1010",
    "H": "#FF4242",
    "M": "#FF6969",
    "L": "#8D0000",
    "O": "#CCC"
}
COLOR_TYPES_PLAYED = {
    "Underwriting": "#9400D3",
    "PSA": "#006A33",
    "StationID": "#8B4500",
    "Promotion": "#AAAAAA",  # TODO: set Promotion color
    "R": "#AAAAAA",          # TODO: set Recently Reviewed color
    "N": "#2258D5",
    "H": "#4D7CE6",
    "M": "#6D92E6",
    "L": "#005280",
    "O": "#999"
}

COLOR_TITLE = "#FFFFFF"
COLOR_ISSUER = "#FFFFFF"
COLOR_LENGTH = "#FFFF00"

FONT = ("Helvetica", 10, "bold")

def get_fmt_time(seconds):
    """Get a formatted time string from a number of seconds.

    :param seconds
    """
    return time.strftime("%M:%S", time.localtime(seconds))

class GridObj(Frame):
    """The GridObj class is a UI element for a cell in a grid of carts."""
    _parent = None
    _end_callback = None
    _enable_remove = False
    _next_key = None

    _rect = None
    _title = None
    _issuer = None
    _length = None

    _cart = None
    _is_playing = False

    def __init__(self, parent, end_callback, enable_remove, next_key=None):
        """Construct a grid object.

        :param parent
        :param enable_remove
        :param next_key
        """
        Frame.__init__(self, parent.master, bd=1, relief=Tkinter.SUNKEN, bg=COLOR_DEFAULT, width=CART_WIDTH, height=CART_HEIGHT)
        self._parent = parent
        self._end_callback = end_callback
        self._enable_remove = enable_remove
        self._next_key = next_key

        self._rect = Canvas(self, width=CART_WIDTH, height=CART_HEIGHT, bg=COLOR_DEFAULT)

        self._title = self._rect.create_text(5, 5, width=CART_WIDTH, anchor=Tkinter.NW, font=FONT, fill=COLOR_TITLE, text="")
        self._issuer = self._rect.create_text(CART_WIDTH / 2, 25, width=CART_WIDTH, anchor=Tkinter.N, font=FONT, fill=COLOR_ISSUER, text="")
        self._length = self._rect.create_text(CART_WIDTH / 2, CART_HEIGHT - 15, anchor=Tkinter.S, font=FONT, fill=COLOR_LENGTH, text="")

        self._rect.bind("<ButtonPress-1>", self._left_click)
        self._rect.bind("<Button-2>", self._right_click)
        self._rect.bind("<Button-3>", self._right_click)
        self._rect.pack()

    def get_cart(self):
        """Get the cart of the grid object."""
        return self._cart

    def set_cart(self, cart):
        """Set a cart for the grid object.

        :param cart
        """
        self._cart = cart

        length = self._cart.get_meter_data()[1] / 1000

        self._rect.itemconfigure(self._title, text=self._cart.title)
        self._rect.itemconfigure(self._issuer, text=(self._cart.issuer + " " + self._cart.cart_id))
        self._rect.itemconfigure(self._length, text=get_fmt_time(length))
        self._rect["bg"] = COLOR_TYPES_NEW[self._cart.cart_type]

    def remove_cart(self):
        """Remove a cart from the grid object."""
        self._cart = None
        self._rect.itemconfigure(self._title, text="")
        self._rect.itemconfigure(self._issuer, text="")
        self._rect.itemconfigure(self._length, text="")
        self._rect["bg"] = COLOR_DEFAULT

    def has_cart(self):
        """Get whether the grid object has a cart."""
        return self._cart is not None

    def start(self):
        """Start the grid object."""
        self._is_playing = True
        self._rect["bg"] = COLOR_PLAYING
        self._cart.start(self._end_callback)

        self._parent.set_active_grid_obj(self)
        self._parent._meter.start()

        database.log_cart(self._cart.cart_id)

    def reset(self, auto_queue=False):
        """Reset the grid object.

        :param auto_queue: whether to start the next grid object
        """
        self._is_playing = False
        self._rect["bg"] = COLOR_TYPES_PLAYED[self._cart.cart_type]

        self._parent.set_active_grid_obj(None)
        self._parent._meter.reset()

        if auto_queue and self._next_key is not None and self._parent._grid[self._next_key].has_cart():
            self._parent._grid[self._next_key].start()

    def _left_click(self, *args):
        """Respond to a left click.

        If this grid object is playing, then it stops. Otherwise, if this
        grid object has a cart and no other cart is playing, then it starts.

        :params args
        """
        if self._cart is not None:
            if self._is_playing:
                self._cart.stop()
                self.reset()
            elif not self._parent.is_playing():
                self.start()

        ### click on an empty cart; add the clipboarded cart
        # TODO: move to DJ Studio
        else:
            try:
                self.set_cart(self._parent._selected_cart)
            except AttributeError:
                pass

        # TODO: move to DJ Studio
        try:
            self._parent._entry.focus_set()
        except AttributeError:
            pass

    def _right_click(self, *args):
        """Respond to a right click.

        If this grid object is not playing and removing is enable, then
        it's cart is removed.

        :params args
        """
        if self._enable_remove and self.has_cart() and not self._is_playing:
            self.remove_cart()

            # TODO: move to DJ Studio
            try:
                self._parent._entry.focus_set()
            except AttributeError:
                pass
