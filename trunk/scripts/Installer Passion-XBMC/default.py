
# GET AND PRINT ALL STATS OF SCRIPT
TEST_PERFORMANCE = False

# script constants
__script__       = "Installer Passion-XBMC"
__plugin__       = "Unknown"
__author__       = "Team Passion-XBMC"
__url__          = "http://passion-xbmc.org/index.php"
__svn_url__      = "http://passion-xbmc.googlecode.com/svn/trunk/scripts/Installer%20Passion-XBMC/"
__credits__      = "Team XBMC, http://xbmc.org/"
__platform__     = "xbmc media center"
__date__         = "10-02-2009"
__version__      = "pre-1.0.0"
__svn_revision__ = 0


#Modules general
import os
import sys

#modules XBMC
import xbmc
import xbmcgui

# INITIALISATION CHEMIN RACINE
ROOTDIR = os.getcwd().replace( ";", "" )

# Shared resources
BASE_RESOURCE_PATH = os.path.join( ROOTDIR, "resources" )
# append the proper libs folder to our path
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "libs" ) )
# append the proper GUI folder to our path
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "libs", "GUI" ) )
# append the proper platforms folder to our path, xbox is the same as win32
env = ( os.environ.get( "OS", "win32" ), "win32", )[ os.environ.get( "OS", "win32" ) == "xbox" ]
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "platform_libraries", env ) )

#modules custom
from specialpath import *
import script_log as logger


#frost: changer la langue par default pour l'anglais, car de cette maniere on ai pas obliger de rejouter le strings manquant dans les autres language
#FONCTION POUR RECUPERER LES LABELS DE LA LANGUE. ( ex: __language__( 0 ) = id="0" du fichier strings.xml )
#__language__ = xbmc.Language( ROOTDIR, "french" ).getLocalizedString
__language__ = xbmc.Language( ROOTDIR ).getLocalizedString

DIALOG_PROGRESS = xbmcgui.DialogProgress()

# Info version
__version_l1__ = __language__( 700 )#"version"
__version_r1__ = __version__
__version_l2__ = __language__( 707 )#"date"
__version_r2__ = __date__
__version_l3__ = __language__( 708 )#"SVN"
__version_r3__ = str( __svn_revision__ )

# team credits
__credits_l1__ = __language__( 702 )#"Developpeurs"
__credits_r1__ = "Frost & Seb & Temhil"
__credits_l2__ = __language__( 703 )#"Conception Graphique"
__credits_r2__ = "Frost & Jahnrik & Temhil"
__credits_l3__ = __language__( 709 )#"Langues"
__credits_r3__ = "Frost & Kottis & Temhil"
__credits_l4__ = __language__( 706 )#"Conseils et soutien"
__credits_r4__ = "Alexsolex & Shaitan"


def MAIN():
    logger.LOG( logger.LOG_DEBUG, str( "*" * 85 ) )
    logger.LOG( logger.LOG_DEBUG, "Lanceur".center( 85 ) )
    logger.LOG( logger.LOG_DEBUG, str( "*" * 85 ) )

    try:
        # INITIALISATION CHEMINS DE FICHIER LOCAUX
        import CONF
        config = CONF.ReadConfig()

        DIALOG_PROGRESS.update( -1, __language__( 101 ), __language__( 110 ) )
        if not config.getboolean( 'InstallPath', 'pathok' ):
            # GENERATION DES INFORMATIONS LOCALES
            CONF.SetConfiguration()

        # VERIFICATION DE LA MISE A JOUR
        import CHECKMAJ
        try:
            from utilities import Settings
            CHECKMAJ.UPDATE_STARTUP = Settings().get_settings().get( "update_startup", True )
            del Settings
        except:
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info() )
        if CHECKMAJ.UPDATE_STARTUP:
            DIALOG_PROGRESS.update( -1, __language__( 102 ), __language__( 110 ) )
        CHECKMAJ.go()
        del CHECKMAJ

        config = CONF.ReadConfig()
        del CONF

        dialog_error = False
        if not config.getboolean( 'Version', 'UPDATING' ):
            try:
                # LANCEMENT DU SCRIPT
                import MainGui
                MainGui.show_main()
            except:
                logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info() )
                dialog_error = True
        else:
            # LANCEMENT DE LA MISE A JOUR
            try:
                scriptmaj = config.get( 'Version', 'SCRIPTMAJ' )
                xbmc.executescript( scriptmaj )

                #import MainGui
                #MainGui.show_main()
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
        if TEST_PERFORMANCE:
            import profile, pstats
            report_file = os.path.join( ROOTDIR, "MainPerform.profile.log" )
            profile.run( "MAIN()", report_file )
            pstats.Stats( report_file ).sort_stats( "time", "name" ).print_stats()
        else:
            MAIN()
    except:
        #import traceback; traceback.print_exc()
        logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info() )
        DIALOG_PROGRESS.close()
