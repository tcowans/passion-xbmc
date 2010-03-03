"""
Item Module: This module provide constants, functions ... in order to get generic information about an item depending on its type
"""
__all__ = [
    # public names
    "TYPE_ROOT",
    "TYPE_SKIN",
    "TYPE_SCRAPER",
    "TYPE_SCRAPER_MUSIC",
    "TYPE_SCRAPER_VIDEO",
    "TYPE_SCRIPT",
    "TYPE_PLUGIN",
    "TYPE_PLUGIN_MUSIC",
    "TYPE_PLUGIN_PICTURES",
    "TYPE_PLUGIN_PROGRAMS",
    "TYPE_PLUGIN_VIDEO",
    "TYPE_NEW",
    "INDEX_SKIN",
    "INDEX_SCRAPER",
    "INDEX_SCRAPER_MUSIC",
    "INDEX_SCRAPER_VIDEO",
    "INDEX_SCRIPT",
    "INDEX_PLUGIN",
    "INDEX_PLUGIN_MUSIC",
    "INDEX_PLUGIN_PICTURES",
    "INDEX_PLUGIN_PROGRAMS",
    "INDEX_PLUGIN_VIDEO",
    "THUMB_NOT_AVAILABLE",
    "THUMB_SKIN",
    "THUMB_SCRAPER",
    "THUMB_SCRAPER_MUSIC",
    "THUMB_SCRAPER_VIDEO",
    "THUMB_SCRIPT",
    "THUMB_PLUGIN",
    "THUMB_PLUGIN_MUSIC",
    "THUMB_PLUGIN_PICTURES",
    "THUMB_PLUGIN_PROGRAMS",
    "THUMB_PLUGIN_VIDEO",
    "TITLE_ROOT",
    "TITLE_SKIN",
    "TITLE_SCRAPER",
    "TITLE_SCRAPER_MUSIC",
    "TITLE_SCRAPER_VIDEO",
    "TITLE_SCRIPT",
    "TITLE_PLUGIN",
    "TITLE_PLUGIN_MUSIC",
    "TITLE_PLUGIN_PICTURES",
    "TITLE_PLUGIN_PROGRAMS",
    "TITLE_PLUGIN_VIDEO",
    "get_install_path",
    "get_thumb",
    "get_type_title",
    "isSupported",
    ]


# Modules general
import os
import sys

# Modules custom
from specialpath import *

#FONCTION POUR RECUPERER LES LABELS DE LA LANGUE.
_ = sys.modules[ "__main__" ].__language__


##################################################
#            VARIABLES GLOBALES
##################################################

TYPE_ROOT               = "ROOT"
TYPE_SKIN               = "SKIN"
TYPE_SKIN_NIGHTLY       = "SKIN_NIGHTLY"
TYPE_SCRAPER            = "SCRAPER"
TYPE_SCRAPER_MUSIC      = "SCRAPER_MUSIC"
TYPE_SCRAPER_VIDEO      = "SCRAPER_VIDEO"
TYPE_SCRIPT             = "SCRIPT"
TYPE_PLUGIN             = "PLUGIN"
TYPE_PLUGIN_MUSIC       = "PLUGIN_MUSIC"
TYPE_PLUGIN_PICTURES    = "PLUGIN_PICTURES"
TYPE_PLUGIN_PROGRAMS    = "PLUGIN_PROGRAMS"
TYPE_PLUGIN_VIDEO       = "PLUGIN_VIDEO"
TYPE_SCRIPT_CAT         = "SCRIPT_CAT"
TYPE_NEW                = "NEW"

