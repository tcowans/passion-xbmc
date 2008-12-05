
#Modules general
import os
import sys
from collections import deque
import ftplib

#Other module
from BeautifulSoup import BeautifulStoneSoup, Tag, NavigableString  #librairie de traitement XML

#modules XBMC
import xbmc
import xbmcgui

#modules custom
from utilities import *

#module logger
try:
    logger = sys.modules[ "__main__" ].logger
except:
    import script_log as logger


#REPERTOIRE RACINE ( default.py )
CWD = os.getcwd().rstrip( ";" )

#FONCTION POUR RECUPERER LES LABELS DE LA LANGUE.
_ = sys.modules[ "__main__" ].__language__

# script constants
__script__ = sys.modules[ "__main__" ].__script__
try: __svn_revision__ = sys.modules[ "__main__" ].__svn_revision__
except: __svn_revision__ = 0
if not __svn_revision__: __svn_revision__ = "0"
__version__ = "%s.%s" % ( sys.modules[ "__main__" ].__version__, __svn_revision__ )


DIALOG_PROGRESS = xbmcgui.DialogProgress()


class ItemDescription( xbmcgui.WindowXMLDialog ):
    def __init__( self, *args, **kwargs ):
        xbmcgui.WindowXMLDialog.__init__( self, *args, **kwargs )

        # Display Loading Window while we are loading the information from the website
        if xbmc.getCondVisibility( "Window.IsActive(progressdialog)" ):
            #si le dialog PROGRESS est visible update
            DIALOG_PROGRESS.update( -1, _( 104 ), _( 110 ) )
        else:
            #si le dialog PROGRESS n'est pas visible affiche le dialog
            DIALOG_PROGRESS.create( _( 0 ), _( 104 ), _( 110 ) )
        # __init__ normal de python
        # On recupere le "self" de le fenetre principal pour benificier de ces variables.
        
        #TODO: deplacer ce chemin dans le fichier de configuration
        self.serverDir  = "/.passionxbmc/Installeur-Passion/content/"
        
        self.mainwin  = kwargs[ "mainwin" ]
        self.itemName = kwargs[ "itemName" ]
        self.itemType = kwargs[ "itemType" ]

        self._get_settings()

    def onInit( self ):
        # onInit est pour le windowXML seulement
        xbmcgui.lock()
        try:
            logger.LOG( logger.LOG_INFO, self.itemName)
            logger.LOG( logger.LOG_INFO, self.itemType)
            
            self.fileName, self.title, self.version, self.language, self.date , self.previewPicture, self.previewVideoURL, self.description_fr, self.description_en = self._get_info()
            #logger.LOG( logger.LOG_INFO, self.fileName)
            #logger.LOG( logger.LOG_INFO, self.title)
            #logger.LOG( logger.LOG_INFO, self.version)
            #logger.LOG( logger.LOG_INFO, str(self.date))
            #logger.LOG( logger.LOG_INFO, self.previewPicture)
            #logger.LOG( logger.LOG_INFO, self.previewVideoURL)
            #logger.LOG( logger.LOG_INFO, self.description_fr)
            #logger.LOG( logger.LOG_INFO, self.description_en)

            self._set_controls_labels()
            self._set_controls_visible()

        except:
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )
            #self._close_dialog()
        xbmcgui.unlock()
        # Close the Loading Window
        DIALOG_PROGRESS.close()

    
    def _get_info( self, defaults=False  ):
        """ reads info """
        fileName            = None
        title               = None
        version             = None
        language            = None
        date                = None
        previewPicture      = None
        previewVideoURL     = None
        description_fr      = None
        description_en      = None

        # On recupere le fichier de description des items
        self._downloadFile(self.srvItemDescripDir + self.srvItemDescripFile)
        self.soup =  BeautifulStoneSoup((open(os.path.join(self.mainwin.CacheDir,self.srvItemDescripFile), 'r')).read())
        #logger.LOG( logger.LOG_INFO,self.soup.prettify())
        cat = None
        
        if self.itemType == "Themes":
            cat = self.soup.find("skins")
        elif self.itemType == "Scrapers":
            cat = self.soup.find("scrapers")
        elif self.itemType == "Scripts":
            cat = self.soup.find("scripts")
        elif self.itemType == "Plugins Musique":
            cat = self.soup.find("musicplugin")
            #plugins
        elif self.itemType == "Plugins Images":
            cat = self.soup.find("pictureplugin")
        elif self.itemType == "Plugins Programmes":
            cat = self.soup.find("programplugin")
        elif self.itemType == "Plugins Vidéos":
            cat = self.soup.find("videoplugin")

        try:
            if cat != None:
                for item in cat.findAll("entry"):
                    if item.filename.string.encode("cp1252") == self.itemName:
                        if hasattr(item.filename,'string'):
                            if item.filename.string != None:
                                fileName            = item.filename.string.encode("cp1252")
                        if hasattr(item.title,'string'):
                            if item.title.string != None:
                                title = item.title.string.encode("cp1252")
                        if hasattr(item.version,'string'): 
                            if item.version.string != None:
                                version = item.version.string.encode("utf-8")
                        if hasattr(item.lang,'string'): 
                            if item.lang.string != None:
                                language = item.lang.string.encode("utf-8")
                        if hasattr(item.date,'string'):
                            if item.date.string != None:
                                date = item.date.string.encode("cp1252")
                        if hasattr(item.previewpictureurl,'string'):
                            if item.previewpictureurl.string != None:
                                previewPictureURL = item.previewpictureurl.string.encode("utf-8")
                                
                                # Telechargement de l'image
                                self._downloadFile(previewPictureURL)
                                checkPathPic = os.path.join(self.mainwin.CacheDir, os.path.basename(previewPictureURL))
                                if os.path.exists(checkPathPic):
                                    previewPicture = checkPathPic
                                    
                        if hasattr(item.previewvideourl,'string'):
                            if item.previewvideourl.string != None:
                                # Non utilse pour le moment
                                previewVideoURL = item.previewvideourl.string.encode("utf-8")
                        if hasattr(item.description_fr,'string'):
                            if item.description_fr.string != None:
                                description_fr = item.description_fr.string.encode("cp1252")
                        if hasattr(item.description_en,'string'):
                            if item.description_en.string != None:
                                description_en = item.description_en.string.encode("cp1252")
                        # We exit the loop since we found the file we were looking for
                        break
               
        except Exception, e:
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )
        
        return fileName, title, version, language, date , previewPicture, previewVideoURL, description_fr, description_en
        
        
    def _get_settings( self, defaults=False  ):
        """ reads settings from conf file """
        self.srvHost             = self.mainwin.configManager.getSrvHost()
        self.srvPassword         = self.mainwin.configManager.getSrvPassword()
        self.srvUser             = self.mainwin.configManager.getSrvUser()
        self.srvItemDescripDir   = self.mainwin.configManager.getSrvItemDescripDir()
        self.srvItemDescripFile  = self.mainwin.configManager.getSrvItemDescripFile()


    def _downloadFile(self,remoteFilePath):
        """
        Fonction de telechargement commune : version, archive, script de mise a jour
        """
        try:
            ftp = ftplib.FTP(self.srvHost,self.srvUser,self.srvPassword)
            filetodlUrl   = remoteFilePath
            localFilePath = os.path.join(self.mainwin.CacheDir, os.path.basename(remoteFilePath))
            localFile = open(str(localFilePath), "wb")
            ftp.retrbinary('RETR ' + filetodlUrl, localFile.write)
            localFile.close()
            ftp.quit()
        except:
            logger.LOG( logger.LOG_ERROR, "_downloaddossier: Exception - Impossible de creer le dossier: %s", localAbsDirPath )
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )

    def _set_controls_labels( self ):
        # setlabel pour les controles du dialog qui a comme info exemple: id="100" et pour avoir son controle on fait un getControl( 100 )
        logger.LOG( logger.LOG_INFO, "**** _set_controls_labels")
        try:
            if self.title != None:
                self.getControl( 100 ).setLabel( self.title )
            else:
                self.getControl( 100 ).setLabel( self.itemName )
                
            if self.version != None:
                self.getControl( 101 ).setLabel( _( 499 ) % ( self.version, ) )
            else:
                self.getControl( 101 ).setLabel( _( 499 ) % ( '-', ) )
                
            if self.language != None:
                langList = self.language.split('-')
                label = ""
                for lang in langList:
                    if lang == 'fr':
                        label = label +  _( 609 )
                    elif lang == 'en':
                        label = label +  _( 610 )
                    elif lang == 'multi':
                        label = label +  _( 611 )
                    else:
                        label = label +  _( 612 )
                    if langList.index(lang) < (len(langList) - 1):
                        label = label + ' / '
                self.getControl( 110 ).setLabel( label )
            
            # Clear all ListItems in this control list
            if self.previewPicture != None:
                self.getControl( 200 ).setImage(self.previewPicture)
                logger.LOG( logger.LOG_INFO, "**** image")

            logger.LOG( logger.LOG_INFO,"Current language")
            logger.LOG( logger.LOG_INFO,xbmc.getLanguage())
            if xbmc.getLanguage() == 'French':
                logger.LOG( logger.LOG_INFO, "**** French")
                if self.description_fr != None:
                    self.getControl( 250 ).setText( self.description_fr )
            else:
                logger.LOG( logger.LOG_INFO, "**** Other language")
                if self.description_en != None:
                    self.getControl( 250 ).setText( self.description_en )
        except:
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )


    def _set_controls_visible( self ):
        """
        ici sa sert a rendre visible les controls qu'on veut voir 
        pour le moment il y a 1 parametre, donc les autres sont mis non visible
        pour le futur on pourra les activer au besoin et coder sa fonction
        penser a retirer les # de bouton_non_visible = [ 170, 180, 190, 200, 210, 220, 230, 240 ] par ordre de grandeur, suivant == 170
        """
        xbmcgui.lock()
        try:
            bouton_non_visible = [ 302 ]
            for control_id in bouton_non_visible:
                self.getControl( control_id ).setEnabled( False )
                self.getControl( control_id ).setVisible( False ) 
        
        except:
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )
        xbmcgui.unlock()

    def onFocus( self, controlID ):
        #cette fonction n'est pas utiliser ici, mais dans les XML si besoin
        #Note: Mais il faut la declarer :)
        pass

    def onClick( self, controlID ):
        try:
            #if controlID == 300:
            #    #bouton zoom image.
            #    self._save_settings()
            if controlID == 301:
                # bouton quitter, on ferme le dialog
                self._close_dialog()
            #elif controlID == 302:
            #    #bouton downlaod, non utilise pour le moment (desactive)
            #    pass
            else:
                pass
        except:
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )

    def onAction( self, action ):
        #( ACTION_PARENT_DIR, ACTION_PREVIOUS_MENU, ACTION_CONTEXT_MENU, )
        if action in ( 9, 10, 117 ): self._close_dialog()

    def _close_dialog( self, OK=False ):
        #xbmc.sleep( 100 )
        self.close()


def show_descript( mainwin, selectedItem , typeItem):
    file_xml = "passion-ItemDescript.xml"
    #depuis la revision 14811 on a plus besoin de mettre le chemin complet, la racine suffit
    dir_path = CWD #xbmc.translatePath( os.path.join( CWD, "resources" ) ) 
    #recupere le nom du skin et si force_fallback est vrai, il va chercher les images du defaultSkin.
    current_skin, force_fallback = getUserSkin()

    w = ItemDescription( file_xml, dir_path, current_skin, force_fallback, mainwin=mainwin, itemName=selectedItem, itemType=typeItem )
    w.doModal()
    del w
