
# plugin constants
__plugin__       = "Xbmc Passion - Nfo creator"
__script__       = "Unknown"
__author__       = "Frost"
__url__          = "http://code.google.com/p/passion-xbmc/"
__svn_url__      = "http://passion-xbmc.googlecode.com/svn/trunk/plugins/video/"
__credits__      = "Team XBMC, http://xbmc.org/"
__platform__     = "xbmc media center"
__date__         = "07-01-2009"
__version__      = "0.1.2"
__svn_revision__ = 0


#Modules general
import sys


if __name__ == "__main__":
    if ( "show_nfo=" in sys.argv[ 2 ] ):
        import resources.pluginAPI.plugin_show_nfo as plugin
    else:
        import resources.pluginAPI.plugin_main as plugin
    plugin.Main()
