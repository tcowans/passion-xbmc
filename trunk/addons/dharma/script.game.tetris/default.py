###################################################################
#
#   Tetris v1.0a
#		by asteron  
#
#	
###################################################################

__addonID__ = "script.game.tetris"

import re, random, math, threading, time
import xbmc, xbmcgui
import threading, os, re
import scores

SPECIAL_PROFILE_DIR = xbmc.translatePath( "special://profile/" )
SPECIAL_SCRIPT_DATA = os.path.join( SPECIAL_PROFILE_DIR, "addon_data", __addonID__ )
if not os.path.isdir( SPECIAL_SCRIPT_DATA ): os.makedirs( SPECIAL_SCRIPT_DATA )
TETRIS_SETTINGS = os.path.join( SPECIAL_SCRIPT_DATA, "tetris_settings.xml" )

ACTION_MOVE_LEFT 	= 1	
ACTION_MOVE_RIGHT	= 2
ACTION_MOVE_UP		= 3
ACTION_MOVE_DOWN	= 4
ACTION_PAGE_UP		= 5
ACTION_PAGE_DOWN	= 6
ACTION_SELECT_ITEM      = 7
ACTION_HIGHLIGHT_ITEM	= 8
ACTION_PARENT_DIR	= 9
ACTION_PREVIOUS_MENU	= 10
ACTION_SHOW_INFO	= 11
ACTION_PAUSE		= 12
ACTION_STOP		= 13
ACTION_NEXT_ITEM	= 14
ACTION_PREV_ITEM	= 15
ACTION_SHOW_GUI = 18  #X Button
ACTION_QUEUE_ITEM = 34
ACTION_SCROLL_UP	= 111
ACTION_SCROLL_DOWN	= 112

KEY_BUTTON_A                        = 256
KEY_BUTTON_B                        = 257
KEY_BUTTON_X                        = 258
KEY_BUTTON_Y                        = 259
KEY_BUTTON_BLACK                    = 260
KEY_BUTTON_WHITE                    = 261
KEY_BUTTON_LEFT_TRIGGER             = 262
KEY_BUTTON_RIGHT_TRIGGER            = 263
KEY_BUTTON_LEFT_THUMB_STICK         = 264
KEY_BUTTON_RIGHT_THUMB_STICK        = 265
KEY_BUTTON_RIGHT_THUMB_STICK_UP     = 266 # right thumb stick directions
KEY_BUTTON_RIGHT_THUMB_STICK_DOWN   = 267 # for defining different actions per direction
KEY_BUTTON_RIGHT_THUMB_STICK_LEFT   = 268
KEY_BUTTON_RIGHT_THUMB_STICK_RIGHT  = 269
KEY_BUTTON_DPAD_UP                  = 270
KEY_BUTTON_DPAD_DOWN                = 271
KEY_BUTTON_DPAD_LEFT                = 272
KEY_BUTTON_DPAD_RIGHT               = 273
KEY_BUTTON_START                    = 274
KEY_BUTTON_BACK                     = 275
KEY_BUTTON_LEFT_THUMB_BUTTON        = 276
KEY_BUTTON_RIGHT_THUMB_BUTTON       = 277
KEY_BUTTON_LEFT_ANALOG_TRIGGER      = 278
KEY_BUTTON_RIGHT_ANALOG_TRIGGER     = 279
KEY_BUTTON_LEFT_THUMB_STICK_UP      = 280 # left thumb stick  directions
KEY_BUTTON_LEFT_THUMB_STICK_DOWN    = 281 # for defining different actions per direction
KEY_BUTTON_LEFT_THUMB_STICK_LEFT    = 282
KEY_BUTTON_LEFT_THUMB_STICK_RIGHT   = 283


XBFONT_LEFT       = 0x00000000
XBFONT_RIGHT      = 0x00000001
XBFONT_CENTER_X   = 0x00000002
XBFONT_CENTER_Y   = 0x00000004
XBFONT_TRUNCATED  = 0x00000008

