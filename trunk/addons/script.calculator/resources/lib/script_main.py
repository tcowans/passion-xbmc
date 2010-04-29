
#####################################################################################################
''' Module: import '''
#####################################################################################################
import os
import sys
import math
import traceback

import xbmc
import xbmcgui

from operator import __neg__
from cmath import pi as __PI__
from marshal import dump, load


CWD = os.getcwd().rstrip( ";" )
LANGUAGE = xbmc.Language( CWD ).getLocalizedString

#####################################################################################################
''' Function: Skin '''
#####################################################################################################
def getUserSkin():
    current_skin = xbmc.getSkinDir()
    force_fallback = os.path.exists( os.path.join( CWD, "resources", "skins", current_skin ) )
    if not force_fallback: current_skin = "Default"
    return current_skin, force_fallback

CURRENT_SKIN, FORCE_FALLBACK = getUserSkin()

#####################################################################################################
''' Function: keymapping '''
#####################################################################################################
class KEYMAPPING( dict ):
    def __init__( self ):
        """ self[ button_id ] = ( skin_control_id=101, keyboard_id=61000, standard_id=9, ) """

        self[ "exp" ]          = ( 101, )
        self[ "square" ]       = ( 102, )
        self[ "pi" ]           = ( 103, )
        self[ "m_plus" ]       = ( 104, )
        self[ "m_moins" ]      = ( 105, )
        self[ "m_read_clean" ] = ( 106, )
        self[ "close" ]        = ( 107, 61467, )#10,
        self[ "x_y" ]          = ( 108, )
        self[ "percent" ]      = ( 109, )
        self[ "#7" ]           = ( 110, 61543, )
        self[ "#8" ]           = ( 111, 61544, )
        self[ "#9" ]           = ( 112, 61545, )
        self[ "div" ]          = ( 113, 61631, )
        self[ "clean" ]        = ( 114, 61486, )#117,
        self[ "x_2" ]          = ( 115, )
        self[ "1_x" ]          = ( 123, )
        self[ "#4" ]           = ( 117, 61540, )
        self[ "#5" ]           = ( 118, 61541, )
        self[ "#6" ]           = ( 119, 61542, )
        self[ "*" ]            = ( 120, )
        self[ "back" ]         = ( 121, 34, )
        self[ "x_3" ]          = ( 122, )
        self[ "fifty_fifty" ]  = ( 116, )
        self[ "#1" ]           = ( 124, 61537, )
        self[ "#2" ]           = ( 125, 61538, )
        self[ "#3" ]           = ( 126, 61539, )
        self[ "-" ]            = ( 127, 61629, )
        self[ "Clear_entry" ]  = ( 128, 61448, 9, )
        self[ "Plus_Moins" ]   = ( 129, )
        self[ "#0" ]           = ( 130, 61536, )
        self[ "point" ]        = ( 131, 61630, )
        self[ "+" ]            = ( 132, 61627, )
        self[ "equal" ]        = ( 133, 18, )#61548, 

