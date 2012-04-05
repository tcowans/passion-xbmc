# -*- coding: cp1252 -*-
"""
   Repository Installer Addon (plugin type) allowing to find and install addon repositories for XBMC
   
   Changelog:
   
   03-21-2011 Version 1.0.3 by Temhil
      - Added Repository info window
      - Set default title display option without description
      
   03-17-2011 Version 1.0.2 by Temhil
      - Added option to add or not description from title
      - Added option for activating or not color of description (set it by default)
      - Removed Bold Title
      
   03-15-2011 Version 1.0.1 by Temhil
      - Added Icon (thank to Willynuisance)
      - Added settings allowing to change color of description
      
   03-13-2011 Version 1.0.0 by Temhil and Frost
      - Creation  (installation part based on Frost work with script.addon.installer)
"""

REMOTE_DBG       = False # For remote debugging with PyDev (Eclipse)


__script__       = "Unknown"
__plugin__       = "Repositories Installer"
__addonID__      = "plugin.program.repo.installer"
__author__       = "Temhil and Frost (http://passion-xbmc.org)"
__url__          = "http://passion-xbmc.org/index.php"
__svn_url__      = "http://passion-xbmc.googlecode.com/svn/trunk/addons/plugin.program.repository.installer/"
__credits__      = "Team XBMC Passion"
__platform__     = "xbmc media center"
__date__         = "03-21-2011"
__version__      = "1.0.3"
__svn_revision__ = 0


import os
import re
import urllib
from traceback import print_exc

# xbmc modules
import xbmc
import xbmcgui
import xbmcplugin
from xbmcaddon import Addon


 
ADDON     = Addon( __addonID__ )
Language  = ADDON.getLocalizedString
ADDON_DIR = ADDON.getAddonInfo( "path" )
LangXBMC  = xbmc.getLocalizedString


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


ROOTDIR            = ADDON_DIR
BASE_RESOURCE_PATH = os.path.join( ROOTDIR, "resources" )
MEDIA_PATH         = os.path.join( BASE_RESOURCE_PATH, "media" )
ADDON_DATA  = xbmc.translatePath( "special://profile/addon_data/%s/" % __addonID__ )
REPO_LIST_URL = "http://wiki.xbmc.org/index.php?title=Unofficial_Add-on_Repositories"
REPO_PACKAGE_DIR = "special://home/addons/packages/"
REPO_INSTALL_DIR = "special://home/addons/"

DIALOG_PROGRESS = xbmcgui.DialogProgress()

#modules custom
try:
    import resources.lib.wikiparser as wikiparser
except:
    print_exc()


def getIdAndVersion( a ):
    ID, VER = os.path.splitext( a )[ 0 ], ""
    match = re.search( "(.+?)-(\d+.\d+.\d+).", a )
    if match: ID, VER = match.groups()

    return ID, VER


