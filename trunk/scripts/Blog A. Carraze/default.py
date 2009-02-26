# -*- coding: cp1252 -*-

"""
Le Blog d'Alain Carrazé Video HTML parser with GUI by Temhil (temhil@gmail.com)
 
24-11-08 Version 1.1 by Temhil
    - Fixed crash on video info since html code is not alwyas identical depending
      on the entry
    - Created regex for getting comment on video (not used yet)
18-10-08 Version 1.0 by Temhil
    - Created info window for videos
    - Fixed regex after changes on the website
    - Major update of the UI
    - Replaced regex by beautiful soup for the XML processing

26-04-08 Version Beta1 by Temhil
    - Creation

Les droits des diffusions et des images utilisées sont exclusivement
réservés à Canal+ 

"""

############################################################################
version = '1.2-Dev02'
date    = '26-02-09'
author  = 'Temhil'
############################################################################

############################################################################
# import  
############################################################################
from string import *
import sys, os.path
import re
import urllib, urllib2, cookielib, urlparse
import ConfigParser
import traceback
from time import gmtime, strptime, strftime
from copy import copy

try:
    import xbmcgui, xbmc
except ImportError:
    raise ImportError, 'This program requires the XBMC extensions for Python.'


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
#DOWNLOADDIR = os.path.join(ROOTDIR, "download")
LIBDIR      = os.path.join(ROOTDIR, "lib")

# List of directories to check at startup
dirCheckList   = (CACHEDIR,) #Tuple - Singleton (Note Extra ,)

# Adding to sys PATH lib path
sys.path.append(LIBDIR)

# Import lib
from BeautifulSoup import BeautifulStoneSoup #librairie de traitement XML


############################################################################
# Get actioncodes from keymap.xml
############################################################################

ACTION_MOVE_LEFT                 = 1    
ACTION_MOVE_RIGHT                = 2
ACTION_MOVE_UP                   = 3
ACTION_MOVE_DOWN                 = 4
ACTION_PAGE_UP                   = 5
ACTION_PAGE_DOWN                 = 6
ACTION_SELECT_ITEM               = 7
ACTION_HIGHLIGHT_ITEM            = 8
ACTION_PARENT_DIR                = 9
ACTION_PREVIOUS_MENU             = 10
ACTION_SHOW_INFO                 = 11

ACTION_PAUSE                     = 12
ACTION_STOP	                     = 13
ACTION_NEXT_ITEM                 = 14
ACTION_PREV_ITEM                 = 15

ACTION_CONTEXT_MENU              = 117

#############################################################################
# autoscaling values
#############################################################################

HDTV_1080i      = 0 #(1920x1080, 16:9, pixels are 1:1)
HDTV_720p       = 1 #(1280x720, 16:9, pixels are 1:1)
HDTV_480p_4x3   = 2 #(720x480, 4:3, pixels are 4320:4739)
HDTV_480p_16x9  = 3 #(720x480, 16:9, pixels are 5760:4739)
NTSC_4x3        = 4 #(720x480, 4:3, pixels are 4320:4739)
NTSC_16x9       = 5 #(720x480, 16:9, pixels are 5760:4739)
PAL_4x3         = 6 #(720x576, 4:3, pixels are 128:117)
PAL_16x9        = 7 #(720x576, 16:9, pixels are 512:351)
PAL60_4x3       = 8 #(720x480, 4:3, pixels are 4320:4739)
PAL60_16x9      = 9 #(720x480, 16:9, pixels are 5760:4739)

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
# Control alignment
#############################################################################
xbfont_left         = 0x00000000
xbfont_right        = 0x00000001
xbfont_center_x     = 0x00000002
xbfont_center_y     = 0x00000004
xbfont_truncated    = 0x00000008

#############################################################################
# Blog configuration
#############################################################################

BASE_BLOGNAME    = "alaincarraze"
#BASE_BLOGNAME    = "oscars"
#BASE_BLOGNAME    = "cesar"
#BASE_BLOGNAME    = "alamaisonblanche"
#BASE_BLOGNAME    = "didierallouch"
BASE_URL_WEBPAGE = "http://%s.blog.canal-plus.com/"%BASE_BLOGNAME
BASE_URL_XML     = "http://www.canalplus.fr/flash/xml/module/embed-video-player/embed-video-player.php?video_id="

# Set Headers
txdata = None
txheaders = {	
    'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.7) Gecko/20070914 Firefox/2.0.0.7'
}


def downloadJPG(source, destination):
    """
    Source MyCine (thanks!)
    Download IF NECESSARY a URL 'source' (string) to a URL 'target' (string)
    Source is downloaded only if target doesn't already exist
    """
    print("downloadJPG with source = " + source)
    print("downloadJPG with destination = " + destination)
    if os.path.exists(destination):
        print("downloadJPG destination already exist")
        pass
    else:
        try:
            print("downloadJPG destination doesn't exist, try to retrieve")
            loc = urllib.URLopener()
            loc.retrieve(source, destination)
        except Exception, e:
            print("Exception while source retrieving")
            print(e)
            pass

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
        self.name       = name
        self.url        = url
        self.entryList  = []
        self.dataLoaded = False
        

    def __repr__( self ):
        return "CategoryObject: ( %s, %s, %s, %s )" % ( self.name, self.url, self.entryList, self.dataLoaded ) 
    
    def __len__( self ):
        len( self.name ) + len( self.url ) + len ( self.entryList ) + len( self.dataLoaded )

class EntryObject:
    """
    Structure de donnees definissant un element de la liste
    """
    def __init__( self ):
        self.videoID     = None
        self.title       = ""
        self.date        = ""       
        self.description = ""
        self.fullDescURL = None
        self.imagePath   = os.path.join( IMAGEDIR,"noImageAvailable.jpg" )
        self.videoURL    = None
        

    def __repr__( self ):
        return "EntryObject: ( %s, %s, %s, %s, %s, %s, %s )" % ( self.videoID, self.title, self.date, self.description, self.fullDescURL, self.imagePath, self.videoURL ) 
    
    def __len__( self ):
        len( self.videoID ) + len( self.title ) + len( self.date ) + len ( self.description ) + len( self.fullDescURL ) + len( self.imagePath )+ len( self.videoURL )


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
                print "##########"
                print filename
                print "saving file at: %s"%(os.path.join(CACHEDIR, filename))
                open(os.path.join(CACHEDIR, filename),"w").write(self.Source)

        except Exception, e:
            print("Exception in WebPage init for URL: " + url)
            print(e)
            
            # pass the Exception
            raise e

