"""
    Database module
"""

#Modules general
import os
import sys
from re import DOTALL, findall, sub
from urllib import urlopen, quote_plus

if sys.version >= "2.5":
    from hashlib import md5 as _hash
else:
    from md5 import new as _hash

# Modules XBMC
import xbmc
import xbmcgui
import xbmcvfs
from xbmcaddon import Addon
from xbmc import translatePath#, executehttpapi

# Modules Custom
import jsonrpc
from utils.log import logAPI
from utils.streamdetails import *
from utils.file_item import Thumbnails


# constants
ADDON = Addon( "script.moviesets" )
MOVIESET_CACHED_THUMB = translatePath( "%sThumbnails/%s.tbn" % ( ADDON.getAddonInfo( "profile" ), "%s" ) )
try: os.makedirs( os.path.dirname( MOVIESET_CACHED_THUMB ) )
except: xbmcvfs.mkdir( os.path.dirname( MOVIESET_CACHED_THUMB ) )

LOGGER = logAPI()
TBN = Thumbnails()


#xbmcdb = executehttpapi
#executehttpapi cause Crash/SystemExit if backend of movieset/tvtunes is running !!!
# use urllib with xbmc.getIPAddress()
from utils.webserver import xbmcHttp
def xbmcdb( command, *params ):
    source = ""
    url = xbmcHttp
    try:
        params = ";".join( list( params ) )
        url   += "?command=%s&parameter=%s" % ( command, params )
        source = urlopen( url ).read()
    except:
        pass
    LOGGER.info.LOG( "xbmcdb::url: %s", url )
    LOGGER.info.LOG( "xbmcdb::response: %r", source )
    return source


# for more see [$SOURCE/xbmc/interfaces/json-rpc/ServiceDescription.h]
VIDEO_FIELDS_MOVIESET = [ "title", "playcount", "fanart", "thumbnail" ]

LIST_FIELDS_ALL = [ "title", "artist", "albumartist", "genre", "year", "rating",
    "album", "track", "duration", "comment", "lyrics", "musicbrainztrackid",
    "musicbrainzartistid", "musicbrainzalbumid", "musicbrainzalbumartistid",
    "playcount", "fanart", "director", "trailer", "tagline", "plot",
    "plotoutline", "originaltitle", "lastplayed", "writer", "studio",
    "mpaa", "cast", "country", "imdbnumber", "premiered", "productioncode",
    "runtime", "set", "showlink", "streamdetails", "top250", "votes",
    "firstaired", "season", "episode", "showtitle", "thumbnail", "file", "resume" ]

VIDEO_FIELDS_MOVIE = [ "title", "genre", "year", "rating", "director", "trailer",
    "tagline", "plot", "plotoutline", "originaltitle", "lastplayed",
    "playcount", "writer", "studio", "mpaa", "cast", "country",
    "imdbnumber", "premiered", "productioncode", "runtime", "set",
    "showlink", "top250", "votes", "streamdetails",
    "fanart", "thumbnail", "file", "resume" ] # "sorttitle" not supported :( !!! and "lastplayed" not returned

SORTTITLE = { "method": "sorttitle", "order": "ascending" } #"descending"


def _encode( text, encoding="utf-8" ):
    try: text = text.encode( encoding )
    except: pass
    return text


def path_exists( filename ):
    # first use os.path.exists and if not exists, test for share with xbmcvfs.
    return os.path.exists( filename ) or xbmcvfs.exists( filename )


def getStarRating( rating ):
    try:
        f = ( float( rating ) * 0.5 ) # + 0.5
        if f >= ( int( f ) + 0.5 ):
            return "rating%d.png" % int( f + 0.5 )
        return "rating%d.png" % int( f )
    except:
        LOGGER.error.print_exc()
    return "rating0.png"


def get_cached_thumb( fpath ):
    try:
        # fixe me: xbmc not change/reload/refresh image if path is same
        rpath = translatePath( fpath )
        filename = _hash( repr( rpath ) + open( rpath ).read( 250 ) ).hexdigest()
        temp = MOVIESET_CACHED_THUMB % filename
        if not path_exists( temp ):
            #executehttpapi( "FileCopy(%s,%s)" % ( fpath, temp ) )#.replace( "<li>", "" )
            xbmcvfs.copy( fpath, temp )
        return ( fpath, temp )[ path_exists( temp ) ]
    except:
        return fpath


