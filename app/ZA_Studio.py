#!/usr/bin/env python

import thread
from Tkinter import Tk, Frame, Label, BooleanVar, SUNKEN, NW, Radiobutton, Entry, Button, S
from ZAutomate_GridObj import GridObj
from ZAutomate_Meter import Meter
from ZAutomate_DBInterface import DBInterface
from ZAutomate_DualBox import DualBox

METER_WIDTH = 1000
GRID_ROWS = 5
GRID_COLS = 6

class Studio(Frame):
    Master = None
    Entry = None
    DualBox = None
    SearchCarts = None
    SelectedCart = None

    ActiveCart = None
    ActiveGrid = None
    AutoCartBool = None    ## tk BooleanVar
    AllowRightClick = True
    RewindOnPause = False

    Rows = 0
    Cols = 0
    Grid = None

    def __init__(self, parent):
        Frame.__init__(self)
        self.Master = parent
        self.Rows = GRID_ROWS
        self.Cols = GRID_COLS
        self.Grid = {}

        # make the whole shebang resizable
        top = self.Master.winfo_toplevel()
        for row in range(2, self.Rows+2):
            for col in range(0, self.Cols):
                top.rowconfigure(row, weight=1)
                top.columnconfigure(col, weight=1)
                self.rowconfigure(row, weight=1)
                self.columnconfigure(col, weight=1)


        title = Label(self.Master, fg='#000', font=('Helvetica', 36, 'bold italic'), text='ZAutomate :: DJ Studio')
        title.grid(row=0, column=0, columnspan=self.Cols)

        self.Meter = Meter(self.Master, METER_WIDTH, self.MeterFeeder, self.EndCallback)
        self.Meter.grid(row=1, column=0, columnspan=self.Cols) #, sticky=E+W


        self.DualBox = DualBox(self)
        self.DualBox.grid(row=self.Rows + 2, column=0, columnspan=4)

        ### auto cart rotation controls
        self.AutoCartBool = BooleanVar()
        self.AutoCartBool.set(True)
        control = Frame(self.Master, bd=2, relief=SUNKEN)
        Label(control, font=('Helvetica', 14, 'bold'), fg='#000', text='Auto-Slot Rotation').pack(anchor=NW)
        Radiobutton(control, text='Enabled', variable=self.AutoCartBool, value=True).pack(anchor=NW)
        rno = Radiobutton(control, text='Disabled', variable=self.AutoCartBool, value=False).pack(anchor=NW)
        control.grid(row=self.Rows+2, column=4, columnspan=self.Cols-4)


        Label(control, font=('Helvetica', 14, 'bold'), fg='#000', text='Search Box').pack(anchor=NW)
        self.Entry = Entry(control, takefocus=True, width=45, bg='#000', fg='#33CCCC')
        self.Entry.bind('<Return>', self.Search)
        ##self.Entry.grid(row=self.Rows+3,column=0,columnspan=5)
        self.Entry.pack(anchor=NW)
        self.Entry.focus_set()

        button = Button(control, text='Search', command=self.Search)
        ##button.grid(row=self.Rows+3,column=5)
        button.pack(anchor=S)

        self.GenerateGrid()

    def SetActiveGrid(self, grid):
        self.ActiveGrid = grid

    def IsCartActive(self):
        if self.ActiveCart is None:
            return False
        else:
            return True

    def SetActiveCart(self, cart):
        if cart is None:
            del cart
            self.ActiveCart = None
        else:
            self.ActiveCart = cart

    ## lovingly ripped off from ZA_Carts.BlankTheGrid
    def GenerateGrid(self):
        for row in range(1, self.Rows + 1):
            for col in range(1, self.Cols + 1):
                key = (str)(row) + "x" + (str)(col)
                try:
                    self.Grid[key].grid_forget()
                    self.Grid[key].destroy()
                    del self.Grid[key]
                except KeyError:
                    pass

                ### default condition. set the auto-rotation next grid position
                keynext = (str)(row+1)+"x"+(str)(col)
                ### bottom right cues into top left
                if row == self.Rows and col == self.Cols:
                    keynext = (str)(1)+"x"+(str)(1)
                 ### bottom of a column cues into top of the next
                elif row == self.Rows:
                    keynext = (str)(1)+"x"+(str)(col+1)


                ## GridObj is by default unpaired with a Cart
                self.Grid[key] = GridObj(self, keynext)
                self.Grid[key].grid(row=row+1, column=col-1)

    def SetClipboard(self, index):
        # weird: index comes in as a str
        if index is not None:
            ##print "Setting cart index "+index+" to the clipboard"
            self.SelectedCart = self.SearchCarts[int(index)]

    ### called by Meter when one cart is done
    def EndCallback(self):
        if self.AutoCartBool.get() == 1:
            self.ActiveCart.Stop()
            self.ActiveGrid.OnComplete()
        else:
            self.ActiveCart.Stop()
            self.ActiveGrid.Reset()

    def MeterFeeder(self):
        if self.ActiveCart is not None:
            return self.ActiveCart.MeterFeeder()
        else:
            return ("-:--", "-:--", "--", "--", None, None)

    def Search(self, event=None):
        thread.start_new_thread(self.SearchInternal, ())

    def SearchInternal(self):
        query = self.Entry.get()

        if len(query) >= 3:
            dbi = DBInterface()
            self.SearchCarts = dbi.Studio_Search(query)

            ## fill the DualBox with the search results
            arr = []
            for cart in self.SearchCarts:
                temp = cart.MeterFeeder()
                arr.append((temp[2], temp[3])) ## was 2,3    5
            self.DualBox.TupleFill(arr)

        thread.exit()

    def Bail(self):
        self.Master.destroy()

root = Tk()
studio = Studio(root)
root.protocol("WM_DELETE_WINDOW", studio.Bail)
root.title("ZAutomate :: DJ Studio")
root.mainloop()
