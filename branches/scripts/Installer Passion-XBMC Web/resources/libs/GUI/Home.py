
# Modules general
import os
import sys
from traceback import print_exc

# Modules XBMC
import xbmc
import xbmcgui

# Modules custom
import RSSUserData
from utilities import *


#FONCTION POUR RECUPERER LES LABELS DE LA LANGUE.
_ = sys.modules[ "__main__" ].__language__

DIALOG_PROGRESS = xbmcgui.DialogProgress()

# set our xbmc.settings path for xbmc get '/resources/settings.xml'
XBMC_SETTINGS = xbmc.Settings( os.getcwd() )


class Home( xbmcgui.WindowXML ):
    def __init__( self, *args, **kwargs ):
        xbmcgui.WindowXML.__init__( self, *args, **kwargs )
        self._get_settings()
        self.action = None
        self.is_started = True
        self.last_pos_container_9000 = None

    def onInit( self ):
        try:
            if self.is_started:
                self.is_started = False
                if self.settings.get( "show_plash" ) == True:
                    # splash desactive par le user 
                    self.getControl( 999 ).setVisible( 0 )
            else:
                self.getControl( 999 ).setVisible( 0 )

            if self.last_pos_container_9000 is not None:
                xbmc.sleep( 100 )
                xbmc.executebuiltin( 'Control.Move(%i,%i)' % ( 9000, int( self.last_pos_container_9000 ) ) )
                self.last_pos_container_9000 = None
        except:
            print_exc()

    def _get_settings( self, defaults=False ):
        """ reads settings """
        self.settings = Settings().get_settings( defaults=defaults )
        if self.settings[ "rss_feed" ] != "0":
            try:
                #RSSUserData.refresh_rss()
                xbmc_rss_feeds_xml = RSSUserData.parse_xml()
                rss_feeds_xml = parse_rss_xml().get( self.settings[ "rss_feed" ] )
                # now if not feed in xbmc RssFeeds.xml update
                feedtag = xbmc_rss_feeds_xml.get( "100", {} ).get( "feed", [] )
                rssfeed = rss_feeds_xml.get( "feed", "http://passion-xbmc.org/scraper/?forumrss=1" )
                found = False
                for feed in feedtag:
                    if rssfeed == feed.get( "feed" ):
                        found = True
                        break
                if not found:
                    add = { '100': { 'feed': [ { 'feed': rssfeed, 'updateinterval':  str( rss_feeds_xml.get( "updateinterval", 30 ) ) } ], 'rtl': 'false' } }
                    xbmc_rss_feeds_xml.update( add )
                    print RSSUserData.save_xml( xbmc_rss_feeds_xml )
            except:
                print_exc()

    def _set_skin_colours( self ):
        #xbmcgui.lock()
        try:
            xbmc.executebuiltin( "Skin.SetString(PassionSkinColourPath,%s)" % ( self.settings[ "skin_colours_path" ], ) )
            xbmc.executebuiltin( "Skin.SetString(PassionSkinHexColour,%s)" % ( ( self.settings[ "skin_colours" ] or get_default_hex_color() ), ) )
        except:
            print_exc()
            xbmc.executebuiltin( "Skin.SetString(PassionSkinHexColour,ffffffff)" )
            xbmc.executebuiltin( "Skin.SetString(PassionSkinColourPath,default)" )
        #xbmcgui.unlock()

    def _start_rss_timer( self ):
        pass

    def onFocus( self, controlID ):
        pass

    def onClick( self, controlID ):
        try: 
            #print "Home::onClick::controlID", controlID
            if 90101 <= controlID <= 90108: # 90109 is desactived because not implanted TYPE_PLUGIN_WEATHER
                act = { 90101: "TYPE_SKIN, 0", 90102: "TYPE_SCRAPER, 1", 90103: "TYPE_SCRIPT, 2",
                    90104: "TYPE_PLUGIN, 3", 90105: "TYPE_PLUGIN_VIDEO, 3", 90106: "TYPE_PLUGIN_PICTURES, 1",
                    90107: "TYPE_PLUGIN_MUSIC, 0", 90108: "TYPE_PLUGIN_PROGRAMS, 2", 90109: "TYPE_PLUGIN_WEATHER,4" }
                self.action = "TYPE, INDEX = %s" % act.get( controlID )
                self._show_file_manager()
            elif 90161 <= controlID <= 90163:
                # for 90164 on click used in xml "run plugin "SVN Repo Installer" button" <onclick>ActivateWindow(10001,plugin://programs/SVN Repo Installer/)</onclick>
                act = { 90161: "default_content=Passion XBMC Web", 90162: "default_content=Passion XBMC FTP",
                    90163: "default_content=XBMC Zone", 90164: "exit" }
                self.action = act.get( controlID )
                self._show_main()
            elif controlID == 90141:
                self._show_settings()
            elif controlID == 90144:
                # Caches Cleaner, bugs si le caches cleaner a ete lancer depuis le xbmc.settings !!!
                import caches_cleaner
                caches_cleaner.Main()
                del caches_cleaner
            elif controlID == 90145:
                # script credits
                self._show_credits()
            elif controlID == 90165:
                # nightly builds
                self._show_nightly()
            elif controlID == 20:
                self.action = "exit"
                self._close_script()
        except:
            print_exc()

    def onContainer9000( self ):
        """ content item not work in onClick( self, controlID )
            but use <onclick>SetProperty(Container_9000_item_id,int)</onclick> and in onAction( self, action )
            use if self.getFocusId() == 9000: print self.getProperty( "Container_9000_item_id" )
        """
        try:
            if self.getFocusId() == 9000:
                item_id = self.getProperty( "Container_9000_item_id" )
                self.clearProperties()
                if item_id:
                    #print "Container_9000_item_id", item_id
                    if item_id == "2":
                        self._show_file_manager()
                    elif item_id == "4":
                        self._show_direct_infos()
                    elif item_id == "5":
                        XBMC_SETTINGS.openSettings()
                        xbmc.sleep( 500 )
                        debug_mode = XBMC_SETTINGS.getSetting( "script_debug" )
                        print "script_debug = %s" % debug_mode
                        sys.modules[ "__main__" ].output.PRINT_DEBUG = ( debug_mode == "true" )
                    elif item_id == "10":
                        self.action = "default_content=Passion XBMC Web"
                        self._show_main()
                    elif item_id == "11":
                        self.action = "exit"
                        self._close_script()
            self.clearProperties()
        except:
            print_exc()

    def _show_credits( self ):
        self.last_pos_container_9000 = 1
        self.action = None
        try:
            import Credits
            Credits.show_credits()
            del Credits
        except:
            print_exc()

    def _show_main( self ):
        try:
            import MainGui
            MainGui.show_main( self.action )
            del MainGui
        except:
            print_exc()
        self.action = None

    def _show_nightly( self ):
        try:
            import nightly_builds
            nightly_builds.show_nightly()
            del nightly_builds
        except:
            print_exc()
        self.action = None

    def _show_settings( self ):
        self.last_pos_container_9000 = 1
        try:
            import DialogSettings
            DialogSettings.show_settings( self )
            #on a plus besoin du settings, on le delete
            del DialogSettings
        except:
            print_exc()
        self.action = None

    def _show_direct_infos( self ):
        self.last_pos_container_9000 = -2
        try:
            import ForumDirectInfos
            ForumDirectInfos.show_direct_infos()
            #on a plus besoin, on le delete
            del ForumDirectInfos
        except:
            print_exc()
        self.action = None

    def _show_file_manager( self ):
        self.last_pos_container_9000 = -1
        try:
            import FileManagerGui
            mainfunctions = [ self._show_settings, self._close_script ]
            FileManagerGui.show_file_manager( mainfunctions, "", self.action )
            #on a plus besoin du manager, on le delete
            del FileManagerGui
        except:
            print_exc()
        self.action = None

    def onAction( self, action ):
        self.onContainer9000()
        if action in [ 9, 10 ]:
            self.action = "exit"
            self._close_script()

    def _close_script( self ):
        self.close()



def show_home():
    file_xml = "IPX-Home.xml"
    dir_path = os.getcwd().replace( ";", "" )
    current_skin, force_fallback = getUserSkin()
    #myfont = os.path.join( dir_path, "resources", "skins", current_skin, "fonts", "MyFont.py" )
    #if os.path.exists( myfont ): xbmc.executescript( myfont )
    try:
        h = Home( file_xml, dir_path, current_skin, force_fallback )
        h.doModal()
        HomeAction = h.action
        del h
    except:
        print_exc()
        HomeAction = "error"
    return HomeAction
