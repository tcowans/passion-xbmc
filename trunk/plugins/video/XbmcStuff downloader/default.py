# -- coding: cp1252 -*-
########################################
#xbmcstuff downloader v1.3.1
#by ppic
########################################
##changelog:
##26/08/09: add season parse and view (all type can be view)
##26/08/09: correct bug from show clearart and tvthumbs
##27/08/09: don't show type in not image of type present
##28/08/09: platform compatibility for sqlite.
##28/08/09: optimisations to get the xml only when changing tvshow.
##30/08/09: add collection support
##03/09/09: add image dowload / correct season all does not show in list . change season format to .tbn
##05/09/09: add path for image dowload, WTF with unicode !
##05/09/09: v1.0
##06/09/09: added support for season > 9
##06/09/09: added collection download.
##06/09/09: added xbmc cache refresh for tvthumb (delete existent file cache when downloading new one)
##06/09/09: progressbar for collection download
##08/09/09: change default clearart path to special://skin
##10/09/09: added tvshow.nfo support if imdb is find in db.
##10/09/09: correction for smb path with tvshow.nfo
##19/09/09: v 1.2 added cache replace
##19/09/09: added language fix for image cache
##25/10/09: code cleaning
##25/10/09: add cleararts download in tvshow folder option.
##05/12/09: add section iconimage
            
########################################

# plugin constants
__plugin__       = "XbmcStuff Downloader"
__author__       = "Ppic"
__url__          = "http://code.google.com/p/passion-xbmc/"
__svn_url__      = "http://passion-xbmc.googlecode.com/svn/trunk/plugins/video/XbmcStuff downloader/"
__credits__      = "Team XBMC, http://xbmc.org/"
__platform__     = "xbmc media center, [LINUX, OS X, WIN32, XBOX]"
__date__         = "05-12-2009"
__version__      = "1.3.1"
__svn_revision__  = "$Revision$"
__XBMC_Revision__ = "20000" #XBMC Babylon

#import des librairies
import urllib,urllib2,re,xbmcplugin,xbmcgui,sys,os,shutil

from traceback import print_exc

# Shared resources
BASE_RESOURCE_PATH = os.path.join( os.getcwd(), "resources" )
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "lib" ) )
# append the proper platforms folder to our path, xbox is the same as win32
env = ( os.environ.get( "OS", "win32" ), "win32", )[ os.environ.get( "OS", "win32" ) == "xbox" ]
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "platform_libraries", env ) )

#import platform's librairies
from pysqlite2 import dbapi2 as sqlite3
import elementtree.ElementTree as ET
from file_item import Thumbnails
thumbnails = Thumbnails()

#chargement des settings

    
    
try: resolution=( "500", "356" )[ int( xbmcplugin.getSetting("resolution") ) ]
except:
    xbmcplugin.openSettings(sys.argv[0])
    resolution=( "500", "356" )[ int( xbmcplugin.getSetting("resolution") ) ]

try:
    clearart_in_tv_folder=(False,True)[ int( xbmcplugin.getSetting("clearart folder") ) ]
except: print_exc()
print "clearart_in_tv_folder= %s" % clearart_in_tv_folder

if not clearart_in_tv_folder:
    print "skin folder"
    try: clearart_path=xbmcplugin.getSetting("path")
    except:
        xbmcplugin.openSettings(sys.argv[0])
        clearart_path=xbmcplugin.getSetting("path")
    if clearart_path == "special://skin": xbmcplugin.openSettings(sys.argv[0])
    if clearart_path.startswith( "special://" ): clearart_path = xbmc.translatePath( clearart_path )
    print "clearart_path: %s" % clearart_path

#variables
tvshow_list= {}
db_path=os.path.join(xbmc.translatePath( "special://profile/Database/" ), "MyVideos34.db")
temp_xml=os.path.join(os.getcwd(), 'resources' , 'data' , 'temp.xml')
base_url= "http://www.xbmcstuff.com/scrapping.php?"
icons_path= os.path.join( BASE_RESOURCE_PATH , "icons" )

options= "id_scrapper=1&size=%s&mode=1" % (resolution)

