import os
import csv
import urllib
import xbmcgui

try:
    #New in python version 2.5
    import sqlite3 as sqlite
except:
    #cette methode provient d'apple movie trailer
    # append the proper platforms folder to our path, xbox is the same as win32
    env = ( os.environ.get( "OS", "win32" ), "win32", )[ os.environ.get( "OS", "win32" ) == "xbox" ]
    sys.path.append( os.path.join( os.getcwd(), "platform_libraries", env ) )
    from pysqlite2 import dbapi2 as sqlite

RootDir  = os.getcwd().replace( ";", "" ) # Create a path with valid format
cacheDir = os.path.join(RootDir, "cache")
DB = os.path.join(RootDir, 'DB.db')


"""
STRUCTURE DE LA TABLE :
(id, name, description, icon, category, type, downloads, file, created, parent, screenshot)
"""

def maketable():
    """
    Fonction de création de la table, à n'appeler que si la table n'existe pas déjà.
    Pour se faire effectuer un test : if not os.path.isfile(DB):
    """
    #On récupère le fichier table.csv
    result = os.path.join(RootDir, 'table.csv')
    requete = 'http://passion-xbmc.org/importcsv.php'
    loc = urllib.URLopener()
    loc.retrieve(requete, result)
    loc = urllib.URLopener()
    loc.retrieve(requete, result)
    
    #Initialisation de la base de donnée
    conn = sqlite.connect(DB)
    c = conn.cursor()
    
    #Creation de la table
    c.execute('''CREATE TABLE Scripts_Plugins
    (id int, name text, description text, icon text, category int, type int, downloads int, file text, created unix_timestamp, parent int, screenshot text )''')

    #On sauvegarde les modifications
    conn.commit()

    #Lecture du fichier table.csv
    reader = csv.reader(open(result),delimiter = '|')

    for row in reader:

        #on retranche l'occurs de fin de ligne     
        colonnes = row[:len(row)-1]

        try:
            #Chaque ligne trouvée dans le table.csv est insérée dans la table
            c.execute("""INSERT into Scripts_Plugins
                         (id, name, description, icon, category, type, downloads, file, created, parent, screenshot)
                         VALUES (?,?,?,?,?,?,?,?,?,?,?)""",colonnes)
        except Exception, e:
            print e

        #Sauvegarde des modifications
        conn.commit()    
    # On ferme l'instance du curseur
    c.close()


def incat(iditem):
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
    
    #requete
    c.execute('''SELECT id, name, parent, file,type
                 FROM Scripts_Plugins
                 WHERE parent = ?
                 AND type = 'dlcat'  
                                
                 UNION ALL      
                            
                 SELECT id, name, category, file,type
                 FROM Scripts_Plugins
                 WHERE category = ?
                 AND type = 'dlitem'                 
                 ORDER BY name ASC
                ''',(iditem,iditem))

                 
    #pour chaque colonne fetchée par la requête on alimente une liste, l'ensemble des  
    #listes constitue le dictionnaire
    for row in c:
        print row
        id.append(row[0])
        name.append(row[1])
        parent.append(row[2])
        file.append(row[3])
        type.append(row[4])
  
    c.close()
         
    return dico 


def outcat(idparent):
    """
    Remonte l'arborescence de la liste. Il faut alimenter cette fonction avec le parent 
    de la liste qu'on affiche.
    Renvoie un dictionnaire constitué comme suit : {id, name, parent, file,type}
    Chaque index du dictionnaire renvoie à une liste d'occurences.
    """
    
    #Connection à la base de donnée
    conn = sqlite.connect(DB)
    c = conn.cursor()
    
    #initialisation des listes du dictionnaire
    id = []
    name = []
    parent = []
    file = []
    type = []
    
    #initialisation du dictionnaire
    dico = {}
    dico['id'] = id
    dico['name'] = name
    dico['parent'] = parent
    dico['file'] = file
    dico['type'] = type
    
    #requete
    c.execute('''SELECT id, name, parent, file,type
                 FROM Scripts_Plugins
                 WHERE parent = (SELECT parent 
                                 FROM Scripts_Plugins
                                 WHERE id = ?)
                 AND type = 'dlcat'
                 
                 UNION ALL
                 
                 SELECT id, name, category, file,type
                 FROM Scripts_Plugins
                 WHERE category = (SELECT parent 
                                   FROM Scripts_Plugins
                                   WHERE id = ?)
                 AND type = 'dlitem'
                 
                 ORDER BY name ASC
                ''',(idparent,idparent))
                 
    #pour chaque colonne fetchée par la requête on alimente une liste, l'ensemble des  
    #listes constitue le dictionnaire
    for row in c:
        id.append(row[0])
        name.append(row[1])
        parent.append(row[2])
        file.append(row[3])
        type.append(row[4])
    c.close()
    
    return dico

def info(id):
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
    print id
    
    c.execute('''SELECT name, description, icon, downloads, file, created, screenshot 
                 FROM Scripts_Plugins 
                 WHERE id = ? 
                 AND type = 'dlitem' 
                 ''',(id,))
                 
    #ici une seule ligne est retournée par la requête
    #pour chaque colonne fetchée par la requête on alimente un index du dictionnaire
    dico = {}
    for row in c:
        dico['name'] = row[0]
        dico['description'] = row[1]
        dico['icon'] = row[2]
        dico['downloads'] = row[3]
        dico['file'] = row[4]
        dico['created'] = row[5]
        dico['screenshot'] = row[6]
    c.close()   
    return dico



