from string import *
import sys#, os.path
import re
from time import gmtime, strptime, strftime
import os
import ftplib
import ConfigParser
import xbmcgui, xbmc
import traceback

try: Emulating = xbmcgui.Emulating
except: Emulating = False

version = 'Beta 1'
author  = 'Seb & Temhil'
designer = 'Jahnrik'

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
ACTION_STOP                         = 13
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
class scriptextracter:
    def zipfolder (self):
        import zipfile
        self.zfile = zipfile.ZipFile(self.archive, 'r')
        for i in self.zfile.namelist():  ## On parcourt l'ensemble des fichiers de l'archive
            print i
            if i.endswith('/'): #TODO : faire des tests sur plusieurs plateformes pour savoir si le '/' de fin depend de l'os sur lequel on est ou est constant
                dossier = self.pathdst + os.sep + i
                try:
                    os.makedirs(dossier)
                    print "dossier = ",dossier
                except Exception, e:
                    print "Erreur creation dossier de l'archive = ",e
            else:
                print "File Case"

    def  extract(self,archive,scriptDir):
        self.pathdst = scriptDir
        self.archive = archive
        if archive.endswith('zip'):
            self.zipfolder() #generation des dossiers dans le cas d'un zip

        print "Extraction de l'archive ", self.archive
        print "Dans le repertoire ",self.pathdst
        #extraction de l'archive
        try:
            xbmc.executebuiltin('XBMC.Extract(%s,%s)'%(self.archive,self.pathdst, ), )
            #os.remove(self.archive)
        except Exception, e:
            print "erreur lors de l'extraction"
            print e


