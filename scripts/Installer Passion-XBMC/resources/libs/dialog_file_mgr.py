# -*- coding: cp1252 -*-

#Modules general
import os
import re
import sys

#modules XBMC
import xbmc
import xbmcgui

#modules custom
from utilities import *
from convert_utc_time import set_local_time

#module logger
try:
    logger = sys.modules[ "__main__" ].logger
except:
    import script_log as logger
    
import traceback

# INITIALISATION CHEMIN RACINE
ROOTDIR = os.getcwd().replace( ";", "" )

#FONCTION POUR RECUPERER LES LABELS DE LA LANGUE.
_ = sys.modules[ "__main__" ].__language__

DIALOG_PROGRESS = xbmcgui.DialogProgress()

# script constants
__svn_revision__ = sys.modules[ "__main__" ].__svn_revision__ or "0"
__version__ = "%s.%s" % ( sys.modules[ "__main__" ].__version__, __svn_revision__ )
__author__ = sys.modules[ "__main__" ].__author__


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
ACTION_CONTEXT_MENU = 117
CLOSE_CONTEXT_MENU = ( ACTION_PARENT_DIR, ACTION_PREVIOUS_MENU, ACTION_CONTEXT_MENU, )




##################################################

TYPE_ROOT            = _( 10 )
TYPE_SKIN            = _( 11 )
TYPE_SCRAPER         = _( 12 )      
TYPE_SCRIPT          = _( 13 )      
TYPE_PLUGIN          = _( 14 )  
TYPE_PLUGIN_MUSIC    = _( 15 )
TYPE_PLUGIN_PICTURES = _( 16 )
TYPE_PLUGIN_PROGRAMS = _( 17 )
TYPE_PLUGIN_VIDEO    = _( 18 )

#INDEX_ROOT            = None
INDEX_SKIN            = 0
INDEX_SCRAPER         = 1      
INDEX_SCRIPT          = 2      
INDEX_PLUGIN          = 3  
INDEX_PLUGIN_MUSIC    = 4
INDEX_PLUGIN_PICTURES = 5
INDEX_PLUGIN_PROGRAMS = 6
INDEX_PLUGIN_VIDEO    = 7




typeList  = [ TYPE_SKIN,         TYPE_SCRAPER,         TYPE_SCRIPT,        TYPE_PLUGIN,        TYPE_PLUGIN_MUSIC,         TYPE_PLUGIN_PICTURES,         TYPE_PLUGIN_PROGRAMS,         TYPE_PLUGIN_VIDEO ] # Note: TYPE_ROOT est en dehors de la liste
thumbList = [ "icone_theme.png", "icone_scrapper.png", "icone_script.png", "icone_script.png", "passion-icone-music.png", "passion-icone-pictures.png", "passion-icone-programs.png", "passion-icone-video.png" ] # Note: TYPE_ROOT est en dehors de la liste

#TODO: mettre les chemins des rep sur le serveur dans le fichier de conf
#localDirLst = [ themesDir, scraperDir, scriptDir, pluginDir, pluginMusDir, pluginPictDir, pluginProgDir, pluginVidDir ]

rootDisplayList   = [ INDEX_SKIN, INDEX_SCRAPER, INDEX_SCRIPT, INDEX_PLUGIN ]                                # Liste de la racine: Cette liste est un filtre ( utilisant l'index ) sur les listes ci-dessus
pluginDisplayList = [ INDEX_PLUGIN_MUSIC, INDEX_PLUGIN_PICTURES, INDEX_PLUGIN_PROGRAMS, INDEX_PLUGIN_VIDEO ] # Liste des plugins : Cette liste est un filtre ( utilisant l'index ) sur les listes ci-dessus




class ListItemObject:
    """
    Structure de donnee definissant un element de la liste
    """
    def __init__( self, type='unknown', name='', local_path=None, thumb='default' ):
        self.type       = type
        self.name       = name
        self.local_path = local_path
        self.thumb      = thumb



class fileMgr:
    """
    
    File manager
    
    """
