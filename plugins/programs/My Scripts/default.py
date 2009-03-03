"""A simple shortcut for view window scripts from program plugins
"""


# script constants
__script__       = "My Scripts (shortcut)"
__author__       = "Temhil"
__url__          = "http://code.google.com/p/passion-xbmc/"
__svn_url__      = "http://passion-xbmc.googlecode.com/svn/trunk/plugins/programs/"
__credits__      = "Team XBMC, http://xbmc.org/"
__platform__     = "xbmc media center"
__date__         = "02-02-2008"
__version__      = "1.0"
__svn_revision__ = "N/A"


from xbmc import executebuiltin
executebuiltin( "XBMC.ActivateWindow(10020,)" )
