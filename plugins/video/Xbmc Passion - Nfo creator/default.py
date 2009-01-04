
import os
import re
import sys
import time
import urllib
import xbmc
import xbmcgui
import xbmcplugin
from traceback import print_exc


_ = xbmc.getLocalizedString

DIALOG_PROGRESS = xbmcgui.DialogProgress()

etape2 = "http://passion-xbmc.org/nfo_creator/index.php?listeFilm=%s&etape=2"
etape3 = "http://passion-xbmc.org/nfo_creator/index.php?etape=3&%s=%s"

regexp = """<input type="radio" name="([^"]+)" value="([^"]+)".*/>([^"]+)<a target=_blank href='([^"]+)'>voir la fiche</a>"""


def set_pretty_formatting( text ):
    text = text.replace( "<i>", "[I]" ).replace( "</i>", "[/I]" )
    text = text.replace( "<b>", "[B]" ).replace( "</b>", "[/B]" )
    return text


def get_html_source( url ):
    """ fetch the html source """
    try:
        if os.path.isfile( url ): sock = open( url, "r" )
        else:
            urllib.urlcleanup()
            sock = urllib.urlopen( url )
        htmlsource = sock.read()
        sock.close()
        return htmlsource
    except:
        print_exc()
        return ""


def unzip( filename, destination=None, report=False ):
    from zipfile import ZipFile
    from StringIO import StringIO
    filename = StringIO( get_html_source( filename ) )
    try:
        zip = ZipFile( filename, "r" )
        namelist = zip.namelist()
        #print namelist
        total_items = len( namelist ) or 1
        diff = 100.0 / total_items
        percent = 0
        # nom du fichier nfo
        nfo_name = namelist[ 0 ]
        for count, item in enumerate( namelist ):
            percent += diff
            if report:
                if DIALOG_PROGRESS.iscanceled():
                    break
                DIALOG_PROGRESS.update( int( percent ), "Unzipping %i of %i items" % ( count + 1, total_items ), item, "Please wait..." )
                #print round( percent, 2 ), item
            if not item.endswith( "/" ):
                root, name = os.path.split( item )
                directory = os.path.normpath( os.path.join( destination, root ) )
                if not os.path.isdir( directory ): os.makedirs( directory )
                file( os.path.join( directory, name ), "wb" ).write( zip.read( item ) )
        zip.close()
        del zip
        return os.path.join( destination, nfo_name ), True
    except:
        print_exc()
        return "", False


class _Info:
    def __init__( self, *args, **kwargs ):
        self.__dict__.update( kwargs )


