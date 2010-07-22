#
# Snake-Game for XBMC
# a Project of Rocko, tAGEdIEB and JackTramiel
#














__title__		= "Snake"
__addonID__		= "script.game.tetris"
__version__		= '0.95'
__coder__		= 'Rocko aka Rockstar'
__designer__	= 'Jack Tramiel'
__author__		= 'Rocko [rocko@fallout-band.de]'
__date__		= 'June/July 2006'
__maintaner__	= __coder__
__credits__		= 'Coded by ' + __coder__ + '\nGraphics by ' + __designer__


########## IMPORTS ###############
import xbmc, xbmcgui
import os,os.path
import time
import glob
import xml.dom.minidom
import thread
import random
import re
import urllib

########## STANDARDS & GLOBALS ###############
HOME_DIR						= os.getcwd()
HOME_DIR						= HOME_DIR+'\\'
SRC_DIR							= HOME_DIR+"src\\"
LIB_DIR							= SRC_DIR+"libary\\"
LANG_DIR						= SRC_DIR+"languages\\"
MEDIA_DIR						= SRC_DIR+"media\\"
THEME_DIR						= SRC_DIR+"levelthemes\\"
LEVEL_DIR						= SRC_DIR+"level\\"
CLEVEL_DIR						= SRC_DIR+"custom_level\\"
#SETTINGSPATH					= "P:\\snake\\"
#SETTINGSFILE					= "settings.xml"
GAMERPICTURE					= "gamerpicture.jpg"
INFOFILE						= SRC_DIR+"info.xml"
HIGHSCOREFILE					= SRC_DIR+"highscores.xml"
LEVELURL						= "http://snake.dirtyduckdesigns.de/pages/script/"

SPECIAL_PROFILE_DIR = xbmc.translatePath( "special://profile/" )
SPECIAL_SCRIPT_DATA = os.path.join( SPECIAL_PROFILE_DIR, "addon_data", __addonID__ )
if not os.path.isdir( SPECIAL_SCRIPT_DATA ): os.makedirs( SPECIAL_SCRIPT_DATA )
SNAKE_SETTINGS = os.path.join( SPECIAL_SCRIPT_DATA, "settings.xml" )
SNAKE_SCORES = os.path.join( SPECIAL_SCRIPT_DATA, "scores.txt" )

sys.path.append(LIB_DIR)
import lang
import level
import highscore
import onlinehighscores
import secure

ONLINEHIGHSCORE=onlinehighscores.highscore()
lsec = secure.Secure()

######### KEY - FUNCTIONS ################
ACTION_DPAD_LEFT				= 1
ACTION_DPAD_RIGHT				= 2
ACTION_DPAD_UP					= 3
ACTION_DPAD_DOWN				= 4
ACTION_SELECT_ITEM				= 7
ACTION_PARENT_DIR				= 9
ACTION_YBUTTON					= 34
ACTION_PREVIOUS_MENU			= 10
ACTION_INFO_BUTTON				= 11
ACTION_SELDIR					= 117
ACTION_RT						= 112 # Right Trigger
ACTION_LT						= 111 # Left Trigger

######## PROGRESS POSITIONS #############
PROGRESS_POSITIONS_BG			= [60,520,600,30]
PROGRESS_POSITIONS_LABEL		= [70,526,250,25]
PROGRESS_POSITIONS_BAR			= [330,530,320,10]

######## ANIMATION POSITIONS ############
SELECT_ANI_FROM					= "right"
SELECT_POSITIONS_BG				= [360,35,300,500]
SELECT_POSITIONS_TITLE			= [380,50,250,30]
SELECT_POSITIONS_LIST			= [380,100,250,450]

HIGHSCORE_ANI_FROM				= "left"
HIGHSCORE_POSITIONS_BG			= [100,100,520,376]
HIGHSCORE_POSITIONS_LIST		= [170,130,300,300]
HIGHSCORE_POSITIONS_LABEL		= [120,110,300,30]
HIGHSCORE_POSITIONS_BUTTON		= [480,128,100,30]
HIGHSCORE_POSITIONS_BUTTON2		= [480,168,100,30]

MESSAGE_ANI_FROM				= "right"
MESSAGE_POSITIONS_BG			= [210,200,300,180]
MESSAGE_POSITIONS_TITLE			= [225,220,260,30]
MESSAGE_POSITIONS_TEXT			= [225,260,260,110]
MESSAGE_POSITIONS_BUTTON		= [410,336,80,30]

YESNO_ANI_FROM					= "right"
YESNO_POSITIONS_BG				= [210,200,300,180]
YESNO_POSITIONS_TITLE			= [225,220,260,30]
YESNO_POSITIONS_TEXT			= [225,260,260,110]
YESNO_POSITIONS_BUTTON			= [320,336,80,30]
YESNO_POSITIONS_BUTTON2			= [410,336,80,30]

PROFILE_ANI_FROM				= "right"
PROFILE_POSITIONS_BG			= [100,100,520,376]
PROFILE_POSITIONS_LIST			= [130,130,200,300]
PROFILE_POSITIONS_TEXT			= [360,130,280,80]
PROFILE_POSITIONS_TEXT2			= [140,250,460,400]
PROFILE_POSITIONS_GP			= [150,250,150,150]

OHIGHSCORE_ANI_FROM				= "left"
OHIGHSCORE_POSITIONS_BG			= [100,100,520,376]
OHIGHSCORE_POSITIONS_LIST		= [120,120,160,336]
OHIGHSCORE_POSITIONS_HS			= [300,120,300,336]







def save_current_settings():
	print "saving settings"

	temp = glob.settings.keys()
	output = "<settings>\n"
	for item in temp:
		#print item + " = " + glob.settings[item]
		output += "  <" + item + ">" + glob.settings[item] + "</" + item + ">\n"
	output += "</settings>"

	aefile = SNAKE_SETTINGS
	if os.path.exists(aefile):
		os.unlink(aefile)
	f=open(str(aefile),'w')
	f.write(str(output))
	f.close()
	print "settings saved"
	print "-----------------------------"

def save_highscore():
	print "saving highscore"
	temp = glob.highscores.keys()
	output = "<highscores>\n"
	for item in temp:
		output += "  <highscore>"
		output += "<name>" + glob.highscores[item]["name"] + "</name>"
		output += "<score>" + str(glob.highscores[item]["score"]) + "</score>"
		output += "<level>" + glob.highscores[item]["level"] + "</level>"
		output += "</highscore>\n"
	output += "</highscores>"

	aefile = HIGHSCOREFILE
	if os.path.exists(aefile):
		os.unlink(aefile)
	f=open(str(aefile),'w')
	f.write(str(output))
	f.close()
	print "highscore saved"
	print "-----------------------------"

def play_sound(toplay, ltheme=""):
	if toplay != "":
		if ltheme != "":
			playpath = THEME_DIR + ltheme + "\\sounds\\" + toplay + ".wav"
			if not os.path.exists(playpath):
				playpath = SRC_DIR + "sounds\\" + toplay + ".wav"
		else:
			playpath = SRC_DIR + "sounds\\" + toplay + ".wav"

		if os.path.exists(playpath):
			xbmc.playSFX(playpath)

def check_connection():
	try:
		glob.OHSGameID = ONLINEHIGHSCORE.get_game_id(__title__)
		if glob.OHSGameID.split("\n")[0].strip() == "<HTML>":
			glob.CONNECTION = 0
			glob.OHSGameID = "0"
			print "no internet connection detected - onlinefeatures are not available"
		else:
			glob.CONNECTION = 1
			print "internet connection detected"
	except:
		glob.OHSGameID = "0"
		glob.CONNECTION = 0
		print "no internet connection detected - onlinefeatures are not available"
	print "GameID: " + glob.OHSGameID

def create_game_in_db():
	if glob.OHSGameID == "0" or glob.OHSGameID == "-1":
		glob.OHSGameID = ONLINEHIGHSCORE.create_new_game(__title__)













class Main(xbmcgui.Window):
########################################################################################
############################### MAIN CLASS #############################################
########################################################################################
	def __init__(self):
		self.setCoordinateResolution(6)
		self.initing = 1
		self.loadscreen = xbmcgui.ControlImage(0,
												0,
												720,
												576,
												MEDIA_DIR + "splash.png"
												)
		self.addControl(self.loadscreen)


	def load_stuff(self):
		progressbar = Progress(text="loading...")
		progressbar.show()
		progressbar.update_progress(1,"loading Settings")
		self.load_settings()
		self.load_info()
		self.load_highscore()
		progressbar.update_progress(25,"loading language")
		self.load_language()
		progressbar.update_progress(50,glob.language.string(5))
		self.get_levels()
		self.get_custom_levels()
		time.sleep(0.5)
		progressbar.update_progress(75,glob.language.string(7))
		self.build_menu()
		progressbar.update_progress(100,glob.language.string(8))
		time.sleep(0.5)
		progressbar.close()
		del progressbar
		self.removeControl(self.loadscreen)
		self.initing = 0
		play_sound("start")
		self.show_menu()
		self.setInfo()





	def onControl(self, control):
		if control == self.startButton:
			play_sound("menu_select")
			self.all_levels=glob.levels+glob.clevels
			selection1 = Select(titre=glob.language.string(9),leschoix=self.all_levels)
			selection1.show()
			selection1.show_panel()
			selection1.doModal()
			self.selected=selection1.retour
			del selection1

			if self.selected != "":
				self.startclass = Game(thelevel=self.all_levels[self.selected])
				self.startclass.show()
				self.startclass.load_field()
				self.startclass.doModal()
				del self.startclass

		if control == self.quitButton:
			play_sound("menu_back")
			self.close()

		if control == self.highscoreButton:
			play_sound("menu_select")
			hClass = Highscore()
			hClass.show()
			hClass.show_panel()
			hClass.doModal()
			del hClass

		if control == self.leveleditorButton:
			play_sound("menu_select")
			selection1 = LEMenu()
			selection1.doModal()
			del selection1

		if control == self.onlineButton:
			if glob.CONNECTION == 1:
				play_sound("menu_select")
				selection1 = Online()
				selection1.doModal()
				del selection1
			else:
				self.message(glob.language.string(10),glob.language.string(11)+"\n"+glob.language.string(12))

	def onAction(self, action):
		play_sound("menu_move")
		self.setInfo()





	def message(self, title, message):
		themessage = Message(title=title,message=message)
		themessage.show()
		themessage.show_panel()
		themessage.doModal()
		del themessage


	def question(self, title, question):
		themessage = YesNo(title=title,question=question)
		themessage.show()
		themessage.show_panel()
		themessage.doModal()
		self.temp = themessage.give
		del themessage
		return self.temp


	def load_settings(self):
		glob.settings = {}
		
		glob.settings["animation"] = "1"
		glob.settings["name"] = "-"
		glob.settings["pass"] = "-"
		glob.settings["userID"] = "0"
		glob.settings["localname"] = "-"
		glob.settings["check_update_startup"] = "1"
		
		print "loading settings..."
		self.settingspath = SNAKE_SETTINGS
		if os.path.exists(self.settingspath):
			sf_exists = 1
			try:
				doc = xml.dom.minidom.parse(self.settingspath)
				error = "no"
			except:
				print "cant read File: \"settings.xml\""
				print "File \"settings.xml\" is probably damaged!"
				error = "yes"
		else:
			sf_exists = 0
			error = "yes"

		if error != "yes":
			parent = doc.getElementsByTagName("settings")[0]
			for child in parent.childNodes:
				if str(child.nodeName) != "#text":
					glob.settings[str(child.nodeName)]=str(child.childNodes[0].nodeValue)
			print "loading settings successfull"

		if sf_exists == 0:
			save_current_settings()
			print "settings created"
		print "-----------------------------"


	def load_info(self):
		glob.info = {}
		print "loading scriptinfo..."
		self.infopath = INFOFILE
		if os.path.exists(self.infopath):
			if_exists = 1
			try:
				doc = xml.dom.minidom.parse(self.infopath)
				error = "no"
			except:
				print "cant read File: \"info.xml\""
				print "File \"info.xml\" is probably damaged!"
				error = "yes"
		else:
			if_exists = 0
			error = "yes"

		if error != "yes":
			parent = doc.getElementsByTagName("info")[0]
			for child in parent.childNodes:
				if str(child.nodeName) != "#text":
					glob.info[str(child.nodeName)]=str(child.childNodes[0].nodeValue)
			print "loading info successfull"
		print "-----------------------------"


	def load_highscore(self):
		glob.highscores = {}
		self.highscorefile = HIGHSCOREFILE

		if not os.path.exists(self.highscorefile):
			save_highscore()
	
		print "loading highscores"
		try:
			f=open(self.highscorefile,'r')
			self.tempstrings=f.readlines()
			f.close()
		except:
			print "Error loading highscores"

		self.exp="""<highscore><name>(.*?)</name><score>(.*?)</score><level>(.*?)</level></highscore>"""

		self.id = 0
		for self.line in self.tempstrings:
			try:
				self.res=re.findall(self.exp,self.line)
				self.results = self.res[0]
			except:
				self.results=0

			if self.results != 0:
				glob.highscores[self.id] = {}
				glob.highscores[self.id]["name"] = str(self.results[0])
				glob.highscores[self.id]["score"] = int(self.results[1])
				glob.highscores[self.id]["level"] = str(self.results[2])
				self.id += 1
		print "highscores loaded"

	def load_language(self):
		glob.language = lang.Language()
		glob.language.load(LANG_DIR)
		print "-----------------------------"

	def get_levels(self):
		glob.levels = []
		for item in os.listdir(LEVEL_DIR):
			if item.split(".")[-1] == "xml":
				glob.levels.append(item.replace(".xml",""))
		glob.levels.sort()

	def get_custom_levels(self):
		glob.clevels = []
		for item in os.listdir(CLEVEL_DIR):
			if item.split(".")[-1] == "xml":
				glob.clevels.append(item.replace(".xml",""))
		glob.clevels.sort()






	def build_menu(self):
		self.mainbg = xbmcgui.ControlImage(0,
											0,
											720,
											576,
											MEDIA_DIR + "background.png"
											)
		self.mainbg.setVisible(0)
		self.addControl(self.mainbg)

		self.credits = xbmcgui.ControlLabel(420,
											30,
											600,
											360,
											"Version: "+glob.info["version"]+"\ncoded by: "+glob.info["coder"]+"\ngraphics by: "+glob.info["gfx"]+"\n"+glob.info["special"]+"\nthanks to: "+glob.info["thanks"],
											#"Test",
											"font10",
											"FFFFFFFF"
											)
		self.credits.setVisible(0)
		self.addControl(self.credits)


		self.logo = xbmcgui.ControlImage(30,
										30,
										340,
										248,
										MEDIA_DIR + "logo_medium.png"
										)
		self.logo.setVisible(0)
		self.addControl(self.logo)


		self.startButton = xbmcgui.ControlButton(70,
												450,
												100,
												100,
												"",
												MEDIA_DIR + "buttons\\button_game_active.png",
												MEDIA_DIR + "buttons\\button_game.png"
												)
		self.startButton.setVisible(0)
		self.addControl(self.startButton)

		self.highscoreButton = xbmcgui.ControlButton(190,
												450,
												100,
												100,
												"",
												MEDIA_DIR + "buttons\\button_editor_active.png",
												MEDIA_DIR + "buttons\\button_editor.png"
												)
		self.highscoreButton.setVisible(0)
		self.addControl(self.highscoreButton)

		self.leveleditorButton = xbmcgui.ControlButton(310,
														450,
														100,
														100,
														"",
														MEDIA_DIR + "buttons\\button_settings_active.png",
														MEDIA_DIR + "buttons\\button_settings.png"
														)
		self.leveleditorButton.setVisible(0)
		self.addControl(self.leveleditorButton)
		
		self.onlineButton = xbmcgui.ControlButton(430,
												450,
												100,
												100,
												"",
												MEDIA_DIR + "buttons\\button_online_active.png",
												MEDIA_DIR + "buttons\\button_online.png"
												)
		self.onlineButton.setVisible(0)
		self.addControl(self.onlineButton)

		self.quitButton = xbmcgui.ControlButton(550,
												450,
												100,
												100,
												"",
												MEDIA_DIR + "buttons\\button_running_active.png",
												MEDIA_DIR + "buttons\\button_running.png"
												)
		self.quitButton.setVisible(0)
		self.addControl(self.quitButton)

		self.infoShadowLabel = xbmcgui.ControlLabel(497,
													407,
													520,
													200,
													"",
													"font13",
													"FF000000"
													)
		self.infoShadowLabel.setVisible(0)
		self.addControl(self.infoShadowLabel)

		self.infoLabel = xbmcgui.ControlLabel(495,
											405,
											520,
											200,
											"",
											"font13",
											"FFFFFFFF"
											)
		self.infoLabel.setVisible(0)
		self.addControl(self.infoLabel)

		self.startButton.controlUp(self.quitButton)
		self.startButton.controlDown(self.highscoreButton)
		self.startButton.controlLeft(self.quitButton)
		self.startButton.controlRight(self.highscoreButton)

		self.highscoreButton.controlUp(self.startButton)
		self.highscoreButton.controlDown(self.leveleditorButton)
		self.highscoreButton.controlLeft(self.startButton)
		self.highscoreButton.controlRight(self.leveleditorButton)

		self.leveleditorButton.controlUp(self.highscoreButton)
		self.leveleditorButton.controlDown(self.onlineButton)
		self.leveleditorButton.controlLeft(self.highscoreButton)
		self.leveleditorButton.controlRight(self.onlineButton)
		
		self.onlineButton.controlUp(self.leveleditorButton)
		self.onlineButton.controlDown(self.quitButton)
		self.onlineButton.controlLeft(self.leveleditorButton)
		self.onlineButton.controlRight(self.quitButton)
		
		self.quitButton.controlUp(self.onlineButton)
		self.quitButton.controlDown(self.startButton)
		self.quitButton.controlLeft(self.onlineButton)
		self.quitButton.controlRight(self.startButton)

		self.setFocus(self.startButton)

	def show_menu(self):
		self.mainbg.setVisible(1)
		self.logo.setVisible(1)
		#self.infobg.setVisible(1)
		self.startButton.setVisible(1)
		self.highscoreButton.setVisible(1)
		self.leveleditorButton.setVisible(1)
		self.onlineButton.setVisible(1)
		self.quitButton.setVisible(1)
		self.infoLabel.setVisible(1)
		self.credits.setVisible(1)
		self.infoShadowLabel.setVisible(1)


	def setInfo(self):
		if self.initing == 0:
			theObj =self.getFocus()
			if theObj == self.startButton:
				self.infoLabel.setLabel(glob.language.string(0))
				self.infoShadowLabel.setLabel(glob.language.string(0))
			if theObj == self.highscoreButton:
				self.infoLabel.setLabel(glob.language.string(1))
				self.infoShadowLabel.setLabel(glob.language.string(1))
			if theObj == self.leveleditorButton:
				self.infoLabel.setLabel(glob.language.string(2))
				self.infoShadowLabel.setLabel(glob.language.string(2))
			if theObj == self.onlineButton:
				self.infoLabel.setLabel(glob.language.string(3))
				self.infoShadowLabel.setLabel(glob.language.string(3))
			if theObj == self.quitButton:
				self.infoLabel.setLabel(glob.language.string(4))
				self.infoShadowLabel.setLabel(glob.language.string(4))














	def hook(self, count_blocks, block_size, total_size):
		current_size = block_size * count_blocks
		value = current_size * 100 / total_size
		self.progressbar.update_progress(value,glob.language.string(18))

	def save(self, url,destination):
		try:
			DL=urllib.urlretrieve( url , destination , self.hook)
		except:
			print "exception while downloading"



