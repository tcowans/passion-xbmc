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
import urllib2

# Module logger
try:
    logger = sys.modules[ "__main__" ].logger
except:
    import script_log as logger

# Modules custom
from utilities import *
import CONF

class cancelRequest(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class ItemInstaller:
    """
    ABSTRACT
    """
    
    def __init__( self , itemId, type, installPath, filesize ):
        self.itemId          = itemId       # Id of the server item 
        self.type            = type         # Type of the item
        self.typeInstallPath = installPath  # Install Path for this type of item
        self.filesize        = filesize     # Size of the file to downlaod
        
        self.configManager = CONF.configCtrl()
        if not self.configManager.is_conf_valid: raise
        self.CACHEDIR = self.configManager.CACHEDIR
        
        
    def downloadItem( self ):
        pass

    def installItem( self ):
        pass

class HTTPInstaller(ItemInstaller):
    """
    Download an item on Passion XBMC http server and install it
    """

    def __init__( self , itemId, type, installPath, filesize ):
        ItemInstaller.__init__( self, itemId, type, installPath, filesize )
        
        #get base url for download
        self.baseurl = CONF.getBaseURLDownloadFile()
        
        #TODO: support progress bar display
        self.displayProgBar = True 
        self.downloadArchivePath = None # Path of the archive to extract
        self.destinationPath     = None # Path of the destination directory
        self.extractedDirPath    = None # Path of the extracted item

    def downloadItem( self, msgFunc=None,progressBar=None ):
        # Get ItemId
        cols = {}
        cols['$id_item'] = str(self.itemId)
        try:            
            print "downlaodItem - itemId" 
            print self.itemId
            
            # Get download link
                    
#            #get parent id of current parent
#            conn = sqlite.connect(self.db)
#            #Initialisation de la base de donnee
#            c = conn.cursor()
#            c.execute(self.nicequery('''SELECT filename, filesize,  
#                                     FROM Server_Items
#                                     WHERE id_file = $id_item''',cols))
#            filename, filesize = c.fetchone()[0]
            
            # Get real filename via the header
            fileURL  = self.baseurl + str(self.itemId)
            #fileName = self.getFileName( fileURL )
            
            print "fileURL = "
            print fileURL
            #print "fileName ="
            #print fileName
            
            # Get destination directory

            # Download file
            # pront download file to cache dir
            self.downloadArchivePath = self.downloadFile( fileURL, self.CACHEDIR, msgFunc=msgFunc, progressBar=progressBar )
        
        # Get temp path
        except Exception, e:
            print "Exception during downlaodItem"
            print e
            print sys.exc_info()
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )
        print self.downloadArchivePath
        return self.downloadArchivePath


    def extractItem( self ):
        """
        Extract item in temp location
        """
        #TODO: update a progress bar during extraction
        print "extractItem - path" 
        print self.downloadArchivePath
        if self.downloadArchivePath.endswith( 'zip' ) or self.downloadArchivePath.endswith( 'rar' ):
            import extractor
            process_error = False
            # on extrat tous dans le cache et si c'est OK on copy par la suite
            file_path, OK = extractor.extract( self.downloadArchivePath, report=True )
            print file_path
            print OK

            if self.type == "ScraperDir":
                # cas des Scrapers
                # ----------------
                #self.extracter.extract( archive, self.localdirList[ self.downloadTypeList.index( self.type ) ] )
                if ( OK == bool( file_path ) ) and os.path.exists( file_path ):
                    # Extraction sucessfull
                    self.destinationPath = self.typeInstallPath
                    self.extractedDirPath = file_path
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
                else:
                    # Extraction sucessfull
                    self.destinationPath = os.path.join( self.typeInstallPath, os.path.basename( file_path ) )
                    self.extractedDirPath = file_path
                    logger.LOG( logger.LOG_NOTICE, self.destinationPath )
            del extractor
            print self.type
            print self.destinationPath
            print self.extractedDirPath
        return self.type, self.destinationPath, self.extractedDirPath

    def isAlreadyInstalled( self ):
        """
        Check if extracted item is already installed
        Needs to be called after extractItem
        """
        if os.path.exists( self.destinationPath ):
            return True
        else:
            return False
    
    def installItem( self ):
        """
        Install item from extracted archive
        Needs to be called after extractItem
        """
        #TODO: update a progress bar during copy
        import extractor
        OK = False
        # get install path
        process_error = False
        print self.extractedDirPath
        print self.destinationPath
        
        if ( ( self.extractedDirPath != None ) and ( self.destinationPath != None ) ):
            print "Check type"
            print self.type
            if self.type == "ScraperDir":
                # cas des Scrapers
                # ----------------
                if os.path.exists( self.extractedDirPath ):
                    print "Starting scraper copy"
                    try:
                        extractor.copy_inside_dir( self.extractedDirPath, self.destinationPath )
                        OK = True
                    except:
                        process_error = True
                    print "Install Scraper completed"
                else:
                    print "self.extractedDirPath does not exist"
            else:
                # Cas des scripts et plugins
                # --------------------------
                # Recuperons le nom du repertorie a l'interieur de l'archive:
                dirName = ""
                if os.path.exists( self.extractedDirPath ):
                    print "Starting item copy"
                    try:
                        extractor.copy_dir( self.extractedDirPath, self.destinationPath )
                        OK = True
                    except:
                        process_error = True
                    print "Install item completed"
                else:
                    print "self.extractedDirPath does not exist"

        

        del extractor
        return OK




             
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
    
    def downloadFile(self, url, destinationDir,msgFunc=None,progressBar=None):
        """
        Download a file at a specific URL and send event to registerd UI if requested
        """
        print("downloadFile with url = " + url)
        print("downloadFile with destination directory = " + destinationDir)
        #print "msgFunc:"
        #print msgFunc
        #print "progressBar:"
        #print progressBar
        
        msgType    = ""
        msgTite    = ""
        msg1       = ""
        msg2       = ""
        msg3       = ""
        destination = None
        #destination = os.path.join( destinationDir, filename )
        noErrorOK  = True # When noErrorOK == True -> no error/Exception occured
               
        try:
            # -- Downloading
            print("downloadFile - Trying to retrieve the file")
            block_size          = 4096
            percent_downloaded  = 0
            num_blocks          = 0
            
            if self.displayProgBar == True:
                req = urllib2.Request(url)
                req.add_header('User-Agent','Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.3) Gecko/20070309 Firefox/2.0.0.3')
                connection  = urllib2.urlopen(req)           # Open connection
                headers     = connection.info()              # Get Headers
                file_size   = self.filesize 
                file_name   = headers['Content-Disposition'].split('"')[1]
                print "downloadFile - file size : %d Octet(s)"%file_size
                print "downloadFile - file name : %s "%file_name
                destination = os.path.join( destinationDir, file_name )
                file = open(destination,'w+b')        # Get ready for writing file
                # Ask for display of progress bar
                try:
                    if (progressBar != None):
                        progressBar.update(percent_downloaded)
                except Exception, e:        
                    print("downloadFile - Exception calling UI callback for download")
                    print(str(e))
                    print progressBar
                    
                ###########
                # Download
                ###########
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
                        print("downloadFile - Exception during reading of the remote file and writing it locally")
                        print(str(e))
                        print ("error during reading of the remote file and writing it locally: " + str(sys.exc_info()[0]))
                        traceback.print_exc()
                        noErrorOK  = False
                        # End of writing: Closing the connection and the file
                        connection.close()
                        file.close()
                        raise e
                    try:
                        # Compute percent of download in progress
                        New_percent_downloaded = min((num_blocks*block_size*100)/file_size, 100)
                        #print "downloadFile - Percent = %d"%New_percent_downloaded
                    except Exception, e:        
                        print("downloadFile - Exception computing percentage downloaded")
                        print(str(e))
                        noErrorOK  = False
                        # End of writing: Closing the connection and the file
                        connection.close()
                        file.close()
                        raise e
                    # We send an update only when percent number increases
                    if (New_percent_downloaded > percent_downloaded):
                        percent_downloaded = New_percent_downloaded
                        #print ("downloadFile - Downloaded %d %%"%percent_downloaded)
                        # Call UI callback in order to update download progress info
                        if (self.displayProgBar == True):
                            progressBar.update(percent_downloaded)

                    # Prepare message to the UI
                    msgType = "OK"
                    msgTite = "Nabbox Téléchargement"
                    msg1    = file_name
                    msg2    = "%d%% terminé. Le fichier disponible dans:"%(percent_downloaded)
                    msg3    = "%s"%destinationDir

                # Closing the file
                file.close()
                # End of writing: Closing the connection and the file
                connection.close()
