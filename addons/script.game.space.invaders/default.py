# Space Invaders for XBMC Python
# Version: 0.98a

"""
	URL: http://members.ozemail.com.au/~darkdonno/?p=projects/space_invaders  [Current]
	Help URL: http://darkdonno.googlepages.com/si-manual
	Forum Py Dev: http://www.xboxmediacenter.com/forum/showthread.php?t=20054
	Forum Support: http://www.xboxmediacenter.com/forum/showthread.php?p=119450

	Coder: Donno    [darkdonno@gmail.com] or on Freenode in #xbmc as Donno
	Graphics: Project Mayhem III and Splash by ChokeManiac  [Do not Contact him, he is not assocated with this project]

	Note to Theme creators if you have any please email them to me so i can include them with the next release of Space Invaders
	Themes are for the game play. Don't modify the actual GUI skin
"""

"""
	Versioning  is 0.9xyz (x = the version,  y = means test pretty much so inbetween versions (if not present its means its 'Stable/Working',   z just means i don't want to release a inbetween as its more or less just a fix/optomized version)

	About:
		Project Started around April/May 2006.
		An attempt to show the true power in combining XBMC with Python.
		So I decide to choose to make  Space Invaders Remake
		I will not release the script till I think its full ready for public use.
		Check the web page for a few avi (which are WIP showing the progress)

	Feature List:
		Themes - Incomplete (Coded but not Made, code needs improving)
		Background Music - Optional 'Overwrite music' with Custom Playlist.pls in Music folder
		Highscore Loading from Internet/Local
		Standard Objects: Red Bonus Saucer, Shields, Invaders
		Collision Dectection between Friendly and Emeny bullet
		Every 1000 score will give you an extra life
		Added Check for Theme Media
		Invader fire at you and the shields
		Settings - Options
		Special Effect Sounds
		Pause
		AutoPause when you go to Full Screen Video/Viz
		GameOver Screens  ('Splash' Full Screen picture)  - Out Of Lifes and Invaders have landed
		Save Settings to Profile (p:\\) and  Local Scores to t:\\

	Setting List:
		-> Use Internet (this is need to submit highscores to internet, and version checker/updater)
		-> VersionOnStartup (this  requires use internet to be on so it will check the net for the latest version)
		-> Track High Scores(this may use internet if enabled)
		-> Use Name Name (this requires Track highscores to be enabled as well)
		-> Set Password for internet score (if none just enter anything)
		-> Sound Effects

	- 30th of Janr 2010 (0.98a)
		- Changed: version 0.98 to 0.98a
		- Fixed: textXOffset to textOffsetX in xbmcgui.ControlButton
		- Fixed/changed: old protocol not work on win32 (p:\\) and  t:\\ now use special://profile/script_data/Space Invaders/
		- Added: French Language
		- Changed: outdated ControlCheckMark -->> ControlRadioButton
		- Added: keyboard spacebar for onFire
		- removed: xbmc.enableNavSounds, because not work on win32, but wors on XBox

	- 16th of Janr (0.98)
		- Fixes - m3u, slowdowns
		- Added Swedish Language

	- 22th of Decemeber (0.97)
		- Offical Release

	- 14th of Demember
		- Finshed the invader landed section
		- fixed a bug found due to the invader landed section being incomplete (lifes were getting reset when u go to next level)

	- Changes 23/24 of September (0.961)
		- Changed DefaultName is now nickname
		- Added Inital Support for new internet scores (Viewing and Settings work)
		- LocalScore Fixed and Improved now its COOL even if i do say so my self
		- Highscore Internet Submission added

	- Changes 2 of September (0.96)
		- Disabled HighScore stuff for public release [ As of 0.961 this was fixed]

	- Since 0.951  (in order from done first)
		- Localaziation started
		- Settings now its own window

	- Changes 14 of July
		- Fixed thread (IVB) it was sleeping now changed so it sleeps shorter and does a count
		- Fixed Bugs
		- Changed Game Over Screens

	-- Changes 12 of July (.9498)
		- Optomized the Invader Thread Class
			- Did too many for x in range 0 to 11 so now just do it once and have combined the checks in ehre
		-  Improved Collistion detection between  Invaders bullets and shields is now 100% better

	-- Changes  11th of July
		- New Toast System
		- Speed up Closing down of script
		- Replaced B/Back button Dialog YesNo with homemade one

	-- Changes Since 0.948
		- Settings Menu now shows Under with the rest of the stuff
		- Pause
		- Splash for Out of lifes and invaders have landed

	-- Changes Since 0.947
		- Changed Starting Location. you now start on left side of shields, and invaders start on right side
		- When u get shot u are teleported to the left.

	TODO LIST:
		Manual Page [EXT: WWW]
		Themes [EXT: GFX]
		Sounds [EXT: WAV]
"""

__title__ = "Space Invaders"
__addonID__ = "script.game.space.invaders"
__version__ = '0.98a'
__coder__ = 'Donno'
__author__ = 'Donno [darkdonno@gmail.com]'
__date__ = 'April/May/June 2006'
__maintaner__ = 'Donno'
__credits__ = 'Coded by Donno\nSplash Screen and GUI Graphics by ChokeManiac'
__extcredits__ = 'Splash Screen and GUI Graphics by ChokeManiac\nThanks to RockStar for his language code and Jezz_X for suggesting the Control screen and BlackBolt for his Controller buttons.\n\nSpace Invaders live again for XBMC :) Tested on win32 and XBox, Not tested on other OS! By Frost 30-01-10.'

#---Start of Imports ---#000000#FFFFFF-----------------------------------------
import os.path # For Reading Path
import xbmc,xbmcgui # For XBMC
import re #,shutil  # Regregssin and File Operations
import urllib  # For Internet Operations
from time import sleep # For the Gaming Stuff
from threading import * # For the Gaming Stuff
import thread
from random import randint # For the Gaming Stuff (Random)
from sys import path
try: Emulating = xbmcgui.Emulating
except: Emulating = False

## Buttons to ID
ACTION_BACK = 10
ACTION_WHITE = 117
ACTION_DPAD_LEFT = 1
ACTION_DPAD_RIGHT = 2
ACTION_DPAD_UP = 3
ACTION_DPAD_DOWN = 3
ACTION_START = 122
ACTION_A = 7
ACTION_B = 9
ACTION_X = 18
ACTION_Y = 34
ACTION_REMOTE_INFO = 11
ACTION_TRIGGER_LEFT = 111
ACTION_TRIGGER_RIGHT = 112
BUTTON_BLACK = 260
BUTTON_LEFTHUMB_LEFT = 282
BUTTON_LEFTHUMB_UP = 280
BUTTON_LEFTHUMB_RIGHT = 283

## Some Standard Varibles
LEFT_X = 48
RIGHT_X = 592

STARTING_X = 96

YOUR_Y = 520
SHIELD_Y = 416
BONUS_Y = 90
MD = 20 # posy it moves down per line
#MS = 16 # posx it moves left/right per time
MS = 10 # posx it moves left/right per time
#LINES_Y = [0,100,135,170,205,240]
LINES_Y = [0,112,144,176,208,240]
SHEILDS_X = [128,256,384,512]
TOP_Y = 110
BASE_SPEED = .008 # For Bullets
BASE_SPEED_A = .05 # For Invaders 1.25   [ 0.15 is a good speed for maybe 5 of them left,    0.8 for 3 and 0.1 for none
BASE_SPEED_B = .025

SYSTEM_URL = "http://members.ozemail.com.au/~darkdonno/si/system.php" # For test/now   until i get real hosting :D
SETTINGS = {}
GAME_ID = ""
USER_ID = "0"
DEBUG = 0


SPECIAL_PROFILE_DIR = xbmc.translatePath( "special://profile/" )
SPECIAL_SCRIPT_DATA = os.path.join( SPECIAL_PROFILE_DIR, "addon_data", __addonID__ )
if not os.path.isdir( SPECIAL_SCRIPT_DATA ): os.makedirs( SPECIAL_SCRIPT_DATA )
SPACEINVADER_SETTINGS = os.path.join( SPECIAL_SCRIPT_DATA, "spaceinvader_settings.xml" )
SPACEINVADER_SCORES = os.path.join( SPECIAL_SCRIPT_DATA, "spaceinvader_scores.txt" )


Root = os.getcwd().replace(";","")+"\\"
ThemeFolder = Root+"Themes\\"
LangFolder = Root+"Languages\\"
## File Lists
theimages = ["splash.jpg","progress_back2.png","progress_over.png","progress_mid.png","background-plain.png","button-focus.png","button-nofocus.png","dialog-panel2.png","Scan-panel-bg.png","panel-bg.png","dialog-panel2.png","ControlBlocks.png","keyboard-btn-backspace.png","keyboard-btn-backspace-focus.png","check-box.png","check-boxNF.png","list-focus.png","list-nofocus.png","Btn_a.png","Btn_b.png","Btn_y.png","seperator.png","btn_dpad.png","btn_start.png","btn_back.png"]
thegameimages = ['vadertop_f1.png','vadertop_f2.png','vaderbottom_f1.png','vaderbottom_f2.png','vadermid_f1.png','vadermid_f2.png','background-plain.png','bonus.png','bullet.png','life.png','me.png','s1.png','s2.png','s3.png','s4.png','s5.png',"ebullet_f0.png","ebullet_f1.png","gotshot.png","gameover.png","gameover-landed.png","paused.png"]

UPDATERSTRING = "from shutil import rmtree\nimport xbmc, xbmcgui\nrmtree('%s')\nxbmc.executebuiltin('XBMC.Extract(E:\\si.zip,%s)')\nxbmc.executehttpapi('FileDelete(E:\\si.zip)')\nxbmcgui.Dialog().ok('Space Invaders','New Version Extraction')" % (Root.replace("\\","\\\\"),Root.replace("\\","\\\\"))

## GUI Functions
fc = "0xFFFFFFFF"
## Global Varibles
global bgMusic
bgMusic = 0

path.append(Root)

path.append(Root+"winpdb-1.0.6")
#import rpdb2; rpdb2.start_embedded_debugger("password",1)

if not Emulating:
	import onlinehighscores
	ONLINEHIGHSCORE=onlinehighscores.highscore()
#---Start of ControlBlock Class ---#000000#FFFFFF-----------------------------------------
class ControlBlock:
	"""
		Creates and Controls a ControlBlock Class
	"""
	def __init__(self,x,y,w,h,win,txtpath,gap=0,CBfc=fc,a="vert"):
		"""
			Previously known as the SetupButton function
				Usage variable = ControlBlock(x,y,width,height,window,gap)
		"""
		self.numbut  = 0
		self.win = win
		self.butx = x
		self.starty = y
		self.buty = y
		self.butwidth = w
		self.butheight = h
		self.font_color = CBfc
		self.butalign = a
		self.tp = txtpath
		self.buttonf = "button-focus.png"
		self.buttonnf = "button-nofocus.png"
		self.gap = gap
	def AddButton(self,text,ext_gap=0,voc=1,align=4,w=""):
		try:
			if text == int(text):
				text = lang.string(text)
		except:
			pass # meaning its doesn't contain numbers at all :)
		if self.butalign == "vert":
			self.buty = self.buty + ext_gap
			newy = self.buty + self.numbut * self.butheight + self.gap * self.numbut
			if w != "":
				self.butwidth = w
			c = xbmcgui.ControlButton(self.butx ,newy,self.butwidth,self.butheight,text,self.tp+self.buttonf,self.tp+self.buttonnf,textOffsetX=25,textColor=self.font_color,font="font14",alignment=align)
		else:
			self.butx = self.butx + ext_gap
			newx = self.butx + self.numbut * self.butwidth + self.gap * self.numbut
			if w != "": self.butwidth = w
			c = xbmcgui.ControlButton(newx,self.buty,self.butwidth,self.butheight,text,self.tp+self.buttonf,self.tp+self.buttonnf,textOffsetX=25,textColor=self.font_color,font="font14",alignment=align)
		self.win.addControl(c)
		c.setVisible(voc)
		self.numbut += 1
		return c
	def AddCM(self,text,ext_gap=0,voc=1):
		if text == int(text):
			text = lang.string(text)
		self.buty = self.buty + ext_gap
		c = xbmcgui.ControlRadioButton(
			self.butx,
			self.buty + (self.numbut * self.butheight + self.gap*self.numbut),
			self.butwidth,
			self.butheight,
			text,
			self.tp+self.buttonf,
			"",
			textOffsetX=25,
			textColor=self.font_color,
			font="font12",
            TextureRadioFocus=self.tp+"check-box.png",
            TextureRadioNoFocus=self.tp+"check-boxNF.png")
		self.win.addControl(c)
		c.setVisible(voc)
		self.numbut += 1
		return c
	def ButSetTex(self,texture_focus,texture_nofocus):
		self.buttonf = texture_focus
		self.buttonnf = texture_nofocus
	def ButSetPos(self,c,butx,nw=0,ext_gap=0):
		self.buty = self.buty + ext_gap
		c.setPosition(butx,self.buty + (self.numbut * self.butheight + self.gap*self.numbut))
		if nw != 0:
			c.setWidth(nw)
		self.numbut += 1
		return c

