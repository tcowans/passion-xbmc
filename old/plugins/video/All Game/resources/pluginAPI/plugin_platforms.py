
import os
import sys
import urllib
import xbmc
import xbmcgui
import xbmcplugin

from convert import translate_string, ENTITY_OR_CHARREF
from scrapers.platforms_scrapers import *
from etree_utilities import *
from plugin_log import *


_ = xbmc.getLocalizedString

DIALOG_PROGRESS = xbmcgui.DialogProgress()

PLATFORMS_DIR_PATH = sys.modules[ "__main__" ].PLATFORMS_DIR_PATH

THUMBNAILS_DIR_PATH = sys.modules[ "__main__" ].THUMBNAILS_DIR_PATH


class Main:
    ARGV_REGEXP = "%s?pluginAPI=Games&&games_url=%s&&platform=/%s"

    def __init__( self ):
        self._get_settings()
        self._set_plugin_fanart()
        self._add_directory_items()

    def _get_settings( self ):
        self.settings = {}
        self.settings[ "refresh_data" ] = xbmcplugin.getSetting( "refresh_data" ) == "true"
        self.settings[ "set_content" ] = int( xbmcplugin.getSetting( "set_content" ) )
        self.settings[ "xbmc_auto_thumbs" ] = xbmcplugin.getSetting( "xbmc_auto_thumbs" ) == "true"
        self.settings[ "no_games_thumb" ] = xbmcplugin.getSetting( "no_games_thumb" ) == "1"
        self.settings[ "custom_games_thumb" ] = xbmcplugin.getSetting( "custom_games_thumb" )
        self.settings[ "enable_fanart" ] = xbmcplugin.getSetting( "enable_fanart" ) == "true"
        self.settings[ "fanart_image" ] = xbmcplugin.getSetting( "fanart_image" )

    def _set_plugin_fanart( self ):
        try:
            # set our fanart from user setting
            if ( self.settings[ "enable_fanart" ] and self.settings[ "fanart_image" ] ):
                fanart_color1 = xbmcplugin.getSetting( "fanart_color1" )
                fanart_color2 = xbmcplugin.getSetting( "fanart_color2" )
                fanart_color3 = xbmcplugin.getSetting( "fanart_color3" )
                xbmcplugin.setPluginFanart( handle=int( sys.argv[ 1 ] ), image=self.settings[ "fanart_image" ], color1=fanart_color1, color2=fanart_color2, color3=fanart_color3 )
                xbmc.sleep( 10 )
        except:
            EXC_INFO( LOG_ERROR, sys.exc_info(), self )

    def _add_directory_items( self ):
        eval( LOG_SELF_FUNCTION )
        OK = True
        try:
            DIALOG_PROGRESS.update( -1, _( 1040 ), _( 30010 ) )
            listed = get_platforms_listed( PLATFORMS_URL )
            total_items = len( listed )
            for count, item in enumerate( listed ):
                item[ "platform" ] = ENTITY_OR_CHARREF( item[ "platform" ] ).entity_or_charref
                DIALOG_PROGRESS.update( -1, _( 1040 ), item[ "platform" ] )

                filename = os.path.join( PLATFORMS_DIR_PATH, "%s.xml" % ( item[ "ID" ], ) )

                try:
                    if self.settings[ "refresh_data" ] or not os.path.isfile( filename ):
                        if self.settings[ "refresh_data" ] and os.path.isfile( filename ):
                            l2 = _( 30009 )
                        else: l2 = _( 30010 )
                        try: dp_line2 = l2 + item[ "platform" ]#.decode( "utf-8" )
                        except: dp_line2 = l2 + translate_string( item[ "platform" ] )
                        DIALOG_PROGRESS.update( -1, _( 1040 ), dp_line2 )

                        urlsource = urljoin( PLATFORMS_URL, item[ "urlsource" ] )
                        tbn, description = get_platform_overview( urlsource )
                        tbn = ( "", urljoin( PLATFORMS_URL, tbn ) )[ tbn != "" ]
                        item.update( { "tbn": tbn, "description": description, "urlsource": urlsource } )
                        DIALOG_PROGRESS.update( -1, _( 1040 ), _( 30011 ) )
                        save_infos( filename, item.copy(), isgame=False )

                    platform_info = load_infos( filename )
                    title = platform_info.findtext( "platform" ).replace( "&amp;", "&" )
                    tbn = platform_info.findtext( "tbn" )
                    genre = platform_info.findtext( "style" )
                    plot = platform_info.findtext( "description" )
                    games_url = platform_info.findtext( "urlsource" )
                except:
                    EXC_INFO( LOG_ERROR, sys.exc_info(), self )
                    total_items -= 1
                    continue

                url = self.ARGV_REGEXP % ( sys.argv[ 0 ], games_url, title )
                tbn = self.get_thumbnail( tbn, url )
                listitem = xbmcgui.ListItem( title, thumbnailImage=tbn )
                listitem.setInfo( type="video", infoLabels={ "title": title, "genre": genre, "plot": plot } )
                OK = xbmcplugin.addDirectoryItem( handle=int( sys.argv[ 1 ] ), url=url, listitem=listitem, isFolder=True, totalItems=total_items )
                if ( not OK ): raise
        except:
            EXC_INFO( LOG_ERROR, sys.exc_info(), self )
            OK = False
        self._set_Content( OK )

    def get_thumbnail( self, online_tbn, xbmc_cached ):
        if online_tbn.endswith( "nogame_large.gif" ) and self.settings[ "no_games_thumb" ] and os.path.isfile( self.settings[ "custom_games_thumb" ] ):
            return self.settings[ "custom_games_thumb" ]

        cached_thumb = xbmc.getCacheThumbName( online_tbn ).replace( "tbn", online_tbn.rsplit( "." )[ -1 ] )
        cover_image = os.path.join( THUMBNAILS_DIR_PATH, cached_thumb[ 0 ], cached_thumb )
        if os.path.isfile( cover_image ): return cover_image

        xbmc_cached = xbmc.getCacheThumbName( xbmc_cached )
        xbmc_cached_thumb = xbmc.translatePath( os.path.join( "P:\\Thumbnails", "Video", xbmc_cached[ 0 ], xbmc_cached ) )
        if os.path.isfile( xbmc_cached_thumb ): return xbmc_cached_thumb

        if online_tbn and ( online_tbn.endswith( "nogame_large.gif" ) or not self.settings[ "xbmc_auto_thumbs" ] ):
            try:
                if not os.path.isdir( os.path.dirname( cover_image ) ):
                    os.makedirs( os.path.dirname( cover_image ) )
                fp, h = urllib.urlretrieve( online_tbn, cover_image )
                try:
                    if "text" in h[ "Content-Type" ]: os.unlink( cover_image )
                except: pass
            except:
                EXC_INFO( LOG_ERROR, sys.exc_info(), self )

        if not os.path.isfile( cover_image ):
            cover_image = online_tbn

        return cover_image

    def _set_Content( self, OK ):
        if ( OK ):
            content = ( "files", "movies", )[ self.settings[ "set_content" ] ]
            xbmcplugin.setContent( handle=int( sys.argv[ 1 ] ), content=content )
            try:
                # set our plugin category
                xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category=_( 30001 ) )
            except:
                EXC_INFO( LOG_ERROR, sys.exc_info(), self )
        self._add_sort_methods( OK )

    def _add_sort_methods( self, OK ):
        if ( OK ):
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_LABEL )
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_GENRE )
        self._end_of_directory( OK )

    def _end_of_directory( self, OK ):
        xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=OK )
