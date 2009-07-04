
import os
import re
import sys
import urllib
from urlparse import urljoin

from constants_scrapers import *


RELEASES_URL = "http://www.allgame.com/cg/agg.dll?p=agg&sql=23:%i"
RECENT, UPCOMING, FUTURE = range( 0, 3 )


def get_releases_listed( url ):
    html = get_html_source( url )
    REGEXP = 'style="width:214px;word-wrap:break-word;"><a href="(.*?)">(.*?)</a></TD><TD class="cell">&nbsp;</TD><TD class="cell" style="width:138;word-wrap:break-word;">(.*?)</TD><TD class="cell" style="width:70px;word-wrap:break-word;">(.*?)</TD><TD class="cell" style="width:114px;word-wrap:break-word;">(.*?)</TD><TD class="cell" style="width:156;word-wrap:break-word;">(.*?)</TD></tr><div class="expand"></div>'
    list_items = []
    for count, items in enumerate( re.compile( REGEXP, re.DOTALL ).findall( html ) ):
        try:
            ID = get_item_id( items[ 0 ] )
            urlsource = urljoin( RELEASES_URL, items[ 0 ] ).replace( "&amp;", "&" )
            try: year = int( re.findall( "(\d{4})", items[ 2 ] )[ 0 ] )
            except: year = 0
            list_items.append( { "ID": ID, "title": items[ 1 ], "year": year, "release_date": items[ 2 ], "genre": items[ 3 ], "style": items[ 4 ], "platform": items[ 5 ], "urlsource": urlsource } )
        except:
            EXC_INFO( LOG_ERROR, sys.exc_info() )
    return list_items



if ( __name__ == "__main__" ):
    import time
    from games_scrapers import *
    t1 = time.ctime()
    games_listed = get_releases_listed( RELEASES_URL % ( FUTURE, ) )
    print len( games_listed )
    raise
    for count, release in enumerate( games_listed ):
        print ( count + 1 ), release[ "title" ]
        release_infos = get_game_overview( release[ "urlsource" ] )
        release.update( release_infos )
        other_infos = get_other_game_infos( release[ "buttons_listed" ], release[ "urlsource" ] )
        release.update( other_infos )
        for key, value in sorted( release.items() ):
            print key, "=", value
        print
        if count == 1: break
    print t1
    print time.ctime()
