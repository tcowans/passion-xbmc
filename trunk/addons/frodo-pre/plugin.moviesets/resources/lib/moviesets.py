"""
    Database module
"""

#Modules general
import os
import sys
import time
from datetime import timedelta
from urllib import quote_plus

# Modules XBMC
import xbmc
import xbmcgui
import xbmcvfs
from xbmcaddon import Addon

# Modules Custom
import xbmcart
from log import logAPI
from videolibrary import *


# constants
ADDON    = Addon( "plugin.moviesets" )
LOGGER   = logAPI()
Language = ADDON.getLocalizedString # ADDON strings
LangXBMC = xbmc.getLocalizedString # XBMC strings


# for more see [$SOURCE/xbmc/interfaces/json-rpc/ServiceDescription.h]
VIDEO_FIELDS_MOVIE = [
    "title", "genre", "year", "rating", "director", "trailer",
    "tagline", "plot", "plotoutline", "originaltitle", "lastplayed",
    "playcount", "writer", "studio", "mpaa", "cast", "country",
    "imdbnumber", "runtime", "set", "showlink", "streamdetails",
    "top250", "votes", "fanart", "thumbnail", "file", "sorttitle",
    "resume", "setid", "dateadded", "tag"
    ]
SORTTITLE = { "method": "sorttitle", "order": "ascending" } #"descending"

# get user separator
try: separator = " %s " % ADDON.getSetting( "separator" )
except: separator = " / "
# get user prefer order
try: SORTTITLE[ "order" ] = ( "ascending", "descending" )[ int( ADDON.getSetting( "order" ) ) ]
except: pass


def time_took( t ):
    return str( timedelta( seconds=( time.time() - t ) ) )


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


def maxRepeat( l ):
    s  = ""
    mx = 0
    for x in l:
        m = l.count( x )
        if m > mx:
            s = x
            mx = m
    return s