class Game(xbmcgui.Window):
########################################################################
######################### Game Class ###################################
########################################################################
	def __init__(self,thelevel=""):
		self.setCoordinateResolution(6)
		xbmcgui.Window.__init__(self)

		self.mainbg = xbmcgui.ControlImage(0,
											0,
											720,
											576,
											MEDIA_DIR + "background.png"
											)
		self.addControl(self.mainbg)

		self.theLevel = thelevel
		self.running = 0
		self.paused = 0
		self.error = 0

		glob.direction = 1
		glob.newdirection = 1
		self.fieldsize = 12

	def zoom_picture(self,picture,fps,wait):
		if int(glob.leveldata.get("width")) <= int(glob.leveldata.get("height")):
			self.countpicWidth = int(glob.leveldata.get("width"))*self.fieldsize
		else:
			self.countpicWidth = int(glob.leveldata.get("height"))*self.fieldsize

		self.countpicPosX = self.startposX + (int(glob.leveldata.get("width"))*self.fieldsize/2) - (int(self.countpicWidth)/2)
		self.countpicPosY = self.startposY + (int(glob.leveldata.get("height"))*self.fieldsize/2) - (int(self.countpicWidth)/2)

		self.tempImage = xbmcgui.ControlImage(self.countpicPosX,
												self.countpicPosY,
												1,
												1,
												MEDIA_DIR + picture
												)
		self.addControl(self.tempImage)

		for i in range(fps):
			time.sleep(0.04)
			self.newTempWidth = (self.countpicWidth/fps)*i
			self.newTempX = self.countpicPosX + ((self.countpicWidth-self.newTempWidth)/2)
			self.newTempY = self.countpicPosY + ((self.countpicWidth-self.newTempWidth)/2)
			if self.newTempWidth > 1:
				self.tempImage.setWidth(self.newTempWidth)
				self.tempImage.setHeight(self.newTempWidth)

				self.tempImage.setPosition(self.newTempX,self.newTempY)

		time.sleep(wait)

		self.removeControl(self.tempImage)

	def create_overlays(self):
		self.pauseImage = xbmcgui.ControlImage(0,
												0,
												1,
												1,
												MEDIA_DIR + "pause.png"
												)
		self.addControl(self.pauseImage)
		self.pauseImage.setVisible(0)
		self.pauseImage.setWidth(720)
		self.pauseImage.setHeight(576)


	def restart_game(self):
		glob.snakefood[glob.food[0]].setVisible(0)
		self.removeControl(self.scoreLabel)
		for item in glob.snake_pos:
			glob.snakehead[item].setVisible(0)
			glob.snakepart[item].setVisible(0)

		self.create_score()
		self.create_snake()

		progressbar = Progress(text=glob.language.string(17))
		progressbar.show()
		progressbar.update_progress(1,glob.language.string(21))

		self.zoom_picture("3.png",8,0)
		progressbar.update_progress(33,glob.language.string(22))
		self.zoom_picture("2.png",8,0)
		progressbar.update_progress(66,glob.language.string(23))
		self.zoom_picture("1.png",8,0)
		progressbar.update_progress(100,glob.language.string(24))
		self.zoom_picture("go.png",3,0.5)
		progressbar.close()
		del progressbar

		self.running = 1
		self.food_set = 0
		glob.newdirection = 1
		thread.start_new_thread(self.food,())

	def load_field(self):
		try:
			self.load_level(self.theLevel)
		except:
			self.message(glob.language.string(25),glob.language.string(26))
			self.error = 1
			self.close()

		if self.error == 0:
			self.get_startpos()
			self.create_ground()
			self.create_walls(self.theLevel)
			self.create_score()
			self.create_snake()

		progressbar = Progress(text=glob.language.string(17))
		progressbar.show()
		progressbar.update_progress(1,glob.language.string(21))

		self.zoom_picture("3.png",25,0)
		progressbar.update_progress(33,glob.language.string(22))
		self.zoom_picture("2.png",25,0)
		progressbar.update_progress(66,glob.language.string(23))
		self.zoom_picture("1.png",25,0)
		progressbar.update_progress(100,glob.language.string(24))
		self.zoom_picture("go.png",12,0.5)
		progressbar.close()
		del progressbar
		self.running = 1
		self.food_set = 0
		thread.start_new_thread(self.loop,())
		thread.start_new_thread(self.food,())


	def onAction(self,action):
		if self.running == 0:
			play_sound("menu_move")
		if action == ACTION_PREVIOUS_MENU:
			if self.running == 1:
				self.running = 0
				self.close()

		if action == ACTION_SELECT_ITEM:
			if self.running == 1:
				if self.paused == 0:
					self.paused = 1
					self.pauseImage.setVisible(1)
				else:
					self.paused = 0
					self.pauseImage.setVisible(0)

		if action == ACTION_DPAD_LEFT and glob.direction != 2:
			glob.newdirection = 1
			play_sound("snake_move", glob.leveldata.get("style"))
		if action == ACTION_DPAD_RIGHT and glob.direction != 1:
			glob.newdirection = 2
			play_sound("snake_move", glob.leveldata.get("style"))
		if action == ACTION_DPAD_UP and glob.direction != 4:
			glob.newdirection = 3
			play_sound("snake_move", glob.leveldata.get("style"))
		if action == ACTION_DPAD_DOWN and glob.direction != 3:
			glob.newdirection = 4
			play_sound("snake_move", glob.leveldata.get("style"))




	def message(self, title, message):
		themessage = Message(title=title,message=message)
		themessage.show()
		themessage.show_panel()
		themessage.doModal()
		del themessage

	def question(self, title, question):
		themessage = YesNo(title=title,question=question)
		themessage.show()
		themessage.show_panel()
		themessage.doModal()
		self.temp = themessage.give
		del themessage
		return self.temp


	def load_level(self,loadlevel):
		glob.leveldata = level.Level()
		if os.path.exists(LEVEL_DIR + loadlevel + ".xml"):
		
			self.theCheck = lsec.check_level(LEVEL_DIR + loadlevel + ".xml")
			if self.theCheck == 0:
				self.message("Error","level has been edited\nno onlinehighscore possible")
				self.levelChanged = 1
			elif self.theCheck == 1:
				self.levelChanged = 0
			else:
				self.levelChanged = 1

			glob.leveldata.load(LEVEL_DIR + loadlevel + ".xml")
			self.custom_level = 0
		else:
			glob.leveldata.load(CLEVEL_DIR + loadlevel + ".xml")
			self.custom_level = 1
		print "-----------------------------"


	def get_startpos(self):
		self.startposX = (720 - (self.fieldsize*int(glob.leveldata.get("width"))))/2
		self.startposY = (576 - (self.fieldsize*int(glob.leveldata.get("height"))))/2

		if glob.leveldata.get("speed") == "1":
			glob.speed = 1
		if glob.leveldata.get("speed") == "2":
			glob.speed = 0.6
		if glob.leveldata.get("speed") == "3":
			glob.speed = 0.3
		if glob.leveldata.get("speed") == "4":
			glob.speed = 0.1
		if glob.leveldata.get("speed") == "5":
			glob.speed = 0.08
		if glob.leveldata.get("speed") == "6":
			glob.speed = 0.06
		if glob.leveldata.get("speed") == "7":
			glob.speed = 0.04
		if glob.leveldata.get("speed") == "8":
			glob.speed = 0.03
		if glob.leveldata.get("speed") == "9":
			glob.speed = 0.02
		if glob.leveldata.get("speed") == "10":
			glob.speed = 0.01



	def create_ground(self):
		self.field_background = xbmcgui.ControlImage(self.startposX-20,
													self.startposY-20,
													int(glob.leveldata.get("width"))*self.fieldsize+40,
													int(glob.leveldata.get("height"))*self.fieldsize+40,
													MEDIA_DIR + "box_black.png"
													)
		self.addControl(self.field_background)


		glob.food = ["0,0"]
		glob.snakepart = {}
		glob.snakehead = {}
		glob.snakefood = {}
		glob.snakepart_coords = []

		progressbar = Progress(text=glob.language.string(17))
		progressbar.show()
		progressbar.update_progress(1,glob.language.string(27))



		for numberY in range(int(glob.leveldata.get("height"))):
			progressbar.update_progress(numberY*100/int(glob.leveldata.get("height")),glob.language.string(27))
			for numberX in range(int(glob.leveldata.get("width"))):
				self.groundpart = xbmcgui.ControlImage(self.startposX+(self.fieldsize*numberX),
														self.startposY+(self.fieldsize*numberY),
														self.fieldsize,
														self.fieldsize,
														THEME_DIR + glob.leveldata.get("style") + "\\ground.png"
														)
				self.addControl(self.groundpart)

				temp = str(numberX)+","+str(numberY)
				glob.snakepart[temp] = xbmcgui.ControlImage(self.startposX+(self.fieldsize*int(numberX)),
																			self.startposY+(self.fieldsize*int(numberY)),
																			self.fieldsize,
																			self.fieldsize,
																			THEME_DIR + glob.leveldata.get("style") + "\\snake_body.png"
																			)
				self.addControl(glob.snakepart[temp])

				glob.snakefood[temp] = xbmcgui.ControlImage(self.startposX+(self.fieldsize*int(numberX)),
																			self.startposY+(self.fieldsize*int(numberY)),
																			self.fieldsize,
																			self.fieldsize,
																			THEME_DIR + glob.leveldata.get("style") + "\\food.png"
																			)
				self.addControl(glob.snakefood[temp])

				glob.snakehead[temp] = xbmcgui.ControlImage(self.startposX+(self.fieldsize*int(numberX)),
																			self.startposY+(self.fieldsize*int(numberY)),
																			self.fieldsize,
																			self.fieldsize,
																			THEME_DIR + glob.leveldata.get("style") + "\\snake_head.png"
																			)
				self.addControl(glob.snakehead[temp])

				glob.snakehead[temp].setVisible(0)
				glob.snakefood[temp].setVisible(0)
				glob.snakepart[temp].setVisible(0)

		progressbar.close()
		del progressbar

	def create_walls(self,loadlevel):
		glob.walls = []
		if os.path.exists(LEVEL_DIR + loadlevel + ".xml"):
			self.aefile = LEVEL_DIR + loadlevel + ".xml"
		else:
			self.aefile = CLEVEL_DIR + loadlevel + ".xml"

		f=open(self.aefile,"r")
		self.xmldata = f.read()
		f.close()
		self.walldata = self.xmldata.split("<walls>")[1].split("</walls>")[0].split("\n")
		self.max = len(self.walldata)
		self.current = 0

		progressbar = Progress(text=glob.language.string(17))
		progressbar.show()
		progressbar.update_progress(1,"create walls")


		for wall in self.walldata:
			progressbar.update_progress(self.current*100/self.max,"creating walls")
			if wall.strip() != "":
				wallx = int(wall.split("<x>")[1].split("</x>")[0]) -1
				wally = int(wall.split("<y>")[1].split("</y>")[0]) -1

				glob.walls.append(str(wallx)+","+str(wally))
				
				self.wallpart = xbmcgui.ControlImage(self.startposX+(int(wallx)*self.fieldsize),
													self.startposY+(int(wally)*self.fieldsize),
													self.fieldsize,
													self.fieldsize,
													THEME_DIR + glob.leveldata.get("style") + "\\wall.png"
													)
				self.addControl(self.wallpart)
			self.current += 1
		progressbar.close()
		del progressbar

	def create_score(self):
		self.highscore_saved = 0
		self.score = highscore.Score()
		
		self.score_bg = xbmcgui.ControlImage(40,
											25,
											100,
											33,
											MEDIA_DIR + "box_black.png"
											)
		self.addControl(self.score_bg)

		self.scoreLabel = xbmcgui.ControlLabel(50,
												30,
												300,
												30,
												"",
												"font13",
												"#FFFFFFFF")
		self.addControl(self.scoreLabel)
		self.score.create_score()
		self.scoreLabel.setLabel(glob.language.string(28)+": "+str(self.score.get_current_score()))
		

	def create_snake(self):
		startx = int(int(glob.leveldata.get("width"))/2)
		starty = int(int(glob.leveldata.get("height"))/2)
		while 1:
			if str(startx)+","+str(starty) in glob.walls:
				random.seed(time.clock())
				startx = random.randint(1,int(glob.leveldata.get("width"))-1)
				starty = random.randint(1,int(glob.leveldata.get("height"))-1)
			else:
				break
		glob.snake_pos = []
		glob.snake_pos.append(str(startx) + "," + str(starty))
		for length in range(int(glob.leveldata.get("snake_startlength"))):
			if not str(startx+1)+","+str(starty) in glob.walls:
				if int(startx+1) < int(glob.leveldata.get("width")):
					startx += 1
			glob.snake_pos.append(str(startx) + "," + str(starty))

		self.head_added = 0
		for item in glob.snake_pos:
			if self.head_added == 1:
				glob.snakepart[item].setVisible(1)
			else:
				glob.snakehead[item].setVisible(1)
				self.head_added = 1

		self.create_overlays()


	def move_snake(self):
		self.current = glob.snake_pos[0].split(",")
		self.currentx = int(self.current[0])
		self.currenty = int(self.current[1])

		glob.direction = glob.newdirection
		
		if glob.direction == 1:
			if (self.currentx - 1) < 0:
				self.currentx = int(glob.leveldata.get("width"))
			self.next = str(self.currentx - 1) + "," + str(self.currenty)
		if glob.direction == 2:
			if (self.currentx - 1) >= int(glob.leveldata.get("width"))-2:
				self.currentx = -1
			self.next = str(self.currentx + 1) + "," + str(self.currenty)
		if glob.direction == 3:
			if (self.currenty - 1) < 0:
				self.currenty = int(glob.leveldata.get("height"))
			self.next = str(self.currentx) + "," + str(self.currenty - 1)
		if glob.direction == 4:
			if (self.currenty - 1) >= int(glob.leveldata.get("height"))-2:
				self.currenty = -1
			self.next = str(self.currentx) + "," + str(self.currenty + 1)

		if self.next in glob.snake_pos or self.next in glob.walls:
			self.running = 0
			play_sound("snake_dead", glob.leveldata.get("style"))
			self.kill_snake()
			self.end_game()
		else:
			#make head invisible and body visible
			temp = glob.snake_pos[0]
			glob.snakehead[temp].setVisible(0)
			glob.snakepart[temp].setVisible(1)

			#make end of snake invisible
			temp = glob.snake_pos[-1]
			glob.snakepart[temp].setVisible(0)
			glob.snake_pos.pop()

			#make new snakehead
			glob.snake_pos.insert(0,self.next)
			temp = self.next
			glob.snakehead[temp].setVisible(1)


		if self.next in glob.food:
			play_sound("snake_eat", glob.leveldata.get("style"))
			self.score.update_score(str(self.next))
			self.scoreLabel.setLabel(glob.language.string(28)+": "+str(self.score.get_current_score()))
			glob.snakefood[glob.food[0]].setVisible(0)
			glob.snake_pos.append("0,0")
			self.food_set = 0

	def save_to_highscore(self):
		if glob.CONNECTION == 1:
			self.check_account()
		else:
			self.theUID = "0"

		if self.theUID == "0" or self.levelChanged == 1:
			self.save_local = 1
			self.save_online = 0
		else:
			self.choices = [glob.language.string(29),glob.language.string(30),glob.language.string(31)]
			selection5 = Select(titre=glob.language.string(32),leschoix=self.choices)
			selection5.show()
			selection5.show_panel()
			selection5.doModal()
			self.selected5=selection5.retour
			del selection5

			if self.selected5 == 0:
				self.save_local = 1
				self.save_online = 0
			if self.selected5 == 1:
				self.save_online = 1
				self.save_local = 0
			if self.selected5 == 2:
				self.save_local = 1
				self.save_online = 1
			if self.selected5 == "":
				self.close()

		if self.save_local == 1:
			if glob.settings["localname"] == "-":
				self.oldname = glob.language.string(33)
			else:
				self.oldname = glob.settings["localname"]

			self.new_name = ""
			while self.new_name == "":
				keyboard = xbmc.Keyboard(self.oldname,glob.language.string(34))
				keyboard.doModal()
				if(keyboard.isConfirmed()):
					self.new_name = keyboard.getText()
					self.dont_save_local = 0
				else:
					if self.question(glob.language.string(36),glob.language.string(35)):
						self.dont_save_local = 1
						self.new_name = "-"

					else:
						self.new_name = ""
						self.dont_save_local = 0
	
			if self.dont_save_local == 0:
				self.newid = len(glob.highscores.keys())
				glob.highscores[self.newid] = {}
				glob.highscores[self.newid]["name"] = self.new_name
				glob.highscores[self.newid]["score"] = str(self.score.get_current_score())
				glob.highscores[self.newid]["level"] = self.theLevel
				save_highscore()
				self.message(glob.language.string(37),glob.language.string(38))
				glob.settings["localname"] = self.new_name

		if self.save_online == 1:
			self.LID = ONLINEHIGHSCORE.get_level_id(str(glob.OHSGameID),self.theLevel)
			if self.LID == "0":
				self.LID = ONLINEHIGHSCORE.create_new_level(self.theLevel,str(glob.OHSGameID))
			if self.LID == "0":
				self.message(glob.language.string(39),glob.language.string(40)+"\n"+glob.language.string(41))
			else:
				if int(self.score.get_current_score()) > int(self.getLastScore()):
					temp = ONLINEHIGHSCORE.insert_new_highscore(str(glob.OHSGameID),str(self.theUID),str(self.score.get_upload_score()),str(self.LID))
					if temp != "0":
						self.message(glob.language.string(37),glob.language.string(42))
					else:
						if temp == "error":
							self.message(glob.language.string(25),"an error occured\nDont try to cheat!")
						else:
							self.message(glob.language.string(25),glob.language.string(41))
				else:
					self.message(glob.language.string(25),glob.language.string(43))

		self.highscore_saved = 1

	def end_game(self):
		self.choices = [glob.language.string(44),glob.language.string(45)]
		if self.custom_level == 0 and self.score.get_current_score() > 0 and self.highscore_saved == 0:
			self.choices.append(glob.language.string(46))
		selection1 = Select(titre=glob.language.string(47),leschoix=self.choices)
		selection1.show()
		selection1.show_panel()
		selection1.doModal()
		self.selected=selection1.retour
		del selection1

		if self.selected == 0:
			self.restart_game()
		if self.selected == 1:
			self.close()
		if self.selected == 2:
			self.save_to_highscore()
			self.end_game()
		if self.selected == "":
			self.close()

	def kill_snake(self):
		for item in glob.snake_pos:
			glob.snakehead[item].setVisible(1)
			glob.snakepart[item].setVisible(0)
			time.sleep(0.05)

	def check_account(self):
		if glob.settings["name"] != "-" and glob.settings["pass"] != "-":
			self.theUID = ONLINEHIGHSCORE.get_user_id(str(glob.settings["name"]),str(glob.settings["pass"]))
			if self.theUID.split("\n")[0].strip() == "<HTML>":
				self.theUID="0"
		else:
			if self.question(glob.language.string(48),glob.language.string(49)+"\n"+glob.language.string(50)+"\nc"+glob.language.string(51)):
				pClass = MyProfile()
				pClass.show()
				pClass.show_panel()
				pClass.doModal()
				del pClass
				self.theUID = ONLINEHIGHSCORE.get_user_id(str(glob.settings["name"]),str(glob.settings["pass"]))
			else:
				self.theUID = "0"


	def loop(self):
		while self.running == 1:
			if self.paused == 0:
				self.move_snake()
				time.sleep(glob.speed)

	def food(self):
		while self.running == 1:
			if self.food_set == 0:
				random.seed(time.clock())
				foodx = random.randint(1,int(glob.leveldata.get("width"))-1)
				foody = random.randint(1,int(glob.leveldata.get("height"))-1)
				if not str(foodx)+","+str(foody) in glob.walls and not str(foodx)+","+str(foody) in glob.snake_pos:
					self.food_set = 1
					glob.food[0] = str(foodx)+","+str(foody)
					glob.snakefood[glob.food[0]].setVisible(1)

	def getLastScore(self):
		self.hsrs = ONLINEHIGHSCORE.get_highscore(str(glob.OHSGameID),str(self.LID)).strip()
		self.lines = self.hsrs.split("\n")
		if len(self.lines) < 10:
			return 1
		else:
			self.lastScore = self.lines[-1].split("|")
			return self.lastScore[1].strip()



