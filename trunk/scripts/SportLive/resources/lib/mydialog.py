# -- coding: cp1252 -*-

import os
import sys
from traceback import print_exc

import xbmc
import xbmcgui


CWD = os.getcwd().rstrip( ";" )

SPECIAL_PROFILE_DIR = xbmc.translatePath( "special://profile/" )
GET_LOCALIZED_STRING = xbmc.Language( CWD ).getLocalizedString

ACTION_PREVIOUS_MENU = 10


class MainGui( xbmcgui.WindowXMLDialog ):
    def __init__( self, *args, **kwargs ):
        xbmcgui.WindowXMLDialog.__init__( self, *args, **kwargs )
        self.tempfile = os.path.join( os.getcwd() , "resources" , "sportsfr.temp" )
        self.filterfile = os.path.join( os.getcwd() , "resources" , "filter" )
        self.matchlist = eval( file( self.tempfile , "r" ).read() )
        
 
    def onInit(self):
      self.title = self.getControl(210)
      self.title.setLabel( GET_LOCALIZED_STRING( 32000 ) )
      #On identifie la liste par son id
      self.xml_list = self.getControl(200)
      
      #Création du dictionnaire
      self.liste_equipe = self.matchlist
      if self.liste_equipe == []:self.liste_equipe = [ {'sport': GET_LOCALIZED_STRING( 32100 ), 'A_name': '', 'B_name': ''} ]
      for equipe in self.liste_equipe :
          equipe['selection'] = 'false'
      self.listEquipe(self.liste_equipe)
      
      
      ######PLACE LE CODE A EXECUTER AU DEMARRAGE ICI
        
        
    ######PLACE TES DEF ICI

    
      
    def listEquipe(self, equipes):
      self.xml_list.reset()  
      for equipe in equipes :
            
            #On crée un element de liste, avec son label
            listitem = xbmcgui.ListItem( ( "%s  %s - %s" % ( equipe['sport'] , equipe['A_name'] , equipe['B_name'] ) ).strip( " -" ) )
            #On définit la variable clicked de l'élément liste
            listitem.setProperty( "clicked", equipe['selection'] )
            #On injecte l'élément liste à la liste xml
            self.xml_list.addItem( listitem )

            
    # Cette def permet de gérer les actions en fonctions de la touche du clavier pressée
    def onAction(self, action):
        #Close the script
        if action == ACTION_PREVIOUS_MENU :
            self.close() 
        
    def onClick(self, controlID):
        """
            Notice: onClick not onControl
            Notice: it gives the ID of the control not the control object
        """
        #action sur la liste
        if controlID == 200 : 
            #Renvoie le numéro de l'item sélectionné
            num = self.xml_list.getSelectedPosition()
            
            #Traitement de l'information
            if self.liste_equipe[num]['selection'] == "false" :
                self.liste_equipe[num]['selection'] = "true"
            else :
                self.liste_equipe[num]['selection'] = "false"
            #item = self.xml_list.getSelectedItem()
            #item.setProperty( "clicked", self.liste_equipe[num]['selection'] )
            
            self.listEquipe(self.liste_equipe)
            self.xml_list.selectItem(num)
            
        if controlID == 9001 :
            matchfilter=[]
            for equipe in self.liste_equipe :
                if equipe['selection'] == "true" :
                    selected={}
                    print "%s  %s - %s" % ( equipe['sport'] , equipe['A_name'] , equipe['B_name'] )
                    selected['sport'] = equipe['sport']
                    selected['A_name'] = equipe['A_name'].strip(" *")
                    selected['B_name'] = equipe['B_name'].strip(" *")
                    matchfilter.append(selected)

            file( self.filterfile , "w" ).write( repr( matchfilter ) )
            self.close()
            
  
    def onFocus(self, controlID):
        pass


def getUserSkin():
    current_skin = xbmc.getSkinDir()
    force_fallback = os.path.exists( os.path.join( CWD, "resources", "skins", current_skin ) )
    if not force_fallback: current_skin = "DefaultSkin"
    return current_skin, force_fallback


def MyDialog():
    current_skin, force_fallback = getUserSkin()
    #"MyDialog.xml", CWD, current_skin, force_fallback sert a ouvrir le xml du script
    w = MainGui( "MyDialog.xml", CWD, current_skin, force_fallback)
    w.doModal()
    del w


def test():
    MyDialog()
