"""
    Google Weather
    url: http://passion-xbmc.googlecode.com/svn/trunk/addons/eden-pre/weather.google/
"""

import os
import sys

import xbmc


def compatibility():
    from xbmcaddon import Addon
    Addon = Addon( "weather.google" )
    # get old settings and if exists delete data xml 
    if Addon.getSetting( 'risingsun_city' ) or Addon.getSetting( 'risingsun1_city' ):
        icon = Addon.getAddonInfo( "icon" )
        xml  = Addon.getAddonInfo( 'profile' ) + 'settings.xml'
        del Addon
        import xbmcvfs
        xbmcvfs.delete( xml )
        if not xbmcvfs.exists( xml ):
            #notifie user
            xbmc.executebuiltin( "XBMC.Notification(Weather Google,Your settings have been renewed! Sorry!,10000,%s)" % icon )


if __name__ == "__main__":
    compatibility()
    loc_index = "".join( sys.argv[ 1: ] )
    if loc_index.isdigit():
        xbmc.executebuiltin( "RunScript(%s)" % os.path.join( sys.path[ 0 ], "resources", "lib", "moon_and_earth_phases.py" ) )
        from resources.lib.weather import Main
        Main( loc_index )

    elif loc_index.lower() == "refreshextra":
        #refresh/load extra info (run script timeanddate)
        xbmc.executebuiltin( "CancelAlarm(moon_earth_phases,true)" )
        xbmc.executebuiltin( "RunScript(%s)" % os.path.join( sys.path[ 0 ], "resources", "lib", "timeanddate.py" ) )
        xbmc.executebuiltin( "RunScript(%s)" % os.path.join( sys.path[ 0 ], "resources", "lib", "moon_and_earth_phases.py" ) )

    else:
        # run old script (weather_dharma)
        loc_index = None
