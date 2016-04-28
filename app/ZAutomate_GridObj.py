from Tkinter import Frame, Canvas
import ZAutomate_DBInterface as database

CART_WIDTH = 175
CART_HEIGHT = 75

# TODO: move all colors to constants

COLOR_PLAYING = "#00FF00"
COLOR_READY = "#009999"
COLOR_TYPES_NEW = {
    "PSA": "#0099A3",
    "Underwriting": "#BF5FFF",
    "StationID": "#FF6600",
    "Promotion": "#888888",  # TODO: set Promotion color
    "R": "#888888",          # TODO: set Recently Reviewed color
    "N": "#FF1010",
    "H": "#FF4242",
    "M": "#FF6969",
    "L": "#8D0000",
    "O": "#CCC"
}
COLOR_TYPES_PLAYED = {
    "Underwriting": "#9400D3",
    "PSA": "#006A33",
    "StationID": "#8B4500",
    "Promotion": "#AAAAAA",  # TODO: set Promotion color
    "R": "#AAAAAA",          # TODO: set Recently Reviewed color
    "N": "#2258D5",
    "H": "#4D7CE6",
    "M": "#6D92E6",
    "L": "#005280",
    "O": "#999"
}

class GridObj(Frame):
    Cart = None
    Rec = None
    Meter = None
    Parent = None

    Playing = False
    NextCoord = None

    def __init__(self, parent, nextcoord='0x0'):
        self.Parent = parent
        width = CART_WIDTH
        height = CART_HEIGHT
        self.NextCoord = nextcoord

        font = ('Helvetica', 10, 'bold')

        Frame.__init__(self, self.Parent.Master, bd=1, relief='sunken', bg='red', width=width, height=height)
        self.Rec = Canvas(self, width=width, height=height)

        self._Title = self.Rec.create_text(5, 5, width=width, anchor='nw', font=font, fill='white', text="---")
        self._Issuer = self.Rec.create_text(width/2, 25, width=width, anchor='n', font=font, fill='white', text="---")

        self._Length = self.Rec.create_text(width/2, height-15, anchor='s', font=font, fill='yellow', text="-:--")

        # self.Frame['bg'] = COLOR_READY

        self.Rec.bind('<ButtonPress-1>', self.LeftClick)
        self.Rec.bind('<Button-2>', self.RightClick)
        self.Rec.bind('<Button-3>', self.RightClick)
        self.Rec.pack()

    def AddCart(self, cart):
        self.Cart = cart

        foo = self.Cart.MeterFeeder()
        self.Rec.itemconfigure(self._Title, text=self.Cart.Title)
        self.Rec.itemconfigure(self._Issuer, text=(self.Cart.Issuer + " " + self.Cart.ID))
        self.Rec.itemconfigure(self._Length, text=self.Parent.Meter.SecsFormat(foo[1]/1000))

        self.Rec['bg'] = COLOR_TYPES_NEW[self.Cart.cartType]

    def RemCart(self):
        self.Cart = None
        self.Rec.itemconfigure(self._Title, text='')
        self.Rec.itemconfigure(self._Issuer, text='---')
        self.Rec.itemconfigure(self._Length, text='-:--')
        self.Rec['bg'] = '#FFF'

    def HasCart(self):
        if self.Cart is None:
            return False
        else:
            return True

    def Reset(self):
        self.Parent.Meter.Reset()
        try:
            self.Rec['bg'] = COLOR_TYPES_PLAYED[self.Cart.cartType]
        except KeyError:
            self.Rec['bg'] = '#00F'

        self.Parent.SetActiveCart(None)
        self.Parent.SetActiveGrid(None)

        self.Playing = False

    def OnComplete(self):
        self.Reset()
        if self.NextCoord is not None and self.Parent.Grid[self.NextCoord].HasCart():
            self.Parent.Grid[self.NextCoord].LeftClick(None)

    def LeftClick(self, clickEvent):
        ### click on a non-empty cart
        if self.Cart is not None:

            ### this cart is playing; stop and don't continue
            if self.Playing:
                self.Cart.Stop()
                if self.Parent.RewindOnPause:
                    self.Cart.SeekToFront()
                self.Reset()

            ### this cart isn't playing, and neither is any other; start!
            elif self.Parent.IsCartActive() is False:
                self.Playing = True

                self.Parent.SetActiveCart(self.Cart)
                self.Parent.SetActiveGrid(self)

                self.Parent.Meter.Start()
                self.Cart.Start(self.Reset) ##self.OnComplete
                self.Rec['bg'] = COLOR_PLAYING
                database.log_cart(self.Cart.ID)
            pass
        ### click on an empty cart; add the clipboarded cart
        else:
            try:
                self.AddCart(self.Parent.SelectedCart)
            except AttributeError:
                ## this error will happen if self.Parent.SelectedCart is not defined
                ## i.e. on any click empty slot in the cart machine
                pass

        ## this is a usability kludge - give focus back to the search bar
        try:
            self.Parent.Entry.focus_set()
        except AttributeError:
            pass

    def RightClick(self, clickEvent):
        if self.Parent.AllowRightClick and self.HasCart() and self.Playing is False:
            self.RemCart()
            try:
                self.Parent.Entry.focus_set()
            except AttributeError:
                pass
