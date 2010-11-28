import zlib
import httplib
import urllib
import urllib2
import gzip
import StringIO
import os

class HTTPCommunicator :
    """
    From gamespot plugin by Dan Dar 3
    """
    #
    # POST
    #
    def post( self, host, url, params ):
        parameters  = urllib.urlencode( params )
        headers     = { "Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain", "Accept-Encoding" : "gzip" }
        connection  = httplib.HTTPConnection("%s:80" % host)
        
        connection.request( "POST", url, parameters, headers )
        response = connection.getresponse()
        
        # Compressed (gzip) response...
        if response.getheader( "content-encoding" ) == "gzip" :
            htmlGzippedData = response.read()
            stringIO       = StringIO.StringIO( htmlGzippedData )
            gzipper        = gzip.GzipFile( fileobj = stringIO )
            htmlData       = gzipper.read()
        # Plain text response...
        else :
            htmlData = response.read()

        # Cleanup
        connection.close()

        # Return value
        return htmlData

    #
    # GET
    #
    def get( self, url ):
        h = urllib2.HTTPHandler(debuglevel=0)
        
        request = urllib2.Request( url )
        request.add_header( "Accept-Encoding", "gzip" ) 
        opener = urllib2.build_opener(h)
        f = opener.open(request)

        # Compressed (gzip) response...
        if f.headers.get( "content-encoding" ) == "gzip" :
            htmlGzippedData = f.read()
            stringIO        = StringIO.StringIO( htmlGzippedData )
            gzipper         = gzip.GzipFile( fileobj = stringIO )
            htmlData        = gzipper.read()
            
            # Debug
            # print "[HTTP Communicator] GET %s" % url
            # print "[HTTP Communicator] Result size : compressed [%u], decompressed [%u]" % ( len( htmlGzippedData ), len ( htmlData ) )
            
        # Plain text response...
        else :
            htmlData = f.read()
        
        # Cleanup
        f.close()

        # Return value
        return htmlData
    
    
def url_join(*args):
    """
    Join any arbitrary strings into a forward-slash delimited list.
    Do not strip leading / from first element, nor trailing / from last element.
    From Coders Eye
    """
    if len(args) == 0:
        return ""

    if len(args) == 1:
        return str(args[0])

    else:
        args = [str(arg).replace("\\", "/") for arg in args]

        work = [args[0]]
        for arg in args[1:]:
            if arg.startswith("/"):
                work.append(arg[1:])
            else:
                work.append(arg)

        joined = reduce(os.path.join, work)

    return joined.replace("\\", "/")