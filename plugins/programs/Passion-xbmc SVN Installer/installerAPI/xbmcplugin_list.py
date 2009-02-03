"""
svn repo installer plugin

Nuka1195
"""

# main imports
import sys
import os
import xbmc
import xbmcgui
import xbmcplugin

import urllib
import re
from xml.sax.saxutils import unescape


class Parser:
    """ Parser Class: grabs all tag versions and urls """
    # regexpressions
    revision_regex = re.compile( '<h2>.+?Revision ([0-9]*): ([^<]*)</h2>' )
    asset_regex = re.compile( '<li><a href="([^"]*)">([^"]*)</a></li>' )

    def __init__( self, htmlSource ):
        # set our initial status
        self.dict = { "status": "fail", "revision": 0, "assets": [], "url": "" }
        # fetch revision number
        self._fetch_revision( htmlSource )
        # if we were successful, fetch assets
        if ( self.dict[ "revision" ] != 0 ):
            self._fetch_assets( htmlSource )

    def _fetch_revision( self, htmlSource ):
        try:
            # parse revision and current dir level
            revision, url = self.revision_regex.findall( htmlSource )[ 0 ]
            # we succeeded :), set our info
            self.dict[ "url" ] = url
            self.dict[ "revision" ] = int( revision )
        except:
            pass

    def _fetch_assets( self, htmlSource ):
        try:
            assets = self.asset_regex.findall( htmlSource )
            if ( len( assets ) ):
                for asset in assets:
                    if ( asset[ 0 ] != "../" ):
                        self.dict[ "assets" ] += [ unescape( asset[ 0 ] ) ]
                self.dict[ "status" ] = "ok"
        except:
            pass


class _Info:
    def __init__( self, *args, **kwargs ):
        self.__dict__.update( kwargs )


