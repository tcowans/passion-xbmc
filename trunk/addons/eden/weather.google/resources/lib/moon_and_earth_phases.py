
import os
import glob
import random
import urllib
from traceback import print_exc

HTTP_USER_AGENT = random.choice( [ "Mozilla/5.0 (Windows NT 5.1; rv:10.0) Gecko/20100101 Firefox/10.0",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.77 Safari/535.7",
    "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; .NET4.0C; .NET4.0E; .NET CLR 2.0.50727; .NET CLR 3.0.04506.648; .NET CLR 3.5.21022; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729)"
    ] )

class _urlopener( urllib.FancyURLopener ):
    version = os.environ.get( "HTTP_USER_AGENT" ) or HTTP_USER_AGENT
urllib._urlopener = _urlopener()


try:
    import xbmc, xbmcgui, xbmcvfs
    from xbmcaddon import Addon
    Addon = Addon( "weather.google" )
    WEATHER_WINDOW = xbmcgui.Window( 12600 )
    REFRESH = not xbmc.getCondVisibility( "System.HasAlarm(moon_earth_phases)" )
    cache_dir = xbmc.translatePath( Addon.getAddonInfo( 'profile' ) )
    if not os.path.exists( cache_dir ): os.makedirs( cache_dir )
    PHASE_IMAGE = os.path.join( cache_dir, "%s.png" )
except:
    # NOT RUNNING ON XBMC, ON DEV
    WEATHER_WINDOW = None
    REFRESH = True
    PHASE_IMAGE = "%s.png"


try: import sqlite3
except: sqlite3 = None

def deleteTexture( sourceurl ):
    OK = False
    #print "-"*100
    #try:
    #    c_filename   = xbmc.getCacheThumbName( sourceurl )
    #    cachedurl    = "%s/%s.png" % ( c_filename[ 0 ], c_filename.replace( ".tbn", "" ) )
    #    cached_tbumb = "special://profile/Thumbnails/" + cachedurl
    #    xbmcvfs.delete( cached_tbumb )
    #    #OK = xbmcvfs.copy( sourceurl, cached_tbumb )
    #    #print "I just deleted %r thumbs" % OK
    #except:
    #    cachedurl = None
    if sqlite3:
        for db in glob.glob( xbmc.translatePath( "special://Database/Textures*.db" ) ):
            conn = None
            try:
                # connect to textures database
                conn = sqlite3.connect( db )
                c_url = conn.execute( 'SELECT cachedurl FROM texture WHERE url=?', ( sourceurl, ) ).fetchone()
                if c_url:
                    cachedurl = c_url[ 0 ]
                    cached_tbumb = "special://profile/Thumbnails/" + cachedurl
                    xbmcvfs.delete( cached_tbumb )
                    #
                    row_count = conn.execute( 'DELETE FROM texture WHERE cachedurl=?', ( cachedurl, ) ).rowcount
                    #print ( cachedurl, sourceurl )
                    #print "I just deleted %r rows in %s" % ( row_count, os.path.basename( db ) )
                    conn.commit()
                    OK = True
            except:
                print_exc()
            if hasattr( conn, "close" ):
                # close database
                conn.close()
    return OK


def SetProperty( key, value="" ):
    if WEATHER_WINDOW:
        WEATHER_WINDOW.setProperty( key, value )
    else:
        # for test print
        print key, value


def get_moon_earth_phases():
    properties = [
        ( "Current.Moon.Phase.Image", "moon.png" ),
        ( "Current.Earth.Phase.Image", "earth.png?view=rise" ),
        ( "Current.Earth.Phase.LargeImage", "earth.png" )
        ]
    OK = False
    try:
        for property, img in properties:
            SetProperty( property )
            url = "http://api.usno.navy.mil/imagery/" + img
            dst = PHASE_IMAGE % property.replace( ".", "" )
            try: dst, h = urllib.urlretrieve( url, dst )
            except:
                try: dst, h = urllib.urlretrieve( url, dst )
                except: dst, h = url, ""
            if dst != url:
                if os.path.getsize( dst ):
                    OK = deleteTexture( dst )
                else:
                    dst, OK = url, False
            SetProperty( property, dst )
        OK = True
    except:
        print_exc()
        OK = False
    return OK

    
def start_alarm():
    if not WEATHER_WINDOW:
        return
    try:
        # start next time to refresh images. 60 minutes (skinner for force refresh use "CancelAlarm(moon_earth_phases,true)")
        command = "RunScript(%s)" % os.path.join( Addon.getAddonInfo( "path" ), "resources", "lib", "moon_and_earth_phases.py" )
        xbmc.executebuiltin( "AlarmClock(moon_earth_phases,%s,60,true)" % command )
    except:
        print_exc()

        
def cancel_alarm():
    if not WEATHER_WINDOW:
        return
    try:
        if xbmc.getCondVisibility( "System.HasAlarm(moon_earth_phases)" ):
            xbmc.executebuiltin( "CancelAlarm(moon_earth_phases,true)" )
    except:
        print_exc()

        
        
if REFRESH:
    if get_moon_earth_phases():
        start_alarm()
    else:
        cancel_alarm()    
