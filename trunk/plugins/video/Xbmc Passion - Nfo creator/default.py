
import os
import re
import sys
import urllib
from traceback import print_exc

import xbmc
import xbmcgui
import xbmcplugin

from resources.pluginAPI.utilities import *


# plugin constants
__plugin__       = "Xbmc Passion - Nfo creator"
__script__       = "Unknown"
__author__       = "Frost"
__url__          = "http://code.google.com/p/passion-xbmc/"
__svn_url__      = "http://code.google.com/p/passion-xbmc/source/browse/#svn/trunk/plugins/video/"
__credits__      = "Team XBMC, http://xbmc.org/"
__platform__     = "xbmc media center"
__date__         = "04-01-2009"
__version__      = "0.1.1"
__svn_revision__ = 0


etape2 = "http://passion-xbmc.org/nfo_creator/index.php?listeFilm=%s&etape=2"
etape3 = "http://passion-xbmc.org/nfo_creator/index.php?etape=3&%s=%s"

regexp = """<input type="radio" name="([^"]+)" value="([^"]+)".*/>([^"]+)<a target=_blank href='([^"]+)'>voir la fiche</a>"""

_ = xbmc.getLocalizedString


class _Info:
    def __init__( self, *args, **kwargs ):
        self.__dict__.update( kwargs )


