
# Modules general
import os
import re
import sys
import time
import urllib
from glob import glob
from shutil import copy
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

PLATFORM_DIR = os.path.join( os.getcwd(), "resources", "platform_updater", os.environ.get( "OS", "xbox" ) )
EXCLUDE_TXT = os.path.join( PLATFORM_DIR, "exclude.txt" )

__script__ = "IPX"

CURRENT_REV = xbmc.getInfoLabel( "System.BuildVersion" ).split( " r" )[ -1 ].strip( " r" )


def get_fresh_userdata():
    try:
        tarball = "http://xbmc.svn.sourceforge.net/viewvc/xbmc/branches/xbox/userdata.tar.gz?view=tar"
        targz = os.path.join( PLATFORM_DIR, "userdata.tar.gz" )
        fp, h = urllib.urlretrieve( tarball, targz )
        from extractor import extract
        OK = extract( fp, PLATFORM_DIR )[ 1 ]
        os.remove( targz )
        del extract
    except:
        print_exc()


def _samefile( src, dst ):
    # Macintosh, Unix.
    if hasattr( os.path, 'samefile' ):
        try:
            return os.path.samefile( src, dst )
        except OSError:
            return False

    # All other platforms: check for same pathname.
    return ( os.path.normcase( os.path.abspath( src ) ) == os.path.normcase( os.path.abspath( dst ) ) )


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


