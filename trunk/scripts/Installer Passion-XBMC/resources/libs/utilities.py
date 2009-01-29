"""
Module de partage des fonctions et des constantes

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
    "cancelRequest",
    "SYSTEM_PLATFORM",
    "XBMC_ROOT",
    "parse_rss_xml",
    "set_web_navigator",
    "is_playable_media",
    "get_html_source",
    "getUserSkin",
    "getSkinColors",
    "get_default_hex_color",
    "add_pretty_color",
    "bold_text",
    "italic_text",
    "set_xbmc_carriage_return",
    "strip_off",
    "Slideshow",
    "Settings",
    "get_infos_path",
    ]

#Modules general
import os
import re
import sys
import time
import urllib
import urllib2
import elementtree.ElementTree as ET

#modules XBMC
import xbmc
import xbmcgui

#module logger
try:
    logger = sys.modules[ "__main__" ].logger
except:
    import script_log as logger


#REPERTOIRE RACINE ( default.py )
CWD = os.getcwd().rstrip( ";" )

try: __script__ = sys.modules[ "__main__" ].__script__
except: __script__ = os.path.basename( CWD )

BASE_SETTINGS_PATH = os.path.join( xbmc.translatePath( "P:\\script_data" ), __script__, "settings.txt" )
RSS_FEEDS_XML = os.path.join( CWD, "resources", "RssFeeds.xml" )


class cancelRequest( Exception ):
    """
    Exception, merci a Alexsolex
    """
    def __init__( self, value ):
        self.value = value
    def __str__( self ):
        return repr( self.value )


def get_system_platform():
    """ fonction: pour recuperer la platform que xbmc tourne """
    platform = "unknown"
    if xbmc.getCondVisibility( "system.platform.linux" ):
        platform = "linux"
    elif xbmc.getCondVisibility( "system.platform.xbox" ):
        platform = "xbox"
    elif xbmc.getCondVisibility( "system.platform.windows" ):
        platform = "windows"
    elif xbmc.getCondVisibility( "system.platform.osx" ):
        platform = "osx"
    return platform

SYSTEM_PLATFORM = get_system_platform()
# we use "U:\\" for linux, windows and osx for platform mode and "Q:\\" for xbox
XBMC_ROOT = xbmc.translatePath( ( "U:\\", "Q:\\", )[ ( SYSTEM_PLATFORM == "xbox" ) ] )


def parse_rss_xml( xml_path=RSS_FEEDS_XML ):
    """ fonction: pour parser le fichier RssFeeds.xml """
    feeds = {}
    try:
        feed = open( xml_path )
        tree = ET.parse( feed )
        feed.close()
        for elems in tree.getroot():
            try:
                urlset, title, feed = elems.getiterator()
                urlset = urlset.attrib.get( "id" )
                if urlset:
                    feeds[ urlset ] = {
                        "updateinterval": int( feed.attrib.get( "updateinterval", "30" ) ),
                        "title": title.text,
                        "feed": feed.text,
                        }
            except:
                logger.EXC_INFO( logger.LOG_DEBUG, sys.exc_info() )
        del tree
    except:
        logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info() )
    return feeds


def set_web_navigator( navigator="" ):
    """ fonction: pour parcourir le navigateur web """
    mask = ( "", ".bat|.exe", )[ ( SYSTEM_PLATFORM == "windows" ) ]
    browser_path = xbmcgui.Dialog().browse( 1, sys.modules[ "__main__" ].__language__( 520 ), "files", mask, False, False, navigator )
    if browser_path:
        title = os.path.basename( browser_path ).split( "." )[ 0 ].title()
        keyboard = xbmc.Keyboard( title, sys.modules[ "__main__" ].__language__( 521 ) )
        keyboard.doModal()
        if keyboard.isConfirmed():
            title = keyboard.getText()
        return title, browser_path


def is_playable_media( filename, media="picture" ):
    """
    getSupportedMedia(media) -- Returns the supported file types for the specific media as a string.
    media          : string - media type
    *Note, media type can be (video, music, picture).
           The return value is a pipe separated string of filetypes (eg. '.mov|.avi').
           You can use the above as keywords for arguments and skip certain optional arguments.
           Once you use a keyword, all following arguments require the keyword.
    example:
      - mTypes = xbmc.getSupportedMedia('video')
    """
    media_types = xbmc.getSupportedMedia( media ).split( "|" )
    try:
        return os.path.splitext( filename )[ 1 ].lower() in media_types
    except:
        logger.EXC_INFO( logger.LOG_DEBUG, sys.exc_info() )
        # si on arrive ici le retour est automatiquement None


def get_html_source( url ):
    """ fetch the html source """
    try:
        if os.path.isfile( url ):
            sock = open( url, "r" )
        else:
            sock = urllib.urlopen( url )
        htmlsource = sock.read()
        sock.close()
        return htmlsource
    except:
        logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info() )
        return ""


def getUserSkin():
    """ FONCTION POUR RECUPERER LE THEME UTILISE PAR L'UTILISATEUR """
    current_skin = xbmc.getSkinDir()
    force_fallback = os.path.exists( os.path.join( CWD, "resources", "skins", current_skin ) )
    if not force_fallback: current_skin = "Default"
    return current_skin, force_fallback


