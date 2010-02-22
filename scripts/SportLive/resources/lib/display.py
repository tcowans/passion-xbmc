# -*- coding: utf-8 -*-
"""Description du script"""

# script constantes
__script__       = "Nom du script"
__plugin__       = "Nom du script"
__author__       = "Ppic , CinPoU, Frost"
__credits__      = "Team XBMC-Passion, http://passion-xbmc.org/"
__platform__     = "xbmc media center, [LINUX, OS X, WIN32, XBOX]"
__date__         = "24-12-2009"
__version__      = "0.0.1"


#Bibliothèques généralistes
import os
import re
import sys
import xbmc, xbmcgui
import time

from traceback import print_exc


# INITIALISATION CHEMIN RACINE
ROOTDIR = os.getcwd().replace( ";", "" )

# Utilisation du snippet permettant la gestion des différents dossiers de XBMC (Cf. fichier "specialpath.py" dans le dossier "libs")
BASE_RESOURCE_PATH = os.path.join( ROOTDIR, "resources" )
# append the proper platforms folder to our path, xbox is the same as win32
env = ( os.environ.get( "OS", "win32" ), "win32", )[ os.environ.get( "OS", "win32" ) == "xbox" ]
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "platform_libraries", env ) )
# append the proper libs folder to our path
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "lib" ) )

xbmc.executebuiltin( "Skin.Reset(TabSettings)" )
xbmc.executebuiltin( "Skin.SetString(TabSettings,1)" )




#On attributs des noms aux actions correspondant aux touches du clavier (cf. keymap.xml)
ACTION_PREVIOUS_MENU = 10

##update1={'A': False, 'A_name': 'New Jersey', 'url': '/nba/2010/direct.html', 'country': 'US', 'B_score': '35', 'start': '01h30', 'part': '', 'B_name': 'Minnesota', 'diff': True, 'B': True, 'sport': 'nba', 'A_score': '30'}
##update2={'A': False, 'A_name': 'Panthers Floride', 'url': '/nba/2010/direct.html', 'country': 'US', 'B_score': '12', 'start': '02h30', 'part': '', 'B_name': 'vancouver canucks', 'diff': True, 'B': True, 'sport': 'nhl', 'A_score': '18'}
##update3 = {'B': True, 'A': True, 'A_name': 'Colorado Avalanche', 'url': '/nba/2010/direct.html', 'country': 'US', 'B_score': '43', 'start': '02h30', 'part': '', 'B_name': 'Nashville Predators', 'sport': 'nhl', 'A_score': '43'}
##update3 = {'B': True, 'A_name': 'Sela *', 'url': '/tennis/directs/chennai/index.html', 'country': 'chennai', 'B_score': '6/2/6/2', 'start': '', 'part': '', 'B_name': 'Wawrinka', 'diff': True, 'sport': 'tennis', 'A_score': '4/5/7/2'}
##update=[]
##update.append(update1)
##
##update.append(update3)
##update.append(update3)
##update.append(update2)
##print update

