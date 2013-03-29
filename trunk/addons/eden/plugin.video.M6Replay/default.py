# -*- coding: utf-8 -*-
"""

plugin video M6 Replay pour XBMC

Please read changelog.txt for more information

"""

REMOTE_DBG       = False # For remote debugging with PyDev (Eclipse)

__addonID__      = "plugin.video.M6Replay"
__author__       = "PECK, mighty_bombero, merindol, Temhil, beenje"
__url__          = "http://passion-xbmc.org/index.php"
__credits__      = "Team XBMC Passion"
__date__         = "26-09-2012"
__version__      = "2.0.7"

import urllib,sys,os,struct
import time
import hashlib
import base64
import string
import pickle
import datetime
import re
from traceback import print_exc
from xml.dom.minidom import parseString

# xbmc modules
import xbmc
import xbmcplugin
import xbmcgui
import xbmcaddon


__addon__ = xbmcaddon.Addon( __addonID__ )
__settings__ = __addon__
__language__ = __addon__.getLocalizedString
__addonDir__ = __settings__.getAddonInfo( "path" )

# Remote debugger using Eclipse and Pydev
if REMOTE_DBG:
    # Note pydevd module need to be copied in XBMC\system\python\Lib\pysrc
    try:
        import pysrc.pydevd as pydevd
        pydevd.settrace('localhost', stdoutToServer=True, stderrToServer=True)
    except ImportError:
        sys.stderr.write("Error: " +
            "You must add org.python.pydev.debug.pysrc to XBMC\system\python\Lib\pysrc")
        sys.exit(1)

ROOTDIR            = __settings__.getAddonInfo('path') # os.getcwd()
BASE_RESOURCE_PATH = os.path.join( ROOTDIR, "resources" )
MEDIA_PATH         = os.path.join( BASE_RESOURCE_PATH, "media" )
#ADDON_DATA         = __addonDir__
ADDON_DATA  = xbmc.translatePath( "special://profile/addon_data/%s/" % __addonID__ )
CACHEDIR           = os.path.join( ADDON_DATA, "cache")
THUMB_CACHE_PATH   = os.path.join( xbmc.translatePath( "special://profile/" ), "Thumbnails", "Video" )

#modules custom
try:
    from resources.lib.utils import convertStrTime2Time, convertTime2FrenchString, bold_text, add_pretty_color, extractDateString, convertMin2Hour
except:
    print_exc()

# Server List
srv_list = [{'rtmp':"rtmpe://groupemsix.fcod.llnwd.net", 'app':"a2883/e1", 'cdn':'llnw'},
            {'rtmp':"rtmpe://m6replayfs.fplive.net", 'app':"m6replaytoken/streaming", 'cdn':'lv3'}]

# List of directories to check at startup
dirCheckList   = ( CACHEDIR, )

# Get the platform and architecture
PYDES_ENABLED = False
SYSTEM_PLATFORM = 'Unknown'
architecture = ''
autoplatform = (__settings__.getSetting('autoplatform') == 'true')
print 'autoplatform: %s' % str(autoplatform)
if not autoplatform:
    os_type_list  = ['All', 'Windows', 'osx', 'ios', 'Linux', 'Xbox']
    cpu_type_list = ['32bit', '64bit', 'arm']
    os_type_id  = int( __settings__.getSetting('ostype') )
    cpu_type_id = int( __settings__.getSetting('cputype') )
    print os_type_list[os_type_id]
    print cpu_type_list[cpu_type_id]
    if os_type_list[os_type_id] in ('Windows', 'Linux'):
        SYSTEM_PLATFORM = os_type_list[os_type_id]
        architecture = cpu_type_list[cpu_type_id]
    elif os_type_list[os_type_id] in ('osx', 'ios'):
        SYSTEM_PLATFORM = 'Darwin'
        architecture = os_type_list[os_type_id]
    elif os_type_list[os_type_id] == 'Xbox':
        SYSTEM_PLATFORM = 'Xbox'
        architecture = ''
    elif os_type_list[os_type_id] == 'All':
        PYDES_ENABLED = True
