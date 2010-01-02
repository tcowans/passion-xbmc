
# Modules general
import os
import sys
from traceback import print_exc

# Modules XBMC
import xbmc
import xbmcgui

# Modules custom
import shutil2
from CONF import *
from utilities import *
from FileManager import *


# INITIALISATION CHEMIN RACINE
ROOTDIR = os.getcwd().replace( ";", "" )

#FONCTION POUR RECUPERER LES LABELS DE LA LANGUE.
_ = sys.modules[ "__main__" ].__language__

DIALOG_PROGRESS = xbmcgui.DialogProgress()


############################################################################
# Get actioncodes from keymap.xml
############################################################################
#ACTION_MOVE_LEFT = 1
#ACTION_MOVE_RIGHT = 2
#ACTION_MOVE_UP = 3
#ACTION_MOVE_DOWN = 4
#ACTION_PAGE_UP = 5
#ACTION_PAGE_DOWN = 6
#ACTION_SELECT_ITEM = 7
#ACTION_HIGHLIGHT_ITEM = 8
ACTION_PARENT_DIR = 9
ACTION_PREVIOUS_MENU = 10
ACTION_SHOW_INFO = 11
#ACTION_PAUSE = 12
#ACTION_STOP = 13
#ACTION_NEXT_ITEM = 14
#ACTION_PREV_ITEM = 15
ACTION_CONTEXT_MENU = 117 # ACTION_MOUSE_RIGHT_CLICK *sa marche maintenant avec les derniere SVN*
CLOSE_CONTEXT_MENU = ( ACTION_PARENT_DIR, ACTION_PREVIOUS_MENU, ACTION_CONTEXT_MENU, )




##################################################


def copy_func( cpt_blk, taille_blk, total_taille ):
    try:
        updt_val = int( ( cpt_blk * taille_blk ) / 10.0 / total_taille )
        if updt_val > 100: updt_val = 100
        DIALOG_PROGRESS.update( updt_val )
    except:
        pass
        #DIALOG_PROGRESS.update( 100 )
    # DON'T ALLOW Progress().iscanceled() BUG CREATE, FIXED SOON
    #if xbmcgui.DialogProgress().iscanceled():
    #    xbmcgui.DialogProgress().close()


