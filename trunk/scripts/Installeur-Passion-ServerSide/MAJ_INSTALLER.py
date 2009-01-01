import ftplib, os
import ConfigParser
import zipfile
import xbmc
import xbmcgui
import string
import sys
import traceback

__language__ = xbmc.getLanguage()

print "****************************************************************"
print "                Updating Installer-passion script               "
print "****************************************************************"

def get_system_platform():
    """ 
    fonction pour recuperer la platform que xbmc tourne 
    """
    platform = "unknown"
    if xbmc.getCondVisibility( "system.platform.linux" ):
        platform = "linux"
    elif xbmc.getCondVisibility( "system.platform.xbox" ):
        platform = "xbox"
    elif xbmc.getCondVisibility( "system.platform.windows" ):
        platform = "windows"
    elif xbmc.getCondVisibility( "system.platform.osx" ):
        platform = "osx"
    print "Platform: %s"%platform
    return platform


def zipextraction (archive,pathdst):
    """
    Decompresse l'archive zip 'archive' au chemin specifié: 'pathdst'
    """
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
                    print "Error during directory creation for archive = ",e

        else:
            #Extraction des fichiers
            compteurfichier = compteurfichier + 1
            data = zfile.read(i)        ## lecture du fichier compresse
            fp = open(filedtst, "wb")   ## creation en local du nouveau fichier
            fp.write(data)              ## ajout des donnees du fichier compresse dans le fichier local
            fp.close()
    zfile.close()
    

def deleteDir(path,keep=[]):
    """
    Efface un repertoire et tout son contenu (le repertoire n'a pas besoin d'etre vide)
    excepté les repertoires (et leur contenu) de la liste keep passée en parametre
    retourne True si le repertoire est efface False sinon
    """
    result = True
    if os.path.isdir(path):
        dirItems=os.listdir(path)
        for item in dirItems:
            itemFullPath=os.path.join(path, item)
            try:
                if os.path.isfile(itemFullPath):
                    # Fichier
                    os.remove(itemFullPath)
                elif os.path.isdir(itemFullPath):
                    if not(itemFullPath in keep):
                        # Repertoire
                        deleteDir(itemFullPath,keep=keep)
            except:
                result = False
                print "deleteDir: Exception during deletion of directory: %s"%path 
                print ("error/INSTALLMAJ go: " + str(sys.exc_info()[0]))
                traceback.print_exc()

        # Suppression du repertoire pere
        if not(path in keep):
            try:
                os.rmdir(path)
            except:
                result = False
                print "deleteDir: Exception during deletion of directory: %s"%path 
                print ("error/INSTALLMAJ go: " + str(sys.exc_info()[0]))
                traceback.print_exc()
    else:
        print "deleteDir: %s is not a directory"%path
        result = False

    return result


def go():
    try:
        if get_system_platform() == "osx":
            print "Platform is MAC OSX : Current update is not compatible with MACOSX"
            print "Stopping update ..."
            
            dialogInfo = xbmcgui.Dialog()
            if __language__ == 'french':
                result = dialogInfo.ok("Installeur Passion-XBMC - Mise a jour", "Désolé, cette mise a jour n'est pas encore disponible pour MAC OSX", "Mise a jour annulée")
            else:
                result = dialogInfo.ok("Installer Passion-XBMC - Update", "Sorry this update is not yet available for MAC OSX", "Update cancelled")
        else:
            print "Other platforme"
            print "Starting update ..."
        
            rootdir = os.path.dirname(os.getcwd().replace(';',''))
            curdir = os.path.join(rootdir, "cache")
        
            confmaj = os.path.join(curdir, "confmaj.cfg")
            config = ConfigParser.ConfigParser()
            config.read(confmaj)
        
            passiondir  = config.get('Localparam', 'passiondir')
            installDir  = config.get('Localparam', 'scriptDir')
            archive     = config.get('Localparam', 'Archive')
            script      = config.get('Localparam', 'Scripttolaunch')       

            dirs2keep = [ passiondir , os.path.dirname(archive) ]
            
            # Nettoyage du repertoire du script avant installation de la nouvelle version
            deleteDir(passiondir,keep=dirs2keep)
            
            print "%s content deleted"%passiondir

            sys.path.append(passiondir)
        
            dp = xbmcgui.DialogProgress()
            if __language__ == 'french':
                dp.create("Installeur Passion-XBMC - Mise a jour","Mise a jour du script en cours","Veuillez patienter...")
            else:
                dp.create("Installer Passion-XBMC - Update","Script update in progress","Please wait...")
            zipextraction(archive,passiondir)
            dp.close()
            del config #On supprime le config parser
            
            dialogInfo = xbmcgui.Dialog()
            if __language__ == 'french':
                result = dialogInfo.ok("Installeur Passion-XBMC - Mise a jour", "Mise a jour effectuée", "Vous pouvez desormais relancer le script")
            else:
                result = dialogInfo.ok("Installer Passion-XBMC - Update", "Update done", "You can now restart the script")
            
        
    except Exception, e:
        print "INSTALLMAJ : go(): Exception",e
        #dialogError = xbmcgui.Dialog()
        #dialogError.ok("Erreur", "Exception durant l'initialisation")
        print ("error/INSTALLMAJ go: " + str(sys.exc_info()[0]))
        traceback.print_exc()



if __name__ == "__main__":
    #ici on pourrait faire des action si le script était lancé en tant que programme
    print "Start script as a program"
    go()
else:
    #ici on est en mode librairie importée depuis un programme
    pass

