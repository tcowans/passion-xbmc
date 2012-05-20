
import re
import random
import urllib
import urllib2
from gzip import GzipFile
from StringIO import StringIO
from traceback import print_exc

import json

try:
    import xbmc
    weatherworld_json = xbmc.translatePath( "special://skin/scripts/weatherworld/weatherworld.json" )
    coordinates_json  = xbmc.translatePath( "special://skin/scripts/weatherworld/coordinates.json" )
except:
    xbmc = None
    weatherworld_json = "weatherworld.json"
    coordinates_json  = "coordinates.json"


BASE_URL = "http://timeanddate.com/weather/"

HTTP_USER_AGENT = random.choice( [ "Mozilla/5.0 (Windows NT 5.1; rv:12.0) Gecko/20100101 Firefox/12.0",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.168 Safari/535.19"
    ] )

HEADERS = {
    'Host':            BASE_URL[ 7: ].split( "/" )[ 0 ],
    'User-Agent':      HTTP_USER_AGENT,
    'Accept':          'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en,en-us;q=0.5,en;q=0.3',
    'Accept-Charset':  'ISO-8859-1,UTF-8;q=0.7,*;q=0.7',
    'Accept-Encoding': 'gzip, deflate',
    'Content-Type':    'text/html; charset=UTF-8',
    'Pragma':          'no-cache',
    'Cache-Control':   'no-store'
    }


def get_html_source( url, filesave=None ):
    html = ""
    try:
        request = urllib2.urlopen( urllib2.Request( url, headers=HEADERS ) )
        is_gzip = request.headers.get( "Content-Encoding" ) == "gzip"
        html    = request.read()
        request.close()

        if is_gzip:
            html = GzipFile( fileobj=StringIO( html ) ).read()

        if filesave:
            file( filesave, "w" ).write( html )
    except:
        print_exc()
    return html


def coords2degree( deg, min, card ):
    deg += ( min * 100.0 / 60.0 / 100.0 )
    if card.lower() in [ "s", "w" ]:
        deg = float( "-" + str( deg ) )
    return str( deg )

def get_coordinates( url ):
    coords = { "lat": [ "", "" ], "long": [ "", "" ] }
    try:
        html = get_html_source( url )
        #print html
        n = re.compile( '<a href="/worldclock/city.html\?n\=(.*?)">' ).findall( html )[ 0 ]
        html = get_html_source( "http://timeanddate.com/worldclock/city.html?n=" + str( n ) )
        latlong_regexp = "<tr><td>(Lat|Long)itude: </td><td class=r>(.*?)&deg;&nbsp;(.*?)'&nbsp;</td><td>(.*?)</td></tr>"
        for coord in re.compile( latlong_regexp ).findall( html ):
            coords[ coord[ 0 ].lower() ] = [
                "%i° %i' %s" % ( int( coord[ 1 ] ), int( coord[ 2 ] ), coord[ 3 ][ 0 ] ),
                coords2degree( int( coord[ 1 ] ), int( coord[ 2 ] ), coord[ 3 ][ 0 ] )
                ]
    except:
        print_exc()
    return coords


def load_coords():
    coords = {}
    try: coords = json.loads( open( coordinates_json ).read() )
    except: print_exc()
    return coords


def get_cities():
    cities = []
    coordinates  = load_coords()
    hasnewcoords = False
    try:
        html = get_html_source( BASE_URL )

        clear_city = re.compile( '<td><a href="/weather/(.*?)">(.*?)</a><span id=.*?>(.*?)</span></td><td class=r id=.*?>(.*?)</td><td class=r>(.*?)</td><td class=r>(.*?)</td>' )

        count = 0
        for v in re.compile( '<tr class=.*?>(.*?)</tr>' ).findall( html ):
            items = clear_city.findall( v )
            #print len( items )
            for item in items:
                count += 1
                try:
                    url = BASE_URL + item[ 0 ]
                    coords = coordinates.get( item[ 0 ].replace( "/", "-" ) )
                    if not coords:
                        print count, url
                        coords = get_coordinates( url )
                        coordinates[ item[ 0 ].replace( "/", "-" ) ] = coords
                        hasnewcoords = True
                    #break
                    city = {
                        "country": item[ 0 ].split( "/" )[ 0 ].title(),
                        "city":    item[ 1 ] + item[ 2 ],
                        "time":    item[ 3 ],
                        "icon":    "",
                        "outlook": "",
                        "temp":    "",
                        "unit":    "",
                        "coords":  coords or { "lat": [ "", "" ], "long": [ "", "" ] },
                        "url":     url,
                        }
                    icon_outlook = re.compile( '<img src="(.*?)" width=30 height=30 alt=".*?" title="(.*?)">' ).findall( item[ 4 ] )
                    if not icon_outlook:
                        html = get_html_source( url )
                        icon_outlook = re.compile( '<img class=mp src="(.*?)" width=30 height=30 alt=".*?" title="(.*?)">' ).findall( html )
                    if icon_outlook:
                        city[ "icon" ] = icon_outlook[ 0 ][ 0 ]
                        city[ "outlook" ] = icon_outlook[ 0 ][ 1 ]

                    temp_unit = item[ 5 ].split( "&nbsp;" ) + [ "" ]
                    city[ "temp" ] = temp_unit[ 0 ]
                    city[ "unit" ] = temp_unit[ 1 ]
                    cities.append( city )
                except:
                    print_exc()
            #break

        #cities.sort( key=lambda c: ( c.get( "country" ), c.get( "city" ) ) )
        #strCities = json.dumps( cities, sort_keys=True, indent=2 )
        #file( weatherworld_json, "w" ).write( strCities )
        #print len( cities ), len( coordinates )
    except:
        print_exc()
    try:
        if hasnewcoords and coordinates:
            #print len( coordinates )
            newcoords = json.dumps( coordinates, sort_keys=True, indent=2 )
            file( coordinates_json, "w" ).write( newcoords )
    except:
        print_exc()
    return cities


def save_cities( cities ):
    ok = True
    try:
        cities.sort( key=lambda c: ( c.get( "country" ), c.get( "city" ) ) )
        strCities = json.dumps( cities, sort_keys=True, indent=2 )
        file( weatherworld_json, "w" ).write( strCities )
    except:
        print_exc()
        ok = False
    return ok
    

def load_cities():
    cities = []
    try: cities = json.loads( open( weatherworld_json ).read() )
    except: print_exc()
    if not cities:
        if xbmc is not None:
            xbmc.executebuiltin( "SetProperty(totals,Loading...)" )
        cities = get_cities()
        ok = save_cities( cities )

    return cities


if __name__ == "__main__":
    cities = load_cities()
