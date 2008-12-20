#
#      Copyright (C) 2005-2008 Team XBMC
#      http://www.xbmc.org
#
#  This Program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2, or (at your option)
#  any later version.
#
#  This Program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with XBMC; see the file COPYING.  If not, write to
#  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
#  http://www.gnu.org/copyleft/gpl.html
#

import xbmc
import xbmcgui
import browse_scripts_plugins as browse
import os

#get actioncodes from keymap.xml

ACTION_MOVE_LEFT                            = 1 
ACTION_MOVE_RIGHT                           = 2
ACTION_MOVE_UP                              = 3
ACTION_MOVE_DOWN                            = 4
ACTION_PAGE_UP                              = 5
ACTION_PAGE_DOWN                            = 6
ACTION_SELECT_ITEM                      = 7
ACTION_HIGHLIGHT_ITEM                   = 8
ACTION_PARENT_DIR                           = 9
ACTION_PREVIOUS_MENU                    = 10
ACTION_SHOW_INFO                            = 11

ACTION_PAUSE                                    = 12
ACTION_STOP                                     = 13
ACTION_NEXT_ITEM                            = 14
ACTION_PREV_ITEM                            = 15

RootDir  = os.getcwd().replace( ";", "" ) # Create a path with valid format
cacheDir = os.path.join(RootDir, "cache")


class Window(xbmcgui.Window):
    def __init__(self):
    
        self.addControl(xbmcgui.ControlImage(0,0,720,576, 'background.png'))
        self.list = xbmcgui.ControlList(200, 100, 400, 400)        
        self.addControl(self.list)
        
        """
        Chemin à mettre dans le conf.cfg
        """
        DB = os.path.join(RootDir, 'DB.db')
        if not os.path.isfile(DB):
            browse.maketable()
        
        """
        self.racine = 11 correspond à la catégorie des scripts et plugins dans le centre de download
        Eventuellement à mettre dans le conf.cfg.
        """
        self.racine = 11
        self.curlist = browse.incat(self.racine)
        self.updateList()
    
    def onAction(self, action):
        if action == ACTION_PREVIOUS_MENU:
            self.close()
        if action == ACTION_PARENT_DIR:
            if self.curlist['parent'][0] != self.racine: 
                """
                Affichage de la catégorie mère. On utilise le parent du premier item de la liste du 
                dictionnaire parent pour cela (tous identiques).
                """   
                self.curlist = browse.outcat(self.curlist['parent'][0])
                self.updateList()
            else:
                """
                Si on est déjà à la racine on réaffiche la catégorie racine. Sert aussi si on vient 
                d'une catégorie fille vide.
                """
                self.curlist = browse.incat(self.racine)
                self.updateList()

    
    def onControl(self, control):
        if control == self.list:
            item = self.list.getSelectedPosition()
            if self.curlist['type'][item] == 'dlcat':
                """
                Cas d'une catégorie, on fait une sauvegarde la liste précédente, au cas où la suivante
                soit vide.
                """
                savelist = self.curlist
                self.curlist = browse.incat(self.curlist['id'][item])
                self.updateList()
                if self.curlist['id'] == []:
                    self.curlist = savelist
 
            else:
                """
                Récupération des informations associées si c'est un fichier. Tentative d'affichage 
                dans la classe infowindow mais ne marche pas, je comprend pas bien pourquoi.
                """
                showitem = browse.info(self.curlist['id'][item])
                print showitem 
                info = InfoWindow(showitem)
                del info             
    
    def updateList(self):
        """
        Update de la liste tout simple, rien à signaler.
        """
        xbmcgui.lock()
        self.list.reset()
        for i in self.curlist['name']:
            self.list.addItem(i)
        xbmcgui.unlock()
        self.setFocus(self.list)
        

class InfoWindow(xbmcgui.WindowDialog):
    """
    Information Window : Merci Temhil ;-)
    """
    def __init__(self, item):
        if Emulating: xbmcgui.Window.__init__(self)
        if not Emulating:
            self.setCoordinateResolution(PAL_4x3) # Set coordinate resolution to PAL 4:3

        # Background image
        self.addControl(xbmcgui.ControlImage(100,100,545,435, os.path.join(IMAGEDIR,"dialog-panel.png")))

        self.strTitle = xbmcgui.ControlLabel(130, 110, 350, 30, "INFORMATION ITEM",'special13')
        self.addControl(self.strTitle)
        self.helpTextBox = xbmcgui.ControlTextBox(130, 140, 540-70, 350, font="font10", textColor='0xFFFFFFFF')
        self.addControl(self.helpTextBox)
        self.helpTextBox.setVisible(True)
        self.setFocus(self.helpTextBox)
         
        # Code copied form Navix-X - Thanks!
        try:            
            text=""
            #lines = data.split("\n")
            #we check each line if it exceeds 70 characters and does not contain
            #any space characters (e.g. long URLs). The textbox widget does not
            #split up these strings. In this case we add a space characters ourself.
            for m in item:
                if (len(m) > 70) and (m.find(" ") == -1):
                    m = m[:70] + " " + m[70:]
                text = text + m + "\n"
            self.helpTextBox.setText(text)
        except IOError:
            print "Help File does not exist!"         
            dialogError = xbmcgui.Dialog()
            dialogError.ok("Aide Nabbox", "le fichier d'aide %s n'a pas été trouvé"%"NABBOX_Aide.txt")
            self.helpTextBox.setText("Impossible de trouve le fichier d'aide %s"%"NABBOX_Aide.txt")
        self.doModal()

w = Window()
w.doModal()

del w
