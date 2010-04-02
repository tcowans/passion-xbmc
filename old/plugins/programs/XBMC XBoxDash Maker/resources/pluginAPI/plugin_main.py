
#Modules general
import os
import sys
import time
from traceback import print_exc
from urllib import quote_plus, unquote_plus

#Modules XBMC
import xbmc
import xbmcgui
import xbmcplugin

#Modules Custom
from dashboard import *
from utilities import *


USE_TBN = ( xbmcplugin.getSetting( "use_tbn" ) == "true" )
TBN_PATH = xbmc.translatePath( xbmcplugin.getSetting( "tbn_path" ) )
#print USE_TBN, TBN_PATH

class _Info:
    def __init__( self, *args, **kwargs ):
        self.__dict__.update( kwargs )


class Main:
    def __init__( self, *args, **kwargs ):
        try:
            self._parse_argv()
        except:
            print_exc()
        self.set_directory()

    def _parse_argv( self ):
        # if first run set title to blank
        if ( sys.argv[ 2 ] == "" ):
            self.args = _Info()
        else:
            # call _Info() with our formatted argv to create the self.args object
            exec "self.args = _Info(%s)" % ( unquote_plus( sys.argv[ 2 ][ 1 : ].replace( "&", ", " ) ), )

    def uix_filter( self ):
        base_path = os.path.join( os.getcwd().rstrip( ";" ), "resources", "ShortcutXBE", "TeamUIX" )
        def _filter( uix_path ):
            cut_path = os.path.join( base_path, uix_path.replace(":" , "") )
            #return True if path uix exists in local HDD and ShortcutXBE exists in plugin resources
            return os.path.isfile( uix_path ) and os.path.isfile( cut_path )
        return filter( _filter, [ os.sep.join( uix ) for uix in Team_UIX_ShortcutXbePath().values() ] )

    def dash_filter( self ):
        dp = DashboardPath()
        #clear critical path
        [ dp.__delitem__( x ) for x in IGNORE_DASH_PATH ]
        def _filter( dpath ):
            #return True if path dash exists in local HDD
            return os.path.isfile( dpath )
        return filter( _filter, [ os.sep.join( value ) for value in dp.values() ] )

    def add_options( self ):
        # OPTIONS
        c_items = []
        listitem = xbmcgui.ListItem( xbmc.getLocalizedString( 30100 ), thumbnailImage=os.path.join( os.getcwd().rstrip( ";" ), "resources", "media", "icon_system.png" ) )
        import plugin_test
        test = plugin_test.Main( False )
        if test not in [ 0, 1 ]:
            url = "cut='%s'&apps_path='%s'&dash_path='%s'" % ( test[ 0 ], quote_plus( test[ 1 ] ), quote_plus( test[ 2 ] ) )
            c_items += [ ( xbmc.getLocalizedString( 30560 ), "XBMC.RunPlugin(plugin://Programs/XBMC XBoxDash Maker/?%s)" % url ) ]
        c_items += [ ( xbmc.getLocalizedString( 30551 ), "XBMC.RunPlugin(plugin://Programs/XBMC XBoxDash Maker/?action=testconfig)" ) ]
        c_items += [ ( xbmc.getLocalizedString( 30800 ), "XBMC.RunPlugin(plugin://Programs/XBMC XBoxDash Maker/?action=svnbuild)" ) ]
        c_items += [ ( xbmc.getLocalizedString( 30552 ), "XBMC.RunPlugin(plugin://Programs/XBMC XBoxDash Maker/?action=cachescleaner)" ) ]
        c_items += [ ( xbmc.getLocalizedString( 654 ), "XBMC.ActivateWindow(scriptsdebuginfo)" ) ]
        listitem.addContextMenuItems( c_items, replaceItems=True )
        url = "%s?showcontextmenu" % ( sys.argv[ 0 ] )
        ok = xbmcplugin.addDirectoryItem( handle=int( sys.argv[ 1 ] ), url=url, listitem=listitem, isFolder=True, totalItems=3 )
        if ( not ok ): raise

    def set_directory( self ):
        if ( not sys.argv[ 2 ] ):
            #type of shortcut
            self.choice_of_shortcut()
        else: 
            if ( self.args.cut != "" ) and ( self.args.cut in "XBMC|UIX" ):
                if ( self.args.apps_path == self.args.dash_path == "" ):
                    self.choice_of_apps()
                else:
                    self.args.apps_path = self.browse_apps( self.args.apps_path )
                    sys.argv[ 2 ] = "%s?cut='%s'&apps_path='%s'&dash_path='%s'" % ( sys.argv[ 0 ], self.args.cut, quote_plus( self.args.apps_path ), "" )
                if ( os.path.isfile( self.args.apps_path ) and self.args.dash_path == "" ):
                    self.choice_of_dash()
                if (self.args.apps_path != self.args.dash_path ) and ( os.path.isfile( self.args.apps_path ) and os.path.isfile( self.args.dash_path ) ):
                    xbmcplugin.endOfDirectory( handle=0, succeeded=False )
                    #xbmc.executebuiltin('XBMC.ActivateWindow(10001,plugin://programs/)')
                    #xbmc.sleep(60)
                    print self.args.cut, self.args.dash_path, self.args.apps_path
                    InstallDashboard( self.args.cut, self.args.dash_path, self.args.apps_path )

    def choice_of_shortcut( self ):
        try:
            ok = True
            # TEAM XBMC CHOICE
            url = "%s?cut='%s'&apps_path='%s'&dash_path='%s'" % ( sys.argv[ 0 ], "XBMC", "", "" )
            listitem = xbmcgui.ListItem( xbmc.getLocalizedString( 30512 ), thumbnailImage=os.path.join( os.getcwd().rstrip( ";" ), "resources", "thumbnails", "team_xbmc.png" ) )
            listitem.addContextMenuItems( [ ( xbmc.getLocalizedString( 654 ), "XBMC.ActivateWindow(scriptsdebuginfo)" ) ], replaceItems=True )
            ok = xbmcplugin.addDirectoryItem( handle=int( sys.argv[ 1 ] ), url=url, listitem=listitem, isFolder=True, totalItems=3 )
            if ( not ok ): raise

            if len( self.uix_filter() ):
                # TEAM UIX CHOICE
                url = "%s?cut='%s'&apps_path='%s'&dash_path='%s'" % ( sys.argv[ 0 ], "UIX", "", "" )
                listitem = xbmcgui.ListItem( xbmc.getLocalizedString( 30513 ), thumbnailImage=os.path.join( os.getcwd().rstrip( ";" ), "resources", "thumbnails", "team_uix.png" ) )
                listitem.addContextMenuItems( [ ( xbmc.getLocalizedString( 654 ), "XBMC.ActivateWindow(scriptsdebuginfo)" ) ], replaceItems=True )
                ok = xbmcplugin.addDirectoryItem( handle=int( sys.argv[ 1 ] ), url=url, listitem=listitem, isFolder=True, totalItems=3 )
                if ( not ok ): raise

            # OPTIONS
            self.add_options()

            #else:
            #    #NO PATH FOR UIX WAS FOUND. SET DEFAULT TEAM XBMC CHOICE
            #    sys.argv[ 2 ] = "%s?cut='%s'&apps_path='%s'&dash_path='%s'" % ( sys.argv[ 0 ], "XBMC", "", "" )
            #    self.choice_of_apps()
            #    return
        except:
            ok = False
            print_exc()
            #LOG( LOG_ERROR, "Main::choice_of_shortcut [%s]", sys.exc_info()[ 1 ] )
        self.end_of_directory( ok )

    def choice_of_apps( self ):
        try:
            ok = True
            if self.args.cut == "XBMC":
                # TEAM XBMC CHOICE
                ismapped = GET_XBMC_IS_MAPPED_TO
                if ismapped:
                    url = "%s?cut='%s'&apps_path='%s'&dash_path='%s'" % ( sys.argv[ 0 ], self.args.cut, quote_plus( ismapped ), "" )
                    listitem = xbmcgui.ListItem( xbmc.getLocalizedString( 30101 ) % ( ismapped, ), thumbnailImage="special://xbmc/media/splash.png" )
                    listitem.addContextMenuItems( [ ( xbmc.getLocalizedString( 654 ), "XBMC.ActivateWindow(scriptsdebuginfo)" ) ], replaceItems=True )
                    ok = xbmcplugin.addDirectoryItem( handle=int( sys.argv[ 1 ] ), url=url, listitem=listitem, isFolder=True, totalItems=2 )
                    if ( not ok ): raise
                url = "%s?cut='%s'&apps_path='%s'&dash_path='%s'" % ( sys.argv[ 0 ], self.args.cut, "BROWSER", "" )
                listitem = xbmcgui.ListItem( xbmc.getLocalizedString( 30102 ), thumbnailImage=os.path.join( os.getcwd().rstrip( ";" ), "resources", "media", "DefaultSearch.png" ) )
                listitem.addContextMenuItems( [ ( xbmc.getLocalizedString( 654 ), "XBMC.ActivateWindow(scriptsdebuginfo)" ) ], replaceItems=True )
                ok = xbmcplugin.addDirectoryItem( handle=int( sys.argv[ 1 ] ), url=url, listitem=listitem, isFolder=True, totalItems=2 )
                if ( not ok ): raise
            elif self.args.cut == "UIX":
                # TEAM UIX CHOICE
                listing = self.uix_filter()
                for uix_path in listing:
                    url = "%s?cut='%s'&apps_path='%s'&dash_path='%s'" % ( sys.argv[ 0 ], self.args.cut, quote_plus( uix_path ), "" )
                    listitem = xbmcgui.ListItem( xbmc.getLocalizedString( 30103 ) % (uix_path, ), thumbnailImage=self._get_thumbnail( uix_path ) )
                    listitem.addContextMenuItems( [ ( xbmc.getLocalizedString( 654 ), "XBMC.ActivateWindow(scriptsdebuginfo)" ) ], replaceItems=True )
                    ok = xbmcplugin.addDirectoryItem( handle=int( sys.argv[ 1 ] ), url=url, listitem=listitem, isFolder=True, totalItems=len(listing) )
                    if ( not ok ): raise
            else: ok = False
        except:
            print_exc()
            ok = False
            #LOG( LOG_ERROR, "Main::choice_of_apps [%s]", sys.exc_info()[ 1 ] )
        self.end_of_directory( ok )

    def choice_of_dash( self ):
        try:
            ok = True
            listing = self.dash_filter()
            for dash in listing:
                dash_path = dash
                url = "%s?cut='%s'&apps_path='%s'&dash_path='%s'" % ( sys.argv[ 0 ], self.args.cut, quote_plus( self.args.apps_path ), quote_plus( dash_path ) )
                title = xbmc.getLocalizedString( 30104 ) % dash_path
                listitem = xbmcgui.ListItem( title , thumbnailImage=self._get_thumbnail( dash_path ) )
                listitem.setInfo( type="Video", infoLabels={ "Title": title } )# , "Size":  float( os.path.getsize( dash_path ) ) } )
                listitem.addContextMenuItems( [ ( xbmc.getLocalizedString( 654 ), "XBMC.ActivateWindow(scriptsdebuginfo)" ) ], replaceItems=True )
                ok = xbmcplugin.addDirectoryItem( handle=int( sys.argv[ 1 ] ), url=url, listitem=listitem, totalItems=len(listing) )
                if ( not ok ): raise
        except:
            print_exc()
            ok = False
            #LOG( LOG_ERROR, "Main::choice_of_dash [%s]", sys.exc_info()[ 1 ] )
        self.end_of_directory( ok )

    def end_of_directory( self, ok ):
        if ( not ok ): print_exc()
        else: xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_NONE )
        xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=ok )

    def browse_apps( self, path ):
        if ( path == "BROWSER" ):
            #while xbmc.getCondVisibility("!Window.IsActive(101)"): continue
            #xbmc.sleep(10)
            path = GET_XBMC_IS_MAPPED_TO
            if not path: path = ""
            else: path = os.path.dirname( path )
            browser = xbmcgui.Dialog().browse( 1, xbmc.getLocalizedString( 30102 ), "files", ".xbe", False, False, path )
            if browser != path and os.path.isfile( browser ):
                if os.path.splitdrive( browser )[ 0 ].lower() == "q:":
                    browser = GET_XBMC_IS_MAPPED_TO
                if browser: return browser
        return path

    def _get_thumbnail( self, thumbnail_path ):
        base_path = os.path.join( "P:\\", "Thumbnails" )
        try:
            filepath = xbmc.translatePath( thumbnail_path.replace( "xbe", "tbn" ) )
            if ( not filepath.endswith( ".tbn", ( len( filepath )-4 ), len( filepath ) ) ) or ( not os.path.isfile( filepath ) ):
                filename = xbmc.getCacheThumbName( thumbnail_path )
                filepath = xbmc.translatePath( os.path.join( base_path, "Programs", filename ) )
            if ( not os.path.isfile( filepath ) ):
                filename = str( xbmc.executehttpapi( "getXBEid(%s)" % thumbnail_path ) ).replace( "<li>", "" )[ 1: ]
                filepath = xbmc.translatePath( os.path.join( base_path, "GameSaves", "%s.tbn" % filename ) )
            if os.path.isfile( filepath ): return filepath
        except:
            print_exc()#LOG( LOG_ERROR, "Main::_get_thumbnail [%s]", sys.exc_info()[ 1 ] )
        return ""


