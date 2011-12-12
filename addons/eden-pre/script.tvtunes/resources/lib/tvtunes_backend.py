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
import xbmcvfs
import xbmcaddon

from common import getThemePath

__addon__     = xbmcaddon.Addon(id='script.tvtunes')
# languages
Language = __addon__.getLocalizedString
LangXBMC = xbmc.getLocalizedString

CONDITION_REFRESH_SETTINGS   = "Window.IsActive(script-TvTunes-main.xml) | [Window.IsActive(addonsettings) + SubString(Control.GetLabel(20),%s)]" % __addon__.getAddonInfo( 'name' )

def log( msg, level=xbmc.LOGDEBUG ):
    xbmc.log( "[TvTunes::Backend] " + str( msg ), level )

"""
try:
    # parse sys.argv for params
    log( sys.argv[ 1 ] )
    try:params = dict( arg.split( "=" ) for arg in sys.argv[ 1 ].split( "&" ) )
    except:
        print_exc()
        params = dict( sys.argv[ 1 ].split( "=" ))
except:
    # no params passed
    print_exc()
    params = {}
"""
class mythread( threading.Thread ):
    def __init__( self ):
        threading.Thread.__init__( self )
        self._stop = False
        log( "### starting TvTunes Backend ###" )
        self.newpath = ""
        self.oldpath = ""
        self.playpath = ""
        self.loud = False
        self.get_settings()
        self.refresh_settings = False
        #self.enable_custom_path = __addon__.getSetting("custom_path_enable")
        #if self.enable_custom_path == "true":
        #    self.custom_path = __addon__.getSetting("custom_path")
        self.base_volume = self.get_volume()

    def get_settings( self ):
        self.default_folder  = __addon__.getSetting( "savetuneintvshowfolder" ) == "true"
        self.separate_folder = __addon__.getSetting( "saveinseparatefolder" ) == "true"
        self.custom_path     = __addon__.getSetting( "customtunesfolder" )
        # reset custom path if not exists
        if self.custom_path and not xbmcvfs.exists( self.custom_path ):
            self.custom_path = ""
            self.default_folder = True

    def run( self ):
        try:
            while not self._stop:           # the code
                if not xbmc.getCondVisibility( "Window.IsVisible(10025)"): self.stop()      #destroy threading

                if xbmc.getCondVisibility( "Container.Content(Seasons)" ) or xbmc.getCondVisibility( "Container.Content(Episodes)" ) and not xbmc.Player().isPlaying() and "plugin://" not in xbmc.getInfoLabel( "ListItem.Path" ) and not xbmc.getInfoLabel( "container.folderpath" ) == "videodb://5/":

                    if not self.default_folder:
                        self.newpath = self.custom_path + xbmc.getInfoLabel( "ListItem.TVShowTitle" )
                    else:
                        self.newpath = xbmc.getInfoLabel( "ListItem.Path" )

                    if not self.newpath == self.oldpath and not self.newpath == "" and not self.newpath == "videodb://2/2/":
                        log( "### old path: %s" % self.oldpath )
                        log( "### new path: %s" % self.newpath )
                        self.oldpath = self.newpath
                        if not xbmc.Player().isPlaying() : self.start_playing()
                        else: log( "### player already playing" )

                if xbmc.getInfoLabel( "Window(10025).Property(TvTunesIsAlive)" ) == "true" and not xbmc.Player().isPlaying():
                    log( "### playing ends" )
                    if self.loud: self.raise_volume()
                    xbmcgui.Window( 10025 ).clearProperty('TvTunesIsAlive')

                if xbmc.getCondVisibility( "Container.Content(tvshows)" ) and self.playpath and not xbmc.getCondVisibility( "Window.IsVisible(12003)" ):
                    log( "### reinit condition" )
                    self.newpath = ""
                    self.oldpath = ""
                    self.playpath = ""
                    log( "### stop playing" )
                    xbmc.Player().stop()
                    if self.loud: self.raise_volume()
                    xbmcgui.Window( 10025 ).clearProperty('TvTunesIsAlive')

                time.sleep( .5 )
                if xbmc.getCondVisibility( CONDITION_REFRESH_SETTINGS ):
                    self.refresh_settings = True
                elif self.refresh_settings:
                    globals().update( { "__addon__": xbmcaddon.Addon('script.tvtunes') } )
                    self.get_settings()
                    # reset refresh status
                    self.refresh_settings = False
                    if __addon__.getSetting( "useplayerv2" ).lower() == "true":
                        #change player
                        self.stop( True )
        except SystemExit:
            log( "SystemExit!" )
            self.stop()
        except:
            print_exc()
            self.stop()

    def get_volume( self ):
        self.downvolume = int( float( __addon__.getSetting( "downvolume" ) ) * 60.0 / 100.0 )
        try: volume = int(xbmc.getInfoLabel('player.volume').split(".")[0])
        except: volume = int(xbmc.getInfoLabel('player.volume').split(",")[0])
        log( "### current volume: %s%%" % (( 60 + volume )*(100/60.0)) )
        log( "### downvolume: %s" % str(self.downvolume) )
        return volume

    def lower_volume( self ):
        try:
            self.base_volume = self.get_volume()
            self.loud = True
            vol = ((60+self.base_volume-self.downvolume )*(100/60.0))
            if vol < 0 : vol = 0
            log( "### volume goal: %s%% " % vol )
            xbmc.executebuiltin('XBMC.SetVolume(%d)' % vol)
            log( "### down volume to %d%%" % vol )
        except:
            print_exc()

    def raise_volume( self ):
        try:
            self.base_volume = self.get_volume()
            vol = ((60+self.base_volume+self.downvolume )*(100/60.0))
            if vol > 100 : vol = 100
            log( "### volume goal : %s%% " % vol )
            log( "### raise volume to %d%% " % vol )
            xbmc.executebuiltin( 'XBMC.SetVolume(%d)' % vol )
            self.loud = False
        except:
            print_exc()

    def start_playing( self ):
        path = xbmc.getInfoLabel( "ListItem.Path" )
        path2 = tvshowtitle = ""
        if not self.default_folder:
            path2 = os.path.dirname( self.newpath )
            tvshowtitle = os.path.basename( self.newpath )
        self.playpath = getThemePath( path, path2, tvshowtitle, self.default_folder, self.separate_folder )
        
        """
        if params.get("smb", "false" ) == "true" and self.newpath.startswith("smb://") : 
            log( "### Try authentification share" )
            self.newpath = self.newpath.replace("smb://", "smb://%s:%s@" % (params.get("user", "guest" ) , params.get("password", "guest" )) )
            log( "### %s" % self.newpath )

        #######hack for episodes stored as rar files
        if 'rar://' in str(self.newpath):
            self.newpath = self.newpath.replace("rar://","")

        #######hack for TV shows stored as ripped disc folders
        if 'VIDEO_TS' in str(self.newpath):
            log( "### FOUND VIDEO_TS IN PATH: Correcting the path for DVDR tv shows" )
            uppedpath = self._updir( self.newpath, 3 )
            if xbmcvfs.exists( os.path.join ( uppedpath , "theme.mp3" )):
                self.playpath = os.path.join ( uppedpath , "theme.mp3" )
            else:
                self.playpath = os.path.join ( self._updir(uppedpath,1) , "theme.mp3" )
        #######end hack
        
        elif xbmcvfs.exists( os.path.join ( self.newpath , "theme.mp3" ) ):
            self.playpath = os.path.join ( self.newpath , "theme.mp3" )
        elif xbmcvfs.exists(os.path.join(os.path.dirname( os.path.dirname( self.newpath ) ) , "theme.mp3")):
            self.playpath = (os.path.join(os.path.dirname( os.path.dirname( self.newpath ) ) , "theme.mp3"))
        else: self.playpath = False
        """

        if self.playpath:
            if not self.loud: self.lower_volume()
            xbmcgui.Window( 10025 ).setProperty( "TvTunesIsAlive", "true" )
            log( "### start playing %s" % self.playpath )
            playlist = self._repeat()
            if playlist is not None: xbmc.Player().play( playlist )
            else: xbmc.Player().play( self.playpath )
            #if params.get("loop", "false" ) == "true" : xbmc.executebuiltin('XBMC.PlayerControl(Repeat)')
            #else: xbmc.executebuiltin('XBMC.PlayerControl(RepeatOff)')
            if self.notify:
                self.notify = False
                self._notification( Language( 32000 ).encode( "utf-8" ),
                    LangXBMC( ( 595, 597, 596 )[ int( __addon__.getSetting( "loop2" ) ) ] ).encode( "utf-8" )
                    )

        else: log( "### no theme found for %s or %s" % ( os.path.join( self.newpath , "theme.mp3" ) , os.path.join ( os.path.dirname( os.path.dirname ( self.newpath ) ) , "theme.mp3" ) ) )

    def _notification( self, header="", message="", sleep=4000, icon=__addon__.getAddonInfo( "icon" ) ):
        """ Will display a notification dialog with the specified header and message,
            in addition you can set the length of time it displays in milliseconds and a icon image.
        """
        xbmc.executebuiltin( "Notification(%s,%s,%i,%s)" % ( header, message, sleep, icon ) )

    def _repeat( self ):
        self.repeat = ( "Off", "", "One" )[ int( __addon__.getSetting( "loop2" ) ) ]
        self.notify = __addon__.getSetting( "loopnotify" ) == "true"
        playlist = None
        if self.repeat != "Off":
            playlist = xbmc.PlayList( xbmc.PLAYLIST_MUSIC )
            playlist.clear()
            for x in xrange( ( 25, 2 )[ self.repeat == "One" ] ):
                playlist.add( self.playpath )
        return playlist

    def _updir(self, thepath, x):
        # move up x directories on thepath
        while x > 0:
            x -= 1
            thepath = (os.path.split(thepath))[0]
        return thepath

    def stop( self, loadplayerv2=False ):
        if xbmc.getInfoLabel( "Window(10025).Property(TvTunesIsAlive)" ) == "true" and not xbmc.Player().isPlayingVideo(): 
            log( "### stop playing" )
            xbmc.Player().stop()
        xbmcgui.Window( 10025 ).clearProperty('TvTunesIsRunning')
        xbmcgui.Window( 10025 ).clearProperty('TvTunesIsAlive')
        
        if self.loud: self.raise_volume()
        log( "### Stopping TvTunes Backend ###" )
        self._stop = True
        if loadplayerv2:
            xbmc.executebuiltin( 'RunScript(script.tvtunes,backend=true)' )


xbmcgui.Window( 10025 ).setProperty( "TvTunesIsRunning", "true" )
thread = mythread()
# start thread
thread.start()
