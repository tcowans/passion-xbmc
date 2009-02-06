
#Modules general
import os
import sys
import shutil
import ftplib

#Other module
from threading import Thread

#modules XBMC
import xbmc

#modules custom
from utilities import *
from pil_util import makeThumbnails

#module logger
try:
    logger = sys.modules[ "__main__" ].logger
except:
    import script_log as logger


#FONCTION POUR RECUPERER LES LABELS DE LA LANGUE.
_ = sys.modules[ "__main__" ].__language__


try: __script__ = sys.modules[ "__main__" ].__script__
except: __script__ = os.path.basename( os.getcwd().rstrip( ";" ) )

BASE_THUMBS_PATH = os.path.join( xbmc.translatePath( "P:\\script_data" ), __script__, "Thumbnails" )

def set_cache_thumb_name( path ):
    try:
        fpath = path
        # make the proper cache filename and path so duplicate caching is unnecessary
        filename = xbmc.getCacheThumbName( fpath )
        thumbnail = os.path.join( BASE_THUMBS_PATH, filename[ 0 ], filename )
        preview_pic = os.path.join( BASE_THUMBS_PATH, "originals", filename[ 0 ], filename )
        # if the cached thumbnail does not exist check for dir does not exist create dir
        if not os.path.isdir( os.path.dirname( preview_pic ) ):
            os.makedirs( os.path.dirname( preview_pic ) )
        if not os.path.isdir( os.path.dirname( thumbnail ) ):
            os.makedirs( os.path.dirname( thumbnail ) )
        return thumbnail, preview_pic
    except:
        #import traceback; traceback.print_exc()
        logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info() )
        return "", ""

class InfoWarehouse:
    """
    Class Abstraite contenant toutes les informations necessaires a la description d'un item
    """
    def __init__( self, *args, **kwargs ):
        pass
    
    def getInfo( self, itemName = None, iTemType=None, itemId = None, ):
        """ 
        Lit les info 
        retourne fileName, title, version, language, date , previewPicture, previewVideoURL, description_fr, description_en
        Fonction abstraite
        """
        fileName        = itemName # Default value if we don't find itemname
        title           = itemName # Default value if we don't find itemname
        version         = None
        language        = None
        date            = None
        previewPicture  = None
        thumbnail       = ""
        previewVideoURL = None
        description_fr  = None
        description_en  = None

        return fileName, title, version, language, date , previewPicture, previewVideoURL, description_fr, description_en, thumbnail


