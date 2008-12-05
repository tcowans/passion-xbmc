
#Modules general
import os
import re
import sys

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

DIALOG_PROGRESS = xbmcgui.DialogProgress()


# Set WindowXMLDialog if not current skin is Project Mayhem III
WIN_XML = ( "xbmcgui.WindowXMLDialog", "xbmcgui.WindowXML", )[ ( xbmc.getSkinDir() == "Project Mayhem III" ) ]

class LogViewer( eval( WIN_XML ) ):
    CONTROL_TEXT_BOX = 5

    COLOR_ERROR   = "[COLOR=FFFF0000]ERROR[/COLOR]"
    COLOR_WARNING = "[COLOR=FFFFFF3D]WARNING[/COLOR]"
    COLOR_DEBUG   = "[COLOR=FF80FF00]DEBUG[/COLOR]"
    #COLOR_INFO    = "[COLOR=FFFFFFFF]INFO[/COLOR]"
    #COLOR_NOTICE  = "[COLOR=FFFFFFFF]NOTICE[/COLOR]"

    def __init__( self, *args, **kwargs ):
        xbmcgui.WindowXMLDialog.__init__( self, *args, **kwargs )
        # Maximum lines set for Xbox 10,000 and 20,000 for the others.
        # because more than 10,000 it takes much memory. "about: 1 Mb for 1000 lines"
        self.max_lines = ( 20000, 10000, )[ ( os.environ.get( "OS", "xbox" ).lower() == "xbox" ) ]

    def onInit( self ):
        # onInit est pour le windowXML seulement
        self.text = "Output not available!"
        try:
            if xbmcgui.Dialog().yesno( "XBMC Output - Select your choice!", "[B]-A- : [/B]" + os.path.basename( logger.LOG_SCRIPT ), "[B]-B- : [/B]xbmc.log", "", "[B]-A-[/B]", "[B]-B-[/B]" ):
                xbmc_log = os.path.join( XBMC_ROOT, "xbmc.log" )
                if not os.path.isfile( xbmc_log ):
                    xbmc_log = os.path.join( os.path.dirname( os.path.dirname( xbmc.translatePath( "T:\\" ) ) ), "xbmc.log" )
                file_path = xbmc_log
            else:
                file_path = logger.LOG_SCRIPT
            DIALOG_PROGRESS.create( "Output", "Reading the lines...", file_path, "Please wait..." )
            self._set_lines_color( file_path )
            DIALOG_PROGRESS.close()
            self._set_controls_values()
        except:
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )

    def _set_lines_color( self, file_path ):
        try:
            text = list()
            f = open( file_path )
            lines = f.readlines()
            f.close()
            percent = 0
            total_lines = len( lines ) or 1
            diff = ( 100.0 / total_lines )
            for count, line in enumerate( lines ):
                percent += diff
                if ( ( count + 1 ) == self.max_lines ):
                    DIALOG_PROGRESS.update( 100, "Line: %i / %i" % ( count + 1, self.max_lines, ) )
                    text.append( "[CR][COLOR=FFFF0000]***FOR MORE INFOS WATCH LOG IN YOUR PC***[/COLOR]" )
                    break
                DIALOG_PROGRESS.update( int( percent ), "Line: %i / %i" % ( count + 1, total_lines, ) )
                if " ERROR:" in line:
                    #line = re.sub( "\\bERROR\\b", self.COLOR_ERROR, line )
                    line = "[COLOR=FFFF0000]%s[/COLOR]" % ( line, )
                elif " WARNING:" in line:
                    #line = re.sub( "\\bWARNING\\b", self.COLOR_WARNING, line )
                    line = "[COLOR=FFFFFF3D]%s[/COLOR]" % ( line, )
                #note: plus que deux couleurs sa marche pas, les couleurs se melange!!!
                #elif " DEBUG:" in line:
                #    #line = re.sub( "\\bDEBUG\\b", self.COLOR_DEBUG, line )
                #    line = "[COLOR=FF80FF00]%s[/COLOR]" % ( line, )
                else:
                    pass
                text.append( line )#.strip( "\n\r" ) )
            self.text = "".join( text )
        except:
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )
            self.text = "Output not available!"

    def _set_controls_values( self ):
        xbmcgui.lock()
        try:
            self.getControl( self.CONTROL_TEXT_BOX ).reset()
            self.getControl( self.CONTROL_TEXT_BOX ).setText( self.text )
        except:
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )
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
        if action in ( 9, 10, 117, ): self._close_dialog()

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
