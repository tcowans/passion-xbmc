
# Modules general
import os
import sys

# Modules custom
from utilities import *


# INITIALISATION CHEMIN RACINE
ROOTDIR = os.getcwd().replace( ";", "" )

#FONCTION POUR RECUPERER LES LABELS DE LA LANGUE.
_ = sys.modules[ "__main__" ].__language__


##################################################

TYPE_ROOT            = _( 10 )
TYPE_SKIN            = _( 11 )
TYPE_SCRAPER         = _( 12 )      
TYPE_SCRIPT          = _( 13 )      
TYPE_PLUGIN          = _( 14 )  
TYPE_PLUGIN_MUSIC    = _( 15 )
TYPE_PLUGIN_PICTURES = _( 16 )
TYPE_PLUGIN_PROGRAMS = _( 17 )
TYPE_PLUGIN_VIDEO    = _( 18 )

#INDEX_ROOT            = None
INDEX_SKIN            = 0
INDEX_SCRAPER         = 1      
INDEX_SCRIPT          = 2      
INDEX_PLUGIN          = 3  
INDEX_PLUGIN_MUSIC    = 4
INDEX_PLUGIN_PICTURES = 5
INDEX_PLUGIN_PROGRAMS = 6
INDEX_PLUGIN_VIDEO    = 7


THUMB_SKIN            = "icone_theme.png"
THUMB_SCRAPER         = "icone_scrapper.png"
THUMB_SCRIPT          = "icone_script.png"
THUMB_PLUGIN          = "icone_script.png"
THUMB_PLUGIN_MUSIC    = "passion-icone-music.png"
THUMB_PLUGIN_PICTURES = "passion-icone-pictures.png"
THUMB_PLUGIN_PROGRAMS = "passion-icone-programs.png"
THUMB_PLUGIN_VIDEO    = "passion-icone-video.png"  


##############################################################################
#                   Initialisation parametres locaux                         #
##############################################################################
DIR_CACHE           = config.get( 'InstallPath', 'CacheDir' )
DIR_SKIN            = config.get( 'InstallPath', 'ThemesDir' )
DIR_SCRAPER         = config.get( 'InstallPath', 'ScraperDir' )
DIR_SCRIPT          = config.get( 'InstallPath', 'ScriptsDir' )
DIR_PLUGIN          = config.get( 'InstallPath', 'PluginDir' )
DIR_PLUGIN_MUSIC    = config.get( 'InstallPath', 'PluginMusDir' )
DIR_PLUGIN_PICTURES = config.get( 'InstallPath', 'PluginPictDir' )
DIR_PLUGIN_PROGRAMS = config.get( 'InstallPath', 'PluginProgDir' )
DIR_PLUGIN_VIDEO    = config.get( 'InstallPath', 'PluginVidDir' )

userdatadir = config.get( 'InstallPath', 'UserDataDir' )
USRPath = config.getboolean( 'InstallPath', 'USRPath' )
if USRPath == True:
    PMIIIDir = config.get( 'InstallPath', 'PMIIIDir' )
RACINE = True

SRV_DIR_SKIN            = "/.passionxbmc/Themes/"
SRV_DIR_SCRAPER         = "/.passionxbmc/Scraper/"
SRV_DIR_SCRIPT          = "/.passionxbmc/Scripts/"
SRV_DIR_PLUGIN          = "/.passionxbmc/Plugins/"
SRV_DIR_PLUGIN_MUSIC    = "/.passionxbmc/Plugins/Music/"
SRV_DIR_PLUGIN_PICTURES = "/.passionxbmc/Plugins/Pictures/"
SRV_DIR_PLUGIN_PROGRAMS = "/.passionxbmc/Plugins/Programs/"
SRV_DIR_PLUGIN_VIDEO    = "/.passionxbmc/Plugins/Videos/"

INDEX_SRV_ITEM_FORMAT_DIR      = 0
INDEX_SRV_ITEM_FORMAT_FILE_ZIP = 1
INDEX_SRV_ITEM_FORMAT_FILE_RAR = 1
INDEX_SRV_ITEM_FORMAT_INVALID  = 2

