"""
    Script Meet Dependencies!
    by Frost (passion-xbmc.org)

    Method use:
      - RunScript(SCRIPT[,INFO,DATADIR,ADDON1,ADDON2,ADDON?,silent])
        SCRIPT = le chemin du dependencies.py

    Params: (si aucun params est indiquer, le script va scanner pour les deps du skin.)
      - INFO       = [opt] URL du addons.xml ou ce trouve la dep
      - DATADIR    = [opt] URL du repertoire des addons du repo pour la dep
      - ADDONS     = [opt] l'id de(s) dep(s) (peut etre multiple, juste a separer par une virgule)
      - Last param = [opt] silent, si on veut pas voir la progression et ni de dialog ok (suffit de mettre silent comme bon dernier)

    Exemple: (Pour tous les deps du skin)
      - RunScript(special://skin/scripts/dependencies.py)
        RunScript(special://skin/scripts/dependencies.py,silent)

    Exemple: (Pour une seule dep)
      - RunScript(special://skin/scripts/dependencies.py,http://passion-xbmc.org/addons/addons.php/11.0,http://passion-xbmc.org/addons/Download.php,script.metadata.actors)
        RunScript(special://skin/scripts/dependencies.py,http://passion-xbmc.org/addons/addons.php/11.0,http://passion-xbmc.org/addons/Download.php,script.metadata.actors,silent)

    Exemple: (Pour plusieurs deps sur le meme repo)
      - RunScript(special://skin/scripts/dependencies.py,http://passion-xbmc.org/addons/addons.php/11.0,http://passion-xbmc.org/addons/Download.php,script.metadata.actors,script.moviesets)
        RunScript(special://skin/scripts/dependencies.py,http://passion-xbmc.org/addons/addons.php/11.0,http://passion-xbmc.org/addons/Download.php,script.metadata.actors,script.moviesets,silent)
"""


import time
START_TIME = time.time()

import os
import re
import sys
import Queue
import socket
import urllib
import zipfile
from traceback import print_exc
from xml.sax.saxutils import unescape

import xbmc
import xbmcgui
import xbmcvfs

ADDONS_DIR      = "special://home/addons/"
PACKAGES_DIR    = ADDONS_DIR + "packages/"


class Stack( Queue.Queue ):
    "Thread-safe stack"
    # method aliases
    push = Queue.Queue.put
    pop  = Queue.Queue.get
    pop_nowait = Queue.Queue.get_nowait
    def _put( self, item ):
        # add at the end, if not exists
        if item not in self.queue:
            self.queue.append( item )
    def add( self, items ):
        for item in items:
            self.push( item )


class _urlopener( urllib.FancyURLopener ):
    version = "Mozilla/5.0 (Windows NT 5.1; rv:12.0) Gecko/20100101 Firefox/12.0"
urllib._urlopener = _urlopener()
socket.setdefaulttimeout( 20 )


def updateLocalAddonsAndAddonRepos():
    # update local addons and repos
    for up in [ 'UpdateLocalAddons', 'UpdateAddonRepos' ]:
        xbmc.executebuiltin( up )
        xbmc.sleep( 100 )


def getAddons( info, datadir, addonsid ):
    addons = []
    dom = None
    xbmc.executebuiltin( 'ActivateWindow(busydialog)' )
    try:
        from xml.dom.minidom import parseString
        dom = parseString( urllib.urlopen( info ).read() )
        for item in dom.getElementsByTagName( "addon" ):
            addonID = item.getAttribute( "id" )
            if addonID in addonsid:
                version = item.getAttribute( "version" )
                url     = "%s/%s/%s-%s.zip" % ( datadir, addonID, addonID, version )
                addons.append( ( item.getAttribute( "name" ), url, addonID, version ) )
                if len( addons ) == len( addonsid ): break
    except:
        print_exc()
    xbmc.executebuiltin( 'Dialog.Close(busydialog,true)' )
    if hasattr( dom, "unlink" ): dom.unlink()
    print "Dependencies for %r : %r" % ( addonsid, addons )
    return addons

