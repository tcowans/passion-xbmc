# -*- coding: cp1252 -*-
"""
ARTE Plus7 video plugin for XBMC 

Place in Q:\plugins\video\artePLUS7

13-10-05 Version Alpha Release by Lolol (cf. http://xbmc.org/forum/showthread.php?t=29100)
    - Creation
29-11-08 Version Alpha2 by Temhil and Seb
    - Fixed issue with icons
    - Fixed issue wit video loading using createVideoURL which create a UNRl from the video preview URL
    - Replaced default URL by French one instead of German
29-11-08 Version Beta1-Dev01 by Temhil
    - Added proxy support for people wiht not an PI address in the area supported by Arte website
      Proxy has to be defined in arteplus7.cfg as follow:
      [server]
      proxy_address = http://<IP-adress>
    - Updated getVideoURL in order to use proxy AND load real video URL in wmv container
"""
import xml.dom.minidom, urllib, os, string, traceback, time, re
import xbmc, xbmcgui, xbmcplugin
import traceback
import urllib2
import ConfigParser


# Set directories
RootDir  = os.getcwd().replace( ";", "" ) # Create a path with valid format
cacheDir = os.path.join(RootDir, "cache")

class SearchParser:
    """
    Parse XML  from arte - code from seeqpod. seeqpod Borrowed this from GameTrailersRSSReader RSS Parser
    """
    def __init__(self):
        # Document Object Model of the XML document
        self.dom = None
        self.proxy_address = None
        self.loadConf()
        self.verifrep(cacheDir)
        
                                           
    def verifrep(self, folder):
        """
        Check a folder exists and make it if necessary
        """
        try:
            #print("verifrep check if directory: " + folder + " exists")
            if not os.path.exists(folder):
                print("verifrep Impossible to find the directory - trying to create the directory: " + folder)
                os.makedirs(folder)
        except Exception, e:
            print("Exception while creating folder " + folder)
            print(str(e))

    def loadConf(self):
        """
        Load configuration file, check it, and correct it if necessary
        """
        try:
            # Create config parser
            self.config = ConfigParser.ConfigParser()
            
            # Read config from .cfg file
            # - Open config file
            self.config.read(os.path.join(RootDir,"arteplus7.cfg"))

            # Check sections exist
            if (self.config.has_section("server") == True):
                # - Read config from file and correct it if necessary
                if (self.config.has_option("server", "proxy_address") == True):
                    self.proxy_address = self.config.get("server", "proxy_address")
                    if self.proxy_address == "":
                        self.proxy_address = None
        except IOError:
            print "Error while loading conf file arteplus7.cfg"
            print (str(sys.exc_info()[0]))
            traceback.print_exc(file=sys.stdout)
            
    def delFiles(self,folder):
        """
        Delete file form cache directory
        """
        for root, dirs, files in os.walk(folder , topdown=False):
            for name in files:
                print "Deleting %s ..."%name
                try:
                    os.remove(os.path.join(root, name))
                except Exception, e:
                    print e
                    
    def reset(self):                                           
        # Document Object Model of the XML document
        self.dom = None
    
    # feeds the xml document from given url to the parser
    def feed(self, url):
        self.dom = None
        #print url
        f = urllib.urlopen(url)
        xmlDocument = f.read()
        f.close()
        self.dom = xml.dom.minidom.parseString(xmlDocument)

    def getVideoURL(self, videoPage):
        print "getVideoURL - videoPage = %s"%videoPage
        opener              = None
        videoUrl            = ""
        videoContainerUrl   = "" 
                
        if self.proxy_address is None:
            print "getVideoURL - NO proxy defined"
            # create opener
            opener = urllib2.build_opener()
        else:
            print "getVideoURL - proxy DEFINED"
            print self.proxy_address
            
            # create the proxy handler
            proxy_handler = urllib2.ProxyHandler({'http': self.proxy_address})
            
            # create opener
            opener = urllib2.build_opener(proxy_handler)

        # install the opener
        urllib2.install_opener(opener)
        
        # Get the Web page with the video url container link
        req=urllib2.Request(videoPage)
        videoDoc=urllib2.urlopen(req).read()
        
#        # Write in a file
#        open(xbmc.makeLegalFilename(os.path.join(cacheDir, os.path.basename(videoPage))),"w").write(videoDoc)

        # Extract the URL of the video URL container file (wmv)
        match = re.search(r'availableFormats\[\d]\[\"format\"\] = \"WMV\";\n *?availableFormats\[\d\]\["quality\"] = \"HQ\";\n *?availableFormats\[\d]\[\"url\"] = "(.*?)\?obj', videoDoc)
        videoContainerUrl = ""
        if match:
            videoContainerUrl = match.group(1)
            
            # Get the video url container file
            videoUrlFile = urllib.urlopen(videoContainerUrl).read()
            #TODO: use urllib2 everywhere, using a mix or urlib and urllib2 is not very elegant
            
