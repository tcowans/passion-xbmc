import os
import ConfigParser
import xbmc
import xbmcgui
import shutil

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
    
    #On copie the fichier du repertoire cache dans le repertoire principal
    fileName = os.path.basename(scriptmaj)
    print "Fichier a copier de cache dans root : %s"%fileName
    print "Fichier Source : %s"%scriptmaj
    print "Fichier Destination : %s"%os.path.join(ROOTDIR, fileName)

    shutil.copyfile(scriptmaj,os.path.join(ROOTDIR, fileName))

    #import cache.INSTALLMAJ2
    import INSTALLMAJ2
    #exec("import " + scriptmaj)
    #xbmc.executebuiltin('XBMC.RunScript(%s)'%scriptmaj)
    INSTALLMAJ2.start()
