"""
Database Manager: this module manage Database reading, writing, browsing, download ...
"""

# Modules general
import os
import sys
import urllib
import ftplib
import traceback

#module logger
try:
    logger = sys.modules[ "__main__" ].logger
except:
    import script_log as logger

# Modules custom
import Item
from utilities import *
#from CONSTANTS import *

ROOTDIR = sys.modules[ "__main__" ].ROOTDIR
SPECIAL_SCRIPT_DATA = sys.modules[ "__main__" ].SPECIAL_SCRIPT_DATA

#DB = os.path.join(SPECIAL_SCRIPT_DATA, 'Passion_XBMC_Installer.sqlite')
#result = os.path.join(SPECIAL_SCRIPT_DATA, 'table.csv')


# SQLite
from pysqlite2 import dbapi2 as sqlite

#TODO: import CSV/ET only if we instanciate CsvDB/XmlDB
import csv
import elementtree.ElementTree as ET

categories = {'None': 'None', 'Other': Item.TYPE_SCRAPER, 'ThemesDir': Item.TYPE_SKIN, 'ScraperDir': Item.TYPE_SCRAPER, 'ThemesDir': Item.TYPE_SKIN, 'ScriptsDir': Item.TYPE_SCRIPT, 'PluginDir': Item.TYPE_PLUGIN, 'PluginMusDir': Item.TYPE_PLUGIN_MUSIC, 'PluginPictDir': Item.TYPE_PLUGIN_PICTURES, 'PluginProgDir': Item.TYPE_PLUGIN_PROGRAMS,  'PluginVidDir': Item.TYPE_PLUGIN_VIDEO }
    
class DBMgr:
    """
    Abstract class allowing to populate, query the DB
    """
    
    def __init__( self, db, datafile=None ):
        self.db       = db          # Database file
        self.datafile = datafile    # Data File downloaded form the server
        
