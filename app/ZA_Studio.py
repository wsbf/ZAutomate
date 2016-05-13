#!/usr/bin/env python

"""The Studio module provides a GUI for the digital library."""
import thread
import Tkinter
from Tkinter import Frame, Label, BooleanVar, Checkbutton, Entry, Button
import ZAutomate_DBInterface as database
from ZAutomate_DualBox import DualBox
from ZAutomate_GridObj import GridObj
from ZAutomate_Meter import Meter

METER_WIDTH = 1000
GRID_ROWS = 5
GRID_COLS = 6

FONT_TITLE = ("Helvetica", 36, "bold italic")
FONT = ("Helvetica", 14, "bold")

TEXT_TITLE = "ZAutomate :: DJ Studio"
TEXT_AUTOSLOT = "Auto-queue tracks"
TEXT_SEARCHBOX = "Search Box"
TEXT_SEARCH = "Search"

class Studio(Frame):
    """The Studio class is a GUI for the digital library."""
    _meter = None

    _rows = GRID_ROWS
    _cols = GRID_COLS
    _grid = None
    _active_grid_obj = None

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
        for row in range(2, self._rows + 2):
            for col in range(0, self._cols):
                top.rowconfigure(row, weight=1)
                top.columnconfigure(col, weight=1)
                self.rowconfigure(row, weight=1)
                self.columnconfigure(col, weight=1)

        # initialize the title
        title = Label(self.master, fg='#000', font=FONT_TITLE, text=TEXT_TITLE)
        title.grid(row=0, column=0, columnspan=self._cols)

        # initialize the meter
        self._meter = Meter(self.master, METER_WIDTH, self._get_meter_data)
        self._meter.grid(row=1, column=0, columnspan=self._cols)

        # initialize the cart grid
        self._grid = {}

        for row in range(1, self._rows + 1):
            for col in range(1, self._cols + 1):
                key = (str)(row) + "x" + (str)(col)

                next_row = row
                next_col = col

                # each cell cues the cell below,
                # bottom cells cue the top cell in the next column,
                # the bottom right cell cues the top left cell
                if next_row is self._rows:
                    if next_col is self._cols:
                        next_row = 1
                        next_col = 1
                    else:
                        next_row = 1
                        next_col += 1
                else:
                    next_row += 1

                next_key = (str)(next_row) + "x" + (str)(next_col)

                self._grid[key] = GridObj(self, self._end_callback, True, next_key)
                self._grid[key].grid(row=row + 1, column=col - 1)

        # initialize the dual box
        self._dual_box = DualBox(self)
        self._dual_box.grid(row=self._rows + 2, column=0, columnspan=4)

        # intialize the auto-queue control
        self._auto_queue = BooleanVar()
        self._auto_queue.set(False)

        control = Frame(self.master, bd=2, relief=Tkinter.SUNKEN)

        Checkbutton(control, text=TEXT_AUTOSLOT, variable=self._auto_queue, onvalue=True, offvalue=False).pack(anchor=Tkinter.NW)
        control.grid(row=self._rows + 2, column=4, columnspan=self._cols - 4)

        # initialize the search box, button
        Label(control, font=FONT, fg='#000', text=TEXT_SEARCHBOX).pack(anchor=Tkinter.NW)
        self._entry = Entry(control, takefocus=True, width=45, bg='#000', fg='#33CCCC')
        self._entry.bind('<Return>', self.search)
        # self._entry.grid(row=self._rows + 3, column=0, columnspan=5)
        self._entry.pack(anchor=Tkinter.NW)
        self._entry.focus_set()

        button = Button(control, text=TEXT_SEARCH, command=self.search)
        # button.grid(row=self._rows + 3, column=5)
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

    def is_playing(self):
        """Get whether a cart is currently playing."""
        return self._active_grid_obj is not None

    def set_active_grid_obj(self, grid_obj):
        """Set the active grid object.

        :param grid_obj
        """
        self._active_grid_obj = grid_obj

    def _get_meter_data(self):
        """Get meter data for the current cart."""
        if self._active_grid_obj is not None:
            return self._active_grid_obj.get_cart().get_meter_data()
        else:
            return None

    def _end_callback(self):
        """Reset the active grid object.

        This function is called whenever a cart finishes.
        """
        self._active_grid_obj.reset(self._auto_queue.get())

Studio()
