
import os
from traceback import print_exc

import xbmc
import xbmcgui
from xbmcaddon import Addon

__settings__ = Addon( "repository.xbmc.builds" )
__addonDir__ = __settings__.getAddonInfo( "path" )

PROFILE_PATH = xbmc.translatePath( __settings__.getAddonInfo( "profile" ) )
DL_INFO_PATH = os.path.join( PROFILE_PATH, "iddl_data" )


class DialogDownloadProgress( xbmcgui.WindowXMLDialog ):
    xbmc.executebuiltin( "Skin.Reset(AnimeWindowXMLDialogClose)" )
    xbmc.executebuiltin( "Skin.SetBool(AnimeWindowXMLDialogClose)" )
    def __init__( self, *args, **kwargs ):
        xbmcgui.WindowXMLDialog.__init__( self, *args, **kwargs )
        self.doModal()

    def onInit( self ):
        pass

    def onFocus( self, controlID ):
        pass

    def onClick( self, controlID ):
        try:
            kill = None
            if controlID == 199:
                self._close_dialog()
            elif controlID == 99:
                try:
                    import shutil
                    try: shutil.rmtree( DL_INFO_PATH, True )
                    except: pass
                    if not os.path.exists( DL_INFO_PATH ):
                        os.makedirs( DL_INFO_PATH )
                except:
                    print_exc()
                xbmc.executebuiltin( "Container.Refresh" )
                self._close_dialog()
            elif 1401 <= controlID <= 1412:
                kill = str( controlID )[ 2: ]
            if kill is not None:
                win = xbmcgui.Window( xbmcgui.getCurrentWindowDialogId() )
                win.setProperty( "progress.%s.isAlive" % kill , "kill" )
                #print xbmcgui.getCurrentWindowDialogId()
        except:
            print_exc()

    def onAction( self, action ):
        if action in [ 9, 10, 117 ]:
            self._close_dialog()

    def _close_dialog( self ):
        xbmc.executebuiltin( "Skin.Reset(AnimeWindowXMLDialogClose)" )
        from time import sleep
        sleep( .4 )
        self.close()



#if ( __name__ == "__main__" ):
DialogDownloadProgress( "DialogDownloadProgress.xml", __addonDir__ )
