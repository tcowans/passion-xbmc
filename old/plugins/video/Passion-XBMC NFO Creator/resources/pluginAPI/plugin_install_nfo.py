
#Modules general
import os
import sys
from traceback import print_exc
from urllib import unquote_plus

#modules XBMC
import xbmc
import xbmcgui
import xbmcplugin

#modules custom
from utilities import *


_ = xbmc.getLocalizedString

DIALOG_PROGRESS = xbmcgui.DialogProgress()


class _Info:
    def __init__( self, *args, **kwargs ):
        self.__dict__.update( kwargs )


class Main:
    # add all video extensions wanted in lowercase
    VIDEO_EXT = xbmc.getSupportedMedia( "video" )

    def __init__( self ):
        self._parse_argv()
        self._install_nfo()

    def _parse_argv( self ):
        # call _Info() with our formatted argv to create the self.args object
        exec "self.args = _Info(%s)" % ( sys.argv[ 2 ][ 1 : ].replace( "&", ", " ), )
        self.args.path = unquote_plus( self.args.path )
        self.args.nfo_file = unquote_plus( self.args.nfo_file )

    def _install_nfo( self ):
        print
        print "plugin_install_nfo::_install_nfo"
        try:
            destination = os.path.dirname( self.args.path ) or os.path.dirname( self._nfo_associated_with() )
            if not destination:
                xbmcgui.Dialog().ok( _( 30000 ), _( 30041 ) )
                return

            #get labels before end_of_directory
            ask1, ask2 = _( 30003 ), _( 30004 )
            ask3 = "%s: %s" % ( _( 30005 ), unicode( os.path.basename( self.args.path ), "utf-8" ) )
            ask4 = "%s: %s" % ( _( 30100 ), os.path.splitext( unicode( os.path.basename( self.args.path ), "utf-8" ) )[ 0 ] + ".nfo" )

            heading, line1 = _( 30000 ), _( 1040 )
            self._end_of_directory( False )
            
            if not xbmcgui.Dialog().yesno( ask1, ask2, ask3, ask4 ): return

            DIALOG_PROGRESS.create( heading, line1, os.path.basename( self.args.path ),  )

            from FileCopy import FileCopy
            results = FileCopy( nfo_source=self.args.nfo_file, movie_path=self.args.path,
                thumbnail=xbmc.getInfoImage( "ListItem.Thumb" ), fanart=xbmc.getInfoImage( "Fanart.Image" ),
                report_copy=DIALOG_PROGRESS )

            nfo = results.nfo_OK or "Not created!"
            tbn = results.tbn_OK or "Not created!"
            fanart = results.fanart_OK or "Not created!"
            print results
            print self.args.path
            print "NFO: " + nfo
            print "TBN: " + tbn
            print "Fanart: " + fanart

            DIALOG_PROGRESS.close()
            xbmcgui.Dialog().ok( reduced_path( os.path.dirname( self.args.path ) ),
                "NFO: " + os.path.basename( nfo ),
                "TBN: " + os.path.basename( tbn ),
                "Fanart: " + os.path.basename( fanart )
                )
        except:
            print_exc()
        DIALOG_PROGRESS.close()

    def _nfo_associated_with( self ):
        vpath = get_browse_dialog( heading=_( 30040 ), mask=self.VIDEO_EXT )
        self.args.path = vpath
        return vpath

    def _end_of_directory( self, OK ):
        xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=OK )