#        try:
#            self.conn = sqlite.connect(DB)
#            
#            #Init Database
#            c = conn.cursor()
#        except:
#            logger.LOG( logger.LOG_DEBUG, "Exception while SQLite DB connection: %s", datafile )
#            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )

        
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
        conn = sqlite.connect(self.db)
        c = conn.cursor()
        try:
            c.execute('''CREATE TABLE IF NOT EXISTS Server_Items
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
            conn.commit()
        except Exception, e:
            print "Exception in makeServer_Items"
            print e        

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
        conn = sqlite.connect(self.db)
        c = conn.cursor()
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
        c.execute ( '''CREATE TABLE IF NOT EXISTS Categories
                        (
                        id_cat int(8) primary key, 
                        title varchar(100), 
                        description text, 
                        image varchar(100), 
                        id_parent int(8), 
                        xbmc_type varchar(100)
                        )''')
        conn.commit()
        
#    def make_install_paths( self ):
#    
#        conn = sqlite.connect(self.db)
#        c = conn.cursor()
#    
##        c.execute ( '''CREATE TABLE IF NOT EXISTS Install_Paths
##                        (
##                        id_path integer primary key autoincrement, 
##                        title varchar(100), 
##                        path varchar(100)
##                        )''')
#        c.execute ( '''CREATE TABLE IF NOT EXISTS Install_Paths
#                        (
#                        id_path integer primary key autoincrement, 
#                        title varchar(100), 
#                        )''')
#        conn.commit()
#        
#        import CONF
#        Path = CONF.GetInstallPaths()
#        del CONF
#        
#        print Path
#        
#        for ind in range(len(Path['title'])):
#            path = {}
#            path['$title'] = Path['title'][ind]
#            #path['$path'] = Path['path'][ind]
#            print path['$title']
##            print path['$path']
##            c.execute(self.nicequery('''INSERT INTO Install_Paths 
##                        (
##                        title,
##                        path
##                        )
##                        VALUES
##                        (
##                        $title ,
##                        $path
##                        ) ''',path))
#            c.execute(self.nicequery('''INSERT INTO Install_Paths 
#                        (
#                        title,
#                        )
#                        VALUES
#                        (
#                        $title ,
#                        ) ''',path))
#        conn.commit()
#        c.close      
        
        
        
class CsvDB(DBMgr):
    """
    Populate the DB from an CSV file (HTTP server)
    """
    def __init__( self, db, datafile=None ):
        print "Init starts"
        DBMgr.__init__( self, db, datafile )
        print "importing CONF"
        import CONF
        self.baseurl = CONF.getBaseURLDownloadManager()
        del CONF
        print "Init done"
        
    def download_csv( self, args ):
        """
        Retrieve the CSV file form the HTTP server
        """
        
        #TODO: add the URL below in conf file instead of hardcoding it     
        # baseurl = 'http://passion-xbmc.org/exportdownloads.php/'
        url = self.baseurl + args
        print "retrieving " + url
        loc = urllib.URLopener()
        loc.retrieve(url, self.datafile)   
        return self.datafile  
    
    def updateServerItems( self ):
        """
        """
        print "CSV updateServerItems"
        conn = sqlite.connect(self.db)
        #Initialisation de la base de donnee
        c = conn.cursor()
        try:
            c.execute('''SELECT max(date) FROM Server_Items''')
            args = '?action=getitems&param=%s'%c.fetchone()[0]
            c.execute('''DELETE * FROM Server_Items''')
        except:
            self.makeServer_Items()
            args = '?action=getitems'
        
        c = conn.cursor()
        try:
            print "reading CSV"
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
                    cols['$title']=unescape( row[2] )
    
                    print "Title"
                    print "from CSV"
                    print repr(row[2])
                    print "for DB"
                    print repr(cols['$title'])
                    #cols['$description']=row[3]
                    cols['$description']=unescape( strip_off_CSV( row[3] ) )
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
        
                    self._insertServerItems(c,cols)
                except Exception, e:
                    print e
                    traceback.print_exc()
        except Exception, e:
            print e
            traceback.print_exc()
                
        #Sauvegarde des modifications
        conn.commit()   
        # On ferme l'instance du curseur
        c.close()

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
            print "Exception in _insertServerItems"
            print e     
            traceback.print_exc()

#    def _insertServerItems( self, c,cols ):
#        try:
#            #Chaque ligne trouvee dans le table.csv est inseree dans la table
#            c.execute(self.nicequery('''INSERT INTO Server_Items
#                                        (id_file,
#                                        date,
#                                        title,
#                                        description,
#                                        totaldownloads,
#                                        filesize, 
#                                        filename, 
#                                        fileurl, 
#                                        commenttotal, 
#                                        id_cat, 
#                                        totalratings, 
#                                        rating, 
#                                        id_topic, 
#                                        keywords, 
#                                        createdate, 
#                                        previewpictureurl, 
#                                        version, 
#                                        author, 
#                                        descript_en, 
#                                        script_language,
#                                        id_new,
#                                        source_type)
#                                    VALUES
#                                        (
#                                        $id_file ,
#                                        $date ,
#                                        $title ,
#                                        $description ,
#                                        $totaldownloads ,
#                                        $filesize ,
#                                        $filename ,
#                                        $fileurl ,
#                                        $commenttotal ,
#                                        $id_cat ,
#                                        $totalratings ,
#                                        $rating ,
#                                        $id_topic 
#                                        $keywords ,
#                                        $createdate ,
#                                        $previewpictureurl ,
#                                        $version ,
#                                        $author ,
#                                        $description ,
#                                        $script_language ,
#                                        $id_new ,
#                                        $source_type
#                                        )
#                               ''',cols))
#        except Exception, e:
#            print "Exception in _insertServerItems"
#            print e     

    def update_categories( self ):
        conn = sqlite.connect(self.db)
        #Initialisation de la base de donnee
        print "update_categories"
        c = conn.cursor()
        try:
            c.execute('''DELETE FROM Categories''')
        except Exception, e:
            print "update_categories: delete failed"
            print e
            print sys.exc_info()
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )
            self.make_Categories()
        args = '?action=getcat'
        try:
            #reader = CsvUnicodeReader(open(self.download_csv(args)), delimiter = '|', encoding="cp1252")    
            reader = csv.reader(open(self.download_csv(args)),delimiter = '|')    
            c = conn.cursor()
        
            print "CSV content"
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
                    
                    self._insertCategories(c,cols)
                except Exception, e:
                    print 'erreur categorie'
                    print e
                    traceback.print_exc()
        except Exception, e:
            print e
            traceback.print_exc()
            
        #Sauvegarde des modifications
        conn.commit()    
        # On ferme l'instance du curseur
        c.close()
        
    def _insertCategories( self, c, cols ):
        print "_insertCategories"
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
            print 'erreur insert'
            print e
            traceback.print_exc()


    
