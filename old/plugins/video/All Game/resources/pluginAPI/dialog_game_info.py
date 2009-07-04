
import os
import sys
import urllib
import xbmc
import xbmcgui
import xbmcplugin

from re import search, sub

# set our thumbnail
g_thumbnail = xbmc.translatePath( xbmc.getInfoImage( "ListItem.Thumb" ) )

from etree_utilities import load_infos
from plugin_log import *


CWD = os.getcwd()#.rstrip( ";" )

_ = xbmc.getLocalizedString

DIALOG_PROGRESS = xbmcgui.DialogProgress()

PLUGIN_RUN_UNDER = sys.modules[ "__main__" ].PLUGIN_RUN_UNDER

GAMES_DIR_PATH = sys.modules[ "__main__" ].GAMES_DIR_PATH

THUMBNAILS_DIR_PATH = sys.modules[ "__main__" ].THUMBNAILS_DIR_PATH

TRAILERS_DIR_PATH = sys.modules[ "__main__" ].TRAILERS_DIR_PATH


def color_matches_words( name, text, text2="", color="d0ffff00" ):
    # used with trailers, but not great work
    for word in name.split( " " ):
        by = "[COLOR=%s]%s[/COLOR]" % ( color, word, )
        w = "\\b(%s)\\b" % ( word, )#word.title(), word.lower(), word.upper(), )
        text = sub( w, by, text )
        text2 = sub( w, by, text2 )
        del w, by, word
    return text, text2


def getUserSkin():
    current_skin = xbmc.getSkinDir()
    force_fallback = os.path.exists( os.path.join( CWD, "resources", "skins", current_skin ) )
    if not force_fallback: current_skin = "Default"
    return current_skin, force_fallback


class pDialogCanceled( Exception ):
    def __init__( self, errmsg="Downloading was canceled by user!" ):
        self.msg = errmsg


class LIST_CONTAINER_150( dict ):
    def __init__( self ):
        self[ 1 ]  = "ID", "Game ID:"
        self[ 2 ]  = "platform", "Platform:"
        self[ 3 ]  = "amg_rating", "AMG Rating:"
        self[ 4 ]  = "esrb_rating", "ESRB Rating:"
        self[ 5 ]  = "genre", "Genre:"
        self[ 6 ]  = "style", "Styles:"
        self[ 7 ]  = "number_players", "Players:"#"Number of Players:"
        self[ 8 ]  = "developer", "Developer:"
        self[ 9 ]  = "publisher", "Publisher:"
        #self[ 10 ] = "year", "Release Date:"
        self[ 10 ] = "release_date", "Release Date:"
        self[ 11 ] = "cabinet_style", "Cabinet Style:"
        self[ 12 ] = "controls", "Controls:"
        self[ 13 ] = "flags", "Flags:"
        self[ 14 ] = "warnings", "Warnings:"
        self[ 15 ] = "supports", "Supports:"
        self[ 16 ] = "included_package", "Included Package:"
        self[ 17 ] = "support_email", "Support E-Mail:"
        self[ 18 ] = "support_url", "Support URL:"
        self[ 19 ] = "support_phone", "Support Phone:"


class ContextMenu( xbmcgui.WindowXMLDialog ):
    def __init__( self, *args, **kwargs ):
        self.selected = 0
        self.mainwin = kwargs[ "mainwin" ]
        self.local_trailer = kwargs.get( "local_trailer", True )
        self.watched = ( "watched", "" )[ xbmc.getInfoLabel( 'Container(232).ListItem.Property(OverlayWatched)' ) != "" ]

    def onInit( self ):
        xbmcgui.lock()
        try:
            # 05-011-08: deactivate "playing now...", because on retour dialog game info XBMC FREEZE.....
            self.getControl( 1002 ).setVisible( False )#bool( xbmc.PlayList( xbmc.PLAYLIST_VIDEO ).size() ) )

            #self.getControl( 1003 ).setVisible( not self.local_trailer )
            if self.local_trailer:
                self.getControl( 1003 ).setLabel( self.mainwin.strings[ 30159 ] )

            self.getControl( 1004 ).setLabel( self.mainwin.strings[ 30160 ] )
            if not self.watched:
                self.getControl( 1004 ).setLabel( self.mainwin.strings[ 30161 ] )
        except:
            EXC_INFO( LOG_ERROR, sys.exc_info(), self )
        xbmcgui.unlock()

    def onFocus( self, controlID ):
        pass

    def onClick( self, controlID ):
        self.selected = controlID
        xbmc.sleep( 10 )
        self.close()

    def onAction( self, action ):
        if action in ( 9, 10, 117 ): self.close()


