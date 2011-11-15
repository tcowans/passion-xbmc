# -*- coding: utf-8 -*-
 
import urllib, urllib2, re, xbmc, os, sys
from elementtree import ElementTree


# INITIALISATION CHEMIN RACINE
ROOTDIR = os.getcwd().replace( ";", "" )
SPECIAL_PROFILE_DIR = xbmc.translatePath( "special://profile/" )
BASE_RESOURCE_PATH = os.path.join( ROOTDIR, "resources" )

imgUserDir = os.path.join( sys.modules[ "__main__" ].SPECIAL_SCRIPT_DATA, "img" )
if not os.path.isdir(imgUserDir) :
    os.mkdir(imgUserDir)


class LibFlyBooks :

    def __init__(self, userID, srcID) :
        self.userID = userID
        self.srcID = srcID

    def UnicodeText(self,text) :    
        if isinstance(text, unicode) :
            return text
        else :
            return unicode(text,"utf8","replace")

    def getBookImg(self,url,isbn) :
        imgExt = url[-3:]
        imgName = "%s.%s" % (isbn, imgExt)
        imgPath = os.path.join(imgUserDir,imgName)
        urllib.urlretrieve(url, imgPath)
        

    def getDesc(self,bookDesc):
        #Traitement du formulaire
        descPattern = re.compile('<div id="description">\s(.+?)</div>',re.DOTALL)
        descOutput = descPattern.search(bookDesc)

        if(descOutput != None) :
            descText = descOutput.groups()[0]
            descText = descText.replace('<span id="etc" style="display:inline;"> ...</span><div style="display:none;" id="deplidesc">','')
            descText = descText.lstrip()

            descText = re.sub('\s*<script.+?>\s*(\n\s*(.+?)*)+</script>\s*', "",descText)
            descText = re.sub("<[^>]+>", "",descText)
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

    def getUrlText(self,url) :
            f = urllib2.urlopen(url)
            urlText = f.read()
            f.close()
            return urlText

    def getBooks(self) :
            #Télécharge la liste de livre
            url = "http://www.libfly.com/Webservice/api/index.php?Service=bibliotheque&Membre=%s&Statut=all&Pagination=1" % (self.userID)
            xmlText = self.getUrlText(url)
            print xmlText

            #Nombre de xml à traiter:    
            tree = ElementTree.fromstring(xmlText)
            channel = tree.find("channel")
            infos = channel.find("infos")
            nbPage = infos.findtext("nb_page")
            print "Le nombre de pages est %s" % (nbPage)

            #Init vars
            i = 0
            Books = []

            #Get Books Infos
            for i in range(int(nbPage)) :

                i = i+1

                if i == 1 :
                    booksXmlText = xmlText

                else :
                    url = "http://www.libfly.com/Webservice/api/index.php?Service=bibliotheque&Membre=%s&Statut=all&Pagination=%d" % (self.userID,i)
                    booksXmlText = self.getUrlText(url)


                #Remplacement de media:content
                booksXmlText = booksXmlText.replace("media:content","media-content")

                #Traitement du xml
                tree = ElementTree.fromstring(booksXmlText)
                channel = tree.find("channel")
                booksItems = channel.findall("item")

                for booksItem in booksItems :
                    
                     #Get Infos from XML
                     BookISBN = booksItem.findtext("isbn")
                     BookTitre = booksItem.findtext("title").replace(";","-")
                     BookUrl = booksItem.findtext("link")
                     BookMedia = booksItem.find("media-content")
                     BookImg = BookMedia.attrib.get("url")
                     #retrieve image
                     self.getBookImg(BookImg,BookISBN)
                     print BookImg
                     #Authors array
                     BookAuthors = []
                     AuthorText = booksItem.findtext("auteur")
                     AuthorsArray = AuthorText.split(";")
                     for AuthorArray in AuthorsArray :
                         AuthorName = AuthorText.split(" ")
                         if len(AuthorName) >= 2 :
                             AuthorForname = self.UnicodeText(AuthorName[1])
                         else :
                             AuthorForname = self.UnicodeText("")
                         AuthorMainName = self.UnicodeText(AuthorName[0].replace(",",""))
                         Author = [AuthorMainName , AuthorForname]
                         BookAuthors.append(Author)
                     #Styles Array
                     Style = unicode("LibFly","utf8","replace")
                     BookStyles = []
                     BookStyles.append(Style)

                     #Get Infos from books url
                     BookInfoText = self.getUrlText(BookUrl)
                     #print self.getDesc(BookInfoText)
                     #BookDesc = unicode(self.getDesc(BookInfoText),"utf8","replace")
                     BookDesc = self.getDesc(BookInfoText)
                     #if not isinstance(BookDesc, unicode) :
                     #    BookDesc = unicode(BookDesc,"utf8","replace")
                     if isinstance(BookDesc, unicode) :
                         print "unicodedatastructure"
                     BookLang = self.getLangue(BookInfoText)
                     BookNumPages = self.getPage(BookInfoText)
                     BookEditor = self.getEditeur(BookInfoText)
                     BookDate = self.getDate(BookInfoText)
                     Book = [self.UnicodeText(BookISBN) , self.UnicodeText(BookTitre) , self.UnicodeText(BookDesc) , self.UnicodeText(BookLang) , self.UnicodeText(BookUrl) , self.UnicodeText(BookImg) , BookNumPages , BookAuthors , BookStyles , self.srcID , self.UnicodeText(BookEditor) , self.UnicodeText(BookDate)]
                     print Book
                     #Book = [unicode(BookISBN,"utf8","replace") , unicode(BookTitre,"utf8","replace") , BookDesc , unicode(BookLang,"utf8","replace") , BookUrl , unicode(BookImg,"utf8","replace") , BookNumPages , BookAuthors , BookStyles , self.srcID , BookEditor , unicode(BookDate,"utf8","replace")]
                     
                     #Book = [BookISBN , BookTitre , BookDesc , BookLang , BookUrl , BookImg , BookNumPages , BookAuthors , BookStyles , self.srcID , BookEditor , BookDate]

                     Books.append(Book)

            print Books
            return Books


