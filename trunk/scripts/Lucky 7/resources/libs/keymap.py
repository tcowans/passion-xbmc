
#http://xbmc.svn.sourceforge.net/viewvc/xbmc/trunk/XBMC/guilib/Key.h
#http://xbmc.org/wiki/?title=HOW-TO_write_Python_Scripts#Control_Type:_Remote

#7 selectbutton impossible use
#11 infobutton impossible use
#13 stopbutton possible use
SHOW_DIALOG_INFOS  = { 117: "REMOTE_TITLE_BUTTON", 261: "BUTTON_WHITE", 61513: "KEYBOARD_LETTER_I" }

CLOSE_GAME         = { 10: "REMOTE_MENU_BUTTON", 275: "BUTTON_BACK" }
CLOSE_DIALOG       = { 117: "REMOTE_TITLE_BUTTON", 261: "BUTTON_WHITE" }
CLOSE_DIALOG.update( CLOSE_GAME )

ACTION_STOP_SLOTS  = { 3: "REMOTE_UP_BUTTON", 61536: "KEYBOARD_NUM_0" }
ACTION_STOP_SLOTS.update( CLOSE_GAME )

ACTION_STOP_SLOT_1 = { 1: "REMOTE_LEFT_BUTTON", 61537: "KEYBOARD_NUM_1" }
ACTION_STOP_SLOT_2 = { 4: "REMOTE_DOWN_BUTTON", 61538: "KEYBOARD_NUM_2" }
ACTION_STOP_SLOT_3 = { 2: "REMOTE_RIGHT_BUTTON", 61539: "KEYBOARD_NUM_3" }

ACTION_AUTO_SPIN   = { 9: "REMOTE_BACK_BUTTON", 61505: "KEYBOARD_LETTER_A" }
ACTION_START_SPIN  = { 18: "DISPLAY_BUTTON", 258: "BUTTON_X", 61472: "KEYBOARD_SPACEBAR" }#, 61548: "KEYBOARD_NUM_ENTER" }

ACTION_BET_2X_GAIN = { 274: "BUTTON_START", 61544: "KEYBOARD_NUM_*" }

ACTION_BET_MAX     = { 12: "REMOTE_PAUSE_BUTTON", 260: "BUTTON_BLACK", 61517: "KEYBOARD_LETTER_M" }

ACTION_BET_UP      = { 14: "REMOTE_SKIP+_BUTTON", 259: "BUTTON_Y", 61473: "KEYBOARD_PAGE_UP" }
ACTION_BET_DOWN    = { 15: "REMOTE_SKIP-_BUTTON", 257: "BUTTON_B", 61474: "KEYBOARD_PAGE_DOWN" }


class ActionDict( dict ):
    """ customized dict, don't raise KeyError exception, return None instead """
    def __getitem__( self, action ):
        if hasattr( action, "getId" ) and hasattr( action, "getButtonCode" ):
            key = action.getId()
            if self.has_key( key  ):
                return dict.__getitem__( self, key  )
            else:
                key = action.getButtonCode()
                if self.has_key( key  ):
                    return dict.__getitem__( self, key )
        return None


class Keymap( dict ):
    """ customized dict, don't raise KeyError exception, return None instead """
    def __init__( self ):
        self[ "close_game" ]         = self.set_action_keys( CLOSE_GAME )
        self[ "close_dialog" ]       = self.set_action_keys( CLOSE_DIALOG )
        self[ "show_dialog_infos" ]  = self.set_action_keys( SHOW_DIALOG_INFOS )
        self[ "action_stop_slots" ]  = self.set_action_keys( ACTION_STOP_SLOTS )
        self[ "action_stop_slot_1" ] = self.set_action_keys( ACTION_STOP_SLOT_1 )
        self[ "action_stop_slot_2" ] = self.set_action_keys( ACTION_STOP_SLOT_2 )
        self[ "action_stop_slot_3" ] = self.set_action_keys( ACTION_STOP_SLOT_3 )
        self[ "action_auto_spin" ]   = self.set_action_keys( ACTION_AUTO_SPIN )
        self[ "action_start_spin" ]  = self.set_action_keys( ACTION_START_SPIN )
        self[ "action_bet_max" ]     = self.set_action_keys( ACTION_BET_MAX )
        self[ "action_bet_up" ]      = self.set_action_keys( ACTION_BET_UP )
        self[ "action_bet_down" ]    = self.set_action_keys( ACTION_BET_DOWN )
        self[ "action_bet_2x_gain" ] = self.set_action_keys( ACTION_BET_2X_GAIN )

    def set_action_keys( self, keys ):
        action = ActionDict()
        action.update( keys )
        return action

    def __getitem__( self, key ):
        key = key.lower()
        if self.has_key( key ):
            return  dict.__getitem__( self, key )
        return ActionDict()



if __name__ == "__main__":
    KEYMAP = Keymap()
    print KEYMAP[ 'close_game' ][ 12 ]
    print KEYMAP[ 'close_dialog' ][ 9 ]
    print KEYMAP
