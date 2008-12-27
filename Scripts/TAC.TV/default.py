# -*- coding: cp1252 -*-
"""
TAC.TV by Temhil (temhil@gmail.com)

Description:
-----------
This script allows to watch videos on www.tac.tv website which I highly recommend. 
Each week a new short video is added. Watch out! Laughing too much can cause belly pain!
If you like and enjoy TAC.tv, please support their creators by visiting their website www.tac.tv and/or buying their DVD(s)

Distribution rights and pictures are property of Salambo productions Inc (www.tac.tv)

History:
-------
26-12-08 Version 2.0 by Temhil
  - Total redesigned UI in order to use WindowXML and all the advantages of it (display using tabs like on the website)
  - Bug fix where picture wasn't displayed picture URL wasn't defined in the XML
  - Download pictures in a separate thread (in case of Mac/Linux it avoid to block the UI while picture are downloaded)
 
14-11-08 Version 1.0 by Temhil:
  - Renamed script to TAC.TV in order to support English and French user (following what already has been done on the website) 
  - GUI improvement
  - Multilanguages fully supported; on language change, the GUI is updated (text +  icons)
  - Added support ot series, it is possible now to watch only the videos of a specific serie
  - Redesign of Data retrieval: separation of view of model
  - Added support to switch Fr->En and En->Fr even within a serie
  - Created a startup window for selecting language the fisrt time script is run
  - Created 'settings' menu allowing to set-up player, automatic cache cleaning and language at startup
  - Created 'About' menu
  - Prepared the script for WindowXML use (to come)
  
21-10-08 Version Beta2 by Temhil: 
  - Adaptation of the script after a full update of the website
  - Added English/French support (language and video browsing)
  - Added Series/TV Ads categories
  - Added background picture download 
   (user doesn't have to wait anymore at startup the full retrieval of pictures)
  - Deleted sorting (vote/date) functions: not supported anymore because of changes done on the website
  
27-04-08 Version Beta1 par Temhil
  - Script creation providing the functionality to watch video on the website:
    www.tetesaclaques.tv (www.tac.tv)
  - Settings support will be provided in the future
  - Pictures are downloaded on the cache directory but are never deleted by the script (will come). 
    The good side of that is script is loading faster! ;-)
"""


############################################################################
# script constants
############################################################################
__script__ = "TAC.TV"
__plugin__ = "Unknown"
__author__ = "Temhil"
__url__ = "http://passion-xbmc.org/index.php"
__svn_url__ = "http://code.google.com/p/passion-xbmc/source/browse/#svn/trunk/Scripts/TAC.TV"
__credits__ = "Team XBMC Passion"
__platform__ = "xbmc media center"
__date__ = "26-12-2008"
__version__ = "2.0"
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

from resources.libs import language # Cutom language lib
from resources.libs.BeautifulSoup import BeautifulStoneSoup # XML parsing lib

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

# We use a modification of language lib since we want to be able to change language separately from XBMC
lang         = language.Language()
__language__ = lang.getLanguageString


#############################################################################
# URLs
#############################################################################
tacBasePageURL          = "http://www.tetesaclaques.tv/"

collecAccueilPageRelURL = "http://www.tetesaclaques.tv/modules/population.php"
collecDatesPageRelURL   = "http://www.tetesaclaques.tv/modules/population.php"
collecVotesPageRelURL   = "http://www.tetesaclaques.tv/modules/population.php"
collecExtrasPageRelURL  = "http://www.tetesaclaques.tv/modules/population.php"
collecPubPageRelURL     = "http://www.tetesaclaques.tv/modules/population.php"
collecSeriesPageRelURL  = "http://www.tetesaclaques.tv/modules/populationSeries.php"

# Selector list
tacNameSelectList        = ( 32306, 32307, 32308, 32309, 32307 ) # "COLLECTION", "SERIES", "EXTRAS", "PUBS"
tacUrlSelectList         = ( collecDatesPageRelURL, collecSeriesPageRelURL, collecExtrasPageRelURL, collecPubPageRelURL )
tacCollecTypeSelectList  = ( "collection", "serie", "extras", "pub" )
tacWebPageFileSelectList = ["populationCollection.xml","populationSeries.xml","populationExtras.xml","populationPubs.xml"]
 

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
        self.language      = ''
        self.delCache      = False
        try:
            # Create config parser
            self.config = ConfigParser.ConfigParser()
            
            # Read config from .cfg file
            # - Open config file
            self.config.read(os.path.join(CONFDIR, "TAC.cfg"))
            
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
            if ( self.config.has_option( "user", "language" ) == False ):
                self.config.set( "user", "language", self.language )
                self.is_conf_valid = False
            else:
                self.language = self.config.get( "user", "language" )
            if ( self.is_conf_valid == False ):
                # Update file
                print "CFG file format wasn't valid: correcting ..."
                #cfgfile=open(os.path.join(ROOTDIR, "resources", "TAC.cfg"), 'w+')
                cfgfile = open( os.path.join( CONFDIR, "TAC.cfg" ), 'w+' )
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
            print( "Exception while loading configuration file " + "TAC.cfg" )
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
            cfgfile = open( os.path.join( CONFDIR, "TAC.cfg" ), 'w+' )
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
        
    def setDefaultLanguage( self,language,save=True ):
        """
            set language parameter locally and in .cfg file
        """
        self.language = language
        
        # Set player parameter
        self.config.set( "user", "language", language )
        
        if save:
            # Update file
            cfgfile = open( os.path.join( CONFDIR, "TAC.cfg" ), 'w+' )
            try:
                self.config.write( cfgfile )
            except Exception, e:
                print( "Exception during setDefaultLanguage" )
                print( str( e ) )
                print ( str( sys.exc_info()[0] ) )
                traceback.print_exc()
            cfgfile.close()
        
    def getDefaultLanguage( self ):
        """
            return the language currently used
        """
        return self.language

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
            cfgfile = open( os.path.join( CONFDIR, "TAC.cfg" ), 'w+' )
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

    def saveConfFile( self ):
        # Update file
        result  = True
        cfgfile = open( os.path.join( CONFDIR, "TAC.cfg" ), 'w+' )
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
    def __init__( self, baseURL, params, selection, classification='date', langue='fr-ca', pageNb='1', geolocation='fr', savehtml=True, filename="defaut.html", check_connexion=True ):
        """
            Init of WebPage
            Load the Web page at the specific URL
            and copy the source code in self.Source        
        """
        try:
            # CookieJar objects support the iterator protocol for iterating over contained Cookie objects.
            h = urllib2.HTTPCookieProcessor( cookielib.CookieJar() )
        
            request = urllib2.Request( baseURL, urllib.urlencode( params ) )
            request.add_header( 'Host', 'www.tetesaclaques.tv' )
            request.add_header( 'User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3' )
            request.add_header( 'Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8' )
            request.add_header( 'Accept-Language', 'fr,fr-fr;en-us,en;q=0.5' )
            request.add_header( 'Accept-Encoding', 'gzip,deflate' )
            request.add_header( 'Accept-Charset', 'ISO-8859-1,utf-8;q=0.7,*;q=0.7' )
            request.add_header( 'Keep-Alive', '300' )
            request.add_header( 'Connection','keep-alive' )
            request.add_header( 'Cookie', 'GELOCATIONtac=%s; selection=%s; page=%s; classification=%s; fichier=video; LANGUEtac=%s'%( geolocation, selection, pageNb, classification, langue ) )
        
            
            cj     = cookielib.CookieJar()
            opener = urllib2.build_opener( urllib2.HTTPCookieProcessor( cj ) )
            urllib2.install_opener( opener )
            self.Source = opener.open( request ).read()
            print( "WebPage created for URL: " + baseURL )
            if savehtml == True:
                print "saving file at: %s"%( os.path.join( CACHEDIR, filename ) )
                open( os.path.join( CACHEDIR, filename ),"w" ).write( self.Source )
        except Exception, e:
            print( "Exception in WebPage init for URL: " + baseURL )
            print( e )
            print ( str( sys.exc_info()[0] ) )
            traceback.print_exc()
            
            # pass the Exception
            raise