COORD_1080I      = 0 
COORD_720P       = 1 
COORD_480P_4X3   = 2 
COORD_480P_16X9  = 3 
COORD_NTSC_4X3   = 4 
COORD_NTSC_16X9  = 5 
COORD_PAL_4X3    = 6 
COORD_PAL_16X9   = 7 
COORD_PAL60_4X3  = 8 
COORD_PAL60_16X9 = 9 

ROOT_DIR = os.getcwd()+'\\'    
IMAGE_DIR = ROOT_DIR+"images\\"
SOUND_DIR = ROOT_DIR+"sounds\\"

MAX_LENGTH 		= 4
COLOR_NONE 		= 0
COLOR_BLUE 		= 1
COLOR_RED 		= 2
COLOR_GREEN 	= 3
COLOR_YELLOW 	= 4
COLOR_CYAN 		= 5
COLOR_MAGENTA 	= 6
COLOR_ORANGE 	= 7
COLOR_GHOST 	= 8
COLORS = ['none','blu','red','gre','yel','cya','mag','ora','ghost']

DO_LOGGING = 0
try:
	LOG_FILE.close()
except Exception:
	pass
if DO_LOGGING:
	LOG_FILE = open(ROOT_DIR+"log.txt",'w')
def LOG(message):
	if DO_LOGGING:
		LOG_FILE.write(str(message)+"\n")
		LOG_FILE.flush()	
def LOGCLOSE():
	if DO_LOGGING:
		LOG_FILE.close()

class PieceType:
	def __init__(self,squares,symmetry,color): 
		self.squares = squares
		self.size = int(math.sqrt(len(squares)))
		self.symmetry = symmetry
		self.color = color
		self.masks = [[squares[i*self.size:(i+1)*self.size] for i in range(self.size)]]
		for k in range(self.symmetry-1):
			self.masks.append([squares[i*self.size:(i+1)*self.size] for i in range(self.size)])
			for i in range(self.size):
				for j in range(self.size):
					self.masks[-1][i][j] = self.masks[-2][j][-1-i]
		
#		print '\n\n'.join(['\n'.join([''.join([str(x) for x in row]) for row in mask]) for mask in self.masks])+'\n\n\n'
PIECETYPE = [
		 	PieceType([	0,0,1,0,
						0,0,1,0,
						0,0,1,0,
						0,0,1,0],2,COLOR_RED),
		  
		 	PieceType([	0,1,0,
						1,1,0,
						0,1,0],4,COLOR_ORANGE),
		  
		 	PieceType([	1,1,0,
						0,1,1,
						0,0,0],2,COLOR_CYAN),
		  
		 	PieceType([	0,1,1,
						1,1,0,
						0,0,0],2,COLOR_GREEN),
		  		  
		 	PieceType([	1,1,0,
						0,1,0,
						0,1,0],4,COLOR_MAGENTA),
		  
		 	PieceType([	0,1,1,
						0,1,0,
						0,1,0],4,COLOR_YELLOW),
		 	
		 	PieceType([	1,1,
						1,1],1,COLOR_BLUE),
		 ]
		 
class Piece:
	def __init__(self,type):
		self.type = type
		self.color = type.color
		self.y = 0
		self.x = 0
		self.rotation = 0
	
	def getCollisionMask(self,rotation):
		return self.type.masks[rotation]
		
