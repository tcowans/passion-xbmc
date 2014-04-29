# -*- coding: cp1252 -*-
"""
plugin video Canal+ pour XBMC

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
__date__         = "29-04-2014"
__version__      = "3.4.1"
__svn_revision__ = 0


import sys
import os, os.path
import urllib
from time import sleep
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

MEDIA_PATH = os.path.join(__addonDir__, 'resources', 'media')



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


ROOTDIR                 = __settings__.getAddonInfo('path') # os.getcwd()
BASE_RESOURCE_PATH      = os.path.join( ROOTDIR, "resources" )
ADDON_DATA              = xbmc.translatePath( "special://profile/addon_data/%s/" % __addonID__ )
DOWNLOADDIR             = os.path.join( ADDON_DATA, "downloads")
CACHEDIR                = os.path.join( ADDON_DATA, "cache")
#COLOR_IMG_URL           = "http://www.color-hex.com/colorimg.php?color="
#COLOR_IMG_URL           = "http://www.colorhexa.com/%s.png"
COLOR_IMG_URL           = os.path.join( MEDIA_PATH, "%s.png")
BOOKMARKS_DB_PATH       = os.path.join( CACHEDIR, "sb.txt" )
#BASE_THUMBS_PATH = os.path.join( xbmc.translatePath( "special://profile/" ), "Thumbnails", "Video" )

# List of directories to check at startup
dirCheckList   = ( CACHEDIR, DOWNLOADDIR, ) #Tuple - Singleton (Note Extra ,)

# Modules custom
#if sys.modules.has_key("cplusplus"):
#    del sys.modules['cplusplus']
try:
    import resources.libs.cplusplus as cpp
    from resources.libs.utilities import PersistentDataCreator, PersistentDataRetriever
except:
    print_exc()




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
    PARAM_LIST_BOOKMARKS  = "listebookmarks"
    PARAM_SEARCH          = "search"
    PARAM_SEARCH_DIALOG   = "searchdialog"
    PARAM_THEME_ID        = "theme_id"
    PARAM_SUBTHEME_ID     = "subtheme_id"
    PARAM_VIDEO_ID        = "video_id"
    PARAM_REFERER         = "referer"
    PARAM_DOWNLOAD_VIDEO  = "dlvideo"
    PARAM_PLAY_VIDEO      = "playvideo"
    PARAM_SHOW_VIDEO_INFO = "showvideoinfos"
    PARAM_SHOW_PICTURE    = "showpicture"
    PARAM_ADD_BOOKMARK    = "addbookmark"
    PARAM_BOOKMARK_URL    = "bookmarkurl"

    pluginhandle = int(sys.argv[1])


    PARAM_TYPE        = 'type'
    PARAM_URL         = 'url'

    def __init__( self, *args, **kwargs ):
        print "===================================="
        print "CANAL+ version %s - DEMARRAGE"%__version__
        print "===================================="
        sleep(1)
        self.set_debug_mode()

        if self.debug_mode:
            print "Python version:"
            print sys.version_info
            print "plugin: URL"
            print sys.argv[ 0 ] + sys.argv[ 2 ]
            print "ROOTDIR: %s"%ROOTDIR
            print "ADDON_DATA: %s"%ADDON_DATA
            print "CACHEDIR: %s"%CACHEDIR

        self.set_options_display()
        self.parameters = self._parse_params()

        # Check if directories in user data exist
        for i in range( len( dirCheckList ) ):
            verifrep( dirCheckList[i] )

        self.select()


    def set_debug_mode(self):
        debug =__settings__.getSetting('debug')
        if debug == 'true':
            self.debug_mode = True
        else:
            self.debug_mode = False
        print "CANAL+: debug Mode:"
        print self.debug_mode

    def set_options_display(self):
        debug =__settings__.getSetting('debug')
        self.options_display = int( __settings__.getSetting( 'option_display' ) ) # 0: context menu / 1: video list / 2: both
        print "CANAL+: options_display Mode:"
        print self.options_display

    def select( self ):
        try:
            if self.debug_mode:
                print "select"
                print self.parameters

            if len(self.parameters) < 1:
                self.show_themes()

            elif self.PARAM_SEARCH_DIALOG in self.parameters.keys():
                self.show_search_dialog( self.parameters[self.PARAM_THEME_ID],self.parameters[self.PARAM_SUBTHEME_ID], self.parameters[self.PARAM_REFERER])

            elif self.PARAM_SEARCH in self.parameters.keys():
                # Lance une recherche et affiche les resultat des videos trouvees
                self.show_search(self.parameters[self.PARAM_SEARCH], self.parameters[self.PARAM_THEME_ID],self.parameters[self.PARAM_SUBTHEME_ID])

            elif self.PARAM_ADD_BOOKMARK in self.parameters.keys():
                ok = self.add_bookmark( self.parameters[self.PARAM_ADD_BOOKMARK], self.parameters[self.PARAM_BOOKMARK_URL] )

                # To prevent to re-save bm after video playback
                xbmc.executebuiltin('XBMC.Container.Update(%s)' % (self.parameters[self.PARAM_BOOKMARK_URL]))


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

            elif self.PARAM_LIST_BOOKMARKS in self.parameters.keys():
                #on liste les favoris
                self.show_bookmarks()

            elif self.PARAM_PLAY_VIDEO in self.parameters.keys():
                # On lance la video
                video_id = int(self.parameters[self.PARAM_VIDEO_ID])
                urls_videos = []
                urls_videos = self.get_video_urls(video_id)
                if self.debug_mode:
                    print "urls_videos :"
                    print str(urls_videos)
                    print str(int(__settings__.getSetting('video_quality')))
                url = urls_videos[int(__settings__.getSetting('video_quality'))]

                # Play  video
                item = xbmcgui.ListItem(path=url)

                print "Canal+: Lecture de la video: %s"%str(url)
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
        if self.debug_mode:
            print paramDic
        return paramDic


    def _create_param_url(self, paramsDic, quote_plus=False):
        """
        Create an plugin URL based on the key/value passed in a dictionary
        """
        url = sys.argv[ 0 ]
        sep = '?'
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
        if self.debug_mode:
            print "_addLink - iconimage: %s"%iconimage
            print itemInfoLabels
            print c_items
            print totalItems
        try:
            lstItem=xbmcgui.ListItem( label=name, label2=name2, iconImage=iconimage, thumbnailImage=iconimage )
            if c_items :
                lstItem.addContextMenuItems( c_items, replaceItems=False )

            if itemInfoLabels:
                iLabels = itemInfoLabels
            else:
                iLabels = { "Title": name }

            lstItem.setInfo( type=itemInfoType, infoLabels=iLabels )
            lstItem.setProperty('IsPlayable', 'true')
            ok=xbmcplugin.addDirectoryItem( handle=int(sys.argv[1]), url=url, listitem=lstItem, totalItems=totalItems )
        except:
            ok = False
        return ok


    def _addDir( self, name, name2="", url="", iconimage="DefaultFolder.png", itemInfoType="Video", itemInfoLabels=None, c_items=None, totalItems=0 ):
        #u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        ok=True
        if self.debug_mode:
            #print "_addDir - name: %s"%str(name)
            print "_addDir - iconimage: %s"%iconimage
            print itemInfoLabels
            print c_items
            print totalItems
        try:
            lstItem=xbmcgui.ListItem( label=name, label2=name2, iconImage=iconimage, thumbnailImage=iconimage )

            if c_items :
                lstItem.addContextMenuItems( c_items, replaceItems=False )

            if itemInfoLabels:
                iLabels = itemInfoLabels
            else:
                iLabels = { "Title": name }

            lstItem.setInfo( type=itemInfoType, infoLabels=iLabels )
            ok=xbmcplugin.addDirectoryItem( handle=int( sys.argv[1] ), url=url, listitem=lstItem, isFolder=True, totalItems=totalItems )
        except:
            ok = False
            print_exc()
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


    def show_search_dialog(self, theme_id,subtheme_id, referer=""):
        """
        Display virtual keyboard and start a search
        """
        kb = xbmc.Keyboard("", __language__( 30203 ), False) #Recherche sur Canal Plus Videos
        kb.doModal()
        if kb.isConfirmed():
            motcle = kb.getText()
            if ( len(motcle) > 2): # Taille mini pour une recherche
                paramsAddonsSearch = {}
                paramsAddonsSearch[self.PARAM_SEARCH]      = motcle
                paramsAddonsSearch[self.PARAM_THEME_ID]    = "theme_id"
                paramsAddonsSearch[self.PARAM_SUBTHEME_ID] = "subtheme_id"
                paramsAddonsSearch[self.PARAM_REFERER]     = referer
                urlSearch = self._create_param_url( paramsAddonsSearch )
                xbmc.executebuiltin('XBMC.Container.Update(%s)' % (urlSearch))
            else:
                #dialogError = xbmcgui.Dialog()
                #ok = dialogError.ok( __language__( 30204 ), __language__( 30205 ), __language__( 30206 ) )
                xbmc.executebuiltin( "XBMC.Notification(%s,%s %s,5000,DefaultIconError.png)" % (  __language__( 30000 ), __language__( 30205 ), __language__( 30206 ) ) )

    def show_search(self, motcle, th_id, subth_id):
        """
        Display virtual keyboard and start a search
        """
        self.show_videos(theme_id=th_id,subtheme_id=subth_id,referer="Resultats pour '%s'"%motcle,keyword=motcle)


    def get_video_urls(self, video_id):
        """
        Retrieve  video URL
        """
        infos = cpp.get_info(video_id)
        return [infos["video.low"], infos["video.hi"], infos["video.mobile"], infos["video.hds"], infos["video.hls"]]


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

        # Bookmarks
        paramsGetBookmarks = {}
        paramsGetBookmarks[self.PARAM_LIST_BOOKMARKS] = "True"
        urlGetBookmarks = self._create_param_url( paramsGetBookmarks )
        self._addDir( __language__ ( 30003 ), url=urlGetBookmarks, iconimage=os.path.join( MEDIA_PATH, "favorites.png") )

        # Recherche
        #url = sys.argv[0]+"?search=&theme_id=%s&subtheme_id=%s&referer=%s"%("Rechercher dans toutes les catégories :",
        #                                                                    "",
        #                                                                    "")
        paramsAddonsSearch = {}
        paramsAddonsSearch[self.PARAM_SEARCH_DIALOG] = "True"
        paramsAddonsSearch[self.PARAM_THEME_ID]      = "None"
        paramsAddonsSearch[self.PARAM_SUBTHEME_ID]   = "None"
        paramsAddonsSearch[self.PARAM_REFERER]       = "Rechercher dans toutes les catégories :"
        urlSearch = self._create_param_url( paramsAddonsSearch )

        # Addboomarks
        paramsAddBookmark = {}
        paramsAddBookmark[self.PARAM_ADD_BOOKMARK] = __language__ ( 30002 )
        paramsAddBookmark[self.PARAM_BOOKMARK_URL] = sys.argv[ 0 ] + sys.argv[ 2 ] # current plugin url

        urlAddBkM = self._create_param_url( paramsAddBookmark, quote_plus=True )

        if self.options_display in [1, 2]:
            self._addDir( __language__ ( 30001 ), url=urlSearch )
            self._addDir( __language__ ( 30110 ), url=urlAddBkM )

        themes=cpp.get_themes()
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

                if self.options_display in [0, 2]:
#                    cm = [(__language__( 30001 ), 'XBMC.Container.Update(%s)' % (urlSearch)),
#                          (__language__( 30110 ), 'XBMC.Container.Update(%s)' % (urlAddBkM))]
                    cm = [(__language__( 30001 ), 'XBMC.Container.Update(%s)' % (urlSearch)),
                          (__language__( 30110 ), 'XBMC.RunPlugin(%s)' % (urlAddBkM))]
                    #TODO: check how to call plugin withotu changing list
#                    url_args = sys.argv[2].replace("self_update=True&", "")
#                    # create path to module in backups
#                    filepath= "plugin://programs/.backups/" + __plugin__
#                    path = '%s%s' % ( filepath, url_args, )
#
#                    # run module from backup
#                    command = 'XBMC.RunPlugin(%s)' % path
#                    log(command)
#                    xbmc.executebuiltin(command)

                else:
                    cm = None
                thumb = COLOR_IMG_URL % (theme_color.lower())
                self._addDir( name=theme_titre, url=url, iconimage=thumb, totalItems=len(themes), c_items=cm )
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
        paramsAddonsSearch[self.PARAM_SEARCH_DIALOG] = ""
        paramsAddonsSearch[self.PARAM_THEME_ID]      = str(theme_id)
        paramsAddonsSearch[self.PARAM_SUBTHEME_ID]   = ""
        paramsAddonsSearch[self.PARAM_REFERER]       = "Rechercher dans %s :"%referer
        urlSearch = self._create_param_url( paramsAddonsSearch )

        paramsAddBookmark = {}
        paramsAddBookmark[self.PARAM_ADD_BOOKMARK] = referer
        paramsAddBookmark[self.PARAM_BOOKMARK_URL] = sys.argv[ 0 ] + sys.argv[ 2 ] # current plugin url
        urlAddBkM = self._create_param_url( paramsAddBookmark, quote_plus=True )

        if self.options_display in [1, 2]:
            self._addDir( __language__ ( 30001 ), url=urlSearch )
            self._addDir( __language__ ( 30110 ), url=urlAddBkM )

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

            if self.options_display in [0, 2]:
#                cm = [(__language__( 30001 ), 'XBMC.Container.Update(%s)' % (urlSearch)),
#                      (__language__( 30110 ), 'XBMC.Container.Update(%s)' % (urlAddBkM))]
                cm = [(__language__( 30001 ), 'XBMC.Container.Update(%s)' % (urlSearch)),
                      (__language__( 30110 ), 'XBMC.RunPlugin(%s)' % (urlAddBkM))]
            else:
                cm = None
            self._addDir( name=subtheme_titre, url=url, totalItems=len(subthemes), c_items=cm )
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
        paramsAddonsSearch[self.PARAM_SEARCH_DIALOG] = ""
        paramsAddonsSearch[self.PARAM_THEME_ID]      = str(theme_id)
        paramsAddonsSearch[self.PARAM_SUBTHEME_ID]   = str(subtheme_id)
        paramsAddonsSearch[self.PARAM_REFERER]       = "Rechercher dans %s"%referer
        urlSearch = self._create_param_url( paramsAddonsSearch )

        paramsAddBookmark = {}
        if keyword == "":
            paramsAddBookmark[self.PARAM_ADD_BOOKMARK] = referer
        else:
            paramsAddBookmark[self.PARAM_ADD_BOOKMARK] = keyword
        paramsAddBookmark[self.PARAM_BOOKMARK_URL] = sys.argv[ 0 ] + sys.argv[ 2 ] # current plugin url
        urlAddBkM = self._create_param_url( paramsAddBookmark, quote_plus=True )

        if self.options_display in [1, 2]:
            self._addDir( __language__ ( 30001 ), url=urlSearch )
            self._addDir( __language__ ( 30110 ), url=urlAddBkM )

        for video in videos:
            try:

                paramsAddons = {}
                paramsAddons[self.PARAM_PLAY_VIDEO]  = "true"
                paramsAddons[self.PARAM_VIDEO_ID]    = str(video["videoID"])
                url = self._create_param_url( paramsAddons )
                thumb=video['image.url']


                #menu contextuel
                if self.options_display in [0, 2]:
#                    cm = [(__language__( 30001 ), 'XBMC.Container.Update(%s)' % (urlSearch)),
#                          (__language__( 30110 ), 'XBMC.Container.Update(%s)' % (urlAddBkM))]
                    cm = [(__language__( 30001 ), 'XBMC.Container.Update(%s)' % (urlSearch)),
                          (__language__( 30110 ), 'XBMC.RunPlugin(%s)' % (urlAddBkM))]
                else:
                    cm = None

                infoLabels={ "Title": video["title"] + " " + video["publication_date"],
                             "Rating":video["note"],
                             "Date": video["publication_date"],
                             "Plot": video["description"] }

                self._addLink( name=video["title"], url=url, iconimage=thumb, itemInfoLabels=infoLabels, c_items=cm )
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

    def show_bookmarks ( self ):
        ok = True
        i= 0

        # Recuperation de la liste des themes
        pDialog = xbmcgui.DialogProgress()
        ret = pDialog.create( 'XBMC', __language__ ( 30200 ) )
        pDialog.update(0, __language__ ( 30202 ) )

        # Recherche
        #url = sys.argv[0]+"?search=&theme_id=%s&subtheme_id=%s&referer=%s"%("Rechercher dans toutes les catégories :",
        #                                                                    "",
        #                                                                    "")
        paramsAddonsSearch = {}
        paramsAddonsSearch[self.PARAM_SEARCH_DIALOG] = "True"
        paramsAddonsSearch[self.PARAM_THEME_ID]      = "None"
        paramsAddonsSearch[self.PARAM_SUBTHEME_ID]   = "None"
        paramsAddonsSearch[self.PARAM_REFERER]       = "Rechercher dans toutes les catégories :"
        urlSearch = self._create_param_url( paramsAddonsSearch )

#        paramsAddBookmark = {}
#        paramsAddBookmark[self.PARAM_ADD_BOOKMARK] = __language__ ( 30002 )
#        paramsAddBookmark[self.PARAM_BOOKMARK_URL] = sys.argv[ 0 ] + sys.argv[ 2 ] # current plugin url
#        urlAddBkM = self._create_param_url( paramsAddBookmark, quote_plus=True )

        if self.options_display in [1, 2]:
            self._addDir( __language__ ( 30001 ), url=urlSearch )
#            self._addDir( __language__ ( 30110 ), url=urlAddBkM )

        bookmarks = self.get_bookmarks()
        for bookmarkName in bookmarks.keys():
            if self.options_display in [0, 2]:
#                    cm = [(__language__( 30001 ), 'XBMC.Container.Update(%s)' % (urlSearch)),
#                          (__language__( 30110 ), 'XBMC.Container.Update(%s)' % (urlAddBkM))]
                cm = [(__language__( 30001 ), 'XBMC.Container.Update(%s)' % (urlSearch))]
            else:
                cm = None
            self._addDir( name=bookmarkName, url=bookmarks[bookmarkName], totalItems=len(bookmarks), c_items=cm )
            i=i+1
            pDialog.update(int(99*float(i)/(len(bookmarks))), __language__ ( 30202 ) )
        xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_NONE)
        xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category= __language__ ( 30003 )) # Catégories
        self._end_of_directory( True )
        return ok

    def get_bookmarks( self ):
        """
        Recupere les favoris
        """
        status = "OK"
        # retrieved bookmarks
        bookmarks = {}
        if os.path.exists(BOOKMARKS_DB_PATH):
            pdr = PersistentDataRetriever( BOOKMARKS_DB_PATH )
            bookmarks = pdr.get_data()
        if self.debug_mode:
            print 'bookmarks:'
            print bookmarks
        return bookmarks


    def add_bookmark( self, name, url ):
        """
        Ajoute un favoris a la iste des favoris
        """
        # retrieved bookmarks
        bookmarks = {}
        if os.path.exists(BOOKMARKS_DB_PATH):
            pdr = PersistentDataRetriever( BOOKMARKS_DB_PATH )
            bookmarks = pdr.get_data()
        if self.debug_mode:
            print 'add_bookmark - bookmarks before:'
            print bookmarks
        bmFound = False
        for key in bookmarks:
            if bookmarks[key] == url:
                # This links is already in the bookmarks
                bmFound = True
                print "bookmark %s already saved"%name
                if self.debug_mode:
                    print "url: %s"%url
                icon = os.path.join( MEDIA_PATH, "favorites.png")
                xbmc.executebuiltin( "XBMC.Notification(%s,%s,5000,DefaultIconError.png)" % ( __language__( 30000 ), __language__( 30005 ) ) )
                break

        if not bmFound:
            print "url not found in bookmarks - adding it ..."
            kb = xbmc.Keyboard(name, __language__( 30208 ), False) #Bookmark name to save
            kb.doModal()
            if kb.isConfirmed():
                motcle = kb.getText()
                if ( len(motcle) > 2): # Minimum size for bookmark name must be > 2 chars
                    if bookmarks.has_key(motcle):
                        # bookmark name already used, we won't save this bookmark
                        xbmc.executebuiltin( "XBMC.Notification(%s,%s,5000,DefaultIconError.png)" % (  __language__( 30000 ), __language__( 30209 ) ) )
                    else:
                        # Saving bookmark
                        bookmarks[motcle] = url
                        if self.debug_mode:
                            print 'add_bookmark - bookmarks after:'
                            print bookmarks

                        # Update bookmarks files
                        PersistentDataCreator( bookmarks, BOOKMARKS_DB_PATH )

                        # notify user of success
                        icon = os.path.join( MEDIA_PATH, "favorites.png")
                        xbmc.executebuiltin( "XBMC.Notification(%s,%s,5000,%s)" % ( __language__( 30000 ), __language__( 30004 ), icon ) )

                else:
                    # String t0o short, we won't save this bookmark
                    xbmc.executebuiltin( "XBMC.Notification(%s,%s %s,5000,DefaultIconError.png)" % (  __language__( 30000 ), __language__( 30207 ), __language__( 30206 ) ) )


    def delete_search_bookmark( self, name ):
        status = "OK"
        # retrieved bookmarks
        bookmarks = {}
        if os.path.exists(BOOKMARKS_DB_PATH):
            pdr = PersistentDataRetriever( BOOKMARKS_DB_PATH )
            bookmarks = pdr.get_data()

        print 'bookmarks:'
        print bookmarks
        if bookmarks.has_key(name):
            bookmarks.pop(name)
            bookmarks.remove(url)
        else:
            print "bookmark not found"
            status = "NOT_FOUND"

        # Update bookmarks files
        PersistentDataCreator( bookmarks, BOOKMARKS_DB_PATH )
        return status


#######################################################################################################################
# BEGIN !
#######################################################################################################################

if ( __name__ == "__main__" ):
    try:
        CanalPlusMosaicPlugin()
    except:
        print_exc()