def getContainerMovieSets( infoSet=None ):
    jsonapi = jsonrpc.jsonrpcAPI()
    # GET MOVIESETS
    json = jsonapi.VideoLibrary.GetMovieSets( properties=VIDEO_FIELDS_MOVIESET )

    movie_sets = json.get( 'sets', [] )
    total = json.get( "limits", {} ).get( "total" ) or len( movie_sets )
    #print total

    # dico for synchronize main container on VideoLibrary with virtual container of MovieSets
    moviesets = {}
    if infoSet is not None:
        # get only one user want info
        listitems = []
    else:
        # set dymmy listitem, label: container title , label2: total movie sets
        listitems = [ xbmcgui.ListItem( "Container MovieSets", str( total ) ) ]

    # reload addon settings 
    try: ADDON = Addon( "script.moviesets" )
    except: pass
    # get user separator
    try: separator = " %s " % ADDON.getSetting( "separator" )
    except: separator = " / "
    # get user prefer order
    try: SORTTITLE[ "order" ] = ( "ascending", "descending" )[ int( ADDON.getSetting( "order" ) ) ]
    except: pass

    # enum movie sets
    for countset, movieset in enumerate( movie_sets ):
        #print movieset.keys()#[u'title', u'fanart', u'label', u'playcount', u'thumbnail', u'setid']
        try:
            idSet = movieset[ "setid" ]
            #print ( idSet, infoSet, str( idSet ) != infoSet )
            if infoSet is not None and str( idSet ) != infoSet:
                continue # get only one user want info
            # get saga icon
            icon = movieset[ "thumbnail" ]
            icon = ( "", icon )[ path_exists( translatePath( icon ) ) ]
            # get saga fanart
            #d, f = os.path.split( movieset[ 'thumbnail' ] )
            #c_fanart = "%sFanart/%s" % ( d[ :-1 ], f )
            c_fanart = movieset[ "fanart" ]
            Fanart_Image = ( "", c_fanart )[ path_exists( translatePath( c_fanart ) ) ]
            # fixe me: xbmc not change/reload/refresh image if path is same
            if Fanart_Image: Fanart_Image = get_cached_thumb( Fanart_Image )
            if icon: icon = get_cached_thumb( icon )

            # set movieset listitem
            listitem = xbmcgui.ListItem( movieset[ 'label' ], str( idSet ), icon, icon )
            #listitem.setPath( "ActivateWindow(10025,videodb://1/7/%i/)" % idSet )

            # get movies list of movieset
            # not good, return only Video.Fields.MovieSet. [use Files.GetDirectory for more fields]
            #json = jsonapi.VideoLibrary.GetMovieSetDetails( setid=idSet, properties=VIDEO_FIELDS_MOVIESET )
            json = jsonapi.Files.GetDirectory( directory="videodb://1/7/%i/" % idSet, properties=VIDEO_FIELDS_MOVIE, sort=SORTTITLE, media="video" )
            movies = json.get( 'files', [] )
            total_movies = json.get( "limits", {} ).get( "total" ) or len( movies )
            # set base variables
            watched, unwatched = 0, total_movies
            rating, votes = 0.0, 0
            plotset = ""
            mpaa    = set()
            studios = set()
            genres  = set()
            years   = set()
            #fanartsets = set()
            countries  = set()
            stackpath  = []
            stacktrailer = []
            duration = 0.1
            iWidth   = 0
            iHeight  = 0
            aspect   = 0.0

            # enum movies
            for count, movie in enumerate( movies ):
                if not bool( movie ): continue
                #print movie.keys()#[u'rating', u'set', u'filetype', u'file', u'year', u'id', u'streamDetails', u'plot', u'votes', u'title', u'fanart', u'mpaa', u'writer', u'label', u'type', u'thumbnail', u'plotoutline', u'resume', u'director', u'imdbnumber', u'studio', u'showlink', u'genre', u'productioncode', u'country', u'premiered', u'originaltitle', u'cast', u'tagline', u'playcount', u'runtime', u'top250', u'trailer']
                # for more infos
                #print jsonapi.VideoLibrary.GetMovieDetails( movieid=int(movie["id"]), properties=VIDEO_FIELDS_MOVIE )
                #print movie[ "votes" ]
                #continue
                try:
                    #optional
                    try:
                        sdv = movie[ "streamdetails"].get( "video", [ {} ] )
                        duration += sum( d.get( "duration", 0 ) for d in sdv )
                        iWidth   += sum( w.get( "width",    0 ) for w in sdv )
                        iHeight  += sum( h.get( "height",   0 ) for h in sdv )
                        aspect   += sum( a.get( "aspect",   0 ) for a in sdv )
                    except:
                        pass
                    # update mpaa
                    if movie.get( "mpaa" ):
                        mpaa.add( movie[ "mpaa" ] )
                    # set watched count
                    #print movie.get( "playcount" )
                    if bool( movie[ "playcount" ] ): watched += 1
                    # update genres and years
                    if movie[ "year" ] > 0:
                        years.add( str( movie[ "year" ] ) )
                    genres.update( movie[ "genre" ].split( " / " ) )
                    # add country
                    if movie.get( "country" ):
                        countries.update( movie[ "country" ].split( " / " ) )
                    # add studio
                    if movie.get( "studio" ):
                        studios.update( movie[ "studio" ].split( " / " ) )
                    # add plot movie to plotset
                    plotset += "[B]%(title)s (%(year)s)[/B][CR]%(plot)s[CR][CR]" % movie
                    # set stack, add movie path and trailer
                    if movie.get( "trailer" ): stacktrailer.append( movie[ "trailer" ] )
                    stackpath.append( movie[ "file" ] )
                    # use first path if stacked. for prevent this [WARNING: XFILE::CFileFactory::CreateLoader - Unsupported protocol(stack) in path_exists( moviepath + "extrafanart" )] 
                    if "stack://" in movie[ "file" ]: movie[ "file" ] = movie[ "file" ][ 8 : ].split( " , " )[ 0 ]
                    # set RatingAndVotes info
                    rating += movie.get( "rating", 0.0 )
                    try: votes += int( movie.get( "votes", "0" ).replace( ",", "" ) )
                    except: pass

                    # set movies properties 'plot', 'votes', 'rating', 'fanart', 'title', 'label',
                    # 'file', 'year', 'genre','playcount', 'runtime', 'thumbnail', 'trailer'
                    b_property = "movie.%i." % ( count + 1 )
                    moviepath = os.path.dirname( movie[ "file" ] ) + ( "/", "\\" )[ not movie[ "file" ].count( "/" ) ]
                    listitem.setProperty( b_property + "Title",     movie[ "title" ] )
                    listitem.setProperty( b_property + "sortTitle", movie.get( "sorttitle", "" ) )
                    listitem.setProperty( b_property + "Filename",  os.path.basename( movie[ "file" ] ) )
                    listitem.setProperty( b_property + "Path",      moviepath )
                    listitem.setProperty( b_property + "Plot",      movie[ "plot" ] )
                    listitem.setProperty( b_property + "Year",      str( movie[ "year" ] or "" ) )
                    listitem.setProperty( b_property + "Trailer",   movie.get( "trailer", "" ) )
                    # set icon property
                    icon = movie[ 'thumbnail' ]
                    icon = ( "", icon )[ path_exists( translatePath( icon ) ) ]
                    #print repr( icon )
                    if not icon: # check for auto-
                        _path, _file = os.path.split( icon )
                        a_icon = os.path.join( _path, "auto-" + _file )
                        icon = ( "", a_icon )[ path_exists( translatePath( a_icon ) ) ]
                    listitem.setProperty( b_property + "Icon", icon )
                    # set fanart property
                    fanart = movie[ 'fanart' ]
                    fanart = ( "", fanart )[ path_exists( translatePath( fanart ) ) ]
                    listitem.setProperty( b_property + "Fanart", fanart )
                    if fanart and not Fanart_Image: Fanart_Image = fanart
                    # set extrafanart: if not exists set empty
                    extrafanart = moviepath + "extrafanart"
                    extrafanart = ( "", extrafanart )[ path_exists( extrafanart ) ]
                    listitem.setProperty( b_property + "ExtraFanart", extrafanart )
                    # set extrafanart for movieset if exists set first found
                    #fanartsets.add( os.path.dirname( os.path.dirname( moviepath ) ) )
                    if listitem.getProperty( "ExtraFanart" ): continue
                    fanartset = os.path.dirname( os.path.dirname( moviepath ) )
                    fanartset += ( "/", "\\" )[ not fanartset.count( "/" ) ] + "extrafanart"
                    if path_exists( fanartset ): listitem.setProperty( "ExtraFanart", fanartset )
                    elif extrafanart: listitem.setProperty( "ExtraFanart", extrafanart )

                    #print _encode(movie[ "file" ]), _encode(moviepath), _encode(fanartset)
                    #print "-"*100
                except:
                    LOGGER.error.print_exc()

            # set movieset properties
            listitem.setProperty( "IsSet",              "true" )
            listitem.setProperty( "idSet",              str( idSet ) )
            listitem.setProperty( "WatchedMovies",      str( watched ) )
            listitem.setProperty( "UnWatchedMovies",    str( unwatched - watched ) )
            listitem.setProperty( "TotalMovies",        str( total_movies ) )
            listitem.setProperty( "Fanart_Image",       Fanart_Image )
            listitem.setProperty( "Years",              separator.join( sorted( years, reverse=( SORTTITLE[ "order" ] == "descending" ) ) ) )
            try: listitem.setProperty( "StarRating",    getStarRating( rating / float( total_movies ) ) )
            except: listitem.setProperty( "StarRating", "rating0.png" )
            listitem.setProperty( "Countries",          separator.join( countries ) )
            listitem.setProperty( "VideoResolution",    VideoDimsToResolutionDescription( int( iWidth / total_movies ), int( iHeight / total_movies ) ) )
            listitem.setProperty( "VideoAspect",        VideoAspectToAspectDescription( float( aspect / total_movies ) ) )

            # set stack path
            stackpath = " ; ".join( stackpath )
            if " ; " in stackpath: stackpath = "stackset://" + stackpath
            listitem.setPath( quote_plus( _encode( stackpath ) ) )
            # set stack trailer
            stacktrailer = " , ".join( stacktrailer )
            if " , " in stacktrailer: stacktrailer = "stack://" + stacktrailer

            # set listitem infoslabels
            listitem.setInfo( "video", {
                "plot":     plotset,
                "votes":    str( votes ),
                "title":    movieset[ 'label' ],
                "studio":   separator.join( studios ),
                #"duration": str( round( duration / 60.0, 2 ) ),
                "duration": str( int( duration / 60.0 ) ),
                "rating":   ( rating / float( total_movies ) ),
                "genre":    separator.join( sorted( [ g.strip() for g in genres ] ) ),
                "mpaa":     separator.join( [ m.strip() for m in mpaa ] ),
                "trailer":  stacktrailer,
                } )

            moviesets[ _encode( movieset[ 'label' ] ) ] = countset + 1
            listitems.append( listitem )

            if infoSet is not None and idSet == infoSet:
                moviesets[ movieset[ 'label' ] ] = 0
                break # get only one user want info
        except:
            LOGGER.error.print_exc()

    return listitems, moviesets



