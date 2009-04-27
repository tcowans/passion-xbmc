import os
import csv
import urllib
import sys

#cette methode provient d'apple movie trailer
# append the proper platforms folder to our path, xbox is the same as win32
env = ( os.environ.get( "OS", "win32" ), "win32", )[ os.environ.get( "OS", "win32" ) == "xbox" ]
sys.path.append( os.path.join( os.getcwd(),"platform_libraries", env ) )
from pysqlite2 import dbapi2 as sqlite

RootDir  = os.getcwd().replace( ";", "" )
DB = os.path.join(RootDir, 'Passion_XBMC_Installer.sqlite')
result = os.path.join(RootDir, 'table.csv')

"""
STRUCTURE DE LA TABLE :
(id, name, description, icon, category, type, downloads, file, created, parent, screenshot)
"""
def update_datas():
    if not os.path.isfile(DB):
        makeCategories()
        makeServer_Items()
    else:
        updateServerItems()
    
def download_csv(args):
    #On récupère le fichier table.csv
    baseurl = 'http://passion-xbmc.org/clone/exportdownloads.php/'
    url = baseurl + args
    loc = urllib.URLopener()
    loc.retrieve(url, result)     

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


def updateServerItems():
    """
    Fonction de création de la table, à n'appeler que si la table n'existe pas déjà.
    Pour se faire effectuer un test : if not os.path.isfile(DB):
    """
    conn = sqlite.connect(DB)
    #Initialisation de la base de donnée
    c = conn.cursor()
    c.execute("""SELECT max(date) FROM Server_Items""")
    args = '?action=getitems&param=%s'%c.fetchone()[0]
    download_csv(args)
    c.close()
    

    
    c = conn.cursor()
    c.execute('''SELECT id_file FROM Server_Items''')
    c.close
    #Lecture du fichier table.csv
    reader = csv.reader(open(result),delimiter = '|')
    print "READER = %s"%reader
    c = conn.cursor()
    
    for row in reader:
        try:
            #on retranche l'occurs de fin de ligne
            cols = {}
            cols['$id_file']=row[0]
            cols['$date']=row[1]
            cols['$title']=row[2]
            cols['$description']=row[3]
            cols['$totaldownloads']=row[4]
            cols['$filesize']=  row[5]
            cols['$filename']=  row[6]
            cols['$fileurl']=   row[7]
            cols['$commenttotal']=  row[8]
            cols['$id_cat']=row[9]
            cols['$totalratings']=  row[10]
            cols['$rating']=row[11]
            cols['$type']=row[12]
            cols['$sendemail']=row[13]
            cols['$id_topic']=row[14]
            cols['$keywords']=row[15]
            cols['$createdate']=row[16]
            cols['$previewpictureurl']=row[17]
            cols['$version']=row[18]
            cols['$author']=row[19]
            cols['$description_en']=row[20]
            cols['$script_language']=row[21]

            
            if row in c:
                _updateServerItems(c,cols)
            else:
                _insertServerItems(c,cols)
        except:pass
    #Sauvegarde des modifications
    conn.commit()    
    # On ferme l'instance du curseur
    c.close()
        
def _insertServerItems(c,cols):
    try:
        #Chaque ligne trouvée dans le table.csv est insérée dans la table
        c.execute(nicequery('''INSERT INTO Server_Items 
                                    (id_file,
                                    date,
                                    title,
                                    description,
                                    totaldownloads,
                                    filesize, 
                                    filename, 
                                    fileurl, 
                                    commenttotal, 
                                    id_cat, 
                                    totalratings, 
                                    rating, 
                                    id_topic, 
                                    keywords, 
                                    createdate, 
                                    previewpictureurl, 
                                    version, 
                                    author, 
                                    description_en, 
                                    script_language)
                                VALUES
                                    (
                                    $id_file ,
                                    $date ,
                                    $title ,
                                    $description ,
                                    $totaldownloads ,
                                    $filesize , 
                                    $filename , 
                                    $fileurl , 
                                    $commenttotal , 
                                    $id_cat , 
                                    $totalratings , 
                                    $rating , 
                                    $id_topic , 
                                    $keywords , 
                                    $createdate , 
                                    $previewpictureurl , 
                                    $version , 
                                    $author , 
                                    $description , 
                                    $script_language
                                    )
                           ''',cols))
    except Exception, e:
        print e     

