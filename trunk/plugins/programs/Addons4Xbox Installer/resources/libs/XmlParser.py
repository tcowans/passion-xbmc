"""
"""


# Modules general
import os
import sys

from traceback import print_exc

import elementtree.ElementTree as ET

# Modules custom
try:
    from specialpath import *
    from utilities import *
    from Item import *
except:
    print_exc()

#FONCTION POUR RECUPERER LES LABELS DE LA LANGUE.
_ = sys.modules[ "__main__" ].__language__



def parseAddonXml( xmlData, itemInfo ):
    """
    Get Item Info from addon.xml and set itemInfo object 
    """
    # id
    # name
    # type
    # version
    # author
    # disclaimer
    # summary
    # description
    # icon
    # fanart
    # changelog
    # library: path of python script
    # raw_item_sys_type: file | archive | dir
    # raw_item_path
    # install_path
    # extracted_path
    # provides
    # required_lib
    
    status = 'OK'
    try:
        if ( xmlData ):
            xmlElt = ET.parse( xmlData ).getroot()
            print 'xmlElt'
            print xmlElt
            status = parseAddonElt( xmlElt, itemInfo )
    except:
        status = 'ERROR'
        print_exc()
    
    return status
            



def parseAddonElt( addonElt, itemInfo ):
    """
    Get Item Info from addon.xml and set itemInfo object 
    """
    # id
    # name
    # type
    # version
    # author
    # disclaimer
    # summary
    # description
    # icon
    # fanart
    # changelog
    # library: path of python script
    # raw_item_sys_type: file | archive | dir
    # raw_item_path
    # install_path
    # extracted_path
    # provides
    # required_lib
    
    status = 'OK'
    try:
        if ( addonElt ):
            libPoint = None
            itemInfo [ "id" ]      = addonElt.attrib.get( "id" )
            #itemInfo [ "name" ]    = addonElt.attrib.get( "name" ).encode( "utf8" )
            itemInfo [ "name" ]    = addonElt.attrib.get( "name" )
            itemInfo [ "version" ] = addonElt.attrib.get( "version" )
            itemInfo [ "author" ]  = addonElt.attrib.get( "provider-name" )
            extensions = addonElt.findall("extension")
            if extensions:
                for extension in extensions:
                    if extension.attrib.get("library"):
                        # Info on lib
                        itemInfo [ "library" ] = extension.attrib.get( "library" )
                        itemInfo [ "provides" ] = extension.findtext( "provides" )
                        libPoint = extension.attrib.get( "point" )
                    elif ("xbmc.addon.metadata" == extension.attrib.get( "point" ) ):
                        # Metadata
                        platform = extension.findtext( "platform" ) 
                        nofanart = extension.findtext( "nofanart" ) 
                        #TODO: parse metadata here
            requires = addonElt.find("requires")
            if requires:
                modules2import = requires.findall("import")
                requiredModuleList = []
                for module in modules2import:
                    moduleInfo = {}
                    moduleInfo [ "id" ]      = module.attrib.get( "addon" )
                    moduleInfo [ "version" ] = module.attrib.get( "version" )
                    itemInfo [ "required_lib" ] = requiredModuleList.append( moduleInfo )
                    
            #itemInfo[ "icon" ] = os.path.join( cwd, "default.tbn" )
            
            # Determine the Type of the addon
            itemInfo [ "type" ] = TYPE_ADDON # Unsupported type of addon
            if libPoint:
                if TYPE_ADDON_PLUGIN in libPoint:
                    # Plugin: we need to check the addons id
                    if TYPE_ADDON_MUSIC in itemInfo [ "id" ]:
                        itemInfo [ "type" ] = TYPE_ADDON_MUSIC
                    elif TYPE_ADDON_PICTURES in itemInfo [ "id" ]:
                        itemInfo [ "type" ] = TYPE_ADDON_PICTURES
                    elif TYPE_ADDON_PROGRAMS in itemInfo [ "id" ]:
                        itemInfo [ "type" ] = TYPE_ADDON_PROGRAMS
                    elif TYPE_ADDON_VIDEO in itemInfo [ "id" ]:
                        itemInfo [ "type" ] = TYPE_ADDON_VIDEO
                elif TYPE_ADDON_MODULE in itemInfo [ "id" ]: # xbmc.python.module
                        itemInfo [ "type" ] = TYPE_ADDON_MODULE
                elif TYPE_ADDON_SCRIPT in itemInfo [ "id" ]: # xbmc.python.script
                        itemInfo [ "type" ] = TYPE_ADDON_SCRIPT
                #TODO: add repo Addons
                
        else:
            print "addonElt not defined"
            status = 'ERROR'

    except:
        status = 'ERROR'
        print_exc()

    print itemInfo
    
    return status

