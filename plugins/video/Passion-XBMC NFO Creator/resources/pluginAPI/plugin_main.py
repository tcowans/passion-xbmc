
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
        if ( self.settings[ "not_share" ] ) and ( urlparse( dpath ).scheme in "ftp|smb|upnp|xbms|http" ):
            return
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
                    self._get_share_listing( path )
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
                    isShare = ( urlparse( path ).scheme in "ftp|smb|upnp|xbms|http" )
                    self.titles_paths.append( ( title, path, isShare ) ) 
                    #print path
                    #print title, isShare
                    #print

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
        listing = []
        try:
            if not self.settings[ "path" ]:
                #xbmcgui.Dialog().ok( _( 30000 ), _( 30008 ) )
                self._end_of_directory( False )
                xbmcplugin.openSettings( sys.argv[ 0 ] )
                return

            xbmc.sleep( 1000 )
            for paths in self.settings[ "path" ]:
                self._get_share_listing( paths )

            for name, path, isShare in self.titles_paths:
                fpath = path
                # get extention 
                ext = os.path.splitext( fpath )[ 1 ]
                # add name in listing for liste.txt
                listing.append( name + ext )
                name = ( name + ext, name )[ self.settings[ "hide_extention" ] ]
                DIALOG_PROGRESS.update( -1, _( 1040 ), name )
                icon = "DefaultVideo.png"
                thumbnail = get_thumbnail( fpath ) or os.path.splitext( fpath )[ 0 ] + ".tbn"
                listitem = xbmcgui.ListItem( name, iconImage=icon, thumbnailImage=thumbnail )
                # add the movie information item
                c_items = [ ( _( 13358 ), "XBMC.PlayMedia(%s)" % ( fpath ), ) ]
                c_items += [ ( _( 30009 ), "XBMC.Action(Info)", ) ]
                # add items to listitem with replaceItems = True so only ours show
                c_items += [ ( _( 654 ), "XBMC.ActivateWindow(scriptsdebuginfo)" ) ]
                listitem.addContextMenuItems( c_items, replaceItems=True )
                #get informations if exists
                infolabels = self._get_infos( fpath )
                if isShare:
                    infolabels.update( { "watched": isShare, "overlay": xbmcgui.ICON_OVERLAY_TRAINED } )
                listitem.setInfo( type="Video", infoLabels=infolabels )
                listitem.setProperty( "Fanart_Image", os.path.splitext( fpath )[ 0 ] + "-fanart.jpg" )
                url = '%s?path=%s&isFolder=%d' % ( sys.argv[ 0 ], repr( quote_plus( fpath ) ), 0, )
                OK = xbmcplugin.addDirectoryItem( handle=int( sys.argv[ 1 ] ), url=url, listitem=listitem, isFolder=True, totalItems=len( self.titles_paths ) )
                if ( not OK ): raise

            # recherche manuel
            listing.sort( key=lambda f: f.lower() )
            self._add_search( listing )

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

    def _save_listing( self, listing ):
        #sauvegarde la liste pour etre utiliser directement avec le generateur nfo en ligne de passion-xbmc
        if listing and ( self.settings[ "write_list" ] > 0 ):
            try:
                file( os.path.join( self.settings[ "path" ][ 0 ], "Liste.txt" ), "w" ).write( os.linesep.join( listing ) )
                #file( os.path.join( os.getcwd().rstrip( ";" ), "Liste.txt" ), "w" ).write( os.linesep.join( listing ) )
            except: print_exc()

    def _add_search( self, listing ):
        # recherche manuel
        c_items = []
        listitem = xbmcgui.ListItem( _( 30001 ), thumbnailImage=os.path.join( os.getcwd().rstrip( ";" ), "default.tbn" ) )
        if ( self.settings[ "write_list" ] == 2 ):
            if self.settings[ "web_navigator" ] != "" and os.path.exists( self.settings[ "web_navigator" ] ):
                c_items += [ ( _( 30009 ), "XBMC.Action(Info)", ) ]
                cmd = "System.Exec"
                url = PASSION_NFO % translate_string( quote_plus( os.linesep ).join( listing ) )#"%0D%0A"
                command = '%s("%s" "%s")' % ( cmd, self.settings[ "web_navigator" ], url, )
                # add the movie information item
                c_items += [ ( _( 30011 ), command, ) ]
                # add items to listitem with replaceItems = True so only ours show
                c_items += [ ( _( 654 ), "XBMC.ActivateWindow(scriptsdebuginfo)" ) ]
                listitem.addContextMenuItems( c_items, replaceItems=True )
            infos = { "Title": reduced_path( os.path.join( self.settings[ "path" ][ 0 ], "Liste.txt" ) ),
                "plot": "[CR]".join( listing ), "genre": "http://passion-xbmc.org/nfo_creator/index.php",
                "watched": 1, "overlay": xbmcgui.ICON_OVERLAY_TRAINED }
            listitem.setInfo( type="Video", infoLabels=infos )
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
        infos = { "Title": os.path.basename( fpath ), "watched": watched, "overlay": overlay }
        try:
            if watched:
                infos = self.get_nfo_infos( os.path.splitext( fpath.replace( "\xe9", "\xc3\xa9" ) )[ 0 ] + ".nfo" )
            else:
                strlist = xbmc.executehttpapi( "GetMovieDetails(%s)" % ( fpath, ) )
                if "error" in strlist.lower():
                    strlist = xbmc.executehttpapi( "GetMovieDetails(%s)" % ( fpath.replace( "\xe9", "\xc3\xa9" ), ) )
                if not "error" in strlist.lower():
                    infos.update( dict( [ tuple( unicode( line.strip( "\n" ), "utf-8" ).split( ":", 1 ) ) for line in strlist.split( "<li>" ) if line.strip( "\n" ) ] ) )
                    if infos.get( "Year" ):
                        infos[ "Year" ] = int( infos[ "Year" ] )
                    if infos.get( "Rating" ):
                        infos[ "Rating" ] = float( infos[ "Rating" ] )
                    if infos.get( "Cast" ):
                        infos[ "Cast" ] = infos[ "Cast" ].split( "\n" )
                    #for key, value in infos.items():
                    #    print key, value.encode( "iso-8859-1" )
            #print infos.keys()
            #print "-"*85
        except:
            print fpath
            print_exc()
        infos.update( { "watched": watched, "overlay": overlay } )
        return infos

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

    def get_nfo_infos( self, url ):
        """use get_nfo_infos and return infos for listitem.setInfo
        setInfo(type, infoLabels) -- Sets the listitem's infoLabels.

        type           : string - type of media(video/music/pictures).
        infoLabels     : dictionary - pairs of { label: value }.

        *Note, To set pictures exif info, prepend 'exif:' to the label. Exif values must be passed
               as strings, separate value pairs with a comma. (eg. {'exif:resolution': '720,480'}
               See CPictureInfoTag::TranslateString in PictureInfoTag.cpp for valid strings.

               You can use the above as keywords for arguments and skip certain optional arguments.
               Once you use a keyword, all following arguments require the keyword.

        example:
          - self.list.getSelectedItem().setInfo('video', { 'Genre': 'Comedy' })
        """

        nfo_r = file( url, "r" ).read()
        try:
            trailer     = ( re.findall( '<trailer>(.*?)</trailer>', nfo_r )      or [ "" ] )[ 0 ]
            title       = ( re.findall( '<title>(.*?)</title>', nfo_r )          or [ "" ] )[ 0 ]
            year        = ( re.findall( '<year>(.*?)</year>', nfo_r )            or [ "" ] )[ 0 ]
            date        = ( re.findall( '<date>(.*?)</date>', nfo_r )            or [ "" ] )[ 0 ]
            director    = ( re.findall( '<director.*?>(.*?)</director>', nfo_r ) or [ "" ] )[ 0 ]
            tagline     = ( re.findall( '<tagline>(.*?)</tagline>', nfo_r )      or [ "" ] )[ 0 ]
            writer      = ( re.findall( '<credits.*?>(.*?)</credits>', nfo_r )   or [ "" ] )[ 0 ]
            studio      = ( re.findall( '<studio.*?>(.*?)</studio>', nfo_r )     or [ "" ] )[ 0 ]
            rating      = ( re.findall( '<rating>(.*?)</rating>', nfo_r )        or [ "" ] )[ 0 ]
            votes       = ( re.findall( '<votes>(.*?)</votes>', nfo_r )          or [ "" ] )[ 0 ]
            mpaa        = ( re.findall( '<mpaa>(.*?)</mpaa>', nfo_r )            or [ "" ] )[ 0 ]
            genre       = ( re.findall( '<genre.*?>(.*?)</genre>', nfo_r )       or [ "" ] )[ 0 ]
            plotoutline = ( re.findall( '<outline>(.*?)</outline>', nfo_r )      or [ "" ] )[ 0 ].replace( "\r", "  " ).replace( "\n", "  " )
            plot        = ( re.findall( '<plot>(.*?)</plot>', nfo_r, re.DOTALL ) or [ "" ] )[ 0 ]

            thumbs      = ( re.findall( '<thumbs>(.*?)</thumbs>', nfo_r, re.DOTALL ) or [ "" ] )[ 0 ]
            thumbs      = ( re.findall( '<thumb>(.*)</thumb>', thumbs )              or [ "" ] )[ 0 ]

            fanart      = ( re.findall( '<fanart>(.*?)</fanart>', nfo_r, re.DOTALL ) or [ "" ] )[ 0 ]
            fanart      = ( re.findall( '<thumb>(.*)</thumb>', fanart )              or [ "" ] )[ 0 ]

            cast_and_role = []
            for actor_role in re.findall( '<actor.*?>(.*?)</actor>', nfo_r, re.DOTALL ):
                try:
                    cast_and_role.append( zip( re.findall( '<name>(.*)</name>', actor_role ),
                        re.findall( '<role>(.*)</role>', actor_role ) )[ 0 ] )
                except: pass
            cast = cast_and_role


            duration    = ( re.findall( '<runtime>(.*?)</runtime>', nfo_r ) or [ "" ] )[ 0 ]
            try:
                hrs, min = re.findall( "(\d{1,4})", duration )
                duration = time.strftime( "%X", time.gmtime( ( int( hrs ) * 60 * 60 ) + ( int( min ) * 60 ) ) )
                del hrs, min
            except: pass

            # set required integer
            if year.isdigit(): year = int( year )
            if rating.isdigit(): rating = float( rating )
            
            # possible others keywords for video type
            #episode = integer
            #season = integer
            #count = integer
            #size = integer
            #watched = integer 1 or 2
            #playcount = integer
            #overlay = integer, look xbmcguimodule.cpp
            #cast or castandrole = ["bla"] or  [("game","over")]
            #tvshowtitle = string
            #premiered = string
            #date = string, format "2009-01-12"
            #trailer = string, playable media local or online
        except:
            print_exc()

        # delete unnecessary infos and return locals is infoLabels (dict)
        del self, url, nfo_r, cast_and_role
        return locals()
