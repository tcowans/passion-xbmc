
# Modules general
import os
import sys
import time

# Modules XBMC
import xbmc
import xbmcgui
import xbmcvfs
from xbmcaddon import Addon

# Modules Custom
from log import logAPI
LOGGER = logAPI()

# constants
ADDON      = Addon( "plugin.moviesets" )
ADDON_NAME = ADDON.getAddonInfo( "name" )
ADDON_DIR  = ADDON.getAddonInfo( "path" )


def notification( header="", message="", sleep=5000, icon=ADDON.getAddonInfo( "icon" ) ):
    """ Will display a notification dialog with the specified header and message,
        in addition you can set the length of time it displays in milliseconds and a icon image.
    """
    icon = ( "DefaultIconInfo.png", icon )[ os.path.isfile( icon ) ]
    xbmc.executebuiltin( "XBMC.Notification(%s,%s,%i,%s)" % ( header, message, sleep, icon ) )


class Viewer:
    # constants
    WINDOW = 10147
    CONTROL_LABEL = 1
    CONTROL_TEXTBOX = 5

    def __init__( self, *args, **kwargs ):
        # activate the text viewer window
        xbmc.executebuiltin( "ActivateWindow(%d)" % ( self.WINDOW, ) )
        # get window
        self.window = xbmcgui.Window( self.WINDOW )
        # give window time to initialize
        xbmc.sleep( 100 )
        # set controls
        self.setControls()

    def setControls( self ):
        #get header, text
        heading, text = self.getText()
        # set heading
        self.window.getControl( self.CONTROL_LABEL ).setLabel( "%s - %s" % ( heading, ADDON_NAME, ) )
        # set text
        self.window.getControl( self.CONTROL_TEXTBOX ).setText( text )

    def getText( self ):
        try:
            if sys.argv[ 1 ] == "changelog":
                return "Changelog", self.readFile( "changelog.txt" )
            elif sys.argv[ 1 ] == "infolabels":
                return "InfoLabels", self.readFile( "README.txt" )
            elif sys.argv[ 1 ] == "license":
                return "License", self.readFile( "LICENSE.txt" )
        except:
            LOGGER.error.print_exc()
        return "", ""

    def readFile( self, filename ):
        try:
            f = xbmcvfs.File( os.path.join( ADDON_DIR, filename ) )
            b = f.read()
            f.close()
            return b
        except:
            return ""


class WebBrowser:
    """ Display url using the default browser. """

    def __init__( self, *args, **kwargs ):
        try:
            url = sys.argv[ 2 ]
            # notify user
            notification( ADDON_NAME, url )
            xbmc.sleep( 100 )
            # launch url
            self.launchUrl( url )
        except:
            LOGGER.error.print_exc()

    def launchUrl( self, url ):
        import webbrowser
        webbrowser.open( url )


def Main():
    try:
        if sys.argv[ 1 ] == "webbrowser":
            WebBrowser()
        else:
            Viewer()
    except:
        LOGGER.error.print_exc()



if ( __name__ == "__main__" ):
    Main()
