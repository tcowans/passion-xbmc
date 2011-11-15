# -*- coding: cp1252 -*-
"""
plugin video Canal+ pour XBMC 


19-11-2008 Version 1.0 par Alexsolex
    - Creation
    
13-05-2009 Version Pre2.0 par Temhil 
    - Adpatation du plugin suite a des modifications sur le site de Canal+
    - Ajout du menu option
    - Ajout du choix de visionnage (HD ou SD) des videos (via les options)
    - Support multilangue
    - Ajout description video via menu info
    - Les images sont desormais automatiquement telechargees par le plugin lui meme
    - Adaptation de la fonction de recherche au modifications du site
    
23-10-2009 Version Pre2.0b by Temhil
    - Replaced separator in the URL "&" by "#" (broken due to change made in XBMC)
    - Added plugin variable for SVN repo installer infos
    
23-10-2009 Version 2.0 by Temhil
    - Replaced XML parser BeautifulSoup by ElementTree (needed because some XML were not correctly formed)
    - Added support of new video stream URL, now http and rtmp urls are both supported
    
09-06-2010 Version 2.1 by Frost
    - Modified the code for Dharma compatibility
    
11-10-2010 Version 2.2 by Temhil
    - Moved cache and download directories to user data
    - some cleanup
    
05-12-2010 Version 3.0 par Temhil
    - Reorganisation du code du code
     (on recupere l'URL de la video lors d'une 2eme etape invisble pour l'utilsateur)
    - Suppression des threads (plus necessaire desormais)
    - Amelioration du chargement des listes de videos 
    - Affiche les couleurs correspondant aux rubriques (provenant de www.color-hex.com)
"""

REMOTE_DBG       = False # For remote debugging with PyDev (Eclipse)

__script__       = "Unknown"
__plugin__       = "Canal Plus"
__addonID__      = "plugin.video.canal.plus"
__author__       = "Alexsolex / Temhil"
__url__          = "http://passion-xbmc.org/index.php"
__svn_url__      = "http://passion-xbmc.googlecode.com/svn/trunk/addons/plugin.video.canal.plus/"
__credits__      = "Team XBMC Passion"
__platform__     = "xbmc media center"
__date__         = "12-05-2010"
__version__      = "3.0"
__svn_revision__ = 0


import sys
import os, os.path
import urllib
from traceback import print_exc

# xbmc modules
import xbmc
import xbmcplugin
import xbmcgui
import xbmcaddon


 
__addon__    = xbmcaddon.Addon( __addonID__ )
__settings__ = __addon__
__language__ = __addon__.getLocalizedString
__addonDir__ = __settings__.getAddonInfo( "path" )



# Remote debugger using Eclipse and Pydev
if REMOTE_DBG:
    # Note pydevd module need to be copied in XBMC\system\python\Lib\pysrc
    try:
        import pysrc.pydevd as pydevd
        pydevd.settrace('localhost', stdoutToServer=True, stderrToServer=True)
    except ImportError:
        sys.stderr.write("Error: " +
            "You must add org.python.pydev.debug.pysrc to XBMC\system\python\Lib\pysrc")
        sys.exit(1)

# Modules custom
if sys.modules.has_key("cplusplus"):
    del sys.modules['cplusplus']  
try:
    import resources.libs.cplusplus as cpp
except:
    print_exc()

ROOTDIR            = os.getcwd()
BASE_RESOURCE_PATH = os.path.join( ROOTDIR, "resources" )
ADDON_DATA         = xbmc.translatePath( "special://profile/addon_data/%s/" % __addonID__ )
DOWNLOADDIR        = os.path.join( ADDON_DATA, "downloads")
CACHEDIR           = os.path.join( ADDON_DATA, "cache")
COLOR_IMG_URL      = "http://www.color-hex.com/colorimg.php?color="
#BASE_THUMBS_PATH = os.path.join( xbmc.translatePath( "special://profile/" ), "Thumbnails", "Video" )

# List of directories to check at startup
dirCheckList   = ( CACHEDIR, DOWNLOADDIR, ) #Tuple - Singleton (Note Extra ,)




