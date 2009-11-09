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
import Item

class cancelRequest(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class ItemInstaller:
    """
    ABSTRACT
    """
    
    #def __init__( self , itemId, type, installPath, filesize ):
    def __init__( self , itemId, type, filesize ):
        self.itemId          = itemId       # Id of the server item 
        self.type            = type         # Type of the item
        #self.typeInstallPath = installPath  # Install Path for this type of item
        self.typeInstallPath = Item.get_install_path( type )  # Install Path for this type of item
        self.filesize        = filesize     # Size of the file to download
        
        self.configManager = CONF.configCtrl()
        if not self.configManager.is_conf_valid: raise
        self.CACHEDIR = self.configManager.CACHEDIR
        
        
    def downloadItem( self, msgFunc=None,progressBar=None ):
        """
        Download an item form the server
        """
        pass

    def isAlreadyInstalled( self ):
        """
        Check if extracted item is already installed
        Needs to be called after extractItem
        """
        pass

    def installItem( self, msgFunc=None,progressBar=None ):
        """
        Install item (download + extract + copy)
        Needs to be called after extractItem
        """
        pass


