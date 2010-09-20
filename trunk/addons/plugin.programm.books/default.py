# -*- coding: utf-8 -*-

# script constants
__plugin__       = "Books"
__addonID__      = "plugin.programm.books"
__author__       = "CinPoU"
__url__          = "http://code.google.com/p/passion-xbmc/"
__credits__      = "Team XBMC passion, http://passion-xbmc.org/developpement-python/plugin-livresbdmangas/"
__platform__     = "xbmc media center, [LINUX, OS X, WIN32]"
__date__         = "08-11-2010"
__version__      = "0.1"

import sys,os,re, shutil
import urllib
import xbmcplugin,xbmcgui,xbmc, xbmcaddon
import unicodedata



# INITIALISATION CHEMIN RACINE
ROOTDIR = os.getcwd().replace( ";", "" )

# Shared resources
BASE_RESOURCE_PATH = os.path.join( ROOTDIR, "resources" )
SPECIAL_PROFILE_DIR = xbmc.translatePath( "special://profile/" )
# append the proper platforms folder to our path, xbox is the same as win32
env = ( os.environ.get( "OS", "win32" ), "win32", )[ os.environ.get( "OS", "win32" ) == "xbox" ]
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "platform_libraries", env ) )
# append the proper libs folder to our path
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "libs" ) )
# append the proper etree folder to our path
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "libs", "elementtree" ) )

#modules custom
from specialpath import *
from DBlib import *
from display import *
from elementtree import ElementTree

imgUserDir = os.path.join( sys.modules[ "__main__" ].SPECIAL_SCRIPT_DATA, "img" )
if not os.path.isdir(imgUserDir) :
    os.mkdir(imgUserDir)


#Initialisation des chemins
imgDir = os.path.join(BASE_RESOURCE_PATH,"images")
#Images du plugin
defaultIcon = os.path.join(imgDir,"Default.png")
defaultFolderIcon = os.path.join(imgDir,"DefaultFolder.png")
titleIcon = os.path.join(imgDir,"titleIcon.png")
authorIcon = os.path.join(imgDir,"authorIcon.png")
genreIcon = os.path.join(imgDir,"genreIcon.png")
langueIcon = os.path.join(imgDir,"langueIcon.png")
sourceIcon = os.path.join(imgDir,"sourceIcon.png")
addIcon = os.path.join(imgDir,"addIcon.png")


#Init Dialog
dialog = xbmcgui.Dialog()


#DEF      
#Clavier                
def show_keyboard (textDefault, textHead, textHide=False) :
    """Show the keyboard's dialog"""
    keyboard = xbmc.Keyboard(textDefault, textHead)
    inputText = ""
    if textHide == True :
        keyboard.setHiddenInput(True)
    keyboard.doModal()
    if (keyboard.isConfirmed()):
        inputText = keyboard.getText()         
        dialogInfo = xbmcgui.Dialog()
    del keyboard
    return inputText


def cleanString(s):
  """Removes all accents from the string"""
  if isinstance(s,str):
      s = unicode(s,"utf8","replace")
      s = unicodedata.normalize('NFD',s)
      return s.encode('ascii','ignore')


#Récupère les paramètres            
def get_params():
        param=[]
        paramstring=sys.argv[2]
        if len(paramstring)>=2:
                params=sys.argv[2]
                cleanedparams=params.replace('?','')
                if (params[len(params)-1]=='/'):
                        params=params[0:len(params)-2]
                pairsofparams=cleanedparams.split('&')
                param={}
                for i in range(len(pairsofparams)):
                        splitparams={}
                        splitparams=pairsofparams[i].split('=')
                        if (len(splitparams))==2:
                                param[splitparams[0]]=splitparams[1]
        return param

#Ouvrir une URL
def launchUrl():
        u=sys.argv[0]+"?mode=3"
        ok=True
        liz=xbmcgui.ListItem(TextLanguage.getLocalizedString(11), iconImage=defaultLaunchIcon, thumbnailImage=defaultLaunchIcon)
        liz.setInfo( type="files", infoLabels={ "Title": TextLanguage.getLocalizedString(11) } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz)
        return ok
        