def verifrep( folder ):
    """
        Source MyCine (thanks!)
        Check a folder exists and make it if necessary
    """
    try:
        #print("verifrep check if directory: " + folder + " exists")
        if not os.path.exists( folder ):
            print( "verifrep Impossible to find the directory - trying to create the directory: " + folder )
            os.makedirs( folder )
    except Exception, e:
        print( "Exception while creating folder " + folder )
        print( str( e ) )

class CanalPlusMosaicPlugin:
    """
    main plugin class
    """
    # define param key names
    PARAM_LISTTYPE        = 'listype'
    PARAM_LIST_THEME      = "listethemes"
    PARAM_LIST_SUBTHEME   = "listesubthemes"
    PARAM_LIST_VIDEOS     = "listevideos"
    PARAM_SEARCH          = "search"
    PARAM_THEME_ID        = "theme_id"
    PARAM_SUBTHEME_ID     = "subtheme_id"
    PARAM_VIDEO_ID        = "video_id"
    PARAM_REFERER         = "referer"
    PARAM_DOWNLOAD_VIDEO  = "dlvideo"
    PARAM_PLAY_VIDEO      = "playvideo"
    PARAM_SHOW_VIDEO_INFO = "showvideoinfos"
    PARAM_SHOW_PICTURE    = "showpicture"
    
    pluginhandle = int(sys.argv[1])

   
    PARAM_TYPE        = 'type'
    PARAM_URL         = 'url'

    def __init__( self, *args, **kwargs ):
        print "================================"
        print "Canal + - DEMARRAGE"
        self.parameters = self._parse_params()
        cpp.CACHEDIR = CACHEDIR
        
        # Check if directories in user data exist
        for i in range( len( dirCheckList ) ):
            verifrep( dirCheckList[i] ) 
            
        # Read settings
        #self.useCacheThumb = __settings__.getSetting('use_cache_thumb') == 'true'
            
        self.select()
        
        
    def select( self ):
        try:
            if len(self.parameters) < 1:
                self.show_themes()
            
            elif self.PARAM_LIST_THEME in self.parameters.keys():
                #on liste les themes
                self.show_themes()
        
            elif self.PARAM_LIST_SUBTHEME in self.parameters.keys():
                #on liste les sous-themes
                self.show_subthemes(self.parameters[self.PARAM_LIST_SUBTHEME],self.parameters[self.PARAM_REFERER])

            elif self.PARAM_LIST_VIDEOS in self.parameters.keys():
                #on liste les videos
                theme_id,subtheme_id = self.parameters[self.PARAM_LIST_VIDEOS].split("#")
                self.show_videos(theme_id,subtheme_id,self.parameters[self.PARAM_REFERER])
                   
            elif self.PARAM_PLAY_VIDEO in self.parameters.keys():
                # On lance la video
                video_id = int(self.parameters[self.PARAM_VIDEO_ID])
                url_video_LQ, url_video_HQ = self.get_video_urls(video_id)
                if int(__settings__.getSetting('video_quality') ) == 1: # Basse qualite
                    url=url_video_LQ
                else:
                    url=url_video_HQ
                
                # Play  video
                item = xbmcgui.ListItem(path=url)

                print "Canal+: Lecture de la video: %s"%url
                xbmcplugin.setResolvedUrl(handle=int(sys.argv[1]), succeeded=True, listitem=item)
                self._end_of_directory( True )

            elif self.PARAM_SHOW_VIDEO_INFO in self.parameters.keys():
                # Non utilise
                # Montre les infos de la video
                self.show_video_infos(self.parameters[self.PARAM_SHOW_VIDEO_INFO])
            
                
            elif self.PARAM_DOWNLOAD_VIDEO in self.parameters.keys():
                # Non utilise
                xbmc.executebuiltin('XBMC.RunScript(%s,%s,%s)'%(os.path.join(os.getcwd(), "resources", "libs","FLVdownload.py"),
                                                                self.parameters[self.PARAM_DOWNLOAD_VIDEO],
                                                                os.path.join(DOWNLOADDIR,xbmc.makeLegalFilename(os.path.basename(self.parameters[self.PARAM_DOWNLOAD_VIDEO])))
                                                                ))
                #    #télécharge la vidéo selon l'url fournie
                #    pDialog = xbmcgui.DialogProgress()
                #    ret = pDialog.create('CanalPlus', 'Démarrage du téléchargement ...')
                #    #téléchargement par Thread : FONCTIONNE MAIS TRES MAL : pas convaincant
                #    goDL = cpp.DL_video(parameters["dlvideo"],
                #                        #xbmc.makeLegalFilename(os.path.join(DOWNLOADDIR,os.path.basename(parameters["dlvideo"]))),
                #                        os.path.join(DOWNLOADDIR,xbmc.makeLegalFilename(os.path.basename(parameters["dlvideo"]))),
                #                        pDialog.update,pDialog)
                #    pDialog.close()
                #    if goDL==1:
                #        xbmc.executebuiltin("XBMC.Notification(%s,%s)"%("Telechargement termine !",""))
                #    elif goDL == 0:
                #        xbmc.executebuiltin("XBMC.Notification(%s,%s)"%("Fichier existant !","Telechargement annule."))
                #    elif goDL == -1:
                #        xbmc.executebuiltin("XBMC.Notification(%s,%s)"%("Telechargement annule par l'utilisateur.",""))

                                                                
            elif self.PARAM_SEARCH in self.parameters.keys():
                # Lance une recherche et affiche les resultat des videos trouvees
                self.show_search(self.parameters[self.PARAM_THEME_ID],self.parameters[self.PARAM_SUBTHEME_ID])

            elif self.PARAM_SHOW_PICTURE in self.parameters.keys():
                # Non utilise
                # ne fait rien
                print os.path.join(CACHEDIR,self.parameters[self.PARAM_SHOW_PICTURE])

            else:
                print "Error: Parametres du plugin inconnus "
                self._end_of_directory( True )
        except:
            print_exc()
            self._end_of_directory( False )


    def _parse_params( self ):
        """
        Parses Plugin parameters and returns it as a dictionary
        """
        paramDic={}
        # Parameters are on the 3rd arg passed to the script
        paramStr=sys.argv[2]
        print paramStr
        if len(paramStr)>1:
            paramStr = paramStr.replace('?','')
            
            # Ignore last char if it is a '/'
            if (paramStr[len(paramStr)-1]=='/'):
                paramStr=paramStr[0:len(paramStr)-2]
                
            # Processing each parameter splited on  '&'   
            for param in paramStr.split("&"):
                try:
                    # Spliting couple key/value
                    key,value=param.split("=")
                except:
                    key=param
                    value=""
                    
                key = urllib.unquote_plus(key)
                value = urllib.unquote_plus(value)
                
                # Filling dictionnary
                paramDic[key]=value
        print paramDic
        return paramDic        


    def _create_param_url(self, paramsDic, quote_plus=False):
        """
        Create an plugin URL based on the key/value passed in a dictionary
        """
        url = sys.argv[ 0 ]
        sep = '?'
        print paramsDic
        try:
            for param in paramsDic:
                #TODO: solve error on name with non ascii char (generate exception)
                if quote_plus:
                    url = url + sep + urllib.quote_plus( param ) + '=' + urllib.quote_plus( paramsDic[param] )
                else:
                    url = url + sep + param + '=' + paramsDic[param]
                    
                sep = '&'
        except:
            url = None
            print_exc()
        return url


    def _addLink( self, name, name2="", url="", iconimage="DefaultVideo.png", itemInfoType="Video", itemInfoLabels=None, c_items=None, totalItems=0 ):
        ok=True
        print iconimage
        lstItem=xbmcgui.ListItem( label=name, label2=name2, iconImage=iconimage, thumbnailImage=iconimage )
        if c_items : 
            lstItem.addContextMenuItems( c_items, replaceItems=True )
            
        if itemInfoLabels:
            iLabels = itemInfoLabels
        else:
            iLabels = { "Title": name }
            
        lstItem.setInfo( type=itemInfoType, infoLabels=iLabels )
        lstItem.setProperty('IsPlayable', 'true')
        ok=xbmcplugin.addDirectoryItem( handle=int(sys.argv[1]), url=url, listitem=lstItem, totalItems=totalItems )
        return ok

        
    def _addDir( self, name, name2="", url="", iconimage="DefaultFolder.png", itemInfoType="Video", itemInfoLabels=None, c_items=None, totalItems=0 ):
        #u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        ok=True
        lstItem=xbmcgui.ListItem( label=name, label2=name2, iconImage=iconimage, thumbnailImage=iconimage )
        
        if c_items : 
            lstItem.addContextMenuItems( c_items, replaceItems=True )
            
        if itemInfoLabels:
            iLabels = itemInfoLabels
        else:
            iLabels = { "Title": name }
            
        lstItem.setInfo( type=itemInfoType, infoLabels=iLabels )
        ok=xbmcplugin.addDirectoryItem( handle=int( sys.argv[1] ), url=url, listitem=lstItem, isFolder=True, totalItems=totalItems )
        
        return ok

        
    
    def _end_of_directory( self, OK, update=False ):
        xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=OK, updateListing=update )#, cacheToDisc=True )#updateListing = True,

    def _add_sort_methods( self, OK ):
        if ( OK ):
            try:
                xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_DATE )
                xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_VIDEO_TITLE )
                #xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE )
                xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_GENRE )
                #xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_VIDEO_RUNTIME )
                #xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_STUDIO )
            except:
                print_exc()
        self._end_of_directory( OK )
    
    def _coloring( self, text , color , colorword ):
        if color == "red": color="FFFF0000"
        if color == "green": color="ff00FF00"
        if color == "yellow": color="ffFFFF00"
        colored_text = text.replace( colorword , "[COLOR=%s]%s[/COLOR]" % ( color , colorword ) )
        return colored_text


    def show_search(self, theme_id,subtheme_id):
        """
        Display virtual keyboard and start a search
        """
        kb = xbmc.Keyboard("", __language__( 30203 ), False) #Recherche sur Canal Plus Videos
        kb.doModal()
        if kb.isConfirmed():
            motcle = kb.getText()
            if ( len(motcle) > 2): # Taille mini pour une recherche
                self.show_videos(theme_id=theme_id,subtheme_id=subtheme_id,referer="Resultats pour '%s'"%motcle,keyword=motcle)
            else:
                dialogError = xbmcgui.Dialog()
                ok = dialogError.ok( __language__( 30204 ), __language__( 30205 ), __language__( 30206 ) )


    def get_video_urls(self, video_id):
        """
        Retrieve  video URL
        """
        infos = cpp.get_info(video_id)
        return infos["video.low"], infos["video.hi"]


    def show_themes(self):
        """
        rempli la liste avec la liste des thèmes
        un lien va contenir :
            la commande 'listesubthemes'
            le parametre 'themeid'
        """
        ok = True
        i= 0
        
        # Recuperation de la liste des themes
        pDialog = xbmcgui.DialogProgress()
        ret = pDialog.create( 'XBMC', __language__ ( 30200 ) )
        pDialog.update(0, __language__ ( 30202 ) )
        themes=cpp.get_themes()

        # Recherche
        #url = sys.argv[0]+"?search=&theme_id=%s&subtheme_id=%s&referer=%s"%("Rechercher dans toutes les catégories :",
        #                                                                    "",
        #                                                                    "")
        paramsAddonsSearch = {}
        paramsAddonsSearch[self.PARAM_SEARCH]      = ""
        paramsAddonsSearch[self.PARAM_THEME_ID]    = ""
        paramsAddonsSearch[self.PARAM_SUBTHEME_ID] = ""
        paramsAddonsSearch[self.PARAM_REFERER]     = "Rechercher dans toutes les catégories :"
        url = self._create_param_url( paramsAddonsSearch )
        self._addDir( __language__ ( 30001 ), url )
        
        for theme_id, theme_titre, theme_color in themes:
            #A ce jour les ID inferieurs à 10000 sont vides
            #De plus les ID au dessus de 10000 sont redondants avec ceux en dessous
            #if int(theme_id) > 10000: 
            if int(theme_id) > 0: 
                paramsAddons = {}
                paramsAddons[self.PARAM_LIST_SUBTHEME]  = str(theme_id)
                paramsAddons[self.PARAM_REFERER]        = theme_titre
                url = self._create_param_url( paramsAddons )
                print url
                #url = sys.argv[0]+"?listesubthemes=%s&referer=%s"%(theme_id,theme_titre)

                thumb = COLOR_IMG_URL + theme_color
