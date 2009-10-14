"""
PassionHttpBrowser: this module allows browsing of server content on the FTP server of Passion-XBMC.org
"""


# Modules general
import os
import sys
import traceback

# Module logger
try:
    logger = sys.modules[ "__main__" ].logger
except:
    import script_log as logger
    
# SQLite
from pysqlite2 import dbapi2 as sqlite

#Other module
from threading import Thread
from pil_util import makeThumbnails
#import urllib

# Modules custom
from utilities import *
from Browser import Browser, ImageQueueElement
import ItemInstaller  


    
class PassionFtpBrowser(Browser):
    """
    Browser FTP server using FTP command and display information about item stored in the database
    """
    def __init__(self):
        pass
    
    