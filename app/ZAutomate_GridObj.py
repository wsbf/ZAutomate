from Tkinter import Frame, Canvas
import ZAutomate_DBInterface as database

CART_WIDTH = 175
CART_HEIGHT = 75

COLOR_DEFAULT = "#DDDDDD"
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

COLOR_TITLE = "#FFFFFF"
COLOR_ISSUER = "#FFFFFF"
COLOR_LENGTH = "#FFFF00"

FONT = ('Helvetica', 10, 'bold')

class GridObj(Frame):
    cart = None
    rect = None
    is_playing = False

    Parent = None
    NextCoord = None

    def __init__(self, parent, nextcoord='0x0'):
        Frame.__init__(self, parent.Master, bd=1, relief='sunken', bg=COLOR_DEFAULT, width=CART_WIDTH, height=CART_HEIGHT)
        self.Parent = parent
        self.NextCoord = nextcoord

        self.rect = Canvas(self, width=CART_WIDTH, height=CART_HEIGHT, bg=COLOR_DEFAULT)

        self._title = self.rect.create_text(5, 5, width=CART_WIDTH, anchor='nw', font=FONT, fill=COLOR_TITLE, text="---")
        self._issuer = self.rect.create_text(CART_WIDTH / 2, 25, width=CART_WIDTH, anchor='n', font=FONT, fill=COLOR_ISSUER, text="---")
        self._length = self.rect.create_text(CART_WIDTH / 2, CART_HEIGHT - 15, anchor='s', font=FONT, fill=COLOR_LENGTH, text="-:--")

        # self.Frame['bg'] = COLOR_READY

        self.rect.bind('<ButtonPress-1>', self.LeftClick)
        self.rect.bind('<Button-2>', self.RightClick)
        self.rect.bind('<Button-3>', self.RightClick)
        self.rect.pack()

    def set_cart(self, cart):
        self.cart = cart

        foo = self.cart.MeterFeeder()
        self.rect.itemconfigure(self._title, text=self.cart.title)
        self.rect.itemconfigure(self._issuer, text=(self.cart.issuer + " " + self.cart.cart_id))
        self.rect.itemconfigure(self._length, text=self.Parent.Meter.SecsFormat(foo[1]/1000))
        self.rect['bg'] = COLOR_TYPES_NEW[self.cart.cart_type]

    def remove_cart(self):
        self.cart = None
        self.rect.itemconfigure(self._title, text='')
        self.rect.itemconfigure(self._issuer, text='---')
        self.rect.itemconfigure(self._length, text='-:--')
        self.rect['bg'] = COLOR_DEFAULT

    def has_cart(self):
        return self.cart is not None

    def Reset(self):
        self.Parent.Meter.Reset()

        self.rect['bg'] = COLOR_TYPES_PLAYED[self.cart.cart_type]

        self.Parent.SetActiveCart(None)
        self.Parent.SetActiveGridObj(None)

        self.is_playing = False

    def OnComplete(self):
        self.Reset()
        if self.NextCoord is not None and self.Parent.Grid[self.NextCoord].has_cart():
            self.Parent.Grid[self.NextCoord].LeftClick(None)

    def LeftClick(self, clickEvent):
        ### click on a non-empty cart
        if self.cart is not None:

            ### this cart is playing; stop and don't continue
            if self.is_playing:
                self.cart.stop()
                if self.Parent.RewindOnPause:
                    self.cart.SeekToFront()
                self.Reset()

            ### this cart isn't playing, and neither is any other; start!
            elif self.Parent.IsCartActive() is False:
                self.is_playing = True

                self.Parent.SetActiveCart(self.cart)
                self.Parent.SetActiveGridObj(self)

                self.Parent.Meter.Start()
                self.cart.start(self.Reset) ##self.OnComplete
                self.rect['bg'] = COLOR_PLAYING
                database.log_cart(self.cart.cart_id)
            pass
        ### click on an empty cart; add the clipboarded cart
        # TODO: move to DJ Studio
        else:
            try:
                self.set_cart(self.Parent.SelectedCart)
            except AttributeError:
                pass

        # TODO: move to DJ Studio
        try:
            self.Parent.Entry.focus_set()
        except AttributeError:
            pass

    def RightClick(self, clickEvent):
        if self.Parent.AllowRightClick and self.has_cart() and self.is_playing is False:
            self.remove_cart()

            # TODO: move to DJ Studio
            try:
                self.Parent.Entry.focus_set()
            except AttributeError:
                pass
