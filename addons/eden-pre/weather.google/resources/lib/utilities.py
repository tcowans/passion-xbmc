# -*- coding: utf-8 -*-

import math

#http://fr.wikipedia.org/wiki/Points_cardinaux#Rose_des_vents
cardinal_direction = [ "N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSO", "SO", "OSO", "O", "ONO", "NO", "NNO" ]

stringsUnit = {
    "kmh":      "km/h",
    "mpmin":    "m/min",
    "mps":      "m/s",
    "fth":      "ft/h",
    "ftm":      "ft/min",
    "fts":      "ft/s",
    "mph":      "mph",
    "kts":      "kts",
    "beaufort": "Beaufort",
    "inchs":    "inch/s",
    "yards":    "yard/s",
    "fpf":      "Furlong/Fortnight",
    }


def CelsiusVsFahrenheit( temp, to="" ):
    # USED FOR OLD XBMC
    temp = int( temp )
    if to == "tf":
        temp = ( ( 9.0 / 5.0 ) * temp + 32 )

    if to == "tc":
        temp = ( ( 5.0 / 9.0 ) * ( temp - 32.0 ) )

    # fix +.5 = +1
    if ( "%.1f" % temp ).split( "." )[ 1 ] >= "5":
        temp += 1

    return str( int( temp ) )


def getFeelsLike( T=10, V=25 ):
    """ The formula to calculate the equivalent temperature related to the wind chill is:
        T(REF) = 13.12 + 0.6215 * T - 11.37 * V**0.16 + 0.3965 * T * V**0.16
        Or:
        T(REF): is the equivalent temperature in degrees Celsius
        V: is the wind speed in km/h measured at 10m height
        T: is the temperature of the air in degrees Celsius
        source: http://zpag.tripod.com/Meteo/eolien.htm
    """
    FeelsLike = T
    #Wind speeds of 4 mph or less, the wind chill temperature is the same as the actual air temperature.
    if round( ( V + .0 ) / 1.609344 ) > 4:
        FeelsLike = ( 13.12 + ( 0.6215 * T ) - ( 11.37 * V**0.16 ) + ( 0.3965 * T * V**0.16 ) )
    #
    return str( round( FeelsLike ) )


def getDewPoint( Tc=0, RH=93, minRH=( 0, 0.075 )[ 0 ] ):
    """ Dewpoint from relative humidity and temperature
        If you know the relative humidity and the air temperature,
        and want to calculate the dewpoint, the formulas are as follows.
    """
    #First, if your air temperature is in degrees Fahrenheit, then you must convert it to degrees Celsius by using the Fahrenheit to Celsius formula.
    # Tc = 5.0 / 9.0 * ( Tf - 32.0 )
    #The next step is to obtain the saturation vapor pressure(Es) using this formula as before when air temperature is known.
    Es = 6.11 * 10.0**( 7.5 * Tc / ( 237.7 + Tc ) )
    #The next step is to use the saturation vapor pressure and the relative humidity to compute the actual vapor pressure(E) of the air. This can be done with the following formula.
    #RH=relative humidity of air expressed as a percent. or except minimum(.075) humidity to abort error with math.log.
    RH = RH or minRH #0.075
    E = ( RH * Es ) / 100
    #Note: math.log( ) means to take the natural log of the variable in the parentheses
    #Now you are ready to use the following formula to obtain the dewpoint temperature.
    try:
        DewPoint = ( -430.22 + 237.7 * math.log( E ) ) / ( -math.log( E ) + 19.08 )
    except ValueError:
        #math domain error, because RH = 0%
        #return "N/A"
        DewPoint = 0 #minRH
    #Note: Due to the rounding of decimal places, your answer may be slightly different from the above answer, but it should be within two degrees.
    return str( int( DewPoint ) )


def mphtokmh( mph ):
    return round( int( mph ) * 1.609344, 2 )


def ConvertSpeed( curSpeed, gUnit, strUnit="mph" ):
    # USED FOR OLD XBMC
    curSpeed = int( curSpeed )
    #curSpeed param must be kmh
    if gUnit == "mph": curSpeed = mphtokmh( curSpeed )

    if strUnit == "kmh":     curSpeed = int( curSpeed ) # already in kmh
    elif strUnit == "mps":   curSpeed = int( curSpeed * ( 1000.0 / 3600.0 ) + 0.5 )
    elif strUnit == "mph":   curSpeed = int( curSpeed / ( 8.0 / 5.0 ) )
    elif strUnit == "mpmin": curSpeed = int( curSpeed * ( 1000.0 / 3600.0 ) + 0.5 * 60 )
    elif strUnit == "fth":   curSpeed = int( curSpeed * 3280.8398888889 )
    elif strUnit == "ftm":   curSpeed = int( curSpeed * 54.6805555556 )
    elif strUnit == "fts":   curSpeed = int( curSpeed * 0.911344 )
    elif strUnit == "kts":   curSpeed = int( curSpeed * 0.5399568 )
    elif strUnit == "inchs": curSpeed = int( curSpeed * 10.9361388889 )
    elif strUnit == "yards": curSpeed = int( curSpeed * 0.3037814722 )
    elif strUnit == "fpf":   curSpeed = int( curSpeed * 1670.25 )
    elif strUnit == "beaufort":
        knot = float( curSpeed * 0.5399568 ) # to kts first
        if ( knot <= 1.0 ): curSpeed = 0
        elif ( knot >  1.0  and knot < 3.5  ): curSpeed = 1
        elif ( knot >= 3.5  and knot < 6.5  ): curSpeed = 2
        elif ( knot >= 6.5  and knot < 10.5 ): curSpeed = 3
        elif ( knot >= 10.5 and knot < 16.5 ): curSpeed = 4
        elif ( knot >= 16.5 and knot < 21.5 ): curSpeed = 5
        elif ( knot >= 21.5 and knot < 27.5 ): curSpeed = 6
        elif ( knot >= 27.5 and knot < 33.5 ): curSpeed = 7
        elif ( knot >= 33.5 and knot < 40.5 ): curSpeed = 8
        elif ( knot >= 40.5 and knot < 47.5 ): curSpeed = 9
        elif ( knot >= 47.5 and knot < 55.5 ): curSpeed = 10
        elif ( knot >= 55.5 and knot < 63.5 ): curSpeed = 11
        elif ( knot >= 63.5 and knot < 74.5 ): curSpeed = 12
        elif ( knot >= 74.5 and knot < 80.5 ): curSpeed = 13
        elif ( knot >= 80.5 and knot < 89.5 ): curSpeed = 14
        elif ( knot >= 89.5 ): curSpeed = 15

    return curSpeed, stringsUnit.get( strUnit, strUnit )


if __name__ == "__main__":
    print getFeelsLike( 8, 3 )
    print getDewPoint( 8, 0 )
    data = "Wind: NE at 7 mph".split( ": ", 1 )[ -1 ]
    data = "Vent : NE à 8 km/h".split( ": ", 1 )[ -1 ]
    #import re
    w_direction, at, curSpeed, gUnit = data.split()
    print w_direction
    #curSpeed, gUnit = re.search( ' (\d+) (mph|km/h)', data.lower() ).groups()
    newSpeed, strUnit = ConvertSpeed( curSpeed, gUnit )#xbmc.getRegion( "speedunit" )
    print data.replace( curSpeed, str( newSpeed ) ).replace( gUnit, strUnit )
