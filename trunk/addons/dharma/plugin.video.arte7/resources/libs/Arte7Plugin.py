# -*- coding: utf-8 -*-
import os
import sys

import urllib2, xml.dom.minidom, string
from traceback import print_exc

import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon

import BeautifulSoup as BS
import SimpleDownloader as downloader

# Recuperation des constants
__plugin__       = sys.modules[ "__main__" ].__plugin__
__addonID__      = sys.modules[ "__main__" ].__addonID__
__author__       = sys.modules[ "__main__" ].__author__
__platform__     = sys.modules[ "__main__" ].__platform__
__date__         = sys.modules[ "__main__" ].__date__
__version__      = sys.modules[ "__main__" ].__version__
__addon__        = sys.modules[ "__main__" ].__addon__
__settings__     = sys.modules[ "__main__" ].__settings__
__language__     = sys.modules[ "__main__" ].__language__
__addonDir__     = sys.modules[ "__main__" ].__addonDir__


# Custom modules
from Catalog import Catalog, unescape_html, get_lang
from Utils import _addLink, _parse_params, verifrep, _add_sort_methods, _end_of_directory, _addDir, _create_param_url, _addContextMenuItems


class Arte7Plugin: 
    
    ROOTDIR            = __addonDir__ 
    BASE_RESOURCE_PATH = os.path.join( ROOTDIR, "resources" )
    ADDON_DATA         = xbmc.translatePath( "special://profile/addon_data/%s/" % __addonID__ )
    DOWNLOADDIR        = os.path.join( ADDON_DATA, "downloads")
    CACHEDIR           = os.path.join( ADDON_DATA, "cache")
    FILENAME           = "arteCatalogue.tmp"
    COLOR_IMG_URL      = "http://www.color-hex.com/colorimg.php?color="
    NB_VIDEO           = 0
    USERAGENT = "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-GB; rv:1.9.2.8) Gecko/20100722 Firefox/3.6.8"
    
    # define param key names
    PARAM_LIST_VIDEOS     = "listevideos"
    PARAM_DOWNLOAD_VIDEO  = "dlvideo"
    PARAM_PLAY_VIDEO      = "playvideo"
    PARAM_SHOW_VIDEO_INFO = "showvideoinfos"
    PARAM_SHOW_PICTURE    = "showpicture"
    PARAM_VIDEO_ID        = "video_id"
    PARAM_VIDEO_NAME      = "video_name"
    
    pluginhandle = int(sys.argv[1])
    dirCheckList = ( CACHEDIR, DOWNLOADDIR )
    
    PARAM_TYPE        = 'type'
    PARAM_URL         = 'url'

    def __init__( self, *args, **kwargs ):
        print "================================"
        print "Arte7 - DEMARRAGE"
