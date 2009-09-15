# -*- coding: cp1252 -*-
"""
Gamekult Video by Temhil (temhil@gmail.com)

Description:
-----------
This script allows to watch videos on www.gamekult.com

Distribution rights and pictures are property of Gamekult.com

History:
-------
29-05-09 Version 1.0-Dev02 by Temhil
    - Passage a WindowXML de l'interface
    - Support de nouvelles categories video (Trailers, retro ...)
    - Adaptations aux modificationx du site web
27-04-08 Version Beta2-Dev02 by Temhil
26-04-08 Version Beta2-Dev01 by Temhil
    - Ajout de log pour debug sous Linux
24-04-08 Version Beta1 by Temhil:
    - Création du script basé sur le script Têtes à claques
     actuellement en cours de developement
    - Pour le moment le script ne supporte que la rubrique "l'émission":
     http://www.gamekult.com/tout/video/emission.html
     Le script permet de parcourir les 2 pages de la rubrique (mais pas plus),
     car les URLs de ces 2 pages sont actuellement codées en dur.
     Support dynamique du nombre de pages à venir
    - Le support d'autres rubriques est à venir
    - Attention les images son telerchargees dans le repertoire cache mais
     ne sont jamais effacées par le script (aussi à venir). Le bon coté,
     c'est le le scriot sera plus rapide à charger! ;-)

"""


############################################################################
# script constants
############################################################################
__script__ = "Gamekult Video"
__plugin__ = "Unknown"
__author__ = "Temhil"
__url__ = "http://passion-xbmc.org/index.php"
__svn_url__ = "http://code.google.com/p/passion-xbmc/source/browse/#svn/trunk/Scripts/Gamekult Video"
__credits__ = "Temhil"
__platform__ = "xbmc media center"
__date__ = "15-09-09"
__version__ = "1.0-Dev02"
__svn_revision__ = 0


############################################################################
# import
############################################################################
from string import *
import sys, os.path
import traceback
import ConfigParser
import re
import urllib, urllib2, cookielib
#from time import gmtime, strptime, strftime
from threading import Thread
try:
    import xbmcgui, xbmc
except ImportError:
    raise ImportError, 'This program requires the XBMC extensions for Python.'

#from resources.libs import language # Cutom language lib
from resources.libs.BeautifulSoup import BeautifulStoneSoup # XML parsing lib
from copy import copy, deepcopy

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
ROOTDIR = os.getcwd().replace( ";", "" ) # Create a path with valid format

IMAGEDIR    = os.path.join( ROOTDIR, "resources", "skins", "Default", "media" )
CACHEDIR    = os.path.join( ROOTDIR, "cache")
CONFDIR     = os.path.join( xbmc.translatePath( "P:\\script_data"  ), __script__ )

# List of directories to check at startup
dirCheckList   = ( CACHEDIR, CONFDIR, ) #Tuple - Singleton (Note Extra ,)



############################################################################
#get actioncodes from keymap.xml
############################################################################
#ACTION_MOVE_LEFT                 = 1
#ACTION_MOVE_RIGHT                = 2
#ACTION_MOVE_UP                   = 3
#ACTION_MOVE_DOWN                 = 4
#ACTION_PAGE_UP                   = 5
#ACTION_PAGE_DOWN                 = 6
#ACTION_SELECT_ITEM               = 7
#ACTION_HIGHLIGHT_ITEM            = 8
#ACTION_PARENT_DIR                = 9
ACTION_PREVIOUS_MENU             = 10
#ACTION_SHOW_INFO                 = 11
#ACTION_PAUSE                     = 12
#ACTION_STOP                      = 13
#ACTION_NEXT_ITEM                 = 14
#ACTION_PREV_ITEM                 = 15
#ACTION_MUSIC_PLAY                = 79
ACTION_MOUSE_CLICK               = 100
#ACTION_CONTEXT_MENU              = 117

#############################################################################
# Player values
#############################################################################
PLAYER_AUTO         = 0 # xbmc.PLAYER_CORE_AUTO
PLAYER_DVDPLAYER    = 1 # xbmc.PLAYER_CORE_DVDPLAYER
PLAYER_MPLAYER      = 2 # xbmc.PLAYER_CORE_MPLAYER
PLAYER_PAPLAYER     = 3 # xbmc.PLAYER_CORE_PAPLAYER
PLAYER_MODPLAYER    = 4 # xbmc.PLAYER_CORE_MODPLAYER

#############################################################################
# View mode values
#############################################################################
VIEWMODE_ICONS = 0
VIEWMODE_LIST  = 1

#############################################################################
# autoscaling values
#############################################################################
#HDTV_1080i      = 0 #(1920x1080, 16:9, pixels are 1:1)
#HDTV_720p       = 1 #(1280x720, 16:9, pixels are 1:1)
#HDTV_480p_4x3   = 2 #(720x480, 4:3, pixels are 4320:4739)
#HDTV_480p_16x9  = 3 #(720x480, 16:9, pixels are 5760:4739)
#NTSC_4x3        = 4 #(720x480, 4:3, pixels are 4320:4739)
#NTSC_16x9       = 5 #(720x480, 16:9, pixels are 5760:4739)
PAL_4x3         = 6 #(720x576, 4:3, pixels are 128:117)
#PAL_16x9        = 7 #(720x576, 16:9, pixels are 512:351)
#PAL60_4x3       = 8 #(720x480, 4:3, pixels are 4320:4739)
#PAL60_16x9      = 9 #(720x480, 16:9, pixels are 5760:4739)

#############################################################################
# Language
#############################################################################

#FONCTION POUR RECUPERER LES LABELS DE LA LANGUE.
__language__ = xbmc.Language( ROOTDIR, "french" ).getLocalizedString

#############################################################################
# Constant values
#############################################################################

INDEX_EMISSION    = 0
INDEX_TRAILERS    = 1
INDEX_GAMEPLAY    = 2
INDEX_RETRO       = 3
INDEX_INTERNAUTES = 4

LABEL_ID_EMISSION    = 100
LABEL_ID_TRAILERS    = 101
LABEL_ID_GAMEPLAY    = 102
LABEL_ID_RETRO       = 103
LABEL_ID_INTERNAUTES = 104

LABEL_EMISSION    = __language__( 100 )
LABEL_TRAILERS    = __language__( 101 )
LABEL_GAMEPLAY    = __language__( 102 )
LABEL_RETRO       = __language__( 103 )
LABEL_INTERNAUTES = __language__( 104 )

TYPE_EMISSION    = __language__( 100 )
TYPE_TRAILERS    = __language__( 101 )
TYPE_GAMEPLAY    = __language__( 102 )
TYPE_RETRO       = __language__( 103 )
TYPE_INTERNAUTES = __language__( 104 )


COLLEC_URL_EMISSION    = "http://www.gamekult.com/tout/video/emission.html"
COLLEC_URL_TRAILERS    = "http://www.gamekult.com/tout/video/trailers.html"
COLLEC_URL_GAMEPLAY    = "http://www.gamekult.com/tout/video/gameplay.html"
COLLEC_URL_RETRO       = "http://www.gamekult.com/tout/video/retro.html"
COLLEC_URL_INTERNAUTES = "http://www.gamekult.com/tout/video/internautes.html"



#############################################################################
# URLs
#############################################################################
gkvBasePageURL          = "http://www.gamekult.com/tout/video/"

emission1PageRelURL  = "emission_page1.html"
emission2PageRelURL  = "emission_page2.html"


# Selector list
gkvNameSelectList        = ( LABEL_ID_EMISSION, LABEL_ID_TRAILERS, LABEL_ID_GAMEPLAY, LABEL_ID_RETRO, LABEL_ID_INTERNAUTES, ) # "L'émission", "Trailers", "Gameplay", "Rétro", "Vos vidéos"
#gkvUrlSelectList         = ( collecDatesPageRelURL, collecSeriesPageRelURL, collecExtrasPageRelURL, collecPubPageRelURL )
gkvUrlSelectList         = ( COLLEC_URL_EMISSION, COLLEC_URL_TRAILERS, COLLEC_URL_GAMEPLAY, COLLEC_URL_RETRO, COLLEC_URL_INTERNAUTES, )
gkvCollecTypeSelectList  = ( "collection", "serie", "extras", "pub" )
gkvWebPageFileSelectList = ["populationCollection.xml","populationSeries.xml","populationExtras.xml","populationPubs.xml"]


collectionsConfigList = [
                            {
                             # INDEX_EMISSION = 0
                             "name": LABEL_EMISSION,
                             "type": TYPE_EMISSION,
                             "url" : COLLEC_URL_EMISSION,
                            },
                            {
                             # INDEX_TRAILERS = 1
                             "name": LABEL_TRAILERS,
                             "type": TYPE_TRAILERS,
                             "url" : COLLEC_URL_TRAILERS,
                            },
                            {
                             # INDEX_GAMEPLAY = 2
                             "name": LABEL_GAMEPLAY,
                             #"type": TYPE_GAMEPLAY,
                             "type": TYPE_TRAILERS,
                             "url" : COLLEC_URL_GAMEPLAY,
                            },
                            {
                             # INDEX_RETRO = 3
                             "name": LABEL_RETRO,
                             #"type": TYPE_RETRO,
                             "type": TYPE_TRAILERS,
                             "url" : COLLEC_URL_RETRO,
                            },
                            {
                             # INDEX_INTERNAUTES = 3
                             "name": LABEL_INTERNAUTES,
                             "type": TYPE_INTERNAUTES,
                             "url" : COLLEC_URL_INTERNAUTES,
                            },
                        ]



# Set tx
txdata = None
txheaders = {
    'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.7) Gecko/20070914 Firefox/2.0.0.7'
}


