#!/usr/bin/env python

import thread
import Tkinter
from Tkinter import Frame, Label, BooleanVar, Checkbutton, Entry, Button
from ZAutomate_GridObj import GridObj
from ZAutomate_Meter import Meter
import ZAutomate_DBInterface as database
from ZAutomate_DualBox import DualBox

METER_WIDTH = 1000
GRID_ROWS = 5
GRID_COLS = 6

FONT_TITLE = ("Helvetica", 36, "bold italic")
FONT = ("Helvetica", 14, "bold")

TEXT_TITLE = "ZAutomate :: DJ Studio"
TEXT_AUTOSLOT = "Auto-queue Tracks"
TEXT_SEARCHBOX = "Search Box"
TEXT_SEARCH = "Search"

class Studio(Frame):
    _meter = None

    _rows = 0
    _cols = 0
    _grid = None
    _active_cart = None
    _active_grid_obj = None

    _dual_box = None
    _auto_cart = None
    _entry = None
    _search_results = None
    _selected_cart = None

    def __init__(self):
        Frame.__init__(self)
        self._rows = GRID_ROWS
        self._cols = GRID_COLS

        # make the whole shebang resizable
        top = self.master.winfo_toplevel()
        for row in range(2, self._rows + 2):
            for col in range(0, self._cols):
                top.rowconfigure(row, weight=1)
                top.columnconfigure(col, weight=1)
                self.rowconfigure(row, weight=1)
                self.columnconfigure(col, weight=1)

        # initialize title
        title = Label(self.master, fg='#000', font=FONT_TITLE, text=TEXT_TITLE)
        title.grid(row=0, column=0, columnspan=self._cols)

        # initialize meter
        self._meter = Meter(self.master, METER_WIDTH, self._get_meter_data, None)
        self._meter.grid(row=1, column=0, columnspan=self._cols)

        # initialize cart grid
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

                next_key = (str)(next_row) + "x" + (str)(next_col)

                self._grid[key] = GridObj(self, True, next_key)
                self._grid[key].grid(row=row + 1, column=col - 1)

        # initialize dual box
        self._dual_box = DualBox(self)
        self._dual_box.grid(row=self._rows + 2, column=0, columnspan=4)

        # intialize auto-cart control
        self._auto_cart = BooleanVar()
        self._auto_cart.set(True)

        control = Frame(self.master, bd=2, relief=Tkinter.SUNKEN)

        Checkbutton(control, text=TEXT_AUTOSLOT, variable=self._auto_cart, onvalue=True, offvalue=False).pack(anchor=Tkinter.NW)
        control.grid(row=self._rows + 2, column=4, columnspan=self._cols - 4)

        # initialize search box, button
        Label(control, font=FONT, fg='#000', text=TEXT_SEARCHBOX).pack(anchor=Tkinter.NW)
        self._entry = Entry(control, takefocus=True, width=45, bg='#000', fg='#33CCCC')
        self._entry.bind('<Return>', self.search)
        # self._entry.grid(row=self._rows + 3, column=0, columnspan=5)
        self._entry.pack(anchor=Tkinter.NW)
        self._entry.focus_set()

        button = Button(control, text=TEXT_SEARCH, command=self.search)
        # button.grid(row=self._rows + 3, column=5)
        button.pack(anchor=Tkinter.S)

    def _search_internal(self):
        query = self._entry.get()

        if len(query) >= 3:
            self._search_results = database.search_library(query)

            arr = []
            for cart in self._search_results:
                data = cart._get_meter_data()
                arr.append((data[2], data[3]))
            self._dual_box.TupleFill(arr)

        thread.exit()

    def search(self, event=None):
        thread.start_new_thread(self._search_internal, ())

    def is_cart_active(self):
        return self._active_cart is not None

    def set_active_cart(self, cart):
        self._active_cart = cart

    def set_active_grid_obj(self, grid_obj):
        self._active_grid_obj = grid_obj

    def select_cart(self, index):
        # weird: index comes in as a str
        if index is not None:
            self._selected_cart = self._search_results[int(index)]

    def _get_meter_data(self):
        if self._active_cart is not None:
            return self._active_cart._get_meter_data()
        else:
            return ("-:--", "-:--", "--", "--", None, None)

    # TODO: Meter never calls this function, so auto-slot rotation doesn't work
    def EndCallback(self):
        self._active_cart.stop()

        if self._auto_cart.get() is True:
            self._active_grid_obj.OnComplete()
        else:
            self._active_grid_obj.Reset()

studio = Studio()
studio.master.title(TEXT_TITLE)
studio.master.mainloop()