class FileMgrWindow( xbmcgui.WindowXML ):
    # control id's
    CONTROL_MAIN_LIST_START  = 50
    CONTROL_MAIN_LIST_END    = 59
    CONTROL_FORUM_BUTTON     = 305
    CONTROL_INSTALLER_BUTTON = 300
    CONTROL_OPTIONS_BUTTON   = 310
    CONTROL_EXIT_BUTTON      = 320

    def __init__( self, *args, **kwargs ):
        """
        Initialisation de l'interface
        """
        xbmcgui.WindowXML.__init__( self, *args, **kwargs )
        #from CONF import configCtrl
        self.configManager = configCtrl()
        if not self.configManager.is_conf_valid: raise

        #used for show cat from new home gui
        self.HomeAction = kwargs.get( "HomeAction" )

        self.rightstest        = kwargs[ "rightstest" ]
        self._show_settings    = kwargs[ "mainfunctions" ][ 0 ]
        self._close_script     = kwargs[ "mainfunctions" ][ 1 ]

        self.localdirList      = self.configManager.localdirList      # Liste des repertoire locaux

        self.itemTypeList      = self.configManager.typeList          # Liste des types des items geres (plugins, scripts, skins ...)
        self.itemThumbList     = self.configManager.thumbList         # Liste des icones standards
        self.rootDisplayList   = self.configManager.rootDisplayList   # Liste de la racine: Cette liste est un filtre ( utilisant l'index ) sur les listes downloadTypeList et localdirList
        self.pluginDisplayList = self.configManager.pluginDisplayList # Liste des plugins : Cette liste est un filtre ( utilisant l'index ) sur les listes downloadTypeList et localdirList

        self.curListType        = TYPE_ROOT
        self.currentItemList    = []
        self.index              = ""
        self.main_list_last_pos = []

        if self.HomeAction is not None:
            try:
                # exemple : self.HomeAction = 'TYPE, INDEX = TYPE_PLUGIN_VIDEO, 3'
                exec self.HomeAction
                self.curListType = TYPE
                self.index       = INDEX
            except:
                print_exc()

        self.fileMgr            = fileMgr()


    def onInit( self ):
        self.SET_VIEW_MODE = True
        try:
            # Title of the current pages

            self._get_settings()
            self._set_skin_colours()
            self.pardir_not_hidden = self.settings.get( "pardir_not_hidden", 1 )

            # Verifications des permissions sur les repertoires
            self.check_w_rights()

            self.updateDataAndList()
            self.set_view_mode()
            id = self.settings.get( "manager_view_mode", self.CONTROL_MAIN_LIST_START )
            xbmc.executebuiltin( "Container.SetViewMode(%i)" % id )

            if self.curListType == TYPE_ROOT:
                self.setProperty( "Category", _( 10 ) )

        except:
            print_exc()

    def onFocus( self, controlID ):
        #self.controlID = controlID
        #cette fonction n'est pas utiliser ici, mais dans les XML si besoin
        #Note: Mais il faut la declarer : )
        pass

    def onClick( self, controlID ):
        try:
            if ( self.CONTROL_MAIN_LIST_START <= controlID <= self.CONTROL_MAIN_LIST_END ):
                #Traitement si selection d'un element de la liste
                if self.pardir_not_hidden and self.getCurrentListPosition() == 0:
                    self.parentDir()
                elif ( self.curListType == TYPE_ROOT or self.curListType == TYPE_PLUGIN ):
                    try: self.main_list_last_pos.append( self.getCurrentListPosition() )
                    except: self.main_list_last_pos.append( 0 )
                    self.curListType = self.currentItemList[ self.getCurrentListPosition()-self.pardir_not_hidden ].type # On extrait le type de l'item selectionne
                    self.updateDataAndList()
                else:
                    self._show_context_menu()
            elif controlID == self.CONTROL_INSTALLER_BUTTON:
                self._close_dialog()
            elif controlID == self.CONTROL_FORUM_BUTTON:
                self._show_direct_infos()
            elif controlID == self.CONTROL_OPTIONS_BUTTON:
                self._show_settings()
                #on prend pas de chance reload ces fonctions
                self._get_settings()
                self._set_skin_colours()
                if self.pardir_not_hidden != self.settings.get( "pardir_not_hidden", 1 ):
                    self.pardir_not_hidden = self.settings.get( "pardir_not_hidden", 1 )
                    self.updateDataAndList()
            elif controlID == self.CONTROL_EXIT_BUTTON:
                self._close_dialog()
                #self._close_script()
        except:
            print_exc()

    def _show_direct_infos( self ):
        try:
            import ForumDirectInfos
            ForumDirectInfos.show_direct_infos()
            #on a plus besoin, on le delete
            del ForumDirectInfos
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
        self.index = self.getCurrentListPosition()

        try:
            # On va ici afficher un menu des options du gestionnaire de fichiers
            item_path     = self.currentItemList[ self.index-self.pardir_not_hidden ].local_path # On extrait le chemin de l'item
            item_basename = os.path.basename( item_path )

            if ( ( self.getListItem( self.index ).getProperty( "Running" ) == "true" ) or self.curListType == TYPE_ROOT or self.curListType == TYPE_PLUGIN ):
                # liste des options pour skin ou l'add-ons en court d'utilisation
                buttons = { 1003: _( 161 ), 1005: _( 185 ), 1006: _( 1002 ) }
            elif ( self.curListType == TYPE_SCRIPT ) or ( self.itemTypeList.index(self.curListType) in self.pluginDisplayList ):
                # liste des options pour plugins et scripts
                buttons = { 1000: _( 160 ), 1001: _( 157 ), 1002: _( 156 ), 1003: _( 161 ), 1004: _( 162 ), 1005: _( 185 ), 1006: _( 1002 ) }
            else:
                # liste des options pour skins et scrapers
                buttons = { 1001: _( 157 ), 1002: _( 156 ), 1003: _( 161 ), 1004: _( 162 ), 1005: _( 185 ), 1006: _( 1002 ) }

            from DialogContextMenu import show_context_menu
            selected = show_context_menu( buttons, self.get_view_mode() )
            del show_context_menu

            if selected == 1000: # Executer/Lancer
                if ( self.itemTypeList.index(self.curListType) in self.pluginDisplayList ):
                    # Cas d'un sous-plugin (video, musique ...)
                    # window id's : http://xbmc.org/wiki/?title=Window_IDs
                    if ( self.curListType == TYPE_PLUGIN_VIDEO ):
                        command = "XBMC.ActivateWindow(10025,plugin://video/%s/)" % ( item_basename, )
                    elif ( self.curListType == TYPE_PLUGIN_MUSIC ):
                        command = "XBMC.ActivateWindow(10502,plugin://music/%s/)" % ( item_basename, )
                    elif ( self.curListType == TYPE_PLUGIN_PROGRAMS ):
                        command = "XBMC.ActivateWindow(10001,plugin://programs/%s/)" % ( item_basename, )
                    elif ( self.curListType == TYPE_PLUGIN_PICTURES ):
                        command = "XBMC.ActivateWindow(10002,plugin://pictures/%s/)" % ( item_basename, )
                elif ( self.curListType == TYPE_SCRIPT ):
                    command = "XBMC.RunScript(%s)" % ( os.path.join( item_path, "default.py" ), )

                #on ferme le script en court pour pas generer des conflits
                self._close_dialog()
                self._close_script()
                #maintenant qu'il y a plus de conflit possible, on execute la command
                xbmc.executebuiltin( command )

            elif selected == 1001: # Renommer
                # Renommer l'element
                item_dirname  = os.path.dirname( item_path )

                if ( self.curListType == TYPE_SCRAPER ):
                    icon_path     = self.currentItemList[ self.index-self.pardir_not_hidden ].thumb # On extrait le chemin de l'icone
                    icon_basename = os.path.basename( icon_path )
                    default_basename = os.path.splitext( item_basename )[ 0 ]
                    keyboard = xbmc.Keyboard( default_basename, _( 154 ) )
                    keyboard.doModal()
                    if ( keyboard.isConfirmed() ):
                        inputText = keyboard.getText()
                        # ne renomme pas l'item si le nouveau nom est le meme que le default
                        if default_basename != inputText:
                            self.fileMgr.renameItem( item_dirname, item_basename, inputText + '.xml' )
                            if not icon_path in self.itemThumbList:
                                self.fileMgr.renameItem( item_dirname, icon_basename, icon_basename.replace( os.path.splitext(icon_basename)[0], inputText) )
                            xbmcgui.Dialog().ok( _( 155 ), inputText )
                            self.updateDataAndList()
                else:
                    keyboard = xbmc.Keyboard( item_basename, _( 154 ) )
                    keyboard.doModal()
                    if ( keyboard.isConfirmed() ):
                        inputText = keyboard.getText()
                        # ne renomme pas l'item si le nouveau nom est le meme que le default
                        if item_basename != inputText:
                            self.fileMgr.renameItem( item_dirname, item_basename, inputText )
                            xbmcgui.Dialog().ok( _( 155 ), inputText )
                            self.updateDataAndList()

            elif selected == 1002:
                # Supprimer l'element
                if ( self.curListType == TYPE_SCRAPER ):
                    icon_path      = self.currentItemList[ self.index-self.pardir_not_hidden ].thumb # On extrait le chemin de l'icone
                    item_shortname = os.path.splitext(item_basename)[0] # Sans extension
                    if xbmcgui.Dialog().yesno( _( 158 )%item_shortname, _( 159 )%item_shortname ):
                        self.fileMgr.deleteItem( item_path )
                        if not icon_path in self.itemThumbList:
                            self.fileMgr.deleteItem( icon_path )
                        self.updateDataAndList()
                else:
                    if xbmcgui.Dialog().yesno( _( 158 )%item_basename, _( 159 )%item_basename ):
                        self.fileMgr.deleteItem( item_path )
                        self.updateDataAndList()

            elif selected == 1003:
                # copier l'element
                if ( self.curListType == TYPE_SCRAPER ):
                    #TODO : A optimiser, on doit pouvoir faire mieux
                    item_dirname   = os.path.dirname( item_path )
                    item_shortname = os.path.splitext(item_basename)[0] # Sans extension
                    icon_path      = self.currentItemList[ self.index-self.pardir_not_hidden ].thumb # On extrait le chemin de l'icone
                    icon_ext       = os.path.splitext(os.path.basename( icon_path ))[1]
                    new_path       = xbmcgui.Dialog().browse( 3, _( 167 ) % item_shortname, "files" )
                    if bool( new_path ):
                        src = os.path.normpath( os.path.join( item_dirname, item_shortname ) )
                        dst = os.path.normpath( os.path.join( new_path, item_shortname ) )
                        if xbmcgui.Dialog().yesno( _( 163 ), _( 165 ), src, dst ):
                            DIALOG_PROGRESS.create( _( 176 ), _( 178 ) + src, _( 179 ) + dst, _( 110 ) )
                            try:
                                shutil2.copy( src + ".xml", dst + ".xml", reportcopy=copy_func, overwrite=True )
                                if os.path.exists( src + icon_ext ):
                                    shutil2.copy( src + icon_ext, dst + icon_ext, reportcopy=copy_func, overwrite=True )
                            except:
                                xbmcgui.Dialog().ok( _( 169 ), _( 170 ), _( 171 ) )
                                print_exc()
                            #self.updateDataAndList()
                            DIALOG_PROGRESS.close()
                else:
                    new_path = xbmcgui.Dialog().browse( 3, _( 167 ) % item_basename, "files" )
                    if bool( new_path ):
                        src = os.path.normpath( item_path )
                        dst = os.path.normpath( os.path.join( new_path, item_basename ) )
                        if xbmcgui.Dialog().yesno( _( 163 ), _( 165 ), src, dst ):
                            DIALOG_PROGRESS.create( _( 176 ), _( 178 ) + src, _( 179 ) + dst, _( 110 ) )
                            try:
                                if os.path.isdir( src ):
                                    if not os.path.isdir( os.path.dirname( dst ) ):
                                        os.makedirs( os.path.dirname( dst ) )
                                    shutil2.copytree( src, dst, reportcopy=copy_func, overwrite=True )
                                else:
                                    shutil2.copy( src, dst, reportcopy=copy_func, overwrite=True )
                            except:
                                xbmcgui.Dialog().ok( _( 169 ), _( 170 ), _( 171 ) )
                                print_exc()
                            #self.updateDataAndList()
                            DIALOG_PROGRESS.close()

            elif selected == 1004:
                # deplacer l'element
                if ( self.curListType == TYPE_SCRAPER ):
                    #TODO : A optimiser, on doit pouvoir faire mieux
                    item_dirname   = os.path.dirname( item_path )
                    item_shortname = os.path.splitext(item_basename)[0] # Sans extension
                    icon_path      = self.currentItemList[ self.index-self.pardir_not_hidden ].thumb # On extrait le chemin de l'icone
                    icon_ext       = os.path.splitext(os.path.basename( icon_path ))[1]
                    new_path       = xbmcgui.Dialog().browse( 3, _( 167 ) % item_shortname, "files" )
                    if bool( new_path ):
                        src = os.path.normpath( os.path.join( item_dirname, item_shortname ) )
                        dst = os.path.normpath( os.path.join( new_path, item_shortname ) )
                        if xbmcgui.Dialog().yesno( _( 164 ), _( 166 ), src, dst ):
                            DIALOG_PROGRESS.create( _( 177 ), _( 178 ) + src, _( 179 ) + dst, _( 110 ) )
                            try:
                                shutil2.copy( src + ".xml", dst + ".xml", reportcopy=copy_func, overwrite=True )
                                self.fileMgr.deleteItem( src + ".xml" )
                                if os.path.exists( src + icon_ext ):
                                    shutil2.copy( src + icon_ext, dst + icon_ext, reportcopy=copy_func, overwrite=True )
                                    self.fileMgr.deleteItem( src + icon_ext )
                            except:
                                xbmcgui.Dialog().ok( _( 169 ), _( 172 ), _( 173 ) )
                                print_exc()
                            self.updateDataAndList()
                            DIALOG_PROGRESS.close()
                else:
                    new_path = xbmcgui.Dialog().browse( 3, _( 168 ) % item_basename, "files" )
                    if bool( new_path ):
                        src = os.path.normpath( item_path )
                        dst = os.path.normpath( os.path.join( new_path, item_basename ) )
                        if xbmcgui.Dialog().yesno( _( 164 ), _( 166 ), src, dst ):
                            DIALOG_PROGRESS.create( _( 177 ), _( 178 ) + src, _( 179 ) + dst, _( 110 ) )
                            try:
                                if os.path.isdir( src ):
                                    if not os.path.isdir( os.path.dirname( dst ) ):
                                        os.makedirs( os.path.dirname( dst ) )
                                    shutil2.copytree( src, dst, reportcopy=copy_func, overwrite=True )
                                else:
                                    shutil2.copy( src, dst, reportcopy=copy_func, overwrite=True )
                                self.fileMgr.deleteItem( src )
                            except:
                                xbmcgui.Dialog().ok( _( 169 ), _( 172 ), _( 173 ) )
                                print_exc()
                            self.updateDataAndList()
                            DIALOG_PROGRESS.close()

            elif selected == 1005:
                # calcule de l'element
                src = os.path.normpath( item_path )
                DIALOG_PROGRESS.create( _( 5 ), _( 186 ), src )
                size = get_infos_path( src, get_size=True, report_progress=DIALOG_PROGRESS )[ 0 ]
                DIALOG_PROGRESS.close()
                self.getListItem( self.index ).setProperty( "size", size )
            elif selected == 1006:
                self._switch_media()
            else:
                pass
        except:
            print_exc()

    def _switch_media( self ):
        try:
            from DialogContextMenu import show_context_menu
            buttons = { 1000: _( 11 ), 1001: _( 12 ), 1002: _( 13 ), 1003: _( 14 ), 1004: _( 18 ), 1005: _( 16 ), 1006: _( 15 ), 1007: _( 17 ) }
            selected = show_context_menu( buttons, self.get_view_mode() )
            del show_context_menu
            switch = None
            if selected == 1000:
                switch = TYPE_SKIN
                self.index = 0
            elif selected == 1001:
                switch = TYPE_SCRAPER
                self.index = 1
            elif selected == 1002:
                switch = TYPE_SCRIPT
                self.index = 2
            elif selected == 1003:
                switch = TYPE_PLUGIN
                self.index = 3
            elif selected == 1004:
                switch = TYPE_PLUGIN_VIDEO
                self.index = 3
            elif selected == 1005:
                switch = TYPE_PLUGIN_PICTURES
                self.index = 1
            elif selected == 1006:
                switch = TYPE_PLUGIN_MUSIC
                self.index = 0
            elif selected == 1007:
                switch = TYPE_PLUGIN_PROGRAMS
                self.index = 2
            if switch:
                self.curListType = switch
                self.updateDataAndList()
        except:
            print_exc()

    def parentDir( self ):
        # remonte l'arborescence
        if self.curListType != TYPE_ROOT:
            if not self.main_list_last_pos:
                try: self.main_list_last_pos.append( self.getCurrentListPosition() )
                except: self.main_list_last_pos.append( 0 )
            try:
                # on verifie si on est un sous plugin
                #if ( TYPE_PLUGIN + ' ' in self.curListType ):
                if ( self.itemTypeList.index(self.curListType) in self.pluginDisplayList ):
                    self.curListType = TYPE_PLUGIN
                else:
                    # cas standard
                    self.curListType = TYPE_ROOT
                self.updateDataAndList()
            except:
                print "FileMgrWindow::onAction::ACTION_PREVIOUS_MENU: Exception durant updateList()"
                print_exc()

        if self.main_list_last_pos:
            self.setCurrentListPosition( self.main_list_last_pos.pop() )

    def onAction( self, action ):
        """
        Remonte l'arborescence et quitte le script
        """
        try:
            if ( action == ACTION_CONTEXT_MENU ):# and not ( self.curListType == TYPE_ROOT or self.curListType == TYPE_PLUGIN ):
                # Affiche les options pour l'utilisateur
                if self.pardir_not_hidden and self.getCurrentListPosition() == 0:
                    # bizard :O pas capable de trouver l'inverse !!!!
                    pass
                else: self._show_context_menu()

            elif ( action == ACTION_PREVIOUS_MENU ):
                # Sortie du script
                self._close_dialog()

            elif ( action == ACTION_PARENT_DIR ):
                 self.parentDir()

            elif ( action == ACTION_SHOW_INFO ):
                # Affiche la description de l'item selectionner
                pass

        except:
            print "FileMgrWindow::onAction: Exception"
            print_exc()

    def _get_settings( self, defaults=False ):
        """ reads settings """
        self.settings = Settings().get_settings( defaults=defaults )
        try:
            self.getControl( self.CONTROL_FORUM_BUTTON ).setVisible( not self.settings.get( "hide_forum", False ) )
        except:
            pass

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

    def updateDataAndList( self ):
        DIALOG_PROGRESS.create( _( 0 ), _( 104 ), _( 110 ) )
        try:
            self.updateData() # On met a jour les donnees
            self.updateList() # On raffraichit la page pour afficher le contenu
        except:
            print_exc()
        DIALOG_PROGRESS.close()

    def updateData( self ):
        """
        Mise a jour des donnnees de la liste courante
        """
        try:
            # Vide la liste
            del self.currentItemList[:]

            #if xbmc.getCondVisibility( "!Window.IsActive(progressdialog)" ):
            #    DIALOG_PROGRESS.create( _( 0 ), _( 104 ), _( 110 ) )

            # Recuperation des infos
            if ( self.curListType == TYPE_ROOT ):
                for index, filterIdx in enumerate( self.rootDisplayList ):
                    listItemObj = ListItemObject( type=self.itemTypeList[ filterIdx ], name=self.itemTypeList[ filterIdx ], local_path=self.localdirList[ filterIdx ], thumb=self.itemThumbList[ filterIdx ] )
                    self.currentItemList.append(listItemObj)
            elif ( self.curListType == TYPE_PLUGIN ):
                for index, filterIdx in enumerate( self.pluginDisplayList ):
                    listItemObj = ListItemObject( type=self.itemTypeList[ filterIdx ], name=self.itemTypeList[ filterIdx ], local_path=self.localdirList[ filterIdx ], thumb=self.itemThumbList[ filterIdx ] )
                    self.currentItemList.append(listItemObj)
            #elif TYPE_PLUGIN + ' ' in self.curListType:
            elif ( ( self.curListType == TYPE_SCRIPT ) or ( self.itemTypeList.index(self.curListType) in self.pluginDisplayList ) ):
                listdir = self.fileMgr.listDirFiles( self.localdirList[ self.itemTypeList.index(self.curListType) ] )
                listdir.sort( key=str.lower )
                for index, item  in enumerate( listdir ):
                    # Note:  dans le futur on pourra ici initialiser 'thumb' avec l'icone du script, plugin, themes ...
                    #        pour le moment on prend l'icone correspondant au type
                    script_path    = os.path.join(self.localdirList[ self.itemTypeList.index(self.curListType) ],item)
                    thumbnail_path = os.path.join(script_path, "default.tbn")
                    if not os.path.exists(thumbnail_path):
                        thumbnail_path = self.itemThumbList[ self.itemTypeList.index(self.curListType) ]
                    listItemObj = ListItemObject( type=self.curListType, name=item, local_path=script_path, thumb=thumbnail_path )
                    self.currentItemList.append(listItemObj)
            elif ( self.curListType == TYPE_SCRAPER ):
                listdir = self.fileMgr.listDirFiles( self.localdirList[ self.itemTypeList.index(self.curListType) ] )
                listdir.sort( key=str.lower )
                for index, item  in enumerate( listdir ):
                    if (item.endswith( '.xml' )):
                        # on cherche l'image
                        scraper_base_path    = self.localdirList[ self.itemTypeList.index(self.curListType) ]
                        scraper_thumb = None
                        if ( os.path.splitext(item)[0] + '.gif' in listdir ):
                            scraper_thumb = os.path.join(scraper_base_path, os.path.splitext(item)[0] + '.gif' )
                        elif ( os.path.splitext(item)[0] + '.jpg' in listdir ):
                            scraper_thumb = os.path.join(scraper_base_path, os.path.splitext(item)[0] + '.jpg' )
                        elif ( os.path.splitext(item)[0] + '.png' in listdir ):
                            scraper_thumb = os.path.join(scraper_base_path, os.path.splitext(item)[0] + '.png' )
                        elif ( os.path.splitext(item)[0] + '.jpeg' in listdir ):
                            scraper_thumb = os.path.join(scraper_base_path, os.path.splitext(item)[0] + '.jpeg' )
                        elif ( os.path.splitext(item)[0] + '.tbn' in listdir ):
                            scraper_thumb = os.path.join(scraper_base_path, os.path.splitext(item)[0] + '.tbn' )
                        else:
                            scraper_thumb = self.itemThumbList[ self.itemTypeList.index(self.curListType) ]
                        listItemObj = ListItemObject( type=self.curListType, name=os.path.splitext(item)[0], local_path=os.path.join(self.localdirList[ self.itemTypeList.index(self.curListType) ],item), thumb=scraper_thumb )
                        self.currentItemList.append(listItemObj)
            else:
                listdir = self.fileMgr.listDirFiles( self.localdirList[ self.itemTypeList.index(self.curListType) ] )
                listdir.sort( key=str.lower )
                for index, item  in enumerate( listdir ):
                    # Note:  dans le futur on pourra ici initialiser 'thumb' avec l'icone du script, plugin, themes ...
                    #        pour le moment on prend l'icone correspondant au type
                    listItemObj = ListItemObject( type=self.curListType, name=item, local_path=os.path.join(self.localdirList[ self.itemTypeList.index(self.curListType) ],item), thumb=self.itemThumbList[ self.itemTypeList.index(self.curListType) ] )
                    self.currentItemList.append(listItemObj)
        except:
            print "FileMgrWindow: Exception durant la recuperation des donnees"
            print_exc()

        #DIALOG_PROGRESS.close()

    def updateList( self ):
        """
        Mise a jour de la liste affichee
        """
        # Clear all ListItems in this control list
        if hasattr( self, 'clearProperties' ):
            self.clearProperties()
        self.clearList()

        # Titre de la categorie
        self.setProperty( "Category", self.curListType )

        #test pour avoir le choix du parent dir avec la souris
        if self.pardir_not_hidden:
            self.addItem( xbmcgui.ListItem( "..", "", iconImage="DefaultFolderBack.png", thumbnailImage="DefaultFolderBack.png" ) )
            self.set_view_mode()

        # Calcul du nombre d'elements de la liste
        itemnumber = len( self.currentItemList )

        cur_skin = xbmc.getSkinDir()
        for index, item  in enumerate( self.currentItemList ):
            if ( item.local_path == ROOTDIR ) or ( item.name == cur_skin ):
                label1 = item.name + " (Running)"
                disable = "true"
            else:
                label1 = item.name
                disable = ""
            displayListItem = xbmcgui.ListItem( label1, "", iconImage=item.thumb, thumbnailImage=item.thumb )
            DIALOG_PROGRESS.update( -1, _( 104 ), label1, _( 110 ) )
            displayListItem.setProperty( "Running", disable )
            try:
                size, c_time, last_access, last_modification = get_infos_path( item.local_path )
                displayListItem.setProperty( "size", size )
                displayListItem.setProperty( "created", c_time )
                displayListItem.setProperty( "last_modification", last_modification )
                displayListItem.setProperty( "last_access", last_access )
                displayListItem.setProperty( "path", item.local_path )
                displayListItem.setProperty( "objects", "" )
                try:
                    if os.path.isdir( item.local_path ): #if ( self.curListType in [ TYPE_ROOT, TYPE_PLUGIN ] ):
                        if ( item.name == TYPE_SCRAPER ):
                            num_item = len( [ scraper for scraper in os.listdir( item.local_path ) if scraper.endswith( ".xml" ) ] )
                        elif ( item.name == TYPE_PLUGIN != self.curListType ):
                            num_item = len( os.listdir( item.local_path+os.sep+"music" ) )
                            num_item += len( os.listdir( item.local_path+os.sep+"pictures" ) )
                            num_item += len( os.listdir( item.local_path+os.sep+"Programs" ) )
                            num_item += len( os.listdir( item.local_path+os.sep+"Video" ) )
                            num_item += len( os.listdir( item.local_path+os.sep+"weather" ) )
                        else:
                            num_item = len( os.listdir( item.local_path ) )
                        displayListItem.setProperty( "objects", str( num_item ) )
                except:
                    print_exc()
            except:
                print_exc()
                displayListItem.setProperty( "size", "" )
                displayListItem.setProperty( "created", "" )
                displayListItem.setProperty( "last_modification", "" )
                displayListItem.setProperty( "last_access", "" )
                displayListItem.setProperty( "path", "" )
                displayListItem.setProperty( "objects", "" )
            self.addItem( displayListItem )
            self.set_view_mode()

    def set_view_mode( self ):
        try:
            pass
            #if self.SET_VIEW_MODE:
            #    id = self.settings.get( "manager_view_mode", self.CONTROL_MAIN_LIST_START )
            #    xbmc.executebuiltin( "Container.SetViewMode(%i)" % id )
            #    self.SET_VIEW_MODE = not xbmc.getCondVisibility( "Control.IsVisible(%i)" % id )
            #    #xbmc.sleep( 1000 )
        except:
            print_exc()

    def check_w_rights(self):
        """
        Verifie les droits en ecriture des repertoires principaux dont on a besoin
        """
        set_write_access = False
        if ( ( SYSTEM_PLATFORM == "linux" ) or ( SYSTEM_PLATFORM == "osx" ) ):
            # On fait un check rapide pour voir si on a les droit en ecriture
            for index, filterIdx in enumerate( self.rootDisplayList ):
                local_path=self.localdirList[ filterIdx ]
                if self.fileMgr.linux_is_write_access( local_path ):
                    # Au moins un element n'a pas les droit, on ne pas pas plus loin et on demande le mot de passe
                    set_write_access = True
                    break

            if ( set_write_access == True ):
                # On parcoure tous les repertoire et on met a jour les droits si besoin
                xbmcgui.Dialog().ok( _( 19 ), _( 20 ) )
                keyboard = xbmc.Keyboard( "", _( 21 ), True )
                keyboard.doModal()
                if keyboard.isConfirmed():
                    password = keyboard.getText()
                    for index, filterIdx in enumerate( self.rootDisplayList ):
                        local_path=self.localdirList[ filterIdx ]
                        if self.fileMgr.linux_is_write_access( local_path ):
                            self.fileMgr.linux_set_write_access( local_path, password )

    def _close_dialog( self ):
        #xbmc.sleep( 100 )
        for id in range( self.CONTROL_MAIN_LIST_START, self.CONTROL_MAIN_LIST_END + 1 ):
            try:
                if xbmc.getCondVisibility( "Control.IsVisible(%i)" % id ):
                    self.settings[ "manager_view_mode" ] = id
                    Settings().save_settings( self.settings )
                    break
            except:
                pass
        self.close()


def show_file_manager( mainfunctions, rightstest="", args=None ):
    dir_path = os.getcwd().rstrip( ";" )
    #recupere le nom du skin et si force_fallback est vrai, il va chercher les images du defaultSkin.
    current_skin, force_fallback = getUserSkin() # Appel fonction dans Utilities
    file_xml = ( "IPX-FileMgr.xml", "passion-FileMgr.xml" )[ current_skin != "Default.HD" ]

    w = FileMgrWindow( file_xml, dir_path, current_skin, force_fallback,
        mainfunctions=mainfunctions, rightstest=rightstest, HomeAction=args )
    w.doModal()
    del w