class blogVideoDescriptWebPage(WebPage):
    """
    
    Inherit from WebPage super class
    Load on AC blog webiste a video description webpage
    
    """
    def GetVideoDescription(self):
        """
        Extract video description from the AC blog collection webpage
        Parameters:
            - [out] Video description
        """
        videoDate       = ""
        videoTitle      = ""
        videoDesciption = ""
        #reVideo     = re.compile(r'<h2 class="date"><span>(?P<videoDate>.+?)</span></h2>.*?<h3><span>(?P<videoTitle>.+?)</span></h3>.*?<div class=\"posttext-decorator2\">  <p>(?P<videoDescription>.+?)<br />', re.DOTALL) 
        reVideo     = re.compile(r'<h2 class="date"><span>(?P<videoDate>.+?)</span></h2>.*?<h3><span>(?P<videoTitle>.+?)</span></h3>.*?<div class=\"posttext-decorator2\">  <p>(?P<videoDescription_part1>.+?)<div id="playercontent.*?"playercontent.*?\);</script>(?P<videoDescription_part2>.*?)</p>   </div> </div> </div> <div class="postbottom"> <div class="postbottom-decorator1"> <div class="postbottom-decorator2"> <p class="posted">', re.DOTALL) 
        for i in reVideo.finditer(self.Source):
            # Copy each item found in a list
            videoDate       = unicode(i.group("videoDate"),"utf-8").encode("cp1252")
            videoTitle      = unicode(i.group("videoTitle"),"utf-8").encode("cp1252")
            videoDesciption = strip_off(unicode(i.group("videoDescription_part1"),"utf-8").encode("cp1252")) + strip_off(unicode(i.group("videoDescription_part2"),"utf-8").encode("cp1252"))
            #videoDesciption = re.sub(r"<.*?>", r"", (unicode(i.group("videoDescription"),"utf-8").encode("cp1252")))
        
        return videoDate,videoTitle,videoDesciption

    def GetVideoCommentsList(self):
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
            print "blogVideoDescriptWebPage - GetVideoCommentsList: "
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
        
    def GetEntryList( self ):
        """
        Extract data about video files from the AC blog collection webpage
        Parameters:
            - [out] dataObj: Data object (blogCollectionData) where data 
              extracted from the Webpage  will be appended 

        """
        self.debug = True
        reEntry = re.compile(r"""(<h2 class="date"><span>(?P<entryDate>.+?)</span></h2>)? *?<a id="(?P<entryID>[a-zA-Z][0-9]+?)"></a> <h3><span>(?P<entryTitle>.+?)</span></h3>.*?<div class=\"posttext-decorator2\">\ <p>(?P<entryContent>.+?)</p> </div> </div> </div>.*?<a href="http://%s\.blog\.canal-plus\.com/(?P<entryDescriptURL>archive.+?html)\">Lien permanent</a>"""%BASE_BLOGNAME, re.DOTALL) 
        #reVideo = re.compile(r"""(?P<videoDescription>.*?)<div id="playercontent(?P<videoID>[0-9]+?)">.*?"playercontent[0-9]+?"\);</script>|(?P<textOnly>.*+)""", re.DOTALL) 
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
                        self.entries.append( copy( blogEntry ) ) # we use copy in order to not losing the value on next loop
                
        except Exception, e:
            print"Exception during GetEntryList"
            print str(e)
            print str(sys.exc_info()[0])
            traceback.print_exc()
        print 'self.entries'
        print self.entries
        print 'len(self.entries)'
        print len(self.entries)
        
        return self.entries

    def GetCategoryList(self):
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

    def GetEntryList( self ):
        """
        Extract data about video files from the AC blog collection webpage
        Parameters:
            - [out] dataObj: Data object (blogCollectionData) where data 
              extracted from the Webpage  will be appended 

        """
        self.debug = True
        reEntry = re.compile(r"""(<h2 class="date"><span>(?P<entryDate>.+?)</span></h2>)? *?<a id="(?P<entryID>[a-zA-Z][0-9]+?)"></a> <h3><span>(?P<entryTitle>.+?)</span></h3>.*?<div class=\"posttext-decorator2\">\ <p>(?P<entryContent>.+?)</p> </div> </div> </div>.*?<a href="http://%s\.blog\.canal-plus\.com/(?P<entryDescriptURL>archive.+?html)\">Lien permanent</a>"""%BASE_BLOGNAME, re.DOTALL) 
        #reVideo = re.compile(r"""(?P<videoDescription>.*?)<div id="playercontent(?P<videoID>[0-9]+?)">.*?"playercontent[0-9]+?"\);</script>|(?P<textOnly>.*+)""", re.DOTALL) 
        reVideo = re.compile(r"""(?P<videoDescriptionWithID>.*?)<strong><a href="http://player.canalplus.fr/#/(?P<videoID>[0-9]+?)"|(?P<videoDescriptionWithLink>.+)<a href="(?P<videoPageURL>.*?)" target=""", re.DOTALL) 

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
                    videoID      = j.group( "videoID" )
                    videoPageURL = j.group( "videoPageURL" )
                    if videoID:
                        blogEntry.videoID      = videoID
                        videoDescriptionWithID = j.group( "videoDescriptionWithID" )
                        if videoDescriptionWithID:
                            blogEntry.description = strip_off( unicode( videoDescriptionWithID, "utf-8" ).encode( "cp1252" ) )
                            
                    elif videoPageURL:
                        # Load external video page and get video ID from it
                        print "**** videoPageURL"
                        print videoPageURL
                        externalFlashVideoPage = blogVideoExternalFlashWebPage( videoPageURL, self.txData, self.txHearder, self.debug ) 
                        blogEntry.videoID = externalFlashVideoPage.GetCurrentVideoID()
                        videoDescriptionWithLink = j.group( "videoDescriptionWithLink" )                        
                        if videoDescriptionWithLink:
                            blogEntry.description = strip_off( unicode( videoDescriptionWithLink, "utf-8" ).encode( "cp1252" ) )
                           
                    # Adding to the list
                    self.entries.append( copy( blogEntry ) ) # we use copy in order to not losing the value on next loop
                    #print '**** blogExternalEntryListWebPage - self.entries'
                    #print self.entries
                
        except Exception, e:
            print"Exception during GetEntryList"
            print str(e)
            print str(sys.exc_info()[0])
            traceback.print_exc()
        print 'self.entries'
        print self.entries
        print 'len(self.entries)'
        print len(self.entries)
        
        return self.entries

