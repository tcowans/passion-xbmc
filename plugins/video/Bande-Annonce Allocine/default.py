# -*- coding: cp1252 -*-

# script constants
__plugin__       = "Bandes-Annonces Allocine"
__author__       = "Ppic"
__url__          = "http://code.google.com/p/passion-xbmc/"
__svn_url__      = "http://passion-xbmc.googlecode.com/svn/trunk/plugins/"
__credits__      = "Team XBMC passion, http://passion-xbmc.org/developpement-python/%28script%29-sporlive-display/"
__platform__     = "xbmc media center, [LINUX, OS X, WIN32, XBOX]"
__date__         = "28-02-2011"
__version__      = "1.5"
__svn_revision__  = "$Revision$".replace( "Revision", "" ).strip( "$: " )
__XBMC_Revision__ = "20000" #XBMC Babylon
__useragent__    = "Mozilla/5.0 (Windows; U; Windows NT 5.1; fr; rv:1.9.0.1) Gecko/2008070208 Firefox/3.0.1"


import urllib
import re
import os
import time
import xbmcgui
import xbmcplugin
from traceback import print_exc

BASE_RESOURCE_PATH = os.path.join( os.getcwd(), "resources" )
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "lib" ) )
cache_dir = os.path.join ( BASE_RESOURCE_PATH , "Cache" )
trailer_dir = xbmcplugin.getSetting("trailer_path")
trailer_dir = xbmc.translatePath(trailer_dir)
print "trailer dir: %s" % trailer_dir

tempfile= os.path.join ( cache_dir , "data.html" )
if not os.path.isdir(cache_dir):
    os.makedirs(cache_dir)

from convert import set_entity_or_charref
from convert import translate_string

try: quality=( "ld", "md", "hd" )[ int( xbmcplugin.getSetting("quality") ) ]
except:
    xbmcplugin.openSettings(sys.argv[0])
    quality=( "ld", "md", "hd" )[ int( xbmcplugin.getSetting("quality") ) ]
print xbmcplugin.getSetting("mon_cine")

def addLink(name,url,iconimage, c_items = None ):
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
        if c_items : liz.addContextMenuItems( c_items, replaceItems=True )
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)
        return ok


def addDir(name,url,mode,iconimage, c_items = None ):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        if c_items : liz.addContextMenuItems( c_items, replaceItems=True )
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
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
    
