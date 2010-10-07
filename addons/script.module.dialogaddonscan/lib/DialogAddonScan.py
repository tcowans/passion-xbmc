
import os
import sys
import time
from traceback import print_exc

import xbmc
import xbmcgui
from xbmcaddon import Addon

__settings__  = Addon( "script.module.dialogaddonscan" )
__addonName__ = __settings__.getAddonInfo( "name" )
__addonDir__  = __settings__.getAddonInfo( "path" )

XBMC_SKIN  = xbmc.getSkinDir()
SKINS_PATH = os.path.join( __addonDir__, "resources", "skins" )
ADDON_SKIN = ( "default", XBMC_SKIN )[ os.path.exists( os.path.join( SKINS_PATH, XBMC_SKIN ) ) ]
MEDIA_PATH = os.path.join( SKINS_PATH, ADDON_SKIN, "media" )

# WINDOW DEFAULT COORDINATES
WINDOW_POSX = 720
WINDOW_POSY = 0

# FONTS
FONT_HEADING = "font10_title", '0xFFEB9E17'
FONT_LINE    = "font10", '0xFFFFFFFF'

# TEXTURES
TEXTURE_BG               = os.path.join( MEDIA_PATH, "BackgroundPanel.png" )
PROGRESS_TEXTURE_BG      = os.path.join( MEDIA_PATH, "ProgressBack.png" )
PROGRESS_TEXTURE_LEFT    = os.path.join( MEDIA_PATH, "ProgressLeft.png" )
PROGRESS_TEXTURE_MID     = os.path.join( MEDIA_PATH, "ProgressFront.png" )
PROGRESS_TEXTURE_RIGHT   = os.path.join( MEDIA_PATH, "ProgressRight.png" )
PROGRESS_TEXTURE_OVERLAY = os.path.join( MEDIA_PATH, "ProgressOverlay.png" )

# VALIDE TEXTURES
TEXTURE_BG               = ( "", TEXTURE_BG )[ os.path.exists( TEXTURE_BG ) ]
PROGRESS_TEXTURE_BG      = ( "", PROGRESS_TEXTURE_BG )[ os.path.exists( PROGRESS_TEXTURE_BG ) ]
PROGRESS_TEXTURE_LEFT    = ( "", PROGRESS_TEXTURE_LEFT )[ os.path.exists( PROGRESS_TEXTURE_LEFT ) ]
PROGRESS_TEXTURE_MID     = ( "", PROGRESS_TEXTURE_MID )[ os.path.exists( PROGRESS_TEXTURE_MID ) ]
PROGRESS_TEXTURE_RIGHT   = ( "", PROGRESS_TEXTURE_RIGHT )[ os.path.exists( PROGRESS_TEXTURE_RIGHT ) ]
PROGRESS_TEXTURE_OVERLAY = ( "", PROGRESS_TEXTURE_OVERLAY )[ os.path.exists( PROGRESS_TEXTURE_OVERLAY ) ]


class xbmcguiWindowError( WindowsError ):
    def __init__( self, winError=None ):
        WindowsError.__init__( self, winError )