#---Language Class by RockStar and tweaked by Donno--#000000#FFFFFF-----------------------------------------
class Language:
	"""
		Language Class
			For reading in xml for automatiacall of the selected lanauge XBMC is running in
			And for returning the string in the given Language for a specified id
		Oringally Coded by Rockstar, Recoded by Donno :D
	"""
	def load(self,thepath):
		self.strings = {}
		tempstrings = []
		self.language = xbmc.getLanguage().lower()
		if os.path.exists(thepath+self.language+"\\strings.xml"):
			self.foundlang = self.language
		else:
			self.foundlang = "english"
		self.langdoc = thepath+self.foundlang+"\\strings.xml"
		print "-Loading Language: " + self.foundlang
		try:
			f=open(self.langdoc,'r')
			tempstrings=f.read()
			f.close()
		except:
			print "Error: Languagefile "+self.langdoc+" cant be opened"
			xbmcgui.Dialog().ok(__title__,"Error","Languagefile "+self.langdoc+" cant be opened")
		self.exp='<string id="(.*?)">(.*?)</string>'
		self.res=re.findall(self.exp,tempstrings)
		for stringdat in self.res:
			self.strings[int(stringdat[0])] = str(stringdat[1])

	def string(self,number):
		if int(number) in self.strings:
			return self.strings[int(number)]
		else:
			return "unknown string id"

#---Shield Block Class Here ---#000000#FFFFFF-----------------------------------------
class SBlock: ## Shield Block Code
	"""
		ShieldBlock - maintains the X,Y and state of a piece of the shield.
		var = ShieldBlock(self,x,y,w)
	"""
	def __init__(self,x,y,w):
		self.power = 1
		self.x = x
		self.y = y
		self.w = w
		self.ctrl = xbmcgui.ControlImage(x, y, 16, 16, Root+"Themes\\"+MEDIA_FOLDER+"s1.png")
		w.addControl(self.ctrl)

	def shoot(self):
		self.power += 1
		tex = "%s%ss%s.png" % (Root,"Themes\\"+MEDIA_FOLDER,(self.power))
		#self.ctrl = xbmcgui.ControlImage(self.x, self.y, 16, 16, tex)
		self.ctrl.setImage(tex)

	def destoryme(self):
		self.power = 5
		tex = "%s%ss%s.png" % (Root,"Themes\\"+MEDIA_FOLDER,(self.power))
		self.ctrl.setImage(tex)

	def newLevel(self):
		self.power = 1
		tex = "%s%ss%s.png" % (Root,"Themes\\"+MEDIA_FOLDER,(self.power))
		self.ctrl.setImage(tex)

class MyDialogSelect(xbmcgui.WindowDialog):
	"""
		My Dialog Select - Don't really like the stock one in PMIII so did it in python instead :D
	"""
	def __init__(self,title=__title__,mylist=[]):
		if Emulating: xbmcgui.WindowDialog.__init__(self)
		self.setCoordinateResolution(6)
		self.addControl(xbmcgui.ControlImage(150, 180, 450,300, Root+"images\\dialog-panel2.png"))
		self.value = -1
		self.addControl(xbmcgui.ControlLabel(190, 200, 370,30,title,font="special13",textColor="DDced8da"))
		self.select_listcontrol = xbmcgui.ControlList(190,240,370,240,"font13",fc,buttonFocusTexture= Root+"images\\list-focus.png",buttonTexture= Root+"images\\list-nofocus.png")
		self.addControl(self.select_listcontrol)
		self.select_listcontrol.reset()
		for x in mylist:
			self.select_listcontrol.addItem(x)
		self.setFocus(self.select_listcontrol)

	def onControl(self,control):
		if self.select_listcontrol == control:
			self.value = self.select_listcontrol.getSelectedPosition()
			self.close()
	def onAction(self,a):
		if a == ACTION_BACK:
			self.value = -1
			self.close()
		elif a == ACTION_B:
			self.value = -1
			self.close()

class MyDialogYesNo(xbmcgui.WindowDialog):
	"""
		My Dialog YesNo - This will replace the built in Dialogs once i do pause :D I hope
	"""
	def __init__(self,title=__title__,line1="",line2="",line3="",mode=0):
		if Emulating: xbmcgui.WindowDialog.__init__(self)
		self.setCoordinateResolution(6)
		xbmcgui.lock()
		self.addControl(xbmcgui.ControlImage(165, 205, 390,190, Root+"images\\dialog-panel2.png"))
		self.value = -1
		self.mode = mode
		self.addControl(xbmcgui.ControlLabel(190, 218, 370,30,title,font="special13",textColor="DDced8da"))

		self.addControl(xbmcgui.ControlLabel(190, 260, 370,30,line1,font="font10",textColor="0xFFFFFFFF"))
		self.addControl(xbmcgui.ControlLabel(190, 280, 370,30,line2,font="font10",textColor="0xFFFFFFFF"))
		self.addControl(xbmcgui.ControlLabel(190, 300, 370,30,line3,font="font10",textColor="0xFFFFFFFF"))
		if mode == 1:
			self.btnOkay = xbmcgui.ControlButton(285, 330,157,32,lang.string(17),font="font10",textColor="0xFFFFFFFF",focusTexture=Root+"\\Images\\keyboard-btn-backspace-focus.png",noFocusTexture=Root+"\\Images\\keyboard-btn-backspace.png",alignment=6)
			self.addControl(self.btnOkay)
			self.setFocus(self.btnOkay)
		else:
			self.btnNo = xbmcgui.ControlButton(365, 330,77,32,lang.string(16),font="font10",textColor="0xFFFFFFFF",focusTexture=Root+"\\Images\\keyboard-btn-backspace-focus.png",noFocusTexture=Root+"\\Images\\keyboard-btn-backspace.png",alignment=6)
			self.btnYes = xbmcgui.ControlButton(285, 330, 77,32,lang.string(15),font="font10",textColor="0xFFFFFFFF",focusTexture=Root+"\\Images\\keyboard-btn-backspace-focus.png",noFocusTexture=Root+"\\Images\\keyboard-btn-backspace.png",alignment=6)
			self.addControl(self.btnYes)
			self.addControl(self.btnNo)
			self.btnNo.controlLeft(self.btnYes)
			self.btnYes.controlRight(self.btnNo)
			self.btnNo.controlRight(self.btnYes)
			self.btnYes.controlLeft(self.btnNo)
			self.setFocus(self.btnNo)
		xbmcgui.unlock()
	def onAction(self,a):
		if a == ACTION_BACK:
			self.value = 0
			self.close()
		elif a == ACTION_START:
			self.value = 1
			self.close()
	def onControl(self,control):
		if self.mode == 1:
			if control == self.btnOkay:
				self.value = 1
				self.close()
		else:
			if control == self.btnYes:
				self.value = 1
				self.close()
			else:
				self.value = 0
				self.close()

class MyDialogYesNoOkLite(xbmcgui.WindowDialog):
	"""
		My Dialog YesNo Lite - This will replace the built in Dialogs for gameover once i do pause
	"""
	def __init__(self,mode=0,posx=265,posy=320):
		if Emulating: xbmcgui.WindowDialog.__init__(self)
		self.setCoordinateResolution(6)
		self.addControl(xbmcgui.ControlImage(posx, posy, 157+40,52, Root+"images\\Scan-panel-bg.png"))
		self.value = -1
		self.mode = mode
		if mode == 0:
			self.btnYes = xbmcgui.ControlButton(posx+140, posy+10,77,32,lang.string(15),font="font10",textColor="0xFFFFFFFF",focusTexture=Root+"\\Images\\keyboard-btn-backspace-focus.png",noFocusTexture=Root+"\\Images\\keyboard-btn-backspace.png",alignment=6)
			self.btnNo = xbmcgui.ControlButton(posx+20, posy+10, 77,32,lang.string(16),font="font10",textColor="0xFFFFFFFF",focusTexture=Root+"\\Images\\keyboard-btn-backspace-focus.png",noFocusTexture=Root+"\\Images\\keyboard-btn-backspace.png",alignment=6)
			self.addControl(self.btnYes)
			self.addControl(self.btnNo)
			self.btnYes.controlLeft(self.btnNo)
			self.btnNo.controlRight(self.btnYes)
			self.setFocus(self.btnNo)
		else:
			self.btnOkay = xbmcgui.ControlButton(posx+20, posy+10,157,32,lang.string(17),font="font10",textColor="0xFFFFFFFF",focusTexture=Root+"\\Images\\keyboard-btn-backspace-focus.png",noFocusTexture=Root+"\\Images\\keyboard-btn-backspace.png",alignment=6)
			self.addControl(self.btnOkay)
			self.setFocus(self.btnOkay)

	def onAction(self,a):
		if a == ACTION_BACK:
			self.value = -1
			self.close()

	def onControl(self,control):
		if self.mode != 0:
			self.close()
		else:
			print "To Be Coded" # eg yes and no will do if i use it

class MyDialogGamePad(xbmcgui.WindowDialog):
	"""
		My Dialog GamePad - The one in XBMC is only for doing passwords so though might as well make it in python :D
	"""
	def __init__(self,title=__title__,line1="",line2=""):
		if Emulating: xbmcgui.WindowDialog.__init__(self)
		self.setCoordinateResolution(6)
		self.addControl(xbmcgui.ControlImage(165, 205, 390,190, Root+"images\\dialog-panel2.png"))
		self.value = -1
		self.addControl(xbmcgui.ControlLabel(190, 218, 370,30,title,font="special13",textColor="DDced8da"))
		self.addControl(xbmcgui.ControlLabel(190, 260, 350,30,line1,font="font10",textColor="0xFFFFFFFF"))
		self.addControl(xbmcgui.ControlLabel(190, 280, 350,30,line2,font="font10",textColor="0xFFFFFFFF"))
		self.code = xbmcgui.ControlFadeLabel(190, 300, 350,30,font="font12",textColor="0xFFFFFFFF")
		self.addControl(self.code)
		self.code.addLabel("A B  Y X ")
		self.thecode = ""
		self.addControl(xbmcgui.ControlLabel(190, 340, 350,30,lang.string(40),font="font10",textColor="0xFFFFFFFF"))
	def coder(self,a):
		#if a == ACTION_BACK:
		#    #return "[Back] "
		if a == ACTION_WHITE: return "[White] "
		elif a == ACTION_A: return "[A] "
		elif a == ACTION_B: return "[B] "
		elif a == ACTION_X: return "[X] "
		elif a == ACTION_Y: return "[Y] "
		elif a == ACTION_REMOTE_INFO: return "[Y] "
		elif a == ACTION_DPAD_LEFT: return "[Right] "
		elif a == ACTION_DPAD_RIGHT: return "[Left] "
		elif a == ACTION_DPAD_UP: return "[Up] "
		elif a == ACTION_DPAD_DOWN: return "[Down] "
		elif a == ACTION_TRIGGER_LEFT: return "[< Trigger] "
		elif a == ACTION_TRIGGER_RIGHT: return "[> Trigger] "
		#elif a.getButtonCode() == BUTTON_BLACK: return "[Black]"
		elif a == 0: return ""
		else:
			pass
			return "[]"

	def onAction(self,a):
		if a == ACTION_BACK:
			self.value = -1
			self.close()
		else:
			self.thecode += self.coder(a)
			self.code.reset()
			self.code.addLabel(self.thecode)

		# every other action record and translate into string and add to the value string

