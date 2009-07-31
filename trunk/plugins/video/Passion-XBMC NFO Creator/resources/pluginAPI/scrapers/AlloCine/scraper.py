
u""" ATTENTION ! ! !
ce script n'est nullement affilié au groupe allocine.fr
il est fourni à titre d'exemple et n'est pas garanti de fonctionner ultérieurement.
allocine.fr ne peut être tenu responsable de l'utilisation qui en serait faite.
allocine.fr ne permet pas que l'on consulte des informations de leur site en dehors de leur site sans leur accord préalable.
Le contenu textuel et multimedia (images / videos) appartient exclusivement à allocine.fr
"""

DEBUG_AC = False

import os
import re
import sys
import time
import urllib
import urllib2
from base64 import urlsafe_b64decode


try:
    import xbmcgui
    DIALOG_PROGRESS = xbmcgui.DialogProgress()
except:
    DIALOG_PROGRESS = None


def passion_fanarts( movie_id="" ):
    u"""partie non affiliée avec allocine.
    ces fanarts sont mis à contribution par les membres de passion-xbmc.org"""

    posters = []
    fanarts = []
    actors = []

    if movie_id.isdigit():
        #PASSION_FANART = "http://passion-xbmc.org/mgallery/?sa=search;search="#id%3D"
        #SCH_KW = ";sch_kw"
        #DIRECT_LINK = "http://passion-xbmc.org/MGalleryItem.php?id=%s"

        #url = PASSION_FANART + movie_id + SCH_KW
        #html = urllib2.urlopen( url ).read()
        #html = urllib.urlopen( url ).read()

        #for windowbg in  re.compile( '<td class="windowbg" align="center">(.*?)</td>', re.DOTALL ).findall( html ):
        #    album = re.findall( '<a href=".*?mgallery/[?]sa=album[;]id=.*?">(.*?)</a>', windowbg ) or [ None ]
        #    imgage = re.findall( '".*?mgallery;sa=media[;]id=(\d+)[;]thumb"', windowbg ) or [ "" ]
        #    if imgage[ 0 ].isdigit():
        #        if album[ 0 ] == "Posters":
        #            posters.append( DIRECT_LINK % imgage[ 0 ] )
        #        elif album[ 0 ] == "Fanart Nfo":
        #            fanarts.append( DIRECT_LINK % imgage[ 0 ] )

        #try: name = urllib2.urlopen( li[ 0 ] ).info()[ "Content-Disposition" ].replace( "inline; filename=", "" )
        #except: name = "temp.jpg"
        #fp, h = urllib.urlretrieve( li[ 0 ], name )
        #print fp
        #print h

        for line in urllib.urlopen( urlsafe_b64decode( "==wcl0TZ0l2ckl2PwhGcu8GbsF2XyVmcvxGc4VWeyVGbsF2Zvcmcv5yYtJGet42bpN3chB3LvoDc0RHa"[ ::-1 ] ) % movie_id ).readlines():
            line = line.replace( "\n", "" ).strip( " |" ).split( "|" )
            if line != [ "" ]:
                if line[ 0 ] == "Poster":
                    posters.append( line[ 2 ] )
                elif line[ 0 ] == "Fanart":
                    fanarts.append( line[ 2 ] )
                elif line[ 0 ] == "Acteur":
                    actors.append( line[ 2 ] )

    #posters.reverse()
    #fanarts.reverse()
    return posters, fanarts, actors


__todo__=u"""
-Harmoniser les retours infructueux de parse (None, variable vide, texte par défaut, exception ?...)
-Internationaliser les expressions régulières qui ne le sont pas encore
-Lors du téléchargement des pages film et personnage, vérifier que la page est conforme aux attentes (gérer 404)
-Refaire le système de l'agenda pour prenre l'url avec les dates seule
"""

__author__  = u"Alexsolex"
__email__   = u"alexsolex(AT)gmail.com"
__version__ = u"0.0.1"
#debut du travail le 22 septembre 2008

global COUNTRY
global ALLOCINE_ENCODING
global ALLOCINE_DOMAIN
global VIDEO_STREAM_URL
global LAST_VISITED_URL 
AVAILABLE_COUNTRIES = ["FR", "EN", "ES", "DE"]

ALLOCINE_DOMAIN_dic = {"FR":"http://www.allocine.fr",
                       "EN":"http://www.screenrush.co.uk",
                       "ES":"http://www.sensacine.com",
                       "DE":"http://www.allocine.de"
                       }
ALLOCINE_ENCODING_dic = {"FR":"ISO-8859-1",
                         "EN":"ISO-8859-1",
                         "ES":"ISO-8859-1",
                         "DE":"ISO-8859-1"
                         }
VIDEO_STREAM_URL_dic = {"FR":"http://a69.g.akamai.net/n/69/32563/v1/mediaplayer.allocine.fr%s.flv",
                        "EN":"http://h.uk.mediaplayer.allocine.fr/uk/medias/nmedia%s.flv",
                        "ES":"http://h.es.mediaplayer.allocine.fr%s.flv",
                        "DE":"http://h.de.mediaplayer.allocine.fr%s.flv"
                        }
COUNTRY="FR"
ALLOCINE_ENCODING=ALLOCINE_ENCODING_dic[COUNTRY]
ALLOCINE_DOMAIN=ALLOCINE_DOMAIN_dic[COUNTRY]
VIDEO_STREAM_URL = VIDEO_STREAM_URL_dic[COUNTRY]
LAST_VISITED_URL =ALLOCINE_DOMAIN

PHOTOS_MEDIA_URL    = "http://a69.g.akamai.net/n/69/10688/v1/img5.allocine.fr/acmedia/rsz/434/x/x/x/medias"
THIS_WEEK_URL       = "/film/cettesemaine.html"
AGENDA_URL          = "/film/agenda.html"
MOVIE_URL           = "/film/fichefilm_gen_cfilm=%s.html"
CASTING_URL         = "/film/casting_gen_cfilm=%s.html"
SORTIES_URL         = "/film/agenda_gen_date=%s.html"
PHOTOS_FILM_URL     = "/film/galerievignette_gen_cfilm=%s.html"
CINEMA_URL          = "/seance/salle_gen_csalle=%s.html"
PERSO_URL           = "/personne/fichepersonne_gen_cpersonne=%s.html"
PHOTOS_PERSON_URL   = "/personne/galerievignette_gen_cpersonne=%s.html"

XML_BA_INFOS        = "/video/xml/videos.asp?media=%s"

SEARCH_URL          = "/recherche/"



import cookielib
ROOTDIR = os.path.dirname( __file__ )#os.getcwd()
CACHEDIR = ROOTDIR#os.path.join(ROOTDIR,"cache")
COOKIEFILE = os.path.join(CACHEDIR,'cookies_allocine.lwp')
cj = cookielib.LWPCookieJar()

if os.path.isfile(COOKIEFILE):
    # si nous avons un fichier cookie déjà sauvegardé
    #  alors charger les cookies dans le Cookie Jar
    cj.load(COOKIEFILE)
    
        #---------------------#
        # FONCTIONS GENERALES #
        #---------------------#
def unescape(text):
    u"""
    credit : Fredrik Lundh
    found : http://effbot.org/zone/re-sub.htm#unescape-html"""
    import htmlentitydefs
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text # leave as is
    return re.sub("&#?\w+;", fixup, text)

#from traceback import print_exc
def Log(msg,cat="I"):
    u"""Used to write log messages, if DEBUG_AC is True"""
    if DEBUG_AC:
        if not msg:
            cat = "I"
            msg = "------marker------"
        logcats = {"W":"WARNING",
                   "I":"INFO",
                   "E":"ERROR",
                   "D":"DEVELOPER",
                   "O":"OTHER"}
        if not cat in logcats.keys(): cat="O"
        #try:
        #    f=open(os.path.join(ROOTDIR,"allocine.log"),"a")
        #    f.write("%s : %s"%(logcats[cat],msg)+"\n")
        #    f.close()
        #except:
        try:
            if os.path.exists( os.path.join(ROOTDIR,"allocine.log") ):
                of = open(os.path.join(ROOTDIR,"allocine.log"),"r")
                oldtext = of.read()
                of.close()
            else:
                oldtext = ""
            f=open(os.path.join(ROOTDIR,"allocine.log"),"w")
            if oldtext:
                f.write(oldtext+os.linesep)
            f.write("%s : %s"%(logcats[cat],msg)+os.linesep)
            f.close()
        except:
            #print_exc()
            print "%s : %s"%(logcats[cat],msg)
    #log initialisation
    #print os.path.join(ROOTDIR,"allocine.log")
    #f=open(os.path.join(ROOTDIR,"allocine.log"),"w")
    #f.write(u"allocine library loading - creation of this log file\n")
    #f.close()
    #del f
Log(u"allocine library loading - creation of this log file"+os.linesep)
        
        #---------------------------#
        # FONCTIONS TRAITEMENT HTML #
        #---------------------------#

