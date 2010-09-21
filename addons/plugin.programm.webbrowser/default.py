# -*- coding: utf-8 -*-
"""
WebBrowser plugin
Auteur : CinPoU
"""

import sys,os,re, shutil
import urllib, urllib2
import xbmcplugin,xbmcgui,xbmc
import xml.dom.minidom
import unicodedata


import random, string

#Browser - by CinPoU



# INITIALISATION CHEMIN RACINE
ROOTDIR = os.getcwd().replace( ";", "" )

# Shared resources
BASE_RESOURCE_PATH = os.path.join( ROOTDIR, "resources" )
# append the proper platforms folder to our path, xbox is the same as win32
env = ( os.environ.get( "OS", "win32" ), "win32", )[ os.environ.get( "OS", "win32" ) == "xbox" ]
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "platform_libraries", env ) )
# append the proper libs folder to our path
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "libs" ) )
# append the proper etree folder to our path
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "libs", "elementtree" ) )

#modules custom
from specialpath import *
from httpsConnect import *
from elementtree import ElementTree



try:
    from xbmcaddon import Addon

    # source path for launchers data
    PLUGIN_DATA_PATH = xbmc.translatePath( os.path.join( "special://profile/addon_data", "plugin.programm.webbrowser") )

    __settings__ = Addon( id="plugin.programm.webbrowser" )
    __language__ = __settings__.getLocalizedString
    print "Mode AddOn ON"


except : 
    # source path for launchers data
    PLUGIN_DATA_PATH = xbmc.translatePath( os.path.join( "special://profile/plugin_data", "programs", sys.modules[ "__main__" ].__plugin__) )

    __settings__ = xbmcplugin
    __language__ = xbmc.getLocalizedString
    print "Mode plugin ON"


#Initialisation des chemins

xmlUserDir = os.path.join( PLUGIN_DATA_PATH, "xml" )
if not os.path.isdir(xmlUserDir) :
    os.mkdir(xmlUserDir)
imgUserDir = os.path.join( PLUGIN_DATA_PATH, "img" )
if not os.path.isdir(imgUserDir) :
    os.mkdir(imgUserDir)
cookieUserDir = os.path.join( PLUGIN_DATA_PATH, "cookie" )
if not os.path.isdir(cookieUserDir) :
    os.mkdir(cookieUserDir)
imgDir = os.path.join(BASE_RESOURCE_PATH,"images")
defaultIcon = os.path.join(imgDir,"Default.png")
defaultGoogleIcon = os.path.join(imgDir,"DefaultGoogle.png")
defaultAddIcon = os.path.join(imgDir,"DefaultAdd.png")
defaultLaunchIcon = os.path.join(imgDir,"launch.png")
defaultFolderIcon = os.path.join(imgDir,"DefaultFolder.png")
defaultGoogleFolderIcon = os.path.join(imgDir,"DefaultGoogleFolder.png")


dialog = xbmcgui.Dialog()


#DEF      
#Clavier                
def show_keyboard (textDefault, textHead, textHide=False) :
    """Show the keyboard's dialog"""
    keyboard = xbmc.Keyboard(textDefault, textHead)
    inputText = ""
    if textHide == True :
        keyboard.setHiddenInput(True)
    keyboard.doModal()
    if (keyboard.isConfirmed()):
        inputText = keyboard.getText()         
        dialogInfo = xbmcgui.Dialog()
    del keyboard
    return inputText


def cleanString(s):
  """Removes all accents from the string"""
  if isinstance(s,str):
      s = unicode(s,"utf8","replace")
      s = unicodedata.normalize('NFD',s)
      return s.encode('ascii','ignore')


