
#Modules general
import os
import sys
import glob
import time
import random
from marshal import dump, load

#modules XBMC
import xbmc


#NON FRUITS
SEVEN      = "nonfruits/seven.png"     # 3: 1000x | border2: 100x | center1: 10x
BELL       = "nonfruits/bell.png"      # 3: 500x
THREE_BAR  = "nonfruits/three_bar.png" # 3: 300x | ANY | TWO BAR +
TWO_BAR    = "nonfruits/two_bar.png"   # 3: 200x | BAR |  ANY BAR
ONE_BAR    = "nonfruits/one_bar.png"   # 3: 100x | 50x |    25x
XBMC       = "nonfruits/xbmc.png"      # 3: 25x
PASSION    = "nonfruits/passion.png"   # 3: 25x
#FRUITS
CHERRIES   = "fruits/cherries.png"     # 3: 100x | any2: 10x | any1: 1x
WATERMELON = "fruits/Watermelon.png"   # 3: 75x
PEACH      = "fruits/peach.png"        # 3: 75x
COCONUT    = "fruits/coconut.png"      # 3: 50x
KIWI       = "fruits/kiwi.png"         # 3: 25x
BANANA     = "fruits/Banana.png"       # 3: 25x
LIME       = "fruits/lime.png"         # 3: 20x
LEMON      = "fruits/lemon.png"        # 3: 20x
APPLE      = "fruits/apple.png"        # 3: 20x
STRAWBERRY = "fruits/Strawberry.png"   # 3: 15x
ORANGE     = "fruits/Orange.png"       # 3: 10x
ORANGE2    = "fruits/Orange straw.png" # 3: 10x
GRAPES     = "fruits/grapes.png"       # 3: 5x
BLACKBERRY = "fruits/Blackberry.png"   # 3: 5x


CWD = os.getcwd().rstrip( ";" )

# assure compatibility translate path, but use special path
FILE_LUCKY_7_V1   = os.path.join( CWD, "resources", "Lucky7v1", "default_v1.py" )
FILE_KEYMAP_INFOS = os.path.join( CWD, "resources", "KeymapInfos.xml" )

CREDITS_FILE      = xbmc.translatePath( "special://masterprofile/addon_data/%s/credits.db" % sys.modules[ "__main__" ].__addonID__ )
SCREENSHOT_DATA   = xbmc.translatePath( "special://masterprofile/addon_data/%s/ScreenShot/" % sys.modules[ "__main__" ].__addonID__ )
WINNER_JACKPOT    = os.path.join( SCREENSHOT_DATA, "jackpot.txt" )

# if necessary create folder data
if not os.path.isdir( SCREENSHOT_DATA ):
    os.makedirs( SCREENSHOT_DATA )


try:
    """
    getRegion(id) -- Returns your regions setting as a string for the specified id.
    id             : string - id of setting to return
    *Note, choices are (dateshort, datelong, time, meridiem, tempunit, speedunit)
           You can use the above as keywords for arguments and skip certain optional arguments.
           Once you use a keyword, all following arguments require the keyword.
    example:
      - date_long_format = xbmc.getRegion('datelong')
    """
    date_short_format = xbmc.getRegion( "dateshort" ).replace( "MM", "M" ).replace( "DD", "D" ).replace( "M", "%m" ).replace( "D", "%d" ).replace( "YYYYY", "%Y" ).replace( "YYYY", "%Y" )
    time_format = xbmc.getRegion( "time" ).replace( "h", "%I" ).replace( "H", "%H" ).replace( "mm", "%M" ).replace( "ss", "%S" ).replace( "xx", "%p" )
    DATE_TIME_FORMAT = date_short_format + " | " + time_format
except:
    DATE_TIME_FORMAT = "%d-%m-%y | %H:%M:%S"


