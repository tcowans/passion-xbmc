# -*- coding: utf-8 -*-

import os
import re
import sys
import time
import urllib
import urllib2
from traceback import print_exc

if sys.version >= "2.5":
    from hashlib import md5 as _hash
else:
    from md5 import new as _hash

import xbmc
import xbmcgui
import xbmcvfs
import xbmcplugin
from xbmcaddon import Addon


ADDON             = Addon( "plugin.video.bandes-annonces.fr" )
ADDON_NAME        = ADDON.getAddonInfo( "name" )
ADDON_DATA        = xbmc.translatePath( ADDON.getAddonInfo( "profile" ) )
CACHE_EXPIRE_TIME = float( ADDON.getSetting( "expiretime" ).replace( "0", ".5" ).replace( "25", "0" ) )

ADDON_CACHE = os.path.join( ADDON_DATA, ".cache" )
#ADDON_CACHE = os.path.join( sys.path[ 0 ], ".cache" )

if not os.path.exists( ADDON_CACHE ):
    os.makedirs( ADDON_CACHE )


HTTP_USER_AGENT = "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.1.1) Gecko/20090715 Firefox/3.5.1"
#HTTP_USER_AGENT = "Mozilla/5.0 (Windows NT 5.1; rv:7.0.1) Gecko/20100101 Firefox/7.0.1"
class _urlopener( urllib.FancyURLopener ):
    version = os.environ.get( "HTTP_USER_AGENT" ) or HTTP_USER_AGENT
urllib._urlopener = _urlopener()


def time_took( t ):
    t = ( time.time() - t )
    #minute
    if t >= 60: return "%.3fm" % ( t / 60.0 )
    #millisecond
    if 0 < t < 1: return "%.3fms" % ( t )
    #second
    return "%.3fs" % ( t )


def is_expired( lastUpdate, hrs=CACHE_EXPIRE_TIME ):
    expired = time.time() >= ( lastUpdate + ( hrs * 60**2 ) )
    return expired


def get_cached_filename( fpath ):
    c_filename = "%s.html" % _hash( repr( fpath ) ).hexdigest()
    return os.path.join( ADDON_CACHE, c_filename )


def get_cached_source( url, refresh=False, uselocal=False, debug=None ):
    """ fetch the cached source """
    c_source, sock, c_filename = "", None, None
    try:
        # set cached filename
        c_filename = get_cached_filename( url )
        # if cached file exists read this, only is expired
        if uselocal: refresh = False
        if not refresh and os.path.exists( c_filename ):
            if uselocal or not is_expired( os.path.getmtime( c_filename ) ):
                #print ( "Reading local source: %r" % c_filename )
                sock = open( c_filename )
                c_source = sock.read()
    except:
        print_exc()
    return c_source, sock, c_filename


def get_html_source( url, refresh=False, uselocal=False ):
    """ fetch the html source """
    source = ""
    try:
        # set cached filename
        source, sock, c_filename = get_cached_source( url, refresh, uselocal )

        if not source or sock is None:
            #print ( "Reading online source: %r" % url )
            sock = urllib.urlopen( url )
            source = sock.read()
            if c_filename:
                try: file( c_filename, "w" ).write( source )
                except: print_exc()
        sock.close()
    except:
        print_exc()
    return source


def get_video( swf=None, content=None ):
    if swf is not None:
        try:
            sock = urllib2.urlopen( swf )
            content = sock.geturl()
            sock.close()
        except:
            print_exc()

    vidName = idvideo = None
    if content is not None:
        try: vidName, idvideo = re.search( 'vidName=(.+?)&.+?idvideo=(.+?)&', content ).groups() #('356985.mp4', '192029')
        except: print_exc()

    media = ""
    if idvideo and vidName:
        try:
            sock = urllib2.urlopen( 'http://bandesannonces.wmaker.tv/_public/get_video.php?v=%s/%s' % ( idvideo, vidName ) )
            media = sock.read().strip()
            sock.close()
        except:
            print_exc()

    return media.startswith( "http://" ) and media


