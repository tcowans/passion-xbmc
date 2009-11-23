#
#Modules general
import os
import re
import md5
import sys
import time
import urllib

from threading import Thread, Timer
import traceback

#modules XBMC
import xbmc
import xbmcgui

#modules custom
from PassionHttpBrowser import PassionHttpBrowser
from PassionFtpBrowser import PassionFtpBrowser
from utilities import *

from info_item import ItemInfosManager
from INSTALLEUR import ftpDownloadCtrl, directorySpy, userDataXML

#module logger
try:
    logger = sys.modules[ "__main__" ].logger
except:
    import script_log as logger


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


class MainWindow( xbmcgui.WindowXML ):
    # control id's
    CONTROL_MAIN_LIST_START = 50
    CONTROL_MAIN_LIST_END   = 59
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
        self.main_list_last_pos = []

        # Display Loading Window while we are loading the information from the website
        if xbmc.getCondVisibility( "Window.IsActive(progressdialog)" ):
            #si le dialog PROGRESS est visible update
            DIALOG_PROGRESS.update( -1, _( 103 ), _( 110 ) )
        else:
            #si le dialog PROGRESS n'est pas visible affiche le dialog
            DIALOG_PROGRESS.create( _( 0 ), _( 103 ), _( 110 ) )

        #TODO: TOUTES ces varibales devraient etre passees en parametre du constructeur de la classe ( __init__ si tu preferes )
        # On ne devraient pas utiliser de variables globale ou rarement en prog objet

        # Creation du configCtrl
        from CONF import configCtrl
        self.configManager = configCtrl()
        if not self.configManager.is_conf_valid: raise

#        self.host               = self.configManager.host
#        self.user               = self.configManager.user
        self.rssfeed            = self.configManager.rssfeed
#        self.password           = self.configManager.password
#        self.remotedirList      = self.configManager.remotedirList

#        self.localdirList       = self.configManager.localdirList
#        self.downloadTypeList   = self.configManager.downloadTypeLst

#        self.racineDisplayList  = [ 0, 1, 2, 3 ]
#        self.pluginDisplayList  = [ 4, 5, 6, 7 ]
#        self.pluginsDirSpyList  = []

        self.curDirList         = []
#        self.connected          = False # status de la connection ( inutile pour le moment )
#        self.index              = ""
        self.index              = 0
        self.scraperDir         = self.configManager.scraperDir
        self.type               = "racine"
        self.USRPath            = self.configManager.USRPath
        self.rightstest         = ""
#        self.scriptDir          = self.configManager.scriptDir
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
        self._get_settings()
        self._set_skin_colours()

#        if self.settings.get( "show_plash" ) == True:
#            # splash desactive par le user 
#            self.getControl( self.CONTROL_SHOW_SPLASH_IMG ).setVisible( 0 )
        self.getControl( self.CONTROL_SHOW_SPLASH_IMG ).setVisible( 0 )

        if self.is_started:
            self.is_started = False

            self._start_rss_timer()

            # Connection au serveur FTP
            try:
                DIALOG_PROGRESS.update( -1, _( 104 ), _( 110 ) )
                # Starting browser of the DB
                #myBrowser = Browser.PassionHttpBrowser( database=db )
                # Use level of abstraction ItemBrowser (super class)
                self.browser_PassionHttp = PassionHttpBrowser()
                self.browser = self.browser_PassionHttp
