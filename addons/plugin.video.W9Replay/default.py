"""

Add-on plugin video W9 Replay pour XBMC 

20-12-2010 Version 1.1.0 par Temhil
    - Merge avec le add-on M6 replay 1.3.0
    - Convertion uf format Add-on compatible Dharma
    - Permet l'acces aux videos en dehors de la France
    
16-06-2010 Version 1.0.0 par PECK
    - Creation

"""

__addonID__      = "plugin.video.W9Replay"
__author__       = "PECK, mighty_bombero, merindol, Temhil (passion-xbmc.org)"
__url__          = "http://passion-xbmc.org/index.php"
__credits__      = "Team XBMC Passion"
__date__         = "12-20-2010"
__version__      = "1.1.0"

import urllib,sys,os,platform
import xbmcplugin,xbmcgui,xbmcaddon,xbmc
#import base64
import string
#import pickle
import datetime
import re
from xml.dom.minidom import parseString

__addon__ = xbmcaddon.Addon( __addonID__ )
__settings__ = __addon__
__language__ = __addon__.getLocalizedString
__addonDir__ = __settings__.getAddonInfo( "path" )


def get_categorie(xml_url):
    dico = {}
    categorie = []
    image = []
    pos= []
    dico['categorie']=categorie
    dico['image']=image
    dico['pos']=pos    
    conn = urllib.urlopen(xml_url)
    xmlrss=parseString(conn.read())
    conn.close()
    for item in range(len(xmlrss.getElementsByTagName("template_exchange_WEB")[0].getElementsByTagName("categorie"))):
        if not xmlrss.getElementsByTagName("template_exchange_WEB")[0].getElementsByTagName("categorie")[item].hasAttribute("tag_dart"):
            categorie.append(xmlrss.getElementsByTagName("template_exchange_WEB")[0].getElementsByTagName("categorie")[item].getElementsByTagName("nom")[0].childNodes[0].data)
            image.append("http://images.w9replay.fr"+xmlrss.getElementsByTagName("template_exchange_WEB")[0].getElementsByTagName("categorie")[item].getAttribute("big_img_url"))
            pos.append(item)
    return dico

def get_sub_categorie(xml_url,parent_pos):
    dico = {}
    categorie = []
    image = []
    pos= []
    dico['categorie']=categorie
    dico['image']=image
    dico['pos']=pos    
    conn = urllib.urlopen(xml_url)
    xmlrss=parseString(conn.read())
    conn.close()
    for item in range(parent_pos+1,len(xmlrss.getElementsByTagName("template_exchange_WEB")[0].getElementsByTagName("categorie"))):
        if xmlrss.getElementsByTagName("template_exchange_WEB")[0].getElementsByTagName("categorie")[item].hasAttribute("tag_dart"):
            categorie.append(xmlrss.getElementsByTagName("template_exchange_WEB")[0].getElementsByTagName("categorie")[item].getElementsByTagName("nom")[0].childNodes[0].data)
            image.append("http://images.w9replay.fr"+xmlrss.getElementsByTagName("template_exchange_WEB")[0].getElementsByTagName("categorie")[item].getAttribute("big_img_url"))
            pos.append(item)
        else:
            break
    return dico

def get_produit(xml_url,parent_pos):
    dico = {}
    path = []
    image = []
    nom = []
    dico['nom']=nom
    dico['path']=path
    dico['image']=image    
    conn = urllib.urlopen(xml_url)
    xmlrss=parseString(conn.read())
    conn.close()
    
