
# Modules general
import os
import sys
import shutil
import ftplib
from threading import Thread
from traceback import print_exc

import elementtree.ElementTree as ET

# Modules XBMC
import xbmc

# Modules custom
from utilities import *
from CONF import configCtrl
from pil_util import makeThumbnails
import Item


#FONCTION POUR RECUPERER LES LABELS DE LA LANGUE.
_ = sys.modules[ "__main__" ].__language__
LANGUAGE_IS_FRENCH = ( xbmc.getLanguage().lower() == "french" )


BASE_THUMBS_PATH = os.path.join( sys.modules[ "__main__" ].SPECIAL_SCRIPT_DATA, "Thumbnails" )


class InfosWarehouse:
    """ Class Abstraite contenant toutes les informations necessaires a la description d'un item """
    def __init__( self, kwargs ):
        self.fileName        = kwargs.get( "fileName" )        or ""
        self.title           = kwargs.get( "title" )           or ""
        self.version         = kwargs.get( "version" )         or ""
        #self.language        = kwargs.get( "language" )        or ""
        self.date            = kwargs.get( "date" )            or ""
        self.added           = kwargs.get( "added" )           or ""
        self.previewPicture  = kwargs.get( "previewPicture" )  or ""
        self.thumbnail       = kwargs.get( "thumbnail" )       or ""
        self.previewVideoURL = kwargs.get( "previewVideoURL" ) or ""
        #self.description_fr  = kwargs.get( "description_fr" )  or ""
        #self.description_en  = kwargs.get( "description_en" )  or ""
        #self.description     = kwargs.get( "description" )     or ""
        self.author          = kwargs.get( "author" )          or ""
        self.itemType        = kwargs.get( "itemType" )        or ""
        self.itemId          = kwargs.get( "itemId" )          or ""
        self.thumb_size_on_load = kwargs.get( "itemId" )          or ""
        self.previewPictureURL = kwargs.get( "previewPictureURL" ) or "None"


class updateIWH( InfosWarehouse ):
    def __init__( self, kwargs ):
        InfosWarehouse.__init__( self, kwargs )
        self.set_description( kwargs )
        self.set_lang( kwargs )

    def set_description( self, kwargs ):
        self.description = ""
        try:
            desc_fr = kwargs.get( "description_fr" )
            desc_us = kwargs.get( "description_en" )
            if LANGUAGE_IS_FRENCH:
                self.description = desc_fr or desc_us or ""
            else:
                self.description = desc_us or desc_fr or ""
        except:
            pass

    def set_lang( self, kwargs ):
        # We use ISO 2 Letter Language Codes ( http://reference.sitepoint.com/html/lang-codes )
        # fr <-> French / en <-> English / fr <-> French / multi <-> Multilanguages / de <-> German / es <-> Spanish / nl <-> Dutch / fi <-> Finnish / sv <-> Swedish
        #lang = ( kwargs.get( "language" ) or "" ).lower().replace( "fr", _( 609 ) ).replace( "en", _( 610 ) ).replace( "multi", _( 611 ) ).replace( "de", _( 615 ) ).replace( "es", _( 616 ) ).replace( "nl", _( 617 ) ).replace( "fi", _( 618 ) ).replace( "sv", _( 619 ) )
        lang = replaceStrs(( kwargs.get( "language" ) or "" ).lower(), ( "fr", _( 609 ) ), ( "en", _( 610 ) ), ( "multi", _( 611 ) ), ( "de", _( 615 ) ), ( "es", _( 616 ) ), ( "nl", _( 617 ) ), ( "fi", _( 618 ) ), ( "sv", _( 619 ) ) )
        self.language = ( lang or _( 612 ) ).replace( "-", " / " )


class ImageQueueElement:
    """ Structure d'un element a mettre dans la FIFO des images a telecharger """
    def __init__( self, url, updateImage_cb=None, listitem=None ):
        self.url            = url
        self.updateImage_cb = updateImage_cb
        self.listitem       = listitem

    def __repr__( self ):
        return "(%s, %s, %s)" % ( self.url, self.updateImage_cb, self.listitem )


