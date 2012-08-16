
# Modules general
import os
import re
import sys
import time
import urllib
from traceback import print_exc

# Modules XBMC
import xbmc
import xbmcgui
import xbmcvfs
from xbmcaddon import Addon

try:
    import json
    # test json
    json.loads( "[null]" )
except:
    import simplejson as json


# constants
ADDON      = Addon( "plugin.program.repo.installer" )
ADDON_DIR  = ADDON.getAddonInfo( "path" )

#Language = ADDON.getLocalizedString # ADDON strings
LangXBMC = xbmc.getLocalizedString # XBMC strings

# set cached filename
C_FILENAME = xbmc.translatePath( ADDON.getAddonInfo( 'profile' ) + 'repos.json' )
if not xbmcvfs.exists( ADDON.getAddonInfo( 'profile' ) ):
    xbmcvfs.mkdir( ADDON.getAddonInfo( 'profile' ) )

OPEN_FILE = open
if hasattr( xbmcvfs, "File" ):
    OPEN_FILE = xbmcvfs.File


class _urlopener( urllib.FancyURLopener ):
    version = "Mozilla/5.0 (Windows NT 5.1; rv:14.0) Gecko/20100101 Firefox/14.0.1"
urllib._urlopener = _urlopener()


def getIdAndVersion( a ):
    ID = a[ :-3 ]
    version = "".join( re.compile( "(\\d+\.)" ).findall( ID ) )
    if version: ID = ID.split( version )[ 0 ]
    return ID.strip( "." ).strip( "-" ), version.strip( "." )


def path_exists( filename ):
    # first use os.path.exists and if not exists, test for share with xbmcvfs.
    return os.path.exists( filename ) or xbmcvfs.exists( filename )


def loadRepos():
    repos = {}
    expired = True
    try:
        if path_exists( C_FILENAME ):
            expired = time.time() >= ( os.path.getmtime( C_FILENAME ) + ( 1 * 60**2 ) ) # 1 hours
            f = OPEN_FILE( C_FILENAME )
            b = f.read().strip( "\x00" )
            f.close()
            repos = json.loads( b )
    except:
        print_exc()
    return repos, expired


def saveRepos( repos ):
    ok = False
    try:
        b = json.dumps( repos, sort_keys=True, indent=2 )
        f = OPEN_FILE( C_FILENAME, "w" )
        f.write( b )
        f.close()
        ok = True
    except:
        print_exc()
    return ok


def parseRepos( html, repos={} ):
    try:
        repos[ "*" ] = "".join( re.compile( 'timestamp="(.*?)"' ).findall( html ) )
        regexp = '\{\|border=&quot;1&quot; cellpadding=&quot;2&quot; cellspacing=&quot;0&quot; width=&quot;100%&quot;.*?\|-(.*?)\|\}'
        strRepos = "".join( re.compile( regexp, re.S ).findall( html ) )
        for count, repo in enumerate( strRepos.strip( "\n" ).split( "|-" )[ 1: ] ):
            try:
                url_name, plot, owner, zip_name, icon = repo.replace( "\n", "" ).split( "|" )[ 1: ]
                urlrepo, title  = url_name.strip( "[]" ).split( " ", 1 )
                urlzip, zipname = zip_name.strip( "[]" ).split( " ", 1 )
                ID, version = getIdAndVersion( zipname.strip() )

                if "http" in title:
                    s = title.replace( "[", "" ).replace( "]", "" ).split()
                    title = " ".join( t for t in s if not t.startswith( "http" ) )

                if not repos.get( ID ):
                    repos[ ID ] = {}

                repos[ ID ].update( {
                    "title":    title,
                    "id":       ID,
                    "version":  version,
                    "url":      urlrepo,
                    "plot":     plot,
                    "author":   owner,
                    "file":     urlzip,
                    "filename": zipname.strip(),
                    "icon":     icon.strip( "[]" ),
                    } )
            except:
                print_exc()
    except:
        print_exc()

    return repos


def getRepos():
    """ fetch the json repos source """
    repos, expired = loadRepos()
    try:
        if expired or not repos:
            url = "http://wiki.xbmc.org/api.php?format=xml&action=query&titles=Unofficial%20add-on%20repositories&prop=revisions&rvprop=content|timestamp"
            #url = "http://wiki.xbmc.org/index.php?title=Unofficial_add-on_repositories&action=edit"
            sock = urllib.urlopen( url )
            html = sock.read()
            sock.close()

            repos = parseRepos( html, repos )
            if repos:
                ok = saveRepos( repos )
    except:
        try: xbmcvfs.delete( C_FILENAME )
        except: pass
        print_exc()

    return repos


def setRealAddonID( ID, repos, zip_file ):
    try:
        # get real addon id
        from zipfile import ZipFile
        zip = ZipFile( zip_file, "r" )
        namelist = zip.namelist()
        zip.close()
        root_name = namelist[ 0 ].strip( "/" )

        addon_xml = xbmc.translatePath( "special://home/addons/%s/addon.xml" % root_name )
        if path_exists( addon_xml ):
            f = OPEN_FILE( addon_xml )
            b = f.read()
            f.close()
            addonID = re.search( '<addon.*?id="(.*?)"', b ).group( 1 )
            repos[ ID ].update( { "addonID": addonID } )
            saveRepos( repos )
            ID = addonID
    except:
        print_exc()
    return ID


def installRepo( ID ):
    try:
        repos = loadRepos()[ 0 ]
        repo = repos[ ID ]

        src = repo[ "file" ]
        dst = xbmc.translatePath( "special://home/addons/packages/" + repo[ "filename" ] )
        ok  = xbmcvfs.copy( src, dst )

        if ok:
            xbmc.executebuiltin( 'XBMC.Extract(%s,%s)' % ( dst, xbmc.translatePath( "special://home/addons/" ) ) )
            xbmc.sleep( 1000 )

            ID = setRealAddonID( ID, repos, dst )

            xbmc.executebuiltin( 'UpdateLocalAddons' )
            xbmc.sleep( 100 )
            xbmc.executebuiltin( "Container.Refresh" )

            icon = xbmc.getInfoLabel( "system.addonicon(%s)" % ID )
            header = xbmc.getInfoLabel( "system.addontitle(%s)" % ID )
            xbmc.executebuiltin( "XBMC.Notification(%s,%s,5000,%s)" % ( header, LangXBMC( 24064 ).encode( "utf-8" ), icon ) )

        else:
            header = repo[ "title" ].encode( "utf-8" )
            xbmc.executebuiltin( "XBMC.Notification(%s,%s,5000,DefaultIconError.png)" % ( header, LangXBMC( 24030 ).encode( "utf-8" ) ) )

        print ( "RepoInstaller", ok, src, dst )
    except:
        print_exc()


def fixeDialogAddonInfo():
    try:
        # fixe skin xml
        id50 = """<controls>
		<control type="list" id="50">
			<visible>false</visible>
		</control>"""
        for res in [ "720p", "1080i" ]:
            x = xbmc.translatePath( "special://skin/%s/DialogAddonInfo.xml" % res )
            if xbmcvfs.exists( x ):
                f = OPEN_FILE( x )
                strxml = f.read()
                f.close()
                if not 'id="50"' in strxml:
                    strxml = strxml.replace( "<controls>", id50 )
                    f = OPEN_FILE( x, "w" )
                    f.write( strxml )
                    f.close()
    except:
        print_exc()
