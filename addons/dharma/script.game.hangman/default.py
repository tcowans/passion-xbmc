# -*- coding: utf-8 -*-

#####################################################################################################
''' Infos: Data '''
#####################################################################################################
__script__       = "HangMan"
__author__       = "Frost"
__url__          = "http://passion-xbmc.org/"
__svn_url__      = "http://passion-xbmc.googlecode.com/svn/trunk/addons/script.game.hangman/"
__credits__      = "Team XBMC, http://xbmc.org/"
__platform__     = "xbmc media center"
__date__         = "16-12-2010"
__version__      = "1.0.6"
__svn_revision__ = "$Revision$"

__hangman__   = r'''
+----------+
|          |
|          0
|        /-+-\
|       /  |  \
|          M
|         / \
|        /   \
|       ¯     ¯
+------\       /--'''

#####################################################################################################
''' Module: import '''
#####################################################################################################
import os
import re
import sys
import glob
import time
import string
import marshal
import traceback

from urllib import urlretrieve
from shutil import copy , rmtree
from random import choice , randint

import xbmc
import xbmcgui

from LibXBPY import Dialogs
from LibXBPY import pyError
from LibXBPY import utility

CWD = os.getcwd().rstrip( ";" )

#####################################################################################################
''' Function: Language '''
#####################################################################################################
def directoryWord():
    language = xbmc.getLanguage().lower()
    if os.path.exists(os.path.join(CWD, "dic", language)): found = language
    else: found = "english"
    return found

label = utility.pyLanguage().parser()
dic_lang = directoryWord()
replace_letter = "_ "

#####################################################################################################
''' Function: xpr '''
#####################################################################################################
def unpack_xpr(path, filename):
    from zipfile import ZipFile
    try:
        zip = ZipFile(filename, "r")
        namelist = zip.namelist()
        for item in namelist:
            if not item.endswith("/"):
                root, name = os.path.split(item)
                directory = os.path.normpath(os.path.join(path, root))
                if not os.path.isdir(directory): os.makedirs(directory)
                file(os.path.join(directory, name), "wb").write(zip.read(item))
        zip.close()
        del zip
    except:
        xbmcgui.Dialog().ok(label[1], label[2]+"\n"+label[3]+"\n"+label[4])

#####################################################################################################
''' Function: Skin '''
#####################################################################################################
skin          = os.path.join(CWD, "media", "Textures.xpr")
hangman       = os.path.join(CWD, "media", "Hangman.xpr")
snd           = os.path.join(CWD, "sounds", "sounds.snd")
myflag        = os.path.join(CWD, "dic", "flag.zip")
skin_cache    = os.path.join(CWD, "media", "cache")
hangman_cache = os.path.join(skin_cache, "hangman")
if not os.path.exists(hangman_cache): os.makedirs(hangman_cache)
unpack_xpr(hangman_cache, hangman)
unpack_xpr(hangman_cache, snd)
unpack_xpr(skin_cache, skin)
unpack_xpr(skin_cache, myflag)
MEDIA = skin_cache
BG0  = os.path.join(MEDIA, "black.png")
BG1  = os.path.join(MEDIA, "dialog-panel2.png")
BG2  = os.path.join(MEDIA, "sub-background-label.png")
BG3  = os.path.join(MEDIA, "keyboard-btn-backspace-focus.png")
BG4  = os.path.join(MEDIA, "keyboard-btn-backspace.png")
BG5  = os.path.join(MEDIA, "keyboard-btn-focus.png")
BG6  = os.path.join(MEDIA, "keyboard-btn.png")
BG7  = os.path.join(MEDIA, "keyboard-btn-mid-sel-focus.png")
BG8  = os.path.join(MEDIA, "keyboard-btn-mid-sel.png")
BG9  = os.path.join(MEDIA, "keyboard-btn-mid-focus.png")
BG10 = os.path.join(MEDIA, "keyboard-btn-mid.png")
BG11 = os.path.join(MEDIA, "keyboard-btn-sol-focus.png")
BG12 = os.path.join(MEDIA, "keyboard-btn-sol.png")
BG13 = os.path.join(MEDIA, "keyboard-btn-new-focus.png")
BG14 = os.path.join(MEDIA, "keyboard-btn-new.png")
BG15 = os.path.join(MEDIA, "keyboard-btn-z-focus.png")
BG16 = os.path.join(MEDIA, "keyboard-btn-z.png")
BG17 = os.path.join(MEDIA, "keyboard-btn-n-focus.png")
BG18 = os.path.join(MEDIA, "keyboard-btn-n.png")
BG19 = os.path.join(MEDIA, "keyboard-btn-space-focus.png")
BG20 = os.path.join(MEDIA, "keyboard-btn-space.png")

BG_gold   = os.path.join(hangman_cache, "goldmedal.png")
BG_silver = os.path.join(hangman_cache, "silvermedal.png")
BG_bronze = os.path.join(hangman_cache, "bronzemedal.png")

heart     = os.path.join(hangman_cache, "heart.wav")

#####################################################################################################
''' Function: Sounds '''
#####################################################################################################
glob.sounds_effect = True
def Sounds(track):
    if glob.sounds_effect: xbmc.Player().play(track)

#####################################################################################################
''' Function: Récupération d'un message au hasard '''
#####################################################################################################
def dead_message():
    deadSounds=[os.path.join(hangman_cache, "hang1.wav"),
                os.path.join(hangman_cache, "hang3.wav"),
                os.path.join(hangman_cache, "hang6.wav"),
                os.path.join(hangman_cache, "hang8.wav"),
                os.path.join(hangman_cache, "fail.wav")]
    deadlist=[label[10], label[11], label[12],
              label[13], label[14], label[15],
              label[16], label[17], label[18],
              label[19]]
    Sounds(choice(deadSounds))
    while True:
        hasard = choice(deadlist)
        if not hasard == "-": return hasard

