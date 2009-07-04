
import os
import re
import sys
import urllib
from urlparse import urljoin


__all__ = [
    # public symbols
    "MAXIMUM_TRAILERS",
    "IS_CANCELED",
    "get_trailers",
    ]


# THIS TWO GLOBALS VARIABLES IS REQUIERED
MAXIMUM_TRAILERS = 0 # 0 == UNLIMITED
IS_CANCELED = None


SEARCH_ON_GAMEVIDEOS_COM = "http://gamevideos.1up.com/video/search?page=%s&searchQuery=%s"
#SEARCH_ON_GAMEVIDEOS_COM = "http://www.gamevideos.com/video/search?page=%s&searchQuery=%s"#&querySort=&frag=list&dojo.transport=xmlhttp&"
PLAYER_GAMEVIDEOS_COM = "http://www.gamevideos.com/video/videoListXML?id=%s"


try: from resources.pluginAPI.plugin_log import *
except:
    LOG_ERROR = 0
    from traceback import print_exc
    def EXC_INFO( *args ): print_exc()
    LOG = EXC_INFO
    #EXC_INFO( LOG_ERROR, sys.exc_info() )


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


def get_total_pages( html ):
    try:
        total = re.findall( ' out of (\d{1,6})', html )[ 0 ]
        estimate = eval( total + "/7" )
        if estimate < total: estimate += 1
        if MAXIMUM_TRAILERS:
            estimate2 = MAXIMUM_TRAILERS / 7
            if ( estimate2 * 7 ) < MAXIMUM_TRAILERS:
                estimate2 += 1
            if estimate2 < estimate:
                return estimate2
        return estimate
    except:
        return 1


def find_trailer( trailer_id ):
    try:
        trailer_source = get_html_source( PLAYER_GAMEVIDEOS_COM % ( trailer_id, ) )
        real_source = re.compile( '<entry id.*? href="(.*?)"' ).findall( trailer_source )[ 0 ]
        return real_source
    except:
        pass#EXC_INFO( LOG_ERROR, sys.exc_info() )
    return ""#[]


def get_trailers( game_name, report_progress=None ):
    trailers = []
    #THUMBS = re.compile( '<div class="gameimage">.*?<img src="(.*?)" .*?</div>', re.DOTALL )
    #ID_TITLE = re.compile( 'playVideo[(]event,(\d{1,6})[)]" class="game">(.*?)</a>' )
    #RUNTIME = re.compile( '\t(\d{1,2}:\d{1,2})&nbsp;' )
    #SUMMARY = re.compile( '<span class="summary">(.*?)</span>' )

    game_name = urllib.quote( game_name )
    #print game_name
    html = get_html_source( SEARCH_ON_GAMEVIDEOS_COM % ( "1", game_name ) )
    total_pages = get_total_pages( html )
    if report_progress: report_progress( 1, total_pages, ispage=True )

    PATTERN = '<div class="gameimage">.*?<img src="(.*?)" .*?</div>.*?playVideo[(]event,(\d{1,6})[)]" class="game">(.*?)</a>.*?\t(\d{1,2}:\d{1,2})&nbsp;.*?<span class="summary">(.*?)</span>'
    #print re.compile( PATTERN, re.DOTALL ).findall( html )
    trailers += re.compile( PATTERN, re.DOTALL ).findall( html )#zip( THUMBS.findall( html ), ID_TITLE.findall( html ), SUMMARY.findall( html ) )

    if total_pages > 1:
        for i in range( 2, total_pages + 1 ):
            if IS_CANCELED: break
            html = get_html_source( SEARCH_ON_GAMEVIDEOS_COM % ( str( i ), game_name ) )
            trailers += re.compile( PATTERN, re.DOTALL ).findall( html )#zip( THUMBS.findall( html ), ID_TITLE.findall( html ), SUMMARY.findall( html ) )
            #print re.compile( PATTERN, re.DOTALL ).findall( html )
            if report_progress: report_progress( i, total_pages, ispage=True )
            if MAXIMUM_TRAILERS and ( ( i * 7 ) >= MAXIMUM_TRAILERS ):
                trailers = trailers[ :MAXIMUM_TRAILERS ]
                break

    # now set en dict ('/img/screen_none.gif', '7747', 'Fable', '5:58', 'Graveyard Fight')
    trailers_contents = []#{}
    total_trailers = len( trailers )
    for count, trailer in enumerate( trailers ):
        if IS_CANCELED: break
        try:
            label = trailer[ 2 ]#trailer[ 1 ][ 1 ]
            label2 = trailer[ 4 ]#trailer[ 2 ]
            icon = ""
            thumb = trailer[ 0 ].replace( " ", "%20" )#urljoin( "http://www.gamevideos.com", trailer[ 0 ].replace( " ", "%20" ) )
            video = find_trailer( trailer[ 1 ] )#[ 0 ] )
            duration = trailer[ 3 ]
            contents = { "label": label, "label2": label2, "icon": icon, "thumb": thumb, "video": video, "duration": duration }
            #trailers_contents[ count ] = contents
            trailers_contents.append( contents )
            if report_progress: report_progress( ( count + 1 ), total_trailers, label, ispage=False, contents=contents )
        except:
            total_trailers -= 1
            EXC_INFO( LOG_ERROR, sys.exc_info() )
    return trailers_contents


def report_progress( *args, **kwargs ):
    print ( 100.0 / args[ 1 ] ) * args[ 0 ], "%"
    if kwargs[ "ispage" ]:
        print "Fetching Page %i of %i" % ( args[ 0 ], args[ 1 ], )
    else:
        print "Fetching Trailer %i of %i" % ( args[ 0 ], args[ 1 ], )
        print "Title:", args[ 2 ]
    print
    #print


if ( __name__ == "__main__" ):
    import time
    t1 = time.ctime()
    #print get_trailers( "fable" , report_progress=report_progress )
    print get_trailers( "doom 4" , report_progress=report_progress )
    print t1
    print time.ctime()
