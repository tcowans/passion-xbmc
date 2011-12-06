# -*- coding: utf-8 -*-

#Modules General
import time
START_TIME = time.time()

from threading import Timer

# General Import's
from common import *

# fix abortRequested for xbox
if not hasattr( xbmc, "abortRequested" ):
    xbmc.abortRequested = False


CONDITION_STOP_TUNES_PLAYER   = "!Window.IsVisible(10025)"
CONDITION_PLAY_TUNE           = "[Container.Content(Seasons) | Container.Content(Episodes)] + !Player.Playing + !SubString(ListItem.Path,plugin://) + !StringCompare(container.folderpath,videodb://5/)"
CONDITION_TUNE_ENDED          = "StringCompare(Window(10025).Property(TvTunesIsAlive),true) + !Player.Playing"#+" | !Player.HasAudio"
CONDITION_REINIT_TUNES_PLAYER = "Container.Content(tvshows) + !Window.IsVisible(movieinformation)"
CONDITION_STOP_TUNE           = "!IsEmpty(Window(10025).Property(TvTunesIsAlive)) + Player.HasAudio"
CONDITION_REFRESH_CONTAINER   = "Window.IsActive(script-TvTunes-main.xml) | [Window.IsActive(addonsettings) + SubString(Control.GetLabel(20),%s)]" % AddonName

WINDOW_VIDEO_NAV = xbmcgui.Window( 10025 )
CONTAINER        = getTVShows( "dict" )


def _unicode( text, encoding='utf-8' ):
    try: text = unicode( text, encoding )
    except: pass
    return text


class XBMCPlayer( xbmc.Player ):
    """ Subclass of XBMC Player class.
        Overrides onplayback events, for custom actions.
    """
    def __init__( self, *args ):
        LOGGER.debug.LOG( "starting TvTunes Backend" )

        self._stop = xbmc.abortRequested
        self.loud = False
        self.initialize()

        #start backend
        self.run()

    def _play( self, tune, listitem ):
        xbmc.PlayList( xbmc.PLAYLIST_MUSIC ).clear()
        WINDOW_VIDEO_NAV.setProperty( "TvTunesIsAlive", "true" )
        self.isAlive = True
        self.playpath = tune
        self.listitem = listitem
        playlist = self._repeat()
        if not self.loud: self.setVolume( "down" )
        if playlist is not None: self.play( playlist )
        else: self.play( self.playpath, self.listitem )

    def onPlayBackStarted( self ):
        if self.playpath:
            LOGGER.debug.LOG( "start playing %s", self.playpath )
            if not self.loud: self.setVolume( "down" )
            WINDOW_VIDEO_NAV.setProperty( "TvTunesIsAlive", "true" )
            self.isAlive = True
            if self.notify:
                self.notify = False
                msg = LangXBMC( ( 595, 597, 596 )[ int( Addon.getSetting( "loop2" ) ) ] )
                self._notification( Language( 32000 ).encode( "utf-8" ), msg.encode( "utf-8" ) )

    def onPlayBackEnded( self ):
        if self.loud: self.setVolume( "up" )
        WINDOW_VIDEO_NAV.clearProperty( 'TvTunesIsAlive' )
        self.isAlive = False

    def onPlayBackStopped( self ):
        if self.loud: self.setVolume( "up" )
        WINDOW_VIDEO_NAV.clearProperty( 'TvTunesIsAlive' )
        self.isAlive = False

    def _notification( self, header="", message="", sleep=4000, icon=Addon.getAddonInfo( "icon" ) ):
        """ Will display a notification dialog with the specified header and message,
            in addition you can set the length of time it displays in milliseconds and a icon image.
        """
        xbmc.executebuiltin( "Notification(%s,%s,%i,%s)" % ( header, message, sleep, icon ) )

    def _repeat( self ):
        self.repeat = ( "Off", "", "One" )[ int( Addon.getSetting( "loop2" ) ) ]
        # new in revision https://github.com/xbmc/xbmc/commit/639950e80d7a19a3150d9b7f799a3def62aef103
        self.notify = IsTrue( Addon.getSetting( "loopnotify" ) )#( "", ",notify" )[ IsTrue( Addon.getSetting( "loopnotify" ) ) ]
        #this built-in not work on Subclass of XBMC Player class.
        #xbmc.executebuiltin( 'PlayerControl(Repeat%s%s)' % ( repeat, notify ) )
        playlist = None
        if self.repeat != "Off":
            playlist = xbmc.PlayList( xbmc.PLAYLIST_MUSIC )
            playlist.clear()
            for x in xrange( ( 25, 1 )[ self.repeat == "One" ] ):
                playlist.add( self.playpath, self.listitem )
        return playlist


