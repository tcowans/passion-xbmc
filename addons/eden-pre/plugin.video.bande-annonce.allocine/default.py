# -*- coding: utf-8 -*-

# script constants
__plugin__       = "Bandes-Annonces Allocine"
__addonID__      = "plugin.video.bande-annonce.allocine"
__author__       = "Ppic"
__url__          = "http://code.google.com/p/passion-xbmc/"

__useragent__    = "Mozilla/5.0 (Windows; U; Windows NT 5.1; fr; rv:1.9.0.1) Gecko/2008070208 Firefox/3.0.1"


import urllib
import re
import os
import time
import xbmcgui
import xbmcplugin
from traceback import print_exc


import xbmcaddon

__settings__ = xbmcaddon.Addon( __addonID__ )
AddonPath = __settings__.getAddonInfo( 'path' )

BASE_RESOURCE_PATH = os.path.join( AddonPath, "resources" )
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "lib" ) )
cache_dir = os.path.join ( xbmc.translatePath( __settings__.getAddonInfo( 'profile' ) ) , "cache" )
trailer_dir = __settings__.getSetting("trailer_path")
trailer_dir = xbmc.translatePath(trailer_dir)
dialog = xbmcgui.Dialog()
print "trailer dir: %s" % trailer_dir
DOWNLOADER = os.path.join( BASE_RESOURCE_PATH, "lib", "downloader.py" )

tempfile= os.path.join ( cache_dir , "data.html" )
if not os.path.isdir(cache_dir):
    os.makedirs(cache_dir)

from convert import set_entity_or_charref
from convert import translate_string

try: quality=( "ld", "md", "hd" )[ int( __settings__.getSetting("quality") ) ]
except:
    #__settings__.openSettings()
    quality=( "ld", "md", "hd" )[ int( __settings__.getSetting("quality") ) ]
print __settings__.getSetting("mon_cine")

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
        nbpage = 10
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
    #dp = xbmcgui.DialogProgress()
    #dp.create("Update Database")
    
    
    while pager <= nbpage and nbpage != "error" and pager <= [5,10,20,30,999][int(__settings__.getSetting("page_limit"))]:
        if not pager == 1:
            current_url= "%s?page=%s" % (url , pager)
            print "page %s: %s" % ( pager , current_url )
            page_data = get_html_source( current_url )
            
        try:   
            #print page_data
            match = re.search( '<a href="/video/emissions/(.*?)/episode/\?cmedia=(.*?)">\s+<img src="(.*?)" alt="" />\s+</a>\s+</div>\s+<div style="float:left; position:relative; width:320px; height:220px; padding:95px 0 0 35px; overflow:hidden;">\s+<h2 class="fs18" style="color:#FFFFFF;">(.*?)</h2>', page_data )
            
            if match:
                film = {}
                count = count+1
                film["type"] = match.group(1)
                film["poster"] = match.group(3)
                film["name"] = match.group(4)
                film["id_allo"] = match.group(2)
                film["id_media"] = match.group(2)
                if __settings__.getSetting("hdimage") == "true":
                    film["poster"] = film["poster"].replace( "c_120_160/b_1_x/o_play.png_5_se" , "r_760_x" ).replace("cx_120_96/b_1_x/o_play.png_5_se", "r_760_x" ).replace("c_120_120/b_1_x/o_play.png_5_se", "r_760_x" )
                    film["poster"] = film["poster"].replace("cx_120_113/o_overlayEmissions-P2C-120.png_1_c", "r_760_x" ).replace("cx_120_113/o_overlayEmissions-MerciQui-120.png_1_c", "r_760_x" ).replace("cx_120_113/o_overlayEmissions-LaMinute-120.png_1_c", "r_760_x" ).replace("cx_120_113/o_overlayEmissions-D2DVD-120.png_1_c", "r_760_x" ).replace("cx_120_113/o_overlayEmissions-TES-120.png_1_c", "r_760_x" ).replace("cx_120_113/o_overlayEmissions-FauxR-120.png_1_c", "r_760_x" )
                catalogue.append(film)
                try:
                    c_items = []
                    local_trailer = os.path.join( trailer_dir, "%s.flv" % translate_string(film["name"] ) )
                    script = DOWNLOADER
                    args = "%s&%s&%s" % ( urllib.quote_plus( "cmedia=%s" % film["id_media"] ), urllib.quote_plus( local_trailer ) , quality)
                    if not os.path.exists(local_trailer):c_items += [ ( "Télécharger", "XBMC.RunScript(%s,%s)" % ( script, args ) ) ]
                    else : c_items += [ ( "jouer en local", "xbmc.PlayMedia(%s)" % local_trailer) ]
                    addDir(film["name"], film["id_media"],5,film["poster"], c_items )
                except: 
                    print_exc()
                print "#######trouvé########trouvé############trouvé##########trouvé###########"
            MEDIA=re.compile( '<div class="mainzone">(.*?)<div class="spacer">', re.DOTALL ).findall(page_data)
            #save_data(page_data)
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
                try: ratio= int(100*float(count)/float(total_item))
                except: ratio=0
                
                match = re.search("<a href=\'/video/emissions.*?>",i)
                if match: film["type"] = "emission"

                if   film["type"] == "serie":      match = re.search( "<strong>(.*?)</strong>(.*?)\s+</a>", i )
                elif film["type"] == "interviews": match = re.search( "<span class=\'bold\'>\s+(.*?)\s+</span>\s+(.*?)<br />", i )
                elif film["type"] == "emission":   match = re.search("<span class=\'bold\'><strong>(.*?)</strong>(.*?)</span></a><br/>", i)
                else : match = re.search( "<strong>(.*?)</strong>", i )
                save_data(i)

                film["name"] = ""
                if match :
                    if film["type"] == "serie": film["name"] = match.group(1) + " " + match.group(2) #match.group(1).replace("</span>"," ")
                    elif film["type"] == "interviews": film["name"] = match.group(1) + match.group(2)
                    elif film["type"] == "emission": film["name"] = match.group(1) + match.group(2)
                    else : 
                        film["name"] = match.group(1)

                print "récupération info %s (%s/%s): %s" % ( film["type"] , count , total_item , film["name"] )
                #dp.update(ratio , "récupération info %s (%s/%s)" % ( film["type"], count , total_item ), film["name"])
