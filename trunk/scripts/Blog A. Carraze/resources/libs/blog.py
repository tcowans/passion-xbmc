# -*- coding: cp1252 -*-

"""
Le Blog d'Alain Carrazé : Blog lib by Temhil (temhil@gmail.com)
"""

#En gros seul les fonctions et variables de __all__ vont etre importees lors du "import *"
#The public names defined by a module are determined by checking the module's namespace
#for a variable named __all__; if defined, it must be a sequence of strings which are names defined
#or imported by that module. The names given in __all__ are all considered public and are required to exist.
#If __all__ is not defined, the set of public names includes all names found in the module's namespace
#which do not begin with an underscore character ("_"). __all__ should contain the entire public API.
#It is intended to avoid accidentally exporting items that are not part of the API (such as library modules
#which were imported and used within the module).
__all__ = [
    # public names
    "ROOTDIR",
    "IMAGEDIR",
    "CACHEDIR",
    "LIBDIR",
    "dirCheckList",
    "PLAYER_AUTO",
    "PLAYER_DVDPLAYER",
    "PLAYER_MPLAYER",
    "playerSelect",
    "BASE_BLOGNAME",
    "BASE_URL_INFO",
    "BASE_URL_XML",
    "BASE_URL_VIDEO_INFO",
    "URL_MAIN_WEBPAGE",
    "URL_EXT_WEBPAGE",
    "downloadJPG",
    "strip_off",
    "txdata",
    "txheaders",
    "CategoryObject",
    "EntryObject",
    "WebPage",
    "blogVideoDescriptWebPage",
    "blogEntryListWebPage",
    "blogExternalEntryListWebPage",
    "blogExternalVideoListFlashWebPage",
    "BlogVideoXML",
    "ConfigCtrl",
    "fileMgr",
    ]


############################################################################
# import  
############################################################################
from string import *
import sys, os.path
import re
import urllib, urllib2, cookielib, urlparse
import htmllib
import ConfigParser
import traceback
from copy import copy, deepcopy
#from threading import Thread, Event

try:
    import xbmc
except ImportError:
    raise ImportError, 'This program requires the XBMC extensions for Python.'


############################################################################
# Get current working directory and update internal vars with it  
############################################################################

# Set paths
ROOTDIR = xbmc.translatePath(os.getcwd().replace( ";", "" )) # Create a path with valid format

#IMAGEDIR    = os.path.join(ROOTDIR, "images")
IMAGEDIR    = os.path.join(ROOTDIR, "resources", "skins", "Default", "media")
CACHEDIR    = os.path.join(ROOTDIR, "cache")
#DOWNLOADDIR = os.path.join(ROOTDIR, "download")
LIBDIR      = os.path.join(ROOTDIR, "lib")

# List of directories to check at startup
dirCheckList   = (CACHEDIR,) #Tuple - Singleton (Note Extra ,)

# Import lib
from BeautifulSoup import BeautifulStoneSoup #librairie de traitement XML



#############################################################################
# Player values
#############################################################################
PLAYER_AUTO         = 0 # xbmc.PLAYER_CORE_AUTO
PLAYER_DVDPLAYER    = 1 # xbmc.PLAYER_CORE_DVDPLAYER
PLAYER_MPLAYER      = 2 # xbmc.PLAYER_CORE_MPLAYER

# Create a tuple matching to the value above
playerSelect = (xbmc.PLAYER_CORE_AUTO,
                xbmc.PLAYER_CORE_DVDPLAYER,
                xbmc.PLAYER_CORE_MPLAYER)

#############################################################################
# Blog configuration
#############################################################################

#BASE_BLOGNAME       = "oscars"
#BASE_BLOGNAME       = "cesar"
#BASE_BLOGNAME       = "alamaisonblanche"
#BASE_BLOGNAME       = "didierallouch"
BASE_BLOGNAME       = "alaincarraze"
BASE_URL_INFO       = "http://www.canalplus.fr"
BASE_URL_XML        = BASE_URL_INFO + "/flash/xml/module/embed-video-player/embed-video-player.php?video_id="
BASE_URL_VIDEO_INFO = BASE_URL_INFO + "/processus/page/midh/xt_desc_video.php?cid="
URL_MAIN_WEBPAGE    = "http://%s.blog.canal-plus.com/"%BASE_BLOGNAME
URL_EXT_WEBPAGE     = BASE_URL_INFO + "/c-series/pid3054-c-series-express.html"

