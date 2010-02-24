# -*- coding: cp1252 -*-

# script constants
__plugin__       = "Noob Web-Serie"
__author__       = "Ppic"
__url__          = "http://code.google.com/p/passion-xbmc/"
__svn_url__      = "http://passion-xbmc.googlecode.com/svn/trunk/plugins/"
__credits__      = "Team XBMC passion, http://passion-xbmc.org"
__platform__     = "xbmc media center, [LINUX, OS X, WIN32, XBOX]"
__date__         = "24-02-2011"
__version__      = "1.0"
__svn_revision__  = "$Revision: 677 $".replace( "Revision", "" ).strip( "$: " )
__XBMC_Revision__ = "20000" #XBMC Babylon
__useragent__    = "Mozilla/5.0 (Windows; U; Windows NT 5.1; fr; rv:1.9.0.1) Gecko/2008070208 Firefox/3.0.1"


import urllib
import re
import os
import time
from traceback import print_exc
import xbmcplugin
import xbmc
import xbmcgui

try: quality=int( xbmcplugin.getSetting("quality") )
except:
    xbmcplugin.openSettings(sys.argv[0])
    quality=int( xbmcplugin.getSetting("quality") )
print quality
cache_dir = os.path.join ( os.getcwd() , "cache" )
tempfile= os.path.join ( cache_dir , "data.html" )

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

def save_data( txt , temp=tempfile):
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
        print "impossible de charger le fichier %s" % tempfile
        temp_data = ""
    return temp_data    
    
def addLink(name,url,iconimage):
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)
        return ok


def addDir(name,url,mode,iconimage):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok

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


#menu principal:

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
    
if mode==None:

    data = get_html_source( "http://fr.anyfilm.tv/noob" )
    saison = 1
    for video in re.compile( '<a href="javascript:load\((.*?)\);" title="Lire l&#039;\xc3\xa9pisode"><img src="/img/small_play.png" alt="" /></a>\t\t\t\t\t\t\t\t \t\t\t\t<a href="javascript:load\((.*?)\);" title="Lire la version HD"><img src="/img/HD.png" alt="" /></a>\t\t\t\t\t\t\t\t \t\t\t</div>\n\t\t\t\t\t\t \t\t\t\t\t<div>\n\t\t\t\t\t\t\t \t\t\t\t<a href="javascript:load\(.*?\);" class="link">(.*?)</a>', re.DOTALL ).findall(data):
        if video[2] == "Episode 1":
            print True
            saison = saison + 1
        addLink("Saison %s: %s" % (saison , video[2]),"http://fr.anyfilm.tv/VideoVersions/get/%s/.mp4" % video[quality] ,"")
    for video in re.compile( '<a href="javascript:load\((.*?)\);" title="Lire le bonus"><img src="/img/small_play.png" alt="" /></a>\t\t\t\t\t\t \t\t\t\t<a href="javascript:load\((.*?)\);" title="Lire la version HD"><img src="/img/HD.png" alt="" /></a>\t\t\t\t \t\t\t\t\t</div>\n\t\t\t\t \t\t\t\t\t<div>\n\t\t\t\t\t \t\t\t\t\t<a href="javascript:load\(.*?\);" class="link">(.*?)</a>', re.DOTALL ).findall(data):
        addLink("Bonus: %s" % video[2],"http://fr.anyfilm.tv/VideoVersions/get/%s/.mp4" % video[quality] ,"")

xbmcplugin.endOfDirectory(int(sys.argv[1]))    

