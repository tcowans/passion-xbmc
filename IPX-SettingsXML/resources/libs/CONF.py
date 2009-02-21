
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

#modules XBMC
import xbmc
from xbmcgui import Dialog

#module logger
try:
    logger = sys.modules[ "__main__" ].logger
except:
    import script_log as logger


SETTINGS = sys.modules[ "__main__" ].SETTINGS

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


def SetConfiguration():
    """ Definit les repertoires locaux de l'utilisateur """
    from utilities import SYSTEM_PLATFORM
    XBMC_ROOT = sys.modules[ "__main__" ].SPECIAL_XBMC_HOME

    logger.LOG( logger.LOG_DEBUG, str( "*" * 85 ) )
    logger.LOG( logger.LOG_DEBUG, "Setting Configuration".center( 85 ) )
    logger.LOG( logger.LOG_DEBUG, str( "*" * 85 ) )
    logger.LOG( logger.LOG_DEBUG, "%s case", SYSTEM_PLATFORM )

    ROOTDIR = os.getcwd().replace( ";", "" )

    USRPath = False

    if not os.path.isdir( XBMC_ROOT ):
        XBMC_ROOT = Dialog().browse( 0, sys.modules[ "__main__" ].__language__( 100 ), "files" )
        logger.LOG( logger.LOG_DEBUG, "Other case, XBMC = %s", XBMC_ROOT )
    SETTINGS.setSetting( "path-xbmc_home", XBMC_ROOT )

    if SYSTEM_PLATFORM == "linux":
        #Set Linux normal ScraperDir
        ScraperDir = os.path.join( os.sep+"usr", "share", "xbmc", "system", "scrapers", "video" )
        SETTINGS.setSetting( "path-ScraperDir", ScraperDir )
        #Set Linux PMIIIDir
        PMIIIDir = os.path.join( os.sep+"usr", "share", "xbmc", "skin" )
        SETTINGS.setSetting( "path-PMIIIDir", PMIIIDir )
        USRPath = True
    else:
        #Set Win ScraperDir
        scraperDir = os.path.join( XBMC_ROOT, "system", "scrapers", "video" )
        SETTINGS.setSetting( "path-ScraperDir", scraperDir )

    #Set ScraperType
    SETTINGS.setSetting( "path-USRPath", repr( USRPath ).lower() )

    #Set ThemesDir
    SETTINGS.setSetting( "path-ThemesDir", os.path.join( XBMC_ROOT, "skin" ) )

    #Set ScriptsDir
    SETTINGS.setSetting( "path-ScriptsDir", os.path.join( XBMC_ROOT, "scripts" ) )

    #Set PluginDir
    PluginDir = os.path.join( XBMC_ROOT, "plugins" )
    SETTINGS.setSetting( "path-PluginDir", PluginDir )
    SETTINGS.setSetting( "path-PluginMusDir", os.path.join( PluginDir, "music" ) )
    SETTINGS.setSetting( "path-PluginPictDir", os.path.join( PluginDir, "pictures" ) )
    SETTINGS.setSetting( "path-PluginProgDir", os.path.join( PluginDir, "programs" ) )
    SETTINGS.setSetting( "path-PluginVidDir", os.path.join( PluginDir, "video" ) )

    #Set CacheDir
    SETTINGS.setSetting( "path-CacheDir", os.path.join( ROOTDIR, "cache" ) )

    #Set UserDataDir
    SETTINGS.setSetting( "path-UserDataDir", os.path.join( XBMC_ROOT, "userdata" ) )

    #Save configuration
    ok = SETTINGS.setSetting( "path_ok", "true", save=True )


class configCtrl:
    """
    OBSOLETE: Controler of configuration
    """
    def __init__( self ):
        """
        Load configuration file, check it, and correct it if necessary
        """
        self.is_conf_valid = False
        try:
            self.rssfeed         = "http://passion-xbmc.org/.xml/?type=rss;limit=10"

            self.itemDescripDir  = "/.passionxbmc/Installeur-Passion/content/"
            self.itemDescripFile = "installeur_content.xml"

            self.host          = SETTINGS.getSetting( "ftp-host", "stock.passionxbmc.org" )
            self.user          = SETTINGS.getSetting( "ftp-user", "anonymous" )
            self.password      = SETTINGS.getSetting( "ftp-password", "xxxx" )

            self.CACHEDIR      = SETTINGS.getSetting( "path-CacheDir" )
            self.themesDir     = SETTINGS.getSetting( "path-ThemesDir" )
            self.scriptDir     = SETTINGS.getSetting( "path-ScriptsDir" )
            self.scraperDir    = SETTINGS.getSetting( "path-ScraperDir" )
            self.pluginDir     = SETTINGS.getSetting( "path-PluginDir" )
            self.pluginMusDir  = SETTINGS.getSetting( "path-PluginMusDir" )
            self.pluginPictDir = SETTINGS.getSetting( "path-PluginPictDir" )
            self.pluginProgDir = SETTINGS.getSetting( "path-PluginProgDir" )
            self.pluginVidDir  = SETTINGS.getSetting( "path-PluginVidDir" )
            self.userdatadir   = SETTINGS.getSetting( "path-UserDataDir" )

            self.USRPath       = SETTINGS.getSetting( "path-USRPath", "false" ) == "true"
            self.PMIIIDir      = ""
            if self.USRPath:
                self.PMIIIDir  = SETTINGS.getSetting( "path-PMIIIDir" )

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
            logger.LOG( logger.LOG_DEBUG, "Exception while loading configuration" )
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