# Set Headers
txdata = None
txheaders = {	
    'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.7) Gecko/20070914 Firefox/2.0.0.7'
}


def unescape(s):
    """
    remplace les séquences d'échappement par leurs caractères équivalent
    """
    p = htmllib.HTMLParser(None)
    p.save_bgn()
    p.feed(s)
    return p.save_end()

def downloadJPG(source, destination, debug=False):
    """
    Source MyCine (thanks!)
    Download IF NECESSARY a URL 'source' (string) to a URL 'target' (string)
    Source is downloaded only if target doesn't already exist
    """
    if debug:
        print("downloadJPG with source = " + source)
        print("downloadJPG with destination = " + destination)
    if os.path.exists(destination):
        if debug:
            print("downloadJPG destination already exist")
    else:
        try:
            if debug:
                print("downloadJPG destination doesn't exist, try to retrieve")
            loc = urllib.URLopener()
            loc.retrieve(source, destination)
        except Exception, e:
            print("Exception while source retrieving")
            print(e)
            print ( str( sys.exc_info()[0] ) )
            traceback.print_exc()

def strip_off( text, by="", xbmc_labels_formatting=False ):
    """ 
    FONCTION POUR RECUPERER UN TEXTE D'UN TAG 
    Merci a Frost
    """
    if xbmc_labels_formatting:
        text = text.replace( "[", "<" ).replace( "]", ">" )
    return re.sub( "(?s)<[^>]*>", by, text )


class CategoryObject:
    """
    Structure de donnees definissant une categorie de liste
    """
    def __init__( self, name="", url=None ):
        self.name               = name
        self.url                = url
        self.entryList          = []
        self.basicDataLoaded    = False
        self.extendedDataLoaded = False
        self.stopDataLoadThread = True
        

    def __repr__( self ):
        return "CategoryObject: ( %s, %s, %s, %s )" % ( self.name, self.url, self.entryList, self.basicDataLoaded, self.extendedDataLoaded ) 
    
    def __len__( self ):
        len( self.name ) + len( self.url ) + len ( self.entryList ) + len( self.basicDataLoaded ) + len( self.extendedDataLoaded )

class EntryObject:
    """
    Structure de donnees definissant un element de la liste
    """
    def __init__( self ):
        self.videoID      = None
        self.title        = ""
        self.date         = ""       
        self.description  = ""
        self.fullDescURL  = None
        self.shortDescURL = None
        self.imagePath    = os.path.join( IMAGEDIR,"noImageAvailable.jpg" )
        self.videoHighURL = None
        self.videoLowURL  = None
        self.type         = None
        

    def __repr__( self ):
        return "EntryObject: ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s )" % ( self.videoID, self.title, self.date, self.description, self.fullDescURL, self.shortDescURL, self.imagePath, self.videoHighURL, self.videoLowURL, self.type ) 
    
    def __len__( self ):
        len( self.videoID ) + len( self.title ) + len( self.date ) + len ( self.description ) + len( self.fullDescURL ) + len( self.shortDescURL ) + len( self.imagePath )+ len( self.videoHighURL ) + len( self.videoLowURL ) + len( self.type )


class WebPage:
    """
    
    Load a remote Web page (html,xml) and provides source code
    
    """
    def __init__(self, url, txData, txHearder,debug=False):
        """
        - Init of WebPage
        - Load the Web page at the specific URL
          and copy the source code in self.Source
        """
        self.debug = debug
        try:
            # CookieJar objects support the iterator protocol for iterating over contained Cookie objects.
            cj = cookielib.CookieJar()
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
            req = urllib2.Request(url, txData, txHearder)
            u = opener.open(req)
            headers = u.info()
            self.Source = u.read()
            
            if self.debug == True:
                # Saving page in debug mode
                print 'WebPage - url:'
                print url
                urlparams = urlparse.urlparse(url)
                print urlparams
                print len(urlparams)
                print urlparams[len(urlparams) -2]
                if urlparams[len(urlparams) -2] == '':
                    filename = urlparams[1] + ".html"
                else:
                    filename = urlparams[1] + '_' + urlparams[len(urlparams) -2]  + ".html"
                print filename
                if filename == None or filename == '':
                    filename = "defaut.html"
                print "WebPage - saving file %s at: %s"%( filename, ( os.path.join( CACHEDIR, filename ) ) )
                open(os.path.join(CACHEDIR, filename),"w").write(self.Source)

        except Exception, e:
            print("Exception in WebPage init for URL: %s"%url )
            print(e)
            print ( str( sys.exc_info()[0] ) )
            traceback.print_exc()


