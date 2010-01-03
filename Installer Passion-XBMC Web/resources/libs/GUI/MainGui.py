
# Modules general
import os
import md5
import sys
import urllib

from traceback import print_exc
from threading import Thread, Timer

# Modules XBMC
import xbmc
import xbmcgui

# Modules custom
from utilities import *
from info_item import ItemInfosManager
from XbmcZoneBrowser import XbmcZoneBrowser
from PassionFtpBrowser import PassionFtpBrowser
from PassionHttpBrowser import PassionHttpBrowser


SPECIAL_SCRIPT_DATA = sys.modules[ "__main__" ].SPECIAL_SCRIPT_DATA

#FONCTION POUR RECUPERER LES LABELS DE LA LANGUE.
_ = sys.modules[ "__main__" ].__language__

DIALOG_PROGRESS = xbmcgui.DialogProgress()

# GET ACTIONCODES FROM KEYMAP.XML
#ACTION_MOVE_LEFT      = 1
#ACTION_MOVE_RIGHT     = 2
#ACTION_MOVE_UP        = 3
#ACTION_MOVE_DOWN      = 4
#ACTION_PAGE_UP        = 5
#ACTION_PAGE_DOWN      = 6
#ACTION_SELECT_ITEM    = 7
#ACTION_HIGHLIGHT_ITEM = 8
ACTION_PARENT_DIR      = 9
ACTION_PREVIOUS_MENU   = 10
ACTION_SHOW_INFO       = 11
#ACTION_PAUSE          = 12
#ACTION_STOP           = 13
#ACTION_NEXT_ITEM      = 14
#ACTION_PREV_ITEM      = 15
ACTION_CONTEXT_MENU    = 117
CLOSE_CONTEXT_MENU     = ( ACTION_PARENT_DIR, ACTION_PREVIOUS_MENU, ACTION_CONTEXT_MENU, )


class Source:
    """
    Defines a source (Browser) used by the installer
    """
    def __init__( self, sourceName, className, instanceName=None, created=False ):
        self.sourceName   = sourceName    # Name of the source
        self.className    = className     # Browser class name for this source
        self.instanceName = instanceName  # Browser instance name
        self.created      = created       # flag set to True when a Browser instance has been created otherwise set to False

    def __repr__( self ):
        return "Source ( sourceName: %s, className: %s, instanceName: %s, created: %s )" % ( self.sourceName, self.className, self.instanceName, self.created )


class Context:
    """
    Context class, allows to retrieve browsers
    """
    def __init__( self ):
        self.curSource = None # Current selected Browser
        #self.listOfSources = []
        self.listOfSources = {}
        self.listOfSrCName = [] #Temporary #TODO use dict
        try:
            # Creating sources (not instanciating Browsers here)
            srcPassionHttp = Source( "Passion XBMC Web", PassionHttpBrowser )
            srcPassionFtp  = Source( "Passion XBMC FTP", PassionFtpBrowser )
            srcXbmcZone    = Source( "XBMC Zone", XbmcZoneBrowser )
            self.addSource(srcPassionHttp)
            self.addSource(srcPassionFtp)
            self.addSource(srcXbmcZone)
        except Exception, e:
            #print "Exception during Context init"
            #print e
            #print sys.exc_info()
            print_exc()
            print_exc()

    def selectSource( self, sourceName ):
        """
        Set a source as the current one
        """
        #TODO use string as param
        self.curSource = self.listOfSources[sourceName]
        
    def getBrowser( self ):
        """
        Returns Browser instance for the current source
        """
        if self.curSource.created == False:
            # Create Browser instance for the 1st time
            self.createBrowser( self.curSource )
        return self.curSource.instanceName

    def getSourceName( self ):
        """
        Returns current source's name
        """
        return self.curSource.sourceName
    
    def addSource(self, sourceItem):
        """
        Adds a new source
        """
        #self.listOfSources.append(sourceItem)
        self.listOfSources[sourceItem.sourceName] = sourceItem
        self.listOfSrCName.append(sourceItem.sourceName)
        
    def createBrowser( self, source ):
        """
        Instanciates the browser for a specific source
        """
        # Create instance name form class name
        instance = "browser_" + source.className.__name__
        
        # Create instance and update source information
        #exec("%s = %s"%( source.instanceName, source.className()))
        exec("%s = %s"%( instance, "source.className()"))
        exec("source.instanceName  = %s"%( instance ))
        source.created = True
        
    def getSourceNameList( self ):
        """
        Returns the list of the source's name
        """
        return self.listOfSrCName
    
    def freeSources(self):
        """
        Free all the source (close the browser: closing connection ...) in order to exit properly 
        """
        print "Context: freeing sources"
        for srcName in self.listOfSrCName:
            print "freing %s ..."%(srcName)
            try:
                print self.listOfSources[srcName]
                if self.listOfSources[srcName].created:
                    self.listOfSources[srcName].instanceName.close()
            except Exception, e:
                print "Exception during freeSources in Context"
                print_exc()


