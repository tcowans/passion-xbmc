"""
ItemInstaller: this module allows download and install an item
"""
import os
import sys
import traceback

# SQLite
from pysqlite2 import dbapi2 as sqlite

#Other module
import urllib
import urllib2, httplib

httplib.HTTPConnection.debuglevel = 1

# Module logger
try:
    logger = sys.modules[ "__main__" ].logger
except:
    import script_log as logger

# Modules custom
#from utilities import *
import CONF


class cancelRequest(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class ItemInstaller:
    """
    ABSTRACT
    """
    
    def __init__( self , itemId, type, installPath, filesize ):
        self.itemId          = itemId       # Id of the server item 
        self.type            = type         # Type of the item
        self.typeInstallPath = installPath  # Install Path for this type of item
        self.filesize        = filesize     # Size of the file to downlaod
        
        self.configManager = CONF.configCtrl()
        if not self.configManager.is_conf_valid: raise
        self.CACHEDIR = self.configManager.CACHEDIR
        
        
    def downloadItem( self, msgFunc=None,progressBar=None ):
        pass

    def installItem( self, msgFunc=None,progressBar=None ):
        pass