def get_film_list( url , database = False):
    catalogue = []
    page_data = get_html_source( url )
    count = 0
    pager = 1
    try: nbpage = int(re.findall( '<span class="navcurrpage">.*</span>(.*?)</li>', page_data )[0].strip( " / "))
    except:
        nbpage = "error"
        print "impossible de trouver le nb de page"
        print_exc()
    print "nb pages: %s" % nbpage
    try: total_item = int(re.findall( '<p class="extrazone">.* sur (.*?) r.*sultats</p>', page_data )[0].strip( " / "))
    except:
        total_item = "error"
        print "impossible de trouver le nb d'item"
        print_exc()
    print "nb d'items: %s" % total_item

    #progress bar:
    dp = xbmcgui.DialogProgress()
    dp.create("Update Database")
    
    
    while pager <= nbpage and nbpage != "error":
        if not pager == 1:
            current_url= "%s?page=%s" % (url , pager)
            print "page %s: %s" % ( pager , current_url )
            page_data = get_html_source( current_url )
        try:        
            MEDIA=re.compile( '<div class="mainzone">(.*?)<div class="spacer">', re.DOTALL ).findall(page_data)
            for i in  MEDIA:
                if database: film = get_film_info(id_allo)
                else: film = {}
                #print i
                film["type"] = url.split("/")[4]
                if film["type"] == "bandes-annonces": film["type"] = "film"
                elif film["type"] == "series": film["type"] = "serie"
                
                print "###################type#############################"
                print film["type"]
                count = count+1
                ratio= int(100*float(count)/float(total_item))
                #save_data(i)
                
                
                if film["type"] == "serie": match = re.search( "<span class='bold'>(.*?)<br />", i )
                elif film["type"] == "interviews": match = re.search( """<span class=\'bold\'>\r\n                                        (.*?)\r\n                                    </span>(.*?)\r\n                                </a>""", i )
                else : match = re.search( "<span class='bold'>(.*?)</span>", i )
                if match :
                    if film["type"] == "serie" : name = match.group(1).replace("</span>"," ")
                    elif film["type"] == "interviews": name = match.group(1) + match.group(2)
                    else : name = match.group(1)
                    
                else: name = ""
                
                print "récupération info %s (%s/%s): %s" % ( film["type"] , count , total_item , name )
                dp.update(ratio , "récupération info %s (%s/%s)" % ( film["type"], count , total_item ), name)
                if dp.iscanceled() :
                    break
                match = re.search( "<a href='/video/player_gen_cmedia=(.*?)&c%s=(.*?).html'" % film["type"] , i )
                if match: 
                    id_allo = match.group(2)
                    id_media = match.group(1)
                    #print "############TEST###############" + "test id:%s %s" % (match.group(1) , match.group(2))
                else : 
                    match = re.search( "cmedia=(.*?)'" , i )
                    if match:
                        id_allo = id_media = match.group(1)
                    
                try: img = re.findall( "<img src='(.*?)'", i )[0]
                except: img = ""
                #try: ba_type = re.findall( '</b> (.*?)" />', i )[0]
                #except: ba_type = ""                
                #print "%s: %s id=%s img=%s" % ( count , name , id_allo , img )
                
                film["id_allo"] = id_allo
                film["id_media"] = id_media
                film["name"] = name
                film["poster"] = img.replace( "c_120_160/b_1_x/o_play.png_5_se" , "r_760_x" ).replace("cx_120_96/b_1_x/o_play.png_5_se", "r_760_x" ).replace("c_120_120/b_1_x/o_play.png_5_se", "r_760_x" )
                film["poster"] = film["poster"].replace("cx_120_113/o_overlayEmissions-P2C-120.png_1_c", "r_760_x" ).replace("cx_120_113/o_overlayEmissions-MerciQui-120.png_1_c", "r_760_x" ).replace("cx_120_113/o_overlayEmissions-LaMinute-120.png_1_c", "r_760_x" ).replace("cx_120_113/o_overlayEmissions-D2DVD-120.png_1_c", "r_760_x" ).replace("cx_120_113/o_overlayEmissions-TES-120.png_1_c", "r_760_x" ).replace("cx_120_113/o_overlayEmissions-FauxR-120.png_1_c", "r_760_x" )
                catalogue.append(film)
        
                
                            
        except:
            print "probleme de récupération de la liste de film"
            print_exc()
            
        pager = pager + 1
    dp.close()
    print "total movies = %s" % count
    return catalogue

def get_film_info(id_allo):
    film = {}
    film_url = "http://www.allocine.fr/film/fichefilm_gen_cfilm=%s.html" % id_allo
    film_data = get_html_source( film_url )
    #save_data(film_data)
    try: media_list = re.findall( '<a href="/video/player_gen_cmedia=(.*?)&cfilm=.*.html"><b>', film_data )
    except:
        print_exc()
        media_list = ""
    try: film["synopsis"] = re.findall( "Synopsis : </span>(.*?)</p>", film_data )[0]
    except:
        print_exc()
        #print re.findall( "Synopsis : </span>(.*?)</p>", film_data ) 
        film["synopsis"] = ""
##    try:
##        if film["poster"]: pass    
##    except:
##        print_exc()
##        film["poster"] = re.findall( '<img src="(.*?)" alt=".*" title=".*" />', film_data )[0].replace( "r_160_214/b_1_cfd7e1" , "r_760_x" )
##        print "POSTER URL: %s" % film["poster"] 
    BA_list = []
    if media_list:
        for id_media in media_list: BA_list.append(get_media_link(id_media))
    film["Bande-annonces"] = BA_list
    return film

