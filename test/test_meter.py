#!/usr/bin/env python

"""Test suite for the meter module."""
import sys
import time
import thread
from Tkinter import Frame, Canvas

sys.path.insert(0, 'app')
from meter import Meter

NUM_COLS = 6
CART_WIDTH = 200
CART_MARGIN = 10

METER_WIDTH = 1000

class Test(Frame):
    _meter = None
    _position = 0
    _length = 10000
    _step = 500

    def __init__(self):
        Frame.__init__(self)

        # width = (CART_WIDTH + CART_MARGIN) * NUM_COLS
        width = METER_WIDTH

        self._meter = Meter(self.master, width, self._get_meter_data)
        self._meter.grid(row=0, column=0, columnspan=NUM_COLS) #, sticky=E+W

        Canvas(self.master, width=900, height=100, bg='#00F').grid(row=2, column=0, columnspan=NUM_COLS)

        self._meter.start()
        thread.start_new_thread(self._run, ())

        self.master.title("Testing Program")
        self.master.mainloop()

    def _run(self):
        while True:
            self._position = (self._position + self._step) % self._length
            time.sleep(self._step / 1000.)

    def _get_meter_data(self):
        return (self._position, self._length, "Fruity", "Blergs")

Test()
