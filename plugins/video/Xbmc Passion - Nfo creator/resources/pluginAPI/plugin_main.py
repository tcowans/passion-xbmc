
#Modules general
import os
import re
import sys
import urllib
from traceback import print_exc

#modules XBMC
import xbmc
import xbmcgui
import xbmcplugin

#modules custom
from utilities import *


etape2 = "http://passion-xbmc.org/nfo_creator/index.php?listeFilm=%s&etape=2"
etape3 = "http://passion-xbmc.org/nfo_creator/index.php?etape=3&%s=%s"

regexp = """<input type="radio" name="([^"]+)" value="([^"]+)".*/>([^"]+)<a target=_blank href='([^"]+)'>voir la fiche</a>"""

_ = xbmc.getLocalizedString

# set our thumbnail
install_thumbnail = xbmc.getInfoImage( "ListItem.Thumb" )
Fanart_thumbnail = xbmc.getInfoImage( "Fanart.Image" )

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
        self.settings[ "path" ] = self._get_path_list( xbmcplugin.getSetting( "path" ) )#xbmcplugin.getSetting( "path" )
        self.settings[ "web_navigator" ] = xbmcplugin.getSetting( "web_navigator" )
        self.settings[ "write_list" ] = int( xbmcplugin.getSetting( "write_list" ) )

    def _add_directory_items( self ):
        OK = True
        listing = []
        try:
            if not self.settings[ "path" ]:
                xbmcgui.Dialog().ok( _( 30000 ), _( 30008 ) )
                return
            total_items = 1
            for paths in self.settings[ "path" ]:
                if not os.path.exists( paths ):
                    print "NFO Creator, videos path invalide:", repr( paths )
                else:
                    for root, dirs, files in os.walk( paths, topdown=False ):
                        #total_items += len( files )
                        for name in files:
                            fpath = os.path.join( root, name )
                            title, ext = os.path.splitext( name )
                            if name.lower() == "video_ts.ifo":
                                name = os.path.basename( root ) + ext
                            elif re.search( "vts_|video_", title.lower() ):
                                #total_items -= 1
                                continue
                            if not ext.lower() in self.VIDEO_EXT:
                                #total_items -= 1
                                continue
                            total_items += 1
                            # add name in listing for liste.txt
                            listing.append( name )
                            DIALOG_PROGRESS.update( -1, _( 1040 ), name )
                            icon = "DefaultVideo.png"
                            thumbnail = get_thumbnail( fpath ) or os.path.splitext( fpath )[ 0 ] + ".tbn"
                            listitem = xbmcgui.ListItem( name, iconImage=icon, thumbnailImage=thumbnail )
                            # add the movie information item
                            c_items = [ ( _( 13358 ), "XBMC.PlayMedia(%s)" % ( fpath ), ) ]
                            # add items to listitem with replaceItems = True so only ours show
                            listitem.addContextMenuItems( c_items, replaceItems=True )
                            #get informations if exists
                            infolabels = self._get_infos( fpath )
                            listitem.setInfo( type="Video", infoLabels=infolabels )
                            listitem.setProperty( "Fanart_Image", os.path.splitext( fpath )[ 0 ] + "-fanart.jpg" )
                            url = '%s?path=%s&isFolder=%d' % ( sys.argv[ 0 ], repr( urllib.quote_plus( fpath ) ), 0, )
                            OK = xbmcplugin.addDirectoryItem( handle=int( sys.argv[ 1 ] ), url=url, listitem=listitem, isFolder=True, totalItems=total_items )
                            if ( not OK ): raise

            # recherche manuel
            listing.sort( key=lambda f: f.lower() )
            self._add_search( listing, total_items )

            xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category=_( 20012 ) )
        except:
            print_exc()
            OK = False
        self._save_listing( listing )
        self._set_Content( OK )

    def _get_path_list( self, paths ):
        # we do not want the slash at end
        if ( paths.endswith( "\\" ) or paths.endswith( "/" ) ):
            paths = paths[ : -1 ]
        # if this is not a multipath return it as a list
        if ( not paths.startswith( "multipath://" ) ): return [ paths ]
        # we need to parse out the separate paths in a multipath share
        fpaths = []
        # multipaths are separated by a forward slash(why not a pipe)
        path_list = paths[ 12 : ].split( "/" )
        # enumerate thru our path list and unquote the url
        for path in path_list:
        # we do not want the slash at end
            if ( path.endswith( "\\" ) or path.endswith( "/" ) ):
                path = path[ : -1 ]
            # add our path
            fpaths += [ urllib.unquote( path ) ]
        return fpaths

    def _save_listing( self, listing ):
        #save la liste pour etre utiliser directement avec le generateur nfo
        if listing and ( self.settings[ "write_list" ] > 0 ):
            try:
                file( os.path.join( self.settings[ "path" ][ 0 ], "Liste.txt" ), "w" ).write( os.linesep.join( listing ) )
            except:
                print_exc()

    def _add_search( self, listing, total_items ):
        # recherche manuel
        c_items = []
        listitem = xbmcgui.ListItem( _( 30001 ), thumbnailImage=os.path.join( os.getcwd().rstrip( ";" ), "default.tbn" ) )
        if ( self.settings[ "write_list" ] == 2 ):
            if self.settings[ "web_navigator" ] != "" and os.path.exists( self.settings[ "web_navigator" ] ):
                cmd = "System.Exec"
                url = etape2 % urllib.quote_plus( os.linesep ).join( listing )#"%0D%0A"
                command = '%s("%s" "%s")' % ( cmd, self.settings[ "web_navigator" ], url, )
                # add the movie information item
                c_items = [ ( _( 30011 ), command, ) ]
                # add items to listitem with replaceItems = True so only ours show
                listitem.addContextMenuItems( c_items, replaceItems=True )
            infos = { "Title": unicode( reduced_path( os.path.join( self.settings[ "path" ][ 0 ], "Liste.txt" ) ), "utf-8" ),
                "plot": unicode( "[CR]".join( listing ), "utf-8" ), "genre": "http://passion-xbmc.org/nfo_creator/index.php" }
            listitem.setInfo( type="Video", infoLabels=infos )
        if not c_items:
            listitem.addContextMenuItems( [], replaceItems=True )
        url = '%s?path=%s&isFolder=%d' % ( sys.argv[ 0 ], repr( "" ), 0, )
        OK = xbmcplugin.addDirectoryItem( handle=int( sys.argv[ 1 ] ), url=url, listitem=listitem, isFolder=True, totalItems=total_items )
        if ( not OK ): raise

    def _get_infos( self, fpath ):
        watched = os.path.exists( os.path.splitext( fpath )[ 0 ] + ".nfo" )
        overlay = ( xbmcgui.ICON_OVERLAY_NONE, xbmcgui.ICON_OVERLAY_RAR, )[ watched ]
        infos = { "Title": os.path.basename( fpath ), "watched": watched, "overlay": overlay }
        try:
            strlist = xbmc.executehttpapi( "GetMovieDetails(%s)" % ( fpath, ) )
            if not "error" in strlist.lower():
                infos.update( dict( [ tuple( unicode( line.strip( "\n" ), "utf-8" ).split( ":", 1 ) ) for line in strlist.split( "<li>" ) if line.strip( "\n" ) ] ) )
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
                    search_nfo = keyboard.getText()
                    # if user use "+" for multiple search replace there by line return
                    search_nfo = urllib.quote_plus( os.linesep ).join( [ n.strip() for n in search_nfo.split( "+" ) ] ).replace( " ", "+" )
            else:
                search_nfo = os.path.basename( self.args.path ).replace( " ", "+" )

            if not search_nfo:
                return

            fpath = repr( urllib.quote_plus( self.args.path ) )

            #cas pour un dvd
            title, ext = os.path.splitext( search_nfo )
            #if title.lower() == "vts_01_1":
            if search_nfo.lower() == "video_ts.ifo":
                search_nfo = os.path.basename( os.path.dirname( self.args.path ) ) + ext

            DIALOG_PROGRESS.update( -1, _( 1040 ), urllib.unquote_plus( search_nfo ).replace( os.linesep, "+" ) )
            if search_nfo:
                source = get_html_source( etape2 % search_nfo )
                nfo_listed =  re.findall( regexp, source )
                for count, items in enumerate( nfo_listed ):
                    name = set_pretty_formatting( items[ 2 ].strip() )
                    DIALOG_PROGRESS.update( -1, _( 1040 ), name )

                    listitem = xbmcgui.ListItem( name, thumbnailImage=os.path.join( os.getcwd().rstrip( ";" ), "default.tbn" ) )

                    nfoUrl = repr( urllib.quote_plus( etape3 % ( items[ 0 ], items[ 1 ].replace( " ", "+" ), ) ) )

                    url = '%s?path=%s&nfoUrl=%s' % ( sys.argv[ 0 ], fpath, nfoUrl, )
                    c_items = [ ( _( 30012 ), "XBMC.RunPlugin(%s)" % ( url, ) ) ]
                    if self.settings[ "web_navigator" ] != "" and os.path.exists( self.settings[ "web_navigator" ] ):
                        cmd = "System.Exec"
                        command = '%s("%s" "%s")' % ( cmd, self.settings[ "web_navigator" ], items[ 3 ], )
                        # add the movie information item
                        c_items += [ ( _( 30010 ), command, ) ]
                        # add items to listitem with replaceItems = True so only ours show
                    listitem.addContextMenuItems( c_items, replaceItems=True )

                    web = repr( urllib.quote_plus( items[ 3 ] ) )
                    url = '%s?show_nfo=%s&path=%s&nfoUrl=%s' % ( sys.argv[ 0 ], web, fpath, nfoUrl, )
                    OK = xbmcplugin.addDirectoryItem( handle=int( sys.argv[ 1 ] ), url=url, listitem=listitem, isFolder=True, totalItems=len( nfo_listed ) )
                    if ( not OK ): raise
            search_nfo = urllib.unquote_plus( search_nfo ).replace( os.linesep, "+" )
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
            #xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_NONE )
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_LABEL )
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
            self._end_of_directory( False )
            DIALOG_PROGRESS.create( heading,  _( 1040 ), os.path.basename( self.args.path ),  )
            nfo, ok = unzip( self.args.nfoUrl, destination, True )
            self._copy_thumbnails()
            DIALOG_PROGRESS.close()
            if not ok: xbmcgui.Dialog().ok( heading, line_error )
            else:
                v_name = os.path.splitext( os.path.basename( self.args.path.lower() ) )[ 0 ]
                n_name = os.path.splitext( os.path.basename( nfo.lower() ) )[ 0 ]
                # les noms sont diffs on renomme le nfo comme le fichier video
                if v_name != n_name: nfo = self._rename_nfo( nfo )
                xbmcgui.Dialog().ok( heading, line1, "Dir: " + reduced_path( os.path.dirname( nfo ) ), "File: " + os.path.basename( nfo ) )
                #xbmc.executebuiltin( "XBMC.updatelibrary(video)" )
        except:
            print_exc()

    def _copy_thumbnails( self ):
        try:
            if os.path.exists( install_thumbnail ):
                thumbpath = os.path.splitext( self.args.path )[ 0 ] + ".tbn"
                DIALOG_PROGRESS.update( -1, install_thumbnail, thumbpath )
                xbmc.executehttpapi( "FileCopy(%s,%s)" % ( install_thumbnail, thumbpath.encode( "utf-8" ), ) )
            if os.path.exists( Fanart_thumbnail ):
                thumbpath = os.path.splitext( self.args.path )[ 0 ] + "-fanart.jpg"
                DIALOG_PROGRESS.update( -1, Fanart_thumbnail, thumbpath )
                xbmc.executehttpapi( "FileCopy(%s,%s)" % ( Fanart_thumbnail, thumbpath.encode( "utf-8" ), ) )
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