class ftpDownloadCtrl:
    """

    Controleur de download via FTP
    Cette classe gere les download via FTP de fichiers et repertoire

    """
    def __init__(self,host,user,password,remotedirList,localdirList,typeList):
        """
        Fonction d'init de la classe ftpDownloadCtrl
        Initialise toutes les variables et lance la connection au serveur FTP
        """

        #Initialise les attributs de la classe ftpDownloadCtrl avec les parametres donnes au constructeur
        self.host               = host
        self.user               = user
        self.password           = password
        self.remotedirList      = remotedirList
        self.localdirList       = localdirList
        self.downloadTypeList   = typeList
        self.connected          = False # status de la connection (inutile pour le moment)
        self.curLocalDirRoot    = ""
        self.curRemoteDirRoot   = ""
        #self.idcancel           = False
        print "self.host = ",self.host
        print "self.user= ",self.user
        print "self.password = ",self.password

        #Connection au serveur FTP
        try:
            self.ftp = ftplib.FTP(self.host,self.user,self.password) # on se connecte
            self.ftp.cwd(self.remotedirList)# va au chemin specifie
            self.connected = True
        except Exception, e:
            print "ftpDownloadCtrl::__init__: Exception durant la connection FTP",e
            print "Impossible de se connecter au serveur FTP: %s"%self.host

    def download(self,pathsrc,rootdirsrc,typeIndex,progressbar_cb=None,dialogProgressWin=None):
        """
        Telecharge les elements a un chemin specifie (repertoires, sous repertoires et fichiers)
        a dans un repertorie local dependant du type de telechargement (theme, scraper, script ...)
        pathsrc     : chemin sur le serveur de l'element a telecharger
        rootdirsrc  : Repertoire root sur le server (correspondant a un type de downaload) - Exemple : "/.passionxbmc/Scraper/" pour les scrapers
        typeIndex   : Index correspondant au type de telechargement, permet notamment de definir le repertorie local de telechargement
        """

        self.curLocalDirRoot  = self.localdirList[typeIndex]
        self.curRemoteDirRoot = rootdirsrc

        print "download: self.curLocalDirRoot: %s"%self.curLocalDirRoot
        print "download: self.curRemoteDirRoot: %s"%self.curRemoteDirRoot

        try:
            if (progressbar_cb != None) and (dialogProgressWin != None):
                print "############(progressbar_cb != None) and (dialogProgressWin != None)##############"
                percent = 0
                print "=================================="
                print
                print "Pourcentage telecharger: %d"%percent
                print
                print "=================================="
                progressbar_cb(percent,dialogProgressWin)
        except Exception, e:
            print("downloadVideo - Exception ProgressBar UI callback for download")
            print(e)
            print progressbar_cb

        #on passe en parametre l'index correspondant au type
        status = self._download(pathsrc,progressbar_cb,dialogProgressWin,0,1)
        print "download Status: %d"%status
        return  status

    def _download(self, pathsrc,progressbar_cb=None,dialogProgressWin=None,curPercent=0,coeff=1):
        """
        Fonction privee (ne pouvant etre appelee que par la classe ftpDownloadCtrl elle meme)
        Telecharge un element sur le server FTP
        """

        # Liste le repertoire
        curDirList     = self.ftp.nlst(pathsrc) #TODO: ajouter try/except
        curDirListSize = len(curDirList) # Defini le nombre d'elements a telecharger correspondant a 100% - pour le moment on ne gere que ce niveau de granularite pour la progressbar



        print "_download: Contenu du repertoire %s :"%pathsrc
        print curDirList
        # On teste le nombre d'element dans la liste : si 0 -> rep vie
        # !!PB!!: la commande NLST dans le cas ou le path est un fichier retourne les details sur le fichier => donc liste non vide
        # donc pour le moment on essaira de telecharger en tant que fichier un rep vide (apres avoir fait un _downloaddossier)
        # mais ca ira ds une exception donc OK mais pas propre
        #TODO: a ameliorer donc
        print "_download: Nombre d'elements: %d"%curDirListSize
        #if len(curDirList) > 0:
        print "_download: Repertoire NON vide - demarrage boucle"
        for i in curDirList:
            #if (self.idcancel == True):
            if dialogProgressWin.iscanceled():
                print "Telechargement annulé"
                # Sortie de la boucle via return
                return -1 # -1 pour telechargement annule
            else:
                # Calcule le pourcentage
                #TODO: verifier que la formule pour le pourcentage est OK (la ca ette fait un peu trop rapidement)
                percent = min(curPercent + int((float(curDirList.index(i)+1)*100)/(curDirListSize * coeff)),100)
                print "=================================="
                print
                print "Pourcentage téléchargé: %d"%percent
                print
                print "=================================="

                try :
                    print "_download: dossier, i = ",i
                    self._downloaddossier(i,dialogProgressWin=dialogProgressWin,curPercent=percent,coeff=coeff*curDirListSize)
                    percent = int((float(curDirList.index(i)+1)*100)/(curDirListSize * coeff))

                except Exception, e:
                    print "_download: Exception _download",e
                    print "_download: fichier, i = ",i
                    try:
                        #Mise a jour de la fentetre de telechargement
                        #TODO: Solution temporaraire -> on veut afficher le nom du theme/script/skin en cours en plus du fichier
                        dialogProgressWin.update(percent,i)
                    except Exception, e:
                        print("downloadVideo - Exception calling UI callback for download")
                        print(e)
                        print progressbar_cb

                    self._downloadfichier(i)

        return 1 # 1 pour telechargement OK

    def _downloaddossier(self, dirsrc,progressbar_cb=None,dialogProgressWin=None,curPercent=0,coeff=1):
        """
        Fonction privee (ne pouvant etre appelee que par la classe ftpDownloadCtrl elle meme)
        Telecharge un repertoire sur le server FTP
        Note: fait un appel recursif sur _download
        """
        emptydir = False
        print "_downloaddossier STARTS"
        print "self.curLocalDirRoot: %s"%self.curLocalDirRoot
        print "self.curRemoteDirRoot: %s"%self.curRemoteDirRoot
        print "dirsrc: %s"%dirsrc
        print "ftp.cwd(dirsrc)"
        self.ftp.cwd(dirsrc) # c'est cette commande qui genere l'exception dans le cas d'un fichier
        print "l = ftp.nlst(i)"
        try:
            dirContent = self.ftp.nlst(dirsrc)
            print "_downloaddossier: Contenu du repertoire i: %s :"%dirsrc
            print dirContent
        except Exception, e:
            print "_downloaddossier: Exception ftp.nlst(i)",e
            print "_downloaddossier: repertoire VIDE"
            emptydir = True

        # Cree le chemin du repertorie local
        # Extrait le chemin relatif: soustrait au chemin remote le chemin de base: par exemple on veut retirer du chemin; /.passionxbmc/Themes
        remoteRelDirPath = dirsrc.replace(self.curRemoteDirRoot,'')
        print "_downloaddossier: Chemin remote relatif extrait: %s"%remoteRelDirPath
        # On remplace dans le chemin sur le serveur FTP les '/' par le separateur de l'OS sur lequel on est
        localRelDirPath = remoteRelDirPath.replace('/',os.sep)
        print "_downloaddossier: Chemin local RELATIF extrait: %s"%localRelDirPath

        # Cree le chemin local (ou on va sauver)
        localAbsDirPath = os.path.join(self.curLocalDirRoot, localRelDirPath)
        print "_downloaddossier: local = %s (ABSOLU)"%localAbsDirPath

        try:
            os.makedirs(localAbsDirPath)
            print "_downloaddossier: repertoire OK (repertoire cree)"
        except Exception, e:
            print "_downloaddossier: Exception dossier",e
            print "_downloaddossier: repertoire KO"
        if (emptydir == True):
            print "_downloaddossier: Repertoire %s VIDE"%dirsrc
        else:
            print "_downloaddossier: Repertoire %s NON vide"%dirsrc
            self._download(dirsrc,dialogProgressWin=dialogProgressWin,curPercent=curPercent,coeff=coeff)

    def _downloadfichier(self, filesrc):
        """
        Fonction privee (ne pouvant etre appelee que par la classe ftpDownloadCtrl elle meme)
        Telecharge un fichier sur le server FTP
        """
        print "_downloadfichier STARTS"
        print "_downloadfichier: self.curLocalDirRoot: %s"%self.curLocalDirRoot
        # Cree le chemin du repertorie local
        # Extrait le chemin relatif: soustrait au chemin remote le chemin de base: par exemple on veut retirer du chemin; /.passionxbmc/Themes
        remoteRelFilePath = filesrc.replace(self.curRemoteDirRoot,'')
        print "_downloadfichier: Chemin remote relatif extrait: %s"%remoteRelFilePath

        #Mise a jour de la fentetre de telechargement
        #TODO: Solution temporaraire -> bien crado de le faire entierment la
        #dialogProgressWin.update(0,line2=remoteRelFilePath)

        # On remplace dans le chemin sur le serveur FTP les '/' par le separateur de l'OS sur lequel on est
        localRelFilePath = remoteRelFilePath.replace('/',os.sep)
        print "_downloadfichier: Chemin local RELATIF extrait: %s"%localRelFilePath

        # Cree le chemin local (ou on va sauver)
        localAbsFilePath = os.path.join(self.curLocalDirRoot, localRelFilePath)
        print "_downloadfichier: Fichier local = %s (ABSOLU)"%localAbsFilePath

        try:
            # On ferme le fichier que l'on ouvre histoire d'etre plus clean (pas sur que ce soit vraiment indispensable, mais bon ...)
            localFile = open(localAbsFilePath, "wb")
            self.ftp.retrbinary('RETR ' + filesrc, localFile.write)
            localFile.close()
            print "_downloadfichier: fichier OK"
        except Exception, e:
            print e
            print "_downloadfichier: fichier KO"



