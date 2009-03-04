# -*- coding: cp1252 -*-

"""
Le Blog d'Alain Carrazé : GUI script by Temhil (temhil@gmail.com)
"""

############################################################################
# import  
############################################################################
from string import *
import sys, os.path
import traceback
from threading import Thread, Event

try:
    import xbmcgui, xbmc
except ImportError:
    raise ImportError, 'This program requires the XBMC extensions for Python.'

from blog import *

############################################################################
# script constants
############################################################################
__script__       = sys.modules[ "__main__" ].__script__
__script_title__ = sys.modules[ "__main__" ].__script_title__
__author__       = sys.modules[ "__main__" ].__author__
__version__      = sys.modules[ "__main__" ].__version__
__date__         = sys.modules[ "__main__" ].__date__


############################################################################
# emulator
############################################################################
try: 
    Emulating = xbmcgui.Emulating
except: 
    Emulating = False

############################################################################
# Get actioncodes from keymap.xml
############################################################################

ACTION_MOVE_LEFT                 = 1    
ACTION_MOVE_RIGHT                = 2
ACTION_MOVE_UP                   = 3
ACTION_MOVE_DOWN                 = 4
ACTION_PAGE_UP                   = 5
ACTION_PAGE_DOWN                 = 6
ACTION_SELECT_ITEM               = 7
ACTION_HIGHLIGHT_ITEM            = 8
ACTION_PARENT_DIR                = 9
ACTION_PREVIOUS_MENU             = 10
ACTION_SHOW_INFO                 = 11

ACTION_PAUSE                     = 12
ACTION_STOP	                     = 13
ACTION_NEXT_ITEM                 = 14
ACTION_PREV_ITEM                 = 15

ACTION_CONTEXT_MENU              = 117

#############################################################################
# autoscaling values
#############################################################################

HDTV_1080i      = 0 #(1920x1080, 16:9, pixels are 1:1)
HDTV_720p       = 1 #(1280x720, 16:9, pixels are 1:1)
HDTV_480p_4x3   = 2 #(720x480, 4:3, pixels are 4320:4739)
HDTV_480p_16x9  = 3 #(720x480, 16:9, pixels are 5760:4739)
NTSC_4x3        = 4 #(720x480, 4:3, pixels are 4320:4739)
NTSC_16x9       = 5 #(720x480, 16:9, pixels are 5760:4739)
PAL_4x3         = 6 #(720x576, 4:3, pixels are 128:117)
PAL_16x9        = 7 #(720x576, 16:9, pixels are 512:351)
PAL60_4x3       = 8 #(720x480, 4:3, pixels are 4320:4739)
PAL60_16x9      = 9 #(720x480, 16:9, pixels are 5760:4739)

#############################################################################
# Control alignment
#############################################################################
xbfont_left         = 0x00000000
xbfont_right        = 0x00000001
xbfont_center_x     = 0x00000002
xbfont_center_y     = 0x00000004
xbfont_truncated    = 0x00000008


