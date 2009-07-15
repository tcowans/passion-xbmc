
#Modules general
import os
import re
import sys
import time
import urllib
from traceback import print_exc
from urllib import quote_plus, unquote_plus

#modules XBMC
import xbmc
import xbmcgui
import xbmcplugin

#modules custom
from utilities import *


_ = xbmc.getLocalizedString


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
            self._end_of_directory( False )
            heading, line1, line_error = _( 30000 ), _( 30006 ), _( 30007 )

            destination = os.path.dirname( self.args.path ) or os.path.dirname( self._nfo_associated_with() )
            if not destination:
                xbmcgui.Dialog().ok( _( 30000 ), _( 30041 ) )
                return

            from FileCopy import FileCopy
            DIALOG_PROGRESS.create( heading,  _( 1040 ), os.path.basename( self.args.path ),  )

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
            #if ( "<li>ok" in OK.lower() ):
            #    xbmcgui.Dialog().ok( heading, line1, "Dir: " + reduced_path( os.path.dirname( nfo_dest ) ), "File: " + os.path.basename( nfo_dest ) )
            #    #xbmc.executebuiltin( "XBMC.updatelibrary(video)" )
            #else: 
            #    xbmcgui.Dialog().ok( heading, line_error )
        except:
            print_exc()

    def _nfo_associated_with( self ):
        vpath = get_browse_dialog( heading=_( 30040 ), mask=self.VIDEO_EXT )
        self.args.path = vpath
        return vpath

    def _end_of_directory( self, OK ):
        xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=OK )
