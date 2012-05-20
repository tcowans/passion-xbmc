

import sys
import xbmc

xbmc.executebuiltin( "SetProperty(python,%s on %s)" % ( sys.version, sys.platform ) )

json = eval( xbmc.executeJSONRPC( '{ "jsonrpc": "2.0", "method": "JSONRPC.Version", "id": 1 }' ) )
xbmc.executebuiltin( "SetProperty(jsonrpc,%s Version %i)" % ( json[ "jsonrpc" ], json[ "result" ][ "version" ] ) )


def set_skin_info():
    try:
        import re
        # get source
        addon_xml = xbmc.translatePath( "special://skin/addon.xml" )
        xml = open( addon_xml, "r" ).read()
        # set addon.xml info into dictionary
        regexp = "<addon.+?id=\"([^\"]+)\".+?version=\"([^\"]+)\".+?name=\"([^\"]+)\".+?provider-name=\"([^\"]+)\".*?>"
        id, version, name, author = re.search( regexp, xml, re.DOTALL ).groups( 1 )
        xbmc.executebuiltin( "SetProperty(skin.name,%s)" % name )
        xbmc.executebuiltin( "SetProperty(skin.version,%s)" % version )
        xbmc.executebuiltin( "SetProperty(skin.author,%s)" % author.replace( ",", " -" ) )
        #print [ id, version, name, author ]
    except:
        from traceback import print_exc
        print_exc()

set_skin_info()
