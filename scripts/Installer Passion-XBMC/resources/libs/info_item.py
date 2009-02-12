
#Modules general
import os
import sys
import shutil
import ftplib

#Other module
from threading import Thread
import elementtree.ElementTree as ET

#modules XBMC
import xbmc

#modules custom
from utilities import *
from CONF import configCtrl
try:
    from pil_util import makeThumbnails
except ImportError:
    makeThumbnails = None

#module logger
try:
    logger = sys.modules[ "__main__" ].logger
except:
    import script_log as logger


#FONCTION POUR RECUPERER LES LABELS DE LA LANGUE.
_ = sys.modules[ "__main__" ].__language__

BASE_THUMBS_PATH = os.path.join( sys.modules[ "__main__" ].SPECIAL_SCRIPT_DATA, "Thumbnails" )


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
        added           = None
        previewPicture  = None
        thumbnail       = ""
        previewVideoURL = None
        description_fr  = None
        description_en  = None
        author          = None

        return fileName, title, version, language, date , previewPicture, previewVideoURL, description_fr, description_en, thumbnail


class InfoWarehouseEltTreeXMLFTP( InfoWarehouse ):
    """
    Class contenant tous les informations dans un fichier XML sur serveur FTP necessaires a la description d'un item
    Pour des raisons de performance, on instanciera cette classe une seule fois au demarrage du script
    Cette classe utilise ElementTree
    """
    def __init__( self, *args, **kwargs ):
        self.configManager = configCtrl()
        if not self.configManager.is_conf_valid: raise

        self.srvHost            = self.configManager.host
        self.srvPassword        = self.configManager.password
        self.srvUser            = self.configManager.user
        self.srvItemDescripDir  = self.configManager.itemDescripDir
        self.srvItemDescripFile = self.configManager.itemDescripFile

        logger.LOG( logger.LOG_DEBUG,"InfoWarehouseEltTreeXMLFTP starts")
        self.mainwin  = kwargs[ "mainwin" ]

        self.thumb_size_on_load = self.mainwin.settings[ "thumb_size" ]

        # On recupere le fichier de description des items
        self._downloadFile( self.srvItemDescripDir + self.srvItemDescripFile, isTBN=False )

        self.parse_xml_sections()

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

        cached_thumbs = set_cache_thumb_name( pictureURL )

        if os.path.exists( cached_thumbs[ 1 ] ):
            previewPicture = cached_thumbs[ 1 ]
        else:
            previewPicture = set_cache_thumb_name( "passion-noImageAvailable.jpg" )[ 1 ]

        # Notifie la callback de mettre a jour l'image
        if updateImage_cb:
            try:
                updateImage_cb( previewPicture, listitem )
            except TypeError:
                logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )

    def check_thumb_size( self ):
        if self.thumb_size_on_load != self.mainwin.settings[ "thumb_size" ]:
            self.thumb_size_on_load = self.mainwin.settings[ "thumb_size" ]
            try:
                shutil.rmtree( BASE_THUMBS_PATH )
            except:
                logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )

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
        retourne fileName, title, version, language, date , previewPicture, previewVideoURL, description_fr, description_en
        Fonction abstraite
        """
        """ reads info """
        fileName        = itemName # default value if we don't find itemname
        title           = itemName # default value if we don't find itemname
        version         = None
        language        = None
        date            = None
        added           = None
        previewPicture  = None
        thumbnail       = ""
        previewVideoURL = None
        description_fr  = None
        description_en  = None
        author          = None

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
                            description_en    = item.findtext( "description_en" )
                            author            = item.findtext( "author" )

                            previewPictureURL = item.findtext( "previewPictureURL" )
                            if not previewPictureURL and hasattr( listitem, "setThumbnailImage" ):
                                listitem.setThumbnailImage( "passion-noImageAvailable.jpg" )
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
                                    self._getImage( previewPictureURL, updateImage_cb=updateImage_cb, listitem=listitem )
                            notfound = False
                            break

            if notfound and hasattr( listitem, "setThumbnailImage" ):
                listitem.setThumbnailImage( "passion-noImageAvailable.jpg" )

        except:
            #import traceback; traceback.print_exc()
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )

        return fileName, title, version, language, date, added, previewPicture, \
            previewVideoURL, description_fr, description_en, thumbnail, author

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
                localFilePath = os.path.join( self.configManager.CACHEDIR, os.path.basename( remoteFilePath ) )

            name, ext = os.path.splitext( filetodlUrl )
            if ext and not os.path.isfile( localFilePath ):
                ftp = ftplib.FTP( self.srvHost, self.srvUser, self.srvPassword )
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
            if isTBN and localFilePath and os.path.isfile( localFilePath ):
                if os.path.getsize( localFilePath ) <= 0:
                    os.remove( localFilePath )
                else:
                    thumb_size = int( self.thumb_size_on_load )
                    if makeThumbnails:
                        thumbnail = makeThumbnails( localFilePath, thumbnail, w_h=( thumb_size, thumb_size ) )
                    else:
                        thumbnail = localFilePath

            if thumbnail and os.path.isfile( thumbnail ) and hasattr( listitem, "setThumbnailImage" ):
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
        self.infoWarehouseFTP = InfoWarehouseEltTreeXMLFTP( mainwin=self.mainwin )
        #infoWarehouseSQL = InfoWarehouseXMLSQL( mainwin=mainwin )

        #TODO: check sur le type afin de passer le bon info warehouse a la classe ItemDescription

    def get_info_warehouse( self ):
        return self.infoWarehouseFTP

