
import os

from PIL import Image

from xbmccolors import *


def makeDirs( dpath ):
    if not os.path.exists( dpath ):
        os.makedirs( dpath )


def createGradient( argb, gradient, dpath="pixels" ):
    png = '%02x%02x%02x%02x-gradient.png' % argb
    fpath = os.path.join( dpath, png )
    if not os.path.exists( fpath ):
        mask = Image.open( gradient )
        mode = ( "RGB", "RGBA" )[ 0 ]#argb[ 0 ] < 255 ]
        rgba = ( argb[ 1 ], argb[ 2 ], argb[ 3 ] )#, argb[ 0 ] )
        grd  = Image.composite( mask, Image.new( mode, mask.size, rgba ), mask )
        makeDirs( os.path.dirname( fpath ) )
        grd.save( fpath, "PNG" )
    return fpath


def createPixel( argb, dpath="pixels", size=( 4, 4 ) ):
    png = '%02x%02x%02x%02x.png' % argb
    fpath = os.path.join( dpath, png )
    if not os.path.exists( fpath ):
        rgba = ( argb[ 1 ], argb[ 2 ], argb[ 3 ], argb[ 0 ] )
        pix  = Image.new( "RGBA", size, rgba )
        makeDirs( os.path.dirname( fpath ) )
        pix.save( fpath, "PNG" )
    return fpath


class IMAGE:
    def __init__( self, filename ):
        self.image = Image.open( filename )
        self.loadColors()

    def loadColors( self ):
        self.colors = self.image.load()

    def resize( self, size, filter=Image.ANTIALIAS ):
        # don't resize for rarely match
        if self.image.size != size:
            self.image = self.image.resize( size, Image.ANTIALIAS )
            self.loadColors()

    def getPixel( self, x, y ):
        color = list( self.colors[ x, y ] ) + [ 255 ]
        red, green, blue, alpha = color[ 0 ], color[ 1 ], color[ 2 ], color[ 3 ]
        return alpha, red, green, blue

    def getColors( self ):
        """ Returns an unsorted list of (count, color) tuples, where the count is the number of times the
            corresponding color occurs in the image.
            If the maxcolors value is exceeded, the method stops counting and returns None. The default maxcolors 
            value is 256. To make sure you get all colors in an image, you can pass in size[0]*size[1] (but make
            sure you have lots of memory before you do that on huge images). 
        """
        maxcolors = eval( "%i*%i" % self.image.size )
        return self.image.getcolors( maxcolors )



#def get_pixel_colour( i_x, i_y ):
#    # UNIX
#    from PIL import ImageStat
#    from Xlib import display, X
#    o_x_root = display.Display().screen().root
#    o_x_image = o_x_root.get_image( i_x, i_y, 1, 1, X.ZPixmap, 0xffffffff )
#    o_pil_image_rgb = Image.fromstring( "RGB", (1, 1), o_x_image.data, "raw", "BGRX" )
#    lf_colour = ImageStat.Stat( o_pil_image_rgb ).mean
#    return tuple( map( int, lf_colour ) )

#def get_pixel_colour( i_x, i_y ):
#    # WINDOWS ONLY
#    from PIL import ImageGrab
#    return ImageGrab.grab().load()[ i_x, i_y ]
#print get_pixel_colour( 640, 360 )

if ( __name__ == "__main__" ):
    #color = ( 255, 128, 255, 128 )
    #gradient = '../skins/default/media/gradient.png'

    #img = createGradient( color, gradient )
    #print createPixel( color )

    #import time
    #t1 = time.time()
    im = IMAGE( "../palettes/eye.jpg" )
    colors = im.getColors()
    print len( colors )
    #for count, color in colors:
    #    color = ( 255, ).__add__( color )
    #    createPixel( color )
    #    print count
    #print
    #print time.time() - t1
    #file( "colors.txt", "w" ).write( repr( colors ) )
