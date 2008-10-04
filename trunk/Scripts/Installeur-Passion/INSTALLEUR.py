from string import *
import sys#, os.path
import re
from time import gmtime, strptime, strftime
import os
import ftplib
import ConfigParser
import xbmcgui, xbmc
import traceback
import time
import urllib2
try:
    del sys.modules['BeautifulSoup']
except:
    pass 
from BeautifulSoup import BeautifulStoneSoup #librairie de traitement XML
import htmlentitydefs


try: Emulating = xbmcgui.Emulating
except: Emulating = False


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
class rssReader:
    """
    Class responsable de la recuperation du flux RSS et de l'extraction des infos RSS
    """
    def __init__(self,rssUrl):
        """
        Init de rssReader
        """
        self.rssURL = rssUrl
        self.rssPage = self.get_rss_page(self.rssURL)

    def get_rss_page(self,rssUrl):
        """
        télécharge et renvoi la page RSS
        """
        print "get_rss_page"
        try:
            #request = urllib2.Request("http://passion-xbmc.org/service-importation/?action=.xml;type=rss2;limit=1")
            request = urllib2.Request(rssUrl)
            request.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; fr; rv:1.9) Gecko/2008052906 Firefox/3.0')
            request.add_header('Accept','text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')
            request.add_header('Accept-Language','fr,fr-fr;q=0.8,en-us;q=0.5,en;q=0.3')
            request.add_header('Accept-Charset','ISO-8859-1,utf-8;q=0.7,*;q=0.7')
#            request.add_header('Keep-Alive','300')
#            request.add_header('Connection','keep-alive')
            response = urllib2.urlopen(request)
            the_page = response.read()
        except Exception, e:
            print("Exception get_rss_page")
            print(e)
            the_page = ""
        # return the RSS page
        return the_page

    def unescape(self,text):
        """
        credit : Fredrik Lundh
        found : http://effbot.org/zone/re-sub.htm#unescape-html"""
        def fixup(m):# m est un objet match
            text = m.group(0)#on récupère le texte correspondant au match
            if text[:2] == "&#":# dans le cas où le match ressemble à &#
                # character reference
                try:
                    if text[:3] == "&#x":#si plus précisément le texte ressemble à &#38;#x (donc notation hexa)
                        return unichr(int(text[3:-1], 16))#alors on retourne le unicode du caractère en base 16 ( hexa)
                    else:
                        return unichr(int(text[2:-1]))#sinon on retourne le unicode du caractère en base 10 (donc notation décimale)
                except ValueError: #si le caractère n'est pas unicode, on le passe simplement
                    pass
            else: #sinon c'est un caractère nommé (htmlentities)
                # named entity
                try:
                    text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])#on renvoi le unicode de la correspondance pour le caractère nommé
                except KeyError:
                    pass #si le caractère nommé n'est pas défini dans les htmlentities alors on passe
            return text # leave as is #dans tous les autres cas, le match n'était pas un caractère d'échapement html on le retourne tel quel
     
        #par un texte issu de la fonction fixup
        return re.sub("&#?\w+;", fixup,   text)    
    
    def GetRssInfo(self):
        """
        Recupere les information du FLux RSS de passion XBMC
        Merci a Alexsolex
        """
        print "GetRssInfo"
        soup = BeautifulStoneSoup(self.rssPage)
        print "titre du flux :"
        print "\t"+soup.find("title").string.encode('ASCII', 'xmlcharrefreplace')
        print "description du flux :"
        #maintitle = "\t"+soup.find("description").string.encode('ASCII', 'xmlcharrefreplace').replace("&#224;","à").replace("&#160;","  -  ") # Note: &#160;=&
        maintitle = soup.find("description").string.encode('ASCII', 'xmlcharrefreplace').replace("&#224;","à").replace("&#234;","ê").replace("&#232;","è").replace("&#233;","é").replace("&#160;","  ***  ") # Note: &#160;=&
        items = ""
        for item in soup.findAll("item"): #boucle si plusieurs items dans le rss
            print "Titre de l'Item :"
            #itemsTitle = "\t"+item.find("title").string.encode('ASCII', 'xmlcharrefreplace').replace("&#224;","à").replace("&#160;","  -  ") # Note: &#160;=&
            itemsTitle = item.find("title").string.encode('ASCII', 'xmlcharrefreplace').replace("&#224;","à").replace("&#234;","ê").replace("&#232;","è").replace("&#233;","é").replace("&#160;","  ***  ") # Note: &#160;=&
            print itemsTitle
            items = items + itemsTitle + ":  "
            #la ligne suivante supprime toutes les balises au sein de l'info "description"
            clean_desc = re.sub(r"<.*?>", r"", "".join(item.find("description").contents))
            #on imprime le texte sans les caract&#232;res d'&#233;chappements html
            print "description de l'item :"
            #itemDesc = "\t"+self.unescape(clean_desc).strip().encode('ASCII', 'xmlcharrefreplace').replace("&#224;","à").replace("&#160;","  -  ") # Note: &#160;=&
            itemDesc = self.unescape(clean_desc).strip().encode('ASCII', 'xmlcharrefreplace').replace("&#224;","à").replace("&#234;","ê").replace("&#232;","è").replace("&#233;","é").replace("&#160;","  ***  ") # Note: &#160;=&
            print itemDesc
            items = items + " " + itemDesc
        #TODO: Faire une convertion au bon format afin d'eviter l'affichage incorrecte de caracteres
        print "ITEMS:"
        print items
        return maintitle,items




