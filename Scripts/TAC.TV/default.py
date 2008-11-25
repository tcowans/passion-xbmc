# -*- coding: cp1252 -*-
"""
Têtes à claques HTML parser with GUI by Temhil (temhil@gmail.com)

Ce script permet de visionner les vidéos sur le site www.tetesaclaques.tv que je vous le recommande fortement. 
Attention rires en vue!
On y découvre chaque semaine un nouveau clip de quelques minutes qui vaut vraiment le détour.

21-11-08 Version 1.1-Dev07 par Temhil:
  - Correction bug ou aucune image s'affichait lorsque l'on n'a pas d'url d'images dans le XML
  - Passage a WindowXML 
 
14-11-08 Version 1.0 par Temhil:
  - Amelioration de l'interface
  - Multilangue completement supporté: sur changement de la langue, l'interface est mise a jour (texte + icones)
  - Ajout support des series avec possibilité de ne voir que les vidéos d'une série
  - Redesign de la recuperation des donnees, separation du modele et de la vue
  - Support passage Fr->En et En->Fr meme dans les serie
  - Creation d'une fenetre de demarrage pour selection langue la 1ere fois
  - Creation d'un menu 'options' permettant le choix du lecteur, l'effacement auto du cache et le choix de la langue au demarrage
  - Creation d'un menu 'A propos'
  - Prepration au passage a WindowXML (à venir)
  
21-10-08 Version Beta2 par Temhil: 
  - Adaptation du script suite a une refonte complet du site
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
  - Attention les images son téléchargées dans le repertoire cache mais
    ne sont jamais effacées par le script (aussi à venir). Le bon coté, 
    c'est que le script sera plus rapide à charger! ;-)

Les droits des diffusions et des images utilisées sont exclusivement
réservés à Salambo productions inc (www.tetesaclaques.tv)
Si vous aimez les Têtes à claques, merci d'encourager leur createurs
en visitant leur site web et/ou en achetant le DVD
"""


############################################################################
version     = '1.1-Dev07'
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

from resources.libs import language # Cutom language lib
from resources.libs.BeautifulSoup import BeautifulStoneSoup # XML parsing lib

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


#REPERTOIRE RACINE ( default.py )
CWD = os.getcwd().rstrip( ";" )

# Set paths
ROOTDIR = os.getcwd().replace( ";", "" ) # Create a path with valid format

IMAGEDIR    = os.path.join(ROOTDIR, "resources", "skins", "Default", "media")
CACHEDIR    = os.path.join(ROOTDIR, "cache")
#LIBDIR      = os.path.join(ROOTDIR, "resources", "lib")

# List of directories to check at startup
dirCheckList   = (CACHEDIR,) #Tuple - Singleton (Note Extra ,)

# Adding to sys PATH lib path
#sys.path.append(LIBDIR)

# Import lib
#from BeautifulSoup import BeautifulStoneSoup #librairie de traitement XML
#import language # Custom lnaguage lib

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

#lang = xbmc.Language( ROOTDIR, "french" )
#__language__ = lang.getLocalizedString
lang = language.Language()
#lang.setLanguage("english")
#lang.setLanguage("french")
__language__ = lang.getLanguageString


tacBasePageURL = "http://www.tetesaclaques.tv/"

collecAccueilPageRelURL  = "http://www.tetesaclaques.tv/modules/population.php"
collecDatesPageRelURL    = "http://www.tetesaclaques.tv/modules/population.php"
collecVotesPageRelURL    = "http://www.tetesaclaques.tv/modules/population.php"
collecExtrasPageRelURL   = "http://www.tetesaclaques.tv/modules/population.php"
collecPubPageRelURL      = "http://www.tetesaclaques.tv/modules/population.php"
collecSeriesPageRelURL   = "http://www.tetesaclaques.tv/modules/populationSeries.php"

