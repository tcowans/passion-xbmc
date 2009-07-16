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
    "BASE_CACHE_PATH",
    "SPECIAL_PROFILE_DIR",
    "SPECIAL_PLUGIN_DATA",
    "SPECIAL_PLUGIN_CACHE",
    "translate_string",
    "reduced_path",
    "get_thumbnail",
    "get_nfo_thumbnail",
    "get_browse_dialog",
    ]

#Modules general
import os
import sys
import urllib
from string import maketrans
from traceback import print_exc

#modules XBMC
import xbmc
import xbmcgui


SPECIAL_PROFILE_DIR = xbmc.translatePath( "special://profile/" )

BASE_CACHE_PATH = os.path.join( SPECIAL_PROFILE_DIR, "Thumbnails", "Video" )

try: scriptname = sys.modules[ "__main__" ].__plugin__
except: scriptname = os.path.basename( os.getcwd() )

SPECIAL_PLUGIN_DATA = os.path.join( SPECIAL_PROFILE_DIR, "plugin_data", "video", scriptname )
if not os.path.isdir( SPECIAL_PLUGIN_DATA ): os.makedirs( SPECIAL_PLUGIN_DATA )

SPECIAL_PLUGIN_CACHE = os.path.join( SPECIAL_PLUGIN_DATA, "cache" )
if not os.path.isdir( SPECIAL_PLUGIN_CACHE ): os.makedirs( SPECIAL_PLUGIN_CACHE )


def translate_string( strtrans, del_char="" ):
    # frm = Representation of " Non-ASCII character "
    if "\xc3\xa9" in strtrans:
        strtrans = strtrans.replace( "\xc3\xa9", "\xe9" )
    frm = '\xe1\xc1\xe0\xc0\xe2\xc2\xe4\xc4\xe3\xc3\xe5\xc5\xe6\xc6\xe7\xc7\xd0\xe9\xc9\xe8\xc8\xea\xca\xeb\xcb\xed\xcd\xec\xcc\xee\xce\xef\xcf\xf1\xd1\xf3\xd3\xf2\xd2\xf4\xd4\xf6\xd6\xf5\xd5\xf8\xd8\xdf\xfa\xda\xf9\xd9\xfb\xdb\xfc\xdc\xfd\xdd'
    #print " Non-ASCII character =", frm
    to = "aAaAaAaAaAaAaAcCDeEeEeEeEiIiIiIiInNoOoOoOoOoOoOsuUuUuUuUyY"
    # Construct a translation string
    table = maketrans( frm, to )
    is_unicode = 0
    if isinstance( strtrans, unicode ):
        is_unicode = 1
        # remove unicode
        strtrans = "".join( [ chr( ord( char ) ) for char in strtrans ] )
    if not del_char:
        # set win32 and xbox default invalid characters
        del_char = """,*=|<>?;:"+""" #+ "\xc3\xa9"
    # translation string
    s = strtrans.translate( table, del_char )
    # now remove others invalid characters
    s = "".join( [ char for char in s if ord( char ) < 127 ] )
    if is_unicode:
        #replace unicode
        s = unicode( s )#, "utf-8" )
    return s


def reduced_path( fpath ):
    try:
        list_path = fpath.split( os.sep )
        for pos in list_path[ 1:-2 ]:
            list_path[ list_path.index( pos ) ] = ".."
        return os.sep.join( list_path )
    except:
        return fpath


def get_thumbnail( path ):
    try:
        fpath = path
        # make the proper cache filename and path so duplicate caching is unnecessary
        filename = xbmc.getCacheThumbName( fpath )
        thumbnail = os.path.join( BASE_CACHE_PATH, filename[ 0 ], filename )
        # if the cached thumbnail does not exist check for a tbn file
        if ( not os.path.isfile( thumbnail ) ):
            # create filepath to a local tbn file
            thumbnail = os.path.splitext( path )[ 0 ] + ".tbn"
            try: thumbnail = thumbnail.encode( "utf-8" )
            except: pass
            # if there is no local tbn file leave blank
            if ( not os.path.isfile( thumbnail ) ):
                thumbnail = ""
        return thumbnail
    except:
        print_exc()
        return ""


def get_nfo_thumbnail( path ):
    try:
        fpath = path
        # make the proper cache filename and path so duplicate caching is unnecessary
        filename = xbmc.getCacheThumbName( fpath )
        thumbnail = os.path.join( BASE_CACHE_PATH, filename[ 0 ], filename )
        # if the cached thumbnail does not exist check for a tbn file
        if ( not os.path.isfile( thumbnail ) ):
            #DIALOG_PROGRESS.update( -1, fpath, thumbnail )
            urllib.urlretrieve( fpath, thumbnail )
        if ( not os.path.isfile( thumbnail ) ):
            thumbnail = ""
        return thumbnail
    except:
        print_exc()
        return ""


def get_browse_dialog( default="", heading="", dlg_type=1, shares="files", mask="", use_thumbs=False, treat_as_folder=False ):
    """ shows a browse dialog and returns a value
        - 0 : ShowAndGetDirectory
        - 1 : ShowAndGetFile
        - 2 : ShowAndGetImage
        - 3 : ShowAndGetWriteableDirectory
    """
    dialog = xbmcgui.Dialog()
    value = dialog.browse( dlg_type, heading, shares, mask, use_thumbs, treat_as_folder, default )
    return value
