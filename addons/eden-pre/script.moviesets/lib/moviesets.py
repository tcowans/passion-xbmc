
import time
START_TIME = time.time()

#Modules General
import os
import sys
from glob import glob
#from threading import Thread

#Modules XBMC
import xbmc
import xbmcgui
from xbmcaddon import Addon

#Modules Custom
from database import getContainerMovieSets
from utils.log import logAPI


# constants
LOGGER   = logAPI()
DB_PATHS = glob( xbmc.translatePath( "special://Database/MyVideos*.db" ) )[ -1: ]
DB_NAME  = "".join( [ os.path.basename( db ) for db in DB_PATHS ] ) or "MyVideos??.db"

def IsTrue( text ):
    return ( text.lower() == "true" )


def time_took( t ):
    t = ( time.time() - t )
    if t >= 60: return "%.3fm" % ( t / 60.0 )
    return "%.3fs" % ( t )


class Main:
    try: args = dict( [ arg.split( "=" ) for arg in sys.argv[ 1 ].split( "&" ) ] )
    except: args = {}

    def __init__( self, windowId=10025 ):
        self.containerId = int( self.args.get( "containerid" ) or "7000" )
        Addon( "script.moviesets" ).setSetting( "containerId", str( self.containerId ) )
        NumItems = xbmc.getInfoLabel( "Container(%i).NumItems" % self.containerId ) or "0"
        if NumItems == "0": self.initialize( windowId )

    def initialize( self, windowId ):
        try:
            self.window = xbmcgui.Window( windowId )
            self.container = self.window.getControl( self.containerId )

            self.condSynchro = "![StringCompare(ListItem.Label,Container(%i).ListItem.Label) + ListItem.IsFolder]" % self.containerId

            self.setContent()
            self.backend = Backend( self )
            #self.backend.setDaemon( True )
            #self.backend.start()
        except:
            LOGGER.error.print_exc()

    def setContent( self ):
        self.window.setProperty( "MovieSets.IsAlive", "true" )
        if xbmc.getCondVisibility( "StringCompare(Container.FolderPath,videodb://1/7/)" ):
            self.window.setProperty( "Content.MovieSets", "true" )
        else:
            self.window.clearProperty( "Content.MovieSets" )

    def setContainer( self ):
        db_start_time = time.time()
        listitems, self.moviesets = getContainerMovieSets()
        if listitems:
            self.container.reset()
            self.container.addItems( listitems )
        LOGGER.notice.LOG( "InfoScanner: Finished scan. Scanning for moviesets info took %s", time_took( db_start_time ) )
        return self.container.size()

    def synchronize( self ):
        try:
            if xbmc.getCondVisibility( self.condSynchro ):
                new_pos = self.moviesets.get( xbmc.getInfoLabel( "ListItem.Label" ) )
                # possible xbmc.getInfoLabel return empty on last Git. check is none
                if new_pos is None:
                    for label, pos in self.moviesets.items():
                        if xbmc.getCondVisibility( "StringCompare(ListItem.Label,%s)" % label ):
                            new_pos = pos
                            break

                new_pos = ( 0, ( new_pos or 0 ) )[ xbmc.getCondVisibility( "ListItem.IsFolder" ) ]
                cur_pos = self.container.getSelectedPosition()
                if ( 0 <= cur_pos <> new_pos ):
                    self.container.selectItem( new_pos )
        except:
            LOGGER.error.print_exc()


class Backend:#( Thread ):
    def __init__( self, main ):
        #Thread.__init__( self, name="Thread-MovieSets" )

        self.main = main
        self.window = main.window
        self.last_mtime = -1
        self.moviesets_stop = xbmc.abortRequested #False
        self.run()

    def run( self ):
        LOGGER.notice.LOG( "initialized took %s", time_took( START_TIME ) )
        try:
            self.clearProperties()
            while ( not self.moviesets_stop ):# or ( not xbmc.abortRequested ):
                self.moviesets_stop = xbmc.abortRequested
                if xbmc.getCondVisibility( "![Window.IsVisible(VideoLibrary) | Skin.HasSetting(MovieSets.Stop)]" ):
                    self.stop(); break
                self.updates()
                time.sleep( .1 )
        except SystemExit:
            LOGGER.warning.LOG( "SystemExit! xbmc.abortRequested(%r)" % xbmc.abortRequested )
            self.stop()
        except:
            LOGGER.error.print_exc()
            self.stop()

    def updates( self ):
        if not IsTrue( self.window.getProperty( "MovieSets.Update" ) ) and xbmc.getCondVisibility( "Window.IsActive(addonsettings)" ):
            self.window.setProperty( "MovieSets.Update", "true" )
        if not xbmc.getCondVisibility( "Skin.HasSetting(MovieSets.Sleep) | Window.IsActive(addonsettings) | Window.IsActive(13000) | Window.IsActive(FileBrowser.xml) | Window.IsActive(DialogVideoInfo.xml) | Window.IsActive(script-MovieSets-Browser.xml) | Window.IsActive(script-MovieSets-DialogInfo.xml) | Window.IsActive(11112)" ):
            if IsTrue( self.window.getProperty( "Content.MovieSets" ) ) or xbmc.getCondVisibility( "Container.Content(Movies) + System.GetBool(videolibrary.groupmoviesets)" ):
                if not self.updateContainer(): return self.stop()
                self.main.synchronize()
            self.main.setContent()

    def updateContainer( self ):
        mtime = sum( [ os.path.getmtime( db ) for db in DB_PATHS ] )
        if ( mtime > self.last_mtime ) or IsTrue( self.window.getProperty( "MovieSets.Update" ) ):
            self.window.clearProperty( "MovieSets.Update" )
            self.last_mtime = mtime # + 180.0 # 3 min
            if not self.main.setContainer(): return False
            LOGGER.notice.LOG( "%s: last modification is %s", DB_NAME, time.strftime( "%Y-%m-%d %H:%M:%S", time.localtime( mtime ) ) )
        return True

    def stop( self ):
        self.clearProperties()
        self.moviesets_stop = True
        LOGGER.notice.LOG( "Backend: Finished Thread. Running moviesets took %s", time_took( START_TIME ) )

    def clearProperties( self ):
        xbmc.executebuiltin( "Skin.Reset(MovieSets.Sleep)" )
        xbmc.executebuiltin( "Skin.Reset(MovieSets.Stop)" )
        for property in [ "MovieSets.Update", "MovieSets.IsAlive", "Content.MovieSets" ]:
            try: self.window.clearProperty( property )
            except:
                try: xbmcgui.Window( 10025 ).clearProperty( property )
                except: LOGGER.error.print_exc()



if ( __name__ == "__main__" ):
    Main()
