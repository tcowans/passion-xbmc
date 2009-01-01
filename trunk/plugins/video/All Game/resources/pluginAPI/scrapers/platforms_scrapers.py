
import os
import re
import sys
import urllib
from urlparse import urljoin

from constants_scrapers import *


PLATFORMS_URL = "http://www.allgame.com/cg/agg.dll?p=agg&sql=9:"
PLATFORMS_OVERVIEW = "~T0"
PLATFORMS_GAMES = "~T1"
PLATFORMS_TECHNICAL_SPECS = "~T2"


def get_platforms_listed( url ):
    html = get_html_source( url )
    REGEXP = '<table id="platform_list" .*?>.*?</table>'
    list_items = []
    for count, contents in enumerate( re.compile( REGEXP, re.DOTALL ).findall( html ) ):
        try:
            style = re.compile( '<td class="grid_heading">(.*?)</td>' ).findall( contents )[ 0 ]
            platforms = re.compile( '<a href="(.*?)">(.*?)</a>' ).findall( contents )
            for items in platforms:
                ID = get_item_id( items[ 0 ] )
                list_items.append( { "ID": ID, "style": style, "platform": items[ 1 ], "urlsource": items[ 0 ] } )
        except:
            EXC_INFO( LOG_ERROR, sys.exc_info() )
    return list_items


def get_platform_overview( url ):
    html = get_html_source( url )
    try:
        tbn = re.compile( '<td valign="top"><img src="(.*?)".*?>' ).findall( html )[ 0 ]
    except:
        tbn = ""
        #EXC_INFO( LOG_ERROR, sys.exc_info() )
    try:
        REGEXP = '<td align="left" class="title">Description</td>.*?<p>(.*?)</p>'
        description = re.compile( REGEXP ).findall( html )[ 0 ]
        description = set_pretty_formatting( description )
    except:
        description = ""#"No description provided by studio."
        #EXC_INFO( LOG_ERROR, sys.exc_info() )
    return tbn, description


def get_platform_technical_specs( url ):
    pass