class InstallDashboard:
    def __init__( self, *args, **kwargs ):
        self.cut = args[ 0 ]
        self.dash_path = args[ 1 ]
        self.apps_path = args[ 2 ]
        if xbmcgui.Dialog().yesno( xbmc.getLocalizedString( 30200 ), xbmc.getLocalizedString( 30201 ) % ( self.cut, ) , xbmc.getLocalizedString( 30202 ) % ( self.dash_path, ), xbmc.getLocalizedString( 30203 ) % ( self.apps_path, ) ):
            #LOG( LOG_NOTICE, "Starting Instalation of Dashboard" )
            #LOG( LOG_NOTICE, "Shortcut xbe by Team %s", self.cut )
            #LOG( LOG_NOTICE, "Dashboard: %s", self.dash_path )
            #LOG( LOG_NOTICE, "Launching: %s", self.apps_path )
            self.install_dashboard()

    def install_dashboard( self ):
        xbmcgui.Dialog().ok( xbmc.getLocalizedString( 30300 ).upper(), xbmc.getLocalizedString( 30301 ).upper(), xbmc.getLocalizedString( 30302 ).upper(), xbmc.getLocalizedString( 30303 ).upper() )
        DIALOG_PROGRESS.create( xbmc.getLocalizedString( 30204 ), "", "", "" )
        success = self.make_backup_dash()
        if success: success = self.install_shortcut()
        DIALOG_PROGRESS.close()
        if success:
            heading = xbmc.getLocalizedString( 30209 )
            line1   = xbmc.getLocalizedString( 30202 ) % (self.dash_path, )
            line2   = xbmc.getLocalizedString( 30203 ) % (self.apps_path, )
            line3   = xbmc.getLocalizedString( 30210 )
            self.create_tbn()
        else:
            heading = xbmc.getLocalizedString( 30211 )
            line1   = xbmc.getLocalizedString( 30212 )
            line2   = xbmc.getLocalizedString( 30213 )
            line3   = "Q:\\xbmc.log"
        xbmcgui.Dialog().ok( heading, line1, line2, line3 )
        #LOG( LOG_INFO, heading )
        #LOG( LOG_INFO, line1 )
        #LOG( LOG_INFO, line2 )
        #LOG( LOG_INFO, line3 )

    def _copy( self, src, dst ):
        try:
            success = Copy( src, dst, report_copy=dialog_report_copy ).success
        except ( IOError, Error ), msg:
            print_exc()
            success = None
        except:
            print_exc()
            #LOG( LOG_ERROR, "InstallDashboard::_copy Unexpected error: [%s]", sys.exc_info()[ 0 ] )
            #LOG( LOG_ERROR, "Unexpected error message: [%s]", sys.exc_info()[ 1 ] )
            success = None
        return success

    def make_backup_dash( self ):
        success = False
        #LOG( LOG_WARNING, "Creating backup of Dashboard..." )
        try:
            base_path = xbmc.translatePath( os.path.join( "P:\\", "Dashboard_Backup", time.strftime( "%d%b%y_%H%M" ) ) )
            backup_path = os.path.join( base_path, os.path.dirname( self.dash_path ).replace(":" , "") )
            cfg_path = self.dash_path.replace(".xbe", ".cfg")
            os.makedirs( backup_path )
            #LOG( LOG_NOTICE, "Dir Created: %s", backup_path )
            success = self._copy( self.dash_path, os.path.join( backup_path, os.path.basename( self.dash_path ) ) )
            if success:
                #LOG( LOG_NOTICE, "File Copied: [%s] to [%s]", self.dash_path, os.path.join( backup_path, os.path.basename( self.dash_path ) ) )
                if os.path.isfile( cfg_path ):
                    success = self._copy( cfg_path, os.path.join( backup_path, os.path.basename( cfg_path ) ) )
                    #if success: #LOG( LOG_NOTICE, "File Copied: [%s] to [%s]", cfg_path, os.path.join( backup_path, os.path.basename( cfg_path ) ) )
        except:
            print_exc()#LOG( LOG_ERROR, "InstallDashboard::make_backup_dash [%s]", sys.exc_info()[ 1 ] )
        if not success:
            success = xbmcgui.Dialog().yesno( xbmc.getLocalizedString( 30205 ), xbmc.getLocalizedString( 30206 ), xbmc.getLocalizedString( 30207 ), xbmc.getLocalizedString( 30202 ) % ( self.dash_path, ) )
            #if success: #LOG( LOG_WARNING, "User to accept, overwrite old Dashboard!" )
        return success

    def install_shortcut( self ):
        #LOG( LOG_WARNING, "Creating shortcut..." )
        try:
            base_path = xbmc.translatePath( os.path.join( os.getcwd().rstrip( ";" ), "resources", "ShortcutXBE" ) )
            if self.cut == "UIX":
                cut_path = os.path.join( base_path, "TeamUIX", self.apps_path.replace(":" , "") )
            if self.cut == "XBMC":
                cut_path = os.path.join( base_path, "TeamXBMC", "TEAM XBMC.xbe" )
            if os.path.isfile( cut_path ) and os.path.isfile( self.dash_path ):
                success = True
                try:
                    if self.cut == "XBMC":
                        cfg_path = cut_path.replace( ".xbe", ".cfg" )
                        success = self.write_dash_cfg( cfg_path )
                        #print repr( file( cfg_path, "r" ).read() )
                        if success:
                            success = self._copy( cfg_path, self.dash_path.replace( ".xbe", ".cfg" ) )
                            #if success: #LOG( LOG_NOTICE, "File Copied: [%s] to [%s]", cfg_path, self.dash_path.replace( ".xbe", ".cfg" ) )
                    if success:
                        success = self._copy( cut_path, self.dash_path )
                        #if success: LOG( LOG_NOTICE, "File Copied: [%s] to [%s]", cut_path, self.dash_path )
                except:
                    print_exc()
                    #LOG( LOG_ERROR, "InstallDashboard::make_backup_dash [%s]", sys.exc_info()[ 1 ] )
                    success = False
                return success
        except:
            print_exc()#LOG( LOG_ERROR, "InstallDashboard::install_shortcut [%s]", sys.exc_info()[ 1 ] )
        return False

    def write_dash_cfg( self, cfg_path ):
        #NOTE A ECRIRE AVANT ET COPIER APRES
        #cfg_path = self.dash_path.replace( ".xbe", ".cfg" )
        file( cfg_path, "w" ).write( self.apps_path.strip() )
        dialog_progress_update( 100, xbmc.getLocalizedString( 30208 ), cfg_path )
        #LOG( LOG_NOTICE, "File writed: [%s]", cfg_path )
        return self.apps_path in file( cfg_path, "r" ).read()

    def create_tbn( self ):
        if USE_TBN:
            if os.path.isfile( TBN_PATH ):
                try:
                    self._copy( TBN_PATH, self.dash_path.replace( ".xbe", ".tbn" ) )
                except:
                    print_exc()
                try:
                    self._copy( TBN_PATH, self.apps_path.replace( ".xbe", ".tbn" ) )
                except:
                    print_exc()

        '''
        if xbmcgui.Dialog().yesno( "Dashboard Maker: Thumbnail Image", "Do you want a creating thumbnail Dashboard?" ):
            try:
                tbn = xbmcgui.Dialog().browse( 2, "Browse for creating thumbnail Dashboard", "files", ".tbn|.png", True, True, os.path.join( os.getcwd().rstrip( ";" ), "media\\") )
                if os.path.isfile( tbn ):
                    #LOG( LOG_WARNING, "Creating thumbnail Dashboard..." )
                    if self._copy( tbn, self.dash_path.replace( ".xbe", ".tbn" ) ):
                        #LOG( LOG_NOTICE, "TBN Copied: [%s] to [%s]", tbn, self.dash_path.replace( ".xbe", ".tbn" ) )
            except:
                print_exc()
                pass#LOG( LOG_ERROR, "InstallDashboard::create_tbn [%s]", sys.exc_info()[ 1 ] )
        '''
