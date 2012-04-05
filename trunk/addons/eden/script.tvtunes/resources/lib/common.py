# -*- coding: utf-8 -*-

import os
import re
import sys
import time
import unicodedata

import xbmc
import xbmcgui
from xbmcaddon import Addon

from utils.log import logAPI


# constants
LOGGER    = logAPI()

Addon     = Addon( 'script.tvtunes' )
AddonID   = Addon.getAddonInfo( 'id' )
AddonName = Addon.getAddonInfo( 'name' )
AddonPath = Addon.getAddonInfo( 'path' )
AddonData = Addon.getAddonInfo( 'profile' )

# languages
Language = Addon.getLocalizedString
LangXBMC = xbmc.getLocalizedString

# default theme name
THEME_FILE = "theme.mp3"

try:
    import xbmcvfs
except ImportError:
    sys.path.append( os.path.join( AddonPath, "resources", "script.module.xbmcvfs", "lib" ) )
    import xbmcvfs


def _unicode( text, encoding='utf-8' ):
    try: text = unicode( text, encoding, errors="ignore" )
    except: pass
    return text


def IsTrue( text ):
    return ( text.lower() == "true" )


def time_took( t ):
    t = ( time.time() - t )
    if t >= 60: return "%.3fm" % ( t / 60.0 )
    if 0 < t < 1: return "%.3fms" % ( t )
    return "%.3fs" % ( t )


def hide_parts_path( path, end=0 ):
    # first normalize the path (win32 support / as path separators)
    path = path.replace( "\\", "/" )
    # split our drive letter
    drive, tail = os.path.splitdrive( path )
    # split the rest of the path
    parts = tail.split( "/" )
    # set end hidden
    if not end: end = int( len( parts ) / 2 )
    # replace part by '..'
    start = ( 2, 1 )[ bool( parts[ 1 ] ) ]
    for i in range( start, start+end ):
        parts[ i ] = ".."
    # return path
    return drive + "/".join( parts )


def normalize_string( text ):
    try: text = unicodedata.normalize( 'NFKD', _unicode( text ) ).encode( 'ascii', 'ignore' )
    except: pass
    # remove illegal characters and return normalized string
    return re.sub( '[\\/:*?"<>|,=;+]', '', text )


def path_exists( filename ):
    # first use os.path.exists and if not exists, test for share with xbmcvfs.
    return os.path.exists( filename ) or xbmcvfs.exists( filename )


def fix_path( fixpath ):
    # fix path
    if fixpath.lower().startswith( "smb://" ) and IsTrue( Addon.getSetting( "smb_share" ) ):
        #remove share
        fixpath = fixpath.replace( "smb://", "" ).replace( "SMB://", "" )
        # add login and pass
        login = Addon.getSetting( "smb_login" )
        if login and not fixpath.startswith( login ):
            fixpath = "%s:%s@%s" % ( login, Addon.getSetting("smb_psw"), fixpath )
        fixpath = "smb://" + fixpath

    elif fixpath.lower().startswith( "ftp://" ) and IsTrue( Addon.getSetting( "ftp_share" ) ):
        #remove share
        fixpath = fixpath.replace( "ftp://", "" ).replace( "FTP://", "" )
        # add login and pass
        login = Addon.getSetting( "ftp_login" )
        if login and not fixpath.startswith( login ):
            fixpath = "%s:%s@%s" % ( login, Addon.getSetting("ftp_psw"), fixpath )
        fixpath = "ftp://" + fixpath

    return fixpath


def getThemePath( path, path2="", tvshowtitle="", default_folder=True, separate=True, updir=4 ):
    #print locals()
    # check in custom path
    if path2 and tvshowtitle and not default_folder:
        # normalize the path (win32 support / as path separators) and make sure endswith by /
        path2 = path2.replace( "\\", "/" ).rstrip( "/" ) + "/" # setting "customtunesfolder"
        # set normalized title
        tvshowtitle = normalize_string( tvshowtitle )
        if separate:
            tune = path2 + tvshowtitle + "/" + THEME_FILE
        else:
            tune = path2 + tvshowtitle + ".mp3"
        if path_exists( tune ):
            return tune

    # normalize the path (win32 support / as path separators) and make sure endswith by /
    path = path.replace( "rar://", "", 1 ).replace( "\\", "/" ).rstrip( "/" ) + "/" # tv show path
    path = fix_path( path )

    # if default_folder or not found in custom path
    tune = path + THEME_FILE
    if path_exists( tune ):
        return tune

    # move up x directories on thepath
    fpath = path.rstrip( "/" )
    for i in xrange( updir ):
        fpath = os.path.dirname( fpath )
        tune = fpath + "/" + THEME_FILE
        if path_exists( tune ):
            return tune

    return ""


