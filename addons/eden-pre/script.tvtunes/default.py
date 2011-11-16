# -*- coding: utf-8 -*-

import os
import sys

import xbmc
from xbmcaddon import Addon


SCRIPT = None
ARGS = "".join( sys.argv[ 1:2 ] )

if "backend" in ARGS.lower():
    if xbmc.getInfoLabel( "Window(10025).Property(TvTunesIsRunning)" ) != "true":
        SCRIPT = "tunesplayer"
else:
    SCRIPT = "tvtunes"

if SCRIPT:
    xbmc.executebuiltin( 'RunScript(%s.py,%s)' % ( 
        os.path.join( Addon( 'script.tvtunes' ).getAddonInfo( 'path' ), "resources", "lib", SCRIPT ),
        ARGS ) )
