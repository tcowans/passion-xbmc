
#context menu du plugin "All Game" de frost

#Modules general
import os
import sys

#modules XBMC
import xbmc
import xbmcgui

#modules custom
from utilities import *


class ContextMenu( xbmcgui.WindowXMLDialog ):
    # control id's
    #CONTROL_CM_BUTTON_START = 1000
    #CONTROL_CM_BUTTON_END   = 1006
    CONTROL_CM_BUTTONS = range( 1000, 1007 )

    def __init__( self, *args, **kwargs ):
        xbmcgui.WindowXMLDialog.__init__( self, *args, **kwargs )
        self.buttons = kwargs.get( "buttons", {} )
        self.selected = 0
        self.actionID = 0
        self.CONTROL_ENABLED_BUTTONS = range( 1000, 1007 )

    def onInit( self ):
        try:
            xbmcgui.lock()
            if self.buttons == {}: raise
            for key in self.CONTROL_CM_BUTTONS:
                label = self.buttons.get( key )
                if label is not None:
                    if isinstance( label, tuple ):
                        self.getControl( key ).setLabel( label[ 0 ] )
                        if label[ 1 ] == "disabled":
                            self.getControl( key ).setEnabled( 0 )
                            try: del self.CONTROL_ENABLED_BUTTONS[ self.CONTROL_ENABLED_BUTTONS.index( key ) ]
                            except: pass
                            if self.CONTROL_ENABLED_BUTTONS: self.setFocusId( self.CONTROL_ENABLED_BUTTONS[ 0 ] )
                    else:#if isinstance( label, str ):
                        self.getControl( key ).setLabel( label )
                else:
                    self.getControl( key ).setVisible( 0 )
            xbmcgui.unlock()
        except:
            try:logger = sys.modules[ "__main__" ].logger
            except: import script_log as logger
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )
            xbmcgui.unlock()
            self.close()

    def onFocus( self, controlID ):
        pass

    def onClick( self, controlID ):
        #if self.actionID != 117:
        if controlID in self.CONTROL_CM_BUTTONS:
            try:
                self.selected = controlID
                xbmc.sleep( 10 )
                self.close()
            except:
                pass

    def onAction( self, action ):
        #self.actionID = action
        xbmc.sleep( 10 )
        if action in ( 9, 10, 117 ):
            self.selected = 0
            self.close()


def show_context_menu( buttons ):
    file_xml = "passion-ContextMenu.xml"
    dir_path = os.getcwd().rstrip( ";" )
    current_skin, force_fallback = getUserSkin()

    w = ContextMenu( file_xml, dir_path, current_skin, force_fallback, buttons=buttons )
    w.doModal()
    selected = w.selected
    del w
    return selected
