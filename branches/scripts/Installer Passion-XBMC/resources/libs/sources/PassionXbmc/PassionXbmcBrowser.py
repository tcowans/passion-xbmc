"""
PassionXbmcBrowser: this module allows browsing of server content on the web server of Passion-XBMC.org using DB Crossway API
NOTE: a lot of is code has been done as temporary patch in order to solve issue on the server side
"""

# Modules general
import os
import sys
import urllib
from threading import Thread
from traceback import print_exc
from  time import strftime, localtime
import re

import simplejson as json

# Modules custom 
import Item
from utilities import *
#from CONSTANTS import *
import PassionXbmcItemInstaller 
from pil_util import makeThumbnails
from Browser import Browser, History, ImageQueueElement


#FONCTION POUR RECUPERER LES LABELS DE LA LANGUE.
_ = sys.modules[ "__main__" ].__language__
LANGUAGE_IS_FRENCH = sys.modules[ "__main__" ].LANGUAGE_IS_FRENCH

SPECIAL_SCRIPT_DATA = sys.modules[ "__main__" ].SPECIAL_SCRIPT_DATA
DIR_CACHE = sys.modules[ "__main__" ].DIR_CACHE

categories = {'ThemesDir'    : Item.TYPE_SKIN, 
              'ThemesNight'  : Item.TYPE_SKIN_NIGHTLY, 
              'Scraper'      : Item.TYPE_SCRAPER_VIDEO, 
              'ScriptsDir'   : Item.TYPE_SCRIPT, 
              'PluginDir'    : Item.TYPE_PLUGIN, 
              'PluginMusDir' : Item.TYPE_PLUGIN_MUSIC, 
              'PluginPictDir': Item.TYPE_PLUGIN_PICTURES, 
              'PluginProgDir': Item.TYPE_PLUGIN_PROGRAMS, 
              'PluginVidDir' : Item.TYPE_PLUGIN_VIDEO,
              'Other'        : 'None',
              ''             : 'None',
              'None'         : 'None'}

xbmctypes  = {Item.TYPE_SKIN            : 'ThemesDir', 
              Item.TYPE_SKIN_NIGHTLY    : 'ThemesNight', 
              Item.TYPE_SCRAPER_VIDEO   : 'Scraper',
              Item.TYPE_SCRIPT          : 'ScriptsDir',
              Item.TYPE_PLUGIN          : 'PluginDir',
              Item.TYPE_PLUGIN_MUSIC    : 'PluginMusDir',
              Item.TYPE_PLUGIN_PICTURES : 'PluginPictDir',
              Item.TYPE_PLUGIN_PROGRAMS : 'PluginProgDir',
              Item.TYPE_PLUGIN_VIDEO    : 'PluginVidDir' }