class Main:
    # base path
    BASE_CACHE_PATH = os.path.join( xbmc.translatePath( "P:\\Thumbnails" ), "Pictures" )

    def __init__( self ):
        # if this is first run list all the repos
        if ( sys.argv[ 2 ] == "" ):
            ok = self._get_repos()
        else:
            # parse sys.argv for our current url
            self._parse_argv()
            # get the repository info
            self._get_repo_info()
            # get the list
            ok = self._show_categories()
        # send notification we're finished, successfully or unsuccessfully
        xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=ok )

    def _parse_argv( self ):
        # call _Info() with our formatted argv to create the self.args object
        exec "self.args = _Info(%s)" % ( urllib.unquote_plus( sys.argv[ 2 ][ 1 : ].replace( "&", ", " ) ), )

    def _get_repos( self ):
        try:
            repos = os.listdir( os.path.join( os.getcwd().replace( ";", "" ), "resources", "repositories" ) )
            # enumerate through the list of categories and add the item to the media list
            for repo in repos:
                if ( os.path.isdir( os.path.join( os.getcwd().replace( ";", "" ), "resources", "repositories", repo ) ) ):
                    url = "%s?category='root'&repo=%s" % ( sys.argv[ 0 ], repr( urllib.quote_plus( repo ) ) )
                    # set the default icon
                    icon = "DefaultFolder.png"
                    # create our listitem, fixing title
                    listitem = xbmcgui.ListItem( repo, iconImage=icon )
                    # set the title
                    listitem.setInfo( type="Video", infoLabels={ "Title": repo } )
                    # add the item to the media list
                    ok = xbmcplugin.addDirectoryItem( handle=int( sys.argv[ 1 ] ), url=url, listitem=listitem, isFolder=True )
                    # if user cancels, call raise to exit loop
                    if ( not ok ): raise
        except:
            # user cancelled dialog or an error occurred
            print "ERROR: %s::%s (%d) - %s" % ( self.__class__.__name__, sys.exc_info()[ 2 ].tb_frame.f_code.co_name, sys.exc_info()[ 2 ].tb_lineno, sys.exc_info()[ 1 ], )
            ok = False
        if ( ok ):
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_LABEL )
        return ok

    def _get_repo_info( self ):
        # path to info file
        repopath = os.path.join( os.getcwd().replace( ";", "" ), "resources", "repositories", self.args.repo, "repo.xml" )
        try:
            # grab a file object
            fileobject = open( repopath, "r" )
            # read the info
            info = fileobject.read()
            # close the file object
            fileobject.close()
            # repo's base url
            self.REPO_URL = re.findall( '<url>([^<]+)</url>', info )[ 0 ]
            # root of repository
            self.REPO_ROOT = re.findall( '<root>([^<]*)</root>', info )[ 0 ]
            # structure of repo
            self.REPO_STRUCTURES = re.findall( '<structure name="([^"]+)" noffset="([^"]+)" install="([^"]*)" ioffset="([^"]+)" voffset="([^"]+)"', info )
            # if category is root, set our repo root
            if ( self.args.category == "root" ):
                self.args.category = self.REPO_ROOT
        except:
            # oops print error message
            print "ERROR: %s::%s (%d) - %s" % ( self.__class__.__name__, sys.exc_info()[ 2 ].tb_frame.f_code.co_name, sys.exc_info()[ 2 ].tb_lineno, sys.exc_info()[ 1 ], )

    def _show_categories( self ):
        ok = False
        # fetch the html source
        items = self._get_items()
        # if successful
        if ( items and items[ "status" ] == "ok" ):
            # if there are assets, we have categories
            ok = self._fill_list( items[ "url" ], items[ "revision" ], items[ "assets" ] )
        return ok

    def _fill_list( self, repo_url, revision, assets ):
        try:
            ok = False
            # enumerate through the list of categories and add the item to the media list
            for item in assets:
                isFolder = True
                for name, noffset, install, ioffset, voffset in self.REPO_STRUCTURES:
                    try:
                        if ( repo_url.split( "/" )[ int( noffset ) ].lower() == name.lower() ):
                            isFolder = False
                            break
                    except:
                        pass
                if ( isFolder ):
                    heading = "category"
                    thumbnail = ""
                else:
                    heading = "download_url"
                    thumbnail = self._get_thumbnail( "%s%s/%sdefault.tbn" % ( self.REPO_URL, repo_url.replace( " ", "%20" ), item.replace( " ", "%20" ), ) )
                url = '%s?%s="%s/%s"&repo=%s&install="%s"&ioffset=%s&voffset=%s' % ( sys.argv[ 0 ], heading, urllib.quote_plus( repo_url ), urllib.quote_plus( item ), repr( urllib.quote_plus( self.args.repo ) ), install, ioffset, voffset, )
                # set the default icon
                icon = "DefaultFolder.png"
                # create our listitem, fixing title
                listitem = xbmcgui.ListItem( urllib.unquote_plus( item[ : -1 ] ), iconImage=icon, thumbnailImage=thumbnail )
                # set the title
                listitem.setInfo( type="Video", infoLabels={ "Title": urllib.unquote_plus( item[ : -1 ] ) } )
                # add the item to the media list
                ok = xbmcplugin.addDirectoryItem( handle=int( sys.argv[ 1 ] ), url=url, listitem=listitem, isFolder=isFolder, totalItems=len( assets ) )
                # if user cancels, call raise to exit loop
                if ( not ok ): raise
        except:
            # user cancelled dialog or an error occurred
            print "ERROR: %s::%s (%d) - %s" % ( self.__class__.__name__, sys.exc_info()[ 2 ].tb_frame.f_code.co_name, sys.exc_info()[ 2 ].tb_lineno, sys.exc_info()[ 1 ], )
            ok = False
        if ( ok ):
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_LABEL )
        return ok

    def _get_items( self ):
        try:
            # open url
            usock = urllib.urlopen( self.REPO_URL + self.args.category )
            # read source
            htmlSource = usock.read()
            # close socket
            usock.close()
            # parse source and return a dictionary
            return self._parse_html_source( htmlSource )
        except:
            # oops print error message
            print "ERROR: %s::%s (%d) - %s" % ( self.__class__.__name__, sys.exc_info()[ 2 ].tb_frame.f_code.co_name, sys.exc_info()[ 2 ].tb_lineno, sys.exc_info()[ 1 ], )
            return {}

    def _parse_html_source( self, htmlSource ):
        # initialize the parser
        parser = Parser( htmlSource )
        # return results
        return parser.dict

    def _get_thumbnail( self, thumbnail_url ):
        # make the proper cache filename and path so duplicate caching is unnecessary
        if ( not thumbnail_url.startswith( "http://" ) ): return thumbnail_url
        try:
            filename = xbmc.getCacheThumbName( thumbnail_url )
            filepath = os.path.join( self.BASE_CACHE_PATH, filename[ 0 ], filename )
            # if the cached thumbnail does not exist fetch the thumbnail
            if ( not os.path.isfile( filepath ) ):
                # fetch thumbnail and save to filepath
                info = urllib.urlretrieve( thumbnail_url, filepath )
                # cleanup any remaining urllib cache
                urllib.urlcleanup()
            return filepath
        except:
            # return empty string if retrieval failed
            print "ERROR: %s::%s (%d) - %s" % ( self.__class__.__name__, sys.exc_info()[ 2 ].tb_frame.f_code.co_name, sys.exc_info()[ 2 ].tb_lineno, sys.exc_info()[ 1 ], )
            return ""        