def getVideoFromPageBA( url ):
    html = get_html_source( url )

    content = re.search( '<meta property="og:video" content="(.*?)" />', html )
    if content:
        content = content.group( 1 )
        if re.search( 'vidName=(.+?)&.+?idvideo=(.+?)&', content ):
            return get_video( content=content )

    swf = re.search( 'data=&quot;(.+?)&quot;', html )
    if swf:
        swf = swf.group( 1 )
        if swf.startswith( "http://bandesannonces.wmaker.tv/v/" ):
            return get_video( swf )


def parsePageBA( html ):
    regexp  = '<div class="cel1 .+?'
    regexp += '<span id="perso.+?" style="background:url\(\'(.+?modules.+?)\'\).+?'
    regexp += '<span class="length">(.+?)</span>.+?'
    regexp += '<div class="titre"><a href="(.+?)">(.+?)</a></div>.+?'
    regexp += '<div class="texte">.+?<a href=".+?">(.*?)</a>'
    ba = re.compile( regexp, re.S ).findall( html )
    #print len( ba ), ba
    return ba


def getBandesAnnonces( itemsperpage=5 ):
    t1 = time.time()
    bandesannonces = []
    url = "http://bandesannonces.wmaker.tv/Chaine-1_r1.html?order=r"
    html = get_html_source( url )
    yield parsePageBA( html )

    try: page = int( re.compile( '<a.*?href=".*?start.*?">(\d+)</a>').findall( html )[ -1 ] )
    except: page = 0

    for i in range( itemsperpage, itemsperpage*page, itemsperpage ):
        t2 = time.time()
        next = url + "&start=%i" % i
        html = get_html_source( next )
        yield parsePageBA( html )

#swf = "http://bandesannonces.wmaker.tv/v/d743c857e12d77c7c3aea80f80cb2da6f5ad24e4"
#media = get_video( swf )
#print media

#content = "http://bandesannonces.wmaker.tv/_public/swf/wmplayer_tv.swf?vidName=733776.mp4&amp;startHD=undefined&amp;vidHDName=undefined&amp;streamMode=lighttpd&amp;autostart=true&amp;urlSite=bandesannonces.wmaker.tv&amp;start=0&amp;idvideo=225499&amp;urlVideo=%2FLES-IMMORTELS-BA-2-VF_v423.html&amp;stats=http%3A%2F%2Fbandesannonces.wmaker.tv%2Findex.php%3Fpreaction%3Dstat_video-225499&amp;ratio=1.77&amp;lang=fr&amp;preview=http%3A%2F%2Fbandesannonces.wmaker.tv%2Fvideossd%2F225499%2Fimages%2Fplayer%2Fplayer_preview.jpg%3Fv%3D1320311408&amp;enableEmbed=true&amp;enablePlaylist=false&amp;enableShare=true&amp;enableSubscribe=false&amp;logo=undefined&amp;position=1&amp;enablePub=false&amp;urlPub=undefined&amp;preroll=undefined&amp;prerollRatio=1.33&amp;prerollLink=undefined&amp;controlBarColor=0x222222&amp;bufferBarColor=0x666666&amp;iconsColor=0xFFFFFF&amp;progressBarColor=0xCC0000&amp;template=1&amp;slice=10&amp;enableDynamicUrl=true&amp;adswizzServerUrl=http%3A%2F%2Fstickyads.adswizz.com%2Fwww%2Fdelivery%2FswfIndex.php&amp;loadTimeout=2&amp;preroll_zone_id=1810&amp;requestMidrollDelay=25&amp;requestAdInterval=-1&amp;midroll_zone_id=-1&amp;postroll_zone_id=-1&amp;component_url=http%3A%2F%2Fstickyads.adswizz.com%2Fwww%2Fcomponents%2FVideoComponent.swf&amp;skin_zone_id=-1&amp;regie=1&amp;shortURL=LES+IMMORTELS+%28BA+2+-+VF%29+http%3A%2F%2Fxfru.it%2FUjuTzS&amp;embeded=false&amp;postview=undefined&amp;"
#media = get_video( content=content )
#print media


