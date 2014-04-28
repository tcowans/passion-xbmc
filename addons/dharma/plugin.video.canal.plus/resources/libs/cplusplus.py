import urllib2, urllib
import cookielib
import os,os.path
import re
import gzip,StringIO
import socket
#from xml.dom import minidom #TODO: replace minidom by ET
import elementtree.ElementTree as ET
import traceback
import sys

# timeout en seconds
#timeout =  10
#socket.setdefaulttimeout(timeout)
#cookies
ROOTDIR  = sys.modules[ "__main__" ].ROOTDIR
CACHEDIR = sys.modules[ "__main__" ].CACHEDIR

#if os.name=='posix':
#    # Linux case
#    ROOTDIR = os.path.abspath(os.curdir).replace(';','')
#else:
#    # Xbox and Windows case
#    ROOTDIR = os.getcwd().replace(';','')

COOKIEFILE = os.path.join(CACHEDIR,'cookies.lwp')
cj = cookielib.LWPCookieJar()

if os.path.isfile(COOKIEFILE):
    # si nous avons un fichier cookie deja sauvegarde
    #  alors charger les cookies dans le Cookie Jar
    cj.load(COOKIEFILE)

xmlParam = "14-1-18/06/2008-0"
videoplayerURL = "http://webservice.canal-plus.com/rest/bigplayer/"
GetMosaicPage = "getMEAs/"
EntrysPage = "video-player-filters.php"
ThemesPage = "initPlayer/"
# TODO : add old base url
VideoInfoPage = "getVideoInformation.php"
SearchPage = "search/"

def get_page(url,params={},savehtml=True,filename="defaut.html",check_connexion=True,debuglevel=1,nocookie=True,stream=False):
    """
    telecharge la page avec les parametres fournis :
        params : dictionnaire de parametres
    Renvoi le code html de la page
    """

    #h=urllib2.HTTPHandler(debuglevel=debuglevel)
    print "get_page:"
    print url
    print params
    if nocookie == False:
        h=urllib2.HTTPCookieProcessor(cj)#urllib2.HTTPCookieProcessor(cookiejar)
    request = urllib2.Request(url,urllib.urlencode(params))
    opener = urllib2.build_opener()
    urllib2.install_opener(opener)
    connexion = opener.open(request)
    #print connexion.headers
    if stream == True:
        return connexion # For ET
    html = connexion.read()
    open(os.path.join(CACHEDIR,filename).encode('utf8'),"w").write(html)
#    if connexion.headers["Content-Encoding"]=="gzip":
#        compressedstream = StringIO.StringIO(html)
#        gzipper = gzip.GzipFile(fileobj=compressedstream)
#        data = gzipper.read()
#    else:
#        data = html
#    try:
#        open(os.path.join(CACHEDIR,filename),"w").write(data)
#    except:
#        print "erreur lors de l'ecriture du fichier de telechargement"
#    # save the cookies again
#    cj.save(COOKIEFILE)
    return html # data


def get_xmlParam():
    """
    Telecharge la page d'accueil puis cherche et renvoi le xmlParam
    """
    print "get_xmlParam called ..."
    html=get_page("http://www.canalplus.fr",filename="index.html",debuglevel=1)
    exp=re.compile(r'"http://www\.canalplus\.fr/flash/xml/configuration/configuration-video-player\.php\?xmlParam=([\-/0-9]*)"')
    try:
        return exp.findall(html)[0]
    except:
        return None

def get_themes():
    """
    recupere et retourne une liste des themes et sous themes
    [ [ themeid , titre , [ [subtheme_id,titre] , ... ] ] , ... ]
    """
    print "get_themes called ..."

    elems = ET.parse(urllib.urlopen(videoplayerURL + ThemesPage)).getroot()
    #print ET.tostring(elems)
    themes=[]

    for theme in elems.find("THEMATIQUES").findall( "THEMATIQUE" ):
        #print ET.tostring(theme)
        try:
            theme_id = int( theme.findtext( "ID" ) )
            theme_nom = theme.findtext( "NOM" )
            theme_color = theme.findtext( "COULEUR" ).replace("#","")

            themes.append( [theme_id, theme_nom.strip(), theme_color] )
        except:
            print "get_themes- Erreur durant le parcorus des themes"
            traceback.print_exc()
    #print 'themes'
    #print themes
    return themes

