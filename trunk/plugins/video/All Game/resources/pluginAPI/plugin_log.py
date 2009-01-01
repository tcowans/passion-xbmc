
import os
import sys
import time
import linecache
from re import findall

import xbmc


DEBUG_MODE = 0

try: __plugin__ = sys.modules[ "__main__" ].__plugin__
except: __plugin__ = "All Game"
DIRECTORY_DATA = xbmc.translatePath( os.path.join( "T:\\plugin_data", "video", __plugin__ ) )
if not os.path.isdir( DIRECTORY_DATA ): os.makedirs( DIRECTORY_DATA )

try: __svn_revision__ = sys.modules[ "__main__" ].__svn_revision__
except: __svn_revision__ = 0
if not __svn_revision__: __svn_revision__ = "0"
try: __version__ = "%s.%s" % ( sys.modules[ "__main__" ].__version__, __svn_revision__ )
except: __version__ = "1.0.0.%s" % ( __svn_revision__, )

CURRENT_DATE = time.strftime( "%d-%m-%Y" )
try: __date__ = sys.modules[ "__main__" ].__date__
except: __date__ = CURRENT_DATE

try: BOOSTER = sys.modules[ "__main__" ].BOOSTER
except: BOOSTER = None

LOG_PLUGIN = os.path.join( DIRECTORY_DATA, "%s.log" % ( __plugin__, ) )
LOG_OLD = os.path.join( DIRECTORY_DATA, "%s.old.log" % ( __plugin__, ) )

SEPARATOR = str( "-" * 85 )

# LOG STATUS CODES
LOG_ERROR, LOG_INFO, LOG_NOTICE, LOG_DEBUG, LOG_WARNING = range( 1, 6 )

#REGEXP FOR FUNCTION, e.g.: eval( LOG_SELF_FUNCTION )
LOG_SELF_FUNCTION = 'LOG( LOG_INFO, "%s::%s::%s", self.__module__, self.__class__.__name__, sys._getframe( 1 ).f_code.co_name )' #self.__module__.split( "." )[ -1 ]
LOG_FUNCTION = 'LOG( LOG_INFO, "%s::%s", globals()[ "__name__" ], sys._getframe( 1 ).f_code.co_name )'


def LOG( status, format, *args ):
    try:
        dwAvailPhys = str( long( xbmc.getFreeMem() * 1024.0 * 1024.0 ) )
    except:
        dwAvailPhys = "?"
    status = ( "ERROR", "INFO", "NOTICE", "DEBUG", "WARNING", )[ status - 1 ]
    _pre_line_ = "%s M: %s %s: " % ( time.strftime( "%X" ), dwAvailPhys, status.rjust( 7 ), )
    _write_line_ = "%s\n" % ( format % args, )
    file( LOG_PLUGIN, "a" ).write( _pre_line_ + _write_line_ )
    if ( DEBUG_MODE >= status ):
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
    if os.path.isfile( LOG_PLUGIN ):
        # XBOX PLATFORM
        try: old_uptime = int( findall( "System Uptime is[:] (\d{1,10})", file( LOG_PLUGIN, "r" ).read() )[ 0 ] )
        except: EXC_INFO( LOG_ERROR, sys.exc_info() )
        # OTHER PLATFORM
        try: same_date = CURRENT_DATE == findall( "- Current Date is[:] (\d{1,2}-\d{1,2}-\d{1,4})", file( LOG_PLUGIN, "r" ).read() )[ 0 ]
        except: EXC_INFO( LOG_ERROR, sys.exc_info() )

    create = ( cur_uptime < ( old_uptime + 1 ) )#<= old_uptime )
    if not same_date: create = True

    return str( cur_uptime ), create


def create_log_file():
    # create if uptime in log is less of current uptime of xbmc
    uptime, create = get_system_uptime()
    #print uptime, create
    if create or not os.path.isfile( LOG_PLUGIN ):
        if os.path.isfile( LOG_OLD ): os.unlink( LOG_OLD )
        if os.path.isfile( LOG_PLUGIN ): os.rename( LOG_PLUGIN, LOG_OLD )
        LOG( LOG_NOTICE, SEPARATOR )
        LOG( LOG_NOTICE, "Starting %s (version: %s).  Built on %s", __plugin__, __version__, __date__ )
        platform = os.environ.get( "OS", "" ).lower().replace( "xbox", "XBox" ).replace( "win32", "Windows" ).replace( "linux", "GNU/Linux" ).replace( "osx", "Mac OS X" )
        if not platform: platform = "Unknown"
        LOG( LOG_NOTICE, "XBMC, Platform: %s.  Built on %s", platform, xbmc.getInfoLabel( "System.BuildDate" ) )
        LOG( LOG_NOTICE, "Log File is located: %s", LOG_PLUGIN )
        LOG( LOG_NOTICE, SEPARATOR )
        LOG( LOG_NOTICE, "Checking the Date!" )
        LOG( LOG_INFO, "- Current Date is: %s", CURRENT_DATE )
        LOG( LOG_NOTICE, "Checking the System Uptime!" )
        LOG( LOG_INFO, "- System Uptime is: %s", uptime )
        
        #booster info
        if BOOSTER: LOG( LOG_NOTICE, "psyco: Plugin use booster" )

        #extra infos
        try:
            from urllib import unquote
            from xbmcplugin import getSetting
            games_path = unquote( getSetting( "game_path_1" ) ).replace( "multipath://", "" ).rstrip( "/" ).split( "/" )
            games_path += unquote( getSetting( "game_path_2" ) ).replace( "multipath://", "" ).rstrip( "/" ).split( "/" )
            games_path += unquote( getSetting( "game_path_3" ) ).replace( "multipath://", "" ).rstrip( "/" ).split( "/" )
            games_path = " , ".join( games_path )
            games_dir = "stack://%s" % ( games_path, )
            for folder in games_dir.replace( "stack://", "" ).split( " , " ):
                if not folder: continue
                if os.path.isdir( folder ): LOG( LOG_INFO, "Game Path is located: %s", folder )
                else: LOG( LOG_WARNING, "Game Path not exists: %s", folder )
        except:
            EXC_INFO( LOG_ERROR, sys.exc_info() )

# ON IMPORT CREATE OR RECREATE LOG FILE
create_log_file()
