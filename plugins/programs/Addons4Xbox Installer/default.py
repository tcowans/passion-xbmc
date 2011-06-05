"""
   Installing XBMC addons on XBMC4XBOX using xbmcaddon Nuka1195 library
   Special thanks to Frost for his library, Nuka1195 for his library too and Maxoo for the logo
   Please read changelog
"""

REMOTE_DBG       = False 


# Plugin constants
__script__       = "Unknown"
__plugin__       = "Addons4Xbox Installer"
__author__       = "Temhil (http://passion-xbmc.org)"
__url__          = "http://passion-xbmc.org/index.php"
__svn_url__      = "http://passion-xbmc.googlecode.com/svn/trunk/plugins/programs/Addons4xbox/"
__credits__      = "Team XBMC Passion"
__platform__     = "xbmc media center [XBOX]"
__date__         = "06-04-2011"
__version__      = "0.7"
__svn_revision__ = 0
__XBMC_Revision__= 30805


import os
import urllib
import xbmc
import xbmcplugin
import xbmcgui
from traceback import print_exc


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



ROOTDIR            = os.getcwd()
BASE_RESOURCE_PATH = os.path.join( ROOTDIR, "resources" )
LIBS               = os.path.join( BASE_RESOURCE_PATH, "libs" )
PERSIT_REPO_LIST   = "repo_list.txt"

# URLs
REPO_LIST_URL = "http://wiki.xbmc.org/index.php?title=Unofficial_Add-on_Repositories"

__platform__ = "xbmc media center, [%s]" % xbmc.__platform__
__language__ = xbmc.Language( ROOTDIR ).getLocalizedString


# Custom modules
try:
    from resources.libs.specialpath import *
    from resources.libs.Item import *
    import resources.libs.LocalArchiveInstaller as LocalArchiveInstaller
    import resources.libs.RemoteArchiveInstaller as RemoteArchiveInstaller
    from resources.libs.utilities import readURL,RecursiveDialogProgress, checkURL
    from resources.libs.XmlParser import ListItemFromXML, parseAddonXml
    from resources.libs.FileManager import fileMgr
except:
    print_exc()

# get xbmc run under?
platform = os.environ.get( "OS", "xbox" )


class PersistentDataCreator:
    """
    Creates persitent data
    """
    def __init__( self, data, filename ):
        self._persitData( data, filename )

    def _persit_data( self, data, filename ):
        f = open( os.path.join( CACHEDIR, filename), 'w' )
        pickle.dump(data, f)
        f.close()

class PersistentDataRetriever:
    """
    Retrieves persitent data
    """
    def __init__( self, filename ):
        self._persitData( data, filename )

    def get_data( self ):
        data = None
        if os.path.isfile( os.path.join( CACHEDIR, filename ) ):
            f = open( os.path.join( CACHEDIR, filename ), 'r')
            try:
                data = pickle.load(f)
            except:
                pass
            f.close()
        return data

