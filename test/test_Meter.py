#!/usr/bin/env python

import sys
import time
import thread
sys.path.insert(0, 'app')

from Tkinter import Tk, Frame, Canvas
from ZAutomate_Meter import Meter

NUM_COLS = 6
CART_WIDTH = 200
CART_MARGIN = 10

METER_WIDTH = 1000

class Test(Frame):
    _meter = None
    _position = 0
    _length = 10

    def __init__(self, parent):
        Frame.__init__(self)

        width = (CART_WIDTH + CART_MARGIN) * NUM_COLS
        width = METER_WIDTH

        self._meter = Meter(parent, width, self._get_meter_data, self._end_callback)
        self._meter.grid(row=0, column=0, columnspan=NUM_COLS) #, sticky=E+W

        Canvas(parent, width=900, height=100, bg='#00F').grid(row=2, column=0, columnspan=NUM_COLS)

        self._meter.start()
        thread.start_new_thread(self._run, ())

    def _run(self):
        while True:
            self._position = (self._position + 1) % self._length
            time.sleep(1.0)

    def _get_meter_data(self):
        return (self._position, self._length, "Fruity", "Blergs", None, None)

    def _end_callback(self):
        print "Meter finished."

root = Tk()
test = Test(root)
root.title("Testing Program")
root.mainloop()