def getSkinColors():
    """ FONCTION POUR RECUPERER LES COULEURS THEME """
    try:
        current_skin, force_fallback = getUserSkin()
        current_skin = os.path.join( CWD, "resources", "skins", current_skin )
        colors_file = os.path.join( current_skin, "colors", "colors.xml" )
        if os.path.exists( colors_file ):
            colors = re.compile( '<color name="(.*?)">(.*?)</color>' ).findall( file( colors_file, "r" ).read() )
            return colors
    except:
        logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info() )


def get_default_hex_color():
    try:
        default_hex_color = dict( getSkinColors() ).get( "default", "FFFFFFFF" )
    except:
        logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info() )
        default_hex_color = "FFFFFFFF"
    return default_hex_color


#NOTE: CE CODE PEUT ETRE REMPLACER PAR UN CODE MIEUX FAIT
def add_pretty_color( word, start="all", end=None, color=None ):
    """ FONCTION POUR METTRE EN COULEUR UN MOT OU UNE PARTIE """
    try:
        if color and start == "all":
            pretty_word = "[COLOR=" + color + "]" + word + "[/COLOR]"
        else:
            pretty_word = []
            for letter in word:
                if color and letter == start:
                    pretty_word.append( "[COLOR=" + color + "]" )
                elif color and letter == end:
                    pretty_word.append( letter )
                    pretty_word.append( "[/COLOR]" )
                    continue
                pretty_word.append( letter )
            pretty_word = "".join( pretty_word )
        return pretty_word
    except:
        logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info() )
        return word


def bold_text( text ):
    """ FONCTION POUR METTRE UN MOT GRAS """
    return "[B]%s[/B]" % ( text, )


def italic_text( text ):
    """ FONCTION POUR METTRE UN MOT ITALIQUE """
    return "[I]%s[/I]" % ( text, )


def set_xbmc_carriage_return( text ):
    """ only for xbmc """
    text = text.replace( "\r\n", "[CR]" )
    text = text.replace( "\n\n", "[CR]" )
    text = text.replace( "\n",   "[CR]" )
    text = text.replace( "\r\r", "[CR]" )
    text = text.replace( "\r",   "[CR]" )
    return text


def strip_off( text, by="", xbmc_labels_formatting=False ):
    """ FONCTION POUR RECUPERER UN TEXTE D'UN TAG """
    if xbmc_labels_formatting:
        text = text.replace( "[", "<" ).replace( "]", ">" )
    return re.sub( "(?s)<[^>]*>", by, text )


