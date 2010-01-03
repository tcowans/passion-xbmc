"""
PassionHttpBrowser: this module allows browsing of server content on the web server of Passion-XBMC.org
"""

# Modules general
import os
import sys
import urllib
from threading import Thread
from traceback import print_exc

from pysqlite2 import dbapi2 as sqlite

# Modules custom 
import Item
from utilities import *
#from CONSTANTS import *
import PassionHttpItemInstaller 
from pil_util import makeThumbnails
from Browser import Browser, ImageQueueElement


#FONCTION POUR RECUPERER LES LABELS DE LA LANGUE.
_ = sys.modules[ "__main__" ].__language__
LANGUAGE_IS_FRENCH = sys.modules[ "__main__" ].LANGUAGE_IS_FRENCH

SPECIAL_SCRIPT_DATA = sys.modules[ "__main__" ].SPECIAL_SCRIPT_DATA
DIR_CACHE = sys.modules[ "__main__" ].DIR_CACHE
#CACHEDIR = os.path.join( ROOTDIR, "cache" )


class PassionHttpBrowser(Browser):
    """
    Browse the item on the HTTP server using only information in the Database
    """
    def __init__( self, *args, **kwargs  ):
        Browser.__init__( self, *args, **kwargs )
        #self.db  = kwargs[ "database" ] # Database file


        import CONF
        #TODO: check if we still need those vars
        self.baseURLDownloadFile   = CONF.getBaseURLDownloadFile()
        self.baseURLPreviewPicture = CONF.getBaseURLPreviewPicture()
        del CONF

        import DBManager
        print "Creating DBMgr"
        # Creating DB form CSV file from the server
        #self.db = os.path.join(SPECIAL_SCRIPT_DATA, 'Passion_XBMC_Installer.sqlite')  # Database file
        #csvFile = os.path.join(SPECIAL_SCRIPT_DATA, 'table.csv')
        self.db = os.path.join(DIR_CACHE, 'Passion_XBMC_Installer.sqlite')  # Database file
        csvFile = os.path.join(DIR_CACHE, 'table.csv')
        
        self.databaseMgr = DBManager.CsvDB( self.db, csvFile )
        self.databaseMgr.update_datas()
        self.conn, cursor = self.databaseMgr.getConnectionInfo() #TODO: move DBManager in the http browser (no interest to have it separated with current design)

        print "update_datas"
        
        #self.db = db      
        self.curList = []  # Current list of item/category

        self.currentItemId = 0
        
        # Init the root list
        # TODO: temporary here
#        self.incat(0)
        

    def reset( self ):
        """
        Reset the browser (back to start page)
        """
        self.curList       = []  
        self.currentItemId = 0

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
                self.currentItemId = itemId #TODO: current categoryID??? instead
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
            print_exc()
            print_exc()   
        return list
    
    def incat( self, itemId=0):
        """
        List sub categories and files for the specified category
        Returns a dictionary with the format: {id, name, parent, file,type}
        """
        
        listOfItems = []
        
        #Connection à la base de donnee
#        conn = sqlite.connect(self.db)
        c = self.conn.cursor()
        #conn.text_factory = unicode
        
        
        cols = {}
        cols['$id_parent'] = str(itemId)
        
        #requete
        self.conn.text_factory = sqlite.OptimizedUnicode
        c.execute(self.nicequery('''SELECT id_cat, title, id_parent,'None','CAT' AS type, image, description, 'None', 'None', 'None', 'None', 'None', 'None'
                                 FROM Categories
                                 WHERE id_parent = $id_parent
                                                
                                 UNION ALL      
                                            
                                 SELECT id_file, title, id_cat,fileurl,'FIC' AS type, previewpictureurl, description, descript_en, script_language, version, author, createdate, strftime('%d-%m-%Y', date, 'unixepoch')  
                                 FROM Server_Items
                                 WHERE id_cat = $id_parent
                                 ORDER BY type ASC, title ASC
                                ''',cols))
