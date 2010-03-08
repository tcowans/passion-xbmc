
# warning: use update_svn_keywords if you want auto update svn:keywords
# just add or remove space value ( "" or " " )
update_svn_keywords = ""

# GET AND PRINT ALL STATS OF SCRIPT
TEST_PERFORMANCE = False
UNIT_TEST        = False


# script constants
__script__       = "Installer Passion-XBMC"
__plugin__       = "Unknown"
__author__       = "Team Passion-XBMC"
__url__          = "http://passion-xbmc.org/index.php"
__svn_url__      = "http://passion-xbmc.googlecode.com/svn/trunk/scripts/Installer%20Passion-XBMC/"
__credits__      = "Team XBMC, http://xbmc.org/"
__platform__     = "xbmc media center, [ALL]"

__version__      = "pre-2.0"
__statut__       = "RC2" #(dev,svn,release,etc)


# don't edit __date__ and __svn_revision__
# use svn:keywords http://svnbook.red-bean.com/nightly/fr/svn.advanced.props.special.keywords.html
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
default_sys_std = sys.stdout, sys.stderr
import custom_sys_stdout_stderr as output


#FONCTION POUR RECUPERER LES LABELS DE LA LANGUE. ( ex: __language__( 0 ) = id="0" du fichier strings.xml )
__language__ = xbmc.Language( ROOTDIR ).getLocalizedString
LANGUAGE_IS_FRENCH = ( xbmc.getLanguage().lower() == "french" )

DIALOG_PROGRESS = xbmcgui.DialogProgress()


def MAIN():
    try: output.PRINT_DEBUG = ( XBMC_SETTINGS.getSetting( "script_debug" ) == "true" )
    except: print_exc()

    # print depend of output.PRINT_DEBUG is True or False
    print "bypass_debug: %s" % str( "-" * 100 )
    print "bypass_debug: Starting %s %s, %s, SVN r%s. Built on %s" % ( __script__, __version__, __statut__, __svn_revision__, __date__ )
    print "bypass_debug: The executable script running is: %s" % os.path.join( os.getcwd(), "default.py" )
    print "bypass_debug: %s" % str( "-" * 100 )
    dialog_error = False
    updating = False
    try:
        from utilities import getUserSkin
        current_skin, force_fallback = getUserSkin()
        print "bypass_debug: load default skin:[%s]" % current_skin
        print "bypass_debug: default skin use force fallback: %s" % repr( force_fallback )
        del getUserSkin
    except:
        pass

    #setup skins utilities and reload xbmc skin if necessary
    import skins_utilities
    if skins_utilities.setupUtilities():
        print "Reloaded Skin: %s" % xbmc.getSkinDir()
        xbmc.executebuiltin( "XBMC.Notification(%s,Reloaded Skin...,3000,%s)" % ( xbmc.getSkinDir(), os.path.join( os.getcwd(), "default.tbn" ), ) )
        xbmc.executebuiltin( "XBMC.ReloadSkin()" )
        xbmc.sleep( 2000 )

    # INITIALISATION CHEMINS DE FICHIER LOCAUX
    try:
        import CONF
        config = CONF.ReadConfig()

        DIALOG_PROGRESS.update( -1, __language__( 101 ), __language__( 110 ) )
        if not config.getboolean( 'InstallPath', 'pathok' ):
            # GENERATION DES INFORMATIONS LOCALES
            CONF.SetConfiguration()
    except:
        dialog_error = True
        print "Error while setting the configuration"
        print_exc()

    # CHECK SCRIPT UPDATE AVAILABILITY AND UPDATE CONFIGUARTION FILE
    try:
        import CHECKMAJ
        try:
            CHECKMAJ.UPDATE_STARTUP = ( XBMC_SETTINGS.getSetting( "update_startup" ) == "true" )
        except:
            CHECKMAJ.UPDATE_STARTUP = False
            print_exc()
        print "CHECKMAJ.UPDATE_STARTUP = %s"%str(CHECKMAJ.UPDATE_STARTUP)
        if CHECKMAJ.UPDATE_STARTUP:
            DIALOG_PROGRESS.update( -1, __language__( 102 ), __language__( 110 ) )
            CHECKMAJ.go()
        del CHECKMAJ
    except:
        # In case of an Exception here we still load the script
        print "Error while checking availability of an update for the installer"
        print "We still going to start the script ..."
        print_exc()

    # RETRIEVING CONFIGURATION FROM CONF FILE
    try:
        config = CONF.ReadConfig()
        del CONF
    except:
        print "Error while reading the configuration"
        dialog_error = True
        print_exc()

    try:
        updating = config.getboolean( 'Version', 'UPDATING' )
    except:
        # Issue with conf file, stopping update
        dialog_error = True
        print_exc()
    try:
        if not updating:
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
                print "bypass_debug: MAIN: Exception while loading the script"
                print_exc()
                dialog_error = True
        else:
            # UPDATING THE SCRIPT
            try:
                scriptmaj = config.get( 'Version', 'SCRIPTMAJ' )
                xbmc.executescript( scriptmaj )
            except:
                print "bypass_debug: MAIN: Exception while updating of the script"
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
        sys.stdout, sys.stderr = default_sys_std
