
#Modules general
import os
import re
import sys
import time
import urllib
from traceback import print_exc

#modules XBMC
import xbmc
import xbmcgui
import xbmcplugin

#modules custom
from utilities import *


_ = xbmc.getLocalizedString


class Main:
    def __init__( self ):
        self._parse_argv()
        self._get_settings()
        self._add_directory_items()

    def _parse_argv( self ):
        # call _Info() with our formatted argv to create the self.args object
        exec "self.args = _Info(%s)" % ( sys.argv[ 2 ][ 1 : ].replace( "&", ", " ), )
        # unquote path
        self.args.nfoUrl = urllib.unquote_plus( self.args.nfoUrl )
        self.args.show_nfo = urllib.unquote_plus( self.args.show_nfo )

    def _get_settings( self ):
        self.settings = {}
        self.settings[ "web_navigator" ] = xbmcplugin.getSetting( "web_navigator" )

    def _add_directory_items( self ):
        OK = True
        try:
            self.nfo = self.get_nfo_infos( self.args.nfoUrl )
            if self.nfo[ "fanart" ]:
                fanart = get_nfo_thumbnail( self.nfo[ "fanart" ] )
                xbmcplugin.setPluginFanart( handle=int( sys.argv[ 1 ] ), image=fanart )

            tbn = get_thumbnail( self.nfo[ "thumbs" ] ) or self.nfo[ "thumbs" ]
            listitem = xbmcgui.ListItem( self.nfo[ "title" ], iconImage=tbn, thumbnailImage=tbn )

            url = '%s?path=%s&nfoUrl=%s' % ( sys.argv[ 0 ], repr( self.args.path ), repr( urllib.quote_plus( self.args.nfoUrl ) ), )

            c_items = [ ( _( 30012 ), "XBMC.RunPlugin(%s)" % ( url, ) ) ]
            c_items += [ ( _( 30009 ), "XBMC.Action(Info)", ) ]
            if self.settings[ "web_navigator" ] != "" and os.path.exists( self.settings[ "web_navigator" ] ):
                cmd = "System.Exec"
                command = '%s("%s" "%s")' % ( cmd, self.settings[ "web_navigator" ], self.args.show_nfo, )
                # add the movie information item
                c_items += [ ( _( 30010 ), command, ) ]
                # add items to listitem with replaceItems = True so only ours show
            listitem.addContextMenuItems( c_items, replaceItems=True )

            # delete unnecessary infos and set infoLabels
            del self.nfo[ "thumbs" ], self.nfo[ "fanart" ]
            listitem.setInfo( type="Video", infoLabels=self.nfo )

            OK = xbmcplugin.addDirectoryItem( handle=int( sys.argv[ 1 ] ), url=url, listitem=listitem, isFolder=False )
            if ( not OK ): raise
            xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category=_( 30013 ) )
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

        nfo_r = nfo_stream( url )
        try:
            #trailer     = ( re.findall( '<trailer>([^"]+)</trailer>', nfo_r )   or [ "" ] )[ 0 ]
            title       = ( re.findall( '<title>([^"]+)</title>', nfo_r )       or [ "" ] )[ 0 ]
            year        = ( re.findall( '<year>([^"]+)</year>', nfo_r )         or [ "" ] )[ 0 ]
            director    = ( re.findall( '<director>([^"]+)</director>', nfo_r ) or [ "" ] )[ 0 ]
            tagline     = ( re.findall( '<tagline>([^"]+)</tagline>', nfo_r )   or [ "" ] )[ 0 ]
            writer      = ( re.findall( '<credits>([^"]+)</credits>', nfo_r )   or [ "" ] )[ 0 ]
            studio      = ( re.findall( '<studio>([^"]+)</studio>', nfo_r )     or [ "" ] )[ 0 ]
            rating      = ( re.findall( '<rating>([^"]+)</rating>', nfo_r )     or [ "" ] )[ 0 ]
            votes       = ( re.findall( '<votes>([^"]+)</votes>', nfo_r )       or [ "" ] )[ 0 ]
            mpaa        = ( re.findall( '<mpaa>([^"]+)</mpaa>', nfo_r )         or [ "" ] )[ 0 ]
            genre       = ( re.findall( '<genre>([^"]+)</genre>', nfo_r )       or [ "" ] )[ 0 ]
            plotoutline = ( re.findall( '<outline>([^"]+)</outline>', nfo_r )   or [ "" ] )[ 0 ].replace( "\r", "  " ).replace( "\n", "  " )
            plot        = ( re.findall( '<plot>([^"]+)</plot>', nfo_r )         or [ "" ] )[ 0 ]

            thumbs      = ( re.findall( '<thumbs>([^"]+)</thumbs>', nfo_r, re.DOTALL ) or [ "" ] )[ 0 ]
            thumbs      = ( re.findall( '<thumb>(.*)</thumb>', thumbs )                or [ "" ] )[ 0 ]

            fanart      = ( re.findall( '<fanart>([^"]+)</fanart>', nfo_r, re.DOTALL ) or [ "" ] )[ 0 ]
            fanart      = ( re.findall( '<thumb>(.*)</thumb>', fanart )                or [ "" ] )[ 0 ]

            cast        = ( re.findall( '<actor>([^"]+)</actor>', nfo_r, re.DOTALL )   or [ "" ] )[ 0 ]
            cast        = zip( re.findall( '<name>(.*)</name>', cast ), re.findall( '<role>(.*)</role>', cast ) )

            duration    = ( re.findall( '<runtime>([^"]+)</runtime>', nfo_r ) or [ "" ] )[ 0 ]
            try:
                hrs, min = re.findall( "(\d{1,4})", duration )
                duration = time.strftime( "%X", time.gmtime( ( int( hrs ) * 60 * 60 ) + ( int( min ) * 60 ) ) )
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
        del self, url, nfo_r
        return locals()
