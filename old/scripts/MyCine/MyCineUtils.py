# -*- coding: iso-8859-1 -*-
# -------------------
# Classes utilitaires
# -------------------

import threading,urllib,os,sys,Image,xbmcgui
from MyCinedatas import *

# codes keymap
ACTION_PREVIOUS_MENU    = 10
ACTION_SELECT_ITEM      = 7
ACTION_MOVE_LEFT        = 1
ACTION_MOVE_RIGHT       = 2
ACTION_MOVE_UP          = 3
ACTION_MOVE_DOWN        = 4
ACTION_X                = 18
ACTION_B                = 9

# --------------------
class Loader(threading.Thread):
    def __init__(self,url,filePath,recipient,trigger):
        threading.Thread.__init__(self)
        self.trigger = trigger
        self.url = url
        self.recipient = recipient
        self.filePath = filePath
        
    def run(self):
        try:
            if self.filePath != None:
                if not os.path.exists(self.filePath):
                    urllib.urlretrieve(self.url,self.filePath)
                getattr(self.recipient,self.trigger)()
            else:
                self.page = urllib.urlopen(self.url).read()
                getattr(self.recipient,self.trigger)(self.page)
        except:
            print "[Loader][run] Error:", sys.exc_info()[0]


# --------------------
class ExtendedList:
    def __init__(self,w,x,y,width,height,spacing,nbItemsMax):
        self.__w = w
        self.__x = x
        self.__y = y
        self.__width = width
        self.__height = height
        self.__visibleItemMax = nbItemsMax
        self.__spacing = spacing
        self.__itemList = []
        self.selectedIndex = 0
        self.__firstIndex = 0
        self.hideInfosWhenUnselected = True

    def addItem(self,item):
        self.__itemList.append(item)
        item.createControls(self.__w,self.__width)
        #item.setVisible(False)
    
    def display(self):
        y = self.__y
        lastItemIndex = self.__firstIndex + self.__visibleItemMax
        if lastItemIndex > len(self.__itemList):
            lastItemIndex = len(self.__itemList)
        for i in range(self.__firstIndex,lastItemIndex):
            item = self.__itemList[i]
            item.setVisible(True)
            if i == self.selectedIndex:
                item.select()
            else:
                item.deselect(self.hideInfosWhenUnselected)
            item.setPosition(self.__x,y)
            y = y + item.height + self.__spacing
    
    def setVisible(self,bVisible):
        lastItemIndex = self.__firstIndex + self.__visibleItemMax
        if lastItemIndex > len(self.__itemList):
            lastItemIndex = len(self.__itemList)
        for i in range(self.__firstIndex,lastItemIndex):
            item = self.__itemList[i]
            item.setVisible(bVisible)

    def onAction(self, action):
        if action == ACTION_MOVE_DOWN:
            if self.selectedIndex < len(self.__itemList) - 1:
                previousItem = self.__itemList[self.selectedIndex]
                self.selectedIndex = self.selectedIndex + 1
                if self.selectedIndex - self.__firstIndex == self.__visibleItemMax:
                    self.itemsUp()
                nextItem = self.__itemList[self.selectedIndex]
                previousItem.deselect(self.hideInfosWhenUnselected)
                nextItem.setPosition(self.__x,previousItem.getPosition()[1] + previousItem.height + self.__spacing)
                nextItem.select()
                
        if action == ACTION_MOVE_UP:
            if self.selectedIndex > 0:
                previousItem = self.__itemList[self.selectedIndex]
                self.selectedIndex = self.selectedIndex - 1
                if self.selectedIndex == self.__firstIndex - 1:
                    self.itemsDown()
                nextItem = self.__itemList[self.selectedIndex]
                nextItem.select()
                previousItem.setPosition(self.__x,nextItem.getPosition()[1] + nextItem.height + self.__spacing)
                previousItem.deselect(self.hideInfosWhenUnselected)

    def itemsUp(self):
        self.__itemList[self.__firstIndex].setVisible(False)
        self.__firstIndex = self.__firstIndex + 1
        self.display()
        self.__itemList[self.__firstIndex + self.__visibleItemMax - 1].setVisible(True)
            
    def itemsDown(self):
        self.__itemList[self.__firstIndex + self.__visibleItemMax - 1].setVisible(False)
        self.__firstIndex = self.__firstIndex - 1
        self.display()
        self.__itemList[self.__firstIndex].setVisible(True)
            
