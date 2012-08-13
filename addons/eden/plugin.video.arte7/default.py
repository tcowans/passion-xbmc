# -*- coding: utf-8 -*-

import xbmc
import xbmcaddon
import xbmcgui
import xbmcvfs

from traceback import print_exc

# Plugin constants
__script__       = "Unknown"
__plugin__       = "arte7"
__addonID__      = "plugin.video.arte7"
__author__       = "Bezleputh"
__mail__         = "carton_ben@yahoo.fr"
__platform__     = "xbmc media center"
__date__         = "09-07-2012"
__version__      = "0.1.3"
__addon__        = xbmcaddon.Addon( __addonID__ )
__settings__     = __addon__
__language__     = __addon__.getLocalizedString
__addonDir__     = __settings__.getAddonInfo( "path" )

# Module custom
from resources.libs.Arte7Plugin import Arte7Plugin

if ( __name__ == "__main__" ):
    try:
        dbglevel = 3
        dbg = False
        plugin = __plugin__
        settings = __settings__
        Arte7Plugin()
    except Exception,msg:
        xbmc.executebuiltin("XBMC.Notification(%s,%s)"%("ERROR",msg))   
        print ("Error default.py")
        print_exc()


