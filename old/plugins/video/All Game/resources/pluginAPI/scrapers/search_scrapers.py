
import os
import re
import sys
import urllib
from urlparse import urljoin

from constants_scrapers import *


SEARCH_URL = "http://www.allgame.com/cg/agg.dll?p=agg&sql=31:%s"


def get_search_games_listed( url ):
    html = get_html_source( url )

    games_listed = []
    games = re.compile( '<tr class="visible" id="trlink" onclick=".*?">.*?</tr>', re.DOTALL ).findall( html )
    for count, item in enumerate( games ):
        try:
            uri, title = re.findall( '<a href="(.*?)">(.*?)</a>', item )[ 0 ]
            urlsource = urljoin( url, uri ).replace( "&amp;", "&" )
            ID = get_item_id( urlsource )
            title = set_pretty_formatting( title ).strip().replace( "&amp;", "&" )
            regexp_style_platform = re.findall( '<TD class=".*?" style=".*?">(.*?)</TD>', item )
            try:
                style = regexp_style_platform[ 3 ].strip()
                if ( "&nbsp;" or ';">' ) in style:
                    style = re.findall( '.*">(.*?)$', style )[ 0 ].strip()
            except: style = ""
            try:
                platform = regexp_style_platform[ -1 ].strip()
                if ( "&nbsp;" or ';">' ) in platform:
                    platform = re.findall( '.*">(.*?)$', platform )[ 0 ].strip()
            except: platform = ""
            try: year = int( re.findall( ">(\d{1,4})<", item )[ 0 ] )
            except: year = 0
            try: amg_rating = re.findall( 'st_r(\d{1,4})', item )[ 0 ]
            except: amg_rating = ""
            games_listed.append( { "ID": ID, "platform": platform, "style": style, "title": title, "amg_rating": amg_rating, "year": year, "urlsource": urlsource } )
        except:
            EXC_INFO( LOG_ERROR, sys.exc_info() )
    return games_listed


if ( __name__ == "__main__" ):
    import time
    t1 = time.ctime()
    GAME_SEARCH = "driver"
    games_listed = get_search_games_listed( SEARCH_URL % ( "|".join( GAME_SEARCH.split() ), ) )
    #raise
    from games_scrapers import *
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