class MainWindow( xbmcgui.WindowXML ):
    # control id's
    CONTROL_MAIN_LIST_START = 50
    CONTROL_MAIN_LIST_END   = 59
    CONTROL_SOURCE_LIST     = 150
    CONTROL_FORUM_BUTTON    = 305
    CONTROL_FILE_MGR_BUTTON = 300
    CONTROL_OPTIONS_BUTTON  = 310
    CONTROL_EXIT_BUTTON     = 320
    CONTROL_SHOW_SPLASH_IMG = 999

    def __init__( self, *args, **kwargs ):
        """
        Initialisation de l'interface
        """
        xbmcgui.WindowXML.__init__( self, *args, **kwargs )
        self.HomeAction = kwargs.get( "HomeAction" )
        self.main_list_last_pos = []

        # Display Loading Window while we are loading the information from the website
        if xbmc.getCondVisibility( "Window.IsActive(progressdialog)" ):
            #si le dialog PROGRESS est visible update
            DIALOG_PROGRESS.update( -1, _( 103 ), _( 110 ) )
        else:
            #si le dialog PROGRESS n'est pas visible affiche le dialog
            DIALOG_PROGRESS.create( _( 0 ), _( 103 ), _( 110 ) )
        #DIALOG_PROGRESS.close()

        #TODO: TOUTES ces varibales devraient etre passees en parametre du constructeur de la classe ( __init__ si tu preferes )
        # On ne devraient pas utiliser de variables globale ou rarement en prog objet

        # Creation du configCtrl
        from CONF import configCtrl
        self.configManager = configCtrl()
        if not self.configManager.is_conf_valid: raise

        self.rssfeed            = self.configManager.rssfeed
        self.curDirList         = []
        self.index              = 0
        self.scraperDir         = self.configManager.scraperDir
        self.type               = "racine"
        self.USRPath            = self.configManager.USRPath
        self.rightstest         = ""
        self.CacheDir           = self.configManager.CACHEDIR
        self.userDataDir        = self.configManager.userdatadir # userdata directory
        self.targetDir          = ""

        # Verifie si le repertoire cacher existe et le cree s'il n'existent pas encore
        if os.path.exists( self.CacheDir ):
            # Si le repertoire cache existe on s'assure de le vider ( au cas ou on ne serait pas sorti proprement du script )
            self.delDirContent( self.CacheDir )
        else:
            self.verifrep( self.CacheDir )
        self.verifrep( self.configManager.pluginProgDir )

        # Change permission on Linux platform
        if SYSTEM_PLATFORM == "linux":
            self.linux_chmod( self.scraperDir )
        
