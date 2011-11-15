
### GOOGLE: 'code'            #DESCRIPTION
code = {
    'N/A': 'na',              #Not Available
    'storm': '00',            #Rain/Lightning
    'chance_of_storm': '01',  #Windy/Rain
    '02': '02',               #Same as 01
    '03': '03',               #Same as 00
    '04': '04',               #Same as 00
    'sleet': '05',            #Cloudy/Snow-Rain Mix
    '06': '06',               #Hail
    'rain_snow': '07',        #Icy/Clouds Rain-Snow
    'chance_of_sleet': '08',  #Icy/Haze Rain
    'mist': '09',             #Haze/Rain
    '10': '10',               #Icy/Rain
    '11': '11',               #Light Rain
    '12': '12',               #Moderate Rain
    'chance_of_snow': '13',   #Cloudy/Flurries
    '14': '14',               #Same as 13
    '15': '15',               #Flurries
    '16': '16',               #Same as 13
    '17': '17',               #Same as 00
    '18': '18',               #Same as 00
    'dust': '19',             #Dust
    'fog': '20',              #Fog
    'haze': '21',             #Haze
    'smoke': '22',            #Smoke
    '23': '23',               #Windy
    '24': '24',               #Same as 23
    'icy': '25',              #Frigid
    'cloudy': '26',           #Mostly Cloudy
    'night_mostly_cloudy': '27', #Mostly Cloudy/Night
    'mostly_cloudy':       '28', #Mostly Cloudy/Sunny
    'night_partly_cloudy': '29', #Partly Cloudy/Night
    'partly_cloudy':       '30', #Partly Cloudy/Day
    'night_sunny': '31',      #Clear/Night
    'sunny': '32',            #Clear/Day
    '33': '33',               #Hazy/Night
    '34': '34',               #Hazy/Day
    '35': '35',               #Same as 00
    '36': '36',               #Hot!
    'chance_of_tstorm': '37', #Lightning/Day
    'thunderstorm': '38',     #Lightning
    'chance_of_rain': '39',   #Rain/Day
    'rain': '40',             #Rain
    'snow': '41',             #Snow
    '42': '42',               #Same as 41
    '43': '43',               #Windy/Snow
    'mostly_sunny': '44',     #Same as 30
    'night_rain': '45',       #Rain/Night
    'night_snow': '46',       #Snow/Night
    'night_thunderstorm': '47', #Thunder Showers/Night
    }


import os
from sys import modules
from urlparse import urljoin


weather = modules.get( 'resources.lib.weather' ) or modules.get( 'weather' ) or modules[ '__main__' ]
PREFIX_ICON_ADDON = ( "night_", "" )[ weather.IN_BROAD_DAYLIGHT ]

try:
    from xbmcvfs import copy, exists
except:
    from shutil import copy
    exists = os.path.exists


def copyIcon( icon_path, dest ):
    OK = False
    try:
        if exists( icon_path ):
            OK = copy( icon_path, "special://temp/weather/128x128/%s" % dest )
            OK = OK or exists( "special://temp/weather/128x128/%s" % dest )
    except:
        weather.print_exc()
    return OK


def getIcon( uri, usenight=False ):
    google_code = os.path.splitext( os.path.basename( uri ) )[ 0 ]
    xbmc_code   = usenight and code.get( PREFIX_ICON_ADDON + google_code )
    xbmc_code   = xbmc_code or code.get( google_code, 'na' )

    # icons of addon
    if weather.ICONS_SET == 0:
        icon = "%s.png" % google_code
        if usenight:
            icon = PREFIX_ICON_ADDON + icon
        custom_icon = "%i.jpg" % int( xbmc_code )
        if copyIcon( weather.WEATHER_ICONS + icon, custom_icon ):
            icon = custom_icon

    # icons xbmc
    elif weather.ICONS_SET in [ 1, 3 ]:
        icon = "%s.png" % xbmc_code
        if xbmc_code.isdigit():
            icon = "%i.png" % int( xbmc_code )
        # icons custom
        if weather.ICONS_SET == 3:
            custom_icon = "%i.jpg" % int( xbmc_code )
            if copyIcon( weather.CUSTOM_ICONS + icon, custom_icon ):
                icon = custom_icon
    
    # icons google
    elif weather.ICONS_SET == 2:
        #icon = urljoin( weather.GOOGLE_WEATHER_URL, uri )
        icon = os.path.basename( uri )
        custom_icon = "%i.jpg" % int( xbmc_code )
        if copyIcon( os.path.join( weather.WEATHER_ICONS + "default", icon ), custom_icon ):
            icon = custom_icon

    #print "%i - %s: %r" % ( weather.ICONS_SET, xbmc_code, icon )
    return xbmc_code, icon
