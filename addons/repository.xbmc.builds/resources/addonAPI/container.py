
#Modules General
import os
import re
import sys
import urllib
from traceback import print_exc

#Modules XBMC
import xbmc
import xbmcgui
import xbmcplugin
from xbmcaddon import Addon


#Modules Custom
import repo
from addonwindow import addonWindow


XBMC_ICON = Addon( "repository.xbmc.org" ).getAddonInfo( "icon" )

__settings__ = sys.modules[ "__main__" ].__settings__
__language__ = __settings__.getLocalizedString # Add-on strings
__string__   = xbmc.getLocalizedString # XBMC strings

FANART = __settings__.getAddonInfo( "fanart" )
#releases icons
MEDIA_PATH = os.path.join( __settings__.getAddonInfo( "path" ), "resources", "media" )

PROFILE_PATH = xbmc.translatePath( __settings__.getAddonInfo( "profile" ) )
DL_INFO_PATH = os.path.join( PROFILE_PATH, "iddl_data" )
if not os.path.exists( DL_INFO_PATH ): os.makedirs( DL_INFO_PATH )
DIALOG_DL_PROGRESS = 'RunScript(%s)' % os.path.join( __settings__.getAddonInfo( "path" ), "resources", "addonAPI", "DialogDLProgress.py" )

xbmc_rev, xbmc_date = xbmc.getInfoLabel( "System.BuildVersion" ), xbmc.getInfoLabel( "System.BuildDate" )
CURRENT_XBMC = "[B]Your current XBMC[/B][CR][B]Version:[/B] %s[CR][B]Compiled:[/B] %s" % ( xbmc_rev, xbmc_date )
UNDER_XBOX = ( os.environ.get( "OS", "xbox" ) == "xbox" )

# used in setAddonInfo
ADDON_PROPERTIES = [ 'broken', 'changelog', 'creator', 'description', 'disclaimer',
    'id', 'name', 'path', 'starrating', 'status', 'summary', 'type', 'version' ]
# used in setAddonInfo
INFOS_VIDEO = [ 'aired', 'album', 'cast', 'castandrole', 'code', 'count', 'credits', 'date',
    'director', 'duration', 'episode', 'genre', 'lastplayed', 'mpaa', 'overlay', 'playcount',
    'plot', 'plotoutline', 'premiered', 'rating', 'season', 'size', 'status', 'studio', 'tagline',
    'title', 'top250', 'tracknumber', 'trailer', 'tvshowtitle', 'votes', 'watched', 'writer', 'year' ]


class _Info:
    def __init__( self, *args, **kwargs ):
        # update dict with our formatted argv
        try: exec "self.__dict__.update(%s)" % ( sys.argv[ 2 ][ 1: ].replace( "&", ", " ), )
        except: print_exc()
        # update dict with custom kwargs
        self.__dict__.update( kwargs )

    def get( self, key, default="" ):
        return self.__dict__.get( key, default )

    def isempty( self ):
        return not bool( self.__dict__ )


