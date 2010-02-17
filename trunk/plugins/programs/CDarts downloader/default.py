
# plugin constants
__plugin__       = "CDart Downloader"
__author__       = "Ppic"
__url__          = "http://code.google.com/p/passion-xbmc/"
#__svn_url__      = "http://passion-xbmc.googlecode.com/svn/trunk/plugins/video/XbmcStuff downloader/"
__credits__      = "Team XBMC, http://passion-xbmc.org/"
__platform__     = "xbmc media center, [LINUX, OS X, WIN32, XBOX]"
__date__         = "17-02-2010"
__version__      = "1.0.1"
__svn_revision__  = "$Revision$"
__XBMC_Revision__ = "20000" #XBMC Babylon
__useragent__    = "Mozilla/5.0 (Windows; U; Windows NT 5.1; fr; rv:1.9.0.1) Gecko/2008070208 Firefox/3.0.1"

#import des librairies
import urllib
import sys
import os
import unicodedata
import re
from traceback import print_exc
import xbmcgui
import xbmcplugin
import xbmc
# Shared resources
BASE_RESOURCE_PATH = os.path.join( os.getcwd(), "resources" )
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "lib" ) )
# append the proper platforms folder to our path, xbox is the same as win32
env = ( os.environ.get( "OS", "win32" ), "win32", )[ os.environ.get( "OS", "win32" ) == "xbox" ]
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "platform_libraries", env ) )

#import platform's librairies
from pysqlite2 import dbapi2 as sqlite3

Language = xbmc.Language(os.getcwd())
#variables
OK = True
db_path = os.path.join(xbmc.translatePath( "special://profile/Database/" ), "MyMusic7.db")
xmlfile = os.path.join( BASE_RESOURCE_PATH , "temp.xml" )
artist_url = "http://www.xbmcstuff.com/music_scraper.php?&id_scraper=OIBNYbNUYBCezub&t=artists"
album_url = "http://www.xbmcstuff.com/music_scraper.php?&id_scraper=OIBNYbNUYBCezub&t=cdarts"
cross_url = "http://www.xbmcstuff.com/music_scraper.php?&id_scraper=OIBNYbNUYBCezub&t=cross"

try: storage=( "skin", "albumfolder" )[ int( xbmcplugin.getSetting("folder") ) ]
except:
    xbmcplugin.openSettings(sys.argv[0])
    storage=( "skin", "albumfolder" )[ int( xbmcplugin.getSetting("folder") ) ]
print "storage = %s" % storage
if storage == "skin":
    cdart_path = os.path.join(xbmc.translatePath("special://skin\media"),"backdrops","artist_fanart","cd")
    if not os.path.exists(cdart_path): os.makedirs(cdart_path)
    print cdart_path

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

def end_of_directory( OK ):
    xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=OK )


def coloring( text , color , colorword ):
    if color == "red": color="FFFF0000"
    if color == "green": color="ff00FF00"
    if color == "yellow": color="ffFFFF00"
    colored_text = text.replace( colorword , "[COLOR=%s]%s[/COLOR]" % ( color , colorword ) )
    return colored_text

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

def save_xml( data ):
        file( xmlfile , "w" ).write( repr( data ) )
        
def load_data( file_path ):
    try:
        temp_data = eval( file( file_path, "r" ).read() )
    except:
        print_exc()
        print "impossible de charger le fichier %s" % xmlfile
        temp_data = ""
    return temp_data

def get_local_artist():
    conn_b = sqlite3.connect(db_path)
    d = conn_b.cursor()
    d.execute('SELECT strArtist , idArtist FROM artist ')
    count = 1
    artist_list = []
    for item in d:
        artist = {}
        artist["name"]= item[0].encode("utf-8")
        artist["local_id"]= item[1]
        artist_list.append(artist)
        #print "artist%s: %s " % ( count , item[1].encode("utf-8") )
        count = count + 1
    d.close
    print count
    return artist_list
    
def get_local_album(artist_name):
    local_album_list = []
    
    conn_b = sqlite3.connect(db_path)
    d = conn_b.cursor()
    d.execute("SELECT DISTINCT strArtist , idArtist, strPath, strAlbum FROM songview Where strArtist LIKE '%s' AND strAlbum != ''" % artist_name )
    for item in d:
        album = {}
        album["artist"] = repr(item[0]).strip("'u")
        album["artist_id"] = repr(item[1]).strip("'u")
        album["path"] = repr(item[2]).strip("'u")
        album["title"] = repr(item[3]).strip("'u").strip('"')
        local_album_list.append(album)
    d.close
    return local_album_list
    
