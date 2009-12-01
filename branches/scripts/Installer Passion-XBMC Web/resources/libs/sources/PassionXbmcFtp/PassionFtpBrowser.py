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
from INSTALLEUR import ftpDownloadCtrl, directorySpy, userDataXML
import ftplib



## Filtre sur les elemens a affciher selon le cas (racine ou plugin)
#rootDisplayList   = [ TYPE_SKIN, TYPE_SCRAPER, TYPE_SCRIPT, TYPE_PLUGIN ]                                # Liste de la racine: Cette liste est un filtre ( utilisant l'index ) sur les listes ci-dessus
#pluginDisplayList = [ TYPE_PLUGIN_MUSIC, TYPE_PLUGIN_PICTURES, TYPE_PLUGIN_PROGRAMS, TYPE_PLUGIN_VIDEO ] # Liste des plugins : Cette liste est un filtre ( utilisant l'index ) sur les listes ci-dessus

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
        #self.db  = kwargs[ "database" ] # Database file
        #self.db = db       # Database file
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
#        self.CacheDir           = self.configManager.CACHEDIR
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

            self.passionFTPCtrl = ftpDownloadCtrl( self.host, self.user, self.password, self.remotedirList, self.localdirList, self.downloadTypeList )
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
            item['previewpicture']    = Item.get_thumb( cat )
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
            item['name']              = Item.get_type_title( cat )
            #item['parent']            = Item.TYPE_PLUGIN
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
            item['previewpicture']    = Item.get_thumb( cat )
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
            item['previewpicture'] = Item.THUMB_NOT_AVAILABLE # preview
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
                item['previewpicture'] = Item.THUMB_NOT_AVAILABLE
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
#            loc = urllib.URLopener()
#            loc.retrieve(filetodlUrl, localFilePath)   
            ftp = ftplib.FTP( self.host, self.user, self.password )
            localFile = open( localFilePath, "wb" )
            try:
                ftp.retrbinary( 'RETR ' + filetodlUrl, localFile.write )
            except:
                #import traceback; traceback.print_exc()
                logger.LOG( logger.LOG_DEBUG, "_downloaddossier: Exception - Impossible de telecharger le fichier: %s", remoteFilePath )
                logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )
                thumbnail, localFilePath = "", ""
            localFile.close()
            ftp.quit()

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
                            item['thumbnail']         = Item.THUMB_NOT_AVAILABLE
                            item['previewpicture']    = Item.THUMB_NOT_AVAILABLE
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
            infos = self.infoswarehouse.getInfo( itemName=os.path.basename( item['downloadurl'] ), itemType=item['xbmc_type'] )

            print "+++++++     INFOS   ++++++++++"
            #item['itemId']            = infos.itemId
            item['name']              = infos.title
            item['previewpictureurl'] = infos.previewPictureURL
            #item['infos.previewVideoURL'] = infos.infos.previewVideoURL
            item['description']       = infos.description
            item['language']          = infos.language
            item['version']           = infos.version
            item['author']            = infos.author
            item['date']              = infos.date
            item['added']             = infos.added or infos.date
            # listitem.setProperty( "itemId",          infos.itemId )
            # listitem.setProperty( "fileName",        infos.fileName )
            # listitem.setProperty( "date",            infos.date )
            # listitem.setProperty( "title",           infos.title )
            # listitem.setProperty( "author",          infos.author )
            # listitem.setProperty( "version",         infos.version )
            # listitem.setProperty( "language",        infos.language )
            # listitem.setProperty( "description",     infos.description )
            # listitem.setProperty( "added",           infos.added or infos.date )
            # listitem.setProperty( "fanartpicture",   infos.previewPicture )
            # listitem.setProperty( "previewVideoURL", infos.previewVideoURL )

            # Set image
            self._setDefaultImages( item )

        except:
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )
            traceback.print_exc()





