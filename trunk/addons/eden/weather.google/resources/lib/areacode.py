# -*- coding: utf-8 -*-

from weather import *
import timeanddate


def keyboard( text="", heading=Addon.getLocalizedString( 32010 ) ):
    kb = xbmc.Keyboard( text, heading, False )
    kb.doModal()
    if kb.isConfirmed():
        return kb.getText()
    return ""


def get_matching_city( country, country2="" ):
    countries = timeanddate.get_countries_id( country )
    totals = len( countries )
    heading = "[Astronomy] " + xbmc.getLocalizedString( 14024 )
    if totals == 0:
        if country2: return get_matching_city( country2, "" )
        location = keyboard( country, heading )
        if location: return get_matching_city( location )

    if totals == 1:
        return countries[ 0 ][ 0 ]

    if totals > 1:
        choices = [ "[B]%s[/B]" % Addon.getLocalizedString( 32052 ) ] + [ c for i, c in countries ]
        while True:
            selected = xbmcgui.Dialog().select( heading, choices )
            if selected == -1: break
            if selected == 0:
                location = keyboard( country, heading )
                if location:
                    return get_matching_city( location )
            else:
                return countries[ selected-1 ][ 0 ]


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
                #now get matching city from timeanddate
                id_city = None
                if Addon.getSetting( sys.argv[ 1 ] + "_city" ) == city.encode( "utf-8" ):
                    id_city = Addon.getSetting( sys.argv[ 1 ] + "_code" )
                if not id_city:
                    id_city = get_matching_city( location, city )
                if id_city:
                    #save settings
                    Addon.setSetting( sys.argv[ 1 ], city )
                    Addon.setSetting( sys.argv[ 1 ] + "_city", city )
                    Addon.setSetting( sys.argv[ 1 ] + "_code", id_city )
                #else:
                #    retry = True
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