class tacSeriesWebPage( WebPage ):
    """
    
        Inherit from WebPage super class
        Load on tete a claque webiste a collection webpage for Series
        (which include list of video to watch but also series IDs) and provides 
        source code (XML  format)    
        (which include video URL to watch) and provides source code
    
    """
    def __init__( self, baseURL, params, selection, classification='date', langue='fr-ca', pageNb='1', geolocation='fr', savehtml=True, filename="defaut.html", check_connexion=True ):
        """
            - Init of WebPage
            - Load the Web page at the specific URL and copy the source code in self.Source
        """
        # Init super Class
        WebPage.__init__( self, baseURL, params, selection, classification, langue, pageNb, geolocation, savehtml, filename, check_connexion )
            
    def GetSerieList( self, seriedataObj ):
        # Extract names of Series from the TAC webpage
        soup = BeautifulStoneSoup( self.Source )
        try:
            for serie in soup.findAll( "serie" ):
                # Copy each item found in a list
                seriedataObj.titleList.append( serie.titreserie.string.encode( "cp1252" ) )
                seriedataObj.idList.append( serie.idserie )
                imageURL = serie.imageserie.string.encode( "utf-8" )
                if not imageURL.startswith( 'http' ):
                    imageURL = tacBasePageURL + imageURL
                seriedataObj.imageFilenameList.append( imageURL )
        except Exception, e:
            print( "GetSerieList: Exception during XMl parsing" )
            print( str( e ) )
            print ( str( sys.exc_info()[0] ) )
            traceback.print_exc()
#        print "++++++++++++++++++++++++++++++++++++"
#        print "tacSeriesWebPage - videosInfo:"    
#        print(seriedataObj.titleList)
#        print(seriedataObj.idList)
#        print(seriedataObj.imageFilenameList)
#        print(seriedataObj.videoFilenameList)
#        print(seriedataObj.imageFilenameList)
#        print(seriedataObj.nbrvotesList)
        
    def GetSerieVideoList( self, idserie, dataObj, reverseList = True ):
        soup = BeautifulStoneSoup( self.Source )
        try:
            for serie in soup.findAll( "serie" ):
                # Copy each item found in a list
                if serie.idserie == idserie:
                    for miniature in serie.clipserie.findAll( "miniature" ):
                        dataObj.titleList.append( miniature.titre.string.encode( "cp1252" ) )
                        dataObj.idList.append( miniature.idproduit )
                        dataObj.videoFilenameList.append( miniature.fichiervideo.string.encode( "utf-8" ) )
                        dataObj.votesList.append( miniature.votes )
                        dataObj.nbrvotesList.append( miniature.nbrvotes )
                        imageURL = miniature.fichierminiature.string.encode( "utf-8" )
                        if not imageURL.startswith( 'http' ):
                            imageURL = tacBasePageURL + imageURL
                        dataObj.imageFilenameList.append( imageURL )
                    # We exit the loop since we foud the serie with our ID
                    break
            if (reverseList == True):
                # Reverse the list on order to be from oldest to newest video
                dataObj.titleList.reverse()
                dataObj.idList.reverse()
                dataObj.videoFilenameList.reverse()
                dataObj.votesList.reverse()
                dataObj.nbrvotesList.reverse()
                dataObj.imageFilenameList.reverse()
            
        except Exception, e:
            print( "GetSerieVideoList: Exception during XMl parsing" )
            print( str( e ) )
            print ( str( sys.exc_info()[0] ) )
            traceback.print_exc()
#        print "++++++++++++++++++++++++++++++++++++"
#        print "GetSerieVideoList - videosInfo:"    
#        print(dataObj.titleList)
#        print(dataObj.idList)
#        print(dataObj.imageFilenameList)
#        print(dataObj.videoFilenameList)
#        print(dataObj.imageFilenameList)
#        print(dataObj.nbrvotesList)


class tacCollectionWebPage( WebPage ):
    """
    
        Inherit from WebPage super class
        Load on tete a claque webiste a collection webpage
        (which include list of video to watch) and provides 
        source code (XML  format)    
        (which include video URL to watch) and provides source code
    
    """
    def __init__( self, baseURL, params, selection, classification='date', langue='fr-ca', pageNb='1', geolocation='fr', savehtml=True, filename="defaut.html", check_connexion=True ):
        """
            - Init of WebPage
            - Load the Web page at the specific URL and copy the source code in self.Source
        """
        # Init super Class
        WebPage.__init__( self, baseURL, params, selection, classification, langue, pageNb, geolocation, savehtml, filename, check_connexion )

    def GetVideoList( self, dataObj ):
        # Extract video File Name from the TAC webpage
        soup = BeautifulStoneSoup( self.Source )
        try:
            for miniature in soup.findAll( "miniature" ):
                #TODO: Check what can we do with a dixtionary instead of parallel lists
                
                # Copy each item found in a list
                dataObj.titleList.append( miniature.titre.string.encode( "cp1252" ) )
                dataObj.idList.append( miniature.idproduit )
                dataObj.videoFilenameList.append( miniature.fichiervideo.string.encode( "utf-8" ) )
                dataObj.votesList.append( miniature.votes )
                dataObj.nbrvotesList.append( miniature.nbrvotes )
                imageURL = miniature.fichierminiature.string.encode( "utf-8" )
                if not imageURL.startswith( 'http' ):
                    imageURL = tacBasePageURL + imageURL
                dataObj.imageFilenameList.append( imageURL )
        except Exception, e:
            print( "tacCollectionWebPage: Exception during XMl parsing" )
            print( str( e ) )
            print ( str( sys.exc_info()[0] ) )
            traceback.print_exc()
