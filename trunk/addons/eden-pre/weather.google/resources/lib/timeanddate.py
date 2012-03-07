
import re
import random
import urllib
import urllib2
from gzip import GzipFile
from StringIO import StringIO
from datetime import datetime
from time import mktime, time
from traceback import print_exc

try:
    import xbmc
    from xbmcgui import Window
    from xbmcaddon import Addon
    Addon = Addon( "weather.google" )
    WEATHER_WINDOW = Window( 12600 )
    LangXBMC = xbmc.getLocalizedString  # XBMC strings
    USER_TIME_FORMAT = xbmc.getRegion( "time" ).replace( ':%S', '', 1 )
    DATE_LONG_FORMAT = xbmc.getRegion( "datelong" )
except:
    # NOT RUNNING ON XBMC, ON DEV
    WEATHER_WINDOW   = None
    USER_TIME_FORMAT = '%I:%M %p'
    DATE_LONG_FORMAT = '%A, %B %d, %Y'
    def LangXBMC( id ): return ""


BASE_URL = "http://timeanddate.com/worldclock/astronomy.html"

HTTP_USER_AGENT = random.choice( [ "Mozilla/5.0 (Windows NT 5.1; rv:10.0.2) Gecko/20100101 Firefox/10.0.2",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.77 Safari/535.7",
    "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; .NET4.0C; .NET4.0E; .NET CLR 2.0.50727; .NET CLR 3.0.04506.648; .NET CLR 3.5.21022; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729)"
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

MONTHS = [ "", "jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec" ]

DAY_MONTH_ID_LONG = {
    "Monday":    11,
    "Tuesday":   12,
    "Wednesday": 13,
    "Thursday":  14,
    "Friday":    15,
    "Saturday":  16,
    "Sunday":    17,
    "January":   21,
    "February":  22,
    "March":     23,
    "April":     24,
    "May":       25,
    "June":      26,
    "July":      27,
    "August":    28,
    "September": 29,
    "October":   30,
    "November":  31,
    "December":  32,
    }

DAY_MONTH_ID_SHORT = {
    "Monday":    41,
    "Tuesday":   42,
    "Wednesday": 43,
    "Thursday":  44,
    "Friday":    45,
    "Saturday":  46,
    "Sunday":    47,
    "January":   51,
    "February":  52,
    "March":     53,
    "April":     54,
    "May":       55,
    "June":      56,
    "July":      57,
    "August":    58,
    "September": 59,
    "October":   60,
    "November":  61,
    "December":  62,
    }

class _urlopener( urllib.FancyURLopener ):
    version = HTTP_USER_AGENT
urllib._urlopener = _urlopener()


def translate_date( str_date, format="long" ):
    dict = ( DAY_MONTH_ID_SHORT, DAY_MONTH_ID_LONG )[ format == "long" ]
    def lang( s ):
        s = s.group( 1 )
        id = dict.get( s )
        if id: s = LangXBMC( id ) or s
        return s
    #str_date = unicode( str_date, 'utf-8', errors='ignore' )
    try: return re.sub( '(%s)' % '|'.join( dict ), lambda s: lang( s ), str_date )
    except: print_exc()
    return str_date


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


def trim_time( str_time ):
    if str_time.startswith( "0" ):
        str_time = str_time[ 1: ]
    return str_time


def get_user_time_format( str_time="5:31 PM" ):
    f_time = time()
    try:
        str_dt = str_time.lower().split()
        if str_dt[ -1 ] not in [ "pm", "am" ]:
            T, P = str_dt + [ "" ]
        else:
            T, P = str_dt
        if T.count( ":" ) == 1:
            H, M = T.split( ":" )
        else:
            H, M, S = T.split( ":" )

        dt = datetime.now()
        dt = dt.replace( hour=int( H ), minute=int( M ), second=0, microsecond=0 )

        hour = ( dt.hour, dt.hour+12 )[ P == "pm" ]
        hour = ( hour, dt.hour-12 )[ P == "am" ]
        try: dt = dt.replace( hour=hour )
        except ValueError: pass

        #17:31
        str_time = dt.strftime( USER_TIME_FORMAT )
        #convert a datetime object into a Unix time stamp
        f_time = mktime( dt.timetuple() ) + 1e-6 * dt.microsecond
    except:
        if str_time:
            print "str_time: %r" % str_time
            print_exc()
    return f_time, trim_time( str_time )


def get_user_datetime_format( str_datetime="Wednesday, February 29, 2012 at 1:58:19 PM" ):
    f_time = time()
    try:
        str_dt = str_datetime.lower().replace( ",", "" ).replace( "at", "" ).split()
        if str_dt[ -1 ] not in [ "pm", "am" ]:
            A, D, B, Y, T, P = str_dt + [ "" ]
        else:
            A, B, D, Y, T, P = str_dt
        B = MONTHS.index( B[ :3 ] )
        H, M, S = T.split( ":" )

        dt = datetime( int( Y ), B, int( D ), int( H ), int( M ), int( S ) )

        hour = ( dt.hour, dt.hour+12 )[ P == "pm" ]
        hour = ( hour, dt.hour-12 )[ P == "am" ]
        try: dt = dt.replace( hour=hour )
        except ValueError: pass

        #Wednesday, 29 February 2012 | 23:58:42
        str_datetime = "%s | %s" % ( dt.strftime( DATE_LONG_FORMAT ), trim_time( dt.strftime( USER_TIME_FORMAT ) ) )
        #convert a datetime object into a Unix time stamp
        f_time = mktime( dt.timetuple() ) + 1e-6 * dt.microsecond
    except:
        if str_datetime:
            print "str_datetime: %r" % str_datetime
            print_exc()
    return f_time, str_datetime


def get_current_local_time_in( countryId=189 ):
    # get real current time of countryId or except local time and return value of in broad daylight
    f_time = time()
    local_time = datetime.now().strftime( "%s | %s" % ( DATE_LONG_FORMAT, USER_TIME_FORMAT ) )
    try:
        html = get_html_source( "http://timeanddate.com/worldclock/city.html?n=" + str( countryId ) )
        current_time = re.search( '<strong id=ct.*?class=big>(.*?)</strong>', html )
        if current_time:
            f_time, local_time = get_user_datetime_format( current_time.group( 1 ) )
            #print current_time.group( 1 )
    except:
        print_exc()
    return f_time, translate_date( local_time )


from decimal import Decimal
def convert_distance( km, i_unit=0 ):
    """
    kilometres (km)         1
    miles (mi)              0.621371192
    Astronomical units (AU) 0.0000000067
    Light Years (l.y.)      0.00000000000011
    Parsec (pc)             0.000000000000033
    """

    dist = km
    if   i_unit == 1: dist = eval( "0.621371192*dist" )
    elif i_unit == 2: dist = eval( "0.0000000067*dist" )
    elif i_unit == 3: dist = eval( "0.00000000000011*dist" )
    elif i_unit == 4: dist = eval( "0.000000000000033*dist" )
    else: i_unit = 0

    dist = Decimal( str( dist ) ) + Decimal( "0.0" )

    s, v = str( dist ).split( "." )
    s = list( s )[ ::-1 ]
    for i in range( 3, len( s ), 4 ): s.insert( i, " " )
    dist = ( "".join( s[ ::-1 ] ) + "." + v ).lower()
    if "e-" in dist:
        s = dist.split( "e-" )
        dist = "0." + ( "0" * ( int( s[ 1 ] ) - 1 ) ) + s[ 0 ].replace( ".", "" )
    units = [ "(km)", "(mi)", "(AU)", "(l.y.)", "(pc)" ]
    return dist, units[ i_unit ]


def get_default_sun():
    f_sunrise, sun_up  = get_user_time_format( "6:00 AM" )
    f_sunset, sun_down = get_user_time_format( "8:00 PM" )
    sun_day  = {
        "Current.AstroTwilight.Start":  sun_up,
        "Current.AstroTwilight.End":    sun_down,
        "Current.NauticTwilight.Start": sun_up,
        "Current.NauticTwilight.End":   sun_down,
        "Current.CivilTwilight.Start":  sun_up,
        "Current.CivilTwilight.End":    sun_down,
        "Current.Sunrise":              sun_up,
        "Current.Sunset":               sun_down,
        "Current.Sunrise.Azimuth":      "N/A",
        "Current.Sunset.Azimuth":       "N/A",
        "Current.Sun.Length":           "14h 0m 0s",
        "Current.Sun.Diff":             "0m 0s",
        "Current.Solarnoon.Time":       "N/A",
        "Current.Solarnoon.Altitude":   "N/A",
        "Current.Solarnoon.Distance":   "N/A",
        "In.Broad.Daylight":            repr( f_sunrise <= time() <= f_sunset ).lower(),
        "Current.Location.LocalTime":   translate_date( datetime.now().strftime( "%s | %s" % ( DATE_LONG_FORMAT, USER_TIME_FORMAT ) ) ),
        }
    return sun_day

def get_sun( countryId=189, i_unit=0 ):
    sun_day = get_default_sun()
    try:
        url = BASE_URL + "?n=%i&obj=sun&afl=-1" % int( countryId )
        #url += strftime( '&month=%m&year=%Y&day=%d', localtime( time() ) )
        html = get_html_source( url )#, "astronomy.html" )

        regexp = '<tr class=c.*?><td>(.*?)</td><td>(.*?)</td><td>(.*?)</td><td>(.*?)</td><td>(.*?)</td><td>(.*?)</td><td>(.*?)</td><td>(.*?)</td><td>(.*?)</td><td>(.*?)&deg;<img.*?</td><td>(.*?)&deg;<img.*?</td><td>(.*?)</td><td>(.*?)</td><td>(.*?)</td><td>(.*?)&deg;.*?</td><td>(.*?)</td></tr>'

        sun = re.search( regexp, html ).groups()

        f_sunrise, sun_up  = get_user_time_format( sun[ 7 ] )
        f_sunset, sun_down = get_user_time_format( sun[ 8 ] )
        f_time, local_time = get_current_local_time_in( countryId )
        sun_day.update( {
            "In.Broad.Daylight":            repr( f_sunrise <= f_time <= f_sunset ).lower(), # en plein jour
            "Current.Location.LocalTime":   local_time,                             # real current time of countryId
            "Current.AstroTwilight.Start":  get_user_time_format( sun[ 1 ] )[ 1 ],  # Astronomical Twilight : starts
            "Current.AstroTwilight.End":    get_user_time_format( sun[ 2 ] )[ 1 ],  # Astronomical Twilight : ends
            "Current.NauticTwilight.Start": get_user_time_format( sun[ 3 ] )[ 1 ],  # Nautical Twilight : starts
            "Current.NauticTwilight.End":   get_user_time_format( sun[ 4 ] )[ 1 ],  # Nautical Twilight : ends
            "Current.CivilTwilight.Start":  get_user_time_format( sun[ 5 ] )[ 1 ],  # Civil Twilight : starts
            "Current.CivilTwilight.End":    get_user_time_format( sun[ 6 ] )[ 1 ],  # Civil Twilight : ends
            "Current.Sunrise":              sun_up,                                 # Sunrise
            "Current.Sunset":               sun_down,                               # Sunset
            "Current.Sunrise.Azimuth":      sun[ 9 ],                               # Azimuth : Sunrise
            "Current.Sunset.Azimuth":       sun[ 10 ],                              # Azimuth : Sunset
            "Current.Sun.Length":           sun[ 11 ],                              # Length of day : This day
            "Current.Sun.Diff":             sun[ 12 ].replace( "&#8722;", "-" ),    # Length of day : Difference
            "Current.Solarnoon.Time":       get_user_time_format( sun[ 13 ] )[ 1 ], # Solar noon : Time
            "Current.Solarnoon.Altitude":   sun[ 14 ],                              # Solar noon : Altitude
            "Current.Solarnoon.Distance":   sun[ 15 ] + " (10**6 km)",              # Solar noon : Distance (10**6 km)
            } )
        try:
            dist, unit = convert_distance( eval( "int(%s*10**6)-660000" % sun[ 15 ] ), i_unit )
            if not dist: dist = ""
            else: dist = " ".join( [ dist, unit ] )
            sun_day[ "Current.Solarnoon.Distance" ] = dist
        except ValueError:
            moon_day[ "Current.Solarnoon.Distance" ] = ""
        except: print_exc()
    except:
        print_exc()
    return sun_day


def get_default_moon():
    return {
        "Current.Moonrise":                  "N/A",
        "Current.Moonset":                   "N/A",
        "Current.Moonrise.Azimuth":          "N/A",
        "Current.Moonset.Azimuth":           "N/A",
        "Current.Moon.Meridian.Time":        "N/A",
        "Current.Moon.Meridian.Altitude":    "N/A",
        "Current.Moon.Meridian.Distance":    "N/A",
        "Current.Moon.Meridian.Illuminated": "N/A",
        "Current.Moon.Phase":                "N/A",
        }

def get_moon( countryId=189, i_unit=0 ):
    moon_day = get_default_moon()
    try:
        url = BASE_URL + "?n=%i&obj=moon&afl=-1" % int( countryId )
        html = get_html_source( url )#, "moon.html" )

        regexp = '<tr class=c.*?>(.*?)</tr>'
        for day in re.compile( regexp ).findall( html )[ :1 ]:
            day = re.sub( "(-<br>|<br>-|&deg;)", "", day )
            moon = re.compile( '<td>(.*?)</td>' ).findall( day )
            moon_day.update( {
                "Current.Moonrise":                  get_user_time_format( moon[ 1 ].strip() )[ 1 ],  # Moonrise
                "Current.Moonset":                   get_user_time_format( moon[ 2 ].strip() )[ 1 ],  # Moonset
                "Current.Moonrise.Azimuth":          moon[ 3 ].strip().split( "<img" )[ 0 ],          # Azimuth-Moonrise (degree)
                "Current.Moonset.Azimuth":           moon[ 4 ].strip().split( "<img" )[ 0 ],          # Azimuth-Moonset (degree)
                "Current.Moon.Meridian.Time":        get_user_time_format( moon[ 5 ].strip() )[ 1 ],  # Meridian Passing : Time
                "Current.Moon.Meridian.Altitude":    moon[ 6 ].strip(),                               # Meridian Passing : Altitude (degree)
                "Current.Moon.Meridian.Distance":    moon[ 7 ].strip().replace( ",", " " ) + " (km)", # Meridian Passing : Distance (km)
                "Current.Moon.Meridian.Illuminated": moon[ 8 ].strip(),                               # Meridian Passing : Illuminated (percent)
                } )
            # Phase
            phase_at = moon[ 9 ].strip().split( " at " )
            if phase_at != ['']: phase_at = [ phase_at[ 0 ], get_user_time_format( phase_at[ 1 ] )[ 1 ] ]
            moon_day[ "Current.Moon.Phase" ] = ", ".join( phase_at ) # Phase of moon and time
            try:
                dist, unit = convert_distance( int( moon[ 7 ].strip().replace( ",", "" ) ), i_unit )
                if not dist: dist = ""
                else: dist = " ".join( [ dist, unit ] )
                moon_day[ "Current.Moon.Meridian.Distance" ] = dist
            except ValueError:
                moon_day[ "Current.Moon.Meridian.Distance" ] = ""
            except: print_exc()
    except:
        print_exc()
    return moon_day


def get_countries_id( country="Quebec City, QC" ):
    countries = []
    #
    try: query = urllib.quote_plus( country.encode( "utf-8" ) )
    except: query = urllib.quote_plus( country )
    url = BASE_URL + "?query=" + query
    #print url
    sock = urllib.urlopen( url )
    real_url = sock.geturl()
    #print real_url
    ID = re.search( ".*?=(\\d+)", real_url )
    if ID:
        countries.append( ( ID.group( 1 ), country ) )
        sock.close()
    else:
        html = sock.read()
        sock.close()
        for city in re.compile( '<tr class=.*?><td><a href=".*?=(\\d+)">(.*?)</a></td><td>(.*?)</td><td>(.*?)</td></tr>' ).findall( html ):
            countries.append( ( city[ 0 ], ", ".join( [ c for c in city[ 1: ] if c ] ) ) )
    #
    return countries



def SetProperty( key, value="" ):
    if WEATHER_WINDOW:
        WEATHER_WINDOW.setProperty( key, value )
    else:
        # for test print
        print key, value

def SetProperties( loc_index=None ):
    in_broad_daylight = True
    try:
        if loc_index is None:
            loc_index = Addon.getSetting( 'currentlocation' )
        ID = Addon.getSetting( 'areacode%s_code' % loc_index )
        i_unit = int( Addon.getSetting( "dist_unit" ) )

        sun = get_sun( ID, i_unit )
        in_broad_daylight = ( sun.get( "In.Broad.Daylight" ) == "true" )
        for key, value in sun.items():
            SetProperty( key, value )

        for key, value in get_moon( ID, i_unit ).items():
            SetProperty( key, value )

        SetProperty( "Weather.ExtraIsFetched", "true" )
    except:
        print_exc()
    return in_broad_daylight



def test():
    import json
    #print json.dumps( get_countries_id(), sort_keys=True, indent=2 )
    #return
    country = "New York, NY"
    countries = get_countries_id( country )
    totals = len( countries )

    if not totals:
        print "errors getting countries for %r" % country

    elif totals == 1:
        ID, city = countries[ 0 ]
        print city
        print "SUN", json.dumps( get_sun( ID ), sort_keys=True, indent=2 )
        print "MOON", json.dumps( get_moon( ID ), sort_keys=True, indent=2 )

    else:
        import random
        ID, city = random.choice( countries )
        print city
        print "SUN", json.dumps( get_sun( ID ), sort_keys=True, indent=4 )
        print "MOON", json.dumps( get_moon( ID ), sort_keys=True, indent=4 )

    print "-"*100


if __name__ == "__main__":
    #test()
    SetProperties()
