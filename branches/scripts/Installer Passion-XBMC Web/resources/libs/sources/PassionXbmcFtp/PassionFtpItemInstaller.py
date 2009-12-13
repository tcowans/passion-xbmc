"""
ItemInstaller: this module allows download and install an item
"""
import os
import sys
import traceback

# SQLite
from pysqlite2 import dbapi2 as sqlite

#Other module

# Module logger
try:
    logger = sys.modules[ "__main__" ].logger
except:
    import script_log as logger

# Modules custom
from utilities import *
import CONF
import Item
try:
    from ItemInstaller import ArchItemInstaller, cancelRequest
except:
    print sys.exc_info()
    traceback.print_exc()
#import extractor

#FONCTION POUR RECUPERER LES LABELS DE LA LANGUE.
_ = sys.modules[ "__main__" ].__language__


class PassionFTPInstaller(ArchItemInstaller):
    """
    Download an item on Passion XBMC FTP server and install it
    """

    #def __init__( self , itemId, type, installPath, filesize, externalURL=None ):
    def __init__( self , name, type, downloadurl, ftpCtrl ):
        ArchItemInstaller.__init__( self, name, type )
        self.downloadurl = downloadurl
        self.ftpCtrl     = ftpCtrl
#        self.filesize = filesize     # Size of the file to download

    def downloadItem( self, msgFunc=None,progressBar=None ):
        """
        Download an item form the server
        Returns the status of the download attemos : OK | ERROR
        """
        percent = 0
        totalpercent = 0
        if progressBar != None:
            progressBar.update( percent, _( 122 ) % ( self.downloadurl ), _( 123 ) % totalpercent )
        try:            
            logger.LOG( logger.LOG_DEBUG, "PassionFTPInstaller::downloadItem - itemId = %d"%self.itemId)
            
#            # Get download link
#                               
#            fileURL  = self.baseurl + str(self.itemId)
#            
#            # Download file (to cache dir) and get destination directory
#            status, self.downloadArchivePath = self._downloadFile( fileURL, self.CACHEDIR, progressBar=progressBar )





            lenbasepath = len( self.remotedirList[ self.downloadTypeList.index( self.type ) ] )
            downloadItem = source[ lenbasepath: ]
            downloadStatus = self.ftpCtrl.download( source, self.type, progressbar_cb=_pbhook, dialogProgressWin = progressBar )
        
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



    def getFileSize(self, sourceurl):
        """
        get the size of the file (in octets)
        !!!ISSUE!!!: +1 on nb of download just calling this method with Passion-XBMC URL
        """
        file_size = 0
#        try:
#            connection  = urllib2.urlopen(sourceurl)
#            headers     = connection.info()
#            file_size   = int( headers['Content-Length'] )
#            connection.close()
#        except Exception, e:
#            print "Exception during getFileSize"
#            print e
#            print sys.exc_info()
#            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )
        return file_size
#
#    def getFileName(self, sourceurl):
#        """
#        get the size of the file name
#        """
#        file_name = ""
#        try:
#            connection  = urllib2.urlopen(sourceurl)
#            headers     = connection.info()
#            file_name   = headers['Content-Disposition'].split('"')[1]
#            connection.close()
#        except Exception, e:
#            print "Exception during getFileName"
#            print e
#            print sys.exc_info()
#            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )
#        return file_name
    


