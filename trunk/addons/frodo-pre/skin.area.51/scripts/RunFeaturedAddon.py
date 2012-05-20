
import sys
import xbmc

addonID     = sys.argv[ 1 ]
strHasAddon = "System.HasAddon(%s)" % addonID
HasAddon    = xbmc.getCondVisibility( strHasAddon )

if not HasAddon:
    install = None
    from installer import dependencies
    conn  = dependencies.openDB()
    try:
        sql = "SELECT name, path, addonID, version FROM addon WHERE addonID='%s'" % addonID
        name, url, addonID, version = conn.execute( sql ).fetchone()
        install = [ ( name, url, addonID, version ) ]
    except Exception, e:
        print repr( e )
    dependencies.closeDB( conn )

    if not install: raise Exception( repr( globals() ) )
    from xbmcgui import Dialog
    if Dialog().yesno( xbmc.getLocalizedString( 24076 ), xbmc.getLocalizedString( 24100 ), xbmc.getLocalizedString( 24101 ), name ):
        ok = dependencies.Main( install )
        HasAddon = xbmc.getCondVisibility( strHasAddon )

if HasAddon:
    xbmc.executebuiltin( "RunAddon(%s,return)" % addonID )
