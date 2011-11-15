
__script__ = "Astral Media"

# Modules General
import os
import sys
import time
import urllib
from traceback import print_exc

# Modules XBMC
import xbmc
import xbmcgui


DIALOG_PROGRESS = xbmcgui.DialogProgress()


class pDialogCanceled( Exception ):
    def __init__( self, errmsg="Downloading was canceled by user!" ):
        self.msg = errmsg


def get_browse_dialog( default="", heading="", dlg_type=3, shares="files", mask="", use_thumbs=False, treat_as_folder=False ):
    """ shows a browse dialog and returns a value
        - 0 : ShowAndGetDirectory
        - 1 : ShowAndGetFile
        - 2 : ShowAndGetImage
        - 3 : ShowAndGetWriteableDirectory
    """
    dialog = xbmcgui.Dialog()
    value = dialog.browse( dlg_type, heading, shares, mask, use_thumbs, treat_as_folder, default )
    return value


def downloader( heading, url, destination="", onBackground=0, progress_id=None ):
    LISTREPORT = []
    if onBackground:
        LISTREPORT = range( 0, 100+onBackground, onBackground )
        onBackground = True
    if not LISTREPORT:
        LISTREPORT = [ 100 ]# report only on end
    if not onBackground: DIALOG_PROGRESS.create( heading, "Please wait..." )
    filepath = ""
    try:
        if not destination:
            dpath = xbmc.translatePath( get_browse_dialog( heading="Recordings folder" ) )
            if not dpath and not os.path.exists( dpath ):
                try: raise pDialogCanceled( "Browse path was canceled by user!" )
                except pDialogCanceled, error:
                    xbmc.log( "[SCRIPT: %s] DIALOG::PROGRESS:BROWSE: %s" % ( __script__, error.msg ), xbmc.LOGWARNING )
                if xbmc.getCondVisibility( "Window.IsActive(progressdialog)" ):
                    DIALOG_PROGRESS.close()
                return url

            bname = urllib.unquote( os.path.basename( url ) ).replace( "  ", "" )
            destination = os.path.join( dpath, bname )

        xbmc.log( "[SCRIPT: %s] Downloading started: %s" % ( __script__, heading ), xbmc.LOGNOTICE )
        tinit = time.time()
        def _report_hook( count, blocksize, totalsize ):
            _line3_ = ""
            if totalsize > 0:
                _line3_ += "Size: %.2f / %.2f Mb" % ( ( ( count * blocksize ) / 1024.0 / 1024.0 ), ( totalsize / 1024.0 / 1024.0  ), )
            else:
                _line3_ += "Size: %.2f / ? Mb" % ( ( ( count * blocksize ) / 1024.0 / 1024.0 ), )
            percent = int( float( count * blocksize * 100 ) / totalsize )
            strProgressBar = str( percent )
            if ( percent <= 0 ) or not strProgressBar: strPercent = "0%"
            else: strPercent = "%s%%" % ( strProgressBar, )
            try:
                duree = time.time() - tinit
                vitesse =  count * blocksize / duree
                _line3_ += " | (%.01f %s)" % ( float( vitesse / 1024 ), "kb/s" )
            except: pass
            _line3_ += " | %s" % ( strPercent, )
            if not onBackground: DIALOG_PROGRESS.update( percent, _line3_, destination, "Please wait..." )
            else:
                if percent in LISTREPORT and not xbmc.getCondVisibility( "Window.IsVisible(infodialog)" ):
                    notif = "%s,Download Report [B]%i%%[/B],4000,DefaultNetwork.png"  % ( heading, percent )
                    xbmc.executebuiltin( "XBMC.Notification(%s)" % notif )
                    #print notif
            if ( not onBackground ) and ( DIALOG_PROGRESS.iscanceled() ):
                raise pDialogCanceled()

            if progress_id is not None:
                try:
                    win = xbmcgui.Window( xbmcgui.getCurrentWindowDialogId() )
                    if win.getProperty( 'progress.%s.isAlive' % progress_id ) == "kill":
                        if xbmcgui.Dialog().yesno( "Confirm canceling....", "Are you sure, cancel this download?", heading ):
                            raise pDialogCanceled()
                    win.setProperty( 'progress.%s.isAlive' % progress_id, "true" )
                    win.setProperty( 'progress.%s.heading' % progress_id, heading )
                    win.setProperty( 'progress.%s.label'   % progress_id, _line3_ )
                    win.setProperty( 'progress.%s.percent' % progress_id, "%i" % percent )
                    win.getControl( 400+int( progress_id ) ).setPercent( int( percent ) )
                except pDialogCanceled, error:
                    raise
                except:
                    pass

        xbmc.log( "[SCRIPT: %s] Downloading: %s to %s" % ( __script__, url, destination ), xbmc.LOGDEBUG )

        fp, h = urllib.urlretrieve( url, destination, _report_hook )
        if h:
            xbmc.log( "[SCRIPT: %s] download infos: %s" % ( __script__, h ), xbmc.LOGDEBUG )
            try:
                if "text" in h[ "Content-Type" ]:
                    os.unlink( destination )
                    xbmc.log( "[SCRIPT: %s] Content-Type=%s: %s" % ( __script__, h[ "Content-Type" ], destination ), xbmc.LOGERROR )
                    return ""
            except:
                print_exc()
        filepath = fp
    except pDialogCanceled, error:
        xbmc.log( "[SCRIPT: %s] DIALOG::PROGRESS: %s" % ( __script__, error.msg ), xbmc.LOGWARNING )
        filepath = ""
    except:
        print_exc()
        filepath = ""
    if xbmc.getCondVisibility( "Window.IsActive(progressdialog)" ):
        DIALOG_PROGRESS.close()
    try:
        if not filepath and os.path.exists( destination ):
            if xbmcgui.Dialog().yesno( "Confirm Deleting....", "You want to delete what was downloaded?", destination ):
                try: os.unlink( destination )
                except: os.remove( destination )
    except:
        print_exc()
    return filepath