class MyMediaPlayer(xbmcgui.WindowDialog):
	"""
		My Media Player - Controls the Media Player side of XBMC (so u don't have to quit :D)
		Not Localized
	"""
	def __init__(self,title=__title__):
		if Emulating: xbmcgui.WindowDialog.__init__(self)
		self.setCoordinateResolution(6)


		self.addControl(xbmcgui.ControlImage(150, 180, 450,270, Root+"images\\dialog-panel2.png"))
		self.addControl(xbmcgui.ControlLabel(190, 200, 370,30,("%s - Media Player" % title),font="special13",textColor="DDced8da"))
		self.songinfo = xbmcgui.ControlFadeLabel(190, 240, 370,30,"special13","DDced8da")
		self.addControl(self.songinfo)
		self.songinfo.addLabel("Currently Playing: $INFO[MusicPlayer.Artist] - $INFO[MusicPlayer.Title]")


		self.CB_MPlayer = ControlBlock(210,300, 90, 35,self,Root+"\\Images\\",a="horz")

		self.btnPause = self.CB_MPlayer.AddButton('Pause',align=6)
		self.btnStop = self.CB_MPlayer.AddButton('Stop',align=6)
		self.btnSelPL = self.CB_MPlayer.AddButton('Select Playlist',align=6,w=150)

		self.btnPause.setNavigation(self.btnPause,self.btnPause,self.btnSelPL,self.btnStop)
		self.btnStop.setNavigation(self.btnStop,self.btnStop,self.btnPause,self.btnSelPL)
		self.btnSelPL.setNavigation(self.btnSelPL,self.btnSelPL,self.btnStop,self.btnPause)

		self.setFocus(self.btnPause)

	def onControl(self,control):
		if control ==  self.btnPause:
			xbmc.Player().pause()
		elif control ==  self.btnStop:
			xbmc.Player().stop()
		elif control == self.btnSelPL:

			test = xbmcgui.Dialog().browse(1,"%s: Select Playlist" % (__title__),"music") #,".pls|.m3u")
			xbmc.Player().play(test)
	def onAction(self,a):
		if a == ACTION_BACK:
			self.close()
		elif a == ACTION_B:
			self.close()

#--- Main Menu Window/Class---#000000#FFFFFF-----------------------------------------
class MainMenu(xbmcgui.Window):
	"""
		The Main Menu - Window that Contains Start, Settings, Highscore and About.
	"""
	def __init__(self):
		if Emulating: xbmcgui.Window.__init__(self)
		xbmcgui.lock()
		self.base_width = 720
		self.base_height = 576
		self.inisb = 260
		self.dosplash = 1

		self.showSettings = 0
		self.HSCA = 0

		self.setmode = 0
		#1024x768
		self.setCoordinateResolution(6)
		cr = self.getResolution()
		# next 4 lines correct the aspect ratio (if its 4:3 it will do normal, if its  16:9 then add 100 each side
		if cr == 2 or cr == 4 or cr == 6 or cr == 8:
			self.splash  = xbmcgui.ControlImage(0, 0, self.base_width ,self.base_height, Root+"images\\splash.jpg",aspectRatio=2)
		else:
			self.splash  = xbmcgui.ControlImage(100, 6, self.base_width-100*2 ,self.base_height-12, Root+"images\\splash.jpg",aspectRatio=0)

		self.bgset =xbmcgui.ControlImage(235, 130, 250, 200, Root+"images\\dialog-panel2.png")
		self.ihb = (xbmcgui.ControlTextBox(170,320,405,225,"font13",fc))
		self.hs = (xbmcgui.ControlList(170,325,395,200,"font13",fc,buttonFocusTexture= Root+"images\\list-focus.png",buttonTexture= Root+"images\\list-nofocus.png"))
		self.hsl = (xbmcgui.ControlLabel(170,425,395,30,lang.string(51),fc,alignment=2))
		self.cb = xbmcgui.ControlImage(150, 320, 455,232, Root+"images\\ControlBlocks.png",aspectRatio=1)
		self.lblsettings = xbmcgui.ControlLabel(170, 320, 395, 30,lang.string(2),font="font13",alignment=2)

		# ControlBlock
		self.cb2 = []
		self.cb2.append(xbmcgui.ControlLabel(170, 320, 196, 30,lang.string(43),font="font13",alignment=2))
		self.cb2.append(xbmcgui.ControlLabel(170+198, 320, 196, 30,lang.string(44),font="font13",alignment=2))
		self.cb2.append(xbmcgui.ControlImage(170+198, 315, 5, 215, Root+"images\\seperator.png"))
		self.cb2.append(xbmcgui.ControlImage(170, 350,32,32, Root+"images\\Btn_a.png"))
		self.cb2.append(xbmcgui.ControlLabel(170+170, 350, 150,30,lang.string(45),font="font13",textColor="0xFFFFFFFF",alignment=5))
		self.cb2.append(xbmcgui.ControlImage(170, 390,32,32, Root+"images\\Btn_b.png"))
		self.cb2.append(xbmcgui.ControlLabel(170+35, 390+8, 10, 30,"&",font="font13",alignment=2))
		self.cb2.append(xbmcgui.ControlImage(170+35+15, 390,32,32, Root+"images\\btn_back.png"))
		self.cb2.append(xbmcgui.ControlLabel(170+170, 390, 150,30,lang.string(46),font="font13",textColor="0xFFFFFFFF",alignment=5))
		self.cb2.append(xbmcgui.ControlImage(170, 430,32,32, Root+"images\\btn_start.png"))
		self.cb2.append(xbmcgui.ControlLabel(170+170, 430, 150,30,lang.string(0),font="font13",textColor="0xFFFFFFFF",alignment=5))
		self.cb2.append(xbmcgui.ControlImage(170, 470,34,34, Root+"images\\btn_dpad.png"))
		self.cb2.append(xbmcgui.ControlLabel(170+170, 470, 150,30,lang.string(47),font="font13",textColor="0xFFFFFFFF",alignment=5))
		self.cb2.append(xbmcgui.ControlImage(545, 350,32,32, Root+"images\\Btn_a.png"))
		self.cb2.append(xbmcgui.ControlLabel(400, 350, 150,30,lang.string(48),font="font13",textColor="0xFFFFFFFF",alignment=4))
		self.cb2.append(xbmcgui.ControlLabel(545-15, 390+8, 10, 30,"&",font="font13"))
		self.cb2.append(xbmcgui.ControlImage(545, 390,32,32, Root+"images\\Btn_b.png"))
		self.cb2.append(xbmcgui.ControlImage(545-35-15, 390,32,32, Root+"images\\btn_back.png"))
		self.cb2.append(xbmcgui.ControlLabel(400, 390, 150,30,lang.string(3),font="font13",textColor="0xFFFFFFFF",alignment=4))
		self.cb2.append(xbmcgui.ControlImage(545, 430,32,32, Root+"images\\btn_y.png"))
		self.cb2.append(xbmcgui.ControlLabel(400, 430, 150,30,lang.string(49),font="font13",textColor="0xFFFFFFFF",alignment=4))

		self.addControl(self.splash)
		xbmcgui.unlock()

	def createControls(self):
		self.addControl(xbmcgui.ControlImage(0, 0, self.base_width, self.base_height, Root+"images\\background-plain.png"))
		self.addControl(xbmcgui.ControlLabel(90, 80, self.base_width, self.base_height, __title__ + ": " + __version__,font="font14",textColor=fc))
		self.addControl(xbmcgui.ControlImage(140, 310, 465, 240, Root+"images\\dialog-panel2.png"))

		self.addControl(self.bgset)
		self.bgset.setVisible(0)

		self.CB_MainMenu = ControlBlock(self.inisb,130, 200, 35,self,Root+"\\Images\\",8)

		self.addControl(self.ihb)
		self.addControl(self.hs)
		#self.addControl(self.hsl)
		self.ihb.setText("%s %s\n%s: %s\n%s: %s\n%s" % (lang.string(12),__title__,lang.string(13),__version__,lang.string(14),__coder__,__extcredits__))

		self.addControl(self.lblsettings)
		self.lblsettings.setVisible(0)
		for c in self.cb2:
			self.addControl(c)
			c.setVisible(0)

		self.btnStart = self.CB_MainMenu.AddButton(0)
		self.btnHS = self.CB_MainMenu.AddButton(1)
		self.btnSettings = self.CB_MainMenu.AddButton(2)
		self.btnQuit = self.CB_MainMenu.AddButton(3)

		self.createNavigation()
		self.togNav(self.ihb)

		self.addControl(self.cb)
		self.ihb.setVisible(1)
		self.hs.setVisible(0)
		self.hsl.setVisible(0)
		self.cb.setVisible(0)

	def createNavigation(self):
		self.btnStart.controlUp(self.btnQuit)
		self.btnHS.controlUp(self.btnStart)
		self.btnSettings.controlUp(self.btnHS)
		self.btnQuit.controlUp(self.btnSettings)

		self.btnStart.controlDown(self.btnHS)
		self.btnHS.controlDown(self.btnSettings)
		self.btnSettings.controlDown(self.btnQuit)
		self.btnQuit.controlDown(self.btnStart)


		self.ihb.controlLeft(self.btnStart)
		self.ihb.controlRight(self.btnStart)
		self.hs.controlLeft(self.btnStart)
		self.hs.controlRight(self.btnStart)

	def togNav(self,c):
		self.btnStart.controlLeft(c)
		self.btnHS.controlLeft(c)
		self.btnSettings.controlLeft(c)
		self.btnQuit.controlLeft(c)
		self.btnStart.controlRight(c)
		self.btnHS.controlRight(c)
		self.btnSettings.controlRight(c)
		self.btnQuit.controlRight(c)

	def onAction(s,a):
		if a == ACTION_BACK:
			if not s.dosplash:
				s.closeme()
		elif a == ACTION_B:
			if not s.dosplash:
				s.closeme()
		else:
			if s.dosplash:
				s.dosplash = 0
				xbmcgui.lock()
				s.removeControl(s.splash)
				s.createControls()
				xbmcgui.unlock()
				#sinme([s.s,s2,s3,s3,s4],0,720,1,200,0.8,288,mode=1,offset=34,t=0.006)
				#sinme([s.s,s2,s3,s3,s4],0,760,1,200,0.8,288,mode=1,offset=34,t=0.006)
				s.setFocus(s.btnStart)
				if (SETTINGS['trackhighscores']  == 1 and SETTINGS['usenet'] == 1):
					if USER_ID == "0":
						MyDialogLoader(4,__title__,lang.string(52),lang.string(53),lang.string(54))
			else:
				if a == ACTION_START:
					s.loadGame()
				#pass  #print a

	def onControl(s, c):
		if c == s.btnQuit:
			s.closeme()
		elif c == s.btnStart:
			s.loadGame()
		elif c == s.btnSettings:
			s.settingMnu = SettingsMenu()
			s.settingMnu.doModal()
			del s.settingMnu
		elif c == s.btnHS:
			s.showSettings == 0
			s.Cylce()
			s.setFocus(s.btnHS)

	def Cylce(self):
		if self.HSCA == 0:
			self.HSCA = 1
			self.btnHS.setLabel(lang.string(4)) # HighScore
			self.ihb.setVisible(0)
			self.hsl.setVisible(0)
			self.hs.setVisible(0)
			#self.cb.setVisible(1)
			for c in self.cb2:
				c.setVisible(1)
			self.togNav(self.btnStart)
		elif self.HSCA == 1:
			self.HSCA = 2
			self.loadHS(SETTINGS['usenet'])
			self.btnHS.setLabel(lang.string(5))   #"About"
			self.ihb.setVisible(0)
			self.hs.setVisible(1)
			self.hsl.setVisible(0)
			self.cb.setVisible(0)
			for c in self.cb2:
				c.setVisible(0)
			self.togNav(self.hs)
		elif self.HSCA == 2:
			self.HSCA = 0
			self.btnHS.setLabel(lang.string(1)) #"Controls"
			self.togNav(self.ihb)
			self.ihb.setVisible(1)
			self.hs.setVisible(0)
			self.hsl.setVisible(0)
			self.cb.setVisible(0)
			for c in self.cb2:
				c.setVisible(0)

	def loadHS(s,un):
		s.hs.reset()
		loadHSDP = MyDialogProgress(title=__title__,line1=lang.string(19),line2=lang.string(20))
		loadHSDP.show()
		score_data = ""
		if int(un) == 1: # use internet scores
			loadHSDP.update(25)
			data = ONLINEHIGHSCORE.get_highscore(GAME_ID)
			data = data.replace("|","=")
			score_data = data
		else:
			if os.path.exists(SPACEINVADER_SCORES):
				loadHSDP.update(25)
				fb = open(SPACEINVADER_SCORES,'r')
				sc = fb.read()
				fb.close()
				score_data = sc
			else:
				loadHSDP.close()
				return
		loadHSDP.update(75)
		for x in score_data.split("\n"):
			dat = x.split("=")
			if len(dat) == 2:
				s.hs.addItem(xbmcgui.ListItem(dat[0],dat[1]))
		loadHSDP.update(99)
		loadHSDP.closewin()
		del loadHSDP
	def closeme(self):
		self.close()
	def loadGame(s):
		global MEDIA_FOLDER
		if SETTINGS['theme'] != "-1":
			if FileCheker("Themes\\"+SETTINGS['theme'],thegameimages):
				MyDialogLoader(4,__title__,lang.string(21),lang.string(22),lang.string(23))
				SETTINGS['theme'] = -1
			else:
				MEDIA_FOLDER = SETTINGS['theme']
		if SETTINGS['theme'] == "-1":
			diaselect = MyDialogSelect(title=__title__,mylist=themes)
			diaselect.doModal()
			retVal = diaselect.value
			del diaselect
			if retVal == -1:
				retVal = 0
				return
			MEDIA_FOLDER = themes[retVal].replace(" ","")+"\\"
		if FileCheker("Themes\\"+MEDIA_FOLDER,thegameimages):
			MyDialogLoader(4,__title__,lang.string(21),lang.string(22),lang.string(23))
		else:
			StartBgMusic("Themes\\"+MEDIA_FOLDER.replace("\\",""))
			gamewin = GameWindow()
			gamewin.doModal()
			del gamewin
			if s.HSCA == 2:
				s.loadHS(SETTINGS['usenet'])
			#xbmc.enableNavSounds(1)
			if bgMusic == 1:
				xbmc.Player().stop()

