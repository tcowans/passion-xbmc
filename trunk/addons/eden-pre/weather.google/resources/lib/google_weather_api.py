# -*- coding: utf-8 -*-

import re
import urllib2
import unicodedata
from urllib import urlencode
from traceback import print_exc
from xml.dom.minidom import parseString
from locale import getdefaultlocale

DEFAULT_HL = str( getdefaultlocale() )[ 2:4 ].lower() or "en"

GOOGLE_WEATHER_URL   = 'http://www.google.com/ig/api?'
GOOGLE_COUNTRIES_URL = 'http://www.google.com/ig/countries?'
GOOGLE_CITIES_URL    = 'http://www.google.com/ig/cities?'


def _unicode( text, encoding='utf-8' ):
    try: text = unicode( text, encoding )
    except: pass
    return text


def normalize_string( text ):
    try: text = unicodedata.normalize( 'NFKD', _unicode( text ) ).encode( 'ascii', 'ignore' )
    except: pass
    return text


def getData( elem, tag, clean=False ):
    try: data = elem.getElementsByTagName( tag )[ 0 ].getAttribute( "data" )
    except: data = ""
    if clean:
        data = data.split( ": ", 1 )[ -1 ]
    return data


def parse_response( xml_response ):
    dom = parseString( xml_response )
    if __name__ == "__main__":
        print dom.toprettyxml()
    return dom


def get_google_response( url ):
    sock = urllib2.urlopen( url )

    #Content-Type: text/html; charset=ISO-8859-1
    contentType = sock.info().get( 'content-type' ) or ''
    encoding = ''.join( re.findall( 'charset\=(.*)', contentType ) )
    if not encoding:
        encoding = 'utf-8'

    xml_response = sock.read()
    if encoding.lower() != 'utf-8':
        try: xml_response = xml_response.decode( encoding ).encode( 'utf-8' )
        except: print_exc()

    sock.close()
    return xml_response


def get_weather( weather, hl=DEFAULT_HL ):
    """ Fetches weather report from Google

        Parameters
          weather: 
            - by zip code (10001)
            - by city name, state (woodland,PA) 
            - by city name, country (london, england);
            - by latitude+longitude (,,,30670000,104019996)

          hl: the language parameter (language code). Default value is empty string, in this case Google will use English.
    """
    #use locals() is { "hl": hl, "weather": weather }
    data = urlencode( locals() )
    url = GOOGLE_WEATHER_URL + data

    xml_response = get_google_response( url )
    return parse_response( xml_response )


def get_countries( hl=DEFAULT_HL, output='xml' ):
    """ Get list of countries in specified language from Google

        Parameters
          hl: the language parameter (language code). Default value is empty string, in this case Google will use English.
    """
    data = urlencode( locals() )
    url = GOOGLE_COUNTRIES_URL + data

    xml_response = get_google_response( url )
    dom = parse_response( xml_response )

    countries = []

    for country in dom.getElementsByTagName( 'country' ):
        country = ( getData( country, "name" ), getData( country, "iso_code" ) )
        countries.append( country )

    dom.unlink()
    return sorted( countries, key=lambda c: normalize_string( c[ 0 ] ).lower() )


def get_cities( country, hl=DEFAULT_HL, output='xml' ):
    """ Get list of cities of necessary country in specified language from Google

        Parameters
          country_code: code of the necessary country. For example 'de' or 'fr'.
          hl: the language parameter (language code). Default value is empty string, in this case Google will use English.
    """
    country = country.lower()
    data = urlencode( locals() )
    url = GOOGLE_CITIES_URL + data

    xml_response = get_google_response( url )
    dom = parse_response( xml_response )

    cities = []

    for city in dom.getElementsByTagName( 'city' ):
        coord = ",,,%s,%s" % ( getData( city, "latitude_e6" ), getData( city, "longitude_e6" ) )
        city  = getData( city, "name" )
        cities.append( ( city, coord ) )

    dom.unlink()
    return sorted( cities, key=lambda c: normalize_string( c[ 0 ] ).lower() )


if __name__ == "__main__":
    #print get_weather( 'Quebec,,,52939916,-73549136' )#'g1j3p8' ) 
    #print get_countries()
    #print get_cities( "CA" )
    url = "http://www.sunrisesunset.com/mobile/day.asp?latitude=52.939916&latitude_n_s=N&longitude=73.549136&longitude_e_w=W&timezone=-6&dayOfMonth=11&month=11&year=2011"
    print urllib2.urlopen( url ).read()