class blogVideoDescriptWebPage(WebPage):
    """
    
    Inherit from WebPage super class
    Load on AC blog webiste a video description webpage
    
    """
    def getVideoDescription(self):
        """
        Extract video description from the AC blog collection webpage
        Parameters:
            - [out] Video description
        """
        videoDate       = ""
        videoTitle      = ""
        videoDesciption = ""
        reVideo     = re.compile(r'<h2 class="date"><span>(?P<videoDate>.+?)</span></h2>.*?<h3><span>(?P<videoTitle>.+?)</span></h3>.*?<div class=\"posttext-decorator2\">  <p>(?P<videoDescription_part1>.+?)<div id="playercontent.*?"playercontent.*?\);</script>(?P<videoDescription_part2>.*?)</p>   </div> </div> </div> <div class="postbottom"> <div class="postbottom-decorator1"> <div class="postbottom-decorator2"> <p class="posted">', re.DOTALL) 
        for i in reVideo.finditer(self.Source):
            # Copy each item found in a list
            videoDate       = unicode(i.group("videoDate"),"utf-8").encode("cp1252")
            videoTitle      = unicode(i.group("videoTitle"),"utf-8").encode("cp1252")
            videoDesciption = strip_off(unicode(i.group("videoDescription_part1"),"utf-8").encode("cp1252")) + strip_off(unicode(i.group("videoDescription_part2"),"utf-8").encode("cp1252"))
        
        return videoDate,videoTitle,videoDesciption

    def getVideoCommentsList(self):
        """
        Extract video comments from the AC blog collection webpage
        Parameters:
            - [out] Video comments
        """
        commentIDList           = []
        commentDescriptionList  = []
        commentAuthorList       = []
        commentDateList         = [] 
        reVideo = re.compile(r'<a id=\"(?P<commentID>[a-zA-Z0-9]+?)\"></a> <p>(?P<commentDescription>.+?)</p> <p class="posted"> Ecrit par : (<a.+?>(?P<commentAuthor1>.+?)</a>|(?P<commentAuthor2>.+?)) \| (?P<commentDate>.+?) </p>', re.DOTALL) 
        
        
        for i in reVideo.finditer(self.Source):
            # Copy each item found in a list
            commentIDList.append(unicode(i.group("commentID"),"utf-8").encode("cp1252"))
            
            commentDesRaw       = unicode(i.group("commentDescription"),"utf-8").encode("cp1252")
            commentDescription  = re.sub(r"<.*?>", r"", commentDesRaw)
            commentDescriptionList.append(commentDescription)
            
            commentAuthor = i.group("commentAuthor1")
            if commentAuthor == None:
                commentAuthor = i.group("commentAuthor2")
            commentAuthorList.append(unicode(commentAuthor,"utf-8").encode("cp1252"))
            
            commentDateList.append(unicode(i.group("commentDate"),"utf-8").encode("cp1252"))
        
        if self.debug: 
            print "blogVideoDescriptWebPage - getVideoCommentsList: "
            print commentIDList
            print commentDescriptionList
            print commentAuthorList
            print commentDateList
        
        return commentIDList,commentDescriptionList,commentAuthorList,commentDateList