def downloadJPG( source, destination ):
    """
        Source MyCine (thanks!)
        Download IF NECESSARY a URL 'source' (string) to a URL 'target' (string)
        Source is downloaded only if target doesn't already exist
    """
    if os.path.exists( destination ):
        pass
    else:
        try:
            #print("downloadJPG destination doesn't exist, try to retrieve")
            loc = urllib.URLopener()
            loc.retrieve( source, destination )
        except Exception, e:
            print( "Exception while source retrieving" )
            print(e)
            print ( str( sys.exc_info()[0] ) )
            traceback.print_exc()

def strip_off( text, by="", xbmc_labels_formatting=False ):
    """
    Retrieves text in a tag and convert it to a XBMC format
    Thanks to the auhtor Frost
    """
    if xbmc_labels_formatting:
        print xbmc_labels_formatting
        text = text.replace( "<", "[" ).replace( ">", "]" )
    return ( re.sub( "(?s)<[^>]*>", by, text ) ).strip()


class fileMgr:
    """

        File manager

    """
    #TODO: Create superclass, inherit and overwrite init
    def __init__( self, checkList ):
        for i in range( len( checkList ) ):
            self.verifrep( checkList[i] )

    def verifrep(self, folder):
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

    def listDirFiles( self, path ):
        """
            List the files of a directory
            @param path:
        """
        dirList=os.listdir( path )
        return dirList

    def deleteFile( self, filename ):
        """
            Delete a file form download directory
            @param filename:
        """
        os.remove( filename )

    def delFiles( self, folder ):
        """
            From Joox
            Deletes all files in a given folder and sub-folders.
            Note that the sub-folders itself are not deleted.
            Parameters : folder=path to local folder
        """
        try:
            for root, dirs, files in os.walk( folder , topdown=False ):
                for name in files:
                    os.remove( os.path.join( root, name ) )
        except Exception, e:
            print "delFiles: __init__: While deleting file",e
            print ( "error delFiles: " + str( sys.exc_info()[0] ) )
            traceback.print_exc()

    def  extract( self, archive, targetDir ):
        """
            Extract an archive in targetDir
        """
        xbmc.executebuiltin( 'XBMC.Extract(%s,%s)'%( archive, targetDir ) )


class configCtrl:
    """

        Controler of configuration

    """
    def __init__( self ):
        """
            Load configuration file, check it, and correct it if necessary
        """
        self.is_conf_valid = True
        self.defaultPlayer = PLAYER_AUTO
        self.delCache      = False
        self.viewMode      = VIEWMODE_LIST
        try:
            # Create config parser
            self.config = ConfigParser.ConfigParser()

            # Read config from .cfg file
            # - Open config file
            self.config.read(os.path.join(CONFDIR, "gkv.cfg"))

            # Check sections exist
            if ( self.config.has_section( "system" ) == False ):
                self.config.add_section( "system" )
                self.is_conf_valid = False
            if ( self.config.has_section( "user" ) == False ):
                self.config.add_section( "user" )
                self.is_conf_valid = False

            # - Read config from file and correct it if necessary
            if ( self.config.has_option( "system", "player" ) == False ):
                self.config.set( "system", "player", self.defaultPlayer )
                self.is_conf_valid = False
            else:
                self.defaultPlayer = int( self.config.get( "system", "player" ) )
            if ( self.config.has_option( "system", "cleancache" ) == False ):
                self.config.set( "system", "cleancache", self.delCache )
                self.is_conf_valid = False
            else:
                self.delCache = self.config.getboolean( "system", "cleancache" )
            if ( self.config.has_option( "user", "viewmode" ) == False ):
                self.config.set( "user", "viewmode", self.viewMode )
                self.is_conf_valid = False
            else:
                self.viewMode = int( self.config.get( "user", "viewmode" ) )
            if ( self.is_conf_valid == False ):
                # Update file
                print "CFG file format wasn't valid: correcting ..."
                #cfgfile=open(os.path.join(ROOTDIR, "resources", "gkv.cfg"), 'w+')
                cfgfile = open( os.path.join( CONFDIR, "gkv.cfg" ), 'w+' )
                try:
                    self.config.write( cfgfile )
                    self.is_conf_valid = True
                except Exception, e:
                    print( "Exception during setPassword" )
                    print( str( e ) )
                    print ( str( sys.exc_info()[0] ) )
                    traceback.print_exc()
                cfgfile.close()
        except Exception, e:
            print( "Exception while loading configuration file " + "gkv.cfg" )
            print( str( e ) )

    def setDefaultPlayer( self, playerType, save=True ):
        """
            set DefaultPlayerparameter locally and in .cfg file
        """
        self.defaultPlayer = playerType

        # Set player parameter
        self.config.set( "system", "player", playerType )

        if save:
            # Update file
            cfgfile = open( os.path.join( CONFDIR, "gkv.cfg" ), 'w+' )
            try:
                self.config.write( cfgfile )
            except Exception, e:
                print( "Exception during setDefaultPlayer" )
                print( str( e ) )
                print ( str( sys.exc_info()[0] ) )
                traceback.print_exc()
            cfgfile.close()

    def getDefaultPlayer( self ):
        """
            return the player currently used
        """
        return self.defaultPlayer


    def setCleanCache( self, cleanCacheStatus, save=True ):
        """
            set clean cache status locally and in .cfg file
            @param cleanCacheStatus: clean cache status - define cache directory will be cleaned or not on exit
        """
        self.delCache = cleanCacheStatus

        # Set cachepages parameter
        self.config.set( "system", "cleancache", self.delCache )

        if save:
            # Update file
            cfgfile = open( os.path.join( CONFDIR, "gkv.cfg" ), 'w+' )
            try:
                self.config.write( cfgfile )
            except Exception, e:
                print( "Exception during setCleanCache" )
                print( str( e ) )
                print ( str( sys.exc_info()[0] ) )
                traceback.print_exc()
            cfgfile.close()

    def getCleanCache( self ):
        """
            return current clean cache status - define cache directory will be cleaned or not on exit
        """
        return self.delCache

    def setViewMode( self, viewMode, save=True ):
        """
            set View Mode locally and in .cfg file
        """
        self.viewMode = viewMode

        # Set player parameter
        self.config.set( "user", "viewmode", self.viewMode )

        if save:
            # Update file
            cfgfile = open( os.path.join( CONFDIR, "gkv.cfg" ), 'w+' )
            try:
                self.config.write( cfgfile )
            except Exception, e:
                print( "Exception during setViewMode" )
                print( str( e ) )
                print ( str( sys.exc_info()[0] ) )
                traceback.print_exc()
            cfgfile.close()

    def getViewMode( self ):
        """
            return the View Mode  currently used
        """
        return self.viewMode

    def saveConfFile( self ):
        # Update file
        result  = True
        cfgfile = open( os.path.join( CONFDIR, "gkv.cfg" ), 'w+' )
        try:
            self.config.write( cfgfile )
        except Exception, e:
            result = False
            print( "Exception during setCleanCache" )
            print( str( e ) )
            print( str( sys.exc_info()[0] ) )
            traceback.print_exc()
        cfgfile.close()
        return result

class WebPage:
    """

        Load a remote Web page (html,xml) and provides source code using cookies

    """
    #def __init__( self, baseURL, params, selection, classification='date', langue='fr-ca', pageNb='1', geolocation='fr', savehtml=True, filename="defaut.html", check_connexion=True ):
    def __init__( self, url, txData, txHearder, savehtml=True, filename="defaut.html" ):
        """
            Init of WebPage
            Load the Web page at the specific URL
            and copy the source code in self.Source
        """
        try:
            # CookieJar objects support the iterator protocol for iterating over contained Cookie objects.
            cj = cookielib.CookieJar()
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
            req = urllib2.Request(url, txData, txHearder)
            u = opener.open(req)
            headers = u.info()
            self.Source = u.read()
            #print("htmlSource created for URL: " + url)

            print( "WebPage created for URL: " + url )
            if savehtml == True:
                print "saving file at: %s"%( os.path.join( CACHEDIR, filename ) )
                open( os.path.join( CACHEDIR, filename ),"w" ).write( self.Source )
        except Exception, e:
            print( "Exception in WebPage init for URL: " + url )
            print( e )
            print ( str( sys.exc_info()[0] ) )
            traceback.print_exc()

            # pass the Exception
            raise

