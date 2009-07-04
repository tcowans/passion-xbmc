
import os
from sys import argv
from xbmc import translatePath

# plugin constants
__plugin__       = "All Game"
__script__       = "Unknown"
__author__       = "FrostBox"
__url__          = "http://code.google.com/p/passion-xbmc/"
__svn_url__      = "http://code.google.com/p/passion-xbmc/source/browse/#svn/trunk/plugins/video/All%20Game/"
__credits__      = "Team XBMC, http://xbmc.org/"
__platform__     = "xbmc media center"
__date__         = "19-11-2008"
__version__      = "0.9.2"
__svn_revision__ = 0


PLUGIN_RUN_UNDER = os.environ.get( "OS", "" ).lower() #"""( "xbox", "win32", "linux", "osx" )"""

API_PATH = translatePath( os.path.join( os.getcwd().rstrip( ";" ), "resources", "pluginAPI" ) )


def set_directories_data():
    from xbmcplugin import getSetting
    if getSetting( "data_path" ) == "0": DIRECTORY_DATA = os.path.join( "T:\\plugin_data", "video", __plugin__ )
    else: DIRECTORY_DATA = getSetting( "custom_path" )
    BOOSTER = getSetting( "plugin_booster" ) == "true"
    del getSetting
    DIRECTORY_DATA = translatePath( DIRECTORY_DATA )
    GAMES_DIR_PATH = os.path.join( DIRECTORY_DATA, "games" )
    PLATFORMS_DIR_PATH = os.path.join( DIRECTORY_DATA, "platforms" )
    THUMBNAILS_DIR_PATH = os.path.join( DIRECTORY_DATA, "thumbnails" )
    TRAILERS_DIR_PATH = os.path.join( DIRECTORY_DATA, "trailers" )
    if not os.path.isdir( GAMES_DIR_PATH ): os.makedirs( GAMES_DIR_PATH )
    if not os.path.isdir( PLATFORMS_DIR_PATH ): os.makedirs( PLATFORMS_DIR_PATH )
    if not os.path.isdir( THUMBNAILS_DIR_PATH ): os.makedirs( THUMBNAILS_DIR_PATH )
    if not os.path.isdir( TRAILERS_DIR_PATH ): os.makedirs( TRAILERS_DIR_PATH )
    globals().update( locals() )

set_directories_data()


def run_plugin():
    try:
        ARGS = [ arg.replace( "=/", "=" ).split( "=", 1 )[ :2 ] for arg in argv[ 2 ][ 1: ].split( "&&" ) ]
        ARGS = dict( ARGS )
    except:
        ARGS = dict()

    plugin = None
    PLUGIN_API = ARGS.get( "pluginAPI" )

    if PLUGIN_API == "Game Info":
        from resources.pluginAPI import dialog_game_info as plugin
        plugin.Main( ARGS.get( "game_id" ), ARGS.get( "platform" ) )
        plugin = None

    elif PLUGIN_API == "Games":
        from resources.pluginAPI import plugin_games as plugin

    elif PLUGIN_API == "Releases":
        from resources.pluginAPI import plugin_releases as plugin

    elif PLUGIN_API == "All Platforms":
        from resources.pluginAPI import plugin_platforms as plugin

    elif PLUGIN_API == "Search":
        from resources.pluginAPI import plugin_search as plugin

    elif not PLUGIN_API:
        from resources.pluginAPI import plugin_categories as plugin

    if plugin:
        plugin.Main()


if __name__ == "__main__":
    if BOOSTER:
        """Psyco -- the Python Specializing Compiler.
        Typical usage: add the following lines to your application's main module,
        preferably after the other imports:
        """
        try:
            import psyco
            psyco.full()
        except ImportError:
            from resources.pluginAPI.plugin_log import *
            LOG( LOG_ERROR, "ImportError: Psyco not installed, our program will just run slower :(" )
        except:
            from sys import exc_info
            from resources.pluginAPI.plugin_log import *
            EXC_INFO( LOG_ERROR, exc_info() )

    run_plugin()
