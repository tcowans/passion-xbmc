
import os
import sys
from threading import Thread
from traceback import print_exc

import xbmc
import xbmcgui
from xbmcaddon import Addon

from backend import WeatherWorld


ADDON      = Addon( "script.widget.weatherworld" )
ADDON_DIR  = ADDON.getAddonInfo( "path" )


class ExitMonitor( xbmc.Monitor ):
    def __init__( self, exit_callback, screensaverMode=True ):
        self.exit_callback = exit_callback
        self.screensaverMode = screensaverMode
    
    def onScreensaverDeactivated( self ):
        if self.screensaverMode:
            self.exit_callback()
    
    def onAbortRequested( self ):
        self.exit_callback()


class Screensaver( xbmcgui.WindowXMLDialog ):
    def __init__( self, *args, **kwargs ):
       self.WW = None
       self.doModal()
        
    def onInit( self ):
        wid = xbmcgui.getCurrentWindowDialogId()
        sys.argv.append( "time=%i&limit=7&mapsize=1280x720&tilesize=360x60&window=%i" % ( int( float( ADDON.getSetting( "time" ) ) ), wid ) )
        showcitieslayout = False
        if ADDON.getSetting( "showcities" ) == "true":
            xbmc.executebuiltin( "SetProperty(showcities,1,%i)" % wid )
            showcitieslayout = True
        if ADDON.getSetting( "showcitiesicons" ) == "true":
            xbmc.executebuiltin( "SetProperty(showcitiesicons,1,%i)" % wid )
            showcitieslayout = True
        if showcitieslayout: 
            xbmc.executebuiltin( "SetProperty(showcitieslayout,1,%i)" % wid )

        self.WW = WeatherWorld
        img = os.path.join( ADDON_DIR, "resources", "skins", "default", "media", "radiobutton-focus.png" )
        self.ww_thread = Thread( target=self.WW, kwargs={"pointer":img} )
        self.ww_thread.start()
        self.monitor = ExitMonitor( self.exit )

    def onClick( self, controlID ):
        self.exit()

    def onAction( self, action ):
        self.exit()

    def onFocus( self, controlID ):
        pass

    def exit( self ):
        try: self.ww_thread.join( 0 )
        except: pass#print_exc()
        try: self.WW.stop()
        except: pass
        self.close()


Screensaver( "Screensaver-WeatherWorld.xml", ADDON_DIR )