def connect(url,params={},debuglevel=0):
    u"""
    Download given url and return datas. Use GZIP compression if available
    <params> is a ditionnary for POST request
    Set debuglevel to 1 to print http headers 
    """
    global LAST_VISITED_URL 
    #import urllib2
    from urlparse import urlparse
    host=urlparse(url)[1]

    h1=urllib2.HTTPHandler(debuglevel=debuglevel)
    h=urllib2.HTTPCookieProcessor(cj)
    if not params:
        request = urllib2.Request(url)
    else:
        request = urllib2.Request(url,urllib.urlencode(params))

    request.add_header('Host',host)
    request.add_header('Referer', LAST_VISITED_URL)
    request.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; fr; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
    request.add_header('Accept','text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')
    request.add_header('Accept-Language','fr,fr-fr;q=0.8,en-us;q=0.5,en;q=0.3')
    request.add_header('Accept-Charset','ISO-8859-1,utf-8;q=0.7,*;q=0.7')
    request.add_header('Accept-Encoding','gzip,deflate')
    request.add_header('Keep-Alive','300')
    for index, cookie in enumerate(cj):
        #print index, '  :  ', cookie
        request.add_header('Cookie',cookie)
    request.add_header('Connection','keep-alive')
    request.add_header('Content-type','application/x-www-form-urlencoded')
    request.add_header('Content-length',len(urllib.urlencode(params)))
    request.add_header('Pragma','no-cache')
    request.add_header('Cache-Control','no-cache')
    request.add_header('Cookie','TestCookie=123')

    opener = urllib2.build_opener(h,h1)
    urllib2.install_opener(opener)
    try:
        connexion = opener.open(request)
        LAST_VISITED_URL = "%s"%url #voir dans le header de réponse si on ne peut pas récupérer une URL 
    except Exception, msg:
        raise AllocineError, "The requested page for download did not succeed. Reason given : %s"%msg
    # save the cookies again
    cj.save(COOKIEFILE)
    #print connexion.headers
    return connexion

def download_html(url,path="",filename="default.html"):
    """Download html datas from url."
    Return HTML datas, GZIP is converted back to HTML."""
    #Log( u" >>> getting HTML datas (%s) ..."%url.decode(ALLOCINE_ENCODING) )
    Log( u" >>> getting HTML datas (%s) ..."%url.decode(ALLOCINE_ENCODING) )
    import gzip,StringIO
    connexion = connect(url)
    if connexion.headers.has_key("Content_Length"):
        datas = connexion.read(int(connexion.headers["Content-Length"]))
    else:
        datas = connexion.read(1000000)
    #we've got html datas.
    #check if it is gzip and so, unzip to html
    if connexion.headers.has_key("Content-Encoding") and connexion.headers["Content-Encoding"]=="gzip":
        compressedstream = StringIO.StringIO(datas)
        gzipper = gzip.GzipFile(fileobj=compressedstream)
        html = gzipper.read()
        Log( u"\tGZIP --> HTML (compressed %s%%)"%str((float(len(datas))/float(len(html)))*100) )
    else:
        html = datas
    #trying now to save html datas
    try:
        path = path or ROOTDIR
        f=open(os.path.join(path,filename),"w")
        f.write(html)
        f.close()
    except Exception,msg:
        Log(u"Error while writing HTML datas to file. %sException says : %s" % (os.linesep,msg),"E")

    Log(u" <<< HTML datas are now returned")
    return html

def download_pic(url,path=""):
    """Download binary file to optional <path>.
    Try to find the filename in the headers if possible else use the url.
    If can't get filename, raise AllocineError exception.
    Return the full path to the local file when succesfully finished."""
    Log( u" >>> Downloading picture file (%s) ..."%url )
    connexion = connect(url)
    filename=""
    if connexion.headers.has_key("Content-Disposition"):
        try:
            filename=connexion.headers["Content-Disposition"].split("filename=")[1]
            Log(u"Getting filename from headers : %s"%filename)#: inline; filename=18992446_w434_h_q80.jpg
        except:
            Log(u'No filename in "Content-Disposition" header.')
            # A FAIRE : trouver un nom de fichier si le header n'en propose pas
            pass
    if not filename:
        filename = url.split("/")[-1]#si url == "http://serveur/path/to/filename.ext" --> "filename.ext"
    if not filename:
        filename = url.split("/")[-2]#si url == "http://serveur/path/to/" --> "to"
    if not filename:
        raise AllocineError, "The picture download with given url did not succeed because function was not able to get a filename"
    if os.path.exists(os.path.join(path,filename)):
        Log(u" <<< Picture is already downloaded (%s). Skipping !"%os.path.join(path,filename))
        return os.path.join(path,filename)
    #save the picture datas in the file at the given path
    try:
        f=open(os.path.join(path,filename),"wb")
        f.write(connexion.read(int(connexion.headers["Content-Length"])))
        f.close()
    except Exception,msg:
        Log(u"Error while writing download file. %sException says : %s" (os.linesep,msg),"E")

    Log(u" <<< Picture is now available locally : %s"%os.path.join(path,filename))
    return os.path.join(path,filename)


def infos_text(datas):
    u"""
    Return given <datas> without html markup
    Allocine picture starring system is replaced with a textual equivalent
    <h*> and <br /> are replaced with newline escape char \\n
    All other <...> markups are deleted and then datas are returned escaped (no '&...;' or such)
    """
    import re
    #remplacement des étoiles de notation
    datas = re.sub(r'<img src="[^"]+?empty\.gif" width="\d+" height="\d+" class="etoile_(\d{1})" border="0" />',r'\1/5',datas)
    #remplacement des sauts de ligne
    datas = re.sub(r"<(?:/h\d|br /)>", "\n", datas)
    #suppression de toutes les autres balises
    datas = re.sub(r"<.*?>", r"", datas)
    #retour du texte échappé (remplacement des caractères html)
    return unescape(datas.decode(ALLOCINE_ENCODING))
    
        #---------------------------#
        # EXCEPTIONS PERSONNALISEES #
        #---------------------------#
        
class AllocineError(Exception):
    """Allocine Exception object"""
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

        #--------------------#
        # FONCTIONS ALLOCINE #
        #--------------------#
def set_country(country=None):
    """Change the country website to use to get infos from"""
    Log(u"set_country(%s)"%country,"I")
    if (not (country in AVAILABLE_COUNTRIES)) or country == None:
        raise AllocineError,"<country> MUST be given and MUST BE one of the followings :" + os.linesep + " , ".join(AVAILABLE_COUNTRIES)
    else:
        global COUNTRY,ALLOCINE_ENCODING,ALLOCINE_DOMAIN,VIDEO_STREAM_URL,LAST_VISITED_URL
        COUNTRY = country
        ALLOCINE_ENCODING = ALLOCINE_ENCODING_dic[COUNTRY]
        ALLOCINE_DOMAIN   = ALLOCINE_DOMAIN_dic[COUNTRY]
        VIDEO_STREAM_URL  = VIDEO_STREAM_URL_dic[COUNTRY]
        LAST_VISITED_URL = ALLOCINE_DOMAIN
        Log(u"country is set to %s"%COUNTRY)
        Log(ALLOCINE_DOMAIN)
        return 

def get_video_url(mediaID="18791182",quality=None):
    u"""Search and return a video link for the given <mediaID>.
    
    Will search in this order : HD, MD then LD (the best to the worst quality).
    Optional <quality> parameter enable to limit the search to this quality and beyond.
    """
    Log(u"Getting video url for %s media"%mediaID)
    from types import StringType
    if not (type(mediaID) is StringType):
        raise AllocineError,"<mediaID> MUST be String type"
    if not quality:
        Log ("\tno quality given for video. HD quality used instead")
        quality="HD" #default max quality
    if not quality in ["HD","MD","LD"]:
        raise AllocineError,"<quality> MUST BE one of the followings : HD (or None), MD, LD"
    lq=["HD","MD","LD"]
    BA_path=""
    for q in lq[lq.index(quality):]:
        Log ("\ttrying %s quality"%q)
        if q=="HD":
            xml=download_html(ALLOCINE_DOMAIN + XML_BA_INFOS % mediaID + "&hd=1") #HD
        else:
            xml=download_html(ALLOCINE_DOMAIN + XML_BA_INFOS % mediaID) #LD et MD

        match = re.search(r'<video\s+title=".*?"\s+xt_title=".*?"\s+ld_path="(.*?)"\s+md_path="(.*?)"\s+hd_path="(.*?)".*?/>',xml)
        if match:
            if q=="LD" and match.group(1): BA_path = match.group(1)
            if q=="MD" and match.group(2): BA_path = match.group(2)
            if q=="HD" and match.group(3): BA_path = match.group(3)
            if BA_path:
                Log(u"\t%s quality successful for media"%q)
                break #si match non vide alors on quitte la boucle for
            else: Log ("\t%s quality not available !"%q)
        else:
            #raise AllocineError,"get_video_url did not match anything for the given mediaID. Make sure mediaID#%s on %s is valid."%(mediaID,ALLOCINE_DOMAIN)
            pass
    if not BA_path:
        return ""
        #raise AllocineError,"The media %s seems not contain videos from <%s> to worst quality(ies). Please try higher quality."%(mediaID,quality)
    else:
        return VIDEO_STREAM_URL % BA_path