else:
    # struct.calcsize("P") is 4 or 8 for 32 or 64 bit Python repectively
    # sys.maxsize > 2**32 would be nice to use but is only available from Pyton 2.6
    if struct.calcsize("P") == 8:
        architecture = '64bit'
    else:
        architecture = '32bit'
    if xbmc.getCondVisibility( "system.platform.linux" ):
        SYSTEM_PLATFORM = 'Linux'
        if 'arm' in os.uname()[4]:
            architecture = 'arm'
    elif xbmc.getCondVisibility( "system.platform.xbox" ):
        SYSTEM_PLATFORM = 'Xbox'
        # No architecture directory for Xbox
        architecture = ''
    elif xbmc.getCondVisibility( "system.platform.windows" ):
        SYSTEM_PLATFORM = 'Windows'
    elif xbmc.getCondVisibility( "system.platform.osx" ):
        SYSTEM_PLATFORM = 'Darwin'
        if 'RELEASE_ARM' in os.uname()[3]:
            architecture = 'ios'
        else:
            # Crypto can be compiled as universal library with multiple
            # architectures for osx
            architecture = 'osx'
    elif xbmc.getCondVisibility( "system.platform.ios" ):
        # Need to check system.platform.osx for eden
        # Changed to system.platform.ios for frodo
        SYSTEM_PLATFORM = 'Darwin'
        architecture = 'ios'

CRYPTO_PATH = os.path.join( __addonDir__, "resources", "platform_libraries", SYSTEM_PLATFORM, architecture)
sys.path.append(CRYPTO_PATH)
if PYDES_ENABLED:
    from resources.lib.pyDes import *
else:
    # Try to import Crypto lib - fall back to pyDes if autoplatform
    try:
        from Crypto.Cipher import DES
    except:
        print "Impossible to import Crypto.Cipher from %s" % CRYPTO_PATH
        if autoplatform:
            print "Falling back to pyDes"
            PYDES_ENABLED = True
            from resources.lib.pyDes import *
        else:
            dialog = xbmcgui.Dialog()
            dialog.ok(__language__(30201), __language__(30202), __language__(30203), __language__(30204))
            exit()


def verifrep( folder ):
    """
        Source MyCine (thanks!)
        Check a folder exists and make it if necessary
    """
    try:
        #print("verifrep check if directory: " + folder + " exists")
        if not os.path.exists( folder ):
            print( "verifrep Impossible to find the directory - trying to create the directory: " + folder )
            os.makedirs( folder )
    except Exception, e:
        print( "Exception while creating folder " + folder )
        print( str( e ) )


class Catalog:
    def __init__(self, catalog):
        self.catalog = catalog
        self.timestamp = datetime.datetime.now()
    def is_old(self):
        delta = datetime.datetime.now() - self.timestamp
        limit = int(__settings__.getSetting('catalog_refresh_rate'))
        print "delta: " + str(delta.seconds) + " / " + str(limit)
        if delta.seconds > limit:
            return True
        else:
            return False