def openDB():
    conn = None
    try:
        import sqlite3
        # connect to Addons database
        conn = sqlite3.connect( xbmc.translatePath( "special://Database/Addons15.db" ) )
    except:
        print_exc()
    return conn

def closeDB( conn ):
    if hasattr( conn, "close" ):
        # close database
        conn.close()

def getDependencies( conn, addonID=xbmc.getSkinDir() ):
    deps = []
    try:
        SQL_DEPS = """SELECT addon.name, addon.path, addon.addonID, addon.version FROM addon WHERE addon.addonID IN (SELECT dependencies.addon FROM dependencies WHERE dependencies.id=(SELECT addon.id FROM addon WHERE addon.addonID="%s")) AND addon.addonID NOT IN (SELECT broken.addonID FROM broken) ORDER BY addon.addonID, addon.version""" % addonID # DESC
        #print SQL_DEPS
        deps = conn.execute( SQL_DEPS ).fetchall()
    except:
        print_exc()
    print "Dependencies for %r : %r" % ( addonID, deps )
    return deps



def get_repo_list_items( url, items=[] ):
    #print url
    sock = urllib.urlopen( url.replace( " ", "%20" ) )
    html = sock.read()
    sock.close()
    if "404 Not Found" in html:
        print "Error: 404 Not found %r" % url
        raise
    files = re.compile( '<li><a href="(.*?)">.*?</a></li>' ).findall( html )
    for item in sorted( files, key=lambda f: f.lower().endswith( "/" ) ):
        if item == "../": continue
        item = unescape( item )
        if item.endswith( "/" ):
            items = get_repo_list_items( url + item, items )
        else:
            items.append( url + item )
    return items

def zip_addon_from_repo( name, addonUrl, addonID, version, tempcache="", report=None ):
    # set our zip name
    addon_name = "%s-%s.zip" % ( addonID, version )
    addon_zip  = os.path.join( tempcache, addon_name )
    file_zip   = None
    error      = 0
    try:
        # get all files
        #START_TIME = time.time()
        print "fetching all files from repo..."
        if report: report.update( -1, "Fetching all files from repo...", addonUrl, "Please wait..." )
        items = get_repo_list_items( addonUrl, [] )

        #print time.time() - START_TIME
        #print "-"*100
        #print
        #START_TIME = time.time()

        # open the zip file for writing, and write stuff to it
        file_zip = zipfile.ZipFile( addon_zip, "w" )
        # set our root name
        arcroot = addonID + "/"
        #
        totals  = len( items )
        diff    = 100.0 / totals
        percent = 0
        # enum files and download to it
        for count, item in enumerate( items ):
            percent += diff
            count   += 1
            # set our arcname
            arcname = arcroot + item.replace( addonUrl, "" ).replace( "%20", " " )
            #print "%i%% Compressing %i of %i :  %s" % ( int( percent ), count, totals, arcname )
            if report:
                line1 = "Downloading %i of %i items %i%%" % ( count, totals, int( percent ) )
                report.update( int( percent ), line1, arcname, "Please wait..." )
            try:
                # download item
                fp, h = urllib.urlretrieve( item, os.path.join( tempcache, os.path.basename( item ) ) )
                # add to file_zip
                file_zip.write( fp, arcname )#, zipfile.ZIP_DEFLATED )
                try: os.remove( fp )
                except: pass
            except:
                error += 1
                print "Error  %s" % arcname
                print_exc()
                break
        #print time.time() - START_TIME
        #print "-"*100
    except:
        error += 1
        print_exc()

    if hasattr( file_zip, 'close' ):
        file_zip.close()

    if not error:
        print "Everything is Ok"
    else:
        print "Everything is not Ok, %i Error!" % error
        try: os.remove( addon_zip )
        except: pass
        addon_zip = None
    return addon_zip


