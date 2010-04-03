"""
Le Video Blog d'Alain Carrazé Video by Temhil (temhil@gmail.com)
 
04-03-09 Version 1.2 by Temhil
    - Update algorithm in order to retrieve each entry in the blog, including 'text only' one
    - Made the code more generic in order to use it for other Canalplus blogs
    - Added Series Express videos category (end of the menu)
    - Added video infos on video playing
    - Fixed thread that wouldn't stop until finished (not very elegant but it works)
    - Improved display info speed and update list image it not yet updated by the thread
    - Changed default setting to cache images, this improve performance for displaying list
    - Display video infos + thumb in player

24-11-08 Version 1.1 by Temhil
    - Fixed crash on video info since html code is not always identical depending
      on the entry
    - Created regex for getting comment on video (not used yet)

18-10-08 Version 1.0 by Temhil
    - Created info window for videos
    - Fixed regex after changes on the website
    - Major update of the UI
    - Replaced regex by beautiful soup for the XML processing

26-04-08 Version Beta1 by Temhil
    - Creation

Les droits des diffusions et des images utilisées sont exclusivement
réservés à Canal+ 

"""



############################################################################
# Script constants
############################################################################
__script__ = "Blog A. Carraze"
__script_title__ = "Le Blog d'Alain Carrazé"
__plugin__ = "Unknown"
__author__ = "Temhil"
__url__ = ""
__svn_url__ = "http://code.google.com/p/passion-xbmc/source/browse/#svn/trunk/scripts/Blog%20A.%20Carraze"
__credits__ = "Temhil"
__platform__ = "xbmc media center"
__date__ = "04-03-09"
__version__ = "1.2"
__svn_revision__ = 0

#from resources.libs.specialpath import *
import resources.libs.gui as gui

if __name__ == "__main__":
    # Calling startup function
    gui.startup()
else:
    # Library case
    pass
