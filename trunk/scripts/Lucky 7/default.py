# -*- coding: iso-8859-1 -*-

#####################################################################################################
''' Infos: Data '''
#####################################################################################################
__script__       = "Lucky $even"
__plugin__       = "Unknown"
__author__       = "Frost"
__url__          = "http://passion-xbmc.org/index.php"
__svn_url__      = "http://passion-xbmc.googlecode.com/svn/branches/scripts/Lucky%207/"
__OldSourceUrl__ = "http://scripts4xbmc.cvs.sourceforge.net/viewvc/scripts4xbmc/Scripts/Lucky%207/"
__credits__      = "Team XBMC, http://xbmc.org/"
__platform__     = "xbmc media center"
__date__         = "24-02-2009"
__version__      = "1.1.0"
__svn_revision__ = 0

#####################################################################################################
''' Module: import '''
#####################################################################################################
import xbmc , xbmcgui
import glob , os , os.path
import re , string , time
from marshal import dump , load
from random import choice , randint

CWD = os.getcwd().replace( ";", "" )

# Time of spin stop = 6sec.
endSpin = 444

#####################################################################################################
''' Function: Skin '''
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
    except: pass

media_xpr  = os.path.join(CWD, "media", "Textures.xpr")
bonus_xpr  = os.path.join(CWD, "media", "bonus.xpr")
thumbs_xpr = os.path.join(CWD, "media", "thumbnails.xpr")
keys_xpr   = os.path.join(CWD, "media", "bgkeys.xpr")
snd        = os.path.join(CWD, "media", "sounds.snd")
skin_cache = os.path.join(CWD, "media", "cache")

unpack_xpr(skin_cache, bonus_xpr)
unpack_xpr(skin_cache, thumbs_xpr)
unpack_xpr(skin_cache, keys_xpr)
unpack_xpr(skin_cache, media_xpr)
unpack_xpr(skin_cache, snd)

BG_00  = os.path.join(skin_cache, "background-plain.png")
BG_01  = os.path.join(skin_cache, "keyboard-numeric-bg.png")
BG_02  = os.path.join(skin_cache, "keyboard-numeric-overlay.png")
BG_03  = os.path.join(skin_cache, "keyboard-btn-backspace-focus.png")
BG_04  = os.path.join(skin_cache, "keyboard-btn-backspace.png")
BG_05  = os.path.join(skin_cache, "keyboard-btn-space-focus.png")
BG_06  = os.path.join(skin_cache, "Vegas_Chips.gif")
BG_07  = os.path.join(skin_cache, "dialog-panel2.png")
BG_08  = os.path.join(skin_cache, "winning-slot.png")
BG_09  = os.path.join(skin_cache, "btn-st-focus.png")
BG_10  = os.path.join(skin_cache, "btn-st.png")
BG_11  = os.path.join(skin_cache, "btn-bet-focus.png")
BG_12  = os.path.join(skin_cache, "btn-bet.png")

BG_K1  = os.path.join(skin_cache, "A.png")
BG_K2  = os.path.join(skin_cache, "B.png")
BG_K3  = os.path.join(skin_cache, "BACK.png")
BG_K4  = os.path.join(skin_cache, "black.png")
BG_K5  = os.path.join(skin_cache, "Start.png")
BG_K6  = os.path.join(skin_cache, "white.png")
BG_K7  = os.path.join(skin_cache, "X.png")
BG_K8  = os.path.join(skin_cache, "Y.png")

BG_V1  = os.path.join(skin_cache, "b_1bar.png")
BG_V2  = os.path.join(skin_cache, "b_1cherry.png")
BG_V3  = os.path.join(skin_cache, "b_1seven.png")
BG_V4  = os.path.join(skin_cache, "b_2bar.png")
BG_V5  = os.path.join(skin_cache, "b_2cherry.png")
BG_V6  = os.path.join(skin_cache, "b_2seven.png")
BG_V7  = os.path.join(skin_cache, "b_3bar.png")
BG_V8  = os.path.join(skin_cache, "b_3cherry.png")
BG_V9  = os.path.join(skin_cache, "b_3seven.png")
BG_V10 = os.path.join(skin_cache, "b_anybar.png")
BG_V11 = os.path.join(skin_cache, "b_bell.png")
BG_V12 = os.path.join(skin_cache, "b_melon.png")
BG_V13 = os.path.join(skin_cache, "b_orange.png")
BG_V14 = os.path.join(skin_cache, "b_prune.png")

