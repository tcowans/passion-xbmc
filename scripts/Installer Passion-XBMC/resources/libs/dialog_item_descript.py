
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
from info_item import InfoWarehouseEltTreeXMLFTP
#module logger
try:
    logger = sys.modules[ "__main__" ].logger
except:
    import script_log as logger


#FONCTION POUR RECUPERER LES LABELS DE LA LANGUE.
_ = sys.modules[ "__main__" ].__language__

DIALOG_PROGRESS = xbmcgui.DialogProgress()

try: __script__ = sys.modules[ "__main__" ].__script__
except: __script__ = os.path.basename( os.getcwd().rstrip( ";" ) )

BASE_THUMBS_PATH = os.path.join( xbmc.translatePath( "P:\\script_data" ), __script__, "Thumbnails" )


class ItemDescription( xbmcgui.WindowXMLDialog ):
    # control id's
    CONTROL_TITLE_LABEL     = 100
    CONTROL_VERSION_LABEL   = 101
    CONTROL_LANGUAGE_LABEL  = 110
    CONTROL_PREVIEW_IMAGE   = 200
    CONTROL_DESC_TEXTBOX    = 250
    CONTROL_CANCEL_BUTTON   = 301
    CONTROL_DOWNLOAD_BUTTON = 302

    def __init__( self, *args, **kwargs ):
        xbmcgui.WindowXMLDialog.__init__( self, *args, **kwargs )
        # Display Loading Window while we are loading the information from the website
        #DIALOG_PROGRESS.create( _( 0 ), _( 104 ), _( 110 ) )

        self.mainwin       = kwargs[ "mainwin" ]
        self.infoWareHouse = kwargs[ "infoWareHouse" ]
        self.itemName      = kwargs[ "itemName" ]
        self.itemType      = kwargs[ "itemType" ]

        self._set_skin_colours()

    def onInit( self ):
        # onInit est pour le windowXML seulement
        xbmcgui.lock()
        try:
            #logger.LOG( logger.LOG_DEBUG, self.itemName )
            #logger.LOG( logger.LOG_DEBUG, self.itemType )
            
            self.getControl( 200 ).setVisible( 0 ) # auto busy
            self.fileName, self.title, self.version, self.language, self.date, self.added, self.previewPicture, self.previewVideoURL, self.description_fr, self.description_en, thumbnail, author = self.infoWareHouse.getInfo( itemName=self.itemName, itemType=self.itemType, updateImage_cb=self._updateThumb_cb )
            #logger.LOG( logger.LOG_DEBUG, self.fileName)
            #logger.LOG( logger.LOG_DEBUG, self.title)
            #logger.LOG( logger.LOG_DEBUG, self.version)
            #logger.LOG( logger.LOG_DEBUG, str(self.date))
            #logger.LOG( logger.LOG_DEBUG, self.previewPicture)
            #logger.LOG( logger.LOG_DEBUG, self.previewVideoURL)
            #logger.LOG( logger.LOG_DEBUG, self.description_fr)
            #logger.LOG( logger.LOG_DEBUG, self.description_en)

            self._set_controls_labels()
            self._set_controls_visible()

        except:
            #import traceback; traceback.print_exc()
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )
            #self._close_dialog()
        xbmcgui.unlock()
        # Close the Loading Window
        #DIALOG_PROGRESS.close()


    def _updateThumb_cb (self, imagePath):
        if imagePath != None:
            self.getControl( self.CONTROL_PREVIEW_IMAGE ).setImage(imagePath)
        self.getControl( 200 ).setVisible( 1 )
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
        eval( logger.LOG_SELF_FUNCTION )
        try:
            if self.title != None:
                self.getControl( self.CONTROL_TITLE_LABEL ).setLabel( self.title )
                
            if self.version != None:
                self.getControl( self.CONTROL_VERSION_LABEL ).setLabel( _( 499 ) % ( self.version, ) )
            else:
                self.getControl( self.CONTROL_VERSION_LABEL ).setLabel( _( 499 ) % ( '-', ) )
                
            label = _( 612 ) # Default value to display for language 
            if self.language != None:
                langList = self.language.split('-')
                label = ""
                for lang in langList:
                    if lang.lower() == 'fr':
                        label = label + _( 609 )
                    elif lang.lower() == 'en':
                        label = label + _( 610 )
                    elif lang.lower() == 'multi':
                        label = label + _( 611 )
                    else:
                        label = label + _( 612 )
                    if langList.index(lang) < (len(langList) - 1):
                        label = label + ' / '
            self.getControl( self.CONTROL_LANGUAGE_LABEL ).setLabel( label )
            
            if self.previewPicture != None:
                if self.previewPicture == "downloading" or not os.path.exists(self.previewPicture):
                    self.getControl( 200 ).setVisible( 0 ) # auto busy
                else:
                    # Image deja presente 
                    self.getControl( self.CONTROL_PREVIEW_IMAGE ).setImage(self.previewPicture)
                    self.getControl( 200 ).setVisible( 1 )
                    logger.LOG( logger.LOG_DEBUG, "**** image")
            else:
                # On affiche l'image par defaut (NoImage)
                self.getControl( 200 ).setVisible( 1 ) 
            
            logger.LOG( logger.LOG_DEBUG,"Current language")
            logger.LOG( logger.LOG_DEBUG,xbmc.getLanguage())
            if xbmc.getLanguage() == 'French':
                logger.LOG( logger.LOG_DEBUG, "**** French")
                if self.description_fr != None:
                    self.getControl( self.CONTROL_DESC_TEXTBOX ).setText( self.description_fr )
            else:
                logger.LOG( logger.LOG_DEBUG, "**** Other language")
                if self.description_en != None:
                    self.getControl( self.CONTROL_DESC_TEXTBOX ).setText( self.description_en )
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