class Leveleditor(xbmcgui.Window):
########################################################################
######################## Editor Class ##################################
########################################################################
	def __init__(self):
		self.setCoordinateResolution(6)
		xbmcgui.Window.__init__(self)

		self.mainbg = xbmcgui.ControlImage(0,
											0,
											720,
											576,
											MEDIA_DIR + "background.png"
											)
		self.addControl(self.mainbg)

		self.author = glob.settings["name"]
		self.levelname = glob.language.string(52)

		self.doEditor = 0
		self.doSettings = 0
		self.newlevel = 1
		self.have_to_save = 1
		self.changedSettings = 0

		self.themes = []
		for item in os.listdir(THEME_DIR):
			if os.path.isdir(THEME_DIR+item):
				self.themes.append(item)
		self.theme = self.themes[0]

		self.minspeed = 1
		self.maxspeed = 10
		self.speed = 5

		self.minsnakelength = 1
		self.maxsnakelength = 20
		self.snakelength = 4

		self.maxfieldwidth = 50
		self.maxfieldheight = 35
		self.minfieldwidth = 10
		self.minfieldheight = 10
		self.fieldwidth = 30
		self.fieldheight = 20
		self.fieldsize = 12

	def start_inputs(self):
		self.inputbg = xbmcgui.ControlImage(100,
											100,
											520,
											376,
											MEDIA_DIR + "box.png"
											)
		self.addControl(self.inputbg)

		self.nameButton=xbmcgui.ControlButton(200,
												120,
												320,
												30,
												glob.language.string(53)+": "+str(self.levelname),
												MEDIA_DIR + "button_focus.png",
												MEDIA_DIR + "button.png"
												)
		self.addControl(self.nameButton)

		self.authorButton=xbmcgui.ControlButton(200,
												160,
												320,
												30,
												glob.language.string(54)+": "+str(self.author),
												MEDIA_DIR + "button_focus.png",
												MEDIA_DIR + "button.png"
												)
		self.addControl(self.authorButton)
		
		self.widthButton=xbmcgui.ControlButton(200,
												200,
												320,
												30,
												glob.language.string(55)+": "+str(self.fieldwidth),
												MEDIA_DIR + "button_focus.png",
												MEDIA_DIR + "button.png"
												)
		self.addControl(self.widthButton)

		self.heightButton=xbmcgui.ControlButton(200,
												240,
												320,
												30,
												glob.language.string(56)+": "+str(self.fieldheight),
												MEDIA_DIR + "button_focus.png",
												MEDIA_DIR + "button.png"
												)
		self.addControl(self.heightButton)

		self.styleButton=xbmcgui.ControlButton(200,
												280,
												320,
												30,
												glob.language.string(57)+": "+self.theme,
												MEDIA_DIR + "button_focus.png",
												MEDIA_DIR + "button.png"
												)
		self.addControl(self.styleButton)

		self.speedButton=xbmcgui.ControlButton(200,
												320,
												320,
												30,
												glob.language.string(58)+": "+str(self.speed),
												MEDIA_DIR + "button_focus.png",
												MEDIA_DIR + "button.png"
												)
		self.addControl(self.speedButton)

		self.snakelengthButton=xbmcgui.ControlButton(200,
													360,
													320,
													30,
													glob.language.string(59)+": "+str(self.snakelength),
													MEDIA_DIR + "button_focus.png",
													MEDIA_DIR + "button.png"
													)
		self.addControl(self.snakelengthButton)

		self.okButton=xbmcgui.ControlButton(200,
											400,
											150,
											30,
											glob.language.string(60),
											MEDIA_DIR + "button_focus.png",
											MEDIA_DIR + "button.png"
											)
		self.addControl(self.okButton)

		self.cancelButton=xbmcgui.ControlButton(370,
												400,
												150,
												30,
												glob.language.string(61),
												MEDIA_DIR + "button_focus.png",
												MEDIA_DIR + "button.png"
												)
		self.addControl(self.cancelButton)

		self.nameButton.controlUp(self.okButton)
		self.nameButton.controlDown(self.authorButton)

		self.authorButton.controlUp(self.nameButton)
		self.authorButton.controlDown(self.widthButton)
		
		self.widthButton.controlUp(self.authorButton)
		self.widthButton.controlDown(self.heightButton)
		
		self.heightButton.controlUp(self.widthButton)
		self.heightButton.controlDown(self.styleButton)

		self.styleButton.controlUp(self.heightButton)
		self.styleButton.controlDown(self.speedButton)

		self.speedButton.controlUp(self.styleButton)
		self.speedButton.controlDown(self.snakelengthButton)

		self.snakelengthButton.controlUp(self.speedButton)
		self.snakelengthButton.controlDown(self.okButton)

		self.okButton.controlUp(self.snakelengthButton)
		self.okButton.controlDown(self.nameButton)
		self.okButton.controlLeft(self.cancelButton)
		self.okButton.controlRight(self.cancelButton)

		self.cancelButton.controlUp(self.snakelengthButton)
		self.cancelButton.controlDown(self.nameButton)
		self.cancelButton.controlLeft(self.okButton)
		self.cancelButton.controlRight(self.okButton)

		self.setFocus(self.nameButton)

		self.doSettings = 1

		self.frame = xbmcgui.ControlImage((self.fieldwidth*self.fieldsize)/2,
											(self.fieldheight*self.fieldsize)/2,
											(720/2)-((self.fieldwidth*self.fieldsize)/2),
											(576/2)-((self.fieldheight*self.fieldsize)/2),
											MEDIA_DIR + "frame.png"
											)
		self.addControl(self.frame)
		self.frame.setVisible(0)

		self.update_start_inputs()

	def update_start_inputs(self):
		self.widthButton.setLabel(glob.language.string(55)+": "+str(self.fieldwidth))
		self.heightButton.setLabel(glob.language.string(56)+": "+str(self.fieldheight))
		
		self.frame.setWidth(self.fieldwidth*self.fieldsize)
		self.frame.setHeight(self.fieldheight*self.fieldsize)
		self.frame.setPosition((720/2)-((self.fieldwidth*self.fieldsize)/2),(576/2)-((self.fieldheight*self.fieldsize)/2))

		self.styleButton.setLabel(glob.language.string(57)+": "+self.theme)
		self.speedButton.setLabel(glob.language.string(58)+": "+str(self.speed))
		self.snakelengthButton.setLabel(glob.language.string(59)+": "+str(self.snakelength))
		self.nameButton.setLabel(glob.language.string(53)+": "+str(self.levelname))
		self.authorButton.setLabel(glob.language.string(54)+": "+str(self.author))

	def close_start_inputs(self):
		self.nameButton.setVisible(0)
		self.authorButton.setVisible(0)
		self.widthButton.setVisible(0)
		self.heightButton.setVisible(0)
		self.styleButton.setVisible(0)
		self.speedButton.setVisible(0)
		self.snakelengthButton.setVisible(0)
		self.okButton.setVisible(0)
		self.cancelButton.setVisible(0)
		self.frame.setVisible(0)
		self.inputbg.setVisible(0)
		self.doSettings = 0



	def load_field(self):
		self.get_startpos()
		self.doEditor = 1
		self.build_menu()
		self.create_ground()


	def onAction(self,action):
		if action == ACTION_PREVIOUS_MENU:
			play_sound("menu_back")
			if self.doSettings == 1:
				if self.doEditor == 1:
					self.close_start_inputs()
					self.setFocus(self.buttons["0,0"])
				else:
					self.close()
			else:
				if self.doEditor == 1:
					if self.have_to_save == 1:
						if self.question(glob.language.string(62),glob.language.string(63)+"\n"+glob.language.string(64)):
							self.save_level()
				self.close()
				
	
		if self.doSettings == 1:
			theObj =self.getFocus()
			if action == ACTION_DPAD_LEFT:
				if theObj == self.widthButton:
					if self.fieldwidth > self.minfieldwidth:
						self.fieldwidth -= 1
					self.changedSettings = 1
				if theObj == self.heightButton:
					if self.fieldheight > self.minfieldheight:
						self.fieldheight -= 1
					self.changedSettings = 1
				if theObj == self.speedButton:
					if self.speed > self.minspeed:
						self.speed -= 1
						self.have_to_save = 1
				if theObj == self.snakelengthButton:
					if self.snakelength > self.minsnakelength:
						self.snakelength -= 1
						self.have_to_save = 1

				if self.changedSettings == 1:
					self.have_to_save = 1

			if action == ACTION_DPAD_RIGHT:
				if theObj == self.widthButton:
					if self.fieldwidth < self.maxfieldwidth:
						self.fieldwidth += 1
					self.changedSettings = 1
				if theObj == self.heightButton:
					if self.fieldheight < self.maxfieldheight:
						self.fieldheight += 1
					self.changedSettings = 1
				if theObj == self.speedButton:
					if self.speed < self.maxspeed:
						self.speed += 1
						self.have_to_save = 1
				if theObj == self.snakelengthButton:
					if self.snakelength < self.maxsnakelength:
						self.snakelength += 1
						self.have_to_save = 1

				if self.changedSettings == 1:
					self.have_to_save = 1

			if action == ACTION_DPAD_UP or action == ACTION_DPAD_DOWN:
				if theObj == self.widthButton or theObj == self.heightButton:
					self.frame.setVisible(1)
				else:
					self.frame.setVisible(0)

			self.update_start_inputs()

		if self.doSettings == 0:
			play_sound("menu_move")
			if action == ACTION_YBUTTON:
				selection1 = Select(titre=glob.language.string(65),leschoix=[glob.language.string(66),glob.language.string(67),glob.language.string(68)])
				selection1.show()
				selection1.show_panel()
				selection1.doModal()
				self.selected=selection1.retour
				del selection1

				if self.selected != "":
					if self.selected == 0:
						self.save_level()
						self.have_to_save = 0
					if self.selected == 1:
						self.doSettings = 1
						self.start_inputs()
					if self.selected == 2:
						if self.doEditor == 1:
							if self.have_to_save == 1:
								if self.question(glob.language.string(62),glob.language.string(63)+"\n"+glob.language.string(64)):
									self.save_level()
						self.close()



	def onControl(self,control):
		play_sound("menu_select")
		if self.doSettings == 1:
			if control == self.styleButton:
				selection1 = Select(titre=glob.language.string(69),leschoix=self.themes)
				selection1.show()
				selection1.show_panel()
				selection1.doModal()
				self.selected=selection1.retour
				del selection1

				if self.selected != "":
					self.theme = self.themes[self.selected]
					self.changedSettings = 1
					self.have_to_save = 1
					self.update_start_inputs()
			
			if control == self.widthButton or control == self.heightButton or control == self.speedButton or control == self.snakelengthButton:
				self.message(glob.language.string(70),glob.language.string(71))

			if control == self.cancelButton:
				play_sound("menu_back")
				if self.doEditor == 1:
					self.close_start_inputs()
					self.setFocus(self.buttons["0,0"])
				else:
					self.close()

			if control == self.okButton:
				self.close_start_inputs()
				if self.doEditor == 0:
					self.load_field()
				elif self.doEditor == 1:
					if self.changedSettings == 1:
						self.remove_all()
						self.reload_ground()
						self.changedSettings = 0
						self.have_to_save = 1
					else:
						self.setFocus(self.buttons["0,0"])

			if control == self.nameButton:
				keyboard = xbmc.Keyboard(self.levelname,glob.language.string(72))
				keyboard.doModal()
				if(keyboard.isConfirmed()):
					self.keyconfirmed = 1
					self.levelname_old = self.levelname
					if self.doEditor == 0:
						if keyboard.getText() in glob.levels or keyboard.getText() in glob.clevels:
							self.message(glob.language.string(39),glob.language.string(73)+"\n"+glob.language.string(74))
						else:
							self.levelname = keyboard.getText()
					else:
						if keyboard.getText() in glob.levels:
							self.message(glob.language.string(39),glob.language.string(73)+"\n"+glob.language.string(74))
						else:
							self.levelname = keyboard.getText()
							if os.path.exists(CLEVEL_DIR + self.levelname_old + ".xml"):
								os.rename(CLEVEL_DIR + self.levelname_old + ".xml",CLEVEL_DIR + self.levelname + ".xml")
								glob.clevels.remove(self.levelname_old)
								glob.clevels.append(self.levelname)


			if control == self.authorButton:
				keyboard = xbmc.Keyboard(self.author,glob.language.string(33))
				keyboard.doModal()
				if(keyboard.isConfirmed()):
					self.keyconfirmed = 1
					self.author = keyboard.getText()
					self.have_to_save = 1

		if self.doEditor == 1:
			for coords in self.buttons:
				if control == self.buttons[coords]:
					if self.walls[coords][1] == 0:
						self.walls[coords][1] = 1
						self.walls[coords][0].setVisible(1)
					else:
						self.walls[coords][1] = 0
						self.walls[coords][0].setVisible(0)
					self.have_to_save = 1

			if control == self.menuButton:
				selection1 = Select(titre=glob.language.string(65),leschoix=[glob.language.string(66),glob.language.string(67),glob.language.string(68)])
				selection1.show()
				selection1.show_panel()
				selection1.doModal()
				self.selected=selection1.retour
				del selection1

				if self.selected != "":
					if self.selected == 0:
						self.save_level()
						self.have_to_save = 0
					if self.selected == 1:
						self.doSettings = 1
						self.start_inputs()
					if self.selected == 2:
						if self.doEditor == 1:
							if self.have_to_save == 1:
								if self.question(glob.language.string(62),glob.language.string(63)+"\n"+glob.language.string(64)):
									self.save_level()
						self.close()




	def message(self, title, message):
		themessage = Message(title=title,message=message)
		themessage.show()
		themessage.show_panel()
		themessage.doModal()
		del themessage

	def question(self, title, question):
		themessage = YesNo(title=title,question=question)
		themessage.show()
		themessage.show_panel()
		themessage.doModal()
		self.temp = themessage.give
		del themessage
		return self.temp

	def get_startpos(self):
		self.startposX = (720 - (self.fieldsize*int(self.fieldwidth)))/2
		self.startposY = (576 - (self.fieldsize*int(self.fieldheight)))/2


	def build_menu(self):
		self.menuButton=xbmcgui.ControlButton(41,
												25,
												150,
												30,
												glob.language.string(75),
												MEDIA_DIR + "box_black.png",
												MEDIA_DIR + "button.png"
												)
		self.addControl(self.menuButton)
		

											


	def load_walls(self,loadlevel):
		glob.leveldata = level.Level()
		glob.leveldata.load(CLEVEL_DIR + loadlevel + ".xml")
		self.theme = glob.leveldata.get("style")
		self.speed = int(glob.leveldata.get("speed"))
		self.snakelength = int(glob.leveldata.get("snake_startlength"))
		self.fieldwidth = int(glob.leveldata.get("width"))
		self.fieldheight = int(glob.leveldata.get("height"))
		self.author = glob.leveldata.get("author")
		self.levelname = loadlevel
		self.newlevel = 0


		
		self.aefile = CLEVEL_DIR + loadlevel + ".xml"

		f=open(self.aefile,"r")
		self.old_walls = []
		self.xmldata = f.read()
		f.close()
		self.walldata = self.xmldata.split("<walls>")[1].split("</walls>")[0].split("\n")
		self.max = len(self.walldata)
		self.current = 0

		progressbar = Progress(text=glob.language.string(17))
		progressbar.show()
		progressbar.update_progress(1,glob.language.string(76))



		for wall in self.walldata:
			progressbar.update_progress(self.current*100/self.max,glob.language.string(76))
			if wall.strip() != "":
				wallx = int(wall.split("<x>")[1].split("</x>")[0]) -1
				wally = int(wall.split("<y>")[1].split("</y>")[0]) -1

				self.old_walls.append(str(wallx)+","+str(wally))
		progressbar.close()
		del progressbar


		self.get_startpos()
		self.doEditor = 1
		self.have_to_save = 0
		self.build_menu()
		self.reload_ground()

	def create_ground(self):
		self.ground = {}
		self.walls = {}
		self.buttons = {}

		self.field_background = xbmcgui.ControlImage(self.startposX-20,
													self.startposY-20,
													int(self.fieldwidth)*self.fieldsize+40,
													int(self.fieldheight)*self.fieldsize+40,
													MEDIA_DIR + "box_black.png"
													)
		self.addControl(self.field_background)



		progressbar = Progress(text=glob.language.string(17))
		progressbar.show()
		progressbar.update_progress(1,glob.language.string(27))
		
		for numberY in range(int(self.fieldheight)):
			progressbar.update_progress(numberY*100/int(self.fieldheight),glob.language.string(27))
			for numberX in range(int(self.fieldwidth)):
				temp = str(numberX)+","+str(numberY)
				self.ground[temp] = xbmcgui.ControlImage(self.startposX+(self.fieldsize*numberX),
													self.startposY+(self.fieldsize*numberY),
													self.fieldsize,
													self.fieldsize,
													THEME_DIR + self.theme + "\\ground.png"
													)
				self.addControl(self.ground[temp])

				self.walls[temp] = []
				self.wallpart = xbmcgui.ControlImage(self.startposX+(self.fieldsize*numberX),
													self.startposY+(self.fieldsize*numberY),
													self.fieldsize,
													self.fieldsize,
													THEME_DIR + self.theme + "\\wall.png"
													)
				self.addControl(self.wallpart)

				self.walls[temp].append(self.wallpart)
				self.walls[temp][0].setVisible(0)
				self.walls[temp].append(0)

				self.buttons[temp] = xbmcgui.ControlButton(self.startposX+(self.fieldsize*numberX),
															self.startposY+(self.fieldsize*numberY),
															self.fieldsize,
															self.fieldsize,
															"",
															MEDIA_DIR + "editor_button.png",
															""
															)
				self.addControl(self.buttons[temp])


		progressbar.close()
		del progressbar

		progressbar = Progress(text=glob.language.string(17))
		progressbar.show()
		progressbar.update_progress(1,glob.language.string(77))
		
		for numberY in range(int(self.fieldheight)):
			progressbar.update_progress(numberY*100/int(self.fieldheight),glob.language.string(77))
			for numberX in range(int(self.fieldwidth)):
				temp = str(numberX)+","+str(numberY)
				temp_left = str(numberX-1)+","+str(numberY)
				temp_right = str(numberX+1)+","+str(numberY)
				temp_top = str(numberX)+","+str(numberY-1)
				temp_bottom = str(numberX)+","+str(numberY+1)
				temp_max_left = "0,"+str(numberY)
				temp_max_right = str(self.fieldwidth-1)+","+str(numberY)
				temp_max_top = str(numberX)+",0"
				temp_max_bottom = str(numberX)+","+str(self.fieldheight-1)

				try:
					self.buttons[temp].controlLeft(self.buttons[temp_left])
				except:
					self.buttons[temp].controlLeft(self.buttons[temp_max_right])

				try:
					self.buttons[temp].controlRight(self.buttons[temp_right])
				except:
					self.buttons[temp].controlRight(self.buttons[temp_max_left])

				try:
					self.buttons[temp].controlUp(self.buttons[temp_top])
				except:
					self.buttons[temp].controlUp(self.buttons[temp_max_bottom])

				try:
					self.buttons[temp].controlDown(self.buttons[temp_bottom])
				except:
					self.buttons[temp].controlDown(self.buttons[temp_max_top])

		self.menuButton.controlDown(self.buttons["0,0"])
		self.menuButton.controlRight(self.buttons["0,0"])
		self.menuButton.controlUp(self.buttons["0,0"])
		self.menuButton.controlLeft(self.buttons["0,0"])
		
		self.setFocus(self.buttons["0,0"])
		progressbar.close()
		del progressbar



	def reload_ground(self):
		self.get_startpos()
		self.ground = {}
		self.walls = {}
		self.buttons = {}

		self.field_background = xbmcgui.ControlImage(self.startposX-20,
												self.startposY-20,
												int(self.fieldwidth)*self.fieldsize+40,
												int(self.fieldheight)*self.fieldsize+40,
												MEDIA_DIR + "box.png"
												)
		self.addControl(self.field_background)




		progressbar = Progress(text=glob.language.string(17))
		progressbar.show()
		progressbar.update_progress(1,glob.language.string(27))
		
		for numberY in range(int(self.fieldheight)):
			progressbar.update_progress(numberY*100/int(self.fieldheight),glob.language.string(27))
			for numberX in range(int(self.fieldwidth)):
				temp = str(numberX)+","+str(numberY)
				self.ground[temp] = xbmcgui.ControlImage(self.startposX+(self.fieldsize*numberX),
													self.startposY+(self.fieldsize*numberY),
													self.fieldsize,
													self.fieldsize,
													THEME_DIR + self.theme + "\\ground.png"
													)
				self.addControl(self.ground[temp])

				self.walls[temp] = []
				self.wallpart = xbmcgui.ControlImage(self.startposX+(self.fieldsize*numberX),
													self.startposY+(self.fieldsize*numberY),
													self.fieldsize,
													self.fieldsize,
													THEME_DIR + self.theme + "\\wall.png"
													)
				self.addControl(self.wallpart)

				self.walls[temp].append(self.wallpart)
				if temp in self.old_walls:
					self.walls[temp][0].setVisible(1)
					self.walls[temp].append(1)
				else:
					self.walls[temp][0].setVisible(0)
					self.walls[temp].append(0)

				self.buttons[temp] = xbmcgui.ControlButton(self.startposX+(self.fieldsize*numberX),
															self.startposY+(self.fieldsize*numberY),
															self.fieldsize,
															self.fieldsize,
															"",
															MEDIA_DIR + "editor_button.png",
															""
															)
				self.addControl(self.buttons[temp])


		progressbar.close()
		del progressbar

		progressbar = Progress(text=glob.language.string(17))
		progressbar.show()
		progressbar.update_progress(1,glob.language.string(77))
		
		for numberY in range(int(self.fieldheight)):
			progressbar.update_progress(numberY*100/int(self.fieldheight),glob.language.string(77))
			for numberX in range(int(self.fieldwidth)):
				temp = str(numberX)+","+str(numberY)
				temp_left = str(numberX-1)+","+str(numberY)
				temp_right = str(numberX+1)+","+str(numberY)
				temp_top = str(numberX)+","+str(numberY-1)
				temp_bottom = str(numberX)+","+str(numberY+1)
				temp_max_left = "0,"+str(numberY)
				temp_max_right = str(self.fieldwidth-1)+","+str(numberY)
				temp_max_top = str(numberX)+",0"
				temp_max_bottom = str(numberX)+","+str(self.fieldheight-1)

				try:
					self.buttons[temp].controlLeft(self.buttons[temp_left])
				except:
					self.buttons[temp].controlLeft(self.buttons[temp_max_right])

				try:
					self.buttons[temp].controlRight(self.buttons[temp_right])
				except:
					self.buttons[temp].controlRight(self.buttons[temp_max_left])

				try:
					self.buttons[temp].controlUp(self.buttons[temp_top])
				except:
					self.buttons[temp].controlUp(self.buttons[temp_max_bottom])

				try:
					self.buttons[temp].controlDown(self.buttons[temp_bottom])
				except:
					self.buttons[temp].controlDown(self.buttons[temp_max_top])

		self.menuButton.controlDown(self.buttons["0,0"])
		self.menuButton.controlRight(self.buttons["0,0"])
		self.menuButton.controlUp(self.buttons["0,0"])
		self.menuButton.controlLeft(self.buttons["0,0"])
		
		self.setFocus(self.buttons["0,0"])
		progressbar.close()
		del progressbar













	def remove_all(self):
		self.old_walls = []
		for coords in self.ground:
			if self.walls[coords][1] == 1:
				self.old_walls.append(coords)
			self.removeControl(self.ground[coords])
			self.removeControl(self.walls[coords][0])
			self.removeControl(self.buttons[coords])
		self.removeControl(self.field_background)

	def save_level(self):
		self.keyconfirmed = 0
		self.saving_cancelled = 0
		
		if self.saving_cancelled == 0:
			if self.author == "":
				if glob.settings["name"] == "-":
					self.oldname = glob.language.string(33)
				else:
					self.oldname = glob.settings["name"]
				keyboard = xbmc.Keyboard(self.oldname,glob.language.string(33))
				keyboard.doModal()
				if(keyboard.isConfirmed()):
					self.author = keyboard.getText()
					glob.settings["name"] = self.author

			comment = "<level>\n"
			comment += "  <author>" + str(self.author) + "</author>\n"
			comment += "  <speed>" + str(self.speed) + "</speed>\n"
			comment += "  <style>" + str(self.theme) + "</style>\n"
			comment += "  <width>" + str(self.fieldwidth) + "</width>\n"
			comment += "  <height>" + str(self.fieldheight) + "</height>\n"
			comment += "  <snake_startlength>" + str(self.snakelength) + "</snake_startlength>\n"
			comment += "  <walls>\n"

			for coords in self.walls:
				if self.walls[coords][1] == 1:
					temp = coords.split(",")
					comment += "	<wall><x>"+str(int(temp[0])+1)+"</x><y>"+str(int(temp[1])+1)+"</y></wall>\n"

			comment += "  </walls>\n"
			comment += "</level>"


			aefile = CLEVEL_DIR + self.levelname + ".xml"
			f = open(aefile,"w")
			f.write(comment)
			f.close()

			self.message(glob.language.string(78),glob.language.string(79))
			if self.newlevel == 1:
				glob.clevels.append(self.levelname)