class Addons4xboxInstallerPlugin:
    """
    Main plugin class
    """
    # define param key names
    PARAM_TITLE             = "title"
    PARAM_TYPE              = 'type'
    PARAM_LISTTYPE          = 'listype'
    PARAM_LOCALPATH         = 'localpath'
    PARAM_INSTALL_FROM_ZIP  = 'installfromzip'
    PARAM_INSTALL_FROM_REPO = 'installfromrepo'
    PARAM_REPO_ID           = 'repoid'
    PARAM_REPO_NAME         = 'reponame'
    PARAM_ADDON_NAME        = 'addonname'
    PARAM_URL               = 'url'
    PARAM_DATADIR           = 'datadir'
    PARAM_REPO_FORMAT       = 'format'
    VALUE_LIST_CATEGORY     = 'listcataddon'
    VALUE_LIST_LOCAL_REPOS  = 'listlocalrepos'
    VALUE_LIST_ALL_ADDONS   = 'alladdons'
    VALUE_LIST_ADDONS       = 'listaddons'

    # List of supported addons
    supportedAddonList = [ TYPE_ADDON_SCRIPT,
                           TYPE_ADDON_MUSIC,
                           TYPE_ADDON_PICTURES,
                           TYPE_ADDON_PROGRAMS,
                           TYPE_ADDON_VIDEO,
                           TYPE_ADDON_WEATHER,
                           TYPE_ADDON_MODULE,
                           TYPE_ADDON_REPO ]

    def __init__( self, *args, **kwargs ):
        if True: #self._check_compatible():
            self._get_settings()
            self.parameters = self._parse_params()

            # if 1st start create missing directories
            self.fileMgr = fileMgr()
            #self.fileMgr.verifrep( get_install_path( TYPE_ADDON ) )
            self.fileMgr.verifrep( DIR_ADDON_MODULE )
            self.fileMgr.verifrep( DIR_ADDON_REPO )
            self.fileMgr.verifrep( DIR_CACHE )
            
            # Check settings
            if xbmcplugin.getSetting('first_run') == 'true':
                # Check (only the 1st time) is xbmcaddon module is available 
                print( "     **First run")
                if self.check_addon_lib():
                    print( "         XBMC Addon 4 XBOX Addon Library already installed")
                    print( "         Installing default repositories")
                    if ( self.installRepos() ):
                        self.select()
                        xbmcplugin.setSetting('first_run','false')
                else:
                    print( "         ERROR - XBMC Addon 4 XBOX Addon Library MISSING")
                    dialog = xbmcgui.Dialog()
                    dialog.ok( __language__(30000), __language__(30091) ,__language__(30092))                   
            else:
                self.select()


    def check_addon_lib(self):
        """
        Check id xbmcaddon module is available
        Returns 1 if success, 0 otherwise
        """
        ok = 1
        try:
            import xbmcaddon
        except ImportError:
            ok = 0
        return ok
    

    def _check_compatible(self):
        """
        Check if XBMC version is compatible with the plugin
        """
        xbmcgui = None
        try:
            # spam plugin statistics to log
            print( "[PLUGIN] '%s: Version - %s-r%s' initialized!" % ( __plugin__, __version__, __svn_revision__.replace( "$", "" ).replace( "Revision", "" ).strip( ": " ) ) )
            # get xbmc revision
            xbmc_version = xbmc.getInfoLabel( "System.BuildVersion" )
            xbmc_rev = int( xbmc_version.split( " " )[ 1 ].replace( "r", "" ) )
            # compatible?
            ok = xbmc_rev >= int( __XBMC_Revision__ )
            print xbmc_rev
            print __XBMC_Revision__
        except:
            # error, so unknown, allow to run
            print_exc()
            xbmc_rev = 0
            ok = 2
        # spam revision info
        print( "     ** Required XBMC Revision: r%s **" % ( __XBMC_Revision__, ) )
        print( "     ** Found XBMC Revision: r%d [%s] **" % ( xbmc_rev, ( "Not Compatible", "Compatible", "Unknown", )[ ok ], ) )
        # if not compatible, inform user
        if ( not ok ):
            xbmcgui.Dialog().ok( "%s - %s: %s" % ( __plugin__, xbmc.getLocalizedString( 30900 ), __version__, ), xbmc.getLocalizedString( 30901 ) % ( __plugin__, ), xbmc.getLocalizedString( 30902 ) % ( __XBMC_Revision__, ), xbmc.getLocalizedString( 30903 ) )
        #if not xbmc run under xbox, inform user
        if ( platform.upper() not in __platform__ ):
            ok = 0
            print( "system::os.environ [%s], This plugin run under %s only." % ( platform, __platform__, ) )
            if xbmcgui == None:
                xbmcgui.Dialog().ok( __plugin__, "%s: system::os.environ [[COLOR=ffe2ff43]%s[/COLOR]]" % ( xbmc.getLocalizedString( 30904 ), platform, ), xbmc.getLocalizedString( 30905 ) % __platform__ )
        return ok

    def installRepos(self):
        """
        Install default repositories in the plugin data directory
        """
        ok = 0
        repo_source = os.path.join( ROOTDIR, "resources", "repositories" )
        try:
            if os.path.exists( repo_source ):
                self.fileMgr.copyDir( repo_source, DIR_ADDON_REPO )
                print "SUCCESS: Repositories copied %s"%DIR_ADDON_REPO
                ok = 1
            else:
                dialog = xbmcgui.Dialog()
                dialog.ok( __language__(30000), __language__(30006), __language__(30007) )
                print "ERROR: impossible to copy repositories"
                print "Repositories are missing in the plugin structure"
        except:
            dialog = xbmcgui.Dialog()
            dialog.ok( __language__(30000), __language__(30006), __language__(30007) )
            print "ERROR: impossible to copy repositories to %s"%DIR_ADDON_REPO
            print_exc()            
        return ok


    def createRootDir ( self ):
        """
        Creates root list of the plugin
        """
        paramsDicZip = {}
        paramsDicZip[self.PARAM_INSTALL_FROM_ZIP] = "true"
        urlZip = self._create_param_url( paramsDicZip )
        if urlZip:
            self._addLink( __language__( 30203 ), urlZip )
        
        paramsDicRepo = {}
        paramsDicRepo[self.PARAM_LISTTYPE] = self.VALUE_LIST_LOCAL_REPOS
        urlRepo = self._create_param_url( paramsDicRepo )
        if urlRepo:
            self._addDir( __language__( 30204 ), urlRepo )
        
        self._end_of_directory( True )


    def createRepo2InstallListDir( self ):
        """
        Creates list for install of the Unofficial repositories available on XBMC wiki 
        """
        
        print "createRepo2InstallListDir"
        #xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category=__language__( 30001 ) )
        
        # Add official repo
        icon = "DefaultAddon.png"
        for repo in self.repoList:
            print repo
            paramsRepo = {}
            #paramsRepo[self.PARAM_REPO_ID] = repo[self.PARAM_REPO_ID]
            paramsRepo[self.PARAM_REPO_ID] = str(self.repoList.index(repo))
            paramsRepo[self.PARAM_LISTTYPE] = self.VALUE_LIST_CATEGORY
            urlRepo = self._create_param_url( paramsRepo )
            if urlRepo:
                self._addDir( repo['name'], urlRepo )
        
        print "Loading wiki page: %s"%REPO_LIST_URL
        status, list = wikiparser.getRepoList(REPO_LIST_URL, addItemFunc=self._addLink, progressBar=None,  msgFunc=None )
        self._add_sort_methods( True )
        self._end_of_directory( True )
        
        # Save list to a file
        PersistentDataCreator( list, PERSIT_REPO_LIST )

    

    def createLocalRepoDir ( self ):
        """
        List of installed repositories
        """
        for repoId in os.listdir( DIR_ADDON_REPO ):
            print "Repo ID = %s"%repoId
            
            # Retrieve info from  addon.xml
            itemInfo = self._getInstalledAddInfo( os.path.join( DIR_ADDON_REPO, repoId) )
            print itemInfo
            if itemInfo:
                # Dic Not empty
                paramsRepo = {}
                paramsRepo[self.PARAM_REPO_ID]  = repoId
                paramsRepo[self.PARAM_LISTTYPE] = self.VALUE_LIST_CATEGORY
                urlRepo = self._create_param_url( paramsRepo )
                if urlRepo:
                    self._addDir( itemInfo [ "name" ], urlRepo, iconimage=itemInfo [ "icon" ] )
        self._end_of_directory( True )


    def _getInstalledAddInfo(self, addonpath):
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
    

    def createAddonCatDir ( self, repoId ):
        """
        Creates list of addon categories for a specific repository
        """
        params = {}
        params[self.PARAM_REPO_ID] = str(repoId)
        params[self.PARAM_LISTTYPE] = self.VALUE_LIST_ADDONS
        params[self.PARAM_TYPE] = self.VALUE_LIST_ALL_ADDONS
        url = self._create_param_url( params )
        if url:
            self._addDir( __language__( 30107 ), url )        
        
        params = {}
        params[self.PARAM_REPO_ID] = str(repoId)
        params[self.PARAM_LISTTYPE] = self.VALUE_LIST_ADDONS
        params[self.PARAM_TYPE] = TYPE_ADDON_SCRIPT
        url = self._create_param_url( params )
        self._addDir( __language__( 30101 ), url )        
        
        params = {}
        params[self.PARAM_REPO_ID] = str(repoId)
        params[self.PARAM_LISTTYPE] = self.VALUE_LIST_ADDONS
        params[self.PARAM_TYPE] = TYPE_ADDON_MUSIC
        url = self._create_param_url( params )
        if url:
            self._addDir( __language__( 30102 ), url )        
        
        params = {}
        params[self.PARAM_REPO_ID] = str(repoId)
        params[self.PARAM_LISTTYPE] = self.VALUE_LIST_ADDONS
        params[self.PARAM_TYPE] = TYPE_ADDON_PICTURES
        url = self._create_param_url( params )
        if url:
            self._addDir( __language__( 30103 ), url )        
        
        params = {}
        params[self.PARAM_REPO_ID] = str(repoId)
        params[self.PARAM_LISTTYPE] = self.VALUE_LIST_ADDONS
        params[self.PARAM_TYPE] = TYPE_ADDON_PROGRAMS
        url = self._create_param_url( params )
        if url:
            self._addDir( __language__( 30104 ), url )        
        
        params = {}
        params[self.PARAM_REPO_ID] = str(repoId)
        params[self.PARAM_LISTTYPE] = self.VALUE_LIST_ADDONS
        params[self.PARAM_TYPE] = TYPE_ADDON_VIDEO
        url = self._create_param_url( params )
        if url:
            self._addDir( __language__( 30105 ), url )        
        
        params = {}
        params[self.PARAM_REPO_ID] = str(repoId)
        params[self.PARAM_LISTTYPE] = self.VALUE_LIST_ADDONS
        params[self.PARAM_TYPE] = TYPE_ADDON_WEATHER
        url = self._create_param_url( params )
        if url:
            self._addDir( __language__( 30106 ), url )        
        
        params = {}
        params[self.PARAM_REPO_ID] = str(repoId)
        params[self.PARAM_LISTTYPE] = self.VALUE_LIST_ADDONS
        params[self.PARAM_TYPE] = TYPE_ADDON_MODULE
        url = self._create_param_url( params )
        if url:
            self._addDir( __language__( 30108 ), url )        
        
        self._end_of_directory( True )

    def createAddonsDir ( self, repoId, cat ):
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
            if cat == self.VALUE_LIST_ALL_ADDONS:
                filter = "item['type'] in self.supportedAddonList"
            elif cat in self.supportedAddonList:
                filter = "item['type'] == '%s'"%cat
