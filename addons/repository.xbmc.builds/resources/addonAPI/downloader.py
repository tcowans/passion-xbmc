
DEBUG = 0

import os
import sys
import time
import urllib
from tempfile import gettempdir
from traceback import print_exc

try:
    import xbmc
    import xbmcgui
    DIALOG_PROGRESS = xbmcgui.DialogProgress()
except:
    xbmc = None
    xbmcgui = None
    DIALOG_PROGRESS = None


class progressCanceled( Exception ):
    def __init__( self, errmsg="Downloading was canceled by user!" ):
        self.msg = errmsg


# exception raised when downloaded size does not match content-length
class ContentTooShortError( IOError ):
    def __init__( self, message, content ):
        IOError.__init__( self, message )
        self.content = content


class Download:
    """ Download( url[, destination, heading, dlInBackground, reportPercent, windowID, windowProgressID ] )

        url              : string - url to retrieve
        [optional arguments require keyword]
        destination      : [opt] string - filename to save / OS tempdir (default) to save tempfilename.
        heading          : [opt] string - blablabla / (default) url basename
        dlInBackground   : [opt] bool - True=(no dialog progress) / False=(dialog progress(default)).
        reportPercent    : [opt] integer - 25%(default) / percent to report progress ( 0 & 100 auto-reported )( percent=active dialog notif )
        windowID         : [opt] integer - window for setProperty( ... ) / (default) xbmcgui.getCurrentWindowDialogId()
        windowProgressID : [opt] integer - progress ID for window.setProperty( ... ) / None=default

        example:
          - dl = Download( "http://mirrors.xbmc.org/releases/win32/xbmc-r33324-Dharma_beta1.exe" )
          - fp, h = dl.start()
    """

    def __init__( self, *args, **kwargs ):
        # url required
        self.url = args[ 0 ]
        # options
        try: bname = sys.argv[ 2 ]
        except: bname = ""
        self.base_name = bname or os.path.basename( self.url )
        self.destination = kwargs.get( "destination" ) or gettempdir()
        self.destination = os.path.join( self.destination, self.base_name )
        self.heading = kwargs.get( "heading" ) or self.base_name

        # ID de la progression pour les properties du skin ou windowXML
        self.winID = kwargs.get( "windowID" ) or 13000
        self.winProgressID = kwargs.get( "windowProgressID" )
        if self.winProgressID is None: self.baseProperty = ""
        else:
            self.baseProperty = "progress.%s." % self.winProgressID
            self.winControlID = 400 + int( self.winProgressID )

        # DL en arriere-plan default: non
        self.dlInBackground = kwargs.get( "dlInBackground" ) or False
        # list of percent to report/notif - percent 0 et 100 sont auto-notifier
        self.reportTo = kwargs.get( "reportPercent", 25 ) or 100
        self.reportTo = ( 100, self.reportTo )[ self.dlInBackground == True ]
        self.reportPercents = range( 0, 100+self.reportTo, self.reportTo )

        # reset variables
        self.cleanProperties()
        self.cleanWindowProperties()

    def cleanProperties( self ):
        # int property
        self.tinit = 0.0
        self.c_size = 0
        self.t_size = 0
        self.percent = 0
        # str property
        self.currentSize = "" # "0.00" in MB
        self.totalSize = "" # "0.00" in MB
        self.kbps = "" # format: "0.00" in kilobits per second
        self.elapsedTime = "" # format: "%H:%M:%S"
        self.estimatedTimeLeft = "" # format: "%H:%M:%S"
        self.estimatedTotalTime = "" # format: "%H:%M:%S"

    def cleanWindowProperties( self ):
        if self.baseProperty and hasattr( xbmcgui, 'Window' ):
            try:
                winID = self.winID or xbmcgui.getCurrentWindowDialogId()
                win = xbmcgui.Window( winID )
                [ win.clearProperty( self.baseProperty + k ) for k in [ "isAlive", "heading", "url", "filename", "destination",
                    "kbps", "percent", "currentSize", "totalSize", "elapsedTime", "estimatedTimeLeft", "estimatedTotalTime" ]
                    ]
            except ValueError: pass#Window id does not exist
            except:
                print_exc()

    def start( self ):
        """ start retrieve(url) returns (filename, headers) for a local object
            or (tempfilename, headers) for a remote object.
        """
        fpath = headers = ""
        #temps de depart
        self.tinit = time.time()
        try:
            if not self.dlInBackground and hasattr( DIALOG_PROGRESS, 'create' ):
                DIALOG_PROGRESS.create( self.heading )
            fpath, headers = urllib.urlretrieve( self.url, self.destination, self._report_hook )
        except progressCanceled, error:
            fpath, headers = "", error.msg
        except:
            fpath = headers = ""
            print_exc()

        if not self.dlInBackground and hasattr( DIALOG_PROGRESS, 'close' ):
            DIALOG_PROGRESS.close()

        # raise exception if actual size does not match content-length header
        if self.t_size >= 0 and self.c_size < self.t_size:
            message = "Incomplete: got only %i out of %i bytes" % ( self.c_size, self.t_size )
            #content = self.destination, headers
            if hasattr( xbmcgui, 'Dialog' ):
                if xbmcgui.Dialog().yesno( "Confirm Deleting....", "You want to delete what was downloaded?", self.destination, message ):
                    try: os.unlink( self.destination )
                    except:
                        try: os.remove( self.destination )
                        except: print_exc()
            #raise ContentTooShortError( "Retrieval %s" % message, content )

        self.cleanWindowProperties()
        return fpath, headers

    def _report_hook( self, count, blocksize, totalsize ):
        # data writing and/or retrieved in bytes
        self.c_size = ( count * blocksize )
        # taille total en bytes
        self.t_size = totalsize
        # pourcentage de la progression
        self.percent = int( float( self.c_size * 100 ) / ( self.t_size or 1 ) )

        # taille en Mb de recuperer
        self.currentSize = "%.2f" % ( self.c_size / ( 1024.0**2 ) )
        # taille total en Mb
        self.totalSize = ( "%.2f" % ( self.t_size / ( 1024.0**2 ) ) ).strip( "0.0" )

        self.speedTimes()
        self.setDialogs()

    def speedTimes( self ):
        # secondes ecouler depuis le debut
        t = ( time.time() - self.tinit )
        # bits per second
        bps = ( self.c_size / t )
        # secondes restante estimer
        x = ( self.t_size - self.c_size ) / ( bps or 1 )
        # kilobits per second
        self.kbps = "%.02f" % ( bps / 1024.0 )
        # temps ecouler
        self.elapsedTime = time.strftime( "%H:%M:%S", time.gmtime( t ) ).replace( "00:", "", 1 )
        # temps restant estimer
        self.estimatedTimeLeft = time.strftime( "%H:%M:%S", time.gmtime( x ) ).replace( "00:", "", 1 )
        # temps total estimer
        self.estimatedTotalTime = time.strftime( "%H:%M:%S", time.gmtime( t+x ) ).replace( "00:", "", 1 )

    def setDialogs( self ):
        self.notification()
        kill = self.setWindowProperties()
        kill = kill or self.dialogProgress()
        if kill and hasattr( xbmcgui, 'Dialog' ):
            if xbmcgui.Dialog().yesno( "Confirm canceling....", "Are you sure, cancel this download?",
                self.heading ): raise progressCanceled()
            else:
                self.setWindowProperties( True )
                if not self.dlInBackground and hasattr( DIALOG_PROGRESS, 'create' ) and DIALOG_PROGRESS.iscanceled():
                    DIALOG_PROGRESS.create( self.heading )
        #if ( self.percent == 5 ):
        #    print "Test Cancel Download"
        #    raise progressCanceled()

    def setWindowProperties( self, nokill=False ):
        win = None
        if self.dlInBackground and self.baseProperty:
            try:
                winID = self.winID or xbmcgui.getCurrentWindowDialogId()
                win = xbmcgui.Window( winID )
                #print "win = xbmcgui.Window(%s)" % str( winID )
            except: pass
        if win is not None:
            if not nokill and win.getProperty( self.baseProperty + "isAlive" ) == "kill":
                return True

            [ win.setProperty( self.baseProperty + k, v ) for k, v in ( ( "isAlive", "true" ),
                ( "heading", self.heading ),
                ( "url", self.url ),
                ( "filename", self.base_name ),
                ( "destination", self.destination ),
                ( "kbps", self.kbps ),
                ( "percent", "%i" % self.percent ),
                ( "currentSize", self.currentSize ),
                ( "totalSize", self.totalSize ),
                ( "elapsedTime", self.elapsedTime ),
                ( "estimatedTimeLeft", self.estimatedTimeLeft ),
                ( "estimatedTotalTime", self.estimatedTotalTime ) )
                ]
            try: win.getControl( self.winControlID ).setPercent( int( self.percent ) )
            except: pass

    def dialogProgress( self ):
        if self.dlInBackground or not hasattr( DIALOG_PROGRESS, 'update' ): return
        try:
            line1 = "Size: %s%s MB (%s Kbps)" % ( self.currentSize, ( " of %s" % self.totalSize, "" )[ not self.totalSize ], self.kbps )
            line3 = "Time: %s, End: %s, Total time: %s" % ( self.elapsedTime, self.estimatedTimeLeft, self.estimatedTotalTime )
            DIALOG_PROGRESS.update( self.percent, line1, self.destination, line3 )
            return DIALOG_PROGRESS.iscanceled()
        except:
            pass

    def notification( self, line1="", line2="", sleep=4000, icon="DefaultNetwork.png" ):
        if self.percent in self.reportPercents:
            # delete l'index du percent pour pas creer deux fois la meme notification
            try: del self.reportPercents[ self.reportPercents.index( self.percent ) ]
            except: pass
            if hasattr( xbmc, 'executebuiltin' ):
                line1 = "[%i%%] %s" % ( self.percent, self.heading )
                line2 = "Size: %s%s MB (%s Kbps)" % ( self.currentSize, ( " of %s" % self.totalSize, "" )[ not self.totalSize ], self.kbps )
                xbmc.executebuiltin( "XBMC.Notification(%s,%s,%i,%s)" % ( line1, line2, sleep, icon ) )

        self._debug()

    def _debug( self, force=0 ):
        if force or DEBUG:
            print "[%i%%] %s" % ( self.percent, self.heading )
            print "Size: %s%s MB (%s Kbps)" % ( self.currentSize, ( " of %s" % self.totalSize, "" )[ not self.totalSize ], self.kbps )
            print "Time: %s, End: %s, Total time: %s" % ( self.elapsedTime, self.estimatedTimeLeft, self.estimatedTotalTime )
            print


