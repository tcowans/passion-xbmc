
#Modules general
import os
import sys
from traceback import print_exc
from threading import Thread, Timer

#modules XBMC
import xbmc
import xbmcgui

#modules custom
from score import Gain
from utilities import *


CWD = os.getcwd().rstrip( ";" )

_ = sys.modules[ "__main__" ].__language__

KEYMAP = sys.modules[ "__main__" ].KEYMAP


class LUCKY7( xbmcgui.WindowXML ):
    def __init__( self, *args, **kwargs ):
        xbmcgui.WindowXML.__init__( self, *args, **kwargs )

        self.items_slots  = getFruitsAndNonFruits()
        self.items_slot_1 = sorted( self.items_slots[ 0 ] )
        self.items_slot_2 = Shuffle( sorted( self.items_slots[ 1 ] ) )
        self.items_slot_3 = sorted( self.items_slots[ 2 ], reverse=True )
        self.range_items_slots = range( 21 )

        self.all_slots_stopped = False
        self.slot1_stopped     = False
        self.slot2_stopped     = False
        self.slot3_stopped     = False
        self.is_rolling        = False

        self.game_is_ok = False

    def play_SFX( self, SFX ):
        if not xbmc.getCondVisibility( "Skin.HasSetting(Lucky7_SFX_Muted)" ):
            xbmc.playSFX( SFX )

    def onInit( self ):
        try: 
            if not self.game_is_ok:
                self.onInitShowSampleSlots()
                self.load_credits()

                self.button_auto_spin = self.getControl( 31 )
                #Enable and reset bet 2x gain radio button
                self.button_2x = self.getControl( 62 )
                self.set_button_2x()

                if self.credits[ "jackpot" ] > 0:
                    self.setProperty( "jackpot", "%i" % self.credits[ "jackpot" ] )

                self.setProperty( "autospin", "" )

                self.game_is_ok = True

            self.fill_credits()
        except:
            print_exc()

    def onInitShowSampleSlots( self ):
        try: 
            s1, s2, s3 = random.sample( self.items_slot_1, 3 )
            self.setProperty( "slot1_top", s1 )
            self.setProperty( "slot1_middle", s2 )
            self.setProperty( "slot1_bottom", s3 )

            s1, s2, s3 = random.sample( self.items_slot_2, 3 )
            self.setProperty( "slot2_top", s1 )
            self.setProperty( "slot2_middle", s2 )
            self.setProperty( "slot2_bottom", s3 )

            s1, s2, s3 = random.sample( self.items_slot_3, 3 )
            self.setProperty( "slot3_top", s1 )
            self.setProperty( "slot3_middle", s2 )
            self.setProperty( "slot3_bottom", s3 )
        except:
            print_exc()

    def set_button_2x( self, statut=0 ):
        self.button_2x.setSelected( 0 )
        self.button_2x.setEnabled( statut )
        self.button_2x.setVisible( statut )

    def fill_credits( self ):
        try: 
            xbmcgui.lock()
            last_betting = 0
            if self.cash:
                try: last_betting = self.getCurrentListPosition()
                except: pass
                zero_cash = self.cash
                self.clearList()

                bronze = range( 1, 100 )
                for mise in bronze:
                    zero_cash = self.cash - mise
                    label2 = str( zero_cash )
                    if zero_cash >= 0:
                        listitem = xbmcgui.ListItem( str( mise ), label2, iconImage="money3.png", thumbnailImage="money3.png" )
                        self.addItem( listitem )

                silver = range( 100, 1000, 25 )
                for mise in silver:
                    zero_cash = self.cash - mise
                    label2 = str( zero_cash )
                    if zero_cash >= 0:
                        listitem = xbmcgui.ListItem( str( mise ), label2, iconImage="money2.png", thumbnailImage="money2.png" )
                        self.addItem( listitem )

                gold = range( 1000, 11000, 1000 )
                if not self.cash in gold + silver + bronze:
                    gold += [ self.cash ]
                for mise in gold:
                    zero_cash = self.cash - mise
                    label2 = str( zero_cash )
                    if zero_cash >= 0:
                        listitem = xbmcgui.ListItem( str( mise ), label2, iconImage="money1.png", thumbnailImage="money1.png" )
                        self.addItem( listitem )

                if last_betting > self.getListSize()-1:
                    last_betting = self.getListSize()-1
                self.setCurrentListPosition( last_betting )

        except:
            print_exc()
        xbmcgui.unlock()

        self.check_cash()

    def check_cash( self ):
        if not self.cash:
            self.cash = 0
            self.betting = 0
            self.last_win = 0
            self.set_button_2x()
            if xbmcgui.Dialog().yesno(  _( 0 ), _( 11 ) % _( 1 ), _( 12 ) ):
                self.cash = 5000
                self.fill_credits()
            else:
                self.clearList()

    def onFocus( self, controlID ):
        pass

    def onClick( self, controlID ):
        try:
            if controlID == 20:
                self.stop_slots( 1 )

            elif controlID == 21:
                self.stop_slots( 2 )

            elif controlID == 22:
                self.stop_slots( 3 )

            elif controlID == 23:
                self.stop_slots( 4 )

            elif controlID in ( 24, 25 ):
                self._start_thread()
                self.check_cash()

            elif controlID == 31:
                if self.button_auto_spin.isSelected():
                    self.setProperty( "autospin", "true" )
                else:
                    self.setProperty( "autospin", "" )

            elif controlID == 30:
                self._show_infos()

            elif controlID == 300:
                self._close_game()
        except:
            print_exc()

    def onAction( self, action ):
        if self.cash and xbmc.getCondVisibility( "Container.OnNext | Container.OnPrevious" ):
            self.play_SFX( PLAY_COIN_SFX )

        try: self.getListItem( self.getCurrentListPosition() ).getLabel()
        except: 
            try: self.setCurrentListPosition( self.getListSize()-1 )
            except: print_exc()

        try:
            if not self.is_rolling and KEYMAP[ "close_game" ][ action ]:
                self._close_game()

            if self.is_rolling:
                if KEYMAP[ "action_stop_slot_1" ][ action ]:
                    self.stop_slots( 1 )

                elif KEYMAP[ "action_stop_slot_2" ][ action ]:
                    self.stop_slots( 2 )

                elif KEYMAP[ "action_stop_slot_3" ][ action ]:
                    self.stop_slots( 3 )

                elif KEYMAP[ "action_stop_slots" ][ action ]:
                    self.stop_slots( 4 )

            if KEYMAP[ "action_start_spin" ][ action ]:
                self._start_thread()

            elif KEYMAP[ "action_bet_max" ][ action ]:
                self.play_SFX( PLAY_COIN_SFX )
                self.setCurrentListPosition( self.getListSize()-1 )

            elif KEYMAP[ "action_bet_up" ][ action ]:
                listsize = self.getListSize()
                pos = self.getCurrentListPosition() + 1
                if pos >= listsize: pos = listsize - 1
                self.play_SFX( PLAY_COIN_SFX )
                self.setCurrentListPosition( pos )

            elif KEYMAP[ "action_bet_down" ][ action ]:
                pos = self.getCurrentListPosition() - 1
                if pos <= 0: pos = 0
                self.play_SFX( PLAY_COIN_SFX )
                self.setCurrentListPosition( pos )

            elif KEYMAP[ "action_bet_2x_gain" ][ action ]:
                if xbmc.getCondVisibility( "Control.IsVisible(62)" ):
                    if self.button_2x.isSelected():
                        self.button_2x.setSelected( 0 )
                    else:
                        self.button_2x.setSelected( 1 )

            elif KEYMAP[ "action_auto_spin" ][ action ]:
                if self.button_auto_spin.isSelected():
                    self.button_auto_spin.setSelected( 0 )
                    self.setProperty( "autospin", "" )
                else:
                    self.setProperty( "autospin", "true" )
                    self.button_auto_spin.setSelected( 1 )

            elif KEYMAP[ "show_dialog_infos" ][ action ]:
                self._show_infos()

        except:
            print_exc()

    def _start_thread( self ):
        if not self.button_auto_spin.isSelected():
            self._stop_sub_thread()
        if not self.is_rolling and self.cash:
            self.setProperty( "active_spinner", "true" )
            self.play_SFX( PLAY_SPINNER_SFX )
            if self.last_win and self.button_2x.isSelected():
                self.betting = self.last_win * 2
            else:
                self.betting = self.getListItem( self.getCurrentListPosition() ).getLabel().strip( "$" )
                self.set_button_2x()
            self._stop_thread()
            self.is_rolling = True
            self._thread = Thread( target=self.start_spin )
            self._thread.start()
        if self.button_auto_spin.isSelected():
            self._stop_sub_thread()
            self._sub_thread = Timer( 3, self._start_thread, () )
            self._sub_thread.start()

    def _stop_thread( self ):
        try: self._thread.cancel()
        except: pass

    def _stop_sub_thread( self ):
        try: self._sub_thread.cancel()
        except: pass

    def stop_slots( self, slot=0 ):
        if slot:
            if slot == 1:
                self.slot1_stopped = True
            elif slot == 2:
                self.slot2_stopped = True
            elif slot == 3:
                self.slot3_stopped = True
            else:
                self.all_slots_stopped = True
                self._stop_thread()
            self.play_SFX( PLAY_STOP_SFX )

    def start_spin( self ):
        self.setProperty( "lose", "" )
        self.setProperty( "winning", "" )
        self.setProperty( "pot_win", "" )
        self.setProperty( "all_fruits", "" )
        self.setProperty( "slot1_win", "" )
        self.setProperty( "slot2_win", "" )
        self.setProperty( "slot3_win", "" )

        xbmc.sleep( 1200 )
        self.setProperty( "active_spinner", "" )
        #self.clearProperties()

        self.items_slot_1 = Shuffle( self.items_slot_1 )
        self.items_slot_2 = Shuffle( self.items_slot_2 )
        self.items_slot_3 = Shuffle( self.items_slot_3 )

        self.all_slots_stopped = False
        self.slot1_stopped = False
        self.slot2_stopped = False
        self.slot3_stopped = False

        for time_sleep in range( 1, 4 ):
            if self.all_slots_stopped: break
            self.play_SFX( PLAY_SPIN_SFX )
            time_sleep *= 40
            try:
                for item in self.range_items_slots:
                    if self.all_slots_stopped: break
                    xbmc.sleep( time_sleep )

                    if not self.slot1_stopped:
                        try: slot1_top    = self.items_slot_1[ item + 1 ]
                        except: slot1_top = self.items_slot_1[ 0 ]
                        slot1_middle      = self.items_slot_1[ item ]
                        slot1_bottom      = self.items_slot_1[ item - 1 ]
                        self.setProperty( "slot1_top", slot1_top )
                        self.setProperty( "slot1_middle", slot1_middle )
                        self.setProperty( "slot1_bottom", slot1_bottom )

                    if not self.slot2_stopped:
                        try: slot2_top    = self.items_slot_2[ item + 1 ]
                        except: slot2_top = self.items_slot_2[ 0 ]
                        slot2_middle      = self.items_slot_2[ item ]
                        slot2_bottom      = self.items_slot_2[ item - 1 ]
                        self.setProperty( "slot2_top", slot2_top )
                        self.setProperty( "slot2_middle", slot2_middle )
                        self.setProperty( "slot2_bottom", slot2_bottom )

                    if not self.slot3_stopped:
                        try: slot3_top    = self.items_slot_3[ item + 1 ]
                        except: slot3_top = self.items_slot_3[ 0 ]
                        slot3_middle      = self.items_slot_3[ item ]
                        slot3_bottom      = self.items_slot_3[ item - 1 ]
                        self.setProperty( "slot3_top", slot3_top )
                        self.setProperty( "slot3_middle", slot3_middle )
                        self.setProperty( "slot3_bottom", slot3_bottom )

                    # slots 1, 2 and 3 stopped
                    if self.slot1_stopped and self.slot2_stopped and self.slot3_stopped:
                        self.all_slots_stopped = True
                        break

                    # for debug only if 3 slots is same
                    #if slot1_middle == slot2_middle == slot3_middle:
                    #    self.all_slots_stopped = True
                    #    break

                if not self.all_slots_stopped:
                    if not self.slot1_stopped:
                        self.items_slot_1 = Shuffle( self.items_slot_1 )
                    if not self.slot2_stopped:
                        self.items_slot_2 = Shuffle( self.items_slot_2 )
                    if not self.slot3_stopped:
                        self.items_slot_3 = Shuffle( self.items_slot_3 )
            except:
                print_exc()

        self.set_gain( Gain( slot1_middle, slot2_middle, slot3_middle,
                slot1_top, slot2_top, slot3_top, slot1_bottom, slot2_bottom, slot3_bottom, gui=self ) )

        try:
            if slot1_middle == slot2_middle == slot3_middle:
                if slot1_middle == SEVEN:
                    self.play_SFX( PLAY_7_SFX )
                    xbmc.sleep( 2000 )
                elif slot1_middle == BELL:
                    self.play_SFX( PLAY_BELL_SFX )
                    xbmc.sleep( 4000 )
        except:
            print_exc()

        #xbmc.sleep( 100 )
        self.betting = 0
        self.fill_credits()
        self.is_rolling = False
        self._stop_thread()

    def set_gain( self, slots_infos ):
        #set credits display
        try:
            cash_win = 0
            _jackpot = 0
            if not self.button_2x.isSelected():
                self.cash -= slots_infos.betting
            if slots_infos.win:

                if slots_infos.all_fruits and not slots_infos.gain:
                    self.play_SFX( PLAY_7_SFX )
                    xbmc.sleep( 2000 )

                if slots_infos.all_fruits:
                    self.setProperty( "all_fruits", _( 405 ) )

                if slots_infos.gain:
                    cash_win += slots_infos.gain
                    self.setProperty( "winning", str( cash_win ) )

                if slots_infos.win_jackpot:
                    _jackpot = self.credits[ "jackpot" ]
                    self.setProperty( "jackpot", "" )
                    self.setProperty( "pot_win", str( self.credits[ "jackpot" ] ) )
                    cash_win += self.credits[ "jackpot" ]
                    self.credits[ "jackpot" ] = 0
                self.cash += cash_win
                self.last_win = cash_win

                if slots_infos.win_slots[ 0 ]:
                    self.setProperty( "slot1_win", "true" )
                if slots_infos.win_slots[ 1 ]:
                    self.setProperty( "slot2_win", "true" )
                if slots_infos.win_slots[ 2 ]:
                    self.setProperty( "slot3_win", "true" )

                #Enable and reset bet 2x gain radio button
                self.set_button_2x( 1 )
            else:
                self.last_win = 0
                if self.button_2x.isSelected():
                    slots_infos.betting /= 2
                    self.cash -= slots_infos.betting
                self.credits[ "jackpot" ] += slots_infos.betting
                self.setProperty( "lose", str( slots_infos.betting ) )
                self.setProperty( "jackpot", str( self.credits[ "jackpot" ] ) )

                #Enable and reset bet 2x gain radio button
                self.set_button_2x()

            if slots_infos.win_jackpot:
                #xbmc.executebuiltin( "XBMC.Action(Screenshot)" )
                OK, date_time = self.screenshot()
                if OK: self.dump_winner_jackpot( slots_infos.betting, cash_win, _jackpot, date_time )
            #OK, date_time = self.screenshot()
            #if OK: self.dump_winner_jackpot( slots_infos.betting, cash_win, _jackpot, date_time )
        except:
            print_exc()

    def load_credits( self ):
        test = {}
        self.credits = {}
        defaults = { "jackpot": 0, "last_cash": 0 }
        if os.path.exists( CREDITS_FILE ):
            try:
                f = open( CREDITS_FILE, "rb" )
                test = load( f )
                f.close()
            except:
                print_exc()
                test = {}

        for key, value in defaults.items():
            # add default values for missing settings
            self.credits[ key ] = test.get( key, defaults[ key ] )
        self.save_credits()

        self.cash = 10000
        #demande pour continuer ancienne partie
        if ( self.credits[ "last_cash" ] > 0 ) and xbmcgui.Dialog().yesno(  _( 0 ), _( 5 ) % ( _( 1 ), self.credits[ "last_cash" ] ), _( 6 ), _( 7 ), _( 8 ), _( 9 ) ):
            self.cash = self.credits[ "last_cash" ]
        self.credits[ "last_cash" ] = 0
        self.last_win = 0
        self.betting = 0

    def save_credits( self ):
        try:
            f = open( CREDITS_FILE, "wb" )
            dump( self.credits, f )
            f.close()
        except:
            print_exc()

    def dump_winner_jackpot( self, bet, cash, jackpot, date_time ):
        winners = []
        name = xbmc.getInfoLabel( "System.ProfileName" )#unicode( , 'utf-8')
        thumb = xbmc.getInfoImage( "System.ProfileThumb" )
        if os.path.isfile( WINNER_JACKPOT ):
            try:
                f = open( WINNER_JACKPOT, "rb" )
                winners = load( f )
                f.close()
            except:
                print_exc()
                winners = []
        try:
            winners.append( [ name, thumb, bet, cash, jackpot, date_time ] )
            f = open( WINNER_JACKPOT, "wb" )
            dump( winners, f )
            f.close()
        except:
            print_exc()
        #print winners

    def screenshot( self ):
        xbmc.sleep( 1000 )
        OK = ""
        name = ""
        try: 
            name = str( time.time() )
            # original size
            #filename = name + "-big.jpg"
            W, H = self.getWidth(), self.getHeight()
            #OK = TakeScreenShot( filename, width=W, height=H )
            # thumbs size
            filename = name + ".jpg"
            W, H = 384, ( ( 384 * H ) / W )
            #W, H = 512, ( ( 512 * H ) / W )
            #W, H = int( ( 256 * W ) / H ), 256
            OK = TakeScreenShot( filename, width=W, height=H )
        except:
            print_exc()
        #print OK
        return ( OK == "OK" ), name

    def _show_infos( self ):
        import dialogInfos
        current_skin, force_fallback = getUserSkin()
        try: w = dialogInfos.DialogInfos( "lucky-7-DialogInfos.xml", CWD, current_skin, "PAL", close_game=self._close_game )
        except: w = dialogInfos.DialogInfos( "lucky-7-DialogInfos.xml", CWD, current_skin, force_fallback, close_game=self._close_game )
        w.doModal()
        del w
        del dialogInfos

    def _close_game( self ):
        self._stop_sub_thread()
        self.all_slots_stopped = True
        #self._stop_thread()
        if self.cash > 10000:
            self.credits[ "last_cash" ] = self.cash
        self.cash = 0
        self.save_credits()
        #xbmc.sleep( 100 )
        self.close()


def show_game():
    file_xml = "lucky-7-main.xml"
    dir_path = CWD
    current_skin, force_fallback = getUserSkin()

    #xbmc.enableNavSounds( False )
    try: w = LUCKY7( file_xml, dir_path, current_skin, "PAL" )
    except: w = LUCKY7( file_xml, dir_path, current_skin, force_fallback )
    w.doModal()
    del w
    #xbmc.enableNavSounds( True )
