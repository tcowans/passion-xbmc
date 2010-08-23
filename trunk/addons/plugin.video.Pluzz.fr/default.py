# -*- coding: cp1252 -*-

# script constants
__plugin__       = "Pluzz.fr"
__addonID__      = "plugin.video.Pluzz.fr"
__author__       = "Ppic"
__url__          = "http://code.google.com/p/passion-xbmc/"
__svn_url__      = "http://passion-xbmc.googlecode.com/svn/trunk/addons/"
__credits__      = "Team XBMC passion, http://passion-xbmc.org/"
__platform__     = "xbmc media center, [LINUX, OS X, WIN32, XBOX]"
__date__         = "23-08-2010"
__version__      = "1.1.0"
__svn_revision__  = "$Revision: 709 $".replace( "Revision", "" ).strip( "$: " )
__XBMC_Revision__ = "20000" #XBMC Babylon
__useragent__    = "Mozilla/5.0 (Windows; U; Windows NT 5.1; fr; rv:1.9.0.1) Gecko/2008070208 Firefox/3.0.1"


import urllib
import re
import os
import xbmcgui
import xbmcplugin
from traceback import print_exc
import xbmcaddon

__settings__ = xbmcaddon.Addon( __addonID__ )
                                      
BASE_RESOURCE_PATH = os.path.join( os.getcwd(), "resources" )
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "lib" ) )
CACHE_PATH = xbmc.translatePath ("special://home/userdata/addon_data/%s" % __addonID__)

if not os.path.exists(CACHE_PATH): os.makedirs(CACHE_PATH)
chaine_path = os.path.join( CACHE_PATH , "liste_chaine.tmp" )
emissions_path = os.path.join( CACHE_PATH , "liste_emissions.tmp" )
asx_path = os.path.join( CACHE_PATH , "temp.asx" )

from convert import translate_string
from convert import set_entity_or_charref
tempfile = os.path.join( os.getcwd() , "temp.html" )

BASE_URL = "http://www.pluzz.fr/"
MAGIC_URL = "http://www.pluzz.fr/appftv/webservices/video/getInfosVideo.php?src=cappuccino&video-type=simple&template=ftvi&template-format=complet&id-externe="
URL_MP4 = "rtmp://videozones-rtmp.francetv.fr/ondemand/mp4:cappuccino/publication"
URL_WMV = "http://a988.v101995.c10199.e.vm.akamaistream.net/7/988/10199/3f97c7e6/ftvigrp.download.akamai.com/10199/cappuccino/production/publication"

def addLink(name,url,iconimage, c_items = None ):
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
        if c_items : liz.addContextMenuItems( c_items, replaceItems=True )
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)
        return ok

def addDir(name,url,mode,iconimage, c_items = None , sortie= None ):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        if c_items : liz.addContextMenuItems( c_items, replaceItems=True )
        if sortie: liz.setInfo( type="Video", infoLabels={ "Title": name , "Date": sortie } )
        else: liz.setInfo( type="Video", infoLabels={ "Title": name } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok
    
def addFilm(name,url,mode,iconimage,genre,director,cast,plot,duration,year):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name , "genre": genre , "director": director , "cast": cast , "plot": plot , "duration": duration , "year": year})
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok

def end_of_directory( OK ):
    xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=OK )
    
def get_params():
    param=[]
    paramstring=sys.argv[2]
    if len(paramstring)>=2:
        params=sys.argv[2]
        cleanedparams=params.replace('?','')
        if (params[len(params)-1]=='/'):
                params=params[0:len(params)-2]
        pairsofparams=cleanedparams.split('&')
        param={}
        for i in range(len(pairsofparams)):
            splitparams={}
            splitparams=pairsofparams[i].split('=')
            if (len(splitparams))==2:
                param[splitparams[0]]=splitparams[1]
    return param 
        
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

def save_data( txt , temp):
    try:
        if txt:file( temp , "w" ).write( repr( txt ) )
    except:
        print_exc()
        print "impossible d'enregistrer le fichier %s" % temp

def load_data( file_path ):
    try:
        temp_data = eval( file( file_path, "r" ).read() )
    except:
        print_exc()
        print "impossible de charger le fichier %s" % file_path
        temp_data = ""
    return temp_data   
            