class agenda:
    u"""Handler for agenda.

    Return movies for the week of the given date.
    """
    def __init__(self,periode=None):
        """Init the agenda handler with the optional <periode> parameter.
        If ommited, <periode> is set to None, which cause the date to be 'this week'.
        <periode> parameter can be:
            - 'now' or None (default) for the actual week
            - 'next' for the next week
            - or a dd/mm/yyyy format date for the corresponding week"""
        if not periode or periode == "now":
            self.HTML = download_html(ALLOCINE_DOMAIN + THIS_WEEK_URL)
        elif periode == "next":
            self.HTML = download_html(ALLOCINE_DOMAIN + AGENDA_URL)
        else:
            if re.match(r'\d\d/\d\d/\d\d\d\d',periode):
                #from time import strptime
                #year,month,day=strptime(periode,"%d/%m/%Y")[:3]#"%d/%m/%Y"
                self.HTML = download_html(ALLOCINE_DOMAIN + SORTIES_URL % periode)
            else:
                raise AllocineError,"<periode> parameter MUST be 'now' for the current week, 'next' for the next week, or a date 'DD/MM/YYYY' for the corresponding week"
        self.PERIODE = periode

    def __repr__(self):
        return "< AGENDA object for '%s' period >"%self.PERIODE

    def get_movies(self):
        """Return a bloc of html datas corresponding to films.
        (This should not be called, and is internally used)"""
        exp = re.compile(r'<a class="link1" href="(?:/film/)??fichefilm_gen_cfilm=\d+\.html">.*?(?:<hr />|</h5><br />)', re.DOTALL)
        movies = exp.findall(self.HTML)
        return movies

    def get_movies_datas(self):
        """Return informations about the films of the week.
        Result format is [ ( ID,Title,OriginalTitle,PictureURL,Genre,Lasts ) , ... ]"""
        datas=[]
        for moviedatas in self.get_movies():
            # id, titre et titre original
            match = re.search(r'<h2><a class="link1" href="(?:/film/)??fichefilm_gen_cfilm=(\d+)\.html">(.*?)</a></h2>(?:&nbsp;<h4>\((.*?)\)</h4>|)',moviedatas)
            if match:
                ID = match.group(1)
                Titre = match.group(2)
                TitreO = match.group(3)
            else:
                ID = Titre = TitreO = None
                
            #url de l'affiche
            match = re.search(r'<img src="(http://[./\w]+\.jpg)" border="0" alt=".+" class="affichette" />', moviedatas)
            if match:
                AfficheURL = match.group(1)
            else:
                AfficheURL = None
                
            #genre et durée
            match = re.search(r"<h5>(.*?)\((.*?)\)</h5>",moviedatas)
            if match:
                Genre = match.group(1)
                Duree = match.group(2)
            else:
                Genre = Duree = None
                
            #notes public
            match = re.search(r'<a href="(?:/film/)??critiquepublic_gen_cfilm=\d+\.html" class="link1">.*?</a> : <img src="[^"]+?empty\.gif" width="\d+" height="\d+" class="etoile_(\d{1})" border="0" />',moviedatas)
            if match:
                NotePublic = match.group(1)
            else:
                NotePublic = None
            #ajoute les données du film
            datas.append((ID,Titre,TitreO,AfficheURL,Genre,Duree,NotePublic))
            
        return datas

    def previous_week_date(self):
        u"""Return a string representing the week period preceding the actual period.
        Return now or next if needed, or a date in dd/mm/yyyy format"""
        if not self.PERIODE or self.PERIODE == "now":
            #cette semaine, on retourne self.PERIODE car on ne revient pas en arrière
            #à voir si c'est vrai ou pas
            return self.PERIODE #renvoi None ou 'now'
        elif self.PERIODE == "next":
            #semaine prochaine : on retourne "now" pour prendre la semaine actuelle
            return "now"
        else:
            match = re.search(ur'<a href="/film/agenda_gen_date=([/\d]+?)\.html" class="link1">(?:Semaine préc\.|Previous week|Anterior|Zurück)</a>',self.HTML)
            #   aide sur l'expression régulière  :                                                      FR             EN         ES      DE
            if match:
                return match.group(1)
            else:
                raise AllocineError,"the 'previous week' match did not succeed. Regular expression may need changes !"
        
    def next_week_date(self):
        u"""Return a string representing the week period following the actual period.
        Return 'next' if needed, or a date in dd/mm/yyyy format"""
        if not self.PERIODE or self.PERIODE == "now":
            #cette semaine, on retourne 'next' pour la semaine prochaine
            return 'next'
        else:
            #semaine prochaine OU tous les autres cas
            match = re.search(ur'<a href="/film/agenda_gen_date=([/\d]+?)\.html" class="link1">(?:Semaine (?:suiv\.|suivante)|Next week|Sigui?ente|Weiter)</a>',self.HTML)
            #   aide sur l'expression régulière                                                                   FR              EN       ES         DE
            if match:
                return match.group(1)
            else:
                raise AllocineError,"the 'next week' match did not succeed. Regular expression may need changes !"            

class Movies:
    u"""Movie object handler"""
    def __init__(self):
        self.Session = {}

    def new(self,IDmovie):
        """Return a Movie object with <IDmovie>.
        If Movie object with <IDmovie> already exists in the handler, return this object.
        Else, return a new Movie object
        """
        if self.Session.has_key(IDmovie):
            return self.Session[IDmovie]
        else:
            f = Movie(IDmovie)
            self.Session[IDmovie]=f
            return f
        
    def titles(self):
        u"""Get all movie title's handled.
        Return a list of tuples [ (id,title) , ... ]"""
        return [( movieID , self.Session[movieID].title() ) for movieID in self.Session.keys() ]

    def __repr__(self):
        return "<Handler for movies - contain now %s movie object's>"%len(self.Session)
    
            
class Movie:
    u"""Movie object instance."""
    def __init__(self,IDmovie):
        """Create a new Movie object with given ID.
        HTML movie page is fetched directly when instantiated.
        Movie infos are parsed with included functions"""
        Log( u"Getting movie ID#%s" )
        Log( ALLOCINE_DOMAIN + MOVIE_URL%IDmovie )
        
        self.ID=IDmovie
        self.HTML = download_html(ALLOCINE_DOMAIN + MOVIE_URL%self.ID)
        self.TITLE = ""
        self.ORIGINAL_TITLE = ""
        self.DATE = ""
        self.DIRECTOR = tuple()
        self.NATIONALITY = ""
        self.INFOS = ""
        self.SYNOPSIS = ""
        self.HAS_VIDEOS = False
        self.HAS_CASTING = False
        self.PHOTOS = []
        self.HAS_PHOTOS = False
        self.CASTING = dict()
        self.PICurl = ""
        self.MEDIAS = []
        #self.PARSEDflag = False

        #self.parser()
    def isvalid(self):
        """Return boolean depending if webpage is correct or not"""
        match = re.search(r"<title>.+</title>",self.HTML)
        if match: return True
        else: return False
        
    def director(self):
        u"""Return the director of the movie as a tuple ( ID , Name )"""
        #  a internationnaliser !
        #print self.HTML
        match = re.search(ur'<h3 class="SpProse">Réalisé par(.*?)</h3>',self.HTML)
        if match:
            direc = re.findall( '<a class="link1" href="/personne/fichepersonne_gen_cpersonne=(\d+)\.html">(.*?)</a>', match.group(1) )
            self.DIRECTOR = " / ".join( [ di[ 1 ] for di in direc ] )#(match.group(1),match.group(2))# id,nom
        else: self.DIRECTOR = ""#(None,None)
        return self.DIRECTOR

    def nationality(self):
        u"""Return the nationality of the movie as string."""
        match = re.search(r'<h4>(?:Film|Nationality :|Land:|Película) (.*?)[\.]?&nbsp;</h4><h4>(?:Genre|Género)',self.HTML)
        if match: self.NATIONALITY = match.group(1)
        else: self.NATIONALITY = "Not found !!"
        return self.NATIONALITY

    def infos(self):
        u"""Return textual global informations about the movie as string."""
        #la récupération suivante prend toutes les infos.
        #A voir si il faut filtrer les infos unitairement
        #INTERNATIONALISATION A FAIRE ! ! ! !
        match = re.search(r'<div style=".*?"><h4>(Date de sortie :.*?)(?:<h5>|<div id=\'divRecos\' style=\'width:175px\'>)',self.HTML)
        if match: self.INFOS = infos_text(match.group(1))
        else: self.INFOS = "No infos found"
        return self.INFOS.encode(ALLOCINE_ENCODING)

    def title(self):
        u"""Return the title of the movie."""
        match = re.search(r'<title>(.*?)- AlloCin.*?</title>',self.HTML)
        self.ORIGINAL_TITLE = ( re.compile( '<h3 class="SpProse">Titre original : <i>(.*?)</i></h3>' ).findall( self.HTML ) or [ "" ] )[ 0 ]
        if match: self.TITLE = match.group(1)
        elif self.ORIGINAL_TITLE: self.TITLE = self.ORIGINAL_TITLE
        else: self.TITLE = ""
        return self.TITLE.strip()

    def date(self):
        u"""Return the release date of the movie as string."""
        match = re.search(r'<h3 class="SpProse">.*?(\d+)/(\d+)/(\d+).html"',self.HTML)
        if match: self.DATE = "%s-%s-%s" % ( match.group(3), match.group(2), match.group(1), )
        else: self.DATE = ""        
        return self.DATE

    def year(self):
        regexp = '<h3 class="SpProse">.*?de production : (\d+)</h3>'
        try: year = re.compile( regexp ).findall( self.HTML )[ 0 ]
        except:
            year = self.date()
            if year: year = year.split( "-" )[ 0 ]
        return year

    def rate_and_vote(self):
        regexp = '<h4>Note moyenne.*?class="etoile_(\d+)" border.*?pour (\d+) critiques</h4>'
        return ( re.compile( regexp ).findall( self.HTML ) or [ ( "", "" ) ] )

    def fiche_tech(self):
        regexp = '<h2 class="SpBlocTitle" >Fiche Technique</h2>(.*?)</table>'
        tech = ( re.compile( regexp, re.DOTALL ).findall( self.HTML ) or [ "" ] )[ 0 ]
        fiche = []
        for text in re.findall( '<h4><b>(.*?)</b>(.*?)</h4><br />', tech ):
            fiche.append( "".join( list( text ) ) )
        return " | ".join( fiche )

    def tagline(self):
        regexp = '<h2 class="SpBlocTitle" >Secrets de tournage</h2>(.*?)</table></td></tr></table>'
        line = ( re.compile( regexp, re.DOTALL ).findall( self.HTML ) or [ "" ] )[ 0 ]
        tag = []
        for text in re.findall( '<h4><b>(.*?)</b></h4>.*?<h4>(.*?)</h4>', line ):
            tag.append( ": ".join( list( text ) ) )
        return " | ".join( tag )

    def studio(self):
        regexp = '<h3 class="SpProse">Distribu.*? par(.*?)</h3>'
        studios = re.compile( regexp, re.DOTALL ).findall( self.HTML ) or [ "" ]
        studios = re.findall( '<a href=".*?" class="link1">(.*?)</a>', studios[ 0 ] )
        return " / ".join( studios )
        
    def get_genre(self):
        regexp = '<a href="/film/alaffiche_genre_gen_genre=.*?" class="link1">(.*?)</a>'
        return " / ".join( re.compile( regexp, re.DOTALL ).findall( self.HTML ) )

    def get_runtime(self):
        regexp = '<h3 class="SpProse">Durée : (.*?)&nbsp;</h3>'
        return ( re.compile( regexp, re.DOTALL ).findall( self.HTML ) or [ "" ] )[ 0 ]

    def get_outline(self):
        regexp = '<div align="justify" style=".*?"><h4>(.*?)</h4></div><h4>'
        return " | ".join( re.compile( regexp, re.DOTALL ).findall( self.HTML ) )

    def synopsis(self):
        u"""Return the synopsis of the movie"""
        Log(u"Movie.synopsis() : Need to verify the regexp as it works on 'regexbuddy' but not in the library... why ?","D")
        #Alex: l'expression suivante fonctionne dans regexbuddy mais pas dans python... pkoi ??
        #Frost: cette expression marche avec "re.compile" et des fois non avec "re.search".
        match = re.search(ur'Synopsis.*?<td valign="top" style="padding:[\d ]+?"><div align="justify"><h4>(.*?)</h4>',self.HTML)
        if match:
            self.SYNOPSIS=infos_text(match.group(1))
            return self.SYNOPSIS.replace( "<br />", "\n" ).replace( "<br>", "" ).replace( "\r", "" ).encode(ALLOCINE_ENCODING)
        else:
            plot = re.compile( '<td valign="top" style="padding:[\d ]+?"><div align="justify"><h4>(.*?)</h4>', re.DOTALL ).findall( self.HTML )
            if plot: self.SYNOPSIS = plot[ 0 ]
            else: self.SYNOPSIS = ""
        return self.SYNOPSIS.replace( "<br />", "\n" ).replace( "<br>", "" ).replace( "\r", "" )#.encode(ALLOCINE_ENCODING)

    def has_videos(self):
        u"""Return a boolean whether the movie has video or not"""
        try:
            match = re.search(r'<a href="/video/player_gen_cmedia=\d+&cfilm=\d+\.html" class="link5">',self.HTML)
            if match:self.HAS_VIDEOS=True
            else: self.HAS_VIDEOS=False
        except:
            self.HAS_VIDEOS=False
        return self.HAS_VIDEOS

    def has_casting(self):
        u"""Return a boolean whether the movie has casting or not"""
        if self.HTML.count(CASTING_URL%self.ID): self.HAS_CASTING=True
        else: self.HAS_CASTING=False
        return self.HAS_CASTING
    
    def has_photos(self):
        u"""Return a boolean whether the movie has photos or not"""
        if self.HTML.count(PHOTOS_FILM_URL%self.ID): self.HAS_PHOTOS=True
        else: self.HAS_PHOTOS=False
        return self.HAS_PHOTOS

    def pictureURL(self):
        #print re.compile( '<img src="(.*?)" border=".*?" alt=".*?" class="affichette" />' ).findall( self.HTML )
        u"""Return the URL of the picture of the movie."""
        match = re.search(r'<img src="((http://[a-z0-9/\._]+?)(\.gif|\.jpg))" border=.*? class="affichette" />',self.HTML)
        if match: self.PICurl=match.group(1)
        else: self.PICurl=""
        return self.PICurl