def get_media_link(id_media):
    media_url = "http://www.allocine.fr/skin/video/AcVisionData_xml.asp?media=%s" % id_media
    media_data = get_html_source( media_url )
    #save_data(media_data)
    media = {}
    try:media_data=re.compile( '<AcVisionVideo(.*?)/>', re.DOTALL ).findall(media_data)[0]
    except:
        print "problème de récupération info média"
        print_exc()
    try:media["name"] = set_entity_or_charref(re.findall( 'title="(.*?)"', media_data )[0])
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
        
    return media

def get_film_in_cinema( id_cine ):
    data = get_html_source( id_cine )
    #save_data(data)
    #data = load_data(tempfile)
    try:
        MEDIA=re.compile( '<div class="datablock">(.*?)<div class="vmargin10b"', re.DOTALL ).findall(data)
        #save_data(MEDIA[1] , "temp.html")
    except:
        print "failed"
        print_exc()
    film_cinema = []    
    for unit in MEDIA:
        film = {}
        try:
            raw = re.compile( "De(.*?)                          </p>", re.DOTALL ).findall(unit)[0]
            film["director"] = re.findall( "title='(.*?)'", raw )
        except: print_exc()
        try:
            raw = re.compile( "Avec(.*?)                          </p>", re.DOTALL ).findall(unit)[0]
            film["cast"] = re.findall( "title='(.*?)'", raw )
        except: print_exc()
        
        match = re.search('class="titlebar"  -->\r\n                    <p>\r\n                        \r\n                                (.*?)\r\n                            \r\n                        \((.*?)\)\r\n                        \r\n                                - Date de sortie : <b>(.*?)</b>\r\n                            \r\n                    </p>\r\n                    \r\n                            <p>', unit )
        if match:
            film["sortie"]= match.group(3)
            film["genre"]= match.group(1)
            film["duree"]= match.group(2)
        else:
            film["sortie"]= None
            film["genre"]= None
            film["duree"]= None

        
        match = re.search('<!-- /notationbar -->\r\n                    <p>\r\n(.*?)\r\n                    </p>\r\n                    <!-- !! Existing template -->', unit )
        if match: film["syno"] = match.group(1).strip(" ")
        else: film["syno"] = None
            
        match = re.search('<a href=\'/film/fichefilm_gen_cfilm=(.*?).html\'>(.*?)</a></h2>', unit )
        if match:
            film["id_allo"] = match.group(1)
            film["name"] = match.group(2) 
        else:
            film["id_allo"] = None
            film["name"] = None 
                
        match = re.search('<img src=\'(.*?)\' alt=".*" title=".*" />', unit ) 
        if match: film["poster"] = match.group(1).replace( "r_120_-1" , "r_760_x" ) 
        else: film["poster"] = None
        
        try:
            film["seances"] = re.findall( '<em ac:data="(.*?)">.*</em>', unit )
        except: print_exc()
        film_cinema.append(film)
        
        
    return film_cinema
 
def create_DB( url , dbname ):
    DB_file= os.path.join( cache_dir , "%s.txt" % dbname )
    try: save_data( get_film_list( url ) , DB_file )
    except:
        print "impossible de créer la base %s" % DB_file
        print_exc()
def load_DB(dbname):
    DB_file= os.path.join( cache_dir , "%s.txt" % dbname )
##    print "last modifications: %s" % os.path.getmtime(DB_file)
##    print "actual %s" % time.time()
##    print time.time() - os.path.getmtime(DB_file)
    
    if  os.path.isfile(DB_file):
        try:
            if time.time() - os.path.getmtime(DB_file) > 3600:
                print "base de plus de 24h, reconstruction..."
                return("")
            data=load_data(DB_file)
        except:
            print "impossible de charger %s" % DB_file
            print_exc()
            data=""
    else: data=""
    return data

