

import os
import ftplib
from traceback import print_exc

from urlparse25 import urlparse

import xbmc
import xbmcplugin


class FileCopy:
    def __init__( self, *args, **kwargs ):
        self.nfo_OK = ""
        self.tbn_OK = ""
        self.fanart_OK = ""

        self.report_copy = kwargs.get( "report_copy" )
 
        self.nfo_source = kwargs.get( "nfo_source", "" )
        self.movie_path = kwargs.get( "movie_path", "" )
        self.thumbnail  = kwargs.get( "thumbnail", "" )
        self.fanart     = kwargs.get( "fanart", "" )

        if self.movie_path.startswith( "ftp://" ):
            self.ftp_copy()
        else:
            self.xbmc_copy()
            self._copy_thumbnails()

    def xbmc_copy( self ):
        print
        print "FileCopy::xbmc_copy"
        try:
            nfo_dest = os.path.splitext( self.movie_path )[ 0 ] + ".nfo"
            if hasattr( self.report_copy, "update" ):
                self.report_copy.update( -1, self.nfo_source, nfo_dest )
            try: OK = xbmc.executehttpapi( "FileCopy(%s,%s)" % ( self.nfo_source, nfo_dest.encode( "utf-8" ), ) )
            except: OK = ""
            if ( not OK ) or ( not "<li>ok" in OK.lower() ):
                OK = xbmc.executehttpapi( "FileCopy(%s,%s)" % ( self.nfo_source, nfo_dest, ) )
            if ( "<li>ok" in OK.lower() ):
                self.nfo_OK = nfo_dest
        except:
            print_exc()

    def _copy_thumbnails( self ):
        print
        print "FileCopy::_copy_thumbnails"
        try:
            # set our thumbnail
            install_thumbnail = self.thumbnail or xbmc.getInfoImage( "ListItem.Thumb" )
            Fanart_thumbnail = self.fanart or xbmc.getInfoImage( "Fanart.Image" )

            #print "ListItem.Thumb", install_thumbnail
            if os.path.exists( install_thumbnail ) or os.path.isfile( install_thumbnail ):
                if ( not "Error! File not found" in file( install_thumbnail, "r" ).read() ):
                    thumbpath = os.path.splitext( self.movie_path )[ 0 ] + ".tbn"
                    if hasattr( self.report_copy, "update" ):
                        self.report_copy.update( -1, install_thumbnail, thumbpath )
                    try: OK = xbmc.executehttpapi( "FileCopy(%s,%s)" % ( install_thumbnail, thumbpath.encode( "utf-8" ), ) )
                    except: OK = ""
                    if ( not OK ) or ( not "<li>ok" in OK.lower() ):
                        OK = xbmc.executehttpapi( "FileCopy(%s,%s)" % ( install_thumbnail, thumbpath, ) )
                    if ( "<li>ok" in OK.lower() ):
                        self.tbn_OK = thumbpath
                else:
                    self.tbn_OK = "XBMC.ListItem.Thumb: Error! File not found" 
                    try: os.remove( install_thumbnail )
                    except: pass
            else:
                self.tbn_OK = "XBMC.ListItem.Thumb: not exists!"
        except:
            print_exc()

        try:
            #print
            #print "Fanart.Image", Fanart_thumbnail
            if os.path.exists( Fanart_thumbnail ) or os.path.isfile( Fanart_thumbnail ):
                if ( not "Error! File not found" in file( Fanart_thumbnail, "r" ).read() ):
                    fanartpath = os.path.splitext( self.movie_path )[ 0 ] + "-fanart.jpg"
                    if hasattr( self.report_copy, "update" ):
                        self.report_copy.update( -1, Fanart_thumbnail, fanartpath )
                    try: OK = xbmc.executehttpapi( "FileCopy(%s,%s)" % ( Fanart_thumbnail, fanartpath.encode( "utf-8" ), ) )
                    except: OK = ""
                    if ( not OK ) or ( not "<li>ok" in OK.lower() ):
                        OK = xbmc.executehttpapi( "FileCopy(%s,%s)" % ( Fanart_thumbnail, fanartpath, ) )
                    if ( "<li>ok" in OK.lower() ):
                        self.fanart_OK = fanartpath
                else:
                    self.fanart_OK = "XBMC.Fanart.Image: Error! File not found" 
                    try: os.remove( Fanart_thumbnail )
                    except: pass
            else:
                self.fanart_OK = "XBMC.Fanart.Image: not exists!"
        except:
            print_exc()

    def ftp_copy( self ):
        print
        print "FileCopy::ftp_copy"
        try:
            def upload( ftp, file, dest ):
                ext = os.path.splitext( file )[ 1 ]
                if ext in ( ".txt", ".htm", ".html", ".nfo" ):
                    ftp.storlines( "STOR " + dest, open( file ) )
                    print 'ftp.storlines'
                else:
                    ftp.storbinary( "STOR " + dest, open( file, "rb" ), 1024 )
                    print 'ftp.storbinary'

            parsed = urlparse( self.movie_path )
            if ( parsed.scheme.lower() == "ftp" ):
                #port = parsed.port # not used
                moviepath = parsed.path
                #print parsed.hostname
                #print parsed.username
                #print parsed.password

                # set our thumbnail
                install_thumbnail = self.thumbnail or xbmc.getInfoImage( "ListItem.Thumb" )
                Fanart_thumbnail = self.fanart or xbmc.getInfoImage( "Fanart.Image" )

                ftp = ftplib.FTP( parsed.hostname )
                ftp.login( parsed.username, parsed.password )
                ftp.cwd( os.path.dirname( moviepath ) )

                # copy nfo file
                try:
                    nfo_dest = os.path.splitext( moviepath )[ 0 ] + ".nfo"
                    if hasattr( self.report_copy, "update" ):
                        self.report_copy.update( -1, self.nfo_source, nfo_dest )
                    upload( ftp, self.nfo_source, nfo_dest )
                    self.nfo_OK = nfo_dest
                except:
                    print_exc()

                # copy thumbnail
                try:
                    thumbpath = os.path.splitext( moviepath )[ 0 ] + ".tbn"
                    if hasattr( self.report_copy, "update" ):
                        self.report_copy.update( -1, install_thumbnail, thumbpath )
                    upload( ftp, install_thumbnail, thumbpath )
                    self.tbn_OK = thumbpath
                except:
                    print_exc()

                # copy fanart
                try:
                    fanartpath = os.path.splitext( moviepath )[ 0 ] + "-fanart.jpg"
                    if hasattr( self.report_copy, "update" ):
                        self.report_copy.update( -1, Fanart_thumbnail, fanartpath )
                    upload( ftp, Fanart_thumbnail, fanartpath )
                    self.fanart_OK = fanartpath
                except:
                    print_exc()

                ftp.close()
        except:
            print_exc()