def get_recognized( distant_artist , local_artist ):
    true = 0
    recognized = []
    for artist in local_artist:
        match = re.search('<artist id="(.*?)">%s</artist>' % str.lower( re.escape(artist["name"]) ), distant_artist )
        if match: 
            true = true + 1
            artist["distant_id"] = match.group(1)
            recognized.append(artist)
            #print "%s: local_id=%s distant_id=%s" % (artist["name"] , artist["distant_id"] , artist["local_id"])
        else:
            artist["distant_id"] = ""
            recognized.append(artist)
    print "total trouvés: %s" % true
    return recognized
    
def search(name):
    artist_album_list = []
    search_list = []
    search_dialog = []
    search_name = str.lower(name)
    for part in search_name.split(" "):
        search_xml = str.lower(get_html_source( cross_url + "&artist=%s" % part) )
        print cross_url + cross_url + "&artist=%s" % part 
        #print search_xml
        save_xml(search_xml)
        match = re.search('<message>(.*?)</message>', search_xml )    
        if match: print "not found"
            #xbmcgui.Dialog().ok( "Not Found on XBMCSTUFF", match.group(1) )
            #OK = False
        elif len(part) == 1 or part in ["the","le","de"]: print "Pass"
        else: 
            raw = re.compile( "<cdart>(.*?)</cdart>", re.DOTALL ).findall(search_xml)
            for i in raw:
                album = {}
                album["local_name"] = name
                match = re.search( "<artist>(.*?)</artist>", i )
                if match: album["artist"] = (match.group(1))
                else: album["artist"] = ""
                if not album["artist"] in search_dialog: search_dialog.append(album["artist"]) 
                match = re.search( "<album>(.*?)</album>", i )
                if match: album["title"] = (match.group(1))
                else: album["title"] = ""
                match = re.search( "<thumb>(.*?)</thumb>", i )
                if match: album["thumb"] = (match.group(1))
                else: album["thumb"] = ""
                match = re.search( "<picture>(.*?)</picture>", i )
                if match: album["picture"] = (match.group(1))
                else: album["picture"] = ""
                print album["artist"]
                search_list.append(album)
            
    if search_dialog: 
        select = None
        select = xbmcgui.Dialog().select(Language.getLocalizedString(30020), search_dialog)
        print "select: %s" % select
        if not select == -1: 
            
            for item in search_list : 
                if item["artist"] == search_list[select]["artist"]:
                    artist_album_list.append(item)
        
    else: xbmcgui.Dialog().ok( Language.getLocalizedString(30021), "%s %s" % (Language.getLocalizedString(30022), name) )
        
    return artist_album_list
    
def find_cdart(album):
    xml = get_html_source( cross_url + "&album=%s&artist=%s" % (album["title"].replace(" " , "%").replace("," , "").replace("'" , "%") , artist_album_list[0]["artist"].replace(" " , "%" )))
    #print cross_url + "&album=%s&artist=%s" % (album["title"].replace(" " , "%").replace("," , "").replace("'" , "%"), artist_album_list[0]["artist"].replace(" " , "%" ))
    match = re.findall( "<picture>(.*?)</picture>", xml )
    print xml
    return match
    
    
    
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

if mode==None :
    addDir( Language.getLocalizedString(30005),"",1,"")
    addDir(Language.getLocalizedString(30006),"",1,"")
if mode== 1 :

    distant_artist = str.lower(get_html_source( artist_url ))
    local_artist = get_local_artist()
    recognized = get_recognized( distant_artist , local_artist )
    
    if name == Language.getLocalizedString(30005):
        for artist in recognized:
            if not artist["distant_id"] == "": 
                addDir(artist["name"],artist["distant_id"],2,"")
                print "%s: local_id=%s distant_id=%s" % ( artist["name"] , artist["local_id"] , artist["distant_id"])
            
    if name == Language.getLocalizedString(30006):        
        for artist  in local_artist :
            if not artist["distant_id"] == "": 
                addDir(coloring( artist["name"] , "green" , artist["name"] ),artist["distant_id"],2,"")
            else:addDir( artist["name"],"",2,"")

    