class Main:
    # base paths
    BASE_CACHE_PATH = os.path.join( xbmc.translatePath( "P:\\Thumbnails" ), "Video" )
    # add all video extensions wanted in lowercase
    VIDEO_EXT = xbmc.getSupportedMedia( "video" )

    def __init__( self ):
        self._get_settings()
        if ( "nfoUrl=" in sys.argv[ 2 ] ):
            self._parse_argv()
            self._install_nfo()
        elif ( "isFolder=0" in sys.argv[ 2 ] ):
            self._parse_argv()
            self._select_nfo()
        else:
            self._add_directory_items()

    def _parse_argv( self ):
        # call _Info() with our formatted argv to create the self.args object
        exec "self.args = _Info(%s)" % ( sys.argv[ 2 ][ 1 : ].replace( "&", ", " ), )
        # unquote path
        self.args.path = urllib.unquote_plus( self.args.path )

    def _get_settings( self ):
        self.settings = {}
        self.settings[ "path" ] = xbmcplugin.getSetting( "path" )
        self.settings[ "web_navigator" ] = xbmcplugin.getSetting( "web_navigator" )

    def _add_directory_items( self ):
        OK = True
        try:
            if not self.settings[ "path" ]:
                xbmcgui.Dialog().ok( _( 30000 ), _( 30008 ) )
                return
            for root, dirs, files in os.walk( self.settings[ "path" ], topdown=False ):
                for name in files:
                    fpath = os.path.join( root, name )
                    title, ext = os.path.splitext( name )
                    if title.lower() == "vts_01_1":
                        name = os.path.basename( root ) + ext
                    elif re.search( "vts_|video_", title.lower() ): continue
                    if not ext.lower() in self.VIDEO_EXT: continue
                    DIALOG_PROGRESS.update( -1, _( 1040 ), name )
                    thumbnail = self._get_thumbnail( fpath )
                    listitem = xbmcgui.ListItem( name, thumbnailImage=thumbnail )
                    # add the movie information item
                    c_items = [ ( _( 13358 ), "XBMC.PlayMedia(%s)" % ( fpath ), ) ]
                    # add items to listitem with replaceItems = True so only ours show
                    listitem.addContextMenuItems( c_items, replaceItems=True )
                    url = '%s?path=%s&isFolder=%d' % ( sys.argv[ 0 ], repr( urllib.quote_plus( fpath ) ), 0, )
                    OK = xbmcplugin.addDirectoryItem( handle=int( sys.argv[ 1 ] ), url=url, listitem=listitem, isFolder=True )
                    if ( not OK ): raise
            listitem = xbmcgui.ListItem( _( 30001 ), thumbnailImage=os.path.join( os.getcwd().rstrip( ";" ), "default.tbn" ) )
            listitem.addContextMenuItems( [], replaceItems=True )
            url = '%s?path=%s&isFolder=%d' % ( sys.argv[ 0 ], repr( urllib.quote_plus( "" ) ), 0, )
            OK = xbmcplugin.addDirectoryItem( handle=int( sys.argv[ 1 ] ), url=url, listitem=listitem, isFolder=True )
            if ( not OK ): raise
            xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category=_( 20012 ) )
        except:
            print_exc()
            OK = False
        self._set_Content( OK )

    def _set_Content( self, OK ):
        if ( OK ):
            content = ( "files", "movies", "tvshows", "episodes", )[ 1 ]
            xbmcplugin.setContent( handle=int( sys.argv[ 1 ] ), content=content )
        self._add_sort_methods( OK )

    def _add_sort_methods( self, OK ):
        if ( OK ):
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_NONE )
        self._end_of_directory( OK )

    def _end_of_directory( self, OK ):
        xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=OK )

    def _get_thumbnail( self, path ):
        try:
            fpath = path
            # make the proper cache filename and path so duplicate caching is unnecessary
            filename = xbmc.getCacheThumbName( fpath )
            thumbnail = os.path.join( self.BASE_CACHE_PATH, filename[ 0 ], filename )
            # if the cached thumbnail does not exist check for a tbn file
            if ( not os.path.isfile( thumbnail ) ):
                # create filepath to a local tbn file
                thumbnail = os.path.splitext( path )[ 0 ] + ".tbn"
                # if there is no local tbn file leave blank
                if ( not os.path.isfile( thumbnail.encode( "utf-8" ) ) ):
                    thumbnail = ""
            return thumbnail
        except:
            print_exc()
            return ""

    def _select_nfo( self ):
        search_nfo = ""
        OK = True
        try:
            if not self.args.path:
                xbmcgui.Dialog().ok( _( 30000 )  , _( 30002 ), _( 30003 ), _( 30004 ) )
                keyboard = xbmc.Keyboard( "", _( 30005 ) )
                keyboard.doModal()
                if keyboard.isConfirmed():
                    search_nfo = keyboard.getText()#.replace( " ", "+" )
            else:
                search_nfo = os.path.basename( self.args.path )#.replace( " ", "+" )

            fpath = repr( urllib.quote_plus( self.args.path ) )

            #cas pour un dvd
            title, ext = os.path.splitext( search_nfo )
            if title.lower() == "vts_01_1":
                search_nfo = os.path.basename( os.path.dirname( self.args.path ) ) + ext
            #print search_nfo

            search_nfo = search_nfo.replace( " ", "+" )
            DIALOG_PROGRESS.update( -1, _( 1040 ), search_nfo )
            if search_nfo:
                #time.sleep( 1 )
                source = get_html_source( etape2 % search_nfo )
                nfo_listed =  re.findall( regexp, source )
                for count, items in enumerate( nfo_listed ):
                    name = set_pretty_formatting( items[ 2 ].strip() )
                    DIALOG_PROGRESS.update( -1, _( 1040 ), name )

                    listitem = xbmcgui.ListItem( name, thumbnailImage=os.path.join( os.getcwd().rstrip( ";" ), "default.tbn" ) )

                    if self.settings[ "web_navigator" ] != "" and os.path.exists( self.settings[ "web_navigator" ] ):
                        cmd = "System.Exec"
                        command = '%s("%s" "%s")' % ( cmd, self.settings[ "web_navigator" ], items[ 3 ], )
                        # add the movie information item
                        c_items = [ ( _( 30010 ), command, ) ]
                        # add items to listitem with replaceItems = True so only ours show
                        listitem.addContextMenuItems( c_items, replaceItems=True )

                    nfoUrl = repr( urllib.quote_plus( etape3 % ( items[ 0 ], items[ 1 ].replace( " ", "+" ), ) ) )
                    url = '%s?path=%s&nfoUrl=%s' % ( sys.argv[ 0 ], fpath, nfoUrl, )
                    OK = xbmcplugin.addDirectoryItem( handle=int( sys.argv[ 1 ] ), url=url, listitem=listitem, isFolder=False )
                    if ( not OK ): raise
            xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category=_( 283 ) + ":[CR]" + search_nfo )
        except:
            print_exc()
            OK = False
        self._set_Content( OK )

    def _install_nfo( self ):
        try:
            heading, line1, line_error = _( 30000 ), _( 30006 ), _( 30007 )
            xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=False )
            self.args.nfoUrl = urllib.unquote_plus( self.args.nfoUrl )
            destination = os.path.dirname( self.args.path ) or os.getcwd().rstrip( ";" )
            filename =  self.args.nfoUrl
            DIALOG_PROGRESS.create( heading, os.path.basename( self.args.path ) )
            nfo, ok = unzip( filename, destination, True )
            DIALOG_PROGRESS.close()
            if not ok: xbmcgui.Dialog().ok( heading, line_error )
            else: xbmcgui.Dialog().ok( heading, line1, "Dir: " + os.path.dirname( nfo ), "File: " + os.path.basename( nfo ) )
        except:
            print_exc()


if __name__ == "__main__":
    Main()
