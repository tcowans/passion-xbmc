
#Modules general
import os
import re
import sys
import time
from traceback import print_exc
from urllib import quote_plus, unquote_plus

#modules XBMC
import xbmc
import xbmcgui
import xbmcplugin

#modules custom
import nfo_utils
from utilities import *

from file_item import Thumbnails
thumbnails = Thumbnails()


_ = xbmc.getLocalizedString

DIALOG_PROGRESS = xbmcgui.DialogProgress()


def is_svn_version():
    #Changeset 21882
    #changed: sanify the thumb handling in scrapers and nfo files.
    #just add several <thumb> tags instead of the <thumbs> sillyness we used before.
    #i have only updated tmdb, imdb and tvdb video scrapers + the music scrapers.
    ok = False
    try:
        xbmc_rev = int( xbmc.getInfoLabel( "System.BuildVersion" ).split( " " )[ 1 ].replace( "r", "" ) )
        ok = xbmc_rev >= 21882
    except:
        pass
    return ok


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
        exec "self.args = _Info(%s)" % ( sys.argv[ 2 ][ 1 : ].replace( "&", ", " ), )
        self.args.path = unquote_plus( self.args.path )
        self.args.show_id = unquote_plus( self.args.show_id )

    def _get_settings( self ):
        self.settings = {}
        self.settings[ "web_navigator" ] = xbmcplugin.getSetting( "web_navigator" )
        self.settings[ "scraper" ] = xbmcplugin.getSetting( "scraper" )
        self.settings[ "download_state" ] = int( xbmcplugin.getSetting( "download_state" ) )
        self.settings[ "passion_fanart" ] = ( xbmcplugin.getSetting( "passion_fanart" ) == "true" )
        self.settings[ "actors_thumbs" ] = ( xbmcplugin.getSetting( "actors_thumbs" ) == "true" )

    def _add_directory_items( self ):
        OK = True
        try:
            exec "from scrapers.%s import scraper" % self.settings[ "scraper" ]
            movie_data = scraper.Movie( self.args.show_id, is_svn_version() )
            self.nfo_file = movie_data.XML( SPECIAL_PLUGIN_CACHE, passion_fanart=self.settings[ "passion_fanart" ]  )
            #print self.nfo_file

            DIALOG_PROGRESS.update( -1, _( 1040 ), self.nfo_file )
            self.nfo = nfo_utils.InfosNFO()
            #self.nfo.isTVShow = True
            self.nfo.parse( self.nfo_file )
            if self.settings[ "actors_thumbs" ]:
                for actor in self.nfo.actor:
                    try:
                        if actor.get( "thumb" ) and actor.get( "name" ):
                            DIALOG_PROGRESS.update( -1, _( 20402 ), actor.get( "name" ) )
                            cached_actor = thumbnails.get_cached_actor_thumb( actor.get( "name" ) )
                            if not os.path.exists( cached_actor ):
                                xbmc.executehttpapi( "FileDownloadFromInternet(%s;%s)" % ( actor.get( "thumb" ), cached_actor, ) )
                                #print cached_actor
                                #print actor.get( "thumb" )
                                #print
                    except:
                        print_exc()

            DIALOG_PROGRESS.update( -1, _( 1040 ), self.nfo.get( "title" ) )

            tbn = ( self.nfo.get( "thumbs" ) or [ "" ] )[ 0 ]
            listitem = xbmcgui.ListItem( self.nfo.get( "title" ), iconImage=tbn, thumbnailImage=tbn )

            url = "%s?path=%s&nfo_file=%s" % ( sys.argv[ 0 ], repr( quote_plus(  self.args.path ) ), repr( self.nfo_file ), )

            c_items = [ ( _( 30012 ), "XBMC.RunPlugin(%s)" % ( url, ) ) ]
            c_items += [ ( _( 30009 ), "XBMC.Action(Info)", ) ]
            if self.settings[ "web_navigator" ] != "" and os.path.exists( self.settings[ "web_navigator" ] ):
                cmd = "System.Exec"
                uri = scraper.ALLOCINE_DOMAIN + scraper.MOVIE_URL % self.args.show_id
                command = '%s("%s" "%s")' % ( cmd, self.settings[ "web_navigator" ], uri, )
                # add the movie information item
                c_items += [ ( _( 30010 ), command, ) ]
            c_items += [ ( _( 654 ), "XBMC.ActivateWindow(scriptsdebuginfo)" ) ]
            # add items to listitem with replaceItems = True so only ours show
            listitem.addContextMenuItems( c_items, replaceItems=True )

            if len( self.nfo.get( "fanart" ) ) >= 1:
                fanart = get_nfo_thumbnail( self.nfo.get( "fanart" )[ 0 ] )
                listitem.setProperty( "Fanart_Image", fanart )
                xbmcplugin.setPluginFanart( handle=int( sys.argv[ 1 ] ), image=fanart )
            listitem.setInfo( type="Video", infoLabels=self.nfo.infoLabels )

            OK = xbmcplugin.addDirectoryItem( handle=int( sys.argv[ 1 ] ), url=url, listitem=listitem, isFolder=True )
            if ( not OK ): raise

            OK = self._add_trailers_item( movie_data )
            xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category="[B]NFO[/B]" )
        except:
            print_exc()
            OK = False
        self._set_content( OK )

    def _add_trailers_item( self, movie_data ):
        OK = True
        try:
            # add trailer bouton if exists
            if movie_data.has_videos():
                trailers = movie_data.get_mediaIDs()
                tbn = os.path.join( os.getcwd().rstrip( ";" ), "resources", "thumbnails", "movies_1.png" )
                listitem = xbmcgui.ListItem( _( 30200 ), iconImage=tbn, thumbnailImage=tbn )
                c_items = [ ( _( 654 ), "XBMC.ActivateWindow(scriptsdebuginfo)" ) ]
                # add items to listitem with replaceItems = True so only ours show
                listitem.addContextMenuItems( c_items )
                url = "%s?trailers=%s" % ( sys.argv[ 0 ], quote_plus( repr( trailers ) ), )
                OK = xbmcplugin.addDirectoryItem( handle=int( sys.argv[ 1 ] ), url=url, listitem=listitem, isFolder=True )
                if ( not OK ): raise
        except:
            print_exc()
            OK = False
        return OK

    def _set_content( self, OK ):
        if ( OK ):
            content = ( "files", "movies", "tvshows", "episodes", )[ 1 ]
            xbmcplugin.setContent( handle=int( sys.argv[ 1 ] ), content=content )
        self._add_sort_methods( OK )

    def _add_sort_methods( self, OK ):
        if ( OK ):
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_NONE )
        self._end_of_directory( OK )

    def _end_of_directory( self, OK ):
        xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=OK )
