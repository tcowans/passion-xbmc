
#Modules general
import sys
from urllib import unquote_plus
from traceback import print_exc

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
    def __init__( self ):
        self._parse_argv()
        self._get_settings()

        self._add_directory_items()

    def _parse_argv( self ):
        # call _Info() with our formatted argv to create the self.args object
        exec "self.args = _Info(%s)" % ( unquote_plus( sys.argv[ 2 ][ 1 : ].replace( "&", ", " ) ), )

    def _get_settings( self ):
        self.settings = {}
        self.settings[ "trailers_scraper" ] = xbmcplugin.getSetting( "trailers_scraper" )
        self.settings[ "download_state" ] = int( xbmcplugin.getSetting( "download_state" ) )
        #self.settings[ "download_path" ] = xbmc.translatePath( xbmcplugin.getSetting( "download_path" ) )
        self.settings[ "download_path" ] = xbmcplugin.getSetting( "download_path" )

    def _add_directory_items( self ):
        OK = True
        try:
            exec "from scrapers.trailers.%s import scraper" % self.settings[ "trailers_scraper" ]
            for ID, tbn, title in self.args.trailers:
                trailer = scraper.get_video_url( ID )
                if trailer:
                    title = ( "%s (%s)" % ( title, _( 20410 ) ) ).replace( "\\'", "'" )
                    DIALOG_PROGRESS.update( -1, _( 1040 ), title )
                    listitem = xbmcgui.ListItem( title, thumbnailImage=tbn )
                    infolabels = { "title": title, "plot": _( 20410 ) }
                    listitem.setInfo( type="Video", infoLabels=infolabels )
                    OK = xbmcplugin.addDirectoryItem( handle=int( sys.argv[ 1 ] ), url=trailer, listitem=listitem, isFolder=False, totalItems=len( self.args.trailers ) )
                    if ( not OK ): raise
            xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category="[B]%s[/B]" % _( 30200 ) )
        except:
            print_exc()
            OK = False
        self._set_Content( OK )

    def _set_Content( self, OK ):
        if ( OK ):
            content = ( "files", "movies", "tvshows", "episodes", )[ 1 ]
            xbmcplugin.setContent( handle=int( sys.argv[ 1 ] ), content=content )
        self._add_sort_methods( OK )

    def _add_sort_methods( self, OK ):
        if ( OK ):
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_LABEL )
        self._end_of_directory( OK )

    def _end_of_directory( self, OK ):
        xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=OK )
