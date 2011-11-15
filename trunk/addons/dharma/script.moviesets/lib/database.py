"""
    Database module
"""

#Modules general
import os
import md5
import sys
from urllib import quote_plus
from re import DOTALL, findall, sub

# Modules XBMC
import xbmcgui
from xbmcaddon import Addon
from xbmc import executehttpapi, translatePath
xbmcdb = executehttpapi
ADDON = Addon( "script.moviesets" )

# Modules Custom
import jsonrpc
from file_item import Thumbnails
from log import logAPI

log = logAPI()

TBN = Thumbnails()

# fielsd for executeJSONRPC, VideoInfoTag.cpp
fields = [ "dbid", "sorttitle", "originaltitle ", "title", "genre", "plot", "year", "fanart", "playcount", "rating",
    "votes", "runtime", "trailer", "director", "studio", "writingcredits", "country", "mpaa" ]
sorttitle = { "method": "sorttitle", "order": "ascending" } #"descending"


def _encode( text, encoding="utf-8" ):
    try: text = text.encode( encoding )
    except: pass
    return text

def getStarRating( rating ):
    try:
        f = ( float( rating ) * 0.5 ) # + 0.5
        if f >= ( int( f ) + 0.5 ):
            return "rating%d.png" % int( f + 0.5 )
        return "rating%d.png" % int( f )
    except:
        log.error.exc_info( sys.exc_info() )
    return "rating0.png"


class Records:
    """ fetch records """

    def __init__( self ):
        self._set_records_format()

    def _set_records_format( self ):
        # format our records start and end
        xbmcdb( "SetResponseFormat()" )
        xbmcdb( "SetResponseFormat(OpenRecord,<records>)" )
        xbmcdb( "SetResponseFormat(CloseRecord,</records>)" )

    def commit( self, sql ):
        done = False
        try: done = ( "done" in xbmcdb( "ExecVideoDatabase(%s)" % quote_plus( sql ), ).lower() )
        except: log.error.exc_info( sys.exc_info(), self )
        return done

    def fetch( self, sql, keys=None, index=None ):
        records = []
        try:
            records_xml = xbmcdb( "QueryVideoDatabase(%s)" % quote_plus( sql ), )
            records = findall( "<records>(.+?)</records>", records_xml, DOTALL )
        except:
            log.error.exc_info( sys.exc_info(), self )
        return self.parseFields( records, keys, index )

    def parseFields( self, records, keys=None, index=None ):
        fields = []
        try:
            for record in records:
                record = findall( "<field>(.*?)</field>", record, DOTALL )
                if keys: record = dict( zip( keys, record ) )
                fields.append( record )
        except:
            log.error.exc_info( sys.exc_info(), self )
        if fields and index is not None:
            try: fields = fields[ index ]
            except: log.error.exc_info( sys.exc_info(), self )
        return fields


