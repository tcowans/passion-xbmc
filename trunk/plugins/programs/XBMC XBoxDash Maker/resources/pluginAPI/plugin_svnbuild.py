"""
this module is not a updater, but a downloaded only.
if you want update... update your xbmc manually
"""

#Modules general
import os
import re
import urllib
from urllib import quote_plus
from traceback import print_exc

#modules XBMC
import xbmc
import xbmcgui


DIALOG_PROGRESS = xbmcgui.DialogProgress()


URL_BASE = "http://www.sshcs.com/xbmc/"
URL_REVISION_INFO = "%sinc/EVA.asp?mode=Build" % URL_BASE
URL_BUILD = "%sbinaries/Builds/" % URL_BASE
NAME_BUILD = "XBMC_XBOX_%s.rar"


class pDialogCanceled( Exception ):
    def __init__( self, errmsg="Downloading was canceled by user!" ):
        self.msg = errmsg


def get_html_source( url ):
    """ fetch the html source """
    try:
        if os.path.isfile( url ):
            sock = open( url, "r" )
        else:
            urllib.urlcleanup()
            sock = urllib.urlopen( url )
        htmlsource = sock.read()
        sock.close()
        return htmlsource
    except:
        print_exc()
    return ""


def get_svn_infos():
    try:
        svn = get_html_source( URL_REVISION_INFO )
        infos = re.search( "^(\\d+) (\\d+)$", svn )
        return infos.group( 1 ), infos.group( 2 )
    except:
        print_exc()
    return "", ""


def dl_build( heading, url, destination ):
    DIALOG_PROGRESS.create( heading )
    filepath = ""
    try:
        def _report_hook( count, blocksize, totalsize ):
            _line3_ = ""
            if totalsize > 0:
                _line3_ += xbmc.getLocalizedString( 30840 ) % ( ( ( count * blocksize ) / 1024.0 / 1024.0 ), ( totalsize / 1024.0 / 1024.0  ), )
            else:
                _line3_ += xbmc.getLocalizedString( 30841 ) % ( ( ( count * blocksize ) / 1024.0 / 1024.0 ), )
            percent = int( float( count * blocksize * 100 ) / totalsize )
            strProgressBar = str( percent )
            if ( percent <= 0 ) or not strProgressBar: strPercent = "0%"
            else: strPercent = "%s%%" % ( strProgressBar, )
            _line3_ += " | %s" % ( strPercent, )
            #DIALOG_PROGRESS.update( percent, url, destination, _line3_ )
            DIALOG_PROGRESS.update( percent, _line3_, destination, xbmc.getLocalizedString( 30890 ) )
            if ( DIALOG_PROGRESS.iscanceled() ):
                raise pDialogCanceled()
        fp, h = urllib.urlretrieve( url, destination, _report_hook )
        if h:
            #print h
            try:
                if "text" in h[ "Content-Type" ]:
                    os.unlink( destination )
            except:
                print_exc()
        filepath = fp
    except pDialogCanceled, error:
        print error.msg
        filepath = ""
    except:
        print_exc()
        filepath = ""
    DIALOG_PROGRESS.close()
    return filepath


def Main():
    rev, date = get_svn_infos()
    if rev and date:
        ok = 0
        try:
            # get xbmc revision
            xbmc_version = xbmc.getInfoLabel( "System.BuildVersion" )
            xbmc_rev = xbmc_version.split( " " )[ 1 ].replace( "r", "" )
            # newest?
            ok = int( rev ) > int( xbmc_rev )
        except:
            print_exc()

        heading = xbmc.getLocalizedString( 30810 ) % rev 
        if ok and xbmcgui.Dialog().yesno( xbmc.getLocalizedString( 30820 ) % rev , xbmc.getLocalizedString( 30821 ) % xbmc_rev, xbmc.getLocalizedString( 30822 ) % rev  ):
            browser = xbmcgui.Dialog().browse( 0, xbmc.getLocalizedString( 30830 ), "files" )
            if browser and os.path.isdir( xbmc.translatePath( browser ) ):
                url = URL_BUILD + NAME_BUILD % rev
                dest = xbmc.translatePath( os.path.join( browser, NAME_BUILD % rev ) )
                ok = dl_build( heading, url, dest )

                if ( not ok ):
                    xbmcgui.Dialog().ok( heading, xbmc.getLocalizedString( 30870 ) )
                else:
                    #xbmcgui.Dialog().ok( heading, xbmc.getLocalizedString( 30850 ), xbmc.getLocalizedString( 30851 ), dest )
                    if xbmcgui.Dialog().yesno( heading, xbmc.getLocalizedString( 30850 ), xbmc.getLocalizedString( 30880 ) ):
                        # AskUser for update with external programs
                        url = "build_rar='%s'&svn_rev='%s'" % ( quote_plus( dest ), rev )
                        xbmc.executebuiltin( "XBMC.RunPlugin(plugin://Programs/XBMC XBoxDash Maker/?%s)" % url )
                    

        elif ( not ok ):
            xbmcgui.Dialog().ok( xbmc.getLocalizedString( 30860 ), xbmc.getLocalizedString( 30861 ) )



if ( __name__ == "__main__" ):
    Main()
