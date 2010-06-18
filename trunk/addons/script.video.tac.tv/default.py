"""
TAC.TV by Temhil (temhil@gmail.com)

Description:
-----------
This script allows to watch videos on www.tac.tv website which I highly recommend. 
Each week a new short video is added. Watch out! Laughing too much can cause belly pain!
If you like and enjoy TAC.tv, please support their creators by visiting their website www.tac.tv and/or buying their DVD(s)

Distribution rights and pictures are property of Salambo productions Inc (www.tac.tv)

History:
-------
26-12-08 Version 2.0 by Temhil
  - Total redesigned UI in order to use WindowXML and all the advantages of it (display using tabs like on the website)
  - Bug fix where picture wasn't displayed picture URL wasn't defined in the XML
  - Download pictures in a separate thread (in case of Mac/Linux it avoid to block the UI while picture are downloaded)

14-11-08 Version 1.0 by Temhil:
  - Renamed script to TAC.TV in order to support English and French user (following what already has been done on the website) 
  - GUI improvement
  - Multilanguages fully supported; on language change, the GUI is updated (text +  icons)
  - Added support ot series, it is possible now to watch only the videos of a specific serie
  - Redesign of Data retrieval: separation of view of model
  - Added support to switch Fr->En and En->Fr even within a serie
  - Created a startup window for selecting language the fisrt time script is run
  - Created 'settings' menu allowing to set-up player, automatic cache cleaning and language at startup
  - Created 'About' menu
  - Prepared the script for WindowXML use (to come)

21-10-08 Version Beta2 by Temhil: 
  - Adaptation of the script after a full update of the website
  - Added English/French support (language and video browsing)
  - Added Series/TV Ads categories
  - Added background picture download 
   (user doesn't have to wait anymore at startup the full retrieval of pictures)
  - Deleted sorting (vote/date) functions: not supported anymore because of changes done on the website

27-04-08 Version Beta1 par Temhil
  - Script creation providing the functionality to watch video on the website:
    www.tetesaclaques.tv (www.tac.tv)
  - Settings support will be provided in the future
  - Pictures are downloaded on the cache directory but are never deleted by the script (will come). 
    The good side of that is script is loading faster! ;-)
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
__date__          = "18-06-2010"
__version__       = "2.0.1"
__svn_revision__  = "$Revision$"

import resources.libs.main as gui


if __name__ == "__main__":
    # Calling startup function
    #show_tac_main_window()
    gui.startup()
else:
    # Library case
    pass
