# -*- coding: utf-8 -*-

import xbmc
import xbmcaddon
import xbmcgui
import xbmcvfs

import CommonFunctions
from traceback import print_exc


# Plugin constants
__script__       = "Unknown"
__plugin__       = "arte7"
__addonID__      = "plugin.video.arte7"
__author__       = "Bezleputh, Temhil"
__platform__     = "xbmc media center"
__date__         = "13-12-2011"
__version__      = "0.0.2"
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
        common = CommonFunctions.CommonFunctions()  
        Arte7Plugin()
    except Exception,msg:
        xbmc.executebuiltin("XBMC.Notification(%s,%s)"%("ERROR",msg))   
        print ("Error default.py")
        print_exc()


