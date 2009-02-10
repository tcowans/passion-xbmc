
import os
import sys
import traceback
from StringIO import StringIO
from urllib import urlopen, urlretrieve
from PIL import Image, ImageEnhance

import xbmc


#set temp file path
TEMP_DIR = xbmc.translatePath( "special://temp/" )
if not os.path.isdir( TEMP_DIR ): TEMP_DIR = xbmc.translatePath( "Z:\\" )
TEMP_FILE = os.path.join( TEMP_DIR, "temp.jpg" )


def _samefile( src, dst ):
    # Macintosh, Unix.
    if hasattr( os.path, 'samefile' ):
        try:
            return os.path.samefile(src, dst)
        except OSError:
            return False

    # All other platforms: check for same pathname.
    return ( os.path.normcase( os.path.abspath( src ) ) == os.path.normcase( os.path.abspath( dst ) ) )


def set_resizing_is_necessary( default_size, new_size=None ):
    """ set_resizing_is_necessary( sequence1, sequence2 ) -> list or tuple with 2 integer

    based on xbmc methode: http://xbmc.org/wiki/?title=Advancedsettings.xml#.3Cthumbsize.3E
    Size of the square in pixels that XBMC will use to cache thumbnail images.
    If the thumb is smaller than this size it will be cached as-is.
    If it is larger it will be scaled so that the number of pixels is less than a square of this value.
    Default is 512 (192 on xbox), which refers to 512x512 = 262144 (for XBox 192x192 = 36864) pixels in total.
    The thumbnail will be cached at using the same aspect ratio as the original image, using up to 262144 (for XBox 36864) pixels. 
    """

    xbmc_size = ( ( 512, 512 ), ( 192, 192 ), )[ ( os.environ.get( "OS", "xbox" ).lower() == "xbox" ) ]
    xbmc_pixels = reduce( lambda x, y: x*y, xbmc_size )

    default_pixels = reduce( lambda x, y: x*y, default_size )
    if new_size is None:
        new_size = xbmc_size
    new_pixels = reduce( lambda x, y: x*y, new_size )

    if new_pixels > xbmc_pixels < default_pixels:
        return xbmc_size

    if default_pixels > new_pixels:
        return new_size

    return default_size


def imageOpener( source, mode="rb" ):
    if source.startswith( "http://" ):
        fp = None
        try:
            f = urlopen( source, mode )
            fp = Image.open( StringIO( f.read() ) )
            f.close()
        except:
            urlretrieve( source, TEMP_FILE )
            f = open( TEMP_FILE, mode )
            try: fp = Image.open( StringIO( f.read() ) )
            except: fp = None
            f.close()
        if fp: return fp
    return Image.open( source )


def makeThumbnails( source, destination=None, watched=False, w_h=None, prefix="tbn" ):
    try:
        # SETUP THUMB NAMES
        if destination and os.path.isdir( destination ):
            local = os.path.join( destination, os.path.basename( source ) )
        elif destination:# and os.path.isfile( destination ):
            local = destination
        elif destination is None and os.path.isfile( source ):
            local = os.path.join( os.path.dirname( source ), os.path.basename( source ) )
        else:
            local = TEMP_FILE
        thumbnail = "%s.%s" % ( os.path.splitext( local )[ 0 ], prefix )
        watched_thumbnail = "%s-w.%s" % ( os.path.splitext( local )[ 0 ], prefix )

        # OPEN IMAGE LOCAL OR ONLINE
        im = imageOpener( source )
        if im is not None:
            # SETUP THUMB SIZE
            if w_h is None:
                size = set_resizing_is_necessary( im.size, w_h )
            else:
                size = w_h
            #if w_h is None: size = im.size # GET DEFAULT IMAGE SIZE
            #else: size = w_h #( 128, 128, )
            # CREATE THUMBNAIL
            if not _samefile( source, thumbnail ):
                im.thumbnail( size, Image.ANTIALIAS )
                im = im.convert( "RGBA" )
                im.save( thumbnail, "PNG" )
            if watched:
                # CREATE WATCHED THUMBNAIL
                if not _samefile( source, watched_thumbnail ):
                    alpha = im.split()[ 3 ]
                    alpha = ImageEnhance.Brightness( alpha ).enhance( 0.2 )
                    im.putalpha( alpha )
                    im.save( watched_thumbnail, "PNG" )
            return thumbnail
        #else:
        #    try: 
        #        urlretrieve(source, thumbnail)
        #        if os.path.isfile(thumbnail): return thumbnail
        #    except: traceback.print_exc()
    except:
        traceback.print_exc()
    return ""


if __name__ == "__main__":
    #source = "http://dahlieka.files.wordpress.com/2008/01/zack-solitude-4.jpg" # 2432px * 1737px
    source = r"C:\Program Files\XBMC\userdata\script_data\Installer Passion-XBMC\Thumbnails\1\136835ec.tbn"
    destination = os.path.join( os.getcwd().rstrip(";"), os.path.basename( source ) )
    #print makeThumbnails( source, destination, w_h=( 256, 256, ), prefix="png" )
    print makeThumbnails( source, destination, watched=True, prefix="png" )

