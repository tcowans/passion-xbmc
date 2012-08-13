
import os
import sys
import urllib

import xbmc
import xbmcgui
import xbmcvfs
import xbmcplugin
from xbmcaddon import Addon

import repoutils

# constants
ADDON      = Addon( "plugin.program.repo.installer" )
ADDON_NAME = ADDON.getAddonInfo( "name" )

#Language = ADDON.getLocalizedString # ADDON strings
LangXBMC = xbmc.getLocalizedString # XBMC strings



class PluginView:
    def __init__( self ):
        listitems = []
        for ID, repo in repoutils.getRepos().items():
            #print repo

            addonID    = repo.get( "addonID" ) or repo[ "id" ]
            playCount  = xbmc.getCondVisibility( "System.HasAddon(%s)" % addonID )
            playCount  = playCount or xbmcvfs.exists( "special://home/addons/%s/addon.xml" % addonID )
            overlay    = ( xbmcgui.ICON_OVERLAY_NONE, xbmcgui.ICON_OVERLAY_WATCHED )[ playCount ]
            Status     = ( "", LangXBMC( 305 ) )[ playCount ]
            infoLabels = {
                "title":     repo[ "title" ],
                "Plot":      repo[ "plot" ],
                "playCount": playCount,
                "overlay":   overlay,
                }

            listitem = xbmcgui.ListItem( repo[ "title" ], "", "DefaultAddonRepository.png" )
            if repo[ "icon" ]: listitem.setThumbnailImage( repo[ "icon" ] )
            if playCount:
                local_icon = xbmc.getInfoLabel( "system.addonicon(%s)" % addonID )
                if xbmcvfs.exists( local_icon ):
                    listitem.setThumbnailImage( local_icon )

            listitem.setInfo( "video", infoLabels )

            listitem.setProperty( "Addon.Name",        repo[ "title" ] )
            listitem.setProperty( "Addon.Version",     repo[ "version" ] )
            listitem.setProperty( "Addon.Summary",     repo[ "plot" ] )
            listitem.setProperty( "Addon.Description", repo[ "plot" ] )
            listitem.setProperty( "Addon.Type",        LangXBMC( 24011 ) )
            listitem.setProperty( "Addon.Creator",     repo[ "author" ] )
            listitem.setProperty( "Addon.Disclaimer",  "" )
            listitem.setProperty( "Addon.Changelog",   "" )
            listitem.setProperty( "Addon.ID",          addonID )
            listitem.setProperty( "Addon.Status",      Status )
            listitem.setProperty( "Addon.Broken",      "" )
            listitem.setProperty( "Addon.Path",        "" )
            listitem.setProperty( "Addon.Icon",        repo[ "icon" ] )

            c_items  = [ ( "Update Local Repos", "UpdateAddonRepos" ) ]
            if repo[ "url" ]:
                uri = '%s?webbrowser=%s' % ( sys.argv[ 0 ], urllib.quote_plus( repo[ "url" ] ) )
                c_items += [ ( "Visit Online Repo", "RunPlugin(%s)" % uri ) ]
            uri = '%s?webbrowser=%s' % ( sys.argv[ 0 ], urllib.quote_plus( "http://wiki.xbmc.org/index.php?title=Unofficial_Add-on_Repositories" ) )
            c_items += [ ( "Unofficial Add-on Repositories", "RunPlugin(%s)" % uri ) ]

            #if playCount: # pas bon xbmc plante
            #    c_items += [ ( "Browse Repo", 'ActivateWindow(AddonBrowser,addons://%s,return)' % addonID ) ]
            listitem.addContextMenuItems( c_items, True )

            url = '%s?install=%s' % ( sys.argv[ 0 ], ID )
            listitem = ( url, listitem, False )
            listitems.append( listitem )

        ok = self._add_directory_items( listitems )

        self._set_content( ok )

    def _add_directory_items( self, listitems ):
        """ addDirectoryItems(handle, items [,totalItems])
            handle      : integer - handle the plugin was started with.
            items       : List - list of (url, listitem[, isFolder]) as a tuple to add.
            totalItems  : [opt] integer - total number of items that will be passed.(used for progressbar)
        """
        return xbmcplugin.addDirectoryItems( int( sys.argv[ 1 ] ), listitems, len( listitems ) )

    def _set_content( self, succeeded, content="addons", sort=True ):
        if ( succeeded ):
            xbmcplugin.setContent( int( sys.argv[ 1 ] ), content )
        if sort:
            self._add_sort_methods( succeeded )
        else:
            self._end_of_directory( succeeded )

    def _add_sort_methods( self, succeeded ):
        if ( succeeded ):
            #xbmcplugin.addSortMethod( int( sys.argv[ 1 ] ), xbmcplugin.SORT_METHOD_UNSORTED )
            xbmcplugin.addSortMethod( int( sys.argv[ 1 ] ), xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE )
        self._end_of_directory( succeeded )

    def _end_of_directory( self, succeeded ):
        xbmcplugin.endOfDirectory( int( sys.argv[ 1 ] ), succeeded )


print sys.argv
if not sys.argv[ 2 ]:
    PluginView()

elif "install=" in sys.argv[ 2 ]:
    # install repo
    ID = sys.argv[ 2 ].split( "=" )[ -1 ]
    repoutils.installRepo( ID )

elif "webbrowser=" in sys.argv[ 2 ]:
    url = sys.argv[ 2 ].split( "=" )[ -1 ]
    url = urllib.unquote_plus( url )
    import webbrowser
    webbrowser.open( url )