def _updateServerItems(c,cols):
    try:
        #Chaque ligne trouvée dans le table.csv est insérée dans la table
        c.execute(nicequery('''UPDATE Server_Items 
                                    SET date = $date ,
                                    title = $title ,
                                    description =$description ,
                                    totaldownloads = $totaldownloads ,
                                    filesize = $filesize , 
                                    filename = $filename , 
                                    fileurl = $fileurl , 
                                    commenttotal = $commenttotal , 
                                    id_cat = $id_cat , 
                                    totalratings = $totalratings , 
                                    rating = $rating , 
                                    id_topic = $id_topic , 
                                    keywords = $keywords , 
                                    createdate = $createdate , 
                                    previewpictureurl = $previewpictureurl , 
                                    version = $version , 
                                    author = $author , 
                                    description_en = $description , 
                                    script_language = $script_language)
                            WHERE id_file = $id_file''',cols))
    except Exception, e:
        print e         
        
def makeServer_Items():
    conn = sqlite.connect(DB)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS Server_Items
                    (
                    id_file int(11) primary key, 
                    date unix_timestamp, 
                    title varchar (100), 
                    description text, 
                    totaldownloads int(10), 
                    filesize int(10), 
                    filename varchar(100), 
                    fileurl varchar(100), 
                    commenttotal int(10), 
                    id_cat int(10), 
                    totalratings int(10), 
                    rating int(10), 
                    id_topic int(8), 
                    keywords varchar(100), 
                    createdate varchar(10), 
                    previewpictureurl varchar(100), 
                    version varchar(100), 
                    author varchar(100), 
                    description_en text, 
                    script_language  varchar(100)
                    )''')
    conn.commit()
    c.close()

    args = '?action=getitems'
    download_csv(args)
    reader = csv.reader(open(result),delimiter = '|')

    c = conn.cursor()
    for row in reader:
        try:
            cols = {}
            cols['$id_file']=row[0]
            cols['$date']=row[1]
            cols['$title']=row[2]
            cols['$description']=row[3]
            cols['$totaldownloads']=row[4]
            cols['$filesize']=  row[5]
            cols['$filename']=  row[6]
            cols['$fileurl']=   row[7]
            cols['$commenttotal']=  row[8]
            cols['$id_cat']=row[9]
            cols['$totalratings']=row[10]
            cols['$rating']=row[11]
            cols['$type']=row[12]
            cols['$sendemail']=row[13]
            cols['$id_topic']=row[14]
            cols['$keywords']=row[15]
            cols['$createdate']=row[16]
            cols['$previewpictureurl']=row[17]
            cols['$version']=row[18]
            cols['$author']=row[19]
            cols['$description_en']=row[20]
            cols['$script_language']=row[21]

            _insertServerItems(c,cols)
        except:pass
    conn.commit()
    c.close()

def _insertCategories(c,cols):
    try:
        #Chaque ligne trouvée dans le table.csv est insérée dans la table
        c.execute(nicequery('''INSERT into Categories
                            (                    
                            id_cat, 
                            title, 
                            description, 
                            image, 
                            id_parent 
                            )
                        VALUES 
                            (
                            $id_cat ,
                            $title ,
                            $description ,
                            $image ,
                            $id_parent
                            )''',cols))
    except Exception, e:
        print e



def makeCategories():
    """
    Fonction de création de la table, à n'appeler que si la table n'existe pas déjà.
    Pour se faire effectuer un test : if not os.path.isfile(DB):
    """
    conn = sqlite.connect(DB)
    c = conn.cursor()
    
    #Creation de la table
    c.execute ( '''CREATE TABLE IF NOT EXISTS Categories
                    (
                    id_cat int(8) primary key, 
                    title varchar(100), 
                    description text, 
                    image varchar(100), 
                    id_parent int(8), 
                    path varchar(100)
                    )''')
    conn.commit()
    c.close()

    args = '?action=getcat'
    download_csv(args)
    reader = csv.reader(open(result),delimiter = '|')
    c = conn.cursor()

    for row in reader:
        try:
            cols = {}
            cols['$id_cat']=row[0]
            cols['$title']=row[1]
            cols['$description']=row[2]
            cols['$image']=row[3]
            cols['$id_parent']= row[4]
            _insertCategories(c,cols)
        except:pass
        
    #Sauvegarde des modifications
    conn.commit()    
    # On ferme l'instance du curseur
    c.close()
