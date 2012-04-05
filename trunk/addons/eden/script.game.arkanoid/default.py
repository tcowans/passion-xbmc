
__started__  = "26-02-2010"

#Modules General
import os
import sys

#sys.path.append( os.path.join( os.getcwd(), "resources", "libs" ) )
sys.path.append( os.path.join( sys.path[ 0 ], "resources", "libs" ) )

#Modules XBMC
import xbmc
from xbmcaddon import Addon

# Add-on Constants
__addonID__  = "script.game.arkanoid"
__settings__ = Addon( __addonID__ )
__language__ = __settings__.getLocalizedString
AddonPath    = __settings__.getAddonInfo( "path" )

if  __name__ == "__main__":
    from home import showMain
    showMain()