#Lance le navigateur
def launchBrowser(url) : 

    if (os.environ.get( "OS", "xbox" ) == "xbox"):
        xbmc.executebuiltin('XBMC.Runxbe(' + cmd + ' '+ __settings__.getSetting('arguments') + ' '+ url + ')')
    else:
        if (sys.platform == 'win32'):
            xbmc.executebuiltin("%s(\"\\\"%s\\\" %s %s\")" % ("System.ExecWait", cmd, __settings__.getSetting('arguments') , url))
        elif (sys.platform.startswith('linux')):
            url = '"'+url+'"'
            #os.system("%s %s" % ("/usr/bin/vlc", url))
            os.system("%s %s %s" % (cmd,__settings__.getSetting('arguments'), url))
        else:
            pass;
            # unsupported platform

    
def writeXml(xmlPath) :
    if not os.path.isfile( xmlPath ):
        xmlSrc = os.path.join( BASE_RESOURCE_PATH, "modeles" , "default.xml" )
        try :
            shutil.copy2(xmlSrc,xmlPath)
        except : "Unable to write the xml file"
        
                    
#Lister les Favoris Google
def getGoogleXml() :
    #Create the Xml
    xmlPath = os.path.join( xmlUserDir, "google.xml" )
    writeXml(xmlPath)















    #Adresse du formulaire de connexion
    the_url = 'https://www.google.com/accounts/Login?hl=fr&continue=https://www.google.com/bookmarks/?output=rss&num=1000'
    
    
    #Initialisation de HttpsConnect
    
    cookieFile = os.path.join( cookieUserDir, 'cookies.lwp' )
    print cookieFile
    test = HttpsConnect(cookieFile,userAgent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)')
    print test
    the_page = test.httpsRequest(the_url,dataRequest={},headerRequest={})[0]

    
    
    #Traitement du formulaire
    dshPattern = re.compile(r'<input type="hidden" name="dsh" id="dsh"\s           value="(.+?)" />')
    dshInput = dshPattern.search(the_page).groups()
    
    galxPattern = re.compile(r'<input type="hidden"\s             name="GALX"\s             value="(.+?)" />')
    galxInput = galxPattern.search(the_page).groups()
    
    print galxInput, dshInput
    
    
    
    
    #Information de connexion
    url = 'https://www.google.com/accounts/LoginAuth'
    values = {'continue' : 'https://www.google.com/bookmarks/?output=rss',
              'dsh' : dshInput[0],
              'GALX' : galxInput[0],
              'Email' : __settings__.getSetting('login'),
              'Passwd' : __settings__.getSetting('password'),
              'PersistentCookie' : "yes",
              'rmShown' : "1",
              'signIn' : "Connexion",
              'asts' : '' }
    
    
    
    #Identification
    test.httpsRequest(url,dataRequest=values,headerRequest={})
    
    #Requêtes
    readXml  = test.httpsRequest("https://www.google.com/bookmarks/?output=rss")[0]
        
        
    xmlFile=open(xmlPath,"wb") #on créé un fichier en écriture mode binaire
    xmlFile.write(readXml) #on ecrit ce qu'on lit de l'image
    xmlFile.close()#on ferme le fichier image




      
      
def returnGoogle() :
    xmlPath = os.path.join( xmlUserDir, "google.xml" )
    xmlFile=open(xmlPath,"r")
    txt = xmlFile.read()
    xmlFile.close()
    
    tree = ElementTree.fromstring(txt)
    channel = tree.find("channel")
    bookmarks = channel.findall("item")
    googleDico = {}
    googleMain = []
    for bookmark in bookmarks:
        title = bookmark.findtext("title")
        url = bookmark.findtext("link")
        guid = bookmark.findtext("{http://www.google.com/history/}bkmk_id")
        print guid
        tags = bookmark.findall("{http://www.google.com/history/}bkmk_label")
        googleItem = {"title" : title , "url" : url , "guid" : guid}
        if len(tags) == 0 :
          googleMain.append(googleItem)
        else :
          for tag in tags :
            if googleDico.has_key(tag.text) :
                googleItems = googleDico[tag.text]
                googleItems.append(googleItem)
            else :
                googleItems = []
                googleItems.append(googleItem)
                
            googleDico[tag.text] = googleItems
    
    print googleDico
    print googleMain
    return googleDico, googleMain


