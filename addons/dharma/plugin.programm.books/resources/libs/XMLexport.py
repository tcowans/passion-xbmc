# -*- coding: utf-8 -*-
 
import re, os, sys, shutil, xbmc
from xml.dom.minidom import Document


# INITIALISATION CHEMIN RACINE
ROOTDIR = os.getcwd().replace( ";", "" )
SPECIAL_PROFILE_DIR = xbmc.translatePath( "special://profile/" )
BASE_RESOURCE_PATH = os.path.join( ROOTDIR, "resources" )

imgUserDir = os.path.join( sys.modules[ "__main__" ].SPECIAL_SCRIPT_DATA, "img" )


class XmlExport :

    def __init__(self,imgPath) :

        self.imgPath = imgPath
 
        self.doc = Document() 
        self.racine = self.doc.createElement("XMLbooks") 
        self.doc.appendChild(self.racine)
    
        #outputfile = open(xmlPath, 'wb')
        #outputfile.write(doc.toxml(encoding="UTF-8"))
        #outputfile.close()

    def getBookImg(self,url,isbn) :
        imgExt = url[-3:]
        imgName = "%s.%s" % (isbn, imgExt)
        imgPath = os.path.join(imgUserDir,imgName)
        imgExportPath = os.path.join(self.imgPath,imgName)
        shutil.copy(imgPath, imgExportPath)
        return imgName

    def addBooks(self , bookInfo) :
        print bookInfo
        
        doc = self.doc

        # Create a main <book> element
        book = self.doc.createElement("book")
        bookbal = self.racine.appendChild(book)
        
        
        # Create the book <isbn> element
        isbn = doc.createElement("isbn")
        isbnbal=bookbal.appendChild(isbn)        
        # Give the <isbn> element some text
        isbntext = doc.createTextNode(bookInfo[0])
        isbnbal.appendChild(isbntext)
        
        
        # Create the book <titre> element
        titre = doc.createElement("titre")
        titrebal=bookbal.appendChild(titre)        
        # Give the <titre> element some text
        titretext = doc.createTextNode(bookInfo[1])
        titrebal.appendChild(titretext)
        
        
        # Create the book <description> element
        description = doc.createElement("description")
        descriptionbal=bookbal.appendChild(description)        
        # Give the <description> element some text
        descriptiontext = doc.createTextNode(bookInfo[2])
        descriptionbal.appendChild(descriptiontext)
        
        
        # Create the book <langue> element
        langue = doc.createElement("langue")
        languebal=bookbal.appendChild(langue)        
        # Give the <description> element some text
        languetext = doc.createTextNode(bookInfo[3])
        languebal.appendChild(languetext)
        
        
        # Create the book <imageurl> element
        imagePath = self.getBookImg(bookInfo[5],bookInfo[0])
        imageurl = doc.createElement("imageurl")
        imageurlbal=bookbal.appendChild(imageurl)        
        # Give the <imageurl> element some text
        imageurltext = doc.createTextNode(imagePath)
        imageurlbal.appendChild(imageurltext)
        
        
        # Create the book <numpage> element
        numpage = doc.createElement("numpage")
        numpagebal=bookbal.appendChild(numpage)        
        # Give the <numpage> element some text
        numpagetext = doc.createTextNode(bookInfo[6])
        numpagebal.appendChild(numpagetext)
        
        
        # Create the book <editeur> element
        editeur = doc.createElement("editeur")
        editeurbal=bookbal.appendChild(editeur)        
        # Give the <editeur> element some text
        editeurtext = doc.createTextNode(bookInfo[8])
        editeurbal.appendChild(editeurtext)
        
        
        # Create the book <auteur> element
        auteur = doc.createElement("auteur")
        auteurbal=bookbal.appendChild(auteur)        
        # Give the <auteur> element some text
        auteurtext = doc.createTextNode(bookInfo[0])
        auteurbal.appendChild(auteurtext)
        
        
        # Create the book <genre> element
        genre = doc.createElement("genre")
        genrebal=bookbal.appendChild(genre)        
        # Give the <genre> element some text
        genretext = doc.createTextNode(bookInfo[7])
        genrebal.appendChild(genretext)
        
        
        # Create the book <date> element
        date = doc.createElement("date")
        datebal=bookbal.appendChild(date)        
        # Give the <date> element some text
        datetext = doc.createTextNode(bookInfo[9])
        datebal.appendChild(datetext)
        
        


    def exportSource(self, xmlPath):
    
        outputfile = open(xmlPath, 'wb')
        
        uglyXml = self.doc.toprettyxml(encoding="ISO-8859-1",indent='  ')

        text_re = re.compile('>\n\s+([^<>\s].*?)\n\s+</', re.DOTALL)    
        prettyXml = text_re.sub('>\g<1></', uglyXml)

        outputfile.write(prettyXml)
        outputfile.close()