##    def _downloadFile(self, url, destinationDir,msgFunc=None,progressBar=None):
#    def _downloadFile(self, url, destinationDir, progressBar=None):
#        """
#        Download a file at a specific URL and send event to registerd UI if requested
#        Returns the status of the download attemos : OK | ERROR
#        """
#        print("_downloadFile with url = " + url)
#        print("_downloadFile with destination directory = " + destinationDir)
#        destination = None
#        #destination = os.path.join( destinationDir, filename )
#        #noErrorOK  = True # When noErrorOK == True -> no error/Exception occured
#        status     = "OK" # Status of download :[OK | ERROR | CANCELED]
#        
#        try:
#            # -- Downloading
#            print("_downloadFile - Trying to retrieve the file")
#            block_size          = 4096
#            percent_downloaded  = 0
#            num_blocks          = 0
#            file_size           = None
#            
#            if self.displayProgBar == True:
#                req = urllib2.Request(url) # Note: downloading item with passion XBMC URL (for download count) even when there is an external URL
#                req.add_header('User-Agent','Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.3) Gecko/20070309 Firefox/2.0.0.3')
#                connection  = urllib2.urlopen(req)           # Open connection
#                print 'self.externalURL'
#                print self.externalURL
#                if self.externalURL != 'None':
#                    #TODO: cover length max of file name (otherwise crash xbmc at writing)
#                    file_name = os.path.basename( self.externalURL ).replace(";","").replace("?","")
#                else:
#                    try:
#                        headers = connection.info()# Get Headers
#                        print "headers:"
#                        print headers
#                        file_name   = headers['Content-Disposition'].split('"')[1]
#                    except Exception, e:
#                        file_name = "unknownfilename.rar"
#                        print("_downloadFile - Exception retrieving header")
#                        print(str(e))
#
#                
#                print "_downloadFile - file name : %s "%file_name
#                destination = os.path.join( destinationDir, file_name )
#                print 'destination'
#                print destination
#                
#                # Check File Size
#                if self.filesize > 0:
#                    file_size = file_size = self.filesize
#                elif self.externalURL != 'None':
#                    # Try to get file size from the external URL header
#                    file_size = self.getFileSize(self.externalURL)
#                else:
#                    file_size = 0
#
#                print "_downloadFile - file size : %d Octet(s)"%file_size
#
#                file = open(destination,'w+b')        # Get ready for writing file
#                print "File opened"
#                # Ask for display of progress bar
#                try:
#                    if (progressBar != None):
#                        progressBar.update(percent_downloaded)
#                except Exception, e:        
#                    print("_downloadFile - Exception calling UI callback for download")
#                    print(str(e))
#                    print progressBar
#                    
#                ###########
#                # Download
#                ###########
#                print "Starting download"
#                while 1:
#                    if (progressBar != None):
#                        if progressBar.iscanceled():
#                            print "Downloaded STOPPED by the user"
#                            break
#                    try:
#                        cur_block  = connection.read(block_size)
#                        if not cur_block:
#                            break
#                        file.write(cur_block)
#                        # Increment for next block
#                        num_blocks = num_blocks + 1
#                    except Exception, e:        
#                        print("_downloadFile - Exception during reading of the remote file and writing it locally")
#                        print(str(e))
#                        print ("error during reading of the remote file and writing it locally: " + str(sys.exc_info()[0]))
#                        traceback.print_exc()
#                        #noErrorOK  = False
#                        status = "ERROR"
#                        # End of writing: Closing the connection and the file
#                        #connection.close()
#                        #file.close()
#                        #raise e
#                    try:
#                        # Compute percent of download in progress
#                        New_percent_downloaded = min((num_blocks*block_size*100)/file_size, 100)
#                        #print "_downloadFile - Percent = %d"%New_percent_downloaded
#                    except Exception, e:        
#                        print("_downloadFile - Exception computing percentage downloaded")
#                        print(str(e))
#                        #noErrorOK  = False
#                        New_percent_downloaded = 0
#                        status = "ERROR"
#                        # End of writing: Closing the connection and the file
#                        #connection.close()
#                        #file.close()
#                        #raise e
#                    # We send an update only when percent number increases
#                    if (New_percent_downloaded > percent_downloaded):
#                        percent_downloaded = New_percent_downloaded
#                        #print ("_downloadFile - Downloaded %d %%"%percent_downloaded)
#                        # Call UI callback in order to update download progress info
#                        if (self.displayProgBar == True):
#                            progressBar.update(percent_downloaded)
#
#    
#                # Closing the file
#                file.close()
#                # End of writing: Closing the connection and the file
#                connection.close()
#        except Exception, e:
#            status = "ERROR"
#            print("Exception while source retrieving")
#            print(str(e))
#            print ("error while source retrieving: " + str(sys.exc_info()[0]))
#            traceback.print_exc()
#            print("_downloadFile ENDED with ERROR")

