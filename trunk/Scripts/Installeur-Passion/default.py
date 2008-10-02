import os
import ConfigParser
import xbmc
import xbmcgui
import shutil
import sys

try:
    del sys.modules['CONF']
except:
    pass 
try:
    del sys.modules['CHECKMAJ']
except:
    pass 
try:
    del sys.modules['INSTALLEUR']
except:
    pass 


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
    dp.create("Installeur Passion - Configuration","Configuration du systeme","Veuillez patienter...")
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
    #del sys.modules['os']
    #del sys.modules['main']
    #del sys.modules['shutil']
#    del sys.modules['CONF']
#    del sys.modules['CHECKMAJ']
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

    # Lance le script recupere du server dans un sous processus
    xbmc.executebuiltin('XBMC.RunScript(%s)'%scriptmaj)
    #mon_module_import = "passion"
    #exec("import %s"%libName)
    #exec("%s.start()"%libName)

        