#        print "++++++++++++++++++++++++++++++++++++"
#        print "tacCollectionWebPage - videosInfo:"    
#        print(dataObj.titleList)
#        print(dataObj.idList)
#        print(dataObj.imageFilenameList)
#        print(dataObj.videoFilenameList)
#        print(dataObj.imageFilenameList)
#        print(dataObj.nbrvotesList)

    def GetNumberofPages( self ):
        """
            Extract and return the number of web pages
            available for one tac collection
        """
        pageNb = 1 # In case we don't find the string pageNb would be 0
        
#        print("Page Number =" + str(pageNb))
#        print("----------------------")

        return pageNb
      
        ##TODO : Deal with the case of more than 1 page number found


class tacSerieData:
    """
        Data Warehouse for datas extracted from Serie
        XML page(s)
        Not currently used for future evolutions
    """
    #TODO: use this structure for series in the future 
    def __init__( self ):
        """
        Init of tacSerieData
        """
        self.dataLoaded         = False # define if data has been extracted from a collection webpage
        self.numberOfPages      = 0     # number of webpage for a collection
        self.idSerieList        = []    # IDs of video in the collection webpage
        self.titleSerieList     = []    # Title of a video    
        self.imageSerieFileList = []    # File name for the image of a video
        self.timeSerieList      = []    # File name for a video

    def reset(self):
        """
            Reset of tacSerieData attributes
        """
        self.dataLoaded         = False
        self.numberOfPages      = 0
        self.idSerieList        = []
        self.titleSerieList     = []
        self.imageSerieFileList = []
        self.timeSerieList      = []
    
    def getNumberofItem( self ):
        """
            Return the total number of item (series) found for the collection
        """
        return len( self.idSerieList )

class tacCollectionData:
    """
         Data Warehouse for datas extracted from collection
         web page(s) (one or more depending on number of pages)    
     """
    def __init__( self ):
        """
            Init of tacCollectionData
        """
        self.dataLoaded        = False # define if data has been extracted from a collection webpage
        self.numberOfPages     = 0     # number of webpage for a collection
        self.idList            = []    # IDs of video in the collection webpage
        self.titleList         = []    # Title of a video    
        self.imageFilenameList = []    # File name for the image of a video
        self.videoFilenameList = []    # File name for a video
        self.votesList         = []    # votes
        self.nbrvotesList      = []    # nbrvotes

    def reset( self ):
        """
            Reset of tacCollectionData attributes
        """
        self.dataLoaded        = False
        self.numberOfPages     = 0
        self.idList            = []
        self.titleList         = []
        self.imageFilenameList = []
        self.videoFilenameList = []
        self.votesList         = []
        self.nbrvotesList      = []
    
    def getNumberofItem( self ):
        """
            Return the total number of item (videos) found for the collection
        """
        return len( self.titleList )