#            # Prepare message to the UI
#            msgType = "Error"
#            msgTite = _ ( 144 )
#            msg1    = file_name
#            msg2    = ""
#            msg3    = ""

#        print("_downloadFile ENDED")

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
                
#        return status, destination
        
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

#    def install_add_ons( self ):
#        """
#        installation de l'item selectionner
#        """
#        try:
#            downloadOK = True
#            correctionPM3bidon = False
#            self.index = self.getCurrentListPosition()
#
#            source = self.curDirList[ self.index ]
#
#            if not xbmcgui.Dialog().yesno( _( 180 ), _( 181 ), source ): return
#
#            if self.type == self.downloadTypeList[ 0 ]:   #Themes
#                # Verifions le themes en cours d'utilisation
#                mySkinInUse = xbmc.getSkinDir()
#                if mySkinInUse in source:
#                    # Impossible de telecharger une skin en cours d'utlisation
#                    dialog = xbmcgui.Dialog()
#                    dialog.ok( _( 117 ), _( 118 ), _( 119 ) )
#                    downloadOK = False
#                if 'Project Mayhem III' in source and self.USRPath == True:
#                    self.linux_chmod( self.PMIIIDir )
#                    if self.rightstest == True:
#                        self.localdirList[ 0 ]= self.PMIIIDir
#                        downloadOK = True
#                        correctionPM3bidon = True
#                    else:
#                        dialog = xbmcgui.Dialog()
#                        dialog.ok( _( 117 ), _( 120 ) )
#                        downloadOK = False
#            elif self.type == self.downloadTypeList[ 1 ] and self.USRPath == True:   #Linux Scrapers
#                self.linux_chmod( self.scraperDir )
#                if self.rightstest == True :
#                    downloadOK = True
#                else:
#                    dialog = xbmcgui.Dialog()
#                    dialog.ok( _( 117 ), _( 121 ) )
#                    downloadOK = False
#
#            if source.endswith( 'zip' ) or source.endswith( 'rar' ):
#                self.targetDir = self.localdirList[ self.downloadTypeList.index( self.type ) ]
#                self.localdirList[ self.downloadTypeList.index( self.type ) ]= self.CacheDir
#
#            if downloadOK == True:
#                continueDownload = True
#
#                # on verifie le si on a deja telecharge cet element ( ou une de ses version anterieures )
#                isDownloaded, localDirPath = self.passionFTPCtrl.isAlreadyDownloaded( source, self.remotedirList[ self.downloadTypeList.index( self.type ) ], self.downloadTypeList.index( self.type ) )
#
#                if ( isDownloaded ) and ( localDirPath != None ):
#                    logger.LOG( logger.LOG_NOTICE, "Repertoire deja present localement" )
#                    # On traite le repertorie deja present en demandant a l'utilisateur de choisir
#                    continueDownload = self.processOldDownload( localDirPath )
#                else:
#                    logger.LOG( logger.LOG_DEBUG, "localDirPath: %s", repr( localDirPath ) )
#                    logger.LOG( logger.LOG_DEBUG, "isDownloaded: %s", repr( isDownloaded ) )
#
#                if continueDownload == True:
#                    # Fenetre de telechargement
#
#                    dp = xbmcgui.DialogProgress()
#                    lenbasepath = len( self.remotedirList[ self.downloadTypeList.index( self.type ) ] )
#                    downloadItem = source[ lenbasepath: ]
#                    percent = 0
#                    dp.create( _( 122 ) % downloadItem, _( 123 ) % percent )
#
#                    # Type est desormais reellement le type de download, on utlise alors les liste pour recuperer le chemin que l'on doit toujours passer
#                    # on appel la classe passionFTPCtrl avec la source a telecharger
#                    downloadStatus = self.passionFTPCtrl.download( source, self.remotedirList[ self.downloadTypeList.index( self.type ) ], self.downloadTypeList.index( self.type ), progressbar_cb=self.updateProgress_cb, dialogProgressWin = dp )
#                    #dp.close()
#
#                    if downloadStatus == -1:
#                        # Telechargment annule par l'utilisateur
#                        title = _( 124 )
#                        message1 = "%s: %s" % ( self.type, downloadItem )
#                        message2 = _( 125 )
#                        message3 = _( 126 )
#                        if xbmcgui.Dialog().yesno( title, message1, message2, message3 ):
#                            logger.LOG( logger.LOG_WARNING, "Suppression du repertoire %s", localDirPath )
#                            if os.path.isdir( localDirPath ):
#                                if self.deleteDir( localDirPath ):
#                                    xbmcgui.Dialog().ok( _( 127 ), _( 128 ), localDirPath, _( 129 ) )
#                                else:
#                                    xbmcgui.Dialog().ok( _( 111 ), _( 130 ), localDirPath )
#                            else:
#                                try:
#                                    os.remove( localDirPath )
#                                    xbmcgui.Dialog().ok( _( 131 ), _( 132 ), localDirPath, _( 129 ) )
#                                except Exception, e:
#                                    xbmcgui.Dialog().ok( _( 111 ), _( 133 ), localDirPath )
#                    else:
#                        title = _( 134 )
#                        message1 = "%s: %s" % ( self.type, downloadItem )
#                        message2 = _( 135 )
#                        message3 = self.localdirList[ self.downloadTypeList.index( self.type ) ]
#
#                        self._save_downloaded_property()
#                        xbmcgui.Dialog().ok( title, message1, message2, message3 )
#
#                    #TODO: Attention correctionPM3bidon n'est pa defini dans le cas d'un scraper ou script
#                    #      Je l'ai donc defini a False au debut
#                    # On remet a la bonne valeur initiale self.localdirList[ 0 ]
#                    if correctionPM3bidon == True:
#                        self.localdirList[ 0 ] = themesDir
#                        correctionPM3bidon = False
#                    # On se base sur l'extension pour determiner si on doit telecharger dans le cache.
#                    # Un tour de passe passe est fait plus haut pour echanger les chemins de destination avec le cache, le chemin de destination
#                    # est retabli ici 'il s'agit de targetDir'
#                    if downloadItem.endswith( 'zip' ) or downloadItem.endswith( 'rar' ):
#                        if downloadStatus != -1:
#                            installCancelled = False
#                            installError = None
#                            #dp = xbmcgui.DialogProgress()
#                            #dp.create( _( 136 ) % downloadItem, _( 123 ) % percent )
#                            #dialogUI = xbmcgui.DialogProgress()
#                            dp.create( _( 137 ), _( 138 ) % downloadItem, _( 110 ) )
#
#                            #Appel de la classe d'extraction des archives
#                            remoteDirPath = self.remotedirList[ self.downloadTypeList.index( self.type ) ]#chemin ou a ete telecharge le script
#                            localDirPath = self.localdirList[ self.downloadTypeList.index( self.type ) ]
#                            archive = source.replace( remoteDirPath, localDirPath + os.sep )#remplacement du chemin de l'archive distante par le chemin local temporaire
#                            self.localdirList[ self.downloadTypeList.index( self.type ) ] = self.targetDir
#                            #fichierfinal0 = archive.replace( localDirPath, self.localdirList[ self.downloadTypeList.index( self.type ) ] )
#                            #if fichierfinal0.endswith( '.zip' ):
#                            #    fichierfinal = fichierfinal0.replace( '.zip', '' )
#                            #elif fichierfinal0.endswith( '.rar' ):
#                            #    fichierfinal = fichierfinal0.replace( '.rar', '' )
#
#                            import extractor
#                            process_error = False
#                            # on extrat tous dans le cache et si c'est OK on copy par la suite
#                            file_path, OK = extractor.extract( archive, report=True )
#                            #print OK, file_path
#                            if self.type == "Scrapers":
#                                # cas des Scrapers
#                                # ----------------
#                                #self.extracter.extract( archive, self.localdirList[ self.downloadTypeList.index( self.type ) ] )
#                                destination = self.localdirList[ self.downloadTypeList.index( self.type ) ]
#                                if ( OK == bool( file_path ) ) and os.path.exists( file_path ):
#                                    extractor.copy_inside_dir( file_path, destination )
#                            else:
#                                # Cas des scripts et plugins
#                                # --------------------------
#                                # Recuperons le nom du repertorie a l'interieur de l'archive:
#                                dirName = ""
#                                if ( OK == bool( file_path ) ) and os.path.exists( file_path ):
#                                    dirName = os.path.basename( file_path )#self.extracter.getDirName( archive )
#                                    destination = os.path.join( self.localdirList[ self.downloadTypeList.index( self.type ) ], os.path.basename( file_path ) )
#
#                                if dirName == "":
#                                    installError = _( 139 ) % archive
#                                    logger.LOG( logger.LOG_ERROR, "Erreur durant l'extraction de %s - impossible d'extraire le nom du repertoire", archive )
#                                else:
#                                    #destination = os.path.join( self.localdirList[ self.downloadTypeList.index( self.type ) ], dirName )
#                                    logger.LOG( logger.LOG_NOTICE, destination )
#                                    if os.path.exists( destination ):
#                                        # Repertoire deja present
#                                        # On demande a l'utilisateur ce qu'il veut faire
#                                        if self.processOldDownload( destination ):
#                                            try:
#                                                #logger.LOG( logger.LOG_NOTICE, "Extraction de %s vers %s", archive, self.localdirList[ self.downloadTypeList.index( self.type ) ] )
#                                                #self.extracter.extract( archive, self.localdirList[ self.downloadTypeList.index( self.type ) ] )
#                                                if ( OK == bool( file_path ) ) and os.path.exists( file_path ):
#                                                    extractor.copy_dir( file_path, destination )
#                                            except:
#                                                process_error = True
#                                        else:
#                                            installCancelled = True
#                                            logger.LOG( logger.LOG_WARNING, "L'installation de %s a ete annulee par l'utilisateur", downloadItem  )
#                                    else:
#                                        # Le Repertoire n'est pas present localement -> on peut deplacer le repertoire depuis cache
#                                        try:
#                                            #logger.LOG( logger.LOG_NOTICE, "Extraction de %s vers %s", archive, self.localdirList[ self.downloadTypeList.index( self.type ) ] )
#                                            #self.extracter.extract( archive, self.localdirList[ self.downloadTypeList.index( self.type ) ] )
#                                            if ( OK == bool( file_path ) ) and os.path.exists( file_path ):
#                                                extractor.copy_dir( file_path, destination )
#                                        except:
#                                            process_error = True
#
#                            del extractor
#                            # Close the Loading Window
#                            #dialogUI.close()
#
#                            if process_error:
#                                installError = _( 140 ) % archive
#                                logger.LOG( logger.LOG_ERROR, "Exception durant l'extraction de %s", archive )
#                                logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )
#
#                            if installCancelled == False and installError == None:
#                                self._save_downloaded_property()
#                                xbmcgui.Dialog().ok( _( 141 ), _( 142 ) % downloadItem, _( 143 ) )
#                            else:
#                                if installError != None:
#                                    # Erreur durant l'install ( meme si on a annule )
#                                    xbmcgui.Dialog().ok( _( 144 ), installError, _( 145 ) )
#                                elif installCancelled == True:
#                                    # Install annulee
#                                    xbmcgui.Dialog().ok( _( 146 ), _( 147 ) % downloadItem )
#                                else:
#                                    # Install annulee
#                                    xbmcgui.Dialog().ok( _( 144 ), _( 148 ), _( 145 ) )
#                        else:
#                            # On remet a la bonne valeur initiale self.localdirList
#                            self.localdirList[ self.downloadTypeList.index( self.type ) ] = self.targetDir
#
#                    # Close the Loading Window
#                    dp.close()
#        except:
#            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )

