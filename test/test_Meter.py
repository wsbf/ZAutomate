#!/usr/bin/env python

import sys
import time
sys.path.insert(0, 'app')

from Tkinter import Frame, Canvas
from ZAutomate_Config import CART_WIDTH, CART_MARGIN, Root
from ZAutomate_Meter import Meter

METER_WIDTH = 1250

class Test(Frame):
    Master = None

    def __init__(self, parent):
        Frame.__init__(self)
        self.Master = parent
        self.Cols = 6

        foo = (CART_WIDTH + CART_MARGIN) * self.Cols
        foo = METER_WIDTH

        self.Meter = Meter(self.Master, foo, self.MeterFeeder, self.EndCallback)
        #self.Meter = Canvas(self.Master, width=50, height=50, bg='#0F0')

        self.Meter.grid(row=0,column=0,columnspan=self.Cols) #, sticky=E+W

        Canvas(self.Master, width=900, height=100, bg='#00F').grid(row=2, column=0, columnspan=self.Cols)

        #self.Meter.Start()

    def EndCallback(self):
        pass

    def MeterFeeder(self):
        return (0, 0, "Fruity", "Blergs", None, None)

test = Test(Root)
Root.title("Testing Program")
Root.mainloop()
