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
from utilities import *
import CONF
try:
    from ItemInstaller import ItemInstaller, cancelRequest
except:
    print sys.exc_info()
#import extractor

#FONCTION POUR RECUPERER LES LABELS DE LA LANGUE.
_ = sys.modules[ "__main__" ].__language__


class PassionHTTPInstaller(ItemInstaller):
    """
    Download an item on Passion XBMC http server and install it
    """

    def __init__( self , itemId, type, installPath, filesize, externalURL=None ):
        ItemInstaller.__init__( self, itemId, type, installPath, filesize )
        
        #get base url for download
        self.baseurl = CONF.getBaseURLDownloadFile()
        
        #TODO: support progress bar display
        self.displayProgBar      = True 
        self.downloadArchivePath = None # Path of the archive to extract
        self.destinationPath     = None # Path of the destination directory
        self.extractedDirPath    = None # Path of the extracted item
        self.externalURL         = externalURL # External URL for download (hosted on another server)
        self.status              = "INIT" # Status of install :[INIT | OK | ERROR | ALREADYINSTALLED |CANCELED]       

    def downloadItem( self, msgFunc=None,progressBar=None ):
        # Get ItemId
        cols = {}
        cols['$id_item'] = str(self.itemId)
        percent = 0
        totalpercent = 0
        if progressBar != None:
            progressBar.update( percent, _( 122 ) % ( self.baseurl + str(self.itemId) ), _( 123 ) % totalpercent )
        try:            
            logger.LOG( logger.LOG_DEBUG, "HTTPInstaller::downloadItem - itemId = %d"%self.itemId)
            
            # Get download link
                               
            fileURL  = self.baseurl + str(self.itemId)
            
            # Download file (to cache dir) and get destination directory
            #status, self.downloadArchivePath = self._downloadFile( fileURL, self.CACHEDIR, msgFunc=msgFunc, progressBar=progressBar )
            status, self.downloadArchivePath = self._downloadFile( fileURL, self.CACHEDIR, progressBar=progressBar )
        
        except Exception, e:
            #print "Exception during downlaodItem"
            #print e
            #print sys.exc_info()
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )
            self.downloadArchivePath = None
        if progressBar != None:
            progressBar.update( percent, _( 122 ) % ( self.baseurl + str(self.itemId) ), _( 134 ) )
        #return status, self.downloadArchivePath
        return status


    def extractItem( self, msgFunc=None,progressBar=None ):
        """
        Extract item in temp location
        """
        #TODO: update a progress bar during extraction
        print "extractItem - path" 
        print self.downloadArchivePath
        status     = "OK" # Status of download :[OK | ERROR | CANCELED]      
        percent = 33
        # Check if the archive exists
        if os.path.exists( self.downloadArchivePath ):
            if progressBar != None:
                progressBar.update( percent, "Extraction:", ( self.baseurl + str(self.itemId) ) )
            if self.downloadArchivePath.endswith( 'zip' ) or self.downloadArchivePath.endswith( 'rar' ):
                import extractor
                process_error = False
                # on extrait tous dans le cache et si c'est OK on copy par la suite
                file_path, OK = extractor.extract( self.downloadArchivePath, report=True )
                #print file_path
                #print OK
    
                if self.type == "ScraperDir":
                    # cas des Scrapers
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
                    # Recuperons le nom du repertorie a l'interieur de l'archive:
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
        Needs to be called after extractItem
        """
        if os.path.exists( self.destinationPath ):
            return True
        else:
            return False
    
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
            if self.type == "ScraperDir":
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
                dirName = ""
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



             
#    def getFileSize(self, source):
#        """
#        get the size of the file (in octets)
#        !!!ISSUE!!!: +1 on nb of download just calling this method
#        """
#        file_size = 0
#        try:
#            connection  = urllib2.urlopen(source)
#            headers     = connection.info()
#            file_size   = int(headers['Content-Length'])
#            connection.close()
#        except Exception, e:
#            print "Exception during getFileSize"
#            print e
#            print sys.exc_info()
#            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )
#        return file_size
#
#    def getFileName(self, source):
#        """
#        get the size of the file name
#        """
#        file_name = ""
#        try:
#            connection  = urllib2.urlopen(source)
#            headers     = connection.info()
#            file_name   = headers['Content-Disposition'].split('"')[1]
#            connection.close()
#        except Exception, e:
#            print "Exception during getFileName"
#            print e
#            print sys.exc_info()
#            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )
#        return file_name
    


#    def _downloadFile(self, url, destinationDir,msgFunc=None,progressBar=None):
    def _downloadFile(self, url, destinationDir, progressBar=None):
        """
        Download a file at a specific URL and send event to registerd UI if requested
        """
        print("_downloadFile with url = " + url)
        print("_downloadFile with destination directory = " + destinationDir)
        #print "msgFunc:"
        #print msgFunc
        #print "progressBar:"
        #print progressBar
        
#        msgType    = ""
#        msgTite    = ""
#        msg1       = ""
#        msg2       = ""
#        msg3       = ""
        destination = None
        #destination = os.path.join( destinationDir, filename )
        #noErrorOK  = True # When noErrorOK == True -> no error/Exception occured
        status     = "OK" # Status of download :[OK | ERROR | CANCELED]       
        
        try:
            # -- Downloading
            print("_downloadFile - Trying to retrieve the file")
            block_size          = 4096
            percent_downloaded  = 0
            num_blocks          = 0
            file_size           = None
            
            if self.displayProgBar == True:
                req = urllib2.Request(url)
                req.add_header('User-Agent','Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.3) Gecko/20070309 Firefox/2.0.0.3')
                connection  = urllib2.urlopen(req)           # Open connection
                file_size   = self.filesize 
                print "_downloadFile - file size : %d Octet(s)"%file_size
                print 'self.externalURL'
                print self.externalURL
                if self.externalURL != 'None':
                    #TODO: cover lengh max of file name (otherwise crash xbmc at writing)
                    file_name = os.path.basename( self.externalURL )
                    #file_name = "test.rar"
