# -*- coding: cp1252 -*-
"""
Passion-XBMC Gallery Explorer Beta 1
Auteur : Seb
"""

import urllib,sys,os
import xbmcplugin,xbmcgui,xbmc
import csv
#import threading
#from Queue import Queue, Empty
#from time import time

#On définit le type du plugin
xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category="Pictures" )

# état des variables initiales
BaseUrl = "http://passion-xbmc.org/galleryexplorer2.php?cat="
RootDir = os.getcwd().replace(';','')


#urllib.urlcleanup()

#NUM_THREADS = 40
#start = time()
#q_in = Queue(0)
#q_out = Queue(0)
 
## on remplit q_in avec les url (ici c'est juste un exemple pour tester)
#for i in xrange(400):
    #q_in.put("http://www.pythonchallenge.com/pc/def/linkedlist.php?nothing=%d" % i)
 
#def getfiles():
    ## fonction exécutée par les threads
    ## ici je me contente de sauver le contenu avec l'url dans q_out
    #try:
        #while True:
            #url = q_in.get_nowait()
            #f = urlopen(url)
            #q_out.put((url,f.read()))
            #f.close()
    #except Empty:
        ## q_in est vide; on a terminé
        #pass
 
## on crée et on démarre les threads
#for i in xrange(NUM_THREADS):
    #t = threading.Thread(target = getfiles)
    #t.start()


#def download(url,title):
    #print "URL = %s"%url
    #try:
        #dlpath = "special://temp/"+title  
        #loc = urllib.URLopener()
        #loc.retrieve(url, dlpath)
        #return dlpath
    #except Exception, e:
        #print e
        #print url


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

   
def show_icones(cat):
    ok=True
    dico = fetchgallery(cat)
    indice = 0
    for id in dico['id']:
        if dico['thumbnail'][indice] != 'None':
            IconeImage = "thumb_"+dico['title'][indice]
        else:
            IconeImage = ''
            
        if dico['type'][indice] == 'PIC':

            PictureName = dico['title'][indice]       
            url = dico['image'][indice]+"&urlwanted"
            
            #On affiche la liste des icones de la galerie
            item=xbmcgui.ListItem(PictureName,iconImage=IconeImage,thumbnailImage=IconeImage)
            ok = ok and xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=item,isFolder=False,totalItems=len(dico['id'])) 
        else:

            CatName = dico['title'][indice]
            
            if IconeImage != 'None':
                item=xbmcgui.ListItem(CatName,iconImage=IconeImage,thumbnailImage=IconeImage)
            else:
                item=xbmcgui.ListItem(CatName,'','')
            
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
 
    
else:
    #pas de paramètres : début du plugin
    show_icones(0)
    
xbmcplugin.endOfDirectory(int(sys.argv[1]))


