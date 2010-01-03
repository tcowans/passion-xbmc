"""
ItemInstaller: this module allows download and install of an item (addons: script, plugin, scraper, skin ...)
"""

# Modules general
import os
import sys
import httplib
from traceback import print_exc

# Modules custom
#from utilities import *
import CONF
import Item
from FileManager import fileMgr

httplib.HTTPConnection.debuglevel = 1

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
    #def __init__( self , itemId, type, filesize ):
    def __init__( self , name, type ):
        #self.itemId          = itemId       # Id of the server item 
        self.name            = name         # Name of teh item
        self.type            = type         # XBMC Type of the item
        #self.typeInstallPath = installPath  # Install Path for this type of item
        self.typeInstallPath = Item.get_install_path( type )  # Install Path for this type of item
        #self.filesize        = filesize     # Size of the file to download
        
        self.configManager = CONF.configCtrl()
        if not self.configManager.is_conf_valid: raise
        self.CACHEDIR = self.configManager.CACHEDIR
        self.fileMgr = fileMgr()
        
        # NOTE: need to be set in a subclass before calling isAlreadyInstalled or deleteInstalledItem
        self.scraperName     = None
        self.scraperFileList = None # List of teh file for a scraper (xml, image ...)
        #self.installNameList = None
        self.installName     = None # Name of the addon used by XBMC: i.e script dir name, plugin dir name, skin dir name, scraper xml file name
        self.destinationPath = None # 

    def downloadItem( self, msgFunc=None,progressBar=None ):
        """
        Download an item form the server
        Returns the status of the download attempt : OK | ERROR
        """
        pass

    def isAlreadyInstalled( self ):
        """
        Check if extracted item is already installed
        Needs to be called after extractItem (destinationPath has to be determined first)
        ==> self.destinationPath need to be set (in a subclass) before calling this method
        """
        result = False
        if self.type != Item.TYPE_SCRAPER:
            if os.path.exists( self.destinationPath ):
                result = True
        else:
            #Scraper
            
            #if self.scraperName != None:
            #or
            if len(self.scraperFileList) > 0:
                # Check if scraper exist (only done on xml file)
                if os.path.exists( os.path.join( self.destinationPath, self.installName + ".xml" ) ):
                #if os.path.exists( os.path.join( self.destinationPath, os.path.splitext(self.scraperFileList[0])[0] + ".xml" ) ):
                    result = True
                
        #TODO : Scraper already installed case
        return result

    def installItem( self, msgFunc=None,progressBar=None ):
        """
        Install item (download + extract + copy)
        Needs to be called after extractItem
        """
        pass


    def getItemInstallName( self ):
        """
        Return the real name of the item (install name) not the name for description
        """
        return self.installName

    def _getItemPaths( self ):
        """
        Returns the list of path of the current item (dir or file path)
        NOTE: self.destinationPath need to be set (in a subclass) before calling this method
        """
        
        #TODO: return path or name in both scenario
        
        paths = []
        if self.type == Item.TYPE_SCRAPER:
            # Files case
            #if self.scraperName != None:
            if len( self.scraperFileList ) > 0:
                for scraperFile in self.scraperFileList:
                    paths.append( os.path.join( self.destinationPath, scraperFile ) )
                # Note: for time being we only delete the XML
                # TODO: delete images and other file too?
                #item_path = os.path.join( self.destinationPath, self.scraperName + ".xml" )
                #item_path = self.scraperFileList
        else:
            # Directory case
            paths.append( self.destinationPath )
        return paths

    def deleteInstalledItem( self ):
        """
        Delete an item already installed (file or directory)
        Return True if success, False otherwise
        NOTE: self.destinationPath need to be set (in a subclass) before calling this method
        """
        result = None
        item_paths = self._getItemPaths ()

        if len( item_paths ) > None:
            for path in item_paths:
                result = self.fileMgr.deleteItem( path )
                if result == False:
                    print "deleteInstalledItem: Impossible to delete one of the element in the item: %s" % path
                    break
        else:
            result = False
            print "deleteInstalledItem: Item invalid - error"
        return result

    def renameInstalledItem( self, inputText ):
        """
        Rename an item already installed (file or directory)
        Return True if success, False otherwise
        NOTE: self.destinationPath need to be set (in a subclass) before calling this method
        """
        
        #TODO; iuse same fomat between delete and rename: path or name
        
        
        result = None
        item_paths = self._getItemPaths ()
        print "renameInstalledItem"

        if len( item_paths ) > None:
            for path in item_paths:
                print "Renaming %s by %s"%(path, path.replace( self.installName, inputText))
                result = self.fileMgr.renameItem( None, path, path.replace( self.installName, inputText) )
                if result == False:
                    print "renameInstalledItem: Impossible to rename one of the element in the item: %s" % path
                    break
        else:
            result = False
            print "renameInstalledItem: Item invalid - error"
        return result