class blogVideoExternalFlashWebPage(WebPage):
    """
    
    Inherit from WebPage super class
    Load on blog webiste a video flash webpage 
    (external to the blog i.e http://www.canalplus.fr/c-cinema-en-salles/c-emissions-cinema/pid3008-c-p-l-hebd-hollywood.html)
    
    """
    def GetCurrentVideoID(self):
        """
        Extract curremt video ID from the flash webpage
        """
        video_id = None
        try:
            reVideo = re.compile(r"""http://www\.canalplus\.fr/flash/xml/configuration/configuration-embed-video-player\.php\?xmlParam=(?P<videoID>[0-9]+?)-[0-9]+?""", re.DOTALL) 
            video_id =  reVideo.findall( self.Source )[0]
            print 'video_id'
            print video_id
        except Exception, e:
            print"Exception during GetCurrentVideoID"
            print str(e)
            print str(sys.exc_info()[0])
            traceback.print_exc()
        return video_id


class blogVideoListWebPage(WebPage):
    """
    
    Inherit from WebPage super class
    Load on AC blog webiste a video list webpage
    which include list of video to watch) and provides source code
    
    """
    def GetVideoList(self, dataObj):
        """
        Extract data about video files from the AC blog collection webpage
        Parameters:
            - [out] dataObj: Data object (blogCollectionData) where data 
              extracted from the Webpage  will be appended 

        """
        self.debug = True
        #reVideo = re.compile(r"""<h2\ class=\"date\"><span>(?P<videoDate>.+?)</span></h2>.*?<h3><span>(?P<videoTitle>.+?)</span></h3>.*?<div id="playercontent(?P<videoID>[0-9]+?)">.+?[0-9]+?\:[0-9]+?.+?<a href="http://%s\.blog\.canal-plus\.com/(?P<videoDescriptURL>archive.+?html)\">Lien permanent</a>"""%BASE_BLOGNAME, re.DOTALL) 
        reVideo = re.compile(r"""(<h2 class="date"><span>(?P<videoDate>.+?)</span></h2>)? *?<a id="[a-zA-Z][0-9]+?"></a> <h3><span>(?P<videoTitle>.+?)</span></h3>.*?<div id="playercontent(?P<videoID>[0-9]+?)">.+?[0-9]+?\:[0-9]+?.+?<a href="http://%s\.blog\.canal-plus\.com/(?P<videoDescriptURL>archive.+?html)\">Lien permanent</a>"""%BASE_BLOGNAME, re.DOTALL) 
        #reVideo = re.compile(r"""(<h2 class="date"><span>(?P<videoDate>.+?)</span></h2>)?( *?<a id="[a-zA-Z][0-9]+?"></a> <h3><span>(?P<videoTitle>.+?)</span></h3>)?.*?<div id="playercontent(?P<videoID>[0-9]+?)">.+?[0-9]+?\:[0-9]+?(.+?<a href="http://%s\.blog\.canal-plus\.com/(?P<videoDescriptURL>archive.+?html)\">Lien permanent</a>)?"""%BASE_BLOGNAME, re.DOTALL) 

        ##TODO Exception on nothing found !!!!!!!!!!!!!!!!!!!!!!!!

        for i in reVideo.finditer(self.Source):
            # Copy each item found in a list
            dataObj.videoIDList.append(i.group("videoID"))
            if i.group("videoDate"):
                dataObj.videoDateList.append(unicode(i.group("videoDate"),"utf-8").encode("cp1252"))
            else:
                dataObj.videoDateList.append("")
            if i.group("videoTitle"):
                dataObj.videotitleList.append(unicode(i.group("videoTitle"),"utf-8").encode("cp1252"))
            else:
                dataObj.videotitleList.append("")
            if i.group("videoDescriptURL"): 
                dataObj.videoPageList.append(i.group("videoDescriptURL"))
            else:
                dataObj.videoPageList.append("")
            
        if self.debug: 
            print "blogVideoListWebPage : VideoList :"
            print dataObj.videoIDList
            print dataObj.videoDateList
            print dataObj.videotitleList
            print dataObj.videoPageList
            print 

    def GetCategoryList(self):
        """
        Extract data about categories from the AC blog collection webpage
        Parameters:
            - [out] List :list of categories
        """
        reStripCat      = re.compile(r'<div\ id=\"box-categories\".*?<ul>(.*?)</ul>', re.DOTALL) 
        reCategories    = re.compile(r'<li><a href="http://%s\.blog\.canal-plus\.com/(?P<catURL>.+?)\">(?P<catName>.+?)</a></li>'%BASE_BLOGNAME, re.DOTALL) 
       
        stripHtmlCategoriesList = reStripCat.findall(self.Source)
        stripHtmlCategories     = ""
        if len(stripHtmlCategoriesList) > 0:
            stripHtmlCategories = stripHtmlCategoriesList[0]
        categoryListName = []
        categoryListURL = []
        categoryListName.append("Accueil")
        categoryListURL.append("")
        
        for i in reCategories.finditer(stripHtmlCategories):
            # Copy each item found in a list
            categoryListName.append(unicode(i.group("catName"),"utf-8").encode("cp1252"))
            categoryListURL.append(i.group("catURL"))
        return categoryListName,categoryListURL
        
