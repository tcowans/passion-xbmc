
# script constants
__script__       = "Lucky $even"
__plugin__       = "Unknown"
__author__       = "Frost"
__url__          = "http://passion-xbmc.org/index.php"
__svn_url__      = "http://passion-xbmc.googlecode.com/svn/trunk/scripts/Lucky%207/"
__credits__      = "Team XBMC, http://xbmc.org/"
__platform__     = "xbmc media center"
__date__         = "10-03-2009"
__version__      = "pre-2.0.0"
__codename__     = "Destiny"
__svn_revision__ = 0


#Modules general
from os import getcwd

#modules XBMC
from xbmc import Language
__language__ = Language( getcwd().replace( ";", "" ) ).getLocalizedString

#modules custom
from resources.libs.keymap import Keymap
KEYMAP = Keymap()


if __name__ == "__main__":
    import resources.libs.luckygui as lucky
    lucky.show_game()