class InfoWarehouseEltTreeXMLFTP:
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

        print "InfoWarehouseEltTreeXMLFTP starts"
        self.mainwin  = kwargs[ "mainwin" ]

        #self.thumb_size_on_load = self.mainwin.settings[ "thumb_size" ]

        # FIFO des images a telecharger
        self.image_queue = []

        # On recupere le fichier de description des items
        print "self._downloadFile", self.srvItemDescripDir + self.srvItemDescripFile
        self._downloadFile( self.srvItemDescripDir + self.srvItemDescripFile, isTBN=False )

        self.parse_xml_sections()
        
        self.stopUpdateImageThread = False # Flag indiquant si on doit stopper ou non le thread getImagesQueue_thread

    def update_Images( self ):
        """
        Recupere toutes les image dans la FIFO et met a jour l'appelant via la callBack
        """
        #print "update_Images"
        #print self.image_queue
        if ( len(self.image_queue) > 0 ):
#            try: self.getImagesQueue_thread.cancel()
#            except: pass
            self.getImagesQueue_thread = Thread( target=self._thread_getImagesQueue )
            self.getImagesQueue_thread.start()

    def cancel_update_Images(self):
        self.stopUpdateImageThread = True
        print "cancel_update_Images: Stopping theard ..."

        # On attend la fin du thread
        self.getImagesQueue_thread.join(10)
        print "cancel_update_Images: Thread STOPPED"
        
         # on vide la liste vide la Queue
        del self.image_queue[ : ]
        
    def _thread_getImagesQueue( self ):
        self.stopUpdateImageThread = False
        while ( len( self.image_queue ) > 0 and self.stopUpdateImageThread == False ):
            imageElt = self.image_queue.pop( 0 )
            cached_thumbs = set_cache_thumb_name( imageElt.url )
            if not os.path.exists( cached_thumbs[ 0 ] ) or not os.path.exists( cached_thumbs[ 1 ] ):
                # Telechargement de l'image
                self._downloadFile( imageElt.url, True, listitem=imageElt.listitem )

                if os.path.exists( cached_thumbs[ 1 ] ):
                    previewPicture = cached_thumbs[ 1 ]
                else:
                    previewPicture = set_cache_thumb_name( Item.THUMB_NOT_AVAILABLE )[ 1 ]

                # Notifie la callback de mettre a jour l'image
                if imageElt.updateImage_cb:
                    try:
                        imageElt.updateImage_cb( previewPicture, imageElt.listitem )
                    except TypeError:
                        print_exc()
                        
        if ( self.stopUpdateImageThread == True):
            print "_thread_getImagesQueue CANCELLED"

    def check_thumb_size( self ):
        if self.thumb_size_on_load != self.mainwin.settings[ "thumb_size" ]:
            self.thumb_size_on_load = self.mainwin.settings[ "thumb_size" ]
            try:
                shutil.rmtree( BASE_THUMBS_PATH )
            except:
                print_exc()

    def parse_xml_sections( self ):
        try:
            elems = ET.parse( open( os.path.join( self.configManager.CACHEDIR, self.srvItemDescripFile ), "r" ) ).getroot()
    
            self.cat_skins         = elems.find( "skins" ).findall( "entry" )
            self.cat_scripts       = elems.find( "scripts" ).findall( "entry" )
            #self.cat_scrapers      = elems.find( "scrapers" ).findall( "entry" )
    
            elemsplugins = elems.find( "plugins" )
            self.cat_videoplugin   = elemsplugins.find( "videoplugin" ).findall( "entry" )
            self.cat_musicplugin   = elemsplugins.find( "musicplugin" ).findall( "entry" )
            self.cat_pictureplugin = elemsplugins.find( "pictureplugin" ).findall( "entry" )
            self.cat_programplugin = elemsplugins.find( "programplugin" ).findall( "entry" )
            
            elemsscrapers = elems.find( "scrapers" )
            self.cat_musicscraper  = elemsscrapers.find( "musicscraper" ).findall( "entry" )
            self.cat_videoscraper  = elemsscrapers.find( "videoscraper" ).findall( "entry" )

            del elemsplugins
            del elemsscrapers
            del elems
        except:
            self.cat_skins         = None
            self.cat_scripts       = None
            self.cat_videoplugin   = None
            self.cat_musicplugin   = None
            self.cat_pictureplugin = None
            self.cat_programplugin = None
            self.cat_musicscraper  = None
            self.cat_videoscraper  = None
            print "Error while parsing installeur_content.xml"
            print_exc()

    def getInfo( self, itemName=None, itemType=None, itemId=None, updateImage_cb=None, listitem=None ):
        #self.check_thumb_size()
        """
        Lit les info
        retourne fileName, title, version, language, date , previewPicture, previewVideoURL, description_fr, description_en
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
        #description_en  = None
        #author          = None

        try:
            category = None
            #Item.TYPE_SCRAPER
            if   itemType == Item.TYPE_SKIN:            category = self.cat_skins
            elif itemType == Item.TYPE_SCRIPT:          category = self.cat_scripts
            #elif itemType == Item.TYPE_SCRAPER:         category = self.cat_scrapers
            elif itemType == Item.TYPE_SCRAPER_MUSIC:   category = self.cat_musicscraper
            elif itemType == Item.TYPE_SCRAPER_VIDEO:   category = self.cat_videoscraper
            elif itemType == Item.TYPE_PLUGIN_VIDEO:    category = self.cat_videoplugin
            elif itemType == Item.TYPE_PLUGIN_MUSIC:    category = self.cat_musicplugin
            elif itemType == Item.TYPE_PLUGIN_PICTURES: category = self.cat_pictureplugin
            elif itemType == Item.TYPE_PLUGIN_PROGRAMS: category = self.cat_programplugin

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
                            print "getInfo: previewPictureURL"
                            print previewPictureURL
                            if not previewPictureURL and hasattr( listitem, "setThumbnailImage" ):
                                listitem.setThumbnailImage( Item.THUMB_NOT_AVAILABLE )
                                #TODO: clean
                                previewPictureURL = 'None'
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
                listitem.setThumbnailImage( Item.THUMB_NOT_AVAILABLE )

            #i = updateIWH( locals() )
            #print i.fileName, i.description
        except:
            print_exc()

        print locals()
        return updateIWH( locals() )
        #return fileName, title, version, language, date, added, previewPicture, \
        #    previewVideoURL, description_fr, description_en, thumbnail, author

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
                    print "_downloaddossier: Exception - Impossible de telecharger le fichier: %s" % remoteFilePath
                    print_exc()
                    thumbnail, localFilePath = "", ""
                localFile.close()
                ftp.quit()

            # remove file if size is 0 bytes and report error if exists error
            if isTBN and localFilePath and os.path.isfile( localFilePath ):
                if os.path.getsize( localFilePath ) <= 0:
                    os.remove( localFilePath )
                else:
                    thumb_size = int( self.thumb_size_on_load )
                    thumbnail = makeThumbnails( localFilePath, thumbnail, w_h=( thumb_size, thumb_size ) )
                    if thumbnail == "": thumbnail = localFilePath

            if thumbnail and os.path.isfile( thumbnail ) and hasattr( listitem, "setThumbnailImage" ):
                listitem.setThumbnailImage( thumbnail )
                listitem.setProperty( "fanartpicture", "" )
                listitem.setProperty( "fanartpicture", thumbnail )
        except:
            print "_downloaddossier: Exception - Impossible de telecharger le fichier: %s" % remoteFilePath
            print_exc()


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