class ConfNetProfile(xbmcgui.WindowDialog):
	"""
		ConfNetProfile
	"""
	def __init__(self):
		if Emulating: xbmcgui.WindowDialog.__init__(self)
		xbmcgui.lock()
		self.setCoordinateResolution(6)

		#self.addControl(xbmcgui.ControlImage(0, 0, 720,576, Root+"images\\background-plain.png"))
		self.addControl(xbmcgui.ControlImage(150, 180, 450,350, Root+"images\\dialog-panel2.png"))
		self.value = -1
		self.doingSelect = 0
		self.addControl(xbmcgui.ControlLabel(190, 200, 370,30,__title__+": "+lang.string(64),font="special13",textColor="DDced8da"))
		# dummy labels to bypass stupid bug
		self.addControl(xbmcgui.ControlLabel(0, 0, 1,1,""))
		self.addControl(xbmcgui.ControlLabel(0, 0, 1,1,""))
		self.addControl(xbmcgui.ControlLabel(0, 0, 1,1,""))
		self.addControl(xbmcgui.ControlLabel(0, 0, 1,1,""))
		self.addControl(xbmcgui.ControlLabel(0, 0, 1,1,""))
		self.addControl(xbmcgui.ControlLabel(0, 0, 1,1,""))
		self.addControl(xbmcgui.ControlLabel(0, 0, 1,1,""))
		self.addControl(xbmcgui.ControlLabel(0, 0, 1,1,""))

		#self.CB_NetSettings = ControlBlock(245,370, 220, 35,self,Root+"\\Images\\",0)
		self.CB_NetSettings = ControlBlock(180,245, 390, 35,self,Root+"\\Images\\",0)
		self.CB_NetSettings.ButSetTex("keyboard-btn-backspace-focus.png","keyboard-btn-backspace.png")
		self.btnENN = self.CB_NetSettings.AddButton(lang.string(60)+": "+ SETTINGS['nickname'],ext_gap=2,voc=1)
		self.btnEPW = self.CB_NetSettings.AddButton(lang.string(61)+": "+SETTINGS['password'],ext_gap=2,voc=1)
		self.CB_NetButton = ControlBlock(245,401, 220, 35,self,Root+"\\Images\\",0)
		self.btnLGI = self.CB_NetButton.AddButton(38,ext_gap=1,voc=1)
		self.btnECA = self.CB_NetButton.AddButton(66,ext_gap=2,voc=1)
		#self.lblNickName = xbmcgui.ControlLabel(190, 255, 370,30,lang.string(60)+": "+SETTINGS['nickname'],font="font12",textColor=fc)
		#self.lblPassword = xbmcgui.ControlLabel(190, 290, 370,30,lang.string(61)+": "+SETTINGS['password'],font="font12",textColor=fc)
		self.lblStatus = xbmcgui.ControlLabel(190, 360, 370,30,lang.string(62)+": "+"unknown",font="font13",textColor=fc)
		#self.addControl(self.lblNickName)
		#self.addControl(self.lblPassword)
		self.addControl(self.lblStatus)
		self.setFocus(self.btnENN)
		self.btnENN.setNavigation(self.btnECA,self.btnEPW,self.btnENN,self.btnENN)
		self.btnEPW.setNavigation(self.btnENN,self.btnLGI,self.btnEPW,self.btnEPW)
		self.btnLGI.setNavigation(self.btnEPW,self.btnECA,self.btnLGI,self.btnLGI)
		self.btnECA.setNavigation(self.btnLGI,self.btnENN,self.btnECA,self.btnECA)
		global USER_ID
		USER_ID = str(ONLINEHIGHSCORE.get_user_id(SETTINGS['nickname'],SETTINGS['password']))
		if USER_ID == "0":
			self.lblStatus.setLabel(lang.string(62)+": invaild")
		else:
			self.lblStatus.setLabel(lang.string(62)+": logged in")
		xbmcgui.unlock()


	def onControl(s,c):
		global SETTINGS
		global USER_ID
		if c == s.btnENN:
			name = unikeyboard(SETTINGS['nickname'],lang.string(7)+":")
			SETTINGS['nickname'] = name
			#s.lblNickName.setLabel(lang.string(60)+": "+SETTINGS['nickname'])
			s.btnENN.setLabel(lang.string(60)+": "+SETTINGS['nickname'])
			s.lblStatus.setLabel(lang.string(62)+": unknown, click LOG IN")
			#USER_ID = str(ONLINEHIGHSCORE.get_user_id(SETTINGS['nickname'],SETTINGS['password']))
		elif c == s.btnEPW:
			#passwd = unikeyboard(SETTINGS['password'],lang.string(65)+":")
			kb = xbmc.Keyboard(SETTINGS['password'],lang.string(65)+":")
			kb.doModal()
			if (kb.isConfirmed()):
				SETTINGS['password'] = kb.getText()
				del kb
			else:
				del kb # no change
			s.btnEPW.setLabel(lang.string(61)+": "+SETTINGS['password'])
			s.lblStatus.setLabel(lang.string(62)+": unknown, click LOG IN")
			#USER_ID = str(ONLINEHIGHSCORE.get_user_id(SETTINGS['nickname'],SETTINGS['password']))
		elif c == s.btnECA:
			USER_ID = str(ONLINEHIGHSCORE.get_user_id(SETTINGS['nickname'],SETTINGS['password']))
			if USER_ID != "0":
				MyDialogLoader(4,__title__,lang.string(68),lang.string(69))
			else:
				temp = ONLINEHIGHSCORE.create_new_user(SETTINGS['nickname'],SETTINGS['password'])
				if temp == "-1":
					MyDialogLoader(4,__title__,lang.string(71),lang.string(69))
				elif temp == "0":
					MyDialogLoader(4,__title__,lang.string(70),lang.string(69))
				else:
					USER_ID = str(ONLINEHIGHSCORE.get_user_id(SETTINGS['nickname'],SETTINGS['password']))
		elif c == s.btnLGI:
			USER_ID = str(ONLINEHIGHSCORE.get_user_id(SETTINGS['nickname'],SETTINGS['password']))
			if USER_ID == "0":
				s.lblStatus.setLabel(lang.string(62)+": "+"invaild or not set")
			else:
				s.lblStatus.setLabel(lang.string(62)+": logged in")
	def onAction(self,a):
		if a == ACTION_BACK:
			saveSettings()
			self.close()
		elif a == ACTION_B:
			saveSettings()
			self.close()

class SettingsMenu(xbmcgui.WindowDialog):
	"""
		Settings Menu
	"""
	def __init__(self):
		if Emulating: xbmcgui.WindowDialog.__init__(self)
		xbmcgui.lock()
		self.setCoordinateResolution(6)
		#self.addControl(xbmcgui.ControlImage(0, 0, 720,576, Root+"images\\background-plain.png"))
		self.addControl(xbmcgui.ControlImage(150, 180, 450,350, Root+"images\\dialog-panel2.png"))
		self.value = -1
		self.doingSelect = 0
		self.addControl(xbmcgui.ControlLabel(190, 200, 370,30,__title__+": "+lang.string(2),font="special13",textColor="DDced8da"))

		self.CB_Settings = ControlBlock(250,245, 250, 30,self,Root+"\\Images\\",0)
		self.btnDT = self.CB_Settings.AddButton(6,voc=1)
		self.btnEDN = self.CB_Settings.AddButton(7,ext_gap=2,voc=1)
		self.btnISC= self.CB_Settings.AddButton(63,ext_gap=2,voc=1)

		self.cmT = self.CB_Settings.AddCM(8,ext_gap=6,voc=1)
		self.cmHHS = self.CB_Settings.AddCM(9,ext_gap=-5,voc=1)
		self.cmADN = self.CB_Settings.AddCM(10,ext_gap=-5,voc=1)
		self.cmAU = self.CB_Settings.AddCM(11,ext_gap=-5,voc=1)
		self.cmSFX = self.CB_Settings.AddCM(50,ext_gap=-5,voc=1)

		self.btnDT.setNavigation(self.cmSFX,self.btnEDN,self.btnDT,self.btnDT)
		self.btnEDN.setNavigation(self.btnDT,self.btnISC,self.btnEDN,self.btnEDN)
		self.btnISC.setNavigation(self.btnEDN,self.cmT,self.btnISC,self.btnISC)
		self.cmT.setNavigation(self.btnISC,self.cmHHS,self.cmT,self.cmT)
		self.cmHHS.setNavigation(self.cmT,self.cmADN,self.cmHHS,self.cmHHS)
		self.cmADN.setNavigation(self.cmHHS,self.cmAU,self.cmADN,self.cmADN)
		self.cmAU.setNavigation(self.cmADN,self.cmSFX,self.cmAU,self.cmAU)
		self.cmSFX.setNavigation(self.cmAU,self.btnDT,self.cmSFX,self.cmSFX)

		self.cmT.setSelected(int(SETTINGS['usenet']))
		self.cmHHS.setSelected(int(SETTINGS['trackhighscores']))
		self.cmADN.setSelected(int(SETTINGS['alwaysusedefaultname']))
		self.cmAU.setSelected(int(SETTINGS['veronstartup']))
		self.cmSFX.setSelected(int(SETTINGS['sfx']))
		self.setFocus(self.btnDT)
		xbmcgui.unlock()

	def onAction(self,action):
		if action == ACTION_BACK:
			saveSettings()
			self.close()
		elif action == ACTION_B:
			saveSettings()
			self.close()

	def onControl(s,c):
		global SETTINGS
		if c == s.btnEDN:
			name = unikeyboard(SETTINGS['nickname'],lang.string(7)+":")
			SETTINGS['nickname'] = name
		elif c == s.cmT:
			SETTINGS['usenet'] = s.cmT.isSelected()
		elif c == s.cmHHS:
			SETTINGS['trackhighscores'] = s.cmHHS.isSelected()
		elif c == s.cmADN:
			SETTINGS['alwaysusedefaultname'] = s.cmADN.isSelected()
		elif c == s.cmAU:
			SETTINGS['veronstartup'] = s.cmAU.isSelected()
		elif c == s.cmSFX:
			SETTINGS['sfx'] = s.cmSFX.isSelected()
		elif c == s.btnISC:
			if SETTINGS['usenet']:
				s.ISCM = ConfNetProfile()
				s.ISCM.doModal()
				del s.ISCM
			else:
				MyDialogLoader(4,__title__,lang.string(55))
		elif c == s.btnDT and not s.doingSelect:
			s.doingSelect = 1
			tempthemes = loadThemeList()
			tempthemes.append('Choose on Play')
			s.themeselect = MyDialogSelect(title=__title__,mylist=tempthemes)
			s.themeselect.doModal()
			retVal = s.themeselect.value
			del s.themeselect
			if retVal == -1:
				SETTINGS['theme'] = "-1"
			elif retVal == len(themes):
				SETTINGS['theme'] = "-1"
			else:
				SETTINGS['theme'] = themes[retVal]+"\\"
			s.doingSelect = 0
		saveSettings()