def TakeScreenShot( filename="", flash=False, rotation=0, width=720, height=576, quality=90 ):
    """
    http://xbmc.org/wiki/?title=WebServerHTTP-API#Action_commands
    Captures the current contents of the XBMC screen.
    If no parameters then the action is the same as initiating a regular screenshot command with the image being saved in the screenshot directory.
    If filename is provided then the image is saved to filename.
    If flash=True the screen will flash as the command executes.
    If resolution, width, height and quality are given then those values are used to define the rotation (in degrees), resolution and jpeg quality of the saved image.
    The command must conform to one of:
    Filename, flash, rotation, width, height, quality 
    """
    if not filename: filename = str( time.time() ) + ".jpg"
    filename = os.path.join( SCREENSHOT_DATA, filename )
    command = "%s;%s;%i;%i;%i;%i" % ( filename, repr( flash ).lower(), rotation, width, height, quality, )
    return xbmc.executehttpapi( "TakeScreenShot(%s)" % ( command, ) ).replace( "<li>", "" )


def wiki_default_controls( controller=0 ):
    extender_remote = "http://wiki.xbmc.org/images/6/6d/Extender_remote_schematics_1_global.jpg"
    xbox_dvd_remote = "http://wiki.xbmc.org/images/4/42/Xbox-dvd-remote-global.jpg"
    xbox_controller = "http://wiki.xbmc.org/images/1/12/Global_Controller.png"
    controller = ( extender_remote, xbox_controller, xbox_dvd_remote )[ controller ]
    return xbmc.executehttpapi( "ShowPicture(%s)" % ( controller, ) ).replace( "<li>", "" )


def Shuffle( list ):
    try:
        shuffle = random.shuffle
    except AttributeError:
        def shuffle( x ):
            for i in xrange( len( x )-1 , 0, -1 ):
                j = int( random.random() * ( i+1 ) )
                x[ i ], x[ j ] = x[ j ], x[ i ]
    shuffle( list )
    return list


def getUserSkin():
    current_skin = xbmc.getSkinDir()
    force_fallback = os.path.exists( os.path.join( CWD, "resources", "skins", current_skin ) )
    if not force_fallback: current_skin = "Default"
    return current_skin, force_fallback


def getSoundsDir():
    current_skin = getUserSkin()[ 0 ]
    sounds_dir = os.path.join( CWD, "resources", "skins", current_skin, "sounds" )
    if not os.path.exists( sounds_dir ) or not os.listdir( sounds_dir ):
        sounds_dir = os.path.join( CWD, "resources", "skins", "Default", "sounds" )
    return sounds_dir


sounds_dir       = getSoundsDir()
PLAY_BELL_SFX    = os.path.join( sounds_dir, "bell.wav" )
PLAY_COIN_SFX    = os.path.join( sounds_dir, "coin.wav" )
PLAY_SPIN_SFX    = os.path.join( sounds_dir, "spin.wav" )
PLAY_STOP_SFX    = os.path.join( sounds_dir, "stop.wav" )
PLAY_7_SFX       = os.path.join( sounds_dir, "seven.wav" )
PLAY_SPINNER_SFX = os.path.join( sounds_dir, "spinner.wav" )


def getFruitsAndNonFruits():
    #default items path
    fruits = os.path.join( CWD, "resources", "skins", "Default", "media", "fruits" )
    nonfruits = os.path.join( CWD, "resources", "skins", "Default", "media", "nonfruits" )

    # items path for non default skin if exists and not empty
    current_skin = getUserSkin()[ 0 ]
    if current_skin != "Default":
        fruits_dir = os.path.join( CWD, "resources", "skins", current_skin, "media", "fruits" )
        nonfruits_dir = os.path.join( CWD, "resources", "skins", current_skin, "media", "nonfruits" )
        if os.path.exists( fruits_dir ) and os.listdir( fruits_dir ):
            fruits = fruits_dir
        if os.path.exists( nonfruits_dir ) and os.listdir( nonfruits_dir ):
            nonfruits = nonfruits_dir

    items = glob.glob( os.path.join( fruits, "*.png" ) ) + glob.glob( os.path.join( nonfruits, "*.png" ) )
    items = [ "/".join( [ os.path.basename( os.path.dirname( f ) ), os.path.basename( f ) ] ) for f in items ]
    extras = Shuffle( [ [], [ THREE_BAR ], [], items, [], [ SEVEN ], [], items, [], [ CHERRIES ], [], items, [], [ BELL ], [] ] )
    extras = random.sample( extras, 3 )
    items_slots = ( items + extras[ 0 ] ), ( items + extras[ 1 ] ), ( items + extras[ 2 ] )
    return items_slots
