
# GET AND PRINT ALL STATS OF SCRIPT
TEST_PERFORMANCE = False
UNIT_TEST        = False
# On release version 2, replace dev_test = False
DEV_TEST         = True


# script constants
__script__       = "Installer Passion-XBMC"
__plugin__       = "Unknown"
__author__       = "Team Passion-XBMC"
__url__          = "http://passion-xbmc.org/index.php"
__svn_url__      = "http://passion-xbmc.googlecode.com/svn/trunk/scripts/Installer%20Passion-XBMC/"
__credits__      = "Team XBMC, http://xbmc.org/"
__platform__     = "xbmc media center"

__version__      = "pre-2.0"
__statut__       = "DevHD; Beta 1" #(dev,svn,release,etc)

if DEV_TEST:
    __script__  += " Web" 
    __svn_url__  = "http://passion-xbmc.googlecode.com/svn/branches/scripts/Installer%20Passion-XBMC%20Web/"

# don't edit __date__ and __svn_revision__
# use svn:keywords http://svnbook.red-bean.com/en/1.4/svn.advanced.props.special.keywords.html
__svn_revision__ = "$Revision$".replace( "Revision", "" ).strip( "$: " ) or __statut__
__date__         = "$Date$"[ 7:17 ]
if not __date__:
    try:
        from urllib import urlopen
        __date__ = urlopen( __svn_url__ + "default.py" ).info()[ "Last-Modified" ]
    except: pass
__date__         = __date__ or "Unknown"


#Modules general
import os
import sys
from traceback import print_exc

# Modules XBMC
import xbmc
import xbmcgui

# set our xbmc.settings path for xbmc get '/resources/settings.xml'
XBMC_SETTINGS = xbmc.Settings( os.getcwd() )


# INITIALISATION CHEMIN RACINE
ROOTDIR = os.getcwd().replace( ";", "" )

# Shared resources
BASE_RESOURCE_PATH = os.path.join( ROOTDIR, "resources" )
PLATFORM_LIBRARIES = os.path.join( BASE_RESOURCE_PATH, "platform_libraries" )
LIBS               = os.path.join( BASE_RESOURCE_PATH, "libs" )
GUI_LIBS           = os.path.join( LIBS, "GUI" )
CONTENTS_LIBS      = os.path.join( LIBS, "sources" )

# append the proper platforms folder to our path, xbox is the same as win32
sys.path.append( os.path.join( PLATFORM_LIBRARIES, ( os.environ.get( "OS", "win32" ), "win32", )[ os.environ.get( "OS", "win32" ) == "xbox" ] ) )
# append the proper libs folder to our path
sys.path.append( LIBS )
# append the proper GUI folder to our path
sys.path.append( GUI_LIBS )
# append the proper sources contents ("PassionXbmcWeb","PassionXbmcFtp","XbmcZone",etc...) folder to our path
for content in os.listdir( CONTENTS_LIBS ):
    try: sys.path.append( os.path.join( CONTENTS_LIBS, content ) )
    except: print_exc()


#modules custom
from specialpath import *
# custom_sys_stdout_stderr is new module for xbmc output
# for active print debug in output, set "PRINT_DEBUG = True", but use options in settings window.
# if you want force print. start print with "bypass: |bypass_debug: |bypass_comment: "
# NB: the variables bypass not printed, look example at end module custom_sys_stdout_stderr
import custom_sys_stdout_stderr as output


#FONCTION POUR RECUPERER LES LABELS DE LA LANGUE. ( ex: __language__( 0 ) = id="0" du fichier strings.xml )
__language__ = xbmc.Language( ROOTDIR ).getLocalizedString
LANGUAGE_IS_FRENCH = ( xbmc.getLanguage().lower() == "french" )

DIALOG_PROGRESS = xbmcgui.DialogProgress()


# Info version (deprecated)
__version_l1__ = __language__( 700 )#"version"
__version_r1__ = __version__
__version_l2__ = __language__( 707 )#"date"
__version_r2__ = __date__
__version_l3__ = __language__( 708 )#"SVN"
__version_r3__ = str( __svn_revision__ )

# team credits (deprecated)
__credits_l1__ = __language__( 702 )#"Developpeurs"
__credits_r1__ = "Frost & Seb & Temhil"
__credits_l2__ = __language__( 703 )#"Conception Graphique"
__credits_r2__ = "Frost & Jahnrik & Temhil"
__credits_l3__ = __language__( 709 )#"Langues"
__credits_r3__ = "Frost & Kottis & Temhil"
__credits_l4__ = __language__( 706 )#"Conseils et soutien"
__credits_r4__ = "Alexsolex & Shaitan"


def MAIN():
    try: output.PRINT_DEBUG = ( XBMC_SETTINGS.getSetting( "script_debug" ) == "true" )
    except: print_exc()

    # print depend of output.PRINT_DEBUG is True or False
    print "bypass_debug: %s" % str( "-" * 100 )
    print "bypass_debug: Starting %s %s, %s, SVN r%s. Built on %s" % ( __script__, __version__, __statut__, __svn_revision__, __date__ )
    print "bypass_debug: The executable script running is: %s" % os.path.join( os.getcwd(), "default.py" )
    print "bypass_debug: %s" % str( "-" * 100 )
    try:
        from utilities import getUserSkin
        current_skin, force_fallback = getUserSkin()
        print "bypass_debug: load default skin:[%s]" % current_skin
        print "bypass_debug: default skin use force fallback: %s" % repr( force_fallback )
        del getUserSkin
    except:
        pass

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
            #from utilities import Settings
            #try: output.PRINT_DEBUG = Settings().get_settings().get( "script_debug", False )
            #except: print_exc()
            CHECKMAJ.UPDATE_STARTUP = ( XBMC_SETTINGS.getSetting( "update_startup" ) == "true" )#Settings().get_settings().get( "update_startup", True )
            #del Settings
        except:
            print_exc()
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
                try:
                    import Home
                    DIALOG_PROGRESS.close()
                    HomeAction = Home.show_home()
                except:
                    print_exc()
                    HomeAction = "error"

                if HomeAction == "error":
                    import MainGui
                    MainGui.show_main()
            except:
                print_exc()
                dialog_error = True
        else:
            # LANCEMENT DE LA MISE A JOUR
            try:
                scriptmaj = config.get( 'Version', 'SCRIPTMAJ' )
                xbmc.executescript( scriptmaj )
            except:
                print "bypass_debug: default : Exception pendant le chargement et/ou La mise a jour"
                print_exc()
                dialog_error = True

        if dialog_error: xbmcgui.Dialog().ok( __language__( 111 ), __language__( 112 ) )
    except:
        print_exc()
    DIALOG_PROGRESS.close()



if __name__ == "__main__":
    try:
        DIALOG_PROGRESS.create( __language__( 0 ), "", "" )
        if TEST_PERFORMANCE:
            import misc
            misc.RUN_PERFORMANCE()
        elif UNIT_TEST:
            import misc
            misc.RUN_UNIT_TEST()
        else:
            MAIN()
    except:
        print_exc()
        DIALOG_PROGRESS.close()

    if not TEST_PERFORMANCE:
        # replace standard stdout and stderr, modified by import custom_sys_stdout_stderr
        sys.stdout = sys.stdout.terminal
        sys.stderr = sys.stderr.terminal