class blogVideoXML(WebPage):
    """
    
    Inherit from WebPage super class
    Load on AC blog webiste a video XML page
    (which include video URL to watch) and provides source code
    
    """
    def __init__(self, url, txData, txHearder,savehtml=False):
        """
        - Init of WebPage
        - Load the Web page at the specific URL and copy the source code in self.Source
        """
        # Init super Class
        WebPage.__init__(self, url, txData, txHearder,savehtml)

        print("Loading XML file: " + url)
        self.videoHQFileURL = ""
        self.videoLQFileURL = ""
        self.videoImageURL  = ""

        # Extract video File Name from the AC blog webpage
        soup = BeautifulStoneSoup(self.Source)
        self.videoHQFileURL = soup.find('hi').string.encode("utf-8")
        self.videoLQFileURL = soup.find('low').string.encode("utf-8")
        self.videoImageURL = soup.find("image").find('url').string.encode("utf-8")
    
    def GetVideoURL(self,videoQuality):
        """
        Return URL of video files extracted from the AC blog webpage
        """
        if videoQuality == "HQ":
            return self.videoHQFileURL
        elif videoQuality == "LQ":
            return self.videoLQFileURL
        else:
            return self.videoHQFileURL

    def GetVideoImageURL(self):
        """
        Return Video Image URL of video files extracted from the AC Blog webpage
        """
        return (self.videoImageURL)


class blogCollectionData:
    """
    
    Data Warehouse for datas extracted from collection web page(s) 
    (one or more depending on number of pages)
    
    """
    def __init__(self):
        """
        Init of blogCollectionData
        """
        self.dataLoaded	       = False # define if data has been extracted from a collection webpage
        self.numberOfPages     = 0     # number of webpage for a collection
        self.videoPageList     = []    # video page URL
        self.videotitleList    = []    # Title of a video    
        self.videoImageList    = []    # Video Image URL 
        self.videoIDList       = []    # Video ID
        self.videoDateList     = []    # Video Date

        print("blogCollectionData init DONE")

    def reset(self):
        """
        Reset of blogCollectionData attributes
        """
        self.dataLoaded	       = False
        self.numberOfPages     = 0
        self.videoPageList     = []
        self.videotitleList    = []
        self.videoImageList    = []
        self.videoIDList       = []
        self.videoDateList     = [] 
        print("blogCollectionData RESET DONE")
    
    def getNumberofItem(self):
        """
        Return the total number of item (videos) found for the collection
        """
        #print("NumberofItem for = " + str(self.videoPageList))
        #return len(self.videoPageList)
        return len(self.videoIDList)

class SelectCollectionWebpage:
    """
    
    Allow to select a Collection Webpage to process (i.e by vote, by date ...)
    
    """
    def __init__(self, pagebaseUrl, nameSelecList, urlSelectList):
        self.selectedMenu          = 0
        self.baseUrl              = pagebaseUrl
        self.selectionNameList      = nameSelecList
        self.selectionURLList      = urlSelectList
        self.selectCollecData      = []
        self.menulen              = len(nameSelecList)

        #TODO: check len(nameSelecList) == len(urlSelectList)

        # Filling selectCollecData
        for i in range(self.menulen):
            self.selectCollecData.append(blogCollectionData())


class configCtrl:
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
        self.delCache      = True
        self.debug         = False
        try:
            # Create config parser
            self.config = ConfigParser.ConfigParser()
            
            # Read config from .cfg file
            # - Open config file
            self.config.read(os.path.join(ROOTDIR,"blog.cfg"))
            
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

class SettingsWindow(xbmcgui.WindowDialog):
    """
    
    This window display settings
    
    """
    def __init__(self):
        if Emulating: xbmcgui.Window.__init__(self)
        if not Emulating:
            self.setCoordinateResolution(PAL_4x3) # Set coordinate resolution to PAL 4:3

    def setWindow(self,configManager):
        self.configManager   = configManager
        self.strListMaxSize  = 50
        self.playerMenuList  = ["Auto","DVD Player","MPlayer"]
        self.qualityMenuList = ["HQ","LQ"]
        self.cleanCacheList  = ["Activé","Désactivé"]
        
        # Background image
        self.addControl(xbmcgui.ControlImage(138,120,445,335, os.path.join(IMAGEDIR,"dialog-panel.png")))

        # Title label:
        self.strlist = xbmcgui.ControlLabel(138, 125, 445, 30, 'Options', 'special13',alignment=6)
        self.addControl(self.strlist)

        # Get settings
        self.defaultPlayer  = self.configManager.getDefaultPlayer()
        self.videoQuality   = self.configManager.getVideoQuality()
        self.cleanCache     = self.configManager.getCleanCache()
        
        
        # item Control List
        self.strDefaultPlayerTitle   = "Player vidéo: "
        self.strDefaultPlayerContent = self.playerMenuList[self.defaultPlayer]
        self.strVideoQualityTitle    = "Qualité vidéo: "
        self.strVideoQualityContent  = str(self.videoQuality)
        self.strCleanCacheTitle      = "Nettoyage auto du cache: "
        if self.cleanCache:
            self.strCleanCacheContent = self.cleanCacheList[0] #Activé
        else:
            self.strCleanCacheContent = self.cleanCacheList[1] #Désactivé
            
        self.settingsListData = [self.strDefaultPlayerTitle + self.strDefaultPlayerContent, self.strVideoQualityTitle + self.strVideoQualityContent, self.strCleanCacheTitle + self.strCleanCacheContent]
        self.settingsList = xbmcgui.ControlList(158, 170, 300 , 400,'font14', buttonTexture = os.path.join(IMAGEDIR,"list-black-nofocus.png"), buttonFocusTexture = os.path.join(IMAGEDIR,"list-black-focus.png"), itemTextXOffset=-10, itemHeight=30)
        self.addControl(self.settingsList)
            
        # OK button:
        self.buttonOK = xbmcgui.ControlButton(478, 170, 80, 30, "OK",font='font12', focusTexture = os.path.join(IMAGEDIR,"list-black-focus.png"), noFocusTexture  = os.path.join(IMAGEDIR,"list-black-nofocus.png"), alignment=6)
        self.addControl(self.buttonOK)
        
        self.settingsList.controlLeft(self.buttonOK)
        self.settingsList.controlRight(self.buttonOK)
        self.buttonOK.controlLeft(self.settingsList)
        self.buttonOK.controlRight(self.settingsList)

        for labelItem in self.settingsListData:
            displayListItem = (xbmcgui.ListItem(label = labelItem))
            # Add list item to the ControlList
            self.settingsList.addItem(displayListItem)
        self.setFocus(self.settingsList)
        
        # show this menu and wait until it's closed
        self.doModal()

    #TODO: Create a general update function???
        
    def onAction(self, action):
        if action == ACTION_PREVIOUS_MENU:
            #close the window
            self.close()
            
    def onControl(self, control):
        if control == self.settingsList:
            selectedIndex = self.settingsList.getSelectedPosition()
            print("selectedIndex = " + str(selectedIndex))
            if selectedIndex == 0:
                dialog = xbmcgui.Dialog()
                chosenIndex = dialog.select('Selectionner le Player désiré', self.playerMenuList)
                self.configManager.setDefaultPlayer(chosenIndex)
                self.defaultPlayer           = chosenIndex
                self.strDefaultPlayerContent = self.playerMenuList[self.defaultPlayer]
                self.settingsList.getListItem(selectedIndex).setLabel(self.strDefaultPlayerTitle + self.strDefaultPlayerContent)
            elif selectedIndex == 1:
                dialog = xbmcgui.Dialog()
                chosenIndex = dialog.select('Selectionner la Qualité vidéo désirée', self.qualityMenuList)
                self.configManager.setVideoQuality(self.qualityMenuList[chosenIndex])
                self.videoQuality            = self.qualityMenuList[chosenIndex]
                self.strVideoQualityContent  = str(self.videoQuality)
                self.settingsList.getListItem(selectedIndex).setLabel(self.strVideoQualityTitle + self.strVideoQualityContent)
                
            elif selectedIndex == 2:
                dialog = xbmcgui.Dialog()
                chosenIndex = dialog.select('Selectionner la gestion du cache désirée', self.cleanCacheList)
                if chosenIndex == 0:
                    self.configManager.setCleanCache(True)
                    self.cleanCache           = True
                    self.strCleanCacheContent = self.cleanCacheList[0] #Activé
                else:
                    self.configManager.setCleanCache(False)
                    self.cleanCache           = False
                    self.strCleanCacheContent = self.cleanCacheList[1] #Désactivé
                self.settingsList.getListItem(selectedIndex).setLabel(self.strCleanCacheTitle + self.strCleanCacheContent)
            else:
                print "SettingsWindow - onControl : Invalid control list index"

        elif control == self.buttonOK:
            self.close()

