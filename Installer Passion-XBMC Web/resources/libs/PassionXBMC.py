"""
    library for authentification on passion-xbmc.org
    created by alexsolex for HurleMaBoite and MegaUpload
"""

import os
import re
import sys
import gzip
import socket
import urllib
import urllib2
import StringIO
import cookielib
from traceback import print_exc


USER_AGENT = "Installer Passion-XBMC/2.0"
try:
    import xbmc
    USER_AGENT += " (XBMC for %s %s; %s)" % ( os.environ.get( "OS", "Xbox" ), xbmc.getInfoLabel( "System.BuildVersion" ), xbmc.getInfoLabel( "System.BuildDate" ) )
except:
    xbmc = None
    USER_AGENT += " (XBMC for %s)" % os.environ.get( "OS", "XBox" )

HEADERS = {
    'Host': 'passion-xbmc.org',
    'Referer': '',
    #'User-Agent': 'Mozilla/5.0 ( Windows; U; Windows NT 5.1; fr; rv:1.9.1.3 ) Gecko/20090824 Firefox/3.5.3 ( .NET CLR 3.5.30729 )',
    'User-Agent': USER_AGENT,
    'Accept': 'text/html, application/xhtml+xml, application/xml;q=0.9, */*;q=0.8',
    'Accept-Language': 'fr, fr-fr;q=0.8, en-us;q=0.5, en;q=0.3',
    'Accept-Charset': 'ISO-8859-1, utf-8;q=0.7, *;q=0.7',
    'Accept-Encoding': 'gzip, deflate',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Keep-Alive': '300',
    'Connection': 'keep-alive',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache'
    }
#print HEADERS


# CHEMINS
CWD = os.getcwd()#.replace( ';', '' )

CACHEDIR = os.path.join( CWD, "~" )
if not os.path.isdir( CACHEDIR ): os.makedirs( CACHEDIR )
COOKIEFILE = os.path.join( CACHEDIR, "passion-xbmc.lwp" )


# met en place la gestion des cookies
CJ = cookielib.LWPCookieJar()
opener = urllib2.build_opener( urllib2.HTTPCookieProcessor( CJ ) )
urllib2.install_opener( opener )
if os.path.isfile( COOKIEFILE ):
    # si nous avons un fichier cookie déjà sauvegardé
    # alors charger les cookies dans le Cookie Jar
    CJ.load( COOKIEFILE )
else:
    CJ.save( COOKIEFILE )


timeout = 10
# timeout en seconds
socket.setdefaulttimeout( timeout )



def get_page( url, params={}, referer="", savehtml=True, filename="default.html", headers=None, check_connexion=True, debuglevel=0 ):
    """
    télécharge la page avec les paramètres fournis :
        params : dictionnaire de paramètres
    Renvoi le code html de la page
    """
    HEADERS.update( { 'Host': url[ 7: ].split( "/" )[ 0 ], 'Referer': referer } )

    if headers:
        opener.addheaders( headers )

    try:
        req = urllib2.Request( url, urllib.urlencode( params ), HEADERS )
        # création d'un objet request
    except IOError, e:
        print 'We failed to open "%s".' % url
        if hasattr( e, 'code' ):
            print 'We failed with error code - %s.' % e.code
        elif hasattr( e, 'reason' ):
            print "The error object has the following 'reason' attribute :"
            print e.reason
            print "This usually means the server doesn't exist, "
            print "is down, or we don't have an internet connection."
        sys.exit()

    #AFFICHAGE DES COOKIES
    if debuglevel:
        if CJ is None:
            print "We don't have a cookie library available - sorry."
        else:
            print 'These are the cookies we have received so far :'
            for index, cook in enumerate( CJ ):
                print index, '  :  ', cook
            # save the cookies again
    CJ.save( COOKIEFILE )

    try:
        connexion = opener.open( req ) #matérialise la page à télécharger
    except Exception, msg:
        print msg.info()
        raise

    if debuglevel:
        print
        print "---------------------"
        print "\turl      : %s" % url
        print "\tgeturl() : %s" % connexion.geturl()
        print "\tinfos    :"
        print connexion.info()
        print "---------------------"
        print

    #GESTION DU CAS OU LE TELECHARGEMENT COMMENCE SANS PAGE INTERMEDIAIRE ( comptes Premiums )
    if "content-transfer-encoding" in connexion.headers.keys() and connexion.headers["content-transfer-encoding"]=="binary":
        raise connexion.geturl()#PrematureDownload( connexion.geturl() )

    #AFFICHAGE DES HEADERS
    if debuglevel:
        print 'Here are the headers of the page :'
        print connexion.info()
        if connexion.geturl() <> url:
            print "Redirection : %s" % connexion.geturl()
        # connexion.read() renvoie la page
        # connexion.geturl() renvoie la véritable url de la page demandée
        # ( au cas où urlopen a été redirigé, ce qui arrive parfois )

    html = connexion.read() #lecture de la page

    #Gestion de la compression gzip
    if "content-encoding" in connexion.headers.keys() and connexion.headers["Content-Encoding"] == "gzip":
        compressedstream = StringIO.StringIO( html )
        gzipper = gzip.GzipFile( fileobj=compressedstream )
        data = gzipper.read()
    else:
        data = html
    #sauvegarde de la page
    if savehtml:
        try:
            open( os.path.join( CACHEDIR, filename ).encode( 'utf-8' ), "w" ).write( data )
        except Exception, msg:
            print "Exception en get_page"
            print Exception, msg
    # save the cookies again
    CJ.save( COOKIEFILE )
    return data


