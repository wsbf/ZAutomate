"""The cartgrid module provides the Grid class."""
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
    _cart = None
    _key = None
    _is_playing = False

    _rect = None
    _title = None
    _issuer = None
    _length = None

    _on_left_click = None
    _on_right_click = None
    _on_cart_end = None

    def __init__(self, parent, key, on_left_click, on_right_click, on_cart_end):
        """Construct a grid object.

        :param parent
        :param on_left_click: callback for left click
        :param on_right_click: callback for right click
        :param on_cart_end: callback for when a cart ends
        """
        Frame.__init__(self, parent.master, bd=1, relief=Tkinter.SUNKEN, bg=COLOR_DEFAULT, width=CART_WIDTH, height=CART_HEIGHT)
        self._key = key
        self._on_left_click = on_left_click
        self._on_right_click = on_right_click
        self._on_cart_end = on_cart_end

        self._rect = Canvas(self, width=CART_WIDTH, height=CART_HEIGHT, bg=COLOR_DEFAULT)

        self._title = self._rect.create_text(5, 5, width=CART_WIDTH, anchor=Tkinter.NW, font=FONT, fill=COLOR_TITLE, text="")
        self._issuer = self._rect.create_text(CART_WIDTH / 2, 25, width=CART_WIDTH, anchor=Tkinter.N, font=FONT, fill=COLOR_ISSUER, text="")
        self._length = self._rect.create_text(CART_WIDTH / 2, CART_HEIGHT - 15, anchor=Tkinter.S, font=FONT, fill=COLOR_LENGTH, text="")

        self._rect.bind("<ButtonPress-1>", self._left_click)
        self._rect.bind("<Button-2>", self._right_click)
        self._rect.bind("<Button-3>", self._right_click)
        self._rect.pack()

    def has_cart(self):
        """Get whether the grid object has a cart."""
        return self._cart is not None

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

    def is_playing(self):
        """Get whether the cart is playing."""
        return self._is_playing

    def start(self):
        """Start the grid object."""
        self._is_playing = True
        self._rect["bg"] = COLOR_PLAYING
        self._cart.start(self._cart_end)

        database.log_cart(self._cart.cart_id)

    def stop(self):
        """Stop the grid object."""
        self._is_playing = False
        self._rect["bg"] = COLOR_TYPES_PLAYED[self._cart.cart_type]
        self._cart.stop()

    def _left_click(self, *args):
        """Respond to a left click."""
        self._on_left_click(self, self._key)

    def _right_click(self, *args):
        """Respond to a right click."""
        self._on_right_click(self)

    def _cart_end(self):
        """Respond to the end of the cart."""
        self._on_cart_end(self._key)

class Grid(object):
    """The Grid class is a grid of carts."""
    _rows = None
    _cols = None
    _grid = None
    _active_cell = None

    _enable_remove = None
    _on_cart_start = None
    _on_cart_stop = None
    _on_cart_end = None
    _on_left_click = None

    def __init__(self, parent, rows, cols, enable_remove, on_cart_start, on_cart_stop, on_cart_end, on_left_click):
        self._rows = rows
        self._cols = cols

        self._grid = {}
        for row in range(1, self._rows + 1):
            for col in range(1, self._cols + 1):
                key = (str)(row) + "x" + (str)(col)
                self._grid[key] = GridObj(parent, key, self._left_click, self._right_click, self._cart_end)
                self._grid[key].grid(row=row + 1, column=col - 1)

        self._enable_remove = enable_remove
        self._on_cart_start = on_cart_start
        self._on_cart_stop = on_cart_stop
        self._on_cart_end = on_cart_end
        self._on_left_click = on_left_click

    def has_cart(self, key):
        """Get whether a cell in the grid has a cart.

        :param key
        """
        return self._grid[key].has_cart()

    def set_cart(self, key, cart):
        """Add a cart to the grid.

        :param key
        :param cart
        """
        self._grid[key].set_cart(cart)

    def is_playing(self):
        """Get whether a cart is currently playing."""
        return self._active_cell is not None

    def get_active_cell(self):
        """Get the active cell."""
        return self._active_cell

    def start(self, key):
        """Start a cart.

        :param key
        """
        self._grid[key].start()
        self._active_cell = self._grid[key]
        self._on_cart_start()

    def stop(self):
        """Stop the active cart."""
        self._active_cell.stop()
        self._active_cell = None
        self._on_cart_stop()

    def clear(self):
        """Remove all carts from the grid."""
        for key in self._grid.keys():
            self._grid[key].remove_cart()

    def _left_click(self, grid_obj, key):
        """Start or stop a cart in the grid.

        :param grid_obj
        :param key
        """
        if grid_obj.has_cart():
            if grid_obj.is_playing():
                self.stop()
            elif not self.is_playing():
                self.start(key)

        if self._on_left_click is not None:
            self._on_left_click(key)

    def _right_click(self, grid_obj):
        """Remove a cart from the grid.

        :param grid_obj
        """
        if self._enable_remove and grid_obj.has_cart() and not grid_obj.is_playing():
            grid_obj.remove_cart()

    def _cart_end(self, key):
        """Stop the active grid object.

        This function is called whenever a cart ends.

        :param key
        """
        self._active_cell.stop()
        self._active_cell = None
        self._on_cart_end(key)
