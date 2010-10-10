
import os
import sys
from traceback import print_exc

import xbmc
import xbmcgui
from xbmcaddon import Addon


__settings__  = Addon( "script.module.dialogaddonscan" )
__addonDir__  = __settings__.getAddonInfo( "path" )

XBMC_SKIN  = xbmc.getSkinDir()
SKINS_PATH = os.path.join( __addonDir__, "resources", "skins" )
ADDON_SKIN = ( "default", XBMC_SKIN )[ os.path.exists( os.path.join( SKINS_PATH, XBMC_SKIN ) ) ]
MEDIA_PATH = os.path.join( SKINS_PATH, ADDON_SKIN, "media" )


class xbmcguiWindowError( WindowsError ):
    def __init__( self, winError=None ):
        WindowsError.__init__( self, winError )


class Control:
    def __init__( self, control, coords=( 0, 0 ), anim=[], **kwargs ):
        self.controlXML = control
        self.id = self.controlXML.getId()
        self.label = xbmc.getInfoLabel( "Control.GetLabel(%i) " % self.id )
        self.anim = anim

        option = {}
        x, y, w, h = self.getCoords( coords )
        if type( self.controlXML ) == xbmcgui.ControlImage:
            # http://passion-xbmc.org/gros_fichiers/XBMC%20Python%20Doc/xbmc_svn/xbmcgui.html#ControlImage
            ex = {}
            if self.label.count( "=" ) or self.label.count( "," ):
                try: ex = dict( [ k.split( "=" ) for k in self.label.split( "," ) ] )
                except: pass
            texture = self.label
            valide = "colorKey, aspectRatio, colorDiffuse".split( ", " )
            for key, value in ex.items():
                if key == "texture": texture = value
                if key not in valide: continue
                option[ key ] = value
                if "color" in key.lower():
                    option[ key ] = '0x' + value
                elif key == "aspectRatio" and value.isdigit():
                    option[ key ] = int( value )
            if not xbmc.skinHasImage( texture ):
                if os.path.isfile( os.path.join( MEDIA_PATH, texture ) ):
                    texture = os.path.join( MEDIA_PATH, texture )
                else:
                    texture = ""
            # ControlImage( x, y, width, height, filename[, colorKey, aspectRatio, colorDiffuse] )
            self.control = xbmcgui.ControlImage( x, y, w, h, texture, **option )

        elif type( self.controlXML ) == xbmcgui.ControlLabel:
            # http://passion-xbmc.org/gros_fichiers/XBMC%20Python%20Doc/xbmc_svn/xbmcgui.html#ControlLabel
            try: ex = dict( [ k.split( "=" ) for k in self.label.split( "," ) ] )
            except: ex = {}
            valide = "font, textColor, disabledColor, alignment, hasPath, angle".split( ", " )
            for key, value in ex.items():
                if key not in valide: continue
                option[ key ] = value
                if "color" in key.lower():
                    option[ key ] = '0x' + value
                elif key == "alignment":
                    option[ key ] = self.getAlignment( value )
                elif key == "hasPath" and value == "true":
                    option[ key ] = True
                elif key == "angle" and value.isdigit():
                    option[ key ] = int( value )
            # ControlLabel(x, y, width, height, label[, font, textColor, disabledColor, alignment, hasPath, angle])
            self.control = xbmcgui.ControlLabel( x, y, w, h, "", **option )

        elif type( self.controlXML ) == xbmcgui.ControlProgress:
            # http://passion-xbmc.org/gros_fichiers/XBMC%20Python%20Doc/xbmc_svn/xbmcgui.html#ControlProgress
            #option = {'texturebg': 'ProgressBack.png', 'texturemid': 'ProgressFront.png'}
            valide = "texturebg, textureleft, texturemid, textureright, textureoverlay".split( ", " )
            for key, img in kwargs.items():
                if key not in valide: continue
                if not img: option[ key ] = ""
                elif xbmc.skinHasImage( img ): option[ key ] = img
                elif os.path.isfile( os.path.join( MEDIA_PATH, img ) ):
                    option[ key ] = os.path.join( MEDIA_PATH, img )
            #ControlProgress(x, y, width, height[, texturebg, textureleft, texturemid, textureright, textureoverlay])
            self.control = xbmcgui.ControlProgress( x, y, w, h,  **option )

    def getCoords( self, default ):
        x, y = self.controlXML.getPosition()
        w, h = self.controlXML.getWidth(), self.controlXML.getHeight()
        try:
            if __settings__.getSetting( "custompos" ) == "true":
                default = ( int( float( __settings__.getSetting( "customposx" ) ) ),
                            int( float( __settings__.getSetting( "customposy" ) ) ) )
        except:
            print_exc()
        return ( default[ 0 ] + x, default[ 1 ] + y, w, h )

    def getAlignment( self, alignment ):
        xbfont = {
            "left"     : 0x00000000,
            "right"    : 0x00000001,
            "centerx"  : 0x00000002,
            "centery"  : 0x00000004,
            "truncated": 0x00000008
            }
        align = xbfont[ "left" ]
        for a in alignment.split( "+" ):
            align += xbfont.get( a, xbfont[ "left" ] )
        return align

    def setAnimations( self ):
        if self.anim and __settings__.getSetting( "animation" ) == "true":
            try: self.control.setAnimations( self.anim )
            except: print_exc()

    def addControl( self, window ):
        window.addControl( self.control )
        self.control.setVisibleCondition( "[SubString(Window.Property(DialogAddonScan.Hide),false) | SubString(Window.Property(DialogAddonScan.Hide),)]" )
        self.setAnimations()
        return self.control