#                #  Get cached thumbnail instead of redownload it when possible
#                img_url = COLOR_IMG_URL + theme_color
#                print self.useCacheThumb
#                if self.useCacheThumb == True:
#                    thumbnailImage = xbmc.getCacheThumbName( img_url )
#                    thumbnailpath = os.path.join( BASE_THUMBS_PATH, thumbnailImage[ 0 ], thumbnailImage )
#                    if os.path.exists(thumbnailpath):
#                        thumb=thumbnailpath
#                    else:
#                        thumb=img_url
#                else:
#                    thumb=img_url
#                    
#                item=xbmcgui.ListItem(label=theme_titre,
#                                      iconImage=thumb,
#                                      thumbnailImage=thumb)
#                
#                
#                
#                ok = ok and xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),
#                                                        url=url,
#                                                        listitem=item,
#                                                        isFolder=True,
#                                                        totalItems=len(themes))
                self._addDir( name=theme_titre, url=url, iconimage=thumb, totalItems=len(themes) )
                i=i+1
                pDialog.update(int(99*float(i)/(len(themes))), __language__ ( 30202 ) )
            else:
                pass
        xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_NONE)
        xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category= __language__ ( 30002 )) # Catégories
        self._end_of_directory( True )
        return ok
    
    
    def show_subthemes(self, theme_id,referer):
        """
        rempli la liste avec la liste des sous-thèmes pour le theme_id fourni
        un lien va contenir :
            la commande 'listevideos'
            les parametres 'themeid' et 'subthemeid'
        """
        ok = True
        i=0
        
        # Recuperation liste de sous-themes
        pDialog = xbmcgui.DialogProgress()
        ret = pDialog.create( 'XBMC', __language__ ( 30200 ) )
        pDialog.update(0, __language__ ( 30202 ) )
        subthemes=cpp.get_subthemes(theme_id)
        # Recherche
        #url = sys.argv[0]+"?search=&theme_id=%s&subtheme_id=%s&referer=%s"%("Rechercher dans %s :"%referer,
        #                                                                    theme_id,
        #                                                                    "")
        paramsAddonsSearch = {}
        paramsAddonsSearch[self.PARAM_SEARCH]      = ""
        paramsAddonsSearch[self.PARAM_THEME_ID]    = str(theme_id)
        paramsAddonsSearch[self.PARAM_SUBTHEME_ID] = ""
        paramsAddonsSearch[self.PARAM_REFERER]     = "Rechercher dans %s :"%referer
        url = self._create_param_url( paramsAddonsSearch )
        self._addDir( __language__ ( 30001 ), url )
    
        for subtheme_id, subtheme_titre in subthemes:
            #url = sys.argv[0]+"?listevideos=%s#%s&referer=%s"%(theme_id,subtheme_id,referer+">"+subtheme_titre)
            paramsAddons = {}
            paramsAddons[self.PARAM_LIST_VIDEOS]  = "%s#%s"%(theme_id,subtheme_id)
            paramsAddons[self.PARAM_REFERER]      = referer+">"+subtheme_titre
            url = self._create_param_url( paramsAddons )

            #item=xbmcgui.ListItem(label=subtheme_titre)
            
            
            #ok = ok and xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),
            #                                        url=url,
            #                                        listitem=item,
            #                                        isFolder=True,
            #                                        totalItems=len(subthemes))
            
            self._addDir( name=subtheme_titre, url=url, totalItems=len(subthemes) )
            i=i+1
            pDialog.update(int(99*float(i)/(len(subthemes))), __language__ ( 30202 ) )

        xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_NONE)
        xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category=referer )
        self._end_of_directory( True )
        return ok


    def show_videos(self, theme_id,subtheme_id,referer,keyword=""):
        """
        rempli la liste avec la liste des videos
        un lien va contenir :
            la commande 'showvideoinfo'
            le paramètre 'videoID'
        """
        ok = True
        cpt=0
        #i=0
        
        # Recuperation liste de videos
        pDialog = xbmcgui.DialogProgress()
        ret = pDialog.create( 'XBMC', __language__ ( 30200 ) )
        pDialog.update(0, __language__ ( 30201 ) )
        
        videos = cpp.get_videos( subtheme_id = subtheme_id, keyword=keyword )

        # Recherche
        #url = sys.argv[0]+"?search=&theme_id=%s&subtheme_id=%s&referer=%s"%("Rechercher dans %s"%referer,
        #                                                                    theme_id,
        #                                                                    subtheme_id)
        paramsAddonsSearch = {}
        paramsAddonsSearch[self.PARAM_SEARCH]      = ""
        paramsAddonsSearch[self.PARAM_THEME_ID]    = str(theme_id)
        paramsAddonsSearch[self.PARAM_SUBTHEME_ID] = str(subtheme_id)
        paramsAddonsSearch[self.PARAM_REFERER]     = "Rechercher dans %s"%referer
        url = self._create_param_url( paramsAddonsSearch )
        self._addDir( __language__ ( 30001 ), url )
        
        for video in videos:
            try:
 
                paramsAddons = {}
                paramsAddons[self.PARAM_PLAY_VIDEO]  = "true"
                paramsAddons[self.PARAM_VIDEO_ID]    = str(video["videoID"])
                url = self._create_param_url( paramsAddons )
                thumb=video['image.url']