def error_message():
    errorSounds=[os.path.join(hangman_cache, "hang5.wav"),
                 os.path.join(hangman_cache, "hang9.wav"),
                 os.path.join(hangman_cache, "hang11.wav")]
    errorlist=[label[20], label[21], label[22],
               label[23], label[24], label[25],
               label[26], label[27], label[28],
               label[29], label[30], label[31],
               label[32], label[33], label[34],
               label[35], label[36]]
    Sounds(choice(errorSounds))
    while True:
        hasard = choice(errorlist)
        if not hasard == "-": return hasard

def good_message():
    goodSounds=[os.path.join(hangman_cache, "goodjob.wav")]
    goodlist=[label[37], label[38], label[39],
              label[40], label[41], label[42],
              label[43], label[44], label[45],
              label[46], label[47], label[48],
              label[49], label[50], label[51],
              label[52], label[53], label[54]]
    Sounds(choice(goodSounds))
    while True:
        hasard = choice(goodlist)
        if not hasard == "-": return hasard

def winner():
    winSounds=[os.path.join(hangman_cache, "success.wav"),
               os.path.join(hangman_cache, "success1.wav")]
    winlist=[label[55], label[56], label[57],
             label[58], label[59]]
    Sounds(choice(winSounds))
    while True:
        hasard = choice(winlist)
        if not hasard == "-": return hasard

#####################################################################################################
''' Function: keyboard '''
#####################################################################################################
def Glob_keyboard(line, heading):
    keyboard = xbmc.Keyboard(line, heading)
    keyboard.doModal()
    if keyboard.isConfirmed(): response = keyboard.getText()
    else: response = ""
    return response

#####################################################################################################
''' Class: flag '''
#####################################################################################################
class __flag__(xbmcgui.WindowDialog):
    def __init__(self):
        self.setCoordinateResolution(6)
        self.addControl(xbmcgui.ControlImage(95,95,520,420,BG1))

        self.addControl(xbmcgui.ControlLabel(120,108,420,32,label[97],'font12','0xDDced8da'))

        self.fileList = xbmcgui.ControlList(120,140,480,335,
            font = "font12",
            imageWidth = 50,
            imageHeight = 34,
            itemTextXOffset = 5,
            itemHeight = 50)
        self.addControl(self.fileList)
        self.setFocus(self.fileList)
        self.fill()

    def fill(self):
        dirFlag = []
        dirFlag = os.listdir(os.path.join(skin_cache, "flag"))
        dirFlag.sort()
        num = 0
        for fg in dirFlag:
            num += 1
            self.fileList.addItem(
                xbmcgui.ListItem(
                    label = str(fg),
                    label2 = "",
                    thumbnailImage = os.path.join(skin_cache, "flag", fg)
                    )
                )

    def onAction(self,action):
        if action ==  10: self.close() # BACK button

    def onControl(self,control):
        if control == self.fileList:
            item  = self.fileList.getSelectedItem().getLabel()
            copy(os.path.join(skin_cache, "flag", item),
                os.path.join(CWD, "dic", dic_lang, "flag.gif"))
            self.close()

#####################################################################################################
''' Class: Hi-Scores '''
#####################################################################################################
class Hi_Scores(xbmcgui.WindowDialog):
    def __init__(self):
        self.setCoordinateResolution(6)
        self.addControl(xbmcgui.ControlImage(95,95,520,420,BG1))

        self.addControl(xbmcgui.ControlLabel(120,108,420,32,label[6],'font12','0xDDced8da'))

        self.fileList = xbmcgui.ControlList(120,140,480,370,
            imageWidth = 16,
            imageHeight = 16,
            itemTextXOffset = 3,
            itemHeight = 32)
        self.addControl(self.fileList)
        self.setFocus(self.fileList)
        self.fill()

    def fill(self):
        lines = []
        f = open(os.path.join(CWD,"HiScores.his"),"rb")
        Scores = f.read()
        f.close()
        lines = Scores.split("\r\n")
        #print Scores , str(lines)
        lines.sort() # trie la liste
        lines.reverse() # mets la liste en décroissant
        num = 0
        for line in lines:
            line = line.split(" ; ")
            num = num + 1
            if   num == 1: thumb = BG_gold
            elif num == 2: thumb = BG_silver
            elif num == 3: thumb = BG_bronze
            else: thumb = ""
            self.fileList.addItem(
                xbmcgui.ListItem(
                    label = str(num)+". "+line[1]+", "+label[8]+" "+line[2]+", "+line[3]+", "+line[4],
                    label2 = line[0],
                    thumbnailImage = thumb
                    )
                )
            if num == 10: break

    def onAction(self,action):
        if action ==  10: self.close() # BACK button

    def onControl(self,control):
        if control == self.fileList:
            glob.item  = self.fileList.getSelectedItem().getLabel()
            glob.item2 = self.fileList.getSelectedItem().getLabel2()
            glob.pos = self.fileList.getSelectedPosition()
            si = Scores_infos()
            si.doModal()
            del si

class Scores_infos(xbmcgui.WindowDialog):
    def __init__(self):
        self.setCoordinateResolution(6)
        self.addControl(xbmcgui.ControlImage(95,95,520,420,BG1))
        if   glob.pos+1 == 1: thumb = BG_gold
        elif glob.pos+1 == 2: thumb = BG_silver
        elif glob.pos+1 == 3: thumb = BG_bronze
        else: thumb = ""
        self.addControl(xbmcgui.ControlImage(565,110,33,33,thumb))
        self.addControl(xbmcgui.ControlLabel(120,108,420,32,label[100],'font12','0xDDced8da'))
        self.label1 = str(glob.item).split(", ")
        self.label2 = self.label1[0].split(". ")
        self.addControl(xbmcgui.ControlLabel(130,150,420,32,label[101]+" "+str(glob.pos+1),"font12"))
        self.addControl(xbmcgui.ControlLabel(130,180,420,32,label[102]+" "+self.label2[1],"font12"))
        self.addControl(xbmcgui.ControlLabel(130,210,420,32,label[103]+" "+str(glob.item2),"font12"))
        self.addControl(xbmcgui.ControlLabel(130,240,420,32,self.label1[1],"font12"))
        self.addControl(xbmcgui.ControlLabel(130,270,420,32,label[104]+" "+self.label1[3],"font12"))
        self.addControl(xbmcgui.ControlLabel(130,300,420,32,label[105]+" "+self.label1[2],"font12"))

    def onAction(self,action):
        if action ==  10: self.close() # BACK button

