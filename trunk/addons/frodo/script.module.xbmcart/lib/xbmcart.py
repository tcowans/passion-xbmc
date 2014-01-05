
__all__ = [ "copyArtToCache", "getArt", "setArt", "DATABASE" ]

from os.path import splitext

import xbmc
import xbmcvfs
from xbmcaddon import Addon

from artwork import Database

DATABASE    = Database()

ARTS_TYPE   = "fanart|thumb".split( "|" )
MEDIAS_TYPE = "actor|director|episode|movie|musicvideo|set|tvshow".split( "|" )


def check_compatibility( minversion="11.9.3" ):
    VERSION = Addon( "xbmc.addon" ).getAddonInfo( "version" )
    return VERSION >= minversion, VERSION

COMPATIBLE, VERSION = check_compatibility()


def copyArtToCache( url ):
    if COMPATIBLE:
        c_thumb = xbmc.getCacheThumbName( url )[ :-4 ] + splitext( url )[ 1 ]
        c_dir   = "special://thumbnails/%s" % c_thumb[ 0 ]
        c_thumb = "%s/%s" % ( c_dir, c_thumb )

        ok = True
        if not xbmcvfs.exists( c_thumb ):
            ok = xbmcvfs.mkdirs( c_dir )
            ok = xbmcvfs.copy( url, c_thumb )

        return ok and c_thumb


def getArt( mediaId, mediaType ):
    """ getArt(mediaId, mediaType) return dictionary  { fanart: value, thumb: value }

        mediaId    :  integer - media_id for media_type
        mediaType  :  string  - type of media (actor/director/episode/movie/musicvideo/set/tvshow)

        Throws: TypeError, if type of media is invalid.

        example:
         - art = xbmcart.getArt( 5, "movie" )
    """
    if mediaType.lower() not in MEDIAS_TYPE:
        raise TypeError( 'xbmcart invalid mediaType: %r' % mediaType.lower() )

    return DATABASE.getArt( mediaId, mediaType.lower() )


def setArt( mediaId, mediaType, artType, url ):
    """ setArt( mediaId, mediaType, artType, url ) set art, returns true/false.
        
        mediaId    :  integer - media_id for media_type
        mediaType  :  string  - type of media (actor/director/episode/movie/musicvideo/set/tvshow)
        artType    :  string  - type of art (fanart/thumb)
        url        :  string  - url of art

        Throws: TypeError, if media_id or type of art/media is invalid.

        example:
         - ok = xbmcart.setArt( 5, "actor", "fanart", "smb://XBMC/movies/The Avengers/Chris Evans-fanart.jpg" )
    """
    if artType.lower() not in ARTS_TYPE:
        raise TypeError( 'xbmcart invalid artType: %r' % artType.lower() )
    if mediaType.lower() not in MEDIAS_TYPE:
        raise TypeError( 'xbmcart invalid mediaType: %r' % mediaType.lower() )
    if DATABASE.notValidMediaID( mediaId, mediaType.lower() ):
        raise TypeError( 'xbmcart invalid mediaId %r for %r' % ( mediaId, mediaType.lower() ) )

    return DATABASE.setArt( mediaId, mediaType.lower(), artType.lower(), url )
