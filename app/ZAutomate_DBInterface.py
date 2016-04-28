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

def get_new_show_id(showID):
    """Get a new show ID for queueing playlists.

    :param showID: previous show ID, which will be excluded
    """

    try:
        res = requests.get(URL_AUTOSTART, params={"showid": showID})
        return res.json()
    except requests.exceptions.SSLError:
        print "Error: Could not fetch starting show ID."
        return -1

def restore_show_id():
    """Attempt to read the show ID that was saved to the config file."""

    if os.access(FILE_AUTOCONF, os.R_OK) is True:
        f = open(FILE_AUTOCONF, "r")
        showID = f.read()

        if showID.isdigit():
            return (int)(showID)

    return -1

def save_show_id(showID):
    """Save a show ID to the config file."""

    try:
        f = open(FILE_AUTOCONF, "w")
        f.write((str)(showID + 1))
        f.close()
    except IOError:
        print "Error: Could not save show ID to config file."

def get_cart(cartType):
    """Get a random cart of a given type."""

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
        print time.asctime() + " :=: Error: Could not fetch cart."

    return None

def get_next_playlist(showID):
    """Get the playlist from a past show.

    Currently the previous show ID is just incremented,
    which is not guaranteed to yield a valid playlist,
    so this function is usually called several times until
    enough tracks are retrieved.

    :param showID: previous show ID
    """

    # get next show ID
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

        for t in show_res["playlist"]:
            # TODO: move pathname building to Track constructor
            filename = LIBRARY_PREFIX + t["file_name"]
            trackID = t["lb_album_code"] + "-" + t["lb_track_num"]

            track = Cart(trackID, t["lb_track_name"], t["artist_name"], t["rotation"], filename)

            if track.Verify():
                show["playlist"].append(track)
            else:
                print time.asctime() + " :=: DBInterface :: Get_Next_Playlist() :: cart file \"" + filename + "\" does not exist"
    except requests.exceptions.SSLError:
        print "Error: Could not fetch playlist."

    return show

def get_carts():
    """Load a dictionary of cart arrays for each cart type."""
    carts = {
        0: [],
        1: [],
        2: [],
        3: []
    }

    try:
        for t in carts:
            res = requests.get(URL_CARTLOAD, params={"type": t})
            carts_res = res.json()

            for c in carts_res:
                # TODO: consider moving filename construction to Cart
                filename = LIBRARY_PREFIX + "carts/" + c["filename"]

                cart = Cart(c["cartID"], c["title"], c["issuer"], c["type"], filename)

                # verify that this file exists
                if cart.Verify():
                    carts[t].append(cart)

    except requests.exceptions.SSLError:
        print time.asctime() + " :=: Error: Could not fetch carts."

    return carts

def search_library(query):
    """Search the music library for tracks and carts.

    :param query: search term
    """

    results = []
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

def log_cart(cartID):
    """Log a cart or track.

    :param cartID: cart ID, or [album_code]-[track_num] for a track
    """

    if LOGGING is False:
        return

    try:
        res = requests.post(URL_LOG, params={"cartid": cartID})
        print res.text
    except requests.exceptions.SSLError:
        print time.asctime() + " :=: Caught error: Could not access cart logger."
