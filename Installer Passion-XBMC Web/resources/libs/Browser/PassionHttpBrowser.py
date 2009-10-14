"""
PassionHttpBrowser: this module allows browsing of server content on the web server of Passion-XBMC.org
"""


# Modules general
import os
import sys
import traceback

# Module logger
try:
    logger = sys.modules[ "__main__" ].logger
except:
    import script_log as logger
    
# SQLite
from pysqlite2 import dbapi2 as sqlite

#Other module
from threading import Thread
from pil_util import makeThumbnails
import urllib

# Modules custom
from utilities import *
import ItemInstaller  
from Browser import Browser, ImageQueueElement

    
class PassionHttpBrowser(Browser):
    """
    Browse the item on the HTTP server using only information in the Database
    """
    def __init__( self, db, *args, **kwargs  ):
        Browser.__init__( self, *args, **kwargs )
        #self.db  = kwargs[ "database" ] # Database file
        self.db = db       # Database file
        self.curList = []  # Current list of item/category

        self.currentItemId = 0
        
        # Init the root list
        # TODO: temporary here
#        self.incat(0)
        
        import CONF
        self.baseURLDownloadFile   = CONF.getBaseURLDownloadFile()
        self.baseURLPreviewPicture = CONF.getBaseURLPreviewPicture()
        del CONF

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
                
        print "nicequery:"
        print query
        return query    

    def getNextList( self, index=0 ):
        """
        Returns the list of item (dictionary) on the server depending on the location we are on the server
        Retrieves list of the items and information about each item
        Other possible name: down
        """
        # Check type of selected item
        list = []
        #TODO: manage exception
        try:            
            if ( ( len(self.curList)> 0 ) and ( self.curList[index]['type'] == 'CAT' ) ):
                # Convert index to id
                itemId = self.curList[index]['id']
                print "getNextList - index" 
                print index
                print "getNextList - itemId" 
                print itemId
            
                self.curCategory = self.curList[index]['name'] # Save the current item name as category
                list = self.incat(itemId) # Get content of the category
                self.currentItemId = itemId
            elif ( len(self.curList)<= 0 ):
                # 1st time (init), we display root list
                list = self.incat(0)
                self.curCategory = "root"
                self.currentItemId = 0
                
            else:
                # Return the current list
                #TODO: start download here?
                print "This is not a category but an item (download)"
                list = self.curList
        except Exception, e:
            print "Exception during getNextList"
            print e
            print sys.exc_info()
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )
        return list
    
    def incat( self, itemId=0):
        """
        Liste des sous-catégories et fichiers de la catégorie sélectionnée
        Renvoie un dictionnaire constitué comme suit : {id, name, parent, file,type}
        Chaque index du dictionnaire renvoie à une liste d'occurences.
        Il faut l'appeler le numéro id de la catégorie dont on veut obtenir le contenu
        Si on veut obtenir la liste des catégories racines, il alimenter la fonction avec 0 
        """
        
        listOfItems = []
        
        #Connection à la base de donnée
        conn = sqlite.connect(self.db)
        c = conn.cursor()
        #conn.text_factory = unicode
        
        
        cols = {}
        cols['$id_parent'] = str(itemId)
        
        #requete
        c.execute(self.nicequery('''SELECT id_cat, title, id_parent,'None','CAT' AS type, image, description, 'None', 'None', 'None', 'None', 'None'
                                 FROM Categories
                                 WHERE id_parent = $id_parent
                                                
                                 UNION ALL      
                                            
                                 SELECT id_file, title, id_cat,fileurl,'FIC' AS type, previewpictureurl, description, script_language, version, author, createdate, strftime('%d-%m-%Y', date, 'unixepoch')  
                                 FROM Server_Items
                                 WHERE id_cat = $id_parent
                                 ORDER BY type ASC, title ASC
                                ''',cols))
