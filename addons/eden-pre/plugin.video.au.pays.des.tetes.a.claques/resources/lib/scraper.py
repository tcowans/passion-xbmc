# -*- coding: utf-8 -*-

import os
import re
import sys
import random
import urllib
from traceback import print_exc

try: SUBTITLES = sys.modules[ "__main__" ].SUBTITLES
except: SUBTITLES = ""

S01_AIRED = [ "2012-01-12", "2012-01-19", "2012-01-27", "2012-02-03", "2012-02-10", "2012-02-17", "2012-02-24", "2012-03-02" ]


class AppURLopener( urllib.FancyURLopener ):
    version = random.choice( [ "Mozilla/5.0 (Windows NT 5.1; rv:10.0) Gecko/20100101 Firefox/10.0",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.77 Safari/535.7",
        "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; .NET4.0C; .NET4.0E; .NET CLR 2.0.50727; .NET CLR 3.0.04506.648; .NET CLR 3.5.21022; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729)"
        ] )
urllib._urlopener = AppURLopener()


def get_html_source( url ):
    """ fetch the html source """
    html = ""
    try:
        if os.path.exists( url ):
            sock = open( url )
        else:
            sock = urllib.urlopen( url )

        html = sock.read()
        sock.close()
    except:
        print "Impossible d'ouvrir la page %r" % url
        print_exc()
    return html


def getSubtitle( subtitle_file, subtitle_name ):
    srt = ""
    try:
        url = subtitle_file
        txt = get_html_source( url ).strip( "\n" )

        for count, line in enumerate( txt.split( "\n" ) ):
            t1, t2, tx = line.split( ",", 2 )
            srt += "%i\n%s0 --> %s0\n%s\n\n" % ( count + 1,
                t1.strip().replace( ";", "," ),
                t2.strip().replace( ";", "," ),
                tx.strip().replace( " | ", "\n" )
                )

        file( SUBTITLES + "%s.srt" % subtitle_name, "w" ).write( srt )
        subtitle_file = SUBTITLES + "%s.srt" % subtitle_name
    except:
        print_exc()
    print subtitle_file
    return subtitle_file


def getClip( ID ):
    srt, hd, sd = "", "", ""
    try:
        url = "http://www.tetesaclaques.tv/services/xml_video/clip-%s-type-episode.xml" % ID
        html = get_html_source( url )
        srt, hd, sd = re.findall( '<subtitle_file>(.*?)</subtitle_file>.*?<high>(.*?)</high>.*?<low>(.*?)</low>', html, re.S )[ 0 ]
    except:
        print_exc()
    return srt, hd, sd


def getEpisodes( getplot=False, full=False ):
    url = "http://tetesaclaques.tv/serietele"
    html = get_html_source( url )

    regexp = '<div class="wrapCapsule.*?">.*?'
    regexp += '<a href="(.*?)" title=".*?" class="titreThumb">(.*?)<br /><span class="saison-episode">(.*?)</span></a>.*?'
    regexp += '<img src="(.*?)".*?'
    #regexp += '<div class="votes">.*?' + ( '<img src="http://tetesaclaques.tv/public/images/(.*?)".*?>' * 5 )
    regexp += '<p class="nbVoteStar">(.*?) votes</p>.*?'

    for count, item in enumerate( re.compile( regexp, re.S ).findall( html ) ):
        ep = {}
        ep[ "aired" ]      = S01_AIRED[ count ]
        try: ep[ "id" ]    = re.sub( '(.*?episode)', '', item[ 0 ] )
        except: ep[ "id" ] = item[ 0 ].split( "episode" )[ -1 ]
        ep[ "url" ]        = item[ 0 ]
        ep[ "title" ]      = item[ 1 ]
        ep[ "episode" ]    = item[ 2 ].split()[ -1 ]
        ep[ "icon" ]       = item[ 3 ]
        ep[ "rate" ]       = str( list( item[ 4:-1 ] ).count( 'starActive.png' ) )
        ep[ "votes" ]      = item[ -1 ]

        ep[ "plot" ] = ""
        if getplot or full:
            html = get_html_source( ep[ "url" ] )
            ep[ "plot" ] = "".join( re.compile( '<div id="playerInfo">.*?<p>(.*?)</p>', re.S ).findall( html ) ).replace( "\n", " " )

        ep[ "srt_url" ], ep[ "hd_url" ], ep[ "sd_url" ] = "", "", ""
        if full: ep[ "srt_url" ], ep[ "hd_url" ], ep[ "sd_url" ] = getClip( ep[ "id" ] )

        yield ep



if ( __name__ == "__main__" ):
    import time
    t1 = time.time()
    for ep in getEpisodes( 1, 1 ):
        print ep
        print
    print time.time() - t1
