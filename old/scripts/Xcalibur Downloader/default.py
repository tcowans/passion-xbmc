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
    def __init__(self,host,user,password,remotepath):
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

    def download(self, pathsrc,pathdst):
        """
        Telecharge un element sur le server FTP
        """
        # Liste le repertoire
        self.pathdst            = pathdst
        curDirList = self.ftp.nlst(pathsrc) #TODO: ajouter try/except

        for i in curDirList:
            try :
                self._downloaddossier(i)
            except Exception, e:
                self._downloadfichier(i)     
 
    def _downloaddossier(self, pathsrc):
        """
        Telecharge un repertoire sur le server FTP
        Note: fait un appel recursif sur download
        """
        emptydir = False
        self.ftp.cwd(pathsrc) # c'est cette commande qui genere l'exception dans le cas d'un fichier
        try:
            dirContent = self.ftp.nlst(pathsrc)
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
            os.makedirs(localAbsDirPath)

        except Exception, e: 
            print "_downloaddossier: Exception dossier",e
            print "_downloaddossier: repertoire KO"
            
        if (emptydir == True):
            print "_downloaddossier: Repertoire %s VIDE"%dirsrc
        else:
            self._download(dirsrc)
 
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
 
        try: 
            # On ferme le fichier que l'on ouvre histoire d'etre plus clean (pas sur que ce soit vraiment indispensable, mais bon ...)
            localFile = open(localAbsFilePath, "wb")
            self.ftp.retrbinary('RETR ' + filesrc, localFile.write)
            localFile.close()
        except Exception, e:
            print e
            print "_downloadfichier: fichier KO"
            
            

class MainWindow(xbmcgui.Window):
    def __init__(self):
        if Emulating: xbmcgui.Window.__init__(self)
        if not Emulating:
            self.setCoordinateResolution(PAL_4x3) # Set coordinate resolution to PAL 4:3
            self.rootdir            = os.getcwd().replace(';','')
            self.imagedir           = os.path.join(self.rootdir, "images")
            self.fichierconf        = os.path.join(self.rootdir, "conf.cfg")
            self.ConfParser         = ConfigParser.ConfigParser()
            self.ConfParser.read(self.fichierconf)
            self.host               = self.ConfParser.get('ServeurID','host')
            self.user               = self.ConfParser.get('ServeurID','user')
            self.password           = self.ConfParser.get('ServeurID','password')
            self.remotepath         = self.ConfParser.get('ServeurID','path') #"/.passionxbmc/Xcalibur/"
            self.remotedirList      = ""
            self.cible              = ""
            self.FTPCtrl = ftpDownloadCtrl(self.host,self.user,self.password,self.remotepath)

            #Connection au serveur FTP
            try: 
                self.ftp = ftplib.FTP(self.host,self.user,self.password) # on se connecte

                #Va au chemin distant specifie (remote directory) 
                self.ftp.cwd(self.remotepath) #TODO: temporaire on se connecte dans la section themes pour le moment


                # Create browser instance
                #self.nabboxBrowser = browser()

                # Display Loading Window while we are loading the information from the website
                dialogUI = xbmcgui.DialogProgress()
                dialogUI.create("Xcalibur Downloader", "Creation de l'interface Graphique", "Veuillez patienter...")

                # Background image
                print ("Get Background image from : " + os.path.join(self.imagedir,"background.png"))
                self.addControl(xbmcgui.ControlImage(0,0,720,576, os.path.join(self.imagedir,"background.png")))
               
                # Set List border image
                self.listborder = xbmcgui.ControlImage(20,120,680,446, os.path.join(self.imagedir, "list-border.png"))
                self.addControl(self.listborder)
                self.listborder.setVisible(True)

                # Set List background image
                self.listbackground = xbmcgui.ControlImage(23, 163, 674, 400, os.path.join(self.imagedir, "list-white.png"))
                self.addControl(self.listbackground)
                self.listbackground.setVisible(True)

                # Set List hearder image
                self.header = xbmcgui.ControlImage(23,123,674,40, os.path.join(self.imagedir, "list-header.png"))
                self.addControl(self.header)
                self.header.setVisible(True)

                # Title of the current pages
                self.strMainTitle = xbmcgui.ControlLabel(35, 130, 200, 40, "Xcalibur Downloader", 'special13')
                self.addControl(self.strMainTitle)

                # item Control List
                self.list = xbmcgui.ControlList(23, 166, 674 , 420,'font14','0xFF000000', buttonTexture = os.path.join(self.imagedir,"list-background.png"),buttonFocusTexture = os.path.join(self.imagedir,"list-focus.png"), imageWidth=40, imageHeight=32, itemTextXOffset=0, itemHeight=55)
                self.addControl(self.list)


                # Version and author(s):
                self.strVersion = xbmcgui.ControlLabel(500, 30, 350, 30, "Version " + version + " par " + author, 'font12')
                self.addControl(self.strVersion)

                # Get the list of items
                self.updateList()

                # Close the Loading Window 
                dialogUI.close()


            except Exception, e: 
                print "Window::__init__: Exception durant la connection FTP",e
                print "Impossible de se connecter au serveur FTP: %s"%self.host
                dialogError = xbmcgui.Dialog()
                dialogError.ok("Erreur", "Exception durant la connection FTP")

    def onAction(self, action):
        """
        Remonte l'arborescence et quitte le script
        """
        try:
            if action == ACTION_PREVIOUS_MENU:

                #sortie du script
                print('action recieved: previous')

                #on se deconnecte du serveur pour etre plus propre
                #self.ftp.quit()
                self.FTPCtrl.closeConnection()

                print "Fermeture de la Window principale"
                self.close()
        except:
            print ("error/onaction: " + str(sys.exc_info()[0]))
            traceback.print_exc()

    def onControl(self, control):
        try:
            if control == self.list:
                item = self.list.getSelectedPosition()
                source = self.curDirList[item]#on definit la source a telecharger
                dialog = xbmcgui.Dialog()
                self.cible = dialog.browse(0, "Choisissez le dossier d'installation d'Xcalibur","files")
                
                dialog = xbmcgui.DialogProgress()
                dialog.create("Telechargement en cours ...")
                self.FTPCtrl.download(source,self.cible)#on appel la classe Telechargement avec la source a telecharger
                dialog.close()


        except:
            print ("error/onControl: " + str(sys.exc_info()[0]))
            traceback.print_exc()
 
    def updateList(self):
        self.curDirList = self.ftp.nlst(self.remotepath)
        xbmcgui.lock()
        # Clear all ListItems in this control list 
        self.list.reset()
        for i in self.curDirList:
            lenpath = len(self.remotepath)
            item = i[lenpath:]
            self.list.addItem(item)
        xbmcgui.unlock()   
        self.setFocus(self.list)



########
#
# Main
#
########
 
print("===================================================================")
print("")
print("        Xcalibur Downloader " + version + " STARTS")
print("")
print("===================================================================")

w = MainWindow()
w.doModal()
 
del w 

