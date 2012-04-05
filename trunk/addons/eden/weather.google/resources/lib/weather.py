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
    WEATHER_WINDOW = xbmcgui.Window( 12600 )
    ICONS_SET = int( Addon.getSetting( 'icons_set' ) )
    CURRENT_LOCATION = int( Addon.getSetting( 'currentlocation' ) ) - 1
    
    WEATHER_ICONS = os.path.join( Addon.getAddonInfo( 'path' ), "resources", "images", "" )
    CUSTOM_ICONS = os.path.join( Addon.getSetting( 'custom_icons' ), "" )
    DATE_TIME_FORMAT = "%s %s" % ( xbmc.getRegion( "dateshort" ), xbmc.getRegion( "time" ) )
    CELSIUS_FORMAT = ( "C" in xbmc.getRegion( "tempunit" ) )
    WEATHER_XML = os.path.join( xbmc.translatePath( Addon.getAddonInfo( 'profile' ) ), "weather.xml" )
    if not os.path.exists( xbmc.translatePath( Addon.getAddonInfo( 'profile' ) ) ):
        os.makedirs( xbmc.translatePath( Addon.getAddonInfo( 'profile' ) ) )
except:
    # NOT RUNNING ON XBMC, ON DEV
    WEATHER_WINDOW   = None
    ICONS_SET        = 2
    WEATHER_ICONS    = ""
    CUSTOM_ICONS     = ""
    DATE_TIME_FORMAT = "%d/%m/%Y %I:%M:%S %p"
    CELSIUS_FORMAT   = True
    WEATHER_XML      = os.path.join( sys.path[ 0 ], "weather.xml" )


IN_BROAD_DAYLIGHT = True

from utilities import *
from google_weather_api import *
from icons_set import getIcon


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


def SetProperty( key, value="" ):
    if WEATHER_WINDOW:
        WEATHER_WINDOW.setProperty( key, value )
    else:
        # for test print
        print key, value


def ClearProperties():
    #clear base properties
    map( SetProperty,
        [ "Updated",
          "Current.OutlookIcon",
          "Current.FanartCode",
          "Current.Condition",
          "Current.Temperature",
          "Current.FeelsLike",
          "Current.UVIndex",
          "Current.Humidity",
          "Current.WindDirection",
          "Current.Wind",
          "Current.DewPoint",
          ]
        )
    for i in xrange( 4 ):
        map( SetProperty,
            [ "Day%i.Title"       % ( i ),
              "Day%i.HighTemp"    % ( i ),
              "Day%i.LowTemp"     % ( i ),
              "Day%i.Outlook"     % ( i ),
              "Day%i.OutlookIcon" % ( i ),
              "Day%i.FanartCode"  % ( i ),
              ]
            )
    #clear extra properties
    map( SetProperty,
        [ "Weather.IsFetched",
          "Weather.ExtraIsFetched",
          "Current.Location.LocalTime",
          "Current.AstroTwilight.Start",
          "Current.AstroTwilight.End",
          "Current.NauticTwilight.Start",
          "Current.NauticTwilight.End",
          "Current.CivilTwilight.Start",
          "Current.CivilTwilight.End",
          "Current.Sunrise",
          "Current.Sunset",
          "Current.Sunrise.Azimuth",
          "Current.Sunset.Azimuth",
          "Current.Sun.Length",
          "Current.Sun.Diff",
          "Current.Solarnoon.Time",
          "Current.Solarnoon.Altitude",
          "Current.Solarnoon.Distance",
          "In.Broad.Daylight",
          "Current.Moonrise",
          "Current.Moonset",
          "Current.Moonrise.Azimuth",
          "Current.Moonset.Azimuth",
          "Current.Moon.Meridian.Time",
          "Current.Moon.Meridian.Altitude",
          "Current.Moon.Meridian.Distance",
          "Current.Moon.Meridian.Illuminated",
          "Current.Moon.Phase",
          #"Current.Earth.Phase.LargeImage",
          #"Current.Earth.Phase.Image",
          #"Current.Moon.Phase.Image",
          ]
        )

def SetProperties( weather, LocationIndex=1 ):
    writeXML( weather )
    #Current weather
    #forecast_information
    forecast_info = weather.getElementsByTagName( "forecast_information" )[ 0 ]

    SetProperty( "Location%s" % int( LocationIndex ), getData( forecast_info, "city" ) )
    #SetProperty( "Location%s" % int( LocationIndex ), getData( forecast_info, "postal_code" ) )
    #SetProperty( "Updated", time.strftime( DATE_TIME_FORMAT, time.localtime( time.time() ) ) )

    #current_conditions
    current_conditions = weather.getElementsByTagName( "current_conditions" )[ 0 ]

    fanartcode, OutlookIcon = getIcon( getData( current_conditions, "icon" ), not IN_BROAD_DAYLIGHT )
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

    SetProperty( "Current.WindDirection", WindDirection )
    SetProperty( "Current.Wind", str( curSpeed ) )
    SetProperty( "Current.DewPoint", DewPoint )

    from timeanddate import DAY_MONTH_ID_LONG
    t1 = time.time()
    #Future weather
    toCelsius = ( getData( forecast_info, "unit_system" ) != "SI" )
    #forecast_conditions
    forecast_conditions = weather.getElementsByTagName( "forecast_conditions" )
    for i, condition in enumerate( forecast_conditions ):
        day = "Day%i." % ( i )
        day_of_week = time.strftime( "%A", time.localtime( t1 ) )
        if DAY_MONTH_ID_LONG.get( day_of_week ):
            day_of_week = xbmc.getLocalizedString( DAY_MONTH_ID_LONG[ day_of_week ] )
        SetProperty( day + "Title", day_of_week )
        t1 += 24*60*60

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

    SetProperty( "Weather.IsFetched", "true" )


def getWeatherSettings( loc_index="1" ):
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


def Main( loc_index="1", retry=3 ):
    try:
        ClearProperties()
        SetProperty( "WeatherProvider", "Google Weather" )

        city, LocationIndex = getWeatherSettings( loc_index )

        if not city: raise ( city, LocationIndex )

        #run extra info
        try:
            import timeanddate
            is_night = timeanddate.SetProperties( LocationIndex )
            globals().update( { "IN_BROAD_DAYLIGHT": is_night } )
        except:
            print_exc()

        weather = get_weather( city, LANG )
        if weather:
            SetProperties( weather, LocationIndex=LocationIndex )
    except:
        print_exc()
        retry -= 1
        if retry > 0:
            Main( loc_index, retry )


def _test():
    cities = [ ( "Paris", "fr" ), ( "New York", "en" ), ( "Quebec, QC", "fr" ) ]
    for city in cities:
        weather = get_weather( *city )
        if weather:
            SetProperties( weather )
            print "-"*100


if __name__ == "__main__":
    _test()