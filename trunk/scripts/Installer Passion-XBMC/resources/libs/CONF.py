
#Modules general
import os
import sys
from ConfigParser import ConfigParser

#modules XBMC
import xbmc
from xbmcgui import Dialog

#module logger
try:
    logger = sys.modules[ "__main__" ].logger
except:
    import script_log as logger

try: __script__ = sys.modules[ "__main__" ].__script__
except: __script__ = os.path.basename( os.getcwd().replace( ";", "" ) )

default_conf = os.path.join( os.getcwd().replace( ";", "" ), "resources", "conf.cfg" )
userdata_conf = xbmc.translatePath( "special://profile/" )
if not os.path.exists( userdata_conf ): userdata_conf = xbmc.translatePath( "P:\\" )
fichier = os.path.join( userdata_conf, "script_data" , __script__, "conf.cfg" )


def ReadConfig():
    config = ConfigParser()
    if not os.path.exists( fichier ):
        config.read( default_conf )
        config.write( open( fichier, "w" ) )

    config.read( fichier )
    return config


def SetConfiguration():
    """ Definit les repertoires locaux de l'utilisateur """
    from utilities import SYSTEM_PLATFORM, XBMC_ROOT
    
    logger.LOG( logger.LOG_DEBUG, str( "*" * 85 ) )
    logger.LOG( logger.LOG_DEBUG, "Setting Configuration".center( 85 ) )
    logger.LOG( logger.LOG_DEBUG, str( "*" * 85 ) )
    logger.LOG( logger.LOG_DEBUG, "%s case", SYSTEM_PLATFORM )

    ROOTDIR = os.getcwd().replace( ";", "" )

    config = ReadConfig()
    USRPath = False

    if not os.path.isdir( XBMC_ROOT ):
        XBMC_ROOT = Dialog().browse( 0, sys.modules[ "__main__" ].__language__( 100 ), "files" )
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


class configCtrl:
    """
    Controler of configuration
    """
    def __init__( self ):
        """
        Load configuration file, check it, and correct it if necessary
        """
        self.is_conf_valid = False
        try:
            #TODO: deplacer ici l'utilisation du config parser
            # Create config parser
            self.config = ReadConfig()

            self.CACHEDIR      = self.config.get( 'InstallPath', 'CacheDir' )
            self.themesDir     = self.config.get( 'InstallPath', 'ThemesDir' )
            self.scriptDir     = self.config.get( 'InstallPath', 'ScriptsDir' )
            self.scraperDir    = self.config.get( 'InstallPath', 'ScraperDir' )
            self.pluginDir     = self.config.get( 'InstallPath', 'PluginDir' )
            self.pluginMusDir  = self.config.get( 'InstallPath', 'PluginMusDir' )
            self.pluginPictDir = self.config.get( 'InstallPath', 'PluginPictDir' )
            self.pluginProgDir = self.config.get( 'InstallPath', 'PluginProgDir' )
            self.pluginVidDir  = self.config.get( 'InstallPath', 'PluginVidDir' )
            self.userdatadir   = self.config.get( 'InstallPath', 'UserDataDir' )

            self.USRPath       = self.config.getboolean( 'InstallPath', 'USRPath' )
            if self.USRPath:
                self.PMIIIDir    = self.config.get( 'InstallPath', 'PMIIIDir' )
            else: self.PMIIIDir  = ""

            self.host            = self.config.get( 'ServeurID', 'host' )
            self.user            = self.config.get( 'ServeurID', 'user' )
            self.rssfeed         = self.config.get( 'ServeurID', 'rssfeed' )
            self.password        = self.config.get( 'ServeurID', 'password' )
            self.itemDescripDir  = self.config.get( 'ServeurID', 'contentdescriptorDir' )
            self.itemDescripFile = self.config.get( 'ServeurID', 'contentdescriptor' )

            self.remotedirList   = [ "/.passionxbmc/Themes/", "/.passionxbmc/Scraper/", "/.passionxbmc/Scripts/", "/.passionxbmc/Plugins/",
                "/.passionxbmc/Plugins/Music/", "/.passionxbmc/Plugins/Pictures/", "/.passionxbmc/Plugins/Programs/", "/.passionxbmc/Plugins/Videos/" ]

            self.localdirList    = [ self.themesDir, self.scraperDir, self.scriptDir, self.pluginDir,
                self.pluginMusDir, self.pluginPictDir, self.pluginProgDir, self.pluginVidDir ]

            self.downloadTypeLst = [ "Themes", "Scrapers", "Scripts", "Plugins",
                "Plugins Musique", "Plugins Images", "Plugins Programmes", "Plugins Videos" ]

            self.is_conf_valid = True
        except:
            self.is_conf_valid = False
            logger.LOG( logger.LOG_DEBUG, "Exception while loading configuration file conf.cfg" )
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )

    def getSrvHost( self ):
        return self.host

    def getSrvPassword( self ):
        return self.password

    def getSrvUser( self ):
        return self.user

    def getSrvItemDescripDir( self ):
        return self.itemDescripDir

    def getSrvItemDescripFile( self ):
        """
        Renvoi le nom du fichier de description sur le serveur
        """
        return self.itemDescripFile
