# -*- coding: cp1252 -*-
"""
NABBOX UI script
- NABBOX core made by Alexsolex
- User interface made by Temhil

14-10-08 Version 1.1 by Temhil and Seb
    - Fixed crash on Linux: replaced .ini extention by .cfg (thanks Seb)
    - Correct exception handling in case of connection parameters not defined
    - Fixed bug: we didn't close ini file after updating it
09-10-08 Version 1.0 by Temhil
    - Added Debug mode support (partially implemented)
    - Added About and Help window
    - Saved file to UNIX(LF) format
    - Added password hidding while entering
    - Added option for deleting folder within download directory (i.e created during archive extraction)
    - Added option for extracting archives
    - Added option to continue background download after exiting (with warning on XBMC stability)
    - Added arrows (up/down) for navigation on the list
    - Modified algorithm for downloading files in order to fix the crashes
    - Added page for browsing, deleting and playing downloaded files
    - Added progress bar for background downloads 
      -> user can still navigate
    - Added dialogprogress window for foreground downloads 
      -> user is blocked while download is in progress
    - Added menu for stopping downloads in progress
    - Moved and modified version label
    - Added password hidden for XBOX (doesn't work - XBMC issue)
    - fixed bug on PLAYER_CORE_PAPLAYER and PLAYER_CORE_MODPLAYER not 
      supported on certain platform
23-06-08 Version Beta1 by Temhil
    - UI Creation 
"""

############################################################################
version     = 'Version 1.1'
authorUI    = 'Temhil'
authorCore  = 'Alexsolex'
############################################################################


############################################################################
# import  
############################################################################
import sys
import os
import traceback
from string import *
import time
import urllib
import urllib2
import ConfigParser
try:
    import xbmcgui, xbmc
except ImportError:
    raise ImportError, 'This program requires the XBMC extensions for Python.'

try:
    del sys.modules['NABBOX']
except:
    pass 

try:
    import NABBOX as NABBOX
except ImportError:
    raise ImportError, 'This program requires NABBOX extensions'
    
from decimal import *



############################################################################
# emulator
############################################################################
try: 
    Emulating = xbmcgui.Emulating
except: 
    Emulating = False

############################################################################
# Get current working directory and update internal vars with it  
############################################################################

# Set paths
ROOTDIR = xbmc.translatePath(os.getcwd().replace( ";", "" )) # Create a path with valid format

IMAGEDIR    = os.path.join(ROOTDIR, "images")
CACHEDIR    = os.path.join(ROOTDIR, "cache")
DOWNLOADDIR = os.path.join(ROOTDIR, "download")

# List of directories to check at startup
#TODO: use tuple
checkList   = [CACHEDIR,DOWNLOADDIR]

# Maximum connection retry
MAX_CONN_RETRY = 1

############################################################################
# Get actioncodes from keymap.xml
############################################################################

ACTION_MOVE_LEFT                    = 1
ACTION_MOVE_RIGHT                   = 2
ACTION_MOVE_UP                      = 3
ACTION_MOVE_DOWN                    = 4
ACTION_PAGE_UP                      = 5
ACTION_PAGE_DOWN                    = 6
ACTION_SELECT_ITEM                  = 7
ACTION_HIGHLIGHT_ITEM               = 8
ACTION_PARENT_DIR                   = 9
ACTION_PREVIOUS_MENU                = 10
ACTION_SHOW_INFO                    = 11
ACTION_PAUSE                        = 12
ACTION_STOP                         = 13
ACTION_NEXT_ITEM                    = 14
ACTION_PREV_ITEM                    = 15
ACTION_MUSIC_PLAY                   = 79

ACTION_MOUSE                        = 90

ACTION_MOUSE_CLICK                  = 100
ACTION_MOUSE_LEFT_CLICK             = 100
ACTION_MOUSE_RIGHT_CLICK            = 101
ACTION_MOUSE_MIDDLE_CLICK           = 102
ACTION_MOUSE_XBUTTON1_CLICK         = 103
ACTION_MOUSE_XBUTTON2_CLICK         = 104
ACTION_MOUSE_DOUBLE_CLICK           = 105
ACTION_MOUSE_LEFT_DOUBLE_CLICK      = 105
ACTION_MOUSE_RIGHT_DOUBLE_CLICK     = 106
ACTION_MOUSE_MIDDLE_DOUBLE_CLICK    = 107
ACTION_MOUSE_XBUTTON1_DOUBLE_CLICK  = 108
ACTION_MOUSE_XBUTTON2_DOUBLE_CLICK  = 109
ACTION_BACKSPACE                    = 110
ACTION_SCROLL_UP                    = 111
ACTION_SCROLL_DOWN                  = 112
ACTION_ANALOG_FORWARD               = 113
ACTION_ANALOG_REWIND                = 114
ACTION_MOVE_ITEM_UP                 = 115  # move item up in playlist
ACTION_MOVE_ITEM_DOWN               = 116  # move item down in playlist
ACTION_CONTEXT_MENU                 = 117

#############################################################################
# Player values
#############################################################################
PLAYER_AUTO         = 0 # xbmc.PLAYER_CORE_AUTO
PLAYER_DVDPLAYER    = 1 # xbmc.PLAYER_CORE_DVDPLAYER
PLAYER_MPLAYER      = 2 # xbmc.PLAYER_CORE_MPLAYER

# Create a tuple maching to the value above
#TODO: use tuple
playerSelect = [xbmc.PLAYER_CORE_AUTO,
                xbmc.PLAYER_CORE_DVDPLAYER,
                xbmc.PLAYER_CORE_MPLAYER]
#############################################################################
# Control alignment
#############################################################################
xbfont_left         = 0x00000000
xbfont_right        = 0x00000001
xbfont_center_x     = 0x00000002
xbfont_center_y     = 0x00000004
xbfont_truncated    = 0x00000008


#############################################################################
# Error Codes
#############################################################################
ERR_NO_LOGIN        = 1
ERR_NO_PASSW        = 2


#############################################################################
# autoscaling values
#############################################################################
HDTV_1080i          = 0 #(1920x1080, 16:9, pixels are 1:1)
HDTV_720p           = 1 #(1280x720, 16:9, pixels are 1:1)
HDTV_480p_4x3       = 2 #(720x480, 4:3, pixels are 4320:4739)
HDTV_480p_16x9      = 3 #(720x480, 16:9, pixels are 5760:4739)
NTSC_4x3            = 4 #(720x480, 4:3, pixels are 4320:4739)
NTSC_16x9           = 5 #(720x480, 16:9, pixels are 5760:4739)
PAL_4x3             = 6 #(720x576, 4:3, pixels are 128:117)
PAL_16x9            = 7 #(720x576, 16:9, pixels are 512:351)
PAL60_4x3           = 8 #(720x480, 4:3, pixels are 4320:4739)
PAL60_16x9          = 9 #(720x480, 16:9, pixels are 5760:4739)

            
            
#############################################################################
# Nabbox UI functions 
#############################################################################

