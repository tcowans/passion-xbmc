# -*- coding: cp1252 -*-
"""
Têtes à claques HTML parser with GUI by Temhil (temhil@gmail.com)
 
07-11-08 Version 1.0-Dev03 par Temhil: 
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
version     = '1.0-Dev03'
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
        #self.language      = 'fr-ca'
        self.language      = ''
        self.delCache      = True
        try:
            # Create config parser
            self.config = ConfigParser.ConfigParser()
            
            # Read config from .cfg file
            # - Open config file
            self.config.read(os.path.join(ROOTDIR,"TAC.cfg"))
            
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
                cfgfile=open(os.path.join(ROOTDIR,"TAC.cfg"), 'w+')
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
        
    def setDefaultPlayer(self,playerType):
        """
        set DefaultPlayerparameter locally and in .cfg file
        """
        self.defaultPlayer = playerType
        
        # Set player parameter
        self.config.set("system", "player", playerType)
        
        # Update file
        cfgfile=open(os.path.join(ROOTDIR,"TAC.cfg"), 'w+')
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
        
    def setLanguage(self,language):
        """
        set language parameter locally and in .cfg file
        """
        self.language = language
        
        # Set player parameter
        self.config.set("user", "language", language)
        
        # Update file
        cfgfile=open(os.path.join(ROOTDIR,"TAC.cfg"), 'w+')
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

    def setCleanCache(self,cleanCacheStatus):
        """
        set clean cache status locally and in .cfg file
        @param cleanCacheStatus: clean cache status - define cache directory will be cleaned or not on exit
        """
        self.delCache = cleanCacheStatus
        
        # Set cachepages parameter
        self.config.set("system", "cleancache", self.delCache)

        # Update file
        cfgfile=open(os.path.join(ROOTDIR,"TAC.cfg"), 'w+')
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
        

#    def GetSerieList(self, seriedataObj):
#
##        self.idSerieList        = []
##        self.titleSerieList     = []
##        self.imageSerieFileList = []
##        self.lenghtSerieList    = []
#            
#        soup = BeautifulStoneSoup(self.Source)
#        #videosInfo=[]
#        try:
#            for serie in soup.findAll("serie"):
#            
#                # Copy each item found in a list
#                seriedataObj.idSerieList.append(serie.idserie)
#                seriedataObj.titleSerieList.append(serie.titreserie.string.encode("cp1252"))
#                imageURL = serie.imageserie.string.encode("utf-8")
#                if not imageURL.startswith('http'):
#                    imageURL = tacBasePageURL + imageURL
#                seriedataObj.imageSerieFileList.append(imageURL)
#                seriedataObj.timeSerieList.append(serie.dureeserie.string.encode("utf-8"))
#        except Exception, e:
#            print("tacSeriesWebPage: Exception during XMl parsing")
#            print(str(e))
#            print (str(sys.exc_info()[0]))
#            traceback.print_exc()
#        print "++++++++++++++++++++++++++++++++++++"
#        print "tacSeriesWebPage - videosInfo:"    
#        #print videosInfo
#        print(seriedataObj.titleSerieList)
#        print(seriedataObj.idSerieList)
#        print(seriedataObj.imageFilenameList)
#        print(seriedataObj.imageSerieFileList)
#        print(seriedataObj.timeSerieList)
    
    def GetSerieList(self, seriedataObj):
        # Extract video File Name from the TAC webpage
        # Liste serie
        soup = BeautifulStoneSoup(self.Source)
        #videosInfo=[]
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

        print "++++++++++++++++++++++++++++++++++++"
        print "tacSeriesWebPage - videosInfo:"    
        #print videosInfo
        print(seriedataObj.titleList)
        print(seriedataObj.idList)
        print(seriedataObj.imageFilenameList)
        print(seriedataObj.videoFilenameList)
        print(seriedataObj.imageFilenameList)
        print(seriedataObj.nbrvotesList)
        
    def GetSerieVideoList(self, idserie, dataObj):
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
            
        except Exception, e:
            print("GetSerieVideoList: Exception during XMl parsing")
            print(str(e))
            print (str(sys.exc_info()[0]))
            traceback.print_exc()
        print "++++++++++++++++++++++++++++++++++++"
        print "GetSerieVideoList - videosInfo:"    
        #print videosInfo
        print(dataObj.titleList)
        print(dataObj.idList)
        print(dataObj.imageFilenameList)
        print(dataObj.videoFilenameList)
        print(dataObj.imageFilenameList)
        print(dataObj.nbrvotesList)


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


class tacSerieData:
    """
     Data Warehouse for datas extracted from Serie
     XML page(s)     
     """
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
        
        print("tacSerieData init DONE")

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
        print("tacSerieData RESET DONE")
    
    def getNumberofItem(self):
        """
        Retrun the total number of item (series) found for the collection
        """
        print("NumberofItem for = " + str(self.idSerieList))
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

    def __init__(self, pagebaseUrl, nameSelecList, urlSelectList,configManager):
        """
        Initialization
        """
        self.language                   ='fr-ca'
        self.isSerieActive              = False
        self.selectedMenu               = int(0)
        
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
            
        # Create additionnal one for the content of s serie
        #TODO: manage paralle list for video of serie???
        self.selectCollecData.append(tacCollectionData())
        
        print("self.SelectCollectionWebpage created")

    def setCollectionLanguage(self, langue):
        """
        Set the language (proposed videos are differents in French and English)
        """
        self.language = langue
        # Reste dataloaded status
        for i in range(self.menulen):
            self.selectCollecData[i].dataLoaded = False
        print "New language = %s"%self.language

    def getCollectionLanguage(self):
        """
        get the current language (proposed videos are differents in French and English)
        """
        return self.language
    
    def getSelectedMenu(self):
        return self.selectedMenu

    def updateSubCollectionData(self,listIdx,language,progressBar=None):
        self.selectedMenu = 4 # Sub collection index
        self.language     = self.language 
        
        print "getSubCollectionData; Subserie case"
        
        barprogression = 0
        try:
            if (progressBar != None):
                progressBar.update(barprogression)
        except Exception, e:        
            print("getCollectionData - Exception calling UI callback for download")
            print(str(e))
            print progressBar

        # Load XML webpage of Têtes à claques
        print "Load XML webpage of Têtes à claques"
        params={}
        print "language = %s"%language
        
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
        
        print("getSubCollectionData: myCollectionWebPage created for selectedMenu = " + str(1) + " with URL: " + tacBasePageURL + self.selectionURLList[1])

        #TODO: check is this line is not optionnal
        self.selectCollecData[self.selectedMenu].reset()
        
        # Extract data from myCollectionWebPage and copy the content in corresponding Collection Data Instance
                    
        try:
            serieIdx = self.selectCollecData[1].idList[listIdx]
            myCollectionWebPage.GetSerieVideoList(serieIdx, self.selectCollecData[self.selectedMenu])
        except Exception, e:        
            print("getSubCollectionData - Subserie case : Impossible to get collection data for all the serie")
            print(str(e))

    def updateCollectionData(self,index,language,progressBar=None):
        """
        Retourne the colelction data correpsonding to index and set it as current index
        """
        self.selectedMenu = index
        self.language     = self.language 
        
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
            print "Load XML webpage of Têtes à claques"
            params={}
            print "language = %s"%language
    
            if self.selectedMenu == 1:
                print "getCollectionData : Series cases"
                myCollectionWebPage=tacSeriesWebPage(self.selectionURLList[index], params, selection=self.selectionCollecTypeList[index], langue=self.language, savehtml=True, filename=self.language +'_'+self.selectionWebPageFileList[index])
                
            else:
                print "getCollectionData : Other cases"
                myCollectionWebPage=tacCollectionWebPage(self.selectionURLList[index], params, selection=self.selectionCollecTypeList[index], langue=self.language, savehtml=True, filename=self.language +'_'+self.selectionWebPageFileList[index])
    
            barprogression = 50
            try:
                if (progressBar != None):
                    progressBar.update(barprogression)
            except Exception, e:        
                print("getCollectionData - Exception calling UI callback for download")
                print(str(e))
                print progressBar
            
            print("myCollectionWebPage created for selectedMenu = " + str(index) + " with URL: " + tacBasePageURL + self.selectionURLList[index])
    
            # Get Webpage Page number for this collection on the 1st webpage
            #pagemax = myCollectionWebPage.GetNumberofPages()   
            #print("Total Number Webpage Page for this collection : " + str(pagemax))
            
            # Reset collection data 
            #TODO: check is this line is not optionnal
            self.selectCollecData[index].reset()
            
            # Extract data from myCollectionWebPage and copy the content in corresponding Collection Data Instance
                        
            if self.selectedMenu == 1:
                print "Series case"
                myCollectionWebPage.GetSerieList(self.selectCollecData[index])
            else:
                print "OTHER CASES"
                myCollectionWebPage.GetVideoList(self.selectCollecData[index])
    
            # Update dataLoaded flag
            self.selectCollecData[index].dataLoaded = True
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
        
        # Return the colelction data
        return self.selectCollecData[index]
        
        
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
            print "isSubCollec: Sub Serie case:"
            
            # Reset collection data for sub colelction (index 4) in case we already had one
            self.selectCollecData[4].reset()
            
            result = True
        else:
            print "isSubCollec:Video case:"
            print("isSubCollec:chosen Index = " + str(listIdx))
                        
            # Get the URl of the video to play
            video2playURL = self.selectCollecData[self.selectedMenu].videoFilenameList[listIdx]
            
            print("isSubCollec:video2playURL = " + video2playURL)
            
            # Play the selected video
            print("isSubCollec:Play the selected video: " + video2playURL)
            #xbmc.Player().play(video2playURL)
            xbmc.Player(self.configManager.getDefaultPlayer()).play(video2playURL)
            
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
        self.configManager   = configManager
        self.strListMaxSize  = 50
        self.playerMenuList  = ["Auto","DVD Player","MPlayer"]
        self.languageMenuList = ["Francais","English"]
        self.languageList = ["fr-ca","en"]
        self.cleanCacheList  = ["Activé","Désactivé"]
        
        # Background image
        self.addControl(xbmcgui.ControlImage(100,100,445,335, os.path.join(IMAGEDIR,"dialog-panel.png")))

        # Title label:
        self.strlist = xbmcgui.ControlLabel(100, 105, 445, 30, 'Options', 'special13',alignment=6)
        self.addControl(self.strlist)

        # Get settings
        self.defaultPlayer  = self.configManager.getDefaultPlayer()
        self.language       = self.configManager.getLanguage()
        self.cleanCache     = self.configManager.getCleanCache()
        
        
        # item Control List
        self.strDefaultPlayerTitle   = "Player vidéo: "
        self.strDefaultPlayerContent = self.playerMenuList[self.defaultPlayer]
        self.strLanguageTitle    = "Langue: "
        
        for lang in self.languageList:
            if str(self.language) == lang:
                self.strLanguageContent  = self.languageMenuList[self.languageList.index(lang)]
                break
        #self.strLanguageContent  = str(self.language)
        self.strCleanCacheTitle      = "Nettoyage auto du cache: "
        if self.cleanCache:
            self.strCleanCacheContent = self.cleanCacheList[0] #Activé
        else:
            self.strCleanCacheContent = self.cleanCacheList[1] #Désactivé
            
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

    #TODO: Create a general update function???
        
    def onAction(self, action):
        if action == ACTION_PREVIOUS_MENU:
            #close the window
            self.close()
            
    def onControl(self, control):
        if control == self.settingsList:
            selectedIndex = self.settingsList.getSelectedPosition()
            print("selectedIndex = " + str(selectedIndex))
            if selectedIndex == 0:
                dialog = xbmcgui.Dialog()
                chosenIndex = dialog.select('Selectionner le Player désiré', self.playerMenuList)
                self.configManager.setDefaultPlayer(chosenIndex)
                self.defaultPlayer           = chosenIndex
                self.strDefaultPlayerContent = self.playerMenuList[self.defaultPlayer]
                self.settingsList.getListItem(selectedIndex).setLabel(self.strDefaultPlayerTitle + self.strDefaultPlayerContent)
            elif selectedIndex == 1:
                dialog = xbmcgui.Dialog()
                chosenIndex = dialog.select('Selectionner la langue désirée au démarrage', self.languageMenuList)
                self.configManager.setLanguage(self.languageList[chosenIndex])
                self.language           = self.languageList[chosenIndex]
                self.strLanguageContent = self.languageMenuList[chosenIndex]
                self.settingsList.getListItem(selectedIndex).setLabel(self.strLanguageTitle + self.strLanguageContent)
                
            elif selectedIndex == 2:
                dialog = xbmcgui.Dialog()
                chosenIndex = dialog.select('Selectionner la gestion du cache désirée', self.cleanCacheList)
                if chosenIndex == 0:
                    self.configManager.setCleanCache(True)
                    self.cleanCache           = True
                    self.strCleanCacheContent = self.cleanCacheList[0] #Activé
                else:
                    self.configManager.setCleanCache(False)
                    self.cleanCache           = False
                    self.strCleanCacheContent = self.cleanCacheList[1] #Désactivé
                self.settingsList.getListItem(selectedIndex).setLabel(self.strCleanCacheTitle + self.strCleanCacheContent)
            else:
                print "SettingsWindow - onControl : Invalid control list index"

        elif control == self.buttonOK:
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
        self.strTitle = xbmcgui.ControlLabel(130, 110, 350, 30, "Les Têtes à claques",'special13')
        self.addControl(self.strTitle)
        self.strVersion = xbmcgui.ControlLabel(130, 140, 350, 30, "Version: " + version)
        self.addControl(self.strVersion)
        self.strAuthor = xbmcgui.ControlLabel(130, 170, 350, 30, "Auteur: "+ author)
        self.addControl(self.strAuthor)        
        self.strDesTitle = xbmcgui.ControlLabel(130, 200, 350, 30, "Description: ")
        self.addControl(self.strDesTitle)        
        strContent = """Ce script permet de visionner les vidéos sur le site www.tetesaclaques.tv que je vous le recommande fortement. Attention rires en vue!
