# -*- coding: utf-8 -*-

# Modules General
from re import findall

# Modules XBMC
from xbmcgui import Window, getCurrentWindowDialogId

# Modules Custom
from RSSUserData import parse_xml


class Main:
    # grab the 1115 or 1116 window
    try: wid = getCurrentWindowDialogId()
    except: wid = 11115
    WINDOW = Window( wid )

    def __init__( self ):
        self._clear_properties()
        self._set_properties()

    def _clear_properties( self ):
        # Clear Feeds Properties
        for count in range( 1, 31 ):
            self.WINDOW.clearProperty( "feeds.%d.name" % ( count + 1, ) )
            self.WINDOW.clearProperty( "feeds.%d.path" % ( count + 1, ) )

    def _set_properties( self ):
        # recupere les rss existant de l'user
        for count, feeds in enumerate( sorted( parse_xml().items(), key=lambda x: str( x[ 0 ].zfill( 3 ) ) ) ):
            idset, feeds = feeds
            # join par une virgule les liens. on va utiliser une virgule comme ceci " , " pour faire la différence des autre virgule dans les liens
            lien = " , ".join( feed[ "feed" ] for feed in feeds[ "feed" ] )
            #print "feeds.%d.path" % ( count + 1 ), lien
            # name est le nom du site, car l'attribut name est pas supporter pour le moment dans le rssfeeds.xml
            name = " / ".join( set( findall( 'http://(.*?)/', lien ) ) )
            #print "feeds.%d.name" % ( count + 1 ), name

            # set window properties
            self.WINDOW.setProperty( "feeds.%d.name" % ( count + 1, ), name )
            self.WINDOW.setProperty( "feeds.%d.path" % ( count + 1, ), lien )


if ( __name__ == "__main__" ):
    Main()