class GameWindow(xbmcgui.Window):
	"""
		The Window where the game is made/takes place
	"""
	def __init__(self):
		if Emulating: xbmcgui.Window.__init__(self)
		#xbmc.enableNavSounds(0) # Disable Nav sounds so we don't end up with them playing as well

		# Inizalize all the Varibles here well most
		self.base_width = 720
		self.base_height = 576
		self.score = 0
		self.fire_trigger = 0
		self.score_b = 0
		self.isPaused = 0
		self.a_line = {}
		self.allshields= []
		self.withshields = 1
		self.gameover = 0
		self.isUserPaused = 0
		self.bonus_x = -190
		self.l = 0
		self.me_x = STARTING_X
		self.collum = {}
		self.life = []
		self.alive = []
		self.numlife = 3
		self.invader_count = 55
		self.invader_shootinprogress = 0
		self.shieldblockcnt = [12,12,12,12]

		#  Init Controls
		self.setCoordinateResolution(6)
		self.addControl(xbmcgui.ControlImage(0, 0, self.base_width, self.base_height, Root+"Themes\\"+MEDIA_FOLDER+"background-plain.png"))
		self.addControl(xbmcgui.ControlLabel(90, 40, self.base_width, self.base_height, __title__ + ": " + __version__,font="font14",textColor=fc))
		self.IMGleveldone  = xbmcgui.ControlImage(0, 0,self.base_width, self.base_height, ("%sThemes\\%sleveldone.PNG"%(Root,MEDIA_FOLDER)))
		self.go_il_splash  = xbmcgui.ControlImage(0, 0, self.base_width, self.base_height, ("%sThemes\\%sgameover-landed.PNG"%(Root,MEDIA_FOLDER)))
		self.theship = xbmcgui.ControlImage(STARTING_X,YOUR_Y,64,38, Root+"Themes\\"+MEDIA_FOLDER+"me.png")
		self.bonus = xbmcgui.ControlImage(self.bonus_x,95,80,35, Root+"Themes\\"+MEDIA_FOLDER+"bonus.png")
		self.level = (xbmcgui.ControlLabel(220, 75, self.base_width, self.base_height, "%s: %s" % (lang.string(31),self.l),font="font12",textColor=fc))
		self.lives = (xbmcgui.ControlLabel(355, 75, self.base_width, self.base_height, "%s: %s" % (lang.string(32),3),font="font12",textColor=fc))
		self.scoreboard = (xbmcgui.ControlLabel(90, 75, self.base_width, self.base_height, "%s: 0" % lang.string(33),font="font12",textColor=fc))
		self.gosplash  = xbmcgui.ControlImage(0, 0, self.base_width, self.base_height, ("%sThemes\\%sgameover.PNG"%(Root,MEDIA_FOLDER)))
		self.txtbx  = xbmcgui.ControlLabel(170, 300, 380,150,"",font="font13",textColor=fc,alignment=3)
		self.bullet = xbmcgui.ControlImage(self.me_x+21,YOUR_Y-18,16,20, Root+"Themes\\"+MEDIA_FOLDER+"bullet.png",aspectRatio=2)

		self.ivbullet1 = xbmcgui.ControlImage(0,0,10,30, Root+"Themes\\"+MEDIA_FOLDER+"ebullet_f0.png")
		self.ivbullet2 = xbmcgui.ControlImage(0,0,10,30, Root+"Themes\\"+MEDIA_FOLDER+"ebullet_f0.png")
		self.addControl(self.ivbullet1)
		self.addControl(self.ivbullet2)
		self.ivbullet1.setVisible(0)
		self.ivbullet2.setVisible(0)

		self.img_pause = xbmcgui.ControlImage(int(self.base_width / 2 - 360 /2),int(self.base_height / 2 - 160 /2),360,180, Root+"Themes\\"+MEDIA_FOLDER+"paused.png")
		self.bt = BulletThread(self,self.me_x+21,YOUR_Y-18)
		self.ivbt = BulletINVThread(self,1)
		self.ivbt2 = BulletINVThread(self,2)
		self.setupGame()
		self.makeControls()
		self.genInvaders()
		self.GoStart()
		DrawLife(self)
		if self.withshields == 1:
			self.shieldblock(SHEILDS_X[0],SHIELD_Y)
			self.shieldblock(SHEILDS_X[1],SHIELD_Y)
			self.shieldblock(SHEILDS_X[2],SHIELD_Y)
			self.shieldblock(SHEILDS_X[3],SHIELD_Y)

	def setupGame(self):
		self.fire_trigger = 0
		self.bullet.setVisible(0)
		self.shieldblockcnt = [12,12,12,12]
		#self.bt = None
		self.l = 0
		self.collum = {}
		self.numlife = 3
		self.alive = []
		self.gameover = 0
		self.invader_count = 55
		self.invader_shootinprogress = 0
		self.bonus_x = -190
		self.me_x = STARTING_X

	def restartGame(self,l):
		self.theship.setPosition(STARTING_X,YOUR_Y)
		self.bt.stop()
		self.IVB.stop()
		self.IVT.stop()
		del self.IVB
		del self.IVT
		lifes_temp =  self.numlife
		self.setupGame()
		self.numlife = lifes_temp
		self.l = l
		DrawLife(self)
		self.clear()
		self.level.setLabel("%s: %s" % (lang.string(31),self.l))
		self.GoStart()

	def clear(self):
		for y in range(1,6):
			a = []
			for x in range(0,11):
				a.append(1)
				self.collum[x] = 5
				self.a_line[y][x].setVisible(1)
				self.a_line[y][x].setPosition(STARTING_X+64+x*40,LINES_Y[y]+self.l*MD)
			self.alive.append(a)

	def makeControls(self):
		xbmcgui.lock()
		self.addControl(self.bonus)
		self.addControl(self.scoreboard)
		self.addControl(self.theship)
		self.addControl(self.level)
		self.addControl(self.lives)
		self.addControl(self.bullet)
		self.bullet.setVisible(0)
		xbmcgui.unlock()

	def GoStart(self):
		self.bonus.setPosition(-190,95)
		self.IVT = InVaders(self,STARTING_X+32,self.l)
		self.bt.iv = self.IVT
		self.IVB = InVadersBonus(self)

	def shieldblock(self,bx,by):
		sb = []
		for x in range(0,4):
			if x != 0:
				sb.append(SBlock(bx,by,self))
				sb.append(SBlock(bx+16*3,by,self))
			if x != 3:
				sb.append(SBlock(bx+16,by,self))
				sb.append(SBlock(bx+16*2,by,self))
			by += 16
		self.allshields.append(sb)

	def dogameOver(self,unlockgui=0):
		#if self.bt is not None:
		self.bt.stop()
		self.IVB.stop()
		self.IVT.stop()

		if unlockgui == 1:
			xbmcgui.unlock()

	def doScores(self):
		name = ""
		Submit2Net = 0
		mode = ""
		if SETTINGS['trackhighscores']:
			if int(SETTINGS['usenet']):
				name = SETTINGS['nickname']
				Submit2Net = int(MyDialogLoader(0,__title__,lang.string(37)))
			else:
				if int(SETTINGS['alwaysusedefaultname']):
					name = SETTINGS['nickname']
				else:
					name = unikeyboard(SETTINGS['nickname'],lang.string(34))
		retval2 = 0
		tmpdp = MyDialogProgress(title=__title__,line1=lang.string(19),line2=lang.string(25))
		tmpdp.show()
		if name != "":
			if Submit2Net == 0:
				tmpdp.update(50,lang.string(19),lang.string(26))
				retval2 = SubmitScores2HDD(name,self.score)
				mode = 72
			else:
				tmpdp.update(50,lang.string(19),lang.string(27))
				if USER_ID == "0":
					MyDialogLoader(4,__title__,lang.string(56),lang.string(53),lang.string(54))
				else:
					mode = 73
					retval2 = SubmitScores(self.score)
		tmpdp.closewin()
		del tmpdp
		if retval2 == 0:
			MyDialogLoader(4,__title__,lang.string(59),lang.string(58),lang.string(mode))
		else:
			MyDialogLoader(4,__title__,lang.string(57),lang.string(mode))

	def meonewin(self,win):
		if  win.numlife == -1:
			win.isPaused = 1
			win.gameover = 1
			win.addControl(win.gosplash)
			win.addControl(win.txtbx)
			win.txtbx.setPosition(170, 350)
			# TODO: Localize
			win.txtbx.setLabel("You have ran out of lifes\nYou got %s points\n Press OK to Return to Menu" % self.score)
			MyDialogLoader(3,420)
			win.doScores()
			xbmcgui.lock()
			win.removeControl(self.gosplash)
			win.removeControl(self.txtbx)
			win.dogameOver(unlockgui=1)
			win.isPaused = 0
			win.close()
		else:
			win.SetLevelClean()
			win.restartGame(self.l)
			DrawLife(self)

	def SetLevelClean(self):
		# AKA Redraw Shields Full all invaders back up top
		self.shieldblockcnt = [12,12,12,12]
		xbmcgui.lock()
		for t in range(0,4):
			for vx in self.allshields[t]:
				vx.newLevel()
		xbmcgui.unlock()
	def levelDone(s):
		s.isPaused = 1
		s.addControl(s.IMGleveldone)
		s.addControl(s.txtbx)
		s.txtbx.setPosition(170, 300)
		# TODO: Localise [needs thinking about
		s.txtbx.setLabel("Level Completed\nYou Got %s points\nClick OK to go to Next Level" % s.score)
		MyDialogLoader(3,230)
		s.removeControl(s.IMGleveldone)
		s.removeControl(s.txtbx)
		s.SetLevelClean()
		s.restartGame(l=s.l+1)
		s.isPaused = 0
	def DoMyToast(self,header,info):
		width = 232
		toast_bg = xbmcgui.ControlImage(250, 90, 232,75, Root+"Images\\panel-bg.png")
		toast_ico = xbmcgui.ControlImage(250+30, 90+15, 40,40, Root+"Images\\infoicon.png")
		headerlabel = xbmcgui.ControlLabel(250+80, 90+17,width-80-20 ,40,header,font="font12",textColor=fc)
		infolabel = xbmcgui.ControlLabel(250+80, 90+33,width-80-20 ,40,info,font="font12",textColor=fc)
		self.addControl(toast_bg)
		self.addControl(toast_ico)
		self.addControl(headerlabel)
		self.addControl(infolabel)
		#while self.running == 1:
		bottomy = 90+33
		sleep(1)
		for myframe in range(1,bottomy):
			toast_bg.setPosition(250,bottomy-33-myframe)
			toast_ico.setPosition(250+30,bottomy-17-myframe)
			headerlabel.setPosition(250+80,bottomy-15-myframe)
			infolabel.setPosition(250+80,bottomy-myframe)
			sleep(0.008)
		self.removeControl(toast_bg)
		self.removeControl(toast_ico)
		self.removeControl(headerlabel)
		self.removeControl(infolabel)

	def genInvaders(self):
		xbmcgui.lock()
		for y in range(1,6):
			self.a_line[y] = []
			a = []
			for x in range(0,11):
				a.append(1)
				self.collum[x] = 5
				if y == 1:
					self.a_line[y].append(self.returnVader(STARTING_X+32+x*40,LINES_Y[y]+self.l*MD,"vadertop_f1.png"))
				elif 1 < y < 4:
					self.a_line[y].append(self.returnVader(STARTING_X+32+x*40,LINES_Y[y]+self.l*MD,"vadermid_f1.png"))
				elif y >= 4:
					self.a_line[y].append(self.returnVader(STARTING_X+32+x*40,LINES_Y[y]+self.l*MD,"vaderbottom_f1.png"))
			self.alive.append(a)
		xbmcgui.unlock()

	def returnVader(self,x,y,img_ext):
		c = xbmcgui.ControlImage(x,y,32,32, Root+"Themes\\"+MEDIA_FOLDER+img_ext,aspectRatio=2)
		self.addControl(c)
		return c

	def onAction(s, a):
		if Emulating: BC = 5
		else:   BC = a.getButtonCode()
		if s.isPaused:
			if s.isUserPaused:
				if a == ACTION_Y or a == ACTION_REMOTE_INFO:
					s.isPaused = 0
					s.isUserPaused = 0
					s.removeControl(s.img_pause)
					return
				elif a == ACTION_B or a == ACTION_BACK:
					if s.gameover == 0:
						s.gameover = MyDialogLoader(0,__title__,lang.string(18))
						if s.gameover == 1:
							s.isPaused = 1
							s.gameover = 1
							s.doScores()
							sleep(2)
							s.dogameOver()
							s.isPaused = 0
							s.close()
							return
					else:
						s.close()
			return
		# Note if its paused it will not reach here :D
		if  a == ACTION_B or a == ACTION_BACK:
			if s.gameover == 0:
				s.isPaused = 1
				s.gameover = MyDialogLoader(0,__title__,lang.string(18))
				if s.gameover == 1:
					s.doScores()
					s.dogameOver()
					s.close()
					return
				s.isPaused = 0
			else:
				s.close()
		elif a == ACTION_Y  or  a == ACTION_REMOTE_INFO and s.isUserPaused == 0:
			s.isPaused = 1
			s.isUserPaused = 1
			print "paused"
			s.addControl(s.img_pause)
		elif a == ACTION_X:
			if  xbmc.Player().isPlaying():
				if s.isPaused == 0:
					s.isPaused = 1
					s.addControl(s.img_pause)
				else:
					s.isPaused = 0
					s.removeControl(s.img_pause)
			else:
				pass
		elif a == ACTION_WHITE:
			s.numlife = -1
			s.meonewin(s)
			#pass
			"""
			mmp = MyMediaPlayer()
			mmp.doModal()
			del mmp
			#"""
		elif a == ACTION_A or a.getButtonCode() == 61472:
			s.onFire()
		elif a == ACTION_TRIGGER_RIGHT:
			if not RIGHT_X <= s.me_x:
				s.me_x += 16
				s.theship.setPosition(s.me_x,YOUR_Y)
		elif a == ACTION_TRIGGER_LEFT:
			if not LEFT_X+16 >= s.me_x:
				s.me_x -= 16
				s.theship.setPosition(s.me_x,YOUR_Y)
		elif a == ACTION_DPAD_RIGHT:
			if not RIGHT_X <= s.me_x:
				s.me_x += 16
				s.theship.setPosition(s.me_x,YOUR_Y)
		elif a == ACTION_DPAD_LEFT:
			if not LEFT_X+16 >= s.me_x:
				s.me_x -= 16
				s.theship.setPosition(s.me_x,YOUR_Y)

		if BC == BUTTON_LEFTHUMB_UP:
			s.onFire()
		elif BC == BUTTON_LEFTHUMB_LEFT:
			if not LEFT_X+16 >= s.me_x:
				s.me_x -= 16
				s.theship.setPosition(s.me_x,YOUR_Y)
		elif BC == BUTTON_LEFTHUMB_RIGHT:
			if not RIGHT_X <= s.me_x:
				s.me_x += 16
				s.theship.setPosition(s.me_x,YOUR_Y)

	def onFire(self):
		if not self.gameover:
			if not self.fire_trigger:
				self.bullet.setVisible(0)
				self.fire_trigger = 1
				SFX("yourfire")
				xbmcgui.lock()
				self.bullet.setVisible(1)
				self.bullet.setPosition(self.me_x+21,YOUR_Y-18)
				xbmcgui.unlock()
				self.bt.running = True
				self.bt.doStart(self,self.me_x+21,YOUR_Y-18,self.IVT)

	def onControl(self, control):
		pass # onControl OverWrite

