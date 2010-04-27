
# plugin constants
__plugin__        = "Astral Media"
__author__        = "Frost"
__url__           = "http://code.google.com/p/passion-xbmc/"
__svn_url__       = "http://passion-xbmc.googlecode.com/svn/trunk/plugins/video/Astral%20Media/"
__credits__       = "Team XBMC, http://xbmc.org/"
__platform__      = "xbmc media center, [ALL]"
__date__          = "27-04-2010"
__version__       = "1.0.1"
__svn_revision__  = "$Revision$"



import os
import sys
import time
import urllib
from traceback import print_exc

import xbmc
import xbmcgui
import xbmcplugin

from resources.pluginAPI.scrapers import *
from resources.pluginAPI.htmldecode import *


_ = xbmc.getLocalizedString

DIALOG_PROGRESS = xbmcgui.DialogProgress()


class _Info:
    def __init__( self, *args, **kwargs ):
        self.__dict__.update( kwargs )


class Main:
    REGEXP_URL = "%s?type='%s'&theme='%s'&emission='%s'&episode='%s'&page='%s'&canal='%s'"

    def __init__( self ):
        self._parse_argv()
        self._get_settings()

        if not sys.argv[ 2 ]:
            self._add_directory_canals()
        elif "='select'" in sys.argv[ 2 ]:
            self.select()
        else:
            self._add_directory_items()

    def select( self ):
        try:
            contents = eval( file( os.path.join( os.getcwd(), "contents.data" ), "r" ).read() )
            if "emission='select" in sys.argv[ 2 ]:
                emissions = contents[ "programId" ]
                choice = [ self._decode( title ) for i, title in emissions ]
                selected = xbmcgui.Dialog().select( "Choix des émissions disponibles" , choice )
                if selected != -1:
                    self.args.emission = str( emissions[ selected ][ 0 ] )
                    self._add_directory_items()
                    return

            elif "episode='select" in sys.argv[ 2 ]:
                episodes = contents[ "episodeId" ]
                choice = [ self._decode( title.replace( "-----", "Tous" ) ) for i, title in episodes ]
                selected = xbmcgui.Dialog().select( "Choix des épisodes disponibles" , choice )
                if selected != -1:
                    self.args.episode = str( episodes[ selected ][ 0 ] )
                    self._add_directory_items()
                    return

            elif "type='select" in sys.argv[ 2 ]:
                types = contents[ "typeId" ]
                choice = [ self._decode( title ) for i, title in types ]
                selected = xbmcgui.Dialog().select( "Choix des types de vidéo disponibles" , choice )
                if selected != -1:
                    self.args.type = str( types[ selected ][ 0 ] )
                    self._add_directory_items()
                    return

            elif "theme='select" in sys.argv[ 2 ]:
                themes = contents[ "themeId" ]
                choice = [ self._decode( title ) for i, title in themes ]
                selected = xbmcgui.Dialog().select( "Choix Thématiques disponibles" , choice )
                if selected != -1:
                    self.args.theme = str( themes[ selected ][ 0 ] )
                    self._add_directory_items()
                    return

            self._end_of_directory( False )
        except:
            print "self.args", dir( self.args )
            print_exc()
            self._end_of_directory( False )

    def _decode( self, text ):
        try:
            return htmlentitydecode( text )
        except:
            print_exc()
        return text

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
        #premiere list
        OK = True
        try:
            for canal, value in sorted( canals.items() ):
                DIALOG_PROGRESS.update( -1, _( 1040 ), value[ 0 ] )
                tbn = os.path.join( os.getcwd(), "resources", "media", "%s.png" % canal )
                listitem = xbmcgui.ListItem( value[ 0 ], "", tbn, tbn )

                c_items = []
                c_items += [ ( _( 654 ), "XBMC.ActivateWindow(scriptsdebuginfo)" ) ]
                listitem.addContextMenuItems( c_items, replaceItems=True )

                infolabels = { "title": value[ 0 ], "plot": value[ 2 ] }
                listitem.setInfo( type="video", infoLabels=infolabels )

                url = self.REGEXP_URL % ( sys.argv[ 0 ], "0", "0", "0", "0", "1", canal )
                OK = xbmcplugin.addDirectoryItem( handle=int( sys.argv[ 1 ] ), url=url, listitem=listitem, isFolder=True )
                if ( not OK ): raise
        except:
            print_exc()
            OK = False
        self._set_content( OK )

    def _add_directory_contents( self, contents ):
        OK = True
        try:
            file( os.path.join( os.getcwd(), "contents.data" ), "w" ).write( repr( contents ) )
            if contents[ "programId" ]:
                tbn = os.path.join( os.getcwd(), "resources", "media", "%s.png" % self.args.canal )
                title = "[B]Émissions[/B] (%i)" % (len( contents[ "programId" ] )-1)
                listitem = xbmcgui.ListItem( title, "", tbn, tbn )

                c_items = [ ( _( 654 ), "XBMC.ActivateWindow(scriptsdebuginfo)" ) ]
                listitem.addContextMenuItems( c_items, replaceItems=True )

                infolabels = { "title": title, "tvshowtitle": canals[ self.args.canal ][ 0 ], "plot": "Afficher la liste des émissions disponibles" }
                listitem.setInfo( type="video", infoLabels=infolabels )

                url = self.REGEXP_URL % ( sys.argv[ 0 ], self.args.type, self.args.theme, "select", self.args.episode, self.args.page, self.args.canal )
                OK = xbmcplugin.addDirectoryItem( handle=int( sys.argv[ 1 ] ), url=url, listitem=listitem, isFolder=True )
                if ( not OK ): raise

            if contents[ "episodeId" ]:
                tbn = os.path.join( os.getcwd(), "resources", "media", "%s.png" % self.args.canal )
                title = "[B]Épisodes[/B] (%i)" % (len( contents[ "episodeId" ] )-1)
                listitem = xbmcgui.ListItem( title, "", tbn, tbn )

                c_items = [ ( _( 654 ), "XBMC.ActivateWindow(scriptsdebuginfo)" ) ]
                listitem.addContextMenuItems( c_items, replaceItems=True )

                tvshowtitle = "".join( [ t for i, t in contents[ "programId" ] if i == self.args.emission ] )
                infolabels = { "title": title, "tvshowtitle": tvshowtitle, "plot": "Afficher la liste des épisodes disponibles" }
                listitem.setInfo( type="video", infoLabels=infolabels )

                url = self.REGEXP_URL % ( sys.argv[ 0 ], self.args.type, self.args.theme, self.args.emission, "select", self.args.page, self.args.canal )
                OK = xbmcplugin.addDirectoryItem( handle=int( sys.argv[ 1 ] ), url=url, listitem=listitem, isFolder=True )
                if ( not OK ): raise

            if contents[ "typeId" ]:
                tbn = os.path.join( os.getcwd(), "resources", "media", "%s.png" % self.args.canal )
                title = "[B]Types de vidéo[/B] (%i)" % (len( contents[ "typeId" ] )-1)
                listitem = xbmcgui.ListItem( title, "", tbn, tbn )

                c_items = [ ( _( 654 ), "XBMC.ActivateWindow(scriptsdebuginfo)" ) ]
                listitem.addContextMenuItems( c_items, replaceItems=True )

                infolabels = { "title": title, "tvshowtitle": canals[ self.args.canal ][ 0 ], "plot": "Afficher la liste des types de vidéo" }
                listitem.setInfo( type="video", infoLabels=infolabels )

                url = self.REGEXP_URL % ( sys.argv[ 0 ], "select", self.args.theme, self.args.emission, self.args.episode, self.args.page, self.args.canal )
                OK = xbmcplugin.addDirectoryItem( handle=int( sys.argv[ 1 ] ), url=url, listitem=listitem, isFolder=True )
                if ( not OK ): raise

            if contents[ "themeId" ]:
                tbn = os.path.join( os.getcwd(), "resources", "media", "%s.png" % self.args.canal )
                title = "[B]Thématiques[/B] (%i)" % (len( contents[ "themeId" ] )-1)
                listitem = xbmcgui.ListItem( title, "", tbn, tbn )

                c_items = [ ( _( 654 ), "XBMC.ActivateWindow(scriptsdebuginfo)" ) ]
                listitem.addContextMenuItems( c_items, replaceItems=True )

                infolabels = { "title": title, "tvshowtitle": canals[ self.args.canal ][ 0 ], "plot": "Afficher la liste Thématiques" }
                listitem.setInfo( type="video", infoLabels=infolabels )

                url = self.REGEXP_URL % ( sys.argv[ 0 ], self.args.type, "select", self.args.emission, self.args.episode, self.args.page, self.args.canal )
                OK = xbmcplugin.addDirectoryItem( handle=int( sys.argv[ 1 ] ), url=url, listitem=listitem, isFolder=True )
                if ( not OK ): raise
        except:
            print_exc()
        return OK

    def _add_directory_items( self ):
        OK = True
        try:
            canal_url = canals[ self.args.canal ][ 1 ]
            # getTvShows( canal_url="", typeid="0", themeid="0", programid="0", episodeid="0", pageid="1" )
            episodes, pages, contents = getTvShows( canal_url, self.args.type, self.args.theme, self.args.emission, self.args.episode, self.args.page )
            #if ( not episodes ): raise
            # save contents if page is 1 and add addDirectoryItem for this
            self._add_directory_contents( contents )

            total_items = len( episodes )
            # { "tvshowtitle": "", "title": "", "type": "", "duration": "",
            #   "date": "", "plot": "", "thumb": "", "episode" : "", "season" : "" }
            for videoid, episode in episodes.items():
                DIALOG_PROGRESS.update( -1, _( 1040 ), episode[ "title" ] )
                listitem = xbmcgui.ListItem( episode[ "title" ], "", episode[ "thumb" ], episode[ "thumb" ] )
                c_items = [ ( _( 13346 ), "XBMC.Action(Info)", ) ]
                c_items += [ ( _( 654 ), "XBMC.ActivateWindow(scriptsdebuginfo)" ) ]
                listitem.addContextMenuItems( c_items, replaceItems=True )

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

                flvs = getWebVideoUrl( canal_url, videoid )
                try: flv = flvs[ int( xbmcplugin.getSetting( "quality" ) ) ]
                except: flv = flvs[ 0 ]

                OK = xbmcplugin.addDirectoryItem( handle=int( sys.argv[ 1 ] ), url=flv, listitem=listitem, isFolder=False, totalItems=total_items )
                if ( not OK ): raise

            try:
                #ajout du bouton next
                if 1 < int( pages ) >= ( int( self.args.page )+1 ):
                    next = str( int( self.args.page )+1 )

                    tbn = os.path.join( os.getcwd(), "resources", "media", "next1.png" )
                    listitem = xbmcgui.ListItem( "[B]Page suivante[/B]", "", tbn, tbn )

                    c_items = [ ( _( 654 ), "XBMC.ActivateWindow(scriptsdebuginfo)" ) ]
                    listitem.addContextMenuItems( c_items, replaceItems=True )

                    infolabels = { "title": "Page suivante", "tvshowtitle": canals[ self.args.canal ][ 0 ], "plot": "Aller à la page %s de %s" % ( next, pages ) }
                    listitem.setInfo( type="video", infoLabels=infolabels )

                    url = self.REGEXP_URL % ( sys.argv[ 0 ], self.args.type, self.args.theme, self.args.emission, self.args.episode, next, self.args.canal )
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