def getTVShows( format="list", isReload=False ):
    # on recup la liste des series en biblio
    if isReload:
        import xbmcaddon
        globals().update( { "Addon": xbmcaddon.Addon( 'script.tvtunes' ) } )
        del xbmcaddon
    # start time
    st = time.time()
    # list of tvshows
    tvshows = []
    # execute JSONRPC if supported
    if hasattr( xbmc, "executeJSONRPC" ):
        from utils.jsonrpc import jsonrpcAPI
        jsonapi = jsonrpcAPI()
        # json statement for get tvshows
        tvshows = jsonapi.VideoLibrary.GetTVShows( properties=[ "file", "thumbnail" ],
            sort={ "method": "label", "order": "ascending" } ).get( "tvshows", [] )

    # fixe me: check if file is empty, reset if empty
    if tvshows and not tvshows[ 0 ].get( "file" ):
        tvshows = []

    # use sql if tvshows is empty or running on XBMC4Xbox
    if not tvshows:
        from urllib import quote_plus
        # sql statement for tv shows
        sql_data = "SELECT tvshow.c00, path.strPath FROM tvshow, path, tvshowlinkpath WHERE path.idPath=tvshowlinkpath.idPath AND tvshow.idShow=tvshowlinkpath.idShow GROUP BY tvshow.c00"
        # get tvshows
        xml_data = xbmc.executehttpapi( "QueryVideoDatabase(%s)" % quote_plus( sql_data ), )
        # set list of tvshows
        for label, file in re.findall( "<field>(.*?)</field><field>(.*?)</field>", xml_data, re.DOTALL ):
            # get cached thumb
            c_thumb = xbmc.getCacheThumbName( file )
            icon = "special://profile/Thumbnails/Video/%s/%s" % ( c_thumb[ 0 ], c_thumb )
            # add show to listing
            tvshows.append( { "label": _unicode( label ), "file": file, "thumbnail": icon } )

    # print time to parse tvshows
    LOGGER.notice.LOG( "Getting TVShows took %s", time_took( st ) )

    st = time.time()
    path2 = Addon.getSetting( "customtunesfolder" )
    # reset custom path if not exists
    if not path_exists( path2 ): path2 = ""
    default_folder = IsTrue( Addon.getSetting( "savetuneintvshowfolder" ) )
    separate       = IsTrue( Addon.getSetting( "saveinseparatefolder" ) )

    listitems = []
    for tvshow in tvshows:
        # get tune path
        tune = getThemePath( tvshow[ "file" ], path2, tvshow[ "label" ], default_folder, separate )
        #print "%r" % tune
        # initialize listitem
        listitem = xbmcgui.ListItem( tvshow[ "label" ], tvshow[ "file" ], tvshow[ "thumbnail" ] )
        listitem.setPath( tvshow[ "file" ] )
        # set images properties
        banner = tvshow[ "file" ] + "banner.jpg"
        listitem.setProperty( "banner", ( "", banner )[ path_exists( banner ) ] )
        logo = tvshow[ "file" ] + "logo.png"
        listitem.setProperty( "logo", ( "", logo )[ path_exists( logo ) ] )
        # set tune properties
        listitem.setProperty( "tune", tune )
        listitem.setProperty( "IsPlayable", ( "", "true" )[ tune != "" ] )
        # set music info
        listitem.setInfo( 'music', { 'title': tvshow[ "label" ], 'Artist': 'TvTunes', 'Album': 'Eden-pre' } )
        # add item
        if format == "dict":
            listitem = ( tvshow[ "label" ], listitem )
        listitems.append( listitem )
    if format == "dict":
        listitems = dict( listitems )
    # print time to set list
    LOGGER.notice.LOG( "Setup listitems took %s", time_took( st ) )

    # return listing
    return listitems


class Info:
    def __init__( self, *args, **kwargs ):
        # update dict with our formatted argv
        try:
            args   = "".join( sys.argv[ 1:2 ] ).replace( "&amp;", "&" )
            params = dict( [ arg.split( "=" ) for arg in args.split( "&" ) ] )
            self.__dict__.update( params )
        except ValueError: pass
        except: LOGGER.error.print_exc()
        # update dict with custom kwargs
        self.__dict__.update( kwargs )

    def __getattr__( self, namespace ):
        return self[ namespace ]

    def __getitem__( self, namespace ):
        return self.get( namespace )

    def __setitem__( self, key, default="" ):
        self.__dict__[ key ] = default

    def get( self, key, default="" ):
        return self.__dict__.get( key, default ).lower()

    def isempty( self ):
        return not bool( self.__dict__ )

    def IsTrue( self, key, default="false" ):
        return IsTrue( self.get( key, default ) )