#                                 SELECT id_file, title, id_cat,fileurl,'FIC' AS type, previewpictureurl, description, script_language, version, author, createdate, date(date, 'unixepoch')  
    
                     
        #pour chaque colonne fetchee par la requête on alimente une liste, l'ensemble des  
        #listes constitue le dictionnaire
        for row in c:   
            item = {}
            item['id']                = row[0]
            item['name']              = row[1].encode("cp1252").decode('string_escape')
            item['parent']            = row[2]
            item['fileexternurl']     = row[3].decode('string_escape')
            item['type']              = row[4].decode('string_escape')
            item['previewpictureurl'] = row[5].decode('string_escape')
            #item['description']       = row[6].encode("cp1252") #unescape( strip_off( row[6].encode("utf8") ) )
            print "################ Description"
            print row[6].encode("cp1252").decode('string_escape')
            print row[7].encode("cp1252").decode('string_escape')
            
            if LANGUAGE_IS_FRENCH:
                item['description']       = row[6].encode("cp1252").decode('string_escape')
            else:
                #item['description']       = urllib.unquote( row[7].encode("cp1252").decode('string_escape') )
                item['description']       = row[7].encode("cp1252").decode('string_escape')
            if item['description'] == 'None':
                item['description'] = _( 604 ) 
            #item['description'] = unescape( (row[6]).encode( "cp1252" ) )
            item['language']          = row[8]
            item['version']           = row[9]
            item['author']            = row[10]
            item['date']              = row[11]
            item['added']             = row[12]
            item['image2retrieve']    = False # Temporary patch for reseting the flag after download (would be better in the thread in charge of the download)
            skipItem = False # Indicate if this item will be added to the list or not
            
            print 'HTTPBrowser::incat - previewpictureurl:'
            print item['previewpictureurl']
            if  item['previewpictureurl'] == 'None':
                if (item['type'] == 'FIC'):
                    #item['thumbnail']      = Item.THUMB_NOT_AVAILABLE
                    #TODO: have different icon between cat and item without thumb
                    parentTitle, xbmc_type = self.getCategoryInfo( item['parent'] )
                    item['xbmc_type']      = xbmc_type
                    item['thumbnail']      = Item.get_thumb( item['xbmc_type'] )
                    item['previewpicture'] = ""#Item.THUMB_NOT_AVAILABLE
                    
                elif (item['type'] == 'CAT'):
                    catTitle, catType = self.getCategoryInfo( item['id'] )
                    item['xbmc_type'] = catType
                    #TODO: use var for title and image file names
                    #TODO:                     
                        #item['thumbnail']      = Item.get_thumb( catType )
                        #item['previewpicture'] = Item.get_thumb( catType )
                        # Be careful with limit case (i.e skip case)
                    if catType == Item.TYPE_SCRAPER: 
                        # Scraper
                        #item['thumbnail']      = "IPX-defaultScraper.png" #TODO replace by THUMB_SCRAPER
                        #item['previewpicture'] = "IPX-defaultScraper.png"
                        item['thumbnail']      = Item.get_thumb( Item.TYPE_SCRAPER )
                        item['previewpicture'] = ""#Item.get_thumb( Item.TYPE_SCRAPER )
                        
                    elif catType == Item.TYPE_SKIN: #TODO replace by TYPE_SKIN form CONF
                        # Theme
                        item['thumbnail']      = Item.get_thumb( Item.TYPE_SKIN )
                        item['previewpicture'] = ""#Item.get_thumb( Item.TYPE_SKIN )
                    elif catType == Item.TYPE_SCRIPT:
                        # Script
                        #item['thumbnail']      = "IPX-defaultScript_Plugin.png"
                        #item['previewpicture'] = "IPX-defaultScript_Plugin.png"
                        item['thumbnail']      = Item.get_thumb( Item.TYPE_SCRIPT )
                        item['previewpicture'] = ""#Item.get_thumb( Item.TYPE_SCRIPT )
                    elif catType == Item.TYPE_PLUGIN:
                        # Plugin
                        #item['thumbnail']      = "IPX-defaultScript_Plugin.png"
                        #item['previewpicture'] = "IPX-defaultScript_Plugin.png"
                        item['thumbnail']      = Item.get_thumb( Item.TYPE_PLUGIN )
                        item['previewpicture'] = ""#Item.get_thumb( Item.TYPE_PLUGIN )
                    elif catType == Item.TYPE_PLUGIN_MUSIC:
                        # Plugin
                        item['thumbnail']      = Item.get_thumb( Item.TYPE_PLUGIN_MUSIC )
                        item['previewpicture'] = ""#Item.get_thumb( Item.TYPE_PLUGIN_MUSIC )
                    elif catType == Item.TYPE_PLUGIN_PICTURES:
                        # Plugin
                        item['thumbnail']      = Item.get_thumb( Item.TYPE_PLUGIN_PICTURES )
                        item['previewpicture'] = ""#Item.get_thumb( Item.TYPE_PLUGIN_PICTURES )
                    elif catType == Item.TYPE_PLUGIN_PROGRAMS:
                        # Plugin
                        item['thumbnail']      = Item.get_thumb( Item.TYPE_PLUGIN_PROGRAMS )
                        item['previewpicture'] = ""#Item.get_thumb( Item.TYPE_PLUGIN_PROGRAMS )
                    elif catType == Item.TYPE_PLUGIN_VIDEO:
                        # Plugin
                        item['thumbnail']      = Item.get_thumb( Item.TYPE_PLUGIN_VIDEO )
                        item['previewpicture'] = ""#Item.get_thumb( Item.TYPE_PLUGIN_VIDEO )
                    else:
                        skipItem = True
            else:
                # On verifie si l'image serait deja la
                downloadImage = False
                thumbnail, checkPathPic = set_cache_thumb_name( item['previewpictureurl'] )
                if thumbnail and os.path.isfile( thumbnail ):
                    item['thumbnail'] = thumbnail
                else:
                    item['thumbnail'] = Item.THUMB_NOT_AVAILABLE
                    downloadImage = True
                    
                if os.path.exists(checkPathPic):
                    item['previewpicture'] = checkPathPic
                else:
                    item['previewpicture'] = ""#Item.THUMB_NOT_AVAILABLE
                    downloadImage = True
                    
                if downloadImage == True:
                    # Set flag for download (separate thread)
                    item['image2retrieve'] = True
                    
