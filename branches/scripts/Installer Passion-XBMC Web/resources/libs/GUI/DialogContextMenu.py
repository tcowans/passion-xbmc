
#context menu du plugin "All Game" de frost

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
    CONTROL_CM_BUTTON_START = 1000
    CONTROL_CM_BUTTON_END   = 1007
    CONTROL_CM_BUTTONS = range( CONTROL_CM_BUTTON_START, ( CONTROL_CM_BUTTON_END + 1 ) )

    def __init__( self, *args, **kwargs ):
        xbmcgui.WindowXMLDialog.__init__( self, *args, **kwargs )
        self.control_enabled_buttons = range( self.CONTROL_CM_BUTTON_START, ( self.CONTROL_CM_BUTTON_END + 1 ) )
        self.buttons = kwargs.get( "buttons", {} )
        self.view_mode = kwargs.get( "view_mode", "0" )
        xbmc.executebuiltin( "Skin.SetString(totals_cm_buttons,%i)" % ( len( self.buttons ), ) )
        self.selected = 0

    def onInit( self ):
        try:
            xbmcgui.lock()
            if self.buttons == {}: raise
            first_cm_button = sorted( self.buttons.keys() )[ 0 ]
            for key in self.CONTROL_CM_BUTTONS:
                label = self.buttons.get( key )
                if label is not None:
                    if isinstance( label, tuple ):
                        self.getControl( key ).setLabel( label[ 0 ] )
                        if label[ 1 ] == "disabled":
                            self.getControl( key ).setEnabled( 0 )
                            try: del self.control_enabled_buttons[ self.control_enabled_buttons.index( key ) ]
                            except: pass
                            if self.control_enabled_buttons: self.setFocusId( self.control_enabled_buttons[ 0 ] )
                    else:#if isinstance( label, str ):
                        self.getControl( key ).setLabel( label )
                else:
                    self.getControl( key ).setVisible( 0 )
            if first_cm_button in self.control_enabled_buttons:
                self.setFocusId( first_cm_button )
            xbmcgui.unlock()
        except:
            print_exc()
            try:
                #new methode for default.hd
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
            #self.close()

    def onFocus( self, controlID ):
        pass

    def onClick( self, controlID ):
        if controlID == 10000:
            try:
                #new methode for default.hd
                self.selected = int( self.getControl( 10000 ).getSelectedItem().getProperty( "controlID" ) )
            except:
                pass
            xbmc.sleep( 10 )
            self.close()

        elif controlID in self.CONTROL_CM_BUTTONS:
            try:
                self.selected = controlID
                try:
                    # verification du cas de la souris qui peut avoir presser un boutons desactiver
                    if isinstance( self.buttons.get( self.selected ), tuple ):
                        if self.buttons.get( self.selected )[ 1 ] == "disabled":
                            self.selected = 0 #"disabled"
                except:
                    pass
                xbmc.sleep( 10 )
                self.close()
            except:
                pass

    def onAction( self, action ):
        xbmc.sleep( 10 )
        if action in ( 9, 10, 117 ):
            self.selected = 0
            self.close()


def show_context_menu( buttons={}, view_mode="0" ):
    dir_path = os.getcwd().rstrip( ";" )
    current_skin, force_fallback = getUserSkin()
    file_xml = ( "IPX-ContextMenu.xml", "passion-ContextMenu.xml" )[ current_skin != "Default.HD" ]

    w = ContextMenu( file_xml, dir_path, current_skin, force_fallback, buttons=buttons, view_mode=view_mode )
    w.doModal()
    selected = w.selected
    del w
    return selected
