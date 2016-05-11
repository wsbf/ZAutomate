#!/usr/bin/env python

"""The CartMachine module provides a GUI for playing carts."""
import random
import Tkinter
from Tkinter import Frame, Label, Button
import ZAutomate_DBInterface as database
from ZAutomate_Gridder import Gridder
from ZAutomate_GridObj import GridObj
from ZAutomate_Meter import Meter

METER_WIDTH = 1000
GRID_ROWS = 8
GRID_COLS = 6

FONT_TITLE = ('Helvetica', 36, 'bold italic')
FONT_RELOAD = ('Helvetica', 24, 'bold')

COLOR_TITLE_BG = "#DDDDDD"
COLOR_TITLE_FG = "#000000"
COLOR_RELOAD_BG = "#FF0000"
COLOR_RELOAD_FG = "#000000"

TEXT_TITLE = "ZAutomate :: Cart Machine"
TEXT_RELOAD = "Reload"

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

        self.Gridder = Gridder(self._rows, self._cols)

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

        # configuration for each cart type
        config = {
            # PSA
            0: {
                "corner": (1, 1),
                "limit": -1,
                "shuffle": True
            },
            # Underwriting
            1: {
                "corner": (self._rows, self._cols),
                "limit": -1,
                "shuffle": False
            },
            # Station ID
            2: {
                "corner": (1, self._cols),
                "limit": 9,
                "shuffle": True
            },
            # Promotion
            3: {
                "corner": (self._rows, 1),
                "limit": -1,
                "shuffle": False
            }
        }

        # generate a progression of cells for each corner
        progs = {}
        for t in config:
            progs[t] = self.Gridder.GridCorner(config[t]["corner"])

        # get a dictonary of carts for each cart type
        carts = database.get_carts()

        # apply limiting and shuffling to each cart type
        for t in carts:
            if config[t]["shuffle"] is True:
                random.shuffle(carts[t])

            limit = config[t]["limit"]
            if limit is not -1:
                carts[t] = carts[t][0:limit]

        # total number of carts inserted
        numinserted = 0

        # number of carts to insert next
        #
        # when iterating through the cart types,
        # each cart type attempts to insert enough
        # carts to fill the next layer (1 for the corner,
        # then 3 for around the corner, then 5, and so on)
        toinsert = 1

        ## keep iterating until the grid is full
        while numinserted <= self._rows * self._cols:
            numempty = 0
            for t in carts:
                for i in range(0, toinsert):

                    # load a cart from this cart type
                    if len(carts[t]) > 0:
                        # pop the first unused coordinate from the progression
                        key = progs[t].pop(0)
                        while self._grid[key].has_cart():
                            if len(progs[t]) > 0:
                                key = progs[t].pop(0)
                            else:
                                return

                        # add the cart to the grid
                        self._grid[key].set_cart(carts[t].pop(0))
                        numinserted += 1

                        ## extra control structure because we are 2 loops in
                        if numinserted == self._rows * self._cols:
                            return
                    else:
                        numempty += 1

            if numempty is len(carts):
                return

            toinsert += 2

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
