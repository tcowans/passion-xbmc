
import re
import time

import xbmc
import xbmcgui

skinId   = xbmc.getSkinDir()
skinName = xbmc.getInfoLabel( "System.AddonTitle(%s)" % skinId )
settings = "special://profile/guisettings.xml"

if xbmcgui.Dialog().yesno( skinName, "Confirm resetting of all skin settings...", "Are you sure?" ):
    dp = xbmcgui.DialogProgress()
    dp.create( skinName )
    try:
        settings = re.compile( '<setting type=".+?" name="%s.(.+?)">' % skinId ).findall( open( settings ).read() )
        for count, setting in enumerate( sorted( settings ) ):
            pct = float( count + 1 ) * ( 100.0 / len( settings ) )
            dp.update( int( pct ), "Resetting settings...", "Setting: %s" % setting, "Please wait..." )
            xbmc.executebuiltin( "Skin.Reset(%s)" % setting )
            time.sleep( .05 )
    except:
        pass
    dp.close()
