# -*- coding: cp1252 -*-
"""
Têtes à claques HTML parser with GUI by Temhil (temhil@gmail.com)
 
21-10-08 Version Beta2 par Temhil: 
  - Adpatation du script suite a une refonte complet du site
  - Ajout support Anglais/Francais
  - Ajout rubriques: Series/Pubs
  - Ajout téléchargement des photos en arriere plan 
   (l'utilisateur n'est plus bloqué au démarrage durant le téléchargement 
    des photos)
  - Suppression des fonctions de tri: plus supportées pour le moment du aux changements du site Web 
27-04-08 Version Beta1 par Temhil
  - Création du script permettant de visionner les videos du site:
    www.tetesaclaques.tv
  - Le support de settings est a venir
  - Attention les images son telerchargees dans le repertoire cache mais
    ne sont jamais effacées par le script (aussi à venir). Le bon coté, 
    c'est le le scriot sera plus rapide à charger! ;-)

Les droits des diffusions et des images utilisées sont exclusivement
réservés à Salambo productions inc (www.tetesaclaques.tv)
Si vous aimez les Têtes à claques, merci d'encourager leur createurs
en visitant leur site web et/ou en achetant le DVD
"""


############################################################################
version     = 'Beta2'
author      = 'Temhil'
############################################################################

############################################################################
# import  
############################################################################
from string import *
import sys, os.path
import traceback
import ConfigParser
import re
import urllib, urllib2, cookielib
from time import gmtime, strptime, strftime
try:
    import xbmcgui, xbmc
except ImportError:
    raise ImportError, 'This program requires the XBMC extensions for Python.'

############################################################################
# emulator
############################################################################
try: 
    Emulating = xbmcgui.Emulating
except: 
    Emulating = False


############################################################################
# Get current working directory and update internal vars with it  
############################################################################

# Set paths
#ROOTDIR = xbmc.translatePath(os.getcwd().replace( ";", "" )) # Create a path with valid format
ROOTDIR = os.getcwd().replace( ";", "" ) # Create a path with valid format

IMAGEDIR    = os.path.join(ROOTDIR, "images")
CACHEDIR    = os.path.join(ROOTDIR, "cache")
#DOWNLOADDIR = os.path.join(ROOTDIR, "download")
LIBDIR      = os.path.join(ROOTDIR, "lib")

# List of directories to check at startup
dirCheckList   = (CACHEDIR,) #Tuple - Singleton (Note Extra ,)

# Adding to sys PATH lib path
sys.path.append(LIBDIR)

# Import lib
from BeautifulSoup import BeautifulStoneSoup #librairie de traitement XML

############################################################################
#get actioncodes from keymap.xml
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
ACTION_MUSIC_PLAY                = 79
ACTION_CONTEXT_MENU              = 117

#############################################################################
# Player values
#############################################################################
PLAYER_AUTO         = 0 # xbmc.PLAYER_CORE_AUTO
PLAYER_DVDPLAYER    = 1 # xbmc.PLAYER_CORE_DVDPLAYER
PLAYER_MPLAYER      = 2 # xbmc.PLAYER_CORE_MPLAYER
PLAYER_PAPLAYER     = 3 # xbmc.PLAYER_CORE_PAPLAYER
PLAYER_MODPLAYER    = 4 # xbmc.PLAYER_CORE_MODPLAYER

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


#############################################################################
# URLs
#############################################################################

tacBasePageURL = "http://www.tetesaclaques.tv/"

collecAccueilPageRelURL  = "http://www.tetesaclaques.tv/modules/population.php"
collecDatesPageRelURL    = "http://www.tetesaclaques.tv/modules/population.php"
collecVotesPageRelURL    = "http://www.tetesaclaques.tv/modules/population.php"
collecExtrasPageRelURL   = "http://www.tetesaclaques.tv/modules/population.php"
collecPubPageRelURL      = "http://www.tetesaclaques.tv/modules/population.php"
collecSeriesPageRelURL   = "http://www.tetesaclaques.tv/modules/populationSeries.php"