##    def parser(self):
##        u"""Parse all informations available for the movie.
##        Does not return anything. The internal vars of the movie object are filled in"""
##        self.date()
####        match = re.search(r'<h4>[ \w]+? : <b>([\s\w\d].*?)</b>',self.HTML)
####        if match: self.DATE = match.group(1)
####        else: self.DATE = None
##        
##        self.director()
####        match = re.search(ur'<h4>Réalisé par <a class="link1" href="/personne/fichepersonne_gen_cpersonne=(\d+)\.html">(.*?)</a></h4>',self.HTML)
####        if match: self.DIRECTOR = (match.group(1),match.group(2))# id,nom
####        else: self.DIRECTOR = (None,None)
##        
##        self.nationality()
####        match = re.search(r'<h4>(?:Film|Nationality :|Land:|Película) (.*?)[\.]?&nbsp;</h4><h4>(?:Genre|Género)',self.HTML)
####        if match: self.NATIONALITY = match.group(1)
####        else: self.NATIONALITY = ""
##        
##        self.infos()
####        #la récupération suivante prend toutes les infos.
####        #A voir si il faut filtrer les infos unitairement
####        match = re.search(r'<div style=".*?"><h4>(Date de sortie :.*?)(?:<h5>|<div id=\'divRecos\' style=\'width:175px\'>)',self.HTML)
####        if match: self.INFOS = infos_text(match.group(1))
####        else: self.INFOS = "No infos found"
##        
##        self.title()
####        match = re.search(r'<title>(.*?)</title>',self.HTML)
####        if match: self.TITLE = match.group(1)
####        else: self.TITLE = ""
##        
##        self.date()
####        match = re.search(r'<h4>(?:Date de sortie |Theatrical release date |Fecha de estreno|Kinostart): <b>(\d+(?:\.)? \S+? \d{4}?)</b>',self.HTML)
####        if match: self.DATE=match.group(1)
####        else: self.DATE=""
##        
##        self.synopsis()
####        #l'expression suivante fonctionne dans regexbuddy mais pas dans python... pkoi ??
####        match = re.search(ur'<td valign="top" style="padding:[\d ]+?"><div align="justify"><h4>(.*?)</h4>',self.HTML)
####        if match: self.SYNOPSIS=infos_text(match.group(1))
####        else: self.SYNOPSIS = ""
##        
##        self.has_videos()#booleen qui permet de savoir si la fiche film propose des vidéos
####        match = re.search(r'<a href="(/video/player_gen_cmedia=\d+&cfilm=\d+\.html)" class="link5">',self.HTML)
####        if match:self.HAS_VIDEOS=match.group(1)
####        else: self.HAS_VIDEOS=False
##        
##        self.has_casting()
####        if self.HTML.count(CASTING_URL%self.ID): self.HAS_CASTING=True
####        else: self.HAS_CASTING=False
##
####        self.NOTES = tuple()
####        self.PICurl = ""
##
##        #when all parsing are done, flag it as parsed
##        self.PARSEDflag = True

    def get_photos(self):
        u"""Return photos list related to the movie.
        Return a list of tuple : [ ( PictureURL , PictureTitle ) , ... ]
        """
        if not self.has_photos(): raise AllocineError,"No photos for the movie ID#%s"%self.ID
        if not self.PHOTOS:
            html=download_html(ALLOCINE_DOMAIN + PHOTOS_FILM_URL%self.ID)#,os.path.join(CACHEDIR,"galery%s.html"%self.ID))
            exp = re.compile(r'{"\w+?":\d+,"\w+":"([a-z0-9\d/]+\.jpg)","\w+":"(.*?)"}')
            # VIDEO_STREAM_URL + picpath
            self.PHOTOS = [(PHOTOS_MEDIA_URL+picpath,unescape(title.decode(ALLOCINE_ENCODING))) for picpath,title in exp.findall(html)]
        return self.PHOTOS

    def get_casting(self):
        u"""Return the movie casting as a list of tuples :
        [ (Category, Job, PersonID, PersonName),(...) ...]
        """
        Log(u"Movie.get_casting : Need to make the get_casting function more fonctionnal... it does not work very well right now","D")
        castandrole = []
        productor = ""
        #if not self.has_casting(): raise AllocineError,"No casting for the movie ID#%s"%self.ID
        if self.has_casting():#else: #si le casting est vide
            html=download_html(ALLOCINE_DOMAIN + CASTING_URL%self.ID)#,os.path.join(CACHEDIR,"casting%s.html"%self.ID))
            try:
                for actor in re.compile( '>Casting complet</h2>(.*?)Production</h2>', re.DOTALL ).findall( html )[ 0 ].split( "</tr>" ):
                    actor_roll = re.findall( '<h5>(.*?)</h5>.*?"link1">(.*?)</a></h5>', actor, re.DOTALL )
                    if actor_roll:
                        thumb = ( re.findall( "<img src='(.*?)'", actor) or [ "" ] )[ 0 ]
                        ID = re.findall( "fichepersonne_gen_cpersonne=(\d+).html", actor )
                        castandrole.append(  { "ID": ID[ 0 ],  "name": actor_roll[ 0 ][ 1 ], "role": actor_roll[ 0 ][ 0 ], "thumb": thumb } )
            except:
                pass
            try:
                prod = ( re.compile( "Producteur(.*?)Producteur", re.DOTALL ).findall( html ) or [ "" ] )[ 0 ]
                productor = " / ".join( re.findall( 'class="link1">(.*?)</a>', prod ) )
            except:
                pass

        return castandrole, productor

    def get_mediaIDs(self):
        u"""Return media IDs for videos as a list of tuples :
            [ ( MediaID , PictureURL, Title ) , ... ]"""
        if not self.has_videos(): raise AllocineError,"No available media Video for the movie ID#%s"%self.ID #retourne si pas de videos pour le film
        if not (self.MEDIAS):
            self.MEDIAS=[]
            #1- on récupère les datas javascripts contenant toutes les vidéos
            exp=re.compile(r"contenu = new Array\('(.+)'\)|contenu.push\('(.+)'\)")
            datas=exp.findall(self.HTML)
            #2- on récupre toutes les vidéos sous forme [(idmedia,urlimage,titre), ... ]
            exp=re.compile(r'<a href="/video/player_gen_cmedia=(\d+)&cfilm=\d+\.html"><img src="(http://[\.\w/-_]+)" width="100" height="80" border="0" alt="(.*?)"></a>')
            for datamedia in datas:
                match = exp.search("".join(datamedia))
                if match:self.MEDIAS.append((match.group(1),match.group(2),unescape(match.group(3).decode(ALLOCINE_ENCODING))))
                else: Log(u"Movie.get_mediaIDs() : No match for these media datas","W")
        return self.MEDIAS

    def BAurl(self, maxi=0):
        u"""Return the first mediaID video url found for the current movie
        """
        playlist = []
        if self.has_videos():
            if DIALOG_PROGRESS:
                DIALOG_PROGRESS.update( -1, "Récupération des bandes-annonces..." )
            mediaList = self.get_mediaIDs()
            if not maxi or maxi > len( mediaList ):
                maxi = len( mediaList )
            for IDmedia,PICurl,title in mediaList[ :maxi ]:
                if DIALOG_PROGRESS:
                    DIALOG_PROGRESS.update( -1, "Récupération de la bande-annonce...", title )
                vidurl = get_video_url(IDmedia)
                if vidurl:
                    playlist.append( ( title, PICurl, vidurl ) )
                    #break
            #return vidurl
            return playlist
        else:
            raise AllocineError,"No available media Video for the movie ID#%s"%self.ID

    def XML(self, fpath="", passion_fanart=False, clear_actor="false", clear_genre="false", clear_studio="false", clear_credits="false", clear_director="false" ):
        # non prioritaire !!
        u"""TO DO !!
        Will return a string in XML format with all infos of the Movie.
        Clients will use this XMLstream as they want (save file, parse it...)
        """
        #A FAIRE ! !
        # et il faudra définir un format de XML intéressant
        #Log(u"Movie.XML() : XML output is not supported yet","D")
        #if fpath:
        #f.write( "\t<>" +  + "</>\n" )

        nfo_file = os.path.join( fpath, "%s.xml" % self.ID )
        f = open( nfo_file, "w" )

        f.write( "<movie>\n" )
        f.write( "\t<!-- AlloCine: Video nfo File created on: %s -->\n" % ( time.strftime( "%d-%m-%Y | %H:%M:%S" ) ) )
        f.write( "\t<id>" + self.ID + "</id>\n" )
        f.write( "\t<title>" + self.title() + "</title>\n" )
        f.write( "\t<originaltitle>" + self.ORIGINAL_TITLE + "</originaltitle>\n" )
        f.write( "\t<date>" + self.date() + "</date>\n" )
        f.write( "\t<year>" + self.year() + "</year>\n" )
        f.write( "\t<runtime>" + self.get_runtime() + "</runtime>\n" )
        f.write( "\t<plot>" + self.set_pretty_formatting( self.synopsis() ) + "</plot>\n" )
        f.write( "\t<outline>" + self.set_pretty_formatting( self.get_outline() ) + "</outline>\n" )
        f.write( "\t<tagline>" + self.set_pretty_formatting( self.tagline() ) + "</tagline>\n" )
        rate, vote = self.rate_and_vote()[ 0 ]
        f.write( "\t<rating>" + rate + "</rating>\n" )
        f.write( "\t<votes>" + vote + "</votes>\n" )
        f.write( "\t<mpaa>" + self.set_pretty_formatting( self.fiche_tech() ) + "</mpaa>\n" )
        #f.write( '\t<genre clear="%s">%s</genre>\n' % ( clear_genre, self.get_genre(), ) )
        #f.write( '\t<studio clear="%s">%s</studio>\n' % ( clear_studio, self.studio(), ) )
        #f.write( '\t<director clear="%s">%s</director>\n' % ( clear_director, self.director()[ 1 ], ) )
        f.write( '\t<genre>%s</genre>\n' % ( self.get_genre(), ) )
        f.write( '\t<studio>%s</studio>\n' % ( self.studio(), ) )
        f.write( '\t<director>%s</director>\n' % ( self.director(), ) )
        castandrole, productor = self.get_casting()
        #f.write( '\t<credits clear="%s">%s</credits>\n' % ( clear_credits, productor, ) )
        f.write( '\t<credits>%s</credits>\n' % ( productor, ) )

        #castings
        for actor in castandrole:
            #f.write( '\t<actor clear="%s">\n' % clear_actor )
            f.write( '\t<actor>\n' )
            f.write( "\t\t<id>" + actor.get( "ID", "" ) + "</id>\n" )
            f.write( "\t\t<name>" + actor.get( "name", "" ) + "</name>\n" )
            f.write( "\t\t<role>" + actor.get( "role", "" ) + "</role>\n" )
            f.write( "\t\t<thumb>" + actor.get( "thumb", "" ) + "</thumb>\n" )
            f.write( "\t</actor>\n" )

        #posters and fanarts
        if not passion_fanart: posters, fanarts, actors = [], [], []
        else: posters, fanarts, actors = passion_fanarts( self.ID )

        icon_allocine = self.pictureURL()
        if posters or icon_allocine:
            f.write( "\t<thumbs>\n" )
            #vignettes passion-xbmc
            if posters:
                for poster in posters:
                    f.write( "\t\t<thumb>" + poster + "</thumb>\n" )
            #vignettes allocine
            if icon_allocine:
                f.write( "\t\t<thumb>" + icon_allocine + "</thumb>\n" )
            f.write( "\t</thumbs>\n" )

        if fanarts or self.has_photos():
            f.write( "\t<fanart>\n" )
            #fanarts passion-xbmc
            if fanarts:
                for fanart in fanarts:
                    f.write( "\t\t<thumb>" + fanart + "</thumb>\n" )
            #fanarts allocine
            if self.has_photos():
                for photo in self.get_photos():
                    f.write( "\t\t<thumb>" + photo[ 0 ] + "</thumb>\n" )
            f.write( "\t</fanart>\n" )

        # add trailer if exists
        if self.has_videos():
            mediaIDs = self.get_mediaIDs()
            trailer = get_video_url( mediaIDs[ 0 ][ 0 ] )
            if trailer: f.write( "\t<trailer>" + trailer + "</trailer>\n" )

        #end close nfo
        f.write( "</movie>\n" )

        # add mix of XML and URL
        if "true" in ( clear_actor, clear_genre, clear_studio, clear_credits, clear_director ):
            url = ALLOCINE_DOMAIN + MOVIE_URL % self.ID
            f.write( "%s\n" % ( url, ) )
        f.close()
        return nfo_file

        #not used for a moment
        #print self.nationality()
        #print self.infos()
        #return ""

    def set_pretty_formatting( self, text, by="" ):
        text = text.replace( "<br />", "\n" )
        text = text.replace( "<i>", "[I]" ).replace( "</i>", "[/I]" )
        text = text.replace( "<b>", "[B]" ).replace( "</b>", "[/B]" )
        #text = re.sub( "(?s)</[^>]*>", "[/B]", text )
        #text = re.sub( "(?s)<[^>]*>", "[B]", text )
        return text

    def __repr__(self):
        return "< Allocine movie object ID#%s >"%self.ID

