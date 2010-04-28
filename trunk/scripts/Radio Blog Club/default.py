# -*- coding: utf-8 -*-

__author__    = '''FrostBox'''
__credits__   = '''nioc.bertheloneum <nioc.bertheloneum@gmail.com> for new rbc_lib'''
__date__      = '''28-12-2008'''
__platform1__ = '''XBMC on XBox, RUN default.py'''
__platform2__ = '''Multi linux/win..., RUN rbc_lib.py via/with command line'''
__title__     = '''Radio.blog.club'''
__version__   = '''2.1.1b'''

import xbmc, xbmcgui
import marshal, os, re
import sys, string
from collections import deque
CWD = os.getcwd().rstrip(';')
sys.path.append(os.path.join(CWD, "lib"))
from mostrecentcalllast import printLastError
import downloader
from utilities import *
import language
__language__ = language.Language().localized
import exechttpapi, rbc_lib


DIALOG_PROGRESS = xbmcgui.DialogProgress()


class GUI(xbmcgui.WindowXML):
    def __init__(self, *args, **kwargs):
        self.actionID = 7
        self.loadUserPreset()
        self.isMyBlog = False
        self.onInitIsStarted = False
        self.currentTitle = self.userPreset['currentTitle']
        self.query_key = self.userPreset['query_key']
        self.fullInfos = historyData(selected=self.currentTitle.replace(' - ', '')).loadData()
        self.selectedItem = 0
        self.lastSelected = self.selectedItem

    def onInit(self):
        if not self.onInitIsStarted:
            self.getControl(14).setLabel(__language__(1))
            self.getControl(6).setLabel(__language__(2))
            if self.fullInfos and self.fullInfos != {}:
                self.addItemsInControlList()
            else:
                self.setFocus(self.getControl(6))
                self.showHistory()
                if self.fullInfos == {}:
                    self.setFocus(self.getControl(5))
                    self.searchOnRBC()
                if self.fullInfos == {}: self.close()
        self.onInitIsStarted = True

    def onFocus(self, controlID): pass

    def onClick(self, controlID):
        self.onClickContextMenu(controlID)
        xbmc.sleep(100) # Added for onAction keep info of self.actionID, before execution of the controllist in onClick.
        try:
            if   controlID == 14: self.getMyBlog()
            elif controlID ==  9: self.playAllItems()
            elif controlID ==  5: self.searchOnRBC()
            elif controlID ==  6: self.showHistory()
            elif controlID == 15: self.settings()
            elif (50 <= controlID <= 59)&(self.actionID == 7):
                self.playItem()
                if xbmc.Player().isPlaying(): self.selItemList()
        except:
            printLastError(False)
            self.selItemList(0)

    def onClickContextMenu(self, controlID):
        try:
            # a mettre ds un fichier python et ne plus mettre en skin.settings(...) avec skin.reset(...), il a trop de dialog busy :P
            if (1000 <= controlID <= 1005) and (controlID != 1004):
                xbmc.executebuiltin('Skin.SetString(rbcdcontextmenu,0)')
                if controlID == 1005: self.playItem()
                elif controlID == 1000: self.musicInfo()
                elif controlID == 1001: self.renameItem()
                elif controlID == 1002: self.moveItem()
                elif controlID == 1003: self.deleteItem()
                self.setFocus(self.getControl(51))
        except:
            xbmc.executebuiltin('Skin.SetString(rbcdcontextmenu,0)')
            self.setFocus(self.getControl(14))
            printLastError(False)

    def onAction(self, action):
        self.actionID = action.getId()

        # a mettre ds un fichier python et ne plus mettre en skin.settings(...) avec skin.reset(...), il a trop de dialog busy :P
        if (action in (9, 10, 117)) and (xbmc.getCondVisibility("Skin.String(rbcdcontextmenu,1)")):
            xbmc.executebuiltin('Skin.SetString(rbcdcontextmenu,0)')
            self.setFocus(self.getControl(51))
            self.selItemList(0)
        elif (action == 117) and (xbmc.getCondVisibility("Skin.String(rbcdcontextmenu,0)")):
            self.selItemList()
            xbmc.executebuiltin('Skin.SetString(rbcdcontextmenu,1)')
            self.setFocus(self.getControl(2))
            self.getControl(1000).setEnabled(exechttpapi.hasWebServer())
            self.getControl(1001).setEnabled(self.isMyBlog)
            self.getControl(1002).setEnabled(self.isMyBlog)
            self.getControl(1003).setEnabled(self.isMyBlog)
        elif action == 34: xbmc.executebuiltin('Skin.ToggleSetting(rbcdrecorder)')
        elif action == 10:
            self.saveUserPreset()
            self.close()

    def addItemsInControlList(self):
        self.getControl(21).setLabel(__language__(0) + self.currentTitle.upper())
        xbmc.sleep(200)
        try:
            itemsInfos = self.fullInfos.values()
            self.clearList()
            for value in itemsInfos:
                if (value == {})|(value is None): continue
                self.addItem(
                    xbmcgui.ListItem(
                        cleanFileName(value.get('title', xbmc.getLocalizedString(13205))),
                        value.get('duration', ''),
                        value.get('ico', DEFAULTAUDIO),
                        value.get('icoBig', DEFAULTAUDIOBIG)
                        )
                    )
        except:
            printLastError(False, True)
            self.setFocus(self.getControl(5))
            #self.searchOnRBC()
            #self.close()

    def renameItem(self):
        position = self.getCurrentListPosition()
        itemInfos = self.fullInfos.get(position)
        if not itemInfos: return
        url = itemInfos.get('url')
        #title = itemInfos.get('title')
        keyboard = xbmc.Keyboard(os.path.basename(url), xbmc.getLocalizedString(16013))
        keyboard.doModal()
        if keyboard.isConfirmed():
            new = keyboard.getText()
            try:
                self.fullInfos[position]['url'] = url.replace(os.path.basename(url), new)
                self.fullInfos[position]['title'] = new
                os.rename(url, url.replace(os.path.basename(url), new))
                try:
                    cover = url.replace('.mp3', '.tbn').replace('.MP3', '.tbn')
                    newcovername = cover.replace(os.path.basename(cover), new.replace('.mp3', '.tbn').replace('.MP3', '.tbn'))
                    os.rename(cover, newcovername)
                    self.fullInfos[position]['ico'] = newcovername
                    self.fullInfos[position]['icoBig'] = newcovername
                except: printLastError(False)
            except:
                xbmcgui.Dialog().ok(xbmc.getLocalizedString(257), __language__(27), __language__(26), __language__(28))
                printLastError(False)
            else:
                self.addItemsInControlList()
                self.setCurrentListPosition(position)

    def moveItem(self):
        position = self.getCurrentListPosition()
        itemInfos = self.fullInfos.get(position)
        if not itemInfos: return
        url = itemInfos.get('url')
        #title = itemInfos.get('title', '')
        browse = xbmcgui.Dialog().browse(3, xbmc.getLocalizedString(20328), "files", '', False, False, os.path.dirname(url))
        if browse and browse != os.path.dirname(url):
            if xbmcgui.Dialog().yesno(xbmc.getLocalizedString(121), xbmc.getLocalizedString(124), os.path.basename(url), 'To : '+browse):
                import shutil
                try:
                    shutil.move(url, os.path.join(browse, os.path.basename(url)))
                    try:
                        cover = url.replace('.mp3', '.tbn').replace('.MP3', '.tbn')
                        shutil.move(cover, os.path.join(browse, os.path.basename(cover)))
                    except: pass
                    self.delPosInDict(position)
                except:
                    xbmcgui.Dialog().ok(xbmc.getLocalizedString(16203), xbmc.getLocalizedString(16204), __language__(26))
                    printLastError(False)
                else:
                    #self.addItemsInControlList()
                    self.removeItem(position)
                del shutil

    def deleteItem(self):
        position = self.getCurrentListPosition()
        itemInfos = self.fullInfos.get(position)
        if not itemInfos: return
        url = itemInfos.get('url')
        #title = itemInfos.get('title', '')
        if xbmcgui.Dialog().yesno(xbmc.getLocalizedString(122), xbmc.getLocalizedString(125), os.path.basename(url)):
            try:
                os.unlink(url)
                try: os.unlink(url.replace('.mp3', '.tbn').replace('.MP3', '.tbn'))
                except: pass
                self.delPosInDict(position)
            except:
                xbmcgui.Dialog().ok(xbmc.getLocalizedString(16205), xbmc.getLocalizedString(16206), __language__(26))
                printLastError(False)
            else:
                #self.addItemsInControlList()
                self.removeItem(position)

    def delPosInDict(self, pos):
        if self.fullInfos.get(pos):
            del self.fullInfos[pos]
            tmp = self.fullInfos
            #file(RECUPINFOS, 'a').write(str(tmp)+'\n')
            self.fullInfos = {}
            index = 0
            for k in tmp.keys():
                self.fullInfos[int(index)] = tmp[k]
                index += 1
            #file(RECUPINFOS, 'a').write(str(self.fullInfos)+'\n')

    def searchOnRBC(self):
        try:
            keyboard = xbmc.Keyboard('', __language__(10))
            keyboard.doModal()
            if keyboard.isConfirmed():
                usersearch = keyboard.getText()
                refreshsearch = True
                if os.path.isfile(os.path.join(HISTORYDATA, str(usersearch)+'.his')):
                    refreshsearch = xbmcgui.Dialog().yesno(__language__(6) % str(usersearch), __language__(7), __language__(4), '', xbmc.getLocalizedString(12018), xbmc.getLocalizedString(184))
                if refreshsearch:
                    DIALOG_PROGRESS.create(__language__(0), __language__(11) % str(usersearch), __language__(12), '')
                    search = usersearch
                    listlimit = int(self.userPreset.get('listlimit', '00'))
                    allinfos = searchSongs(search, listlimit)
                    DIALOG_PROGRESS.close()
                else: allinfos = historyData(selected=str(usersearch).replace(' - ', '')).loadData()
                if allinfos is not None and allinfos != {}:
                    if refreshsearch: historyData(selected=str(usersearch), dict=allinfos).saveData()
                    self.fullInfos = allinfos
                    self.userPreset['currentTitle'] = ' - '+usersearch
                    self.saveUserPreset()
                    self.currentTitle = self.userPreset['currentTitle']
                    self.addItemsInControlList()
                else:
                    xbmcgui.Dialog().ok(xbmc.getLocalizedString(257), __language__(0), xbmc.getLocalizedString(16031))
        except: printLastError(False)
        self.isMyBlog = False

    def setNameLimit(self, name):
        if len(name) > 42:
            while True:
                cutname = os.path.splitext(name)
                n = cleanFileName(cutname[0])
                n = compatibleFatX(n)
                keyboard = xbmc.Keyboard(n, __language__(15))
                keyboard.doModal()
                if keyboard.isConfirmed():
                    newname = keyboard.getText()
                    if len(newname) > 38: continue
                    name = newname+".mp3"
                break
        name = cleanFileName(name)
        name = compatibleFatX(name)
        return name

    def playItem(self):
        try:
            position = self.getCurrentListPosition()
            itemInfos = self.fullInfos.get(position)
            if not itemInfos: return
            url = itemInfos.get('url')
            title = itemInfos.get('title')
            if not os.path.isfile(url): url += self.query_key
            xbmc.PlayList(0).clear()# added xbmc semble jouer la playliste. apres l'item??
            if xbmc.getCondVisibility("Skin.HasSetting(rbcdrecorder)") and not self.isMyBlog:
                localitem = self.retrieveItem(url, title)
                if os.path.isfile(localitem):
                    url = localitem
            if url: xbmc.Player().play(url)
        except: printLastError(False)

    def retrieveItem(self, url, title):
        try:
            destination = self.getDirRecorder()
            if not destination: return url
            freespace = xbmc.getInfoLabel('System.Freespace(%s)' % (str(destination.split(':')[0]).upper(), ))
            if 100 >= int(freespace.split()[1]): xbmcgui.Dialog().ok(__language__(8), __language__(9), freespace)
            title = self.setNameLimit(title)
            normdir = os.path.join(destination, self.currentTitle.replace(' - ', ''))
            if not os.path.exists(normdir):
                try:
                    os.makedirs(normdir)
                    destination = normdir
                except: pass
            else: destination = normdir
            pathdest = os.path.splitext(os.path.join(destination, title))[0]+'.mp3'
            if not os.path.exists(pathdest):
                DIALOG_PROGRESS.create(__language__(0), __language__(20), pathdest, __language__(12))
                try:
                    #pb = DIALOG_PROGRESS.update
                    dl = downloader.Download(url.replace(' ','%20'), pathdest, progressbar=DIALOG_PROGRESS.update)
                    dl.start()
                    while not dl.stop:
                        if DIALOG_PROGRESS.iscanceled():
                            dl.abort()
                            break
                    success = dl.SUCCESS
                    del dl
                except:
                    printLastError(False)
                    success = False, None
                DIALOG_PROGRESS.close()
                if success[0] and success[1]:
                    if os.path.isfile(success[1]):
                        try:
                            if (os.path.getsize(success[1]) < 10000): os.unlink(success[1])
                        except: printLastError(False)
                    if os.path.isfile(success[1]): url = success[1]
            else: url = pathdest
        except: printLastError(False)
        return url

    def playAllItems(self):
        playmode = xbmcgui.Dialog().yesno(xbmc.getLocalizedString(559), __language__(25), '', '', xbmc.getLocalizedString(21385), xbmc.getLocalizedString(208))
        xbmc.PlayList(0).clear()
        for val in self.fullInfos.values():
            url = val['url']
            if not os.path.isfile(url): url += self.query_key
            xbmc.PlayList(0).add(url, cleanFileName(val['title']))
        if not playmode: xbmc.executebuiltin('XBMC.ActivateWindow(mymusicplaylist)')
        else: xbmc.Player().play(xbmc.PlayList(0)); xbmc.executebuiltin('XBMC.ActivateWindow(visualisation)')

    def getDirRecorder(self):
        userdir = self.userPreset['userdir']
        browse = None
        if (userdir is None) or (not os.path.isdir(userdir)):
            browse = xbmcgui.Dialog().browse(3, "Recordings folder", "files")
        if browse:
            self.userPreset["userdir"] = str(browse)
            self.saveUserPreset()
            userdir = self.userPreset['userdir']
        return userdir

    def setDirRecorder(self):
        userdir = self.userPreset['userdir']
        browse = xbmcgui.Dialog().browse(3, "Recordings folder", "files")
        if browse:
            self.userPreset["userdir"] = str(browse)
            self.saveUserPreset()
            userdir = self.userPreset['userdir']
        return userdir

    def getMyBlog(self):
        allinfos = {}
        index = 0
        mp3Re = re.compile("[.]*.mp3")
        userdir = self.getDirRecorder()
        listlimit = int(self.userPreset.get('listlimit', '00'))
        if listlimit <= 0: listlimit = 50000
        if os.path.exists(userdir):
            DIALOG_PROGRESS.create(__language__(1), __language__(13), __language__(12), '')
            for root, dirs, files in os.walk(userdir, topdown=False):
                if DIALOG_PROGRESS.iscanceled() or index == listlimit: break
                pct = 0
                try: diff = (100.0/len(files))
                except ZeroDivisionError: diff = 100
                files.sort(key=lambda f: f.lower())
                for name in files:
                    fullName = os.path.join(root, name)
                    if mp3Re.search(fullName.lower()) != None:
                        title = ''
                        tagsmp3 = exechttpapi.getTagFromFilename(fullName, False)
                        track = tagsmp3.get('track number')
                        if track:
                            if int(track) <= 9: track = '0'+track
                            if int(track) == 0: track = None
                            if track: title += track + '. '
                        artist = tagsmp3.get('artist')
                        if artist: title += artist + ' - '
                        tagtitle = tagsmp3.get('title')
                        if tagtitle and not tagtitle == '': title += tagtitle
                        else: title += name
                        allinfos[index] = {'url': fullName, 'title': title, 'duration': tagsmp3.get('duration', ''),
                            'ico': str(tagsmp3.get('thumb', DEFAULTAUDIO)).replace('Big.png', '.png'),
                            'icoBig': tagsmp3.get('thumb', DEFAULTAUDIOBIG)}
                        index += 1
                    pct += diff
                    if pct >= 100: pct = 100
                    DIALOG_PROGRESS.update(int(pct), __language__(13), str(fullName), __language__(12))
                    if DIALOG_PROGRESS.iscanceled() or index == listlimit: break
                if DIALOG_PROGRESS.iscanceled() or index == listlimit: break
            DIALOG_PROGRESS.update(100)
            DIALOG_PROGRESS.close()
        if allinfos != {}:
            self.fullInfos = allinfos
            self.userPreset['currentTitle'] = ' - ' + __language__(1)
            self.saveUserPreset()
            self.currentTitle = self.userPreset['currentTitle']
            self.addItemsInControlList()
            self.isMyBlog = True
        else:
            xbmcgui.Dialog().ok(xbmc.getLocalizedString(257), xbmc.getLocalizedString(1025))

    def showHistory(self):
        list = []
        if os.path.isdir(HISTORYDATA):
            try:
                history = os.listdir(HISTORYDATA)
                if len(history) >= 1:
                    history = [os.path.splitext(f)[0] for f in history]
                    history.sort(key=lambda f: f.lower())
                    list = history
            except: printLastError(False)
        if list != []:
            list.append(__language__(29))
            selected = xbmcgui.Dialog().select(__language__(2), list)
            if selected != -1:
                if list[selected] == __language__(29):
                    list = list[:-1]
                    list.append(__language__(31))
                    selected = xbmcgui.Dialog().select(__language__(30), list)
                    if selected != -1:
                        if list[selected] == __language__(31):
                            import shutil
                            try: shutil.rmtree(HISTORYDATA)
                            except: printLastError(False)
                            del shutil
                        else:
                            try: os.unlink( os.path.join(HISTORYDATA, list[selected]+'.his'))
                            except: printLastError(False)
                        if not os.path.isdir(HISTORYDATA): os.makedirs(HISTORYDATA)
                else:
                    usersearch = list[selected]
                    refreshsearch = xbmcgui.Dialog().yesno(xbmc.getLocalizedString(184), __language__(4), __language__(5) % (str(usersearch), ), '', xbmc.getLocalizedString(12018), xbmc.getLocalizedString(184))
                    if refreshsearch:
                        DIALOG_PROGRESS.create(__language__(0), __language__(11) % str(usersearch), __language__(12), '')
                        search = usersearch
                        listlimit = int(self.userPreset.get('listlimit', '00'))
                        allinfos = searchSongs(search, listlimit)
                        DIALOG_PROGRESS.close()
                    else: allinfos = historyData(selected=str(usersearch).replace(' - ', '')).loadData()
                    if allinfos is not None and allinfos != {}:
                        if refreshsearch: historyData(selected=str(usersearch), dict=allinfos).saveData()
                        self.fullInfos = allinfos
                        self.userPreset['currentTitle'] = ' - '+usersearch
                        self.saveUserPreset()
                        self.currentTitle = self.userPreset['currentTitle']
                        self.addItemsInControlList()
                    else:
                        xbmcgui.Dialog().ok(xbmc.getLocalizedString(257), __language__(0), xbmc.getLocalizedString(16031))
                self.isMyBlog = False

    def settings(self):
        try:
            set = settings("SettingsSkin.xml", CWD, getUserSkin(), 1, win=self)
            set.doModal()
            del set
        except: printLastError(False)

    def musicInfo(self):
        try:
            position = self.getCurrentListPosition()
            itemInfos = self.fullInfos.get(position)
            if not itemInfos: return
            url = itemInfos.get('url')
            title = itemInfos.get('title')
            if url and title:
                title = self.setNameLimit(title)
                amc = allMusic_com("DialogMusicInfoSkin.xml", CWD, getUserSkin(), 1, dest=url, albumname=title)
                amc.doModal()
                tbn = amc.newTBN
                del amc
                if tbn: self.setNewTbn(tbn)
        except: printLastError(False)

    def setNewTbn(self, tbn):
        try:
            position = self.getCurrentListPosition()
            self.getListItem(position).setIconImage( tbn )
            self.getListItem(position).setThumbnailImage( tbn )
        except: printLastError(False)

    def selItemList(self, nosel=1):
        try:
            self.selectedItem = self.getCurrentListPosition()
            lastitem = self.getListItem(int(self.lastSelected))
            if lastitem.isSelected(): lastitem.select(0)
            newitem = self.getListItem(int(self.selectedItem))
            newitem.select(int(nosel))
            self.lastSelected = self.selectedItem
        except:
            printLastError(False)
            self.selectedItem = 0
            self.lastSelected = self.selectedItem

    def loadUserPreset(self):
        self.userPreset = {}
        test = {'userdir': None, 'currentTitle': '', 'listlimit': '00', 'query_key': QUERY_KEY}
        if os.path.exists(USERDATA):
            f = open(USERDATA, "rb")
            self.userPreset = marshal.load(f)
            f.close()
        for k in test.keys():
            if not self.userPreset.has_key(k): self.userPreset[k] = test[k]

    def saveUserPreset(self):
        f = open(USERDATA, "wb")
        marshal.dump(self.userPreset, f)
        f.close()

