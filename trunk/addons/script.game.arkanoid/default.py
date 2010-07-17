
# Add-on Constants
__script__        = "Arkanoid"
__addonID__       = "script.game.arkanoid"
__author__        = "Frost"
__url__           = "http://passion-xbmc.org/"
__svn_url__       = "http://passion-xbmc.googlecode.com/svn/trunk/addons/script.game.arkanoid/"
__credits__       = "Team XBMC, http://xbmc.org/"
__platform__      = "xbmc media center, [ALL]"
__started__       = "26-02-2010"
__date__          = "17-07-2010"
__version__       = "1.0.1"
__statut__        = "Beta3"
__svn_revision__  = "$Revision$".replace( "Revision", "" ).strip( "$: " )


#Modules General
import os
import sys

sys.path.append( os.path.join( os.getcwd(), "resources", "libs" ) )

#Modules XBMC
import xbmc
import xbmcaddon

__addon__ = xbmcaddon.Addon( __addonID__ )
__settings__ = __addon__
__language__ = __addon__.getLocalizedString


if  __name__ == "__main__":
    from home import showMain
    showMain()
