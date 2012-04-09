# -*- coding: cp1252 -*-
"""
   Video Addon (plugin type) allowing to watch 8 Art City Blogs' videos
"""

REMOTE_DBG       = False # For remote debugging with PyDev (Eclipse)


__script__       = "Unknown"
__plugin__       = "8 Art City"
__addonID__      = "plugin.video.8artcity"
__author__       = "Temhil (http://passion-xbmc.org)"
__url__          = "http://passion-xbmc.org/index.php"
__svn_url__      = "http://passion-xbmc.googlecode.com/svn/trunk/addons/plugin.video.8artcity/"
__credits__      = "Team XBMC Passion"
__platform__     = "xbmc media center"
__date__         = "08-05-2012"
__version__      = "1.2"
__svn_revision__ = 0


import os
import urllib
from traceback import print_exc

# xbmc modules
import xbmc
import xbmcplugin
import xbmcgui
import xbmcaddon


 
__addon__    = xbmcaddon.Addon( __addonID__ )
__settings__ = __addon__
__language__ = __addon__.getLocalizedString
__addonDir__ = __settings__.getAddonInfo( "path" )

# Remote debugger using Eclipse and Pydev
if REMOTE_DBG:
    # Note pydevd module need to be copied in XBMC\system\python\Lib\pysrc
    try:
        import pysrc.pydevd as pydevd
        pydevd.settrace('localhost', stdoutToServer=True, stderrToServer=True)
    except ImportError:
        sys.stderr.write("Error: " +
            "You must add org.python.pydev.debug.pysrc to XBMC\system\python\Lib\pysrc")
        sys.exit(1)



ROOTDIR            = os.getcwd()
BASE_RESOURCE_PATH = os.path.join( ROOTDIR, "resources" )
MEDIA_PATH = os.path.join( BASE_RESOURCE_PATH, "media" )
#LIBS               = os.path.join( BASE_RESOURCE_PATH, "lib" )

# append the proper libs folder to our path
#sys.path.append( LIBS )


#modules custom
try:
    import resources.lib.huitartcity as huitartcity
    from resources.lib.utils import url_join, convertStrDate
except:
    print_exc()


ADDON_DATA  = xbmc.translatePath( "special://profile/addon_data/%s/" % __addonID__ )
DOWNLOADDIR = os.path.join( ADDON_DATA, "downloads")
CACHEDIR    = os.path.join( ADDON_DATA, "cache")

# List of directories to check at startup
dirCheckList   = ( CACHEDIR, DOWNLOADDIR, ) #Tuple - Singleton (Note Extra ,)



def verifrep( folder ):
    """
        Source MyCine (thanks!)
        Check a folder exists and make it if necessary
    """
    try:
        #print("verifrep check if directory: " + folder + " exists")
        if not os.path.exists( folder ):
            print( "verifrep Impossible to find the directory - trying to create the directory: " + folder )
            os.makedirs( folder )
    except Exception, e:
        print( "Exception while creating folder " + folder )
        print( str( e ) )