# Selector list
tacNameSelectList           = ("COLLECTION", "SERIES", "EXTRAS", "PUBS")
tacUrlSelectList            = (collecDatesPageRelURL, collecSeriesPageRelURL, collecExtrasPageRelURL, collecPubPageRelURL)
tacCollecTypeSelectList     = ("collection","serie","extras","pub")
tacWebPageFileSelectList    = ["populationCollection.xml","populationSeries.xml","populationExtras.xml","populationPubs.xml"]


def downloadJPG(source, destination):
    """
    Source MyCine (thanks!)
    Download IF NECESSARY a URL 'source' (string) to a URL 'target' (string)
    Source is downloaded only if target doesn't already exist
    """
    if os.path.exists(destination):
        pass
    else:
        try:
            #print("downloadJPG destination doesn't exist, try to retrieve")
            loc = urllib.URLopener()
            loc.retrieve(source, destination)
        except Exception, e:
            print("Exception while source retrieving")
            print(e)
            print (str(sys.exc_info()[0]))
            traceback.print_exc()
            pass



class fileMgr:
    """
    
    File manager
    
    """
    #TODO: Create superclass, inherit and overwrite init
    def __init__(self,checkList):
        for i in range(len(checkList)):
            self.verifrep(checkList[i]) 

    def verifrep(self, folder):
        """
        Source MyCine (thanks!)
        Check a folder exists and make it if necessary
        """
        try:
            #print("verifrep check if directory: " + folder + " exists")
            if not os.path.exists(folder):
                print("verifrep Impossible to find the directory - trying to create the directory: " + folder)
                os.makedirs(folder)
        except Exception, e:
            print("Exception while creating folder " + folder)
            print(str(e))
            
    def listDirFiles(self, path):
        """
        List the files of a directory
        @param path:
        """
        dirList=os.listdir(path)
        return dirList
        
    def deleteFile(self, filename):
        """
        Delete a file form download directory
        @param filename:
        """
        os.remove(filename)
        
    def delFiles(self,folder):
        """
        From Joox
        Deletes all files in a given folder and sub-folders.
        Note that the sub-folders itself are not deleted.
        Parameters : folder=path to local folder
        """
        for root, dirs, files in os.walk(folder , topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
    
    def  extract(self,archive,targetDir):
        """
        Extract an archive in targetDir
        """
        xbmc.executebuiltin('XBMC.Extract(%s,%s)'%(archive,targetDir) )



class WebPage:
    """
    
    Load a remote Web page (html,xml) and provides source code using cookies
    
    """
    def __init__(self, baseURL,params,selection,classification='date',langue='fr-ca',pageNb='1',geolocation='fr',savehtml=True,filename="defaut.html",check_connexion=True):
        """
        Init of WebPage
        Load the Web page at the specific URL
        and copy the source code in self.Source        
        """
        try:
            # CookieJar objects support the iterator protocol for iterating over contained Cookie objects.
            h=urllib2.HTTPCookieProcessor(cookielib.CookieJar())
        
            request = urllib2.Request(baseURL,urllib.urlencode(params))
            request.add_header('Host', 'www.tetesaclaques.tv')
            request.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
            request.add_header('Accept','text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')
            request.add_header('Accept-Language','fr,fr-fr;en-us,en;q=0.5')
            request.add_header('Accept-Encoding','gzip,deflate')
            request.add_header('Accept-Charset','ISO-8859-1,utf-8;q=0.7,*;q=0.7')
            request.add_header('Keep-Alive','300')
            request.add_header('Connection','keep-alive')
            request.add_header('Cookie', 'GELOCATIONtac=%s; selection=%s; page=%s; classification=%s; fichier=video; LANGUEtac=%s'%(geolocation,selection,pageNb,classification,langue))
        
            
            cj = cookielib.CookieJar()
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
            urllib2.install_opener(opener)
            self.Source = opener.open(request).read()
            print("WebPage created for URL: " + baseURL)
            if savehtml == True:
                print "saving file at: %s"%(os.path.join(CACHEDIR, filename))
                open(os.path.join(CACHEDIR, filename),"w").write(self.Source)
        except Exception, e:
            print("Exception in WebPage init for URL: " + url)
            print(e)
            print (str(sys.exc_info()[0]))
            traceback.print_exc()
            
            # pass the Exception
            raise

class tacCollectionWebPage(WebPage):
    """
    
    Inherit from WebPage super class
    Load on tete a claque webiste a collection webpage
    (which include list of video to watch) and provides 
    source code (XML  format)    
    (which include video URL to watch) and provides source code
    
    """
    def __init__(self, baseURL,params,selection,classification='date',langue='fr-ca',pageNb='1',geolocation='fr',savehtml=True,filename="defaut.html",check_connexion=True):
        """
        - Init of WebPage
        - Load the Web page at the specific URL and copy the source code in self.Source
        """
        # Init super Class
        WebPage.__init__(self, baseURL,params,selection,classification,langue,pageNb,geolocation,savehtml,filename,check_connexion)

    def GetVideoList(self, dataObj):
        # Extract video File Name from the AC blog webpage
        soup = BeautifulStoneSoup(self.Source)
        #videosInfo=[]
        try:
            for miniature in soup.findAll("miniature"):
                #TODO: Check wajt can we do with a dixtionary instead of parallel lists
#                videosInfo.append( { 'productID' : miniature.idproduit,
#                                 'title': miniature.titre.string.encode("utf-8"),
#                                 'image_url': miniature.fichierminiature.string.encode("utf-8"),
#                                 'video_url': miniature.fichiervideo.string.encode("utf-8"),
#                                 'votes': miniature.votes,
#                                 'nbrvotes': miniature.nbrvotes
#                                 } )
            # Copy each item found in a list
                dataObj.titleList.append(miniature.titre.string.encode("cp1252"))
                dataObj.idList.append(miniature.idproduit)
                dataObj.videoFilenameList.append(miniature.fichiervideo.string.encode("utf-8"))
                dataObj.votesList.append(miniature.votes)
                dataObj.nbrvotesList.append(miniature.nbrvotes)
                imageURL = miniature.fichierminiature.string.encode("utf-8")
                if not imageURL.startswith('http'):
                    imageURL = tacBasePageURL + imageURL
                dataObj.imageFilenameList.append(imageURL)
        except Exception, e:
            print("tacCollectionWebPage: Exception during XMl parsing")
            print(str(e))
            print (str(sys.exc_info()[0]))
            traceback.print_exc()

        print "++++++++++++++++++++++++++++++++++++"
        print "tacCollectionWebPage - videosInfo:"    
        #print videosInfo
        print(dataObj.titleList)
        print(dataObj.idList)
        print(dataObj.imageFilenameList)
        print(dataObj.videoFilenameList)
        print(dataObj.imageFilenameList)
        print(dataObj.nbrvotesList)

    def GetNumberofPages(self):
        """
        Extract and return the number of web pages
        available for one tac collection
        """
        pageNb = 1 # In case we don't find the string pageNb would be 0
        
        print("Page Number =" + str(pageNb))
        print("----------------------")

        return pageNb
      
        ##TODO : Deal with the case of more than 1 page number found
    



class tacCollectionData:
    """
     Data Warehouse for datas extracted from collection
     web page(s) (one or more depending on number of pages)    
     """
    def __init__(self):
        """
        Init of tacCollectionData
        """
        self.dataLoaded        = False # define if data has been extracted from a collection webpage
        self.numberOfPages     = 0     # number of webpage for a collection
        self.idList            = []    # IDs of video in the collection webpage
        self.titleList         = []    # Title of a video    
        self.imageFilenameList = []    # File name for the image of a video
        self.videoFilenameList = []    # File name for a video
        self.votesList         = []    # votes
        self.nbrvotesList      = []    # nbrvotes
        
        print("tacCollectionData init DONE")

    def reset(self):
        """
        Reset of tacCollectionData attributes
        """
        self.dataLoaded        = False
        self.numberOfPages     = 0
        self.idList            = []
        self.titleList         = []
        self.imageFilenameList = []
        self.videoFilenameList = []
        self.votesList         = []
        self.nbrvotesList      = []
        print("tacCollectionData RESET DONE")
    
    def getNumberofItem(self):
        """
        Retrun the total number of item (videos) found for the collection
        """
        print("NumberofItem for = " + str(self.titleList))
        return len(self.titleList)

class SelectCollectionWebpage:
    """
    Allow to select a Collection Webpage to process (i.e by vote, by date ...)
    """

    def __init__(self, pagebaseUrl, nameSelecList, urlSelectList):
        """
        Initialization
        """
        self.selectedMenu               = int(0)
        self.baseUrl                    = pagebaseUrl
        self.selectionNameList          = nameSelecList
        self.selectionURLList           = urlSelectList
        self.selectionCollecTypeList    = tacCollecTypeSelectList
        self.selectionWebPageFileList   = tacWebPageFileSelectList
        self.selectCollecData           = []
        self.menulen                    = len(nameSelecList)
        self.language                   ='fr-ca'
        
        ##TODO: check len(nameSelecList) == len(urlSelectList)
        
        # Filling selectCollecData
        for i in range(self.menulen):
            self.selectCollecData.append(tacCollectionData())

        print("self.SelectCollectionWebpage created")

    def setLanguage(self, langue):
        """
        Set the language (proposed videos are differents in French and English)
        """
        self.language = langue
        # Reste dataloaded status
        for i in range(self.menulen):
            self.selectCollecData[i].dataLoaded = False

    def getLanguage(self):
        """
        get the current language (proposed videos are differents in French and English)
        """
        return self.language

class Window(xbmcgui.Window):
    """
    Tete a Claques Window UI
    """
    def __init__(self):
        """
        UI Initialization
        """
        if Emulating: xbmcgui.Window.__init__(self)
        if not Emulating:
            self.setCoordinateResolution(PAL_4x3) # Set coordinate resolution to PAL 4:3

        # Display Loading Window while we are loading the information from the website
        dialogUI = xbmcgui.DialogProgress()
        dialogUI.create("Têtes à claques", "Creation de l'interface Graphique", "Veuillez patienter...")

        # Create a file manager and check directory
        self.fileMgr = fileMgr(dirCheckList)
        
        # Background image
        self.addControl(xbmcgui.ControlImage(0,0,720,576, os.path.join(IMAGEDIR,"background.png")))
        
        # Set the TAC logo at top-left position
        self.user_logo_path_fr = os.path.join(IMAGEDIR,"logo-fr.png")
        self.user_logo_path_en = os.path.join(IMAGEDIR,"logo-en.png")
        self.user_logo = xbmcgui.ControlImage(20,25,235,144, self.user_logo_path_fr)
        self.addControl(self.user_logo)
        self.user_logo.setVisible(True)

        # Create selectCollectionWebpage instance in order to display choice of video collection
        self.CollectionSelector = SelectCollectionWebpage(tacBasePageURL, tacNameSelectList, tacUrlSelectList)
        print ("self.CollectionSelector.selectionNameList")
        print(self.CollectionSelector.selectionNameList)
        print ("self.CollectionSelector.selectionURLList")
        print(self.CollectionSelector.selectionURLList)
    
        # Add image in background behind list
        self.list_back = xbmcgui.ControlImage(270,60,420,500, os.path.join(IMAGEDIR,"texture.png"))
        self.addControl(self.list_back)
        self.list_back.setVisible(True)

        # Add image in background behind list
        self.list_back = xbmcgui.ControlImage(280,70,400,480, os.path.join(IMAGEDIR,"background.png"))
        self.addControl(self.list_back)
        self.list_back.setVisible(True)


        # Control List
        self.list = xbmcgui.ControlList(300, 100, 370, 470, imageWidth=143, space=5, itemHeight=80, font='font12', textColor='0xFFFFFF00',buttonFocusTexture  = os.path.join(IMAGEDIR,"texture.png"))

        # Number of Video in the list:
        self.strItemNb = xbmcgui.ControlLabel(600, 520, 150, 20, '0 Vidéo', 'font12', '0xFFFFFF00')

        # Version and author:
        self.strVersion = xbmcgui.ControlLabel(40, 520, 250, 30, "Version " + version + " par " + author, 'font12', '0xFFFFFF00')
        
        # Info for menu
        self.strAction = xbmcgui.ControlLabel(40, 200, 150, 20, 'SELECTIONNEZ:', 'font12', '0xFFFFFF00')
        
        # Title of list
        currentLanguage = self.CollectionSelector.getLanguage()
        if currentLanguage == 'fr-ca':
                currentLanguageLabel = 'Francais'
        elif currentLanguage == 'en':
                currentLanguageLabel = 'Anglais'
        self.strButton = xbmcgui.ControlLabel(380, 30, 200, 20, self.CollectionSelector.selectionNameList[self.CollectionSelector.selectedMenu] + ' - ' + currentLanguageLabel, 'font12', '0xFFFFFF00')
        
        self.addControl(self.list)      
        self.addControl(self.strItemNb)
        self.addControl(self.strVersion)
        self.addControl(self.strAction)
        self.addControl(self.strButton)
        
        # Buttons               
        self.button0 = xbmcgui.ControlButton(50, 240, 150, 30, self.CollectionSelector.selectionNameList[0],textColor='0xFFFFFF00', focusTexture = os.path.join(IMAGEDIR,"list-focus.png"),noFocusTexture = os.path.join(IMAGEDIR,"list-focus.png"))
        self.addControl(self.button0)
        self.button1 = xbmcgui.ControlButton(50, 280, 150, 30, self.CollectionSelector.selectionNameList[1],textColor='0xFFFFFF00', focusTexture = os.path.join(IMAGEDIR,"list-focus.png"),noFocusTexture = os.path.join(IMAGEDIR,"list-focus.png"))
        self.addControl(self.button1)
        self.button2 = xbmcgui.ControlButton(50, 320, 150, 30, self.CollectionSelector.selectionNameList[2],textColor='0xFFFFFF00', focusTexture = os.path.join(IMAGEDIR,"list-focus.png"),noFocusTexture = os.path.join(IMAGEDIR,"list-focus.png"))
        self.addControl(self.button2)
        self.button3 = xbmcgui.ControlButton(50, 360, 150, 30, self.CollectionSelector.selectionNameList[3],textColor='0xFFFFFF00', focusTexture = os.path.join(IMAGEDIR,"list-focus.png"),noFocusTexture = os.path.join(IMAGEDIR,"list-focus.png"))
        self.addControl(self.button3)
        self.butOptions = xbmcgui.ControlButton(50, 400, 150, 30, "ANGLAIS", textColor='0xFFFFFF00', focusTexture = os.path.join(IMAGEDIR,"list-focus.png"),noFocusTexture = os.path.join(IMAGEDIR,"list-focus.png"))
        self.addControl(self.butOptions)
#        self.butAPropos = xbmcgui.ControlButton(50, 440, 150, 30, "A propos",textColor='0xFF191970', focusTexture = os.path.join(IMAGEDIR,"background.png"),noFocusTexture = os.path.join(IMAGEDIR,"background.png"))
#        self.addControl(self.butAPropos)
        
        self.button0.controlDown(self.button1)
        self.button0.controlRight(self.list)
        self.button1.controlUp(self.button0)
        self.button1.controlDown(self.button2)
        self.button1.controlRight(self.list)
        self.button2.controlUp(self.button1)
        self.button2.controlRight(self.list)
        self.button2.controlDown(self.button3)
        self.button3.controlUp(self.button2)
        self.button3.controlRight(self.list)
        self.button3.controlDown(self.butOptions)
        self.butOptions.controlUp(self.button3)
        self.butOptions.controlRight(self.list)
        #self.butOptions.controlDown(self.butAPropos)
        #self.butAPropos.controlUp(self.butOptions)
        #self.butAPropos.controlRight(self.list)

        self.list.controlLeft(self.button0)

        # Set Focus on 1st button
        self.setFocus(self.button0)

        # Close the Loading Window 
        dialogUI.close()
           
        # Update the list of video 
        self.updateControlList(self.CollectionSelector.selectedMenu)

        # Start to diplay the window before doModal call
        self.show()
        
        # No UI is displayed, continue to get and display the picture (would be too long to wait if we were waiting doModla call)
        self.updateIcons(self.CollectionSelector.selectedMenu)
       

    def updateData(self, menuSelectIndex):
        """
        Update tacData objet for a specific index (menu) 
        """
        # Display Loading Window while we are loading the information from the website
        dialogLoading = xbmcgui.DialogProgress()
        dialogLoading.create("Têtes à claques", "Chargement des informations", "Veuillez patienter...")
        try:
            # Load XML webpage of Têtes à claques
            #i = 1
            print "Load XML webpage of Têtes à claques"
            params={}
            language = self.CollectionSelector.getLanguage()
            print "language = %s"%language
            
            myCollectionWebPage=tacCollectionWebPage(self.CollectionSelector.selectionURLList[menuSelectIndex], params, selection=self.CollectionSelector.selectionCollecTypeList[menuSelectIndex], langue=language, savehtml=True, filename=language+'_'+self.CollectionSelector.selectionWebPageFileList[menuSelectIndex])
    
            #barprogression = ((i*100)/pagemax)
            barprogression = 50
            dialogLoading.update(barprogression)
            
            print("myCollectionWebPage created for self.CollectionSelector.selectedMenu = " + str(menuSelectIndex) + " with URL: " + tacBasePageURL + self.CollectionSelector.selectionURLList[menuSelectIndex])
    
            # Get Webpage Page number for this collection on the 1st webpage
            #pagemax = myCollectionWebPage.GetNumberofPages()   
            #print("Total Number Webpage Page for this collection : " + str(pagemax))
            
            # Reset collection data 
            self.CollectionSelector.selectCollecData[menuSelectIndex].reset()
            
            # Extract data from myCollectionWebPage and copy the content in corresponding Collection Data Instance
            myCollectionWebPage.GetVideoList(self.CollectionSelector.selectCollecData[menuSelectIndex])
    
            #barprogression = ((i*100)/pagemax)
            barprogression = 100
            dialogLoading.update(barprogression)
    
#            i = i + 1
#                    
#            while i <= int(pagemax) :
#                # Load next webpage in the collection 
#                myCollectionWebPage=tacCollectionWebPage((tacBasePageURL + self.CollectionSelector.selectionURLList[menuSelectIndex] + str(i)),txdata,txheaders)
#                print("New myCollectionWebPage created : " + str(i) + " with URL: " + (tacBasePageURL + self.CollectionSelector.selectionURLList[menuSelectIndex] + str(i)))
#                
#                # Append data from myCollectionWebPage and copy the content in corresponding Collection Data Instance
#                myCollectionWebPage.GetVideoList(self.CollectionSelector.selectCollecData[menuSelectIndex])
#                
#                barprogression = ((i*100)/pagemax)
#                dialogLoading.update(barprogression)
#               
#                i = i + 1
                
            # Update dataLoaded flag
            self.CollectionSelector.selectCollecData[menuSelectIndex].dataLoaded = True
            # Close the Loading Window 
            dialogLoading.close()
        except Exception, e:
            print("Exception during list update")
            print(str(e))
            print (str(sys.exc_info()[0]))
            traceback.print_exc()
        
            # Close the Loading Window 
            dialogLoading.close()
            # pass the exception
 
            dialogError = xbmcgui.Dialog()
            dialogError.ok("Erreur", "Impossible de charger la page Têtes à claques.tv", "probleme de connection?", "un changement sur le site distant?")
            
    def updateControlList(self, menuSelectIndex):
        """
        Update ControlList objet 
        """
        # Create loading windows after updateData
        dialogimg = xbmcgui.DialogProgress()
        dialogimg.create("Têtes à claques", "Chargement des images", "Veuillez patienter...")
        
        print "Update ControlList objet with menuSelectIndex = %s"%menuSelectIndex
        
        # Check is data have already been loaded for this collection
        if (self.CollectionSelector.selectCollecData[menuSelectIndex].dataLoaded == False):
            # Never been updated before, go and get the data
            self.updateData(menuSelectIndex)
            
        dialogimg.update(50)

        numberOfPictures=self.CollectionSelector.selectCollecData[menuSelectIndex].getNumberofItem()
  
        language = self.CollectionSelector.getLanguage()
        if language == 'en':
            # English
            if numberOfPictures > 0:
                videoLabel = " Videos"
            else:
                videoLabel = " Video"
        else:
            # French
            if numberOfPictures > 0:
                videoLabel = " Vidéos"
            else:
                videoLabel = " Vidéo"
            
        self.strItemNb.setLabel(str(numberOfPictures) + videoLabel ) # Update number of video at the bottom of the page

        # Lock the UI in order to update the list
        xbmcgui.lock()    

        # Clear all ListItems in this control list 
        self.list.reset()
            
        # add a few items to the list
        for name in self.CollectionSelector.selectCollecData[menuSelectIndex].titleList:
            
            index = self.CollectionSelector.selectCollecData[menuSelectIndex].titleList.index(name)
                
            image2load = os.path.join(CACHEDIR, os.path.basename(self.CollectionSelector.selectCollecData[menuSelectIndex].imageFilenameList[index]))                        
            if not os.path.exists(image2load):
                # images not here use default
                image2load = os.path.join(IMAGEDIR,"noImageAvailable.jpg")
                    
            #print("Adding to the List picture: " + image2load)
            self.list.addItem(xbmcgui.ListItem(label = name, thumbnailImage = image2load))

        # Go back on 1st button (even if overwritten later)
        self.setFocus(self.button0)
                
        # Unlock the UI and close the popup
        xbmcgui.unlock()
        dialogimg.update(100)
        dialogimg.close()
            

    def updateIcons(self, menuSelectIndex):
        """
        Retrieve images and update list
        """
        # Now get the images:
        try:       
            for name in self.CollectionSelector.selectCollecData[menuSelectIndex].titleList:
                index = self.CollectionSelector.selectCollecData[menuSelectIndex].titleList.index(name)
                
                image2load = os.path.join(CACHEDIR, os.path.basename(self.CollectionSelector.selectCollecData[menuSelectIndex].imageFilenameList[index]))                        
                #print("Trying to load locally: " + image2load)
                image2download = self.CollectionSelector.selectCollecData[menuSelectIndex].imageFilenameList[index]
                image2save     = os.path.join(CACHEDIR,os.path.basename(self.CollectionSelector.selectCollecData[menuSelectIndex].imageFilenameList[index]))
                
                try:
                    downloadJPG(image2download, image2save)
                    
                except:
                    print("Exception on image downloading: " + image2download)

                # Display the picture
                if os.path.exists(image2save):
                    self.list.getListItem(index).setThumbnailImage(image2save)
        except Exception, e:
            print("Exception")
            print(e)
            print (str(sys.exc_info()[0]))
            traceback.print_exc()


    def onAction(self, action):
        if action == ACTION_PREVIOUS_MENU:
            print('action received: previous')
            self.close()
            
        if action == ACTION_SHOW_INFO:
            print("action received: show info")
            
        if action == ACTION_STOP:
            print("action received: stop")
            
        if action == ACTION_PAUSE:
            print('action received: pause')
            #dialog = xbmcgui.Dialog()
            #dialog.ok('action received','ACTION_PAUSE')
    
    def onControl(self, control):
        if control == self.button0:
            self.CollectionSelector.selectedMenu = 0
            currentLanguage = self.CollectionSelector.getLanguage()
            if currentLanguage == 'fr-ca':
                    currentLanguageLabel = 'Francais'
            elif currentLanguage == 'en':
                    currentLanguageLabel = 'English'
            self.strButton.setLabel(self.CollectionSelector.selectionNameList[0] + ' - ' + currentLanguageLabel)
            self.updateControlList(0)
            self.setFocus(self.button0)
            self.updateIcons(0)

        elif control == self.button1:
            self.CollectionSelector.selectedMenu = 1
            currentLanguage = self.CollectionSelector.getLanguage()
            if currentLanguage == 'fr-ca':
                    currentLanguageLabel = 'Francais'
            elif currentLanguage == 'en':
                    currentLanguageLabel = 'English'
            self.strButton.setLabel(self.CollectionSelector.selectionNameList[1] + ' - ' + currentLanguageLabel)
            self.updateControlList(1)
            self.setFocus(self.button1)
            self.updateIcons(1)
                        
        elif control == self.button2:
            self.CollectionSelector.selectedMenu = 2
            currentLanguage = self.CollectionSelector.getLanguage()
            if currentLanguage == 'fr-ca':
                    currentLanguageLabel = 'Francais'
            elif currentLanguage == 'en':
                    currentLanguageLabel = 'English'
            self.strButton.setLabel(self.CollectionSelector.selectionNameList[2] + ' - ' + currentLanguageLabel)
            self.updateControlList(2)
            self.setFocus(self.button2)
            self.updateIcons(2)

        elif control == self.button3:
            self.CollectionSelector.selectedMenu = 3
            currentLanguage = self.CollectionSelector.getLanguage()
            if currentLanguage == 'fr-ca':
                    currentLanguageLabel = 'Francais'
            elif currentLanguage == 'en':
                    currentLanguageLabel = 'English'
            self.strButton.setLabel(self.CollectionSelector.selectionNameList[3] + ' - ' + currentLanguageLabel)
            self.updateControlList(3)
            self.setFocus(self.button3)
            self.updateIcons(3)

        elif control == self.butOptions:
            currentLanguage = self.CollectionSelector.getLanguage()
            if currentLanguage == 'fr-ca':
                # Go to English
                self.CollectionSelector.setLanguage('en')
                currentLanguageLabel    = "English"
                buttonLanguageLabel     = "Francais"
                actionLabel             = "SELECT:"
                self.user_logo.setImage(self.user_logo_path_en)
            elif currentLanguage == 'en':
                # Go to French
                self.CollectionSelector.setLanguage('fr-ca')
                currentLanguageLabel    = "Francais"
                buttonLanguageLabel     = "English"
                actionLabel             = "SELECTIONNEZ:"
                self.user_logo.setImage(self.user_logo_path_fr)
            self.butOptions.setLabel(buttonLanguageLabel)
            self.strAction.setLabel(actionLabel)
            self.strButton.setLabel(self.CollectionSelector.selectionNameList[self.CollectionSelector.selectedMenu] + ' - ' + currentLanguageLabel)
            self.updateControlList(self.CollectionSelector.selectedMenu)
            self.setFocus(self.butOptions)
            self.updateIcons(self.CollectionSelector.selectedMenu)

        elif control == self.list:
            chosenIndex = self.list.getSelectedPosition()
            print("chosenIndex = " + str(chosenIndex))
                        
            # Get the URl of the video to play
            video2playURL = self.CollectionSelector.selectCollecData[self.CollectionSelector.selectedMenu].videoFilenameList[chosenIndex]
            
            print("video2playURL = " + video2playURL)
            
            # Play the selected video
            print("Play the selected video: " + video2playURL)
            xbmc.Player().play(video2playURL)



########
#
# Main
#
########

print("===================================================================")
print("")
print("              Têtes à claques HTML parser STARTS")
print("")
print("===================================================================")



# Print Path information
print("ROOTDIR" + ROOTDIR)
print("IMAGEDIR" + IMAGEDIR)
print("CACHEDIR" + CACHEDIR)


# Create main Window
tacgui = Window()

# Display this window until close() is called
tacgui.doModal()
del tacgui
    

