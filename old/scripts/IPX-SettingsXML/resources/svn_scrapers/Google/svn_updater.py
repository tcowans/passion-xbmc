"""
Update module

Nuka1195
"""

# repository info
REPO_URL     = "http://passion-xbmc.googlecode.com/svn/"
DOWNLOAD_URL = ( "/branches/scripts/IPX-SettingsXML/", "/trunk/scripts/Installer%20Passion-XBMC/" )[ 0 ]
INSTALL      = ""
IOFFSET      = 2
VOFFSET      = 0

# main imports
import sys
import os
import xbmc
import xbmcgui

import urllib
import re
from xml.sax.saxutils import unescape
from traceback import print_exc
from time import strftime


CWD = os.sep.join( os.getcwd().rstrip( ";" ).split( os.sep )[ :-3 ] )

LANGUAGE = xbmc.Language( CWD ).getLocalizedString

DIALOG_PROGRESS = xbmcgui.DialogProgress()


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
            globals()[ "REVISION" ] = str( revision )
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


class Main:
    def __init__( self ):
        # set the repository info
        self.REPO_URL     = REPO_URL
        self.download_url = DOWNLOAD_URL
        self.install      = INSTALL
        self.ioffset      = IOFFSET
        self.voffset      = VOFFSET
        # create the script
        parts = self.download_url.split( "/" )
        version = ""
        if ( self.voffset != 0 ):
            version = " - %s" % ( parts[ self.voffset ].replace( "%20", " " ) )
            del parts[ self.voffset ]
        if not version:
            try: version = " - %s" % ( sys.argv[ 1 ], )
            except: pass
        self.title = parts[ -2 ].replace( "%20", " " ) + version
        # get the list
        self._download_item()

    def _download_item( self ):
        try:
            #if ( xbmcgui.Dialog().yesno( self.title, LANGUAGE( 32000 ), "", "", LANGUAGE( 32020 ), LANGUAGE( 32021 ) ) ):
            DIALOG_PROGRESS.create( self.title, LANGUAGE( 32002 ), LANGUAGE( 32003 ) )
            asset_files = []
            folders = [ self.download_url.replace( " ", "%20" ) ]
            while folders:
                try:
                    htmlsource = self._get_html_source( self.REPO_URL + folders[ 0 ] )
                    if ( not htmlsource ): raise
                    items = self._parse_html_source( htmlsource )
                    if ( not items or items[ "status" ] == "fail" ): raise
                    files, dirs = self._parse_items( items )
                    for file in files:
                        asset_files.append( "%s/%s" % ( items[ "url" ], file, ) )
                    for folder in dirs:
                        folders.append( folders[ 0 ] + folder )
                    folders = folders[ 1 : ]
                except:
                    folders = []
            self._get_files( asset_files )
        except:
            # oops print error message
            print_exc()
            DIALOG_PROGRESS.close()
            xbmcgui.Dialog().ok( self.title, LANGUAGE( 32030 ) )
        
    def _get_files( self, asset_files ):
        """ fetch the files """
        try:
            failed = []
            finished_path = ""
            for cnt, url in enumerate( asset_files ):
                items = os.path.split( url )
                # TODO: Change this to U: for other than xbox
                drive = xbmc.translatePath( ( "U:\\%s" % self.install, "Q:\\%s" % self.install, )[ os.environ.get( "OS", "xbox" ) == "xbox" ] )
                # create the script/plugin/skin title
                parts = items[ 0 ].split( "/" )
                version = ""
                if ( self.voffset != 0 ):
                    version = " - %s" % ( parts[ self.voffset ], )
                    del parts[ self.voffset ]
                    parts[ self.voffset - 1 ] = parts[ self.voffset - 1 ].replace( "%20", " " ) + version
                path = os.path.join( drive, os.path.sep.join( parts[ self.ioffset : ] ).replace( "%20", " " ) )
                if ( not finished_path ): finished_path = path
                file = items[ 1 ].replace( "%20", " " )
                pct = int( ( float( cnt ) / len( asset_files ) ) * 100 )
                DIALOG_PROGRESS.update( pct, "%s %s" % ( LANGUAGE( 32005 ), url, ), "%s %s" % ( LANGUAGE( 32006 ), path, ), "%s %s" % ( LANGUAGE( 32007 ), file, ) )
                # don't allow cancel for update current script
                #if ( DIALOG_PROGRESS.iscanceled() ): raise
                if ( not os.path.isdir( path ) ): os.makedirs( path )
                url = self.REPO_URL + url
                fpath = os.path.join( path, file )
                # ignore files build.sh, build.bat and svn_updater.py
                if fpath.endswith( "build.sh" ) or fpath.endswith( "build.bat" ) or fpath.endswith( "svn_updater.py" ):
                    continue
                try:
                    urllib.urlretrieve( url.replace( " ", "%20" ), fpath )
                except:
                    failed.append( ( url.replace( " ", "%20" ), fpath ) )
                #Create new default.py with __svn_revision__ embedded
                if fpath.endswith( "default.py" ) and os.path.isfile( fpath ):
                    OK = self._write_svn_revision( fpath )
                    if not OK:
                        urllib.urlretrieve( url.replace( " ", "%20" ), fpath )
            # retry to download files failed
            for url, fpath in failed:
                file = os.path.basename( fpath )
                path = os.path.dirname( fpath )
                DIALOG_PROGRESS.update( pct, "%s %s" % ( LANGUAGE( 32005 ), url, ), "%s %s" % ( LANGUAGE( 32006 ), path, ), "%s %s" % ( LANGUAGE( 32007 ), file, ) )
                urllib.urlretrieve( url.replace( " ", "%20" ), fpath )
        except:
            # oops print error message
            print fpath
            print_exc()
            raise
        else:
            DIALOG_PROGRESS.close()
            xbmcgui.Dialog().ok( self.title, LANGUAGE( 32008 ), finished_path )
            # launch script xbmc bug use this !!! :(
            #xbmc.sleep( 1000 )
            #script = os.path.join( CWD, "default.py" )
            #xbmc.executebuiltin( 'XBMC.RunScript(%s)' % ( script, ) )

    def _get_html_source( self, url ):
        try:
            sock = urllib.urlopen( url )
            htmlsource = sock.read()
            sock.close()
            return htmlsource
        except:
            return ""

    def _parse_html_source( self, htmlsource ):
        """ parse html source for tagged version and url """
        try:
            parser = Parser( htmlsource )
            return parser.dict
        except:
            return {}
            
    def _parse_items( self, items ):
        """ separates files and folders """
        folders = []
        files = []
        for item in items[ "assets" ]:
            if ( item.endswith( "/" ) ):
                folders.append( item )
            else:
                files.append( item )
        return files, folders

    def _write_svn_revision( self, script ):
        """ Create new default.py with __svn_revision__ embedded """
        try:
            rev = globals().get( "REVISION", "0" )
            f = open( script, "r" )
            source = f.read()
            f.close()
            f = open( script, "w" )
            f.write( "# %s script Built on %s (SVN:%s) - built with svn_updater.py version 1.0 #\n" % ( self.title, strftime( "%d-%m-%y, %H:%M:%S" ), rev, ) )
            f.write( source.replace( "__svn_revision__ = 0", '__svn_revision__ = "%s"' % rev ) )
            f.close()
            return True
        except:
            return False


if __name__ == "__main__":
    # sleep for xbmc unload others modules
    xbmc.sleep( 1000 )
    Main()
