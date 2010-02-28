"""
Database Manager: this module manage Database reading, writing, browsing, download ...
"""

# Modules general
import os
import csv #TODO: import CSV/ET only if we instanciate CsvDB/XmlDB
import sys
import urllib
from traceback import print_exc

import elementtree.ElementTree as ET
from pysqlite2 import dbapi2 as sqlite

# Modules custom
import Item
from utilities import *


SPECIAL_SCRIPT_DATA = sys.modules[ "__main__" ].SPECIAL_SCRIPT_DATA

categories = {'None': 'None', 'Other': 'None', 'ThemesDir': Item.TYPE_SKIN, 'Scraper': Item.TYPE_SCRAPER, 'ThemesDir': Item.TYPE_SKIN, 'ScriptsDir': Item.TYPE_SCRIPT, 'PluginDir': Item.TYPE_PLUGIN, 'PluginMusDir': Item.TYPE_PLUGIN_MUSIC, 'PluginPictDir': Item.TYPE_PLUGIN_PICTURES, 'PluginProgDir': Item.TYPE_PLUGIN_PROGRAMS,  'PluginVidDir': Item.TYPE_PLUGIN_VIDEO }


class DBMgr:
    """
    Abstract class allowing to populate, query the DB
    """
    
    def __init__( self, db, datafile=None ):
        self.db       = db          # Database file
        self.datafile = datafile    # Data File downloaded form the server
        
        try:
            self.conn = sqlite.connect(self.db)
            
            #Init Database
            self.cursor = self.conn.cursor()
        except Exception, e:
            self.conn   = None
            self.cursor = None
            print "Exception while SQLite DB connection: %s" % datafile
            print_exc()

    def getConnectionInfo(self): 
        """
        Returns connection variables in order to interact with SQLite DB
        """
        return self.conn, self.cursor
        
    def update_datas( self ):
        """
        Get external data and populate the DB with it
        """
        if not os.path.isfile(self.db):
            #self.make_install_paths()
            self.make_Categories()
            self.update_categories()
            self.makeServer_Items()
            self.updateServerItems()
        else:
            self.update_categories()
            self.updateServerItems()
        #TODO: cursor case to deal with
        self.cursor.close
        self.cursor = None
    
    
    def nicequery( self, query ,dico ):
        """
        Replace in a query variable starting by $ with corresponding value in a dictionary
        """
        words = query.split()
    
        for indice in range(len(words)):
            
            if "$" in words[indice]:
                word = dico[words[indice]]
                try:
                    testnum = int(word)
                    arg = str(word)
                except:
                    arg = repr(word)
                query = query.replace(words[indice],arg)
                
#        print "nicequery:"
#        print query
        return query    


    def updateServerItems( self ):
        """
        Downloads from the server the list of items and update the DB
        ABSTRACT
        """
        pass
    
    def makeServer_Items( self ):
        """
        Create Server_Items table
        """
        print "makeServer_Items"
#        conn = sqlite.connect(self.db)
#        c = conn.cursor()
        try:
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS Server_Items
                            (
                            id_file int(11) primary key, 
                            date unix_timestamp, 
                            title varchar (100), 
                            description text, 
                            totaldownloads int(10), 
                            filesize int(10), 
                            filename varchar(100), 
                            fileurl varchar(100), 
                            commenttotal int(10), 
                            id_cat int(10), 
                            totalratings int(10), 
                            rating int(10), 
                            id_topic int(8), 
                            keywords varchar(100), 
                            createdate varchar(10), 
                            previewpictureurl varchar(100), 
                            version varchar(100), 
                            author varchar(100), 
                            descript_en text, 
                            script_language  varchar(100),
                            id_new varchar(5),
                            source_type  varchar(100)
                            )''')
            self.conn.commit()
        except Exception, e:
            print "Exception in makeServer_Items"
            print_exc()

    def update_categories( self ):
        """
        Update Categories table
        ABSTRACT
        """
        pass

    def make_Categories( self ):
        """
        Create Categories table
        """   
        print "make_Categories"
#        conn = sqlite.connect(self.db)
#        c = conn.cursor()
        #Creation de la table
#        c.execute ( '''CREATE TABLE IF NOT EXISTS Categories
#                        (
#                        id_cat int(8) primary key, 
#                        title varchar(100), 
#                        description text, 
#                        image varchar(100), 
#                        id_parent int(8), 
#                        id_path varchar(100)
#                        )''')
        self.cursor.execute ( '''CREATE TABLE IF NOT EXISTS Categories
                        (
                        id_cat int(8) primary key, 
                        title varchar(100), 
                        description text, 
                        image varchar(100), 
                        id_parent int(8), 
                        xbmc_type varchar(100)
                        )''')
        self.conn.commit()
        

    def exit(self):
        """
        Exit Database manager: release allocated resources
        """   
        # Close DB connection
        try:     
            self.conn.close()
        except Exception, e:
            print "DBMgr - Exception in exit"
            print_exc()
        
        