## TIMER THING THREAD FOR BULLET
class BulletINVThread(Thread):
	"""
		This Threaded Class maintains the code for the invaders bullet
		It controls movement and collistion detection
	"""
	def __init__(self, win, bn):
		Thread.__init__(self)
		self.win = win
		self.posx = 0 #posx+16
		self.posy = 0 #iniposy+32
		self.gfx = Root+"Themes\\"+MEDIA_FOLDER+"ebullet_f0.png"
		self.running = False
		self.quitDone = 0
		self.changeframe = 0
		self.BulNum = bn

	def doStart(self, posx,posy,iv):
		self.posx = posx
		self.iv = iv
		self.posy = posy
		self.running = True
		if self.BulNum == 1:
			self.win.ivbullet1.setVisible(1)
			self.win.ivbullet1.setPosition(self.posx,self.posy)
		else:
			self.win.ivbullet2.setVisible(1)
			self.win.ivbullet2.setPosition(self.posx,self.posy)
		self.start()

	def run(self):
		bullet_height = 30
		while self.running and not self.win.gameover:
			if self.win.gameover == 1:
				self.stop()
				return
			if not self.win.isPaused:
				if self.win.gameover == 1:
					self.stop()
					return
				sleep(BASE_SPEED*3.7)
				if self.win.gameover == 1:
					self.stop()
					return
				if  self.win.fire_trigger == 1:
					# This therefore means this bullet is looking for Your bullet to hit
					try:
						if self.win.bt.posx == self.posx or self.posx-8 < self.win.bt.posx <= self.posx+10:
							if  self.posy <= self.win.bt.posy <= self.posy+30:
								self.win.bt.stop()
								self.stop()
								return
					except:
						print "Error has occured detecting bullet - afaik i fixed this issuse but oh well"
				if self.win.gameover == 1:
					self.stop()
					return
				if YOUR_Y+40 <= self.posy+bullet_height:
					self.stop()
					return
				elif SHIELD_Y <=  self.posy + bullet_height <= SHIELD_Y+16*4:
					retVal = BulletVsShield(self,30)
					if retVal == 1:
						self.stop()
						return
					self.posy += 5
				elif YOUR_Y <= (self.posy + bullet_height) <= YOUR_Y+35:
					if self.win.me_x <= (self.posx) <= self.win.me_x+62:
						self.win.numlife -= 1
						SFX("INVFireHitU")
						if self.win.numlife == -1:
							self.win.meonewin(self.win)
							self.stop()
							return
						else:
							DrawLife(self.win)
							self.posy += 5
							self.stop()
							self.win.isPaused = 1
							self.win.me_x = STARTING_X
							self.win.theship.setPosition(STARTING_X,YOUR_Y)
							sleep(0.5)
							self.win.isPaused = 0
						return
					else:
						self.posy += 5
				else:
					self.posy += 5
				if self.win.gameover == 1:
					self.stop()
					return
				if self.changeframe == 8:
					if self.gfx == self.gfx.replace("_f1.png","_f0.png"):
						self.gfx = self.gfx.replace("_f0.png","_f1.png")
					else:
						self.gfx = self.gfx.replace("_f1.png","_f0.png")
					self.changeframe = -1
					if self.BulNum == 1:
						self.win.ivbullet1.setImage(self.gfx)
					else:
						self.win.ivbullet2.setImage(self.gfx)
				if self.BulNum == 1:
					self.win.ivbullet1.setPosition(self.posx,self.posy)
				else:
					self.win.ivbullet2.setPosition(self.posx,self.posy)
				self.changeframe += 1
				if self.win.gameover == 1:
					self.stop()
					return
			if self.win.gameover == 1:
				self.stop()
				return
		self.stop()

	def stop(self):
		if self.BulNum == 1:
			self.win.ivbullet1.setVisible(0)
		else:
			self.win.ivbullet2.setVisible(0)
		if self.quitDone == 0:
			self.win.invader_shootinprogress -= 1
			self.running = False
			self.quitDone = 1
		else:
			self.running = False

class BulletThread(Thread):
	"""
		This Threaded Class maintains the code for the players bullet
		The movement and collistion detection.
	"""
	def __init__(self, win, posx,iniposy): #,iv):
		Thread.__init__(self)
		self.win = win
		self.posx = posx
		self.posy = iniposy
		self.running = False
		self.iv = None

	def doStart(self, win, posx,iniposy,iv):
		self.win = win
		self.posx = posx
		self.posy = iniposy
		self.running = True
		self.iv = iv
		self.start()
	def run(self):
		while self.running and not self.win.gameover:
			if self.win.gameover == 1:
				self.stop()
				return
			if not self.win.isPaused:
				sleep(BASE_SPEED)
				if self.win.gameover == 1:
					self.stop()
					return
				if TOP_Y >= self.posy:  self.stop()
				elif BONUS_Y < self.posy < BONUS_Y + 40 and self.win.bonus_x < self.posx <  self.win.bonus_x + 80:
					self.win.score += 300
					if self.win.score-self.win.score_b*1000 >= 1000:
						self.win.score_b += 1
						self.win.numlife += 1
						DrawLife(self.win)
						thread.start_new_thread(self.win.DoMyToast,(lang.string(28),lang.string(30)))
					self.win.scoreboard.setLabel("Score: %s" % self.win.score)
					SFX("bonus_destory")
					self.win.IVB.clearIVB()
					self.stop()
					thread.start_new_thread(self.win.DoMyToast,(lang.string(28),"300 %s" % lang.string(29)))
				else:
					self.posy -= 5
					self.win.bullet.setPosition(self.posx,self.posy)
				if SHIELD_Y <=  self.posy-5 <= SHIELD_Y+16*4:
					retVal = BulletVsShield(self,0)
					if retVal == 1:
						self.stop()
						return
				d = range(1,6)
				d.reverse()
				for y in d:
					TOP_Y_BOUND = LINES_Y[y]+self.iv.lines*MD
					BOTTOM_Y_BOUND = LINES_Y[y]+self.iv.lines*MD+35  # add hieght of invader ontop top location to find bottom coordiants
					if TOP_Y_BOUND < self.posy < BOTTOM_Y_BOUND:
						for x in xrange (0,11):
							LEFT_X_BOUND = self.iv.posx+x*40-5
							RIGHT_X_BOUND = self.iv.posx+x*40+35
							if LEFT_X_BOUND < self.posx < RIGHT_X_BOUND:
								if self.win.alive[y-1][x] == 1:
									self.win.invader_count += -1
									self.win.alive[y-1][x] = 0  # its dead now
									self.win.score += 10*(6-y)
									if self.win.score-self.win.score_b*1000 >= 1000:
										self.win.score_b += 1
										self.win.numlife += 1
										DrawLife(self.win)
										thread.start_new_thread(self.win.DoMyToast,("Bonus","Extra Life"))
									self.win.scoreboard.setLabel("Score: %s" % self.win.score)
									self.win.a_line[y][x].setVisible(0)
									self.win.collum[x] -= 1
									SFX("youhitvader")
									if self.win.invader_count == 0:
										self.iv.stop()
										SFX("win")
										self.win.levelDone()
									self.stop()
									return
								else:   pass # Invader located there is already dead
					else:   pass    # this means its not reached the line yet
		self.stop()
	def stop(self):
		self.running = False
		self.win.bullet.setVisible(0)
		self.win.fire_trigger = 0

