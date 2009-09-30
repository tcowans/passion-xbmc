
#Modules general
import os
import re
import sys
from traceback import print_exc
from urllib import quote_plus, unquote_plus, unquote

from urlparse25 import urlparse

#modules XBMC
import xbmc
import xbmcgui
import xbmcplugin

#modules custom
import nfo_utils
from utilities import *


PASSION_NFO = "http://passion-xbmc.org/nfo_creator/index.php?listeFilm=%s&etape=2"

_ = xbmc.getLocalizedString

DIALOG_PROGRESS = xbmcgui.DialogProgress()


class Main:
    # add all video extensions wanted in lowercase
    VIDEO_EXT = xbmc.getSupportedMedia( "video" )

    def __init__( self ):
        self.total_items = 1
        self.titles_paths = []
        self.listing = []

        self._get_settings()
        self._add_directory_items()

    def _get_settings( self ):
        self.settings = {}
        self.settings[ "path" ] = self._get_path_list( xbmcplugin.getSetting( "path" ) )
        self.settings[ "write_list" ] = int( xbmcplugin.getSetting( "write_list" ) )
        self.settings[ "web_navigator" ] = xbmcplugin.getSetting( "web_navigator" )
        self.settings[ "hide_extention" ] = ( xbmcplugin.getSetting( "hide_extention" ) == "true" )
        self.settings[ "not_share" ] = ( xbmcplugin.getSetting( "not_share" ) == "true" )

    def _get_share_listing( self, dpath ):
        OK = True
        if ( self.settings[ "not_share" ] ) and ( urlparse( dpath ).scheme in ( "ftp", "smb", "upnp", "xbms", "http" ) ):
            return OK
        entries = xbmc.executehttpapi( "GetDirectory(%s)" % ( dpath, ) ).split( "\n" )
        #print dpath
        for count, entry in enumerate( entries ):
            if entry:
                # fix path
                path = entry.replace( "<li>", "" )
                # remove slash at end
                if ( path.endswith( "/" ) or path.endswith( "\\" ) ):
                    path = path[ :-1 ]
                else:
                    title, ext = os.path.splitext( os.path.basename( path ) )
                    if ( ext and not ext.lower() in self.VIDEO_EXT ):
                        continue
                # get the item info
                title, isVideo, isFolder = self._get_file_info( path )
                if title and isFolder:
                    OK = self._get_share_listing( path )
                else:
                    name, ext = os.path.splitext( os.path.basename( path ) )
                    if name.lower() == "video_ts" and ext.lower() == ".ifo":
                        if re.search( "video", os.path.basename( os.path.dirname( path ) ).lower() ):
                            title = os.path.basename( os.path.dirname( os.path.dirname( path ) ) )
                        else:
                            title = os.path.basename( os.path.dirname( path ) )
                    elif re.search( "vts_|video_", title.lower() ):
                        continue
                    DIALOG_PROGRESS.update( -1, _( 1040 ), title )
                    self.total_items += 1
                    isShare = ( urlparse( path ).scheme in ( "ftp", "smb", "upnp", "xbms", "http" ) )
                    
                    self.titles_paths.append( ( title, path, isShare ) )
                    OK = self._add_directory_item( title, path, isShare )
                    #print path
                    #print title, isShare
                    #print
            #if ( DIALOG_PROGRESS.iscanceled() ): break
        return OK

    def _get_file_info( self, file_path ):
        try:
            # parse item for title
            title, ext = os.path.splitext( os.path.basename( file_path ) )
            # is this a folder?
            isFolder = ( ( not ext) or ( ext == ".rar" ) or os.path.isdir( file_path ) )
            # if it's a folder keep extension in title
            title += ( "", ext, )[ isFolder ]
            # default isVideo to false
            isVideo = False
            # if this is a file, check to see if it's a valid video file
            if ( not isFolder ):
                # if it is a video file add it to our items list
                isVideo = ( ext and ext.lower() in self.VIDEO_EXT )
            return title, isVideo, isFolder
        except:
            # oops print error message
            print repr( file_path )
            print "ERROR: %s::%s (%d) - %s" % ( self.__class__.__name__, sys.exc_info()[ 2 ].tb_frame.f_code.co_name, sys.exc_info()[ 2 ].tb_lineno, sys.exc_info()[ 1 ], )
            return "", False, False

    def _add_directory_items( self ):
        OK = True
        #listing = []
        try:
            if not self.settings[ "path" ]:
                #xbmcgui.Dialog().ok( _( 30000 ), _( 30008 ) )
                self._end_of_directory( False )
                xbmcplugin.openSettings( sys.argv[ 0 ] )
                return

            xbmc.sleep( 1000 )
            for paths in self.settings[ "path" ]:
                OK = self._get_share_listing( paths )

            # recherche manuel
            self.listing.sort( key=lambda f: f.lower() )
            self._add_search()

            xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category=_( 20012 ) )
        except:
            print_exc()
            OK = False
        self._save_listing()
        self._set_content( OK )

    def _add_directory_item( self, name, path, isShare ):
        OK = True
        try:
            #for name, path, isShare in self.titles_paths:
            fpath = path
            # get extention 
            filename, ext = os.path.splitext( fpath )
            # add name in self.listing for liste.txt
            self.listing.append( name + ext )
            name = ( name + ext, name )[ self.settings[ "hide_extention" ] ]
            DIALOG_PROGRESS.update( -1, _( 1040 ), name )
            icon = "DefaultVideo.png"
            thumbnail = get_thumbnail( fpath )
            if not thumbnail:
                try: thumbnail = ( filename + ".tbn" )#.replace( "\xc3\xa9", "\xe9" )
                except: print_exc()
            listitem = xbmcgui.ListItem( name, iconImage=icon, thumbnailImage=thumbnail )
            # add the movie information item
            c_items = [ ( _( 13358 ), "XBMC.PlayMedia(%s)" % ( fpath ), ) ]
            c_items += [ ( _( 30009 ), "XBMC.Action(Info)", ) ]
            c_items += [ ( _( 654 ), "XBMC.ActivateWindow(scriptsdebuginfo)" ) ]
            # add items to listitem with replaceItems = True so only ours show
            listitem.addContextMenuItems( c_items, replaceItems=True )
            #get informations if exists
            infolabels = self._get_infos( fpath )
            if isShare:
                infolabels.update( { "watched": isShare, "overlay": xbmcgui.ICON_OVERLAY_TRAINED } )
            listitem.setInfo( type="Video", infoLabels=infolabels )
            try:
                fanart = filename + "-fanart.jpg"
                listitem.setProperty( "Fanart_Image", fanart )
            except:
                print_exc()
            url = '%s?path=%s&isFolder=%d' % ( sys.argv[ 0 ], repr( quote_plus( fpath ) ), 0, )
            OK = xbmcplugin.addDirectoryItem( handle=int( sys.argv[ 1 ] ), url=url, listitem=listitem, isFolder=True, totalItems=len( self.titles_paths ) )
            if ( not OK ): raise

        except:
            print_exc()
            OK = False
        return OK

    def _get_path_list( self, paths ):
        # we do not want the slash at end
        if ( paths.endswith( "\\" ) or paths.endswith( "/" ) ):
            paths = paths[ : -1 ]
        # if not settings path return empty list
        if not paths: return []
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
            fpaths += [ unquote( path ) ]
        return sorted( fpaths )

    def _save_listing( self ):
        #sauvegarde la liste pour etre utiliser directement avec le generateur nfo en ligne de passion-xbmc
        if self.listing and ( self.settings[ "write_list" ] > 0 ):
            try:
                file( os.path.join( self.settings[ "path" ][ 0 ], "Liste.txt" ), "w" ).write( os.linesep.join( self.listing ) )
                #file( os.path.join( os.getcwd().rstrip( ";" ), "Liste.txt" ), "w" ).write( os.linesep.join( self.listing ) )
            except: print_exc()

    def _add_search( self ):
        # recherche manuel
        c_items = []
        listitem = xbmcgui.ListItem( _( 30001 ), thumbnailImage=os.path.join( os.getcwd().rstrip( ";" ), "default.tbn" ) )
        #if ( self.settings[ "write_list" ] == 2 ):
        #    if self.settings[ "web_navigator" ] != "" and os.path.exists( self.settings[ "web_navigator" ] ):
        #        c_items += [ ( _( 30009 ), "XBMC.Action(Info)", ) ]
        #        cmd = "System.Exec"
        #        url = PASSION_NFO % translate_string( quote_plus( os.linesep ).join( self.listing ) )#"%0D%0A"
        #        command = '%s("%s" "%s")' % ( cmd, self.settings[ "web_navigator" ], url, )
        #        # add the movie information item
        #        c_items += [ ( _( 30011 ), command, ) ]
        #        # add items to listitem with replaceItems = True so only ours show
        #        c_items += [ ( _( 654 ), "XBMC.ActivateWindow(scriptsdebuginfo)" ) ]
        #        listitem.addContextMenuItems( c_items, replaceItems=True )
        #    infos = { "Title": reduced_path( os.path.join( self.settings[ "path" ][ 0 ], "Liste.txt" ) ),
        #        "plot": "[CR]".join( self.listing ), "genre": "http://passion-xbmc.org/nfo_creator/index.php",
        #        "watched": 1, "overlay": xbmcgui.ICON_OVERLAY_TRAINED }
        #    listitem.setInfo( type="Video", infoLabels=infos )
        if not c_items:
            c_items += [ ( _( 30009 ), "XBMC.Action(Info)", ) ]
            c_items += [ ( _( 654 ), "XBMC.ActivateWindow(scriptsdebuginfo)" ) ]
            listitem.addContextMenuItems( c_items, replaceItems=True )
        url = '%s?path=%s&isFolder=%d' % ( sys.argv[ 0 ], repr( "" ), 0, )
        OK = xbmcplugin.addDirectoryItem( handle=int( sys.argv[ 1 ] ), url=url, listitem=listitem, isFolder=True, totalItems=len( self.titles_paths ) )
        if ( not OK ): raise

    def _get_infos( self, fpath ):
        watched = os.path.exists( os.path.splitext( fpath )[ 0 ] + ".nfo" )
        overlay = ( xbmcgui.ICON_OVERLAY_NONE, xbmcgui.ICON_OVERLAY_RAR, )[ watched ]

        self.nfo = nfo_utils.InfosNFO()
        self.nfo.set( "title", os.path.basename( fpath ) )
        #self.nfo.isTVShow = True
        try:
            if watched:
                self.nfo.parse( os.path.splitext( fpath.replace( "\xe9", "\xc3\xa9" ) )[ 0 ] + ".nfo" )
            else:
                strlist = xbmc.executehttpapi( "GetMovieDetails(%s)" % ( fpath, ) )
                if "error" in strlist.lower():
                    strlist = xbmc.executehttpapi( "GetMovieDetails(%s)" % ( fpath.replace( "\xe9", "\xc3\xa9" ), ) )
                if not "error" in strlist.lower():
                    self.nfo.__dict__.update( dict( [ tuple( unicode( line.strip( "\n" ), "utf-8" ).split( ":", 1 ) ) for line in strlist.split( "<li>" ) if line.strip( "\n" ) ] ) )
                    if self.nfo.get( "Year" ):
                        self.nfo.Year = int( self.nfo.get( "Year" ) or "0" )
                        self.nfo.infoLabels.update( { "year": self.nfo.Year } )
                    if self.nfo.get( "Rating" ):
                        self.nfo.Rating = float( self.nfo.get( "Rating" ) or "0.0" )
                        self.nfo.infoLabels.update( { "rating": self.nfo.Rating } )
                    if self.nfo.get( "Cast" ):
                        self.nfo.Cast = self.nfo.get( "Cast", "" ).split( "\n" )
                        self.nfo.infoLabels.update( { "cast": self.nfo.Cast } )
        except:
            print fpath
            print_exc()
        self.nfo.infoLabels.update( { "title": self.nfo.title, "watched": watched, "overlay": overlay } )
        return self.nfo.infoLabels

    def _set_content( self, OK ):
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
