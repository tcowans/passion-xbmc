
#Modules general
import os
import re
import sys
from traceback import print_exc

#Modules XBMC
import xbmc
import xbmcgui
import xbmcplugin


def samelauncher( type_of_shortcut, dash_path, launch_path ):
    try:
        txt = file( dash_path, "rb" ).read()
        if ( type_of_shortcut == "XBMC" ) and ( "INFO - launching cutfile:" in txt and "INFO - openening cutfile:" in txt ):
            cut_path = file( dash_path.replace( ".xbe", ".cfg" ), "r" ).read()
            #print "current path (" + cut_path + ") in cfg\n"
            return ( os.path.normcase( os.path.abspath( launch_path ) ) == os.path.normcase( os.path.abspath( cut_path ) ) )
        else:
            cut = re.compile( '([a-z]:\\\\(?:[-\\w\\.\\d]+\\\\)*(?:[-\\w\\.\\d]+)?).xbe' ).search( txt )
            if cut:
                cut_path = cut.group()
                #print "current path (" + cut_path + " in xbe)\n"
                return ( os.path.normcase( os.path.abspath( launch_path ) ) == os.path.normcase( os.path.abspath( cut_path ) ) )
    except:
        print_exc()


def Main( popup=True ):
    type_of_shortcut = int( xbmcplugin.getSetting( "type_of_shortcut" ) )
    uix_shortcut = "E:\Apps\XBMC\default.xbe|F:\Apps\XBMC\default.xbe|G:\Apps\XBMC\default.xbe|E:\Logiciels\XBMC\default.xbe|F:\Logiciels\XBMC\default.xbe|G:\Logiciels\XBMC\default.xbe".split( "|" )[ int( xbmcplugin.getSetting( "uix_shortcut" ) ) ]
    apps_path = xbmcplugin.getSetting( "apps_path" )

    dash_path = xbmcplugin.getSetting( "dash_path" )
    use_tbn = ( xbmcplugin.getSetting( "use_tbn" ) == "true" )
    tbn_path = xbmcplugin.getSetting( "tbn_path" )

    ok = False
    apps_ok = False
    dash_ok = False

    try:
        # check apps file if exsits
        apps_path = ( apps_path, uix_shortcut, )[ type_of_shortcut ]
        if apps_path == "Q:\\default.xbe":
            # translate path
            try:
                from utilities import GET_XBMC_IS_MAPPED_TO
                if GET_XBMC_IS_MAPPED_TO: apps_path = GET_XBMC_IS_MAPPED_TO
            except:
                print_exc()
        apps_ok = ( apps_path != "Q:\\default.xbe" ) and os.path.isfile( apps_path ) and os.path.exists( apps_path )
        # check dashbord xbe if exsits
        dash_ok = os.path.isfile( dash_path ) and os.path.exists( dash_path )
        ok = ( apps_ok and dash_ok )
    except:
        print_exc()
        ok = False

    base_path = os.path.join( os.getcwd().rstrip( ";" ), "resources", "ShortcutXBE" )
    if type_of_shortcut == 1:
        cut_path = os.path.join( base_path, "TeamUIX", apps_path.replace( ":" , "" ) )
    elif type_of_shortcut == 0:
        cut_path = os.path.join( base_path, "TeamXBMC", "TEAM XBMC.xbe" )
    else:
        cut_path = os.path.join( base_path, "oops.err" )
    cut_infos = ""
    if not ( os.path.isfile( cut_path ) and os.path.exists( cut_path ) ):
        cut_infos = xbmc.getLocalizedString( 30610 )
        ok = False

    if ok:
        if samelauncher( ( "XBMC", "UIX", )[ type_of_shortcut ], dash_path, apps_path ):
            if popup:
                xbmcgui.Dialog().ok( xbmc.getLocalizedString( 30600 ),
                    xbmc.getLocalizedString( 30601 ),
                    xbmc.getLocalizedString( 30602 ) % ( dash_path, ),
                    xbmc.getLocalizedString( 30603 ) % ( apps_path, ) )
            return 1
        else:
            if popup:
                xbmcgui.Dialog().ok( xbmc.getLocalizedString( 30604 ),
                    xbmc.getLocalizedString( 30605 ) % ( ( "XBMC", "UIX", )[ type_of_shortcut ], ),
                    xbmc.getLocalizedString( 30602 ) % ( dash_path, ),
                    xbmc.getLocalizedString( 30606 ) % ( apps_path, ) )
            return ( "XBMC", "UIX", )[ type_of_shortcut ], apps_path, dash_path
    else:
        if popup:
            xbmcgui.Dialog().ok( xbmc.getLocalizedString( 30607 ),
                "%s%s" % ( xbmc.getLocalizedString( 30605 ) % ( "XBMC", "UIX", )[ type_of_shortcut ], cut_infos, ),
                xbmc.getLocalizedString( 30608 ) % ( ( xbmc.getLocalizedString( 30611 ), "", )[ dash_ok ], dash_path, ),
                xbmc.getLocalizedString( 30609 ) % ( ( xbmc.getLocalizedString( 30611 ), "", )[ apps_ok ], apps_path, ) )
        return 0