class AboutWindow(xbmcgui.WindowDialog):
    """
    
    About Window
    
    """
    def __init__(self):
        if Emulating: xbmcgui.Window.__init__(self)
        if not Emulating:
            self.setCoordinateResolution(PAL_4x3) # Set coordinate resolution to PAL 4:3

        self.addControl(xbmcgui.ControlImage(100,100,545,435, os.path.join(IMAGEDIR,"dialog-panel.png")))
        self.strTitle = xbmcgui.ControlLabel(130, 110, 350, 30, "Le Blog d'Alain Carrazé",'special13')
        self.addControl(self.strTitle)
        self.strVersion = xbmcgui.ControlLabel(130, 140, 350, 30, "Version: " + version)
        self.addControl(self.strVersion)
        self.strAuthor = xbmcgui.ControlLabel(130, 170, 350, 30, "Auteur: "+ author)
        self.addControl(self.strAuthor)        
        self.strDesTitle = xbmcgui.ControlLabel(130, 200, 350, 30, "Description: ")
        self.addControl(self.strDesTitle)        
        strContent = """Ce script vous permet de vous connecter sur le Blog d'Alain Carrazé 
(http://alaincarraze.blog.canal-plus.com) et de visionner les videos
du blog ainsi que d'en lire leur description.
"""
        self.strDesContent = xbmcgui.ControlLabel(130, 220, 490, 100, strContent, "font12", textColor='0xFFD3D3D3')
        self.addControl(self.strDesContent)

        self.strACTitle = xbmcgui.ControlLabel(130, 290, 350, 30, "A propos d'Alain Carrazé: ")
        self.addControl(self.strACTitle) 
               
        strAboutAC = """Depuis ses débuts en 1979 en tant que collaborateur de 'Temps X', l'émission de science-fiction, Alain CARRAZE à partagé ses passions pour le cinéma fantastique, les comics et surtout les séries TV à travers des émissions comme 'Fantasy' ( dans le cadre des 'Enfants du Rock' ) et principalement la cultissime 'Destination Séries', sur Canal Jimmy de 1992 à 2000 (pres de 225 éditions) , avec aussi des émissions spéciales comme le 'Marathon Friends', 'La Fête à Jerry Seinfeld', les Emmy Awards ou la 'Nuit Star Trek'.
A travers des magazines, aussi, comme 'Esode, le magazine de la culture séries', des hors-séries pour Mad Movies ou 'Episodik'. A travers des livres, enfin, avec des ouvrages comme 'Le Prisonnier, chef d'oeuvre télévisionnaire', ou sur 'Chapeau Melon et Bottes de Cuir ', 'Mission: Impossible', 'Les Grandes Séries' et, récemment, la mini-encyclopedie 'Les séries télé' dans la collection 'Toute les Clés '.
Il travaille sur des bonus de DVD ('Amicalement Vôtre', 'Le Prisonnier', 'Twin Peaks'), chronique aussi les séries à la radio et dans un grand quinzomadaire de programmes télé... et maintenant en exclusivité sur Canalplus.fr !
"""
        self.aboutACTextBox = xbmcgui.ControlTextBox(130, 310, 545-50, 145, font="font12", textColor='0xFFD3D3D3')
        self.addControl(self.aboutACTextBox)
        self.aboutACTextBox.setText(strAboutAC)
        self.aboutACTextBox.setVisible(True)
        self.setFocus(self.aboutACTextBox)
        
        strCopyRight = """Les droits des diffusions et des images utilisées sont exclusivement réservés
à Canal+"""
        self.strCopyRight = xbmcgui.ControlLabel(130, 465, 500, 20,strCopyRight, "font10",'0xFFFF0000')
        self.addControl(self.strCopyRight)
        
        self.doModal()
        
    def onAction(self, action):
        if action == ACTION_PREVIOUS_MENU:
            #close the window
            self.close()
            