#Récupère les paramètres            
def get_params():
        param=[]
        paramstring=sys.argv[2]
        if len(paramstring)>=2:
                params=sys.argv[2]
                cleanedparams=params.replace('?','')
                if (params[len(params)-1]=='/'):
                        params=params[0:len(params)-2]
                pairsofparams=cleanedparams.split('&')
                param={}
                for i in range(len(pairsofparams)):
                        splitparams={}
                        splitparams=pairsofparams[i].split('=')
                        if (len(splitparams))==2:
                                param[splitparams[0]]=splitparams[1]
        return param

#Ouvrir une URL
def launchUrl():
        u=sys.argv[0]+"?mode=3"
        ok=True
        liz=xbmcgui.ListItem(__language__(11), iconImage=defaultLaunchIcon, thumbnailImage=defaultLaunchIcon)
        liz.setInfo( type="files", infoLabels={ "Title": __language__(11) } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz)
        return ok
        
#Ajoute un lien
def addLink(name,url,iconimage, imgPath , readonly = False):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode=2&name="+urllib.quote_plus(name)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
        liz.setInfo( type="files", infoLabels={ "Title": name } )
        
        c_items = []
        # ajout d'un bouton dans le contextmenu pour rafraichir l'image
        refreshLabelButton = __language__(201)
        refreshActionButton = 'XBMC.RunPlugin(%s?mode=7&name=%s&url=%s)' % ( sys.argv[ 0 ], urllib.quote_plus( imgPath ), urllib.quote_plus( url ), )
        c_items.append(( refreshLabelButton, refreshActionButton ))
        if readonly == False :
            deleteLabelButton = __language__(202)
            deleteActionButton = 'XBMC.RunPlugin(%s?mode=8&name=%s&url=%s)' % ( sys.argv[ 0 ], urllib.quote_plus( name ), urllib.quote_plus( url ), )
            c_items.append(( deleteLabelButton, deleteActionButton ))
        else :
            addXmlLabelButton = __language__(203)
            addXmlActionButton = 'XBMC.RunPlugin(%s?mode=6&name=%s&url=%s)' % ( sys.argv[ 0 ], urllib.quote_plus( name ), urllib.quote_plus( url ), )
            c_items.append(( addXmlLabelButton, addXmlActionButton ))
        # replaceItems=True, seulement mon bouton va etre visible dans le contextmenu 
        # si on veut tous les boutons plus le notre on mets rien listitem.addContextMenuItems( c_items ), car False est par default
        liz.addContextMenuItems( c_items, replaceItems=True )
        
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz)
        return ok

#Ajoute un dossier
def addDir(name,url,mode,iconimage):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        ok=True
        iconimage = os.path.join(imgDir,iconimage)
        liz=xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)

        
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok


 
 



def randomString(length=None):
    # on définit les caractères acceptés
    chars = string.letters + string.digits
    # longueur de la chaine, paramètre défini ou entre 6  et 24
    length = length or random.randint(6,24)
    # une chaine concaténée a partir d'un choix aléatoire d'éléments
    return ''.join(random.sample(chars, length)) 
 
def randomFile(dirUrl, fileExt) :

    fileName = randomString()
    fileUrl = os.path.join(dirUrl, fileName)
    return fileName


def getThumb(PageWebURL,name) :
    # état des variables initiales
    ThumbSize = "640x480" #taille en pixel, pas plus de 1024
    
    urllib.urlcleanup()
    
    ThumbUrl = "http://www.apercite.fr/api/apercite/%s/non/non/%s" % (ThumbSize , PageWebURL)
    #Ecriture de l'image
    #name = "%s.jpg" % (name)
    imgPath = os.path.join(imgUserDir, name)
    f=open(imgPath,"wb") #on créé un fichier en écriture mode binaire
    f.write(urllib.urlopen(ThumbUrl).read()) #on ecrit ce qu'on lit de l'image
    f.close()#on ferme le fichier image  
    
    return imgPath      
    
