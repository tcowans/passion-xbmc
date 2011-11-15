import zlib
import httplib
import urllib
import urllib2
import gzip
import StringIO
import os
import re

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


def convertStrDate( dateTxt):
    dateResult = "00-00-00"
    monthTxt2Int = { u'janvier'  : 1, 
                     u'février'  : 2, 
                     u'fevrier'  : 2, 
                     u'mars'     : 3, 
                     u'avril'    : 4, 
                     u'mai'      : 5, 
                     u'juin'     : 6, 
                     u'juillet'  : 7, 
                     u'août'     : 8, 
                     u'aout'     : 8, 
                     u'septembre': 9, 
                     u'octobre'  : 10, 
                     u'novembre' : 11, 
                     u'décembre' : 12, 
                     u'decembre' : 12 
                    }
    
    u'Février'.lower()
    splittedDate = dateTxt.split(" ") #u'Jeudi, 04 F\xe9vrier 2010 12:43' --> [u'Jeudi,', u'04', u'F\xe9vrier', u'2010', u'12:43']
    try:
        weekDay    = splittedDate[0]
        dayOfMonth = int( splittedDate[1] )
        monthTxt   = splittedDate[2]
        year       = int(splittedDate[3])
        timeTxt    = splittedDate[4]
        
        # Convert Month to int
        month = int(monthTxt2Int[monthTxt.lower()])
        
        # Create date to return i.e: (2008-12-07)
        #dateResult = "{yyyy}-{mm:0{digits}n}-{dd:0{digits}n}".format(yyyy=year,mm=12, dd=9, digits=2)
        dateResult = str(year).rjust(4, '0') + "-" + str(month).rjust(2, '0') + "-" + str(dayOfMonth).rjust(2, '0')
        
    except:
        print "Error converting Date: %s"%repr(dateTxt)
        print_exc()
    print dateResult
    return dateResult


def set_xbmc_carriage_return( text ):
    """ only for xbmc """
    text = text.replace( "\r\n", "[CR]" )
    text = text.replace( "\n\n", "[CR]" )
    text = text.replace( "\n",   "[CR]" )
    text = text.replace( "\r\r", "[CR]" )
    text = text.replace( "\r",   "[CR]" )
    text = text.replace( "</br>",   "[CR]" )
    return text


def strip_off( text, by="", xbmc_labels_formatting=False ):
    """ FONCTION POUR RECUPERER UN TEXTE D'UN TAG """
    if xbmc_labels_formatting:
        #text = re.sub( "\[url[^>]*?\]|\[/url\]", by, text )
        text = text.replace( "[", "<" ).replace( "]", ">" )
    return re.sub( "(?s)<[^>]*>", by, text )
