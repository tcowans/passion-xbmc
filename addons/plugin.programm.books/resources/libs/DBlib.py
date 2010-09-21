# -*- coding: utf-8 -*-

import os, sys, string, xbmc

# INITIALISATION CHEMIN RACINE
ROOTDIR = os.getcwd().replace( ";", "" )

# Shared resources
RESOURCES_PATH = os.path.join( ROOTDIR, "resources" )

# INITIALISATION CHEMIN RACINE
SPECIAL_PROFILE_DIR = xbmc.translatePath( "special://profile/" )

dbDir = os.path.join( sys.modules[ "__main__" ].SPECIAL_SCRIPT_DATA )
dbPath = os.path.join(dbDir,"MyBooks.db")


# append the proper platforms folder to our path, xbox is the same as win32
#env = ( os.environ.get( "OS", "win32" ), "win32", )[ os.environ.get( "OS", "win32" ) == "xbox" ]
#sys.path.append( os.path.join( RESOURCES_PATH, "platform_libraries", env ) )
from pysqlite2 import dbapi2 as sqlite3




class MyBooksDB:
    
  def __init__(self):

    self.BooksDB = sqlite3.connect(dbPath)  # ouverture de la base

    #Création de la base de donnée    
    DBcursor = self.BooksDB.cursor()                             # obtention d'un curseur

    try :
        DBcursor.execute('''create table books (isbn VARCHAR(20) primary key , titre VARCHAR(50) , description VARCHAR(500) , langue VARCHAR(20) , bookurl VARCHAR(100) , imageurl VARCHAR(100) , numpages INTEGER , source INTEGER , editeur VARCHAR(50) , date VARCHAR(50) )''')
        DBcursor.execute('''CREATE TABLE authorsbooks (isbn VARCHAR(20) , id integer )''')
        DBcursor.execute('''CREATE TABLE authors (id INTEGER  PRIMARY KEY, name VARCHAR(50) , forname VARCHAR(50) )''')
        DBcursor.execute('''CREATE TABLE genresbooks (id  INTEGER, isbn VARCHAR(20) )''')
        DBcursor.execute('''CREATE TABLE genres (id INTEGER  PRIMARY KEY , genre VARCHAR(50) )''')
        DBcursor.execute('''CREATE TABLE sources (id INTEGER PRIMARY KEY , title VARCHAR(50) , type INTEGER, arg1 VARCHAR(50), arg2 VARCHAR(50), arg3 VARCHAR(50) )''')
    except : 
        pass

    DBcursor.close()

    
  def addBooks(self,booksArray=[],sourceID=0):
    print "sourceID " + str(sourceID)
    DBcursor = self.BooksDB.cursor()                             # obtention d'un curseur
    
    for bookInfos in booksArray :

        #Ajout des auteurs dans la base de donnée
        authors = bookInfos[7]
        authorsID = ""
            
        DBcursor.execute("SELECT * FROM books WHERE isbn =(?)" , [bookInfos[0]])

        if DBcursor.fetchall() == [] :
            print "Le livre %s n'existe pas, il va etre ajoute" % (bookInfos[1].encode("utf8"))

            for author in authors :
                author[1] = string.capitalize(author[1].lower())
                author[0] = author[0].upper()
                #Vérifie que l'auteur n'est pas dans la base
                print type(author[0])
                print type(author[1])
                DBcursor.execute("SELECT * FROM authors WHERE name =(?) AND forname =(?)" , (author[0], author[1]))
                queryReturn = DBcursor.fetchall()

                if queryReturn == [] :
                    print "L'auteur %s %s n'existe pas, il va etre ajoute" % (author[0].encode("utf8"), author[1].encode("utf8"))
                    DBcursor.execute("INSERT INTO authors VALUES  (NULL, ?, ?)", (author[0], author[1]))
                    authorsID = int(DBcursor.lastrowid)
            
                #Ajout de l'auteur
                else :
                    authorsID = queryReturn[0][0]

            genres = bookInfos[8]
            for genre in genres :
                genre = string.capitalize(genre.lower())
                #Vérifie que le genre n'est pas dans la base
                DBcursor.execute("SELECT * FROM genres WHERE genre =(?)" , [genre])
                queryReturn = DBcursor.fetchall()

                if queryReturn == [] :
                    print "Le genre %s n'existe pas, il va etre ajoute" % (genre)
                    DBcursor.execute("INSERT INTO genres VALUES  (NULL, ?)", [genre])
                    genresID = int(DBcursor.lastrowid)
            
                #Ajout de l'auteur
                else :
                    genresID = queryReturn[0][0]

            #print bookInfos[2]
            print bookInfos[2].encode("utf8")
            DBcursor.execute("INSERT INTO authorsbooks VALUES  (?, ?)", (bookInfos[0], authorsID))
            DBcursor.execute("INSERT INTO genresbooks VALUES  (?, ?)", (genresID , bookInfos[0]))
            print bookInfos[9]
            DBcursor.execute("INSERT INTO books VALUES  (?, ?, ?, ?, ?, ?, ? , ? , ? , ?)", (bookInfos[0], bookInfos[1], bookInfos[2], bookInfos[3], bookInfos[4], bookInfos[5], bookInfos[6], sourceID, bookInfos[10], bookInfos[11]))


    self.BooksDB.commit()

    DBcursor.close()


  def addSource(self, title, sourcenum, arg1="", arg2="", arg3="") :

    DBcursor = self.BooksDB.cursor()                             # obtention d'un curseur

    DBcursor.execute("INSERT INTO sources VALUES (NULL, ?, ?, ?, ?, ?)", [title , sourcenum , arg1 , arg2 , arg3])
    sourceID = int(DBcursor.lastrowid)

    self.BooksDB.commit()

    DBcursor.close()
    return sourceID

    
  def getBooks(self,author=None, genre=None, langue=None, sources=None):

    DBquery = "SELECT * FROM books ORDER BY titre"
    print author
    if langue != None :
        DBquery  = "SELECT * FROM books WHERE langue = '%s' ORDER BY titre" % (langue)

    if sources != None :
        DBquery  = "SELECT * FROM books  WHERE source = '%s' ORDER BY titre" % (sources)

    DBcursor = self.BooksDB.cursor()                             # obtention d'un curseur
    DBcursor.execute(DBquery)

    booksInfo = DBcursor.fetchall()

    if author != None :
        DBquery = "SELECT isbn FROM authorsbooks WHERE id = '%s'" % (author)
        DBcursor.execute(DBquery)
        authorBooks = DBcursor.fetchall()
        authorBooksInfo = []
        for bookInfo in booksInfo :
          for authorBook in authorBooks :
            if bookInfo[0] in authorBook :
                authorBooksInfo.append(bookInfo)
        booksInfo = authorBooksInfo

    if genre != None :
        print "le genre est "+genre
        DBquery = "SELECT isbn FROM genresbooks WHERE id = '%s'" % (int(genre))
        DBcursor.execute(DBquery)
        genreBooks = DBcursor.fetchall()
        print genreBooks 
        genreBooksInfo = []
        for bookInfo in booksInfo :
          for genreBook in genreBooks :
            if bookInfo[0] in genreBook :
                genreBooksInfo.append(bookInfo)
        booksInfo = genreBooksInfo

    DBcursor.close()
    print booksInfo
    return booksInfo

    
  def getBookInfo(self,isbn):

    DBquery = "SELECT * FROM books WHERE isbn = '%s'" % (isbn)

    DBcursor = self.BooksDB.cursor()                             # obtention d'un curseur
    DBcursor.execute(DBquery)
    bookInfo = DBcursor.fetchall()[0]
    print bookInfo
    #Infos sur l'auteur
    DBquery = "SELECT id FROM authorsbooks WHERE isbn = '%s'" % (isbn)
    DBcursor.execute(DBquery)
    Authors = DBcursor.fetchall()
    AuthorsInfo = ""
    for Author in Authors :
        idAuthor = Author[0]
        DBquery = "SELECT name,forname FROM authors WHERE id = '%s'" % (idAuthor)
        DBcursor.execute(DBquery)
        AuthorsQuery = DBcursor.fetchall()
        AuthorInfo = "%s %s" % (AuthorsQuery[0][1],AuthorsQuery[0][0])
        if not AuthorsInfo == "" :
            AuthorsInfo = AuthorsInfo + " - "
        AuthorsInfo = AuthorsInfo + AuthorInfo
    #Infos sur le genre
    DBquery = "SELECT id FROM genresbooks WHERE isbn = '%s'" % (isbn)
    DBcursor.execute(DBquery)
    genres = DBcursor.fetchall()
    genresInfo = ""
    for genre in genres :
        idGenre = genre[0]
        DBquery = "SELECT genre FROM genres WHERE id = '%s'" % (idGenre)
        DBcursor.execute(DBquery)
        GenresQuery = DBcursor.fetchall()
        genreInfo = "%s" % (GenresQuery[0][0])
        if not genresInfo == "" :
            genresInfo = genresInfo + " , "
        genresInfo = genresInfo + genreInfo
    #Infos sur la source
    DBquery = "SELECT type FROM sources WHERE id = %d" % (bookInfo[7])
    DBcursor.execute(DBquery)
    source = DBcursor.fetchall()
    print source
    sourceTitle = source[0]
    bookInfoList = list(bookInfo)
    bookInfoList[7] = sourceTitle
    bookInfo = tuple(bookInfoList)

    bookInfo = bookInfo + (AuthorsInfo,genresInfo,)

    DBcursor.close()
    return bookInfo

    
  def getAuthors(self):

    DBcursor = self.BooksDB.cursor()                             # obtention d'un curseur

    DBcursor.execute("SELECT * FROM authors ORDER BY name")

    authorsList = []
    for ligne in DBcursor:
        authorList = []
        authorList.append(ligne[0])
        authorName = ligne[2]+' '+ligne[1]
        authorList.append(authorName)

        authorsList.append(authorList)

    DBcursor.close()
    return authorsList
    
  def getStyles(self):

    DBcursor = self.BooksDB.cursor()                             # obtention d'un curseur

    returnStyles = DBcursor.execute("SELECT * FROM genres GROUP BY id ORDER BY genre").fetchall()
    return returnStyles
    
  def getLangues(self):

    DBcursor = self.BooksDB.cursor()                             # obtention d'un curseur

    returnStyles = DBcursor.execute("SELECT * FROM books GROUP BY langue ORDER BY langue")
    return returnStyles.fetchall()
    
  def getSources(self):

    DBcursor = self.BooksDB.cursor()                             # obtention d'un curseur

    returnSources = DBcursor.execute("SELECT * FROM sources")
    return returnSources.fetchall()
    
  def getSourcesById(self,idSource):

    DBcursor = self.BooksDB.cursor()                             # obtention d'un curseur

    returnSources = DBcursor.execute("SELECT * FROM sources WHERE id=?",(idSource))
    return returnSources.fetchall()[0]
    
  def deleteSource(self,idSource):

    print "Suppresion de la source n: " + str(idSource)

    returnBooks = []

    DBcursor = self.BooksDB.cursor()                             # obtention d'un curseur

    #Sélection des livres correspondant
    DBquery = "SELECT * FROM books WHERE source = %s" % (idSource)        
    DBcursor.execute(DBquery)
    sourceBooks = DBcursor.fetchall()
    print sourceBooks
    for sourceBook in sourceBooks :
        returnBook = []
        #Suppression des auteurs
        #On récupère les id des auteurs du livre
        DBquery = "SELECT * FROM authorsbooks WHERE isbn = '%s'" % (sourceBook[0])
        DBcursor.execute(DBquery)
        authorsBook = DBcursor.fetchall()
        #On vérifie pour chaque auteur qu'il n'existe pas d'autre livre
        for authorBook in authorsBook :
            DBquery = "SELECT * FROM authorsbooks WHERE id = '%s'" % (authorBook[1])
            DBcursor.execute(DBquery)
            authorBooks = DBcursor.fetchall()
            if len(authorBooks) <= 1 :
                #Suppression de l'auteur
                DBquery = "DELETE FROM authors WHERE id=%s" % (authorBook[1])
                DBcursor.execute(DBquery)
                self.BooksDB.commit()
            #Suppression du livre de la liste des auteurs
            DBquery = "DELETE FROM authorsbooks WHERE isbn='%s'" % (authorBook[0])
            DBcursor.execute(DBquery)
            self.BooksDB.commit()
        
        #Suppression des genres
        #On récupère les id des genres du livre
        DBquery = "SELECT * FROM genresbooks WHERE isbn = '%s'" % (sourceBook[0])
        DBcursor.execute(DBquery)
        genresBook = DBcursor.fetchall()
        #On vérifie pour chaque genre qu'il n'existe pas d'autre livre
        for genreBook in genresBook :
            DBquery = "SELECT * FROM genresbooks WHERE id = '%s'" % (genreBook[1])
            DBcursor.execute(DBquery)
            genreBooks = DBcursor.fetchall()
            if len(genreBooks) <= 1 :
                #Suppression de l'auteur
                DBquery = "DELETE FROM genres WHERE id = %s" % (genreBook[0])
                DBcursor.execute(DBquery)
                self.BooksDB.commit()
            #Suppression du livre de la liste des auteurs
            DBquery = "DELETE FROM genresbooks WHERE isbn='%s'" % (genreBook[1])
            DBcursor.execute(DBquery)
            self.BooksDB.commit()



        #Suppression des livres
        print "Suppresion du livre: " + str(sourceBook[0])
        DBquery = "DELETE FROM books WHERE isbn = '%s'" % (sourceBook[0])        
        returnSources = DBcursor.execute(DBquery)
        self.BooksDB.commit()
        returnBook.append(sourceBook[0])
        returnBook.append(sourceBook[5])
        returnBooks.append(returnBook)
        print returnBook
        print returnBooks

    #Suppression de la source
    DBquery = "DELETE FROM sources WHERE id = %s" % (idSource)        
    DBcursor.execute(DBquery)

    self.BooksDB.commit()
    self.BooksDB.close()

    return returnBooks