LIMIT = ['00', '10', '25', '50', '100', '250', '500', '1000']
LISTLIMIT = deque(LIMIT)

class settings(xbmcgui.WindowXML):
    def __init__(self, *args, **kwargs):
        self.win = kwargs['win']
        self.userdir = self.win.userPreset.get('userdir', '')
        self.listlimit = self.win.userPreset.get('listlimit', '00')
        self.query_key = self.win.userPreset.get('query_key', __language__(68))

    def onInit(self):
        self.getControl(260).setLabel(self.query_key)
        self.getControl(200).setLabel(__language__(60))
        self.getControl(240).setLabel(__language__(61))
        self.getControl(25).setLabel(__language__(62))
        self.setupControls()

    def setupControls(self):
        if self.userdir != '': self.getControl(210).setLabel(self.userdir, "font13", "0xffffffff")
        else: self.getControl(210).setLabel(xbmc.getLocalizedString(20078), "font13", "0x60ffffff")
        try:
            if not LISTLIMIT[0] == self.listlimit: LISTLIMIT.rotate(-(int(LIMIT.index(self.listlimit))+1))
            limit = LISTLIMIT[0]
            if limit == '00': limit = xbmc.getLocalizedString(21428)
            else: limit = xbmc.getLocalizedString(21436) % (int(limit), )
            self.getControl(250).setLabel('%s' % (limit, ))
        except:
            self.getControl(250).setLabel(xbmc.getLocalizedString(21428))

    def onFocus(self, controlID): pass

    def onClick(self, controlID):
        try:
            if controlID == 14:
                self.win.userPreset['userdir'] = ''
                self.win.userPreset['listlimit'] = '00'
                self.win.saveUserPreset()
                self.userdir = self.win.userPreset.get('userdir', '')
                self.listlimit = self.win.userPreset.get('listlimit', '00')
                self.setupControls()
            elif controlID == 21:
                self.userdir = self.win.setDirRecorder()
                if self.userdir != '': self.getControl(210).setLabel(self.userdir, "font13", "0xffffffff")
                else: self.getControl(210).setLabel(xbmc.getLocalizedString(20078), "font13", "0x60ffffff")
            elif controlID in (251, 252):
                try:
                    if controlID == 251: LISTLIMIT.rotate(1)
                    elif controlID == 252: LISTLIMIT.rotate(-1)
                except: pass
                saveUserPreset = False
                limit = LISTLIMIT[0]
                try:
                    if limit == '00': limit = xbmc.getLocalizedString(21428)
                    else: limit = xbmc.getLocalizedString(21436) % (int(limit), )
                    self.getControl(250).setLabel('%s' % (limit, ))
                    saveUserPreset = True
                except: pass
                if saveUserPreset:
                    self.win.userPreset['listlimit'] = LISTLIMIT[0]
                    self.win.saveUserPreset()
                    self.listlimit = self.win.userPreset['listlimit']
            elif controlID == 26:
                keyboard = xbmc.Keyboard(self.query_key, __language__(63))
                keyboard.doModal()
                if keyboard.isConfirmed():
                    newkey = keyboard.getText()
                    if xbmcgui.Dialog().yesno(__language__(64), __language__(65), __language__(66) % self.query_key, __language__(67) % newkey):
                        self.win.userPreset['query_key'] = newkey
                        self.win.saveUserPreset()
                        self.query_key = self.win.userPreset.get('query_key', __language__(68))
                        self.win.query_key = self.query_key
                        self.getControl(260).setLabel(self.query_key)
        except: printLastError(False)

    def onAction(self, action):
        if action in (9, 10): self.close()

