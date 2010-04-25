
import os
import re
import sys
import urllib
from traceback import print_exc


canals = {
    "canald":     ( "Canal D", "http://www.canald.com", "Canal D vous propose des documentaires divers dont des documentaires animaliers, des biographies, des enquêtes policières et des émissions d'humour." ),
    "canalvie":   ( "Canal Vie", "http://www.canalvie.com", "Canal Vie vous présente des émissions et vous propose de la webtélé." ),
    "historiatv": ( "HiSToriA TV", "http://www.historiatv.com", "HiSToRiA TV - Chaîne de télévision francophone spécialisée sur l'histoire" ),
    "seriesplus": ( "Séries+", "http://www.seriesplus.com", "Séries+ propose des séries télé ayant comme genres le drame, la comédie, les enquêtes policières et le suspense ainsi que des nouvelles et potins de stars." ),
    #"vraktv":     ( "VRAK.TV", "http://www.vrak.tv", "VRAK.TV propose des émissions!" ),
    "ztele":      ( "Ztélé", "http://www.ztele.com", "Ztélé est une chaîne de télévision spécialisée dans les nouvelles technologies, la science, le multimédia, les jeux vidéo et les séries de science-fiction." ),
    }


def get_html_source( url ):
    """ fetch the html source """
    try:
        if os.path.isfile( url ): sock = open( url, "r" )
        else:
            urllib.urlcleanup()
            sock = urllib.urlopen( url )
        htmlsource = sock.read()
        sock.close()
        return htmlsource
    except:
        print_exc()
        return ""


def getWebVideoUrl( canal_url, videoid ):
    url = "%s/webtele/_dyn/getWebVideoUrl_highlow.jsp?videoId=%s" % ( canal_url, videoid )
    jsp = get_html_source( url )
    return re.findall( '(http:/(?:\\/[\\w\\.\\-]+)+)', jsp )


def getTvShows( canal_url="", page="1" ):
    tvshows = {}
    pages = "1"
    try:
        if "canalvie" in canal_url: uri = "%s/webtele/recherche/?type=0&theme=0&emission=0&episode=0&tri=0&page=%s"
        else: uri = "%s/webtele/recherche/?type=0&emission=0&episode=0&tri=0&page=%s"
        url = uri % ( canal_url, page )
        html = get_html_source( url )
        #print url
        #print html
        #html = get_html_source( "www.seriesplus.com.htm" )
        #html = get_html_source( "www.canald.com.htm" )
        #html = get_html_source( "www.ztele.com.htm" )
        #html = get_html_source( "www.historiatv.com.htm" )
        #html = get_html_source( "www.canalvie.com.htm" )
        try:
            total = int( re.compile( '<a name="resultats"></a>.*?\t(\\d+) r.*?sultats.*?</div>', re.S ).search( html ).group( 1 ) )
            if ( total / 10 ) * 10 < total: pages = str( ( total / 10 ) + 1 )
            else: pages = str( ( total / 10 ) )
        except:
            print_exc()
        for video in re.compile( '<div class="video_rangee.*?">(.*?)</div><!-- fin // video_rangee -->', re.S ).findall( html ):
            try:
                id_and_title = re.search( '--><a href=".*?-(\d+)/" title=".*?">(.*?)</a></div>', video )
                ID, title = id_and_title.group( 1 ).strip(), id_and_title.group( 2 ).strip()

                try: episode = int( re.search( "[pisode|ep\.|webisode] (\d+)", title.lower() ).group( 1 ) )
                except: episode = 0
                try: season = int( re.search( "saison (\d+)", title.lower() ).group( 1 ) )
                except: season = 0

                tvshowtitle = re.search( '<div class="video_texte">.*?<div.*?>(.*?)</div>', video, re.S ).group( 1 ).strip()
                tvshowtitle = ( tvshowtitle or title )

                match = re.compile( 'ICONE ici.*?title="(.*?)".*?(\d{1,2}:\d{1,2}).*?(\d{1,2}/\d{1,2}/\d{1,2})', re.S ).search( video )
                if match: type, duration, date = match.group( 1 ), match.group( 2 ), match.group( 3 )
                else: type, duration, date = "", "", ""

                try: plot = re.search( '<div class="font11">(.*?)</div>', video ).group( 1 ).strip()
                except: plot = ""

                thumb = re.search( '-->.*?<img src="(.*?)".*?>', video ).group( 1 ).strip()

                tvshows[ ID ] = { "tvshowtitle": tvshowtitle, "title": title, "type": type.strip(), "duration": duration.strip(),
                    "date": date.strip(), "plot": plot, "thumb": thumb, "episode" : episode, "season" : season }
            except:
                print_exc()
                print tvshowtitle, title
    except:
        print_exc()
    return tvshows, pages



if ( __name__ == "__main__" ):
    import time
    t1 = time.time()
    canal_url = canals[ "ztele" ][ 1 ]
    tvshows, pages = getTvShows( canal_url, "20" )
    print pages
    for k, v in tvshows.items():
        print v[ "tvshowtitle" ]
        print v[ "title" ]
        print v[ "episode" ]
        print v[ "season" ]
        videoid = k#tvshows.keys()[ 0 ]
        print getWebVideoUrl( canal_url, videoid )
        print
        break
    print time.time() - t1
