
# plugin constants
__plugin__        = "Astral Media"
__author__        = "Frost"
__url__           = "http://code.google.com/p/passion-xbmc/"
__svn_url__       = "http://passion-xbmc.googlecode.com/svn/trunk/plugins/video/"
__credits__       = "Team XBMC, http://xbmc.org/"
__platform__      = "xbmc media center, [ALL]"
__date__          = "25-04-2010"
__version__       = "1.0.0"
__svn_revision__  = "$Revision$"



import os
import sys
import time
from traceback import print_exc

import xbmc
import xbmcgui
import xbmcplugin

from resources.pluginAPI.scrapers import *


_ = xbmc.getLocalizedString

DIALOG_PROGRESS = xbmcgui.DialogProgress()


class _Info:
    def __init__( self, *args, **kwargs ):
        self.__dict__.update( kwargs )


class Main:
    def __init__( self ):
        self._parse_argv()
        self._get_settings()

        if not sys.argv[ 2 ]:
            self._add_directory_canals()
        else:
            self._add_directory_items()

    def _parse_argv( self ):
        # call _Info() with our formatted argv to create the self.args object
        self.args = _Info()
        try:
            exec "self.args = _Info(%s)" % ( sys.argv[ 2 ][ 1: ].replace( "&", ", " ), )
        except:
            print_exc()

    def _get_settings( self ):
        self.settings = {}

    def _add_directory_canals( self ):
        OK = True
        try:
            for canal, value in sorted( canals.items() ):
                DIALOG_PROGRESS.update( -1, _( 1040 ), value[ 0 ] )
                tbn = os.path.join( os.getcwd(), "resources", "media", "%s.png" % canal )
                listitem = xbmcgui.ListItem( value[ 0 ], "", tbn, tbn )

                c_items = []
                #c_items += [ ( _( 13346 ), "XBMC.Action(Info)", ) ]
                c_items += [ ( _( 654 ), "XBMC.ActivateWindow(scriptsdebuginfo)" ) ]
                listitem.addContextMenuItems( c_items, replaceItems=True )

                infolabels = { "title": value[ 0 ], "plot": value[ 2 ] }
                listitem.setInfo( type="video", infoLabels=infolabels )
                url = '%s?page="1"&canal="%s"' % ( sys.argv[ 0 ], canal, )
                OK = xbmcplugin.addDirectoryItem( handle=int( sys.argv[ 1 ] ), url=url, listitem=listitem, isFolder=True )
                if ( not OK ): raise
        except:
            print_exc()
            OK = False
        self._set_content( OK )

    def _add_directory_items( self ):
        OK = True
        try:
            canal_url = canals[ self.args.canal ][ 1 ]
            episodes, pages = getTvShows( canal_url, self.args.page )

            total_items = len( episodes )
            #tvshows[ ID ] = { "tvshowtitle": "", "title": "", "type": "", "duration": "",
            #        "date": "", "plot": "", "thumb": "", "episode" : "", "season" : "" }
            for videoid, episode in episodes.items():
                DIALOG_PROGRESS.update( -1, _( 1040 ), episode[ "title" ] )
                listitem = xbmcgui.ListItem( episode[ "title" ], "", episode[ "thumb" ], episode[ "thumb" ] )
                infolabels = {
                    "title": episode[ "title" ],
                    "tvshowtitle": episode[ "tvshowtitle" ],
                    "genre": episode[ "type" ],
                    "studio": canals[ self.args.canal ][ 0 ],
                    "plot": episode[ "plot" ],
                    "premiered": episode[ "date" ],
                    "date": time.strftime( "%d.%m.%Y", time.localtime( time.mktime( time.strptime( episode[ "date" ], "%d/%m/%y" ) ) ) ),
                    "aired": episode[ "date" ],
                    "episode": episode[ "episode" ],
                    "season": episode[ "season" ],
                    "duration": episode[ "duration" ],
                    }
                listitem.setInfo( type="video", infoLabels=infolabels )

                try: flv = getWebVideoUrl( canal_url, videoid )[ int( xbmcplugin.getSetting( "quality" ) ) ]
                except: flv = getWebVideoUrl( canal_url, videoid )[ 0 ]
                OK = xbmcplugin.addDirectoryItem( handle=int( sys.argv[ 1 ] ), url=flv, listitem=listitem, isFolder=False, totalItems=total_items )
                if ( not OK ): raise

            try:
                #ajout du bouton next
                if 1 < int( pages ) >= ( int( self.args.page )+1 ):
                    next = int( self.args.page )+1
                    url = '%s?page="%i"&canal="%s"' % ( sys.argv[ 0 ], next, self.args.canal, )
                    tbn = os.path.join( os.getcwd(), "resources", "media", "next1.png" )
                    listitem = xbmcgui.ListItem( "[B]Page suivante[/B]", "", tbn, tbn )
                    infolabels = { "title": "Page suivante", "tvshowtitle": canals[ self.args.canal ][ 0 ],
                        "plot": "Aller à la page %i de %s" % ( next, pages ) }
                    listitem.setInfo( type="video", infoLabels=infolabels )
                    OK = xbmcplugin.addDirectoryItem( handle=int( sys.argv[ 1 ] ), url=url, listitem=listitem, isFolder=True, totalItems=total_items+1 )
                    if ( not OK ): raise
            except: pass
        except:
            print_exc()
            OK = False
        self._set_content( OK, 3 )

    def _set_content( self, OK, index=1 ):
        if ( OK ):
            content = ( "files", "movies", "tvshows", "episodes", )[ index ]
            xbmcplugin.setContent( handle=int( sys.argv[ 1 ] ), content=content )
        self._add_sort_methods( OK )

    def _add_sort_methods( self, OK ):
        if ( OK ):
            try:
                xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_DATE )
                #xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE )
                xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_VIDEO_TITLE )
                xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_GENRE )
                xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_VIDEO_RUNTIME )
                xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_STUDIO )
            except:
                print_exc()
        self._end_of_directory( OK )

    def _end_of_directory( self, OK ):
        xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=OK )#, cacheToDisc=True )#updateListing = True,



if ( __name__ == "__main__" ):
    Main()
