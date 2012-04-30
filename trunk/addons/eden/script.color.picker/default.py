
DEBUG = False

#Modules General
import os
import time
from sys import argv
from glob import glob
from traceback import print_exc

# Modules XBMC
import xbmc
import xbmcgui
import xbmcvfs
from xbmcaddon import Addon

from resources.lib.pil_utils import *


if not hasattr( xbmcgui, "getMousePosition" ):
    skinWidth, skinHeight = 1280, 720
    def _getMousePosition( win ):
        #action.getAmount1-2 VS xbmcgui.getMousePosition
        point_x, point_y = 0, 0
        try:
            #transform the amounts coordinates to this window's coordinates
            #but is not real, if g_guiSkinzoom = (CSettingInt*)g_guiSettings.GetSetting("lookandfeel.skinzoom");
            #for info see https://github.com/xbmc/xbmc/blob/master/xbmc/guilib/GraphicContext.cpp#L568
            point_x = win.amount1 * skinWidth  / float( win.getWidth() )
            point_y = win.amount2 * skinHeight / float( win.getHeight() )
        except:
            print_exc()
        return int( point_x ), int( point_y )

    xbmcgui.getMousePosition = _getMousePosition


# Constants
ADDON      = Addon( "script.color.picker" )
ADDON_DIR  = ADDON.getAddonInfo( "path" )

PALETTES_PATH = os.path.join( ADDON_DIR, "resources", "palettes" )
PIXELS_PATH   = xbmc.translatePath( ADDON.getAddonInfo( 'profile' ) + 'pixels' )
GRADIENT      = os.path.join( ADDON_DIR, "resources", "skins", "default", "media", "picker-gradient.png" )


# https://raw.github.com/xbmc/xbmc/master/xbmc/guilib/Key.h
ACTION_PARENT_DIR    = 9
ACTION_PREVIOUS_MENU = 10
ACTION_NAV_BACK      = 92
ACTION_MOUSE_MOVE    = 107
ACTION_CONTEXT_MENU  = 117
CLOSE_DIALOG         = [ ACTION_PARENT_DIR, ACTION_PREVIOUS_MENU, ACTION_NAV_BACK, ACTION_CONTEXT_MENU ]



def get_browse_dialog( default="", heading="", dlg_type=2, shares="pictures", mask="", use_thumbs=False, treat_as_folder=False ):
    """ shows a browse dialog and returns a value
        - 0 : ShowAndGetDirectory
        - 1 : ShowAndGetFile
        - 2 : ShowAndGetImage
        - 3 : ShowAndGetWriteableDirectory
    """
    dialog = xbmcgui.Dialog()
    value = dialog.browse( dlg_type, heading, shares, mask, use_thumbs, treat_as_folder, default )
    return value



