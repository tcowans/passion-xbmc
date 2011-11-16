"""
   MovieSets Addon Library and manager
   by Frost (passion-xbmc.org)
"""

#Modules General
import os
from sys import argv
from urllib import quote_plus

# Modules XBMC
import xbmc
from xbmcaddon import Addon

ADDON = Addon( "script.moviesets" )


def IsTrue( text ):
    return ( text == "true" )


def runScript():
    script = None
    args = "".join( argv[ 1:2 ] ).lower()

    if ( "moviesetinfo" in args ):
        script = "dialogs"

    elif ( not args ) or ( "manager" in args ):
        script = "manager" #"moviesets_mgr"

    elif ( "containerid" in args ) and ( not IsTrue( xbmc.getInfoLabel( "Window(VideoLibrary).Property(MovieSets.IsAlive)" ) ) ):
        #if xbmc.getCondVisibility( "SubString(Container.FolderPath,videodb://1) | StringCompare(ListItem.Path,videodb://)" ):
        script = "moviesets"
        #else:
        #    #start later 3 seconds
        #    alarm_name = "MovieSets.Reload"
        #    if xbmc.getCondVisibility( "System.HasAlarm(%s)" % alarm_name ):
        #        xbmc.executebuiltin( "CancelAlarm(%s,true)" % alarm_name )
        #    if xbmc.getCondVisibility( "Window.IsVisible(VideoLibrary)" ):
        #        xbmc.executebuiltin( "AlarmClock(%s,RunScript(%s),0:02,true)" % ( alarm_name, ",".join( argv + [ alarm_name ] ) ) )

    if script:
        if script != "moviesets":
            if not xbmc.getCondVisibility( "System.GetBool(services.webserver)" ):
                message = "Please! Enable XBMC Web Server..."
                header, icon = ADDON.getAddonInfo( "name" ), ADDON.getAddonInfo( "icon" )
                xbmc.executebuiltin( "Notification(%s,%s,6000,%s)" % ( header, message, icon ) )

        command = "RunScript(%s.py,%s)" % ( os.path.join( ADDON.getAddonInfo( "path" ), "lib", script ), args, )

        # cancel last action of moviesets if exists
        alarm_name = "MovieSets." + script
        #print alarm_name + " started"
        if xbmc.getCondVisibility( "System.HasAlarm(%s)" % alarm_name ):
            xbmc.executebuiltin( "CancelAlarm(%s,true)" % alarm_name )
        if script == "moviesets" and argv[ -1 ] != "MovieSets.Reload":
            #wait 1or2 seconds for tvtunes load correctly ;)
            xbmc.executebuiltin( "AlarmClock(%s,%s,0:02,true)" % ( alarm_name, command ) )
        else:
            xbmc.executebuiltin( command )



if ( __name__ == "__main__" ):
    try:
        if not xbmc.getCondVisibility( "Library.HasContent(Movies)" ):
            from xbmcgui import Dialog
            Dialog().ok( "Movie Sets", "You have no movies in your library!", "Update your library, before use this add-on." )
        else:
            runScript()
    except:
        from traceback import print_exc
        print_exc()