
import os
import time
import random

import xbmc
import xbmcvfs
from xbmcaddon import Addon

Addon = Addon( "script.xbmc.intro.movie" )


if xbmc.getCondVisibility( '!Window.IsVisible(Home)' ):
    ReplaceWindowHome = xbmc.getCondVisibility( '!Window.IsVisible(Programs)' )
    print "XBMC Intro Movie"

    intros_dir = os.path.join( Addon.getAddonInfo( "path" ), "resources", "intros" )
    intro = Addon.getSetting( "intro" )

    if Addon.getSetting( "use_custom_intro" ) == "true":
        c_intro = Addon.getSetting( "path_custom_intro" )
        if c_intro and xbmcvfs.exists( c_intro ):
            intro = c_intro

    if intro == "Random":
        intros = os.listdir( intros_dir )
        random.shuffle( intros )
        intro = random.choice( intros )

    player = xbmc.Player()
    player.play( os.path.join( intros_dir, intro ) )

    if ReplaceWindowHome:
        xbmc.sleep( 1000 )

        while player.isPlaying():
            #continue
            time.sleep( .2 )

        xbmc.executebuiltin( "ReplaceWindow(Home)" )

        xbmc.sleep( 1000 )