BG_R1  = os.path.join(skin_cache, "random1.GIF")
BG_R2  = os.path.join(skin_cache, "random2.GIF")
BG_R3  = os.path.join(skin_cache, "random3.GIF")

BG_F1  = os.path.join(skin_cache, "one_bar.PNG")
BG_F2  = os.path.join(skin_cache, "two_bar.PNG")
BG_F3  = os.path.join(skin_cache, "three_bar.PNG")
BG_F4  = os.path.join(skin_cache, "bell.PNG")
BG_F5  = os.path.join(skin_cache, "cherries.PNG")
BG_F6  = os.path.join(skin_cache, "melon.PNG")
BG_F7  = os.path.join(skin_cache, "orange.PNG")
BG_F8  = os.path.join(skin_cache, "prune.png")
BG_F9  = os.path.join(skin_cache, "seven.PNG")

slotchoices = [BG_F1, BG_F2, BG_F3, BG_F4, BG_F5,
               BG_F6, BG_F7, BG_F8, BG_F9]

coin = os.path.join(skin_cache, "coin.wav")

#####################################################################################################
''' Function: Sounds '''
#####################################################################################################
glob.sounds_effect = True
def Sounds(track):
    if glob.sounds_effect:
        #if not xbmc.Player().isPlaying():
            path = os.path.join(skin_cache, track)
            xbmc.Player().play(path)

