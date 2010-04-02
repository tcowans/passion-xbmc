# plugin constants
__plugin__       = "Skins Nightly Builds Passion"
__author__       = "Ppic"
__url__          = "http://code.google.com/p/passion-xbmc/"
__svn_url__      = "http://passion-xbmc.googlecode.com/svn/trunk/plugins/program/Skins Nightly Builds Passion/"
__credits__      = "Team XBMC, http://passion-xbmc.org/"
__platform__     = "xbmc media center, [LINUX, OS X, WIN32, XBOX]"
__date__         = "02-04-2010"
__version__      = "1.0"
__svn_revision__  = "$Revision$"
__XBMC_Revision__ = "20000" #XBMC Babylon
__useragent__    = "Mozilla/5.0 (Windows; U; Windows NT 5.1; fr; rv:1.9.0.1) Gecko/2008070208 Firefox/3.0.1"

#import des librairies
import urllib
import sys
import os
import re
import xbmcgui
import xbmcplugin
import xbmc

from traceback import print_exc

# Shared resources
BASE_RESOURCE_PATH = os.path.join( os.getcwd(), "resources" )
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "lib" ) )
BASE_URL = [ "http://passion-xbmc.org/downloads/?cat=7;start=%s" , "http://passion-xbmc.org/downloads/?cat=24;start=%s" ][int(xbmcplugin.getSetting("skin_type"))]
BASE_DL = "http://passion-xbmc.org/downloads/?sa=downfile;id=%s"
CACHE_DIR = os.path.join( BASE_RESOURCE_PATH , "cache" )
Language = xbmc.Language(os.getcwd())
DIALOG_PROGRESS = xbmcgui.DialogProgress()
dialog = xbmcgui.Dialog()
SKIN_DIR = xbmc.translatePath("special://home/skin/")
print SKIN_DIR

import unzip


#variables:
OK = True
skin_unziped = False


def addLink(name,url,iconimage):
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
        liz.setInfo( type="file", infoLabels={ "Title": name } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)
        return ok

def addDir(name,url,mode,iconimage):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        ok=True

        already_exists = os.path.exists( os.path.join( SKIN_DIR, name ) )
        label2 = ( "", Language.getLocalizedString( 30005 ) )[ already_exists ]

        liz=xbmcgui.ListItem( name, label2, iconImage="DefaultFolder.png", thumbnailImage=iconimage )

        infolabels = { "Title": name, "Genre": label2 }
        # Ajout d'un overlay pour dire qu'il est installer
        # ICON_OVERLAY_HD, ICON_OVERLAY_LOCKED, ICON_OVERLAY_NONE, ICON_OVERLAY_RAR, ICON_OVERLAY_HAS_TRAINER
        # ICON_OVERLAY_TRAINED, ICON_OVERLAY_UNWATCHED, ICON_OVERLAY_WATCHED, ICON_OVERLAY_ZIP
        overlay = ( xbmcgui.ICON_OVERLAY_UNWATCHED, xbmcgui.ICON_OVERLAY_WATCHED )[ already_exists ]
        # verifie si c'est pas le skin courant est change l'overlay pour un lock
        overlay = ( overlay, xbmcgui.ICON_OVERLAY_LOCKED )[ ( name.lower() == xbmc.getSkinDir().lower() ) ]
        infolabels.update( { "watched": already_exists, "overlay": overlay } )
        liz.setInfo( type="Video", infoLabels=infolabels )

        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False)
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

def end_of_directory( OK ):
    if ( OK ):
        # sort by genre so all installed status
        xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_GENRE )
    xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=OK )

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
########################TOOLS##############################
def svg( data , filename ): 
    if not os.path.exists( CACHE_DIR ): os.makedirs( CACHE_DIR )
    file( os.path.join( CACHE_DIR , filename ) , "w" ).write( repr( data ) )
    
########################MENUS##############################
class pDialogCanceled( Exception ):
    def __init__( self, errmsg="Downloading was canceled by user!" ):
        self.msg = errmsg

