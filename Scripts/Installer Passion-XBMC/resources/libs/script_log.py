
import os
import sys
import time
import thread
import linecache
from re import findall

import xbmc

try:
    from utilities import Settings
except:
    pass


#for use DEBUG_MODE change value [ 0 ] to [ 1 ], and all LOG(...) will be written in the xbmc.log
DEBUG_MODE = ( None, "DEBUGS", )[ 0 ]


try: __script__ = sys.modules[ "__main__" ].__script__
except: __script__ = "Installer Passion-XBMC"
DIRECTORY_DATA = os.path.join( xbmc.translatePath( "T:\\script_data" ), __script__ )
if not os.path.isdir( DIRECTORY_DATA ): os.makedirs( DIRECTORY_DATA )

try: __svn_revision__ = sys.modules[ "__main__" ].__svn_revision__
except: __svn_revision__ = 0
if not __svn_revision__: __svn_revision__ = "0"
try: __version__ = "%s.%s" % ( sys.modules[ "__main__" ].__version__, __svn_revision__ )
except: __version__ = "1.0.0.%s" % ( __svn_revision__, )

CURRENT_DATE = time.strftime( "%d-%m-%Y" )
try: __date__ = sys.modules[ "__main__" ].__date__
except: __date__ = CURRENT_DATE

LOG_SCRIPT = os.path.join( DIRECTORY_DATA, "%s.log" % ( __script__, ) )
LOG_OLD = os.path.join( DIRECTORY_DATA, "%s.old.log" % ( __script__, ) )

SEPARATOR = str( "-" * 85 )

# LOG STATUS CODES
LOG_DEBUG, LOG_INFO, LOG_NOTICE, LOG_WARNING, LOG_ERROR, LOG_FATAL = range( 1, 7 )

#REGEXP FOR FUNCTION, e.g.: eval( LOG_SELF_FUNCTION )
LOG_SELF_FUNCTION = 'logger.LOG( logger.LOG_DEBUG, "%s::%s::%s", self.__module__, self.__class__.__name__, sys._getframe( 1 ).f_code.co_name )' #self.__module__.split( "." )[ -1 ]
LOG_FUNCTION = 'logger.LOG( logger.LOG_DEBUG, "%s::%s", globals()[ "__name__" ], sys._getframe( 1 ).f_code.co_name )'


def LOG( status, format, *args ):
    if ( status == 1 ):
        # utiliser avec le setting script_debug.
        # si le setting est false tous les "LOG( LOG_DEBUG, ... )" ne seront pas ecrie
        try: OK = Settings().get_settings().get( "script_debug", False )
        except: OK = False
        if not OK: return
    try: dwAvailPhys = str( long( xbmc.getFreeMem() * 1024.0 * 1024.0 ) )
    except: dwAvailPhys = "?"
    status = ( "DEBUG", "INFO", "NOTICE", "WARNING", "ERROR", "FATAL ERROR", )[ status - 1 ]
    _pre_line_ = "%s T:%s M:%s %s: " % ( time.strftime( "%X" ), str( thread.get_ident() ).rjust( 4 ), dwAvailPhys, status.rjust( 7 ), )
    _write_line_ = "%s\n" % ( format % args, )
    WRITABLE_LOG.write( _pre_line_ + _write_line_ )
    if ( DEBUG_MODE == "DEBUGS" ):
        xbmc.output( _write_line_.strip( "\n" ) )


def EXC_INFO( status, infos, _self_=None ):
    _filename_ = infos[ 2 ].tb_frame.f_code.co_filename
    _write_line_ = "%s" % ( os.path.basename( os.path.splitext( _filename_ )[ 0 ] ), )

    if _self_: _write_line_ += "::%s" % ( _self_.__class__.__name__, )

    _func_ = infos[ 2 ].tb_frame.f_code.co_name
    _lineno_ = infos[ 2 ].tb_lineno
    _write_line_ += "::%s (%d)" % ( _func_, _lineno_, )

    _next_ = infos[ 2 ].tb_next
    if _next_ is not None: _write_line_ += " in %s" % ( _next_.tb_frame.f_code.co_name, )

    linecache.checkcache( _filename_ )
    try: _strline_ = linecache.getline( _filename_, _lineno_, infos[ 2 ].tb_frame.f_globals )# python 2.5
    except: _strline_ = linecache.getline( _filename_, _lineno_ )
    if _strline_: _write_line_ += ", %s" % ( repr( _strline_.strip() ), )

    _write_line_ += " - %s" % ( infos[ 1 ], )
    LOG( status, "%s", _write_line_ )


