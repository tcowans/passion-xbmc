"""
   Simulating xbmcaddon library for XBox
"""

REMOTE_DBG       = False 


# Plugin constants
__script__       = "Unknown"
__plugin__       = "Addons4Xbox Installer"
#__author__       = authorUI + " and " + authorCore
__author__       = "Frost & Temhil (http://passion-xbmc.org)"
__url__          = "http://passion-xbmc.org/index.php"
__svn_url__      = "http://passion-xbmc.googlecode.com/svn/trunk/plugins/programs/Addons4xbox/"
__credits__      = "Team XBMC Passion"
__platform__     = "xbmc media center"
__date__         = "08-11-2010"
__version__      = "0.1"
__svn_revision__ = 0


import os
import urllib
#import xbmc
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



ROOTDIR = os.getcwd()
BASE_RESOURCE_PATH = os.path.join( ROOTDIR, "resources" )
LIBS               = os.path.join( BASE_RESOURCE_PATH, "libs" )

__platform__ = "xbmc media center, [%s]" % xbmc.__platform__
__language__ = xbmc.Language( ROOTDIR ).getLocalizedString

# append the proper libs folder to our path
sys.path.append( LIBS )

#modules custom
try:
    from specialpath import *
    from Item import *
    from FileManager import *
    import LocalArchiveInstaller #,ItemInstaller
    import RemoteArchiveInstaller
    from utilities import copy_dir, copy_inside_dir, readURL
    from XmlParser import ListItemFromXML
except:
    print_exc()



