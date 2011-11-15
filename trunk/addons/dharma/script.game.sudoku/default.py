
# Sudoku v1.00 Feb 04 2006 By MrZ (matz.hedman@telia.com)
# Thank you Robert Wohleb for the grid generator
# Sudoku for XBMC. v1.00 = PAL
# Fixed X-button, use Trigger Right instead
# Download grids from websudoku.com, 4 levels
# Save/Load multiple files
# Enjoy!
# MrZ

# 28-07-2009 by Frost (passion-xbmc.org)
# Cleanup some code
# added compatibility for all XBMC platform use os.path.join and xbmc.translatePath
# changed version 1.00 to 1.1.0
# added xbmc language
# fixed deleted game


scriptname = "Sudoku"
VER = 'v1.1.0'

__addonID__ = "script.game.sudoku"

import os
import sys
import random
import string
import urllib
from time import strftime
from threading import Timer
from datetime import datetime
from traceback import print_exc

import xbmc
import xbmcgui
import xbmcaddon

GET_LOCALIZED_STRING = xbmcaddon.Addon( __addonID__ ).getLocalizedString


scriptPath = os.getcwd()

RESOURCES = os.path.join( scriptPath, "resources" )
GAMES = xbmc.translatePath( "special://profile/addon_data/%s/Games/" % __addonID__ )
if not os.path.isdir( GAMES ): os.makedirs( GAMES )


ACTION_MOVE_LEFT     = 1
ACTION_MOVE_RIGHT    = 2
ACTION_MOVE_UP       = 3
ACTION_MOVE_DOWN     = 4
ACTION_SELECT_ITEM   = 7
ACTION_BACK          = 9
ACTION_PREVIOUS_MENU = 10
ACTION_SHOW_INFO     = 11
ACTION_NEXT          = 14
ACTION_PREVIOUS      = 15
ACTION_DISPLAY       = 18
ACTION_TITLE         = 117


def setup():
    global xOfs;    xOfs    = 200
    global yOfs;    yOfs    = 28
    global btnX;    btnX    = 38
    global btnY;    btnY    = 28
    global btnW;    btnW    = 140
    global size;    size    = 44
    global mFill;   mFill   = 30
    global mSquare; mSquare = 3
    global mNums;   mNums   = 3


def getGame( loadedGame ):
    myFiles = os.listdir( GAMES )
    i = len( myFiles ) -1
    firstFound = ''
    nextFound = ''
    hit = False
    while i > -1:
        if myFiles[ i ][ -4: ].lower() == '.sdu':
            if hit:
                nextFound = myFiles[ i ]
                hit = False
            if firstFound == '':
                firstFound = myFiles[ i ]
            if myFiles[ i ] == loadedGame:
                hit = True
        i -= 1
    if nextFound <> '':
        return nextFound
    else:
        return firstFound


def getWEBGrid( level ):
    grid = []
    try:
        data = urllib.urlopen( 'http://show.websudoku.com/?level=' + str( level ) )
        webpage = data.read().lower()
        gridData = webpage[ webpage.find( 'board' ): ]
        gridData = gridData[ 0:gridData.find( '</table>' ) ]
        cellData = string.split( gridData, '</td' )
        i = 0
        while i < len( cellData ):
            myValue = 0
            ptr = cellData[ i ].find( 'readonly value="' )
            if ptr > 0:
                myValue = int( cellData[ i ][ ptr+16:ptr+17 ] )
            if myValue > 0:
                grid.append( [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, myValue, myValue, 1 ] )
            else:
                grid.append( [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0, 0, 0 ] )
            i += 1
    except:
        print 'Failed downloading sudoku grid'
        print_exc()
    return grid