def get_subthemes(theme_id):
    """
    recupere les sous-themes du theme fourni et renvoi un dictionnaire :
    { subthemeID : titre , ... }
    """
    print "get_subthemes called ..."
    #print theme_id

    elems = ET.parse(urllib.urlopen(videoplayerURL + ThemesPage)).getroot()
    #print ET.tostring(elems)
    subthemes=[]

    for theme in elems.find("THEMATIQUES").findall( "THEMATIQUE" ):
        #print ET.tostring(theme)
        try:
            cur_id = int( theme.findtext( "ID" ) )
            if int( cur_id ) == int( theme_id ):
                for subtheme in theme.find("SELECTIONS").findall("SELECTION"):
                    subtheme_id = int( subtheme.findtext( "ID" ) )
                    subtheme_nom = subtheme.findtext( "NOM" )
                    subthemes.append( [subtheme_id, subtheme_nom.strip()] )
                break
        except:
            print "get_subthemes - Erreur durant le parcorus des themes"
            traceback.print_exc()
    #print 'subthemes'
    #print subthemes
    return subthemes


def get_videos( subtheme_id,keyword='' ):
    """
    retourne l'equivalent de la mosaique canalplus sous forme d'une liste de dictionnaires
    [ { videoid , title , publication , imageURL , theme , visualized , note , duration } ]
    """
    print "get_videos called ..."
    videos=[]
    firstTag = ""
    if ( keyword != '' ):
        print 'Searching: %s'%keyword
#        print videoplayerURL + SearchPage + keyword
        #videos = _searchvideo( keyword )
        urlxml = videoplayerURL + SearchPage + keyword
        print urlxml
        firstTag = "VIDEO"
    else:
        urlxml = videoplayerURL + GetMosaicPage + subtheme_id
        firstTag = "MEA"


    elems = ET.parse( urllib.urlopen( urlxml ) ).getroot()
    #print ET.tostring(elems)

    for vid in elems.findall( firstTag ):
        #print ET.tostring( vid )
        try:
            videoID         = int( vid.findtext( "ID" ) )
            #title           = vid.find( "INFOS" ).find( "TITRAGE" ).findtext( "TITRE" ) + ': ' + vid.find( "INFOS" ).find( "TITRAGE" ).findtext( "SOUS_TITRE" )
            title           = vid.find( "INFOS" ).find( "TITRAGE" ).findtext( "TITRE" ).strip() + ': ' #+ vid.find( "INFOS" ).find( "TITRAGE" ).findtext( "SOUS_TITRE" )
            publicationDate = vid.find( "INFOS" ).find( "TITRAGE" ).findtext( "SOUS_TITRE" )
            description     = vid.find( "INFOS" ).findtext( "DESCRIPTION" ).strip()
            note            = float( vid.find( "INFOS" ).find( "NOTE" ).findtext( "MOYENNE" ).replace(",", ".") )
            imageURL        = vid.find( "MEDIA" ).find( "IMAGES" ).findtext( "GRAND" )

            videos.append( { 'videoID' : videoID,
                             'title': title,
                             'publication_date': publicationDate,
                             'image.url': imageURL,
                             'description': description,
                             'note': note,
                             } )
        except:
            print "cplusplus: error while retrieving videos list and info"
            traceback.print_exc()
    #print "videos"
    #print videos
    return videos


