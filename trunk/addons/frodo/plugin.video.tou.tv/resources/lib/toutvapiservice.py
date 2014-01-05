import os
import re
import urllib

try:
    import json
except ImportError:
    import simplejson as json

from utilities import *

DEBUG = False

API_SERVICE_URL         = "http://api.tou.tv/v1/toutvapiservice.svc/json/"
THEPLATFORM_CONTENT_URL = "http://release.theplatform.com/content.select?pid=%s&format=SMIL" #+"&mbr=true"
VALIDATION_MEDIA_URL    = "http://api.radio-canada.ca/validationMedia/v1/Validation.html?appCode=thePlatform&connectionType=broadband&output=json&"
#VALIDATION_MEDIA_URL2    = "http://api.radio-canada.ca/validationMedia/v1/Validation.html?output=json&appCode=thePlatform&deviceType=LGTV&connectionType=broadband&idMedia=%s"
VALIDATION_MEDIA_URL2    = "http://api.radio-canada.ca/validationMedia/v1/Validation.html?output=json&appCode=thePlatform&deviceType=Android&connectionType=wifi&idMedia=%s"

HTTP_USER_AGENT         = "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.1.1) Gecko/20090715 Firefox/3.5.1"
#HTTP_USER_AGENT         = "Mozilla/5.0 (Windows NT 5.1; rv:7.0.1) Gecko/20100101 Firefox/7.0.1"


def setDebug( yesno ):
    global DEBUG
    DEBUG = yesno


def _print( msg, debug=False ):
    if DEBUG or debug:
        print msg


def json_dumps( data, sort_keys=True, indent=2, debug=False ):
    try:
        str_dump = json.dumps( data, sort_keys=sort_keys, indent=indent )
        if DEBUG or debug:
            _print( str_dump, debug )
            _print( "-"*100, debug )
        return str_dump
    except:
        return "%r" % data


def get_html_source( url, refresh=False, uselocal=False ):
    """ fetch the html source """
    source = ""
    try:
        print "getting html source: %s"%url

        # set cached filename
        source, sock, c_filename = get_cached_source( url, refresh, uselocal, debug=_print )

        if not source or sock is None:
            _print( "Reading online source: %r" % url )
            sock = urllib.urlopen( url )
            source = sock.read()
            if c_filename:
                try: file( c_filename, "w" ).write( source )
                except: print_exc()
        sock.close()
    except:
        print_exc()
    return source


class _urlopener( urllib.FancyURLopener ):
    version = os.environ.get( "HTTP_USER_AGENT" ) or HTTP_USER_AGENT
urllib._urlopener = _urlopener()


class TouTvApi:
    def __init__( self ):
        self.__handler_cache = {}
        #setDebug( True )

    def __getattr__( self, method ):
        if method in self.__handler_cache:
            return self.__handler_cache[ method ]

        def handler( *args, **kwargs ):
            if method.lower() == "theplatform":
                return self.content_select( args[ 0 ], kwargs.get( "refresh", True ) )
            elif method.lower() == "validation":
                return self.validation( **kwargs )
            else:
                return self.getRepertoire( method, **kwargs )

        handler.method = method
        self.__handler_cache[ method ] = handler
        return handler

    def getRepertoire( self, method, **kwargs ):
        start_time = time.time()
        # get params
        refresh = False
        if kwargs.has_key( "refresh" ):
            refresh = kwargs[ "refresh" ]
            kwargs.pop( "refresh" )
        uselocal = False
        if kwargs.has_key( "uselocal" ):
            uselocal = kwargs[ "uselocal" ]
            kwargs.pop( "uselocal" )
        #
        url = API_SERVICE_URL + method
        query = urllib.urlencode( kwargs )
        if query: url += "?" + query
        #
        content = get_html_source( url, refresh, uselocal )
        data = json.loads( content ).get( "d" )
        #
        _print( "[TouTvApi] %s took %s" % ( method, time_took( start_time ) ) )
        json_dumps( data )
        return data

    def content_select( self, PID, refresh=True ):
        start_time = time.time()
        content = get_html_source( VALIDATION_MEDIA_URL2 % PID, refresh )

        jdata = json.loads(content)
        rtsp_url = jdata['url']
        rtsp_url = re.compile('(.+?)\\?').findall(rtsp_url)[0]    # Find the mp4 rtsp link
        rtsp_url = rtsp_url.replace('_800.', '_1200.');           # We want the best quality...

        _print( "[TouTvApi] thePlatform took %s" % time_took( start_time ) )
        json_dumps( jdata )
        return rtsp_url

    def validation( self, **kwargs ):
        start_time = time.time()
        kwargs[ "deviceType" ] = kwargs.get( "deviceType" ) or "iphone4" #ipad"
        refresh = True
        if kwargs.has_key( "refresh" ):
            refresh = kwargs[ "refresh" ]
            kwargs.pop( "refresh" )
        content = get_html_source( VALIDATION_MEDIA_URL + urllib.urlencode( kwargs ), refresh )
        data = json.loads( content )
        #
        _print( "[TouTvApi] Validation took %s" % time_took( start_time ) )
        json_dumps( data )
        return data


if ( __name__ == "__main__" ):
    setDebug( True )
    toutvapi = TouTvApi()

    toutvapi.GetPays()

    #toutvapi.GetPageRepertoire()
    #toutvapi.GetPageAccueil()
    #toutvapi.GetGenres()
    #toutvapi.GetCollections()
    #toutvapi.GetEmissions()
    #toutvapi.GetPageGenre( genre="animation" )
    #toutvapi.GetPageEmission( emissionId=2041271036 ) # digit
    #toutvapi.GetPageEpisode( episodeId=2060099162 ) # digit
    #toutvapi.GetCarrousel( playlistName="carrousel-animation" )
    #toutvapi.SearchTerms( query="vie de quartier"  )

    #print toutvapi.theplatform( '2S7KnmMzf3qdFokIL61ORofYT7vh73Am', refresh=True )

    # not supported on xbmc is m3u8 file type
    #toutvapi.validation( idMedia='2S7KnmMzf3qdFokIL61ORofYT7vh73Am', refresh=True )