class RepoInstallerPlugin:
    """
    main plugin class
    """
    # define param key names
    PARAM_NAME              = 'name'
    PARAM_ACTION            = 'action'
    PARAM_URL               = 'url'
    VALUE_INSTALL_FROM_ZIP  = 'installfromzip'
    VALUE_INSTALL_FROM_REPO = 'installfromrepo'
    VALUE_INSTALL_ALL       = 'installfromzip'
    VALUE_DISPLAY_INFO      = 'displayinfo'

    # Constant
    colorList = ["red", "green", "yellow", "lightblue", None]
    debugMode = False
    shortTitleDisplay = False


    def __init__( self, *args, **kwargs ):
        
        # Parse plugin parameters
        self.parameters = self._parse_params()
       
        # Check settings
        #if ( ADDON.getSetting('first_run') == 'true' ):
        #    #xbmcplugin.openSettings(sys.argv[0])
        #else:
        #    self.select()
        self._set_title_display()
        self.select()


    def create_root_dir ( self ):
        print "createRootDir"
        xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category=Language( 30001 ) )
        print "Loading wiki page: %s"%REPO_LIST_URL
        wikiparser.getRepoList(REPO_LIST_URL, addItemFunc=self._addLink, progressBar=None,  msgFunc=None )
        self._add_sort_methods( True )
        self._end_of_directory( True )

        
    def install_repo(self, repoName, repoURL):
        """
        Install a repository in XBMC
        -> will need XBMC restart in order to have the new Repo taken in account by XBMC
        """
        continueInstall = True
        dialogYesNo = xbmcgui.Dialog()
        if dialogYesNo.yesno(repoName, Language( 30100 ), Language( 30101 )):           
            if continueInstall:
                ri = RepoInstaller()
                    
                newRepo = ri.download( repoURL )
                print newRepo
        
                if newRepo:
                    fp, ok = ri.install( newRepo )
                    print "---"
                    print fp, ok
                    xbmc.executebuiltin( 'UpdateLocalAddons' )
                    xbmc.sleep( 100 )
                    xbmc.executebuiltin( 'UpdateAddonRepos' )
                    xbmc.sleep( 100 )
                    try:
                        _N_ = Addon( os.path.basename( fp ) )
                        print "Addon %s Installed"%s_N_
                        ri.notification( _N_.getAddonInfo( "name" ), Language( 24065 ).encode( "utf-8" ), 5000, _N_.getAddonInfo( "icon" ) )
                    except:
                        xbmcgui.Dialog().ok( ADDON.getAddonInfo( "name" ), Language( 30007 ) + " : " + repoName, Language( 30010 ) )
        self._end_of_directory( True, update=False )
        

        
    def select( self ):
        try:
            print "select"
            print self.parameters
            if len(self.parameters) < 1:
                self.create_root_dir()
                
            elif self.PARAM_ACTION in self.parameters.keys():
                if self.parameters[self.PARAM_ACTION] == self.VALUE_INSTALL_FROM_ZIP:
                    repoName = self.parameters[self.PARAM_NAME]
                    repoURL  = self.parameters[self.PARAM_URL]
                    #print repoName
                    #print repoURL
                    #xbmc.executebuiltin('XBMC.ActivateWindow(146)')
                    #xbmc.executebuiltin( "Action(Info)")
                    
                    self.install_repo(repoName, repoURL)
                elif self.parameters[self.PARAM_ACTION] == self.VALUE_DISPLAY_INFO:
                    try:
                        from resources.lib.DialogRepoInfo import DialogRepoInfo
                        repoWindow = DialogRepoInfo( "DialogRepoInfo.xml", ADDON_DIR )
                        del repoWindow
                    except:
                        print_exc()
                    self._end_of_directory( False )
            else:   
                self._end_of_directory( True, update=False )

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
        print paramStr
        if len(paramStr)>1:
            paramStr = paramStr.replace('?','')
            
            # Ignore last char if it is a '/'
            if (paramStr[len(paramStr)-1]=='/'):
                paramStr=paramStr[0:len(paramStr)-2]
                
            # Processing each parameter splited on  '&'   
            for param in paramStr.split("&"):
                try:
                    # Splitting couple key/value
                    key,value=param.split("=")
                except:
                    key=param
                    value=""
                    
                key = urllib.unquote_plus(key)
                value = urllib.unquote_plus(value)
                
                # Filling dictionary
                paramDic[key]=value
        print paramDic
        return paramDic        


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

    def _set_title_display(self):
        descriptInTitle =ADDON.getSetting('desintitle')
        if descriptInTitle == 'true':
            self.shortTitleDisplay = False
        else:
            self.shortTitleDisplay = True
        
    def _addLink( self, itemInfo ):
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
        
        descriptColor = self.colorList[ int( ADDON.getSetting( "descolor" ) ) ]
        
        if self.shortTitleDisplay:
            labelTxt = itemInfo["name"]
        else:
            labelTxt = itemInfo["name"] + ": " + self._coloring( itemInfo["description"], descriptColor ) 
        liz=xbmcgui.ListItem( label=labelTxt, iconImage="DefaultAddonRepository.png", thumbnailImage=icon )

        ID, VER = getIdAndVersion( os.path.basename( itemInfo["repoUrl"] ) )
        playCount = xbmc.getCondVisibility( "System.HasAddon(%s)" % ID )
        overlay = ( xbmcgui.ICON_OVERLAY_NONE, xbmcgui.ICON_OVERLAY_WATCHED )[ playCount ]
        Status = ( "", LangXBMC( 305 ) )[ playCount ]
        infoLabels = {
            "title": itemInfo["name"],
            "Plot": itemInfo["description"],
            "playCount": playCount,
            "overlay": overlay,
            }
        liz.setInfo( "video", infoLabels )

        liz.setProperty("Addon.Name",itemInfo["name"])
        liz.setProperty("Addon.Version",VER)
        liz.setProperty("Addon.Summary", "")
        liz.setProperty("Addon.Description", itemInfo["description"])
        liz.setProperty("Addon.Type", Language( 30011 ))
        liz.setProperty("Addon.Creator", itemInfo["owner"])
        liz.setProperty("Addon.Disclaimer","")
        liz.setProperty("Addon.Changelog", "")
        liz.setProperty("Addon.ID", ID)
        liz.setProperty("Addon.Status", Status)
        liz.setProperty("Addon.Broken", "")
        liz.setProperty("Addon.Path","")
        liz.setProperty("Addon.Icon",icon)
           
        
        
        #dirItem.addContextMenuItem( self.Addon.getLocalizedString( 30900 ), "XBMC.RunPlugin(%s?showtimes=%s)" % ( sys.argv[ 0 ], urllib.quote_plus( repr( video[ "title" ] ) ), ) )
        paramsMenu = {}
        paramsMenu[self.PARAM_NAME] = itemInfo["name"]
        paramsMenu[self.PARAM_ACTION] = self.VALUE_DISPLAY_INFO
        urlMenu = self._create_param_url( paramsMenu )
        if urlMenu:
            c_items = [ ( Language( 30012 ), "XBMC.RunPlugin(%s)" % ( urlMenu)) ]
            liz.addContextMenuItems( c_items )
        params = {}
        params[self.PARAM_NAME] = itemInfo["name"]
        params[self.PARAM_ACTION] = self.VALUE_INSTALL_FROM_ZIP
        params[self.PARAM_URL] = itemInfo["repoUrl"]
        urlRepo = self._create_param_url( params )
        if urlRepo:
            ok=xbmcplugin.addDirectoryItem( handle=int(sys.argv[1]), url=urlRepo, listitem=liz, isFolder=False  )
        return ok

    def _set_content( self, OK, content="addons" ):
        if ( OK ):
            xbmcplugin.setContent( int( sys.argv[ 1 ] ), content )
    
    def _end_of_directory( self, OK, update=False ):
        xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=OK, updateListing=update )#, cacheToDisc=True )#updateListing = True,

    def _add_sort_methods( self, OK ):
        self._set_content( OK )
        if ( OK ):
            try:
                xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_UNSORTED )
                xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_LABEL )
            except:
                print_exc()
    
    def _coloring( self, text , color  ):
        if color:
            if color == "red": color="FFFF0000"
            if color == "green": color="FF00FF00"
            if color == "yellow": color="FFFFFF00"
            if color == "lightblue": color="FFB1C7EC"
            colored_text = "[COLOR=%s]%s[/COLOR]" % ( color , text )
        else:
            colored_text = text
        return colored_text

    def _bold_text( self, text ):
        """ FONCTION POUR METTRE UN MOT GRAS """
        return "[B]%s[/B]" % ( text, )
    