def search_cinema():
    kb = xbmc.Keyboard( "", "Entrez le nom pour la recherche" )
    kb.doModal()
    if kb.isConfirmed(): 
        kw = kb.getText()
        progress = xbmcgui.DialogProgress()
        progress.create( "récupérations des informations" , "interrogation Allociné ...")
        data = get_html_source( "http://www.allocine.fr/salle/recherche/?q=%s" % kw)
        #save_data(data)
        try:
            liste_cine = re.findall( '<a class="bold" href="/seance/salle_gen_csalle=(.*?).html">(.*?)</a>', data )
            liste_dialog_choix = []
            for i in liste_cine :
                progress.update( 0 , i[1])
                liste_dialog_choix.append(i[1])
            print liste_cine
            select = xbmcgui.Dialog().select("Choisissez votre cinéma", liste_dialog_choix)
            if select == -1: OK = False
            else: 
                mes_cines = []
                if os.path.exists(os.path.join(cache_dir , "cine.list")): mes_cines = load_data(os.path.join(cache_dir , "cine.list"))
                mes_cines.append(liste_cine[select])
                save_data( mes_cines ,os.path.join(cache_dir , "cine.list"))
                xbmc.executebuiltin("Container.Refresh")
        except:
            print "echec récupération liste ciné"
            print_exc()
        
        
        if progress.iscanceled(): OK = False
        progress.close()
    else : OK = False       
    
def get_emission_list(url):
    data = get_html_source( url )
    #save_data(data)
    match = re.compile('<div class="clmmastertopic"><a href="/video/emissions/">(.*?)<div class="clmmastertopic">',re.DOTALL ).findall( data )
    if match: menu_emission = match[0]
    else: menu_emission = ""

    match = re.compile('<a href="(.*?)/">(.*?)</a>',re.DOTALL ).findall( menu_emission )
    if match: emission_list = match
    else: emission_list = ""    
    return emission_list
    

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

OK = True

if mode==None or url==None or len(url)<1:
    addDir("A ne pas manquer","http://www.allocine.fr/video/bandes-annonces/",1,"")
    addDir("films au cinema","http://www.allocine.fr/video/bandes-annonces/films-au-cinema/",1,"")
    addDir("prochainement","http://www.allocine.fr/video/bandes-annonces/films-prochainement/",1,"")
    addDir("séries Tv","http://www.allocine.fr/video/series/",1,"")
    addDir("émissions","http://www.allocine.fr/video/",6,"")
    addDir("interviews","http://www.allocine.fr/video/interviews/",1,"")
    if xbmcplugin.getSetting("mon_cine") == "true" :
        if os.path.exists(os.path.join(cache_dir , "cine.list")): 
            mes_cines = load_data(os.path.join(cache_dir , "cine.list"))
            for cine in mes_cines:
                addDir( cine[1],"http://www.allocine.fr/seance/salle_gen_csalle=%s.html" % cine[0],4,"")
        addDir("Ajouter Un Cinéma...","",3,"")

if mode == 1:
    xbmcplugin.setPluginCategory(int(sys.argv[1]), name)
    if load_DB( name ) == "": create_DB( url , name)
    data=load_DB( name )
    for film in data:
        if film["type"] == "film": addDir(film["name"],"%s##%s" % (film["poster"] , film["id_allo"]),2,film["poster"])
        else :
            print "image:%s " % film["poster"]
            c_items = []
            local_trailer = os.path.join( trailer_dir, "%s.flv" % translate_string(film["name"] ) )
            script = "special://home/plugins/video/Bande-Annonce Allocine/resources/lib/downloader.py"
            args = "%s&%s&%s" % ( urllib.quote_plus( "cmedia=%s" % film["id_media"] ), urllib.quote_plus( local_trailer ) , quality)
            if not os.path.exists(local_trailer):c_items += [ ( "Télécharger", "XBMC.RunScript(%s,%s)" % ( script, args ) ) ]
            else : c_items += [ ( "jouer en local", "xbmc.PlayMedia(%s)" % local_trailer) ]
            addDir(film["name"], film["id_media"],5,film["poster"], c_items )
        