class InfoWarehouseBSoupXMLFTP( InfoWarehouse ):
    """
    Class contenant tous les informations dans un fichier XML sur serveur FTP necessaires a la description d'un item
    Pour des raisons de performance, on instanciera cette classe une seule fois au demarrage du script
    Cette classe utilise BeautifulSoup
    """
    def __init__( self, *args, **kwargs ):
        # import BeautifulSoup module
        from BeautifulSoup import BeautifulStoneSoup, Tag, NavigableString  #librairie de traitement XML

        logger.LOG( logger.LOG_DEBUG,'InfoWarehouseBSoupXMLFTP starts')
        self.mainwin  = kwargs[ "mainwin" ]

        self._get_settings()
        self.thumb_size_on_load = self.mainwin.settings[ "thumb_size" ]
        
        # On recupere le fichier de description des items
        self._downloadFile( self.srvItemDescripDir + self.srvItemDescripFile, isTBN=False )
        self.soup =  BeautifulStoneSoup((open(os.path.join(self.mainwin.CacheDir,self.srvItemDescripFile), 'r')).read())
    
    def _getImage( self, pictureURL, updateImage_cb=None, listitem=None ):
        cached_thumbs = set_cache_thumb_name( pictureURL )
        if not os.path.exists( cached_thumbs[ 0 ] ) or not os.path.exists( cached_thumbs[ 1 ] ):
            try: self.getImage_thread.cancel()
            except: pass
            self.getImage_thread = Thread( target=self._thread_getImage, args=( pictureURL, updateImage_cb, listitem ) )
            self.getImage_thread.start()

    def _thread_getImage( self, pictureURL, updateImage_cb=None, listitem=None ):
        """
        Recupere l'image dans un thread separe
        """
        # Telechargement de l'image
        self._downloadFile( pictureURL, listitem=listitem )
        #checkPathPic = set_cache_thumb_name( pictureURL )#os.path.join(self.mainwin.CacheDir, os.path.basename(pictureURL))
        
        cached_thumbs = set_cache_thumb_name( pictureURL )

        if os.path.exists( cached_thumbs[ 1 ] ):
            previewPicture = cached_thumbs[ 1 ]
        else:
            previewPicture = None
        
        # Notifie la callback de mettre a jour l'image
        if updateImage_cb:
            try: updateImage_cb( cached_thumbs[ 1 ] )
            except TypeError: pass

    def check_thumb_size( self ):
        if self.thumb_size_on_load != self.mainwin.settings[ "thumb_size" ]:
            self.thumb_size_on_load = self.mainwin.settings[ "thumb_size" ]
            try:
                BASE_THUMBS_PATH = os.path.join( xbmc.translatePath( "P:\\script_data" ), __script__, "Thumbnails" )
                shutil.rmtree( BASE_THUMBS_PATH )
            except:
                #import traceback; traceback.print_exc()
                logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )

    def getInfo( self, itemName=None, itemType=None, itemId=None, updateImage_cb=None, listitem=None ):
        self.check_thumb_size()
        """ 
        Lit les info 
        retourne fileName, title, version, language, date , previewPicture, previewVideoURL, description_fr, description_en
        Fonction abstraite
        """
        """ reads info """
        fileName        = itemName # Defaukt value if we don't find itemname
        title           = itemName # Defaukt value if we don't find itemname
        version         = None
        language        = None
        date            = None
        previewPicture  = None
        thumbnail       = ""
        previewVideoURL = None
        description_fr  = None
        description_en  = None

        cat = None
        
        if itemType == "Themes":
            cat = self.soup.find("skins")
        elif itemType == "Scrapers":
            cat = self.soup.find("scrapers")
        elif itemType == "Scripts":
            cat = self.soup.find("scripts")
        elif itemType == "Plugins Musique":
            cat = self.soup.find("musicplugin")
        elif itemType == "Plugins Images":
            cat = self.soup.find("pictureplugin")
        elif itemType == "Plugins Programmes":
            cat = self.soup.find("programplugin")
        elif itemType == "Plugins Vidéos":
            cat = self.soup.find("videoplugin")

        try:
            if cat != None:
                for item in cat.findAll("entry"):
                    if hasattr(item.filename,'string'):
                        if item.filename.string != None:
                            fileName = item.filename.string.encode("cp1252")

                            if fileName == itemName:
                                if hasattr(item.title,'string'):
                                    if item.title.string != None:
                                        title = item.title.string.encode("cp1252")
                                if hasattr(item.version,'string'): 
                                    if item.version.string != None:
                                        version = item.version.string.encode("utf-8")
                                if hasattr(item.lang,'string'): 
                                    if item.lang.string != None:
                                        language = item.lang.string.encode("utf-8")
                                if hasattr(item.date,'string'):
                                    if item.date.string != None:
                                        date = item.date.string.encode("cp1252")
                                if hasattr(item.added,'string'):
                                    if item.added.string != None:
                                        added = item.added.string.encode("cp1252")
                                if hasattr(item.previewpictureurl,'string'):
                                    if item.previewpictureurl.string != None:
                                        previewPictureURL = item.previewpictureurl.string.encode("utf-8")
                                        
                                        # On verifie si l'image serait deja la
                                        #checkPathPic = os.path.join(self.mainwin.CacheDir, os.path.basename(previewPictureURL))
                                        thumbnail, checkPathPic = set_cache_thumb_name( previewPictureURL )
                                        if thumbnail and os.path.isfile( thumbnail ) and hasattr( listitem, 'setThumbnailImage' ):
                                            #if listitem and hasattr( listitem, 'setThumbnailImage' ):
                                            listitem.setThumbnailImage( thumbnail )
                                        if os.path.exists(checkPathPic):
                                            previewPicture = checkPathPic
                                        else:
                                            # Telechargement et mise a jour de l'image (thread de separe)
                                            previewPicture = checkPathPic#"downloading"
                                            self._getImage( previewPictureURL, updateImage_cb=updateImage_cb, listitem=listitem )
                                            
                                if hasattr(item.previewvideourl,'string'):
                                    if item.previewvideourl.string != None:
                                        # Non utilse pour le moment
                                        previewVideoURL = item.previewvideourl.string.encode("utf-8")
                                if hasattr(item.description_fr,'string'):
                                    if item.description_fr.string != None:
                                        description_fr = item.description_fr.string.encode("cp1252")
                                if hasattr(item.description_en,'string'):
                                    if item.description_en.string != None:
                                        description_en = item.description_en.string.encode("cp1252")
                                if hasattr(item.author,'string'):
                                    if item.author.string != None:
                                        author = item.author.string.encode("cp1252")
                                # We exit the loop since we found the file we were looking for
                                break
               
        except Exception, e:
            #import traceback; traceback.print_exc()
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )
        
        return fileName, title, version, language, date , previewPicture, previewVideoURL, description_fr, description_en, thumbnail
        return fileName, title, version, language, date, added, previewPicture, previewVideoURL, description_fr, description_en, thumbnail, author

    def _get_settings( self, defaults=False  ):
        """ reads settings from conf file """
        self.settings           = Settings().get_settings( defaults=defaults )
        self.srvHost            = self.mainwin.configManager.getSrvHost()
        self.srvPassword        = self.mainwin.configManager.getSrvPassword()
        self.srvUser            = self.mainwin.configManager.getSrvUser()
        self.srvItemDescripDir  = self.mainwin.configManager.getSrvItemDescripDir()
        self.srvItemDescripFile = self.mainwin.configManager.getSrvItemDescripFile()
        
        logger.LOG( logger.LOG_DEBUG,self.srvHost)
        logger.LOG( logger.LOG_DEBUG,self.srvItemDescripDir)

    def _downloadFile( self, remoteFilePath, isTBN=True, listitem=None ):
        """
        Fonction de telechargement commune : version, archive, script de mise a jour
        """
        try:
            filetodlUrl = remoteFilePath
            if isTBN:
                thumbnail, localFilePath = set_cache_thumb_name( remoteFilePath )
            else:
                thumbnail = ""
                localFilePath = os.path.join( self.mainwin.CacheDir, os.path.basename( remoteFilePath ) )

            if not os.path.isfile( localFilePath ):
                ftp = ftplib.FTP( self.srvHost, self.srvUser, self.srvPassword )
                localFile = open( localFilePath, "wb" )
                try:
                    ftp.retrbinary( 'RETR ' + filetodlUrl, localFile.write )
                except:
                    logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )
                    #import traceback; traceback.print_exc()
                localFile.close()
                ftp.quit()

            # remove file if size is 0 bytes and report error if exists error
            if isTBN and os.path.isfile( localFilePath ):
                if os.path.getsize( localFilePath ) <= 0:
                    os.remove( localFilePath )
                else:
                    thumb_size = int( self.thumb_size_on_load )
                    thumbnail = makeThumbnails( localFilePath, thumbnail, w_h=( thumb_size, thumb_size ) )

            if thumbnail and os.path.isfile( thumbnail ) and hasattr( listitem, 'setThumbnailImage' ):
                #if listitem and hasattr( listitem, 'setThumbnailImage' ):
                listitem.setThumbnailImage( thumbnail )
        except:
            logger.LOG( logger.LOG_DEBUG, "_downloaddossier: Exception - Impossible de telecharger le fichier: %s", remoteFilePath )
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )
            #import traceback; traceback.print_exc()