class Records:
    """ fetch records """

    def __init__( self ):
        self._set_records_format()

    def _set_records_format( self ):
        # format our records start and end
        #xbmcdb( "SetResponseFormat()" )
        #xbmcdb( "SetResponseFormat(OpenRecord,<records>)" )
        #xbmcdb( "SetResponseFormat(CloseRecord,</records>)" )
        xbmcdb( "SetResponseFormat" )
        xbmcdb( "SetResponseFormat", "OpenRecord", "<records>", "CloseRecord", "</records>" )

    def commit( self, sql ):
        done = False
        try:
            #done = ( "done" in xbmcdb( "ExecVideoDatabase(%s)" % quote_plus( sql ), ).lower() )
            done = ( "done" in xbmcdb( "ExecVideoDatabase", quote_plus( sql ) ).lower() )
        except: LOGGER.error.print_exc()
        return done

    def fetch( self, sql, keys=None, index=None ):
        records = []
        try:
            #records_xml = xbmcdb( "QueryVideoDatabase(%s)" % quote_plus( sql ), )
            records_xml = xbmcdb( "QueryVideoDatabase", quote_plus( sql ) )
            records = findall( "<records>(.+?)</records>", records_xml, DOTALL )
        except:
            LOGGER.error.print_exc()
        return self.parseFields( records, keys, index )

    def parseFields( self, records, keys=None, index=None ):
        fields = []
        try:
            for record in records:
                record = findall( "<field>(.*?)</field>", record, DOTALL )
                if keys: record = dict( zip( keys, record ) )
                fields.append( record )
        except:
            LOGGER.error.print_exc()
        if fields and index is not None:
            try: fields = fields[ index ]
            except: LOGGER.error.print_exc()
        return fields