class MainWindow(xbmcgui.Window):
    """

    Interface graphique

    """
    def __init__(self):
        """
        Initialisation de l'interface
        """
        if Emulating: xbmcgui.Window.__init__(self)
        if not Emulating:
            self.setCoordinateResolution(PAL_4x3) # Set coordinate resolution to PAL 4:3

        self.host               = host
        self.user               = user
        self.password           = password
        self.remotedirList      = remoteDirLst
        self.localdirList       = localDirLst
        self.downloadTypeList   = downloadTypeLst
        self.connected          = False # status de la connection (inutile pour le moment)
        self.racine             = RACINE
        self.index              = ""
        self.scraperDir         = scraperDir
        self.type               = "racine"
        self.numindex           = ""
        self.USRPath             = USRPath
        self.rightstest         = ""
        self.scriptDir          = scriptDir
        if self.USRPath == True:
           self.PMIIIDir           = PMIIIDir

        # Connection au serveur FTP
        try:
            self.ftp = ftplib.FTP(self.host,self.user,self.password) # on se connecte
            self.connected = True

            # Display Loading Window while we are loading the information from the website
            dialogUI = xbmcgui.DialogProgress()
            dialogUI.create("Nabbox", "Creation de l'interface Graphique", "Veuillez patienter...")

            # Background image
            print ("Get Background image from : " + os.path.join(IMAGEDIR,"background.png"))
            self.addControl(xbmcgui.ControlImage(0,0,720,576, os.path.join(IMAGEDIR,"background.png")))

            # Set List border image
            self.listborder = xbmcgui.ControlImage(19,120,681,446, os.path.join(IMAGEDIR, "list-border.png"))
            self.addControl(self.listborder)

            self.listborder.setVisible(True)
            # Set List background image
            self.listbackground = xbmcgui.ControlImage(20, 163, 679, 402, os.path.join(IMAGEDIR, "list-white.png"))
            self.addControl(self.listbackground)
            self.listbackground.setVisible(True)

            # Set List hearder image
            # print ("Get Logo image from : " + os.path.join(IMAGEDIR,"logo.gif"))
            self.header = xbmcgui.ControlImage(20,121,679,41, os.path.join(IMAGEDIR, "list-header.png"))
            self.addControl(self.header)
            self.header.setVisible(True)

            # Title of the current pages

            self.strMainTitle = xbmcgui.ControlLabel(35, 130, 200, 40, "passion-xbmc.org", 'special13')
            self.addControl(self.strMainTitle)

            # item Control List
            self.list = xbmcgui.ControlList(22, 166, 674 , 420,'font14','0xFF000000', buttonTexture = os.path.join(IMAGEDIR,"list-background.png"),buttonFocusTexture = os.path.join(IMAGEDIR,"list-focus.png"), imageWidth=40, imageHeight=32, itemTextXOffset=0, itemHeight=55)
            self.addControl(self.list)

            # Version and author(s):
            #self.strVersion = xbmcgui.ControlLabel(370, 30, 350, 30, version, 'font12')
            self.strVersion = xbmcgui.ControlLabel(690, 87, 350, 30, version, 'font10','0xFF000000', alignment=1)
            self.addControl(self.strVersion)

            # Get the list of items
            self.updateList()

            # Close the Loading Window
            dialogUI.close()

        except Exception, e:
            print "Window::__init__: Exception durant la connection FTP",e
            print "Impossible de se connecter au serveur FTP: %s"%self.host
            dialogError = xbmcgui.Dialog()
            dialogError.ok("Erreur", "Exception durant l'initialisation")
            print ("error/MainWindow __init__: " + str(sys.exc_info()[0]))
            traceback.print_exc()

    def onAction(self, action):
        """
        Remonte l'arborescence et quitte le script
        """
        try:
            if action == ACTION_PREVIOUS_MENU:
                #sortie du script
                print('action recieved: previous')
                self.close()
            if action == ACTION_PARENT_DIR:
                #remonte l'arborescence
                print ("Previous page requested")
                self.racine = True
                self.type   = "racine"
                self.updateList()
        except:
            print ("error/onaction: " + str(sys.exc_info()[0]))
            traceback.print_exc()

    def onControl(self, control):
        """
        Traitement si selection d'un element de la liste
        """
        try:
            if control == self.list:

                if (self.racine == True):

                    self.racine = False
                    self.index = self.list.getSelectedPosition()
                    self.type = self.downloadTypeList[self.list.getSelectedPosition()]
                    self.updateList()#on raffraichit la page pour afficher le contenu

                else:

                    downloadOK = True
                    self.index = self.list.getSelectedPosition()
                    print "type = ",self.type
                    source = self.curDirList[self.index]

                    if self.type == self.downloadTypeList[0]:   #Themes
                        # Verifions le themes en cours d'utilisation
                        mySkinInUse = xbmc.getSkinDir()
                        print "Skin en cours d'utilisation est : %s"%mySkinInUse
                        print "Skin a telechrger est : %s"%source
                        if mySkinInUse in source:
                            # Impossible de telecharger une skin en cours d'utlisation
                            dialog = xbmcgui.Dialog()
                            dialog.ok('Action impossible', "Vous ne pouvez écraser le Theme en cours d'utilisation", "Merci de changer le Theme en cours d'utilisation", "avant de le télécharger")
                            downloadOK = False
                        if 'Project Mayhem III' in source and self.USRPath == True:
                            self.linux_chmod(self.PMIIIDir)
                            if self.rightstest == True:
                               self.localdirList[0]= self.PMIIIDir
                               downloadOK = True
                               correctionPM3bidon = True
                            else:
                               dialog = xbmcgui.Dialog()
                               dialog.ok('Action impossible', "Vous ne pouvez installer ce theme sans les droits", "d'administrateur")
                               downloadOK = False


                    elif self.type == self.downloadTypeList[1] and self.USRPath == True:   #Linux Scrapers
                       self.linux_chmod(self.scraperDir)
                       print "linux scraper case"
                       if self.rightstest == True :
                          downloadOK = True
                       else:
                          dialog = xbmcgui.Dialog()
                          dialog.ok('Action impossible', "Vous ne pouvez installer le scraper sans les droits", "d'administrateur")
                          downloadOK = False


                    if downloadOK == True:
                        #fenetre de telechargement
                        dp = xbmcgui.DialogProgress()
                        lenbasepath = len(self.remotedirList[self.downloadTypeList.index(self.type)])
                        downloadItem = source[lenbasepath:]
                        dp.create("Téléchargement en cours ...", "%s %s en cours de téléchargement"%(self.type,downloadItem))
                        # Type est desormais reellement le type dee download, on utlise alros les liste pour recuperer le chemin que l'on doit toujours passer
                        #on appel la classe passionFTPCtrl avec la source a telecharger
                        self.passionFTPCtrl = ftpDownloadCtrl(self.host,self.user,self.password,self.remotedirList,self.localdirList,self.downloadTypeList)
                        downloadStatus = self.passionFTPCtrl.download(source, self.remotedirList[self.downloadTypeList.index(self.type)], self.numindex,progressbar_cb=self.updateProgress_cb,dialogProgressWin = dp)
                        dp.close()
                        print "downloadStatus %d"%downloadStatus

                        if self.type == self.downloadTypeList[2]:
                           #Appel de la classe d'extraction des archives scripts
                           remoteDirPath = self.remotedirList[self.downloadTypeList.index(self.type)]#chemin ou a ete telecharge le script
                           localDirPath = self.localdirList[self.downloadTypeList.index(self.type)]
                           archive = source.replace(remoteDirPath,localDirPath + os.sep)#remplacement du chemin de l'archive distante par le chemin local temporaire
                           scriptfinal0 = archive.replace(localDirPath,self.scriptDir)
                           if scriptfinal0.endswith('.zip'):
                                scriptfinal = scriptfinal0.replace('.zip','')
                           elif scriptfinal0.endswith('.rar'):
                                scriptfinal = scriptfinal0.replace('.rar','')
                           extracter = scriptextracter()
                           extracter.extract(archive,self.scriptDir)

                        if downloadStatus == -1:
                            # Telechargment annule par l'utilisateur
                            title    = "Téléchargement annulé"
                            message1 = "%s: %s"%(self.type,downloadItem)
                            message2 = "Téléchargement annulé alors qu'il etait en cours "
                            message3 = "Il se peut que des fichiers aient déjà été téléchargés"
                        else:
                            title    = "Téléchargement terminé"
                            message1 = "%s: %s"%(self.type,downloadItem)
                            message2 = "a été téléchargé dans le repertoire:"
                            if self.type == self.downloadTypeList[2]:

                                message3 = "%s"%scriptfinal
                            else:
                                message3 = "%s"%self.localdirList[self.downloadTypeList.index(self.type)]

                        dialogInfo = xbmcgui.Dialog()
                        dialogInfo.ok(title, message1, message2,message3)


                        if correctionPM3bidon == True:
                           self.localdirList[0] = themesDir
                           correctionPM3bidon = False


        except:
            print ("error/onControl: " + str(sys.exc_info()[0]))
            traceback.print_exc()

    def updateProgress_cb(self, percent, dp=None):
        """
        Met a jour la barre de progression
        """
        #TODO Dans le futur, veut t'on donenr la responsabilite a cette fonction le clacul du pouircentage????
        try:
            print percent
            dp.update(percent)
        except:
            percent = 100
            dp.update(percent)


    def updateList(self):
        """
        Mise a jour de la liste affichee
        """
        if (self.racine == True):
            #liste virtuelle des sections
            self.curDirList = self.remotedirList
        else:
            #liste physique d'une section sur le ftp
            self.curDirList = self.ftp.nlst(self.remotedirList[self.index])

        print "update list de : "
        print self.curDirList
        xbmcgui.lock()
        # Clear all ListItems in this control list
        self.list.reset()

        # On utilise la fonction range pour faire l'iteration sur index
        for j in range(len(self.curDirList)):
            #print "j = %d"%j
            ItemListPath = self.curDirList[j]
            #!!Q!!: est-ce que cela ne serait pas mieux d'utiliser une liste de string qui mappe plutot que de faire un filtre sur un path qui peut chmager dans le futur
            # Plutot que d'utiliser une valeur num, faire comem tu fais apres avec la commande len serait ideal, genre len(path) avec path=/.passionxbmc/
            #self.remoteroot = i[:14]
            if (self.racine == False):
                #affichage de l'interieur d'une section
                self.numindex = self.index
                lenindex = len(self.remotedirList[self.index]) # on a tjrs besoin de connaitre la taille du chemin de base pour le soustraire/retirer du chemin global plus tard

                # Met a jour le titre et les icones:
                if self.type == self.downloadTypeList[0]:   #Themes
                    self.strMainTitle.setLabel("Themes")
                    imagePath = os.path.join(IMAGEDIR,"icone_theme.png")
                elif self.type == self.downloadTypeList[1]: #Scrapers
                    self.strMainTitle.setLabel("Scrapers")
                    imagePath = os.path.join(IMAGEDIR,"icone_scrapper.png")
                elif self.type == self.downloadTypeList[2]: #Scripts
                    self.strMainTitle.setLabel("Scripts")
                    imagePath = os.path.join(IMAGEDIR,"icone_script.png")
                else:
                    # Image par defaut (ou aucune si = "")
                    imagePath = ""

                item2download = ItemListPath[lenindex:]

                displayListItem = xbmcgui.ListItem(label = item2download, thumbnailImage = imagePath)
                self.list.addItem(displayListItem)
            else:
                # Met a jour le titre:
                self.strMainTitle.setLabel("passion-xbmc.org")
                # Affichage de la liste des sections
                # -> On compare avec la liste affichee dans l'interface
                self.section = self.downloadTypeList[j]
                if self.section == self.downloadTypeList[0]:
                    imagePath = os.path.join(IMAGEDIR,"icone_theme.png")
                elif self.section == self.downloadTypeList[1]:
                    imagePath = os.path.join(IMAGEDIR,"icone_scrapper.png")
                elif self.section == self.downloadTypeList[2]:
                    imagePath = os.path.join(IMAGEDIR,"icone_script.png")
                else:
                    # Image par defaut (ou aucune si = "")
                    imagePath = ""
                print "ItemListPath = %s"%ItemListPath
                print "imagePath = %s"%imagePath
                #self.section = self.section0.replace("/","")
                #displayListItem = xbmcgui.ListItem(label = self.section, thumbnailImage = os.path.join(IMAGEDIR,"passionxbmc_scripts_right.png"))
                displayListItem = xbmcgui.ListItem(label = self.section, thumbnailImage = imagePath)
                self.list.addItem(displayListItem)
        xbmcgui.unlock()
        # Set Focus on list
        self.setFocus(self.list)

    def linux_chmod(self,path):
        print 'chemin a chmoder = ',path
        Wtest = os.access(path,os.W_OK)
        if Wtest == True:
            self.rightstest = True
            print "rightest OK"
        else:
            dialog = xbmcgui.Dialog()
            dialog.ok('Demande de mot de passe', "Vous devez saisir votre mot de passe administrateur", "systeme")
            keyboard = xbmc.Keyboard("","Mot de passe Administrateur", True)
            #keyboard = xbmc.Keyboard("")
            keyboard.doModal()
            if (keyboard.isConfirmed()):
                password = keyboard.getText()
                PassStr = "echo %s | "%password
                ChmodStr = "sudo -S chmod 777 -R %s"%path
                print "commande = ",PassStr + ChmodStr
                try:
                    os.system(PassStr + ChmodStr)
                    self.rightstest = True

                except Exception, e:
                    print "erreur CHMOD %s"%path
                    print e
                    self.rightstest = False
            else:
                self.rightstest = False