#fonction du plugin All Game by Frost
from string import maketrans
def translate_string( strtrans, del_char="" ):
    # frm = Representation of " Non-ASCII character "
    #if "\xc3\xa9" in strtrans:
    #    strtrans = strtrans.replace( "\xc3\xa9", "\xe9" )
    frm = '\xe1\xc1\xe0\xc0\xe2\xc2\xe4\xc4\xe3\xc3\xe5\xc5\xe6\xc6\xe7\xc7\xd0\xe9\xc9\xe8\xc8\xea\xca\xeb\xcb\xed\xcd\xec\xcc\xee\xce\xef\xcf\xf1\xd1\xf3\xd3\xf2\xd2\xf4\xd4\xf6\xd6\xf5\xd5\xf8\xd8\xdf\xfa\xda\xf9\xd9\xfb\xdb\xfc\xdc\xfd\xdd'
    #print " Non-ASCII character =", frm
    to = "aAaAaAaAaAaAaAcCDeEeEeEeEiIiIiIiInNoOoOoOoOoOoOsuUuUuUuUyY"
    # Construct a translation string
    table = maketrans( frm, to )
    is_unicode = 0
    if isinstance( strtrans, unicode ):
        is_unicode = 1
        # remove unicode
        strtrans = "".join( [ chr( ord( char ) ) for char in strtrans ] )
    if not del_char:
        # set win32 and xbox default invalid characters
        del_char = """,*=|<>?;:"+""" #+ "\xc3\xa9"
    # translation string
    s = strtrans.translate( table, del_char )
    # now remove others invalid characters
    s = "".join( [ char for char in s if ord( char ) < 127 ] )
    #if is_unicode:
    #    #replace unicode
    #    s = unicode( s )#, "utf-8" )
    return s

#classe permettant de manipuler chaque serie
class Tvshow:
    def __init__(self,tvid):
        self.tvid = tvid
        self.name = self.get_db("name")
        self.path = self.get_db("path")
        self.tvshowthumb = ""
        self.clearart = ""
        self.season = ""
        self.xmldata = ""
        self.collection = ""

    #récupération de l'id tvdb dans le nfo si un imdb est présent en base.
    def get_nfo_id(self):
        nfo= os.path.join(self.path , "tvshow.nfo")
        print nfo
        nfo_read = file(repr(nfo).strip("u'\""), "r" ).read()
        tvdb_id = re.findall( "<tvdbid>(\d{1,10})</tvdbid>", nfo_read )
        print "thetvdb id: %s" % tvdb_id[0]
        return tvdb_id[0]


    
    #télechargement image par image
    def get_image(self,name,url):
        success = False
        try:
            print "parametres:"
            url = url.replace(" ", "%20")
            print "-%s-" % (url)
            
            if name =="Clearart":
                if clearart_in_tv_folder: folder = repr( self.path ).strip( "u'\"" )
                else: folder = clearart_path
                print "folder: %s" % (folder)
                try:
                    if clearart_in_tv_folder: filename = "clearart.png"
                    else: filename = "%s.png" % translate_string( self.name )
                    print "name: %s" % filename #translate_string( self.name )
                except:
                    print_exc()
                
            elif name == "TVthumbs":
                filename = "folder.jpg"
                folder = repr( self.path ).strip( "u'\"" )
                thumb = thumbnails.get_cached_video_thumb( self.path )
                
            elif name[:6] == "season":
                if name[:10]=="season-all":
                    filename = "%s.tbn" % (name[:10])
                else:
                    filename = "%s.tbn" % (name[:8])
                folder = repr( self.path ).strip( "u'\"" )
                try:
                    if name[6:8] == "-a": thumb =  thumbnails.get_cached_season_thumb( "%s%s" % (self.path , xbmc.getLocalizedString(20366)) )
                    elif int(name[6:8]) == 0: thumb = thumbnails.get_cached_season_thumb( "%s%s" % (self.path, xbmc.getLocalizedString(20381)) )
                    elif int(name[6:8]) < 10: thumb = thumbnails.get_cached_season_thumb( "%s%s%s" % (self.path , xbmc.getLocalizedString(20358).strip("%i"), name[7:8]) )
                    else: thumb = thumbnails.get_cached_season_thumb( "%s%s%s" % (self.path , xbmc.getLocalizedString(20358).strip("%i"), name[6:8]) )
                except:
                    print_exc()

            fp, h = urllib.urlretrieve(url,os.path.join(folder,filename))
            
            try:
                if os.path.isfile(thumb): os.remove(thumb)
            except:
                print_exc()
            try:
                shutil.copyfile(os.path.join(folder,filename), thumb)
            except:
                print_exc()
            print fp # fp = filename
            print h # h = headers
            success = fp
        except:
            print "error: impossible de downloader l'image"
            print_exc()
        return success

    def dl_collection(self,type,id,name):
        dp = xbmcgui.DialogProgress()
        
        dp.create("Downloading files...")
        total_item= float(len(self.collection[name]))
        for i, (imgname , imgurl) in enumerate(self.collection[name]):
            current_item= float(i+1)
            ratio= int(current_item/total_item*100)
            dp.update(ratio , "Downloading %s" % imgname , "From %s" % imgurl)
            if dp.iscanceled() :
                message = "Download canceled"
                break                    
            try:
                if self.get_image( imgname, imgurl ): message = "Collection downloaded successfully"
                else: message = "Error while downloading collection"
            except:
                message = "Error while downloading"
                print_exc()
        dp.close()
        end_of_directory( False )
        xbmcgui.Dialog().ok( name, message )


    #téléchargement du xml
    def get_xml(self):
        if not self.tvid.isdigit(): url_id = self.get_nfo_id()
        else: url_id = self.tvid
        self.xmldata = urllib.urlopen("%s%s&thetvdb=%s" % (base_url, options, url_id)).read()
        open(temp_xml, 'wb').write(str(self.xmldata.strip()))
        print "!!!!!!!! xml download: %s  : %s%s&thetvdb=%s !!!!!!!!" % (url,base_url, options, self.tvid)
        
    #génération menus images    
    def menu_list(self,type):
        if type == "TVthumbs":
            selec = self.tvshowthumb.rsplit("|")
            for i in range(len(selec)-1):
                if i == 0:
                    num = ""
                else:
                    num = i                  
                addDir(selec[i],"TVthumbs&&%s" %(self.tvid),3,selec[i].replace(" ", "%20"))

                    
        elif type == "Clearart":
            selec = self.clearart.rsplit("|")
      
            for i in range(len(selec)-1):
                if i == 0:
                    num = ""
                else:
                    num = i
                try:
                    addDir(selec[i],"Clearart&&%s" %(self.tvid),3,selec[i].replace(" ", "%20"))

                except:
                    pass

        
        elif type == "Seasonthumbs":
            
            for season, imgurl in sorted(set(self.season.items())):                
                selec = imgurl.rsplit("|")

                num = season
                for i in range(len(selec)):
                    if i == 0:
                        plus=""
                    else:
                        plus="-%s" % (i)
                    try:
                        addDir("%s%s" % (num,plus),"%s&&%s" %(selec[i],self.tvid),3,selec[i].replace(" ", "%20"))
                    except:
                        pass

                    
        elif type[:10] == "Collection":            
            for imgname , imgurl in self.collection[type[12:]]:
                try:
                    addDir("%s" % (imgname),"%s&&%s" %(imgurl,self.tvid),3,imgurl.replace(" ", "%20"))
                except:
                    print_exc()
            #ajout d'un élément pour télécharger une collection
            addDir("Download the collection" ,"%s&&%s" %(type[12:],self.tvid),4,"")
       
    #methode pour récup les info en base, passage en parametre de l'action
    def get_db(self,action):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
 
        req = None
        if action == "path":
            req='select path.strpath from tvshow,tvshowlinkpath,path where tvshow.idShow=tvshowlinkpath.idshow and tvshowlinkpath.idpath=path.idpath and tvshow.c12=\"%s\"' % (self.tvid)
        elif action == "name":
            req='select c00 from tvshow where c12=\"%s\"' % (self.tvid)
        elif action == "strFileName":
            for fname in c.execute('select episodeview.strFileName from tvshow , episodeview where tvshow.c12=\"%s\" AND tvshow.idShow=episodeview.idShow' % (self.tvid)):
                c.close()
                return fname[0]
 
        if req is not None:
            for raw in c.execute( req ):
                c.close()
                print repr( raw[0] ).strip( "u'\"" ) #print "%s" % raw[0]
                return raw[0]
        c.close()



