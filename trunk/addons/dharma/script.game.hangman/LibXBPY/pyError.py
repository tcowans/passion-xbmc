
#####################################################################################################
''' Module: import '''
#####################################################################################################
import os
import sys
import traceback
from xbmcgui import Dialog
from time import localtime , time

CWD = os.getcwd().rstrip( ";" )

#####################################################################################################
''' Function: Last Error '''
#####################################################################################################
def logLastError():
    year, month, day, hour, minute, second, weekday, yearday, daylight = localtime(time())
    date = "%04d-%02d-%02d | %02d:%02d:%02d" % (year, month, day, hour, minute, second)
    infoType = sys.exc_info()[0]
    infoValue = sys.exc_info()[1]
    infoTB = traceback.extract_tb(sys.exc_info()[2])
    f = open( os.path.join( CWD, "pyLastError.log" ), "a" )
    f.write("Python error in routine of scripts.\n%s\n" % str(date))
    f.write(" Error Type: %s\nError Value: %s\n  Traceback: %s\n" % (str(infoType), str(infoValue), str(infoTB)))
    f.write("====================================================================================================================\n")
    f.close()

def printAndLog_LastError():
    logLastError()
    ei = sys.exc_info()
    Dialog().ok("Error !!!", str(ei[1]))
    traceback.print_exception(ei[0], ei[1], ei[2])