class LEMenu(xbmcgui.Window):
########################################################################
######################## LE-Menu Class #################################
########################################################################
	def __init__(self):
		self.setCoordinateResolution(6)
		xbmcgui.Window.__init__(self)

		self.build_menu()



	def build_menu(self):

		self.mainbg = xbmcgui.ControlImage(0,
											0,
											720,
											576,
											MEDIA_DIR + "background.png"
											)
		self.addControl(self.mainbg)

		self.background=xbmcgui.ControlImage(80,
											 80,
											 560,
											 416,
											 MEDIA_DIR + "box.png"
											 )
		self.addControl(self.background)

		self.titre=xbmcgui.ControlLabel(100,
										100,
										400,
										30,
										glob.language.string(2),
										"font13",
										"#FFFFFFFF"
										)
		self.addControl(self.titre)

		self.lst_choix=xbmcgui.ControlList(100,
											150,
											220,
											300,
											buttonFocusTexture=MEDIA_DIR + "button_focus.png",
											buttonTexture=MEDIA_DIR + "button.png",
											textColor="#FFFFFFFF",
											font="font12"
											)
		self.addControl(self.lst_choix)

		self.choix=[glob.language.string(80),glob.language.string(81),glob.language.string(82),glob.language.string(83),glob.language.string(84)]
		for ch in self.choix:
			self.lst_choix.addItem(ch)
		
		self.setFocus(self.lst_choix)






	def onAction(self, action):
		play_sound("menu_move")
		if action == ACTION_PREVIOUS_MENU:
			play_sound("menu_back")
			self.close()

	def onControl(self,control):
		play_sound("menu_select")
		if control==self.lst_choix:
			self.selected=self.lst_choix.getSelectedPosition()

			if self.selected != "":
				if self.selected == 0:
					self.startclass = Leveleditor()
					self.startclass.show()
					self.startclass.start_inputs()
					self.startclass.doModal()
					del self.startclass
					
				if self.selected == 1:
					selection2 = Select(titre=glob.language.string(9),leschoix=glob.clevels)
					selection2.show()
					selection2.show_panel()
					selection2.doModal()
					self.selected2=selection2.retour
					del selection2

					if self.selected2 != "":
						self.startclass = Leveleditor()
						self.startclass.show()
						self.startclass.load_walls(glob.clevels[self.selected2])
						self.startclass.doModal()
						del self.startclass

				if self.selected == 2:
					selection2 = Select(titre=glob.language.string(9),leschoix=glob.clevels)
					selection2.show()
					selection2.show_panel()
					selection2.doModal()
					self.selected2=selection2.retour
					del selection2

					if self.selected2 != "":
						keyboard = xbmc.Keyboard(glob.clevels[self.selected2],glob.language.string(85))
						keyboard.doModal()
						if(keyboard.isConfirmed()):
							if keyboard.getText() in glob.levels:
								self.message(glob.language.string(39),glob.language.string(73)+"\n"+glob.language.string(74))
							else:
								self.new_level_name = keyboard.getText()
								if self.new_level_name != "":
									os.rename(CLEVEL_DIR+glob.clevels[self.selected2] + ".xml",CLEVEL_DIR+self.new_level_name + ".xml")
									glob.clevels[self.selected2] = self.new_level_name
									self.message(glob.language.string(8),glob.language.string(86))

				if self.selected == 3:
					selection2 = Select(titre=glob.language.string(9),leschoix=glob.clevels)
					selection2.show()
					selection2.show_panel()
					selection2.doModal()
					self.selected2=selection2.retour
					del selection2

					if self.selected2 != "":
						if self.question(glob.language.string(87),glob.language.string(88)+": "+glob.clevels[self.selected2]+"?"):
							os.unlink(CLEVEL_DIR+glob.clevels[self.selected2] + ".xml")
							glob.clevels.remove(glob.clevels[self.selected2])
							self.message(glob.language.string(8),glob.language.string(126))

				if self.selected == 4:
					play_sound("menu_back")
					self.close()


	def message(self, title, message):
		themessage = Message(title=title,message=message)
		themessage.show()
		themessage.show_panel()
		themessage.doModal()
		del themessage


	def question(self, title, question):
		themessage = YesNo(title=title,question=question)
		themessage.show()
		themessage.show_panel()
		themessage.doModal()
		self.temp = themessage.give
		del themessage
		return self.temp