class Slideshow:
    def clearPlayList( self, m3u ):
        #xbmc.PlayList(0).clear()
        #xbmc.PlayList(1).clear()
        try: os.unlink( m3u )
        except: pass


    def playSlideshow( self, screens=[] ):
        if not screens: return
        elif len( screens ) == 1:
            xbmc.executehttpapi( "ShowPicture(%s)" % ( screens[ 0 ], ) )
        else:
            #Clears the slideshow playlist.
            #print xbmc.executehttpapi( "ClearSlideshow" )

            #AddToSlideshow(media;[mask];[recursive])
            #Adds a file or folder (media is either a file or a folder) to the slideshow playlist. To specify a file mask use mask e.g. .jpg|.bmp
            #[Added 4 Jan 08] If recursive = "1" and media is a folder then all appropriate media within subfolders beneath media will be added otherwise only media within the folder media
            #will be added. Default behaviour is to be recursive. [Added 5 Jan 08] mask can now also be set to one of the
            #following values [music], [video], [pictures], [files] in which case XBMC's current set of file extensions for the
            #type specified will be used as the mask. (Note it only makes much sense for this command to use a value of [pictures].

            m3u = os.path.join( xbmc.translatePath( "Z:\\" ), "passion_slideshow.m3u" )
            #clearPlayList is not very necessary, because next line "w" is used. "w" == write new file.
            self.clearPlayList( m3u )

            file = open( m3u, "w+" )
            file.write( "#EXTM3U" )
            for count, screen in enumerate( screens ):
                #thumb = xbmc.getCacheThumbName( screen )
                #print thumb
                file.write( "\n#EXTINF:0,%i - %s\n%s" % ( ( count + 1 ), os.path.basename( screen ), screen, ) )
                #print xbmc.executehttpapi( "AddToSlideshow(%s)" % ( screen, ) )
            file.close()

            #PlaySlideshow([directory];[recursive])
            #Starts the slideshow. Directory specifies a folder of images to add to the slideshow playlist.
            #If recursive has a value of True then all directories beneath directory are searched for images and added to the slideshow playlist.
            xbmc.executehttpapi( "PlaySlideshow(%s;false)" % ( m3u, ) )


class Settings:
    """ this function comes from apple movie trailer """
    def _settings_defaults_values( self ):
        defaults = {
            # GENERAL
            "updating": False,
            "update_startup": True,
            "xbmc_xml_update": False,
            "rss_feed": ( "0", "1", )[ ( xbmc.getLanguage().lower() == "french" ) ],
            "script_debug": False,
            "manager_view_mode": 50,
            "main_view_mode": 50,
            # SKINS
            "skin_colours_path": "default",
            "skin_colours": "",
            # SERVEUR FTP
            "host": "stock.passionxbmc.org",
            "user": "anonymous",
            "password": "xxxx",
            # FORUM
            "topics_limit": "5",
            "web_title": "",
            "hide_forum": False,
            "web_navigator": "",
            "win32_exec_wait": False,
            }
        return defaults

    def get_settings( self, defaults=False ):
        """ read settings """
        try:
            settings = {}
            if ( defaults ): raise
            settings_file = open( BASE_SETTINGS_PATH, "r" )
            settings = eval( settings_file.read() )
            settings_file.close()
            if settings:
                settings = self._check_compatibility( settings )
        except:
            settings = self._use_defaults( settings, save=( defaults == False ) )
        return settings

    def _check_compatibility( self, current_settings={} ):
        try:
            if sorted( current_settings.keys() ) != sorted( self._settings_defaults_values().keys() ):
                logger.LOG( logger.LOG_WARNING, "Settings: [added default values for missing settings]" )
                return self._use_defaults( current_settings )
        except:
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info() )
        return current_settings

    def _use_defaults( self, current_settings=None, save=True ):
        """ setup default values if none obtained """
        #TODO: verifier pourquoi la ligne suivante fait planter XBMC sous Mac
        #logger.LOG( logger.LOG_DEBUG, "Settings: [used default settings]" )
        settings = {}
        defaults = self._settings_defaults_values()
        for key, value in defaults.items():
            # add default values for missing settings
            settings[ key ] = current_settings.get( key, defaults[ key ] )
        if ( save ):
            ok = self.save_settings( settings )
        return settings

    def save_settings( self, settings ):
        """ save settings """
        try:
            settings_file = open( BASE_SETTINGS_PATH, "w" )
            settings_file.write( repr( settings ) )
            settings_file.close()
            return True
        except:
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )
            return False


