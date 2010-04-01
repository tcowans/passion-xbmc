import os
import xbmcgui
import shutil
dialog2 = xbmcgui.Dialog()
cache = os.path.join( os.getcwd(), "cache")
if os.path.exists(cache): 
    shutil.rmtree(cache)
    message = "suppress ok"
else: message = "no cache found"
dialog2.ok("Cache Suppression" , message)
