
# Modules general
import os
import sys
import time
import urllib
from traceback import print_exc

# Modules XBMC
import xbmc
import xbmcgui

# Modules custom
from utilities import getUserSkin
from xbmc_svn_nightly_builds import get_nightly_builds


#FONCTION POUR RECUPERER LES LABELS DE LA LANGUE.
_ = sys.modules[ "__main__" ].__language__

DIALOG_PROGRESS = xbmcgui.DialogProgress()

SPECIAL_SCRIPT_DATA = sys.modules[ "__main__" ].SPECIAL_SCRIPT_DATA

NIGHTLY_BUILDS_DATA = os.path.join( SPECIAL_SCRIPT_DATA, "nightly_builds.svn" )


__script__ = "IPX"#sys.modules[ "__main__" ].__script__


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


class pDialogCanceled( Exception ):
    def __init__( self, errmsg="Downloading was canceled by user!" ):
        self.msg = errmsg


def downloader( heading, url, destination="", onBackground=False ):
    # onBackground : pas implanter doit deplacer le downloader et utiliser runscript avec des parametres et tester sans thread
    if not onBackground: DIALOG_PROGRESS.create( heading, "Veuillez patienter..." )
    xbmc.log( "[SCRIPT: %s] Downloading started: %s" % ( __script__, heading ), xbmc.LOGNOTICE )
    filepath = ""
    try:
        if not destination:
            dpath = xbmc.translatePath( get_browse_dialog( heading=_( 20005 ) ) )
            if not dpath and not os.path.exists( dpath ):
                try: raise pDialogCanceled()
                except pDialogCanceled, error:
                    xbmc.log( "[SCRIPT: %s] DIALOG::PROGRESS:BROWSE: %s" % ( __script__, error.msg ), xbmc.LOGWARNING )
                #if not onBackground:
                DIALOG_PROGRESS.close()
                return url

            bname = os.path.basename( url ).replace( "  ", "" )
            destination = os.path.join( dpath, bname )

        tinit = time.time()
        def _report_hook( count, blocksize, totalsize ):
            _line3_ = ""
            if totalsize > 0:
                _line3_ += "Taille: %.2f / %.2f Mo" % ( ( ( count * blocksize ) / 1024.0 / 1024.0 ), ( totalsize / 1024.0 / 1024.0  ), )
            else:
                _line3_ += "Taille: %.2f / ? Mo" % ( ( ( count * blocksize ) / 1024.0 / 1024.0 ), )
            percent = int( float( count * blocksize * 100 ) / totalsize )
            strProgressBar = str( percent )
            if ( percent <= 0 ) or not strProgressBar: strPercent = "0%"
            else: strPercent = "%s%%" % ( strProgressBar, )
            try:
                duree = time.time() - tinit
                vitesse =  count * blocksize / duree
                _line3_ += " | (%.01f ko/s)" %  float( vitesse / 1024 )
            except: pass
            _line3_ += " | %s" % ( strPercent, )
            if not onBackground: DIALOG_PROGRESS.update( percent, _line3_, destination, "Veuillez patienter..." )
            else:
                if percent in [ 0, 25, 50, 75, 100 ]:
                    notif = "XBMC Nightly Builds,Download Report [B]%i%%[/B],4000,"  % ( percent )
                    xbmc.executebuiltin( "XBMC.Notification(%s)" % notif )
            if ( not onBackground ) and ( DIALOG_PROGRESS.iscanceled() ):
                raise pDialogCanceled()
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
    #if not onBackground:
    DIALOG_PROGRESS.close()
    return filepath


class Nightly( xbmcgui.WindowXMLDialog ):
    def __init__( self, *args, **kwargs ):
        xbmcgui.WindowXMLDialog.__init__( self, *args, **kwargs )
        self._get_nightly_builds()

    def onInit( self ):
        try:
            self._set_containers()
        except:
            print_exc()

    def _get_nightly_builds( self, refresh=False ):
        DIALOG_PROGRESS.create( "XBMC Nightly Builds from SVN", "Fetching Unofficial Nightly Builds...", _( 110 ) )
        try:
            nightly_builds = self._load_nightly_data( refresh )
            if nightly_builds is None:
                nightly_builds = get_nightly_builds()
                try: file( NIGHTLY_BUILDS_DATA, "w" ).write( repr( nightly_builds ) )
                except: print_exc()
            # types : str, str, str, str, list returned by get_nightly_builds
            self.heading, self.info, self.changelog, self.available_builds, self.builds = nightly_builds
        except:
            self.heading, self.info, self.changelog, self.available_builds, self.builds = "", "", "", "", []
            print_exc()
        DIALOG_PROGRESS.close()

    def _load_nightly_data( self, refresh=False ):
        if refresh:
            try: os.unlink( NIGHTLY_BUILDS_DATA )
            except: pass
        try:
            if os.path.exists( NIGHTLY_BUILDS_DATA ):
                return eval( file( NIGHTLY_BUILDS_DATA, "r" ).read() )
        except:
            print_exc()

    def _set_containers( self ):
        try:
            self.getControl( 48 ).reset()
            listitem = xbmcgui.ListItem( self.heading )
            listitem.setProperty( "info", self.info )
            listitem.setProperty( "changelog", self.changelog )
            listitem.setProperty( "available_builds", self.available_builds )
            self.getControl( 48 ).addItem( listitem )
        except:
            print_exc()
        try:
            self.getControl( 49 ).reset()
            #build: [ title, desc, icon, dl_times, build_url ]
            for build in self.builds:
                title, desc, icone, dl_times, build_url = build
                #print "bypass: %s" % icone
                listitem = xbmcgui.ListItem( title, desc, icone, icone )
                listitem.setProperty( "icon", icone )
                listitem.setProperty( "dl_times", dl_times )
                listitem.setProperty( "build_url", build_url )
                self.getControl( 49 ).addItem( listitem )
        except:
            print_exc()

    def onFocus( self, controlID ):
        pass

    def onClick( self, controlID ):
        try:
            if controlID in [ 5, 49 ]:
                item = self.getControl( 49 ).getSelectedItem()
                build_url = item.getProperty( "build_url" )
                heading = item.getLabel()
                if xbmcgui.Dialog().yesno( "XBMC Nightly Builds", "Confirmer le téléchargement!", "%s: %s" % ( heading, os.path.basename( build_url ) ), "Êtes-vous sûr de vouloir télécharger cette build?"  ):
                    # onBackground : pas implanter doit deplacer le downloader et utiliser runscript avec des parametres et tester sans thread
                    print downloader( heading, build_url )#, destination="", onBackground=False )
            elif controlID == 6:
                self._get_nightly_builds( True )
                self._set_containers()
        except:
            print_exc()

    def onAction( self, action ):
        if action in ( 9, 10, ):
            self.close()
            xbmc.sleep( 1000 )



def show_nightly():
    file_xml = "IPX-Nightly.xml"
    dir_path = os.getcwd().replace( ";", "" )
    current_skin, force_fallback = getUserSkin()

    w = Nightly( file_xml, dir_path, current_skin, force_fallback )
    w.doModal()
    del w
