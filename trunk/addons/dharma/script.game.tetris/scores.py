###################################################################
#
#   Tetris v1.0
#		by asteron  
#
#  This module is pretty much entirely self contained, the interface to it is the showDialog on the gameDialog class
#  You do have to load its settings manually though.
###################################################################

__addonID__ = "script.game.tetris"

import xbmc,xbmcgui
import onlinehighscores
import os, threading, traceback

SPECIAL_PROFILE_DIR = xbmc.translatePath( "special://profile/" )
SPECIAL_SCRIPT_DATA = os.path.join( SPECIAL_PROFILE_DIR, "addon_data", __addonID__ )
if not os.path.isdir( SPECIAL_SCRIPT_DATA ): os.makedirs( SPECIAL_SCRIPT_DATA )
TETRIS_SCORES = os.path.join( SPECIAL_SCRIPT_DATA, "%s_scores.txt" )

MAX_SCORE_LENGTH = 10

ACTION_PARENT_DIR	= 9
ACTION_STOP		= 13
ACTION_PREVIOUS_MENU	= 10

COORD_720P    = 1
COORD_PAL_4X3    = 6 


DO_LOGGING = 0
try:
	LOG_FILE.close()
except Exception:
	pass
if DO_LOGGING:
	LOG_FILE = open(os.getcwd()[:-1]+"\\scorelog.txt",'w')
def LOG(message):
	if DO_LOGGING:
		LOG_FILE.write(str(message)+"\n")
		LOG_FILE.flush()	
def LOGCLOSE():
	if DO_LOGGING:
		LOG_FILE.close()
		
def unikeyboard(default,header=""):
	"""
		Opens XBMC Virtual Keyboard
		Give it the Default value and header and it will return the value entered
		If user cancelled it will return the default text.
	"""
	kb = xbmc.Keyboard(default,header)
	kb.doModal()
	while (kb.isConfirmed()):
		text = kb.getText()
		if len(text) > 0:
			return text
		kb.doModal()
	return default

#avoid stretching on different pixel aspect ratios
def noStretch(window):
	if window.getResolution() < 2: window.setCoordinateResolution(COORD_720P)
	else: window.setCoordinateResolution(COORD_PAL_4X3)
	
# I had problems with onlinehighscores giving exceptions if network unplugged...  wrap it up to be safe
class SafeOnlineHighScores:
	def __init__(self):
		self.ohs = onlinehighscores.highscore()

	def get_user_id(self,u,p):
		LOG("GUI! - " + u+'-'+p)
		try:
			return self.ohs.get_user_id(u,p)
		except Exception:
			return "0"
	def create_new_user(self,u,p):
		LOG("CNU! -"+u+"|"+p)
		try:
			return self.ohs.create_new_user(u,p)
		except Exception:
			return "0"
	def insert_new_highscore(self,gi,ui,sc):
		LOG("INH!")
		try:
			return self.ohs.insert_new_highscore(gi,ui,sc)
		except Exception:
			traceback.print_exc()
			return "0"
	def get_highscore(self,i):
		LOG("GHS - " + str(i))
		try:
			return self.ohs.get_highscore(i)
		except Exception:
			LOG("GHS error")
			traceback.print_exc()
			return ""
	def get_game_id(self,g):
		LOG("GGID - " + g)
		try:
			return self.ohs.get_game_id(g)
		except Exception:
			traceback.print_exc()
			return "0"
	def create_new_game(self,g):
		LOG("CNG! - " +g)
		try:
			return self.ohs.create_new_game(g)
		except Exception:
			traceback.print_exc()
			return "0"

ONLINEHIGHSCORE=SafeOnlineHighScores()