if mode == 2:
    poster = url.split("##")[0]
    url = url.split("##")[1]
    film = get_film_info(url)

    for ba in film["Bande-annonces"]:
        #print ba
        # ajout d'un bouton dans le contextmenu pour télécharger / jouer le trailer
        c_items = []
        local_trailer = os.path.join( trailer_dir, "%s.flv" % translate_string(ba["name"] ) )
        script = "special://home/plugins/video/Bande-Annonce Allocine/resources/lib/downloader.py"
        args = "%s&%s" % ( urllib.quote_plus( ba["%s" % quality ] ), urllib.quote_plus( local_trailer ) )
        if not os.path.exists(local_trailer):c_items += [ ( "Télécharger", "XBMC.RunScript(%s,%s)" % ( script, args ) ) ]
        else : c_items += [ ( "jouer en local", "xbmc.PlayMedia(%s)" % local_trailer) ]
        
#         DLLabelButton = "Télécharger"
#         DLActionButton = 'XBMC.RunPlugin(%s?mode=10&name=%s&url=%s)' % ( sys.argv[ 0 ], urllib.quote_plus( set_entity_or_charref(ba["name"] )), urllib.quote_plus( ba["%s" % quality ] ), )
#         c_items.append(( DLLabelButton, DLActionButton ))
        addLink(ba["name"].split(" - ")[1],ba["%s" % quality ],poster , c_items )
    
    #########################################################
if mode == 3:
    search_cinema()
    OK= False
    
if mode == 4:
    mon_cine = get_film_in_cinema( url )
    #print mon_cine
    for film_in_cine in mon_cine:
        print "#######################film###################################"
        print film_in_cine["name"]
        print film_in_cine["poster"]
        print film_in_cine["syno"]
        print film_in_cine["id_allo"]
        print film_in_cine["genre"]
        print film_in_cine["director"]
        print film_in_cine["cast"]
        print film_in_cine["duree"]
        print int(film_in_cine["sortie"].split("/")[2])
        print "################################################################"
        try: addFilm(film_in_cine["name"],"%s##%s" % (film_in_cine["poster"] , film_in_cine["id_allo"]),2,film_in_cine["poster"],film_in_cine["genre"] ,film_in_cine["director"][0] ,film_in_cine["cast"] ,film_in_cine["syno"] ,film_in_cine["duree"] ,int(film_in_cine["sortie"].split("/")[2]) )
        except : print_exc()


if mode == 5:
    
    ba = get_media_link( url )
    trailer = ba["%s" % quality ]
    
    print "name: %s" % name
    print "trailer: %s" % trailer
    playableVideoItem = xbmcgui.ListItem( name , path = trailer) 
    xbmc.Player().play(trailer, playableVideoItem, False)
    OK = False

if mode == 6:
    emission_list = get_emission_list(url)
    print emission_list
    picture = {}
    picture["La Minute"] = "http://images.allocine.fr/r_120_x/commons/logos/Logos_minute_160x128.jpg"
    picture["Tueurs en SÃ©ries"] = "http://images.allocine.fr/r_120_x/commons/logos/Logos_tes_160x128.jpg"
    picture["Merci Qui?"] = "http://images.allocine.fr/r_120_x/commons/logos/Logos_merciqui_160x128.jpg"
    picture["Direct 2 DVD"] = "http://images.allocine.fr/r_120_x/commons/logos/Logos_D2D_160x128.jpg"
    picture["Faux Raccord"] = "http://images.allocine.fr/r_120_x/commons/logos/Logos_FauxR_160x128.jpg"
    picture["Plein 2 CinÃ©"] = "http://images.allocine.fr/r_120_x/commons/logos/Logos_p2c_160x128.jpg"
    for emission in emission_list:
        try: image = picture["%s" % emission[1]]
        except : image = ""
        addDir(emission[1], "http://www.allocine.fr%s" % emission[0], 1 , image )
end_of_directory( OK )