class SelectCollectionWebpage:
    """
        Allow to select a Collection Webpage to process (i.e by vote, by date ...)
    """

    def __init__( self, pagebaseUrl, nameSelecList, urlSelectList, configManager ):
        """
            Initialization
        """
        self.language                   ='fr-ca'
        self.isSerieActive              = False
        self.selectedMenu               = 0
        self.subcollecIdx               = -1
        
        self.baseUrl                    = pagebaseUrl
        self.selectionNameList          = nameSelecList
        self.selectionURLList           = urlSelectList
        self.selectionCollecTypeList    = tacCollecTypeSelectList
        self.selectionWebPageFileList   = tacWebPageFileSelectList
        self.configManager              = configManager
        self.selectCollecData           = []
        self.menulen                    = len(nameSelecList)
        
        ##TODO: check len(nameSelecList) == len(urlSelectList)
        
        # Filling selectCollecData
        for i in range(self.menulen):
            self.selectCollecData.append( tacCollectionData() )
            
        # Create additionnal one for the content of serie
        #TODO: manage paralle list for video of serie???
        self.selectCollecData.append( tacCollectionData() )

    def setCollectionLanguage( self, language ):
        """
            Set the language (proposed videos are differents in French and English)
        """
        if language == "french":
            self.language = "fr-ca"
        elif language == "english":
            self.language = "en"
        else:
            print "setCollectionLanguage : Unsupported language : %s - defined french as default language"%language
            self.language = "fr-ca"
            
        # Reset dataloaded status
        for i in range( self.menulen ):
            self.selectCollecData[i].dataLoaded = False
        print "New language = %s"%self.language

    def getCollectionLanguage(self):
        """
            get the current language (proposed videos are differents in French and English)
        """
        if self.language == "fr-ca":
            language = "french"
        elif self.language == "en":
            language = "english"
        else:
            print "getCollectionLanguage : Unsupported language : %s - None is returned"%self.language
            language = None
        return language
    
    def getSelectedMenu( self ):
        return self.selectedMenu

    def updateSubCollectionData( self, listIdx, language, progressBar=None ):
        self.selectedMenu = 4 # collection index for a sub colelction
        self.subcollecIdx = listIdx
        if language == "french":
            self.language = "fr-ca"
        elif language == "english":
            self.language = "en"
        else:
            print "updateSubCollectionData : Unsupported language : %s - defined french as default language"%language
            self.language = "fr-ca"
        
        print "updateSubCollectionData; Subserie case"
        
        barprogression = 0
        try:
            if ( progressBar != None ):
                progressBar.update( barprogression )
        except Exception, e:        
            print( "updateSubCollectionData - Exception calling UI callback for download" )
            print( str( e ) )
            print progressBar

        # Load XML webpage of Têtes à claques
        params={}
        
        #TODO: utiliser le xml deja telecharger au lieu de le retelecharger
        myCollectionWebPage = tacSeriesWebPage( self.selectionURLList[1], params, selection=self.selectionCollecTypeList[1], langue=self.language, savehtml=True, filename= self.language + '_' + self.selectionWebPageFileList[1] )

        barprogression = 50
        try:
            if ( progressBar != None ):
                progressBar.update( barprogression )
        except Exception, e:        
            print( "getSubCollectionData - Exception calling UI callback for download" )
            print( str( e ) )
            print progressBar
        
        #TODO: check if this line is not optionnal
        self.selectCollecData[self.selectedMenu].reset()
        
        # Extract data from myCollectionWebPage and copy the content in corresponding Collection Data Instance
        try:
            serieIdx = self.selectCollecData[1].idList[listIdx]
            myCollectionWebPage.GetSerieVideoList( serieIdx, self.selectCollecData[self.selectedMenu] )
        except Exception, e:        
            print( "getSubCollectionData - Subserie case : Impossible to get collection data for all the serie" )
            print( str( e ) )

        barprogression = 100
        try:
            if ( progressBar != None ):
                progressBar.update( barprogression )
                xbmc.sleep(100)
        except Exception, e:        
            print( "getSubCollectionData - Exception calling UI callback for download" )
            print( str( e ) )
            print progressBar

    def updateCollectionData( self, index, language, progressBar=None ):
        """
            Retourne the colelction data correpsonding to index and set it as current index
        """        
        # Set current selected menu
        self.selectedMenu = index
        
        if self.selectedMenu == 4:
            self.updateSubCollectionData(self.subcollecIdx,language,progressBar)
        else:
            # Standard case (not sub collection)
            if language == "french":
                self.language = "fr-ca"
            elif language == "english":
                self.language = "en"
            else:
                print "updateCollectionData : Unsupported language : %s - defined french as default language"%language
                self.language = "fr-ca"
            
            barprogression = 0
            try:
                if ( progressBar != None ):
                    progressBar.update( barprogression )
            except Exception, e:        
                print( "getCollectionData - Exception calling UI callback for download" )
                print( str( e ) )
                print progressBar
    
            if self.selectCollecData[index].dataLoaded == False:
                # First time we load thos data for this categorie
                    
                # Load XML webpage of Têtes à claques
                params={}
        
                if self.selectedMenu == 1:
                    myCollectionWebPage=tacSeriesWebPage( self.selectionURLList[index], params, selection=self.selectionCollecTypeList[index], langue=self.language, savehtml=True, filename= self.language + '_' + self.selectionWebPageFileList[index] )
                    
                else:
                    myCollectionWebPage=tacCollectionWebPage( self.selectionURLList[index], params, selection=self.selectionCollecTypeList[index], langue=self.language, savehtml=True, filename= self.language + '_' + self.selectionWebPageFileList[index] )
        
                barprogression = 50
                try:
                    if ( progressBar != None ):
                        progressBar.update( barprogression )
                except Exception, e:        
                    print( "getCollectionData - Exception calling UI callback for download" )
                    print( str( e ) )
                    print progressBar
                
                # Reset collection data 
                #TODO: check is this line is not optionnal
                self.selectCollecData[index].reset()
                
                # Extract data from myCollectionWebPage and copy the content in corresponding Collection Data Instance
                try:            
                    if self.selectedMenu == 1:
                        myCollectionWebPage.GetSerieList( self.selectCollecData[index] )
                    else:
                        myCollectionWebPage.GetVideoList( self.selectCollecData[index] )
                        
                    # Update dataLoaded flag
                    self.selectCollecData[index].dataLoaded = True
                except Exception, e:        
                    print( "updateCollectionData - standard case : Impossible to get collection data" )
                    print( str( e ) )
            else:
                print "Data already loaded for this categorie: %d"%index
            
            barprogression = 100
            try:
                if ( progressBar != None ):
                    progressBar.update( barprogression )
                    xbmc.sleep( 100 )
            except Exception, e:        
                print( "getCollectionData - Exception calling UI callback for download" )
                print( str( e ) )
                print progressBar
        
    def isSubCollec( self, listIdx ):
        """
            Do action on an item selcted in a list
            - could be play
            - could be sublist
        """
        result = False
        if self.selectedMenu == 1: # Index 1 for serie
            # We are in serie case (list of serie is displayed to user)
            # -> we have to display list of video for the serie
            
            # Reset collection data for sub colelction (index 4) in case we already had one
            self.selectCollecData[4].reset()
            
            result = True
        else:
            # Get the URl of the video to play
            video2playURL = self.selectCollecData[self.selectedMenu].videoFilenameList[listIdx]
            
            # Play the selected video
            xbmc.Player( self.configManager.getDefaultPlayer() ).play( video2playURL )
            
            #TODO: Add Subtitle support when setSubtitles will be integrated im XBMC offcicial releases
#            # Subtitle support
#            myPlayer = xbmc.Player(self.configManager.getDefaultPlayer())
#            print "setSubtitles"
#            myPlayer.setSubtitles(os.path.join(CACHEDIR, "1071.txt")) # Seems to be only for Linux
#            print "play"
#            myPlayer.play(video2playURL)
            
        return result 


class FirstStartWindow( xbmcgui.Window ):
    """
        This window is display only when startup language is not set
        it gets language to set from the user
    """
    def __init__(self):
        if Emulating: xbmcgui.Window.__init__( self )
        if not Emulating:
            self.setCoordinateResolution(PAL_4x3) # Set coordinate resolution to PAL 4:3

        self.__loc_language__ = xbmc.Language( ROOTDIR, "french" ).getLocalizedString
            
        self.language = None
        
        # Background image
        self.addControl(xbmcgui.ControlImage( 0, 0, 720, 576, os.path.join( IMAGEDIR,"background.png" ) ) )
        
        # Add central image 
        self.logo = xbmcgui.ControlImage( 65, 138, 590, 299, os.path.join( IMAGEDIR,"startupLogo.png" ) )
        self.addControl( self.logo )
        
        self.buttonEn = xbmcgui.ControlButton( 95, 310, 120, 30, "ENGLISH", textColor='0xFFFFFFFF', shadowColor='0xFF696969', focusedColor='0xFFFFFF00', focusTexture=os.path.join( IMAGEDIR, "list-black-focus.png" ), noFocusTexture=os.path.join( IMAGEDIR, "list-focus.png" ), alignment=6 )
        self.addControl( self.buttonEn )

        self.buttonFr = xbmcgui.ControlButton( 505, 310, 120, 30, "FRANCAIS", textColor='0xFFFFFFFF', shadowColor='0xFF696969', focusedColor='0xFFFFFF00', focusTexture=os.path.join( IMAGEDIR, "list-black-focus.png" ), noFocusTexture=os.path.join( IMAGEDIR, "list-focus.png" ), alignment=6 )
        self.addControl( self.buttonFr )

        self.buttonEn.controlRight( self.buttonFr )
        self.buttonFr.controlLeft( self.buttonEn )
        
        # Set Focus on 1st button
        self.setFocus( self.buttonEn )

    def getDefaultLanguage( self, configManager ):
        """
            Get the language chosen by the user
        """
        self.configManager = configManager
        
        # show this menu and wait until it's closed
        self.doModal()
        
        return self.language
    
    def onControl( self, control ):
        if control == self.buttonEn:
            self.configManager.setDefaultLanguage( 'english' )
            self.language = 'english'
            xbmc.sleep( 100 )
            self.close()
        if control == self.buttonFr:
            self.configManager.setDefaultLanguage( 'french' )
            self.language = 'french'
            xbmc.sleep( 100 )
            self.close()
            
    def onAction(self, action):
        if action == ACTION_PREVIOUS_MENU:
            dialogError = xbmcgui.Dialog()
            #dialogError.ok("Error", "You need to select a language the fisrt time", "in order to use this script", "You will be able to change it later on if necessary")
            dialogError.ok( self.__loc_language__( 32111 ), self.__loc_language__( 32116 ), self.__loc_language__( 32117 ), self.__loc_language__( 32118 ) )

            #close the window
            self.close()

 
