
# Script Constants
__script__        = "Arkanoid"
__scriptID__      = "script.game.arkanoid"
__author__        = "Frost"
__url__           = "http://passion-xbmc.org/"
__svn_url__       = "http://passion-xbmc.googlecode.com/svn/trunk/addons/script.game.arkanoid/"
__credits__       = "Team XBMC, http://xbmc.org/"
__platform__      = "xbmc media center, [ALL]"
__started__       = "26-02-2010"
__date__          = "26-05-2010"
__version__       = "pre-1.0.0"
__statut__        = "Beta1"
__svn_revision__  = "$Revision$".replace( "Revision", "" ).strip( "$: " )
__XBMC_Revision__ = "29000"


#Modules General
import os
import sys

import xbmc


try:
    from re import search
    xbmc_rev = search( '.*?r(\\d+)', xbmc.getInfoLabel( "System.BuildVersion" ) ).group( 1 )
    OK = eval( "%s>=%s" % ( xbmc_rev, __XBMC_Revision__ ) )
except:
    OK = False
    import traceback; traceback.print_exc()

def settings():
    if OK: SETTINGS = xbmc.Settings( __scriptID__ )
    else: SETTINGS = xbmc.Settings( os.getcwd() )
    return SETTINGS


sys.path.append( os.path.join( os.getcwd(), "resources", "libs" ) )


if  __name__ == "__main__":
    from home import showMain
    showMain()