#                    # Telechargement et mise a jour de l'image (thread de separe)
#                    # Ajout a de l'image a la queue de telechargement
#                    #self.image_queue.append( ImageQueueElement( previewPictureURL, updateImage_cb, listitem ) )
#                    self.image_queue.append( ImageQueueElement( item['previewpictureurl'] ) )
#                    #TODO: dynamic update of image (right now image is not updatd in the GUI after download)
                 
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
#        conn = sqlite.connect(self.db)
#        #Initialisation de la base de donnée
        c = self.conn.cursor()
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
        catId = 0
        if ( len(self.curList) > 0 ):
            # Not the 1st load
            # Get current categorie id 
            catId = self.curList[0]['parent']
        return self.getNextList(catId)
    
    def getContextMenu( self ):
        """
        Returns the list of the commands available via the context menu
        """
        pass
    
    def getCategoryInfo( self, catId ):
        """
        Retrieves Categorie Name and Install path
        """
        title = ""
        path = ""
#        # Connect to Database
#        conn = sqlite.connect(self.db)
        c = self.conn.cursor()  
        try:
#            c.execute('''SELECT A.title, A.path
#                         FROM Install_Paths A, Categories B
#                         WHERE B.id_cat = ? 
#                         AND A.id_path = B.id_path
#                         ''',(catId,))
            c.execute('''SELECT title, xbmc_type
                         FROM Categories
                         WHERE id_cat = ? 
                         ''',(catId,))
        except Exception, e:
            print "getCategoryTitle: exception"
            print e
            
        for row in c:
            print row
            title = row[0].encode( "cp1252" )
            type = row[1].encode( "utf8" )
        c.close()   
        print "title = %s"%title
        print "type = %s"%type
        return title, type


    def getInfo( self, index ):
        """
        Returns the information about a specific item (dictionnary)
        Returns a dictionnary with the structure:
        {name, description, icon, downloads, file, created, screenshot}
        Chaque index du dictionnaire renvoie à une liste d'occurences.
        Alimenter cette fonction avec l'id du fichier dont on veut obtenir les infos.
        """
        itemId = self.curList[index]['id']
    
        #Connection à la base de donnee
