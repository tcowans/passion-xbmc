
__all__ = [
    # public names
    "configCtrl",
    "TYPE_ROOT",
    "TYPE_SKIN",
    "TYPE_SCRAPER",
    "TYPE_SCRIPT",
    "TYPE_PLUGIN",
    "TYPE_PLUGIN_MUSIC",
    "TYPE_PLUGIN_PICTURES",
    "TYPE_PLUGIN_PROGRAMS",
    "TYPE_PLUGIN_VIDEO",
    "INDEX_SKIN",
    "INDEX_SCRAPER",
    "INDEX_SCRIPT",
    "INDEX_PLUGIN",
    "INDEX_PLUGIN_MUSIC",
    "INDEX_PLUGIN_PICTURES",
    "INDEX_PLUGIN_PROGRAMS",
    "INDEX_PLUGIN_VIDEO",
    "THUMB_SKIN",
    "THUMB_SCRAPER",
    "THUMB_SCRIPT",
    "THUMB_PLUGIN",
    "THUMB_PLUGIN_MUSIC",
    "THUMB_PLUGIN_PICTURES",
    "THUMB_PLUGIN_PROGRAMS",
    "THUMB_PLUGIN_VIDEO",
    ]

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

# FICHIERS DE CONFIGURATION
default_conf = os.path.join( os.getcwd().replace( ";", "" ), "resources", "conf.cfg" )
profile_conf = os.path.join( sys.modules[ "__main__" ].SPECIAL_SCRIPT_DATA, "conf.cfg" )

#FONCTION POUR RECUPERER LES LABELS DE LA LANGUE.
_ = sys.modules[ "__main__" ].__language__


##################################################
#            VARIABLES GLOBALES
##################################################

TYPE_ROOT               = _( 10 )
TYPE_SKIN               = _( 11 )
TYPE_SCRAPER            = _( 12 )
TYPE_SCRIPT             = _( 13 )
TYPE_PLUGIN             = _( 14 )
TYPE_PLUGIN_MUSIC       = _( 15 )
TYPE_PLUGIN_PICTURES    = _( 16 )
TYPE_PLUGIN_PROGRAMS    = _( 17 )
TYPE_PLUGIN_VIDEO       = _( 18 )

#INDEX_ROOT              = None
INDEX_SKIN              = 0
INDEX_SCRAPER           = 1
INDEX_SCRIPT            = 2
INDEX_PLUGIN            = 3
INDEX_PLUGIN_MUSIC      = 4
INDEX_PLUGIN_PICTURES   = 5
INDEX_PLUGIN_PROGRAMS   = 6
INDEX_PLUGIN_VIDEO      = 7

SRV_DIR_SKIN            = "/.passionxbmc/Themes/"
SRV_DIR_SCRAPER         = "/.passionxbmc/Scraper/"
SRV_DIR_SCRIPT          = "/.passionxbmc/Scripts/"
SRV_DIR_PLUGIN          = "/.passionxbmc/Plugins/"
SRV_DIR_PLUGIN_MUSIC    = "/.passionxbmc/Plugins/Music/"
SRV_DIR_PLUGIN_PICTURES = "/.passionxbmc/Plugins/Pictures/"
SRV_DIR_PLUGIN_PROGRAMS = "/.passionxbmc/Plugins/Programs/"
SRV_DIR_PLUGIN_VIDEO    = "/.passionxbmc/Plugins/Videos/"

THUMB_SKIN              = "IPX-defaultSkin.png"
THUMB_SCRAPER           = "IPX-defaultScraper.png"
THUMB_SCRIPT            = "IPX-defaultScript_Plugin.png"
THUMB_PLUGIN            = THUMB_SCRIPT
THUMB_PLUGIN_MUSIC      = "IPX-defaultPluginMusic.png"
THUMB_PLUGIN_PICTURES   = "IPX-defaultPluginPicture.png"
THUMB_PLUGIN_PROGRAMS   = "IPX-defaultPluginProgram.png"
THUMB_PLUGIN_VIDEO      = "IPX-defaultPluginVideo.png"  

