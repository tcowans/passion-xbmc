import xbmc, xbmcgui, urllib, md5, os

HOME=os.getcwd()[:-1]+"\\"
UPDATE_URL="http://netbourse.free.fr/xbmc/MyCine/"

class Updater:
    def update(self):
        updateAllowed = False
        update = urllib.urlopen(UPDATE_URL+"versions.php").read()
        fics = update.split('#');
        for fic in fics:
            fileName,chksum=fic.split('|')
            chksum=chksum[:32]
            try:
                f=open(HOME+fileName,'r')
                s=f.read()
                f.close()
                m=md5.new()
                m.update(s)
                hd=m.hexdigest()
                del m
            except:
                hd=0

            if hd != chksum:
                if not updateAllowed:
                    if xbmcgui.Dialog().yesno('Mise à jour','nouvelle version disponible!','Mettre à jour?') == False:
                        return
                    updateAllowed = True
                urllib.urlretrieve(UPDATE_URL+"download.php?file="+fileName,HOME+fileName)

def update():
    dialog = xbmcgui.DialogProgress()
    dialog.create("MyCine","Vérification de la version","","")
    try:
        u=Updater()
        u.update()
        del u
        dialog.close()
    except:
        dialog.close()
        del dialog
        dialog = xbmcgui.Dialog()
        dialog.ok("MyCine","Echec de la mise à jour","","")
    del dialog

def updateLauncher():
    chksum = urllib.urlopen(UPDATE_URL+"versionLauncher.php").read()
    try:
        f=open(HOME+"MyCine.py",'r')
        s=f.read()
        f.close()
        m=md5.new()
        m.update(s)
        hd=m.hexdigest()
        del m
    except:
        hd=0

    if hd != chksum:
        urllib.urlretrieve(UPDATE_URL+"MyCineModifier.py",HOME+"MyCineModifier.py")
        xbmc.executescript(HOME+"MyCineModifier.py")
        return 1
    return 0