class SettingsWindow(xbmcgui.WindowDialog):
    """
    
    This window display settings
    
    """
    def __init__(self):
        if Emulating: xbmcgui.Window.__init__(self)
        if not Emulating:
            self.setCoordinateResolution(PAL_4x3) # Set coordinate resolution to PAL 4:3

    def setWindow(self,configManager):
        self.configManager   = configManager
        self.strListMaxSize  = 50
        self.playerMenuList  = ["Auto","DVD Player","MPlayer"]
        self.qualityMenuList = ["HQ","LQ"]
        self.cleanCacheList  = ["Activé","Désactivé"]
        
        # Background image
        self.addControl(xbmcgui.ControlImage(138,120,445,335, os.path.join(IMAGEDIR,"dialog-panel.png")))

        # Title label:
        self.strlist = xbmcgui.ControlLabel(138, 125, 445, 30, 'Options', 'special13',alignment=6)
        self.addControl(self.strlist)

        # Get settings
        self.defaultPlayer  = self.configManager.getDefaultPlayer()
        self.videoQuality   = self.configManager.getVideoQuality()
        self.cleanCache     = self.configManager.getCleanCache()
        
        
        # item Control List
        self.strDefaultPlayerTitle   = "Player vidéo: "
        self.strDefaultPlayerContent = self.playerMenuList[self.defaultPlayer]
        self.strVideoQualityTitle    = "Qualité vidéo: "
        self.strVideoQualityContent  = str(self.videoQuality)
        self.strCleanCacheTitle      = "Nettoyage auto du cache: "
        if self.cleanCache:
            self.strCleanCacheContent = self.cleanCacheList[0] #Activé
        else:
            self.strCleanCacheContent = self.cleanCacheList[1] #Désactivé
            
        self.settingsListData = [self.strDefaultPlayerTitle + self.strDefaultPlayerContent, self.strVideoQualityTitle + self.strVideoQualityContent, self.strCleanCacheTitle + self.strCleanCacheContent]
        self.settingsList = xbmcgui.ControlList(158, 170, 300 , 400,'font14', buttonTexture = os.path.join(IMAGEDIR,"list-black-nofocus.png"), buttonFocusTexture = os.path.join(IMAGEDIR,"list-black-focus.png"), itemTextXOffset=-10, itemHeight=30)
        self.addControl(self.settingsList)
            
        # OK button:
        self.buttonOK = xbmcgui.ControlButton(478, 170, 80, 30, "OK",font='font12', focusTexture = os.path.join(IMAGEDIR,"list-black-focus.png"), noFocusTexture  = os.path.join(IMAGEDIR,"list-black-nofocus.png"), alignment=6)
        self.addControl(self.buttonOK)
        
        self.settingsList.controlLeft(self.buttonOK)
        self.settingsList.controlRight(self.buttonOK)
        self.buttonOK.controlLeft(self.settingsList)
        self.buttonOK.controlRight(self.settingsList)

        for labelItem in self.settingsListData:
            displayListItem = (xbmcgui.ListItem(label = labelItem))
            # Add list item to the ControlList
            self.settingsList.addItem(displayListItem)
        self.setFocus(self.settingsList)
        
        # show this menu and wait until it's closed
        self.doModal()

    #TODO: Create a general update function???
        
    def onAction(self, action):
        if action == ACTION_PREVIOUS_MENU:
            #close the window
            self.close()
            
    def onControl(self, control):
        if control == self.settingsList:
            selectedIndex = self.settingsList.getSelectedPosition()
            print("selectedIndex = " + str(selectedIndex))
            if selectedIndex == 0:
                dialog = xbmcgui.Dialog()
                chosenIndex = dialog.select('Selectionner le Player désiré', self.playerMenuList)
                self.configManager.setDefaultPlayer(chosenIndex)
                self.defaultPlayer           = chosenIndex
                self.strDefaultPlayerContent = self.playerMenuList[self.defaultPlayer]
                self.settingsList.getListItem(selectedIndex).setLabel(self.strDefaultPlayerTitle + self.strDefaultPlayerContent)
            elif selectedIndex == 1:
                dialog = xbmcgui.Dialog()
                chosenIndex = dialog.select('Selectionner la Qualité vidéo désirée', self.qualityMenuList)
                self.configManager.setVideoQuality(self.qualityMenuList[chosenIndex])
                self.videoQuality            = self.qualityMenuList[chosenIndex]
                self.strVideoQualityContent  = str(self.videoQuality)
                self.settingsList.getListItem(selectedIndex).setLabel(self.strVideoQualityTitle + self.strVideoQualityContent)
                
            elif selectedIndex == 2:
                dialog = xbmcgui.Dialog()
                chosenIndex = dialog.select('Selectionner la gestion du cache désirée', self.cleanCacheList)
                if chosenIndex == 0:
                    self.configManager.setCleanCache(True)
                    self.cleanCache           = True
                    self.strCleanCacheContent = self.cleanCacheList[0] #Activé
                else:
                    self.configManager.setCleanCache(False)
                    self.cleanCache           = False
                    self.strCleanCacheContent = self.cleanCacheList[1] #Désactivé
                self.settingsList.getListItem(selectedIndex).setLabel(self.strCleanCacheTitle + self.strCleanCacheContent)
            else:
                print "SettingsWindow - onControl : Invalid control list index"

        elif control == self.buttonOK:
            self.close()