class EmissionVideoListWebPage(WebPage):
    """

        Inherit from WebPage super class
        Load on Gamekult Video webiste a video list webpage
        which include list of video to watch) and provides source code

    """
    def getVideoList( self ):
        """
            Extract data about video files from the
            a Gamekult video collection webpage

            Parameters:
                - dataObj: Data object (CollectionData) where data
                           extrated from the Webpage  will be appended
        """
        videoEntriesList = []
        # Example of strings we are looking for:
        #   <a href="/video/15040800/" title="Voir l'émission"><img src="http://img2.kult-mag.com/images/emission/15040800.jpg"
        #   <a href="/video/18030800/" title="Voir l'émission"><b>Diffusée le 18/03/2008</b><br><b>Vues
        #reVideo  = re.compile(r"<a href=\"/video/(?P<videoID>[0-9]+?)/\" title=\"Voir l'émission\"><img src=\"(?P<videoImageURL>.+?)\"(.*?)<a href=\"/video/(?P<videoID2>[0-9]+?)/\" title=\"Voir l'émission\"><b>(?P<title>.+?)</b><br><b>Vues", re.DOTALL)
        #reVideo  = re.compile(r"""<a href=\"/video/(?P<videoID>[0-9]+?)/\" title=\"Voir l'.+?mission\"><img src=\"(?P<videoImageURL>.+?)\".*?<a href=\"/video/[0-9]+?/\" title=\"Voir l'.+?mission\"><b>(?P<date>.+?)</b><br><b>Vues.*?<li class=orange>(?P<title>.+?)<br>""", re.DOTALL)
        reVideo  = re.compile(r"""<a href=\"/video/(?P<videoID>[0-9]+?)/\" title=\"Voir l'.mission\"><h3>(?P<title>.+?)</h3>.*?title=\"Voir l'.mission\"><img src=\"(?P<videoImageURL>.+?)\".*?<a href=\"/video/[0-9]+?/\" title=\"Voir l'.mission\"><b>(?P<date>.+?)</b><br><b>Vues\ \:</b>\ (?P<hits>[0-9]+?)\ Hits.*?Note.*?etoilesmall/(?P<notex2>[0-9]+?)\.gif.*?Au sommaire\ \:</b><br>(?P<sommaireraw>.+?)<br></a></td></tr></table>""", re.DOTALL)
        try:
            for i in reVideo.finditer(self.Source):

                # Copy each item found in a list
                videoEntry              = Entry()
                videoEntry.title        = i.group( "title" )
                videoEntry.videoID      = i.group( "videoID" )
                videoEntry.videoURL     = "http://www.gamekult.com/video/" + i.group( "videoID" ) + "/" # URL of the webpage of the video (description, XML URL ...)
                videoEntry.imageURL     = i.group( "videoImageURL" )
                videoEntry.date         = i.group( "date" )

                #TODO : add support of following field
                sommaireraw = strip_off( i.group( "sommaireraw" ) )
                print 'summary'
                print sommaireraw
                videoEntry.summary      = sommaireraw   # Description about the video (text)
                videoEntry.note         = float( i.group( "notex2" ) )/2 # Note of the video
                videoEntry.hits         = int( i.group( "hits" ) ) # Hits number on the video
                self.type               = None # Type of the entry

                print "Note: %d"%videoEntry.note
                print "Hits: %d"%videoEntry.hits



                # TODO: pass im param entries[] from collection
                # TODO: pass im param entries[] from collection
                # TODO: pass im param entries[] from collection

                videoEntriesList.append( copy( videoEntry ) ) # we use copy in order to not losing the value on next loop


        except Exception, e:
            print"Exception during getVideoList"
            print str(e)
            print str(sys.exc_info()[0])
            traceback.print_exc()

        return videoEntriesList

    def getNextPageURL(self):
        """
        get next page url
        """
        nextPageURL = None
        renp  = re.compile(r"""\|  <a href="/tout/video/(?P<nextpageurl>.+?)">Suivante</a></center><br>""", re.DOTALL)
        try:
            for i in renp.finditer(self.Source):

                # Copy each item found in a list
                nextPageURL        = i.group("nextpageurl")
                if nextPageURL != None:
                    nextPageURL = gkvBasePageURL + nextPageURL
                    break
        except Exception, e:
            print"Exception during getNextPageURL"
            print str(e)
            print str(sys.exc_info()[0])
            traceback.print_exc()

        print "nextPageURL:"
        print nextPageURL
        return nextPageURL


class TrailersVideoListWebPage(WebPage):
    """

        Inherit from WebPage super class
        Load on Gamekult Video webiste a video list webpage
        which include list of video to watch) and provides source code

    """
    def getVideoList( self ):
        """
            Extract data about video files from the
            a Gamekult video collection webpage

            Parameters:
                - dataObj: Data object (CollectionData) where data
                           extrated from the Webpage  will be appended
        """
        videoEntriesList = []
        # Example of strings we are looking for:
        #   <a href="/video/15040800/" title="Voir l'émission"><img src="http://img2.kult-mag.com/images/emission/15040800.jpg"
        #   <a href="/video/18030800/" title="Voir l'émission"><b>Diffusée le 18/03/2008</b><br><b>Vues
        #reVideo  = re.compile(r"<a href=\"/video/(?P<videoID>[0-9]+?)/\" title=\"Voir l'émission\"><img src=\"(?P<videoImageURL>.+?)\"(.*?)<a href=\"/video/(?P<videoID2>[0-9]+?)/\" title=\"Voir l'émission\"><b>(?P<title>.+?)</b><br><b>Vues", re.DOTALL)
        reVideo  = re.compile(r"""<td\ class=\"size2v\"\ align=\"left\">.*?align=\"absmiddle\">(?P<title>.+?)</a>.*?background-image\:url\((?P<videoImageURL>.+?)\)"><a href=\"/video/(?P<videoID>[0-9]+?)/\"\ title=\"(?P<title2>.+?)\"""", re.DOTALL)
        try:
            for i in reVideo.finditer(self.Source):

                # Copy each item found in a list
                videoEntry              = Entry()
                videoEntry.title        = strip_off( i.group("title") )
                videoEntry.videoID      = i.group("videoID")
                videoEntry.videoURL     = "http://www.gamekult.com/video/" + i.group("videoID") + "/" # URL of the webpage of the video (description, XML URL ...)
                videoEntry.imageURL     = i.group("videoImageURL")
                #videoEntry.date         = i.group("date")
                videoEntry.date         = ""

                #TODO : add support of following field
                #videoEntry.summary      = ""   # Description about the video (text)

                #TODO get full description of the video here
                videoEntry.summary      = i.group("title2")
                videoEntry.note         = None # Note of the video
                videoEntry.hits         = None # Hits number on the video
                self.type               = None # Type of the entry





                # TODO: pass im param entries[] from collection
                # TODO: pass im param entries[] from collection
                # TODO: pass im param entries[] from collection

                videoEntriesList.append( copy( videoEntry ) ) # we use copy in order to not losing the value on next loop


        except Exception, e:
            print"Exception during getVideoList"
            print str(e)
            print str(sys.exc_info()[0])
            traceback.print_exc()

        return videoEntriesList

    def getNextPageURL(self):
        """
        """
        pass

class VideoWebPage(WebPage):
    """

        Inherit from WebPage super class
        Load on Gamekult Video webiste a video Webpage
        (which include video XML URL) and provides source code

    """
    def __init__(self, url, txData, txHearder):
        """
            Load the Web page at the specific URL and copy the source code in self.Source
        """
        # Init super Class
        WebPage.__init__(self, url, txData, txHearder)

        # Extract video XML File URL from the gkv video webpage
        #print("Extract video XML File URL from the gkv video webpage")
        try:
            # Example of strings we are looking for:
            #   so.addVariable('paramsURI', '/fiche/video_xml.html?video=0E15040800');
            #reXMLPath  = re.compile(r"so\.addVariable\(\'paramsURI\'\,\ \'(?P<XMLFileURL>.+?)\'\)\;", re.DOTALL)
            reXMLPath  = re.compile(r"""so\.addVariable\('xspf'\,\ '(?P<XMLFileURL>.+?)'\);""", re.DOTALL)
            print ("VideoWebPage __init__ : Starting loop")
            for i in reXMLPath.finditer(self.Source):
                #self.videoXMLFileURL = "http://www.gamekult.com" + i.group("XMLFileURL")
                self.videoXMLFileURL = i.group("XMLFileURL")
                print ("Video XML File URL: " + self.videoXMLFileURL)

            #print ("Video XML File URL: " + self.videoXMLFileURL)
        except Exception, e:
            print"Exception during VideoWebPage __init__ - impossible de to retrieve data from Webpage"
            print str(e)
            print str(sys.exc_info()[0])
            traceback.print_exc()

    def getVideoXMLURL(self):
        """
            Return URL of video files extracted from the GKV video webpage
        """
        print("VideoWebPage - getVideoXMLURL starts ...")
        print("videoXMLFileURL " + self.videoXMLFileURL)
        return (self.videoXMLFileURL)


class VideoXML(WebPage):
    """

        Inherit from WebPage super class
        Load on Gamekult Video webiste a video XML page
        (which include video URL to watch) and provides source code

    """
    def __init__(self, url, txData, txHearder):
        """
            Load the Web page at the specific URL and copy the source code in self.Source
        """
        # Init super Class
        WebPage.__init__(self, url, txData, txHearder)

        # Extract video File Name from the GKV video webpage
        try:
            # Example of strings we are looking for:
            #   <URI>http://media.cnetnetworks.fr/cnettv-fr/2008/gamekult/gamekult-038-20080422.flv</URI>
            reVidPath  = re.compile(r"<location>(?P<videoFileURL>.+?)</location>", re.DOTALL)
            for i in reVidPath.finditer(self.Source):
                self.videoFileURL = i.group("videoFileURL")
                #print ("Video File Name: " + self.videoFileURL)
        except Exception, e:
            print"Exception during VideoXML __init__ - impossible de to retrieve data from XML"
            print str(e)
            print str(sys.exc_info()[0])
            traceback.print_exc()

    def GetVideoURL(self):
        """
            Return URL of video files extracted from the GKV video webpage
        """
        print("VideoXML - GetVideoURL starts ...")
        print("videoFileURL" + self.videoFileURL)
        return (self.videoFileURL)



class Element:
    """
    Data structure defining an element used by the GUI
    """
    def __init__( self ):
        self.title     = ""
        self.date      = ""
        self.summary   = ""   # Description about the video (text)
        self.note      = None # Note of the video
        self.hits      = None # Hits number on the video
        self.imagePath = os.path.join( IMAGEDIR,"noImageAvailable.jpg" )

    def __repr__( self ):
        return "EntryObject: ( %s, %s, %s, %s, %s, %s )" % ( self.title, self.date, self.summary, self.note, self.hits, self.imagePath )

    def __len__( self ):
        len( self.title ) + len( self.date ) + len( self.summary ) + len ( self.note ) + len( self.hits ) + len( self.imagePath )

class Entry(Element):
    """
    Data structure defining a list entry (specilization of Element) used by the collection (so need more info)
    Inherits from super class Element:
            self.title        = ""
            self.date         = ""
            self.note         = None # Note of the video
            self.hits         = None # Hits number on the video
            self.imagePath    = os.path.join( IMAGEDIR,"noImageAvailable.jpg" )
    """
    def __init__( self ):
        Element.__init__( self )
        self.videoID      = None
        self.videoPageURL = None # URL of the webpage of the video (description, XML URL ...)
        self.description  = None # Description about the video (text)
        self.videoURL     = None
        self.imageURL     = None # Image URL
        self.type         = None # Type of the entry


    def __repr__( self ):
        return "EntryObject: ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s )" % ( self.title, self.date, self.summary, self.note, self.hits, self.imagePath, self.videoID, self.videoPageURL, self.description, self.videoURL, self.imageURL, self.type )

    def __len__( self ):
        len( self.title ) + len( self.date ) + len( self.summary ) + len( self.note ) + len( self.hits ) + len( self.imagePath ) + len( self.videoID ) + len( self.videoPageURL ) + len ( self.description ) + len( self.videoURL ) + len( self.imageURL ) + len( self.type )