#        xbmc.executebuiltin("XBMC.Notification(%s,%s)"%("Arte7","DEMARRAGE")) 
        self.parameters = _parse_params()
        
        # Check if directories in user data exist
        for i in range( len( self.dirCheckList ) ):
            verifrep( self.dirCheckList[i] ) 
  
        self.select()

    def select( self ):
        try:
            if len(self.parameters) < 1:
                #on liste les videos
                self.show_videos_init()

            elif self.PARAM_LIST_VIDEOS in self.parameters.keys():
                #on liste les videos
                self.show_videos()
                   
            elif self.PARAM_PLAY_VIDEO in self.parameters.keys():
                # On lance la video               
                url_page = self.parameters[self.PARAM_VIDEO_ID]
                url = self.get_rtmp_url( url_page, quality = "hd"  )

                # Play  video
                item = xbmcgui.ListItem(path=url)

                xbmcplugin.setResolvedUrl(handle=int(sys.argv[1]), succeeded=True, listitem=item)
                _end_of_directory( True )
                
            elif self.PARAM_DOWNLOAD_VIDEO in self.parameters.keys(): 
                video = {}
                
                name = self.parameters[self.PARAM_VIDEO_NAME]
                
                url_page = self.parameters[self.PARAM_VIDEO_ID]
                url = self.get_rtmp_url( url_page, quality = "hd"  )             

                video[self.PARAM_VIDEO_ID] = url
                video[self.PARAM_VIDEO_NAME] = name

                self.downloadVideo(video)     

        except Exception,msg:
            xbmc.executebuiltin("XBMC.Notification(%s,%s)"%("ERROR select",msg)) 
            print ("Error select")
            print_exc()
            
            _end_of_directory( False )

    def show_videos_init(self):
        
        ok = True
        cpt = 0

        file = xbmc.makeLegalFilename(os.path.join(self.CACHEDIR,self.FILENAME))
        f = open(file,'w')
        
        pDialog = xbmcgui.DialogProgress()
        ret = pDialog.create( 'XBMC', __language__ ( 30200 ) )        
        pDialog.update(0, __language__ ( 30202 ) )
        
        catalog = Catalog()
        self.NB_VIDEO = catalog.videos.__len__();
                 
        for video in catalog.videos:                 
            f.write('\n'.join(['%s;%s;%s;%s' % (video[Catalog.TITLE_TAG].encode('utf-8'),video[Catalog.DATE_TAG].encode('utf-8'), video[Catalog.URL_TAG].encode('utf-8'), video[Catalog.IMAGE_TAG].encode('utf-8'))]))
          
            cpt=cpt+1

            paramsAddons = {}
            paramsAddons[self.PARAM_PLAY_VIDEO]  = "true"
            paramsAddons[self.PARAM_VIDEO_ID]    = video[Catalog.URL_TAG]
            url = _create_param_url( paramsAddons )
                            
            infoLabels={ "Title": video[Catalog.DATE_TAG] + " - " + video[Catalog.TITLE_TAG],
                         "Date": video[Catalog.DATE_TAG]}            
            
            paramsAddonsContextMenu = {}
            paramsAddonsContextMenu[self.PARAM_DOWNLOAD_VIDEO]  = "true"
            paramsAddonsContextMenu[self.PARAM_VIDEO_ID]    = video[Catalog.URL_TAG]
            paramsAddonsContextMenu[self.PARAM_VIDEO_NAME]    = video[Catalog.TITLE_TAG]
            
            urlContextMenu = _create_param_url( paramsAddonsContextMenu )
            
            cm = _addContextMenuItems(name=video[Catalog.TITLE_TAG], url=urlContextMenu, msg= __language__(30102))
            
            _addLink( name=video[Catalog.TITLE_TAG], url=url, iconimage=video[Catalog.IMAGE_TAG], itemInfoLabels=infoLabels, c_items=cm )

            pDialog.update(int(99*float(cpt)/(self.NB_VIDEO)), __language__ ( 30202 ) )            
       
        pDialog.close()
        
        f.close()
                
        xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_NONE)
        xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category="referer" )
        xbmcplugin.setContent(int(sys.argv[1]), 'movies')
        _end_of_directory( True )

        return ok

    def show_videos(self):
        """
        rempli la liste avec la liste des videos
        """
        ok = True
        cpt = 0
        file = xbmc.makeLegalFilename(os.path.join(self.CACHEDIR,self.FILENAME))
        f = open(file,"r")

        pDialog = xbmcgui.DialogProgress()
        ret = pDialog.create( 'XBMC', __language__ ( 30200 ) )        
        pDialog.update(0, __language__ ( 30202 ) )

        for line in f:        
            video = line.split(";")
            cpt=cpt+1

            paramsAddons = {}
            paramsAddons[self.PARAM_PLAY_VIDEO]  = "true"
            paramsAddons[self.PARAM_VIDEO_ID]    = video[2]
            url = _create_param_url( paramsAddons )
            
            infoLabels={ "Title": video[1] + " - " + video[0],
                         "Date": video[1]}            
            
            _addLink( name=video[0], url=url, iconimage=video[3], itemInfoLabels=infoLabels )

            paramsAddons = {}
            paramsAddons[self.PARAM_DOWNLOAD_VIDEO]  = "true"
            paramsAddons[self.PARAM_VIDEO_ID]    = video[2]
            url = _create_param_url( paramsAddons )
            _addContextMenuItems(video[1],url, __language__(30102))
            
            pDialog.update(int(99*float(cpt)/(self.NB_VIDEO)), __language__ ( 30202 ) )

        pDialog.close()
        
        f.close()
                
        xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_NONE)
        xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category="referer" )
        xbmcplugin.setContent(int(sys.argv[1]), 'movies')
        _end_of_directory( True )

        return ok

    def unescape_xml(self, text):
        text = text.replace( "%3A", ":").replace( "%2F", "/").replace( "%2C", ",")
        return BS.BeautifulStoneSoup(text, convertEntities=BS.BeautifulStoneSoup.XML_ENTITIES).contents[0]

    def get_rtmp_url(self, url_page, quality ):
        page_soup = BS.BeautifulSoup( urllib2.urlopen(url_page).read() )

        movie_object = page_soup.find("object", classid="clsid:d27cdb6e-ae6d-11cf-96b8-444553540000")
        movie = movie_object.find("param", {"name":"movie"})
        movie_url = "http" + self.unescape_xml(movie['value'].split("http")[-1])

        xml_soup = BS.BeautifulStoneSoup( urllib2.urlopen(movie_url).read() )
        movie_url = xml_soup.find("video", {'lang': get_lang()})['ref']

        xml_soup = BS.BeautifulStoneSoup( urllib2.urlopen(movie_url).read() )
        base_soup = xml_soup.find("urls")
        movie_url = base_soup.find("url", {"quality": quality}).string
        return movie_url

    def downloadVideo(self, video):
        ok = True    
        try:
            my_downloader = downloader.SimpleDownloader()
            params = {"videoid": "1", "video_url": video[self.PARAM_VIDEO_ID], "Title": video[self.PARAM_VIDEO_NAME]}
            my_downloader.downloadVideo(params)            
            
        except Exception,msg:
            print_exc("Error downloadVideo : %s", msg)
            xbmc.executebuiltin("XBMC.Notification(%s,%s)"%("ERROR downloadVideo ",msg))  

        return ok
