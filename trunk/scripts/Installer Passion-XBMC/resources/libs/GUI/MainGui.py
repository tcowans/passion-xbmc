
#Modules general
import os
import re
import md5
import sys
import time

from threading import Thread, Timer

#modules XBMC
import xbmc
import xbmcgui

#modules custom
from utilities import *
from info_item import ItemInfosManager
from INSTALLEUR import ftpDownloadCtrl, directorySpy, userDataXML

#module logger
try:
    logger = sys.modules[ "__main__" ].logger
except:
    import script_log as logger


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

        self.host               = self.configManager.host
        self.user               = self.configManager.user
        self.rssfeed            = self.configManager.rssfeed
        self.password           = self.configManager.password
        self.remotedirList      = self.configManager.remotedirList
        
        self.localdirList       = self.configManager.localdirList
        self.downloadTypeList   = self.configManager.downloadTypeLst

        self.racineDisplayList  = [ 0, 1, 2, 3 ]
        self.pluginDisplayList  = [ 4, 5, 6, 7 ]
        self.pluginsDirSpyList  = []

        self.curDirList         = []
        self.connected          = False # status de la connection ( inutile pour le moment )
        self.index              = ""
        self.scraperDir         = self.configManager.scraperDir
        self.type               = "racine"
        self.USRPath            = self.configManager.USRPath
        self.rightstest         = ""
        self.scriptDir          = self.configManager.scriptDir
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

        #TODO: A nettoyer, ton PMIIIDir n'est pas defini pour XBOX sans le test si dessous
        if self.USRPath == True:
            self.PMIIIDir = self.configManager.PMIIIDir

        self.is_started = True
        # utiliser pour remettre la liste courante a jour lorsqu'on reviens sur cette fenetre depuis le forum ou le manager
        self.listitems = []
        self.current_cat = ""

    def onInit( self ):
        self._get_settings()
        self._set_skin_colours()

        if self.is_started:
            self.is_started = False

            self._start_rss_timer()

            # Connection au serveur FTP
            try:

                self.passionFTPCtrl = ftpDownloadCtrl( self.host, self.user, self.password, self.remotedirList, self.localdirList, self.downloadTypeList )
                self.connected = True

                # Recuperation de la liste des elements
                DIALOG_PROGRESS.update( -1, _( 104 ), _( 110 ) )
                self.updateList()

            except:
                xbmcgui.Dialog().ok( _( 111 ), _( 112 ) )
                logger.LOG( logger.LOG_DEBUG, "Window::__init__: Exception durant la connection FTP" )
                logger.LOG( logger.LOG_DEBUG, "Impossible de se connecter au serveur FTP: %s", self.host )
                logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )

            # Title of the current pages
            self.setProperty( "Category", _( 10 ) )
            xbmc.executebuiltin( "Container.SetViewMode(%i)" % self.settings.get( "main_view_mode", self.CONTROL_MAIN_LIST_START ) )

            # Capturons le contenu des sous-repertoires plugins
            for type in self.downloadTypeList:
                if type.find( "Plugins" ) != -1:
                    #self.pluginsInitList.append( os.listdir( self.localdirList[ self.downloadTypeList.index( type ) ] ) )
                    self.pluginsDirSpyList.append( directorySpy( self.localdirList[ self.downloadTypeList.index( type ) ] ) )
                else:
                    self.pluginsDirSpyList.append( None )
                    
            # Creons ItemInfosManager afin de recuperer les descriptions des items
            self.itemInfosManager = ItemInfosManager( mainwin=self )
            
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
            # Affiche la description de l'item selectionner
            if ( not self.type.lower() in ( "racine", "plugins", ) ) and ( self.CONTROL_MAIN_LIST_START <= self.getFocusId() <= self.CONTROL_MAIN_LIST_END ):
                currentListIndex = self.getCurrentListPosition()
                if currentListIndex >= 0:
                    selectedItem = os.path.basename( self.curDirList[ currentListIndex ] )
                    from DialogItemDescription import show_item_descript_window
                    show_item_descript_window( self, self.itemInfosManager, selectedItem, self.type )
        except:
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )

    def _show_settings( self ):
        try:
            thumb_size_on_load = self.settings[ "thumb_size" ]
            from DialogSettings import show_settings
            show_settings( self )
            #on a plus besoin du settings, on le delete
            del show_settings
            if thumb_size_on_load != self.settings[ "thumb_size" ]:
                self.updateList() #on raffraichit la page pour afficher la taille des vignettes
        except:
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )

    def _show_direct_infos( self ):
        try:
            from ForumDirectInfos import show_direct_infos
            show_direct_infos( self )
            #on a plus besoin, on le delete
            del show_direct_infos
        except:
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )

    def _show_context_menu( self ):
        try:
            if ( not self.type.lower() in ( "racine", "plugins", ) ) and ( self.CONTROL_MAIN_LIST_START <= self.getFocusId() <= self.CONTROL_MAIN_LIST_END ):#( self.getFocusId() == self.CONTROL_MAIN_LIST ):
                from DialogContextMenu import show_context_menu
                #buttons = { 1000 : ( "teste 1", "disabled" ), 1001 : "teste 2", 1002 : "teste 3",
                #    1003 : "teste 4", 1004 : ( "teste 5", "disabled" ), 1005 : "teste 6", 1006 : "teste 7" }
                buttons = { 1000: _( 1000 ), 1001: _( 1001 ), 1002: _( 1002 ) }
                selected = show_context_menu( buttons )
                del show_context_menu
                if selected == 1000:
                    #installe add-ons
                    self.install_add_ons()
                elif selected == 1001:
                    self._show_descript()
                elif selected == 1002:
                    self._switch_media()
                else:
                    pass
        except:
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )

    def _switch_media( self ):
        try:
            from DialogContextMenu import show_context_menu
            buttons = { 1000: _( 11 ), 1001: _( 12 ), 1002: _( 13 ), 1003: _( 14 ),
                1004: _( 18 ), 1005: _( 16 ), 1006: _( 15 ), 1007: _( 17 ) }
            selected = show_context_menu( buttons )
            del show_context_menu
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

                # On se deconnecte du serveur pour etre plus propre
                self.passionFTPCtrl.closeConnection()

                # On efface le repertoire cache
                self.deleteDir( self.CacheDir )

                # Verifions si la mise a jour du XML a ete activee
                if self.settings[ "xbmc_xml_update" ]:
                    # Capturons le contenu des sous-repertoires plugins a la sortie du script
                    xmlConfFile = userDataXML( os.path.join( self.userDataDir, "sources.xml" ), os.path.join( self.userDataDir, "sourcesNew.xml" ) )
                    for type in self.downloadTypeList:
                        if type.find( "Plugins" ) != -1:
                            # Verifions si des plugins on ete ajoutes
                            newPluginList = None
                            try:
                                #newPluginList = list( set( self.pluginsExitList[ self.downloadTypeList.index( type ) ] ).difference( set( self.pluginsInitList[ self.downloadTypeList.index( type ) ] ) ) )
                                newPluginList = self.pluginsDirSpyList[ self.downloadTypeList.index( type ) ].getNewItemList()
                            except:
                                logger.LOG( logger.LOG_DEBUG, "Exception durant la comparaison des repertoires plugin avant et apres installation" )
                                logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )
                            if len( newPluginList ) > 0:
                                for newPluginName in newPluginList:
                                    # Creation du chemin qui sera ajoute au XML, par ex : "plugin://video/Google video/"
                                    # TODO: extraire des chemins local des plugins les strings, 'music', 'video' ... et n'avoir qu'une implementation
                                    if type == "Plugins Musique":
                                        categorieStr = "music"

                                    elif type == "Plugins Images":
                                        categorieStr = "pictures"

                                    elif type == "Plugins Programmes":
                                        categorieStr = "programs"

                                    elif type == "Plugins Videos":
                                        categorieStr = "video"
                                    newPluginPath = "plugin://" + categorieStr + "/" + newPluginName + "/"

                                    # Mise a jour de sources.xml
                                    xmlConfFile.addPluginEntry( type, newPluginName, newPluginPath )
                    # Validation et sauvegarde des modificatiobs du XML
                    newConfFile = xmlConfFile.commit()
                    del xmlConfFile

                    # On verifie si on a cree un nouveau XML
                    if newConfFile:
                        currentTimeStr = str( time.time() )
                        # on demande a l'utilisateur s'il veut remplacer l'ancien xml par le nouveau
                        menuList = [ _( 113 ), _( 114 ), _( 115 ) ]
                        dialog = xbmcgui.Dialog()
                        chosenIndex = dialog.select( _( 116 ), menuList )
                        if chosenIndex == 0:
                            # Mettre a jour la configuation et sortir
                            # On renomme sources.xml en ajoutant le timestamp
                            os.rename( os.path.join( self.userDataDir, "sources.xml" ), os.path.join( self.userDataDir, "sources_%s.xml"%currentTimeStr ) )
                            # On renomme sourcesNew.xml source.xml
                            os.rename( os.path.join( self.userDataDir, "sourcesNew.xml" ), os.path.join( self.userDataDir, "sources.xml" ) )

                        elif chosenIndex == 1:
                            # Mettre a jour la configuation et redemarrer
                            # On renomme source.xml en ajoutant le timestamp
                            os.rename( os.path.join( self.userDataDir, "sources.xml" ), os.path.join( self.userDataDir, "sources_%s.xml"%currentTimeStr ) )
                            # On renomme sourcesNew.xml source.xml
                            os.rename( os.path.join( self.userDataDir, "sourcesNew.xml" ), os.path.join( self.userDataDir, "sources.xml" ) )
                            # on redemarre
                            xbmc.restart()
                        else:
                            # On supprime le xml que nous avons genere
                            os.remove( os.path.join( self.userDataDir, "sourcesNew.xml" ) )
                #on ferme tout
                self._close_script()

            elif action == ACTION_PARENT_DIR:
                # remonte l'arborescence
                # On verifie si on est a l'interieur d'un ses sous section plugin
                #if ( self.type == "Plugins Musique" ) or ( self.type == "Plugins Images" ) or ( self.type == "Plugins Programmes" ) or ( self.type == "Plugins Videos" ):
                if not self.main_list_last_pos:
                    try: self.main_list_last_pos.append( self.getCurrentListPosition() )
                    except: self.main_list_last_pos.append( 0 )
                try:
                    if "Plugins " in self.type:
                        self.type = "Plugins"
                    else:
                        # cas standard
                        self.type = "racine"
                    self.updateList()
                except:
                    logger.LOG( logger.LOG_DEBUG, "Window::onAction::ACTION_PREVIOUS_MENU: Exception durant updateList()" )
                    logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )

                if self.main_list_last_pos:
                    self.setCurrentListPosition( self.main_list_last_pos.pop() )

            elif action == ACTION_SHOW_INFO:
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
            downloadOK = True
            correctionPM3bidon = False
            self.index = self.getCurrentListPosition()

            source = self.curDirList[ self.index ]

            if self.type == self.downloadTypeList[ 0 ]:   #Themes
                # Verifions le themes en cours d'utilisation
                mySkinInUse = xbmc.getSkinDir()
                if mySkinInUse in source:
                    # Impossible de telecharger une skin en cours d'utlisation
                    dialog = xbmcgui.Dialog()
                    dialog.ok( _( 117 ), _( 118 ), _( 119 ) )
                    downloadOK = False
                if 'Project Mayhem III' in source and self.USRPath == True:
                    self.linux_chmod( self.PMIIIDir )
                    if self.rightstest == True:
                        self.localdirList[ 0 ]= self.PMIIIDir
                        downloadOK = True
                        correctionPM3bidon = True
                    else:
                        dialog = xbmcgui.Dialog()
                        dialog.ok( _( 117 ), _( 120 ) )
                        downloadOK = False
            elif self.type == self.downloadTypeList[ 1 ] and self.USRPath == True:   #Linux Scrapers
                self.linux_chmod( self.scraperDir )
                if self.rightstest == True :
                    downloadOK = True
                else:
                    dialog = xbmcgui.Dialog()
                    dialog.ok( _( 117 ), _( 121 ) )
                    downloadOK = False

            if source.endswith( 'zip' ) or source.endswith( 'rar' ):
                self.targetDir = self.localdirList[ self.downloadTypeList.index( self.type ) ]
                self.localdirList[ self.downloadTypeList.index( self.type ) ]= self.CacheDir

            if downloadOK == True:
                continueDownload = True

                # on verifie le si on a deja telecharge cet element ( ou une de ses version anterieures )
                isDownloaded, localDirPath = self.passionFTPCtrl.isAlreadyDownloaded( source, self.remotedirList[ self.downloadTypeList.index( self.type ) ], self.downloadTypeList.index( self.type ) )

                if ( isDownloaded ) and ( localDirPath != None ):
                    logger.LOG( logger.LOG_NOTICE, "Repertoire deja present localement" )
                    # On traite le repertorie deja present en demandant a l'utilisateur de choisir
                    continueDownload = self.processOldDownload( localDirPath )
                else:
                    logger.LOG( logger.LOG_DEBUG, "localDirPath: %s", repr( localDirPath ) )
                    logger.LOG( logger.LOG_DEBUG, "isDownloaded: %s", repr( isDownloaded ) )

                if continueDownload == True:
                    # Fenetre de telechargement

                    dp = xbmcgui.DialogProgress()
                    lenbasepath = len( self.remotedirList[ self.downloadTypeList.index( self.type ) ] )
                    downloadItem = source[ lenbasepath: ]
                    percent = 0
                    dp.create( _( 122 ) % downloadItem, _( 123 ) % percent )

                    # Type est desormais reellement le type de download, on utlise alors les liste pour recuperer le chemin que l'on doit toujours passer
                    # on appel la classe passionFTPCtrl avec la source a telecharger
                    downloadStatus = self.passionFTPCtrl.download( source, self.remotedirList[ self.downloadTypeList.index( self.type ) ], self.downloadTypeList.index( self.type ), progressbar_cb=self.updateProgress_cb, dialogProgressWin = dp )
                    #dp.close()

                    if downloadStatus == -1:
                        # Telechargment annule par l'utilisateur
                        title = _( 124 )
                        message1 = "%s: %s" % ( self.type, downloadItem )
                        message2 = _( 125 )
                        message3 = _( 126 )
                        if xbmcgui.Dialog().yesno( title, message1, message2, message3 ):
                            logger.LOG( logger.LOG_WARNING, "Suppression du repertoire %s", localDirPath )
                            if os.path.isdir( localDirPath ):
                                if self.deleteDir( localDirPath ):
                                    xbmcgui.Dialog().ok( _( 127 ), _( 128 ), localDirPath, _( 129 ) )
                                else:
                                    xbmcgui.Dialog().ok( _( 111 ), _( 130 ), localDirPath )
                            else:
                                try:
                                    os.remove( localDirPath )
                                    xbmcgui.Dialog().ok( _( 131 ), _( 132 ), localDirPath, _( 129 ) )
                                except Exception, e:
                                    xbmcgui.Dialog().ok( _( 111 ), _( 133 ), localDirPath )
                    else:
                        title = _( 134 )
                        message1 = "%s: %s" % ( self.type, downloadItem )
                        message2 = _( 135 )
                        message3 = self.localdirList[ self.downloadTypeList.index( self.type ) ]

                        self._save_downloaded_property()
                        xbmcgui.Dialog().ok( title, message1, message2, message3 )

                    #TODO: Attention correctionPM3bidon n'est pa defini dans le cas d'un scraper ou script
                    #      Je l'ai donc defini a False au debut
                    # On remet a la bonne valeur initiale self.localdirList[ 0 ]
                    if correctionPM3bidon == True:
                        self.localdirList[ 0 ] = themesDir
                        correctionPM3bidon = False
                    # On se base sur l'extension pour determiner si on doit telecharger dans le cache.
                    # Un tour de passe passe est fait plus haut pour echanger les chemins de destination avec le cache, le chemin de destination
                    # est retabli ici 'il s'agit de targetDir'
                    if downloadItem.endswith( 'zip' ) or downloadItem.endswith( 'rar' ):
                        if downloadStatus != -1:
                            installCancelled = False
                            installError = None
                            #dp = xbmcgui.DialogProgress()
                            #dp.create( _( 136 ) % downloadItem, _( 123 ) % percent )
                            #dialogUI = xbmcgui.DialogProgress()
                            dp.create( _( 137 ), _( 138 ) % downloadItem, _( 110 ) )

                            #Appel de la classe d'extraction des archives
                            remoteDirPath = self.remotedirList[ self.downloadTypeList.index( self.type ) ]#chemin ou a ete telecharge le script
                            localDirPath = self.localdirList[ self.downloadTypeList.index( self.type ) ]
                            archive = source.replace( remoteDirPath, localDirPath + os.sep )#remplacement du chemin de l'archive distante par le chemin local temporaire
                            self.localdirList[ self.downloadTypeList.index( self.type ) ] = self.targetDir
                            #fichierfinal0 = archive.replace( localDirPath, self.localdirList[ self.downloadTypeList.index( self.type ) ] )
                            #if fichierfinal0.endswith( '.zip' ):
                            #    fichierfinal = fichierfinal0.replace( '.zip', '' )
                            #elif fichierfinal0.endswith( '.rar' ):
                            #    fichierfinal = fichierfinal0.replace( '.rar', '' )

                            import extractor
                            process_error = False
                            # on extrat tous dans le cache et si c'est OK on copy par la suite
                            file_path, OK = extractor.extract( archive, report=True )
                            #print OK, file_path
                            if self.type == "Scrapers":
                                # cas des Scrapers
                                # ----------------
                                #self.extracter.extract( archive, self.localdirList[ self.downloadTypeList.index( self.type ) ] )
                                destination = self.localdirList[ self.downloadTypeList.index( self.type ) ]
                                if ( OK == bool( file_path ) ) and os.path.exists( file_path ):
                                    extractor.copy_inside_dir( file_path, destination )
                            else:
                                # Cas des scripts et plugins
                                # --------------------------
                                # Recuperons le nom du repertorie a l'interieur de l'archive:
                                dirName = ""
                                if ( OK == bool( file_path ) ) and os.path.exists( file_path ):
                                    dirName = os.path.basename( file_path )#self.extracter.getDirName( archive )
                                    destination = os.path.join( self.localdirList[ self.downloadTypeList.index( self.type ) ], os.path.basename( file_path ) )

                                if dirName == "":
                                    installError = _( 139 ) % archive
                                    logger.LOG( logger.LOG_ERROR, "Erreur durant l'extraction de %s - impossible d'extraire le nom du repertoire", archive )
                                else:
                                    #destination = os.path.join( self.localdirList[ self.downloadTypeList.index( self.type ) ], dirName )
                                    logger.LOG( logger.LOG_NOTICE, destination )
                                    if os.path.exists( destination ):
                                        # Repertoire deja present
                                        # On demande a l'utilisateur ce qu'il veut faire
                                        if self.processOldDownload( destination ):
                                            try:
                                                #logger.LOG( logger.LOG_NOTICE, "Extraction de %s vers %s", archive, self.localdirList[ self.downloadTypeList.index( self.type ) ] )
                                                #self.extracter.extract( archive, self.localdirList[ self.downloadTypeList.index( self.type ) ] )
                                                if ( OK == bool( file_path ) ) and os.path.exists( file_path ):
                                                    extractor.copy_dir( file_path, destination )
                                            except:
                                                process_error = True
                                        else:
                                            installCancelled = True
                                            logger.LOG( logger.LOG_WARNING, "L'installation de %s a ete annulee par l'utilisateur", downloadItem  )
                                    else:
                                        # Le Repertoire n'est pas present localement -> on peut deplacer le repertoire depuis cache
                                        try:
                                            #logger.LOG( logger.LOG_NOTICE, "Extraction de %s vers %s", archive, self.localdirList[ self.downloadTypeList.index( self.type ) ] )
                                            #self.extracter.extract( archive, self.localdirList[ self.downloadTypeList.index( self.type ) ] )
                                            if ( OK == bool( file_path ) ) and os.path.exists( file_path ):
                                                extractor.copy_dir( file_path, destination )
                                        except:
                                            process_error = True

                            del extractor
                            # Close the Loading Window
                            #dialogUI.close()

                            if process_error:
                                installError = _( 140 ) % archive
                                logger.LOG( logger.LOG_ERROR, "Exception durant l'extraction de %s", archive )
                                logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )

                            if installCancelled == False and installError == None:
                                self._save_downloaded_property()
                                xbmcgui.Dialog().ok( _( 141 ), _( 142 ) % downloadItem, _( 143 ) )
                            else:
                                if installError != None:
                                    # Erreur durant l'install ( meme si on a annule )
                                    xbmcgui.Dialog().ok( _( 144 ), installError, _( 145 ) )
                                elif installCancelled == True:
                                    # Install annulee
                                    xbmcgui.Dialog().ok( _( 146 ), _( 147 ) % downloadItem )
                                else:
                                    # Install annulee
                                    xbmcgui.Dialog().ok( _( 144 ), _( 148 ), _( 145 ) )
                        else:
                            # On remet a la bonne valeur initiale self.localdirList
                            self.localdirList[ self.downloadTypeList.index( self.type ) ] = self.targetDir

                    # Close the Loading Window
                    dp.close()
        except:
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )

    def _close_script( self ):
        #**IMPORTANT** faut annuler les thread avant de fermer le script, sinon xbmc risque de planter
        #NB: le meme scenario va ce produire si vous fermer ou redemarrer xbmc avec le script en marche
        #on annule les thread
        self._stop_rss_timer()
        try: self.itemInfosManager.get_info_warehouse().getImage_thread.cancel()
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
                try: self.main_list_last_pos.append( self.getCurrentListPosition() )
                except: self.main_list_last_pos.append( 0 )
                if ( self.type == "racine" ):
                    self.index = self.getCurrentListPosition()
                    self.type = self.downloadTypeList[ self.racineDisplayList[ self.getCurrentListPosition() ] ] # On utilise le filtre
                    self.updateList() #on raffraichit la page pour afficher le contenu

                elif ( self.type == "Plugins" ):
                    self.index = self.getCurrentListPosition()
                    self.type = self.downloadTypeList[ self.pluginDisplayList[ self.getCurrentListPosition() ] ] # On utilise le filtre
                    self.updateList() #on raffraichit la page pour afficher le contenu

                else:
                    self.install_add_ons()

            elif controlID == self.CONTROL_OPTIONS_BUTTON:
                self._show_settings()

            elif controlID == self.CONTROL_FILE_MGR_BUTTON:
                thumb_size_on_load = self.settings[ "thumb_size" ]
                from FileManager import show_file_manager
                show_file_manager( self )
                #on a plus besoin du manager, on le delete
                del show_file_manager
                if thumb_size_on_load != self.settings[ "thumb_size" ]:
                    self.updateList() #on raffraichit la page pour afficher la taille des vignettes

            elif controlID == self.CONTROL_FORUM_BUTTON:
                self._show_direct_infos()

            elif controlID == self.CONTROL_EXIT_BUTTON:
                self._close_script()

            else:
                pass

        except:
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )

    def _load_downloaded_property( self ):
        try:
            file_path = os.path.join( logger.DIRECTORY_DATA, "downloaded.txt" )
            self.downloaded_property = eval( file( file_path, "r" ).read() )
        except:
            logger.EXC_INFO( logger.LOG_DEBUG, sys.exc_info(), self )
            self.downloaded_property = set()

    def _save_downloaded_property( self ):
        try:
            self._load_downloaded_property()
            selected_label = self.getListItem( self.getCurrentListPosition() ).getLabel()
            self.downloaded_property.update( [ md5.new( selected_label ).hexdigest() ] )
            file_path = os.path.join( logger.DIRECTORY_DATA, "downloaded.txt" )
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

    def updateList( self ):
        """
        Mise a jour de la liste affichee
        """
        self._load_downloaded_property()
        if not xbmc.getCondVisibility( "Window.IsActive(progressdialog)" ):
            DIALOG_PROGRESS.create( _( 0 ), _( 104 ), _( 110 ) )
        # On verifie self.type qui correspond au type de liste que l'on veut afficher
        if ( self.type == "racine" ):
            #liste virtuelle des sections
            #del self.curDirList[ : ] # on vide la liste
            self.curDirList = self.racineDisplayList

        elif ( self.type == "Plugins" ):
            #liste virtuelle des sections
            self.curDirList = self.pluginDisplayList
        #elif ( self.type == "Plugins Musique" ) or ( self.type == "Plugins Images" ) or ( self.type == "Plugins Programmes" ) or ( self.type == "Plugins Videos" ):
        elif "Plugins " in self.type:
            self.curDirList = self.passionFTPCtrl.getDirList( self.remotedirList[ self.pluginDisplayList[ self.index ] ] )
        else:
            #liste virtuelle des sections
            #del self.curDirList[ : ] # on vide la liste

            #liste physique d'une section sur le ftp
            self.curDirList = self.passionFTPCtrl.getDirList( self.remotedirList[ self.index ] )

        #xbmcgui.lock()

        # Clear all ListItems in this control list
        if hasattr( self, 'clearProperties' ):
            self.clearProperties()
        self.clearList()
        self.listitems = []

        # Calcul du nombre d'elements de la liste
        itemnumber = len( self.curDirList )

        # On utilise la fonction range pour faire l'iteration sur index
        for j in range( itemnumber ):
            imagePath = ""
            if ( self.type == "racine" ):
                # Nom de la section
                sectionName = self.downloadTypeList[ self.racineDisplayList[ j ] ] # On utilise le filtre
                # Met a jour le titre:
                self.setProperty( "Category", _( 10 ) )

                # Affichage de la liste des sections
                # -> On compare avec la liste affichee dans l'interface
                if sectionName == self.downloadTypeList[ 0 ]:
                    # Theme
                    imagePath = "icone_theme.png"
                    sectionLocTitle = _( 11 )
                elif sectionName == self.downloadTypeList[ 1 ]:
                    # Scraper
                    imagePath = "icone_scrapper.png"
                    sectionLocTitle = _( 12 )
                elif sectionName == self.downloadTypeList[ 2 ]:
                    # Script
                    imagePath = "icone_script.png"
                    sectionLocTitle = _( 13 )
                elif sectionName == self.downloadTypeList[ 3 ]:
                    # Plugin
                    imagePath = "icone_script.png"
                    sectionLocTitle = _( 14 )

                displayListItem = xbmcgui.ListItem( sectionLocTitle, "", iconImage=imagePath, thumbnailImage=imagePath )
                displayListItem.setProperty( "Downloaded", "" )
                displayListItem.setProperty( "previewPicture",  imagePath )
                self.addItem( displayListItem )
                
            elif ( self.type == "Plugins" ):
                # Nom de la section
                sectionName = self.downloadTypeList[ self.pluginDisplayList[ j ] ] # On utilise le filtre
                # Met a jour le titre:
                self.setProperty( "Category", _( 14 ) )
            
                if sectionName == self.downloadTypeList[ 4 ]:  
                    # Music
                    imagePath = "passion-icone-music.png"
                    sectionLocTitle = _( 15 )
                elif sectionName == self.downloadTypeList[ 5 ]: 
                    # Pictures
                    imagePath = "passion-icone-pictures.png"
                    sectionLocTitle = _( 16 )
                elif sectionName == self.downloadTypeList[ 6 ]: 
                    # Programs
                    imagePath = "passion-icone-programs.png"
                    sectionLocTitle = _( 17 )
                elif sectionName == self.downloadTypeList[ 7 ]: 
                    # Video
                    imagePath = "passion-icone-video.png"
                    sectionLocTitle = _( 18 )

                displayListItem = xbmcgui.ListItem( sectionLocTitle, "", iconImage=imagePath, thumbnailImage=imagePath )
                displayListItem.setProperty( "Downloaded", "" )
                displayListItem.setProperty( "previewPicture",  imagePath )
                self.addItem( displayListItem )
            
            
            #elif ( self.type == "Plugins Musique" ) or ( self.type == "Plugins Images" ) or ( self.type == "Plugins Programmes" ) or ( self.type == "Plugins Videos" ):
            elif "Plugins " in self.type:
                # Element de la liste
                ItemListPath = self.curDirList[ j ]

                lenindex = len( self.remotedirList[ self.pluginDisplayList[ self.index ] ] ) # on a tjrs besoin de connaitre la taille du chemin de base pour le soustraire/retirer du chemin global plus tard

                # Met a jour le titre et les icones:
                if self.type == self.downloadTypeList[ 4 ]:  
                    # Music
                    self.setProperty( "Category", _( 15 ) )
                    imagePath = "passion-icone-music.png"
                elif self.type == self.downloadTypeList[ 5 ]: 
                    # Pictures
                    self.setProperty( "Category", _( 16 ) )
                    imagePath = "passion-icone-pictures.png"
                elif self.type == self.downloadTypeList[ 6 ]:
                    # Programs
                    self.setProperty( "Category", _( 17 ) )
                    imagePath = "passion-icone-programs.png"
                elif self.type == self.downloadTypeList[ 7 ]:
                    # Video
                    self.setProperty( "Category", _( 18 ) )
                    imagePath = "passion-icone-video.png"

                # nettoyage du nom: replace les souligner pas un espace et enleve l'extension
                try:
                    item2download = ItemListPath[ lenindex: ].replace( "_", " " )
                    if self.settings.get( "hide_extention", True ):
                        item2download = os.path.splitext( item2download )[ 0 ]
                except:
                    item2download = ItemListPath[ lenindex: ]
                DIALOG_PROGRESS.update( -1, _( 103 ), item2download, _( 110 ) )

                if self.downloaded_property.__contains__( md5.new( item2download ).hexdigest() ):
                    already_downloaded = "true"
                else:
                    already_downloaded = ""

                displayListItem = xbmcgui.ListItem( item2download, "", iconImage=imagePath, thumbnailImage=imagePath )
                displayListItem.setProperty( "Downloaded", already_downloaded )
                self.set_item_info( displayListItem, ItemListPath )
                self.addItem( displayListItem )
                DIALOG_PROGRESS.update( -1, _( 103 ), item2download, _( 110 ) )

            else:
                # Element de la liste
                ItemListPath = self.curDirList[ j ]

                #affichage de l'interieur d'une section
                #self.numindex = self.index
                lenindex = len( self.remotedirList[ self.index ] ) # on a tjrs besoin de connaitre la taille du chemin de base pour le soustraire/retirer du chemin global plus tard

                # Met a jour le titre et les icones:
                if self.type == self.downloadTypeList[ 0 ]: #Themes
                    self.setProperty( "Category", _( 11 ) )
                    imagePath = "icone_theme.png"
                elif self.type == self.downloadTypeList[ 1 ]: #Scrapers
                    self.setProperty( "Category", _( 12 ) )
                    imagePath = "icone_scrapper.png"
                elif self.type == self.downloadTypeList[ 2 ]: #Scripts
                    self.setProperty( "Category", _( 13 ) )
                    imagePath = "icone_script.png"

                # nettoyage du nom: replace les souligner pas un espace et enleve l'extension
                try:
                    item2download = ItemListPath[ lenindex: ].replace( "_", " " )
                    if self.settings.get( "hide_extention", True ):
                        item2download = os.path.splitext( item2download )[ 0 ]
                except:
                    item2download = ItemListPath[ lenindex: ]
                DIALOG_PROGRESS.update( -1, _( 103 ), item2download, _( 110 ) )

                if self.downloaded_property.__contains__( md5.new( item2download ).hexdigest() ):
                    already_downloaded = "true"
                else:
                    already_downloaded = ""

                displayListItem = xbmcgui.ListItem( item2download, "", iconImage=imagePath, thumbnailImage=imagePath )
                displayListItem.setProperty( "Downloaded", already_downloaded )
                self.set_item_info( displayListItem, ItemListPath )
                self.addItem( displayListItem )
                DIALOG_PROGRESS.update( -1, _( 103 ), item2download, _( 110 ) )

            # utiliser pour remettre la liste courante a jour lorsqu'on reviens sur cette fenetre depuis le forum ou le manager
            self.listitems.append( displayListItem )
        self.current_cat = unicode( xbmc.getInfoLabel( 'Container.Property(Category)' ), 'utf-8')
        #xbmcgui.unlock()

        DIALOG_PROGRESS.close()

    def set_item_info( self, listitem, ipath ):
        #infos = fileName, title, version, language, date , previewPicture, previewVideoURL, description_fr, description_en, thumbnail
        try:
            infos = self.itemInfosManager.get_info_warehouse().getInfo( itemName=os.path.basename( ipath ), itemType=self.type, listitem=listitem )
            #listitem.setProperty( "fileName",        infos[ 0 ] or "" )
            listitem.setProperty( "title",           infos[ 1 ] or "" )
            listitem.setProperty( "version",         infos[ 2 ] or "" )
            listitem.setProperty( "language",        infos[ 3 ] or "" )
            listitem.setProperty( "date",            infos[ 4 ] or "" )
            listitem.setProperty( "added",           infos[ 5 ] or infos[ 4 ] or "" )
            listitem.setProperty( "previewPicture",  infos[ 6 ] or "passion-noImageAvailable.jpg" ) # used for simulate fanart
            #listitem.setProperty( "previewVideoURL", infos[ 7 ] or "" )

            desc_fr = infos[ 8 ] or ""
            desc_us = infos[ 9 ] or ""
            if ( xbmc.getLanguage().lower() == "french" ):
                listitem.setProperty( "description", desc_fr or desc_us )
            else:
                listitem.setProperty( "description", desc_us or desc_fr )

            listitem.setProperty( "author", infos[ 11 ] or "" )

        except:
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )

    def deleteDir( self, path ):
        """
        Efface un repertoire et tout son contenu ( le repertoire n'a pas besoin d'etre vide )
        retourne True si le repertoire est effece False sinon
        """
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
        folder: chemin du repertpoire local
        """
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
                self.deleteDir( localAbsDirPath )
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
