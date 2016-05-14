#!/usr/bin/env python

"""The Studio module provides a GUI for the digital library."""
import thread
import Tkinter
from Tkinter import Frame, Label, BooleanVar, Checkbutton, Entry, Button
import database
from dualbox import DualBox
from cartgrid import Grid
from meter import Meter

METER_WIDTH = 1000
GRID_ROWS = 5
GRID_COLS = 6

FONT_TITLE = ("Helvetica", 36, "bold italic")
FONT = ("Helvetica", 14, "bold")

TEXT_TITLE = "ZAutomate :: DJ Studio"
TEXT_AUTOSLOT = "Auto-queue tracks"
TEXT_SEARCHBOX = "Search Box"
TEXT_SEARCH = "Search"

def get_next_key(rows, cols, key):
    """Get the next cell to queue after a cell.

    - each cell queues the cell below
    - bottom cells queue the top cell in the next column
    - the bottom right cell queues the top left cell

    :param rows
    :param cols
    :param key
    """
    next_row = (int)(key[0])
    next_col = (int)(key[2])

    if next_row is rows:
        if next_col is cols:
            next_row = 1
            next_col = 1
        else:
            next_row = 1
            next_col += 1
    else:
        next_row += 1

    return (str)(next_row) + "x" + (str)(next_col)

class Studio(Frame):
    """The Studio class is a GUI for the digital library."""
    _meter = None
    _grid = None
    _dual_box = None
    _auto_queue = None
    _entry = None
    _search_results = None
    _selected_cart = None

    def __init__(self):
        """Construct a Studio window."""
        Frame.__init__(self)

        # make the window resizable
        top = self.master.winfo_toplevel()
        for row in range(2, GRID_ROWS + 2):
            for col in range(0, GRID_COLS):
                top.rowconfigure(row, weight=1)
                top.columnconfigure(col, weight=1)
                self.rowconfigure(row, weight=1)
                self.columnconfigure(col, weight=1)

        # initialize the title
        title = Label(self.master, fg='#000', font=FONT_TITLE, text=TEXT_TITLE)
        title.grid(row=0, column=0, columnspan=GRID_COLS)

        # initialize the meter
        self._meter = Meter(self.master, METER_WIDTH, self._get_meter_data)
        self._meter.grid(row=1, column=0, columnspan=GRID_COLS)

        # initialize the cart grid
        self._grid = Grid(self, GRID_ROWS, GRID_COLS, True, self._cart_start, self._cart_stop, self._cart_end, self.add_cart)

        # initialize the dual box
        self._dual_box = DualBox(self)
        self._dual_box.grid(row=GRID_ROWS + 2, column=0, columnspan=4)

        # intialize the auto-queue control
        self._auto_queue = BooleanVar()
        self._auto_queue.set(False)

        control = Frame(self.master, bd=2, relief=Tkinter.SUNKEN)

        Checkbutton(control, text=TEXT_AUTOSLOT, variable=self._auto_queue, onvalue=True, offvalue=False).pack(anchor=Tkinter.NW)
        control.grid(row=GRID_ROWS + 2, column=4, columnspan=GRID_COLS - 4)

        # initialize the search box, button
        Label(control, font=FONT, fg='#000', text=TEXT_SEARCHBOX).pack(anchor=Tkinter.NW)
        self._entry = Entry(control, takefocus=True, width=45, bg='#000', fg='#33CCCC')
        self._entry.bind('<Return>', self.search)
        # self._entry.grid(row=GRID_ROWS + 3, column=0, columnspan=5)
        self._entry.pack(anchor=Tkinter.NW)
        self._entry.focus_set()

        button = Button(control, text=TEXT_SEARCH, command=self.search)
        # button.grid(row=GRID_ROWS + 3, column=5)
        button.pack(anchor=Tkinter.S)

        # begin the event loop
        self.master.protocol("WM_DELETE_WINDOW", self.master.destroy)
        self.master.title(TEXT_TITLE)
        self.master.mainloop()

    def _search_internal(self):
        """Search the digital library in a separate thread."""
        query = self._entry.get()

        if len(query) >= 3:
            print "Searching library with query \"%s\"..." % query

            self._search_results = database.search_library(query)
            self._dual_box.fill(self._search_results)

            print "Found %d results." % len(self._search_results)

    def search(self, *args):
        """Search the digital library.

        :param args
        """
        thread.start_new_thread(self._search_internal, ())

    def select_cart(self, index):
        """Select a cart from the search results.

        :param index: index of cart in search results
        """
        if index is not None:
            self._selected_cart = self._search_results[index]

    def add_cart(self, key):
        """Add the selected cart to the grid.

        :param key
        """
        if not self._grid.has_cart(key) and self._selected_cart is not None:
            self._grid.set_cart(key, self._selected_cart)

    def _cart_start(self):
        """Start the meter when a cart starts."""
        self._meter.start()

    def _cart_stop(self):
        """Reset the meter when a cart stops."""
        self._meter.reset()

    def _cart_end(self, key):
        """Reset the meter when a cart ends.

        Also, if auto-queue is enabled, queue the next cart.

        :param key
        """
        self._meter.reset()

        if self._auto_queue.get():
            next_key = get_next_key(GRID_ROWS, GRID_COLS, key)
            if self._grid.has_cart(next_key):
                self._grid.start(next_key)

    def _get_meter_data(self):
        """Get meter data for the currently active cart."""
        return self._grid.get_active_cell().get_cart().get_meter_data()

Studio()
