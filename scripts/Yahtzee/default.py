# -*- coding: utf-8 -*-

#####################################################################################################
''' Infos: Data '''
#####################################################################################################
__script__       = "Yahtzee"
__plugin__       = "Unknown"
__author__       = "FrostBox"
__url__          = "http://code.google.com/p/passion-xbmc/"
__svn_url__      = "http://code.google.com/p/passion-xbmc/source/browse/#svn/trunk/scripts/Yahtzee/"
__credits__      = "Team XBMC, http://xbmc.org/"
__platform__     = "xbmc media center"
__date__         = "27-12-2008"
__version__      = "1.0.0"
__svn_revision__ = 0

#####################################################################################################
''' Module: import '''
#####################################################################################################
import os
import sys
import time
import random
import traceback

import xbmc
import xbmcgui

CWD = os.getcwd().rstrip( ";" )
sys.path.append( os.path.join( CWD, "lib" ) )

from libYahtzee import DICE , SCORE
from xcolor import userColorDice

MULTICOLORONROLLING = 1

#####################################################################################################
''' Function: Language, Temp. here for future in xml '''
#####################################################################################################
if xbmc.getLanguage().lower() == "french":
    ROLL = "L A N C E R"
    NAMEOFUPPERSECTION = ["As", "Deux", "Trois", "Quatre", "Cinq", "Six", "Sous-Total", "Bonus", "Total Supérieur"]
    NAMEOFLOWERSECTION = ["Brelan", "Carré", "Full", "Petite Suite", "Grande Suite",
                          "Yahtzee", "Chance","Yahtzee Bonus", "Total Inférieur", "Grand Total"]
else:
    ROLL = "R O L L"
    NAMEOFUPPERSECTION = ["Aces", "Twos", "Threes", "Fours", "Fives", "Sixes", "SubTotal", "Bonus", "Total Upper"]
    NAMEOFLOWERSECTION = ["3 of kind", "4 of kind", "Full House", "Sm. Straight", "Lg. Straight",
                          "Yahtzee", "Chance","Yahtzee Bonus", "Total Lower", "Grand Total"]

#####################################################################################################
''' Function: Global '''
#####################################################################################################
BG00      = os.path.join(CWD, "media", "background-plain.png")
BG01      = os.path.join(CWD, "media", "homeinfo-overlay.png")
BG02      = os.path.join(CWD, "media", "btn-focus.png")
BG03      = os.path.join(CWD, "media", "btn.png")
BG04      = os.path.join(CWD, "media", "logo.png")
BG05      = os.path.join(CWD, "media", "input-focus.png")
BG06      = os.path.join(CWD, "media", "input-nofocus.png")
XBUT      = os.path.join(CWD, "media", "X.png")
BGRADIO   = os.path.join(CWD, "media", "check-box.png")
BGNORADIO = os.path.join(CWD, "media", "check-boxNF.png")

DICEBG      = os.path.join(CWD, "media", "dice", "d%s.png")

TROPHYGOLD  = os.path.join(CWD, "media", "trophy-gold.gif")
TROPHYDICE  = os.path.join(CWD, "media", "trophy-dice.png")

ROLLINGDICE = os.path.join(CWD, "sounds", "rolling.wav")
ROLLDICE    = os.path.join(CWD, "sounds", "roll.wav")
BABY        = os.path.join(CWD, "sounds", "baby.wav")
YABBA       = os.path.join(CWD, "sounds", "yabba.wav")
APPLO       = os.path.join(CWD, "sounds", "applo.wav")

def printLastError():
    ei = sys.exc_info()
    xbmcgui.Dialog().ok("Error !!!", str(ei[1]))
    traceback.print_exception(ei[0], ei[1], ei[2])

def gameSounds(snd):
    if os.path.exists(snd): xbmc.playSFX(snd)

#####################################################################################################
''' Class: Yahtzee '''
#####################################################################################################
CHEXDICE = [ 50,430,90,90]
CH01DICE = [180,430,90,90]
CH02DICE = [275,430,90,90]
CH03DICE = [370,430,90,90]
CH04DICE = [465,430,90,90]
CH05DICE = [560,430,90,90]

ANIMZOOM = 1
STEP     = 65

