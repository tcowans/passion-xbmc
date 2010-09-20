# -*- coding: utf-8 -*-
__addonID__      = "plugin.programm.books"

import os
import sys
from traceback import print_exc

import xbmc
import xbmcgui
import xbmcaddon
import urllib2

#modules custom
from specialpath import *
from DBlib import *
from elementtree import ElementTree

imgUserDir = os.path.join( sys.modules[ "__main__" ].SPECIAL_SCRIPT_DATA, "img" )

#import MyFont
#Add Fonts
#try:  
#  MyFont.addFont( "book10" , "book.ttf" , "10")
#  MyFont.addFont( "book12" , "book.ttf" , "12")
#except : pass

# INITIALISATION CHEMIN RACINE
ROOTDIR = os.getcwd().replace( ";", "" )


#get actioncodes from keymap.xml
ACTION_PREVIOUS_MENU = 10





class MainGui( xbmcgui.WindowXMLDialog ):
    def __init__( self, *args, **kwargs ):
        xbmcgui.WindowXMLDialog.__init__( self, *args, **kwargs )
        
        
 
    def onInit(self):
    
      #Language :
      self.Language = xbmcaddon.Addon( __addonID__ )

      #Controls :
      self.title = self.getControl(1)
      self.scrapListTitle = self.getControl(2)
      self.optionsTitle = self.getControl(3)
      self.scrapList = self.getControl(4)
      self.okTitle = self.getControl(28)
      self.cancelTitle = self.getControl(29)
      self.argOneTitle = self.getControl(11)
      self.argTwoTitle = self.getControl(12)
      self.argThreeTitle = self.getControl(13)

      #Change label text :
      self.title.setLabel( self.Language.getLocalizedString(510) )
      self.scrapListTitle.setLabel( self.Language.getLocalizedString(511) )
      self.optionsTitle.setLabel( self.Language.getLocalizedString(512) )
      self.okTitle.setLabel( self.Language.getLocalizedString(514) )
      self.cancelTitle.setLabel( self.Language.getLocalizedString(513) )
      self.argOneTitle.setLabel( self.Language.getLocalizedString(516) )
      self.argTwoTitle.setLabel( self.Language.getLocalizedString(515) )

      #Add Scraper List
      #create Listitem
      listitem = xbmcgui.ListItem( "LibFLY" )
      listitem.setIconImage('logo-libfly.gif')
      self.scrapList.addItem( listitem )
      #create Listitem
      listitem = xbmcgui.ListItem( "BDGest" )
      listitem.setIconImage('logo-bdgest.png')
      self.scrapList.addItem( listitem )

      #Init Args
      self.argOneContent = ""
      self.argTwoContent = ""
      self.argThreeContent = ""
            
                    
    def show_keyboard (self, textDefault, textHead, textHide=False) :
        """Show the keyboard's dialog"""
        keyboard = xbmc.Keyboard(textDefault, textHead)
        inputText = ""
        if textHide == True :
            keyboard.setHiddenInput(True)
        keyboard.doModal()
        if (keyboard.isConfirmed()):
            inputText = keyboard.getText()         
            dialogInfo = xbmcgui.Dialog()
        del keyboard
        return inputText

  
   

    def onContainerList( self ):
        """ content item not work in onClick( self, controlID )
            but use <onclick>SetProperty(Container_9000_item_id,int)</onclick> and in onAction( self, action )
            use if self.getFocusId() == 9000: print self.getProperty( "Container_9000_item_id" )
        """
        try:
            if self.getFocusId() == 4:
                print "yo"
                item_id = self.getControl(4).getSelectedPosition()
                print "Container_9000_item_id", item_id
                if item_id == 0:
                        self.getControl(4).selectItem(0)
                        xbmc.executebuiltin( "Skin.SetString(arg1,1)" )
                        xbmc.executebuiltin( "Skin.SetString(arg2,1)" )
                        xbmc.executebuiltin( "Skin.SetString(arg3,0)" )
                        self.argOneTitle.setLabel( self.Language.getLocalizedString(516) )
                        self.argTwoTitle.setLabel( self.Language.getLocalizedString(515) )
                if item_id == 1:
                        self.getControl(4).selectItem(1)
                        xbmc.executebuiltin( "Skin.SetString(arg1,1)" )
                        xbmc.executebuiltin( "Skin.SetString(arg2,1)" )
                        xbmc.executebuiltin( "Skin.SetString(arg3,1)" )
                        self.argOneTitle.setLabel( self.Language.getLocalizedString(516) )
                        self.argTwoTitle.setLabel( self.Language.getLocalizedString(517) )
                        self.argThreeTitle.setLabel( self.Language.getLocalizedString(518) )
        
        except:
            pass  
            
    def onAction(self, action):
        #Close the script
        
        if action == ACTION_PREVIOUS_MENU :
            self.close()
        self.onContainerList()
        
    def onClick(self, controlID):
        """
            Notice: onClick not onControl
            Notice: it gives the ID of the control not the control object
        """
        
        print controlID
        
        if controlID == 11 : 
            self.argOneContent = ""
            self.argOne_GetTitle = self.show_keyboard ("", self.Language.getLocalizedString(516))
            label = self.Language.getLocalizedString(516)
            label_colored = "[COLOR=%s]%s[/COLOR]" % ( "ff555555", self.argOne_GetTitle  )
            self.getControl( controlID ).setLabel( label , label2=label_colored )
            self.argOneContent = self.argOne_GetTitle
        
        if controlID == 12 : 

            if self.scrapList.getSelectedPosition() == 0 : 
                self.argTwoContent = ""
                self.argTwo_GetTitle = self.show_keyboard ("", self.Language.getLocalizedString(515))
                label = self.Language.getLocalizedString(515)
                label_colored = "[COLOR=%s]%s[/COLOR]" % ( "ff555555", self.argTwo_GetTitle  )
                self.getControl( controlID ).setLabel( label , label2=label_colored )
                self.argTwoContent = self.argTwo_GetTitle

            if self.scrapList.getSelectedPosition() == 1 : 
                self.argTwoContent = ""
                self.argTwo_GetTitle = xbmcgui.Dialog().browse( 1 , self.Language.getLocalizedString(517) , 'files' , '.xml')
                label = self.Language.getLocalizedString(517)
                label_colored = "[COLOR=%s]%s[/COLOR]" % ( "ff555555", self.argTwo_GetTitle  )
                self.getControl( controlID ).setLabel( label , label2=label_colored )
                self.argTwoContent = self.argTwo_GetTitle
        
        if controlID == 13 : 

            if self.scrapList.getSelectedPosition() == 0 : 
                self.argThreeContent = ""
                self.argThree_GetTitle = self.show_keyboard ("", self.Language.getLocalizedString(517))
                label = self.Language.getLocalizedString(515)
                label_colored = "[COLOR=%s]%s[/COLOR]" % ( "ff555555", self.argThree_GetTitle  )
                self.getControl( controlID ).setLabel( label , label2=label_colored )
                self.argThreeContent = self.argThree_GetTitle

            if self.scrapList.getSelectedPosition() == 1 : 
                self.argThreeContent = ""
                self.argThree_GetTitle = xbmcgui.Dialog().browse( 0 , self.Language.getLocalizedString(518) , 'files'	)
                label = self.Language.getLocalizedString(518)
                label_colored = "[COLOR=%s]%s[/COLOR]" % ( "ff555555", self.argThree_GetTitle  )
                self.getControl( controlID ).setLabel( label , label2=label_colored )
                self.argThreeContent = self.argThree_GetTitle

        if controlID == 40 : 
            if self.scrapList.getSelectedPosition() == 0 : 
                xbmc.executebuiltin( "Skin.SetString(arg1,1)" )
                xbmc.executebuiltin( "Skin.SetString(arg2,1)" )
                xbmc.executebuiltin( "Skin.SetString(arg3,0)" )
                self.argOneTitle.setLabel( self.Language.getLocalizedString(516) )
                self.argTwoTitle.setLabel( self.Language.getLocalizedString(515) )
            if self.scrapList.getSelectedPosition() == 1 : 
                xbmc.executebuiltin( "Skin.SetString(arg1,1)" )
                xbmc.executebuiltin( "Skin.SetString(arg2,1)" )
                xbmc.executebuiltin( "Skin.SetString(arg3,1)" )
                self.argOneTitle.setLabel( self.Language.getLocalizedString(516) )
                self.argTwoTitle.setLabel( self.Language.getLocalizedString(515) )
                self.argThreeTitle.setLabel( self.Language.getLocalizedString(517) )
        
        if controlID == 28 : 
            #Init DBtools
            DBtools = MyBooksDB()

            #Recup de l'id du scraper
            scrapID = self.scrapList.getSelectedPosition()
            print "l'id de la source est %s"% (scrapID)
    
            pDialog = xbmcgui.DialogProgress()
            pDialog.create(self.Language.getLocalizedString(54),self.Language.getLocalizedString(55))
            pDialog.update(0)

            if scrapID == 0 :

                sourceTitle = self.argOneContent
                userID = self.argTwoContent
                sourceID = DBtools.addSource(sourceTitle, 1, userID)

                from LibFly import LibFlyBooks
                LibFlyBooksArray = LibFlyBooks(userID,scrapID+1)
                BooksArray = LibFlyBooksArray.getBooks()

                DBtools.addBooks(BooksArray,sourceID)

            if scrapID == 1 :

                sourceTitle = self.argOneContent
                xmlPath = self.argTwoContent
                imgPath = self.argThreeContent
                sourceID = DBtools.addSource(sourceTitle, 2, xmlPath, imgPath)

                from XMLscraper import XmlBooks
                XmlBooksArray = XmlBooks(xmlPath,imgPath, sourceID)
                BooksArray = XmlBooksArray.getBooks()

                DBtools.addBooks(BooksArray,sourceID)

            pDialog.update(100)
        
            pDialog.close()


            self.close()

    
            
  
    def onFocus(self, controlID):
        pass





