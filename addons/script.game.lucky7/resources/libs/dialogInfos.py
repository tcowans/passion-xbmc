
#Modules general
import os
import sys
from traceback import print_exc

import elementtree.ElementTree as ET

#modules XBMC
import xbmc
import xbmcgui

#modules custom
from utilities import *


_ = sys.modules[ "__main__" ].__language__

KEYMAP = sys.modules[ "__main__" ].KEYMAP


class DialogInfos( xbmcgui.WindowXMLDialog ):
    def __init__( self, *args, **kwargs ):
        xbmcgui.WindowXMLDialog.__init__( self, *args, **kwargs )
        self._close_game = kwargs[ "close_game" ]

        self.winners = []
        if os.path.isfile( WINNER_JACKPOT ):
            try:
                f = open( WINNER_JACKPOT, "rb" )
                self.winners = sorted( load( f ), reverse=True,
                    key=lambda id: ( int( id[ 4 ] ), int( id[ 4 ] ) / int( id[ 2 ] ), int( id[ 3 ] ) > int( id[ 4 ] ) )
                    )
                f.close()
            except:
                self.winners = []
                print_exc()
        
        try:
            tree = open( FILE_KEYMAP_INFOS )
            self.KeymapInfos = ET.parse( tree ).getroot()
            tree.close()
        except:
            self.KeymapInfos = None
            print_exc()

        self.dialog_is_ok = False

    def onInit( self ):
        if not self.dialog_is_ok:
            try:
                xbmcgui.lock()
                self.set_bonus()
                self.set_keymap_infos()
                self.set_winner_jackpot()
                self.set_credits()

                self.window = xbmcgui.Window( xbmcgui.getCurrentWindowId() )
                self.set_version_properties()
                self.set_lucky7v1_properties()
            except:
                print_exc()
            xbmcgui.unlock()
            self.dialog_is_ok = True

    def set_lucky7v1_properties( self ):
        #window = xbmcgui.Window( xbmcgui.getCurrentWindowId() )
        self.window.setProperty( "lucky7v1_author", "Frost" )
        self.window.setProperty( "lucky7v1_version", "1.1.0" )
        self.window.setProperty( "lucky7v1_release_date", "25-11-2006" )
        self.window.setProperty( "lucky7v1_url", sys.modules[ "__main__" ].__svn_url__ + "resources/Lucky7v1/" )

    def set_version_properties( self ):
        #window = xbmcgui.Window( xbmcgui.getCurrentWindowId() )
        self.window.setProperty( "version", "%s.%s" % ( sys.modules[ "__main__" ].__version__, sys.modules[ "__main__" ].__svn_revision__, ) )
        self.window.setProperty( "codename", sys.modules[ "__main__" ].__codename__ )

    def set_credits( self ):
        try:
            # TEAM CREDITS
            self.getControl( 601 ).setLabel( _( 901 ) )
            self.getControl( 600 ).reset()
            # Head Developer & Coder
            list_item = xbmcgui.ListItem( _( 910 ), sys.modules[ "__main__" ].__author__ )
            self.getControl( 600 ).addItem( list_item )
            # Coder & Skinning
            list_item = xbmcgui.ListItem( _( 911 ), sys.modules[ "__main__" ].__author__ )
            self.getControl( 600 ).addItem( list_item )
            # Graphics & Skinning
            list_item = xbmcgui.ListItem( _( 912 ), sys.modules[ "__main__" ].__author__ )
            self.getControl( 600 ).addItem( list_item )

            # ADDITIONAL CREDITS
            self.getControl( 611 ).setLabel( _( 902 ) )
            self.getControl( 610 ).reset()
            # XBMC Media Center
            list_item = xbmcgui.ListItem( _( 100 ), "Team XBMC" )
            self.getControl( 610 ).addItem( list_item )
            # Usability
            list_item = xbmcgui.ListItem( _( 913 ), "Team XBMC for Skining Engine" )
            self.getControl( 610 ).addItem( list_item )
            # Language File & Translators name
            list_item = xbmcgui.ListItem( _( 914 ), _( 101 ) )
            self.getControl( 610 ).addItem( list_item )
            # Skin credits
            self.getControl( 621 ).setLabel( _( 903 ) )

            # Lucky 7 url
            self.getControl( 666 ).setLabel( sys.modules[ "__main__" ].__svn_url__ )
        except:
            print_exc()

    def set_keymap_infos( self ):
        try:
            self.getControl( 250 ).reset()
            if not self.KeymapInfos: return
            for lcount, line in enumerate( self.KeymapInfos.findall( "line" ) ):
                for rcount, row in enumerate( line.findall( "row" ) ):
                    try: string = _( int( row.text.lower().replace( "string", "" ) ) )
                    except: string = row.text
                    label = string
                    alt_label = string
                    attribs = row.attrib
                    usealt = attribs.get( "usealt", "" )
                    img1 = attribs.get( "img1", "" )
                    img2 = attribs.get( "img2", "" )
                    img3 = attribs.get( "img3", "" )
                    if img1 or img2 or img3: label = ""

                    xbmcwiki = ""
                    if "xbmcwiki=" in usealt:
                        xbmcwiki = usealt.split( "=" )[ 1 ]

                    list_item = xbmcgui.ListItem( label )
                    list_item.setProperty( "xbmcwiki", xbmcwiki )
                    list_item.setProperty( "alt_label", alt_label )
                    list_item.setProperty( "img1", img1 )
                    list_item.setProperty( "img2", img2 )
                    list_item.setProperty( "img3", img3 )
                    self.getControl( 250 ).addItem( list_item )
        except:
            print_exc()

    def set_bonus( self ):
        self.getControl( 150 ).reset()
        def set_bonus_properties( listitem, slot1, slot2, slot3 ):
            listitem.setProperty( "slot1", slot1 )
            listitem.setProperty( "slot2", slot2 )
            listitem.setProperty( "slot3", slot3 )
            return listitem

        list_item = xbmcgui.ListItem( _( 32100 ) % _( 1 ) )
        self.getControl( 150 ).addItem( set_bonus_properties( list_item, SEVEN, SEVEN, SEVEN ) )

        list_item = xbmcgui.ListItem( _( 32101 ) % _( 1 ) )
        self.getControl( 150 ).addItem( set_bonus_properties( list_item, SEVEN, "", SEVEN ) )

        list_item = xbmcgui.ListItem( _( 32102 ) % _( 1 ) )
        self.getControl( 150 ).addItem( set_bonus_properties( list_item, "", SEVEN, "" ) )

        list_item = xbmcgui.ListItem( _( 32103 ) % _( 1 ) )
        self.getControl( 150 ).addItem( set_bonus_properties( list_item, BELL, BELL, BELL ) )

        list_item = xbmcgui.ListItem( _( 32104 ) % _( 1 ) )
        self.getControl( 150 ).addItem( set_bonus_properties( list_item, THREE_BAR, THREE_BAR, THREE_BAR ) )

        list_item = xbmcgui.ListItem( _( 32105 ) % _( 1 ) )
        self.getControl( 150 ).addItem( set_bonus_properties( list_item, TWO_BAR, TWO_BAR, TWO_BAR ) )

        list_item = xbmcgui.ListItem( _( 32106 ) % _( 1 ) )
        self.getControl( 150 ).addItem( set_bonus_properties( list_item, ONE_BAR, ONE_BAR, ONE_BAR ) )

        list_item = xbmcgui.ListItem( _( 32107 ) % _( 1 ) )
        self.getControl( 150 ).addItem( set_bonus_properties( list_item, ONE_BAR, THREE_BAR, TWO_BAR ) )

        list_item = xbmcgui.ListItem( _( 32108 ) % _( 1 ) )
        self.getControl( 150 ).addItem( set_bonus_properties( list_item, ONE_BAR, THREE_BAR, ONE_BAR ) )

        list_item = xbmcgui.ListItem( _( 32109 ) % _( 1 ) )
        self.getControl( 150 ).addItem( set_bonus_properties( list_item, CHERRIES, CHERRIES, CHERRIES ) )

        list_item = xbmcgui.ListItem( _( 32110 ) % _( 1 ) )
        self.getControl( 150 ).addItem( set_bonus_properties( list_item, "", CHERRIES, CHERRIES ) )

        list_item = xbmcgui.ListItem( _( 32111 ) % _( 1 ) )
        self.getControl( 150 ).addItem( set_bonus_properties( list_item, "", "", CHERRIES ) )

        list_item = xbmcgui.ListItem( _( 32112 ) % _( 1 ) )
        self.getControl( 150 ).addItem( set_bonus_properties( list_item, WATERMELON, WATERMELON, WATERMELON ) )

        list_item = xbmcgui.ListItem( _( 32112 ) % _( 1 ) )
        self.getControl( 150 ).addItem( set_bonus_properties( list_item, PEACH, PEACH, PEACH ) )

        list_item = xbmcgui.ListItem( _( 32113 ) % _( 1 ) )
        self.getControl( 150 ).addItem( set_bonus_properties( list_item, COCONUT, COCONUT, COCONUT ) )

        list_item = xbmcgui.ListItem( _( 32114 ) % _( 1 ) )
        self.getControl( 150 ).addItem( set_bonus_properties( list_item, XBMC, XBMC, XBMC ) )

        list_item = xbmcgui.ListItem( _( 32114 ) % _( 1 ) )
        self.getControl( 150 ).addItem( set_bonus_properties( list_item, BANANA, BANANA, BANANA ) )

        list_item = xbmcgui.ListItem( _( 32114 ) % _( 1 ) )
        self.getControl( 150 ).addItem( set_bonus_properties( list_item, PASSION, PASSION, PASSION ) )

        list_item = xbmcgui.ListItem( _( 32114 ) % _( 1 ) )
        self.getControl( 150 ).addItem( set_bonus_properties( list_item, KIWI, KIWI, KIWI ) )

        list_item = xbmcgui.ListItem( _( 32115 ) % _( 1 ) )
        self.getControl( 150 ).addItem( set_bonus_properties( list_item, LEMON, LEMON, LEMON ) )

        list_item = xbmcgui.ListItem( _( 32115 ) % _( 1 ) )
        self.getControl( 150 ).addItem( set_bonus_properties( list_item, LIME, LIME, LIME ) )

        list_item = xbmcgui.ListItem( _( 32115 ) % _( 1 ) )
        self.getControl( 150 ).addItem( set_bonus_properties( list_item, APPLE, APPLE, APPLE ) )

        list_item = xbmcgui.ListItem( _( 32116 ) % _( 1 ) )
        self.getControl( 150 ).addItem( set_bonus_properties( list_item, STRAWBERRY, STRAWBERRY, STRAWBERRY ) )

        list_item = xbmcgui.ListItem( _( 32117 ) % _( 1 ) )
        self.getControl( 150 ).addItem( set_bonus_properties( list_item, ORANGE, ORANGE, ORANGE ) )

        list_item = xbmcgui.ListItem( _( 32117 ) % _( 1 ) )
        self.getControl( 150 ).addItem( set_bonus_properties( list_item, ORANGE2, ORANGE2, ORANGE2 ) )

        list_item = xbmcgui.ListItem( _( 32118 ) % _( 1 ) )
        self.getControl( 150 ).addItem( set_bonus_properties( list_item, BLACKBERRY, BLACKBERRY, BLACKBERRY ) )

        list_item = xbmcgui.ListItem( _( 32118 ) % _( 1 ) )
        self.getControl( 150 ).addItem( set_bonus_properties( list_item, GRAPES, GRAPES, GRAPES ) )

        list_item = xbmcgui.ListItem( _( 32119 ) )
        self.getControl( 150 ).addItem( set_bonus_properties( list_item, CHERRIES, BANANA, STRAWBERRY ) )

    def set_winner_jackpot( self ):
        try:
            self.getControl( 350 ).reset()
            for name, thumb, bet, cash, jackpot, date_time in self.winners:
                list_item = xbmcgui.ListItem( name, "", iconImage=thumb, thumbnailImage=thumb )
                list_item.setProperty( "bet", str( bet ) )
                list_item.setProperty( "cash", str( cash ) )
                list_item.setProperty( "jackpot", str( jackpot ) )
                list_item.setProperty( "date_time", time.strftime( DATE_TIME_FORMAT, time.localtime( float( date_time ) ) ) )
                list_item.setProperty( "screenshot", os.path.join( SCREENSHOT_DATA, date_time + ".jpg" ) )
                #list_item.setProperty( "screenshotBig", os.path.join( SCREENSHOT_DATA, date_time + "-big.jpg" ) )
                self.getControl( 350 ).addItem( list_item )
        except:
            print_exc()

    def onClick( self, controlID ):
        try:
            if controlID == 250:
                wikiID = self.getControl( 250 ).getSelectedItem().getProperty( "xbmcwiki" )
                if wikiID in [ "0", "1", "2" ]:
                    if "OK" == wiki_default_controls( int( wikiID ) ):
                        self._close_dialog()

            elif controlID == 700:
                self._close_dialog()
                self._close_game()
                xbmc.executebuiltin( "XBMC.RunScript(%s)" % FILE_LUCKY_7_V1 )

            elif controlID == 303:
                self._close_dialog()
        except:
            print_exc()

    def onFocus( self, controlID ):
        pass

    def onAction( self, action ):
        try:
            if KEYMAP[ "close_dialog" ][ action ]:
                self._close_dialog()
        except:
            print_exc()

    def _close_dialog( self ):
        xbmc.sleep( 100 )
        self.close()