class XmlDB(DBMgr):
    """
    Populate the DB from an XML file (FTP server)
    """
    def __init__( self, db, datafile ):
        print "Init strats"
        DBMgr.__init__( self, db, datafile=None )
        
        from CONF import configCtrl
        self.configManager = configCtrl()
        if not self.configManager.is_conf_valid: raise

        self.srvHost            = self.configManager.host
        self.srvPassword        = self.configManager.password
        self.srvUser            = self.configManager.user
        self.srvItemDescripDir  = self.configManager.itemDescripDir
        self.srvItemDescripFile = self.configManager.itemDescripFile

        logger.LOG( logger.LOG_DEBUG,"XmlDB starts")

#        # On recupere le fichier de description des items
#        self._downloadFile( self.srvItemDescripDir + self.srvItemDescripFile, isTBN=False )
#
#        self.parse_xml_sections()
#        
#        self.stopUpdateImageThread = False # Flag indiquant si on doit stopper ou non le thread getImagesQueue_thread
        print "Init done"
        
    def download_xml( self ):
        """
        Retrieve the XML file form the FTP server
        """
        
        try:
            filetodlUrl   = self.srvItemDescripDir + self.srvItemDescripFile
            if self.datafile != None:
                localFilePath = self.datafile
            else:
                localFilePath = os.path.join( SPECIAL_SCRIPT_DATA, os.path.basename( filetodlUrl ) )

            ftp = ftplib.FTP( self.srvHost, self.srvUser, self.srvPassword )
            localFile = open( localFilePath, "wb" )
            try:
                ftp.retrbinary( 'RETR ' + filetodlUrl, localFile.write )
            except:
                #import traceback; traceback.print_exc()
                logger.LOG( logger.LOG_DEBUG, "_downloaddossier: Exception - Impossible de telecharger le fichier: %s", filetodlUrl )
                logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )
                localFilePath = ""
            localFile.close()
            ftp.quit()

        except:
            #import traceback; traceback.print_exc()
            logger.LOG( logger.LOG_DEBUG, "_downloaddossier: Exception - Impossible de telecharger le fichier: %s", filetodlUrl )
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )
        
        return localFilePath  

    
    def updateServerItems( self ):
        """
        """
        pass