class Board:
	def __init__(self,width,height):
		self.width = width
		self.height = height
		self.blocks = []
		for i in range(self.height):
			self.blocks.append([COLOR_NONE]*self.width)

	def clear(self):
		LOG('Clear')
		self.blocks = []
		for i in range(self.height):
			self.blocks.append([COLOR_NONE]*self.width)

	def isCollision(self,piece,x,y,rotation):
		collisionMask = piece.getCollisionMask(rotation)
		for i in range(len(collisionMask[0])):
			for j in range(len(collisionMask)):
				if collisionMask[i][j]:
					if i+y < 0 or i+y >= self.height or j+x < 0 or j+x >= self.width:
						return True  #collided with wall
					if self.blocks[i+y][j+x]:
						return True  #collided with block
		return False
	
	def addPiece(self,piece):
		mask = piece.getCollisionMask(piece.rotation)
		for i in range(len(mask[0])):
			for j in range(len(mask)):
				if mask[i][j]:
					self.blocks[i+piece.y][j+piece.x] = piece.type.color
	
	def deleteRow(self,row):
		for i in range(row,0,-1):
			self.blocks[i] = self.blocks[i-1][:]
		self.blocks[0] = [0]*self.width

	def isRowFilled(self,row):
		return reduce(lambda x,y: x and y, self.blocks[row], True)
				
	
	def printBoard(self):
		print '\n'.join([''.join([str(x) for x in row]) for row in self.blocks])

class BoardController:
	def __init__(self, board):
		self.nLines = 0
		self.nPieceCount = [0]*len(PIECETYPE)
		self.nScore = 0
		self.nLevel = 1
		self.board = board
		self.nextPiece = Piece(PIECETYPE[random.randint(0,len(PIECETYPE)-1)])
		self.curPiece = Piece(PIECETYPE[random.randint(0,len(PIECETYPE)-1)])
		self.doNewPiece()

#	returns whether number 
	def dropPiece(self):
		LOG('DropPiece')
		if not self.board.isCollision(self.curPiece,self.curPiece.x,self.curPiece.y+1,self.curPiece.rotation):
			LOG('DP1')
			self.curPiece.y = self.curPiece.y + 1
			return EVENT_DROP,0
		else:
			LOG('DP2')
			self.board.addPiece(self.curPiece)
			self.nPieceCount[PIECETYPE.index(self.curPiece.type)] += 1
			rows = self.checkBoard()
			#gamestate = self.doNewPiece()
			self.nScore += self.nLevel * rows * rows
			if self.nLines >= 15*self.nLevel:
				self.nLevel += 1
				self.nScore += 15 * self.nLevel
				return EVENT_LEVEL_UP,rows
			LOG('DP3')
			return EVENT_NEW_PIECE,rows
			
	
	def checkBoard(self):
		LOG('  CheckBoard->')
		rows = 0
		for row in range(self.board.height):
			if board.isRowFilled(row):
				board.deleteRow(row)
				self.nLines += 1
				rows += 1
		LOG('  CheckBoard<-' + str(rows))
		return rows
		
	def movePiece(self,dx):
		if not self.board.isCollision(self.curPiece,self.curPiece.x+dx,self.curPiece.y,self.curPiece.rotation):
			self.curPiece.x = self.curPiece.x + dx
		return EVENT_MOVE

	def rotatePiece(self,dr):
		if not self.board.isCollision(self.curPiece,self.curPiece.x,self.curPiece.y,(self.curPiece.rotation + dr) % self.curPiece.type.symmetry):
			self.curPiece.rotation = (self.curPiece.rotation + dr) % self.curPiece.type.symmetry
		return EVENT_ROTATE
	
	def quickDrop(self, fromGround=2):
		while not self.board.isCollision(self.curPiece,self.curPiece.x,self.curPiece.y+fromGround+1,self.curPiece.rotation):
			self.dropPiece()
		return self.dropPiece()
	
	def getDroppedPieceCopy(self):
		copyPiece = Piece(self.curPiece.type)
		copyPiece.x,copyPiece.y,copyPiece.rotation = self.curPiece.x,self.curPiece.y,self.curPiece.rotation
		while not self.board.isCollision(copyPiece,copyPiece.x,copyPiece.y+1,copyPiece.rotation):
			copyPiece.y += 1
		copyPiece.color = COLOR_GHOST
		return copyPiece

	def doNewPiece(self):
		LOG('DN')
		self.curPiece = self.nextPiece
		self.curPiece.x = self.board.width/2 - self.curPiece.type.size / 2
		self.nextPiece = Piece(PIECETYPE[random.randint(0,len(PIECETYPE)-1)])
		if self.board.isCollision(self.curPiece,self.curPiece.x,self.curPiece.y,self.curPiece.rotation):
			LOG('DN2')
			self.gameOver()
			return EVENT_GAME_OVER
		return EVENT_NEW_PIECE

	def gameOver(self):
		LOG('GameOver')
		#self.newGame()

	def newGame(self):
		self.nLines = 0
		self.nLevel = 1
		self.nScore = 0	
		LOG('NewGame')
		self.board.clear()
		LOG('NG2')
		self.doNewPiece();
		self.doNewPiece();
		self.nPieceCount = [0]*len(PIECETYPE)
		

