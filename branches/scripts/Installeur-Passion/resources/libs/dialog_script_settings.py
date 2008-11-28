
#Modules general
import os
import sys
from collections import deque

#modules XBMC
import xbmc
import xbmcgui

#modules custom
from utilities import *

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
    FEED_LIMIT = _( 504 ).split( "|" )#[ "00", "5", "10", "25", "50", "100" ]

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
            self._set_controls_labels()
            self._set_controls_values()
            self._set_controls_visible()
        except:
            EXC_INFO( LOG_ERROR, sys.exc_info(), self )
            self._close_dialog()

    def _get_settings( self, defaults=False  ):
        """ reads settings """
        self.feed_limit = deque( self.FEED_LIMIT )
        self.skin_colours = getSkinColors()
        self.settings = Settings().get_settings( defaults=defaults )
        if defaults:
            xbmc.executebuiltin( "Skin.Reset(use_passion_custom_background)" )
            #solution temporaire questionne le user pour le background
            #la bonne solution serai que le bouton reset est ete activer et confirmer avec ok apres.
            custom_path = bool( xbmc.getInfoLabel( "Skin.String(passion_custom_background)" ) )
            if custom_path and xbmcgui.Dialog().yesno( _( 500 ), "Voulez vous effacer le chemin de l'arrire-plan?" ):
                xbmc.executebuiltin( "Skin.Reset(passion_custom_background)" )

    def _set_controls_labels( self ):
        # setlabel pour les controles du dialog qui a comme info exemple: id="100" et pour avoir son controle on fait un getControl( 100 )
        try:
            self.getControl( 101 ).setLabel( _( 499 ) % ( __version__, ) )
            self.getControl( 160 ).setLabel( _( 501 ) )
        except:
            EXC_INFO( LOG_ERROR, sys.exc_info(), self )

    def _set_controls_values( self ):
        xbmcgui.lock()
        try:
            # boutons pour la limitation des topics
            self._set_control_limit_feeds()
            # boutons pour la couleur du theme
            self._set_control_colors()
            #bouton pour activer desactiver la modification du fichier sources.xml
            #selon l'etat de self.settings[ "xbmc_xml_update" ], l'image du radiobutton sera blanc ou non visible
            self.getControl( 160 ).setSelected( self.settings[ "xbmc_xml_update" ] )
            # cache le bouton activer desactiver la modification du fichier sources.xml, sy la version d'xbmc est compatible atlantis
            atlantis = not bool( re.search( "\\b(pre-8.10|8.10)\\b", xbmc.getInfoLabel( "System.BuildVersion" ) ) )
            self.getControl( 160 ).setEnabled( atlantis )
            self.getControl( 160 ).setVisible( atlantis ) 
            #le bouton valider les changements ont le desactive, il va etre reactiver seulement s'il y a un changement dans les settings
            self.getControl( 300 ).setEnabled( False ) 
            #le bouton credits est desactiver, le temps d'implanter cette fonction
            self.getControl( 303 ).setEnabled( False ) 
            # boutons pour le web
            self._set_control_web_visibility()
        except:
            EXC_INFO( LOG_ERROR, sys.exc_info(), self )
        xbmcgui.unlock()

    def _set_control_web_visibility( self ):
        platform = os.environ.get( "OS", "xbox" )
        self.getControl( 250 ).setLabel( _( 518 ), label2=self.settings.get( "web_title", _( 506 ) ) )
        self.getControl( 250 ).setEnabled( ( platform in ( "win32", "linux" ) ) )
        self.getControl( 250 ).setVisible( ( platform in ( "win32", "linux" ) ) )
        self.getControl( 260 ).setSelected( self.settings[ "win32_exec_wait" ] )
        self.getControl( 260 ).setEnabled( bool( self.settings[ "web_navigator" ] ) )
        self.getControl( 260 ).setVisible( ( platform == "win32" ) )

    def _set_control_limit_feeds( self ):
        try:
            self.feeds_limit = self.settings[ "feeds_limit" ]
            if not self.feed_limit[ 0 ] == self.feeds_limit:
                self.feed_limit.rotate( -( int( self.FEED_LIMIT.index( self.feeds_limit ) ) ) )#+ 1 ) )
            limit = self.feed_limit[ 0 ]
            if limit == "00": limit = _( 503 )
            self.getControl( 140 ).setLabel( _( 502 ), label2=limit )
        except:
            self.getControl( 140 ).setLabel( _( 502 ), label2=_( 503 ) )

    def _get_default_hex_color( self ):
        try:
            default_hex_color = dict( self.skin_colours ).get( "default", "FFFFFFFF" )
        except:
            EXC_INFO( LOG_ERROR, sys.exc_info(), self )
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
                self.getControl( 130 ).setLabel( _( 505 ), label2=label2 )
            else:
                enable_control = True
        except:
            EXC_INFO( LOG_ERROR, sys.exc_info(), self )
            enable_control = True
        if enable_control:
            try:
                self.getControl( 131 ).setEnabled( 0 )
                self.getControl( 132 ).setEnabled( 0 )
            except:
                EXC_INFO( LOG_ERROR, sys.exc_info(), self )

    def _set_controls_visible( self ):
        """
        ici sa sert a rendre visible les controls qu'on veut voir 
        pour le moment il y a 1 parametre, donc les autres sont mis non visible
        pour le futur on pourra les activer au besoin et coder sa fonction
        penser a retirer les # de bouton_non_visible = [ 170, 180, 190, 200, 210, 220, 230, 240 ] par ordre de grandeur, suivant == 170
        """
        xbmcgui.lock()
        try:
            bouton_non_visible = [ 170, 180, 190, 200, 210, 220 ]#range( 170, 250, 10 )
            for control_id in bouton_non_visible:
                self.getControl( control_id ).setEnabled( False )
                self.getControl( control_id ).setVisible( False ) 
        except:
            EXC_INFO( LOG_ERROR, sys.exc_info(), self )
        xbmcgui.unlock()

    def onFocus( self, controlID ):
        #cette fonction n'est pas utiliser ici, mais dans les XML si besoin
        #Note: Mais il faut la declarer :)
        pass

    def onClick( self, controlID ):
        try:
            if controlID in ( 141, 142 ):
                self.toggle_feed_control( controlID )
            elif controlID in ( 131, 132 ):
                self.toggle_color_control( controlID )
            elif controlID == 160:
                #bouton pour activer desactiver la modification du fichier sources.xml
                self._set_xml_update()
            elif controlID == 300:
                #bouton ok on save les changements.
                self._save_settings()
            elif controlID == 301:
                # bouton annuler on ferme le dialog
                self._close_dialog()
            elif controlID == 302:
                #bouton reset settings, ont recup les settings par default
                self._get_defaults()
            elif controlID == 230:
                #bouton custom background a ete activer depuis le xml
                #balise utiliser: <onclick>Skin.ToggleSetting(use_passion_custom_background)</onclick>
                self.getControl( 300 ).setEnabled( True )
            elif controlID == 250:
                #bouton pour choisir le navigateur web
                self._set_web_navigator()
            elif controlID == 260:
                #bouton pour activer desactiver wait state win32 seulement
                self._set_wait_state()
            else:
                pass
        except:
            EXC_INFO( LOG_ERROR, sys.exc_info(), self )

    def _set_web_navigator( self ):
        web_navigator = set_web_navigator( self.settings[ "web_navigator" ] )
        if web_navigator:
            self.settings[ "web_title" ] = web_navigator[ 0 ]
            self.settings[ "web_navigator" ] = web_navigator[ 1 ]
            self.getControl( 250 ).setLabel( _( 518 ), label2=self.settings[ "web_title" ] )
            self.getControl( 260 ).setEnabled( True )
            self.getControl( 300 ).setEnabled( True )

    def _set_wait_state( self ):
        if not self.settings[ "win32_exec_wait" ]:
            #Active
            self.settings[ "win32_exec_wait" ] = True
        else:
            #Desactive
            self.settings[ "win32_exec_wait" ] = False
        self.getControl( 300 ).setEnabled( True )

    def _set_xml_update( self ):
        # fonction plus tres utile depuis xbmc atlantis
        if not self.settings[ "xbmc_xml_update" ]:
            #Active
            self.settings[ "xbmc_xml_update" ] = True
        else:
            #Desactive
            self.settings[ "xbmc_xml_update" ] = False
        self.getControl( 300 ).setEnabled( True )

    def toggle_feed_control( self, controlID ):
        try:
            try:
                if controlID == 141: self.feed_limit.rotate( 1 )
                elif controlID == 142: self.feed_limit.rotate( -1 )
            except: pass
            toggle_preset = False
            limit = self.feed_limit[ 0 ]
            try:
                if limit == "00": limit = _( 503 )
                self.getControl( 140 ).setLabel( _( 502 ), label2=limit )
                toggle_preset = True
            except: pass
            if toggle_preset:
                self.feeds_limit = limit
                self.settings[ "feeds_limit" ] = self.feeds_limit
                self.getControl( 300 ).setEnabled( True )
        except:
            EXC_INFO( LOG_ERROR, sys.exc_info(), self )

    def toggle_color_control( self, controlID ):
        try:
            try:
                if controlID == 131: self.colors_limit.rotate( 1 )
                elif controlID == 132: self.colors_limit.rotate( -1 )
            except: pass
            toggle_preset = False
            color_index = self.names_colors.index( self.colors_limit[ 0 ] )
            name_color = self.names_colors[ color_index ]
            try:
                label2 = add_pretty_color( name_color[ 0 ], color=name_color[ 1 ] )
                self.getControl( 130 ).setLabel( _( 505 ), label2=label2 )
                toggle_preset = True
            except: pass
            if toggle_preset:
                self.skin_colour_path = name_color[ 0 ]
                self.skin_colour = name_color[ 1 ]
                self.settings[ "skin_colours_path" ] = self.skin_colour_path
                self.settings[ "skin_colours" ] = self.skin_colour
                self.getControl( 300 ).setEnabled( True )
        except:
            EXC_INFO( LOG_ERROR, sys.exc_info(), self )

    def _save_settings( self ):
        """ save values settings """
        OK = Settings().save_settings( self.settings )
        self.mainwin.configManager.setXbmcXmlUpdate( self.settings[ "xbmc_xml_update" ] )
        self.mainwin._get_settings()
        self.mainwin._set_skin_colours()
        self._close_dialog( OK )

    def _get_defaults( self ):
        """ resets values to defaults """
        self._get_settings( defaults=True )
        self._set_controls_values()
        self.getControl( 300 ).setEnabled( True )

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