class scriptextracter:
    """
    Extracteur de script, dezip ou derar une archive et l'efface

    """
    def zipfolder (self):
        import zipfile
        self.zfile = zipfile.ZipFile(self.archive, 'r')
        for i in self.zfile.namelist():  ## On parcourt l'ensemble des fichiers de l'archive
            print i
            if i.endswith('/'):
                dossier = self.pathdst + os.sep + i
                try:
                    os.makedirs(dossier)
                except Exception, e:
                    print "Erreur creation dossier de l'archive = ",e
            else:
                print "File Case"

        # On ferme l'archive
        self.zfile.close()

    def  extract(self,archive,TargetDir):
        self.pathdst = TargetDir
        self.archive = archive
        if archive.endswith('zip'):
            self.zipfolder() #generation des dossiers dans le cas d'un zip
        #extraction de l'archive
        xbmc.executebuiltin('XBMC.Extract(%s,%s)'%(self.archive,self.pathdst) )

        #On delete le cache a la sortie du script

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
            print "ftpDownloadCtrl: __init__: Exception durant la connection FTP",e
            print "ftpDownloadCtrl: Impossible de se connecter au serveur FTP: %s"%self.host
            pass

    def closeConnection(self):
        """
        Close FTP conenction
        """
        #on se deconnecte du serveur pour etre plus propre
        self.ftp.quit()

    def getDirList(self,remotedir):
        """
        Close FTP conenction
        """
        curDirList = self.ftp.nlst(remotedir)
        
        # Tri de la liste
        curDirList.sort(key=str.lower)
        return curDirList


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
        self.ftp.cwd(dirsrc) # c'est cette commande qui genere l'exception dans le cas d'un fichier
        try:
            dirContent = self.ftp.nlst(dirsrc)
            print dirContent
        except Exception, e:
            print "_downloaddossier: Exception ftp.nlst(i)",e
            print "_downloaddossier: repertoire VIDE"
            emptydir = True

        # Cree le chemin du repertorie local
        # Extrait le chemin relatif: soustrait au chemin remote le chemin de base: par exemple on veut retirer du chemin; /.passionxbmc/Themes
        remoteRelDirPath = dirsrc.replace(self.curRemoteDirRoot,'')

        # On remplace dans le chemin sur le serveur FTP les '/' par le separateur de l'OS sur lequel on est
        localRelDirPath = remoteRelDirPath.replace('/',os.sep)

        # Cree le chemin local (ou on va sauver)
        localAbsDirPath = os.path.join(self.curLocalDirRoot, localRelDirPath)

        try:
            os.makedirs(localAbsDirPath)
        except Exception, e:
            print "_downloaddossier: Exception dossier",e
            print "_downloaddossier: repertoire KO"
        if (emptydir == True):
            print "_downloaddossier: Repertoire %s VIDE"%dirsrc
        else:
            self._download(dirsrc,dialogProgressWin=dialogProgressWin,curPercent=curPercent,coeff=coeff)

    def _downloadfichier(self, filesrc):
        """
        Fonction privee (ne pouvant etre appelee que par la classe ftpDownloadCtrl elle meme)
        Telecharge un fichier sur le server FTP
        """
        # Cree le chemin du repertorie local
        # Extrait le chemin relatif: soustrait au chemin remote le chemin de base: par exemple on veut retirer du chemin; /.passionxbmc/Themes
        remoteRelFilePath = filesrc.replace(self.curRemoteDirRoot,'')

        # On remplace dans le chemin sur le serveur FTP les '/' par le separateur de l'OS sur lequel on est
        localRelFilePath = remoteRelFilePath.replace('/',os.sep)

        # Cree le chemin local (ou on va sauver)
        localAbsFilePath = os.path.join(self.curLocalDirRoot, localRelFilePath)

        try:
            # On ferme le fichier que l'on ouvre histoire d'etre plus clean (pas sur que ce soit vraiment indispensable, mais bon ...)
            localFile = open(localAbsFilePath, "wb")
            self.ftp.retrbinary('RETR ' + filesrc, localFile.write)
            localFile.close()
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

        #TODO: TOUTES ces varibales devraient etre passees en parametre du constructeur de la classe (__init__ si tu preferes)
        # On ne devraient pas utiliser de variables globale ou rarement en prog objet

        self.host               = host
        self.user               = user
        self.rssfeed            = rssfeed
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
        self.USRPath            = USRPath
        self.rightstest         = ""
        self.scriptDir          = scriptDir
        self.extracter          = scriptextracter() # On cree un instance d'extracter
        self.CacheDir           = CACHEDIR
        self.targetDir          = ""
        self.delCache           = ""
        self.scrollingSizeMax   = 480

        # Display Loading Window while we are loading the information from the website
        dialogUI = xbmcgui.DialogProgress()
        dialogUI.create("Installeur Passion XBMC", "Creation de l'interface Graphique", "Veuillez patienter...")

        # Verifie si les repertoires cache et imagedir existent et les cree s'il n'existent pas encore
        self.verifrep(CACHEDIR)
        self.verifrep(IMAGEDIR)

        #TODO: A nettoyer, ton PMIIIDir n'est pas defini pour XBOX sans le test si dessous
        if self.USRPath == True:
            self.PMIIIDir = PMIIIDir


        # Background image
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
        self.strMainTitle = xbmcgui.ControlLabel(35, 130, 200, 40, "Sélection", 'special13')
        self.addControl(self.strMainTitle)

        # item Control List
        self.list = xbmcgui.ControlList(22, 166, 674 , 420,'font14','0xFF000000', buttonTexture = os.path.join(IMAGEDIR,"list-background.png"),buttonFocusTexture = os.path.join(IMAGEDIR,"list-focus.png"), imageWidth=40, imageHeight=32, itemTextXOffset=0, itemHeight=55)
        self.addControl(self.list)

        # Version and author(s):
        self.strVersion = xbmcgui.ControlLabel(621, 69, 350, 30, version, 'font10','0xFF000000', alignment=1)
        self.addControl(self.strVersion)

        # Get RSS Feed
        try:
            #fluxRSS = get_rss_page()
            self.passionRssReader = rssReader(self.rssfeed)
            print "Flux RSS page:"
            print self.passionRssReader.rssPage
            print "Flux RSS infos:"
            maintitle,title = self.passionRssReader.GetRssInfo()

        except Exception, e:
            print "Window::__init__: Exception durant la recuperation du Flux RSS",e
            print ("error/MainWindow __init__: " + str(sys.exc_info()[0]))
            title = "Impossible de recuperer le flux RSS"
            self.scrollingSizeMax = 260 # On reduit la taille du scrolling text car le message d'erruer est plus court
            traceback.print_exc()

        # Scrolling message
        self.scrollingText = xbmcgui.ControlFadeLabel(20, 87, 680, 30, 'font12', '0xFFFFFFFF')
        self.addControl(self.scrollingText)
        scrollStripTextSize = len(title)
        # Afin d'avoir un message assez long pour defiler, on va ajouter des espaces afin d'atteindre la taille max de self.scrollingSizeMax
        print "scrollStripTextSize = %d"%scrollStripTextSize
        print "self.scrollingSizeMax = %d"%self.scrollingSizeMax
        scrollingLabel = title.rjust(self.scrollingSizeMax)
        print "scrollingLabel:"
        print scrollingLabel
        scrollingLabelSize = len(scrollingLabel)
        print "scrollingLabelSize = %d"%scrollingLabelSize
        self.scrollingText.addLabel(scrollingLabel)
        #self.scrollingText.setVisible(False)

        # Connection au serveur FTP
        try:
            self.passionFTPCtrl = ftpDownloadCtrl(self.host,self.user,self.password,self.remotedirList,self.localdirList,self.downloadTypeList)

            self.connected = True

            # Get the list of items
            self.updateList()

        except Exception, e:
            print "Window::__init__: Exception durant la connection FTP",e
            print "Impossible de se connecter au serveur FTP: %s"%self.host
            dialogError = xbmcgui.Dialog()
            dialogError.ok("Erreur", "Exception durant l'initialisation")
            print ("error/MainWindow __init__: " + str(sys.exc_info()[0]))
            traceback.print_exc()

        # Close the Loading Window
        dialogUI.close()

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
                self.passionFTPCtrl.closeConnection()

                #On vide le cache
                if self.delCache == True:
                    self.delFiles(CACHEDIR)

                #on ferme tout
                winId = xbmcgui.getCurrentWindowId()
                print "Current Main Windows ID = "
                print winId

                print "Fermeture de la Window principale"
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
                    self.updateList() #on raffraichit la page pour afficher le contenu

                else:

                    downloadOK = True
                    correctionPM3bidon = False
                    self.index = self.list.getSelectedPosition()
                    source = self.curDirList[self.index]

                    if self.type == self.downloadTypeList[0]:   #Themes
                        # Verifions le themes en cours d'utilisation
                        mySkinInUse = xbmc.getSkinDir()
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
                        if self.rightstest == True :
                            downloadOK = True
                        else:
                            dialog = xbmcgui.Dialog()
                            dialog.ok('Action impossible', "Vous ne pouvez installer le scraper sans les droits", "d'administrateur")
                            downloadOK = False

                    if source.endswith('zip') or source.endswith('rar'):
                        self.delCache = True
                        self.targetDir = self.localdirList[self.numindex]
                        self.localdirList[self.numindex]= self.CacheDir


                    if downloadOK == True:
                        #fenetre de telechargement
                        dp = xbmcgui.DialogProgress()
                        lenbasepath = len(self.remotedirList[self.downloadTypeList.index(self.type)])
                        downloadItem = source[lenbasepath:]
                        dp.create("Téléchargement en cours ...", "%s %s en cours de téléchargement"%(self.type,downloadItem))
                        # Type est desormais reellement le type dee download, on utlise alros les liste pour recuperer le chemin que l'on doit toujours passer
                        #on appel la classe passionFTPCtrl avec la source a telecharger
                        downloadStatus = self.passionFTPCtrl.download(source, self.remotedirList[self.downloadTypeList.index(self.type)], self.numindex,progressbar_cb=self.updateProgress_cb,dialogProgressWin = dp)
                        dp.close()
                        print "downloadStatus %d"%downloadStatus


                        #On se base sur l'extension pour determiner si on doit telecharger dans le cache.
                        #Un tour de passe passe est fait plus haut pour echanger les chemins de destination avec le cache, le chemin de destination
                        #est retabli ici 'il s'agit de targetDir'
                        if downloadItem.endswith('zip') or downloadItem.endswith('rar'):
                            #Appel de la classe d'extraction des archives
                            remoteDirPath = self.remotedirList[self.downloadTypeList.index(self.type)]#chemin ou a ete telecharge le script
                            localDirPath = self.localdirList[self.downloadTypeList.index(self.type)]
                            archive = source.replace(remoteDirPath,localDirPath + os.sep)#remplacement du chemin de l'archive distante par le chemin local temporaire
                            self.localdirList[self.numindex]= self.targetDir
                            fichierfinal0 = archive.replace(localDirPath,self.localdirList[self.numindex])
                            if fichierfinal0.endswith('.zip'):
                                fichierfinal = fichierfinal0.replace('.zip','')
                            elif fichierfinal0.endswith('.rar'):
                                fichierfinal = fichierfinal0.replace('.rar','')


                            # On n'a besoin d'ue d'un instance d'extracteur sinon on va avoir une memory leak ici car on ne le desalloue jamais
                            # Je l'ai donc creee dans l'init comem attribut de la classe
                            #extracter = scriptextracter()
                            self.extracter.extract(archive,self.localdirList[self.numindex])

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
                            message3 = "%s"%self.localdirList[self.downloadTypeList.index(self.type)]

                        dialogInfo = xbmcgui.Dialog()
                        dialogInfo.ok(title, message1, message2,message3)


                        #TODO: Attention correctionPM3bidon n'est pa defini dans le cas d'un scraper ou script
                        #      Je l;ai donc defini a False au debut
                        # On remet a la bonne valeur initiale self.localdirList[0]
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
            #self.curDirList = self.ftp.nlst(self.remotedirList[self.index])
            self.curDirList = self.passionFTPCtrl.getDirList(self.remotedirList[self.index])

        print self.curDirList
        xbmcgui.lock()
        # Clear all ListItems in this control list
        self.list.reset()

        # Calcul du mobre d'elements de la liste
        itemnumber = len(self.curDirList)

        # On utilise la fonction range pour faire l'iteration sur index
        for j in range(itemnumber):
            #print "j = %d"%j
            ItemListPath = self.curDirList[j]

            if (self.racine == False):
                #affichage de l'interieur d'une section
                self.numindex = self.index
                lenindex = len(self.remotedirList[self.index]) # on a tjrs besoin de connaitre la taille du chemin de base pour le soustraire/retirer du chemin global plus tard

                # Met a jour le titre et les icones:
                if self.type == self.downloadTypeList[0]:   #Themes
                    self.strMainTitle.setLabel(str(itemnumber) + " Themes")
                    imagePath = os.path.join(IMAGEDIR,"icone_theme.png")
                elif self.type == self.downloadTypeList[1]: #Scrapers
                    self.strMainTitle.setLabel(str(itemnumber) + " Scrapers")
                    imagePath = os.path.join(IMAGEDIR,"icone_scrapper.png")
                elif self.type == self.downloadTypeList[2]: #Scripts
                    self.strMainTitle.setLabel(str(itemnumber) + " Scripts")
                    imagePath = os.path.join(IMAGEDIR,"icone_script.png")
                else:
                    # Image par defaut (ou aucune si = "")
                    imagePath = ""

                item2download = ItemListPath[lenindex:]

                displayListItem = xbmcgui.ListItem(label = item2download, thumbnailImage = imagePath)
                self.list.addItem(displayListItem)
            else:
                # Met a jour le titre:
                self.strMainTitle.setLabel("Sélection")
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

                displayListItem = xbmcgui.ListItem(label = self.section, thumbnailImage = imagePath)
                self.list.addItem(displayListItem)
        xbmcgui.unlock()
        # Set Focus on list
        self.setFocus(self.list)

    ######################################################################
    # Function delFiles from Joox
    # Description: Deletes all files in a given folder and sub-folders.
    #              Note that the sub-folders itself are not deleted.
    # Parameters : folder=path to local folder
    # Return     : -
    ######################################################################
    #TODO move this function in a class
    def delFiles(self,folder):
        for root, dirs, files in os.walk(folder , topdown=False):
            for name in files:
                try:
                    os.remove(os.path.join(root, name))
                except Exception, e:
                    print e

    #########################################################################
    # Function verifrep (from myCine)
    # Description: Check a folder exists and make it if necessary
    #########################################################################
    def verifrep(self,folder):
        try:
            print("verifrep check if directory: " + folder + " exists")
            if not os.path.exists(folder):
                print("verifrep Impossible to find the directory - trying to create the directory: " + folder)
                os.makedirs(folder)

        except Exception, e:
            print("Exception while creating folder " + folder)
            print(e)
            pass

    def linux_chmod(self,path):
        """
        Effectue un chmod sur un repertoire pour ne plus etre bloque par les droits root sur plateforme linux
        """
        Wtest = os.access(path,os.W_OK)
        if Wtest == True:
            self.rightstest = True
            print "rightest OK"
        else:
            dialog = xbmcgui.Dialog()
            dialog.ok('Demande de mot de passe', "Vous devez saisir votre mot de passe administrateur", "systeme")
            keyboard = xbmc.Keyboard("","Mot de passe Administrateur", True)
            keyboard.doModal()
            if (keyboard.isConfirmed()):
                password = keyboard.getText()
                PassStr = "echo %s | "%password
                ChmodStr = "sudo -S chmod 777 -R %s"%path
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



