
import xbmc, xbmcgui
import os, time, traceback

FILELOG = os.path.join(os.getcwd().rstrip(';'), 'rbc.log')

def printLastError(showoutput, notif=None):
    if notif: xbmc.executebuiltin("XBMC.Notification(Traceback,(most recent call last),1000)")
    try: xbmcgui.DialogProgress().close()
    except: pass
    separator = str('-'.ljust(1)*116)
    try:
        print time.ctime()
        traceback.print_exc()
        print separator
    except: showoutput = None
    else:
        file(FILELOG, 'a').write(time.ctime()+'\n')
        traceback.print_exc(file=open(FILELOG, 'a'))
        file(FILELOG, 'a').write(separator+'\n')
    if showoutput: xbmc.executebuiltin('XBMC.ActivateWindow(scriptsdebuginfo)')
