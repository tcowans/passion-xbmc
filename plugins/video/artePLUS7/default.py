# -*- coding: cp1252 -*-
"""
ARTE Plus7 video plugin for XBMC 

Place in Q:\plugins\video\artePLUS7

13-10-07 Version Alpha Release by Lolol (cf. http://xbmc.org/forum/showthread.php?t=29100)
    - Creation
29-11-08 Version Alpha2 by Temhil and Seb
    - Fixed issue with icons
    - Fixed issue wit video loading using createVideoURL which create a UNRl from the video preview URL
    - Replaced default URL by French one instead of German
02-12-08 Version Beta1 by Temhil
    - Added proxy support for people wiht not an PI address in the area supported by Arte website
      Proxy has to be defined in arteplus7.cfg as follow:
      [server]
      proxy_address = http://<IP-adress>
    - Updated getVideoURL in order to use proxy AND load real video URL in wmv container
    - Added video language support, it has to be defined (fr = fench / de = German) as follow 
      [user_pref]
      videos_language = fr
    - Conf file is generated automatically during 1st startup:
      -> default video language is French
      -> default proxy is empty (no proxy)
07-12-08 Version Beta1.1 by Seb
    - Corrected progress bar update issue
07-12-08 Version Beta2 by Temhil
    - Improved algorithm with proxy use, now proxy is used only for a video (not for the list)
05-10-09 Version 1.0 by Temhil
    - Added automatic proxy support (using webproxy www.surferanonymement.com) 
    - Added plugin settings menu
    - Added video description window
    - Added video info while playing
05-19-09 Version 1.0b by Temhil
    - Added German language (thanks to Lolo)
    - Added finnish language (thanks to Kottis)
    - Fixed few localization bug (few strings still in french) 
07-05-09 Version 1.1 by Temhil
	- Fixed regex for automatic proxy due to changes on webiste
	- Use www.surferanonymement.com now for getting the real video URL (country check is done)
	- Moved webpage download management in a separate function
"""

__script__ = "Unknown"
__plugin__ = "artePLUS7"
__author__ = "Lolol, Temhil, Seb"
__url__ = "http://passion-xbmc.org/index.php"
__svn_url__ = "http://code.google.com/p/passion-xbmc/source/browse/#svn/trunk/plugins/video/artePLUS7"
__credits__ = "Team XBMC Passion"
__platform__ = "xbmc media center"
__date__ = "05-07-2009"
__version__ = "1.1"
__svn_revision__ = 0

import xml.dom.minidom, urllib, os, string, traceback, time, re
import xbmc, xbmcgui, xbmcplugin
import traceback
import urllib2
#import ConfigParser
import sys
from resources.libs.specialpath import *



INDEX_PROXY_NONE = 0
INDEX_PROXY_AUTO = 1
INDEX_PROXY_STD  = 2

# Set directories
ROOTDIR  = os.getcwd().replace( ";", "" ) # Create a path with valid format
CACHEDIR = os.path.join(ROOTDIR, "cache")
  
#BASE_THUMBS_PATH = os.path.join( SPECIAL_PROFILE_DIR, "Thumbnails", 'Video' )
BASE_THUMBS_PATH = os.path.join( SPECIAL_MASTERPROFILE_DIR, "Thumbnails", 'Video' )
__language__ = xbmc.Language( ROOTDIR, "french" ).getLocalizedString



def strip_off( text, by="", xbmc_labels_formatting=False ):
    """ FONCTION POUR RECUPERER UN TEXTE D'UN TAG """
    if xbmc_labels_formatting:
        text = text.replace( "[", "<" ).replace( "]", ">" )
    return re.sub( "(?s)<[^>]*>", by, text )