class HuitArtCityPlugin:
    """
    main plugin class
    """
    # define param key names
    PARAM_TITLE       = "title"
    PARAM_TYPE        = 'type'
    PARAM_LISTTYPE    = 'listype'
    PARAM_URL         = 'url'
    PARAM_REPO_FORMAT = 'format'
    VALUE_LIST_BLOGS  = 'listblogs'
    VALUE_LIST_VIDEO  = 'listvideo'

    # Constant
    BASE_URL = "http://www.8artcity.com"
    URL_LIST_BLOGS = "/le-videoblog-dalain-carraze"

    def __init__( self, *args, **kwargs ):
        self.parameters = self._parse_params()

        
        # Check settings
        #if ( __settings__.getSetting('first_run') == 'true' ):
        #    #xbmcplugin.openSettings(sys.argv[0])
        #    print "First run of Addons Installer Plugin, ckeling if Addon Libraries are installed"
        #else:
        #    self.select()
        self.select()


    def createRootDir ( self ):
        print "createRootDir"
        xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category=__language__( 30001 ) )
        #TODO: set category with the name of the blog
        #TODO: Display number of pages
        pageUrl = url_join(self.BASE_URL, self.URL_LIST_BLOGS)
        print pageUrl
        huitartcity.getBlogsList(pageUrl, addItemFunc=self._addDir, progressBar=None,  msgFunc=None )
        self._end_of_directory( True )

        
    def createVideoList ( self, rel_url ):
        pageUrl = url_join(self.BASE_URL, rel_url)
        print "createVideoList"
        xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category=__language__( 30001 ) )
        #TODO: set category with the name of the blog
        #TODO: Display number of pages
        
       
        numberIter = int( __settings__.getSetting('videoperpage') ) + 1
        nextPageRel_url = None
        
        # We are going to load numberIter web pages
        for i in range(numberIter):
            print pageUrl
            nextPageRel_url = huitartcity.getVideoList(pageUrl, addItemFunc=self._addLink, progressBar=None,  msgFunc=None )
            pageUrl = url_join(self.BASE_URL, nextPageRel_url)
            if nextPageRel_url == None:
                break
        if nextPageRel_url:
            self._addDir({"title": "Suivant", "url": nextPageRel_url, "image": os.path.join(MEDIA_PATH, "next-page.png"), "description": "Charge la page suivante"})
        self._end_of_directory( True )

        
    def select( self ):
        try:
            #print "select"
            #print self.parameters
            if len(self.parameters) < 1:
                self.createRootDir()
                
            elif self.PARAM_LISTTYPE in self.parameters.keys():
                listType = self.parameters[self.PARAM_LISTTYPE]
                rel_url  = self.parameters[self.PARAM_URL]
                
                if listType == self.VALUE_LIST_VIDEO:
                    self.createVideoList(rel_url)
            else:   
                self._end_of_directory( True, update=False )

        except:
            print_exc()
            self._end_of_directory( False )


    def _parse_params( self ):
        """
        Parses Plugin parameters and returns it as a dictionary
        """
        paramDic={}
        # Parameters are on the 3rd arg passed to the script
        paramStr=sys.argv[2]
        print paramStr
        if len(paramStr)>1:
            paramStr = paramStr.replace('?','')
            
            # Ignore last char if it is a '/'
            if (paramStr[len(paramStr)-1]=='/'):
                paramStr=paramStr[0:len(paramStr)-2]
                
            # Processing each parameter splited on  '&'   
            for param in paramStr.split("&"):
                try:
                    # Spliting couple key/value
                    key,value=param.split("=")
                except:
                    key=param
                    value=""
                    
                key = urllib.unquote_plus(key)
                value = urllib.unquote_plus(value)
                
                # Filling dictionnary
                paramDic[key]=value
        print paramDic
        return paramDic        


    def _create_param_url(self, paramsDic):
        """
        Create an plugin URL based on the key/value passed in a dictionary
        """
        url = sys.argv[ 0 ]
        sep = '?'
        print paramsDic
        try:
            for param in paramsDic:
                #TODO: solve error on name with non ascii char (generate exception)
                url = url + sep + urllib.quote_plus( param ) + '=' + urllib.quote_plus( paramsDic[param] )
                sep = '&'
        except:
            url = None
            print_exc()
        return url

    def _addLink( self, itemInfo ):
        ok=True
        
        #paramsAddons = {}
        #paramsAddons[self.PARAM_LISTTYPE] = VALUE_LIST_VIDEO
        #paramsAddons[self.PARAM_URL] = dirInfo["url"]
        if itemInfo["url_image"] != None:
            icon = url_join(self.BASE_URL, itemInfo["url_image"])
        else:
            icon = "DefaultVideo.png"
            
        liz=xbmcgui.ListItem( label=itemInfo["title"], label2=itemInfo["create_date"], iconImage=icon, thumbnailImage=icon )
        liz.setInfo( type="Video", 
                     infoLabels={ "title": itemInfo["title"], 
                                  "plotoutline": itemInfo["create_date"],
                                  "plot" : itemInfo["description"], 
                                  "aired": convertStrDate(itemInfo["create_date"]) } )
        liz.setProperty('mimetype', 'video/x-flv')
                                  
        url = url_join(self.BASE_URL, itemInfo["url_video"])
        if url:
            ok=xbmcplugin.addDirectoryItem( handle=int(sys.argv[1]), url=url, listitem=liz, isFolder=False  )
        return ok

    

    def _addDir( self, dirInfo ):
        """
        Credit to ppic
        """
        #u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        ok=True
        paramsAddons = {}

        paramsAddons[self.PARAM_LISTTYPE] = self.VALUE_LIST_VIDEO
        paramsAddons[self.PARAM_URL] = dirInfo["url"]
        
        if dirInfo["image"] != None:
            icon = url_join(self.BASE_URL, dirInfo["image"])
        else:
            icon = "DefaultVideo.png"

        liz=xbmcgui.ListItem( dirInfo["title"], iconImage=icon, thumbnailImage=icon )
        
        #Context Menu
        #if c_items : 
        #    liz.addContextMenuItems( c_items, replaceItems=True )
        liz.setInfo( type="Video", 
                     infoLabels={ "title": dirInfo["title"], 
                                  "plot" : dirInfo["description"] } )

        url = self._create_param_url( paramsAddons )
        if url:
            ok=xbmcplugin.addDirectoryItem( handle=int( sys.argv[1] ), url=url, listitem=liz, isFolder=True )
        return ok

    
    def _end_of_directory( self, OK, update=False ):
        xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=OK, updateListing=update )#, cacheToDisc=True )#updateListing = True,

    def _add_sort_methods( self, OK ):
        if ( OK ):
            try:
                xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_DATE )
                xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_VIDEO_TITLE )
                #xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE )
                xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_GENRE )
                #xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_VIDEO_RUNTIME )
                #xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_STUDIO )
            except:
                print_exc()
        self._end_of_directory( OK )
    
    def _coloring( self, text , color , colorword ):
        if color == "red": color="FFFF0000"
        if color == "green": color="ff00FF00"
        if color == "yellow": color="ffFFFF00"
        colored_text = text.replace( colorword , "[COLOR=%s]%s[/COLOR]" % ( color , colorword ) )
        return colored_text

    
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


#######################################################################################################################    
# BEGIN !
#######################################################################################################################

if ( __name__ == "__main__" ):
    try:
        HuitArtCityPlugin()
    except:
        print_exc()