class AboutWindow(xbmcgui.WindowDialog):
    """
    
    About Window
    
    """
    def __init__(self):
        if Emulating: xbmcgui.Window.__init__(self)
        if not Emulating:
            self.setCoordinateResolution(PAL_4x3) # Set coordinate resolution to PAL 4:3

        self.addControl(xbmcgui.ControlImage(100,100,545,435, os.path.join(IMAGEDIR,"dialog-panel.png")))
        self.strTitle = xbmcgui.ControlLabel(130, 110, 350, 30, __script_title__,'special13')
        self.addControl(self.strTitle)
        self.strVersion = xbmcgui.ControlLabel(130, 140, 350, 30, "Version: " + __version__)
        self.addControl(self.strVersion)
        self.strAuthor = xbmcgui.ControlLabel(130, 170, 350, 30, "Auteur: "+ __author__)
        self.addControl(self.strAuthor)        
        self.strDesTitle = xbmcgui.ControlLabel(130, 200, 350, 30, "Description: ")
        self.addControl(self.strDesTitle)        
        strContent = """Ce script vous permet de vous connecter sur le Blog d'Alain Carrazé 
(http://alaincarraze.blog.canal-plus.com) et de visionner les videos
du blog ainsi que d'en lire leur description.
"""
        self.strDesContent = xbmcgui.ControlLabel(130, 220, 490, 100, strContent, "font12", textColor='0xFFD3D3D3')
        self.addControl(self.strDesContent)

        self.strACTitle = xbmcgui.ControlLabel(130, 290, 350, 30, "A propos d'Alain Carrazé: ")
        self.addControl(self.strACTitle) 
               
        strAboutAC = """Depuis ses débuts en 1979 en tant que collaborateur de 'Temps X', l'émission de science-fiction, Alain CARRAZE à partagé ses passions pour le cinéma fantastique, les comics et surtout les séries TV à travers des émissions comme 'Fantasy' ( dans le cadre des 'Enfants du Rock' ) et principalement la cultissime 'Destination Séries', sur Canal Jimmy de 1992 à 2000 (pres de 225 éditions) , avec aussi des émissions spéciales comme le 'Marathon Friends', 'La Fête à Jerry Seinfeld', les Emmy Awards ou la 'Nuit Star Trek'.
A travers des magazines, aussi, comme 'Esode, le magazine de la culture séries', des hors-séries pour Mad Movies ou 'Episodik'. A travers des livres, enfin, avec des ouvrages comme 'Le Prisonnier, chef d'oeuvre télévisionnaire', ou sur 'Chapeau Melon et Bottes de Cuir ', 'Mission: Impossible', 'Les Grandes Séries' et, récemment, la mini-encyclopedie 'Les séries télé' dans la collection 'Toute les Clés '.
Il travaille sur des bonus de DVD ('Amicalement Vôtre', 'Le Prisonnier', 'Twin Peaks'), chronique aussi les séries à la radio et dans un grand quinzomadaire de programmes télé... et maintenant en exclusivité sur Canalplus.fr !
"""
        self.aboutACTextBox = xbmcgui.ControlTextBox(130, 310, 545-50, 145, font="font12", textColor='0xFFD3D3D3')
        self.addControl(self.aboutACTextBox)
        self.aboutACTextBox.setText(strAboutAC)
        self.aboutACTextBox.setVisible(True)
        self.setFocus(self.aboutACTextBox)
        
        strCopyRight = """Les droits des diffusions et des images utilisées sont exclusivement réservés
à Canal+"""
        self.strCopyRight = xbmcgui.ControlLabel(130, 465, 500, 20,strCopyRight, "font10",'0xFFFF0000')
        self.addControl(self.strCopyRight)
        
        self.doModal()
        
    def onAction(self, action):
        if action == ACTION_PREVIOUS_MENU:
            #close the window
            self.close()
            

class InfoWindow(xbmcgui.WindowDialog):
    """
    
    This window display informations about a video
    
    """
    def __init__(self):
        if Emulating: xbmcgui.Window.__init__(self)
        if not Emulating:
            self.setCoordinateResolution(PAL_4x3) # Set coordinate resolution to PAL 4:3

        # Background image
        self.addControl(xbmcgui.ControlImage(100,100,545,435, os.path.join(IMAGEDIR,"dialog-panel.png")))

        # Set the Video Image at top-left position
        self.videoPicture = xbmcgui.ControlImage(130,120,214,160, os.path.join(IMAGEDIR,"noImageAvailable.jpg"))
        self.addControl(self.videoPicture)
        self.videoPicture.setVisible(True)

    def updateImage(self,path):
        """
        Update the image of the video in the window
        """
        self.videoPicture.setImage(path)

    def updateInfo(self,videoDate,videoTitle,videoDesciption):
        """
        Set and fill the information for a video
        """
        print 'videoDesciption'
        print videoDesciption
        self.strDate = xbmcgui.ControlLabel(355, 120, 200, 30, videoDate,'special13')
        self.addControl(self.strDate)
        self.strTitle = xbmcgui.ControlLabel(355, 150, 270, 30, videoTitle,'special13')
        self.addControl(self.strTitle)
        self.descriptTextBox = xbmcgui.ControlTextBox(130, 285, 545-50, 210, font="font12", textColor='0xFFFFFFFF')
        self.addControl(self.descriptTextBox)
        self.descriptTextBox.setText(videoDesciption)
        self.descriptTextBox.setVisible(True)
        self.setFocus(self.descriptTextBox)
        

