"""
Item Module: This module provide constants, functions ... in order to get generic information about an item depending on its type
"""
__all__ = [
    # public names
    "TYPE_RAWITEM_ARCHIVE",
    "TYPE_RAWITEM_DIR",
    "TYPE_ADDON",
    "TYPE_ADDON_SCRIPT",
    "TYPE_ADDON_MUSIC",
    "TYPE_ADDON_PICTURES",
    "TYPE_ADDON_PROGRAMS",
    "TYPE_ADDON_VIDEO",
    "TYPE_ADDON_WEATHER",
    "TYPE_ADDON_MODULE",
    "TYPE_ADDON_PLUGIN",
    "TYPE_ADDON_REPO",
    "TYPE_SYSTEM_FILE",
    "TYPE_SYSTEM_ARCHIVE",
    "TYPE_SYSTEM_DIRECTORY",
    "INDEX_ADDON",
    "INDEX_ADDON_SCRIPT",
    "INDEX_ADDON_MUSIC",
    "INDEX_ADDON_PICTURES",
    "INDEX_ADDON_PROGRAMS",
    "INDEX_ADDON_VIDEO",
    "INDEX_ADDON_WEATHER",
    "INDEX_ADDON_MODULE",
    "THUMB_NOT_AVAILABLE",
    "THUMB_ADDON",
    "THUMB_ADDON_SCRIPT",
    "THUMB_ADDON_MUSIC",
    "THUMB_ADDON_PICTURES",
    "THUMB_ADDON_PROGRAMS",
    "THUMB_ADDON_VIDEO",
    "THUMB_ADDON_WEATHER",
    "THUMB_ADDON_MODULE",
    "TITLE_ADDON",
    "TITLE_ADDON_SCRIPT",
    "TITLE_ADDON_MUSIC",
    "TITLE_ADDON_PICTURES",
    "TITLE_ADDON_PROGRAMS",
    "TITLE_ADDON_VIDEO",
    "TITLE_ADDON_WEATHER",
    "TITLE_ADDON_MODULE",
    "get_install_path",
    "get_thumb",
    "get_type_title"
    ]


# Modules general
import os
import sys

# Modules custom
from specialpath import *

#FONCTION POUR RECUPERER LES LABELS DE LA LANGUE.
_ = sys.modules[ "__main__" ].__language__


##################################################
#                GLOBAL VARS
##################################################

#TYPE_ROOT              = "ROOT"
TYPE_RAWITEM_ARCHIVE    = "ARCHIVE"   # Deprecated
TYPE_RAWITEM_DIR        = "DIRECTORY" # Deprecated

TYPE_ADDON             = "ADDON"
TYPE_ADDON_SCRIPT      = "script" #"ADDON_SCRIPT"
TYPE_ADDON_MUSIC       = "plugin.audio." #"ADDON_MUSIC"
TYPE_ADDON_PICTURES    = "plugin.image." #"ADDON_PICTURES"
TYPE_ADDON_PROGRAMS    = "plugin.program." #"ADDON_PROGRAMS"
TYPE_ADDON_VIDEO       = "plugin.video." #"ADDON_VIDEO"
TYPE_ADDON_WEATHER     = "weather"
TYPE_ADDON_MODULE      = ".module" #"ADDON_SCRIPT"
TYPE_ADDON_PLUGIN      = "pluginsource" 
TYPE_ADDON_REPO        = "repository."

TYPE_SYSTEM_FILE       = "file"
TYPE_SYSTEM_ARCHIVE    = "archive"
TYPE_SYSTEM_DIRECTORY  = "dir"

#TYPE_ADDON_NEW         = "NEW"

#TITLE_ROOT               = _( 10 )
TITLE_ADDON             = _( 30107 )
TITLE_ADDON_SCRIPT      = _( 30101 )
TITLE_ADDON_MUSIC       = _( 30102 )
TITLE_ADDON_PICTURES    = _( 30103 )
TITLE_ADDON_PROGRAMS    = _( 30104 )
TITLE_ADDON_VIDEO       = _( 30105 )
TITLE_ADDON_WEATHER     = _( 30106 )
TITLE_ADDON_MODULE      = _( 30108 )
#TITLE_ADDON_NEW         = _( 22 )

# Note: those indexes are also used in CONF.py careful with any changes
#INDEX_ROOT              = None
INDEX_ADDON            = 0
INDEX_ADDON_SCRIPT     = 1
INDEX_ADDON_MUSIC      = 2
INDEX_ADDON_PICTURES   = 3
INDEX_ADDON_PROGRAMS   = 3
INDEX_ADDON_VIDEO      = 4
INDEX_ADDON_WEATHER    = 5
INDEX_ADDON_MODULE     = 6

