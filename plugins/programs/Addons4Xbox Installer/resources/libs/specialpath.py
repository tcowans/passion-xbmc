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
    "DIR_ADDON_SKIN",
    "DIR_ADDON_SCRIPT",
    "DIR_ADDON",
    "DIR_ADDON_PLUGIN",
    "DIR_ADDON_MUSIC",
    "DIR_ADDON_PICTURES",
    "DIR_ADDON_PROGRAMS",
    "DIR_ADDON_VIDEO",
    "DIR_ADDON_WEATHER",
    "DIR_ADDON_MODULE",
    "DIR_ROOT",
    "DIR_CACHE"
    ]


# Modules General
import os
import sys

# Modules XBMC
from xbmc import translatePath, getCondVisibility


try: pluginname = sys.modules[ "__main__" ].__plugin__
except: pluginname = os.path.basename( os.getcwd() )

SPECIAL_XBMC_DIR = translatePath( "special://xbmc/" )
if not os.path.isdir( SPECIAL_XBMC_DIR  ): SPECIAL_XBMC_DIR = translatePath( "Q:\\" )

SPECIAL_HOME_DIR = translatePath( "special://home/" )
if not os.path.isdir( SPECIAL_HOME_DIR  ): SPECIAL_HOME_DIR = translatePath( "U:\\" )

SPECIAL_TEMP_DIR = translatePath( "special://temp/" )
if not os.path.isdir( SPECIAL_TEMP_DIR  ): SPECIAL_TEMP_DIR = translatePath( "Z:\\" )

SPECIAL_PROFILE_DIR = translatePath( "special://profile/" )
if not os.path.isdir( SPECIAL_PROFILE_DIR  ): SPECIAL_PROFILE_DIR = translatePath( "P:\\" )

SPECIAL_MASTERPROFILE_DIR = translatePath( "special://masterprofile/" )
if not os.path.isdir( SPECIAL_MASTERPROFILE_DIR  ): SPECIAL_MASTERPROFILE_DIR = translatePath( "T:\\" )

SPECIAL_XBMC_HOME = ( SPECIAL_HOME_DIR, SPECIAL_XBMC_DIR )[ ( os.environ.get( "OS", "xbox" ).lower() == "xbox" ) ]

XBMC_IS_HOME = SPECIAL_HOME_DIR == SPECIAL_XBMC_DIR

SPECIAL_SCRIPT_DATA = os.path.join( SPECIAL_PROFILE_DIR, "plugin_data", "programs", pluginname )
if not os.path.isdir( SPECIAL_SCRIPT_DATA ): os.makedirs( SPECIAL_SCRIPT_DATA )


# Calculate directories needed by the installer
#DIR_XBMC_ROOT       = SPECIAL_XBMC_HOME
DIR_ADDON_SKIN     = os.path.join( SPECIAL_HOME_DIR, "skin" )
DIR_ADDON_SCRIPT   = os.path.join( SPECIAL_HOME_DIR, "scripts" )
DIR_ADDON          = os.path.join( SPECIAL_HOME_DIR, "addons" )
DIR_ADDON_PLUGIN   = os.path.join( SPECIAL_HOME_DIR, "plugins" )
DIR_ADDON_MUSIC    = os.path.join( DIR_ADDON_PLUGIN, "music" )
DIR_ADDON_PICTURES = os.path.join( DIR_ADDON_PLUGIN, "pictures" )
DIR_ADDON_PROGRAMS = os.path.join( DIR_ADDON_PLUGIN, "programs" )
DIR_ADDON_VIDEO    = os.path.join( DIR_ADDON_PLUGIN, "video" )
DIR_ADDON_WEATHER  = os.path.join( DIR_ADDON_PLUGIN, "weather" )
DIR_ADDON_MODULE   = os.path.join( SPECIAL_HOME_DIR, "scripts", ".modules" )


DIR_ROOT            = os.getcwd().replace( ";", "" )
DIR_CACHE           = os.path.join( SPECIAL_SCRIPT_DATA, "cache" )