class allMusic_com(xbmcgui.WindowXMLDialog):
    def __init__(self, *args, **kwargs):
        self.newTBN = None
        self.img, self.text = None, None
        self.albumname = kwargs.get('albumname')
        self.destinationTBN = kwargs.get('dest')
        if self.destinationTBN:
            self.tagsmp3 = exechttpapi.getTagFromFilename(self.destinationTBN)
            self.getThumb = os.path.isfile(self.destinationTBN)
            self.destinationTBN = str(self.destinationTBN.replace('.mp3', '.tbn').replace('.MP3', '.tbn'))
        else:
            self.getThumb = False
            self.tagsmp3 = {}
        if self.albumname:
            self.img, self.text = exechttpapi.requestOnAllMusic_Com(self.albumname.replace('.mp3', '').replace('.MP3', ''))

    def onInit(self):
        if not self.text and not self.img: self.close()
        else: self.setupControls()

    def setupControls(self):
        if not self.text: self.text = xbmc.getLocalizedString(414)
        self.getControl(5).reset()
        self.getControl(5).setText(self.text)
        if not self.img or not os.path.isfile(self.img): self.img = DEFAULTAUDIOBIG
        self.getControl(10).setImage(self.img)
        self.getControl(20).setImage(self.img)
        self.getControl(7).setEnabled(os.path.isfile(self.img) and self.getThumb)
        self.setupInfoTags()

    def setupInfoTags(self):
        self.getControl(30).reset()
        self.getControl(30).addLabel(self.tagsmp3.get('title', self.albumname))
        self.getControl(31).reset()
        self.getControl(31).addLabel(self.tagsmp3.get('artist', __language__(200)))
        self.getControl(32).reset()
        self.getControl(32).addLabel(self.tagsmp3.get('album', __language__(200)))
        self.getControl(33).reset()
        self.getControl(33).addLabel(self.tagsmp3.get('genre', __language__(200)))
        self.getControl(34).reset()
        self.getControl(34).addLabel(self.tagsmp3.get('release year', __language__(200)))
        self.getControl(35).reset()
        self.getControl(35).addLabel(self.tagsmp3.get('track number', __language__(200)))

    def onFocus(self, controlID): pass

    def onClick(self, controlID):
        if controlID == 7:
            if self.destinationTBN and self.img != DEFAULTAUDIOBIG:
                import shutil
                try:
                    shutil.copy(self.img, self.destinationTBN)
                    xbmcgui.Dialog().ok(__language__(120), self.destinationTBN)
                except:
                    printLastError(False)
                    xbmcgui.Dialog().ok(__language__(106), __language__(121))
                else: self.newTBN = self.destinationTBN
                del shutil
        elif controlID == 8:
            album = self.tagsmp3.get('album', self.albumname.replace('.mp3', '').replace('.MP3', ''))
            keyboard = xbmc.Keyboard(album, xbmc.getLocalizedString(16011))
            keyboard.doModal()
            if keyboard.isConfirmed():
                albumsearch = keyboard.getText()
                artist = self.tagsmp3.get('artist', self.albumname.replace('.mp3', '').replace('.MP3', ''))
                keyboard = xbmc.Keyboard(artist, xbmc.getLocalizedString(16025))
                keyboard.doModal()
                if keyboard.isConfirmed():
                    artistsearch = keyboard.getText()
                    if not albumsearch == artistsearch: manuelsearch = '%s - %s' % (albumsearch, artistsearch)
                    else: manuelsearch = albumsearch
                    self.img, self.text = exechttpapi.requestOnAllMusic_Com(manuelsearch)
                    if not self.text == self.img: self.setupControls()
                    #else: xbmcgui.Dialog().ok(language(106), xbmc.getLocalizedString(500))

    def onAction(self, action):
        if action in (9, 10): self.close()