class ColorPicker( xbmcgui.WindowXMLDialog ):
    def __init__( self, *args, **kwargs ):
        self.color_picked = kwargs.get( "colorPicked" )
        params = kwargs[ "params" ]
        self.builtin = params[ "builtin" ]
        # execute built-in in real time
        self.executeBuiltIn = params.get( "setstringinrealtime" ) == "true" and self.builtin.lower().startswith( "skin." )
        

        self.filename = xbmc.translatePath( ADDON.getSetting( "palette" ) )
        if not self.filename or not xbmcvfs.exists( self.filename ):
            self.filename = os.path.join( PALETTES_PATH, "color-wheel.png" )
            ADDON.setSetting( "palette", self.filename )

        self.image = None
        self.imageGradient = None
        self.loadImage( self.filename )

        self.slider_percent = ( "0", "0", "0", "0" )

    def loadImage( self, filename,  ):
        #del image objet
        try: del self.image
        except: pass
        self.image = IMAGE( filename )

    def onInit( self ):
        if DEBUG:
            xbmc.executebuiltin( "SetProperty(debug,debug)" )

        self.setProperty( "ImageColor", self.filename )

        self.offsetx, self.offsety = self.getControl( 300 ).getPosition()
        self.image.resize( ( self.getControl( 300 ).getWidth(), self.getControl( 300 ).getHeight() ) )
        #used if not xbmcgui hasattr getMousePosition
        self.amount1, self.amount2 = self.getOffSet( ( self.getWidth() / 2.0 ), ( self.getHeight() / 2.0 ) )

        self.fixe_rule_304 = self.getControl( 304 ).getPosition()[ 1 ]
        self.fixe_rule_305 = self.getControl( 305 ).getPosition()[ 0 ]
        self.fixe_rule_offset_304 = int( self.getControl( 304 ).getWidth() / 2.0 )
        self.fixe_rule_offset_305 = int( self.getControl( 305 ).getHeight() / 2.0 )

        self.addSavedColors()

        #previouscolor
        self.setProperty( "PreviousPickerColor", ADDON.getSetting( "previouscolor" ) )

        if self.color_picked:
            self.sendClick( 3001 )

    def addSavedColors( self, setfocus=False ):
        savedcolors = ADDON.getSetting( "savedcolors" ).split( "|" )
        listitems = []
        for color in savedcolors:
            argb = hex_to_argb( color )
            li = xbmcgui.ListItem( color, repr( argb ), createPixel( argb, PIXELS_PATH ) )
            listitems.append( li )
        self.getControl( 9001 ).reset()
        self.getControl( 9001 ).addItems( listitems )
        if setfocus: self.setFocusId( 9001 )

    def getOffSet( self, x, y ):
        return ( ( x - self.offsetx ), ( y - self.offsety ) )

    def onFocus( self, controlID ):
        pass

    def sendClick( self, controlID ):
        try: self.onClick( controlID )
        except: print_exc()

    def onClick( self, controlID ):
        colorPicked = None
        set_input_text = True
        set_slider_percent = True
        try:
            if controlID != 301:
                self.resetGradient()

            if controlID == 301:
                # get pixel clicked
                x, y = xbmcgui.getMousePosition( self )
                if self.imageGradient is not None:
                    colorPicked = self.imageGradient.getPixel( *self.getOffSet( x, y ) )
                else:
                    colorPicked = self.image.getPixel( *self.getOffSet( x, y ) )

            elif controlID == 141:
                # get value of input text
                value = self.getControl( 141 ).getText()
                self.setProperty( "CurrentPickerColor", "" )
                if value:
                    argb = None
                    # first check for name ( blue, red, pink ... )
                    try: argb = name_to_argb( value )
                    except:
                        # ValueError for check name last chance check hex
                        try: argb = hex_to_argb( value )
                        except: pass
                    if argb is not None:
                        color = argb_to_hex( argb )
                        if color:
                            colorPicked = argb
                            set_input_text = False

            elif controlID in [ 24, 25 ]:
                # change image to pick color
                default = ( self.filename, "" )[ controlID - 24 ]
                if default and ( PALETTES_PATH not in default ): default = os.path.join( PALETTES_PATH, "color-wheel.png" )#PALETTES_PATH + os.sep
                new_img = get_browse_dialog( default, xbmc.getInfoLabel( "System.CurrentControl" ) )
                if new_img and new_img != self.filename:
                    self.filename = new_img
                    self.loadImage( self.filename )
                    self.image.resize( ( self.getControl( 300 ).getWidth(), self.getControl( 300 ).getHeight() ) )
                    self.setProperty( "ImageColor", self.filename )
                    ADDON.setSetting( "palette", self.filename )

            elif controlID == 20:
                # add current color to user fav color
                # hmmm! xbmc.getInfoLabel broken on xbmc Built on Oct  3 2011 Git:20111003-fc543cb
                color = xbmc.getInfoLabel( "Container(50).Property(CurrentPickerColor)" )
                color = color or xbmc.getInfoLabel( "Control.GetLabel(142)" )
                color = color or self.getControl( 142 ).getLabel()
                savedcolors = ADDON.getSetting( "savedcolors" ).split( "|" )
                if color and color not in savedcolors:
                    ADDON.setSetting( "savedcolors", "|".join( [ color ] + savedcolors ) )
                    self.addSavedColors( True )

            elif controlID == 9001:
                #get color in saved colors
                colorPicked = eval( self.getControl( controlID ).getSelectedItem().getLabel2() )

            elif controlID == 21:
                #get color on fullscreen
                colorPicked = pickColorOnScreen()

            elif controlID == 22:
                # user accept color
                #color = self.getProperty( "CurrentPickerColor" ) # return empty !!
                # hmmm! xbmc.getInfoLabel broken on xbmc Built on Oct  3 2011 Git:20111003-fc543cb
                color = xbmc.getInfoLabel( "Container(50).Property(CurrentPickerColor)" )
                color = color or xbmc.getInfoLabel( "Control.GetLabel(142)" )
                color = color or self.getControl( 142 ).getLabel()
                if color:
                    self.color_picked = color
                    ADDON.setSetting( "previouscolor", color )
                self._close_dialog()

            elif controlID == 142:
                # ajust CurrentPickerColor with gradient
                # hmmm! xbmc.getInfoLabel broken on xbmc Built on Oct  3 2011 Git:20111003-fc543cb
                hexcolor = xbmc.getInfoLabel( "Container(50).Property(CurrentPickerColor)" )
                hexcolor = hexcolor or xbmc.getInfoLabel( "Control.GetLabel(142)" )
                hexcolor = hexcolor or self.getControl( 142 ).getLabel()
                img = createGradient( hex_to_argb( hexcolor ), GRADIENT, PIXELS_PATH )
                # test
                self.imageGradient = IMAGE( img )
                self.imageGradient.resize( ( self.getControl( 300 ).getWidth(), self.getControl( 300 ).getHeight() ) )
                self.setProperty( "ImageColor", img )

            elif controlID == 143:
                # get previous color
                # hmmm! xbmc.getInfoLabel broken on xbmc Built on Oct  3 2011 Git:20111003-fc543cb
                hexcolor = xbmc.getInfoLabel( "Container(50).Property(PreviousPickerColor)" )
                hexcolor = hexcolor or xbmc.getInfoLabel( "Control.GetLabel(143)" )
                hexcolor = hexcolor or self.getControl( 143 ).getLabel()
                colorPicked = hex_to_argb( hexcolor )

            elif controlID in [ 101, 111, 121, 131 ]:
                # ajust color with moved slider
                # NOTE: ON MULTIPLE CLICK/SCROLLING XBMC FREEZE !!!! AH ok is getInfoLabel :)
                p1 = self.slider_percent[ 0 ].strip( "%" ) #xbmc.getInfoLabel( "Container(50).Property(alpha_percent)" ).strip( "%" ) or "0"
                p2 = self.slider_percent[ 1 ].strip( "%" ) #xbmc.getInfoLabel( "Container(50).Property(red_percent)"   ).strip( "%" ) or "0"
                p3 = self.slider_percent[ 2 ].strip( "%" ) #xbmc.getInfoLabel( "Container(50).Property(green_percent)" ).strip( "%" ) or "0"
                p4 = self.slider_percent[ 3 ].strip( "%" ) #xbmc.getInfoLabel( "Container(50).Property(blue_percent)"  ).strip( "%" ) or "0"
                percent = self.getControl( controlID ).getPercent()
                #percent = int( xbmc.getInfoLabel( "Control.GetLabel(%i)" % controlID ).strip( "%" ) )
                if controlID == 131:
                    if 0 < percent < 100:
                        percent += float( "." + str( float( p1 ) ).split( "." )[ -1 ] )
                    p1 = percent
                elif controlID == 101:
                    if 0 < percent < 100:
                        percent += float( "." + str( float( p2 ) ).split( "." )[ -1 ] )
                    p2 = percent
                elif controlID == 111:
                    if 0 < percent < 100:
                        percent += float( "." + str( float( p3 ) ).split( "." )[ -1 ] )
                    p3 = percent
                elif controlID == 121:
                    if 0 < percent < 100:
                        percent += float( "." + str( float( p4 ) ).split( "." )[ -1 ] )
                    p4 = percent

                colorPicked = argb_percent_to_argb( ( float( p1 ), float( p2 ), float( p3 ), float( p4 ) ) )
                set_slider_percent = False

            elif controlID == 3001:
                # set color from pickcoloronscreen is startup window
                colorPicked = self.color_picked
                self.color_picked = None

            if colorPicked is not None:
                # now if colorPicked setup vars
                alpha, red, green, blue = colorPicked
                currentpickercolor = argb_to_hex( ( alpha, red, green, blue ) )
                #print 'Color: %s' % argb_to_hex( color )

                if self.executeBuiltIn:
                    #print self.builtin % currentpickercolor
                    xbmc.executebuiltin( self.builtin % currentpickercolor )

                self.setProperty( "CurrentPickerColor", currentpickercolor )
                if set_input_text:
                    self.getControl( 141 ).setText( currentpickercolor )

                self.slider_percent = argb_to_argb_percent( ( alpha, red, green, blue ) )
                p1, p2, p3, p4 = self.slider_percent
                # set real info labels
                self.setProperty( "alpha_percent", p1 )
                self.setProperty( "red_percent",   p2 )
                self.setProperty( "green_percent", p3 )
                self.setProperty( "blue_percent",  p4 )

                if set_slider_percent:
                    self.getControl( 131 ).setPercent( float( p1.strip( "%" ) ) )
                    self.getControl( 101 ).setPercent( float( p2.strip( "%" ) ) )
                    self.getControl( 111 ).setPercent( float( p3.strip( "%" ) ) )
                    self.getControl( 121 ).setPercent( float( p4.strip( "%" ) ) )

                self.resetGradient()
        except:
            print_exc()

    def resetGradient( self ):
        if self.imageGradient is not None:
            # replace image
            self.setProperty( "ImageColor", self.filename )
            try: del self.imageGradient
            except: pass
            self.imageGradient = None

    def setFocusColor( self ):
        try:
            if self.getFocusId() == 301:
                x, y = xbmcgui.getMousePosition( self )
                self.getControl( 303 ).setPosition( x, y )
                self.getControl( 304 ).setPosition( ( x - self.fixe_rule_offset_304 ), self.fixe_rule_304 )
                self.getControl( 305 ).setPosition( self.fixe_rule_305, ( y - self.fixe_rule_offset_305 ) )

                self.setProperty( "MousePosX", str( x ) )
                self.setProperty( "MousePosY", str( y ) )
                self.setProperty( "MouseCoords", "Pipette: (%i,%i)" % self.getOffSet( x, y ) )

                try:
                    if self.imageGradient is not None:
                        color = self.imageGradient.getPixel( *self.getOffSet( x, y ) )
                    else:
                        color = self.image.getPixel( *self.getOffSet( x, y ) )
                    currentfocuscolor = argb_to_hex( color )
                    self.setProperty( "CurrentFocusColor", currentfocuscolor )
                except IndexError:
                    pass

                if DEBUG:
                    label = "[COLOR=%s]X: %i[CR]Y: %i[/COLOR]" % ( currentfocuscolor, x, y )
                    self.getControl( 302 ).setLabel( label )
                    self.getControl( 302 ).setPosition( x, y )
        except:
            print_exc()

    def onAction( self, action ):
        if action == ACTION_MOUSE_MOVE:
            self.amount1 = action.getAmount1()
            self.amount2 = action.getAmount2()
            self.setFocusColor()

        if action in CLOSE_DIALOG:
            self._close_dialog()

    def _close_dialog( self ):
        self.close()
        xbmc.sleep( 500 )