DL_INFO_PATH = os.path.join( os.getcwd(), "iddl" )
if not os.path.exists( DL_INFO_PATH ): os.makedirs( DL_INFO_PATH )


def getProgressID():
    # list des id possible 12 max
    a = set( sorted( [ str( i ).zfill( 2 ) for i in range( 1, 13 ) ] ) )
    #list des fichiers du dossier dl
    b = set( [ str( i ).zfill( 2 ) for i in os.listdir( DL_INFO_PATH ) if i.isdigit() ] )
    #enleve les id qui sont en executions
    a.difference_update( b )
    id = sorted( a )[ 0 ]
    file( os.path.join( DL_INFO_PATH, id ), "w" ).close()
    return id


if ( __name__ == "__main__" ):
    #print sys.argv
    heading = urllib.unquote( os.path.basename( sys.argv[ 1 ] ) )
    url = sys.argv[ 1 ]
    destination = urllib.unquote( sys.argv[ 2 ] )
    onBackground = eval( sys.argv[ 3 ] )
    if xbmc.getCondVisibility( "Window.IsActive(progressdialog)" ):
        DIALOG_PROGRESS.close()
    xbmc.sleep( 500 )
    progress_id = getProgressID()
    downloader( heading, url, destination, onBackground, progress_id )
    try: os.unlink( os.path.join( DL_INFO_PATH, progress_id ) )
    except: print_exc()
    try:
        win = xbmcgui.Window( xbmcgui.getCurrentWindowDialogId() )
        win.clearProperty( 'progress.%s.isAlive' % progress_id )
        win.clearProperty( 'progress.%s.heading' % progress_id )
        win.clearProperty( 'progress.%s.label'   % progress_id )
        win.clearProperty( 'progress.%s.percent' % progress_id )
    except: print_exc()
