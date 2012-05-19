"""
    Database module
"""

#Modules general
import time
from glob import glob
from datetime import timedelta
from traceback import print_exc
from urllib import urlopen, quote_plus
from re import DOTALL, findall, search

# Modules XBMC
import xbmc
import xbmcvfs

sqlite3 = None
try: import sqlite3
except: pass


DB_PATHS = "".join( glob( xbmc.translatePath( "special://Database/MyVideos*.db" ) )[ -1: ] )

TABLES = {
    'actor':      ( 'actors',     'idActor'   ),
    'director':   ( 'actors',     'idActor'   ),
    'episode':    ( 'episode',    'idEpisode' ),
    'movie':      ( 'movie',      'idMovie'   ),
    'musicvideo': ( 'musicvideo', 'idMVideo'  ),
    'set':        ( 'sets',       'idSet'     ),
    'tvshow':     ( 'tvshow',     'idShow'    ),
    }


def time_took( t ):
    return str( timedelta( seconds=( time.time() - t ) ) )


def LOG( msg, level=xbmc.LOGDEBUG ):
    xbmc.log( msg, level )


#xbmcdb = xbmc.executehttpapi
#executehttpapi cause Crash/SystemExit if multi addon running in backend!!!
# use urllib with xbmc.getIPAddress()
def getXbmcHttpBaseUrl():
    data = open( xbmc.translatePath( "special://userdata/guisettings.xml" ) ).read()
    webserver = search( '<webserver>(.*?)</webserver>',                 data ).group( 1 )
    password  = search( '<webserverpassword>(.*?)</webserverpassword>', data ).group( 1 )
    port      = search( '<webserverport>(.*?)</webserverport>',         data ).group( 1 )
    username  = search( '<webserverusername>(.*?)</webserverusername>', data ).group( 1 )
    xbmcHttp  = "http://"
    if password and username: xbmcHttp += "%s:%s@" % ( username, password )
    xbmcHttp += xbmc.getIPAddress() #"localhost" #"107.0.0.1"
    if port and port != "80": xbmcHttp += ":%s" % port
    xbmcHttp += "/xbmcCmds/xbmcHttp"
    return xbmcHttp
xbmcHttp = getXbmcHttpBaseUrl()
def xbmcdb( command, *params ):
    source = ""
    url = xbmcHttp
    try:
        params = ";".join( list( params ) )
        url   += "?command=%s&parameter=%s" % ( command, params )
        source = urlopen( url ).read()
        #source = xbmc.executehttpapi( "%s(%s)" % ( command, params ) )
    except:
        pass
    LOG( "xbmcart.xbmcdb::url: %s" % url )
    LOG( "xbmcart.xbmcdb::response: %r" % source )
    return source


class Records:
    """ fetch records """

    def __init__( self ):
        self.idVersion = self.getVersion()
        if self.idVersion < 63:
            raise Exception( 'xbmcart invalid database version: %r' % self.idVersion )

    def deprecatedCommit( self, sql ):
        done = False
        try:
            done = ( "done" in xbmcdb( "ExecVideoDatabase", quote_plus( sql ) ).lower() )
        except: print_exc()
        return done

    def deprecatedFetch( self, sql, index=None ):
        fields = []
        try:
            records = xbmcdb( "QueryVideoDatabase", quote_plus( sql ) )
            regexp = "<field>(.*?)</field>"
            if index is None: regexp *= 2
            fields = findall( regexp, records, DOTALL )
        except:
            print_exc()
        return fields

    def commit( self, sql ):
        done = False
        committed = False
        if DB_PATHS and sqlite3:
            db = None
            try:
                db = sqlite3.connect( DB_PATHS, check_same_thread=False )
                done = bool( db.execute( sql ).rowcount )
                if done: db.commit()
                committed = True
            except:
                print_exc()
            if hasattr( db, "close" ):
                db.close()
        if not committed:
            done = self.deprecatedCommit( sql )
        return done

    def fetch( self, sql, index=None ):
        fields = []
        fetched = False
        if DB_PATHS and sqlite3:
            db = None
            try:
                db = sqlite3.connect( DB_PATHS, check_same_thread=False )
                records = db.execute( sql )
                if index == 0: fields = records.fetchone()
                else: fields = records.fetchall()
                fetched = True
            except:
                print_exc()
            if hasattr( db, "close" ):
                db.close()
        if not fetched:
            fields = self.deprecatedFetch( sql, index )
        return fields

    def getVersion( self ):
        return int( self.fetch( "SELECT idVersion FROM version", index=0 )[ 0 ] )


class Database( Records ):
    """ Main database class """

    def __init__( self ):
        Records.__init__( self )

    def getArt( self, mediaId, mediaType ):
        st = time.time()
        art = []
        try:
            sql = "SELECT type, url FROM art WHERE media_id=%i AND media_type='%s'" % ( int( mediaId ), mediaType )
            for t, u in self.fetch( sql ):
                if not u: continue
                try: u = "image://" + quote_plus( u.encode( "utf-8" ) )
                except:
                    try: u = "image://" + quote_plus( u )
                    except: pass
                art.append( ( t, u ) )
        except:
            print_exc()
        LOG( "xbmcart.getArt(%r, %r) took %r" % ( mediaId, mediaType, time_took( st ) ) )
        return dict( art )

    def setArt( self, mediaId, mediaType, artType, url ):
        st = time.time()
        OK = False
        try:
            # check if exists
            sql = "SELECT art_id FROM art WHERE media_id=%i AND media_type='%s' AND type='%s'" % ( int( mediaId ), mediaType, artType )
            artId = self.fetch( sql, index=0 )
            if artId: # update
                sql = "UPDATE art SET url='%s' WHERE art_id=%i" % ( url, int( artId[ 0 ] ) )
            else: # insert
                sql = "INSERT INTO art(media_id, media_type, type, url) VALUES (%i, '%s', '%s', '%s')" % ( int( mediaId ), mediaType, artType, url )
            OK = self.commit( sql )
        except:
            print_exc()
        if mediaType in [ "actor", "director" ]:
            OK = self.setPeopleArt( mediaId, mediaType, artType, url )
        LOG( "xbmcart.setArt(%r, %r, %r, %r) took %r" % ( mediaId, mediaType, artType, url, time_took( st ) ) )
        return OK

    def setPeopleArt( self, mediaId, mediaType, artType, url ):
        # switch media type
        mediaType = ( "actor", "director" )[ mediaType == "actor" ]
        OK = False
        try:
            sql = "SELECT type, art_id FROM art WHERE media_id=%i AND media_type='%s'" % ( int( mediaId ), mediaType )
            art = dict( [ ( t, i ) for t, i in self.fetch( sql ) ] )
            # check if exists
            artId = art.get( artType )
            if artId: # update
                sql = "UPDATE art SET url='%s' WHERE art_id=%i" % ( url, int( artId ) )
            else: # insert
                sql = "INSERT INTO art (media_id, media_type, type, url) VALUES (%i, '%s', '%s', '%s')" % ( int( mediaId ), mediaType, artType, url )
            OK = self.commit( sql )
        except:
            print_exc()
        return OK

    def notValidMediaID( self, mediaId, mediaType ):
        media_id = -1
        try:
            table, col = TABLES[ mediaType ]
            sql = "SELECT %s FROM %s WHERE %s=%i" % ( col, table, col, int( mediaId ) )
            media_id = int( self.fetch( sql, index=0 )[ 0 ] )
        except:
            print_exc()
        return media_id != int( mediaId )