TITLE_ROOT               = _( 10 )
TITLE_SKIN               = _( 11 )
TITLE_SKIN_NIGHTLY       = _( 1101 )
TITLE_SCRAPER            = _( 12 )
TITLE_SCRAPER_MUSIC      = _( 1201 )
TITLE_SCRAPER_VIDEO      = _( 1202 )
TITLE_SCRIPT             = _( 13 )
TITLE_PLUGIN             = _( 14 )
TITLE_PLUGIN_MUSIC       = _( 15 )
TITLE_PLUGIN_PICTURES    = _( 16 )
TITLE_PLUGIN_PROGRAMS    = _( 17 )
TITLE_PLUGIN_VIDEO       = _( 18 )
TITLE_NEW                = _( 22 )

#INDEX_ROOT              = None
INDEX_SKIN              = 0
INDEX_SCRAPER           = 1
INDEX_SCRAPER_MUSIC     = 2
INDEX_SCRAPER_VIDEO     = 3
INDEX_SCRIPT            = 4
INDEX_PLUGIN            = 5
INDEX_PLUGIN_MUSIC      = 6
INDEX_PLUGIN_PICTURES   = 7
INDEX_PLUGIN_PROGRAMS   = 8
INDEX_PLUGIN_VIDEO      = 9
INDEX_SCRIPT_CAT        = 10
INDEX_NEW               = 11
INDEX_SKIN_NIGHTLY      = 12

THUMB_NOT_AVAILABLE     = "IPX-NotAvailable2.png"
THUMB_SKIN              = "IPX-defaultSkin.png"
THUMB_SKIN_NIGHTLY      = "IPX-defaultSkinNightly.png"
THUMB_SCRAPER           = "IPX-defaultScraper.png"
THUMB_SCRAPER_MUSIC     = "IPX-defaultScraperMusic.png"
THUMB_SCRAPER_VIDEO     = "IPX-defaultScraperVideo.png"
THUMB_SCRIPT            = "IPX-defaultScript.png"
THUMB_PLUGIN            = "IPX-defaultPlugin.png"
THUMB_PLUGIN_MUSIC      = "IPX-defaultPluginMusic.png"
THUMB_PLUGIN_PICTURES   = "IPX-defaultPluginPicture.png"
THUMB_PLUGIN_PROGRAMS   = "IPX-defaultPluginProgram.png"
THUMB_PLUGIN_VIDEO      = "IPX-defaultPluginVideo.png"
THUMB_PLUGIN_WEATHER    = "IPX-defaultPluginWeather.png"
THUMB_NEW               = "IPX-defaultNew.png"

INDEX_SRV_ITEM_FORMAT_DIR      = 0
INDEX_SRV_ITEM_FORMAT_FILE_ZIP = 1
INDEX_SRV_ITEM_FORMAT_FILE_RAR = 1
INDEX_SRV_ITEM_FORMAT_INVALID  = 2

supportedAddonList = [ TYPE_SCRAPER, 
                       TYPE_SCRAPER_MUSIC, 
                       TYPE_SCRAPER_VIDEO, 
                       TYPE_SKIN, 
                       TYPE_SKIN_NIGHTLY, 
                       TYPE_SCRIPT,
                       TYPE_PLUGIN,
                       TYPE_PLUGIN_MUSIC,
                       TYPE_PLUGIN_PICTURES,
                       TYPE_PLUGIN_PROGRAMS,
                       TYPE_PLUGIN_VIDEO,
                       TYPE_SCRIPT_CAT,
                       TYPE_NEW ]

item_path = { TYPE_SCRAPER         : DIR_SCRAPER,
              TYPE_SCRAPER_MUSIC   : DIR_SCRAPER_MUSIC, 
              TYPE_SCRAPER_VIDEO   : DIR_SCRAPER_VIDEO, 
              TYPE_SKIN            : DIR_SKIN, 
              TYPE_SKIN_NIGHTLY    : DIR_SKIN, 
              TYPE_SCRIPT          : DIR_SCRIPT, 
              TYPE_PLUGIN          : DIR_PLUGIN, 
              TYPE_PLUGIN_MUSIC    : DIR_PLUGIN_MUSIC, 
              TYPE_PLUGIN_PICTURES : DIR_PLUGIN_PICTURES, 
              TYPE_PLUGIN_PROGRAMS : DIR_PLUGIN_PROGRAMS, 
              TYPE_PLUGIN_VIDEO    : DIR_PLUGIN_VIDEO,
              TYPE_SCRIPT_CAT      : None,
              TYPE_NEW             : None }