def get_avatar( html ):
    avatar = ""
    match = re.search( r'''<img src="(.*?)" alt="" class="avatar" border="0" /><br /><span class="normaltext">Salut,''', html )
    if match:
        avatar_url = match.group( 1 )
        if avatar_url.startswith( "http://" ):
            avatar_cached = os.path.join( CACHEDIR, os.path.basename( avatar_url ) )
            if not os.path.exists( avatar_cached ):
                urllib.urlretrieve( avatar_url, avatar_cached )
            if os.path.exists( avatar_cached ):
                avatar = avatar_cached
    return avatar


def get_MP_avatar( avatar_url ):
    avatar = ""
    if avatar_url.startswith( "http://" ):
        avatar_cached = os.path.join( CACHEDIR, "mp_" + os.path.basename( avatar_url ) )
        if not os.path.exists( avatar_cached ):
            urllib.urlretrieve( avatar_url, avatar_cached )
        if os.path.exists( avatar_cached ):
            avatar = avatar_cached
    return avatar


def hasMP( html ):
    MP = 0
    match = re.search( r'''href="http://passion-xbmc.org/pm/">Nouveau:(.*?)</a>''', html )
    if match:
        try: MP = int( match.group( 1 ).strip() )
        except: print_exc()
    return MP


def decode_smileys( text ):
    # smileys to :code: or :)
    smileys = {
        "left": "&larr;",
        "arrows_right": "&rarr;",
        "arrows_right1": "&rarr;",
        "smiley": ":)",
        "beer": "{_}]",
        "beer by frost": "{_}]",
        "niark niark": ":D",
        #"Cheerleader": ":Cheerleader:",
        #"sweat": ":sweat:",
        #"grin": ":grin:",
        #"handshake": ":handshake:",
        #"": "",
        #"": "",
        #"": "",
        #"": "",
        #"": "",
        #"": "",
        #"": "",
        #"": "",
        "tongue": ":p"
        }
    for img, txt in set( re.findall( '<img src="http://passion-xbmc.org/Smileys/(.*?)" alt="(.*?)" border="0" />', text ) ):
        search_for = '<img src="http://passion-xbmc.org/Smileys/%s" alt="%s" border="0" />' % ( img, txt )
        if smileys.has_key( txt ):
            text = re.sub( search_for, "[B]%s[/B]" % smileys[ txt ], text )
        else:
            text = re.sub( search_for, "[B]:%s:[/B]" % txt, text )

    return text.strip()


def getMP():
    MP = []
    from htmldecode import htmlentitydecode, set_pretty_formatting, set_quote_and_code_in_color
    #html = open( os.path.join( CACHEDIR, "pm.html" ), "r" ).read()
    html = get_page( "http://passion-xbmc.org/pm/", filename='pm.html' )
    windowbg = re.compile( '<td colspan="2" class="windowbg(.*?)<td valign="bottom" class="smalltext" width="85%">', re.DOTALL ).findall( html )
    for mp in windowbg:
        auteur = re.findall( '<a href="http://passion-xbmc.org/profile.*?" title="Voir le profil.*?" style="color\:#(.*?)\;">(.*?)</a>', mp )
        auteur_avatar = re.findall( '<img src="(.*?)" alt="" class="avatar reflect" border="0" />', mp )
        if auteur_avatar: auteur_avatar = get_MP_avatar( auteur_avatar[ 0 ] )
        else: auteur_avatar = ""
        title, date = re.findall( '<td align="left" valign="middle">.*?<b>(.*?)</b>.*?<b> le:</b>(.*?) &#187;</div>', mp, re.DOTALL )[ 0 ]
        isread = re.findall( '<div class="smalltext">&#171; (.*?) &#187;</div>', mp, re.DOTALL )
        message = re.findall( '<div class="personalmessage">(.*?)</div>\n', mp, re.DOTALL )

        auteur = "[COLOR=FF%s]%s[/COLOR]" % ( auteur[ 0 ][ 0 ], auteur[ 0 ][ 1 ], )
        title = set_pretty_formatting( htmlentitydecode( unicode( title, 'utf-8' ) ) )
        date = set_pretty_formatting( htmlentitydecode( unicode( date, 'utf-8' ) ) )
        if len( isread ) >= 2:
            isread = htmlentitydecode( unicode( isread[ 1 ], 'utf-8' ) )
        else:
            isread = ""
        message = htmlentitydecode( decode_smileys( set_pretty_formatting( set_quote_and_code_in_color( unicode( message[ 0 ], 'utf-8' ) ) ) ) )#+"</div>"
        #le reste du nettoyage ce passe dans GUI/ForumDirectInfos.py
        #message = re.sub( "(?s)<[^>]*>", "", message )
        MP.append( ( auteur_avatar, auteur, title, date, isread, message ) )

    return MP