#            # Write in a file
#            open(xbmc.makeLegalFilename(os.path.join(cacheDir, os.path.basename(videoContainerUrl))),"w").write(videoUrlFile)
            
            # Extract the URL of the video (usually mms)
            matchVideoURL = re.search(r'<REF HREF=\"(.*?)\" />', videoUrlFile)
            if matchVideoURL:
                videoUrl = matchVideoURL.group(1)
                
        print "videoContainerUrl = %s"%videoContainerUrl
        print "videoUrl = %s"%videoUrl
        return videoUrl

    def createVideoURL(self, previewVideoUrl):
        """
        Convert previewVideoUrl to real video URL
        Obsolete and replaced by getVideoURL
        This function is faster and more efficient than getVideoURL, but unfortunately does not cover all the case
        """
        print "createVideoURL - BEFORE previewVideoUrl = %s"%previewVideoUrl
        
        #videoUrl_step1 = previewVideoUrl.replace("http://dl.plus7.arte.tv/","mms://a255.v39759c.c39759.g.vm.akamaistream.net/7/255/39759/v0001/artegeie.download.akamai.com/39759/mfile/").replace("21","06").replace("TE","PG").replace("LQ","MQ")
        #self.videoUrl = videoUrl_step1.split("flv")[0] + "wmv"
        videoUrl_step1 = previewVideoUrl.replace("http://dl.plus7.arte.tv/","mms://a255.v39759c.c39759.g.vm.akamaistream.net/7/255/39759/v0001/artegeie.download.akamai.com/39759/mfile/").replace("21","08").replace("TE","PG").replace("LQ","HQ")
        self.videoUrl = videoUrl_step1.split("flv")[0] + "wmv"
        print "createVideoURL - AFTER videoUrl = %s"%self.videoUrl
        return self.videoUrl
        
    def old_downloadFile(self, URL, localfile):
        """
        Download file
        Obsolete and replaced by downloadFile
        """
        print "URL = %s"%URL
        print "localfile = %s"%localfile
        newURL = xbmc.makeLegalFilename(URL)
        print "newURL = %s"%newURL
        try:
            loc = urllib.URLopener()
            #loc.retrieve(URL, localfile)
            loc.retrieve("http://www.gstatic.com/codesite/ph/images/code_sm.png", localfile)
        except IOError:
            print (str(sys.exc_info()[0]))
            traceback.print_exc(file=sys.stdout)
            return -1
        return 0

    def downloadFile(self, source, destination):
        """
        Source MyCine (thanks!)
        Download IF NECESSARY a URL 'source' (string) to a URL 'target' (string)
        Source is downloaded only if target doesn't already exist
        """
        if os.path.exists(destination):
            pass
        else:
            try:
                #print("downloadJPG destination doesn't exist, try to retrieve")
                loc = urllib.URLopener()
                loc.retrieve(source, destination)
            except Exception, e:
                print("Exception while source retrieving")
                print(e)
                print (str(sys.exc_info()[0]))
                traceback.print_exc()
                pass


    # parses the RSS document, for now it assumes that RSS document is valid
    def parse(self):
        self.delFiles(cacheDir)
        self.__parseItems()
    
    # parses RSS document items and returns an list containing RSSItem objects
    def __parseItems(self):
        items = self.dom.getElementsByTagName("video")
        print items
        self.urls={}
        self.thumbs={}
        self.titles={}
        self.index={}
        self.startDates={}
        self.speakingthumbs={}
        self.previewVideoUrl={}
        itemObjects = []
        i=0
        for item in items:
            i=i+1
            #print i
            elements = {}
            try:
                self.thumbs[i] = item.getElementsByTagName("previewPictureURL")[0].childNodes[0].data
                self.urls[i] = item.getElementsByTagName("targetURL")[0].childNodes[0].data
                self.startDates[i] = item.getElementsByTagName("startDate")[0].childNodes[0].data
                self.titles[i] = item.getElementsByTagName("title")[0].childNodes[0].data
                self.index[i] = item.getElementsByTagName("index")[0].childNodes[0].data
                self.previewVideoUrl[i] = item.getElementsByTagName("previewVideoURL")[0].childNodes[0].data
                
                #videoUrl = self.createVideoURL(self.previewVideoUrl[i])
                videoUrl = self.getVideoURL(self.urls[i])
                index = self.index[i]
                localimg = xbmc.makeLegalFilename(os.path.join(cacheDir,self.index[i]+".jpg"))
                #localimg.replace('\\\\','\\')
                print "i = %d"%i
                print "self.thumbs[i] (URL) = %s"%self.thumbs[i]
                print "localimg = %s"%localimg
                self.downloadFile(self.thumbs[i],localimg)

#                liz=xbmcgui.ListItem(index.zfill(2)+' - '+self.titles[i],'',localimg)
                liz=xbmcgui.ListItem(index.zfill(2)+' - '+self.titles[i], iconImage = localimg, thumbnailImage = localimg)
                ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=videoUrl,listitem=liz)
            except:
                error=1
                print "Something was wrong during __parseItems!"
                print (str(sys.exc_info()[0]))
                traceback.print_exc()
        return itemObjects


s=SearchParser()
s.feed("http://plus7.arte.tv/fr/streaming-home/1698112,templateId=renderCarouselXml,CmPage=1697480,CmPart=com.arte-tv.streaming.xml")
s.parse()
    
xbmcplugin.endOfDirectory(int(sys.argv[1]))