if mode == 2:
    
    if url:
        artist_album_list = []
        artist_xml = get_html_source( album_url + "&id_artist=%s" % url )
        #save_xml(artist_xml)
        raw = re.compile( "<cdart (.*?)</cdart>", re.DOTALL ).findall(artist_xml)
        for i in raw:
            album = {}
            
            album["local_name"] = album["artist"] = name.replace("[COLOR=ff00FF00]"  , "").replace("[/COLOR]"  , "")
            match = re.search( 'album="(.*?)">', i )
            if match: album["title"] = (match.group(1))
            else: album["title"] = ""
            match = re.search( "<thumb>(.*?)</thumb>", i )
            if match: album["thumb"] = (match.group(1))
            else: album["thumb"] = ""
            match = re.search( "<picture>(.*?)</picture>", i )
            if match: album["picture"] = (match.group(1))
            else: album["picture"] = ""
            artist_album_list.append(album)
        
    else: artist_album_list = search( name)
    
    if not artist_album_list: OK = False
    else: 
        local_album_list = get_local_album(artist_album_list[0]["local_name"])
        print artist_album_list[0]["local_name"]
        #print artist_album_list
        print local_album_list
        for album in local_album_list:
            thumb =find_cdart(album)
            
            if len(thumb) == 1: 
                name = "%s-%s" % (artist_album_list[0]["local_name"] , album["title"])
                url = "%s&&%s" % (album["path"], thumb[0] )
                img = thumb[0]
                addDir(coloring( name , "green" , name ),url,4,img)
                #print "title: %s" % album["title"]
            
            elif len(thumb) == 0:
                name = "choose for %s-%s (%s)" % (album["local_name"] , album["title"] , len(thumb) )
                url = album["path"]
                for elem in artist_album_list:
                    print elem["title"]
                    print elem["picture"]
                    url = url + "&&&&" + elem["title"] + "&&" + elem["picture"]
                
                img = ""
                addDir( name ,url,4,img)
            
            else :
                url = ""
                #for elem in thumb:
                    #url = url + elem + "&&"
                for elem in artist_album_list:
                    print elem["title"]
                    print elem["picture"]
                    url = url + "&&&&" + elem["title"] + "&&" + elem["picture"]
                name = "choose for %s-%s (%s)" % (album["local_name"] , album["title"] , len(thumb) )
                img = ""
                addDir( name ,url,4,img)
            
            
if mode == 3:
    pass           
if mode == 4:
    if storage == "albumfolder" : name = "cdart"
    else: name = name.replace("[COLOR=ff00FF00]"  , "").replace("[/COLOR]"  , "").replace("(.*)"  , "").replace("choose for "  , "")
    print len(url.split("&&")) , len(url.split("&&&&"))
    
    if len(url.split("&&")) == 2:
        if storage == "albumfolder" : path =  os.path.join(url.split("&&")[0],"%s.png" % name ).encode("utf8")
        if storage == "skin" : path =  os.path.join( cdart_path , "%s.png" % name ).encode("utf8")
        else : path =  os.path.join(url.split("&&")[0],"%s.png" % name ).encode("utf8")
        cdart = url.split("&&")[1]
        select = 0
        
    else:
        album_search = []
        album_choice = []
        for unit in url.split("&&&&"):
            print unit.split("&&")
            if len(unit.split("&&")) == 1:
                if storage == "albumfolder" :path = os.path.join(unit,"%s.png" % name ).encode("utf8")
                if storage == "skin" : os.path.join( cdart_path , "%s.png" % name ).encode("utf8")
            else:
                if not unit.split("&&") == ['']:
                    print unit.split("&&")[0] , unit.split("&&")[1]
                    album = {}
                    album["search_name"] = unit.split("&&")[0]
                    album["search_url"] = unit.split("&&")[1]
                    album_search.append(album["search_name"])
                    album_choice.append(album)
        select = xbmcgui.Dialog().select(Language.getLocalizedString(30007), album_search)
        print select
        cdart = album_choice[select]["search_url"]
    
        #print_exc()
        #message = ["Download Error", "CDart Download Error !", "CDart get data failed", "Please report on forum"]
    
    
    if not select == -1:
        print "path =%s" % path
        print "cdart =%s" % cdart
        try : 
            fp, h = urllib.urlretrieve(cdart,path)
            print fp , h
            message = [Language.getLocalizedString(30010), Language.getLocalizedString(30011), "File: %s" % path , "Url: %s" % cdart]
            #xbmcgui.Dialog().ok( "Download Successfull", "CDart Download Succeed", "File: %s" % path , "Url: %s" % cdart )
            
        except: 
            message = [Language.getLocalizedString(30013), Language.getLocalizedString(30014), "File: %s" % path , "Url: %s" % cdart]
            print_exc()
        
    else:
        message = [Language.getLocalizedString(30015), Language.getLocalizedString(30016), Language.getLocalizedString(30017) , Language.getLocalizedString(30018) ]    
    xbmcgui.Dialog().ok(message[0] ,message[1] ,message[2] ,message[3])
    OK = False

end_of_directory( OK )
