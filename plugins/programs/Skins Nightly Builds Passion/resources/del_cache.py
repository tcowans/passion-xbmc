import os
import xbmcgui
import shutil
import sys

print "suppression de %s" % sys.argv[1]
message = "error"
if sys.argv[1] == "cache":
    cache = os.path.join( os.getcwd(), "cache")
    if os.path.exists(cache): 
        shutil.rmtree(cache)
        message = "suppress ok"
        message2 = ""
    else: message = "no cache found"
elif sys.argv[1] == "skin":
    skinpath = sys.argv[2]
    print "chemin de skin: %s" % skinpath
    if os.path.exists(skinpath):
        shutil.rmtree(skinpath)
        message = "suppress ok"
        message2 = sys.argv[2]
    else: 
        message = "Directory not exist"
        message2 = sys.argv[2]
dialog2 = xbmcgui.Dialog()   
dialog2.ok("%s Suppression" % sys.argv[1] , message)