#                 if dp.iscanceled() :
#                     dp.close()
#                     break
                match = re.search( "<a href='/video/player_gen_cmedia=(.*?)&c%s=(.*?).html'" % film["type"] , i )
                if match: 
                    film["id_allo"] = match.group(2)
                    film["id_media"] = match.group(1)
                    #print "############TEST###############" + "test id:%s %s" % (match.group(1) , match.group(2))
                else : 
                    match = re.search( "cmedia=(.*?)'" , i )
                    if match:
                        film["id_allo"] = film["id_media"] = match.group(1)
                    else: film["id_allo"] = film["id_media"] = ""
                        
                match = re.search( "<p>Date de sortie :\s+(.*?)</p>", i )
                if match: 
                    print "sortie: %s " % match.group(1).replace("/",".")
                    film["sortie"] = match.group(1).replace("/",".")
                try: film["poster"] = re.findall( "<img src='(.*?)'", i )[0]
                except: film["poster"] = ""
                print "hd image: %s" % __settings__.getSetting("hdimage")
                if __settings__.getSetting("hdimage") == "true":
                    film["poster"] = film["poster"].replace( "c_120_160/b_1_x/o_play.png_5_se" , "r_760_x" ).replace("cx_120_96/b_1_x/o_play.png_5_se", "r_760_x" ).replace("c_120_120/b_1_x/o_play.png_5_se", "r_760_x" )
                    film["poster"] = film["poster"].replace("cx_120_113/o_overlayEmissions-P2C-120.png_1_c", "r_760_x" ).replace("cx_120_113/o_overlayEmissions-MerciQui-120.png_1_c", "r_760_x" ).replace("cx_120_113/o_overlayEmissions-LaMinute-120.png_1_c", "r_760_x" ).replace("cx_120_113/o_overlayEmissions-D2DVD-120.png_1_c", "r_760_x" ).replace("cx_120_113/o_overlayEmissions-TES-120.png_1_c", "r_760_x" ).replace("cx_120_113/o_overlayEmissions-FauxR-120.png_1_c", "r_760_x" )
                catalogue.append(film)
                if film["type"] == "film":
                    if __settings__.getSetting("date_sortie") == "true" : ajout_sortie = "[CR]" +  film.get( "sortie", "" )
                    else : ajout_sortie = ""
                    addDir(film["name"] + ajout_sortie ,"%s##%s" % (film["poster"] , film["id_allo"]),2,film["poster"], sortie=film.get( "sortie", "" ))
                    xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_TITLE)
                    xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_DATE)
                    #xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_NONE)
                else :
                    #print "image:%s " % film["poster"]
                    c_items = []
                    local_trailer = os.path.join( trailer_dir, "%s.flv" % translate_string(film["name"] ) )
                    script = DOWNLOADER
                    args = "%s&%s&%s" % ( urllib.quote_plus( "cmedia=%s" % film["id_media"] ), urllib.quote_plus( local_trailer ) , quality)
                    if not os.path.exists(local_trailer):c_items += [ ( "Télécharger", "XBMC.RunScript(%s,%s)" % ( script, args ) ) ]
                    else : c_items += [ ( "jouer en local", "xbmc.PlayMedia(%s)" % local_trailer) ]
                    addDir(film["name"], film["id_media"],5,film["poster"], c_items )
        
                
                            
        except:
            print "probleme de récupération de la liste de film"
            print_exc()
            
        pager = pager + 1
    #dp.close()
    print "total movies = %s" % count
    return catalogue