try:
    import xbmc
    """
    getRegion(id) -- Returns your regions setting as a string for the specified id.
     
    id             : string - id of setting to return
     
    *Note, choices are (dateshort, datelong, time, meridiem, tempunit, speedunit)
     
           You can use the above as keywords for arguments and skip certain optional arguments.
           Once you use a keyword, all following arguments require the keyword.
     
    example:
      - date_long_format = xbmc.getRegion('datelong')
    """
    date_long_format = xbmc.getRegion( "datelong" ).replace( "DDDD, ", "" ).replace( "MMMM", "%m" ).replace( "D", "%d" ).replace( "YYYY", "%Y" )
    time_format = xbmc.getRegion( "time" ).replace( "H", "%H" ).replace( "mm", "%M" ).replace( "ss", "%S" )
    DATE_TIME_FORMAT = date_long_format.replace( " ", "-" ) + " | " + time_format
except:
    DATE_TIME_FORMAT = "%d-%m-%y | %H:%M:%S"


def get_infos_path( path ):
    # Return the system's ctime which, on some systems (like Unix) is the time of the last change, and, on others (like Windows), is the creation time for path. The return value is a number giving the number of seconds since the epoch (see the time module). Raise os.error if the file does not exist or is inaccessible. New in version 2.3.
    try: c_time = time.strftime( DATE_TIME_FORMAT, time.localtime( os.path.getctime( path ) ) )
    except: c_time = ""

    # Return the time of last access of path. The return value is a number giving the number of seconds since the epoch (see the time module). Raise os.error if the file does not exist or is inaccessible. New in version 1.5.2. Changed in version 2.3: If os.stat_float_times() returns True, the result is a floating point number.
    try: last_access = time.strftime( DATE_TIME_FORMAT, time.localtime( os.path.getatime( path ) ) )
    except: last_access = ""

    # Return the time of last modification of path. The return value is a number giving the number of seconds since the epoch (see the time module). Raise os.error if the file does not exist or is inaccessible. New in version 1.5.2. Changed in version 2.3: If os.stat_float_times() returns True, the result is a floating point number.
    try: last_modification = time.strftime( DATE_TIME_FORMAT, time.localtime( os.path.getmtime( path ) ) )
    except: last_modification = ""

    # Return the size, in bytes, of path. Raise os.error if the file does not exist or is inaccessible. New in version 1.5.2.
    # calculate dir size "os.walk( path, topdown=False )"
    try:
        size = 0
        if os.path.isfile( path ):
            try: size += os.path.getsize( fpath )
            except: pass
        else:
            for root, dirs, files in os.walk( path, topdown=False ):
                for file in files:
                    try:
                        fpath = os.path.join( root, file )
                        size += os.path.getsize( fpath )
                    except:
                        pass
        if size <= 0:
            size = "0.0 KB"
        elif 1024.0 > size < ( 1024.0 * 1024.0 ):
            size = "%00s KB" % round( size / 1024.0, 2 )
        elif size > ( 1024.0 * 1024.0 ):
            size = "%00s MB" % round( size / 1024.0 / 1024.0, 2 )
        else:
            size = "%00s Bytes" % size
    except:
        size = "0.0 KB"

    return size, c_time, last_access, last_modification