class InVadersBonus(Thread):
	"""
		This Threaded Class controls the movment of the Bonus UFO
	"""
	def __init__(self, win):
		Thread.__init__(self)
		self.w = win
		self.x = -90
		self.tim = 25
		self.fac = 0.8
		self.moving = 0
		self.running = 1
		self.movintval = 0
		self.start()

	def run(self):
		while self.running and not self.w.gameover:
			if not self.w.isPaused and not self.w.gameover:
				if self.moving == 0:
					sleep(0.5)
					self.movintval += 1
					if self.movintval == self.tim*self.fac*2:
						self.movintval  = 0
						self.tim = self.tim*self.fac*2
						SFX("bonus")
						self.moving = 1
				elif self.moving == 1 and not self.w.gameover:
					sleep(BASE_SPEED_B)
					self.x += MS/3
					if self.x >= (RIGHT_X + 70):
						self.clearIVB()
					else:
						self.w.bonus.setPosition(self.x,BONUS_Y)
						self.w.bonus_x = self.x

	def clearIVB(self):
		self.moving = 0
		self.x = -190
		self.w.bonus.setPosition(self.x,BONUS_Y)

	def stop(self):
		self.running = 0
		self.moving = 0
		self.x = -190
		self.w.bonus.setPosition(self.x,BONUS_Y)

class InVaders(Thread):
	"""
		This Threaded Class maintains the momvement of all the invaders ship as well as collisition detection and firing
	"""
	def __init__(self, win, x,start_line=0):
		Thread.__init__(self)
		self.win = win
		self.posx = x
		self.lines = start_line # means hasn't moved down yet :D
		self.dir = 1 # moving right
		self.did_change = 0
		self.linechange = 0
		self.tframe = 1
		self.shoot_from_x = -1
		self.running = True
		self.start()

	def calctime(self,x):
		# Contruct formulas
		a = 4.95852548087e-007
		b = -6.2857171343663e-005
		c = 0.0028608768
		d = (-0.07639687364933)
		#e = 1.55549
		e = 1.48
		# "%sx^4 + %sx^3 + %sx^2 + %sx + %s" % ( a,b,c,d,e)
		ans = a*x**4+b*x**3+c*x**2+d*x+e
		return ans

	def IVShootCalc(self,win,x,y):
		#print "Shoot calc y: %s" % y
		#print "Shoot calc x: %s" % x
		if y > 0 and not win.isPaused:
			posy = LINES_Y[y]+self.lines*MD
			posx = self.posx+x*40
			if win.invader_shootinprogress != 2 and not win.isPaused :
				if (randint(0,3) > 1): # 50-50    as it can be  0,1   or  2,3
					if win.invader_shootinprogress == 0:
						win.invader_shootinprogress += 1
						win.ivbt.doStart(posx,posy,self)
						self.shoot_from_x = x
					elif win.invader_shootinprogress ==  1 and  randint(0,6) == 4 and x != self.shoot_from_x:
						win.invader_shootinprogress += 1
						win.ivbt2.doStart(posx,posy,self)
	def run(self):
		self.did_change = 0
		self.linechange = 0
		self.tframe = 1
		while self.running and not self.win.gameover:
			if self.win.gameover == 1:
				self.stop()
				return
			if not self.win.isPaused:
				sleep (self.calctime(55-self.win.invader_count))
				if self.win.gameover == 1:
					self.stop()
					return
				if not self.win.isPaused:
					linedead = 0
					self.linechange = 0
					if self.did_change  == 0:
						self.linechange = 0
						a = range(0,11)
						if self.dir == 0:   # means the invaders are moving left so check the left side of the screen :D
							for x in a:
								if self.win.collum[x] == 0:
									linedead = 1
								else:
									if LEFT_X >= self.posx+x*40:
										self.dir = 1
										self.lines +=1
										self.linechange = 1
										self.did_change = 1
						else:
							a.reverse() # This next bit checks to see if its at the egde of the right screen but first it has to check from right to left if the rows are dead if so it can go more
							for x in a:
								if self.win.collum[x] == 0: # means its a live then
									linedead = 1 # that means check the next one
								else:
									if RIGHT_X+16 < self.posx+x*40:
										self.dir = 0
										self.lines +=1
										self.linechange = 1
										self.did_change = 1
					else:
						self.linechange == 0

					if self.linechange == 0 and not self.win.isPaused:
						if self.dir == 1:   self.posx += MS
						else:   self.posx -= MS

					BaseImg = Root+"Themes\\"+MEDIA_FOLDER
					for y in range(1,6):
						#rowliving = 0
						cl = self.win.a_line[y]
						vr = range(0,11)
						if self.dir:    vr.reverse()             # if dir =  1 then   invaders are moving <-    so run from  11 to 0 (right to left)
						for x in vr:
							if self.win.gameover == 1:
								self.stop()
								return
							if self.tframe == 1: theframe = 2
							else: theframe = 1
							if y == 1:  cl[x].setImage("%svadertop_f%s.png"%(BaseImg,theframe))
							elif 1 < y < 4: cl[x].setImage("%svadermid_f%s.png"%(BaseImg,theframe))
							elif y >= 4:    cl[x].setImage("%svaderbottom_f%s.png"%(BaseImg,theframe))
							cl[x].setPosition(self.posx+x*40,LINES_Y[y]+self.lines*MD)
							if self.win.alive[y-1][x] == 1:
								# This if Checks to see if the invaders is inline with the shields
								if SHIELD_Y-10 <=  LINES_Y[y]+self.lines*MD+10<= SHIELD_Y+16*4:
									self.ShieldCheck(self.posx+x*40,y)
								elif YOUR_Y  <=  LINES_Y[y]+self.lines*MD+32:
									# This menas that the ships is in the row where u are  (also the ship is alive in there :D)
									#   rowliving = 1  \n if rowliving == 1:
									# Ships are in bottom row
									self.win.gameover = 1
									self.win.isPaused = 1
									self.stop()
									invaderlanded(self.win)
									return
					self.shoot_from_x = -1
					if self.win.invader_count >  4:
						xes = [randint(0,5),randint(0,5),randint(5,10),randint(5,10)]
						# any row choose via the collum method must be alive as it it 5-1 (when the collum is shot)
						# problem if we shoot out the top row and have the bottom row still their this will muck up oh well
						self.IVShootCalc(self.win,xes[0],self.win.collum[int(xes[0])])
						self.IVShootCalc(self.win,xes[1],self.win.collum[int(xes[1])])
						self.IVShootCalc(self.win,xes[2],self.win.collum[int(xes[2])])
						self.IVShootCalc(self.win,xes[3],self.win.collum[int(xes[3])])
					if self.linechange == 0 and  self.did_change  == 1:
						self.did_change = 0
					self.tframe = self.tframe*-1
		self.stop()
	def ShieldCheck(self,invx,y):
		for sn in range(0,4):
			if SHEILDS_X[sn]-42 <=  (invx) <= SHEILDS_X[sn]+16*4:
				for sb in self.win.allshields[sn]:
					if sb.power < 5:
						if LINES_Y[y]+self.lines*MD <= sb.y <= LINES_Y[y]+self.lines*MD+MD and invx-5  <=  sb.x  <= invx+43:
							self.win.shieldblockcnt[sn] -= 1
							sb.destoryme()
	def stop(self):
		self.running = False
class MyDialogProgress(xbmcgui.WindowDialog):
	"""
		MyDialogProgress - This will replace the built in DialogProgress (so its uses PM3 No matter what the skin is)
	"""
	def __init__(self,title=__title__,line1="",line2="",line3="",mode=0):
		if Emulating: xbmcgui.WindowDialog.__init__(self)
		self.setCoordinateResolution(6)
		xbmcgui.lock()
		self.addControl(xbmcgui.ControlImage(165, 205, 390,190, Root+"images\\dialog-panel2.png"))
		self.value = -1
		self.mode = mode
		self.addControl(xbmcgui.ControlLabel(190, 218, 370,30,title,font="special13",textColor="DDced8da"))
		self.cancelled = 0
		self.linea = xbmcgui.ControlLabel(190, 260, 370,30,line1,font="font10",textColor="0xFFFFFFFF")
		self.lineb = xbmcgui.ControlLabel(190, 280, 370,30,line2,font="font10",textColor="0xFFFFFFFF")
		self.linec = xbmcgui.ControlLabel(190, 300, 370,30,line3,font="font10",textColor="0xFFFFFFFF")
		self.addControl(self.linea)
		self.addControl(self.lineb)
		self.addControl(self.linec)

		if mode == 0:
			self.btnCancel = xbmcgui.ControlButton(463, 335, 77,32,lang.string(42),font="font10",textColor="0xFFFFFFFF",focusTexture=Root+"images\\keyboard-btn-backspace-focus.png",noFocusTexture=Root+"images\\keyboard-btn-backspace.png",alignment=6)
			self.addControl(self.btnCancel)
			self.setFocus(self.btnCancel)
		self.addControl(xbmcgui.ControlImage(190, 346, 261,13, Root+"images\\progress_back2.png"))
		self.midPB = xbmcgui.ControlImage(190, 346, 1,13, Root+"images\\progress_mid.png")
		self.addControl(self.midPB)
		self.addControl(xbmcgui.ControlImage(190, 346, 261,13, Root+"images\\progress_over.png"))
		xbmcgui.unlock()

	def onAction(self,a):
		if a == ACTION_BACK:
			self.value = 0
			self.close()
		elif a == ACTION_START:
			self.value = 1
			self.close()
	def onControl(self,control):
		if self.mode == 0:
			if control == self.btnCancel:
				self.value = 1
				self.cancelled = 1
				self.close()

	def update(self, pc,line1 = "", line2 = "", line3 = ""):
		# Chagne the lines etc
		if line1 != "": self.linea.setLabel(line1)
		if line2 != "": self.lineb.setLabel(line2)
		if line3 != "": self.linec.setLabel(line3)
		if 0 < pc < 100:
			self.new_width = int(261*(pc/float(100)))
			self.midPB.setWidth(self.new_width)
		elif pc > 100:
			self.close()
			return
		else:
			return

	def closewin(self):
		self.close()
	def iscanceled(self):
		return self.cancelled

#--- Global Functions---#000000#FFFFFF-----------------------------------------
def DrawLife(win):
	for c in win.life:
		win.removeControl(c)
	win.life = []
	win.lives.setLabel("Lives: %s" % win.numlife)
	for y in range(0,win.numlife):
		win.life.insert(y,xbmcgui.ControlImage(425+y*40, 65, 35,23, Root+"Themes\\"+MEDIA_FOLDER+"life.png"))
		win.addControl(win.life[y])
def BulletVsShield(o,bh_off):
	for sn in range(0,4):
		if o.win.shieldblockcnt[sn] != 0:
			#print "%s  < %s < %s" % (SHEILDS_X[sn],o.posx,SHEILDS_X[sn]+16*4)
			if SHEILDS_X[sn] <=  (o.posx) < SHEILDS_X[sn]+16*4:
				if o.win.allshields == []:
					return 0
				t =  range(0,len(o.win.allshields[sn]))
				t.reverse()
				for sb in t:
					shx = o.win.allshields[sn][sb].x
					if shx  <=  (o.posx) < shx +16:
						shy = o.win.allshields[sn][sb].y
						if shy <= o.posy+bh_off < shy+16+bh_off:
							if o.win.allshields[sn][sb].power < 4:
								o.win.allshields[sn][sb].shoot()
								o.stop()
								return 1
							elif o.win.allshields[sn][sb].power == 4:
								o.win.shieldblockcnt[sn] -= 1
								o.win.allshields[sn][sb].shoot()
								o.stop()
								return 1
	return 0