class GameInfo( xbmcgui.WindowXML ):#Dialog ):
    # we need to store the strings as they do not exists after the call to endOfDirector()
    # main strings
    strings = {}
    strings[ 30013 ] = xbmc.getLocalizedString( 30013 )
    for stringId in range( 30100, 30200 ):
        strings[ stringId ] = xbmc.getLocalizedString( stringId )

    # main Settings
    TRAILERS_SCRAPER = xbmcplugin.getSetting( "trailers_scraper" )
    MAXIMUM_TRAILERS = ( 0, 10, 50, 100, 200, 500, 1000, )[ int( xbmcplugin.getSetting( "max_trailer" ) ) ]
    #RECORD_PATH = xbmc.translatePath( xbmcplugin.getSetting( "download_path" ) )
    RECORD_PATH = xbmcplugin.getSetting( "download_path" )

    #set animated
    anime_dialog = bool( xbmc.getCondVisibility( "!Skin.HasSetting(animated_plugin_allgame)" ) )
    anime_setting = xbmcplugin.getSetting( "anime_dialog" ) == "true"
    if anime_setting and not anime_dialog:
        xbmc.executebuiltin( "Skin.Reset(animated_plugin_allgame)" )
    elif not anime_setting and anime_dialog:
        xbmc.executebuiltin( "Skin.ToggleSetting(animated_plugin_allgame)" )
    #else: print anime_setting, anime_dialog

    # end the directory (failed) since this does not fill a media list
    xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=False )

    #clear playlist on startup
    xbmc.PlayList( xbmc.PLAYLIST_VIDEO ).clear()

    def __init__( self, *args, **kwargs ):
        self.isStarted = False
        self._kwargs = kwargs
        self.label_button_160 = 1
        self.label_button_190 = 1
        skin_dir = xbmc.translatePath( os.path.join( args[ 1 ], "resources", "skins" ) )
        self.dir_rating = os.path.join( skin_dir, args[ 2 ], "media", "rating" )
        if not os.path.exists( self.dir_rating ):
            self.dir_rating = os.path.join( skin_dir, "Default", "media", "rating" )

    def trailer_exists( self, video ):
        local_video = ""
        try:
            name = os.path.basename( video ).replace( "gv.com", "" ).strip( "." )
            local_video = xbmc.makeLegalFilename( os.path.join( self.RECORD_PATH, name ) )
        except:
            EXC_INFO( LOG_ERROR, sys.exc_info(), self )
        return os.path.isfile( local_video ), local_video

    def setup_variables( self ):
        game_id = self._kwargs.get( "game_id" )
        platform = self._kwargs.get( "platform" )
        if game_id and platform:
            self.platform_games_dir_path = os.path.join( GAMES_DIR_PATH, platform.replace( "/", "_" ) )
            filename = os.path.join( self.platform_games_dir_path, "%s.xml" % ( game_id, ) )
            self.game_info = load_infos( filename )

    def onInit( self ):
        eval( LOG_SELF_FUNCTION )
        if not self.isStarted:
            #xbmcgui.lock()
            try:
                self.getControl( 100 ).setVisible( 0 ) # auto busy
                #xbmcgui.lock()
                self.setup_variables()
                self.set_controls_labels()
                self.group_list_set_visibility()
                self.set_list_container_150()
                #xbmcgui.unlock()
                self.set_plot_and_review()
                self.set_list_container_181()
                self.set_credits_and_extra()
                self.set_list_container_201()
                self.set_esrb_rating_image()
                self.set_panel_container_221()
                self.set_cover_image()
                self.getControl( 100 ).setVisible( 1 ) # auto remove busy
            except:
                LOG( LOG_ERROR, "Game Info: [%s -> %s]", self._kwargs.get( "game_id" ), self._kwargs.get( "platform" ) )
                EXC_INFO( LOG_ERROR, sys.exc_info(), self )
                #xbmcgui.unlock()
                self.close()
            #xbmcgui.unlock()
        self.isStarted = True

    def set_controls_labels( self ):
        self.getControl( 1 ).setLabel( self.strings[ 30100 ] )
        self.getControl( 110 ).setLabel( self.game_info.findtext( "title" ) )
        self.getControl( 160 ).setLabel( self.strings[ 30126 ] )
        self.getControl( 190 ).setLabel( self.strings[ 30128 ] )
        self.getControl( 170 ).setLabel( self.strings[ 30129 ] )
        self.getControl( 180 ).setLabel( self.strings[ 30112 ].strip( ":" ) )
        self.getControl( 200 ).setLabel( self.strings[ 30130 ] )
        self.getControl( 210 ).setLabel( self.strings[ 30131 ] )
        self.getControl( 220 ).setLabel( self.strings[ 30132 ] )
        self.getControl( 230 ).setLabel( self.strings[ 30133 ] )
        self.getControl( 231 ).setLabel( self.strings[ 30138 ] )

    def get_thumbnail( self, online_tbn, dir_name="" ):
        if not online_tbn.startswith( "http://" ): return ""
        ext = online_tbn.rsplit( "." )[ -1 ]
        cached_thumb = xbmc.getCacheThumbName( online_tbn ).replace( "tbn", ext )
        cover_image = os.path.join( THUMBNAILS_DIR_PATH, dir_name, cached_thumb[ 0 ], cached_thumb )
        if not os.path.isfile( cover_image ):
            try:
                if not os.path.isdir( os.path.dirname( cover_image ) ):
                    os.makedirs( os.path.dirname( cover_image ) )
                fp, h = urllib.urlretrieve( online_tbn, cover_image )
                try:
                    if "text" in h[ "Content-Type" ]: os.unlink( cover_image )
                except: pass
            except:
                EXC_INFO( LOG_ERROR, sys.exc_info(), self )
                cover_image = online_tbn
        return cover_image

    def set_esrb_rating_image( self ):
        #eval( LOG_SELF_FUNCTION )
        esrb_rating_img = self.game_info.findtext( "esrb_rating_img" )
        if esrb_rating_img:
            esrb_thumb = self.get_thumbnail( esrb_rating_img, "esrb" )
            if os.path.isfile( esrb_thumb ):
                self.getControl( 102 ).setImage( esrb_thumb )

    def set_cover_image( self ):
        #eval( LOG_SELF_FUNCTION )
        online_tbn = self.game_info.findtext( "tbn" )
        if online_tbn and not os.path.isfile( g_thumbnail ) and g_thumbnail != "DefaultProgramBig.png":
            cover_image = self.get_thumbnail( online_tbn )
        else:
            cover_image = g_thumbnail
        if os.path.isfile( cover_image ) or ( g_thumbnail == "DefaultProgramBig.png" ):
            self.getControl( 100 ).setImage( cover_image )
            self.getControl( 101 ).setImage( cover_image )
            #for my OLD TV dim white color. :( my tv not like white. frostbox
            if ( "88b9f2ef" in cover_image ):# or online_tbn.endswith( "nogame_large.gif" ):
                self.getControl( 100 ).setColorDiffuse('0x70FFFFFF')
                self.getControl( 101 ).setColorDiffuse('0x80FFFFFF')

    def group_list_set_visibility( self ):
        #eval( LOG_SELF_FUNCTION )
        under_xbox = ( PLUGIN_RUN_UNDER == "xbox" ) and bool( self.game_info.findtext( "game_on_hdd" ) )
        self.getControl( 170 ).setVisible( under_xbox )
        self.getControl( 180 ).setVisible( bool( self.game_info.findtext( "controls_listed" ) ) )
        self.getControl( 200 ).setVisible( bool( self.game_info.findtext( "system_requirements" ) ) )
        self.getControl( 210 ).setVisible( bool( self.game_info.findtext( "game_buy" ) ) )
        self.getControl( 220 ).setVisible( bool( self.game_info.findtext( "screens" ) ) )

    def set_list_container_150( self ):
        #eval( LOG_SELF_FUNCTION )
        list_container = sorted( LIST_CONTAINER_150().items(), key=lambda id: id[ 0 ] )
        for key, value in list_container:
            label1 = self.strings[ ( 30100 + key ) ]
            text = self.game_info.findtext( value[ 0 ] )
            if ( not text and ( value[ 0 ] == "release_date" ) ):
                text = self.game_info.findtext( "year" )
            if ( text and ( value[ 0 ] == "amg_rating" ) ):
                rate = os.path.join( self.dir_rating, "%s.png" % ( text, ) )
                if os.path.isfile( rate ):
                    text = ""
                    self.getControl( 150 ).addItem( xbmcgui.ListItem( label1, text, "", rate ) )
            if text: self.getControl( 150 ).addItem( xbmcgui.ListItem( label1, text, "", "" ) )

    def set_plot_and_review( self ):
        #eval( LOG_SELF_FUNCTION )
        self.getControl( 161 ).reset()
        self.getControl( 162 ).reset()

        self.review = self.game_info.findtext( "review" )
        if self.review: self.getControl( 162 ).setText( self.review )
        else: self.getControl( 160 ).setLabel( self.strings[ 30125 ] )
        self.getControl( 162 ).setVisible( False )

        self.plot = self.game_info.findtext( "synopsis" )
        if self.plot: self.getControl( 161 ).setText( self.plot )
        else: self.getControl( 161 ).setVisible( False )

        if not self.plot and not self.review:
            self.getControl( 160 ).setVisible( False )
        if not self.plot and self.review:
            self.getControl( 162 ).setVisible( True )

    def set_list_container_181( self ):
        #eval( LOG_SELF_FUNCTION )
        controls_listed = self.game_info.findtext( "controls_listed" )
        if controls_listed:
            for control in eval( controls_listed ):
                heading = control[ 0 ]
                if heading: self.getControl( 181 ).addItem( xbmcgui.ListItem( "[B]%s[/B]" % ( heading, ), "", "", "" ) )
                for ctrl in control[ 1 ]:
                    self.getControl( 181 ).addItem( xbmcgui.ListItem( ctrl[ 0 ]+":", ctrl[ 1 ], "", "" ) )

    def set_credits_and_extra( self ):
        #eval( LOG_SELF_FUNCTION )
        self.credits_listed = self.game_info.findtext( "credits_listed" )
        if self.credits_listed:
            for credit in eval( self.credits_listed ):
                self.getControl( 191 ).addItem( xbmcgui.ListItem( credit[ 0 ]+":", credit[ 1 ], "", "" ) )
        else: self.getControl( 191 ).setVisible( False )

        self.getControl( 192 ).reset()
        self.extra_credits = self.game_info.findtext( "extra_credits" )
        if self.extra_credits: self.getControl( 192 ).setText( self.extra_credits )
        else: self.getControl( 190 ).setLabel( self.strings[ 30127 ] )
        self.getControl( 192 ).setVisible( False )

        if not self.credits_listed and not self.extra_credits:
            self.getControl( 190 ).setVisible( False )
        if not self.credits_listed and self.extra_credits:
            self.getControl( 192 ).setVisible( True )

    def set_list_container_201( self ):
        #eval( LOG_SELF_FUNCTION )
        system_requirements = self.game_info.findtext( "system_requirements" )
        if system_requirements:
            for required in eval( system_requirements ):
                heading = required[ 0 ]
                if heading: self.getControl( 201 ).addItem( xbmcgui.ListItem( "[B]%s[/B]" % ( heading, ), "", "", "" ) )
                for line in required[ 1 ]:
                    self.getControl( 201 ).addItem( xbmcgui.ListItem( line, "", "", "" ) )

    def set_panel_container_221( self ):
        #eval( LOG_SELF_FUNCTION )
        screens = self.game_info.findtext( "screens" )
        if screens:
            game_id = self.game_info.findtext( "ID" )
            for count, screen in enumerate( eval( screens ) ):
                thumb = self.get_thumbnail( screen, "screens" )
                if os.path.isfile( thumb ):
                    self.getControl( 221 ).addItem( xbmcgui.ListItem( "", "", "", thumb ) )

    def onFocus( self, controlID ):
        pass

    def onClick( self, controlID ):
        if controlID == 160:
            if self.review and self.label_button_160 == 1:
                self.label_button_160 = 0
                if self.plot:
                    self.getControl( 160 ).setLabel( self.strings[ 30125 ] )
                self.getControl( 161 ).setVisible( False )
                self.getControl( 162 ).setVisible( True )
            elif self.plot and self.label_button_160 == 0:
                self.label_button_160 = 1
                if self.review:
                    self.getControl( 160 ).setLabel( self.strings[ 30126 ] )
                self.getControl( 162 ).setVisible( False )
                self.getControl( 161 ).setVisible( True )
        elif controlID == 170:
            try: xbmc.executebuiltin('XBMC.RunXBE(%s)' % ( self.game_info.findtext( "game_on_hdd" ), ) )
            except: EXC_INFO( LOG_ERROR, sys.exc_info(), self )
            #else: self.close()
        elif controlID == 190:
            if self.extra_credits and self.label_button_190 == 1:
                self.label_button_190 = 0
                if self.credits_listed:
                    self.getControl( 190 ).setLabel( self.strings[ 30127 ] )
                self.getControl( 191 ).setVisible( False )
                self.getControl( 192 ).setVisible( True )
            elif self.credits_listed and self.label_button_190 == 0:
                self.label_button_190 = 1
                if self.extra_credits:
                    self.getControl( 190 ).setLabel( self.strings[ 30128 ] )
                self.getControl( 192 ).setVisible( False )
                self.getControl( 191 ).setVisible( True )
        elif controlID == 220:
            from plugin_slideshow import playSlideshow
            playSlideshow( eval( self.game_info.findtext( "screens" ) ) )
            del playSlideshow
            #self.close() if use dialog window only
        elif controlID == 221:
            #play single screen
            screens = self.game_info.findtext( "screens" )
            if screens:
                pos = self.getControl( 221 ).getSelectedPosition()
                if pos >= 0:
                    screen = eval( screens )[ pos ]
                    xbmc.executehttpapi( "ShowPicture(%s)" % ( screen, ) )
                    #self.close() if use dialog window only
        elif ( controlID == 230 ) and ( self.getControl( 232 ).size() == 0 ):
            game = self.set_list_container_232()
            LOG( LOG_INFO, "%i trailers found for %s" % ( self.getControl( 232 ).size(), game ) )
        elif controlID == 232:
            self.set_player_core_and_play()

    def set_player_core_and_play( self, selected="", video="" ):
        myPlayer = xbmc.Player()
        if selected:
            core = ( xbmc.PLAYER_CORE_MPLAYER, xbmc.PLAYER_CORE_DVDPLAYER, )[ selected - 1000 ]
            myPlayer = xbmc.Player( core )
        #play trailer
        playlist = self.set_playlist( video )
        if playlist and bool( xbmc.PlayList( xbmc.PLAYLIST_VIDEO ).size() ):
            myPlayer.play( playlist )
            self.getControl( 232 ).getSelectedItem().setProperty( "OverlayWatched", "watched" )
            #self.close() if use dialog window only

    def set_playlist( self, video="" ):
        playlist = None
        try:
            pos = self.getControl( 232 ).getSelectedPosition()
            if not video:
                video = self.trailers[ pos ][ "video" ]
                trailer_path =  self.trailer_exists( video )
                if trailer_path[ 0 ]: video = trailer_path[ 1 ]
            if video:
                item = self.trailers[ pos ]
                playlist = xbmc.PlayList( xbmc.PLAYLIST_VIDEO )
                thumb = self.get_thumbnail( item[ "thumb" ], "trailers" )
                listitem = xbmcgui.ListItem( item[ "label" ], item[ "label2" ], "defaultVideo.png", "defaultVideoBig.png" )
                listitem.setInfo( "video", { "Title": item[ "label" ], "Genre": self.strings[ 30133 ], "Studio": self.TRAILERS_SCRAPER } )
                if os.path.isfile( thumb ):
                    listitem.setIconImage( thumb )
                    listitem.setThumbnailImage( thumb )
                playlist.clear()
                playlist.add( video, listitem )
        except:
            EXC_INFO( LOG_ERROR, sys.exc_info(), self )
            playlist = None

        return playlist

    def onAction( self, action ):
        if action in ( 9, 10 ): self.close()
        try:
            if action == 117 and self.getFocusId() == 232:
                self.getControl( 232 ).getSelectedItem().select( True )
                self.show_context_menu()
                self.getControl( 232 ).getSelectedItem().select( False )
        except:
            #Throws: SystemError, on Internal error
            #RuntimeError, if no control has focus
            EXC_INFO( LOG_ERROR, sys.exc_info(), self )
        

    def show_context_menu( self ):
        try:
            item_selected = self.trailers[ self.getControl( 232 ).getSelectedPosition() ]
            if not item_selected[ "video" ]: return
            trailer_path = self.trailer_exists( item_selected[ "video" ] )
            file_xml = "PluginDialogContextMenu.xml"
            dir_path = CWD #xbmc.translatePath( os.path.join( CWD, "resources" ) )
            current_skin, force_fallback = getUserSkin()
            cm = ContextMenu( file_xml, dir_path, current_skin, force_fallback,
                mainwin=self, local_trailer=trailer_path[ 0 ] )
            cm.doModal()
            selected = cm.selected
            del cm
            if selected in ( 1000, 1001 ):
                self.set_player_core_and_play( selected )
            elif selected == 1002:
                # a built-in is automaticly exec in PluginDialogContextMenu.xml "<onclick>XBMC.ActivateWindow(videoplaylist)</onclick>"
                pass
            elif selected == 1003:
                #record
                if not trailer_path[ 0 ]:
                    video = self.dl_trailer( item_selected[ "label" ], item_selected[ "video" ], trailer_path[ 1 ] )
                    if video:
                        overlay_rar = ( "", "is_rar" )[ self.trailer_exists( item_selected[ "video" ] )[ 0 ] ]
                        self.getControl( 232 ).getSelectedItem().setProperty( "OverlayRAR", overlay_rar )
                else:
                    # remove trailer
                    video = trailer_path[ 1 ]
                    if xbmcgui.Dialog().yesno( _( 122 ), _( 125 ), item_selected[ "label" ] ):
                        LOG( LOG_NOTICE, "Removed Trailer by the user!" )
                        video = self._remove( video )
                        self.getControl( 232 ).getSelectedItem().setProperty( "OverlayRAR", "" )
                    video = ""
                if video:
                    self.set_player_core_and_play( video=video )
            elif selected == 1004:
                watched = ( "watched", "" )[ xbmc.getInfoLabel( 'Container(232).ListItem.Property(OverlayWatched)' ) != "" ]
                self.getControl( 232 ).getSelectedItem().setProperty( "OverlayWatched", watched )
                # future function mark watched or unwatched
        except:
            EXC_INFO( LOG_ERROR, sys.exc_info(), self )

    def set_list_container_232( self ):
        self.trailers = []
        game = self.game_info.findtext( "title" )
        cached_file = xbmc.getCacheThumbName( game ).replace( "tbn", "trailer" )
        filename = os.path.join( TRAILERS_DIR_PATH, cached_file[ 0 ], cached_file )

        DIALOG_PROGRESS.create( self.strings[ 30133 ], game )
        self.is_canceled = None
        if os.path.isfile( filename ) and not xbmcgui.Dialog().yesno( self.strings[ 30133 ], game, self.strings[ 30143 ], "", self.strings[ 30144 ], self.strings[ 30145 ] ):
            try:
                trailers_contents = eval( file( filename, "r" ).read() )
                total_trailers = len( trailers_contents )
                for count, contents in enumerate( trailers_contents ):
                    self.report( ( count + 1 ), total_trailers, contents[ "label" ], ispage=False, contents=contents )
                self.is_canceled = True
            except:
                EXC_INFO( LOG_ERROR, sys.exc_info(), self )
        if not self.is_canceled:
            try:
                #import scrapers.trailers.GameVideos.trailers_scraper as TRS
                exec "from scrapers.trailers.%s import trailers_scraper as TRS" % self.TRAILERS_SCRAPER
                self.tr = TRS
                TRS.IS_CANCELED = None
                TRS.MAXIMUM_TRAILERS = self.MAXIMUM_TRAILERS
                TRS.get_trailers( game, report_progress=self.report )
                self.is_canceled = TRS.IS_CANCELED
            except:
                EXC_INFO( LOG_ERROR, sys.exc_info(), self )

        if not self.trailers and self.is_canceled is None:
            self.getControl( 231 ).setLabel( "No trailers found!" )
        elif self.trailers:
            try:
                self.getControl( 231 ).setVisible( 0 )
                if not os.path.isdir( os.path.dirname( filename ) ):
                    os.makedirs( os.path.dirname( filename ) )
                file( filename, "w" ).write( repr( self.trailers ) )
            except:
                EXC_INFO( LOG_ERROR, sys.exc_info(), self )
        DIALOG_PROGRESS.close()
        return game

    def report( self, *args, **kwargs ):
        if ( DIALOG_PROGRESS.iscanceled() ):
            try: self.tr.IS_CANCELED = True
            except: self.is_canceled = True
        try:
            percent = int( ( 100.0 / args[ 1 ] ) * args[ 0 ] )
            if kwargs[ "ispage" ]:
                line1 = self.strings[ 30135 ] % ( args[ 0 ], args[ 1 ], )
                line2 = self.game_info.findtext( "title" )
            else:
                line1 = self.strings[ 30136 ] % ( args[ 0 ], args[ 1 ], )
                line2 = args[ 2 ] #self.strings[ 30137 ] + 
            DIALOG_PROGRESS.update( percent, line1, line2, "" )

            if kwargs.get( "contents" ):
                gamename = args[ 2 ]
                item = kwargs[ "contents" ]
                label, label2 = item[ "label" ], item[ "label2" ]
                if not item[ "video" ]:
                    label = "[COLOR=60d0d0d0]" + label + "[/COLOR]"
                    label2 = self.strings[ 30146 ]#"[COLOR=60d0d0d0]" + label2 + "[/COLOR]"
                #else:
                #    try: label, label2 = color_matches_words( gamename, label, label2 )
                #    except: EXC_INFO( LOG_ERROR, sys.exc_info(), self )
                thumb = self.get_thumbnail( item[ "thumb" ], "trailers" )
                listitem = xbmcgui.ListItem( label, label2, "defaultVideo.png", "defaultVideoBig.png" )
                if os.path.isfile( thumb ):
                    listitem.setIconImage( thumb )
                    listitem.setThumbnailImage( thumb )
                listitem.setInfo( type="video", infoLabels={ "duration": item.get( "duration", "" ) } )

                IS_HD = search( "\\b(HD|HDTV|HD-DVD|BR)\\b", label.upper() )
                overlay_hd = ( "", "is_hd" )[ IS_HD is not None ]
                listitem.setProperty( "OverlayHD", overlay_hd )

                overlay_rar = ( "", "is_rar" )[ self.trailer_exists( item[ "video" ] )[ 0 ] ]
                listitem.setProperty( "OverlayRAR", overlay_rar )
                listitem.setProperty( "OverlayWatched", ( "", "watched" )[ overlay_rar != "" ] )

                position = self.strings[ 30013 ] % ( args[ 0 ], args[ 1 ], )
                listitem.setProperty( "ItemPosition", position )

                listitem.select( False )
                self.getControl( 232 ).addItem( listitem )
                self.trailers.append( item )

            if ( self.getControl( 232 ).size() > 0 ): self.getControl( 231 ).setVisible( 0 )
        except:
            EXC_INFO( LOG_ERROR, sys.exc_info(), self )

    def dl_trailer( self, heading, url, destination ):
        eval( LOG_SELF_FUNCTION )
        DIALOG_PROGRESS.create( heading )
        try:
            def _report_hook( count, blocksize, totalsize ):
                _line3_ = ""
                if totalsize > 0:
                    _line3_ += _( 30141 ) % ( ( ( count * blocksize ) / 1024.0 / 1024.0 ), ( totalsize / 1024.0 / 1024.0  ), )
                else:
                    _line3_ += _( 30142 ) % ( ( ( count * blocksize ) / 1024.0 / 1024.0 ), )
                percent = int( float( count * blocksize * 100 ) / totalsize )
                strProgressBar = str( percent ) #xbmc.getInfoLabel( "System.Progressbar" )
                if ( percent <= 0 ) or not strProgressBar: strPercent = "0%"
                else: strPercent = "%s%%" % ( strProgressBar, )
                _line3_ += " | %s" % ( strPercent, )
                DIALOG_PROGRESS.update( percent, url, destination, _line3_ )
                if ( DIALOG_PROGRESS.iscanceled() ): raise pDialogCanceled()
            fp, h = urllib.urlretrieve( url, destination, _report_hook )
            if h:
                tab = "".rjust( 50 )
                LOG( LOG_INFO, "Infos of download: [%s -> %s]\n%s", url, fp,
                    tab + str( h ).strip( " \n\r" ).replace( "\r", "" ).replace( "\n", ( "\n" + tab ) ) )
            try:
                if "text" in h[ "Content-Type" ]: os.unlink( destination )
            except: pass
            filepath = fp
        except pDialogCanceled, error:
            LOG( LOG_WARNING, error.msg )
            filepath = self._remove( destination )
        except:
            EXC_INFO( LOG_ERROR, sys.exc_info(), self )
            filepath = self._remove( destination )
        DIALOG_PROGRESS.close()
        return filepath

    def _remove( self, filepath, remove_tries=3 ):
        eval( LOG_SELF_FUNCTION )
        urllib.urlcleanup()
        try:
            script = xbmc.translatePath( os.path.join( os.getcwd().rstrip( ";" ), "resources", "pluginAPI", "badfile.py" ) )
            url = "filepath=%s&&remove_tries=%i" % ( filepath, remove_tries )
            xbmc.executebuiltin( 'XBMC.RunScript(%s,%s)' % ( script, url, ) )
        except:
            EXC_INFO( LOG_ERROR, sys.exc_info(), self )
        return ""


def Main( game_id, platform ):
    file_xml = "DialogGameInfo.xml"
    dir_path = CWD #xbmc.translatePath( os.path.join( CWD, "resources" ) )
    current_skin, force_fallback = getUserSkin()

    w = GameInfo( file_xml, dir_path, current_skin, force_fallback, game_id=game_id, platform=platform )
    w.doModal()
    del w
