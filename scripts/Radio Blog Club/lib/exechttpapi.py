# -*- coding: utf-8 -*-

import xbmc, xbmcgui
import os, sys, urllib
import xml.dom.minidom

DEFAULTAUDIO = 'defaultAudio.png'
DEFAULTAUDIOBIG = 'defaultAudioBig.png'

TEMPDEST = 'z:\\temp.jpg'

language = sys.modules["__main__"].__language__
printLastError = sys.modules["__main__"].printLastError

DIALOG_PROGRESS = xbmcgui.DialogProgress()

def hasWebServer():
    webserver = False
    xmlfile = 'P:\\guisettings.xml'
    if os.path.isfile(xmlfile):
        doc = xml.dom.minidom.parse(xmlfile)
        root = doc.documentElement
        if not root or root.tagName != "settings": return webserver
        for itag in root.getElementsByTagName("webserver"):
            if itag.hasChildNodes():
                b = itag.firstChild.nodeValue
                if (b in 'false|true')&(b == 'true'):
                    webserver = True
    return webserver

def requestOnAllMusic_Com(albumname, popup=True):
    listname, listurl = [], []
    try: os.unlink('z:\\temp.jpg')
    except: pass
    try:
        if hasWebServer():
            DIALOG_PROGRESS.create(xbmc.getLocalizedString(185),  xbmc.getLocalizedString(501))
            albumname = albumname.replace(' ', '%20')
            lookupalbum = xbmc.executehttpapi('LookupAlbum(%s)' % (albumname, ))
            if not '<li>Error:' in lookupalbum:
                lookupalbum = lookupalbum.replace('<li>', '').split('\n')
                try: lookupalbum.remove('')
                except: pass
                for item in [x.split('<@@>') for x in lookupalbum]:
                    if len(item) == 2:
                        listname.append(item[0]); listurl.append(item[1])
                #file('Q:\\musicinfo.txt', 'w').write(str(listname)+'\n'); file('Q:\\musicinfo.txt', 'a').write(str(listurl)+'\n\n')
                DIALOG_PROGRESS.close()
                selected = xbmcgui.Dialog().select(xbmc.getLocalizedString(181), listname)
                xbmc.sleep(200)
                if selected != -1:
                    DIALOG_PROGRESS.create(xbmc.getLocalizedString(13351),  xbmc.getLocalizedString(20097))
                    choosealbum = xbmc.executehttpapi('ChooseAlbum(%s)' % (listurl[selected], ))
                    if not '<li>Error:' in choosealbum:
                        choosealbum = choosealbum.replace('<li>', '').split('\n')
                        try: choosealbum.remove('')
                        except: pass
                        imageUrl = choosealbum[0].split('image:')[1]
                        reviewtext = choosealbum[1].split('review:')[1]
                        if (imageUrl != TEMPDEST)&(imageUrl != '')&(TEMPDEST != ''):
                            try: urllib.urlretrieve(imageUrl, TEMPDEST)
                            except: printLastError(False)
                        #file('Q:\\musicinfo.txt', 'a').write('urltbn = '+str(imageUrl)+'\n'); file('Q:\\musicinfo.txt', 'a').write('text = '+str(reviewtext)+'\n')
                        DIALOG_PROGRESS.close()
                        return TEMPDEST, reviewtext
                    #else: print str(choosealbum)
            #else: print str(lookupalbum)
            DIALOG_PROGRESS.close()
            xbmcgui.Dialog().ok(language(106), xbmc.getLocalizedString(500))
        else:
            if popup: xbmcgui.Dialog().ok(language(106), language(107), language(108), language(109))
            print 'no web for requestOnAllMusic_Com'
    except: printLastError(False)
    return None, None

#if __name__ == "__main__":
#    keyboard = xbmc.Keyboard('dio - holy driver', xbmc.getLocalizedString(16011))
#    keyboard.doModal()
#    if keyboard.isConfirmed():
#        img, text = requestOnAllMusic_Com(str(keyboard.getText()))
#        if img: xbmc.executehttpapi("ShowPicture(%s)" % (img, ))
#        if text: print str(text)


def getTagFromFilename(filename, popup=True):
    alltag = {}
    try:
        if hasWebServer():
            tag = xbmc.executehttpapi("GetTagFromFilename(%s)" % filename).replace('<li>', '').split('\n')
            for x in tag:
                iTag = x.split(':')
                if len(iTag) == 2: alltag.update({iTag[0].lower(): iTag[1]})
                if (len(iTag) == 3)&(iTag[0] == 'Thumb'): alltag.update({iTag[0].lower(): '%s:%s' % (iTag[1], iTag[2])})
            #tranform duration seconde at 00:00
            ts = alltag.get('duration')
            if ts:
                min = str(int(ts)/60)
                sec = str(int(ts)-(int(min)*60))
                if int(sec) <= 9: sec = '0'+sec
                alltag['duration'] = '%s:%s' % (min, sec)
        else:
            if popup: xbmcgui.Dialog().ok(language(106), language(107), language(108), language(109))
            print 'no web for getTagFromFilename'
        # if not thumb or not exists: set DEFAULTAUDIO
        tbn = None
        try:
            defauttbn = filename.replace('.mp3','.tbn').replace('.MP3','.tbn')
            if os.path.isfile(defauttbn): tbn = defauttbn
        except: pass
        if not tbn:
            defauttbn = alltag.get('thumb', '')
            if os.path.isfile(defauttbn): tbn = defauttbn
        if not tbn: alltag['thumb'] = DEFAULTAUDIOBIG
        else: alltag['thumb'] = tbn
    except:
        printLastError(False)
        alltag['error'] = 'Traceback,(most recent call last)'
    if alltag == {}: alltag['error'] = 'Not know error!'
    return alltag

#if __name__ == "__main__":
#    mp3 = xbmcgui.Dialog().browse(1, 'Browse for GetTagFromFilename', "files", ".mp3")
#    if mp3:
#        allTag = getTagFromFilename(mp3)
#        print str(allTag)
