
#Modules general
import os
import sys
import ConfigParser

#modules XBMC
import xbmc
from xbmcgui import Dialog

#modules custom
#from utilities import SYSTEM_PLATFORM, XBMC_ROOT

#module logger
try:
    logger = sys.modules[ "__main__" ].logger
except:
    import script_log as logger


DIALOG_BROWSE = Dialog().browse


def SetConfiguration():
    """ Definit les repertoires locaux de l'utilisateur """
    from utilities import SYSTEM_PLATFORM, XBMC_ROOT
    
    logger.LOG( logger.LOG_DEBUG, str( "*" * 85 ) )
    logger.LOG( logger.LOG_DEBUG, "Setting Configuration".center( 85 ) )
    logger.LOG( logger.LOG_DEBUG, str( "*" * 85 ) )
    logger.LOG( logger.LOG_DEBUG, "%s case", SYSTEM_PLATFORM )

    ROOTDIR = os.getcwd().replace( ";", "" )
    fichier = os.path.join( ROOTDIR, "resources", "conf.cfg" )
    config = ConfigParser.ConfigParser()
    config.read( fichier )
    USRPath = False

    if not os.path.isdir( XBMC_ROOT ):
        XBMC_ROOT = DIALOG_BROWSE( 0, sys.modules[ "__main__" ].__language__( 100 ), "files" )
        logger.LOG( logger.LOG_DEBUG, "Other case, XBMC = %s", XBMC_ROOT )
    config.set( "InstallPath", "path", XBMC_ROOT )

    if SYSTEM_PLATFORM == "linux":
        #Set Linux normal ScraperDir
        ScraperDir = os.path.join( os.sep+"usr", "share", "xbmc", "system", "scrapers", "video" )
        config.set( "InstallPath", "ScraperDir", ScraperDir )
        #Set Linux PMIIIDir
        PMIIIDir = os.path.join( os.sep+"usr", "share", "xbmc", "skin" )
        config.set( "InstallPath", "PMIIIDir", PMIIIDir )
        USRPath = True
    else:
        #Set Win ScraperDir
        scraperDir = os.path.join( XBMC_ROOT, "system", "scrapers", "video" )
        config.set( "InstallPath", "ScraperDir", scraperDir )

    #Set ScraperType
    config.set( "InstallPath", "USRPath", USRPath )

    #Set ThemesDir
    config.set( "InstallPath", "ThemesDir", os.path.join( XBMC_ROOT, "skin" ) )

    #Set ScriptsDir
    config.set( "InstallPath", "ScriptsDir", os.path.join( XBMC_ROOT, "scripts" ) )

    #Set PluginDir
    PluginDir = os.path.join( XBMC_ROOT, "plugins" )
    config.set( "InstallPath", "PluginDir", PluginDir )
    config.set( "InstallPath", "PluginMusDir", os.path.join( PluginDir, "music" ) )
    config.set( "InstallPath", "PluginPictDir", os.path.join( PluginDir, "pictures" ) )
    config.set( "InstallPath", "PluginProgDir", os.path.join( PluginDir, "programs" ) )
    config.set( "InstallPath", "PluginVidDir", os.path.join( PluginDir, "video" ) )

    #Set CacheDir
    config.set( "InstallPath", "CacheDir", os.path.join( ROOTDIR, "cache" ) )

    #Set UserDataDir
    config.set( "InstallPath", "UserDataDir", os.path.join( XBMC_ROOT, "userdata" ) )

    #Save configuration
    config.set( "InstallPath", "pathok", True )
    config.write( open( fichier, "w" ) )