#Ajoute un lien
def addLink(name,url,iconimage, readonly = False):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode=2&name="+urllib.quote_plus(name)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
        liz.setInfo( type="files", infoLabels={ "Title": name } )
        
        c_items = []
        # ajout d'un bouton dans le contextmenu pour rafraichir l'image
        refreshLabelButton = TextLanguage.getLocalizedString(201)
        refreshActionButton = 'XBMC.RunPlugin(%s?mode=7&name=%s&url=%s)' % ( sys.argv[ 0 ], urllib.quote_plus( name ), urllib.quote_plus( url ), )
        c_items.append(( refreshLabelButton, refreshActionButton ))
        if readonly == False :
            deleteLabelButton = TextLanguage.getLocalizedString(202)
            deleteActionButton = 'XBMC.RunPlugin(%s?mode=8&name=%s&url=%s)' % ( sys.argv[ 0 ], urllib.quote_plus( name ), urllib.quote_plus( url ), )
            c_items.append(( deleteLabelButton , deleteActionButton))
        else :
            addXmlLabelButton = TextLanguage.getLocalizedString(203)
            addXmlActionButton = 'XBMC.RunPlugin(%s?mode=6&name=%s&url=%s)' % ( sys.argv[ 0 ], urllib.quote_plus( name ), urllib.quote_plus( url ), )
            c_items.append(( addXmlLabelButton, addXmlActionButton ))
        # replaceItems=True, seulement mon bouton va etre visible dans le contextmenu 
        # si on veut tous les boutons plus le notre on mets rien listitem.addContextMenuItems( c_items ), car False est par default
        liz.addContextMenuItems( c_items, replaceItems=True )
        
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz)
        return ok

#Ajoute un dossier
def addDir(name,url,mode,iconimage):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        ok=True
        iconimage = os.path.join(imgDir,iconimage)
        liz=xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)

        
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok

def addMainDir(name,mode,iconimage):
        u=sys.argv[0]+"?mode="+str(mode)
        ok=True
        liz=xbmcgui.ListItem(name, iconimage, iconimage)
        liz.setInfo( type="files", infoLabels={ "Title": name } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)

def addAuthors(name,authorID,iconimage):
        u=sys.argv[0]+"?mode=1&idAuthor="+str(authorID)
        ok=True
        liz=xbmcgui.ListItem(name, iconimage, iconimage)
        liz.setInfo( type="files", infoLabels={ "Title": name } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)

def addGenres(name,genreID,iconimage):
        u=sys.argv[0]+"?mode=1&idGenre="+str(genreID)
        print u
        ok=True
        liz=xbmcgui.ListItem(name, iconimage, iconimage)
        liz.setInfo( type="files", infoLabels={ "Title": name } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)

def addLangues(name,langueID,iconimage):
        u=sys.argv[0]+"?mode=1&idLangue="+urllib.quote_plus(langueID)
        ok=True
        liz=xbmcgui.ListItem(name, iconimage, iconimage)
        liz.setInfo( type="files", infoLabels={ "Title": name } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)

def addSources(name,sourceID,iconimage,scrapID):
        u=sys.argv[0]+"?mode=1&idSource="+str(sourceID)
        ok=True
        liz=xbmcgui.ListItem(name, iconimage, iconimage)
        liz.setInfo( type="files", infoLabels={ "Title": name } )
        
        # ajout d'un bouton dans le contextmenu pour rafraichir l'image
        c_items = []
        deleteSource = TextLanguage.getLocalizedString(52)
        deleteSourceButton = 'XBMC.RunPlugin(%s?mode=71&idSource=%s)' % ( sys.argv[ 0 ], str(sourceID), )
        c_items.append(( deleteSource, deleteSourceButton ))
        updateSource = TextLanguage.getLocalizedString(53)
        updateSourceButton = 'XBMC.RunPlugin(%s?mode=72&idSource=%s)' % ( sys.argv[ 0 ], str(sourceID), )
        c_items.append(( updateSource, updateSourceButton ))
        if  scrapID == 1 :
            exportSource = TextLanguage.getLocalizedString(56)
            exportSourceButton = 'XBMC.RunPlugin(%s?mode=8&idSource=%s)' % ( sys.argv[ 0 ], str(sourceID), )
            c_items.append(( exportSource, exportSourceButton ))
        # replaceItems=True, seulement mon bouton va etre visible dans le contextmenu 
        # si on veut tous les boutons plus le notre on mets rien listitem.addContextMenuItems( c_items ), car False est par default
        liz.addContextMenuItems( c_items, replaceItems=True )

        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)

def addBooksList(name,mode,iconimage,isbn):
        u=sys.argv[0]+"?mode="+str(mode)+"&book="+str(isbn)
        ok=True
        liz=xbmcgui.ListItem(name, iconimage, iconimage)
        liz.setInfo( type="files", infoLabels={ "Title": name } )
        print u
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz)


def deleteSource(sourceID):
    returnBooks = DBtools.deleteSource(sourceID)
    print "source deleted successfully"
    return returnBooks