def parser(data):
    def load_infos(filename):
        try:
            tree = ET.parse(filename)
            root = tree.getroot()            
            del tree
            return root
        except:
            print "error load_info xml"
            print_exc()

    #print data.xmldata    
    elems = load_infos(temp_xml)
    collect = {}

    # récup collection --> {'collection_name1': [['tvthumb', 'image_url'], ['season00', 'image_url']], 'collection2_name': [['image_url'], ['season00', 'image_url']]}
    def add_collection(c_name,imgname,imgurl):
        if c_name in collect:
            collect[c_name].append([imgname,imgurl])
        else:
            collect[c_name] = []
            collect[c_name].append([imgname,imgurl])
    
    # récup url vignettes tv --> "url1|url2|url3|..."    
    try:
        for elem in elems.find( "tvthumbs" ).findall( "tvthumb" ):
            if elem.attrib.has_key('collection'):
                add_collection(elem.attrib['collection'],"tvthumb",elem.text)
            data.tvshowthumb="%s|%s" % (elem.text, data.tvshowthumb)
    except:
        data.tvshowthumb="no tvthumb"
        
    # récup url vignettes saison --> {"seasonxx": "url1|url2|url3|...",...}        
    season = {}
    try:
        for i in range(0,20):
            if i <= 9: c_season = "0%s" % (i)
            else : c_season = "%s" % (i)
            for elem in elems.find( "seasonthumbs" ).findall('season%s' % (c_season)):
                if elem.attrib.has_key('collection'):
                    add_collection(elem.attrib['collection'],"season%s" % (c_season),elem.text)
                if season.has_key('season%s' % (c_season)):
                    prev = season['season%s' % (c_season)]
                    season['season%s' % (c_season)]= "%s|%s" % (elem.text,prev)
                else:
                    season['season%s' % (c_season)]= "%s" % (elem.text)
    except: print_exc()

    try:
        for elem in elems.find( "seasonthumbs" ).findall('season-1'):
            if elem.attrib.has_key('collection'):
                add_collection(elem.attrib['collection'],"season-all",elem.text)
            if season.has_key('season-all'):
                prev = season['season-all']
                season['season-all']= "%s|%s" % (elem.text,prev)
            else:
                season['season-all']= "%s" % (elem.text)
    except: print_exc()
    
    data.season = season
    
    # récup url clearart --> "url1|url2|url3|..." 
    try:
        for elem in elems.find( "cleararts" ).findall( "clearart" ):
            if elem.attrib.has_key('collection'):
                add_collection(elem.attrib['collection'],"clearart",elem.text)
            data.clearart="%s|%s" % (elem.text, data.clearart)
    except:
        data.clearart="no clearart"   

    #enregistrement des collection dans l'instance
    data.collection=collect