#        if not xbmc.getCondVisibility( "Window.IsActive(progressdialog)" ):
#            DIALOG_PROGRESS.create( _( 0 ), _( 104 ), _( 110 ) )
#        # On verifie self.type qui correspond au type de liste que l'on veut afficher
#        if ( self.type == "racine" ):
#            #liste virtuelle des sections
#            #del self.curDirList[ : ] # on vide la liste
#            self.curDirList = self.racineDisplayList
#
#        elif ( self.type == "Plugins" ):
#            #liste virtuelle des sections
#            self.curDirList = self.pluginDisplayList
#        #elif ( self.type == "Plugins Musique" ) or ( self.type == "Plugins Images" ) or ( self.type == "Plugins Programmes" ) or ( self.type == "Plugins Videos" ):
#        elif "Plugins " in self.type:
#            # Arret du theard de chargement des images
#            try: self.infoswarehouse.cancel_update_Images()
#            except: pass
#
#            self.curDirList = self.passionFTPCtrl.getDirList( self.remotedirList[ self.pluginDisplayList[ self.index ] ] )
#        else:
#            #liste virtuelle des sections
#            #del self.curDirList[ : ] # on vide la liste
#
#            # Arret du theard de chargement des images
#            try: self.infoswarehouse.cancel_update_Images()
#            except: pass
#
#            #liste physique d'une section sur le ftp
#            self.curDirList = self.passionFTPCtrl.getDirList( self.remotedirList[ self.index ] )
#            
#
#        #xbmcgui.lock()
#
#        # Clear all ListItems in this control list
#        if hasattr( self, 'clearProperties' ):
#            self.clearProperties()
#        self.clearList()
#        self.listitems = []
#
#        # Calcul du nombre d'elements de la liste
#        itemnumber = len( self.curDirList )
#
#        # On utilise la fonction range pour faire l'iteration sur index
#        for j in range( itemnumber ):
#            imagePath = ""
#            if ( self.type == "racine" ):
#                # Nom de la section
#                sectionName = self.downloadTypeList[ self.racineDisplayList[ j ] ] # On utilise le filtre
#                # Met a jour le titre:
#                self.setProperty( "Category", _( 10 ) )
#
#                # Affichage de la liste des sections
#                # -> On compare avec la liste affichee dans l'interface
#                if sectionName == self.downloadTypeList[ 0 ]:
#                    # Theme
#                    imagePath = "IPX-defaultSkin.png"
#                    sectionLocTitle = _( 11 )
#                elif sectionName == self.downloadTypeList[ 1 ]:
#                    # Scraper
#                    imagePath = "IPX-defaultScraper.png"
#                    sectionLocTitle = _( 12 )
#                elif sectionName == self.downloadTypeList[ 2 ]:
#                    # Script
#                    imagePath = "IPX-defaultScript_Plugin.png"
#                    sectionLocTitle = _( 13 )
#                elif sectionName == self.downloadTypeList[ 3 ]:
#                    # Plugin
#                    imagePath = "IPX-defaultScript_Plugin.png"
#                    sectionLocTitle = _( 14 )
#
#                displayListItem = xbmcgui.ListItem( sectionLocTitle, "", iconImage=imagePath, thumbnailImage=imagePath )
#                displayListItem.setProperty( "title", sectionLocTitle )
#                displayListItem.setProperty( "description", " " )
#                displayListItem.setProperty( "Downloaded", "" )
#                self.addItem( displayListItem )
#
#            elif ( self.type == "Plugins" ):
#                # Nom de la section
#                sectionName = self.downloadTypeList[ self.pluginDisplayList[ j ] ] # On utilise le filtre
#                # Met a jour le titre:
#                self.setProperty( "Category", _( 14 ) )
#
#                if sectionName == self.downloadTypeList[ 4 ]:
#                    # Music
#                    imagePath = "IPX-defaultPluginMusic.png"
#                    sectionLocTitle = _( 15 )
#                elif sectionName == self.downloadTypeList[ 5 ]:
#                    # Pictures
#                    imagePath = "IPX-defaultPluginPicture.png"
#                    sectionLocTitle = _( 16 )
#                elif sectionName == self.downloadTypeList[ 6 ]:
#                    # Programs
#                    imagePath = "IPX-defaultPluginProgram.png"
#                    sectionLocTitle = _( 17 )
#                elif sectionName == self.downloadTypeList[ 7 ]:
#                    # Video
#                    imagePath = "IPX-defaultPluginVideo.png"
#                    sectionLocTitle = _( 18 )
#
#                displayListItem = xbmcgui.ListItem( sectionLocTitle, "", iconImage=imagePath, thumbnailImage=imagePath )
#                displayListItem.setProperty( "title", sectionLocTitle )
#                displayListItem.setProperty( "description", " " )
#                displayListItem.setProperty( "Downloaded", "" )
#                self.addItem( displayListItem )
#
#            elif "Plugins " in self.type:
#                # Element de la liste
#                ItemListPath = self.curDirList[ j ]
#
#                # on a tjrs besoin de connaitre la taille du chemin de base pour le soustraire/retirer du chemin global plus tard
#                lenindex = len( self.remotedirList[ self.pluginDisplayList[ self.index ] ] )
#
#                # Met a jour le titre et les icones:
#                if self.type == self.downloadTypeList[ 4 ]:
#                    # Music
#                    self.setProperty( "Category", _( 15 ) )
#                    imagePath = "IPX-defaultPluginMusic.png"
#                elif self.type == self.downloadTypeList[ 5 ]:
#                    # Pictures
#                    self.setProperty( "Category", _( 16 ) )
#                    imagePath = "IPX-defaultPluginPicture.png"
#                elif self.type == self.downloadTypeList[ 6 ]:
#                    # Programs
#                    self.setProperty( "Category", _( 17 ) )
#                    imagePath = "IPX-defaultPluginProgram.png"
#                elif self.type == self.downloadTypeList[ 7 ]:
#                    # Video
#                    self.setProperty( "Category", _( 18 ) )
#                    imagePath = "IPX-defaultPluginVideo.png"
#
#                # nettoyage du nom: replace les souligner pas un espace et enleve l'extension
#                try:
#                    item2download = ItemListPath[ lenindex: ].replace( "_", " " )
#                    if self.settings.get( "hide_extention", True ):
#                        item2download = os.path.splitext( item2download )[ 0 ]
#                except:
#                    item2download = ItemListPath[ lenindex: ]
#                DIALOG_PROGRESS.update( -1, _( 103 ), item2download, _( 110 ) )
#
#                if self.downloaded_property.__contains__( md5.new( item2download ).hexdigest() ):
#                    already_downloaded = "true"
#                else:
#                    already_downloaded = ""
#
#                displayListItem = xbmcgui.ListItem( item2download, "", iconImage=imagePath, thumbnailImage=imagePath )
#                displayListItem.setProperty( "Downloaded", already_downloaded )
#                self.set_item_infos( displayListItem, ItemListPath )
#                self.addItem( displayListItem )
#                DIALOG_PROGRESS.update( -1, _( 103 ), item2download, _( 110 ) )
#
#            else:
#                # Element de la liste
#                ItemListPath = self.curDirList[ j ]
#
#                #affichage de l'interieur d'une section
#                #self.numindex = self.index
#                lenindex = len( self.remotedirList[ self.index ] ) # on a tjrs besoin de connaitre la taille du chemin de base pour le soustraire/retirer du chemin global plus tard
#
#                # Met a jour le titre et les icones:
#                if self.type == self.downloadTypeList[ 0 ]: #Themes
#                    self.setProperty( "Category", _( 11 ) )
#                    imagePath = "IPX-defaultSkin.png"
#                elif self.type == self.downloadTypeList[ 1 ]: #Scrapers
#                    self.setProperty( "Category", _( 12 ) )
#                    imagePath = "IPX-defaultScraper.png"
#                elif self.type == self.downloadTypeList[ 2 ]: #Scripts
#                    self.setProperty( "Category", _( 13 ) )
#                    imagePath = "IPX-defaultScript_Plugin.png"
#
#                # nettoyage du nom: replace les souligner pas un espace et enleve l'extension
#                try:
#                    item2download = ItemListPath[ lenindex: ].replace( "_", " " )
#                    if self.settings.get( "hide_extention", True ):
#                        item2download = os.path.splitext( item2download )[ 0 ]
#                except:
#                    item2download = ItemListPath[ lenindex: ]
#                DIALOG_PROGRESS.update( -1, _( 103 ), item2download, _( 110 ) )
#
#                if self.downloaded_property.__contains__( md5.new( item2download ).hexdigest() ):
#                    already_downloaded = "true"
#                else:
#                    already_downloaded = ""
#
#                displayListItem = xbmcgui.ListItem( item2download, "", iconImage=imagePath, thumbnailImage=imagePath )
#                displayListItem.setProperty( "Downloaded", already_downloaded )
#                self.set_item_infos( displayListItem, ItemListPath )
#                self.addItem( displayListItem )
#                DIALOG_PROGRESS.update( -1, _( 103 ), item2download, _( 110 ) )
#
#            # utiliser pour remettre la liste courante a jour lorsqu'on reviens sur cette fenetre depuis le forum ou le manager
#            self.listitems.append( displayListItem )
#        self.current_cat = unicode( xbmc.getInfoLabel( 'Container.Property(Category)' ), 'utf-8')
#
#        if ( self.type != "racine" ) and ( self.type != "Plugins" ):
#            # Mise a jour des images
#            self.set_list_images()
#        #xbmcgui.unlock()
#
#        DIALOG_PROGRESS.close()
        
        
        
    def isCat( self, index ):
        """
        Returns True when selected item is a category
        """
        if ( ( len(self.curList)> 0 ) and ( self.curList[index]['type'] == 'CAT' ) ):
            # Convert index to id
            return True
        else:
            return False
        
        
        
        
    
    