class Database( Records ):
    """ Main database class """

    def __init__( self, *args, **kwargs ):
        Records.__init__( self )

    def addSet( self, strSet ):
        try:
            # check if exists
            sql = "select idSet from sets where strSet like '%s'" % strSet
            id = "".join( self.fetch( sql, index=0 ) )
            if not id:
                # insert not exists
                OK = self.commit( "insert into sets (idSet, strSet) values(NULL, '%s')" % strSet )
                #if OK:
                id = "".join( self.fetch( sql, index=0 ) )
            return int( id )
        except:
            log.error.exc_info( sys.exc_info(), self )
        return -1

    def addSetToMovie( self, idMovie, idSet ):
        OK = False
        try:
            # check if match or if exists in other set
            #sql = "select * from setlinkmovie where idSet=%i and idMovie=%i" % ( idSet, idMovie, )
            sql = "select * from setlinkmovie where (idSet=%i and idMovie=%i) or idMovie=%i" % ( int( idSet ), int( idMovie ), int( idMovie ), )
            exists = self.fetch( sql, index=0 )
            if not exists:
                # insert not exists
                OK = self.commit( "insert into setlinkmovie (idSet,idMovie) values(%i,%i)" % ( int( idSet ), int( idMovie ), ) )
        except:
            log.error.exc_info( sys.exc_info(), self )
        return OK

    def deleteMovieOfSet( self, idMovie, idSet ):
        OK = False
        try:
            if idMovie == -1: sql = "delete from setlinkmovie where idSet=%i" % ( int( idSet ), )
            else: sql = "delete from setlinkmovie where idSet=%i and idMovie=%i" % ( int( idSet ), int( idMovie ), )
            OK = self.commit( sql )
        except:
            log.error.exc_info( sys.exc_info(), self )
        return OK

    def deleteSet( self, idSet ):
        OK = False
        try:
            OK = self.commit( "delete from sets where idSet=%i" % int( idSet ) )
            if OK:
                icon = TBN.get_cached_saga_thumb( idSet )
                if os.path.exists( icon ): os.remove( icon )
                fanart = TBN.get_cached_saga_thumb( idSet, True )
                if os.path.exists( fanart ): os.remove( fanart )
                OK = self.deleteMovieOfSet( -1, idSet )
        except:
            log.error.exc_info( sys.exc_info(), self )
        return OK

    def editMovieSortTitle( self, sortTitle, idMovie ):
        OK = False
        try: OK = self.commit( "update movie set c10='%s' where idMovie=%i" % ( sortTitle, int( idMovie ) ) )
        except: log.error.exc_info( sys.exc_info(), self )
        return OK

    def getFileId( self, strFilenameAndPath ):
        try:
            # SplitPath
            strPath, strFileName = os.path.split( strFilenameAndPath )
            if strPath: strPath += ( "/", "\\" )[ not strPath.count( "/" ) ]
            idPath = self.getPathId( strPath )
            if ( idPath >= 0 ):
                sql = "select idFile from files where strFileName like '%s' and idPath=%i" % ( strFileName, idPath )
                idFile = "".join( self.fetch( sql, index=0 ) )
                return int( idFile )
        except:
            log.error.exc_info( sys.exc_info(), self )
        return -1

    def getPathId( self, strPath ):
        try:
            sql = "select idPath from path where strPath like '%s'" % strPath
            idPath = "".join( self.fetch( sql, index=0 ) )
            if not idPath:
                if strPath.startswith( "ftp://" ) or strPath.startswith( "smb://" ):
                    for ipath, spath in self.fetch( "select idPath, strPath from path" ):
                        if strPath == sub( "(.*?://)(.*?@)(.*?)", "\\1", spath ):
                            idPath = ipath
                            break
            if idPath:
                return int( idPath )
        except:
            log.error.exc_info( sys.exc_info(), self )
        return -1

    def getMovie( self, strFilenameAndPath, strTitle ):
        try:
            idFile = self.getFileId( strFilenameAndPath )
            if ( idFile == -1 ):
                sql = "select idMovie, c00, c10 from movie where c00 like \"%s\"" % strTitle
            else:
                sql = "select idMovie, c00, c10 from movie where idFile=%i" % int( idFile )
            movie = self.fetch( sql, index=0 )
            return int( movie[ 0 ] ), movie[ 1 ], movie[ 2 ]
        except:
            log.error.exc_info( sys.exc_info(), self )
        return -1, "", ""

    def getSet( self, strSet ):
        try:
            movieset = self.fetch( 'select * from sets where strSet like \"%s\"' % strSet, index=0 )
            if movieset:
                idSet, strSet = movieset
                return int( idSet ), strSet
        except:
            log.error.exc_info( sys.exc_info(), self )
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
            log.error.exc_info( sys.exc_info(), self )
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
            log.error.exc_info( sys.exc_info(), self )
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
                    WHERE setlinkmovie.idSet=%i ORDER BY c10
                    """ % int( idSet )
            movies = self.fetch( sql, keys )
        except:
            log.error.exc_info( sys.exc_info(), self )
        return movies

    def getThumbsOfSet( self, idSet ):
        movieset = []
        try:
            sql = """
                SELECT c10, c08, c20
                FROM movieview JOIN setlinkmovie ON movieview.idMovie=setlinkmovie.idMovie
                WHERE setlinkmovie.idSet=%i ORDER BY c10
                """
            keys = [ "strSortTitle", "strThumbs", "strFanarts" ]
            movieset = self.fetch( sql % int( idSet ), keys )
        except:
            log.error.exc_info( sys.exc_info(), self )
        return movieset

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
            log.error.exc_info( sys.exc_info(), self )
        return duration

    def getCastAndRoleOfSet( self, idSet ):
        castandrole = []
        try:
            sql = """
                SELECT strActor, strRole, movieview.c00
                FROM movieview JOIN setlinkmovie ON movieview.idMovie=setlinkmovie.idMovie
                JOIN actorlinkmovie ON movieview.idMovie=actorlinkmovie.idMovie
                JOIN actors ON actors.idActor=actorlinkmovie.idActor
                WHERE setlinkmovie.idSet=%i ORDER BY strActor, movieview.c10
                """
            keys = [ "cast", "role", "movie" ]
            castandrole = self.fetch( sql % int( idSet ) )#, keys )
        except:
            log.error.exc_info( sys.exc_info(), self )
        return castandrole

    def get_cached_thumb( self, fpath ):
        # fixe me: xbmc not change/reload/refresh image if path is same
        fpath = translatePath( fpath )
        filename = md5.new( open( fpath ).read( 250 ) ).hexdigest()
        temp = "special://temp/moviesets/%s.tbn" % filename
        if not os.path.exists( temp ): executehttpapi( "FileCopy(%s,%s)" % ( fpath, temp ) )#.replace( "<li>", "" )
        return ( fpath, temp )[ os.path.exists( temp ) ]

    def getContainerMovieSets( self, infoSet=None ):
        jrapi = jsonrpc.jsonrpcAPI()
        # GET MOVIESETS
        json = jrapi.Files.GetDirectory( directory="videodb://1/7/", media="video" )
        movie_sets = json.get( 'directories', [] )
        total = json.get( "total" ) or len( movie_sets )

        # dico for synchronize container
        moviesets = {}
        # set dymmy listitem label: container title , label2: total movie sets
        if infoSet is not None: listitems = [] # get only one user want info
        else: listitems = [ xbmcgui.ListItem( "Movie Sets", str( total ) ) ]

        # get user separator
        try: separator = " %s " % ADDON.getSetting( "separator" )
        except: separator = " / "
        # get user prefer order
        try: sorttitle[ "order" ] = ( "ascending", "descending" )[ int( ADDON.getSetting( "order" ) ) ]
        except: pass

        # enum movie sets
        for countset, movieset in enumerate( movie_sets ):
            #print movieset.keys()
            try:
                idSet = movieset[ "file" ][ 14:-1 ]
                if infoSet is not None and idSet != infoSet:
                    continue # get only one user want info
                # get saga icon and fanart
                icon = ( "", movieset[ 'thumbnail' ] )[ os.path.exists( translatePath( movieset[ 'thumbnail' ] ) ) ]
                d, f = os.path.split( movieset[ 'thumbnail' ] )
                c_fanart = "%sFanart/%s" % ( d[ :-1 ], f )
                Fanart_Image = ( "", c_fanart )[ os.path.exists( translatePath( c_fanart ) ) ]
                # fixe me: xbmc not change/reload/refresh image if path is same
                if Fanart_Image: Fanart_Image = self.get_cached_thumb( Fanart_Image )
                if icon: icon = self.get_cached_thumb( icon )
                # set movieset listitem
                listitem = xbmcgui.ListItem( movieset[ 'label' ], idSet, icon, icon )
                #listitem.setPath( "ActivateWindow(10025,%s)" % movieset[ "file" ] )

                # get list of movieset
                json = jrapi.Files.GetDirectory( directory=movieset[ "file" ], fields=fields, sort=sorttitle, media="video" )
                movies = json.get( 'files', [] )
                total_movies = json.get( "total" ) or len( movies )
                # set base variables
                watched, unwatched = 0, total_movies
                rating, votes = 0.0, 0
                plotset = ""
                studios = set()
                genres  = set()
                years   = set()
                fanartsets = set()
                countries  = set()
                stackpath  = []
                stacktrailer = []

                # enum movies
                for count, movie in enumerate( movies ):
                    #print movie.keys()
                    try:
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
                        # set RatingAndVotes info
                        rating += movie.get( "rating", 0.0 )
                        votes += int( movie.get( "votes", "0" ).replace( ",", "" ) )

                        # set movies properties 'plot', 'votes', 'rating', 'fanart', 'title', 'label',
                        # 'dbid', 'file', 'year', 'genre','playcount', 'runtime', 'thumbnail', 'trailer'
                        b_property = "movie.%i." % ( count + 1 )
                        #for key in movie.keys(): listitem.setProperty( b_property + key, str( movie[ key ] ) )
                        moviepath = os.path.dirname( movie[ "file" ] ) + ( "/", "\\" )[ not movie[ "file" ].count( "/" ) ]
                        listitem.setProperty( b_property + "Title",     movie[ "title" ] )
                        listitem.setProperty( b_property + "sortTitle", movie.get( "sorttitle", "" ) )
                        listitem.setProperty( b_property + "Filename",  os.path.basename( movie[ "file" ] ) )
                        listitem.setProperty( b_property + "Path",      moviepath )
                        listitem.setProperty( b_property + "Plot",      movie[ "plot" ] )
                        listitem.setProperty( b_property + "Year",      str( movie[ "year" ] or "" ) )
                        listitem.setProperty( b_property + "Trailer",   movie.get( "trailer", "" ) )
                        # set icon property
                        icon = ( "", movie[ 'thumbnail' ] )[ os.path.exists( translatePath( movie[ 'thumbnail' ] ) ) ]
                        #print repr( icon )
                        if not icon: # check for auto-
                            _path, _file = os.path.split( movie[ 'thumbnail' ] )
                            a_icon = os.path.join( _path, "auto-" + _file )
                            icon = ( "", a_icon )[ os.path.exists( translatePath( a_icon ) ) ]
                        listitem.setProperty( b_property + "Icon", icon )
                        # set fanart property
                        fanart = ( "", movie[ 'fanart' ] )[ os.path.exists( translatePath( movie[ 'fanart' ] ) ) ]
                        listitem.setProperty( b_property + "Fanart", fanart )
                        if fanart and not Fanart_Image: Fanart_Image = fanart
                        # set extrafanart: if not exists set empty
                        extrafanart = moviepath + "extrafanart"
                        extrafanart = ( "", extrafanart )[ os.path.exists( extrafanart ) ]
                        listitem.setProperty( b_property + "ExtraFanart", extrafanart )
                        # set extrafanart for movieset if exists set first found
                        #fanartsets.add( os.path.dirname( os.path.dirname( moviepath ) ) )
                        if listitem.getProperty( "ExtraFanart" ): continue
                        fanartset = os.path.dirname( os.path.dirname( moviepath ) )
                        fanartset += ( "/", "\\" )[ not fanartset.count( "/" ) ] + "extrafanart"
                        if os.path.exists( fanartset ): listitem.setProperty( "ExtraFanart", fanartset )
                    except:
                        log.error.exc_info( sys.exc_info(), self )

                # set movieset properties
                listitem.setProperty( "HasMovieSets",    "true" )
                listitem.setProperty( "WatchedMovies",   str( watched ) )
                listitem.setProperty( "UnWatchedMovies", str( unwatched - watched ) )
                listitem.setProperty( "TotalMovies",     str( total_movies ) )
                listitem.setProperty( "Fanart_Image",    Fanart_Image )
                listitem.setProperty( "Years",           separator.join( sorted( years ) ) )
                listitem.setProperty( "StarRating",      getStarRating( rating / float( total_movies ) ) )
                listitem.setProperty( "Countries",       separator.join( countries ) )

                # set stack path
                stackpath = " , ".join( stackpath )
                if " , " in stackpath: stackpath = "stack://" + stackpath
                listitem.setPath( quote_plus( _encode( stackpath ) ) )
                # set stack trailer
                stacktrailer = " , ".join( stacktrailer )
                if " , " in stacktrailer: stacktrailer = "stack://" + stacktrailer

                # set listitem infoslabels
                listitem.setInfo( "video", {
                    "plot":     plotset,
                    "votes":    str( votes ),
                    "title":    movieset[ 'label' ],
                    "studio":   separator.join( studios  ),
                    "duration": self.getDurationOfSet( idSet ),
                    "rating":   ( rating / float( total_movies ) ),
                    "genre":    separator.join( sorted( [ g.strip() for g in genres ] ) ),
                    "trailer":  stacktrailer,
                    } )

                moviesets[ movieset[ 'label' ] ] = countset + 1
                listitems.append( listitem )

                if infoSet is not None and idSet == infoSet:
                    moviesets[ movieset[ 'label' ] ] = 0
                    break # get only one user want info
            except:
                log.error.exc_info( sys.exc_info(), self )
        return listitems, moviesets