class Main:
    def __init__( self ):
        self._parse_argv()
        self._get_settings()

        if not self.args.get( "listurl" ):
            self._add_directory_items()
        else:
            self._add_releases_items()

    def _parse_argv( self ):
        # create the self.args object
        self.args = _Info()

    def _get_settings( self ):
        self.settings = {}

    def addContextMenuAction( self, listitem, c_items=[] ):
        try:
            if os.listdir( DL_INFO_PATH ): c_items += [ ( "Téléchargements en cours...", DIALOG_DL_PROGRESS ) ]
            # ContextMenu: add xbmc trac
            c_items += [ ( "XBMC Trac Timeline", 'RunPlugin(%s?action="\'timeline\'")' % sys.argv[ 0 ] ) ]
            # add ContextMenuitems
            listitem.addContextMenuItems( c_items )#, replaceItems=True )
        except:
            print_exc()
        return listitem

    def setAddonInfo( self, listitem, infoLabels={} ):
        info_labels = {}
        for key, value in infoLabels.items():
            property = ( key, "Addon.%s" % key )[ key.lower() in ADDON_PROPERTIES ]
            if property.lower() not in INFOS_VIDEO:
                listitem.setProperty( property, value )
            else:
                info_labels[ property ] = value
        if info_labels:
            listitem.setInfo( "video", info_labels )
        return listitem

    def _add_directory_items( self ):
        OK = True
        try:
            #Releases (Stable)
            title = "Releases (Stable)"
            icon = XBMC_ICON#"DefaultNetwork.png"
            listitem = xbmcgui.ListItem( title, "", icon )
            listitem.setProperty( "Addon.Name", title )
            listitem.setProperty( "Addon.Creator", "Team XBMC" )
            listitem.setProperty( "Addon.StarRating", "rating5.png" )
            listitem.setProperty( "Addon.Description", CURRENT_XBMC )
            listitem.setProperty( "Addon.Type", "Live / OSX / Win32" )
            listitem.setProperty( "Addon.Version", "Stable" )
            # ContextMenu: add open and visit repo
            if UNDER_XBOX: c_items = []
            else: c_items = [ ( "Visit Official Repo", 'RunPlugin(%s?action="\'visitrepo\'")' % sys.argv[ 0 ] ) ]
            listitem = self.addContextMenuAction( listitem, c_items )
            url = '%s?listurl="%s"&cat="%s"' % ( sys.argv[ 0 ], urllib.quote_plus( repo.releases_url ), title )
            OK = xbmcplugin.addDirectoryItem( handle=int( sys.argv[ 1 ] ), url=url, listitem=listitem, isFolder=True )
            if ( not OK ): raise

            #Nightlies (SVN)
            title = "Nightlies (SVN)"
            icon = XBMC_ICON#"DefaultNetwork.png"
            listitem = xbmcgui.ListItem( title, "", icon )
            listitem.setProperty( "Addon.Name", title )
            listitem.setProperty( "Addon.Creator", "Team XBMC" )
            listitem.setProperty( "Addon.StarRating", "rating4.png" )
            listitem.setProperty( "Addon.Description", CURRENT_XBMC )
            listitem.setProperty( "Addon.Type", "Live / OSX / Win32" )
            listitem.setProperty( "Addon.Version", "SVN" )
            # ContextMenu: add open and visit repo
            if UNDER_XBOX: c_items = []
            else: c_items = [ ( "Visit Official Repo", 'RunPlugin(%s?action="\'visitrepo\'")' % sys.argv[ 0 ] ) ]
            listitem = self.addContextMenuAction( listitem, c_items )
            url = '%s?listurl="%s"&cat="%s"' % ( sys.argv[ 0 ], urllib.quote_plus( repo.nightlies_url ), title )
            OK = xbmcplugin.addDirectoryItem( handle=int( sys.argv[ 1 ] ), url=url, listitem=listitem, isFolder=True )
            if ( not OK ): raise

            #Available Updates, only if new revision is retrieved
            if self._getAvailableUpdates():
                title = __string__( 24043 )
                icon = XBMC_ICON#"DefaultNetwork.png"
                listitem = xbmcgui.ListItem( title, "", icon )
                listitem.setProperty( "Addon.Name", title )
                listitem.setProperty( "Addon.Creator", "Team XBMC" )
                listitem.setProperty( "Addon.StarRating", "rating5.png" )
                listitem.setProperty( "Addon.Description", CURRENT_XBMC )
                listitem.setProperty( "Addon.Type", "OSX / Win32" )
                listitem.setProperty( "Addon.Version", "Stable / SVN" )
                # ContextMenu: add open and visit repo
                c_items = [ ( "Visit Official Repo", 'RunPlugin(%s?action="\'visitrepo\'")' % sys.argv[ 0 ] ) ]
                listitem = self.addContextMenuAction( listitem, c_items )
                url = '%s?listurl="available"&cat="%s"' % ( sys.argv[ 0 ], title )
                OK = xbmcplugin.addDirectoryItem( handle=int( sys.argv[ 1 ] ), url=url, listitem=listitem, isFolder=True )
                if ( not OK ): raise

            if os.listdir( DL_INFO_PATH ):
                # download progress
                title = "Téléchargements en cours"
                icon = "DefaultHardDisk.png"
                listitem = xbmcgui.ListItem( title, "", icon )
                listitem.setProperty( "Addon.Name", title )
                listitem.setProperty( "Addon.StarRating", "rating0.png" )
                listitem.setProperty( "Addon.Description", CURRENT_XBMC )
                listitem = self.addContextMenuAction( listitem, [] )
                url = '%s?action="dlprogress"' % ( sys.argv[ 0 ] )
                OK = xbmcplugin.addDirectoryItem( handle=int( sys.argv[ 1 ] ), url=url, listitem=listitem, isFolder=True )
                if ( not OK ): raise

            ''' BROKEN
            #Unofficial Nightly Builds
            title = "Unofficial Nightly Builds From SVN"
            icon = XBMC_ICON#"DefaultNetwork.png"
            listitem = xbmcgui.ListItem( title, "", icon )
            listitem.setProperty( "Addon.Name", title )
            listitem.setProperty( "Addon.Creator", " " )
            listitem.setProperty( "Addon.StarRating", "rating4.png" )
            listitem.setProperty( "Addon.Description", CURRENT_XBMC )
            listitem.setProperty( "Addon.Type", "All" )
            listitem.setProperty( "Addon.Version", "SVN" )
            if UNDER_XBOX: c_items = []
            else: c_items = [ ( "Visit Unofficial Repo", 'RunPlugin(%s?action="\'visitunorepo\'")' % sys.argv[ 0 ] ) ]
            listitem = self.addContextMenuAction( listitem, c_items )
            url = '%s?listurl="unofficial"&cat="%s"' % ( sys.argv[ 0 ], title )
            OK = xbmcplugin.addDirectoryItem( handle=int( sys.argv[ 1 ] ), url=url, listitem=listitem, isFolder=True )
            if ( not OK ): raise'''

            #browse
            title = "Update from custom build"
            icon = "DefaultHardDisk.png"
            listitem = xbmcgui.ListItem( title, "", icon )
            listitem.setProperty( "Addon.Name", title )
            listitem.setProperty( "Addon.StarRating", "rating0.png" )
            listitem.setProperty( "Addon.Description", CURRENT_XBMC )
            listitem = self.addContextMenuAction( listitem, [] )
            url = '%s?action="browse"' % ( sys.argv[ 0 ] )
            OK = xbmcplugin.addDirectoryItem( handle=int( sys.argv[ 1 ] ), url=url, listitem=listitem, isFolder=True )
            if ( not OK ): raise

        except:
            print_exc()
            OK = False
        self._set_content( OK )

    def _getAvailableUpdates( self ):
        #Available Updates ( only for official repo )
        hasNew = []
        if not UNDER_XBOX:
            try:
                rev = int( re.search( "r(\d+)", xbmc_rev ).group( 1 ) )
                platform = ( "osx", "win32" )[ sys.platform == "win32" ]
                hasNew = repo.getAvailableUpdates( platform, rev )
            except:
                print_exc()
        return hasNew

    def _add_releases_items( self, lasted=False ):
        OK = True
        try:
            url = urllib.unquote_plus( self.args.get( "listurl" ) )
            if url == "unofficial":
                self.releases = repo.getUnofficialBuilds()
                creator = ""
            elif url == "available":
                self.releases = self._getAvailableUpdates()
                creator = "Team XBMC"
            else:
                self.releases = repo.getListing( url )
                creator = "Team XBMC"
            self.releases = sorted( self.releases, key=lambda l: not l[ "isFolder" ] )
            #self.releases.reverse()
            StarRating = 5
            for release in self.releases:
                title = os.path.splitext( release[ "title" ].replace( "-", " " ).replace( "_", " " ) )[ 0 ].strip( "/" )#.replace( ".exe", "" )
                icon = ( XBMC_ICON, "" )[ release[ "isFolder" ] ]
                icon2 = os.path.join( MEDIA_PATH, release[ "icon" ] )
                icon = ( icon, icon2 )[ bool( release[ "icon" ] ) ]
                listitem = xbmcgui.ListItem( title, "", icon )

                infoLabels = { 
                    "Name": title,
                    "Path": release[ "link" ],
                    "Type": release[ "type" ],
                    "Creator": creator,
                    "StarRating": "rating0.png",
                    "Version": release[ "revision" ],
                    "Status": release[ "date" ] or release[ "type" ],
                    }

                isFolder = release[ "isFolder" ]
                desc = ""
                if not isFolder:
                    #if StarRating == 5: desc += "[B]Last Revision:[/B] r%s[CR]" % ( release[ "revision" ] )
                    infoLabels[ "StarRating" ] = "rating%i.png" % StarRating
                    if StarRating > 0: StarRating -= 1

                if release[ "lastplayed" ]:
                    desc += "[B]%s:[/B] %s[CR]" % ( __string__( 21803 ), release[ "lastplayed" ] )
                if release[ "size" ]:
                    desc += "[B]%s:[/B] %s MB[CR]" % ( __string__( 21802 ), str( release[ "size" ]/(1024.0**2) ) )
                #if desc: desc += "[CR]" 
                #desc += CURRENT_XBMC

                infoLabels.update( {
                    "Description": desc, 
                    "Fanart_Image": FANART,
                    "title": title,
                    "plot": desc, 
                    "genre": release[ "type" ],
                    "size": release[ "size" ],
                    "date": release[ "date" ],
                    "year": release[ "year" ],
                    "lastplayed": release[ "lastplayed" ],
                    "filename": release.get( "filename", "" )
                    } )
                listitem = self.setAddonInfo( listitem, infoLabels )

                c_items = []
                if not isFolder:
                    c_items += [ ( "Download", 'RunPlugin(%s?action="\'%s\'")' % ( sys.argv[ 0 ], "DL" ) ) ]
                    if not UNDER_XBOX: c_items += [ ( "Open Release", 'RunPlugin(%s?action="\'open\'")' % sys.argv[ 0 ] ) ]
                    url = '%s?action="%s"' % ( sys.argv[ 0 ], "DL" )
                else:
                    url = '%s?listurl="%s"&cat="%s"' % ( sys.argv[ 0 ], urllib.quote_plus( release[ "link" ] ), release[ "type" ].title() )
                listitem = self.addContextMenuAction( listitem, c_items )

                OK = xbmcplugin.addDirectoryItem( handle=int( sys.argv[ 1 ] ), url=url, listitem=listitem, isFolder=isFolder )
                if ( not OK ): raise

                #if lasted: break
        except:
            print_exc()
            OK = False
        self._set_content( OK, False )

    def _set_content( self, OK, nosort=True ):
        if ( OK ):
            content = ( "addons", "files", "songs", "artists", "albums", "movies", "tvshows", "episodes", "musicvideos" )
            xbmcplugin.setContent( handle=int( sys.argv[ 1 ] ), content=content[ 0 ] )
        self._add_sort_methods( OK, nosort )

    def _add_sort_methods( self, OK, nosort=True ):
        if ( OK ):
            #if nosort:
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_NONE )
            #else:
            #    xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_VIDEO_TITLE )
        self._end_of_directory( OK )

    def _end_of_directory( self, OK ):
        addonWindow( 10001 )
        xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=OK )
