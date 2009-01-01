import os
import ConfigParser


ROOTDIR = os.getcwd().replace(';','')
fichier = os.path.join(ROOTDIR, "conf.cfg")
config = ConfigParser.ConfigParser()
config.read(fichier)

print "****************************************************************"
print "                      Lanceur                                   "
print "****************************************************************"


pathok = config.getboolean('InstallPath','pathok')

if pathok == True:
    import INSTALLEUR
    #Les parametres d'installation sont definis
    INSTALLEUR.start()
    
else:
    #Les parametres d'installation sont a definir
    import CONF
    CONF.SetConfiguration()
    import INSTALLEUR
    INSTALLEUR.start()