validCatList = [ 'ThemesDir', 'ThemesNight', 'Scraper', 'ThemesDir', 'ScriptsDir', 'PluginDir', 'PluginMusDir', 'PluginPictDir', 'PluginProgDir', 'PluginVidDir']
class PassionXbmcBrowser(Browser):
    """
    Browse the item on the HTTP server using dbcrossway api
    """
    def __init__( self, *args, **kwargs  ):
        Browser.__init__( self, *args, **kwargs )
        #self.db  = kwargs[ "database" ] # Database file


        import CONF
        #TODO: check if we still need those vars
        self.baseURL = CONF.getBaseURLDbCrossway() # http://passion-xbmc.org/dbcrossway/
        self.catcontentURL = "all/downloads/idparent=%d"
        self.xbmctypecontentURL = "all/downloads/type=file;xbmc_type=%s"
        
        self.baseURLDownloadFile   = CONF.getBaseURLDownloadFile()
        self.baseURLPreviewPicture = CONF.getBaseURLPreviewPicture()
        del CONF

        #csvFile = os.path.join(DIR_CACHE, 'table.csv')
        

        print "update_datas"
        

        self.currentItemId = 0
        
        # Create History instance in order to store browsing history
        self.history = History()
        

    def reset( self ):
        """
        Reset the browser (back to start page)
        """
        Browser.reset()
        self.currentItemId = 0

    def strip_off_passionCDT( self, text, by="", xbmc_labels_formatting=False  ):
        """ FONCTION POUR RECUPERER UN TEXTE D'UN TAG Passion-XBMC """
        text = re.sub( "\[img\](.*?)\[/img\]", by, text )
        result = set_xbmc_carriage_return ( re.sub( "(?s)\[[^\]]*\]", by, text ).replace("[/code]","</br>").replace("[code]","</br>").replace("[/spoiler]","</br>").replace("[spoiler]","</br>"))
        print "strip_off_passionCDT - result"
        return result

    def _removeInvalidChar ( self, match ):
        """
        Remove invalid char for json decoding 
        We use a trick here replacing the string by its quote version
        """
        #return match.group().replace('"',"").replace('description:', '"description":"').replace(',image:', '","image')
        return urllib.quote( match.group() ).replace('%22description%22%3A%22', '"description":"').replace('%22%2C%22image', '","image')
    

    def _retrieve_json( self, url, skipdescript=False, save=True ):
        """
        Retrieve the json file form the HTTP server and save it as a file
        """
        jsondata = ""
        print "JsonDB - retrieving " + url
        try:
            if skipdescript:
                # it make everything slower to use skipdescript (regex + replace ...)
                print "_retrieve_json: skipping description field"
                rawdata = urllib.urlopen(url).read()
                #jsondata = re.sub("""\"description\":\".*?\",\"image""","""\"description\":\"\",\"image""",rawdata)
                jsondata = re.sub("""\"description\":\".*?\",\"image""",self._removeInvalidChar,rawdata)
                
            else:
                jsondata = urllib.urlopen(url).read()#.replace("\\","")#.replace("}{","},{") # Substitution is a Temporary patch for fixing issue on teh server
            jsondata = jsondata.replace( "\\", "\\\\" )
            if save:
                filename = 'passionjson.txt'
                open(os.path.join(DIR_CACHE,filename).encode('utf8'),"w").write(jsondata)
        except Exception, e:
            print "Exception during retrieve_json"
            print e
            print_exc()
        
        return jsondata 

    def _createListFromJson( self, requestURL, skipdescript=False ):
        """
        Create and return the list from json data
        Returns list and name of the list
        
        Json data:
            u'rating'
            u'script_language'
            u'image'
            u'totalitems'
            u'id'
            u'title'
            u'version'
            u'filesize'
            u'totaldownloads'
            u'type'
            u'filetype'
            u'description'
            u'views'
            u'createdate'
            u'orginalfilename'
            u'description_en'
            u'xbmc_type'
            u'commenttotal'
            u'date'
            u'fileurl'
            u'ID_TOPIC'
            u'author'
            u'idparent'        
        """
        list = []

        # Retrieve json data
        jsondata = self._retrieve_json( requestURL, skipdescript )
        
        dicdata = json.loads( jsondata )
        
        # List the main categories at the root level
        for entry in dicdata:
            if Item.isSupported( categories[ entry['xbmc_type'] ] ):
                item = {}
                item['id']                = int( entry['id'] )
                item['name']              = entry['title']#.encode( "utf8" )
                item['parent']            = int( entry['idparent'] )
                item['downloadurl']       = entry['fileurl']
                item['type']              = entry['type']#'CAT'
                item['totaldownloads']    = entry['totaldownloads']
                item['xbmc_type']         = categories[ entry['xbmc_type'] ]
                #item['cattype']           = entry
                if LANGUAGE_IS_FRENCH:
                    item['description']       = self.strip_off_passionCDT( unescape( urllib.unquote( entry['description'] ) ) )#.encode("cp1252").
                else:
                    item['description']       = self.strip_off_passionCDT( unescape( urllib.unquote( entry['description_en'] ) ) )#.encode("cp1252").decode('string_escape')
                if item['description'] == 'None':
                    item['description'] = _( 604 ) 
                item['language']          = entry['script_language']
                item['version']           = entry['version']
                item['author']            = entry['author']
                item['date']              = entry['createdate']
                if entry['date'] != '':
                    item['added'] = strftime( '%d-%m-%Y', localtime( int (entry['date'] ) ) )
                else:
                    item['added'] = entry['date']
                if entry['filesize'] != '':
                    item['filesize'] = int( entry['filesize'] )
                else:
                    item['filesize'] = 0 # ''
                item['thumbnail']         = Item.get_thumb( item['xbmc_type'] )
                item['previewpictureurl'] = entry['image']
                item['previewpicture']    = ""#Item.get_thumb( entry )
                item['image2retrieve']    = False # Temporary patch for reseting the flag after downlaad (would be better in the thread in charge of the download)
                
                item['orginalfilename']     = entry['orginalfilename']
                #TODO: deprecated??? Check server side
                item['fileexternurl']     = "None"
                self._setDefaultImages( item )
                list.append(item)
                print item
            else:
                print "Type not supported by the installer:"
                print entry
            
        return list
    
    def _createCatList( self, id, skipdescript=False ):
        """
        Create and return the list for a category(all type available)
        Returns list and name of the list
        """
        # Create URL in order to retrieve root list (idparent=id)
        requestURL = self.baseURL + self.catcontentURL%id
        
        # Retrieve date from json file
        list = self._createListFromJson( requestURL, skipdescript )

        return list

    def _createXbmcTypeList( self, xbmcType, skipdescript=False ):
        """
        Create and return the list for a specific type of Addon (xbmc_type)
        Returns list and name of the list
        """
        
        #http://passion-xbmc.org/dbcrossway/all/downloads/type=file;xbmc_type=ScriptsDir
        
        print "_createXbmcTypeList"
        
        # Create URL in order to retrieve root list (idparent=id)
        requestURL = self.baseURL + self.xbmctypecontentURL%xbmctypes[xbmcType]
        print requestURL
        
        # Retrieve date from json file
        list = self._createListFromJson( requestURL, skipdescript )
        
        #return listTitle, list
        return list
    
    def _createNewItemList( self, xbmcType, sincedate, skipdescript ):
        """
        Create and return the list since date
        Returns list and name of the list
        """
        
        #http://passion-xbmc.org/dbcrossway/all/downloads/type=file;date%3E1248278091

        # Create URL in order to retrieve root list (idparent=id)
        requestURL = self.baseURL + self.xbmctypecontentURL%xbmctypes[xbmcType] + ";date>%d"%sincedate
        
        # Retrieve date from json file
        list = self._createListFromJson( requestURL, skipdescript )
        
        return listTitle, list
    
    
    def _createALLListItem ( self, xbmcType):
        # Create ALL category
        item = {}
        item['name']              = _( 2201 )
        item['parent']            = 0
        item['type']              = 'addon_type'
        item['description']       = ""
        item['xbmc_type']         = xbmcType
        item['thumbnail']         = Item.get_thumb( item['xbmc_type'] )
        item['previewpictureurl'] = ""
        item['previewpicture']    = ""#Item.get_thumb( entry )
        item['image2retrieve']    = False # Temporary patch for reseting the flag after downlaad (would be better in the thread in charge of the download)
        item['language']          = ""
        item['version']           = ""
        item['author']            = ""
        item['added']             = ""
        item['date']              = ""
        self._setDefaultImages( item )
        print item
        return item
    
    
    
    
    
    
    def _getList( self, listItem=None ):
        """
        Retrieves list matching to a specific list Item
        """
        # Check type of selected item
        list = []
        curCategory = None
        #TODO: manage exception
        
        try:            
            if listItem != None:
                listItemName = listItem['name']
                if listItem['type'] == 'cat':
                    listItemID = listItem['id']
                    listTitle  = listItem['name']
                    if listItem['xbmc_type'] == Item.TYPE_NEW:
                        # Lastest/new items case
                        curCategory = listItemName
                        #TODO: to implement
                        #list = _createNewItemList( self, xbmcType, sincedate )
                        #TODO: remove, this is temporary while fixing server
                    elif listItem['xbmc_type'] == Item.TYPE_SKIN_NIGHTLY:
                        curCategory = listItemName
                        list = self._createCatList( listItemID, skipdescript=True )
                        list.append( self._createALLListItem( listItem['xbmc_type'] ) )
                    else:
                        # List of item to download case                  
                        curCategory = listItemName
                        list = self._createCatList( listItemID )
                        list.append( self._createALLListItem( listItem['xbmc_type'] ) )
                elif listItem['type'] == 'addon_type':
                        curCategory = Item.get_type_title( listItem['xbmc_type'] )
                        list = self._createXbmcTypeList( listItem['xbmc_type'] )
                    
                else:
                    # Return the current list
                    #TODO: start download here?
                    print "This is not a category but an item (download)"
                    list = None
            else: # listItem == None 
                # 1st time (init), we display root list
                # List the main categorie at the root level
                curCategory = _( 10 )
                list = self._createCatList( 0 )
        except Exception, e:
            print "Exception during getNextList"
            print e
            print_exc()
            
        return curCategory, list


    def getNextList( self, index=0 ):
        """
        Returns the list of item (dictionary) on the server depending on the location we are on the server
        Retrieves list of the items and information about each item
        Other possible name: down
        """
        # Check type of selected item
        list = []
        #TODO: manage exception
        try:            
            if len(self.curList)> 0 :
                # Retrieve the list for the selected item
                self.curCategory, list = self._getList( self.curList[index] )
                self.history.push(self.curCategory, self.curList[index], "LIST_ITEM")
            else: # len(self.curList)<= 0 
                # 1st time (init), we display root list
                self.curCategory, list = self._getList()
                self.history.push(self.curCategory, None, "LIST_ITEM")
        except Exception, e:
            print "Exception during getNextList"
            print e
            print sys.exc_info()
            print_exc()
            print_exc()
        #TODO: find better solution, temporary fix for the case of empty list, with current implementation of hetPrevList backward is not possible when list is empty    
        if len( list ) > 0:
            # Replace current list
            self.curList = list
            
        return self.curList
    
    

    def getPrevList( self ):
        """
        Returns the list (up) of item (dictionary) on the server depending on the location we are on the server
        Go to previous page/list 
        Other possible name: Up
        """
        list = []
        #TODO: cover case of empty list
        item = self.curList[0] # We have to check the info one of the items in the list (why not the 1st?)

        try:
            # delete current page from history (we are going to load the previous one)
            self.history.pop()

            # Get previous entry (the one we gonna reload) but since we did a pop this is the current
            #previousIndex, previousHdl, previousHdlType, previousTitleLabel = self.history.getPrevious()
            previousCategory, previousItem, previousHdlType = self.history.getCurrent()
            
            # Get the list
            self.curCategory, list = self._getList( previousItem )

        except Exception, e:
            print "Exception during getPrevList"
            print e
            print sys.exc_info()
            print_exc()
            print_exc()
        # Replace current list
        self.curList = list
        return list
    
        
    def reloadList( self ):
        """
        Reload and returns the current list
        """
        catId = 0
        if ( len(self.curList) > 0 ):
            # Not the 1st load
            # Get current categorie id 
            catId = self.curList[0]['parent']
        return self.getNextList(catId)
    
    def getContextMenu( self ):
        """
        Returns the list of the commands available via the context menu
        """
        pass
    
    def getCategoryInfo( self, catId ):
        """
        Retrieves Categorie Name and Install path
        """
        title = ""
        path = ""
        print "title = %s"%title
        print "type = %s"%type
        return title, type


    def getInfo( self, index ):
        """
        Returns the information about a specific item (dictionnary)
        Returns a dictionnary with the structure:
        {name, description, icon, downloads, file, created, screenshot}
        Chaque index du dictionnaire renvoie à une liste d'occurences.
        Alimenter cette fonction avec l'id du fichier dont on veut obtenir les infos.
        """
        return self.curList[index]
    
    def _loadData ( self ):
        """
        Load the data for the current page
        """
    
    def sortByDate( self ):
        """
        Returns current list sorted by date
        """
        pass

    def sortByLang( self ):
        """
        Returns current list sorted by language
        """
        pass
    
    def sortByAuthor( self ):
        """
        Returns current list sorted by author
        """
        pass    
    

    def isCat( self, index ):
        """
        Returns True when selected item is a category
        """
        if ( ( len(self.curList)> 0 ) and ( self.curList[index]['type'] in ['cat', 'addon_type'] ) ):
            # Convert index to id
            return True
        else:
            return False
    
    def getInstaller( self, index ):
        """
        Returns an ItemInstaller instance
        """
        itemInstaller = None
        try:            
            if ( ( len(self.curList)> 0 ) and ( self.curList[index]['type'] == 'file' ) ):
                # Convert index to id
                itemId      = self.curList[index]['id']
                name        = self.curList[index]['name']
                catId       = self.curList[index]['parent']
                externalURL = self.curList[index]['fileexternurl'].encode('utf8')
                #type        = self.curList[index]['xbmc_type']

                # Get file size
                itemInfos = self.getInfo(index)
                filesize  = itemInfos['filesize']
                xbmc_type = itemInfos['xbmc_type']
                
                print itemInfos

                print "getInstaller - name" 
                print name
                #print "getInstaller - externalURL" 
                #print externalURL
                print "getInstaller - filesize"
                print filesize

                # Create the right type of Installer Object
                #itemInstaller = PassionXbmcItemInstaller.PassionXbmcItemInstaller( name, itemId, xbmc_type, filesize, externalURL )
                itemInstaller = PassionXbmcItemInstaller.PassionXbmcItemInstaller( itemInfos )
            else:
                print "getInstaller: error impossible to install a category, it has to be an item "

        except Exception, e:
            print "Exception during getInstaller"
            print_exc()
                 
        return itemInstaller

    def applyFilter( self ):
        pass


    def _setDefaultImages(self, item):
        """
        Set the images with default value depending on the type of the item
        """
        print "_setDefaultImages"
        print item['previewpictureurl']
        if  item['previewpictureurl'] == '':
            # No picture available -> use default one
            item['thumbnail']      = Item.get_thumb( item['xbmc_type'] ) # icone
            item['previewpicture'] = ""#Item.THUMB_NOT_AVAILABLE # preview
        else:
            # Check if picture is already downloaded and available
            downloadImage = False
            thumbnail, checkPathPic = set_cache_thumb_name( item['previewpictureurl'] )
            if thumbnail and os.path.isfile( thumbnail ):
                item['thumbnail'] = thumbnail
            else:
                item['thumbnail'] = Item.THUMB_NOT_AVAILABLE
                downloadImage = True
                
            if os.path.exists(checkPathPic):
                item['previewpicture'] = checkPathPic
            else:
                item['previewpicture'] = ""#Item.THUMB_NOT_AVAILABLE
                downloadImage = True
                
            if downloadImage == True:
                # Set flag for download (separate thread)
                item['image2retrieve'] = True
                

    #def _downloadImage( self, picname, listitem=None ):
    def _downloadImage( self, picname ):
        """
        Download picture from the server, save it, create the thumbnail and return path of it
        """
        print "_downloadImage %s"%picname
        try:
        
            filetodlUrl = self.baseURLPreviewPicture + picname
            print "filetodlUrl"            
            print filetodlUrl
            thumbnail, localFilePath = set_cache_thumb_name( picname )
            print thumbnail
            print localFilePath
            loc = urllib.URLopener()
            loc.retrieve(filetodlUrl, localFilePath)   

            # remove file if size is 0 bytes and report error if exists error
            if localFilePath and os.path.isfile( localFilePath ):
                if os.path.getsize( localFilePath ) <= 0:
                    os.remove( localFilePath )
                    #TODO: create a thumb for the default image?
                    #TODO: return empty and manage default image at the level of the caller
                    thumbnail = "" 
                else:
                    thumb_size = int( self.thumb_size_on_load )
                    thumbnail = makeThumbnails( localFilePath, thumbnail, w_h=( thumb_size, thumb_size ) )
                    if thumbnail == "": thumbnail = localFilePath

#            if thumbnail and os.path.isfile( thumbnail ) and hasattr( listitem, "setThumbnailImage" ):
#                listitem.setThumbnailImage( thumbnail )
            else:
                thumbnail, localFilePath = "", ""
        except:
            print "_downloadImage: Exception - Impossible to downlod the picture: %s" % picname
            print_exc()
            #TODO: create a thumb for the default image?
            #TODO: return empty and manage default image at the level of the caller
            thumbnail, localFilePath = "", "" 
        print "thumbnail = %s"%thumbnail
        print "localFilePath = %s"%localFilePath
        return thumbnail, localFilePath

    def close( self ):
        """
        Close browser: i.e close connection, free memory ...
        """
        try: self.cancel_update_Images()
        except: print "PassionXbmcBrowser: error on close (cancel image)"

    