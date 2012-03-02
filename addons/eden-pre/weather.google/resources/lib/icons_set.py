
code = {
    #GOOGLE:               code  DESCRIPTION
    'N/A':                 'na', #Not Available
    'storm':               '0',  #Rain/Lightning
    'chance_of_storm':     '1',  #Windy/Rain
    '02':                  '2',  #Same as 01
    '03':                  '3',  #Same as 00
    '04':                  '4',  #Same as 00
    'sleet':               '5',  #Cloudy/Snow-Rain Mix
    '06':                  '6',  #Hail
    'rain_snow':           '7',  #Icy/Clouds Rain-Snow
    'chance_of_sleet':     '8',  #Icy/Haze Rain
    'mist':                '9',  #Haze/Rain
    '10':                  '10', #Icy/Rain
    '11':                  '11', #Light Rain
    '12':                  '12', #Moderate Rain
    'chance_of_snow':      '13', #Cloudy/Flurries
    '14':                  '14', #Same as 13
    'flurries':            '15', #Flurries
    '16':                  '16', #Same as 13
    '17':                  '17', #Same as 00
    '18':                  '18', #Same as 00
    'dust':                '19', #Dust
    'fog':                 '20', #Fog
    'haze':                '21', #Haze
    'smoke':               '22', #Smoke
    '23':                  '23', #Windy
    '24':                  '24', #Same as 23
    'icy':                 '25', #Frigid
    'cloudy':              '26', #Mostly Cloudy
    'night_mostly_cloudy': '27', #Mostly Cloudy/Night
    'mostly_cloudy':       '28', #Mostly Cloudy/Sunny
    'night_partly_cloudy': '29', #Partly Cloudy/Night
    'partly_cloudy':       '30', #Partly Cloudy/Day
    'night_sunny':         '31', #Clear/Night
    'sunny':               '32', #Clear/Day
    '33':                  '33', #Hazy/Night
    '34':                  '34', #Hazy/Day
    '35':                  '35', #Same as 00
    '36':                  '36', #Hot!
    'chance_of_tstorm':    '37', #Lightning/Day
    'thunderstorm':        '38', #Lightning
    'chance_of_rain':      '39', #Rain/Day
    'rain':                '40', #Rain
    'snow':                '41', #Snow
    '42':                  '42', #Same as 41
    '43':                  '43', #Windy/Snow
    'mostly_sunny':        '44', #Same as 30
    'night_rain':          '45', #Rain/Night
    'night_snow':          '46', #Snow/Night
    'night_thunderstorm':  '47', #Thunder Showers/Night
    }


import os
from sys import modules


weather = modules.get( 'resources.lib.weather' ) or modules.get( 'weather' ) or modules[ '__main__' ]


def getIcon( uri, usenight=False ):
    PREFIX_ICON_ADDON = ( "", "night_" )[ usenight ]
    google_code = os.path.splitext( os.path.basename( uri ) )[ 0 ]
    xbmc_code   = usenight and code.get( PREFIX_ICON_ADDON + google_code )
    xbmc_code   = xbmc_code or code.get( google_code, 'na' )

    #default icon
    icon = "%s.png" % xbmc_code

    # icons of addon
    if weather.ICONS_SET == 0:
        if not usenight: icon = weather.WEATHER_ICONS + icon
        else: icon = os.path.join( weather.WEATHER_ICONS + "night", icon )

    # icons custom
    elif weather.ICONS_SET == 3:
        icon = weather.CUSTOM_ICONS + icon
    
    # icons google
    elif weather.ICONS_SET == 2:
        if code.get( google_code ):
            icon = os.path.join( weather.WEATHER_ICONS + "default", code[ google_code ] + ".gif" )

    #print "%i - %s: %r" % ( weather.ICONS_SET, xbmc_code, icon )
    return xbmc_code, icon