class Online(xbmcgui.Window):
########################################################################
######################### Online Class #################################
########################################################################
	def __init__(self):
		self.setCoordinateResolution(6)

		self.mainbg = xbmcgui.ControlImage(0,
											0,
											720,
											576,
											MEDIA_DIR + "background.png"
											)
		self.addControl(self.mainbg)

		self.build_menu()



	def build_menu(self):
		self.background=xbmcgui.ControlImage(80,
											80,
											560,
											416,
											MEDIA_DIR + "box.png"
											)
		self.addControl(self.background)

		self.titre=xbmcgui.ControlLabel(100,
										100,
										400,
										30,
										glob.language.string(3),
										"font13",
										"#FFFFFFFF"
										)
		self.addControl(self.titre)

		self.lst_choix=xbmcgui.ControlList(100,
											150,
											220,
											300,
											buttonFocusTexture=MEDIA_DIR + "button_focus.png",
											buttonTexture=MEDIA_DIR + "button.png",
											textColor="#FFFFFFFF",
											font="font12"
											)
		self.addControl(self.lst_choix)

		self.choix=[glob.language.string(89),glob.language.string(90),glob.language.string(91)]
		for ch in self.choix:
			self.lst_choix.addItem(ch)

		self.setFocus(self.lst_choix)






	def onAction(self, action):
		play_sound("menu_move")
		if action == ACTION_PREVIOUS_MENU:
			play_sound("menu_back")
			self.close()

	def onControl(self,control):
		play_sound("menu_select")
		if control==self.lst_choix:
			self.selected=self.lst_choix.getSelectedPosition()

			if self.selected != "":
				if self.selected == 0:
					self.get_level_online()
			if self.selected == 1:
				pClass = MyProfile()
				pClass.show()
				pClass.show_panel()
				pClass.doModal()
				del pClass
			if self.selected == 2:
				ohClass = OHighscore()
				ohClass.show()
				ohClass.show_panel()
				ohClass.doModal()
				del ohClass




	def message(self, title, message):
		themessage = Message(title=title,message=message)
		themessage.show()
		themessage.show_panel()
		themessage.doModal()
		del themessage


	def question(self, title, question):
		themessage = YesNo(title=title,question=question)
		themessage.show()
		themessage.show_panel()
		themessage.doModal()
		self.temp = themessage.give
		del themessage
		return self.temp



	def get_level_online(self):
		self.progressbar = Progress(text=glob.language.string(17))
		self.progressbar.show()
		self.progressbar.update_progress(1,glob.language.string(93))
		testurl = urllib.urlopen(LEVELURL + "level_download.php")
		temp = testurl.read()
		testurl.close()
		self.progressbar.close()
		del self.progressbar

		self.downloadlevels = temp.split("\n")

		self.dlevels = {}
		self.dlevels_list = []
		self.listcount = 0
		for self.item in self.downloadlevels:
			if self.item != "":
				self.tmp = self.item.split("|")
				if not self.tmp[0].replace("_"," ") in glob.levels:
					self.dlevels[self.tmp[0]] = self.tmp[1]
					self.dlevels_list.append(self.tmp[0])
					self.listcount = self.listcount + 1


		if self.listcount > 0:
			selection2 = Select(titre=glob.language.string(9),leschoix=self.dlevels_list)
			selection2.show()
			selection2.show_panel()
			selection2.doModal()
			self.selected2=selection2.retour
			del selection2

			if self.selected2 != "":
				self.progressbar = Progress(text=glob.language.string(17))
				self.progressbar.show()
				self.progressbar.update_progress(1,glob.language.string(94))
			
				self.new_lname = self.dlevels_list[self.selected2].replace("_"," ")
				if self.question(glob.language.string(62),glob.language.string(95)+": "+self.new_lname+"?"):
					self.save(self.dlevels[self.dlevels_list[self.selected2]],LEVEL_DIR+self.new_lname+".xml")
					glob.levels.append(self.dlevels_list[self.selected2].replace("_"," "))
					self.message(glob.language.string(78),glob.language.string(96))

				self.progressbar.close()
				del self.progressbar

		else:
			self.message(glob.language.string(97),glob.language.string(98))
		


	def do_update(self):
		self.updateurl = "http://snake.dirtyduckdesigns.de/script_update/"
		self.updatefile = "update.xml"
		self.versionfile = "version.txt"
		
		print "-----------------------------"
		print "searching for update"
		self.progressbar = Progress(text=glob.language.string(99))
		self.progressbar.show()
		self.progressbar.update_progress(1,glob.language.string(99))
		vurl = urllib.urlopen(self.updateurl+self.versionfile)
		self.uversion = vurl.read()
		vurl.close()
		self.progressbar.close()
		del self.progressbar
		print "done searching for update"
		print "-----------------------------"
		
		if str(self.uversion).strip() != str(glob.info["version"]):
			if self.question(glob.language.string(13),glob.language.string(14)+"\nversion "+str(self.uversion).strip()+"\n"+glob.language.string(15)):
				self.progressbar = Progress(text=glob.language.string(16))
				self.progressbar.show()
				self.progressbar.update_progress(1,glob.language.string(16))
				tempurl = urllib.urlopen(self.updateurl+self.updatefile)
				self.tempstrings = tempurl.readlines()
				tempurl.close()
				self.progressbar.close()
				del self.progressbar
				
				self.exp="""<file><source>(.*?)</source><destination>(.*?)</destination></file>"""
				self.exp2="""<folder><destination>(.*?)</destination></folder>"""
		
				self.id = 0
				for self.line in self.tempstrings:
					try:
						self.res=re.findall(self.exp,self.line)
						self.results = self.res[0]
					except:
						self.results = 0
		
					if self.results != 0:
						self.progressbar = Progress(text=glob.language.string(17))
						self.progressbar.show()
						self.progressbar.update_progress(1,glob.language.string(18))
						self.save(self.updateurl+str(self.results[0]),HOME_DIR+str(self.results[1]))
						self.progressbar.close()
						del self.progressbar

					try:
						self.res2=re.findall(self.exp2,self.line)
						self.results2 = self.res2[0]
					except:
						self.results2 = 0
		
					if self.results2 != 0:
						self.progressbar = Progress(text=glob.language.string(17))
						self.progressbar.show()
						self.progressbar.update_progress(1,glob.language.string(18))
						os.mkdir(HOME_DIR+self.results2,0777)
						self.progressbar.close()
						del self.progressbar
				self.message(glob.language.string(19),glob.language.string(19)+"\n"+glob.language.string(20))

		else:
			self.message(glob.language.string(100),glob.language.string(101)+"\n"+glob.language.string(102))


			









	def hook(self, count_blocks, block_size, total_size):
		current_size = block_size * count_blocks
		value = current_size * 100 / total_size
		self.progressbar.update_progress(value,glob.language.string(18))

	def save(self, url,destination):
		try:
			DL=urllib.urlretrieve( url , destination , self.hook)
		except:
			print "exception while downloading"



