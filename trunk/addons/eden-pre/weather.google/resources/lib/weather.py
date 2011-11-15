# -*- coding: utf-8 -*-

import os
import re
import sys
import time
from traceback import print_exc


try:
    import xbmc
    import xbmcgui
    from xbmcaddon import Addon
    Addon = Addon( "weather.google" )
    WEATHER_WINDOW   = xbmcgui.Window( 12600 )
    ICONS_SET        = int( Addon.getSetting( 'icons_set' ) )
    RISING_SUN_CODE  = int( Addon.getSetting( 'risingsun_code' ) )
    RISING_SUN_PREF  = 0
    if RISING_SUN_CODE and Addon.getSetting( 'risingsun_none' ) == "false":
        RISING_SUN_PREF = int( Addon.getSetting( 'risingsun_pref' ) ) + 1
    WEATHER_ICONS    = os.path.join( Addon.getAddonInfo( 'path' ), "resources", "images", "" )
    CUSTOM_ICONS     = os.path.join( Addon.getSetting( 'custom_icons' ), "" )
    DATE_TIME_FORMAT = "%s %s" % ( xbmc.getRegion( "dateshort" ), xbmc.getRegion( "time" ) )
    CELSIUS_FORMAT   = ( "C" in xbmc.getRegion( "tempunit" ) )
    WEATHER_XML      = os.path.join( xbmc.translatePath( Addon.getAddonInfo( 'profile' ) ), "weather.xml" )
    if not os.path.exists( xbmc.translatePath( Addon.getAddonInfo( 'profile' ) ) ):
        os.makedirs( xbmc.translatePath( Addon.getAddonInfo( 'profile' ) ) )
except:
    # NOT RUNNING ON XBMC, ON DEV
    WEATHER_WINDOW   = None
    ICONS_SET        = 2
    RISING_SUN_CODE  = 0
    RISING_SUN_PREF  = 0
    WEATHER_ICONS    = ""
    CUSTOM_ICONS     = ""
    DATE_TIME_FORMAT = "%d/%m/%Y %I:%M:%S %p"
    CELSIUS_FORMAT   = True
    WEATHER_XML      = os.path.join( sys.path[ 0 ], "weather.xml" )


from risingsun import get_sun
SUN_UP, SUN_DOWN, IN_BROAD_DAYLIGHT = get_sun( RISING_SUN_CODE, RISING_SUN_PREF, True )
#print SUN_UP, SUN_DOWN, IN_BROAD_DAYLIGHT, RISING_SUN_CODE, RISING_SUN_PREF

from utilities import *
from google_weather_api import *
from icons_set import getIcon


def getDaysOfWeeks():
    days_of_week = {}
    try:
        dow = os.path.join( Addon.getAddonInfo( 'path' ), "resources", "language", xbmc.getLanguage(), "days_of_week.xml" )
        days_of_week = dict( re.findall( 'short="(.+?)".+?long="(.+?)"', open( dow ).read() ) )
    except Exception, e:
        #NameError: global name 'Addon' is not defined
        if "'Addon'" not in str( e ):
            print_exc()
    return days_of_week
DAYS_OF_WEEK = getDaysOfWeeks()


def getLang():
    lang = ""
    try:
        lang = xbmc.getRegion( "locale" )# supported on xbox, but not supported with XBMC mainline
        if not lang:
            langinfo = xbmc.translatePath( "special://xbmc/language/%s/langinfo.xml" % xbmc.getLanguage() )
            lang = re.search( '<menu>(.+?)</menu>', open( langinfo ).read() ).group( 1 )
    except Exception, e:
        #NameError: global name 'xbmc' is not defined
        if "'xbmc'" not in str( e ):
            print_exc()
    if not lang:
        #from locale import getdefaultlocale
        lang = DEFAULT_HL #str( getdefaultlocale() )[ 2:4 ].lower() or "en"
    return lang
LANG = getLang()


def writeXML( xml ):
    try: xml = xml.toprettyxml( encoding="utf-8" )
    except: print_exc()
    try: file( WEATHER_XML, "w" ).write( xml )
    except: print_exc()
    try: xbmc.log( xml, xbmc.LOGDEBUG )
    except: pass


def SetProperty( key, value ):
    if WEATHER_WINDOW:
        WEATHER_WINDOW.setProperty( key, value )
    else:
        # for test print
        print key, value