def getFullMovieSetsDetails( allsets=False ):
    from setdetails import MovieSetDetails
    st = time.time()
    listitems  = []
    movie_sets = getMovieSets()
    #print json.dumps( movie_sets, sort_keys=True, indent=2 )
    movies     = getMovies( VIDEO_FIELDS_MOVIE )
    #
    sets = {}
    for s in movie_sets: #keys: [u'title', u'fanart', u'label', 'movies', u'playcount', u'thumbnail', u'setid'] default: movies
        sets[ s[ "setid" ] ] = MovieSetDetails( s )
    for movie in movies:
        if not movie[ "setid" ]: continue
        setid = movie[ "setid" ]
        if not sets.get( setid ):
            if not allsets: continue
            title = movie[ "set" ]
            art = xbmcart.getArt( setid, "set" )
            s = { "setid": setid, "title": title, "label": title, "thumbnail": art.get( "thumb", "" ), "fanart": art.get( "fanart", "" ) }
            sets[ setid ] = MovieSetDetails( s )
        sets[ setid ][ "movies" ].append( movie )

    sortorder = ( SORTTITLE[ "order" ] == "descending" )
    for countset, item in enumerate( sorted( sets.items() ) ):
        try:
            setid, movieset = item
            # set total movie in set
            movieset[ "total_movies" ] = len( movieset[ "movies" ] )
            #print ( movieset[ "title" ], movieset[ "total_movies" ] )

            # set saga icon
            movieset[ "thumbnail" ] = movieset.get( "thumbnail" ) or ""
            # set saga fanart
            movieset[ "fanart" ] = movieset.get( "fanart" ) or ""

            # set movieset listitem
            listitem = xbmcgui.ListItem( movieset[ 'title' ], str( setid ), "DefaultMovies.png" )

            movies = sorted( movieset[ "movies" ], key=lambda m: m[ "year" ], reverse=sortorder )
            for count, movie in enumerate( movies ):
                try:
                    try:
                        dateadded = ".".join( movie[ "dateadded" ].split()[ 0 ].split( "-" )[ ::-1 ] )
                        if dateadded > movieset[ "date" ]: movieset[ "date" ] = dateadded
                    except: pass
                    # set last movie played in set
                    if movie.get( "lastplayed" ) > movieset[ "lastplayed" ]:
                        movieset[ "lastplayed" ] = movie[ "lastplayed" ]
                    # add movie title to original
                    movieset[ "originaltitle" ].append( movie[ "title" ] )
                    # update cast and role (cast as role in movie  (year))
                    for c in movie[ "cast" ]:
                        try:
                            role = " ".join( [ c[ "role" ], LangXBMC( 1405 ), movie[ "title" ], " (%s)" % str( movie[ "year" ] ) ] )
                            movieset[ "cast" ].append( ( c[ "name" ], role ) )
                        except:
                            pass
                   # set writer and director
                    if movie.get( "writer" ):   movieset[ "writer" ] += [ w for w in movie[ "writer" ] if w and w not in movieset[ "writer" ] ]
                    if movie.get( "director" ): movieset[ "director" ] += [ d for d in movie[ "director" ] if d and d not in movieset[ "director" ] ]
                    # update runtime
                    movieset[ "runtime" ] += int( movie.get( "runtime" ) or "0" )
                    # update years
                    if movie[ "year" ] > 0: movieset[ "years" ].add( str( movie[ "year" ] ) )
                    # update mpaa
                    if movie.get( "mpaa" ): movieset[ "mpaa" ].add( movie[ "mpaa" ] )
                    # set watched count
                    if bool( movie[ "playcount" ] ): movieset[ "watched" ] += 1
                    # update genres
                    movieset[ "genre" ].update( movie[ "genre" ] )
                    movieset[ "genre" ].discard( "" )
                    # add country
                    movieset[ "country" ].update( movie[ "country" ] )
                    movieset[ "country" ].discard( "" )
                    # add studio
                    movieset[ "studio" ].update( movie[ "studio" ] )
                    movieset[ "studio" ].discard( "" )
                    # add plot movie to plotset
                    movieset[ "plot" ] += "[B]%(title)s (%(year)s)[/B][CR]%(plot)s[CR][CR]" % movie
                    # set RatingAndVotes info
                    movieset[ "rating" ] += movie.get( "rating" ) or 0.0
                    try: movieset[ "votes" ] += int( movie.get( "votes", "0" ).replace( ",", "" ) )
                    except: pass

                    # set stacktrailer, add trailer
                    if movie.get( "trailer" ): movieset[ "stacktrailer" ].append( movie[ "trailer" ] )
                    # set stackpath, add movie path
                    movieset[ "stackpath" ].append( movie[ "file" ] )

                    #optional streamdetails
                    sd = movie.get( "streamdetails" ) or {}
                    try:
                        sdv = ( sd.get( "video" ) or [{}] )[ 0 ]
                        movieset[ "sdv_duration" ] += sdv.get( "duration", 0 )
                        movieset[ "sdv_width" ]    += sdv.get( "width",    0 )
                        movieset[ "sdv_height" ]   += sdv.get( "height",   0 )
                        movieset[ "sdv_aspect" ]   += sdv.get( "aspect",   0 )
                        movieset[ "sdv_codecs" ].append( sdv.get( "codec", "" ) )
                    except:
                        LOGGER.error.print_exc()
                    try:
                        sda = ( sd.get( "audio" ) or [{}] )[ 0 ]
                        movieset[ "sda_codecs" ].append( sda.get( "codec", "" ) )
                        movieset[ "sda_channels" ].append( sda.get( "channels", "" ) )
                        movieset[ "sda_langs" ].append( sda.get( "language", "" ) )
                    except:
                        LOGGER.error.print_exc()

                    # use first path if stacked. for prevent [WARNING: XFILE::CFileFactory::CreateLoader - Unsupported protocol(stack) in path_exists( moviepath + "extrafanart" )] 
                    if "stack://" in movie[ "file" ]: movie[ "file" ] = movie[ "file" ][ 8 : ].split( " , " )[ 0 ]
                    # set movie dir path
                    moviepath, filename  = os.path.split( movie[ "file" ] )
                    filesep = ( "/", "\\" )[ not movie[ "file" ].count( "/" ) ]

                    # not realy used
                    if not movieset[ "nfofile" ]:
                        setpath = os.path.dirname( moviepath ) + filesep
                        if xbmcvfs.exists( setpath + "movieset.nfo" ):
                            movieset[ "nfofile" ] = setpath + "movieset.nfo"

                    # set movies properties
                    movie_base_prop = "movie.%i." % ( count + 1 )
                    listitem.setProperty( movie_base_prop + "Title",     movie[ "title" ] )
                    listitem.setProperty( movie_base_prop + "sortTitle", movie.get( "sorttitle" ) or "" )
                    listitem.setProperty( movie_base_prop + "Filename",  filename )
                    listitem.setProperty( movie_base_prop + "Path",      moviepath + filesep )
                    #listitem.setProperty( movie_base_prop + "Plot",      movie[ "plot" ] )
                    listitem.setProperty( movie_base_prop + "Year",      str( movie[ "year" ] or "" ) )
                    listitem.setProperty( movie_base_prop + "Trailer",   movie.get( "trailer" ) or "" )
                    listitem.setProperty( movie_base_prop + "DBID",      str( movie[ "movieid" ] or "-1" ) )
                    listitem.setProperty( movie_base_prop + "Icon",      movie[ 'thumbnail' ] )
                    listitem.setProperty( movie_base_prop + "Fanart",    movie[ 'fanart' ] )

                except:
                    LOGGER.error.print_exc()

            # set stack path
            movieset[ "stackpath" ] = " ; ".join( movieset[ "stackpath" ] )
            if " ; " in movieset[ "stackpath" ]: movieset[ "stackpath" ] = "stack://" + movieset[ "stackpath" ]
            # set stack trailer
            movieset[ "stacktrailer" ] = " , ".join( movieset[ "stacktrailer" ] )
            if " , " in movieset[ "stacktrailer" ]: movieset[ "stacktrailer" ] = "stack://" + movieset[ "stacktrailer" ]

            # fixe playcount of set
            if movieset[ "watched" ] >= movieset[ "total_movies" ]: movieset[ "playcount" ] = 1

            # set saga icon, if not exists use movie icon
            if not movieset[ "thumbnail" ]: movieset[ "thumbnail" ] = listitem.getProperty( "movie.1.Icon" )
            if movieset[ "thumbnail" ]:     listitem.setThumbnailImage( movieset[ "thumbnail" ] )
            # set saga fanart, if not exists use movie fanart
            if not movieset[ "fanart" ]: movieset[ "fanart" ] = listitem.getProperty( "movie.1.Fanart" )
            if movieset[ "fanart" ]:     listitem.setProperty( "Fanart_Image", movieset[ "fanart" ] )

            # set movieset properties
            listitem.setProperty( "IsSet",              "true" )
            listitem.setProperty( "idSet",              str( setid ) )
            listitem.setProperty( "WatchedMovies",      str( movieset[ "watched" ] ) )
            listitem.setProperty( "UnWatchedMovies",    str( movieset[ "total_movies" ] - movieset[ "watched" ] ) )
            listitem.setProperty( "TotalMovies",        str( movieset[ "total_movies" ] ) )
            listitem.setProperty( "playset",            movieset[ "stackpath" ] )
            listitem.setProperty( "Years",              separator.join( sorted( movieset[ "years" ], reverse=sortorder ) ) )
            listitem.setProperty( "StarRating",         getStarRating( movieset[ "rating" ] / float( movieset[ "total_movies" ] ) ) )
            listitem.setProperty( "Countries",          separator.join( movieset[ "country" ] ) )

            # set listitem infoslabels
            listitem.setInfo( "video", {
                "originaltitle": separator.join( movieset[ "originaltitle" ] ),
                "year":          int( max( movieset[ "years" ] ) ),
                "plot":          movieset[ "plot" ],
                "votes":         str( movieset[ "votes" ] ),
                "title":         movieset[ 'title' ],
                "studio":        separator.join( movieset[ "studio" ] ),
                "rating":        ( movieset[ "rating" ] / float( movieset[ "total_movies" ] ) ),
                "genre":         separator.join( sorted( [ g.strip() for g in movieset[ "genre" ] ] ) ),
                "mpaa":          separator.join( [ m.strip() for m in movieset[ "mpaa" ] ] ),
                "trailer":       movieset[ "stacktrailer" ],
                "playcount":     movieset.get( "playcount" ) or 0,
                "count":         int( movieset[ "total_movies" ] ),
                "duration":      str( movieset[ "runtime" ] ),
                "castandrole":   movieset[ "cast" ],
                "writer":        separator.join( movieset[ "writer" ] ),
                "director":      separator.join( movieset[ "director" ] ),
                "date":          movieset[ "date" ],
                "lastplayed":    movieset[ "lastplayed" ],
                } )
            # set listitem streamdetails
            listitem.addStreamInfo( "video", {
                "codec":    maxRepeat( movieset[ "sdv_codecs" ] ),
                "aspect":   float( movieset[ "sdv_aspect" ] / movieset[ "total_movies" ] ),
                "width":    int(   movieset[ "sdv_width" ]  / movieset[ "total_movies" ] ),
                "height":   int(   movieset[ "sdv_height" ] / movieset[ "total_movies" ] ),
                "duration": int(   movieset[ "sdv_duration" ] ) or int( movieset[ "runtime" ]*60.0 )
                } )
            listitem.addStreamInfo( "audio", {
                "codec":    maxRepeat( movieset[ "sda_codecs" ] ),
                "language": maxRepeat( movieset[ "sda_langs" ] ),
                "channels": int( maxRepeat( movieset[ "sda_channels" ] ) or "-1" )
                } )

            # set Context Menu Items
            c_items  = []# ( LangXBMC( 13347 ), "Action(Queue)" ) ] # add movies to playlist
            c_items += [ ( LangXBMC( 22081 ), "Action(Info)" ) ] # info movie set
            #
            if movieset[ "stackpath" ]:
                # play movies of movie set
                c_items += [ ( LangXBMC( ( 22083, 208 )[ setid == -1 ] ), "RunScript(plugin.moviesets,playset,%s)" % movieset[ "stackpath" ] ) ]

            if setid > -1:
                if listitem.getProperty( "UnWatchedMovies" ) == "0":
                    c_items += [ ( LangXBMC( 16104 ), "RunScript(plugin.moviesets,unwatched,%s)" % str( setid ) ) ]
                else:
                    c_items += [ ( LangXBMC( 16103 ), "RunScript(plugin.moviesets,setwatched,%s)" % str( setid ) ) ]

                c_items += [ ( LangXBMC( 16105 ), "RunScript(plugin.moviesets,edittitle,%s,%s)" % ( str( setid ), movieset[ 'title' ] ) ) ] # edit movie set

            #c_items += [ ( "Manager", "RunScript(plugin.moviesets,manager,%s)" % movieset[ 'title' ] ) ] # manage set
            c_items += [ ( " ".join( [ LangXBMC( 15019 ), LangXBMC( 20342 ) ] ), "RunScript(plugin.moviesets,addmovie,%s)" % movieset[ 'title' ] ) ] # add movies
            c_items += [ ( " ".join( [ LangXBMC( 15015 ), LangXBMC( 20342 ) ] ), "RunScript(plugin.moviesets,remmovie,%s)" % movieset[ 'title' ] ) ] # rem movies
            c_items += [ ( Language( 32330 ), "RunScript(plugin.moviesets,newset,%s)" % movieset[ 'title' ] ) ] # create new movie set

            if setid > -1:
                c_items += [ ( LangXBMC( 20435 ), "RunScript(plugin.moviesets,setthumb,%s,%s)" % ( str( setid ), movieset[ 'title' ] ) ) ] # set thumb
                c_items += [ ( LangXBMC( 20456 ), "RunScript(plugin.moviesets,setfanart,%s,%s)" % ( str( setid ), movieset[ 'title' ] ) ) ] # set fanart

            c_items += [ ( LangXBMC( 646 ),   "RunScript(plugin.moviesets,remset,%s)" % movieset[ 'title' ] ) ] # remove from library
            c_items += [ ( LangXBMC( 1045 ), "Addon.OpenSettings(plugin.moviesets)" ) ] # info movie set
            # add Context Menu Items
            listitem.addContextMenuItems( c_items, True )

            #url = 'videodb://1/7/%s/' % str( setid )
            url = '%s?index=%i&idset=%s' % ( sys.argv[ 0 ], countset, str( setid ) )

            listitem = ( url, listitem, False )
            listitems.append( listitem )
        except:
            LOGGER.error.print_exc()
    
    print "MovieSets::GetFullMovieSetsDetails(allsets=%r) took %r" % ( allsets, time_took( st ) )
    return listitems