class board:
    boardlist = []
    grid = []

    def generate( self ):
        global mFill, mSquare, mNums
        slots = []
        self.boardlist = []
        random.seed()

        for i in range( 0, 9 ):
            self.boardlist.append( [ 0, 0, 0, 0, 0, 0, 0, 0, 0 ] )

        for j in range( 0, 9 ):
            for i in range( 0, 9 ):
                slots.append( ( i, j ) )

        self.search( slots, 0 )
        self.grid = []

        for row in range( 0, 9 ):
            for col in range( 0, 9 ):
                nr = self.boardlist[ row ][ col ]
                self.grid.append( [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, nr, nr, 1 ] ) # column 0 should be text

        pairs = 0
        for x in ( 0, 3, 6 ):
            for y in range( x+1, x+3 ):
                rr = self.grid[ y*9 ][ 11 ]*10
                rr += self.grid[ x*9 ][ 11 ]
                cr = self.grid[ y ][ 11 ]*10
                cr += self.grid[ x ][ 11 ]
                for z in range( 1, 9 ):
                    rc = self.grid[ x*9+z ][ 11 ]*10
                    rc += self.grid[ y*9+z ][ 11 ]
                    cc = self.grid[ z*9+x ][ 11 ]*10
                    cc += self.grid[ z*9+y ][ 11 ]
                    if rr == rc:
                        self.grid[ x*9 ][ 12 ] = 0
                        pairs += 1
                        #print 'row', rr, rc
                    elif cr == cc:
                        self.grid[ x ][ 12 ] = 0
                        pairs += 1
                        #print 'col', cr, cc
        #print pairs

        matrix = self.calcMatrix()
        loops = 0
        while matrix[ 0 ] > mFill and loops < 25000:
            loops += 1
            b = random.randint( 0, 80 )
            row = b/9
            col = ( b-row*9 )
            if ( matrix[ self.grid[ b ][ 10 ] ] > mNums and self.grid[ b ][ 12 ] == 1 ) or loops > 25000:
                if matrix[ 10 + ( row/3 ) * 3 + ( col/3 ) ] > mSquare or loops > 25000:
                    self.grid[ b ][ 10 ] = 0
                    self.grid[ b ][ 12 ] = 0
            matrix = self.calcMatrix()
        for i in range( 0, 81 ):
            gPtr = self.grid[ i ]
            if gPtr[ 10 ] > 0:
                gPtr[ 12 ] = 1
        return self.grid

    def calcMatrix( self ):
        res = [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ]
        for row in range( 0, 9 ):
            for col in range( 0, 9 ):
                if self.grid[ row*9+col ][ 10 ] > 0:
                    res[ 0 ] += 1
                    res[ self.grid[ row*9+col ][ 10 ] ] += 1
                    res[ 10 + ( row/3 ) * 3 + ( col/3 ) ] += 1
        return res

    def search( self, slots, index ):
        nums = []
        fillOrder = []

        if len( slots ) == index:
            return self.check()

        for i in range( 1, 10 ):
            nums.append( i )

        while len( nums ) > 0:
            i = random.randint( 0, len( nums )-1 )
            fillOrder.append( nums[ i ] )
            del nums[ i ]

        for i in fillOrder:
            x = slots[ index ][ 0 ]
            y = slots[ index ][ 1 ]
            self.boardlist[ x ][ y ] = i
            if ( self.check() ):
                if self.search( slots, index+1 ):
                    return True
            self.boardlist[ x ][ y ] = 0
        return False

    def check( self ):
        for i in range( 0, 9 ):
            if ( not self.checkRow( i ) ) or ( not self.checkCol( i ) ) or ( not self.checkSquare( i ) ):
                return False
        return True

    def checkRow( self, row ):
        found = []
        for i in range( 0, 9 ):
            if not self.boardlist[ i ][ row ] == 0:
                if self.boardlist[ i ][ row ] in found:
                    return False
                found.append( self.boardlist[ i ][ row ] )
        return True

    def checkCol( self, col ):
        found = []
        for j in range( 0, 9 ):
            if not self.boardlist[ col ][ j ] == 0:
                if self.boardlist[ col ][ j ] in found:
                    return False
                found.append( self.boardlist[ col ][ j ] )
        return True

    def checkSquare( self, square ):
        found = []
        xO = ( 3*( square % 3 ) )
        yO = int( square / 3 ) * 3
        for x in range( xO, xO+3 ):
            for y in range( yO, yO+3 ):
                if not self.boardlist[ y ][ x ] == 0:
                    if self.boardlist[ y ][ x ] in found:
                        return False
                    found.append( self.boardlist[ y ][ x ] )
        return True


