#!/usr/bin/env python

import sys
import time
sys.path.insert(0, 'app')

from Tkinter import Tk, Frame, Canvas
from ZAutomate_Meter import Meter

CART_WIDTH = 200
CART_MARGIN = 10

METER_WIDTH = 1250

class Test(Frame):
    Master = None

    def __init__(self, parent):
        Frame.__init__(self)
        self.Master = parent
        self.Cols = 6

        width = (CART_WIDTH + CART_MARGIN) * self.Cols
        width = METER_WIDTH

        self.Meter = Meter(self.Master, width, self.MeterFeeder, self.EndCallback)
        #self.Meter = Canvas(self.Master, width=50, height=50, bg='#0F0')

        self.Meter.grid(row=0,column=0,columnspan=self.Cols) #, sticky=E+W

        Canvas(self.Master, width=900, height=100, bg='#00F').grid(row=2, column=0, columnspan=self.Cols)

        #self.Meter.Start()

    def EndCallback(self):
        pass

    def MeterFeeder(self):
        return (0, 0, "Fruity", "Blergs", None, None)

root = Tk()
test = Test(root)
root.title("Testing Program")
root.mainloop()