def get_film_info(id_allo , BA = False , all_BA = False , emissions_liees = False , interviews = False):
    film = {}
    film_url = "http://www.allocine.fr/film/fichefilm_gen_cfilm=%s.html" % id_allo
    film_data = get_html_source( film_url )
    #save_data(film_data) #DEBUG
    
    try: media_list = re.findall( '<a class=".+" href="/video/player_gen_cmedia=(.*?)&cfilm=.*.html">', film_data )
    except:
        print_exc()
        media_list = ""
    match = re.search(r'<a class="fs11 underline" href="(.*)"><img class="ico icoticka" alt=" " width="0" height="0" src="http://images.allocine.fr/commons/empty.gif"/><span>Toutes les vid\xc3\xa9os</span></a>', film_data, re.IGNORECASE)
    if match: url_all_video = match.group(1)
    else: url_all_video = ""
#    print "url_video: %s" % url_all_video #DEBUG

    if BA:
        BA_list = []
        if media_list:
            for id_media in media_list: BA_list.append(get_media_link(id_media))
        film["Bande-annonces"] = BA_list
        return film
    
    if emissions_liees or all_BA or interviews:
#        print "test liens toutes vidéos" #DEBUG
        if not url_all_video == "":
#            print "url toutes vidéos trouvé" #DEBUG
            video_data = get_html_source( "http://www.allocine.fr" + url_all_video )
#            save_data(video_data) #DEBUG
    
    if interviews:
#        print "test interviews liées" #DEBUG
        match = re.search(r"<h2>\s+(\d+) Interviews li\xc3\xa9es \xc3\xa0 ce film\s+</h2>(.*?)<h2>Autres bandes-annonces</h2>", video_data, re.DOTALL | re.IGNORECASE)
        if match: 
            nbre_interviews = match.group(1)
            interviews_data = match.group(2)
        else:
            dialog.ok("Interviews Allociné" , "aucune interview liée")
            return False
            nbre_interviews = ""
            interviews_data = ""
#        save_data(interviews_data) #DEBUG
#        print "nombre interviews liées: %s" % nbre_interviews #DEBUG
        result = re.findall(r'(?i)<a href=\'/film/fichefilm-\d+/interviews/\?cmedia=(\d+)\'>\s+<img src=\'(.*?)\' alt="Photo : (.*?)"  title="Photo : (.*?)" />\s+</a>', interviews_data)
#        print "nombre emissions liées trouvées: %s" % len(result) #DEBUG
        for i in result: 