class SearchOLD:
    def __init__(self):#,keyword,searchtype="0"):
        #/recherche/?motcle=""&rub=
        #   0 - tout allocine
        #   1 - les films
        #   2 - les stars
        #   3 - les salles
        #   4 - les localités
        #   5 - les articles
        #   6 - les séries TV
        #   8 - les sociétés
        #   10- les tags
        #   13- les blogs

##        #basic checkings
##        from types import StringType
##        if not (type(searchtype) is StringType): raise AllocineError, "Type for <searchtype> argument MUST be string. (searchtype argument is now %s)"%type(searchtype)
##        if not (type(keyword) is StringType): raise AllocineError, "Type for <keyword> argument MUST be string. (keyword argument is now %s)"%type(keyword)

        self.HAS_NEXT = False #booleen pour savoir si la recherche contient une page de résultat suivante
        self.KW = ""#keyword
        self.TYPE = "0"#searchtype
        self.RESULTS_PER_PAGE = [] #the results on only one page
        self.RESULTS_ALL = [] #all differents results found for this search
        self.REGEXP = { "1" : r'<a href="/film/fichefilm_gen_cfilm=(\d+)\.html"><img src="(http:[a-z0-9/\.-]+?)"[^/]*?/>.*?</a></td><td valign="top"><h4><a href="/film/fichefilm_gen_cfilm=\1\.html" class="link1">(.*?)</a></h4>',
                        "2" : r'<a href="/personne/fichepersonne_gen_cpersonne=(\d+)\.html"><img src="(http:[a-z0-9/\.-]+?)"[^/]*?/>.*?</a></td><td valign="top"><h4><a href="/personne/fichepersonne_gen_cpersonne=\1\.html" class="link1">(.*?)</a>', #REGEXP est utilisé également pour connaitre les recherches supportées
                        "3" : r'<a href="/seance/salle_gen_csalle=([A-Za-z0-9]+)\.html" class="link1">(.*?)<hr />',
                        'etc':'etc'
                        }
        #getting allocine search themes
        self.SEARCH_THEMES = self.get_Themes()
        #print "\n".join(["%s : %s"%(tid,self.SEARCH_THEMES[tid]) for tid in self.SEARCH_THEMES.keys()])
        ##advanced checkings
        #if not searchtype in self.SEARCH_THEMES.keys(): raise AllocineError,"If given, <searchtype> argument MUST be one of the followings : "+self.SEARCH_THEMES.keys()

        #if not searchtype in self.REGEXP.keys(): raise AllocineError,"Sorry, '%s' search is currently not supported. Supported search(s) is(are) %s."%(self.SEARCH_THEMES[searchtype],
        #                                                                                                                                          ",".join(self.SEARCH_THEMES.values())
        #                                                                                                                                          )
        #routage
        #if searchtype in self.REGEXP.keys():
        #    self.search(keyword,searchtype)
            
    def supported(self):
        u"""
        retourne un dictionnaire des recherches disponibles sur le site et supportées par la librairie
        """
        return dict( [ (thid,self.SEARCH_THEMES[thid]) for thid in set(self.REGEXP.keys()).intersection(self.SEARCH_THEMES.keys())])    
        
    def get_type(self):
        u"""
        Return the associated name of the type of search
        """
        return self.SEARCH_THEMES[self.TYPE]
            
    def get_Themes(self):
        u"""
        Return a dictionnary with themesID as int and themes name as string
        """
        html=download_html(ALLOCINE_DOMAIN + SEARCH_URL)
        exp=re.compile(r'<option value="(\d+)" (?:selected="selected" )?/>([^<\t]*)')
        types = exp.findall(html)
        return dict([(tid,unescape(tname.decode(ALLOCINE_ENCODING))) for tid,tname in types])

                        
    def search(self,keyword="",Type="0",next=None):
        u"""
        Search in <Type> for <keyword> results
        Return a list with (id,text,title)
            -id for the id of the searched item
            -text for something interesting (i.e: picture url)
            -title for the label to give to the found items
        """
        keyword=keyword.encode(ALLOCINE_ENCODING)
        if next and self.HAS_NEXT: page="&page="+next
        else: page =""
        #on va remplir une liste de résultats
        html = download_html(ALLOCINE_DOMAIN + SEARCH_URL + "?motcle=%s&rub=%s"%(keyword,Type) + page)
        #parser html selon le theme
        exp=re.compile(self.REGEXP[Type]) #ATTENTION, le parser doit retourner l'ID de l'élément considéré ainsi que son libellé
        results = exp.findall(html)
        results = [ (id,text,infos_text(title).replace("\n","")) for id,text,title in results ]
        #rechercher
        if results: # en cas de résultats ...
            self.HTML = html #... on mémorise le code HTML
            self.KW = keyword #... on mémorie le mot clé
            self.TYPE = Type #... on mémorise le type de recherche
            self.HAS_NEXT = self.has_next() #... on cherche si éventuellement la page contient d'autres résultats et on mémorise
            self.RESULTS_ALL= self.RESULTS_ALL + results #... on ajoute les résultats à tous les autres résultats précédents
            self.RESULTS_PAGE = results#... on mémorise les derniers résultats trouvés
            return results
        else:
            raise AllocineError, "Search in '%s' (%s) for '%s' did not match anything."%(self.SEARCH_THEMES[Type],Type,keyword) 


        
    
    def has_next(self):
        u"""
        Return wether or not, the search results contain a 'next page' link
        Return False if no other page or page number if next page
        """
        match=re.search(ur'<a href="/recherche/default\.html\?motcle=.*?&rub=\d*?&page=(\d*)" class="link1">.*?</a>&nbsp;',self.HTML)
        if match: self.HAS_NEXT = match.group(1)
        else: self.HAS_NEXT = None
        return self.HAS_NEXT
        #A FAIRE
        
        
    def next_results(self):
        u"""
        Récupère la prochaine page de résultats
        """
        if self.has_next(): return self.search(self.KW,self.TYPE,self.HAS_NEXT)

    def __repr__(self):
        return "< Allocine Search instance [keyword=%s , Theme_searched=%s]>"%(self.KW,self.TYPE)


