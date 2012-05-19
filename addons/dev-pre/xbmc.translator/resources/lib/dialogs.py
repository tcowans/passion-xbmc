
import xbmcgui


class DialogContextMenu( xbmcgui.WindowXMLDialog ):
    CONTROLS_RADIO_BUTTON = [ 19, 20, 21 ]
    CONTROLS_BUTTON = { 1001: 33, 1002: 34, 1003: 19, 1004: 20, 1010: 32 }

    def __init__( self, *args, **kwargs ):
        self.parent = kwargs[ "parent" ]

    def onInit( self ):
        try:
            rb1 = self.parent.getControl( 19 ).isSelected()
            rb2 = self.parent.getControl( 20 ).isSelected()
            self.getControl( 1003 ).setVisible( not rb1 )
            self.getControl( 1004 ).setVisible( not rb2 and self.parent.IsModified )
            self.getControl( 1009 ).setVisible( rb1 or rb2 )
            
            IsModified = self.parent.getControl( self.parent.ContainerId ).getSelectedItem().getProperty( "IsModified" )
            if IsModified != "true":
                self.getControl( 1007 ).setVisible( False )
                self.setFocusId( 1001 )
        except:
            print_exc()

    def onFocus( self, controlID ):
        pass

    def onClick( self, controlID ):
        try:
            if controlID == 1007:
                listitem = self.parent.getControl( self.parent.ContainerId ).getSelectedItem()
                pos = int( listitem.getProperty( "Position" ) )
                self.parent.listitems[ pos ].setLabel( listitem.getProperty( "DefaultString" ) )
                self.parent.listitems[ pos ].setProperty( "IsModified", "" )

                hasModified = False
                for li in self.parent.listitems:
                    hasModified = li.getProperty( "IsModified" ) == "true"
                    if hasModified: break
                if not hasModified:
                    self.parent.setProperty( "IsModified", "" )
                    self.parent.IsModified = False

                self._close_dialog()

            elif controlID == 1008:
                self.parent.googleTrans = True
                self._close_dialog()
                self.parent.sendClick( self.parent.ContainerId )

            elif controlID == 1009:
                for control, id in { 1003: 19, 1004: 20, 1005: 21 }.items():
                    radiobutton = self.parent.getControl( id )
                    if radiobutton.isSelected():
                        controlID = control
                        break

            if controlID in self.CONTROLS_BUTTON.keys():
                selected = self.CONTROLS_BUTTON[ controlID ]

                if selected in self.CONTROLS_RADIO_BUTTON:
                    radiobutton = self.parent.getControl( selected )
                    radiobutton.setSelected( not radiobutton.isSelected() )

                self._close_dialog()
                self.parent.sendClick( selected )
        except:
            print_exc()
            self._close_dialog()

    def onAction( self, action ):
        if action in [ 9, 10, 117 ]:
            self._close_dialog()

    def _close_dialog( self ):
        self.close()
