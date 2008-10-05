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
        #self.strVersion = xbmcgui.ControlLabel(370, 30, 350, 30, version, 'font12')
        #self.strVersion = xbmcgui.ControlLabel(690, 87, 350, 30, version, 'font10','0xFF000000', alignment=1)
        self.strVersion = xbmcgui.ControlLabel(621, 69, 350, 30, version, 'font10','0xFF000000', alignment=1)
        self.addControl(self.strVersion)

        self.updateList()
        
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
                self.close()

        except:
            print ("error/onaction: " + str(sys.exc_info()[0]))
            traceback.print_exc()

    def onControl(self, control):
        """
        Traitement si selection d'un element de la liste
        """
        try:
            if control == self.list:
                print('control == self.list')



        except:
            print ("error/onControl: " + str(sys.exc_info()[0]))
            traceback.print_exc()



    def updateList(self):
        """
        Mise a jour de la liste affichee
        """
        xbmcgui.lock()
        # Clear all ListItems in this control list
        self.list.reset()

        # Calcul du mobre d'elements de la liste
        itemnumber = 5

        # On utilise la fonction range pour faire l'iteration sur index
        for j in range(itemnumber):
            #print "j = %d"%j
            self.strMainTitle.setLabel(str(itemnumber) + " TITRE")
            imagePath = os.path.join(IMAGEDIR,"icone_theme.png")

            displayListItem = xbmcgui.ListItem(label = "Item "+ str(j), thumbnailImage = imagePath)
            self.list.addItem(displayListItem)
        xbmcgui.unlock()
        # Set Focus on list
        self.setFocus(self.list)


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

            #if not os.path.exists(os.path.join(IMAGEDIR,"noImageAvailable.jpg")):
            #    print "Error: " + os.path.join(IMAGEDIR,"noImageAvailable.jpg") + "n'existe pas!"
            #    return # TODO: Le fichier par defaut n'existe pas -> pb
        except Exception, e:
            print("Exception while creating folder " + folder)
            print(e)
            pass



########
#
# Main
#
########



def start():
    #Fonction de demarrage
    #passionFTPCtrl = ftpDownloadCtrl(host,user,password,remoteDirLst,localDirLst,downloadTypeLst)
    wid = xbmcgui.getCurrentWindowId()
    print "Current Windows ID = "
    print wid
    w = MainWindow()
    w.doModal()
    print "Delete Window"
    del w
    print "INSTALLEUR - Fin start"

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


##############################################################################
#                   Version et auteurs                                       #
##############################################################################
version  = config.get('Version','version')
author   = 'Seb & Temhil'
designer = 'Jahnrik'

##############################################################################
#                   Verification parametres locaux et serveur                #
##############################################################################

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
    start()
else:
    #ici on est en mode librairie importée depuis un programme
    pass