#            elif cat == TYPE_ADDON_SCRIPT:
#                filter = "item['type'] == TYPE_ADDON_SCRIPT"
#            elif cat == TYPE_ADDON_MUSIC:
#                filter = "item['type'] == TYPE_ADDON_MUSIC"
#            elif cat == TYPE_ADDON_PICTURES:
#                filter = "item['type'] == TYPE_ADDON_PICTURES"
#            elif cat == TYPE_ADDON_PROGRAMS:
#                filter = "item['type'] == TYPE_ADDON_PROGRAMS"
#            elif cat == TYPE_ADDON_VIDEO:
#                filter = "item['type'] == TYPE_ADDON_VIDEO"
#            elif cat == TYPE_ADDON_WEATHER:
#                filter = "item['type'] == TYPE_ADDON_WEATHER"
#            elif cat == TYPE_ADDON_MODULE:
#                filter = "item['type'] == TYPE_ADDON_MODULE"

            keepParsing = True
            while (keepParsing):
                item = listAddonsXml.getNextItem()
                print item
                if item:
                    print "filter: %s"%filter
                    if eval(filter):
                        if repoInfo [ "repo_format" ] ==  'zip':
                            downloadUrl = (repoInfo [ "repo_datadir" ] + '/' + item["id"] + '/' + item["id"] + '-' + item["version"] + ".zip").replace(' ', '%20')
                            iconimage   = (repoInfo [ "repo_datadir" ] + '/' + item["id"] + '/' + "icon.png").replace(' ', '%20') 
                        else:
                            downloadUrl = (repoInfo [ "repo_datadir" ] + '/' + item["id"] + '/').replace(' ', '%20') 
                            iconimage   = (repoInfo [ "repo_datadir" ] + '/' + item["id"] + '/' + "icon.png").replace(' ', '%20')
                            
                        print downloadUrl
                        paramsAddons = {}
                        paramsAddons[self.PARAM_INSTALL_FROM_REPO] = "true"
                        paramsAddons[self.PARAM_ADDON_NAME] = item['name'].encode('utf8')
                        paramsAddons[self.PARAM_URL] = downloadUrl
                        paramsAddons[self.PARAM_DATADIR] = repoInfo [ "repo_datadir" ]
                        paramsAddons[self.PARAM_TYPE] = repoInfo [ "repo_format" ]
                        paramsAddons[self.PARAM_REPO_ID] = repoId

                        url = self._create_param_url( paramsAddons )

                        if ( url ):
                            self._addLink( item['name'], url, iconimage=iconimage)
                            print "Link added"
                else:
                    keepParsing = False
        self._end_of_directory( True )
        
    def select( self ):
        """
        Decides what to do based on the plugin URL
        """
        try:
            print "select"
            print self.parameters
            if len(self.parameters) < 1:
                print "createRootDir"
                self.createRootDir()
                
            elif self.PARAM_INSTALL_FROM_REPO in self.parameters.keys():               
                # Install from remote repository
               
                #TODO: solve encoding pb on name
                
                addonName = unicode(self.parameters[self.PARAM_ADDON_NAME] , 'ISO 8859-1', errors='ignore') 
                addonUrl = self.parameters[self.PARAM_URL].replace(' ', '%20')
                addonFormat = self.parameters[self.PARAM_TYPE]
                repoId = self.parameters[self.PARAM_REPO_ID]
                dataDir = self.parameters[self.PARAM_DATADIR].replace(' ', '%20') #self.repoList[repoId]['datadir']
                status, itemName, destination, addonInstaller = self._install_from_repo(addonName, addonUrl, addonFormat, dataDir)
                
                # Check if install went well
                self._check_install(status, itemName, destination, addonInstaller)
                
                print "_end_of_directory"
                self._end_of_directory( True, update=False )
                
            elif self.PARAM_INSTALL_FROM_ZIP in self.parameters.keys():
                # Install from zip file
                status, itemName, destination, addonInstaller = self._install_from_zip()
                
                #Check if install went well
                self._check_install(status, itemName, destination, addonInstaller)
                
                print "_end_of_directory"
                self._end_of_directory( True, update=False )
                
            elif self.PARAM_LISTTYPE in self.parameters.keys() and self.VALUE_LIST_LOCAL_REPOS == self.parameters[self.PARAM_LISTTYPE]:
                print "List of available Add-ons repositories"
                #self.createRepoDir()
                self.createLocalRepoDir()

            elif self.PARAM_LISTTYPE in self.parameters.keys() and self.VALUE_LIST_CATEGORY == self.parameters[self.PARAM_LISTTYPE]:
                print "List of Add-ons' categories"
                repoId = self.parameters[self.PARAM_REPO_ID]
                #repo = self.repoList[repoId]

                self.createAddonCatDir(repoId)

            elif self.PARAM_LISTTYPE in self.parameters.keys() and self.VALUE_LIST_ADDONS == self.parameters[self.PARAM_LISTTYPE]:
                print "List of Add-ons"
                repoId = self.parameters[self.PARAM_REPO_ID]
                addonCat = self.parameters[self.PARAM_TYPE]
                #repo = self.repoList[repoId]

                self.createAddonsDir(repoId, addonCat)


            elif self.PARAM_LISTTYPE in self.parameters.keys():
                addon_type = self.parameters[self.PARAM_LISTTYPE]
                self.fileMgr = fileMgr()
                paramsDic = {}
                
                if addon_type in self.supportedAddonList:
                    print addon_type
                    listdir = self.fileMgr.listDirFiles( get_install_path( addon_type ) )
                    listdir.sort( key=str.lower )
                    for addon_dir  in listdir:
                        if TYPE_ADDON_SCRIPT in addon_dir:
                            addon_path    = os.path.join( get_install_path( addon_type ), addon_dir )
                            thumbnail_path = os.path.join( addon_path, "icon.png" )
                            if not os.path.exists(thumbnail_path):
                            #    thumbnail_path = get_thumb( self.curListType )
                                thumbnail_path = get_thumb( addon_type ) #"DefaultVideo.png"
                            #listItemObj = ListItemObject( type = addon_type, name = addon_dir, local_path = addon_path, thumb = thumbnail_path )
                            #self.currentItemList.append( listItemObj )
                            paramsDic[self.PARAM_TYPE]      = addon_type
                            paramsDic[self.PARAM_TITLE]     = addon_dir
                            paramsDic[self.PARAM_LOCALPATH] = addon_dir
                            
                            url = self._create_param_url( paramsDic )
                            if url:
                                self._addLink( addon_dir, url, iconimage=thumbnail_path )
                self._end_of_directory( True )
                    
            elif self.PARAM_TYPE in self.parameters.keys():
                print "Run addon"
                addon_type = self.parameters[self.PARAM_TYPE]
                addon_basename = self.parameters[self.PARAM_LOCALPATH]
                self._run_addon(addon_type, addon_basename)
                
                self._end_of_directory( True )

        

        except:
            print_exc()
            self._end_of_directory( False )


    def _parse_params( self ):
        """
        Parses Plugin parameters and returns it as a dictionary
        """
        paramDic={}
        # Parameters are on the 3rd arg passed to the script
        paramStr=sys.argv[2]
        if len(paramStr)>1:
            paramStr = paramStr.replace('?','')
            
            # Ignore last char if it is a '/'
            if (paramStr[len(paramStr)-1]=='/'):
                paramStr=paramStr[0:len(paramStr)-2]
                
            # Processing each parameter splited on  '&'   
            for param in paramStr.split("&"):
                try:
                    # Spliting couple key/value
                    key,value=param.split("=")
                except:
                    key=param
                    value=""
                    
                key = urllib.unquote_plus(key)
                value = urllib.unquote_plus(value)
                
                # Filling dictionnary
                paramDic[key]=value
        return paramDic        

    def _install_from_repo( self, addonName, addonUrl, addonFormat, repoUrl ):
        """
        Install an addon from a remote/web repository
        """
        status = "CANCELED"
        destination = None
        addonInstaller = None
        
        if ( xbmcgui.Dialog().yesno( addonName, __language__( 30050 ), "", "" ) ):
            # install from zip file
            if addonFormat == "zip":
                addonInstaller = RemoteArchiveInstaller.RemoteArchiveInstaller( addonName, addonUrl )
            else:
                # Remote dir installer
                addonInstaller = RemoteArchiveInstaller.RemoteDirInstaller( addonName, addonUrl, repoUrl )
            #dp = xbmcgui.DialogProgress()
            #dp.create(__language__( 137 ))
            dp = RecursiveDialogProgress(__language__( 137 ), __language__( 138 ))
            status, destination = addonInstaller.installItem( msgFunc=self.message_cb, progressBar=dp )
    
            dp.close()
            del dp
        return status, addonName, destination, addonInstaller

    def _install_from_zip(self):
        """
        Install an addon from a local zip file
        """        
        status = "CANCELED"
        destination = None
        addonInstaller = None
        
        dialog = xbmcgui.Dialog()
        zipPath = dialog.browse(1, 'XBMC', 'files', '', False, False, SPECIAL_HOME_DIR)
        itemName = os.path.basename(zipPath)
        print("_install_from_zip - installing %s"%zipPath)
        
        # install from zip file
        addonInstaller = LocalArchiveInstaller.LocalArchiveInstaller( zipPath )
        #dp = xbmcgui.DialogProgress()
        #dp.create(__language__( 137 ))
        dp = RecursiveDialogProgress(__language__( 137 ), __language__( 138 ))
        status, destination = addonInstaller.installItem( msgFunc=self.message_cb, progressBar=dp )

        dp.close()
        del dp
        return status, itemName, destination, addonInstaller

    def _check_install(self, status, itemName, destination, itemInstaller):
        """
        Check if install went well and if not ask the user what to do
        """
        # Default message: error
        title = __language__( 144 )
        msg1  = __language__( 144 )
        msg2  = ""
        loop = True
        # Get Item install name
        if itemInstaller:      
            itemInstallName = itemInstaller.getItemInstallName()
            
        try:
            while loop:
                if status == "OK":
                    #self._save_downloaded_property()
                    title = __language__( 141 )
                    #msg1  = _( 142 )%(unicode(itemName,'cp1252')) # should we manage only unicode instead of string?
                    msg1  = __language__( 142 )%itemName # should we manage only unicode instead of string?
                    #msg1  = _( 142 )%"" + itemName
                    msg2  = __language__( 143 )
                    loop = False
                elif status == "CANCELED":
                    title = __language__( 146 )
                    #msg1  = _( 147 )%(unicode(itemName,'cp1252'))
                    msg1  = __language__( 147 )%itemName
                    msg2  = ""
                    loop = False
                elif status == "ALREADYINSTALLED":
                    title = __language__( 144 )
                    #msg1  = _( 149 )%(unicode(itemName,'cp1252'))
                    msg1  = __language__( 149 )%itemName
                    msg2  = ""
                    if self._processOldInstall( itemInstaller ):
                        # Continue install
                        dp = xbmcgui.DialogProgress()
                        dp.create(__language__( 137 ))
                        status, destination = itemInstaller.installItem( msgFunc=self.message_cb, progressBar=dp )
                        dp.close()
                        del dp
                        #self._save_downloaded_property()
                        title = __language__( 141 )
                        msg1  = __language__( 142 )%itemName # should we manage only unicode instead of string?
                        #msg1  = __language__( 142 )%"" + itemName
                        msg2  = __language__( 143 )
                        if status == "OK":
                            loop = False                            
                    else:
                        #installCancelled = True
                        print "bypass: %s install has been cancelled by the user" % itemName
                        title = __language__( 146 )
                        msg1  = __language__( 147 )%itemName
                        msg2  = ""
                        loop = False
                        #dp = xbmcgui.DialogProgress()
                        #dp.create(__language__( 153 ))
                        #dp.update(100)
                        #dp.close()
                elif status == "INVALIDNAME":
                    keyboard = xbmc.Keyboard( itemInstallName, __language__( 154 ) )
                    keyboard.doModal()
                    if ( keyboard.isConfirmed() ):
                        inputText = keyboard.getText()
                        dp = xbmcgui.DialogProgress()
                        dp.create(__language__( 137 ))
                        status, destination = itemInstaller.installItem( itemName=inputText, msgFunc=self.message_cb, progressBar=dp )
                        dp.close()
                        if status == "OK":
                            title = __language__( 141 )
                            msg1  = __language__( 142 )%itemName # should we manage only unicode instead of string?
                            msg2  = __language__( 143 )
                            loop = False                            
                    del keyboard
                    
                elif status == "ALREADYINUSE":
                    print "%s currently used by XBMC, install impossible" % itemName
                    title = __language__( 117 )
                    msg1  = __language__( 117 )
                    msg2  = __language__( 119 )
                    loop = False                            
                else:
                    title = __language__( 144 )
                    msg1  = __language__( 136 )%itemName
                    msg2  = ""
                    loop = False                            
        #                else:
        #                    title = "Unknown Error"
        #                    msg1  = "Please check the logs"
        #                    msg2  = ""
                xbmcgui.Dialog().ok( title, msg1, msg2 )
        
            del itemInstaller

        except:
            print_exc()

        return status


    def _processOldInstall( self, itemInstaller ):
        """
        Traite les ancien download suivant les desirs de l'utilisateur
        retourne True si le download peut continuer.
        """
        continueInstall = True

        # Get Item install name
        if itemInstaller:      
            itemInstallName = itemInstaller.getItemInstallName()
            
            exit = False
            while exit == False:
                menuList = [ __language__( 150 ), __language__( 151 ), __language__( 152 ), __language__( 153 ) ]
                dialog = xbmcgui.Dialog()
                chosenIndex = dialog.select( __language__( 149 ) % itemInstallName, menuList )
                if chosenIndex == 0:
                    # Delete
                    print "Deleting:"
                    OK = itemInstaller.deleteInstalledItem()
                    if OK == True:
                        exit = True
                    else:
                        xbmcgui.Dialog().ok( __language__(148), __language__( 117) )
                elif chosenIndex == 1: 
                    # Rename
                    print "Renaming:"
                    #dp = xbmcgui.DialogProgress()
                    #dp.create(__language__( 157 ))
                    #dp.update(50)
                    keyboard = xbmc.Keyboard( itemInstallName, __language__( 154 ) )
                    keyboard.doModal()
                    if ( keyboard.isConfirmed() ):
                        inputText = keyboard.getText()
                        OK = itemInstaller.renameInstalledItem( inputText )
                        if OK == True:
                            xbmcgui.Dialog().ok( __language__( 155 ), inputText  )
                            exit = True
                        else:
                            xbmcgui.Dialog().ok( __language__( 148 ), __language__( 117 ) )
                            
                    del keyboard
                    #dp.close()
                elif chosenIndex == 2: 
                    # Overwrite
                    print "Overwriting:"
                    exit = True
                else:
                    # EXIT
                    exit = True
                    continueInstall = False
        else:
            continueInstall = False
        
        return continueInstall
        
    def _create_param_url(self, paramsDic):
        """
        Create an plugin URL based on the key/value passed in a dictionary
        """
        url = sys.argv[ 0 ]
        sep = '?'
        print paramsDic
        try:
            for param in paramsDic:
                #TODO: solve error on name with non ascii char (generate exception)
                url = url + sep + urllib.quote_plus( param ) + '=' + urllib.quote_plus( paramsDic[param] )
                sep = '&'
        except:
            url = None
            print_exc()
        return url

    def _get_settings( self ):
        self.settings = {}


    def _addLink( self, name, url, iconimage="DefaultProgram.png" ):
        ok=True
        print "_addLink"
        #TODO: reenable image downlaod, the checkURL freeze for whetever reason
        #if ( ( iconimage !="DefaultProgram.png" ) and ( not checkURL(iconimage) ) ):
        #    iconimage  = "DefaultProgram.png"
            
        print "Icon: %s"%iconimage
        liz=xbmcgui.ListItem( name, iconImage=iconimage, thumbnailImage=iconimage )
        print "List item created"
        liz.setInfo( type="Program", infoLabels={ "Title": name } )
        print "List item Set Info done"
        ok=xbmcplugin.addDirectoryItem( handle=int(sys.argv[1]), url=url, listitem=liz )
        print "Item added"
        return ok


    def _addLinkNew( self, itemInfo ):
        """
        Add a link to the list of items
        """
        ok=True
        
        print itemInfo
        
        if itemInfo["ImageUrl"]:
            icon = itemInfo["ImageUrl"]
        else:
            #icon = "DefaultFolder.png"
            #icon = "DefaultAddon.png"
            icon = os.path.join(MEDIA_PATH, "DefaultAddonRepository.png")
        
        descriptColor = self.colorList[ int( __settings__.getSetting( "descolor" ) ) ]
        
        if self.shortTitleDisplay:
            labelTxt = itemInfo["name"]
        else:
            labelTxt = itemInfo["name"] + ": " + self._coloring( itemInfo["description"], descriptColor ) 
        liz=xbmcgui.ListItem( label=labelTxt, iconImage=icon, thumbnailImage=icon )
        liz.setInfo( type="addons", 
                     infoLabels={ "title": itemInfo["name"], "Plot": itemInfo["description"] } )
        liz.setProperty("Addon.Name",itemInfo["name"])
        liz.setProperty("Addon.Version"," ")
        liz.setProperty("Addon.Summary", "")
        liz.setProperty("Addon.Description", itemInfo["description"])
        liz.setProperty("Addon.Type", __language__( 30011 ))
        liz.setProperty("Addon.Creator", itemInfo["owner"])
        liz.setProperty("Addon.Disclaimer","")
        liz.setProperty("Addon.Changelog", "")
        liz.setProperty("Addon.ID", "")
        liz.setProperty("Addon.Status", "Stable")
        liz.setProperty("Addon.Broken", "Stable")
        liz.setProperty("Addon.Path","")
        liz.setProperty("Addon.Icon",icon)
           
        paramsMenu = {}
        paramsMenu[self.PARAM_NAME] = itemInfo["name"]
        paramsMenu[self.PARAM_ACTION] = self.VALUE_DISPLAY_INFO
        urlMenu = self._create_param_url( paramsMenu )
        if urlMenu:
            c_items = [ ( __language__( 30012 ), "XBMC.RunPlugin(%s)" % ( urlMenu)) ]
            liz.addContextMenuItems( c_items )
        params = {}
        params[self.PARAM_NAME] = itemInfo["name"]
        params[self.PARAM_ACTION] = self.VALUE_INSTALL_FROM_ZIP
        params[self.PARAM_URL] = itemInfo["repoUrl"]
        urlRepo = self._create_param_url( params )
        if urlRepo:
            ok=xbmcplugin.addDirectoryItem( handle=int(sys.argv[1]), url=urlRepo, listitem=liz, isFolder=False  )
        return ok
    

    #def _addDir( self, name, url, mode, iconimage="DefaultFolder.png", c_items = None ):
    def _addDir( self, name, url, iconimage="DefaultFolder.png", c_items = None ):
        """
        Credit to ppic
        """
        print name
        print url
        print iconimage
        #u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        ok=True
        liz=xbmcgui.ListItem( name, iconImage=iconimage, thumbnailImage=iconimage )
        if c_items : 
            liz.addContextMenuItems( c_items, replaceItems=True )
        liz.setInfo( type="Program", infoLabels={ "Title": name } )
        ok=xbmcplugin.addDirectoryItem( handle=int( sys.argv[1] ), url=url, listitem=liz, isFolder=True )
        return ok

    
    def _end_of_directory( self, OK, update=False ):
        xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=OK, updateListing=update )#, cacheToDisc=True )#updateListing = True,

    def _add_sort_methods( self, OK ):
        if ( OK ):
            try:
                xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_VIDEO_TITLE )
                xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_DATE )
                #xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE )
                xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_GENRE )
                #xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_VIDEO_RUNTIME )
                #xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_STUDIO )
            except:
                print_exc()
        self._end_of_directory( OK )
    
    def _coloring( self, text , color , colorword ):
        if color == "red": color="FFFF0000"
        if color == "green": color="ff00FF00"
        if color == "yellow": color="ffFFFF00"
        colored_text = text.replace( colorword , "[COLOR=%s]%s[/COLOR]" % ( color , colorword ) )
        return colored_text

    def _isSupported( self, type ):
        """
        Returns if type of this addon is supported by the installer
        """
        if type in self.supportedAddonList:
            result = True
        else:
            result = False
        return result

    def _run_addon( self, type, addon_basename ):
        """
        """
        print "_run_addon"
        print type
        print addon_basename
        result = True
        if ( type == TYPE_ADDON_VIDEO ):
            #command = "XBMC.ActivateWindow(10025,plugin://addons/%s/)" % ( addon_basename, )
            #command = "RunPlugin(%s)" % ( os.path.join( get_install_path( type ), addon_basename ))
            command = "XBMC.ActivateWindow(10025,%s/)" % ( os.path.join( get_install_path( type ), addon_basename) )
            
        elif ( type == TYPE_ADDON_MUSIC ):
            command = "XBMC.ActivateWindow(10502,plugin://addons/%s/)" % ( addon_basename, )
        elif ( type == TYPE_ADDON_PROGRAMS ):
            command = "XBMC.ActivateWindow(10001,plugin://addons/%s/)" % ( addon_basename, )
        elif ( type == TYPE_ADDON_PICTURES ):
            command = "XBMC.ActivateWindow(10002,plugin://addons/%s/)" % ( addon_basename, )
        elif ( type == TYPE_ADDON_SCRIPT ):
            command = "XBMC.RunScript(%s)" % ( os.path.join( get_install_path( type ), addon_basename, "default.py" ), )

        try:
            xbmc.executebuiltin( command )
        except:
            print_exc()
            result = False
        return result
    
    def message_cb(self, msgType, title, message1, message2="", message3=""):
        """
        Callback function for sending a message to the UI
        @param msgType: Type of the message
        @param title: Title of the message
        @param message1: Message part 1
        @param message2: Message part 2
        @param message3: Message part 3
        """
        #print("message_cb with %s STARTS"%msgType)
        result = None

        # Display the correct dialogBox according the type
        if msgType == "OK" or msgType == "Error":
            dialogInfo = xbmcgui.Dialog()
            result = dialogInfo.ok(title, message1, message2,message3)
        elif msgType == "YESNO":
            dialogYesNo = xbmcgui.Dialog()
            result = dialogYesNo.yesno(title, message1, message2, message3)
        return result

    #===========================================================================
    # def updateProgress_cb( self, percent, dp=None ):
    #    """
    #    Met a jour la barre de progression
    #    """
    #    #TODO Dans le futur, veut t'on donner la responsabilite a cette fonction le calcul du pourcentage????
    #    try:
    #        dp.update( percent )
    #    except:
    #        percent = 100
    #        dp.update( percent )        
    #===========================================================================
#######################################################################################################################    
# BEGIN !
#######################################################################################################################

if ( __name__ == "__main__" ):
    try:
        Addons4xboxInstallerPlugin()
    except:
        print_exc()