THUMB_NOT_AVAILABLE    = os.path.join( DIR_ROOT, "resources", "media", "IPX-NotAvailable2.png")
THUMB_ADDON            = "IPX-defaultPlugin.png"
THUMB_ADDON_SCRIPT     = "IPX-defaultScript.png"
THUMB_ADDON_MUSIC      = "IPX-defaultPluginMusic.png"
THUMB_ADDON_PICTURES   = "IPX-defaultPluginPicture.png"
THUMB_ADDON_PROGRAMS   = "IPX-defaultPluginProgram.png"
THUMB_ADDON_VIDEO      = "IPX-defaultPluginVideo.png"
THUMB_ADDON_WEATHER    = "IPX-defaultPluginWeather.png"
THUMB_ADDON_MODULE     = "IPX-NotAvailable2.png"
THUMB_NEW              = "IPX-defaultNew.png"



item_path = { TYPE_ADDON          : DIR_ADDON,
              TYPE_ADDON_SCRIPT   : DIR_ADDON_SCRIPT, 
              TYPE_ADDON_MUSIC    : DIR_ADDON_MUSIC, 
              TYPE_ADDON_PICTURES : DIR_ADDON_PICTURES, 
              TYPE_ADDON_PROGRAMS : DIR_ADDON_PROGRAMS, 
              TYPE_ADDON_VIDEO    : DIR_ADDON_VIDEO,
              TYPE_ADDON_WEATHER  : DIR_ADDON_WEATHER,
              TYPE_ADDON_MODULE   : DIR_ADDON_MODULE }

item_thumb = { TYPE_ADDON          : THUMB_ADDON,
               TYPE_ADDON_SCRIPT   : THUMB_ADDON_SCRIPT, 
               TYPE_ADDON_MUSIC    : THUMB_ADDON_MUSIC, 
               TYPE_ADDON_PICTURES : THUMB_ADDON_PICTURES, 
               TYPE_ADDON_PROGRAMS : THUMB_ADDON_PROGRAMS, 
               TYPE_ADDON_VIDEO    : THUMB_ADDON_VIDEO,
               TYPE_ADDON_WEATHER  : THUMB_ADDON_WEATHER,
               TYPE_ADDON_MODULE   : THUMB_ADDON_MODULE }

item_title = { TYPE_ADDON          : TITLE_ADDON, 
               TYPE_ADDON_SCRIPT   : TITLE_ADDON_SCRIPT, 
               TYPE_ADDON_MUSIC    : TITLE_ADDON_MUSIC, 
               TYPE_ADDON_PICTURES : TITLE_ADDON_PICTURES, 
               TYPE_ADDON_PROGRAMS : TITLE_ADDON_PROGRAMS, 
               TYPE_ADDON_VIDEO    : TITLE_ADDON_VIDEO,
               TYPE_ADDON_WEATHER  : TITLE_ADDON_WEATHER,
               TYPE_ADDON_MODULE   : TITLE_ADDON_MODULE }

item_index = { TYPE_ADDON          : INDEX_ADDON,
               TYPE_ADDON_SCRIPT   : INDEX_ADDON_SCRIPT, 
               TYPE_ADDON_MUSIC    : INDEX_ADDON_MUSIC, 
               TYPE_ADDON_PICTURES : INDEX_ADDON_PICTURES, 
               TYPE_ADDON_PROGRAMS : INDEX_ADDON_PROGRAMS, 
               TYPE_ADDON_VIDEO    : INDEX_ADDON_VIDEO,
               TYPE_ADDON_WEATHER  : INDEX_ADDON_WEATHER,
               TYPE_ADDON_MODULE   : INDEX_ADDON_MODULE }


def get_install_path( type ):
    """
    Returns the install directory
    """
    print "get_install_path"
    print item_path
    try:
        result = item_path[ type ]
    except:
        result = None
        from traceback import print_exc
        print_exc()
    return result

def get_thumb( type ):
    """
    Returns the thumbs
    """
    try:
        result = item_thumb[ type ]
    except:
        result = THUMB_NOT_AVAILABLE
    return result

def get_type_title( type ):
    """
    Returns a generic title for the type of an item
    """
    try:
        result = item_title[ type ]
    except:
        result = ""
    return result

def get_type_index( type ):
    """
    Returns a index for the type of an item
    """
    try:
        result = item_index[ type ]
    except:
        result = None
    return result