# Selector list
tacNameSelectList           = (32306, 32307, 32308, 32309, 32307) # "COLLECTION", "SERIES", "EXTRAS", "PUBS"
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
        try:
            for root, dirs, files in os.walk(folder , topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
        except Exception, e:
            print "delFiles: __init__: While deleting file",e
            print ("error delFiles: " + str(sys.exc_info()[0]))
            traceback.print_exc()
    
    def  extract(self,archive,targetDir):
        """
        Extract an archive in targetDir
        """
        xbmc.executebuiltin('XBMC.Extract(%s,%s)'%(archive,targetDir) )


class configCtrl:
    """
    
    Controler of configuration
    
    """
    def __init__(self):
        """
        Load configuration file, check it, and correct it if necessary
        """
        self.is_conf_valid = True
        self.defaultPlayer = PLAYER_AUTO
        #self.language      = 'french'
        self.language      = ''
        self.delCache      = True
        try:
            # Create config parser
            self.config = ConfigParser.ConfigParser()
            
            # Read config from .cfg file
            # - Open config file
            self.config.read(os.path.join(ROOTDIR, "resources", "TAC.cfg"))
            
            # Check sections exist
            if (self.config.has_section("system") == False):
                self.config.add_section("system")
                self.is_conf_valid = False
            if (self.config.has_section("user") == False):
                self.config.add_section("user")
                self.is_conf_valid = False
                
            # - Read config from file and correct it if necessary
            if (self.config.has_option("system", "player") == False):
                self.config.set("system", "player", self.defaultPlayer)
                self.is_conf_valid = False
            else:
                self.defaultPlayer = int(self.config.get("system", "player"))
            if (self.config.has_option("system", "cleancache") == False):
                self.config.set("system", "cleancache", self.delCache)
                self.is_conf_valid = False
            else:
                self.delCache = self.config.getboolean("system", "cleancache")
            if (self.config.has_option("user", "language") == False):
                self.config.set("user", "language", self.language)
                self.is_conf_valid = False
            else:
                self.language = self.config.get("user", "language")
            if (self.is_conf_valid == False):
                # Update file
                print "CFG file format wasn't valid: correcting ..."
                cfgfile=open(os.path.join(ROOTDIR, "resources", "TAC.cfg"), 'w+')
                try:
                    self.config.write(cfgfile)
                    self.is_conf_valid = True
                except Exception, e:
                    print("Exception during setPassword")
                    print(str(e))
                    print (str(sys.exc_info()[0]))
                    traceback.print_exc()
                cfgfile.close()
        except Exception, e:
            print("Exception while loading configuration file " + "TAC.cfg")
            print(str(e))
        
    def setDefaultPlayer(self,playerType,save=True):
        """
        set DefaultPlayerparameter locally and in .cfg file
        """
        self.defaultPlayer = playerType
        
        # Set player parameter
        self.config.set("system", "player", playerType)
        
        if save:
            # Update file
            cfgfile=open(os.path.join(ROOTDIR, "resources", "TAC.cfg"), 'w+')
            try:
                self.config.write(cfgfile)
            except Exception, e:
                print("Exception during setDefaultPlayer")
                print(str(e))
                print (str(sys.exc_info()[0]))
                traceback.print_exc()
            cfgfile.close()
        
    def getDefaultPlayer(self):
        """
        return the player currently used
        """
        return self.defaultPlayer
        
    def setLanguage(self,language,save=True):
        """
        set language parameter locally and in .cfg file
        """
        self.language = language
        
        # Set player parameter
        self.config.set("user", "language", language)
        
        if save:
            # Update file
            cfgfile=open(os.path.join(ROOTDIR, "resources", "TAC.cfg"), 'w+')
            try:
                self.config.write(cfgfile)
            except Exception, e:
                print("Exception during setLanguage")
                print(str(e))
                print (str(sys.exc_info()[0]))
                traceback.print_exc()
            cfgfile.close()
        
    def getLanguage(self):
        """
        return the language currently used
        """
        return self.language

    def setCleanCache(self,cleanCacheStatus,save=True):
        """
        set clean cache status locally and in .cfg file
        @param cleanCacheStatus: clean cache status - define cache directory will be cleaned or not on exit
        """
        self.delCache = cleanCacheStatus
        
        # Set cachepages parameter
        self.config.set("system", "cleancache", self.delCache)

        if save:
            # Update file
            cfgfile=open(os.path.join(ROOTDIR, "resources", "TAC.cfg"), 'w+')
            try:
                self.config.write(cfgfile)
            except Exception, e:
                print("Exception during setCleanCache")
                print(str(e))
                print (str(sys.exc_info()[0]))
                traceback.print_exc()
            cfgfile.close()
        
    def getCleanCache(self):
        """
        return current clean cache status - define cache directory will be cleaned or not on exit
        """
        return self.delCache

    def saveConfFile(self):
        # Update file
        cfgfile=open(os.path.join(ROOTDIR, "resources", "TAC.cfg"), 'w+')
        try:
            self.config.write(cfgfile)
        except Exception, e:
            print("Exception during setCleanCache")
            print(str(e))
            print (str(sys.exc_info()[0]))
            traceback.print_exc()
        cfgfile.close()
        


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

class tacSeriesWebPage(WebPage):
    """
    
    Inherit from WebPage super class
    Load on tete a claque webiste a collection webpage for Series
    (which include list of video to watch but also series IDs) and provides 
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
            
    def GetSerieList(self, seriedataObj):
        # Extract names of Series from the TAC webpage
        soup = BeautifulStoneSoup(self.Source)
        try:
            for serie in soup.findAll("serie"):
                # Copy each item found in a list
                seriedataObj.titleList.append(serie.titreserie.string.encode("cp1252"))
                seriedataObj.idList.append(serie.idserie)
                imageURL = serie.imageserie.string.encode("utf-8")
                if not imageURL.startswith('http'):
                    imageURL = tacBasePageURL + imageURL
                seriedataObj.imageFilenameList.append(imageURL)
        except Exception, e:
            print("GetSerieList: Exception during XMl parsing")
            print(str(e))
            print (str(sys.exc_info()[0]))
            traceback.print_exc()
#        print "++++++++++++++++++++++++++++++++++++"
#        print "tacSeriesWebPage - videosInfo:"    
#        print(seriedataObj.titleList)
#        print(seriedataObj.idList)
#        print(seriedataObj.imageFilenameList)
#        print(seriedataObj.videoFilenameList)
#        print(seriedataObj.imageFilenameList)
#        print(seriedataObj.nbrvotesList)
        
    def GetSerieVideoList(self, idserie, dataObj, reverseList = True):
        soup = BeautifulStoneSoup(self.Source)
        try:
            for serie in soup.findAll("serie"):
                # Copy each item found in a list
                if serie.idserie == idserie:
                    for miniature in serie.clipserie.findAll("miniature"):
                        dataObj.titleList.append(miniature.titre.string.encode("cp1252"))
                        dataObj.idList.append(miniature.idproduit)
                        dataObj.videoFilenameList.append(miniature.fichiervideo.string.encode("utf-8"))
                        dataObj.votesList.append(miniature.votes)
                        dataObj.nbrvotesList.append(miniature.nbrvotes)
                        imageURL = miniature.fichierminiature.string.encode("utf-8")
                        if not imageURL.startswith('http'):
                            imageURL = tacBasePageURL + imageURL
                        dataObj.imageFilenameList.append(imageURL)
                    # We exit the loop since we foud the serie with our ID
                    break
            if (reverseList == True):
                # Reverse the list on order to be from oldest to newest video
                dataObj.titleList.reverse()
                dataObj.idList.reverse()
                dataObj.videoFilenameList.reverse()
                dataObj.votesList.reverse()
                dataObj.nbrvotesList.reverse()
                dataObj.imageFilenameList.reverse()
            
        except Exception, e:
            print("GetSerieVideoList: Exception during XMl parsing")
            print(str(e))
            print (str(sys.exc_info()[0]))
            traceback.print_exc()
#        print "++++++++++++++++++++++++++++++++++++"
#        print "GetSerieVideoList - videosInfo:"    
#        print(dataObj.titleList)
#        print(dataObj.idList)
#        print(dataObj.imageFilenameList)
#        print(dataObj.videoFilenameList)
#        print(dataObj.imageFilenameList)
#        print(dataObj.nbrvotesList)


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
        # Extract video File Name from the TAC webpage
        soup = BeautifulStoneSoup(self.Source)
        try:
            for miniature in soup.findAll("miniature"):
                #TODO: Check what can we do with a dixtionary instead of parallel lists
                
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
#        print "++++++++++++++++++++++++++++++++++++"
#        print "tacCollectionWebPage - videosInfo:"    
#        print(dataObj.titleList)
#        print(dataObj.idList)
#        print(dataObj.imageFilenameList)
#        print(dataObj.videoFilenameList)
#        print(dataObj.imageFilenameList)
#        print(dataObj.nbrvotesList)

    def GetNumberofPages(self):
        """
        Extract and return the number of web pages
        available for one tac collection
        """
        pageNb = 1 # In case we don't find the string pageNb would be 0
        
#        print("Page Number =" + str(pageNb))
#        print("----------------------")

        return pageNb
      
        ##TODO : Deal with the case of more than 1 page number found


class tacSerieData:
    """
    Data Warehouse for datas extracted from Serie
    XML page(s)
    Not currently used for future evolutions
    """
    #TODO: use this structure for series in the future 
    def __init__(self):
        """
        Init of tacSerieData
        """
        self.dataLoaded         = False # define if data has been extracted from a collection webpage
        self.numberOfPages      = 0     # number of webpage for a collection
        self.idSerieList        = []    # IDs of video in the collection webpage
        self.titleSerieList     = []    # Title of a video    
        self.imageSerieFileList = []    # File name for the image of a video
        self.timeSerieList      = []    # File name for a video

    def reset(self):
        """
        Reset of tacSerieData attributes
        """
        self.dataLoaded         = False
        self.numberOfPages      = 0
        self.idSerieList        = []
        self.titleSerieList     = []
        self.imageSerieFileList = []
        self.timeSerieList      = []
    
    def getNumberofItem(self):
        """
        Retrun the total number of item (series) found for the collection
        """
        return len(self.idSerieList)

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
    
    def getNumberofItem(self):
        """
        Retrun the total number of item (videos) found for the collection
        """
        return len(self.titleList)


class SelectCollectionWebpage:
    """
    Allow to select a Collection Webpage to process (i.e by vote, by date ...)
    """

    def __init__(self, pagebaseUrl, nameSelecList, urlSelectList,configManager):
        """
        Initialization
        """
        self.language                   ='fr-ca'
        self.isSerieActive              = False
        self.selectedMenu               = 0
        self.subcollecIdx               = -1
        
        self.baseUrl                    = pagebaseUrl
        self.selectionNameList          = nameSelecList
        self.selectionURLList           = urlSelectList
        self.selectionCollecTypeList    = tacCollecTypeSelectList
        self.selectionWebPageFileList   = tacWebPageFileSelectList
        self.configManager              = configManager
        self.selectCollecData           = []
        self.menulen                    = len(nameSelecList)
        
        ##TODO: check len(nameSelecList) == len(urlSelectList)
        
        # Filling selectCollecData
        for i in range(self.menulen):
            self.selectCollecData.append(tacCollectionData())
            
        # Create additionnal one for the content of serie
        #TODO: manage paralle list for video of serie???
        self.selectCollecData.append(tacCollectionData())

    def setCollectionLanguage(self, language):
        """
        Set the language (proposed videos are differents in French and English)
        """
        if language == "french":
            self.language = "fr-ca"
        elif language == "english":
            self.language = "en"
        else:
            print "setCollectionLanguage : Unsupported language : %s - defined french as default language"%language
            self.language = "fr-ca"
            
        # Reset dataloaded status
        for i in range(self.menulen):
            self.selectCollecData[i].dataLoaded = False
        print "New language = %s"%self.language

    def getCollectionLanguage(self):
        """
        get the current language (proposed videos are differents in French and English)
        """
        if self.language == "fr-ca":
            language = "french"
        elif self.language == "en":
            language = "english"
        else:
            print "getCollectionLanguage : Unsupported language : %s - None is returned"%self.language
            language = None
        return language
    
    def getSelectedMenu(self):
        return self.selectedMenu

    def updateSubCollectionData(self,listIdx,language,progressBar=None):
        self.selectedMenu = 4 # collection index for a sub colelction
        self.subcollecIdx = listIdx
        if language == "french":
            self.language = "fr-ca"
        elif language == "english":
            self.language = "en"
        else:
            print "updateSubCollectionData : Unsupported language : %s - defined french as default language"%language
            self.language = "fr-ca"
        
        print "updateSubCollectionData; Subserie case"
        
        barprogression = 0
        try:
            if (progressBar != None):
                progressBar.update(barprogression)
        except Exception, e:        
            print("updateSubCollectionData - Exception calling UI callback for download")
            print(str(e))
            print progressBar

        # Load XML webpage of Têtes à claques
#        print "updateSubCollectionData - Load XML webpage of Têtes à claques"
#        print "language = %s"%language
        params={}
        
        #TODO: utiliser le xml deja telecharger au lieu de le retelecharger
        myCollectionWebPage=tacSeriesWebPage(self.selectionURLList[1], params, selection=self.selectionCollecTypeList[1], langue=self.language, savehtml=True, filename=self.language +'_'+self.selectionWebPageFileList[1])

        barprogression = 50
        try:
            if (progressBar != None):
                progressBar.update(barprogression)
        except Exception, e:        
            print("getSubCollectionData - Exception calling UI callback for download")
            print(str(e))
            print progressBar
        
        #TODO: check if this line is not optionnal
        self.selectCollecData[self.selectedMenu].reset()
        
        # Extract data from myCollectionWebPage and copy the content in corresponding Collection Data Instance
        try:
            serieIdx = self.selectCollecData[1].idList[listIdx]
            myCollectionWebPage.GetSerieVideoList(serieIdx, self.selectCollecData[self.selectedMenu])
        except Exception, e:        
            print("getSubCollectionData - Subserie case : Impossible to get collection data for all the serie")
            print(str(e))
#        # Return the collection data
#        return self.selectCollecData[index]

    def updateCollectionData(self,index,language,progressBar=None):
        """
        Retourne the colelction data correpsonding to index and set it as current index
        """        
        # Set current selected menu
        self.selectedMenu = index
        
        if self.selectedMenu == 4:
            self.updateSubCollectionData(self.subcollecIdx,language,progressBar)
        else:
            # Standard case (not sub collection)
            if language == "french":
                self.language = "fr-ca"
            elif language == "english":
                self.language = "en"
            else:
                print "updateCollectionData : Unsupported language : %s - defined french as default language"%language
                self.language = "fr-ca"
            
            barprogression = 0
            try:
                if (progressBar != None):
                    progressBar.update(barprogression)
            except Exception, e:        
                print("getCollectionData - Exception calling UI callback for download")
                print(str(e))
                print progressBar
    
            if self.selectCollecData[index].dataLoaded == False:
                # First time we load thos data for this categorie
                    
                # Load XML webpage of Têtes à claques
#                print "Load XML webpage of Têtes à claques"
#                print "language = %s"%language
                params={}
        
                if self.selectedMenu == 1:
                    myCollectionWebPage=tacSeriesWebPage(self.selectionURLList[index], params, selection=self.selectionCollecTypeList[index], langue=self.language, savehtml=True, filename=self.language +'_'+self.selectionWebPageFileList[index])
                    
                else:
                    myCollectionWebPage=tacCollectionWebPage(self.selectionURLList[index], params, selection=self.selectionCollecTypeList[index], langue=self.language, savehtml=True, filename=self.language +'_'+self.selectionWebPageFileList[index])
        
                barprogression = 50
                try:
                    if (progressBar != None):
                        progressBar.update(barprogression)
                except Exception, e:        
                    print("getCollectionData - Exception calling UI callback for download")
                    print(str(e))
                    print progressBar
                
                # Reset collection data 
                #TODO: check is this line is not optionnal
                self.selectCollecData[index].reset()
                
                # Extract data from myCollectionWebPage and copy the content in corresponding Collection Data Instance
                try:            
                    if self.selectedMenu == 1:
                        myCollectionWebPage.GetSerieList(self.selectCollecData[index])
                    else:
                        myCollectionWebPage.GetVideoList(self.selectCollecData[index])
                        
                    # Update dataLoaded flag
                    self.selectCollecData[index].dataLoaded = True
                except Exception, e:        
                    print("updateCollectionData - standard case : Impossible to get collection data")
                    print(str(e))
            else:
                print "Data already loaded for this categorie: %d"%index
            
            barprogression = 100
            try:
                if (progressBar != None):
                    progressBar.update(barprogression)
            except Exception, e:        
                print("getCollectionData - Exception calling UI callback for download")
                print(str(e))
                print progressBar
        
#        # Return the collection data
#        return self.selectCollecData[index]
        
    def isSubCollec(self,listIdx):
        """
        Do action on an item selcted in a list
        - could be play
        - could be sublist
        """
        result = False
        if self.selectedMenu == 1: # Index 1 for serie
            # We are in serie case (list of serie is displayed to user)
            # -> we have to display list of video for the serie
            
            # Reset collection data for sub colelction (index 4) in case we already had one
            self.selectCollecData[4].reset()
            
            result = True
        else:
            # Get the URl of the video to play
            video2playURL = self.selectCollecData[self.selectedMenu].videoFilenameList[listIdx]
            
            # Play the selected video
            xbmc.Player(self.configManager.getDefaultPlayer()).play(video2playURL)
#            myPlayer = xbmc.Player(self.configManager.getDefaultPlayer())
#            print "setSubtitles"
#            myPlayer.setSubtitles(os.path.join(CACHEDIR, "1071.txt")) # Seems to be only for Linux
#            print "play"
#            myPlayer.play(video2playURL)
            
        return result 

class SettingsWindow(xbmcgui.WindowDialog):
    """
    
    This window display settings
    
    """
    def __init__(self):
        if Emulating: xbmcgui.Window.__init__(self)
        if not Emulating:
            self.setCoordinateResolution(PAL_4x3) # Set coordinate resolution to PAL 4:3

    def setWindow(self,configManager):
        self.configManager          = configManager
        self.strListMaxSize         = 50
        self.languageList           = ["french","english"] # Languages - strings used in conf file
        self.playerMenuList         = [ __language__(32501), __language__(32502),__language__(32503)] # "Auto","DVD Player","MPlayer"
        self.languageMenuList       = [__language__(32505),__language__(32506)] # "French","English"
        self.cleanCacheList         = [__language__(32508),__language__(32509)] # "Activated","Deactivated"
        self.cleanCacheActionList   = [__language__(32513),__language__(32514)]
        
        # Background image
        self.addControl(xbmcgui.ControlImage(100,100,445,335, os.path.join(IMAGEDIR,"dialog-panel.png")))

        # Title label:
        self.strlist = xbmcgui.ControlLabel(100, 105, 445, 30, __language__(32303), 'special13',alignment=6) # Options
        self.addControl(self.strlist)

        # Get settings and flag indicating on exit if they have been modified
        self.defaultPlayer  = (self.configManager.getDefaultPlayer(), False) 
        self.language       = (self.configManager.getLanguage(), False)
        self.cleanCache     = (self.configManager.getCleanCache(), False)
        
        
        # item Control List
        self.strDefaultPlayerTitle   = __language__(32500) # Player vidéo:
        self.strDefaultPlayerContent = self.playerMenuList[self.defaultPlayer[0]]
        self.strLanguageTitle    = __language__(32504) # Langue: 
        for lang in self.languageList:
            if str(self.language[0]) == lang:
                self.strLanguageContent  = self.languageMenuList[self.languageList.index(lang)]
                break
        self.strCleanCacheTitle      = __language__(32507) # "Nettoyage auto du cache: "
        if self.cleanCache[0]:
            self.strCleanCacheContent = self.cleanCacheList[0] #Activated
        else:
            self.strCleanCacheContent = self.cleanCacheList[1] #Deactiated
            
        self.settingsListData = [self.strDefaultPlayerTitle + self.strDefaultPlayerContent, self.strLanguageTitle + self.strLanguageContent, self.strCleanCacheTitle + self.strCleanCacheContent]
        self.settingsList = xbmcgui.ControlList(120, 150, 300 , 400,'font14', buttonTexture = os.path.join(IMAGEDIR,"list-black-nofocus.png"), buttonFocusTexture = os.path.join(IMAGEDIR,"list-black-focus.png"), itemTextXOffset=-10, itemHeight=30)
        self.addControl(self.settingsList)
            
        # OK button:
        self.buttonOK = xbmcgui.ControlButton(440, 150, 80, 30, "OK",font='font12', focusTexture = os.path.join(IMAGEDIR,"list-black-focus.png"), noFocusTexture  = os.path.join(IMAGEDIR,"list-black-nofocus.png"), alignment=6)
        self.addControl(self.buttonOK)
        
        self.settingsList.controlLeft(self.buttonOK)
        self.settingsList.controlRight(self.buttonOK)
        self.buttonOK.controlLeft(self.settingsList)
        self.buttonOK.controlRight(self.settingsList)

        for labelItem in self.settingsListData:
            displayListItem = (xbmcgui.ListItem(label = labelItem))
            # Add list item to the ControlList
            self.settingsList.addItem(displayListItem)
        self.setFocus(self.settingsList)
        
        # show this menu and wait until it's closed
        self.doModal()
        
    def onAction(self, action):
        if action == ACTION_PREVIOUS_MENU:
            #close the window
            self.close()
            
    def onControl(self, control):
        if control == self.settingsList:
            selectedIndex = self.settingsList.getSelectedPosition()
            if selectedIndex == 0:
                dialog = xbmcgui.Dialog()
                chosenIndex = dialog.select(__language__(32510), self.playerMenuList) # 'Selectionner le Player désiré'
                self.defaultPlayer           = (chosenIndex, True)
                self.strDefaultPlayerContent = self.playerMenuList[self.defaultPlayer[0]]
                self.settingsList.getListItem(selectedIndex).setLabel(self.strDefaultPlayerTitle + self.strDefaultPlayerContent)
            elif selectedIndex == 1:
                dialog = xbmcgui.Dialog()
                chosenIndex = dialog.select(__language__(32511), self.languageMenuList) #'Selectionner la langue désirée au démarrage'
                self.language           = (self.languageList[chosenIndex], True)
                self.strLanguageContent = self.languageMenuList[chosenIndex]
                self.settingsList.getListItem(selectedIndex).setLabel(self.strLanguageTitle + self.strLanguageContent)
                
            elif selectedIndex == 2:
                dialog = xbmcgui.Dialog()
                chosenIndex = dialog.select(__language__(32512), self.cleanCacheActionList) # 'Selectionner la gestion du cache désirée'
                if chosenIndex == 0:
                    self.cleanCache           = (True,True) # Change flag alos updated to True
                    self.strCleanCacheContent = self.cleanCacheList[0] #Activé
                else:
                    self.cleanCache           = (False,True)
                    self.strCleanCacheContent = self.cleanCacheList[1] #Désactivé
                    
                self.settingsList.getListItem(selectedIndex).setLabel(self.strCleanCacheTitle + self.strCleanCacheContent)
            else:
                print "SettingsWindow - onControl : Invalid control list index"

        elif control == self.buttonOK:
            # Saving modification and close
            
            # Check change flag on each property
            save = False
            if self.defaultPlayer[1]:
                self.configManager.setDefaultPlayer(self.defaultPlayer[0], False)
                save = True
            if self.language[1]:
                self.configManager.setLanguage(self.language[0], False)
                save = True
            if self.cleanCache[1]:
                self.configManager.setCleanCache(self.cleanCache[0], False)
                save = True
            if save == True:
                # Save conf file
                self.configManager.saveConfFile()
            # close current window
            self.close()

    
class AboutWindow(xbmcgui.WindowDialog):
    """
    
    About Window
    
    """
    def __init__(self):
        if Emulating: xbmcgui.Window.__init__(self)
        if not Emulating:
            self.setCoordinateResolution(PAL_4x3) # Set coordinate resolution to PAL 4:3

        self.addControl(xbmcgui.ControlImage(100,100,545,435, os.path.join(IMAGEDIR,"dialog-panel.png")))
        self.strTitle = xbmcgui.ControlLabel(130, 110, 350, 30, __language__( 32000 ),'special13') # Les Têtes à claques
        self.addControl(self.strTitle)
        self.strVersion = xbmcgui.ControlLabel(130, 140, 350, 30, __language__( 32800 ) + version) # Version
        self.addControl(self.strVersion)
        #self.strAuthor = xbmcgui.ControlLabel(130, 170, 350, 30, "Auteur: "+ author)
        self.strAuthor = xbmcgui.ControlLabel(130, 170, 350, 30, __language__( 32801 ) + author) # Auteur
        self.addControl(self.strAuthor)        
        #self.strDesTitle = xbmcgui.ControlLabel(130, 200, 350, 30, "Description: ")
        self.strDesTitle = xbmcgui.ControlLabel(130, 200, 350, 30, __language__( 32802 )) # Description:
        self.addControl(self.strDesTitle)        

        # Textbox
        self.desContentTextBox = xbmcgui.ControlTextBox(130, 225, 500, 200, font="font12", textColor='0xFFD3D3D3')
        self.addControl(self.desContentTextBox)
        self.desContentTextBox.setVisible(True)
        
        strContent = __language__( 32803 ) # Description
        self.desContentTextBox.setText(strContent)
        
        strCopyRight = __language__( 32804 ) # Copyrights
        self.strCopyRight = xbmcgui.ControlLabel(130, 465, 500, 20,strCopyRight, "font10",'0xFFFF0000')
        self.addControl(self.strCopyRight)
        
        self.doModal()
        
    def onAction(self, action):
        if action == ACTION_PREVIOUS_MENU:
            #close the window
            self.close()

class FirstStartWindow(xbmcgui.Window):
    def __init__(self):
        if Emulating: xbmcgui.Window.__init__(self)
        if not Emulating:
            self.setCoordinateResolution(PAL_4x3) # Set coordinate resolution to PAL 4:3

        self.__loc_language__ = xbmc.Language( ROOTDIR, "french" ).getLocalizedString
            
        self.language = None
        
        # Background image
        self.addControl(xbmcgui.ControlImage(0,0,720,576, os.path.join(IMAGEDIR,"background.png")))
        
        # Add central image 
        self.logo = xbmcgui.ControlImage(65,138,590,299, os.path.join(IMAGEDIR,"startupLogo.png"))
        self.addControl(self.logo)
        
        self.buttonEn = xbmcgui.ControlButton(80, 300, 150, 30, "ENGLISH", textColor='0xFFFFFFFF',shadowColor = '0xFF696969',focusedColor='0xFFFFFF00', focusTexture = os.path.join(IMAGEDIR,"list-focus.png"),noFocusTexture = os.path.join(IMAGEDIR,"list-focus.png"),alignment=6)
        self.addControl(self.buttonEn)

        self.buttonFr = xbmcgui.ControlButton(490, 300, 150, 30, "FRANCAIS", textColor='0xFFFFFFFF',shadowColor = '0xFF696969',focusedColor='0xFFFFFF00', focusTexture = os.path.join(IMAGEDIR,"list-focus.png"),noFocusTexture = os.path.join(IMAGEDIR,"list-focus.png"),alignment=6)
        self.addControl(self.buttonFr)

        self.buttonEn.controlRight(self.buttonFr)
        self.buttonFr.controlLeft(self.buttonEn)
        
        # Set Focus on 1st button
        self.setFocus(self.buttonEn)

    def getLanguage(self,configManager):
        """
        Get the language chosen by the user
        """
        self.configManager = configManager
        
        # show this menu and wait until it's closed
        self.doModal()
        
        return self.language
    
    def onControl(self, control):
        if control == self.buttonEn:
            self.configManager.setLanguage('english')
            self.language = 'english'
            xbmc.sleep( 100 )
            self.close()
        if control == self.buttonFr:
            self.configManager.setLanguage('french')
            self.language = 'french'
            xbmc.sleep( 100 )
            self.close()
            
    def onAction(self, action):
        if action == ACTION_PREVIOUS_MENU:
            dialogError = xbmcgui.Dialog()
            #dialogError.ok("Error", "You need to select a language the fisrt time", "in order to use this script", "You will be able to change it later on if necessary")
            dialogError.ok(self.__loc_language__(32111),self.__loc_language__(32116), self.__loc_language__(32117), self.__loc_language__(32118))

            #close the window
            self.close()


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
        
        

        # Check conf file
        self.configManager = configCtrl()
        
        if (self.configManager.getLanguage() == 'french'):
            lang.setLanguage("french")
        else:
            lang.setLanguage("english")
            
        dialogUI.create(__language__( 32000 ), __language__( 32100 ),__language__( 32110 ) ) # "Têtes à claques", "Creation de l'interface Graphique", "Veuillez patienter..."

        # Create a file manager and check directory
        self.fileMgr = fileMgr(dirCheckList)
        
        # User logo paths
        logoImage = os.path.join(IMAGEDIR,__language__( 32900 )) # "logo-fr.png" or "logo-en.png"
            
        # Menu labels
        optionLabel             = __language__(32303) # Options
        buttonlanguageLabel     = __language__(32301) # English
        aboutLabel              = __language__(32304) # A propos
        currentLanguageLabel    = __language__(32300) # Francais
        menuInfoLabel           = __language__(32302) # SELECTIONNEZ:

        # Background image
        self.addControl(xbmcgui.ControlImage(0,0,720,576, os.path.join(IMAGEDIR,"background.png")))
        
        # Set the TAC logo at top-left position
        self.user_logo = xbmcgui.ControlImage(20,25,235,144, logoImage)
        self.addControl(self.user_logo)
        self.user_logo.setVisible(True)

        # Create selectCollectionWebpage instance in order to display choice of video collection
        self.CollectionSelector = SelectCollectionWebpage(tacBasePageURL, tacNameSelectList, tacUrlSelectList,self.configManager)
        print ("self.CollectionSelector.selectionNameList")
        print(self.CollectionSelector.selectionNameList)
        print ("self.CollectionSelector.selectionURLList")
        print(self.CollectionSelector.selectionURLList)
        
        # Update language variable at startup
        self.CollectionSelector.setCollectionLanguage(self.configManager.getLanguage())
    
        # Add image in background behind main list
        self.list_back = xbmcgui.ControlImage(285,70,400,480, os.path.join(IMAGEDIR,"BackList.png"))
        self.addControl(self.list_back)
        self.list_back.setVisible(True)

        # Control List
        self.list = xbmcgui.ControlList(300, 100, 370, 470, imageWidth=143, space=5, itemHeight=80, font='font12', textColor='0xFFFFFF00',buttonTexture = os.path.join(IMAGEDIR,"blueButton.png"),buttonFocusTexture  = os.path.join(IMAGEDIR,"blueButtonFocus.png"))
        self.addControl(self.list)      

        # Number of Video in the list:
        self.strItemNb = xbmcgui.ControlLabel(680, 525, 120, 20, '0 ' + __language__(32305), 'font12', '0xFFFFFF00',alignment=1) # Videos + align right of 680 pos
        self.addControl(self.strItemNb)

        # Version:
        self.strVersion = xbmcgui.ControlLabel(255,45,120,20, "[B]%s%s[/B]"%(__language__(32312),version), 'font101', textColor='0xFFFFFF00',alignment=1) # Version
        self.addControl(self.strVersion)
        
        # Title image background
        self.list_back = xbmcgui.ControlImage(285,20,400,40, os.path.join(IMAGEDIR,"TitleBg.png"))
        self.addControl(self.list_back)
        self.list_back.setVisible(True)

        # Title of list
        self.strButton = xbmcgui.ControlLabel(285, 30, 400, 20, "[B]%s[/B]"%__language__(self.CollectionSelector.selectionNameList[self.CollectionSelector.getSelectedMenu()]) + "[COLOR=0xFFFFFFFF] - %s[/COLOR]"%currentLanguageLabel, 'special13', textColor='0xFFFFFF00',alignment=6)
        self.addControl(self.strButton)
        
        # Menu image background
        # Top
        self.menu_back_top = xbmcgui.ControlImage(70,200,150,170, os.path.join(IMAGEDIR,"menuBackTop.png"))
        self.addControl(self.menu_back_top)
        self.menu_back_top.setVisible(True)
        # Bottom
        self.menu_back_bottom = xbmcgui.ControlImage(70,410,150,140, os.path.join(IMAGEDIR,"menuBackBottom.png"))
        self.addControl(self.menu_back_bottom)
        self.menu_back_bottom.setVisible(True)
        
        # Menu Buttons
        # -> Navigations             
        self.button0 = xbmcgui.ControlButton(100, 210, 150, 30, __language__(self.CollectionSelector.selectionNameList[0]), textColor='0xFFFFFFFF',focusedColor='0xFFFFFF00', focusTexture = os.path.join(IMAGEDIR,"list-focus.png"),noFocusTexture = os.path.join(IMAGEDIR,"list-focus.png"))
        self.addControl(self.button0)
        self.button1 = xbmcgui.ControlButton(100, 250, 150, 30, __language__(self.CollectionSelector.selectionNameList[1]), textColor='0xFFFFFFFF',focusedColor='0xFFFFFF00', focusTexture = os.path.join(IMAGEDIR,"list-focus.png"),noFocusTexture = os.path.join(IMAGEDIR,"list-focus.png"))
        self.addControl(self.button1)
        self.button2 = xbmcgui.ControlButton(100, 290, 150, 30, __language__(self.CollectionSelector.selectionNameList[2]), textColor='0xFFFFFFFF',focusedColor='0xFFFFFF00', focusTexture = os.path.join(IMAGEDIR,"list-focus.png"),noFocusTexture = os.path.join(IMAGEDIR,"list-focus.png"))
        self.addControl(self.button2)
        self.button3 = xbmcgui.ControlButton(100, 330, 150, 30, __language__(self.CollectionSelector.selectionNameList[3]), textColor='0xFFFFFFFF',focusedColor='0xFFFFFF00', focusTexture = os.path.join(IMAGEDIR,"list-focus.png"),noFocusTexture = os.path.join(IMAGEDIR,"list-focus.png"))
        self.addControl(self.button3)

        # -> Others             
        self.butLanguage = xbmcgui.ControlButton(100, 425, 150, 30, buttonlanguageLabel, textColor='0xFFFFFFFF',focusedColor='0xFFFFFF00', focusTexture = os.path.join(IMAGEDIR,"list-focus.png"),noFocusTexture = os.path.join(IMAGEDIR,"list-focus.png"))
        self.addControl(self.butLanguage)
        self.butOptions = xbmcgui.ControlButton(100, 465, 150, 30, optionLabel, textColor='0xFFFFFFFF',focusedColor='0xFFFFFF00', focusTexture = os.path.join(IMAGEDIR,"list-focus.png"),noFocusTexture = os.path.join(IMAGEDIR,"list-focus.png"))
        self.addControl(self.butOptions)
        self.butAPropos = xbmcgui.ControlButton(100, 505, 150, 30, aboutLabel,textColor='0xFFFFFFFF',focusedColor='0xFFFFFF00', focusTexture = os.path.join(IMAGEDIR,"list-focus.png"),noFocusTexture = os.path.join(IMAGEDIR,"list-focus.png"))
        self.addControl(self.butAPropos)
        
        # Navigation
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
        self.button3.controlDown(self.butLanguage)
        self.butLanguage.controlUp(self.button3)
        self.butLanguage.controlRight(self.list)
        self.butLanguage.controlDown(self.butOptions)
        self.butOptions.controlUp(self.butLanguage)
        self.butOptions.controlRight(self.list)
        self.butOptions.controlDown(self.butAPropos)
        self.butAPropos.controlUp(self.butOptions)
        self.butAPropos.controlRight(self.list)
        self.list.controlLeft(self.button0)

        # Set Focus on 1st button
        self.setFocus(self.button0)

        # Close the Loading Window 
        dialogUI.close()
           
        # Update the list of video 
        self.updateDataOnMenu(self.CollectionSelector.getSelectedMenu())
        self.updateControlListFromData()

        # Start to diplay the window before doModal call
        self.show()
        
        # No UI is displayed, continue to get and display the picture (would be too long to wait if we were waiting doModla call)
        self.updateIcons()
       
    def updateDataOnList(self, listItemIndex):
        """
        Update tacData objet for a specific index in the main list
        """
        # Display Loading Window while we are loading the information from the website
        dialogLoading = xbmcgui.DialogProgress()
        dialogLoading.create(__language__( 32000 ), __language__( 32102 ),__language__( 32110 ) ) # "Têtes à claques", "Chargement des informations", "Veuillez patienter..."
        
        try:
            curLanguage = self.CollectionSelector.getCollectionLanguage()
            self.CollectionSelector.updateSubCollectionData(listItemIndex,language=curLanguage,progressBar=dialogLoading)
            
            # Close the Loading Window 
            xbmc.sleep( 100 )
            dialogLoading.close()
        except Exception, e:
            print("Exception during list update")
            print(str(e))
            print (str(sys.exc_info()[0]))
            traceback.print_exc()
        
            # Close the Loading Window 
            dialogLoading.close()
 
            dialogError = xbmcgui.Dialog()
            dialogError.ok(__language__( 32111 ), __language__( 32113 ), __language__( 32114 ), __language__( 32115 )) #"Erreur", "Impossible de charger la page Têtes à claques.tv", "probleme de connection?", "un changement sur le site distant?"

    def updateDataOnMenu(self, menuSelectIndex):
        """
        Update tacData objet for a specific index in the menu 
        """
        # Display Loading Window while we are loading the information from the website
        dialogLoading = xbmcgui.DialogProgress()
        dialogLoading.create(__language__( 32000 ), __language__( 32102 ),__language__( 32110 ) ) # "Têtes à claques", "Chargement des informations", "Veuillez patienter..."
        try:
            curLanguage = self.CollectionSelector.getCollectionLanguage()
            self.CollectionSelector.updateCollectionData(menuSelectIndex,language=curLanguage,progressBar=dialogLoading)
            
            # Close the Loading Window 
            xbmc.sleep( 100 )
            dialogLoading.close()
        except Exception, e:
            print("Exception during list update")
            print(str(e))
            print (str(sys.exc_info()[0]))
            traceback.print_exc()
        
            # Close the Loading Window 
            dialogLoading.close()
 
            dialogError = xbmcgui.Dialog()
            dialogError.ok(__language__( 32111), __language__( 32113), __language__( 32114), __language__( 32115)) # "Erreur", "Impossible de charger la page Têtes à claques.tv", "probleme de connection?", "un changement sur le site distant?"
            
    def updateControlListFromData(self):
        """
        Update ControlList objet 
        """
        # Create loading windows after updateData
        dialogimg = xbmcgui.DialogProgress()
        dialogimg.create(__language__( 32000 ), __language__( 32104 ),__language__( 32110 ) ) # "Têtes à claques", "Chargement des images", "Veuillez patienter..."
        dialogimg.update(0)

        menuSelectIndex  = self.CollectionSelector.getSelectedMenu()
        numberOfPictures = self.CollectionSelector.selectCollecData[menuSelectIndex].getNumberofItem()
        language         = self.CollectionSelector.getCollectionLanguage()
        videoLabel       = __language__(32305) # " Vidéos"
            
        self.strItemNb.setLabel(str(numberOfPictures) + ' ' + videoLabel ) # Update number of video at the bottom of the page

        # Lock the UI in order to update the list
        xbmcgui.lock()    

        # Clear all ListItems in this control list 
        self.list.reset()
        
        numberOfItem = len(self.CollectionSelector.selectCollecData[menuSelectIndex].titleList)
            
        # add a few items to the list
        for name in self.CollectionSelector.selectCollecData[menuSelectIndex].titleList:
            index      = self.CollectionSelector.selectCollecData[menuSelectIndex].titleList.index(name)
            image2load = os.path.join(CACHEDIR, os.path.basename(self.CollectionSelector.selectCollecData[menuSelectIndex].imageFilenameList[index]))                        
            if not os.path.exists(image2load):
                # images not here use default
                image2load = os.path.join(IMAGEDIR,"noImageAvailable.jpg")
                    
            # Adding to the List picture image2load
            self.list.addItem(xbmcgui.ListItem(label = name, thumbnailImage = image2load))

            # Compute % of Image proceeded
            percent = int(((index+1)*100)/numberOfItem)
            dialogimg.update(percent)

        # Go back on 1st button (even if overwritten later)
        self.setFocus(self.button0)
                
        # Set 1st item in the list
        if self.list:
            self.list.selectItem(0)
            
        # Unlock the UI and close the popup
        xbmcgui.unlock()
        dialogimg.update(100)
        dialogimg.close()
            
    def updateIcons(self):
        """
        Retrieve images and update list
        """
        # Now get the images:
        menuSelectIndex = self.CollectionSelector.getSelectedMenu()
        try:       
            for name in self.CollectionSelector.selectCollecData[menuSelectIndex].titleList:
                index           = self.CollectionSelector.selectCollecData[menuSelectIndex].titleList.index(name)
                image2load      = os.path.join(CACHEDIR, os.path.basename(self.CollectionSelector.selectCollecData[menuSelectIndex].imageFilenameList[index]))                        
                image2download  = self.CollectionSelector.selectCollecData[menuSelectIndex].imageFilenameList[index]
                image2save      = os.path.join(CACHEDIR,os.path.basename(self.CollectionSelector.selectCollecData[menuSelectIndex].imageFilenameList[index]))
                
                # Downloading image
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
            if self.configManager.getCleanCache() == True:
                print "Deleting cache"
                self.fileMgr.delFiles(CACHEDIR)
            self.close()
    
    def onControl(self, control):
        if control == self.button0:
            currentLanguageLabel = __language__(32300) # 'Francais' or 'English'
            self.strButton.setLabel("[B]%s[/B]"%__language__(self.CollectionSelector.selectionNameList[0]) + "[COLOR=0xFFFFFFFF] - %s[/COLOR]"%currentLanguageLabel)
            
            self.updateDataOnMenu(0)
            self.updateControlListFromData()
            self.setFocus(self.button0)
            self.updateIcons()

        elif control == self.button1:
            currentLanguageLabel = __language__(32300)  # 'Francais' or 'English'
            self.strButton.setLabel("[B]%s[/B]"%__language__(self.CollectionSelector.selectionNameList[1]) + "[COLOR=0xFFFFFFFF] - %s[/COLOR]"%currentLanguageLabel)
            
            self.updateDataOnMenu(1)
            self.updateControlListFromData()
            self.setFocus(self.button1)
            self.updateIcons()
                        
        elif control == self.button2:
            currentLanguageLabel = __language__(32300)  # 'Francais' or 'English'
            self.strButton.setLabel("[B]%s[/B]"%__language__(self.CollectionSelector.selectionNameList[2]) + "[COLOR=0xFFFFFFFF] - %s[/COLOR]"%currentLanguageLabel)
            
            self.updateDataOnMenu(2)
            self.updateControlListFromData()
            self.setFocus(self.button2)
            self.updateIcons()

        elif control == self.button3:
            currentLanguageLabel = __language__(32300)  # 'Francais' or 'English'
            self.strButton.setLabel("[B]%s[/B]"%__language__(self.CollectionSelector.selectionNameList[3]) + "[COLOR=0xFFFFFFFF] - %s[/COLOR]"%currentLanguageLabel)
            
            self.updateDataOnMenu(3)
            self.updateControlListFromData()
            self.setFocus(self.button3)
            self.updateIcons()

        elif control == self.butOptions:
            # Opening settings window
            winSettingsVideo = SettingsWindow()
            winSettingsVideo.setWindow(self.configManager) # include doModal call
            del winSettingsVideo

        elif control == self.butAPropos:
            # Opening About window
            winAboutVideo = AboutWindow()
            del winAboutVideo
            
        elif control == self.butLanguage:
            currentLanguage = self.CollectionSelector.getCollectionLanguage()
                    
            if currentLanguage == 'french':
                # Go to English
                self.CollectionSelector.setCollectionLanguage('english')
                lang.setLanguage("english")
            else:
                # Go to French
                self.CollectionSelector.setCollectionLanguage('french')
                lang.setLanguage("french")
            
            # Logo
            logoImage = os.path.join(IMAGEDIR,__language__( 32900 ))    
                
            # Menu labels
            optionLabel             = __language__(32303) # "Options"
            buttonlanguageLabel     = __language__(32301) # "English"
            aboutLabel              = __language__(32304) # "A propos"
            currentLanguageLabel    = __language__(32300) # "Francais"
            menuInfoLabel           = __language__(32302) # "SELECTIONNEZ:"
            collectionLabel         = __language__(self.CollectionSelector.selectionNameList[0]) # Collection
            seriesLabel             = __language__(self.CollectionSelector.selectionNameList[1]) # Séries
            extrasLabel             = __language__(self.CollectionSelector.selectionNameList[2]) # Extras
            adsLabel                = __language__(self.CollectionSelector.selectionNameList[3]) # Pubs
            
            # Set the labels
            self.butLanguage.setLabel(buttonlanguageLabel)
            self.strButton.setLabel("[B]%s[/B]"%__language__(self.CollectionSelector.selectionNameList[self.CollectionSelector.getSelectedMenu()]) + "[COLOR=0xFFFFFFFF] - %s[/COLOR]"%currentLanguageLabel)
            self.butOptions.setLabel(optionLabel)
            self.butAPropos.setLabel(aboutLabel)
            self.button0.setLabel(collectionLabel)
            self.button1.setLabel(seriesLabel)
            self.button2.setLabel(extrasLabel)
            self.button3.setLabel(adsLabel)
            self.user_logo.setImage(logoImage)
            
            self.updateDataOnMenu(self.CollectionSelector.getSelectedMenu())
            self.updateControlListFromData()
            self.setFocus(self.butLanguage)
            self.updateIcons()

        elif control == self.list:
            chosenIndex = self.list.getSelectedPosition()
            
            # Play the video or load sub-serie list depending on the type of list we are
            if self.CollectionSelector.isSubCollec(chosenIndex): # this function will play the video if the list item was a video
                self.updateDataOnList(chosenIndex)
                self.updateControlListFromData()
                self.updateIcons()



#FONCTION POUR RECUPERER LE THEME UTILISE PAR L'UTILISATEUR.
def getUserSkin():
    print "getUserSkin"
    current_skin = xbmc.getSkinDir()
    print "current_skin = %s"%current_skin
    force_fallback = os.path.exists( os.path.join( CWD, "resources", "skins", current_skin ) )
    print "force_fallback = %s"%force_fallback
    if not force_fallback: current_skin = "Default"
    print "current_skin = %s"%current_skin
    return current_skin, force_fallback


KEY_BUTTON_BACK = 275
KEY_KEYBOARD_ESC = 61467

 
class TacMainWindow( xbmcgui.WindowXML ):
    def __init__( self, *args, **kwargs ):
        """
        The Idea for this function is to be used to put the inital data 
        """
        if Emulating: xbmcgui.Window.__init__(self)
        if not Emulating:
            self.setCoordinateResolution(PAL_4x3) # Set coordinate resolution to PAL 4:3
        print "TacMainWindow __init__"
        # Check conf file
        print "TacMainWindow creating configManager"
        self.configManager = configCtrl()

        if (self.configManager.getLanguage() == 'french'):
            lang.setLanguage("french")
            print "french"
        else:
            lang.setLanguage("english")
            print "english"
            
        # Create a file manager and check directory
        print "TacMainWindow creating fileMgr"
        self.fileMgr = fileMgr(dirCheckList)
        print "TacMainWindow __init__ DONE"

        # Display Loading Window while we are loading the information from the website
        #self.dialogUI = xbmcgui.DialogProgress()        

        # Check conf file
        print "TacMainWindow creating configManager"
        self.configManager = configCtrl()
        
        if (self.configManager.getLanguage() == 'french'):
            lang.setLanguage("french")
            print "french"
        else:
            lang.setLanguage("english")
            print "english"
            
        #self.dialogUI.create(__language__( 32000 ), __language__( 32100 ),__language__( 32110 ) ) # "Têtes à claques", "Creation de l'interface Graphique", "Veuillez patienter..."

        #xbmcgui.lock()

        # Create selectCollectionWebpage instance in order to display choice of video collection
        self.CollectionSelector = SelectCollectionWebpage(tacBasePageURL, tacNameSelectList, tacUrlSelectList,self.configManager)
        print ("self.CollectionSelector.selectionNameList")
        print(self.CollectionSelector.selectionNameList)
        print ("self.CollectionSelector.selectionURLList")
        print(self.CollectionSelector.selectionURLList)
        
        # Update language variable at startup
        self.CollectionSelector.setCollectionLanguage(self.configManager.getLanguage())

    def onInit( self ):
        #self.setCoordinateResolution(PAL_4x3) # Set coordinate resolution to PAL 4:3
        #print "TacMainWindow onInit"
        print "onInit(): Window Initalized"



        
        # User logo paths
        logoImage = os.path.join(IMAGEDIR,__language__( 32900 )) # "logo-fr.png" or "logo-en.png"
            
        # Menu labels
        optionLabel             = __language__(32303) # Options
        buttonlanguageLabel     = __language__(32301) # English
        aboutLabel              = __language__(32304) # A propos
        currentLanguageLabel    = __language__(32300) # Francais
        menuInfoLabel           = __language__(32302) # SELECTIONNEZ:

        menuInfoLabel           = __language__(32302) # "SELECTIONNEZ:"
        collectionLabel         = __language__(self.CollectionSelector.selectionNameList[0]) # Collection
        seriesLabel             = __language__(self.CollectionSelector.selectionNameList[1]) # Séries
        extrasLabel             = __language__(self.CollectionSelector.selectionNameList[2]) # Extras
        adsLabel                = __language__(self.CollectionSelector.selectionNameList[3]) # Pubs


#        xbmcgui.lock()
        try: 
            self._reset_views()
            self.setProperty( "view-Collection", "activated" )

            print "TacMainWindow setting control WIndowXML"
            self.getControl( 30 ).setImage(logoImage)
#            self.getControl( 100 ).setLabel("CCH CCH CCH" )

            
#            self.getControl( 1 ).reset()
#            self.getControl( 1 ).setImage(logoImage)
#            self.getControl( 2 ).reset()
#            self.getControl( 2 ).setLabel("Vue" )
#            self.getControl( 100 ).reset()
            self.getControl( 100 ).setLabel("[B]%s[/B]"%__language__(self.CollectionSelector.selectionNameList[self.CollectionSelector.getSelectedMenu()]) + "[COLOR=0xFFFFFFFF] - %s[/COLOR]"%currentLanguageLabel)
#            self.getControl( 150 ).setLabel(__language__( 32306 ))
#            self.getControl( 160 ).setLabel(__language__( 32307 ))
#            self.getControl( 170 ).setLabel(__language__( 32308 ))
#            self.getControl( 180 ).setLabel(__language__( 32309 ))
#            self.getControl( 190 ).setLabel(__language__( 32303 ))
            self.getControl( 140 ).setLabel(buttonlanguageLabel)
            self.getControl( 150 ).setLabel(collectionLabel)
            self.getControl( 160 ).setLabel(seriesLabel)
            self.getControl( 170 ).setLabel(extrasLabel)
            self.getControl( 180 ).setLabel(adsLabel)
            self.getControl( 190 ).setLabel(optionLabel)
            self.getControl( 400 ).setLabel(__language__( 32507 ))
            #self.getControl( 5 ).reset()
        
        except:
            #EXC_INFO( LOG_ERROR, sys.exc_info(), self )
            print "Error setting comtrol with windowXML"
            print (str(sys.exc_info()[0]))
            traceback.print_exc()
        #xbmcgui.unlock()

        
        
#        # Set the TAC logo at top-left position
#        self.user_logo = xbmcgui.ControlImage(20,25,235,144, logoImage)
#        self.addControl(self.user_logo)
#        self.user_logo.setVisible(True)

        
        
        # Close the Loading Window 
        #self.dialogUI.close()
           
        # Update the list of video 
        self.updateDataOnMenu(self.CollectionSelector.getSelectedMenu())
        self.updateControlListFromData()
        #self.updateIcons()

        # Start to diplay the window before doModal call
        #self.show()
        
        # No UI is displayed, continue to get and display the picture (would be too long to wait if we were waiting doModla call)
        self.updateIcons()
        
    def onAction(self, action):
        """"
            onAction in WindowXML works same as on a Window or WindowDialog its for keypress/controller buttons etc
            Handle user input events.
        """
        buttonCode =  action.getButtonCode()
        actionID   =  action.getId()
        print "onAction(): actionID=%i buttonCode=%i" % (actionID,buttonCode)
#        if (buttonCode == KEY_BUTTON_BACK or buttonCode == KEY_KEYBOARD_ESC or buttonCode == 61467):
#            self.close()
        if action == ACTION_PREVIOUS_MENU:
            if self.configManager.getCleanCache() == True:
                print "Deleting cache"
                #self.fileMgr.delFiles(CACHEDIR)
            self.close()

    def onClick(self, controlID):
        """
            onClick(self, controlID) is the replacement for onControl. It gives an interger.
            Handle widget events
        """
        print "onclick(): control %i" % controlID
#        if (controlID == 7):
#            #xbmcgui.Dialog().ok(__title__ + ": About","Example Script coded by Donno :D","WindowXML Class coded by Donno","With help from Spiff and jmarshall :)")
#            dialog = WindowXMLDialogExample("DialogOK.xml",os.path.join(scriptPath,'DefaultSkin'))
#            dialog.setHeading(__title__ + ": About")
#            dialog.setLines("Example Script coded by Donno :D","WindowXML Class coded by Donno","With help from Spiff and jmarshall :)")
#            dialog.doModal()
#            del dialog

        if (controlID == 13):
            pass
#            self.clearList()
#        elif (controlID == 99):
#            for x in range(0,10):
#                self.addItem(xbmcgui.ListItem(("Hello %i" % x),("World %i" % x), "defaultVideo.png", "defaultVideoBig.png"))
#                self.addItem(xbmcgui.ListItem(("Test %i"  % x),("Hey %i"   % x), "defaultVideo.png", "defaultVideoBig.png"))
        elif controlID == 140:
            # Language
            currentLanguage = self.CollectionSelector.getCollectionLanguage()
                    
            if currentLanguage == 'french':
                # Go to English
                self.CollectionSelector.setCollectionLanguage('english')
                lang.setLanguage("english")
            else:
                # Go to French
                self.CollectionSelector.setCollectionLanguage('french')
                lang.setLanguage("french")
            
            # Logo
            logoImage = os.path.join(IMAGEDIR,__language__( 32900 ))    
                
            # Menu labels
            optionLabel             = __language__(32303) # "Options"
            buttonlanguageLabel     = __language__(32301) # "English"
            aboutLabel              = __language__(32304) # "A propos"
            currentLanguageLabel    = __language__(32300) # "Francais"
            menuInfoLabel           = __language__(32302) # "SELECTIONNEZ:"
            collectionLabel         = __language__(self.CollectionSelector.selectionNameList[0]) # Collection
            seriesLabel             = __language__(self.CollectionSelector.selectionNameList[1]) # Séries
            extrasLabel             = __language__(self.CollectionSelector.selectionNameList[2]) # Extras
            adsLabel                = __language__(self.CollectionSelector.selectionNameList[3]) # Pubs
            
            # Set the labels
            self.getControl( 30 ).setImage(logoImage)
            self.getControl( 100 ).setLabel("[B]%s[/B]"%__language__(self.CollectionSelector.selectionNameList[self.CollectionSelector.getSelectedMenu()]) + "[COLOR=0xFFFFFFFF] - %s[/COLOR]"%currentLanguageLabel)
            self.getControl( 140 ).setLabel(buttonlanguageLabel)
            self.getControl( 150 ).setLabel(collectionLabel)
            self.getControl( 160 ).setLabel(seriesLabel)
            self.getControl( 170 ).setLabel(extrasLabel)
            self.getControl( 180 ).setLabel(adsLabel)
            self.getControl( 190 ).setLabel(optionLabel)
            self.getControl( 400 ).setLabel(__language__( 32507 ))
            
            #self.butAPropos.setLabel(aboutLabel)
            
            # Update display
            self.updateDataOnMenu(self.CollectionSelector.getSelectedMenu())
            self.updateControlListFromData()
            self.setFocus(self.getControl( 140 )) # Set focus on language button
            self.updateIcons()
        
        elif controlID == 150:
            # Collection
            self._reset_views()
            self.setProperty( "view-Collection", "activated" )
            
            currentLanguageLabel = __language__(32300) # 'Francais' or 'English'
            self.getControl( 100 ).setLabel("[B]%s[/B]"%__language__(self.CollectionSelector.selectionNameList[0]) + "[COLOR=0xFFFFFFFF] - %s[/COLOR]"%currentLanguageLabel)
            
            self.updateDataOnMenu(0)
            self.updateControlListFromData()
            #self.setFocus(self.button0)
            self.updateIcons()
            
        elif controlID == 160:
            # Serie
            self._reset_views()
            self.setProperty( "view-Series", "activated" )
            
            currentLanguageLabel = __language__(32300)  # 'Francais' or 'English'
            self.getControl( 100 ).setLabel("[B]%s[/B]"%__language__(self.CollectionSelector.selectionNameList[1]) + "[COLOR=0xFFFFFFFF] - %s[/COLOR]"%currentLanguageLabel)
            
            self.updateDataOnMenu(1)
            self.updateControlListFromData()
            #self.setFocus(self.button1)
            self.updateIcons()
            
        elif controlID == 170:
            # Extras
            self._reset_views()
            self.setProperty( "view-Extras", "activated" )
            
            currentLanguageLabel = __language__(32300)  # 'Francais' or 'English'
            self.getControl( 100 ).setLabel("[B]%s[/B]"%__language__(self.CollectionSelector.selectionNameList[2]) + "[COLOR=0xFFFFFFFF] - %s[/COLOR]"%currentLanguageLabel)
            
            self.updateDataOnMenu(2)
            self.updateControlListFromData()
            #self.setFocus(self.button1)
            self.updateIcons()

        elif controlID == 180:
            # Ads
            self._reset_views()
            self.setProperty( "view-Ads", "activated" )
            
            currentLanguageLabel = __language__(32300)  # 'Francais' or 'English'
            self.getControl( 100 ).setLabel("[B]%s[/B]"%__language__(self.CollectionSelector.selectionNameList[3]) + "[COLOR=0xFFFFFFFF] - %s[/COLOR]"%currentLanguageLabel)
            
            self.updateDataOnMenu(3)
            self.updateControlListFromData()
            #self.setFocus(self.button1)
            self.updateIcons()
            
        elif controlID == 190:
            # Settings
            self._reset_views()
            self.setProperty( "view-Settings", "activated" )

        elif (50 <= controlID <= 59):
#            print "CurrentListPosition: %i" % self.getCurrentListPosition()
#            selItem = self.getListItem(self.getCurrentListPosition())
#            print "Selected List Item: Label: %s  Label 2 %s" % (selItem.getLabel(),selItem.getLabel2())
#            print "List Item 2: Label: %s   Label 2: %s" % (self.getListItem(2).getLabel(),self.getListItem(2).getLabel2())
            chosenIndex = self.getCurrentListPosition()
            
            # Play the video or load sub-serie list depending on the type of list we are
            if self.CollectionSelector.isSubCollec(chosenIndex): # this function will play the video if the list item was a video
                self._reset_views()
                self.setProperty( "view-Sub-Serie", "activated" )
                self.updateDataOnList(chosenIndex)
                self.updateControlListFromData()
                self.updateIcons()

    def onFocus( self, controlID ):
        #cette fonction n'est pas utiliser ici, mais dans les XML si besoin
        pass
    
    def updateDataOnMenu(self, menuSelectIndex):
        """
        Update tacData objet for a specific index in the menu 
        """
        # Display Loading Window while we are loading the information from the website
        dialogLoading = xbmcgui.DialogProgress()
        dialogLoading.create(__language__( 32000 ), __language__( 32102 ),__language__( 32110 ) ) # "Têtes à claques", "Chargement des informations", "Veuillez patienter..."
        try:
            curLanguage = self.CollectionSelector.getCollectionLanguage()
            #self.CollectionSelector.updateCollectionData(menuSelectIndex,language=curLanguage,progressBar=dialogLoading)
            self.CollectionSelector.updateCollectionData(menuSelectIndex,language=curLanguage)
            
            # Close the Loading Window 
            xbmc.sleep( 100 )
            dialogLoading.close()
        except Exception, e:
            print("Exception during list update")
            print(str(e))
            print (str(sys.exc_info()[0]))
            traceback.print_exc()
        
            # Close the Loading Window 
            dialogLoading.close()
 
            dialogError = xbmcgui.Dialog()
            dialogError.ok(__language__( 32111), __language__( 32113), __language__( 32114), __language__( 32115)) # "Erreur", "Impossible de charger la page Têtes à claques.tv", "probleme de connection?", "un changement sur le site distant?"
        
    def updateDataOnList(self, listItemIndex):
        """
        Update tacData objet for a specific index in the main list
        """
        # Display Loading Window while we are loading the information from the website
        dialogLoading = xbmcgui.DialogProgress()
        dialogLoading.create(__language__( 32000 ), __language__( 32102 ),__language__( 32110 ) ) # "Têtes à claques", "Chargement des informations", "Veuillez patienter..."
        
        try:
            curLanguage = self.CollectionSelector.getCollectionLanguage()
            self.CollectionSelector.updateSubCollectionData(listItemIndex,language=curLanguage,progressBar=dialogLoading)
            
            # Close the Loading Window 
            xbmc.sleep( 100 )
            dialogLoading.close()
        except Exception, e:
            print("Exception during list update")
            print(str(e))
            print (str(sys.exc_info()[0]))
            traceback.print_exc()
        
            # Close the Loading Window 
            dialogLoading.close()
 
            dialogError = xbmcgui.Dialog()
            dialogError.ok(__language__( 32111 ), __language__( 32113 ), __language__( 32114 ), __language__( 32115 )) #"Erreur", "Impossible de charger la page Têtes à claques.tv", "probleme de connection?", "un changement sur le site distant?"

    def updateControlListFromData(self):
        """
        Update ControlList objet 
        """
        # Create loading windows after updateData
        dialogimg = xbmcgui.DialogProgress()
        dialogimg.create(__language__( 32000 ), __language__( 32104 ),__language__( 32110 ) ) # "Têtes à claques", "Chargement des images", "Veuillez patienter..."
        dialogimg.update(0)

        print "updateControlListFromData"

        menuSelectIndex  = self.CollectionSelector.getSelectedMenu()
        numberOfPictures = self.CollectionSelector.selectCollecData[menuSelectIndex].getNumberofItem()
        language         = self.CollectionSelector.getCollectionLanguage()
        videoLabel       = __language__(32305) # " Vidéos"
            
        #self.strItemNb.setLabel(str(numberOfPictures) + ' ' + videoLabel ) # Update number of video at the bottom of the page
        print self.CollectionSelector.selectCollecData[menuSelectIndex].titleList

        # Lock the UI in order to update the list
        xbmcgui.lock()    

        # Clear all ListItems in this control list 
        self.clearList()
        
        numberOfItem = len(self.CollectionSelector.selectCollecData[menuSelectIndex].titleList)
            
        # add a few items to the list
        for name in self.CollectionSelector.selectCollecData[menuSelectIndex].titleList:
            index      = self.CollectionSelector.selectCollecData[menuSelectIndex].titleList.index(name)
            image2load = os.path.join(CACHEDIR, os.path.basename(self.CollectionSelector.selectCollecData[menuSelectIndex].imageFilenameList[index]))
            print "updateControlListFromData - image2load = %s"%image2load              
            if not os.path.exists(image2load) or os.path.isdir(image2load):
                # images not here use default
                image2load = os.path.join(IMAGEDIR,"noImageAvailable.jpg")
                    
            # Adding to the List picture image2load
            self.addItem(xbmcgui.ListItem(label = name, thumbnailImage = image2load))

            # Compute % of Image proceeded
            percent = int(((index+1)*100)/numberOfItem)
#            dialogimg.update(percent)

        print "updateControlListFromData END"
        # Go back on 1st button (even if overwritten later)
        #self.setFocus(self.button0)
                
#        # Set 1st item in the list
#        if self.list:
#            self.list.selectItem(0)
            
        # Unlock the UI and close the popup
        xbmcgui.unlock()
        dialogimg.update(100)
        dialogimg.close()
            
    def updateIcons(self):
        """
        Retrieve images and update list
        """
        # Now get the images:
        menuSelectIndex = self.CollectionSelector.getSelectedMenu()
        print "updateIcons"
        try:       
            for name in self.CollectionSelector.selectCollecData[menuSelectIndex].titleList:
                index           = self.CollectionSelector.selectCollecData[menuSelectIndex].titleList.index(name)
                image2load      = os.path.join(CACHEDIR, os.path.basename(self.CollectionSelector.selectCollecData[menuSelectIndex].imageFilenameList[index]))                        
                image2download  = self.CollectionSelector.selectCollecData[menuSelectIndex].imageFilenameList[index]
                image2save      = os.path.join(CACHEDIR,os.path.basename(self.CollectionSelector.selectCollecData[menuSelectIndex].imageFilenameList[index]))
                
                # Downloading image
                try:
                    downloadJPG(image2download, image2save)
                except:
                    print("Exception on image downloading: " + image2download)

                # Display the picture
                print "image2save = %s"%image2save
                print "image2download = %s"%image2download
                if os.path.exists(image2save) and not image2download.endswith('/'):
                    print "set image %s"%image2save
                    self.getListItem(index).setThumbnailImage(image2save)
                else:
                    print "%s does NOT exist"%image2save
        except Exception, e:
            print("Exception")
            print(e)
            print (str(sys.exc_info()[0]))
            traceback.print_exc()

    def _reset_views( self ):
        self.setProperty( "view-Collection", "")
        self.setProperty( "view-Series", "")
        self.setProperty( "view-Sub-Serie", "")
        self.setProperty( "view-Extras", "")
        self.setProperty( "view-Ads", "")
        self.setProperty( "view-Settings", "")
        
def show_tac_main_window():
    file_xml = "tac-MainWindow.xml"
    #file_xml = "Script_WindowXMLExample.xml"
    #depuis la revision 14811 on a plus besoin de mettre le chemin complet, la racine suffit
    dir_path = CWD #xbmc.translatePath( os.path.join( CWD, "resources" ) ) 
    #recupere le nom du skin et si force_fallback est vrai, il va chercher les images du defaultSkin.
    current_skin, force_fallback = getUserSkin()
    
    print "Creating TacMainWindow"
    w = TacMainWindow( file_xml, dir_path, current_skin, force_fallback )
    w.doModal()
    del w
                        

def startup():
    """
    
    Startup function
    
    """
    # Check conf file
    configManager = configCtrl()
        
    if configManager.getLanguage() == "":
        # Language not set
        print "Language not set"
        # Get language using FirstStartWindow
        selectLangWin = FirstStartWindow()
        language = selectLangWin.getLanguage(configManager)
        del selectLangWin
        del configManager
        if language != None:
            # Create main Window
            tacgui = Window()
            tacgui.doModal() # Display this window until close() is called
            del tacgui
    else:
        print "Language already set"
        # Create main Window
        tacgui = Window()
        tacgui.doModal() # Display this window until close() is called
        del tacgui
    
    
    

########
#
# Main
#
########

if __name__ == "__main__":
    print("===================================================================")
    print("")
    print("              TAC.tv HTML parser STARTS")
    print("")
    print("===================================================================")
    
    # Print Path information
    print("ROOTDIR" + ROOTDIR)
    print("IMAGEDIR" + IMAGEDIR)
    print("CACHEDIR" + CACHEDIR)
    
    # Calling startup function
    show_tac_main_window()
    #startup()
else:
    # Library case
    pass


    