class InfoWindow(xbmcgui.WindowDialog):
    """
    
    This window display informations about a video
    
    """
    def __init__(self):
        if Emulating: xbmcgui.Window.__init__(self)
        if not Emulating:
            self.setCoordinateResolution(PAL_4x3) # Set coordinate resolution to PAL 4:3

        # Background image
        self.addControl(xbmcgui.ControlImage(100,100,545,435, os.path.join(IMAGEDIR,"dialog-panel.png")))

        # Set the Video Image at top-left position
        self.videoPicture = xbmcgui.ControlImage(130,120,214,160, os.path.join(IMAGEDIR,"noImageAvailable.jpg"))
        self.addControl(self.videoPicture)
        self.videoPicture.setVisible(True)

    def updateImage(self,path):
        """
        Update the image of the video in the window
        """
        self.videoPicture.setImage(path)

    def updateInfo(self,videoDate,videoTitle,videoDesciption):
        """
        Set and fill the information for a video
        """
        print 'videoDesciption'
        print videoDesciption
        self.strDate = xbmcgui.ControlLabel(355, 120, 200, 30, videoDate,'special13')
        self.addControl(self.strDate)
        self.strTitle = xbmcgui.ControlLabel(355, 150, 270, 30, videoTitle,'special13')
        self.addControl(self.strTitle)
        self.descriptTextBox = xbmcgui.ControlTextBox(130, 285, 545-50, 210, font="font12", textColor='0xFFFFFFFF')
        self.addControl(self.descriptTextBox)
        self.descriptTextBox.setText(videoDesciption)
        self.descriptTextBox.setVisible(True)
        self.setFocus(self.descriptTextBox)
        

class MainWindow(xbmcgui.Window):
    """
    AC Blog main UI
    """
    def __init__(self):

        if Emulating: xbmcgui.Window.__init__(self)
        if not Emulating:
            self.setCoordinateResolution(PAL_4x3) # Set coordinate resolution to PAL 4:3
        # Create a file manager and check directory
        self.fileMgr = fileMgr(dirCheckList)

        # Check conf file
        self.configManager = configCtrl()
        
        # Display Loading Window while we are loading the information from the website
        dialogUI = xbmcgui.DialogProgress()
        dialogUI.create("Le Blog d'Alain Carrazé", "Creation de l'interface Graphique", "Veuillez patienter...")

        # Background image
        print ("Get Background image from : " + os.path.join(IMAGEDIR,"background.png"))
        self.addControl(xbmcgui.ControlImage(0,0,720,576, os.path.join(IMAGEDIR,"background.png")))
       
        # Set the Video logo at top-left position
        print ("Get Logo image from : " + os.path.join(IMAGEDIR,"logo.png"))
        self.user_logo = xbmcgui.ControlImage(550,25,130,97, os.path.join(IMAGEDIR, "portrait.jpg"))
        self.addControl(self.user_logo)
        self.user_logo.setVisible(True)

        # Extract categories from main webpage
        startupWebPage=blogEntryListWebPage(BASE_URL_WEBPAGE ,txdata,txheaders)
        print "Calling GetCategoryList"
        self.categoryList = startupWebPage.GetCategoryList()
        
        # Menu Control List
        self.currentMenuIdx = 0
        menuItemsize   = 30
        menuItemNumber = len(self.categoryList)
        if menuItemNumber > 11:
            menuItemNumber = 11 # We don't want to go outise the screen if the number of categories is too big
        menuListSize   = menuItemsize * menuItemNumber
        menuListWidth = 175
        self.Menulist = xbmcgui.ControlList( 25, 190, menuListWidth, menuListSize, space=0,font='font12', textColor='0xFF000000', itemTextXOffset=-5, buttonTexture=os.path.join( IMAGEDIR, "list-background.png" ), buttonFocusTexture=os.path.join( IMAGEDIR, "list-focus.png" ) )

        # Videos Control List
        self.list = xbmcgui.ControlList( 207, 140, 473, 380, space=8, itemHeight=80, font='font12', textColor='0xFF000000', itemTextXOffset=0, buttonFocusTexture=os.path.join( IMAGEDIR, "list-background.png" ), imageWidth=107, imageHeight=80 )

        # Title of the current page
        title =  "LE BLOG D'ALAIN CARRAZÉ"
        self.strMainTitle = xbmcgui.ControlLabel( 230, 40, 270, 20, title, 'special13','0xFF000000',alignment= 6 )

        # Current Catégories Title
        self.strButton = xbmcgui.ControlLabel( 230, 80, 270, 20, self.categoryList[ self.currentMenuIdx ].name, 'special13', '0xFF000000', alignment=6 )

        # List label:
        self.strlist = xbmcgui.ControlLabel( 250, 300, 260, 20, '', 'font12', '0xFFFF0000' )

        # Number of Video in the list:
        self.strItemNb = xbmcgui.ControlLabel( 600, 530, 150, 20, '0 entrée', 'font12', '0xFFFF0000' )

        # Version and author:
        self.strVersion = xbmcgui.ControlLabel( 230, 58, 270, 20,"v" + version,'font10', '0xFFFF0000', alignment=6 )


        self.addControl( self.list )
        self.addControl( self.Menulist )
        self.addControl( self.strButton )
        self.addControl( self.strlist )
        self.addControl( self.strMainTitle )
        self.addControl( self.strItemNb )
        self.addControl( self.strVersion )
          
        # Option button:
        self.buttonOption = xbmcgui.ControlButton( 25, 190 + menuListSize - menuItemsize + 5, menuListWidth, 30, "Options", font='font12', textColor='0xFF000000', focusTexture=os.path.join( IMAGEDIR, "list-focus.png" ), noFocusTexture=os.path.join( IMAGEDIR, "list-background.png" ), textXOffset=15 )
        self.addControl(self.buttonOption)

        # About button:
        self.buttonAbout = xbmcgui.ControlButton( 25, 220 + menuListSize - menuItemsize + 5, menuListWidth, 30, "A propos", font='font12', textColor='0xFF000000', focusTexture=os.path.join( IMAGEDIR, "list-focus.png" ), noFocusTexture=os.path.join( IMAGEDIR, "list-background.png" ), textXOffset=15 )
        self.addControl( self.buttonAbout )

        self.list.controlLeft( self.Menulist )
        self.Menulist.controlRight( self.list )
        self.Menulist.controlUp( self.buttonOption )
        self.Menulist.controlDown( self.buttonOption )
        self.buttonOption.controlRight( self.list )
        self.buttonOption.controlUp( self.Menulist )
        self.buttonOption.controlDown( self.buttonAbout )
        self.buttonAbout.controlRight( self.list )
        self.buttonAbout.controlUp( self.buttonOption )
        self.buttonAbout.controlDown( self.Menulist )

        # add items to the Menu list
        xbmcgui.lock()