#                else:
#                    print "downloadFile - *** using urlretrieve method ***"
#                    try:
#                        #urllib.urlretrieve(url,destination)
#                        urllib.urlretrieve(url,destination,lambda nb, bs, fs, url=url: self._pbhook(nb,bs,fs,url,progressBar))
#                    except cancelRequest:
#                    #except IOError, (errno, strerror):
#                        traceback.print_exc(file = sys.stdout)
#                        print "Downloaded STOPPED by the user"
#                    except Exception, e:
#                        traceback.print_exc(file = sys.stdout)
#                        print "=============================================="        
#                        print("downloadFile - Exception during urlretrieve")
#                        print(e)
#                        noErrorOK == False
#                        urllib.urlcleanup()
#                        raise e
#                    urllib.urlcleanup()
#                    # Prepare message to the UI
#                    msgType = "OK"
#                    msgTite = "Nabbox Téléchargement"
#                    msg1    = file_name
#                    msg2    = "Téléchargement terminé. Le fichier disponible dans:"
#                    msg3    = "%s"%destinationDir
#                    percent_downloaded = 0
        except Exception, e:
            print("Exception while source retrieving")
            print(str(e))
            print ("error while source retrieving: " + str(sys.exc_info()[0]))
            traceback.print_exc()
            print("downloadFile ENDED with ERROR")

            # Prepare message to the UI
            msgType = "Error"
            msgTite = "Nabbox Téléchargement - Erreur"
            msg1    = file_name
            msg2    = "%d%% Téléchargement terminé. Une erreur s'est produite durant le téléchargement du fichier"%(percent_downloaded)
            msg3    = "Erreur: %s"%e

            print("downloadFile ENDED")

                                
            # Close/Reset progress bar
            if (progressBar != None):
                progressBar.close()
            
            # Send the message to the UI
            try:
                if (msgFunc != None):
                    msgFunc(msgType, msgTite, msg1,msg2, msg3)
            except Exception, e:        
                print("downloadFile - Exception calling UI callback for message")
                print(str(e))
                print msgFunc
                
        return destination
        
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