class blogEntryListWebPage( WebPage ):
    """
    
    Inherit from WebPage super class
    Load on blog webiste a entry list webpage
    which include list of entry (video and/or text) and provides source code
    
    """
    def __init__( self, url, txData, txHearder, debug=False ):
        WebPage.__init__( self, url, txData, txHearder, debug )
        self.entries = []
        self.debug = debug
        
    def getEntryList( self ):
        """
        Extract data about video files from the AC blog collection webpage
        """
        reEntry = re.compile(r"""(<h2 class="date"><span>(?P<entryDate>.+?)</span></h2>)? *?<a id="(?P<entryID>[a-zA-Z][0-9]+?)"></a> <h3><span>(?P<entryTitle>.+?)</span></h3>.*?<div class=\"posttext-decorator2\">\ <p>(?P<entryContent>.+?)</p> </div> </div> </div>.*?<a href="http://%s\.blog\.canal-plus\.com/(?P<entryDescriptURL>archive.+?html)\">Lien permanent</a>"""%BASE_BLOGNAME, re.DOTALL) 
        reVideo = re.compile(r"""(?P<videoDescription>.*?)<div id="playercontent(?P<videoID>[0-9]+?)">.*?"playercontent[0-9]+?"\);</script>|(?P<textOnly>.+)""", re.DOTALL) 

        ##TODO Exception on nothing found !!!!!!!!!!!!!!!!!!!!!!!!
        try:
            for i in reEntry.finditer( self.Source ):
                # Copy each item found in a list
                blogEntry = EntryObject()
                title     = i.group( "entryTitle" )
                newEntry  = True
                if title: # !=None
                    blogEntry.title = unicode( title, "utf-8" ).encode( "cp1252" )
                date = i.group( "entryDate" )
                if date:
                    blogEntry.date  = unicode( date, "utf-8" ).encode( "cp1252" )
                blogEntry.fullDescURL = i.group( "entryDescriptURL" )

                # Now let's try to find a video inside this entry
                entryContent  = i.group( "entryContent" )
                for j in reVideo.finditer( entryContent ):
                    blogEntry.videoID = j.group( "videoID" )
                    #blogEntry.shortDescURL = BASE_URL_VIDEO_INFO + blogEntry.videoID
                    description = j.group( "videoDescription" )
                    textOnly    = j.group( "textOnly" )
                    if description:
                        entryDescription = strip_off( unicode( description, "utf-8" ).encode( "cp1252" ) )
                    elif textOnly:
                        entryDescription = strip_off( unicode( textOnly, "utf-8" ).encode( "cp1252" ) )

                    else:
                        entryDescription = ""
                    
                    if not blogEntry.videoID and self.entries and blogEntry.title == self.entries[-1].title: # we check if title is the same than last entry
                        self.entries[-1].description = self.entries[-1].description + entryDescription
                        newEntry  = False

                    if newEntry:
                        blogEntry.description = entryDescription
                        if blogEntry.videoID:
                            blogEntry.type = "video_blog"
                        else:
                            blogEntry.type = "textOnly"
                        self.entries.append( copy( blogEntry ) ) # we use copy in order to not to lose the value on next loop
                
        except Exception, e:
            print"Exception during getEntryList"
            print str(e)
            print str(sys.exc_info()[0])
            traceback.print_exc()
        if self.debug:
            print 'blogEntryListWebPage - entries:'
            print self.entries
            print 'blogEntryListWebPage - entries size'
            print len(self.entries)
        
        return self.entries

    def getCategoryList(self):
        """
        Extract data about categories from the AC blog collection webpage
        Parameters:
            - [out] List :list of categories
        """
        reStripCat      = re.compile(r'<div\ id=\"box-categories\".*?<ul>(.*?)</ul>', re.DOTALL) 
        reCategories    = re.compile(r'<li><a href="http://%s\.blog\.canal-plus\.com/(?P<catURL>.+?)\">(?P<catName>.+?)</a></li>'%BASE_BLOGNAME, re.DOTALL) 
        categoryList = []
       
        stripHtmlCategoriesList = reStripCat.findall( self.Source )
        stripHtmlCategories     = ""
        if len(stripHtmlCategoriesList) > 0:
            stripHtmlCategories = stripHtmlCategoriesList[0]

        categoryList.append( CategoryObject( "Accueil", "" ) )
        
        for i in reCategories.finditer(stripHtmlCategories):
            # Copy each item found in a list
            categoryList.append( CategoryObject( unicode( i.group( "catName" ), "utf-8" ).encode( "cp1252" ), i.group( "catURL" ) ) )
        if self.debug:
            print "blogEntryListWebPage - categoryList:"
            print categoryList

        return categoryList


