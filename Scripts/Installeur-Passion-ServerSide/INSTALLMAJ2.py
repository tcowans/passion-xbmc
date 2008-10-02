import ftplib, os
import shutil
import ConfigParser
import zipfile
import xbmc
import xbmcgui
import string
import sys

print "****************************************************************"
print "                      Mise  a jour du script                   "
print "****************************************************************"


def zipextraction (archive,pathdst):
    idracine = False
    zfile = zipfile.ZipFile(archive, 'r')
    compteurdossier = 0
    compteurfichier = 0
    for i in zfile.namelist():  ## On parcourt l'ensemble des fichiers de l'archive
        if idracine == False:
            filedst = pathdst + os.sep + i
        else:
            filedtst = pathdst + os.sep + i[len(root):]

        print filedst

        if i.endswith('/'): #Creation des repertoires avant extraction
            compteurdossier = compteurdossier + 1

            if compteurdossier == 1 and compteurfichier == 0:
                print "id racine true"
                idracine = True
                root = i

            else:
                try:
                    os.makedirs(filedtst)
                    print "dossier = ",filedtst
                except Exception, e:
                    print "Erreur creation dossier de l'archive = ",e

        else:
            compteurfichier = compteurfichier + 1
            print "File Case"
            print "file = ",filedtst
            data = zfile.read(i)                   ## lecture du fichier compresse
            fp = open(filedtst, "wb")  ## creation en local du nouveau fichier
            fp.write(data)                         ## ajout des donnees du fichier compresse dans le fichier local
            fp.close()
    zfile.close()


def start():
    rootdir = os.path.dirname(os.getcwd().replace(';',''))
    print "rootdir: %s"%rootdir
    curdir = os.path.join(rootdir, "cache")
    
    print "curdir : %s"%curdir

    confmaj = os.path.join(curdir, "confmaj.cfg")
    print "Lecture du fichier de conf: %s"%confmaj
    config = ConfigParser.ConfigParser()
    config.read(confmaj)

    passiondir  = config.get('Localparam', 'passiondir')
    installDir  = config.get('Localparam', 'scriptDir')
    archive     = config.get('Localparam', 'Archive')
    script      = config.get('Localparam', 'Scripttolaunch')
    
    print "passiondir : %s"%passiondir
    print "installDir : %s"%installDir
    print "archive : %s"%archive
    print "Scripttolaunch : %s"%script
    
    sys.path.append(passiondir)

    dp = xbmcgui.DialogProgress()
    dp.create("Mise a jour","Mise a jour du script","Veuillez patienter...")
    zipextraction(archive,passiondir)
    dp.close()
    del config #On supprime le config parser
    
    #import CONF
    #CONF.SetConfiguration()
    #dp.close()

    
    #import INSTALLEUR
    #INSTALLEUR.start()
    #exec("import " + script)
    # -> pas besoin de retirer les libs standard, ce sont nos modules qui doivent etre retires
#    del sys.modules['ftplib']
#    del sys.modules['os']
#    del sys.modules['shutil']
#    del sys.modules['zipfile']
#    del sys.modules['xbmcgui']
#    del sys.modules['string']
#    del sys.modules['ConfigParser']
    xbmc.executebuiltin('XBMC.RunScript(%s)'%script)
    print "Sortie de INSTALLMAJ2"
    #sys.exit(0)

if __name__ == "__main__":
    #ici on pourrait faire des action si le script était lancé en tant que programme
    print "demarrage du script en tant que programme"
    start()
else:
    #ici on est en mode librairie importée depuis un programme
    pass