class ShowBook( xbmcgui.WindowXMLDialog ):
    def __init__( self, *args, **kwargs ):
        xbmcgui.WindowXMLDialog.__init__( self, *args, **kwargs )
        print args
        print kwargs
        self.bookIsbn = kwargs['isbn']
        self.booktitre = kwargs['titre']
        self.bookauteur = kwargs['auteur']
        self.bookediteur = kwargs['editeur']
        self.bookimage = kwargs['image']
        self.bookpage = kwargs['page']
        self.bookstyle = kwargs['style']
        self.bookdescription = kwargs['description']
        self.booksource = kwargs['source']
        self.bookdate = kwargs['date']
        self.booklangue = kwargs['langue']
 
    def onInit(self):
    
      #Language :
      self.Language = xbmcaddon.Addon( __addonID__ )

      #Controls :

      self.author = self.getControl(2)
      self.editor = self.getControl(3)
      self.numpage = self.getControl(4)
      self.style = self.getControl(5)
      self.langue = self.getControl(6)
      self.date = self.getControl(7)
      self.source = self.getControl(8)

      self.title = self.getControl(1)
      self.bookImg = self.getControl(20)
      self.descText = self.getControl(31)

      self.okTitle = self.getControl(28)
      self.cancelTitle = self.getControl(29)

      #Change label text :
      self.author.setLabel( self.bookauteur )
      self.editor.setLabel( self.bookediteur )
      self.numpage.setLabel( str(self.bookpage) )
      self.style.setLabel( self.bookstyle )
      self.langue.setLabel( self.booklangue )
      self.date.setLabel( self.bookdate )

      self.okTitle.setLabel( self.Language.getLocalizedString(514) )
      self.cancelTitle.setLabel( self.Language.getLocalizedString(513) )
      self.title.setLabel( self.booktitre )
      self.descText.setText( self.bookdescription.encode("utf8","replace") )

      #Set image :
      imgExt = self.bookimage[-3:]
      imgName = "%s.%s" % (self.bookIsbn, imgExt)
      imgPath = os.path.join(imgUserDir,imgName)
      print imgPath
      self.bookImg.setImage(imgPath)
      #Scraper Image :
      if self.booksource[0] == 1 :
          self.source.setImage("logo-libfly.gif")
            
    def onAction(self, action):
        #Close the script
        
        if action == ACTION_PREVIOUS_MENU :
            self.close()
        
    def onClick(self, controlID):
        """
            Notice: onClick not onControl
            Notice: it gives the ID of the control not the control object
        """
        
        print controlID

    
            
  
    def onFocus(self, controlID):
        pass
















def AddSource():

    base_path = os.getcwd()
    w = MainGui("default.xml", base_path, "Default.HD")
    w.doModal()
    del w

def DisplayInfo(bookInfo) :
    base_path = os.getcwd()
    w = ShowBook("showbook.xml", base_path, "Default.HD", isbn = bookInfo[0] , titre = bookInfo[1] , auteur = bookInfo[10] , editeur = bookInfo[8] , image = bookInfo[5] , page = bookInfo[6] , style = bookInfo[11] , description = bookInfo[2] , source = bookInfo[7] , date = bookInfo[9] , langue = bookInfo[3])
    w.doModal()
    del w


def test():
    MyDisplay()
    
