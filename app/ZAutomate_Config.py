from Tkinter import Tk

LIBRARY_PREFIX = "/media/ZAL/"

### define which sound backend to use
### current options: "madao", "vlc" -- "snack" used to work
PLAYER_CLASS = "madao"

## how big do you want the cart machine?
CARTS_ROWS = 8
CARTS_COLS = 6

CART_WIDTH = 200
CART_MARGIN = 10
CART_HEIGHT = 75

### all modules use this
Root = Tk()