class CsvDB(DBMgr):
    """
    Populate the DB from an CSV file (HTTP server)
    """
    def __init__( self, db, datafile=None ):
        print "CsvDB - Init starts"
        DBMgr.__init__( self, db, datafile )
        print "CsvDB - importing CONF"
        import CONF
        self.baseurl = CONF.getBaseURLDownloadManager()
        del CONF
        print "CsvDB - Init done"
        
#        # Delete DB and CSV if already here
#        if os.path.isfile( self.db ):
#            os.remove( self.db )
#        if os.path.isfile( self.datafile ):
#            os.remove( self.datafile )
        
    def download_csv( self, args ):
        """
        Retrieve the CSV file form the HTTP server
        """
        
        #TODO: add the URL below in conf file instead of hardcoding it     
        # baseurl = 'http://passion-xbmc.org/exportdownloads.php/'
        url = self.baseurl + args
        print "CsvDB - retrieving " + url
        loc = urllib.URLopener()
        loc.retrieve(url, self.datafile)   
        return self.datafile  
        
    def updateServerItems( self ):
        """
        """
        print "CsvDB - CSV updateServerItems"
#        conn = sqlite.connect(self.db)
#        #Initialisation de la base de donnee
#        c = conn.cursor()
        try:
            self.cursor.execute('''SELECT max(date) FROM Server_Items''')
            args = '?action=getitems&param=%s'%self.cursor.fetchone()[0]
            self.cursor.execute('''DELETE * FROM Server_Items''')
        except:
            self.makeServer_Items()
            args = '?action=getitems'
        
        #c = conn.cursor()
        try:
            print "CsvDB - reading CSV"
            #reader = CsvUnicodeReader(open(self.download_csv(args)), delimiter = '|', encoding="cp1252")    
            reader = csv.reader(open(self.download_csv(args)),delimiter = '|')    
            
            for row in reader:
                print row
                try:
                    #on retranche l'occurs de fin de ligne
                    cols = {}
                    cols['$id_file']=row[0]
                    cols['$date']=row[1]
                    #cols['$title']=row[2]
                    #cols['$title']=unicode(row[2],"cp1252")
                    #cols['$title']=unicode(unescape( strip_off(row[2])),"cp1252")
                    #cols['$title']=adapt_str(unescape( row[2].decode("cp1252")))
                    cols['$title'] = urllib.quote( unescape( row[2] ) ) #TODO: clean THAT!!!
                    
                    print "Title"
                    print "from CSV"
                    print repr(row[2])
                    print "for DB"
                    print repr(cols['$title'])
                    #cols['$description']=row[3]
                    cols['$description'] = urllib.quote( unescape( strip_off_CSV( row[3] ) ) )
                    print repr(cols['$description'])
                    #cols['$description']=unicode(row[3],"cp1252")
                    #print "description"
                    #print cols['$description']
                    #print cols['$description'].encode("cp1252")
                    cols['$totaldownloads']=row[4]
                    cols['$filesize']=  row[5]
                    cols['$filename']=  row[6]
                    cols['$fileurl']=   row[7]
                    cols['$commenttotal']=  row[8]
                    cols['$id_cat']=row[9]
                    cols['$totalratings']=  row[10]
                    cols['$rating']=row[11]
                    cols['$type']=row[12]
                    cols['$sendemail']=row[13]
                    cols['$id_topic']=row[14]
                    cols['$keywords']=row[15]
                    cols['$createdate']=row[16]
                    cols['$previewpictureurl']=row[17]
                    cols['$version']=row[18]
                    cols['$author']=row[19]
                    cols['$descript_en']=row[20]
                    cols['$script_language']=row[21]
                    cols['$id_new']=row[22]
                    cols['$source_type']="http_passion"
        
                    self._insertServerItems(self.cursor,cols)
                except Exception, e:
                    print_exc()
        except Exception, e:
            print_exc()
                
        #Sauvegarde des modifications
        self.conn.commit()   
