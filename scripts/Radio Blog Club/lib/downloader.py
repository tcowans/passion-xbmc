
import os, urllib
import sys, traceback
from shutil import copy
from threading import Thread
from tempfile import gettempdir
from smarturlretrieve import SmartFancyURLopener

import xbmcgui

DIALOG_PROGRESS = xbmcgui.DialogProgress()

class Abort(Exception): pass

class Download(Thread):
    def __init__(self, url, local=None, tmpfile=None, progressbar=None):
        Thread.__init__(self)
        self.progressBar = progressbar
        self.SUCCESS = False, None
        self.stop = False
        self.url = url
        if not tmpfile: tmpfile = os.path.abspath(os.path.join(gettempdir(), 'tmpfile.tmp'))
        self.tmpfile = tmpfile
        if not local: local = self.tmpfile
        self.local = local
        self._remove()

    def _hook(self, cpt_blk, taille_blk, total_taille):
        if self.stop: raise Abort
        try: pct = ((taille_blk * cpt_blk) * 100.0 / total_taille)
        except ZeroDivisionError: pct = 100
        if 0 > pct > 100: pct = 100
        if self.progressBar: self.progressBar(int(pct))

    def _remove(self):
        urllib.urlcleanup()
        try: os.unlink(self.tmpfile)
        except: pass#traceback.print_exc()

    def _tmpFileIsLocal(self):
        if self.stop: return
        if self.tmpfile == self.local:
            self.SUCCESS = True, self.tmpfile
        elif self.tmpfile != self.local:
            try: copy(self.tmpfile, self.local)
            except: traceback.print_exc()
            else: self.SUCCESS = True, self.local
            self._remove()
        self.stop = True

    def run(self):
        try:
            urllib._urlopener = SmartFancyURLopener()
            urllib.urlretrieve(self.url, self.tmpfile, reporthook=self._hook)
            urllib.urlcleanup()
        except Abort: print 'Download Aborted'
        except:
            traceback.print_exc()
            self.stop = True
            self._remove()
            raise
        self._tmpFileIsLocal()

    def abort(self):
        self.stop = True

def progressBar(pct):
    sys.stdout.write ( '\r\t\t[' + (int(round(pct/2))*'#').ljust(50) + '] %.2f%%' % pct )
    sys.stdout.flush()

def mainXBMC():
    import xbmcgui
    url = 'http://ftp1.srv.endpoint.nu/pub/repository/t3ch/XBMC-SVN_2007-06-04_rev9200-T3CH.rar'
    try:
        DIALOG_PROGRESS.create('Teste pour annuler un gros download', url)
        pb = DIALOG_PROGRESS.update
        dl = Download(url, progressbar=pb)
        dl.start()
        while not dl.stop:
            if DIALOG_PROGRESS.iscanceled():
                dl.abort()
                break
        DIALOG_PROGRESS.close()
    except:
        traceback.print_exc()

def main():
    url = 'http://ftp1.srv.endpoint.nu/pub/repository/t3ch/XBMC-SVN_2007-06-04_rev9200-T3CH.rar'
    try:
        pb = progressBar
        dl = Download(url, progressbar=pb)
        dl.start()
        while not dl.stop:
            try:
                if dl.stop: print 'Terminer'
            except KeyboardInterrupt, EOFError:
                print 'Download Aborted'
                dl.abort()
    except:
        traceback.print_exc()

if __name__ == "__main__":
    try: mainXBMC()
    except: main()