def get_emissions_list():    #récupération de la liste des émissions
    data = get_html_source( "http://www.pluzz.fr/appftv/webservices/video/catchup/getListeAutocompletion.php" )
    match = re.findall('<item class="programme" chaine_principale="(.*?)"><\!\[CDATA\[(.*?)\]\]></item>' , data)
    if match:  
        print "### nombre d'émission trouvées: %s" % len(match)
        for infos in match:
            emission = {}
            emission["chaine"] = infos[0]
            emission["nom"] = infos[1]
            if emission["chaine"] not in liste_chaines: liste_chaines.append(emission["chaine"])
            liste_emissions.append(emission)
            
def get_video_url(em_url):
    print "### récupération page %s%s%s" % ( BASE_URL , em_url , ".html")
    data = get_html_source ( BASE_URL + em_url + ".html")
    
    match = re.search(r'<div id="playerCtnr">\s+<a href="http://info\.francetelevisions\.fr/\?id-video=(.*)" id="current_video" class="video" type="video/cappuccino">.*?</a>\s+<div class="accroche">(.*)\s+</div>', data)
    if match:
        video_id = match.group(1)
        video_name = match.group(2)
        print "### video_id = %s" % video_id
        video = get_video_info(video_id)
# 	   liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
# 	   liz.setInfo( type="Video", infoLabels={ "Title": name } )
# 	   xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)
        return video
    else:
        print "### pas de vidéo trouvée"
        video_id = False
        video_name = False        
    
def get_video_info(video_id):
    print "### récupération page %s%s" % ( MAGIC_URL , video_id)
    data = get_html_source ( MAGIC_URL + video_id )
    #save_data(data,tempfile)         
    video = {}
    #récupération infos du film
    match = re.search("<titre-public><!\[CDATA\[(.*?)\]\]></titre-public>",data)
    if match: video["titre"] = match.group(1)
    match = re.search("<nom><!\[CDATA\[(.*?)\]\]></nom>",data)
    if match: video["nomfichier"] = match.group(1)
    match = re.search("<chemin><!\[CDATA\[(.*?)\]\]></chemin>",data)
    if match: video["chemin"] = match.group(1)
    match = re.search("<url><!\[CDATA\[(.*?)\]\]></url>",data)
    if match: video["image"] = match.group(1)
    else: video["image"] = ""
    match = re.search("<duree><!\[CDATA\[(.*?)\]\]></duree>",data)
    if match: video["duree"] = match.group(1)
    
    #chemin en fonction du type
    if ".wmv" in video["nomfichier"]: video["link"] = URL_WMV + video["chemin"] + video["nomfichier"] + "?MSWMExt=.asf"
    elif ".asx" in video["nomfichier"]: 
        data = get_html_source ( video["chemin"] + video["nomfichier"])
        match = re.search("""<ref href = "(.*?)" />""" , data )
        if match: video["link"] = match.group(1)    
    elif ".mp4" in video["nomfichier"]: video["link"] = URL_MP4 + video["chemin"] + video["nomfichier"]
    print video
    return video
 
    
#début du code:

params=get_params()
url=None
name=None
mode=None
try: url=urllib.unquote_plus(params["url"])
except: pass
try: name=urllib.unquote_plus(params["name"])
except: pass
try: mode=int(params["mode"])
except: pass
print "Mode: "+str(mode)
print "URL: "+str(url)
print "Name: "+str(name)
OK = True

if mode==None or url==None or len(url)<1: #menu principal
    #initialisation des listes
    liste_chaines = []
    liste_emissions = []     
    get_emissions_list()
    save_data( liste_chaines , chaine_path )   
    print liste_chaines
    save_data( liste_emissions , emissions_path )
    for chaine in liste_chaines:
        addDir(chaine,chaine,1,"" )

if mode == 1:
    liste_emissions = load_data( emissions_path )
    for emission in liste_emissions:
        if emission["chaine"] == url: addDir(emission["nom"] , translate_string(emission["nom"].replace("Î","i").replace("ô","o").replace("è","e")).replace(" ","-").replace("'","-").lower() ,2,"" )
        
if mode == 2: 
     
    video = get_video_url(url)
    try: 
        playableVideoItem = xbmcgui.ListItem( video["titre"] , path = video["link"] )
        playableVideoItem.setThumbnailImage(video["image"])
        print "###%s###" % video["link"]
        xbmc.Player().play( video["link"] , playableVideoItem , False )  
    except: xbmcgui.Dialog().ok("Plugin Pluzz.fr" , "Impossible de lire la vidéo")   
     
    OK = False    
        
        
end_of_directory( OK )    