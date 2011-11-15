""" convert UTC time to user local time
    by frost
"""

DATE_TIME_FORMAT = "%A, %B %d, %Y | %I:%M:%S %p"
#DATE_TIME_FORMAT = "%A, %d %B %Y | %H:%M:%S"
import os
import time
from traceback import print_exc

try:
    from xbmc import getRegion
    """ getRegion(id) -- Returns your regions setting as a string for the specified id.

        id             : string - id of setting to return

        *Note, choices are (dateshort, datelong, time, meridiem, tempunit, speedunit)

               You can use the above as keywords for arguments.

        example:
          - date_long_format = xbmc.getRegion('datelong')
    """
    DATE_TIME_FORMAT = "%s | %s" % ( getRegion( "datelong" ), getRegion( "time" ) )
except ImportError:
    pass
#print DATE_TIME_FORMAT

def utc_to_local( utc_string, format="%a, %d %b %Y %H:%M:%S GMT" ):
    try:
        # convert time in string format "%a, %d %b %Y %H:%M:%S GMT" to local time in same format
        # this works with and without daylight saving time (i.e. times obtained here
        # agree with online logbook for runs in August as well as in January)
        utctuple = time.mktime( time.strptime( utc_string, format ) )
        # there is no routine to convert UTC time strings. It is always assumed
        # that the string contains local time. Therefore we have to convert it
        # assuming that it is local time, and then correct the time zone afterwards.
        # In order to do that, we get the difference of UTC and local time in seconds
        # here.
        secdiff = 0#time.mktime( time.gmtime( utctuple ) ) - time.mktime( time.localtime( utctuple ) )
        # Then we subtract that difference from the pseudo-local time we get
        utcsecs = time.mktime( time.localtime( utctuple ) ) - secdiff
        # Now we have real UTC time and can convert that into a local time string
        return time.strftime( DATE_TIME_FORMAT, time.localtime( utcsecs ) )
    except:
        print_exc()
        return utc_string

def setTimeFormat( t_string="", format="%d/%m/%Y %H:%M", styles="datelong,time", sep=" | " ):
    # style choices are (dateshort, datelong, time, meridiem, tempunit, speedunit)
    try:
        r1, r2 = styles.split( "," )
        new_format = sep.join( [ xbmc.getRegion( r1 ), xbmc.getRegion( r2 ) ] )
    except:
        new_format = "%A, %B %d, %Y | %I:%M:%S %p"
    t_tuple = time.mktime( time.strptime( t_string, format ) )
    t_secs  = time.mktime( time.localtime( t_tuple ) )
    return  time.strftime( new_format, time.localtime( t_secs ) )

if __name__ == "__main__":
    print setTimeFormat( "06/10/2010 14:44" )
    print utc_to_local( 'Mon, 27 Sep 2010 22:31:58 GMT' )