class Window:
    def __init__( self, parent_win=None, **kwargs ):
        # http://wiki.xbmc.org/index.php?title=Window_IDs
        self.window = parent_win

        self.background = None
        self.heading = None
        self.label = None
        self.progress1 = None
        self.progress2 = None

    def setupWindow( self ):
        error = 0
        try: xbmcgui.lock()
        except: pass
        #get the id for the current 'active' window as an integer.
        try: current_window = xbmcgui.getCurrentWindowId()
        except: current_window = self.window

        #if self.window is None and hasattr( current_window, "__int__" ):
        #    self.window = xbmcgui.Window( current_window )
        if hasattr( current_window, "__int__" ) and current_window != self.window:
            self.removeControls()
            self.window = xbmcgui.Window( current_window )
            self.initialize()

        #print hasattr( self.window, "addControl" )
        if not self.window or not hasattr( self.window, "addControl" ):
            self.removeControls()
            error = 1

        xbmcgui.unlock()
        if error:
            raise xbmcguiWindowError( "xbmcgui.Window(%s)" % repr( current_window ) )

    def initialize( self ):
        try:
            # http://passion-xbmc.org/gros_fichiers/XBMC%20Python%20Doc/xbmc_svn/xbmcgui.html#ControlImage
            # BACKGROUND
            self.background = xbmcgui.ControlImage( WINDOW_POSX, WINDOW_POSY, 400, 70, TEXTURE_BG )
            self.window.addControl( self.background )

            # http://passion-xbmc.org/gros_fichiers/XBMC%20Python%20Doc/xbmc_svn/xbmcgui.html#ControlLabel
            # HEADING
            self.heading = xbmcgui.ControlLabel( WINDOW_POSX+15, WINDOW_POSY+4, 370, 18,
                self.header,
                FONT_HEADING[ 0 ],
                FONT_HEADING[ 1 ]
                )
            self.window.addControl( self.heading )

            # LABEL
            self.label = xbmcgui.ControlLabel( WINDOW_POSX+15, WINDOW_POSY+20, 370, 18,
                self.line,
                FONT_LINE[ 0 ],
                FONT_LINE[ 1 ]
                )
            self.window.addControl( self.label )

            # http://passion-xbmc.org/gros_fichiers/XBMC%20Python%20Doc/xbmc_svn/xbmcgui.html#ControlProgress
            # CURRENT PROGRESS
            self.progress1 = xbmcgui.ControlProgress( WINDOW_POSX+15, WINDOW_POSY+38, 370, 8,
                texturebg=PROGRESS_TEXTURE_BG,
                textureleft=PROGRESS_TEXTURE_LEFT,
                texturemid=PROGRESS_TEXTURE_MID,
                textureright=PROGRESS_TEXTURE_RIGHT,
                textureoverlay=PROGRESS_TEXTURE_OVERLAY
                )
            self.window.addControl( self.progress1 )

            # PROGRESS OF LISTING
            self.progress2 = xbmcgui.ControlProgress( WINDOW_POSX+15, WINDOW_POSY+45, 370, 8,
                texturebg=PROGRESS_TEXTURE_BG,
                textureleft=PROGRESS_TEXTURE_LEFT,
                texturemid=PROGRESS_TEXTURE_MID,
                textureright=PROGRESS_TEXTURE_RIGHT,
                textureoverlay=PROGRESS_TEXTURE_OVERLAY
                )
            self.window.addControl( self.progress2 )
        except:
            print_exc()

    def removeControls( self ):
        if self.progress2:
            try: self.window.removeControl( self.progress2 )
            except: pass
        if self.progress1:
            try: self.window.removeControl( self.progress1 )
            except: pass
        if self.label:
            try: self.window.removeControl( self.label )
            except: pass
        if self.heading:
            try: self.window.removeControl( self.heading )
            except: pass
        if self.background:
            try: self.window.removeControl( self.background )
            except: pass


class AddonScan( Window ):
    def __init__( self, parent_win=None, **kwargs ):
        # get class Window object
        Window.__init__( self, parent_win, **kwargs )

        self.header = ""
        self.line = ""

    def close( self ):
        self.removeControls()

    def create( self, line1="", line2="" ):
        self.header = line1 or __addonName__
        self.line   = line2
        self.update( 0, 0, line1, line2 )

    def iscanceled( self ):
        pass

    def update( self, percent1=0, percent2=0, line1="", line2="" ):
        self.setupWindow()
        if line1:
            # set heading
            try: self.heading.setLabel( line1 )
            except: print_exc()
        if line2:
            # set label
            self.line = line2
            try: self.label.setLabel( line2 )
            except: print_exc()
        if percent1:
            # set current progress
            try: self.progress1.setPercent( percent1 )
            except: print_exc()
        if percent2: 
            # set progress of listing
            try: self.progress2.setPercent( percent2 )
            except: print_exc()


def Demo():
    scan = AddonScan()
    # create dialog
    scan.create( "Demo: "+__addonName__ )

    for pct in range( 101 ):
        percent2 = pct
        percent1 = percent2*10
        while percent1 > 100:
            percent1 -= 100
        line2 = "Progress1 [B]%i%%[/B]   |   Progress2 [B]%i%%[/B]" % ( percent1, percent2 )

        # update dialog ( [ int1, int2, line1=str, line2=str ] ) all args optional
        scan.update( percent1, percent2, line2=line2 )
        time.sleep( .25 )

    # close dialog and auto destroy all controls
    scan.close()



if ( __name__ == "__main__" ):
    try:
        #args = "dit moi quoi faire :)"
        print sys.argv[ 1 ]
    except:
        print "ok rien ...."

    Demo()