class historyData:
    def __init__(self, *args, **kwargs):
        if not os.path.isdir(HISTORYDATA): os.makedirs(HISTORYDATA)
        self.selected = kwargs.get('selected', '')
        self.saveListData = kwargs.get('dict', {})
        self.filename = os.path.join(HISTORYDATA, 'fake.his')
        if self.selected != '': self.filename = os.path.join(HISTORYDATA, self.selected+'.his')

    def loadData(self):
        if (self.selected != '') and os.path.isfile(self.filename):
            try:
                f = open(self.filename, "rb")
                self.saveListData = marshal.load(f)
                f.close()
            except:
                xbmcgui.Dialog().ok(__language__(106), __language__(40), __language__(41))
                printLastError(False)
        return self.saveListData

    def saveData(self):
        if (self.selected != '')&(self.saveListData != {})&(self.filename != os.path.join(HISTORYDATA, 'fake.his')):
            f = open(self.filename, "wb")
            marshal.dump(self.saveListData, f)
            f.close()
        else: xbmcgui.Dialog().ok(__language__(106), __language__(42))

xbmc.executebuiltin('Skin.SetString(rbcdcontextmenu,0)')

if __name__ == "__main__":
    try:
        w = GUI("HomeSkin.xml", CWD, getUserSkin(), 1)
        w.doModal()
        del w
    finally:
        xbmc.PlayList(0).clear()
