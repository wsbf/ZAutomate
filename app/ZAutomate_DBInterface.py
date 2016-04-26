import os
import time
import requests
from ZAutomate_Cart import Cart

LIBRARY_PREFIX = "/media/ZAL/"

### URLs for the web interface
URL_CARTLOAD = "https://dev.wsbf.net/api/zautomate/cartmachine_load.php"
URL_AUTOLOAD = "https://dev.wsbf.net/api/zautomate/automation_generate_showplist.php"
URL_AUTOSTART = "https://dev.wsbf.net/api/zautomate/automation_generate_showid.php"
URL_AUTOCART = "https://dev.wsbf.net/api/zautomate/automation_add_carts.php"
URL_STUDIOSEARCH = "https://dev.wsbf.net/api/zautomate/studio_search.php"
URL_LOG = "https://dev.wsbf.net/api/zautomate/zautomate_log.php"

### sid.conf stores the previous/current showID
FILE_AUTOCONF = "sid.conf"

### enable logging
LOGGING = True

def timeStamp():
    return time.asctime(time.localtime(time.time()))

### try to pull the show id we last used from the config file.
def ShowID_Restore():
    if os.access(FILE_AUTOCONF, os.R_OK) is True:
        f = open(FILE_AUTOCONF, "r")
        showID = f.read();

        if showID.isdigit():
            return (int)(showID)

    return ShowID_GetNewID(-1)

### get a random show ID from the recent past
def ShowID_GetNewID(showID):
    try:
        res = requests.get(URL_AUTOSTART, params={"showid": showID})
        return res.json()
    except requests.exceptions.SSLError:
        print "Error: Could not fetch starting show ID."
        return -1

def ShowID_Save(showID):
    f = open(FILE_AUTOCONF, "w")
    f.write((str)(showID + 1))
    f.close()

### return a Cart object based on its type
def Cart_Request(cartType):
    # temporary code to transform cartType to index
    types = {
        0: "PSA",
        1: "Underwriting",
        2: "StationID"
    }
    for t in types:
        if types[t] is cartType:
            cartType = t

    try:
        # attempt to find a valid cart
        count = 0
        while count < 5:
            # fetch a random cart
            res = requests.get(URL_AUTOCART, params={"type": cartType})
            c = res.json()

            # return if cart type is empty
            if c is None:
                return None

            # construct cart
            filename = LIBRARY_PREFIX + "carts/" + c["filename"]
            cart = Cart(c["cartID"], c["title"], c["issuer"], c["type"], filename)

            # verify cart filename
            if cart.Verify():
                return cart
            else:
                count += 1
    except requests.exceptions.SSLError:
        print timeStamp() + " :=: Error: Could not fetch cart."

    return None

def Get_Next_Playlist(showID):
    # get next show ID
    if showID is -1:
        print timeStamp() + " :=: DBInterface :: Get_Next_Playlist() :: calling ShowID_GetNewID()"
        showID = ShowID_GetNewID()
    else:
        showID += 1

    # get next playlist
    show = {
        "showID": -1,
        "playlist": []
    }
    try:
        res = requests.get(URL_AUTOLOAD, params={"showid": showID})
        show_res = res.json()

        show["showID"] = show_res["showID"]

        print "DBInterface :: Get_Next_Playlist() :: Enqueueing new showID " + (str)(show["showID"])

        for t in show_res["playlist"]:
            # TODO: move pathname building to Track constructor
            filename = LIBRARY_PREFIX + t["file_name"]
            trackID = t["lb_album_code"] + "-" + t["lb_track_num"]

            track = Cart(trackID, t["lb_track_name"], t["artist_name"], t["rotation"], filename)

            if track.Verify():
                show["playlist"].append(track)
            else:
                print timeStamp() + " :=: DBInterface :: Get_Next_Playlist() :: cart file \"" + filename + "\" does not exist"
    except requests.exceptions.SSLError:
        print "Error: Could not fetch playlist."

    return show

### load a dictionary of cart types to cart arrays
def CartMachine_Load():
    types = [0, 1, 2, 3]
    carts = {}

    try:
        for t in types:
            res = requests.get(URL_CARTLOAD, params={"type": t})
            carts_res = res.json()

            carts[t] = []

            for c in carts_res:
                # TODO: consider moving filename construction to Cart
                filename = LIBRARY_PREFIX + "carts/" + c["filename"]

                cart = Cart(c["cartID"], c["title"], c["issuer"], c["type"], filename)

                # verify that this file exists
                if cart.Verify():
                    carts[t].append(cart)

    except requests.exceptions.SSLError:
        print timeStamp() + " :=: Error: Could not fetch carts."

    return carts

def Studio_Search(query):
    results = [];
    try:
        res = requests.get(URL_STUDIOSEARCH, params={"query": query})
        results_res = res.json()

        for c in results_res["carts"]:
            filename = LIBRARY_PREFIX + "carts/" + c["filename"]

            cart = Cart(c["cartID"], c["title"], c["issuer"], c["type"], filename)
            if cart.Verify():
                results.append(cart)

        for t in results_res["tracks"]:
            filename = LIBRARY_PREFIX + t["file_name"]
            trackID = t["album_code"] + "-" + t["track_num"]

            track = Cart(trackID, t["track_name"], t["artist_name"], t["rotation"], filename)
            if track.Verify():
                results.append(track)
    except requests.exceptions.SSLError:
        print "Error: Could not fetch search results."

    return results

def Logbook_Log(cartID):
    if LOGGING is False:
        return

    ## id will be libcart primary key for non-song; for libtrack, it will be H199-4 (for example)
    try:
        res = requests.post(URL_LOG, params={"cartid": cartID})
        print res.text
    except:
        print timeStamp() + " :=: Caught error: Could not access cart logger."
