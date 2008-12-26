"""
convert UTC time to user local time

frost
"""

import re
import time


def utc_to_local( utc_string ):
    # convert time in string format "%Y-%m-%d %H:%M:%S" to local time in same format
    # this works with and without daylight saving time (i.e. times obtained here
    # agree with online logbook for runs in August as well as in January)
    utctuple = time.mktime( time.strptime( utc_string, "%Y-%m-%d %H:%M:%S" ) )
    # there is no routine to convert UTC time strings. It is always assumed
    # that the string contains local time. Therefore we have to convert it
    # assuming that it is local time, and then correct the time zone afterwards.
    # In order to do that, we get the difference of UTC and local time in seconds
    # here.
    secdiff = time.mktime( time.gmtime( utctuple ) ) - time.mktime( time.localtime( utctuple ) )
    # Then we subtract that difference from the pseudo-local time we get
    utcsecs = time.mktime( time.localtime( utctuple ) ) - secdiff
    # Now we have real UTC time and can convert that into a local time string
    #return time.strftime( "%Y-%m-%d %H:%M:%S", time.localtime( utcsecs ) )
    return time.strftime( "%d-%m-%y %H:%M:%S", time.localtime( utcsecs ) )


# Day Of Week
REGEXP = '((?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday|Tues|Thur|Thurs|Sun|Mon|Tue|Wed|Thu|Fri|Sat)).*?'
# Day
REGEXP += '((?:(?:[0-2]?\\d{1})|(?:[3][0,1]{1})))(?![\\d]).*?'
# Month
REGEXP += '((?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:t|ember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)).*?'
# Year
REGEXP += '((?:(?:[1]{1}\\d{1}\\d{1}\\d{1})|(?:[2]{1}\\d{3})))(?![\\d]).*?'
# HourMinuteSec
REGEXP += '((?:(?:[0-1][0-9])|(?:[2][0-3])|(?:[0-9])):(?:[0-5][0-9])(?::[0-5][0-9])?(?:\\s?(?:am|AM|pm|PM))?)'

def set_local_time( utc_string ):
    try:
        _ = re.compile( REGEXP, re.IGNORECASE | re.DOTALL ).search( utc_string )
        if _:
            _dayofweek = _.group( 1 )
            _day = _.group( 2 )
            _month = str( "Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec".split( "|" ).index( _.group( 3 ) ) + 1 )
            _year = _.group( 4 )
            _time = _.group( 5 )
            utc_string = "%s, %s" % ( _dayofweek, utc_to_local( "%s-%s-%s %s" % ( _year, _month, _day, _time ) ), )
    except:
        pass
    return utc_string


if __name__ == "__main__":
    passion_gmt = 'Sat, 22 Jan 2008 12:10:53 GMT'
    print passion_gmt
    print set_local_time( passion_gmt )
    passion_gmt = 'Sat, 22 Jan 2008 00:10:53 GMT'
    print passion_gmt
    print set_local_time( passion_gmt )
