
# plugin constants
__plugin__        = "XBMC XBoxDash Maker"
__author__        = "Frost"
__url__           = "http://code.google.com/p/passion-xbmc/"
__svn_url__       = "http://passion-xbmc.googlecode.com/svn/trunk/plugins/programs/XBMC%20XBoxDash%20Maker"
__credits__       = "Team XBMC, http://xbmc.org/"
__platform__      = "xbmc media center, [XBOX]"
__date__          = "07-08-09"
__version__       = "1.0.1"
__svn_revision__  = "$Revision$"
__XBMC_Revision__ = "19001"


# OUTDATED VERSION: Lite(2006), vDash(2005) and v1(2005)
#__Lite__  = "Scricpt Python Aic4Xbmc_Lite, http://scripts4xbmc.cvs.sourceforge.net/scripts4xbmc/Scripts/Aic4Xbmc_Lite/"
#NB: vDash and v1 uses UnleashX is a full application for XBox
#__vDash__ = "AIC_XBMC_vDash, http://gueux-forum.net/index.php?showtopic=89486"
#__v1__    = "Auto-Install & Clearning XBMC, http://gx-mod.com/xbox/modules/mydownloads/viewcat.php?cid=6"


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
    if ( platform != "xbox" ):
        ok = 0
        xbmc.log( "system::os.environ [%s], This plugin run under XBox only." % ( platform, ), xbmc.LOGERROR )
        if xbmcgui is None:
            import xbmcgui
        xbmcgui.Dialog().ok( __plugin__, "%s: system::os.environ [%s]" % ( xbmc.getLocalizedString( 30904 ), platform, ), xbmc.getLocalizedString( 30905 ) )
    #return result
    return ok


if ( __name__ == "__main__" ):
    plugin = None
    if "showcontextmenu" in sys.argv[ 2 ]:
        from xbmcplugin import endOfDirectory
        endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=False )
        xbmc.executebuiltin( "XBMC.Action(ContextMenu)" )

    elif "action=cachescleaner" in sys.argv[ 2 ]:
        from resources.pluginAPI import plugin_cleaner as plugin

    elif "action=xbmcrealpath" in sys.argv[ 2 ] and ( platform == "xbox" ):
        from resources.pluginAPI import plugin_translate as plugin

    elif "action=testconfig" in sys.argv[ 2 ] and ( platform == "xbox" ):
        from resources.pluginAPI import plugin_test as plugin

    elif "action=svnbuild" in sys.argv[ 2 ] and ( platform == "xbox" ):
        from resources.pluginAPI import plugin_svnbuild as plugin

    elif "build_rar=" in sys.argv[ 2 ] and ( platform == "xbox" ):
        from resources.pluginAPI import updater as plugin

    else:
        from resources.pluginAPI import plugin_main as plugin
        # check for compatibility, only need to check this once, continue if ok
        if ( not sys.argv[ 2 ] ) and ( not _check_compatible() ):
            plugin = None

    if hasattr( plugin, "Main" ):
        plugin.Main()
