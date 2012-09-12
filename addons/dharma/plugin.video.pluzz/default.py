# -*- coding: cp1252 -*-

__addonID__      = "plugin.video.pluzz"
__author__       = "mighty_bombero, merindol, Temhil (passion-xbmc.org), tom.net, rimram31"
__url__          = "http://passion-xbmc.org/index.php"
__credits__      = "Team XBMC Passion"
__date__         = "02-09-2012"
__version__      = "1.1.1"

import xbmcplugin
import xbmcgui
import xbmc

import urllib, urllib2
from urllib import urlencode, unquote_plus, quote_plus
from urllib2 import build_opener, HTTPCookieProcessor, HTTPHandler
import cookielib
import htmlentitydefs

import sys
import os
import re
import time

from traceback import print_exc
from resources.libs.BeautifulSoup import BeautifulSoup
from resources.libs.BeautifulSoup import BeautifulStoneSoup

from resources.libs.PluzzDL import PluzzDL


ROOTDIR            = os.getcwd()
BASE_RESOURCE_PATH = os.path.join( ROOTDIR, "resources" )
MEDIA_PATH = os.path.join( BASE_RESOURCE_PATH, "media" )

STREAM_URL_PART1='mms://a988.v101995.c10199.e.vm.akamaistream.net/7/988/10199/3f97c7e6/ftvigrp.download.akamai.com/10199/cappuccino/production/publication'

WEBSITE = "http://www.pluzz.fr"

IMAGE_URL = "/layoutftv/arches/catchup/images/logos/"

TYPES = {'categories' :{"Accueil":"/",
        "Info":"/info/",
        "Documentaire":"/documentaire/",
        "Séries - Fictions":"/serie--fiction/",
        "Magazine":"/magazine/",
        "Culture":"/culture/",
        "Jeunesse":"/jeunesse/",
        "Divertissement":"/divertissement/",
        "Sport":"/sport/",
        "Jeu":"/jeu/",
        "Autre":"/autre/"
        },
        'chaines' : {"La 1ere":"/la_1ere/",
        "France 2":"/france2/",
        "France 3":"/france3/",
        "France 4":"/france4/",
        "France 5":"/france5/",
        "France Ô":"/franceo/"
        }}

IMAGES = {"La 1ere":"1ere.png",
          "France 2":"f2.png",
          "France 3":"f3.png",
          "France 4":"f4.png",
          "France 5":"f5.png",
          "France Ô":"fo.png"
        }


def get_content_for_type(type):
    content_list = list()
    for title,(path) in TYPES[type].items():
        content_list.append({'link' : path, 'title' : title})
    return content_list

def get_category_episodes(url):
    html = urllib.urlopen(WEBSITE + url).read()
    vignettes = re.findall("""<li class="vignette">\s+<h4 class="_titre">\s+<a class="" href="([^"]+)">([^<]+)</a>\s+</h4>\s+(?:<p class="date">(\d{2}/\d{2}/\d{4})</p>\s+)?<p class="mute pgm_id">[^<]*</p>\s+<img class="illustration" src="([^"]+)"[^<]*/>\s+<img class="chaine[^"]*" src="([^"]+)"[^<]*/>""",html)

    episode_list = list()
    for lien_em,titre,date,path_img,path_logoch in vignettes:
        episode_list.append({'link' : lien_em, 'title' : BeautifulSoup(titre,convertEntities="html").prettify(), 'image': path_img})
    return episode_list


def get_episode(url):
    pluzzDL = PluzzDL( url, True, None )
    #print "urlFrag" + pluzzDL.urlFrag
    path = None
    type = "inconnu"
    if pluzzDL.lienRTMP != None:
        path = pluzzDL.lienRTMP
        type = 'RTMP'
        print "lien RTMP found"
    elif pluzzDL.lienMMS:
        path = pluzzDL.lienMMS
        type = 'MMS'
        print "lien MMS found"
    elif pluzzDL.manifestURL:
        #path = pluzzDL.manifestURL
        type = "F4M" 
        print "lien F4M found (manisfest) - not supported"
    elif pluzzDL.m3u8URL:
        #path = pluzzDL.m3u8URL
        type = "M3U8"
        print "lien M3U8 found - not supported"
    if pluzzDL.drm:
        if pluzzDL.drm == "oui" :
            print "get_episode: La vidéo posséde un DRM ; elle sera sans doute illisible"
            type = 'DRM'
            
    print "get_episode: path"
    print path # path can be None and cannot be concatenated with a string in this case
    return path , type
    
