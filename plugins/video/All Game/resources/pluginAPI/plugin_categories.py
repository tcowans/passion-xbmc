
import os
import sys
import xbmc
import xbmcgui
import xbmcplugin

from plugin_log import *


CWD = os.getcwd().rstrip( ";" )

_ = xbmc.getLocalizedString

DIALOG_PROGRESS = xbmcgui.DialogProgress()

PLUGIN_RUN_UNDER = sys.modules[ "__main__" ].PLUGIN_RUN_UNDER

API_PATH = sys.modules[ "__main__" ].API_PATH


def getUserSkin():
    current_skin = xbmc.getSkinDir()
    force_fallback = os.path.exists( os.path.join( CWD, "resources", "skins", current_skin ) )
    if not force_fallback: current_skin = "Default"
    return current_skin, force_fallback


class Main:
    ARGV_REGEXP = "%s?pluginAPI=/%s"
    RELEASES_REGEXP = "%s?pluginAPI=Releases&&release_id=%s&&release=/%s"
    GAMES_REGEXP = "%s?pluginAPI=Games&&games_url=http://www.allgame.com/cg/agg.dll?p=agg&sql=5:%s&&platform=/%s"

    def __init__( self ):
        self._get_settings()
        self._set_plugin_fanart()
        self._add_directory_items()

    def _get_settings( self ):
        self.settings = {}
        self.settings[ "extra_button" ] = ( None,
            ( 30028, "45571", "Nintendo DS" ),
            ( 30027, "45561", "PlayStation Portable" ),
            ( 30026, "49611", "Wii" ),
            ( 30025, "47504", "XBox 360" ),
            ( 30024, "47532", "PlayStation 3" ), )[ int( xbmcplugin.getSetting( "extra_button" ) ) ]
        self.settings[ "enable_fanart" ] = xbmcplugin.getSetting( "enable_fanart" ) == "true"
        self.settings[ "fanart_image" ] = xbmcplugin.getSetting( "fanart_image" )
        self.base_media = xbmc.translatePath( os.path.join( CWD, "resources", "skins", getUserSkin()[ 0 ], "media" ) )
        if not os.path.exists( self.base_media ):
            self.base_media = xbmc.translatePath( os.path.join( CWD, "resources", "skins", "Default", "media" ) )

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
            # ALL PLATFORMS
            if os.path.isfile( os.path.join( API_PATH, "plugin_platforms.py" ) ):
                DIALOG_PROGRESS.update( -1, _( 1040 ), _( 30001 ) )
                tbn = os.path.join( self.base_media, "Platforms.png" )
                listitem = xbmcgui.ListItem( _( 30001 ), thumbnailImage=( "", tbn, )[ os.path.isfile( tbn ) ] )
                listitem.setInfo( type="video", infoLabels={ "title": _( 30001 ), "plot": " " } )
                url = self.ARGV_REGEXP % ( sys.argv[ 0 ], "All Platforms", )
                OK = xbmcplugin.addDirectoryItem( handle=int( sys.argv[ 1 ] ), url=url, listitem=listitem, isFolder=True )
                if ( not OK ): raise

            # RELEASES RECENT, UPCOMING, FUTURE
            if os.path.isfile( os.path.join( API_PATH, "plugin_releases.py" ) ):
                DIALOG_PROGRESS.update( -1, _( 1040 ), _( 30002 ) )
                tbn = os.path.join( self.base_media, "recent.png" )
                listitem = xbmcgui.ListItem( _( 30002 ), thumbnailImage=( "", tbn, )[ os.path.isfile( tbn ) ] )
                listitem.setInfo( type="video", infoLabels={ "title": _( 30002 ), "plot": " " } )
                url = self.RELEASES_REGEXP % ( sys.argv[ 0 ], "0", "Recent Releases", )
                OK = xbmcplugin.addDirectoryItem( handle=int( sys.argv[ 1 ] ), url=url, listitem=listitem, isFolder=True )
                if ( not OK ): raise

                DIALOG_PROGRESS.update( -1, _( 1040 ), _( 30003 ) )
                tbn = os.path.join( self.base_media, "upcoming.png" )
                listitem = xbmcgui.ListItem( _( 30003 ), thumbnailImage=( "", tbn, )[ os.path.isfile( tbn ) ] )
                listitem.setInfo( type="video", infoLabels={ "title": _( 30003 ), "plot": " " } )
                url = self.RELEASES_REGEXP % ( sys.argv[ 0 ], "1", "Upcoming Releases", )
                OK = xbmcplugin.addDirectoryItem( handle=int( sys.argv[ 1 ] ), url=url, listitem=listitem, isFolder=True )
                if ( not OK ): raise

                DIALOG_PROGRESS.update( -1, _( 1040 ), _( 30004 ) )
                tbn = os.path.join( self.base_media, "future.png" )
                listitem = xbmcgui.ListItem( _( 30004 ), thumbnailImage=( "", tbn, )[ os.path.isfile( tbn ) ] )
                listitem.setInfo( type="video", infoLabels={ "title": _( 30004 ), "plot": " " } )
                url = self.RELEASES_REGEXP % ( sys.argv[ 0 ], "2", "Future Releases", )
                OK = xbmcplugin.addDirectoryItem( handle=int( sys.argv[ 1 ] ), url=url, listitem=listitem, isFolder=True )
                if ( not OK ): raise

            # EXTRA BUTTON
            if self.settings[ "extra_button" ]:
                DIALOG_PROGRESS.update( -1, _( 1040 ), _( self.settings[ "extra_button" ][ 0 ] ) )
                tbn = os.path.join( self.base_media, "%s.png" % ( self.settings[ "extra_button" ][ 2 ], ) )
                tbn = ( tbn, "", )[ not os.path.isfile( tbn ) ]
                listitem = xbmcgui.ListItem( _( self.settings[ "extra_button" ][ 0 ] ), thumbnailImage=tbn )
                listitem.setInfo( type="video", infoLabels={ "title": _( self.settings[ "extra_button" ][ 0 ] ), "plot": " " } )
                url = self.GAMES_REGEXP % ( sys.argv[ 0 ], self.settings[ "extra_button" ][ 1 ], self.settings[ "extra_button" ][ 2 ], )
                #print xbmc.getCacheThumbName( url )
                OK = xbmcplugin.addDirectoryItem( handle=int( sys.argv[ 1 ] ), url=url, listitem=listitem, isFolder=True )
                if ( not OK ): raise

            # PLUGIN RUN UNDER XBOX SHOW THIS CATEGORIE
            if PLUGIN_RUN_UNDER == "xbox":
                DIALOG_PROGRESS.update( -1, _( 1040 ), _( 30020 ) )
                tbn = os.path.join( self.base_media, "xbox.png" )
                tbn = ( tbn, "http://www.allgame.com/img/systems/xbox.gif", )[ not os.path.isfile( tbn ) ]
                listitem = xbmcgui.ListItem( _( 30020 ), thumbnailImage=tbn )
                listitem.setInfo( type="video", infoLabels={ "title": _( 30020 ), "plot": " " } )
                url = self.GAMES_REGEXP % ( sys.argv[ 0 ], "26052", "Xbox", )
                #print xbmc.getCacheThumbName( url )
                OK = xbmcplugin.addDirectoryItem( handle=int( sys.argv[ 1 ] ), url=url, listitem=listitem, isFolder=True )
                if ( not OK ): raise

            # PLUGIN RUN UNDER WINDOW OR LINUX SHOW "IBM PC Compatible" CATEGORIE
            if PLUGIN_RUN_UNDER in ( "win32", "linux" ):
                DIALOG_PROGRESS.update( -1, _( 1040 ), _( 30021 ) )
                tbn = os.path.join( self.base_media, "pc.png" )
                tbn = ( tbn, "http://www.allgame.com/img/systems/ibmpc.gif", )[ not os.path.isfile( tbn ) ]
                listitem = xbmcgui.ListItem( _( 30021 ), thumbnailImage=tbn )
                listitem.setInfo( type="video", infoLabels={ "title": _( 30021 ), "plot": " " } )
                url = self.GAMES_REGEXP % ( sys.argv[ 0 ], "2", "IBM PC Compatible", )
                #print xbmc.getCacheThumbName( url )
                OK = xbmcplugin.addDirectoryItem( handle=int( sys.argv[ 1 ] ), url=url, listitem=listitem, isFolder=True )
                if ( not OK ): raise

            # PLUGIN RUN UNDER MAC OS X SHOW THIS CATEGORIE
            if PLUGIN_RUN_UNDER == "osx":
                DIALOG_PROGRESS.update( -1, _( 1040 ), _( 30022 ) )
                tbn = os.path.join( self.base_media, "osx.png" )
                tbn = ( tbn, "http://www.allgame.com/img/systems/mac.gif", )[ not os.path.isfile( tbn ) ]
                listitem = xbmcgui.ListItem( _( 30022 ), thumbnailImage=tbn )
                listitem.setInfo( type="video", infoLabels={ "title": _( 30022 ), "plot": " " } )
                url = self.GAMES_REGEXP % ( sys.argv[ 0 ], "5", "Macintosh", )
                #print xbmc.getCacheThumbName( url )
                OK = xbmcplugin.addDirectoryItem( handle=int( sys.argv[ 1 ] ), url=url, listitem=listitem, isFolder=True )
                if ( not OK ): raise

            # PLUGIN RUN UNDER COMPUTER SHOW "Hybrid Windows/Mac" CATEGORIE
            if PLUGIN_RUN_UNDER in ( "win32", "linux", "osx" ):
                DIALOG_PROGRESS.update( -1, _( 1040 ), _( 30023 ) )
                tbn = os.path.join( self.base_media, "hybrid.png" )
                tbn = ( tbn, "", )[ not os.path.isfile( tbn ) ]
                listitem = xbmcgui.ListItem( _( 30023 ), thumbnailImage=tbn )
                listitem.setInfo( type="video", infoLabels={ "title": _( 30023 ), "plot": " " } )
                url = self.GAMES_REGEXP % ( sys.argv[ 0 ], "46", "Hybrid Windows/Mac", )
                #print xbmc.getCacheThumbName( url )
                OK = xbmcplugin.addDirectoryItem( handle=int( sys.argv[ 1 ] ), url=url, listitem=listitem, isFolder=True )
                if ( not OK ): raise

            # SEARCH
            if os.path.isfile( os.path.join( API_PATH, "plugin_search.py" ) ):
                DIALOG_PROGRESS.update( -1, _( 1040 ), _( 30006 ) )
                tbn = os.path.join( self.base_media, "Search.png" )
                listitem = xbmcgui.ListItem( _( 30006 ), thumbnailImage=( "", tbn, )[ os.path.isfile( tbn ) ] )
                listitem.setInfo( type="video", infoLabels={ "title": _( 30006 ), "plot": " " } )
                url = self.ARGV_REGEXP % ( sys.argv[ 0 ], "Search", )
                OK = xbmcplugin.addDirectoryItem( handle=int( sys.argv[ 1 ] ), url=url, listitem=listitem, isFolder=True )
                if ( not OK ): raise

        except:
            EXC_INFO( LOG_ERROR, sys.exc_info(), self )
            OK = False
        self._add_sort_methods( OK )

    def _add_sort_methods( self, OK ):
        if ( OK ):
            #xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_LABEL )
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_NONE )
        self._end_of_directory( OK )

    def _end_of_directory( self, OK ):
        xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=OK )