def deleteThumbs(isbn,url) :
    imgExt = url[-3:]
    imgName = "%s.%s" % (isbn, imgExt)
    imgPath = os.path.join(imgUserDir,imgName)
    os.remove(imgPath)

def updateSource(sourceID, sourceType):
    print "source updated successfully"




#INIT
#Init Parameter       

#Variable           
params = get_params()
print params
url = None
name = None
mode = None
idAuthor = None
idGenre = None
idLangue = None
idSource = None
idBook = None


#Language
TextLanguage = xbmcaddon.Addon( __addonID__ )

#Recup Parameter 
try:
        url=urllib.unquote_plus(params["url"])
except:
        pass
try:
        name=urllib.unquote_plus(params["name"])
except:
        pass
try:
        mode=int(params["mode"])
except:
        pass
try:
        idAuthor=urllib.unquote_plus(params["idAuthor"])
except:
        pass
try:
        idGenre=str(urllib.unquote_plus(params["idGenre"]))
except:
        pass
try:
        idLangue=urllib.unquote_plus(params["idLangue"])
except:
        pass
try:
        idSource=urllib.unquote_plus(params["idSource"])
except:
        pass
try:
        idBook=urllib.unquote_plus(params["book"])
except:
        pass
        
print "Mode: "+str(mode)
print "URL: "+str(url)
print "Name: "+str(name)
print "Author: "+str(idAuthor)
print "Genre: "+str(idGenre)
print "Langue: "+str(idLangue)
print "Source: "+str(idSource)
print "Book: "+str(idBook)


           
                

#LAUNCH LIST
#Default
if mode == None or mode == 0:
        print "-- MODE 0 --  MAIN" 

        addMainDir(TextLanguage.getLocalizedString(1) , 1 , titleIcon)
        addMainDir(TextLanguage.getLocalizedString(2) , 2 , authorIcon)
        addMainDir(TextLanguage.getLocalizedString(5) , 3 , genreIcon)
        addMainDir(TextLanguage.getLocalizedString(6) , 4 , langueIcon)
        addMainDir(TextLanguage.getLocalizedString(8) , 5 , sourceIcon)

else :
        #Call the Agenda Class
        DBtools = MyBooksDB()



#Liste des livres
if mode == 1:
        print "-- MODE 1 --  BOOKS TITLE"
        booksInfo = DBtools.getBooks(author=idAuthor, genre=idGenre, langue=idLangue, sources=idSource)

        for bookInfo in booksInfo :
            bookImg = "%s.%s" % (bookInfo[0], bookInfo[5][-3:])
            bookImgUrl = os.path.join(imgUserDir , bookImg)
            addBooksList(bookInfo[1] , 6 , bookImgUrl , bookInfo[0])



#Liste des Auteurs
if mode == 2:
        print "-- MODE 2 --  AUTHORS"

        authorsList = DBtools.getAuthors()

        for author in authorsList :

            addAuthors(author[1],author[0],authorIcon)



#Liste des Genres
if mode == 3:
        print "-- MODE 3 --  GENRES"

        genresList = DBtools.getStyles()

        for genreList in genresList :
            addGenres(genreList[1] , genreList[0] , genreIcon)



#Liste des Langues
if mode == 4:
        print "-- MODE 4 --  LANGUAGE"

        languesList = DBtools.getLangues()
        print languesList

        for langue in languesList :
            addLangues(langue[3] , langue[3] , langueIcon)



#Gestion des sources
if mode == 5 or mode == 51:
        print "-- MODE 5 --  SOURCES" 
        sourcesList = DBtools.getSources()
        print sourcesList
        for sourceList in sourcesList :
            addSources(sourceList[1] , sourceList[0] , langueIcon , sourceList[2])
        addMainDir(TextLanguage.getLocalizedString(51) , 51 , addIcon)

xbmcplugin.endOfDirectory(int(sys.argv[1]))


#Scripts        
if mode == 51 :
        print "-- MODE 51 --  ADD SOURCE"
        AddSource()


#Scripts        
if mode == 6 :
        print "-- MODE 6 --  DISPLAY BOOK INFO"

        bookInfo = DBtools.getBookInfo(idBook)
        DisplayInfo(bookInfo)

#DeleteSource        
if mode == 71 :
        print "-- MODE 71 --  DELETE SOURCE"

        deletedBooks = deleteSource(idSource)
        print "Livres supprimés"
        print deletedBooks
        for deletedBook in deletedBooks :
            deleteThumbs(deletedBook[0],deletedBook[1])