class Main:
    # add all video extensions wanted in lowercase
    VIDEO_EXT = xbmc.getSupportedMedia( "video" )

    def __init__( self ):
        self._get_settings()
        if ( "nfoUrl=" in sys.argv[ 2 ] ):
            self._parse_argv()
            self._install_nfo()
        elif ( "isFolder=0" in sys.argv[ 2 ] ):
            self._parse_argv()
            self._select_nfo()
        else:
            self._add_directory_items()

    def _parse_argv( self ):
        # call _Info() with our formatted argv to create the self.args object
        exec "self.args = _Info(%s)" % ( sys.argv[ 2 ][ 1 : ].replace( "&", ", " ), )
        # unquote path
        self.args.path = urllib.unquote_plus( self.args.path )

    def _get_settings( self ):
        self.settings = {}
        self.settings[ "path" ] = xbmcplugin.getSetting( "path" )
        self.settings[ "web_navigator" ] = xbmcplugin.getSetting( "web_navigator" )

    def _add_directory_items( self ):
        OK = True
        try:
            if not self.settings[ "path" ]:
                xbmcgui.Dialog().ok( _( 30000 ), _( 30008 ) )
                return
            total_items = 1
            for root, dirs, files in os.walk( self.settings[ "path" ], topdown=False ):
                total_items += len( files )
                for name in files:
                    fpath = os.path.join( root, name )
                    title, ext = os.path.splitext( name )
                    if title.lower() == "vts_01_1":
                        name = os.path.basename( root ) + ext
                    elif re.search( "vts_|video_", title.lower() ):
                        total_items -= 1
                        continue
                    if not ext.lower() in self.VIDEO_EXT:
                        total_items -= 1
                        continue
                    DIALOG_PROGRESS.update( -1, _( 1040 ), name )
                    thumbnail = get_thumbnail( fpath )
                    listitem = xbmcgui.ListItem( name, thumbnailImage=thumbnail )
                    # add the movie information item
                    c_items = [ ( _( 13358 ), "XBMC.PlayMedia(%s)" % ( fpath ), ) ]
                    # add items to listitem with replaceItems = True so only ours show
                    listitem.addContextMenuItems( c_items, replaceItems=True )
                    #get informations if exists
                    infolabels = self._get_infos( fpath )
                    listitem.setInfo( type="Video", infoLabels=infolabels )
                    url = '%s?path=%s&isFolder=%d' % ( sys.argv[ 0 ], repr( urllib.quote_plus( fpath ) ), 0, )
                    OK = xbmcplugin.addDirectoryItem( handle=int( sys.argv[ 1 ] ), url=url, listitem=listitem, isFolder=True )
                    if ( not OK ): raise
            listitem = xbmcgui.ListItem( _( 30001 ), thumbnailImage=os.path.join( os.getcwd().rstrip( ";" ), "default.tbn" ) )
            listitem.addContextMenuItems( [], replaceItems=True )
            url = '%s?path=%s&isFolder=%d' % ( sys.argv[ 0 ], repr( urllib.quote_plus( "" ) ), 0, )
            OK = xbmcplugin.addDirectoryItem( handle=int( sys.argv[ 1 ] ), url=url, listitem=listitem, isFolder=True, totalItems=total_items )
            if ( not OK ): raise
            xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category=_( 20012 ) )
        except:
            print_exc()
            OK = False
        self._set_Content( OK )

    def _get_infos( self, fpath ):
        infos = { "Title": os.path.basename( fpath ) }
        try:
            list = xbmc.executehttpapi( "GetMovieDetails(%s)" % ( fpath, ) ).split( "<li>" )
            infos.update( dict( [ tuple( unicode( line.strip( "\n" ), "utf-8" ).split( ":", 1 ) ) for line in list if line.strip( "\n" ) ] ) )
            if infos.get( "Year" ):
                infos[ "Year" ] = int( infos[ "Year" ] )
            if infos.get( "Rating" ):
                infos[ "Rating" ] = float( infos[ "Rating" ] )
            if infos.get( "Cast" ):
                infos[ "Cast" ] = infos[ "Cast" ].split( "\n" )
            #for key, value in infos.items():
            #    print key, value
            #print infos.keys()
            #print "-"*85
        except:
            print_exc()
        return infos

    def _select_nfo( self ):
        search_nfo = ""
        OK = True
        try:
            if not self.args.path:
                #xbmcgui.Dialog().ok( _( 30000 )  , _( 30002 ), _( 30003 ), _( 30004 ) )
                keyboard = xbmc.Keyboard( "", _( 30005 ) )
                keyboard.doModal()
                if keyboard.isConfirmed():
                    search_nfo = keyboard.getText().replace( " ", "+" )
                else:
                    return
            else:
                search_nfo = os.path.basename( self.args.path ).replace( " ", "+" )

            fpath = repr( urllib.quote_plus( self.args.path ) )

            #cas pour un dvd
            title, ext = os.path.splitext( search_nfo )
            if title.lower() == "vts_01_1":
                search_nfo = os.path.basename( os.path.dirname( self.args.path ) ) + ext

            DIALOG_PROGRESS.update( -1, _( 1040 ), search_nfo )
            if search_nfo:
                source = get_html_source( etape2 % search_nfo )
                nfo_listed =  re.findall( regexp, source )
                for count, items in enumerate( nfo_listed ):
                    name = set_pretty_formatting( items[ 2 ].strip() )
                    DIALOG_PROGRESS.update( -1, _( 1040 ), name )

                    listitem = xbmcgui.ListItem( name, thumbnailImage=os.path.join( os.getcwd().rstrip( ";" ), "default.tbn" ) )

                    if self.settings[ "web_navigator" ] != "" and os.path.exists( self.settings[ "web_navigator" ] ):
                        cmd = "System.Exec"
                        command = '%s("%s" "%s")' % ( cmd, self.settings[ "web_navigator" ], items[ 3 ], )
                        # add the movie information item
                        c_items = [ ( _( 30010 ), command, ) ]
                        # add items to listitem with replaceItems = True so only ours show
                        listitem.addContextMenuItems( c_items, replaceItems=True )

                    nfoUrl = repr( urllib.quote_plus( etape3 % ( items[ 0 ], items[ 1 ].replace( " ", "+" ), ) ) )
                    url = '%s?path=%s&nfoUrl=%s' % ( sys.argv[ 0 ], fpath, nfoUrl, )
                    OK = xbmcplugin.addDirectoryItem( handle=int( sys.argv[ 1 ] ), url=url, listitem=listitem, isFolder=False, totalItems=len( nfo_listed ) )
                    if ( not OK ): raise
            xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category=_( 283 ) + ":[CR]" + search_nfo )
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
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_NONE )
        self._end_of_directory( OK )

    def _end_of_directory( self, OK ):
        xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=OK )

    def _install_nfo( self ):
        try:
            self.args.nfoUrl = urllib.unquote_plus( self.args.nfoUrl )
            destination = os.path.dirname( self.args.path ) or os.path.dirname( self._nfo_associated_with() )
            if not destination:
                xbmcgui.Dialog().ok( _( 30000 ), _( 30041 ) )
                return

            heading, line1, line_error = _( 30000 ), _( 30006 ), _( 30007 )
            #xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=False )
            self._end_of_directory( False )
            DIALOG_PROGRESS.create( heading,  _( 1040 ), os.path.basename( self.args.path ),  )
            nfo, ok = unzip( self.args.nfoUrl, destination, True )
            DIALOG_PROGRESS.close()
            if not ok: xbmcgui.Dialog().ok( heading, line_error )
            else:
                #cas pour un dvd
                #if "vts_01_1" in self.args.path.lower():
                v_name = os.path.splitext( os.path.basename( self.args.path.lower() ) )[ 0 ]
                n_name = os.path.splitext( os.path.basename( nfo.lower() ) )[ 0 ]
                # les noms sont diffs on renomme le nfo comme le fichier video
                if v_name != n_name: nfo = self._rename_nfo( nfo )
                xbmcgui.Dialog().ok( heading, line1, "Dir: " + reduced_path( os.path.dirname( nfo ) ), "File: " + os.path.basename( nfo ) )
                #xbmc.executebuiltin( "XBMC.updatelibrary(video)" )
        except:
            print_exc()

    def _nfo_associated_with( self ):
        vpath = get_browse_dialog( heading=_( 30040 ), mask=self.VIDEO_EXT )
        self.args.path = vpath
        return vpath

    def _rename_nfo( self, old_name ):
        try:
            title, ext = os.path.splitext( os.path.basename( self.args.path ) )
            n_title, n_ext = os.path.splitext( os.path.basename( old_name ) )
            new_name = os.path.join( os.path.dirname( self.args.path ), title + n_ext )
            if os.path.exists( new_name ):
                os.remove( new_name )
            os.rename( old_name, new_name )
            return new_name
        except:
            print_exc()
            return old_name


if __name__ == "__main__":
    Main()
