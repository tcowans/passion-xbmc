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

   
def update_datas():
    if not os.path.isfile(DB):
        make_install_paths()
        make_Categories()
        makeServer_Items()
        updateServerItems()
        update_categories()
    else:
        update_categories()
        updateServerItems()
    
def download_csv(args):
    #On récupère le fichier table.csv
    baseurl = 'http://passion-xbmc.org/exportdownloads.php/'
    url = baseurl + args
    loc = urllib.URLopener()
    loc.retrieve(url, result)   
    return result  

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
    """
    conn = sqlite.connect(DB)
    #Initialisation de la base de donnée
    c = conn.cursor()
    try:
        c.execute('''SELECT max(date) FROM Server_Items''')
        args = '?action=getitems&param=%s'%c.fetchone()[0]
        c.execute('''DELETE * FROM Server_Items''')
    except:
        makeServer_Items()
        args = '?action=getitems'
    
    c = conn.cursor()
    reader = csv.reader(open(download_csv(args)),delimiter = '|')    
    
    for row in reader:
        print row
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
            cols['$id_new']=row[22]

            _insertServerItems(c,cols)
        except Exception, e:
            print e
            
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
                                    script_language,
                                    id_new)
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
                                    $script_language ,
                                    $id_new
                                    )
                           ''',cols))
    except Exception, e:
        print e     
        
def makeServer_Items():
    conn = sqlite.connect(DB)
    c = conn.cursor()
    try:
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
                        script_language  varchar(100),
                        id_new varchar(5)
                        )''')
        conn.commit()
    except Exception, e:
        print e    


def update_categories():
    conn = sqlite.connect(DB)
    #Initialisation de la base de donnée
    c = conn.cursor()
    try:
        c.execute('''DELETE * FROM Categories''')
    except:
        make_Categories()
    args = '?action=getcat'
    reader = csv.reader(open(download_csv(args)),delimiter = '|')
    c = conn.cursor()

    for row in reader:
        print row
        try:
            cols = {}
            cols['$id_cat']=row[0]
            cols['$title']=row[1]
            cols['$description']=row[2]
            cols['$image']=row[3]
            cols['$id_parent']= row[4]
            print "row[5] = %s"%row[5]
            c.execute('''SELECT id_path FROM install_paths WHERE title LIKE ?''',(row[5],))
            cols['$id_path'] = str(c.fetchone()[0])
            print "cols['$id_path'] = %s"%cols['$id_path']  
                
            
            _insertCategories(c,cols)
        except Exception, e:
            print 'erreur categorie'
            print e
        
    #Sauvegarde des modifications
    conn.commit()    
    # On ferme l'instance du curseur
    c.close()
    
def _insertCategories(c,cols):
    try:
        c.execute(nicequery('''INSERT into Categories
                            (                    
                            id_cat, 
                            title, 
                            description, 
                            image, 
                            id_parent,
                            id_path
                            )
                        VALUES 
                            (
                            $id_cat ,
                            $title ,
                            $description ,
                            $image ,
                            $id_parent ,
                            $id_path
                            )''',cols))
    except Exception, e:
        print 'erreur insert'
        print e

def make_Categories():
    """
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
                    id_path varchar(100)
                    )''')
    conn.commit()

def make_install_paths():

    conn = sqlite.connect(DB)
    c = conn.cursor()

    c.execute ( '''CREATE TABLE IF NOT EXISTS Install_Paths
                    (
                    id_path integer primary key autoincrement, 
                    title varchar(100), 
                    path varchar(100)
                    )''')
    conn.commit()
    
    from CONF import SetConfiguration
    Path = SetConfiguration()
    
    for ind in range(len(Path['title'])):
        path = {}
        path['$title'] = Path['title'][ind]
        path['$path'] = Path['path'][ind]
        print path['$title']
        print path['$path']
        c.execute(nicequery('''INSERT INTO Install_Paths 
                    (
                    title,
                    path
                    )
                    VALUES
                    (
                    $title ,
                    $path
                    ) ''',path))
    conn.commit()
    c.close
  

    
