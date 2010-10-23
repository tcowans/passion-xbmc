# -*- coding: utf-8 -*-
import sys
import os

RESOURCES_PATH = os.path.join( os.getcwd() , "resources" )
sys.path.append( RESOURCES_PATH )
try:
    # parse sys.argv for params
    params = dict( arg.split( "=" ) for arg in sys.argv[ 1 ].split( "&" ) )
except:
    # no params passed
    params = {}
if params.get("backend", False ): xbmc.executebuiltin('XBMC.RunScript(%s)' % os.path.join( RESOURCES_PATH , "tvtunes_backend.py"))
else: 
    import xbmcaddon
    __settings__ = xbmcaddon.Addon( "script.TvTunes" )     
    print " %s v%s" % ( __settings__.getAddonInfo("id") , __settings__.getAddonInfo("version") )
    import tvtunes_scraper