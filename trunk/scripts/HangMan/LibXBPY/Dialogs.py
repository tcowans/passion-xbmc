# -*- coding: utf-8 -*-

#####################################################################################################
''' Infos: Data '''
#####################################################################################################
__author__    = '''FrostBox'''
__copyright__ = '''Copyright (c) 2006'''
__credits__   = '''Team XBMC'''
__date__      = '''25 november 2006'''
__platform__  = '''XBOX, Apps: Script for XBMC'''
__title__     = '''ContextMenu'''
__version__   = '''1.0.0'''

#####################################################################################################
''' Module: import '''
#####################################################################################################
import xbmc
import xbmcgui

#####################################################################################################
''' Function: Global '''
#####################################################################################################
DCT   = "dialog-context-top.png"
DCM   = "dialog-context-middle.png"
DCB   = "dialog-context-bottom.png"
BTNF  = "keyboard-btn-space-focus2.png"
BTNNF = "keyboard-btn-space.png"

#####################################################################################################
''' Class: ContextMenu '''
#####################################################################################################
class __ContextMenu__(xbmcgui.WindowDialog):
    def __init__(self):
        self.setCoordinateResolution(6)

        self.addControl(xbmcgui.ControlImage(245,170,235,26,DCT))
        self.img01 = xbmcgui.ControlImage(245,195,235,235,DCM)
        self.addControl(self.img01)
        self.img02 = xbmcgui.ControlImage(245,430,235,25,DCB)
        self.addControl(self.img02)

        self.list = xbmcgui.ControlList(
            267,192,200,266, font="font13", textColor="0xFFFFFFFF",
            buttonFocusTexture = BTNF, buttonTexture = BTNNF,
            imageWidth=18, imageHeight=18, itemTextXOffset=5,
            alignmentY=0x00000004, itemHeight=32, space=3)
        self.addControl(self.list)
        self.list.setPageControlVisible(0)

        self.setFocus(self.list)
        self.selection = None
        self.items = []

    def fill(self, list, thumbs):
        pos = 0
        for item in list:
            try: tbn = thumbs[pos]
            except: tbn = ""
            self.items.append(item)
            self.list.addItem(
                xbmcgui.ListItem(
                    label  = str(item),
                    label2 = "",
                    thumbnailImage = tbn
                    )
                )
            pos += 1
        if int(len(list)) <= 1:
            self.img01.setHeight(25)
            self.img02.setPosition(245,220)
        elif int(len(list)) == 2:
            self.img01.setHeight(60)
            self.img02.setPosition(245,255)
        elif int(len(list)) == 3:
            self.img01.setHeight(95)
            self.img02.setPosition(245,290)
        elif int(len(list)) == 4:
            self.img01.setHeight(130)
            self.img02.setPosition(245,325)
        elif int(len(list)) == 5:
            self.img01.setHeight(165)
            self.img02.setPosition(245,360)
        elif int(len(list)) == 6:
            self.img01.setHeight(200)
            self.img02.setPosition(245,395)
        else: pass

    def onAction(self, action):
        if (action == 10) or (action == 117):
            self.selection = None
            self.close()

    def onControl(self, control):
        if control == self.list:
            try:
                if self.list.getSelectedPosition() >= 0:
                    self.selection = self.items[self.list.getSelectedPosition()]
            except: pass 
            self.close()

#####################################################################################################
''' Function: Start ContextMenu '''
#####################################################################################################
def ContextMenu(list, thumbs=[]):
    w = None
    w = __ContextMenu__()
    w.fill(list, thumbs)
    w.doModal()
    value = w.selection
    del w
    return value

#####################################################################################################
''' Test Function: Start ContextMenu '''
#####################################################################################################
if __name__ == "__main__":
    MyList = ["I","Testings","My","Custom","ContextMenu","Ok","Cancel"]
    thumbs = ["","check-box.png","","","check-box.png","",""]
    response = ContextMenu(MyList,thumbs)
    if not response: print "Is Canceled"
    else: print response
