"""
   Simulating xbmcaddon library for XBox
"""



__script__       = "Addons4xbox Installer"
__plugin__       = "Unknown"
#__author__       = authorUI + " and " + authorCore
__author__       = "Frost / Temhil - http://passion-xbmc.org"
__url__          = "http://passion-xbmc.org/index.php"
__svn_url__      = "http://passion-xbmc.googlecode.com/svn/trunk/scripts/Addons4xbox%20Installer/"
__credits__      = "Team XBMC Passion"
__platform__     = "xbmc media center"
__date__         = "12-10-2010"
__version__      = "1.0"
__svn_revision__ = 0


import os
import xbmc
import xbmcgui
import traceback

ROOTDIR = os.getcwd()
__platform__ = "xbmc media center, [%s]" % xbmc.__platform__
__language__ = xbmc.Language( ROOTDIR ).getLocalizedString


if  __name__ == "__main__":
    dialogYesNo = xbmcgui.Dialog()
    if ( dialogYesNo.yesno( __language__(30000), __language__(30003) ) ):
        try:
            import xbmcaddon
            dialog = xbmcgui.Dialog()
            dialog.ok( __language__(30000), __language__(30002) )
            print "XBMC4XBOX Addon Library already installed"
        except ImportError:
            lib_xbmcaddon = "special://xbmc/system/python/Lib/xbmcaddon.py"
            lib_source = os.path.join( ROOTDIR, "resources", "libs", "xbmcaddon.py" )
            dialogProg = xbmcgui.DialogProgress()
            dialogProg.create( __language__( 30000 ) ) 
            dialogProg.update(0, __language__ ( 30001 ) )
            try: os.mkdirs( "special://xbmc/system/python/Lib" )
            except: pass
            try:
                xbmc.executehttpapi( "FileCopy(%s,%s)" % ( lib_source, lib_xbmcaddon ) )
                dialogProg.update(100, __language__ ( 30001 ) )
                dialogProg.close()
                dialog = xbmcgui.Dialog()
                dialog.ok( __language__(30000), __language__(30005) )
                print "SUCCESS: xbmcaddon.py copied to special://xbmc/system/python/Lib/xbmcaddon.py"
            except:
                dialogProg.close()
                dialog = xbmcgui.Dialog()
                dialog.ok( __language__(30000), __language__(30006), __language__(30007) )
                print "ERROR: impossible to copy xbmcaddon.py to special://xbmc/system/python/Lib/xbmcaddon.py"
                traceback.print_exc()
    else:
        dialog = xbmcgui.Dialog()
        dialog.ok( __language__(30000), __language__(30004) )
        

