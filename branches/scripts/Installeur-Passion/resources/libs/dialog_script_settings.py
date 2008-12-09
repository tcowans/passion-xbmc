
#Modules general
import os
import sys
from collections import deque

#modules XBMC
import xbmc
import xbmcgui

#modules custom
from utilities import *

#module logger
try:
    logger = sys.modules[ "__main__" ].logger
except:
    import script_log as logger


#REPERTOIRE RACINE ( default.py )
CWD = os.getcwd().rstrip( ";" )

#FONCTION POUR RECUPERER LES LABELS DE LA LANGUE.
_ = sys.modules[ "__main__" ].__language__

# script constants
__script__ = sys.modules[ "__main__" ].__script__
try: __svn_revision__ = sys.modules[ "__main__" ].__svn_revision__
except: __svn_revision__ = 0
if not __svn_revision__: __svn_revision__ = "0"
__version__ = "%s.%s" % ( sys.modules[ "__main__" ].__version__, __svn_revision__ )


class ScriptSettings( xbmcgui.WindowXMLDialog ):
    TOPIC_LIMIT = _( 504 ).split( "|" )#[ "00", "5", "10", "25", "50", "100" ]

    def __init__( self, *args, **kwargs ):
        xbmcgui.WindowXMLDialog.__init__( self, *args, **kwargs )
        # __init__ normal de python
        # On recupere le "self" de le fenetre principal pour benificier de ces variables.
        self.mainwin = kwargs[ "mainwin" ]
        self.use_custom_background = xbmc.getCondVisibility( "!Skin.HasSetting(use_passion_custom_background)" )

    def onInit( self ):
        # onInit est pour le windowXML seulement
        try:
            self._get_settings()
            self._set_skin_colours()
            self._set_controls_labels()
            self._set_controls_values()
            #self._set_controls_visible()
            # recupere la valeur sur le démarrage, utiliser pour rafraifir en temps reel, si l'etat est pas le meme 
            self.coulour_on_load = self.settings[ "skin_colours_path" ]
            self.rss_on_load = self.settings[ "rss_feed" ]
        except:
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )
            self._close_dialog()

    def _get_settings( self, defaults=False  ):
        """ reads settings """
        self.topic_limit = deque( self.TOPIC_LIMIT )
        self.skin_colours = getSkinColors()
        self.settings = Settings().get_settings( defaults=defaults )
        if defaults:
            xbmc.executebuiltin( "Skin.Reset(use_passion_custom_background)" )
            #solution temporaire questionne le user pour le background
            #la bonne solution serai que le bouton reset est ete activer et confirmer avec ok apres.
            custom_path = bool( xbmc.getInfoLabel( "Skin.String(passion_custom_background)" ) )
            if custom_path and xbmcgui.Dialog().yesno( _( 500 ), "Voulez vous effacer le chemin de l'arrire-plan?" ):
                xbmc.executebuiltin( "Skin.Reset(passion_custom_background)" )

    def _set_skin_colours( self ):
        try:
            xbmc.executebuiltin( "Skin.SetString(PassionSettingsColours,%s)" % ( self.settings[ "skin_colours_path" ], ) )
        except:
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )

    def _set_controls_labels( self ):
        # setlabel pour les controles du dialog qui a comme info exemple: id="100" et pour avoir son controle on fait un getControl( 100 )
        try:
            self.getControl( 99 ).setLabel( _( 499 ) % ( __version__, ) )
            #self.getControl( 130 ).setLabel( _( 501 ) )
        except:
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )

    def _set_controls_values( self ):
        xbmcgui.lock()
        try:
            #
            # boutons pour lflux rss
            self._set_control_rss_feeds()
            # boutons pour la couleur du theme
            self._set_control_colors()
            # boutons pour la limitation des topics
            self._set_control_limit_topics()
            # pour bouton activer desactiver la modification du fichier sources.xml, si la version d'xbmc est compatible atlantis
            #atlantis = not bool( re.search( "\\b(pre-8.10|8.10)\\b", xbmc.getInfoLabel( "System.BuildVersion" ) ) )
            #bouton pour activer desactiver la modification du fichier sources.xml
            #selon l'etat de self.settings[ "xbmc_xml_update" ], l'image du radiobutton sera blanc ou non visible
            self.getControl( 130 ).setSelected( self.settings[ "xbmc_xml_update" ] )#atlantis )
            #selon l'etat de self.settings[ "update_startup" ], l'image du radiobutton sera blanc ou non visible
            self.getControl( 140 ).setSelected( self.settings[ "update_startup" ] )
            #selon l'etat de self.settings[ "update_startup" ], l'image du radiobutton sera blanc ou non visible
            self.getControl( 150 ).setSelected( self.settings[ "script_debug" ] )
            #le bouton valider les changements ont le desactive, il va etre reactiver seulement s'il y a un changement dans les settings
            self.getControl( 80 ).setEnabled( False )
            #le bouton credits est desactiver, le temps d'implanter cette fonction
            #self.getControl( 40 ).setEnabled( False )
            # boutons pour le web
            self._set_control_web_visibility()
        except:
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )
        xbmcgui.unlock()

    def _set_control_web_visibility( self ):
        compatible = ( SYSTEM_PLATFORM in ( "windows", "linux", "osx" ) )
        web_title = self.settings.get( "web_title", "" ) or  _( 506 )
        self.getControl( 330 ).setLabel( _( 518 ), label2=web_title )
        self.getControl( 330 ).setEnabled( compatible )
        self.getControl( 330 ).setVisible( compatible )
        self.getControl( 340 ).setSelected( self.settings[ "win32_exec_wait" ] )
        self.getControl( 340 ).setEnabled( bool( self.settings[ "web_navigator" ] ) )

    def _set_control_limit_topics( self ):
        try:
            self.topics_limit = self.settings[ "topics_limit" ]
            if not self.topic_limit[ 0 ] == self.topics_limit:
                self.topic_limit.rotate( -( int( self.TOPIC_LIMIT.index( self.topics_limit ) ) ) )
            limit = self.topic_limit[ 0 ]
            if limit == "00": limit = _( 503 )
            self.getControl( 320 ).setLabel( _( 502 ), label2=limit )
        except:
            self.getControl( 320 ).setLabel( _( 502 ), label2=_( 503 ) )

    def _get_default_hex_color( self ):
        try:
            default_hex_color = dict( self.skin_colours ).get( "default", "FFFFFFFF" )
        except:
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )
            default_hex_color = "FFFFFFFF"
        return default_hex_color

    def _set_control_colors( self ):
        enable_control = False
        try:
            if self.skin_colours:
                self.names_colors = self.skin_colours
                self.colors_limit = deque( self.names_colors )

                self.skin_colour_path = self.settings[ "skin_colours_path" ]
                self.skin_colour = self.settings[ "skin_colours" ] or self._get_default_hex_color()

                if not self.names_colors[ 0 ] == self.skin_colour_path:
                    str_index = self.skin_colour_path, self.skin_colour
                    self.colors_limit.rotate( -( int( self.names_colors.index( str_index ) ) ) )

                label2 = add_pretty_color( self.skin_colour_path, color=self.skin_colour )
                self.getControl( 220 ).setLabel( _( 505 ), label2=label2 )
            else:
                enable_control = True
        except:
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )
            enable_control = True
        if enable_control:
            try:
                self.getControl( 200 ).setEnabled( 0 )
                self.getControl( 210 ).setEnabled( 0 )
            except:
                logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )

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
                self.getControl( 120 ).setLabel( _( 511 ), label2=label2 )
            else:
                enable_control = True
        except:
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )
            enable_control = True
        if enable_control:
            try:
                self.getControl( 100 ).setEnabled( 0 )
                self.getControl( 110 ).setEnabled( 0 )
            except:
                logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )

    def _set_controls_visible( self ):
        pass
        """
        ici sa sert a rendre visible les controls qu'on veut voir
        pour le moment il y a 1 parametre, donc les autres sont mis non visible
        pour le futur on pourra les activer au besoin et coder sa fonction
        penser a retirer les # de bouton_non_visible = [  ] par ordre de grandeur, suivant == ?
        """
        """
        xbmcgui.lock()
        try:
            #bouton_non_visible = [  ]
            #for control_id in bouton_non_visible:
            self.getControl( ).setEnabled( False )
            self.getControl( ).setVisible( False )
        except:
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )
        xbmcgui.unlock()
        """

    def onFocus( self, controlID ):
        #cette fonction n'est pas utiliser ici, mais dans les XML si besoin
        #Note: Mais il faut la declarer :)
        pass

    def onClick( self, controlID ):
        try:
            if controlID in ( 300, 310 ):
                self.toggle_topic_control( controlID )
            elif controlID in ( 200, 210 ):
                self.toggle_color_control( controlID )
            elif controlID in ( 100, 110 ):
                self.toggle_rss_control( controlID )
            elif controlID == 130:
                #bouton pour activer desactiver la modification du fichier sources.xml
                self._set_bool_setting( "xbmc_xml_update" )
            elif controlID == 140:
                #bouton pour activer desactiver la verification de la mise à jour au demarrage
                self._set_bool_setting( "update_startup" )
            elif controlID == 150:
                #bouton pour activer desactiver la mode debug du script seulement
                self._set_bool_setting( "script_debug" )
            elif controlID == 80:
                #bouton ok on save les changements.
                self._save_settings()
            elif controlID == 81:
                # bouton annuler on ferme le dialog
                self._close_dialog()
            elif controlID == 82:
                #bouton reset settings, ont recup les settings par default
                self._get_defaults()
            elif controlID == 230:
                #bouton custom background a ete activer depuis le xml
                #balise utiliser: <onclick>Skin.ToggleSetting(use_passion_custom_background)</onclick>
                self.getControl( 80 ).setEnabled( True )
            elif controlID == 330:
                #bouton pour choisir le navigateur web
                self._set_web_navigator()
            elif controlID == 340:
                #bouton pour activer desactiver wait state win32 seulement
                self._set_bool_setting( "win32_exec_wait" )
            else:
                pass
        except:
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )

    def _set_web_navigator( self ):
        web_navigator = set_web_navigator( self.settings[ "web_navigator" ] )
        if web_navigator:
            self.settings[ "web_title" ] = web_navigator[ 0 ]
            self.settings[ "web_navigator" ] = web_navigator[ 1 ]
            self.getControl( 330 ).setLabel( _( 518 ), label2=self.settings[ "web_title" ] )
            self.getControl( 340 ).setEnabled( True )
            self.getControl( 80 ).setEnabled( True )

    def _set_bool_setting( self, str_setting ):
        if not self.settings[ str_setting ]:
            #Active
            self.settings[ str_setting ] = True
        else:
            #Desactive
            self.settings[ str_setting ] = False
        self.getControl( 80 ).setEnabled( True )
        # delete le str
        del str_setting

    def toggle_rss_control( self, controlID ):
        try:
            try:
                if controlID == 100: self.url_set.rotate( 1 )
                elif controlID == 110: self.url_set.rotate( -1 )
            except: pass
            toggle_preset = False
            rss_id = self.url_set[ 0 ]
            try:
                label2 = self.rss_feeds.get( rss_id, {} ).get( "title", _( 506 ) )
                self.getControl( 120 ).setLabel( _( 511 ), label2=label2 )
                toggle_preset = True
            except: pass
            if toggle_preset:
                self.settings[ "rss_feed" ] = rss_id
                self.getControl( 80 ).setEnabled( True )
        except:
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )

    def toggle_topic_control( self, controlID ):
        try:
            try:
                if controlID == 300: self.topic_limit.rotate( 1 )
                elif controlID == 310: self.topic_limit.rotate( -1 )
            except: pass
            toggle_preset = False
            limit = self.topic_limit[ 0 ]
            try:
                if limit == "00": limit = _( 503 )
                self.getControl( 320 ).setLabel( _( 502 ), label2=limit )
                toggle_preset = True
            except: pass
            if toggle_preset:
                self.topics_limit = limit
                self.settings[ "topics_limit" ] = self.topics_limit
                self.getControl( 80 ).setEnabled( True )
        except:
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )

    def toggle_color_control( self, controlID ):
        try:
            try:
                if controlID == 200: self.colors_limit.rotate( 1 )
                elif controlID == 210: self.colors_limit.rotate( -1 )
            except: pass
            toggle_preset = False
            color_index = self.names_colors.index( self.colors_limit[ 0 ] )
            name_color = self.names_colors[ color_index ]
            try:
                label2 = add_pretty_color( name_color[ 0 ], color=name_color[ 1 ] )
                self.getControl( 220 ).setLabel( _( 505 ), label2=label2 )
                toggle_preset = True
            except: pass
            if toggle_preset:
                self.skin_colour_path = name_color[ 0 ]
                self.skin_colour = name_color[ 1 ]
                self.settings[ "skin_colours_path" ] = self.skin_colour_path
                self.settings[ "skin_colours" ] = self.skin_colour
                self.getControl( 80 ).setEnabled( True )
        except:
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )

    def _save_settings( self ):
        """ save values settings """
        OK = Settings().save_settings( self.settings )
        self.mainwin.configManager.setXbmcXmlUpdate( self.settings[ "xbmc_xml_update" ] )
        self.mainwin._get_settings()
        if self.rss_on_load != self.settings[ "rss_feed" ]:
            self.mainwin._start_rss_timer()
        if self.coulour_on_load != self.settings[ "skin_colours_path" ]:
            self.mainwin._set_skin_colours()
        self._close_dialog( OK )

    def _get_defaults( self ):
        """ resets values to defaults """
        self._get_settings( defaults=True )
        self._set_controls_values()
        self.getControl( 80 ).setEnabled( True )

    def onAction( self, action ):
        #( ACTION_PARENT_DIR, ACTION_PREVIOUS_MENU, ACTION_CONTEXT_MENU, )
        if action in ( 9, 10, 117 ): self._close_dialog()

    def _close_dialog( self, OK=False ):
        # verifie si l'option default a ete utilise, si oui remets l'etat du custom backgroung
        if not OK and ( self.use_custom_background != xbmc.getCondVisibility( "!Skin.HasSetting(use_passion_custom_background)" ) ):
            xbmc.executebuiltin( "Skin.ToggleSetting(use_passion_custom_background)" )
        xbmc.sleep( 100 )
        self.close()


def show_settings( mainwin ):
    file_xml = "passion-DialogScriptSettings.xml"
    #depuis la revision 14811 on a plus besoin de mettre le chemin complet, la racine suffit
    dir_path = CWD #xbmc.translatePath( os.path.join( CWD, "resources" ) )
    #recupere le nom du skin et si force_fallback est vrai, il va chercher les images du defaultSkin.
    current_skin, force_fallback = getUserSkin()

    w = ScriptSettings( file_xml, dir_path, current_skin, force_fallback, mainwin=mainwin )
    w.doModal()
    del w
