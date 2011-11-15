
import os
import re
import sys
import urllib
from traceback import print_exc


canals = {
    "canald":     ( "Canal D", "http://www.canald.com", "Canal D vous propose des documentaires divers dont des documentaires animaliers, des biographies, des enquêtes policières et des émissions d'humour." ),
    #"canalvie":   ( "Canal Vie", "http://www.canalvie.com", "Canal Vie vous présente des émissions et vous propose de la webtélé." ),
    #"historiatv": ( "HiSToriA TV", "http://www.historiatv.com", "HiSToRiA TV - Chaîne de télévision francophone spécialisée sur l'histoire" ),
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
    return re.findall( '(http:/(?:\\/[\\w\\.\\-]+)+)', get_html_source( url ) )


def getContents( html, canal_url, programid ):
    contents = { "typeId": [], "themeId": [], "programId": [], "episodeId": [] }
    try:
        for content in contents.keys():
            regexp = '<select name="%s" id="%s".*?>(.*?)</select>' % ( content, content )
            for options in re.compile( regexp, re.S ).findall( html ):
                contents[ content ] = re.findall( '<option value="(\d+)".*?>(.*?)</option>', options )
    except:
        print_exc()
    try:
        if programid != "0":
            url = "%s/webtele/_dyn/getEpisodesWithVideosXml.jsp?programId=%s&episodeId=0" % ( canal_url, programid )
            html = get_html_source( url )
            contents[ "episodeId" ] = re.findall( '<episode id="(\d+)".*?>(.*?)</episode>', html )
    except:
        print_exc()
    return contents


def getTvShows( canal_url="", typeid="0", themeid="0", programid="0", episodeid="0", pageid="1" ):
    contents = {}
    tvshows = {}
    pages = "1"
    try:
        themeid = ( "", "&theme=" + themeid )[ "canalvie" in canal_url ]
        url = "%s/webtele/recherche/?type=%s%s&emission=%s&episode=%s&tri=0&page=%s" % ( canal_url, typeid, themeid, programid, episodeid, pageid )
        html = get_html_source( url )
        #html = get_html_source( "../../source/www.seriesplus.com.htm" )
        #print url
        #print html

        contents = getContents( html, canal_url, programid )

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
    return tvshows, pages, contents



if ( __name__ == "__main__" ):
    import time
    t1 = time.time()
    canal_url = canals[ "ztele" ][ 1 ]
    tvshows, pages, contents = getTvShows( canal_url, programid="2209", pageid="1" )
    print pages
    print contents
    print
    for k, v in tvshows.items():
        print v[ "tvshowtitle" ]
        print v[ "title" ]
        print v[ "episode" ]
        print v[ "season" ]
        videoid = k#tvshows.keys()[ 0 ]
        #print getWebVideoUrl( canal_url, videoid )
        print
        #break
    print time.time() - t1
