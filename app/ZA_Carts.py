#!/usr/bin/env python

from ZAutomate_Config import *
from ZAutomate_GridObj import *
from ZAutomate_Meter import *
from ZAutomate_DBInterface import *

from ZAutomate_Gridder import *
import time, random
    ## ROW COL maxROW maxCOL

###    TO DO
###        hourly reload - add to tkinter event loop? (call Carts.Reload)
###
### KNOWN BUGS
###        the end of the meter bar is misaligned (fixed with a kludge)
###        dual playback bug (esp. with madao) is fixed in GridObj.LeftClick
###        one cart stop, then restart: meter is not reset correctly
###        underwriting restricted to rightmost column


class Carts(Frame):
    ###Master Window Variable
    Master = None
    ###Title at top, contains Application title and Reload Button
    Title = None
    ###Meter for counting down time left
    Meter = None

    ###Grid which holds the cart.
    Grid = None
    ###ActiveCart which is playing
    ActiveCart = None
    ###YATES_COMMENT: Not sure what this one is yet
    ActiveGrid = None
    ###Look to ensure we don't remove carts from the grid.  Included because
    ###The gridder/gridObject classes are also used in the DJ Studio
    AllowRightClick = False
    RewindOnPause = True

    ###Array which holds all the carts
    Carts = None

    def __init__(self): #width, height,
        Frame.__init__(self)
        self.Grid = {}

        ###Initialize Rows and Cols from ZAutomate_Config
        self.Rows = CARTS_ROWS  ##8
        self.Cols = CARTS_COLS  ##6
        ###Instantiate new Gridder object
        self.Gridder = Gridder(self.Rows, self.Cols)

        ###YATES_COMMENT: Great comment, Zach.
        ## make the whole shebang resizable
        top=self.winfo_toplevel()
        for row in range(2, self.Rows+2):
            for col in range(0, self.Cols):
                top.rowconfigure(row, weight=1)
                top.columnconfigure(col, weight=1)
                self.rowconfigure(row, weight=1)
                self.columnconfigure(col, weight=1)

        ###Instantiate new Title Label.
        self.Title = Label(self.Master, fg='#000', \
                font=('Helvetica', 36, 'bold italic'), \
                text='ZAutomate :: Cart Machine')

        ###YATES_COMMENT: Puts the title in the grid[0][0].
        ###               Makes the Title span across
        ###               Not sure what sticky=n does.
        self.Title.grid(row=0,column=0,columnspan=self.Cols-1, sticky=N)

        ###YATES_COMMENT: Reload Button.  Command calls Carts::Reload()
        self.B_Reload = Button(self.Master, text='Reload', bg='red', \
                        font=('Helvetica', 24, 'bold'), command=self.Reload)
        ###YATES_COMMENT: Places the reload button in grid[0][Cols-1], or rather
        ###               grid[0][5]
        self.B_Reload.grid(row=0, column=self.Cols-1)

        ###YATES_COMMENT: Instantiate the meter class for the cartMachine.
        ###               Param1 binds to Master window.
        ###               Param2 determines how long the meter will be.
        ###               NOTA BENE: By using the METER_WIDTH variable defined
        ###                 in ZAutomate_config.py, if we resize the Window, it
        ###                 will not accurately tick through the meter.
        ###               Param3 is the callback to function to get the percent
        ###               completion of a track for redrawing the meter
        ###               Param4 is the callback for when the meter hits the end
        self.Meter = Meter(self.Master, METER_WIDTH, self.MeterFeeder, \
                     self.EndCallback)
        ###YATES_COMMENT: Stick the meter in grid[1][0], row 1, column 0, make
        ###               it span across all the columns
        self.Meter.grid(row=1,column=0,columnspan=self.Cols) #, sticky=E+W
        ##self.Meter.grid_propagate(0)

        ###YATES_COMMENT: Call reload to fill the cart machine.
        self.Reload(firstRun=True)

    def FillTheGrid(self):
        print "Carts :: FillTheGrid :: Entered Function"
        ###YATES_COMMENT: These should probably be member variables, but they're
        ###               Only used here.
        # limits and shuffle flags for each cart type
        config = {
            0: { "limits": -1, "shuffle": True },   # PSA
            1: { "limits": -1, "shuffle": False },  # Underwriting
            2: { "limits": 9, "shuffle": True },    # Station ID
            3: { "limits": -1, "shuffle": False }   # Promotion
        }

        ## the starting corner coordinates as tuples
        corners = [ (self.Rows, self.Cols), \
                    (1, self.Cols), \
                    (self.Rows, 1), \
                    (1, 1) ]

        ## progressions to follow for each corner
        progs = []
        for corner in corners:
            progs.append( self.Gridder.GridCorner(corner) )

        # get a dictonary of carts for each cart type
        DBI = DBInterface()
        carts = DBI.CartMachine_Load()

        for t in carts:
            if config[t]["shuffle"] is True:
                random.shuffle(carts[t])

            limit = config[t]["limits"]
            if limit is not -1:
                carts[t] = carts[t][0:limit]

        ###YATES_COMMENT: Used to keep track of number of carts inserted.
        ###               numinserted should not exceed ROWS * COLS
        numinserted = 0

        ###YATES_COMMENT: No idea what's going on here.
        ## lets us keep track of the iterations.
        ## insert 1 of each, then 3 of each...
        toinsert = 1

        ## keep iterating until the grid is full
        while numinserted <= self.Rows * self.Cols:
            for t in carts:

                ## insert N carts of each type... 1, 3, 5, 7, 9...
                inserted = 0
                while inserted < toinsert:

                    ## load a cart from this cart type
                    if len(carts[t]) > 0:
                        ## pop off coordinates until we find one that's unused
                        key = progs[t][0]
                        while self.Grid[key].HasCart():
                            progs[t].pop(0)
                            if len(progs[t]) > 0:
                                key = progs[t][0]
                            else:
                                ## all possible positions filled - the whole grid is filled
                                return

                        ## Actually fill a cart
                        self.Grid[key].AddCart(carts[t][0])
                        carts[t].pop(0)
                        progs[t].pop(0)

                        numinserted += 1
                        inserted += 1

                        ## extra control structure because we are 2 loops in
                        if numinserted == self.Rows * self.Cols:
                            #print "ENDING - grid full"
                            return

                        ###print (str)(ctr) + " | " + (str)(inserted) + " | " + (str)(toinsert)

                    ## no more carts for this category... check the rest. if they're all empty, you're done.
                    else:
                        #print types[ctr] + " is empty..."
                        numempty = 0
                        for t in carts:
                            if len(carts[t]) is 0:
                                numempty += 1
                        if numempty == len(carts):
                            return
                        #print "Ran out of carts of type "+types[ctr]
                        ## drop to the next category since this one's empty
                        break