#        # On ferme l'instance du curseur
#        c.close()

    def _insertServerItems( self, c,cols ):
        try:
            #Chaque ligne trouvee dans le table.csv est inseree dans la table
            #c.text_factory = lambda x: unicode(x, "utf-8", "ignore")
            c.execute(self.nicequery('''INSERT INTO Server_Items 
                                        (id_file,
                                        date,
                                        title,
                                        description,
                                        totaldownloads,
                                        filesize, 
                                        filename, 
                                        fileurl, 
                                        commenttotal, 
                                        id_cat, 
                                        totalratings, 
                                        rating, 
                                        id_topic, 
                                        keywords, 
                                        createdate, 
                                        previewpictureurl, 
                                        version, 
                                        author, 
                                        descript_en, 
                                        script_language,
                                        id_new,
                                        source_type)
                                    VALUES
                                        (
                                        $id_file ,
                                        $date ,
                                        $title ,
                                        $description ,
                                        $totaldownloads ,
                                        $filesize , 
                                        $filename , 
                                        $fileurl , 
                                        $commenttotal , 
                                        $id_cat , 
                                        $totalratings , 
                                        $rating , 
                                        $id_topic , 
                                        $keywords , 
                                        $createdate , 
                                        $previewpictureurl , 
                                        $version , 
                                        $author , 
                                        $descript_en , 
                                        $script_language ,
                                        $id_new ,
                                        $source_type
                                        )
                               ''',cols))
        except Exception, e:
            print "CsvDB - Exception in _insertServerItems"
            print_exc()


    def update_categories( self ):
#        conn = sqlite.connect(self.db)
#        #Initialisation de la base de donnee
#        print "update_categories"
#        c = conn.cursor()
        try:
            self.cursor.execute('''DELETE FROM Categories''')
        except Exception, e:
            print "CsvDB - update_categories: delete failed"
            print e
            print sys.exc_info()
            print_exc()
            self.make_Categories()
        args = '?action=getcat'
        try:
            #reader = CsvUnicodeReader(open(self.download_csv(args)), delimiter = '|', encoding="cp1252")    
            reader = csv.reader(open(self.download_csv(args)),delimiter = '|')    
            #self.cursor = conn.cursor()
        
            print "CsvDB - CSV content"
            print reader
            for row in reader:
                print row
                try:
                    cols = {}
                    cols['$id_cat']=row[0]
                    cols['$title']=unescape( row[1] )
                    cols['$description']=unescape( strip_off_CSV( row[2] ) )
                    cols['$image']=row[3]
                    cols['$id_parent']= row[4]
#                    c.execute('''SELECT id_path FROM install_paths WHERE title LIKE ?''',(row[5],))
#                    cols['$id_path'] = str(c.fetchone()[0])
                    cols['$xbmc_type'] = categories[ row[5] ]
                    print "categories[ row[5] ]"
                    print categories[ row[5] ]
                    
                    self._insertCategories(self.cursor,cols)
                except Exception, e:
                    print 'erreur categorie'
                    print_exc()
        except Exception, e:
            print_exc()
            
        #Sauvegarde des modifications
        self.conn.commit()    
#        # On ferme l'instance du curseur
#        c.close()
        
    def _insertCategories( self, c, cols ):
        print "CsvDB - _insertCategories"
        print c
        print cols
        try:
            #c.text_factory = lambda x: unicode(x, "utf-8", "ignore")
#            c.execute(self.nicequery('''INSERT into Categories
#                                (                    
#                                id_cat, 
#                                title, 
#                                description, 
#                                image, 
#                                id_parent,
#                                id_path
#                                )
#                            VALUES 
#                                (
#                                $id_cat ,
#                                $title ,
#                                $description ,
#                                $image ,
#                                $id_parent ,
#                                $id_path
#                                )''',cols))
            c.execute(self.nicequery('''INSERT into Categories
                                (                    
                                id_cat, 
                                title, 
                                description, 
                                image, 
                                id_parent,
                                xbmc_type
                                )
                            VALUES 
                                (
                                $id_cat ,
                                $title ,
                                $description ,
                                $image ,
                                $id_parent ,
                                $xbmc_type
                                )''',cols))
        except Exception, e:
            print 'CsvDB - erreur insert'
            print_exc()

 