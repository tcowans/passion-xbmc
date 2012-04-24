
import os
import time
import random

import xbmc
import xbmcgui
import xbmcvfs
from xbmcaddon import Addon

Addon = Addon( "script.xbmc.intro.movie" )


isplayed = xbmc.getInfoLabel( "Window(Home).Property(intro.isplayed)" ).lower() == "true"
winPrograms = xbmc.getCondVisibility( 'Window.IsVisible(Programs)' )

if not isplayed or winPrograms:
    ReplaceWindowHome = not winPrograms
    print "XBMC Intro Movie"

    intros_dir = os.path.join( Addon.getAddonInfo( "path" ), "resources", "intros" )
    intro = Addon.getSetting( "intro" )

    if Addon.getSetting( "use_custom_intro" ) == "true":
        c_intro = Addon.getSetting( "path_custom_intro" )
        if c_intro and xbmcvfs.exists( c_intro ):
            intro = c_intro

    if intro == "Random":
        intros = os.listdir( intros_dir )
        last = Addon.getSetting( "last_random" )
        if last and last in intros:
            del intros[ intros.index( last ) ]
        random.shuffle( intros )
        intro = random.choice( intros )
        Addon.setSetting( "last_random", intro )

    player = xbmc.Player()
    player.play( os.path.join( intros_dir, intro ) )
    xbmcgui.Window( 10000 ).setProperty( "intro.isplayed", "true" )

    if ReplaceWindowHome:
        xbmc.sleep( 1000 )

        while player.isPlaying():
            #continue
            time.sleep( .2 )

        xbmc.executebuiltin( "ReplaceWindow(Home)" )

        xbmc.sleep( 1000 )
