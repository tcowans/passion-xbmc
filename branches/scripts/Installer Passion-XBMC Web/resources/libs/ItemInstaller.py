"""
ItemInstaller: this module allows download and install an item
"""
import os
import sys
import traceback

# SQLite
from pysqlite2 import dbapi2 as sqlite

#Other module
import urllib
import urllib2, httplib

httplib.HTTPConnection.debuglevel = 1

# Module logger
try:
    logger = sys.modules[ "__main__" ].logger
except:
    import script_log as logger

# Modules custom
#from utilities import *
import CONF
import Item

#FONCTION POUR RECUPERER LES LABELS DE LA LANGUE.
_ = sys.modules[ "__main__" ].__language__

class cancelRequest(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class ItemInstaller:
    """
    ABSTRACT
    """
    
    #def __init__( self , itemId, type, installPath, filesize ):
    def __init__( self , itemId, type, filesize ):
        self.itemId          = itemId       # Id of the server item 
        self.type            = type         # Type of the item
        #self.typeInstallPath = installPath  # Install Path for this type of item
        self.typeInstallPath = Item.get_install_path( type )  # Install Path for this type of item
        self.filesize        = filesize     # Size of the file to download
        
        self.configManager = CONF.configCtrl()
        if not self.configManager.is_conf_valid: raise
        self.CACHEDIR = self.configManager.CACHEDIR
        
        
    def downloadItem( self, msgFunc=None,progressBar=None ):
        """
        Download an item form the server
        Returns the status of the download attemos : OK | ERROR
        """
        pass

    def isAlreadyInstalled( self ):
        """
        Check if extracted item is already installed
        Needs to be called after extractItem
        """
        pass

    def installItem( self, msgFunc=None,progressBar=None ):
        """
        Install item (download + extract + copy)
        Needs to be called after extractItem
        """
        pass


class ArchItemInstaller(ItemInstaller):
    """
    Installer from an archive
    """

    def __init__( self , itemId, type, filesize ):
        ItemInstaller.__init__( self, itemId, type, filesize )

        #TODO: support progress bar display
        self.displayProgBar      = True 
        self.downloadArchivePath = None # Path of the archive to extract
        self.destinationPath     = None # Path of the destination directory
        self.extractedDirPath    = None # Path of the extracted item
        self.status              = "INIT" # Status of install :[INIT | OK | ERROR | ALREADYINSTALLED |CANCELED]       

    def extractItem( self, msgFunc=None,progressBar=None ):
        """
        Extract item in temp location
        """
        #TODO: update a progress bar during extraction
        print "extractItem - path" 
        print self.downloadArchivePath
        status  = "OK" # Status of download :[OK | ERROR | CANCELED]      
        percent = 33
        # Check if the archive exists
        if os.path.exists( self.downloadArchivePath ):
            if progressBar != None:
                progressBar.update( percent, "Extraction:", ( self.baseurl + str(self.itemId) ) )
            if self.downloadArchivePath.endswith( 'zip' ) or self.downloadArchivePath.endswith( 'rar' ):
                import extractor
                process_error = False
                # Extraction in cache directory (if OK copy later on to the correct location)
                file_path, OK = extractor.extract( self.downloadArchivePath, report=True )

                if self.type == Item.TYPE_SCRAPER:
                    # Scrapers
                    # ----------------
                    #self.extracter.extract( archive, self.localdirList[ self.downloadTypeList.index( self.type ) ] )
                    if ( OK == bool( file_path ) ) and os.path.exists( file_path ):
                        # Extraction sucessfull
                        self.destinationPath = self.typeInstallPath
                        self.extractedDirPath = file_path
                    else:
                        status = "ERROR"
                else:
                    # Cas des scripts et plugins
                    # --------------------------
                    # Recuperons le nom du repertoire a l'interieur de l'archive:
                    dirName = ""
                    if ( OK == bool( file_path ) ) and os.path.exists( file_path ):
                        dirName = os.path.basename( file_path )#self.extracter.getDirName( archive )
                        
    
                    if dirName == "":
                        installError = _( 139 ) % archive
                        logger.LOG( logger.LOG_ERROR, "Erreur durant l'extraction de %s - impossible d'extraire le nom du repertoire", archive )
                        status = "ERROR"
                    else:
                        # Extraction sucessfull
                        self.destinationPath = os.path.join( self.typeInstallPath, os.path.basename( file_path ) )
                        self.extractedDirPath = file_path
                        logger.LOG( logger.LOG_NOTICE, self.destinationPath )
                #TODO: add skin case (requirements need to be defined first)
                del extractor
                
                #print self.type
                #print self.destinationPath
                #print self.extractedDirPath
            percent = 100
            if progressBar != None:
                progressBar.update( percent, "Fin Extraction", ( self.baseurl + str(self.itemId) ) )
        else:
            print "extractItem - Archive does not exist - extraction impossible"
            status = "ERROR"
        #return status, self.type, self.destinationPath, self.extractedDirPath
        return status

    def isAlreadyInstalled( self ):
        """
        Check if extracted item is already installed
        Needs to be called after extractItem (destinationPath has to be determined fisrt)
        """
        result = False
        if self.type != Item.TYPE_SCRAPER:
            if os.path.exists( self.destinationPath ):
                result = True
        #TODO : Scraper already installed case
        return result
    
    def copyItem( self, msgFunc=None,progressBar=None ):
        """
        Install item from extracted archive
        Needs to be called after extractItem
        """
        #TODO: update a progress bar during copy
        import extractor
        OK = False
        # get install path
        process_error = False
        percent = 0
        if progressBar != None:
            progressBar.update( percent, "Copy:", ( self.extractedDirPath ) )
        if ( ( self.extractedDirPath != None ) and ( self.destinationPath != None ) ):
            if self.type == Item.TYPE_SCRAPER:
                # cas des Scrapers
                # ----------------
                logger.LOG( logger.LOG_DEBUG, "ItemInstaller::installItem - Starting item copy" )
                try:
                    #if ( OK == bool( self.extractedDirPath ) ) and os.path.exists( self.extractedDirPath ):
                    if os.path.exists( self.extractedDirPath ):
                        extractor.copy_inside_dir( self.extractedDirPath, self.destinationPath )
                        OK = True
                    else:
                        logger.LOG( logger.LOG_DEBUG, "ItemInstaller::installItem - self.extractedDirPath does not exist")
                except Exception, e:        
                    logger.LOG( logger.LOG_DEBUG, "ItemInstaller::installItem - Exception during copy of the directory %s", self.extractedDirPath )
                    logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )
                    process_error = True
                print "Install Scraper completed"
            else:
                # Cas des scripts et plugins
                # --------------------------
                # Recuperons le nom du repertorie a l'interieur de l'archive:
                logger.LOG( logger.LOG_DEBUG, "ItemInstaller::installItem - Starting item copy" )
                try:
                    #if ( OK == bool( self.extractedDirPath ) ) and os.path.exists( self.extractedDirPath ):
                    if os.path.exists( self.extractedDirPath ):
                        extractor.copy_dir( self.extractedDirPath, self.destinationPath )
                        OK = True
                    else:
                        logger.LOG( logger.LOG_DEBUG, "ItemInstaller::installItem - self.extractedDirPath does not exist")
                except Exception, e:        
                    logger.LOG( logger.LOG_DEBUG, "ItemInstaller::installItem - Exception during copy of the directory %s", self.extractedDirPath )
                    logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )
                    process_error = True
                print "Install item completed"

        del extractor
        percent = 100
        if progressBar != None:
            progressBar.update( percent, "Copy:", ( self.extractedDirPath ) )
        return OK

    def installItem( self, msgFunc=None,progressBar=None ):
        """
        Install item (download + extract + copy)
        Needs to be called after extractItem
        """
        print "Download and install case"
        percent = 0
        result  = "OK" # result after install :[ OK | ERROR | ALREADYINSTALLED |CANCELED]       
        
        
        print "Download via itemInstaller"
        if self.status == "INIT":
            #TODO: support message callback in addition of pb callback
            #statusDownload = self.downloadItem( msgFunc=msgFunc, progressBar=progressBar )
            statusDownload = self.downloadItem( progressBar=progressBar )
            if statusDownload == "OK":
                if self.extractItem( msgFunc=msgFunc, progressBar=progressBar ) == "OK":
                    if not self.isAlreadyInstalled():
                        print "installItem - Item is not yet installed - installing"
                        # TODO: in case of skin check skin is not the one currently used
                        if self.copyItem( msgFunc=msgFunc, progressBar=progressBar ) == False:
                            result = "ERROR"
                            print "installItem - Error during copy"
                        else:
                            self.status = "INSTALL_DONE"
                    else:
                        print "installItem - Item is already installed - stopping install"
                        result = "ALREADYINSTALLED"
                        self.status = "EXTRACTED"
            elif statusDownload == "CANCELED":
                result = "CANCELED"
                print "installItem - Install cancelled by the user"
            else:
                result = "ERROR"
                print "installItem - Error during download"
        elif self.status == "EXTRACTED":
            print "installItem - continue install"
            # TODO: in case of skin check skin is not the one currently used
            if self.copyItem( msgFunc=msgFunc, progressBar=progressBar ) == False:
                result = "ERROR"
                print "installItem - Error during copy"
            else:
                self.status = "INSTALL_DONE"
            

        return result, self.destinationPath



             