###                print "FillTheGrid :: inserted "+(str)(inserted)+" of type "+types[ctr]

            toinsert += 2
        print "Carts :: FillTheGrid :: Exiting Function"

    def BlankTheGrid(self):
        ###YATES_COMMENT: BlankTheGrid function removes all existing carts from
        ###               the Grid.
        print "Carts :: BlankTheGrid :: Entered Function"
        for row in range(1, self.Rows+1):
            for col in range(1, self.Cols+1):
                key = (str)(row)+"x"+(str)(col)
                try:
                    self.Grid[key].grid_forget()
                    self.Grid[key].destroy()
                    del self.Grid[key]
                except KeyError:
                    print "Carts :: BlankTheGrid :: KeyError exception thrown"\
                          + " for key " + (str)(key)
        self.initializeGrid()
        print "Carts :: BlankTheGrid :: Exiting Function"

    ###==================================

    def initializeGrid(self):
        print "Carts :: InitializeGrid :: Entered Function"
        for row in range(1, self.Rows+1):
            for col in range(1, self.Cols+1):
                key = (str)(row) + "x" + (str)(col)
                self.Grid[key] = GridObj(self)
                self.Grid[key].grid(row = row + 1, column = col - 1)
        print "Carts :: InitializeGrid :: Entered Function"

    def Reload(self, firstRun=False):
        if self.ActiveCart is not None:
            return
        print "Carts :: Reload :: Entering Reload Function"
        if firstRun is False:
            self.BlankTheGrid()
        else:
            self.initializeGrid()
        self.FillTheGrid()
        print "Carts :: Reload :: Exiting Function"

    def EndCallback(self):
        #print "Ended playback"
        self.ActiveCart.Stop()
        self.ActiveGrid.Reset()

    def SetActiveGrid(self, grid):
        self.ActiveGrid = grid

    def SetActiveCart(self, cart):
        if cart is None:
            del cart
            self.ActiveCart = None
        else:
            self.ActiveCart = cart

    def IsCartActive(self):
        if self.ActiveCart is None:
            return False
        else:
            return True

    def MeterFeeder(self):
        if self.ActiveCart is not None:
            return self.ActiveCart.MeterFeeder()
        else:
            return ("-:--", "-:--", "--", "--", None, None)

    def Bail(self):
        self.master.destroy()


Lol = Carts()
Lol.master.protocol("WM_DELETE_WINDOW", Lol.Bail)
Lol.master.title("ZAutomate :: Cart Machine")
Lol.mainloop()
