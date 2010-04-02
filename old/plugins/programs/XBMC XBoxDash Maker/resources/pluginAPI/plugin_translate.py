
#Module General
import sys

#Modules XBMC
import xbmc
import xbmcgui
import xbmcplugin


def Main():
    ok = 0
    try:
        if xbmcplugin.getSetting( "apps_path" ) == "Q:\\default.xbe":
            # translate path
            from utilities import GET_XBMC_IS_MAPPED_TO
            if GET_XBMC_IS_MAPPED_TO: 
                xbmcplugin.setSetting( "apps_path", GET_XBMC_IS_MAPPED_TO )
                xbmc.log( "[%s]: %s" % ( sys.modules["__main__"].__plugin__, "Translate XBMC Home Path", ), xbmc.LOGDEBUG )
                xbmc.log( "Home Path: Q:\\default.xbe to Real Path: %s" % ( GET_XBMC_IS_MAPPED_TO, ), xbmc.LOGDEBUG )
                ok = 1
    except:
        from traceback import print_exc
        print_exc()

    xbmcgui.Dialog().ok( xbmc.getLocalizedString( 30700 ), xbmc.getLocalizedString( 30701 ), xbmc.getLocalizedString( 30702 ) % ( ( "?", xbmcplugin.getSetting( "apps_path" ), )[ ok ], ) )
    xbmcplugin.openSettings( sys.argv[ 0 ] )