def get_skins_list():
    compteur = 0
    while compteur < 100:
        print compteur
        data = get_html_source( BASE_URL % compteur )
        if data == "": break
        #svg( data , "page.html" )
        result = re.findall(r'<div class="titlebg" width="100%" height="100%" align="center" style="vertical-align: center; font-size: 14px;"><strong><a href="http://passion-xbmc.org/downloads/\?sa=view;down=(\d+).*" style="font-size: 14px;" title="[! a-zA-Z0-9_-]+">([! a-zA-Z0-9_-]+)</a></strong></span>', data)
        for i in result: addDir(i[1],BASE_DL % i[0],1,"")
        if result == [] : break
        else: compteur = compteur + 12
        print result

def skin_download(name , url):
    download = dialog.yesno( Language.getLocalizedString(30031) , Language.getLocalizedString(30032) , name )
    if download:
        if not os.path.exists( CACHE_DIR ): os.makedirs( CACHE_DIR )
        try:
            destination = os.path.join( CACHE_DIR , "%s.zip" % name )
            DIALOG_PROGRESS.create( Language.getLocalizedString(30031), Language.getLocalizedString(30033) )
            def _report_hook( count, blocksize, totalsize ):
                _line3_ = ""
                if totalsize > 0:
                    _line3_ += "%s: %sMo/%sMo" % ( Language.getLocalizedString(30034) , round(( ( count * blocksize ) / 1024.0 / 1024.0 ), 2 ), round(( totalsize / 1024.0 / 1024.0  ) , 2), )
                else:
                    _line3_ += "string2 %s" % ( ( ( count * blocksize ) / 1024.0 / 1024.0 ), )
                percent = int( float( count * blocksize * 100 ) / totalsize )
                strProgressBar = str( percent )
                if ( percent <= 0 ) or not strProgressBar: strPercent = "0%"
                else: strPercent = "%s%%" % ( strProgressBar, )
                _line3_ += " | %s" % ( strPercent, )
                DIALOG_PROGRESS.update( percent, name, _line3_ )
                if ( DIALOG_PROGRESS.iscanceled() ):
                    raise pDialogCanceled()
            fp , h = urllib.urlretrieve(url,destination , _report_hook )
            print fp
            return fp
        except pDialogCanceled, error:
            xbmc.log( "[SCRIPT: %s] DIALOG::PROGRESS: %s" % ( __plugin__, error.msg ), xbmc.LOGWARNING )
        DIALOG_PROGRESS.close()
        return(False)
        
    else: dialog.ok( Language.getLocalizedString(30035) , Language.getLocalizedString(30036) )

def unzip_skin( temp_zip , name ):
    dezip = dialog.yesno( Language.getLocalizedString(30037) , Language.getLocalizedString(30038) , name)
    if dezip:
        DIALOG_PROGRESS.create( Language.getLocalizedString(30037) , Language.getLocalizedString(30039) , Language.getLocalizedString(30040))
        xbmc.log( "[SCRIPT: %s] starting - [unzip(%s,%s)]" % ( __plugin__, "%s.zip" % name, SKIN_DIR ), xbmc.LOGNOTICE )
        zipskin = unzip.unzip()
        zipskin.extract(temp_zip, SKIN_DIR)
        DIALOG_PROGRESS.close()
        xbmc.log( "[SCRIPT: %s] finish - [unzip(%s,%s)]" % ( __plugin__, "%s.zip" % name, SKIN_DIR ), xbmc.LOGNOTICE )
        return (True)
        
#menu principal:

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

if mode==None: get_skins_list()

if mode==1: 
    temp_zip = skin_download(name , url)
    print "temp: %s" % temp_zip
    skin_path = xbmc.translatePath( "special://skin" ).strip( os.sep )
    cur_skin  = os.path.basename( skin_path )
    print cur_skin
    if name == cur_skin: dialog.ok( Language.getLocalizedString(30041) , Language.getLocalizedString(30042) )
    elif temp_zip: skin_unziped = unzip_skin( temp_zip , name )
    if skin_unziped : xbmc.executebuiltin("XBMC.Notification(%s,%s,5000,%s)"%( "install success",name , ""))
    OK = False

end_of_directory( OK )