class Database( Records ):
    """ Main database class """

    def __init__( self, *args, **kwargs ):
        Records.__init__( self )
        self.idVersion = int( self.fetch( "SELECT idVersion FROM version", index=0 )[ 0 ] )
        self._clean_cached_thumbs()

    def _clean_cached_thumbs( self, limit=25 ):
        if self.idVersion >= 63: return
        # clean all images, if set not exists. For prevent bad match with new set.
        try:
            id_moviesets = self.fetch( "SELECT idSet FROM sets" )
            for idSet in xrange( 1, limit+1 ):
                if [ str( idSet ) ] not in id_moviesets:
                    icon = TBN.get_cached_saga_thumb( str( idSet ) )
                    if path_exists( icon ):
                        LOGGER.warning.LOG( "Deleting icon for movieset %i, because this movieset not exists...", idSet )
                        xbmcvfs.delete( icon )

                    fanart = TBN.get_cached_saga_thumb( str( idSet ), True )
                    if path_exists( fanart ):
                        LOGGER.warning.LOG( "Deleting fanart for movieset %i, because this movieset not exists...", idSet )
                        xbmcvfs.delete( fanart )
        except:
            LOGGER.error.print_exc()

    def getArtForItem( self, mediaId, mediaType="set" ):
        if self.idVersion >= 63:
            try:
                sql = "SELECT type,url FROM art WHERE media_id=%i AND media_type='%s'" % ( int( mediaId ), mediaType )
                return dict( [ ( t, ( "image://" + quote_plus( u ) ) ) for t, u in self.fetch( sql ) ] )
            except:
                LOGGER.error.print_exc()

    def setArtForItem( self, mediaId, mediaType, artType, url ):
        OK = False
        if self.idVersion >= 63:
            try:
                # check if exists
                sql = "SELECT art_id FROM art WHERE media_id=%i AND media_type='%s' AND type='%s'" % ( int( mediaId ), mediaType, artType )
                artId = "".join( self.fetch( sql, index=0 ) )
                if artId: # update
                    sql = "UPDATE art SET url='%s' WHERE art_id=%i" % ( url, int( artId ) )
                else: # insert
                    sql = "INSERT INTO art(media_id, media_type, type, url) VALUES (%i, '%s', '%s', '%s')" % ( int( mediaId ), mediaType, artType, url )
                OK = self.commit( sql )
            except:
                LOGGER.error.print_exc()
        return OK

    def addSet( self, strSet ):
        try:
            # check if exists
            sql = "SELECT idSet FROM sets WHERE strSet LIKE '%s'" % strSet
            id = "".join( self.fetch( sql, index=0 ) )
            if not id:
                # insert not exists
                OK = self.commit( "INSERT INTO sets (idSet, strSet) values(NULL, '%s')" % strSet )
                #if OK:
                id = "".join( self.fetch( sql, index=0 ) )
            return int( id )
        except:
            LOGGER.error.print_exc()
        return -1

    def addSetToMovie( self, idMovie, idSet ):
        OK = False
        try:
            # check if match or if exists in other set
            #sql = "select * from setlinkmovie where idSet=%i and idMovie=%i" % ( idSet, idMovie, )
            sql = "SELECT * FROM setlinkmovie WHERE (idSet=%i AND idMovie=%i) OR idMovie=%i" % ( int( idSet ), int( idMovie ), int( idMovie ), )
            exists = self.fetch( sql, index=0 )
            if not exists:
                # insert not exists
                OK = self.commit( "INSERT INTO setlinkmovie (idSet,idMovie) values(%i,%i)" % ( int( idSet ), int( idMovie ), ) )
        except:
            LOGGER.error.print_exc()
        return OK

    def deleteMovieOfSet( self, idMovie, idSet ):
        OK = False
        try:
            if idMovie == -1: sql = "DELETE FROM setlinkmovie WHERE idSet=%i" % ( int( idSet ), )
            else: sql = "DELETE FROM setlinkmovie WHERE idSet=%i AND idMovie=%i" % ( int( idSet ), int( idMovie ), )
            OK = self.commit( sql )
        except:
            LOGGER.error.print_exc()
        return OK

    def deleteSet( self, idSet ):
        OK = False
        try:
            OK = self.commit( "DELETE FROM sets WHERE idSet=%i" % int( idSet ) )
            if OK:
                icon = TBN.get_cached_saga_thumb( idSet )
                if path_exists( icon ): os.remove( icon )
                fanart = TBN.get_cached_saga_thumb( idSet, True )
                if path_exists( fanart ): os.remove( fanart )
                OK = self.deleteMovieOfSet( -1, idSet )
        except:
            LOGGER.error.print_exc()
        return OK

    def editMovieSortTitle( self, sortTitle, idMovie ):
        OK = False
        try: OK = self.commit( "UPDATE movie SET c10=\"%s\" WHERE idMovie=%i" % ( sortTitle, int( idMovie ) ) )
        except: LOGGER.error.print_exc()
        return OK

    def editMovieSetTitle( self, strSet, idSet ):
        OK = False
        try: OK = self.commit( "UPDATE sets SET strSet=\"%s\" WHERE idSet=%i" % ( strSet, int( idSet ) ) )
        except: LOGGER.error.print_exc()
        return OK

    def getFileId( self, strFilenameAndPath ):
        try:
            # SplitPath
            strPath, strFileName = os.path.split( strFilenameAndPath )
            if strPath: strPath += ( "/", "\\" )[ not strPath.count( "/" ) ]
            idPath = self.getPathId( strPath )
            if ( idPath >= 0 ):
                sql = "SELECT idFile FROM files WHERE strFileName LIKE '%s' AND idPath=%i" % ( strFileName, idPath )
                idFile = "".join( self.fetch( sql, index=0 ) )
                return int( idFile )
        except:
            LOGGER.error.print_exc()
        return -1

    def getPathId( self, strPath ):
        try:
            sql = "SELECT idPath FROM path WHERE strPath LIKE \"%s\"" % strPath
            idPath = "".join( self.fetch( sql, index=0 ) )
            if not idPath:
                if strPath.startswith( "ftp://" ) or strPath.startswith( "smb://" ):
                    for ipath, spath in self.fetch( "SELECT idPath, strPath FROM path" ):
                        if strPath == sub( "(.*?://)(.*?@)(.*?)", "\\1", spath ):
                            idPath = ipath
                            break
            if idPath:
                return int( idPath )
        except:
            LOGGER.error.print_exc()
        return -1

    def getMovie( self, strFilenameAndPath, strTitle ):
        try:
            idFile = self.getFileId( strFilenameAndPath )
            if ( idFile == -1 ):
                sql = "SELECT idMovie, c00, c10 FROM movie WHERE c00 LIKE \"%s\"" % strTitle
            else:
                sql = "SELECT idMovie, c00, c10 FROM movie WHERE idFile=%i" % int( idFile )
            movie = self.fetch( sql, index=0 )
            return int( movie[ 0 ] ), movie[ 1 ], movie[ 2 ]
        except:
            LOGGER.error.print_exc()
        return -1, "", ""

    def getSet( self, strSet ):
        try:
            movieset = self.fetch( 'SELECT * FROM sets WHERE strSet LIKE \"%s\"' % strSet, index=0 )
            if movieset:
                idSet, strSet = movieset
                return int( idSet ), strSet
        except:
            LOGGER.error.print_exc()
        return -1, ""

    def getSetByIdMovie( self, idMovie ):
        try:
            sql = """
                SELECT sets.* FROM sets
                JOIN setlinkmovie ON setlinkmovie.idSet=sets.idSet
                JOIN movie ON movie.idMovie=setlinkmovie.idMovie
                WHERE movie.idMovie=%i
                """
            movieset = self.fetch( sql % int( idMovie ), index=0 )
            if movieset:
                idSet, strSet = movieset
                return int( idSet ), strSet
        except:
            LOGGER.error.print_exc()
        return -1, ""

    def getSets( self, order=False, count=False, keys=None ):
        moviesets = []
        if keys:
            keys = [ "idSet", "strSet" ]
        try:
            if count:
                sql = "SELECT sets.*, count(sets.idSet) FROM sets JOIN setlinkmovie ON setlinkmovie.idSet=sets.idSet GROUP BY sets.idSet"
            else:
                sql = "SELECT * FROM sets"
            moviesets = self.fetch( sql + ( "", " ORDER BY strSet" )[ order ], keys )
        except:
            LOGGER.error.print_exc()
        return moviesets

    def getMovies( self, idSet=None, keys=None ):
        movies = []
        if keys:
            keys = [ "idMovie", "strTitle", "strSort", "strGenre", "strPlot", "strYear", "playCount", "strPath", "strFileName" ]
        try:
            if idSet is None:
                sql = "SELECT idMovie, c00, c10 FROM movie ORDER BY c00"
            else:
                sql = """
                    SELECT movieview.idMovie, c00, c10, c14, c01, c07, playCount, strPath, strFileName
                    FROM movieview JOIN setlinkmovie ON movieview.idMovie=setlinkmovie.idMovie
                    WHERE setlinkmovie.idSet=%i ORDER BY c07
                    """ % int( idSet )
            movies = self.fetch( sql, keys )
        except:
            LOGGER.error.print_exc()
        return movies

    def getThumbsOfSet( self, idSet ):
        movieset, art = [], {}
        try:
            sql = """
                SELECT c00, c10, c08, c20, c07
                FROM movieview JOIN setlinkmovie ON movieview.idMovie=setlinkmovie.idMovie
                WHERE setlinkmovie.idSet=%i ORDER BY c07
                """
            keys = [ "strTitle", "strSortTitle", "strThumbs", "strFanarts", "strYear" ]
            movieset = self.fetch( sql % int( idSet ), keys )
            art      = self.getArtForItem( idSet )
        except:
            LOGGER.error.print_exc()
        return movieset, art

    def getDurationOfSet( self, idSet ):
        duration = ""
        try:
            sql = """
                SELECT ROUND(SUM(iVideoDuration)/60.0)
                FROM movieview JOIN setlinkmovie ON movieview.idMovie=setlinkmovie.idMovie
                JOIN streamdetails ON movieview.idFile=streamdetails.idFile
                WHERE setlinkmovie.idSet=%i
                """
            duration = self.fetch( sql % int( idSet ), index=0 )
            if duration: duration = "".join( duration ).split( "." )[ 0 ]
        except:
            LOGGER.error.print_exc()
        return duration

    def getCastAndRoleOfSet( self, idSet ):
        castandrole = []
        try:
            sql = """
                SELECT actors.idActor, actors.strActor, actorlinkmovie.strRole, movieview.c00
                FROM movieview JOIN setlinkmovie ON movieview.idMovie=setlinkmovie.idMovie
                JOIN actorlinkmovie ON movieview.idMovie=actorlinkmovie.idMovie
                JOIN actors ON actors.idActor=actorlinkmovie.idActor
                WHERE setlinkmovie.idSet=%i ORDER BY movieview.c07, actorlinkmovie.iOrder
                """
            #keys = [ "idActor", "cast", "role", "movie" ]
            castandrole = self.fetch( sql % int( idSet ) )#, keys )
        except:
            LOGGER.error.print_exc()
        return castandrole
