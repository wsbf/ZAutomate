from ZAutomate_Config import *
from ZAutomate_Cart import *
import os, urllib
import requests

## GLOBALS USED
##    LIBRARY_PREFIX     '/media/ZAL/'
##    PLATFORM_DELIMITER = '/'

### URLs for the web interface
URL_CARTLOAD     = 'https://dev.wsbf.net/api/zautomate/cartmachine_load.php'
URL_AUTOLOAD     = 'http://stream.wsbf.net/wizbif/zautomate_2.0/automation_generate_showplist.php'
URL_AUTOSTART    = 'https://dev.wsbf.net/api/zautomate/automation_generate_showid.php'
URL_AUTOCART     = 'https://dev.wsbf.net/api/zautomate/automation_add_carts.php'
URL_STUDIOSEARCH = 'http://stream.wsbf.net/wizbif/zautomate_2.0/studio_search.php'

### sid.conf stores the previous/current showID
FILE_AUTOCONF = 'sid.conf'

class DBInterface():
    ShowID = -1

    def __init__(self):
        pass

    # TODO: is this method necessary?
    def LogAppend(self, text):
        print text

    ### try to pull the show id we last used from the config file.
    def ShowID_Restore(self):
        if self.ShowID is -1:
            if os.access(FILE_AUTOCONF, os.R_OK) is True:
                f = open(FILE_AUTOCONF, 'r')

                try:
                    self.ShowID = (int)(f.read())
                except ValueError:
                    self.LogAppend("Error: Prior show ID is malformed.")

            ### otherwise, step back in time here to get self.ShowID without hardset
            else:
                self.ShowID_GetNewID()

    ### push automation back a global number of days
    ### only call this if it gets to the present
    def ShowID_GetNewID(self):
        try:
            r = requests.get(URL_AUTOSTART, params = {
                "showid": self.ShowID
            })
            self.ShoWID = r.json()
        except URLError, Error:
            self.LogAppend("Error: Could not fetch starting show ID.")

    def ShowID_Save(self):
        f = open(FILE_AUTOCONF, 'w')
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
                r = requests.get(URL_AUTOCART, params = {
                    "type": cartType
                })
                c = r.json()

                # return if cart type is empty
                if c is None:
                    return None

                # construct cart
                pathname = LIBRARY_PREFIX + 'carts' + PLATFORM_DELIMITER + c["filename"]
                cart = Cart(c["cartID"], c["title"], c["issuer"], c["type"], pathname)

                # verify cart filename
                if cart.Verify():
                    return cart
                else:
                    count += 1
        except URLError, Error:
            print self.timeStamp() + " :=: Error: Could not fetch cart."

        return None

    def Playlist_Next_Enqueue(self):
        ReturnList = []
        Counter = 0        ##DEBUG

        if self.ShowID is not -1:
            self.ShowID += 1
            print self.timeStamp() + " :=: DBInterface :: Playlist_Next_Enqueue() :: Next ShowID = " + (str)(self.ShowID)
        else:
            print self.timeStamp() + " :=: DBInterface :: Playlist_Next_Enqueue() :: ShowID = " + (str)(self.ShowID)
            print self.timeStamp() + " :=: DBInterface :: Playlist_Next_Enqueue() :: calling ShowID_GetNewID()"
            self.ShowID_GetNewID()
        lines = None
        if self.ShowID is not None:
            print self.timeStamp() + " :=: DBInterface :: Playlist_Next_Enqueue() :: calling automation_generate_showplist.php"
            url = URL_AUTOLOAD + "?sid=" + (str)(self.ShowID)
            try:
                resource = urlopen(url)
                lines = resource.read().split("\n")
            except URLError, Error:
                self.LogAppend("Error: Could not fetch playlist.")
                self.LogAppend("url: "+url)

        ###YATES_COMMENT: I have no idea what this does.  I assume it takes the
        ###                    characters 7:Strlen of line[0] and casts it as an int.
        ###                    What that does, I have no idea.

        ###YATES_ANSWER: echo "SHOWID ".$sID."\n" is the first line returned from
        ###                  automation_generate_showplist.php.
        print self.timeStamp() + " :=: DBInterface :: Playlist_Next_Enqueue :: old showid = " + str(lines[0][7:])
        try:
            self.ShowID = int(lines[0][7:])
        except ValueError:
            print self.timeStamp() + " :=: url = " + (str)(url)
            print self.timeStamp() + " :=: DBInterface :: Playlist_Next_Enqueue :: new showid = " + str(lines[0][7:])
        print self.timeStamp() + " :=: DBInterface :: Playlist_Next_Enqueue :: new showid = " + str(lines[0][7:])
        lines.pop(0)
        self.LogAppend( "DBInterface :: Playlist_Enqueue_Next() :: Enqueueing new showID "+(str)(self.ShowID) )
        print self.timeStamp() + " :=: DBInterface :: Playlist_Enqueue_Next() :: Entering the enqueue loop"
        for line in lines:
            if(line is ""):
                continue
            fd = line.split("<|>")
            #CONTENTS of fd :: id title issue type filename
            try:
                filename = urllib.unquote_plus(fd[8])
            except IndexError:
                self.LogAppend("DBInterface :: Playlist_Enqueue_Next() :: Index Out Of Bounds Error")
                self.LogAppend("DBInterface :: Playlist_Enqueue_Next() :: line = " + (str)(line))

            ###YATES_COMMENT: Python URLLib function call.
            ###  See http://docs.python.org/library/urllib.html#urllib.unquote_plus
            ###        Replace %xx escapes by their single-character equivalent.
            ###        Example: unquote('/%7Econnolly/') yields '/~connolly/'.
            ###        Changes the filename to a HTML friendly form

            ###YATES_COMMENT: Get the filename in the absolute path form.
            filename = LIBRARY_PREFIX+filename[0]+PLATFORM_DELIMITER+filename[1]+PLATFORM_DELIMITER+filename[2:]

            ###YATES_COMMENT: Results in IDCode - FileName (Not Path)
            songID = str(fd[0]) + '-' + str(fd[1])    # ID code for logging purposes

            ###YATES_COMMENT: This seems a little hairy.  We're using the Cart class for both
            ###                    Songs being played and Carts (PSA/UW/ID/Etc)
            thiscart = Cart(songID, fd[5], fd[4], fd[3], filename)

            ###def __init__(self, cid, title, issuer, cartType, filename):
            if thiscart.Verify():
                ReturnList.append(thiscart)
            else:
                print self.timeStamp() + " :=: DBInterface :: Playlist_Enqueue_Next :: cart file " + filename + " does not exist"
        return ReturnList

    ### load a dictionary of cart types to cart arrays
    def CartMachine_Load(self):
        types = [0, 1, 2, 3]
        carts = {}

        try:
            for t in types:
                r = requests.get(URL_CARTLOAD, params = {
                    "type": t
                })

                carts_res = r.json()
                carts[t] = []

                for c in carts_res:
                    # TODO: consider moving pathname construction to Cart
                    pathname = LIBRARY_PREFIX + 'carts' + PLATFORM_DELIMITER + c["filename"]

                    cart_tmp = Cart(c["cartID"], c["title"], c["issuer"], c["type"], pathname)

                    # verify that this file exists
                    if ( cart_tmp.Verify() ):
                        carts[t].append(cart_tmp)

        except URLError, Error:
            print self.timeStamp() + " :=: Error: Could not fetch carts."

        return carts

    def Studio_Search(self, query):
        query = urllib.quote_plus(query)
        ###Python URLLib call.
        ###http://docs.python.org/library/urllib.html#urllib.quote_plus
        ###Replace special characters in string using the %xx escape.
        ###Letters, digits, and the characters '_.-' are never quoted.
        ###By default, this function is intended for quoting path section of URL
        ###The optional safe parameter specifies additional characters
        ###that should not be quoted - its default value is '/'.
        ###Example: quote('/~connolly/') yields '/%7econnolly/'.
        ###YATES_COMMENT: Turns a string into an HTML Friendly String.
        ReturnList = []
        try:
            resource = urlopen(URL_STUDIOSEARCH + "?query=" + (str)(query))
            ###YATES_COMMENT: Returns an array of matches with the form:
            ###Line[i][]={album_code, track_num, genre, rotation_bin,
            ###           artist_name, track_name, album_name, label, file_name}
            lines = resource.read().split("\n")

        except URLError, Error:
            self.LogAppend("Error: Could not fetch search results.")

        for line in lines:
            if len(line) is 0:
                continue

            fd = line.split("<|>")
            ###YATES_COMMENT:
            ###fd[0] = cdCode             / cartID
            ###fd[1] = track_num
            ###fd[2] = genre
            ###fd[3] = rotation_bin     / playMask
            ###fd[4] = artist_name      / cartIssuer
            ###fd[5] = track_name        / cartTitle
            ###fd[6] = album_name
            ###fd[7] = label
            ###fd[8] = file_name
            filename = urllib.unquote_plus(fd[8])
            # ID code for logging purposes - just the cartID for carts, cdCode-trNum for songs
            songID = str(fd[0])

            thiscart = None
            ### a -1 in the track field (index 1) means it's a cart, not a song
            if fd[1] != str(-1):
                filename = LIBRARY_PREFIX+filename[0]+PLATFORM_DELIMITER+filename[1]+PLATFORM_DELIMITER+filename[2:]
                songID = str(fd[0]) + '-' + str(fd[1])
                thiscart = Cart(songID, fd[5], fd[4], fd[3], filename) ## fd[6] is the album
                ###NB: fd[3] = rotation_bin, fd[4] = artist_name, fd[5] = track_name for songs
            else:
                filename = LIBRARY_PREFIX+'carts'+PLATFORM_DELIMITER+filename
                thiscart = Cart(songID, fd[5], fd[4], fd[3], filename) #3 was 6
                ###NB: fd[3] = issue, fd[4] = title, fd[5] = track for carts.

            if thiscart.Verify():
                ReturnList.append(thiscart)

        return ReturnList

    def timeStamp(self):
        return time.asctime(time.localtime(time.time()))
