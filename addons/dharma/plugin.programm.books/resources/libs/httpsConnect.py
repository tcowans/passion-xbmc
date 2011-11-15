# -*- coding: utf-8 -*-
import urllib
import urllib2
import re, os, sys



class HttpsConnect:
    
  def __init__(self,cookiesUrl,userAgent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'):

    
    self.cookiesUrl = cookiesUrl
    self.userAgent = {'User-agent' : userAgent}
    # the path and filename to save your cookies in

    self.cj = None
    ClientCookie = None
    cookielib = None
    self.httpsForm = None

    # Let's see if cookielib is available
    try:
        import cookielib
    except ImportError:
        # If importing cookielib fails
        # let's try ClientCookie
        try:
            import ClientCookie
        except ImportError:
            # ClientCookie isn't available either
            self.urlopen = urllib2.urlopen
            self.Request = urllib2.Request
        else:
            # imported ClientCookie
            self.urlopen = ClientCookie.urlopen
            self.Request = ClientCookie.Request
            self.cj = ClientCookie.LWPCookieJar()

    else:
        # importing cookielib worked
        self.urlopen = urllib2.urlopen
        self.Request = urllib2.Request
        self.cj = cookielib.LWPCookieJar()
        # This is a subclass of FileCookieJar
        # that has useful load and save methods



    if self.cj is not None:
    # we successfully imported
    # one of the two cookie handling modules

        if os.path.isfile(self.cookiesUrl):
            # if we have a cookie file already saved
            # then load the cookies into the Cookie Jar
            self.cj.load(self.cookiesUrl)

        # Now we need to get our Cookie Jar
        # installed in the opener;
        # for fetching URLs
        if cookielib is not None:
            # if we use cookielib
            # then we get the HTTPCookieProcessor
            # and install the opener in urllib2
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
            urllib2.install_opener(opener)

        else:
            # if we use ClientCookie
            # then we get the HTTPCookieProcessor
            # and install the opener in ClientCookie
            opener = ClientCookie.build_opener(ClientCookie.HTTPCookieProcessor(self.cj))
            ClientCookie.install_opener(opener)          


  def returnForm(self) :
      return self.httpsForm

  def httpsRequest(self,urlRequest,dataRequest={},headerRequest={}) :
        headerRequest =  dict(self.userAgent.items() + headerRequest.items())
        print headerRequest
        
        request_body = urllib.urlencode(dataRequest)
        # fake a user agent, some websites (like google) don't like automated exploration
        
        try:
            req = self.Request(urlRequest, request_body, headerRequest)
            # create a request object

            handle = self.urlopen(req)
            #print handle.read(),handle.info()
            print self.cj
            # and open it to return a handle on the url

        except IOError, e:
            print 'We failed to open "%s".' % urlRequest
            if hasattr(e, 'code'):
                print 'We failed with error code - %s.' % e.code
            elif hasattr(e, 'reason'):
                print "The error object has the following 'reason' attribute :"
                print e.reason
                print "This usually means the server doesn't exist,"
                print "is down, or we don't have an internet connection."
            sys.exit()

        else:
            print 'Here are the headers of the page :'
            # handle.read() returns the page
            # handle.geturl() returns the true url of the page fetched
            # (in case urlopen has followed any redirects, which it sometimes does)


        
        if self.cj is None:
            print "We don't have a cookie library available - sorry."
            print "I can't show you any cookies."
        else:
            print 'These are the cookies we have received so far :'
            for index, cookie in enumerate(self.cj):
                print index, '  :  ', cookie
            self.cj.save(self.cookiesUrl)                     # save the cookies again

            
        return handle.read(),handle.info()