class CollectionIterator:
    """
    An iterator over a collection
    """
    def __init__( self, collection ):
        self.collection = collection
        self.currentEntryIdx = 0
        #self.removedLastElement = False

    def hasMoreElements( self ):
        """
        Tests if there are more element available in the Collection. If this method returns true, then a subsequent call to nextElement with no argument will successfully return a Element.
        """
        print "len( self.collection.entryList ) : %d"%len( self.collection.entryList )
        print "self.currentEntryIdx: %d"%self.currentEntryIdx
        if ( ( len( self.collection.entryList ) > 0 ) and ( len( self.collection.entryList ) > self.currentEntryIdx ) ):
            return True
        else:
            return False

    def nextElement( self ):
        """
        Returns the next Element available in the Collection with only basic info: Video Title, Date, Summary, Note, Hits, Image URL
        """
        result = None
        if ( len( self.collection.entryList ) > self.currentEntryIdx ):
            result = self.collection.entryList[self.currentEntryIdx]
            self.currentEntryIdx = self.currentEntryIdx + 1
        return result

#    def removeElement( self ):
#        """
#        Removes from the underlying collection the last element returned by the iterator (optional operation).
#        This method can be called only once per call to next.
#        """
#        del self.entryList[self.currentEntryIdx]
#        #TODO: cover next element case after a removal of current element
#        self.removedLastElement = True

    def reset( self ):
        """
        Reset an iterator (optional operation)
        """
        self.currentEntryIdx = 0


class Collection:
    """
        Represents a collection of video and provides methods in order to retrieve info from it
        Use Design Pattern State
    """
    def __init__( self, name="", url=None ):
        self.name               = name
        self.url                = url
        self.entryList          = []
        #self.currentEntryIdx    = 0
        self.basicDataLoaded    = False
        self.extendedDataLoaded = False
        self.stopDataLoadThread = True
        self.currentPageIdx     = 1     # number the current webpage for a collection (1 by default)
        self.nextPage           = False # Flag indicating if a next page is available


    def iterator( self ):
        """
        Returns an iterator over the elements in this collection - used to iterate thru all the elements of the Collection
        """
        return CollectionIterator(self)

    def isEmpty( self ):
        """
        Returns true if this collection contains no elements
        """
        return ( len( self.entryList ) <= 0)

    def size( self ):
        """
        Returns the number of elements in this collection
        """
        return ( len ( self.entryList ) )

    def getName( self ):
        """
        Returns the name of the collection
        """
        return self.name


#    def hasMoreElements( self ):
#        """
#        Tests if there are more element available in the Collection. If this method returns true, then a subsequent call to nextElement with no argument will successfully return a Element.
#        """
#        print "len( self.entryList ) : %d"%len( self.entryList )
#        print "self.currentEntryIdx: %d"%self.currentEntryIdx
#        if ( ( len( self.entryList ) > 0 ) and ( len( self.entryList ) > self.currentEntryIdx ) ):
#            return True
#        else:
#            # TODO: this could be an issue in multithreads situation
#            self.reset()
#            return False
#
#    def nextElement( self ):
#        """
#        Returns the next Element available in the Collection with only basic info: Video Title, Date, Summary, Note, Hits, Image URL
#        """
#        result = None
#        if ( len( self.entryList ) > self.currentEntryIdx ):
#            result = self.entryList[self.currentEntryIdx]
#            self.currentEntryIdx = self.currentEntryIdx + 1
#        return result

    def getElement( self, index ):
        """
        Returns an Element available in the Collection with full infos
        """
        result = None
        if ( len( self.entryList ) > index ):
            result = self.entryList[index]
        return result

    def getTitle( self, index ):
        """
        Returns the Description of an element (video)
        """
        if ( self.entryList[index].title == None ):
            # Retrieve the Description
            self.entryList[index].title = _retrieveTitle( index ) # Result could be ""
        return self.entryList[index].title

    def getDescription( self, index ):
        """
        Returns the Description of an element (video)
        """
        if ( self.entryList[index].description == None ):
            # Retrieve the Description
            self.entryList[index].description = _retrieveVideoDescription( index ) # Result could be ""
        return self.entryList[index].description


    def getVideoURL( self, index ):
        """
        Returns the URL of an element (video) playable by XBMC, None otherwise
        """
        if ( self.entryList[index].videoURL == None ):
            # Retrieve the video URL
            self.entryList[index].videoURL = _retrieveVideoURL( index ) # Result could be None
        return self.entryList[index].videoURL

    def getImage( self, index ):
        """
        Returns the local path of the image of an element (video) playable by XBMC
        """
        if ( self.entryList[index].imagePath == os.path.join( IMAGEDIR,"noImageAvailable.jpg" ) ):
            # Tryu to retrieve the picture
            imagePath =  self._retrieveImage( index )
            if ( imagePath == None ):
                self.entryList[index].imagePath = os.path.join( IMAGEDIR,"noImageAvailable.jpg" )
            else:
                self.entryList[index].imagePath = imagePath
        return self.entryList[index].imagePath

    def getCurrentPageIndex( self ):
        """
        Return the current page index
        """
        return self.currentPageIdx

    def hasNextPage( self ):
        """
        Check if another page is available
        """
        return self.nextPage

    def retrievePageCollection( self, pageIndex=1, progressBar=None ):
        """
        Loads Collection Datas (entries) from a specific page
        Note: pageIndex starts at 1 (not 0)
        This method must be implemnted in subclasses
        """
        pass

    def retrieveNextPageCollection( self, progressBar=None ):
        """
        Loads Collection Datas (entries) from the next page
        This method must be implemnted in subclasses
        """
        pass

    def _retrieveTitle( self, index ):
        pass

    def _retrieveImage( self, index ):
        """
        Download an image from the website and store it locally
        Returns local path if success, None otherwise
        This method must be implemnted in subclasses
        """
        pass

    def _retrieveVideoURL( self, index ):
        """
        Retrieves the URL of the video from the website and store it locally
        This method must be implemnted in subclasses
        """
        pass

    def _retrieveVideoDescription( self, index ):
        """
        Retrieves the Description of the video from the website and store it locally
        This method must be implemnted in subclasses
        """
        pass


class CollectionEmission(Collection):
    def __init__( self, name="", url=None ):
        Collection.__init__( self, name, url )

    def retrievePageCollection( self, progressBar=None ):
        """
        Loads Collection Datas (entries) from a specific page
        Note: pageIndex starts at 1 (not 0)
        """

        #TODO: just paste -> finish implemntation


        # Standard case (not sub collection)
        barprogression = 0
        try:
            if ( progressBar != None ):
                progressBar.update( barprogression )
        except Exception, e:
            print( "retrieveNextPageCollection - Exception calling UI callback for download" )
            print( str( e ) )
            print progressBar

        #TODO: Retrieve web page and process it
        if self.basicDataLoaded == False:
            # First time we load thos data for this categorie

            # Load XML webpage of Têtes à claques
            params={}

            myCollectionWebPage = EmissionVideoListWebPage(self.url,txdata,txheaders)
            print 'myCollectionWebPage:'
            print myCollectionWebPage

            print "# Next page URL"
            print myCollectionWebPage.getNextPageURL()

            barprogression = 50
            try:
                if ( progressBar != None ):
                    progressBar.update( barprogression )
            except Exception, e:
                print( "retrieveNextPageCollection - Exception calling UI callback for download" )
                print( str( e ) )
                print progressBar

            # Reset collection data
            #TODO: check is this line is not optionnal
            #self.selectCollecData[index].reset()

            # Extract data from myCollectionWebPage and copy the content in corresponding Collection Data Instance
            try:
                self.entryList = myCollectionWebPage.getVideoList()

                # Update dataLoaded flag
                self.basicDataLoaded = True
            except Exception, e:
                print( "retrieveNextPageCollection - standard case : Impossible to get collection data" )
                print( str( e ) )
                print  (str( sys.exc_info()[0] ) )
                traceback.print_exc()
        else:
            print "Data already loaded for the categorie: "
            #print self.name

        barprogression = 100
        try:
            if ( progressBar != None ):
                progressBar.update( barprogression )
                xbmc.sleep( 100 )
        except Exception, e:
            print( "retrieveNextPageCollection - Exception calling UI callback for download" )
            print( str( e ) )
            print  (str( sys.exc_info()[0] ) )
            traceback.print_exc()
            print progressBar

    def retrieveNextPageCollection( self, progressBar=None ):
        """
        Loads Collection Datas (entries) from the next page
        """
        pass

    def _retrieveImage( self, index ):
        """
        Download an image from the website and store it locally
        Returns local path if success, None otherwise
        """
        pass

    def _retrieveVideoURL( self, index ):
        """
        Retrieves the URL of the video from the website and store it locally
        """
        pass

    def _retrieveVideoDescription( self, index ):
        """
        Retrieves the Description of the video from the website and store it locally
        """
        pass


