
# Modules general
import os
import sys

# Modules XBMC
import xbmc

# Modules Custom
from log import logAPI
log = logAPI()


try:
    from PIL import Image
except:
    log.error.exc_info( sys.exc_info() )
    # Require PIL for FLIP
    def flip_fanart( fanart ):
        return fanart
else:
    def flip_fanart( fanart ):
        #NB: the EXIF infos is not preserved :(
        try:
            im = Image.open( fanart )
            im = im.transpose( Image.FLIP_LEFT_RIGHT )
            format = ( im.format or "JPEG" )
            #PIL ignore param exif= in save
            try: im.save( fanart, format, quality=90, dpi=im.info.get( "dpi", ( 0, 0 ) ), exif=im.info.get( "exif", "" ) )
            except: im.save( fanart, "PNG" )
        except:
            log.error.exc_info( sys.exc_info() )
        return fanart


def IsTrue( text ):
    return ( text == "true" )