#                #  Get cached thumbnail instead of redownload it when possible
#                if self.useCacheThumb == True:
#                    #thumbnailImage = xbmc.getCacheThumbName( os.path.basename(video['image.url']) )
#                    print video['image.url']
#                    print sys.argv[ 0 ] + sys.argv[ 2 ]
#                    thumbnailImage = xbmc.getCacheThumbName( video['image.url'] )
#                    print thumbnailImage
#                    thumbnailpath = os.path.join( BASE_THUMBS_PATH, thumbnailImage[ 0 ], thumbnailImage )
#                    print thumbnailpath
#                    
#                    if os.path.exists(thumbnailpath):
#                        thumb=thumbnailpath
#                    else:
#                        thumb=video['image.url']
#                else:
#                    thumb=video['image.url']

#                item=xbmcgui.ListItem(label=video["title"],label2=video["publication_date"],
#                                      iconImage=thumb,
#                                      thumbnailImage=thumb)
        
                #menu contextuel
#                label  = __language__( 30100 ) # Enregistrer (Haute Qualitée)
#                action = 'XBMC.RunScript(%s,%s,%s)'%(os.path.join(os.getcwd(), "resources", "libs", "FLVdownload.py"),
#                                                     infos["video.hi"],
#                                                     os.path.join(DOWNLOADDIR,xbmc.makeLegalFilename(os.path.basename(infos["video.hi"])))
#                                                     )
#                item.addContextMenuItems([ (
#                    __language__( 30100 ),
#                    'XBMC.RunScript(%s,%s,%s)'%(os.path.join(os.getcwd(), "resources", "libs","FLVdownload.py"),
#                                                infos["video.hi"],
#                                                os.path.join(DOWNLOADDIR,xbmc.makeLegalFilename(os.path.basename(infos["video.hi"])))
#                                                ),
#                                            ),(
#                    __language__( 30101 ),
#                    'XBMC.RunScript(%s,%s,%s)'%(os.path.join(os.getcwd(), "resources", "libs","FLVdownload.py"),
#                                                     infos["video.low"],
#                                                     os.path.join(DOWNLOADDIR,xbmc.makeLegalFilename(os.path.basename(infos["video.hi"])))
#                                                     ),
#                                            )
#                    ])
                #infos sur la video