class CollectionTrailers(Collection):
    def __init__( self, name="", url=None ):
        Collection.__init__( self, name, url )

    def retrievePageCollection( self, progressBar=None ):
        """
        Loads Collection Datas (entries) from a specific page
        Note: pageIndex starts at 1 (not 0)
        """

        #TODO: just paste -> finish implemntation


        # Standard case (not sub collection)
        barprogression = 0
        try:
            if ( progressBar != None ):
                progressBar.update( barprogression )
        except Exception, e:
            print( "retrieveNextPageCollection - Exception calling UI callback for download" )
            print( str( e ) )
            print progressBar

        #TODO: Retrieve web page and process it
        if self.basicDataLoaded == False:
            # First time we load thos data for this categorie

            # Load XML webpage of Têtes à claques
            params={}

            myCollectionWebPage = TrailersVideoListWebPage(self.url,txdata,txheaders)
            print 'myCollectionWebPage:'
            print myCollectionWebPage

            barprogression = 50
            try:
                if ( progressBar != None ):
                    progressBar.update( barprogression )
            except Exception, e:
                print( "retrieveNextPageCollection - Exception calling UI callback for download" )
                print( str( e ) )
                print progressBar

            # Reset collection data
            #TODO: check is this line is not optionnal
            #self.selectCollecData[index].reset()

            # Extract data from myCollectionWebPage and copy the content in corresponding Collection Data Instance
            try:
                self.entryList = myCollectionWebPage.getVideoList()

                print "# Next page URL"
                print myCollectionWebPage.getNextPageURL()

                # Update dataLoaded flag
                self.basicDataLoaded = True
            except Exception, e:
                print( "retrieveNextPageCollection - standard case : Impossible to get collection data" )
                print( str( e ) )
                print  (str( sys.exc_info()[0] ) )
                traceback.print_exc()
        else:
            print "Data already loaded for the categorie: "
            #print self.name

        barprogression = 100
        try:
            if ( progressBar != None ):
                progressBar.update( barprogression )
                xbmc.sleep( 100 )
        except Exception, e:
            print( "retrieveNextPageCollection - Exception calling UI callback for download" )
            print( str( e ) )
            print  (str( sys.exc_info()[0] ) )
            traceback.print_exc()
            print progressBar

    def retrieveNextPageCollection( self, progressBar=None ):
        """
        Loads Collection Datas (entries) from the next page
        """
        pass

    def _retrieveImage( self, index ):
        """
        Download an image from the website and store it locally
        Returns local path if success, None otherwise
        """
        pass

    def _retrieveVideoURL( self, index ):
        """
        Retrieves the URL of the video from the website and store it locally
        """
        pass

    def _retrieveVideoDescription( self, index ):
        """
        Retrieves the Description of the video from the website and store it locally
        """
        pass


class CollectionGameplay(Collection):
    def __init__( self, name="", url=None ):
        Collection.__init__( self, name,url )


class CollectionRetro(Collection):
    def __init__( self, name="", url=None ):
        Collection.__init__( self, name,url )


class CollectionInternautes(Collection):
    def __init__( self, name="", url=None ):
        Collection.__init__( self, name,url )


class ContextCollection:
    """
        Allow to select a Collection to process (i.e by vote, by date ...)
        Use Design Pattern State
    """

    def __init__( self, collectionConfList, configManager ):
        """
            Initialization
        """
        self.curCollectionIdx     = 0

        #self.collectionConfigList = collectionConfList
        self.configManager        = configManager
        self.CollectionsList      = [] # List of all the collection supported

#         "name": LABEL_EMISSION,
#         "type": TYPE_EMISSION,
#         "url" : COLLEC_URL_EMISSION,
#        INDEX_EMISSION    = 0
#        INDEX_TRAILERS    = 1
#        INDEX_GAMEPLAY    = 2
#        INDEX_RETRO       = 3
#        INDEX_INTERNAUTES = 4


        # Creating a Collection instance for each type of collection supported
        for i in range( len( collectionConfList ) ):
            tempCollection = None
            if ( TYPE_EMISSION == collectionConfList[i]["type"] ):
                tempCollection = CollectionEmission( collectionConfList[i]["name"], collectionConfList[i]["url"] )
            elif ( TYPE_TRAILERS == collectionConfList[i]["type"] ):
                tempCollection = CollectionTrailers( collectionConfList[i]["name"], collectionConfList[i]["url"] )
            elif ( TYPE_GAMEPLAY == collectionConfList[i]["type"] ):
                tempCollection = CollectionGameplay( collectionConfList[i]["name"], collectionConfList[i]["url"] )
            elif ( TYPE_RETRO == collectionConfList[i]["type"] ):
                tempCollection = CollectionRetro( collectionConfList[i]["name"], collectionConfList[i]["url"] )
            elif ( TYPE_INTERNAUTES == collectionConfList[i]["type"] ):
                tempCollection = CollectionInternautes( collectionConfList[i]["name"], collectionConfList[i]["url"] )
            else:
                print "ContextCollection - init : **unsupported type**: %s"%collectionConfList[i]["type"]
                # TODO: Rise exception??
            self.CollectionsList.append( tempCollection )

        # Set default collection
        self.setCollection(INDEX_EMISSION)

    def setCollection( self, collectionIdx, progressBar=None ):
        """
        Sets the current selected collection and retrieve data if not alaready available
        """
        self.CollectionsList[collectionIdx].retrievePageCollection(progressBar)
        self.curCollectionIdx = collectionIdx

    def getCollection( self ):
        """
        Returns the current selected collection (Collection object)
        """
        return self.CollectionsList[self.curCollectionIdx]

    def getSelectedMenu( self ):
        return self.curCollectionIdx





#    def updateSubCollectionData( self, listIdx, progressBar=None ):
#        self.curCollectionIdx = 4 # collection index for a sub collection
#        self.subcollecIdx = listIdx
#
#        print "updateSubCollectionData; Subserie case"
#
#        barprogression = 0
#        try:
#            if ( progressBar != None ):
#                progressBar.update( barprogression )
#        except Exception, e:
#            print( "updateSubCollectionData - Exception calling UI callback for download" )
#            print( str( e ) )
#            print progressBar
#
#        # Load XML webpage of Têtes à claques
#        params={}
#
#
#        barprogression = 50
#        try:
#            if ( progressBar != None ):
#                progressBar.update( barprogression )
#        except Exception, e:
#            print( "getSubCollectionData - Exception calling UI callback for download" )
#            print( str( e ) )
#            print progressBar
#
#        #TODO: check if this line is not optionnal
#        self.selectCollecData[self.curCollectionIdx].reset()
#
#        # Extract data from myCollectionWebPage and copy the content in corresponding Collection Data Instance
#        try:
#            serieIdx = self.selectCollecData[1].idList[listIdx]
#            myCollectionWebPage.GetSerieVideoList( serieIdx, self.selectCollecData[self.curCollectionIdx] )
#        except Exception, e:
#            print( "getSubCollectionData - Subserie case : Impossible to get collection data for all the serie" )
#            print( str( e ) )
#
#        barprogression = 100
#        try:
#            if ( progressBar != None ):
#                progressBar.update( barprogression )
#                xbmc.sleep(100)
#        except Exception, e:
#            print( "getSubCollectionData - Exception calling UI callback for download" )
#            print( str( e ) )
#            print progressBar

#    def updateCollectionData( self, index, progressBar=None ):
#        """
#            Retourne the collection data correpsonding to index and set it as current index
#        """
#        # Set current selected menu
#        self.curCollectionIdx = index
#
#        # Standard case (not sub collection)
#        barprogression = 0
#        try:
#            if ( progressBar != None ):
#                progressBar.update( barprogression )
#        except Exception, e:
#            print( "getCollectionData - Exception calling UI callback for download" )
#            print( str( e ) )
#            print progressBar
#
#
#
#        if self.selectCollecData[index].dataLoaded == False:
#            # First time we load thos data for this categorie
#
#            # Load XML webpage of Têtes à claques
#            params={}
#
#            #myCollectionWebPage=EmissionVideoListWebPage( self.selectionURLList[index], params, selection=self.selectionCollecTypeList[index], langue=self.language, savehtml=True, filename= self.language + '_' + self.selectionWebPageFileList[index] )
#            myCollectionWebPage=EmissionVideoListWebPage(self.selectionURLList[index],txdata,txheaders)
#            print 'myCollectionWebPage:'
#            print myCollectionWebPage
#
#            barprogression = 50
#            try:
#                if ( progressBar != None ):
#                    progressBar.update( barprogression )
#            except Exception, e:
#                print( "getCollectionData - Exception calling UI callback for download" )
#                print( str( e ) )
#                print progressBar
#
#            # Reset collection data
#            #TODO: check is this line is not optionnal
#            self.selectCollecData[index].reset()
#
#            # Extract data from myCollectionWebPage and copy the content in corresponding Collection Data Instance
#            try:
#                myCollectionWebPage.GetVideoList( self.selectCollecData[index] )
#
#                # Update dataLoaded flag
#                self.selectCollecData[index].dataLoaded = True
#            except Exception, e:
#                print( "updateCollectionData - standard case : Impossible to get collection data" )
#                print( str( e ) )
#        else:
#            print "Data already loaded for this categorie: %d"%index
#
#        barprogression = 100
#        try:
#            if ( progressBar != None ):
#                progressBar.update( barprogression )
#                xbmc.sleep( 100 )
#        except Exception, e:
#            print( "getCollectionData - Exception calling UI callback for download" )
#            print( str( e ) )
#            print progressBar

    def playItem( self, listIdx ):
        """
            Do action on an item selected in a list
            - could be play
            - could be sublist
        """
        result = True
        # Display Loading Window while we are loading the information from the website
        dialogVideo = xbmcgui.DialogProgress()
        dialogVideo.create("Gamekult Video", "Chargement des informations sur la vidéo", "Veuillez patienter...")
        try:

            # Load video webpage corresponding to the selected video (chosenIndex)
            myVideoWebPage = VideoWebPage(self.CollectionsList[self.curCollectionIdx].getVideoURL(listIdx),txdata,txheaders)


            # Update Progress bar (half of the job is done)
            dialogVideo.update(50)

            # Get corresponding XML file
            myVideoXMLPage = VideoXML(myVideoWebPage.getVideoXMLURL(),txdata,txheaders)

            dialogVideo.update(80)

            # Get the URl of the video to play
            video2playURL= myVideoXMLPage.GetVideoURL()

            dialogVideo.update(100)

            videoListItem = xbmcgui.ListItem( label=self.CollectionsList[self.curCollectionIdx].getTitle(listIdx), thumbnailImage=self.CollectionsList[self.curCollectionIdx].getImage(listIdx))

            dialogVideo.close()

            # Play the selected video
            xbmc.Player( self.configManager.getDefaultPlayer() ).play( video2playURL, videoListItem )
        except Exception, e:
            print("Exception")
            print(e)
            dialogVideo.update(100)
            dialogVideo.close()
            dialogError = xbmcgui.Dialog()
            dialogError.ok("Erreur", "Impossible de charger les informations du à", "- un probleme de connection", "- un changement sur le site distant")


        return result



