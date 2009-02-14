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

DIALOG_PROGRESS = xbmcgui.DialogProgress()

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
    try:
        for i in zfile.namelist():  ## On parcourt l'ensemble des fichiers de l'archive
            if idracine == False:
                filedst = xbmc.translatePath( pathdst + os.sep + i )
            else:
                filedtst = xbmc.translatePath( pathdst + os.sep + i[len(root):] )
    
            if i.endswith('/'): 
                #Creation des repertoires avant extraction
                compteurdossier = compteurdossier + 1
    
                if compteurdossier == 1 and compteurfichier == 0:
                #On determine le repertoire racine s'il existe pour le retirer du chemin d'extraction
                    idracine = True
                    root = i
    
                else:
                    try:
                        #os.makedirs(filedtst.rstrip( "/" ))
                        os.makedirs(filedtst)
                        #print "creating directory %s"%filedtst
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
    except:
        print "deleteDir: Exception during zipextraction of %s"%archive 
        print ("error/INSTALLMAJ go: " + str(sys.exc_info()[0]))
        traceback.print_exc()
    

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
        print "Starting update ..."
        dialog_lang  = []
        PLATFORM_MAC = get_system_platform() == "osx"
        
        if __language__.lower() == 'french':
            dialog_lang = [ "Installeur Passion-XBMC - Mise a jour", "Mise a jour du script en cours", "Veuillez patienter...", "Recuperation des parametre locaux", 
                           "Suppression de l'ancienne version ","Suppression de des donnees locales de l'ancienne version","Extraction et installation de la mise a jour" ]
        else:
            dialog_lang = [ "Installer Passion-XBMC - Update", "Script update in progress", "Please wait...", "Retrieving local settings", 
                           "Deleting old version", "Deleting local data of the old version", "Extracting and installing update" ]
            

        DIALOG_PROGRESS.create( dialog_lang[0], dialog_lang[1], dialog_lang[2] )
        
#        if get_system_platform() == "osx":
#            print "Platform is MAC OSX : Current update is not compatible with MACOSX"
#            print "Stopping update ..."
#            
#            dialogInfo = xbmcgui.Dialog()
#            if __language__ == 'french':
#                result = dialogInfo.ok("Installeur Passion-XBMC - Mise a jour", "Désolé, cette mise a jour n'est pas encore disponible pour MAC OSX", "Mise a jour annulée")
#            else:
#                result = dialogInfo.ok("Installer Passion-XBMC - Update", "Sorry this update is not yet available for MAC OSX", "Update cancelled")
#        else:
#            print "Other platforme"

        DIALOG_PROGRESS.update( -1, dialog_lang[1], dialog_lang[2], dialog_lang[3] )
        xbmc.sleep(100)
            
        rootdir = os.path.dirname(os.getcwd().replace(';',''))
        curdir = os.path.join(rootdir, "cache")
    
        confmaj = os.path.join(curdir, "confmaj.cfg")
        config = ConfigParser.ConfigParser()
        config.read(confmaj)
    
        passiondir  = config.get('Localparam', 'passiondir')
        installDir  = config.get('Localparam', 'scriptDir')
        archive     = config.get('Localparam', 'Archive')
        script      = config.get('Localparam', 'Scripttolaunch')
        
        SPECIAL_PROFILE_DIR = xbmc.translatePath( "special://profile/" )
        if PLATFORM_MAC or not os.path.isdir( SPECIAL_PROFILE_DIR  ): SPECIAL_PROFILE_DIR = xbmc.translatePath( "P:\\" )
        
        SPECIAL_SCRIPT_DATA = os.path.join( SPECIAL_PROFILE_DIR, "script_data", "Installer Passion-XBMC" )

        dirs2keep = [ passiondir , os.path.dirname(archive) ]
        
        DIALOG_PROGRESS.update( -1, dialog_lang[1], dialog_lang[2], dialog_lang[4] )

        # Nettoyage du repertoire du script avant installation de la nouvelle version
        deleteDir(passiondir,keep=dirs2keep)
        print "%s content deleted"%passiondir
        
        try:
            # Nettoyage des donnes dans user data
            if os.path.isdir( SPECIAL_SCRIPT_DATA ):
                DIALOG_PROGRESS.update( -1, dialog_lang[1], dialog_lang[2], dialog_lang[5] )
                deleteDir(SPECIAL_SCRIPT_DATA)
                print "%s content deleted"%SPECIAL_SCRIPT_DATA
        except Exception, e:
            print "INSTALLMAJ : go(): Impossible to delete script data in user date dir",e
            print ("error/INSTALLMAJ go: " + str(sys.exc_info()[0]))
            traceback.print_exc()
        
        sys.path.append(passiondir)
        
        print "Extracting %s"%archive
        DIALOG_PROGRESS.update( -1, dialog_lang[1], dialog_lang[2], dialog_lang[6] )
        zipextraction(archive,passiondir)

        DIALOG_PROGRESS.close()
        
        #On supprime le config parser
        del config 
        
        print "Update DONE - Please restart the script"
        dialogInfo = xbmcgui.Dialog()
        if __language__.lower() == 'french':
            result = dialogInfo.ok( "Installeur Passion-XBMC - Mise a jour", "Mise a jour effectuée", "Vous pouvez desormais relancer le script" )
        else:
            result = dialogInfo.ok( "Installer Passion-XBMC - Update", "Update done", "You can now restart the script" )
            
        
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