class TunesPlayer( XBMCPlayer ):
    def __new__( cls, *args ):
        return XBMCPlayer.__new__( cls, *args )

    def initialize( self ):
        WINDOW_VIDEO_NAV.setProperty( "TvTunesIsRunning", "true" )
        WINDOW_VIDEO_NAV.clearProperty( 'TvTunesIsAlive' )
        self.isAlive = False
        self.playpath = ""
        self.showLogo()

    def run( self ):
        try:
            LOGGER.notice.LOG( "initialized Player took %s", time_took( START_TIME ) )
            self.refresh_container = False
            while ( not self._stop ):
                self._stop = xbmc.abortRequested
                if xbmc.getCondVisibility( CONDITION_STOP_TUNES_PLAYER ):
                    self.stopTunesPlayer()

                #if xbmc.getCondVisibility( "!IsEmpty(ListItem.Path) + !StringCompare(ListItem.Path,%s/)" % os.path.dirname( self.playpath ) ):
                #    print repr( xbmc.getInfoLabel( "ListItem.Path" ) + THEME_FILE )

                if xbmc.getCondVisibility( CONDITION_PLAY_TUNE ):
                    TVShowTitle = _unicode( xbmc.getInfoLabel( "ListItem.TVShowTitle" ) or xbmc.getInfoLabel( "Container.FolderName" ) )
                    if TVShowTitle and CONTAINER.has_key( TVShowTitle ):
                        listitem = CONTAINER[ TVShowTitle ]
                        #default tune
                        tune = listitem.getProperty( "tune" )
                        if tune and tune != self.playpath:
                            if not self.isPlaying():
                                self._play( tune, listitem )
                                xbmc.sleep( 100 )
                            else:
                                LOGGER.debug.LOG( "player already playing" )

                #if xbmc.getCondVisibility( CONDITION_TUNE_ENDED ):
                if self.isAlive and not self.isPlaying() or IsTrue( WINDOW_VIDEO_NAV.getProperty( 'TvTunesIsAlive' ) ) and not self.isPlaying():
                    LOGGER.debug.LOG( "playing ends" )
                    if self.loud:
                        self.setVolume( "up" )
                    WINDOW_VIDEO_NAV.clearProperty( 'TvTunesIsAlive' )
                    self.isAlive = False

                if self.playpath and xbmc.getCondVisibility( CONDITION_REINIT_TUNES_PLAYER ):
                    LOGGER.debug.LOG( "stop playing" )
                    self.stop()
                    if self.loud:
                        self.setVolume( "up" )
                    LOGGER.debug.LOG( "reinit condition" )
                    self.initialize()

                time.sleep( .5 )

                if xbmc.getCondVisibility( CONDITION_REFRESH_CONTAINER ):
                    self.refresh_container = True
                elif self.refresh_container:
                    #refresh container
                    globals().update( { "CONTAINER": getTVShows( "dict", True ) } )
                    # reload Addon objet
                    from common import Addon
                    globals().update( { "Addon": Addon } )
                    # reset refresh status
                    self.refresh_container = False
                    # set again logo for change
                    self.showLogo()
        except SystemExit:
            LOGGER.warning.LOG( "SystemExit! xbmc.abortRequested(%r)" % xbmc.abortRequested )
            self.stopTunesPlayer()
        except:
            LOGGER.error.print_exc()
            self.stopTunesPlayer()

    def setVolume( self, action ):
        try:
            operator = None
            if action == "down":
                self.loud = True
                operator  = "-"
            elif action == "up":
                self.loud = False
                operator  = "+"
            if operator:
                volume = xbmc.getInfoLabel( "Player.Volume" ).replace( ",", "." )
                formula = "int((60+%s%s%s)*(100/60.0))" % ( volume.split( " " )[ 0 ], operator, Addon.getSetting( "downvolume" ) )
                vol = eval( formula )
                if vol > 100 : vol = 100
                elif vol < 0 : vol = 0
                xbmc.executebuiltin( 'XBMC.SetVolume(%d)' % vol )
                xbmc.sleep( 100 )
                LOGGER.debug.LOG( "SetVolume: %s to %s, Formula: %s" % ( volume, xbmc.getInfoLabel( "Player.Volume" ), formula ) )
        except:
            LOGGER.error.print_exc()

    def stopTunesPlayer( self ):
        xbmc.PlayList( xbmc.PLAYLIST_MUSIC ).clear()
        #if xbmc.getCondVisibility( CONDITION_STOP_TUNE ):
        if self.isAlive and self.isPlayingAudio() or xbmc.getCondVisibility( "Player.Playing + StringCompare(Player.Filenameandpath,%s)" % self.playpath ) or self.isPlaying() and self.playpath == self.getPlayingFile():
            LOGGER.debug.LOG( "stop playing" )
            self.stop()

        if self.loud: self.setVolume( "up" )

        WINDOW_VIDEO_NAV.clearProperty( 'TvTunesIsRunning' )
        WINDOW_VIDEO_NAV.clearProperty( 'TvTunesIsAlive' )
        self.isAlive = False

        LOGGER.notice.LOG( "running backend took %s", time_took( START_TIME ) )
        self._stop = True

    def showLogo( self ):
        try:
            # skinner test
            try: WINDOW_VIDEO_NAV.removeControl( self.logo )
            except: pass
            if IsTrue( Addon.getSetting( "showlogo" ) ) or IsTrue( Addon.getSetting( "showlogo2" ) ):
                size = int( float( Addon.getSetting( "logosize" ) ) )
                posx = int( float( Addon.getSetting( "logoposx" ) ) )
                posy = int( float( Addon.getSetting( "logoposy" ) ) )
                if size + posx > 1280: posx = 1280 - size
                if size + posy > 720:  posy = 720 - size
                self.logo = xbmcgui.ControlImage( posx, posy, size, size, Addon.getAddonInfo( "icon" ), aspectRatio=2 )
                prop = ( "Running", "Alive" )[ IsTrue( Addon.getSetting( "showlogo2" ) ) ]
                WINDOW_VIDEO_NAV.addControl( self.logo )
                self.logo.setVisibleCondition( '!IsEmpty(Window(10025).Property(TvTunesIs%s))' % prop )
                self.logo.setAnimations( [ ( 'Visible', 'effect=fade time=300' ), ( 'Hidden', 'effect=fade time=300' ) ] )
        except:
            LOGGER.error.print_exc()


if ( __name__ == "__main__" ):
    TunesPlayer( xbmc.PLAYER_CORE_PAPLAYER )