#    #TODO: Create superclass, inherit and overwrite init
#    def __init__(self,checkList):
##        self.verifrep(checkList[0]) #CACHEDIR
##        self.verifrep(checkList[1]) #DOWNLOADDIR
#        for i in range(len(checkList)):
#            self.verifrep(checkList[i]) 
#
#        # Set variables needed by NABBOX module
#        NABBOX.HTMLFOLDER = checkList[0] #CACHEDIR
#        print"browser - set NABBOX.HTMLFOLDER: %s"%(NABBOX.HTMLFOLDER)

    def verifrep(self, folder):
        """
        Check a folder exists and make it if necessary
        """
        try:
            #print("verifrep check if directory: " + folder + " exists")
            if not os.path.exists(folder):
                logger.LOG( logger.LOG_DEBUG, "verifrep: Impossible de trouver le repertoire - Tentative de creation du repertoire: %s", folder )
                os.makedirs(folder)
        except Exception, e:
            logger.LOG( logger.LOG_DEBUG, "verifrep: Exception durant la suppression du reperoire: %s", folder )
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )
            
    def listDirFiles(self, path):
        """
        List the files of a directory
        @param path:
        """
        logger.LOG( logger.LOG_DEBUG, "listDirFiles: Liste le repertoire: %s", path )
        dirList = os.listdir( str( path ) )        

        return dirList
        
    def renameItem( self, base_path, old_name, new_name):
        """
        Renomme un fichier ou repertoire
        """
        os.rename( os.path.join(base_path, old_name), os.path.join(base_path, new_name) )
    
    def deleteItem( self, item_path):
        """
        Supprime un element (repertoire ou fichier)
        """
        if os.path.isdir(item_path):
            self.deleteDir(item_path)
        else:
            self.deleteFile(item_path)
            
    def deleteFile(self, filename):
        """
        Delete a file form download directory
        @param filename:
        """
        os.remove(filename)
            
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
    
    def  extract(self,archive,targetDir):
        """
        Extract an archive in targetDir
        """
        xbmc.executebuiltin('XBMC.Extract(%s,%s)'%(archive,targetDir) )
        

    def linux_is_write_access( self, path ):
        """
        Linux
        Verifie si on a les dorit en ecriture sur un element
        """
        Wtest = os.access( path, os.W_OK )
        if Wtest == True:
            rightstest = True
            logger.LOG( logger.LOG_NOTICE, "linux chmod rightest OK for %s"%path )
        else:
            logger.LOG( logger.LOG_NOTICE, "linux chmod rightest NOT OK for %s"%path )
            rightstest = False
        return rightstest
        
    def linux_set_write_access( self, path, password ):
        """
        Linux
        Effectue un chmod sur un repertoire pour ne plus etre bloque par les droits root sur plateforme linux
        Retourne True en cas de succes ou False dans le cas contraire
        """
        PassStr = "echo %s | "%password
        ChmodStr = "sudo -S chmod 777 -R %s"%path
        try:
            os.system( PassStr + ChmodStr )
            rightstest = True
        except:
            rightstest = False
            logger.LOG( logger.LOG_ERROR, "erreur CHMOD %s", path )
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )
        return rightstest


class FileMgrWindow( xbmcgui.WindowXML ):
    # control id's
    CONTROL_MAIN_LIST      = 150
    CONTROL_FORUM_BUTTON   = 300
    CONTROL_OPTIONS_BUTTON = 310

    def __init__( self, *args, **kwargs ):
        """
        Initialisation de l'interface
        """
        xbmcgui.WindowXML.__init__( self, *args, **kwargs )

        self.mainwin           = kwargs[ "mainwin" ]
        self.configManager     = self.mainwin.configManager
        self.localdirList      = self.mainwin.localdirList      # Liste des repertoire locaux

        #self.ItemTypeList      = self.mainwin.downloadTypeList  # Liste des types des items geres (plugins, scripts, skins ...)
        #self.racineDisplayList = self.mainwin.racineDisplayList # Liste de la racine: Cette liste est un filtre ( utilisant l'index ) sur les listes downloadTypeList et localdirList
        #self.pluginDisplayList = self.mainwin.pluginDisplayList # Liste des plugins : Cette liste est un filtre ( utilisant l'index ) sur les listes downloadTypeList et localdirList
        self.itemTypeList      = typeList          # Liste des types des items geres (plugins, scripts, skins ...)
        self.itemThumbList     = thumbList         # Liste des icones standards
        self.rootDisplayList   = rootDisplayList   # Liste de la racine: Cette liste est un filtre ( utilisant l'index ) sur les listes downloadTypeList et localdirList
        self.pluginDisplayList = pluginDisplayList # Liste des plugins : Cette liste est un filtre ( utilisant l'index ) sur les listes downloadTypeList et localdirList
        self.scraperDir        = self.mainwin.scraperDir
        self.USRPath           = self.mainwin.USRPath
        self.rightstest        = self.mainwin.rightstest
        self.scriptDir         = self.mainwin.scriptDir
        self.CacheDir          = self.mainwin.CacheDir
        self.userDataDir       = self.mainwin.userDataDir
        #self.rightstest         = ""
        
        self.curListType        = TYPE_ROOT
        self.currentItemList    = []
        self.index              = ""
        self.main_list_last_pos = []

        self.fileMgr             = fileMgr()