class ScreenColor( xbmcgui.WindowXMLDialog ):
    def __init__( self, *args, **kwargs ):
        self.image = None
        self.colorPicked = None

        dpath = ( xbmc.translatePath( "special://screenshots" ) or xbmc.translatePath( "special://temp" ) )
        screenshots = set( glob( os.path.join( dpath, "screenshot*.*" ) ) )

        xbmc.executebuiltin( "TakeScreenshot" )
        xbmc.sleep( 800 )
        while xbmc.getCondVisibility( "Window.IsVisible(FileBrowser)" ):
            time.sleep( .25 )

        dpath = ( xbmc.translatePath( "special://screenshots" ) or xbmc.translatePath( "special://temp" ) )
        self.screenshot = set( glob( os.path.join( dpath, "screenshot*.*" ) ) ).difference( screenshots ).pop()
        #print self.screenshot

    def onInit( self ):
        try:
            if not xbmcvfs.exists( self.screenshot ):
                self._close_dialog()
            else:
                self.setProperty( "ScreenColor", self.screenshot )
                self.image = IMAGE( self.screenshot )

                self.offsetx, self.offsety = self.getControl( 1300 ).getPosition()
                self.image.resize( ( self.getControl( 1300 ).getWidth(), self.getControl( 1300 ).getHeight() ) )

                #used if not xbmcgui hasattr getMousePosition
                self.amount1 = ( self.getWidth() / 2.0 )
                self.amount2 = ( self.getHeight() / 2.0 )
                self.setFocusColor()
                # simule action for getAmount 1-2
                #xbmc.executebuiltin( "Action(MouseMove)" )
        except:
            print_exc()
            self._close_dialog()

    def getOffSet( self, x, y ):
        return ( ( x - self.offsetx ), ( y - self.offsety ) )

    def onFocus( self, controlID ):
        pass

    def onClick( self, controlID ):
        try:
            if controlID == 1301:
                x, y = xbmcgui.getMousePosition( self )
                self.colorPicked = self.image.getPixel( *self.getOffSet( x, y ) )
        except:
            self.colorPicked = None
            print_exc()
        self._close_dialog()

    def setFocusColor( self ):
        try:
            x, y = xbmcgui.getMousePosition( self )
            if self.image:
                color = self.image.getPixel( *self.getOffSet( x, y ) )
                currentfocuscolor = argb_to_hex( color )
                self.setProperty( "CurrentFocusColor", currentfocuscolor )
            self.setProperty( "MousePosX", str( x ) )
            self.setProperty( "MousePosY", str( y ) )
            self.setProperty( "MouseCoords", "Pipette: (%i,%i)" % ( x, y ) )
            self.getControl( 1303 ).setPosition( x, y )
        except:
            print_exc()

    def onAction( self, action ):
        if action == ACTION_MOUSE_MOVE:
            self.amount1 = action.getAmount1()
            self.amount2 = action.getAmount2()
            self.setFocusColor()

        if action in CLOSE_DIALOG:
            self.colorPicked = None
            self._close_dialog()

    def _close_dialog( self ):
        #ClearProperties  before delete, for prevent this -> ERROR: Texture manager unable to load file: .../screenshot[000].png
        self.clearProperties()
        xbmc.sleep( 100 )
        self.close()
        try: xbmcvfs.delete( self.screenshot )
        except: print_exc()
        xbmc.sleep( 500 )


