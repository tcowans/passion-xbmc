
# Modules general
import time
from datetime import timedelta

# Modules XBMC
import xbmc

try:
    import json
    # test json
    json.loads( "[null]" )
except:
    import simplejson as json

from log import logAPI
LOGGER = logAPI()


def time_took( t ):
    return str( timedelta( seconds=( time.time() - t ) ) )


def getMovies( properties ):
    st = time.time()
    postdata = '{"jsonrpc": "2.0", "id":"1", "method":"VideoLibrary.GetMovies", "params": {"sort":{"method": "title", "order": "ascending"}, "properties": %s}}' % json.dumps( properties )
    s_json = xbmc.executeJSONRPC( postdata )
    try: s_json = unicode( s_json, 'utf-8', errors='ignore' )
    except: pass
    o_json = json.loads( s_json ).get( "result", {} )
    movies = o_json.get( "movies" ) or []
    print "MovieSets::getMovies took %r" % time_took( st )
    return movies


def getMovieSets():
    st = time.time()
    postdata = '{"jsonrpc": "2.0", "id":"1", "method":"VideoLibrary.GetMovieSets", "params": {"properties":["title", "playcount", "fanart", "thumbnail"]}}'
    s_json = xbmc.executeJSONRPC( postdata )
    try: s_json = unicode( s_json, 'utf-8', errors='ignore' )
    except: pass
    o_json = json.loads( s_json ).get( "result", {} )
    movie_sets = o_json.get( "sets" ) or []
    print "MovieSets::getMovieSets took %r" % time_took( st )
    return movie_sets


def setMovieDetails( params ):
    st = time.time()
    postdata = '{"jsonrpc": "2.0", "id": 1, "method": "VideoLibrary.SetMovieDetails", "params": %s}' % json.dumps( params )
    s_json = xbmc.executeJSONRPC( postdata )
    OK = json.loads( s_json ).get( "result" ) == "OK"
    #print s_json, postdata
    print "MovieSets::setMovieDetails took %r" % time_took( st )
    return OK


def setMovieSetPlayCount( idset, playcount ):
    st = time.time()
    postdata = '{"jsonrpc": "2.0", "id":"1", "method":"Files.GetDirectory", "params": {"directory":"videodb://1/7/%i/", "properties":["playcount"], "media":"video"}}' % int( idset )
    result = json.loads( xbmc.executeJSONRPC( postdata ) ).get( "result", {} )

    refresh = False
    for movie in result[ "files" ]:
        if ( movie[ "playcount" ] != playcount ):
            params = { "playcount": playcount, "movieid": int( movie[ "id" ] ) }
            refresh = setMovieDetails( params ) or refresh

    print "MovieSets::setMovieSetPlayCount( %r, %r ) took %r" % ( idset, playcount, time_took( st ) )
    return refresh


def editMovieSetTitle( strSet, idSet ):
    st = time.time()
    OK = False
    try:
        from xbmcart import DATABASE
        OK = DATABASE.commit( "UPDATE sets SET strSet=\"%s\" WHERE idSet=%i" % ( strSet, int( idSet ) ) )
    except:
        LOGGER.error.print_exc()
    print "MovieSets::editMovieSetTitle( %r, %r ) took %r" % ( strSet, idSet, time_took( st ) )
    return OK


def getArtsOfSet( idSet, type="" ):
    st = time.time()
    c_type =  "c08, c20 "
    if type:
        c_type = ( "c08", "c20" )[ type == "fanart" ]
    movieset, art = [], {}
    try:
        from xbmcart import getArt, DATABASE
        #sql = "SELECT c00, c07, %s FROM movieview JOIN setlinkmovie ON movieview.idMovie=setlinkmovie.idMovie WHERE setlinkmovie.idSet=%i ORDER BY c07"
        sql = "SELECT c00, c07, %s FROM movieview WHERE idSet=%i ORDER BY c07"
        movieset = DATABASE.fetch( sql % ( c_type, int( idSet ) ) )
        art      = getArt( idSet, "set" )
    except:
        LOGGER.error.print_exc()
    print "MovieSets::getArtsOfSet( %r, %r ) took %r" % ( idSet, type, time_took( st ) )
    return movieset, art
