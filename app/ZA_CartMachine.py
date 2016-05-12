#!/usr/bin/env python

"""The CartMachine module provides a GUI for playing carts."""
import random
import Tkinter
from Tkinter import Frame, Label, Button
import ZAutomate_DBInterface as database
from ZAutomate_GridObj import GridObj
from ZAutomate_Meter import Meter

METER_WIDTH = 1000
GRID_ROWS = 8
GRID_COLS = 6

# configuration for each cart type
CONFIG_CARTS = {
    # PSA
    0: {
        "corner": (1, 1),
        "limit": -1
    },
    # Underwriting
    1: {
        "corner": (GRID_ROWS, GRID_COLS),
        "limit": -1
    },
    # Station ID
    2: {
        "corner": (1, GRID_COLS),
        "limit": 9
    },
    # Promotion
    3: {
        "corner": (GRID_ROWS, 1),
        "limit": -1
    }
}

FONT_TITLE = ('Helvetica', 36, 'bold italic')
FONT_RELOAD = ('Helvetica', 24, 'bold')

COLOR_TITLE_BG = "#DDDDDD"
COLOR_TITLE_FG = "#000000"
COLOR_RELOAD_BG = "#FF0000"
COLOR_RELOAD_FG = "#000000"

TEXT_TITLE = "ZAutomate :: Cart Machine"
TEXT_RELOAD = "Reload"

def progression_radius(ROWS, COLS, corner, radius):
    """Generate a progression of coordinates at a given radius from a corner.

    Examples:
    - radius = 0 yields the corner
    - radius = 1 yields the 3 coordinates around the corner
    - radius = 2 yields the 5 coordinates around the previous 3, etc

    :param ROWS: rows in the grid
    :param COLS: columns in the grid
    :param corner: corner coordinate as a 2-tuple (row, col)
    :param radius: number of diagonal cells from corner
    """

    # determine the directions from the corner
    if corner[0] == 1:
        dirR = 1
    elif corner[0] == ROWS:
        dirR = -1

    if corner[1] == 1:
        dirC = 1
    elif corner[1] == COLS:
        dirC = -1

    # determine the pivot from the corner and radius
    pivot = (corner[0] + dirR * radius, corner[1] + dirC * radius)

    array = []

    # append coordinates along the same row
    for col in range(corner[1], pivot[1], dirC):
        array.append((pivot[0], col))

    # append coordinates along the same column
    for row in range(corner[0], pivot[0], dirR):
        array.append((row, pivot[1]))

    # append the pivot coordinate
    array.append(pivot)

    # filter valid coordinates
    array = [elem for elem in array if 0 < elem[0] <= ROWS and 0 < elem[1] <= COLS]

    return array

def progression(ROWS, COLS, corner):
    """Generate a progression of coordinates from a corner.

    The progression begins at the corner and expands outward
    until every coordinate in the grid is included.

    :param ROWS: rows in the grid
    :param COLS: columns in the grid
    :param corner: corner coordinate as a 2-tuple (row, col)
    """

    # append each radius of the progression
    array = []

    for radius in range(0, max(ROWS, COLS)):
        array.extend(progression_radius(ROWS, COLS, corner, radius))

    # temporary code to transform tuples into strings
    array = [(str)(elem[0])+"x"+(str)(elem[1]) for elem in array]

    return array