#        for name in self.CollectionSelector.selectionNameList:         
#            self.Menulist.addItem(xbmcgui.ListItem(label = name))
        for category in self.categoryList:         
            self.Menulist.addItem( xbmcgui.ListItem( label=category.name ) )

        
        xbmcgui.unlock()


        # Set Focus on Menulist
        self.setFocus( self.Menulist )

        # Close the Loading Window 
        dialogUI.close()
       
        # Update the list of video 
        
        self.updateControlList( self.currentMenuIdx )
        # Start to diplay the window before doModal call
        self.show()
        
        # No UI is displayed, continue to get and display the picture (would be too long to wait if we were waiting doModla call)
        self.updateIcons( self.currentMenuIdx )

    def updateData(self, menuSelectIndex):
        """
        Update Data objet for a specific index (menu) 
        """
        # Display Loading Window while we are loading the information from the website
        dialogLoading = xbmcgui.DialogProgress()
        dialogLoading.create("Le blog d'Alain Carrazé", "Chargement des informations", "Veuillez patienter...")

        # Load Main webpage of Blog d'Alain Carrazé
#        if menuSelectIndex == 1: # 2nd entry: "1. EMISSION L'HEBD'HOLLYWOOD"
#            #TODO: clean that, this is a temporary fix but it won;t support website changes very well
#            myEntryListWebPage = blogExternalEntryListWebPage( BASE_URL_WEBPAGE + self.categoryList[ menuSelectIndex ].url, txdata, txheaders, self.configManager.getDebug() )   
#        else:
#            myEntryListWebPage = blogEntryListWebPage( BASE_URL_WEBPAGE + self.categoryList[ menuSelectIndex ].url, txdata, txheaders, self.configManager.getDebug() )
        myEntryListWebPage = blogEntryListWebPage( BASE_URL_WEBPAGE + self.categoryList[ menuSelectIndex ].url, txdata, txheaders, self.configManager.getDebug() )
        # Extract data from myCollectionWebPage and copy the content in corresponding Collection Data Instance
        self.categoryList[ menuSelectIndex ].entryList = myEntryListWebPage.GetEntryList()
        
        print 'len name'
        print len( self.categoryList[ menuSelectIndex ].name )
        print 'len entryList'
        print len( self.categoryList[ menuSelectIndex ].entryList )