def go():
    #Fonction de demarrage
    wid = xbmcgui.getCurrentWindowId()
    print "Current Windows ID = "
    print wid
    w = MainWindow()
    w.doModal()
    print "Delete Window"
    del w
    print "INSTALLEUR - Fin go"

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
USRPath = config.getboolean('InstallPath','USRPath')
if USRPath == True:
    PMIIIDir = config.get('InstallPath','PMIIIDir')
RACINE = True

##############################################################################
#                   Initialisation parametres serveur                        #
##############################################################################
host        = config.get('ServeurID','host')
user        = config.get('ServeurID','user')
rssfeed     = config.get('ServeurID','rssfeed')
password    = config.get('ServeurID','password')
downloadTypeLst = ["Themes","Scrapers","Scripts"]
remoteDirLst  = ["/.passionxbmc/Themes/","/.passionxbmc/Scraper/","/.passionxbmc/Scripts/"]
localDirLst   = [themesDir,scraperDir,scriptDir]

##############################################################################
#                   Version et auteurs                                       #
##############################################################################
version  = config.get('Version','version')
author   = 'Seb & Temhil'
designer = 'Jahnrik'

##############################################################################
#                   Verification parametres locaux et serveur                #
##############################################################################
print "FTP host: %s"%host
print "Chemin ou les themes seront telecharges: %s"%themesDir

print("===================================================================")
print("")
print("        Passion XBMC Installeur " + version + " STARTS")
print("        Auteurs : "+ author)
print("        Graphic Design by : "+ designer)
print("")
print("===================================================================")

if __name__ == "__main__":
    #ici on pourrait faire des action si le script était lancé en tant que programme
    print "demarrage du script INSTALLEUR.py en tant que programme"
    go()
else:
    #ici on est en mode librairie importée depuis un programme
    pass