EVENT_NONE = 0
EVENT_NEW_PIECE = 1
EVENT_GAME_OVER = 2
EVENT_NEW_GAME = 3
EVENT_LEVEL_UP = 4
EVENT_MOVE = 5
EVENT_ROTATE = 6
EVENT_DROP = 7

GRAVITY_SPEED_DELAY = 4
GRAVITY_NEW_PIECE_DELAY = 0.4

STATE_READY = 0
STATE_PAUSED = 1
STATE_QUITTING = 2

#avoid stretching on different pixel aspect ratios
def noStretch(window):
	if window.getResolution() < 2: window.setCoordinateResolution(COORD_720P)
	else: window.setCoordinateResolution(COORD_PAL_4X3)

class PauseDialog(xbmcgui.WindowDialog):
	def __init__(self,parent=None):
		noStretch(self)
		self.parent = parent
		self.addControl(xbmcgui.ControlImage(parent.blockX-20,parent.blockY+70,213,113, IMAGE_DIR+'pause.png'))
		self.addControl(xbmcgui.ControlLabel(parent.blockX+10,parent.blockY+10, 100,25,"High Score:",'font14','FFFFFF00'))
		self.lblHighScoreName = xbmcgui.ControlLabel(parent.blockX+30,parent.blockY+29, 100,25,"Asteron",'font14','FFFFFFFF')
		self.lblHighScore = xbmcgui.ControlLabel(parent.blockX+170,parent.blockY+27, 100,25,"00000",'font14','FFFFFFFF',alignment=XBFONT_RIGHT)
		self.chkGhostPiece = xbmcgui.ControlCheckMark(parent.blockX+25,parent.blockY+230, 100,25,"Ghost Piece",font='font14',focusTexture=IMAGE_DIR+"check-box.png",noFocusTexture=IMAGE_DIR+"check-box-nofocus.png",checkWidth=24,checkHeight=24)
		self.addControl(self.lblHighScoreName)
		self.addControl(self.lblHighScore)
		self.addControl(self.chkGhostPiece)
		self.setFocus(self.chkGhostPiece)
	
	def onControl(self,control):
		LOG("PW - Oc -->")
		if control == self.chkGhostPiece:
			self.parent.drawGhostPiece = self.chkGhostPiece.getSelected()
		LOG("PW - Oc <--")
	
	def onAction(self, action):
		LOG("PW - OA")
		if action in (ACTION_PREVIOUS_MENU, ACTION_PAUSE) or action.getButtonCode() == KEY_BUTTON_START:
			xbmcgui.lock()
			self.close()

