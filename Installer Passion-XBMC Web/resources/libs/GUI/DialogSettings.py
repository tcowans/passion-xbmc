
# Modules general
import os
import sys
from collections import deque
from traceback import print_exc

# Modules XBMC
import xbmc
import xbmcgui

# Modules custom
from utilities import *

# set our xbmc.settings path for xbmc get '/resources/settings.xml'
XBMC_SETTINGS = xbmc.Settings( os.getcwd() )


#FONCTION POUR RECUPERER LES LABELS DE LA LANGUE.
_ = sys.modules[ "__main__" ].__language__

# script constants
__script__ = sys.modules[ "__main__" ].__script__
__svn_revision__ = sys.modules[ "__main__" ].__svn_revision__ or "0"
__version__ = "%s.%s" % ( sys.modules[ "__main__" ].__version__, __svn_revision__ )


class ScriptSettings( xbmcgui.WindowXMLDialog ):
    TOPIC_LIMIT = [ "5", "10", "15", "20", "25", "50", "100" ] #_( 504 ).split( "|" ) #values[ "00", "5", "10", "25", "50", "100" ]
    TSIZE_LIMIT = [ "192", "256", "384", "512", "1024" ]

    # control id's
    CONTROL_OK_BUTTON             = 80
    CONTROL_CANCEL_BUTTON         = 81
    CONTROL_CANCEL2_BUTTON        = 303 # bouton mouse only
    CONTROL_RESET_BUTTON          = 82
    CONTROL_VERSION_LABEL         = 99
    CONTROL_XML_UPDATE_BUTTON     = 130
    CONTROL_UPDATE_STARTUP_BUTTON = 140
    CONTROL_SCRIPT_DEBUG_BUTTON   = 150
    CONTROL_PARENT_DIR_BUTTON     = 160
    CONTROL_EXTENTION_BUTTON      = 170
    CONTROL_SHOW_SPLASH_BUTTON    = 180
    CONTROL_DECREASE_COLOR_BUTTON = 200
    CONTROL_INCREASE_COLOR_BUTTON = 210
    CONTROL_SKIN_COLOR_LABEL      = 220
    CONTROL_CUSTOM_BG_BUTTON      = 230
    CONTROL_SHOW_FANART_BUTTON    = 250
    CONTROL_DECREASE_TSIZE_BUTTON = 260
    CONTROL_INCREASE_TSIZE_BUTTON = 270
    CONTROL_THUMB_SIZE_LABEL      = 280
    CONTROL_DECREASE_SKIN_BUTTON  = 290
    CONTROL_INCREASE_SKIN_BUTTON  = 291
    CONTROL_SKIN_LABEL            = 292
    CONTROL_DECREASE_RSS_BUTTON   = 100
    CONTROL_INCREASE_RSS_BUTTON   = 110
    CONTROL_RSS_FEEDS_LABEL       = 120
    CONTROL_DECREASE_TOPIC_BUTTON = 300
    CONTROL_INCREASE_TOPIC_BUTTON = 310
    CONTROL_LIMIT_TOPIC_LABEL     = 320
    CONTROL_HIDE_FORUM_BUTTON     = 350
    CONTROL_WEB_BUTTON            = 330
    CONTROL_WIN32_WAIT_BUTTON     = 340

    def __init__( self, *args, **kwargs ):
        xbmcgui.WindowXMLDialog.__init__( self, *args, **kwargs )
        # __init__ normal de python
        # On recupere le "self" de le fenetre principal pour benificier de ces variables.
        self.mainwin = kwargs[ "mainwin" ]
        self.reload_script = False

        # recupere la valeur sur le demarrage, utiliser pour rafraifir en temps reel, si l'etat est pas le meme
        self.passion_show_fanart = xbmc.getCondVisibility( "!Skin.HasSetting(PassionShowFanart)" )
        self.use_custom_background = xbmc.getCondVisibility( "!Skin.HasSetting(use_passion_custom_background)" )
        self.custom_background = unicode( xbmc.getInfoLabel( 'Skin.String(passion_custom_background)' ), 'utf-8')

    def onInit( self ):
        # onInit est pour le windowXML seulement
        try:
            self._get_settings()
            self._set_skin_colours()
            self._set_controls_labels()
            self._set_controls_values()

            # recupere la valeur sur le demarrage, utiliser pour rafraifir en temps reel, si l'etat est pas le meme
            self.coulour_on_load = self.settings[ "skin_colours_path" ]
            self.rss_on_load = self.settings[ "rss_feed" ]
            self.skin_on_load = self.settings.get( "current_skin", "Default" )
        except:
            print_exc()
            self._close_dialog()

    def _get_settings( self, defaults=False  ):
        """ reads settings """
        self.topic_limit = deque( self.TOPIC_LIMIT )
        self.skin_colours = getSkinColors()
        self.settings = Settings().get_settings( defaults=defaults )
        self.settings[ "script_debug" ] = ( XBMC_SETTINGS.getSetting( "script_debug" ) == "true" )
        if defaults:
            xbmc.executebuiltin( "Skin.Reset(use_passion_custom_background)" )
            xbmc.executebuiltin( "Skin.Reset(passion_custom_background)" )
            xbmc.executebuiltin( "Skin.Reset(PassionShowFanart)" )

    def _set_skin_colours( self ):
        #xbmcgui.lock()
        try:
            xbmc.executebuiltin( "Skin.SetString(PassionSkinColourPath,%s)" % ( self.settings[ "skin_colours_path" ], ) )
            xbmc.executebuiltin( "Skin.SetString(PassionSkinHexColour,%s)" % ( ( self.settings[ "skin_colours" ] or get_default_hex_color() ), ) )
        except:
            xbmc.executebuiltin( "Skin.SetString(PassionSkinHexColour,ffffffff)" )
            xbmc.executebuiltin( "Skin.SetString(PassionSkinColourPath,default)" )
            print_exc()
        #xbmcgui.unlock()

    def _set_controls_labels( self ):
        # setlabel pour les controles du dialog qui a comme info exemple: id="100" et pour avoir son controle on fait un getControl( 100 )
        try:
            self.getControl( self.CONTROL_VERSION_LABEL ).setLabel( _( 499 ) % ( __version__, ) )

            # Tab 'a propos'
            self.getControl( 601 ).reset()
            list_item = xbmcgui.ListItem( sys.modules[ "__main__" ].__version_l1__, sys.modules[ "__main__" ].__version_r1__ )
            self.getControl( 601 ).addItem( list_item )
            list_item = xbmcgui.ListItem( sys.modules[ "__main__" ].__version_l2__, sys.modules[ "__main__" ].__version_r2__ )
            self.getControl( 601 ).addItem( list_item )
            list_item = xbmcgui.ListItem( sys.modules[ "__main__" ].__version_l3__, sys.modules[ "__main__" ].__version_r3__ )
            self.getControl( 601 ).addItem( list_item )

            self.getControl( 602 ).reset()
            list_item = xbmcgui.ListItem( sys.modules[ "__main__" ].__credits_l1__, sys.modules[ "__main__" ].__credits_r1__ )
            self.getControl( 602 ).addItem( list_item )
            list_item = xbmcgui.ListItem( sys.modules[ "__main__" ].__credits_l2__, sys.modules[ "__main__" ].__credits_r2__ )
            self.getControl( 602 ).addItem( list_item )
            list_item = xbmcgui.ListItem( sys.modules[ "__main__" ].__credits_l3__, sys.modules[ "__main__" ].__credits_r3__ )
            self.getControl( 602 ).addItem( list_item )
            list_item = xbmcgui.ListItem( sys.modules[ "__main__" ].__credits_l4__, sys.modules[ "__main__" ].__credits_r4__ )
            self.getControl( 602 ).addItem( list_item )
        except:
            print_exc()

    def _set_controls_values( self ):
        xbmcgui.lock()
        try:
            self._set_control_skins()
            # boutons pour le flux rss
            self._set_control_rss_feeds()
            # boutons pour la couleur du theme
            self._set_control_colors()
            #boutons pour la taille des vignettes
            self._set_control_tbn_size()
            # boutons pour la limitation des topics
            self._set_control_limit_topics()
            # pour bouton activer desactiver la modification du fichier sources.xml, si la version d'xbmc est compatible atlantis
            #atlantis = not bool( re.search( "\\b(pre-8.10|8.10)\\b", xbmc.getInfoLabel( "System.BuildVersion" ) ) )
            #bouton pour activer desactiver la modification du fichier sources.xml
            #selon l'etat de self.settings[ "xbmc_xml_update" ], l'image du radiobutton sera blanc ou non visible
            self.getControl( self.CONTROL_XML_UPDATE_BUTTON ).setSelected( self.settings[ "xbmc_xml_update" ] )#atlantis )
            #selon l'etat de self.settings[ "update_startup" ], l'image du radiobutton sera blanc ou non visible
            self.getControl( self.CONTROL_UPDATE_STARTUP_BUTTON ).setSelected( self.settings[ "update_startup" ] )
            #selon l'etat de self.settings[ "script_debug" ], l'image du radiobutton sera blanc ou non visible
            self.getControl( self.CONTROL_SCRIPT_DEBUG_BUTTON ).setSelected( self.settings[ "script_debug" ] )
            #le bouton valider les changements ont le desactive, il va etre reactiver seulement s'il y a un changement dans les settings
            self.getControl( self.CONTROL_OK_BUTTON ).setEnabled( False )
            #selon l'etat de self.settings[ "hide_forum" ], l'image du radiobutton sera blanc ou non visible
            self.getControl( self.CONTROL_HIDE_FORUM_BUTTON ).setSelected( self.settings.get( "hide_forum", False ) )
            #selon l'etat de self.settings[ "pardir_not_hidden" ], l'image du radiobutton sera blanc ou non visible
            self.getControl( self.CONTROL_PARENT_DIR_BUTTON ).setSelected( not self.settings.get( "pardir_not_hidden", 1 ) )
            #selon l'etat de self.settings[ "hide_extention" ], l'image du radiobutton sera blanc ou non visible
            self.getControl( self.CONTROL_EXTENTION_BUTTON ).setSelected( self.settings.get( "hide_extention", True ) )
            #selon l'etat de self.settings[ "show_plash"], l'image du radiobutton sera blanc ou non visible
            self.getControl( self.CONTROL_SHOW_SPLASH_BUTTON ).setSelected( self.settings.get( "show_plash", False ) )
            # boutons pour le web
            self._set_control_web_visibility()
        except:
            print_exc()
        xbmcgui.unlock()

    def _set_control_skins( self ):
        try:
            self.current_skin  = self.settings.get( "current_skin", "Default" )
            self.skins_list         = sorted( getSkinsListing(), key=lambda l: l.lower() )
            self.skins_listing = deque( self.skins_list )
            if not self.current_skin in self.skins_list:
                self.current_skin = "Default"

            if not self.skins_listing[ 0 ] == self.current_skin:
                self.skins_listing.rotate( -( int( self.skins_list.index( self.current_skin ) ) ) )

            try: skin_label = "(%i/%i) %s" % ( self.skins_list.index( self.current_skin )+1, len( self.skins_list ), self.skins_listing[ 0 ], )
            except: skin_label = self.skins_listing[ 0 ]
            self.getControl( self.CONTROL_SKIN_LABEL ).setLabel( "Skin", label2=skin_label )
        except:
            print_exc()

    def _set_control_web_visibility( self ):
        compatible = ( SYSTEM_PLATFORM in ( "windows", "linux", "osx" ) )
        web_title = self.settings.get( "web_title", "" ) or  _( 506 )
        self.getControl( self.CONTROL_WEB_BUTTON ).setLabel( _( 518 ), label2=web_title )
        self.getControl( self.CONTROL_WEB_BUTTON ).setEnabled( compatible )
        self.getControl( self.CONTROL_WEB_BUTTON ).setVisible( compatible )
        self.getControl( self.CONTROL_WIN32_WAIT_BUTTON ).setSelected( self.settings[ "win32_exec_wait" ] )
        self.getControl( self.CONTROL_WIN32_WAIT_BUTTON ).setEnabled( bool( self.settings[ "web_navigator" ] ) )

    def _set_control_limit_topics( self ):
        try:
            self.topics_limit = self.settings[ "topics_limit" ]
            if not self.topic_limit[ 0 ] == self.topics_limit:
                self.topic_limit.rotate( -( int( self.TOPIC_LIMIT.index( self.topics_limit ) ) ) )
            limit = self.topic_limit[ 0 ]
            #if limit == "00": limit = _( 503 )
            self.getControl( self.CONTROL_LIMIT_TOPIC_LABEL ).setLabel( _( 502 ), label2=limit )
        except:
            self.getControl( self.CONTROL_LIMIT_TOPIC_LABEL ).setLabel( _( 502 ), label2=_( 503 ) )

    def _set_control_tbn_size( self ):
        try:
            self.thumb_size = self.settings[ "thumb_size" ]
            self.thumbs_size = deque( self.TSIZE_LIMIT )
            if not self.thumbs_size[ 0 ] == self.thumb_size:
                self.thumbs_size.rotate( -( int( self.TSIZE_LIMIT.index( self.thumb_size ) ) ) )
            limit = self.thumbs_size[ 0 ]
            self.getControl( self.CONTROL_THUMB_SIZE_LABEL ).setLabel( _( 517 ), label2=str( limit ) )
        except:
            print_exc()
            #default_thumb_size = self.settings.get( "thumb_size" ) or ( "512", "192" )[ ( SYSTEM_PLATFORM == "xbox" ) ]
            #self.getControl( self.CONTROL_THUMB_SIZE_LABEL ).setLabel( _( 517 ), label2=str( default_thumb_size ) )

    def _set_control_colors( self ):
        enable_control = False
        try:
            if self.skin_colours:
                self.names_colors = self.skin_colours
                self.colors_limit = deque( self.names_colors )

                self.skin_colour_path = self.settings[ "skin_colours_path" ]
                self.skin_colour = self.settings[ "skin_colours" ] or get_default_hex_color()

                if not self.names_colors[ 0 ] == self.skin_colour_path:
                    str_index = self.skin_colour_path, self.skin_colour
                    self.colors_limit.rotate( -( int( self.names_colors.index( str_index ) ) ) )

                label2 = add_pretty_color( self.skin_colour_path, color=self.skin_colour )
                self.getControl( self.CONTROL_SKIN_COLOR_LABEL ).setLabel( _( 505 ), label2=label2 )
            else:
                enable_control = True
        except:
            print_exc()
            enable_control = True
        if enable_control:
            try:
                self.getControl( self.CONTROL_DECREASE_COLOR_BUTTON ).setEnabled( 0 )
                self.getControl( self.CONTROL_INCREASE_COLOR_BUTTON ).setEnabled( 0 )
            except:
                print_exc()

    def _set_control_rss_feeds( self ):
        enable_control = False
        try:
            self.rss_feeds = parse_rss_xml()
            if self.rss_feeds:
                self.url_set = deque( sorted( self.rss_feeds.keys() + [ "0" ] ) )

                if not self.url_set[ 0 ] == self.settings[ "rss_feed" ]:
                    str_index = sorted( self.rss_feeds.keys() ).index( self.settings[ "rss_feed" ] )
                    self.url_set.rotate( -( int( str_index ) + 1 ) )

                label2 = self.rss_feeds.get( self.url_set[ 0 ], {} ).get( "title", _( 506 ) )
                self.getControl( self.CONTROL_RSS_FEEDS_LABEL ).setLabel( _( 511 ), label2=label2 )
            else:
                enable_control = True
        except:
            print_exc()
            enable_control = True
        if enable_control:
            try:
                self.getControl( self.CONTROL_DECREASE_RSS_BUTTON ).setEnabled( 0 )
                self.getControl( self.CONTROL_INCREASE_RSS_BUTTON ).setEnabled( 0 )
            except:
                print_exc()

    def onFocus( self, controlID ):
        #cette fonction n'est pas utiliser ici, mais dans les XML si besoin
        #Note: Mais il faut la declarer :)
        pass

    def toggle_skin_control( self, controlID ):
        try:
            try:
                if controlID == self.CONTROL_DECREASE_SKIN_BUTTON: self.skins_listing.rotate( 1 )
                elif controlID == self.CONTROL_INCREASE_SKIN_BUTTON: self.skins_listing.rotate( -1 )
            except: pass
            toggle_preset = False
            new_skin = self.skins_listing[ 0 ]
            try:
                try: skin_label = "(%i/%i) %s" % ( self.skins_list.index( new_skin )+1, len( self.skins_list ), new_skin, )
                except: skin_label = new_skin
                self.getControl( self.CONTROL_SKIN_LABEL ).setLabel( "Skin", label2=skin_label )
                toggle_preset = True
            except: pass
            if toggle_preset:
                self.current_skin = new_skin
                self.settings[ "current_skin" ] = self.current_skin
                self.getControl( self.CONTROL_OK_BUTTON ).setEnabled( True )
        except:
            print_exc()

    def onClick( self, controlID ):
        try:
            if controlID in ( self.CONTROL_DECREASE_SKIN_BUTTON, self.CONTROL_INCREASE_SKIN_BUTTON ):
                self.toggle_skin_control( controlID )

            elif controlID in ( self.CONTROL_DECREASE_TOPIC_BUTTON, self.CONTROL_INCREASE_TOPIC_BUTTON ):
                self.toggle_topic_control( controlID )

            elif controlID in ( self.CONTROL_DECREASE_COLOR_BUTTON, self.CONTROL_INCREASE_COLOR_BUTTON ):
                self.toggle_color_control( controlID )

            elif controlID in ( self.CONTROL_DECREASE_RSS_BUTTON, self.CONTROL_INCREASE_RSS_BUTTON ):
                self.toggle_rss_control( controlID )

            elif controlID in ( self.CONTROL_DECREASE_TSIZE_BUTTON, self.CONTROL_INCREASE_TSIZE_BUTTON ):
                self.toggle_tbn_size_control( controlID )

            elif controlID == self.CONTROL_SHOW_SPLASH_BUTTON:
                #bouton pour activer desactiver le spalsh
                self._set_bool_setting( "show_plash" )

            elif controlID == self.CONTROL_PARENT_DIR_BUTTON:
                #bouton pour activer desactiver le repertoire parent dans les listes
                self._set_bool_setting( "pardir_not_hidden" )

            elif controlID == self.CONTROL_EXTENTION_BUTTON:
                #bouton pour activer desactiver les extentions dans les noms des items
                self._set_bool_setting( "hide_extention" )

            elif controlID == self.CONTROL_XML_UPDATE_BUTTON:
                #bouton pour activer desactiver la modification du fichier sources.xml
                self._set_bool_setting( "xbmc_xml_update" )

            elif controlID == self.CONTROL_UPDATE_STARTUP_BUTTON:
                #bouton pour activer desactiver la verification de la mise a jour au demarrage
                self._set_bool_setting( "update_startup" )

            elif controlID == self.CONTROL_SCRIPT_DEBUG_BUTTON:
                #bouton pour activer desactiver la mode debug du script seulement
                self._set_bool_setting( "script_debug" )

            elif controlID == self.CONTROL_OK_BUTTON:
                #bouton ok on save les changements.
                self._save_settings()

            elif controlID in ( self.CONTROL_CANCEL_BUTTON, self.CONTROL_CANCEL2_BUTTON ):
                # bouton annuler on ferme le dialog
                self._close_dialog()

            elif controlID == self.CONTROL_RESET_BUTTON:
                #bouton reset settings, ont recup les settings par default
                self._get_defaults()

            elif controlID == self.CONTROL_SHOW_FANART_BUTTON:
                #bouton fanart background a ete activer depuis le xml
                #balise utiliser: <onclick>Skin.ToggleSetting(PassionShowFanart)</onclick>
                self.getControl( self.CONTROL_OK_BUTTON ).setEnabled( True )

            elif controlID == self.CONTROL_CUSTOM_BG_BUTTON:
                #bouton custom background a ete activer depuis le xml
                #balise utiliser: <onclick>Skin.ToggleSetting(use_passion_custom_background)</onclick>
                self.getControl( self.CONTROL_OK_BUTTON ).setEnabled( True )

            elif controlID == self.CONTROL_HIDE_FORUM_BUTTON:
                #bouton pour masquer le bouton forum du menu principal
                self._set_bool_setting( "hide_forum" )

            elif controlID == self.CONTROL_WEB_BUTTON:
                #bouton pour choisir le navigateur web
                self._set_web_navigator()

            elif controlID == self.CONTROL_WIN32_WAIT_BUTTON:
                #bouton pour activer desactiver wait state win32 seulement
                self._set_bool_setting( "win32_exec_wait" )
            else:
                pass
        except:
            print_exc()

    def _set_web_navigator( self ):
        web_navigator = set_web_navigator( self.settings[ "web_navigator" ] )
        if web_navigator:
            self.settings[ "web_title" ] = web_navigator[ 0 ]
            self.settings[ "web_navigator" ] = web_navigator[ 1 ]
            self.getControl( self.CONTROL_WEB_BUTTON ).setLabel( _( 518 ), label2=self.settings[ "web_title" ] )
            self.getControl( self.CONTROL_WIN32_WAIT_BUTTON ).setEnabled( True )
            self.getControl( self.CONTROL_OK_BUTTON ).setEnabled( True )

    def _set_bool_setting( self, str_setting ):
        if not self.settings[ str_setting ]:
            #Active
            self.settings[ str_setting ] = True
        else:
            #Desactive
            self.settings[ str_setting ] = False
        self.getControl( self.CONTROL_OK_BUTTON ).setEnabled( True )
        # delete le str
        del str_setting

    def toggle_rss_control( self, controlID ):
        try:
            try:
                if controlID == self.CONTROL_DECREASE_RSS_BUTTON: self.url_set.rotate( 1 )
                elif controlID == self.CONTROL_INCREASE_RSS_BUTTON: self.url_set.rotate( -1 )
            except: pass
            toggle_preset = False
            rss_id = self.url_set[ 0 ]
            try:
                label2 = self.rss_feeds.get( rss_id, {} ).get( "title", _( 506 ) )
                self.getControl( self.CONTROL_RSS_FEEDS_LABEL ).setLabel( _( 511 ), label2=label2 )
                toggle_preset = True
            except: pass
            if toggle_preset:
                self.settings[ "rss_feed" ] = rss_id
                self.getControl( self.CONTROL_OK_BUTTON ).setEnabled( True )
        except:
            print_exc()

    def toggle_topic_control( self, controlID ):
        try:
            try:
                if controlID == self.CONTROL_DECREASE_TOPIC_BUTTON: self.topic_limit.rotate( 1 )
                elif controlID == self.CONTROL_INCREASE_TOPIC_BUTTON: self.topic_limit.rotate( -1 )
            except: pass
            toggle_preset = False
            limit = self.topic_limit[ 0 ]
            try:
                #if limit == "00": limit = _( 503 )
                self.getControl( self.CONTROL_LIMIT_TOPIC_LABEL ).setLabel( _( 502 ), label2=limit )
                toggle_preset = True
            except: pass
            if toggle_preset:
                self.topics_limit = limit
                self.settings[ "topics_limit" ] = self.topics_limit
                self.getControl( self.CONTROL_OK_BUTTON ).setEnabled( True )
        except:
            print_exc()

    def toggle_tbn_size_control( self, controlID ):
        try:
            try:
                if controlID == self.CONTROL_DECREASE_TSIZE_BUTTON: self.thumbs_size.rotate( 1 )
                elif controlID == self.CONTROL_INCREASE_TSIZE_BUTTON: self.thumbs_size.rotate( -1 )
            except: pass
            toggle_preset = False
            limit = self.thumbs_size[ 0 ]
            try:
                self.getControl( self.CONTROL_THUMB_SIZE_LABEL ).setLabel( _( 517 ), label2=str( limit ) )
                toggle_preset = True
            except: pass
            if toggle_preset:
                self.thumb_size = limit
                self.settings[ "thumb_size" ] = self.thumb_size
                self.getControl( self.CONTROL_OK_BUTTON ).setEnabled( True )
        except:
            print_exc()

    def toggle_color_control( self, controlID ):
        try:
            try:
                if controlID == self.CONTROL_DECREASE_COLOR_BUTTON: self.colors_limit.rotate( 1 )
                elif controlID == self.CONTROL_INCREASE_COLOR_BUTTON: self.colors_limit.rotate( -1 )
            except: pass
            toggle_preset = False
            color_index = self.names_colors.index( self.colors_limit[ 0 ] )
            name_color = self.names_colors[ color_index ]
            try:
                label2 = add_pretty_color( name_color[ 0 ], color=name_color[ 1 ] )
                self.getControl( self.CONTROL_SKIN_COLOR_LABEL ).setLabel( _( 505 ), label2=label2 )
                toggle_preset = True
            except: pass
            if toggle_preset:
                self.skin_colour_path = name_color[ 0 ]
                self.skin_colour = name_color[ 1 ]
                self.settings[ "skin_colours_path" ] = self.skin_colour_path
                self.settings[ "skin_colours" ] = self.skin_colour
                self.getControl( self.CONTROL_OK_BUTTON ).setEnabled( True )
        except:
            print_exc()

    def _save_settings( self ):
        """ save values settings """
        OK = Settings().save_settings( self.settings )
        self.mainwin._get_settings()
        if self.rss_on_load != self.settings[ "rss_feed" ]:
            self.mainwin._start_rss_timer()
        if self.coulour_on_load != self.settings[ "skin_colours_path" ]:
            self.mainwin._set_skin_colours()
        if self.skin_on_load != self.settings.get( "current_skin", "Default" ):
            #required script reload
            if xbmcgui.Dialog().yesno( _( 532 ), _( 533 ), _( 534 ) ):
                self.reload_script = True
        XBMC_SETTINGS.setSetting( "script_debug", repr( self.settings[ "script_debug" ] ).lower() )
        self._close_dialog( OK )

    def _get_defaults( self ):
        """ resets values to defaults """
        self._get_settings( defaults=True )
        self._set_controls_values()
        self.getControl( self.CONTROL_OK_BUTTON ).setEnabled( True )

    def onAction( self, action ):
        #( ACTION_PARENT_DIR, ACTION_PREVIOUS_MENU, ACTION_CONTEXT_MENU, )
        if action in ( 9, 10, 117 ): self._close_dialog()

    def _close_dialog( self, OK=False ):
        # verifie si l'option default a ete utilise, si oui remets l'etat du custom backgroung
        if not OK:
            if ( self.passion_show_fanart != xbmc.getCondVisibility( "!Skin.HasSetting(PassionShowFanart)" ) ):
                xbmc.executebuiltin( "Skin.ToggleSetting(PassionShowFanart)" )
            if ( self.use_custom_background != xbmc.getCondVisibility( "!Skin.HasSetting(use_passion_custom_background)" ) ):
                xbmc.executebuiltin( "Skin.ToggleSetting(use_passion_custom_background)" )
            if ( self.custom_background != unicode( xbmc.getInfoLabel( 'Skin.String(passion_custom_background)' ), 'utf-8') ):
                xbmc.executebuiltin( "Skin.SetString(passion_custom_background,%s)" % ( self.custom_background, ) )

        xbmc.sleep( 100 )
        self.close()
        if self.reload_script:
            self.mainwin._close_script()
            sys.modules[ "__main__" ].MAIN()
        sys.modules[ "__main__" ].output.PRINT_DEBUG = ( XBMC_SETTINGS.getSetting( "script_debug" ) == "true" )


def show_settings( mainwin ):
    file_xml = "passion-DialogScriptSettings.xml"
    #depuis la revision 14811 on a plus besoin de mettre le chemin complet, la racine suffit
    dir_path = os.getcwd().rstrip( ";" )
    #recupere le nom du skin et si force_fallback est vrai, il va chercher les images du defaultSkin.
    current_skin, force_fallback = getUserSkin()

    w = ScriptSettings( file_xml, dir_path, current_skin, force_fallback, mainwin=mainwin )
    w.doModal()
    del w
