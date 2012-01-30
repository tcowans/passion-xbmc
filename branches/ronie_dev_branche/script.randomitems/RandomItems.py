# *  Thanks to:
# *
# *  Nuka for the original RecentlyAdded.py on which this is based
# *
# *  ppic, Hitcher & ronie for the updates
# *  frost for the rewrite

import time
start_time = time.time()

import os
import re
import sys
import random
from urllib import unquote
from traceback import print_exc

import xbmc
import xbmcgui
import xbmcvfs
import xbmcaddon

try: import json # Use speedup
except: import simplejson as json # No speed

__addon__   = xbmcaddon.Addon("script.randomitems")
__addonid__ = __addon__.getAddonInfo('id')
log_prefix  = "[RandomItems-%s]" % __addon__.getAddonInfo('version')

def log( txt, level=xbmc.LOGDEBUG ):
    message = '%s %s' % ( log_prefix, txt )
    xbmc.log( message, level )

class Main:
    # grab the home window
    WINDOW = xbmcgui.Window( 10000 )

    def _clear_properties( self ):
        # reset totals property for visible condition
        self.WINDOW.clearProperty( "RandomMovie.Count" )
        self.WINDOW.clearProperty( "RandomEpisode.Count" )
        self.WINDOW.clearProperty( "RandomMusicVideo.Count" )
        self.WINDOW.clearProperty( "RandomSong.Count" )
        self.WINDOW.clearProperty( "RandomAlbum.Count" )
        self.WINDOW.clearProperty( "RandomAddon.Count" )
        # we clear title for visible condition
        for count in range( self.LIMIT ):
            self.WINDOW.clearProperty( "RandomMovie.%d.Title"      % ( count + 1 ) )
            self.WINDOW.clearProperty( "RandomEpisode.%d.Title"    % ( count + 1 ) )
            self.WINDOW.clearProperty( "RandomMusicVideo.%d.Title" % ( count + 1 ) )
            self.WINDOW.clearProperty( "RandomSong.%d.Title"       % ( count + 1 ) )
            self.WINDOW.clearProperty( "RandomAlbum.%d.Title"      % ( count + 1 ) )
            self.WINDOW.clearProperty( "RandomAddon.%d.Name"       % ( count + 1 ) )

    def _parse_argv( self ):
        # default params
        params = {}
        # parse sys.argv for params
        try: params = dict( arg.split( "=" ) for arg in sys.argv[ 1 ].split( "&" ) )
        except: pass
        # set our preferences
        self.LIMIT        = int( params.get( "limit", "5" ) )
        self.UNPLAYED     = params.get( "unplayed", "False" )
        self.PLAY_TRAILER = params.get( "trailer", "False" )
        self.ALARM        = int( params.get( "alarm", "0" ) )
        self.ALBUMID      = params.get( "albumid", "" )
        self.EXTRA_IMAGES = str( params.get( "extraimages" ) ).lower() == "true"

    def _set_alarm( self ):
        # only run if user/skinner preference
        if ( not self.ALARM ): return
        # set the alarms command
        command = "XBMC.RunScript(%s,limit=%d&unplayed=%s&trailer=%s&alarm=%d&extraimages=%r)" % ( __addonid__, self.LIMIT, str( self.UNPLAYED ), str( self.PLAY_TRAILER ), self.ALARM, self.EXTRA_IMAGES, )
        xbmc.executebuiltin( "AlarmClock(RandomItems,%s,%d,true)" % ( command, self.ALARM, ) )

    def __init__( self ):
        # parse argv for any preferences
        self._parse_argv()
        # check if we were executed internally
        if self.ALBUMID:
            self._Play_Album( self.ALBUMID )
        else:
            # clear properties
            self._clear_properties()
            # set any alarm
            self._set_alarm()
            # fetch media info, but don't visit, if not content
            if xbmc.getCondVisibility( "Library.HasContent(Movies)" ): 
                self._fetch_movie_info() #function modified by frost

            if xbmc.getCondVisibility( "Library.HasContent(TVShows)" ):
                self._fetch_episode_info() #function modified by frost

            if xbmc.getCondVisibility( "Library.HasContent(MusicVideos)" ):
                self._fetch_musicvideo_info() #function modified by frost

            if xbmc.getCondVisibility( "Library.HasContent(Music)" ):
                self._fetch_album_info() #function modified by frost
                self._fetch_song_info() #function modified by frost

            #Frost: xbmc crash on my system winxp, nightly build
            self._fetch_addon_info() # ok I rewrited this function now work correctly (don't use xbmcaddon for get object)

    def _jsonrpc( self, key, *args ):
        try:
            # query the database
            query = xbmc.executeJSONRPC( '{"jsonrpc": "2.0", "method": "%s", "params": {"properties": %s}, "id": 1}' % args )
            query = unicode( query, 'utf-8', errors='ignore' )
            # separate the records
            json_response = json.loads( query ).get( 'result' ) or {}
            return json_response.get( key ) or []
        except:
            print_exc()
            return []

    def _get_generate_random_items( self, items ):
        # random items generator
        count = 0
        while count < self.LIMIT:
            count += 1
            # check if we don't run out of items before LIMIT is reached
            if len( items ) == 0:
                break
            # Shuffle items in place
            random.shuffle( items )
            # select a random item
            item = random.choice( items )
            # remove the item from our list
            items.remove( item )
            # find values
            if self.UNPLAYED == "True":
                if int( item.get( 'playcount' ) or 0 ) > 0:
                    count -= 1
                    continue
            # Returns the value of "item", the result of the current iteration
            yield count, item

    def _fetch_movie_info( self ):
        try:
            # get movies
            movies = self._jsonrpc( 'movies', "VideoLibrary.GetMovies", '["playcount", "year", "plot", "runtime", "fanart", "thumbnail", "file", "trailer", "rating"]' )
            # set total value
            self.WINDOW.setProperty( "RandomMovie.Count", str( len( movies ) ) )
            if movies:
                # enumerate thru our records
                for count, item in self._get_generate_random_items( movies ):
                    # set base property
                    b_property = "RandomMovie.%d." % ( count )
                    # set our properties
                    self.WINDOW.setProperty( b_property + "Title",       item[ 'label' ] )
                    self.WINDOW.setProperty( b_property + "Rating",      str( round( float( item[ 'rating' ] ), 1 ) ) )
                    self.WINDOW.setProperty( b_property + "Year",        str( item[ 'year' ] ) )
                    self.WINDOW.setProperty( b_property + "Plot",        item[ 'plot' ] )
                    self.WINDOW.setProperty( b_property + "RunningTime", item[ 'runtime' ] )
                    self.WINDOW.setProperty( b_property + "Path",        item[ 'file' ] )
                    self.WINDOW.setProperty( b_property + "Trailer",     item[ 'trailer' ] )
                    self.WINDOW.setProperty( b_property + "Fanart",      item[ 'fanart' ] )
                    self.WINDOW.setProperty( b_property + "Thumb",       item[ 'thumbnail' ] )
        except:
            print_exc()
        #print locals()

    def _fetch_episode_info( self ):
        try:
            # get episodes
            episodes = self._jsonrpc( 'episodes', "VideoLibrary.GetEpisodes", '["playcount", "season", "episode", "showtitle", "plot", "fanart", "thumbnail", "file", "rating"]' )
            # set total value
            self.WINDOW.setProperty( "RandomEpisode.Count", str( len( episodes ) ) )
            if episodes:
                # enumerate thru our records
                for count, item in self._get_generate_random_items( episodes ):
                    # set base property
                    b_property = "RandomEpisode.%d." % ( count )
                    season     = "%.2d" % float( item[ 'season' ] )
                    episode    = "%.2d" % float( item[ 'episode' ] )
                    episodeno  = "s%se%s" % ( season, episode )
                    # set our properties
                    self.WINDOW.setProperty( b_property + "ShowTitle",     item['showtitle'] )
                    self.WINDOW.setProperty( b_property + "EpisodeTitle",  item['label'] )
                    self.WINDOW.setProperty( b_property + "EpisodeNo",     episodeno )
                    self.WINDOW.setProperty( b_property + "EpisodeSeason", season )
                    self.WINDOW.setProperty( b_property + "EpisodeNumber", episode )
                    self.WINDOW.setProperty( b_property + "Rating",        str(round(float(item['rating']),1)) )
                    self.WINDOW.setProperty( b_property + "Plot",          item['plot'] )
                    self.WINDOW.setProperty( b_property + "Path",          item['file'] )
                    self.WINDOW.setProperty( b_property + "Fanart",        item['fanart'] )
                    self.WINDOW.setProperty( b_property + "Thumb",         item['thumbnail'] )
                    # 
                    if not self.EXTRA_IMAGES: continue
                    # get dir of episode (by frost)
                    if os.path.isdir( item['file'] ): d_path = item['file']
                    else: d_path = item['file'].replace( os.path.basename( item['file'] ), "" )
                    # if rar, get dir (by frost)
                    if "rar://" in d_path:
                        d_path = unquote( d_path.replace( "rar://", "" ) ).rstrip( "/" ).rstrip( "\\" )
                        d_path = os.path.dirname( d_path ) + ( "/", "\\" )[ d_path.count( "\\" ) ]
                    # set images properties (by frost)
                    for extra_img in [ "banner.jpg", "logo.png", "clearart.png", "poster.jpg" ]:
                        property = b_property + extra_img[ :-4 ]
                        self.WINDOW.setProperty( property, "" )
                        if xbmcvfs.exists( d_path + extra_img ):
                            self.WINDOW.setProperty( property, d_path + extra_img )
                        else:
                            #check parent dir (by frost)
                            p_dir = os.path.dirname( d_path.rstrip( "/" ).rstrip( "\\" ) ) + ( "/", "\\" )[ d_path.count( "\\" ) ]
                            if xbmcvfs.exists( p_dir + extra_img ):
                                self.WINDOW.setProperty( property, p_dir + extra_img )
                    # debug (by frost)
                    #print b_property
                    #print "file: %r"     % self.WINDOW.getProperty( b_property + "path" )
                    #print "banner: %r"   % self.WINDOW.getProperty( b_property + "banner" )
                    #print "logo: %r"     % self.WINDOW.getProperty( b_property + "logo" )
                    #print "clearart: %r" % self.WINDOW.getProperty( b_property + "clearart" )
                    #print "poster: %r"   % self.WINDOW.getProperty( b_property + "poster" )
                    #print "-"*100
        except:
            print_exc()
        #print locals()

    def _fetch_musicvideo_info( self ):
        try:
            # get musicvideos
            musicvideos = self._jsonrpc( 'musicvideos', "VideoLibrary.GetMusicVideos", '["artist", "playcount", "year", "plot", "runtime", "fanart", "thumbnail", "file"]' )
            # set total value
            self.WINDOW.setProperty( "RandomMusicVideo.Count", str( len( musicvideos ) ) )
            if musicvideos:
                # enumerate thru our records
                for count, item in self._get_generate_random_items( musicvideos ):
                    # set base property
                    b_property = "RandomMusicVideo.%d." % ( count )
                    # set our properties
                    self.WINDOW.setProperty( b_property + "Title",       item[ 'label' ] )
                    self.WINDOW.setProperty( b_property + "Year",        str( item[ 'year' ] ) )
                    self.WINDOW.setProperty( b_property + "Plot",        item[ 'plot' ] )
                    self.WINDOW.setProperty( b_property + "RunningTime", item[ 'runtime' ] )
                    self.WINDOW.setProperty( b_property + "Path",        item[ 'file' ] )
                    self.WINDOW.setProperty( b_property + "Fanart",      item[ 'fanart' ] )
                    self.WINDOW.setProperty( b_property + "Artist",      item[ 'artist' ] )
                    self.WINDOW.setProperty( b_property + "Thumb",       item[ 'thumbnail' ] )
        except:
            print_exc()
        #print locals()

    def _fetch_album_info( self ):
        try:
            # get albums
            albums = self._jsonrpc( 'albums', "AudioLibrary.GetAlbums", '["artist", "year", "thumbnail", "fanart", "rating"]' )
            # set total value
            self.WINDOW.setProperty( "RandomAlbum.Count", str( len( albums ) ) )
            if albums:
                # enumerate thru our records
                for count, item in self._get_generate_random_items( albums ):
                    # set base property
                    b_property = "RandomAlbum.%d." % ( count )
                    # set our properties
                    self.WINDOW.setProperty( b_property + "Title",  item[ 'label' ] )
                    self.WINDOW.setProperty( b_property + "Rating", ( str( item[ 'rating' ] ), "" )[ str( item[ 'rating' ] ) == '48' ] )
                    self.WINDOW.setProperty( b_property + "Year",   str( item[ 'year' ] ) )
                    self.WINDOW.setProperty( b_property + "Artist", item[ 'artist' ] )
                    self.WINDOW.setProperty( b_property + "Path",   'RunScript(%s,albumid=%s)' % ( __addonid__, str( item[ 'albumid' ] ) ) )
                    self.WINDOW.setProperty( b_property + "Fanart", item[ 'fanart' ] )
                    self.WINDOW.setProperty( b_property + "Thumb",  item[ 'thumbnail' ] )
        except:
            print_exc()
        #print locals()

    def _fetch_song_info( self ):
        try:
            # get songs
            songs = self._jsonrpc( 'songs', "AudioLibrary.GetSongs", '["playcount", "artist", "album", "year", "file", "thumbnail", "fanart", "rating"]' )
            # set total value
            self.WINDOW.setProperty( "RandomSong.Count", str( len( songs ) ) )
            if songs:
                # enumerate thru our records
                for count, item in self._get_generate_random_items( songs ):
                    # set base property
                    b_property = "RandomSong.%d." % ( count )
                    # set our properties
                    self.WINDOW.setProperty( b_property + "Title",  item[ 'label' ] )
                    self.WINDOW.setProperty( b_property + "Rating", str( int( item[ 'rating' ] ) - 48 ) )
                    self.WINDOW.setProperty( b_property + "Year",   str( item ['year' ] ) )
                    self.WINDOW.setProperty( b_property + "Artist", item[ 'artist' ] )
                    self.WINDOW.setProperty( b_property + "Album",  item[ 'album' ] )
                    self.WINDOW.setProperty( b_property + "Path",   item[ 'file' ] )
                    self.WINDOW.setProperty( b_property + "Fanart", item[ 'fanart' ] )
                    self.WINDOW.setProperty( b_property + "Thumb",  item[ 'thumbnail' ] )
        except:
            print_exc()
        #print locals()

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
                    self.WINDOW.setProperty( b_property + "Summary", summary )
                    self.WINDOW.setProperty( b_property + "Name",    re.search( '<addon.*?name="(.*?)"', str_xml, re.S ).group( 1 ) )
                    self.WINDOW.setProperty( b_property + "Author",  re.search( '<addon.*?provider-name="(.*?)"', str_xml, re.S ).group( 1 ) )
                    self.WINDOW.setProperty( b_property + "Version", re.search( '<addon.*?version="(.*?)"', str_xml, re.S ).group( 1 ) )
                    self.WINDOW.setProperty( b_property + "Fanart",  addon_xml.replace( 'addon.xml', 'fanart.jpg' ) )
                    self.WINDOW.setProperty( b_property + "Thumb",   addon_xml.replace( 'addon.xml', 'icon.png' ) )
                    self.WINDOW.setProperty( b_property + "Type",    "".join( re.findall( '<provides>(.*?)</provides>', str_xml ) ) or "executable" )
                    self.WINDOW.setProperty( b_property + "Path",    re.search( '<addon.*?id="(.*?)"', str_xml, re.S ).group( 1 ) )
                    #
                    #print "Addon: %r" % self.WINDOW.getProperty( b_property + "Path" )
        except:
            print_exc()
        #print locals()

    def _Play_Album( self, ID ):
        # create a playlist
        playlist = xbmc.PlayList(0)
        # clear the playlist
        playlist.clear()
        try:
            # add songs
            for item in self._jsonrpc( 'songs', "AudioLibrary.GetSongs", '["file", "thumbnail", "fanart"], "albumid":%s' % ID ):
                listitem = xbmcgui.ListItem( item[ 'label' ], "", item[ 'thumbnail' ], item[ 'thumbnail' ] )
                listitem.setProperty( "fanart_image", item['fanart'] )
                playlist.add( item[ 'file' ], listitem )
        except:
            print_exc()
        # play the playlist
        if playlist.size():
            xbmc.Player().play( playlist )


def time_took( t ):
    t = ( time.time() - t )
    if t >= 60: return "%.3fm" % ( t / 60.0 )
    if 0 < t < 1: return "%.3fms" % ( t )
    return "%.3fs" % ( t )


if ( __name__ == "__main__" ):
    log( 'script started' )
    Main()
    log( "time took %s" % time_took( start_time ), xbmc.LOGNOTICE )
    log( 'script stopped' )
