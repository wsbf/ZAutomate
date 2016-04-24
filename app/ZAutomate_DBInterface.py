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
URL_AUTOSTART    = 'http://stream.wsbf.net/wizbif/zautomate_2.0/automation_generate_showid.php'
URL_AUTOCART     = 'http://stream.wsbf.net/wizbif/zautomate_2.0/automation_add_carts.php'
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
        print self.timeStamp() + " :=: DBInterface:: ShowID_Restore :: Executing..."

        if os.access(FILE_AUTOCONF, os.R_OK) is True and self.ShowID < 0:
            f = open(FILE_AUTOCONF, 'r')

            try:
                self.ShowID = (int)(f.read())
                print self.timeStamp() + " :=: DBInterface :: ShowID_Restore :: Saved ShowID = " + (str)(self.ShowID)
            except ValueError:
                self.LogAppend("Error: Prior show ID is malformed.")
        else:
            print self.timeStamp() + " :=: DBInterface :: ShowID_Restore :: Could not open file " + FILE_AUTOCONF

        ### otherwise, step back in time here to get self.ShowID without hardset
        if self.ShowID is -1:
            print self.timeStamp() + " :=: DBInterface :: ShowID_Restore :: ShowID = -1, calling ShowID_Rewind"
            self.ShowID_GetNewID()

    ### simple - get or generate the ShowID
    ###YATES_COMMENT: Mutating getters are bad.
    def ShowID_Get(self):
        if self.ShowID is -1:
            print self.timeStamp() + " :=: DBInterface :: ShowID_Get() :: ShowID == -1, calling ShowID_Restore()"
            self.ShowID_Restore()
        return self.ShowID

    ### push automation back a global number of days
    ### only call this if it gets to the present
    def ShowID_GetNewID(self):
        self.LogAppend("DBInterface :: ShowID_GetNewID :: Getting new ShowID...")
        self.LogAppend("DBInterface :: ShowID_GetNewID :: calling automation_generate_showid("+(str)(self.ShowID)+")")
        url = URL_AUTOSTART + "?showid=" + (str)(self.ShowID)
        try:
            resource = urlopen(url)
            ##YATES_COMMENT: Where does resource come from?
            ##YATES_ANSWER:  Resource is a temporary variable that is used to read
            ##                    a showID from the URL
            self.ShowID = (int)(resource.read())
            print self.timeStamp() + " :=: DBInterface :: ShowID_GetNewID :: new ShowID = " + (str)(self.ShowID)
        except URLError, Error:
            self.LogAppend("Error: Could not fetch starting show ID.")
            self.LogAppend("url: "+url)

    def ShowID_Save(self):
        f = open(FILE_AUTOCONF, 'w')
        f.write((str)(self.ShowID+1))
        f.close()

    ### return a Cart object based on its type
    def Cart_Request(self, cartType):
        ###YATES_COMMENT: Why do we have a nested/embedded function here?
        ###YATES_ANSWER: So that no one else can call it.  internal simply returns
        ###                  a valid cart so we can... do something with it.
        ###                  The Cart_Request function loops until we find a good cart
        print self.timeStamp() + " :=: DBInterface :: Cart_Request() :: Entered Function"
        def internal(self, cartType):
            print self.timeStamp() + " :=: DBInterface :: Cart_Request() :: Internal() :: Entered Function"
            lines = None
            ###YATES_COMMENT: What can type be?
            ###YATES_ANSWER:
            ### MySQL TinyInt(3) --- 0 for PSA
            ###                             1 for Underwriting
            ###                             2 for StationID
            ###                             3 for Promos (Fall Fest Promo?)
            ###                             4 for NewsBombs
            ###                             5 for SignOn Cart
            url = URL_AUTOCART + "?type=" + cartType
            try:
                print self.timeStamp() + " :=: DBInterface :: Cart_Request() :: Internal() :: Grabbing a cart of type " + cartType
                resource = urlopen(url)
                lines = resource.read().split("\n")
                if lines[0] == '':
                    self.LogAppend("DBInterface :: Cart_Request() :: Internal() :: Error: No carts of type " + cartType)
                    return None
            except URLError:
                self.LogAppend("DBInterface :: Cart_Request() :: Internal() :: Error: Could not fetch cart.")
                self.LogAppend("DBInterface :: Cart_Request() :: Internal() :: url: "+url)
                return None

            ###YATES_COMMENT: At this point, automation_add_carts.php returns is
            ###                    a random cart in the form of a string with the fields
            ###                    from the libcart table.

            fd = lines[0].split(', ')
            ###YATES_COMMENT: Split results in the following array
            ###                    fd[0] = cartID
            ###                    fd[1] = start_date
            ###                    fd[2] = end_date
            ###                    fd[3] = play_mask
            ###                    fd[4] = issuer
            ###                    fd[5] = title
            ###                    fd[6] = cart_typeID
            ###                    fd[7] = filename


            ###YATES_COMMENT: Python URLLib function call.
            ###  See http://docs.python.org/library/urllib.html#urllib.unquote_plus
            ###        Replace %xx escapes by their single-character equivalent.
            ###        Example: unquote('/%7Econnolly/') yields '/~connolly/'.
            ###        Changes the filename to a HTML friendly form

            filename = urllib.unquote_plus(fd[7])
            filename = LIBRARY_PREFIX+'carts'+PLATFORM_DELIMITER+filename

            ###YATES_COMMENT: filename is now a resolvable absolute path to the
            ###                    cart that was added.  LIRBARY_PREFIX resides in
            ###                    ZAutomate_Confi.py, LIBRARY_PREFIX = '/media/ZAL/'

            ###          Cart(cartID, issuer, typeID, typeID, filename)
            ###YATES_COMMENT: Why is typeID being passed twice?
            ################thiscart = Cart(fd[0], fd[4], fd[6], fd[6], filename)
            ###Cart Constructor
            ###def __init__(self, cid, title, issuer, ctype, filename):
            ###I think this really needs to be changed to
            thiscart = Cart(fd[0], fd[5], fd[4], fd[8], filename)
            ###Also, I think making the filename into its absolute form should be
            ###the Cart constructor's job.
            return thiscart
        print self.timeStamp() + " :=: DBInterface :: Cart_Request() :: Entering loop to get a cart"
        ctr = 0
        while ctr < 5:
            ct = internal(self, cartType)
            if ct.Verify():
                print self.timeStamp() + " :=: DBInterface :: Cart_Request() :: Found a good cart, Returning"
                break
            else:
                print self.timeStamp() + " :=: DBInterface :: Cart_Request() :: Cart is no good, requesting another cart"
                ctr += 1
                ct = None
        return ct

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
            if os.path.isfile(filename) is not True:
                print self.timeStamp() + " :=: Could not find file: " + (str)(filename)
                pass
            else:
                print self.timeStamp() + " :=: Found file: " + (str)(filename)
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
                    pathname = LIBRARY_PREFIX + 'carts' + PLATFORM_DELIMITER + c["filename"]

                    # TODO: mock ZAutoLib in development
                    pathname = "test/test.mp3"

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
