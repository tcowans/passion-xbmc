# -*- coding: utf-8 -*-

"""
Downloader Passion XBMC for Windows

frost
"""

import os
import re
import urllib 
from urlparse import urljoin
from traceback import print_exc

import xbmc
import xbmcgui


DIALOG_PROGRESS = xbmcgui.DialogProgress()

URL_BASE = "http://passion-xbmc.org/gros_fichiers/windows/index.php"


def launch_install( XBMCSetup ):
    if xbmcgui.Dialog().yesno( "Confirmer installation", "Désirez-vous installer votre nouvelle version?", "NB: Fermeture automatique de XBMC." ):
        xbmc.executebuiltin( 'System.Exec("%s")' % ( XBMCSetup ) )
        xbmc.shutdown()


def reduced_path( fpath ):
    list_path = fpath.split( os.sep )
    for pos in list_path[ 1:-2 ]:
        list_path[ list_path.index( pos ) ] = ".."
    return os.sep.join( list_path )


def get_html_source( url ):
    """ fetch the html source """
    try:
        sock = urllib.urlopen( url )
        html = sock.read()
        sock.close()
        return html
    except:
        print_exc()
        return ""


regexp =  '.*?(exe)'
regexp += '.*?((?:[a-z][a-z\\.\\d\\-]+)\\.(?:[a-z][a-z\\-]+))(?![\\w\\.])'
regexp += '.*?([+-]?\\d*\\.\\d+)(?![-+0-9\\.])'
regexp += '.*?((?:(?:[0-2]?\\d{1})|(?:[3][0,1]{1}))[-:\\/.](?:[0]?[1-9]|[1][012])[-:\\/.](?:(?:\\d{1}\\d{1})))(?![\\d])'
regexp += '.*?((?:(?:[0-1][0-9])|(?:[2][0-3])|(?:[0-9])):(?:[0-5][0-9])(?::[0-5][0-9])?(?:\\s?(?:am|AM|pm|PM))?)'

RELEASES = re.compile( regexp, re.IGNORECASE | re.DOTALL ).findall( get_html_source( URL_BASE ) )
RELEASES.sort( reverse= True )

LIST_SELECT = []
for ext, release, size, date, time in RELEASES:
    stritem = release + " | " + size + " MB | " + date + ", " + time
    LIST_SELECT.append( stritem )
LIST_SELECT[ 0 ] = "[B]" + LIST_SELECT[ 0 ] + "[/B]"


class pDialogCanceled( Exception ):
    def __init__( self, errmsg="Downloading was canceled by user!" ):
        self.msg = errmsg


def _remove( filepath, remove_tries=3 ):
    urllib.urlcleanup()
    try:
        script = os.path.join( os.getcwd().rstrip( ";" ), "badfile.py" )
        url = "filepath=%s&&remove_tries=%i" % ( filepath, remove_tries )
        xbmc.executebuiltin( 'XBMC.RunScript(%s,%s)' % ( script, url, ) )
    except:
        print_exc()
    return ""


def dl_release( heading, url, destination ):
    DIALOG_PROGRESS.create( heading )
    try:
        def _report_hook( count, blocksize, totalsize ):
            _line3_ = ""
            if totalsize > 0:
                _line3_ += "Size: %.2f / %.2f Mb" % ( ( ( count * blocksize ) / 1024.0 / 1024.0 ), ( totalsize / 1024.0 / 1024.0  ), )
            else:
                _line3_ += "Size: %.2f / ?.?? Mb" % ( ( ( count * blocksize ) / 1024.0 / 1024.0 ), )
            percent = int( float( count * blocksize * 100 ) / totalsize )
            strProgressBar = str( percent ) #xbmc.getInfoLabel( "System.Progressbar" )
            if ( percent <= 0 ) or not strProgressBar: strPercent = "0%"
            else: strPercent = "%s%%" % ( strProgressBar, )
            _line3_ += " | %s" % ( strPercent, )
            DIALOG_PROGRESS.update( percent, url, destination, _line3_ )
            if ( DIALOG_PROGRESS.iscanceled() ): raise pDialogCanceled()
        fp, h = urllib.urlretrieve( url, destination, _report_hook )
        filepath = fp
    except pDialogCanceled, error:
        print error.msg
        filepath = _remove( destination )
    except:
        print_exc()
        filepath = _remove( destination )
    DIALOG_PROGRESS.close()
    return filepath


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


def select_release():
    selected = xbmcgui.Dialog().select( "Releases Passion XBMC pour Windows", LIST_SELECT )
    if selected >=0:
        release = RELEASES[ selected ][ 1 ]
        url_release = urljoin( URL_BASE, release )
        destination = get_browse_dialog( heading="Parcourir pour sauvegarder " + release )
        if destination and os.path.isdir( destination ):
            destination = os.path.join( destination, release )
            if os.path.isfile( destination ):
                if not xbmcgui.Dialog().yesno( release, "Voulez-vous télécharger à nouveau cette release?", reduced_path( destination ) ):
                    return launch_install( destination )
            if xbmcgui.Dialog().yesno( "Confirmer téléchargement du fichier", "Êtes-vous sûr de télécharger ce fichier?", release ):
                filepath = dl_release( release, url_release, destination )
                if filepath and os.path.isfile( filepath ):
                    xbmcgui.Dialog().ok( "Passion XBMC pour Windows", "Téléchagement terminé avec succès.", reduced_path( destination ) )
                    launch_install( filepath )
                else:
                    xbmcgui.Dialog().ok( "Passion XBMC pour Windows", "Le fichier n'a pas été téléchargé avec succès!" )

select_release()
