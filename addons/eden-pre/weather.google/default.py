"""
    Google Weather
    url: http://passion-xbmc.googlecode.com/svn/trunk/addons/eden-pre/weather.google/
"""

from resources.lib.weather import *

#print sys.argv

loc_index = "".join( sys.argv[ 1: ] )
if loc_index.isdigit():
    GWS = getWeatherSettings2
    SP  = SetProperties2
else:
    loc_index = None
    GWS = getWeatherSettings
    SP  = SetProperties


def Main( retry=3 ):
    try:
        ClearProperties()
        SetProperty( "WeatherProvider", "Google Weather" )

        city, LocationIndex = GWS( loc_index )

        if not city: raise ( city, LocationIndex )

        weather = get_weather( city, LANG )
        if weather:
            SP( weather, LocationIndex=LocationIndex )
    except:
        print_exc()
        retry -= 1
        if retry > 0:
            Main( retry )



if __name__ == "__main__":
    Main()
