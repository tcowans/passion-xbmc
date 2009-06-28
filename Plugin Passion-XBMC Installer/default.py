# -*- coding: utf-8 -*-
"""
Passion-XBMC Gallery Explorer Beta 2
Auteurs : Seb & Frost
"""

import urllib,sys,os
import xbmcplugin,xbmcgui,xbmc
import csv
import browse_scripts_plugins as browse
 

#On définit le type du plugin
#xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category="Programs" )

#Etat des variables initiales
SiteUrl = "http://passion-xbmc.org/downloads/"
urllib.urlcleanup()
  
def _unicode( s, encoding="utf-8" ):
    """ customized unicode, don't raise UnicodeDecodeError exception, return no unicode str instead """
    try: s = unicode( s, encoding )
    except: pass
    return s

def download_file(id):
    """
    """
    dico = browse.info_item(id)
    print dico['id']
    filename=dico['name']
    url=SiteUrl+dico['file']
    try:
        path2download=dico['path2download']  
        if 'Browse' in path2download:
            path2download = xbmcgui.Dialog().browse(0,"Choisir Dossier",'programs','',True,)
    except Exception, e:
        print e
        

    urllib.urlretrieve( url, os.path.join(path2download,filename))
    # downloader sans erreur , on le dit par popup
    xbmcgui.Dialog().ok( _unicode('téléchargement terminé'), filename )  

   
def show_icones(cat=0):
    """
    Affichage
    """
    ok=True
    dico = browse.incat(cat)
    print dico['id']
    for indice in range(len(dico['id'])):

        if dico['type'][indice] == 'CAT':
            print "dico[name] = %s"%dico['name'][indice]
            url=sys.argv[0]+"?cat="+str(dico['id'][indice])
           
            #On affiche la liste des icones de la galerie
            item=xbmcgui.ListItem(_unicode(dico['name'][indice]))
            ok = ok and xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=item,isFolder=True,totalItems=len(dico['id'])) 
        
        else:
            print "dico[name] = %s"%dico['name'][indice]
            url=sys.argv[0]+"?file="+str(dico['id'][indice])
            item=xbmcgui.ListItem(_unicode(dico['name'][indice]))
            
            #Demander information
            #c_items = [ ( _(30011), 'XBMC.RunPlugin(%s?set_screensaver=%s)' % ( sys.argv[ 0 ],id) ) ]
            
            #item.addContextMenuItems( c_items)
            
            #listitem.addContextMenuItems('Save...',)
            ok = ok and xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=item,isFolder=False,totalItems=len(dico['id']))     
           
    return ok

print "PARAM = %s"%sys.argv[2]

if "cat=" in sys.argv[2]:
    show_icones(sys.argv[2].split('cat=')[1])
    ##paramètre 'cat' : on liste l'image correspondante
    
elif "file=" in sys.argv[2]:    
    download_file(sys.argv[2].split('file=')[1])
else:
    import update_datas
    update_datas.update_datas()
    show_icones()
    
xbmcplugin.endOfDirectory(int(sys.argv[1]))

 
 
        
