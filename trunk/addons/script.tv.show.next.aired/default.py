
__script__       = "TV-Show Next-Aired"
__author__       = "Ppic, Frost"
__url__          = "http://code.google.com/p/passion-xbmc/"
__svn_url__      = ""
__credits__      = "Team Passion-XBMC, http://passion-xbmc.org/"
__platform__     = "xbmc media center, [ALL, without XBox]"
__date__         = "07-07-2010"
__version__      = "1.0.0"
__svn_revision__  = "$Revision$"


import os
import sys
from traceback import print_exc


RESOURCES_PATH = os.path.join( os.getcwd() , "resources" )
sys.path.append( os.path.join( RESOURCES_PATH, "lib" ) )


try:
    from scraper import getDetails
    import next_aired_dialog
    next_aired_list = getDetails()
    next_aired_dialog.MyDialog(next_aired_list)
    print "### Exiting ... "
except:
    print_exc()
