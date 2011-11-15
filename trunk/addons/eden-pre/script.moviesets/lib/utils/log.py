
# Modules general
import os
import sys
import linecache
from traceback import print_exc

# Modules XBMC
try: import xbmc
except: xbmc = None

IsNotPython24 = ( sys.version >= "2.5" )
LEVELS = [ "debug", "info", "notice", "warning", "error", "severe", "fatal", "none" ]


def xbmc_log( level, format, *args ):
    try:
        if not args: s = format
        else: s = format % args
        line = "[MovieSets] %s" % s
        level = LEVELS.index( level )
        if not xbmc:
            level = LEVELS[ level ]
            print "%s: %s" % ( level, line )
        else:
            xbmc.log( line.strip( "\r\n" ), level )
    except:
        print "xbmc_log( %r, %r, %r )" % ( level, format, args )
        print_exc()


def sys_exc_info( level, infos, main=None ):
    try:
        filename = infos[ 2 ].tb_frame.f_code.co_filename
        write_line = "%s" % ( os.path.basename( os.path.splitext( filename )[ 0 ] ), )

        if main:
            write_line += "::%s" % ( main[ 0 ].__class__.__name__, )

        lineno = infos[ 2 ].tb_lineno
        write_line += "::%s (%d)" % ( infos[ 2 ].tb_frame.f_code.co_name, lineno, )

        next = infos[ 2 ].tb_next
        if next is not None:
            write_line += " in %s" % ( next.tb_frame.f_code.co_name, )

        linecache.checkcache( filename )
        if IsNotPython24:
            strline = linecache.getline( filename, lineno, infos[ 2 ].tb_frame.f_globals )
        else:
            strline = linecache.getline( filename, lineno )
        if strline:
            write_line += ", %s" % ( repr( strline.strip() ), )

        write_line += " - %s" % ( infos[ 1 ], )
        xbmc_log( level, write_line )
    except:
        print_exc()


class execNamespace:
    def __init__( self, level, api ):
        self.__handler_cache = {}
        self.level = level
        self.api = api

    def __getattr__( self, method ):
        if method in self.__handler_cache:
            return self.__handler_cache[ method ]

        def handler( *args, **kwargs ):
            if method == "exc_info":
                sys_exc_info( self.level, args[ 0 ], args[ 1:2 ] )
            elif method == "LOG":
                xbmc_log( self.level, args[ 0 ], *args[ 1: ] )

        handler.method = method
        self.__handler_cache[ method ] = handler
        return handler


class logAPI:
    def __init__( self ):
        self.__namespace = None
        self.__namespace = execNamespace
        self.__namespace_cache = {}

    def __getattr__( self, namespace ):
        if namespace in self.__namespace_cache:
            return self.__namespace_cache[ namespace ]

        self__namespace = self.__namespace #to prevent recursion
        nsobj = self__namespace( namespace, self )

        self.__namespace_cache[ namespace ] = nsobj
        return nsobj


def testing():
    log = logAPI()
    log.info.LOG( "testing" )
    try: oops
    except:
        log.error.exc_info( sys.exc_info() )


if ( __name__ == "__main__" ):
    testing()