class TacMainWindow( xbmcgui.WindowXML ):
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

        if ( self.configManager.getDefaultLanguage() == 'french' ):
            lang.setLanguage( "french" )
            print "french"
        else:
            lang.setLanguage( "english" )
            print "english"
            
        # Create a file manager and check directory
        self.fileMgr = fileMgr( dirCheckList )
        print "TacMainWindow __init__ DONE"

        # Lock the UI
        xbmcgui.lock()

        # Create selectCollectionWebpage instance in order to display choice of video collection
        self.CollectionSelector = SelectCollectionWebpage( tacBasePageURL, tacNameSelectList, tacUrlSelectList, self.configManager )
        print ( "self.CollectionSelector.selectionNameList" )
        print( self.CollectionSelector.selectionNameList )
        print ( "self.CollectionSelector.selectionURLList" )
        print( self.CollectionSelector.selectionURLList )
        
        # Update language variable at startup
        self.CollectionSelector.setCollectionLanguage( self.configManager.getDefaultLanguage() )

    def onInit( self ):
        print "onInit(): Window Initalized"
        #xbmcgui.lock()
        try: 
            self._reset_views()
            self.setProperty( "display-item-number", "" ) # Used for hidding item number during the update
            self.setProperty( "view-Collection", "activated" )
            
            # Update Labels
            self._set_menu_labels()
            self._set_settings_tab_labels( update="startup" )
            self._set_controls_visible()
        
        except:
            #EXC_INFO( LOG_ERROR, sys.exc_info(), self )
            print "Error setting comtrol with windowXML"
            print  (str( sys.exc_info()[0] ) )
            traceback.print_exc()
            
        # Unlock the UI
        xbmcgui.unlock()
           
        # Close the Loading Window 
        #self.dialogUI.close()
           
        # Update the list of video 
        self.updateDataOnMenu( self.CollectionSelector.getSelectedMenu() )
        self.updateControlListFromData()
        
        self.setProperty( "display-item-number", "activated" )
        # No UI is displayed, continue to get and display the picture (would be too long to wait if we were waiting doModla call)
        self.updateIcons()
        
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
            if self.CollectionSelector.isSubCollec( chosenIndex ): # this function will play the video if the list item was a video
                self._reset_views()
                self.setProperty( "display-item-number", "" ) # Used for hidding item number during the update
                self.setProperty( "view-Sub-Serie", "activated" )
                self.updateDataOnList( chosenIndex )
                self.updateControlListFromData()
                self.setProperty( "display-item-number", "activated" )
                self.updateIcons()
        
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
            if self.CollectionSelector.isSubCollec( chosenIndex ): # this function will play the video if the list item was a video
                self._reset_views()
                self.setProperty( "display-item-number", "" ) # Used for hidding item number during the update
                self.setProperty( "view-Sub-Serie", "activated" )
                self.updateDataOnList( chosenIndex )
                self.updateControlListFromData()
                self.setProperty( "display-item-number", "activated" )
                self.updateIcons()
                
        elif controlID == 140:
            # Language
            currentLanguage = self.CollectionSelector.getCollectionLanguage()
                    
            if currentLanguage == 'french':
                # Go to English
                self.CollectionSelector.setCollectionLanguage( 'english' )
                lang.setLanguage( "english" )
            else:
                # Go to French
                self.CollectionSelector.setCollectionLanguage( 'french' )
                lang.setLanguage( "french" )

            # Update Labels
            self._set_menu_labels()
            self._set_settings_tab_labels()          
            
            # Update display
            self.updateDataOnMenu( self.CollectionSelector.getSelectedMenu() )
            self.updateControlListFromData()
            self.setFocus( self.getControl( 140 ) ) # Set focus on language button
            self.updateIcons()
        
        elif controlID == 150:
            # Collection
            self._reset_views()
            self.setProperty( "display-item-number", "" ) # Used for hidding item number during the update
            self.setProperty( "view-Collection", "activated" )
            
            currentLanguageLabel = __language__( 32300 ) # 'Francais' or 'English'
            self.getControl( 100 ).setLabel( "[B]%s[/B]"%__language__( self.CollectionSelector.selectionNameList[0] ) + "[COLOR=0xFFFFFFFF] - %s[/COLOR]"%currentLanguageLabel )
            
            self.updateDataOnMenu(0)
            self.updateControlListFromData()
            self.setProperty( "display-item-number", "activated" )
            self.updateIcons()
            
        elif controlID == 160:
            # Serie
            self._reset_views()
            self.setProperty( "display-item-number", "" )
            self.setProperty( "view-Series", "activated" )
            
            currentLanguageLabel = __language__( 32300 )  # 'Francais' or 'English'
            self.getControl( 100 ).setLabel( "[B]%s[/B]"%__language__( self.CollectionSelector.selectionNameList[1] ) + "[COLOR=0xFFFFFFFF] - %s[/COLOR]"%currentLanguageLabel )
            
            self.updateDataOnMenu( 1 )
            self.updateControlListFromData()
            #self.setFocus(self.button1)
            self.setProperty( "display-item-number", "activated" )
            self.updateIcons()
            
        elif controlID == 170:
            # Extras
            self._reset_views()
            self.setProperty( "display-item-number", "" ) # Used for hidding item number during the update
            self.setProperty( "view-Extras", "activated" )
            
            currentLanguageLabel = __language__( 32300 )  # 'Francais' or 'English'
            self.getControl( 100 ).setLabel( "[B]%s[/B]"%__language__( self.CollectionSelector.selectionNameList[2] ) + "[COLOR=0xFFFFFFFF] - %s[/COLOR]"%currentLanguageLabel )
            
            self.updateDataOnMenu( 2 )
            self.updateControlListFromData()
            #self.setFocus(self.button1)
            self.setProperty( "display-item-number", "activated" )
            self.updateIcons()

        elif controlID == 180:
            # Ads
            self._reset_views()
            self.setProperty( "display-item-number", "" ) # Used for hidding item number during the update
            self.setProperty( "view-Ads", "activated" )
            
            currentLanguageLabel = __language__( 32300 )  # 'Francais' or 'English'
            self.getControl( 100 ).setLabel( "[B]%s[/B]"%__language__( self.CollectionSelector.selectionNameList[3] ) + "[COLOR=0xFFFFFFFF] - %s[/COLOR]"%currentLanguageLabel )
            
            self.updateDataOnMenu( 3 )
            self.updateControlListFromData()
            #self.setFocus(self.button1)
            self.setProperty( "display-item-number", "activated" )
            self.updateIcons()
            
        elif controlID == 190:
            # Settings
            self._reset_views()
            self.setProperty( "view-Settings", "activated" )
            #self._set_settings_tab_labels()

        elif controlID == 200:
            # About
            self._reset_views()
            self.setProperty( "view-About", "activated" )

        elif controlID == 201:
            # Settings decrease language button
            print "down"
            self._set_player_setting_label( update = "down" )
            
        elif controlID == 202:
            # Settings increase language button
            print "up"
            self._set_player_setting_label( update = "up" )
            
        elif controlID == 231:
            # Settings decrease language button
            self._set_language_setting_label( update = "down" )
            
        elif controlID == 232:
            # Settings increase language button
            self._set_language_setting_label( update = "up" )
            
        elif controlID == 261:
            # Settings decrease language button
            self._set_current_language_setting_label( update = "down" )
            
        elif controlID == 262:
            # Settings increase language button
            self._set_current_language_setting_label( update = "up" )
            
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
            Update tacData objet for a specific index in the menu 
        """
        # Display Loading Window while we are loading the information from the website
        dialogLoading = xbmcgui.DialogProgress()
        dialogLoading.create( __language__( 32000 ), __language__( 32102 ),__language__( 32110 ) ) # "Têtes à claques", "Chargement des informations", "Veuillez patienter..."
        try:
            curLanguage = self.CollectionSelector.getCollectionLanguage()
            self.CollectionSelector.updateCollectionData( menuSelectIndex, language=curLanguage, progressBar=dialogLoading )
            #self.CollectionSelector.updateCollectionData(menuSelectIndex,language=curLanguage)
            
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
        
    def updateDataOnList( self, listItemIndex ):
        """
            Update tacData objet for a specific index in the main list
        """
        # Display Loading Window while we are loading the information from the website
        dialogLoading = xbmcgui.DialogProgress()
        dialogLoading.create( __language__( 32000 ), __language__( 32102 ),__language__( 32110 ) ) # "Têtes à claques", "Chargement des informations", "Veuillez patienter..."
        
        try:
            curLanguage = self.CollectionSelector.getCollectionLanguage()
            self.CollectionSelector.updateSubCollectionData( listItemIndex, language=curLanguage, progressBar=dialogLoading )
            
            # Close the Loading Window 
            xbmc.sleep( 100 )
            dialogLoading.close()
        except Exception, e:
            print( "Exception during list update" )
            print( str( e ) )
            print ( str(sys.exc_info()[0] ) )
            traceback.print_exc()
        
            # Close the Loading Window 
            dialogLoading.close()
 
            dialogError = xbmcgui.Dialog()
            dialogError.ok( __language__( 32111 ), __language__( 32113 ), __language__( 32114 ), __language__( 32115 ) ) #"Erreur", "Impossible de charger la page Têtes à claques.tv", "probleme de connection?", "un changement sur le site distant?"

    def updateControlListFromData( self ):
        """
            Update ControlList objet 
        """
        # Create loading windows after updateData
        dialogimg = xbmcgui.DialogProgress()
        dialogimg.create( __language__( 32000 ), __language__( 32104 ), __language__( 32110 ) ) # "Têtes à claques", "Mise a jour des informations", "Veuillez patienter..."
        dialogimg.update( 0 )

        print "updateControlListFromData"

        menuSelectIndex  = self.CollectionSelector.getSelectedMenu()
        numberOfPictures = self.CollectionSelector.selectCollecData[menuSelectIndex].getNumberofItem()
        language         = self.CollectionSelector.getCollectionLanguage()
        videoLabel       = __language__( 32305 ) # " Vidéos"
        
        #print "List of videos:"    
        #print self.CollectionSelector.selectCollecData[menuSelectIndex].titleList

        # Clear all ListItems in this control list 
        self.clearList()
        
        # Lock the UI in order to update the list
        xbmcgui.lock()    

        numberOfItem = len( self.CollectionSelector.selectCollecData[menuSelectIndex].titleList )
            
        # add a few items to the list
        for name in self.CollectionSelector.selectCollecData[menuSelectIndex].titleList:
            index      = self.CollectionSelector.selectCollecData[menuSelectIndex].titleList.index( name )
            image2load = os.path.join( CACHEDIR, os.path.basename( self.CollectionSelector.selectCollecData[menuSelectIndex].imageFilenameList[index] ) )
            #print "updateControlListFromData - image2load = %s"%image2load              
            if not os.path.exists( image2load ) or os.path.isdir( image2load ):
                # images not here use default
                image2load = "tac_noImageAvailable_wide.jpg"
                self.addItem( xbmcgui.ListItem( label=name ) )
            else:
                self.addItem( xbmcgui.ListItem( label=name, thumbnailImage=image2load ) )
            
            # Compute % of Image proceeded
            percent = int( ( ( index + 1 ) * 100 ) / numberOfItem )
            dialogimg.update( percent, __language__( 32104 ),__language__( 32110 ) ) # There is an issue during Display View: Icons appear, so in order to prevent it we force dsiplay of '32104' instead

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
        menuSelectIndex = self.CollectionSelector.getSelectedMenu()
        print "updateIcons"
        try:       
            for name in self.CollectionSelector.selectCollecData[menuSelectIndex].titleList:
                index           = self.CollectionSelector.selectCollecData[menuSelectIndex].titleList.index( name )
                image2load      = os.path.join( CACHEDIR, os.path.basename( self.CollectionSelector.selectCollecData[menuSelectIndex].imageFilenameList[index] ) )                        
                image2download  = self.CollectionSelector.selectCollecData[menuSelectIndex].imageFilenameList[index]
                image2save      = os.path.join( CACHEDIR,os.path.basename( self.CollectionSelector.selectCollecData[menuSelectIndex].imageFilenameList[index] ) )
                
                # Downloading image
                try:
                    downloadJPG( image2download, image2save )
                except:
                    print( "Exception on image downloading: " + image2download )

                # Display the picture
                print "image2save = %s"%image2save
                print "image2download = %s"%image2download
                if os.path.exists( image2save ) and not image2download.endswith( '/' ):
                    #print "set image %s"%image2save
                    self.getListItem( index ).setThumbnailImage( image2save )
                else:
                    print "%s does NOT exist"%image2save
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
        self.setProperty( "view-Collection", "" )
        self.setProperty( "view-Series", "" )
        self.setProperty( "view-Sub-Serie", "" )
        self.setProperty( "view-Extras", "" )
        self.setProperty( "view-Ads", "")
        self.setProperty( "view-Settings", "" )
        self.setProperty( "view-About", "" )
        
        
    def _set_menu_labels( self ):
        try:
            # Logo
            logoImage = os.path.join( IMAGEDIR,__language__( 32900 ) )    
                
            # Menu labels
            optionLabel             = __language__( 32303 ) # "Options"
            buttonlanguageLabel     = __language__( 32301 ) # "English"
            aboutLabel              = __language__( 32304 ) # "A propos"
            currentLanguageLabel    = __language__( 32300 ) # "Francais"
            menuInfoLabel           = __language__( 32302 ) # "SELECTIONNEZ:"
            collectionLabel         = __language__( self.CollectionSelector.selectionNameList[0] ) # Collection
            seriesLabel             = __language__( self.CollectionSelector.selectionNameList[1] ) # Séries
            extrasLabel             = __language__( self.CollectionSelector.selectionNameList[2] ) # Extras
            adsLabel                = __language__( self.CollectionSelector.selectionNameList[3] ) # Pubs
            videoNbLabel            = __language__( 32305 ) # Video(s)
            serieNbLabel            = __language__( 32307 ) # Serie(s)
            scriptTitleAboutLabel   = "%s"%( __language__( 32000 ) )
            versionAboutLabel       = "[B]%s[/B]%s"%( __language__( 32800 ), __version__ )
            authorAboutLabel        = "[B]%s[/B]%s"%( __language__( 32801 ), __author__ )
            descriptTitleAboutLabel = "[B]%s[/B]"%( __language__( 32802 ) )
            descriptContAboutLabel  = "%s"%( __language__( 32803 ) )
            copyRightsAboutLabel    = "%s"%( __language__( 32804 ) )
            
            # Set the labels
            self.getControl( 30 ).setImage( logoImage )
            self.getControl( 100 ).setLabel( "[B]%s[/B]"%__language__( self.CollectionSelector.selectionNameList[self.CollectionSelector.getSelectedMenu()] ) + "[COLOR=0xFFFFFFFF] - %s[/COLOR]"%currentLanguageLabel )
            self.setProperty( "video-number-label", videoNbLabel )
            self.setProperty( "serie-number-label", serieNbLabel )
            
            self.getControl( 140 ).setLabel( buttonlanguageLabel )
            self.getControl( 150 ).setLabel( collectionLabel )
            self.getControl( 160 ).setLabel( seriesLabel )
            self.getControl( 170 ).setLabel( extrasLabel )
            self.getControl( 180 ).setLabel( adsLabel )
            self.getControl( 190 ).setLabel( optionLabel )
            self.getControl( 200 ).setLabel( aboutLabel )
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
        self.getControl( 203 ).setLabel( defaultPlayerTitleLabel, label2=defaultPlayerContentLabel )

    def _set_language_setting_label( self, update="startup" ):
        defaultLanguageTitleLabel = __language__( 32504 ) # Langue: 
        languageMenuList          = [__language__( 32505 ), __language__( 32506 ), __language__( 32515 )] # "French","English"
        languageList              = ["french","english","none"] # Languages - strings used in conf file
        
        if update == "default":
            self.defaultLanguageDisplay = "none"
            defaultLanguageContentLabel = languageMenuList[languageList.index( self.defaultLanguageDisplay )]
            self.defaultLanguageUpdated = True # flag indicating on exit if they have been modified
            self.activateSaveSettings()
        elif  update == "refresh":
            defaultLanguageContentLabel = languageMenuList[languageList.index( self.defaultLanguageDisplay )]
        elif update == "startup":
            self.defaultLanguageDisplay = self.configManager.getDefaultLanguage()
            defaultLanguageContentLabel = languageMenuList[languageList.index( self.defaultLanguageDisplay )]
            self.defaultLanguageUpdated = False # flag indicating on exit if they have been modified
        elif  update == "up":
            currentIndex = languageList.index( self.defaultLanguageDisplay )
            if currentIndex < (len(languageList)-1):
                newIndex = currentIndex + 1
            else:
                # Max reached
                newIndex = 0
            defaultLanguageContentLabel = languageMenuList[newIndex]
            self.defaultLanguageDisplay = languageList[newIndex]
            self.defaultLanguageUpdated = True # flag indicating on exit if they have been modified
            self.activateSaveSettings()
        elif update == "down":
            currentIndex                = languageList.index( self.defaultLanguageDisplay )
            if currentIndex > 0:
                newIndex = currentIndex - 1
            else:
                # Min reached
                newIndex = ( len( languageList ) - 1 )
            defaultLanguageContentLabel = languageMenuList[newIndex]
            self.defaultLanguageDisplay = languageList[newIndex]
            self.defaultLanguageUpdated = True # flag indicating on exit if they have been modified
            self.activateSaveSettings()
        # Update label
        self.getControl( 233 ).setLabel( defaultLanguageTitleLabel, label2=defaultLanguageContentLabel )

    def _set_current_language_setting_label( self, update="startup" ):
        currentLanguageTitleLabel   = __language__( 32516 ) # Langue: 
        languageMenuList            = [__language__( 32505 ), __language__( 32506 )] # "French","English"
        languageList                = ["french","english"] # Languages - strings used in conf file
        currentLanguageUpdated      = False
        
        if update == "startup":
            self.currentLanguage = self.CollectionSelector.getCollectionLanguage()
            currentLanguageContentLabel = languageMenuList[languageList.index( self.currentLanguage )]
        elif  update == "refresh":
            currentLanguageContentLabel = languageMenuList[languageList.index( self.currentLanguage )]
        elif  update == "up":
            currentIndex                = languageList.index( self.currentLanguage )
            if currentIndex < ( len( languageList ) - 1 ):
                newIndex = currentIndex + 1
            else:
                # Max reached
                newIndex = 0
            currentLanguageContentLabel = languageMenuList[newIndex]
            self.currentLanguage = languageList[newIndex]
            currentLanguageUpdated = True # flag indicating on exit if they have been modified
        elif update == "down":
            currentIndex                = languageList.index( self.currentLanguage )
            if currentIndex > 0:
                newIndex = currentIndex - 1
            else:
                # Min reached
                newIndex = ( len( languageList ) - 1 )
            currentLanguageContentLabel = languageMenuList[newIndex]
            self.currentLanguage        = languageList[newIndex]
            currentLanguageUpdated      = True # flag indicating on exit if they have been modified
        # Update label
        self.getControl( 263 ).setLabel( currentLanguageTitleLabel, label2=currentLanguageContentLabel )

        if currentLanguageUpdated:
            # Update the language of the UI (all the labels will be updated)
            self._set_current_language( self.currentLanguage )
            self.currentLanguageUpdated = False

    def _set_current_language( self,language ):
        """
            Set the current language of the UI
        """
        if language == 'english':
            # Go to English
            self.CollectionSelector.setCollectionLanguage( 'english' )
            lang.setLanguage( "english" )
        else:
            # Go to French
            self.CollectionSelector.setCollectionLanguage( 'french' )
            lang.setLanguage( "french" )

        # Update Labels
        self._set_menu_labels()
        self._set_settings_tab_labels( 'refresh' )          
        
        # Update display
        self.updateDataOnMenu( self.CollectionSelector.getSelectedMenu() )
        self.updateControlListFromData()
        self.updateIcons()

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
            
            # - Startup Language
            self._set_language_setting_label( update="default" )
            
            # - Cache cleaning
            self._set_cleancache_setting_label( update="default" )
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
            self._set_current_language_setting_label( update )
            
            # - Player
            self._set_player_setting_label( update )
            
            # - Startup Language
            self._set_language_setting_label( update )
            
            # - Cache cleaning
            self._set_cleancache_setting_label( update )
            
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
            bouton_non_visible = [ 100, 115, 125, 140 ]
            for control_id in bouton_non_visible:
                self.getControl( control_id ).setEnabled( False )
                self.getControl( control_id ).setVisible( False ) 
        
        except:
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )
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
        if self.defaultLanguageUpdated:
            self.configManager.setDefaultLanguage( self.defaultLanguageDisplay, False )
            save = True
        if self.cleanCacheUpdated:
            self.configManager.setCleanCache( self.cleanCacheDisplay, False )
            save = True
            
        if save == True:
            # Save conf file
            dialogsave = xbmcgui.DialogProgress()
            dialogsave.create( __language__( 32000 ), __language__( 32701 ),__language__( 32110 ) ) 
            dialogsave.update(0)
            if self.configManager.saveConfFile():
                dialogsave.update( 100 )
                xbmc.sleep( 100 )
                dialogsave.close()
                
                # Reset update flags
                self.defaultPlayerUpdated   = False
                self.defaultLanguageUpdated = False
                self.cleanCacheUpdated      = False
                
                # Disable save button
                self.deactivateSaveSettings()
                
                dialogInfo = xbmcgui.Dialog()
                result = dialogInfo.ok( __language__( 32000 ), __language__( 32703 ) )
            else:
                dialogsave.update( 100 )
                xbmc.sleep( 200 )
                dialogsave.close()
                
                dialogInfo = xbmcgui.Dialog()
                result = dialogInfo.ok( __language__( 32000 ), __language__( 32702 ) )
        else:
            print 'self.currentLanguageUpdated'
            print self.currentLanguageUpdated
            if not self.currentLanguageUpdated:
                dialogInfo = xbmcgui.Dialog()
                result = dialogInfo.ok( __language__( 32000 ), __language__( 32704 ) )
            else:
                self.currentLanguageUpdated = False # Reset update flags
            

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



        
def show_tac_main_window( startupwin=None ):
    """
        Create TAC Main Window UI
    """
    file_xml = "tac-MainWindow.xml"
    #file_xml = "Script_WindowXMLExample.xml"
    #depuis la revision 14811 on a plus besoin de mettre le chemin complet, la racine suffit
    dir_path = ROOTDIR 
    #recupere le nom du skin et si force_fallback est vrai, il va chercher les images du defaultSkin.
    current_skin, force_fallback = getUserSkin()
    
    print "Creating TacMainWindow"
    w = TacMainWindow( file_xml, dir_path, current_skin, force_fallback, startupwin=startupwin )
    w.doModal()
    del w
                        

def startup():
    """
    
        Startup function
    
    """
    # Create a file manager and check directory
    fisrtStartFileMgr = fileMgr( dirCheckList )
    
    # Check conf file
    fisrtStartConfigManager = configCtrl()
    setting_language = fisrtStartConfigManager.getDefaultLanguage()
    print setting_language
        
    if setting_language == "" or setting_language == "none":
        # Language not set
        print "Language not set"
        # Get language using FirstStartWindow
        selectLangWin = FirstStartWindow()
        language = selectLangWin.getDefaultLanguage( fisrtStartConfigManager )
        del selectLangWin
        del fisrtStartConfigManager
        del fisrtStartFileMgr
        if language != None:
            # Create main Window
            show_tac_main_window()
    else:
        print "Language already set"
        # Create main Window
        show_tac_main_window()
    
    
    

########
#
# Main
#
########

if __name__ == "__main__":
    print( str( "=" * 85 ) )
    print( "" )
    print( "TAC.tv XBMC script STARTS".center( 85 ) )
    print( "" )
    print( str( "=" * 85 ) )
    
    # Print Path information
    print( "ROOTDIR"  + ROOTDIR )
    print( "IMAGEDIR" + IMAGEDIR )
    print( "CACHEDIR" + CACHEDIR )
    print( "CONFDIR"  + CONFDIR )
    
    # Calling startup function
    #show_tac_main_window()
    startup()
else:
    # Library case
    pass