class ArchItemInstaller(ItemInstaller):
    """
    Installer from an archive
    """

    #def __init__( self , itemId, type, filesize ):
    def __init__( self , name, type ):
        #ItemInstaller.__init__( self, itemId, type, filesize )
        ItemInstaller.__init__( self, name, type )

        #TODO: support progress bar display
        self.displayProgBar      = True 
        self.downloadArchivePath = None # Path of the archive to extract
        #self.destinationPath     = None # Path of the installation directory (i.e script dir path, plugin dir path, skin dir path, scraper xml file path)
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
                progressBar.update( percent, "Extraction:", ( self.name ) )
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
                        
                        # Get scraper file's name
                        try:
                            self.scraperFileList = os.listdir( str( self.extractedDirPath ) )
                            #self.installNameList = os.listdir( str( self.extractedDirPath ) )
                            #self.scraperName = os.path.splitext(self.scraperFileList[0])[0]
                            self.installName = os.path.splitext(self.scraperFileList[0])[0]
                            print "self.scraperFileList"
                            print self.scraperFileList
                            #print "self.scraperName"
                            #print self.scraperName
                        except Exception, e:
                            print "ArchItemInstaller: Exception in extractItem while listing scraper files: %s" % self.extractedDirPath
                            print_exc()
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
                        print "Erreur durant l'extraction de %s - impossible d'extraire le nom du repertoire" % archive
                        status = "ERROR"
                    else:
                        # Extraction sucessfull
                        self.destinationPath = os.path.join( self.typeInstallPath, os.path.basename( file_path ) )
                        #self.installNameList = [ os.path.basename( file_path ) ] # For the future if we manage package of addons
                        self.installName = os.path.basename( file_path )
                        self.extractedDirPath = file_path
                        print self.destinationPath
                #TODO: add skin case (requirements need to be defined first)
                del extractor
                
                #print self.type
                #print self.destinationPath
                #print self.extractedDirPath
            percent = 100
            if progressBar != None:
                progressBar.update( percent, "Fin Extraction", ( self.name ) )
        else:
            print "extractItem - Archive does not exist - extraction impossible"
            status = "ERROR"
        print "self.destinationPath"
        print self.destinationPath
        print "self.installName"
        print self.installName
        #return status, self.type, self.destinationPath, self.extractedDirPath
        return status

#    def isAlreadyInstalled( self ):
#        """
#        Check if extracted item is already installed
#        Needs to be called after extractItem (destinationPath has to be determined fisrt)
#        """
#        result = False
#        if self.type != Item.TYPE_SCRAPER:
#            if os.path.exists( self.destinationPath ):
#                result = True
#        else:
#            #Scraper
#            if self.scraperName != None:
#                # Check if scraper exist (only done on xml file)
#                if os.path.exists( os.path.join( self.destinationPath, self.scraperName + ".xml" ) ):
#                    result = True
#                
#        #TODO : Scraper already installed case
#        return result
    
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
                print "ItemInstaller::installItem - Starting item copy"
                try:
                    #if ( OK == bool( self.extractedDirPath ) ) and os.path.exists( self.extractedDirPath ):
                    if os.path.exists( self.extractedDirPath ):
                        extractor.copy_inside_dir( self.extractedDirPath, self.destinationPath )
                        OK = True
                    else:
                        print "ItemInstaller::installItem - self.extractedDirPath does not exist"
                except Exception, e:        
                    print "ItemInstaller::installItem - Exception during copy of the directory %s" % self.extractedDirPath
                    print_exc()
                    process_error = True
                print "Install Scraper completed"
            else:
                # Cas des scripts et plugins
                # --------------------------
                # Recuperons le nom du repertorie a l'interieur de l'archive:
                print "ItemInstaller::installItem - Starting item copy"
                try:
                    #if ( OK == bool( self.extractedDirPath ) ) and os.path.exists( self.extractedDirPath ):
                    if os.path.exists( self.extractedDirPath ):
                        extractor.copy_dir( self.extractedDirPath, self.destinationPath )
                        OK = True
                    else:
                        print "ItemInstaller::installItem - self.extractedDirPath does not exist"
                except Exception, e:        
                    print "ItemInstaller::installItem - Exception during copy of the directory %s" % self.extractedDirPath
                    print_exc()
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
        print "installItem: Download and install case"
        percent = 0
        result  = "OK" # result after install :[ OK | ERROR | ALREADYINSTALLED |CANCELED]       
        
        
        print "installItem: Download via itemInstaller"
        if self.status == "INIT":
            #TODO: support message callback in addition of pb callback
            #statusDownload = self.downloadItem( msgFunc=msgFunc, progressBar=progressBar )
            statusDownload, downloadArchivePath = self.downloadItem( progressBar=progressBar )
            print "installItem: statusDownload and downloadArchivePath"
            print statusDownload
            print downloadArchivePath
            print 
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



class DirItemInstaller(ItemInstaller):
    """
    Installer from a directory
    """

    #def __init__( self , itemId, type, filesize ):
    def __init__( self , name, type ):
        #ItemInstaller.__init__( self, itemId, type, filesize )
        ItemInstaller.__init__( self, name, type )

        #TODO: support progress bar display
        self.displayProgBar      = True 
        self.downloadArchivePath = None # Path of the archive to extract
        self.destinationPath     = None # Path of the destination directory
        self.extractedDirPath    = None # Path of the extracted item
        self.status              = "INIT" # Status of install :[INIT | OK | ERROR | ALREADYINSTALLED |CANCELED]       

             
