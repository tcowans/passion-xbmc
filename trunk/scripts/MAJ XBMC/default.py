from string import *
import sys#, os.path
import os
import ftplib
import xbmcgui, xbmc
import ConfigParser
import traceback

try: Emulating = xbmcgui.Emulating
except: Emulating = False

version = 'Alpha1'
author  = 'Seb'

############################################################################
# Get actioncodes from keymap.xml
############################################################################

ACTION_MOVE_LEFT                 = 1    
ACTION_MOVE_RIGHT                = 2
ACTION_MOVE_UP                   = 3
ACTION_MOVE_DOWN                 = 4
ACTION_PAGE_UP                   = 5
ACTION_PAGE_DOWN                 = 6
ACTION_SELECT_ITEM               = 7
ACTION_HIGHLIGHT_ITEM            = 8
ACTION_PARENT_DIR                = 9
ACTION_PREVIOUS_MENU             = 10
ACTION_SHOW_INFO                 = 11

ACTION_PAUSE                     = 12
ACTION_STOP                      = 13
ACTION_NEXT_ITEM                 = 14
ACTION_PREV_ITEM                 = 15

#############################################################################
# autoscaling values
#############################################################################

HDTV_1080i      = 0 #(1920x1080, 16:9, pixels are 1:1)
HDTV_720p       = 1 #(1280x720, 16:9, pixels are 1:1)
HDTV_480p_4x3   = 2 #(720x480, 4:3, pixels are 4320:4739)
HDTV_480p_16x9  = 3 #(720x480, 16:9, pixels are 5760:4739)
NTSC_4x3        = 4 #(720x480, 4:3, pixels are 4320:4739)
NTSC_16x9       = 5 #(720x480, 16:9, pixels are 5760:4739)
PAL_4x3         = 6 #(720x576, 4:3, pixels are 128:117)
PAL_16x9        = 7 #(720x576, 16:9, pixels are 512:351)
PAL60_4x3       = 8 #(720x480, 4:3, pixels are 4320:4739)
PAL60_16x9      = 9 #(720x480, 16:9, pixels are 5760:4739) 
 
############################################################################
 