class blogExternalEntryListWebPage(WebPage):
    """
    
    Inherit from WebPage super class
    Load on blog webiste a external video list webpage
    which include list of video to watch) and provides source code
    
    """
    def __init__( self, url, txData, txHearder, debug=False ):
        WebPage.__init__( self, url, txData, txHearder, debug )
        self.entries   = []
        self.txData    = txData
        self.txHearder = txHearder
        self.debug     = debug

    def _getFlashVideoListURL(self):
        """
        Extract URL of the flash webpage with video ID
        """
        reXML = re.compile(r"""function afficher_mea_trombi_(?P<zoneTemplateID>[0-9]+?)\(\).*?var sURL = "(?P<videoFlashPageURL>.*?)"\+page;""", re.DOTALL) 
        xml_url = None
        try:
            for i in reXML.finditer( self.Source ):
                xml_url = i.group( "videoFlashPageURL" )
        except Exception, e:
            print"Exception during getXMLURL"
            print str(e)
            print str(sys.exc_info()[0])
            traceback.print_exc()
        if self.debug:
            print 'blogExternalEntryListWebPage - _getFlashVideoListURL: xml_url:'
            print xml_url
        return BASE_URL_INFO + xml_url


    def getEntryList( self ):
        """
        Extract data about video files from the AC blog collection webpage
        Parameters:
        """
        #self.debug = True
        
        # Get the URL of flash page with video list
        videoListUrl = self._getFlashVideoListURL()
        
        if videoListUrl:
            # List exists
            videoListPage = blogExternalVideoListFlashWebPage( videoListUrl, self.txData, self.txHearder, self.debug, 0 ) 
            self.entries = videoListPage.getVideoList()
        
        if self.debug:
            print "blogExternalEntryListWebPage - getEntryList - videoListUrl"
            print videoListUrl
        return self.entries

class blogExternalVideoListFlashWebPage(WebPage):
    """
    
    Inherit from WebPage super class
    Load on blog webiste a video flash webpage 
    (external to the blog i.e http://www.canalplus.fr/c-cinema-en-salles/c-emissions-cinema/pid3008-c-p-l-hebd-hollywood.html)
    
    """
    def __init__( self, url, txData, txHearder, debug=False, pageIndex=0 ):
        WebPage.__init__( self, url + str(pageIndex), txData, txHearder, debug )
        self.entries   = []
        self.url       = url
        self.txData    = txData
        self.txHearder = txHearder
        self.debug     = debug
        self.pageIndex = pageIndex

    def getCurrentVideoID(self):
        """
        Extract curremt video ID from the flash webpage
        """
        video_id = None
        reVideo = re.compile(r"""http://www\.canalplus\.fr/flash/xml/configuration/configuration-embed-video-player\.php\?xmlParam=(?P<videoID>[0-9]+?)-[0-9]+?""", re.DOTALL) 
        try:
            video_id =  reVideo.findall( self.Source )[0]
        except Exception, e:
            print"Exception during getCurrentVideoID"
            print str(e)
            print str(sys.exc_info()[0])
            traceback.print_exc()
        if self.debug:
            print 'blogExternalVideoListFlashWebPage - video_id'
            print video_id
        return video_id

    def _isLastPage(self):
        """
        Check if a next page is available or not
        return True when a next page is available
        """
        reState = re.compile(r"""src=.http://media\.canal-plus\.com/design/front_office_wwwplus//images/fleches/droite_(?P<state>[a-zA-Z]*?)_v2.gif.""", re.DOTALL)
        result = True
        try:
            nextPageState =  reState.findall( self.Source )[0]
            if nextPageState:
                print nextPageState
                if nextPageState == "active":
                    result = False
        except Exception, e:
            print"Exception during isLastPage"
            print str(e)
            print str(sys.exc_info()[0])
            traceback.print_exc()
        if self.debug:
            print "blogExternalVideoListFlashWebPage - _isLastPage result:"
            print result
        return result

    def getVideoList(self):
        """
        Return video list from the flash list (bottom of the main page)
        """
        reVideo = re.compile(r"""<img width="80" height="60"  src="(?P<videoThumbURL>.*?)"  onclick="DisplayVideo\((?P<videoID>[0-9]+?)\);"/>.*?" class="txt-noir9">(?P<videoTitle>.*?(?P<videoDate>[0-9][0-9]/[0-9][0-9]/[0-9][0-9][0-9][0-9]+?).*?)</div>""", re.DOTALL) 
        try:
            for i in reVideo.finditer( self.Source ):
                # Copy each item found in a list
                videoEntry         = EntryObject()
                title              = i.group( "videoTitle" )
                videoEntry.videoID = i.group( "videoID" )
                videoEntry.type    = "video_external"

                if title: # !=None
                    #videoEntry.title = unicode( title, "utf-8" ).encode( "cp1252" )
                    videoEntry.title = unescape( strip_off( unicode( title, "utf-8" ).encode( "cp1252" ) ) )
                date = i.group( "videoDate" )
                if date:
                    #videoEntry.date  = unicode( date, "utf-8" ).encode( "cp1252" )
                    videoEntry.date = date
                    
