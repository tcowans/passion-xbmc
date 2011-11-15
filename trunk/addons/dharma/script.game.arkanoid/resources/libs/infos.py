
#Modules General
import os
import sys
import time
from traceback import print_exc

#Modules XBMC
import xbmc
import xbmcgui

#Modules Customs
from htmldecode import htmlentitydecode


def _decode( text ):
    try: return htmlentitydecode( text )
    except: print_exc()
    return text


def get_revision():
    import re
    addon_rev = ""
    try:
        txt = file( os.path.join( os.getcwd(), "addon.xml" ), "r" ).read()
        rev = re.search( "<.+?Revision.+?(\d+).+?>", txt )
        if rev: addon_rev = rev.group( 1 )
    except:
        print_exc()
    return addon_rev


class Info( xbmcgui.WindowXMLDialog ):
    def __init__( self, *args, **kwargs ):
        xbmcgui.WindowXMLDialog.__init__( self, *args, **kwargs )
        xbmc.executebuiltin( "Skin.Reset(AnimeWindowXMLDialogClose)" )
        xbmc.executebuiltin( "Skin.SetBool(AnimeWindowXMLDialogClose)" )

    def onInit( self ):
        try:
            self.getControl( 48 ).reset()
            icon = sys.modules[ "__main__" ].__settings__.getAddonInfo( "icon" )
            listitem = xbmcgui.ListItem( _decode( sys.modules[ "__main__" ].__settings__.getAddonInfo( "name" ) ), "", icon, icon )
            
            for property in ( "author", "changelog", "description", "disclaimer",
                "fanart", "icon", "id", "name", "path", "profile", "stars", "summary", "type", "version" ):
                    value = str( sys.modules[ "__main__" ].__settings__.getAddonInfo( property ) )
                    listitem.setProperty( property, _decode( value ) )

            listitem.setProperty( "revision", get_revision() )
            self.getControl( 48 ).addItem( listitem )
        except:
            print_exc()

    def onFocus( self, controlID ):
        pass

    def onClick( self, controlID ):
        if controlID == 12:
            self._close_dialog()

    def onAction( self, action ):
        if action in [ 9, 10, 117 ] or action.getButtonCode() in [ 275, 257, 261 ]:
            self._close_dialog()

    def _close_dialog( self ):
        xbmc.executebuiltin( "Skin.Reset(AnimeWindowXMLDialogClose)" )
        time.sleep( .4 )
        self.close()