class Main:
    def __init__( self ):
        try:
            url = sys.argv[ 1 ]
            yesno = True
            if hasattr( xbmcgui, 'Dialog' ):
                try: bname = sys.argv[ 2 ]
                except: bname = ""
                bname = bname or os.path.basename( url )
                yesno = xbmcgui.Dialog().yesno( "Confirm Downloading...", "Are you sure download this file?", bname )
            if yesno:
                settings = self.getSettings()
                progress_id = self.getProgressID( settings.get( "iddl_data", "" ) )
                dl = Download( url, destination=settings.get( "downloadpath" ),
                    dlInBackground=settings.get( "downloadinbackground" ),
                    reportPercent=settings.get( "reportpercent" ),
                    windowProgressID=progress_id#"01" #required
                    )
                xbmc.executebuiltin( "Container.Refresh" )
                fp, h = dl.start()
                try: os.unlink( os.path.join( settings.get( "iddl_data", "" ), progress_id ) )
                except: print_exc()
                print fp, h
                if fp and os.path.exists( fp ):
                    try:
                        if xbmcgui.Dialog().yesno( "Confirm executing...", "Do you want execute file?", os.path.basename( fp ), "Remember XBMC will be closed!" ):
                            from action import start_file
                            start_file( fp.decode( "utf-8" ), kill_xbmc=True )
                    except:
                        print_exc()
                    xbmc.executebuiltin( "Container.Refresh" )
        except:
            print_exc()

    def get_browse_dialog( self, default="", heading="", dlg_type=3, shares="files", mask="", use_thumbs=False, treat_as_folder=False ):
        """ shows a browse dialog and returns a value
            - 0 : ShowAndGetDirectory
            - 1 : ShowAndGetFile
            - 2 : ShowAndGetImage
            - 3 : ShowAndGetWriteableDirectory
        """
        dialog = xbmcgui.Dialog()
        value = dialog.browse( dlg_type, heading, shares, mask, use_thumbs, treat_as_folder, default )
        return value

    def getSettings( self, id="repository.xbmc.builds" ):
        settings = {}
        try:
            from xbmcaddon import Addon
            addon = Addon( id )
            usetempdir = addon.getSetting( "usetempdir" ) == "true" 
            browsedir  = addon.getSetting( "browsedir" ) == "true" 
            settings[ "downloadpath" ] = ( addon.getSetting( "downloadpath" ), "" )[ browsedir ] 
            if not usetempdir:
                #browse for save dir
                if not settings[ "downloadpath" ] or not os.path.exists( settings[ "downloadpath" ] ):
                    dpath = xbmc.translatePath( self.get_browse_dialog( heading="Recordings folder" ) )
                    if dpath and os.path.exists( dpath ):
                        settings[ "downloadpath" ] = dpath
                        addon.setSetting( "downloadpath", settings[ "downloadpath" ] )
                    else:
                        settings[ "downloadpath" ] = ""
            settings[ "downloadinbackground" ] = addon.getSetting( "downloadinbackground" ) == "true"
            settings[ "reportpercent" ] = int( "0|5|10|20|25|50|100".split( "|" )[ int( addon.getSetting( "reportpercent" ) ) ] )

            PROFILE_PATH = xbmc.translatePath( addon.getAddonInfo( "profile" ) )
            settings[ "iddl_data" ] = os.path.join( PROFILE_PATH, "iddl_data" )
            if not os.path.exists( settings[ "iddl_data" ] ): os.makedirs( settings[ "iddl_data" ] )
        except:
            pass
        return settings

    def getProgressID( self, iddl_data ):
        # list des id possible 12 max
        a = set( sorted( [ str( i ).zfill( 2 ) for i in range( 1, 13 ) ] ) )
        #list des fichiers du dossier dl
        b = set( [ str( i ).zfill( 2 ) for i in os.listdir( iddl_data ) if i.isdigit() ] )
        #enleve les id qui sont en executions
        a.difference_update( b )
        id = sorted( a )[ 0 ]
        file( os.path.join( iddl_data, id ), "w" ).close()
        return id


# Test dialog
def DialogDLProgress():
    try:
        script = os.path.join( os.getcwd(), "DialogDLProgress.py" )
        xbmc.executebuiltin( "RunScript(%s)" % ( script ) )
    except:
        print_exc()
# Test program
def test( args=[] ):
    # Download( url[, destination, heading, dlInBackground, reportPercent, windowID, windowProgressID ] )
    dl = Download(
        "http://mirrors.xbmc.org/releases/win32/xbmc-r33778-Dharma_beta2.exe",
        #destination="",#getsettings
        #heading="",
        dlInBackground=True,#getsettings
        #reportPercent=5,#getsettings
        #windowID=13000,
        windowProgressID="01" )#required
    #DialogDLProgress()
    fp, h = dl.start()
    # infos du DL
    print fp
    print h


if ( __name__ == "__main__" ):
    if len( sys.argv ) >= 1:
        Main()
    else:
        DEBUG = 1
        test()

