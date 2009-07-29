# -*- coding: utf-8 -*-
"""
Passion-XBMC Gallery Explorer Beta 2
Auteurs : Seb & Frost
"""

import urllib,sys,os,string
import xbmcplugin,xbmcgui,xbmc

from elementtree import ElementTree as ET
from fetchgallery import fetchgallery
from download import preparesaving

#On définit le type du plugin
xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category="Pictures" )
urllib.urlcleanup()


_ = xbmc.getLocalizedString


def _unicode( s, encoding="utf-8" ):
    """ customized unicode, don't raise UnicodeDecodeError exception, return no unicode str instead """
    try: s = unicode( s, encoding )
    except: pass
    return s
       
def show_icones(cat=0):
    """
    Affichage
    """
    ok=True
    dico = fetchgallery(cat)
    #for id in dico['id']:
    for index in range(len(dico['id'])):
        
        IconeImage = dico['thumbnail'][index]
        
        if dico['type'][index] == 'PIC':
            #On lit une image
            PictureName = dico['title'][index]       
            url = dico['image'][index]
           
            #On affiche la liste des icones de la galerie
            item=xbmcgui.ListItem(_unicode(PictureName),iconImage=IconeImage,thumbnailImage=IconeImage)
            
            ##On ajoute les boutons au menu contextuel
            ##Enregistrer..
            c_items = [ ( _(30003), 'XBMC.RunPlugin(%s?download_path=%s)' % ( sys.argv[ 0 ], preparesaving(dico['image'][index],PictureName)) ) ]
            ###Enregistrer sous...
            c_items += [ ( _(30004), 'XBMC.RunPlugin(%s?download_as=%s)' % ( sys.argv[ 0 ], preparesaving(dico['image'][index],PictureName)) ) ]
            ##Définir commme fond d'écran
            #c_items += [ ( _(30011), 'XBMC.RunPlugin(%s?skinsettings=%s)' % ( sys.argv[ 0 ], dico['image'][indice]) ) ]
            #Alimentation Menu Contextuel
            item.addContextMenuItems( c_items)
            
            ok = ok and xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=item,isFolder=False,totalItems=len(dico['id'])) 
        
        else:
            #On lit un dossier
            CatName = dico['title'][index]
            
            if IconeImage != 'None':
                item=xbmcgui.ListItem(_unicode(CatName),iconImage=IconeImage,thumbnailImage=IconeImage)
            else:
                item=xbmcgui.ListItem(_unicode(CatName))
            
            #Définir commme fond d'écran
            c_items = [ ( _(30012), 'XBMC.RunPlugin(%s?set_screensaver=%s)' % ( sys.argv[ 0 ],dico['id'][index]) ) ]          
            #Alimentation du menu contextuel
            item.addContextMenuItems( c_items)

            url=sys.argv[0]+"?cat="+dico['id'][index]
            
            ok = ok and xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=item,isFolder=True,totalItems=len(dico['id']))     
    
    return ok

def set_home_background_imgage(url):
    # fonction pour PM3.HD seulement
    if xbmc.getSkinDir().lower() != "pm3.hd":
        # on a pas d'affaire ici return 
        return
 
    list = [ "Video", "Music", "Pictures", "Programs", "Weather", "Scripts", "Settings" ]
    #ici on mets un dialog select pour choisir la section video, picture, etc
    selected = xbmcgui.Dialog().select( "Arrières-plans de l'accueil", list )
 
    # s'il y a une reponse avec le dialog select on continu la fonction
    if selected != -1:
        # si l'options activer le background est pas activer, on l'active
        if xbmc.getCondVisibility( "!Skin.HasSetting(Home_Enable_Custom_Back_%s)" % list[selected] ):
            xbmc.executebuiltin( "Skin.ToggleSetting(Home_Enable_Custom_Back_%s)" % list[selected] )
        builtin = "Skin.SetPath(Home_Custom_Back_%s_Folder,%s)"% ( selected,)
        xbmc.executebuiltin(builtin) 

def main():

    print "PARAM = %s"%sys.argv[2]

    if "cat=" in sys.argv[2]:
        show_icones(sys.argv[2].split('cat=')[1])
        ##paramètre 'cat' : on liste l'image correspondante
     
    #elif "skinsettings=" in sys.argv[2]:       
    #    set_home_background_image(sys.argv[2].split('skinsettings=')[1])
            
    else:
        #pas de paramètres : début du plugin
        show_icones()
        
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

 
 
        
