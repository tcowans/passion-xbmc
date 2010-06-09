
from shutil import rmtree
from traceback import print_exc
from os import getcwd, makedirs
from os.path import dirname, exists, join

from xbmcgui import Dialog
from xbmc import translatePath, getLocalizedString
from xbmcaddon import Addon

__addonID__ = "script.game.arkanoid"

CACHE = translatePath( "special://profile/addon_data/%s/" % __addonID__ )

try:
    if exists( CACHE ) and Dialog().yesno( "Arkanoid Cache", getLocalizedString( 122 ) ):
        try: rmtree( CACHE, True )
        except: print_exc()
except: print_exc()

try:
    if not exists( CACHE ): makedirs( CACHE )
except: print_exc()

try: Addon( __addonID__ ).openSettings()
except: print_exc()