#####################################################################################################
''' Function: Timer '''
#####################################################################################################
glob.play_start = ""
glob.play_end   = ""
glob.diff_time  = ""
def play_timed(on_off=None):
    now = time.localtime(time.time())
    year, month, day, hour, minute, second, weekday, yearday, daylight = now
    h = "%02d" % (hour)
    m = "%02d" % (minute)
    s = "%02d" % (second)
    if on_off: glob.play_start = h+m+s
    if not on_off:
        glob.play_end = h+m+s
        if not glob.play_start == "":
            time_diff = str(eval(str(float(glob.play_end))+"-"+str(float(glob.play_start))))
            if float(time_diff) > 60:
                minutes = str(round(float(time_diff)/60.0,2)).split(".")
                if float(minutes[1]) > 60:
                    min = str(round(float(minutes[1])-60.0,2)).split(".")
                    glob.diff_time = str(round(float(minutes[0])+1+float("0."+min[1]),2))+" Min."
                else: glob.diff_time = str(minutes[0]+" Min. "+minutes[1]+" Sec. ")
            else: glob.diff_time = time_diff+" Sec."

#####################################################################################################
''' Class: Mots '''
#####################################################################################################
all_letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
class Word:
    def __init__(self, s):
        if type (s)!=type (""):
            TypeError, "oops!"
        self.s = string.upper(s)
        self.a = [0]*len(s)
        for i in range(0, len(self.s)):
            if self.s[i] not in all_letters: self.a[i] = 1
        self.g = ""

    def __str__(self):
        z = ''
        for i in range (0, len(self.s)):
            if self.a[i] == 0: z = z + replace_letter
            else: z = z + self.s[i] + ' '
        return z

    def guess(self, g):
        n = 0
        self.g = self.g + g
        for i in range (0, len(self.s)):
            if self.s[i] == g:
                self.a[i] = 1
                n = n + 1
        return n

    def is_completed(self): return not 0 in self.a

