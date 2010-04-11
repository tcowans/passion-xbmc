
__all__ = [
    # public names
    #"copy_func",
    "ListItemObject",
    "fileMgr"
    ]

# Modules general
import os
import sys
from traceback import print_exc

# Modules XBMC
import xbmc

# Modules custom
import shutil2
from CONF import *
from utilities import *


# INITIALISATION CHEMIN RACINE
ROOTDIR = os.getcwd().replace( ";", "" )

#FONCTION POUR RECUPERER LES LABELS DE LA LANGUE.
_ = sys.modules[ "__main__" ].__language__



############################################################################
# Get actioncodes from keymap.xml
############################################################################
#ACTION_MOVE_LEFT = 1
#ACTION_MOVE_RIGHT = 2
#ACTION_MOVE_UP = 3
#ACTION_MOVE_DOWN = 4
#ACTION_PAGE_UP = 5
#ACTION_PAGE_DOWN = 6
#ACTION_SELECT_ITEM = 7
#ACTION_HIGHLIGHT_ITEM = 8
ACTION_PARENT_DIR = 9
ACTION_PREVIOUS_MENU = 10
ACTION_SHOW_INFO = 11
#ACTION_PAUSE = 12
#ACTION_STOP = 13
#ACTION_NEXT_ITEM = 14
#ACTION_PREV_ITEM = 15
ACTION_CONTEXT_MENU = 117 # ACTION_MOUSE_RIGHT_CLICK *sa marche maintenant avec les derniere SVN*
CLOSE_CONTEXT_MENU = ( ACTION_PARENT_DIR, ACTION_PREVIOUS_MENU, ACTION_CONTEXT_MENU, )




##################################################


#def copy_func( cpt_blk, taille_blk, total_taille, dialogCB=None ):
#    try:
#        updt_val = int( ( cpt_blk * taille_blk ) / 10.0 / total_taille )
#        if updt_val > 100: updt_val = 100
#        if dialogCB != None:
#            dialogCB.update( updt_val )
#    except:
#        pass
#        #dialogCB.update( 100 )
#    # DON'T ALLOW Progress().iscanceled() BUG CREATE, FIXED SOON
#    #if xbmcgui.DialogProgress().iscanceled():
#    #    xbmcgui.DialogProgress().close()

class ListItemObject:
    """
    Structure de donnee definissant un element de la liste
    """
    def __init__( self, type='unknown', name='', local_path=None, thumb='default' ):
        self.type       = type
        self.name       = name
        self.local_path = local_path
        self.thumb      = thumb

    def __repr__(self):
        return "(%s, %s, %s, %s)" % ( self.type, self.name, self.local_path, self.thumb )


class fileMgr:
    """
    File manager
    """
    def verifrep(self, folder):
        """
        Check a folder exists and make it if necessary
        Return True if success, False otherwise
        """
        result = True
        try:
            #print("verifrep check if directory: " + folder + " exists")
            if not os.path.exists(folder):
                print "verifrep: Impossible to find the directory - Trying to create directory: %s" % folder
                os.makedirs(folder)
        except Exception, e:
            result = False
            print "verifrep: Exception while creating the directory: %s" % folder
            print_exc()
        return result

    def listDirFiles(self, path):
        """
        List the files of a directory
        @param path: path of directory we want to list the content of
        """
        print "listDirFiles: Liste le repertoire: %s" % path
        dirList = os.listdir( str( path ) )

        return dirList

    def renameItem( self, base_path, old_name, new_name):
        """
        Rename an item (file or directory)
        Return True if success, False otherwise
        """
        print "renameItem"
        print "renameItem - base_path"
        print base_path
        print "renameItem - old_name"
        print old_name
        print "renameItem - new_name"
        print new_name
        result = True
        try:
            if base_path == None:
                # old_name and new_name are path and not just filename
                print "renameItem - base_path == None"
                os.rename( old_name, new_name )                
            else:
                # old_name and new_name are just filename
                # concatenating with base path
                print "renameItem - base_path != None"
                os.rename( os.path.join(base_path, old_name), os.path.join(base_path, new_name) )
        except:
            result = False
            print "renameItem: Exception renaming Item: %s" % old_name
            print_exc()
        return result
    
    def deleteItem( self, item_path):
        """
        Delete an item (file or directory)
        Return True if success, False otherwise
        """
        result = None
        if os.path.isdir(item_path):
            result = self.deleteDir(item_path)
        else:
            result = self.deleteFile(item_path)
            
        return result

    def deleteFile(self, filename):
        """
        Delete a file form download directory
        @param filename: name of the file to delete
        Return True if success, False otherwise
        """
        result = True
        try:
            if os.path.exists( filename ):
                os.remove( filename )
            else:
                print "deleteFile: File %s does NOT exist" % filename
                result = False
        except:
            result = False
            print "deleteFile: Exception deleting file: %s" % filename
            print_exc()
        return result

    def deleteDir( self, path ):
        """
        Delete a directory and all in content (files and subdirs)
        Note: the directory does NOT need to be empty
        Return True if success, False otherwise
        """
        result = True
        if os.path.isdir( path ):
            dirItems=os.listdir( path )
            for item in dirItems:
                itemFullPath=os.path.join( path, item )
                try:
                    if os.path.isfile( itemFullPath ):
                        # Fichier
                        os.remove( itemFullPath )
                    elif os.path.isdir( itemFullPath ):
                        # Repertoire
                        self.deleteDir( itemFullPath )
                except:
                    result = False
                    print "deleteDir: Exception deleting directory: %s" % path
                    print_exc()
            # Suppression du repertoire pere
            try:
                os.rmdir( path )
            except:
                result = False
                print "deleteDir: Exception deleting directory: %s" % path
                print_exc()
        else:
            print "deleteDir: %s is not a directory" % path
            result = False

        return result

    def extract(self,archive,targetDir):
        """
        Extract an archive in targetDir
        """
        xbmc.executebuiltin('XBMC.Extract(%s,%s)'%(archive,targetDir) )

    def linux_is_write_access( self, path ):
        """
        Linux
        Verifie si on a les droit en ecriture sur un element
        """
        Wtest = os.access( path, os.W_OK )
        if Wtest == True:
            rightstest = True
            print "linux chmod rightest OK for %s" % path
        else:
            print "linux chmod rightest NOT OK for %s" % path
            rightstest = False
        return rightstest

    def linux_set_write_access( self, path, password ):
        """
        Linux
        Effectue un chmod sur un repertoire pour ne plus etre bloque par les droits root sur plateforme linux
        Retourne True en cas de succes ou False dans le cas contraire
        """
        PassStr = "echo %s | "%password
        ChmodStr = "sudo -S chmod 777 -R %s"%path
        try:
            os.system( PassStr + ChmodStr )
            rightstest = True
        except:
            rightstest = False
            print "erreur CHMOD %s" % path
            print_exc()
        return rightstest