class MainWindow( xbmcgui.WindowXML ):
    def __init__( self, *args, **kwargs ):
        """
            The Idea for this function is to be used to put the inital data
        """
        #if Emulating: xbmcgui.Window.__init__(self)
        #if not Emulating:
        #    self.setCoordinateResolution(PAL_4x3) # Set coordinate resolution to PAL 4:3
        print "TacMainWindow __init__"
        #self.startupWin = kwargs[ "startupwin" ]

        # Check conf file
        self.configManager = configCtrl()

        # Create a file manager and check directory
        self.fileMgr = fileMgr( dirCheckList )
        print "TacMainWindow __init__ DONE"

        # Lock the UI
        xbmcgui.lock()

        # Create ContextCollection instance in order to display choice of video collection
        self.CollectionCtrl = ContextCollection( collectionsConfigList, self.configManager )

    def onInit( self ):
        print "onInit(): Window Initalized"
        #xbmcgui.lock()
        # Unlock the UI
        xbmcgui.unlock()
        try:
            currentViewProperty = self.getViewProperty( self.CollectionCtrl.getSelectedMenu())
            print "currentViewProperty"
            print currentViewProperty
            print self.getProperty(currentViewProperty)
            if ( self.getProperty(currentViewProperty) == "" ):
                #TODO: check why the getProperty always return nothing, something is wrong ...
                # For an unknow reason the property in WindowXML is not identical to what we have stored, reset and repaint diplay
                print "For an unknow reason the property in WindowXML is not identical to what we have stored, reset and repaint diplay"
                self._reset_views()
                self.setProperty( "display-item-number", "" ) # Used for hidding item number during the update
                self.setProperty( currentViewProperty, "activated" )
                print "result after setting property :%s"%currentViewProperty
                print self.getProperty(currentViewProperty)


            # Update Labels
            self._set_menu_labels()
            self._set_settings_tab_labels( update="startup" )
            self._set_controls_visible()

            if ( int( self.configManager.getViewMode() ) == VIEWMODE_ICONS ):
                self.setProperty( "view-List", "" )
                self.setProperty( "view-Icons", "activated" )
            else:
                self.setProperty( "view-Icons", "" )
                self.setProperty( "view-List", "activated" )


            # Update the list of video
            self.updateDataOnMenu( self.CollectionCtrl.getSelectedMenu() )
            self.updateControlListFromData()

            self.setProperty( "display-item-number", "activated" )
            # No UI is displayed, continue to get and display the picture (would be too long to wait if we were waiting doModla call)
            self.updateIcons()
        except:
            #EXC_INFO( LOG_ERROR, sys.exc_info(), self )
            print "Error while setting controls with windowXML"
            print  (str( sys.exc_info()[0] ) )
            traceback.print_exc()


        # Close the Loading Window
        #self.dialogUI.close()


    def getViewProperty(self, menuIndex):
        """
        Returns the view property as a string corresponding to the menu Index
        """
        result = "view-Emission"
        if ( INDEX_TRAILERS == menuIndex ):
            result = "view-Trailers"
        elif ( INDEX_GAMEPLAY == menuIndex ):
            result = "view-Gameplay"
        elif ( INDEX_RETRO == menuIndex ):
            result = "view-Retro"
        elif ( INDEX_INTERNAUTES == menuIndex ):
            result = "view-Internautes"
        return result

    def onFocus( self, controlId ):
        """
            Needed to be declared since it needed by XML
        """
        #xbmc.sleep( 5 )
        #self.controlID = controlID
        #print "onFocus"
        #print controlId
        pass

    def onAction( self, action ):
        """"
            onAction in WindowXML works same as on a Window or WindowDialog its for keypress/controller buttons etc
            Handle user input events.
        """
        buttonCode  =  action.getButtonCode()
        actionID    =  action.getId()
        print "onAction(): actionID=%i buttonCode=%i"%( actionID, buttonCode )

        # -- Temporary patch in order to fix focus lost when progress bar is not displayed in About TAB
        ctrlFocusID = 0
        try:
            ctrlFocusID = self.getFocusId()
            #print "Control Focus ID:"
            #print ctrlFocusID
        except:
            #EXC_INFO( LOG_ERROR, sys.exc_info(), self )
            #print "onAction: Error calling getFocusId"
            #print (str(sys.exc_info()[0]))
            #traceback.print_exc()
            pass
        if int( ctrlFocusID ) == 0:
            #TODO: Figure out why we lose focus and Fix it
            self.setFocus( self.getControl( 9000 ) )
        # -- End of patch

        if  action == ACTION_MOUSE_CLICK:
            print "ACTION_MOUSE_CLICK"
            #TODO: temporary patch, we test if the follwing code work in case of mouse click, and if yes, create a function for it
            chosenIndex = self.getCurrentListPosition()

            # Play the video or load sub-serie list depending on the type of list we are
            self.CollectionCtrl.playItem( chosenIndex ) # this function will play the video if the list item was a video

        if action == ACTION_PREVIOUS_MENU:
            # Stop update icons thread if it is running
            self._stopUpdateIcons()
            if self.configManager.getCleanCache() == True:
                print "Deleting cache"
                self.fileMgr.delFiles( CACHEDIR )
            self.close()

    def onClick( self, controlID ):
        """
            onClick(self, controlID) is the replacement for onControl. It gives an interger.
            Handle widget events
        """
        #print "onclick(): control %i" % controlID

        if ( 50 <= controlID <= 59 ):
            chosenIndex = self.getCurrentListPosition()

            # Play the video or load sub-serie list depending on the type of list we are
            currentViewProperty = self.getViewProperty( self.CollectionCtrl.getSelectedMenu())
            self.CollectionCtrl.playItem( chosenIndex ) # this function will play the video if the list item was a video
            currentViewProperty = self.getViewProperty( self.CollectionCtrl.getSelectedMenu())

        elif controlID == 150:
            # Collection
            self._reset_views()
            self.setProperty( "display-item-number", "" ) # Used for hidding item number during the update
            self.setProperty( "view-Emission", "activated" )

            self.updateDataOnMenu( INDEX_EMISSION )
            self.updateControlListFromData()
            self.getControl( 100 ).setLabel( "[B]%s[/B]"%self.CollectionCtrl.getCollection().getName() )
            self.setProperty( "display-item-number", "activated" )
            self.updateIcons()

        elif controlID == 160:
            # Collection
            self._reset_views()
            self.setProperty( "display-item-number", "" ) # Used for hidding item number during the update
            self.setProperty( "view-Trailers", "activated" )

            self.updateDataOnMenu( INDEX_TRAILERS )
            self.updateControlListFromData()
            self.getControl( 100 ).setLabel( "[B]%s[/B]"%self.CollectionCtrl.getCollection().getName() )
            self.setProperty( "display-item-number", "activated" )
            self.updateIcons()

        elif controlID == 170:
            # Collection
            self._reset_views()
            self.setProperty( "display-item-number", "" ) # Used for hidding item number during the update
            self.setProperty( "view-Gameplay", "activated" )

            self.updateDataOnMenu( INDEX_GAMEPLAY )
            self.updateControlListFromData()
            self.getControl( 100 ).setLabel( "[B]%s[/B]"%self.CollectionCtrl.getCollection().getName() )
            self.setProperty( "display-item-number", "activated" )
            self.updateIcons()

        elif controlID == 180:
            # Collection
            self._reset_views()
            self.setProperty( "display-item-number", "" ) # Used for hidding item number during the update
            self.setProperty( "view-Retro", "activated" )

            self.updateDataOnMenu( INDEX_RETRO )
            self.updateControlListFromData()
            self.getControl( 100 ).setLabel( "[B]%s[/B]"%self.CollectionCtrl.getCollection().getName() )
            self.setProperty( "display-item-number", "activated" )
            self.updateIcons()

        elif controlID == 190:
            # Settings
            self._reset_views()
            self.setProperty( "view-Settings", "activated" )
            #self.setProperty( "view-color", "0xFF000000" )
            #self._set_settings_tab_labels()

        elif controlID == 200:
            # About
            self._reset_views()
            self.setProperty( "view-About", "activated" )

        elif controlID == 211:
            # Settings decrease language button
            print "down"
            self._set_player_setting_label( update = "down" )

        elif controlID == 212:
            # Settings increase language button
            print "up"
            self._set_player_setting_label( update = "up" )

        elif controlID == 231:
            # Settings increase language button
            print "up"
            self._set_viewmode_setting_label( update = "down" )

        elif controlID == 232:
            # Settings increase language button
            print "up"
            self._set_viewmode_setting_label( update = "up" )


        elif controlID == 300:
            # Settings cleancache
            self._set_cleancache_setting_label( update = "onclick" )

        elif controlID == 400:
            # Save settings
            self._save_settings()

        elif controlID == 410:
            # Default settings
            self._set_default_settings()

    def onFocus( self, controlID ):
        #cette fonction n'est pas utiliser ici, mais dans les XML si besoin
        pass

    def updateDataOnMenu( self, menuSelectIndex ):
        """
            Update gkvData objet for a specific index in the menu
        """
        # Display Loading Window while we are loading the information from the website
        dialogLoading = xbmcgui.DialogProgress()
        dialogLoading.create( __language__( 0 ), __language__( 32102 ),__language__( 32110 ) ) # "Têtes à claques", "Chargement des informations", "Veuillez patienter..."
        try:
            #self.CollectionSelector.updateCollectionData( menuSelectIndex, progressBar=dialogLoading )
            print "setCollection: %d"%menuSelectIndex
            self.CollectionCtrl.setCollection( menuSelectIndex, progressBar=dialogLoading )

            # Close the Loading Window
            xbmc.sleep( 100 )
            dialogLoading.close()
        except Exception, e:
            print("Exception during list update")
            print( str( e ) )
            print ( str( sys.exc_info()[0] ) )
            traceback.print_exc()

            # Close the Loading Window
            dialogLoading.close()

            dialogError = xbmcgui.Dialog()
            dialogError.ok( __language__( 32111 ), __language__( 32113 ), __language__( 32114 ), __language__( 32115 ) ) # "Erreur", "Impossible de charger la page Têtes à claques.tv", "probleme de connection?", "un changement sur le site distant?"


    def updateControlListFromData( self ):
        """
            Update ControlList objet
        """
        # Create loading windows after updateData
        dialogimg = xbmcgui.DialogProgress()
        dialogimg.create( __language__( 0 ), __language__( 32104 ), __language__( 32110 ) ) # "Têtes à claques", "Mise a jour des informations", "Veuillez patienter..."
        dialogimg.update( 0 )

        print "updateControlListFromData"

        menuSelectIndex  = self.CollectionCtrl.getSelectedMenu()
        #numberOfPictures = self.CollectionSelector.selectCollecData[menuSelectIndex].getNumberofItem()
        videoLabel       = __language__( 32305 ) # " Vidéos"

        #print "List of videos:"
        #print self.CollectionSelector.selectCollecData[menuSelectIndex].titleList

        # Clear all ListItems in this control list
        self.clearList()

        # Lock the UI in order to update the list
        xbmcgui.lock()

        # get the current collection
        curCollection = self.CollectionCtrl.getCollection()
        numberOfItem  = curCollection.size()

        # add a few items to the list