#    for item in range(len(xmlrss.getElementsByTagName("template_exchange_WEB")[0].getElementsByTagName("categorie")[parent_pos].getElementsByTagName("produit"))):
#        nom.append(xmlrss.getElementsByTagName("template_exchange_WEB")[0].getElementsByTagName("categorie")[parent_pos].getElementsByTagName("produit")[item].getElementsByTagName("nom")[0].childNodes[0].data)        
#        path.append(xmlrss.getElementsByTagName("template_exchange_WEB")[0].getElementsByTagName("categorie")[parent_pos].getElementsByTagName("produit")[item].getElementsByTagName("fichemedia")[0].getAttribute("video_url"))
#        image.append("http://images.w9replay.fr"+xmlrss.getElementsByTagName("template_exchange_WEB")[0].getElementsByTagName("categorie")[parent_pos].getElementsByTagName("produit")[item].getAttribute("big_img_url"))

    for item in range(len(xmlrss.getElementsByTagName("template_exchange_WEB")[0].getElementsByTagName("categorie")[parent_pos].getElementsByTagName("produit"))):
       
        medias = xmlrss.getElementsByTagName("template_exchange_WEB")[0].getElementsByTagName("categorie")[parent_pos].getElementsByTagName("produit")[item].getElementsByTagName("fichemedia")
       
        # Parcours les "fiche_media" pour en extraire le lien video. Normalement il n'y en a qu'une, sauf pour les series VOSTFR/VF
        for media in medias:
            if( len(medias) == 1 ):
                nom_media = ''
            else:
                nom_media = " ["+media.getAttribute("langue")+"]"
            nom.append(xmlrss.getElementsByTagName("template_exchange_WEB")[0].getElementsByTagName("categorie")[parent_pos].getElementsByTagName("produit")[item].getElementsByTagName("nom")[0].childNodes[0].data + nom_media)        
            path.append(media.getAttribute("video_url"))
            image.append("http://images.w9replay.fr"+xmlrss.getElementsByTagName("template_exchange_WEB")[0].getElementsByTagName("categorie")[parent_pos].getElementsByTagName("produit")[item].getAttribute("big_img_url"))
        
    return dico

def add_menu_item(title,action,size,thumb,folder):
    item=xbmcgui.ListItem(title,thumbnailImage=thumb)
    cm = []    
    cm +=[ (title,"XBMC.RunPlugin("+sys.argv[ 0 ]+"?"+action+")")]
    url=sys.argv[ 0 ]+"?"+action
    item.addContextMenuItems(cm, replaceItems=True)
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=item,isFolder=folder,totalItems=size)

if ( not sys.argv[ 2 ] ):
    dico=get_categorie("http://www.w9replay.fr/catalogue/120-w9.xml")
    for cat in range(len(dico['categorie'])):
        add_menu_item(dico['categorie'][cat],"display_pos="+str(dico['pos'][cat]),len(dico['categorie']),dico['image'][cat],True)

elif ( "display_pos=" in sys.argv[ 2 ] ):
    dico=get_sub_categorie("http://www.w9replay.fr/catalogue/120-w9.xml",int(sys.argv[ 2 ].split("=")[1]))
    for cat in range(len(dico['categorie'])):
        add_menu_item(dico['categorie'][cat],"display_produit="+str(dico['pos'][cat]),len(dico['categorie']),dico['image'][cat],True)

elif ( "display_produit=" in sys.argv[ 2 ] ):
    dico=get_produit("http://www.w9replay.fr/catalogue/120-w9.xml",int(sys.argv[ 2 ].split("=")[1]))
    for cat in range(len(dico['nom'])):
        add_menu_item(dico['nom'][cat],"stream="+dico['path'][cat],len(dico['nom']),dico['image'][cat],False)

elif ( "stream=" in sys.argv[ 2 ] ):    
    rtmp = "rtmpe://m6dev.fcod.llnwd.net:443/a3100/d1"
    app = "a3100/d1"
    playpath = re.sub( "[ ]", "%20", sys.argv[ 2 ].split("=")[1] )
    item = xbmcgui.ListItem("W9 Replay")
    url = rtmp + " app=" + app + " swfUrl=http://l3.player.m6.fr/swf/StatPlaylibrary_20100401.swf playpath=" + playpath + " swfvfy=true socks=80.67.172.70:9050 flashVer=LNX 10,0,45,2"
    #url = rtmp + playpath.lstrip('mp4:')
    if rtmp =="":
        url = playpath
    xbmc.Player(xbmc.PLAYER_CORE_DVDPLAYER).play(url, item)
    xbmc.executebuiltin('XBMC.ActivateWindow(fullscreenvideo)')


xbmcplugin.endOfDirectory(int(sys.argv[1]))