#        print "CSV updateServerItems"
#        conn = sqlite.connect(self.db)
#        #Initialisation de la base de donnee
#        c = conn.cursor()
#        try:
#            c.execute('''SELECT max(date) FROM Server_Items''')
#            args = '?action=getitems&param=%s'%c.fetchone()[0]
#            c.execute('''DELETE * FROM Server_Items''')
#        except:
#            self.makeServer_Items()
#            args = '?action=getitems'
#        
#        c = conn.cursor()
#        reader = csv.reader(open(self.download_csv(args)),delimiter = '|')    
#        
#        for row in reader:
#            print row
#            try:
#                #on retranche l'occurs de fin de ligne
#                cols = {}
#                cols['$id_file']=row[0]
#                cols['$date']=row[1]
#                cols['$title']=row[2]
#                cols['$description']=row[3]
#                cols['$totaldownloads']=row[4]
#                cols['$filesize']=  row[5]
#                cols['$filename']=  row[6]
#                cols['$fileurl']=   row[7]
#                cols['$commenttotal']=  row[8]
#                cols['$id_cat']=row[9]
#                cols['$totalratings']=  row[10]
#                cols['$rating']=row[11]
#                cols['$type']=row[12]
#                cols['$sendemail']=row[13]
#                cols['$id_topic']=row[14]
#                cols['$keywords']=row[15]
#                cols['$createdate']=row[16]
#                cols['$previewpictureurl']=row[17]
#                cols['$version']=row[18]
#                cols['$author']=row[19]
#                cols['$description_en']=row[20]
#                cols['$script_language']=row[21]
#                cols['$id_new']=row[22]
#                cols['$source_type']="http_passion"
#    
#                self._insertServerItems(c,cols)
#            except Exception, e:
#                print e
#                
#        #Sauvegarde des modifications
#        conn.commit()   
#        # On ferme l'instance du curseur
#        c.close()

    def _insertServerItems( self, c,cols ):
        try:
            #Chaque ligne trouvee dans le table.csv est inseree dans la table
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
                                        $description , 
                                        $script_language ,
                                        $id_new ,
                                        $source_type
                                        )
                               ''',cols))
        except Exception, e:
            print "Exception in _insertServerItems"
            print e     

    def update_categories( self ):
        conn = sqlite.connect(self.db)
        #Initialisation de la base de donnee
        c = conn.cursor()
        try:
            c.execute('''DELETE * FROM Categories''')
        except:
            print "update_categories: delete failed"
            self.make_Categories()
              
        #TODO: Use localization for name
        catNameList = ["skins", "scripts", "scrapers", "videoplugin", "musicplugin", "pictureplugin", "programplugin"]
        catIdList = [10001, 10002, 10003, 10004, 10005, 10006, 10007]
        catIdParentList = [0, 0, 0, 0, 0, 0, 0]
        catInstallPatth = ["ThemesDir", "ScriptsDir", "scraperdir", "PluginVidDir", "PluginMusDir", "PluginPictDir", "PluginProgDir"]
                
        for name in catNameList:
            print name
            try:
                index = catNameList.index(name)
                cols = {}
                cols['$id_cat']= catIdList[index]
                cols['$title']= name
                cols['$description']="None"
                cols['$image']="None"
                cols['$id_parent']= catIdParentList[index]
                print "row[5] = %s"%catInstallPatth[index]
                c.execute('''SELECT id_path FROM install_paths WHERE title LIKE ?''',(catInstallPatth[index],))
                cols['$id_path'] = str(c.fetchone()[0])
                print "cols['$id_path'] = " 
                print cols['$id_path']  
                    
                
                self._insertCategories(c,cols)
            except Exception, e:
                print 'erreur update_categories (XML)'
                print e
            
        #Sauvegarde des modifications
        conn.commit()    
        # On ferme l'instance du curseur
        c.close()

        
    def _insertCategories( self, c, cols ):
        try:
            c.execute(self.nicequery('''INSERT into Categories
                                (                    
                                id_cat, 
                                title, 
                                description, 
                                image, 
                                id_parent,
                                id_path
                                )
                            VALUES 
                                (
                                $id_cat ,
                                $title ,
                                $description ,
                                $image ,
                                $id_parent ,
                                $id_path
                                )''',cols))
        except Exception, e:
            print 'erreur insert'
            print e

    def parse_xml_sections( self ):
        elems = ET.parse( open( os.path.join( self.configManager.CACHEDIR, self.srvItemDescripFile ), "r" ) ).getroot()

        self.cat_skins         = elems.find( "skins" ).findall( "entry" )
        self.cat_scripts       = elems.find( "scripts" ).findall( "entry" )
        self.cat_scrapers      = elems.find( "scrapers" ).findall( "entry" )

        elems = elems.find( "plugins" )
        self.cat_videoplugin   = elems.find( "videoplugin" ).findall( "entry" )
        self.cat_musicplugin   = elems.find( "musicplugin" ).findall( "entry" )
        self.cat_pictureplugin = elems.find( "pictureplugin" ).findall( "entry" )
        self.cat_programplugin = elems.find( "programplugin" ).findall( "entry" )

        del elems

    def getInfo( self, itemName=None, itemType=None, itemId=None, updateImage_cb=None, listitem=None ):
        self.check_thumb_size()
        """
        Lit les info
        retourne fileName, title, version, language, date , previewPicture, previewVideoURL, description_fr, descript_en
        Fonction abstraite
        """
        """ reads info """
        fileName        = itemName # default value if we don't find itemname
        title           = itemName # default value if we don't find itemname
        #version         = None
        #language        = None
        #date            = None
        #added           = None
        #previewPicture  = None
        #thumbnail       = ""
        #previewVideoURL = None
        #description_fr  = None
        #descript_en  = None
        #author          = None

        try:
            category = None
            if   itemType == "Themes":             category = self.cat_skins
            elif itemType == "Scripts":            category = self.cat_scripts
            elif itemType == "Scrapers":           category = self.cat_scrapers
            elif itemType == "Plugins Videos":     category = self.cat_videoplugin
            elif itemType == "Plugins Musique":    category = self.cat_musicplugin
            elif itemType == "Plugins Images":     category = self.cat_pictureplugin
            elif itemType == "Plugins Programmes": category = self.cat_programplugin

            notfound = True
            if category:
                for item in category:
                    filename_raw = item.findtext("fileName")
                    if filename_raw:
                        fileName = filename_raw
                        if ( itemName == fileName ):
                            title             = item.findtext( "title" ) or title
                            version           = item.findtext( "version" )
                            language          = item.findtext( "lang" )
                            date              = item.findtext( "date" )
                            added             = item.findtext( "added" )
                            previewVideoURL   = item.findtext( "previewVideoURL" )
                            description_fr    = item.findtext( "description_fr" )
                            description_en    = item.findtext( "descript_en" )
                            author            = item.findtext( "author" )

                            previewPictureURL = item.findtext( "previewPictureURL" )
                            if not previewPictureURL and hasattr( listitem, "setThumbnailImage" ):
                                listitem.setThumbnailImage( "IPX-NotAvailable2.png" )
                            elif previewPictureURL:
                                # On verifie si l'image serait deja la
                                thumbnail, checkPathPic = set_cache_thumb_name( previewPictureURL )
                                if thumbnail and os.path.isfile( thumbnail ) and hasattr( listitem, "setThumbnailImage" ):
                                    listitem.setThumbnailImage( thumbnail )
                                if os.path.exists(checkPathPic):
                                    previewPicture = checkPathPic
                                else:
                                    # Telechargement et mise a jour de l'image (thread de separe)
                                    previewPicture = checkPathPic#"downloading"
                                    # Ajout a de l'image a la queue de telechargement
                                    #self._getImage( previewPictureURL, updateImage_cb=updateImage_cb, listitem=listitem )
                                    self.image_queue.append( ImageQueueElement(previewPictureURL, updateImage_cb, listitem ) )
                            notfound = False
                            break

            if notfound and hasattr( listitem, "setThumbnailImage" ):
                listitem.setThumbnailImage( "IPX-NotAvailable2.png" )

            #i = updateIWH( locals() )
            #print i.fileName, i.description
        except:
            #import traceback; traceback.print_exc()
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )

        return updateIWH( locals() )
        #return fileName, title, version, language, date, added, previewPicture, \
        #    previewVideoURL, description_fr, description_en, thumbnail, author
    