class CartMachine(Frame):
    """The CartMachine class is a GUI that provides a grid of carts."""
    _meter = None

    _rows = GRID_ROWS
    _cols = GRID_COLS
    _grid = None
    _active_cart = None
    _active_grid_obj = None

    def __init__(self):
        """Construct a CartMachine window."""
        Frame.__init__(self)

        # make the window resizable
        top = self.winfo_toplevel()
        for row in range(2, self._rows + 2):
            for col in range(0, self._cols):
                top.rowconfigure(row, weight=1)
                top.columnconfigure(col, weight=1)
                self.rowconfigure(row, weight=1)
                self.columnconfigure(col, weight=1)

        # initialize the title
        title = Label(self.master, \
            bg=COLOR_TITLE_BG, fg=COLOR_TITLE_FG, \
            font=FONT_TITLE, text=TEXT_TITLE)
        title.grid(row=0, column=0, columnspan=self._cols - 1, sticky=Tkinter.N)

        # initialize the reload button
        reload_button = Button(self.master, \
            bg=COLOR_RELOAD_BG, fg=COLOR_RELOAD_FG, \
            font=FONT_RELOAD, text=TEXT_RELOAD, \
            command=self.reload)
        reload_button.grid(row=0, column=self._cols - 1)

        # initialize the meter
        self._meter = Meter(self.master, METER_WIDTH, self._get_meter_data, None)
        self._meter.grid(row=1, column=0, columnspan=self._cols)
        # self._meter.grid_propagate(0)

        # initialize the grid
        self._grid = {}
        for row in range(1, self._rows + 1):
            for col in range(1, self._cols + 1):
                key = (str)(row) + "x" + (str)(col)
                self._grid[key] = GridObj(self, False)
                self._grid[key].grid(row=row + 1, column=col - 1)

        self._load()

        # begin the event loop
        self.master.title(TEXT_TITLE)
        self.mainloop()

    def _load(self):
        """Load the grid with carts.

        Since there are four cart types, each type is assigned
        to a corner of the grid, and the carts in that type expand
        from that corner. Carts are added one type at a time until
        the grid is full.

        Typically, since PSAs are the most numerous cart type, they
        fill middle space not covered by the other types.
        """

        # generate a progression of cells for each corner
        progs = {}
        for cart_type in CONFIG_CARTS:
            progs[cart_type] = progression(self._rows, self._cols, CONFIG_CARTS[cart_type]["corner"])

        # get a dictonary of carts for each cart type
        carts = database.get_carts()

        # apply shuffling and limiting to each cart type
        for cart_type in carts:
            random.shuffle(carts[cart_type])

            limit = CONFIG_CARTS[cart_type]["limit"]
            if limit is not -1:
                carts[cart_type] = carts[cart_type][0:limit]

        # insert carts until the grid is full or all carts are inserted
        num_inserted = 0

        for i in range(0, max(self._rows, self._cols)):
            for cart_type in carts:
                # insert a layer for each cart type
                num_toinsert = 1 + 2 * i

                while len(carts[cart_type]) > 0 and num_toinsert > 0:
                    # pop the first empty coordinate from the progression
                    key = progs[cart_type].pop(0)
                    while self._grid[key].has_cart():
                        key = progs[cart_type].pop(0)

                    # add the cart to the grid
                    self._grid[key].set_cart(carts[cart_type].pop(0))
                    num_inserted += 1
                    num_toinsert -= 1

                    # exit if the grid is full
                    if num_inserted is self._rows * self._cols:
                        return

                # exit if all carts are inserted
                if len([key for key in carts if len(carts[key]) > 0]) is 0:
                    break

    def reload(self):
        """Reload the cart machine."""

        if self._active_cart is not None:
            return

        print "Reloading the Cart Machine..."
        for key in self._grid.keys():
            self._grid[key].remove_cart()

        self._load()
        print "Cart Machine reloaded."

    # TODO: remove active cart, use only active grid object
    def is_cart_active(self):
        """Get whether a cart is currently playing."""
        return self._active_cart is not None

    def set_active_cart(self, cart):
        """Set the active cart.

        :param cart
        """
        self._active_cart = cart

    def set_active_grid_obj(self, grid_obj):
        """Set the active grid object.

        :param grid_obj
        """
        self._active_grid_obj = grid_obj

    def _get_meter_data(self):
        """Get meter data for the current cart."""
        if self._active_cart is not None:
            return self._active_cart.get_meter_data()
        else:
            return ("-:--", "-:--", "--", "--", None, None)

    # TODO: Meter never actually calls this function
    def EndCallback(self):
        self._active_cart.stop()
        self._active_grid_obj.Reset()

CartMachine()