#####################################################################################################
''' Class: Principal '''
#####################################################################################################
class __HangMan__(xbmcgui.WindowDialog):
    def __init__(self):
        self.setCoordinateResolution(6)

        self.tmp_file = os.path.join(CWD,"HangMan.log")
        self.Load_tmp()
        self.default_entry()
        self.align = 0x00000002+0x00000004

        self.addControl(xbmcgui.ControlImage(0,  0,720,576,BG0))
        self.addControl(xbmcgui.ControlImage(95,95,520,420,BG1))
        self.addControl(xbmcgui.ControlImage(0,500,800,42,BG2))

        self.Heading = xbmcgui.ControlLabel(120,108,420,32,__script__,'font12','0xDDced8da')
        self.addControl(self.Heading)

        self.hidden_letter = xbmcgui.ControlLabel(0,325,720,18,"","font12",alignment=0x00000002)
        self.addControl(self.hidden_letter)

        self.info_Score = xbmcgui.ControlLabel(540,463,720,18,label[9]+" 0","font12","0xffD2FF00",alignment=0x00000001)
        self.addControl(self.info_Score)

        self.info_error = xbmcgui.ControlLabel(180,463,720,18,"","font12","0xFFFF9600")
        self.addControl(self.info_error)
        self.Line_mess = xbmcgui.ControlLabel(0,503,720,18,label[5],"font12",'0xDDced8da',alignment=0x00000002)
        self.addControl(self.Line_mess)

        self.Line_hi_score = xbmcgui.ControlLabel(600,108,420,32,label[7]+" "+str(self.level["hi_score"]),'font12',"0xffD2FF00",alignment=0x00000001)
        self.addControl(self.Line_hi_score)

        if self.level["game"] == "Normal.wrd": self.label_hard = label[60]
        else: self.label_hard = label[61]
        self.tmp_word = os.path.join(CWD, "dic", dic_lang, self.level["game"])
        self.default_(self.tmp_word)
        self.load_words(self.tmp_word)

        self.hangman = xbmcgui.ControlImage(255,123,250,222,"")
        self.addControl(self.hangman)
        try: my_flag = os.path.join(CWD, "dic", dic_lang, "flag.gif")
        except: my_flag = ""
        self.flag = xbmcgui.ControlImage(398,283,30,30,my_flag)
        self.addControl(self.flag)
        self.set_hangman(self.error)

        self.btn_A = xbmcgui.ControlButton(
            165,400,30,30,"A",font="font12",
            focusTexture=BG5,
            noFocusTexture=BG6,
            alignment=self.align)
        self.addControl(self.btn_A)

        self.btn_B = xbmcgui.ControlButton(
            195,400,30,30,"B",font="font12",
            focusTexture=BG5,
            noFocusTexture=BG6,
            alignment=self.align)
        self.addControl(self.btn_B)

        self.btn_C = xbmcgui.ControlButton(
            225,400,30,30,"C",font="font12",
            focusTexture=BG5,
            noFocusTexture=BG6,
            alignment=self.align)
        self.addControl(self.btn_C)

        self.btn_D = xbmcgui.ControlButton(
            255,400,30,30,"D",font="font12",
            focusTexture=BG5,
            noFocusTexture=BG6,
            alignment=self.align)
        self.addControl(self.btn_D)

        self.btn_E = xbmcgui.ControlButton(
            285,400,30,30,"E",font="font12",
            focusTexture=BG5,
            noFocusTexture=BG6,
            alignment=self.align)
        self.addControl(self.btn_E)

        self.btn_F = xbmcgui.ControlButton(
            315,400,30,30,"F",font="font12",
            focusTexture=BG5,
            noFocusTexture=BG6,
            alignment=self.align)
        self.addControl(self.btn_F)

        self.btn_G = xbmcgui.ControlButton(
            345,400,30,30,"G",font="font12",
            focusTexture=BG5,
            noFocusTexture=BG6,
            alignment=self.align)
        self.addControl(self.btn_G)

        self.btn_H = xbmcgui.ControlButton(
            375,400,30,30,"H",font="font12",
            focusTexture=BG5,
            noFocusTexture=BG6,
            alignment=self.align)
        self.addControl(self.btn_H)

        self.btn_I = xbmcgui.ControlButton(
            405,400,30,30,"I",font="font12",
            focusTexture=BG5,
            noFocusTexture=BG6,
            alignment=self.align)
        self.addControl(self.btn_I)

        self.btn_J = xbmcgui.ControlButton(
            435,400,30,30,"J",font="font12",
            focusTexture=BG5,
            noFocusTexture=BG6,
            alignment=self.align)
        self.addControl(self.btn_J)

        self.btn_K = xbmcgui.ControlButton(
            465,400,30,30,"K",font="font12",
            focusTexture=BG5,
            noFocusTexture=BG6,
            alignment=self.align)
        self.addControl(self.btn_K)

        self.btn_L = xbmcgui.ControlButton(
            495,400,30,30,"L",font="font12",
            focusTexture=BG5,
            noFocusTexture=BG6,
            alignment=self.align)
        self.addControl(self.btn_L)

        self.btn_M = xbmcgui.ControlButton(
            525,400,30,30,"M",font="font12",
            focusTexture=BG5,
            noFocusTexture=BG6,
            alignment=self.align)
        self.addControl(self.btn_M)

        self.btn_N = xbmcgui.ControlButton(
            165,430,30,30,"N",font="font12",
            focusTexture=BG17,
            noFocusTexture=BG18,
            alignment=self.align)
        self.addControl(self.btn_N)

        self.btn_O = xbmcgui.ControlButton(
            195,430,30,30,"O",font="font12",
            focusTexture=BG5,
            noFocusTexture=BG6,
            alignment=self.align)
        self.addControl(self.btn_O)

        self.btn_P = xbmcgui.ControlButton(
            225,430,30,30,"P",font="font12",
            focusTexture=BG5,
            noFocusTexture=BG6,
            alignment=self.align)
        self.addControl(self.btn_P)

        self.btn_Q = xbmcgui.ControlButton(
            255,430,30,30,"Q",font="font12",
            focusTexture=BG5,
            noFocusTexture=BG6,
            alignment=self.align)
        self.addControl(self.btn_Q)

        self.btn_R = xbmcgui.ControlButton(
            285,430,30,30,"R",font="font12",
            focusTexture=BG5,
            noFocusTexture=BG6,
            alignment=self.align)
        self.addControl(self.btn_R)

        self.btn_S = xbmcgui.ControlButton(
            315,430,30,30,"S",font="font12",
            focusTexture=BG5,
            noFocusTexture=BG6,
            alignment=self.align)
        self.addControl(self.btn_S)

        self.btn_T = xbmcgui.ControlButton(
            345,430,30,30,"T",font="font12",
            focusTexture=BG5,
            noFocusTexture=BG6,
            alignment=self.align)
        self.addControl(self.btn_T)

        self.btn_U = xbmcgui.ControlButton(
            375,430,30,30,"U",font="font12",
            focusTexture=BG5,
            noFocusTexture=BG6,
            alignment=self.align)
        self.addControl(self.btn_U)

        self.btn_V = xbmcgui.ControlButton(
            405,430,30,30,"V",font="font12",
            focusTexture=BG5,
            noFocusTexture=BG6,
            alignment=self.align)
        self.addControl(self.btn_V)

        self.btn_W = xbmcgui.ControlButton(
            435,430,30,30,"W",font="font12",
            focusTexture=BG5,
            noFocusTexture=BG6,
            alignment=self.align)
        self.addControl(self.btn_W)

        self.btn_X = xbmcgui.ControlButton(
            465,430,30,30,"X",font="font12",
            focusTexture=BG5,
            noFocusTexture=BG6,
            alignment=self.align)
        self.addControl(self.btn_X)

        self.btn_Y = xbmcgui.ControlButton(
            495,430,30,30,"Y",font="font12",
            focusTexture=BG5,
            noFocusTexture=BG6,
            alignment=self.align)
        self.addControl(self.btn_Y)

        self.btn_Z = xbmcgui.ControlButton(
            525,430,30,30,"Z",font="font12",
            focusTexture=BG15,
            noFocusTexture=BG16,
            alignment=self.align)
        self.addControl(self.btn_Z)

        self.btn_indice = xbmcgui.ControlButton(
            255,370,210,30,label[62],font="font12",
            focusTexture=BG19,
            noFocusTexture=BG20,
            alignment=self.align)
        self.addControl(self.btn_indice)

        self.btn_new = xbmcgui.ControlButton(
            165,370,90,30,label[64],font="font12",
            focusTexture=BG13,
            noFocusTexture=BG14,
            alignment=self.align)
        self.addControl(self.btn_new)

        self.btn_solution = xbmcgui.ControlButton(
            465,370,90,30,label[63],font="font12",
            focusTexture=BG11,
            noFocusTexture=BG12,
            alignment=self.align)
        self.addControl(self.btn_solution)

        self.btn_hi_scores = xbmcgui.ControlButton(
            120,145,110,32,label[6],font="font12",
            focusTexture=BG3,
            noFocusTexture=BG4,
            alignment=self.align)
        self.addControl(self.btn_hi_scores)

        self.btn_sounds = xbmcgui.ControlButton(
            120,180,110,32,label[65],font="font12",
            focusTexture=BG3,
            noFocusTexture=BG4,
            alignment=self.align)
        self.addControl(self.btn_sounds)

        self.btn_flag = xbmcgui.ControlButton(
            120,215,110,32,label[96],font="font12",
            focusTexture=BG3,
            noFocusTexture=BG4,
            alignment=self.align)
        self.addControl(self.btn_flag)

        self.btn_hard = xbmcgui.ControlButton(
            120,250,110,32,self.label_hard,font="font12",
            focusTexture=BG3,
            noFocusTexture=BG4,
            alignment=self.align)
        self.addControl(self.btn_hard)

        self.btn_dic = xbmcgui.ControlButton(
            120,285,110,32,label[92],font="font12",
            focusTexture=BG3,
            noFocusTexture=BG4,
            alignment=self.align)
        self.addControl(self.btn_dic)

        self.btn_quit = xbmcgui.ControlButton(
            120,320,110,32,label[67],font="font12",
            focusTexture=BG3,
            noFocusTexture=BG4,
            alignment=self.align)
        self.addControl(self.btn_quit)

        self.btn_A.controlUp(self.btn_new)
        self.btn_A.controlLeft(self.btn_M)
        self.btn_A.controlRight(self.btn_B)
        self.btn_A.controlDown(self.btn_N)

        self.btn_B.controlUp(self.btn_new)
        self.btn_B.controlLeft(self.btn_A)
        self.btn_B.controlRight(self.btn_C)
        self.btn_B.controlDown(self.btn_O)

        self.btn_C.controlUp(self.btn_new)
        self.btn_C.controlLeft(self.btn_B)
        self.btn_C.controlRight(self.btn_D)
        self.btn_C.controlDown(self.btn_P)

        self.btn_D.controlUp(self.btn_indice)
        self.btn_D.controlLeft(self.btn_C)
        self.btn_D.controlRight(self.btn_E)
        self.btn_D.controlDown(self.btn_Q)

        self.btn_E.controlUp(self.btn_indice)
        self.btn_E.controlLeft(self.btn_D)
        self.btn_E.controlRight(self.btn_F)
        self.btn_E.controlDown(self.btn_R)

        self.btn_F.controlUp(self.btn_indice)
        self.btn_F.controlLeft(self.btn_E)
        self.btn_F.controlRight(self.btn_G)
        self.btn_F.controlDown(self.btn_S)

        self.btn_G.controlUp(self.btn_indice)
        self.btn_G.controlLeft(self.btn_F)
        self.btn_G.controlRight(self.btn_H)
        self.btn_G.controlDown(self.btn_T)

        self.btn_H.controlUp(self.btn_indice)
        self.btn_H.controlLeft(self.btn_G)
        self.btn_H.controlRight(self.btn_I)
        self.btn_H.controlDown(self.btn_U)

        self.btn_I.controlUp(self.btn_indice)
        self.btn_I.controlLeft(self.btn_H)
        self.btn_I.controlRight(self.btn_J)
        self.btn_I.controlDown(self.btn_V)

        self.btn_J.controlUp(self.btn_indice)
        self.btn_J.controlLeft(self.btn_I)
        self.btn_J.controlRight(self.btn_K)
        self.btn_J.controlDown(self.btn_W)

        self.btn_K.controlUp(self.btn_solution)
        self.btn_K.controlLeft(self.btn_J)
        self.btn_K.controlRight(self.btn_L)
        self.btn_K.controlDown(self.btn_X)

        self.btn_L.controlUp(self.btn_solution)
        self.btn_L.controlLeft(self.btn_K)
        self.btn_L.controlRight(self.btn_M)
        self.btn_L.controlDown(self.btn_Y)

        self.btn_M.controlUp(self.btn_solution)
        self.btn_M.controlLeft(self.btn_L)
        self.btn_M.controlRight(self.btn_A)
        self.btn_M.controlDown(self.btn_Z)

        self.btn_N.controlUp(self.btn_A)
        self.btn_N.controlLeft(self.btn_Z)
        self.btn_N.controlRight(self.btn_O)
        self.btn_N.controlDown(self.btn_A)

        self.btn_O.controlUp(self.btn_B)
        self.btn_O.controlLeft(self.btn_N)
        self.btn_O.controlRight(self.btn_P)
        self.btn_O.controlDown(self.btn_B)

        self.btn_P.controlUp(self.btn_C)
        self.btn_P.controlLeft(self.btn_O)
        self.btn_P.controlRight(self.btn_Q)
        self.btn_P.controlDown(self.btn_C)

        self.btn_Q.controlUp(self.btn_D)
        self.btn_Q.controlLeft(self.btn_P)
        self.btn_Q.controlRight(self.btn_R)
        self.btn_Q.controlDown(self.btn_D)

        self.btn_R.controlUp(self.btn_E)
        self.btn_R.controlLeft(self.btn_Q)
        self.btn_R.controlRight(self.btn_S)
        self.btn_R.controlDown(self.btn_E)

        self.btn_S.controlUp(self.btn_F)
        self.btn_S.controlLeft(self.btn_R)
        self.btn_S.controlRight(self.btn_T)
        self.btn_S.controlDown(self.btn_F)

        self.btn_T.controlUp(self.btn_G)
        self.btn_T.controlLeft(self.btn_S)
        self.btn_T.controlRight(self.btn_U)
        self.btn_T.controlDown(self.btn_G)

        self.btn_U.controlUp(self.btn_H)
        self.btn_U.controlLeft(self.btn_T)
        self.btn_U.controlRight(self.btn_V)
        self.btn_U.controlDown(self.btn_indice)

        self.btn_V.controlUp(self.btn_I)
        self.btn_V.controlLeft(self.btn_U)
        self.btn_V.controlRight(self.btn_W)
        self.btn_V.controlDown(self.btn_indice)

        self.btn_W.controlUp(self.btn_J)
        self.btn_W.controlLeft(self.btn_V)
        self.btn_W.controlRight(self.btn_X)
        self.btn_W.controlDown(self.btn_indice)

        self.btn_X.controlUp(self.btn_K)
        self.btn_X.controlLeft(self.btn_W)
        self.btn_X.controlRight(self.btn_Y)
        self.btn_X.controlDown(self.btn_solution)

        self.btn_Y.controlUp(self.btn_L)
        self.btn_Y.controlLeft(self.btn_X)
        self.btn_Y.controlRight(self.btn_Z)
        self.btn_Y.controlDown(self.btn_solution)

        self.btn_Z.controlUp(self.btn_M)
        self.btn_Z.controlLeft(self.btn_Y)
        self.btn_Z.controlRight(self.btn_N)
        self.btn_Z.controlDown(self.btn_solution)

        self.btn_new.controlUp(self.btn_quit)
        self.btn_new.controlLeft(self.btn_solution)
        self.btn_new.controlRight(self.btn_indice)
        self.btn_new.controlDown(self.btn_B)

        self.btn_indice.controlUp(self.btn_quit)
        self.btn_indice.controlLeft(self.btn_new)
        self.btn_indice.controlRight(self.btn_solution)
        self.btn_indice.controlDown(self.btn_G)

        self.btn_solution.controlUp(self.btn_quit)
        self.btn_solution.controlLeft(self.btn_indice)
        self.btn_solution.controlRight(self.btn_new)
        self.btn_solution.controlDown(self.btn_L)

        self.btn_hi_scores.controlUp(self.btn_new)
        self.btn_hi_scores.controlLeft(self.btn_solution)
        self.btn_hi_scores.controlRight(self.btn_indice)
        self.btn_hi_scores.controlDown(self.btn_sounds)

        self.btn_sounds.controlUp(self.btn_hi_scores)
        self.btn_sounds.controlLeft(self.btn_solution)
        self.btn_sounds.controlRight(self.btn_indice)
        self.btn_sounds.controlDown(self.btn_flag)

        self.btn_flag.controlUp(self.btn_sounds)
        self.btn_flag.controlLeft(self.btn_solution)
        self.btn_flag.controlRight(self.btn_indice)
        self.btn_flag.controlDown(self.btn_hard)

        self.btn_hard.controlUp(self.btn_flag)
        self.btn_hard.controlLeft(self.btn_solution)
        self.btn_hard.controlRight(self.btn_indice)
        self.btn_hard.controlDown(self.btn_dic)

        self.btn_dic.controlUp(self.btn_hard)
        self.btn_dic.controlLeft(self.btn_solution)
        self.btn_dic.controlRight(self.btn_indice)
        self.btn_dic.controlDown(self.btn_quit)

        self.btn_quit.controlUp(self.btn_dic)
        self.btn_quit.controlLeft(self.btn_solution)
        self.btn_quit.controlRight(self.btn_indice)
        self.btn_quit.controlDown(self.btn_new)

        self.setFocus(self.btn_G)

    def default_entry(self):
        #play_timed(False)
        self.error        = 0
        self.solution     = ""
        self.indice       = ""
        self.is_dead      = False
        self.letters      = [] # Liste des lettres jouées
        play_timed(True)

    def set_hangman(self, lucky):
        if lucky == 5: xbmc.playSFX(heart)
        self.hangman.setImage(hangman_cache+"\\index_"+str(lucky)+".png")
        self.info_error.setLabel(label[68]+" "+str(lucky)+" / 6")
        if lucky == 0: self.flag.setPosition(398,283)
        elif lucky == 6: self.flag.setPosition(438,283)

    def onAction(self, action):
        if   action ==   9: self.Clear_entry()       # B button
        elif action ==  10: self.Remove_skin_cache() # BACK button
        elif action ==  18: self.Set_response()      # X button
        elif action ==  34: self.Get_indice()        # Y button
        elif action == 117: self.Set_game_level()    # White button

    def onControl(self, control):
        if control == self.btn_A:
            if not self.is_dead: self.btn_A.setEnabled(False)
            self.Get_value("A")
        elif control == self.btn_B:
            if not self.is_dead: self.btn_B.setEnabled(False)
            self.Get_value("B")
        elif control == self.btn_C:
            if not self.is_dead: self.btn_C.setEnabled(False)
            self.Get_value("C")
        elif control == self.btn_D:
            if not self.is_dead: self.btn_D.setEnabled(False)
            self.Get_value("D")
        elif control == self.btn_E:
            if not self.is_dead: self.btn_E.setEnabled(False)
            self.Get_value("E")
        elif control == self.btn_F:
            if not self.is_dead: self.btn_F.setEnabled(False)
            self.Get_value("F")
        elif control == self.btn_G:
            if not self.is_dead: self.btn_G.setEnabled(False)
            self.Get_value("G")
        elif control == self.btn_H:
            if not self.is_dead: self.btn_H.setEnabled(False)
            self.Get_value("H")
        elif control == self.btn_I:
            if not self.is_dead: self.btn_I.setEnabled(False)
            self.Get_value("I")
        elif control == self.btn_J:
            if not self.is_dead: self.btn_J.setEnabled(False)
            self.Get_value("J")
        elif control == self.btn_K:
            if not self.is_dead: self.btn_K.setEnabled(False)
            self.Get_value("K")
        elif control == self.btn_L:
            if not self.is_dead: self.btn_L.setEnabled(False)
            self.Get_value("L")
        elif control == self.btn_M:
            if not self.is_dead: self.btn_M.setEnabled(False)
            self.Get_value("M")
        elif control == self.btn_N:
            if not self.is_dead: self.btn_N.setEnabled(False)
            self.Get_value("N")
        elif control == self.btn_O:
            if not self.is_dead: self.btn_O.setEnabled(False)
            self.Get_value("O")
        elif control == self.btn_P:
            if not self.is_dead: self.btn_P.setEnabled(False)
            self.Get_value("P")
        elif control == self.btn_Q:
            if not self.is_dead: self.btn_Q.setEnabled(False)
            self.Get_value("Q")
        elif control == self.btn_R:
            if not self.is_dead: self.btn_R.setEnabled(False)
            self.Get_value("R")
        elif control == self.btn_S:
            if not self.is_dead: self.btn_S.setEnabled(False)
            self.Get_value("S")
        elif control == self.btn_T:
            if not self.is_dead: self.btn_T.setEnabled(False)
            self.Get_value("T")
        elif control == self.btn_U:
            if not self.is_dead: self.btn_U.setEnabled(False)
            self.Get_value("U")
        elif control == self.btn_V:
            if not self.is_dead: self.btn_V.setEnabled(False)
            self.Get_value("V")
        elif control == self.btn_W:
            if not self.is_dead: self.btn_W.setEnabled(False)
            self.Get_value("W")
        elif control == self.btn_X:
            if not self.is_dead: self.btn_X.setEnabled(False)
            self.Get_value("X")
        elif control == self.btn_Y:
            if not self.is_dead: self.btn_Y.setEnabled(False)
            self.Get_value("Y")
        elif control == self.btn_Z:
            if not self.is_dead: self.btn_Z.setEnabled(False)
            self.Get_value("Z")
        elif control == self.btn_indice:
            try: self.Get_indice()
            except: pyError.printAndLog_LastError()
        elif control == self.btn_solution: self.Set_response()
        elif control == self.btn_flag:
            self.Line_mess.setLabel(__script__+__version__)
            try:
                fg = __flag__()
                fg.doModal()
                del fg
            except: pyError.printAndLog_LastError()
            self.flag.setImage("")
            self.flag.setImage(os.path.join(CWD, "dic", dic_lang, "flag.gif"))
        elif control == self.btn_hard:      self.Set_game_level()
        elif control == self.btn_hi_scores: self.goHi_scores()
        elif control == self.btn_sounds:
            if glob.sounds_effect:
                glob.sounds_effect = False
                self.btn_sounds.setLabel(label[66])
            else:
                glob.sounds_effect = True
                self.btn_sounds.setLabel(label[65])
        elif control == self.btn_quit: self.Remove_skin_cache()
        elif control == self.btn_new:  self.Clear_entry()
        elif control == self.btn_dic:
            tumbs = []
            list  = os.listdir(os.path.join(CWD, "dic"))
            ignore = ["flag.zip","Edit for your lang!"]
            try:
                for rm in ignore:
                    if rm in list: list.remove(rm)
            except: pass
            for dic in list:
                tbn = os.path.join(CWD, "dic", dic, "flag.gif")
                tumbs.append(tbn)
            response = Dialogs.ContextMenu(list, tumbs)
            if not response is None:
                if not response in ignore:
                    self.tmp_word = os.path.join(CWD, "dic", response, self.level["game"])
                    self.flag.setImage(os.path.join(CWD, "dic", response, "flag.gif"))
                    self.default_(self.tmp_word)
                    self.Clear_entry()
        else: pass

    def goHi_scores(self):
        self.not_hs_exists()
        self.Line_mess.setLabel(__script__+__version__)
        hs = Hi_Scores()
        hs.doModal()
        del hs

    def default_(self, dic_path):
        self.words = []
        f = open(dic_path,"r")
        for lines in f.readlines():
            self.words.append(lines)
        f.close()
        #print str(len(self.words))
        self.already_done = []
        self.score        = 0
        self.toGain       = 0

    def load_words(self, dic_path):
        try:
            if len(self.words) == len(self.already_done):
                xbmcgui.Dialog().ok(__script__+__version__,label[69])
            r = randint(0, len(self.words)-1)
            for r in self.already_done:
                if len(self.already_done) > len(self.words)/2:
                    r = (r + 1) % len(self.words)
                else: r = randint(0, len(self.words)-1)
            self.already_done.append(r)
            w = self.words[r]
            if "\n" in w: w = w.replace("\n","")
            if "\r" in w: w = w.replace("\r","")
            self.word = Word(w.split(" ; ")[0])
            self.indice = w.split(" ; ")[1]
            self.hidden_letter.setLabel(str(self.word))
            #xbmcgui.Dialog().ok(__script__+__version__,label[85]+" "+str(self.indice)+"\n"+label[70])
            #print str(self.word.s)
        except:
            xbmcgui.Dialog().ok(__script__+__version__,label[71]+"\n%s.\n%s" % (dic_path, label[72]))

    def Get_value(self, letter):
        info_mess = ""
        if letter in self.letters:
            xbmcgui.Dialog().ok(__script__+__version__,label[73]+" %s " % letter+label[74]+"\n"+label[75])
            return
        else:
            self.letters.append(letter)
            self.letters.sort()
        if self.is_dead:
            self.toGain = self.toGain - 1
            if xbmcgui.Dialog().yesno(__script__+__version__,label[76]+"\n"+label[77]+"\n"+label[78]):
                self.Clear_entry()
                return
            else: self.Remove_skin_cache()
        if not letter in str(self.word.s): # self.word.s = mot caché
            self.error = self.error+1
            if self.error == 6:
                info_mess = dead_message()
                self.Set_scrore()
                self.hidden_letter.setLabel(str(self.word.s))
                self.setFocus(self.btn_new)
            else: info_mess = error_message()
            self.set_hangman(self.error)
        else:
            if not self.is_dead: #if not self.error > 6:
                if self.word.guess(letter):
                    info_mess = good_message()
                    self.hidden_letter.setLabel(str(self.word))
        if self.word.is_completed():
            if not self.is_dead: #if not self.error > 6:
                self.Set_scrore()
                self.toGain = self.toGain + 1
                info_mess = winner()
                self.setFocus(self.btn_new)
                xbmcgui.Dialog().ok(__script__+__version__,label[79]+"\n"+label[80]+" %s " % str(len(self.letters))+label[81]+"\n"+label[82]+" "+str(self.score))
        self.Line_mess.setLabel(info_mess)
        if self.error == 5: xbmc.playSFX(heart)

    def Set_scrore(self):
        if   self.error == 0: self.score = self.score + 100
        elif self.error == 1: self.score = self.score + 75
        elif self.error == 2: self.score = self.score + 50
        elif self.error == 3: self.score = self.score + 25
        elif self.error == 4: self.score = self.score + 15
        elif self.error == 5: self.score = self.score + 10
        elif self.error == 6: self.score = self.score - 50
        self.is_dead = True # REAL DEAD OR FAKE DEAD, added win game
        self.info_Score.setLabel(label[9]+" "+str(self.score))
        if self.score > self.level["hi_score"]:
            # Le Hi-Score a été brisé...
            self.level["hi_score"] = self.score
            self.Line_hi_score.setLabel(label[7]+" "+str(self.level["hi_score"]))
            self.Save_tmp()

    def Get_indice(self, show=True):
        if not self.word.is_completed():
            if self.error == 5:
                if xbmcgui.Dialog().yesno(__script__+__version__,label[83]+"\n"+label[84]):
                    self.hidden_letter.setLabel(str(self.word.s))
                    show = True
                else: show = False
            elif self.error == 6: show = False
            if show:
                self.error = self.error + 1
                self.set_hangman(self.error)
                try: uLabel = unicode(str(self.indice),"utf-8")
                except UnicodeError: uLabel = label[95]
                self.btn_indice.setLabel(uLabel)
                self.Line_mess.setLabel(error_message())
                if self.error == 6:
                    self.Set_scrore()
                    self.Line_mess.setLabel(dead_message())

    def Set_response(self):
        if not self.is_dead:
            self.error = 6
            dead_message()
            self.Set_scrore()
            self.set_hangman(self.error)
            self.hidden_letter.setLabel(str(self.word.s))
            self.Line_mess.setLabel(label[86])

    def Clear_entry(self):
        self.default_entry()
        self.show_Control()
        self.set_hangman(self.error)
        self.btn_indice.setLabel(label[62])
        self.hidden_letter.setLabel(self.solution)
        self.Line_mess.setLabel(label[5])
        self.load_words(self.tmp_word)
        self.setFocus(self.btn_G)

    def Set_game_level(self):
        if self.level["game"] == "Normal.wrd":
            self.level["game"] = "Hard.wrd"
            self.tmp_word = os.path.join(CWD, "dic", dic_lang, "Hard.wrd")
            setlabel = label[61]
        else:
            self.level["game"] = "Normal.wrd"
            self.tmp_word = os.path.join(CWD, "dic", dic_lang, "Normal.wrd")
            setlabel = label[60]
        self.Save_tmp()
        self.default_(self.tmp_word)
        self.Clear_entry()
        self.btn_hard.setLabel(setlabel)

    def Load_tmp(self):
        test = {"game":"Normal.wrd", "hi_score":900}
        self.level = {}
        if os.path.exists(self.tmp_file):
            f = open(self.tmp_file,"rb")
            self.level = marshal.load(f)
            f.close()
        for k in test.keys():
            if not self.level.has_key(k): self.level[k] = test[k]

    def Save_tmp(self):
        f = open(self.tmp_file,"wb")
        marshal.dump(self.level,f)
        f.close()

    def Remove_skin_cache(self):
        if not self.score == 0 and not self.toGain == 0:
            if xbmcgui.Dialog().yesno(__script__+__version__,label[87]+" %s ?" % str(self.score)):
                response = Glob_keyboard("", label[89])
                play_timed(False)
                if response == "": self.not_hs_exists("HangMan")
                else: self.not_hs_exists(response)
                self.goHi_scores()
        try: rmtree(skin_cache)
        except: pass
        play_timed(False)
        self.close()

    def not_hs_exists(self, response=None):
        file = os.path.join(CWD,"HiScores.his")
        HS1  = "900 ; HangMan ; 9 ; Normal ; 9 Min. 0 Sec.\n"
        HS2  = "700 ; HangMan ; 7 ; Normal ; 7 Min. 0 Sec.\n"
        HS3  = "500 ; HangMan ; 5 ; Normal ; 5 Min. 0 Sec.\n"
        HS4  = "0 ; Frost ; 0 ; Normal ; 0 Min. 0 Sec."
        if not os.path.exists(file):
            xbmcgui.DialogProgress().create(__script__+label[90]+" "+label[6],label[91])
            xbmcgui.DialogProgress().update(0)
            try:
                urlretrieve(
                    "http://frost.ueuo.com/xbmc/scripts/HangMan/Online_HiScores.his",
                    file, reporthook=self.hook_func)
            except:
                f = open(file,"a")
                f.write(HS1+HS2+HS3+HS4)
                f.close()
            xbmcgui.DialogProgress().close()
        if not response is None:
            f = open(file,"a")
            f.write("\n"+str(self.score)+" ; "+str(response)+" ; "+str(self.toGain)+" ; %s" % self.label_hard+" ; "+glob.diff_time)
            f.close()

    def hook_func(self,cpt_blk,taille_blk,total_taille):
        updt_val = int((cpt_blk*taille_blk)*100.0/total_taille)
        if updt_val < 100:
            for pct in range(100+1):
                xbmcgui.DialogProgress().update(int(pct))
                time.sleep(0.01)
        else: xbmcgui.DialogProgress().update(updt_val)

    def show_Control(self, show=True):
        self.btn_A.setEnabled(show)
        self.btn_B.setEnabled(show)
        self.btn_C.setEnabled(show)
        self.btn_D.setEnabled(show)
        self.btn_E.setEnabled(show)
        self.btn_F.setEnabled(show)
        self.btn_G.setEnabled(show)
        self.btn_H.setEnabled(show)
        self.btn_I.setEnabled(show)
        self.btn_J.setEnabled(show)
        self.btn_K.setEnabled(show)
        self.btn_L.setEnabled(show)
        self.btn_M.setEnabled(show)
        self.btn_N.setEnabled(show)
        self.btn_O.setEnabled(show)
        self.btn_P.setEnabled(show)
        self.btn_Q.setEnabled(show)
        self.btn_R.setEnabled(show)
        self.btn_S.setEnabled(show)
        self.btn_T.setEnabled(show)
        self.btn_U.setEnabled(show)
        self.btn_V.setEnabled(show)
        self.btn_W.setEnabled(show)
        self.btn_X.setEnabled(show)
        self.btn_Y.setEnabled(show)
        self.btn_Z.setEnabled(show)

#####################################################################################################
''' Starter: Script OR import Custom Module '''
#####################################################################################################

if __name__ == "__main__":
    #xbmc.executebuiltin('XBMC.ReplaceWindow(Home)')
    w = None
    w = __HangMan__()
    w.doModal()
    del w
    #xbmc.executebuiltin('XBMC.ReplaceWindow(Scripts)')
