import sys
import xbmcplugin,xbmcgui,xbmc

from fetchgallery import fetchgallery

def _unicode( s, encoding="utf-8" ):
    """ customized unicode, don't raise UnicodeDecodeError exception, return no unicode str instead """
    try: s = unicode( s, encoding )
    except: pass
    return s

def show_pics(cat):
    ok=True
    dico = fetchgallery(cat)
    for index in range(len(dico['id'])):
        if dico['type'][index] == 'PIC':
            PictureName = dico['title'][index]       
            url = dico['image'][index]
            item=xbmcgui.ListItem(_unicode(PictureName),)
            print "url = %s"%url
            ok = ok and xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=item,isFolder=False,totalItems=len(dico['id'])) 
    return ok

def main():
    print "ici 1"
    if "slideshow=" in sys.argv[2]:
        show_pics(sys.argv[2].split('slideshow=')[1])
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