def add_directory_items():
    t1 = time.time()
    totals = 0
    for bandesannonces in getBandesAnnonces():
        totals += len( list( bandesannonces ) )

        for thumb, duration, url, title, plot in bandesannonces:
            try:
                m, s = duration.split( ":" )
                duration = eval( "(%i*60)+%i" % ( int( m ), int( s ) ) )
            except:
                pass#print_exc()

            listitem = xbmcgui.ListItem( title, '', 'DefaultVideo.png', thumb )
            #use music type. for sort by duration work correctly
            listitem.setInfo( 'music', { 'title': title, 'plot': plot, 'duration': duration } )

            url = urllib.quote_plus( url )
            uri = '%s?webbrowser=\"%s\"' % ( sys.argv[ 0 ], url )
            c_items = [ ( "Play on Site", "RunPlugin(%s)" % uri ) ]

            uri = '%s?url=\"%s\"&download=True' % ( sys.argv[ 0 ], url )
            c_items += [ ( "Download", "RunPlugin(%s)" % uri ) ]

            uri = '%s?url=\"%s\"&download=True&tomovie=True' % ( sys.argv[ 0 ], url )
            c_items += [ ( "Download in movie folder", "RunPlugin(%s)" % uri ) ]
            listitem.addContextMenuItems( c_items )

            url = '%s?url="%s"' % ( sys.argv[ 0 ], url )
            xbmcplugin.addDirectoryItem( int( sys.argv[ 1 ] ), url, listitem, False, totals )

    xbmcplugin.setContent( int( sys.argv[ 1 ] ), "movies" )

    xbmcplugin.addSortMethod( int( sys.argv[ 1 ] ), xbmcplugin.SORT_METHOD_UNSORTED )
    xbmcplugin.addSortMethod( int( sys.argv[ 1 ] ), xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE )
    xbmcplugin.addSortMethod( int( sys.argv[ 1 ] ), xbmcplugin.SORT_METHOD_DURATION  )

    xbmcplugin.endOfDirectory( int( sys.argv[ 1 ] ) )

    #print totals
    print "[%s] initialized container took %s" % ( ADDON_NAME, time_took( t1 ) )


def download( url, destination, title, _wait="" ):
    t1 = time.time()
    OK, dl_path = False, ""
    DIALOG_PROGRESS = xbmcgui.DialogProgress()
    try:
        DIALOG_PROGRESS.create( title )
        ext1 = os.path.splitext( destination )[ 1 ]
        if ext1:
            ext2 = "-trailer%s" % os.path.splitext( url )[ 1 ]
            destination = destination.replace( ext1, ext2 )
        else:
            destination = destination + os.path.basename( url )

        try: destination = destination.decode( "utf-8" )
        except: pass

        download._wait = _wait = "Please wait[B].[/B]"
        def please_wait():
            download._wait += "[B].[/B]"
            if download._wait.count( "." ) >= 4:
                download._wait = "Please wait[B].[/B]"

        def _report_hook( count, blocksize, totalsize, please_wait=None ):
            if please_wait: please_wait()
            percent = int( float( count * blocksize * 100 ) / totalsize )
            DIALOG_PROGRESS.update( percent, "Downloading: %s " % url, "to: %s" % destination, download._wait )
            if DIALOG_PROGRESS.iscanceled(): raise IOError

        try:
            part = destination + ".part"
            hook = lambda c, b, t, please_wait=please_wait: _report_hook( c, b, t, please_wait )
            fp, h = urllib.urlretrieve( url, part, hook )
            try:
                print "%r" % fp
                print str( h ).replace( "\r", "" )
            except:
                pass
            if xbmcvfs.exists( destination ):
                xbmcvfs.delete( destination )
            OK = xbmcvfs.rename( part, destination )
            dl_path = destination
        except IOError:
            xbmcvfs.delete( destination )
            print "%r xbmcvfs.delete(%r)" % ( not xbmcvfs.exists( destination ), destination )
    except:
        print_exc()
    DIALOG_PROGRESS.close()
    print "[%s] Download took %s for trailer %r" % ( ADDON_NAME, time_took( t1 ), dl_path )
    return OK and dl_path