#        #TODO: A nettoyer, ton PMIIIDir n'est pas defini pour XBOX sans le test si dessous
#        if self.USRPath == True:
#            self.PMIIIDir = self.configManager.PMIIIDir

        self.is_started = True
        # utiliser pour remettre la liste courante a jour lorsqu'on reviens sur cette fenetre depuis le forum ou le manager
        self.listitems = []
        self.current_cat = ""

    def onInit( self ):
        try:
            self._get_settings()
            self._set_skin_colours()

            # desactive le splash
            try: self.getControl( self.CONTROL_SHOW_SPLASH_IMG ).setVisible( 0 )
            except: pass
    #        if self.settings.get( "show_plash" ) == True:
    #            # splash desactive par le user
    #            self.getControl( self.CONTROL_SHOW_SPLASH_IMG ).setVisible( 0 )

            if self.is_started:
                self.is_started = False

                self._start_rss_timer()

                # Connection au serveur FTP
                try:
                    DIALOG_PROGRESS.update( -1, _( 104 ), _( 110 ) )
                    if self.HomeAction and "default_content" in self.HomeAction:
                        self.default_content = self.HomeAction.split( "=" )[ 1 ]
                    else:
                        self.default_content = "Passion XBMC Web"
                    # Loading context
                    self.contextSrc = Context()
                    self.contextSrc.selectSource( self.default_content )#"XBMC Zone" )
                    #self.browser = self.contextSrc.getBrowser()

                    self.set_list_container_150()


                    #print "Updating displayed list"
                    self.updateData_Next()
                    self.updateList()
                    #print "End of update for the displayed list

                except:
                    xbmcgui.Dialog().ok( _( 111 ), _( 112 ) )
                    print "Window::__init__: Exception durant la connection FTP"
                    print "Impossible de se connecter au serveur FTP: %s" % self.host
                    print_exc()

                # Title of the current pages
                self.setProperty( "Category", _( 10 ) )
                self.setProperty( "DlSource", self.default_content )
                xbmc.executebuiltin( "Container.SetViewMode(%i)" % self.settings.get( "main_view_mode", self.CONTROL_MAIN_LIST_START ) )



                # Close the Loading Window
                DIALOG_PROGRESS.close()
                if self.HomeAction and self.HomeAction.startswith( "self." ):
                    exec self.HomeAction
            else:
                # pas le choix avec les nouvelles vue, mais on lui joue un tour avec une listitems deja ready :P
                if xbmc.getCondVisibility( "Window.IsActive(IPX-Installer.xml)" ) or xbmc.getCondVisibility( "Window.IsActive(passion-main.xml)" ):
                    if self.listitems: self.re_updateList()
                    else: self.updateList()
                # .addItems( items=listitems )
                # print "self.addItems( items= )", hasattr( self, 'addItems' )
                # for ControlList only :(

            # desactive le splash
            try: self.getControl( self.CONTROL_SHOW_SPLASH_IMG ).setVisible( 0 )
            except: pass
        except:
            print_exc()

    def _get_settings( self, defaults=False ):
        """ reads settings """
        self.settings = Settings().get_settings( defaults=defaults )
        try:
            self.getControl( self.CONTROL_FORUM_BUTTON ).setVisible( not self.settings.get( "hide_forum", False ) )
        except Exception, e:
            if not "Non-Existent Control" in str( e ):
                print_exc()

    def _set_skin_colours( self ):
        #xbmcgui.lock()
        try:
            xbmc.executebuiltin( "Skin.SetString(PassionSkinColourPath,%s)" % ( self.settings[ "skin_colours_path" ], ) )
            xbmc.executebuiltin( "Skin.SetString(PassionSkinHexColour,%s)" % ( ( self.settings[ "skin_colours" ] or get_default_hex_color() ), ) )
        except:
            xbmc.executebuiltin( "Skin.SetString(PassionSkinHexColour,ffffffff)" )
            xbmc.executebuiltin( "Skin.SetString(PassionSkinColourPath,default)" )
            print_exc()
        #xbmcgui.unlock()

    def _start_rss_timer( self ):
        # temps entre chaque mise a jour du flux rss 15 min.
        self.rss_update_interval = 60.0 * 15.0
        self.rss_title = ""
        self._stop_rss_timer()
        if self.settings[ "rss_feed" ] != "0":
            try:
                rss_feeds_xml = parse_rss_xml().get( self.settings[ "rss_feed" ] )
                self.rss_update_interval = 60.0 * rss_feeds_xml.get( "updateinterval", 15 )
                self.rss_title = rss_feeds_xml.get( "title", self.rss_title )
                self.rssfeed = rss_feeds_xml.get( "feed", self.rssfeed )
            except:
                print_exc()
            self.rss_thread = Thread( target=self._set_control_rss_feed )
            self.rss_thread.start()
        else:
            try: self.getControl( 100 ).setVisible( False )
            except: pass

    def _stop_rss_timer( self ):
        try: self.rss_timer.cancel()
        except: pass
        try: self.rss_thread.cancel()
        except: pass

    def _set_control_rss_feed( self ):
        #test fadelabel for rssfeed in Thread
        import RSSParser
        try:
            title_color = repr( self.getControl( 101 ).getLabel() ).strip( "u'" )
            text_color  = repr( self.getControl( 101 ).getLabel2() ).strip( "u'" )
            #print repr( title_color ), repr( text_color )
            self.rss_feed = RSSParser.rssReader( self.rss_title, self.rssfeed, title_color, text_color ).GetRssInfo()[ 1 ]
        except Exception, e:
            if not "Non-Existent Control" in str( e ):
                print_exc()
            try:
                self.rss_feed = RSSParser.rssReader( self.rss_title, self.rssfeed ).GetRssInfo()[ 1 ]
            except:
                print_exc()
        del RSSParser
        try:
            self.getControl( 100 ).reset()
            self.getControl( 100 ).addLabel( self.rss_feed )
            self.getControl( 100 ).setVisible( True )
        except Exception, e:
            if not "Non-Existent Control" in str( e ):
                print_exc()
            try: self.getControl( 100 ).setVisible( False )
            except: pass
            self._stop_rss_timer()
        else:
            try:
                self.rss_timer = Timer( self.rss_update_interval, self._set_control_rss_feed, () )
                self.rss_timer.start()
            except:
                print_exc()

    def _show_descript( self ):
        try:
            #TODO: modify DialogItemDescription in order to use DB instead of XML
            # Affiche la description de l'item selectionner
            currentListIndex = self.getCurrentListPosition()
            #if ( ( not self.browser.isCat( currentListIndex ) ) and ( self.CONTROL_MAIN_LIST_START <= self.getFocusId() <= self.CONTROL_MAIN_LIST_END ) ):
            if ( self.CONTROL_MAIN_LIST_START <= self.getFocusId() <= self.CONTROL_MAIN_LIST_END ):
                if currentListIndex >= 0:
                    import DialogItemDescription
                    reload( DialogItemDescription )
                    DialogItemDescription.show_description( self )
                    del DialogItemDescription
        except:
            print_exc()

    def _show_settings( self ):
        try:
            self.HomeAction = None
            thumb_size_on_load = self.settings[ "thumb_size" ]
            import DialogSettings
            DialogSettings.show_settings( self )
            #on a plus besoin du settings, on le delete
            del DialogSettings
            if thumb_size_on_load != self.settings[ "thumb_size" ]:
                self.updateList() #on raffraichit la page pour afficher la taille des vignettes
        except:
            print_exc()

    def _show_direct_infos( self ):
        try:
            self.HomeAction = None
            import ForumDirectInfos
            ForumDirectInfos.show_direct_infos()
            #on a plus besoin, on le delete
            del ForumDirectInfos
        except:
            print_exc()

    def _show_file_manager( self, args=None ):
        try:
            self.HomeAction = None
            thumb_size_on_load = self.settings[ "thumb_size" ]
            import FileManagerGui
            mainfunctions = [ self._show_settings, self._close_script ]
            FileManagerGui.show_file_manager( mainfunctions, self.rightstest, args )
            #on a plus besoin du manager, on le delete
            del FileManagerGui
            if thumb_size_on_load != self.settings[ "thumb_size" ]:
                self.updateList() #on raffraichit la page pour afficher la taille des vignettes
        except:
            print_exc()

    def get_view_mode( self ):
        view_mode = ""
        for id in range( self.CONTROL_MAIN_LIST_START, self.CONTROL_MAIN_LIST_END + 1 ):
            try:
                if xbmc.getCondVisibility( "Control.IsVisible(%i)" % id ):
                    view_mode = repr( id )
                    return view_mode
                    break
            except:
                pass
        return view_mode

    def _show_context_menu( self ):
        try:
            if ( not self.current_cat.lower() in [ "root", "racine", "plugins", _( 10 ).lower() ] ) and ( self.CONTROL_MAIN_LIST_START <= self.getFocusId() <= self.CONTROL_MAIN_LIST_END ):#( self.getFocusId() == self.CONTROL_MAIN_LIST ):
                import DialogContextMenu
                #buttons = { 1000 : ( "teste 1", "disabled" ), 1001 : "teste 2", 1002 : "teste 3",
                #    1003 : "teste 4", 1004 : ( "teste 5", "disabled" ), 1005 : "teste 6", 1006 : "teste 7" }
                buttons = { 1000: _( 1000 ), 1001: _( 1001 ), 1002: _( 184 ), 1003: _( 1002 ) }
                selected = DialogContextMenu.show_context_menu( buttons, self.get_view_mode() )
                del DialogContextMenu
                if selected == 1000:
                    #installe add-ons
                    self.install_add_ons()
                elif selected == 1001:
                    self._show_descript()
                elif selected == 1002:
                    self.refresh_item()
                elif selected == 1003:
                    self._switch_media()
                else:
                    pass
        except:
            print_exc()
            #print_exc()

    def _switch_media( self ):
        #TODO: adpat implementation to multisources
        try:
            import DialogContextMenu
            buttons = { 1000: _( 11 ), 1001: _( 12 ), 1002: _( 13 ), 1003: _( 14 ),
                1004: _( 18 ), 1005: _( 16 ), 1006: _( 15 ), 1007: _( 17 ) }
            selected = DialogContextMenu.show_context_menu( buttons, self.get_view_mode() )
            del DialogContextMenu
            switch = None
            if selected == 1000:
                switch = "Themes"
                self.index = 0
            elif selected == 1001:
                switch = "Scrapers"
                self.index = 1
            elif selected == 1002:
                switch = "Scripts"
                self.index = 2
            elif selected == 1003:
                switch = "Plugins"
                self.index = 3
            elif selected == 1004:
                switch = "Plugins Videos"
                self.index = 3
            elif selected == 1005:
                switch = "Plugins Images"
                self.index = 1
            elif selected == 1006:
                switch = "Plugins Musique"
                self.index = 0
            elif selected == 1007:
                switch = "Plugins Programmes"
                self.index = 2
            if switch:
                self.type = switch
                self.index = self.index
                self.updateList() #on raffraichit la page pour afficher le contenu
        except:
            print_exc()

    def set_list_container_150( self ):
        #list_container = sorted( self.list_container_150.items(), key=lambda id: id[ 0 ] )
        #self.rss_id = [ rss[ 0 ] for rss in list_container ]
        try:
            label2 = ""#not used
            icone = "windows.png"
            #for key, value in list_container:
            self.listOfSourceName = self.contextSrc.getSourceNameList()
            #print "set_list_container_150"
            for source in self.listOfSourceName:
                #label1 = source['title']
                label1 = source
                #print label1
                #displayListItem = xbmcgui.ListItem( "test", "", iconImage=icone, thumbnailImage=icone )
                #self.getControl( 150 ).addItem( displayListItem )
                self.getControl( self.CONTROL_SOURCE_LIST ).addItem( xbmcgui.ListItem( label1, label1, icone, icone ) )
            self.getControl( self.CONTROL_SOURCE_LIST ).setVisible( True )
        except Exception, e:
            if not "Non-Existent Control" in str( e ):
                print_exc()

    def onAction( self, action ):
        """
        Remonte l'arborescence et quitte le script
        """
        try:
            if action == ACTION_PREVIOUS_MENU:
                # Sortie du script
                print "exiting script"
                self.onExit()

            elif action == ACTION_PARENT_DIR:
                #print "ACTION_PARENT_DIR"
                # remonte l'arborescence
                if not self.main_list_last_pos:
                    try: self.main_list_last_pos.append( self.getCurrentListPosition() )
                    except: self.main_list_last_pos.append( 0 )
                try:
                    # Get data and update display
                    self.updateData_Prev()
                    self.updateList()
                except:
                    print "Window::onAction::ACTION_PREVIOUS_MENU: Exception durant updateList()"
                    print_exc()

                if self.main_list_last_pos:
                    self.setCurrentListPosition( self.main_list_last_pos.pop() )

            elif action == ACTION_SHOW_INFO:
                 #print "_show_descript - ItemDescription"
                 self._show_descript()

            elif action == ACTION_CONTEXT_MENU:
                self._show_context_menu()

            else:
                pass

        except:
            print "Window::onAction: Exception"
            print_exc()

    def install_add_ons( self ):
        """
        installation de l'item selectionner
        """
        # Default message: error
        title = _( 144 )
        msg1  = _( 136 )%(unicode(itemName,'cp1252'))
        msg2  = ""

        try:
            # Get the installer Object who now how to do the job (depending on the source)
            itemName = self.curDirList[self.index]['name']
            if not xbmcgui.Dialog().yesno( _( 180 ), _( 181 ), itemName ): return
            
            itemInstaller = self.contextSrc.getBrowser().getInstaller(self.index)

            if itemInstaller != None:
                #print "Download via itemInstaller"
                dp = xbmcgui.DialogProgress()
                dp.create(_( 137 ))
                #status, destination = itemInstaller.installItem( msgFunc=self.message_cb, progressBar=dp )
                status, destination = itemInstaller.installItem( msgFunc=self.message_cb, progressBar=dp )
    
                dp.close()
                del dp
    
                #Check if install went well
                #print itemName
                #print repr(itemName)
                if status == "OK":
                    self._save_downloaded_property()
                    title = _( 141 )
                    msg1  = _( 142 )%(unicode(itemName,'cp1252')) # should we manage only unicode instead of string?
                    #msg1  = _( 142 )%"" + itemName
                    msg2  = _( 143 )
                elif status == "CANCELED":
                    title = _( 146 )
                    msg1  = _( 147 )%(unicode(itemName,'cp1252'))
                    msg2  = ""
                elif status == "ALREADYINSTALLED":
                    title = _( 144 )
                    msg1  = _( 149 )%(unicode(itemName,'cp1252'))
                    msg2  = ""
                    #if self.processOldDownload( destination ):
                    if self.processOldDownload( itemInstaller ):
                        # Continue install
                        dp = xbmcgui.DialogProgress()
                        dp.create(_( 137 ))
                        status, destination = itemInstaller.installItem( msgFunc=self.message_cb, progressBar=dp )
                        dp.close()
                        del dp
                        self._save_downloaded_property()
                        title = _( 141 )
                        msg1  = _( 142 )%(unicode(itemName,'cp1252')) # should we manage only unicode instead of string?
                        #msg1  = _( 142 )%"" + itemName
                        msg2  = _( 143 )
                    else:
                        installCancelled = True
                        print "bypass: %s install has been cancelled by the user" % itemName
                        title = _( 146 )
                        msg1  = _( 147 )%(unicode(itemName,'cp1252'))
                        msg2  = ""
                else:
                    title = _( 144 )
                    msg1  = _( 136 )%(unicode(itemName,'cp1252'))
                    msg2  = ""
                del itemInstaller
            else:
                # No installer available
                print "No installer available for %s - Install impossible" % itemName
                #TODO: create string for this particular case i.e: Install not supported for this type of item
                title = _( 144 )
                msg1  = _( 136 )%(unicode(itemName,'cp1252'))
                msg2  = ""
            
        except:
            print_exc()

        xbmcgui.Dialog().ok( title, msg1, msg2 )

    def _close_script( self ):
        #**IMPORTANT** faut annuler les thread avant de fermer le script, sinon xbmc risque de planter
        #NB: le meme scenario va ce produire si vous fermer ou redemarrer xbmc avec le script en marche
        #on annule les thread
        self._stop_rss_timer()
