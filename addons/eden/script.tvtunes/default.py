# -*- coding: utf-8 -*-

import os
import sys

import xbmc
from xbmcaddon import Addon


SCRIPT = None
ARGS = "".join( sys.argv[ 1:2 ] )
ADDON = Addon( 'script.tvtunes' )

if "backend" in ARGS.lower():
    if xbmc.getInfoLabel( "Window(10025).Property(TvTunesIsRunning)" ).lower() != "true":
        SCRIPT = ( "tvtunes_backend", "tunesplayer" )[ ADDON.getSetting( "useplayerv2" ).lower() == "true" ]
else:
    SCRIPT = "tvtunes"

if SCRIPT:
    xbmc.executebuiltin( 'RunScript(%s.py,%s)' % ( 
        os.path.join( ADDON.getAddonInfo( 'path' ), "resources", "lib", SCRIPT ),
        ARGS ) )
