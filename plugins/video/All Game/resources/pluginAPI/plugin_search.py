
import os
import re
import sys
import xbmc
import xbmcgui
import xbmcplugin
from urllib import unquote, urlretrieve

from convert import translate_string, ENTITY_OR_CHARREF
from scrapers.search_scrapers import *
from scrapers.games_scrapers import *
from etree_utilities import *
from plugin_log import *


CWD = os.getcwd().rstrip( ";" )

_ = xbmc.getLocalizedString

DIALOG_PROGRESS = xbmcgui.DialogProgress()

PLUGIN_RUN_UNDER = sys.modules[ "__main__" ].PLUGIN_RUN_UNDER

GAMES_DIR_PATH = sys.modules[ "__main__" ].GAMES_DIR_PATH

THUMBNAILS_DIR_PATH = sys.modules[ "__main__" ].THUMBNAILS_DIR_PATH


def xbmc_date_format( strdate ):
    date, year = "", 0
    try:
        t = re.search( "(.*) (\d{1,2}), (\d{4})", strdate )
        try: month = [ "January", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december" ].index(  t.group( 1 ).lower() )
        except: month = [ "jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec" ].index(  t.group( 1 ).lower() )
        year = int( t.group( 3 ) )
        date = "%02d/%02d/%04d" % ( int( t.group( 2 ) ), ( month + 1 ), year )
    except:
        try: year = int( re.findall( "(\d{4})", strdate )[ 0 ] )
        except: pass

    return date, year


class Main:
    ARGV_REGEXP = "%s?pluginAPI=Game Info&&game_id=%s&&platform=%s&&game=/%s"

    def __init__( self ):
        self._get_args()
        self._get_settings()
        self._set_plugin_fanart()
        self._add_directory_items()

    def _get_args( self ):
        self.args = dict( [ arg.split( "=", 1 ) for arg in sys.argv[ 2 ][ 1: ].replace( "=/", "=" ).split( "&&" ) ] )

    def _get_settings( self ):
        self.settings = {}
        self.settings[ "refresh_data" ] = xbmcplugin.getSetting( "refresh_data" ) == "true"
        self.settings[ "set_content" ] = int( xbmcplugin.getSetting( "set_content" ) )
        self.settings[ "xbmc_auto_thumbs" ] = xbmcplugin.getSetting( "xbmc_auto_thumbs" ) == "true"
        self.settings[ "no_games_thumb" ] = int( xbmcplugin.getSetting( "no_games_thumb" ) )
        self.settings[ "custom_games_thumb" ] = xbmcplugin.getSetting( "custom_games_thumb" )
        self.settings[ "whole_words" ] = xbmcplugin.getSetting( "whole_words" ) == "true"
        self.settings[ "enable_fanart" ] = xbmcplugin.getSetting( "enable_fanart" ) == "true"
        self.settings[ "fanart_image" ] = xbmcplugin.getSetting( "fanart_image" )
        self._set_local_games()

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

    def _set_local_games( self ):
        games_path = unquote( xbmcplugin.getSetting( "game_path_1" ) ).replace( "multipath://", "" ).rstrip( "/" ).split( "/" )
        games_path += unquote( xbmcplugin.getSetting( "game_path_2" ) ).replace( "multipath://", "" ).rstrip( "/" ).split( "/" )
        games_path += unquote( xbmcplugin.getSetting( "game_path_3" ) ).replace( "multipath://", "" ).rstrip( "/" ).split( "/" )
        games_path = " , ".join( games_path )
        self.settings[ "games_dir" ] = "stack://%s" % ( games_path, )
        self.my_local_games = []
        try:
            for folder in self.settings[ "games_dir" ].replace( "stack://", "" ).split( " , " ):
                if os.path.isdir( folder ):
                    self.my_local_games += [ game.lower() for game in os.listdir( folder ) ]
            self.my_local_games = sorted( self.my_local_games )
        except:
            EXC_INFO( LOG_ERROR, sys.exc_info(), self )
        if not self.my_local_games:
            self.my_local_games = [ ":(" ]

    def is_on_hdd( self, title ):
        run_game = ""
        if PLUGIN_RUN_UNDER == "xbox":
            try:
                title = xbmc.makeLegalFilename( title.lower() ).replace( ":", "" )
                if self.settings[ "whole_words" ]:
                    folder = self.my_local_games[ self.my_local_games.index( title ) ]
                    for root in self.settings[ "games_dir" ].replace( "stack://", "" ).split( " , " ):
                        if os.path.isdir( root ):
                            rgame = os.path.join( root, folder, "default.xbe" )
                            if os.path.isfile( rgame ):
                                run_game = rgame
                                break
                elif not "[canceled]" in title:
                    ignore_tokens = "\\b(the|a|of|and|0|1|2|3|4|5|6|7|8|9|I|II|III)\\b"
                    title = " ".join( re.sub( ignore_tokens, "", title ).split() ).replace( " - ", " " )
                    for game in self.my_local_games:
                        folder = game
                        tgame = " ".join( re.sub( ignore_tokens, "", game ).split() ).replace( " - ", " " )
                        a = re.search( "\\b(%s)\\b" % tgame.replace( " ", "|" ).strip( "|" ), title )
                        b = re.search( "\\b(%s)\\b" % title.replace( " ", "|" ).strip( "|" ), tgame )
                        if not a or not b: continue
                        for root in self.settings[ "games_dir" ].replace( "stack://", "" ).split( " , " ):
                            if os.path.isdir( root ):
                                rgame = os.path.join( root, folder, "default.xbe" )
                                if os.path.isfile( rgame ):
                                    run_game = rgame
                                    return run_game
            except ( IndexError, ValueError, ):
                pass
            except:
                EXC_INFO( LOG_ERROR, sys.exc_info(), self )
        return run_game

    def _add_directory_items( self ):
        eval( LOG_SELF_FUNCTION )
        OK = True
        try:
            keyboard = xbmc.Keyboard( "", _( 30008 ) )
            keyboard.doModal()
            if not keyboard.isConfirmed(): return
            self.user_search = keyboard.getText()
            if not self.user_search: return
            DIALOG_PROGRESS.update( -1, _( 1040 ), self.user_search )
            games_listed = get_search_games_listed( SEARCH_URL % ( "|".join( self.user_search.split() ), ) )
            total_items = len( games_listed )

            for count, game in enumerate( games_listed ):
                game[ "title" ] = ENTITY_OR_CHARREF( game[ "title" ] ).entity_or_charref
                DIALOG_PROGRESS.update( -1, _( 1040 ), game[ "title" ] )
                game_on_hdd = self.is_on_hdd( game[ "title" ] )
                platform = translate_string( game[ "platform" ].replace( "/", "_" ) )

                platform_games_dir_path = os.path.join( GAMES_DIR_PATH, platform )
                if not os.path.isdir( platform_games_dir_path ): os.makedirs( platform_games_dir_path )
                filename = os.path.join( platform_games_dir_path, "%s.xml" % ( game[ "ID" ], ) )

                try:
                    if self.settings[ "refresh_data" ] or not os.path.isfile( filename ):
                        if self.settings[ "refresh_data" ] and os.path.isfile( filename ):
                            l2 = _( 30009 )
                        else: l2 = _( 30010 )
                        try: dp_line2 = l2 + game[ "title" ]#.decode( "utf-8" )
                        except: dp_line2 = l2 + translate_string( game[ "title" ] )
                        DIALOG_PROGRESS.update( -1, _( 1040 ), dp_line2 )

                        game_infos = get_game_overview( game[ "urlsource" ] )
                        game.update( game_infos )
                        other_infos = get_other_game_infos( game[ "buttons_listed" ], game[ "urlsource" ] )
                        game.update( other_infos )
                        if bool( game_on_hdd ) and self.settings[ "whole_words" ]:
                            game.update( { "game_on_hdd": game_on_hdd } )
                        DIALOG_PROGRESS.update( -1, _( 1040 ), _( 30012 ) )
                        save_infos( filename, game.copy() )

                    game_info = load_infos( filename )
                    title = game_info.findtext( "title" )
                    tbn = game_info.findtext( "tbn" )
                    genre = game_info.findtext( "genre" )
                    plot = game_info.findtext( "synopsis" )
                    games_id = game_info.findtext( "ID" )
                    year = game_info.findtext( "year" )
                    if year.isdigit(): year = int( year )
                    date = xbmc_date_format( game_info.findtext( "release_date" ) )[ 0 ]
                    game_on_hdd = game_info.findtext( "game_on_hdd" ) or game_on_hdd or ""
                    rate = game_info.findtext( "amg_rating" ) or ""
                    if not rate.isdigit(): rating = "0.0"
                    else: rating = ( "0.5", "1.0", "1.5" , "2.0", "2.5", "3.0", "3.5" , "4.0", "4.5", "5.0", )[ int( rate ) ]
                except:
                    EXC_INFO( LOG_ERROR, sys.exc_info(), self )
                    total_items -= 1
                    continue

                watched = bool( game_on_hdd )
                overlay = ( xbmcgui.ICON_OVERLAY_NONE, xbmcgui.ICON_OVERLAY_WATCHED, )[ watched ]
                info_labels = { "watched": watched, "overlay": overlay, "title": title, "studio": platform, "genre": genre, "plot": plot, "rating": float( rating ) }
                if year: info_labels.update( { "year": year } )
                if date: info_labels.update( { "date": date } )

                url = self.ARGV_REGEXP % ( sys.argv[ 0 ], games_id, platform, title )
                game_icon, game_thumbnail = self.get_thumbnail( tbn, url )
                listitem = xbmcgui.ListItem( title, iconImage=game_icon, thumbnailImage=game_thumbnail )
                listitem.setInfo( type="video", infoLabels=info_labels )
                OK = xbmcplugin.addDirectoryItem( handle=int( sys.argv[ 1 ] ), url=url, listitem=listitem, totalItems=total_items )
                if ( not OK ): raise
            if total_items == 0: return
        except:
            EXC_INFO( LOG_ERROR, sys.exc_info(), self )
            OK = False
        self._set_Content( OK )

    def get_thumbnail( self, online_tbn, xbmc_cached ):
        game_icon = "DefaultProgram.png"
        cover_image = ""
        try:
            if online_tbn.endswith( "nogame_large.gif" ) and ( self.settings[ "no_games_thumb" ] > 0 ):
                if os.path.isfile( self.settings[ "custom_games_thumb" ] ) and ( self.settings[ "no_games_thumb" ] < 2 ):
                    return game_icon, self.settings[ "custom_games_thumb" ]
                return game_icon, game_icon.replace( ".", "Big." )

            cached_thumb = xbmc.getCacheThumbName( online_tbn ).replace( "tbn", online_tbn.rsplit( "." )[ -1 ] )
            cover_image = os.path.join( THUMBNAILS_DIR_PATH, cached_thumb[ 0 ], cached_thumb )
            if os.path.isfile( cover_image ): return game_icon, cover_image

            xbmc_cached = xbmc.getCacheThumbName( xbmc_cached )
            xbmc_cached_thumb = xbmc.translatePath( os.path.join( "P:\\Thumbnails", "Video", xbmc_cached[ 0 ], xbmc_cached ) )
            if os.path.isfile( xbmc_cached_thumb ): return game_icon, xbmc_cached_thumb

            if online_tbn and ( online_tbn.endswith( "nogame_large.gif" ) or not self.settings[ "xbmc_auto_thumbs" ] ):
                try:
                    if not os.path.isdir( os.path.dirname( cover_image ) ):
                        os.makedirs( os.path.dirname( cover_image ) )
                    fp, h = urlretrieve( online_tbn, cover_image )
                    try:
                        if "text" in h[ "Content-Type" ]: os.unlink( cover_image )
                    except: pass
                except:
                    EXC_INFO( LOG_ERROR, sys.exc_info(), self )

            if not os.path.isfile( cover_image ):
                cover_image = online_tbn

        except:
            EXC_INFO( LOG_ERROR, sys.exc_info(), self )
            cover_image = game_icon.replace( ".", "Big." )

        return game_icon, cover_image

    def _set_Content( self, OK ):
        if ( OK ):
            content = ( "files", "movies", )[ self.settings[ "set_content" ] ]
            xbmcplugin.setContent( handle=int( sys.argv[ 1 ] ), content=content )
            try:
                # set our plugin category
                xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category=_( 30007 ) % self.user_search )
            except:
                EXC_INFO( LOG_ERROR, sys.exc_info(), self )
        self._add_sort_methods( OK )

    def _add_sort_methods( self, OK ):
        if ( OK ):
            methods = [
                xbmcplugin.SORT_METHOD_LABEL,
                xbmcplugin.SORT_METHOD_DATE,
                xbmcplugin.SORT_METHOD_VIDEO_YEAR,
                xbmcplugin.SORT_METHOD_GENRE,
                xbmcplugin.SORT_METHOD_STUDIO,
                xbmcplugin.SORT_METHOD_VIDEO_RATING
                ]
            [ xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=method ) for method in methods ]
        self._end_of_directory( OK )

    def _end_of_directory( self, OK ):
        xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=OK )