#            print i[3] , i[1]#DEBUG
            #ba = get_media_link(i[0])
            print i[2]
            if __settings__.getSetting("hdimage") == "true": image = i[1].replace( "cx_120_96/b_1_x/o_play.png_5_se" , "r_760_x" )
            else: image = i[1]
            print image
            c_items = []
            local_trailer = os.path.join( trailer_dir, "%s.flv" % translate_string( i[3] ) )
            script = DOWNLOADER
            args = "%s&%s&%s" % ( urllib.quote_plus( "cmedia=%s" % i[0] ), urllib.quote_plus( local_trailer ) , quality)
            if not os.path.exists(local_trailer):c_items += [ ( "Télécharger", "XBMC.RunScript(%s,%s)" % ( script, args ) ) ]
            else : c_items += [ ( "jouer en local", "xbmc.PlayMedia(%s)" % local_trailer) ]
            addDir(i[3], i[0],5,image, c_items )
            
    if emissions_liees:
#        print "test emisions liées" #DEBUG
        match = re.search(r"<h2>(\d+) \xc3\xa9missions li\xc3\xa9es</h2>(.*?)<h2>Autres bandes-annonces</h2>", video_data, re.DOTALL | re.IGNORECASE)
        if match: 
            nbre_emissions = match.group(1)
            emision_data = match.group(2)
        else:
            dialog.ok("Emissions Allociné" , "aucune emission liée")
            return False
            nbre_emissions = ""
            emision_data = ""
#        save_data(emision_data) #DEBUG
#        print "nombre emissions liées: %s" % nbre_emissions #DEBUG
        result = re.findall(r'(?i)<a href=\'/video/emissions/(.*?)/episode/\?cmedia=(\d+)\'>\s+<img src=\'(.*?)\' alt="Photo : (.*?)"  title="Photo : (.*?)" />', emision_data)
#        print "nombre emissions liées trouvées: %s" % len(result) #DEBUG
        for i in result: 
#            print i[4] #DEBUG
            #ba = get_media_link(i[0])
            print i[2]
            if __settings__.getSetting("hdimage") == "true": image = i[2].replace("cx_120_110/o_overlayEmissions-P2C-120.png_1_c", "r_760_x" ).replace("cx_120_110/o_overlayEmissions-MerciQui-120.png_1_c", "r_760_x" ).replace("cx_120_110/o_overlayEmissions-LaMinute-120.png_1_c", "r_760_x" ).replace("cx_120_110/o_overlayEmissions-D2DVD-120.png_1_c", "r_760_x" ).replace("cx_120_110/o_overlayEmissions-TES-120.png_1_c", "r_760_x" ).replace("cx_120_110/o_overlayEmissions-FauxR-120.png_1_c", "r_760_x" )
            else: image = i[2]
            print image
            c_items = []
            local_trailer = os.path.join( trailer_dir, "%s.flv" % translate_string( i[4] ) )
            script = DOWNLOADER
            args = "%s&%s&%s" % ( urllib.quote_plus( "cmedia=%s" % i[0] ), urllib.quote_plus( local_trailer ) , quality)
            if not os.path.exists(local_trailer):c_items += [ ( "Télécharger", "XBMC.RunScript(%s,%s)" % ( script, args ) ) ]
            else : c_items += [ ( "jouer en local", "xbmc.PlayMedia(%s)" % local_trailer) ]
            addDir(i[4], i[1],5,image, c_items )
        
    if all_BA:
#        print "test all ba" #DEBUG     
        if url_all_video:            
            match = re.search(r"(\d+) bandes-annonces", video_data)
            if match: nb_ba = match.group(1)
            else: nb_ba = ""
#            print "nombre BA: %s" % nb_ba #DEBUG
            
            match = re.search("-- CONSTRAINT RIGHT COLUMN -->(.*?)Autres bandes-annonces", video_data, re.DOTALL)
            if match: video_data = match.group(1)
            else: video_data = ""
            #save_data(video_data) #DEBUG
            #result = re.findall(r"(?i)<a href=\'/video/player_gen_cmedia=(.*?)&cfilm=(.*?).html\'>\s+", video_data) #DEBUG
            result = re.findall(r"""<a href=\'/video/player_gen_cmedia=(.*?)&cfilm=(.*?).html\'>\s+<img src=\'(.*?)\' alt="Photo : (.*?)"  title="Photo : (.*?)" />\s+</a>""", video_data)
