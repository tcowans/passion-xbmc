"""
PassionFtpBrowser: this module allows browsing of server content on the FTP server of Passion-XBMC.org
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
    
#Other module
from threading import Thread
from pil_util import makeThumbnails
#import urllib

# Modules custom
from utilities import *
from Browser import Browser, ImageQueueElement
import Item
import ItemInstaller  
from info_item import ItemInfosManager
from PassionFtpmanager import FtpDownloadCtrl
import ftplib
import PassionFtpItemInstaller


#FONCTION POUR RECUPERER LES LABELS DE LA LANGUE.
_ = sys.modules[ "__main__" ].__language__
LANGUAGE_IS_FRENCH = sys.modules[ "__main__" ].LANGUAGE_IS_FRENCH

    
class PassionFtpBrowser(Browser):
    """
    Browser FTP server using FTP command and display information about item stored in the database
    """
#    def __init__(self):
    def __init__( self, *args, **kwargs  ):
        Browser.__init__( self, *args, **kwargs )

        # Creation du configCtrl
        from CONF import configCtrl
        self.configManager = configCtrl()
        if not self.configManager.is_conf_valid: raise

        self.host               = self.configManager.host
        self.user               = self.configManager.user
        self.password           = self.configManager.password
        self.remotedirList      = self.configManager.remotedirList

        self.localdirList       = self.configManager.localdirList
        self.downloadTypeList   = self.configManager.downloadTypeLst

        self.racineDisplayList  = [ Item.TYPE_SKIN, Item.TYPE_SCRAPER, Item.TYPE_SCRIPT, Item.TYPE_PLUGIN ]
        self.pluginDisplayList  = [ Item.TYPE_PLUGIN_MUSIC, Item.TYPE_PLUGIN_PICTURES, Item.TYPE_PLUGIN_PROGRAMS, Item.TYPE_PLUGIN_VIDEO ]

#        self.curDirList         = []
        self.connected          = False # status de la connection ( inutile pour le moment )
        self.index              = ""
#        self.scraperDir         = self.configManager.scraperDir
#        self.type               = "racine"
#        self.USRPath            = self.configManager.USRPath
        self.rightstest         = ""
#        self.scriptDir          = self.configManager.scriptDir
        self.CACHEDIR           = self.configManager.CACHEDIR
#        self.userDataDir        = self.configManager.userdatadir # userdata directory
#        self.targetDir          = ""

#        # utiliser pour remettre la liste courante a jour lorsqu'on reviens sur cette fenetre depuis le forum ou le manager
#        self.listitems = []
#        self.type = Item.TYPE_ROOT
#        self.curCategory = Item.get_type_title( self.type )
        
        
        self.curList = []  # Current list of item/category

        #self.currentItemId = 0

        # Connection au serveur FTP
        try:

            self.passionFTPCtrl = FtpDownloadCtrl( self.host, self.user, self.password, self.remotedirList, self.localdirList, self.downloadTypeList, self.CACHEDIR )
            self.connected = True

            #self.updateList()

        except:
            logger.LOG( logger.LOG_DEBUG, "PassionFtpBrowser::__init__: Exception durant la connection FTP" )
            logger.LOG( logger.LOG_DEBUG, "Impossible de se connecter au serveur FTP: %s", self.host )
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )
            traceback.print_exc()

        # Creons ItemInfosManager afin de recuperer les descriptions des items
        self.itemInfosManager = ItemInfosManager( mainwin=self )
        self.infoswarehouse = self.itemInfosManager.get_info_warehouse()
        

    def reset( self ):
        """
        Reset the browser (back to start page)
        """
        self.curList = []  
        #self.index   = ""

    def _createRootList(self):
        """
        Create and return the root list (all type available)
        Returns list and name of the list
        """
        list = []
        listTitle = _( 10 )

        # List the main categorie at the root level
        for cat in self.racineDisplayList:   
            item = {}
            #item['id']                = ""
            item['name']              = Item.get_type_title( cat )
            #item['parent']            = self.type
            item['downloadurl']       = None
            item['type']              = 'CAT'
            item['xbmc_type']           = cat
            item['previewpictureurl'] = None
            item['description']       = Item.get_type_title( cat )
            item['language']          = ""
            item['version']           = ""
            item['author']            = ""
            item['date']              = ""
            item['added']             = ""
            item['thumbnail']         = Item.get_thumb( cat )
            item['previewpicture']    = ""#Item.get_thumb( cat )
            item['image2retrieve']    = False # Temporary patch for reseting the flag after download (would be better in the thread in charge of the download)

            list.append(item)
            print item
            
        return listTitle, list

    def _createPluginList(self):
        """
        Create and return the list of plugin types
        Returns list and name of the list
        """
        list = []
        listTitle = Item.get_type_title( Item.TYPE_PLUGIN )
        
        # List all the type of plugins
        for cat in self.pluginDisplayList:   
            item = {}
            #item['id']                = ""
            #item['parent']            = Item.TYPE_PLUGIN
            item['name']              = Item.get_type_title( cat )
            item['downloadurl']       = None
            item['type']              = 'CAT'
            item['xbmc_type']         = cat
            item['previewpictureurl'] = None
            item['description']       = Item.get_type_title( cat )
            item['language']          = ""
            item['version']           = ""
            item['author']            = ""
            item['date']              = ""
            item['added']             = ""
            item['thumbnail']         = Item.get_thumb( cat )
            item['previewpicture']    = ""#Item.get_thumb( cat )
            item['image2retrieve']    = False # Temporary patch for reseting the flag after download (would be better in the thread in charge of the download)

            list.append(item)
            print item
            
        return listTitle, list
    
    def _setDefaultImages(self, item):
        """
        Set the images with default value depending on the type of the item
        """
        print "_setDefaultImages"
        print item['previewpictureurl']
        if  item['previewpictureurl'] == 'None':
            # No picture available -> use default one
            item['thumbnail']      = Item.get_thumb( item['xbmc_type'] ) # icone
            item['previewpicture'] = ""#Item.THUMB_NOT_AVAILABLE # preview
        else:
            # Check if picture is already downloaded and available
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
                

    def _downloadImage( self, picname ):
        """
        Download picture from the server, save it, create the thumbnail and return path of it
        """
        print "_downloadImage %s"%picname
        try:
        
            filetodlUrl = picname # image path on FTP server
            print "filetodlUrl"
            print filetodlUrl
            thumbnail, localFilePath = set_cache_thumb_name( picname )
            print thumbnail
            print localFilePath
            
            # Retrieve image
            if not self.passionFTPCtrl.downloadImage( filetodlUrl, localFilePath):
                print "ERROR while retrieving image via FTP"
                thumbnail, localFilePath = "", ""

#            ftp = ftplib.FTP( self.host, self.user, self.password )
#            #self.passionFTPCtrl.openConnection()
#            localFile = open( localFilePath, "wb" )
#            try:
#                ftp.retrbinary( 'RETR ' + filetodlUrl, localFile.write )
#                #self.passionFTPCtrl.retrbinary( self, 'RETR ' + filetodlUrl, callback, blocksize=8192, rest=None )
#            except:
#                #import traceback; traceback.print_exc()
#                logger.LOG( logger.LOG_DEBUG, "_downloaddossier: Exception - Impossible de telecharger le fichier: %s", remoteFilePath )
#                logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )
#                thumbnail, localFilePath = "", ""
#            localFile.close()
#            ftp.quit()

            #self.passionFTPCtrl.downloadImage(pathsrc, isSingleFile=True)
            
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
        except Exception, e:
            print "Exception during _downloadImage"
            print e
            #TODO: create a thumb for the default image?
            #TODO: return empty and manage default image at the level of the caller
            thumbnail, localFilePath = "", "" 
            print sys.exc_info()
            logger.LOG( logger.LOG_DEBUG, "_downloadImage: Exception - Impossible to download the picture: %s", picname )
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )
            traceback.print_exc()
        print "thumbnail = %s"%thumbnail
        print "localFilePath = %s"%localFilePath
        return thumbnail, localFilePath

    
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
            if len(self.curList)> 0 :
                if self.curList[index]['type'] == 'CAT':
                    if self.curList[index]['xbmc_type'] == Item.TYPE_PLUGIN:
                        # root plugin case
                        self.type = Item.TYPE_PLUGIN
                        self.curCategory, list = self._createPluginList()
                    else:
                        # List of item to download case                  
                        #list = self.incat(itemId) # Get content of the category
                        #self.currentItemId = itemId
                        self.type = self.curList[index]['xbmc_type']
                        self.curCategory = Item.get_type_title( self.type )
                        listOfItem = self.passionFTPCtrl.getDirList( self.remotedirList[ Item.get_type_index( self.type ) ] )
                        print "listOfItem in a cat"
                        print listOfItem
                        for elt in listOfItem:
                            item = {}
                            item['name']              = os.path.basename( elt ).replace( "_", " " )
                            item['downloadurl']       = elt
                            item['type']              = 'FIC'
                            item['xbmc_type']           = self.type
                            item['previewpictureurl'] = None
                            item['description']       = _( 604 )
                            item['language']          = ""
                            item['version']           = ""
                            item['author']            = ""
                            item['date']              = ""
                            item['added']             = ""
                            #TODO: have different icon between cat and item without thumb
                            #item['thumbnail']         = Item.THUMB_NOT_AVAILABLE
                            item['thumbnail']         = Item.get_thumb( item['xbmc_type'] )
                            item['previewpicture']    = ""#Item.THUMB_NOT_AVAILABLE
                            item['image2retrieve']    = False # Temporary patch for reseting the flag after download (would be better in the thread in charge of the download)
        
                            self._set_item_infos(item) # Update infos
                            list.append(item)
                            print item
                            
                        
                    # Save the current item name as category
                    self.curCategory = self.curList[index]['name'] 
                else:
                    # Return the current list
                    #TODO: start download here?
                    print "This is not a category but an item (download)"
                    list = self.curList
               
            else: # len(self.curList)<= 0 
                # 1st time (init), we display root list
                self.type = Item.TYPE_ROOT
                # List the main categorie at the root level
                self.curCategory, list = self._createRootList()
        except Exception, e:
            print "Exception during getNextList"
            print e
            print sys.exc_info()
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )
            traceback.print_exc()
        # Replace current list
        self.curList = list
        return self.curList

    def getPrevList( self ):
        """
        Returns the list (up) of item (dictionary) on the server depending on the location we are on the server
        Go to previous page/list 
        Other possible name: Up
        """
        list = []

        try:
            if Item.TYPE_PLUGIN + "_" in self.type:
                self.type = Item.TYPE_PLUGIN
                self.curCategory, list = self._createPluginList()
            else:
                # We display root
                self.type = Item.TYPE_ROOT
                self.curCategory, list = self._createRootList()
        except Exception, e:
            print "Exception during getPrevList"
            print e
            print sys.exc_info()
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )
            traceback.print_exc()
        # Replace current list
        self.curList = list
        return list

    def _set_item_infos( self, item ):
        print "set_item_infos"
        try:
            # Retrieve info (using V implementation mostly)
            infos = self.infoswarehouse.getInfo( itemName=os.path.basename( item['downloadurl'] ), itemType=item['xbmc_type'] )
            #item['itemId']            = infos.itemId
            #item['infos.previewVideoURL'] = infos.infos.previewVideoURL
            #item['fileName']          = infos.fileName
            item['name']              = infos.title
            item['previewpictureurl'] = infos.previewPictureURL
            item['description']       = infos.description
            item['language']          = infos.language
            item['version']           = infos.version
            item['author']            = infos.author
            item['date']              = infos.date
            item['added']             = infos.added or infos.date

            # Set image
            self._setDefaultImages( item )
        except:
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )
            traceback.print_exc()
        
        
    def isCat( self, index ):
        """
        Returns True when selected item is a category
        """
        if ( ( len(self.curList)> 0 ) and ( self.curList[index]['type'] == 'CAT' ) ):
            # Convert index to id
            return True
        else:
            return False
        
        
    def close( self ):
        """
        Close browser: i.e close connection, free memory ...
        """
        self.passionFTPCtrl.closeConnection()
        try: self.cancel_update_Images()
        except: print "PassionFtpBrowser: error on close (cancel image)"
        
        
    def getInstaller( self, index ):
        """
        Returns an ItemInstaller instance
        """
        itemInstaller = None
        try:            
            if ( ( len(self.curList)> 0 ) and ( self.curList[index]['type'] == 'FIC' ) ):
                if self.curList[index]['xbmc_type'] == Item.TYPE_SKIN:
                    # Use installer for Skin (file per file download)
                    print "Installing skin case"
                    #TODO
                else:
                
                    # Convert index to id
                    name        = self.curList[index]['name']
                    downloadurl = self.curList[index]['downloadurl']
                    type        = self.curList[index]['xbmc_type']
                    print "getInstaller - name" 
                    print name
                    print "getInstaller - downloadurl" 
                    print downloadurl
    
                    # Create the right type of Installer Object
                    itemInstaller = PassionFtpItemInstaller.PassionFTPInstaller( name, type, downloadurl, self.passionFTPCtrl )
            else:
                print "getInstaller: error impossible to install a category, it has to be an item "

        except Exception, e:
            print "Exception during getInstaller of Passion XBMC FTP Browser"
            print e
            print sys.exc_info()
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )
            traceback.print_exc()   
                 
        return itemInstaller
    
    