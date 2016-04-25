import os
import time
import requests
from ZAutomate_Config import LIBRARY_PREFIX
from ZAutomate_Cart import Cart

### URLs for the web interface
URL_CARTLOAD = "https://dev.wsbf.net/api/zautomate/cartmachine_load.php"
URL_AUTOLOAD = "https://dev.wsbf.net/api/zautomate/automation_generate_showplist.php"
URL_AUTOSTART = "https://dev.wsbf.net/api/zautomate/automation_generate_showid.php"
URL_AUTOCART = "https://dev.wsbf.net/api/zautomate/automation_add_carts.php"
URL_STUDIOSEARCH = "https://dev.wsbf.net/api/zautomate/studio_search.php"

### sid.conf stores the previous/current showID
FILE_AUTOCONF = "sid.conf"

class DBInterface():
    ShowID = -1

    def __init__(self):
        pass

    ### try to pull the show id we last used from the config file.
    def ShowID_Restore(self):
        if self.ShowID is -1:
            if os.access(FILE_AUTOCONF, os.R_OK) is True:
                f = open(FILE_AUTOCONF, "r")

                try:
                    self.ShowID = (int)(f.read())
                except ValueError:
                    print "Error: Prior show ID is malformed."

            ### otherwise, step back in time here to get self.ShowID without hardset
            else:
                self.ShowID_GetNewID()

    ### push automation back a global number of days
    ### only call this if it gets to the present
    def ShowID_GetNewID(self):
        try:
            res = requests.get(URL_AUTOSTART, params={"showid": self.ShowID})
            self.ShowID = res.json()
        except requests.exceptions.SSLError:
            print "Error: Could not fetch starting show ID."

    def ShowID_Save(self):
        f = open(FILE_AUTOCONF, "w")
        f.write((str)(self.ShowID + 1))
        f.close()

    ### return a Cart object based on its type
    def Cart_Request(self, cartType):
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
            print self.timeStamp() + " :=: Error: Could not fetch cart."

        return None

    def Get_Next_Playlist(self):
        # get next show ID
        if self.ShowID is -1:
            print self.timeStamp() + " :=: DBInterface :: Get_Next_Playlist() :: calling ShowID_GetNewID()"
            self.ShowID_GetNewID()
        else:
            self.ShowID += 1

        # get next playlist
        playlist = []
        try:
            res = requests.get(URL_AUTOLOAD, params={"showid": self.ShowID})
            show = res.json()

            self.showID = show["showID"]

            print "DBInterface :: Get_Next_Playlist() :: Enqueueing new showID " + (str)(self.ShowID)

            for t in show["playlist"]:
                # TODO: move pathname building to Track constructor
                filename = LIBRARY_PREFIX + t["file_name"]
                trackID = t["lb_album_code"] + "-" + t["lb_track_num"]

                track = Cart(trackID, t["lb_track_name"], t["artist_name"], t["rotation"], filename)

                if track.Verify():
                    playlist.append(track)
                else:
                    print self.timeStamp() + " :=: DBInterface :: Get_Next_Playlist() :: cart file \"" + filename + "\" does not exist"
        except requests.exceptions.SSLError:
            print "Error: Could not fetch playlist."

        return playlist

    ### load a dictionary of cart types to cart arrays
    def CartMachine_Load(self):
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
            print self.timeStamp() + " :=: Error: Could not fetch carts."

        return carts

    def Studio_Search(self, query):
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

    def timeStamp(self):
        return time.asctime(time.localtime(time.time()))