On y découvre chaque semaine un nouveau clip de quelques minutes qui vaut vraiment le détour.
Si vous aimez les Têtes à claques, merci d'encourager leur createurs
en visitant leur site web et/ou en achetant le DVD
"""
        self.strDesContent = xbmcgui.ControlLabel(130, 225, 490, 100, strContent, "font12", textColor='0xFFD3D3D3')
        self.addControl(self.strDesContent)
        
        strCopyRight = """Les droits des diffusions et des images utilisées sont exclusivement réservés à
Salambo productions inc (www.tetesaclaques.tv)"""
        self.strCopyRight = xbmcgui.ControlLabel(130, 465, 500, 20,strCopyRight, "font10",'0xFFFF0000')
        self.addControl(self.strCopyRight)
        
        self.doModal()
        
    def onAction(self, action):
        if action == ACTION_PREVIOUS_MENU:
            #close the window
            self.close()

class getLanguageWindow(xbmcgui.Window):
    def __init__(self):
        if Emulating: xbmcgui.Window.__init__(self)
        if not Emulating:
            self.setCoordinateResolution(PAL_4x3) # Set coordinate resolution to PAL 4:3
        # Background image
        self.addControl(xbmcgui.ControlImage(0,0,720,576, os.path.join(IMAGEDIR,"background.png")))
        
        # Add central image 
        self.logo = xbmcgui.ControlImage(65,138,590,299, os.path.join(IMAGEDIR,"startupLogo.png"))
        self.addControl(self.logo)

    def setConfigManager(self,configManager):
        self.configManager = configManager

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
        
        # Check conf file
        self.configManager = configCtrl()
        
        # User logo paths
        self.user_logo_path_fr = os.path.join(IMAGEDIR,"logo-fr.png")
        self.user_logo_path_en = os.path.join(IMAGEDIR,"logo-en.png")

        # Get current language
        print "Langue: %s"%(self.configManager.getLanguage())
        if (self.configManager.getLanguage() == 'fr-ca'):
            # French menu
            optionLabel             = "Options"
            buttonlanguageLabel     = "English"
            aboutLabel              = "A propos"
            currentLanguageLabel    = "Francais"
            menuInfoLabel           = "SELECTIONNEZ:"
            logoImage               = self.user_logo_path_fr
        else:
            # English menu
            optionLabel             = "Settings"
            buttonlanguageLabel     = "Francais"
            aboutLabel              = "About"
            currentLanguageLabel    = "English"
            menuInfoLabel           = "SELECT:"
            logoImage               = self.user_logo_path_en
        
        
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
    
        # Add image in background behind list
        #self.list_back = xbmcgui.ControlImage(270,60,420,500, os.path.join(IMAGEDIR,"texture.png"))
        self.list_back = xbmcgui.ControlImage(285,70,400,480, os.path.join(IMAGEDIR,"BackList.png"))
        self.addControl(self.list_back)
        self.list_back.setVisible(True)

#        # Add image in background behind list
#        self.list_back = xbmcgui.ControlImage(280,70,400,480, os.path.join(IMAGEDIR,"background.png"))
#        self.addControl(self.list_back)
#        self.list_back.setVisible(True)


        # Control List
        self.list = xbmcgui.ControlList(300, 100, 370, 470, imageWidth=143, space=5, itemHeight=80, font='font12', textColor='0xFFFFFF00',buttonTexture = os.path.join(IMAGEDIR,"blueButton.png"),buttonFocusTexture  = os.path.join(IMAGEDIR,"blueButtonFocus.png"))

        # Number of Video in the list:
        self.strItemNb = xbmcgui.ControlLabel(600, 520, 150, 20, '0 Vidéo', 'font12', '0xFFFFFF00')

        # Version and author:
        self.strVersion = xbmcgui.ControlLabel(40, 520, 250, 30, "Version " + version, 'font12', '0xFFFFFF00')
        
        # Title image background
        self.list_back = xbmcgui.ControlImage(285,20,400,40, os.path.join(IMAGEDIR,"TitleBg.png"))
        self.addControl(self.list_back)
        self.list_back.setVisible(True)

        # Title of list
        self.strButton = xbmcgui.ControlLabel(285, 30, 400, 20, self.CollectionSelector.selectionNameList[self.CollectionSelector.getSelectedMenu()] + ' - ' + currentLanguageLabel, 'special13', '0xFFFFFF00',alignment=6)
        
        self.addControl(self.list)      
        self.addControl(self.strItemNb)
        self.addControl(self.strVersion)
        self.addControl(self.strButton)
        
#        # Menu image background
#        self.menu_back = xbmcgui.ControlImage(35,195,160,315, os.path.join(IMAGEDIR,"blueButton.png"))
#        self.addControl(self.menu_back)
#        self.menu_back.setVisible(True)
        
        # Info for menu
        self.strAction = xbmcgui.ControlLabel(40, 200, 150, 20, menuInfoLabel, 'font12', '0xFFFFFF00')
        self.addControl(self.strAction)
        
        # Buttons               
        self.button0 = xbmcgui.ControlButton(50, 240, 150, 30, self.CollectionSelector.selectionNameList[0],textColor='0xFFFFFF00', focusTexture = os.path.join(IMAGEDIR,"list-focus.png"),noFocusTexture = os.path.join(IMAGEDIR,"list-focus.png"))
        self.addControl(self.button0)
        self.button1 = xbmcgui.ControlButton(50, 280, 150, 30, self.CollectionSelector.selectionNameList[1],textColor='0xFFFFFF00', focusTexture = os.path.join(IMAGEDIR,"list-focus.png"),noFocusTexture = os.path.join(IMAGEDIR,"list-focus.png"))
        self.addControl(self.button1)
        self.button2 = xbmcgui.ControlButton(50, 320, 150, 30, self.CollectionSelector.selectionNameList[2],textColor='0xFFFFFF00', focusTexture = os.path.join(IMAGEDIR,"list-focus.png"),noFocusTexture = os.path.join(IMAGEDIR,"list-focus.png"))
        self.addControl(self.button2)
        self.button3 = xbmcgui.ControlButton(50, 360, 150, 30, self.CollectionSelector.selectionNameList[3],textColor='0xFFFFFF00', focusTexture = os.path.join(IMAGEDIR,"list-focus.png"),noFocusTexture = os.path.join(IMAGEDIR,"list-focus.png"))
        self.addControl(self.button3)

            
        self.butLanguage = xbmcgui.ControlButton(50, 400, 150, 30, buttonlanguageLabel, textColor='0xFFFFFF00', focusTexture = os.path.join(IMAGEDIR,"list-focus.png"),noFocusTexture = os.path.join(IMAGEDIR,"list-focus.png"))
        self.addControl(self.butLanguage)
        self.butOptions = xbmcgui.ControlButton(50, 440, 150, 30, optionLabel, textColor='0xFFFFFF00', focusTexture = os.path.join(IMAGEDIR,"list-focus.png"),noFocusTexture = os.path.join(IMAGEDIR,"list-focus.png"))
        self.addControl(self.butOptions)
        self.butAPropos = xbmcgui.ControlButton(50, 480, 150, 30, aboutLabel,textColor='0xFFFFFF00', focusTexture = os.path.join(IMAGEDIR,"list-focus.png"),noFocusTexture = os.path.join(IMAGEDIR,"list-focus.png"))
        self.addControl(self.butAPropos)
        
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
        #self.updateControlList(self.CollectionSelector.selectedMenu)
        self.updateDataOnMenu(self.CollectionSelector.getSelectedMenu())
        self.updateControlListFromData()

        # Start to diplay the window before doModal call
        self.show()
        
        # No UI is displayed, continue to get and display the picture (would be too long to wait if we were waiting doModla call)
        #self.updateIcons(self.CollectionSelector.selectedMenu)
        self.updateIcons()
       
    def updateDataOnList(self, listItemIndex):
        """
        Update tacData objet for a specific index (menu) 
        """
        # Display Loading Window while we are loading the information from the website
        dialogLoading = xbmcgui.DialogProgress()
        dialogLoading.create("Têtes à claques", "Chargement des informations", "Veuillez patienter...")
        try:
            curLanguage = self.CollectionSelector.getCollectionLanguage()
            self.CollectionSelector.updateSubCollectionData(listItemIndex,language=curLanguage,progressBar=dialogLoading)
            
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

    def updateDataOnMenu(self, menuSelectIndex):
        """
        Update tacData objet for a specific index (menu) 
        """
        # Display Loading Window while we are loading the information from the website
        dialogLoading = xbmcgui.DialogProgress()
        dialogLoading.create("Têtes à claques", "Chargement des informations", "Veuillez patienter...")
        try:
            curLanguage = self.CollectionSelector.getCollectionLanguage()
            self.CollectionSelector.updateCollectionData(menuSelectIndex,language=curLanguage,progressBar=dialogLoading)
            
#            # Load XML webpage of Têtes à claques
#            #i = 1
#            print "Load XML webpage of Têtes à claques"
#            params={}
#            language = self.CollectionSelector.getCollectionLanguage()
#            print "language = %s"%language
#
#            if menuSelectIndex == 1:
#                print "SERIES"
#                
#                myCollectionWebPage=tacSeriesWebPage(self.CollectionSelector.selectionURLList[menuSelectIndex], params, selection=self.CollectionSelector.selectionCollecTypeList[menuSelectIndex], langue=language, savehtml=True, filename=language+'_'+self.CollectionSelector.selectionWebPageFileList[menuSelectIndex])
#            else:
#                print "OTHER CASES"
#            
#                myCollectionWebPage=tacCollectionWebPage(self.CollectionSelector.selectionURLList[menuSelectIndex], params, selection=self.CollectionSelector.selectionCollecTypeList[menuSelectIndex], langue=language, savehtml=True, filename=language+'_'+self.CollectionSelector.selectionWebPageFileList[menuSelectIndex])
#    
#            #barprogression = ((i*100)/pagemax)
#            barprogression = 50
#            dialogLoading.update(barprogression)
#            
#            print("myCollectionWebPage created for self.CollectionSelector.selectedMenu = " + str(menuSelectIndex) + " with URL: " + tacBasePageURL + self.CollectionSelector.selectionURLList[menuSelectIndex])
#    
#            # Get Webpage Page number for this collection on the 1st webpage
#            #pagemax = myCollectionWebPage.GetNumberofPages()   
#            #print("Total Number Webpage Page for this collection : " + str(pagemax))
#            
#            # Reset collection data 
#            self.CollectionSelector.selectCollecData[menuSelectIndex].reset()
#            
#            # Extract data from myCollectionWebPage and copy the content in corresponding Collection Data Instance
#            
##        tacSeriesWebPage
#            
#            
#            myCollectionWebPage.GetVideoList(self.CollectionSelector.selectCollecData[menuSelectIndex])
#    
#            #barprogression = ((i*100)/pagemax)
#            barprogression = 100
#            dialogLoading.update(barprogression)
#    
##            i = i + 1
##                    
##            while i <= int(pagemax) :
##                # Load next webpage in the collection 
##                myCollectionWebPage=tacCollectionWebPage((tacBasePageURL + self.CollectionSelector.selectionURLList[menuSelectIndex] + str(i)),txdata,txheaders)
##                print("New myCollectionWebPage created : " + str(i) + " with URL: " + (tacBasePageURL + self.CollectionSelector.selectionURLList[menuSelectIndex] + str(i)))
##                
##                # Append data from myCollectionWebPage and copy the content in corresponding Collection Data Instance
##                myCollectionWebPage.GetVideoList(self.CollectionSelector.selectCollecData[menuSelectIndex])
##                
##                barprogression = ((i*100)/pagemax)
##                dialogLoading.update(barprogression)
##               
##                i = i + 1
#                
#            # Update dataLoaded flag
#            self.CollectionSelector.selectCollecData[menuSelectIndex].dataLoaded = True

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
            
    #def updateControlList(self, menuSelectIndex):
    def updateControlListFromData(self):
        """
        Update ControlList objet 
        """
        # Create loading windows after updateData
        dialogimg = xbmcgui.DialogProgress()
        dialogimg.create("Têtes à claques", "Chargement des images", "Veuillez patienter...")
        
        menuSelectIndex = self.CollectionSelector.getSelectedMenu()
        print "Update ControlList objet with menuSelectIndex = %s"%menuSelectIndex
        
        # Check is data have already been loaded for this collection
#        if (self.CollectionSelector.selectCollecData[menuSelectIndex].dataLoaded == False):
#            # Never been updated before, go and get the data
#            self.updateData(menuSelectIndex)
        #self.updateData(menuSelectIndex)
            
        dialogimg.update(0)

        numberOfPictures=self.CollectionSelector.selectCollecData[menuSelectIndex].getNumberofItem()
  
        language = self.CollectionSelector.getCollectionLanguage()
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
            

    def updateIcons(self):
        """
        Retrieve images and update list
        """
        # Now get the images:
        menuSelectIndex = self.CollectionSelector.getSelectedMenu()
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
            if self.configManager.getCleanCache() == True:
                print "Deleting cache"
                self.fileMgr.delFiles(CACHEDIR)
            self.close()
            
        elif action == ACTION_SHOW_INFO:
            print("action received: show info")
            
        elif action == ACTION_STOP:
            print("action received: stop")
            
        elif action == ACTION_PAUSE:
            print('action received: pause')
            #dialog = xbmcgui.Dialog()
            #dialog.ok('action received','ACTION_PAUSE')
    
    def onControl(self, control):
        if control == self.button0:
            self.CollectionSelector.selectedMenu = 0
            currentLanguage = self.CollectionSelector.getCollectionLanguage()
            if currentLanguage == 'fr-ca':
                    currentLanguageLabel = 'Francais'
            elif currentLanguage == 'en':
                    currentLanguageLabel = 'English'
            self.strButton.setLabel(self.CollectionSelector.selectionNameList[0] + ' - ' + currentLanguageLabel)
            
            #self.updateControlList(0)
            self.updateDataOnMenu(0)
            self.updateControlListFromData()
            self.setFocus(self.button0)
            #self.updateIcons(0)
            self.updateIcons()

        elif control == self.button1:
            self.CollectionSelector.selectedMenu = 1
            currentLanguage = self.CollectionSelector.getCollectionLanguage()
            if currentLanguage == 'fr-ca':
                    currentLanguageLabel = 'Francais'
            elif currentLanguage == 'en':
                    currentLanguageLabel = 'English'
            self.strButton.setLabel(self.CollectionSelector.selectionNameList[1] + ' - ' + currentLanguageLabel)
            
            #self.updateControlList(1)
            self.updateDataOnMenu(1)
            self.updateControlListFromData()
            self.setFocus(self.button1)
            #self.updateIcons(1)
            self.updateIcons()
                        
        elif control == self.button2:
            self.CollectionSelector.selectedMenu = 2
            currentLanguage = self.CollectionSelector.getCollectionLanguage()
            if currentLanguage == 'fr-ca':
                    currentLanguageLabel = 'Francais'
            elif currentLanguage == 'en':
                    currentLanguageLabel = 'English'
            self.strButton.setLabel(self.CollectionSelector.selectionNameList[2] + ' - ' + currentLanguageLabel)
            
            #self.updateControlList(2)
            self.updateDataOnMenu(2)
            self.updateControlListFromData()
            self.setFocus(self.button2)
            #self.updateIcons(2)
            self.updateIcons()

        elif control == self.button3:
            self.CollectionSelector.selectedMenu = 3
            currentLanguage = self.CollectionSelector.getCollectionLanguage()
            if currentLanguage == 'fr-ca':
                    currentLanguageLabel = 'Francais'
            elif currentLanguage == 'en':
                    currentLanguageLabel = 'English'
            self.strButton.setLabel(self.CollectionSelector.selectionNameList[3] + ' - ' + currentLanguageLabel)
            
            #self.updateControlList(3)
            self.updateDataOnMenu(3)
            self.updateControlListFromData()
            self.setFocus(self.button3)
            #self.updateIcons(3)
            self.updateIcons(0)

        elif control == self.butOptions:
            winSettingsVideo = SettingsWindow()
            winSettingsVideo.setWindow(self.configManager) # include doModal call
            del winSettingsVideo

        elif control == self.butAPropos:
            winAboutVideo = AboutWindow()
            del winAboutVideo
            
        elif control == self.butLanguage:
            currentLanguage = self.CollectionSelector.getCollectionLanguage()
            if currentLanguage == 'fr-ca':
                # Go to English
                self.CollectionSelector.setCollectionLanguage('en')
                currentLanguageLabel    = "English"
                buttonLanguageLabel     = "Francais"
                optionLabel             = "Settings"
                aboutLabel              = "About"
                menuInfoLabel           = "SELECT:"
                logoImage               = self.user_logo_path_en
            else:
                # Go to French
                self.CollectionSelector.setCollectionLanguage('fr-ca')

                currentLanguageLabel    = "Francais"
                buttonLanguageLabel     = "English"
                optionLabel             = "Options"
                aboutLabel              = "A propos"
                menuInfoLabel           = "SELECTIONNEZ:"
                logoImage               = self.user_logo_path_fr
            self.butLanguage.setLabel(buttonLanguageLabel)
            self.strAction.setLabel(menuInfoLabel)
            self.strButton.setLabel(self.CollectionSelector.selectionNameList[self.CollectionSelector.getSelectedMenu()] + ' - ' + currentLanguageLabel)
            self.butOptions.setLabel(optionLabel)
            self.butAPropos.setLabel(aboutLabel)
            self.user_logo.setImage(logoImage)
            
            #self.updateControlList(self.CollectionSelector.selectedMenu)
            self.updateDataOnMenu(self.CollectionSelector.selectedMenu)
            self.updateControlListFromData()
            self.setFocus(self.butLanguage)
            #self.updateIcons(self.CollectionSelector.getSelectedMenu())
            self.updateIcons()

        elif control == self.list:
            chosenIndex = self.list.getSelectedPosition()
            print("chosenIndex = " + str(chosenIndex))
            
            if self.CollectionSelector.isSubCollec(chosenIndex): # this function will play the video if the list item was a video
                self.updateDataOnList(chosenIndex)
                self.updateControlListFromData()
                self.updateIcons()
                
                        
#            # Get the URl of the video to play
#            video2playURL = self.CollectionSelector.selectCollecData[self.CollectionSelector.getSelectedMenu()].videoFilenameList[chosenIndex]
#            
#            print("video2playURL = " + video2playURL)
#            
#            # Play the selected video
#            print("Play the selected video: " + video2playURL)
#            #xbmc.Player().play(video2playURL)
#            xbmc.Player(self.configManager.getDefaultPlayer()).play(video2playURL)

def startup():
    # Check conf file
    configManager = configCtrl()
        
    if configManager.getLanguage() == "":
        # Language not set
        print "Language not set"
        selectLangWin = getLanguageWindow()
        selectLangWin.setConfigManager(configManager)
        selectLangWin.doModal()
        del selectLangWin

        # Create main Window
        tacgui = Window()
        
        # Display this window until close() is called
        tacgui.doModal()
        del tacgui

    else:
        print "Language already set"
        # Create main Window
        tacgui = Window()
        
        # Display this window until close() is called
        tacgui.doModal()
        del tacgui
    
    
    

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

startup()
## Create main Window
#tacgui = Window()
#
## Display this window until close() is called
#tacgui.doModal()
#del tacgui
    

