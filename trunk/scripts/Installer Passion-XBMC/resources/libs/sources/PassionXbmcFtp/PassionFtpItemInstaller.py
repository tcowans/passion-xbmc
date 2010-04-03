"""
ItemInstaller: this module allows download and install an item
"""

# Modules general
import os
import sys
from traceback import print_exc


# Modules XBMC
import xbmc

# Modules custom
#import extractor
from utilities import *
try:
    from ItemInstaller import ArchItemInstaller, DirItemInstaller, cancelRequest
except:
    print_exc()

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
        self.ftpCtrl     = ftpCtrl # FtpDownloadCtrl instance
#        self.filesize = filesize     # Size of the file to download

    def downloadItem( self, msgFunc=None,progressBar=None ):
        """
        Download an item form the server
        Returns - the status of the download attempt : OK | ERROR 
                - the path of the archive downloaded
        """
        percent      = 0
        totalpercent = 0
        destination  = None
        status       = "OK" # Status of download :[OK | ERROR | CANCELED]
        if progressBar != None:
            progressBar.update( percent, _( 122 ) % ( self.downloadurl ), _( 123 ) % totalpercent )
        try:            
            print "PassionFTPInstaller::downloadItem - name = %s" % self.name
            
            status = self.ftpCtrl.download( self.downloadurl, self.type, progressbar_cb=self._pbhook, dialogProgressWin = progressBar )
            
            #TODO: this is a temp solution,downloadArchivePath should be returned by PassionFtpManager
            downloadArchivePath = xbmc.translatePath( os.path.join( self.CACHEDIR, os.path.basename(self.downloadurl) ) )
        except Exception, e:
            print "Exception during downlaodItem"
            print_exc()
            downloadArchivePath = None
            status = "ERROR"
        if progressBar != None:
            progressBar.update( percent, _( 122 ) % ( self.downloadurl ), _( 134 ) )
        return status, downloadArchivePath
        #return status



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
#            print_exc()
        return file_size
        
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



class PassionSkinFTPInstaller(DirItemInstaller):
    """
    Download a skin item on Passion XBMC FTP server and install it
    """

    def __init__( self , name, type, downloadurl, ftpCtrl ):
        DirItemInstaller.__init__( self, name, type )
        self.downloadurl = downloadurl
        self.ftpCtrl     = ftpCtrl # FtpDownloadCtrl instance

    def downloadItem( self, msgFunc=None,progressBar=None ):
        """
        Download an item form the server
        Returns the status of the download attemos : OK | ERROR
        """
        percent      = 0
        totalpercent = 0
        destination  = None
        status       = "OK" # Status of download :[OK | ERROR | CANCELED]
        if progressBar != None:
            progressBar.update( percent, _( 122 ) % ( self.name ), _( 123 ) % totalpercent )
        try:            
            print "PassionFTPInstaller::downloadItem - name = %s" % self.name
            
            status = self.ftpCtrl.download( self.downloadurl, self.type, progressbar_cb=self._pbhook, dialogProgressWin = progressBar )
            
            #TODO: this is a temp solution,downloadDirPath should be returned by PassionFtpManager
            downloadDirPath = xbmc.translatePath( os.path.join( self.CACHEDIR, os.path.basename(self.downloadurl) ) )
        except Exception, e:
            print "Exception during downlaodItem"
            print_exc()
            downloadDirPath = None
            status = "ERROR"
        if progressBar != None:
            progressBar.update( percent, _( 122 ) % ( self.name ), _( 134 ) )
        return status, downloadDirPath

    def _pbhook(self,numblocks, blocksize, filesize, url=None,dp=None):
        """
        Hook function for progress bar
        Inspired from the example on xbmc.org wiki
        """
        if ( ( dp != None ) and ( dp.iscanceled() ) ): 
            print "_pbhook: DOWNLOAD CANCELLED" # need to get this part working
            #dp.close() #-> will be calose in calling function
            #raise IOError
            raise cancelRequest,"User pressed CANCEL button"