#        try: self.infoswarehouse.getImage_thread.cancel()
#        except: pass
#        try: self.infoswarehouse.cancel_update_Images()
#        except: pass
        for id in range( self.CONTROL_MAIN_LIST_START, self.CONTROL_MAIN_LIST_END + 1 ):
            try:
                if xbmc.getCondVisibility( "Control.IsVisible(%i)" % id ):
                    self.settings[ "main_view_mode" ] = id
                    Settings().save_settings( self.settings )
                    break
            except:
                pass
        #on ferme le script
        self.close()

    def onFocus( self, controlID ):
        #self.controlID = controlID
        #cette fonction n'est pas utiliser ici, mais dans les XML si besoin
        #Note: Mais il faut la declarer : )
        pass

    def onClick( self, controlID ):
        """
        Traitement si selection d'un element de la liste
        """
        try:
            if ( self.CONTROL_MAIN_LIST_START <= controlID <= self.CONTROL_MAIN_LIST_END ):
                self.index = self.getCurrentListPosition()
                if self.contextSrc.getBrowser().isCat(self.getCurrentListPosition()):
                    try: self.main_list_last_pos.append( self.getCurrentListPosition() )
                    except: self.main_list_last_pos.append( 0 )
                    
                    # Get data and update display
                    self.updateData_Next()
                    self.updateList()
    
                    #TODO: case of install an item
                else:
                    #print "Download and install case"
                    self.install_add_ons()

            elif controlID in [ 201, 202, 203, self.CONTROL_SOURCE_LIST ]:
                new_content = None
                if controlID == self.CONTROL_SOURCE_LIST:
                    #index = self.getControl( self.CONTROL_SOURCE_LIST ).getCurrentListPosition()
                    #sourceName = self.listOfSourceName[index]
                    new_contentt = self.getControl( self.CONTROL_SOURCE_LIST ).getSelectedItem().getLabel()
                elif controlID == 201:
                    new_content = "Passion XBMC Web"
                elif controlID == 202:
                    new_content = "Passion XBMC FTP"
                elif controlID == 203:
                    new_content = "XBMC Zone"
                if new_content is not None:
                    self.default_content = new_content
                    self.contextSrc.selectSource( self.default_content )
                    #self.browser = self.contextSrc.getBrowser()
                    #print "Updating displayed list on NEW SOURCE: %s"%sourceName
                    self.updateData_Next()
                    self.updateList()

            elif controlID == self.CONTROL_OPTIONS_BUTTON:
                self._show_settings()

            elif controlID == self.CONTROL_FILE_MGR_BUTTON:
                self._show_file_manager()

            elif controlID == self.CONTROL_FORUM_BUTTON:
                self._show_direct_infos()

            elif controlID == self.CONTROL_EXIT_BUTTON:
                #self._close_script()
                self.onExit()

            else:
                pass

        except Exception, e:
            #print "Exception during onClick"
            #print e
            #print sys.exc_info()
            print_exc()
            print_exc()

    def onExit( self ):
        """
        Action done on exit of the application
        """
        try:
            # Free all the sources
            # self.browser.close()
            self.contextSrc.freeSources()
        except:
            print_exc()
        try:
            # Delete cache directory
            self.deleteDir( self.CacheDir )
        except:
            print_exc()

        # Closing everything
        self._close_script()

    def _load_downloaded_property( self ):
        self.downloaded_property = set()
        try:
            file_path = os.path.join( SPECIAL_SCRIPT_DATA, "downloaded.txt" )
            if os.path.exists( file_path ):
                self.downloaded_property = eval( file( file_path, "r" ).read() )
        except:
            print_exc()

    def _save_downloaded_property( self ):
        try:
            self._load_downloaded_property()
            selected_label = self.getListItem( self.getCurrentListPosition() ).getLabel()
            self.downloaded_property.update( [ md5.new( selected_label ).hexdigest() ] )
            file_path = os.path.join( SPECIAL_SCRIPT_DATA, "downloaded.txt" )
            file( file_path, "w" ).write( repr( self.downloaded_property ) )
        except:
            print_exc()
        else:
            self.getListItem( self.getCurrentListPosition() ).setProperty( "Downloaded", "isDownloaded" )

    def updateProgress_cb( self, percent, dp=None ):
        """
        Met a jour la barre de progression
        """
        #TODO Dans le futur, veut t'on donner la responsabilite a cette fonction le calcul du pourcentage????
        try:
            dp.update( percent )
        except:
            percent = 100
            dp.update( percent )

    def re_updateList( self ):
        try:
            # Clear all ListItems in this control list
            if hasattr( self, 'clearProperties' ):
                self.clearProperties()
            self.clearList()
            self.setProperty( "Category", self.current_cat )
            self.setProperty( "DlSource", self.default_content )
            for item in self.listitems:
                self.addItem( item )
        except:
            self.updateList()

    def updateData_Prev( self ):
        """
        Retrieve previous data (parent)
        """
        #TODO: use correct string for update data (for time being we use the one of update list)
        if not xbmc.getCondVisibility( "Window.IsActive(progressdialog)" ):
            DIALOG_PROGRESS.create( _( 0 ), _( 104 ), _( 110 ) )
        try:
            #print "Getting list of items got from the browser"
            self.curDirList = self.contextSrc.getBrowser().getPrevList()
        except Exception, e:
            #print "Excpetion during updateData_Prev"
            #print e
            #print sys.exc_info()
            print_exc()
        if not xbmc.getCondVisibility( "Window.IsActive(progressdialog)" ):
            DIALOG_PROGRESS.close()
    
    def updateData_Next( self ):
        """
        Retrieve next data for a specific item of the list
        """
        #TODO: use correct string for update data (for time being we use the one of update list)
        if not xbmc.getCondVisibility( "Window.IsActive(progressdialog)" ):
            DIALOG_PROGRESS.create( _( 0 ), _( 104 ), _( 110 ) )
        try:
            #print "Getting list of items from the browser for current item ID:"
            #print self.index
            self.curDirList = self.contextSrc.getBrowser().getNextList(self.index)
        except Exception, e:
            #print "Exception during updateData_Next"
            #print e
            #print sys.exc_info()
            print_exc()
        if not xbmc.getCondVisibility( "Window.IsActive(progressdialog)" ):
            DIALOG_PROGRESS.close()


    def updateList( self ):
        """
        Mise a jour de la liste affichee
        """
        self._load_downloaded_property()
        if not xbmc.getCondVisibility( "Window.IsActive(progressdialog)" ):
            DIALOG_PROGRESS.create( _( 0 ), _( 104 ), _( 110 ) )

        try:
            #xbmcgui.lock()

            # Clear all ListItems in this control list
            if hasattr( self, 'clearProperties' ):
                self.clearProperties()
            self.clearList()
            self.listitems = []

            # Calcul du nombre d'elements de la liste
            itemnumber = len( self.curDirList )

            self.current_cat = self.contextSrc.getBrowser().getCurrentCategory()
            self.setProperty( "Category", self.current_cat )
            self.setProperty( "DlSource", self.default_content )
            #print "Current Category"
            #print self.current_cat

            #self.setProperty( "Category", self.contextSrc.getBrowser().getCurrentCategory() )

            #print "Starting loop on list of items got from the browser"
            for elt in self.curDirList:
                imagePath = ""
                #print elt

                if self.settings.get( "hide_extention", True ):
                    itemName = os.path.splitext( urllib.unquote( elt['name'] ) )[ 0 ]
                else:
                    itemName = urllib.unquote( elt['name'] )

                displayListItem = xbmcgui.ListItem( itemName, "", elt['thumbnail'], elt['thumbnail'] )

                # Register in case image is not downloaded yet
                self.contextSrc.getBrowser().imageUpdateRegister( elt, updateImage_cb=self._updateListThumb_cb, obj2update=displayListItem )

                self.set_item_infos( displayListItem, elt )

                #print "Item to display"
                #print displayListItem

                self.addItem( displayListItem )
                # utiliser pour remettre la liste courante a jour lorsqu'on reviens sur cette fenetre depuis le forum ou le manager
                self.listitems.append( displayListItem )

            #self.current_cat = unicode( xbmc.getInfoLabel( 'Container.Property(Category)' ), 'utf-8')
            #print "Current Category"
            #print self.current_cat
    
            # Mise a jour des images
            self.set_list_images()
            
            #xbmcgui.unlock()
        except Exception, e:
            #print "Excpetion during updateList"
            #print e
            #print sys.exc_info()
            print_exc()
            
        DIALOG_PROGRESS.close()

    def clear_item_infos( self, listitem ):
        try:
            listitem.setProperty( "itemId",          "" )
            listitem.setProperty( "fileName",        "" )
            listitem.setProperty( "date",            "" )
            listitem.setProperty( "title",           "" )
            listitem.setProperty( "author",          "" )
            listitem.setProperty( "version",         "" )
            listitem.setProperty( "language",        "" )
            listitem.setProperty( "description",     "" )
            listitem.setProperty( "outline",         "" )
            listitem.setProperty( "added",           "" )
            listitem.setProperty( "fanartpicture",   "" )
            listitem.setProperty( "previewVideoURL", "" )
        except:
            print_exc()

    def refresh_item( self ):
        DIALOG_PROGRESS.create( _( 0 ), _( 104 ), _( 110 ) )
        try:
            self.index = self.getCurrentListPosition()
            listitem = self.getListItem( self.index )
            self.clear_item_infos( listitem )
