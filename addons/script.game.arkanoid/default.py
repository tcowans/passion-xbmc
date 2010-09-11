
__started__  = "26-02-2010"
__statut__   = "Beta3"

#Modules General
import os
import sys

sys.path.append( os.path.join( os.getcwd(), "resources", "libs" ) )

#Modules XBMC
import xbmc
from xbmcaddon import Addon

# Add-on Constants
__addonID__  = "script.game.arkanoid"
__settings__ = Addon( __addonID__ )
__language__ = __settings__.getLocalizedString


if  __name__ == "__main__":
    from home import showMain
    showMain()
