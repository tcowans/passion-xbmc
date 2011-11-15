# -*- coding: utf-8 -*-
"""
XbmcTV plugin
Auteur : Seb & CinPoU
"""

import urllib,sys,os,re
import xbmcplugin,xbmcgui,xbmc

#On définit le type du plugin
xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category="Video" )

urllib.urlcleanup()
_playlist = xbmc.PlayList(1)



try:
    from xbmcaddon import Addon

    # source path for launchers data
    PLUGIN_DATA_PATH = xbmc.translatePath( os.path.join( "special://profile/addon_data", "plugin.video.tvplugin") )

    __settings__ = Addon( id="plugin.video.tvplugin" )
    __language__ = __settings__.getLocalizedString
    print "Mode AddOn ON"
    print PLUGIN_DATA_PATH


except : 
    # source path for launchers data
    PLUGIN_DATA_PATH = xbmc.translatePath( os.path.join( "special://profile/plugin_data", "programs", sys.modules[ "__main__" ].__plugin__) )

    __settings__ = xbmcplugin
    __language__ = xbmc.getLocalizedString
    print "Mode plugin ON"
    print PLUGIN_DATA_PATH



#Définition des variables des dossiers

if os.name=='posix':
    # Linux case
    ROOTDIR = os.path.abspath(os.curdir).replace(';','')
else:
    # Xbox and Windows case
    ROOTDIR = os.getcwd().replace(';','')

imgDir = os.path.join(ROOTDIR,"resources","Icons")


if __settings__.getSetting('FAI') == "" :
    __settings__.openSettings(url=sys.argv[0])


  
def _unicode( s, encoding="utf-8" ):
    """ customized unicode, don't raise UnicodeDecodeError exception, return no unicode str instead """
    try: s = unicode( s, encoding )
    except: pass
    return s

def download(url):
    download_path = "special://temp/playlist.m3u"
    urllib.urlretrieve( url, download_path)
    return download_path

def get_m3u_url():
    #m3u_url='http://mafreebox.freebox.fr/freeboxtv/playlist.m3u'
    fai = __settings__.getSetting('FAI')
    print "FAI= %s"%fai
    if fai == '1':
        m3u_url = 'http://tv.sfr.fr/tv-pc/televisionsurpc.m3u'
    elif fai == '0':
        m3u_url = 'http://mafreebox.freebox.fr/freeboxtv/playlist.m3u'
    elif fai == '2':
        m3u_url = 'http://download.porciello.com/orange/tv/BouquetTV_Orange_v2.3.m3u'
        
        
    return m3u_url

    

def playlist(playlist_file):
    _playlist.load(playlist_file)
    dico = {}
    listitem = []
    description = []
    position = []
    dico['listitem']=listitem
    dico['description']=description
    dico['position']=position
    for item in range(_playlist.size()):
        position.append(item)
        listitem.append(_playlist[item].getfilename())
        description.append(_playlist[item].getdescription())   
    return dico 




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
        
        
        
def externalPlay(url) :
    
    if __settings__.getSetting('cmdline') == "" and __settings__.getSetting('path') == "":
        __settings__.openSettings(url=sys.argv[0])
    elif __settings__.getSetting('cmdline') != "" :
        cmd = __settings__.getSetting('cmdline')
    else:
        cmd = __settings__.getSetting('path') 

    if (os.environ.get( "OS", "xbox" ) == "xbox"):
        xbmc.executebuiltin('XBMC.Runxbe(' + cmd + ' '+ __settings__.getSetting('arguments') + ' '+ url + ')')
    else:
        if (sys.platform == 'win32'):
            xbmc.executebuiltin("%s(\"\\\"%s\\\" %s %s\")" % ("System.ExecWait", cmd, __settings__.getSetting('arguments') , url))
        elif (sys.platform.startswith('linux')):
            url = '"'+url+'"'
            #os.system("%s %s" % ("/usr/bin/vlc", url))
            os.system("%s %s %s" % (cmd,__settings__.getSetting('arguments'), url))
        else:
            pass;
            # unsupported platform
            
            
            
def chaineNum(stream, fai) :
    
    if fai == '0':
        try :
            match = re.compile('(.+?) - ').findall(stream)
            num = match[0]  
            return num
        except:
            return "tv"
            
            
   
def show_icones():
    """
    Affichage
    """
    print __settings__.getSetting('extplayer')
        
    ok=True
    m3u_url = get_m3u_url()
    dico = playlist(download(m3u_url))
    fai = __settings__.getSetting('FAI')
    
    if __settings__.getSetting('extplayer') == "true" :
        item=xbmcgui.ListItem("0 - Zapping")
        url=sys.argv[0]+"?url="+urllib.quote_plus(m3u_url)+"&mode=2"
        ok = ok and xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=item,isFolder=True,totalItems=len(dico['listitem']))
    
    for indice in range(len(dico['listitem'])):
        if not '#' in dico['description'][indice]:
            #url=sys.argv[0]+"?filename="+str(dico['listitem'][indice])
            url=dico['listitem'][indice]

            
            
            if fai == '0' :
                num = chaineNum(dico['description'][indice],fai)
                iconimage = num + ".gif"
                iconimage = os.path.join(imgDir,iconimage)
                                
                item=xbmcgui.ListItem(_unicode(dico['description'][indice]), iconImage=iconimage, thumbnailImage=iconimage)
                
            else :
                item=xbmcgui.ListItem(_unicode(dico['description'][indice]))
                
            if __settings__.getSetting('extplayer') == "false" :
                ok = ok and xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=item,isFolder=False,totalItems=len(dico['listitem']))
            else :
                url=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode=2"
                ok = ok and xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=item,isFolder=True,totalItems=len(dico['listitem']))
           
    return ok






print "PARAM = %s"%sys.argv[2]

#Récupération des paramètres             
params=get_params()
url=None
mode=None
playerPath = __settings__.getSetting('path')
try:
        url=urllib.unquote_plus(params["url"])
except:
        pass
try:
        mode=int(params["mode"])
except:
        pass
        
print "Mode: "+str(mode)
print "URL: "+str(url)
if mode==2 and __settings__.getSetting('extplayer') == "true":
    print "CHARGEMENT..."
    externalPlay(url)
    show_icones()
else :
    show_icones()    
xbmcplugin.endOfDirectory(int(sys.argv[1]))

 
 
        
