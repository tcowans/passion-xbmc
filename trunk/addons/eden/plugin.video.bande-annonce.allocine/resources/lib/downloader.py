# -*- coding: utf-8 -*-

import xbmc
import urllib
import re
import os
from traceback import print_exc

__useragent__    = "Mozilla/5.0 (Windows; U; Windows NT 5.1; fr; rv:1.9.0.1) Gecko/2008070208 Firefox/3.0.1"

def get_html_source( url ):
    """ fetch the html source """
    class AppURLopener(urllib.FancyURLopener):
        version = __useragent__
    urllib._urlopener = AppURLopener()

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
        print "impossible d'ouvrir la page %s" % url
        return ""

def get_media_link(id_media , quality):
    media_url = "http://www.allocine.fr/skin/video/AcVisionData_xml.asp?media=%s" % id_media
    media_data = get_html_source( media_url )
    #save_data(media_data)
    media = {}
    try:media_data=re.compile( '<AcVisionVideo(.*?)/>', re.DOTALL ).findall(media_data)[0]
    except:
        print "problème de récupération info média"
        print_exc()
    try:media["name"] = re.findall( 'title="(.*?)"', media_data )[0]
    except:
        media["name"] = ""
        print_exc()
    print "récupération info média: %s" % media["name"]
    try:media["ld"] = re.findall( 'ld_path="(.*?)"', media_data )[0]
    except:
        media["ld"] = ""
        print_exc()
    try:media["md"] =re.findall( 'md_path="(.*?)"', media_data )[0]
    except:
        media["md"] = ""
        print_exc()
    try:media["hd"] = re.findall( 'hd_path="(.*?)"', media_data )[0]
    except:
        media["hd"] = ""
        print_exc()
#     print "###############media####################"
#     print media
#     print media_data
    return media["%s" % quality]

try:
    print "args: %s" % sys.argv[ 1 ]
    path= urllib.unquote_plus(sys.argv[ 1 ].split("&")[1])
    url= urllib.unquote_plus(sys.argv[ 1 ].split("&")[0])
    
    xbmc.executebuiltin( "XBMC.Notification( %s, 'Téléchargement en cours...', 'icone.png')" % path )
    if url[:7] == "cmedia=" : 
        quality= urllib.unquote_plus(sys.argv[ 1 ].split("&")[2])
        url = get_media_link(url[7:] , quality)
    print "path: %s" % path
    print "url: %s" % url
    
except: 
    print_exc()
    notif = "%s,%s,5000,%s" % ( "Erreur récupération ", "transfert paramètres", "icone.png" )

try:    
    Filename, headers = urllib.urlretrieve( url , path )
    #print Filename
    #print headers 
    notif = "%s,%s,5000,%s" % ( Filename, "Téléchargement terminé", "icone.png" )
    xbmc.Player().play( Filename )
except:
    print_exc()
    notif = "%s,%s,5000,%s" % ( "Erreur de téléchargement !!!", "", "icone.png" )
    
xbmc.executebuiltin( "XBMC.Notification(%s)" % notif )