#                item.setInfo( type="Video",
#                              infoLabels={ "Title": video["title"] + " " + video["publication_date"],
#                                           "Rating":video["note"],
#                                           "Date": video["publication_date"],
#                                           "Plot": video["description"]})
#                item.setProperty('IsPlayable', 'true')
#
#                ok = ok and xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),
#                                                        url=url,
#                                                        listitem=item,
#                                                        isFolder=False)
#                
                infoLabels={ "Title": video["title"] + " " + video["publication_date"],
                             "Rating":video["note"],
                             "Date": video["publication_date"],
                             "Plot": video["description"] }

                
                self._addLink( name=video["title"], url=url, iconimage=thumb, itemInfoLabels=infoLabels )
                cpt=cpt+1
                pDialog.update(int(99*float(cpt)/(len(videos))), __language__ ( 30202 ) )
            except:
                print "cplusplus - show_videos: error while retrieving videos list and info"
                print_exc()
            
        pDialog.close()
        xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_NONE)
        xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category=referer )
        xbmcplugin.setContent(int(sys.argv[1]), 'movies')
        self._end_of_directory( True )
        return ok



                                                
#######################################################################################################################    
# BEGIN !
#######################################################################################################################

if ( __name__ == "__main__" ):
    try:
        CanalPlusMosaicPlugin()
    except:
        print_exc()