class Select(xbmcgui.WindowDialog):
########################################################################
######################## Select Class ##################################
########################################################################
	def __init__(self,titre="",leschoix=[]):
		self.setCoordinateResolution(6)
		xbmcgui.Window.__init__(self)

		self.choix=leschoix
		self.retour=""

		if glob.settings["animation"] == "1":
			if SELECT_ANI_FROM == "right":
				self.diff=(720-int(SELECT_POSITIONS_BG[0]))
				self.diff2 = 0

			if SELECT_ANI_FROM == "bottom":
				self.diff2=(576-int(SELECT_POSITIONS_BG[1]))
				self.diff = 0

			if SELECT_ANI_FROM == "left":
				self.diff=(0-(int(SELECT_POSITIONS_BG[2])))
				self.diff2 = 0

			if SELECT_ANI_FROM == "top":
				self.diff2=(0-(int(SELECT_POSITIONS_BG[3])))
				self.diff = 0
		else:
			self.diff = 0
			self.diff2 = 0
		
	

		self.background=xbmcgui.ControlImage(SELECT_POSITIONS_BG[0]+self.diff,
											 SELECT_POSITIONS_BG[1]+self.diff2,
											 SELECT_POSITIONS_BG[2],
											 SELECT_POSITIONS_BG[3],
											 MEDIA_DIR + "select_background.png"
											 )
		self.addControl(self.background)

		self.titre=xbmcgui.ControlLabel(SELECT_POSITIONS_TITLE[0]+self.diff,
										SELECT_POSITIONS_TITLE[1]+self.diff2,
										SELECT_POSITIONS_TITLE[2],
										SELECT_POSITIONS_TITLE[3],
										titre,
										"font13",
										"#FFFFFFFF"
										)
		self.addControl(self.titre)
		
		self.lst_choix=xbmcgui.ControlList(SELECT_POSITIONS_LIST[0]+self.diff,
											SELECT_POSITIONS_LIST[1]+self.diff2,
											SELECT_POSITIONS_LIST[2],
											SELECT_POSITIONS_LIST[3],
											buttonFocusTexture=MEDIA_DIR + "button_focus.png",
											buttonTexture=MEDIA_DIR + "button.png",
											textColor="#FFFFFFFF",
											font="font12"
											)
		self.addControl(self.lst_choix)

		for ch in self.choix:
			self.lst_choix.addItem(ch.replace("_"," "))
		
		self.setFocus(self.lst_choix)








		
	def show_panel(self):
		if glob.settings["animation"] == "1":
			for pos in  range(10,-1,-1):
				time.sleep(0.01)
				self.animation(pos)

	def hide_panel(self):
		if glob.settings["animation"] == "1":
			for pos in range(0,10,1):
				time.sleep(0.01)
				self.animation(pos)

	def animation(self, pct):
		if SELECT_ANI_FROM == "right" or SELECT_ANI_FROM == "left":
			elmt_step=float(self.diff)/float(10)
			
			delta = int(pct*elmt_step)
			self.background.setPosition(int(SELECT_POSITIONS_BG[0])+delta, int(SELECT_POSITIONS_BG[1]))
			self.titre.setPosition(int(SELECT_POSITIONS_TITLE[0])+delta, int(SELECT_POSITIONS_TITLE[1]))
			self.lst_choix.setPosition(int(SELECT_POSITIONS_LIST[0])+delta, int(SELECT_POSITIONS_LIST[1]))

		if SELECT_ANI_FROM == "bottom" or SELECT_ANI_FROM == "top":
			elmt_step=float(self.diff2)/float(int(glob.skin.get("menu1_animation_step")))
			
			delta = int(pct*elmt_step)
			self.background.setPosition(int(SELECT_POSITIONS_BG[0]), int(SELECT_POSITIONS_BG[1])+delta)
			self.titre.setPosition(int(SELECT_POSITIONS_TITLE[0]), int(SELECT_POSITIONS_TITLE[1])+delta)
			self.lst_choix.setPosition(int(SELECT_POSITIONS_LIST[0]), int(SELECT_POSITIONS_LIST[1])+delta)


	def onAction(self, action):
		play_sound("menu_move")
		if action == ACTION_PREVIOUS_MENU:
			self.retour=""
			self.hide_panel()
			play_sound("menu_back")
			self.close()

	def onControl(self,control):
		play_sound("menu_select")
		if control==self.lst_choix:
			self.retour=self.lst_choix.getSelectedPosition()
			self.hide_panel()
			self.close()



class Message(xbmcgui.WindowDialog):
########################################################################
######################## Message Class #################################
########################################################################
	def __init__(self,title="",message=""):
		self.setCoordinateResolution(6)
		xbmcgui.Window.__init__(self)

		if glob.settings["animation"] == "1":
			if MESSAGE_ANI_FROM == "right":
				self.diff=(720-int(MESSAGE_POSITIONS_BG[0]))
				self.diff2 = 0

			if MESSAGE_ANI_FROM == "bottom":
				self.diff2=(576-int(MESSAGE_POSITIONS_BG[1]))
				self.diff = 0

			if MESSAGE_ANI_FROM == "left":
				self.diff=(0-(int(MESSAGE_POSITIONS_BG[2])))
				self.diff2 = 0

			if MESSAGE_ANI_FROM == "top":
				self.diff2=(0-(int(MESSAGE_POSITIONS_BG[3])))
				self.diff = 0
		else:
			self.diff = 0
			self.diff2 = 0
		
	

		self.background=xbmcgui.ControlImage(MESSAGE_POSITIONS_BG[0]+self.diff,
											 MESSAGE_POSITIONS_BG[1]+self.diff2,
											 MESSAGE_POSITIONS_BG[2],
											 MESSAGE_POSITIONS_BG[3],
											 MEDIA_DIR + "message_background.png"
											 )
		self.addControl(self.background)

		self.title=xbmcgui.ControlLabel(MESSAGE_POSITIONS_TITLE[0]+self.diff,
										MESSAGE_POSITIONS_TITLE[1]+self.diff2,
										MESSAGE_POSITIONS_TITLE[2],
										MESSAGE_POSITIONS_TITLE[3],
										title,
										"font13",
										"#FFFFFFFF"
										)
		self.addControl(self.title)

		self.message=xbmcgui.ControlLabel(MESSAGE_POSITIONS_TEXT[0]+self.diff,
										MESSAGE_POSITIONS_TEXT[1]+self.diff2,
										MESSAGE_POSITIONS_TEXT[2],
										MESSAGE_POSITIONS_TEXT[3],
										message,
										"font13",
										"#FFFFFFFF"
										)
		self.addControl(self.message)
		
		self.button=xbmcgui.ControlButton(MESSAGE_POSITIONS_BUTTON[0]+self.diff,
										MESSAGE_POSITIONS_BUTTON[1]+self.diff2,
										MESSAGE_POSITIONS_BUTTON[2],
										MESSAGE_POSITIONS_BUTTON[3],
										glob.language.string(60),
										MEDIA_DIR + "button_focus.png",
										MEDIA_DIR + "button.png"
										)
		self.addControl(self.button)

		self.setFocus(self.button)








		
	def show_panel(self):
		if glob.settings["animation"] == "1":
			for pos in  range(10,-1,-1):
				time.sleep(0.01)
				self.animation(pos)

	def hide_panel(self):
		if glob.settings["animation"] == "1":
			for pos in range(0,10,1):
				time.sleep(0.01)
				self.animation(pos)

	def animation(self, pct):
		if MESSAGE_ANI_FROM == "right" or MESSAGE_ANI_FROM == "left":
			elmt_step=float(self.diff)/float(10)
			
			delta = int(pct*elmt_step)
			self.background.setPosition(int(MESSAGE_POSITIONS_BG[0])+delta, int(MESSAGE_POSITIONS_BG[1]))
			self.title.setPosition(int(MESSAGE_POSITIONS_TITLE[0])+delta, int(MESSAGE_POSITIONS_TITLE[1]))
			self.message.setPosition(int(MESSAGE_POSITIONS_TEXT[0])+delta, int(MESSAGE_POSITIONS_TEXT[1]))
			self.button.setPosition(int(MESSAGE_POSITIONS_BUTTON[0])+delta, int(MESSAGE_POSITIONS_BUTTON[1]))

		if MESSAGE_ANI_FROM == "bottom" or MESSAGE_ANI_FROM == "top":
			elmt_step=float(self.diff2)/float(int(glob.skin.get("menu1_animation_step")))
			
			delta = int(pct*elmt_step)
			self.background.setPosition(int(MESSAGE_POSITIONS_BG[0]), int(MESSAGE_POSITIONS_BG[1])+delta)
			self.title.setPosition(int(MESSAGE_POSITIONS_TITLE[0]), int(MESSAGE_POSITIONS_TITLE[1])+delta)
			self.message.setPosition(int(MESSAGE_POSITIONS_TEXT[0]), int(MESSAGE_POSITIONS_TEXT[1])+delta)
			self.button.setPosition(int(MESSAGE_POSITIONS_BUTTON[0]), int(MESSAGE_POSITIONS_BUTTON[1])+delta)


	def onAction(self, action):
		if action == ACTION_PREVIOUS_MENU:
			self.hide_panel()
			play_sound("menu_back")
			self.close()

	def onControl(self,control):
		play_sound("menu_select")
		if control==self.button:
			self.hide_panel()
			self.close()



class YesNo(xbmcgui.WindowDialog):
########################################################################
########################## YesNo Class #################################
########################################################################
	def __init__(self,title="",question=""):
		self.setCoordinateResolution(6)
		xbmcgui.Window.__init__(self)

		if glob.settings["animation"] == "1":
			if YESNO_ANI_FROM == "right":
				self.diff=(720-int(YESNO_POSITIONS_BG[0]))
				self.diff2 = 0

			if YESNO_ANI_FROM == "bottom":
				self.diff2=(576-int(YESNO_POSITIONS_BG[1]))
				self.diff = 0

			if YESNO_ANI_FROM == "left":
				self.diff=(0-(int(YESNO_POSITIONS_BG[2])))
				self.diff2 = 0

			if YESNO_ANI_FROM == "top":
				self.diff2=(0-(int(YESNO_POSITIONS_BG[3])))
				self.diff = 0
		else:
			self.diff = 0
			self.diff2 = 0
		
	

		self.background=xbmcgui.ControlImage(YESNO_POSITIONS_BG[0]+self.diff,
											 YESNO_POSITIONS_BG[1]+self.diff2,
											 YESNO_POSITIONS_BG[2],
											 YESNO_POSITIONS_BG[3],
											 MEDIA_DIR + "message_background.png"
											 )
		self.addControl(self.background)

		self.title=xbmcgui.ControlLabel(YESNO_POSITIONS_TITLE[0]+self.diff,
										YESNO_POSITIONS_TITLE[1]+self.diff2,
										YESNO_POSITIONS_TITLE[2],
										YESNO_POSITIONS_TITLE[3],
										title,
										"font13",
										"#FFFFFFFF"
										)
		self.addControl(self.title)

		self.message=xbmcgui.ControlLabel(YESNO_POSITIONS_TEXT[0]+self.diff,
										YESNO_POSITIONS_TEXT[1]+self.diff2,
										YESNO_POSITIONS_TEXT[2],
										YESNO_POSITIONS_TEXT[3],
										question,
										"font13",
										"#FFFFFFFF"
										)
		self.addControl(self.message)
		
		self.button=xbmcgui.ControlButton(YESNO_POSITIONS_BUTTON[0]+self.diff,
										YESNO_POSITIONS_BUTTON[1]+self.diff2,
										YESNO_POSITIONS_BUTTON[2],
										YESNO_POSITIONS_BUTTON[3],
										glob.language.string(103),
										MEDIA_DIR + "button_focus.png",
										MEDIA_DIR + "button.png"
										)
		self.addControl(self.button)

		self.button2=xbmcgui.ControlButton(YESNO_POSITIONS_BUTTON2[0]+self.diff,
										YESNO_POSITIONS_BUTTON2[1]+self.diff2,
										YESNO_POSITIONS_BUTTON2[2],
										YESNO_POSITIONS_BUTTON2[3],
										glob.language.string(104),
										MEDIA_DIR + "button_focus.png",
										MEDIA_DIR + "button.png"
										)
		self.addControl(self.button2)

		self.setFocus(self.button)

		self.button.controlRight(self.button2)
		self.button.controlLeft(self.button2)
		self.button2.controlRight(self.button)
		self.button2.controlLeft(self.button)






		
	def show_panel(self):
		if glob.settings["animation"] == "1":
			for pos in  range(10,-1,-1):
				time.sleep(0.01)
				self.animation(pos)

	def hide_panel(self):
		if glob.settings["animation"] == "1":
			for pos in range(0,10,1):
				time.sleep(0.01)
				self.animation(pos)

	def animation(self, pct):
		if YESNO_ANI_FROM == "right" or YESNO_ANI_FROM == "left":
			elmt_step=float(self.diff)/float(10)
			
			delta = int(pct*elmt_step)
			self.background.setPosition(int(YESNO_POSITIONS_BG[0])+delta, int(YESNO_POSITIONS_BG[1]))
			self.title.setPosition(int(YESNO_POSITIONS_TITLE[0])+delta, int(YESNO_POSITIONS_TITLE[1]))
			self.message.setPosition(int(YESNO_POSITIONS_TEXT[0])+delta, int(YESNO_POSITIONS_TEXT[1]))
			self.button.setPosition(int(YESNO_POSITIONS_BUTTON[0])+delta, int(YESNO_POSITIONS_BUTTON[1]))
			self.button2.setPosition(int(YESNO_POSITIONS_BUTTON2[0])+delta, int(YESNO_POSITIONS_BUTTON2[1]))

		if YESNO_ANI_FROM == "bottom" or YESNO_ANI_FROM == "top":
			elmt_step=float(self.diff2)/float(int(glob.skin.get("menu1_animation_step")))
			
			delta = int(pct*elmt_step)
			self.background.setPosition(int(YESNO_POSITIONS_BG[0]), int(YESNO_POSITIONS_BG[1])+delta)
			self.title.setPosition(int(YESNO_POSITIONS_TITLE[0]), int(YESNO_POSITIONS_TITLE[1])+delta)
			self.message.setPosition(int(YESNO_POSITIONS_TEXT[0]), int(YESNO_POSITIONS_TEXT[1])+delta)
			self.button.setPosition(int(YESNO_POSITIONS_BUTTON[0]), int(YESNO_POSITIONS_BUTTON[1])+delta)
			self.button2.setPosition(int(YESNO_POSITIONS_BUTTON2[0]), int(YESNO_POSITIONS_BUTTON2[1])+delta)


	def onAction(self, action):
		play_sound("menu_move")
		if action == ACTION_PREVIOUS_MENU:
			self.give=0
			self.hide_panel()
			play_sound("menu_back")
			self.close()

	def onControl(self,control):
		play_sound("menu_select")
		if control==self.button:
			self.give=1
			self.hide_panel()
			self.close()
		if control==self.button2:
			self.give=0
			self.hide_panel()
			self.close()