#            print "liste BA: %s ba trouvées " %  len(result)  #DEBUG
#            print "#####################liste des BA##########################" #DEBUG
            for i in result: 
#                print i[4] #DEBUG
                if __settings__.getSetting("hdimage") == "true": image = i[2].replace( "cx_120_96/b_1_x/o_play.png_5_se" , "r_760_x" )
                else: image = i[2]
                c_items = []
                local_trailer = os.path.join( trailer_dir, "%s.flv" % translate_string( i[4] ) )
                script = DOWNLOADER
                args = "%s&%s&%s" % ( urllib.quote_plus( "cmedia=%s" % i[0] ), urllib.quote_plus( local_trailer ) , quality)
                if not os.path.exists(local_trailer):c_items += [ ( "Télécharger", "XBMC.RunScript(%s,%s)" % ( script, args ) ) ]
                else : c_items += [ ( "jouer en local", "xbmc.PlayMedia(%s)" % local_trailer) ]
                addDir(i[4], i[0],5,image, c_items )
#            print "#####################liste des BA FIN######################" #DEBUG 
    return True
    

def get_media_link(id_media):
    media_url = "http://www.allocine.fr/skin/video/AcVisionData_xml.asp?media=%s" % id_media
    media_data = get_html_source( media_url )
    #save_data(media_data)
    media = {}
    
    match = re.search( '<AcVisionVideo(.*?)/>', media_data , re.DOTALL )
    if match: media_data = match.group(1)
    else : print "problème de récupération info média"
    
    match = re.search( 'title="(.*?)"', media_data )
    if match: media["name"] = set_entity_or_charref(match.group(1))
    else: media["name"] = ""
    print "récupération info média: %s" % media["name"]
    
    for video_quality in [ "ld" , "md" , "hd"]:
        match = re.search( '%s_path="(.*?)"' % video_quality , media_data )
        if match: media[video_quality] = match.group(1)
        else: media[video_quality] = ""
    print media    
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
        #save_data(unit)
        try:
             raw = re.compile( "De(.*?)\s+</p>", re.DOTALL ).search(unit)
             film["director"] = ""
             for i in re.findall( "title='(.*?)'", raw.group() ):
                film["director"] = film["director"] + " , " + i
             film["director"] = film["director"].strip(" ,")
             
        except: print_exc()
        try:
            raw = re.compile( "Avec(.*?)\s+</p>", re.DOTALL ).findall(unit)[0]
            film["cast"] = re.findall( "title='(.*?)'", raw )
        except: print_exc()
        
        match = re.search('class="titlebar"  -->\s+<p>\s+(.*?)\s+\((.*?)\)\s+- Date de sortie : <b>(.*?)</b>\s+</p>\s+<p>', unit )
        if match:
            film["sortie"]= match.group(3)
            film["genre"]= match.group(1)
            film["duree"]= match.group(2)
        else:
            film["sortie"]= ""
            film["genre"]= ""
            film["duree"]= ""

        
        match = re.search('<!-- /notationbar -->\s+<p>\s+(.*?)\s+</p>\s+<!-- !! Existing template -->', unit )
        if match: film["syno"] = match.group(1).strip(" ")
        else: film["syno"] = ""
            
        match = re.search('<a class=".+" href="/film/fichefilm_gen_cfilm=(.*?).html\">(.*?)</a></h2>', unit )
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
    DB_file= os.path.join( cache_dir , translate_string("%s.txt" % dbname) )
    try: save_data( get_film_list( url ) , DB_file )
    except:
        print "impossible de créer la base %s" % DB_file
        print_exc()
def load_DB(dbname):
    
    DB_file= os.path.join( cache_dir , translate_string("%s.txt" % dbname) )
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
    match = re.compile('<li class="clmmastertopic"><a href="/video/emissions/">(.*?)<li class="clmmastertopic"><a href="/video/series/">',re.DOTALL ).findall( data )
    if match: menu_emission = match[0]
    else: menu_emission = ""
    #print "menu emission" + menu_emission

    match = re.compile('<a href="(.*?)">(.*?)</a>',re.DOTALL ).findall( menu_emission )
    if match: emission_list = match
    else: emission_list = ""    
    return emission_list
 

