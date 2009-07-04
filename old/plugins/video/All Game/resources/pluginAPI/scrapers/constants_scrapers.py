
import os
import re
import sys
import urllib


BASE_URL = "http://www.allgame.com"
ESRB_IMG = BASE_URL + "/img/esrb/"


try: from resources.pluginAPI.plugin_log import *
except:
    LOG_ERROR = 0
    from traceback import print_exc
    def EXC_INFO( *args ): print_exc()
    LOG = EXC_INFO
    #EXC_INFO( LOG_ERROR, sys.exc_info() )


def set_pretty_formatting( text, by="" ):
    text = text.replace( "<br />", "\n" )
    text = text.replace( "<i>", "[I]" ).replace( "</i>", "[/I]" )
    text = text.replace( "<b>", "[B]" ).replace( "</b>", "[/B]" )
    text = re.sub( "(?s)</[^>]*>", "[/B]", text )
    text = re.sub( "(?s)<[^>]*>", "[B]", text )
    return text


def strip_off( text, by="" ):
    #text = text.replace( "[", "<" ).replace( "]", ">" )
    return re.sub( "(?s)<[^>]*>", by, text )


def get_item_id( item ):
    return re.findall( ':(\d{1,9})', item )[ 0 ]


def get_html_source( url ):
    """ fetch the html source """
    try:
        if os.path.isfile( url ): sock = open( url, "r" )
        else: sock = urllib.urlopen( url )
        htmlsource = sock.read()
        sock.close()
        htmlsource = htmlsource.replace( "\r", "" )
        return htmlsource
    except:
        EXC_INFO( LOG_ERROR, sys.exc_info() )
        return ""