class Sudoku( xbmcgui.Window ):
    global yOfs, size

    def __init__( self ):
        xbmcgui.Window.__init__( self )
        self.setCoordinateResolution( 6 )
        try:
            self.addControl( xbmcgui.ControlImage( 0, 0, 725, 576, os.path.join( RESOURCES, "media", 'Background.png' ) ) )
            self.addControl( xbmcgui.ControlLabel( 655, 500, 250, 35, "[B]%s[/B]" % VER, textColor='0xa0ffffff' ) )

            self.btnClearError = xbmcgui.ControlButton( btnX, btnY+180, btnW, 35, GET_LOCALIZED_STRING( 32140 ), textColor='0xff000000', focusTexture=os.path.join( RESOURCES, "media", 'b0.png' ), noFocusTexture=os.path.join( RESOURCES, "media", 'y0.png' ) )
            self.addControl( self.btnClearError )
            self.btnReveal = xbmcgui.ControlButton( btnX, btnY+225, btnW, 35, GET_LOCALIZED_STRING( 32150 ), textColor='0xff000000', focusTexture=os.path.join( RESOURCES, "media", 'b0.png' ), noFocusTexture=os.path.join( RESOURCES, "media", 'y0.png' ) )
            self.addControl( self.btnReveal )
            self.btnSave = xbmcgui.ControlButton( btnX, btnY+270, btnW, 35, GET_LOCALIZED_STRING( 32160 ), textColor='0xff000000', focusTexture=os.path.join( RESOURCES, "media", 'b0.png' ), noFocusTexture=os.path.join( RESOURCES, "media", 'y0.png' ) )
            self.addControl( self.btnSave )
            self.btnLoad = xbmcgui.ControlButton( btnX, btnY+315, btnW, 35, GET_LOCALIZED_STRING( 32170 ), textColor='0xff000000', focusTexture=os.path.join( RESOURCES, "media", 'b0.png' ), noFocusTexture=os.path.join( RESOURCES, "media", 'y0.png' ) )
            self.addControl( self.btnLoad )
            self.btnDelete = xbmcgui.ControlButton( btnX, btnY+360, btnW, 35, GET_LOCALIZED_STRING( 32180 ), textColor='0xff000000', focusTexture=os.path.join( RESOURCES, "media", 'b0.png' ), noFocusTexture=os.path.join( RESOURCES, "media", 'y0.png' ) )
            self.addControl( self.btnDelete )
            self.btnExit = xbmcgui.ControlButton( btnX, btnY+405, btnW, 35, GET_LOCALIZED_STRING( 32190 ), textColor='0xff000000', focusTexture=os.path.join( RESOURCES, "media", 'b0.png' ), noFocusTexture=os.path.join( RESOURCES, "media", 'y0.png' ) )
            self.addControl( self.btnExit )

            self.lblHint = xbmcgui.ControlLabel( xOfs+2, yOfs+10*size-30, 250, 35, '', textColor='0xff000000' )
            self.addControl( self.lblHint )
            self.lblName = xbmcgui.ControlLabel( xOfs+2, yOfs+10*size-10, 350, 35, '', textColor='0xff000000' )
            self.addControl( self.lblName )
            self.lblTimer = xbmcgui.ControlLabel( xOfs+400, yOfs+10*size-30, 200, 35, GET_LOCALIZED_STRING( 32220 ) % '00:00:00', textColor='0xff000000', alignment=0x00000001 )
            self.addControl( self.lblTimer )

            self.btnClearError.controlDown( self.btnReveal )
            self.btnReveal.controlUp( self.btnClearError )
            self.btnReveal.controlDown( self.btnSave )
            self.btnSave.controlUp( self.btnReveal )
            self.btnSave.controlDown( self.btnLoad )
            self.btnLoad.controlUp( self.btnSave )
            self.btnLoad.controlDown( self.btnDelete )
            self.btnDelete.controlUp( self.btnLoad )
            self.btnDelete.controlDown( self.btnExit )
            self.btnExit.controlUp( self.btnDelete )
        except:
            print 'Failed to draw buttons'
            print_exc()
        self.grid = []
        self.gameName = getGame( '' )
        self.generateMode = 10
        self.genMode()
        self.gameTimer = 0
        if self.gameName == '':
            self.newGrid()
        else:
            self.loadGrid()
        self.tmrStatus = 1
        self.startTimer()

    def startTimer( self ):
        self.t = None
        self.t = Timer( 1.0, self.drawTimer )
        self.t.start()

    def drawTimer( self ):
        self.gameTimer += 1
        self.lblTimer.setLabel( GET_LOCALIZED_STRING( 32220 ) % self.timeFormat( self.gameTimer ) )
        if self.tmrStatus == 1:
            self.startTimer()
        else:
            self.tmrStatus = 2

    def timeFormat( self, ticks ):
        h = ticks / 3600
        m = ( ticks - h*3600 ) / 60
        s = ticks - h*3600 - m*60
        return str( h+100 )[ 1: ] + ':' + str( m+100 )[ 1: ] + ':' + str( s+100 )[ 1: ]

    def genMode( self ):
        try: self.removeControl( self.btnNewGame )
        except: pass
        self.generateMode += 1
        if self.generateMode > 4:
            self.generateMode = 0
        if self.generateMode == 0:
            self.btnNewGame = xbmcgui.ControlButton( btnX, btnY, btnW, 35, GET_LOCALIZED_STRING( 32100 ), textColor='0xff000000', focusTexture=os.path.join( RESOURCES, "media", 'b0.png' ), noFocusTexture=os.path.join( RESOURCES, "media", 'y0.png' ) )
        elif self.generateMode == 1:
            self.btnNewGame = xbmcgui.ControlButton( btnX, btnY, btnW, 35, GET_LOCALIZED_STRING( 32101 ), textColor='0xff000000', focusTexture=os.path.join( RESOURCES, "media", 'b0.png' ), noFocusTexture=os.path.join( RESOURCES, "media", 'y0.png' ) )
        elif self.generateMode == 2:
            self.btnNewGame = xbmcgui.ControlButton( btnX, btnY, btnW, 35, GET_LOCALIZED_STRING( 32102 ), textColor='0xff000000', focusTexture=os.path.join( RESOURCES, "media", 'b0.png' ), noFocusTexture=os.path.join( RESOURCES, "media", 'y0.png' ) )
        elif self.generateMode == 3:
            self.btnNewGame = xbmcgui.ControlButton( btnX, btnY, btnW, 35, GET_LOCALIZED_STRING( 32103 ), textColor='0xff000000', focusTexture=os.path.join( RESOURCES, "media", 'b0.png' ), noFocusTexture=os.path.join( RESOURCES, "media", 'y0.png' ) )
        elif self.generateMode == 4:
            self.btnNewGame = xbmcgui.ControlButton( btnX, btnY, btnW, 35, GET_LOCALIZED_STRING( 32104 ), textColor='0xff000000', focusTexture=os.path.join( RESOURCES, "media", 'b0.png' ), noFocusTexture=os.path.join( RESOURCES, "media", 'y0.png' ) )
        self.addControl( self.btnNewGame )
        self.btnExit.controlDown( self.btnNewGame )
        self.btnNewGame.controlUp( self.btnExit )
        try: self.removeControl( self.btnMinFill )
        except: pass
        try: self.removeControl( self.btnMinSquare )
        except: pass
        try: self.removeControl( self.btnMinNums )
        except: pass
        if self.generateMode == 0:
            self.config( 0, 0 )
        else:
            self.btnNewGame.controlDown( self.btnClearError )
            self.btnClearError.controlUp( self.btnNewGame )
        self.setFocus( self.btnNewGame )

    def config( self, type, change ):
        global mFill, mSquare, mNums
        try: self.removeControl( self.btnMinFill )
        except: pass
        try: self.removeControl( self.btnMinSquare )
        except: pass
        try: self.removeControl( self.btnMinNums )
        except: pass

        if type == 1:
            mFill += change
            if mFill < 16: mFill = 60
            elif mFill > 60: mFill = 16
            if mSquare * 9 > mFill:
                mSquare -= 1
            if mNums * 9 > mFill:
                mNums -= 1
        elif type == 2:
            mSquare += change
            if mSquare < 0: mSquare = 5
            elif mSquare > 5: mSquare = 0
        elif type == 3:
            mNums += change
            if mNums < 0: mNums = 5
            elif mNums > 5: mNums = 0
        if mFill < mSquare * 9: mFill = mSquare * 9
        if mFill < mNums * 9: mFill = mNums * 9

        self.btnMinFill = xbmcgui.ControlButton( btnX+20, btnY+45, btnW-20, 35, GET_LOCALIZED_STRING( 32110 ) % str( mFill ), textColor='0xff000000', focusTexture=os.path.join( RESOURCES, "media", 'b0.png' ), noFocusTexture=os.path.join( RESOURCES, "media", 'y0.png' ) )
        self.addControl( self.btnMinFill )
        self.btnMinSquare = xbmcgui.ControlButton( btnX+20, btnY+90, btnW-20, 35, GET_LOCALIZED_STRING( 32120 ) % str( mSquare ), textColor='0xff000000', focusTexture=os.path.join( RESOURCES, "media", 'b0.png' ), noFocusTexture=os.path.join( RESOURCES, "media", 'y0.png' ) )
        self.addControl( self.btnMinSquare )
        self.btnMinNums = xbmcgui.ControlButton( btnX+20, btnY+135, btnW-20, 35, GET_LOCALIZED_STRING( 32130 ) % str( mNums ), textColor='0xff000000', focusTexture=os.path.join( RESOURCES, "media", 'b0.png' ), noFocusTexture=os.path.join( RESOURCES, "media", 'y0.png' ) )
        self.addControl( self.btnMinNums )

        if type == 1: self.setFocus( self.btnMinFill )
        elif type == 2: self.setFocus( self.btnMinSquare )
        elif type == 3: self.setFocus( self.btnMinNums )

        self.btnNewGame.controlDown( self.btnMinFill )
        self.btnMinFill.controlUp( self.btnNewGame )
        self.btnMinFill.controlDown( self.btnMinSquare )
        self.btnMinSquare.controlUp( self.btnMinFill )
        self.btnMinSquare.controlDown( self.btnMinNums )
        self.btnMinNums.controlUp( self.btnMinSquare )
        self.btnMinNums.controlDown( self.btnClearError )
        self.btnClearError.controlUp( self.btnMinNums )

    def onControl( self, control ):
        try:
            if control == self.btnNewGame:
                self.newGrid()
            elif self.generateMode == 0 and control in ( self.btnMinFill, self.btnMinSquare, self.btnMinNums ):
                self.newGrid()
            elif control == self.btnClearError:
                self.cleanUp()
            elif control == self.btnReveal:
                self.revealNumber()
            elif control == self.btnSave:
                self.saveGrid()
            elif control == self.btnLoad:
                self.gameName = getGame( self.gameName )
                self.loadGrid()
                self.setFocus( self.btnLoad )
                self.pgmMode = 'MENU'
            elif control == self.btnDelete:
                if os.path.isfile( os.path.join( GAMES, self.gameName ) ):
                    try:
                        os.remove( os.path.join( GAMES, self.gameName ) )
                        #self.gameName = getGame( self.gameName )
                        #self.loadGrid()
                    except:
                        print_exc()
                    else:
                        self.newGrid()
            elif control == self.btnExit:
                if self.tmrStatus == 1:
                    self.tmrStatus = 0
                    while self.tmrStatus <> 2:
                        pass
                self.close()
        except:
            print 'Error handling controls'
            print_exc()

    def onAction( self, action ):
        try:
            if self.pgmMode == 'GRID':
                if action == ACTION_PREVIOUS_MENU:
                    self.pgmMode = 'MENU'
                    self.setFocus( self.btnNewGame )
                if action == ACTION_MOVE_LEFT:
                    self.setMarker( self.row, self.col-1 )
                if action == ACTION_MOVE_RIGHT:
                    self.setMarker( self.row, self.col+1 )
                if action == ACTION_MOVE_UP:
                    self.setMarker( self.row-1, self.col )
                if action == ACTION_MOVE_DOWN:
                    self.setMarker( self.row+1, self.col )
                if action == ACTION_DISPLAY or action == ACTION_TITLE or action == 6:
                    self.getNumber( self.row, self.col )
                if action == ACTION_SELECT_ITEM:
                    self.setNumber( self.row, self.col, self.nr )
                if action == ACTION_SHOW_INFO or action == 34:
                    self.solve()
                if action in range( 58, 68 ):
                    self.setNumber( self.row, self.col, action-58 )
            else:
                if action == ACTION_PREVIOUS_MENU:
                    self.pgmMode = 'GRID'
                    self.setFocus( self.boxes[ 0 ] )
                if self.generateMode == 0:
                    if action == ACTION_MOVE_LEFT:
                        if self.getFocus() == self.btnMinFill:
                            self.config( 1, -1 )
                        elif self.getFocus() == self.btnMinSquare:
                            self.config( 2, -1 )
                        elif self.getFocus() == self.btnMinNums:
                            self.config( 3, -1 )
                    if action == ACTION_MOVE_RIGHT:
                        if self.getFocus() == self.btnNewGame:
                            self.genMode()
                        elif self.getFocus() == self.btnMinFill:
                            self.config( 1, 1 )
                        elif self.getFocus() == self.btnMinSquare:
                            self.config( 2, 1 )
                        elif self.getFocus() == self.btnMinNums:
                            self.config( 3, 1 )
                else:
                    if action == ACTION_MOVE_RIGHT:
                        if self.getFocus() == self.btnNewGame:
                            self.genMode()
        except:
            print 'Error handling controls'
            print_exc()

    def saveGrid( self ):
        if self.gameName == '':
            self.gameName = datetime.today().strftime( '%Y%m%d_%H%M%S' ) + '.SDU'
        try:
            f = open( os.path.join( GAMES, self.gameName ), 'w' )
            f.write( str( self.gameTimer ) + '\n' )
            for i in range( 0, 81 ):
                f.write( str( self.grid[ i ] ) + '\n' )
            f.close()
        except:
            print 'Error saving game'
            print_exc()
        self.drawScreen()

    def loadGrid( self ):
        self.row = 0
        self.col = 0
        self.nr = 0
        try:
            f = open( os.path.join( GAMES, self.gameName ), 'r' )
            grid = f.readlines()
            f.close()
            self.grid = []
            i = 1
            while i < len( grid ):
                data = []
                src = grid[ i ][ 1:len( grid[ i ] )-2 ]
                box = string.split( src, ', ' )
                j = 0
                while j < len( box ):
                    data.append( int( box[ j ] ) )
                    j += 1
                self.grid.append( data )
                i += 1
        except:
            print 'Error loading game'
            print_exc()
        self.setPossible()
        self.drawScreen()
        self.gameTimer = int( grid[ 0 ][ :-1 ] )

    def newGrid( self ):
        self.gameName = ''
        self.row = 0
        self.col = 0
        self.nr = 0
        if len( self.grid ) > 0:
            for i in range( 0, 81 ):
                self.grid[ i ][ 10 ] = 0
                self.grid[ i ][ 11 ] = 0
                self.grid[ i ][ 12 ] = 0
            self.drawScreen()
        if self.generateMode == 0:
            self.grid = board().generate()
        else:
            self.grid = getWEBGrid( self.generateMode )
        self.setPossible()
        self.drawScreen()
        self.gameTimer = 0

    def cleanUp( self ):
        for i in range( 0, 81 ):
            gPtr = self.grid[ i ]
            if gPtr[ 10 ] <> gPtr[ 11 ]:
                gPtr[ 10 ] = 0
        self.setPossible()
        self.drawScreen()

    def revealNumber( self ):
        hits = 0
        for i in range( 0, 81 ):
            if self.grid[ i ][ 10 ] > 0:
                hits += 1
                self.grid[ i ][ 12 ] = 1
        if hits > 0:
            i = random.randint( 0, 80 )
            while self.grid[ i ][ 10 ] > 0:
                i = random.randint( 0, 80 )
            self.grid[ i ][ 10 ] = self.grid[ i ][ 11 ]
        self.setPossible()
        self.drawScreen()

    def solve( self ):
        hits = 0
        for i in range( 0, 81 ):
            gPtr = self.grid[ i ]
            if gPtr[ 10 ] == gPtr[ 11 ]:
                hits += 1
            else:
                gPtr[ 10 ] = gPtr[ 11 ]
        if hits == 81:
            for i in range( 0, 81 ):
                gPtr = self.grid[ i ]
                if gPtr[ 12 ] == 1:
                    gPtr[ 10 ] = gPtr[ 11 ]
                else:
                    gPtr[ 10 ] = 0
        self.drawScreen()

    def getNumber( self, row, col ):
        gPtr = self.grid[ row*9+col ]
        if gPtr[ 10 ] == 0:
            ctr = 0
            ptr = self.nr+1
            if ptr > 9:
                ptr = 1
            while ctr < 10 and gPtr[ ptr ] <> ptr:
                ptr += 1
                if ptr > 9:
                    ptr = 1
                ctr += 1
            self.setMarker( self.row, self.col, gPtr[ ptr ] )
        else:
            self.nr = gPtr[ 10 ]

    def setNumber( self, row, col, nr ):
        gPtr = self.grid[ row*9+col ]
        if gPtr[ 12 ] == 0:
            gPtr[ 10 ] = nr
            self.setPossible()
            self.drawBox( row, col )
            self.setMarker( row, col )

    def setPossible( self ):
        for i in range( 0, 81 ):
            for x in range( 1, 10 ):
                self.grid[ i ][ x ] = x
        for row in range( 0, 9 ):
            for col in range( 0, 9 ):
                nr = self.grid[ row*9+col ][ 10 ]
                if nr > 0:
                    for i in range( 0, 9 ):
                        self.grid[ i*9+col ][ nr ] = 0
                        self.grid[ row*9+i ][ nr ] = 0
                    for r in ( row/3*3, row/3*3+1, row/3*3+2 ):
                        for c in ( col/3*3, col/3*3+1, col/3*3+2 ):
                            self.grid[ r*9+c ][ nr ] = 0

    def setMarker( self, row, col, nr=0 ):
        global box, xOfs, yOfs, size
        if row == 0 and col == 0:
            col = 9
            row = 9
        if col > self.col:
            while col > 8 or self.grid[ row*9+col ][ 12 ] <> 0:
                col += 1
                if col > 8:
                    col = 0
                    row += 1
                    if row > 8:
                        row = 0
        elif col < self.col:
            while col < 0 or self.grid[ row*9+col ][ 12 ] <> 0:
                col -= 1
                if col < 0:
                    col = 8
                    row -= 1
                    if row < 0:
                        row = 8
        elif row > self.row:
            while row > 8 or self.grid[ row*9+col ][ 12 ] <> 0:
                row += 1
                if row > 8:
                    row = 0
                    col += 1
                    if col > 8:
                        col = 0
        elif row < self.row:
            while row < 0 or self.grid[ row*9+col ][ 12 ] <> 0:
                row -= 1
                if row < 0:
                    row = 8
                    col -= 1
                    if col < 0:
                        col = 8
        self.row = row
        self.col = col

        gPtr = self.grid[ self.row*9+self.col ]
        try: self.removeControl( self.marker )
        except: pass
        try:
            self.nr = nr
            if nr == 0:
                icon = os.path.join( RESOURCES, "media", 'b%s.png' % str( gPtr[ 10 ] ) )
            else:
                icon = os.path.join( RESOURCES, "media", 'b%s.png' % str( nr ) )
            self.marker = xbmcgui.ControlImage( xOfs+self.col*size + self.col/3*5, yOfs+self.row*size + self.row/3*5, size, size, icon )
            self.addControl( self.marker )
        except:
            pass
        hint = ''
        if gPtr[ 10 ] == 0:
            for i in range( 0, 10 ):
                if gPtr[ i ] > 0:
                    hint = hint + str( i ) + '-'
        set = 0
        for i in range( 0, 81 ):
            if self.grid[ i ][ 10 ] == 0:
                set += 1
        if set > 0:
            if len( hint ) > 1:
                message = GET_LOCALIZED_STRING( 32200 ) % ( hint[ :len( hint )-1 ], str( set ) )
            else:
                message = GET_LOCALIZED_STRING( 32201 ) % str( set )
        else:
            message = GET_LOCALIZED_STRING( 32202 ) % self.timeFormat( self.gameTimer )
        self.lblHint.setLabel( message )

    def drawScreen( self ):
        self.boxes = []
        for row in range( 0, 9 ):
            for col in range( 0, 9 ):
                self.boxes.append( 0 )
                self.drawBox( row, col )
        self.setMarker( self.row, self.col )
        if self.gameName <> '':
            self.lblName.setLabel( GET_LOCALIZED_STRING( 32210 ) % self.gameName )
        else:
            self.lblName.setLabel( GET_LOCALIZED_STRING( 32211 ) )
        self.setFocus( self.boxes[ 0 ] )
        self.pgmMode = 'GRID'

    def drawBox( self, row, col ):
        global xOfs, yOfs, size
        gPtr = self.grid[ row*9+col ]
        if gPtr[ 12 ] == 1:
            icon = os.path.join( RESOURCES, "media", 'y%s.png' % str( gPtr[ 10 ] ) )
        else:
            icon = os.path.join( RESOURCES, "media", 'ys%s.png' % str( gPtr[ 10 ] ) )
        try:
            self.removeControl( self.boxes[ row*9+col ] )
        except:
            pass
        try:
            self.boxes[ row*9+col ] = xbmcgui.ControlImage( xOfs+col*size + col/3*5, yOfs+row*size + row/3*5, size, size, icon )
            self.addControl( self.boxes[ row*9+col ] )
        except:
            print 'Problems with graphics'
            print_exc()



if ( __name__ == "__main__" ):
    setup()
    W = Sudoku()
    W.doModal()
    del W