#                                 SELECT id_file, title, id_cat,fileurl,'FIC' AS type, previewpictureurl, description, script_language, version, author, createdate, date(date, 'unixepoch')  
    
                     
        #pour chaque colonne fetchée par la requête on alimente une liste, l'ensemble des  
        #listes constitue le dictionnaire
        for row in c:   
            item = {}
            item['id']                = row[0]
            #item['name']              = ( strip_off( row[1].encode("cp1252") ) )
            print 'incat: name'
            print row[1].encode("cp1252")
            print row[1].encode("cp1252").replace( r"\\", "\\" )
#            item['name']              = row[1].encode("cp1252").replace( r"\\", "\\" )
            item['name']              = row[1]
            item['parent']            = row[2]
            item['fileexternurl']     = row[3]
            item['type']              = row[4]
            item['previewpictureurl'] = row[5]
            #item['description']       = row[6].encode("cp1252") #unescape( strip_off( row[6].encode("utf8") ) )
            if (row[6] != None):
                item['description']       = unescape( strip_off( row[6].encode("utf8") ) ).replace( r"\\", "\\" )
            else:
                item['description'] = "No description" #TODO: support localization
            #item['description'] = unescape( (row[6]).encode( "cp1252" ) )
            item['language']          = row[7]
            item['version']           = row[8]
            item['author']            = row[9]
            item['date']              = row[10]
            item['added']             = row[11]
            skipItem = False # Indicate if ths item will be added to the list or not
            
            print 'HTTPBrowser::incat - previewpictureurl:'
            print item['previewpictureurl']
            if  item['previewpictureurl'] == 'None':
                if (item['type'] == 'FIC'):
                    item['thumbnail']      = "IPX-NotAvailable2.png"
                    item['previewpicture'] = "IPX-NotAvailable2.png"
                    
                elif (item['type'] == 'CAT'):
                    catTitle, catPath = self.getCategoryInfo( item['id'] )
    
                    #TODO: use var for title and image file names
                    if catTitle == "ScraperDir": #TODO replace by TYPE_SCRAPER form CONF
                        # Scraper
                        item['thumbnail']      = "IPX-defaultScraper.png" #TODO replace by THUMB_SCRAPER
                        item['previewpicture'] = "IPX-defaultScraper.png"
                    elif catTitle == "ThemesDir": #TODO replace by TYPE_SKIN form CONF
                        # Theme
                        item['thumbnail']      = "IPX-defaultSkin.png"
                        item['previewpicture'] = "IPX-defaultSkin.png"
                    elif catTitle == "ScriptsDir":
                        # Script
                        item['thumbnail']      = "IPX-defaultScript_Plugin.png"
                        item['previewpicture'] = "IPX-defaultScript_Plugin.png"
                    elif catTitle == "PluginDir":
                        # Plugin
                        item['thumbnail']      = "IPX-defaultScript_Plugin.png"
                        item['previewpicture'] = "IPX-defaultScript_Plugin.png"
                    elif catTitle == "PluginMusDir":
                        # Plugin
                        item['thumbnail']      = "IPX-defaultPluginMusic.png"
                        item['previewpicture'] = "IPX-defaultPluginMusic.png"
                    elif catTitle == "PluginPictDir":
                        # Plugin
                        item['thumbnail']      = "IPX-defaultPluginPicture.png"
                        item['previewpicture'] = "IPX-defaultPluginPicture.png"
                    elif catTitle == "PluginProgDir":
                        # Plugin
                        item['thumbnail']      = "IPX-defaultPluginProgram.png"
                        item['previewpicture'] = "IPX-defaultPluginProgram.png"
                    elif catTitle == "PluginVidDir":
                        # Plugin
                        item['thumbnail']      = "IPX-defaultScript_Plugin.png"
                        item['previewpicture'] = "IPX-defaultScript_Plugin.png"
                    else:
                        skipItem = True
            else:
                # On verifie si l'image serait deja la
                downloadImage = False
                thumbnail, checkPathPic = set_cache_thumb_name( item['previewpictureurl'] )
                if thumbnail and os.path.isfile( thumbnail ):
                    item['thumbnail'] = thumbnail
                else:
                    item['thumbnail'] = "IPX-NotAvailable2.png"
                    downloadImage = True
                    
                if os.path.exists(checkPathPic):
                    item['previewpicture'] = checkPathPic
                else:
                    item['previewpicture'] = "IPX-NotAvailable2.png"
                    downloadImage = True
                    
                if downloadImage == True:

                    # Telechargement et mise a jour de l'image (thread de separe)
                    # Ajout a de l'image a la queue de telechargement
                    #self.image_queue.append( ImageQueueElement( previewPictureURL, updateImage_cb, listitem ) )
                    self.image_queue.append( ImageQueueElement( item['previewpictureurl'] ) )
                    #TODO: dynamic update of image (right now image is not updatd in the GUI after download)
            
                
            #TODO: else case for type == 'CAT'
            if skipItem == False:
                listOfItems.append(item)
                print item
        if ( len(listOfItems) > 0 ):
            #TODO: check here
            # Clear current list if at least a value is return from the query
            self.curList[:] = listOfItems
        else:
            print "incat: resultset empty - return old list"
            
        c.close()
        print "incat current list"
        print self.curList
        print "incat listOfItems"
        print listOfItems
        return self.curList 
    
    def getPrevList( self ):
        """
        Returns the list (up) of item (dictionary) on the server depending on the location we are on the server
        Go to previous page/list 
        Other possible name: Up
        """

        # Get current categorie id 
        catId = self.curList[0]['parent']
        print "Current categorie"
        print catId
        cols = {}
        cols['$id_parent'] = str(catId)
                
        #get parent id of current parent
        conn = sqlite.connect(self.db)
        #Initialisation de la base de donnÃ©e
        c = conn.cursor()
        try:
            c.execute(self.nicequery('''SELECT id_parent 
                      FROM Categories
                      WHERE id_cat = $id_parent''',cols))
            curParentId = c.fetchone()[0]
            print "getPrevList - parent (new itemId):" 
            print curParentId
            
            curList =  self.incat(curParentId)
            self.currentItemId = curParentId
            cols2 = {}
            cols2['$id_cat'] = str(curParentId)
            c.execute(self.nicequery('''SELECT title 
                      FROM Categories
                      WHERE id_cat = $id_cat''',cols2))
            self.curCategory = c.fetchone()[0]
            
        except Exception, e:
            print "getPrevList: exception - returning list without change"
            print e
            curList = self.curList

        c.close()
        
        return curList
        
    def reloadList( self ):
        """
        Reload and returns the current list
        """
        pass
    
    def getContextMenu( self ):
        """
        Returns the list of the commands available via the context menu
        """
        pass
    
    def getCategoryInfo( self, catId ):
        """
        """
        title = ""
        path = ""
        # Connect to Database
        conn = sqlite.connect(self.db)
        c = conn.cursor()  
        try:
            c.execute('''SELECT A.title, A.path
                         FROM Install_Paths A, Categories B
                         WHERE B.id_cat = ? 
                         AND A.id_path = B.id_path
                         ''',(catId,))
        except Exception, e:
            print "getCategoryTitle: exception"
            print e
            
        for row in c:
            print row
            title = row[0].encode( "cp1252" )
            path = row[1].encode( "utf8" )
        c.close()   
        print "title = %s"%title
        print "path = %s"%path
        return title, path
       
    def getInfo( self, index ):
        """
        Returns the information about a specific item (dictionnary)
        Returns a dictionnary with the structure:
        {name, description, icon, downloads, file, created, screenshot}
        Chaque index du dictionnaire renvoie à une liste d'occurences.
        Alimenter cette fonction avec l'id du fichier dont on veut obtenir les infos.
        """
        itemId = self.curList[index]['id']
    
        #Connection à la base de donnée
        conn = sqlite.connect(self.db)
        c = conn.cursor()  
        
        try:
            c.execute('''SELECT A.id_file , 
                                A.title, 
                                A.description, 
                                A.previewpictureurl, 
                                A.totaldownloads, 
                                A.filename, 
                                A.filesize, 
                                A.createdate,
                                C.path
                         FROM Server_Items A, Categories B, Install_Paths C
                         WHERE id_file = ? 
                         AND A.id_cat = B.id_cat
                         AND B.id_path = C.id_path
                         ''',(itemId,))
        except Exception, e:
            print e
                     
        #ici une seule ligne est retournée par la requête
        #pour chaque colonne fetchée par la requête on alimente un index du dictionnaire
        dico = {}
        for row in c:
            print row
            dico['id'] = row[0]
            dico['name'] = (row[1].encode( "cp1252" ) )
            dico['description'] = unescape( row[2].encode( "cp1252" ) )
            dico['screenshot'] = row[3]
            dico['downloads'] = row[4]
            dico['filename'] = row[5]
            dico['filesize'] = row[6]
            dico['created'] = row[7]
            dico['path2download']=row[8]
        c.close()   
        return dico
    
    def _loadData ( self ):
        """
        Load the data for the current page
        """
    
    def sortByDate( self ):
        """
        Returns current list sorted by date
        """
        pass

    def sortByLang( self ):
        """
        Returns current list sorted by language
        """
        pass
    
    def sortByAuthor( self ):
        """
        Returns current list sorted by author
        """
        pass    
    

    def isCat( self, index ):
        """
        Returns True when selected item is a category
        """
        if ( ( len(self.curList)> 0 ) and ( self.curList[index]['type'] == 'CAT' ) ):
            # Convert index to id
            return True
        else:
            return False
    
    def getInstaller( self, index ):
        """
        Returns an ItemInstaller instance
        """
        try:            
            if ( ( len(self.curList)> 0 ) and ( self.curList[index]['type'] == 'FIC' ) ):
                # Convert index to id
                itemId      = self.curList[index]['id']
                catId       = self.curList[index]['parent']
                externalURL = self.curList[index]['fileexternurl'].encode('utf8')

                # Get file size
                itemInfos = self.getInfo(index)
                filesize = itemInfos['filesize']

                print "getInstaller - externalURL" 
                print externalURL
                print "getInstaller - filesize"
                print filesize
            
                type, installPath = self.getCategoryInfo( catId )
                
                # Create the right type of Installer Object
                itemInstaller = ItemInstaller.HTTPInstaller( itemId, type, installPath, filesize, externalURL )
            else:
                print "getInstaller: error impossible to install a category, it has to be an item "

        except Exception, e:
            print "Exception during getInstaller"
            print e
            print sys.exc_info()
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )
            traceback.print_exc()   
                 
        return itemInstaller

    def applyFilter( self ):
        pass


    #def _downloadImage( self, picname, listitem=None ):
    def _downloadImage( self, picname ):
        """
        Download picture from the server, save it, create the thumbnail and return path of it
        """
        print "_downloadImage %s"%picname
        try:
        
            filetodlUrl = self.baseURLPreviewPicture + picname
            print "filetodlUrl"            
            print filetodlUrl
            thumbnail, localFilePath = set_cache_thumb_name( picname )
            print thumbnail
            print localFilePath
            loc = urllib.URLopener()
            loc.retrieve(filetodlUrl, localFilePath)   

            # remove file if size is 0 bytes and report error if exists error
            if localFilePath and os.path.isfile( localFilePath ):
                if os.path.getsize( localFilePath ) <= 0:
                    os.remove( localFilePath )
                    #TODO: create a thumb for the default image?
                    #TODO: return empty and manage default image at the level of the caller
                    thumbnail = "" 
                else:
                    thumb_size = int( self.thumb_size_on_load )
                    thumbnail = makeThumbnails( localFilePath, thumbnail, w_h=( thumb_size, thumb_size ) )
                    if thumbnail == "": thumbnail = localFilePath

#            if thumbnail and os.path.isfile( thumbnail ) and hasattr( listitem, "setThumbnailImage" ):
#                listitem.setThumbnailImage( thumbnail )
            else:
                thumbnail, localFilePath = "", ""
        except:
            #import traceback; traceback.print_exc()
            logger.LOG( logger.LOG_DEBUG, "_downloadImage: Exception - Impossible to downlod the picture: %s", picname )
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )
            #TODO: create a thumb for the default image?
            #TODO: return empty and manage default image at the level of the caller
            thumbnail, localFilePath = "", "" 
        print "thumbnail = %s"%thumbnail
        print "localFilePath = %s"%localFilePath
        return thumbnail, localFilePath

    
    