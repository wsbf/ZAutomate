from Tkinter import *


LIBRARY_PREFIX = '/media/ZAL/' 	## '/media/DATA_NEW/ZAL/'
PLATFORM_DELIMITER = '/' 		### should be \ on win32, / on *nix

### turn this to True to automatically log tracks played
AUTOLOG = True

### define which sound backend to use
### current options: "madao", "vlc" -- "snack" used to work
PLAYER_CLASS = "madao"
PLAYER_DRIVER = "alsa"


VALID_CART_TYPES = ['StationID','PSA','Underwriting']
AUTOMATION_CARTS = [('StationID', 1, 300),
                    ('StationID+PSA', 15, 300), 
					('StationID+Underwriting', 30, 300), 
					('StationID+PSA', 45, 300)
				   ]

## how big do you want the cart machine?
CARTS_ROWS = 8
CARTS_COLS = 6

##CARTMACHINE_DIMENSIONS = (1280, 960)
LIBRARY_DIMENSIONS = (1050, 788)


### these three apply only to automation
SizeX = 800
SizeY = 600
WinGeometry = (str)(SizeX)+"x"+(str)(SizeY)+"+0+0" #SIZEXxSIZEY+XOFFSET+YOFFSET

### Automation will add to its playlist when there are this many or fewer tracks to go
PlistGenThreshold = 10
### How many prior carts to keep in the queue
PlistHistThreshold = 3

URL_CartLoad = 'http://stream.wsbf.net/wizbif/zautomate_2.0/cartmachine_load.php'
URL_Log = 'http://stream.wsbf.net/wizbif/zautomate_2.0/zautomate_log.php'
URL_AutoLoad = 'http://stream.wsbf.net/wizbif/zautomate_2.0/automation_generate_showplist.php'
URL_AutoStart = 'http://stream.wsbf.net/wizbif/zautomate_2.0/automation_generate_showid.php'
URL_AutoCart = 'http://stream.wsbf.net/wizbif/zautomate_2.0/automation_add_carts.php'
URL_StudioSearch = 'http://stream.wsbf.net/wizbif/zautomate_2.0/studio_search.php' ##query


File_AutoConf = 'sid.conf'

### all modules use this
Root = Tk()


CART_WIDTH = 200
CART_MARGIN = 10
CART_HEIGHT = 75

METER_INTERVAL = .25
METER_WIDTH = 1250






