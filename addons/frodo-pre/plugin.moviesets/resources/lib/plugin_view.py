
import sys
import xbmc
import xbmcplugin
from xbmcaddon import Addon

from moviesets import getFullMovieSetsDetails

# constants
ADDON      = Addon( "plugin.moviesets" )
ADDON_NAME = ADDON.getAddonInfo( "name" )

Language = ADDON.getLocalizedString # ADDON strings
LangXBMC = xbmc.getLocalizedString # XBMC strings



class PluginView:
    def __init__( self ):
        listitems = getFullMovieSetsDetails( ADDON.getSetting( "allsets" ) == "true" )
        ok = self._add_directory_items( listitems )

        xbmcplugin.setProperty( int( sys.argv[ 1 ] ), "Content", "MovieSets" )
        xbmcplugin.setProperty( int( sys.argv[ 1 ] ), "TotalSets", str( len( listitems ) ) )
        #xbmcplugin.setProperty( int( sys.argv[ 1 ] ), "FolderName", ADDON_NAME )

        #xbmcplugin.setPluginCategory( int( sys.argv[ 1 ] ), ADDON_NAME )

        self._set_content( ok )

    def _add_directory_item( self, url, listitem, isFolder, totalItems=0 ):
        """ addDirectoryItem(handle, url, listitem [,isFolder, totalItems])
            handle      : integer - handle the plugin was started with.
            url         : string - url of the entry. would be plugin:// for another virtual directory
            listitem    : ListItem - item to add.
            isFolder    : [opt] bool - True=folder / False=not a folder(default).
            totalItems  : [opt] integer - total number of items that will be passed.(used for progressbar)
        """
        return xbmcplugin.addDirectoryItem( int( sys.argv[ 1 ] ), url, listitem, isFolder, totalItems )
    
    def _add_directory_items( self, listitems ):
        """ addDirectoryItems(handle, items [,totalItems])
            handle      : integer - handle the plugin was started with.
            items       : List - list of (url, listitem[, isFolder]) as a tuple to add.
            totalItems  : [opt] integer - total number of items that will be passed.(used for progressbar)
        """
        return xbmcplugin.addDirectoryItems( int( sys.argv[ 1 ] ), listitems, len( listitems ) )

    def _set_content( self, succeeded, content="movies", sort=True ):
        if ( succeeded ):
            #content = ( "addons", "files", "movies", "tvshows", "episodes", "musicvideos", "albums", "artists", "songs" )[ 2 ]
            #content = "moviesets"
            xbmcplugin.setContent( int( sys.argv[ 1 ] ), content )
        if sort:
            self._add_sort_methods( succeeded )
        else:
            self._end_of_directory( succeeded )

    def _add_sort_methods( self, succeeded ):
        if ( succeeded ):
            #xbmcplugin.addSortMethod( int( sys.argv[ 1 ] ), xbmcplugin.SORT_METHOD_UNSORTED )
            xbmcplugin.addSortMethod( int( sys.argv[ 1 ] ), xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE )
            xbmcplugin.addSortMethod( int( sys.argv[ 1 ] ), xbmcplugin.SORT_METHOD_VIDEO_RATING )
            xbmcplugin.addSortMethod( int( sys.argv[ 1 ] ), xbmcplugin.SORT_METHOD_VIDEO_YEAR )
            xbmcplugin.addSortMethod( int( sys.argv[ 1 ] ), xbmcplugin.SORT_METHOD_GENRE )
            xbmcplugin.addSortMethod( int( sys.argv[ 1 ] ), xbmcplugin.SORT_METHOD_MPAA_RATING )
            xbmcplugin.addSortMethod( int( sys.argv[ 1 ] ), xbmcplugin.SORT_METHOD_PROGRAM_COUNT )
            xbmcplugin.addSortMethod( int( sys.argv[ 1 ] ), xbmcplugin.SORT_METHOD_DATE )
        self._end_of_directory( succeeded )

    def _end_of_directory( self, succeeded ):
        xbmcplugin.endOfDirectory( int( sys.argv[ 1 ] ), succeeded )


#PluginView()