#        conn = sqlite.connect(self.db)
        c = self.conn.cursor()  
        
        try:
#            c.execute('''SELECT A.id_file , 
#                                A.title, 
#                                A.description, 
#                                A.previewpictureurl, 
#                                A.totaldownloads, 
#                                A.filename, 
#                                A.filesize, 
#                                A.createdate,
#                                C.path
#                         FROM Server_Items A, Categories B, Install_Paths C
#                         WHERE id_file = ? 
#                         AND A.id_cat = B.id_cat
#                         AND B.id_path = C.id_path
#                         ''',(itemId,))
            c.execute('''SELECT A.id_file , 
                                A.title, 
                                A.description, 
                                A.previewpictureurl, 
                                A.totaldownloads, 
                                A.filename, 
                                A.filesize, 
                                A.createdate,
                                B.xbmc_type
                         FROM Server_Items A, Categories B
                         WHERE id_file = ? 
                         AND A.id_cat = B.id_cat
                         ''',(itemId,))
        except Exception, e:
            print e
                     
        #ici une seule ligne est retournee par la requête
        #pour chaque colonne fetchee par la requête on alimente un index du dictionnaire
        dico = {}
        for row in c:
            print row
            dico['id']          = row[0]
            dico['name']        = (row[1].encode( "cp1252" ) )
            dico['description'] = unescape( row[2].encode( "cp1252" ) )
            dico['screenshot']  = row[3]
            dico['downloads']   = row[4]
            dico['filename']    = row[5]
            dico['filesize']    = row[6]
            dico['created']     = row[7]
            #dico['type']=row[8]
            dico['xbmc_type']   = row[8]
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
        itemInstaller = None
        try:            
            if ( ( len(self.curList)> 0 ) and ( self.curList[index]['type'] == 'FIC' ) ):
                # Convert index to id
                itemId      = self.curList[index]['id']
                name        = self.curList[index]['name']
                catId       = self.curList[index]['parent']
                externalURL = self.curList[index]['fileexternurl'].encode('utf8')
                #type        = self.curList[index]['xbmc_type']

                # Get file size
                itemInfos = self.getInfo(index)
                filesize  = itemInfos['filesize']
                xbmc_type = itemInfos['xbmc_type']
                
                print itemInfos

                print "getInstaller - name" 
                print name
                print "getInstaller - externalURL" 
                print externalURL
                print "getInstaller - filesize"
                print filesize

                # Create the right type of Installer Object
                #itemInstaller = PassionHttpItemInstaller.PassionHTTPInstaller( itemId, type, installPath, filesize, externalURL )
                #itemInstaller = PassionHttpItemInstaller.PassionHTTPInstaller( itemId, type, filesize, externalURL )
                itemInstaller = PassionHttpItemInstaller.PassionHTTPInstaller( name, itemId, xbmc_type, filesize, externalURL )
            else:
                print "getInstaller: error impossible to install a category, it has to be an item "

        except Exception, e:
            print "Exception during getInstaller"
            print_exc()
                 
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
            print "_downloadImage: Exception - Impossible to downlod the picture: %s" % picname
            print_exc()
            #TODO: create a thumb for the default image?
            #TODO: return empty and manage default image at the level of the caller
            thumbnail, localFilePath = "", "" 
        print "thumbnail = %s"%thumbnail
        print "localFilePath = %s"%localFilePath
        return thumbnail, localFilePath

    def close( self ):
        """
        Close browser: i.e close connection, free memory ...
        """
        self.databaseMgr.exit()
        try: self.cancel_update_Images()
        except: print "PassionHttpBrowser: error on close (cancel image)"

    