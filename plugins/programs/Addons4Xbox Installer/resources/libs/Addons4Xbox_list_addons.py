

import os
#import urllib
import sys
#import xbmc
#import xbmcplugin
#import xbmcgui
from traceback import print_exc

#__script__       = sys.modules[ "__main__" ].__script__
#__plugin__       = sys.modules[ "__main__" ].__plugin__
#__author__       = sys.modules[ "__main__" ].__author__
#__url__          = sys.modules[ "__main__" ].__url__
#__svn_url__      = sys.modules[ "__main__" ].__svn_url__
#__credits__      = sys.modules[ "__main__" ].__credits__
#__platform__     = sys.modules[ "__main__" ].__platform__
#__date__         = sys.modules[ "__main__" ].__date__
#__version__      = sys.modules[ "__main__" ].__version__
#__svn_revision__ = sys.modules[ "__main__" ].__svn_revision__
#__XBMC_Revision__= sys.modules[ "__main__" ].__XBMC_Revision__
__language__     = sys.modules[ "__main__" ].__language__
#ROOTDIR            = sys.modules[ "__main__" ].ROOTDIR
#BASE_RESOURCE_PATH = sys.modules[ "__main__" ].BASE_RESOURCE_PATH
#LIBS_PATH          = sys.modules[ "__main__" ].LIBS_PATH
#MEDIA_PATH         = sys.modules[ "__main__" ].MEDIA_PATH


# Custom modules
try:
    from globalvars import DIR_CACHE, DIR_ADDON_REPO, PARAM_REPO_ID, PARAM_TYPE, PARAM_INSTALL_FROM_REPO, PARAM_ADDON_NAME, PARAM_URL, PARAM_DATADIR, VALUE_LIST_ALL_ADDONS
    from PluginMgr import PluginMgr
    from Item import supportedAddonList #TYPE_ADDON_SCRIPT, TYPE_ADDON_MUSIC, TYPE_ADDON_PICTURES, TYPE_ADDON_PROGRAMS, TYPE_ADDON_VIDEO, TYPE_ADDON_WEATHER, TYPE_ADDON_MODULE
    from utilities import readURL,RecursiveDialogProgress, checkURL
    from XmlParser import ListItemFromXML, parseAddonXml
except:
    print_exc()


class Main:
    """
    Main plugin class
    """

    def __init__( self, *args, **kwargs ):
        
        self.pluginMgr = PluginMgr()
        self.parameters = self.pluginMgr.parse_params()
        
        print "List of Add-ons"
        repoId = self.parameters[ PARAM_REPO_ID ]
        addonCat = self.parameters[ PARAM_TYPE ]
        self._createAddonsDir( repoId, addonCat )

        print "end_of_directory"
        #self.pluginMgr.end_of_directory( True, update=False )
        self.pluginMgr.add_sort_methods( True )
        self.pluginMgr.end_of_directory( True )


    def _createAddonsDir ( self, repoId, cat ):
        """
        Display the addons to install for a repository
        """
        # Retrieve info from  addon.xml for the repository
        repoInfo = self._getInstalledAddInfo( os.path.join( DIR_ADDON_REPO, repoId) )       
              
        # Retrieving addons.xml from remote repository
        xmlInfofPath = os.path.join( DIR_CACHE, "addons.xml")
        if os.path.isfile(xmlInfofPath):
            os.remove(xmlInfofPath)
        data = readURL( repoInfo [ "repo_url" ], save=True, localPath=xmlInfofPath )
        if ( os.path.exists( xmlInfofPath ) ):
            try:
                xmlData = open( os.path.join( xmlInfofPath ), "r" )
                listAddonsXml = ListItemFromXML(xmlData)
                xmlData.close()
            except:
                print_exc()            
            
            filter = "False"
            if cat == VALUE_LIST_ALL_ADDONS:
                filter = "item['type'] in supportedAddonList"
            elif cat in supportedAddonList:
                filter = "item['type'] == '%s'"%cat

            keepParsing = True
            while (keepParsing):
                item = listAddonsXml.getNextItem()
                print item
                if item:
                    print "filter: %s"%filter
                    if eval(filter):
                        endRepoChar = "/"
                        if repoInfo [ "repo_datadir" ].endswith( "/" ):
                            endRepoChar = ""
                        
                        if repoInfo [ "repo_format" ] ==  'zip':
                            downloadUrl = (repoInfo [ "repo_datadir" ] + endRepoChar + item["id"] + '/' + item["id"]  + '-' + item["version"] + ".zip").replace(' ', '%20')
                            changelog   = (repoInfo [ "repo_datadir" ] + endRepoChar + item["id"] + '/' + "changelog" + '-' + item["version"] + ".txt").replace(' ', '%20') 
                            iconimage   = (repoInfo [ "repo_datadir" ] + endRepoChar + item["id"] + '/' + "icon.png").replace(' ', '%20')                             
                        else:
                            downloadUrl = (repoInfo [ "repo_datadir" ] + endRepoChar + item["id"] + '/').replace(' ', '%20') 
                            changelog   = (repoInfo [ "repo_datadir" ] + endRepoChar + item["id"] + '/' + "changelog" + ".txt").replace(' ', '%20') 
                            iconimage   = (repoInfo [ "repo_datadir" ] + endRepoChar + item["id"] + '/' + "icon.png").replace(' ', '%20')
                        item["ImageUrl"] = iconimage
                        item["changelog"] = changelog
                            
                        print downloadUrl
                        paramsAddons = {}
                        paramsAddons[PARAM_INSTALL_FROM_REPO]   = "true"
                        paramsAddons[PARAM_ADDON_NAME]          = item['name'].encode('utf8')
                        paramsAddons[PARAM_URL]                 = downloadUrl
                        paramsAddons[PARAM_DATADIR]             = repoInfo [ "repo_datadir" ]
                        paramsAddons[PARAM_TYPE]                = repoInfo [ "repo_format" ]
                        paramsAddons[PARAM_REPO_ID]             = repoId

                        url = self.pluginMgr.create_param_url( paramsAddons )

                        if ( url ):
                            #self._addLink( item['name'], url, iconimage=iconimage)
                            item["PluginUrl"] = url
                            self.pluginMgr.addItemLink( item )
                            print "Link added"
                else:
                    keepParsing = False

    def _getInstalledAddInfo( self, addonpath ):
        #TODO: move to InstallMgr?
        """
        Get metadata from addon.xml of an installed addon
        """
        itemInfo = {}
        
        # Open addon.xml
        print "Addon path: %s"%addonpath
        xmlInfofPath = os.path.join( addonpath, "addon.xml")
        if os.path.exists( xmlInfofPath ):
            try:
                xmlData = open( os.path.join( xmlInfofPath ), "r" )
                statusGetInfo = parseAddonXml( xmlData, itemInfo )
                xmlData.close()
            except:
                print_exc()            
            if statusGetInfo == "OK":
                iconPath = os.path.join( xmlInfofPath, "icon.png")
                if os.path.exists( iconPath ):
                    itemInfo [ "icon" ] = iconPath
                else:
                    #TODO: move default image selection in the caller code????
                    itemInfo [ "icon" ]="DefaultFolder.png"
        return itemInfo
        