import os
import ConfigParser
import xbmc


ROOTDIR = os.getcwd().replace(';','')
fichier = os.path.join(ROOTDIR, "conf.cfg")
print "fichier = ",fichier
config = ConfigParser.ConfigParser()
config.read(fichier)

print "****************************************************************"
print "                      Lanceur                                   "
print "****************************************************************"

#print "dans fichier", config.get(
pathok = config.getboolean('InstallPath','pathok')

print "lancement du script de mise a jour"
script = os.path.join(ROOTDIR, 'CHECKMAJ.py')
xbmc.executebuiltin('XBMC.RunScript(%s)'%script)

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