#####################################################################################################
''' Class: Lucky7 '''
#####################################################################################################
class __Lucky7__(xbmcgui.Window):
    def __init__(self):
        self.setCoordinateResolution(6)
        xbmc.executebuiltin("XBMC.Notification(Lucky $even,Welcome,800,%s)" % choice(slotchoices))

        self.tmp_file = os.path.join(CWD,"Jack.pot")
        self.Load_Jackpot()
        self.Jackpot    = self.pot["Jackpot"]

        self.is_started = False
        self.winner_pot  = False
        self.x2           = False
        self.max_is_betted = False

        self.display1   = ""
        self.display2   = ""
        self.display3   = ""
        self.display    = 0

        self.gain       = 0
        self.bet        = 0
        self.max_bet    = 25
        self.cash       = 250
        self.max_cash   = 7e+7

        self.align = 0x00000002+0x00000004

        self.addControl(xbmcgui.ControlImage(0,0,0,0,BG_00))

        self.addControl(xbmcgui.ControlLabel(200,63,0,0,"xbmc media center",'special12',alignment=0x00000001))
        self.addControl(xbmcgui.ControlLabel(207,63,0,0,__script__,'special13'))

        self.addControl(xbmcgui.ControlImage(135,130,150,150,BG_01))
        self.addControl(xbmcgui.ControlImage(285,130,150,150,BG_01))
        self.addControl(xbmcgui.ControlImage(435,130,150,150,BG_01))

        self.win_slot1 = xbmcgui.ControlImage(135,130,150,150,BG_08)
        self.addControl(self.win_slot1)
        self.win_slot2 = xbmcgui.ControlImage(285,130,150,150,BG_08)
        self.addControl(self.win_slot2)
        self.win_slot3 = xbmcgui.ControlImage(435,130,150,150,BG_08)
        self.addControl(self.win_slot3)

        self.slot1 = xbmcgui.ControlImage(155,140,120,120,"")
        self.addControl(self.slot1)
        self.slot2 = xbmcgui.ControlImage(305,140,120,120,"")
        self.addControl(self.slot2)
        self.slot3 = xbmcgui.ControlImage(455,140,120,120,"")
        self.addControl(self.slot3)

        self.addControl(xbmcgui.ControlImage(135,130,150,150,BG_02))
        self.addControl(xbmcgui.ControlImage(285,130,150,150,BG_02))
        self.addControl(xbmcgui.ControlImage(435,130,150,150,BG_02))

        self.default_focus_slot()
        self.default_start_slot()

        self.info_Jackpot = xbmcgui.ControlLabel(550,63,0,0,"Jackpot($): "+str(self.Jackpot),'special12','0xFFFF9600')
        self.addControl(self.info_Jackpot)

        self.info_Win = xbmcgui.ControlLabel(0,450,720,0,"","font13",'0xFFFF9600',alignment=self.align)
        self.addControl(self.info_Win)

        self.info_Bet = xbmcgui.ControlLabel(510,375,0,0,"Mi$e\n"+str(self.bet),"font13",'0xffD2FF00',alignment=0x00000002)
        self.addControl(self.info_Bet)

        self.info_cash = xbmcgui.ControlLabel(200,375,0,0,"Ca$h\n"+str(self.cash),"font13",'0xffD2FF00',alignment=0x00000002)
        self.addControl(self.info_cash)

        self.btn_betm = xbmcgui.ControlButton(
            250,370,60,60,"Bet\n-",font="special13",
            focusTexture=BG_11,
            noFocusTexture=BG_12,
            alignment=self.align)
        self.addControl(self.btn_betm)

        self.btn_betmax = xbmcgui.ControlButton(
            330,370,60,60,"Bet\nMax.",font="special13",
            focusTexture=BG_11,
            noFocusTexture=BG_12,
            alignment=self.align)
        self.addControl(self.btn_betmax)

        self.btn_betp = xbmcgui.ControlButton(
            410,370,60,60,"Bet\n+",font="special13",
            focusTexture=BG_11,
            noFocusTexture=BG_12,
            alignment=self.align)
        self.addControl(self.btn_betp)

        self.btn_start = xbmcgui.ControlButton(
            150,300,200,50,"Start Spin",font="special13",
            focusTexture=BG_09,
            noFocusTexture=BG_10,
            alignment=self.align)
        self.addControl(self.btn_start)

        self.btn_stop_all = xbmcgui.ControlButton(
            370,300,200,50,"Stop Spin",font="special13",
            focusTexture=BG_09,
            noFocusTexture=BG_10,
            alignment=self.align)
        self.addControl(self.btn_stop_all)

        self.btn_bonus = xbmcgui.ControlButton(
            260,470,200,50,"Bonus($)",font="special13",
            focusTexture=BG_09,
            noFocusTexture=BG_10,
            alignment=self.align)
        self.addControl(self.btn_bonus)

        self.btn_start.controlUp(self.btn_bonus)
        self.btn_start.controlLeft(self.btn_stop_all)
        self.btn_start.controlRight(self.btn_stop_all)
        self.btn_start.controlDown(self.btn_betm)

        self.btn_stop_all.controlUp(self.btn_bonus)
        self.btn_stop_all.controlLeft(self.btn_start)
        self.btn_stop_all.controlRight(self.btn_start)
        self.btn_stop_all.controlDown(self.btn_betp)

        self.btn_betm.controlUp(self.btn_start)
        self.btn_betm.controlLeft(self.btn_betp)
        self.btn_betm.controlRight(self.btn_betmax)
        self.btn_betm.controlDown(self.btn_bonus)

        self.btn_betmax.controlUp(self.btn_start)
        self.btn_betmax.controlLeft(self.btn_betm)
        self.btn_betmax.controlRight(self.btn_betp)
        self.btn_betmax.controlDown(self.btn_bonus)

        self.btn_betp.controlUp(self.btn_stop_all)
        self.btn_betp.controlLeft(self.btn_betmax)
        self.btn_betp.controlRight(self.btn_betm)
        self.btn_betp.controlDown(self.btn_bonus)

        self.btn_bonus.controlUp(self.btn_betmax)
        self.btn_bonus.controlLeft(self.btn_bonus)
        self.btn_bonus.controlRight(self.btn_bonus)
        self.btn_bonus.controlDown(self.btn_start)

        self.setFocus(self.btn_bonus)

    def default_start_slot(self):
        start_slot1 = choice(slotchoices)
        start_slot2 = choice(slotchoices)
        start_slot3 = choice(slotchoices)
        self.Set_slots1(start_slot1)
        self.Set_slots2(start_slot2)
        self.Set_slots3(start_slot3)
        if (start_slot1 == start_slot2) and (start_slot2 == start_slot3):
            self.focus_slot1 = True
            self.focus_slot2 = True
            self.focus_slot3 = True
            self.win_slot()

    def default_focus_slot(self):
        self.focus_slot1 = False
        self.focus_slot2 = False
        self.focus_slot3 = False
        self.win_slot()

    def win_slot(self):
        self.win_slot1.setVisible(self.focus_slot1)
        self.win_slot2.setVisible(self.focus_slot2)
        self.win_slot3.setVisible(self.focus_slot3)

    def Set_slots1(self, un=""):
        self.slot1.setImage(un)
        #if self.is_started: time.sleep(.05)

    def Set_slots2(self, deux=""):
        self.slot2.setImage(deux)
        #if self.is_started: time.sleep(.05)

    def Set_slots3(self, trois=""):
        self.slot3.setImage(trois)

    def play_game(self):
        if not self.is_started:
            if not self.cash >= self.max_cash:
                while True:
                    if not self.bet == 0:
                        self.is_started = True
                        self.default_focus_slot()
                        if randint(5, 20) < randint(0, 25):
                            randnum1 = randint(0, len(slotchoices)-1)
                            randnum2 = randint(0, len(slotchoices)-1)
                            randnum3 = randint(0, len(slotchoices)-1)
                            self.display1 = slotchoices[randnum1]
                            self.display2 = slotchoices[randnum2]
                            self.display3 = slotchoices[randnum3]
                        else:
                            self.display1 = choice(slotchoices)
                            self.display2 = choice(slotchoices)
                            self.display3 = choice(slotchoices)
                        Sounds("spin.wav")
                        self.Set_slots1(BG_R1)
                        self.Set_slots2(BG_R2)
                        self.Set_slots3(BG_R3)
                        break
                    else:
                        if not self.cash <= 0:
                            self.bet = self.bet + 1
                            self.info_Bet.setLabel("Mi$e\n"+str(self.bet))
                            self.cash = self.cash - 1
                            self.info_cash.setLabel("Ca$h\n"+str(self.cash))
                        else:
                            if xbmcgui.Dialog().yesno(__script__,"Error...\nYour Ca$h is %s, Try again!." % str(self.cash)):
                                self.cash = self.Jackpot/7
                                if self.cash <= 0: self.cash = 250
                                self.info_cash.setLabel("Ca$h\n"+str(self.cash))
                                break
                            else:
                                self.Remove_skin_cache()
                                break

    def onAction(self,action):
        if   action ==  34: # Y button
            if self.is_started: pass
            else: self.play_game()
        elif action ==  10: # BACK button
            if self.is_started: self.stop_all()
            else:
                if xbmcgui.Dialog().yesno(__script__,"Are you sure?\nQuit game."):
                    self.Remove_skin_cache()
        elif action ==   9: self.Bet_minus() # B button
        elif action ==  18: self.Bet_plus()  # X button
        elif action == 117:                  # WHITE button
            b = Bonus()
            b.doModal()
            del b
        #elif (action == 18) and (action == 34): print "Special commande" #MARCHE PAS :(

    def onControl(self, control):
        if control == self.btn_stop_all: self.stop_all()
        elif control == self.btn_betm: self.Bet_minus()
        elif control == self.btn_betp: self.Bet_plus()
        elif control == self.btn_betmax:
            if not self.is_started:
                if self.x2: # It's the special Bonus
                    self.cash = self.cash + self.bet
                    self.bet  = self.bet*2
                    self.cash = self.cash - self.bet
                    if self.cash <= 0: self.cash = 0
                    self.x2 = False #Fixe: One Tour per Win
                    self.btn_betmax.setLabel("Bet\nMax.")
                else:
                    if not self.max_is_betted:
                        self.max_is_betted = True
                        self.cash = self.cash + self.bet
                        if not self.cash < self.max_bet:
                            self.bet  = self.max_bet
                            self.cash = self.cash - self.bet
                        else:
                            self.bet  = self.cash
                            self.cash = self.cash - self.bet
                        self.btn_betmax.setLabel("Max.\nbetted")
                self.info_Bet.setLabel("Mi$e\n"+str(self.bet))
                self.info_cash.setLabel("Ca$h\n"+str(self.cash))
            else: pass
        elif control == self.btn_start:
            if not self.is_started: self.play_game()
            else: pass
        elif control == self.btn_bonus:
            b = Bonus()
            b.doModal()
            del b

    def Bet_minus(self):
        if not self.is_started:
            if not self.bet == 0:
                self.bet = self.bet - 1
                self.info_Bet.setLabel("Mi$e\n"+str(self.bet))
                self.cash = self.cash + 1
                self.info_cash.setLabel("Ca$h\n"+str(self.cash))
                if self.bet < self.max_bet:
                    self.max_is_betted = False
                    self.btn_betmax.setLabel("Bet\nMax.")

    def Bet_plus(self):
        if not self.is_started:
            if not self.cash == 0:
                if not self.bet >= self.max_bet:
                    self.bet = self.bet + 1
                    xbmc.playSFX(coin)
                    self.info_Bet.setLabel("Mi$e\n"+str(self.bet))
                    self.cash = self.cash - 1
                    self.info_cash.setLabel("Ca$h\n"+str(self.cash))
                    if self.bet == self.max_bet:
                        self.max_is_betted = True
                        self.btn_betmax.setLabel("Max.\nbetted")

    def stop_all(self):
        if self.is_started:
            self.Set_slots1(self.display1)
            self.Set_slots2(self.display2)
            self.Set_slots3(self.display3)
            self.display = 3
            self.Stopped_diplay()

    def Stopped_diplay(self):
        if self.is_started:
            if self.display == 3:
                self.display = 0
                self.is_started = False
                self.max_is_betted = False
                self.check_score(self.display1, self.display2, self.display3)
                if not self.winner_pot:
                    if xbmc.Player().isPlaying():
                        try: xbmc.Player().stop()
                        except: pass
                    xbmc.playSFX(os.path.join(skin_cache, "stop.wav"))
                    self.winner_pot = False

    def check_score(self, slot1display, slot2display, slot3display):
        all_slot  = [slot1display, slot2display, slot3display]
        and_add   = 0
        if (slot1display == slot2display) and (slot2display == slot3display):
            #print ''' SAME SLOTS. EXAMPLE: |7|7|7| '''
            if   slot1display == BG_F1: self.gain = self.gain + (self.bet*20)
            elif slot1display == BG_F2: self.gain = self.gain + (self.bet*25)
            elif slot1display == BG_F3: self.gain = self.gain + (self.bet*50)
            elif slot1display == BG_F4:
                self.gain = self.gain + (self.bet*15)
                #xbmc.playSFX(os.path.join(skin_cache, "bell.wav"))
                self.winner_pot = True # FAKE: added bell.wav for playing
            elif slot1display == BG_F5: self.gain = self.gain + (self.bet*10)
            elif slot1display == BG_F6: self.gain = self.gain + (self.bet*20)
            elif slot1display == BG_F7: self.gain = self.gain + (self.bet*5)
            elif slot1display == BG_F8: self.gain = self.gain + (self.bet*10)
            elif slot1display == BG_F9:
                self.gain = self.gain + (self.bet*100)
                xbmc.playSFX(os.path.join(skin_cache, "seven.wav"))
                self.winner_pot = True
                self.win_Jackpot()
            self.focus_slot1 = True
            self.focus_slot2 = True
            self.focus_slot3 = True
            self.win()
            #self.TakeScreenShot()
        elif (BG_F1 in all_slot) and (BG_F2 in all_slot) and (BG_F3 in all_slot):
            #print ''' ANY BAR. EXAMPLE: |B3R|B1R|B2R| '''
            self.gain = self.gain + (self.bet*8)
            self.focus_slot1 = True
            self.focus_slot2 = True
            self.focus_slot3 = True
            self.win()
        elif (slot1display == slot2display) or (slot1display == slot3display) or (slot2display == slot3display):
            #print ''' DOUBLE FOR SEVEN AND CHERRY ONLY OR B?R.'''
            #print ''' EXAMPLE: |7|CHERRY|7| OR |CHERRY|CHERRY|B1R|'''
            if (all_slot[0] == BG_F5) and (all_slot[1] == BG_F5):
                self.gain = self.gain + (self.bet*(5+and_add))
                self.focus_slot1 = True
                self.focus_slot2 = True
                self.win()
            elif (all_slot[0] == BG_F5) and (all_slot[2] == BG_F5):
                if slot2display == BG_F9:
                    and_add   = 5
                    self.focus_slot2 = True
                self.gain = self.gain + (self.bet*(5+and_add))
                self.focus_slot1 = True
                self.focus_slot3 = True
                self.win()
            elif (all_slot[1] == BG_F5) and (all_slot[2] == BG_F5):
                self.gain = self.gain + (self.bet*(5+and_add))
                self.focus_slot2 = True
                self.focus_slot3 = True
                self.win()
            elif (all_slot[0] == BG_F9) and (all_slot[2] == BG_F9):
                if slot2display == BG_F5:
                    and_add   = 1
                    self.focus_slot2 = True
                self.gain = self.gain + (self.bet*(15+and_add))
                self.focus_slot1 = True
                self.focus_slot3 = True
                self.win()
            else: self.double_bar_and_(all_slot)
        elif BG_F5 in all_slot:  self.is_cherry(all_slot)
        elif slot2display == BG_F9:
            #print ''' ONE SEVEN IN CENTER SLOT. EXAMPLE: |Bell|7|B3R| '''
            self.gain = self.gain + (self.bet*5)
            self.focus_slot2 = True
            self.win()
        else: self.lose()

    def double_bar_and_(self, slot):
        #print ''' DOUBLE BAR ONLY.'''
        bar = False
        if (slot[0] == BG_F1 and slot[1] == BG_F1) or (slot[0] == BG_F1 and slot[2] == BG_F1) or (slot[1] == BG_F1 and slot[2] == BG_F1):
            if (BG_F2 in slot) or (BG_F3 in slot):
                self.focus_slot1 = True
                self.focus_slot2 = True
                self.focus_slot3 = True
                bar = True
        elif (slot[0] == BG_F2 and slot[1] == BG_F2) or (slot[0] == BG_F2 and slot[2] == BG_F2) or (slot[1] == BG_F2 and slot[2] == BG_F2):
            if (BG_F1 in slot) or (BG_F3 in slot):
                self.focus_slot1 = True
                self.focus_slot2 = True
                self.focus_slot3 = True
                bar = True
        elif (slot[0] == BG_F3 and slot[1] == BG_F3) or (slot[0] == BG_F3 and slot[2] == BG_F3) or (slot[1] == BG_F3 and slot[2] == BG_F3):
            if (BG_F1 in slot) or (BG_F2 in slot):
                self.focus_slot1 = True
                self.focus_slot2 = True
                self.focus_slot3 = True
                bar = True
        if bar:
            self.gain = self.gain + (self.bet*8)
            self.win()
        else:
            if slot[1] == BG_F9:
                #print ''' ONE SEVEN IN CENTER SLOT. EXAMPLE: |Bell|7|B3R| '''
                self.gain = self.gain + (self.bet*5)
                self.focus_slot2 = True
                self.win()
            elif BG_F5 in slot: self.is_cherry(slot)
            else: self.lose()

    def is_cherry(self, slot):
        #print ''' ONE CHERRY ONLY. EXAMPLE: |?|?|?| '''
        and_add = 0
        if slot[0] == BG_F5:
            if slot[1] == BG_F9:
                and_add   = 5
                self.focus_slot2 = True
            self.focus_slot1 = True
        elif slot[1] == BG_F5: self.focus_slot2 = True
        elif slot[2] == BG_F5:
            if slot[1] == BG_F9:
                and_add  = 5
                self.focus_slot2 = True
            self.focus_slot3 = True
        self.gain = self.gain + (self.bet*(1+and_add))
        self.win()

    def lose(self):
        if self.bet > 25:
            self.bet = 25
        if not self.Jackpot >= 25000:
            self.Jackpot = self.Jackpot + self.bet
            if self.Jackpot > 25000: self.Jackpot = 25000
            self.info_Jackpot.setLabel("Jackpot($): "+str(self.Jackpot))
            self.pot["Jackpot"] = self.Jackpot
            self.Save_Jackpot()
        self.info_Win.setLabel("You lose: "+str(self.bet))
        if self.cash <= 0:
            self.bet  = 0
            self.cash = 0
        if self.cash < self.bet:
            self.bet  = self.cash
            self.cash = 0
        else: self.cash = self.cash - self.bet
        self.info_cash.setLabel("Ca$h\n"+str(self.cash))
        self.info_Bet.setLabel("Mi$e\n"+str(self.bet))
        self.btn_betmax.setLabel("Bet\nMax.")
        self.x2 = False

    def win_Jackpot(self):
        self.gain = self.gain + self.Jackpot
        self.Jackpot = 0
        self.info_Jackpot.setLabel("Jackpot($): $WIN$")
        self.pot["Jackpot"] = self.Jackpot
        self.Save_Jackpot()

    def win(self):
        self.win_slot()
        self.cash = self.cash + self.gain
        self.info_cash.setLabel("Ca$h\n"+str(self.cash))
        self.info_Win.setLabel("You win: "+str(self.gain))
        self.btn_betmax.setLabel("Bet\n(x2)")
        self.x2   = True
        self.gain = 0
        if self.cash >= self.max_cash: xbmcgui.Dialog().ok(__script__,"Sorry...\nYou made jump the casino.\nCa$h %s" % str(self.cash))

    def Load_Jackpot(self):
        test = {"Jackpot":0}
        self.pot = {}
        if os.path.exists(self.tmp_file):
            f = open(self.tmp_file,"rb")
            self.pot = load(f)
            f.close()
        for k in test.keys():
            if not self.pot.has_key(k):
                self.pot[k] = test[k]
        self.Save_Jackpot()

    def Save_Jackpot(self):
        f = open(self.tmp_file,"wb")
        dump(self.pot,f)
        f.close()

    def Remove_skin_cache(self):
        from shutil import rmtree
        try: rmtree(skin_cache)
        except: pass
        self.close()

    def TakeScreenShot(self):
        try:
            if xbmc.Player().isPlaying():
                try: xbmc.Player().stop()
                except: pass
            #time.sleep(1)
            directory = os.path.join(CWD, "screenshot_win")
            if not os.path.exists(directory): os.makedirs(directory)
            now = time.localtime(time.time())
            year, month, day, hour, minute, second, weekday, yearday, daylight = now
            dated = "%02d%02d%02d_%02d%02d%02d" % (year, month, day, hour, minute, second)
            name  = os.path.join(directory, dated)
            screen = {"x":int(self.getWidth()), "y":int(self.getHeight())}
            command = "TakeScreenShot(%s.jpg,0,false,%s,-1,%s)" % (name, screen["x"], screen["y"])
            xbmc.playSFX(os.path.join(skin_cache, "screenshot.wav"))
            xbmc.executehttpapi(command)
        except: pass