#                self.browser_PassionFtp  = PassionFtpBrowser()
#                self.browser = self.browser_PassionFtp
                # Recuperation de la liste des elements
                print "Updating displayed list"
                self.updateData_Next()
                self.updateList()
                print "End of update for the displayed list" 

            except:
                #print str(sys.exc_info()[0])
                print sys.exc_info()
                traceback.print_exc()
                xbmcgui.Dialog().ok( _( 111 ), _( 112 ) )
                logger.LOG( logger.LOG_DEBUG, "Window::__init__: Exception durant la connection FTP" )
                logger.LOG( logger.LOG_DEBUG, "Impossible de se connecter au serveur FTP: %s", self.host )
                logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )

            # Title of the current pages
            self.setProperty( "Category", _( 10 ) )
            xbmc.executebuiltin( "Container.SetViewMode(%i)" % self.settings.get( "main_view_mode", self.CONTROL_MAIN_LIST_START ) )


            # Close the Loading Window
            DIALOG_PROGRESS.close()
        else:
            # pas le choix avec les nouvelles vue, mais on lui joue un tour avec une listitems deja ready :P
            if xbmc.getCondVisibility( "Window.IsActive(passion-main.xml)" ):
                if self.listitems: self.re_updateList()
                else: self.updateList()
            # .addItems( items=listitems )
            # print "self.addItems( items= )", hasattr( self, 'addItems' )
            # for ControlList only :(

        # desactive le splash
        self.getControl( self.CONTROL_SHOW_SPLASH_IMG ).setVisible( 0 )

    def _get_settings( self, defaults=False ):
        """ reads settings """
        self.settings = Settings().get_settings( defaults=defaults )
        self.getControl( self.CONTROL_FORUM_BUTTON ).setVisible( not self.settings.get( "hide_forum", False ) )

    def _set_skin_colours( self ):
        #xbmcgui.lock()
        try:
            xbmc.executebuiltin( "Skin.SetString(PassionSkinColourPath,%s)" % ( self.settings[ "skin_colours_path" ], ) )
            xbmc.executebuiltin( "Skin.SetString(PassionSkinHexColour,%s)" % ( ( self.settings[ "skin_colours" ] or get_default_hex_color() ), ) )
        except:
            xbmc.executebuiltin( "Skin.SetString(PassionSkinHexColour,ffffffff)" )
            xbmc.executebuiltin( "Skin.SetString(PassionSkinColourPath,default)" )
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )
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
                logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )
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
            text_color = repr( self.getControl( 101 ).getLabel2() ).strip( "u'" )
            #print repr( title_color ), repr( text_color )
            self.rss_feed = RSSParser.rssReader( self.rss_title, self.rssfeed, title_color, text_color ).GetRssInfo()[ 1 ]
        except:
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )
            try:
                self.rss_feed = RSSParser.rssReader( self.rss_title, self.rssfeed ).GetRssInfo()[ 1 ]
            except:
                logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )
        del RSSParser
        try:
            self.getControl( 100 ).reset()
            self.getControl( 100 ).addLabel( self.rss_feed )
            self.getControl( 100 ).setVisible( True )
        except:
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )
            try: self.getControl( 100 ).setVisible( False )
            except: pass
            self._stop_rss_timer()
        else:
            try:
                self.rss_timer = Timer( self.rss_update_interval, self._set_control_rss_feed, () )
                self.rss_timer.start()
            except:
                logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )

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
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )

    def _show_settings( self ):
        try:
            thumb_size_on_load = self.settings[ "thumb_size" ]
            import DialogSettings
            DialogSettings.show_settings( self )
            #on a plus besoin du settings, on le delete
            del DialogSettings
            if thumb_size_on_load != self.settings[ "thumb_size" ]:
                self.updateList() #on raffraichit la page pour afficher la taille des vignettes
        except:
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )

    def _show_direct_infos( self ):
        try:
            import ForumDirectInfos
            ForumDirectInfos.show_direct_infos()
            #on a plus besoin, on le delete
            del ForumDirectInfos
        except:
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )

    def _show_context_menu( self ):
        try:
            if ( not self.type.lower() in ( "racine", "plugins", ) ) and ( self.CONTROL_MAIN_LIST_START <= self.getFocusId() <= self.CONTROL_MAIN_LIST_END ):#( self.getFocusId() == self.CONTROL_MAIN_LIST ):
                import DialogContextMenu
                #buttons = { 1000 : ( "teste 1", "disabled" ), 1001 : "teste 2", 1002 : "teste 3",
                #    1003 : "teste 4", 1004 : ( "teste 5", "disabled" ), 1005 : "teste 6", 1006 : "teste 7" }
                buttons = { 1000: _( 1000 ), 1001: _( 1001 ), 1002: _( 184 ), 1003: _( 1002 ) }
                selected = DialogContextMenu.show_context_menu( buttons )
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
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )

    def _switch_media( self ):
        try:
            import DialogContextMenu
            buttons = { 1000: _( 11 ), 1001: _( 12 ), 1002: _( 13 ), 1003: _( 14 ),
                1004: _( 18 ), 1005: _( 16 ), 1006: _( 15 ), 1007: _( 17 ) }
            selected = DialogContextMenu.show_context_menu( buttons )
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
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )

    def onAction( self, action ):
        """
        Remonte l'arborescence et quitte le script
        """
        try:
            if action == ACTION_PREVIOUS_MENU:
                # Sortie du script
                self.onExit()

            elif action == ACTION_PARENT_DIR:
                print "ACTION_PARENT_DIR"
                # remonte l'arborescence
                if not self.main_list_last_pos:
                    try: self.main_list_last_pos.append( self.getCurrentListPosition() )
                    except: self.main_list_last_pos.append( 0 )
                try:
                    # Get data and update display
                    self.updateData_Prev()
                    self.updateList()
                except:
                    logger.LOG( logger.LOG_DEBUG, "Window::onAction::ACTION_PREVIOUS_MENU: Exception durant updateList()" )
                    logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )

                if self.main_list_last_pos:
                    self.setCurrentListPosition( self.main_list_last_pos.pop() )

            elif action == ACTION_SHOW_INFO:
                 print "_show_descript - ItemDescription"
                 self._show_descript()

            elif action == ACTION_CONTEXT_MENU:
                self._show_context_menu()

            else:
                pass

        except:
            logger.LOG( logger.LOG_DEBUG, "Window::onAction: Exception" )
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )

    def install_add_ons( self ):
        """
        installation de l'item selectionner
        """

        try:
            # Get the installer Object who now how to do the job (depending on the source)
            itemName = self.curDirList[self.index]['name']
            if not xbmcgui.Dialog().yesno( _( 180 ), _( 181 ), itemName ): return
            
            itemInstaller = self.browser.getInstaller(self.index)
            
            print "Download via itemInstaller"
            dp = xbmcgui.DialogProgress()
            dp.create(_( 137 ))
            status, destination = itemInstaller.installItem( msgFunc=self.message_cb, progressBar=dp )
    
            dp.close()
            del dp
    
            #Check if install went well
            print itemName
            print repr(itemName)
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
                if self.processOldDownload( destination ):
                    # Continue install
                    dp = xbmcgui.DialogProgress()
                    dp.create(_( 137 ))
                    status, destination = itemInstaller.installItem( msgFunc=self.message_cb, progressBar=dp )                
                    dp.close()
                    del dp
                else:
                    installCancelled = True
                    logger.LOG( logger.LOG_WARNING, "L'installation de %s a ete annulee par l'utilisateur", downloadItem  )

            else:
                title = _( 144 )
                msg1  = _( 136 )%itemName
                msg2  = ""
            xbmcgui.Dialog().ok( title, msg1, msg2 )
            del itemInstaller
        except:
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )

    def _close_script( self ):
        #**IMPORTANT** faut annuler les thread avant de fermer le script, sinon xbmc risque de planter
        #NB: le meme scenario va ce produire si vous fermer ou redemarrer xbmc avec le script en marche
        #on annule les thread
        self._stop_rss_timer()
