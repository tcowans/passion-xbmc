# -*- coding: utf-8 -*-
import sys
if sys.modules.has_key("cplusplus"):
    del sys.modules['cplusplus']
import cplusplus as cpp

import xbmc#,xbmcgui,xbmcplugin

import os,os.path
ROOTDIR = os.getcwd().replace(';','')
DOWNLOADDIR = os.path.join(ROOTDIR,"downloads")

if __name__=="__main__":
    try:
        url=sys.argv[1]
        filename=sys.argv[2]
    except Exception,msg:
        xbmc.executebuiltin("XBMC.Notification(%s,%s)"%("Erreur de téléchargement",msg))
        sys.exit("ERROR : FLVdownload usage :\n\tFLVdownload.py url filename")
    xbmc.executebuiltin("XBMC.Notification(%s,%s)"%("Lancement du téléchargement...",""))
    goDL = cpp.DL_video(url,
                        os.path.join(DOWNLOADDIR,xbmc.makeLegalFilename(filename))
                        )
    if goDL==1:
        xbmc.executebuiltin("XBMC.Notification(%s,%s)"%("Téléchargement terminé !",os.path.join(DOWNLOADDIR,xbmc.makeLegalFilename(filename))))
    elif goDL == 0:
        xbmc.executebuiltin("XBMC.Notification(%s,%s)"%("Fichier existant !","Téléchargement annulé."))
    elif goDL == -1:
        xbmc.executebuiltin("XBMC.Notification(%s,%s)"%("Telechargement annulé par l'utilisateur.",""))

