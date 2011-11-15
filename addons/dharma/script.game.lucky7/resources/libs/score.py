
#modules custom
from utilities import *


class Gain:
    def __init__( self, *args, **kwargs ):
        self.gui = kwargs[ "gui" ]
        try:
            bet = self.gui.betting#getListItem( self.gui.getCurrentListPosition() ).getLabel().strip( "$" )
            self.betting = int( bet )
        except: self.betting = 0 #1
        self.slots = args
        self.slot1 = self.slots[ 0 ]
        self.slot2 = self.slots[ 1 ]
        self.slot3 = self.slots[ 2 ]

        self.gain = 0
        self.win_slots = [ 0, 0, 0 ]

        #special bonus
        self.all_fruits = ( [ s.split( "/" )[ 0 ] for s in self.slots ].count( "fruits" ) == 9 )
        self.win_jackpot = self.all_fruits
        self.win = self.win_jackpot

        self.checking_gain()

    def checking_gain( self ):
        if self.slot1 == self.slot2 == self.slot3:
            #print ''' SAME SLOTS. EXAMPLE: |7|7|7| '''
            self.tripple()
            return

        bars = [ self.slot1, self.slot2, self.slot3 ]
        if ( bars.count( ONE_BAR ) + bars.count( TWO_BAR ) + bars.count( THREE_BAR ) ) >= 3:
            self.win = True
            self.win_slots = [ 1, 1, 1 ]
            if ( ONE_BAR in bars ) and ( TWO_BAR in bars ) and ( THREE_BAR in bars ):
                #print ''' ANY BAR. EXAMPLE: |B3R|B1R|B2R| '''
                self.gain = self.betting * 50
            else:
                #print ''' TWO SAME BAR AND ANY BAR. EXAMPLE: |B3R|B3R|B2R| '''
                self.gain = self.betting * 25
            return

        if ( self.slot1 == self.slot2 ) or ( self.slot1 == self.slot3 ) or ( self.slot2 == self.slot3 ):
            #print ''' DOUBLE FOR SEVEN AND CHERRY ONLY'''
            #print ''' EXAMPLE: |7|CHERRY|7| OR |CHERRY|CHERRY|B1R|'''
            if self.double():
                return

        # LAST CHANCE FOR SIMPLE SEVEN AND CHERRY ONLY
        if self.simple():
            return

        #print self.slots

    def simple( self ):
        OK = False
        if ( self.slot2 == SEVEN ):
            #print ''' ONE SEVEN IN CENTER SLOT. EXAMPLE: |Bell|7|B3R| '''
            x = 10
            s1 = ( self.slot1 == CHERRIES )
            s3 = ( self.slot3 == CHERRIES )
            if s1 or s3:
                #print ''' ONE SEVEN IN CENTER SLOT AND CHERRIES. EXAMPLE: |CHERRIES|7|B3R| OR |B2R|7|CHERRIES| '''
                x += 1
            self.win = True
            self.win_slots = [ s1, 1, s3 ]
            self.gain = self.betting * x
            OK = True

        elif CHERRIES in [ self.slot1, self.slot2, self.slot3 ]:
            #print ''' ONE CHERRY ONLY IN ANY SLOT. EXAMPLE: |?|?|?| '''
            self.win = True
            s1 = ( self.slot1 == CHERRIES )
            s2 = ( self.slot2 == CHERRIES )
            s3 = ( self.slot3 == CHERRIES )
            self.win_slots = [ s1, s2, s3 ]
            self.gain = self.betting * 1
            OK = True

        return OK

    def double( self ):
        OK = False
        if ( self.slot1 == self.slot2 == CHERRIES ) or ( self.slot2 == self.slot3 == CHERRIES ):
            self.win = True
            s1 = ( self.slot1 == CHERRIES )
            s2 = ( self.slot2 == CHERRIES )
            s3 = ( self.slot3 == CHERRIES )
            self.win_slots = [ s1, s2, s3 ]
            self.gain = self.betting * 10
            OK = True

        elif ( self.slot1 == CHERRIES ) and ( self.slot3 == CHERRIES ):
            x = 10
            if ( self.slot2 == SEVEN ):
                x += 10
            self.win = True
            self.win_slots = [ 1, ( x > 10 ), 1 ]
            self.gain = self.betting * x
            OK = True

        elif ( self.slot1 == SEVEN ) and ( self.slot3 == SEVEN ):
            x = 100
            if ( self.slot2 == CHERRIES ):
                x += 1
            self.win = True
            self.win_slots = [ 1, ( x > 100 ), 1 ]
            self.gain = self.betting * x
            OK = True

        return OK

    def tripple( self ):
        self.win = True
        self.win_slots = [ 1, 1, 1 ]

        if self.slot1 == SEVEN:
            self.win_jackpot = True
            self.gain = self.betting * 1000

        elif self.slot1 == BELL:
            self.gain = self.betting * 500

        elif self.slot1 == THREE_BAR:
            self.gain = self.betting * 300

        elif self.slot1 == TWO_BAR:
           self.gain = self.betting * 200

        elif self.slot1 in ( CHERRIES, ONE_BAR ):
           self.gain = self.betting * 100

        elif self.slot1 in ( PEACH, WATERMELON ):
            self.gain = self.betting * 75

        elif self.slot1 == COCONUT:
            self.gain = self.betting * 50

        elif self.slot1 in ( BANANA, KIWI, PASSION, XBMC ):
            self.gain = self.betting * 25

        elif self.slot1 in ( APPLE, LEMON, LIME ):
            self.gain = self.betting * 20

        elif self.slot1 == STRAWBERRY:
            self.gain = self.betting * 15

        elif self.slot1 in ( ORANGE, ORANGE2 ):
            self.gain = self.betting * 10

        elif self.slot1 in ( BLACKBERRY, GRAPES ):
           self.gain = self.betting * 5


if __name__ == "__main__":
    print Gain( BELL, CHERRIES, BELL,
        BELL, BELL, BELL, BELL, BELL, BELL, gui=None ).gain
