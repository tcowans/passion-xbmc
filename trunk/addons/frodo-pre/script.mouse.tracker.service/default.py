
# http://activeden.net/item/reaistic-spider-mouse-tracker/59425


import os
import time
#from threading import Thread
from traceback import print_exc

import xbmc
import xbmcgui
from xbmcaddon import Addon


class windowXML( xbmcgui.WindowXMLDialog ):
    """ The main GUI """

    def __init__( self, *args, **kwargs ):
        self.spriteDir = kwargs[ "spriteDir" ]
        self.controls = {}
        self.doModal()

    def onAction( self, action ):
        pass

    def onClick( self, controlID ):
        pass

    def onFocus( self, controlID ):
        pass

    def onInit( self ):
        try:
            self.control = self.getControl( 3001 )
            self.sprites = {
                "wait":  self.getTexture( xbmc.getInfoLabel( "Control.GetLabel(3001)" ) ),
                "right": self.getTexture( xbmc.getInfoLabel( "Control.GetLabel(3002)" ) ),
                "left":  self.getTexture( xbmc.getInfoLabel( "Control.GetLabel(3003)" ) ),
                "sfx":   xbmc.getInfoLabel( "Control.GetLabel(3010)" ).strip( "-" ) }
            if self.sprites[ "sfx" ]:
                self.sprites[ "sfx" ] = os.path.join( self.spriteDir, self.sprites[ "sfx" ] )
                if not os.path.exists( self.sprites[ "sfx" ] ): self.sprites[ "sfx" ] = ""
        except:
            print_exc()
        self.close()

    def getTexture( self, texture ):
        """ verifie si la texture existe dans le XBT du skin en cours,
            sinon retourne le chemin complet
        """
        if not texture or os.path.exists( texture ) or xbmc.skinHasImage( texture ):
            return texture

        # check in xbmc skin
        skinpath = xbmc.translatePath( "special://skin" )
        if os.path.exists( os.path.join( skinpath, texture ) ):
            texture = os.path.join( skinpath, texture )
        # check in xbmc skin media
        elif os.path.exists( os.path.join( skinpath, "media", texture ) ):
            texture = os.path.join( skinpath, "media", texture )
        # check in add-on skins
        elif os.path.exists( os.path.join( self.spriteDir, texture ) ):
            texture = os.path.join( self.spriteDir, texture )

        return texture


class MouseTracker:#( Thread ):
    def __init__( self ):
        #Thread.__init__( self )

        self.winId  = None
        self.window = None

        self.reload_addon = False
        self.addon = Addon( "script.mouse.tracker.service" )

        self.getMedias()
        self.current_pos = ( 0, 0 )

        self.run()
        #self.start()

    def getMedias( self ):
        self.sprite = self.addon.getSetting( "sprite" ) #"Dog"
        self.speed  = self.addon.getSetting( "speed" ).split( "." )[ 0 ] #"300"
        try:
            # get control and sprites in xml
            spriteDir = os.path.join( self.addon.getAddonInfo( "path" ), "resources", "skins", self.sprite, "media" )
            xml = windowXML( "%s.xml" % self.sprite, self.addon.getAddonInfo( "path" ), self.sprite, spriteDir=spriteDir )
            # get our controls, before del xml
            self.image = xml.control
            self.sprites = xml.sprites
            # del window object
            del xml
            self.imgId = self.image.getId()
            self.offsetx = 0 #self.image.getPosition()[ 0 ]
        except:
            print_exc()
            raise

    def getWindow( self ):
        current_win_id = xbmcgui.getCurrentWindowId()
        if self.winId != current_win_id or not self.window:
            self.winId = current_win_id
            self.window = xbmcgui.Window( self.winId )
            self.getControl()

    def getControl( self ):
        self.window.addControl( self.image )
        self.imgId = self.image.getId()
        self.control = self.window.getControl( self.imgId )
        self.control.setVisibleCondition( 'Window.IsActive(Pointer.xml)' )
        self.setAnimation( xbmcgui.getMousePosition() )#, (640,360) )#self.control.getPosition() )

    def setAnimation( self, pos, start="" ):
        if start: start = "%i,%i" % start
        else: start = "%i,%i" % self.current_pos
        end   = "%i,%i" % ( pos[ 0 ]-self.offsetx, pos[ 1 ] )
        #self.speed = str( self.current_pos[ 0 ] - pos[ 0 ] ).strip( "-" )
        self.control.setAnimations( [ ( 'conditional', 'condition=true effect=slide start=%s end=%s time=%s' % ( start, end, self.speed ) ) ] )

    def run( self ):
        try:
            play_sfx = False
            # NB: xbmc.abortRequested not work correctly with threading.Thread
            while not xbmc.abortRequested:
                try:
                    self.getWindow()
                    if self.sprite != self.addon.getSetting( "sprite" ):
                        self.getMedias()
                    
                    if not xbmc.getCondVisibility( 'Window.IsActive(Pointer.xml)' ):
                        time.sleep( .3 )
                        continue

                    pos = xbmcgui.getMousePosition()

                    if ( ( pos[ 0 ]-self.offsetx ) == self.current_pos[ 0 ] ) and ( pos[ 1 ] == self.current_pos[ 1 ] ):
                        self.control.setImage( self.sprites[ "wait" ] )
                        if play_sfx:
                            if self.sprites[ "sfx" ] and self.addon.getSetting( "playsfx" ) == "true":
                                xbmc.playSFX( self.sprites[ "sfx" ] )
                            play_sfx = False
                    else:
                        play_sfx = True
                        if pos[ 0 ] < self.current_pos[ 0 ]:
                            self.control.setImage( self.sprites[ "left" ] )
                        else:
                            self.control.setImage( self.sprites[ "right" ] )

                        #start = "%i,%i" % self.current_pos
                        #end   = "%i,%i" % ( pos[ 0 ]-self.offsetx, pos[ 1 ] )
                        ##self.speed = str( self.current_pos[ 0 ] - pos[ 0 ] ).strip( "-" )
                        #self.control.setAnimations( [ ( 'conditional', 'condition=true effect=slide start=%s end=%s time=%s' % ( start, end, self.speed ) ) ] )
                        self.setAnimation( pos )

                        self.current_pos = ( pos[ 0 ]-self.offsetx, pos[ 1 ] )
                        #self.control.setPosition( *self.current_pos )

                    if xbmc.getCondVisibility( "Window.IsActive(addonsettings)" ):
                        self.reload_addon = True
                    elif self.reload_addon:
                        self.addon = Addon( "script.mouse.tracker.service" )
                        self.speed = self.addon.getSetting( "speed" ).split( "." )[ 0 ]
                        self.reload_addon = False
                except SystemExit:
                    break
                except:
                    print_exc()

                time.sleep( float( int( self.speed ) ) * 0.001 )
        except SystemExit:
            pass
        except:
            print_exc()

if hasattr( xbmcgui, "getMousePosition" ):
    MouseTracker()
