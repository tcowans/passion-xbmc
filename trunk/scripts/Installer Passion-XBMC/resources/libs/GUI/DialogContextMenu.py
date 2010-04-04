
# Modules general
import os
import sys
from traceback import print_exc

# Modules XBMC
import xbmc
import xbmcgui

# Modules custom
from utilities import *


class ContextMenu( xbmcgui.WindowXMLDialog ):
    # control id's
    CONTROL_CM_BUTTON_START = 999
    CONTROL_CM_BUTTON_END   = 1007
    CONTROL_CM_BUTTONS = range( CONTROL_CM_BUTTON_START, ( CONTROL_CM_BUTTON_END + 1 ) )

    def __init__( self, *args, **kwargs ):
        xbmcgui.WindowXMLDialog.__init__( self, *args, **kwargs )
        xbmc.executebuiltin( "Skin.Reset(AnimeWindowXMLDialogClose)" )
        xbmc.executebuiltin( "Skin.SetBool(AnimeWindowXMLDialogClose)" )

        self.buttons = kwargs.get( "buttons", {} )
        self.view_mode = kwargs.get( "view_mode", "0" )
        xbmc.executebuiltin( "Skin.SetString(totals_cm_buttons,%i)" % ( len( self.buttons ), ) )
        self.selected = 0

    def onInit( self ):
        try:
            xbmcgui.lock()
            if self.buttons == {}: raise
            for key in self.CONTROL_CM_BUTTONS:
                label = self.buttons.get( key )
                if label is not None:
                    if isinstance( label, tuple ):
                        label = label[ 0 ]
                    context_item = xbmcgui.ListItem( label )
                    context_item.setProperty( "controlID", str( key ) )
                    context_item.setProperty( "main_view_mode", self.view_mode )
                    self.getControl( 10000 ).addItem( context_item )
        except:
            print_exc()
        xbmcgui.unlock()

    def onFocus( self, controlID ):
        pass

    def onClick( self, controlID ):
        if controlID == 10000:
            try:
                #new methode for default.hd
                self.selected = int( self.getControl( 10000 ).getSelectedItem().getProperty( "controlID" ) )
            except:
                pass
            self.close_dialog()

    def onAction( self, action ):
        if action in ( 9, 10, 117 ):
            self.selected = 0
            self.close_dialog()

    def close_dialog( self ):
        import time
        xbmc.executebuiltin( "Skin.Reset(AnimeWindowXMLDialogClose)" )
        time.sleep( .01 ) # pour les fade plus que .1 pas beau :(
        self.close()

def show_context_menu( buttons={}, view_mode="0" ):
    dir_path = os.getcwd().rstrip( ";" )
    current_skin, force_fallback = getUserSkin()
    file_xml = "IPX-ContextMenu.xml"

    w = ContextMenu( file_xml, dir_path, current_skin, force_fallback, buttons=buttons, view_mode=view_mode )
    w.doModal()
    selected = w.selected
    del w
    return selected