class SearchParser:
    """
    Parse XML from arte - code from seeqpod. seeqpod Borrowed this from GameTrailersRSSReader RSS Parser
    """
    def __init__(self):
        # Document Object Model of the XML document

        self.dom = None
        #self.cfgMgr = confManager(os.path.join(ROOTDIR,"arteplus7.cfg"))
        self.verifrep(CACHEDIR)
        print "xbmcplugin.getSetting('language')"
        print xbmcplugin.getSetting('language')
        if int(xbmcplugin.getSetting('language')) == 1:
            # German videos
            print "German videos"
            self.video_feed_url = "http://plus7.arte.tv/de/streaming-home/1698112,templateId=renderCarouselXml,CmPage=1697480,CmPart=com.arte-tv.streaming.xml"
        else: 
            # French videos
            print "French videos"
            self.video_feed_url = "http://plus7.arte.tv/fr/streaming-home/1698112,templateId=renderCarouselXml,CmPage=1697480,CmPart=com.arte-tv.streaming.xml"
                                           
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
    
    def feed(self, url):
        """
        feeds the xml document from given url to the parser
        """
        self.dom = None
        #print url
        f = urllib.urlopen(url)
        xmlDocument = f.read()
        f.close()
        self.dom = xml.dom.minidom.parseString(xmlDocument)


    def getwebpage( self, url ):
        """
        Download webpage using specfic proxy settings
        """
        base_webproxy_url="http://www.surferanonymement.com/includes/process.php?action=update"
        referer = "http://www.surferanonymement.com/"
        nameInForm = 'u'
        
        opener              = None
        videoUrl            = ""
        videoContainerUrl   = "" 
        webpage             = None
        
        if ( int( xbmcplugin.getSetting('proxy') ) == INDEX_PROXY_AUTO ): # Auto
            print "getVideoURL - Auto: Use of Webproxy viproxy.info"
            
            h=urllib2.HTTPHandler(debuglevel=0)
            values = {'%s'%nameInForm : url}
            data = urllib.urlencode(values)
            print base_webproxy_url
            print data
            # Get the Web page with the video url container link
            #req=urllib2.Request(base_webproxy_url + urllib.quote(url) + "&b=4&f=norefer")
            req=urllib2.Request(base_webproxy_url, data)
            req.add_header('Referer', '%s'%referer)
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 MRA 5.3 (build 02560) Firefox/3.0.7 FirePHP/0.2.4')
            req.add_header('Accept','text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')
            req.add_header('Accept-Language','fr,fr-fr;q=0.8,en-us;q=0.5,en;q=0.3')
            req.add_header('Accept-Charset','ISO-8859-1,utf-8;q=0.7,*;q=0.7')
            req.add_header('Keep-Alive','300')
            req.add_header('Connection','keep-alive')
    
            opener = urllib2.build_opener(h)
    
        elif (  int( xbmcplugin.getSetting('proxy') ) ==  INDEX_PROXY_STD ): 
            if ( ( xbmcplugin.getSetting('proxy_ip') != "" ) and ( xbmcplugin.getSetting('proxy_port') != "" ) ):
                print "getVideoURL - proxy DEFINED"
                proxy_address = xbmcplugin.getSetting('proxy_ip') + ":" + xbmcplugin.getSetting('proxy_port')
                print proxy_address
                
                # create the proxy handler
                proxy_handler = urllib2.ProxyHandler({'http':proxy_address})
                
                # create opener
                opener = urllib2.build_opener(proxy_handler)
                
                # Get the Web page with the video url container link
                req=urllib2.Request(videoPage)
            else:
                print "getVideoURL - proxy settings INCORRECT"
                dialogError = xbmcgui.Dialog()
                ok = dialogError.ok(__language__( 30201 ), __language__( 30206 )+'\n\n' + __language__( 30207 ))
                    
                    
        else:
            print "getVideoURL - NO proxy defined"
            # create opener
            opener = urllib2.build_opener()
            
            # Get the Web page with the video url container link
            req=urllib2.Request(videoPage)
        try:     
            # install the opener
            urllib2.install_opener(opener)
            
            # Get the webpage
            response = urllib2.urlopen(req)
            webpage = response.read()
            response.close()

        except:
            print ( str( sys.exc_info()[0] ) )
            traceback.print_exc()

        return webpage


    def loadVideo( self, videoPage, title, thumbnailImageURL ):
        """
        Load video info and start playing
        """
        print "loadVideo - videoPage = %s"%videoPage
                
        dialogLoading = xbmcgui.DialogProgress()
        dialogLoading.create( __language__( 30208 ) ) 
        
        # Get the video description webpage
        videoDoc = self.getwebpage( videoPage )
        try:     
            # Write in a file
            #TODO: save only in debug mode and check why it crash on XBOX
#            htmlsave = os.path.join( CACHEDIR, urllib.quote_plus( os.path.basename( videoPage ) ) )
#            print 'htmlsave'
#            print htmlsave
#            open( xbmc.makeLegalFilename( htmlsave ),"w" ).write( videoDoc )

            # Extract the URL of the video URL container file (wmv)
            match = re.search(r'availableFormats\[\d]\[\"format\"\] = \"WMV\";\n *?availableFormats\[\d\]\["quality\"] = \"HQ\";\n *?availableFormats\[\d]\[\"url\"] = \"(.*?)\";', videoDoc)
            videoContainerUrl = ""
            if match:
                videoContainerUrl = match.group(1)
                print "video Container URL = "
                print videoContainerUrl
                
                # Get the video url container file
                #videoUrlFile = urllib.urlopen(videoContainerUrl).read()
                videoUrlFile = self.getwebpage( videoContainerUrl )
                
                # Write in a file
                #TODO: save only in debug mode and check why it crash on XBOX