########
#
# Main
#
########

print("===================================================================")
print("")
print("        Passion XBMC Installeur " + version + " STARTS")
print("        Auteurs : "+ author)
print("        Graphic Design by : "+ designer)
print("")
print("===================================================================")

def start():
    #Fonction de demarrage
    passionFTPCtrl = ftpDownloadCtrl(host,user,password,remoteDirLst,localDirLst,downloadTypeLst)
    w = MainWindow()
    w.doModal()
    del w

ROOTDIR = os.getcwd().replace(';','')

##############################################################################
#                   Initialisation conf.cfg                                  #
##############################################################################
fichier = os.path.join(ROOTDIR, "conf.cfg")
config = ConfigParser.ConfigParser()
config.read(fichier)

##############################################################################
#                   Initialisation parametres locaux                         #
##############################################################################
IMAGEDIR = config.get('InstallPath','ImageDir')
CACHEDIR = config.get('InstallPath','CacheDir')
themesDir   = config.get('InstallPath','ThemesDir')
scriptDir   = config.get('InstallPath','ScriptsDir')
scraperDir  = config.get('InstallPath','ScraperDir')
TempscriptDir = config.get('InstallPath','TempscriptDir')
USRPath = config.getboolean('InstallPath','USRPath')
if USRPath == True:
    PMIIIDir = config.get('InstallPath','PMIIIDir')
RACINE = True

##############################################################################
#                   Initialisation parametres serveur                        #
##############################################################################
host = config.get('ServeurID','host')
user = config.get('ServeurID','user')
password = config.get('ServeurID','password')
downloadTypeLst = ["Themes","Scrapers","Scripts"]
remoteDirLst  = ["/.passionxbmc/Themes/","/.passionxbmc/Scraper/","/.passionxbmc/Scripts/"]
localDirLst   = [themesDir,scraperDir,TempscriptDir]

##############################################################################
#                   Verification parametres locaux et serveur                #
##############################################################################
print "FTP host: %s"%host
print "Chemin ou les themes seront telecharges: %s"%themesDir



