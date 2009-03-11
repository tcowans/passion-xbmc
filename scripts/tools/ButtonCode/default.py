
"""
More infos about Button Codes: 
url = http://www.xboxmediacenter.com/wiki/index.php?title=Building_Scripts#Button_Codes:

Or to obtain an updated list of Action & Button Codes, please see: Key.h and XBIRRemote.h
url = http://xbmc.svn.sourceforge.net/viewvc/xbmc/trunk/XBMC/guilib/Key.h?view=markup
url = http://xbmc.svn.sourceforge.net/viewvc/xbmc/trunk/XBMC/xbmc/XBIRRemote.h?view=markup

PS: For infos keyboard layout.
url = http://en.wikipedia.org/wiki/Keyboard_layout

NOTE: - The last CODE Button in DIC please not include ',' a ends line.
        include a ',' create a bug python
      - and Python won't run the lines that we put a '#' in front of they are considered as
        "commented out" python will skip them.
"""

#####################################################################################################
''' Infos: Data '''
#####################################################################################################
__author__    = '''FrostBox'''
__date__      = '''13 December 2006'''
__title__     = '''Button Code Reference'''
__version__   = '''1.0.0'''

#####################################################################################################
''' Module: import '''
#####################################################################################################
import os , os.path
import xbmc , xbmcgui

#####################################################################################################
''' Function: Global '''
#####################################################################################################
class KeymapGeneral:
    def __init__(self):
        self.EXITSCRIPTS = {
            # Controller: Button Code Reference
            275 : "Back Button",
            # Remote: Button Code Reference
            247 : "Menu Button",
            # Additional keys from the media center extender for xbox remote
            249 : "Clear Button",
            # Mouse: Button Code Reference not used
            # USB Keyboard: Button Code Reference
            61467 : "Escape Button"
            }

PADSIZE = {"w":276, "h":258}
PADIMG  = os.path.join(os.getcwd(), "media", "pad.png")

DVDSIZE = {"w":118, "h":188}
DVDIMG  = os.path.join(os.getcwd(), "media", "xbox dvd kit.png")

KBSIZE  = {"w":289, "h":232}
KBIMG   = os.path.join(os.getcwd(), "media", "keyboard.png")

file    = os.path.join(os.getcwd(), "INFOSBUTTONCODE.TXT")

#####################################################################################################
''' Class: Button Code Reference '''
#####################################################################################################
class buttoncode(xbmcgui.Window):
    def __init__(self):
        self.setCoordinateResolution(6)
        self.setKeymap()
        self.descriptionButtonCode = ""
        self.fileinfos = open(file, "w")
        print "Your button code infos"

        #self.addControl(xbmcgui.ControlImage(0,0,720,576, "background-plain.png"))

        self.addControl(xbmcgui.ControlLabel(200,63,0,0, "xbox media center", "special12", alignment=0x00000001))
        self.addControl(xbmcgui.ControlLabel(207,63,0,0, "Button Code", "special13"))

        self.PAD = xbmcgui.ControlImage(50,270,0,0, PADIMG)
        self.addControl(self.PAD)
        self.KB = xbmcgui.ControlImage(345,121,0,0, KBIMG)
        self.addControl(self.KB)
        self.DVD = xbmcgui.ControlImage(500,340,0,0, DVDIMG)
        self.addControl(self.DVD)

        self.imageFocus = xbmcgui.ControlImage(360,288,0,0, "")
        self.addControl(self.imageFocus)

        self.addControl(xbmcgui.ControlLabel(150,121,0,0, "Press Any Button\nAnd\nEnter Name For Code", alignment=0x00000002))

    def setKeymap(self):
        generalKey = KeymapGeneral()
        self.exitscripts = generalKey.EXITSCRIPTS

    def onAction(self, action):
        BUTTONCODE = action.getButtonCode()
        self.setImageFocus(BUTTONCODE)
        if self.exitscripts.has_key(BUTTONCODE):
            IDCODE = '%d : "%s"' % (BUTTONCODE, self.exitscripts[BUTTONCODE])
            self.fileinfos.write(str(IDCODE)+"\n")
            print str(IDCODE)
            self.fileinfos.close()
            xbmcgui.Dialog().ok("Infos Button Code", "Last code: %s" % str(IDCODE), "Your button code infos is saved here:", file)
            self.close()
        elif (BUTTONCODE > 0)&(BUTTONCODE < 1000000):
            keyboard = xbmc.Keyboard(self.descriptionButtonCode, "Enter name for this button code: %d" % BUTTONCODE)
            keyboard.doModal()
            if keyboard.isConfirmed():
                NAME = keyboard.getText()
                IDCODE = '%d : "%s"' % (BUTTONCODE, NAME)
                self.fileinfos.write(str(IDCODE)+"\n")
                print str(IDCODE)

    def setImageFocus(self, CODE):
        if (CODE > 61000)&(CODE < 62000):
            self.imageFocus.setPosition(360-(KBSIZE["w"]/2), 338-(KBSIZE["h"]/2))
            self.imageFocus.setHeight(KBSIZE["h"])
            self.imageFocus.setWidth(KBSIZE["w"])
            self.imageFocus.setImage(KBIMG)
            self.defaultImages(0)
            self.descriptionButtonCode = "Button Keyboard"
        elif (CODE >= 256)&(CODE <= 283):
            self.imageFocus.setPosition(360-(PADSIZE["w"]/2), 338-(PADSIZE["h"]/2))
            self.imageFocus.setHeight(PADSIZE["h"])
            self.imageFocus.setWidth(PADSIZE["w"])
            self.imageFocus.setImage(PADIMG)
            self.defaultImages(0)
            self.descriptionButtonCode = "Button Controller"
        elif (CODE > 0)&(CODE < 256):
            self.imageFocus.setPosition(360-(DVDSIZE["w"]/2), 338-(DVDSIZE["h"]/2))
            self.imageFocus.setHeight(DVDSIZE["h"])
            self.imageFocus.setWidth(DVDSIZE["w"])
            self.imageFocus.setImage(DVDIMG)
            self.defaultImages(0)
            self.descriptionButtonCode = "Button Remote"
        else:
            self.imageFocus.setImage("")
            self.defaultImages(1)
            self.descriptionButtonCode = ""

    def defaultImages(self, show):
        self.PAD.setVisible(show)
        self.DVD.setVisible(show)
        self.KB.setVisible(show)

try:
    win = buttoncode()
    win.doModal()
    del win
finally:
    xbmc.executebuiltin('XBMC.ActivateWindow(ScriptsDebugInfo)')