class Search:
    """Class to search for allocine content"""
    def __init__(self,keyword="",searchtype="0"):
        """INITialise vars and check of searchtype is correct (i.e. the searchtype is supported by the website AND by the library).
        Client SHOULD check for available searchs before instantiate a search."""
        from urllib import quote
        self.KW               = quote(keyword)#.decode(ALLOCINE_ENCODING)
        self.TYPE             = searchtype
        self.HAS_NEXT         = False #booleen pour savoir si la recherche contient une page de résultat suivante
        self.HAS_PREVIOUS     = False #booleen pour savoir si la recherche contient une page de résultat précédente
        self.CURRENT_PAGE     = "1"
        self.RESULTS_PER_PAGE = [] #the results on only one page
        self.RESULTS_ALL      = [] #all differents results found for this search
        self.HTML             = ""
        self.SEARCH_THEMES    = self.get_Themes()
        #check if searctype is supported by the website
        if not self.TYPE in self.SEARCH_THEMES.keys():
            raise AllocineError,"The search ID you asked for is not available for this website. Available web site searchs are %s"%", ".join(self.SEARCH_THEMES.keys())
        
        AvailableRegexp = { "1" : r'<a href="/film/fichefilm_gen_cfilm=(\d+)\.html"><img src="(http:[-_/a-z0-9\.]+?)"[^/]*?/>.*?</a></td><td valign="top"><h4><a href="/film/fichefilm_gen_cfilm=\1\.html" class="link1">(.*?)</a></h4>',
                            "2" : r'<a href="/personne/fichepersonne_gen_cpersonne=(\d+)\.html"><img src="(http:[-_/a-z0-9\.]+?)"[^>]*>(|<br/><img border="0" src="(http:[-_/a-z0-9\.]+?)"[^>]*>)</a></td><td valign="top"><h4><a href="/personne/fichepersonne_gen_cpersonne=\1\.html" class="link1">(.*?)</a>',#r'<a href="/personne/fichepersonne_gen_cpersonne=(\d+)\.html"><img src="(http:[a-z0-9/\.-_]+?)"[^/]*?/>.*?</a></td><td valign="top"><h4><a href="/personne/fichepersonne_gen_cpersonne=\1\.html" class="link1">(.*?)</a>', #REGEXP est utilisé également pour connaitre les recherches supportées
                            "3" : r'<a href="/seance/salle_gen_csalle=([A-Za-z0-9]+)\.html" class="link1"([^>]*)>(.*?)<hr />'
                            }
        #check if searchtype is supported by the library
        if not self.TYPE in AvailableRegexp.keys(): raise AllocineError,u"Type of search #%s is not supported. Should be in %s"%(self.TYPE,AvailableRegexp.keys())
        else: self.REGEXP = AvailableRegexp[self.TYPE]

    def result_number(self):
        u"""Return number of results for the search"""
        Log(u"Search.result_number() : need to parse HTML to get results number. Need some more tests.","D")
        if not self.HTML:
            raise AllocineError,"To get result number for the search, you fist MUST run search() function"
        return len(self.RESULTS_ALL)
    
    def get_Themes(self):
        u"""Return available search types of the website used.
        Return format is a dictionnary with themeID as key and themeName as value."""
        html=download_html(ALLOCINE_DOMAIN + SEARCH_URL)
        exp=re.compile(r'<option value="(\d+)" (?:selected="selected" )?/>([^<\t]*)')
        types = exp.findall(html)
        return dict([(tid,unescape(tname.decode(ALLOCINE_ENCODING))) for tid,tname in types])
    
    def search(self,nextpage=None):
        u"""Start the search and return a list of tuples [ (id,text,title) , ... ]
        If <nextpage> is not given, first page of results is returned."""
        if nextpage: page="&page="+nextpage
        else: page =""
        html = download_html(ALLOCINE_DOMAIN + SEARCH_URL + "?motcle=%s&rub=%s"%(self.KW,self.TYPE) + page)
        #parser html selon le theme
        exp=re.compile(self.REGEXP)
        results = exp.findall(html)
        results = [ (id,text,infos_text(title).replace("\n","")) for id,text,title in results ]
        if results: # en cas de résultats ...
            self.HTML = html
            self.CURRENT_PAGE = nextpage #... la page en cours de traitement est mémorisée
            self.HAS_NEXT = self.has_next() #... on cherche si éventuellement la page contient d'autres résultats et on mémorise le numéro de page suivante
            self.HAS_PREVIOUS = self.has_previous() #... on cherche si éventuellement la page contient d'autres résultats et on mémorise le numéro de page précédente
            self.RESULTS_ALL= list(set(self.RESULTS_ALL + results)) #... on ajoute les résultats à tous les autres résultats précédents
            self.RESULTS_PAGE = results#... on mémorise les derniers résultats trouvés
            #print "current:",self.CURRENT_PAGE
            #print "next:",self.HAS_NEXT
            #print "previous:",self.HAS_PREVIOUS
            return results
        else:
            #raise AllocineError, "Search in '%s' (%s) for '%s' did not match anything."%(self.SEARCH_THEMES[self.TYPE],self.TYPE,self.KW.decode(ALLOCINE_ENCODING))
            Log(u"Search in '%s' (%s) for '%s' did not match anything."%(self.SEARCH_THEMES[self.TYPE],self.TYPE,self.KW.decode(ALLOCINE_ENCODING)))
            return []

    def nbresults(self):
        u"""Return the number of results as mentionned in the web page."""
        match=re.search(ur'<h4>\((\d+) .*\)</h4>',self.HTML)
        if match: return match.group(1)
        else: return "0"
        
    def has_next(self):
        """
        Return wether or not, the search results contain a 'next page' link
        Return False if no other page or page number if next page
        """
        match=re.search(ur'<a href="/recherche/default\.html\?motcle=[^&]*?&rub=\d*?&page=(\d*)" class="link1">[^<]+</a>&nbsp;',self.HTML)
        if match: return match.group(1)
        else: return False

    def next(self):
        u"Continue la recherche sur la page suivante"
        if self.has_next(): return self.search(self.has_next())
        else:
            Log(u"Search do not have more page results","I")
            return []#raise AllocineError, u"Search do not have more page results"

    def has_previous(self):
        """
        Return wether or not, the search results contain a 'previous page' link
        Return False if no other page or page number if previous page
        """
        match=re.search(ur'&nbsp;<a href="/recherche/default\.html\?motcle=[^&]*?&rub=\d*?&page=(\d*)" class="link1">[^<]+</a>',self.HTML)
        if match: return match.group(1)
        else: return False
        
    def previous(self):
        u"Continue la recherche sur la page précédente"
        if self.has_previous(): return self.search(self.has_previous())
        else:
            Log(u"Search do not have previous page results","I")
            return []#raise AllocineError, u"Search do not have more page results"
    
    def current(self):
        u"""Return current page of results"""
        return self.CURRENT_PAGE
    