#            self.itemInfosManager = ItemInfosManager( mainwin=self )
#            self.infoswarehouse = self.itemInfosManager.get_info_warehouse()
            self.set_item_infos( listitem, self.curDirList[ self.index ] )
        except:
            print_exc()
        DIALOG_PROGRESS.close()
        return listitem

    def set_item_infos( self, listItem, dataItem ):
        try:
            #print "MainGUI - set_item_infos"
            #print dataItem['name']
            #infos = self.infoswarehouse.getInfo( itemName=os.path.basename( ipath ), itemType=self.type, listitem=listitem )

            listItem.setProperty( "itemId",           "" )

            listItem.setProperty( "fileName",         "" ) # Deprecated

            listItem.setProperty( "date",             dataItem['date'].replace( "None", "" ) )

            try: listItem.setProperty( "title",       urllib.unquote( dataItem['name'].decode('string_escape') ).replace( "None", "" ) )
            except: listItem.setProperty( "title",    urllib.unquote( dataItem['name'] ).replace( "None", "" ) )

            try: listItem.setProperty( "author",      dataItem['author'].decode('string_escape').replace( "None", "" ) )
            except: listItem.setProperty( "author",   dataItem['author'].replace( "None", "" ) )

            try: listItem.setProperty( "version",     dataItem['version'].decode('string_escape').replace( "None", "" ) )
            except: listItem.setProperty( "version",  dataItem['version'].replace( "None", "" ) )

            try: listItem.setProperty( "language",    dataItem['language'].decode('string_escape').replace( "None", "" ) )
            except: listItem.setProperty( "language", dataItem['language'].replace( "None", "" ) )

            listItem.setProperty( "added",            dataItem['added'].replace( "None", "" ) )

            #listItem.setProperty( "fanartpicture",    dataItem['previewpictureurl'] )
            listItem.setProperty( "fanartpicture",    dataItem['previewpicture'].replace( "None", "" ) )

            listItem.setProperty( "previewVideoURL",  "" )

            try: description = urllib.unquote( dataItem['description'].decode('string_escape') )
            except: description = urllib.unquote( dataItem['description'] )
            listItem.setProperty( "description", description.replace( "None", "" ) )
            listItem.setProperty( "outline",     description.replace( "None", "" ).replace( "\r", "\n" ).replace( "\n\n", "  " ).replace( "\n", " " ).replace( "[CR]", " " ) )
            #print "set_item_infos"
            #print dataItem
        except:
            print_exc()
            print_exc()

    def _updateListThumb_cb( self, imagePath, listitem ):
        """
        Callback updating one specific image in the displayed list
        Need to use imageUpdateRegister() on Browser in order to be called
        """
        if imagePath and hasattr( listitem, "setThumbnailImage" ):
            listitem.setThumbnailImage( imagePath )
            listitem.setIconImage( imagePath ) # TODO" do we keep the same resoltuin between thumb and image???

    def set_list_images( self ):
        """
        Recuperation de toutes les images dans la FIFO et mise a jour dans la liste via appel sur la callback _updateListThumb_cb
        """
        try:
            # Recuperation des images dans un thread separe via la fonction update_Images()
            self.contextSrc.getBrowser().update_Images()
        except:
            print_exc()

    def deleteDir( self, path ):
        """
        Efface un repertoire et tout son contenu ( le repertoire n'a pas besoin d'etre vide )
        retourne True si le repertoire est effece False sinon
        """
        result = True
        #print "deleteDir"
        #print path
        if os.path.isdir( path ):
            dirItems=os.listdir( path )
            for item in dirItems:
                itemFullPath=os.path.join( path, item )
                try:
                    if os.path.isfile( itemFullPath ):
                        # Fichier
                        os.remove( itemFullPath )
                    elif os.path.isdir( itemFullPath ):
                        # Repertoire
                        self.deleteDir( itemFullPath )
                except:
                    result = False
                    print "deleteDir: Exception la suppression du reperoire: %s" % path
                    print_exc()
            # Suppression du repertoire pere
            try:
                os.rmdir( path )
            except:
                result = False
                print "deleteDir: Exception la suppression du reperoire: %s" % path
                print_exc()
        else:
            print "deleteDir: %s n'est pas un repertoire" % path
            result = False

        return result

    def delDirContent( self, path ):
        """
        Efface tous le contenu d'un repertoire ( fichiers  et sous-repertoires )
        mais pas le repertoire lui meme
        folder: chemin du repertoire local
        """
        #print "delDirContent"
        #print path
        result = True
        if os.path.isdir( path ):
            dirItems=os.listdir( path )
            for item in dirItems:
                itemFullPath=os.path.join( path, item )
                try:
                    if os.path.isfile( itemFullPath ):
                        # Fichier
                        os.remove( itemFullPath )
                    elif os.path.isdir( itemFullPath ):
                        # Repertoire
                        self.deleteDir( itemFullPath )
                except:
                    result = False
                    print "delDirContent: Exception la suppression du contenu du reperoire: %s" % path
                    print_exc()
        else:
            print "delDirContent: %s n'est pas un repertoire" % path
            result = False

        return result

    def verifrep( self, folder ):
        """
        Source: myCine
        Verifie l'existance  d'un repertoire et le cree si besoin
        """
        try:
            if not os.path.exists( folder ):
                os.makedirs( folder )
        except:
            print "verifrep - Exception durant la creation du repertoire: %s" % folder
            print_exc()

    def linux_chmod( self, path ):
        """
        Effectue un chmod sur un repertoire pour ne plus etre bloque par les droits root sur plateforme linux
        """
        Wtest = os.access( path, os.W_OK )
        if Wtest == True:
            self.rightstest = True
            print "linux chmod rightest OK"
        else:
            xbmcgui.Dialog().ok( _( 19 ), _( 20 ) )
            keyboard = xbmc.Keyboard( "", _( 21 ), True )
            keyboard.doModal()
            if keyboard.isConfirmed():
                password = keyboard.getText()
                PassStr = "echo %s | "%password
                ChmodStr = "sudo -S chmod 777 -R %s"%path
                try:
                    os.system( PassStr + ChmodStr )
                    self.rightstest = True
                except:
                    self.rightstest = False
                    print "bypass: erreur CHMOD %s" % path
                    print_exc()
            else:
                self.rightstest = False

    #def processOldDownload( self, localAbsDirPath ):
    def processOldDownload( self, itemInstaller ):
        """
        Traite les ancien download suivant les desirs de l'utilisateur
        retourne True si le download peut continuer.
        """