class Tetris(xbmcgui.WindowDialog):
	def __init__(self):
		noStretch(self)
		self.blockSize = 17
		self.spacing = 3
		self.blockX = 400
		self.blockY = 70
		self.drawGhostPiece = False
		self.dlgPause = PauseDialog(parent=self)
		self.dlgGame= scores.GameDialog(gamename='Tetris',imagedir=IMAGE_DIR,x=self.blockX -20, y=self.blockY)
		self.gravityControl = 0 # 0 = let fall, 1 = wait to fall, >1 = new piece take a break
		self.gravityDelay = time.clock() 
		self.state = STATE_READY
		
		self.addControl(xbmcgui.ControlImage(self.blockX-111,self.blockY-20,320,445, IMAGE_DIR+'background.png'))
		self.imgBlocks = []
		self.imgPiece = []
		self.imgNextPiece = []
		self.imgGhostPiece = []
		self.mutex = True
		self.pendingAction = None
		self.timer = True
		self.renderPieces()
		self.renderLabels()
		
		
	def setController(self,controller):
		LOG('SC')
		self.controller = controller
		self.board = controller.board
		self.updatePiece()
		
	def drawBloom(self,msg,x,y,duration=45,font='font12'):
		def SubProc(window,msg,x,y,duration,font):
			LOG("dsb 3a")
			lbl = xbmcgui.ControlLabel(x,y,200,25,msg,font)
			window.addControl(lbl)
			amp = random.uniform(2,6)
			if random.randint(0,1): amp = -amp
			freq = random.uniform(8,15)
			offset = random.uniform(0,3)
			for i in range(0,duration):
				lock.acquire()
				if window.state == STATE_QUITTING:
					lock.release()
					return
				lbl.setPosition(x+int(amp*math.sin((offset+float(i))/freq)),y-i)
				lock.release()
				time.sleep(.016)
			window.removeControl(lbl)
		
		LOG("dsb 1 " + str(msg) + "-"+str(x)+"-"+str(y))
		screenx = self.blockX + (self.blockSize + self.spacing)*x + 10
		screeny = self.blockY + (self.blockSize + self.spacing)*y
		LOG("dsb 2")

		thread = threading.Thread(target=SubProc, args=(self,msg,screenx,screeny,duration,font))
		thread.setDaemon(True)
		thread.start()


	def startTimer(self):
		LOG('Start Timer')
		self.timer = True

		def timerProc(view,controller,delay):
			sleeptime = max(delay * (0.6**(controller.nLevel-1)),0.05)
			time.sleep(sleeptime)		
			while view.timer and not view.state == STATE_QUITTING:
				if not view.state == STATE_PAUSED:
					LOG('-> TIMER attempting lock')
					lock.acquire()
					LOG('   TIMER lock acquired!')
					event,rows = controller.dropPiece()
					view.processEvent(event,rows)
					LOG('   TIMER: LOCK released!')
					lock.release()
				sleeptime = max(delay * (0.6**(controller.nLevel-1)),0.05)
				time.sleep(sleeptime)
			
		self.subThread = threading.Thread(target=timerProc, args=(self,self.controller,1.50))
		self.subThread.setDaemon(True)
		self.subThread.start()
	
	def stopTimer(self):
		LOG('ST: Killing Timer '+ str(self.subThread))
		self.timer = False
		self.subThread.join()
		LOG('ST: Thread joined')


	def renderPieces(self):
		for i in range(len(PIECETYPE)):
			piece = Piece(PIECETYPE[i])
			piece.rotation = (1,3,0,0,3,1,0)[i]
			self.rasterPiece(piece,self.blockX-50-12*(PIECETYPE[i].size),self.blockY+130+40*i,2,10)
 
	def renderLabels(self):
		x = self.blockX - 100
		y = self.blockY + 60
		self.addControl(xbmcgui.ControlLabel(x,y,455,20,'Lines:','font12','FFFFFF00'))
		self.lblLines   = xbmcgui.ControlLabel(x+80,y,40,20,'','font12','FFFFFFFF',alignment=XBFONT_RIGHT)
		self.addControl(self.lblLines)
		self.addControl(xbmcgui.ControlLabel(x,y+20,455,20,'Score:','font12','FFFFFF00'))
		self.lblScore   = xbmcgui.ControlLabel(x+80,y+20,40,20,'','font12','FFFFFFFF',alignment=XBFONT_RIGHT)
		self.addControl(self.lblScore)
		self.addControl(xbmcgui.ControlLabel(x,y+40,455,20,'Level:','font12','FFFFFF00'))
		self.lblLevel   = xbmcgui.ControlLabel(x+80,y+40,40,20,'','font12','FFFFFFFF',alignment=XBFONT_RIGHT)
		self.addControl(self.lblLevel)
		self.lblPieceCount = []
		for i in range(len(PIECETYPE)):
			self.lblPieceCount.append(xbmcgui.ControlLabel(x+80,self.blockY+130+40*i,40,20,'','font12','FFFFFFFF',alignment=XBFONT_RIGHT))
			self.addControl(self.lblPieceCount[-1])
			
 	
	def updateBlocks(self):
 		LOG('-> UB' + str(len(self.imgBlocks)))
		for i in self.imgBlocks:
			self.removeControl(i)
		self.imgBlocks = []
 		for i in range(self.board.height):
 			for j in range(self.board.width):
 				if self.board.blocks[i][j]:
 					LOG('UB3')
 					self.imgBlocks.append(self.blockImage(i,j,self.board.blocks[i][j],self.blockX,self.blockY,self.spacing,self.blockSize))
 					self.addControl(self.imgBlocks[-1])
 		LOG('<- UB4')

	def removeBlocks(self, blocks):
		for img in blocks:
 			self.removeControl(img)
 		
 	def updatePiece(self):
 		LOG('-> Update Piece')
		self.removeBlocks(self.imgGhostPiece)	
		self.imgGhostPiece = []
		if self.drawGhostPiece:
			self.imgGhostPiece = self.rasterPiece(self.controller.getDroppedPieceCopy(),self.blockX,self.blockY,self.spacing,self.blockSize)
		self.removeBlocks(self.imgPiece)
		self.imgPiece = self.rasterPiece(self.controller.curPiece,self.blockX,self.blockY,self.spacing,self.blockSize)

		self.removeBlocks(self.imgNextPiece)
		self.imgNextPiece = self.rasterPiece(self.controller.nextPiece,
			self.blockX-40-self.controller.nextPiece.type.size*12,self.blockY+18-self.controller.nextPiece.type.size*6,2,10)
			
		self.lblLines.setLabel(str(self.controller.nLines))
		self.lblScore.setLabel(str(self.controller.nScore))
		self.lblLevel.setLabel(str(self.controller.nLevel))
		for i in range(len(PIECETYPE)):
			self.lblPieceCount[i].setLabel(str(self.controller.nPieceCount[i]))
 		LOG('<- Update Piece')
 		

	def rasterPiece(self,piece,blockX,blockY,spacing,size):
		LOG('RasterPiece ->')
		mask = piece.getCollisionMask(piece.rotation)
		imgRaster = []
 		for i in range(len(mask)):
 			for j in range(len(mask[0])):
 				if mask[i][j]:
 					imgRaster.append(self.blockImage(i+piece.y,j+piece.x,piece.color,blockX,blockY,spacing,size))
 					self.addControl(imgRaster[-1])
 		return imgRaster
 		LOG('RasterPiece <-')
		

 	def blockImage(self,i,j,color,blockX,blockY,spacing,size):
 		return xbmcgui.ControlImage(blockX + (size + spacing)*j, blockY + (size + spacing)*i,
									size, size, IMAGE_DIR+"block_"+COLORS[color]+'.jpg')

	def processEvent(self,event,rows):
		xbmcgui.lock()
		LOG('ProcessEvent-> ' + str(event)+ ' ' + str(rows))
		self.updatePiece()
		entryEvent = event
		clearLev = bloomX = bloomY = 0
		if event == EVENT_NEW_PIECE or event == EVENT_LEVEL_UP:
			if rows>0 or True:
				clearLev = self.controller.nLevel - (event == EVENT_LEVEL_UP)
				bloomX = self.controller.curPiece.x+self.controller.curPiece.type.size/2 -1
				bloomY = self.controller.curPiece.y
			self.imgBlocks.extend(self.imgPiece)
			self.imgPiece = []
			event = self.controller.doNewPiece()
			self.updatePiece()
		if event == EVENT_GAME_OVER:      #sound priority
			self.state = STATE_PAUSED
			xbmc.playSFX(SOUND_DIR+"gameover.wav")
			xbmcgui.unlock()
			doNewGame = self.dlgGame.showDialog(self.controller.nScore) #it unlocks and locks gui
			xbmcgui.lock()
			if doNewGame:
				self.state = STATE_READY
				self.controller.newGame()
				self.updateBlocks()
				self.updatePiece()
			else:
				self.state = STATE_QUITTING
				self.close()
			LOG('PE after GO - '+str(self.state))
		elif entryEvent == EVENT_LEVEL_UP:
			xbmc.playSFX(SOUND_DIR+"levelup.wav")
			self.updateBlocks()
			self.drawBloom("+"+str(rows*rows*clearLev),bloomX,bloomY)
			self.drawBloom("Level Up! +"+str(self.controller.nLevel*15),-1,5,font="font14",duration=90)
		elif rows > 0:
			xbmc.playSFX(SOUND_DIR+"clear"+str(rows)+".wav")
			self.updateBlocks()
			self.drawBloom("+"+str(rows*rows*clearLev),bloomX,bloomY)
		elif entryEvent == EVENT_NEW_PIECE:
			xbmc.playSFX(SOUND_DIR+"lock.wav")
		elif entryEvent == EVENT_MOVE:
			xbmc.playSFX(SOUND_DIR+"move.wav")
		elif entryEvent == EVENT_ROTATE:
			xbmc.playSFX(SOUND_DIR+"rotate.wav")
		elif entryEvent == EVENT_DROP:
			xbmc.playSFX(SOUND_DIR+"drop.wav")
		LOG('ProcessEvent<-')
		xbmcgui.unlock()

	def togglePause(self):
		xbmcgui.lock()
		self.removeBlocks(self.imgBlocks + self.imgPiece + self.imgNextPiece + self.imgGhostPiece)
		xbmcgui.unlock()		
		self.state = STATE_PAUSED
		xbmc.playSFX(SOUND_DIR+"pause.wav")		
		name,score = self.dlgGame.dlgHighScores.getHighestScore()
		self.dlgPause.lblHighScore.setLabel(score)
		self.dlgPause.lblHighScoreName.setLabel(name)
		self.dlgPause.doModal() #leaves gui locked
		xbmc.playSFX(SOUND_DIR+"unpause.wav")
		self.state = STATE_READY
		for img in (self.imgBlocks + self.imgPiece + self.imgNextPiece + self.imgGhostPiece):
			self.addControl(img)
		xbmcgui.unlock()
		
	# I had huge freezing problems with the incoming thread not being able to wait properly on a lock.  XBMC really want the
	# thread to return quickly so we spawn a child thread immediately
	def onAction(self, action):
		def SubProc(view,action):
			view.onActionProc(action)

		# The scroll actions have a very high freq
		# decrease this frequency so we dont get bogged down with extra threads		
		if action == ACTION_SCROLL_DOWN or action == ACTION_SCROLL_UP:  
			if time.clock() < self.gravityDelay: 
				return
			else: 
				# this slows down the frequency			
				self.gravityControl = (1 + self.gravityControl) % GRAVITY_SPEED_DELAY 
				if not self.gravityControl == 0:
					return
		
		thread = threading.Thread(target=SubProc, args=(self,action))
		thread.setDaemon(True)
		thread.start()

	def onActionProc(self, action):
		lock.acquire()
		if self.state == STATE_QUITTING or self.state == STATE_PAUSED:
			lock.release()
			return

		LOG('   OnAct lock acquired!!')
		event = 0
		rows = 0
	 	if action == ACTION_MOVE_LEFT:
	 		event = controller.movePiece(-1)
	 	elif action == ACTION_MOVE_RIGHT:
	 		event = controller.movePiece(1)
	 	elif action == ACTION_MOVE_UP:
	 		event,rows = controller.quickDrop(fromGround=2)
	 		if event == EVENT_DROP:
	 			event = EVENT_MOVE
	 	elif action == ACTION_MOVE_DOWN or action == ACTION_SELECT_ITEM:
	 		event,rows = controller.quickDrop(fromGround=0)
	 	elif action in [ACTION_QUEUE_ITEM, ACTION_SHOW_GUI]:
			event = controller.rotatePiece(1)
	  	elif action == ACTION_PARENT_DIR:
			event = controller.rotatePiece(-1)
		elif action == ACTION_SCROLL_DOWN:
			event,rows = controller.dropPiece()
			# give it a break after you hit bottom
			if event == EVENT_NEW_PIECE or event == EVENT_LEVEL_UP:
				# if we hit the ground give gravity a break for a bit 			
				self.gravityDelay = time.clock() + GRAVITY_NEW_PIECE_DELAY
		elif action == ACTION_PAUSE or action.getButtonCode() == KEY_BUTTON_START:
	 		self.togglePause()
		elif action == ACTION_PREVIOUS_MENU:
			LOG('OA2: lock released')
			self.state = STATE_QUITTING
			self.close()
			lock.release()
			return
		LOG('OA2')
		self.processEvent(event,rows)
		LOG('OA: lock released')
		lock.release()
		LOG('<- OnAction')

			
	def saveSettings(self):
		dict = {"username":self.dlgGame.dlgSubmit.username,
				"password":self.dlgGame.dlgSubmit.password,
				"userid":self.dlgGame.dlgSubmit.userID,
				"nickname":self.dlgGame.username,
				"gameid":self.dlgGame.gameID,
				"ghost":(self.drawGhostPiece and "True") or "False"  # like ? : operator
				}
		curdat = "<tetris>\n" + "\n".join(["\t<"+key+">"+dict[key]+"</"+key+">" for key in dict.keys()])+ "\n</tetris>"
		LOG("Save settings : " + curdat)
		fb = open(TETRIS_SETTINGS,'w')
		fb.write(curdat)
		fb.close()
	
	def loadSettings(self):
		if not os.path.exists(TETRIS_SETTINGS):
			return
		fb = open(TETRIS_SETTINGS,'r')
		indat = fb.read()
		fb.close()
		LOG("LoadSettings: reading" + indat)
		regp = '<([^<]*)>([^</]*)</'
		save_info = re.compile(regp,re.IGNORECASE).findall(indat)
		dict = {"username":'',"password":'',"userid":'',"nickname":'',"gameid":'',"ghost":'False'}
		for x in save_info:
			dict[x[0]] = x[1]
		self.dlgGame.dlgSubmit.setUsername(dict["username"])
		self.dlgGame.dlgSubmit.setPassword(dict["password"])
		self.dlgGame.dlgSubmit.userID=dict["userid"]
		self.dlgGame.setUsername(dict["nickname"])
		self.dlgGame.gameID=dict["gameid"]
		self.drawGhostPiece=dict["ghost"]=="True"
		self.dlgPause.chkGhostPiece.setSelected(self.drawGhostPiece)

#xbmc.enableNavSounds(False)
lock = threading.Lock()
random.seed(time.time())
board = Board(10,20)
controller = BoardController(board)
t = Tetris()
t.loadSettings()
t.setController(controller)
t.startTimer()
t.doModal()
t.stopTimer()
t.saveSettings()
del t,controller,board
#xbmc.enableNavSounds(True)
LOGCLOSE()