#        # Display Loading Window while we are loading the information from the website
#        if xbmc.getCondVisibility( "Window.IsActive(progressdialog)" ):
#            #si le dialog PROGRESS est visible update
#            DIALOG_PROGRESS.update( -1, _( 103 ), _( 110 ) )
#        else:
#            #si le dialog PROGRESS n'est pas visible affiche le dialog
#            DIALOG_PROGRESS.create( _( 0 ), _( 103 ), _( 110 ) )

        #TODO: TOUTES ces varibales devraient etre passees en parametre du constructeur de la classe ( __init__ si tu preferes )
        # On ne devraient pas utiliser de variables globale ou rarement en prog objet


        #TODO: A nettoyer, ton PMIIIDir n'est pas defini pour XBOX sans le test si dessous
        if self.USRPath == True:
            self.PMIIIDir = PMIIIDir

        self.is_started = True


    def onInit( self ):
        # Title of the current pages
        self.setProperty( "Category", _( 10 ) )

        self._get_settings()
        self._set_skin_colours()
        
        # Verifications des permissions sur les repertoires
        self.check_w_rights()
        
        if self.is_started:
            self.is_started = False

            self.updateData()
            self.updateList()
            
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
            if controlID == self.CONTROL_MAIN_LIST:
                try: self.main_list_last_pos.append( self.getControl( self.CONTROL_MAIN_LIST ).getSelectedPosition() )
                except: self.main_list_last_pos.append( 0 )
                
                self.index = self.getControl( self.CONTROL_MAIN_LIST ).getSelectedPosition()
                if ( self.curListType == TYPE_ROOT or self.curListType == TYPE_PLUGIN):
                    self.curListType = self.currentItemList[ self.index ].type # On extrait le type de l'item selectionne
                    self.updateData() # On met a jour les donnees
                    self.updateList() # On raffraichit la page pour afficher le contenu

                else:
                    # On va ici afficher un menu des options du gestionnaire de fichiers
                    #dialog = xbmcgui.Dialog()
                    #dialog.ok( _( 117 ), _( 117 ) )
                    item_path     = self.currentItemList[ self.index ].local_path # On extrait le chemin de l'item
                    item_basename = os.path.basename( item_path )
                    
                    menuList = [ _( 160 )%item_basename,  _( 157 )%item_basename, _( 156 )%item_basename, _( 153 ) ]
                    dialog = xbmcgui.Dialog()
                    chosenIndex = dialog.select( "%s : %s"%( _( 5 ), item_basename), menuList )
                    if chosenIndex == 0: # Executer/Lancer
                        if ( self.itemTypeList.index(self.curListType) in self.pluginDisplayList ):
                            # Cas d'un sous-plugin (video, musique ...)
                            if ( self.curListType == TYPE_PLUGIN_VIDEO ):
                                rel_plugin_basedir = "video"
                            elif ( self.curListType == TYPE_PLUGIN_MUSIC ):
                                rel_plugin_basedir = "music"
                            elif ( self.curListType == TYPE_PLUGIN_PROGRAMS ):
                                rel_plugin_basedir = "programs"
                            elif ( self.curListType == TYPE_PLUGIN_PICTURES ):
                                rel_plugin_basedir = "pictures"
                            xbmc.executebuiltin( "XBMC.ActivateWindow(10001,plugin://%s/%s/)"%( rel_plugin_basedir,item_basename ) )
                        elif ( self.curListType == TYPE_SCRIPT ):
                            xbmc.executescript( os.path.join(item_path, "default.py") )
                            
                    elif chosenIndex == 1: # Renommer
                        # Renommer l'element
                        item_dirname  = os.path.dirname( item_path )
                        keyboard = xbmc.Keyboard( item_basename, _( 154 ) )
                        keyboard.doModal()
                        if ( keyboard.isConfirmed() ):
                            inputText = keyboard.getText()
                            self.fileMgr.renameItem( item_dirname, item_basename, inputText )
                            xbmcgui.Dialog().ok( _( 155 ), inputText )
                            self.updateData() # On met a jour les donnees
                            self.updateList() # On raffraichit la page pour afficher le contenu
                            
                    elif chosenIndex == 2:
                        # Supprimer l'element
                        if xbmcgui.Dialog().yesno( _( 158 )%item_basename, _( 159 )%item_basename ):
                            self.fileMgr.deleteItem( item_path )
                            self.updateData() # On met a jour les donnees
                            self.updateList() # On raffraichit la page pour afficher le contenu
                            
                            

                    else:
                        pass

            else:
                self._on_action_control( controlID )

        except:
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )
            
    def onAction( self, action ):
        """
        Remonte l'arborescence et quitte le script
        """
        try:
            if ( action == ACTION_PREVIOUS_MENU ):
                # Sortie du script
                self.close()

            elif ( action == ACTION_PARENT_DIR ):
                # remonte l'arborescence
                if not self.main_list_last_pos:
                    try: self.main_list_last_pos.append( self.getControl( self.CONTROL_MAIN_LIST ).getSelectedPosition() )
                    except: self.main_list_last_pos.append( 0 )
                try:
                    # on verifie si on est un sous plugin
                    #if ( TYPE_PLUGIN + ' ' in self.curListType ):
                    if ( self.itemTypeList.index(self.curListType) in self.pluginDisplayList ): 
                        self.curListType = TYPE_PLUGIN
                    else:
                        # cas standard
                        self.curListType = TYPE_ROOT
                    self.updateData()
                    self.updateList()
                except:
                    logger.LOG( logger.LOG_DEBUG, "FileMgrWindow::onAction::ACTION_PREVIOUS_MENU: Exception durant updateList()" )
                    logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )

                if self.main_list_last_pos:
                    self.getControl( self.CONTROL_MAIN_LIST ).selectItem( self.main_list_last_pos.pop() )

            elif ( action == ACTION_SHOW_INFO ):
                # Affiche la description de l'item selectionné
                pass
            else:
                self._on_action_control( action )
                self._on_action_control( action.getButtonCode() )

        except:
            logger.LOG( logger.LOG_DEBUG, "FileMgrWindow::onAction: Exception" )
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )

    def _on_action_control( self, act_ctrl_id ):
        try:
            pass