class Addons4xboxInstallerPlugin:
    """
    main plugin class
    """
    # define param key names
    PARAM_TITLE = "title"
    PARAM_TYPE = 'type'
    PARAM_LISTTYPE = 'listype'
    PARAM_LOCALPATH = 'localpath'
    PARAM_INSTALL_FROM_ZIP  = 'installfromzip'
    PARAM_INSTALL_FROM_REPO = 'installfromrepo'
    PARAM_REPO_ID = 'repoid'
    PARAM_REPO_NAME = 'reponame'
    PARAM_ADDON_NAME = 'addonname'
    PARAM_URL = 'url'
    PARAM_REPO_FORMAT = 'format'
    VALUE_LIST_CATEGORY = 'listcataddon'
    VALUE_LIST_LOCAL_REPOS = 'listlocalrepos'
    VALUE_LIST_ALL_ADDONS = 'alladdons'
    VALUE_LIST_ADDONS = 'listaddons'

    supportedAddonList = [ TYPE_ADDON_SCRIPT,
                           TYPE_ADDON_MUSIC,
                           TYPE_ADDON_PICTURES,
                           TYPE_ADDON_PROGRAMS,
                           TYPE_ADDON_VIDEO,
                           TYPE_ADDON_MODULE,
                           TYPE_ADDON_REPO ]
                           
    repoList = [
                 {'id': "xbmc.addon.repository", 'name': "Official XBMC.org Add-on Repository", 'url': "http://mirrors.xbmc.org/addons/dharma-pre/addons.xml", 'format': "zip", 'datadir': "http://mirrors.xbmc.org/addons/dharma-pre"},
                 {'id': "repository.googlecode.xbmc-addons", 'name': "Passion-XBMC Add-on Repository", 'url': "http://passion-xbmc.org/addons/addons.php", 'format': "zip", 'datadir': "http://passion-xbmc.org/addons/Download.php"}
               ]
    

    def __init__( self, *args, **kwargs ):
        self._get_settings()
        self.parameters = self._parse_params()

        #TODO: if 1st start create missing dir
        self.fileMgr = fileMgr()
        #self.fileMgr.verifrep( get_install_path( TYPE_ADDON ) )
        self.fileMgr.verifrep( DIR_ADDON_MODULE )
        
        # Check settings
        if ( xbmcplugin.getSetting('first_run') == 'true' ):
            #xbmcplugin.openSettings(sys.argv[0])
            print "First run of Addons Installer Plugin, ckeling if Addon Libraries are installed"
            self.installLibs()
        else:
            try:
                import xbmcaddon
                #TODO: add import on each module or none
                #dialog = xbmcgui.Dialog()
                #dialog.ok( __language__(30000), __language__(30002) )
                print "XBMC Addon 4 XBOX Addon Library already installed"
                xbmcplugin.setSetting('first_run','false')
                self.select()
            except ImportError:
                self.installLibs()

        def installLibs(self):
            try:
                dialog = xbmcgui.Dialog()
                if ( dialog.ok( __language__(30021), __language__(30003) ) ):
                    # Install XBMC Addons librairies
                    #lib_xbmcaddon = "special://xbmc/system/python/Lib/xbmcaddon.py"
                    lib_source = os.path.join( ROOTDIR, "resources", "script.modules" )
                    dialogProg = xbmcgui.DialogProgress()
                    dialogProg.create( __language__( 30000 ) ) 
                    dialogProg.update(0, __language__ ( 30001 ) )
                    #try: os.mkdirs( "special://xbmc/system/python/Lib" )
                    #except: pass
                    try:
                        #xbmc.executehttpapi( "FileCopy(%s,%s)" % ( lib_source, lib_xbmcaddon ) )
                        if os.path.exists( lib_source ):
                            copy_dir( lib_source, DIR_ADDON_MODULE )
                            xbmcplugin.setSetting('first_run','false')
                            self.select()
                        else:
                            dialogProg.close()
                            dialog = xbmcgui.Dialog()
                            dialog.ok( __language__(30000), __language__(30006), __language__(30007) )
                            print "ERROR: impossible to copy xbmc addon librairies"
                            print "Librairies are missing in the plugin structure"
                        
                        dialogProg.update(100, __language__ ( 30001 ) )
                        dialogProg.close()
                        dialog = xbmcgui.Dialog()
                        dialog.ok( __language__(30000), __language__(30005) )
                        print "SUCCESS: xbmcaddon.py copied to special://xbmc/system/python/Lib/xbmcaddon.py"
                    except:
                        dialogProg.close()
                        dialog = xbmcgui.Dialog()
                        dialog.ok( __language__(30000), __language__(30006), __language__(30007) )
                        print "ERROR: impossible to copy xbmcaddon.py to special://xbmc/system/python/Lib/xbmcaddon.py"
                        print_exc()
                else:
                    dialog = xbmcgui.Dialog()
                    dialog.ok( __language__(30000), __language__(30004) )
            except:
                print_exc()
 

    def createRootDir ( self ):
        paramsDicZip = {}
        paramsDicZip[self.PARAM_INSTALL_FROM_ZIP] = "true"
        urlZip = self._create_param_url( paramsDicZip )
        self._addLink( __language__( 30203 ), urlZip )
        
        paramsDicRepo = {}
        paramsDicRepo[self.PARAM_LISTTYPE] = self.VALUE_LIST_LOCAL_REPOS
        urlRepo = self._create_param_url( paramsDicRepo )
        self._addDir( __language__( 30204 ), urlRepo )
        
        self._end_of_directory( True )

    def createRepoDir ( self ):
        for repo in self.repoList:
            print repo
            paramsRepo = {}
            #paramsRepo[self.PARAM_REPO_ID] = repo[self.PARAM_REPO_ID]
            paramsRepo[self.PARAM_REPO_ID] = str(self.repoList.index(repo))
            paramsRepo[self.PARAM_LISTTYPE] = self.VALUE_LIST_CATEGORY
            urlRepo = self._create_param_url( paramsRepo )
            self._addDir( repo['name'], urlRepo )
        self._end_of_directory( True )


    def createAddonCatDir ( self, repoId ):
        params = {}
        params[self.PARAM_REPO_ID] = str(repoId)
        params[self.PARAM_LISTTYPE] = self.VALUE_LIST_ADDONS
        params[self.PARAM_TYPE] = self.VALUE_LIST_ALL_ADDONS
        url = self._create_param_url( params )
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
        self._addDir( __language__( 30102 ), url )        
        
        params = {}
        params[self.PARAM_REPO_ID] = str(repoId)
        params[self.PARAM_LISTTYPE] = self.VALUE_LIST_ADDONS
        params[self.PARAM_TYPE] = TYPE_ADDON_PICTURES
        url = self._create_param_url( params )
        self._addDir( __language__( 30103 ), url )        
        
        params = {}
        params[self.PARAM_REPO_ID] = str(repoId)
        params[self.PARAM_LISTTYPE] = self.VALUE_LIST_ADDONS
        params[self.PARAM_TYPE] = TYPE_ADDON_PROGRAMS
        url = self._create_param_url( params )
        self._addDir( __language__( 30104 ), url )        
        
        params = {}
        params[self.PARAM_REPO_ID] = str(repoId)
        params[self.PARAM_LISTTYPE] = self.VALUE_LIST_ADDONS
        params[self.PARAM_TYPE] = TYPE_ADDON_VIDEO
        url = self._create_param_url( params )
        self._addDir( __language__( 30105 ), url )        
        
        params = {}
        params[self.PARAM_REPO_ID] = str(repoId)
        params[self.PARAM_LISTTYPE] = self.VALUE_LIST_ADDONS
        params[self.PARAM_TYPE] = TYPE_ADDON_MODULE
        url = self._create_param_url( params )
        self._addDir( __language__( 30108 ), url )        
        
        
        # for addonType in self.supportedAddonList:
            
            # paramsDic[self.PARAM_LISTTYPE] = addonType
            # #paramsDic[self.PARAM_TYPE] = addonType
            # url = self._create_param_url( paramsDic )
            # print url
            # self._addDir( get_type_title( addonType ), url )
           
        self._end_of_directory( True )

    def createAddonsDir ( self, repoId, cat ):
        # Retrieving addons.xml from repository
        xmlInfofPath = os.path.join( DIR_CACHE, "addons.xml")
        #xmlData = readURL( self.repoList[repoId]['url'], save=True, localPath=xmlInfofPath )
        data = readURL( self.repoList[repoId]['url'], save=True, localPath=xmlInfofPath )
        if ( os.path.exists( xmlInfofPath ) ):
            xmlData = open( os.path.join( xmlInfofPath ), "r" )
    
            listAddonsXml = ListItemFromXML(xmlData)
            
            filter = "False"
            if cat == self.VALUE_LIST_ALL_ADDONS:
                filter = "item['type'] in self.supportedAddonList"
            elif cat == TYPE_ADDON_SCRIPT:
                filter = "item['type'] == TYPE_ADDON_SCRIPT"
            elif cat == TYPE_ADDON_MUSIC:
                filter = "item['type'] == TYPE_ADDON_MUSIC"
            elif cat == TYPE_ADDON_PICTURES:
                filter = "item['type'] == TYPE_ADDON_PICTURES"
            elif cat == TYPE_ADDON_PROGRAMS:
                filter = "item['type'] == TYPE_ADDON_PROGRAMS"
            elif cat == TYPE_ADDON_VIDEO:
                filter = "item['type'] == TYPE_ADDON_VIDEO"
            elif cat == TYPE_ADDON_MODULE:
                filter = "item['type'] == TYPE_ADDON_MODULE"

            keepParsing = True
            while (keepParsing):
                item = listAddonsXml.getNextItem()
                print item
                if item:
                    if eval(filter):
                        downloadUrl = self.repoList[repoId]['datadir'] + '/' + item["id"] + '/' + item["id"] + '-' + item["version"] + ".zip"
                        print downloadUrl
                        paramsAddons = {}
                        paramsAddons[self.PARAM_INSTALL_FROM_REPO] = "true"
                        paramsAddons[self.PARAM_ADDON_NAME] = item['name']
                        paramsAddons[self.PARAM_URL] = downloadUrl
                        paramsAddons[self.PARAM_TYPE] = self.repoList[repoId]['format']
                        url = self._create_param_url( paramsAddons )
                        self._addLink( item['name'], url)
                else:
                    keepParsing = False
        self._end_of_directory( True )
        
    def select( self ):
        try:
            print "select"
            print self.parameters
            if len(self.parameters) < 1:
                print "createRootDir"
                self.createRootDir()
                
            elif self.PARAM_INSTALL_FROM_REPO in self.parameters.keys():
                
                # Install from remote repository
                #TODO: solve encoding pb on name
                #addonName = self.parameters[self.PARAM_ADDON_NAME]
                addonName = unicode(self.parameters[self.PARAM_ADDON_NAME] , 'ISO 8859-1', errors='ignore') 
                addonUrl = self.parameters[self.PARAM_URL].replace(' ', '%20')
                addonFormat = self.parameters[self.PARAM_TYPE]
                status, itemName, destination, addonInstaller = self._install_from_repo(addonName, addonUrl, addonFormat)
                
                #Check if install went well
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
                self.createRepoDir()

            elif self.PARAM_LISTTYPE in self.parameters.keys() and self.VALUE_LIST_CATEGORY == self.parameters[self.PARAM_LISTTYPE]:
                print "List of Add-ons' categories"
                repoId = self.parameters[self.PARAM_REPO_ID]
                #repo = self.repoList[repoId]

                self.createAddonCatDir(repoId)

            elif self.PARAM_LISTTYPE in self.parameters.keys() and self.VALUE_LIST_ADDONS == self.parameters[self.PARAM_LISTTYPE]:
                print "List of Add-ons"
                repoId = int(self.parameters[self.PARAM_REPO_ID])
                addonCat = self.parameters[self.PARAM_TYPE]
                #repo = self.repoList[repoId]

                self.createAddonsDir(repoId, addonCat)


            elif self.PARAM_LISTTYPE in self.parameters.keys():
                addon_type = self.parameters[self.PARAM_LISTTYPE]
                self.fileMgr = fileMgr()
                paramsDic = {}
                if TYPE_ADDON == addon_type:
                    print addon_type
                    
                    listdir = self.fileMgr.listDirFiles( get_install_path( addon_type ) )
                    listdir.sort( key=str.lower )
                    for addon_dir  in listdir:
                        if TYPE_ADDON_SCRIPT in addon_dir:
                            real_addon_type = TYPE_ADDON_SCRIPT
                        elif TYPE_ADDON_MUSIC in addon_dir:
                            real_addon_type = TYPE_ADDON_MUSIC
                        elif TYPE_ADDON_PICTURES in addon_dir:
                            real_addon_type = TYPE_ADDON_PICTURES
                        elif TYPE_ADDON_PROGRAMS in addon_dir:
                            real_addon_type = TYPE_ADDON_PROGRAMS
                        elif TYPE_ADDON_VIDEO in addon_dir:
                            real_addon_type = TYPE_ADDON_VIDEO
                        else:
                            real_addon_type = addon_type
                        addon_path    = os.path.join( get_install_path( real_addon_type ), addon_dir )
                        thumbnail_path = os.path.join( addon_path, "icon.png" )
                        if not os.path.exists(thumbnail_path):
                        #    thumbnail_path = get_thumb( self.curListType )
                            thumbnail_path = "DefaultVideo.png"
                        #listItemObj = ListItemObject( type = addon_type, name = addon_dir, local_path = addon_path, thumb = thumbnail_path )
                        #self.currentItemList.append( listItemObj )
                        paramsDic[self.PARAM_TYPE]      = real_addon_type
                        paramsDic[self.PARAM_TITLE]     = addon_dir
                        paramsDic[self.PARAM_LOCALPATH] = addon_dir
                        
                        url = self._create_param_url( paramsDic )
                        self._addLink( addon_dir, url, iconimage=thumbnail_path )
                    self._end_of_directory( True )
                        
                elif TYPE_ADDON_SCRIPT == addon_type:
                    print addon_type
                    listdir = self.fileMgr.listDirFiles( get_install_path( addon_type ) )
                    listdir.sort( key=str.lower )
                    for addon_dir  in listdir:
                        if TYPE_ADDON_SCRIPT in addon_dir:
                            addon_path    = os.path.join( get_install_path( addon_type ), addon_dir )
                            thumbnail_path = os.path.join( addon_path, "icon.png" )
                            if not os.path.exists(thumbnail_path):
                            #    thumbnail_path = get_thumb( self.curListType )
                                thumbnail_path = "DefaultVideo.png"
                            #listItemObj = ListItemObject( type = addon_type, name = addon_dir, local_path = addon_path, thumb = thumbnail_path )
                            #self.currentItemList.append( listItemObj )
                            paramsDic[self.PARAM_TYPE]           = addon_type
                            paramsDic[self.PARAM_TITLE]     = addon_dir
                            paramsDic[self.PARAM_LOCALPATH] = addon_dir
                            
                            url = self._create_param_url( paramsDic )
                            self._addLink( addon_dir, url, iconimage=thumbnail_path )
                    self._end_of_directory( True )

                elif TYPE_ADDON_MUSIC == addon_type:
                    print addon_type
                    listdir = self.fileMgr.listDirFiles( get_install_path( addon_type ) )
                    listdir.sort( key=str.lower )
                    for addon_dir  in listdir:
                        if TYPE_ADDON_MUSIC in addon_dir:
                            addon_path    = os.path.join( get_install_path( addon_type ), addon_dir )
                            thumbnail_path = os.path.join( addon_path, "icon.png" )
                            if not os.path.exists(thumbnail_path):
                            #    thumbnail_path = get_thumb( self.curListType )
                                thumbnail_path = "DefaultVideo.png"
                            #listItemObj = ListItemObject( type = addon_type, name = addon_dir, local_path = addon_path, thumb = thumbnail_path )
                            #self.currentItemList.append( listItemObj )
                            paramsDic[self.PARAM_TYPE]           = addon_type
                            paramsDic[self.PARAM_TITLE]     = addon_dir
                            paramsDic[self.PARAM_LOCALPATH] = addon_dir

                            url = self._create_param_url( paramsDic )
                            self._addLink( addon_dir, url, iconimage=thumbnail_path )
                    self._end_of_directory( True )

                elif TYPE_ADDON_PICTURES == addon_type:
                    print addon_type
                    listdir = self.fileMgr.listDirFiles( get_install_path( addon_type ) )
                    listdir.sort( key=str.lower )
                    for addon_dir  in listdir:
                        if TYPE_ADDON_PICTURES in addon_dir:
                            addon_path    = os.path.join( get_install_path( addon_type ), addon_dir )
                            thumbnail_path = os.path.join( addon_path, "icon.png" )
                            if not os.path.exists(thumbnail_path):
                            #    thumbnail_path = get_thumb( self.curListType )
                                thumbnail_path = "DefaultVideo.png"
                            #listItemObj = ListItemObject( type = addon_type, name = addon_dir, local_path = addon_path, thumb = thumbnail_path )
                            #self.currentItemList.append( listItemObj )
                            paramsDic[self.PARAM_TYPE]           = addon_type
                            paramsDic[self.PARAM_TITLE]     = addon_dir
                            paramsDic[self.PARAM_LOCALPATH] = addon_dir

                            url = self._create_param_url( paramsDic )
                            self._addLink( addon_dir, url, iconimage=thumbnail_path )
                    self._end_of_directory( True )

                elif TYPE_ADDON_PROGRAMS == addon_type:
                    print addon_type
                    listdir = self.fileMgr.listDirFiles( get_install_path( addon_type ) )
                    listdir.sort( key=str.lower )
                    for addon_dir  in listdir:
                        if TYPE_ADDON_PROGRAMS in addon_dir:
                            addon_path    = os.path.join( get_install_path( addon_type ), addon_dir )
                            thumbnail_path = os.path.join( addon_path, "icon.png" )
                            if not os.path.exists(thumbnail_path):
                            #    thumbnail_path = get_thumb( self.curListType )
                                thumbnail_path = "DefaultVideo.png"
                            #listItemObj = ListItemObject( type = addon_type, name = addon_dir, local_path = addon_path, thumb = thumbnail_path )
                            #self.currentItemList.append( listItemObj )
                            paramsDic[self.PARAM_TYPE]           = addon_type
                            paramsDic[self.PARAM_TITLE]     = addon_dir
                            paramsDic[self.PARAM_LOCALPATH] = addon_dir

                            url = self._create_param_url( paramsDic )
                            self._addLink( addon_dir, url, iconimage=thumbnail_path )
                    self._end_of_directory( True )

                elif TYPE_ADDON_VIDEO == addon_type:
                    print addon_type
                    listdir = self.fileMgr.listDirFiles( get_install_path( addon_type ) )
                    listdir.sort( key=str.lower )
                    for addon_dir  in listdir:
                        if TYPE_ADDON_VIDEO in addon_dir:
                            addon_path    = os.path.join( get_install_path( addon_type ), addon_dir )
                            thumbnail_path = os.path.join( addon_path, "icon.png" )
                            if not os.path.exists(thumbnail_path):
                            #    thumbnail_path = get_thumb( self.curListType )
                                thumbnail_path = "DefaultVideo.png"
                            #listItemObj = ListItemObject( type = addon_type, name = addon_dir, local_path = addon_path, thumb = thumbnail_path )
                            #self.currentItemList.append( listItemObj )
                            paramsDic[self.PARAM_TYPE]           = addon_type
                            paramsDic[self.PARAM_TITLE]     = addon_dir
                            paramsDic[self.PARAM_LOCALPATH] = addon_dir

                            url = self._create_param_url( paramsDic )
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

    def _install_from_repo( self, addonName, addonUrl, addonFormat ):
        
        # install from zip file
        if addonFormat == "zip":
            addonInstaller = RemoteArchiveInstaller.RemoteArchiveInstaller( addonName, addonUrl )
        else:
            # Remote dir installer
            raise
        dp = xbmcgui.DialogProgress()
        dp.create(__language__( 137 ))
        status, destination = addonInstaller.installItem( msgFunc=self.message_cb, progressBar=dp )

        dp.close()
        del dp
        return status, addonName, destination, addonInstaller

    def _install_from_zip(self):
        dialog = xbmcgui.Dialog()
        zipPath = dialog.browse(1, 'XBMC', 'files', '', False, False, SPECIAL_HOME_DIR)
        print("installing %s"%zipPath)
        
        itemName = os.path.basename(zipPath)
        # install from zip file
        addonInstaller = LocalArchiveInstaller.LocalArchiveInstaller( zipPath )
        dp = xbmcgui.DialogProgress()
        dp.create(__language__( 137 ))
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

        try:
            if status == "OK":
                #self._save_downloaded_property()
                title = __language__( 141 )
                #msg1  = _( 142 )%(unicode(itemName,'cp1252')) # should we manage only unicode instead of string?
                msg1  = __language__( 142 )%itemName # should we manage only unicode instead of string?
                #msg1  = _( 142 )%"" + itemName
                msg2  = __language__( 143 )
            elif status == "CANCELED":
                title = __language__( 146 )
                #msg1  = _( 147 )%(unicode(itemName,'cp1252'))
                msg1  = __language__( 147 )%itemName
                msg2  = ""
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
                else:
                    #installCancelled = True
                    print "bypass: %s install has been cancelled by the user" % itemName
                    title = __language__( 146 )
                    msg1  = __language__( 147 )%itemName
                    msg2  = ""
                    #dp = xbmcgui.DialogProgress()
                    #dp.create(__language__( 153 ))
                    #dp.update(100)
                    #dp.close()
            elif status == "ALREADYINUSE":
                print "%s currently used by XBMC, install impossible" % itemName
                title = __language__( 117 )
                msg1  = __language__( 117 )
                msg2  = __language__( 119 )
            else:
                title = __language__( 144 )
                msg1  = __language__( 136 )%itemName
                msg2  = ""
    #                else:
    #                    title = "Unknown Error"
    #                    msg1  = "Please check the logs"
    #                    msg2  = ""
    
            del itemInstaller
        except:
            print_exc()

        xbmcgui.Dialog().ok( title, msg1, msg2 )


    def _processOldInstall( self, itemInstaller ):
        """
        Traite les ancien download suivant les desirs de l'utilisateur
        retourne True si le download peut continuer.
        """