def createItemListFromXml( xmlData ):
    """
    Create and return the list of addons from XML data
    Returns list and name of the list
   """
    status = 'OK'
    list = []

    try:
        if ( xmlData ):
            xmlElt = ET.parse( xmlData ).getroot() # root: <addons>
            print 'xmlElt'
            print xmlElt
            if ( xmlElt ):
                addons = xmlElt.findall("addon")
                for addon in addons:
                    # dictionary to hold addon info
                    itemInfo = {}
                    status = parseAddonElt( addon, itemInfo )
                    list.append(itemInfo)
    except:
        status = 'ERROR'
        print_exc()
    
    return status, list

class ListItemFromXML:
    currentParseIdx = 0
    addons = []
    def __init__( self, xmlData ):
        try:
            if ( xmlData ):
                #print xmlData
                rootXmlElt = ET.parse( xmlData ).getroot() # root: <addons>
                print 'rootXmlElt'
                print rootXmlElt
                
                if ( rootXmlElt ):
                    self.addons = rootXmlElt.findall("addon")
        except:
            status = 'ItemList::__init__: ERROR'
            print_exc()
    
        
    def _parseAddonElement(self, addonElt, itemInfo):
        return parseAddonElt( addonElt, itemInfo )
    
    
    def getNextItem(self):
        result = None
        if len(self.addons) > 0 and self.currentParseIdx < len(self.addons):
            itemInfo = {}
            status = self._parseAddonElement( self.addons[self.currentParseIdx], itemInfo )
            self.currentParseIdx = self.currentParseIdx + 1
            if status == 'OK':
                result = itemInfo
        else:
            result = None
        return result
    
    
#    
#    # List the main categories at the root level
#    for entry in dicdata:
#        if Item.isSupported( categories[ entry['xbmc_type'] ] ):
#            item = {}
#            item['id']                = int( entry['id'] )
#            item['name']              = entry['title']#.encode( "utf8" )
#            item['parent']            = int( entry['idparent'] )
#            item['downloadurl']       = entry['fileurl']
#            item['type']              = entry['type']#'CAT'
#            item['totaldownloads']    = entry['totaldownloads']
#            item['xbmc_type']         = categories[ entry['xbmc_type'] ]
#            #item['cattype']           = entry
#            if LANGUAGE_IS_FRENCH:
#                item['description']       = self.strip_off_passionCDT( unescape( urllib.unquote( entry['description'] ) ) )#.encode("cp1252").
#            else:
#                item['description']       = self.strip_off_passionCDT( unescape( urllib.unquote( entry['description_en'] ) ) )#.encode("cp1252").decode('string_escape')
#            if item['description'] == 'None':
#                item['description'] = _( 604 ) 
#            item['language']          = entry['script_language']
#            item['version']           = entry['version']
#            item['author']            = entry['author']
#            item['date']              = entry['createdate']
#            if entry['date'] != '':
#                item['added'] = strftime( '%d-%m-%Y', localtime( int (entry['date'] ) ) )
#            else:
#                item['added'] = entry['date']
#            if entry['filesize'] != '':
#                item['filesize'] = int( entry['filesize'] )
#            else:
#                item['filesize'] = 0 # ''
#            item['thumbnail']         = Item.get_thumb( item['xbmc_type'] )
#            item['previewpictureurl'] = entry['image']
#            item['previewpicture']    = ""#Item.get_thumb( entry )
#            item['image2retrieve']    = False # Temporary patch for reseting the flag after downlaad (would be better in the thread in charge of the download)
#            
#            item['orginalfilename']     = entry['orginalfilename']
#            #TODO: deprecated??? Check server side
#            item['fileexternurl']     = "None"
#            self._setDefaultImages( item )
#            list.append(item)
#            print item
#        else:
#            print "Type not supported by the installer:"
#            print entry
#        
#    return list

