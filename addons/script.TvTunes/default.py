# -*- coding: utf-8 -*-
import sys
import os
import xbmcaddon
__settings__ = xbmcaddon.Addon( "script.TvTunes" )
RESOURCES_PATH = os.path.join( os.getcwd() , "resources" )
sys.path.append( RESOURCES_PATH )
try:
    # parse sys.argv for params
    try:params = dict( arg.split( "=" ) for arg in sys.argv[ 1 ].split( "&" ) )
    except:params =  dict( sys.argv[ 1 ].split( "=" ))
except:
    # no params passed
    params = {}   
if params.get("backend", False ): 

    loop = __settings__.getSetting("loop")
    downvolume = __settings__.getSetting("downvolume")
    if xbmc.getInfoLabel( "Window(10025).Property(TvTunesIsRunning)" ) != "true":
        xbmc.executebuiltin('XBMC.RunScript(%s,loop=%s&downvolume=%s)' % (os.path.join( RESOURCES_PATH , "tvtunes_backend.py"), loop , int( float( downvolume ) ) ))
else: 
    print " %s v%s" % ( __settings__.getAddonInfo("id") , __settings__.getAddonInfo("version") )
    import tvtunes_scraper