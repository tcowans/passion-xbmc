"""
    NB: the credits window is reserved for the default.hd only
    please don't edit credits this fonction is reserved for manager of Installer. thanks
"""


#Modules general
import os
import sys
from threading import Timer
from traceback import print_exc

#modules XBMC
import xbmc
import xbmcgui



class ScriptCredits( xbmcgui.WindowXML ):
    def __init__( self, *args, **kwargs ):
        xbmcgui.WindowXML.__init__( self, *args, **kwargs )
        self.player = xbmc.Player()

    def onInit( self ):
        self.set_properties()
        self.set_auto_close()

    def set_properties( self ):
        try:
            # set container/windowXML properties
            self.setProperty( "IPX_Statut",   sys.modules[ "__main__" ].__statut__ )
            self.setProperty( "IPX_Version",  sys.modules[ "__main__" ].__version__ )
            self.setProperty( "IPX_Date",     sys.modules[ "__main__" ].__date__ )
            self.setProperty( "IPX_revision", sys.modules[ "__main__" ].__svn_revision__ )
        except:
            print_exc()

    def set_auto_close( self ):
        delay = 160
        try:
            xbmc.sleep( 1000 )
            if self.player.isPlaying():
                delay = int( self.player.getTotalTime() )
                #print "player time", delay
        except:
            print_exc()
            delay = 160
        try:
            # auto close credits based of xbmc Player Total Time or max 160 (2 min 40 sec)
            self.auto_close = Timer( delay, self._close_credits, () )
            self.auto_close.start()
        except:
            print_exc()

    def onFocus( self, controlID ):
        pass

    def onClick( self, controlID ):
        if controlID in [ 206, 320 ]:
            self._close_credits()

    def onAction( self, action ):
        if action in [ 9, 10, 13 ]:
            self._close_credits()

    def _close_credits( self ):
        xbmc.executebuiltin( 'Skin.Reset(IPX_HideVisu)' )
        try:
            if self.player.isPlaying():
                self.player.stop()
        except:
            print_exc()
        try: self.auto_close.cancel()
        except: print_exc()
        self.close()



def show_credits():
    file_xml = "IPX-Credits.xml"
    dir_path = os.getcwd().replace( ";", "" )
    #NB: the credits window is reserved for the default.hd only
    current_skin, force_fallback = "Default.HD", True

    w = ScriptCredits( file_xml, dir_path, current_skin, force_fallback )
    w.doModal()
    del w