class Transparency( xbmcgui.WindowXMLDialog ):
    def __init__( self, *args, **kwargs ):
        self.transColor = None

        #parse params
        params = kwargs[ "params" ]
        self.builtin = params[ "builtin" ]
        # execute built-in in real time
        self.executeBuiltIn = params.get( "setstringinrealtime" ) == "true" and self.builtin.lower().startswith( "skin." )
        
        # get percent from hex color
        p1, p2, p3, p4 = hex_to_argb_percent( params[ "default_color" ] or "ffffffff" )
        self.alpha_percent = float( p1.strip( "%" ) )
        self.red_percent   = float( p2.strip( "%" ) )
        self.green_percent = float( p3.strip( "%" ) )
        self.blue_percent  = float( p4.strip( "%" ) )

        # get max and min if is specified
        max = int( params.get( "max" ) or "100" )
        self.min = int( params.get( "min" ) or "0" )
        if max > 100: max = 100
        if self.min < 0: self.min = 0
        self.min = float( self.min )
        diff = float( max ) - self.min
        self.step = diff / 100.0

    def onInit( self ):
        self.getControl( 11 ).setPercent( self.alpha_percent )
        start_percent = self.min + ( self.alpha_percent * self.step )
        CurrentColorPercent = argb_percent_to_hex( ( start_percent, self.red_percent, self.green_percent, self.blue_percent ) )
        xbmc.executebuiltin( "SetProperty(CurrentColorPercent,%s)" % CurrentColorPercent )
        xbmc.executebuiltin( "SetProperty(CurrentPercent,%s%%)" % str( start_percent ) )

    def onFocus( self, controlID ):
        pass

    def onClick( self, controlID ):
        if controlID == 11:
            alpha_percent = self.min + ( self.getControl( controlID ).getPercent() * self.step )
            CurrentColorPercent = argb_percent_to_hex( ( alpha_percent, self.red_percent, self.green_percent, self.blue_percent ) )
            xbmc.executebuiltin( "SetProperty(CurrentColorPercent,%s)" % CurrentColorPercent )
            xbmc.executebuiltin( "SetProperty(CurrentPercent,%s%%)" % str( alpha_percent ) )
            self.transColor = CurrentColorPercent

            if self.executeBuiltIn:
                #print self.builtin % CurrentColorPercent
                xbmc.executebuiltin( self.builtin % CurrentColorPercent )

    def onAction( self, action ):
        if action in CLOSE_DIALOG:
            self._close_dialog()

    def _close_dialog( self ):
        self.close()
        xbmc.sleep( 500 )


