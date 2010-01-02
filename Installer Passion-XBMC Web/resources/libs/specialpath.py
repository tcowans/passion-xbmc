# If the dir exists with the requested name, simply return it

__all__ = [
    # public names
    "XBMC_IS_HOME",
    "SPECIAL_XBMC_DIR",
    "SPECIAL_HOME_DIR",
    "SPECIAL_TEMP_DIR",
    "SPECIAL_PROFILE_DIR",
    "SPECIAL_MASTERPROFILE_DIR",
    "SPECIAL_XBMC_HOME",
    "SPECIAL_SCRIPT_DATA",
    "DIR_XBMC_ROOT",
    "DIR_SCRAPER",
    "DIR_SKIN",
    "DIR_SCRIPT",
    "DIR_PLUGIN",
    "DIR_PLUGIN_MUSIC",
    "DIR_PLUGIN_PICTURES",
    "DIR_PLUGIN_PROGRAMS",
    "DIR_PLUGIN_VIDEO",
    "DIR_ROOT",
    "DIR_CACHE"
    ]


# Modules General
import os
import sys

# Modules XBMC
from xbmc import translatePath, getCondVisibility


try: scriptname = sys.modules[ "__main__" ].__script__
except: scriptname = os.path.basename( os.getcwd() )

SPECIAL_XBMC_DIR = translatePath( "special://xbmc/" )
#if PLATFORM_MAC or not os.path.isdir( SPECIAL_XBMC_DIR  ): SPECIAL_XBMC_DIR = translatePath( "Q:\\" )
if not os.path.isdir( SPECIAL_XBMC_DIR  ): SPECIAL_XBMC_DIR = translatePath( "Q:\\" )

SPECIAL_HOME_DIR = translatePath( "special://home/" )
#if PLATFORM_MAC or not os.path.isdir( SPECIAL_HOME_DIR  ): SPECIAL_HOME_DIR = translatePath( "U:\\" )
if not os.path.isdir( SPECIAL_HOME_DIR  ): SPECIAL_HOME_DIR = translatePath( "U:\\" )

SPECIAL_TEMP_DIR = translatePath( "special://temp/" )
#if PLATFORM_MAC or not os.path.isdir( SPECIAL_TEMP_DIR  ): SPECIAL_TEMP_DIR = translatePath( "Z:\\" )
if not os.path.isdir( SPECIAL_TEMP_DIR  ): SPECIAL_TEMP_DIR = translatePath( "Z:\\" )

SPECIAL_PROFILE_DIR = translatePath( "special://profile/" )
#if PLATFORM_MAC or not os.path.isdir( SPECIAL_PROFILE_DIR  ): SPECIAL_PROFILE_DIR = translatePath( "P:\\" )
if not os.path.isdir( SPECIAL_PROFILE_DIR  ): SPECIAL_PROFILE_DIR = translatePath( "P:\\" )

SPECIAL_MASTERPROFILE_DIR = translatePath( "special://masterprofile/" )
#if PLATFORM_MAC or not os.path.isdir( SPECIAL_MASTERPROFILE_DIR  ): SPECIAL_MASTERPROFILE_DIR = translatePath( "T:\\" )
if not os.path.isdir( SPECIAL_MASTERPROFILE_DIR  ): SPECIAL_MASTERPROFILE_DIR = translatePath( "T:\\" )

SPECIAL_XBMC_HOME = ( SPECIAL_HOME_DIR, SPECIAL_XBMC_DIR )[ ( os.environ.get( "OS", "xbox" ).lower() == "xbox" ) ]

XBMC_IS_HOME = SPECIAL_HOME_DIR == SPECIAL_XBMC_DIR

SPECIAL_SCRIPT_DATA = os.path.join( SPECIAL_PROFILE_DIR, "script_data", scriptname )
if not os.path.isdir( SPECIAL_SCRIPT_DATA ): os.makedirs( SPECIAL_SCRIPT_DATA )


def get_system_platform():
    """ fonction: pour recuperer la platform que xbmc tourne """
    platform = "unknown"
    if getCondVisibility( "system.platform.linux" ):
        platform = "linux"
    elif getCondVisibility( "system.platform.xbox" ):
        platform = "xbox"
    elif getCondVisibility( "system.platform.windows" ):
        platform = "windows"
    elif getCondVisibility( "system.platform.osx" ):
        platform = "osx"
    return platform


SYSTEM_PLATFORM = get_system_platform()


# Calculate directories needed by the installer
DIR_XBMC_ROOT = SPECIAL_XBMC_HOME
DIR_SKIN            = os.path.join( DIR_XBMC_ROOT, "skin" )
DIR_SCRIPT          = os.path.join( DIR_XBMC_ROOT, "scripts" )
DIR_PLUGIN          = os.path.join( DIR_XBMC_ROOT, "plugins" )
DIR_PLUGIN_MUSIC    = os.path.join( DIR_PLUGIN, "music" )
DIR_PLUGIN_PICTURES = os.path.join( DIR_PLUGIN, "pictures" )
DIR_PLUGIN_PROGRAMS = os.path.join( DIR_PLUGIN, "programs" )
DIR_PLUGIN_VIDEO    = os.path.join( DIR_PLUGIN, "video" )

DIR_ROOT            = os.getcwd().replace( ";", "" )
DIR_CACHE           = os.path.join( DIR_ROOT, "cache" )

if SYSTEM_PLATFORM == "linux":
    #Set Linux dir
    DIR_SCRAPER         = os.path.join( os.sep+"usr", "share", "xbmc", "system", "scrapers", "video" )
elif SYSTEM_PLATFORM == "osx":
    #Set OSX dir
    DIR_SCRAPER = os.path.join( SPECIAL_XBMC_HOME, "system", "scrapers", "video" )
else:
    #Set Win ScraperDir
    DIR_SCRAPER = os.path.join( DIR_XBMC_ROOT, "system", "scrapers", "video" )

