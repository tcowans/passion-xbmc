"""
TAC.TV by Temhil (temhil@gmail.com)

Description:
-----------
This script allows to watch videos on www.tac.tv website which I highly recommend. 
Each week a new short video is added. Watch out! Laughing too much can cause belly pain!
If you like and enjoy TAC.tv, please support their creators by visiting their website www.tac.tv and/or buying their DVD(s)

Distribution rights and pictures are property of Salambo productions Inc (www.tac.tv)
"""


############################################################################
# script constants
############################################################################
__script__        = "TAC.TV"
__addonID__       = "script.video.tac.tv"
__author__        = "Temhil"
__url__           = "http://code.google.com/p/passion-xbmc/"
__svn_url__       = "http://passion-xbmc.googlecode.com/svn/trunk/addons/script.video.tac.tv/"
__credits__       = "Team XBMC Passion"
__platform__      = "xbmc media center, [ALL]"
__date__          = "08-04-2012"
__version__       = "2.0.3"
__svn_revision__  = "$Revision$"

import resources.libs.main as gui


if __name__ == "__main__":
    # Calling startup function
    #show_tac_main_window()
    gui.startup()
else:
    # Library case
    pass
