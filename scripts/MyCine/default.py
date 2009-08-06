import urllib, os

import sys
sys.path.insert( 0, os.path.join( os.getcwd().replace(';',''), "Image_Lib" ) )

HOME=os.getcwd().replace(';','') + os.sep
UPDATER_FILE_NAME="MyCineUpdater.py"
UPDATE_URL="http://netbourse.free.fr/xbmc/MyCine/"

#try:
#    if os.path.isfile(HOME+UPDATER_FILE_NAME) == False:
#        urllib.urlretrieve(UPDATE_URL+UPDATER_FILE_NAME,HOME+UPDATER_FILE_NAME)
#    import MyCineUpdater
#    MyCineUpdater.update()
#except:
#   pass

import MyCine85
MyCine85.start()