def get_info( videoID ):
    """
    retrouve les informations de l'ID de video fourni
    """
    print "get_videos called for video ID: %d"%videoID

    #print "get_info - Retrieving page:" + videoplayerURL +"getVideosLiees/%d"%videoID

    elems = ET.parse(urllib.urlopen(videoplayerURL +"getVideosLiees/%d"%videoID)).getroot()

    type = 'rtmp'

    #print elems
    #print elems.tag
    #print ET.tostring(elems)
    #print elems.find( "VIDEO" )
    for videoinfos in elems.findall( "VIDEO" ):
        videoinfos_id          = int ( videoinfos.findtext( "ID" ) )
        videoinfos_type        = videoinfos.findtext( "TYPE" )
        videoinfos_title       = videoinfos.findtext( "INFOS/TITRAGE/TITRE" )#.encode("cp1252")
        videoinfos_description = videoinfos.findtext( "INFOS/DESCRIPTION" )#.encode("cp1252")
        videoinfos_videoHD     = videoinfos.findtext( "MEDIA/VIDEOS/HAUT_DEBIT" )
        videoinfos_videoBD     = videoinfos.findtext( "MEDIA/VIDEOS/BAS_DEBIT" )
        videoinfos_videoHLS    = videoinfos.findtext( "MEDIA/VIDEOS/HLS" )
        videoinfos_videoHDS    = videoinfos.findtext( "MEDIA/VIDEOS/HDS" )
        videoinfos_videoMOBILE = videoinfos.findtext( "MEDIA/VIDEOS/MOBILE" )
        videoinfos_publication_date = videoinfos.findtext( "INFOS/PUBLICATION/DATE" )
        videoinfos_image       = videoinfos.findtext( "MEDIA/IMAGES/GRAND" )
        videoinfos_smallimage  = videoinfos.findtext( "MEDIA/IMAGES/PETIT" )
        videoinfos_categorie   = videoinfos.findtext( "RUBRIQUAGE/CATEGORIE" )
        if videoinfos_id == videoID:
            # Found
            print "Video ID found"
            if videoinfos_type == "VOD PROG":
                type = 'http'
                videoHD_URL = videoinfos_videoHD
                videoBD_URL = videoinfos_videoBD
            else:
                type = 'rtmp'
                videoHD_URL = videoinfos_videoHD.replace("rtmp://vod-fms.canalplus.fr","rtmp://vod-fms.canalplus.fr:1935").replace(".flv","")
                videoBD_URL = videoinfos_videoBD.replace("rtmp://vod-fms.canalplus.fr","rtmp://vod-fms.canalplus.fr:1935").replace(".flv","")

            #print "videoHD_URL = %s"%videoHD_URL
            #print "videoBD_URL = %s"%videoBD_URL
            return {'title' : videoinfos_title,
                    'summary' : videoinfos_description,
                    'publication_date' :  videoinfos_publication_date,
                    'image.url' : videoinfos_image,
                    'smallimage.url' : videoinfos_smallimage,
                    'theme' : videoinfos_categorie,
                    'video.stream_server' : "",
                    'video.hi' : videoHD_URL,
                    'video.low' : videoBD_URL,
                    'video.mobile' : videoinfos_videoMOBILE,
                    'video.hds' : videoinfos_videoHDS,
                    'video.hls' : videoinfos_videoHLS,
                    }
    print "get_info - video info not FOUND - ERROR"
    return None

def Cache_Pic(url,filename):
    try:
        if not os.path.exists(filename):
            urllib.urlretrieve(url,filename)
        else:
            pass
    except:
        pass


def DL_video(url,fichier,ProgressUpdate=None,ProgressObject=None,debuglevel=0):
    """
    telecharge la video a l'url mentionnee
    """
    if os.path.exists(fichier):
        for i in range(100):
            try:
                ProgressUpdate(i)
            except:
                pass
        return 0
    h=urllib2.HTTPHandler(debuglevel=debuglevel)
    request = urllib2.Request(url)

    #request.add_header('Host','www.canalplus.fr')
    request.add_header('Referer', 'http://www.canalplus.fr/flash/loader/loader_canalplus_V0_1.swf')
    request.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; fr; rv:1.9) Gecko/2008052906 Firefox/3.0')
    request.add_header('Accept','text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')
    request.add_header('Accept-Language','fr,fr-fr;q=0.8,en-us;q=0.5,en;q=0.3')
    request.add_header('Accept-Charset','ISO-8859-1,utf-8;q=0.7,*;q=0.7')
    #request.add_header('Accept-Encoding','gzip,deflate')
    request.add_header('Keep-Alive','300')
    request.add_header('Connection','keep-alive')
    #request.add_header('Content-type','application/x-www-form-urlencoded')
    #request.add_header('Content-length',len(urllib.urlencode(params)))
    opener = urllib2.build_opener(h)
    urllib2.install_opener(opener)
    connexion = opener.open(request)
    taille = connexion.headers["Content-Length"]
    f=open(fichier,"wb")
    for i in range(1,int(taille),100000):
        f.write(connexion.read(100000))
        try:
            ProgressUpdate(int(float(i)/int(taille)*100),"%s sur %s Ko (%s%%)"%(str(i/1024),str(int(taille)/1024),int(float(i)/int(taille)*100)))
            if ProgressObject.iscanceled():
                f.close()
                return -1
        except:
            pass
    f.write(connexion.read(int(taille)-i))
    #f.write(connexion.read(int(connexion.headers["Content-Length"])))
    # open(filename,"wb").write(connexion.read(int(connexion.headers["Content-Length"])))
    f.close()
    return 1

if __name__ == "__main__":
    ###avant tout, recuperons le xmlParam
    xmlParam = get_xmlParam()
    #xmlParam = "14-1-24/06/2008-0"
    print get_themes()
    print xmlParam
    global infos
    infos = get_info("136491")
    print "\n".join([video['title'] for video in get_videos(xmlParam, theme_id="5" , subtheme_id = "0")])
    ##
    #print get_subthemes(u"23")