class M6Replay:
    """
    main plugin class
    """
    debug_mode = False # Debug mode
    
    def __init__( self, *args, **kwargs ):
        print "==============================="
        print "  M6 Replay - Version: %s"%__version__
        print "==============================="
        print
        self.set_debug_mode()
        ok = False
        if self.debug_mode:
            print "Python version:"
            print sys.version_info
            print "URL du plugin:"
            print sys.argv[ 0 ] + sys.argv[ 2 ]
            print "ROOTDIR: %s"%ROOTDIR
            print "ADDON_DATA: %s"%ADDON_DATA
            print "CACHEDIR: %s"%CACHEDIR
            print "SYSTEM_PLATFORM: %s"%SYSTEM_PLATFORM
            print "CRYPTO_PATH: %s"%CRYPTO_PATH
            print "PYDES_ENABLED: %s"%PYDES_ENABLED
        
        # Check if directories in user data exist
        for i in range( len( dirCheckList ) ):
            verifrep( dirCheckList[i] ) 
        
        #xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category= __language__ ( 30000 )) # Catégories
        #xbmcplugin.setContent(int(sys.argv[1]), "Video")
        
        if ( not sys.argv[ 2 ] ):
            # Main Categories
            try:
                dico=self.get_categorie("http://www.m6replay.fr/catalogue/catalogueWeb3.xml")
                for cat in range(len(dico['categorie'])):
                    #infoLabels={ "Title": dico['categorie'][cat],
                    #             "count": cat}
                    ok = self.add_menu_item(dico['categorie'][cat], "display_pos="+str(dico['pos'][cat]), len(dico['categorie']), dico['image'][cat], True)               
                    # if user cancels, call raise to exit loop
                    if ( not ok ): raise
            except Exception, e:
                # oops, notify user what error occurred
                print_exc()
                
            # if successful (or not the play video case) and user did not cancel, add all the required sort methods and set plugin category
            if ( ok ):
                xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_UNSORTED)
                xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_LABEL )
       
        elif ( "display_pos=" in sys.argv[ 2 ] ):
            # Sub Categories
            try:
                dico=self.get_sub_categorie("http://www.m6replay.fr/catalogue/catalogueWeb3.xml",int(sys.argv[ 2 ].split("=")[1]))
                for cat in range(len(dico['categorie'])):
                    #infoLabels={ "Title": dico['categorie'][cat],
                    #             "count": cat}
                    ok = self.add_menu_item(dico['categorie'][cat], "display_produit="+str(dico['pos'][cat]), len(dico['categorie']), dico['image'][cat], True)
                    # if user cancels, call raise to exit loop
                    if ( not ok ): raise
            except Exception, e:
                # oops, notify user what error occurred
                print_exc()
                
            # if successful (or not the play video case) and user did not cancel, add all the required sort methods and set plugin category
            if ( ok ):
                xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_UNSORTED)
                xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_LABEL )
        
        elif ( "display_produit=" in sys.argv[ 2 ] ):
            # Produit
            try:
                dico=self.get_produit("http://www.m6replay.fr/catalogue/catalogueWeb3.xml",int(sys.argv[ 2 ].split("=")[1]))
                for produit in range(len(dico['nom'])):
                    infoLabels={ "Title": dico['nom'][produit],#+ " " + video["publication_date"],
                                 #"Rating":5,
                                 "Date": extractDateString( dico['date'][produit] ), # Format: u'17-12-2010'
                                 "Aired": extractDateString( dico['date'][produit] ), # Format: u'17-12-2010'
                                 "Duration": convertMin2Hour(dico['duree'][produit]),
                                 "Plot": bold_text( __language__ ( 30001 ) ) + add_pretty_color( self.convert_time_to_string( dico['date'][produit] ), color='FFFFCC00' ) + "[CR]" 
                                       + bold_text( __language__ ( 30002 ) ) + add_pretty_color( self.convert_time_to_string( dico['date_fin'][produit] ), color='FFFF0000' ) + "[CR][CR]" 
                                       + dico['description'][produit]}
                    #{ "TVShowTitle": "CNN Video", "Season": 1, "Episode": 1, "Title": video.title, "Genre": self.args.title, "Duration": video.duration, "Date": video.date, "Premiered": video.date }
                    #{ "Title": pname, "Duration": duration, "Label": name, "SortLetter":sort_letter, "date": date, "Year": year, "Plot":plot, "Rating":rating, "Path":path, "Director":director, "Genre":genre, "Tagline":tagline, "Writer":writer, "Studio": str(id)  }
                    cm = [(__language__(30060), 'XBMC.RunPlugin(%s?download=%s)' % (sys.argv[0], dico['path'][produit]))]
                    ok = self.add_menu_item(dico['nom'][produit], "stream="+dico['path'][produit], len(dico['nom']), dico['image'][produit], False, itemInfoLabels=infoLabels, contextmenu=cm)
                    # if user cancels, call raise to exit loop
                    if ( not ok ): raise
            except Exception, e:
                # oops, notify user what error occurred
                print_exc()
                
            # if successful (or not the play video case) and user did not cancel, add all the required sort methods and set plugin category
            if ( ok ):
                xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_UNSORTED)
                xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_LABEL )
                xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_DATE )
                xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_VIDEO_RUNTIME )
                #xbmcplugin.setContent(int(sys.argv[1]), "movies")
                xbmcplugin.setContent(int(sys.argv[1]), "episodes")
                
                
        elif ( "stream=" in sys.argv[ 2 ] ): 
            # Resolve URL in order to play a video
            rtmp_url, filename = self.get_rtmp_args()
            url = rtmp_url + " timeout=10"
            if rtmp_url =="":
                url = playpath

            # Play  video
            item = xbmcgui.ListItem(path=url)
        
            if self.debug_mode:
                print "Lecture de la video: %s"%url
            xbmcplugin.setResolvedUrl(handle=int(sys.argv[1]), succeeded=True, listitem=item)


        elif ( "download=" in sys.argv[ 2 ] ):
            rtmpdump = __settings__.getSetting('rtmpdump')
            if not rtmpdump:
                # Hope that rtmpdump is in the path
                rtmpdump = 'rtmpdump'
            download_path = self.get_download_path()
            rtmp_url, filename = self.get_rtmp_args()
            if self.check_path(download_path, filename):
                full_filename = os.path.join(download_path, filename)
                cmd = '%(rtmpdump)s -r "%(rtmp_url)s" -m 10 -o %(full_filename)s' % locals()
                print cmd
                self.showNotification(__language__(30205), filename)
                try:
                    retcode = os.system(cmd)
                except OSError, e:
                    print_exc()
                    self.showNotification(__language__(30207), e.__str__())
                else:
                    # We should check the return code, but it doesn't work in XBMC
                    # because SIGCHLD is set to SIG_IGN
                    print "Download complete"
                    self.showNotification(__language__(30206), filename)


        # set our plugin category
        xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category=__language__ ( 30000 ) )
        
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

    def showNotification(self, header, message):
        xbmc.executebuiltin('XBMC.Notification("%s", "%s")' % (header.encode( "utf-8", "ignore" ), message.encode( "utf-8", "ignore" )))

    def encode_rtmp(self, app, playpath, timestamp):
        """Return the encoded token url (with hash)"""
        delay = 86400
        secret_key = 'vw8kuo85j2xMc'
        url = '%s?s=%d&e=%d' % (playpath, timestamp, timestamp + delay)
        url_hash = hashlib.md5('/'.join([secret_key, app, url[4:]])).hexdigest()
        token_url = url + '&h=' + url_hash
        return token_url

    def get_rtmp_args(self):
        "Return rtmp args as a tuple (rtmp_url, filename)"
        server_id = int( __settings__.getSetting( 'server' ) )
        if server_id > len(srv_list) - 1:
            print "Server id %d out of range. Server 0 forced." % server_id
            server_id = 0
        rtmp = srv_list[server_id]['rtmp']
        app = srv_list[server_id]['app']
        playpath = re.sub( "[ ]", "%20", sys.argv[ 2 ].split("=")[1] )
        filename =  os.path.basename(playpath)
        token_url = self.encode_rtmp(app, playpath, int(time.time()))
        rtmp_url = '/'.join([rtmp, app, token_url])
        return (rtmp_url, filename)

    def check_path(self, path, filename):
        if os.path.isdir(path):
            if os.path.isfile(os.path.join(path, filename)):
                if os.path.getsize(os.path.join(path, filename))>0:
                    self.showNotification(__language__(30208), '%s %s' % (filename, __language__(30209)))
                else:
                    return True #overwrite empty files, #skip others.
            else:
                return True
        return False

    def get_download_path(self):
        download_mode = __settings__.getSetting('downloadMode')
        if download_mode == 'true':
            download_path = xbmcgui.Dialog().browse(3, __language__(30060), 'video')
        else:
            download_path = __settings__.getSetting('downloadPath')
        return download_path
           
    def set_debug_mode(self):
        debug =__settings__.getSetting('debug')
        if debug == 'true':
            self.debug_mode = True
        else:
            self.debug_mode = False
        print "M6 Replay: debug Mode:"
        print self.debug_mode
        
    def m6_decrypt(self, url):
        key = 'RWxGc2cuT3Q='
        no_catalog = False
        if os.path.isfile(os.path.join( CACHEDIR, "current_catalog")):
            f = open(os.path.join( CACHEDIR, "current_catalog"), 'r')
            try:
                #PB TODO
                catalog = pickle.load(f)
            except:
                no_catalog = True
            f.close()
        else:
            no_catalog = True

        if no_catalog or catalog.is_old():
            data = urllib.urlopen( url ).read()
            if PYDES_ENABLED:
                self.showNotification(__language__(30210), __language__(30211))
                file_buffer = base64.b64decode(data)
                passw = base64.b64decode(key)
                cipher = des(passw)
                catalog_xml = cipher.decrypt(file_buffer)
            else:
                cipher = DES.new( base64.b64decode(key), DES.MODE_ECB )
                catalog_xml = cipher.decrypt( base64.standard_b64decode(data) )
            catalog_xml = string.rstrip( string.split( catalog_xml, '</template_exchange_WEB>' )[0] ) + '</template_exchange_WEB>'
            catalog = Catalog( catalog_xml )
            f = open(os.path.join( CACHEDIR, "current_catalog"), 'w')
            pickle.dump(catalog, f)
            #PB TODO
            f.close()
            if self.debug_mode:
                open(os.path.join(CACHEDIR,'catalog_m6.xml').encode('utf8'),"w").write(catalog_xml)
    
        return catalog.catalog     
    
    def get_categorie(self, xml_url):
        dico = {}
        categorie = []
        image = []
        pos= []
        dico['categorie']=categorie
        dico['image']=image
        dico['pos']=pos    
        cleartext=self.m6_decrypt(xml_url)
        xml_end = cleartext.rfind('>') + 1
        cleartext=cleartext[:xml_end]
        xmlrss=parseString(cleartext)
        
        for item in range(len(xmlrss.getElementsByTagName("template_exchange_WEB")[0].getElementsByTagName("categorie"))):
            if not xmlrss.getElementsByTagName("template_exchange_WEB")[0].getElementsByTagName("categorie")[item].hasAttribute("tag_dart"):
                categorie.append(xmlrss.getElementsByTagName("template_exchange_WEB")[0].getElementsByTagName("categorie")[item].getElementsByTagName("nom")[0].childNodes[0].data)
                image.append("http://images.m6replay.fr"+xmlrss.getElementsByTagName("template_exchange_WEB")[0].getElementsByTagName("categorie")[item].getAttribute("big_img_url"))
                pos.append(item)
        if self.debug_mode:
            print "Categories:"
            print dico    
        return dico
    
    def get_sub_categorie(self, xml_url,parent_pos):
        dico = {}
        categorie = []
        image = []
        pos= []
        dico['categorie']=categorie
        dico['image']=image
        dico['pos']=pos    
        cleartext=self.m6_decrypt(xml_url)
        xml_end = cleartext.rfind('>') + 1
        cleartext=cleartext[:xml_end]
        xmlrss=parseString(cleartext)
        
        for item in range(parent_pos+1,len(xmlrss.getElementsByTagName("template_exchange_WEB")[0].getElementsByTagName("categorie"))):
            if xmlrss.getElementsByTagName("template_exchange_WEB")[0].getElementsByTagName("categorie")[item].hasAttribute("tag_dart"):
                categorie.append(xmlrss.getElementsByTagName("template_exchange_WEB")[0].getElementsByTagName("categorie")[item].getElementsByTagName("nom")[0].childNodes[0].data)
                image.append("http://images.m6replay.fr"+xmlrss.getElementsByTagName("template_exchange_WEB")[0].getElementsByTagName("categorie")[item].getAttribute("big_img_url"))
                pos.append(item)
            else:
                break
        if self.debug_mode:
            print "Sous Categories:"
            print dico    
        return dico
    
    def get_produit(self, xml_url,parent_pos):
        dico = {}
        path = []
        image = []
        nom = []
        description = []
        date = []
        date_fin = []
        description = []
        duree = []
        dico['nom']=nom
        dico['path']=path
        dico['image']=image    
        dico['description']=description    
        dico['date']=date    
        dico['date_fin']=date_fin
        dico['duree']= duree
        cleartext=self.m6_decrypt(xml_url)
        xml_end = cleartext.rfind('>') + 1
        cleartext=cleartext[:xml_end]
        xmlrss=parseString(cleartext)
        
        for item in range(len(xmlrss.getElementsByTagName("template_exchange_WEB")[0].getElementsByTagName("categorie")[parent_pos].getElementsByTagName("produit"))):
           
           medias = xmlrss.getElementsByTagName("template_exchange_WEB")[0].getElementsByTagName("categorie")[parent_pos].getElementsByTagName("produit")[item].getElementsByTagName("fichemedia")
           
           # Parcours les "fiche_media" pour en extraire le lien vidéo. Normalement il n'y en a qu'une, sauf pour les séries VOSTFR/VF
           for media in medias:
               if( len(medias) == 1 ):
                   nom_media = ''
               else:
                   nom_media = " ["+media.getAttribute("langue")+"]"
               nom.append(xmlrss.getElementsByTagName("template_exchange_WEB")[0].getElementsByTagName("categorie")[parent_pos].getElementsByTagName("produit")[item].getElementsByTagName("nom")[0].childNodes[0].data + nom_media)        
               path.append(media.getAttribute("video_url"))
               duree.append(media.getAttribute("duree"))
               image.append("http://images.m6replay.fr"+xmlrss.getElementsByTagName("template_exchange_WEB")[0].getElementsByTagName("categorie")[parent_pos].getElementsByTagName("produit")[item].getAttribute("big_img_url"))
               description.append(xmlrss.getElementsByTagName("template_exchange_WEB")[0].getElementsByTagName("categorie")[parent_pos].getElementsByTagName("produit")[item].getElementsByTagName("resume")[0].childNodes[0].data)
               date.append(xmlrss.getElementsByTagName("template_exchange_WEB")[0].getElementsByTagName("categorie")[parent_pos].getElementsByTagName("produit")[item].getElementsByTagName("diffusion")[0].getAttribute("date"))
               date_fin.append(xmlrss.getElementsByTagName("template_exchange_WEB")[0].getElementsByTagName("categorie")[parent_pos].getElementsByTagName("produit")[item].getElementsByTagName("diffusion")[0].getAttribute("dateFin"))
        if self.debug_mode:
            print "Produits:"
            print dico    
        return dico
    
    def add_menu_item(self, title,action,size,thumb,folder, itemInfoLabels=None, contextmenu=None):
        if self.debug_mode:
            print "add_menu_item:"
            print "title = %s"%repr(title)
            print "thumb= %s"%(thumb)
            print "action= %s"%(action)
            print "itemInfoLabels:"
            print itemInfoLabels
            print
        item=xbmcgui.ListItem(title,thumbnailImage=thumb)
        if contextmenu is None:
            contextmenu = [ (title,"XBMC.RunPlugin("+sys.argv[ 0 ]+"?"+action+")")]
        url=sys.argv[ 0 ]+"?"+action
        
        # Clean the Thumb (cache thumbnail name being based on plugin URL)
        self.clean_thumbnail(url)
        
        item.addContextMenuItems(contextmenu, replaceItems=True)
        if itemInfoLabels:
            iLabels = itemInfoLabels
        else:
            iLabels = { "Title": title }
        if not folder:
            item.setInfo( type="Video", infoLabels=iLabels)
            item.setProperty('IsPlayable', 'true')
            
        ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=item,isFolder=folder,totalItems=size)
        return ok

    def convert_time_to_string(self, xmlTime):
        """
        Convert time retrieved from XMl to a date in French such as 'samedi 2 janvier 2010'
        """
        time = convertStrTime2Time(xmlTime)
        return convertTime2FrenchString(time)

    def clean_thumbnail(self, video_url):
        """
        Clean thumb
        This is done because XBMC does not use the right thumb in the case of sub categories
        The reason is the Cache Thumb Name is based on a URL such as 'plugin://plugin.video.M6Replay/?display_pos=0'
        Which can reprensent different category (for the same URL) depending on the change in the XML
        """
        try:
            filename = xbmc.getCacheThumbName( video_url )
            filepath = xbmc.translatePath( os.path.join( THUMB_CACHE_PATH, filename[ 0 ], filename ) )
            if os.path.isfile( filepath ):
                os.remove(filepath)
                if self.debug_mode:
                    print "Deleted %s thumb matching to %s video"%(filepath, video_url)
            elif self.debug_mode:
                print "No thumb found %s thumb matching to %s video"%(filepath, video_url)
                
            return True
        except:
            print "Error: clean_thumbnail()"
            print_exc()
            return False
#######################################################################################################################    
# BEGIN !
#######################################################################################################################

if ( __name__ == "__main__" ):
    try:
        M6Replay()
    except:
        print_exc()
    