class Highscore(xbmcgui.WindowDialog):
########################################################################
###################### Highscore Class #################################
########################################################################
	def __init__(self):
		self.setCoordinateResolution(6)
		xbmcgui.Window.__init__(self)


		if glob.settings["animation"] == "1":
			if HIGHSCORE_ANI_FROM == "right":
				self.diff=(720-int(HIGHSCORE_POSITIONS_BG[0]))
				self.diff2 = 0

			if HIGHSCORE_ANI_FROM == "bottom":
				self.diff2=(576-int(HIGHSCORE_POSITIONS_BG[1]))
				self.diff = 0

			if HIGHSCORE_ANI_FROM == "left":
				self.diff=(0-(int(HIGHSCORE_POSITIONS_BG[2])))
				self.diff2 = 0

			if HIGHSCORE_ANI_FROM == "top":
				self.diff2=(0-(int(HIGHSCORE_POSITIONS_BG[3])))
				self.diff = 0
		else:
			self.diff = 0
			self.diff2 = 0

		self.build_menu()



	def message(self, title, message):
		themessage = Message(title=title,message=message)
		themessage.show()
		themessage.show_panel()
		themessage.doModal()
		del themessage


	def question(self, title, question):
		themessage = YesNo(title=title,question=question)
		themessage.show()
		themessage.show_panel()
		themessage.doModal()
		self.temp = themessage.give
		del themessage
		return self.temp


	def build_menu(self):
		self.background=xbmcgui.ControlImage(HIGHSCORE_POSITIONS_BG[0]+self.diff,
											 HIGHSCORE_POSITIONS_BG[1]+self.diff2,
											 HIGHSCORE_POSITIONS_BG[2],
											 HIGHSCORE_POSITIONS_BG[3],
											 MEDIA_DIR + "box.png"
											 )
		self.addControl(self.background)

		self.delButton=xbmcgui.ControlButton(HIGHSCORE_POSITIONS_BUTTON[0]+self.diff,
											HIGHSCORE_POSITIONS_BUTTON[1]+self.diff2,
											HIGHSCORE_POSITIONS_BUTTON[2],
											HIGHSCORE_POSITIONS_BUTTON[3],
											glob.language.string(105),
											MEDIA_DIR + "button_focus.png",
											MEDIA_DIR + "button.png"
											)
		self.addControl(self.delButton)

		self.quitButton=xbmcgui.ControlButton(HIGHSCORE_POSITIONS_BUTTON2[0]+self.diff,
											HIGHSCORE_POSITIONS_BUTTON2[1]+self.diff2,
											HIGHSCORE_POSITIONS_BUTTON2[2],
											HIGHSCORE_POSITIONS_BUTTON2[3],
											glob.language.string(106),
											MEDIA_DIR + "button_focus.png",
											MEDIA_DIR + "button.png"
											)
		self.addControl(self.quitButton)

		self.delButton.controlUp(self.quitButton)
		self.delButton.controlDown(self.quitButton)
		self.quitButton.controlUp(self.delButton)
		self.quitButton.controlDown(self.delButton)

		self.setFocus(self.delButton)

	def create_lists(self):
		self.templist = []
		self.levels = glob.levels #+glob.clevels
		for test in glob.highscores.keys():
			self.templist.append([int(glob.highscores[test]["score"]),test])
			if not glob.highscores[test]["level"] in self.levels:
				self.levels.append(glob.highscores[test]["level"])

		self.templist.sort()
		self.templist.reverse()

		self.scoreControls = {}
		for item in self.levels:
			self.scoreControls[item] = {}
			self.scoreControls[item]["list"] = xbmcgui.ControlList(HIGHSCORE_POSITIONS_LIST[0],
																	HIGHSCORE_POSITIONS_LIST[1],
																	HIGHSCORE_POSITIONS_LIST[2],
																	HIGHSCORE_POSITIONS_LIST[3],
																	buttonFocusTexture=MEDIA_DIR + "button_focus.png",
																	buttonTexture=MEDIA_DIR + "button.png",
																	textColor="#FFFFFFFF",
																	font="font12"
																	)
			self.addControl(self.scoreControls[item]["list"])
			self.scoreControls[item]["list"].setVisible(0)

			self.scoreControls[item]["label"] = xbmcgui.ControlLabel(HIGHSCORE_POSITIONS_LABEL[0],
																	 HIGHSCORE_POSITIONS_LABEL[1],
																	 HIGHSCORE_POSITIONS_LABEL[2],
																	 HIGHSCORE_POSITIONS_LABEL[3],
																	 "",
																	 "font12",
																	 "#FFFFFFFF"
																	 )
			self.addControl(self.scoreControls[item]["label"])
			self.scoreControls[item]["label"].setLabel(item)
			self.scoreControls[item]["label"].setVisible(0)

			self.scoreControls[item]["listitems"] = 0
			for temp in self.templist:
				if glob.highscores[temp[1]]["level"] == item:
					self.scoreControls[item]["listitems"] += 1
					self.scoreControls[item]["list"].addItem(	xbmcgui.ListItem(
																label = str(self.scoreControls[item]["listitems"]) + ". " + str(glob.highscores[temp[1]]["name"]),
																label2 = str(glob.highscores[temp[1]]["score"])
																)
															)
			if self.scoreControls[item]["listitems"] == 0:
				self.scoreControls[item]["list"].addItem("no highscores")

			self.currentControl = 0
			self.scoreControls[self.levels[self.currentControl]]["list"].setVisible(1)
			self.scoreControls[self.levels[self.currentControl]]["label"].setVisible(1)







	def show_panel(self):
		if glob.settings["animation"] == "1":
			for pos in  range(10,-1,-1):
				time.sleep(0.01)
				self.animation(pos)
		self.create_lists()

	def hide_panel(self):
		self.scoreControls[self.levels[self.currentControl]]["list"].setVisible(0)
		self.scoreControls[self.levels[self.currentControl]]["label"].setVisible(0)
		if glob.settings["animation"] == "1":
			for pos in range(0,10,1):
				time.sleep(0.01)
				self.animation(pos)

	def animation(self, pct):
		if HIGHSCORE_ANI_FROM == "right" or HIGHSCORE_ANI_FROM == "left":
			elmt_step=float(self.diff)/float(10)
			
			delta = int(pct*elmt_step)
			self.background.setPosition(int(HIGHSCORE_POSITIONS_BG[0])+delta, int(HIGHSCORE_POSITIONS_BG[1]))
			self.delButton.setPosition(int(HIGHSCORE_POSITIONS_BUTTON[0])+delta, int(HIGHSCORE_POSITIONS_BUTTON[1]))
			self.quitButton.setPosition(int(HIGHSCORE_POSITIONS_BUTTON2[0])+delta, int(HIGHSCORE_POSITIONS_BUTTON2[1]))

		if HIGHSCORE_ANI_FROM == "bottom" or HIGHSCORE_ANI_FROM == "top":
			elmt_step=float(self.diff2)/float(int(glob.skin.get("menu1_animation_step")))
			
			delta = int(pct*elmt_step)
			self.background.setPosition(int(HIGHSCORE_POSITIONS_BG[0]), int(HIGHSCORE_POSITIONS_BG[1])+delta)
			self.delButton.setPosition(int(HIGHSCORE_POSITIONS_BUTTON[0]), int(HIGHSCORE_POSITIONS_BUTTON[1])+delta)
			self.quitButton.setPosition(int(HIGHSCORE_POSITIONS_BUTTON2[0]), int(HIGHSCORE_POSITIONS_BUTTON2[1])+delta)


	def onAction(self, action):
		play_sound("menu_move")
		if action == ACTION_PREVIOUS_MENU:
			self.hide_panel()
			play_sound("menu_back")
			self.close()

		if action == ACTION_DPAD_RIGHT:
			if self.currentControl < len(self.levels)-1:
				self.scoreControls[self.levels[self.currentControl]]["list"].setVisible(0)
				self.scoreControls[self.levels[self.currentControl]]["label"].setVisible(0)
				self.currentControl += 1
				self.scoreControls[self.levels[self.currentControl]]["list"].setVisible(1)
				self.scoreControls[self.levels[self.currentControl]]["label"].setVisible(1)

		if action == ACTION_DPAD_LEFT:
			if self.currentControl > 0:
				self.scoreControls[self.levels[self.currentControl]]["list"].setVisible(0)
				self.scoreControls[self.levels[self.currentControl]]["label"].setVisible(0)
				self.currentControl -= 1
				self.scoreControls[self.levels[self.currentControl]]["list"].setVisible(1)
				self.scoreControls[self.levels[self.currentControl]]["label"].setVisible(1)

	def onControl(self, control):
		if control == self.quitButton:
			self.hide_panel()
			play_sound("menu_back")
			self.close()

		if control == self.delButton:
			if self.question(glob.language.string(87), glob.language.string(125)+"\n" + self.levels[self.currentControl] + "?"):
				temp = glob.highscores.keys()
				self.new_highscores = {}
				
				for item in temp:
					if glob.highscores[item]["level"] != self.levels[self.currentControl]:
						self.new_highscores[item] = {}
						self.new_highscores[item]["name"] = glob.highscores[item]["name"]
						self.new_highscores[item]["score"] = glob.highscores[item]["score"]
						self.new_highscores[item]["level"] = glob.highscores[item]["level"]

				glob.highscores = {}
				glob.highscores = self.new_highscores
				self.scoreControls[self.levels[self.currentControl]]["list"].reset()
				self.scoreControls[self.levels[self.currentControl]]["list"].addItem("no highscores")
				save_highscore()
		play_sound("menu_select")



class OHighscore(xbmcgui.WindowDialog):
########################################################################
################### Online Highscore Class #############################
########################################################################
	def __init__(self):
		self.setCoordinateResolution(6)
		xbmcgui.Window.__init__(self)
		

		if glob.settings["animation"] == "1":
			if OHIGHSCORE_ANI_FROM == "right":
				self.diff=(720-int(OHIGHSCORE_POSITIONS_BG[0]))
				self.diff2 = 0

			if OHIGHSCORE_ANI_FROM == "bottom":
				self.diff2=(576-int(OHIGHSCORE_POSITIONS_BG[1]))
				self.diff = 0

			if OHIGHSCORE_ANI_FROM == "left":
				self.diff=(0-(int(OHIGHSCORE_POSITIONS_BG[2])))
				self.diff2 = 0

			if OHIGHSCORE_ANI_FROM == "top":
				self.diff2=(0-(int(OHIGHSCORE_POSITIONS_BG[3])))
				self.diff = 0
		else:
			self.diff = 0
			self.diff2 = 0

		self.build_menu()
		self.update_menu()



	def message(self, title, message):
		themessage = Message(title=title,message=message)
		themessage.show()
		themessage.show_panel()
		themessage.doModal()
		del themessage


	def question(self, title, question):
		themessage = YesNo(title=title,question=question)
		themessage.show()
		themessage.show_panel()
		themessage.doModal()
		self.temp = themessage.give
		del themessage
		return self.temp


	def build_menu(self):
		self.background=xbmcgui.ControlImage(OHIGHSCORE_POSITIONS_BG[0]+self.diff,
											 OHIGHSCORE_POSITIONS_BG[1]+self.diff2,
											 OHIGHSCORE_POSITIONS_BG[2],
											 OHIGHSCORE_POSITIONS_BG[3],
											 MEDIA_DIR + "box_black.png"
											 )
		self.addControl(self.background)

		self.menuList=xbmcgui.ControlList(OHIGHSCORE_POSITIONS_LIST[0]+self.diff,
											OHIGHSCORE_POSITIONS_LIST[1]+self.diff2,
											OHIGHSCORE_POSITIONS_LIST[2],
											OHIGHSCORE_POSITIONS_LIST[3],
											buttonFocusTexture=MEDIA_DIR + "button_focus.png",
											buttonTexture=MEDIA_DIR + "button.png",
											textColor="#FFFFFFFF",
											font="font12"
											)
		self.addControl(self.menuList)

		self.showScoreLabel = xbmcgui.ControlLabel(OHIGHSCORE_POSITIONS_HS[0]+self.diff,
											OHIGHSCORE_POSITIONS_HS[1]+self.diff2,
											OHIGHSCORE_POSITIONS_HS[2],
											OHIGHSCORE_POSITIONS_HS[3],
											"",
											"font18",
											"#FFFFFFFF"
											)
		self.addControl(self.showScoreLabel)

		self.setFocus(self.menuList)



	def update_menu(self):
		self.menuList.reset()
		self.levellist_str = ONLINEHIGHSCORE.get_level_list(str(glob.OHSGameID))
		self.lines_got = self.levellist_str.split("\n")
		self.allLevels = {}
		for lev in self.lines_got:
			if lev != "":
				lev2 = lev.split("|")
				self.allLevels[lev2[0]] = lev2[1]
				self.menuList.addItem(str(lev2[0]))



	def show_panel(self):
		if glob.settings["animation"] == "1":
			for pos in  range(10,-1,-1):
				time.sleep(0.01)
				self.animation(pos)

	def hide_panel(self):
		if glob.settings["animation"] == "1":
			for pos in range(0,10,1):
				time.sleep(0.01)
				self.animation(pos)

	def animation(self, pct):
		if OHIGHSCORE_ANI_FROM == "right" or OHIGHSCORE_ANI_FROM == "left":
			elmt_step=float(self.diff)/float(10)

			delta = int(pct*elmt_step)
			self.background.setPosition(int(OHIGHSCORE_POSITIONS_BG[0])+delta, int(OHIGHSCORE_POSITIONS_BG[1]))
			self.menuList.setPosition(int(OHIGHSCORE_POSITIONS_LIST[0])+delta, int(OHIGHSCORE_POSITIONS_LIST[1]))
			self.showScoreLabel.setPosition(int(OHIGHSCORE_POSITIONS_HS[0])+delta, int(OHIGHSCORE_POSITIONS_HS[1]))


		if OHIGHSCORE_ANI_FROM == "bottom" or OHIGHSCORE_ANI_FROM == "top":
			elmt_step=float(self.diff2)/float(int(glob.skin.get("menu1_animation_step")))

			delta = int(pct*elmt_step)
			self.background.setPosition(int(OHIGHSCORE_POSITIONS_BG[0]), int(OHIGHSCORE_POSITIONS_BG[1])+delta)
			self.menuList.setPosition(int(OHIGHSCORE_POSITIONS_LIST[0]), int(OHIGHSCORE_POSITIONS_LIST[1])+delta)
			self.showScoreLabel.setPosition(int(OHIGHSCORE_POSITIONS_HS[0]), int(OHIGHSCORE_POSITIONS_HS[1])+delta)




	def onAction(self, action):
		play_sound("menu_move")
		if action == ACTION_PREVIOUS_MENU:
			self.hide_panel()
			play_sound("menu_back")
			self.close()

	def onControl(self, control):
		play_sound("menu_select")
		if control == self.menuList:
			self.item=self.menuList.getSelectedItem()
			self.item2 = self.item.getLabel()
			
			self.hsrs = ONLINEHIGHSCORE.get_highscore(str(glob.OHSGameID),str(self.allLevels[self.item2]))
			self.hsrs = self.hsrs.replace("|",": ")
			self.showScoreLabel.setLabel("          "+glob.language.string(107)+": "+self.item2+"\n\n"+self.hsrs)

			#self.showScoreLabel.setLabel(str(self.allLevels[self.item2]))



