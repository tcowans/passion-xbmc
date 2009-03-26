# -*- coding: cp1252 -*-
"""
Passion-XBMC Gallery Explorer Beta 1
Auteur : Seb
"""

import urllib,sys,os
import xbmcplugin,xbmcgui,xbmc
import csv
import string

#On définit le type du plugin
xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category="Pictures" )

# état des variables initiales
BaseUrl = "http://passion-xbmc.org/galleryexplorer.php?cat="
RootDir = os.getcwd().replace(';','')


urllib.urlcleanup()

def fetchgallery(idcat):
    """
    Fonction de recherche dans la galerie, alimenter avec l'id de la catégorie recherchée, 0 étant la racine
    """
    #On récupère le fichier result.csv
    result = os.path.join(RootDir, 'result.csv')
    url = BaseUrl + str(idcat)
    
    loc = urllib.URLopener()
    loc.retrieve(url, result)

    #Lecture du fichier table.csv
    reader = csv.reader(open(result),delimiter = '|')

    #initialisation des listes du dictionnaire
    id = []
    type = []
    title = []
    description = []
    thumbnail = []
    image = []
    parent =[]

    #Initialisation du dictionnaire
    dico = {}
    dico['id']=id
    dico['type']=type
    dico['title']=title
    dico['description']=description
    dico['thumbnail']=thumbnail
    dico['image']=image
    dico['parent']=parent


    for row in reader:

        if row != [' ']:
            id.append(row[0])
            type.append(row[1])
            title.append(row[2])
            description.append(row[3])
            thumbnail.append(row[4])
            image.append(row[5])
            parent.append(row[6])       
        
    return dico 

def preparesaving(path,title):
    try:
        ext = title.split('.')[1]
        return path + '|' + title
    except:
        ext = path.split('.')[1]
        return path + '|' + title + ext
   
def show_icones(cat):
    ok=True
    dico = fetchgallery(cat)
    indice = 0
    for id in dico['id']:
        IconeImage = dico['thumbnail'][indice]
        if dico['type'][indice] == 'PIC':

            PictureName = dico['title'][indice]       
            if  xbmcplugin.getSetting( "SAVE" ) == "true":
                url = '%s?download_path=%s' % ( sys.argv[ 0 ], preparesaving(dico['image'][indice],PictureName))
            

            else:
                url = dico['image'][indice]
           
            #On affiche la liste des icones de la galerie
            item=xbmcgui.ListItem(PictureName,iconImage=IconeImage,thumbnailImage=IconeImage)
        
            # ajout d'un bouton dans le contextmenu pour downloader l'image
            label_du_bouton = "Save..."
            action_du_bouton = 'XBMC.RunPlugin(%s?download_path=%s)' % ( sys.argv[ 0 ], preparesaving(dico['image'][indice],PictureName))
            #A list of tuples consisting of label and action pairs.
            c_items = [ ( label_du_bouton, action_du_bouton ) ]
            # replaceItems=True, seulement mon bouton va etre visible dans le contextmenu 
            # si on veut tous les boutons plus le notre on mets rien listitem.addContextMenuItems( c_items ), car False est par default
            item.addContextMenuItems( c_items )
            
            #item.addContextMenuItems([('', '',)],)
            ok = ok and xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=item,isFolder=False,totalItems=len(dico['id'])) 
        else:

            CatName = dico['title'][indice]
            
            if IconeImage != 'None':
                item=xbmcgui.ListItem(CatName,iconImage=IconeImage,thumbnailImage=IconeImage)
            else:
                item=xbmcgui.ListItem(CatName,'','')
            item.addContextMenuItems([('', '',)],)
            
            #listitem.addContextMenuItems('Save...',)
            url=sys.argv[0]+"?cat="+id
            
            ok = ok and xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=item,isFolder=True,totalItems=len(dico['id']))     
        indice = indice + 1
    
    return ok


#Pave repris des investigations de alexsolex en matiere de plugin
stringparams = sys.argv[2]
print 'STRING PARAMS = %s'%stringparams
try:
    if stringparams[0]=="?":
        stringparams=stringparams[1:]
except:
    pass
parametres={}
for param in stringparams.split("&"):
    try:
        cle,valeur=param.split("=")
    except:
        cle=param
        valeur=""
    parametres[cle]=valeur

if "cat" in parametres.keys():

    show_icones(parametres["cat"].replace('cat=',''))
    ##paramètre 'cat' : on liste l'image correspondante
    
elif  "download_path" in parametres.keys():
    folder = xbmcplugin.getSetting( "PATH" )
    if os.path.exists( folder ):
        path = parametres["download_path"].replace('download_path=','')
        dl_path = path.split('||')[0]
        file = os.path.join(folder,path.split('|')[1])
        print dl_path
        print file
        urllib.urlretrieve( dl_path, file)
    
else:
    #pas de paramètres : début du plugin
    show_icones(0)
    
xbmcplugin.endOfDirectory(int(sys.argv[1]))