class ftpDownloadCtrl:
    """
 
    Controleur de download via FTP
    Cette classe gere les download via FTP de fichiers et repertoire
 
    """
    def __init__(self,host,user,password,remotepath,progressbar_cb=None,dialogProgressWin=None):
        """
        Fonction d'init de la classe ftpDownloadCtrl
        Initialise toutes les variables et lance la connection au serveur FTP
        """
 
        #Initialise les attributs de la classe ftpDownloadCtrl avec les parametres donnes au constructeur
        self.host               = host
        self.user               = user
        self.password           = password
        self.remotepath         = remotepath
        self.ftp                = ftplib.FTP(self.host,self.user,self.password)
        self.ficmajxbmc         = ""

        #Connection au serveur FTP
        try: 
            self.ftp.cwd(self.remotepath) 
        except Exception, e: 
            print "ftpDownloadCtrl::__init__: Exception durant la connection FTP",e
            print "Impossible de se connecter au serveur FTP: %s"%self.host
            

    def closeConnection(self):
        """
        Close FTP conenction
        """
        #on se deconnecte du serveur pour etre plus propre
        self.ftp.quit()
    
    def download(self,source,pathdst,progressbar_cb=None,dialogProgressWin=None):
        """
        Telecharge les elements a un chemin specifie (repertoires, sous repertoires et fichiers)
        a dans un repertorie local dependant du type de telechargement (theme, scraper, script ...)
        pathsrc     : chemin sur le serveur de l'element a telecharger
        rootdirsrc  : Repertoire root sur le server (correspondant a un type de downaload) - Exemple : "/.passionxbmc/Scraper/" pour les scrapers
        typeIndex   : Index correspondant au type de telechargement, permet notamment de definir le repertorie local de telechargement
        Renvoi le status du download:
            - (-1) pour telechargement annule
            - (1)  pour telechargement OK
        """
        self.pathdst            = pathdst
        pathsrc = self.remotepath + source

        try:
            if (progressbar_cb != None) and (dialogProgressWin != None):
                percent = 0
                #print "=================================="
                #print
                #print "Pourcentage telecharger: %d"%percent
                #print
                #print "=================================="
                # Initialisation de la barre de progression (via callback)
                progressbar_cb(percent,dialogProgressWin)
        except Exception, e:
            print("download - Exception ProgressBar UI callback for download")
            print(e)
            print progressbar_cb
        
        # Appel de la fonction privee en charge du download - 
        status = self._download(pathsrc,progressbar_cb,dialogProgressWin,0,1)
        return  status # retour du status du download recupere

    def _download(self, pathsrc,progressbar_cb=None,dialogProgressWin=None,curPercent=0,coeff=1):
        """
        Telecharge un element sur le server FTP
        """
        # Liste le repertoire
        
        curDirList = self.ftp.nlst(pathsrc) #TODO: ajouter try/except
        curDirListSize = len(curDirList)
        print curDirList
        for i in curDirList:
            print 'i = ',i
            if dialogProgressWin.iscanceled():
                print "Telechargement annulé par l'utilisateur"
                # Sortie de la boucle via return
                return -1 # -1 pour telechargement annule
            try :
                # Calcule le pourcentage
                #TODO: verifier que la formule pour le pourcentage est OK (la ca ette fait un peu trop rapidement)
                percent = min(curPercent + int((float(curDirList.index(i)+1)*100)/(curDirListSize * coeff)),100)
                #print "=================================="
                #print
                #print "Pourcentage téléchargé: %d"%percent
                #print
                #print "=================================="
                self._downloaddossier(i,dialogProgressWin=dialogProgressWin,curPercent=percent,coeff=coeff*curDirListSize)
                percent = int((float(curDirList.index(i)+1)*100)/(curDirListSize * coeff))
            except Exception, e:
                try:
                    #Mise a jour de la barre de progression (via cvallback)
                    #TODO: Solution temporaraire -> on veut afficher le nom du theme/script/skin en cours en plus du fichier
                    dialogProgressWin.update(percent,i)
                except Exception, e:
                    print("downloadVideo - Exception calling UI callback for download")
                    print(e)
                    print progressbar_cb

                self._downloadfichier(i)     
 
    def _downloaddossier(self, pathsrc,progressbar_cb=None,dialogProgressWin=None,curPercent=0,coeff=1):
        """
        Telecharge un repertoire sur le server FTP
        Note: fait un appel recursif sur download
        """
        emptydir = False
        self.ftp.cwd(pathsrc) # c'est cette commande qui genere l'exception dans le cas d'un fichier
        try:
            dirContent = self.ftp.nlst(pathsrc)
            print dirContent
        except Exception, e: 
            print "_downloaddossier: Exception ftp.nlst(i)",e
            print "_downloaddossier: repertoire VIDE"
            emptydir = True
 
        # Cree le chemin du repertorie local 
        # Extrait le chemin relatif: soustrait au chemin remote le chemin de base: par exemple on veut retirer du chemin; /.passionxbmc/Themes
        remoteRelDirPath = pathsrc.replace(self.remotepath,'')

        # On remplace dans le chemin sur le serveur FTP les '/' par le separateur de l'OS sur lequel on est
        localRelDirPath = remoteRelDirPath.replace('/',os.sep)
 
        # Cree le chemin local (ou on va sauver)
        localAbsDirPath = os.path.join(self.pathdst, localRelDirPath) 
 
        try: 
            print 'localAbsDirPath =',localAbsDirPath
            os.makedirs(localAbsDirPath)

        except Exception, e: 
            print "_downloaddossier: Exception dossier",e
            print "_downloaddossier: repertoire KO"
            
        if (emptydir == True):
            print "_downloaddossier: Repertoire %s VIDE"%dirsrc
        else:
            self._download(pathsrc,dialogProgressWin=dialogProgressWin,curPercent=curPercent,coeff=coeff)
 
    def _downloadfichier(self, filesrc):
        """
        Fonction privee (ne pouvant etre appelee que par la classe ftpDownloadCtrl elle meme)
        Telecharge un fichier sur le server FTP
        """
        # Cree le chemin du repertorie local 
        # Extrait le chemin relatif: soustrait au chemin remote le chemin de base: par exemple on veut retirer du chemin; /.passionxbmc/Themes
        remoteRelFilePath = filesrc.replace(self.remotepath,'')
        # On remplace dans le chemin sur le serveur FTP les '/' par le separateur de l'OS sur lequel on est
        localRelFilePath = remoteRelFilePath.replace('/',os.sep)
 
        # Cree le chemin local (ou on va sauver)
        localAbsFilePath = os.path.join(self.pathdst, localRelFilePath)
        if localAbsFilePath.endswith('.xbe'):
            self.ficmajxbmc = localAbsFilePath
 
        try: 
            print 'localAbsFilePath =',localAbsFilePath
            # On ferme le fichier que l'on ouvre histoire d'etre plus clean (pas sur que ce soit vraiment indispensable, mais bon ...)
            localFile = open(localAbsFilePath, "wb")
            self.ftp.retrbinary('RETR ' + filesrc, localFile.write)
            localFile.close()
        except Exception, e:
            print e
            print "_downloadfichier: fichier KO"
            

