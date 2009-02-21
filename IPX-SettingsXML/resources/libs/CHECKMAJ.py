
import os
import sys
import ftplib
from ConfigParser import ConfigParser

import xbmc
import xbmcgui


#module logger
try:
    logger = sys.modules[ "__main__" ].logger
except:
    import script_log as logger


#FONCTION POUR RECUPERER LES LABELS DE LA LANGUE.
_ = sys.modules[ "__main__" ].__language__

SETTINGS = sys.modules[ "__main__" ].SETTINGS
UPDATE_STARTUP = ( SETTINGS.getSetting( "gen-update_startup", "true" ) == "true" )


logger.LOG( logger.LOG_DEBUG, str( "*" * 85 ) )
logger.LOG( logger.LOG_DEBUG, "Script de mise a jour auto".center( 85 ) )
logger.LOG( logger.LOG_DEBUG, str( "*" * 85 ) )


class CheckMAJ:
    def __init__(self):

        self.rootdir = os.getcwd().replace(';','')

        ##############################################################################
        #                   Initialisation parametres locaux                         #
        ##############################################################################
        self.cacheDir   = SETTINGS.getSetting( "path-CacheDir" )
        self.scriptDir  = SETTINGS.getSetting( "path-ScriptsDir" )
        self.curversion = SETTINGS.getSetting( "version", sys.modules[ "__main__" ].__version__ )

        ##############################################################################
        #                   Verification des repertoires et creation si besoin
        ##############################################################################
        self.verifrep(self.cacheDir)

        ##############################################################################
        #                   Initialisation parametres serveur                        #
        ##############################################################################

        self.host             = SETTINGS.getSetting( "ftp-host", "stock.passionxbmc.org" )
        self.user             = SETTINGS.getSetting( "ftp-user", "anonymous" )
        self.password         = SETTINGS.getSetting( "ftp-password", "xxxx" )
        self.remoteversionDir = "/.passionxbmc/Installeur-Passion/"

        self.filetodl = ""
        self.newversionfile = ""
        self.newversion = ""
        self.filedst = ""
        self.completedfile = ""
        self.versiontodl = ""
        self.confmaj = os.path.join(self.cacheDir, "confmaj.cfg")
        self.archive = ""
        self.scripttolaunch = os.path.join(self.rootdir, "default.py")

        #########################################################
        # DEMARRAGE DE LA CONNEXION                             #
        #########################################################
        if UPDATE_STARTUP:
            self.ftp = ftplib.FTP(self.host,self.user,self.password)
            self.remoteDirLst = self.ftp.nlst(self.remoteversionDir)
        else:
            self.ftp = UPDATE_STARTUP
            self.remoteDirLst = list()

    def verifrep(self,folder):
        """
        verifrep (de myCine)
        verifie que le repertoire existe et le cree si besoin
        """
        try:
            if not os.path.exists(folder):
                os.makedirs(folder)

        except:
            logger.LOG( logger.LOG_DEBUG, "verifrep - Exception while creating folder %s", folder )
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info() )

    def download(self):
        """
        Fonction de telechargement commune : version, archive, script de mise a jour
        """
        self.ftp = ftplib.FTP(self.host,self.user,self.password)
        self.filedst = self.filetodl[len(self.remoteversionDir):]
        self.completedfile = os.path.join(self.cacheDir, self.filedst)
        localFile = open(str(self.completedfile), "wb")
        self.ftp.retrbinary('RETR ' + self.filetodl, localFile.write)
        localFile.close()
        self.ftp.quit()

    def orientation(self):
        """
        Oriente le script vers une mise a jour ou non
        """
        self.delFiles(self.cacheDir) # on vide le cache pour etre sur d'etre plus propre

        if UPDATE_STARTUP:
            for file in self.remoteDirLst:
                #On isole les fichiers qu'il faudra telecharger
                if file.endswith('zip'):
                    self.newscript = file
                elif file.endswith('py'):
                    self.installmaj = file
                elif file.endswith('cfg'):
                    self.versiontodl = file

            #Telechargement du nouveau fichier de version
            self.filetodl = self.versiontodl
            self.download()

            #Lecture des parametres du nouveau fichier de version
            remoteConfParser = ConfigParser()
            remoteConfParser.read(self.completedfile)
            self.newversion = remoteConfParser.get('Lastversion','lastversion')

            # Suppression de l'instance du config parser de remoteConf
            del remoteConfParser
        else:
            self.newversion = self.curversion
        self.newversion = self.newversion.lower()

        if self.newversion == self.curversion or self.newversion in self.curversion:
            #version a jour
            SETTINGS.setSetting( "updating", "false" )
        else:
            # version non a jour - Demande a l'utlisateur
            # Message a l'utilisateur pour l'update
            dialog = xbmcgui.Dialog()
            if dialog.yesno( _( 0 ), _( 105 ), _( 106 ) ):

                #Telechargement de la nouvelle archive
                self.filetodl = self.newscript
                self.download()
                self.archive = self.completedfile
                #Telechargement du script d'extraction
                self.filetodl = self.installmaj
                self.download()
                scriptmaj = self.completedfile

                SETTINGS.setSetting( "path-scriptMAJ", scriptmaj )
                SETTINGS.setSetting( "updating", "true" )
                self.configmaj()
            else:
                #L'utilisateur a REFUSE la mise a jour
                SETTINGS.setSetting( "updating", "false" )

    def configmaj(self):
        """
        Creation du fichier de conf qui servira au script de mise a jour
        """
        configMAJParser = ConfigParser()
        configMAJParser.add_section('Localparam')
        configMAJParser.set('Localparam', 'PassionDir', self.rootdir)
        configMAJParser.set('Localparam', 'Archive', self.archive)
        configMAJParser.set('Localparam','Scripttolaunch',self.scripttolaunch)
        configMAJParser.set("Localparam", "scriptDir", self.scriptDir)
        configMAJParser.write(open(self.confmaj,'w'))
        # Suppression de l'instance de configMAJParser
        del configMAJParser


    def delFiles(self,folder):
        for root, dirs, files in os.walk(folder , topdown=False):
            for name in files:
                logger.LOG( logger.LOG_WARNING, "Effaccement de %s en cours ...", name )
                try:
                    os.remove(os.path.join(root, name))
                except:
                    logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info() )


def go():
    CkMAJ = CheckMAJ()
    CkMAJ.orientation()
    del CkMAJ