def get_system_uptime():
    uptime = findall( "(\d{1,4})", xbmc.getInfoLabel( "system.uptime" ) )
    #print uptime, xbmc.getInfoLabel( "system.uptime" )
    if len( uptime ) == 1:
        cur_uptime = int( uptime[ 0 ] )
    elif len( uptime ) == 2:
        cur_uptime = ( int( uptime[ 0 ] ) * 60 ) + int( uptime[ 1 ] )
    elif len( uptime ) == 3:
        cur_uptime = ( int( uptime[ 0 ] ) * 60 * 60 ) + ( int( uptime[ 1 ] ) * 60 ) + int( uptime[ 2 ] )
    else:
        cur_uptime = 0

    old_uptime = 0
    same_date = True
    if os.path.isfile( LOG_SCRIPT ):
        # XBOX PLATFORM
        try: old_uptime = int( findall( "System Uptime is[:] (\d{1,10})", file( LOG_SCRIPT, "r" ).read() )[ 0 ] )
        except: pass #EXC_INFO( LOG_ERROR, sys.exc_info() )
        # OTHER PLATFORM
        try: same_date = CURRENT_DATE == findall( "- Current Date is[:] (\d{1,2}-\d{1,2}-\d{1,4})", file( LOG_SCRIPT, "r" ).read() )[ 0 ]
        except: pass #EXC_INFO( LOG_ERROR, sys.exc_info() )

    create = ( cur_uptime < ( old_uptime + 1 ) )#<= old_uptime )
    if not same_date: create = True

    return str( cur_uptime ), create


def create_log_file():
    # create if uptime in log is less of current uptime of xbmc for xbox or not same date for other platform
    uptime, create = get_system_uptime()
    #print uptime, create
    globals()[ "WRITABLE_LOG" ] = None
    if create or not os.path.isfile( LOG_SCRIPT ):
        if os.path.isfile( LOG_OLD ): os.unlink( LOG_OLD )
        if os.path.isfile( LOG_SCRIPT ): os.rename( LOG_SCRIPT, LOG_OLD )
        globals()[ "WRITABLE_LOG" ] = open( LOG_SCRIPT, "w+" )
        LOG( LOG_NOTICE, SEPARATOR )
        LOG( LOG_NOTICE, "Starting %s (version: %s).  Built on %s", __script__, __version__, __date__ )
        platform = ( os.environ.get( "OS", "" ).lower() or "Unknown" )
        platform = platform.replace( "linux", "GNU/Linux" ).replace( "osx", "Mac OS X" ).replace( "win32", "Windows" ).replace( "xbox", "XBox" )
        LOG( LOG_NOTICE, "XBMC, Platform: %s.  Built on %s", platform, xbmc.getInfoLabel( "System.BuildDate" ) )
        LOG( LOG_NOTICE, "Q is mapped to: %s", xbmc.translatePath( ( "U:\\", "Q:\\", )[ ( platform == "XBox" ) ] ) )
        LOG( LOG_NOTICE, "The executable script running is: %s", os.path.join( os.getcwd().rstrip( ";" ), sys.modules[ "__main__" ].__file__ ) )
        LOG( LOG_NOTICE, "Log File is located: %s", LOG_SCRIPT )
        LOG( LOG_NOTICE, SEPARATOR )
        LOG( LOG_NOTICE, "Checking the Date!" )
        LOG( LOG_INFO, "- Current Date is: %s", CURRENT_DATE )
        LOG( LOG_NOTICE, "Checking the System Uptime!" )
        LOG( LOG_INFO, "- System Uptime is: %s", uptime )

        try:
            from utilities import getUserSkin
            current_skin, force_fallback = getUserSkin()
            LOG( LOG_NOTICE, "load default skin:[%s]", current_skin )
            LOG( LOG_NOTICE, "default skin use force fallback: %s", repr( force_fallback ) )
            del getUserSkin
        except:
            pass

    if WRITABLE_LOG is None:
        old_log = ""
        if os.path.isfile( LOG_SCRIPT ):
            f = open( LOG_SCRIPT, "r" )
            old_log = f.read()
            f.close()
        globals()[ "WRITABLE_LOG" ] = open( LOG_SCRIPT, "w+" )
        if old_log != "":
            WRITABLE_LOG.write( old_log )
            LOG( LOG_NOTICE, SEPARATOR )
            LOG( LOG_NOTICE, SEPARATOR )
            LOG( LOG_NOTICE, "Checking the Date!" )
            LOG( LOG_INFO, "- Current Date is: %s", CURRENT_DATE )


class LogErr:
    def write( self, data ):
        error_line = "%s" % ( data.strip( "\r\n" ), )
        if error_line.strip( " " ) != "":
            print error_line
            self._log_sys_stderr( error_line )

    def _log_sys_stderr( self, error_line ):
        LOG( LOG_FATAL, error_line )


try:
    sys.stderr = LogErr()
except:
    pass


# ON IMPORT CREATE OR RECREATE LOG FILE
create_log_file()