#            #button_code_F1_keyboard = 61552
#            if ( act_ctrl_id in ( self.CONTROL_FORUM_BUTTON, 61552 ) ):
#                from dialog_direct_infos import show_direct_infos
#                show_direct_infos( self )
#                #on a plus besoin, on le delete
#                del show_direct_infos
#
#            elif ( act_ctrl_id in ( ACTION_CONTEXT_MENU, self.CONTROL_OPTIONS_BUTTON ) ):
#                from dialog_script_settings import show_settings
#                show_settings( self )
#                #on a plus besoin du settins, on le delete
#                del show_settings
#            else:
#                pass
        except:
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )

    def _get_settings( self, defaults=False ):
        """ reads settings """
        self.settings = Settings().get_settings( defaults=defaults )
        
    def _set_skin_colours( self ):
        #xbmcgui.lock()
        try:
            self.setProperty( "style_PMIII.HD", ( "", "true" )[ ( self.settings[ "skin_colours_path" ] == "style_PMIII.HD" ) ] )
            self.setProperty( "Skin-Colours-path", self.settings[ "skin_colours_path" ] )
            self.setProperty( "Skin-Colours", ( self.settings[ "skin_colours" ] or get_default_hex_color() ) )
        except:
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )
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

    def updateData( self ):
        """
        Mise a jour des donnnees de la liste courante
        """
        try:
            # Vide la liste
            del self.currentItemList[:]
            
            if not xbmc.getCondVisibility( "Window.IsActive(progressdialog)" ):
                DIALOG_PROGRESS.create( _( 0 ), _( 104 ), _( 110 ) )
                
            # Recuperation des infos
            if ( self.curListType == TYPE_ROOT ):
                for index, filterIdx in enumerate( self.rootDisplayList ):
                    item = ListItemObject( type=self.itemTypeList[ filterIdx ], name=self.itemTypeList[ filterIdx ], local_path=self.localdirList[ filterIdx ], thumb=self.itemThumbList[ filterIdx ] )
                    self.currentItemList.append(item)
            elif ( self.curListType == TYPE_PLUGIN ):
                for index, filterIdx in enumerate( self.pluginDisplayList ):
                    item = ListItemObject( type=self.itemTypeList[ filterIdx ], name=self.itemTypeList[ filterIdx ], local_path=self.localdirList[ filterIdx ], thumb=self.itemThumbList[ filterIdx ] )
                    self.currentItemList.append(item)
            #elif TYPE_PLUGIN + ' ' in self.curListType:
            elif ( ( self.curListType == TYPE_SCRIPT ) or ( self.itemTypeList.index(self.curListType) in self.pluginDisplayList ) ):
                listdir = self.fileMgr.listDirFiles( self.localdirList[ self.itemTypeList.index(self.curListType) ] )
                for index, item  in enumerate( listdir ):
                    # Note:  dans le futur on pourra ici initialiser 'thumb' avec l'icone du script, plugin, themes ... 
                    #        pour le moment on prend l'icone correspondant au type
                    script_path    = os.path.join(self.localdirList[ self.itemTypeList.index(self.curListType) ],item)
                    thumbnail_path = os.path.join(script_path, "default.tbn")
                    if not os.path.exists(thumbnail_path):
                        thumbnail_path = self.itemThumbList[ self.itemTypeList.index(self.curListType) ]
                    item = ListItemObject( type=self.curListType, name=item, local_path=script_path, thumb=thumbnail_path )
                    self.currentItemList.append(item)
            else:
                listdir = self.fileMgr.listDirFiles( self.localdirList[ self.itemTypeList.index(self.curListType) ] )
                for index, item  in enumerate( listdir ):
                    # Note:  dans le futur on pourra ici initialiser 'thumb' avec l'icone du script, plugin, themes ... 
                    #        pour le moment on prend l'icone correspondant au type
                    item = ListItemObject( type=self.curListType, name=item, local_path=os.path.join(self.localdirList[ self.itemTypeList.index(self.curListType) ],item), thumb=self.itemThumbList[ self.itemTypeList.index(self.curListType) ] )
                    self.currentItemList.append(item)
        except:
            logger.LOG( logger.LOG_DEBUG, "FileMgrWindow: Exception durant la recuperation des donnees" )
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )

        DIALOG_PROGRESS.close()

    
    def updateList( self ):
        """
        Mise a jour de la liste affichee
        """
        if not xbmc.getCondVisibility( "Window.IsActive(progressdialog)" ):
            DIALOG_PROGRESS.create( _( 0 ), _( 104 ), _( 110 ) )

        xbmcgui.lock()

        # Clear all ListItems in this control list
        self.getControl( self.CONTROL_MAIN_LIST ).reset()

        # Calcul du nombre d'elements de la liste
        itemnumber = len( self.currentItemList )
        
        # Titre de la categorie
        self.setProperty( "Category", self.curListType )

        for index, item  in enumerate( self.currentItemList ):
            displayListItem = xbmcgui.ListItem( item.name, "", thumbnailImage = item.thumb )
            #displayListItem.setProperty( "Downloaded", "" )
            self.getControl( self.CONTROL_MAIN_LIST ).addItem( displayListItem )

#            # nettoyage du nom: replace les souligner pas un espace et enleve l'extension
#            try: item2download = os.path.splitext( ItemListPath[ lenindex: ] )[ 0 ].replace( "_", " " )
#            except: item2download = ItemListPath[ lenindex: ]
#
#            if self.downloaded_property.__contains__( md5.new( item2download ).hexdigest() ):
#                already_downloaded = "true"
#            else:
#                already_downloaded = ""

        xbmcgui.unlock()

        DIALOG_PROGRESS.close()


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
        
        


def show_file_manager( mainwin ):
    """
    Affiche la fenetre du gestionnaire de fichier
    Merci a Frost pour l'algo
    """
    file_xml = "passion-FileMgr.xml"
    dir_path = os.getcwd().rstrip( ";" )
    #recupere le nom du skin et si force_fallback est vrai, il va chercher les images du defaultSkin.
    current_skin, force_fallback = getUserSkin() # Appel fonction dans Utilities

    w = FileMgrWindow( file_xml, dir_path, current_skin, force_fallback, mainwin=mainwin )
    w.doModal()
    del w