def delete_cinema(cine_to_del):
    print cine_to_del
    cine_list = load_data( os.path.join(cache_dir , "cine.list"))
    print cine_list
    if cine_to_del in cine_list: 
        print "oui il y est !!!!!!!!!"
        print cine_to_del
        cine_list.remove(cine_to_del)
        print cine_list
    if cine_list == []: os.remove( os.path.join(cache_dir , "cine.list"))
    else: save_data( cine_list ,os.path.join(cache_dir , "cine.list"))
       

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

OK = True

if mode==None or url==None or len(url)<1: #menu principal
    addDir("A ne pas manquer","http://www.allocine.fr/video/bandes-annonces/plus/",1,"")
    addDir("films au cinema","http://www.allocine.fr/video/bandes-annonces/films-au-cinema/plus/",1,"")
    addDir("prochainement","http://www.allocine.fr/video/bandes-annonces/films-prochainement/plus/",1,"")
    addDir("séries Tv","http://www.allocine.fr/video/series/plus/",1,"")
    addDir("émissions","http://www.allocine.fr/video/",6,"")
    addDir("interviews","http://www.allocine.fr/video/interviews/plus",1,"")
    if __settings__.getSetting("mon_cine") == "true" :
        if os.path.exists(os.path.join(cache_dir , "cine.list")): 
            mes_cines = load_data(os.path.join(cache_dir , "cine.list"))
            for cine in mes_cines:
                c_items = []
                c_items += [ ( "Effacer ce cinéma", 'XBMC.RunPlugin(%s?mode=7&name=%s&url=%s)' % ( sys.argv[ 0 ], urllib.quote_plus( cine[1] ), urllib.quote_plus( cine[0] ), ) ) ]
                addDir( cine[1],"http://www.allocine.fr/seance/salle_gen_csalle=%s.html" % cine[0],4,"", c_items )                
        addDir("Ajouter Un Cinéma...","",3,"")

if mode == 1: # affichage des liste ba / series / emissions / interviews
    xbmcplugin.setPluginCategory(int(sys.argv[1]), name)
    if load_DB( name ) == "": create_DB( url , name)
    else: 
        data=load_DB( name )
        for film in data:
            if film["type"] == "film":
                if __settings__.getSetting("date_sortie") == "true" : ajout_sortie = "[CR]" +  film.get( "sortie", "" )
                else : ajout_sortie = ""
                addDir(film["name"] + ajout_sortie ,"%s##%s" % (film["poster"] , film["id_allo"]),2,film["poster"], sortie=film.get( "sortie", "" ))
                xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_TITLE)
                xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_DATE)
                #xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_NONE)
            else :
                #print "image:%s " % film["poster"]
                c_items = []
                local_trailer = os.path.join( trailer_dir, "%s.flv" % translate_string(film["name"] ) )
                script = DOWNLOADER
                args = "%s&%s&%s" % ( urllib.quote_plus( "cmedia=%s" % film["id_media"] ), urllib.quote_plus( local_trailer ) , quality)
                if not os.path.exists(local_trailer):c_items += [ ( "Télécharger", "XBMC.RunScript(%s,%s)" % ( script, args ) ) ]
                else : c_items += [ ( "jouer en local", "xbmc.PlayMedia(%s)" % local_trailer) ]
                addDir(film["name"], film["id_media"],5,film["poster"], c_items )

        
        