def getBrowseDialog( default="", heading="", dlg_type=3, shares="files", mask=xbmc.getSupportedMedia( 'video' ), use_thumbs=False, treat_as_folder=False ):
    """ shows a browse dialog and returns a value
        - 0 : ShowAndGetDirectory
        - 1 : ShowAndGetFile
        - 2 : ShowAndGetImage
        - 3 : ShowAndGetWriteableDirectory
    """
    dialog = xbmcgui.Dialog()
    value  = dialog.browse( dlg_type, heading, shares, mask, use_thumbs, treat_as_folder, default )
    return value


class Info:
    def __init__( self, *args, **kwargs ):
        # update dict with our formatted argv
        try: exec "self.__dict__.update(%s)" % ( sys.argv[ 2 ][ 1: ].replace( "&", ", " ), )
        except: print_exc()
        # update dict with custom kwargs
        self.__dict__.update( kwargs )

    def __getattr__( self, namespace ):
        return self[ namespace ]

    def __getitem__( self, namespace ):
        return self.get( namespace )

    def __setitem__( self, key, default="" ):
        self.__dict__[ key ] = default

    def get( self, key, default="" ):
        return self.__dict__.get( key, default )#.lower()

    def isempty( self ):
        return not bool( self.__dict__ )

    def IsTrue( self, key, default="false" ):
        return ( self.get( key, default ).lower() == "true" )


def Main():
    try:
        args = Info()

        if args.isempty():
            add_directory_items()

        elif args.url:
            title    = unicode( xbmc.getInfoLabel( "ListItem.Title" ),    "utf-8" )
            plot     = unicode( xbmc.getInfoLabel( "ListItem.Plot" ),     "utf-8" )
            duration = unicode( xbmc.getInfoLabel( "ListItem.Duration" ), "utf-8" )
            thumb    = unicode( xbmc.getInfoImage( "ListItem.Thumb" ),    "utf-8" )

            destination = None
            if args.download:
                # default select folder
                if args.tomovie:
                    destination = getBrowseDialog( heading="Select movie to save trailer", dlg_type=1, shares="video" )
                else:
                    destination = getBrowseDialog( heading="Choose folder to save trailer" )

            xbmc.executebuiltin( 'ActivateWindow(busydialog)' )
            xbmc.sleep( 100 )
            url = urllib.unquote_plus( args.url )
            media = getVideoFromPageBA( url )

            if destination:
                xbmc.executebuiltin( 'Dialog.Close(busydialog,true)' )
                local_media = download( media, destination, title )
                if local_media:
                    try: local_media = local_media.encode( "utf-8" )
                    except: pass
                    media = local_media

                #if local_media and os.path.exists( local_media ):
                #    media = local_media
                else:
                    # reload url is expired
                    xbmc.executebuiltin( 'ActivateWindow(busydialog)' )
                    xbmc.sleep( 100 )
                    url = urllib.unquote_plus( args.url )
                    media = getVideoFromPageBA( url )

            if media:
                listitem = xbmcgui.ListItem( title, '', 'DefaultVideo.png', thumb )
                listitem.setInfo( 'video', { 'title': title, 'plot': plot, 'duration': duration } )

                xbmc.Player( xbmc.PLAYER_CORE_DVDPLAYER ).play( media, listitem )

            xbmc.executebuiltin( 'Dialog.Close(busydialog,true)' )

        elif args.webbrowser:
            import webbrowser
            webbrowser.open( urllib.unquote_plus( args.webbrowser ) )
    except:
        print_exc()



Main()