#DeleteSource        
if mode == 72 :
        print "-- MODE 72 --  UPDATE SOURCE"
        print "Source modifiee: " + str(idSource)
        #Init DBtools
        DBtools = MyBooksDB()
        sourceInfo = DBtools.getSourcesById(idSource)
        print sourceInfo
        #Suppression des infos existantes
        deletedBooks = deleteSource(idSource)
        print "Livres supprimés"
        print deletedBooks
        for deletedBook in deletedBooks :
            deleteThumbs(deletedBook[0],deletedBook[1])

        

        #Recup de l'id du scraper
        scrapID = sourceInfo[2]

        if scrapID == 1 :

                sourceTitle = sourceInfo[1]
                userID = sourceInfo[3]
                DBtools = MyBooksDB()
                sourceID = DBtools.addSource(sourceTitle, 1, userID)

                from LibFly import LibFlyBooks
                LibFlyBooksArray = LibFlyBooks(userID,scrapID)
                BooksArray = LibFlyBooksArray.getBooks()

                DBtools.addBooks(BooksArray,sourceID)

        if scrapID == 2 :

                sourceTitle = sourceInfo[1]
                xmlPath = sourceInfo[3]
                xmlImgPath = sourceInfo[4]
                DBtools = MyBooksDB()
                sourceID = DBtools.addSource(sourceTitle, 2, xmlPath, xmlImgPath)

                from XMLscraper import XmlBooks
                XmlBooksArray = XmlBooks(xmlPath,xmlImgPath,sourceID)
                BooksArray = XmlBooksArray.getBooks()

                DBtools.addBooks(BooksArray,sourceID)


#Export        
if mode == 8 :
        print "-- MODE 8 --  EXPORT LIB"
        print "Source modifiee: " + str(idSource)

        #Init DBtools
        DBtools = MyBooksDB()
        sourceInfo = DBtools.getSourcesById(idSource)

        xbmcDialog = xbmcgui.Dialog()
        exportBool = True

        #Define Path
        xmlDirectory = xbmcDialog.browse( 0 , TextLanguage.getLocalizedString(81) , 'files')
        xmlFile = "%s.xml" % (sourceInfo[1])
        xmlPath = os.path.join(xmlDirectory,xmlFile)
        xmlImgPath = os.path.join(xmlDirectory,"covers")

        #Verify Path
        #verify xml
        if os.path.isfile(xmlPath) :
            exportBool = xbmcDialog.yesno( TextLanguage.getLocalizedString(82) , TextLanguage.getLocalizedString(83) , TextLanguage.getLocalizedString(84))
        
        #verify image directory
        if exportBool :
            if not os.path.isdir(xmlImgPath) :
                os.mkdir(xmlImgPath)
            else :
                exportBool = xbmcDialog.yesno( TextLanguage.getLocalizedString(85) , TextLanguage.getLocalizedString(86) , TextLanguage.getLocalizedString(84))

        # Export Lib
        if exportBool :

            booksInfo = DBtools.getBooks(author=idAuthor, genre=idGenre, langue=idLangue, sources=idSource)

            xbmcProgress = xbmcgui.DialogProgress()

            xbmcProgress.create(TextLanguage.getLocalizedString(89))

            from XMLexport import XmlExport
            exportXml = XmlExport(xmlImgPath)

            for bookNum,bookInfo in enumerate(booksInfo) :

                pCount = bookNum * 100 / len(booksInfo)
                xbmcProgress.update(pCount, bookInfo[1])

                exportXml.addBooks(bookInfo)

            exportXml.exportSource(xmlPath)

            replaceBool = xbmcDialog.yesno(TextLanguage.getLocalizedString(891), TextLanguage.getLocalizedString(892))

            if replaceBool :

                #Init DBtools
                DBtools = MyBooksDB()
                sourceInfo = DBtools.getSourcesById(idSource)

                #Recup de l'id du scraper
                scrapID = sourceInfo[2]
                #Suppression des infos existantes
                deletedBooks = deleteSource(idSource)
                print "Livres supprimés"
                print deletedBooks
                for deletedBook in deletedBooks :
                   deleteThumbs(deletedBook[0],deletedBook[1])

                DBtools = MyBooksDB()
                sourceID = DBtools.addSource(sourceInfo[1], 2, xmlPath, xmlImgPath)

                from XMLscraper import XmlBooks
                XmlBooksArray = XmlBooks(xmlPath,xmlImgPath, sourceID)
                BooksArray = XmlBooksArray.getBooks()

                DBtools.addBooks(BooksArray,sourceID)
                

        else :
            xbmcDialog.ok(TextLanguage.getLocalizedString(87), TextLanguage.getLocalizedString(88))














 