def checkThumb(PageWebURL,name=None) :
    if name == None :
        name = randomFile(imgUserDir)
    name = "%s.jpg" % (name)
    imgPath = os.path.join(imgUserDir, name)
    if not os.path.isfile(imgPath) :
        getThumb(PageWebURL,name)
    return name
        


#Ajouter un favoris
def addBookmark(discuss = True, titleStr = "", urlStr = ""):
    xmlPath = os.path.join(xmlUserDir , "default.xml")
    if discuss == True :
        urlStr = show_keyboard ("http://", __language__(101))
        titleStr = show_keyboard ("", __language__(102))
    imgPath = cleanString(titleStr)
    titleStr = "%s" % titleStr.decode("utf-8")
    #print titleStr, imgPath
    if urlStr != "" and titleStr != "" :
    
        #Création de la miniature :
        getThumb(urlStr,imgPath)
    
        # Open the document
        doc=xml.dom.minidom.parse(xmlPath)
        main=doc.childNodes[0]
        
        # Create a main <fav> element
        fav = doc.createElement("fav")
        favbal=main.appendChild(fav)
        
        
        # Create the fav <title> element
        title = doc.createElement("title")
        titlebal=favbal.appendChild(title)
        
        # Give the <title> element some text
        titletext = doc.createTextNode(titleStr)
        titlebal.appendChild(titletext)
        
        
        # Create the fav <link> element
        link = doc.createElement("link")
        linkbal=favbal.appendChild(link)
        
        # Give the <title> element some text
        linktext = doc.createTextNode(urlStr)
        linkbal.appendChild(linktext)
        
        
        # Create the fav <image> element
        image = doc.createElement("image")
        imagebal=favbal.appendChild(image)
        
        # Give the <image> element some text
        imagelink = os.path.join
        imagetext = doc.createTextNode("%s" % imgPath)
        imagebal.appendChild(imagetext)
        
        
        # Print our newly created XML
        #print doc.toprettyxml(encoding="UTF-8")
    
        outputfile = open(xmlPath, 'wb')
        outputfile.write(doc.toxml(encoding="UTF-8"))
        outputfile.close()
        
        dialog.ok(__language__(105) , __language__(106))
    else :
        dialog.ok(__language__(103) , __language__(104))
 
 
def removeXml(nameBookmark, urlBookmark) :
    xmlPath = os.path.join(xmlUserDir , "default.xml")
    # Open the document
    doc=xml.dom.minidom.parse(xmlPath)
    node = doc.firstChild
    
    for e in node.childNodes :
    
        if e.nodeType == e.ELEMENT_NODE and e.localName == "fav" :
        
            foundUrl = False
            foundName = False
        
            for c in e.childNodes :
            
                if c.nodeType == c.ELEMENT_NODE and c.localName == "title" :
                
                    if c.firstChild.nodeValue.encode("utf-8") == nameBookmark :
                        
                        foundName = True
                        print "foundName"
            
                if c.nodeType == c.ELEMENT_NODE and c.localName == "link" :
                    print "ok"  
                    if c.firstChild.nodeValue.encode("utf-8") == urlBookmark :
                        
                        foundUrl = True
                        print "foundUrl"  
                            
            if foundUrl == True and foundName == True :
            
                node.removeChild(e)

                print "removeChild"
    
                outputfile = open(xmlPath, 'wb')
                outputfile.write(doc.toxml(encoding="UTF-8"))
                outputfile.close()
                
                dialog.ok(__language__(107) , __language__(106))
                break
                            
            
 
         
           
def getXmlFav(xmlName) :
    #Path of the xml file
    xmlPath = os.path.join( xmlUserDir, xmlName )
    #Parse xml file
    document = xml.dom.minidom.parse(xmlPath)
    
    for item in document.getElementsByTagName('fav'):
      name = item.getElementsByTagName('title')[0].firstChild.data
      url = item.getElementsByTagName('link')[0].firstChild.data
      imgPath = item.getElementsByTagName('image')[0].firstChild.data
      thumbnail = "%s.jpg" % imgPath
      thumbnail = os.path.join(imgUserDir, thumbnail)
      addLink(name.encode("utf-8"),url,thumbnail,imgPath)


