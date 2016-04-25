from Tkinter import Frame, Canvas
from ZAutomate_Config import CART_WIDTH, CART_HEIGHT

ColorNowPlaying = "#00FF00"
ColorReady = "#009999"
##ColorCartContainer = "#FF7400"

## what about T R O

## UNDERWRITING PSA STATION PROMOTION
## T R N H M L O

ColorTypesNew = dict(UNDERWRITING="#BF5FFF", PSA="#0099A3", STATION="#FF6600",
    N='#FF1010', H='#FF4242', M='#FF6969', L='#8D0000', O='#CCC')
## can now add codes T R N H M L O
ColorTypesPlayed = dict(UNDERWRITING="#9400D3", PSA="#006A33", STATION="#8B4500",
    N='#2258D5', H='#4D7CE6', M='#6D92E6', L='#005280', O='#999' )


class GridObj(Frame):
    Cart = None
    Rec = None
    Meter = None
    Parent = None

    Playing = False
    NextCoord = None

    ## parent (ZA_Carts)
    def __init__(self, parent, nextcoord='0x0'):
        self.Parent = parent
        width = CART_WIDTH
        height = CART_HEIGHT
        self.NextCoord = nextcoord

        ## BUG :: if you have larger than 9x9 this will break!
        #Row = int(coord[0])
        #Col = int(coord[2])

## HUGE HACK TO MAKE THE LEFT MONITOR LOOK RIGHT AT WSBF
        font = ('Helvetica', 12, 'bold')
        if self.Parent.AllowRightClick:
            font = ('Helvetica', 10, 'bold')
            width -= 25

        Frame.__init__(self, self.Parent.Master, bd=1, relief='sunken', bg='red', width=width, height=height)
        self.Rec = Canvas(self, width=width, height=height)

        #self._Title = self.Rec.create_text(5, 5, width=width/2, anchor='nw', text="---")
        #self._Issuer = self.Rec.create_text(width-5, 5, width=width/2, anchor='ne', text="---")


        self._Title = self.Rec.create_text(5, 5, width=width, anchor='nw', font=font, fill='white', text="---")
        self._Issuer = self.Rec.create_text(width/2, 25, width=width, anchor='n', font=font, fill='white', text="---")

        self._Length = self.Rec.create_text(width/2, height-15, anchor='s', font=font, fill='yellow', text="-:--")

        ##self.Frame['bg'] = ColorReady

        self.Rec.bind('<ButtonPress-1>', self.LeftClick)
        self.Rec.bind('<Button-2>', self.RightClick) #right click from an MBP trackpad
        self.Rec.bind('<Button-3>', self.RightClick) #right click - normally?
        self.Rec.pack()

    def AddCart(self, cart):
        self.Cart = cart
        #print "ADDING CART "+self.Cart.cartType

        foo = self.Cart.MeterFeeder()
        self.Rec.itemconfigure(self._Title, text=self.Cart.Title )
        ## Below: Issuer used to be Type
        self.Rec.itemconfigure(self._Issuer, text=(self.Cart.Issuer + " " + self.Cart.ID) )
        self.Rec.itemconfigure(self._Length, text=self.Parent.Meter.SecsFormat(foo[1]/1000) )

        try:
            self.Rec['bg'] = ColorTypesNew[self.Cart.cartType]
        except KeyError:
            self.Rec['bg'] = '#F00'

    def RemCart(self):
        self.Cart = None
        self.Rec.itemconfigure(self._Title, text='' )
        self.Rec.itemconfigure(self._Issuer, text='---' )
        self.Rec.itemconfigure(self._Length, text='-:--' )
        self.Rec['bg'] = '#FFF'

    def HasCart(self):
        if self.Cart is None:
            return False
        else:
            return True

    def Reset(self):
        self.Parent.Meter.Reset()
        try:
            self.Rec['bg'] = ColorTypesPlayed[self.Cart.cartType]
        except KeyError:
            self.Rec['bg'] = '#00F'

        self.Parent.SetActiveCart(None)
        self.Parent.SetActiveGrid(None)

        self.Playing = False

    def OnComplete(self):
        #print "GridObj :: TRIGGERED ONCOMPLETE"

        self.Reset()
        try:
            if self.Parent.Grid[self.NextCoord].HasCart():
                self.Parent.Grid[self.NextCoord].LeftClick(None)
        except KeyError:
            #print "GridObj OnComplete KeyError"
            pass

    def LeftClick(self, clickEvent):
        #print "LEFTCLICK"

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

                # cart logging is done in Cart.Start
                #print "Leftclick begin to play"

                self.Playing = True

                self.Parent.SetActiveCart(self.Cart)
                self.Parent.SetActiveGrid(self)

                self.Parent.Meter.Start()
                self.Cart.Start(self.Reset) ##self.OnComplete
                self.Rec['bg'] = ColorNowPlaying
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
        if self.Parent.AllowRightClick:
            if self.HasCart() and self.Playing is False:
                self.RemCart()
            else:
                pass
            try:
                self.Parent.Entry.focus_set()
            except AttributeError:
                pass
