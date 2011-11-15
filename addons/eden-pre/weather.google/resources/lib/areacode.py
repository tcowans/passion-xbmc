# -*- coding: utf-8 -*-

from weather import *


def keyboard( text="" ):
    kb = xbmc.Keyboard( text, Addon.getLocalizedString( 32010 ), False )
    kb.doModal()
    if kb.isConfirmed():
        return kb.getText()
    return ""


def changeLocation( location, onselection=False ):
    retry = False
    if location:
        weather = get_weather( location, LANG )
        try: 
            forecast   = weather.getElementsByTagName( "forecast_information" )[ 0 ]
            conditions = weather.getElementsByTagName( "current_conditions" )[ 0 ]

            Temp      = getData( conditions, ( "temp_f", "temp_c" )[ CELSIUS_FORMAT ] )
            condition = getData( conditions, "condition" )
            humidity  = getData( conditions, "humidity" )
            wind      = getData( conditions, "wind_condition" )
            city      = getData( forecast, "city" )

            # now ask user
            heading = "%s  (%s%s)" % ( city.encode( "utf-8" ), Temp.encode( "utf-8" ), xbmc.getRegion( "tempunit" ) )
            if xbmcgui.Dialog().yesno( heading, condition, humidity, wind, xbmc.getLocalizedString( 222 ), xbmc.getLocalizedString( 424 ) ):
                Addon.setSetting( sys.argv[ 1 ], city )#location )
            else:
                retry = True
        except:
            print_exc()
            retry = True
    else:
        retry = True

    if retry and not onselection:
        location = keyboard( location )
        if location:
            return changeLocation( location )

    return not retry


def selection():
    countries = get_countries()
    while True:
        selected = xbmcgui.Dialog().select( Addon.getLocalizedString( 32011 ), [ "%s   [%s]" % c for c in countries ] )
        if selected == -1: break
        country  = countries[ selected ][ 0 ]
        iso_code = countries[ selected ][ 1 ]
        
        cities = get_cities( iso_code )
        if not cities:
            xbmcgui.Dialog().ok( Addon.getLocalizedString( 32000 ), Addon.getLocalizedString( 32012 ), country )
            continue

        while True:
            selected = xbmcgui.Dialog().select( Addon.getLocalizedString( 32013 ) % country, [ c[ 0 ] for c in cities ] )
            if selected == -1: break
            city = cities[ selected ][ 0 ]
            #location = cities[ selected ][ 1 ] # not good for all countries
            location = "%s, %s" % ( normalize_string( city ), normalize_string( country ) )

            OK = changeLocation( location, True )
            if OK:
                return


def Main():
    if xbmcgui.Dialog().yesno( Addon.getLocalizedString( 32000 ), "", Addon.getLocalizedString( 32014 ), "", xbmc.getLocalizedString( 413 ), xbmc.getLocalizedString( 396 ) ):
        selection()
    else:
        text = keyboard()
        if text:
            changeLocation( text )


    #Addon.openSettings()
    xbmc.executebuiltin( "Addon.openSettings(weather.google)" )

    xbmc.executebuiltin( "SetFocus(200)" )
    id = 100 + int( sys.argv[ 1 ].replace( "areacode", "" ) )
    xbmc.executebuiltin( "SetFocus(%i)" % id )



Main()
