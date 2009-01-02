"""A simple shortcut for view window program plugins
"""


# script constants
__script__       = "My Program Plugins (shortcut)"
__author__       = "Frost"
__url__          = "http://code.google.com/p/passion-xbmc/"
__svn_url__      = "http://passion-xbmc.googlecode.com/svn/trunk/scripts/"
__credits__      = "Team XBMC, http://xbmc.org/"
__platform__     = "xbmc media center"
__date__         = "27-12-2008"
__version__      = "1.0"
__svn_revision__ = "N/A"


from xbmc import executebuiltin
executebuiltin( "XBMC.ActivateWindow(10001,plugin://programs/)" )