#INIT
#Init Parameter       
if __settings__.getSetting('cmdline') == "" and __settings__.getSetting('path') == "":
    pass #__settings__.openSettings(url=sys.argv[0])
elif __settings__.getSetting('cmdline') != "" :
    cmd = __settings__.getSetting('cmdline')
else:
    cmd = __settings__.getSetting('path')
#Variable           
params = get_params()
url = None
name = None
mode = None
#Language
TextLanguage = __language__

#Recup Parameter 
try:
        url=urllib.unquote_plus(params["url"])
except:
        pass
try:
        name=urllib.unquote_plus(params["name"])
except:
        pass
try:
        mode=int(params["mode"])
except:
        pass
        
print "Mode: "+str(mode)
print "URL: "+str(url)
print "Name: "+str(name)

if mode == None: 

    if __settings__.getSetting('login') != "" and __settings__.getSetting('password') != "":
        getGoogleXml()
        
                
if mode == None or mode == 0 or mode == 4 :   

    if __settings__.getSetting('login') != "" and __settings__.getSetting('password') != "":     
        googleTags, googleMainTags = returnGoogle()             
                

#LAUNCH LIST
#Default
if mode == None or mode == 0:
        print "CATEGORY INDEX : "
        launchUrl()
        
        #XML BOOKMARKS
        writeXml(os.path.join(xmlUserDir, "default.xml"))
        getXmlFav("default.xml")
        if __settings__.getSetting('login') != "" and __settings__.getSetting('password') != "":   
            #GOOGLE BOOKMARKS
            for googleBookmark in googleMainTags :
                print googleBookmark
                imgPath = checkThumb(googleBookmark["url"].encode("utf-8"),name=googleBookmark["guid"])
                thumbnail = os.path.join(imgUserDir, imgPath)
                addLink(googleBookmark["title"].encode("utf-8"),googleBookmark["url"].encode("utf-8"),thumbnail, imgPath, readonly = True)
            for googleTag in googleTags.keys() :
                addDir(googleTag.encode("utf-8"),"none",4,defaultGoogleFolderIcon)
                
        
        u=sys.argv[0]+"?mode=5"
        ok=True
        liz=xbmcgui.ListItem(__language__(12), iconImage=defaultAddIcon, thumbnailImage=defaultAddIcon)
        liz.setInfo( type="files", infoLabels={ "Title": __language__(12) } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz)

#Lister les favoris        
elif mode == 1:
        print "GET INDEX OF PAGE : " + url

#Lancer un favoris
elif mode == 2:
        print "LAUNCH URL: " + url
        launchBrowser(url)

#Ouvrir une URL        
elif mode == 3:
        print "ASK URL: "
        url = show_keyboard ("http://", __language__(101))
        launchBrowser(url)

#Afficher les favoris du tag google        
elif mode == 4:
        print "SHOW GOOGLE TAGS BOOKMARKS: "
        print googleTags
        for googleBookmark in googleTags[name.decode("utf-8")] :
            imgPath = checkThumb(googleBookmark["url"].encode("utf-8"),name=googleBookmark["guid"])
            thumbnail = os.path.join(imgUserDir, imgPath)
            addLink(googleBookmark["title"].encode("utf-8"),googleBookmark["url"].encode("utf-8"),thumbnail, imgPath ,readonly = True)

#Ajouter un favoris
elif mode == 5:
        print "ADD A BOOKMARK: "
        addBookmark()
        
elif mode == 6 :
    print "ADD A GOOGLE BOOKMARK: "
    addBookmark(discuss = False, titleStr = name, urlStr = url)
        
elif mode == 7 :
    print "REFRESH A THUMB: "
    getThumb(url,name)
    dialog.ok(__language__(108) , __language__(106))
        
elif mode == 8 :
    print "DELETE A BOOKMARK: "
    removeXml(name, url)
    xbmc.executebuiltin("Container.Refresh")

xbmcplugin.endOfDirectory(int(sys.argv[1]))























 
