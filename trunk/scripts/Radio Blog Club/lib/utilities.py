# -*- coding: utf-8 -*-

import xbmc, xbmcgui
import os, string, sys

QUERY_KEY = '&k='+'657ecb3231ac0b275497d4d6f00b61a1'

DEFAULTAUDIO = 'defaultAudio.png'
DEFAULTAUDIOBIG = 'defaultAudioBig.png'

CWD = os.getcwd().rstrip(';')

HISTORYDATA = os.path.join(CWD, 'historyData')
USERDATA    = os.path.join(CWD, 'userdata.rbc')
RECUPINFOS  = os.path.join(CWD, 'recupinfo.txt')

printLastError = sys.modules["__main__"].printLastError

DIALOG_PROGRESS = xbmcgui.DialogProgress()

def getUserSkin():
    current_skin = xbmc.getSkinDir()
    if not os.path.exists(os.path.join(CWD, "resources", 'skins', current_skin)): current_skin = 'Default'
    return current_skin

def compatibleFatX(s, dels=None):
    nofatx = "*,/;?|¿+<=>±«»×÷¢£¤¥§©¬®°µ¶·€¼½¾¹²³ªáÁàÀâÂäÄãÃåÅæÆçÇðÐéÉèÈêÊëËíÍìÌîÎïÏñÑºóÓòÒôÔöÖõÕøØßþÞúÚùÙûÛüÜýÝ"
    fatx   = "____________________________________aAaAaAaAaAaAaAcC_DeEeEeEeEiIiIiIiInN_oOoOoOoOoOoOs__uUuUuUuUyY"
    table = string.maketrans(nofatx, fatx)
    if dels: dels = nofatx
    s = string.translate(s, table, deletions=dels)#[:38]
    return s

def cleanFileName(text):
    result = string.replace(text, ":", "_")
    result = string.replace(result, "&amp;", "&")
    result = string.replace(result, "amp;", "")
    result = string.replace(result, "[", "(")
    result = string.replace(result, "]", ")")
    result = string.replace(result, ";", "_")
    result = string.replace(result, ", ", "_")
    result = string.replace(result, "\n", " ")
    return result

def hookFunc(cpt_blk, taille_blk, total_taille):
    try: updt_val = ((taille_blk * cpt_blk) * 100.0 / total_taille)
    except ZeroDivisionError: updt_val = 100
    if updt_val > 100: updt_val = 100
    DIALOG_PROGRESS.update(int(updt_val))
    if DIALOG_PROGRESS.iscanceled(): raise

def reportSearch(nb, totalsongs):
    """Print a progress bar during the research"""
    nb = max ( nb, 0 )
    try: p = ( float ( 100 * ( totalsongs - nb ) ) / totalsongs )
    except ZeroDivisionError: p = 100.0
    DIALOG_PROGRESS.update(int(p))

def searchSongs(artistMusic, listlimit=0):
    import rbc_lib
    try:
        # 25000 est la maximun pour xbox. La cause low memory :o
        limit = int(listlimit)
        if limit <= 0: limit = 25000
    except: limit = 25000
    allinfos = {}
    index = 0
    try:
        rbcl = rbc_lib.rbc_lib( maxresults=limit )
        rbcl._keepresults_ = {}
        n = rbcl.searchArtistMusic( artistMusic, True, report_search=reportSearch )
        if n:
            #file(RECUPINFOS, 'a').write(str(rbcl._keepresults_)+'\n')
            list = rbcl._keepresults_.values()[0]
            list.sort(key=lambda f: (f[1].lower().strip()))
            for val in list:
                allinfos[int(index)] = { 'url' : val[0], 'title' : val[1] }
                index += 1
            #file(RECUPINFOS, 'a').write(str(allinfos)+'\n')
        #else: print 'no song found'
    except: printLastError(False)
    del rbc_lib
    return allinfos
