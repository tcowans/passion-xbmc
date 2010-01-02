# -*- coding: utf-8 -*-

# Modules general
import os
#import sys
    
# append the proper platforms folder to our path, xbox is the same as win32
#env = ( os.environ.get( "OS", "win32" ), "win32", )[ os.environ.get( "OS", "win32" ) == "xbox" ]
#sys.path.append( os.path.join( os.getcwd(),"platform_libraries", env ) )
from pysqlite2 import dbapi2 as sqlite

RootDir  = os.getcwd().replace( ";", "" ) # Create a path with valid format
cacheDir = os.path.join(RootDir, "cache")
DB = os.path.join(cacheDir, 'Passion_XBMC_Installer.sqlite')


def nicequery(query,dico):
    words = query.split()

    for indice in range(len(words)):
        
        if "$" in words[indice]:
            word = dico[words[indice]]
            try:
                testnum = int(word)
                arg = str(word)
            except:
                arg = repr(word)
            query = query.replace(words[indice],arg)
    return query    


def incat(iditem=0):
    """
    Liste des sous-catégories et fichiers de la catégorie sélectionnée
    Renvoie un dictionnaire constitué comme suit : {id, name, parent, file,type}
    Chaque index du dictionnaire renvoie à une liste d'occurences.
    Il faut l'appeler le numéro id de la catégorie dont on veut obtenir le contenu
    Si on veut obtenir la liste des catégories racines, il alimenter la fonction avec 0 
    """
    
    #Connection à la base de donnée
    conn = sqlite.connect(DB)
    c = conn.cursor()
    
    #initialisation des listes du dictionnaire
    id = []
    name = []
    parent = []
    file = []
    type =[]
    
    #initialisation du dictionnaire
    dico = {}
    dico['id'] = id
    dico['name'] = name
    dico['parent'] = parent
    dico['file'] = file
    dico['type'] = type
    
    cols = {}
    cols['$id_parent'] = str(iditem)
    
    #requete
    c.execute(nicequery('''SELECT id_cat, title, id_parent,'None','CAT' AS type
                             FROM Categories
                             WHERE id_parent = $id_parent
                                            
                             UNION ALL      
                                        
                             SELECT id_file, title, id_cat,fileurl,'FIC' AS type
                             FROM Server_Items
                             WHERE id_cat = $id_parent
                             ORDER BY type ASC, title ASC
                            ''',cols))

                 
    #pour chaque colonne fetchée par la requête on alimente une liste, l'ensemble des  
    #listes constitue le dictionnaire
    for row in c:   
        #for colomn in row:
            #colomn = unicode( colomn, "utf-8" )
            #colomn = colomn.encode( "utf-8" )    
        id.append(row[0])
        name.append(row[1].encode("cp1252"))
        parent.append(row[2])
        file.append(row[3])
        type.append(row[4])
  
    c.close()
         
    return dico 

def info_item(id):
    """
    Sert à obtenir des informations sur un fichier.
    Renvoie un dictionnaire constitué comme suit : 
    {name, description, icon, downloads, file, created, screenshot}
    Chaque index du dictionnaire renvoie à une liste d'occurences.
    Alimenter cette fonction avec l'id du fichier dont on veut obtenir les infos.
    """

    #Connection à la base de donnée
    conn = sqlite.connect(DB)
    c = conn.cursor()  
    
    try:
        c.execute('''SELECT A.id_file , 
                            A.title, 
                            A.description, 
                            A.previewpictureurl, 
                            A.totaldownloads, 
                            A.filename, 
                            A.createdate,
                            C.path
                     FROM Server_Items A, Categories B, Install_Paths C
                     WHERE id_file = ? 
                     AND A.id_cat = B.id_cat
                     AND B.id_path = C.id_path
                     ''',(id,))
    except Exception, e:
        print e
                 
    #ici une seule ligne est retournée par la requête
    #pour chaque colonne fetchée par la requête on alimente un index du dictionnaire
    dico = {}
    for row in c:
        print row
        dico['id'] = row[0]
        dico['name'] = (row[1].encode("cp1252"))
        dico['description'] = (row[2].encode("cp1252"))
        dico['screenshot'] = row[3]
        dico['downloads'] = row[4]
        dico['file'] = row[5]
        dico['created'] = row[6]
        dico['path2download']=row[7]
    c.close()   
    return dico




