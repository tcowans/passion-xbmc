""" 
   MovieSets Addon Library
   by Frost (passion-xbmc.org)
"""

from sys import argv
from operator import truth as isAlive
from xbmc import getInfoLabel

try: windowId = int( argv[ 2 ] )
except: windowId = 0
windowId = windowId or 10025

#print getInfoLabel( "Window(%i).Property(MovieSets.IsAlive)" % windowId )
#print isAlive( getInfoLabel( "Window(%i).Property(MovieSets.IsAlive)" % windowId ) )

if not isAlive( getInfoLabel( "Window(%i).Property(MovieSets.IsAlive)" % windowId ) ):
    from lib.moviesets import Main
    Main()