#récupération du nom et de l'id des tvshow dans la base xbmc pour faire une liste
def listing():
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('select c00,c12 from tvshow')
    try:
        for import_base in c:
            tvshow_list[import_base[1]] = import_base[0]    
        for tvshow_id, tvshow_name in sorted(tvshow_list.items(), key=lambda item: item[1]):
                addDir(tvshow_name,tvshow_id,1,"")
        c.close()
    except:
        print "no tvdbid found in db"
        print_exc()

#génération des entrée de menu
def addDir(name,url,mode,iconimage):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Picture", infoLabels={ "Title": name } )
        if mode == 5: liz.addContextMenuItems([("download collection","RunScript(os.path.join(BASE_RESOURCE_PATH,'test.py')")])
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok

#fin de liste 
def end_of_directory( OK ):
    xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=OK )

        
#récupération des paramètres entre chaque menu
def get_params():
        param=[]
        print "runplugin", sys.argv[ 0 ] + sys.argv[ 2 ]
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

   
#initialisation
url=None
name=None
mode=None
params=get_params()

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


#Menu principal
if mode==None:
    listing()
    end_of_directory( True )
    
#Menu série tv
elif mode==1:
    current_show = Tvshow(url)
    current_show.get_xml()
    parser(current_show)
    if current_show.clearart != "no clearart": addDir('Clearart',url,2,os.path.join( icons_path , "clearart.png" ))
    if current_show.season: addDir('Seasonthumbs',url,2,os.path.join( icons_path , "seasons.png" ))
    if current_show.tvshowthumb != "no tvthumb": addDir('TVthumbs',url,2,os.path.join( icons_path , "thumbs.png" ))
    if current_show.collection:
        for i in current_show.collection: addDir("Collection: %s" % (i),url,2,os.path.join( icons_path , "collections.png" ))
    end_of_directory( True )


#Menu images
elif mode==2:
    current_show = Tvshow(url)
    parser(current_show)
    current_show.menu_list(name)
    end_of_directory( True )
    
#mode de téléchargement des images
elif mode==3:
    #tri car les saisons arrive avec des parametres différents
    if name[:6] == "season":
        type = name
        id = url.rsplit("&&")[1]
        url= url.rsplit("&&")[0]
    else:
        type=url.rsplit("&&")[0]
        id=url.rsplit("&&")[1]
        url=name
        
    print "--type: %s"%(type)
    print "--id: %s"%(id)
    print "--url: %s"%(url)
    current_show = Tvshow(id)
    print "tvshowpath= %s" % (current_show.path)
    
    end_of_directory( False )
    
    from mydialog import MyDialog
    MyDialog( type, url, type=type )
    
#mode de téléchargement de collection
elif mode==4:
    type=name[13:]
    id=url.rsplit("&&")[1]
    name=url.rsplit("&&")[0]
    print "--type: %s"%(type)
    print "--id: %s"%(id)
    print "--collection name: %s"%(name)
    
    
    if xbmcgui.Dialog().yesno( "collection download" , "Do you want to download this collection?" ):
        current_show = Tvshow(id)
        parser(current_show)
        current_show.dl_collection(type,id,name)

    else:
        end_of_directory( False )
