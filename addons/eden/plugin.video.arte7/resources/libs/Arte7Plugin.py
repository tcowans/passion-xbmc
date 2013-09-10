# -*- coding: utf-8 -*-
import os, re, sys
import xbmc, xbmcgui, xbmcplugin, xbmcaddon
import urllib2, xml.dom.minidom, string
from threading import Thread, current_thread
from traceback import print_exc

# Custom modules
import SimpleDownloader as downloader
from parsers import PlusParser, LiveParser, EventParser, BonusParser, ProgrammesParser, SearchParser
from Utils import _addLink, _parse_params, verifrep, _end_of_directory, _addDir, _create_param_url, _add_to_index, strip_html

# Recuperation des constantes
__addonID__      = sys.modules[ "__main__" ].__addonID__
__settings__     = sys.modules[ "__main__" ].__settings__
__language__     = sys.modules[ "__main__" ].__language__

class Arte7Plugin: 
    
    ADDON_DATA         = xbmc.translatePath( "special://profile/addon_data/%s/" % __addonID__ )
    DOWNLOADDIR        = os.path.join( ADDON_DATA, "downloads")
    
    # define param key names
    PARAM_DOWNLOAD_VIDEO              = "dlvideo"
    PARAM_PLAY_VIDEO                  = "playvideo"
    PARAM_SHOW_CATEGORIE              = "show_categorie"
    PARAM_VIDEO_ID                    = "video_id"
    PARAM_VIDEO_NAME                  = "video_name"

    PARAM_ARTE_PLUS                   = "arte_plus"
    PARAM_ARTE_LIVE                   = "arte_live"
    PARAM_ARTE_EVENT                  = "arte_event"
    PARAM_ARTE_BONUS                  = "arte_bonus"
    PARAM_ARTE_PROGRAMMES             = "arte_programmes"
    PARAM_ARTE_SEARCH                 = "arte_search"

    PARAM_NEXT_PAGE                   = "arte_next_page"
    PARAM_NEXT_PAGE_NUMBER            = "arte_next_page_number"

    PARAM_ARTE_CATEGORIE              = "arte_categorie"
    PARAM_ARTE_CATEGORIE_KEY          = "arte_categorie_key"
    PARAM_ARTE_CATEGORIE_VALUE        = "arte_categorie_value"

    #verification du dossier de téléchargement
    dl_dir = __settings__.getSetting( 'downloadPath' )
    if dl_dir != "":
        DOWNLOADDIR = dl_dir
    dirCheckList = ( DOWNLOADDIR )

    #récupération des données pour pagination
    pluginhandle = int( sys.argv[1] )
    numbers=[ "10","25","50","100" ]
    NB_VIDEOS_PER_PAGE=numbers[ int( __settings__.getSetting( "nbVideoPerPage" ) ) ]
    PAGE_NUMBER = 1
    NEXT_PAGE_NUMBER = None

    #recupération de la langue
    lang_id = int( __settings__.getSetting( 'vid_language' ) )
    lang    = [ "fr","de" ][ lang_id ]

    quality = int( __settings__.getSetting( 'vid_quality' ) )

    if quality == 0:
        is_HD = True
    else:
        is_HD = False

    #Initialisation des principales variables
    ARTE_CATEGORIE = None
    PASER          = None
    VIDEOS         = []
    CATEGORIES     = {}

    def __init__( self, *args, **kwargs ):
        print "================================"
        print "Arte7 - DEMARRAGE"

        self.parameters = _parse_params()

        #on recupere le bon parser
        if self.PARAM_ARTE_CATEGORIE in self.parameters.keys():
            self.ARTE_CATEGORIE = self.parameters[ self.PARAM_ARTE_CATEGORIE ]
            self.PARSER = self.retrieveParser( self.lang )

        self.select()

    def select( self ):
        try:
            if len( self.parameters ) < 1:
                #initialisation
                self.show_menu()

            elif self.PARAM_ARTE_PLUS in self.parameters.keys():
                #on liste les videos arte+7, une page contenant au max 200 vidéos
                self.ARTE_CATEGORIE = self.PARAM_ARTE_PLUS
                self.PARSER = PlusParser( self.lang, self.VIDEOS )
                self.PARSER.parse( 1, 200 )
                self.show_videos( self.VIDEOS )

            elif self.PARAM_ARTE_LIVE in self.parameters.keys():
                #on liste les categories arte live
                self.ARTE_CATEGORIE = self.PARAM_ARTE_LIVE
                self.show_categories()

            elif self.PARAM_ARTE_EVENT in self.parameters.keys():
                #on liste les categories arte event
                self.ARTE_CATEGORIE = self.PARAM_ARTE_EVENT
                self.show_categories()

            elif self.PARAM_ARTE_BONUS in self.parameters.keys():
                #on liste les categories arte bonus
                self.ARTE_CATEGORIE = self.PARAM_ARTE_BONUS
                self.show_categories()

            elif self.PARAM_ARTE_PROGRAMMES in self.parameters.keys():
                #on liste les categories arte programmes
                self.ARTE_CATEGORIE = self.PARAM_ARTE_PROGRAMMES
                self.show_categories()

            elif self.PARAM_ARTE_SEARCH in self.parameters.keys():
                keyboard = xbmc.Keyboard('', __language__( 30001 ))
                keyboard.doModal()
                if keyboard.isConfirmed() and keyboard.getText():
                    search = keyboard.getText().replace(" ","+")
                    self.ARTE_CATEGORIE = self.PARAM_ARTE_SEARCH
                    self.PARSER = SearchParser( self.lang, self.VIDEOS )
                    self.PARSER.parse( 1, 200, search )
                    self.show_videos( self.VIDEOS )

            elif self.PARAM_SHOW_CATEGORIE in self.parameters.keys() and self.PARSER is not None:
                #on liste les videos arte event
                key = self.parameters[ self.PARAM_ARTE_CATEGORIE_KEY ].replace( 'brinbrin','&' )
                value = self.parameters[ self.PARAM_ARTE_CATEGORIE_VALUE ]

                if isinstance( self.PARSER, LiveParser ) :
                    self.PARSER.get_videos_list( key, self.VIDEOS )
                else:
                    self.NEXT_PAGE_NUMBER = self.PARSER.parse( value, self.PAGE_NUMBER, self.NB_VIDEOS_PER_PAGE )

                self.show_videos( self.VIDEOS )

            elif self.PARAM_NEXT_PAGE in self.parameters.keys() and self.PARSER is not None:
                #en cas de passage a la page suivante
                self.PAGE_NUMBER = self.parameters[ self.PARAM_NEXT_PAGE_NUMBER ]

                value = self.parameters[ self.PARAM_ARTE_CATEGORIE_VALUE ]
                self.NEXT_PAGE_NUMBER = self.PARSER.parse( value, self.PAGE_NUMBER, self.NB_VIDEOS_PER_PAGE )

                self.show_videos( self.VIDEOS )

            elif self.PARAM_PLAY_VIDEO in self.parameters.keys() and self.PARSER is not None:
                # On lance la video               
                hd = self.retrieveVideoLink( link = self.parameters[ self.PARAM_VIDEO_ID ] )

                if hd is None:
                    xbmc.executebuiltin( "XBMC.Notification(%s,%s)"%( __language__( 30300 ) , __language__( 30301 ) ) )

                else:

                    if isinstance(self.PARSER, LiveParser) :
                        hd, downloadParams = self.PARSER.decode_link( hd ) 

                    item = xbmcgui.ListItem( path = hd )
                    xbmcplugin.setResolvedUrl( handle = int( sys.argv[ 1 ] ), succeeded=True, listitem=item )
                
            elif self.PARAM_DOWNLOAD_VIDEO in self.parameters.keys() and self.PARSER is not None:
                # On telecharge la video
                video = {}
                name = self.parameters[ self.PARAM_VIDEO_NAME ]
                hd = self.retrieveVideoLink( link = self.parameters[ self.PARAM_VIDEO_ID ] )

                if hd is None:
                    xbmc.executebuiltin( "XBMC.Notification(%s,%s)"%( __language__( 30300 ), __language__( 30301 ) ) )

                else:
                    video[self.PARAM_VIDEO_ID] = hd
                    video[self.PARAM_VIDEO_NAME] = name
                    self.downloadVideo(video)

            else :
                #Probleme, pas de bon parametre detecte donc on initialise
                self.show_menu()

            _end_of_directory( True )

        except Exception,msg:
            xbmc.executebuiltin( "XBMC.Notification(%s,%s)"%( "ERROR select", msg ) ) 
            print ( "Error select" )
            print_exc()
            _end_of_directory( False )

    def show_menu( self ):
        ok = True

        """ ARTE PLUS """
        _add_to_index(context = self.PARAM_ARTE_PLUS, name = __language__ ( 30003 ) )

        """ ARTE PROGRAMMES """
        _add_to_index(context = self.PARAM_ARTE_PROGRAMMES, name = __language__ ( 30007 ) )

        """ ARTE EVENTS """
        _add_to_index(context = self.PARAM_ARTE_EVENT, name = __language__ ( 30005 ) )

        """ ARTE BONUS """
        _add_to_index(context = self.PARAM_ARTE_BONUS, name = __language__ ( 30006 ) )

        """ ARTE SEARCH """
        _add_to_index(context = self.PARAM_ARTE_SEARCH, name = __language__ ( 30001 ) )

        """ ARTE LIVE """
        _add_to_index(context = self.PARAM_ARTE_LIVE, name = __language__ ( 30004 ) )

        return ok

    def show_categories( self ):
        ok = True

        self.PARSER = self.retrieveParser( self.lang )
        self.PARSER.get_categories_list()

        for key,value in self.CATEGORIES.items(): 
            paramsAddons = {}
            paramsAddons[ self.PARAM_SHOW_CATEGORIE ]       = "True"
            paramsAddons[ self.PARAM_ARTE_CATEGORIE_KEY ]   = key.replace('&','brinbrin')
            paramsAddons[ self.PARAM_ARTE_CATEGORIE_VALUE ] = value
            paramsAddons[ self.PARAM_ARTE_CATEGORIE ]       = self.ARTE_CATEGORIE

            url = _create_param_url( paramsAddons )
            name = key.encode( 'utf-8' )
            _addDir( name = name, url = url )

        return ok

    def show_videos( self, videos ): 
        ok = True

        threads = []         
        for video in videos:
            aThread = Thread(target=self.updateVideosInfos, args=(video,))
            aThread.start()
            threads.append(aThread)
        
        for t in threads:
            t.join()

        if self.NEXT_PAGE_NUMBER :
            paramsAddons = {}
            paramsAddons[ self.PARAM_NEXT_PAGE ]            = "True"
            paramsAddons[ self.PARAM_NEXT_PAGE_NUMBER ]     = self.NEXT_PAGE_NUMBER
            paramsAddons[ self.PARAM_ARTE_CATEGORIE_VALUE ] = self.parameters[ self.PARAM_ARTE_CATEGORIE_VALUE ]

            url = _create_param_url( paramsAddons )
            name = __language__( 30302 )+" ("+self.NEXT_PAGE_NUMBER+")"
            _addDir( name = name, url = url )

        return ok

    def updateVideosInfos(self, video):
        name = strip_html( video.date + " - " + video.title )
        year = " "
        summary = strip_html( video.pitch.encode('utf-8') )
        genre = " "
        country = " "
        if isinstance( self.PARSER, PlusParser ) :
            infos = self.PARSER.fetch_summary(video.link)
            if infos[0] and infos[1] and infos[2]:
                try:
                    splitted_text = (infos[1][1:-1]).split(',')
                    year          = splitted_text[1].encode('utf-8')
                    country       = splitted_text[0].encode('utf-8')
                    genre         = infos[2].encode('utf-8')
                    summary       = infos[0].encode('utf-8')
		
                except Exception, why:
                    year    = " "
                    summary = " "
                    genre   = " "
                    country = " "
                    print "Erreur while getting video infos"
                    print_exc()

        infoLabels={ "Title": strip_html( video.title ), 
                     "Overlay": "", 
                     "Size": "", 
                     "Year": year, 
                     "Plot": strip_html( summary ), 
                     "PlotOutline": strip_html( video.pitch.encode('utf-8') ), 
                     "MPAA": "", 
                     "Genre": strip_html( genre ),
                     "Studio": "", 
                     "Country":country,
                     "Director": video.author, 
                     "Duration": video.duration,
                     "Cast": "",
                     "Date": video.date }

        c_items = self.createVideoContextMenu( video )
        paramsAddons = self.createParamsAddons( self.PARAM_PLAY_VIDEO, video )

        url = _create_param_url( paramsAddons )
        _addLink( name = name, url = url, iconimage = video.pix, itemInfoLabels = infoLabels, c_items = c_items )

    def retrieveVideoLink( self, link ):
        hd = None

        if isinstance( self.PARSER, LiveParser ) :
            links = self.PARSER.get_links( link )

            if links[ 'Live' ] is not None:
                #hd = links['Live']
                hd = None

            elif links[ 'HD' ] is not None and self.is_HD:
                hd = links[ 'HD' ]

            else :
                hd = links[ 'SD' ]

        else:
            hd, sd = self.PARSER.fetch_stream_links( link )
            if not self.is_HD:
                hd = sd
        return hd        

    def retrieveParser( self, lang ):
        parser = None

        if self.ARTE_CATEGORIE == self.PARAM_ARTE_EVENT:
            parser = EventParser( lang, self.CATEGORIES, self.VIDEOS )

        elif self.ARTE_CATEGORIE == self.PARAM_ARTE_BONUS:
            parser = BonusParser( lang, self.CATEGORIES, self.VIDEOS )

        elif self.ARTE_CATEGORIE == self.PARAM_ARTE_PROGRAMMES:
            parser = ProgrammesParser( lang, self.CATEGORIES, self.VIDEOS )

        elif self.ARTE_CATEGORIE == self.PARAM_ARTE_LIVE:
            parser = LiveParser( lang, self.CATEGORIES )

        elif self.ARTE_CATEGORIE == self.PARAM_ARTE_PLUS:
            parser = PlusParser( lang, self.VIDEOS )

        elif self.ARTE_CATEGORIE == self.PARAM_ARTE_SEARCH:
            parser = SearchParser( lang, self.VIDEOS )

        return parser

    def createParamsAddons( self, menuName, video ):
        paramsAddons = {}
        paramsAddons[ menuName ]  = "True"
        paramsAddons[ self.PARAM_ARTE_CATEGORIE ] = self.ARTE_CATEGORIE

        if self.ARTE_CATEGORIE == self.PARAM_ARTE_LIVE:
            paramsAddons[ self.PARAM_VIDEO_ID ] = str( video.order )

        else:
            paramsAddons[ self.PARAM_VIDEO_ID ] = video.link

        paramsAddons[ self.PARAM_VIDEO_NAME ] = strip_html( video.title )

        return paramsAddons

    def createVideoContextMenu( self, video ):
        cm = []

        #Information
        cm.append( ( __language__( 30103 ), "XBMC.Action(Info)" ) )

        #Téléchargement
        paramsAddonsContextMenu = self.createParamsAddons( self.PARAM_DOWNLOAD_VIDEO, video )
        url = _create_param_url( paramsAddonsContextMenu )
        cm.append( ( __language__( 30102 ) , "XBMC.PlayMedia(%s)" % ( url ) ) )
        
        return cm

    def downloadVideo( self, video ):
        ok = True

        my_downloader = downloader.SimpleDownloader()
        try:
            if my_downloader.isRTMPInstalled():
                url= video[ self.PARAM_VIDEO_ID ]

                if isinstance( self.PARSER, LiveParser ) :
                    hd, params = self.PARSER.decode_link( hd )

                    params[ "download_path" ] = self.DOWNLOADDIR
                    params[ "Title" ] = video[ self.PARAM_VIDEO_NAME ]
                    params[ "use_rtmpdump" ] = True

                else:
                    params = { "url": url,"download_path": self.DOWNLOADDIR , "Title": video[ self.PARAM_VIDEO_NAME ] }

                name = "%s.mp4" %( video[ self.PARAM_VIDEO_NAME ] )
                my_downloader.download( name, params, False )

            else:
                print( "You must install rtmpdump" )
                xbmc.executebuiltin( "XBMC.Notification(%s,%s)" %( "ERROR downloadVideo","You must install rtmpdump" ) )  

        except Exception,msg:
            print( "Error downloadVideo : %s", msg )
            print_exc()
            item = my_downloader._getNextItemFromQueue()

            if item is not None:
                (item_id, item) = item
                my_downloader._removeItemFromQueue( item_id )

            xbmc.executebuiltin( "XBMC.Notification(%s,%s)" %( "ERROR downloadVideo", msg ) )

        return ok
