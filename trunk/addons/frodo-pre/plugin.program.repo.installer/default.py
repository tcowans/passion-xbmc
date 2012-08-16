
import os
import sys
import urllib
from traceback import print_exc

import xbmc
import xbmcgui
import xbmcvfs
import xbmcplugin
from xbmcaddon import Addon

import repoutils as utils

# constants
ADDON      = Addon( "plugin.program.repo.installer" )
ADDON_NAME = ADDON.getAddonInfo( "name" )

#Language = ADDON.getLocalizedString # ADDON strings
LangXBMC = xbmc.getLocalizedString # XBMC strings


class PluginView:
    def __init__( self ):
        listitems = []
        for ID, repo in utils.getRepos().items():
            if ID == "*": continue
            #print repo

            addonID    = repo.get( "addonID" ) or repo[ "id" ]
            playCount  = xbmc.getCondVisibility( "System.HasAddon(%s)" % addonID )
            playCount  = playCount or xbmcvfs.exists( "special://home/addons/%s/addon.xml" % addonID )
            infoLabels = { "title": repo[ "title" ], "Plot": repo[ "plot" ], "playCount": playCount,
                "overlay": ( xbmcgui.ICON_OVERLAY_NONE, xbmcgui.ICON_OVERLAY_WATCHED )[ playCount ],
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
            listitem.setProperty( "Addon.Status",      ( "", LangXBMC( 305 ) )[ playCount ] )
            listitem.setProperty( "Addon.Broken",      "" )
            listitem.setProperty( "Addon.Path",        "" )
            listitem.setProperty( "Addon.Icon",        repo[ "icon" ] )

            url = '%s?info=%s' % ( sys.argv[ 0 ], ID )
            c_items  = [ ( LangXBMC( 24003 ), 'RunPlugin(%s)' % url ) ]
            c_items += [ ( "Update Local Repos", "UpdateAddonRepos" ) ]
            if repo[ "url" ]: c_items += [ ( "Visit Online Repo", "RunPlugin(%s?webbrowser=%s)" % ( sys.argv[ 0 ], urllib.quote_plus( repo[ "url" ] ) ) ) ]
            c_items += [ ( "Unofficial Add-on Repositories", "RunPlugin(%s?webbrowser=%s)" % ( sys.argv[ 0 ], urllib.quote_plus( "http://wiki.xbmc.org/index.php?title=Unofficial_Add-on_Repositories" ) ) ) ]

            listitem.addContextMenuItems( c_items, True )

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

    def _set_content( self, succeeded, content="addons" ):
        if ( succeeded ):
            xbmcplugin.setContent( int( sys.argv[ 1 ] ), content )
        self._add_sort_methods( succeeded )

    def _add_sort_methods( self, succeeded ):
        if ( succeeded ):
            #xbmcplugin.addSortMethod( int( sys.argv[ 1 ] ), xbmcplugin.SORT_METHOD_UNSORTED )
            xbmcplugin.addSortMethod( int( sys.argv[ 1 ] ), xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE )
        self._end_of_directory( succeeded )

    def _end_of_directory( self, succeeded ):
        xbmcplugin.endOfDirectory( int( sys.argv[ 1 ] ), succeeded )


class AddonInfo( xbmcgui.WindowXMLDialog ):
    def __init__( self, *args, **kwargs ):
        self.ID   = kwargs[ "ID" ]
        self.repo = utils.loadRepos()[ 0 ][ self.ID ]
        utils.fixeDialogAddonInfo()

    def onInit( self ):
        try:
            self.addonID = self.repo.get( "addonID" ) or self.repo[ "id" ]
            playCount    = xbmc.getCondVisibility( "System.HasAddon(%s)" % self.addonID )
            playCount    = playCount or xbmcvfs.exists( "special://home/addons/%s/addon.xml" % self.addonID )

            listitem = xbmcgui.ListItem( self.repo[ "title" ], "", "DefaultAddonRepository.png" )
            if self.repo[ "icon" ]: listitem.setThumbnailImage( self.repo[ "icon" ] )
            if playCount:
                local_icon = xbmc.getInfoLabel( "system.addonicon(%s)" % self.addonID )
                if xbmcvfs.exists( local_icon ):
                    listitem.setThumbnailImage( local_icon )

            listitem.setProperty( "Addon.Name",        self.repo[ "title" ] )
            listitem.setProperty( "Addon.Version",     self.repo[ "version" ] )
            listitem.setProperty( "Addon.Summary",     self.repo[ "plot" ] )
            listitem.setProperty( "Addon.Description", self.repo[ "plot" ] )
            listitem.setProperty( "Addon.Type",        LangXBMC( 24011 ) )
            listitem.setProperty( "Addon.Creator",     self.repo[ "author" ] )
            listitem.setProperty( "Addon.Disclaimer",  "" )
            listitem.setProperty( "Addon.Changelog",   "" )
            listitem.setProperty( "Addon.ID",          self.addonID )
            listitem.setProperty( "Addon.Status",      ( "", LangXBMC( 305 ) )[ playCount ] )
            listitem.setProperty( "Addon.Broken",      "" )
            listitem.setProperty( "Addon.Path",        "" )
            listitem.setProperty( "Addon.Icon",        self.repo[ "icon" ] )

            self.addItem( listitem )

            #set label button
            label6 = ( LangXBMC( 24038 ), LangXBMC( 1024 ) )[ playCount ]
            self.getControl( 6 ).setLabel( label6 )
            self.getControl( 10 ).setLabel( "Homepage" )

            # desable controls
            #self.getControl( 6 ).setEnabled( playCount )
            for id in [ 7, 8, 9, 11 ]:
                self.getControl( id ).setEnabled( 0 )
        except:
            print_exc()

    def onFocus( self, controlID ):
        pass

    def onClick( self, controlID ):
        try:
            if controlID == 6:
                # install repo
                self._close_dialog()
                if self.getControl( 6 ).getLabel() == LangXBMC( 24038 ):
                    utils.installRepo( self.ID )

                elif xbmc.getCondVisibility( "System.HasAddon(%s)" % self.addonID ):
                    xbmc.executebuiltin( 'ActivateWindow(AddonBrowser,addons://%s,return)' % self.addonID )

            elif controlID == 10:
                import webbrowser
                webbrowser.open( self.repo[ "url" ] )

        except:
            print_exc()

    def onAction( self, action ):
        if action in [ 9, 10, 92, 117 ]:
            self._close_dialog()

    def _close_dialog( self, t=500 ):
        self.close()
        if t: xbmc.sleep( t )

        
        
print sys.argv
if not sys.argv[ 2 ]:
    PluginView()

elif "info=" in sys.argv[ 2 ]:
    ai = AddonInfo( "DialogAddonInfo.xml", ADDON.getAddonInfo( "path" ), ID=sys.argv[ 2 ].split( "=" )[ -1 ] )
    ai.doModal()
    del ai

elif "webbrowser=" in sys.argv[ 2 ]:
    import webbrowser
    webbrowser.open( urllib.unquote_plus( sys.argv[ 2 ].split( "=" )[ -1 ] ) )
