# -*- coding: utf-8 -*-
#Modules General
import threading
from traceback import print_exc
import time
import os
#Modules XBMC
import xbmc
import xbmcgui
import sys
try:
    # parse sys.argv for params
    params = dict( arg.split( "=" ) for arg in sys.argv[ 1 ].split( "&" ) )
except:
    # no params passed
    params = {}   
class mythread( threading.Thread ):
    def __init__( self ):
        threading.Thread.__init__( self )
        self._stop = False
        print "### starting TvTunes Backend ###"
 
    def run( self ):
        newpath = ""
        oldpath = ""
        try:
            while not self._stop:
                # le code
                #print "visibility: %s" % xbmc.getCondVisibility( "Window.IsActive(10025)")
                if not xbmc.getCondVisibility( "Window.IsVisible(10025)"):
                    #destroy threading
                    self.stop()
                #print "old path: %s" % oldpath
                #print " new path: %s" % newpath
                if xbmc.getCondVisibility( "Container.Content(Seasons)" ) or xbmc.getCondVisibility( "Container.Content(Episodes)" ):
                    newpath = xbmc.getInfoLabel( "ListItem.Path" )
                    if not newpath == oldpath and not newpath == "" and not newpath == "videodb://2/2/": 
                        print "season level? %s" % xbmc.getCondVisibility( "Container.Content(Seasons)" )
                        print "Episodes level? %s" % xbmc.getCondVisibility( "Container.Content(Episodes)" )
                        print "old path: %s" % oldpath
                        print " new path: %s" % newpath
                        oldpath = newpath
                        if not xbmc.Player().isPlaying() and os.path.exists(newpath + "theme.mp3"): 
                            xbmc.Player().play(newpath + "theme.mp3")
                            if params.get("loop", False ) : xbmc.executebuiltin('XBMC.PlayerControl(Repeat)')
                            else: xbmc.executebuiltin('XBMC.PlayerControl(RepeatOff)')
                    # tu détecte si c'est pas la même toune et tu la lance
                else:
                    if not xbmc.getCondVisibility( "Container.Content(episodes)" ) and not xbmc.Player().isPlayingVideo() and not xbmc.getCondVisibility( "Window.IsVisible(12003)" ) and xbmc.Player().isPlayingAudio(): 
                        print "condition to stop theme playing!"
                        xbmc.Player().stop()
                time.sleep( .5 )
        except:
            print_exc()
            self.stop()
 
    def stop( self ):        
        print "### Stopping TvTunes Backend ###"
        self._stop = True
        xbmcgui.Window( 10025 ).clearProperty('TvTunesIsAlive')
if xbmc.getInfoLabel( "Window(10025).Property(TvTunesIsAlive)" ) != "true":
    xbmcgui.Window( 10025 ).setProperty( "TvTunesIsAlive", "true" )
    thread = mythread()
    thread.start()

