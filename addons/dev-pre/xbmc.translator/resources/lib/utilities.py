"""
    by frost (passion-xbmc.org)
"""

#Modules General
import os
import time
from traceback import print_exc

try:
    import xbmc
except ImportError:
    xbmc = None

AddonId = "xbmc.translator"

log_levels = [ "debug", "info", "notice", "warning", "error", "severe", "fatal", "none" ]
def LOG( level, format, *args ):
    level = level or "debug"
    try:
        line = "[%s] %s" % ( AddonId, format % args, )
        if xbmc:
            xbmc.log( line.strip( "\r\n" ), log_levels.index( level ) )
        else: 
            print line
    except:
        print_exc()


def time_took( t ):
    t = ( time.time() - t )
    if t >= 60: return "%.3fm" % ( t / 60.0 )
    return "%.3fs" % ( t )


def fixe_line_return( text, reverse=False ):
    try:
        if reverse:
            text = text.replace( "¶", "[CR]" )
        else:
            try:
                text = text.replace( "[CR]", unichr( 182 ) )
                text = text.replace( "\r\n", unichr( 182 ) )
                text = text.replace( "\r",   unichr( 182 ) )
                text = text.replace( "\n",   unichr( 182 ) )
            except:
                text = text.replace( "[CR]", "¶" )
                text = text.replace( "\r\n", "¶" )
                text = text.replace( "\r",   "¶" )
                text = text.replace( "\n",   "¶" )
    except:
        print locals()
        print_exc()
    return text