class SubmitDialog(xbmcgui.WindowDialog):
	def __init__(self,parent=None):
		noStretch(self)
		self.parent = parent
		x = self.parent.posX + 50
		y = self.parent.posY + 130
		imagedir = self.parent.imagedir
		self.addControl(xbmcgui.ControlImage(x,y,243,113, imagedir+'submit.png'))
		self.btnUsername = xbmcgui.ControlButton(x + 20, y+10, 100, 25, 'Username:', textOffsetY=3,focusTexture=imagedir+"button-focus.png",noFocusTexture=imagedir+"button-nofocus.png")
		self.btnPassword = xbmcgui.ControlButton(x + 20, y+40, 100, 25, 'Password:', textOffsetY=3,focusTexture=imagedir+"button-focus.png",noFocusTexture=imagedir+"button-nofocus.png")
		self.lblUsername = xbmcgui.ControlLabel(x+135, y+10+3, 100, 25, '')
		self.lblPassword = xbmcgui.ControlLabel(x+135, y+40+3, 100, 25, '')
		self.btnSubmit = xbmcgui.ControlButton(x+20, y+75, 100, 25, 'Submit',focusTexture=imagedir+"button-focus.png",noFocusTexture=imagedir+"button-nofocus.png")
		
		self.addControl(xbmcgui.ControlLabel(0,0,0,0,''))
		self.addControl(xbmcgui.ControlLabel(0,0,0,0,''))
		self.addControl(xbmcgui.ControlLabel(0,0,0,0,''))
		self.addControl(xbmcgui.ControlLabel(0,0,0,0,''))
		self.addControl(xbmcgui.ControlLabel(0,0,0,0,''))
		self.addControl(xbmcgui.ControlLabel(0,0,0,0,''))
		for control in (self.btnUsername, self.btnPassword, self.btnSubmit, self.lblUsername, self.lblPassword):
			self.addControl(control)
		
		self.btnUsername.controlUp(self.btnSubmit)
		self.btnPassword.controlUp(self.btnUsername)
		self.btnSubmit.controlUp(self.btnPassword)
		self.btnUsername.controlDown(self.btnPassword)
		self.btnPassword.controlDown(self.btnSubmit)
		self.btnSubmit.controlDown(self.btnUsername)
		self.setFocus(self.btnSubmit)
		
		self.username = ''
		self.password = ''
		self.userID = "0"
	
	def setUsername(self,username):
		self.username = username
		self.lblUsername.setLabel(username)
		self.userID = "0"
		
	def setPassword(self,password):
		self.password = password
		self.lblPassword.setLabel('*'*len(password))
		self.userID = "0"
	
	def promptUsername(self):
		self.setUsername(unikeyboard(self.username, 'Enter Username'))
	
	def promptPassword(self):
		if self.username == '':
			self.setPassword(unikeyboard(self.password, 'Enter Password'))
		else:
			self.setPassword(unikeyboard(self.password, 'Enter Password for ' + self.username))
		
	def getUserID(self,refresh=True):
		if not self.userID == "0" and not refresh:
			return self.userID
		if self.username == "":	self.promptUsername()
		if self.username == "": return "0"
		if self.password == "":	self.promptPassword()			
		if self.password == "":	return "0"			
			
		userID = ONLINEHIGHSCORE.get_user_id(self.username,self.password)
		LOG("GUID ID="+userID)
		if userID == "0":
			if xbmcgui.Dialog().yesno(self.parent.gamename, 'Account for username '+self.username+' not found', 'Create new account?'):
				userID = ONLINEHIGHSCORE.create_new_user(self.username, self.password)
		return userID
	
	def	submitScore(self,score):
		LOG("SS " + str(score) + '-'+str(self.userID))
		if self.userID == "0":
			self.userID = self.getUserID()
		LOG("SS2 " + self.userID)
		if self.userID == "0":
			LOG("SS2.1")
			return False
		retVal = ONLINEHIGHSCORE.insert_new_highscore(self.parent.gameID, self.userID, str(score))
		LOG("SS4 " + str(retVal))	
		return retVal
		
	def onControl(self, control):
		LOG('SD - OC1 - ' + str(control.getId()))
		if control == self.btnUsername:
			self.promptUsername()
		elif control == self.btnPassword:
			self.promptPassword()
		elif control == self.btnSubmit:
			if not self.submitScore(self.parent.score) == "0":
				xbmcgui.Dialog().ok(self.parent.gamename, 'Submission Successful!')
				self.close()
			else:
				xbmcgui.Dialog().ok(self.parent.gamename, 'Submission Failure')
			

	def onAction(self, action):
		if action in (ACTION_PREVIOUS_MENU, ACTION_PARENT_DIR, ACTION_STOP):
			self.close()			
		
	