#        from FileManager import fileMgr
#        fileMgr = fileMgr()

        continueInstall = True

        # Get Item install name
        itemInstallName = itemInstaller.getItemInstallName()
        
        # Verifie se on telecharge un repertoire ou d'un fichier
#        if os.path.isdir( localAbsDirPath ):
#            # Repertoire
        exit = False
        while exit == False:
            menuList = [ __language__( 150 ), __language__( 151 ), __language__( 152 ), __language__( 153 ) ]
            dialog = xbmcgui.Dialog()
            #chosenIndex = dialog.select( __language__( 149 ) % os.path.basename( localAbsDirPath ), menuList )
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
        return continueInstall
        
    def _create_param_url(self, paramsDic):
        """
        Create an plugin URL based on the key/value passed in a dictionary
        """
        url = sys.argv[ 0 ]
        sep = '?'
        print paramsDic
        for param in paramsDic:
            url = url + sep + urllib.quote_plus( param ) + '=' + urllib.quote_plus( paramsDic[param] )
            sep = '&'
        return url

    def _get_settings( self ):
        self.settings = {}


    def _addLink( self, name, url, iconimage="DefaultVideo.png" ):
        ok=True
        liz=xbmcgui.ListItem( name, iconImage=iconimage, thumbnailImage=iconimage )
        liz.setInfo( type="Program", infoLabels={ "Title": name } )
        ok=xbmcplugin.addDirectoryItem( handle=int(sys.argv[1]), url=url, listitem=liz )
        return ok

    

    #def _addDir( self, name, url, mode, iconimage="DefaultFolder.png", c_items = None ):
    def _addDir( self, name, url, iconimage="DefaultFolder.png", c_items = None ):
        """
        Credit to ppic
        """
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

#######################################################################################################################    
# BEGIN !
#######################################################################################################################


try:
    Addons4xboxInstallerPlugin()
except:
    print_exc()