#        from FileManager import fileMgr
#        fileMgr = fileMgr()

        continueDownload = True

        # Get Item install name
        itemInstallName = itemInstaller.getItemInstallName()
        
        # Verifie se on telecharge un repertoire ou d'un fichier
#        if os.path.isdir( localAbsDirPath ):
#            # Repertoire
        exit = False
        while exit == False:
            menuList = [ _( 150 ), _( 151 ), _( 152 ), _( 153 ) ]
            dialog = xbmcgui.Dialog()
            #chosenIndex = dialog.select( _( 149 ) % os.path.basename( localAbsDirPath ), menuList )
            chosenIndex = dialog.select( _( 149 ) % itemInstallName, menuList )
            if chosenIndex == 0:
                # Delete
                print "Deleting: %s"%itemInstallName
                #OK = self.deleteDir( localAbsDirPath )
                #OK = fileMgr.deleteItem( localAbsDirPath )
                OK = itemInstaller.deleteInstalledItem()
                if OK == True:
                    exit = True
                else:
                    xbmcgui.Dialog().ok( _(148), _( 117) )
            elif chosenIndex == 1: 
                # Rename
                #keyboard = xbmc.Keyboard( os.path.basename( localAbsDirPath ), _( 154 ) )
                keyboard = xbmc.Keyboard( os.path.basename( itemInstallName ), _( 154 ) )
                keyboard.doModal()
                if ( keyboard.isConfirmed() ):
                    inputText = keyboard.getText()
                    #os.rename( localAbsDirPath, localAbsDirPath.replace( os.path.basename( localAbsDirPath ), inputText ) )
                    #OK = fileMgr.renameItem( base_path, old_name, new_name)
                    OK = itemInstaller.renameInstalledItem( inputText )
                    #xbmcgui.Dialog().ok( _( 155 ), localAbsDirPath.replace( os.path.basename( localAbsDirPath ), inputText ) )
                    if OK == True:
                        xbmcgui.Dialog().ok( _( 155 ), inputText  )
                        exit = True
                    else:
                        xbmcgui.Dialog().ok( _(148), _( 117) )
                        
                del keyboard
            elif chosenIndex == 2: # Ecraser
                exit = True
            else:
                # EXIT
                exit = True
                continueDownload = False
#        else:
#            # Fichier
#            print "bypass: processOldDownload: Fichier : %s - ce cas n'est pas encore traite" % localAbsDirPath
#            #TODO: cas a implementer

        return continueDownload
        
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



def show_main( HomeAction=None ):
    #Fonction de demarrage
    #depuis la revision 14811 on a plus besoin de mettre le chemin complet, la racine suffit
    dir_path = os.getcwd().replace( ";", "" )
    #recupere le nom du skin et si force_fallback est vrai, il va chercher les images du defaultSkin.
    current_skin, force_fallback = getUserSkin()
    file_xml = ( "IPX-Installer.xml", "passion-main.xml" )[ current_skin != "Default.HD" ]

    w = MainWindow( file_xml, dir_path, current_skin, force_fallback, HomeAction=HomeAction )
    w.doModal()
    del w
