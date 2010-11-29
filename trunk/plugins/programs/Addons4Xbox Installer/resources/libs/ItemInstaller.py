"""
ItemInstaller: this module allows download and install of an item (addons: script, plugin, scraper, skin ...)
"""

# Modules general
import os
import sys
import httplib
from traceback import print_exc
from time import sleep

# Modules custom
try:
    from Item import *
    from FileManager import fileMgr
    from utilities import copy_dir, copy_inside_dir
    from specialpath import *
    from XmlParser import parseAddonXml

except:
    print_exc()

httplib.HTTPConnection.debuglevel = 1

#FONCTION POUR RECUPERER LES LABELS DE LA LANGUE.
_ = sys.modules[ "__main__" ].__language__

# XBMC modules
import xbmc

class cancelRequest(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


class ItemInstaller:
    """
    ABSTRACT
    """
    # dictionary to hold addon info
    itemInfo = {}
        # id
        # name
        # type
        # version
        # author
        # disclaimer
        # summary
        # description
        # icon
        # fanart
        # changelog
        # library: path of python script
        # raw_item_sys_type: file | archive | dir
        # raw_item_path
        # install_path
        # temp_item_path
        # provides
        # required_lib
        
    def __init__( self ):
        
        self.CACHEDIR = DIR_CACHE
        self.fileMgr  = fileMgr()
        self.status   = "INIT" # Status of install :[ INIT | OK | ERROR | DOWNLOADED | EXTRACTED | ALREADYINSTALLED | ALREADYINUSE | CANCELED | INSTALL_DONE ]       
        
        # Clean cache directory
        self.fileMgr.delDirContent(self.CACHEDIR)
        
    def GetRawItem( self, msgFunc=None,progressBar=None ):
    #def downloadItem( self, msgFunc=None,progressBar=None ):
        """
        Get an item (local or remote)
        Set rawItemSysType - the filetype of the item: ARCHIVE | DIRECTORY
        Set rawItemPath - the path of the item: path of an archive or a directory
        Returns the status of the retrieval attempt : OK | ERROR
        TO IMPLEMENT in a child class
        """
        print "ItemInstaller::GetRawItem not implemented"
        raise

    def isAlreadyInstalled( self ):
        """
        Check if item is already installed
        Needs to be called after extractItem (destinationPath has to be determined first)
        ==> self.itemInfo [ "install_path" ] need to be set (in a subclass) before calling this method
        """
        result = False
        #if hasattr( self.itemInfo, "install_path" ) and os.path.exists( self.itemInfo [ "install_path" ] ):
        if os.path.exists( self.itemInfo [ "install_path" ] ):
            result = True
                
        return result

    def isInUse( self ):
        """
        Check if item is currently in use
        Needs to be called after extractItem (destinationPath has to be determined first)
        ==> installName need to be set (in a subclass) before calling this method
        """
        result = False
        return result

    
    def installItem( self, msgFunc=None,progressBar=None ):
        """
        Install item (download + extract + copy)
        Needs to be called after extractItem
        TO IMPLEMENT in a child class
        """
        print "ItemInstaller::installItem not implemented"
        raise


    def getItemInstallName( self ):
        """
        Return the real name (path) of the item (install name) not the name for description
        """
#        name = None
#        if hasattr( self.itemInfo, "name" ):
#            name = self.itemInfo[ "name" ]
        return self.itemInfo[ "name" ]

    def _getItemPaths( self ):
        """
        Returns the list of path of the current item (dir or file path)
        NOTE 1: A list is necessary in case of scrapers for instance
        NOTE 2: self.itemInfo [ "install_path" ] need to be set (in a subclass) before calling this method
        """
        
        #TODO: return path or name in both scenario
        
        paths = []
        #if hasattr( self.itemInfo, "install_path" ):
        # Directory case
        paths.append( self.itemInfo[ "install_path" ] )
        return paths

    def deleteInstalledItem( self ):
        """
        Delete an item already installed (file or directory)
        Return True if success, False otherwise
        NOTE: self.itemInfo [ "install_path" ] need to be set (in a subclass) before calling this method
        """
        result = None
        item_paths = self._getItemPaths ()

        if len( item_paths ) > None:
            for path in item_paths:
                result = self.fileMgr.deleteItem( path )
                if result == False:
                    print "deleteInstalledItem: Impossible to delete one of the element in the item: %s" %path
                    break
        else:
            result = False
            print "deleteInstalledItem: Item invalid - error"
        return result

    def renameInstalledItem( self, inputText ):
        """
        Rename an item already installed (file or directory)
        Return True if success, False otherwise
        NOTE: self.itemInfo [ "install_path" ] need to be set (in a subclass) before calling this method
        """
        
        #TODO; iuse same fomat between delete and rename: path or name
        
        
        result = None
        item_paths = self._getItemPaths ()
        print "renameInstalledItem"

        if len( item_paths ) > None:
            for path in item_paths:
                print u"Renaming %s by %s"%(path, path.replace( os.path.basename( path ), inputText))
                result = self.fileMgr.renameItem( None, path, path.replace( os.path.basename( path ), inputText) )
                if result == False:
                    print "renameInstalledItem: Impossible to rename one of the element in the item: %s" % path
                    break
        else:
            result = False
            print "renameInstalledItem: Item invalid - error"
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
            progressBar.update( percent, _( 176 ), self.itemInfo [ "temp_item_path" ] )
        if ( ( self.itemInfo [ "temp_item_path" ] != None ) and ( self.itemInfo [ "install_path" ] != None ) ):
            # Let's get the dir name in the archive
            print "ItemInstaller::installItem - Starting item copy"
            try:
                #if ( OK == bool( self.itemInfo [ "temp_item_path" ] ) ) and os.path.exists( self.itemInfo [ "temp_item_path" ] ):
                if os.path.exists( self.itemInfo [ "temp_item_path" ] ):
                    copy_dir( self.itemInfo [ "temp_item_path" ], self.itemInfo [ "install_path" ] )
                    OK = True
                else:
                    print "ItemInstaller::installItem - self.itemInfo [ 'temp_item_path' ] does not exist"
            except Exception, e:        
                print "ItemInstaller::installItem - Exception during copy of the directory %s" % self.itemInfo [ "temp_item_path" ]
                print_exc()
                process_error = True
            print "Install item completed"

        del extractor
        percent = 100
        if progressBar != None:
            progressBar.update( percent, _( 176 ), ( self.itemInfo [ "temp_item_path" ] ) )
        return OK

    def _prepareItem4xbox( self, item ):
        """
        Prepare an addon in order to be runnable on XBMC4XBOX
        (python script, icon renaming, folder renaming ...)
        """
        status = "OK"
        if TYPE_ADDON_MODULE != item[ "type" ]:
            print "Renaming addon elements"
            # Rename python script
            oldScriptPath = os.path.join( item[ "temp_item_path" ], item[ "library" ] )
            newScriptPath = os.path.join( item[ "temp_item_path" ], "default.py" )
            if ( oldScriptPath != newScriptPath and os.path.exists( oldScriptPath ) ):
                result = self.fileMgr.renameItem( None, oldScriptPath, newScriptPath )
                if result == False:
                    status = "ERROR"
                else:
                    item[ "library" ] = "default.py"
                
            # Rename logo
            oldLogoPath = os.path.join( item[ "temp_item_path" ], "icon.png" )
            newLogoPath = os.path.join( item[ "temp_item_path" ], "default.tbn" )
            if ( oldScriptPath != newScriptPath and os.path.exists( oldLogoPath ) ):
                result = self.fileMgr.renameItem( None, oldLogoPath, newLogoPath )
                if result == False:
                    status = "ERROR"
                    
            # Rename directory
            newItemPath = item[ "temp_item_path" ].replace(os.path.basename( item[ "temp_item_path" ] ) , item[ "name" ] )
            #print "itemPath: %s"%item[ "temp_item_path" ]    
            #print "newItemPath: %s"%newItemPath    
            try:
                if ( os.path.exists( item[ "temp_item_path" ] ) ):
                    result = self.fileMgr.renameItem( None, item[ "temp_item_path" ], newItemPath )
                    if result == False:
                            status = "ERROR"
            except Exception, e:
                status = "ERROR"
                print("Exception while renaming folder " + item[ "temp_item_path" ])
                print(str(e))
                print_exc()
    
        else:
            status = "UNCHANGED"
            
        if ( "OK" == status ):
            item [ "temp_item_path" ] = newItemPath 
        print item
        return status



    def setItemInfo( self ):
        """
        Get Type, name 
        """
        # id
        # name
        # type
        # version
        # author
        # disclaimer
        # summary
        # description
        # icon
        # fanart
        # changelog
        # library: path of python script
        # raw_item_sys_type: file | archive | dir
        # raw_item_path
        # install_path
        # temp_item_path
        # provides
        # required_lib
        
        itemExtractedPath = self.itemInfo [ "temp_item_path" ]
        
        status = 'OK'
        try:
            xmlInfofPath = os.path.join( itemExtractedPath, "addon.xml")
            if ( os.path.exists( xmlInfofPath ) ):
                xmlData = open( os.path.join( xmlInfofPath ), "r" )
                statusGetInfo = parseAddonXml( xmlData, self.itemInfo )
                xmlData.close()
                sleep(3)
                        
                if ( "OK" == statusGetInfo ):
                    typeInstallPath = get_install_path( self.itemInfo [ "type" ] )
                
                    status = self._prepareItem4xbox( self.itemInfo )
                    if ( "OK" == status ):
                        self.itemInfo [ "install_path" ] = os.path.join( typeInstallPath, self.itemInfo [ "name" ] )
                    else:
                        self.itemInfo [ "install_path" ] = os.path.join( typeInstallPath, os.path.basename( self.itemInfo [ "temp_item_path" ] ) )
                else:
                    print "Error parsing addon.xml"
                    status = 'ERROR'
            else:
                print "addon.xml not found"
                status = 'ERROR'
        except:
            print_exc()
            status = 'ERROR'

        print self.itemInfo
        print "setItemInfo - status: %s"%status
        return status



class ArchItemInstaller(ItemInstaller):
    """
    Installer from an archive
    """

    #def __init__( self , itemId, type, filesize ):
    #def __init__( self , name, type ):
    def __init__( self ):
        #ItemInstaller.__init__( self, itemId, type, filesize )
        ItemInstaller.__init__( self )
        self.itemInfo [ "install_path" ] = None

        #TODO: support progress bar display


    def extractItem( self, msgFunc=None,progressBar=None ):
        """
        Extract item in temp location
        Update:
        temp_item_path
        install_path
        name
        """
        #TODO: update a progress bar during extraction
        status  = "OK" # Status of download :[OK | ERROR | CANCELED]      
        percent = 33
        # Check if the archive exists
        print "extractItem"
        print self.itemInfo
        #if ( hasattr( self.itemInfo, "raw_item_path" ) \
        # and hasattr( self.itemInfo, "raw_item_sys_type" ) \
        # and os.path.exists( self.itemInfo[ "raw_item_path" ] ) \
        # and TYPE_SYSTEM_ARCHIVE == self.itemInfo[ "raw_item_sys_type" ] ):
        if ( os.path.exists( self.itemInfo[ "raw_item_path" ] ) and TYPE_SYSTEM_ARCHIVE == self.itemInfo[ "raw_item_sys_type" ] ):
            if progressBar != None:
                progressBar.update( percent, "Extraction:", ( self.itemInfo [ "name" ] ) )
                import extractor
                process_error = False
                # Extraction in cache directory (if OK copy later on to the correct location)
                file_path, OK = extractor.extract( self.itemInfo [ "raw_item_path" ], destination=self.CACHEDIR, report=True )

                if file_path == "":
                    installError = _( 139 ) % os.path.basename( self.itemInfo[ "raw_item_path" ] )
                    print "ArchItemInstaller - extractItem: Error during the extraction of %s - impossible to extract the name of the directory " % os.path.basename( self.itemInfo [ "raw_item_path" ] )
                    status = "ERROR"
                else:
                    # Extraction successful
                    self.itemInfo[ "temp_item_path" ] = file_path
                    
                    #TODO: check error case
                    if "ERROR" == self.setItemInfo():
                        print "extractItem - Impossible to retrieve data from addon.xml or transform the addon"
                        status = "ERROR"
                #TODO: add skin case (requirements need to be defined first)
                del extractor
                
            percent = 100
            if progressBar != None:
                progressBar.update( percent, _( 182 ), self.itemInfo [ "name" ] )
        else:
            print "extractItem - Archive does not exist - extraction impossible"
            status = "ERROR"
        return status

    
    def installItem( self, msgFunc=None,progressBar=None ):
        """
        Install item (download + extract + copy)
        Needs to be called after extractItem
        """
        print "installItem: Download and install case"
        percent = 0
        result  = "OK" # result after install :[ OK | ERROR | ALREADYINSTALLED |CANCELED]       
        
        
        print "installItem: Get Item"
        if ( self.status == "INIT" ) or ( self.status == "ERROR" ):
            #TODO: support message callback in addition of pb callback
            #statusDownload = self.GetRawItem( msgFunc=msgFunc, progressBar=progressBar )
            #statusDownload, self.itemInfo [ "raw_item_path" ] = self.GetRawItem( progressBar=progressBar )
            statusDownload = self.GetRawItem( progressBar=progressBar )
            print "installItem: statusDownload"
            print statusDownload
            print self.itemInfo [ "raw_item_path" ]
            print 
            if statusDownload in ["OK", "ERRORFILENAME"]:
                if self.extractItem( msgFunc=msgFunc, progressBar=progressBar ) == "OK":
                    if not self.isAlreadyInstalled():
                        if not self.isInUse():
                            print "installItem - Item is not yet installed - installing"
                            # TODO: in case of skin check skin is not the one currently used
                            if self.copyItem( msgFunc=msgFunc, progressBar=progressBar ) == False:
                                result = "ERROR"
                                self.status = "ERROR"
                                print "installItem - Error during copy"
                            else:
                                self.status = "INSTALL_DONE"
                        else:
                            print "installItem - Item is already currently used by XBMC - stopping install"
                            result = "ALREADYINUSE"
                            self.status = "EXTRACTED"
                    else:
                        print "installItem - Item is already installed - stopping install"
                        result = "ALREADYINSTALLED"
                        self.status = "EXTRACTED"
                else:
                    print "installItem - unknown error during extraction"
                    result = "ERROR"
                    self.status = "ERROR"
                    
#            elif statusDownload == "ERRORFILENAME":
#                pass
            elif statusDownload == "CANCELED":
                result      = "CANCELED"
                self.status = "CANCELED"
                print "installItem - Install cancelled by the user"
            else:
                result      = "ERROR"
                self.status = "ERROR"
                print "installItem - Error during download"
        elif self.status == "EXTRACTED":
            print "installItem - continue install"
            # TODO: in case of skin check skin is not the one currently used
            if self.copyItem( msgFunc=msgFunc, progressBar=progressBar ) == False:
                result      = "ERROR"
                self.status = "ERROR"
                print "installItem - Error during copy"
            else:
                self.status = "INSTALL_DONE"
            

        return result, self.itemInfo [ "install_path" ]



class DirItemInstaller(ItemInstaller):
    """
    Installer from a directory
    """

    #def __init__( self , itemId, type, filesize ):
    def __init__( self ):
        #ItemInstaller.__init__( self, itemId, type, filesize )
        #ItemInstaller.__init__( self, name, type )
        ItemInstaller.__init__( self )
        self.itemInfo [ "install_path" ] = None

        #TODO: support progress bar display
        #self.rawItemPath = None # Path of the archive to extract
        #self.destinationPath     = None # Path of the destination directory
        #self.downloadDirPath     = None # Path of the extracted item
        #self.status              = "INIT" # Status of install :[INIT | OK | ERROR | ALREADYINSTALLED |CANCELED]       


    def installItem( self, msgFunc=None,progressBar=None ):
        """
        Install item (download + extract + copy)
        Needs to be called after extractItem
        """
        print "installItem: Download and install case"
        percent = 0
        result  = "OK" # result after install :[ OK | ERROR | ALREADYINSTALLED |CANCELED]
        print "installItem: Download via itemInstaller"
        if ( self.status == "INIT" ) or ( self.status == "ERROR" ):
            #TODO: support message callback in addition of pb callback
            statusGetFile = self.GetRawItem( progressBar=progressBar )
            print "installItem: statusGetFile"
            print statusGetFile
            print self.itemInfo [ "raw_item_path" ]
            print 
            self.itemInfo [ "temp_item_path" ] = self.itemInfo [ "raw_item_path" ] #Since it is an directory those 2 path are identical
            if statusGetFile == "OK":
                if os.path.exists( self.itemInfo [ "temp_item_path" ] ):
                    # Download successful
                    if "ERROR" == self.setItemInfo():
                        print "installItem - Impossible to retrieve data from addon.xml or transform the addon"
                        status = "ERROR"
                    else:
                        if not self.isAlreadyInstalled():
                            if not self.isInUse():
                                print "installItem - Item is not yet installed - installing"
                                # TODO: in case of skin check skin is not the one currently used
                                if self.copyItem( msgFunc=msgFunc, progressBar=progressBar ) == False:
                                    result = "ERROR"
                                    print "installItem - Error during copy"
                                else:
                                    self.status = "INSTALL_DONE"
                            else:
                                print "installItem - Item is already currently used by XBMC - stopping install"
                                result = "ALREADYINUSE"
                                self.status = "EXTRACTED"
                        else:
                            print "installItem - Item is already installed - stopping install"
                            result = "ALREADYINSTALLED"
                            self.status = "DOWNLOADED"
            elif statusGetFile == "CANCELED":
                result      = "CANCELED"
                self.status = "CANCELED"
                print "installItem - Install cancelled by the user"
            else:
                result      = "ERROR"
                self.status = "ERROR"
                print "installItem - Error during download"
        elif self.status == "DOWNLOADED":
            print "installItem - continue install"
            # TODO: in case of skin check skin is not the one currently used
            if self.copyItem( msgFunc=msgFunc, progressBar=progressBar ) == False:
                result      = "ERROR"
                self.status = "ERROR"
                print "installItem - Error during copy"
            else:
                self.status = "INSTALL_DONE"
            

        return result, self.itemInfo [ "install_path" ]
             