#####################################################################################################
''' Class: Principal '''
#####################################################################################################
class CALC( xbmcgui.WindowXMLDialog ):
    KEYMAP = KEYMAPPING().items()

    def __init__( self, *args, **kwargs ):
        self.first    = ""
        self.second   = ""
        self.action   = ""
        self.def_nbre = str( 0 )
        self.m_read_clean = False
        self.tmp_file = os.path.join( CWD, "memory.mrc" )
        self.Load_tmp()

    def onInit( self ):
        self.set_label()
        self.set_button_label()

    def set_label( self ):
        self.getControl( 1 ).setLabel( LANGUAGE( 32000 ) )
        if not self.mrc[ "MRC" ]:
            self.getControl( 23 ).setLabel( "" )
        elif "-" in self.mrc[ "MRC" ]:
            self.getControl( 23 ).setLabel( LANGUAGE( 32015 ) )
        else: self.getControl( 23 ).setLabel( LANGUAGE( 32014 ) )

    def set_button_label( self ):
        btn_lbl = [
            ( 101, 11 ), ( 104, 14 ), ( 105, 15 ), ( 106, 16 ), ( 108, 17 ), ( 109, 18 ), ( 110, 8 ),
            ( 111, 9 ), ( 112, 10 ), ( 113, 19 ), ( 114, 20 ), ( 115, 21 ), ( 116, 22 ), ( 117, 5 ), ( 118, 6 ),
            ( 119, 7 ), ( 120, 23 ), ( 121, 24 ), ( 122, 25 ), ( 123, 26 ), ( 124, 2 ), ( 125, 3 ),  ( 126, 4 ),
            ( 127, 27 ), ( 129, 29 ), ( 130, 1 ), ( 131, 30 ), ( 132, 31 ), ( 133, 32 ),
            #( 102, 12 ), ( 103, 13 ), ( 107, 33 ), ( 128, 28 ),
            ]
        for btn, lbl in btn_lbl:
            self.getControl( btn ).setLabel( LANGUAGE( 32000 + lbl ) )

    def onFocus( self, controlID ): pass

    def onClick( self, controlID ):
        try:
            self.action_click( controlID )
        except:
            traceback.print_exc()
            #xbmc.executebuiltin( "XBMC.ActivateWindow(scriptsdebuginfo)" )

    def onAction( self, action ):
        try:
            self.action_click( action.getButtonCode() )
        except:
            traceback.print_exc()
            #xbmc.executebuiltin( "XBMC.ActivateWindow(scriptsdebuginfo)" )

    def action_click( self, action_click_id ):
        CLOSE = False
        for key, value in self.KEYMAP:
            if action_click_id in value:
                if   key == "exp": self.Get_exp()
                elif key == "square": self.Get_square()
                elif key == "pi": self.Get_pi()
                elif key == "m_plus": self.Set_m_plus()
                elif key == "m_moins": self.Set_m_moins()
                elif key == "m_read_clean": self.Get_m_read_clean()
                elif key == "close": CLOSE = True
                elif key == "x_y": self.Get_x_ala_y()
                elif key == "percent": self.Get_Pourcentage()
                elif key == "#7": self.Get_value( str( 7 ) )
                elif key == "#8": self.Get_value( str( 8 ) )
                elif key == "#9": self.Get_value( str( 9 ) )
                elif key == "div": self.Get_operator( "/" )
                elif key == "clean": self.Set_clean()
                elif key == "x_2": self.Get_x_ala_2()
                elif key == "1_x": self.Get_1_x()
                elif key == "#4": self.Get_value( str( 4 ) )
                elif key == "#5": self.Get_value( str( 5 ) )
                elif key == "#6": self.Get_value( str( 6 ) )
                elif key == "*": self.Get_operator( "*" )
                elif key == "back": self.Set_back()
                elif key == "x_3": self.Get_x_ala_3()
                elif key == "fifty_fifty": self.Get_fifty_fifty()
                elif key == "#1": self.Get_value( str( 1 ) )
                elif key == "#2": self.Get_value( str( 2 ) )
                elif key == "#3": self.Get_value( str( 3 ) )
                elif key == "-": self.Get_operator( "-" )
                elif key == "Clear_entry": self.Clear_entry()
                elif key == "Plus_Moins": self.Get_Plus_Moins()
                elif key == "#0": self.Get_value( str( 0 ) )
                elif key == "point": self.Get_point()
                elif key == "+": self.Get_operator( "+" )
                elif key == "equal": self.Get_equal()
                #print key, action_click_id
                break
        if CLOSE: self.close()

    def Load_tmp( self ):
        test = { "action_tmp":"", "MRC":"" }
        self.mrc = {}
        try:
            if os.path.exists( self.tmp_file ):
                f = open( self.tmp_file, "rb" )
                self.mrc = load( f )
                f.close()
        except:
            traceback.print_exc()
        for k in test.keys():
            if not self.mrc.has_key( k ): self.mrc[ k ] = test[ k ]

    def Save_tmp( self ):
        try:
            f = open( self.tmp_file, "wb" )
            dump( self.mrc, f )
            f.close()
        except:
            traceback.print_exc()

    def Get_exp( self ):
        if self.action == "":
            if not self.first == "":
                if not "e+" in self.first:
                    if not "e-" in self.first:
                        self.first = str( self.first + "e+" )
                        self.getControl( 20 ).setLabel( self.first )
                        self.getControl( 21 ).setLabel( LANGUAGE( 32011 ) )
        elif not self.second == "":
            if not "e+" in self.second:
                if not "e-" in self.second:
                    self.second = str( self.second + "e+" )
                    self.getControl( 20 ).setLabel( self.second )
                    self.getControl( 21 ).setLabel( LANGUAGE( 32011 ) )
        self.m_read_clean = False

    def Get_square( self ):
        if self.action == "":
            if not self.first == "":
                self.first = str( math.sqrt( float( self.first ) ) )
                self.getControl( 20 ).setLabel( self.first )
                self.getControl( 21 ).setLabel( LANGUAGE( 32012 ) )
        elif not self.second == "":
            self.second = str( math.sqrt( float( self.second ) ) )
            self.getControl( 20 ).setLabel( self.second )
            self.getControl( 21 ).setLabel( LANGUAGE( 32012 ) )
        self.m_read_clean = False

    def Get_pi( self ):
        if self.action == "":
            self.first = str( float( __PI__ ) )
            self.getControl( 20 ).setLabel( self.first )
            self.getControl( 21 ).setLabel( LANGUAGE( 32113 ) )
        else:
            self.second = str( float( __PI__ ) )
            self.getControl( 20 ).setLabel( self.second )
            self.getControl( 21 ).setLabel( LANGUAGE( 32113 ) )
        self.m_read_clean = False

    def Get_x_ala_y( self ):
        if self.action == "":
            if not self.first == "":
                if not "**" in self.first:
                    self.first = str( self.first + "**" )
                    self.getControl( 20 ).setLabel( self.first )
                    self.getControl( 21 ).setLabel( LANGUAGE( 32017 ) )
        elif not self.second == "":
            if not "**" in self.second:
                self.second = str( self.second + "**" )
                self.getControl( 20 ).setLabel( self.second )
                self.getControl( 21 ).setLabel( LANGUAGE( 32017 ) )
        self.m_read_clean = False

    def Get_Pourcentage( self ):
        if not self.action == "":
            if not self.second == "":
                self.second = str( float( self.second )/100.00 )
                self.getControl( 20 ).setLabel( self.second )
                self.getControl( 21 ).setLabel( LANGUAGE( 32018 ) )
                self.Get_equal()
        elif not self.first == "":
            self.first = str( float( self.first )/100.00 )
            self.getControl( 20 ).setLabel( self.first )
            self.getControl( 21 ).setLabel( LANGUAGE( 32018 ) )
        self.m_read_clean = False

    def Set_clean( self ):
        self.first  = ""
        self.second = ""
        self.action = ""
        self.m_read_clean = False
        self.getControl( 21 ).setLabel( "" )
        self.getControl( 22 ).setLabel( "" )
        self.getControl( 20 ).setLabel( self.def_nbre )

    def Get_x_ala_2( self ):
        if self.action == "":
            if not self.first == "":
                self.first = str( math.pow( float( self.first ), 2 ) )
                self.getControl( 20 ).setLabel( self.first )
                self.getControl( 21 ).setLabel( LANGUAGE( 32021 ) )
        elif not self.second == "":
            self.second = str( math.pow( float( self.second ), 2 ) )
            self.getControl( 20 ).setLabel( self.second )
            self.getControl( 21 ).setLabel( LANGUAGE( 32021 ) )
        self.m_read_clean = False

    def Get_fifty_fifty( self ):
        if not self.action == "":
            if not self.second == "":
                self.second = str( float( self.second )/2.0 )
                self.getControl( 20 ).setLabel( self.second )
                self.getControl( 21 ).setLabel( LANGUAGE( 32022 ) )
                self.Get_equal()
        elif not self.first == "":
            self.first = str( float( self.first )/2.0 )
            self.getControl( 20 ).setLabel( self.first )
            self.getControl( 21 ).setLabel( LANGUAGE( 32022 ) )
        self.m_read_clean = False

    def Set_back( self ):
        if self.action == "":
            self.first  = ""
            self.getControl( 21 ).setLabel( "" )
        elif self.second == "":
            self.first    = ""
            self.action   = ""
            self.getControl( 21 ).setLabel( "" )
        else: self.second = ""
        self.m_read_clean = False
        self.getControl( 20 ).setLabel( self.def_nbre )

    def Get_x_ala_3( self ):
        if self.action == "":
            if not self.first == "":
                self.first = str( math.pow( float( self.first ), 3 ) )
                self.getControl( 20 ).setLabel( self.first )
                self.getControl( 21 ).setLabel( LANGUAGE( 32025 ) )
        elif not self.second == "":
            self.second = str( math.pow( float( self.second ), 3 ) )
            self.getControl( 20 ).setLabel( self.second )
            self.getControl( 21 ).setLabel( LANGUAGE( 32025 ) )
        self.m_read_clean = False

    def Get_1_x( self ):
        if self.action == "":
            if not self.first == "":
                self.first = str( math.fabs( 1/float( self.first ) ) )
                self.getControl( 20 ).setLabel( self.first )
                self.getControl( 21 ).setLabel( LANGUAGE( 32026 ) )
        elif not self.second == "":
            self.second = str( math.fabs( 1/float( self.second ) ) )
            self.getControl( 20 ).setLabel( self.second )
            self.getControl( 21 ).setLabel( LANGUAGE( 32026 ) )
        self.m_read_clean = False

    def Clear_entry( self ):
        if self.action == "":
            if not self.first == "":
                for e in range( len( self.first ) ):
                    infoexp = str( self.first[ e ] )
                if infoexp == "+": self.first = self.first[ :-2 ]
                elif infoexp == "-": self.first = self.first[ :-2 ]
                else: self.first = self.first[ :-1 ]
                self.getControl( 20 ).setLabel( self.first )
        elif not self.action == "":
            if self.second == "":
                self.action = ""
                self.getControl( 22 ).setLabel( "" )
            else:
                for e in range( len( self.second ) ):
                    infoexp = str( self.second[ e ] )
                if infoexp == "+": self.second = self.second[ :-2 ]
                elif infoexp == "-": self.second = self.second[ :-2 ]
                else: self.second = self.second[ :-1 ]
                self.getControl( 20 ).setLabel( self.second )
        self.m_read_clean = False

    def check_exp( self, Value ):
        t = Value.split( "e" )
        if "." in t[ 0 ]: t1 = str( __neg__( float( t[ 0 ] ) ) )
        else: t1 = str( __neg__( float( t[ 0 ] ) ) )[ :-2 ]
        Value = str( t1 + "e" + t[ 1 ] )
        return Value

    def Get_Plus_Moins( self ):
        if self.action == "":
            if not self.first == "":
                if "e+" in self.first: self.first = self.check_exp( self.first )
                elif "e-" in self.first: self.first = self.check_exp( self.first )
                else: self.first = str( __neg__( float( self.first ) ) )
                self.getControl( 20 ).setLabel( self.first )
        elif not self.second == "":
            if "e+" in self.second: self.second = self.check_exp( self.second )
            elif "e-" in self.second: self.second = self.check_exp( self.second )
            else: self.second = str( __neg__( float( self.second ) ) )
            self.getControl( 20 ).setLabel( self.second )
        self.m_read_clean = False

    def Get_point( self ):
        if self.action == "":
            if self.first == "": self.first = "0."
            elif "." in self.first: pass
            else: self.first = self.first + "."
            self.getControl( 20 ).setLabel( self.first )
            return
        elif self.second == "": self.second = "0."
        elif "." in self.second: pass
        else: self.second = self.second + "."
        self.getControl( 20 ).setLabel( self.second )
        self.m_read_clean = False

    def Get_value( self, nbre ):
        if self.first == "":
            self.first = nbre
            self.getControl( 20 ).setLabel( self.first )
        elif self.action == "":
            if len( self.first ) > 30:
                self.getControl( 22 ).setLabel( LANGUAGE( 32035 ) )
                return
            self.first = self.first + nbre
            self.getControl( 20 ).setLabel( self.first )
        elif self.second == "":
            self.second = nbre
            self.getControl( 20 ).setLabel( self.second )
        else:
            if len( self.second ) > 30:
                self.getControl( 22 ).setLabel( LANGUAGE( 32035 ) )
                return
            self.second = self.second + nbre
            self.getControl( 20 ).setLabel( self.second )
        self.m_read_clean = False

    def Get_operator( self, Ope ):
        if self.first == "":
            if Ope == "-": self.first = "-"
            self.getControl( 20 ).setLabel( self.first )
        elif self.second == "":
            if self.action == "":
                self.action = Ope
                self.getControl( 22 ).setLabel( Ope.replace( "/", LANGUAGE( 32019 ) ).replace( "*", LANGUAGE( 32023 ) ) )
            elif Ope == "-": self.second = "-"
        else: 
            result = self.Get_equal()
            if result:# != ERR:
                try: self.getControl( 20 ).setLabel( result )
                except:
                    traceback.print_exc()
                    self.action = Ope
        self.m_read_clean = False

    def Get_power( self, Power ):
        #xy    = Power.split( "**" )
        #value = math.pow( float( xy[ 0 ] ), float( xy[ 1 ] ) )
        x, y  = Power.split( "**" )
        value = math.pow( float( x ), float( y ) )
        return str( value )

    def Get_equal( self ):
        try:
            if self.second == "": self.second = self.first
            if self.action == "": self.action = self.mrc[ "action_tmp" ]
            if "**" in self.first:  self.first  = self.Get_power( self.first )
            if "**" in self.second: self.second = self.Get_power( self.second )
            result = str( eval( str( float( self.first ) ) + self.action + str( float( self.second ) ) ) )
            self.mrc[ "action_tmp" ] = self.action
            self.Save_tmp()
            self.action = ""
            if len( self.first ) + len( self.second ) > 28: Split = "\n"
            else: Split = " "
            label_Operations = str( self.first + " " + self.mrc[ "action_tmp" ] + Split + self.second + " " + "=" )
            print "- Operations: %s %s" % ( label_Operations, result, )
            label_Operations = label_Operations.replace( "/", LANGUAGE( 32019 ) ).replace( "*", LANGUAGE( 32023 ) )
            self.getControl( 22 ).setLabel( label_Operations )
            self.second = ""
            self.first  = result
            self.action = ""
            self.getControl( 20 ).setLabel( self.first )
            if "e+" in self.first: self.getControl( 21 ).setLabel( LANGUAGE( 32011 ) )
            elif "e-" in self.first: self.getControl( 21 ).setLabel( LANGUAGE( 32011 ) )
            return result
        except:
            result      = ""
            self.first  = ""
            self.second = ""
            self.action = ""
            self.getControl( 21 ).setLabel( "" )
            self.getControl( 22 ).setLabel( "" )
            self.getControl( 20 ).setLabel( LANGUAGE( 32034 ) )
            traceback.print_exc()
            return result
        self.m_read_clean = False

    def Set_m_plus( self ):
        if self.first == "": return
        elif not self.action == "": 
            if self.second == "": return
        if self.action == "": entry = self.first
        else: entry = self.second
        if "-" in entry: str( __neg__( float( entry ) ) )
        self.mrc[ "MRC" ] = entry
        f = open( self.tmp_file, "wb" )
        dump( self.mrc, f )
        f.close()
        self.getControl( 23 ).setLabel( LANGUAGE( 32014 ) )
        self.m_read_clean = False

    def Set_m_moins( self ):
        if self.first == "": return
        elif not self.action == "": 
            if self.second == "": return
        if self.action == "": entry = self.first
        else: entry = self.second
        self.mrc[ "MRC" ] = str( __neg__( float( entry ) ) )
        f = open( self.tmp_file, "wb" )
        dump( self.mrc, f )
        f.close()
        self.getControl( 23 ).setLabel( LANGUAGE( 32015 ) )
        self.m_read_clean = False

    def Get_m_read_clean( self ):
        test = { "MRC":"" }
        self.mrc = {}
        if os.path.exists( self.tmp_file ):
            f = open( self.tmp_file, "rb" )
            self.mrc = load( f )
            f.close()
        for k in test.keys():
            if not self.mrc.has_key( k ): self.mrc[ k ] = test[ k ]
        if not self.m_read_clean:
            if self.action == "":
                self.first = self.mrc[ "MRC" ]
                self.getControl( 20 ).setLabel( self.first )
            else:
                self.second = self.mrc[ "MRC" ]
                self.getControl( 20 ).setLabel( self.second )
            if "-" in self.mrc[ "MRC" ]: self.getControl( 23 ).setLabel( LANGUAGE( 32015 ) )
            elif ( not self.first == "" ) or ( not self.second == "" ):
                self.getControl( 23 ).setLabel( LANGUAGE( 32014 ) )
            #elif not self.second == "": self.getControl( 23 ).setLabel( LANGUAGE( 32014 ) )
        else:
            self.mrc[ "MRC" ] = ""
            f = open( self.tmp_file, "wb" )
            dump( self.mrc, f )
            f.close()
            self.getControl( 23 ).setLabel( self.mrc[ "MRC" ] )
            if not self.second == "": setlabel = self.second
            elif not self.first == "": setlabel = self.first
            else: setlabel = self.def_nbre
            self.getControl( 20 ).setLabel( setlabel )
        self.m_read_clean = True

#####################################################################################################
''' Starter: Script OR import Custom Module '''
#####################################################################################################
#if __name__ == "__main__":
def Main():
    try:
        file_xml = "DialogCalculator.xml"
        dir_path = CWD #xbmc.translatePath( os.path.join( CWD, "resources" ) )
        w = CALC( file_xml, dir_path, CURRENT_SKIN, FORCE_FALLBACK )
        w.doModal()
        del w
    except:
        traceback.print_exc()
        #xbmc.executebuiltin( "XBMC.ActivateWindow(scriptsdebuginfo)" )