#        try: self.infoswarehouse.getImage_thread.cancel()
#        except: pass
        try: self.infoswarehouse.cancel_update_Images()
        except: pass
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
                if self.browser.isCat(self.getCurrentListPosition()):
                    try: self.main_list_last_pos.append( self.getCurrentListPosition() )
                    except: self.main_list_last_pos.append( 0 )
                    
                    # Get data and update display
                    self.updateData_Next()
                    self.updateList()
    
                    #TODO: case of install an item
                else:
                    print "Download and install case"
                    self.install_add_ons()

                    # Save in local directory
                    #TODO: support message callback in addition of pb callback
                    # itemInstaller.downloadItem( progressBar=dp )
                    # itemInstaller.extractItem( progressBar=dp )
                    # if not itemInstaller.isAlreadyInstalled():
                        # print "Item is not yet installed - installing"
                        # import time
                        # time.sleep(10)
                        # itemInstaller.installItem( progressBar=dp )
                    # else:
                        # print "Item is already installed - stopping install"

            elif controlID == self.CONTROL_OPTIONS_BUTTON:
                self._show_settings()

            elif controlID == self.CONTROL_FILE_MGR_BUTTON:
                thumb_size_on_load = self.settings[ "thumb_size" ]
                import FileManagerGui
                mainfunctions = [ self._show_settings, self._close_script ]
                FileManagerGui.show_file_manager( mainfunctions, self.rightstest )
                #on a plus besoin du manager, on le delete
                del FileManagerGui
                if thumb_size_on_load != self.settings[ "thumb_size" ]:
                    self.updateList() #on raffraichit la page pour afficher la taille des vignettes

            elif controlID == self.CONTROL_FORUM_BUTTON:
                self._show_direct_infos()

            elif controlID == self.CONTROL_EXIT_BUTTON:
                self._close_script()

            else:
                pass

        except Exception, e:
            print "Exception during onClick"
            print e
            print sys.exc_info()
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )

    def onExit( self ):
        """
        Action done on exit of the application
        """
        # Close Browser
        self.browser.close()

        # Delete cache directory
        self.deleteDir( self.CacheDir )

        # Closing everything
        self._close_script()

    def _load_downloaded_property( self ):
        self.downloaded_property = set()
        try:
            file_path = os.path.join( SPECIAL_SCRIPT_DATA, "downloaded.txt" )
            if os.path.exists( file_path ):
                self.downloaded_property = eval( file( file_path, "r" ).read() )
        except:
            logger.EXC_INFO( logger.LOG_DEBUG, sys.exc_info(), self )

    def _save_downloaded_property( self ):
        try:
            self._load_downloaded_property()
            selected_label = self.getListItem( self.getCurrentListPosition() ).getLabel()
            self.downloaded_property.update( [ md5.new( selected_label ).hexdigest() ] )
            file_path = os.path.join( SPECIAL_SCRIPT_DATA, "downloaded.txt" )
            file( file_path, "w" ).write( repr( self.downloaded_property ) )
        except:
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )
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
            print "Getting list of items got from the browser"
            self.curDirList = self.browser.getPrevList()
        except Exception, e:
            print "Excpetion during updateData_Prev"
            print e
            print sys.exc_info()
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )
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
            print "Getting list of items from the browser for current item ID:"
            print self.index
            self.curDirList = self.browser.getNextList(self.index)
        except Exception, e:
            print "Exception during updateData_Next"
            print e
            print sys.exc_info()
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )
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

            print "Starting loop on list of items got from the browser"
            for elt in self.curDirList:
                imagePath = ""
                print elt
                
                
                self.setProperty( "Category", self.browser.getCurrentCategory() )
                if self.settings.get( "hide_extention", True ):
                    itemName = os.path.splitext( urllib.unquote( elt['name'] ) )[ 0 ]
                else:
                    itemName = urllib.unquote( elt['name'] )

                displayListItem = xbmcgui.ListItem( itemName, "", iconImage=elt['previewpicture'], thumbnailImage=elt['thumbnail'] )

                # Register in case image is not downloaded yet
                self.browser.imageUpdateRegister( elt, updateImage_cb=self._updateListThumb_cb, obj2update=displayListItem )

                self.set_item_infos( displayListItem, elt )
                
                print "Item to display"
                print displayListItem
                
                self.addItem( displayListItem )                
                # utiliser pour remettre la liste courante a jour lorsqu'on reviens sur cette fenetre depuis le forum ou le manager
                self.listitems.append( displayListItem )
    
            self.current_cat = unicode( xbmc.getInfoLabel( 'Container.Property(Category)' ), 'utf-8')
            #print "Current Category"
            #print self.current_cat
    
            # Mise a jour des images
            self.set_list_images()
            
            #xbmcgui.unlock()
        except Exception, e:
            print "Excpetion during updateList"
            print e
            print sys.exc_info()
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )
            
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
            listitem.setProperty( "added",           "" )
            listitem.setProperty( "fanartpicture",   "" )
            listitem.setProperty( "previewVideoURL", "" )
        except:
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )

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
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )
        DIALOG_PROGRESS.close()
        return listitem

    def set_item_infos( self, listItem, dataItem ):
        try:
            print "MainGUI - set_item_infos"
            print dataItem['name']
            #infos = self.infoswarehouse.getInfo( itemName=os.path.basename( ipath ), itemType=self.type, listitem=listitem )
            listItem.setProperty( "itemId",          "" )
            listItem.setProperty( "fileName",        "" ) # Deprecated
            listItem.setProperty( "date",            dataItem['date'] )
            listItem.setProperty( "title",           urllib.unquote( dataItem['name'].decode('string_escape') ) )
            listItem.setProperty( "author",          dataItem['author'].decode('string_escape') )
            listItem.setProperty( "version",         dataItem['version'].decode('string_escape') )
            listItem.setProperty( "language",        dataItem['language'].decode('string_escape') )
            listItem.setProperty( "description",     urllib.unquote( dataItem['description'].decode('string_escape') ) )
            listItem.setProperty( "added",           dataItem['added'] )
            listItem.setProperty( "fanartpicture",   dataItem['previewpictureurl'] )
            listItem.setProperty( "previewVideoURL", "" )
            print "set_item_infos"
            print dataItem            
        except:
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )
            print sys.exc_info()
            traceback.print_exc()

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
            self.browser.update_Images()
        except:
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )

    def deleteDir( self, path ):
        """
        Efface un repertoire et tout son contenu ( le repertoire n'a pas besoin d'etre vide )
        retourne True si le repertoire est effece False sinon
        """
        result = True
        print "deleteDir"
        print path
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
                    logger.LOG( logger.LOG_DEBUG, "deleteDir: Exception la suppression du reperoire: %s", path )
                    logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )
            # Suppression du repertoire pere
            try:
                os.rmdir( path )
            except:
                result = False
                logger.LOG( logger.LOG_DEBUG, "deleteDir: Exception la suppression du reperoire: %s", path )
                logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )
        else:
            logger.LOG( logger.LOG_DEBUG, "deleteDir: %s n'est pas un repertoire", path )
            result = False

        return result

    def delDirContent( self, path ):
        """
        Efface tous le contenu d'un repertoire ( fichiers  et sous-repertoires )
        mais pas le repertoire lui meme
        folder: chemin du repertoire local
        """
        print "delDirContent"
        print path
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
                    logger.LOG( logger.LOG_DEBUG, "delDirContent: Exception la suppression du contenu du reperoire: %s", path )
                    logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )
                    traceback.print_exc()
        else:
            logger.LOG( logger.LOG_ERROR, "delDirContent: %s n'est pas un repertoire", path )
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
            logger.LOG( logger.LOG_DEBUG, "verifrep - Exception durant la creation du repertoire: %s", folder )
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )
            pass

    def linux_chmod( self, path ):
        """
        Effectue un chmod sur un repertoire pour ne plus etre bloque par les droits root sur plateforme linux
        """
        Wtest = os.access( path, os.W_OK )
        if Wtest == True:
            self.rightstest = True
            logger.LOG( logger.LOG_NOTICE, "linux chmod rightest OK" )
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
                    logger.LOG( logger.LOG_ERROR, "erreur CHMOD %s", path )
                    logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )
            else:
                self.rightstest = False

    def processOldDownload( self, localAbsDirPath ):
        """
        Traite les ancien download suivant les desirs de l'utilisateur
        retourne True si le download peut continuer.
        """
        continueDownload = True

        # Verifie se on telecharge un repertoire ou d'un fichier
        if os.path.isdir( localAbsDirPath ):
            # Repertoire
            menuList = [ _( 150 ), _( 151 ), _( 152 ), _( 153 ) ]
            dialog = xbmcgui.Dialog()
            chosenIndex = dialog.select( _( 149 ) % os.path.basename( localAbsDirPath ), menuList )
            if chosenIndex == 0:
                # Supprimer
                print "Delete Dir: %s"%localAbsDirPath
                OK = self.deleteDir( localAbsDirPath )
                print OK
            elif chosenIndex == 1: # Renommer
                # Suppression du repertoire
                keyboard = xbmc.Keyboard( os.path.basename( localAbsDirPath ), _( 154 ) )
                keyboard.doModal()
                if ( keyboard.isConfirmed() ):
                    inputText = keyboard.getText()
                    os.rename( localAbsDirPath, localAbsDirPath.replace( os.path.basename( localAbsDirPath ), inputText ) )
                    xbmcgui.Dialog().ok( _( 155 ), localAbsDirPath.replace( os.path.basename( localAbsDirPath ), inputText ) )
                del keyboard
            elif chosenIndex == 2: # Ecraser
                pass
            else:
                continueDownload = False
        else:
            # Fichier
            logger.LOG( logger.LOG_ERROR, "processOldDownload: Fichier : %s - ce cas n'est pas encore traite", localAbsDirPath )
            #TODO: cas a implementer

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


def show_main():
    #Fonction de demarrage
    file_xml = "passion-main.xml"
    #depuis la revision 14811 on a plus besoin de mettre le chemin complet, la racine suffit
    dir_path = os.getcwd().replace( ";", "" )
    #recupere le nom du skin et si force_fallback est vrai, il va chercher les images du defaultSkin.
    current_skin, force_fallback = getUserSkin()

    w = MainWindow( file_xml, dir_path, current_skin, force_fallback )
    #w = MainWindow()
    w.doModal()
    del w
