"""
   MovieSets Addon Library and manager
   by Frost (passion-xbmc.org)
"""

#Modules General
import os
from sys import argv

# Modules XBMC
import xbmc
from xbmcaddon import Addon

ADDON = Addon( "script.moviesets" )


def IsTrue( text ):
    return ( text == "true" )


def runScript():
    script = None
    args = "".join( argv[ 1:2 ] )

    if "moviesetinfo" in args:
        strListItem = "Container(%s).ListItem" % ADDON.getSetting( "containerId" )
        if IsTrue( xbmc.getInfoLabel( "%s.Property(HasMovieSets)" % strListItem ) ):
            idset = xbmc.getInfoLabel( "%s.Label2" % strListItem )
            xbmc.executebuiltin( "ActivateWindow(busydialog)" )
            from lib import dialogs
            if dialogs.showInfo( idset ):
                xbmc.executebuiltin( "SetProperty(MovieSets.Update,true)" )
        else:
            xbmc.executebuiltin( "Action(Info)" )

    elif not args or "manager" in args:
        xbmc.executebuiltin( "ActivateWindow(busydialog)" )
        script = "moviesets_mgr"

    elif "containerId" in args and not IsTrue( xbmc.getInfoLabel( "Window(VideoLibrary).Property(MovieSets.IsAlive)" ) ):
        script = "moviesets"

    if script:
        xbmc.executebuiltin( "RunScript(%s.py,%s)" % ( os.path.join( os.getcwd(), "lib", script ), args, ) )



if ( __name__ == "__main__" ):
    runScript()