#                wmvsave = os.path.join( CACHEDIR, urllib.quote_plus( os.path.basename( videoContainerUrl ) ) )
#                print 'wmvsave'
#                print wmvsave
#                open( xbmc.makeLegalFilename( wmvsave ),"w" ).write( videoUrlFile )
                
                # Extract the URL of the video (usually mms)
                matchVideoURL = re.search(r'<REF HREF=\"(.*?)\"', videoUrlFile)
                if matchVideoURL:
                    videoUrl = matchVideoURL.group(1)
        except:
            print ( str( sys.exc_info()[0] ) )
            traceback.print_exc()
                
        print 'URL of the video:'
        print videoUrl

        #TODO: Check if mms download can be supported by XBMC
        if ( videoUrl != ""):
            # Get player type
            player_type_idx = int(xbmcplugin.getSetting("dvdplayer"))
            player_type = {0:xbmc.PLAYER_CORE_AUTO, 1:xbmc.PLAYER_CORE_MPLAYER, 2:xbmc.PLAYER_CORE_DVDPLAYER}[player_type_idx]

            #  Get cached thumbnail instead of redownload it
            thumbnailImage = xbmc.getCacheThumbName( sys.argv[ 0 ] + sys.argv[ 2 ] )
            #print thumbnailImage
            thumbnailpath = os.path.join( BASE_THUMBS_PATH, thumbnailImage[ 0 ], thumbnailImage )
            print "thumbnail path:"
            print thumbnailpath
            videoListItem = xbmcgui.ListItem( label=title, thumbnailImage=thumbnailpath) 
           
            dialogLoading.close()
            xbmc.Player( player_type ).play( str(videoUrl), videoListItem )
            xbmc.sleep(200)
            
        else:
            dialogLoading.close()
            dialogError = xbmcgui.Dialog()
            ok = dialogError.ok(__language__( 30201 ), __language__( 30204 )+'\n\n' + __language__( 30205 ))
                   