#        for name in self.CollectionSelector.selectCollecData[menuSelectIndex].titleList:
#            index      = self.CollectionSelector.selectCollecData[menuSelectIndex].titleList.index( name )
#            image2load = os.path.join( CACHEDIR, os.path.basename( self.CollectionSelector.selectCollecData[menuSelectIndex].imageFilenameList[index] ) )
#            #print "updateControlListFromData - image2load = %s"%image2load
#            if not os.path.exists( image2load ) or os.path.isdir( image2load ):
#                # images not here use default
#                image2load = "gkv_noImageAvailable_wide.jpg"
#                self.addItem( xbmcgui.ListItem( label=name ) )
#            else:
#                self.addItem( xbmcgui.ListItem( label=name, thumbnailImage=image2load ) )
        index = 0
        iter = curCollection.iterator()
        while iter.hasMoreElements():
            element = iter.nextElement()
            self.addItem( xbmcgui.ListItem( label=element.title, label2=element.summary ) )

            # Compute % of Image proceeded
            percent = int( ( ( index + 1 ) * 100 ) / numberOfItem )
            dialogimg.update( percent, __language__( 32104 ),__language__( 32110 ) ) # There is an issue during Display View: Icons appear, so in order to prevent it we force dsiplay of '32104' instead
            index = index + 1
            try:
                print element
            except Exception, e:
                print( "Exception" )
                print(e)
                print ( str( sys.exc_info()[0] ) )
                traceback.print_exc()

        print "updateControlListFromData END"


        # Unlock the UI and close the popup
        xbmcgui.unlock()
        dialogimg.update( 100, __language__( 32104 ),__language__( 32110 ) )
        xbmc.sleep( 100 )
        dialogimg.close()

    def updateIcons( self ):
        try:
            self.updateIcon_thread.cancel()
        except:
            pass
        self.updateIcon_thread = Thread( target=self._updateIcons )
        self.updateIcon_thread.start()

    def _updateIcons( self ):
        """
            Retrieve images and update list
        """
        print '_updateIcons'
        # Now get the images:
        menuSelectIndex = self.CollectionCtrl.getSelectedMenu()
        print "menuSelectIndex"
        print menuSelectIndex
        try:
            # get the current collection
            curCollection = self.CollectionCtrl.getCollection()
            print curCollection
            numberOfItem  = curCollection.size()
            print "numberOfItem %d"%numberOfItem
            index = 0
            iter = curCollection.iterator()
            while iter.hasMoreElements():
                element        = iter.nextElement()
                image2download = element.imageURL
                image2save     = os.path.join( CACHEDIR,os.path.basename( image2download ) )

                # Downloading image
                try:
                    print "Downloading:"
                    print image2download
                    downloadJPG( image2download, image2save )
                except:
                    print( "Exception on image downloading: " + image2download )

                # Display the picture
                print "image2save = %s"%image2save
                print "image2download = %s"%image2download
                if os.path.exists( image2save ) and not image2download.endswith( '/' ):
                    #print "set image %s"%image2save
                    self.getListItem( index ).setThumbnailImage( image2save )

                    #TODO : use a method
                    element.imagePath = image2save
                else:
                    print "%s does NOT exist"%image2save
                index = index + 1
        except Exception, e:
            print( "Exception" )
            print(e)
            print ( str( sys.exc_info()[0] ) )
            traceback.print_exc()

    def _stopUpdateIcons( self ):
        try:
            self.updateIcon_thread.cancel()
        except:
            pass

    def _reset_views( self ):
        print "** Calling _reset_views"
        self.setProperty( "view-Emission", "" )
        self.setProperty( "view-Trailers", "" )
        self.setProperty( "view-Gameplay", "" )
        self.setProperty( "view-Retro", "" )
        self.setProperty( "view-Settings", "" )
        self.setProperty( "view-About", "" )


    def _set_menu_labels( self ):
        try:
            # Logo
            #logoImage = os.path.join( IMAGEDIR,__language__( 32900 ) )

            # Menu labels
            #optionLabel             = __language__( 32303 ) # "Options"
            buttonlanguageLabel     = __language__( 32301 ) # "English"
            aboutLabel              = __language__( 32304 ) # "A propos"
            currentLanguageLabel    = __language__( 32300 ) # "Francais"
            menuInfoLabel           = __language__( 32302 ) # "SELECTIONNEZ:"
#            collectionLabel         = __language__( self.CollectionSelector.selectionNameList[0] ) # Collection
#            seriesLabel             = __language__( self.CollectionSelector.selectionNameList[1] ) # Séries
#            extrasLabel             = __language__( self.CollectionSelector.selectionNameList[2] ) # Extras
#            adsLabel                = __language__( self.CollectionSelector.selectionNameList[3] ) # Pubs
            videoNbLabel            = __language__( 32305 ) # Video(s)
            serieNbLabel            = __language__( 32307 ) # Serie(s)
            scriptTitleAboutLabel   = "%s"%( __language__( 0 ) )
            versionAboutLabel       = "[B]%s[/B]%s"%( __language__( 32800 ), __version__ )
            authorAboutLabel        = "[B]%s[/B]%s"%( __language__( 32801 ), __author__ )
            descriptTitleAboutLabel = "[B]%s[/B]"%( __language__( 32802 ) )
            descriptContAboutLabel  = "%s"%( __language__( 32803 ) )
            copyRightsAboutLabel    = "%s"%( __language__( 32804 ) )

            # Set the labels
            #self.getControl( 30 ).setImage( logoImage )
            #self.getControl( 100 ).setLabel( "[B]%s[/B]"%__language__( self.CollectionSelector.selectionNameList[self.CollectionSelector.getSelectedMenu()] ) + "[COLOR=0xFFFFFFFF] - %s[/COLOR]"%currentLanguageLabel )
            self.getControl( 100 ).setLabel( "[B]%s[/B]"%self.CollectionCtrl.getCollection().getName() )
            self.setProperty( "video-number-label", videoNbLabel )
            self.setProperty( "serie-number-label", serieNbLabel )

