import ftplib, os
import shutil
import ConfigParser
import zipfile
import xbmc

print "****************************************************************"
print "                 Script de mise a jour auto                     "
print "****************************************************************"
print "version de PassionXBMC Installeur = ",version

def zipextraction (archive,pathdst):
    zfile = zipfile.ZipFile(archive, 'r')
    for i in zfile.namelist():  ## On parcourt l'ensemble des fichiers de l'archive
        print i

        if i.endswith('/'): #Creation des repertoires avant extraction
            dossier = pathdst + os.sep + i
            try:
                os.makedirs(dossier)
                print "dossier = ",dossier
            except Exception, e:
                print "Erreur creation dossier de l'archive = ",e

        else:
            print "File Case"
            data = zfile.read(i)                   ## lecture du fichier compresse
            fp = open(pathdst + os.sep + i, "wb")  ## creation en local du nouveau fichier
            fp.write(data)                         ## ajout des donnees du fichier compresse dans le fichier local
            fp.close()
    zfile.close()


def download(filesrc, filedst):
        pathfiledst = os.path.join(ROOTDIR, "Cache" + os.sep + filedst)
        localFile = open(pathfiledst, "wb")
        self.ftp.retrbinary('RETR ' + filesrc, localFile.write)
        localFile.close()

def orientation():

    for i in remoteDirLst: #On isole le script qu'il faudra telecharger
        if i.endswith('zip'):
            newscript = i

    if newversion in remoteDirLst:

        #Telechargement du nouveau fichier de version
        print "telecharge version"
        filetodl = installeurdir + '/' + file
        download(filetodl,newversion)

        #Lecture des parametres du nouveau fichier de version
        print "lecture fichier"
        newversionfile = os.path.join(ROOTDIR, "Cache" + os.sep + newversion)
        config.read(newversionfile)
        remoteversion = config.get('Version','version')

        if remoteversion == newversion:
            print "version a jour"

        else:
            print "version non a jour"
            #Telechargement de la nouvelle archive
            filetodl = installeurdir + '/' + file
            download(filetodl, newscript)
            print "download version ok"
            #extraction de la nouvelle archive du script
            archive = os.path.join(ROOTDIR, "Cache" + os.sep + pathdst)
            zipextraction (archive,pathdst)
            print "extraction ok"
            script = 'default.py'
            xbmc.executebuiltin(XBMC.RunScript(script))



#########################################################
# INITIALISATION DES PARAMETRES SERVEUR                 #
#########################################################
host = "stock.passionxbmc.org"  # adresse du serveur FTP
user = "anonymous"              # votre identifiant
password = "xxxx"               # votre mot de passe
installeurdir = "/.passionxbmc/Installeur-Passion"

#########################################################
# INITIALISATION DES PARAMETRES LOCAUX                  #
#########################################################
ROOTDIR = os.getcwd().replace(';','')

#LECTURE DU FICHIER LOCAL DE VERSION
oldversionfile = os.path.join(ROOTDIR, "conf.cfg")
config = ConfigParser.ConfigParser()
config.read(oldversionfile)
oldversion = config.get('Version','version')

#POSTULAT DU NOUVEAU FICHIER DE VERSION DISTANT
newversionfile = 'version.cfg'

#########################################################
# DEMARRAGE DE LA CONNEXION                             #
#########################################################
ftp = ftplib.FTP(host,user,password)
remoteDirLst = ftp.nlst(installeurdir)

#########################################################
# DEMARRAGE DU TRAITEMENT                               #
#########################################################
orientation()