class YAHTZEE(xbmcgui.Window):
    def __init__(self):
        self.setCoordinateResolution(6)

        self.startNewGame()

        self.addControl(xbmcgui.ControlImage(0,0,720,576, BG00))
        self.addControl(xbmcgui.ControlImage(-100,95,920,360, BG01))
        self.addControl(xbmcgui.ControlLabel(200,63,0,0, "xbox media center", 'special12', alignment=0x00000001))
        self.addControl(xbmcgui.ControlLabel(207,63,0,0, __script__, 'special13'))
        self.logo = xbmcgui.ControlImage(550,40,74,74, BG04)
        self.addControl(self.logo)

        self.countMaxRolling =  xbmcgui.ControlLabel(115,472,90,0, "", 'special12', alignment=0x00000002+0x00000004)
        self.addControl(self.countMaxRolling)
        self.countMaxRolling.setLabel(str(self.score.maxRolling)+"[CR]/[CR]16")

        # EXTRA BUTTON DICE
        self.addControl(xbmcgui.ControlLabel(50,415,90,0, ROLL, 'special13', '0xeeFF0000', alignment=0x00000002+0x00000004))
        self.btn_dice_ex = xbmcgui.ControlButton(50,430,90,90, "", font="font13", textColor='0xeeFF0000',
            focusTexture=BG02, noFocusTexture=BG03, alignment=0x00000002+0x00000004)
        self.addControl(self.btn_dice_ex)
        self.dummy = xbmcgui.ControlButton(50,430,90,90, "", focusTexture="", noFocusTexture="")
        self.addControl(self.dummy)

        # GROUP OF RADIO BUTTON ROLL (EXTRA BUTTON DICE)
        self.roll_1 = xbmcgui.ControlImage(59,520,22,22, BGRADIO)
        self.addControl(self.roll_1)
        self.roll_2 = xbmcgui.ControlImage(84,520,22,22, BGRADIO)
        self.addControl(self.roll_2)
        self.roll_3 = xbmcgui.ControlImage(109,520,22,22, BGRADIO)
        self.addControl(self.roll_3)

        # GROUP OF BUTTON DICE
        self.btn_dice_1 = xbmcgui.ControlButton(180,430,90,90, "", font="font13",
            focusTexture=BG02, noFocusTexture=BG03, alignment=0x00000002+0x00000004)
        self.addControl(self.btn_dice_1)
        self.btn_dice_2 = xbmcgui.ControlButton(275,430,90,90, "", font="font13",
            focusTexture=BG02, noFocusTexture=BG03, alignment=0x00000002+0x00000004)
        self.addControl(self.btn_dice_2)
        self.btn_dice_3 = xbmcgui.ControlButton(370,430,90,90, "", font="font13",
            focusTexture=BG02, noFocusTexture=BG03, alignment=0x00000002+0x00000004)
        self.addControl(self.btn_dice_3)
        self.btn_dice_4 = xbmcgui.ControlButton(465,430,90,90, "", font="font13",
            focusTexture=BG02, noFocusTexture=BG03, alignment=0x00000002+0x00000004)
        self.addControl(self.btn_dice_4)
        self.btn_dice_5 = xbmcgui.ControlButton(560,430,90,90, "", font="font13",
            focusTexture=BG02, noFocusTexture=BG03, alignment=0x00000002+0x00000004)
        self.addControl(self.btn_dice_5)

        # GROUP OF RADIO BUTTON DICE
        self.dice_1Hold = xbmcgui.ControlImage(214,520,22,22, BGNORADIO)
        self.addControl(self.dice_1Hold)
        self.dice_2Hold = xbmcgui.ControlImage(309,520,22,22, BGNORADIO)
        self.addControl(self.dice_2Hold)
        self.dice_3Hold = xbmcgui.ControlImage(404,520,22,22, BGNORADIO)
        self.addControl(self.dice_3Hold)
        self.dice_4Hold = xbmcgui.ControlImage(499,520,22,22, BGNORADIO)
        self.addControl(self.dice_4Hold)
        self.dice_5Hold = xbmcgui.ControlImage(594,520,22,22, BGNORADIO)
        self.addControl(self.dice_5Hold)

        # GROUP OF BUTTON SCORE
        self.upperScore = xbmcgui.ControlList(
            87,120,270,350, font = "font13",
            textColor = "0xFFFFFFFF", selectedColor = "0xFFFF9600",
            buttonFocusTexture = BG05,
            buttonTexture = BG06,
            itemTextXOffset = -10, itemHeight = 28)
        self.addControl(self.upperScore)

        self.lowerScore = xbmcgui.ControlList(
            363,120,270,350, font = "font13",
            textColor = "0xFFFFFFFF", selectedColor = "0xFFFF9600",
            buttonFocusTexture = BG05,
            buttonTexture = BG06,
            itemTextXOffset = -10, itemHeight = 28)
        self.addControl(self.lowerScore)

        # EXTRA DICE
        self.dice_ex = xbmcgui.ControlImage(CHEXDICE[0], CHEXDICE[1], CHEXDICE[2], CHEXDICE[3], DICEBG % self.dice.ex)
        self.addControl(self.dice_ex)
        # GROUP OF DICE
        self.dice_1  = xbmcgui.ControlImage(CH01DICE[0], CH01DICE[1], CH01DICE[2], CH01DICE[3], DICEBG % self.dice.d1)
        self.addControl(self.dice_1)
        self.dice_2  = xbmcgui.ControlImage(CH02DICE[0], CH02DICE[1], CH02DICE[2], CH02DICE[3], DICEBG % self.dice.d2)
        self.addControl(self.dice_2)
        self.dice_3  = xbmcgui.ControlImage(CH03DICE[0], CH03DICE[1], CH03DICE[2], CH03DICE[3], DICEBG % self.dice.d3)
        self.addControl(self.dice_3)
        self.dice_4  = xbmcgui.ControlImage(CH04DICE[0], CH04DICE[1], CH04DICE[2], CH04DICE[3], DICEBG % self.dice.d4)
        self.addControl(self.dice_4)
        self.dice_5  = xbmcgui.ControlImage(CH05DICE[0], CH05DICE[1], CH05DICE[2], CH05DICE[3], DICEBG % self.dice.d5)
        self.addControl(self.dice_5)

        self.setNavigationOnDice()
        self.setHoldForNewGame()
        self.setScoreSection()
        self.setColorDice()

    def showAnimation(self):
        #self.diffXzoom = ANIMZOOM*(50 - CHEXDICE[0])
        #self.diffYzoom = ANIMZOOM*( 0 - CHEXDICE[1])
        #self.diffXzoom = ANIMZOOM*(random.choice(range(-360, 360)) - CHEXDICE[0])
        #self.diffYzoom = ANIMZOOM*(random.choice(range(-288, 288)) - CHEXDICE[1])
        self.diffXzoom = ANIMZOOM*(random.choice(range(-720, 720)))
        self.diffYzoom = ANIMZOOM*(random.choice(range(-576, 576)))
        self.diffWzoom = ANIMZOOM*(CHEXDICE[2] - 1)
        self.diffHzoom = ANIMZOOM*(CHEXDICE[3] - 1)
        if not MULTICOLORONROLLING: self.setMultiColor()
        for zoompos in range(STEP, -1, -1):
            self.zoomAnimation(zoompos)
            if MULTICOLORONROLLING: self.setMultiColor()
            time.sleep(0.01)

    def zoomAnimation(self, pct):
        elmt_stepX = float(self.diffXzoom)/float(STEP)
        elmt_stepY = float(self.diffYzoom)/float(STEP)
        elmt_stepW = float(self.diffWzoom)/float(STEP)
        elmt_stepH = float(self.diffHzoom)/float(STEP)
        deltaX     = int(pct*elmt_stepX)
        deltaY     = int(pct*elmt_stepY)
        deltaW     = int(pct*elmt_stepW)
        deltaH     = int(pct*elmt_stepH)
        if not self.dice_1HoldOn:
            self.dice_1.setPosition(CH01DICE[0]+deltaX, CH01DICE[1]+deltaY)
            self.dice_1.setWidth(   CH01DICE[2]-deltaW)
            self.dice_1.setHeight(  CH01DICE[3]-deltaH)
            self.dice.d1 = str(random.choice(self.randomDice))
            self.dice_1.setImage(DICEBG % self.dice.d1)
        if not self.dice_2HoldOn:
            self.dice_2.setPosition(CH02DICE[0]+deltaX, CH02DICE[1]+deltaY)
            self.dice_2.setWidth(   CH02DICE[2]-deltaW)
            self.dice_2.setHeight(  CH02DICE[3]-deltaH)
            self.dice.d2 = str(random.choice(self.randomDice))
            self.dice_2.setImage(DICEBG % self.dice.d2)
        if not self.dice_3HoldOn:
            self.dice_3.setPosition(CH03DICE[0]+deltaX, CH03DICE[1]+deltaY)
            self.dice_3.setWidth(   CH03DICE[2]-deltaW)
            self.dice_3.setHeight(  CH03DICE[3]-deltaH)
            self.dice.d3 = str(random.choice(self.randomDice))
            self.dice_3.setImage(DICEBG % self.dice.d3)
        if not self.dice_4HoldOn:
            self.dice_4.setPosition(CH04DICE[0]+deltaX, CH04DICE[1]+deltaY)
            self.dice_4.setWidth(   CH04DICE[2]-deltaW)
            self.dice_4.setHeight(  CH04DICE[3]-deltaH)
            self.dice.d4 = str(random.choice(self.randomDice))
            self.dice_4.setImage(DICEBG % self.dice.d4)
        if not self.dice_5HoldOn:
            self.dice_5.setPosition(CH05DICE[0]+deltaX, CH05DICE[1]+deltaY)
            self.dice_5.setWidth(   CH05DICE[2]-deltaW)
            self.dice_5.setHeight(  CH05DICE[3]-deltaH)
            self.dice.d5 = str(random.choice(self.randomDice))
            self.dice_5.setImage(DICEBG % self.dice.d5)
        if self.rollDice == 3:
            self.dice_ex.setPosition(CHEXDICE[0]+deltaX, CHEXDICE[1]+deltaY)
            self.dice_ex.setWidth(   CHEXDICE[2]-deltaW)
            self.dice_ex.setHeight(  CHEXDICE[3]-deltaH)
            self.dice.ex = str(random.choice(self.randomDice))
            self.dice_ex.setImage(DICEBG % self.dice.ex)

    def setNavigationOnDice(self):
        self.groupID = self.btn_dice_ex.getId()
        self.btn_dice_ex.setNavigation(self.btn_dice_ex, self.btn_dice_ex, self.btn_dice_5,  self.btn_dice_1)
        self.btn_dice_1.setNavigation( self.btn_dice_1,  self.btn_dice_1,  self.btn_dice_ex, self.btn_dice_2)
        self.btn_dice_2.setNavigation( self.btn_dice_2,  self.btn_dice_2,  self.btn_dice_1,  self.btn_dice_3)
        self.btn_dice_3.setNavigation( self.btn_dice_3,  self.btn_dice_3,  self.btn_dice_2,  self.btn_dice_4)
        self.btn_dice_4.setNavigation( self.btn_dice_4,  self.btn_dice_4,  self.btn_dice_3,  self.btn_dice_5)
        self.btn_dice_5.setNavigation( self.btn_dice_5,  self.btn_dice_5,  self.btn_dice_4,  self.btn_dice_ex)
        self.setFocus(self.btn_dice_ex)

    def setNavigationOnScore(self):
        self.groupID = self.upperScore.getId()
        self.upperScore.setNavigation(self.upperScore, self.upperScore, self.lowerScore, self.lowerScore)
        self.lowerScore.setNavigation(self.lowerScore, self.lowerScore, self.upperScore, self.upperScore)
        self.setFocus(self.upperScore)

    def startNewGame(self):
        try: self.setLocalScore()
        except: pass#printLastError()
        self.score = SCORE()
        self.score.reset()
        self.nextRound()
        try: self.countMaxRolling.setLabel(str(self.score.maxRolling)+"[CR]/[CR]16")
        except: pass
        xbmc.executebuiltin("XBMC.Notification(Yahrzee,New Game,4000,%s)" % TROPHYGOLD)

    def nextRound(self):
        if self.score.maxRolling > 0:
            self.dice = DICE()
            self.randomDice = self.dice.choiceDice(6)
            self.dice.d1 = str(random.choice(self.randomDice))
            self.dice.d2 = str(random.choice(self.randomDice))
            self.dice.d3 = str(random.choice(self.randomDice))
            self.dice.d4 = str(random.choice(self.randomDice))
            self.dice.d5 = str(random.choice(self.randomDice))
            self.dice.ex = str(random.choice(self.randomDice))
            self.rollDice = 3
            self.rollDiceIsStarted = 0
            try: self.setHoldForNewGame()
            except: pass
        if self.score.maxRolling <= 0:
            xbmc.executebuiltin("XBMC.Notification(Game Over,X New Game,4000,%s)" % XBUT)

    def setHoldForNewGame(self):
        self.dice_1HoldOn = 0
        self.dice_2HoldOn = 0
        self.dice_3HoldOn = 0
        self.dice_4HoldOn = 0
        self.dice_5HoldOn = 0
        self.roll_1.setImage(BGRADIO)
        self.roll_2.setImage(BGRADIO)
        self.roll_3.setImage(BGRADIO)
        self.dice_1Hold.setImage(BGNORADIO)
        self.dice_2Hold.setImage(BGNORADIO)
        self.dice_3Hold.setImage(BGNORADIO)
        self.dice_4Hold.setImage(BGNORADIO)
        self.dice_5Hold.setImage(BGNORADIO)

    def setScoreSection(self):
        self.setScoreUpperSection()
        self.setScoreLowerSection()

    def setScoreUpperSection(self):
        self.upperScore.reset()
        listlabel = [self.score.current["uppersection"]["Aces"], self.score.current["uppersection"]["Twos"],
                     self.score.current["uppersection"]["Threes"], self.score.current["uppersection"]["Fours"],
                     self.score.current["uppersection"]["Fives"], self.score.current["uppersection"]["Sixes"],
                     self.score.current["uppersection"]["SubTotal"], self.score.current["uppersection"]["Bonus"],
                     self.score.current["uppersection"]["Total Upper"]]
        [self.upperScore.addItem(xbmcgui.ListItem(label=str(l), label2=str(l2))) for l, l2 in zip(NAMEOFUPPERSECTION, listlabel)]

    def setScoreLowerSection(self):
        self.lowerScore.reset()
        listlabel = [self.score.current["lowersection"]["3 of kind"], self.score.current["lowersection"]["4 of kind"],
                     self.score.current["lowersection"]["Full House"], self.score.current["lowersection"]["Sm. Straight"],
                     self.score.current["lowersection"]["Lg. Straight"], self.score.current["lowersection"]["Yahtzee"],
                     self.score.current["lowersection"]["Chance"], self.score.current["lowersection"]["Yahtzee Bonus"],
                     self.score.current["lowersection"]["Total Lower"], self.score.current["lowersection"]["Grand Total"]]
        [self.lowerScore.addItem(xbmcgui.ListItem(label=str(l), label2=str(l2))) for l, l2 in zip(NAMEOFLOWERSECTION, listlabel)]

    def allDice(self):
        return [self.dice.ex, self.dice.d1, self.dice.d2, self.dice.d3, self.dice.d4, self.dice.d5]

    def onActionScore(self, action):
        if self.getFocus() == self.upperScore and self.upperScore.getSelectedPosition() != -1:
            alldice = self.allDice()
            self.setScoreLowerSection()
            if   self.upperScore.getSelectedPosition() == 6: self.upperScore.selectItem(0)
            elif self.upperScore.getSelectedPosition() == 8: self.upperScore.selectItem(5)
            if self.upperScore.getSelectedPosition() == 0:
                if self.score.current["uppersection"]["Aces"] == self.score.default["uppersection"]["Aces"]:
                    self.upperScore.getSelectedItem().setLabel2(self.score.singleXDice("1", alldice))
            elif self.upperScore.getSelectedPosition() == 1:
                if self.score.current["uppersection"]["Twos"] == self.score.default["uppersection"]["Twos"]:
                    self.upperScore.getSelectedItem().setLabel2(self.score.singleXDice("2", alldice))
            elif self.upperScore.getSelectedPosition() == 2:
                if self.score.current["uppersection"]["Threes"] == self.score.default["uppersection"]["Threes"]:
                    self.upperScore.getSelectedItem().setLabel2(self.score.singleXDice("3", alldice))
            elif self.upperScore.getSelectedPosition() == 3:
                if self.score.current["uppersection"]["Fours"] == self.score.default["uppersection"]["Fours"]:
                    self.upperScore.getSelectedItem().setLabel2(self.score.singleXDice("4", alldice))
            elif self.upperScore.getSelectedPosition() == 4:
                if self.score.current["uppersection"]["Fives"] == self.score.default["uppersection"]["Fives"]:
                    self.upperScore.getSelectedItem().setLabel2(self.score.singleXDice("5", alldice))
            elif self.upperScore.getSelectedPosition() == 5:
                if self.score.current["uppersection"]["Sixes"] == self.score.default["uppersection"]["Sixes"]:
                    self.upperScore.getSelectedItem().setLabel2(self.score.singleXDice("6", alldice))

        elif self.getFocus() == self.lowerScore and self.lowerScore.getSelectedPosition() != -1:
            alldice = self.allDice()
            self.setScoreUpperSection()
            if   self.lowerScore.getSelectedPosition() == 7: self.lowerScore.selectItem(0)
            elif self.lowerScore.getSelectedPosition() == 9: self.lowerScore.selectItem(6)
            if self.lowerScore.getSelectedPosition() == 0:
                if self.score.current["lowersection"]["3 of kind"] == self.score.default["lowersection"]["3 of kind"]:
                    self.lowerScore.getSelectedItem().setLabel2(self.score.ofKind(3, alldice))
            elif self.lowerScore.getSelectedPosition() == 1:
                if self.score.current["lowersection"]["4 of kind"] == self.score.default["lowersection"]["4 of kind"]:
                    self.lowerScore.getSelectedItem().setLabel2(self.score.ofKind(4, alldice))
            elif self.lowerScore.getSelectedPosition() == 2:
                if self.score.current["lowersection"]["Full House"] == self.score.default["lowersection"]["Full House"]:
                    self.lowerScore.getSelectedItem().setLabel2(self.score.fullHouse(alldice))
            elif self.lowerScore.getSelectedPosition() == 3:
                if self.score.current["lowersection"]["Sm. Straight"] == self.score.default["lowersection"]["Sm. Straight"]:
                    self.lowerScore.getSelectedItem().setLabel2(self.score.smStraight(alldice))
            elif self.lowerScore.getSelectedPosition() == 4:
                if self.score.current["lowersection"]["Lg. Straight"] == self.score.default["lowersection"]["Lg. Straight"]:
                    self.lowerScore.getSelectedItem().setLabel2(self.score.lgStraight(alldice))
            elif self.lowerScore.getSelectedPosition() == 5:
                sc, sd = self.score.current["lowersection"]["Yahtzee"], self.score.default["lowersection"]["Yahtzee"]
                if (sc == sd)|(sc != sd)&(not sc == "0"):
                    self.lowerScore.getSelectedItem().setLabel2(self.score.yahtzee(alldice))
            elif self.lowerScore.getSelectedPosition() == 6:
                if self.score.current["lowersection"]["Chance"] == self.score.default["lowersection"]["Chance"]:
                    self.lowerScore.getSelectedItem().setLabel2(self.score.chance(alldice))

    def onAction(self, action):
        if action == 10:
            try: self.setLocalScore()
            except: pass#printLastError()
            self.close()
        if (action == 18)&(not self.rollDiceIsStarted):
            self.startNewGame()
            self.setNavigationOnDice()
            self.setScoreSection()
        if (action == 34)&(not self.rollDiceIsStarted):
            self.showLocalHiScore()
        if (action == 117)&(not self.rollDiceIsStarted):
            self.setScoreSection()
            if self.groupID == self.btn_dice_ex.getId(): self.setNavigationOnScore()
            elif self.groupID == self.upperScore.getId(): self.setNavigationOnDice()
        try: self.onActionScore(action)
        except: printLastError()

    def onControlScore(self, control):
        if (control == self.upperScore)&(self.rollDice != 3):
            if self.score.maxRolling <= 0:
                xbmc.executebuiltin("XBMC.Notification(Game Over,X New Game,4000,%s)" % XBUT)
            else:
                alldice = self.allDice()
                if self.upperScore.getSelectedPosition() == 0:
                    if self.score.current["uppersection"]["Aces"] == self.score.default["uppersection"]["Aces"]:
                        value = self.score.singleXDice("1", alldice)
                        self.score.current["uppersection"]["Aces"] = value
                        self.upperScore.getSelectedItem().setLabel2(value)
                        self.setFinally()
                elif self.upperScore.getSelectedPosition() == 1:
                    if self.score.current["uppersection"]["Twos"] == self.score.default["uppersection"]["Twos"]:
                        value = self.score.singleXDice("2", alldice)
                        self.score.current["uppersection"]["Twos"] = value
                        self.upperScore.getSelectedItem().setLabel2(value)
                        self.setFinally()
                elif self.upperScore.getSelectedPosition() == 2:
                    if self.score.current["uppersection"]["Threes"] == self.score.default["uppersection"]["Threes"]:
                        value = self.score.singleXDice("3", alldice)
                        self.score.current["uppersection"]["Threes"] = value
                        self.upperScore.getSelectedItem().setLabel2(value)
                        self.setFinally()
                elif self.upperScore.getSelectedPosition() == 3:
                    if self.score.current["uppersection"]["Fours"] == self.score.default["uppersection"]["Fours"]:
                        value = self.score.singleXDice("4", alldice)
                        self.score.current["uppersection"]["Fours"] = value
                        self.upperScore.getSelectedItem().setLabel2(value)
                        self.setFinally()
                elif self.upperScore.getSelectedPosition() == 4:
                    if self.score.current["uppersection"]["Fives"] == self.score.default["uppersection"]["Fives"]:
                        value = self.score.singleXDice("5", alldice)
                        self.score.current["uppersection"]["Fives"] = value
                        self.upperScore.getSelectedItem().setLabel2(value)
                        self.setFinally()
                elif self.upperScore.getSelectedPosition() == 5:
                    if self.score.current["uppersection"]["Sixes"] == self.score.default["uppersection"]["Sixes"]:
                        value = self.score.singleXDice("6", alldice)
                        self.score.current["uppersection"]["Sixes"] = value
                        self.upperScore.getSelectedItem().setLabel2(value)
                        self.setFinally()
                else: pass

        if (control == self.lowerScore)&(self.rollDice != 3):
            if self.score.maxRolling <= 0:
                xbmc.executebuiltin("XBMC.Notification(Game Over,X New Game,4000,%s)" % XBUT)
            else:
                alldice = self.allDice()
                if self.lowerScore.getSelectedPosition() == 0:
                    if self.score.current["lowersection"]["3 of kind"] == self.score.default["lowersection"]["3 of kind"]:
                        value = self.score.ofKind(3, alldice)
                        self.score.current["lowersection"]["3 of kind"] = value
                        self.lowerScore.getSelectedItem().setLabel2(value)
                        self.setFinally()
                elif self.lowerScore.getSelectedPosition() == 1:
                    if self.score.current["lowersection"]["4 of kind"] == self.score.default["lowersection"]["4 of kind"]:
                        value = self.score.ofKind(4, alldice)
                        self.score.current["lowersection"]["4 of kind"] = value
                        self.lowerScore.getSelectedItem().setLabel2(value)
                        self.setFinally()
                elif self.lowerScore.getSelectedPosition() == 2:
                    if self.score.current["lowersection"]["Full House"] == self.score.default["lowersection"]["Full House"]:
                        value = self.score.fullHouse(alldice)
                        self.score.current["lowersection"]["Full House"] = value
                        self.lowerScore.getSelectedItem().setLabel2(value)
                        self.setFinally()
                elif self.lowerScore.getSelectedPosition() == 3:
                    if self.score.current["lowersection"]["Sm. Straight"] == self.score.default["lowersection"]["Sm. Straight"]:
                        value = self.score.smStraight(alldice)
                        self.score.current["lowersection"]["Sm. Straight"] = value
                        self.lowerScore.getSelectedItem().setLabel2(value)
                        self.setFinally()
                elif self.lowerScore.getSelectedPosition() == 4:
                    if self.score.current["lowersection"]["Lg. Straight"] == self.score.default["lowersection"]["Lg. Straight"]:
                        value = self.score.lgStraight(alldice)
                        self.score.current["lowersection"]["Lg. Straight"] = value
                        self.lowerScore.getSelectedItem().setLabel2(value)
                        self.setFinally()
                elif self.lowerScore.getSelectedPosition() == 5:
                    sc, sd = self.score.current["lowersection"]["Yahtzee"], self.score.default["lowersection"]["Yahtzee"]
                    if (sc == sd)|(sc != sd)&("[ ]" in self.score.current["lowersection"]["Yahtzee Bonus"])&(not sc == "0"):
                        value = self.score.yahtzee(alldice)
                        if (value == "0")&(sc == sd):
                            self.score.current["lowersection"]["Yahtzee Bonus"] = str("[0] [0] [0]")
                            self.score.current["lowersection"]["Yahtzee"] = value
                            self.score.maxRolling -= 3
                        elif (value == sc)|((value == "0")&(sc == "50"))|((value == "0")&(sc == "150"))|((value == "0")&(sc == "250")):
                            self.score.lossYahtzeeBonus()
                        elif ((value == "50")&(sc == sd))|((value == "150")&(sc == "50"))|((value == "250")&(sc == "150"))|((value == "350")&(sc == "250")):
                            self.score.current["lowersection"]["Yahtzee"] = value
                            self.lowerScore.getSelectedItem().setLabel2(value)
                            self.score.markYahtzeeBonus()
                        self.setFinally()
                elif self.lowerScore.getSelectedPosition() == 6:
                    if self.score.current["lowersection"]["Chance"] == self.score.default["lowersection"]["Chance"]:
                        value = self.score.chance(alldice)
                        self.score.current["lowersection"]["Chance"] = value
                        self.lowerScore.getSelectedItem().setLabel2(value)
                        self.setFinally()
                else: pass

    def setFinally(self):
        self.score.totalUpper()
        self.score.totalLower()
        self.score.grandTotal()
        self.score.decreaseMaxRolling()
        self.countMaxRolling.setLabel(str(self.score.maxRolling)+"[CR]/[CR]16")
        self.nextRound()
        self.setScoreSection()
        self.setNavigationOnDice()

    def onControl(self, control):
        if control == self.dummy: pass
        if (control == self.btn_dice_ex)&(not self.rollDiceIsStarted):
            numdice = 5-int(sum([self.dice_1HoldOn, self.dice_2HoldOn, self.dice_3HoldOn, self.dice_4HoldOn, self.dice_5HoldOn]))
            if not numdice <= 0:
                self.randomDice = self.dice.choiceDice(numdice)
                if self.rollDice > 0:
                    self.rollDiceIsStarted = 1
                    self.setFocus(self.dummy)
                    gameSounds(ROLLINGDICE)
                    try: self.showAnimation()
                    except: printLastError()
                    self.rollDiceIsStarted = 0
                    xbmc.sleep(500)
                    self.playSpecial()
                    self.setFocus(self.btn_dice_ex)
            self.rollDice -= 1
            if self.rollDice <= -1:
                self.setNavigationOnScore()
            elif self.rollDice == 2:
                self.roll_3.setImage(BGNORADIO)
            elif self.rollDice == 1:
                self.roll_2.setImage(BGNORADIO)
            elif self.rollDice == 0:
                self.roll_1.setImage(BGNORADIO)
                gameSounds(APPLO)
                self.setNavigationOnScore()
                if self.score.current["uppersection"]["Aces"] == self.score.default["uppersection"]["Aces"]:
                    self.upperScore.getSelectedItem().setLabel2(self.score.singleXDice("1", self.allDice()))
        if self.rollDice != 3:
            if control == self.btn_dice_1:
                if self.dice_1HoldOn:
                    self.dice_1Hold.setImage(BGNORADIO)
                    self.dice_1HoldOn = 0
                else:
                    self.dice_1Hold.setImage(BGRADIO)
                    self.dice_1HoldOn = 1
            if control == self.btn_dice_2:
                if self.dice_2HoldOn:
                    self.dice_2Hold.setImage(BGNORADIO)
                    self.dice_2HoldOn = 0
                else:
                    self.dice_2Hold.setImage(BGRADIO)
                    self.dice_2HoldOn = 1
            if control == self.btn_dice_3:
                if self.dice_3HoldOn:
                    self.dice_3Hold.setImage(BGNORADIO)
                    self.dice_3HoldOn = 0
                else:
                    self.dice_3Hold.setImage(BGRADIO)
                    self.dice_3HoldOn = 1
            if control == self.btn_dice_4:
                if self.dice_4HoldOn:
                    self.dice_4Hold.setImage(BGNORADIO)
                    self.dice_4HoldOn = 0
                else:
                    self.dice_4Hold.setImage(BGRADIO)
                    self.dice_4HoldOn = 1
            if control == self.btn_dice_5:
                if self.dice_5HoldOn:
                    self.dice_5Hold.setImage(BGNORADIO)
                    self.dice_5HoldOn = 0
                else:
                    self.dice_5Hold.setImage(BGRADIO)
                    self.dice_5HoldOn = 1
        else: pass
        try: self.onControlScore(control)
        except: printLastError()

    def playSpecial(self):
        snd = None
        alldice = self.allDice()
        if alldice.count("6") == 5: snd = BABY
        if alldice.count("5") == 5: snd = BABY
        if alldice.count("4") == 5: snd = BABY
        if alldice.count("3") == 5: snd = BABY
        if alldice.count("2") == 5: snd = BABY
        if alldice.count("1") == 5: snd = BABY
        if alldice.count("6") == 6: snd = YABBA
        if alldice.count("5") == 6: snd = YABBA
        if alldice.count("4") == 6: snd = YABBA
        if alldice.count("3") == 6: snd = YABBA
        if alldice.count("2") == 6: snd = YABBA
        if alldice.count("1") == 6: snd = YABBA
        if snd: gameSounds(snd)

    def setLocalScore(self, perfect=""):
        if self.score.maxRolling <= 0 and not self.score.isSameDict():
            if self.score.current["lowersection"]["Grand Total"] == "714":
                perfect="*"
                self.dice_ex.setImage(TROPHYGOLD)
                xbmcgui.Dialog().ok("Perfect Game 714", "Great job %s" % name)
            keyboard = xbmc.Keyboard("", "If you want to save current score enter your name.")
            keyboard.doModal()
            if keyboard.isConfirmed():
                f = open(os.path.join(CWD, "Hi-Score.txt"), "a")
                f.write(perfect+"%s, %s, %s\n" % (self.score.current["lowersection"]["Grand Total"], keyboard.getText(), time.ctime()))
                f.close()

    def showLocalHiScore(self):
        if os.path.exists(os.path.join(CWD, "Hi-Score.txt")):
            scorelist = file(os.path.join(CWD, "Hi-Score.txt"), "r").read().split('\n')[:-1]
            scorelist.sort(key=lambda x: int(x.split(",")[0]), reverse=True)
            if len(scorelist) > 0: xbmcgui.Dialog().select("Yahtzee Hi-Score", scorelist)

    def setColorDice(self):
        ucd = userColorDice()
        ucd.doModal()
        color = ucd.colorDice
        self.multi = ucd.multiColor
        del ucd
        if self.multi: self.setMultiColor()
        elif color:
            self.dice_1.setColorDiffuse(color)
            self.dice_2.setColorDiffuse(color)
            self.dice_3.setColorDiffuse(color)
            self.dice_4.setColorDiffuse(color)
            self.dice_5.setColorDiffuse(color)
        self.dice_ex.setColorDiffuse('0xaaAA0000')
        self.logo.setColorDiffuse('0x80FFFFFF')

    def setMultiColor(self):
        if self.multi:
            self.dice.changeColorDice(self.multi)
            if not self.dice_1HoldOn: self.dice_1.setColorDiffuse(random.choice(self.multi))
            if not self.dice_2HoldOn: self.dice_2.setColorDiffuse(random.choice(self.multi))
            if not self.dice_3HoldOn: self.dice_3.setColorDiffuse(random.choice(self.multi))
            if not self.dice_4HoldOn: self.dice_4.setColorDiffuse(random.choice(self.multi))
            if not self.dice_5HoldOn: self.dice_5.setColorDiffuse(random.choice(self.multi))

if __name__ == "__main__":
    w = YAHTZEE()
    w.doModal()
    del w
