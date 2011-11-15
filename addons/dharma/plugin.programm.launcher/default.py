"""
    Plugin for Launching programs
"""

# main imports
import sys
import os

# plugin constants
__plugin__ = "Launcher"
__author__ = "CinPoU,leo212"
__url__ = ""
__svn_url__ = ""
__credits__ = "Lior Tamam"
__version__ = "1.5"


if ( __name__ == "__main__" ):
    import resources.lib.launcher_plugin as plugin
    plugin.Main()
sys.modules.clear()