#####################################################################################################
''' Class: Bonus '''
#####################################################################################################
class Bonus(xbmcgui.WindowDialog):
    def __init__(self):
        self.setCoordinateResolution(6)

        self.addControl(xbmcgui.ControlImage(0,0,0,0,BG_00))

        self.addControl(xbmcgui.ControlLabel(200,63,0,0,"xbmc media center",'special12',alignment=0x00000001))
        self.addControl(xbmcgui.ControlLabel(207,63,0,0,__script__+" - Bonus($)",'special13'))

        self.addControl(xbmcgui.ControlImage(157,115,200,30,BG_V9))
        self.addControl(xbmcgui.ControlLabel(147,115,0,0,"x 100 +(Jp$)",'font13',alignment=0x00000001))

        self.addControl(xbmcgui.ControlImage(157,150,200,30,BG_V6))
        self.addControl(xbmcgui.ControlLabel(147,150,0,0,"x 15",'font13',alignment=0x00000001))

        self.addControl(xbmcgui.ControlImage(157,185,200,30,BG_V3))
        self.addControl(xbmcgui.ControlLabel(147,185,0,0,"x 5",'font13',alignment=0x00000001))

        self.addControl(xbmcgui.ControlImage(157,220,200,30,BG_V7))
        self.addControl(xbmcgui.ControlLabel(147,220,0,0,"x 50",'font13',alignment=0x00000001))

        self.addControl(xbmcgui.ControlImage(157,255,200,30,BG_V4))
        self.addControl(xbmcgui.ControlLabel(147,255,0,0,"x 25",'font13',alignment=0x00000001))

        self.addControl(xbmcgui.ControlImage(157,290,200,30,BG_V1))
        self.addControl(xbmcgui.ControlLabel(147,290,0,0,"x 20",'font13',alignment=0x00000001))

        self.addControl(xbmcgui.ControlImage(157,325,200,30,BG_V10))
        self.addControl(xbmcgui.ControlLabel(147,325,0,0,"x 8",'font13',alignment=0x00000001))

        self.addControl(xbmcgui.ControlImage(363,115,200,30,BG_V12))
        self.addControl(xbmcgui.ControlLabel(573,115,0,0,"x 20",'font13'))

        self.addControl(xbmcgui.ControlImage(363,150,200,30,BG_V11))
        self.addControl(xbmcgui.ControlLabel(573,150,0,0,"x 15",'font13'))

        self.addControl(xbmcgui.ControlImage(363,185,200,30,BG_V14))
        self.addControl(xbmcgui.ControlLabel(573,185,0,0,"x 10",'font13'))

        self.addControl(xbmcgui.ControlImage(363,220,200,30,BG_V13))
        self.addControl(xbmcgui.ControlLabel(573,220,0,0,"x 5",'font13'))

        self.addControl(xbmcgui.ControlImage(363,255,200,30,BG_V8))
        self.addControl(xbmcgui.ControlLabel(573,255,0,0,"x 10",'font13'))

        self.addControl(xbmcgui.ControlImage(363,290,200,30,BG_V5))
        self.addControl(xbmcgui.ControlLabel(573,290,0,0,"x 5",'font13'))

        self.addControl(xbmcgui.ControlImage(363,325,200,30,BG_V2))
        self.addControl(xbmcgui.ControlLabel(573,325,0,0,"x 1",'font13'))


        self.addControl(xbmcgui.ControlImage(150,360,410,190,BG_07))
        self.addControl(xbmcgui.ControlImage(310,400,100,100,BG_06))
        self.addControl(xbmcgui.ControlImage(310,400,100,100,"black.png"))

        self.addControl(xbmcgui.ControlLabel(170,368,0,0,"Keys Help!","special13","0xDDced8da"))

        self.addControl(xbmcgui.ControlImage(170,400,20,21,BG_K1))
        self.addControl(xbmcgui.ControlLabel(200,400,0,0,"Select ???","font12"))

        self.addControl(xbmcgui.ControlImage(170,430,20,20,BG_K2))
        self.addControl(xbmcgui.ControlLabel(200,430,0,0,"Bet -","font12"))

        self.addControl(xbmcgui.ControlImage(170,460,21,21,BG_K7))
        self.addControl(xbmcgui.ControlLabel(200,460,0,0,"Bet +","font12"))

        self.addControl(xbmcgui.ControlImage(170,490,20,20,BG_K8))
        self.addControl(xbmcgui.ControlLabel(200,490,0,0,"Start Spin","font12"))

        self.addControl(xbmcgui.ControlImage(365,400,18,18,BG_K6))
        self.addControl(xbmcgui.ControlLabel(390,400,0,0,"Infos Bonus($)\nand keys Help!","font12"))

        #self.addControl(xbmcgui.ControlImage(365,430,18,18,BG_K4))
        #self.addControl(xbmcgui.ControlLabel(390,430,0,0,"","font12"))

        self.addControl(xbmcgui.ControlImage(360,460,26,22,BG_K3))
        self.addControl(xbmcgui.ControlLabel(390,460,0,0,"Slots is spin: Stop Spin\nor not spin: Close Lucky7.","font12"))

        #self.addControl(xbmcgui.ControlImage(360,490,26,22,BG_K5))
        #self.addControl(xbmcgui.ControlLabel(390,490,0,0,"","font12"))

        self.addControl(xbmcgui.ControlLabel(0,510,720,0,"Jackpot($) is cumulative. Max: 25000","font12",alignment=0x00000002))

    def onAction(self, action):
        if   action ==  9: self.close() # B button
        elif action == 10: self.close() # BACK button

if __name__ == "__main__":
    w = None
    w = __Lucky7__()
    w.doModal()
    del w