class RepoInstaller:
    """
    main plugin class
    """
    def download( self, url, destination=REPO_PACKAGE_DIR ):
        try:
            DIALOG_PROGRESS.create( ADDON.getAddonInfo( "name" ) )
            destination = xbmc.translatePath( destination ) + os.path.basename( url )
            def _report_hook( count, blocksize, totalsize ):
                percent = int( float( count * blocksize * 100 ) / totalsize )
                DIALOG_PROGRESS.update( percent, Language( 30005 ) % url,  Language( 30006 ) % destination )
            fp, h = urllib.urlretrieve( url, destination, _report_hook )
            print fp, h
            return fp
        except:
            print_exc()
        DIALOG_PROGRESS.close()
        return ""
    
    
    def install( self, filename ):
        from resources.lib.extractor import extract
        return extract( filename, xbmc.translatePath( REPO_INSTALL_DIR ) )
    
    
    def notification( self, header="", message="", sleep=5000, icon=ADDON.getAddonInfo( "icon" ) ):
        """ Will display a notification dialog with the specified header and message,
            in addition you can set the length of time it displays in milliseconds and a icon image. 
        """
        xbmc.executebuiltin( "XBMC.Notification(%s,%s,%i,%s)" % ( header, message, sleep, icon ) )


#######################################################################################################################    
# BEGIN !
#######################################################################################################################

if ( __name__ == "__main__" ):
    try:
        RepoInstallerPlugin()
    except:
        print_exc()
