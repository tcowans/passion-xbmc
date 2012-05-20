
import os
import re
import sys
import random
from traceback import print_exc

import xbmc
import xbmcgui

ADDONS_DB = xbmc.translatePath( "special://Database/Addons15.db" )


class Main:
    # grab the home window
    WINDOW = xbmcgui.Window( 10000 )

    def __init__( self ):
        # parse argv for any preferences
        self._parse_argv()
        # clear properties
        self._clear_properties()
        #Frost: xbmc crash on my system winxp, nightly build
        self._fetch_addon_info() # ok I rewrited this function now work correctly (don't use xbmcaddon for get object)
        self._fetch_featured_addon_info()

    def _parse_argv( self ):
        # default params
        params = {}
        # parse sys.argv for params
        try: params = dict( arg.split( "=" ) for arg in sys.argv[ 1 ].split( "&" ) )
        except: pass
        # set our preferences
        self.LIMIT = int( params.get( "limit", "10" ) )

    def _clear_properties( self ):
        # reset totals property for visible condition
        self.WINDOW.clearProperty( "RandomAddon.Count" )
        self.WINDOW.clearProperty( "FeaturedAddon.Count" )
        # we clear title for visible condition
        for count in range( self.LIMIT ):
            # set base property
            r_prop = "RandomAddon.%d." % ( count + 1 )
            f_prop = "FeaturedAddon.%d." % ( count + 1 )
            for prop in [ "Title", "Summary", "Author", "Version", "Fanart", "Thumb", "Type", "Path", "Url", "HasAddon", "Disclaimer", "Description" ]:
                self.WINDOW.clearProperty( r_prop + prop )
                self.WINDOW.clearProperty( f_prop + prop )

    def _fetch_featured_addon_info( self ):
        try:
            addons = []
            conn = None
            try:
                import sqlite3
                # connect to Addons database
                conn = sqlite3.connect( ADDONS_DB, check_same_thread=False )
                sql = """SELECT addon.* FROM addon WHERE addon.type IN ('xbmc.python.script', 'xbmc.python.pluginsource') AND addon.addonID NOT IN (SELECT broken.addonID FROM broken) AND addon.addonID NOT IN (SELECT disabled.addonID FROM disabled)"""
                #print sql
                addons = conn.execute( sql ).fetchall()
            except:
                print_exc()
            if hasattr( conn, "close" ):
                # close database
                conn.close()

            # get total value
            self.WINDOW.setProperty( "FeaturedAddon.Count", str( len( addons ) ) )
            # Shuffle addons in place.
            random.shuffle( addons )
            # select a random xml
            addons = random.sample( addons, self.LIMIT )
            #print "Addons: %r" % ( addons )
            # addon: [(0, 'id'), (1, 'type'), (2, 'name'), (3, 'summary'), (4, 'description'), (5, 'stars'), (6, 'path'), (7, 'addonID'), (8, 'icon'), (9, 'version'), (10, 'changelog'), (11, 'fanart'), (12, 'author'), (13, 'disclaimer'), (14, 'minversion')]
            for count, addon in enumerate( addons ):
                #print count+1, addon
                # set base property
                b_property = "FeaturedAddon.%d." % ( count+1 )
                # set properties
                self.WINDOW.setProperty( b_property + "Title",       addon[ 2 ] )
                self.WINDOW.setProperty( b_property + "Summary",     addon[ 3 ] )
                self.WINDOW.setProperty( b_property + "Description", addon[ 4 ] )#.strip().strip( "\n" ).strip() )
                self.WINDOW.setProperty( b_property + "Disclaimer",  addon[ 13 ] )
                self.WINDOW.setProperty( b_property + "Author",      addon[ 12 ] )
                self.WINDOW.setProperty( b_property + "Version",     addon[ 9 ] )
                self.WINDOW.setProperty( b_property + "Fanart",      addon[ 11 ] )
                self.WINDOW.setProperty( b_property + "Thumb",       addon[ 8 ] )
                self.WINDOW.setProperty( b_property + "Type",        addon[ 1 ] )
                self.WINDOW.setProperty( b_property + "Path",        addon[ 7 ] )
                self.WINDOW.setProperty( b_property + "Url",         addon[ 6 ] )
                self.WINDOW.setProperty( b_property + "HasAddon",    str( xbmc.getCondVisibility( "System.HasAddon(%s)" % addon[ 7 ] ) ) )
                #print addon[ 6 ]
        except:
            print_exc()

    def _fetch_addon_info( self ):
        try:
            from glob import glob
            from locale import getdefaultlocale
            #get lang info for getting summary
            g_langInfo = str( getdefaultlocale() )[ 2:4 ] or "en"
            # list the contents of the addons folder and get addons listing
            addons =  glob( os.path.join( xbmc.translatePath( 'special://home/addons' ), "*", "addon.xml" ) )
            addons += glob( os.path.join( xbmc.translatePath( 'special://xbmc/addons' ), "*", "addon.xml" ) )
            # get total value
            self.WINDOW.setProperty( "RandomAddon.Count", str( len( addons ) ) )
            # count thru our addons
            count = 0
            while count < self.LIMIT:
                # check if we don't run out of items before LIMIT is reached
                if len( addons ) == 0:
                    break
                # Shuffle addons in place.
                random.shuffle( addons )
                # select a random xml
                addon_xml = random.choice( addons )
                # remove the xml from our list
                addons.remove( addon_xml )
                # read xml
                str_xml = open( addon_xml ).read()
                # find plugins and scripts only
                if re.search( 'point="xbmc.python.(script|pluginsource)"', str_xml ):
                    count += 1
                    # set base property
                    b_property = "RandomAddon.%d." % ( count )
                    # get summary
                    summary = re.search( '<summary.*?lang="[%s|en]">(.*?)</summary>' % g_langInfo, str_xml, re.S )
                    summary = summary or re.search( '<summary>(.*?)</summary>', str_xml, re.S )
                    if summary: summary = summary.group( 1 )
                    else: summary = ""
                    # set properties
                    self.WINDOW.setProperty( b_property + "Summary",  summary )
                    self.WINDOW.setProperty( b_property + "Title",    re.search( '<addon.*?name="(.*?)"', str_xml, re.S ).group( 1 ) )
                    self.WINDOW.setProperty( b_property + "Author",   re.search( '<addon.*?provider-name="(.*?)"', str_xml, re.S ).group( 1 ) )
                    self.WINDOW.setProperty( b_property + "Version",  re.search( '<addon.*?version="(.*?)"', str_xml, re.S ).group( 1 ) )
                    self.WINDOW.setProperty( b_property + "Fanart",   addon_xml.replace( 'addon.xml', 'fanart.jpg' ) )
                    self.WINDOW.setProperty( b_property + "Thumb",    addon_xml.replace( 'addon.xml', 'icon.png' ) )
                    self.WINDOW.setProperty( b_property + "Type",     "".join( re.findall( '<provides>(.*?)</provides>', str_xml ) ) or "executable" )
                    self.WINDOW.setProperty( b_property + "Path",     re.search( '<addon.*?id="(.*?)"', str_xml, re.S ).group( 1 ) )
                    self.WINDOW.setProperty( b_property + "Url",      "" )
                    self.WINDOW.setProperty( b_property + "HasAddon", "1" )
                    #
                    #print "Addon: %r" % self.WINDOW.getProperty( b_property + "Path" )
        except:
            print_exc()
        #print locals()


if ( __name__ == "__main__" ):
    Main()
    