INDEX_SRV_ITEM_FORMAT_DIR      = 0
INDEX_SRV_ITEM_FORMAT_FILE_ZIP = 1
INDEX_SRV_ITEM_FORMAT_FILE_RAR = 1
INDEX_SRV_ITEM_FORMAT_INVALID  = 2


def ReadConfig():
    config = ConfigParser()
    if not os.path.exists( profile_conf ):
        config.read( default_conf )
        config.write( open( profile_conf, "w" ) )

    config.read( profile_conf )
    return config


def SetConfiguration():
    """ Definit les repertoires locaux de l'utilisateur """
    from utilities import SYSTEM_PLATFORM
    XBMC_ROOT = sys.modules[ "__main__" ].SPECIAL_XBMC_HOME

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
    config.write( open( profile_conf, "w" ) )


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

#            self.remotedirList   = [ "/.passionxbmc/Themes/", "/.passionxbmc/Scraper/", "/.passionxbmc/Scripts/", "/.passionxbmc/Plugins/",
#                "/.passionxbmc/Plugins/Music/", "/.passionxbmc/Plugins/Pictures/", "/.passionxbmc/Plugins/Programs/", "/.passionxbmc/Plugins/Videos/" ]

            # Repertoire sur le serveur FTP
            # ATTENTION: Ne pas changer l'ordre de ce tableau, il correspond aux index (INDEX_SKIN ...)
            self.remotedirList   = [ SRV_DIR_SKIN, SRV_DIR_SCRAPER, SRV_DIR_SCRIPT, SRV_DIR_PLUGIN, SRV_DIR_PLUGIN_MUSIC, 
                                     SRV_DIR_PLUGIN_PICTURES, SRV_DIR_PLUGIN_PROGRAMS, SRV_DIR_PLUGIN_VIDEO ]
            
            # Repertoire locaux
            # ATTENTION: Ne pas changer l'ordre de ce tableau, il correspond aux index (INDEX_SKIN ...)
            self.localdirList    = [ self.themesDir, self.scraperDir, self.scriptDir, self.pluginDir,
                self.pluginMusDir, self.pluginPictDir, self.pluginProgDir, self.pluginVidDir ]

            #TODO: A supprimer et remplacer par self.typeList une fois le code mias a jour dans les fichiers utilisant CONF
            self.downloadTypeLst = [ "Themes", "Scrapers", "Scripts", "Plugins",
                "Plugins Musique", "Plugins Images", "Plugins Programmes", "Plugins Videos" ]
            
            # Type d'elements
            # ATTENTION: Ne pas changer l'ordre de ce tableau, il correspond aux index (INDEX_SKIN ...)
            self.typeList = [ TYPE_SKIN, TYPE_SCRAPER, TYPE_SCRIPT, TYPE_PLUGIN, TYPE_PLUGIN_MUSIC,    
                              TYPE_PLUGIN_PICTURES, TYPE_PLUGIN_PROGRAMS, TYPE_PLUGIN_VIDEO    ] # Note: TYPE_ROOT est en dehors de la liste

            # Thumbs des elements selon le type
            # ATTENTION: Ne pas changer l'ordre de ce tableau, il correspond aux index (INDEX_SKIN ...)
            self.thumbList    = [ THUMB_SKIN, THUMB_SCRAPER, THUMB_SCRIPT, THUMB_PLUGIN, THUMB_PLUGIN_MUSIC, 
                                  THUMB_PLUGIN_PICTURES, THUMB_PLUGIN_PROGRAMS,THUMB_PLUGIN_VIDEO   ] # Note: TYPE_ROOT est en dehors de la liste
            
            # Filtre sur les elemens a affciher selon le cas (racine ou plugin)
            self.rootDisplayList   = [ INDEX_SKIN, INDEX_SCRAPER, INDEX_SCRIPT, INDEX_PLUGIN ]                                # Liste de la racine: Cette liste est un filtre ( utilisant l'index ) sur les listes ci-dessus
            self.pluginDisplayList = [ INDEX_PLUGIN_MUSIC, INDEX_PLUGIN_PICTURES, INDEX_PLUGIN_PROGRAMS, INDEX_PLUGIN_VIDEO ] # Liste des plugins : Cette liste est un filtre ( utilisant l'index ) sur les listes ci-dessus

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
