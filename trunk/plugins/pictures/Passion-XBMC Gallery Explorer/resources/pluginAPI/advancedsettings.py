# -*- coding: utf-8 -*-
from elementtree import ElementTree as ET
import sys,os
import xbmcgui,xbmc

_ = xbmc.getLocalizedString
ENCODING = ( "", "iso-8859-1", "UTF-8", )[ 2 ]
rootdir = os.getcwd().replace(';','')

def get_screensaver_settings(slideshow):
    """
    """ 
    slideshowpath = 'plugin://pictures/Passion-XBMC Gallery Explorer/' + slideshow.replace('set_screensaver=','slideshow=')
    
    tree = ET.parse(os.path.join(rootdir,'resources','screensaversettings.xml'))
    root = tree.getroot()
    
    scr = root.tag
    settings = {}
    settings[scr]={}
    
    for child in root.getchildren():
        childname = child.tag
        if 'slideshowpath' in childname:
            settings[scr][childname] = slideshowpath
        else:
            settings[scr][childname] = child.text   

    return settings


def insert_screensaver_settings(root,settings):
    """
    """
    tab = '    '
    ret = '\n'
    root.text = ret + tab
    for setting in settings.keys():
        subelement = ET.SubElement(root,setting)
        subelement.text = ret + tab + tab
        for param in settings[setting].keys():
            subsub = ET.SubElement(subelement, param)
            subsub.text = settings[setting][param]
            subsub.tail = ret + tab + tab
        subelement.tail = ret

    return root


def update_screensaver_settings(root,settings):
    """
    """
    for child in root.getchildren():
        childname = child.tag
        if 'screensaver' in child.tag:
            for subchild in child:
                subchildname = subchild.tag
                if subchildname in settings[childname].keys():
                    subchild.text = settings[childname][subchildname]   
    return root


def copy_advanced_settings(source,advset):
    """
    """
    import shutil
    shutil.copy(source, advset)  
    del shutil


def main():
    """
    """
    advset = 'special://userdata/advancedsettings.xml'
    source = os.path.join(rootdir,'resources','advancedsettings.xml')
    try:
        if os.path.isfile(advset):
            settings = get_screensaver_settings(sys.argv[2])
            tree = ET.parse(advset)
            root = tree.getroot()
            if tree.findtext('screensaver'):
                newroot = update_screensaver_settings(root, settings)
            else:
                newroot = insert_screensaver_settings(root, settings)
            
            # wrap it in an ElementTree instance, and save as XML
            tree = ET.ElementTree( newroot )
            tree.write( advset, ENCODING )
        else:
            if copy_advanced_settings(source,advset):
                main()     
        #xbmc.executebuiltin('XBMC.ReloadSkin()')
        #xbmcgui.Dialog().ok( _(30013), _(30014),slideshowpath)
        if xbmcgui.Dialog().yesno( _(30013), _(30014), _(30015)):
            xbmc.executebuiltin('XBMC.RestartApp')
    except:
        return
    


