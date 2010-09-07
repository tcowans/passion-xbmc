#
# Snake-Game for XBMC
# a Project of Rocko, tAGEdIEB and JackTramiel
#


__title__ = "Snake"
__addonID__ = "script.game.tetris"


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
INFOFILE						= SRC_DIR+"info.xml"
#SETTINGSPATH					= "P:\\snake\\"
#SETTINGSFILE					= "settings.xml"

SPECIAL_PROFILE_DIR = xbmc.translatePath( "special://profile/" )
SPECIAL_SCRIPT_DATA = os.path.join( SPECIAL_PROFILE_DIR, "addon_data", __addonID__ )
if not os.path.isdir( SPECIAL_SCRIPT_DATA ): os.makedirs( SPECIAL_SCRIPT_DATA )
SNAKE_SETTINGS = os.path.join( SPECIAL_SCRIPT_DATA, "settings.xml" )


sys.path.append(LIB_DIR)
import lang
import level
import onlinehighscores

ONLINEHIGHSCORE=onlinehighscores.highscore()

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














class Main(xbmcgui.Window):
########################################################################################
############################### MAIN CLASS #############################################
########################################################################################
	def __init__(self):
		self.setCoordinateResolution(6)

		self.load_settings()
		self.load_info()
		self.load_language()


	def onAction(self, action):
		play_sound("menu_move")


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

	def load_language(self):
		glob.language = lang.Language()
		glob.language.load(LANG_DIR)
		print "-----------------------------"

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

	def hook(self, count_blocks, block_size, total_size):
		current_size = block_size * count_blocks
		value = current_size * 100 / total_size
		self.progressbar.update_progress(value,glob.language.string(18))

	def save(self, url,destination):
		try:
			DL=urllib.urlretrieve( url , destination , self.hook)
		except:
			print "exception while downloading"



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

run = Main()
del run

xbmc.executescript(HOME_DIR+"game.py")