if mode == 2: #menu bande-annonce de film + liens contenus liées
#    print 'name : %s' % name #DEBUG
    poster = url.split("##")[0]
    url = url.split("##")[1]
    film = get_film_info(url, BA = True)
    for ba in film["Bande-annonces"]:
        #print ba
        # ajout d'un bouton dans le contextmenu pour télécharger / jouer le trailer
        c_items = []
        local_trailer = os.path.join( trailer_dir, "%s.flv" % translate_string(ba["name"] ) )
        script = DOWNLOADER
        args = "%s&%s" % ( urllib.quote_plus( ba["%s" % quality ] ), urllib.quote_plus( local_trailer ) )
        if not os.path.exists(local_trailer):c_items += [ ( "Télécharger", "XBMC.RunScript(%s,%s)" % ( script, args ) ) ]
        else : c_items += [ ( "jouer en local", "xbmc.PlayMedia(%s)" % local_trailer) ]
        addLink(ba["name"].split(" - ")[1],ba["%s" % quality ],poster , c_items )
    addDir("Voir toutes les bandes-annonce",  url ,8, poster )
    addDir("Voir les émissions liées",  url ,9, poster )
    addDir("Voir les interviews liées",  url ,10, poster )
    
    #########################################################
if mode == 3:
    search_cinema()
    OK= False
    
if mode == 4: # liste des films dans le cinema
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
        try : film_in_cine["sortie"] = int(film_in_cine["sortie"].split("/")[2])
        except : film_in_cine["sortie"] = 0
        print film_in_cine["sortie"]
        print "################################################################"
        save_data( film_in_cine , os.path.join ( cache_dir , "film-%s.txt" % film_in_cine["id_allo"]))
        try: addFilm(film_in_cine["name"],"%s##%s" % (film_in_cine["poster"] , film_in_cine["id_allo"]),2,film_in_cine["poster"],film_in_cine["genre"] ,film_in_cine["director"] ,film_in_cine["cast"] ,film_in_cine["syno"] ,film_in_cine["duree"] ,int(film_in_cine["sortie"]) )
        except : print_exc()


if mode == 5: #envoi de la video au lecteur et recherche de la video via l'idmedia
    
    ba = get_media_link( url )
    trailer = ba["%s" % quality ]
    while trailer == "":
        select = xbmcgui.Dialog().select("Média indisponible, choisir une autre qualité", [ "ld" , "md" , "hd"])
        if select == -1: break
        else: trailer = ba["%s" % [ "ld" , "md" , "hd"][select] ]
    print "name: %s" % name
    print "trailer: %s" % trailer
    playableVideoItem = xbmcgui.ListItem( name , path = trailer) 
    xbmc.Player().play(trailer, playableVideoItem, False)
    OK = False

if mode == 6: #liste des emissions et images associées
    emission_list = get_emission_list(url)
    print emission_list
    picture = {}
    picture["La Minute"] = "http://images.allocine.fr/r_720_x/commons/logos/Logos_minute_160x128.jpg"
    picture["Tueurs en S\xc3\xa9ries"] = "http://images.allocine.fr/r_720_x/commons/logos/Logos_tes_160x128.jpg"
    picture["Merci Qui?"] = "http://images.allocine.fr/r_720_x/commons/logos/Logos_merciqui_160x128.jpg"
    picture["Direct 2 DVD"] = "http://images.allocine.fr/r_720_x/commons/logos/Logos_D2D_160x128.jpg"
    picture["Faux Raccord"] = "http://images.allocine.fr/r_720_x/commons/logos/Logos_FauxR_160x128.jpg"
    picture["Plein 2 Cin\xc3\xa9"] = "http://images.allocine.fr/r_720_x/commons/logos/Logos_p2c_160x128.jpg"
    for emission in emission_list:
        try: 
            if __settings__.getSetting("hdimage") == "true":
                image = picture["%s" % emission[1]].replace("r_760_x","")
            else: image = picture["%s" % emission[1]]
            
        except : 
            print_exc()
            image = ""
        addDir(emission[1], "http://www.allocine.fr%s" % emission[0], 1 , image )
        

if mode == 7: #suppression cinema perso
    delete_cinema( (url, name ))
    xbmc.executebuiltin("Container.Refresh")
    OK=False
    
if mode == 8: #toutes les ba du film
    OK = get_film_info(url, all_BA = True)

if mode == 9: #toutes les vidéo liées du film
    OK = get_film_info(url, emissions_liees = True)

if mode == 10: #toutes les vidéo liées du film
    OK = get_film_info(url, interviews = True)
        
end_of_directory( OK )