#On définit la class gérant l'affichage en windowXML
class MainGUI(xbmcgui.WindowXMLDialog):
    """The main GUI"""

    def __init__( self, *args, **kwargs ):
        xbmcgui.WindowXMLDialog.__init__( self, *args, **kwargs)
        self.update = kwargs.get( "dico" )
        self.imagepath = os.path.join( BASE_RESOURCE_PATH, "images" )
 
    def onInit(self):        
        # Ici on déclare une variable pour chaque élément à manipuler. Le nombre correspond à l'id déclaré dans le fichier xml
        #print self.update
        self.Group = self.getControl(201)
        
        self.sport_equip = self.getControl(2010)
        self.country_equip = self.getControl(2050)
        self.image_equip1 = self.getControl(2011)
        self.nom_equip1 = self.getControl(2012)
        self.score_equip1 = self.getControl(2013)
        self.image_equip2 = self.getControl(2021)
        self.nom_equip2 = self.getControl(2022)
        self.score_equip2 = self.getControl(2023)

        self.sport_joueur = self.getControl(2030)
        self.country_joueur = self.getControl(2031)
        self.nom_joueur1 = self.getControl(2032)
        self.nom_joueur2 = self.getControl(2033)
        self.score_joueur1 = self.getControl(2034)
        self.score_joueur2 = self.getControl(2035)
        self.image_joueur1 = self.getControl(2036)
        self.image_joueur2 = self.getControl(2037)

              
        for match in self.update:
            if match["sport"] == "tennis":
                self.sport_equip.setVisible(False)
                self.country_equip.setVisible(False)        
                self.image_equip1.setVisible(False)
                self.nom_equip1.setVisible(False)
                self.score_equip1.setVisible(False)
                self.image_equip2.setVisible(False)
                self.nom_equip2.setVisible(False)
                self.score_equip2.setVisible(False)
                
                self.sport_joueur.setVisible(True)
                self.country_joueur.setVisible(True)
                self.nom_joueur1.setVisible(True)
                self.nom_joueur2.setVisible(True)
                self.score_joueur1.setVisible(True)
                self.score_joueur2.setVisible(True)
                self.image_joueur1.setVisible(False)
                self.image_joueur2.setVisible(False)

                self.sport_joueur.setLabel( match["sport"] )
                self.country_joueur.setLabel( match["country"] )
                self.nom_joueur1.setLabel( match["A_name"].strip( " *" ) )
                self.nom_joueur2.setLabel( match["B_name"].strip( " *" ) )

                if "*" in match["A_name"]:
                    self.image_joueur1.setVisible(True)
                    self.image_joueur1.setImage(os.path.join(self.imagepath, match["sport"] , "default.png" ))
                if "*" in match["B_name"]:
                    self.image_joueur2.setVisible(True)
                    self.image_joueur2.setImage(os.path.join(self.imagepath, match["sport"] , "default.png" ))

                match["A_score"] = match["A_score"].replace("/" , " | ")
                match["B_score"] = match["B_score"].replace("/" , " | ")
                if "A" in match: 
                    if match["A"]:
                        match["A_score"] = "[COLOR=ff00ff00]%s[/COLOR]" % match["A_score"]
                                                
                if "B" in match: 
                    if match["B"]:
                        match["B_score"] = "[COLOR=ff00ff00]%s[/COLOR]" % match["B_score"]                                             
                    
                self.score_joueur1.setLabel( match["A_score"] )
                self.score_joueur2.setLabel( match["B_score"] )

            else:
                self.sport_joueur.setVisible(False)
                self.country_joueur.setVisible(False)
                self.nom_joueur1.setVisible(False)
                self.nom_joueur2.setVisible(False)
                self.score_joueur1.setVisible(False)
                self.score_joueur2.setVisible(False)
                self.image_joueur1.setVisible(False)
                self.image_joueur2.setVisible(False)
                
                self.sport_equip.setVisible(True)
                self.country_equip.setVisible(True)        
                self.image_equip1.setVisible(True)
                self.nom_equip1.setVisible(True)
                self.score_equip1.setVisible(True)
                self.image_equip2.setVisible(True)
                self.nom_equip2.setVisible(True)
                self.score_equip2.setVisible(True)
                
                self.sport_equip.setLabel( match["sport"] )
                self.country_equip.setLabel( match["country"] )
                self.image_equip1.setImage(os.path.join(self.imagepath, match["sport"] , "%s.png" % match["A_name"]))
                if "A" in match: 
                    if match["A"]:match["A_score"] = "[COLOR=ff00ff00]%s[/COLOR]" % match["A_score"]
                self.nom_equip1.setLabel( match["A_name"] )
                self.score_equip1.setLabel( match["A_score"] )
                self.image_equip2.setImage(os.path.join(self.imagepath, match["sport"] , "%s.png" % match["B_name"]))
                if "B" in match: 
                    if match["B"]:match["B_score"] = "[COLOR=ff00ff00]%s[/COLOR]" % match["B_score"]
                self.nom_equip2.setLabel( match["B_name"] )
                self.score_equip2.setLabel( match["B_score"] )
            
            
            time.sleep(5)
        
        #self.score_equip1.setLabel( "56" )
        #self.score_equip2.setLabel( "78" )
        #time.sleep(3)
        xbmc.executebuiltin( "Skin.SetString(TabSettings,0)" )
        time.sleep(2)
        self.close()

            
    # Cette def permet de gérer les actions en fonctions de la touche du clavier pressée
    def onAction(self, action):
        #Close the script
        if action == ACTION_PREVIOUS_MENU :
            xbmc.executebuiltin( "Skin.SetString(TabSettings,0)" )
            time.sleep(2)
            self.close()

    # Cette def permet de gérer les actions sur les boutons du windowXML. Pour chaque bouton manipulé, son id est associé à une action. 
    def onClick(self, controlID):
        """
            Notice: onClick not onControl
            Notice: it gives the ID of the control not the control object
        """
        pass 
  
    def onFocus(self, controlID):
        pass


def getUserSkin():
    current_skin = xbmc.getSkinDir()
    force_fallback = os.path.exists( os.path.join( ROOTDIR, "resources", "skins", current_skin ) )
    if not force_fallback: current_skin = "DefaultSkin"
    return current_skin, force_fallback

def display( update ):
    xbmc.executebuiltin( "Skin.Reset(TabSettings)" )
    xbmc.executebuiltin( "Skin.SetString(TabSettings,1)" )
    current_skin, force_fallback = getUserSkin()
    #"MyDialog.xml", CWD, current_skin, force_fallback sert a ouvrir le xml du script
    w = MainGUI( "display.xml", ROOTDIR, current_skin, force_fallback , dico=update )
    w.doModal()
    del w