#        myEntryListWebPage.GetCategoryList()
        
        # Update dataLoaded flag
        self.categoryList[ menuSelectIndex ].dataLoaded = True

        # Close the Loading Window 
        dialogLoading.close()


    def updateControlList( self, menuSelectIndex ):
        """
        Update ControlList objet
        """
        dialogimg = xbmcgui.DialogProgress()
        dialogimg.create("Le Blog d'Alain Carrazé", "Chargement des images", "Veuillez patienter...")
        try:
          
            # Check is data have already been loaded for this collection
            if (self.categoryList[ menuSelectIndex ].dataLoaded == False):
                # Never been updated before, go and get the data
                self.updateData( menuSelectIndex )
                
            #self.categoryList[ menuSelectIndex ].entryList

            # Get and Update number of video at the bottom of the page        
            #TODO: filter on video only not only on entry
            numberOfPictures = len( self.categoryList[ menuSelectIndex ].entryList )
            self.strItemNb.setLabel( str(numberOfPictures ) + " Entrées" ) 
                
            # Lock the UI in order to add pictures
            xbmcgui.lock()    

            # Clear all ListItems in this control list 
            self.list.reset()

            for entry in self.categoryList[ menuSelectIndex ].entryList:                
                index = self.categoryList[ menuSelectIndex ].entryList.index( entry )
               
                #pic = CACHEDIR + self.CollectionSelector.selectCollecData[menuSelectIndex].videoIDList[index] + ".jpg"
                title = entry.title
                date  = entry.date
                pic   = CACHEDIR + str( entry.videoID ) + ".jpg"
                if not os.path.exists( pic ):
                    # images not here use default
                    print"Image" + pic + "not found - use default image"
                    pic = entry.imagePath
                    
                # Add in the List pictures
                self.list.addItem( xbmcgui.ListItem( label=date + "\n" + title, thumbnailImage=pic ) )
                
            if not self.categoryList[ menuSelectIndex ].entryList:
                self.strlist.setLabel("Il n'y a pas d'émissions disponibles")
            else:
                self.strlist.setLabel( "" )
                # Set focus on the list
                self.setFocus( self.list )

            # Go back on 1st button (even if overwritten later)
            self.setFocus( self.Menulist )
        
            # Unlock the UI 
            xbmcgui.unlock()

            dialogimg.close()
        except Exception, e:
            print("Exception")
            print(e)
            print str( sys.exc_info()[0] )
            traceback.print_exc()

            dialogimg.update( 100 )

            # Unlock the UI 
            xbmcgui.unlock()
            dialogimg.close()
            dialogError = xbmcgui.Dialog()
            dialogError.ok( "Erreur", "Impossible de charger la liste des Video du à", "un probleme de connection ou à", "un changement sur le site distant" )



    def updateIcons( self, menuSelectIndex ):
        """
        Retrieve images and update list
        """
        # Now get the images:
        try:       
            for entry in self.categoryList[ menuSelectIndex ].entryList:
                
                #index = self.CollectionSelector.selectCollecData[menuSelectIndex].videoIDList.index(videoID) 
                index = self.categoryList[ menuSelectIndex ].entryList.index( entry )
                # Load video XML file
                if entry.videoID:
                    myVideoXMLPage = blogVideoXML( BASE_URL_XML + str( entry.videoID ), txdata, txheaders, self.configManager.getDebug() )
            
                    # Get the URL of the video picture
                    videoimg = myVideoXMLPage.GetVideoImageURL()
                    
                    # Get the URL of the video for later on
                    #TODO: cover case when video quality is change between here and video playing
                    entry.videoURL = myVideoXMLPage.GetVideoURL( self.configManager.getVideoQuality() )
        
                    videoimgdest = os.path.join( CACHEDIR, str( entry.videoID ) + ".jpg" )
        
                    #print("Try to Download : " + videoimg)
                    #print("at : " + videoimgdest)
                    if not os.path.exists( videoimgdest ):
                        # Download the picture    
                        try:
                            downloadJPG( videoimg, videoimgdest )
                            #print("Downloaded: " + videoimgdest)
                        except:
                            print("Exception on image download")
                            pass
                else:
                    videoimgdest = os.path.join(IMAGEDIR, "portrait.jpg")
                # Display the picture
                if os.path.exists( videoimgdest ):
                    entry.imagePath = videoimgdest
                    self.list.getListItem( index ).setThumbnailImage( entry.imagePath )
                    
        except Exception, e:
            print("Exception")
            print(e)
            print (str(sys.exc_info()[0]))
            traceback.print_exc()

    def showInfo( self, index ):
        try:       
            videoimg          = self.categoryList[ self.currentMenuIdx ].entryList[ index ].imagePath 
            myVideoTitle      = self.categoryList[ self.currentMenuIdx ].entryList[ index ].title
            myVideoDate       = self.categoryList[ self.currentMenuIdx ].entryList[ index ].date
            myVideoDesciption = self.categoryList[ self.currentMenuIdx ].entryList[ index ].description
                        
            # Create winInfoVideo
            winInfoVideo = InfoWindow()
            # Update image and info and display
            winInfoVideo.updateInfo( myVideoDate, myVideoTitle, myVideoDesciption )
            winInfoVideo.updateImage( videoimg )
            winInfoVideo.doModal()   
            del winInfoVideo
            
        except Exception, e:
            print("Exception in showInfo")
            print(e)
            print (str( sys.exc_info()[0]) )
            traceback.print_exc()
            dialogError = xbmcgui.Dialog()
            dialogError.ok("Erreur", "Impossible de charger les informations du à", "- un probleme de connection", "- un changement sur le site distant")
    

    def onAction(self, action):
        if action == ACTION_PREVIOUS_MENU:
            print('action received: previous')
            # Clean the cache is requested
            if self.configManager.getCleanCache() == True:
                print "Deleting cache"
                self.fileMgr.delFiles(CACHEDIR)
                
            self.close()

            
        if ( ( action == ACTION_SHOW_INFO ) or ( action == ACTION_CONTEXT_MENU ) ):
            # Show the information for a video
            chosenIndex = self.list.getSelectedPosition()
     
            # Display Loading Window while we are loading the information from the website
            self.showInfo(chosenIndex)

    def onControl( self, control ):
        if control == self.Menulist:
            self.currentMenuIdx = self.Menulist.getSelectedPosition()
            self.strButton.setLabel( self.categoryList[self.currentMenuIdx].name )
            self.updateControlList( self.currentMenuIdx )
            self.setFocus( self.Menulist )
            self.updateIcons( self.currentMenuIdx )

        elif control == self.buttonOption:
            winSettingsVideo = SettingsWindow()
            winSettingsVideo.setWindow( self.configManager ) # include doModal call
            del winSettingsVideo
            
        elif control == self.buttonAbout:
            winAboutVideo = AboutWindow()
            del winAboutVideo

        elif control == self.list:
            chosenIndex = self.list.getSelectedPosition()
    
            # Display Loading Window while we are loading the information from the website
#            dialogVideo = xbmcgui.DialogProgress()
#            dialogVideo.create("Blog d'Alain Carrazé", "Chargement des informations sur la vidéo", "Veuillez patienter...")
            try:
#                # Load video XML file
#                myVideoXMLPage = blogVideoXML( BASE_URL_XML + self.categoryList[self.currentMenuIdx].entryList[chosenIndex].videoID, txdata, txheaders, self.configManager.getDebug() )
#
#                # Update Progress bar (half of the job is done)
#                dialogVideo.update( 50 )
#      
#                # Get the URL of the video to play
#                video2playURL = myVideoXMLPage.GetVideoURL( self.configManager.getVideoQuality() )
#                dialogVideo.update( 100 )
#                dialogVideo.close()

                video2playURL = self.categoryList[ self.currentMenuIdx ].entryList[ chosenIndex ].videoURL
                if video2playURL:
                    # Play the selected video
                    print("Play the selected video: %s"%video2playURL)
                    xbmc.Player( self.configManager.getDefaultPlayer() ).play( video2playURL )
                else:
                    # Show the information for a video
                    chosenIndex = self.list.getSelectedPosition()
             
                    # Display Loading Window while we are loading the information from the website
                    self.showInfo(chosenIndex)

            except Exception, e:
                print("Exception")
                print(e)
                dialogVideo.update( 100 )
                dialogVideo.close()
                dialogError = xbmcgui.Dialog()
                dialogError.ok("Erreur", "Impossible de charger les informations du à", "un probleme de connection ou à", "un changement sur le site distant")
  
  



########
#
# Main
#
########

print("=============================================================================")
print("")
print("	    Le Blog d'Alain Carrazé " + version + " by "+ author +" HTML parser STARTS")
print("")
print("=============================================================================")

# Create main Window
bloggui = MainWindow()

# Display this window until close() is called
bloggui.doModal()

del bloggui

 