class cancelRequest(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class fileMgr:
    """
    
    File manager
    
    """
    #TODO: Create superclass, inherit and overwrite init
    def __init__(self,checkList):
        self.verifrep(checkList[0]) #CACHEDIR
        self.verifrep(checkList[1]) #DOWNLOADDIR

        # Set variables needed by NABBOX module
        NABBOX.HTMLFOLDER = checkList[0] #CACHEDIR
        print"browser - set NABBOX.HTMLFOLDER: %s"%(NABBOX.HTMLFOLDER)

    def verifrep(self, folder):
        """
        Check a folder exists and make it if necessary
        """
        try:
            #print("verifrep check if directory: " + folder + " exists")
            if not os.path.exists(folder):
                print("verifrep Impossible to find the directory - trying to create the directory: " + folder)
                os.makedirs(folder)
        except Exception, e:
            print("Exception while creating folder " + folder)
            print(str(e))
            
    def listDirFiles(self, path):
        """
        List the files of a directory
        @param path:
        """
        #print("List File of directory = " + path)
        dirList=os.listdir(path)
        #print dirList
        return dirList
        
    def deleteFile(self, filename):
        """
        Delete a file form download directory
        @param filename:
        """
        os.remove(filename)
        
    def delFiles(self,folder):
        """
        From Joox
        Deletes all files in a given folder and sub-folders.
        Note that the sub-folders itself are not deleted.
        Parameters : folder=path to local folder
        """
        for root, dirs, files in os.walk(folder , topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
    
    def  extract(self,archive,targetDir):
        """
        Extract an archive in targetDir
        """
        xbmc.executebuiltin('XBMC.Extract(%s,%s)'%(archive,targetDir) )
    

class browser:
    """
    
    Provides browsing functions
    User of Nabbox module
    
    """
    def __init__(self):
        """
        browser init
        """
        self.fileMgr             = fileMgr(checkList)
        
        # Configuration attributes
        self.login               = ""
        self.password            = ""
        self.thanks              = "Merci"
        #self.thanks             = "Merci pour tout !\n\n%s"%self.login
        self.delCache            = True
        self.cachepages          = False
        self.defaultPlayer       = PLAYER_AUTO
        self.displayProgBar      = True
        self.debugMode           = False
        # timeout in seconds
        self.timeout             = 15
        
        # Other internal attributes
        self.currentTitleLabel   = "Forum Nabbox"
        self.currentHandlerList  = []
        self.currentdisplayList  = []
        self.currentLinkTypeList = []
        self.currentConnecStatus = False
        
        self.currentPage_str      = "1/1"
        self.currentNextPageHdl   = None
        self.currentPrevPageHdl   = None
        
        self.is_conf_valid        = True # Define if configuration file is valid or not
        
        # Flag for history or download page is active or not
        self.localpageisactive     = False
        self.isXbox                = False # True is current platform is an XBOX
        
        # Download status
        self.dowldInProgress       = False
        
        # Create history instance in order to store browsing history
        self.history               = history()
        
        if (len (xbmc.getInfoLabel('system.xboxserial')) > 0):
            print "Current platform is XBOX"
            self.isXbox = True
            #self.displayProgBar = False # Will be overwritten by the value defined in conf file (only if this value is defined)
        else:
            print "Current platform is NOT XBOX"

        # Load configuration file
        print "Loading configuration file"
        self.loadConf()
        
        if self.isXbox == True:
            # Set the default timeout
            from socket import setdefaulttimeout # For supporting timeout
            setdefaulttimeout(self.timeout) 
            
        if self.debugMode == True:
            import httplib
            httplib.HTTPConnection.debuglevel = 1
        
        # Connect to Nabbox.com and create a session
        if self.connect():
            print"Connected to Nabbox.com"
            
        #######################################################
        # Create first entry corresponding to the startup page
        #######################################################
        # - Create dictionary
        params              = {}
        params["s"]         = self.sessionID # Adding to dictionary the session ID
        params["showforum"] = "46"           # !!!!! We load forum directly from capture TV forum (id=46)
        #params["act"]      = "idx"          # That would be the value if we start from the main page of Nabbox
        
        self.currentdisplayList.append("Captures TV")   # adding forum title
        self.currentHandlerList.append(params)          # adding handler (here params for the forum ID)
        self.currentLinkTypeList.append("forum")        # adding type of hander / linked page
        
        #TODO: function in browser allowing to know if an account is set        
        
    def loadConf(self):
        """
        Load configuration file, check it, and correct it if necessary
        """
        try:
            # Create config parser
            self.config = ConfigParser.ConfigParser()
            
            # Read config from .cfg file
            # - Open config file
            self.config.read(os.path.join(ROOTDIR,"nabbox.cfg"))
            
            # Check sections exist
            if (self.config.has_section("account") == False):
                self.config.add_section("account")
                self.is_conf_valid = False
            if (self.config.has_section("messages") == False):
                self.config.add_section("messages")
                self.is_conf_valid = False
            if (self.config.has_section("system") == False):
                self.config.add_section("system")
                self.is_conf_valid = False
                
            # - Read config from file and correct it if necessary
            if (self.config.has_option("account", "login") == False):
                self.config.set("account", "login", self.login)
                self.is_conf_valid = False
            else:
                self.login = self.config.get("account", "login")
            if (self.config.has_option("account", "password") == False):
                self.config.set("account", "password", self.password)
                self.is_conf_valid = False
            else:
                self.password = self.config.get("account", "password")
                
            if (self.config.has_option("messages", "remerciement") == False):
                self.config.set("messages", "remerciement", self.thanks)
                self.is_conf_valid = False
            else:
                self.thanks = self.config.get("messages", "remerciement")
            if (self.config.has_option("system", "cleancache") == False):
                self.config.set("system", "cleancache", self.delCache)
                self.is_conf_valid = False
            else:
                self.delCache = self.config.getboolean("system", "cleancache")
            if (self.config.has_option("system", "cachepages") == False):
                self.config.set("system", "cachepages", self.cachepages)
                self.is_conf_valid = False           
            else:
                self.cachepages = self.config.getboolean("system", "cachepages")
            if (self.config.has_option("system", "player") == False):
                self.config.set("system", "player", self.defaultPlayer)
                self.is_conf_valid = False
            else:
                self.defaultPlayer = int(self.config.get("system", "player"))
            if (self.config.has_option("system", "timeout") == False):
                self.config.set("system", "timeout", self.timeout)
                self.is_conf_valid = False
            else:
                self.timeout = int(self.config.get("system", "timeout"))
            if (self.config.has_option("system", "progbar") == False):
                self.config.set("system", "progbar", self.displayProgBar)
                self.is_conf_valid = False           
            else:
                self.displayProgBar = self.config.getboolean("system", "progbar")
            if (self.config.has_option("system", "debugmode") == False):
                self.config.set("system", "debugmode", self.debugMode)
                self.is_conf_valid = False           
            else:
                self.debugMode = self.config.getboolean("system", "debugmode")
                
            if (self.is_conf_valid == False):
                # Update file
                print "INI file format wasn't valid: correcting ..."
                cfgfile=open(os.path.join(ROOTDIR,"nabbox.cfg"), 'w+')
                self.config.write(cfgfile)
                self.is_conf_valid = True
                cfgfile.close()
        except Exception, e:
            print("Exception while loading configuration file " + "nabbox.cfg")
            print(str(e))
            self.is_conf_valid = False
        
        return self.is_conf_valid
        
        
    def setLogin(self,login):
        """
        set Nabbox account Login locally and in .cfg file
        @param login: account login
        """
        print "******** setLogin STARTS"
        self.login               = login
        self.currentConnecStatus = False # Will force to reconnect and create a new session ID
        
        try:
            # Set login parameter
            self.config.set("account", "login", login)
    
            # Update file
            cfgfile=open(os.path.join(ROOTDIR,"nabbox.cfg"), 'w+')
            self.config.write(cfgfile)
            cfgfile.close()
        except Exception, e:
            print("Exception during setLogin")
            print(str(e))
            print (str(sys.exc_info()[0]))
            traceback.print_exc()
        print "******** setLogin ENDS"
        
    def getLogin(self):
        """
        return the Nabbox account Login currently used
        """
        return self.login
        
    def setPassword(self,password):
        """
        set Nabbox account Password locally and in .cfg file
        @param password: account password
        """
        print "******** setPassword STARTS"
        self.password            = password
        self.currentConnecStatus = False # Will force to reconnect and create a new session ID

        try:
            # Set password parameter
            self.config.set("account", "password", password)
    
            # Update file
            cfgfile=open(os.path.join(ROOTDIR,"nabbox.cfg"), 'w+')
            self.config.write(cfgfile)
            cfgfile.close()
        except Exception, e:
            print("Exception during setPassword")
            print(str(e))
            print (str(sys.exc_info()[0]))
            traceback.print_exc()
        print "******** setPassword ENDS"
        
    def getPassword(self):
        """
        return the Nabbox account Password currently used
        """
        return self.password
        
    def setThanksMsg(self,thanku):
        """
        set Thank You parameter locally and in .cfg file
        """
        self.thanks = thanku
        
        # Set message parameter
        self.config.set("messages", "remerciement", thanku)
        
        # Update file
        cfgfile=open(os.path.join(ROOTDIR,"nabbox.cfg"), 'w+')
        self.config.write(cfgfile)
        cfgfile.close()
        
    def getThanksMsg(self):
        """
        return the Thank You message currently used
        """
        return self.thanks
        
    def setDefaultPlayer(self,playerType):
        """
        set DefaultPlayerparameter locally and in .cfg file
        """
        self.defaultPlayer = playerType
        
        # Set player parameter
        self.config.set("system", "player", playerType)
        
        # Update file
        cfgfile=open(os.path.join(ROOTDIR,"nabbox.cfg"), 'w+')
        self.config.write(cfgfile)
        cfgfile.close()
        
    def getDefaultPlayer(self):
        """
        return the player currently used
        """
        return self.defaultPlayer

    def setCleanCache(self,cleanCacheStatus):
        """
        set clean cache status locally and in .cfg file
        @param cleanCacheStatus: clean cache status - define cache directory will be cleaned or not on exit
        """
        self.delCache = cleanCacheStatus
        
        # Set cachepages parameter
        self.config.set("system", "cleancache", self.delCache)

        # Update file
        cfgfile=open(os.path.join(ROOTDIR,"nabbox.cfg"), 'w+')
        self.config.write(cfgfile)
        cfgfile.close()
        
    def getCleanCache(self):
        """
        return current clean cache status - define cache directory will be cleaned or not on exit
        """
        return self.delCache
        
    def setCachePages(self,cachepagesStatus):
        """
        set cache pages status locally and in .cfg file
        @param cachepages: cachepages status - define if page will be cached or not
        """
        self.cachepages = cachepagesStatus
        
        # Set cachepages parameter
        self.config.set("system", "cachepages", self.cachepages)

        # Update file
        cfgfile=open(os.path.join(ROOTDIR,"nabbox.cfg"), 'w+')
        self.config.write(cfgfile)
        cfgfile.close()
        
    def getCachePages(self):
        """
        return current cachepages status - define if page will be cahed or not
        """
        return self.cachepages
        
    def setDisplayProgBar(self,displayProgBarStatus):
        """
        set progress bar status locally and in .cfg file
        @param cachepages: progress bar status 
                           -> define progress bar will be displayed or not during download
                           -> define download method used
        """
        self.displayProgBar = displayProgBarStatus
        
        # Set cachepages parameter
        self.config.set("system", "progbar", self.displayProgBar)

        # Update file
        cfgfile=open(os.path.join(ROOTDIR,"nabbox.cfg"), 'w+')
        self.config.write(cfgfile)
        cfgfile.close()
        
    def getDisplayProgBar(self):
        """
        return current progress bar status
                           -> define progress bar will be displayed or not during download
                           -> define download method used
        """
        return self.displayProgBar
        
    def setDebugMode(self,debugModeStatus):
        """
        set Debug Mode status locally and in .cfg file
        @param cachepages: Debug Mode status - define if debug mode is active or not
        """
        self.debugMode = debugModeStatus

        if debugModeStatus == True:
            import httplib
            httplib.HTTPConnection.debuglevel = 1
        else:
            if sys.modules.has_key("httplib"):
                del sys.modules['httplib']
            
        # Set cachepages parameter
        self.config.set("system", "debugmode", self.debugMode)

        # Update file
        cfgfile=open(os.path.join(ROOTDIR,"nabbox.cfg"), 'w+')
        self.config.write(cfgfile)
        cfgfile.close()
        
    def getDebugMode(self):
        """
        return current Debug Mode status - define if debug mode is active or not
        """
        return self.debugMode
    
    def get_next_page_hdl(self):
        """
        Return the Handler of the next page
        """
        return self.currentNextPageHdl
               
    def get_prev_page_hdl(self):
        """
        Return the Handler of the previous page
        """
        return self.currentPrevPageHdl
               
    def get_page_str(self):
        """
        Return a string composed by the current page and total number of page separated by '/' 
        i.e '1/2'
        """
        return self.currentPage_str
        
    def get_title(self):
        """
        Return title of current page
        """
        return self.currentTitleLabel
        
    def get_nameItem(self,index):
        """
        Return the name of an item from the current display list for a specific index
        @param index: item index in current list
        """
        return self.currentdisplayList[index]
    
    def get_typeItem(self,index):
        """
        Return the type of an item from the curuent Link Type list for a specific index
        @param index: item index in current list
        """
        return self.currentLinkTypeList[index]
    
    def get_hdlItem(self,index):
        """
        Return the handler of an item from the current HandlerList for a specific index
        In the particular case of video, handler are video ULRs
        @param index: item index in current list
        """
        return self.currentHandlerList[index]
    
    def get_displayList(self):
        """
        Return the list of list items to display in the UI
        """
        return self.currentdisplayList
    
    def get_linkTypeList(self):
        """
        Return the list of list of type of list corresponding to the displayed item (
        it could be forum, topic, video ...
        """
        return self.currentLinkTypeList
    
    def is_connected(self):
        """
        Return last known status of the connection
        """
        return self.currentConnecStatus
        
    def errorDiagnosis(self):
        """
        Try to identify the cause of the failure
        Return an error code
        """
        #TODO: return string to display
        result = ""
        if (self.login == ""):
            print("Login non defini")
            result = "NO_LOGIN"
        if (self.password == ""):
            print("Password non defini")
            result = "NO_PASSWORD"
        return result
            
    def connect(self):
        """
        Connect to Nabbox website using account settings and create a session
        """
        # Opening a session
        try:
            self.sessionID = NABBOX.connexion(self.login,self.password,savehtml=self.cachepages)
            
            # Connection succeeded
            self.currentConnecStatus    = True
        except NABBOX.ConnectError:
            print("Exception during connection (NABBOX.ConnectError): Account not set (login and/or password)")
            self.sessionID              = None
            self.currentConnecStatus    = False
        except Exception, e:
            # Connection failed
            print("UNXPECTED Exception during connection:")
            print(str(e))
            print (str(sys.exc_info()[0]))
            traceback.print_exc()
            self.sessionID              = None
            self.currentConnecStatus    = False
        return self.currentConnecStatus
    
    def updateData(self, pageHdl, pageType):
        """
        Private function
        get data from a webpage according to the type of the webpage
        and update attribute of browser class
        return True in case of succes or false in case of connection error
        @param pageHdl: Handler for a page
        @param pageType:Type of a page (Forum, Topic ...)       
        """
        print " --- Updating data from Nabbox"
        
        # Load the page (only if we are connected)
        retry = 1 # Connection Retry
        if (self.currentConnecStatus == True):
            html = self.loadPage(pageHdl, pageType)
            #print "updateData - self.currentConnecStatus == True"
        else:
            # Not connected so return an empty hmtl
            html = ""
            #print "updateData - self.currentConnecStatus == False"
        
        # Check if we are connected and if we reach the max number of retry attempt
        while ((self.currentConnecStatus == False) or (len(html) == 0)) and (retry <= MAX_CONN_RETRY):
            print "updateData : NOT CONNECTED"
            print "updateData - Trying to reconnect"
            
            # Connection retry
            print "Connection Retry N %d"%retry
            self.connect()
            if (self.currentConnecStatus == True):
                # Load the page 
                print "updateData : CONNECTED"
                html = self.loadPage(pageHdl, pageType)
            retry = retry + 1
            
        # We check we are connected and got a valid page
        if  ((self.currentConnecStatus == True) and (len(html) != 0)):
            # Update page number
            # -> get current page
            currentPage = NABBOX.get_page_courante(html)
            if currentPage == None:
                currentPage = 1
            # -> get total number of pages
            totalPage = NABBOX.get_total_page(html)
            
            # -> Create the string to display
            self.currentPage_str = str(currentPage) + '/' + str(totalPage)

            # Update next and previous page handlers
            nextPageURL  = NABBOX.get_next_page(html)
            if nextPageURL != None:
                self.currentNextPageHdl = NABBOX.parse_params(nextPageURL)[1]
            else:
                self.currentNextPageHdl = None
                
            prevPageURL  = NABBOX.get_prev_page(html)
            if prevPageURL != None:
                self.currentPrevPageHdl = NABBOX.parse_params(prevPageURL)[1]
            else:
                self.currentPrevPageHdl = None

            # Update Title
            self.currentTitleLabel = NABBOX.get_title(html)
            
            if pageType == "index":
                # Index case
                # ----------
                
                # Looking for forums
                forums = NABBOX.get_forums(html)
                
                # Now we got the info -> Clear the lists: display / handler / type
                self.currentdisplayList  = []
                self.currentHandlerList  = []
                self.currentLinkTypeList = []
                
                for IDforum,forumTitle, forumDesc in forums:
                    #print "%s : %s\n\t%s"%(IDforum,forumTitle,forumDesc)
                    # Building dictionnary
                    params              = {}
                    params["s"]         = self.sessionID # adding session ID to the dictionnary
                    params["showforum"] = IDforum        
                    #params["act"]      = "idx"

                    #label = NABBOX.unescape(forumTitle) + "\n" + NABBOX.unescape(forumDesc)
                    label = forumTitle + "\n" + forumDesc
                    self.currentdisplayList.append(label)    # adding forum title
                    #self.currentHandlerList.append(IDforum) # adding handler (here the forum ID)
                    self.currentHandlerList.append(params)   # adding handler (here params for the forum ID)
                    self.currentLinkTypeList.append("forum") # adding type of hander / linked page
                    
            elif pageType == "forum":
                # Forum case
                # ----------
                # -> pageHdl is a Forum ID
                
                # on recherche d'abord les forums
                forums = NABBOX.get_forums(html)
                
                # puis on cherche les topics du salon
                topics = NABBOX.get_topics(html)
                
                # Now we got the info -> Clear the lists: display / handler / type
                self.currentdisplayList  = []
                self.currentHandlerList  = []
                self.currentLinkTypeList = []
                
                # and now we can process data the way we need
                # -> forums
                for IDforum,forumTitle, forumDesc in forums:
                    #print "%s : %s\n\t%s"%(IDforum,forumTitle,forumDesc)

                    # Building dictionnary
                    params              = {}
                    params["s"]         = self.sessionID # Adding session ID to the dictionnary
                    params["showforum"] = IDforum        # We load forum directly from capture TV forum (id=46)

                    #label = NABBOX.unescape(forumTitle) + "\n" + NABBOX.unescape(forumDesc)
                    label = forumTitle + "\n" + forumDesc
                    self.currentdisplayList.append(label)       # adding forum title
                    #self.currentHandlerList.append(IDforum)    # adding handler (here the forum ID)
                    self.currentHandlerList.append(params)      # adding handler (here params for the forum ID)
                    self.currentLinkTypeList.append("forum")    # adding type of hander / linked page
                
                # -> topics
                for topicID,titretopic in topics:
                    #print "%s (%s)"%(topicID,titretopic)

                    # Building dictionnary
                    params              = {}
                    params["s"]         = self.sessionID # Adding session ID to the dictionnary
                    params["showtopic"] = topicID        # In order to get a Topic, showtopic key has to set with the Topic ID in the dictionary

                    #label = NABBOX.unescape(titretopic)
                    label = NABBOX.unescape(titretopic)
                    self.currentdisplayList.append(label)       # adding topic title
                    #self.currentHandlerList.append(topicID)    # adding handler (here the forum ID)
                    self.currentHandlerList.append(params)      # adding handler (here params for the Topic ID)
                    self.currentLinkTypeList.append("topic")    # adding type of hander / linked page
                
            elif pageType == "topic":
                # Topic case
                # ----------
                
                # Looking for links within the Topic
                liens = NABBOX.get_liens(html)     
                
                # Now we got the info -> Clear the lists: display / handler / type
                self.currentdisplayList  = []
                self.currentHandlerList  = []
                self.currentLinkTypeList = []
                
                # get_liens(html) return either :
                #   -1: if Topic DOES NOT have any link (even hidden)
                #   -2: if Topic HAS links but HIDDEN
                #   Link list if Topic get an answer
                if liens==-2:
                    #print "We need to send an answer (thank you message) in order to get the link"
                    
                    # We retrieve the dictionnary
                    params = pageHdl
            
                    # Get Forum ID and Topic ID of current page in order to sent a message
                    curForumID, currentTopicID = NABBOX.get_param_answer(html)
                    
                    # Make and answer for Thank message :
                    NABBOX.make_answer(self.sessionID,curForumID,params["showtopic"],self.thanks,savehtml=self.cachepages) 
                    #print "Answer sent..."
                    
                    # Load the page 
                    #print "Getting links ..."
                    html  = self.loadPage(pageHdl, pageType)
                    liens = NABBOX.get_liens(html)
                    
                    # Thanks to the answer, here are the links, voici les liens :"
                    for lien in liens:
                        #print lien
                        label = NABBOX.unescape(os.path.basename(lien))
                        #print "label %s"%label
                        self.currentdisplayList.append(label)                   # For time being we display the full path of the video #TODO: name of video to send
                        self.currentHandlerList.append(lien)                    # adding handler (here video link)
                        self.currentLinkTypeList.append("liensVideo")           # adding type of hander / linked page (-> video)
                        
                elif liens==-1:
                    #print "Not links in the topic, you need to chose another one"
                    pass
                else:
                    for lien in liens:
                        #print lien
                        label = NABBOX.unescape(os.path.basename(lien))
                        #print "label %s"%label
                        self.currentdisplayList.append(label)
                        self.currentHandlerList.append(lien)
                        self.currentLinkTypeList.append("liensVideo")
                    #print "Links are availble and can be used"
        else:
            print"Retry failed: Connection impossible, please check your connection and account settings"
            print "NOT CONNECTED"
            # Clear the lists
            self.currentdisplayList  = []
            self.currentHandlerList  = []
            self.currentLinkTypeList = []
        #print
        #print "updateData - self.currentdisplayList:"
        #print self.currentdisplayList
        #print "self.currentHandlerList:"
        #print self.currentHandlerList
        #print "updateData - self.currentLinkTypeList:"
        #print self.currentLinkTypeList
        #print "updateData - self.currentConnecStatus:"
        #print self.currentConnecStatus
            
        # Return status of connection (which mean success or not)
        return self.currentConnecStatus
        
    def getFileSize(self, source):
        """
        get the size of the file (in octets)
        """
        connection  = urllib2.urlopen(source)
        headers     = connection.info()
        file_size   = int(headers['Content-Length'])
        connection.close()
        return int(file_size)
#        file = urllib.urlopen(source)
#        size = file.headers.get("content-length")
#        file.close()
#        return int(size)

    def downloadFile(self, source, destination,msgFunc=None,progressBar=None):
        """
        Download a file at a specific URL and send event to registerd UI if requested
        """
        print("downloadFile with source = " + source)
        print("downloadFile with destination = " + destination)
        #print "msgFunc:"
        #print msgFunc
        #print "progressBar:"
        #print progressBar
        
        msgType    = ""
        msgTite    = ""
        msg1       = ""
        msg2       = ""
        msg3       = ""
        filename   = os.path.basename(source) # Extracting filename from full path
        downloadOK = False
        noErrorOK  = True # When noErrorOK == True -> no error/Exception occured
               
        if self.dowldInProgress == True:
            print("downloadFile a download is already in progress")
            downloadOK = False
            # Prepare message to the UI
            msgType = "OK"
            msgTite = "Nabbox Téléchargement"
            msg1    = "Un Téléchargement est dejà en cours"
            msg2    = "Afin de pouvoir démarrer ce téléchargement vous devez"
            msg3    = "terminer ou stopper le téléchargement en cours"
        
            # Send the message to the UI in order to get decision form user
            try:
                if (msgFunc != None):
                    msgFunc(msgType, msgTite, msg1,msg2, msg3)
            except Exception, e:        
                print("downloadFile - Exception calling UI callback for 'Un Téléchargement est deja en cours' message")
                print(str(e))
                print msgFunc
            
        elif os.path.exists(destination):
            print("downloadFile destination already exist")
            print("downloadFile ENDED")

            # Prepare message to the UI
            msgType = "YESNO"
            msgTite = "Nabbox Téléchargement"
            msg1    = "Ce fichier existe dejà dans le répertoire:"
            msg2    = "%s"%DOWNLOADDIR
            msg3    = "Voulez le re-télécharger et écraser le fichier existant?"
        
            # Send the message to the UI in order to get decision form user
            try:
                if (msgFunc != None):
                    if msgFunc(msgType, msgTite, msg1,msg2, msg3):
                        downloadOK = True
            except Exception, e:        
                print("downloadFile - Exception calling UI callback for message")
                print(str(e))
                print msgFunc
        else:
            print("downloadFile destination doesn't exist -> gonna start download")
            downloadOK = True
        
        if downloadOK == True:
            try:
                # -- Downloading
                print("downloadFile - Trying to retrieve the file")
                block_size          = 4096
                percent_downloaded  = 0
                num_blocks          = 0
                
                # Update 'Download in Progress' state
                self.dowldInProgress = True
                retry                = 3
                
                if self.displayProgBar == True:
                    req = urllib2.Request(source)
                    req.add_header('User-Agent','Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.3) Gecko/20070309 Firefox/2.0.0.3')
                    connection  = urllib2.urlopen(req)           # Open connection
                    headers     = connection.info()              # Get Headers
                    file_size   = int(headers['Content-Length']) # Read Size from headers
                    print "downloadFile - file size : %d Octet(s)"%file_size
                    
                    # Get free space on the drive
                    print "Free space"
                    print xbmc.getInfoLabel('System.Freespace')
                    freespace_size = int((xbmc.getInfoLabel('System.Freespace')).split(' ')[1])*1024*1024
                    
                    print "downloadFile - Free space availbale : %d Octet(s)"%freespace_size
    
                    #TODO: check issue on download on XBOX
                    #TODO: Check space available format on every platform
                    #if file_size < freespace_size:
                    if True:
                        file = open(destination,'w+b')        # Get ready for writing file
                        # Ask for display of progress bar
                        try:
                            if (progressBar != None):
                                progressBar.update(percent_downloaded)
                        except Exception, e:        
                            print("downloadFile - Exception calling UI callback for download")
                            print(str(e))
                            print progressBar
                            
                        ###########
                        # Download
                        ###########
                        while 1:
                            if (progressBar != None):
                                if progressBar.iscanceled():
                                    #self.dowldInProgress = False
                                    print "Downloaded STOPPED by the user"
                                    break
                            try:
                                cur_block  = connection.read(block_size)
                                if not cur_block:
                                    break
                                file.write(cur_block)
                                # Increment for next block
                                num_blocks = num_blocks + 1
                            except Exception, e:        
                                print("downloadFile - Exception during reading of the remote file and writing it locally")
                                print(str(e))
                                print ("error during reading of the remote file and writing it locally: " + str(sys.exc_info()[0]))
                                traceback.print_exc()
                                noErrorOK  = False
                                # End of writing: Closing the connection and the file
                                connection.close()
                                file.close()
                                raise e
                            try:
                                # Compute percent of download in progress
                                New_percent_downloaded = min((num_blocks*block_size*100)/file_size, 100)
                                #print "downloadFile - Percent = %d"%New_percent_downloaded
                            except Exception, e:        
                                print("downloadFile - Exception computing percentage downloaded")
                                print(str(e))
                                noErrorOK  = False
                                # End of writing: Closing the connection and the file
                                connection.close()
                                file.close()
                                raise e
                            # We send an update only when percent number increases
                            if (New_percent_downloaded > percent_downloaded):
                                percent_downloaded = New_percent_downloaded
                                #print ("downloadFile - Downloaded %d %%"%percent_downloaded)
                                # Call UI callback in order to update download progress info
                                if (self.displayProgBar == True):
                                    progressBar.update(percent_downloaded)
                        # Closingthe file
                        file.close()

                        # Prepare message to the UI
                        msgType = "OK"
                        msgTite = "Nabbox Téléchargement"
                        msg1    = filename
                        msg2    = "%d%% terminé. Le fichier disponible dans:"%(percent_downloaded)
                        msg3    = "%s"%DOWNLOADDIR
                    else:
                        # Prepare message to the UI
                        msgType = "OK"
                        msgTite = "Nabbox Téléchargement"
                        msg1    = "Il n'y a pas assez d'espace disponible sur le disque dur pour:"
                        msg2    = filename
                        msg3    = "Veuillez faire de l'espace"
                    # End of writing: Closing the connection and the file
                    connection.close()
                else:
                    print "downloadFile - *** using urlretrieve method ***"
                    try:
                        #urllib.urlretrieve(source,destination)
                        urllib.urlretrieve(source,destination,lambda nb, bs, fs, url=source: self._pbhook(nb,bs,fs,url,progressBar))
                    except cancelRequest:
                    #except IOError, (errno, strerror):
                        traceback.print_exc(file = sys.stdout)
                        print "Downloaded STOPPED by the user"
                    except Exception, e:
                        traceback.print_exc(file = sys.stdout)
                        print "=============================================="        
                        print("downloadFile - Exception during urlretrieve")
                        print(e)
                        noErrorOK == False
                        urllib.urlcleanup()
                        raise e
                    urllib.urlcleanup()
                    # Prepare message to the UI
                    msgType = "OK"
                    msgTite = "Nabbox Téléchargement"
                    msg1    = filename
                    msg2    = "Téléchargement terminé. Le fichier disponible dans:"
                    msg3    = "%s"%DOWNLOADDIR
                    percent_downloaded = 0
            except Exception, e:
                print("Exception while source retrieving")
                print(str(e))
                print ("error while source retrieving: " + str(sys.exc_info()[0]))
                traceback.print_exc()
                print("downloadFile ENDED with ERROR")

                # Prepare message to the UI
                msgType = "Error"
                msgTite = "Nabbox Téléchargement - Erreur"
                msg1    = filename
                msg2    = "%d%% Téléchargement terminé. Une erreur s'est produite durant le téléchargement du fichier"%(percent_downloaded)
                msg3    = "Erreur: %s"%e

                
            # Stop download
            self.dowldInProgress = False

            # Check if we end the loop because user stopped download in progress
            if (progressBar != None):
                if (progressBar.iscanceled() or noErrorOK == False) :
                    incompleteFileName = xbmc.makeLegalFilename(destination + "_part")
                    #incompleteFileName = "incomplete" + "_part"
                    print "Incomplte download -> replacing %s by %s"%(destination,incompleteFileName)
                    # Check if an incomplete file with the same same is already here
                    if os.path.exists(incompleteFileName):
                        # And delete it
                        os.remove(incompleteFileName)
                    # Rename partially dowmloaded file
                    rename_attempt=5 # Max Retries 
                    while rename_attempt:
                            try:
                                os.rename(destination,incompleteFileName)
                                rename_attempt = 0 # Succes so we can leave the loop
                            except:
                                rename_attempt = rename_attempt -1 
                                print "Attempt N %d"%rename_attempt
                                time.sleep(1)            
            
            print("downloadFile ENDED")

                                
            # Close/Reset progress bar
            progressBar.close()
            
            # Send the message to the UI
            try:
                if (msgFunc != None):
                    msgFunc(msgType, msgTite, msg1,msg2, msg3)
            except Exception, e:        
                print("downloadFile - Exception calling UI callback for message")
                print(str(e))
                print msgFunc
                
    def _pbhook(self,numblocks, blocksize, filesize, url=None,dp=None):
        """
        Hook function for progress bar
        Inspired from the example on xbmc.org wiki
        """
#        try:
#            percent = min((numblocks*blocksize*100)/filesize, 100)
#            print "_pbhook - percent = %s%%"%percent
#            dp.update(percent)
#        except Exception, e:        
#            print("_pbhook - Exception during percent computing AND update")
#            print(e)
#            percent = 100
#            dp.update(percent)
        if dp.iscanceled(): 
            print "_pbhook: DOWNLOAD CANCELLED" # need to get this part working
            #dp.close() #-> will be calose in calling function
            #raise IOError
            raise cancelRequest,"User pressed CANCEL button"


    def isDownloadInProgress(self):
        """
        Return True is a download is in progress, False otherwise
        """                
        return self.dowldInProgress
        
    def loadvideo(self, videoURL, save=False, msg_cb=None, progBar=None):
        """
        play video
        #TODO: Move in a better place the use of this function
        """
        #TODO: move to file manager
        
        #print "getDisplayLists - liensVideo case"
        # We are going to play video here so we don't change any display list 
        # (we want user back to the video list after a video play)
        
        # Check if download or play
        if (save == False):
            # Play the selected video
            print("Play the selected video: " + videoURL)
            xbmc.Player(playerSelect[self.defaultPlayer]).play(videoURL)
        else:
            print("Save the selected video: " + videoURL)
            # Download the file in Download directory
            localFile = xbmc.makeLegalFilename(os.path.join(DOWNLOADDIR,os.path.basename(videoURL)))
            #localFile = xbmc.translatePath(os.path.join(DOWNLOADDIR,os.path.basename(videoURL)))
            self.downloadFile(videoURL,localFile,msgFunc=msg_cb,progressBar=progBar)

    def loadPage(self, pageHdl, pageType):
        """
        Load a page and return html page
        A session has to be opened before calling this function otherwise, it will fail
        """
        #TODO: Add here test on self.sessionID, return empty html if no session
        if pageType == "index":
            #print "loadPage - index case"
            
            # we retrieve the dictionnary
            params      = pageHdl
            params["s"] = self.sessionID # update session ID param with the last value known
            
            # on télécharge la page du forum général
            html = NABBOX.get_page(params,savehtml=self.cachepages,filename="accueil.html")
            
        elif pageType == "forum":
            #print "loadPage - forum case"
                       
            # we retrieve the dictionnary
            params      = pageHdl
            params["s"] = self.sessionID # update session ID param with the last value known
            
            # on télécharge la page du salon
            html = NABBOX.get_page(params,savehtml=self.cachepages,filename="forum %s.html"%params["showforum"])
            
            
        elif pageType == "topic":
            #print "loadPage - topic case"
                       
            # we retrieve the dictionnary
            params      = pageHdl
            params["s"] = self.sessionID # update session ID param with the last value known
             
            # une fois le paramètre showtopic configuré on télécharge la page comme suit
            html = NABBOX.get_page(params,savehtml=self.cachepages,filename="topic %s.html"%params["showtopic"]) #on récupère la page
            
        return html
        
        
    def getDownloadPage(self):
        """
        Update data with Download directory information (used by the UI)
        returns True if OK, False otherwise
        """
        # Set flag indicating current page is an history or download page (same case between history and dowmload page)
        self.localpageisactive = True

        # Result
        retval = False

        # Now we got the info -> Clear the lists: display / handler / type
        self.currentdisplayList  = []
        self.currentHandlerList  = []
        self.currentLinkTypeList = []
        
        
        for filename in self.fileMgr.listDirFiles(DOWNLOADDIR):
            #label = NABBOX.unescape(forumTitle) + "\n" + NABBOX.unescape(forumDesc)
            self.currentdisplayList.append(filename)                            # adding file name 
            self.currentHandlerList.append(os.path.join(DOWNLOADDIR,filename))  # adding handler (here file path)
            self.currentLinkTypeList.append("file")                             # adding type of hander / linked page
        # Update page number
        self.currentPage_str = "1/1"

        # Update next and previous page handlers
        self.currentNextPageHdl = None
        self.currentPrevPageHdl = None
        
        # Update Title
        self.currentTitleLabel = "Téléchargements"       
        
        retval = True
        
        # Return code (success or failure)
        return retval
        
    def getHistoryPage(self):
        """
        Update data with History information (used by the UI)
        returns True if OK, False otherwise
        """
        # Set flag indicating current page is an history page
        self.localpageisactive = True
        
        # Result
        retval = False

        # Copy the info from the history instance : display / handler / type
        self.currentdisplayList  = self.history.titleLabel
        self.currentHandlerList  = self.history.handler
        self.currentLinkTypeList = self.history.handlerType

        # Update page number
        self.currentPage_str = "1/1"

        # Update next and previous page handlers
        self.currentNextPageHdl = None
        self.currentPrevPageHdl = None
        
        # Update Title
        self.currentTitleLabel = "Historique"       
        
        retval = True
        
        # Return code (success or failure)
        #TODO: case of NOT CONNECTED
        return retval


    def getPreviousHistPage(self):
        """
        Update data with previous page information (used by the UI)
        returns True if OK, False otherwise
        """
        # Result
        retval = False
        
        # Check is history page is currently displayed
        if (self.localpageisactive == False):
            #print "Local Page is NOT ACTIVE - removing last entry"
            # delete current page from history (we are going to load the previous one)
            self.history.pop()
        else:
            # History page is display so we want to display last page stored (before calling history display)

            # reset flag for next time 
            #print "Local Page is ACTIVE - deactivating ..."
            self.localpageisactive = False

        # Get previous entry (the one we gonna reload) but since we did a pop this is the current
        #previousIndex, previousHdl, previousHdlType, previousTitleLabel = self.history.getPrevious()
        previousTitleLabel,previousHdl, previousHdlType = self.history.getCurrent()
        
        # Now we can update internal lists with previous page information (which we will return)
        retval = self.updateData(previousHdl, previousHdlType)

        # Return code (success or failure)
        #TODO: case of NOT CONNECTED
        return retval
        
        
    def getNewPageWithIdx(self, index=0):
        """
        Update data with a new page information using an index as parameter (used by the UI)
        returns True if OK, False otherwise
        """
        # Result
        retval = False
        
        # We retrieve handler and page type
        pageHdl     = self.currentHandlerList[index]
        pageHdlType = self.currentLinkTypeList[index]
        
        if self.currentLinkTypeList[index]  == "liensVideo":
            #TODO: move video playing in a better place
            #print "getNewPage -  - liensVideo CASE"
            # We are going to play video here so we don't change any display list 
            # (we want user back to the video list after a video play)
            
            # Get video URL
            vidURL = str(self.currentHandlerList[index])
            print "getNewPage - vidURL:"
            print (vidURL)

            # Load video
            self.loadvideo(vidURL)

            retval = True

        elif self.currentLinkTypeList[index]  == "file":
            #TODO: move video playing in a better place
            #print "getNewPage -  - liensVideo CASE"
            # We are going to play video here so we don't change any display list 
            # (we want user back to the video list after a video play)
            
            # Get video PATH
            vidPath = str(self.currentHandlerList[index])

            # Load video
            self.loadvideo(vidPath)

            retval = True
        else:
            # Get new page and update history
            retval = self.getNewPageWithHdl(pageHdl, pageHdlType, True)
                    
        # Return code (success or failure)
        #TODO: case of NOT CONNECTED
        return retval



    def getNewPageWithHdl(self, pageHdl,pageType,updateHist=True):
        """
        Update data with a page information using an handler an page type as paramter (used by the UI)
        Page is added to history or not according updateHist
        returns True if OK, False otherwise
        """
        # Result
        retval = False
        
        # Now we can update internal lists page information (which we will return)
        retval = self.updateData(pageHdl, pageType)
        
        if (updateHist == True):
            # add to history
            self.history.push(self.currentTitleLabel,pageHdl,pageType)
                
        # Return code (success or failure)
        #TODO: case of NOT CONNECTED
        return retval


    def getReloadPage(self):
        """
        Reaload  and update data with a Current page information using if it exists (used by the UI)
        Page is not added to history
        returns True if OK, False otherwise
        """

        # Get current entry (in order to get retrieve the type)
        curTitle, curHdl, curHdlType = self.history.getCurrent()

        # Get current page WITHOUT history update
        retval = self.getNewPageWithHdl(curHdl, curHdlType, False)
            
        # Return code (success or failure)
        #TODO: case of NOT CONNECTED
        return retval


    def getNextPage(self):
        """
        Update data with a Next page information using if it exists (used by the UI)
        returns True if OK, False otherwise
        """
        
        # Result
        retval = False
        
        # Check if a next page exists
        if (self.currentNextPageHdl != None):
            #print "Next page exists"
            
            # Get current entry (in order to get retrieve the type)
            curTitle, curHdl, curHdlType = self.history.getCurrent()
            
            # Get Next page and update history
            retval = self.getNewPageWithHdl(self.currentNextPageHdl, curHdlType, True)
                    
        # Return code (success or failure)
        #TODO: case of NOT CONNECTED
        return retval
        
    def getPrevPage(self):
        """
        Update data with a Previous page (from website not history) information if it exists (used by the UI)
        returns True if OK, False otherwise
        """
        
        # Result
        retval = False
        
        # Check if a next page exists
        if (self.currentPrevPageHdl != None):
            #print "Next page exists"
            
            # Get current entry (in order to get retrieve the type)
            curTitle, curHdl, curHdlType = self.history.getCurrent()
            
            # Get Next page and update history
            retval = self.getNewPageWithHdl(self.currentPrevPageHdl, curHdlType, True)
                    
        # Return code (success or failure)
        #TODO: case of NOT CONNECTED
        return retval
        
class history:
    """
    Class history save history of webpage browsed
    in the future we can even cache here all the page info including lists
    """
    def __init__(self):
        self.handler        = []
        self.handlerType    = []
        self.titleLabel     = []
        self.current        = - 1
        
    def push(self, title, hdl, hdlType):
        """
        Add a webpage to history
        @param title:
        @param hdl:
        @param hdlType:
        """
        self.handler.append(hdl)
        self.handlerType.append(hdlType)
        self.titleLabel.append(title)
        self.current = self.current + 1
        
    def pop(self):
        """
        Remove a webpage from 
        """
        if self.current >= 0:
            self.handler.pop()
            self.handlerType.pop()
            self.titleLabel.pop()
            self.current = self.current - 1
        else:
            print "history: History already empty!!! - cannot do pop"
            
    def getCurrent(self):
        """
        Returns current page info (index / Handler / Handler Type) on succes
                or "None" if failure (no current page)
        """
        if self.current >= 0:
            return self.titleLabel[self.current],self.handler[self.current], self.handlerType[self.current]
        else:
            return "None", "None", "None"
            
    def getPrevious(self):
        """
        Returns previous page info (index / Handler / Handler Type) on succes
                or "None" if failure (no previous page)
        """
        if (self.current - 1) >= 0:
            return self.titleLabel[(self.current - 1)], self.handler[(self.current - 1)], self.handlerType[(self.current - 1)]
        else:
            return "None", "None", "None"

    def getEntry(self, index):
        """
        Returns an history entry for a specific Index
        @param index: history entry index 
        """
        return self.titleLabel[index], self.handler[index], self.handlerType[index]
        
    def getHistoryTitle(self):
        """
        Returns list ot Titles stored in history
        """
        return self.titleLabel
        

class HelpWindow(xbmcgui.WindowDialog):
    """
    Information Window
    """
    def __init__(self):
        if Emulating: xbmcgui.Window.__init__(self)
        if not Emulating:
            self.setCoordinateResolution(PAL_4x3) # Set coordinate resolution to PAL 4:3

        # Background image
        self.addControl(xbmcgui.ControlImage(100,100,545,435, os.path.join(IMAGEDIR,"dialog-panel.png")))

        self.strTitle = xbmcgui.ControlLabel(130, 110, 350, 30, "AIDE NABBOX",'special13')
        self.addControl(self.strTitle)
        self.helpTextBox = xbmcgui.ControlTextBox(130, 140, 540-70, 350, font="font10", textColor='0xFFFFFFFF')
        self.addControl(self.helpTextBox)
        self.helpTextBox.setVisible(True)
        self.setFocus(self.helpTextBox)
         
        # Code copied form Navix-X - Thanks!
        try:            
            helpfile=open(os.path.join(ROOTDIR,"NABBOX_Aide.txt"), 'r')
            data = helpfile.read()
            helpfile.close()
            text=""
            lines = data.split("\n")
            #we check each line if it exceeds 70 characters and does not contain
            #any space characters (e.g. long URLs). The textbox widget does not
            #split up these strings. In this case we add a space characters ourself.
            for m in lines:
                if (len(m) > 70) and (m.find(" ") == -1):
                    m = m[:70] + " " + m[70:]
                text = text + m + "\n"
            self.helpTextBox.setText(text)
        except IOError:
            print "Help File does not exist!"         
            dialogError = xbmcgui.Dialog()
            dialogError.ok("Aide Nabbox", "le fichier d'aide %s n'a pas été trouvé"%"NABBOX_Aide.txt")
            self.helpTextBox.setText("Impossible de trouve le fichier d'aide %s"%"NABBOX_Aide.txt")
        self.doModal()


class InfoWindow(xbmcgui.WindowDialog):
    """
    Information Window
    """
    def __init__(self):
        if Emulating: xbmcgui.Window.__init__(self)
        if not Emulating:
            self.setCoordinateResolution(PAL_4x3) # Set coordinate resolution to PAL 4:3

        # Background image
        print ("Get Background image from : " + os.path.join(IMAGEDIR,"dialog-panel.png"))
        self.addControl(xbmcgui.ControlImage(100,100,545,435, os.path.join(IMAGEDIR,"dialog-panel.png")))

        self.strTitle = xbmcgui.ControlLabel(130, 110, 350, 30, "NABBOX",'special13')
        self.addControl(self.strTitle)
        self.strVersion = xbmcgui.ControlLabel(130, 150, 350, 30, "Version: " + version)
        self.addControl(self.strVersion)
        self.strAuthor = xbmcgui.ControlLabel(130, 190, 350, 30, "Auteurs: ")
        self.addControl(self.strAuthor)        
        self.strAuthorCore = xbmcgui.ControlLabel(160, 210, 350, 30, "- Interface graphique: " + authorUI)
        self.addControl(self.strAuthorCore)
        self.strAuthorUI = xbmcgui.ControlLabel(160, 230, 350, 30, "- Noyau: " + authorCore)
        self.addControl(self.strAuthorUI)
        self.strDesTitle = xbmcgui.ControlLabel(130, 270, 350, 30, "Description: ")
        self.addControl(self.strDesTitle)        
        self.strDesContent = xbmcgui.ControlLabel(130, 290, 490, 100, """Ce script vous permet de vous connecter via un compte(gratuit) sur le forum 
'www.nabbox.com'qui met en ligne des captures TV de videos en tout genre
(émissions TV francaises pour la plupart).
Le script NABBOX vous permet de naviguer sur le forum et met a disposition
les liens des videos que vous pourrez voir et/ou télécharger via XBMC.
N'oubliez pas d'aller régulierement sur 'www.nabbox.com' et de remercier
les Capseurs pour leur formidable travail.""", "font10")
        self.addControl(self.strDesContent)        
        self.strIdea = xbmcgui.ControlLabel(130, 430, 350, 30, "Script créé sur une idée originale de Roots66")
        self.addControl(self.strIdea)        
        self.strThanks = xbmcgui.ControlLabel(130, 470, 480, 60, "Merci aux membres de passion-xbmc.org pour leur aide et leur support")
        self.addControl(self.strThanks)        
        
        self.doModal()


class DropDownMenu(xbmcgui.WindowDialog):
    """
    Drop-Down Menu window
    """
    def __init__(self): #TODO: support all arg of controlButton
        """
        init
        """
        if Emulating: xbmcgui.Window.__init__(self)
        if not Emulating:
            self.setCoordinateResolution(PAL_4x3) # Set coordinate resolution to PAL 4:3
            
        # Create a result variable
        self.result = -1
            
            
    def onAction(self, action):
        if action == ACTION_PREVIOUS_MENU:
            # previous menu action recieved, set result to 0 (cancel / aborted) and close the window
            self.result = -1
            self.close()
            
    def onControl(self, control):
        if control == self.menuoptionlist:
            self.result = self.menuoptionlist.getSelectedPosition()
            self.close()
            
    def getSelect(self,refX, refY, refWidth, refHeight, menWidth, menItemHeight, relPosition, menList, direction="Down"):
        """
        Get selected item index in the list
        @param refX:
        @param refY:
        @param refWidth:
        @param refHeight:
        @param menWidth:
        @param menItemHeight:
        @param relPosition:
        @param menList: List of string d
        @param direction:
        """

        self.menuWidth  = menWidth
        self.menuHeight = menItemHeight * len(menList)
        self.menuList   = menList
                
        if relPosition == 'Right':
            #print "relPosition : Right"
            self.menuX = refX + refWidth
            self.menuY = refY 
            
        elif relPosition == 'Left':
            #print "relPosition : Left"
            self.menuX = refX - refWidth
            self.menuY = refY 
            
        elif relPosition == 'Up':
            #print "relPosition : Up"
            self.menuX = refX
            self.menuY = refY
            
        elif relPosition == 'Down':
            #print "relPosition : Down"
            self.menuX = refX
            self.menuY = refY + refHeight
        else:
            print"Invalid relPosition parameter " #TODO: Rise execption

        # Background image
        self.addControl(xbmcgui.ControlImage(self.menuX, self.menuY-2, self.menuWidth+4 , self.menuHeight+4, os.path.join(IMAGEDIR,"menu-focus.png")))
        # Set the control list of the menu
        #TODO: CHECK WHY WE NEED TO ADD menItemHeight on the HEIGHT
        self.menuoptionlist = xbmcgui.ControlList(self.menuX+2, self.menuY, self.menuWidth , self.menuHeight + menItemHeight,'font14','0xFF000000', buttonTexture = os.path.join(IMAGEDIR,"list-forum.png"),buttonFocusTexture = os.path.join(IMAGEDIR,"list-background.png"), itemTextXOffset=0, space=0, itemHeight=menItemHeight)
        self.addControl(self.menuoptionlist)
        for menu in self.menuList:
            displayMenuOptItem = xbmcgui.ListItem(label = menu)
            self.menuoptionlist.addItem(displayMenuOptItem)

        # Set focus on the list
        self.setFocus(self.menuoptionlist)
        
        # show this menu and wait until it's closed
        self.doModal()
        return self.result
    
class backProgressBar:
    """
    Background progress bar
    This progress bar contrary to xbmcgui dialogprogress is display in the main window
    (it uses MainWindow Control) and does not block the user from using the interface
    """
    def __init__(self,labelTitle, lableTitleMaxSize, labelPercent,imageFrontProgBar,imageBackProgbar,uiLockMgr):
        """
        Create a progress bar in the background
        """
        self.labelTitle         = labelTitle        # Contol Label
        self.lableTitleMaxSize  = lableTitleMaxSize # Max size of scrolling text
        self.labelPercent       = labelPercent      # Contol Label
        self.imageFrontProgBar  = imageFrontProgBar # Contol Image
        self.imageBackProgbar   = imageBackProgbar  # Contol Image
        self.cancel             = False
        self.uiLockMgr          = uiLockMgr
        
        # Get Width of the progress bar
        self.barWidth       = imageFrontProgBar.getWidth()
        
    def cancelAction(self):
        """
        Set cancel state to True
        """
        print "backProgressBar; cancel"
        self.cancel = True
        
    def close(self):
        """
        Close the progress dialog
        """
        self.labelTitle.setVisible(False)
        self.imageFrontProgBar.setVisible(False)
        self.imageBackProgbar.setVisible(False)
        self.labelPercent.setLabel("0%%")
        self.labelPercent.setVisible(False)
        self.cancel = False
        self.labelTitle.reset()
        
    def create(self,heading=None, line1=None, line2=None, line3=None):
        """
        open/show the progress bar in the background
        """
        #TODO: Case of download already in progress: we don't want to overwrite the title!
        print "backProgressBar; create"
        startTitle = "Téléchargement"
        startTitle = startTitle.center(self.lableTitleMaxSize)
        self.labelTitle.addLabel(startTitle)
        if heading != None:
            heading    = heading.center(self.lableTitleMaxSize)
            self.labelTitle.addLabel(heading)
            
        self.labelTitle.setVisible(True)      
        self.cancel = False

    def iscanceled(self):
        """
        Returns True if the user pressed cancel
        """
        #print "backProgressBar: iscanceled() : %s"%self.cancel
        return self.cancel
        
    def update(self,percent):
        """
        Update the progress bar
        """
        #print "backProgressBar: update: %s%%"%percent
        uiJob = False
        
        if (self.uiLockMgr.isWindowlocked()):
            uiJob = True
        if (uiJob == True):
            self.uiLockMgr.unlockWindow()
        if (percent == 0):
            #self.labelTitle.setLabel("Téléchargement")
            self.labelPercent.setLabel("%s%%"%percent)
            #self.labelTitle.setVisible(True)
            self.imageBackProgbar.setVisible(True)
            self.labelPercent.setVisible(True)
        elif (percent == 1):
            # We only start to display the progress bar at 1%
            self.labelPercent.setLabel("%s%%"%percent)
            self.imageFrontProgBar.setWidth(percent)
            self.imageFrontProgBar.setVisible(True)
        else:
            # Compute size we need to add to the image of the bar
            currentWidth = (percent * self.barWidth)/100
            self.labelPercent.setLabel("%s%%"%percent)
            self.imageFrontProgBar.setWidth(currentWidth)
        if (uiJob == True):
            self.uiLockMgr.lockWindow()
        
class guiCtrl:
    """
    Manage the user interface
    """
    def __init__(self):
        """
        """
        # Window loack status
        self.windowLock = False
        
    def lockWindow(self):
        """
        Lock UI and update internal state value
        """
        # Lock UI before changes
        xbmcgui.lock()
        self.windowLock = True
        
    def unlockWindow(self):
        """
        Unlock UI and update internal state value
        """
        # Unlock UI before changes
        xbmcgui.unlock()
        self.windowLock = False

    def isWindowlocked(self):
        """
        Return True is UI is locked
        """
        return  self.windowLock
        
        
        
class MainWindow(xbmcgui.Window):
    def __init__(self):
        """
        Main Window Init 
        """
        if Emulating: xbmcgui.Window.__init__(self)
        if not Emulating:
            self.setCoordinateResolution(PAL_4x3) # Set coordinate resolution to PAL 4:3
                   
        # Create a gui controler in order to manage lock/unlock of the UI
        self.guiCtrl = guiCtrl()
        
        # Size maxi of scrolling text message
        self.scrollingSizeMax = 350
        
        # Display List size -> maxi number of element we can see in the list
        self.displayListSize = 6
        
        # Display Loading Window while we are loading the information from the website
        dialogUI = xbmcgui.DialogProgress()
        dialogUI.create("NABBOX", "Creation de l'interface Graphique", "Veuillez patienter...")
        
        # Create browser instance
        self.nabboxBrowser = browser()
        
        # Background image
        self.addControl(xbmcgui.ControlImage(0,0,720,576, os.path.join(IMAGEDIR,"background.png")))
        
        # Reload button a the top
        self.buttonReload = xbmcgui.ControlButton(20, 117, 85, 25, "Recharger", focusTexture = os.path.join(IMAGEDIR,"menu-focus.png"), noFocusTexture  = os.path.join(IMAGEDIR,"list-forum.png"), alignment=6)
        self.addControl(self.buttonReload)
        
        # History button a the top
        self.buttonHist = xbmcgui.ControlButton(110, 117, 85, 25, "Historique", focusTexture = os.path.join(IMAGEDIR,"menu-focus.png"), noFocusTexture  = os.path.join(IMAGEDIR,"list-forum.png"), alignment=6)
        self.addControl(self.buttonHist)
        
        # Download button a the top
        self.buttonDld = xbmcgui.ControlButton(200, 117, 85, 25, "Download", focusTexture = os.path.join(IMAGEDIR,"menu-focus.png"), noFocusTexture  = os.path.join(IMAGEDIR,"list-forum.png"), alignment=6)
        self.addControl(self.buttonDld)
        
        # Menu option buttons a the top
        self.buttonOptions = xbmcgui.ControlButton(290, 117, 85, 25, "Options", focusTexture = os.path.join(IMAGEDIR,"menu-focus.png"), noFocusTexture  = os.path.join(IMAGEDIR,"list-forum.png"), alignment=6)
        self.addControl(self.buttonOptions)
        
        # Help button a the top
        self.buttonHelp = xbmcgui.ControlButton(380, 117, 85, 25, "Aide", focusTexture = os.path.join(IMAGEDIR,"menu-focus.png"), noFocusTexture  = os.path.join(IMAGEDIR,"list-forum.png"), alignment=6)
        self.addControl(self.buttonHelp)
        
        # Set List border image
        self.listborder = xbmcgui.ControlImage(20,150,680,416, os.path.join(IMAGEDIR, "list-forum.png"))
        self.addControl(self.listborder)
        self.listborder.setVisible(True)
        
        # Set List background image
        self.listbackground = xbmcgui.ControlImage(23, 193, 674, 340, os.path.join(IMAGEDIR, "list-white.png"))
        self.addControl(self.listbackground)
        self.listbackground.setVisible(True)
        
        # Set List hearder image
        self.header = xbmcgui.ControlImage(23,153,674,40, os.path.join(IMAGEDIR, "list-header.png"))
        self.addControl(self.header)
        self.header.setVisible(True)
        
        # Arrow up image (for list browsing)
        self.arrowUp = xbmcgui.ControlImage(684,180,13,13, os.path.join(IMAGEDIR,"ArrowUp.png"))
        self.addControl(self.arrowUp)
        self.arrowUp.setVisible(False)
        
        # Arrow down image (for list browsing)
        self.arrowDown = xbmcgui.ControlImage(684,537,13,13, os.path.join(IMAGEDIR,"ArrowDown.png"))
        self.addControl(self.arrowDown)
        self.arrowDown.setVisible(False)

        # Title of the current list
        self.strListTitle = xbmcgui.ControlLabel(35, 160, 540, 40, "NABBOX Forum", 'special13', alignment=xbfont_left)
        self.addControl(self.strListTitle)
        
        # Number of Video in the list:
        self.strItemNb = xbmcgui.ControlLabel(680, 160, 150, 40, '0 Elément(s)', 'special13', alignment=xbfont_right)
        self.addControl(self.strItemNb)
        
        # item Control List
        self.forumlist = xbmcgui.ControlList(23, 196, 674 , 390,'font14','0xFF000000', buttonTexture = os.path.join(IMAGEDIR,"list-background.png"), buttonFocusTexture = os.path.join(IMAGEDIR,"list-border.png"), imageWidth=40, imageHeight=32, itemTextXOffset=2, itemHeight=55)
        self.addControl(self.forumlist)
        
        # List label:
        #self.strlist = xbmcgui.ControlLabel(250, 300, 260, 20, '', 'font12', '0xFFFF0000')
        self.strlist = xbmcgui.ControlLabel(240, 330, 260, 20, '', 'font12', '0xFFFF0000',alignment=6)
        self.addControl(self.strlist)
        
        # Version and author(s):
        #self.strVersion = xbmcgui.ControlLabel(370, 30, 350, 30, "Version " + version + " par " + author, 'font12')
        self.strVersion = xbmcgui.ControlLabel(24, 89, 350, 30, version, 'font10', '0xFF000000', alignment=xbfont_left)
        self.addControl(self.strVersion)
        
        # Connection status:
        self.strUser = xbmcgui.ControlLabel(690, 86, 350, 30, "",alignment=xbfont_right)
        self.addControl(self.strUser)
        
        # ------------------------------------------------------------------------------------------------
        #                                 Download progress bar:        
        # Prepare the control which will be used by backProgressBar instance
        # 
        # -> Background Download progress bar:
        # Background image
        self.backDownldBar = xbmcgui.ControlImage(495, 130, 200, 15, os.path.join(IMAGEDIR,"list-forum.png"))
        self.addControl(self.backDownldBar)
        self.backDownldBar.setVisible(False)
        # Frontground image (progress bar)
        self.downldBar = xbmcgui.ControlImage(495, 130, 200, 15, os.path.join(IMAGEDIR,"list-header.png"))
        self.addControl(self.downldBar)
        self.downldBar.setVisible(False)
        
        # -> Download status:
        self.strDownload = xbmcgui.ControlLabel(495, 130, 200, 15, "100%",'font10','0xFF000000',alignment=6)
        self.addControl(self.strDownload)
        self.strDownload.setVisible(False)
        
        # Download scrolling text
        # Scrolling message
        self.downloadScrTxtSize = 45
        self.downloadScrTxt     = xbmcgui.ControlFadeLabel(495, 110, 210, 15, 'font10', '0xFF000000')
        self.addControl(self.downloadScrTxt)
        #self.downloadScrTxt.addLabel(downloadScrLabel)
        self.downloadScrTxt.setVisible(False)

        # Create an instance of backProgressBar
        self.backProgressBar = backProgressBar(self.downloadScrTxt, self.downloadScrTxtSize, self.strDownload, self.downldBar, self.backDownldBar, self.guiCtrl)
        # ------------------------------------------------------------------------------------------------
        
        # Previous button a the bottom
        self.buttonPrevious = xbmcgui.ControlButton(300, 537, 30, 27, "<", font = 'font12', focusedColor = '0xFFFF0000',noFocusTexture  = os.path.join(IMAGEDIR, "list-forum.png"),focusTexture = os.path.join(IMAGEDIR, "list-forum.png"), alignment=6)
        self.addControl(self.buttonPrevious)
        
        # Next button a the bottom
        self.buttonNext = xbmcgui.ControlButton(390, 537, 30, 27, ">", font = 'font12',focusedColor = '0xFFFF0000',noFocusTexture  = os.path.join(IMAGEDIR, "list-forum.png"),focusTexture = os.path.join(IMAGEDIR, "list-forum.png"), alignment=6)
        self.addControl(self.buttonNext)
        
        # Page Number:
        self.strPage = xbmcgui.ControlLabel(330, 537, 60, 27, self.nabboxBrowser.get_page_str(), 'font12',alignment=6)
        self.addControl(self.strPage)
        
        # Set navigation between control
        self.buttonReload.controlUp(self.buttonNext)
        self.buttonReload.controlDown(self.forumlist)
        self.buttonReload.controlRight(self.buttonHist)
        self.buttonReload.controlLeft(self.buttonHelp)
        
        self.buttonHist.controlUp(self.buttonNext)
        self.buttonHist.controlDown(self.forumlist)
        self.buttonHist.controlRight(self.buttonDld)
        self.buttonHist.controlLeft(self.buttonReload)
        
        self.buttonDld.controlUp(self.buttonNext)
        self.buttonDld.controlDown(self.forumlist)
        self.buttonDld.controlRight(self.buttonOptions)
        self.buttonDld.controlLeft(self.buttonHist)
        
        self.buttonOptions.controlUp(self.buttonNext)
        self.buttonOptions.controlDown(self.forumlist)
        self.buttonOptions.controlLeft(self.buttonDld)
        self.buttonOptions.controlRight(self.buttonHelp)
        
        self.buttonHelp.controlUp(self.buttonNext)
        self.buttonHelp.controlDown(self.forumlist)
        self.buttonHelp.controlLeft(self.buttonOptions)
        self.buttonHelp.controlRight(self.buttonReload)
        
        self.forumlist.controlUp(self.buttonReload)
        self.forumlist.controlDown(self.buttonNext)
        self.forumlist.controlRight(self.buttonNext)
        self.forumlist.controlLeft(self.buttonPrevious)
        
        self.buttonPrevious.controlUp(self.forumlist)
        self.buttonPrevious.controlRight(self.buttonNext)
        self.buttonPrevious.controlDown(self.buttonReload)
        
        self.buttonNext.controlUp(self.forumlist)
        self.buttonNext.controlLeft(self.buttonPrevious)
        self.buttonNext.controlDown(self.buttonReload)
        
        # Scrolling message
        stripScrollingText  = 'Afin de définir les parametres de votre compte Nabbox, selectionnez le menu Option puis definissez vos Login, Mot de passe et message de remerciement qui seront envoyé sur le Forum Nabbox'
        scrollingLabel      = stripScrollingText.rjust(self.scrollingSizeMax) # We add space on the right in order to have longer scrolling message
        self.scrollingText  = xbmcgui.ControlFadeLabel(20, 87, 680, 30, 'font12', '0xFFFFFFFF')
        self.addControl(self.scrollingText)
        self.scrollingText.addLabel(scrollingLabel)
       
        # Get the list of items
        self.newList()
                
        # Close the Loading Window 
        dialogUI.close()
        
    def updateDisplay(self):
        """
        Update all the information displayed in the UI
        """
        # Lock UI before changes
        self.guiCtrl.lockWindow()
        
        # Just to be sure scrolling won't be displayed
        self.scrollingText.setVisible(False)
        
        # Update title of the list
        self.strListTitle.setLabel(self.nabboxBrowser.get_title())
        
        # Update page label
        self.strPage.setLabel(self.nabboxBrowser.get_page_str()) 
        
        # Clear all ListItems in this control list 
        self.forumlist.reset()
        
        # Get status of connection
        connecStatus = self.nabboxBrowser.is_connected()
        
        # Get List of items to display
        srcList2Display = self.nabboxBrowser.get_displayList()
        
        # Get the type of items of previous list
        srcListLinkType = self.nabboxBrowser.get_linkTypeList()
        
        if not connecStatus:
            self.strlist.setLabel("Vous n'êtes pas connecté")
            print"updateDisplay - You are not connected"
            # Test : hide scrolling text
            self.scrollingText.setVisible(True)
            #self.strUser.setLabel("Non connecté")
            self.strUser.setLabel("")
            # Check if Nabbox account is defined
            if ((self.nabboxBrowser.getLogin() == "") or (self.nabboxBrowser.getPassword() == "")):
                print"updateDisplay - Nabbox account not defined"
            
        elif not srcList2Display:
            self.strlist.setLabel("Il n'y a pas d'émissions disponibles")
            self.strUser.setLabel("Connecté en tant que : %s"%self.nabboxBrowser.getLogin())
        else:
            self.strlist.setLabel("")
            # Set focus on the list
            self.setFocus(self.forumlist)
            self.strUser.setLabel("Connecté en tant que : %s"%self.nabboxBrowser.getLogin())
        for mylabel in srcList2Display:
            idx = srcList2Display.index(mylabel)
            # Select icon to diplay according the type of the item
            if srcListLinkType[idx] == "forum":
                mylabelList = mylabel.split("\n")
                mylabel1 = mylabelList[0]
                displayListItem = xbmcgui.ListItem(label = mylabel1, thumbnailImage = os.path.join(IMAGEDIR,"forum_icon.png"))
            elif srcListLinkType[idx] == "topic":
                displayListItem = (xbmcgui.ListItem(label = mylabel, thumbnailImage = os.path.join(IMAGEDIR,"topic.png")))
            elif srcListLinkType[idx] == "liensVideo":
                if (mylabel.endswith('zip') or mylabel.endswith('rar')):
                    displayListItem = (xbmcgui.ListItem(label = mylabel, thumbnailImage = os.path.join(IMAGEDIR,"icone_zip.png")))
                else:
                    displayListItem = (xbmcgui.ListItem(label = mylabel, thumbnailImage = os.path.join(IMAGEDIR,"icon_video.png")))
            elif srcListLinkType[idx] == "file":
                if (mylabel.endswith('zip') or mylabel.endswith('rar')):
                    displayListItem = (xbmcgui.ListItem(label = mylabel, thumbnailImage = os.path.join(IMAGEDIR,"icone_zip.png")))
                elif os.path.isdir(os.path.join(DOWNLOADDIR,mylabel)):
                    displayListItem = (xbmcgui.ListItem(label = mylabel, thumbnailImage = os.path.join(IMAGEDIR,"directory.png")))
                elif (mylabel.endswith('_part')):
                    displayListItem = (xbmcgui.ListItem(label = mylabel, thumbnailImage = os.path.join(IMAGEDIR,"reload.png")))
                else:
                    displayListItem = (xbmcgui.ListItem(label = mylabel, thumbnailImage = os.path.join(IMAGEDIR,"videohdd.png")))
            else:
                displayListItem = (xbmcgui.ListItem(label = mylabel, thumbnailImage = os.path.join(IMAGEDIR,"f_hot.gif")))
            # Add list item to the ControlList
            self.forumlist.addItem(displayListItem)
            #self.bgList.addItem(bgListItem)
            
        # Update the lablel for the number of items in the list
        itemnumber = len(srcList2Display)
        self.strItemNb.setLabel(str(itemnumber) + " Elément(s)" ) 
        
        # Set Focus on list
        self.setFocus(self.forumlist)
        
        # Set 1st item in the list
        if self.forumlist:
            self.forumlist.selectItem(0)

        # Display arrows if necessary
        if (self.forumlist.size() > self.displayListSize):
            # Real list bigger than we can display
            self.arrowUp.setVisible(False)
            self.arrowDown.setVisible(True)
        else:
            self.arrowDown.setVisible(False)
            self.arrowUp.setVisible(False)
        
        # Unlock UI
        self.guiCtrl.unlockWindow()
                
    def message_cb(self, msgType, title, message1, message2="", message3=""):
        """
        Callback function for sending a message to the UI
        @param msgType: Type of the message
        @param title: Title of the message
        @param message1: Message part 1
        @param message2: Message part 2
        @param message3: Message part 3
        """
        #print("message_cb with %s STARTS"%msgType)
        result = None

        # Display the correct dialogBox according the type
        if msgType == "OK" or msgType == "Error":
            dialogInfo = xbmcgui.Dialog()
            result = dialogInfo.ok(title, message1, message2,message3)
        elif msgType == "YESNO":
            dialogYesNo = xbmcgui.Dialog()
            result = dialogYesNo.yesno(title, message1, message2, message3)
        return result
            
    def newList(self, index=0):
        """
        Get list for requested item and update display
        @param index: index in the list (default = 0)
        """
        # Display Loading Window while we are loading the information from the website
        dialogUI = xbmcgui.DialogProgress()
        dialogUI.create("NABBOX", "Chargement des informations", "Veuillez patienter...")
               
        if (self.nabboxBrowser.getNewPageWithIdx(index) == True):
            # Update display
            self.updateDisplay()
            
            # Close the Loading Window 
            dialogUI.close()
        else:
            # Update display
            self.updateDisplay()
            
            # Close the Loading Window 
            dialogUI.close()
            
            # Display error windows
            dialogError = xbmcgui.Dialog()
            dialogError.ok("NABBOX - Erreur", "Une erreur s'est produite durant le chargement", "Merci de verifier votre configuration")
            
    def previousHistoryList(self):
        """
        Get previous list (from history) and update display
        """
        # Display Loading Window while we are loading the information from the website
        dialogUI = xbmcgui.DialogProgress()
        dialogUI.create("NABBOX", "Chargement des informations", "Veuillez patienter...")
        
        if (self.nabboxBrowser.getPreviousHistPage() == True):
            # Update display
            self.updateDisplay()
            
            # Close the Loading Window 
            dialogUI.close()
        else:
            # Update display
            self.updateDisplay()
            
            # Close the Loading Window 
            dialogUI.close()
            
            # Display error windows
            dialogError = xbmcgui.Dialog()
            dialogError.ok("NABBOX - Erreur", "Une erreur s'est produite durant le chargement", "Merci de verifier votre configuration")
            
    def nextPageList(self):
        """
        Get list from next page and update display
        """
        # Display Loading Window while we are loading the information from the website
        dialogUI = xbmcgui.DialogProgress()
        dialogUI.create("NABBOX", "Chargement des informations", "Veuillez patienter...")
        
        if (self.nabboxBrowser.getNextPage() == True):
            # Update display
            self.updateDisplay()
            
            # Close the Loading Window 
            dialogUI.close()
        else:
            # Update display
            self.updateDisplay()
            
            # Close the Loading Window 
            dialogUI.close()
            
            # Display error windows
            dialogError = xbmcgui.Dialog()
            dialogError.ok("NABBOX", "Impossible de charger la page suivante", "Elle n'est pas disponible")
            
    def prevPageList(self):
        """
        Get list from previous page and update display
        """
        # Display Loading Window while we are loading the information from the website
        dialogUI = xbmcgui.DialogProgress()
        dialogUI.create("NABBOX", "Chargement des informations", "Veuillez patienter...")
        
        if (self.nabboxBrowser.getPrevPage() == True):
            # Update display
            self.updateDisplay()
            
            # Close the Loading Window 
            dialogUI.close()
        else:
            # Update display
            self.updateDisplay()
            
            # Close the Loading Window 
            dialogUI.close()
            
            # Display error windows
            dialogError = xbmcgui.Dialog()
            dialogError.ok("NABBOX", "Impossible de charger la page précédente", "Elle n'est pas disponible")
            
    def reloadList(self):
        """
        Reload list for current page and update display
        """
        # Display Loading Window while we are loading the information from the website
        dialogUI = xbmcgui.DialogProgress()
        dialogUI.create("NABBOX", "Chargement des informations", "Veuillez patienter...")
        
        if (self.nabboxBrowser.getReloadPage() == True):
            self.updateDisplay()
            
            # Close the Loading Window 
            dialogUI.close()
        else:
            # Update display
            self.updateDisplay()
            
            # Close the Loading Window 
            dialogUI.close()
            
            # Display error windows
            dialogError = xbmcgui.Dialog()
            dialogError.ok("NABBOX - Erreur", "Une erreur s'est produite durant le chargement", "Merci de verifier votre configuration")
            
    def historyList(self):
        """
        Load history list and update display
        """
        # Display Loading Window while we are loading the information from the website
        dialogUI = xbmcgui.DialogProgress()
        dialogUI.create("NABBOX", "Chargement des informations", "Veuillez patienter...")
        
        if (self.nabboxBrowser.getHistoryPage() == True):
            self.updateDisplay()
            
            # Close the Loading Window 
            dialogUI.close()
        else:
            # Update display
            self.updateDisplay()
            
            # Close the Loading Window 
            dialogUI.close()
            
            # Display error windows
            dialogError = xbmcgui.Dialog()
            dialogError.ok("NABBOX - Erreur", "Une erreur durant la lecture de l'historique")
            
    def downloadList(self):
        """
        Load download list and update display
        """
        # Display Loading Window while we are loading the information locally
        dialogUI = xbmcgui.DialogProgress()
        dialogUI.create("NABBOX", "Chargement des informations", "Veuillez patienter...")
        
        if (self.nabboxBrowser.getDownloadPage() == True):
            self.updateDisplay()
            
        # Close the Loading Window 
        dialogUI.close()
        
    def onControl(self, control):
        try:
            if control == self.forumlist:
                # Read index of list item
                chosenIndex = self.forumlist.getSelectedPosition()
                
                # Get Selected Item Name
                selecItemName = self.nabboxBrowser.get_nameItem(chosenIndex)
                    
                # Get Selected Item Type
                selecItemType = self.nabboxBrowser.get_typeItem(chosenIndex)

                if selecItemType == "file":                        
                    if (selecItemName.endswith('zip') or selecItemName.endswith('rar')):
                        dialog = xbmcgui.Dialog()
                        if (dialog.yesno("Nabbox - Fichiers Téléchargés", "%s est une archive"%selecItemName,"Voulez-vous l'extraire?")):
                            self.nabboxBrowser.fileMgr.extract(os.path.join(DOWNLOADDIR,selecItemName),DOWNLOADDIR)
                            # Reload the page
                            # Get the list for the Download list
                            self.downloadList()
                    elif os.path.isdir(os.path.join(DOWNLOADDIR,selecItemName)):
                        dialog = xbmcgui.Dialog()
                        dialog.ok("Nabbox - Fichiers Téléchargés", "%s est un répertoire"%selecItemName, "NABBOX ne peut naviguer à l'interieur")
                    else:
                        # Get the new list
                        self.newList(chosenIndex)
                elif selecItemType == "liensVideo":
                    if (selecItemName.endswith('zip') or selecItemName.endswith('rar')):
                        dialog = xbmcgui.Dialog()
                        dialog.ok("Nabbox - Fichiers Téléchargés", "%s"%selecItemName,"est une archive","Vous ne pouvez la lire directement")
                    else:
                        # Get the new list
                        self.newList(chosenIndex)
                else:
                    # Get the new list
                    self.newList(chosenIndex)
                
            if control == self.buttonNext:
                # Get the listfor the next page
                self.nextPageList()
                
            if control == self.buttonPrevious:
                # Get the listfor the next page
                self.prevPageList()
                
            if control == self.buttonReload:
                # Reload case
                # Get the listfor the next page
                self.reloadList()
                
            if control == self.buttonHist:
                # History case
                # Get the list for the history
                self.historyList()
                
            if control == self.buttonDld:
                # Create a list for the download menu
                if self.nabboxBrowser.getDisplayProgBar():
                    dldMenu2 = "Désactiver la barre de progression"
                else:
                    dldMenu2 = "Activer la barre de progression"
                self.dldMenuList = ["Fichiers téléchargés","Stopper le téléchargement en cours",dldMenu2]
                menudldWindow = DropDownMenu()

                # Display this window until close() is called
                menudldSelected = menudldWindow.getSelect(200, 117, 85, 25,285,33,"Down", self.dldMenuList, 'Down')
                
                if menudldSelected == 0:
                    # Download list
                    # Get the list for the Download list
                    self.downloadList()

                elif menudldSelected == 1:
                    # A propos
                    # Download stop requested by user
                    # Stop the download

                    if self.nabboxBrowser.isDownloadInProgress() == True:
                        # Cancel the download
                        self.backProgressBar.cancelAction()
                    else:
                        # Prepare message to the UI
                        msgTite = "Nabbox - Annulation du téléchargement"
                        msg1    = "Aucun téléchargement n'est en cours"
                    
                        # Display message   
                        dialogInfo = xbmcgui.Dialog()
                        result = dialogInfo.ok(msgTite, msg1)
                elif menudldSelected == 2:
                    if self.nabboxBrowser.isDownloadInProgress():
                        # Display message   
                        dialogInfo = xbmcgui.Dialog()
                        result = dialogInfo.ok("Nabbox - Barre de progression", "Impossible d'activer ou désactiver la barre de ","progression lorsqu'un téléchargement est en cours")
                        
                    else:
                        if self.nabboxBrowser.getDisplayProgBar():
                            # Deactivation of progress bar (will also use another download method)
                            self.nabboxBrowser.setDisplayProgBar(False)
                            dialogInfo = xbmcgui.Dialog()
                            result = dialogInfo.ok("Nabbox - Barre de progression", "Barre de progression désactivée")
                        else:
                            # Activation of progress bar (will also use standard download method)
                            self.nabboxBrowser.setDisplayProgBar(True)
                            dialogInfo = xbmcgui.Dialog()
                            result = dialogInfo.ok("Nabbox - Barre de progression", "Barre de progression activée")
                else:
                    #print('User CANCELED')
                    pass
                
            if control == self.buttonOptions:
                # Create a list for the menu option
                if self.nabboxBrowser.getCachePages():
                    dldMenu4 = "Désactiver le cache"
                else:
                    dldMenu4 = "Activer le cache"
                    
                if self.nabboxBrowser.getCleanCache():
                    dldMenu5 = "Désactiver nettoyage auto du cache"
                else:
                    dldMenu5 = "Activer nettoyage auto du cache"
                    
                self.optionMenuList = ["Login NABBOX","Mot de passe NABBOX","Message de remerciements","Choix du Player",dldMenu4,dldMenu5]
                menuOptWindow = DropDownMenu()
                
                # Display this window until close() is called
                menOptSelected = menuOptWindow.getSelect(290, 117, 85, 25, 285, 33,"Down", self.optionMenuList, 'Down')
                    
                if menOptSelected == 0:
                    # Login
                    
                    # Read current login value
                    currentLogin = self.nabboxBrowser.getLogin()
                    if (currentLogin == ""):
                        yesnoText1 = "Votre Login n'est pas encore défini"
                        yesnoText2 = "Voulez vous le définir?"
                        yesnoText3 = ""
                    else:
                        yesnoText1 = "Votre Login actuel est:"
                        yesnoText2 = "%s"%currentLogin
                        yesnoText3 = "Voulez vous le redéfinir?"
                        
                    dialog = xbmcgui.Dialog()
                    if (dialog.yesno("Compte Nabbox - Login", yesnoText1, yesnoText2, yesnoText3)):
                        # Read login via a keyboard
                        keyboard = xbmc.Keyboard("", heading = "Saisir votre Login Nabbox")
                        keyboard.setHeading('Login') # optional
                        keyboard.doModal()
                        if (keyboard.isConfirmed()):
                            inputText = keyboard.getText()
                            print"Login: %s"%inputText
                            
                            # set login parameter
                            self.nabboxBrowser.setLogin(inputText)
                            
                            dialogInfo = xbmcgui.Dialog()
                            dialogInfo.ok("Login Nabbox", "Votre nouveau Login est:", "%s"%inputText)
                        del keyboard
                            
                elif menOptSelected == 1:
                    # Password
                    
                    # Read Password login value
                    currentPassword = self.nabboxBrowser.getPassword()

                    if (currentPassword == ""):
                        yesnoText1 = "Votre mot de passe n'est pas encore défini"
                        yesnoText2 = "Voulez vous le définir?"
                    else:
                        yesnoText1 = "Votre mot de passe est déja défini"
                        yesnoText2 = "Voulez vous le redéfinir?"
                        
                    dialog = xbmcgui.Dialog()
                    if (dialog.yesno("Compte Nabbox - Mot de passe", yesnoText1, yesnoText2)):
                        # Read login via a keyboard
                        keyboard = xbmc.Keyboard("", heading = "Saisir votre Mot de passe Nabbox", hidden = True)
                        keyboard.setHeading('Mot de passe') # optional
                        keyboard.setHiddenInput(True) # optional
                        keyboard.doModal()
                        if (keyboard.isConfirmed()):
                            inputText = keyboard.getText()
                            
                            # set password parameter
                            self.nabboxBrowser.setPassword(inputText)
                            
                            dialogInfo = xbmcgui.Dialog()
                            dialogInfo.ok("Mot de passe Nabbox", "Votre mot de passe a bien été défini")
                        keyboard.setHiddenInput(False) # optional
                        del keyboard
                            
                elif menOptSelected == 2:
                    # Thank you message
                    # Read Thanks message  value
                    currentThanks = self.nabboxBrowser.getThanksMsg()
                    
                    if (currentThanks == ""):
                        yesnoText1 = "Votre message de remerciements n'est pas encore défini"
                        yesnoText2 = "Voulez vous le définir?"
                        yesnoText3 = ""
                    else:
                        yesnoText1 = "Votre message de remerciements actuel est:"
                        yesnoText2 = "%s"%currentThanks
                        yesnoText3 = "Voulez vous le redéfinir?"
                        
                    dialog = xbmcgui.Dialog()
                    if (dialog.yesno("Compte Nabbox - Message de Remerciements", yesnoText1, yesnoText2, yesnoText3)):
                        # Read login via a keyboard
                        keyboard = xbmc.Keyboard("", heading = "Saisir votre Message de Remerciements")
                        keyboard.setHeading('Message de remerciement')  # optional
                        keyboard.setDefault("Merci")                    # optional

                        keyboard.doModal()
                        if (keyboard.isConfirmed()):
                            inputText = keyboard.getText()
                            print"Remerciement: %s"%inputText
                            
                            # set Thank you parameter
                            self.nabboxBrowser.setThanksMsg(inputText)
                            
                            dialogInfo = xbmcgui.Dialog()
                            dialogInfo.ok("Message de remerciements", "Votre nouveau Message de remerciements est:", "%s"%inputText)
                        del keyboard
                            

                elif menOptSelected == 3:
                    # Player
                    # Displat selection list
                    playerMenuList = ["Auto","DVD Player","MPlayer"]
                    
                    # Read Thanks message  value
                    currentPlayer = self.nabboxBrowser.getDefaultPlayer()
                    print "current Player: %s"%currentPlayer
                    
                    yesnoText1 = "Votre Player actuel est:"
                    yesnoText2 = "%s"%playerMenuList[int(currentPlayer)]
                    yesnoText3 = "Voulez vous le redéfinir?"
                    
                    dialog = xbmcgui.Dialog()
                    if (dialog.yesno("Nabbox - Player", yesnoText1, yesnoText2, yesnoText3)):
                        dialogPlayer = xbmcgui.Dialog()
                        chosenIndex = dialogPlayer.select('Selectionner le Player désiré', playerMenuList)
                        self.nabboxBrowser.setDefaultPlayer(chosenIndex)
                        
                        dialogInfo = xbmcgui.Dialog()
                        dialogInfo.ok("Player Nabbox", "Votre nouveau Player est:", "%s"%playerMenuList[chosenIndex])
                                            
                elif menOptSelected == 4:
                    # cache activation
                    if self.nabboxBrowser.getCachePages():
                        # Deactivation of page caching
                        self.nabboxBrowser.setCachePages(False)
                        dialogInfo = xbmcgui.Dialog()
                        result = dialogInfo.ok("Nabbox - Gestion du cache", "Cache désactivé")
                    else:
                        # Activation of page caching
                        self.nabboxBrowser.setCachePages(True)
                        dialogInfo = xbmcgui.Dialog()
                        result = dialogInfo.ok("Nabbox - Gestion du cache", "Cache activé")
                
                elif menOptSelected == 5:
                    # cache cleaning
                    if self.nabboxBrowser.getCleanCache():
                        # Deactivation of cache cleaning
                        self.nabboxBrowser.setCleanCache(False)
                        dialogInfo = xbmcgui.Dialog()
                        result = dialogInfo.ok("Nabbox - Gestion du cache", "Nettoyage automatique du Cache désactivé")
                    else:
                        # Activation of cache cleaning
                        self.nabboxBrowser.setCleanCache(True)
                        dialogInfo = xbmcgui.Dialog()
                        result = dialogInfo.ok("Nabbox - Gestion du cache", "Nettoyage automatique du Cache activé")
                
                else:
                    #print('user canceled')
                    pass
                    
                del menuOptWindow # !!!! Pb or reference instead of copy, if use menOptSelected after del of menuOptWindow -> crash
                
            if control == self.buttonHelp:
                if self.nabboxBrowser.getDebugMode():
                    helpMenu2 = "Mode STANDARD"
                else:
                    helpMenu2 = "Mode DEBUG"
                
                # Create a list for the Help option
                self.helpMenuList = ["Aide","A propos",helpMenu2]
                menuHelpWindow = DropDownMenu()
                
                # Display this window until close() is called
                menuHelpSelected = menuHelpWindow.getSelect(380, 117, 85, 25,160,33,"Down", self.helpMenuList, 'Down')
                
                if menuHelpSelected == 0:
                    # Aide
                    infoHelpWindow = HelpWindow()
                    del infoHelpWindow
                elif menuHelpSelected == 1:
                    # A propos
                    infoAboutWindow = InfoWindow()
                    del infoAboutWindow
                elif menuHelpSelected == 2:
                    # Debug mode
                    if self.nabboxBrowser.getDebugMode():
                        # Standrad Mode
                        self.nabboxBrowser.setDebugMode(False)
                        dialogInfo = xbmcgui.Dialog()
                        result = dialogInfo.ok("Nabbox - Mode de fonctionnement", "Mode STANDARD activé - Mode DEBUG désactivé", "Merci de redemarrer pour")
                    else:
                        # Debug Mode
                        self.nabboxBrowser.setDebugMode(True)
                        dialogInfo = xbmcgui.Dialog()
                        result = dialogInfo.ok("Nabbox - Mode de fonctionnement", "Mode DEBUG activé - Mode STANDARD désactivé")
                else:
                    #print('user canceled')
                    pass
        except:
            print ("error/onControl: " + str(sys.exc_info()[0]))
            traceback.print_exc()
            
    def onAction(self, action):
        try:
            if action == ACTION_PREVIOUS_MENU:
                # Check if a download is already in progress
                if self.nabboxBrowser.isDownloadInProgress() == True:
                    dialog = xbmcgui.Dialog()
                    if (dialog.yesno("Nabbox - Fin du programme", "Un Téléchargement est en cours", "Voulez vous le poursuivre en arriere plan?","Attention ceci peut causer des problemes de stabilité d'XBMC")):
                        print "Exiting Nabbox: Download will continue after exiting"
                    else:
                        # Stop download in progress
                        print "Exiting Nabbox: Stopping download in progress"
                        self.backProgressBar.cancelAction()
                
                # Clean the cache is requested
                if self.nabboxBrowser.delCache == True:
                    print "Deleting cache"
                    self.nabboxBrowser.fileMgr.delFiles(CACHEDIR)
                
                self.close()
                
            #if action == ACTION_SHOW_INFO:
            if ((action == ACTION_SHOW_INFO) or (action==ACTION_CONTEXT_MENU)):
                # Check we have the focus on the list
                if self.getFocus() == self.forumlist:
                    # Focus on the list
                    # Get focus item index
                    chosenIndex = self.forumlist.getSelectedPosition()
                    
                    # Get Name for Display  
                    selecItemName = self.nabboxBrowser.get_nameItem(chosenIndex)
                    
                    # Get the type of the link in order to be sure
                    selecItemType = self.nabboxBrowser.get_typeItem(chosenIndex)
                    
                    # check on the type of link
                    if selecItemType == "liensVideo":
                        fileMenu = ["Description","Lire","Télécharger","Télécharger en arriere plan","Annuler"]
                        dialogPlayer = xbmcgui.Dialog()
                        menuIndex = dialogPlayer.select("Selectionner l'action désiré pour ce fichier", fileMenu)
                        
                        if (menuIndex == 0):
                            # Get File Description
                            # --------------------
                            
                            # Get the handler (in case of video handler is a URL)
                            selecVideoURL = self.nabboxBrowser.get_hdlItem(chosenIndex)
                            
                            # Get File Size
                            videoFileSize = float((self.nabboxBrowser.getFileSize(selecVideoURL)))/(1024*1024)
                            videoFileSizeStr = str(videoFileSize)
                            videoFileSizeDec = Decimal(videoFileSizeStr).quantize(Decimal('.1'), rounding=ROUND_UP)
                            
                            dialogInfo = xbmcgui.Dialog()
                            dialogInfo.ok("Description du fichier", "Nom: %s"%(os.path.basename(selecVideoURL)), "Taille: %s Mo"%videoFileSizeDec)
                            
                        if (menuIndex == 1):
                            # Play
                            # ----
                            if (selecItemName.endswith('zip') or selecItemName.endswith('rar')):
                                dialog = xbmcgui.Dialog()
                                dialog.ok("Nabbox - Fichiers Téléchargés", "%s"%selecItemName,"est une archive","Vous ne pouvez la lire directement")
                            else:
                                # Get the new list
                                self.newList(chosenIndex)
                            
                        if (menuIndex == 2):
                            # Download the video in foreground
                            # --------------------------------
                            
                            # Check if a download is already in progress
                            if self.nabboxBrowser.isDownloadInProgress() == True:
                                dialog = xbmcgui.Dialog()
                                dialog.ok("Nabbox - Télécharger en arrière plan", "Un Téléchargement est deja en cours", "Afin de pouvoir démarrer ce téléchargement vous devez","terminer ou stopper le téléchargement en cours")
                            else:
                                # Get the handler (in case of video handler is a URL)
                                selecVideoURL = self.nabboxBrowser.get_hdlItem(chosenIndex)
                                
                                dp = xbmcgui.DialogProgress()
                                dp.create("Téléchargement en cours ...", "%s"%(os.path.basename(selecVideoURL))," en cours de téléchargement")
                                
                                # Save in local directory
                                self.nabboxBrowser.loadvideo(selecVideoURL, save=True, msg_cb=self.message_cb, progBar=dp)
                                del dp
                            
                        if (menuIndex == 3):
                            # Download the video in background
                            # --------------------------------
                            
                            # Check if a download is already in progress
                            if self.nabboxBrowser.isDownloadInProgress() == True:
                                dialog = xbmcgui.Dialog()
                                dialog.ok("Nabbox - Télécharger en arriere plan", "Un Téléchargement est dejà en cours", "Afin de pouvoir démarrer ce téléchargement vous devez","terminer ou stopper le téléchargement en cours")
                            else:
                                # Get the handler (in case of video handler is a URL)
                                selecVideoURL = self.nabboxBrowser.get_hdlItem(chosenIndex)
                                
                                dialog = xbmcgui.Dialog()
                                if (dialog.yesno("Nabbox - Télécharger en arriere plan","Ce mode de téléchargement en arriere plan requiert","plus de resources et peut rendre le script instable", "Etes vous sur de vouloir l'utiliser?")):
                                    # Save in local directory
                                    self.backProgressBar.create(os.path.basename(selecVideoURL))
                                    self.nabboxBrowser.loadvideo(selecVideoURL, save=True, msg_cb=self.message_cb, progBar=self.backProgressBar)
                                
                    elif selecItemType == "file":           
                        isArchive = False            
                        if (selecItemName.endswith('zip') or selecItemName.endswith('rar')):
                            isArchive = True
                            fileMenu = ["Description","Extraire","Supprimer","Annuler"]                            
                        else:
                            fileMenu = ["Description","Lire","Supprimer","Annuler"]
                            
                        dialogPlayer = xbmcgui.Dialog()
                        menuIndex = dialogPlayer.select("Selectionner l'action désiré pour ce fichier", fileMenu)
                        if (menuIndex == 0):
                            # Description
                            videoFileSize = (float(os.path.getsize(os.path.join(DOWNLOADDIR,selecItemName))))/(1024*1024)
                            videoFileSizeStr = str(videoFileSize)
                            videoFileSizeDec = Decimal(videoFileSizeStr).quantize(Decimal('.1'), rounding=ROUND_UP)
                            
                            # Get File Size
                            print "File %s  with size: %dMo"%(selecItemName,videoFileSize)
                            print videoFileSizeStr
                            
                            dialogInfo = xbmcgui.Dialog()
                            dialogInfo.ok("Description du fichier", "Nom: %s"%(os.path.basename(selecItemName)), "Taille: %s Mo"%videoFileSizeDec)
                        if (menuIndex == 1):
                            if isArchive == False:
                                # Play
                                
                                # Get the new list
                                self.newList(chosenIndex)
                            else:
                                # Archive extraction
                                self.nabboxBrowser.fileMgr.extract(os.path.join(DOWNLOADDIR,selecItemName),DOWNLOADDIR)
                                
                                # Reload the page
                                # Get the list for the Download list
                                self.downloadList()

                            
                        if (menuIndex == 2):
                            dialog = xbmcgui.Dialog()
                            if not os.path.isdir(os.path.join(DOWNLOADDIR,selecItemName)):
                                if (dialog.yesno("Nabbox - Fichiers Téléchargés", "Etes vous sur de vouloir supprimer le fichier:", selecItemName)):
                                    # Delete file
                                    self.nabboxBrowser.fileMgr.deleteFile(os.path.join(DOWNLOADDIR,selecItemName))
                                    # Reload the page
                                    # Get the list for the Download list
                                    self.downloadList()
                            else:
                                if (dialog.yesno("Nabbox - Fichiers Téléchargés", "Etes vous sur de vouloir supprimer le répertoire:", selecItemName, "et tout son contenu?")):
                                    # Delete dir
                                    self.nabboxBrowser.fileMgr.delFiles(os.path.join(DOWNLOADDIR,selecItemName))
                                    os.removedirs(os.path.join(DOWNLOADDIR,selecItemName))
                                    # Reload the page
                                    # Get the list for the Download list
                                    self.downloadList()
                            
            if action == ACTION_PARENT_DIR:
                # Get the previous list (from history)
                self.previousHistoryList()
                
            if (action == ACTION_MOVE_UP) or (action == ACTION_MOVE_DOWN):
                if self.getFocus() == self.forumlist:
                    if (self.forumlist.size() > self.displayListSize):
                        # List is bigger than what we can display
                        # Get focus item index
                        chosenIndex = self.forumlist.getSelectedPosition()
                        if chosenIndex == 0:
                            # First element of the list
                            self.arrowUp.setVisible(False)
                            self.arrowDown.setVisible(True)
                            
                        elif (chosenIndex >= self.displayListSize) and (chosenIndex < (self.forumlist.size() - 1)):
                            self.arrowDown.setVisible(True)
                            self.arrowUp.setVisible(True)
                        elif chosenIndex == (self.forumlist.size() - 1):
                            # Last element of the list
                            self.arrowDown.setVisible(False)
                    else:
                        # No ARROW to display
                        self.arrowUp.setVisible(False)
                        self.arrowDown.setVisible(False)
            #TODO: Add case of Mouse scrolling up/down for displaying or not the arrow
        except:
            print ("error/onaction: " + str(sys.exc_info()[0]))
            traceback.print_exc()
            
            
########
#
# Main
#
########

print("==================================================================================")
print("")
print("     NABBOX " + version + " by " + authorUI + " and " + authorCore+ " HTML parser STARTS")
print("")
print("==================================================================================")


# Print Path information
print("ROOTDIR: " + ROOTDIR)
print("IMAGEDIR: " + IMAGEDIR)
print("CACHEDIR: " + CACHEDIR)
print("DOWNLOADDIR: " + DOWNLOADDIR)


# Create main Window
nabboxui = MainWindow()

# Display this window until close() is called
nabboxui.doModal()
del nabboxui

print "UI closed"
print ("=================================Exiting NABBOX==================================")
    

