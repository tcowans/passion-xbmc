# -*- coding: utf-8 -*-
"""
Passion-XBMC Gallery Explorer Beta 2
Auteurs : Seb & Frost
"""

import urllib,sys,os
import xbmcplugin, xbmcgui,xbmc

_ = xbmc.getLocalizedString

def download_as(url,folder=""):
    """
    propose un choix de noms de fichiers et / ou une saisie au clavier
    """
    dlpath=url.split('|')[0]
    picname=(url.split('|')[1])  
    choice=[picname,"folder.jpg","default.tbn","%s-fanart.jpg"%picname.split('.')[0],_(30010)]
    newpicname = xbmcgui.Dialog().select(_(30009),choice)
    
    if newpicname == 4:
        keyboard = xbmc.Keyboard(picname,_(30009))
        keyboard.doModal()
        if (keyboard.isConfirmed()):
            newpicname=keyboard.getText()
            url=url=preparesaving(dlpath,newpicname)
        del keyboard 
    else:
        url=preparesaving(dlpath,choice[newpicname])
         
    download_picture(url,folder) 

def download_picture(url,folder=""):
    """
    télécharge une image, si pas de paramètre, affichage d'une fenêtre de browse
    """
    print "folder = %s"%folder
    if folder == "":
        folder = xbmcgui.Dialog().browse(0,_(30002),'pictures','',True,)
    if os.path.exists(folder):
        dl_path = url.split('|')[0]
        file = os.path.join(folder,url.split('|')[1])
        urllib.urlretrieve( dl_path, file)
        # downloader sans erreur , on le dit par popup
        xbmcgui.Dialog().ok( _(30005), file )
    else:
        xbmcgui.Dialog().ok( _(30006), _(30007) )


def preparesaving(path,title):
    #concatène l'url à passer en paramètre et ajoute l'extension au nom  
    try:
        ext = title.split('.')[1]
        return path + '|' + title
    except:
        ext = '.' + path[len(path)-3:]
        return path + '|' + title + ext      

def main():

    print "PARAM = %s"%sys.argv[2]
      
    if  "download_path=" in sys.argv[2]:
        if xbmcplugin.getSetting( "SAVE" ) == "true":
            download_picture(sys.argv[2].split('download_path=')[1],xbmcplugin.getSetting( "PATH" ))
        else:
            download_picture(sys.argv[2].split('download_path=')[1],xbmcplugin.getSetting(''))

    elif "download_as=" in sys.argv[2]:
        if xbmcplugin.getSetting( "SAVE" ) == "true":
            download_as(sys.argv[2].split('download_as=')[1],xbmcplugin.getSetting( "PATH" ))
        else:
            download_as(sys.argv[2].split('download_as=')[1],xbmcplugin.getSetting(''))


 
 
        