#    def downloadFile(self, source, destination):
#        """
#        Source MyCine (thanks!)
#        Download IF NECESSARY a URL 'source' (string) to a URL 'target' (string)
#        Source is downloaded only if target doesn't already exist
#        """
#        if os.path.exists(destination):
#            pass
#        else:
#            try:
#                #print("downloadJPG destination doesn't exist, try to retrieve")
#                loc = urllib.URLopener()
#                loc.retrieve(source, destination)
#            except Exception, e:
#                print("Exception while source retrieving")
#                print(e)
#                print (str(sys.exc_info()[0]))
#                traceback.print_exc()
#                pass


    # parses the RSS document, for now it assumes that RSS document is valid
    def parse(self):
        self.delFiles(CACHEDIR)
        self.feed(self.video_feed_url)
        self.__parseItems()
    
    # parses RSS document items and returns an list containing RSSItem objects
    def __parseItems(self):
        items = self.dom.getElementsByTagName("video")
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
                
                index = self.index[i]
                #print "i = %d"%i
                #print "self.thumbs[i] (URL) = %s"%self.thumbs[i]
                #print "self.urls[i] = %s"%self.urls[i]

                item=xbmcgui.ListItem(index.zfill(2)+' - '+self.titles[i], iconImage = self.thumbs[i], thumbnailImage = self.thumbs[i])
                #item.setInfo( type="Video", infoLabels={ "Title": self.titles[i] } )
                
                if (xbmcplugin.getSetting('download_descript') == 'true'):
                    title, headline, plot, country, year, duration = self._parseInfo(self.urls[i])
                    item.setInfo( type="Video",
                                  infoLabels={ "Title": self.titles[i],
                                               "Plotoutline": headline,
                                               "Year": year,
                                               "Plot": plot})
                else:
                    item.setInfo( type="Video", infoLabels={ "Title": self.titles[i] } )

                u = sys.argv[0]+"?url=%s&loadvideo&title=%s&thumbnail=%s"%( urllib.quote_plus(self.urls[i]), self.titles[i], urllib.quote_plus(self.thumbs[i]) )
                
                ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=item,isFolder=False,totalItems=len(items))
            except Exception, e:
                error=1
                print "Something was wrong during __parseItems!"
                print e
                print (str(sys.exc_info()[0]))
                traceback.print_exc()
                
        #TODO: Use language localization
        xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category=__language__( 30204 ) )
 
        path_img = os.path.join(ROOTDIR,"arte_tv.png")
        fanart_color1 = "ffffff00"
        fanart_color2 = ""
        fanart_color3 = ""
        try:
            #xbmcplugin.setPluginFanart( handle=int( sys.argv[ 1 ] ), image=path_img, color1=fanart_color1, color2=fanart_color2, color3=fanart_color3 )
            #TODO  :
            xbmcplugin.setContent(int(sys.argv[1]), 'videos')
            xbmcplugin.setPluginFanart(int(sys.argv[1]), path_img)
            xbmc.sleep( 10 )
        except:
            error=1
            print "Something was wrong during setPluginFanart!"
            print (str(sys.exc_info()[0]))
            traceback.print_exc()
            
        return itemObjects

    def _parseInfo(self, urlInfo):
        # Extract video infos:
        title = None
        headline = None
        plot = None
        country = None
        year = None
        duration = None
        try:     
            # create opener
            opener = urllib2.build_opener()
            
            # Get the Web page with the video url container link
            req=urllib2.Request(urlInfo)
            
            # install the opener
            urllib2.install_opener(opener)
            
            response = urllib2.urlopen(req)
            videoDoc = response.read()
            response.close()

            reVideo = re.compile(r"""<h2>\s+(?P<videoShowTitle>.+?)\n</h2>.*?<p class="headline">\s+(?P<videoHeadline>.+?)<br />.*?<p class="text">\s+(?P<videoDescript>.+?)<br />.*?<p class="info">.*?\((?P<videoCountry>.+?), (?P<videoYear>[0-9].+?), (?P<videoDuration>.+?)\)""", re.DOTALL) 
            for i in reVideo.finditer( videoDoc ):
                # Copy each item found in a list
                videoShowTitle     = i.group( "videoShowTitle" )
                if videoShowTitle: # !=None
                    title = strip_off( unicode( videoShowTitle, "utf-8" ).encode( "cp1252" ) )
                    #print "title: %s"%title
                videoHeadline     = i.group( "videoHeadline" )
                if videoHeadline: # !=None
                    headline = strip_off( unicode( videoHeadline, "utf-8" ).encode( "cp1252" ) )
                    #print "headline: %s"%headline
                videoDescript     = i.group( "videoDescript" )
                if videoDescript: # !=None
                    plot = strip_off( unicode( videoDescript, "utf-8" ).encode( "cp1252" ) )
                    #print "plot: %s"%plot
                videoCountry     = i.group( "videoCountry" )
                if videoCountry: # !=None
                    country = strip_off( unicode( videoCountry, "utf-8" ).encode( "cp1252" ) )
                    #print "country: %s"%country
                videoYear     = i.group( "videoYear" )
                if videoYear: # !=None
                    year = int( videoYear )
                    #print "year: %d"%year
                videoDuration     = i.group( "videoDuration" )
                if videoDuration: # !=None
                    duration = strip_off( unicode( videoDuration, "utf-8" ).encode( "cp1252" ) )
                    #print "duration: %s"%duration
        except Exception, e:
            print"Exception during loadVideo: Extract video infos"
            print str(e)
            print str(sys.exc_info()[0])
            traceback.print_exc()
        return title, headline, plot, country, year, duration
        

############
#
# Main
#
############

# Check settings
if ( xbmcplugin.getSetting('first_start') == 'true' ):
    try:
        dialog = xbmcgui.Dialog()
        dialog.ok( __language__(30200), __language__(30201) )
        xbmcplugin.openSettings(sys.argv[0])
        xbmcplugin.setSetting('first_start','false')
    except:
        # builtin missing from build - inform user to use ContextMenu for settings
        traceback.print_exc()
        dialog = xbmcgui.Dialog()
        dialog.ok( __language__(30202), __language__(30202), __language__(30203) )

print "first_start:"
print xbmcplugin.getSetting('first_start')
# Parse parameter
stringparams = sys.argv[2] #les paramètres sont sur le 3ieme argument passé au script

try:
    if stringparams[0]=="?":#pour enlever le ? si il est en début des paramètres
        stringparams=stringparams[1:]
except:
    pass
parametres={}
for param in stringparams.split("&"):#on découpe les paramètres sur le '&'
    try:
        cle,valeur=param.split("=")#on sépare les couples clé/valeur
    except:
        cle=param
        valeur=""
    parametres[cle]=valeur #on rempli le dictionnaire des paramètres
#voilà, 'parametres' contient les paramètres parsés


s=SearchParser()
#xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=False)
if "loadvideo" in parametres.keys():
    
    # Play video
    urlVideoPage=urllib.unquote_plus(parametres["url"])
    print "urlVideoPage: "
    print urlVideoPage
    print parametres
    s.loadVideo(urlVideoPage, parametres["title"], parametres["thumbnail"] )
else:
    # Video list
    s.parse()
    
xbmcplugin.endOfDirectory(int(sys.argv[1]))

