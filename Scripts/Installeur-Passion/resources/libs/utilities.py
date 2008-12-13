"""
Module de partage des fonctions et des constantes

"""

#Modules general
import os
import re
import sys
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


def get_system_platform():
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
    text = text.replace( "\n", "[CR]" )
    text = text.replace( "\r\r", "[CR]" )
    text = text.replace( "\r", "[CR]" )
    return text


def set_pretty_formatting( text, bold_links=False ):
    """ FONCTION POUR RENDRE COMPATIBLE LES TAGS HTML POUR XBMC """
    text = text.replace( "<br />", "\n" )#.replace( "<br />", "[CR]" )
    text = text.replace( "<i>", "[I]" ).replace( "</i>", "[/I]" )
    text = text.replace( "<b>", "[B]" ).replace( "</b>", "[/B]" )
    text = re.sub( "(?s)</[^>]*>", "\n", text )
    if bold_links:
        text = re.sub( "(?s)</[^>]*>", "[/B]", text )
        text = re.sub( "(?s)<[^>]*>", "[B]", text )
    return text


def strip_off( text, by="", xbmc_labels_formatting=False ):
    """ FONCTION POUR RECUPERER UN TEXTE D'UN TAG """
    if xbmc_labels_formatting:
        text = text.replace( "[", "<" ).replace( "]", ">" )
    return re.sub( "(?s)<[^>]*>", by, text )


class CONVERT:
    def __init__( self, strvalue="" ):
        # Internal -- convert entity or character reference
        # http://www.toutimages.com/codes_caracteres.htm
        strvalue = self._replace_html_to_iso( strvalue )

        self.entitydefs = { 'lt': '<', 'gt': '>', 'amp': '&', 'quot': '"', 'apos': '\'' }

        self.entity_or_charref = re.compile( '&(?:'
            '([a-zA-Z][-.a-zA-Z0-9]*)|#([0-9]+)'
            ')(;?)' ).sub( self._convert_ref, strvalue )

    def _replace_html_to_iso( self, strvalue ):
        strvalue = strvalue.replace( "&#160;", '&nbsp;' )
        # NO CONFORM
        html_to_iso = {
            '&#8211;': "-",
            '&#8217;': "'",
            '&euro;': "&#128;",
            '&ldquo;': "&#147;",
            '&rdquo;': "&#148;",
            '&nbsp;': "&#32;", #'&nbsp;':   "&#160;",
            '&hellip;': "&#133;", '&Hellip;': "&#133;",
            '&agrave;': "&#224;", '&Agrave;': "&#192;",
            '&acirc;':  "&#226;", '&Acirc;':  "&#194;",
            '&ccedil;': "&#231;", '&Ccedil;': "&#199;",
            '&egrave;': "&#232;", '&Egrave;': "&#200;",
            '&eacute;': "&#233;", '&Eacute;': "&#201;",
            '&ecirc;':  "&#234;", '&Ecirc;':  "&#202;",
            '&icirc;':  "&#238;", '&Icirc;':  "&#206;",
            '&iuml;':   "&#239;", '&Iuml;':   "&#207;",
            '&ocirc;':  "&#244;", '&Ocirc;':  "&#212;",
            '&ugrave;': "&#249;", '&Ugrave;': "&#217;",
            '&ucirc;':  "&#251;", '&Ucirc;':  "&#219;"
            }
        for key, value in html_to_iso.items():
            strvalue = strvalue.replace( key, value )
        return strvalue

    def _convert_ref( self, match ):
        if match.group( 2 ):
            return self.convert_charref( match.group( 2 ) ) or ( '&#%s%s' % match.groups( )[ 1: ] )
        elif match.group( 3 ):
            return self.convert_entityref( match.group( 1 ) ) or ( '&%s;' % match.group( 1 ) )
        else:
            return '&%s' % match.group( 1 )

    def convert_charref( self, name ):
        """Convert character reference, may be overridden."""
        try:
            n = int( name )
        except ValueError:
            return
        if not 0 <= n <= 255:
            return
        return self.convert_codepoint( n )

    def convert_codepoint( self, codepoint ):
        return chr( codepoint )

    def convert_entityref( self, name ):
        """Convert entity references.

        As an alternative to overriding this method; one can tailor the
        results by setting up the self.entitydefs mapping appropriately.
        """
        table = self.entitydefs
        if name in table:
            return table[ name ]
        else:
            return


class Settings:
    """ this function comes from apple movie trailer """
    def _settings_defaults_values( self ):
        defaults = {
            # GENERAL
            "updating": False,
            "update_startup": True,
            "xbmc_xml_update": False,
            "rss_feed": "1",
            "script_debug": False,
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
        logger.LOG( logger.LOG_DEBUG, "Settings: [used default settings]" )
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