# **** Move to the thread in order to improve performance on list loading *****                   
#                #videoEntry.shortDescURL = BASE_URL_VIDEO_INFO + videoEntry.videoID
#                # Get video description
#                try:
#                    videoDescriptText = WebPage( BASE_URL_VIDEO_INFO + videoEntry.videoID, self.txData, self.txHearder, self.debug ).Source
#                    #videoEntry.description = strip_off( unicode( videoDescriptText, "utf-8" ).encode( "cp1252" ) )
#                    videoEntry.description = strip_off( videoDescriptText )
#    
#            
#                except Exception, e:
#                    print"Exception during getVideoList, impossible to retrieve vide description"
#                    print str(e)
#                    print str(sys.exc_info()[0])
#                    traceback.print_exc()
# *****************************************************************************
                self.entries.append( copy( videoEntry ) ) # we use copy in order to not losing the value on next loop
        except Exception, e:
            print"Exception during getVideoList"
            print str(e)
            print str(sys.exc_info()[0])
            traceback.print_exc()
        
        # Check if a next page is availble
        if not self._isLastPage():
            # Recursive call on next page
            nextPage = blogExternalVideoListFlashWebPage( self.url, self.txData, self.txHearder, self.debug, self.pageIndex+1 )
            nextPageVideoList = nextPage.getVideoList()
            
            #Concatenate list
            self.entries.extend(nextPageVideoList)
        
        return self.entries

        
class BlogVideoXML(WebPage):
    """
    
    Inherit from WebPage super class
    Load on AC blog webiste a video XML page
    (which include video URL to watch) and provides source code
    
    """
    def __init__(self, url, txData, txHearder,debug=False):
        """
        - Init of WebPage
        - Load the Web page at the specific URL and copy the source code in self.Source
        """
        # Init super Class
        WebPage.__init__(self, url, txData, txHearder,debug)
        if debug:
            print("BlogVideoXML - Loading XML file: " + url)
        self.videoHQFileURL = ""
        self.videoLQFileURL = ""
        self.videoImageURL  = ""

        # Extract video File Name from the AC blog webpage
        soup = BeautifulStoneSoup(self.Source)
        self.videoHQFileURL = soup.find('hi').string.encode("utf-8")
        self.videoLQFileURL = soup.find('low').string.encode("utf-8")
        self.videoImageURL = soup.find("image").find('url').string.encode("utf-8")
    
    def getVideoURL(self,videoQuality):
        """
        Return URL of video files extracted from the AC blog webpage
        """
        if videoQuality == "HQ":
            return self.videoHQFileURL
        elif videoQuality == "LQ":
            return self.videoLQFileURL
        else:
            return self.videoHQFileURL

    def getVideoImageURL(self):
        """
        Return Video Image URL of video files extracted from the AC Blog webpage
        """
        return (self.videoImageURL)


