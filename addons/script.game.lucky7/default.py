
# script constants
__script__       = "Lucky $even"
__addonID__      = "script.game.lucky7"
__plugin__       = "Unknown"
__author__       = "Frost"
__url__          = "http://passion-xbmc.org/"
__svn_url__      = "http://passion-xbmc.googlecode.com/svn/trunk/addons/script.game.lucky7/"
__credits__      = "Team XBMC, http://xbmc.org/"
__platform__     = "xbmc media center"
__date__         = "10-06-2010"
__version__      = "2.0.0"
__codename__     = "Destiny"
__svn_revision__ = "$Revision$"


#Modules general
from os import getcwd

#modules XBMC
import xbmcaddon

__addon__ = xbmcaddon.Addon( __addonID__ )
#__language__ = xbmc.getLocalizedString
__language__ = __addon__.getLocalizedString

#modules custom
from resources.libs.keymap import Keymap
KEYMAP = Keymap()


if __name__ == "__main__":
    import resources.libs.luckygui as lucky
    lucky.show_game()