# --------------------
class ExtendedListItem:
    __DESELECT_RATIO = 2
    HRATIO = 1
    
    def __init__(self,maxHeight):
        self.__maxHeight = maxHeight
        self.__isSelected = False
    
    def setBean(self,bean):
        self.__bean = bean
        return self.setPicture()
        
    def pictureLoaded(self):
        self.setPicture()
        self.setPictureSize()
        self.__imageCtrl.setImage(self.__bean.getPictureFilePath())
        
    def setPicture(self):
        try:
            pic = Image.open(self.__bean.getPictureFilePath())
            self.pictureWidth = pic.size[0]
            self.pictureHeight = pic.size[1]
            del pic
            if self.pictureHeight > self.__maxHeight:
                self.pictureWidth = self.__maxHeight * self.pictureWidth / self.pictureHeight
                self.pictureHeight = self.__maxHeight
            self.pictureWidth = int(self.pictureWidth / self.HRATIO)
            return True
        except:
            print "[ExtendedListItem][setPicture] Error in opening: " + self.__bean.getPictureFilePath()
            return False
            

    def createControls(self,w,width):
        self.__imageCtrl = xbmcgui.ControlImage(-720,0,self.pictureWidth,self.pictureHeight,self.__bean.getPictureFilePath())
        w.addControl(self.__imageCtrl)
        self.__titleCtrl = xbmcgui.ControlLabel(-720,0,width - self.pictureWidth,10,self.__bean.title,textColor='0xFFF2F44B')
        w.addControl(self.__titleCtrl)
        self.__textCtrl = xbmcgui.ControlTextBox(-720,0,width - self.pictureWidth,self.__maxHeight - 20,'font13','0xFFFFFFFF')
        try: # Suppression du spinControl
            sc = self.__textCtrl.getSpinControl()
            sc.setPosition(-720,0)
        except:
            pass
        w.addControl(self.__textCtrl)
        self.__textCtrl.setText(self.__bean.infos)
        self.__bottomCtrl = xbmcgui.ControlLabel(-720,0,width - self.pictureWidth,10,self.__bean.info2,textColor='0xFFAAAAAA')
        w.addControl(self.__bottomCtrl)
        self.height = self.pictureHeight
        self.__position = self.__imageCtrl.getPosition()
        
    def setPictureSize(self):
        if self.__isSelected:
            self.__imageCtrl.setWidth(self.pictureWidth)
            self.__imageCtrl.setHeight(self.pictureHeight)
        else:
            self.__imageCtrl.setWidth(self.pictureWidth / self.__DESELECT_RATIO)
            self.__imageCtrl.setHeight(self.pictureHeight / self.__DESELECT_RATIO)
        self.setPosition(self.__position[0],self.__position[1])

    def setPosition(self,x,y):
        self.__imageCtrl.setPosition(x,y)
        self.__position = self.__imageCtrl.getPosition()
        self.__titleCtrl.setPosition(x + self.__imageCtrl.getWidth() + 5,y - 5)
        self.__textCtrl.setPosition(x + self.pictureWidth + 5,y + 11)
        self.__bottomCtrl.setPosition(x + self.pictureWidth + 5,y + self.pictureHeight - 17)

    def getPosition(self):
        return self.__position

    def select(self):
        self.__isSelected = True
        self.__textCtrl.setVisible(True)
        self.__bottomCtrl.setVisible(True)
        self.setPictureSize()
        self.height = self.pictureHeight
        
    def deselect(self,hideInfosWhenUnselected):
        self.__isSelected = False
        if hideInfosWhenUnselected:
            self.__textCtrl.setVisible(False)
        self.__bottomCtrl.setVisible(False)
        self.setPictureSize()
        self.height = self.pictureHeight / self.__DESELECT_RATIO

    def setVisible(self,bVisible):
        self.__imageCtrl.setVisible(bVisible)
        self.__titleCtrl.setVisible(bVisible)
        self.__textCtrl.setVisible(bVisible)
        self.__bottomCtrl.setVisible(bVisible)
        