def IsAuthenticated():
    html = get_page( "http://passion-xbmc.org/index.php", filename='index.html' )
    connexion = "http://passion-xbmc.org/logout/?sesc=" in html
    match = re.search( r'''<span class="normaltext">Salut, <b>([a-z0-9]+)</b></span>''', html, re.DOTALL )
    match = match or re.search( r'''<span class="normaltext">Salut, <b>(.*?)</b></span>''', html )
    if match:
        pseudo = match.group( 1 )
        avatar = get_avatar( html )
        mp = hasMP( html )
    else:
        pseudo = None
        avatar = ""
        mp = 0
    return pseudo, connexion, avatar, mp


def authentification( login, psw, force=False ):
    """Make authentification using login and psw parameters if needed ( i.e cookie is not set or expired ).
    Force authentification if force parameter is set to True"""
    if force or not IsAuthenticated()[ 1 ]:
        POSTDATA = {
            "user":login,
            "passwrd":psw,
            #"cookielength":"60",
            "cookieneverexp":"on",
            "hash_passwrd":""
            }
        #note sur le hash
        # il semblerait q'il faille hash en sha1 hexa le user en minuscule utf-8 + sha1 hexa utf-8 du passwrd + sessionID
        html = get_page( "http://passion-xbmc.org/login2/", POSTDATA, "", filename="authentification.html" )
    return IsAuthenticated()


def Disconnect():
    """Effectue la suppression de tous les cookies stockés dans le cookiejar.
    Retourne un tuple pseudo, connexion"""
    for c in CJ:
        CJ.clear( c.domain, c.path, c.name )
        CJ.save( COOKIEFILE )
    return IsAuthenticated()


def Connect( force=False ):
    if force: Disconnect()
    pseudo, connexion, avatar, mp = IsAuthenticated()
    if not connexion:
        if xbmc is None:
            login = raw_input( "Login Passion-XBMC ? ( vide si pas de login )" )
            psw = raw_input( "Password ? ( vide si pas de login )" )
        else:
            kb = xbmc.Keyboard( '', 'Veuillez saisir votre login Passion-XBMC', False )
            kb.doModal()
            if kb.isConfirmed():
                login = kb.getText()
                kb.setHeading( 'Veuillez saisir maintenant le mot de passe' )
                kb.setHiddenInput( True ) # optional
                kb.doModal()
                if kb.isConfirmed():
                    psw = kb.getText()
                else:
                    xbmc.executebuiltin( "XBMC.Notification(Passion-XBMC,Identification incomplète,4000,)" )
            else:
                xbmc.executebuiltin( "XBMC.Notification(Passion-XBMC,Identification annulée,4000,)" )

        pseudo, connexion, avatar, mp = authentification( login, psw, True )

    return pseudo, connexion, avatar, mp



if __name__  == "__main__":
    getMP()
    raise
    #attention la récépération de la page MP efface l'info "message non lu" sur le site.
    #private_rss = "http://passion-xbmc.org/pm/"#"http://passion-xbmc.org/underground/?action=.xml;type=rss"

    #Disconnect()
    #html = get_page( private_rss, filename='PM_nopass.html' )
    #pseudo, connexion, avatar, mp = IsAuthenticated()
    pseudo, connexion, avatar, mp = Connect()
    #if connexion: html = get_page( private_rss, filename='PM.html' )

    #if xbmc is not None:
    #    if connexion:
    #        if mp == 0: notif = "Bonjour %s,Vous êtes connecté !,5000,%s" % ( pseudo, avatar, )
    #        else: notif = "Bonjour %s,Vous avez %i message !,5000,%s"  % ( pseudo, mp, avatar, )
    #        xbmc.executebuiltin( "XBMC.Notification(%s)" % notif )
    #    else:
    #        xbmc.executebuiltin( "XBMC.Notification(Passion-XBMC,Identification erronée,4000,)" )
    #else:
    if connexion:
        print u"Bonjour %s, vous êtes connecté !" % pseudo
        if mp > 0: print u"Vous avez %i message !" % mp
    else:
        print u"erreur d'authentification"
    print


    #fp, h = urllib.urlretrieve( private_rss, "underground.xml" )
    #print fp
    #print h

    count = 0
    f = open( "../forum_links.txt", "r" )
    for line in f.readlines():
        if line.startswith( "##" ):
            count += 1
            rss = line.strip( "# " + os.linesep ).split( ", " )
            for r in rss:
                print r
            print
            #urllib.urlretrieve( rss[ 0 ], "rssfiles/%s.xml" % count )
            #html = get_page( rss[ 0 ] )
            #file( "rssfiles/%s.xml" % count, "w" ).write( html )
            #print "##", re.compile( "<title>(.*?)</title>" ).findall( file( "rssfiles/%s.xml" % count, "r" ).read() )[ 0 ].decode( "utf-8" ), ",", rss[ 0 ], ",", rss[ 1 ]
            #print rss
            #print
        #elif line.startswith( "#" ):
        #    print
        #    print line.strip( os.linesep ).decode( "utf-8" )

    f.close()