item_thumb = { TYPE_SCRAPER         : THUMB_SCRAPER, 
               TYPE_SCRAPER_MUSIC   : THUMB_SCRAPER_MUSIC,
               TYPE_SCRAPER_VIDEO   : THUMB_SCRAPER_VIDEO,
               TYPE_SKIN            : THUMB_SKIN, 
               TYPE_SKIN_NIGHTLY    : THUMB_SKIN_NIGHTLY, 
               TYPE_SCRIPT          : THUMB_SCRIPT, 
               TYPE_PLUGIN          : THUMB_PLUGIN, 
               TYPE_PLUGIN_MUSIC    : THUMB_PLUGIN_MUSIC, 
               TYPE_PLUGIN_PICTURES : THUMB_PLUGIN_PICTURES, 
               TYPE_PLUGIN_PROGRAMS : THUMB_PLUGIN_PROGRAMS, 
               TYPE_PLUGIN_VIDEO    : THUMB_PLUGIN_VIDEO,
               TYPE_SCRIPT_CAT      : THUMB_SCRIPT,
               TYPE_NEW             : THUMB_NEW }

item_title = { TYPE_SCRAPER         : TITLE_SCRAPER, 
               TYPE_SCRAPER_MUSIC   : TITLE_SCRAPER_MUSIC,
               TYPE_SCRAPER_VIDEO   : TITLE_SCRAPER_VIDEO,
               TYPE_SKIN            : TITLE_SKIN, 
               TYPE_SKIN_NIGHTLY    : TITLE_SKIN_NIGHTLY, 
               TYPE_SCRIPT          : TITLE_SCRIPT, 
               TYPE_PLUGIN          : TITLE_PLUGIN, 
               TYPE_PLUGIN_MUSIC    : TITLE_PLUGIN_MUSIC, 
               TYPE_PLUGIN_PICTURES : TITLE_PLUGIN_PICTURES, 
               TYPE_PLUGIN_PROGRAMS : TITLE_PLUGIN_PROGRAMS, 
               TYPE_PLUGIN_VIDEO    : TITLE_PLUGIN_VIDEO,
               TYPE_SCRIPT_CAT      : TITLE_SCRIPT, 
               TYPE_NEW             : TITLE_NEW}

item_index = { TYPE_SCRAPER         : INDEX_SCRAPER, 
               TYPE_SCRAPER_MUSIC   : INDEX_SCRAPER_MUSIC,
               TYPE_SCRAPER_VIDEO   : INDEX_SCRAPER_VIDEO,
               TYPE_SKIN            : INDEX_SKIN, 
               TYPE_SKIN_NIGHTLY    : INDEX_SKIN_NIGHTLY, 
               TYPE_SCRIPT          : INDEX_SCRIPT, 
               TYPE_PLUGIN          : INDEX_PLUGIN, 
               TYPE_PLUGIN_MUSIC    : INDEX_PLUGIN_MUSIC, 
               TYPE_PLUGIN_PICTURES : INDEX_PLUGIN_PICTURES, 
               TYPE_PLUGIN_PROGRAMS : INDEX_PLUGIN_PROGRAMS, 
               TYPE_PLUGIN_VIDEO    : INDEX_PLUGIN_VIDEO,
               TYPE_SCRIPT_CAT      : INDEX_SCRIPT_CAT,
               TYPE_NEW             : INDEX_NEW }

def isSupported( type ):
    """
    Returns if type of this addon is supported by the installer
    """
    if type in supportedAddonList:
        result = True
    else:
        result = False
    return result

def get_install_path( type ):
    """
    Returns the install directory
    """
    try:
        result = item_path[ type ]
    except:
        result = None
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
