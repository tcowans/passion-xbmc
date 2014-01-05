# -*- coding: utf-8 -*-

import os
import re
import sys
import random
import urllib
from traceback import print_exc

try:
    xbmcvfs   = sys.modules[ "__main__" ].xbmcvfs
    SUBTITLES = sys.modules[ "__main__" ].SUBTITLES
except:
    xbmcvfs   = None
    SUBTITLES = ""

S01_AIRED = [ "2012-01-12", "2012-01-19", "2012-01-27", "2012-02-03", "2012-03-02", "2012-04-06", "2012-05-04", "2012-06-01" ]


class AppURLopener( urllib.FancyURLopener ):
    version = random.choice( [ "Mozilla/5.0 (Windows NT 5.1; rv:12.0) Gecko/20100101 Firefox/12.0",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.77 Safari/535.7"
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
            #print sock.geturl()
            #print sock.info()

        html = sock.read()
        sock.close()
    except:
        print "Impossible d'ouvrir la page %r" % url
        print_exc()
    return html


def getSubtitle( subtitle_file, subtitle_name ):
    srt = ""
    try:
        txt = get_html_source( subtitle_file )
        if not re.search( '<title>(Err.*?404.*?tetesaclaques.tv)</title>', txt ):
            srt = txt.replace( "\r", "" ).strip( "\n" )

            #for count, line in enumerate( txt.split( "\n" ) ):
            #    t1, t2, tx = line.split( ",", 2 )
            #    srt += "%i\n%s0 --> %s0\n%s\n\n" % ( count + 1,
            #        t1.strip().replace( ";", "," ),
            #        t2.strip().replace( ";", "," ),
            #        tx.strip().replace( " | ", "\n" )
            #        )

            #f = xbmcvfs.File( SUBTITLES + "%s.srt" % subtitle_name, "w" )
            #ok = f.write( txt )
            #f.close()

            file( SUBTITLES + "%s.srt" % subtitle_name, "wb" ).write( srt.replace( "<br/>", "\n" ) )
            subtitle_file = SUBTITLES + "%s.srt" % subtitle_name
    except:
        print_exc()
        try: xbmcvfs.delete( SUBTITLES + "%s.srt" % subtitle_name )
        except: pass
    print subtitle_file
    return subtitle_file


def getClipID( ID=2893 ):
    srt, hd, sd = "", "", ""
    try:
        url = "http://www.tetesaclaques.tv/services/xml_video/clip-%s-type-episode.xml" % ID
        html = get_html_source( url )
        file( "clip-%s-type-episode.xml" % ID, "wb" ).write( html )
        srt, hd, sd = re.findall( '<subtitle_file>(.*?)</subtitle_file>.*?<high>(.*?)</high>.*?<low>(.*?)</low>', html, re.S )[ 0 ]
    except:
        print_exc()
    return srt, hd, sd


def getClip( url ):
    plot, subtitle, playpath, playpath2 = "", "", "", ""
    html = get_html_source( url )
    try: plot = "".join( re.compile( '<div id="playerInfo">.*?<p>(.*?)</p>', re.S ).findall( html ) ).replace( "\n", " " )
    except: pass
    try: subtitle, playpath, playpath2 = re.compile( "clip\:.*?captionUrl\:.*?'(.*?)'\,.*?bitrates.*?url\:.*?\"(.*?)\".*?url\:.*?\"(.*?)\"", re.S ).findall( html )[ 0 ]
    except: pass
    return plot, subtitle, playpath, playpath2


def getCollection( page="1" ):
    url = "http://www.tetesaclaques.tv/collection/par_date/" + str( page )
    #html = open( "collection.html" ).read()
    html = get_html_source( url )

    nextpage = re.compile( '<a href="(.*?)" title="Page suivante" class="btnSuiv">' ).findall( html )

    regexp   = '<div class="wrapCapsule.*?">(.*?)</div><!--/wrapCapsule'
    regexp2  = '<a href="(.*?)" title=".*?" class="lienThumbCollection"><span></span><img src="(.*?)".*?'
    regexp2 += '<h2>(.*?)</h2>.*?<br />(.*?) votes.*?'

    for count, item in enumerate( re.compile( regexp, re.S ).findall( html ) ):
        rate = item.count( 'starActive_min.png' ) + ( item.count( 'starHalf_min.png' ) * .5 )
        item = re.search( regexp2, item, re.S ).groups()

        clip = {
            "rate":     rate,
            "aired":    "",
            "id":       "",
            "url":      item[ 0 ],
            "title":    item[ 2 ],
            "episode":  -1,
            "icon":     "http://tetesaclaques.tv/" + item[ 1 ],
            "votes":    item[ 3 ].replace( "\t", "" ).strip(),
            "plot":     "",
            "subtitle": "",
            "playpath": "",
            "playpath2": "",
            }
        clip[ "plot" ], clip[ "subtitle" ], clip[ "playpath" ], clip[ "playpath2" ] = getClip( item[ 0 ] )

        yield clip

    yield { "nextpage": ''.join( nextpage ).split( "/" )[ -1 ] }


def getEpisodes():
    url = "http://tetesaclaques.tv/serietele"
    #html = open( "serietele.html" ).read()
    html = get_html_source( url )

    regexp   = '<div class="wrapCapsule.*?">(.*?)</div><!--/wrapCapsule'
    regexp2  = '<a href="(.*?)" title=".*?" class="titreThumb">(.*?)<br /><span class="saison-episode">(.*?)</span></a>.*?'
    regexp2 += '<img src="(.*?)".*?<p class="nbVoteStar">(.*?) votes</p>.*?'

    for count, item in enumerate( re.compile( regexp, re.S ).findall( html ) ):
        rate = item.count( 'starActive.png' ) + ( item.count( 'starHalf.png' ) * .5 )
        item = re.search( regexp2, item, re.S ).groups()

        ep = {
            "rate":     rate,
            "aired":    S01_AIRED[ count ],
            "id":       item[ 0 ].split( "episode" )[ -1 ],
            "url":      item[ 0 ],
            "title":    item[ 1 ],
            "episode":  item[ 2 ].split()[ -1 ],
            "icon":     "http://tetesaclaques.tv/" + item[ 3 ],
            "votes":    item[ 4 ],
            "plot":     "",
            "subtitle": "",
            "playpath": "",
            "playpath2": "",
            }
        ep[ "plot" ], ep[ "subtitle" ], ep[ "playpath" ], ep[ "playpath2" ] = getClip( item[ 0 ] )

        yield ep


fanarts = {
    'le_pilote':         'le-pilote-1280x800.jpg',
    'monique_et_lucien': 'monique-et-lucien-1280x800.jpg',
    'gabriel_et_samuel': 'gabriel-et-samuel-1280x800.jpg',
    'raoul':             'raoul-1280x800.jpg',
    'oncle_tom':         'oncle-tom-1280x800.jpg',
    'natacha':           'natacha-1280x800.jpg',
    'general':           'la-famille-1280x800.jpg',
    'rene-charles':      'rene_charles-1280x800.jpg',
    'jimmy_et_rejean':   'whitaker-1280x800.jpg',
    'turcotte':          'turcotte-1280x800.jpg',
    'yvon':              'yvon-1280x800.jpg',
    'a': 'georges-1280x800.jpg',
    'b': 'cap_kungfu-1280x800.jpg',
    'c': 'oncletom_sport-1280x800.jpg',
    'd': 'crometnamou-1280x800.jpg',
    }

def getPersonnages():
    url = "http://www.tetesaclaques.tv/personnages"
    #html = open( "personnages.html" ).read()
    html = get_html_source( url )

    regexp = '<div class="wrapThumb.*?">.*?<a href="(.*?)" title="(.*?)"><img src="(.*?)".*?</a>.*?<br />(.*?)</div>'

    for count, item in enumerate( re.compile( regexp, re.S ).findall( html ) ):
        extra = item[ -1 ].replace( "\t", "" ).replace( "\n", "" ).strip().split()
        fanart = fanarts.get( os.path.basename( item[ 0 ] ).split( "_playlist" )[ 0 ] ) or fanarts[ "general" ]
        person = {
            "url":      item[ 0 ],
            "title":    item[ 1 ],
            "icon":     item[ 2 ],
            "duration": extra[ -1 ].strip( "()" ),
            "clips":    extra[ 0 ],
            "fanart":   'http://www.tetesaclaques.tv/public/images/wallpapers/' + fanart
        }
        yield person


def getPersonnageClips( url ):
    #html = open( "gabriel_et_samuel_playlist71.html" ).read()
    html = get_html_source( url )

    regexp   = '<div class="wrapCapsule.*?">(.*?)</div><!--/wrapCapsule'
    regexp2  = '<a href="(.*?)" title=".*?" class="lienThumbCollection"><span></span><img src="(.*?)".*?'
    regexp2 += '<h2>(.*?)</h2>.*?<br />(.*?) votes.*?'

    for count, item in enumerate( re.compile( regexp, re.S ).findall( html ) ):
        rate = item.count( 'starActive_min.png' ) + ( item.count( 'starHalf_min.png' ) * .5 )
        item = re.search( regexp2, item, re.S ).groups()
        
        clip = {
            "rate":     rate,
            "aired":    "",
            "id":       "-1",
            "url":      item[ 0 ],
            "title":    item[ 2 ],
            "episode":  -1,
            "icon":     "http://tetesaclaques.tv/" + item[ 1 ],
            "votes":    item[ 3 ].replace( "\t", "" ).strip(),
            "plot":     "",
            "subtitle": "",
            "playpath": "",
            "playpath2": "",
            }
        clip[ "plot" ], clip[ "subtitle" ], clip[ "playpath" ], clip[ "playpath2" ] = getClip( item[ 0 ] )

        yield clip


def getExtras():
    url = "http://www.tetesaclaques.tv/extras"
    #html = open( "extras.html" ).read()
    html = get_html_source( url )

    regexp  = '<h2 id="(.*?)"><span>(.*?)</span></h2>(.*?)<!--/clearfix -->'
    regexp2 = '<div class="wrapCapsule.*?">(.*?)<!--/wrapCapsule'
    regexp3 = '<h4>(.*?)</h4>.*?<a href="(.*?)" title=".*?" class="lienThumbExtra"><span></span><img src="(.*?)".*?'
    revotes = '<div class="votes">(.*?) votes</div>'
    
    for count, item in enumerate( re.compile( regexp, re.S ).findall( html ) ):
        if  item[ 0 ] == "fondsEcran": continue
        genre = item[ 1 ]
        plot  = "".join( re.findall( '<h3>(.*?)</h3>', item[ 2 ], re.S ) )
        for i in re.findall( regexp2, item[ 2 ], re.S ):
            title, url, icon = re.findall( regexp3, i, re.S )[ 0 ]
            rate  = i.count( 'starActive.png' ) + ( i.count( 'starHalf.png' ) * .5 )
            votes = "".join( re.findall( revotes, i, re.S ) )
            mp3   = "".join( re.findall( '<p>.*?<a href="(.*?)">.*?</a>.*?</p>', i, re.S )[ :1 ] )
            if not icon.startswith( "http://" ): icon = "http://tetesaclaques.tv/" + icon
            extra = {
                "genre":    genre,
                "plot":     plot,
                "title":    title,
                "url":      url,
                "icon":     icon,
                "rate":     rate,
                "votes":    votes,
                "mp3":      mp3,
                "subtitle": "",
                "playpath": "",
                "playpath2": "",
                }
            plot2, extra[ "subtitle" ], extra[ "playpath" ], extra[ "playpath2" ] = getClip( url )
            if plot2 and not plot: extra[ "plot" ] = plot2

            yield extra


if ( __name__ == "__main__" ):
    import time
    t1 = time.time()
    for item in getEpisodes():
        print item
        print "-"*100
    print time.time() - t1