def SetProperties( weather, LocationIndex=1 ):
    # USED FOR OLD XBMC
    writeXML( weather )
    #Current weather
    #forecast_information
    forecast_info = weather.getElementsByTagName( "forecast_information" )[ 0 ]

    SetProperty( "Location", getData( forecast_info, "city" ) )
    SetProperty( "Location%s" % int( LocationIndex ), str( LocationIndex ) )
    SetProperty( "LocationIndex", str( LocationIndex ) )
    SetProperty( "AreaCode", getData( forecast_info, "postal_code" ) )

    #date = getData( forecast_info, "forecast_date" )
    #longdate = getData( forecast_info, "current_date_time" ).split()#[ 1: ]
    #longdate[ 0 ] = date
    #SetProperty( "Updated", " ".join( longdate ) )
    SetProperty( "Updated", time.strftime( DATE_TIME_FORMAT, time.localtime( time.time() ) ) )

    #extra info
    SetProperty( "Latitude", getData( forecast_info, "latitude_e6" ) )
    SetProperty( "Longitude", getData( forecast_info, "longitude_e6" ) )
    unit_system = getData( forecast_info, "unit_system" )
    SetProperty( "UnitSystem", unit_system )

    #current_conditions
    current_conditions = weather.getElementsByTagName( "current_conditions" )[ 0 ]

    fanartcode, icon = getIcon( getData( current_conditions, "icon" ), True )
    #print fanartcode, icon
    SetProperty( "Current.ConditionIcon", "special://temp/weather/128x128/%s" % icon )
    SetProperty( "Current.FanartCode", fanartcode )
    SetProperty( "Current.Condition", getData( current_conditions, "condition" ) )

    Temperature = getData( current_conditions, "temp_c" )
    Humidity    = getData( current_conditions, "humidity", True )
    Wind        = getData( current_conditions, "wind_condition", True )

    curSpeed, gUnit = re.search( ' (\d+) (mph|km/h)', Wind.lower() ).groups()
    newSpeed, strUnit = ConvertSpeed( curSpeed, gUnit, xbmc.getRegion( "speedunit" ) )
    Wind = Wind.replace( curSpeed, str( int( newSpeed ) ) ).replace( gUnit, strUnit )

    V = ( curSpeed, mphtokmh( curSpeed ) )[ gUnit.lower() == "mph" ]
    FeelsLike = getFeelsLike( int( Temperature ), int( V ) )
    DewPoint  = getDewPoint( int( Temperature ), int( Humidity.strip( "%" ) ) )

    if not CELSIUS_FORMAT:
        Temperature = getData( current_conditions, "temp_f" )
        FeelsLike   = CelsiusVsFahrenheit( FeelsLike, "tf" )
        DewPoint    = CelsiusVsFahrenheit( DewPoint, "tf" )

    SetProperty( "Current.Temperature", Temperature )
    SetProperty( "Current.FeelsLike", FeelsLike ) # "N/A" )

    SetProperty( "Current.UVIndex", "N/A" )
    SetProperty( "Current.Humidity", Humidity )

    SetProperty( "Current.Wind", Wind )
    SetProperty( "Current.DewPoint", DewPoint ) # "N/A" )

    #Future weather
    #forecast_conditions
    forecast_conditions = weather.getElementsByTagName( "forecast_conditions" )
    for i, condition in enumerate( forecast_conditions ):
        day = "Day%i." % ( i )
        day_of_week = getData( condition, "day_of_week" )
        SetProperty( day + "Title", DAYS_OF_WEEK.get( day_of_week ) or day_of_week )

        high = getData( condition, "high" )
        low = getData( condition, "low" )
        if unit_system == "SI" and not CELSIUS_FORMAT:
            high = CelsiusVsFahrenheit( high, "tf" )
            low = CelsiusVsFahrenheit( low, "tf" )
        if unit_system != "SI" and CELSIUS_FORMAT:
            high = CelsiusVsFahrenheit( high, "tc" )
            low = CelsiusVsFahrenheit( low, "tc" )
        SetProperty( day + "HighTemp", high )
        SetProperty( day + "LowTemp", low )
        
        SetProperty( day + "Outlook", getData( condition, "condition" ) )
        code, icon = getIcon( getData( condition, "icon" ) )
        SetProperty( day + "OutlookIcon", "special://temp/weather/128x128/%s" % icon )
        SetProperty( day + "FanartCode", code )

    SetProperty( "Current.Sunrise", SUN_UP )
    SetProperty( "Current.Sunset", SUN_DOWN )
    SetProperty( "Weather.IsFetched", "true" )


def getWeatherSettings( loc_index=None ):
    # USED FOR OLD XBMC
    location = None
    try:
        city = xbmc.getInfoLabel( "Window(Weather).Property(Location)" )
        LocationIndex = xbmc.getInfoLabel( "Window(Weather).Property(LocationIndex)" )
        if city and LocationIndex:
            location, loc_index = city, LocationIndex
        else:
            strxml = open( xbmc.translatePath( "special://userdata/guisettings.xml" ) ).read()
            currentlocation = re.search( '<currentlocation>(\d+)</currentlocation>', strxml )
            if currentlocation:
                loc_index = currentlocation.group( 1 )
                areacode = re.search( '<areacode%s>(.+?)</areacode%s>' % ( loc_index, loc_index ), strxml )
                if areacode:
                    location = areacode.group( 1 ).split( " - " )[ -1 ]

        if not loc_index:
            loc_index = Addon.getSetting( 'currentlocation' )
        if loc_index:
            Addon.setSetting( 'currentlocation', loc_index )
            #reset weather setting from xbmc guisettings.xml
            location = Addon.getSetting( 'areacode%s' % loc_index )
    except:
        print_exc()
    SetProperty( "Location", location )
    SetProperty( "Location%s" % int( loc_index ), str( loc_index ) )
    return location, loc_index