def pickColorOnScreen():
    sc = ScreenColor( "script-ColorPicker-screen.xml", ADDON_DIR )
    sc.doModal()
    colorPicked = sc.colorPicked
    del sc
    return colorPicked


def transparency( params ):
    t = Transparency( "script-ColorPicker-transparency.xml", ADDON_DIR, params=params )
    t.doModal()
    transColor = t.transColor
    del t
    return transColor


def parse_argv():
    #parse params
    default_color = ""
    builtin = "".join( argv[ 1:2 ] )
    options = "".join( argv[ 2:3 ] ).replace( "&amp;", "&" )

    if builtin.lower().startswith( "skin." ) or builtin.lower().startswith( "addon(" ):
        try:
            builtin, default_color = ( builtin.strip( ")" ).split( ",", 1 ) + [ "" ] )[ :2 ]
            builtin += ( ",%s)", ",'%s')" )[ builtin.lower().startswith( "addon(" ) ]
            builtin = builtin.replace( "addon(", "Addon(" ).replace( "setsetting(", "setSetting(" )
        except:
            print_exc()
        # print "$VAR[rating]: %r" % xbmc.getInfoLabel( "$VAR[rating]" ) # yes work on XBMC (12.0-ALPHA1 Git:20120420-f57f8ec)
        if default_color.lower().startswith( "$var[" ):
            #default_color = "ffffffff" #reset color xbmc.getSkinVariable is not ready in xbmc require this patch : http://trac.xbmc.org/ticket/12031
            default_color = xbmc.getInfoLabel( default_color.replace( "$var[", "$VAR[" ) )
        elif default_color.lower().startswith( "$" ):
            default_color = xbmc.getInfoLabel( default_color.strip( "]" ).split( "[" )[ -1 ] )
    else:
        builtin = ""
        options = "&".join( argv[ 1: ] )

    # get max and min if is specified
    options = options.lower().replace( "transparency", "transparency=true" )
    params = dict( [ arg.split( "=" ) for arg in options.split( "&" ) if arg ] )
    params.update( { "builtin": builtin, "default_color": default_color } )

    print "[ColorPicker] Params: %r" % params
    return params
