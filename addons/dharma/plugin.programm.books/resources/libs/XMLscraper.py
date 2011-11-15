# -*- coding: utf-8 -*-
 
import re, os, sys, shutil, xbmc
from elementtree import ElementTree


# INITIALISATION CHEMIN RACINE
ROOTDIR = os.getcwd().replace( ";", "" )
SPECIAL_PROFILE_DIR = xbmc.translatePath( "special://profile/" )
BASE_RESOURCE_PATH = os.path.join( ROOTDIR, "resources" )

imgUserDir = os.path.join( sys.modules[ "__main__" ].SPECIAL_SCRIPT_DATA, "img" )

#imgUserDir = os.path.join( "XmlBook", "img" )

if not os.path.isdir(imgUserDir) :
    os.mkdir(imgUserDir)


class XmlBooks :

    def __init__(self, xmlPath,imgPath, srcID,actorPath=None) :
        self.xmlPath = xmlPath
        self.imgPath = imgPath
        self.srcID = srcID
        #self.actorPath = actorPath

    def UnicodeText(self,text) :    
        if text :
            if isinstance(text, unicode) :
                return text
            else :
                return unicode(text,"utf8","replace")
        else :
            return unicode("")

    def getBookImg(self,url,isbn) :
        imgExt = url[-3:]
        imgName = "%s.%s" % (isbn, imgExt)
        imgPath = os.path.join(imgUserDir,imgName)
        shutil.copy(url, imgPath)
        

    def getDesc(self,bookDesc):
        #Traitement du formulaire
        descPattern = re.compile('<div id="description">\s(.+?)</div>',re.DOTALL)
        descOutput = descPattern.search(bookDesc)

        if(descOutput != None) :
            descText = descOutput.groups()[0]
            descText = descText.replace('<span id="etc" style="display:inline;"> ...</span><div style="display:none;" id="deplidesc">','')
            descText = descText.lstrip()
            descText = descText.decode('ISO-8859-1')
            return descText

        else :
            return  ""

    def getPage(self,urlText):
        #Traitement du formulaire
        pagePattern = re.compile('<div class="poche">.+?([0-9]+).+?</span>')
        searchOutput = pagePattern.search(urlText)

        if(searchOutput != None) :
            searchText = searchOutput.groups()[0]
            return searchText

        else :
            return  ""

    def getLangue(self,urlText):
        #Traitement du formulaire
        languePattern = re.compile('<div class="annee">\s.+?<span class=\'strong\'>(.+?)</span>')
        searchOutput = languePattern.search(urlText)

        if(searchOutput != None) :
            searchText = searchOutput.groups()[0]
            return searchText

        else :
            return  ""

    def getEditeur(self,urlText):
        #Traitement du formulaire
        editeurPattern = re.compile('<div class="editeur">.+?<span class=\'strong\'>\s*(.*)\s')
        searchOutput = editeurPattern.search(urlText)

        if(searchOutput != None) :
            searchText = searchOutput.groups()[0]
            searchText = searchText.decode('ISO-8859-1')
            return searchText.rstrip()

        else :
            return  ""

    def getDate(self,urlText):
        #Traitement du formulaire
        datePattern = re.compile('<div class="langue">.+?<span class=\'strong\'>\s(.+?)</span>')
        searchOutput = datePattern.search(urlText)

        if(searchOutput != None) :
            searchText = searchOutput.groups()[0]
            return searchText

        else :
            return ""

    def getBooks(self) :

            Books = []
            #ouverture du xml
            print self.xmlPath
            tree = ElementTree.parse(self.xmlPath)
            #récupération des noeuds "book"
            booksItems = tree.findall("book")






            for booksItem in booksItems :
                     print booksItem
                    
                     #Get Infos from XML
                     BookISBN = booksItem.findtext("isbn")
                     BookTitre = booksItem.findtext("titre")
                     BookUrl = ""
                     BookImg = booksItem.findtext("imageurl")
                     #retrieve image
                     BookImg = os.path.join(self.imgPath,BookImg)
                     self.getBookImg(BookImg,BookISBN)
                     #Authors array
                     BookAuthors = []
                     AuthorText = booksItem.findtext("auteur")
                     AuthorsArray = AuthorText.split(" - ")
                     for AuthorArray in AuthorsArray :
                         AuthorName = AuthorText.split(" ")
                         if len(AuthorName) >= 2 :
                             if isinstance(AuthorName[1], unicode) :
                                 AuthorForname = AuthorName[1]
                             else :
                                 AuthorForname = unicode(AuthorName[1],"utf8","replace")
                         else :
                             AuthorForname = ""
                         AuthorName[0] = AuthorName[0].replace(",","")
                         if isinstance(AuthorName[0], unicode) :
                             AuthorMainName = AuthorName[0]
                         else :
                             AuthorMainName = unicode(AuthorName[0],"utf8","replace")
                         Author = [AuthorMainName , AuthorForname]
                         BookAuthors.append(Author)
                     #Styles Array
                     BookStyles = []
                     StylesText = booksItem.findtext("genre")
                     BookStyles = StylesText.split(" - ")
                     #BookDesc = unicode(self.getDesc(BookInfoText),"utf8","replace")
                     BookDesc = booksItem.findtext("description")
                     BookLang = booksItem.findtext("langue")
                     BookNumPages = booksItem.findtext("numpage")
                     BookEditor = booksItem.findtext("editeur")
                     BookDate = booksItem.findtext("date")
                     #print BookISBN , BookTitre , BookDesc , BookLang , BookUrl , BookImg , BookNumPages , BookAuthors , BookStyles , self.srcID , BookEditor , BookDate
                     Book = [self.UnicodeText(BookISBN) , self.UnicodeText(BookTitre) , self.UnicodeText(BookDesc) , self.UnicodeText(BookLang) , self.UnicodeText(BookUrl) , self.UnicodeText(BookImg) , BookNumPages , BookAuthors , BookStyles , self.srcID , self.UnicodeText(BookEditor) , self.UnicodeText(BookDate)]

                     Books.append(Book)
            return Books