'''
class SetDetails:
    """ movie set base variables """
    def __init__( self ):
        self.NFO = ""

        self.watched      = 0
        self.unwatched    = 0
        self.total_movies = 0

        self.rating       = 0.0
        self.votes        = 0
        self.runtime      = 0
        self.duration     = 0.1

        
        self.plotset      = ""
        self.mpaa         = set()
        self.studios      = set()
        self.genres       = set()
        self.years        = set()
        self.countries    = set()
        #self.fanartsets   = set()

        self.stackpath    = []
        self.stacktrailer = []
        self.cast         = []

        self.iWidth       = 0
        self.iHeight      = 0
        self.aspect       = 0.0


def getMovieSetFullDetails( allsets=False ):
    st = time.time()
    listitems  = []
    movie_sets = getMovieSets()
    movies     = getMovies( VIDEO_FIELDS_MOVIE )
    #
    sets = {}
    for s in movie_sets:
        s[ "movies" ] = []
        sets[ s[ "label" ] ] = s
    for movie in movies:
        if movie[ "set" ]:
            strSet = movie[ "set" ]
            if type( strSet ) == type( [] ):
                strSet = strSet[ 0 ]
            sets[ strSet ] = sets.get( strSet ) or { "movies": [] }
            sets[ strSet ][ "movies" ].append( movie )
    #print json.dumps( sets, sort_keys=True, indent=2 )
    #print "MovieSets::GetMovieSetsFullDetails1(allsets=%r) took %r" % ( allsets, time_took( st ) )

    for countset, item in enumerate( sorted( sets.items() ) ):
        strSet, movieset = item
        #print movieset.keys() #[u'title', u'fanart', u'label', 'movies', u'playcount', u'thumbnail', u'setid'] default: movies
        try:
            setid = movieset.get( "setid" ) or -1
            if not allsets and setid == -1: continue

            movies = sorted( movieset[ "movies" ], key=lambda m: m[ "year" ], reverse=( SORTTITLE[ "order" ] == "descending" ) )
            # a changer: use dict movieset and remove SetDetails
            MSD = SetDetails()
            MSD.total_movies = len( movies )
            MSD.unwatched = MSD.total_movies
            #
            # set saga icon
            movieset[ "thumbnail" ] = movieset.get( "thumbnail" ) or ""
            icon = movieset[ "thumbnail" ]
            # set saga fanart
            movieset[ "fanart" ] = movieset.get( "fanart" ) or ""
            Fanart_Image = movieset[ "fanart" ]
            # set label
            movieset[ 'label' ] = movieset.get( 'label' ) or strSet

            # set movieset listitem
            listitem = xbmcgui.ListItem( movieset[ 'label' ], str( setid ), icon, icon )

            #
            sdv_codecs   = []
            sda_codecs   = []
            sda_channels = []
            sda_langs    = []
            #
            originaltitle = []
            director      = []
            writer        = []
            lastplayed    = ""
            for count, movie in enumerate( movies ):
                #print movie.keys() #[u'rating', u'set', u'tagline', u'file', u'year', u'setid', u'plot', u'votes', u'title', u'fanart', u'mpaa', u'writer', u'label', u'thumbnail', u'streamdetails', u'plotoutline', u'resume', u'director', u'imdbnumber', u'studio', u'showlink', u'genre', u'dateadded', u'movieid', u'productioncode', u'country', u'lastplayed', u'premiered', u'originaltitle', u'cast', u'sorttitle', u'playcount', u'runtime', u'top250', u'trailer']
                try:
                    #print zip( movie[ "setid" ], movie[ "set" ] )
                    # fixe id set
                    if setid == -1:
                        try: setid = movie[ "setid" ][ 0 ]
                        except: pass
                        if setid != -1 and ( not movieset[ "thumbnail" ] or not movieset[ "fanart" ] ):
                            art = xbmcart.getArt( setid, "set" )
                            movieset[ "thumbnail" ] = movieset[ "thumbnail" ] or art.get( "thumb" )
                            movieset[ "fanart" ]    = movieset[ "fanart" ] or art.get( "fanart" )
                            listitem.setIconImage( movieset[ "thumbnail" ] )

                    # set last movie played in set
                    if movie.get( "lastplayed" ) > lastplayed:
                        lastplayed = movie[ "lastplayed" ]
                    # add movie title to original
                    originaltitle.append( movie[ "label" ] )
                    # update cast and role
                    for c in movie[ "cast" ]:
                        ## cast as role in movie  (year)
                        try:
                            role = " ".join( [ c[ "role" ], LangXBMC( 1405 ), movie[ "label" ], " (%s)" % str( movie[ "year" ] ) ] )
                            MSD.cast.append( ( c[ "name" ], role ) )
                        except:
                            pass
                    # set writer and director
                    if movie.get( "writer" ):   writer += [ w for w in movie[ "writer" ].split( " / " ) if w not in writer ]
                    if movie.get( "director" ): director += [ w for w in movie[ "director" ].split( " / " ) if w not in director ]
                    # update runtime
                    MSD.runtime += int( movie.get( "runtime" ) or "0" )
                    # update years
                    if movie[ "year" ] > 0: MSD.years.add( str( movie[ "year" ] ) )
                    # update mpaa
                    if movie.get( "mpaa" ): MSD.mpaa.add( movie[ "mpaa" ] )
                    # set watched count
                    if bool( movie[ "playcount" ] ): MSD.watched += 1
                    # update genres
                    MSD.genres.update( movie[ "genre" ].split( " / " ) )
                    # add country
                    if movie.get( "country" ): MSD.countries.update( movie[ "country" ].split( " / " ) )
                    # add studio
                    if movie.get( "studio" ): MSD.studios.update( movie[ "studio" ].split( " / " ) )
                    # add plot movie to plotset
                    MSD.plotset += "[B]%(title)s (%(year)s)[/B][CR]%(plot)s[CR][CR]" % movie
                    # set RatingAndVotes info
                    MSD.rating += movie.get( "rating" ) or 0.0
                    try: MSD.votes += int( movie.get( "votes", "0" ).replace( ",", "" ) )
                    except: pass

                    # set stacktrailer, add trailer
                    if movie.get( "trailer" ): MSD.stacktrailer.append( movie[ "trailer" ] )
                    # set stackpath, add movie path
                    MSD.stackpath.append( movie[ "file" ] )

                    # use first path if stacked. for prevent [WARNING: XFILE::CFileFactory::CreateLoader - Unsupported protocol(stack) in path_exists( moviepath + "extrafanart" )] 
                    if "stack://" in movie[ "file" ]: movie[ "file" ] = movie[ "file" ][ 8 : ].split( " , " )[ 0 ]
                    # 
                    filesep = ( "/", "\\" )[ not movie[ "file" ].count( "/" ) ]
                    moviepath  = os.path.dirname( movie[ "file" ] )

                    # set movies properties 'plot', 'votes', 'rating', 'fanart', 'title', 'label', 'file', 'year', 'genre','playcount', 'runtime', 'thumbnail', 'trailer'
                    movie_base_prop = "movie.%i." % ( count + 1 )
                    listitem.setProperty( movie_base_prop + "Title",     movie[ "title" ] )
                    listitem.setProperty( movie_base_prop + "sortTitle", movie.get( "sorttitle" ) or "" )
                    listitem.setProperty( movie_base_prop + "Filename",  os.path.basename( movie[ "file" ] ) )
                    listitem.setProperty( movie_base_prop + "Path",      moviepath + filesep )
                    listitem.setProperty( movie_base_prop + "Plot",      movie[ "plot" ] )
                    listitem.setProperty( movie_base_prop + "Year",      str( movie[ "year" ] or "" ) )
                    listitem.setProperty( movie_base_prop + "Trailer",   movie.get( "trailer" ) or "" )
                    listitem.setProperty( movie_base_prop + "movieid",   str( movie[ "movieid" ] or "-1" ) )
                    listitem.setProperty( movie_base_prop + "Icon",      movie[ 'thumbnail' ] )
                    listitem.setProperty( movie_base_prop + "Fanart",    movie[ 'fanart' ] )

                    #optional streamdetails
                    try:
                        sd = movie.get( "streamdetails" ) or {}
                        sdv = sd.get( "video" ) or []
                        #print sdv
                        MSD.duration += sum( d.get( "duration", 0 ) for d in sdv )
                        MSD.iWidth   += sum( w.get( "width",    0 ) for w in sdv )
                        MSD.iHeight  += sum( h.get( "height",   0 ) for h in sdv )
                        MSD.aspect   += sum( a.get( "aspect",   0 ) for a in sdv )
                        sdv_codecs   += [ c.get( "codec", "" ) for c in sdv ]
                        # 
                        sda = sd.get( "audio" ) or []
                        #print sda #[{u'channels': 2, u'codec': u'mp3', u'language': u''}]
                        sda_codecs   += [ c.get( "codec", "" ) for c in sda ]
                        sda_channels += [ c.get( "channels", "" ) for c in sda ]
                        sda_langs    += [ l.get( "language", "" ) for l in sda ]
                    except:
                        pass

                    #setpath    = os.path.dirname( moviepath ) + filesep # not realy used
                    #if not MSD.NFO:
                    #    dirs, files = xbmcvfs.listdir( setpath )
                    #    #
                    #    if "movieset.nfo" in files:
                    #        MSD.NFO = setpath + "movieset.nfo"
                            #f = xbmcvfs.File( MSD.NFO )
                            #b = f.read()
                            #f.close()
                            #print repr( b )
                    #print movie.get( "streamdetails" )
                except:
                    LOGGER.error.print_exc()
            try:
                # set saga icon if not exists with movie icon
                if movie[ 'thumbnail' ] and not movieset[ "thumbnail" ]:
                    movieset[ "thumbnail" ] = movie[ 'thumbnail' ]
                    listitem.setIconImage( movieset[ "thumbnail" ] )
                # set saga fanart if not exists with movie fanart
                if movie[ 'fanart' ] and not movieset[ "fanart" ]:
                    movieset[ "fanart" ] = movie[ 'fanart' ]
            except:
                LOGGER.error.print_exc()

            # set movieset properties
            listitem.setProperty( "IsSet",              "true" )
            listitem.setProperty( "idSet",              str( setid ) )
            listitem.setProperty( "WatchedMovies",      str( MSD.watched ) )
            listitem.setProperty( "UnWatchedMovies",    str( MSD.unwatched - MSD.watched ) )
            listitem.setProperty( "TotalMovies",        str( MSD.total_movies ) )
            listitem.setProperty( "Fanart_Image",       movieset[ "fanart" ] )
            listitem.setProperty( "Years",              separator.join( sorted( MSD.years, reverse=( SORTTITLE[ "order" ] == "descending" ) ) ) )
            try: listitem.setProperty( "StarRating",    getStarRating( MSD.rating / float( MSD.total_movies ) ) )
            except: listitem.setProperty( "StarRating", "rating0.png" )
            listitem.setProperty( "Countries",          separator.join( MSD.countries ) )
            #
            #listitem.setProperty( "VideoResolution",    VideoDimsToResolutionDescription( int( MSD.iWidth / MSD.total_movies ), int( MSD.iHeight / MSD.total_movies ) ) )
            #listitem.setProperty( "VideoAspect",        VideoAspectToAspectDescription( float( MSD.aspect / MSD.total_movies ) ) )

            # set stack path
            MSD.stackpath = " ; ".join( MSD.stackpath )
            if " ; " in MSD.stackpath: MSD.stackpath = "stackset://" + MSD.stackpath
            #listitem.setPath( quote_plus( _encode( MSD.stackpath ) ) )
            listitem.setProperty( "playset", MSD.stackpath.replace( "stackset", "stack" ) )
            # set stack trailer
            MSD.stacktrailer = " , ".join( MSD.stacktrailer )
            if " , " in MSD.stacktrailer: MSD.stacktrailer = "stack://" + MSD.stacktrailer

            # fixe playcount
            if MSD.watched >= MSD.total_movies: movieset[ "playcount" ] = 1
            #
            try: dateadded = ".".join( movie[ "dateadded" ].split()[ 0 ].split( "-" )[ ::-1 ] )
            except: dateadded = ""
            # set listitem infoslabels
            listitem.setInfo( "video", {
                "originaltitle": separator.join( originaltitle ),
                "year":        int( max( MSD.years ) ),
                "plot":        MSD.plotset,
                "votes":       str( MSD.votes ),
                "title":       movieset[ 'label' ],
                "studio":      separator.join( MSD.studios ),
                "rating":      ( MSD.rating / float( MSD.total_movies ) ),
                "genre":       separator.join( sorted( [ g.strip() for g in MSD.genres ] ) ),
                "mpaa":        separator.join( [ m.strip() for m in MSD.mpaa ] ),
                "trailer":     MSD.stacktrailer,
                "playcount":   movieset.get( "playcount" ) or 0,
                "count":       int( MSD.total_movies ),
                "duration":    str( MSD.runtime ),
                "castandrole": MSD.cast,
                "writer":      separator.join( writer ),
                "director":    separator.join( director ),
                "date":        dateadded,
                "lastplayed":  lastplayed,
                } )
            # set listitem streamdetails
            listitem.addStreamInfo( "video", {
                "Codec":    maxRepeat( sdv_codecs ),
                "aspect":   float( MSD.aspect / MSD.total_movies ),
                "Width":    int( MSD.iWidth / MSD.total_movies ),
                "Height":   int( MSD.iHeight / MSD.total_movies ),
                "duration": int( MSD.duration ) or int( MSD.runtime*60.0 )
                } )
            listitem.addStreamInfo( "Audio", {
                "Codec":    maxRepeat( sda_codecs ),
                "language": maxRepeat( sda_langs ),
                "channels": int( maxRepeat( sda_channels ) or "-1" )
                } )

            # set Context Menu Items
            c_items  = []# ( LangXBMC( 13347 ), "Action(Queue)" ) ] # add movies to playlist
            c_items += [ ( LangXBMC( 22081 ), "Action(Info)" ) ] # info movie set
            #
            playset = listitem.getProperty( "playset" )
            if playset:
                # play movies of movie set
                c_items += [ ( LangXBMC( ( 22083, 208 )[ setid == -1 ] ), "RunScript(plugin.moviesets,playset,%s)" % playset ) ]

            if setid > -1:
                if listitem.getProperty( "UnWatchedMovies" ) == "0":
                    c_items += [ ( LangXBMC( 16104 ), "RunScript(plugin.moviesets,unwatched,%s)" % str( setid ) ) ]
                else:
                    c_items += [ ( LangXBMC( 16103 ), "RunScript(plugin.moviesets,setwatched,%s)" % str( setid ) ) ]

                c_items += [ ( LangXBMC( 16105 ), "RunScript(plugin.moviesets,edittitle,%s,%s)" % ( str( setid ), strSet ) ) ] # edit movie set

            #c_items += [ ( "Manager", "RunScript(plugin.moviesets,manager,%s)" % strSet ) ] # manage set
            c_items += [ ( " ".join( [ LangXBMC( 15019 ), LangXBMC( 20342 ) ] ), "RunScript(plugin.moviesets,addmovie,%s)" % strSet ) ] # add movies
            c_items += [ ( " ".join( [ LangXBMC( 15015 ), LangXBMC( 20342 ) ] ), "RunScript(plugin.moviesets,remmovie,%s)" % strSet ) ] # rem movies
            c_items += [ ( Language( 32330 ), "RunScript(plugin.moviesets,newset,%s)" % strSet ) ] # create new movie set

            if setid > -1:
                c_items += [ ( LangXBMC( 20435 ), "RunScript(plugin.moviesets,setthumb,%s,%s)" % ( str( setid ), strSet ) ) ] # set thumb
                c_items += [ ( LangXBMC( 20456 ), "RunScript(plugin.moviesets,setfanart,%s,%s)" % ( str( setid ), strSet ) ) ] # set fanart

            c_items += [ ( LangXBMC( 646 ),   "RunScript(plugin.moviesets,remset,%s)" % strSet ) ] # remove from library
            c_items += [ ( LangXBMC( 1045 ), "Addon.OpenSettings(plugin.moviesets)" ) ] # info movie set
            # add Context Menu Items
            listitem.addContextMenuItems( c_items, True )

            #url = 'videodb://1/7/%s/' % setid
            url = '%s?index=%i&idset=%s' % ( sys.argv[ 0 ], countset, str( setid ) )

            listitem = ( url, listitem, False )
            listitems.append( listitem )
            #yield listitem

            #print ( maxRepeat( sdv_codecs ), sdv_codecs )
            #print ( strSet, len( movies ), MSD.years )
            #print json.dumps( MSD.cast,  indent=2 )
            #print "-"*100
        except:
            LOGGER.error.print_exc()
    print "MovieSets::GetMovieSetFullDetails(allsets=%r) took %r" % ( allsets, time_took( st ) )
    return listitems


'''
