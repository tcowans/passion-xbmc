import os
import ConfigParser
import xbmc
import xbmcgui
import shutil
import sys
import traceback

if sys.modules.has_key("CONF"):
    del sys.modules['CONF']
if sys.modules.has_key("CHECKMAJ"):
    del sys.modules['CHECKMAJ']
if sys.modules.has_key("INSTALLEUR"):
    del sys.modules['INSTALLEUR']


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
    try:
        ##########################################################################
        #               Lancement du script                                      #
        ##########################################################################
        import INSTALLEUR
        INSTALLEUR.start()
    except Exception, e:
        print "default : Exception pendant le chargement et/ou l'utilisation de l'INSTALLEUR",e
        #dialogError = xbmcgui.Dialog()
        #dialogError.ok("Erreur", "Exception durant l'initialisation")
        print ("error/default: " + str(sys.exc_info()[0]))
        traceback.print_exc()

else:
    ##########################################################################
    #               Lancement de la mise a jour                              #
    ##########################################################################
    try:
        scriptmaj = updating = config.get('Version','SCRIPTMAJ')
            
        # Ajout au sys PATH le chemin du script d'install
        dirLibName = os.path.dirname(scriptmaj) # recuperation du chemin du repertoire script
        sys.path.append(dirLibName)
        fileName = os.path.basename(scriptmaj)
        libName  = fileName.replace(".py","")
    
        # Lance le script recupere du server dans un sous processus
        #xbmc.executebuiltin('XBMC.RunScript(%s)'%scriptmaj)
        xbmc.executescript(scriptmaj)
        #mon_module_import = "passion"
        #exec("import %s"%libName)
        #exec("%s.start()"%libName)
    except Exception, e:
        print "default : Exception pendant le chargement et/ou La mise a jour",e
        #dialogError = xbmcgui.Dialog()
        #dialogError.ok("Erreur", "Exception durant l'initialisation")
        print ("error/default: " + str(sys.exc_info()[0]))
        traceback.print_exc()
print "default : FIN DU SCRIPT"

        
