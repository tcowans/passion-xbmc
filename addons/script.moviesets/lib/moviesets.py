
#Modules General
import os
import sys
import time
from threading import Lock, Thread

#Modules XBMC
import xbmc
import xbmcgui
from xbmcaddon import Addon

#Modules Custom
from database import Database
from log import logAPI

log = logAPI()

START_TIME = time.time()

ADDON = Addon( "script.moviesets" )

database = Database()


def IsTrue( text ):
    return ( text == "true" )


def time_took( t ):
    t = ( time.time() - t )
    if t >= 60: return "%.3fm" % ( t / 60.0 )
    return "%.3fs" % ( t )


class Main:
    try: args = dict( [ arg.split( "=" ) for arg in argv[ 1 ].split( "&" ) ] )
    except: args = {}

    def __init__( self, windowId=10025 ):
        self.containerId = int( self.args.get( "containerId" ) or "7000" )
        ADDON.setSetting( "containerId", str( self.containerId ) )
        if xbmc.getInfoLabel( "Container(%i).NumItems" % self.containerId ) == "0":
            self.initialize( windowId )

    def initialize( self, windowId ):
        try:
            self.window = xbmcgui.Window( windowId )
            self.container = self.window.getControl( self.containerId )

            self.condSynchro = "![StringCompare(ListItem.Label,Container(%i).ListItem.Label) + ListItem.IsFolder]" % self.containerId

            self.setContent()
            self.backend = Backend( self, Lock() )
            self.backend.setDaemon( True )
            self.backend.start()
        except:
            log.error.exc_info( sys.exc_info(), self )
        log.notice.LOG( "initialized took %s", time_took( START_TIME ) )

    def setContent( self ):
        self.window.setProperty( "MovieSets.IsAlive", "true" )
        if xbmc.getCondVisibility( "StringCompare(Container.FolderPath,videodb://1/7/)" ):
            self.window.setProperty( "Content.MovieSets", "true" )
        else:
            self.window.clearProperty( "Content.MovieSets" )

    def setContainer( self ):
        db_start_time = time.time()
        listitems, self.moviesets = database.getContainerMovieSets()
        if listitems:
            self.container.reset()
            self.container.addItems( listitems )
        log.notice.LOG( "InfoScanner: Finished scan. Scanning for moviesets info took %s", time_took( db_start_time ) )
        return self.container.size()

    def synchronize( self ):
        try:
            if xbmc.getCondVisibility( self.condSynchro ):
                new_pos = self.moviesets.get( xbmc.getInfoLabel( "ListItem.Label" ) )
                new_pos = ( 0, ( new_pos or 0 ) )[ xbmc.getCondVisibility( "ListItem.IsFolder" ) ]
                cur_pos = self.container.getSelectedPosition()
                if ( 0 <= cur_pos <> new_pos ):
                    self.container.selectItem( new_pos )
        except:
            log.error.exc_info( sys.exc_info(), self )


class Backend( Thread ):
    def __init__( self, main, lock ):
        Thread.__init__( self, name="Thread-MovieSets" )
        self.lock = lock
        self.main = main
        self.window = main.window
        self.last_mtime = 0
        self._stop = False

    def run( self ):
        try:
            self.lock.acquire()
            self.clearProperties()
            while not self._stop:
                if xbmc.getCondVisibility( "![Window.IsVisible(VideoLibrary) | Skin.HasSetting(MovieSets.Stop)]" ):
                    self.stop(); break
                self.updates()
                time.sleep( .025 )
        except SystemExit:
            #log.error.exc_info( sys.exc_info(), self )
            self.stop()
        except:
            log.error.exc_info( sys.exc_info(), self )
            self.stop()

    def updates( self ):
        if not xbmc.getCondVisibility( "Skin.HasSetting(MovieSets.Sleep) | Window.IsActive(13000) | Window.IsActive(FileBrowser.xml) | Window.IsActive(DialogVideoInfo.xml)" ):
            if IsTrue( self.window.getProperty( "Content.MovieSets" ) ) or xbmc.getCondVisibility( "Container.Content(Movies)" ):
                if not self.updateContainer(): return self.stop()
                self.main.synchronize()
            self.main.setContent()

    def updateContainer( self ):
        mtime = os.path.getmtime( "special://Database/MyVideos34.db" )
        if ( mtime > self.last_mtime ) or IsTrue( self.window.getProperty( "MovieSets.Update" ) ):
            self.window.clearProperty( "MovieSets.Update" )
            self.last_mtime = mtime# + 180.0 # 3 min
            self.busy()
            if not self.main.setContainer(): return False
            self.busy( True )
            log.notice.LOG( "MyVideos_db: last modification is %s", time.strftime( "%Y-%m-%d %H:%M:%S", time.localtime( mtime ) ) )
        return True

    def busy( self, close=False ):
        if IsTrue( ADDON.getSetting( "busydialog" ) ):
            hasbusy = xbmc.getCondVisibility( "Window.IsVisible(busydialog)" )
            if close or hasbusy: xbmc.executebuiltin( "Dialog.Close(busydialog)" )
            elif not hasbusy: xbmc.executebuiltin( "ActivateWindow(busydialog)" )

    def stop( self ):
        xbmc.executebuiltin( "Skin.Reset(MovieSets.Sleep)" )
        self.busy( True )
        #self.clearProperties()
        self.window.clearProperty( "MovieSets.Update" )
        self.window.clearProperty( "MovieSets.IsAlive" )
        self.window.clearProperty( "Content.MovieSets" )
        self._stop = True
        log.notice.LOG( "Backend: Finished Thread. Running moviesets took %s", time_took( START_TIME ) )
        try: self.lock.release()
        except: pass

    def clearProperties( self ):
        xbmc.executebuiltin( "Skin.Reset(MovieSets.Sleep)" )
        xbmc.executebuiltin( "Skin.Reset(MovieSets.Stop)" )
        try:
            self.window.clearProperty( "MovieSets.Update" )
            self.window.clearProperty( "MovieSets.IsAlive" )
            self.window.clearProperty( "Content.MovieSets" )
        except:
            log.error.exc_info( sys.exc_info(), self )



if ( __name__ == "__main__" ):
    Main()