class DialogAddonScanXML( xbmcgui.WindowXMLDialog ):
    def __init__( self, *args, **kwargs ):
        xbmcgui.WindowXMLDialog.__init__( self, *args, **kwargs )
        self.doModal()

    def onInit( self ):
        self.controls = {}
        try:
            xbmcgui.lock()
            self.getControls()
        except:
            print_exc()
        xbmcgui.unlock()
        self.close()

    def getControls( self ):
        coordinates = self.getControl( 2000 ).getPosition()

        c_anim = []
        try:
            import re
            for anim in re.findall( "(\[.*?\])", xbmc.getInfoLabel( "Control.GetLabel(1999)" ), re.S ):
                try: c_anim.append( tuple( eval( anim ) ) )
                except: pass
        except:
            print_exc()

        self.controls[ "background" ] = Control( self.getControl( 2001 ), coordinates, c_anim )

        self.controls[ "heading" ] = Control( self.getControl( 2002 ), coordinates, c_anim )

        self.controls[ "label" ] = Control( self.getControl( 2003 ), coordinates, c_anim )

        try:
            v = xbmc.getInfoLabel( "Control.GetLabel(2045)" ).replace( ", ", "," )
            progressTextures = dict( [ k.split( "=" ) for k in v.split( "," ) ] )
        except:
            progressTextures = {}

        self.controls[ "progress1" ] = Control( self.getControl( 2004 ), coordinates, c_anim, **progressTextures )

        self.controls[ "progress2" ] = Control( self.getControl( 2005 ), coordinates, c_anim, **progressTextures )

    def onFocus( self, controlID ):
        pass

    def onClick( self, controlID ):
        pass

    def onAction( self, action ):
        if action in [ 9, 10, 117 ]:
            self.close()


class Window:
    def __init__( self, parent_win=None, **kwargs ):
        if xbmc.getInfoLabel( "Window.Property(DialogAddonScan.IsAlive)" ) == "true":
            raise xbmcguiWindowError( "DialogAddonScan IsAlive: Not possible to overscan!" )

        windowXml = DialogAddonScanXML( "DialogAddonScan.xml", __addonDir__, ADDON_SKIN )
        self.controls = windowXml.controls
        del windowXml

        self.window   = parent_win
        self.windowId = parent_win

        self.background = None
        self.heading    = None
        self.label      = None
        self.progress1  = None
        self.progress2  = None

    def setupWindow( self ):
        error = 0
        try: xbmcgui.lock()
        except: pass
        #get the id for the current 'active' window as an integer.
        # http://wiki.xbmc.org/index.php?title=Window_IDs
        try: currentWindowId = xbmcgui.getCurrentWindowId()
        except: currentWindowId = self.window

        if hasattr( self.window, "getProperty" ):
            self.canceled = ( self.window.getProperty( "DialogAddonScan.Cancel" ) == "true" )
        if hasattr( self.window, "setProperty" ):
            self.window.setProperty( "DialogAddonScan.Hide", __settings__.getSetting( "hidedialog" ) )

        #if self.window is None and hasattr( currentWindowId, "__int__" ):
        #    self.window = xbmcgui.Window( currentWindowId )
        if hasattr( currentWindowId, "__int__" ) and currentWindowId != self.windowId:
            self.removeControls()
            self.windowId = currentWindowId
            self.window = xbmcgui.Window( self.windowId )
            self.initialize()

        if not self.window or not hasattr( self.window, "addControl" ):
            self.removeControls()
            error = 1

        self.window.setProperty( "DialogAddonScan.Hide", __settings__.getSetting( "hidedialog" ) )
        xbmcgui.unlock()
        if error:
            raise xbmcguiWindowError( "xbmcgui.Window(%s)" % repr( currentWindowId ) )

        #self.canceled = ( self.window.getProperty( "DialogAddonScan.Cancel" ) == "true" )
        self.window.setProperty( "DialogAddonScan.IsAlive", "true" )

    def initialize( self ):
        try:
            # BACKGROUND
            self.background = self.controls[ "background" ].addControl( self.window )
        except:
            print_exc()
        try:
            # HEADING
            self.heading = self.controls[ "heading" ].addControl( self.window )
            self.heading.setLabel( self.header )
        except:
            print_exc()
        try:
            # LABEL
            self.label = self.controls[ "label" ].addControl( self.window )
            self.label.setLabel( self.line )
        except:
            print_exc()
        try:
            # CURRENT PROGRESS
            self.progress1 = self.controls[ "progress1" ].addControl( self.window )
        except:
            print_exc()
        try:
            # PROGRESS OF LISTING
            self.progress2 = self.controls[ "progress2" ].addControl( self.window )
        except:
            print_exc()

    def removeControls( self ):
        if hasattr( self.window, "removeControl" ):
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
        if hasattr( self.window, "clearProperty" ):
            self.window.clearProperty( "DialogAddonScan.Hide" )
            self.window.clearProperty( "DialogAddonScan.Cancel" )
            self.window.clearProperty( "DialogAddonScan.IsAlive" )
