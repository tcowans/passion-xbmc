import os
import ConfigParser
import xbmc
import xbmcgui
import shutil
import sys

print "****************************************************************"
print "                      Lanceur                                   "
print "****************************************************************"


##############################################################################
#               Initialisation chemins de fichier locaux                     #
##############################################################################
ROOTDIR = os.getcwd().replace(';','')

fichier = os.path.join(ROOTDIR, "conf.cfg")
config = ConfigParser.ConfigParser()
config.read(fichier)

pathok = config.getboolean('InstallPath','pathok')

if pathok == False:
    ##########################################################################
    #               Generation des informations locales                      #
    ##########################################################################
    dp = xbmcgui.DialogProgress()
    dp.create("Configuration","Configuration du systeme","Veuillez patienter...")
    import CONF
    CONF.SetConfiguration()
    dp.close()


##############################################################################
#                   Verification de la mise a jour                           #
##############################################################################
dp = xbmcgui.DialogProgress()
dp.create("Mise a jour automatique","Verification de la mise a jour","Veuillez patienter...")
import CHECKMAJ
CHECKMAJ.start()
dp.close()

config.read(fichier)
updating = config.getboolean('Version','UPDATING')

if updating == False:
    ##########################################################################
    #               Lancement du script                                      #
    ##########################################################################
    import INSTALLEUR
    INSTALLEUR.start()

else:
    ##########################################################################
    #               Lancement de la mise a jour                              #
    ##########################################################################
    scriptmaj = updating = config.get('Version','SCRIPTMAJ')
    
    # Ajout au sys PATH le chemin du script d'install
    dirLibName = os.path.dirname(scriptmaj) # recuperation du chemin du repertoire script
    sys.path.append(dirLibName)
    fileName = os.path.basename(scriptmaj)
    libName  = fileName.replace(".py","")
    
    mon_module_import = "passion"
    exec("import %s"%libName)
    exec("%s.start()"%libName)
        