class ConfigCtrl:
    """
    
    Controler of configuration
    
    """
    def __init__(self):
        """
        Load configuration file, check it, and correct it if necessary
        """
        self.is_conf_valid = False
        self.defaultPlayer = PLAYER_AUTO
        self.video_quality = "HQ"
        self.delCache      = False
        self.debug         = False
        try:
            # Create config parser
            self.config = ConfigParser.ConfigParser()
            
            # Read config from .cfg file
            # - Open config file
            self.config.read(os.path.join(ROOTDIR,"blog.cfg"))
            
            #TODO: check why conf is never valid at startup
            
            # Check sections exist
            if (self.config.has_section("system") == False):
                self.config.add_section("system")
                self.is_conf_valid = False
                
            # - Read config from file and correct it if necessary
            if (self.config.has_option("system", "player") == False):
                self.config.set("system", "player", self.defaultPlayer)
                self.is_conf_valid = False
            else:
                self.defaultPlayer = int(self.config.get("system", "player"))
            if (self.config.has_option("system", "video_quality") == False):
                self.config.set("system", "video_quality", self.video_quality)
                self.is_conf_valid = False
            else:
                self.video_quality = self.config.get("system", "video_quality")
            if (self.config.has_option("system", "cleancache") == False):
                self.config.set("system", "cleancache", self.delCache)
                self.is_conf_valid = False
            else:
                self.delCache = self.config.getboolean("system", "cleancache")
            if (self.config.has_option("system", "debug") == False):
                self.config.set("system", "debug", self.debug)
                self.is_conf_valid = False
            else:
                self.debug = self.config.getboolean("system", "debug")
            if (self.is_conf_valid == False):
                # Update file
                print "CFG file format wasn't valid: correcting ..."
                cfgfile=open(os.path.join(ROOTDIR,"blog.cfg"), 'w+')
                try:
                    self.config.write(cfgfile)
                    self.is_conf_valid = True
                except Exception, e:
                    print("Exception during setPassword")
                    print(str(e))
                    print (str(sys.exc_info()[0]))
                    traceback.print_exc()
                cfgfile.close()
        except Exception, e:
            print("Exception while loading configuration file " + "blog.cfg")
            print(str(e))
            print ( str( sys.exc_info()[0] ) )
            traceback.print_exc()
        
    def setDefaultPlayer(self,playerType):
        """
        set DefaultPlayerparameter locally and in .cfg file
        """
        self.defaultPlayer = playerType
        
        # Set player parameter
        self.config.set("system", "player", playerType)
        
        # Update file
        cfgfile=open(os.path.join(ROOTDIR,"blog.cfg"), 'w+')
        try:
            self.config.write(cfgfile)
        except Exception, e:
            print("Exception during setDefaultPlayer")
            print(str(e))
            print (str(sys.exc_info()[0]))
            traceback.print_exc()
        cfgfile.close()
        
    def getDefaultPlayer(self):
        """
        return the player currently used
        """
        return self.defaultPlayer
        
    def setVideoQuality(self,videoQuality):
        """
        set video quality parameter locally and in .cfg file
        """
        self.video_quality = videoQuality
        
        # Set player parameter
        self.config.set("system", "video_quality", videoQuality)
        
        # Update file
        cfgfile=open(os.path.join(ROOTDIR,"blog.cfg"), 'w+')
        try:
            self.config.write(cfgfile)
        except Exception, e:
            print("Exception during setVideoQuality")
            print(str(e))
            print (str(sys.exc_info()[0]))
            traceback.print_exc()
        cfgfile.close()
        
    def getVideoQuality(self):
        """
        return the video quality currently used
        """
        return self.video_quality

    def setCleanCache(self,cleanCacheStatus):
        """
        set clean cache status locally and in .cfg file
        @param cleanCacheStatus: clean cache status - define cache directory will be cleaned or not on exit
        """
        self.delCache = cleanCacheStatus
        
        # Set cachepages parameter
        self.config.set("system", "cleancache", self.delCache)

        # Update file
        cfgfile=open(os.path.join(ROOTDIR,"blog.cfg"), 'w+')
        try:
            self.config.write(cfgfile)
        except Exception, e:
            print("Exception during setCleanCache")
            print(str(e))
            print (str(sys.exc_info()[0]))
            traceback.print_exc()
        cfgfile.close()
        
    def getCleanCache(self):
        """
        return current clean cache status - define cache directory will be cleaned or not on exit
        """
        return self.delCache
    
    def setDebug(self,debugMode):
        """
        set debug status locally and in .cfg file
        @param debugMode
        """
        self.debug = debugMode
        
        # Set cachepages parameter
        self.config.set("system", "debug", self.debug)

        # Update file
        cfgfile=open(os.path.join(ROOTDIR,"blog.cfg"), 'w+')
        try:
            self.config.write(cfgfile)
        except Exception, e:
            print("Exception during setDebug")
            print(str(e))
            print (str(sys.exc_info()[0]))
            traceback.print_exc()
        cfgfile.close()
        
    def getDebug(self):
        """
        return debug mode
        """
        return self.debug


class fileMgr:
    """
    
    File manager
    
    """
    #TODO: Create superclass, inherit and overwrite init
    def __init__(self,checkList):
        for i in range(len(checkList)):
            self.verifrep(checkList[i]) 

    def verifrep(self, folder):
        """
        Source MyCine (thanks!)
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
            print ( str( sys.exc_info()[0] ) )
            traceback.print_exc()
            
    def listDirFiles(self, path):
        """
        List the files of a directory
        @param path:
        """
        dirList=os.listdir(path)
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



########
#
# Main
#
########

if __name__ == "__main__":
    # Calling startup function
    pass
else:
    # Library case
    pass
 