class MyProfile(xbmcgui.WindowDialog):
########################################################################
######################## Profile Class #################################
########################################################################
	def __init__(self):
		self.setCoordinateResolution(6)
		xbmcgui.Window.__init__(self)


		if glob.settings["animation"] == "1":
			if PROFILE_ANI_FROM == "right":
				self.diff=(720-int(PROFILE_POSITIONS_BG[0]))
				self.diff2 = 0

			if PROFILE_ANI_FROM == "bottom":
				self.diff2=(576-int(PROFILE_POSITIONS_BG[1]))
				self.diff = 0

			if PROFILE_ANI_FROM == "left":
				self.diff=(0-(int(HIGHSCORE_POSITIONS_BG[2])))
				self.diff2 = 0

			if PROFILE_ANI_FROM == "top":
				self.diff2=(0-(int(PROFILE_POSITIONS_BG[3])))
				self.diff = 0
		else:
			self.diff = 0
			self.diff2 = 0

		self.build_menu()
		self.update_menu()
		self.getGamerpic()


	def message(self, title, message):
		themessage = Message(title=title,message=message)
		themessage.show()
		themessage.show_panel()
		themessage.doModal()
		del themessage


	def question(self, title, question):
		themessage = YesNo(title=title,question=question)
		themessage.show()
		themessage.show_panel()
		themessage.doModal()
		self.temp = themessage.give
		del themessage
		return self.temp


	def build_menu(self):
		self.background=xbmcgui.ControlImage(PROFILE_POSITIONS_BG[0]+self.diff,
											PROFILE_POSITIONS_BG[1]+self.diff2,
											PROFILE_POSITIONS_BG[2],
											PROFILE_POSITIONS_BG[3],
											MEDIA_DIR + "box_black.png"
											)
		self.addControl(self.background)

		self.infoLabel = xbmcgui.ControlLabel(PROFILE_POSITIONS_TEXT[0]+self.diff,
											PROFILE_POSITIONS_TEXT[1]+self.diff2,
											PROFILE_POSITIONS_TEXT[2],
											PROFILE_POSITIONS_TEXT[3],
											"",
											"font13",
											"#FFFFFFFF"
											)
		self.addControl(self.infoLabel)

		self.infoLabel2 = xbmcgui.ControlLabel(PROFILE_POSITIONS_TEXT2[0]+self.diff,
											PROFILE_POSITIONS_TEXT2[1]+self.diff2,
											PROFILE_POSITIONS_TEXT2[2],
											PROFILE_POSITIONS_TEXT2[3],
											"",
											"font12",
											"#FFFFFFFF"
											)
		self.addControl(self.infoLabel2)

		self.menuList=xbmcgui.ControlList(PROFILE_POSITIONS_LIST[0]+self.diff,
											PROFILE_POSITIONS_LIST[1]+self.diff2,
											PROFILE_POSITIONS_LIST[2],
											PROFILE_POSITIONS_LIST[3],
											buttonFocusTexture=MEDIA_DIR + "button_focus.png",
											buttonTexture=MEDIA_DIR + "button.png",
											textColor="#FFFFFFFF",
											font="font12"
											)
		self.addControl(self.menuList)
		
		self.gamerpicture=xbmcgui.ControlImage(PROFILE_POSITIONS_GP[0]+self.diff,
												PROFILE_POSITIONS_GP[1]+self.diff2,
												PROFILE_POSITIONS_GP[2],
												PROFILE_POSITIONS_GP[3],
												""
												)
		self.addControl(self.gamerpicture)

		self.setFocus(self.menuList)


	def update_menu(self):
		self.check_account()

		self.menuList.reset()
		if self.theUID == "0":
			self.choix=[glob.language.string(108),glob.language.string(109)]
		else:
			self.choix=[glob.language.string(110),glob.language.string(109)]
		for ch in self.choix:
			self.menuList.addItem(ch)

		self.load_infos()

	def load_infos(self):
		if self.theUID == "0":
			self.infoLabel.setLabel(glob.language.string(111))
		else:
			self.infoLabel.setLabel(glob.language.string(53)+": "+glob.settings["name"]+"\n"+glob.language.string(112)+": "+glob.settings["userID"])
		
		#self.levellist = ONLINEHIGHSCORE.get_level_list(str(glob.OHSGameID))
		#self.infoLabel2.setLabel("Level:\n"+self.levellist)

	def check_account(self):
		if glob.settings["name"] != "-" and glob.settings["pass"] != "-":
			self.theUID = ONLINEHIGHSCORE.get_user_id(str(glob.settings["name"]),str(glob.settings["pass"]))
		else:
			self.theUID = "0"







	def show_panel(self):
		if glob.settings["animation"] == "1":
			for pos in  range(10,-1,-1):
				time.sleep(0.01)
				self.animation(pos)
		self.gamerpicture.setVisible(1)

	def hide_panel(self):
		if glob.settings["animation"] == "1":
			for pos in range(0,10,1):
				time.sleep(0.01)
				self.animation(pos)

	def animation(self, pct):
		if PROFILE_ANI_FROM == "right" or PROFILE_ANI_FROM == "left":
			elmt_step=float(self.diff)/float(10)
			
			delta = int(pct*elmt_step)
			self.background.setPosition(int(PROFILE_POSITIONS_BG[0])+delta, int(PROFILE_POSITIONS_BG[1]))
			self.menuList.setPosition(int(PROFILE_POSITIONS_LIST[0])+delta, int(PROFILE_POSITIONS_LIST[1]))
			self.infoLabel.setPosition(int(PROFILE_POSITIONS_TEXT[0])+delta, int(PROFILE_POSITIONS_TEXT[1]))
			self.infoLabel2.setPosition(int(PROFILE_POSITIONS_TEXT2[0])+delta, int(PROFILE_POSITIONS_TEXT2[1]))
			self.gamerpicture.setPosition(int(PROFILE_POSITIONS_GP[0])+delta, int(PROFILE_POSITIONS_GP[1]))

		if PROFILE_ANI_FROM == "bottom" or PROFILE_ANI_FROM == "top":
			elmt_step=float(self.diff2)/float(int(glob.skin.get("menu1_animation_step")))
			
			delta = int(pct*elmt_step)
			self.background.setPosition(int(PROFILE_POSITIONS_BG[0]), int(PROFILE_POSITIONS_BG[1])+delta)
			self.menuList.setPosition(int(PROFILE_POSITIONS_LIST[0]), int(PROFILE_POSITIONS_LIST[1])+delta)
			self.infoLabel.setPosition(int(PROFILE_POSITIONS_TEXT[0]), int(PROFILE_POSITIONS_TEXT[1])+delta)
			self.infoLabel2.setPosition(int(PROFILE_POSITIONS_TEXT2[0]), int(PROFILE_POSITIONS_TEXT2[1])+delta)
			self.gamerpicture.setPosition(int(PROFILE_POSITIONS_GP[0]), int(PROFILE_POSITIONS_GP[1])+delta)


	def onAction(self, action):
		play_sound("menu_move")
		if action == ACTION_PREVIOUS_MENU:
			self.hide_panel()
			play_sound("menu_back")
			self.close()


	def onControl(self, control):
		play_sound("menu_select")
		if control == self.menuList:
			self.number=self.menuList.getSelectedPosition()

			if self.theUID == "0":
				if self.number == 1:
					self.new_name = ""
					self.new_pass1 = ""
					self.new_pass2 = ""

					if glob.settings["name"] == "-":
						self.oldname = ""
					else:
						self.oldname = glob.settings["name"]
					keyboard = xbmc.Keyboard(self.oldname,glob.language.string(33))
					keyboard.doModal()
					if(keyboard.isConfirmed()):
						self.new_name = keyboard.getText()

						keyboard2 = xbmc.Keyboard("",glob.language.string(113))
						keyboard2.doModal()
						if(keyboard2.isConfirmed()):
							self.new_pass1 = keyboard2.getText()

							keyboard3 = xbmc.Keyboard("",glob.language.string(114))
							keyboard3.doModal()
							if(keyboard3.isConfirmed()):
								self.new_pass2 = keyboard3.getText()

					if self.new_name != "" and self.new_pass1 != "" and self.new_pass2 != "":
						if self.new_pass1 == self.new_pass2:
							self.newUID = ONLINEHIGHSCORE.create_new_user(str(self.new_name),str(self.new_pass1))
							if self.newUID == "-1":
								self.message(glob.language.string(39),glob.language.string(115))
							elif self.newUID == "0":
								self.message(glob.language.string(39),glob.language.string(116))
							else:
								self.message(glob.language.string(118),glob.language.string(119)+" " + str(self.new_name) + "\n"+glob.language.string(117))
								glob.settings["userID"] = self.newUID
								glob.settings["name"] = str(self.new_name)
								glob.settings["pass"] = str(self.new_pass1)
								self.message(glob.language.string(8),glob.language.string(120))
								self.update_menu()
						else:
							self.message(glob.language.string(39),glob.language.string(121))

				if self.number == 0:
					self.new_name = ""
					self.new_pass1 = ""

					if glob.settings["name"] == "-":
						self.oldname = ""
					else:
						self.oldname = glob.settings["name"]
					keyboard = xbmc.Keyboard(self.oldname,glob.language.string(33))
					keyboard.doModal()
					if(keyboard.isConfirmed()):
						self.new_name = keyboard.getText()

						keyboard2 = xbmc.Keyboard("",glob.language.string(113))
						keyboard2.doModal()
						if(keyboard2.isConfirmed()):
							self.new_pass1 = keyboard2.getText()


					if self.new_name != "" and self.new_pass1 != "":
						self.newUID = ONLINEHIGHSCORE.get_user_id(str(self.new_name),str(self.new_pass1))
						if self.newUID == "0":
							self.message(glob.language.string(39),glob.language.string(116)+"\n"+glob.language.string(122)+"?")
						else:
							self.message(glob.language.string(118),glob.language.string(119)+" " + str(self.new_name) + "\n"+glob.language.string(123))
							glob.settings["userID"] = self.newUID
							glob.settings["name"] = str(self.new_name)
							glob.settings["pass"] = str(self.new_pass1)
							self.update_menu()
							self.getGamerpic()
			else:
				if self.number == 0:
					self.new_name = ""
					self.new_pass1 = ""

					if glob.settings["name"] == "-":
						self.oldname = ""
					else:
						self.oldname = glob.settings["name"]
					keyboard = xbmc.Keyboard(self.oldname,glob.language.string(33))
					keyboard.doModal()
					if(keyboard.isConfirmed()):
						self.new_name = keyboard.getText()

						keyboard2 = xbmc.Keyboard("",glob.language.string(113))
						keyboard2.doModal()
						if(keyboard2.isConfirmed()):
							self.new_pass1 = keyboard2.getText()


					if self.new_name != "" and self.new_pass1 != "":
						self.newUID = ONLINEHIGHSCORE.get_user_id(str(self.new_name),str(self.new_pass1))
						if self.newUID == "0":
							self.message(glob.language.string(39),glob.language.string(116)+"\n"+glob.language.string(122)+"?")
						else:
							self.message(glob.language.string(118),glob.language.string(119)+" " + str(self.new_name) + "\n"+glob.language.string(123))
							glob.settings["userID"] = self.newUID
							glob.settings["name"] = str(self.new_name)
							glob.settings["pass"] = str(self.new_pass1)
							self.update_menu()
							self.getGamerpic()

				if self.number == 1:
					self.new_name = ""
					self.new_pass1 = ""
					self.new_pass2 = ""

					if glob.settings["name"] == "-":
						self.oldname = ""
					else:
						self.oldname = glob.settings["name"]
					keyboard = xbmc.Keyboard(self.oldname,glob.language.string(33))
					keyboard.doModal()
					if(keyboard.isConfirmed()):
						self.new_name = keyboard.getText()

						keyboard2 = xbmc.Keyboard("",glob.language.string(113))
						keyboard2.doModal()
						if(keyboard2.isConfirmed()):
							self.new_pass1 = keyboard2.getText()

							keyboard3 = xbmc.Keyboard("",glob.language.string(114))
							keyboard3.doModal()
							if(keyboard3.isConfirmed()):
								self.new_pass2 = keyboard3.getText()

					if self.new_name != "" and self.new_pass1 != "" and self.new_pass2 != "":
						if self.new_pass1 == self.new_pass2:
							self.newUID = ONLINEHIGHSCORE.create_new_user(str(self.new_name),str(self.new_pass1))
							if self.newUID == "-1":
								self.message(glob.language.string(39),glob.language.string(115))
							elif self.newUID == "0":
								self.message(glob.language.string(39),glob.language.string(116))
							else:
								self.message(glob.language.string(118),glob.language.string(119)+" " + str(self.new_name) + "\n"+glob.language.string(117))
								glob.settings["userID"] = self.newUID
								glob.settings["name"] = str(self.new_name)
								glob.settings["pass"] = str(self.new_pass1)
								self.message(glob.language.string(8),glob.language.string(120))
								self.update_menu()
								self.getGamerpic()
						else:
							self.message(glob.language.string(39),glob.language.string(121))




	def getGamerpic(self):
		if glob.settings["userID"] == "0":
			if os.path.exists(os.path.join( SPECIAL_SCRIPT_DATA, GAMERPICTURE )):
				self.thePic = os.path.join( SPECIAL_SCRIPT_DATA, GAMERPICTURE )
			else:
				self.thePic = "0"
		else:
			self.temp = ONLINEHIGHSCORE.get_picture_url(str(glob.settings["userID"]))
			if self.temp != "0":
				self.progressbar = Progress(text=glob.language.string(17))
				self.progressbar.show()
				self.progressbar.update_progress(1,glob.language.string(124))
				self.save(self.temp,os.path.join( SPECIAL_SCRIPT_DATA, GAMERPICTURE ))
				self.progressbar.close()
				del self.progressbar
				self.thePic = os.path.join( SPECIAL_SCRIPT_DATA, GAMERPICTURE )
			else:
				self.thePic = "0"

		if self.thePic != "0":
			self.removeControl(self.gamerpicture)

			self.gamerpicture=xbmcgui.ControlImage(PROFILE_POSITIONS_GP[0],
													PROFILE_POSITIONS_GP[1],
													PROFILE_POSITIONS_GP[2],
													PROFILE_POSITIONS_GP[3],
													self.thePic
													)
			self.gamerpicture.setVisible(0)
			self.addControl(self.gamerpicture)


	def hook(self, count_blocks, block_size, total_size):
		current_size = block_size * count_blocks
		value = current_size * 100 / total_size
		self.progressbar.update_progress(value,glob.language.string(124))

	def save(self, url,destination):
		try:
			DL=urllib.urlretrieve( url , destination , self.hook)
		except:
			print "exception while downloading"



class Progress(xbmcgui.WindowDialog):
########################################################################
######################## Progress Class ################################
########################################################################
	def __init__(self,text=""):
		self.setCoordinateResolution(6)


		self.progressBackground = xbmcgui.ControlImage(PROGRESS_POSITIONS_BG[0],
														PROGRESS_POSITIONS_BG[1],
														PROGRESS_POSITIONS_BG[2],
														PROGRESS_POSITIONS_BG[3],
														MEDIA_DIR + "progress_background.png"
														)
		self.addControl(self.progressBackground)

		self.progressBar = xbmcgui.ControlImage(PROGRESS_POSITIONS_BAR[0],
												PROGRESS_POSITIONS_BAR[1],
												PROGRESS_POSITIONS_BAR[2],
												PROGRESS_POSITIONS_BAR[3],
												MEDIA_DIR + "progress_bar.png"
												)
		self.addControl(self.progressBar)

		self.progressBarOver = xbmcgui.ControlImage(PROGRESS_POSITIONS_BAR[0],
												PROGRESS_POSITIONS_BAR[1],
												PROGRESS_POSITIONS_BAR[2],
												PROGRESS_POSITIONS_BAR[3],
												MEDIA_DIR + "progress_bar_overlay.png"
												)
		self.addControl(self.progressBarOver)

		self.progressLabel = xbmcgui.ControlLabel(PROGRESS_POSITIONS_LABEL[0],
												PROGRESS_POSITIONS_LABEL[1],
												PROGRESS_POSITIONS_LABEL[2],
												PROGRESS_POSITIONS_LABEL[3],
												text,
												"font10",
												"FFFFFFFF"
												)
		self.addControl(self.progressLabel)


	def update_progress(self,width,text=""):
		if text != "":
			self.progressLabel.setLabel(text)

		self.new_width = int((width*PROGRESS_POSITIONS_BAR[2])/100)
		if self.new_width > PROGRESS_POSITIONS_BAR[2]:
			self.progressBar.setWidth(PROGRESS_POSITIONS_BAR[2])
		else:
			self.progressBar.setWidth(self.new_width)





























#xbmc.enableNavSounds(0)

check_connection()
if glob.CONNECTION == 1:
	create_game_in_db()

run = Main()
run.show()
run.load_stuff()

run.doModal()

del run

print "stopping script"
print "-----------------------------"
save_current_settings()
print "script stopped"
#xbmc.enableNavSounds(1)
