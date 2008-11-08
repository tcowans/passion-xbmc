
# script constants
__script__ = "Installeur-Passion"
__plugin__ = "Unknown"
__author__ = "Team Passion-XBMC"
__url__    = "http://passion-xbmc.org/index.php"
__svn_url__ = "http://code.google.com/p/passion-xbmc/source/browse/#svn/trunk/Scripts/Installeur-Passion"
__credits__ = "Team XBMC, http://xbmc.org/"
__platform__  = "xbmc media center"
__date__    = "08-11-2008"
__version__ = "1.0.0dev"
__svn_revision__ = 0


import os
import ConfigParser
import xbmc
import xbmcgui
import shutil
import sys
#import traceback

if sys.modules.has_key("CONF"):
    del sys.modules['CONF']
if sys.modules.has_key("CHECKMAJ"):
    del sys.modules['CHECKMAJ']
if sys.modules.has_key("INSTALLEUR"):
    del sys.modules['INSTALLEUR']

from resources.libs.script_log import *

def MAIN():
    LOG( LOG_INFO, "****************************************************************" )
    LOG( LOG_INFO, "                      Lanceur                                   " )
    LOG( LOG_INFO, "****************************************************************" )


    ##############################################################################
    #               Initialisation chemins de fichier locaux                     #
    ##############################################################################
    ROOTDIR = os.getcwd().replace(';','')

    dp = xbmcgui.DialogProgress()
    dp.create("Installateur Passion","","")

    fichier = os.path.join(ROOTDIR, "resources", "conf.cfg")
    config = ConfigParser.ConfigParser()
    config.read(fichier)

    pathok = config.getboolean('InstallPath','pathok')

    if pathok == False:
        ##########################################################################
        #               Generation des informations locales                      #
        ##########################################################################
        dp.update(50,"Configuration du systeme","Veuillez patienter...")
        from resources.libs import CONF
        CONF.SetConfiguration()
        #dp.close()

    ##############################################################################
    #                   Verification de la mise a jour                           #
    ##############################################################################
    dp.update(75, "Verification de la mise a jour","Veuillez patienter...")
    from resources.libs import CHECKMAJ
    CHECKMAJ.go()

    dp.update(100, ""," ")
    config.read(fichier)
    updating = config.getboolean('Version','UPDATING')

    dp.close()

    if updating == False:
        try:
            ##########################################################################
            #               Lancement du script                                      #
            ##########################################################################
            from resources.libs import INSTALLEUR
            INSTALLEUR.go()
        except Exception, e:
            #print "default : Exception pendant le chargement et/ou l'utilisation de l'INSTALLEUR",e
            #dialogError = xbmcgui.Dialog()
            #dialogError.ok("Erreur", "Exception durant l'initialisation")
            #print ("error/default: " + str(sys.exc_info()[0]))
            EXC_INFO( LOG_ERROR, sys.exc_info() )
            #traceback.print_exc()
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
            #import INSTALLEUR
            #INSTALLEUR.go()
            #mon_module_import = "passion"
            #exec("import %s"%libName)
            #exec("%s.go()"%libName)
        except Exception, e:
            #print "default : Exception pendant le chargement et/ou La mise a jour",e
            LOG( LOG_ERROR, "default : Exception pendant le chargement et/ou La mise a jour" )
            #dialogError = xbmcgui.Dialog()
            #dialogError.ok("Erreur", "Exception durant l'initialisation")
            #print ("error/default: " + str(sys.exc_info()[0]))
            EXC_INFO( LOG_ERROR, sys.exc_info() )
            #traceback.print_exc()
            #print "default : FIN DU SCRIPT"

if __name__ == "__main__":
    MAIN()