def SetProperties2( weather, LocationIndex=1 ):
    # new method for xbmc.python 2.0
    writeXML( weather )
    #Current weather
    #forecast_information
    forecast_info = weather.getElementsByTagName( "forecast_information" )[ 0 ]

    SetProperty( "Location%s" % int( LocationIndex ), getData( forecast_info, "city" ) )
    #SetProperty( "Location%s" % int( LocationIndex ), getData( forecast_info, "postal_code" ) )

    SetProperty( "Updated", time.strftime( DATE_TIME_FORMAT, time.localtime( time.time() ) ) )

    #current_conditions
    current_conditions = weather.getElementsByTagName( "current_conditions" )[ 0 ]

    fanartcode, OutlookIcon = getIcon( getData( current_conditions, "icon" ), True )
    SetProperty( "Current.OutlookIcon", OutlookIcon )
    SetProperty( "Current.FanartCode", fanartcode )
    SetProperty( "Current.Condition", getData( current_conditions, "condition" ) )

    Temperature = getData( current_conditions, "temp_c" )
    Humidity    = getData( current_conditions, "humidity", True ).strip( "%" )
    Wind        = getData( current_conditions, "wind_condition", True )
    WindDirection, at, curSpeed, gUnit = Wind.split()
    curSpeed, strUnit = ConvertSpeed( curSpeed, gUnit, "kmh" )

    FeelsLike = getFeelsLike( int( Temperature ), int( curSpeed ) )
    DewPoint  = getDewPoint( int( Temperature ), int( Humidity ) )

    SetProperty( "Current.Temperature", Temperature )
    SetProperty( "Current.FeelsLike", FeelsLike )

    SetProperty( "Current.UVIndex", "N/A" )
    SetProperty( "Current.Humidity", Humidity )
    
    #try: WindDirection = Addon.getLocalizedString( 32500 + cardinal_direction.index( WindDirection ) )
    #except: pass
    SetProperty( "Current.WindDirection", WindDirection )
    SetProperty( "Current.Wind", str( curSpeed ) )
    SetProperty( "Current.DewPoint", DewPoint )

    #Future weather
    toCelsius = ( getData( forecast_info, "unit_system" ) != "SI" )
    #forecast_conditions
    forecast_conditions = weather.getElementsByTagName( "forecast_conditions" )
    for i, condition in enumerate( forecast_conditions ):
        day = "Day%i." % ( i )
        day_of_week = getData( condition, "day_of_week" )
        SetProperty( day + "Title", DAYS_OF_WEEK.get( day_of_week ) or day_of_week )

        high = getData( condition, "high" )
        low  = getData( condition, "low" )
        if toCelsius:
            high = CelsiusVsFahrenheit( high, "tc" )
            low  = CelsiusVsFahrenheit( low,  "tc" )

        SetProperty( day + "HighTemp", high )
        SetProperty( day + "LowTemp", low )
        
        SetProperty( day + "Outlook", getData( condition, "condition" ) )
        fanartcode, OutlookIcon = getIcon( getData( condition, "icon" ) )
        SetProperty( day + "OutlookIcon", OutlookIcon )
        SetProperty( day + "FanartCode", fanartcode )

    SetProperty( "Current.Locale.Sunrise", SUN_UP )
    SetProperty( "Current.Locale.Sunset", SUN_DOWN )
    SetProperty( "Weather.IsFetched", "true" )
    SetProperty( "WeatherProvider", "Google Weather" )


def getWeatherSettings2( loc_index="1" ):
    # new method for xbmc.python 2.0
    try:
        location = Addon.getSetting( 'areacode%s' % loc_index )
        SetProperty( "Location", location )
        for i in range( 1, 4 ):
            SetProperty( "Location%i" % i, Addon.getSetting( "areacode%i" % i ) )
        SetProperty( "Locations", str( i ) )
        Addon.setSetting( 'currentlocation', loc_index )
    except:
        print_exc()
    return location, loc_index


def _test():
    cities = [ ( "Paris", "fr" ), ( "New York", "en" ), ( "Quebec, QC", "fr" ) ]
    for city in cities:
        weather = get_weather( *city )
        if weather:
            SetProperties( weather )
            print "-"*100


if __name__ == "__main__":
    _test()
