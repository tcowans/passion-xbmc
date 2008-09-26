import os
import ConfigParser

def SetConfiguration ():

    print("===================================================================")
    print("")
    print("        Setting Configuration                                      ")
    print("")
    print("===================================================================")

    ROOTDIR = os.getcwd().replace(';','')
    fichier = os.path.join(ROOTDIR, "conf.cfg")
    config = ConfigParser.ConfigParser()
    config.read(fichier)
    USRPath = False

    if os.name=='posix':

        #Linux Case
        print "linux case"

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
            print "linux other case, XBMC = ", XBMC
            config.set("InstallPath", "path", XBMC)
            #Set Linux other case ScraperDir
            scraperDir  = os.path.join(XBMC, "system"+os.sep+"scrapers"+os.sep+"video")
            config.set("InstallPath", "ScraperDir", ScraperDir)

        #Set Linux ScraperDir
        #ScraperDir  = os.path.join(ROOTDIR, "download")
        #config.set("InstallPath", "ScraperDir", ScraperDir)

    else:

        # Xbox and Windows case
        print "Xbox and Windows case"

        if os.path.isdir("Q:"+os.sep) == True:

           # Xbox and Windows normal case
            XBMC = "Q:"+os.sep
            config.set("InstallPath", "path", XBMC)

        else:

           # Xbox and Windows other case
           dialog = xbmcgui.Dialog()
           XBMC = dialog.browse(0, "Choisissez le dossier d'installation d'XBMC","files")
           print "win other case, XBMC = ",XBMC
           config.set("InstallPath", "path", XBMC)

        #Set Win ScraperDir
        scraperDir  = os.path.join(XBMC, "system"+os.sep+"scrapers"+os.sep+"video")
        config.set("InstallPath", "ScraperDir", scraperDir)

    #Set ScraperType
    config.set("InstallPath", "USRPath", USRPath)

    #Set ThemesDir
    ThemesDir   = os.path.join(XBMC, "skin")
    config.set("InstallPath", "ThemesDir", ThemesDir)

    #Set TempscriptDir
    TempscriptDir = os.path.join(ROOTDIR, "download")
    config.set("InstallPath","TempscriptDir",TempscriptDir)

    #Set ScriptsDir
    ScriptsDir   = os.path.join(XBMC, "scripts")
    config.set("InstallPath", "ScriptsDir", ScriptsDir)

    #Set ImageDir
    ImageDir = os.path.join(ROOTDIR, "images")
    config.set("InstallPath", "ImageDir", ImageDir)

    #Set CacheDir
    CacheDir = os.path.join(ROOTDIR, "cache")
    config.set("InstallPath", "CacheDir", CacheDir)

    #Save configuration
    config.set("InstallPath", "pathok", True)
    config.write(open(fichier,'w'))