class traitement:
    
    def __init__(self):
        self.rootdir            = os.getcwd().replace(';','')
        self.installpath        = ""
        #################################################################
        #            INITIALISATION PARAMETRES SERVEUR                  #
        #################################################################
        self.fichierconf        = os.path.join(self.rootdir, "conf.cfg")
        self.ConfParser         = ConfigParser.ConfigParser()
        self.ConfParser.read(self.fichierconf)
        self.host               = self.ConfParser.get('ServeurID','host')
        self.user               = self.ConfParser.get('ServeurID','user')
        self.password           = self.ConfParser.get('ServeurID','password')
        self.remotepath         = self.ConfParser.get('ServeurID','path') #"/.passionxbmc/Xcalibur/"
        self.majxbmc            = self.ConfParser.get('ServeurID','majxbmc')
        self.annul              = False
        try:
            self.FTPCtrl = ftpDownloadCtrl(self.host,self.user,self.password,self.remotepath)
            
        except Exception, e:
            print "Window::__init__: Exception durant la connection FTP",e
            print "Impossible de se connecter au serveur FTP: %s"%self.host
            dialogError = xbmcgui.Dialog()
            dialogError.ok("Erreur", "Exception durant l'initialisation")
            print ("error/MainWindow __init__: " + str(sys.exc_info()[0]))
            traceback.print_exc()

    
    def lancement(self):
        confirm = self.askmajxbmc()  
        if confirm == True:
            self.choosepath()
            self.download()
            if self.annul == False:
                self.lancementmaj()
            self.FTPCtrl.closeConnection()
        
    
    def askmajxbmc(self):
        titre = 'XBMC Updater'
        question = 'Voulez vous mettre a jour XBMC?'
        dialog = xbmcgui.Dialog()
        ret = dialog.yesno(titre, question)
        if ret == True:
            return True
        else:
            return False
    
    def choosepath(self):
        titre = 'Choisissez un chemin temporaire de telechargement'
        choix1 = 'E:'+os.sep+'Apps'+os.sep+self.majxbmc
        choix2 = 'Autre'
        liste = [choix1,choix2]
        dialog = xbmcgui.Dialog()
        ret = dialog.select(titre, liste)
        if ret == 0:
            self.installpath = 'E:'+os.sep+'Apps'+os.sep
        else:
            dialog = xbmcgui.Dialog()
            self.installpath = dialog.browse(0, "Choisissez un dossier","files")
            #lenbrowse = (len(browse))-1
            #self.installpath = browse[:lenbrowse]
            print "chemin d'installation = ",self.installpath
    
    def download(self):
        dp = xbmcgui.DialogProgress()
        dp.create("Telechargement en cours ...", "XBMC en cours de telechargement")
        downloadStatus = self.FTPCtrl.download(self.majxbmc, self.installpath, progressbar_cb=self.updateProgress_cb,dialogProgressWin = dp)
        #self.FTPCtrl.download(self.majxbmc,self.installpath)
        dp.close()
        
        if downloadStatus == -1:
            self.annul = True
            # Telechargment annule par l'utilisateur
            title    = "Telechargement annule"
            message1 = "%s"%(self.installpath)
            message2 = "Telechargement annule alors qu'il etait en cours "
            message3 = "Il se peut que des fichiers aient deja ete telecharges"
        else:
            title    = "Telechargement termine"
            message1 = 'La nouvelle version de XBMC'
            message2 = "a ete telechargee dans le repertoire:"
            message3 = "%s"%(self.installpath)

        dialogInfo = xbmcgui.Dialog()
        dialogInfo.ok(title, message1, message2,message3)

    def updateProgress_cb(self, percent, dp=None):
        """
        Met a jour la barre de progression
        """
        #TODO Dans le futur, veut t'on donner la responsabilite a cette fonction le calcul du pourcentage????
        try:
            print percent
            dp.update(percent)
        except:
            percent = 100
            dp.update(percent)
    
    def lancementmaj(self):
        dialog = xbmcgui.Dialog()
        reponse = dialog.yesno('Mise a jour de XBMC', 'Voulez vous lancer la MAJ de xbmc?')
        if reponse == True:
            xbmc.executebuiltin('XBMC.RunXBE(%s)'%self.FTPCtrl.ficmajxbmc)       
           

########
#
# Main
#
########
 
print("===================================================================")
print("")
print("        XBMC MAJ " + version + " STARTS")
print("")
print("===================================================================")

w = traitement()
w.lancement()
del w 