#    #get the id
#    req = urllib2.Request(url)
#    req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-GB; rv:1.9.1.7) Gecko/20091221 Firefox/3.5.7')
#    response = urllib2.urlopen(req).read()
#    video_id = re.compile('id-video=(.*?)"').findall(response)[0]
#    #get the episode url
#    #print 'http://www.pluzz.fr/appftv/webservices/video/getInfosVideo.php?src=cappuccino&video-type=simple&template=ftvi&template-format=complet&id-externe=' + video_id
#    req = urllib2.Request('http://www.pluzz.fr/appftv/webservices/video/getInfosVideo.php?src=cappuccino&video-type=simple&template=ftvi&template-format=complet&id-externe=' + video_id)
#    req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-GB; rv:1.9.1.7) Gecko/20091221 Firefox/3.5.7')
#    response = urllib2.urlopen(req).read()
#    print response
#    #<nom><![CDATA[144846_docu_010742_3_288816.wmv]]></nom>
#    video_base = 'mms://a988.v101995.c10199.e.vm.akamaistream.net/7/988/10199/3f97c7e6/ftvigrp.download.akamai.com/10199/cappuccino/production/publication'
#    video_name = re.compile('<nom><!\[CDATA\[(.*?)\]\]></nom>').findall(response)[0]
#    video_path = re.compile('<chemin><!\[CDATA\[(.*?)\]\]></chemin>').findall(response)[0]
#    type = 'wmv'
#    
#    if video_name.find('mp4') != -1:
#        video_base = 'rtmp://videozones-rtmp.francetv.fr/ondemand/mp4:cappuccino/publication'
#        type = 'mp4'
#    print video_path + video_name
#    return video_base + video_path + video_name, type

def get_all_episodes():
    #pour lister toutes les émissions par ordre alphabétique:
    html = urllib.urlopen(WEBSITE + '/liste-des-videos.html').read()
    print "All HTML: " + html
    liste_emissions = re.findall('<li><a href="(http://www.pluzz.fr/.*?)">(.*?)</a></li>',html)
    episode_list = list()
    for path,title in liste_emissions:
        print title,"(",path,")"
        episode_list.append({'link' : path, 'title' : title})
    return episode_list

def get_linux_url(url):
    print "In get Linux"
    url = url.replace('mms:','http:')
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-GB; rv:1.9.1.7) Gecko/20091221 Firefox/3.5.7')
    response = urllib2.urlopen(req).read()
    url = re.compile('Ref1=(.*?).asf').findall(response)[0]
    url = url + '.asf'
    return url

def newFill(fillString, toLength, fillChar):
    """pads a string"""
    return fillString+''.join([fillChar for x in range(len(fillString),toLength)])

def pagination(url_emission):
    #retourne le numéro de page précédente, la liste des pages, le num de page active, la page suivante
    html = urllib.urlopen(url_emission).read()
    #précédent
    match = re.search("""<a href="(.*?)">&lt;&lt; &nbsp; Pr.c.dent </a>""",html)
    if match:
        page_precedente = match.group(1)
    else:
        page_precedente = None
    #courante
    match = re.search("""<li class="current">(.*?)</li>""",html)
    if match:
        page_courante = match.group(1)
    else:
        page_courante = None
    #liste des autres pages
    autres_pages= re.findall("""<a href="(.*?)">\d+</a></li>""",html)
    #suivant
    #match = re.search("""<a href="(\d+)">Suivant &nbsp; >></a>""",html)
    match = re.search("""<a href="(.*?)">Suivant &nbsp; &gt;&gt;</a>""",html)

    if match:
        page_suivante = match.group(1)
    else:
        page_suivante = None
    return page_precedente,page_courante,autres_pages,page_suivante
        
def INDEX():
    addDir('Chaines', 'chaines', 2, '')
    addDir('Categories', 'categories', 2, '')
    addDir('Les plus vues', '/les-plus-vues', 3, '')
    #addDir('Toutes les episodes', '', 4, '')
    
        