#downloadTypeLst = [ "Themes", "Scrapers", "Scripts", "Plugins", "Plugins Musique", "Plugins Images", "Plugins Programmes", "Plugins Vidéos" ]
#TODO: mettre les chemins des rep sur le serveur dans le fichier de conf

#racineDisplayLst = [ 0, 1, 2, 3 ] # Liste de la racine: Cette liste est un filtre ( utilisant l'index ) sur les listes ci-dessus
#pluginDisplayLst = [ 4, 5, 6, 7 ] # Liste des plugins : Cette liste est un filtre ( utilisant l'index ) sur les listes ci-dessus




typeList     = [ TYPE_SKIN,    TYPE_SCRAPER,    TYPE_SCRIPT,    TYPE_PLUGIN,    TYPE_PLUGIN_MUSIC,    TYPE_PLUGIN_PICTURES,    TYPE_PLUGIN_PROGRAMS,    TYPE_PLUGIN_VIDEO    ] # Note: TYPE_ROOT est en dehors de la liste
thumbList    = [ THUMB_SKIN,   THUMB_SCRAPER,   THUMB_SCRIPT,   THUMB_PLUGIN,   THUMB_PLUGIN_MUSIC,   THUMB_PLUGIN_PICTURES,   THUMB_PLUGIN_PROGRAMS,   THUMB_PLUGIN_VIDEO   ] # Note: TYPE_ROOT est en dehors de la liste
serverDirLst = [ SRV_DIR_SKIN, SRV_DIR_SCRAPER, SRV_DIR_SCRIPT, SRV_DIR_PLUGIN, SRV_DIR_PLUGIN_MUSIC, SRV_DIR_PLUGIN_PICTURES, SRV_DIR_PLUGIN_PROGRAMS, SRV_DIR_PLUGIN_VIDEO ]
localDirLst  = [ DIR_SKIN,     DIR_SCRAPER,     DIR_SCRIPT,     DIR_PLUGIN,     DIR_PLUGIN_MUSIC,     DIR_PLUGIN_PICTURES,     DIR_PLUGIN_PROGRAMS,     DIR_PLUGIN_VIDEO     ]

itemFormatLst = [ '', '.zip', '.rar', 'invalid_format' ]
#TODO: mettre les chemins des rep sur le serveur dans le fichier de conf
#localDirLst = [ themesDir, scraperDir, scriptDir, pluginDir, pluginMusDir, pluginPictDir, pluginProgDir, pluginVidDir ]

rootDisplayList   = [ INDEX_SKIN, INDEX_SCRAPER, INDEX_SCRIPT, INDEX_PLUGIN ]                                # Liste de la racine: Cette liste est un filtre ( utilisant l'index ) sur les listes ci-dessus
pluginDisplayList = [ INDEX_PLUGIN_MUSIC, INDEX_PLUGIN_PICTURES, INDEX_PLUGIN_PROGRAMS, INDEX_PLUGIN_VIDEO ] # Liste des plugins : Cette liste est un filtre ( utilisant l'index ) sur les listes ci-dessus




class ListItemObject:
    """
    Structure de donnees definissant un element de la liste
    """
    def __init__( self, type='unknown', name=None, thumb=None ):
        self.type  = type        # Type de l'item: racine, script, plugin, scraper, plugin video ...
        self.name  = name        # Nom de l'item        
        self.thumb = ( thumb, thumbList( typeList.index( type ) )) [thumb == None]  # Thumb

    def __repr__( self ):
        return "(%s, %s, %s)" % ( self.type, self.name, self.thumb ) 

    
class LocalListItemObject(ListItemObject):
    """
    Structure de donnees definissant un element local (fichier, repertoire ... -> Utiliser par le manager par ex.)
    """
    def __init__( self, type='unknown', name=None, thumb=None, local_path=None ):
        ListItemObject.__init__( self, type=type, name=name, thumb=thumb )
        self.local_path = local_path  # Chemin local de l'item
        self.name       = ( name, os.path.splitext(os.path.basename(local_path))[0])[ name == None and local_path != None ]  # Nom de l'item
    
    def __repr__( self ):
        return "(%s, %s, %s, %s)" % ( self.type, self.name, self.thumb, self.local_path ) 

    