class InfoWarehouseEltTreeXMLFTP( InfoWarehouse ):
    """
    Class contenant tous les informations dans un fichier XML sur serveur FTP necessaires a la description d'un item
    Pour des raisons de performance, on instanciera cette classe une seule fois au demarrage du script
    Cette classe utilise ElementTree
    """
    def __init__( self, *args, **kwargs ):
        # Import elementtree
        import elementtree.ElementTree as ET

        logger.LOG( logger.LOG_DEBUG,'InfoWarehouseEltTreeXMLFTP starts')
        self.mainwin  = kwargs[ "mainwin" ]

        self._get_settings()
        self.thumb_size_on_load = self.mainwin.settings[ "thumb_size" ]
        
        # On recupere le fichier de description des items
        self._downloadFile( self.srvItemDescripDir + self.srvItemDescripFile, isTBN=False )
        
        tree = ET.parse( open( os.path.join(self.mainwin.CacheDir,self.srvItemDescripFile ), 'r' ) )
        self.elemroot = tree.getroot()

    
    def _getImage( self, pictureURL, updateImage_cb=None, listitem=None ):
        cached_thumbs = set_cache_thumb_name( pictureURL )
        if not os.path.exists( cached_thumbs[ 0 ] ) or not os.path.exists( cached_thumbs[ 1 ] ):
            try: self.getImage_thread.cancel()
            except: pass
            self.getImage_thread = Thread( target=self._thread_getImage, args=( pictureURL, updateImage_cb, listitem ) )
            self.getImage_thread.start()

    def _thread_getImage( self, pictureURL, updateImage_cb=None, listitem=None ):
        """
        Recupere l'image dans un thread separe
        """
        # Telechargement de l'image
        self._downloadFile( pictureURL, listitem=listitem )
        #checkPathPic = set_cache_thumb_name( pictureURL )#os.path.join(self.mainwin.CacheDir, os.path.basename(pictureURL))
        
        cached_thumbs = set_cache_thumb_name( pictureURL )

        if os.path.exists( cached_thumbs[ 1 ] ):
            previewPicture = cached_thumbs[ 1 ]
        else:
            previewPicture = None
        
        # Notifie la callback de mettre a jour l'image
        if updateImage_cb:
            try: updateImage_cb( cached_thumbs[ 1 ] )
            except TypeError: pass

    def check_thumb_size( self ):
        if self.thumb_size_on_load != self.mainwin.settings[ "thumb_size" ]:
            self.thumb_size_on_load = self.mainwin.settings[ "thumb_size" ]
            try:
                BASE_THUMBS_PATH = os.path.join( xbmc.translatePath( "P:\\script_data" ), __script__, "Thumbnails" )
                shutil.rmtree( BASE_THUMBS_PATH )
            except:
                logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )

    def getInfo( self, itemName=None, itemType=None, itemId=None, updateImage_cb=None, listitem=None ):
        self.check_thumb_size()
        """ 
        Lit les info 
        retourne fileName, title, version, language, date , previewPicture, previewVideoURL, description_fr, description_en
        Fonction abstraite
        """
        """ reads info """
        fileName        = itemName # Defaukt value if we don't find itemname
        title           = itemName # Defaukt value if we don't find itemname
        version         = None
        language        = None
        date            = None
        previewPicture  = None
        thumbnail       = ""
        #thumbnail       = None
        previewVideoURL = None
        description_fr  = None
        description_en  = None

        cat = None
        try:
            if itemType == "Themes":
                cat = self.elemroot.find('skins')
            elif itemType == "Scrapers":
                cat = self.elemroot.find('scrapers')
            elif itemType == "Scripts":
                cat = self.elemroot.find('scripts')
            elif itemType == "Plugins Musique":
                cat = self.elemroot.find('plugins').find('musicplugin')
            elif itemType == "Plugins Images":
                cat = self.elemroot.find('plugins').find('pictureplugin')
            elif itemType == "Plugins Programmes":
                cat = self.elemroot.find('plugins').find('programplugin')
            elif itemType == "Plugins Vidéos":
                cat = self.elemroot.find('plugins').find('videoplugin')
                
            if cat != None:
                for item in cat.findall( "entry" ):
                    filename_raw = item.findtext('fileName')
                    if ( filename_raw not in ('', None) ):
                        fileName = filename_raw
                        if ( itemName == fileName ):
                            title_raw = item.findtext('title')
                            if ( title_raw not in ('', None) ):
                                title = title_raw
                            version_raw = item.findtext('version')
                            if ( version_raw not in ('', None) ):
                                version = version_raw
                            language_raw = item.findtext('lang')
                            if ( language_raw not in ('', None) ):
                                language = language_raw
                            date_raw = item.findtext('date')
                            if ( date_raw not in ('', None) ):
                                date = date_raw
                            added_raw = item.findtext('added')
                            if ( added_raw not in ('', None) ):
                                added = added_raw
                            previewPictureURL_raw = item.findtext('previewPictureURL')
                            if ( previewPictureURL_raw not in ('', None) ):
                                previewPictureURL = previewPictureURL_raw
                                
                                # On verifie si l'image serait deja la
                                thumbnail, checkPathPic = set_cache_thumb_name( previewPictureURL )
                                if thumbnail and os.path.isfile( thumbnail ) and hasattr( listitem, 'setThumbnailImage' ):
                                    #if listitem and hasattr( listitem, 'setThumbnailImage' ):
                                    listitem.setThumbnailImage( thumbnail )
                                if os.path.exists(checkPathPic):
                                    previewPicture = checkPathPic
                                else:
                                    # Telechargement et mise a jour de l'image (thread de separe)
                                    previewPicture = checkPathPic#"downloading"
                                    self._getImage( previewPictureURL, updateImage_cb=updateImage_cb, listitem=listitem )
                            previewVideoURL_raw = item.findtext('previewVideoURL')
                            if ( previewVideoURL_raw not in ('', None) ):
                                previewVideoURL = previewVideoURL_raw
                            description_fr_raw = item.findtext('description_fr')
                            if ( description_fr_raw not in ('', None) ):
                                description_fr = description_fr_raw
                            description_en_raw = item.findtext('description_en')
                            if ( description_en_raw != '' ):
                                description_en = description_en_raw
                                
                            author_raw = item.findtext('author')
                            if ( author_raw not in ('', None) ):
                                author = author_raw
                                
                            # We exit the loop since we found the file we were looking for
                            #item.clear()
                            break
        

               
        except Exception, e:
            #import traceback; traceback.print_exc()
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )
        
        return fileName, title, version, language, date, added, previewPicture, previewVideoURL, description_fr, description_en, thumbnail, author

    def _get_settings( self, defaults=False  ):
        """ reads settings from conf file """
        self.settings           = Settings().get_settings( defaults=defaults )
        self.srvHost            = self.mainwin.configManager.getSrvHost()
        self.srvPassword        = self.mainwin.configManager.getSrvPassword()
        self.srvUser            = self.mainwin.configManager.getSrvUser()
        self.srvItemDescripDir  = self.mainwin.configManager.getSrvItemDescripDir()
        self.srvItemDescripFile = self.mainwin.configManager.getSrvItemDescripFile()
        
        logger.LOG( logger.LOG_DEBUG,self.srvHost)
        logger.LOG( logger.LOG_DEBUG,self.srvItemDescripDir)

    def _downloadFile( self, remoteFilePath, isTBN=True, listitem=None ):
        """
        Fonction de telechargement commune : version, archive, script de mise a jour
        """
        try:
            filetodlUrl = remoteFilePath
            if isTBN:
                thumbnail, localFilePath = set_cache_thumb_name( remoteFilePath )
            else:
                thumbnail = ""
                localFilePath = os.path.join( self.mainwin.CacheDir, os.path.basename( remoteFilePath ) )

            if not os.path.isfile( localFilePath ):
                ftp = ftplib.FTP( self.srvHost, self.srvUser, self.srvPassword )
                localFile = open( localFilePath, "wb" )
                try:
                    ftp.retrbinary( 'RETR ' + filetodlUrl, localFile.write )
                except:
                    #import traceback; traceback.print_exc()
                    logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )
                localFile.close()
                ftp.quit()

            # remove file if size is 0 bytes and report error if exists error
            if isTBN and os.path.isfile( localFilePath ):
                if os.path.getsize( localFilePath ) <= 0:
                    os.remove( localFilePath )
                else:
                    thumb_size = int( self.thumb_size_on_load )
                    thumbnail = makeThumbnails( localFilePath, thumbnail, w_h=( thumb_size, thumb_size ) )

            if thumbnail and os.path.isfile( thumbnail ) and hasattr( listitem, 'setThumbnailImage' ):
                #if listitem and hasattr( listitem, 'setThumbnailImage' ):
                listitem.setThumbnailImage( thumbnail )
        except:
            #import traceback; traceback.print_exc()
            logger.LOG( logger.LOG_DEBUG, "_downloaddossier: Exception - Impossible de telecharger le fichier: %s", remoteFilePath )
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )

class ItemInfosManager:
    """
    Class gerant toutes les description quelque soit leur provenance (FTP, SQL ...)
    """
    def __init__( self, *args, **kwargs ):
        self.mainwin = kwargs[ "mainwin" ]
        self.create_info_warehouses()

    def create_info_warehouses( self ):
        #self.infoWarehouseFTP = InfoWarehouseBSoupXMLFTP( mainwin=self.mainwin )
        self.infoWarehouseFTP = InfoWarehouseEltTreeXMLFTP( mainwin=self.mainwin )
        #infoWarehouseSQL = InfoWarehouseXMLSQL( mainwin=mainwin )
        
        #TODO: check sur le type afin de passer le bon info warehouse a la classe ItemDescription
    
    def get_info_warehouse( self ):
        return self.infoWarehouseFTP

