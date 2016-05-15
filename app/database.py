"""The database module provides a collection of functions for the server API."""
import time
import requests
from cart import Cart

LIBRARY_PREFIX = "/media/ZAL/"

URL_CARTLOAD = "https://dev.wsbf.net/api/zautomate/cartmachine_load.php"
URL_AUTOLOAD = "https://dev.wsbf.net/api/zautomate/automation_generate_showplist.php"
URL_AUTOSTART = "https://dev.wsbf.net/api/zautomate/automation_generate_showid.php"
URL_AUTOCART = "https://dev.wsbf.net/api/zautomate/automation_add_carts.php"
URL_STUDIOSEARCH = "https://dev.wsbf.net/api/zautomate/studio_search.php"
URL_LOG = "https://dev.wsbf.net/api/zautomate/zautomate_log.php"

def get_new_show_id(show_id):
    """Get a new show ID for queueing playlists.

    :param show_id: previous show ID, which will be excluded
    """
    try:
        res = requests.get(URL_AUTOSTART, params={"showid": show_id})
        return res.json()
    except requests.exceptions.ConnectionError:
        print "Error: Could not fetch starting show ID."
        return -1

def get_cart(cart_type):
    """Get a random cart of a given type.

    :param cart_type
    """

    # temporary code to transform cart_type to index
    types = {
        0: "PSA",
        1: "Underwriting",
        2: "StationID",
        3: "Promotion"
    }
    for t in types:
        if types[t] is cart_type:
            cart_type = t

    try:
        # attempt to find a valid cart
        count = 0
        while count < 5:
            # fetch a random cart
            res = requests.get(URL_AUTOCART, params={"type": cart_type})
            c = res.json()

            # return if cart type is empty
            if c is None:
                return None

            # construct cart
            filename = LIBRARY_PREFIX + "carts/" + c["filename"]
            cart = Cart(c["cartID"], c["title"], c["issuer"], c["type"], filename)

            # verify cart filename
            if cart.is_playable():
                return cart
            else:
                count += 1
    except requests.exceptions.ConnectionError:
        print time.asctime() + " :=: Error: Could not fetch cart."

    return None

def get_playlist(show_id):
    """Get the playlist from a past show.

    :param show_id: show ID
    """
    playlist = []

    try:
        res = requests.get(URL_AUTOLOAD, params={"showid": show_id})
        show_res = res.json()

        for t in show_res["playlist"]:
            # TODO: move pathname building to Track constructor
            filename = LIBRARY_PREFIX + t["file_name"]
            track_id = t["lb_album_code"] + "-" + t["lb_track_num"]

            track = Cart(track_id, t["lb_track_name"], t["artist_name"], t["rotation"], filename)

            if track.is_playable():
                playlist.append(track)
    except requests.exceptions.ConnectionError:
        print "Error: Could not fetch playlist."

    return playlist

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
                # TODO: move pathname building to Cart constructor
                filename = LIBRARY_PREFIX + "carts/" + c["filename"]

                cart = Cart(c["cartID"], c["title"], c["issuer"], c["type"], filename)

                if cart.is_playable():
                    carts[t].append(cart)

    except requests.exceptions.ConnectionError:
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
            if cart.is_playable():
                results.append(cart)

        for t in results_res["tracks"]:
            filename = LIBRARY_PREFIX + t["file_name"]
            track_id = t["album_code"] + "-" + t["track_num"]

            track = Cart(track_id, t["track_name"], t["artist_name"], t["rotation"], filename)
            if track.is_playable():
                results.append(track)
    except requests.exceptions.ConnectionError:
        print "Error: Could not fetch search results."

    return results

def log_cart(cart_id):
    """Log a cart or track.

    :param cart_id: cart ID, or [album_code]-[track_num] for a track
    """
    try:
        res = requests.post(URL_LOG, params={"cartid": cart_id})
        print res.text
    except requests.exceptions.ConnectionError:
        print time.asctime() + " :=: Caught error: Could not access cart logger."