def manage_exclude_txt():
    excludes = []
    try:
        try:
            f = open( EXCLUDE_TXT, "r" )
            for line in f.readlines():
                exclude = line.strip( os.linesep )
                if exclude:
                    excludes.append( exclude )
            f.close()
        except IOError:
            pass
        except:
            print_exc()

        excludes = sorted( list( set( excludes ) ) )
        excludes_list = [ "Add file", "Add folder", "Remove all", "Cancel" ] + [ "Excluded: %s" % exclude for exclude in excludes ]
        
        selected = xbmcgui.Dialog().select( "Add/Remove file or folder on update", excludes_list )
        if selected != -1:
            if selected == 0:
                # Add file
                add_file = get_browse_dialog( "special://xbmc/", "Browse for exclude file on update", 1 )
                if not add_file.lower() == "special://xbmc/xbmc.exe":
                    add_file = os.path.basename( add_file )
                    excludes.append( add_file )
                    str_excludes = "\n".join( excludes ) + "\n"
                    file( EXCLUDE_TXT, "w" ).write( str_excludes )
                manage_exclude_txt()
            elif selected == 1:
                # Add folder
                add_folder = get_browse_dialog( "special://xbmc/", "Browse for exclude folder on update" )
                if not add_folder.lower() == "special://xbmc/":
                    add_folder = os.path.basename( add_folder.strip( "/" ) )
                    excludes.append( add_folder )
                    str_excludes = "\n".join( excludes ) + "\n"
                    file( EXCLUDE_TXT, "w" ).write( str_excludes )
                manage_exclude_txt()
            elif selected == 2:
                # Remove all
                if xbmcgui.Dialog().yesno( "Confirmer le retrait", "Êtes-vous sûr de vouloir de tout les retirés?" ):
                    try: os.remove( EXCLUDE_TXT )
                    except IOError: pass
                    except: print_exc()
                manage_exclude_txt()
            elif selected == 3:
                # cancel
                return
            else:
                # demande pour retirer un item
                if xbmcgui.Dialog().yesno( "Confirmer le retrait", "Êtes-vous sûr de vouloir retirer:", excludes[ selected-4 ] ):
                    del excludes[ selected-4 ]
                    str_excludes = "\n".join( excludes ) + "\n"
                    file( EXCLUDE_TXT, "w" ).write( str_excludes )
                manage_exclude_txt()

    except:
        print_exc()


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
        xbmc.executebuiltin( "Skin.Reset(AnimeWindowXMLDialogClose)" )
        xbmc.executebuiltin( "Skin.SetBool(AnimeWindowXMLDialogClose)" )
        self._close_script = kwargs[ "close_script" ]
        self._get_nightly_builds()

    def onInit( self ):
        try:
            self._set_containers()
            get_fresh_userdata()
        except:
            print_exc()

    def _get_nightly_builds( self, refresh=False ):
        DIALOG_PROGRESS.create( "XBMC Nightly Builds from SVN", "Fetching Unofficial Nightly Builds...", _( 110 ) )
        try:
            nightly_builds = self._load_nightly_data( refresh )
            if nightly_builds is None:
                nightly_builds = get_nightly_builds( CURRENT_REV )
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
            self.getControl( 7 ).setVisible( os.path.exists( os.path.join( PLATFORM_DIR, "paths.txt" ) ) )
        except:
            print_exc()
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
                    new_build = downloader( heading, build_url )#, destination="", onBackground=False )
                    #new_build = "F:\\XBMC_PC_26532.rar"
                    if new_build and os.path.exists( new_build ):
                        exclude_txt = ( "", EXCLUDE_TXT )[ os.path.exists( EXCLUDE_TXT ) ]
                        InfoPaths = open( os.path.join( PLATFORM_DIR, "paths.txt" ), "w" )
                        # pour une raison X, XBMC change le %CD% de dos pour la racine d'xbmc!!!!
                        # donc au besoin selon le OS ajoute le vrai %CD% dans les paths si le programme en a de besoin
                        InfoPaths.write( 'cd_real="%s"\n' % PLATFORM_DIR )
                        InfoPaths.write( 'xbmc_install_path="%s"\n' % xbmc.translatePath( "special://xbmc/" ) )
                        InfoPaths.write( 'xbmc_build="%s"\n' % new_build )
                        InfoPaths.write( 'exclude_txt="%s"\n' % exclude_txt )
                        InfoPaths.write( 'backup_revision=r%s\n' % CURRENT_REV )
                        # add info xbmc run on portable mode true or false
                        InfoPaths.write( 'xbmc_is_portable="%s"\n' % repr( _samefile( xbmc.translatePath( "special://xbmc/" ), xbmc.translatePath( "special://home/" ) ) ).lower() )
                        InfoPaths.close()
                        self.getControl( 7 ).setVisible( os.path.exists( os.path.join( PLATFORM_DIR, "paths.txt" ) ) )
            elif controlID == 7:
                # get and run externe program - win32: updater.bat, xbox: updater.xbe, linux: ..., osx: ...
                platform_updater = ( glob( os.path.join( PLATFORM_DIR, "updater*" ) ) + [ "" ] )[ 0 ]
                # set french updater if exists and current language is french
                platform_updater_fr = os.path.join( os.path.dirname( platform_updater ), "fr_" + os.path.basename( platform_updater ) )
                if ( xbmc.getLanguage().lower() == "french" ) and ( os.path.exists( platform_updater_fr ) ):
                    platform_updater = platform_updater_fr
                if platform_updater:
                    #pour des besoins sous MS-DOS et que XBMC change le %CD% de dos pour la racine d'xbmc, fait une copie dans la racine d'xbmc
                    copy( os.path.join( PLATFORM_DIR, "paths.txt" ), os.path.join( xbmc.translatePath( "special://xbmc/" ), "paths.txt" ) )
                    build_path = re.findall( 'xbmc_build="(.*?)"', file( os.path.join( xbmc.translatePath( "special://xbmc/" ), "paths.txt" ), "r" ).read() )[ 0 ]
                    build_name = os.path.basename( build_path )
                    info_compiled = xbmc.getInfoLabel( "System.BuildVersion" )
                    if not CURRENT_REV.isdigit():
                        info_compiled += ", " + xbmc.getInfoLabel( "System.BuildDate" )
                    if xbmcgui.Dialog().yesno( "XBMC %s Updater" % os.environ.get( "OS", "XBox" ), "Confirmer le lancement de la mise à jour.", "Votre version: " + info_compiled, "MAJ vers: " + build_name ):
                        if os.environ.get( "OS", "XBox" ).lower() == "xbox":
                            sys.path.append( PLATFORM_DIR )
                            import updater
                            self._close_dialog()
                            self._close_script()
                            updater.Main()
                        else:
                            command = '"%s"' % platform_updater
                            os.system( command )
                else:
                    xbmcgui.Dialog().ok( "XBMC %s Updater" % os.environ.get( "OS", "XBox" ), "Il y a pas d'Updater pour vôtre Platform!", "Soyez patient cela serait tardé!" )
            elif controlID == 6:
                self._get_nightly_builds( True )
                self._set_containers()
            elif controlID == 8:
                manage_exclude_txt()
        except:
            print_exc()

    def onAction( self, action ):
        if action in ( 9, 10, ):
            self._close_dialog()

    def _close_dialog( self ):
            xbmc.executebuiltin( "Skin.Reset(AnimeWindowXMLDialogClose)" )
            time.sleep( .4 )
            self.close()



def show_nightly( close_script ):
    file_xml = "IPX-Nightly.xml"#"IPX-Updater.xml"
    dir_path = os.getcwd().replace( ";", "" )
    current_skin, force_fallback = getUserSkin()

    w = Nightly( file_xml, dir_path, current_skin, force_fallback, close_script=close_script )
    w.doModal()
    del w