#class FtpListItemObject(ListItemObject):
#    """
#    Structure de donnees definissant un element FTP (fichier, repertoire ... -> Utiliser par l'installer par ex.)
#    """
#    def __init__( self, type='unknown', name='', thumb='default', server_path=None, added_item_date=None, server_item_format=None, local_install_dir=None ):
#        ListItemObject.__init__( type=type, name=name, thumb=thumb )
#        self.server_path        = server_path
#        self.added_item_date   = added_item_date
#        self.server_item_format = server_item_format
#        self.local_install_dir  = local_install_dir
#    
#    def __repr__(self):
#        return "(%s, %s, %s, %s, %s, %s, %s)" % ( self.type, self.name, self.thumb, self.server_path, self.added_item_date, self.server_item_format, self.local_install_dir ) 
    
class FtpListItemObject(ListItemObject):
    """
    Structure de donnees definissant un element FTP (fichier, repertoire ... -> Utiliser par l'installer par ex.)
    """
    def __init__( self, type='unknown', name=None, thumb=None, server_path=None, added_item_date=None, clean_name=True ):
        ListItemObject.__init__( type=type, name=name, thumb=thumb )
        # Lorsque le nom n'est pas defni on le cree a partir de server_path et on le nettoie si clean_name == True
        self.name               = ( name, ( os.path.basename(server_path), os.path.splitext(os.path.basename(server_path))[0].replace( "_", " " ) )[ clean_name == True ] )[ name == None and local_path != None ]  # Nom de l'item
        self.server_path        = server_path
        self.added_item_date    = added_item_date
        self.server_item_format = itemFormatLst.index( os.path.splitext( os.path.basename( server_path ) )[ 1 ].lower())
        self.local_install_dir  = localDirLst( typeList.index( type ) )
    
    def __repr__( self ):
        return "(%s, %s, %s, %s, %s, %s, %s)" % ( self.type, self.name, self.thumb, self.server_path, self.added_item_date, self.server_item_format, self.local_install_dir ) 


class ExtentedFtpListItemObject(FtpListItemObject):
    """
    Structure de donnees definissant un element FTP avec sa description 
    """
    def __init__( self, type='unknown', name='', thumb='default', server_path=None, added_item_date=None, server_item_format=None, local_install_dir=None ):
        FtpListItemObject.__init__( type=type, name=name, thumb=thumb,server_path=server_path, added_item_date=added_item_date, server_item_format=server_item_format, local_install_dir=local_install_dir )
        self.version         = version
        self.language        = language
        self.creation_date   = creation_date
        self.local_pic_path  = local_pic_path
        self.server_pic_path = server_pic_path
        self.previewVideoURL = previewVideoURL
        self.description     = description
        self.author          = author
    
    def __repr__( self ):
        return "(%s, %s, %s, %s, %s, %s, %s)" % ( self.type, self.name, self.thumb, self.server_path, self.added_item_date, self.server_item_format, self.local_install_dir ) 


    def set_extented_info(self, extInfosList):
        """
        Format extInfosList[]: fileName, title, version, language, date, added, previewPicture, previewVideoURL, description_fr, description_en, thumbnail, author
        """
        # extInfosList[0] # Non utilise car deja dans server_path
        self.name            = ( self.name, extInfosList[1] )[ extInfosList[1] != extInfosList[0] ] # On modifie Name seulement si fileName != Title
        self.version         = extInfosList[2]
        self.language        = extInfosList[3]
        self.creation_date   = extInfosList[4] or ""
        self.added_item_date = extInfosList[5] or extInfosList[ 4 ] or ""
        self.local_pic_path  = extInfosList[6] or None

    
class ListOfItems:
    """
    Liste de ListItemObject
    """
    def __init__( self ):
        self.ItemsList    = []

    def append( self, listItemObj ):
        pass
    
    def sort ( self, key = None ):
        """
        Tri la liste en prenant pour cle un des champ de ListItemObject
        """
        