def invaderlanded(win):
	SFX("invaders_landed")
	win.addControl(win.go_il_splash)
	MyDialogLoader(3,420)
	win.doScores()
	win.dogameOver()
	win.isPaused = 0
	win.close()
def unikeyboard(default,header=""):
	"""
		Opens XBMC Virtual Keyboard
		Give it the Default value and header and it will return the value entered
		If user cancelled it will return the default text.
	"""
	kb = xbmc.Keyboard(default,header)
	kb.doModal()
	if (kb.isConfirmed()):
		return kb.getText()
	else:
		return default

def SubmitScores(score):
	"""
	txdata  = urllib.urlencode({'score':score, 'name':name, 'secureid':'4815162342'})
	html = urllib.urlopen(SYSTEM_URL,txdata).read()
	if html == "New Score":
		xbmcgui.Dialog().ok(__title__,"Congratulation, You got a HighScore")
	else:
		xbmcgui.Dialog().ok(__title__,"Sorry, you didn't get a HighScore","There will always be next time")
	"""

	retVal = ONLINEHIGHSCORE.insert_new_highscore(GAME_ID, USER_ID, str(score))
	return int(retVal)

def SubmitScores2HDD(name,score):
	score = int(score)
	curdat = ""
	d = -1
	if os.path.exists(SPACEINVADER_SCORES):
		fb = open(SPACEINVADER_SCORES,'r')
		sc = fb.read()
		fb.close()
		if sc == "":
			curdat = "%s=%s\n" % (name,str(score))
		else:
			sc = sc.split("\n")
			d = highscorePos(sc,score)
			if d != -1:
				newline = "%s=%s" % (name,str(score))
				sc.insert(d,newline)
			c = 0
			for x in sc:
				c +=1
				if c <= 10:
					curdat += x + "\n"
	else:
		curdat = "%s=%s\n" % (name,str(score))
		d = 0
	fb = open(SPACEINVADER_SCORES,'w')
	fb.write(curdat)
	fb.close
	if d == -1:
		return 0
	elif d >= 10:
		return 0
	else:
		return 1

def highscorePos(sd,myscore):
	pos = -1
	for x in sd:
		if  x != "":
			dat = x.split("=")
			pos += 1 # this will make it 0 so top of list
			if myscore >= int(dat[1]):
				return pos
	if pos <= 10:
		return pos+1

	return -1

def se(extra):
	return os.path.exists(Root+(extra))

def StartBgMusic(theme="Music"):
	if WasPlaying  != 1: # if ppl already listening to music/video don't do this
		bgurl = Root+ theme + "\\InvaderBackground"
		if  os.path.exists(Root+"Music\\Playlist.m3u"):
			bgmusicpl = xbmc.PlayList(xbmc.PLAYLIST_MUSIC)
			bgmusicpl.load(Root+"Music\\Playlist.m3u")
			xbmc.Player(xbmc.PLAYER_CORE_AUTO).play(bgmusicpl)
		elif os.path.exists(bgurl + ".mp3"):
			xbmc.Player(xbmc.PLAYER_CORE_AUTO).play(bgurl + ".mp3")
		elif os.path.exists(bgurl + ".mod"):
			xbmc.Player(xbmc.PLAYER_CORE_AUTO).play(bgurl + ".mod")
		elif os.path.exists(Root+"Music\\InvaderBackground.mp3"):
			xbmc.Player(xbmc.PLAYER_CORE_AUTO).play(Root+"Music\\InvaderBackground.mp3") # Default  If no user playlist or Theme music use this
		global bgMusic
		bgMusic = 1

def FileCheker(base_path,imgs):
	failed = 0
	for x in imgs:
		if not se("%s%s" % (base_path,x)):
			print "failed to find file %s" % x
			failed = 1
	if failed == 1:
		return 1
	else:
		return 0

def saveSettings():
	global SETTINGS
	fb = open(SPACEINVADER_SETTINGS,'w')
	try:
		curdat = "<spaceinvaders>\n\t<usenet>%s</usenet>\n\t<trackhighscores>%s</trackhighscores>\n\t<alwaysusedefaultname>%s</alwaysusedefaultname>\n\t<veronstartup>%s</veronstartup>\n\t<theme>%s</theme>\n\t<sfx>%s</sfx>\n\t<nickname>%s</nickname>\n\t<password>%s</password>\n</spaceinvaders>" % (SETTINGS['usenet'],SETTINGS['trackhighscores'],SETTINGS['alwaysusedefaultname'],SETTINGS['veronstartup'],SETTINGS['theme'],SETTINGS['sfx'],SETTINGS['nickname'],SETTINGS['password'])
	except:
		SETTINGS = {'nickname': '','password': '', 'alwaysusedefaultname': '0', 'trackhighscores': '1', 'usenet': '0', 'veronstartup': '1', 'theme': '-1', 'sfx': '1'}
		curdat = "<spaceinvaders>\n\t<usenet>%s</usenet>\n\t<trackhighscores>%s</trackhighscores>\n\t<alwaysusedefaultname>%s</alwaysusedefaultname>\n\t<veronstartup>%s</veronstartup>\n\t<theme>%s</theme>\n\t<sfx>%s</sfx>\n\t<nickname>%s</nickname>\n\t<password>%s</password>\n</spaceinvaders>" % (SETTINGS['usenet'],SETTINGS['trackhighscores'],SETTINGS['alwaysusedefaultname'],SETTINGS['veronstartup'],SETTINGS['theme'],SETTINGS['sfx'],SETTINGS['nickname'],SETTINGS['password'])
	fb.write(curdat)
	fb.close()
def loadSettings():
	global SETTINGS
	if not os.path.exists(SPACEINVADER_SETTINGS):
		SETTINGS = {'nickname': '','password': '', 'alwaysusedefaultname': '0', 'trackhighscores': '1', 'usenet': '0', 'veronstartup': '1', 'theme': '-1', 'sfx': '1'}
		saveSettings()
	fb = open(SPACEINVADER_SETTINGS,'r')
	indat = fb.read()
	fb.close()
	regp = '<([^<]*)>([^</]*)</'
	if indat == "":
		SETTINGS = {'nickname': '','password': '', 'alwaysusedefaultname': '0', 'trackhighscores': '1', 'usenet': '0', 'veronstartup': '1', 'theme': '-1', 'sfx': '1'}
		saveSettings()
		loadSettings()
		return
	save_info = re.compile(regp,re.IGNORECASE).findall(indat)
	for x in save_info:
		SETTINGS[x[0]] = x[1]

def checkVoS():
	print "Checking Space Invaders Version"
	olv = "1.0"
	VOS_URL =  "%s?s=Check+For+Update" % SYSTEM_URL
	DLD_URL =  "%s?s=Download" % SYSTEM_URL
	try:
		html = urllib.urlopen(VOS_URL).read()
		t = re.search("<skinversion>([^</]*)</skinversion>",html)
		olv =  t.group(1)
	except:
		print "Error Checking Version"
	print "Running Version %s  [%s].   Online Version: %s" % (__version__,__date__,olv)
	if float(olv) > float(__version__):
		xbmc.executebuiltin("XBMC.Notification(Space Invaders,New version)")
		retval = xbmcgui.Dialog().yesno(__title__,"Found a New Version","Press Yes to Download It")
		if retval == 1:
			dp = xbmcgui.DialogProgress()
			dp.create(__title__,lang.string(35),"New Space invaders")
			rv2 = DownloaderClass(DLD_URL,"E:\\si.zip",dp)
			if rv2:
				try:
					fb = open("Z:\\updateSI.py",'w')
					fb.write(UPDATERSTRING)
					fb.close()
					return "CLOSE2"
				except:
					print "Update Script Failed"
	return ""

def DownloaderClass(url,dest,dp):
	xbmc.executehttpapi('FileDelete(' + dest +')')
	try:
		urllib.urlretrieve(url,dest,lambda nb, bs, fs, url=url: _pbhook(nb,bs,fs,url,dp))
		dp.close()
		return 1
	except:
		dp.close()
		xbmc.executebuiltin(('XBMC.Notification(%s,%s)' % (__title__, lang.string(36))))
		return 0

def _pbhook(numblocks, blocksize, filesize, url=None,dp=None,ratio=1.0):
	try:
		percent = min((numblocks*blocksize*100)/filesize, 100)
		dp.update(int(percent*ratio))
	except:
		percent = 100
		dp.update(int(percent*ratio))
	if dp.iscanceled():
		raise IOError

def FS(fs):
	fo = str(fs)
	if fs > 1024:
		fs = fs / 1024
		fo = str(fs) + " KB"
	elif fs > 1024*2:
		fs = fs / 1024 / 1024
		fo = str(fs) + " MB"
	else:
		fo = str(fs) + " Bytes"
	return fo

def XBMCVND():
	print "-Checking XBMC Version and Date"
	if not Emulating:
		try:
			res = xbmc.executehttpapi("GetSystemInfo(120;121)").split("<li>")
		except:
			res = ['','1.1.0','20 May 2006']
	else:
		res = ['','2.0.0','29 Sep 2006']
	print res
	ver = res[1]
	#date = res[2]
	if str(ver) == "2.0.0":
		return ""
	else:
		xbmcgui.Dialog().ok(__title__,"This script is desinged for XBMC 2.0","Please Upgrade or downgrade")
		print "--XBMC Version and Date Incorrect %s" %  ver
		return "CLOSE"

def MyDialogLoader(type,title="",line1="",line2="",line3=""):
	if type == 0:
		mydialog = MyDialogYesNo(title=title,line1=line1,line2=line2,line3=line3)
	elif type == 2:
		mydialog = MyDialogYesNoOkLite(mode=0,posy=int(title))
	elif type == 3:
		mydialog = MyDialogYesNoOkLite(mode=1,posy=int(title))
	elif type == 4:
		mydialog = MyDialogYesNo(title=title,line1=line1,line2=line2,line3=line3,mode=1)
	else:
		mydialog = MyDialogYesNo(title=title,line1=line1,line2=line2,line3=line3)
	mydialog.doModal()
	retval = mydialog.value
	del mydialog
	return retval

def SFX(fn=""):
	if SETTINGS['sfx']:
		purl = "%s%s%s.wav" % (Root,MEDIA_FOLDER,fn)
		if not os.path.exists(purl):
			purl = "%s\\%s\\%s.wav" % (Root,"Music",fn)
			xbmc.playSFX(purl)
		else:
			xbmc.playSFX(purl)

def loadThemeList():
	themelist = []
	if  os.path.exists(ThemeFolder):
		try:
			test = os.listdir(ThemeFolder)
		except:
			test = []
		if test != []:
			for x in test:
				if os.path.isdir(ThemeFolder+x):
					themelist.append(x)
	return themelist
#--- Main Function---#000000#FFFFFF-----------------------------------------
def main():
	print "Starting  %s    Version: %s " % ( __title__,__version__)
	#retvo = XBMCVND()
	retvo = ""
	if retvo == "CLOSE": return 0
	global lang
	lang = Language()
	lang.load(LangFolder)
	if int(SETTINGS['usenet']):
		if int(SETTINGS['veronstartup']):
			retvo = checkVoS()
			if retvo == "CLOSE2":
				print "Closing " + __title__
				return 1
		if (SETTINGS['trackhighscores']):
			global GAME_ID
			global USER_ID
			GAME_ID = ONLINEHIGHSCORE.get_game_id("SpaceInvaders")
			USER_ID = str(ONLINEHIGHSCORE.get_user_id(SETTINGS['nickname'],SETTINGS['password']))
	if FileCheker("images\\",theimages):
		xbmcgui.Dialog().ok(__title__,lang.string(21),lang.string(24),lang.string(23))
		retvo = "CLOSE"
	global themes
	themes = loadThemeList()
	if not retvo == "CLOSE":
		mainwin = MainMenu()
		mainwin.doModal()
		del mainwin
	print "Closing " + __title__
	return 0

if __name__ == "__main__":
	WasPlaying = xbmc.Player().isPlaying()
	loadSettings()
	v = main()
	if v:
		xbmc.executebuiltin('XBMC.RunScript(Z:\\updateSI.py)')
	else:
		saveSettings()