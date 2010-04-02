
#Modules general
import os
import sys
import stat
import exceptions
from traceback import print_exc

#Modules XBMC
import xbmc
import xbmcgui


DIALOG_PROGRESS = xbmcgui.DialogProgress()


def dialog_progress_update( pct, strLine1="", strLine2="", strLine3="" ):
    try:
        DIALOG_PROGRESS.update( pct, strLine1, strLine2, strLine3 )
    except:
        sys.stdout.write ( "\n[%s] %.2f%%" % ( ( int( round( pct/2 ) )*"#" ).ljust( 50 ), pct, ) )
        sys.stdout.flush()


def dialog_report_copy( blocknum, blocksize, totalsize, srcname, dstname ):
    percent = ( ( blocknum * blocksize ) * 100.0 / totalsize )
    dialog_progress_update( int( percent ), "%.1f%% Copied..." % ( percent, ), srcname, dstname )


def getXbmcIsMappedTo():
    import re
    ismapped = None
    try:
        xbmc_log = file( xbmc.translatePath( "special://home/xbmc.log" ), "r" ).read()
        ismapped = re.compile( "NOTICE: The executable running is: (.*)", re.IGNORECASE ).findall( xbmc_log )
        if not ismapped: ismapped = re.compile( "NOTICE: Q is mapped to: (.*)", re.IGNORECASE ).findall( xbmc_log )
        if ismapped:
            ismapped = ismapped[ 0 ]
            if not ismapped.endswith( ".xbe", ( len( ismapped )-4 ), len( ismapped ) ):
                ismapped = os.path.join( ismapped, "default.xbe" )
            if not os.path.isfile( ismapped ): ismapped = None
    except:
        print_exc()#LOG( LOG_ERROR, "utilities::getXbmcIsMappedTo [%s]", sys.exc_info()[ 1 ] )
    del re
    if not ismapped: xbmc.translatePath( "special://home/default.xbe" )
    return ismapped
GET_XBMC_IS_MAPPED_TO = getXbmcIsMappedTo()



class Error( exceptions.EnvironmentError ): pass


class ContentTooShortError( IOError ):
    # exception raised when copied size does not match content-length
    def __init__( self, message, content ):
        IOError.__init__( self, message )
        self.content = content


class Copy:
    """ Copy data and mode bits ( "cp src dst" ). The destination may be a directory. """
    def __init__( self, *args, **kwargs ):
        self.success = None
        self.src = args[ 0 ]
        self.dst = args[ 1 ]

        if not os.path.exists( self.src ):
            #LOG( LOG_ERROR, "Copy::__init__ The source '%s' not exists!", self.src )
            raise Error, "The source '%s' not exists!" % ( self.src, )

        if os.path.isdir( self.dst ):
            self.dst = os.path.join( self.dst, os.path.basename( self.src ) )

        if self._samefile( self.src, self.dst ):
            #LOG( LOG_ERROR, "Copy::__init__._samefile '%s' and '%s' are the same file.", self.src, self.dst )
            raise Error, "'%s' and '%s' are the same file." % ( self.src, self.dst )

        self.result = self.dst, os.stat( self.src )
        self.src_size = os.path.getsize( self.src )
        self.read_size = 0
        self.blocknum = 0

        self.length = self._length( kwargs.get( "length" ) )
        self.report_copy = kwargs.get( "report_copy" )

        self.success = self.copy_file()
        self.copy_mode()

    def _length( self, length ):
        if ( not isinstance( length, int ) ) or ( length < 2048 ) or ( length > 16384 ):
            if   self.src_size < 1048576:  length = 2*1024
            elif self.src_size < 5242880:  length = 4*1024
            elif self.src_size < 10485760: length = 8*1024
            elif self.src_size > 10485760: length = 16*1024
        #print length
        return int( length )

    def _samefile( self, src, dst ):
        # Macintosh, Unix.
        if hasattr( os.path, "samefile" ):
            try: return os.path.samefile( src, dst )
            except OSError: return False
        # All other platforms: check for same pathname.
        return ( os.path.normcase( os.path.abspath( src ) ) == os.path.normcase( os.path.abspath( dst ) ) )

    def copy_mode( self ):
        """ Copy mode bits from src to dst """
        if hasattr( os, "chmod" ):
            st = os.stat( self.src )
            mode = stat.S_IMODE( st.st_mode )
            os.chmod( self.dst, mode )

    def copy_file( self ):
        """ Copy data from src to dst """
        fsrc = None
        fdst = None
        try:
            fsrc = open( self.src, "rb" )
            fdst = open( self.dst, "wb" )
            """copy data from file-like object fsrc to file-like object fdst"""
            if self.report_copy:
                self.report_copy( self.blocknum, self.length, self.src_size, self.src, self.dst )
            while 1:
                buf = fsrc.read( self.length )
                if not buf: break
                self.read_size += len( buf )
                fdst.write( buf )
                self.blocknum += 1
                if self.report_copy:
                    self.report_copy( self.blocknum, self.length, self.src_size, self.src, self.dst )
        finally:
            if fdst: fdst.close()
            if fsrc: fsrc.close()
        # raise exception if actual size does not match
        if ( self.src_size >= 0 and self.read_size < self.src_size ):
            #LOG( LOG_ERROR, "Copy::copy_file copying incomplete: got only %i out of %i bytes", self.read_size, self.src_size )
            raise ContentTooShortError( "copying incomplete: got only %i out "
                                       "of %i bytes" % ( self.read_size, self.src_size ), self.result )
        else: return True



if __name__ == "__main__":
    def report_percent( blocknum, blocksize, totalsize, srcname, dstname ):
        percent = ( ( blocknum * blocksize ) * 100.0 / totalsize )
        dialog_progress_update( int( percent ), "%.1f%% Copied..." % ( percent, ), srcname, dstname )
        return percent

    def report_copy( blocknum, blocksize, totalsize, srcname, dstname ):
        # Report during remote transfers
        percent = int( report_percent( blocknum, blocksize, totalsize, srcname, dstname ) )
        #print "\nBlock number: %d, Block size: %d, Total size: %d, Percent: %.2f%%" % (
        #    blocknum, blocksize, totalsize, percent )

    def test_copy():
        DIALOG_PROGRESS.create('Test Copy With Progress Bar', "Copy...", "", "" )
        try:
            success = Copy( "C:\Documents and Settings\[OOPS!]\Bureau\Downloaded\XBMC_prog_xbox\XBMC-9.04.1-FIXED-BABYLON-T3CH.RAR", xbmc.translatePath("special://temp/xbmc.rar"), report_copy=report_copy ).success
        except ( IOError, Error ), msg:
            print msg
            success = None
        except:
            print "Unexpected error:", sys.exc_info()[ 0 ]
            print "Error message:", sys.exc_info()[ 1 ]
            #print "Traceback:", sys.exc_info()[ 2 ]
            success = None
        DIALOG_PROGRESS.close()
        print "copied on destination?", success

    import time
    #import profile, pstats
    #t1 = time.ctime()
    test_copy()
    #report_file = xbmc.translatePath(  'Z:\\testcopy.profile.log' )
    #profile.run( 'test_copy()', report_file )
    #pstats.Stats( report_file ).sort_stats( 'time' ).print_stats()
    #print t1
    #print time.ctime()