class MainWindow(xbmcgui.Window):
    """
    AC Blog main UI
    """
    def __init__(self):

        if Emulating: xbmcgui.Window.__init__(self)
        if not Emulating:
            self.setCoordinateResolution(PAL_4x3) # Set coordinate resolution to PAL 4:3
        # Create a file manager and check directory
        self.fileMgr = fileMgr(dirCheckList)

        # Check conf file
        self.configManager = ConfigCtrl()
        
        if self.configManager.getDebug():
            print "BASE_BLOGNAME = %s"%BASE_BLOGNAME       
            print "BASE_URL_INFO = %s"%BASE_URL_INFO       
            print "BASE_URL_XML = %s"%BASE_URL_XML       
            print "BASE_URL_VIDEO_INFO = %s"%BASE_URL_VIDEO_INFO       
            print "URL_MAIN_WEBPAGE = %s"%URL_MAIN_WEBPAGE       
            print "URL_EXT_WEBPAGE = %s"%URL_EXT_WEBPAGE       
        
        # List of thread per menu index
        self.stopThreadList = []

        # Display Loading Window while we are loading the information from the website
        dialogUI = xbmcgui.DialogProgress()
        dialogUI.create(__script_title__, "Creation de l'interface Graphique", "Veuillez patienter...")

        # Background image
        self.addControl(xbmcgui.ControlImage(0,0,720,576, os.path.join(IMAGEDIR,"background.png")))
       
        # Set the Video logo at top-left position
        self.user_logo = xbmcgui.ControlImage(550,25,130,97, os.path.join(IMAGEDIR, "portrait.jpg"))
        self.addControl(self.user_logo)
        self.user_logo.setVisible(True)

        # Extract categories from main webpage
        startupWebPage=blogEntryListWebPage(URL_MAIN_WEBPAGE ,txdata,txheaders)
        self.categoryList = startupWebPage.getCategoryList()
        
        # Add external webpage to the list
        #TODO: put full url not relative
        self.categoryList.append( CategoryObject( "SERIES EXPRESS", "" ) ) 
        
        # Menu Control List
        self.currentMenuIdx = 0
        menuItemsize   = 30
        menuItemNumber = len(self.categoryList)
        if menuItemNumber > 11:
            menuItemNumber = 11 # We don't want to go outise the screen if the number of categories is too big
        menuListSize   = menuItemsize * menuItemNumber
        menuListWidth = 175
        self.Menulist = xbmcgui.ControlList( 25, 190, menuListWidth, menuListSize, space=0,font='font12', textColor='0xFF000000', itemTextXOffset=-5, buttonTexture=os.path.join( IMAGEDIR, "list-background.png" ), buttonFocusTexture=os.path.join( IMAGEDIR, "list-focus.png" ) )

        # Videos Control List
        self.list = xbmcgui.ControlList( 207, 140, 473, 380, space=8, itemHeight=80, font='font12', textColor='0xFF000000', itemTextXOffset=0, buttonFocusTexture=os.path.join( IMAGEDIR, "list-background.png" ), imageWidth=107, imageHeight=80 )

        # Title of the current page
        title =  __script_title__.upper().replace('é', 'É') # "LE BLOG D'ALAIN CARRAZÉ"
        self.strMainTitle = xbmcgui.ControlLabel( 230, 40, 270, 20, title, 'special13','0xFF000000',alignment= 6 )

        # Current Catégories Title
        self.strButton = xbmcgui.ControlLabel( 230, 80, 270, 20, self.categoryList[ self.currentMenuIdx ].name, 'special13', '0xFF000000', alignment=6 )

        # List label:
        self.strlist = xbmcgui.ControlLabel( 250, 300, 260, 20, '', 'font12', '0xFFFF0000' )

        # Number of Video in the list:
        self.strItemNb = xbmcgui.ControlLabel( 600, 530, 150, 20, '0 entrée', 'font12', '0xFFFF0000' )

        # Version and author:
        self.strVersion = xbmcgui.ControlLabel( 230, 58, 270, 20,"v" + __version__,'font10', '0xFFFF0000', alignment=6 )


        self.addControl( self.list )
        self.addControl( self.Menulist )
        self.addControl( self.strButton )
        self.addControl( self.strlist )
        self.addControl( self.strMainTitle )
        self.addControl( self.strItemNb )
        self.addControl( self.strVersion )
          
        # Option button:
        self.buttonOption = xbmcgui.ControlButton( 25, 190 + menuListSize - menuItemsize + 5, menuListWidth, 30, "Options", font='font12', textColor='0xFF000000', focusTexture=os.path.join( IMAGEDIR, "list-focus.png" ), noFocusTexture=os.path.join( IMAGEDIR, "list-background.png" ), textXOffset=15 )
        self.addControl(self.buttonOption)

        # About button:
        self.buttonAbout = xbmcgui.ControlButton( 25, 220 + menuListSize - menuItemsize + 5, menuListWidth, 30, "A propos", font='font12', textColor='0xFF000000', focusTexture=os.path.join( IMAGEDIR, "list-focus.png" ), noFocusTexture=os.path.join( IMAGEDIR, "list-background.png" ), textXOffset=15 )
        self.addControl( self.buttonAbout )

        self.list.controlLeft( self.Menulist )
        self.Menulist.controlRight( self.list )
        self.Menulist.controlUp( self.buttonOption )
        self.Menulist.controlDown( self.buttonOption )
        self.buttonOption.controlRight( self.list )
        self.buttonOption.controlUp( self.Menulist )
        self.buttonOption.controlDown( self.buttonAbout )
        self.buttonAbout.controlRight( self.list )
        self.buttonAbout.controlUp( self.buttonOption )
        self.buttonAbout.controlDown( self.Menulist )

        # add items to the Menu list
        xbmcgui.lock()
        for category in self.categoryList:         
            self.Menulist.addItem( xbmcgui.ListItem( label=category.name ) )

        
        xbmcgui.unlock()


        # Set Focus on Menulist
        self.setFocus( self.Menulist )

        # Close the Loading Window 
        dialogUI.close()
       
        # Update the list of video 
        
        self.updateControlList( self.currentMenuIdx )
        # Start to diplay the window before doModal call
        self.show()
        
        # No UI is displayed, continue to get and display the picture (would be too long to wait if we were waiting doModla call)
        self.startupdateIconsThread( self.currentMenuIdx )

    def updateData(self, menuSelectIndex):
        """
        Update Data objet for a specific index (menu) 
        """
        # Display Loading Window while we are loading the information from the website
        dialogLoading = xbmcgui.DialogProgress()
        dialogLoading.create(__script_title__, "Chargement des informations", "Veuillez patienter...")

        # Load Main webpage of the Blog
        if ( menuSelectIndex == len(self.categoryList) - 1 ): # Last item of the list (series express)
            #TODO: clean that, this is a temporary fix but it won't support website changes very well
            myEntryListWebPage = blogExternalEntryListWebPage( URL_EXT_WEBPAGE, txdata, txheaders, self.configManager.getDebug() )   
        else:
            myEntryListWebPage = blogEntryListWebPage( URL_MAIN_WEBPAGE + self.categoryList[ menuSelectIndex ].url, txdata, txheaders, self.configManager.getDebug() )
        # Extract data from myCollectionWebPage and copy the content in corresponding Collection Data Instance
        self.categoryList[ menuSelectIndex ].entryList = myEntryListWebPage.getEntryList()
        
        # Update basicDataLoaded flag
        self.categoryList[ menuSelectIndex ].basicDataLoaded = True

        # Close the Loading Window 
        dialogLoading.close()


    def updateControlList( self, menuSelectIndex ):
        """
        Update ControlList objet
        """
        dialogimg = xbmcgui.DialogProgress()
        dialogimg.create(__script_title__, "Chargement des images", "Veuillez patienter...")
        try:
          
            # Check is data have already been loaded for this collection
            if (self.categoryList[ menuSelectIndex ].basicDataLoaded == False):                
                # Never been updated before, go and get the data
                self.updateData( menuSelectIndex )
                
            # Get and Update number of video at the bottom of the page        
            #TODO: filter on video only not only on entry
            numberOfPictures = len( self.categoryList[ menuSelectIndex ].entryList )
            self.strItemNb.setLabel( str(numberOfPictures ) + " Entrées" ) 
                
            # Lock the UI in order to add pictures
            xbmcgui.lock()    

            # Clear all ListItems in this control list 
            self.list.reset()

            for entry in self.categoryList[ menuSelectIndex ].entryList:                
                index = self.categoryList[ menuSelectIndex ].entryList.index( entry )
                title = entry.title
                date  = entry.date
                if entry.videoID:
                    pic   = os.path.join( CACHEDIR, str( entry.videoID ) + ".jpg" )
                else:
                    pic = "default"
                if not os.path.exists( pic ):
                    # images not here use default
                    print"Image" + pic + "not found - use default image"
                    pic = entry.imagePath
                # Add the item to the List 
                self.list.addItem( xbmcgui.ListItem( label=date + "\n" + title, thumbnailImage=pic ) )
                
            if not self.categoryList[ menuSelectIndex ].entryList:
                self.strlist.setLabel("Il n'y a pas d'émissions disponibles")
            else:
                self.strlist.setLabel( "" )
                # Set focus on the list
                self.setFocus( self.list )

            # Go back on 1st button (even if overwritten later)
            self.setFocus( self.Menulist )
        
            # Unlock the UI 
            xbmcgui.unlock()

            dialogimg.close()
        except Exception, e:
            print("Exception")
            print(e)
            print str( sys.exc_info()[0] )
            traceback.print_exc()

            dialogimg.update( 100 )

            # Unlock the UI 
            xbmcgui.unlock()
            dialogimg.close()
            dialogError = xbmcgui.Dialog()
            dialogError.ok( "Erreur", "Impossible de charger la liste des Video du à", "un probleme de connection ou à", "un changement sur le site distant" )

    def startupdateIconsThread( self, menuSelectIndex ):
        """
        Create a thread downloading infos and images of the main list
        """
        self.categoryList[ menuSelectIndex ].stopDataLoadThread = False
        self.updateIcon_thread = Thread( target=self._updateIcons, args=(menuSelectIndex,) )
        self.updateIcon_thread.start()
        
    def stopupdateIconsThread( self, menuSelectIndex ):
        """
        Send a stop to the thread
        """
        self.categoryList[ menuSelectIndex ].stopDataLoadThread = True

    def _updateIcons( self, menuSelectIndex ):
        """
        Retrieve images, video info (URL) and update list
        """
        #TODO: implement STOP of theard
        
        # Now get the images:
        #menuSelectIndex = copy(menuIndex)
        if not self.categoryList[ menuSelectIndex ].extendedDataLoaded:
            try:
                for entry in self.categoryList[ menuSelectIndex ].entryList:
                    
                    if self.categoryList[ menuSelectIndex ].stopDataLoadThread:
                        print "MainWindow - _updateIcons: Stop thread request received: exiting the loop"
                        break                
    
                    index = self.categoryList[ menuSelectIndex ].entryList.index( entry )
                    # Load video XML file
                    if entry.videoID:
                        # Get description
                        if entry.description == "":
                            if entry.fullDescURL:
                                # Try to retrieve the full video description from a webpage
                                #TODO
                                pass
                            else:
                                # Retrieve video info from http API (external video webpage case)
                                info_url = BASE_URL_VIDEO_INFO + entry.videoID
                                videoDescriptText = WebPage( info_url, txdata, txheaders, self.configManager.getDebug() ).Source
                                entry.description = strip_off( videoDescriptText )
    
                        # Get XML
                        myVideoXMLPage = BlogVideoXML( BASE_URL_XML + str( entry.videoID ), txdata, txheaders, self.configManager.getDebug() )
                
                        # Get the URL of the video picture
                        videoimg = myVideoXMLPage.getVideoImageURL()
                        
                        # Get the URL of the video for later on
                        entry.videoHighURL = myVideoXMLPage.getVideoURL( "HQ" )
                        entry.videoLowURL = myVideoXMLPage.getVideoURL( "LQ" )
            
                        videoimgdest = os.path.join( CACHEDIR, str( entry.videoID ) + ".jpg" )
            
                        if not os.path.exists( videoimgdest ):
                            # Download the picture    
                            try:
                                downloadJPG( videoimg, videoimgdest, self.configManager.getDebug() )
                                #print("Downloaded: " + videoimgdest)
                            except:
                                print("Exception on image download")
                                print ( str( sys.exc_info()[0] ) )
                                traceback.print_exc()
                    else:
                        videoimgdest = os.path.join(IMAGEDIR, "Article.png")
                    # Display the picture
                    if os.path.exists( videoimgdest ):
                        entry.imagePath = videoimgdest
                        # Pb here: if thread is not stopped before self.list update -> risk index out of range
                        self.list.getListItem( index ).setThumbnailImage( entry.imagePath )
            except Exception, e:
                print("Exception")
                print(e)
                print (str(sys.exc_info()[0]))
                traceback.print_exc()
            if not self.categoryList[ menuSelectIndex ].stopDataLoadThread:
                self.categoryList[ menuSelectIndex ].extendedDataLoaded = True
        
    def showInfo( self, index ):
        try:
            myVideoTitle      = self.categoryList[ self.currentMenuIdx ].entryList[ index ].title
            myVideoDate       = self.categoryList[ self.currentMenuIdx ].entryList[ index ].date
            myVideoDesciption = self.categoryList[ self.currentMenuIdx ].entryList[ index ].description
            if not self.categoryList[ self.currentMenuIdx ].extendedDataLoaded and self.categoryList[ self.currentMenuIdx ].entryList[ index ].videoID:
                # * Get image *
                myVideoXMLPage = BlogVideoXML( BASE_URL_XML + str( self.categoryList[ self.currentMenuIdx ].entryList[ index ].videoID ), txdata, txheaders, self.configManager.getDebug() )
                videoimgUrl = myVideoXMLPage.getVideoImageURL() # Get the URL of the video picture
                videoimgdest = os.path.join( CACHEDIR, str( self.categoryList[ self.currentMenuIdx ].entryList[ index ].videoID ) + ".jpg" )
                # Get video info for series express via http request api!!!
                if myVideoDesciption == "": 
                    # Retrieve video info from http API (external video webpage case)
                    info_url = BASE_URL_VIDEO_INFO + self.categoryList[ self.currentMenuIdx ].entryList[ index ].videoID
                    videoDescriptText = WebPage( info_url, txdata, txheaders, self.configManager.getDebug() ).Source
                    self.categoryList[ self.currentMenuIdx ].entryList[ index ].description = strip_off( videoDescriptText ) #We use this opportunity in order to update the main list
                    myVideoDesciption = self.categoryList[ self.currentMenuIdx ].entryList[ index ].description
                    
                if not os.path.exists( videoimgdest ):
                    # Download the picture    
                    try:
                        downloadJPG( videoimgUrl, videoimgdest, self.configManager.getDebug() )
                    except:
                        print("Exception on image download")
                        print ( str( sys.exc_info()[0] ) )
                        traceback.print_exc()
                # Display the picture
                if os.path.exists( videoimgdest ):
                    self.categoryList[ self.currentMenuIdx ].entryList[ index ].imagePath = videoimgdest # Otherwise imagePath remain to its default value
                    
                    #We use this opportunity in order to update the main list
                    if self.configManager.getDebug():
                        print "MainWindow - showInfo: Updating image in list"
                        print "- Item index = %d"%index
                        print "- videoimgdest = %s"%videoimgdest
                    self.list.getListItem( index ).setThumbnailImage( videoimgdest )
            if not self.categoryList[ self.currentMenuIdx ].entryList[ index ].videoID:
                self.categoryList[ self.currentMenuIdx ].entryList[ index ].imagePath = os.path.join(IMAGEDIR, "Article.png")        
            videoimg = self.categoryList[ self.currentMenuIdx ].entryList[ index ].imagePath 
           
            # Create winInfoVideo
            winInfoVideo = InfoWindow()
            
            # Update image and info and display
            winInfoVideo.updateInfo( myVideoDate, myVideoTitle, myVideoDesciption )
            winInfoVideo.updateImage( videoimg )
            winInfoVideo.doModal()   
            del winInfoVideo
            
        except Exception, e:
            print("Exception in showInfo")
            print(e)
            print (str( sys.exc_info()[0]) )
            traceback.print_exc()
            dialogError = xbmcgui.Dialog()
            dialogError.ok("Erreur", "Impossible de charger les informations du à", "- un probleme de connection", "- un changement sur le site distant")
    
    def onAction(self, action):
        if action == ACTION_PREVIOUS_MENU:
            # Stop update icons thread if it is running
            self.stopupdateIconsThread(self.currentMenuIdx)
            
            # Clean the cache if requested
            if self.configManager.getCleanCache() == True:
                print "Deleting cache ..."
                self.fileMgr.delFiles( CACHEDIR )
            self.close()

        if ( ( action == ACTION_SHOW_INFO ) or ( action == ACTION_CONTEXT_MENU ) ):
            # Show the information for a video
            chosenIndex = self.list.getSelectedPosition()
     
            # Display Loading Window while we are loading the information from the website
            self.showInfo(chosenIndex)
            
    def onMenuAction( self , menuIndex ):
        """
        Update GUI on Menu click
        """
        if ( self.currentMenuIdx != menuIndex ):
            # Stopping thread in case it is running
            self.stopupdateIconsThread(self.currentMenuIdx)
            self.currentMenuIdx = menuIndex
            self.strButton.setLabel( self.categoryList[self.currentMenuIdx].name )
            self.updateControlList( self.currentMenuIdx )
            self.setFocus( self.Menulist )
            self.startupdateIconsThread( self.currentMenuIdx )
        
    def onControl( self, control ):
        if control == self.Menulist:
            selectedMenu = self.Menulist.getSelectedPosition()
            self.onMenuAction( selectedMenu )

        elif control == self.buttonOption:
            winSettingsVideo = SettingsWindow()
            winSettingsVideo.setWindow( self.configManager ) # include doModal call
            del winSettingsVideo
            
        elif control == self.buttonAbout:
            winAboutVideo = AboutWindow()
            del winAboutVideo

        elif control == self.list:
            chosenIndex = self.list.getSelectedPosition()
    
            try:
                currentEntry = self.categoryList[ self.currentMenuIdx ].entryList[ chosenIndex ]
                
                # Check if thread already has download video info    
                if not self.categoryList[ self.currentMenuIdx ].extendedDataLoaded and self.categoryList[ self.currentMenuIdx ].entryList[ chosenIndex ].videoID:
                    # Display Loading Window while we are loading the information from the website
                    dialogVideo = xbmcgui.DialogProgress()
                    
                    dialogVideo.create("Blog d'Alain Carrazé", "Chargement des informations sur la vidéo", "Veuillez patienter...")
                    #TODO: Cache the XML too??
                    # Get XML
                    myVideoXMLPage = BlogVideoXML( BASE_URL_XML + str( currentEntry.videoID ), txdata, txheaders, self.configManager.getDebug() )
            
                    # Get the URL of the video picture
                    videoimg = myVideoXMLPage.getVideoImageURL()
                    
                    # Get the URL of the video for later on
                    currentEntry.videoHighURL = myVideoXMLPage.getVideoURL( "HQ" )
                    currentEntry.videoLowURL = myVideoXMLPage.getVideoURL( "LQ" )
                    
                    # Video thumb
                    videoimgdest = os.path.join( CACHEDIR, str( currentEntry.videoID ) + ".jpg" )
                    
                    dialogVideo.update( 100 )
                    xbmc.sleep( 100 )
                    dialogVideo.close()

                videoURL = ( currentEntry.videoHighURL, currentEntry.videoLowURL )[ self.configManager.getVideoQuality() == "LQ" ]
                videoimgdest = os.path.join( CACHEDIR, str( currentEntry.videoID ) + ".jpg" )
                if not os.path.exists( videoimgdest ):
                    #TODO: download image
                    videoimgdest = ""


                if videoURL:
                    # Play the selected video
                    print("Play the selected video: %s"%videoURL)
                    #chosenListItem =  self.list.getListItem( chosenIndex )
                    #chosenListItem.setLabel( chosenListItem.getLabel().replace("\n", " - ") )
                    
                    if currentEntry.type == "video_external":
                        videoListItem = xbmcgui.ListItem( label=self.categoryList[ self.currentMenuIdx ].name + ": " + currentEntry.title, thumbnailImage=videoimgdest) 
                    else: 
                        videoListItem = xbmcgui.ListItem( label=currentEntry.date + " - " + currentEntry.title, thumbnailImage=videoimgdest) 
                    #currentListItem.setInfo('video', {'Title': currentListItem.getLabel().replace("\n", " - "), 'Genre': 'Series TV'})
                    xbmc.Player( self.configManager.getDefaultPlayer() ).play( videoURL, videoListItem )
                else:
                    # Show the information for a video
             
                    # Display Loading Window while we are loading the information from the website
                    self.showInfo(chosenIndex)

            except Exception, e:
                print("Exception")
                print(e)
                print ( str( sys.exc_info()[0] ) )
                traceback.print_exc()
                dialogError = xbmcgui.Dialog()
                dialogError.ok("Erreur", "Impossible de charger les informations du à", "un probleme de connection ou à", "un changement sur le site distant")
  
  

def startup():
    """
    
        Startup function
    
    """
    print( str( "=" * 85 ) )
    print( "" )
    print( "TAC.tv XBMC script STARTS".center( 85 ) )
    print( (__script_title__ + " script" + __version__ + " by "+ __author__ +"STARTS").center( 85 ) )
    print( "" )
    print( str( "=" * 85 ) )

    # Create main Window
    bloggui = MainWindow()
    
    # Display this window until close() is called
    bloggui.doModal()
    
    del bloggui



########
#
# Main
#
########

if __name__ == "__main__":
    # Calling startup function
    startup()
else:
    # Library case
    pass
 