def download( addons, silent=False ):
    DIALOG_PROGRESS = xbmcgui.DialogProgress()
    def _pbhook( numblocks, blocksize, filesize, ratio=1.0 ):
        if not silent:
            try: pct = int( min( ( numblocks * blocksize * 100 ) / filesize, 100 ) * ratio )
            except: pct = 100
            DIALOG_PROGRESS.update( pct )
            if DIALOG_PROGRESS.iscanceled():
                raise IOError
    REPORTHOOK = lambda nb, bs, fs: _pbhook( nb, bs, fs )

    if not silent: DIALOG_PROGRESS.create( "Skin Meet Dependencies!" )
    totals = len( addons )
    diff = 100.0 / totals
    percent = 0
    installed = 0
    for i, dep in enumerate( addons ):
        percent += diff
        name, url, addonID, version = dep
        line1 = "Dep %i of %i (%s)" % ( i+1, totals, name )
        if not silent: DIALOG_PROGRESS.update( int( percent ), line1, url, "Downloading Please wait..." )

        fp = None
        print url
        if url.lower().endswith( ".zip" ):
            dest = xbmc.translatePath( PACKAGES_DIR + os.path.basename( url ) )
            try: fp, h = urllib.urlretrieve( url, dest, REPORTHOOK )
            except IOError: xbmcvfs.delete( dest )
            except: print_exc()
        else:
            # download directory
            tempcache = xbmc.translatePath( PACKAGES_DIR )
            report = not silent and DIALOG_PROGRESS
            fp = zip_addon_from_repo( name, url, addonID, version, tempcache, report )

        if fp and xbmcvfs.exists( fp ):
            if not silent: DIALOG_PROGRESS.update( int( percent ), line1, ADDONS_DIR + addonID, "Installing Please wait..." )
            xbmc.executebuiltin( "XBMC.Extract(%s,%s)" % ( fp, xbmc.translatePath( ADDONS_DIR ) ) )
            xbmc.sleep( 1000 )
            installed += 1

        print fp #, str( h ).replace( "\r", "" )
        print "-"*100
        if not silent and DIALOG_PROGRESS.iscanceled():
            break

    print time.time()-START_TIME
    if not silent: DIALOG_PROGRESS.close()

    return installed


def Main( install=None ):
    # parse sys.argv
    silent = sys.argv[ -1 ].lower() == "silent"
    args   = sys.argv[ 1: ]
    if silent: args = args[ :-1 ]

    # connect to Addons database
    conn  = openDB()
    stack = Stack( 0 )
    # push deps on stack
    if install: stack.add( install )
    elif not args: stack.add( getDependencies( conn ) )
    else: stack.add( getAddons( args[ 0 ], args[ 1 ].rstrip( "/" ), args[ 2: ] ) )

    # meet only if system has not addon
    meet = []
    try:
        while stack.qsize():
            dep = stack.pop()
            #don't visit if in meet
            if dep not in meet:
                addonID = dep[ 2 ]
                stack.add( getDependencies( conn, addonID ) )
                cond = "System.HasAddon(%s)" % addonID
                if xbmc.getCondVisibility( cond ):
                    print cond
                else:
                    meet.append( dep )
    except Queue.Empty:
        pass
    closeDB( conn )

    print "Meet: %r" % meet
    # if missing addons download this
    if meet:
        installed = download( meet, silent ) or 0
        message = "Installed %i of %i Dependencies" % ( installed, len( meet ) )
        # update local addons and repos
        updateLocalAddonsAndAddonRepos()
    else:
        message = "Dependencies are already installed or not found!"
    if not silent:
        xbmcgui.Dialog().ok( "Skin Meet Dependencies!", message )



if ( __name__ == "__main__" ):
    updateLocalAddonsAndAddonRepos()
    Main()
