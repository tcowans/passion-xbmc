
DEBUG = False

import os
import sys
import ftplib
import urlparse
from traceback import print_exc

import ping

from log import logAPI
LOGGER = logAPI()

IsNotPython24 = ( sys.version >= "2.5" )

if IsNotPython24:
    url_parse = urlparse.urlparse
else:
    class BaseResult( tuple ):
        """Base class for the parsed result objects.

        This provides the attributes shared by the two derived result
        objects as read-only properties.  The derived classes are
        responsible for checking the right number of arguments were
        supplied to the constructor.

        """

        __slots__ = ()

        # Attributes that access the basic components of the URL:

        @property
        def scheme(self):
            return self[0]

        @property
        def netloc(self):
            return self[1]

        @property
        def path(self):
            return self[2]

        @property
        def query(self):
            return self[-2]

        @property
        def fragment(self):
            return self[-1]

        # Additional attributes that provide access to parsed-out portions
        # of the netloc:

        @property
        def username(self):
            netloc = self.netloc
            if "@" in netloc:
                userinfo = netloc.split("@", 1)[0]
                if ":" in userinfo:
                    userinfo = userinfo.split(":", 1)[0]
                return userinfo
            return None

        @property
        def password(self):
            netloc = self.netloc
            if "@" in netloc:
                userinfo = netloc.split("@", 1)[0]
                if ":" in userinfo:
                    return userinfo.split(":", 1)[1]
            return None

        @property
        def hostname(self):
            netloc = self.netloc
            if "@" in netloc:
                netloc = netloc.split("@", 1)[1]
            if ":" in netloc:
                netloc = netloc.split(":", 1)[0]
            return netloc.lower() or None

        @property
        def port(self):
            netloc = self.netloc
            if "@" in netloc:
                netloc = netloc.split("@", 1)[1]
            if ":" in netloc:
                port = netloc.split(":", 1)[1]
                return int(port, 10)
            return None

    class ParseResult( BaseResult ):
        __slots__ = ()

        def __new__( cls, *args ):
            return BaseResult.__new__( cls, args )

        @property
        def params( self ):
            return self[ 3 ]

        def geturl( self ):
            return urlparse.urlunparse(self)

    def url_parse( url, scheme='', allow_fragments=True ):
        o = urlparse.urlparse( url, scheme, allow_fragments )
        return ParseResult( *o )


class Remotes( dict ):
    def __init__( self, *args, **kwargs ):
        self.update( kwargs )

    def getStatut( self, hostname, refresh=False ):
        if refresh and self.has_key( hostname ):
            del self[ hostname ]
        if not self.has_key( hostname ):
            on_off = ( ping.quiet_ping( hostname, count=2 )[ 1 ] is None )
            self[ hostname ] = ( "on", "off" )[ on_off ]
        return self[ hostname ]

    def getStatutFromPath( self, rpath, onoff="off", refresh=False ):
        return ( self.getStatut( url_parse( rpath ).hostname, refresh ) == onoff )

    def isOff( self, hostname, refresh=False ):
        return ( self.getStatut( hostname, refresh ) == "off" )

    def isOn( self, hostname, refresh=False ):
        return ( self.getStatut( hostname, refresh ) == "on" )

REMOTES = Remotes()


def copy_to_ftp( src, dst ):
    OK = False
    ftp = None
    try:
        o = url_parse( os.path.dirname( dst ) + "/" )
        if DEBUG:
            print o

        if REMOTES.isOff( o.hostname ):
            return OK

        ftp = ftplib.FTP( o.hostname )
        ftp.login( o.username, o.password )

        ftp.cwd( o.path )
        if DEBUG:
            ftp.retrlines( 'LIST' ) # list directory contents
            print "-"*100
        ftp.storbinary( "STOR " + os.path.basename( src ), open( src, "rb" ) )
        if DEBUG:
            ftp.retrlines( 'LIST' ) # list directory contents
            print "-"*100
        OK = True
    except:
        OK = False
        LOGGER.error.print_exc()
    if hasattr( ftp, "quit" ):
        try: ftp.quit()
        except: LOGGER.error.print_exc()
    return OK


def delete_to_ftp( filename ):
    OK = False
    ftp = None
    try:
        o = url_parse( os.path.dirname( filename ) + "/" )
        if DEBUG:
            print o

        if REMOTES.isOff( o.hostname ):
            return OK

        ftp = ftplib.FTP( o.hostname )
        ftp.login( o.username, o.password )

        ftp.cwd( o.path )
        if DEBUG:
            ftp.retrlines( 'LIST' ) # list directory contents
            print "-"*100
        ftp.delete( os.path.basename( filename ) )
        if DEBUG:
            ftp.retrlines( 'LIST' ) # list directory contents
            print "-"*100
        OK = True
    except:
        OK = False
        LOGGER.error.print_exc()
    if hasattr( ftp, "quit" ):
        try: ftp.quit()
        except: LOGGER.error.print_exc()
    return OK

if __name__ == '__main__':
    print REMOTES
    src = "remote_utils.py"
    dst = 'ftp://xbox:xbox@192.168.0.2:21/F/Medias/Series TV/Cosmos 1999/'
    print copy_to_ftp( src, dst )
    print delete_to_ftp( dst + os.path.basename( src ) )
    print REMOTES
