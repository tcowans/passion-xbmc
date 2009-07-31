
# plugin constants
__plugin__       = "Passion-XBMC NFO Creator"
__author__       = "Frost"
__url__          = "http://code.google.com/p/passion-xbmc/"
__svn_url__      = "http://passion-xbmc.googlecode.com/svn/trunk/plugins/video/"
__credits__      = "Team XBMC, http://xbmc.org/"
__platform__     = "xbmc media center, [LINUX, OS X, WIN32, XBOX]"
__date__         = "31-07-2009"
__version__      = "1.0.2a"
__svn_revision__  = "$Revision$"
__XBMC_Revision__ = "20000" #XBMC Babylon


#Modules general
import sys
from os import environ

#Module XBMC
import xbmc


# get xbmc run under?
platform = environ.get( "OS", "xbox" )


def _check_compatible():
    xbmcgui = None
    try:
        # spam plugin statistics to log
        xbmc.log( "[PLUGIN] '%s: Version - %s-r%s' initialized!" % ( __plugin__, __version__, __svn_revision__.replace( "$", "" ).replace( "Revision", "" ).strip( ": " ) ), xbmc.LOGNOTICE )
        # get xbmc revision
        xbmc_version = xbmc.getInfoLabel( "System.BuildVersion" )
        xbmc_rev = int( xbmc_version.split( " " )[ 1 ].replace( "r", "" ) )
        # compatible?
        ok = xbmc_rev >= int( __XBMC_Revision__ )
    except:
        # error, so unknown, allow to run
        xbmc_rev = 0
        ok = 2
    # spam revision info
    xbmc.log( "     ** Required XBMC Revision: r%s **" % ( __XBMC_Revision__, ), xbmc.LOGNOTICE )
    xbmc.log( "     ** Found XBMC Revision: r%d [%s] **" % ( xbmc_rev, ( "Not Compatible", "Compatible", "Unknown", )[ ok ], ), xbmc.LOGNOTICE )
    # if not compatible, inform user
    if ( not ok ):
        import xbmcgui
        xbmcgui.Dialog().ok( "%s - %s: %s" % ( __plugin__, xbmc.getLocalizedString( 30900 ), __version__, ), xbmc.getLocalizedString( 30901 ) % ( __plugin__, ), xbmc.getLocalizedString( 30902 ) % ( __XBMC_Revision__, ), xbmc.getLocalizedString( 30903 ) )
    #if not xbmc run under xbox, inform user
    if ( platform.upper() not in __platform__ ):
        ok = 0
        xbmc.log( "system::os.environ [%s], This plugin run under %s only." % ( platform, __platform__, ), xbmc.LOGERROR )
        if xbmcgui is None:
            import xbmcgui
        xbmcgui.Dialog().ok( __plugin__, "%s: system::os.environ [[COLOR=ffe2ff43]%s[/COLOR]]" % ( xbmc.getLocalizedString( 30904 ), platform, ), xbmc.getLocalizedString( 30905 ) % __platform__ )
    #return result
    return ok


if __name__ == "__main__":
    plugin = None
    if ( not sys.argv[ 2 ] ):
        if _check_compatible():
            import resources.pluginAPI.plugin_main as plugin

    elif ( "isFolder=0" in sys.argv[ 2 ] ):
        import resources.pluginAPI.plugin_select as plugin

    elif ( "show_id=" in sys.argv[ 2 ] ):
        import resources.pluginAPI.plugin_show_nfo as plugin

    elif ( "nfo_file=" in sys.argv[ 2 ] ):
        import resources.pluginAPI.plugin_install_nfo as plugin

    elif ( "trailers=" in sys.argv[ 2 ] ):
        import resources.pluginAPI.plugin_trailers as plugin

    if hasattr( plugin, "Main" ):
        plugin.Main()
