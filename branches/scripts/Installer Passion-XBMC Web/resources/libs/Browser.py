"""
Browser: this module allows browsing of server content
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


class ImageQueueElement:
    """ Structure d'un element a mettre dans la FIFO des images a telecharger """
    def __init__( self, filename, updateImage_cb=None, item=None ):
        self.filename       = filename
        self.updateImage_cb = updateImage_cb
        self.item       = item

    def __repr__( self ):
        return "(%s, %s, %s)" % ( self.filename, self.updateImage_cb, self.item )

class ItemBrowser:
    """
    This abstract class allow to browse item to download available on the server
    """
    def __init__( self, *args, **kwargs ):
        try:
            self.mainwin  = kwargs[ "mainwin" ]
            self.configManager = self.mainwin.configManager
            self.thumb_size_on_load = self.mainwin.settings[ "thumb_size" ]
        except:
            import CONF
            config = CONF.ReadConfig()
            self.configManager = CONF.configCtrl()
            del CONF
            self.thumb_size_on_load = 512

        # FIFO des images a telecharger
        self.image_queue = []
        self.curCategory = "root"
        
        self.stopUpdateImageThread = False # Flag indiquant si on doit stopper ou non le thread getImagesQueue_thread
        
    def getNextList( self, index=0 ):
        """
        Returns the list of item (dictionary) on the server depending on the location we are on the server
        Retrieves list of the items and information about each item
        Other possible name: down
        """
        pass
    
    def getPrevList( self ):
        """
        Returns the list (up) of item (dictionary) on the server depending on the location we are on the server
        Go to previous page/list 
        Other possible name: Up
        """
        pass
    
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
    
    def getInfo( self, itemId ):
        """
        Returns the information about a specific item (dictionnary)
        """
        pass
    
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
        pass
    
    def getInstaller( self, index ):
        """
        Returns an ItemInstaller instance
        """
        pass

    def applyFilter( self ):
        """
        Apply a specific filter in order to get a filtered list of item (specific author, date, ...)
        """
        pass

    def getCurrentCategory(self):
        """
        returns the current category
        """
        return self.curCategory
    
    def update_Images( self ):
        """
        Recupere toutes les image dans la FIFO et met a jour l'appelant via la callBack
        """
        #print "update_Images"
        #print self.image_queue
        if ( len(self.image_queue) > 0 ):
            self.getImagesQueue_thread = Thread( target=self._thread_getImagesQueue )
            self.getImagesQueue_thread.start()

    def cancel_update_Images(self):
        self.stopUpdateImageThread = True
        logger.LOG( logger.LOG_DEBUG,"cancel_update_Images: Stopping theard ...")

        # On attend la fin du thread
        self.getImagesQueue_thread.join(10)
        logger.LOG( logger.LOG_DEBUG,"cancel_update_Images: Thread STOPPED")
        
         # on vide la liste vide la Queue
        del self.image_queue[ : ]
        
    def imageUpdateRegister( self, listItemId, updateImage_cb=None, obj2update=None ):
        """
        Register am external graphic object needing to update the picture (listitem, image ...)
        """
        previewPictureURL   = self.curList[listItemId]['previewpictureurl']
        previewPictureLocal = self.curList[listItemId]['previewpicture']
        previewThumbLocal   = self.curList[listItemId]['thumbnail']
        if  ( previewPictureURL != 'None' and ( ( previewPictureLocal=="IPX-NotAvailable2.png"  ) or ( previewThumbLocal=="IPX-NotAvailable2.png" ) ) ):
            # We will download the picture only we we have the url and we currently have a default picture displayed
            self.image_queue.append( ImageQueueElement(previewPictureURL, updateImage_cb, obj2update ) )
    
    def _thread_getImagesQueue( self ):
        self.stopUpdateImageThread = False
        while ( len( self.image_queue ) > 0 and self.stopUpdateImageThread == False ):
            imageElt = self.image_queue.pop( 0 )
            
            # Download picture and create local Thumbnail
            thumbnail, previewPicture = self._downloadImage( imageElt.filename )
            if ( thumbnail == "" ):
                # Impossible to download picture and/or create thumb
                thumbnail = "IPX-NotAvailable2.png"

            # Notifie la callback de mettre a jour l'image
            if imageElt.updateImage_cb:
                try:
                    imageElt.updateImage_cb( thumbnail, imageElt.item )
                except TypeError:
                    logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )
                        
        if ( self.stopUpdateImageThread == True):
            logger.LOG( logger.LOG_DEBUG,"_thread_getImagesQueue CANCELLED")

    def _downloadImage( self, picname ):
        """
        Download picture from the server, save it, create the thumbnail and return path of it
        ABSTRACT
        """
        pass
    
