
#Modules general
import os
import sys

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
    def __init__( self, *args, **kwargs ):
        # __init__ normal de python
        # On recupere le "self" de le fenetre principal pour benificier de ces variables.
        self.mainwin = kwargs[ "mainwin" ]

    def onInit( self ):
        # onInit est pour le windowXML seulement
        self._get_settings()
        self._set_controls_labels()
        self._set_controls_values()
        self._set_controls_visible()

    def _get_settings( self ):
        # Get settings
        try:
            self.configManager = self.mainwin.configManager
            self.xbmcXmlUpdate  = self.configManager.getXbmcXmlUpdate()
        except:
            EXC_INFO( LOG_ERROR, sys.exc_info(), self )
            self._close_dialog()

    def _set_controls_labels( self ):
        # setlabel pour les controles du dialog qui a comme info exemple: id="100" et pour avoir son controle on fait un getControl( 100 )
        try:
            self.getControl( 101 ).setLabel( _( 32499 ) % ( __version__, ) )
            self.getControl( 100 ).setLabel( "%s - %s" % ( _( 32000 ), _( 32500 ), ) )
            self.getControl( 160 ).setLabel( _( 32501 ) )
        except:
            EXC_INFO( LOG_ERROR, sys.exc_info(), self )

    def _set_controls_values( self ):
        xbmcgui.lock()
        try:
            #bouton pour activer desactiver la modification du fichier sources.xml
            #selon l'etat de self.xbmcXmlUpdate, l'image du radiobutton sera blanc ou non visible
            self.getControl( 160 ).setSelected( self.xbmcXmlUpdate )
            #le bouton reset settings est desactiver, le temps d'implanter cette fonction
            self.getControl( 302 ).setEnabled( 0 )
            #le bouton credits est desactiver, le temps d'implanter cette fonction
            self.getControl( 303 ).setEnabled( 0 )
        except:
            EXC_INFO( LOG_ERROR, sys.exc_info(), self )
        xbmcgui.unlock()

    def _set_controls_visible( self ):
        """
        ici sa sert a rendre visible les controls qu'on veut voir 
        pour le moment il y a 1 parametre, donc les autres sont mis non visible
        pour le futur on pourra les activer au besoin et coder sa fonction
        penser a retirer les # de bouton_non_visible = [ 170, 180, 190, 200, 210, 220, 230, 240 ] par ordre de grandeur, suivant == 170
        """
        xbmcgui.lock()
        try:
            bouton_non_visible = [ 170, 180, 190, 200, 210, 220, 230, 240 ]#range( 170, 250, 10 )
            for control_id in bouton_non_visible:
                self.getControl( control_id ).setEnabled( False )
                self.getControl( control_id ).setVisible( False ) 
        except:
            EXC_INFO( LOG_ERROR, sys.exc_info(), self )
        xbmcgui.unlock()
        
    def onFocus( self, controlID ):
        #cette fonction n'est pas utiliser ici, mais dans les XML si besoin
        pass

    def onClick( self, controlID ):
        try:
            if controlID == 160:
                #bouton pour activer desactiver la modification du fichier sources.xml
                if not self.xbmcXmlUpdate: self.xbmcXmlUpdate = True #Activer
                else: self.xbmcXmlUpdate = False #Desactiver
            elif controlID == 300:
                #bouton ok on save les changements.
                self.configManager.setXbmcXmlUpdate( self.xbmcXmlUpdate )
                self._close_dialog()
            elif controlID == 301:
                # bouton annuler on ferme le dialog
                self._close_dialog()
            elif controlID == 302:
                #le bouton reset settings est desactiver, le temps d'implanter cette fonction
                #print "on reset tous les settings"
                pass
            else:
                pass
        except:
            EXC_INFO( LOG_ERROR, sys.exc_info(), self )

    def onAction( self, action ):
        #( ACTION_PARENT_DIR, ACTION_PREVIOUS_MENU, ACTION_CONTEXT_MENU, )
        if action in ( 9, 10, 117 ): self._close_dialog()

    def _close_dialog( self ):
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
