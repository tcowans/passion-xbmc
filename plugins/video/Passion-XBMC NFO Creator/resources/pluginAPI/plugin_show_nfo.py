
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
from utilities import *


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

    def _add_directory_items( self ):
        OK = True
        try:
            exec "from scrapers.%s import scraper" % self.settings[ "scraper" ]
            movie_data = scraper.Movie( self.args.show_id, is_svn_version() )
            self.nfo_file = movie_data.XML( SPECIAL_PLUGIN_CACHE, passion_fanart=self.settings[ "passion_fanart" ]  )
            #del scraper

            DIALOG_PROGRESS.update( -1, _( 1040 ), self.nfo_file )
            self.nfo = self.get_nfo_infos( self.nfo_file )

            DIALOG_PROGRESS.update( -1, _( 1040 ), self.nfo[ "title" ] )

            tbn = get_nfo_thumbnail( self.nfo[ "thumbs" ] ) or self.nfo[ "thumbs" ]
            listitem = xbmcgui.ListItem( self.nfo[ "title" ], iconImage=tbn, thumbnailImage=tbn )

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

            if self.nfo[ "fanart" ]:
                fanart = get_nfo_thumbnail( self.nfo[ "fanart" ] )
                listitem.setProperty( "Fanart_Image", fanart )
                xbmcplugin.setPluginFanart( handle=int( sys.argv[ 1 ] ), image=fanart )
            # delete unnecessary infos and set infoLabels
            del self.nfo[ "thumbs" ], self.nfo[ "fanart" ]
            listitem.setInfo( type="Video", infoLabels=self.nfo )

            OK = xbmcplugin.addDirectoryItem( handle=int( sys.argv[ 1 ] ), url=url, listitem=listitem, isFolder=True )
            if ( not OK ): raise

            OK = self._add_trailers_item( movie_data )
            xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category="[B]NFO[/B]" )
        except:
            print_exc()
            OK = False
        self._set_Content( OK )

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
            title       = ( re.findall( '<title>(.*?)</title>', nfo_r )          or [ "" ] )[ 0 ] + " [B](NFO File)[/B]"
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
