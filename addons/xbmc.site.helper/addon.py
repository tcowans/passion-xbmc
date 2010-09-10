
#Modules General
import os
import sys
import webbrowser
from traceback import print_exc

#Modules XBMC
import xbmc
import xbmcgui
from xbmcaddon import Addon

# Add-on Constants
__date__    = "10-09-2010"
__addonID__ = "xbmc.site.helper"

__settings__ = Addon( __addonID__ )
__addonDir__ = __settings__.getAddonInfo( "path" )
__language__ = __settings__.getLocalizedString # Add-on strings
#__string__   = xbmc.getLocalizedString # XBMC strings


# Increase load of backgrounds, add info of full path for winxml
SKIN_PATH = os.path.join( __addonDir__, "resources", "skins", "Default/" ).replace( "\\", "/" )
if SKIN_PATH != xbmc.getInfoLabel( "Skin.String(helper.skin.path)" ):
    xbmc.executebuiltin( "Skin.SetString(helper.skin.path, %s)" % SKIN_PATH )

# Web site: names, plots and urls 
SITE_HELPER = [
    ( 30010, 30110, "http://wiki.xbmc.org/?title=XBMC_Online_Manual" ),
    ( 30020, 30120, "http://wiki.passion-xbmc.org/" ),
    ( 30030, 30130, "http://forum.xbmc.org/" ),
    ( 30040, 30140, "http://passion-xbmc.org/forum/" ),
    ( 30050, 30150, "http://trac.xbmc.org/" ),
    ( 30060, 30160, "http://trac.xbmc.org/timeline" ),
    ]


def notification( header="", message="", sleep=5000, icon=__settings__.getAddonInfo( "icon" ) ):
    """ Will display a notification dialog with the specified header and message,
        in addition you can set the length of time it displays in milliseconds and a icon image. 
    """
    xbmc.executebuiltin( "XBMC.Notification(%s,%s,%i,%s)" % ( header, message, sleep, icon ) )


def launchUrl( url ):
    # Display url using the default browser.
    try: webbrowser.open( url )
    except: print_exc()


class DialogHelper( xbmcgui.WindowXMLDialog ):
    xbmc.executebuiltin( "Skin.Reset(AnimeWindowXMLDialogClose)" )
    xbmc.executebuiltin( "Skin.SetBool(AnimeWindowXMLDialogClose)" )

    CONTROL_MAIN_LIST_MENU = 9000

    def __init__( self, *args, **kwargs ):
        xbmcgui.WindowXMLDialog.__init__( self, *args, **kwargs )
        self.setListItems()

    def setListItems( self ):
        self.listitems = []
        try:
            # set listitems
            for titleID, plotID, url in SITE_HELPER:
                listitem = xbmcgui.ListItem( __language__( titleID ), __language__( plotID ) )
                listitem.setProperty( "url", url )
                self.listitems.append( listitem )
        except:
            print_exc()

    def onInit( self ):
        try:
            # add listitems
            if self.listitems:
                self.getControl( self.CONTROL_MAIN_LIST_MENU ).reset()
                self.getControl( self.CONTROL_MAIN_LIST_MENU ).addItems( self.listitems )
                self.setFocusId( self.CONTROL_MAIN_LIST_MENU )
        except:
            print_exc()

    def onFocus( self, controlID ):
        pass

    def onClick( self, controlID ):
        try:
            if controlID == self.CONTROL_MAIN_LIST_MENU:
                # get clicked listitem
                listitem = self.getControl( self.CONTROL_MAIN_LIST_MENU ).getSelectedItem()
                # get url
                url = listitem.getProperty( "url" )
                if url:
                    # notify user
                    notification( listitem.getLabel(), url )
                    # launch url
                    launchUrl( url )
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


def Main():
    """ for skinner: <onclick>XBMC.RunScript(xbmc.site.helper[,url])</onclick> """
    try:
        w = DialogHelper( "DialogHelper.xml", __addonDir__ )
        w.doModal()
        del w
    except:
        print_exc()


def Main2():
    """ for skinner: <onclick>XBMC.RunScript(xbmc.site.helper,http://forum.xbmc.org/)</onclick> """
    try:
        print sys.argv
        # launch url
        launchUrl( sys.argv[ 1 ] ) 
    except:
        print_exc()



if ( __name__ == "__main__" ):
    if not sys.argv[ 1: ]:
        # show default add-on GUI
        Main()
    else:
        # launch url from xbmc skin
        Main2()