class HighScoreDialog(xbmcgui.WindowDialog):
	def __init__(self,parent=None):
		noStretch(self)
		self.parent = parent
		self.posX = parent.posX -55
		self.posY = parent.posY + 30
		
		self.hsFileName = TETRIS_SCORES % self.parent.gamename
		self.localHighScores = self.loadLocalHighScores()
		self.onlineHighScores = []
		
		self.buildGui()
		self.currentTab = 0 #local
		self.populateList(self.localHighScores)
		
		
		
	def buildGui(self):
		self.addControl(xbmcgui.ControlImage(self.posX,self.posY,270,355, self.parent.imagedir+'highscore.png'))
		self.imgtabLocal = [
			xbmcgui.ControlImage(self.posX + 20, self.posY+9, 80, 32,self.parent.imagedir+'tab-noselect-nofocus.png'),
			xbmcgui.ControlImage(self.posX + 20, self.posY+9, 80, 32,self.parent.imagedir+'tab-noselect-focus.png'),
			xbmcgui.ControlImage(self.posX + 20, self.posY+9, 80, 32,self.parent.imagedir+'tab-select-nofocus.png'),
			xbmcgui.ControlImage(self.posX + 20, self.posY+9, 80, 32,self.parent.imagedir+'tab-select-focus.png')]
		self.imgtabOnline = [
			xbmcgui.ControlImage(self.posX + 80, self.posY+9, 80, 32,self.parent.imagedir+'tab-noselect-nofocus.png'),
			xbmcgui.ControlImage(self.posX + 80, self.posY+9, 80, 32,self.parent.imagedir+'tab-noselect-focus.png'),
			xbmcgui.ControlImage(self.posX + 80, self.posY+9, 80, 32,self.parent.imagedir+'tab-select-nofocus.png'),
			xbmcgui.ControlImage(self.posX + 80, self.posY+9, 80, 32,self.parent.imagedir+'tab-select-focus.png')]
		# This adds the textures so that the select textures are in front of the unselected textures... this way tabs can have a little overlap and it looks nicer
		for i in range(0,4):  
			self.addControl(self.imgtabLocal[i])
			self.imgtabLocal[i].setVisible(False)
			self.addControl(self.imgtabOnline[i])
			self.imgtabOnline[i].setVisible(False)
		self.addControl(xbmcgui.ControlImage(self.posX+5,self.posY+38,263,4, self.parent.imagedir+'seperator.png'))
		self.btnLocal = xbmcgui.ControlButton(self.posX + 20, self.posY+12, 70, 25, 'Local',focusTexture='',noFocusTexture='')
		self.btnOnline = xbmcgui.ControlButton(self.posX + 80, self.posY+12, 70, 25, 'Online',focusTexture='',noFocusTexture='')
		self.btnRefresh = xbmcgui.ControlButton(self.posX + 180, self.posY+10, 70, 25, 'Refresh',focusTexture=self.parent.imagedir+"button-focus.png",noFocusTexture=self.parent.imagedir+"button-nofocus.png")
		self.lstHighScores = xbmcgui.ControlList(self.posX +20, self.posY + 50, 230, 320)
		self.addControl(xbmcgui.ControlLabel(0,0,0,0,''))
		self.addControl(self.btnLocal)
		self.addControl(self.btnOnline)
		self.addControl(self.lstHighScores)
		self.addControl(self.btnRefresh)
		
		self.btnLocal.controlLeft(self.btnRefresh)
		self.btnRefresh.controlLeft(self.btnOnline)
		self.btnOnline.controlLeft(self.btnLocal)
		self.btnLocal.controlRight(self.btnOnline)
		self.btnRefresh.controlRight(self.btnLocal)
		self.btnOnline.controlRight(self.btnRefresh)
		#self.btnRefresh.setVisible(False)
		self.lstHighScores.setEnabled(False)
		self.btnRefresh.setEnabled(False)
		self.setFocus(self.btnLocal)
		self.imgtabLocal[3].setVisible(True)
		self.imgtabOnline[0].setVisible(True)
		
	def isHighScore(self,score):
		scores = [s[1] for s in self.localHighScore]
		scores.append(score)
		scores.sort()
		if scores.index(score) < self.maxScoreLength:
			return True
		return False
	
	def parseScores(self, data):
		LOG('Parsing data ')
		scores = []
		for line in data.split("\n"):
			nameScore = line.split("|")
			if len(nameScore) == 2:
				scores.append((nameScore[0],nameScore[1]))
		LOG("scores")
		LOG(scores)
		return scores
	
	def populateList(self,scores):
		LOG("PL setting to "+str(scores))
		xbmcgui.lock()
		self.updateTabImages()
		self.lstHighScores.reset()
		for name,score in scores:
			self.lstHighScores.addItem(xbmcgui.ListItem(name,str(score)))
		xbmcgui.unlock()
	
	def loadLocalHighScores(self):
		data = ''
		if os.path.exists(self.hsFileName):
			input = open(self.hsFileName,'r')
			data = input.read()
			input.close()		
		return self.parseScores(data)
		
	def loadOnlineHighScores(self):
		LOG("LOH")
		scores = self.parseScores(ONLINEHIGHSCORE.get_highscore(self.parent.gameID))
		LOG("LOH score: " + str(scores))
		return scores
	
	def replaceName(self, oldName, newName, score):
		try: idx = self.localHighScores.index((oldName,score))
		except: return False
		self.localHighScores[idx] = (newName,score)
		self.currentTab = 0
		self.populateList(self.localHighScores)
		return True
	
	def addScore(self,name,score):
	
		LOG('AS1 - ' + str(name) + '|'+str(score))
		self.localHighScores.append((name,score)) #add
		self.localHighScores.sort(key=lambda x: int(x[1]),reverse=True) #sort
		self.localHighScores = self.localHighScores[0:min(len(self.localHighScores),self.parent.maxScoreLength)] #truncate
		self.populateList(self.localHighScores)
		LOG('AS5')
		try:
			return self.localHighScores.index((name,score)) #return index or -1
		except Exception:
			return -1
	
	def getHighestScore(self):
		if len(self.localHighScores) > 0:
			return self.localHighScores[0]
		else:
			return ('-------','0')
	
	def saveHighScores(self):
		output = open(self.hsFileName,'w')
		LOG("Scores:" + str(self.localHighScores))
		scoreStrings = [str(x[0]) +"|"+str(x[1]) for x in self.localHighScores]
		output.write("\n".join(scoreStrings))
		output.close()
	
	def updateTabImages(self):
		LOG("UTI1")
		focusControl = self.getFocus()
		imgidx = [0,0]
		if focusControl == self.btnLocal:
			if self.currentTab == 0: imgidx = [3,0]
			else: imgidx = [1,2]
		elif focusControl == self.btnOnline:
			if self.currentTab == 1: imgidx = [0,3]
			else: imgidx = [2,1]		
		else:
			if self.currentTab == 0: imgidx = [2,0]
			else: imgidx = [0,2]
		LOG("UTI2 " + str(imgidx))
		for i in range(4):
			self.imgtabLocal[i].setVisible(i==imgidx[0])
			self.imgtabOnline[i].setVisible(i==imgidx[1])
		
	def onControl(self, control):
		LOG('HS - OC1 - ' + str(control.getId()))
		if control == self.btnLocal:
			self.currentTab = 0
			self.populateList(self.localHighScores)
			#self.btnRefresh.setVisible(False)
			self.btnRefresh.setEnabled(False)
		LOG('HS - OC2')
		if control == self.btnOnline:
			if len(self.onlineHighScores) == 0:
				LOG('HS - OC2.1')
				self.onlineHighScores = self.loadOnlineHighScores()
			LOG('HS - OC2.2')
			self.currentTab = 1
			self.populateList(self.onlineHighScores)
			#self.btnRefresh.setVisible(True)
			self.btnRefresh.setEnabled(True)
		LOG('HS - OC3')
		if control == self.btnRefresh:
			self.currentTab = 1
			self.onlineHighScores = self.loadOnlineHighScores()
			self.populateList(self.onlineHighScores)
		LOG('HS - OC4')
	
	def onAction(self, action):
		self.updateTabImages()
		LOG('HS - OA1')
		if action in (ACTION_PREVIOUS_MENU, ACTION_PARENT_DIR, ACTION_STOP):
			self.close()
	
WINDOW_NONE = 0
WINDOW_GAME = 3
WINDOW_HIGHSCORE = 1
WINDOW_SUBMIT = 2
class GameDialog(xbmcgui.WindowDialog):
	def __init__(self, gamename='',x=100,y=100, imagedir='', maxScoreLength=10):
		noStretch(self)
		self.posX = x
		self.posY = y
		# I had a problem with different window dialogs having duplicate  ControlIDs
		# This generated two differen onControl events,  use self.focusWindow as a lock
		self.focusWindow = WINDOW_GAME 
		self.imagedir = imagedir
		self.score = "0"
		self.buildGui()
		self.gamename = gamename
		self.gameID = ''
		LOG("init gameID is " + str(self.gameID))
		self.maxScoreLength = maxScoreLength
		self.retVal = True
		
		self.username = ''
		self.dlgSubmit = SubmitDialog(parent=self)
		self.dlgHighScores = HighScoreDialog(parent=self)
		
	def buildGui(self):
		self.addControl(xbmcgui.ControlImage(self.posX,self.posY,270,150, self.imagedir+'panel.png'))
		self.btnUsername = xbmcgui.ControlButton(self.posX + 20, self.posY+10, 100, 25, 'Name:', textOffsetX=10, textOffsetY=3,focusTexture=self.imagedir+"button-focus.png",noFocusTexture=self.imagedir+"button-nofocus.png")
		self.lblUsername = xbmcgui.ControlLabel(self.posX+140, self.posY+13, 100, 25, '')
		self.lblScore	= xbmcgui.ControlLabel(self.posX+140, self.posY+40, 100, 25, '0')
		self.addControl(xbmcgui.ControlLabel(self.posX+30, self.posY+40, 100, 25, 'Score:'))
		self.btnNewGame = xbmcgui.ControlButton(self.posX + 20, self.posY+75, 100, 25, 'Play Again',textOffsetX=10, textOffsetY=3,focusTexture=self.imagedir+"button-focus.png",noFocusTexture=self.imagedir+"button-nofocus.png")
		self.btnHighScores = xbmcgui.ControlButton(self.posX + 130, self.posY+75, 120, 25, 'High Scores',textOffsetX=10, textOffsetY=3,focusTexture=self.imagedir+"button-focus.png",noFocusTexture=self.imagedir+"button-nofocus.png")
		self.btnSubmit = xbmcgui.ControlButton(self.posX + 130, self.posY+105, 120, 25, 'Submit Online',textOffsetX=10, textOffsetY=3,focusTexture=self.imagedir+"button-focus.png",noFocusTexture=self.imagedir+"button-nofocus.png")
		self.btnQuit = xbmcgui.ControlButton(self.posX + 20, self.posY+105, 100, 25, 'Quit',textOffsetX=10, textOffsetY=3,focusTexture=self.imagedir+"button-focus.png",noFocusTexture=self.imagedir+"button-nofocus.png")
		for control in (self.btnNewGame, self.btnHighScores, self.btnQuit, self.btnSubmit, self.btnUsername, self.lblUsername, self.lblScore):
			self.addControl(control)
		self.btnNewGame.setNavigation(self.btnUsername, self.btnQuit, self.btnHighScores, self.btnHighScores)
		self.btnHighScores.setNavigation(self.btnUsername, self.btnSubmit, self.btnNewGame, self.btnNewGame)
		self.btnQuit.setNavigation(self.btnNewGame, self.btnUsername, self.btnSubmit, self.btnSubmit)
		self.btnSubmit.setNavigation(self.btnHighScores, self.btnUsername, self.btnQuit, self.btnQuit)
		self.btnUsername.controlDown(self.btnNewGame)
		self.setFocus(self.btnNewGame)
		
	def showDialog(self,score):
		LOG("Show Dialog")
		self.score = str(score)
		self.lblScore.setLabel(str(score))
		while self.username == '':
			self.setUsername(unikeyboard(self.username, "Enter New Player Name"))
			if self.dlgSubmit.username == '':
				self.dlgSubmit.setUsername(self.username)
		self.dlgHighScores.addScore(self.username,str(score))
		self.gameID = self.getGameID(self.gamename)
		#xbmc.enableNavSounds(True)
		self.focusWindow = WINDOW_GAME
		self.doModal() #leaves xbmcgui locked
		#xbmc.enableNavSounds(False)
		LOG("SD7")
		self.dlgHighScores.saveHighScores()
		xbmcgui.unlock()
		LOG("SD8")
		return self.retVal
		
		
		
	def getGameID(self,gamename):
		LOG('gGID ' +self.gameID)
		if self.gameID == '':
			self.gameID = ONLINEHIGHSCORE.get_game_id(gamename)		
		if self.gameID == "0":
			LOG("game not found");
			self.gameID = ONLINEHIGHSCORE.create_new_game(gamename)
		return self.gameID

		
	def setUsername(self,username):
		self.username = username
		self.lblUsername.setLabel(username)
	
	def onControl(self, control):
		if not self.focusWindow == WINDOW_GAME:
			return
		LOG('OC1 - ' + str(control.getId()))
		if control == self.btnUsername:
			oldname = self.username
			self.setUsername(unikeyboard(self.username, "Enter New Name"))
			self.dlgHighScores.replaceName(oldname, self.username, self.score)
			if self.dlgSubmit.username == '':
				self.dlgSubmit.setUsername(self.username)
		LOG('OC2')
		if control == self.btnNewGame:
			LOG('OC2.3')
			self.retVal = True
			xbmcgui.lock()
			self.close()
		LOG('OC3')
		if control == self.btnQuit:
			self.retVal = False
			xbmcgui.lock()
			self.close()
		LOG('OC4')
		if control == self.btnSubmit:
			self.focusWindow = WINDOW_SUBMIT
			self.dlgSubmit.doModal()
			self.focusWindow = WINDOW_GAME
		LOG('OC5')
		if control == self.btnHighScores:
			self.focusWindow = WINDOW_HIGHSCORE
			self.dlgHighScores.doModal()
			self.focusWindow = WINDOW_GAME
		LOG('OC6')

	def onAction(self, action):
		if not self.focusWindow == WINDOW_GAME:
			return
		if action in (ACTION_PREVIOUS_MENU, ACTION_PARENT_DIR, ACTION_STOP):
			self.focusWindow = WINDOW_NONE
			self.close()