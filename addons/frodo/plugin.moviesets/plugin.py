
import os
import sys

import xbmc
import xbmcvfs
from xbmcaddon import Addon

from resources.lib.log import logAPI
LOGGER = logAPI()

#print xbmc.executeJSONRPC( '{ "jsonrpc": "2.0", "method": "JSONRPC.Version", "id": 1 }' )
print sys.argv


def xbmcvfs_copytree( src, dst ):
    if not xbmcvfs.exists( dst ): xbmcvfs.mkdirs( dst )
    dirs, files = xbmcvfs.listdir( src )

    for file in files:
        srcname = os.path.join( src, file )
        dstname = os.path.join( dst, file )
        ok = xbmcvfs.copy( srcname, dstname )
        print "%r xbmcvfs.copy( %r, %r )" % ( bool( ok ), srcname, dstname )

    for dir in dirs:
        srcname = os.path.join( src, dir )
        dstname = os.path.join( dst, dir )
        xbmcvfs_copytree( srcname, dstname )


if not str( sys.argv[ 1 ] ).strip( "-" ).isdigit():
    if str( sys.argv[ 1 ] ) == "manager":
        import xbmcgui
        choice = [
            " ".join( [ xbmc.getLocalizedString( 15019 ), xbmc.getLocalizedString( 20342 ) ] ),
            " ".join( [ xbmc.getLocalizedString( 15015 ), xbmc.getLocalizedString( 20342 ) ] )
            ]
        selected = xbmcgui.Dialog().select( ", ".join( sys.argv[ 2: ] ), choice )
        if selected == 0: sys.argv[ 1 ] = "addmovie"
        if selected == 1: sys.argv[ 1 ] = "remmovie"

    if str( sys.argv[ 1 ] ) in [ "addmovie", "remmovie", "newset", "remset" ]:
        from resources.lib.dialog_select import Main
        Main()

    elif str( sys.argv[ 1 ] ) == "playset":
        # PLAY ALL MOVIES IN SET
        # create our playlist
        playlist = xbmc.PlayList( xbmc.PLAYLIST_VIDEO )
        # clear any possible entries
        playlist.clear()
        for movie in sys.argv[ 2 ].replace( "stack://", "" ).split( " ; " ):
            playlist.add( movie )
        xbmc.Player().play( playlist )

    elif str( sys.argv[ 1 ] ) == "edittitle":
        # EDIT TITLE OF SET
        idSet = sys.argv[ 2 ]
        title = ", ".join( sys.argv[ 3: ] )

        kb = xbmc.Keyboard( title, xbmc.getLocalizedString( 16105 ) )
        kb.doModal()
        if kb.isConfirmed():
            new_title = kb.getText()

            if new_title and new_title != title:
                import xbmcgui
                def _unicode( text, encoding="utf-8" ):
                    try: text = unicode( text, encoding )
                    except: pass
                    return text

                if xbmcgui.Dialog().yesno( "Confirm new title", "New: %s" % _unicode( new_title ), "Old: %s" % _unicode( title ), "", xbmc.getLocalizedString( 222 ), xbmc.getLocalizedString( 186 ) ):
                    from resources.lib.videolibrary import editMovieSetTitle
                    refresh = editMovieSetTitle( new_title, idSet )
                    if refresh: xbmc.executebuiltin( "Container.Refresh" )

    elif str( sys.argv[ 1 ] ) in [ "setthumb", "setfanart" ]:
        # SET FANART OR THUMB
        refresh = False
        xbmc.executebuiltin( 'ActivateWindow(busydialog)' )
        try:
            from resources.lib.dialogs import browser
            idset = sys.argv[ 2 ]
            heading = ", ".join( sys.argv[ 3: ] )
            type = str( sys.argv[ 1 ] ).replace( "set", "" )

            # **attrs: Set movieset fanart or Set movieset thumb
            refresh = browser( heading=heading, idset=idset, type=type )
        except:
            LOGGER.error.print_exc()
        xbmc.executebuiltin( 'Dialog.Close(busydialog,true)' )
        if refresh: xbmc.executebuiltin( "Container.Refresh" )

    elif str( sys.argv[ 1 ] ) in [ "setwatched", "unwatched" ]:
        # TOGGLE WATCHED
        refresh = False
        xbmc.executebuiltin( 'ActivateWindow(busydialog)' )
        try:
            from resources.lib.videolibrary import setMovieSetPlayCount

            if str( sys.argv[ 1 ] ) == "setwatched": playcount = 1
            if str( sys.argv[ 1 ] ) == "unwatched":  playcount = 0
            refresh = setMovieSetPlayCount( sys.argv[ 2 ], playcount )
        except:
            LOGGER.error.print_exc()
        xbmc.executebuiltin( 'Dialog.Close(busydialog,true)' )
        if refresh: xbmc.executebuiltin( "Container.Refresh" )

    elif str( sys.argv[ 1 ] ) == "setconfluence":
        ADDON_DIR  = Addon( "plugin.moviesets" ).getAddonInfo( "path" )
        addon_skin = os.path.join( ADDON_DIR, "resources", "skins", xbmc.getSkinDir() )
        if xbmcvfs.exists( addon_skin ):
            xbmcvfs_copytree( addon_skin, xbmc.translatePath( "special://skin" ) )
            xbmc.executebuiltin( 'ReloadSkin()' )

    elif str( sys.argv[ 1 ] ) == "libraryxml":
        ADDON_DIR = Addon( "plugin.moviesets" ).getAddonInfo( "path" )
        xbmcvfs_copytree( os.path.join( ADDON_DIR, "system" ), xbmc.translatePath( "special://xbmc/system" ) )

else:
    if not sys.argv[ 2 ]:
        BLT = 'SetProperty(moviesets.refresh,1,Videos)'
        from resources.lib.plugin_view import PluginView
        PluginView()

    else:
        idset = sys.argv[ 2 ].split( "=" )[ -1 ]
        if idset != "-1": BLT = "Container.Update(videodb://1/7/%s/)" % idset
        else: BLT = "RunScript(plugin.moviesets,playset,%s)" % xbmc.getInfoLabel( "ListItem.Property(playset)" )
    xbmc.executebuiltin( BLT )
