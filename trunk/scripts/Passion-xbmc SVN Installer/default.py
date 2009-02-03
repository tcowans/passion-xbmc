"""
    Plugin for downloading scripts/plugins/skins from SVN repositories
"""

# main imports
import sys

# plugin constants
__plugin__ = "Passion-xbmc SVN Installer"
__author__ = "nuka1195"
__url__ = "http://code.google.com/p/passion-xbmc/"
__svn_url__ = "http://passion-xbmc.googlecode.com/svn/trunk/plugins/programs/Passion-xbmc%20SVN%20Installer"
__credits__ = "Team XBMC"
__version__ = "1.3.1"


if ( __name__ == "__main__" ):
    if ( "download_url=" in sys.argv[ 2 ] ):
        from installerAPI import xbmcplugin_downloader as plugin
    else:
        from installerAPI import xbmcplugin_list as plugin
    plugin.Main()
