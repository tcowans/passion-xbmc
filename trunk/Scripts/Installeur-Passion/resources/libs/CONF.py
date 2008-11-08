import os
import sys
import ConfigParser
import xbmcgui, xbmc

from script_log import *


def SetConfiguration ():
    eval( LOG_FUNCTION )
    """
    Definit les repertoires locaux de l'utilisateur
    """

    LOG( LOG_INFO, "===================================================================")
    #print("")
    LOG( LOG_INFO, "        Setting Configuration                                      ")
    #print("")
    LOG( LOG_INFO, "===================================================================")

    ROOTDIR = os.getcwd().replace(';','')
    fichier = os.path.join(ROOTDIR, "resources", "conf.cfg")
    config = ConfigParser.ConfigParser()
    config.read(fichier)
    USRPath = False

    if os.name=='posix':

        #Linux Case
        LOG( LOG_NOTICE, "linux case" )

        if os.path.isdir(".xbmc") == True:

            # Linux normal case
            XBMC = ".xbmc"+os.sep
            config.set("InstallPath", "path", XBMC)
            USRXBMC = os.sep+'usr'+os.sep+'share'+os.sep+'xbmc'+os.sep
            #Set Linux normal ScraperDir
            ScraperDir  = os.path.join(USRXBMC, "system"+os.sep+"scrapers"+os.sep+"video")
            config.set("InstallPath", "ScraperDir", ScraperDir)
            #Set Linux PMIIIDir
            PMIIIDir = os.path.join(USRXBMC, "skin")
            config.set("InstallPath", "PMIIIDir",PMIIIDir)
            USRPath = True

        else:

            #Linux other case
            dialog = xbmcgui.Dialog()
            XBMC = dialog.browse(0, "Choisissez le dossier d'installation d'XBMC","files")
            #print "linux other case, XBMC = ", XBMC
            LOG( LOG_NOTICE, "linux other case, XBMC = %s", XBMC )
            config.set("InstallPath", "path", XBMC)
            #Set Linux other case ScraperDir
            ScraperDir  = os.path.join(XBMC, "system"+os.sep+"scrapers"+os.sep+"video")
            config.set("InstallPath", "ScraperDir", ScraperDir)


    else:

        # Xbox and Windows case
        LOG( LOG_NOTICE, "Xbox and Windows case" )
        #print "Xbox and Windows case"

        if os.path.isdir("Q:"+os.sep) == True:

            # Xbox and Windows normal case
            XBMC = "Q:"+os.sep
            config.set("InstallPath", "path", XBMC)

        else:

            # Xbox and Windows other case
            dialog = xbmcgui.Dialog()
            XBMC = dialog.browse(0, "Choisissez le dossier d'installation d'XBMC","files")
            #print "win other case, XBMC = ",XBMC
            LOG( LOG_NOTICE, "win other case, XBMC = %s", XBMC )
            config.set("InstallPath", "path", XBMC)

        #Set Win ScraperDir
        scraperDir  = os.path.join(XBMC, "system"+os.sep+"scrapers"+os.sep+"video")
        config.set("InstallPath", "ScraperDir", scraperDir)

    #Set ScraperType
    config.set("InstallPath", "USRPath", USRPath)

    #Set ThemesDir
    ThemesDir   = os.path.join(XBMC, "skin")
    config.set("InstallPath", "ThemesDir", ThemesDir)

    #Set ScriptsDir
    ScriptsDir   = os.path.join(XBMC, "scripts")
    config.set("InstallPath", "ScriptsDir", ScriptsDir)

    #Set PluginDir
    PluginDir   = os.path.join(XBMC, "plugins")
    config.set("InstallPath", "PluginDir", PluginDir)
    PluginMusDir   = os.path.join(XBMC, "plugins" + os.sep + "music")
    config.set("InstallPath", "PluginMusDir", PluginMusDir)
    PluginPictDir   = os.path.join(XBMC, "plugins" + os.sep + "pictures")
    config.set("InstallPath", "PluginPictDir", PluginPictDir)
    PluginProgDir   = os.path.join(XBMC, "plugins" + os.sep + "programs")
    config.set("InstallPath", "PluginProgDir", PluginProgDir)
    PluginVidDir   = os.path.join(XBMC, "plugins" + os.sep + "video")
    config.set("InstallPath", "PluginVidDir", PluginVidDir)
    
    #Set ImageDir
    #ImageDir = os.path.join(ROOTDIR, "images")
    ImageDir = os.path.join(ROOTDIR, "resources", "skins", "Default", "media")
    config.set("InstallPath", "ImageDir", ImageDir)

    #Set CacheDir
    CacheDir = os.path.join(ROOTDIR, "cache")
    config.set("InstallPath", "CacheDir", CacheDir)
    
    #Set UserDataDir
    #UserDataDir = xbmc.translatePath( "Q:\\userdata" )
    UserDataDir = os.path.join(XBMC, "userdata")
    config.set("InstallPath", "UserDataDir", UserDataDir)

    #Save configuration
    config.set("InstallPath", "pathok", True)
    config.write(open(fichier,'w'))

