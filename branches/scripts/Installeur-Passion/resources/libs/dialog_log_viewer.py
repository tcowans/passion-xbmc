
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


class LogViewer( xbmcgui.WindowXMLDialog ):
    CONTROL_TEXT_BOX = 5

    def __init__( self, *args, **kwargs ):
        xbmcgui.WindowXMLDialog.__init__( self, *args, **kwargs )

    def onInit( self ):
        # onInit est pour le windowXML seulement
        self.text = "Output not available!"
        try:
            if xbmcgui.Dialog().yesno( "XBMC Output - Select your choice!", "[B]-A- : [/B]" + os.path.basename( LOG_SCRIPT ), "[B]-B- : [/B]xbmc.log", "", "[B]-A-[/B]", "[B]-B-[/B]" ):
                xbmc_log = os.path.join( XBMC_ROOT, "xbmc.log" )
                if not os.path.isfile( xbmc_log ):
                    xbmc_log = os.path.join( os.path.dirname( os.path.dirname( xbmc.translatePath( "T:\\" ) ) ), "xbmc.log" )
                if os.path.isfile( xbmc_log ):
                    self.text = file( xbmc_log, "r" ).read()
            else:
                self.text = file( LOG_SCRIPT, "r" ).read()
            self._set_controls_values()
        except:
            EXC_INFO( LOG_ERROR, sys.exc_info(), self )

    def _set_controls_values( self ):
        xbmcgui.lock()
        try:
            self.getControl( self.CONTROL_TEXT_BOX ).reset()
            self.getControl( self.CONTROL_TEXT_BOX ).setText( self.text )
        except:
            EXC_INFO( LOG_ERROR, sys.exc_info(), self )
            self._close_dialog()
        xbmcgui.unlock()

    def onFocus( self, controlID ):
        #cette fonction n'est pas utiliser ici, mais dans les XML si besoin
        #Note: Mais il faut la declarer :)
        pass

    def onClick( self, controlID ):
        pass

    def onAction( self, action ):
        #( ACTION_PARENT_DIR, ACTION_PREVIOUS_MENU, ACTION_CONTEXT_MENU, )
        if action in ( 9, 10, 117 ): self._close_dialog()

    def _close_dialog( self ):
        xbmc.sleep( 100 )
        self.close()


def show_log():
    file_xml = "DialogScriptInfo.xml" # ont va utiliser un xml qui se trouve dans le skin par defaut d'xbmc
    dir_path = CWD
    #recupere le nom du skin et si force_fallback est vrai, il va chercher les images du defaultSkin.
    current_skin, force_fallback = getUserSkin()

    w = LogViewer( file_xml, dir_path, current_skin, force_fallback )
    w.doModal()
    del w
