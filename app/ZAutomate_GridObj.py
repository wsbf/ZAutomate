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
    _parent = None
    _enable_remove = False
    _next_key = None

    _rect = None
    _title = None
    _issuer = None
    _length = None

    _cart = None
    _is_playing = False

    def __init__(self, parent, enable_remove, next_key=None):
        Frame.__init__(self, parent.master, bd=1, relief='sunken', bg=COLOR_DEFAULT, width=CART_WIDTH, height=CART_HEIGHT)
        self._parent = parent
        self._enable_remove = enable_remove
        self._next_key = next_key

        self._rect = Canvas(self, width=CART_WIDTH, height=CART_HEIGHT, bg=COLOR_DEFAULT)

        self._title = self._rect.create_text(5, 5, width=CART_WIDTH, anchor='nw', font=FONT, fill=COLOR_TITLE, text="---")
        self._issuer = self._rect.create_text(CART_WIDTH / 2, 25, width=CART_WIDTH, anchor='n', font=FONT, fill=COLOR_ISSUER, text="---")
        self._length = self._rect.create_text(CART_WIDTH / 2, CART_HEIGHT - 15, anchor='s', font=FONT, fill=COLOR_LENGTH, text="-:--")

        self._rect.bind('<ButtonPress-1>', self.LeftClick)
        self._rect.bind('<Button-2>', self.RightClick)
        self._rect.bind('<Button-3>', self.RightClick)
        self._rect.pack()

    def set_cart(self, cart):
        self._cart = cart

        seconds = self._cart._get_meter_data()[1] / 1000

        self._rect.itemconfigure(self._title, text=self._cart.title)
        self._rect.itemconfigure(self._issuer, text=(self._cart.issuer + " " + self._cart.cart_id))
        self._rect.itemconfigure(self._length, text=self._parent._meter._get_fmt_time(seconds))
        self._rect['bg'] = COLOR_TYPES_NEW[self._cart.cart_type]

    def remove_cart(self):
        self._cart = None
        self._rect.itemconfigure(self._title, text='')
        self._rect.itemconfigure(self._issuer, text='---')
        self._rect.itemconfigure(self._length, text='-:--')
        self._rect['bg'] = COLOR_DEFAULT

    def has_cart(self):
        return self._cart is not None

    def Reset(self):
        self._parent._meter.reset()

        self._rect['bg'] = COLOR_TYPES_PLAYED[self._cart.cart_type]

        self._parent.set_active_cart(None)
        self._parent.set_active_grid_obj(None)

        self._is_playing = False

    def OnComplete(self):
        self.Reset()
        if self._next_key is not None and self._parent.Grid[self._next_key].has_cart():
            self._parent.Grid[self._next_key].LeftClick(None)

    def LeftClick(self, clickEvent):
        ### click on a non-empty cart
        if self._cart is not None:

            ### this cart is playing; stop and don't continue
            if self._is_playing:
                self._cart.stop()
                self.Reset()

            ### this cart isn't playing, and neither is any other; start!
            elif not self._parent.is_cart_active():
                self._is_playing = True

                self._parent.set_active_cart(self._cart)
                self._parent.set_active_grid_obj(self)

                self._parent._meter.start()
                self._cart.start(self.Reset) ##self.OnComplete
                self._rect['bg'] = COLOR_PLAYING
                database.log_cart(self._cart.cart_id)

        ### click on an empty cart; add the clipboarded cart
        # TODO: move to DJ Studio
        else:
            try:
                self.set_cart(self._parent._selected_cart)
            except AttributeError:
                pass

        # TODO: move to DJ Studio
        try:
            self._parent._entry.focus_set()
        except AttributeError:
            pass

    def RightClick(self, clickEvent):
        if self._enable_remove and self.has_cart() and not self._is_playing:
            self.remove_cart()

            # TODO: move to DJ Studio
            try:
                self._parent._entry.focus_set()
            except AttributeError:
                pass