def SELECT_CATEGORY(type):
    categories = get_content_for_type(type)
    for category in categories:
        if category == 'chaines':
            icon = WEBSITE + IMAGE_URL + IMAGES[category['title']]
        else:
            icon = ''
        addDir(category['title'], category['link'], 3, icon)
        
def SELECT_EPISODE(url):
    print "SELECT_EPISODE"
    print WEBSITE + url
    page_precedente,page_courante,autres_pages,page_suivante = pagination(WEBSITE + url)
    print "next: " + str(page_suivante)
    #if page_precedente != None:
    #    addDir('Page precedente', url + "/" + page_precedente, 3, '')
    if page_suivante != None:
        addDir('Page suivante', url + "/" + page_suivante, 3, os.path.join(MEDIA_PATH, "next-page.png"))
    if url in TYPES['chaines'].values():
        addDir("Toutes les vidéos", url + "/" + "1", 3, '')
        
    episodes = get_category_episodes(url)
    for episode in episodes:
        addLink(episode['title'], sys.argv[0] + "?url=" + urllib.quote_plus(episode['link']) + "&mode=1&name=" + urllib.quote_plus(episode['title']), WEBSITE + episode['image'])

def SELECT_EPISODE_FROM_ALL():
    episodes = get_all_episodes()
    print episodes
    for episode in episodes:
        addLink(episode['title'], sys.argv[0] + "?url=" + urllib.quote_plus(episode['link']) + "&mode=1&name=" + urllib.quote_plus(episode['title']),'')
            
                    
def VIDEO(url, name):
        url, type = get_episode(url)
        #if type == 'wmv':
        #    url = get_linux_url(url)
        #item = xbmcgui.ListItem(name)
        #xbmc.Player(xbmc.PLAYER_CORE_AUTO).play(url, item)
        #xbmc.executebuiltin('XBMC.ActivateWindow(fullscreenvideo)')        

        # Play  video
        if url:
            item = xbmcgui.ListItem(path=url)
            #if self.debug_mode:
            #print "Lecture de la video %s with URL: %s"%(name, url)
            xbmcplugin.setResolvedUrl(handle=int(sys.argv[1]), succeeded=True, listitem=item)
        elif type == 'DRM':
            showNotification("Vidéo avec DRM", '%s' % (name))
        else:
            showNotification("Format video %s non supporté"%type, '%s'%(name))
    
        
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

      
def addLink(name,url,iconimage):
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        liz.setProperty('IsPlayable', 'true')
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)
        return ok


def addDir(name,url,mode,iconimage):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok
    
def showNotification(header="", message="", sleep=5000, icon="DefaultVideo.png"):
    """ 
       Will display a notification dialog with the specified header and message,
       In addition you can set the length of time it displays in milliseconds and a icon image. 
    """
    print "notification:"
    print "XBMC.Notification(%s,%s,%i,%s)" % ( header, message, sleep, icon )
    xbmc.executebuiltin( "XBMC.Notification(%s,%s,%i,%s)" % ( header, message, sleep, icon ) )
        
#######################################################################################################################    
# BEGIN !
#######################################################################################################################

if ( __name__ == "__main__" ):
    try:
        print "==============================="
        print "  PLUZZ - Version: %s"%__version__
        print "==============================="
        print

        params=get_params()
        url=None
        name=None
        mode=None
        try:
                url=urllib.unquote_plus(params["url"])
        except:
                pass
        try:
                name=urllib.unquote_plus(params["name"])
        except:
                pass
        try:
                mode=int(params["mode"])
        except:
                pass
        print "Mode: "+str(mode)
        print "URL: "+str(url)
        print "Name: "+str(name)

        if mode==None or url==None or len(url)<1:
                print "categories"
                INDEX()
        elif mode==1:
                print "index of : "+url
                VIDEO(url, name)
        elif mode==2:
                print "index of : "+url
                SELECT_CATEGORY(url)
        elif mode==3:
                print "index of : "+url
                SELECT_EPISODE(url)
        elif mode==4:
                print "index of : "+url
                SELECT_EPISODE_FROM_ALL()        

        #xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_UNSORTED)
        xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_LABEL )
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
    except:
        print_exc()

