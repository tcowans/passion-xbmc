
import time
from threading import Timer
from traceback import print_exc

import xbmc


class AutoMove:
    def __init__( self ):
        self._stop = xbmc.abortRequested
        self.wait = 10
        self.move_thread = None
        self.controls_id = [ 8000, 8001, 8002, 8003, 8004 ]
        self.condition   = "Control.IsVisible(%i) + !Control.HasFocus(%i) + IntegerGreaterThan(Container(%i).NumItems,1)"
        # start thread
        self.run()

    def run( self ):
        try:
            while not self._stop:
                self._stop = xbmc.abortRequested
                if xbmc.getCondVisibility( "!Window.IsVisible(10000) | System.IdleTime(7200)" ):
                    self.stop()
                if not self.move_thread:
                    self.move_thread = Timer( self.wait, self.move, () )
                    self.move_thread.start()
                    #print time.ctime()
                time.sleep( .25 )
        except SystemExit:
            print "SystemExit!"
        except:
            print_exc()
        self.stop()

    def move( self ):
        for i in self.controls_id:
            self._stop = xbmc.abortRequested
            if self._stop: break
            if xbmc.getCondVisibility( self.condition % ( i, i, i ) ):
                xbmc.executebuiltin( "Control.Move(%i,-1)" % i )
                time.sleep( .25 )
        self._stop_move_thread()

    def _stop_move_thread( self ):
        try: self.move_thread.cancel()
        except: pass
        self.move_thread = None

    def stop( self ):
        self._stop_move_thread()
        self._stop = True

AutoMove()