class Movie_search(Search):#inutilisé, pour tests et conservé pour mémoire
    def __init__(self,kw):
        Search.__init__(self,kw,"1")
        self.REGEXP = r'<a href="/film/fichefilm_gen_cfilm=(\d+)\.html"><img src="(http:[a-z0-9/\.-_]+?)"[^/]*?/>.*?</a></td><td valign="top"><h4><a href="/film/fichefilm_gen_cfilm=\1\.html" class="link1">(.*?)</a></h4>'

        
class Personality:
    u"""Person Handler."""
    def __init__(self,IDperso):
        u"""Initialise vars and get source page for the requested <IDperso>."""
        self.ID = IDperso
        self.HTML = download_html(ALLOCINE_DOMAIN + PERSO_URL%self.ID)
        self.NAME = ""
        self.JOBS = ""
        self.BIRTH =""
        self.PICurl = ""
        self.BIO = ""
        self.HAS_PHOTO = None
        self.PHOTOS = []
        self.HAS_VIDEOS = None
        self.MEDIAS = None
        self.parser()

    def isvalid(self):
        """Return boolean depending if webpage is correct or not"""
        match = re.search(r"<title>.+</title>",self.HTML)
        if match: return True
        else: return False

    def parser(self):
        u"""Parse all informations available for the personnality.
        Does not return anything. The internal vars of the movie object are filled in."""
        self.nom = ""
        self.PICurl = ""

    def name(self):
        u"""Return personnality name."""
        if not self.NAME:
            match=re.search(r'<title>(.*?)</title>',self.HTML)
            if match: self.NAME=match.group(1)
            else: self.NAME="Not found"
        return self.NAME

    def jobs(self):
        u"""Return cinema functions (jobs) of the personnality."""
        if not self.JOBS:
            match=re.search(r'<div><h4><b>(.*?)</b></h4></div>',self.HTML)
            if match: self.JOBS = match.group(1)
            else: self.JOBS = "Not found !"
        return self.JOBS
    
    def pictureURL(self):
        u"""Return personnality portrait url"""
        if not self.PICurl:
            match=re.search(r'<img src="(http://[\w\./_-]+)" width="\d+" height="\d+" border="0"><br />',self.HTML)
            if match: self.PICurl = match.group(1)
            else: self.PICurl = None
        return self.PICurl
    
    def birth(self):
        u"""Return birth infos."""
        if not self.BIRTH:
            match = re.search(r'<h4><div[^>]+>(.*?)</h4></div>',self.HTML)
            if match: self.BIRTH = match.group(1)
            else: self.BIRTH = "Not found !"
        return self.BIRTH

    def Biography(self,force=False):
        u"""Return biography of the personnality.
        FR, EN and ES websites are supported only. DE website does not expose the biography.
        Set <force> to True to force parsing datas if needed.
        Return format is a list [ biography (string), movies (list), personnalities (list) ]
            movies contain [(movieID,movieTitle),...] as quoted in the biography
            personnalities contain [(persoID,persoName),...] as quoted in the biography"""
        if not (self.BIO) or force:
            match=re.search(ur'<h3><b>(?:Biographie|Biography|Biografie|Biografía)</b></h3>(.*?)</table>',self.HTML)
            #  match for countries :       FR           EN       DE         ES
            if match: datas = match.group(1)
            else: return ["No Biography available",[],[]]
            bio = infos_text(datas)
            exp=re.compile(r'<a class="link1" href="/personne/fichepersonne_gen_cpersonne=(\d+)\.html">(.*?)</a>')
            persos = exp.findall(datas)
            exp=re.compile(r'<a class="link1" href="/film/fichefilm_gen_cfilm=(\d+)\.html"><b>(.*?)</b></a>')
            movies = exp.findall(datas)
            self.BIO = [bio,movies,persos]
        return self.BIO

    def Filmography(self,force=False):
        u"""Return filmography of the personnality.
        NOT FULLY WORKING"""
        Log(u"Personnality.Filmography() is not fully working yet. Need improvments !!","D")
        ## NON FONCTIONNEL... A refaire plus complet ultérieurement
        #il faut télécharger la page de filmographie
        if not(self.FILMO) or force:
            match=re.search(r'<table cellpadding="0" cellspacing="0" border="0" width="100%">.*?</table>\r',self.HTML)
            if match:#il faut parser le resultat
                exp=re.compile(r'<h4><a href="/film/fichefilm_gen_cfilm=(?P<idfilm>\d+)\.html" class="link1"><b>(?P<title>[^<]+?)</b></a>(?: \((?P<year>[\w ]+)\))*(?:, [.\w]+ <a class="link1" href="/personne/fichepersonne_gen_cpersonne=(?P<idperson>\d+).html">(.*?)</a>)*</h4>')
                self.FILMO=exp.findall(match.group())
                return self.FILMO
            else:
                pass
                        
    def has_photos(self):
        u"""Return a boolean whether personnality has photos related or not"""
        if self.HTML.count(PHOTOS_PERSON_URL%self.ID): self.HAS_PHOTOS=True
        else: self.HAS_PHOTOS=False
        return self.HAS_PHOTOS
    
    def get_photos(self,force=False):
        u"""Return related photos for the personnality.
        return is a list of tuples : [ ( PicturePath , PictureTitle ) , ... ]"""
        if not self.has_photos(): raise AllocineError,"No photos for the personnality ID#%s"%self.ID
        if not (self.PHOTOS) or force:
            html=download_html(ALLOCINE_DOMAIN + PHOTOS_PERSON_URL%self.ID)
            exp = re.compile(r'{"\w+?":\d+,"\w+":"([a-z0-9\d/]+\.jpg)","\w+":"(.*?)"}')
            self.PHOTOS = [(PHOTOS_MEDIA_URL+picpath,unescape(title.decode(ALLOCINE_ENCODING))) for picpath,title in exp.findall(html)]
        return self.PHOTOS

    def has_videos(self):
        u"""Return a boolean whether personnality has videos related or not"""
        match = re.search(r'<a href="(/video/player_gen_cmedia=\d+&cpersonne=\d+\.html)" class="link5">',self.HTML)
        if match:self.HAS_VIDEOS=match.group(1)
        else: self.HAS_VIDEOS=False
        return self.HAS_VIDEOS
    
    def get_mediaIDs(self,force=False):
        u"""Return media IDs for videos as a list of tuples :
            [ ( MediaID , PictureURL, Title ) , ... ]"""
        if not self.has_videos(): raise AllocineError,"No available media Video for the personnality ID#%s"%self.ID #retourne si pas de videos pour le film
        if not (self.MEDIAS) or force:
            self.MEDIAS=[]
            #1- on récupère les datas javascripts contenant toutes les vidéos
            exp=re.compile(r"contenu = new Array\('(.+)'\)|contenu.push\('(.+)'\)")
            datas=exp.findall(self.HTML)
            #2- on récupre toutes les vidéos sous forme [(idmedia,urlimage,titre), ... ]
            exp=re.compile(r'<a href="/video/player_gen_cmedia=(\d+)&cpersonne=\d+\.html"><img src="(http://[\.\w/-_]+)" width="100" height="80" border="0" alt="(.*?)"></a>')
            for datamedia in datas:
                match = exp.search("".join(datamedia))
                if match:self.MEDIAS.append((match.group(1),match.group(2),unescape(match.group(3).decode(ALLOCINE_ENCODING))))
                else: Log(u"Personality.get_mediaIDs() : No match for these media datas","W")
        return self.MEDIAS
    
    def __repr__(self):
        return "< Allocine character object ID#%s >"%self.ID

    
class Cinemas:
    def __init__(self):
        self.HTML = ""
        self.Session = {}
        
    def new(self,CID):
        """Create a new cinema object if needed"""
        if self.Session.has_key(CID):
            return self.Session[CID]
        else:
            c = Cinema(CID)
            self.Session[CID]=c
            return c
    def discard(self,CID):
        """Discard from Cinemas Handler, the #<CID> cinema"""
        if self.Session.has_key(CID):
            self.Session.pop(CID)
            
    def whereplaying(self,MID):
        """Browse all Cinema instance handled by Cinemas and return a list of Cinema IDs where playing the #<MID> movie"""
        playingIn = {}
        for CID in self.Session.keys():
            if self.Session[CID].isplaying(MID):
                playingIn[CID] = self.Session[CID]
        return playingIn[CID]
    
            
            