class HTTPBrowser(ItemBrowser):
    """
    Browse the item on the HTTP server using only information in the Database
    """
    def __init__( self, db, *args, **kwargs  ):
        ItemBrowser.__init__( self, *args, **kwargs )
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
        
        
        cols = {}
        cols['$id_parent'] = str(itemId)
        
        #requete
        c.execute(self.nicequery('''SELECT id_cat, title, id_parent,'None','CAT' AS type, image, description
                                 FROM Categories
                                 WHERE id_parent = $id_parent
                                                
                                 UNION ALL      
                                            
                                 SELECT id_file, title, id_cat,fileurl,'FIC' AS type, previewpictureurl, description
                                 FROM Server_Items
                                 WHERE id_cat = $id_parent
                                 ORDER BY type ASC, title ASC
                                ''',cols))
    
                     
        #pour chaque colonne fetchée par la requête on alimente une liste, l'ensemble des  
        #listes constitue le dictionnaire
        for row in c:   
            item = {}
            item['id']                = row[0]
            item['name']              = unescape( strip_off( row[1].encode("cp1252") ) )
            item['parent']            = row[2]
            item['file']              = row[3]
            item['type']              = row[4]
            item['previewpictureurl'] = row[5]
            item['description']       = row[6].encode("cp1252") #unescape( strip_off( row[6].encode("utf8") ) )
            skipItem = False # Indicate if ths item will be added to the list or not
            
           
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
                thumbnail, checkPathPic = set_cache_thumb_name( item['previewpictureurl'] )
                if thumbnail and os.path.isfile( thumbnail ):
                    item['thumbnail'] = thumbnail
                else:
                    item['thumbnail'] = "IPX-NotAvailable2.png"
                    
                if os.path.exists(checkPathPic):
                    item['previewpicture'] = checkPathPic
                else:
                    item['previewpicture'] = "IPX-NotAvailable2.png"
#                    else:
#                        # Telechargement et mise a jour de l'image (thread de separe)
#                        previewPicture = checkPathPic #"downloading"
#                        # Ajout a de l'image a la queue de telechargement
#                        self.image_queue.append( ImageQueueElement(previewPictureURL, updateImage_cb, listitem ) )
            
                
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
            
        except e:
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
            title = row[0]
            path = row[1]
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
            dico['name'] = (row[1].encode("cp1252"))
            dico['description'] = (row[2].encode("cp1252"))
            dico['screenshot'] = row[3]
            dico['downloads'] = row[4]
            dico['file'] = row[5]
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
                itemId = self.curList[index]['id']
                catId  = self.curList[index]['parent']
                print "getInstaller - index" 
                print index
                print "getInstaller - itemId" 
                print itemId
                print "getInstaller - catId" 
                print catId
                
                # Get file size
                itemInfos = self.getInfo(index)
                filesize = itemInfos['filesize']
                print "filesize"
                print filesize
            
                type, installPath = self.getCategoryInfo( catId )
                itemInstaller = ItemInstaller.HTTPInstaller( itemId, type, installPath, filesize )
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
            thumbnail, localFilePath = set_cache_thumb_name( picname )
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

    
class FTPBrowser(ItemBrowser):
    """
    Browser FTP server using FTP command and display information about item stored in the database
    """
    def __init__(self):
        pass
    
    