PARAMS = parse_argv()


def Main():
    colorPicked = None

    if PARAMS.get( "transparency" ) == "true":
        colorPicked = transparency( PARAMS )

    else:
        if PARAMS.get( "start" ) == "pickcoloronscreen":
            colorPicked = pickColorOnScreen()

        else:
            try:
                if PARAMS[ "default_color" ]:
                    try: colorPicked = name_to_argb( PARAMS[ "default_color" ] )
                    except: # ValueError for check name last chance check hex
                        try: colorPicked = hex_to_argb( PARAMS[ "default_color" ] )
                        except:
                            colorPicked = None
            except:
                print_exc()

        w = ColorPicker( "script-ColorPicker-main.xml", ADDON_DIR, colorPicked=colorPicked, params=PARAMS )
        w.doModal()
        colorPicked = w.color_picked
        del w

    if PARAMS[ "builtin" ]:
        #set builtin with color
        default_color = colorPicked or PARAMS[ "default_color" ] or "ffffffff"
        builtin = PARAMS[ "builtin" ] % default_color

        #executebuiltin
        if builtin.count( "," ) > 0:
            if builtin.lower().startswith( "skin." ):
                xbmc.executebuiltin( builtin )
            elif builtin.lower().startswith( "addon(" ):
                exec builtin
            return

        print "hmmm! what is builtin(%r)" % builtin



if ( __name__ == "__main__" ):
    Main()
