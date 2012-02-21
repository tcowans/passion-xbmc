
import os
import sys
import xbmc
from traceback import print_exc

xbmc.executebuiltin( "SetProperty(script.metadata.actors.isactive,1)" )

try:
    args = ", ".join( sys.argv[ 1: ] )
    if "backend" in args.lower():
        from xbmcaddon import Addon
        ADDON_DIR = Addon( "script.metadata.actors" ).getAddonInfo( "path" )
        xbmc.executebuiltin( "Runscript(%s)" % os.path.join( ADDON_DIR, "resources", "lib", "backend.py" ) )

    elif "homepage=" in args.lower():
        import webbrowser
        webbrowser.open( args.replace( "homepage=", "" ) )
    else:
        from resources.lib.dialoginfo import Main
        Main( args )
except:
    print_exc()

xbmc.executebuiltin( "ClearProperty(script.metadata.actors.isactive)" )