#                    connection.close()
#                    req = urllib2.Request(self.externalURL)
#                    req.add_header('User-Agent','Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.3) Gecko/20070309 Firefox/2.0.0.3')
#                    connection  = urllib2.urlopen(req)           # Open connection
                else:
                    headers     = connection.info()              # Get Headers
                    print "headers:"
                    print headers
                    file_name   = headers['Content-Disposition'].split('"')[1]
                print "_downloadFile - file name : %s "%file_name
                destination = os.path.join( destinationDir, file_name )
                print 'destination'
                print destination
                file = open(destination,'w+b')        # Get ready for writing file
                print "File opened"
                # Ask for display of progress bar
                try:
                    if (progressBar != None):
                        progressBar.update(percent_downloaded)
                except Exception, e:        
                    print("_downloadFile - Exception calling UI callback for download")
                    print(str(e))
                    print progressBar
                    
                ###########
                # Download
                ###########
                print "Starting download"
                while 1:
                    if (progressBar != None):
                        if progressBar.iscanceled():
                            print "Downloaded STOPPED by the user"
                            break
                    try:
                        cur_block  = connection.read(block_size)
                        if not cur_block:
                            break
                        file.write(cur_block)
                        # Increment for next block
                        num_blocks = num_blocks + 1
                    except Exception, e:        
                        print("_downloadFile - Exception during reading of the remote file and writing it locally")
                        print(str(e))
                        print ("error during reading of the remote file and writing it locally: " + str(sys.exc_info()[0]))
                        traceback.print_exc()
                        #noErrorOK  = False
                        status = "ERROR"
                        # End of writing: Closing the connection and the file
                        #connection.close()
                        #file.close()
                        #raise e
                    try:
                        # Compute percent of download in progress
                        New_percent_downloaded = min((num_blocks*block_size*100)/file_size, 100)
                        #print "_downloadFile - Percent = %d"%New_percent_downloaded
                    except Exception, e:        
                        print("_downloadFile - Exception computing percentage downloaded")
                        print(str(e))
                        #noErrorOK  = False
                        status = "ERROR"
                        # End of writing: Closing the connection and the file
                        #connection.close()
                        #file.close()
                        #raise e
                    # We send an update only when percent number increases
                    if (New_percent_downloaded > percent_downloaded):
                        percent_downloaded = New_percent_downloaded
                        #print ("_downloadFile - Downloaded %d %%"%percent_downloaded)
                        # Call UI callback in order to update download progress info
                        if (self.displayProgBar == True):
                            progressBar.update(percent_downloaded)

    
                # Closing the file
                file.close()
                # End of writing: Closing the connection and the file
                connection.close()
        except Exception, e:
            status = "ERROR"
            print("Exception while source retrieving")
            print(str(e))
            print ("error while source retrieving: " + str(sys.exc_info()[0]))
            traceback.print_exc()
            print("_downloadFile ENDED with ERROR")

#            # Prepare message to the UI
#            msgType = "Error"
#            msgTite = _ ( 144 )
#            msg1    = file_name
#            msg2    = ""
#            msg3    = ""

        print("_downloadFile ENDED")

#        if status == "OK":
#            # Prepare message to the UI
#            msgType = "OK"
#            msgTite = _( 137 )
#            msg1    = file_name
#            msg2    = _( 134 )
#            msg3    = ""
#        elif status == "CANCELED":
#            # Prepare message to the UI
#            msgType = "OK"
#            msgTite = _ ( 124 )
#            msg1    = file_name
#            msg2    = _ ( 125 )
#            msg3    = ""
#        else:
#            print "_downloadFile - An error has occured"
#            destination = None
#
#            # Prepare message to the UI
#            msgType = "Error"
#            msgTite = _ ( 144 )
#            msg1    = file_name
#            msg2    = ""
#            msg3    = ""
                            
#        # Close/Reset progress bar
#        if (progressBar != None):
#            progressBar.close()
        
#        # Send the message to the UI
#        try:
#            if (msgFunc != None):
#                msgFunc(msgType, msgTite, msg1,msg2, msg3)
#        except Exception, e:        
#            print("_downloadFile - Exception calling UI callback for message")
#            print(str(e))
#            print msgFunc
                
        return status, destination
        
    def _pbhook(self,numblocks, blocksize, filesize, url=None,dp=None):
        """
        Hook function for progress bar
        Inspired from the example on xbmc.org wiki
        """
#        try:
#            percent = min((numblocks*blocksize*100)/filesize, 100)
#            print "_pbhook - percent = %s%%"%percent
#            dp.update(percent)
#        except Exception, e:        
#            print("_pbhook - Exception during percent computing AND update")
#            print(e)
#            percent = 100
#            dp.update(percent)
        if ( ( dp != None ) and ( dp.iscanceled() ) ): 
            print "_pbhook: DOWNLOAD CANCELLED" # need to get this part working
            #dp.close() #-> will be calose in calling function
            #raise IOError
            raise cancelRequest,"User pressed CANCEL button"


