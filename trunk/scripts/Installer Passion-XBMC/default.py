
# script constants
__script__       = "Installer Passion-XBMC"
__plugin__       = "Unknown"
__author__       = "Team Passion-XBMC"
__url__          = "http://passion-xbmc.org/index.php"
__svn_url__      = "http://passion-xbmc.googlecode.com/svn/trunk/scripts/Installer%20Passion-XBMC/"
__credits__      = "Team XBMC, http://xbmc.org/"
__platform__     = "xbmc media center"
__date__         = "14-01-2009"
__version__      = "pre-1.0.0"
__svn_revision__ = 0


#Modules general
import os
import sys
from ConfigParser import ConfigParser

#modules XBMC
import xbmc
import xbmcgui

#modules custom
import resources.libs.script_log as logger


# INITIALISATION CHEMIN RACINE
ROOTDIR = os.getcwd().replace( ";", "" )

#FONCTION POUR RECUPERER LES LABELS DE LA LANGUE. ( ex: __language__( 0 ) = id="0" du fichier strings.xml )
__language__ = xbmc.Language( ROOTDIR, "french" ).getLocalizedString

DIALOG_PROGRESS = xbmcgui.DialogProgress()

# Info version
__version_l1__ = __language__( 700 )#"version"
__version_r1__ = __version__
__version_l2__ = __language__( 707 )#"date"
__version_r2__ = __date__
__version_l3__ = __language__( 708 )#"SVN"
__version_r3__ = str( __svn_revision__ )

# team credits
__credits_l1__ = __language__( 702 )#"Développeurs"
__credits_r1__ = "Frost & Seb & Temhil"
__credits_l2__ = __language__( 703 )#"Conception Graphique"
__credits_r2__ = "Frost & Jahnrik & Temhil"
__credits_l3__ = __language__( 706 )#"Conseils et soutien"
__credits_r3__ = "Alexsolex & Shaitan"


def MAIN():
    logger.LOG( logger.LOG_DEBUG, str( "*" * 85 ) )
    logger.LOG( logger.LOG_DEBUG, "Lanceur".center( 85 ) )
    logger.LOG( logger.LOG_DEBUG, str( "*" * 85 ) )

    try:
        # INITIALISATION CHEMINS DE FICHIER LOCAUX
        fichier = os.path.join( ROOTDIR, "resources", "conf.cfg" )
        config = ConfigParser()
        config.read( fichier )

        DIALOG_PROGRESS.update( -1, __language__( 101 ), __language__( 110 ) )
        if not config.getboolean( 'InstallPath', 'pathok' ):
            # GENERATION DES INFORMATIONS LOCALES
            from resources.libs import CONF
            CONF.SetConfiguration()

        # VERIFICATION DE LA MISE A JOUR
        from resources.libs import CHECKMAJ
        try:
            from resources.libs.utilities import Settings
            CHECKMAJ.UPDATE_STARTUP = Settings().get_settings().get( "update_startup", True )
            del Settings
        except:
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info() )
        if CHECKMAJ.UPDATE_STARTUP:
            DIALOG_PROGRESS.update( -1, __language__( 102 ), __language__( 110 ) )
        CHECKMAJ.go()

        config.read( fichier )

        dialog_error = False
        if not config.getboolean( 'Version', 'UPDATING' ):
            try:
                # LANCEMENT DU SCRIPT
                from resources.libs import INSTALLEUR
                INSTALLEUR.go()
            except:
                logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info() )
                dialog_error = True
        else:
            # LANCEMENT DE LA MISE A JOUR
            try:
                scriptmaj = config.get( 'Version', 'SCRIPTMAJ' )
                xbmc.executescript( scriptmaj )

                #from resources.libs import INSTALLEUR
                #INSTALLEUR.go()
            except:
                logger.LOG( logger.LOG_DEBUG, "default : Exception pendant le chargement et/ou La mise a jour" )
                logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info() )
                dialog_error = True

        if dialog_error: xbmcgui.Dialog().ok( __language__( 111 ), __language__( 112 ) )
    except:
        logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info() )
    DIALOG_PROGRESS.close()


if __name__ == "__main__":
    try:
        DIALOG_PROGRESS.create( __language__( 0 ), "", "" )
        MAIN()
    except:
        logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info() )
        DIALOG_PROGRESS.close()
