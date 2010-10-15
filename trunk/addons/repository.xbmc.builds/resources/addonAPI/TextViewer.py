
# Modules general
import os
import re
import sys
from traceback import print_exc

# Modules XBMC
import xbmc
import xbmcgui


class DialogTextViewer( xbmcgui.WindowXMLDialog ):
    def __init__( self, *args, **kwargs ):
        xbmcgui.WindowXMLDialog.__init__( self, *args, **kwargs )
        self.heading = kwargs.get( "heading" )
        self.text = kwargs.get( "text" )

    def onInit( self ):
        try:
            self.getControl( 1 ).setLabel( self.heading )
            self.getControl( 5 ).setText( self.text )
        except:
            print_exc()

    def onFocus( self, controlID ):
        pass

    def onClick( self, controlID ):
        pass

    def onAction( self, action ):
        if action in [ 9, 10, 117 ]:
            self.close()


def showText( heading="", text="" ):
    w = DialogTextViewer( "DialogTextViewer.xml", os.getcwd(), heading=heading, text=text )
    w.doModal()
    del w