#            self.getControl( 140 ).setLabel( buttonlanguageLabel )
#            self.getControl( 150 ).setLabel( collectionLabel )
#            self.getControl( 160 ).setLabel( seriesLabel )
#            self.getControl( 170 ).setLabel( extrasLabel )
#            self.getControl( 180 ).setLabel( adsLabel )
#            #self.getControl( 190 ).setLabel( optionLabel )
#            self.getControl( 200 ).setLabel( aboutLabel )
            self.getControl( 200 ).setLabel( aboutLabel )

            # About
            self.setProperty( "script-title-about-label", scriptTitleAboutLabel )
            self.setProperty( "version-about-label", versionAboutLabel )
            self.setProperty( "author-about-label", authorAboutLabel )
            self.setProperty( "descrip-title-about-label", descriptTitleAboutLabel )
            self.setProperty( "descrip-content-about-label", descriptContAboutLabel )
            self.setProperty( "copyrights-about-label", copyRightsAboutLabel )
        except:
            print "Error _set_menu_labels"
            print ( str( sys.exc_info()[0] ) )
            traceback.print_exc()

    def _set_player_setting_label( self, update="startup" ):
        defaultPlayerTitleLabel = __language__( 32500 ) # Player vidéo:
        playerMenuList          = [__language__( 32501 ), __language__( 32502 ),__language__( 32503 )] # "Auto","DVD Player","MPlayer"

        if update == "default":
            self.defaultPlayerIdxDisplay = 0 # Default value
            defaultPlayerContentLabel    = playerMenuList[self.defaultPlayerIdxDisplay]
            self.defaultPlayerUpdated    = True # flag indicating on exit if they have been modified
            self.activateSaveSettings()
        elif  update == "refresh":
            defaultPlayerContentLabel    = playerMenuList[self.defaultPlayerIdxDisplay]
        elif update == "startup":
            self.defaultPlayerIdxDisplay = self.configManager.getDefaultPlayer()
            defaultPlayerContentLabel    = playerMenuList[self.defaultPlayerIdxDisplay]
            self.defaultPlayerUpdated    = False # flag indicating on exit if they have been modified
        elif  update == "up":
            if self.defaultPlayerIdxDisplay < ( len( playerMenuList ) - 1 ):
                self.defaultPlayerIdxDisplay = self.defaultPlayerIdxDisplay + 1
            else:
                # Max reached
                self.defaultPlayerIdxDisplay = 0
            defaultPlayerContentLabel = playerMenuList[self.defaultPlayerIdxDisplay]
            self.defaultPlayerUpdated = True # flag indicating on exit if they have been modified
            self.activateSaveSettings()
        elif update == "down":
            if self.defaultPlayerIdxDisplay > 0:
                self.defaultPlayerIdxDisplay = self.defaultPlayerIdxDisplay - 1
            else:
                # Min reached
                self.defaultPlayerIdxDisplay = (len(playerMenuList)-1)
            defaultPlayerContentLabel = playerMenuList[self.defaultPlayerIdxDisplay]
            self.defaultPlayerUpdated = True # flag indicating on exit if they have been modified
            self.activateSaveSettings()
        # Update label
        self.getControl( 213 ).setLabel( defaultPlayerTitleLabel, label2=defaultPlayerContentLabel )

    def _set_viewmode_setting_label( self, update="startup" ):
        viewModeTitleLabel = __language__( 32504 ) # View Mode
        playerMenuList          = [__language__( 32505 ), __language__( 32506 )] # Panel, List

        if update == "default":
            self.viewModeIdxDisplay = 0 # Default value
            viewModeContentLabel    = playerMenuList[self.viewModeIdxDisplay]
            self.viewModeUpdated    = True # flag indicating on exit if they have been modified
            self.activateSaveSettings()
        elif  update == "refresh":
            viewModeContentLabel    = playerMenuList[self.viewModeIdxDisplay]
        elif update == "startup":
            self.viewModeIdxDisplay = self.configManager.getViewMode()
            viewModeContentLabel    = playerMenuList[self.viewModeIdxDisplay]
            self.viewModeUpdated    = False # flag indicating on exit if they have been modified
        elif  update == "up":
            if self.viewModeIdxDisplay < ( len( playerMenuList ) - 1 ):
                self.viewModeIdxDisplay = self.viewModeIdxDisplay + 1
            else:
                # Max reached
                self.viewModeIdxDisplay = 0
            viewModeContentLabel = playerMenuList[self.viewModeIdxDisplay]
            self.viewModeUpdated = True # flag indicating on exit if they have been modified
            self.activateSaveSettings()
        elif update == "down":
            if self.viewModeIdxDisplay > 0:
                self.viewModeIdxDisplay = self.viewModeIdxDisplay - 1
            else:
                # Min reached
                self.viewModeIdxDisplay = (len(playerMenuList)-1)
            viewModeContentLabel = playerMenuList[self.viewModeIdxDisplay]
            self.viewModeUpdated = True # flag indicating on exit if they have been modified
            self.activateSaveSettings()
        # Update label
        self.getControl( 233 ).setLabel( viewModeTitleLabel, label2=viewModeContentLabel )

    def _set_cleancache_setting_label( self,update="startup" ):
        cleanCacheTitleLabel        = __language__( 32507 ) # "Nettoyage auto du cache: "

        if update == "default":
            self.cleanCacheDisplay = True
            self.cleanCacheUpdated = True # flag indicating on exit if they have been modified
            self.activateSaveSettings()
        elif update == "startup":
            self.cleanCacheDisplay = self.configManager.getCleanCache()
            self.cleanCacheUpdated = False # flag indicating on exit if they have been modified
        elif  update == "refresh":
            self.cleanCacheDisplay = self.configManager.getCleanCache()
        elif update == "onclick":
            if self.cleanCacheDisplay:
                self.cleanCacheDisplay = False
            else:
                self.cleanCacheDisplay = True
            self.cleanCacheUpdated = True # flag indicating on exit if they have been modified
            self.activateSaveSettings()
        # Update label (niclude refresh case)
        self.getControl( 300 ).setLabel( cleanCacheTitleLabel )
        if self.cleanCacheDisplay:
            self.getControl( 300 ).setSelected( True )
        else:
            self.getControl( 300 ).setSelected( False )

    def _set_default_settings( self ):
        """
            Set default value foir settings
            A save is necessary in order to validate it in the conf file
        """
        try:
            # - Player
            self._set_player_setting_label( update="default" )

            # - Cache cleaning
            self._set_cleancache_setting_label( update="default" )

            # - View Mode
            self._set_viewmode_setting_label( update="default" )

        except:
            #EXC_INFO( LOG_ERROR, sys.exc_info(), self )
            print "Error _set_default_settings"
            print ( str( sys.exc_info()[0] ) )
            traceback.print_exc()

    def _set_settings_tab_labels( self, update="startup" ):
        """
            Set the labels of Settings tab
        """
        try:
            # Current language
            #self._set_current_language_setting_label( update )

            # - Player
            self._set_player_setting_label( update )

            # - Cache cleaning
            self._set_cleancache_setting_label( update )

            # - View Mode
            self._set_viewmode_setting_label( update )
            # Buttons
            self.getControl( 400 ).setLabel( __language__( 32602 ) )
            self.getControl( 410 ).setLabel( __language__( 32604 ) )

            if update =="startup":
                self.deactivateSaveSettings()
        except:
            #EXC_INFO( LOG_ERROR, sys.exc_info(), self )
            print "Error _set_settings_tab_labels"
            print ( str( sys.exc_info()[0] ) )
            traceback.print_exc()

    def _set_controls_visible( self ):
        """
            Thanks to Frostbox
            ici sa sert a rendre visible les controls qu'on veut voir
            pour le moment il y a 1 parametre, donc les autres sont mis non visible
            pour le futur on pourra les activer au besoin et coder sa fonction
            penser a retirer les # de bouton_non_visible = [ 170, 180, 190, 200, 210, 220, 230, 240 ] par ordre de grandeur, suivant == 170
        """
        xbmcgui.lock()
        try:
            bouton_non_visible = [ 100, 115, 140 ]
            for control_id in bouton_non_visible:
                self.getControl( control_id ).setEnabled( False )
                self.getControl( control_id ).setVisible( False )

        except:
            print "Error _set_controls_visible"
            print ( str( sys.exc_info()[0] ) )
            traceback.print_exc()
        xbmcgui.unlock()

    def activateSaveSettings( self ):
        self.getControl( 400 ).setEnabled( True )

    def deactivateSaveSettings( self ):
        self.getControl( 400 ).setEnabled( False )

    def _save_settings( self ):
        """
            Saving modification in the configuration file
        """

        # Check change flag on each property
        save = False

        if self.defaultPlayerUpdated:
            self.configManager.setDefaultPlayer( self.defaultPlayerIdxDisplay, False )
            save = True
        if self.cleanCacheUpdated:
            self.configManager.setCleanCache( self.cleanCacheDisplay, False )
            save = True
        if self.viewModeUpdated:
            self.configManager.setViewMode( self.viewModeIdxDisplay, False )
            if ( self.viewModeIdxDisplay == VIEWMODE_ICONS ):
                self.setProperty( "view-List", "" )
                self.setProperty( "view-Icons", "activated" )
            else:
                self.setProperty( "view-Icons", "" )
                self.setProperty( "view-List", "activated" )
            save = True

        if save == True:
            # Save conf file
            dialogsave = xbmcgui.DialogProgress()
            dialogsave.create( __language__( 0 ), __language__( 32701 ),__language__( 32110 ) )
            dialogsave.update(0)
            if self.configManager.saveConfFile():
                dialogsave.update( 100 )
                xbmc.sleep( 100 )
                dialogsave.close()

                # Reset update flags
                self.defaultPlayerUpdated   = False
                self.cleanCacheUpdated      = False
                self.viewModeUpdated        = False

                # Disable save button
                self.deactivateSaveSettings()

                dialogInfo = xbmcgui.Dialog()
                result = dialogInfo.ok( __language__( 0 ), __language__( 32703 ) )
            else:
                dialogsave.update( 100 )
                xbmc.sleep( 200 )
                dialogsave.close()

                dialogInfo = xbmcgui.Dialog()
                result = dialogInfo.ok( __language__( 0 ), __language__( 32702 ) )


def getUserSkin():
    """
        This function return the current skin used
        Thanks to Frostbox
    """
    current_skin = xbmc.getSkinDir()
    print "Skin currently used by XBMC = %s"%current_skin
    force_fallback = os.path.exists( os.path.join( ROOTDIR, "resources", "skins", current_skin ) )
    print "force_fallback = %s"%force_fallback
    if not force_fallback:
        current_skin = "Default"
    print "Skin used by the script = %s"%current_skin
    return current_skin, force_fallback




def show_main_window( startupwin=None ):
    """
        Create Main Window UI
    """
    file_xml = "gkv-MainWindow.xml"
    #file_xml = "Script_WindowXMLExample.xml"
    #depuis la revision 14811 on a plus besoin de mettre le chemin complet, la racine suffit
    dir_path = ROOTDIR
    #recupere le nom du skin et si force_fallback est vrai, il va chercher les images du defaultSkin.
    current_skin, force_fallback = getUserSkin()

    print "Creating gkvMainWindow"
    w = MainWindow( file_xml, dir_path, current_skin, force_fallback, startupwin=startupwin )
    w.doModal()
    del w


def startup():
    """

        Startup function

    """
    show_main_window()



########
#
# Main
#
########

if __name__ == "__main__":
    print( str( "=" * 85 ) )
    print( "" )
    print( "Gamekult Video XBMC script STARTS".center( 85 ) )
    print( "" )
    print( str( "=" * 85 ) )

    # Print Path information
    print( "ROOTDIR"  + ROOTDIR )
    print( "IMAGEDIR" + IMAGEDIR )
    print( "CACHEDIR" + CACHEDIR )
    print( "CONFDIR"  + CONFDIR )

    # Calling startup function
    startup()
else:
    # Library case
    pass


