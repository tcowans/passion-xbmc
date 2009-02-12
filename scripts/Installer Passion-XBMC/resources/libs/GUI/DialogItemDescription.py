
#Modules general
import os
import sys
import shutil
import ftplib

#Other module
from threading import Thread

#modules XBMC
import xbmc
import xbmcgui

#modules custom
from utilities import *
from pil_util import makeThumbnails

#module logger
try:
    logger = sys.modules[ "__main__" ].logger
except:
    import script_log as logger


#FONCTION POUR RECUPERER LES LABELS DE LA LANGUE.
_ = sys.modules[ "__main__" ].__language__

DIALOG_PROGRESS = xbmcgui.DialogProgress()

BASE_THUMBS_PATH = os.path.join( sys.modules[ "__main__" ].SPECIAL_SCRIPT_DATA, "Thumbnails" )


class ItemDescription( xbmcgui.WindowXMLDialog ):
    # control id's
    CONTROL_TITLE_LABEL     = 100
    CONTROL_VERSION_LABEL   = 101
    CONTROL_LANGUAGE_LABEL  = 110
    CONTROL_PREVIEW_IMAGE   = 200
    CONTROL_DESC_TEXTBOX    = 250
    CONTROL_CANCEL_BUTTON   = 301
    CONTROL_DOWNLOAD_BUTTON = 302

    # autre facon de recuperer tous les infos d'un item dans la liste.
    i_thumbnail       = xbmc.getInfoImage( "ListItem.Thumb" )
    i_previewPicture  = xbmc.getInfoImage( "ListItem.Property(fanartpicture)" )
    i_date            = unicode( xbmc.getInfoLabel( "ListItem.Property(date)" ), 'utf-8')
    i_title           = unicode( xbmc.getInfoLabel( "ListItem.Property(title)" ), "utf-8")
    i_added           = unicode( xbmc.getInfoLabel( "ListItem.Property(added)" ), 'utf-8')
    i_itemId          = unicode( xbmc.getInfoLabel( "ListItem.Property(itemId)" ), 'utf-8')
    i_author          = unicode( xbmc.getInfoLabel( "ListItem.Property(author)" ), 'utf-8')
    i_version         = unicode( xbmc.getInfoLabel( "ListItem.Property(version)" ), "utf-8")
    i_language        = unicode( xbmc.getInfoLabel( "ListItem.Property(language)" ), "utf-8")
    i_fileName        = unicode( xbmc.getInfoLabel( "ListItem.Property(fileName)" ), 'utf-8')
    i_type            = unicode( xbmc.getInfoLabel( "Container.Property(Category)" ), "utf-8")
    i_description     = unicode( xbmc.getInfoLabel( "ListItem.Property(description)" ), "utf-8")
    i_previewVideoURL = unicode( xbmc.getInfoLabel( "ListItem.Property(previewVideoURL)" ), 'utf-8')

    def __init__( self, *args, **kwargs ):
        xbmcgui.WindowXMLDialog.__init__( self, *args, **kwargs )

        self.mainwin       = kwargs[ "mainwin" ]
        self.infoWareHouse = kwargs[ "infoWareHouse" ]
        self.itemName      = kwargs[ "itemName" ]
        self.itemType      = kwargs[ "itemType" ]

        self._set_skin_colours()

    def onInit( self ):
        # onInit est pour le windowXML seulement
        xbmcgui.lock()
        try:
            self.getControl( self.CONTROL_PREVIEW_IMAGE ).setVisible( 0 ) # auto busy

            self._set_controls_labels()
            self._set_controls_visible()

        except:
            #import traceback; traceback.print_exc()
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )
        xbmcgui.unlock()
        # Close the Loading Window
        #DIALOG_PROGRESS.close()


    def _updateThumb_cb( self, imagePath, listitem=None ):
        if imagePath:
            self.getControl( self.CONTROL_PREVIEW_IMAGE ).setImage(imagePath)
        self.getControl( self.CONTROL_PREVIEW_IMAGE ).setVisible( 1 )
        logger.LOG( logger.LOG_DEBUG, "**** image")

    def _set_skin_colours( self ):
        #xbmcgui.lock()
        try:
            xbmc.executebuiltin( "Skin.SetString(PassionSkinColourPath,%s)" % ( self.mainwin.settings[ "skin_colours_path" ], ) )
            xbmc.executebuiltin( "Skin.SetString(PassionSkinHexColour,%s)" % ( ( self.mainwin.settings[ "skin_colours" ] or get_default_hex_color() ), ) )
        except:
            xbmc.executebuiltin( "Skin.SetString(PassionSkinHexColour,ffffffff)" )
            xbmc.executebuiltin( "Skin.SetString(PassionSkinColourPath,default)" )
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )
        #xbmcgui.unlock()

    def _set_controls_labels( self ):
        # setlabel pour les controles du dialog qui a comme info exemple: id="100" et pour avoir son controle on fait un getControl( 100 )
        try:
            self.getControl( self.CONTROL_TITLE_LABEL ).setLabel( self.i_type + ": " + self.i_title )

            self.getControl( self.CONTROL_VERSION_LABEL ).setLabel( _( 499 ) % ( self.i_version or _( 612 ), ) )

            self.getControl( self.CONTROL_LANGUAGE_LABEL ).setLabel( self.i_language )

            self.getControl( self.CONTROL_DESC_TEXTBOX ).setText( self.i_description or _( 604 ) )

            if self.i_previewPicture:
                if not os.path.exists( self.i_previewPicture ):
                    self.getControl( self.CONTROL_PREVIEW_IMAGE ).setVisible( 0 ) # auto busy
                    # Recuperation de l'image dans la FIFO
                    self.infoWareHouse.getInfo( itemName=self.itemName, itemType=self.itemType, updateImage_cb=self._updateThumb_cb )
                    self.infoWareHouse.update_Images()
                else:
                    # Image deja presente
                    self.getControl( self.CONTROL_PREVIEW_IMAGE ).setImage( self.i_previewPicture )
                    self.getControl( self.CONTROL_PREVIEW_IMAGE ).setVisible( 1 )
            else:
                # On affiche l'image par defaut (NoImage)
                self.getControl( self.CONTROL_PREVIEW_IMAGE ).setVisible( 1 )
        except:
            #import traceback; traceback.print_exc()
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )

    def _set_controls_visible( self ):
        xbmcgui.lock()
        try:
            self.getControl( self.CONTROL_DOWNLOAD_BUTTON ).setEnabled( False )
            self.getControl( self.CONTROL_DOWNLOAD_BUTTON ).setVisible( False )
        except:
            #import traceback; traceback.print_exc()
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )
        xbmcgui.unlock()

    def onFocus( self, controlID ):
        #cette fonction n'est pas utiliser ici, mais dans les XML si besoin
        #Note: Mais il faut la declarer :)
        pass

    def onClick( self, controlID ):
        try:
            if controlID == self.CONTROL_CANCEL_BUTTON:
                # bouton quitter, on ferme le dialog
                self._close_dialog()
            #elif controlID == self.CONTROL_DOWNLOAD_BUTTON:
            #    #bouton downlaod, non utilise pour le moment (desactive)
            #    pass
            else:
                pass
        except:
            #import traceback; traceback.print_exc()
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )

    def onAction( self, action ):
        #( ACTION_PARENT_DIR, ACTION_PREVIOUS_MENU, ACTION_CONTEXT_MENU, )
        if action in ( 9, 10, 117 ): self._close_dialog()

    def _close_dialog( self, OK=False ):
        #xbmc.sleep( 100 )
        self.close()


def show_item_descript_window( mainwin, itemInfosManager, selectedItem , typeItem ):
    """
    Affiche une fenetre contenant les informations sur un item
    """
    file_xml = "passion-ItemDescript.xml"
    #depuis la revision 14811 on a plus besoin de mettre le chemin complet, la racine suffit
    dir_path = os.getcwd().rstrip( ";" )
    #recupere le nom du skin et si force_fallback est vrai, il va chercher les images du defaultSkin.
    current_skin, force_fallback = getUserSkin()

    #TODO: ajouter check si infoWarehouse n'a pas ete cree

    w = ItemDescription( file_xml, dir_path, current_skin, force_fallback, mainwin=mainwin, infoWareHouse=itemInfosManager.infoWarehouseFTP,itemName=selectedItem, itemType=typeItem )
    w.doModal()
    del w
