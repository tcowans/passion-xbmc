"""
ItemInstaller: this module allows download and install an item from Passion XBMC download center
"""

# Modules general
import os
import sys
import httplib
import urllib2
from traceback import print_exc

# Modules XBMC
import xbmc

# Modules custom
from utilities import *
try:
    from ItemInstaller import ArchItemInstaller, cancelRequest
    from Item import *
except:
    print_exc()

httplib.HTTPConnection.debuglevel = 1

#FONCTION POUR RECUPERER LES LABELS DE LA LANGUE.
_ = sys.modules[ "__main__" ].__language__


class RemoteArchiveInstaller(ArchItemInstaller):
    """
    Download an item on Passion XBMC http server and install it
    """

    def __init__( self , name, url ):
        ArchItemInstaller.__init__( self )

        self.itemInfo [ "name" ] = name
        #self.itemInfo [ "name" ] = unicode( name, 'ISO 8859-1', errors='ignore')
        
        self.itemInfo [ "url" ] = url
        self.itemInfo [ "filename" ] = os.path.basename(url)
        self.itemInfo [ "filesize" ] = 0
        self.itemInfo [ "raw_item_sys_type" ] = TYPE_SYSTEM_ARCHIVE
        print self.itemInfo
        #TODO: support progress bar display

    def GetRawItem( self, msgFunc=None,progressBar=None ):
        """
        Download an item form the server
        Returns the status of the download attempts : OK | ERROR
        """
        # Get ItemId
        percent = 0
        
        if progressBar != None:
            #progressBar.update( percent, unicode(_( 122 )) % ( self.itemInfo [ "name" ] ), unicode(_( 123 )) % percent )
            progressBar.update( percent, ( self.itemInfo [ "name" ] ), _( 123 ) % percent )
            #print _( 122 )
            #print self.itemInfo[ "name" ]
            #from types import *
            #print type(self.itemInfo[ "name" ])
            #print unicode(self.itemInfo[ "name" ], errors='ignore')
            #print _( 122 )%ustr
        try:            
            print "HTTPInstaller::GetRawItem "
            # Download file (to cache dir) and get destination directory
            status, self.itemInfo [ "raw_item_path" ] = self._downloadFile( progressBar=progressBar )
        
        except Exception, e:
            print "Exception during downlaodItem"
            print e
            print_exc()
            self.itemInfo [ "raw_item_path" ] = None
        if progressBar != None:
            progressBar.update( percent, ( self.itemInfo [ "name" ] ), _( 134 ) )
        #return status, self.itemInfo [ "raw_item_path" ]
        return status



    def getFileSize(self, sourceurl):
        """
        get the size of the file (in octets)
        !!!ISSUE!!!: +1 on nb of download just calling this method with Passion-XBMC URL
        """
        file_size = 0
        try:
            connection  = urllib2.urlopen(sourceurl)
            headers     = connection.info()
            file_size   = int( headers['Content-Length'] )
            connection.close()
        except Exception, e:
            print "Exception during getFileSize"
            print e
            print sys.exc_info()
            print_exc()
        return file_size

    def _downloadFile(self, progressBar=None):
        """
        Download a file at a specific URL and send event to registerd UI if requested
        Returns the status of the download attempt : OK | ERROR
        """
        destinationDir = self.CACHEDIR
        print("_downloadFile with url = " + self.itemInfo [ "url" ])
        print("_downloadFile with destination directory = " + destinationDir)
        destination = None
        status     = "OK" # Status of download :[OK | ERROR | CANCELED | ERRORFILENAME]
        
        try:
            # -- Downloading
            print("_downloadFile - Trying to retrieve the file")
            block_size          = 8192
            percent_downloaded  = 0
            num_blocks          = 0
            
            req = urllib2.Request(self.itemInfo [ "url" ]) # Note: downloading item with passion XBMC URL (for download count) even when there is an external URL
            req.add_header('User-Agent','Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.3) Gecko/20070309 Firefox/2.0.0.3')
            connection  = urllib2.urlopen(req)           # Open connection
            if self.itemInfo [ "filename" ] == '' or self.itemInfo [ "filesize" ] <= 0:
                # Try to retrieve file name / file size
                try:
                    headers = connection.info()# Get Headers
                    print "_downloadFile: headers:"
                    print headers
                    print "---"
                    if self.itemInfo [ "filename" ] == '':
                        try:
                            if 'Content-Disposition' in headers:
                                content_disposition =  headers['Content-Disposition']
                                if "\"" in content_disposition:
                                    self.itemInfo [ "filename" ] = headers['Content-Disposition'].split('"')[1]
                                else:
                                    self.itemInfo [ "filename" ] = headers['Content-Disposition'].split('=')[1]
                                    
                            if self.itemInfo [ "filename" ] == '':
                                # It wasn't possible to read filename within the headers
                                realURL = connection.geturl().encode('utf-8') # Get URL (possible redirection)
                                print realURL
                                if self.itemInfo [ "url" ] != realURL:
                                    # Redirection
                                    print "redirect url = %s"%realURL
                                    self.itemInfo [ "filename" ] = os.path.basename(realURL)
                                    if not self.itemInfo [ "filename" ].lower().endswith('zip') and not self.itemInfo [ "filename" ].lower().endswith('rar'):
                                        self.itemInfo [ "filename" ] = "unknownfilename"
                                        status = "ERRORFILENAME"
                                else:
                                    self.itemInfo [ "filename" ] = "unknownfilename"
                                    status = "ERRORFILENAME"
                        except:
                            self.itemInfo [ "filename" ] = "unknownfilename"
                            status = "ERRORFILENAME"
                            print_exc()
                    #if self.itemInfo [ "filesize" ] <= 0:
                    try:
                        self.itemInfo [ "filesize" ] = int( headers['Content-Length'] )
                    except:
                        pass

                except Exception, e:
                    self.itemInfo [ "filename" ] = "unknownfilename"
                    status = "ERRORFILENAME"
                    self.itemInfo [ "filesize" ] = 0
                    print("_downloadFile - Exception retrieving header")
                    print(str(e))
                    print_exc()

            
            destination = xbmc.translatePath( os.path.join( destinationDir, self.itemInfo [ "filename" ] ) )
            print "_downloadFile - file name : %s "%self.itemInfo [ "filename" ]
            print "_downloadFile - file size : %d Octet(s)"%self.itemInfo [ "filesize" ]
            print "_downloadFile: destination %s"%destination
            


            file = open(destination,'w+b')        # Get ready for writing file
            print "_downloadFile: File opened"
            # Ask for display of progress bar
            try:
                if (progressBar != None):
                    #progressBar.update(percent_downloaded)
                    progressBar.update( percent_downloaded, _( 122 ) % ( self.itemInfo [ "name" ] ), _( 123 ) % percent_downloaded )
            except Exception, e:        
                print("_downloadFile - Exception calling UI callback for download")
                print(str(e))
                print progressBar
                
            ###########
            # Download
            ###########
            print "_downloadFile: Starting download"
            while 1:
                if (progressBar != None):
                    if progressBar.iscanceled():
                        print "_downloadFile: Downloaded STOPPED by the user"
                        status = "CANCELED"
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
                    print ("_downloadFile: error during reading of the remote file and writing it locally: " + str(sys.exc_info()[0]))
                    print_exc()
                    status = "ERROR"
                try:
                    # Compute percent of download in progress
                    New_percent_downloaded = min((num_blocks*block_size*100)/self.itemInfo [ "filesize" ], 100)
                    #print "_downloadFile - Percent = %d"%New_percent_downloaded
                except Exception, e:        
                    print("_downloadFile - Exception computing percentage downloaded")
                    print(str(e))
                    New_percent_downloaded = 0
                # We send an update only when percent number increases
                if (New_percent_downloaded > percent_downloaded):
                    percent_downloaded = New_percent_downloaded
                    # Call UI callback in order to update download progress info
                    if (progressBar != None):
                        #progressBar.update(percent_downloaded)
                        progressBar.update( percent_downloaded, _( 122 ) % ( self.itemInfo [ "name" ] ), _( 123 ) % percent_downloaded )


            # Closing the file
            file.close()
            # End of writing: Closing the connection and the file
            connection.close()
        except Exception, e:
            status = "ERROR"
            print("_downloadFile: Exception while source retrieving")
            print(str(e))
            print ("_downloadFile: error while source retrieving: " + str(sys.exc_info()[0]))
            print_exc()
            print("_downloadFile ENDED with ERROR")

#            # Prepare message to the UI
#            msgType = "Error"
#            msgTite = _ ( 144 )
#            msg1    = file_name
#            msg2    = ""
#            msg3    = ""

        print "_downloadFile: status of download"
        print status
        print destination
        print("_downloadFile ENDED")
                
        return status, destination
        
