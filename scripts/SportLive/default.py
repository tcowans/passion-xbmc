# -*- coding: cp1252 -*-

# script constants
__script__       = "Sportlive"
__author__       = "Ppic"
__url__          = "http://code.google.com/p/passion-xbmc/"
__svn_url__      = "http://passion-xbmc.googlecode.com/svn/trunk/scripts/"
__credits__      = "Team XBMC passion, http://passion-xbmc.org/developpement-python/%28script%29-sporlive-display/"
__platform__     = "xbmc media center, [LINUX, OS X, WIN32, XBOX]"
__date__         = "06-03-2009"
__version__      = "1.5.1"
__svn_revision__  = "$Revision: 667 $".replace( "Revision", "" ).strip( "$: " )
__XBMC_Revision__ = "20000" #XBMC Babylon
__useragent__    = "Mozilla/5.0 (Windows; U; Windows NT 5.1; fr; rv:1.9.0.1) Gecko/2008070208 Firefox/3.0.1"



import os
import xbmc
import xbmcgui
from traceback import print_exc

BASE_RESOURCE_PATH = os.path.join( os.getcwd(), "resources" )
GET_LOCALIZED_STRING = xbmc.Language( os.getcwd() ).getLocalizedString

process = os.path.join( BASE_RESOURCE_PATH , "sportlive.pid")
if os.path.exists(process):
    if xbmcgui.Dialog().yesno( GET_LOCALIZED_STRING( 32005 ) , GET_LOCALIZED_STRING( 32006 ) ):
        os.remove(process)        
else:
    file( process , "w" ).write( "" )
    xbmc.executebuiltin('XBMC.RunScript(%s)' % os.path.join( os.getcwd() , "sportlive.py" ))
