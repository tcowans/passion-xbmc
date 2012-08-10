"""
   MovieSets Addon Library and manager
   by Frost (passion-xbmc.org)
"""

#Modules General
import os
import sys

# Modules XBMC
import xbmc
from xbmcgui import Dialog
from xbmcaddon import Addon

ADDON = Addon( "script.moviesets" )

# log infos system
PREFIX = "[MovieSets-%s] " % ADDON.getAddonInfo( 'version' )
xbmc.log( PREFIX + "XBMC (%s), Built on %s" % ( xbmc.getInfoImage( 'System.BuildVersion' ), xbmc.getInfoImage( 'System.BuildDate' ) ) )
xbmc.log( PREFIX + "Python %s on %s" % ( sys.version, sys.platform ) )


def IsTrue( text ):
    return ( text.lower() == "true" )


def runScript():
    script = None
    args = "".join( sys.argv[ 1:2 ] ).lower()

    if ( "moviesetinfo" in args ):
        script = "dialogs"

    elif ( not args ) or ( "manager" in args ):
        #script = "manager" #"moviesets_mgr"
        Dialog().ok( "Manager Broken", "The manager is broken, due to API change!", "Sorry!" )
        return

    elif ( "containerid" in args ) and ( not IsTrue( xbmc.getInfoLabel( "Window(VideoLibrary).Property(MovieSets.IsAlive)" ) ) ):
        script = "moviesets"

    if script:
        if script != "moviesets":
            if not xbmc.getCondVisibility( "System.GetBool(services.webserver)" ):
                message = "Please! Enable XBMC Web Server..."
                header, icon = ADDON.getAddonInfo( "name" ), ADDON.getAddonInfo( "icon" )
                xbmc.executebuiltin( "Notification(%s,%s,6000,%s)" % ( header, message, icon ) )
                xbmc.executebuiltin( "ActivateWindow(networksettings)" )
                xbmc.executebuiltin( "SetFocus(-101)" )
                xbmc.executebuiltin( "SetFocus(-75)" )
                xbmc.executebuiltin( "Action(Select)" )
                return

        command = "RunScript(%s.py,%s)" % ( os.path.join( ADDON.getAddonInfo( "path" ), "lib", script ), args, )

        # cancel last action of moviesets if exists
        #alarm_name = "MovieSets." + script
        #print alarm_name + " started"
        #if xbmc.getCondVisibility( "System.HasAlarm(%s)" % alarm_name ):
        #    xbmc.executebuiltin( "CancelAlarm(%s,true)" % alarm_name )
        #if script == "moviesets" and str( sys.argv[ -1 ] ).lower() != "moviesets.reload":
        #    #wait 1or2 seconds for tvtunes load correctly ;)
        #    xbmc.executebuiltin( "AlarmClock(%s,%s,0:00,true)" % ( alarm_name, command ) )
        #else:
        xbmc.executebuiltin( command )



if ( __name__ == "__main__" ):
    try:
        if not xbmc.getCondVisibility( "Library.HasContent(Movies)" ):
            Dialog().ok( "Movie Sets", "You have no movies in your library!", "Update your library, before use this add-on." )
        else:
            runScript()
    except:
        from traceback import print_exc
        print_exc()