class Cinema:
    def __init__(self,CID):
        self.CID=CID
        self.HTML = download_html(ALLOCINE_DOMAIN + CINEMA_URL%self.CID )
        self.TIMETABLE={}
        self.maketimetable() #launch the making of the time table
    def name(self):
        u"""Return the name of the Cinema."""
        Log(u"Cinema.name : TODO","D")
        return self.address().split("-")[0]
    def address(self):
        u"""return the address of the cinema."""
        #match=re.search(ur'</SCRIPT>\s*<h4 style="[^>]+>(.*?)</a><a href="/salle/fichesalle_gen_csalle=[A-Za-z0-9]+\.html">',self.HTML,re.DOTALL)
        match=re.search(r'<meta name="description" content="(.*?)">',self.HTML,re.DOTALL)
        if match: return infos_text(match.group(1).replace("\n",""))
        else: return "not found"
    def movies(self):
        u"""Return movies playing in the Cinema"""
        MOVIES = {}
        Log(u"Cinema.movies(MID) : make it better to catch infos singlely, and to prevent a no match at all when only one of the movie ino is not found","D")
##        for MovieBlocMatch in re.finditer(r'<a class="link1" href="/film/fichefilm_gen_cfilm=(\d+)\.html"><img src="([a-zA-Z0-9/:\._\-]+)"[^/]+/></a></td><td[^>]+>.*?<table[^>]+><tr>(.*?)</tr><tr>(.*?)</tr>.*?<tr><td[^>]+><h5 style="color:#808080">(.*?)</h5></td></tr>',self.HTML):
##            MOVIES[MovieBlocMatch.group(1)] = [infos_text(MovieBlocMatch.group(3)),MovieBlocMatch.group(2),infos_text(MovieBlocMatch.group(4)),infos_text(MovieBlocMatch.group(5))]
##        print MOVIES
        for MovieBlocDatas in re.finditer(r'<a class="link1" href="/film/fichefilm_gen_cfilm=\d+\.html"><img.*?\r',self.HTML):
            #ID and picture URL
            match = re.search(r'<a class="link1" href="/film/fichefilm_gen_cfilm=(\d+)\.html"><img src="([a-zA-Z0-9/:\._\-]+)"[^/]+/></a>',MovieBlocDatas.group(0))
            if match:
                MID = match.group(1)
                pictureURL = match.group(2)
            else:
                raise
            #title
            match = re.search(r'<h2><a class="link1" href="/film/fichefilm_gen_cfilm=%s\.html">(.*?)</a>'%MID,MovieBlocDatas.group(0))
            if match: title=match.group(1)
            else: title = "Not Found !"
            #genre and lasting
            match = re.search(r'<h5>([^\(]+)\((\d+h(?: \d+min)?)\)</h5>',MovieBlocDatas.group(0))
            if match:
                genre=match.group(1)
                duree=match.group(2)
            else:
                genre="Not Found !!"
                duree="Not Found !!"
            match = re.search(r'<h5 style="color:#808080">(.*?)</h5>',MovieBlocDatas.group(0))
            if match: synopsis=match.group(1)
            else: synopsis="Not Found !!"
            MOVIES[MID]=[title,pictureURL,genre,duree,synopsis]
        #print MOVIES            

    def isplaying(self,MID):
        u"""Return True/False whether movie #<MID> is playing in this Cinema or not."""
        if MID in self.TIMETABLE: return True
        else: return False

    def maketimetable(self):
        """Feed and return timetable for all movies in this Cinema
        {IDmovie : [ [day1,scheduling], [day2,scheduling], ... ], .... }"""
        #htmlMovieDataBlocs = re.findall(r'<a class="link1" href="/film/fichefilm_gen_cfilm=\d+\.html"><img.*?\r',self.HTML)
        #TimePlayingMoviesBlocs = re.findall(r'<tr><td[^>]+><table[^>]+>.*?(?:<div id="div_seance\d+_jour\d"[^>]+>).*?\r',self.HTML)
        #CalendarInfoBlocs = re.findall(r'<table[^>]+>\s+<tr>\s+(<td id="td_(seance\d+_jour\d)"[^>]+>\s+<h5 id="h5_\2"[^>]+>.*?</h5>\s+</td>\s+)+</tr>\s+</table>',self.HTML)
        #cinema page is made of :
        #   - one bloc of html datas for movie infos
        #   - one or more bloc made of :
        #       - one bloc of calendar infos (each day that has scheduling, has a link)
        #       - one bloc of scheduling infos
        #the idea is to browse all this big blocs (for each movie).
        #For on movie bloc, get the Movie ID, get the html infos of the movie, get a list of all links per day
        #   then, for any of these days, we find the corresponding schedule using 'seanceXX_jourX' string as key
        #get a big bloc of html datas
        for match in re.finditer(r'<a class="link1" href="/film/fichefilm_gen_cfilm=(\d+)\.html"><img.*?(?:</td></tr><tr><td colspan="2"><hr|</td></tr></table><br />)',self.HTML,re.DOTALL):
            MID = match.group(1)
            MovieBlocMatch = re.match(r'<a class="link1" href="/film/fichefilm_gen_cfilm=\d+\.html"><img.*?\r',match.group())
            MovieDataBloc = MovieBlocMatch.group(0)
            DayLinks = re.findall(r'<h5 id="h5_(seance\d+_jour\d+)"[^>]+><a href="javascript:change_seance_jour\(\d+, \d\);"[^>]+>(.*?)(?:</a>)?</h5>',match.group())
            for repere,date in DayLinks:
                match2=re.search(r'<div id="div_%s"[^>]+>(.*?)</table></div>'%repere,match.group(0))
                if match2:
                    if MID in self.TIMETABLE:
                        self.TIMETABLE[MID].append([date,infos_text(match2.group(1))])
                    else:
                        self.TIMETABLE[MID]=[[date,infos_text(match2.group(1))]]
                else:
                    Log("Cinema.maketimetable() : No match for given day.","E")

        return self.TIMETABLE
            
    def get_schedule(self,MID):
        """Return scheduling for the <MID> movie in this Cinema.
        [ [day1, [ (timestart,timeend) , ... ]] , [day2, [ (timestart,timeend) , ... ]] , ... ]"""
        if not MID in self.TIMETABLE:
            return []
        else:
            return self.TIMETABLE[MID]
    def pictureURL(self):
        u"""return the picture url of the movie"""
        exp=re.compile(r'<img src="([a-z0-9:/_.-]+)" border="0" alt=".*?" />')        
    def __repr__(self):
        return "<Theater ID#%s object>"%self.CID

class Favourite:
    """handle favourite items"""
    def __init__(self,name=""):
        """favourite initialisation."""
        Log(u"Favourite.__init__ : a voir l'utilité de la variable name en définition d'instance. Soit on utilise name pour enregistrer ou charger, soit on travaille avec un favoris nommé lors de son instanciation")
        self.NAME = name 
        self.FAVOURITE = []
        self.FAVTYPES = ["MOVIE","PERSON","CINEMA"]
        
    def load(self,name,path="",append=True):
        """Load a favourite file using the name given to the Favourite instance"""
        if not name: name="MyFavourites"
        if not os.path.exists(os.path.join(path,name+".p")): raise AllocineError,"Favourite pickle file not found !"
        import cPickle
        favourite = cPickle.load(open(os.path.join(path,name+".p")))
        from types import ListType
        if not type(favourite) is ListType:
            raise AllocineError,"file is not a valid Favourite Pickle file"
        #...
        #we may need some more tests to be sure 'favourite' looks like a FAVOURITE correct list variable [(type,id,title),....]
        if append:
            self.FAVOURITE = list(set(self.FAVOURITE + favourite))
        else:
            self.FAVOURITE = favourite
        #return favourite

    def save(self,name,path="",replace=False):
        """Save the FAVOURITE list in a pickle stream.
        If the pickle stream file exist, and <replace> is set to False, load the pickle stream before writing the new one.
        Else, write the temporary pickle stream into <name> file inside <path>."""
        Log(u"Favourite.save(name,path,replace) : Need to be tested", "D")
        Log(u"Favourite.save(name,path,replace) : Need to test if pickling 'self' is possible and if it works. Not sure if useful, but need to know","D")
        if not name: name="MyFavourites"
        import cPickle
        if os.path.exists(os.path.join(path,name+".p")) and not replace:
            favourite = cPickle.load(open(os.path.join(path,name+".p"))) #lecture
            favourite = list(set(favourite + self.FAVOURITE)) #ajout du pickle lu et des temporaires
        else:
            favourite = self.FAVOURITE
        cPickle.dump(favourite,open(os.path.join(path,name+".p"),"w"))
        
    def add(self,identifier):
        """Add an item represented by the <identifier> to the favourites.
        <identifier> is a tuple (type,id,title)"""
        Log(u"Favourite.add(identifier) : TODO", "D")
        self.FAVOURITE.append(identifier)
        self.FAVOURITE = list(set(self.FAVOURITE)) #extract 'doublons'
        
    def remove(self,identifier):
        """Remove the favourite item represented by the <identifier>."""
        Log(u"Favourite.remove(identifier) : Need to be tested", "D")
        if self.FAVOURITE.count(identifier):
            self.FAVOURITE.remove(identifier)
        
        
        
#LAST_VISITED_URL    = "http://www.allocine.fr"
#initialisation des domaines pour l'internationalisation
#set_country("FR")



if __name__ == "__main__":
    #Log( u"This script is intended to be used as a library.")
    #film = Movie( "110096" )
    #print film.XML( passion_fanart=True )
    print passion_fanarts( "110096" )
