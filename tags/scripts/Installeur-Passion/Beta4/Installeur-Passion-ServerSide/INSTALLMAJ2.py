import ftplib, os
import ConfigParser
import zipfile
import xbmc
import xbmcgui
import string
import sys
import traceback

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

        if i.endswith('/'): 
            #Creation des repertoires avant extraction
            compteurdossier = compteurdossier + 1

            if compteurdossier == 1 and compteurfichier == 0:
            #On determine le repertoire racine s'il existe pour le retirer du chemin d'extraction
                idracine = True
                root = i

            else:
                try:
                    os.makedirs(filedtst)
                except Exception, e:
                    print "Erreur creation dossier de l'archive = ",e

        else:
            #Extraction des fichiers
            compteurfichier = compteurfichier + 1
            data = zfile.read(i)                   ## lecture du fichier compresse
            fp = open(filedtst, "wb")  ## creation en local du nouveau fichier
            fp.write(data)                         ## ajout des donnees du fichier compresse dans le fichier local
            fp.close()
    zfile.close()


def go():
    try:
        rootdir = os.path.dirname(os.getcwd().replace(';',''))
        curdir = os.path.join(rootdir, "cache")
    
        confmaj = os.path.join(curdir, "confmaj.cfg")
        config = ConfigParser.ConfigParser()
        config.read(confmaj)
    
        passiondir  = config.get('Localparam', 'passiondir')
        installDir  = config.get('Localparam', 'scriptDir')
        archive     = config.get('Localparam', 'Archive')
        script      = config.get('Localparam', 'Scripttolaunch')       

        sys.path.append(passiondir)
    
        dp = xbmcgui.DialogProgress()
        dp.create("Installeur passion - Mise a jour","Mise a jour du script en cours","Veuillez patienter...")
        zipextraction(archive,passiondir)
        dp.close()
        del config #On supprime le config parser
        
        dialogInfo = xbmcgui.Dialog()
        result = dialogInfo.ok("Installeur passion - Mise a jour", "Mise a jour effectuée", "Vous pouvez desormais relancer le script")
        
    except Exception, e:
        print "INSTALLMAJ : go(): Exception",e
        #dialogError = xbmcgui.Dialog()
        #dialogError.ok("Erreur", "Exception durant l'initialisation")
        print ("error/INSTALLMAJ go: " + str(sys.exc_info()[0]))
        traceback.print_exc()

if __name__ == "__main__":
    #ici on pourrait faire des action si le script était lancé en tant que programme
    print "demarrage du script en tant que programme"
    go()
else:
    #ici on est en mode librairie importée depuis un programme
    pass

