# -*- coding: cp1252 -*-

#Modules general
import os
import re
import md5
import sys
import time
import ftplib
import urllib
import rarfile
import zipfile
import ConfigParser

from threading import Thread, Timer
from htmlentitydefs import name2codepoint
import elementtree.HTMLTreeBuilder as HTB
from StringIO import StringIO

#from string import * #a verifier si on a besoin de cette methode import *
from BeautifulSoup import BeautifulStoneSoup, Tag, NavigableString  #librairie de traitement XML

#modules XBMC
import xbmc
import xbmcgui

#modules custom
from utilities import *

#module logger
try:
    logger = sys.modules[ "__main__" ].logger
except:
    import script_log as logger


# INITIALISATION CHEMIN RACINE
ROOTDIR = os.getcwd().replace( ";", "" )

#FONCTION POUR RECUPERER LES LABELS DE LA LANGUE.
_ = sys.modules[ "__main__" ].__language__

DIALOG_PROGRESS = xbmcgui.DialogProgress()

# script constants
__svn_revision__ = sys.modules[ "__main__" ].__svn_revision__ or "0"
__version__ = "%s.%s" % ( sys.modules[ "__main__" ].__version__, __svn_revision__ )
__author__ = sys.modules[ "__main__" ].__author__


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
ACTION_CONTEXT_MENU = 117
CLOSE_CONTEXT_MENU = ( ACTION_PARENT_DIR, ACTION_PREVIOUS_MENU, ACTION_CONTEXT_MENU, )

#############################################################################

class cancelRequest( Exception ):
    """
    Exception, merci a Alexsolex
    """
    def __init__( self, value ):
        self.value = value
    def __str__( self ):
        return repr( self.value )


class rssReader:
    """
    Class responsable de la recuperation du flux RSS et de l'extraction des infos RSS
    """
    def __init__( self, rss_title, rssUrl, titlecolor="ffffffff", textcolor="ffffffff" ):
        self.rss_title = rss_title
        self.titlecolor = titlecolor
        self.textcolor = textcolor
        self.rssPage = self.load_feeds_infos( rssUrl )

    def load_feeds_infos( self, url ):
        try:
            html = urllib.urlopen( url )
            source = re.sub( "<!\[CDATA\[|\]\]>", "", html.read() )
            html.close()
            return HTB.parse( StringIO( source ), "utf-8"  ).findall( "channel" )[ 0 ]
        except:
            logger.EXC_INFO( logger.LOG_DEBUG, sys.exc_info() )
            # si on arrive ici le retour est automatiquement None

    def GetRssInfo( self ):
        try:
            if self.rssPage is None: raise
            items_listed = self.rssPage.findall( "item" )
            if not self.rss_title: maintitle = _( 107 )
            else: maintitle = self.rss_title
            items = add_pretty_color( maintitle + ": ", color=self.titlecolor )
            item_sep = add_pretty_color( " - ", color=self.textcolor )
            item_end = len( items_listed )
            for count, item in enumerate( items_listed ):
                try:
                    items += item.findtext( "title" ).replace( u'\xa0', " " )
                except:
                    logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )
                    continue
                if ( ( count + 1 ) < item_end ):
                    items += item_sep

            return maintitle, items
        except:
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )
            return "", ( add_pretty_color( _( 107 ), color=self.titlecolor ) + _( 108 ) )


class scriptextracter:
    """
    Extracteur de script, dezip ou derar une archive et l'efface
    """
    def zipfolder ( self ):
        self.zfile = zipfile.ZipFile( self.archive, 'r' )
        for i in self.zfile.namelist():  # On parcourt l'ensemble des fichiers de l'archive
            if i.endswith( '/' ):
                dossier = self.pathdst + os.sep + i
                try:
                    os.makedirs( dossier )
                except:
                    logger.LOG( logger.LOG_DEBUG, "Erreur creation dossier de l'archive!" )
                    logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )
            else:
                logger.LOG( logger.LOG_DEBUG, "File Case: %s", repr( i ) )

        # On ferme l'archive
        self.zfile.close()

    def  extract( self, archive, TargetDir ):
        self.pathdst = TargetDir
        self.archive = archive
        logger.LOG( logger.LOG_DEBUG, "self.pathdst = %s", self.pathdst )
        logger.LOG( logger.LOG_DEBUG, "self.archive = %s", self.archive )

        if archive.endswith( 'zip' ):
            self.zipfolder() #generation des dossiers dans le cas d'un zip
        #extraction de l'archive
        xbmc.executebuiltin( 'XBMC.Extract(%s, %s)'%( self.archive, self.pathdst ) )

    def getDirName( self, archive ):
        """
        Retourne le nom du repertorie root a l'interieur d'un archive
        Attention il s'agit du nom et non du chemin du repertoire
        """
        dirName = ""
        if archive.endswith( 'zip' ):
            zfile = zipfile.ZipFile( archive, 'r' )
            dirName = zfile.namelist()[ 0 ].split( '/' )[ 0 ]
            logger.LOG( logger.LOG_DEBUG, "scriptextracter::getDirName: dirName = %s", dirName )
            logger.LOG( logger.LOG_DEBUG, repr( zfile.namelist() ) )
            # On verifie que la chaine de caractere est bien un repertoire
            if zfile.namelist()[ 0 ].find( dirName + '/' ) == -1:
                logger.LOG( logger.LOG_DEBUG, "%s n'est pas un repertoire", dirName )
                dirName = ""
            logger.LOG( logger.LOG_DEBUG, "Zip dirname:" )
            logger.LOG( logger.LOG_DEBUG, dirName )
        elif archive.endswith( 'rar' ):
            rfile = rarfile.RarFile( archive, 'r' )
            dirName = rfile.namelist()[ 0 ].split( "\\" )[ 0 ]
            logger.LOG( logger.LOG_DEBUG, "Rar dirname:" )
            logger.LOG( logger.LOG_DEBUG, dirName )
            # On verifie que la chaine de caractere est bien un repertoire
            if rfile.getinfo( dirName ).isdir() == False:
                logger.LOG( logger.LOG_DEBUG, "%s n'est pas un repertoire", dirName )
                dirName = ""
        else:
            logger.LOG( logger.LOG_DEBUG, "Format d'archive non supporter" )
        return dirName



class GDDFTP( ftplib.FTP ):
    """
    Gère la reconnexion au serveur FTP quand la connexion est perdu au moment de l'exécution de la requête.
    Cette classe hérite de ftplib.FTP qui gère le client FTP.
    Crédit: Guigui_
    Source: http://python.developpez.com/faq/?page=FTP#FTPAllTimeConnect
    """
    def __init__( self, adresse, port, user, password ):
        ftplib.FTP.__init__( self, '' )
        self.adresse = adresse
        self.port = port
        self.user = user
        self.password = password

    def Reconnect( self ):
        """
        Permet la ( re )connexion au serveur
        """
        self.connect( self.adresse, self.port ) # Recherche FTP
        self.login( self.user, self.password )  # Connexion

    def Command( self, command, *args ):
        """
        Exécute la requête command avec la liste de paramètres donnés par *args en se reconnectant si nécessaire au serveur
        """
        try: return command( *args )
        except:
            self.Reconnect()
            logger.EXC_INFO( logger.LOG_DEBUG, sys.exc_info(), self )
            return command( *args )


class ftpDownloadCtrl:
    """
    Controleur de download via FTP
    Cette classe gere les download via FTP de fichiers et repertoire
    """
    def __init__( self, host, user, password, remotedirList, localdirList, typeList ):
        """
        Fonction d'init de la classe ftpDownloadCtrl
        Initialise toutes les variables et lance la connection au serveur FTP
        """

        #Initialise les attributs de la classe ftpDownloadCtrl avec les parametres donnes au constructeur
        self.host = host
        self.user = user
        self.port = 21
        self.password = password
        self.remotedirList = remotedirList
        self.localdirList = localdirList
        self.downloadTypeList = typeList

        self.connected = False # status de la connection ( inutile pour le moment )
        self.curLocalDirRoot = ""
        self.curRemoteDirRoot = ""

        logger.LOG( logger.LOG_INFO, "host = %s", self.host )
        logger.LOG( logger.LOG_INFO, "user = %s", self.user )

        #Connection au serveur FTP
        self.openConnection()

    def openConnection( self ):
        """
        Ouvre la connexion FTP
        """
        #Connection au serveur FTP
        try:
            #self.ftp = ftplib.FTP( self.host, self.user, self.password ) # on se connecte
            self.ftp = GDDFTP( self.host, self.port, self.user, self.password ) # on se connecte

            # DEBUG: Seulement pour le dev
            #self.ftp.set_debuglevel( 2 )

            self.connected = True
            logger.LOG( logger.LOG_INFO, "Connecté au serveur FTP" )

        except:
            logger.LOG( logger.LOG_DEBUG, "Exception durant la connection, mpossible de se connecter au serveur FTP: %s", self.host )
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )

    def closeConnection( self ):
        """
        Ferme la connexion FTP
        """
        #on se deconnecte du serveur pour etre plus propre
        try:
            self.ftp.quit
        except:
            logger.LOG( logger.LOG_DEBUG, "Exception durant la fermeture de la connection FTP" )
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )
        else:
            # la fermeture a reussi avec succes
            logger.LOG( logger.LOG_NOTICE, "Connection avec le serveur FTP fermée" )

    def getDirList( self, remotedir ):
        """
        Retourne la liste des elements d'un repertoire sur le serveur
        """
        curDirList = []

        # Recuperation de la liste
        try:
            #curDirList = self.ftp.nlst( remotedir )
            curDirList = self.ftp.Command( self.ftp.nlst, remotedir )
        except:
            logger.LOG( logger.LOG_DEBUG, "Exception durant la recuperation de la liste des fichiers du repertoire: %s", remotedir )
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )

        # Tri de la liste et renvoi
        curDirList.sort( key=str.lower )
        return curDirList

    def isDir( self, pathsrc ):
        """
        Verifie si le chemin sur le serveur correspond a un repertoire
        """
        isDir = True
        # Verifie se on telecharge un repertoire ou d'un fichier
        try:
            #self.ftp.cwd( pathsrc ) # c'est cette commande qui genere l'exception dans le cas d'un fichier
            self.ftp.Command( self.ftp.cwd, pathsrc ) # c'est cette commande qui genere l'exception dans le cas d'un fichier
            # Pas d'excpetion => il s'agit d'un dossier
            logger.LOG( logger.LOG_DEBUG, "isDir: %s EST un DOSSIER", pathsrc )
        except:
            logger.LOG( logger.LOG_DEBUG, "isDir: %s EST un FICHIER", pathsrc )
            isDir = False
        return isDir

    def isAlreadyDownloaded( self, pathsrc, rootdirsrc, typeIndex ):
        """
        Verifie si un repertoire local correspondanf au rootdirsrc existe dans dans pathsrc
        Pour le moment on verifie la meme chose pour un fichier ais cela ne couvre pas encore le cas
        d'un archive extraite localement
        retourne True si c'est le cas, False sinon
        """
        isDownloaded = False
        curLocalDirRoot = self.localdirList[ typeIndex ]
        curRemoteDirRoot = rootdirsrc
        localAbsDirPath = None

        #TODO: couvrir le cas d'une archive?

        # Cree le chemin du repertorie local
        # Extrait le chemin relatif: soustrait au chemin remote le chemin de base: par exemple on veut retirer du chemin; /.passionxbmc/Themes
        remoteRelDirPath = pathsrc.replace( curRemoteDirRoot, '' )

        # On remplace dans le chemin sur le serveur FTP les '/' par le separateur de l'OS sur lequel on est
        localRelDirPath = remoteRelDirPath.replace( '/', os.sep )

        # Cree le chemin local ( ou on va sauver )
        localAbsDirPath = os.path.join( curLocalDirRoot, localRelDirPath )

        # Verifie se on telecharge un repertoire ou d'un fichier
        if self.isDir( pathsrc ):
            # cas d'un repertoire
            isDownloaded = os.path.isdir( localAbsDirPath )
        else:
            # Cas d'un fichier
            isDownloaded = os.path.exists( localAbsDirPath )
        return isDownloaded, localAbsDirPath

    def download( self, pathsrc, rootdirsrc, typeIndex, progressbar_cb=None, dialogProgressWin=None ):
        """
        Telecharge les elements a un chemin specifie ( repertoires, sous repertoires et fichiers )
        a dans un repertorie local dependant du type de telechargement ( theme, scraper, script ... )
        pathsrc     : chemin sur le serveur de l'element a telecharger
        rootdirsrc  : Repertoire root sur le server ( correspondant a un type de download ) - Exemple : "/.passionxbmc/Scraper/" pour les scrapers
        typeIndex   : Index correspondant au type de telechargement, permet notamment de definir le repertorie local de telechargement
        Renvoi le status du download:
            - ( -1 ) pour telechargement annule
            - ( 1 )  pour telechargement OK
        """

        self.curLocalDirRoot = self.localdirList[ typeIndex ]
        self.curRemoteDirRoot = rootdirsrc
        
        if typeIndex == "Themes":
            isSingleFile = False
        else:
            isSingleFile = True

        # Appel de la fonction privee en charge du download - on passe en parametre l'index correspondant au type
        status = self._download( pathsrc, isSingleFile, progressbar_cb, dialogProgressWin, 0, 1 )
        return  status # retour du status du download recupere


    def _download( self, pathsrc, isSingleFile=False, progressbar_cb=None, dialogProgressWin=None, curPercent=0, coeff=1 ):
        """
        Fonction privee ( ne pouvant etre appelee que par la classe ftpDownloadCtrl elle meme )
        Telecharge un element sur le server FTP
        Renvoi le status du download:
            - ( -1 ) pour telechargement annule
            - ( 1 )  pour telechargement OK
        """
        result = 1 # 1 pour telechargement OK
        # Liste le repertoire
        #curDirList = self.ftp.nlst( pathsrc ) #TODO: ajouter try/except
        curDirList = self.ftp.Command( self.ftp.nlst, pathsrc ) #TODO: ajouter try/except
        curDirListSize = len( curDirList ) # Defini le nombre d'elements a telecharger correspondant a 100% - pour le moment on ne gere que ce niveau de granularite pour la progressbar

        for i in curDirList:
            if dialogProgressWin.iscanceled():
                logger.LOG( logger.LOG_WARNING, "Telechargement annuler par l'utilisateur" )
                # Sortie de la boucle via return
                result = -1 # -1 pour telechargement annule
                break
            else:
                # Calcule le pourcentage avant download
                #TODO: verifier que la formule pour le pourcentage est OK ( la ca ette fait un peu trop rapidement )
                percentBefore = min( curPercent + int( ( float( curDirList.index( i )+0 )*100 )/( curDirListSize * coeff ) ), 100 )

                # Mise a jour de la barre de progression ( via callback )
                try:
                    # percent est le poucentage du FICHIER telecharger et non le pourcentage total
                    dialogProgressWin.update( 0, _( 123 )%percentBefore, "%s"%i )
                except:
                    logger.LOG( logger.LOG_DEBUG, "download - Exception calling UI callback for download" )
                    logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )

                # Verifie si le chemin correspond a un repertoire
                if self.isDir( i ):
                    # pathsrc est un repertoire

                    # Telechargement du dossier
                    self._downloaddossier( i, dialogProgressWin=dialogProgressWin, curPercent=percentBefore, coeff=coeff*curDirListSize )

                else:
                    # pathsrc est un fichier

                    # Telechargement du fichier
                    self._downloadfichier( i, isSingleFile=isSingleFile, dialogProgressWin=dialogProgressWin, curPercent=percentBefore, coeff=coeff*curDirListSize )

                percentAfter = min( curPercent + int( ( float( curDirList.index( i )+1 )*100 )/( curDirListSize * coeff ) ), 100 )

                #Mise a jour de la barre de progression ( via callback )
                try:
                    #TODO: Resoudre le pb que la ligbe ci-dessous est invible ( trop rapide )
                    dialogProgressWin.update( 100, _( 123 ) % percentAfter, i )
                    #time.sleep( 1 )
                except:
                    logger.LOG( logger.LOG_DEBUG, "download - Exception calling UI callback for download" )
                    logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )

        # Calcul pourcentage final
        percent = min( curPercent + int( 100/( coeff ) ), 100 )
        try:
            #Mise a jour de la barre de progression ( via callback )
            dialogProgressWin.update( 100, _( 123 ) % percent, i )
        except:
            logger.LOG( logger.LOG_DEBUG, "download - Exception calling UI callback for download" )
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )

        # verifie si on a annule le telechargement
        if dialogProgressWin.iscanceled():
            logger.LOG( logger.LOG_WARNING, "Telechargement annulé par l'utilisateur" )

            # Sortie de la boucle via return
            result = -1 # -1 pour telechargement annule

        return result

    def _downloaddossier( self, dirsrc, progressbar_cb=None, dialogProgressWin=None, curPercent=0, coeff=1 ):
        """
        Fonction privee ( ne pouvant etre appelee que par la classe ftpDownloadCtrl elle meme )
        Telecharge un repertoire sur le server FTP
        Note: fait un appel RECURSIF sur _download
        """
        emptydir = False
        try:
            #dirContent = self.ftp.nlst( dirsrc )
            dirContent = self.ftp.Command( self.ftp.nlst, dirsrc )
            logger.LOG( logger.LOG_DEBUG, "dirContent: %s", repr( dirContent ) )
        except Exception, e:
            # Repertoire non vide -> il faut telecharger les elementss de ce repertoire
            emptydir = True

        # Cree le chemin du repertorie local
        # Extrait le chemin relatif: soustrait au chemin remote le chemin de base: par exemple on veut retirer du chemin; /.passionxbmc/Themes
        remoteRelDirPath = dirsrc.replace( self.curRemoteDirRoot, '' )

        # On remplace dans le chemin sur le serveur FTP les '/' par le separateur de l'OS sur lequel on est
        localRelDirPath = remoteRelDirPath.replace( '/', os.sep )

        # Créé le chemin local ( ou on va sauver )
        localAbsDirPath = os.path.join( self.curLocalDirRoot, localRelDirPath )

        # Créé le dossier
        try:
            if not os.path.isdir( localAbsDirPath ):
                os.makedirs( localAbsDirPath )
        except:
            logger.LOG( logger.LOG_DEBUG, "_downloaddossier: Exception - Impossible de creer le dossier: %s", localAbsDirPath )
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )
        if ( emptydir == False ):
            # Repertoire non vide - lancement du download ( !!!APPEL RECURSIF!!! )
            self._download( dirsrc, dialogProgressWin=dialogProgressWin, curPercent=curPercent, coeff=coeff )

    def _downloadfichier( self, filesrc, isSingleFile=False, dialogProgressWin=None, curPercent=0, coeff=1 ):
        """
        Fonction privee ( ne pouvant etre appelee que par la classe ftpDownloadCtrl elle meme )
        Telecharge un fichier sur le server FTP
        """
        # Recupere la taille du fichier
        remoteFileSize = 1
        block_size = 4096

        # Recuperation de la taille du fichier
        try:
            #self.ftp.sendcmd( 'TYPE I' )
            self.ftp.Command( self.ftp.sendcmd, 'TYPE I' )
            #remoteFileSize = int( self.ftp.size( filesrc ) )
            remoteFileSize = int( self.ftp.Command( self.ftp.size, filesrc ) )
            if remoteFileSize <= 0:
                # Dans le cas ou un fichier n'a pas une taille valide ou corrompue
                remoteFileSize = 1
        except:
            logger.LOG( logger.LOG_DEBUG, "_downloadfichier: Exception - Impossible de recuperer la taille du fichier: %s", filesrc )
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )

        # Créé le chemin du repertorie local
        # Extraction du chemin relatif: soustrait au chemin remote le chemin de base: par exemple on veut retirer du chemin; /.passionxbmc/Themes
        remoteRelFilePath = filesrc.replace( self.curRemoteDirRoot, '' )

        # On remplace dans le chemin sur le serveur FTP les '/' par le separateur de l'OS sur lequel on est
        localRelFilePath = remoteRelFilePath.replace( '/', os.sep )

        # Creation du chemin local ( ou on va sauver )
        localAbsFilePath = xbmc.translatePath( os.path.join( self.curLocalDirRoot, localRelFilePath ) )
        #localFileName = os.path.basename( localAbsFilePath )

        localFile = open( localAbsFilePath, "wb" )
        try:
            # Creation de la fonction callback appele a chaque block_size telecharge
            ftpCB = FtpCallback( remoteFileSize, localFile, filesrc, dialogProgressWin, curPercent, coeff*remoteFileSize, isSingleFile=isSingleFile )

            # Telecahrgement ( on passe la CB en parametre )
            # !!NOTE!!: on utilise un implemenation locale et non celle de ftplib qui ne supporte pas l'interuption d'un telechargement
            result = self.retrbinary( 'RETR ' + filesrc, ftpCB, block_size )
            logger.LOG( logger.LOG_DEBUG, "Response Server FTP sur retrieve: %s", repr( result ) )
        except:
            logger.LOG( logger.LOG_DEBUG, "_downloadfichier: Exception - Impossible de telecharger le fichier: %s", filesrc )
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )
        # On ferme le fichier
        localFile.close()

    def retrbinary( self, cmd, callback, blocksize=8192, rest=None ):
        """
        Cette version de retrbinary permet d'interompte un telechargement en cours alors que la version de ftplib ne le permet pas
        Inspirée du code dispo a http://www.archivum.info/python-bugs-list@python.org/2007-03/msg00465.html
        """
        abort = False
        #self.ftp.voidcmd( 'TYPE I' )
        self.ftp.Command( self.ftp.voidcmd, 'TYPE I' )
        #conn = self.ftp.transfercmd( cmd, rest )
        conn = self.ftp.Command( self.ftp.transfercmd, cmd, rest )
        fp = conn.makefile( 'rb' )
        while 1:
            data = fp.read( blocksize )
            if not data:
                break
            try:
                callback( data )
            except cancelRequest:
                abort = True
                logger.LOG( logger.LOG_NOTICE, "retrbinary: Download ARRETE par l'utilisateur" )
                logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )
                break
        fp.close()
        conn.close()
        if abort:
            self.ftp.Command( self.ftp.abort ) # Afin d'eviter un blockage dans le cas d'un cancel et puis d'un self.ftp.voidresp
        #return self.ftp.voidresp()
        return self.ftp.Command( self.ftp.voidresp )



class FtpCallback( object ):
    """
    Inspired from source Justin Ezequiel ( Thanks )
    http://coding.derkeiler.com/pdf/Archive/Python/comp.lang.python/2006-09/msg02008.pdf
    """
    def __init__( self, filesize, localfile, filesrc, dp=None, curPercent=0, coeff=1 , isSingleFile=False ):
        self.filesize       = filesize
        self.localfile      = localfile
        self.srcName        = filesrc
        self.received       = 0
        self.curPercent     = curPercent # Pourcentage total telecharger ( et non du fichier en cours )
        self.isSingleFile   = isSingleFile  # Flag indiquant si on telecharge un fichier seul, dans ce cas on met a jour le string %
        self.coeff          = coeff
        self.dp             = dp

    def __call__( self, data ):
        if self.dp != None:
            if self.dp.iscanceled():
                #dp.close() #-> will be close in calling function
                logger.LOG( logger.LOG_WARNING, "User pressed CANCEL button" )
                raise cancelRequest, "User pressed CANCEL button"
        self.localfile.write( data )
        self.received += len( data )
        try:
            percent = min( ( self.received*100 )/self.filesize, 100 )
        except:
            logger.LOG( logger.LOG_DEBUG, "FtpCallback - Exception during percent computing AND update" )
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )
            percent = 100

        if self.isSingleFile:
            self.curPercent = percent
        if self.dp != None:
            self.dp.update( percent, _( 123 ) % self.curPercent, self.srcName )


class userDataXML:
    """
    Cette classe represente le fichier sources.xml dans user data
    """
    def __init__( self, filesrc, filedest=None ):
        self.newEntry = False
        self.filesrc = filesrc
        self.filedest = filedest
        self.soup = BeautifulStoneSoup( open( filesrc ).read() )


    def addPluginEntry( self, plugintype, pluginNameStr, pluginPathStr ):
        """
        Ajoute une nouvelle entrée plugin au XML
        Attention pour valider ce changement il est necessaire de faire un commit par la suite
        """
        if plugintype == "Plugins Musique":
            typeTag = self.soup.find( "music" )

        elif plugintype == "Plugins Images":
            typeTag = self.soup.find( "pictures" )

        elif plugintype == "Plugins Programmes":
            typeTag = self.soup.find( "programs" )

        elif plugintype == "Plugins Vidéos":
            typeTag = self.soup.find( "video" )

        sourceTag = Tag( self.soup, "source" )
        typeTag.insert( 0, sourceTag )

        nameTag = Tag( self.soup, "name" )
        sourceTag.insert( 0, nameTag )
        textName = NavigableString( pluginNameStr )
        nameTag.insert( 0, textName )

        pathTag = Tag( self.soup, "path" )
        sourceTag.insert( 1, pathTag )
        pathText = NavigableString( pluginPathStr )
        pathTag.insert( 0, pathText )

        logger.LOG( logger.LOG_NOTICE, "Plugin entry %s added", pluginNameStr )
        self.newEntry = True

    def commit( self ):
        """
        Sauvegarde les modification dans self.filedest
        retourne True si la sauvegarde s'est bine passee False autrement
        """
        # sauvegarde nouveau fichier
        result = False
        if self.newEntry == True:
            logger.LOG( logger.LOG_NOTICE, "userDataXML: sauvegarde du fichier modifié %s", self.filedest )
            try:
                newFile = open( self.filedest, 'w+' )
                newFile.write( self.soup.prettify() )
                newFile.close()
                result = True
            except:
                percent = 100
                logger.LOG( logger.LOG_DEBUG, "userDataXML - Exception durant la creation de %s", self.filedest )
                logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )
                result = False
        else:
            logger.LOG( logger.LOG_NOTICE, "userDataXML: aucun changement pour %s", self.filedest )
            result = False
        return result


class directorySpy:
    """
    Permet d'observer l'ajout ou la suppression des elements d'un repertoire
    """
    def __init__( self, dirpath ):
        """
        Capture le contenu d'un repertoire a l'init
        On s'en servira comme reference dans le future pour observer les modifications dans ce repertoire
        """
        self.dirPath            = dirpath
        self.dirContentInitList = []
        if os.path.isdir( dirpath ):
            # On capture le contenu du repertoire et on le sauve
            self.dirContentInitList = os.listdir( dirpath )
        else:
            logger.LOG( logger.LOG_NOTICE, "directorySpy - __init__: %s n'est pas un repertoire", self.dirPath )
            #TODO: Lever un exception

    def getNewItemList( self ):
        """
        Retourne la liste des nouveaux elements ajoute a un repertorie depuis l'instancaition de directorySpy
        Sinon aucun element a ete ajoutem retourne une liste vide
        """
        # On capture le contenu courant du repertoire
        dirContentCurrentList = os.listdir( self.dirPath )
        try:
            newItemList = list( set( dirContentCurrentList ).difference( set( self.dirContentInitList ) ) )
        except:
            logger.LOG( logger.LOG_DEBUG, "directorySpy - getNewItemList: Exception durant la comparaison du repertoires %s", self.dirPath )
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )
            newItemList = []

        logger.LOG( logger.LOG_DEBUG, "directorySpy - getNewItemList: Liste des nouveaux elements du repertoire %s", self.dirPath )
        logger.LOG( logger.LOG_DEBUG, "newItemList: %s", repr( newItemList ) )

        return newItemList


class configCtrl:
    """
    Controler of configuration
    """
    def __init__( self ):
        """
        Load configuration file, check it, and correct it if necessary
        """
        self.is_conf_valid = False
        try:
            #TODO: deplacer ici l'utilisation du config parser

            # Create config parser
            #self.config = ConfigParser.ConfigParser()
            self.config = config # config parser

            # Read config from .cfg file
            # - Open config file
            #self.config.read( os.path.join( ROOTDIR, "resources", "conf.cfg" ) )

            #self.CACHEDIR = self.config.get( 'InstallPath', 'CacheDir' )
            #self.themesDir = self.config.get( 'InstallPath', 'ThemesDir' )
            #self.scriptDir = self.config.get( 'InstallPath', 'ScriptsDir' )
            #self.scraperDir = self.config.get( 'InstallPath', 'ScraperDir' )
            #self.pluginDir = self.config.get( 'InstallPath', 'PluginDir' )
            #self.pluginMusDir = self.config.get( 'InstallPath', 'PluginMusDir' )
            #self.pluginPictDir = self.config.get( 'InstallPath', 'PluginPictDir' )
            #self.pluginProgDir = self.config.get( 'InstallPath', 'PluginProgDir' )
            #self.pluginVidDir = self.config.get( 'InstallPath', 'PluginVidDir' )
            #self.userdatadir = self.config.get( 'InstallPath', 'UserDataDir' )
            #self.USRPath = self.config.getboolean( 'InstallPath', 'USRPath' )
            #if self.USRPath == True:
            #    self.PMIIIDir = self.config.get( 'InstallPath', 'PMIIIDir' )

            self.host = self.config.get( 'ServeurID', 'host' )
            self.user = self.config.get( 'ServeurID', 'user' )
            self.rssfeed = self.config.get( 'ServeurID', 'rssfeed' )
            self.password = self.config.get( 'ServeurID', 'password' )
            self.itemDescripDir = self.config.get( 'ServeurID', 'contentdescriptorDir' )
            self.itemDescripFile = self.config.get( 'ServeurID', 'contentdescriptor' )

            self.is_conf_valid = True
        except:
            logger.LOG( logger.LOG_DEBUG, "Exception while loading configuration file conf.cfg" )
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )

    def getSrvHost( self ):
        return self.host

    def getSrvPassword( self ):
        return self.password

    def getSrvUser( self ):
        return self.user

    def getSrvItemDescripDir( self ):
        return self.itemDescripDir
    
    def getSrvItemDescripFile( self ):
        """
        Renvoi le nom du fichier de description sur le serveur
        """
        return self.itemDescripFile


class MainWindow( xbmcgui.WindowXML ):
    # control id's
    CONTROL_MAIN_LIST = 150
    CONTROL_FORUM_BUTTON = 300
    CONTROL_OPTIONS_BUTTON = 310

    def __init__( self, *args, **kwargs ):
        xbmcgui.WindowXML.__init__( self, *args, **kwargs )
        """
        Initialisation de l'interface
        """
        self.main_list_last_pos = []

        # Display Loading Window while we are loading the information from the website
        if xbmc.getCondVisibility( "Window.IsActive(progressdialog)" ):
            #si le dialog PROGRESS est visible update
            DIALOG_PROGRESS.update( -1, _( 103 ), _( 110 ) )
        else:
            #si le dialog PROGRESS n'est pas visible affiche le dialog
            DIALOG_PROGRESS.create( _( 0 ), _( 103 ), _( 110 ) )

        #TODO: TOUTES ces varibales devraient etre passees en parametre du constructeur de la classe ( __init__ si tu preferes )
        # On ne devraient pas utiliser de variables globale ou rarement en prog objet

        # Creation du configCtrl
        self.configManager = configCtrl()

        self.host               = host
        self.user               = user
        self.rssfeed            = rssfeed
        self.password           = password
        self.remotedirList      = remoteDirLst
        self.localdirList       = localDirLst
        self.downloadTypeList   = downloadTypeLst

        self.racineDisplayList  = racineDisplayLst
        self.pluginDisplayList  = pluginDisplayLst
        self.pluginsDirSpyList  = []

        self.curDirList         = []
        self.connected          = False # status de la connection ( inutile pour le moment )
        self.index              = ""
        self.scraperDir         = scraperDir
        self.type               = "racine"
        self.USRPath            = USRPath
        self.rightstest         = ""
        self.scriptDir          = scriptDir
        #self.extracter          = scriptextracter() # On cree un instance d'extracter
        self.CacheDir           = CACHEDIR
        self.userDataDir        = userdatadir # userdata directory
        self.targetDir          = ""

        # Verifie si le repertoire cacher existe et le cree s'il n'existent pas encore
        if os.path.exists( CACHEDIR ):
            # Si le repertoire cache existe on s'assure de le vider ( au cas ou on ne serait pas sorti proprement du script )
            self.delDirContent( CACHEDIR )
        else:
            self.verifrep( CACHEDIR )
        self.verifrep( pluginProgDir )

        #TODO: A nettoyer, ton PMIIIDir n'est pas defini pour XBOX sans le test si dessous
        if self.USRPath == True:
            self.PMIIIDir = PMIIIDir

        self.is_started = True


    def onInit( self ):
        # Title of the current pages
        self.setProperty( "Category", _( 10 ) )

        self._get_settings()
        self._set_skin_colours()

        if self.is_started:
            self.is_started = False

            self._start_rss_timer()

            # Connection au serveur FTP
            try:

                self.passionFTPCtrl = ftpDownloadCtrl( self.host, self.user, self.password, self.remotedirList, self.localdirList, self.downloadTypeList )
                self.connected = True

                # Recuperation de la liste des elements
                DIALOG_PROGRESS.update( -1, _( 104 ), _( 110 ) )
                self.updateList()

            except:
                xbmcgui.Dialog().ok( _( 111 ), _( 112 ) )
                logger.LOG( logger.LOG_DEBUG, "Window::__init__: Exception durant la connection FTP" )
                logger.LOG( logger.LOG_DEBUG, "Impossible de se connecter au serveur FTP: %s", self.host )
                logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )

            # Capturons le contenu des sous-repertoires plugins
            for type in self.downloadTypeList:
                if type.find( "Plugins" ) != -1:
                    #self.pluginsInitList.append( os.listdir( self.localdirList[ self.downloadTypeList.index( type ) ] ) )
                    self.pluginsDirSpyList.append( directorySpy( self.localdirList[ self.downloadTypeList.index( type ) ] ) )
                else:
                    self.pluginsDirSpyList.append( None )

            # Close the Loading Window
            DIALOG_PROGRESS.close()

    def _get_settings( self, defaults=False ):
        """ reads settings """
        self.settings = Settings().get_settings( defaults=defaults )

    def _set_skin_colours( self ):
        #xbmcgui.lock()
        try:
            self.setProperty( "style_PMIII.HD", ( "", "true" )[ ( self.settings[ "skin_colours_path" ] == "style_PMIII.HD" ) ] )
            self.setProperty( "Skin-Colours-path", self.settings[ "skin_colours_path" ] )
            self.setProperty( "Skin-Colours", ( self.settings[ "skin_colours" ] or get_default_hex_color() ) )
        except:
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )
        #xbmcgui.unlock()

    def _start_rss_timer( self ):
        # temps entre chaque mise a jour du flux rss 15 min.
        self.rss_update_interval = 60.0 * 15.0
        self.rss_title = ""
        self._stop_rss_timer()
        if self.settings[ "rss_feed" ] != "0":
            try:
                rss_feeds_xml = parse_rss_xml().get( self.settings[ "rss_feed" ] )
                self.rss_update_interval = 60.0 * rss_feeds_xml.get( "updateinterval", 15 )
                self.rss_title = rss_feeds_xml.get( "title", self.rss_title )
                self.rssfeed = rss_feeds_xml.get( "feed", self.rssfeed )
            except:
                logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )
            self.rss_thread = Thread( target=self._set_control_rss_feed )
            self.rss_thread.start()
        else:
            try: self.getControl( 100 ).setVisible( False )
            except: pass

    def _stop_rss_timer( self ):
        try: self.rss_timer.cancel()
        except: pass
        try: self.rss_thread.cancel()
        except: pass

    def _set_control_rss_feed( self ):
        #test fadelabel for rssfeed in Thread
        try:
            title_color = repr( self.getControl( 101 ).getLabel() ).strip( "u'" )
            text_color = repr( self.getControl( 101 ).getLabel2() ).strip( "u'" )
            #print repr( title_color ), repr( text_color )
            self.rss_feed = rssReader( self.rss_title, self.rssfeed, title_color, text_color )
        except:
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )
            try:
                self.rss_feed = rssReader( self.rss_title, self.rssfeed )
            except:
                logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )
        try:
            self.getControl( 100 ).reset()
            self.getControl( 100 ).addLabel( self.rss_feed.GetRssInfo()[ 1 ] )
            self.getControl( 100 ).setVisible( True )
        except:
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )
            try: self.getControl( 100 ).setVisible( False )
            except: pass
            self._stop_rss_timer()
        else:
            try:
                self.rss_timer = Timer( self.rss_update_interval, self._set_control_rss_feed, () )
                self.rss_timer.start()
            except:
                logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )

    def _on_action_control( self, act_ctrl_id ):
        try:
            #button_code_F1_keyboard = 61552
            if ( act_ctrl_id in ( self.CONTROL_FORUM_BUTTON, 61552 ) ):
                from dialog_direct_infos import show_direct_infos
                show_direct_infos( self )
                #on a plus besoin, on le delete
                del show_direct_infos

            elif ( act_ctrl_id in ( ACTION_CONTEXT_MENU, self.CONTROL_OPTIONS_BUTTON ) ):
                from dialog_script_settings import show_settings
                show_settings( self )
                #on a plus besoin du settins, on le delete
                del show_settings

            #button_code_F3_keyboard = 61554
            elif ( act_ctrl_id in ( ACTION_SHOW_INFO, 61554 ) ):
                if ( not self.type.lower() in ( "racine", "plugins", ) ) and ( self.getFocusId() == self.CONTROL_MAIN_LIST ):
                    currentListIndex = self.getControl( self.CONTROL_MAIN_LIST ).getSelectedPosition()
                    if currentListIndex >= 0:
                        selectedItem = os.path.basename( self.curDirList[ currentListIndex ] )
                        from dialog_item_descript import show_descript
                        show_descript( self, selectedItem, self.type )
                        #on a plus besoin du descript, on le delete
                        del show_descript

            else:
                pass
        except:
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )

    def onAction( self, action ):
        """
        Remonte l'arborescence et quitte le script
        """
        try:
            if action == ACTION_PREVIOUS_MENU:
                # Sortie du script

                # On se deconnecte du serveur pour etre plus propre
                self.passionFTPCtrl.closeConnection()

                # On efface le repertoire cache
                self.deleteDir( CACHEDIR )

                # Verifions si la mise a jour du XML a ete activee
                if self.settings[ "xbmc_xml_update" ]:
                    # Capturons le contenu des sous-repertoires plugins a la sortie du script
                    xmlConfFile = userDataXML( os.path.join( self.userDataDir, "sources.xml" ), os.path.join( self.userDataDir, "sourcesNew.xml" ) )
                    for type in self.downloadTypeList:
                        if type.find( "Plugins" ) != -1:
                            # Verifions si des plugins on ete ajoutes
                            newPluginList = None
                            try:
                                #newPluginList = list( set( self.pluginsExitList[ self.downloadTypeList.index( type ) ] ).difference( set( self.pluginsInitList[ self.downloadTypeList.index( type ) ] ) ) )
                                newPluginList = self.pluginsDirSpyList[ self.downloadTypeList.index( type ) ].getNewItemList()
                            except:
                                logger.LOG( logger.LOG_DEBUG, "Exception durant la comparaison des repertoires plugin avant et apres installation" )
                                logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )
                            if len( newPluginList ) > 0:
                                for newPluginName in newPluginList:
                                    # Creation du chemin qui sera ajoute au XML, par ex : "plugin://video/Google video/"
                                    # TODO: extraire des chemins local des plugins les strings, 'music', 'video' ... et n'avoir qu'une implementation
                                    if type == "Plugins Musique":
                                        categorieStr = "music"

                                    elif type == "Plugins Images":
                                        categorieStr = "pictures"

                                    elif type == "Plugins Programmes":
                                        categorieStr = "programs"

                                    elif type == "Plugins Vidéos":
                                        categorieStr = "video"
                                    newPluginPath = "plugin://" + categorieStr + "/" + newPluginName + "/"

                                    # Mise a jour de sources.xml
                                    xmlConfFile.addPluginEntry( type, newPluginName, newPluginPath )
                    # Validation et sauvegarde des modificatiobs du XML
                    newConfFile = xmlConfFile.commit()
                    del xmlConfFile

                    # On verifie si on a cree un nouveau XML
                    if newConfFile:
                        currentTimeStr = str( time.time() )
                        # on demande a l'utilisateur s'il veut remplacer l'ancien xml par le nouveau
                        menuList = [ _( 113 ), _( 114 ), _( 115 ) ]
                        dialog = xbmcgui.Dialog()
                        chosenIndex = dialog.select( _( 116 ), menuList )
                        if chosenIndex == 0:
                            # Mettre a jour la configuation et sortir
                            # On renomme sources.xml en ajoutant le timestamp
                            os.rename( os.path.join( self.userDataDir, "sources.xml" ), os.path.join( self.userDataDir, "sources_%s.xml"%currentTimeStr ) )
                            # On renomme sourcesNew.xml source.xml
                            os.rename( os.path.join( self.userDataDir, "sourcesNew.xml" ), os.path.join( self.userDataDir, "sources.xml" ) )

                        elif chosenIndex == 1:
                            # Mettre a jour la configuation et redemarrer
                            # On renomme source.xml en ajoutant le timestamp
                            os.rename( os.path.join( self.userDataDir, "sources.xml" ), os.path.join( self.userDataDir, "sources_%s.xml"%currentTimeStr ) )
                            # On renomme sourcesNew.xml source.xml
                            os.rename( os.path.join( self.userDataDir, "sourcesNew.xml" ), os.path.join( self.userDataDir, "sources.xml" ) )
                            # on redemarre
                            xbmc.restart()
                        else:
                            # On supprime le xml que nous avons genere
                            os.remove( os.path.join( self.userDataDir, "sourcesNew.xml" ) )
                #on ferme tout
                self._close_script()

            elif action == ACTION_PARENT_DIR:
                # remonte l'arborescence
                # On verifie si on est a l'interieur d'un ses sous section plugin
                #if ( self.type == "Plugins Musique" ) or ( self.type == "Plugins Images" ) or ( self.type == "Plugins Programmes" ) or ( self.type == "Plugins Vidéos" ):
                if not self.main_list_last_pos:
                    try: self.main_list_last_pos.append( self.getControl( self.CONTROL_MAIN_LIST ).getSelectedPosition() )
                    except: self.main_list_last_pos.append( 0 )
                try:
                    if "Plugins " in self.type:
                        self.type = "Plugins"
                    else:
                        # cas standard
                        self.type = "racine"
                    self.updateList()
                except:
                    logger.LOG( logger.LOG_DEBUG, "Window::onAction::ACTION_PREVIOUS_MENU: Exception durant updateList()" )
                    logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )

                if self.main_list_last_pos:
                    self.getControl( self.CONTROL_MAIN_LIST ).selectItem( self.main_list_last_pos.pop() )

            else:
                self._on_action_control( action )
                self._on_action_control( action.getButtonCode() )

        except:
            logger.LOG( logger.LOG_DEBUG, "Window::onAction: Exception" )
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )

    def _close_script( self ):
        #**IMPORTANT** faut annuler les thread avant de fermer le script, sinon xbmc risque de planter
        #NB: le meme scenario va ce produire si vous fermer ou redemarrer xbmc avec le script en marche
        #on annule les thread
        self._stop_rss_timer()
        #on ferme le script
        self.close()

    def onFocus( self, controlID ):
        #self.controlID = controlID
        #cette fonction n'est pas utiliser ici, mais dans les XML si besoin
        #Note: Mais il faut la declarer : )
        pass

    def onClick( self, controlID ):
        """
        Traitement si selection d'un element de la liste
        """
        try:
            if controlID == self.CONTROL_MAIN_LIST:
                try: self.main_list_last_pos.append( self.getControl( self.CONTROL_MAIN_LIST ).getSelectedPosition() )
                except: self.main_list_last_pos.append( 0 )
                if ( self.type == "racine" ):
                    self.index = self.getControl( self.CONTROL_MAIN_LIST ).getSelectedPosition()
                    self.type = self.downloadTypeList[ self.racineDisplayList[ self.getControl( self.CONTROL_MAIN_LIST ).getSelectedPosition() ] ] # On utilise le filtre
                    self.updateList() #on raffraichit la page pour afficher le contenu

                elif ( self.type == "Plugins" ):
                    self.index = self.getControl( self.CONTROL_MAIN_LIST ).getSelectedPosition()
                    self.type = self.downloadTypeList[ self.pluginDisplayList[ self.getControl( self.CONTROL_MAIN_LIST ).getSelectedPosition() ] ] # On utilise le filtre
                    self.updateList() #on raffraichit la page pour afficher le contenu

                else:
                    downloadOK = True
                    correctionPM3bidon = False
                    self.index = self.getControl( self.CONTROL_MAIN_LIST ).getSelectedPosition()

                    source = self.curDirList[ self.index ]

                    if self.type == self.downloadTypeList[ 0 ]:   #Themes
                        # Verifions le themes en cours d'utilisation
                        mySkinInUse = xbmc.getSkinDir()
                        if mySkinInUse in source:
                            # Impossible de telecharger une skin en cours d'utlisation
                            dialog = xbmcgui.Dialog()
                            dialog.ok( _( 117 ), _( 118 ), _( 119 ) )
                            downloadOK = False
                        if 'Project Mayhem III' in source and self.USRPath == True:
                            self.linux_chmod( self.PMIIIDir )
                            if self.rightstest == True:
                                self.localdirList[ 0 ]= self.PMIIIDir
                                downloadOK = True
                                correctionPM3bidon = True
                            else:
                                dialog = xbmcgui.Dialog()
                                dialog.ok( _( 117 ), _( 120 ) )
                                downloadOK = False
                    elif self.type == self.downloadTypeList[ 1 ] and self.USRPath == True:   #Linux Scrapers
                        self.linux_chmod( self.scraperDir )
                        if self.rightstest == True :
                            downloadOK = True
                        else:
                            dialog = xbmcgui.Dialog()
                            dialog.ok( _( 117 ), _( 121 ) )
                            downloadOK = False

                    if source.endswith( 'zip' ) or source.endswith( 'rar' ):
                        self.targetDir = self.localdirList[ self.downloadTypeList.index( self.type ) ]
                        self.localdirList[ self.downloadTypeList.index( self.type ) ]= self.CacheDir

                    if downloadOK == True:
                        continueDownload = True

                        # on verifie le si on a deja telecharge cet element ( ou une de ses version anterieures )
                        isDownloaded, localDirPath = self.passionFTPCtrl.isAlreadyDownloaded( source, self.remotedirList[ self.downloadTypeList.index( self.type ) ], self.downloadTypeList.index( self.type ) )

                        if ( isDownloaded ) and ( localDirPath != None ):
                            logger.LOG( logger.LOG_NOTICE, "Repertoire deja present localement" )
                            # On traite le repertorie deja present en demandant a l'utilisateur de choisir
                            continueDownload = self.processOldDownload( localDirPath )
                        else:
                            logger.LOG( logger.LOG_DEBUG, "localDirPath: %s", repr( localDirPath ) )
                            logger.LOG( logger.LOG_DEBUG, "isDownloaded: %s", repr( isDownloaded ) )

                        if continueDownload == True:
                            # Fenetre de telechargement

                            dp = xbmcgui.DialogProgress()
                            lenbasepath = len( self.remotedirList[ self.downloadTypeList.index( self.type ) ] )
                            downloadItem = source[ lenbasepath: ]
                            percent = 0
                            dp.create( _( 122 ) % downloadItem, _( 123 ) % percent )

                            # Type est desormais reellement le type de download, on utlise alors les liste pour recuperer le chemin que l'on doit toujours passer
                            # on appel la classe passionFTPCtrl avec la source a telecharger
                            downloadStatus = self.passionFTPCtrl.download( source, self.remotedirList[ self.downloadTypeList.index( self.type ) ], self.downloadTypeList.index( self.type ), progressbar_cb=self.updateProgress_cb, dialogProgressWin = dp )
                            #dp.close()

                            if downloadStatus == -1:
                                # Telechargment annule par l'utilisateur
                                title = _( 124 )
                                message1 = "%s: %s" % ( self.type, downloadItem )
                                message2 = _( 125 )
                                message3 = _( 126 )
                                if xbmcgui.Dialog().yesno( title, message1, message2, message3 ):
                                    logger.LOG( logger.LOG_WARNING, "Suppression du repertoire %s", localDirPath )
                                    if os.path.isdir( localDirPath ):
                                        if self.deleteDir( localDirPath ):
                                            xbmcgui.Dialog().ok( _( 127 ), _( 128 ), localDirPath, _( 129 ) )
                                        else:
                                            xbmcgui.Dialog().ok( _( 111 ), _( 130 ), localDirPath )
                                    else:
                                        try:
                                            os.remove( localDirPath )
                                            xbmcgui.Dialog().ok( _( 131 ), _( 132 ), localDirPath, _( 129 ) )
                                        except Exception, e:
                                            xbmcgui.Dialog().ok( _( 111 ), _( 133 ), localDirPath )
                            else:
                                title = _( 134 )
                                message1 = "%s: %s" % ( self.type, downloadItem )
                                message2 = _( 135 )
                                message3 = self.localdirList[ self.downloadTypeList.index( self.type ) ]

                                self._save_downloaded_property()
                                xbmcgui.Dialog().ok( title, message1, message2, message3 )

                            #TODO: Attention correctionPM3bidon n'est pa defini dans le cas d'un scraper ou script
                            #      Je l'ai donc defini a False au debut
                            # On remet a la bonne valeur initiale self.localdirList[ 0 ]
                            if correctionPM3bidon == True:
                                self.localdirList[ 0 ] = themesDir
                                correctionPM3bidon = False
                            # On se base sur l'extension pour determiner si on doit telecharger dans le cache.
                            # Un tour de passe passe est fait plus haut pour echanger les chemins de destination avec le cache, le chemin de destination
                            # est retabli ici 'il s'agit de targetDir'
                            if downloadItem.endswith( 'zip' ) or downloadItem.endswith( 'rar' ):
                                if downloadStatus != -1:
                                    installCancelled = False
                                    installError = None
                                    #dp = xbmcgui.DialogProgress()
                                    #dp.create( _( 136 ) % downloadItem, _( 123 ) % percent )
                                    #dialogUI = xbmcgui.DialogProgress()
                                    dp.create( _( 137 ), _( 138 ) % downloadItem, _( 110 ) )

                                    #Appel de la classe d'extraction des archives
                                    remoteDirPath = self.remotedirList[ self.downloadTypeList.index( self.type ) ]#chemin ou a ete telecharge le script
                                    localDirPath = self.localdirList[ self.downloadTypeList.index( self.type ) ]
                                    archive = source.replace( remoteDirPath, localDirPath + os.sep )#remplacement du chemin de l'archive distante par le chemin local temporaire
                                    self.localdirList[ self.downloadTypeList.index( self.type ) ] = self.targetDir
                                    #fichierfinal0 = archive.replace( localDirPath, self.localdirList[ self.downloadTypeList.index( self.type ) ] )
                                    #if fichierfinal0.endswith( '.zip' ):
                                    #    fichierfinal = fichierfinal0.replace( '.zip', '' )
                                    #elif fichierfinal0.endswith( '.rar' ):
                                    #    fichierfinal = fichierfinal0.replace( '.rar', '' )

                                    import extractor
                                    process_error = False
                                    # on extrat tous dans le cache et si c'est OK on copy par la suite
                                    file_path, OK = extractor.extract( archive, report=True )
                                    #print OK, file_path
                                    if self.type == "Scrapers":
                                        # cas des Scrapers
                                        # ----------------
                                        #self.extracter.extract( archive, self.localdirList[ self.downloadTypeList.index( self.type ) ] )
                                        destination = self.localdirList[ self.downloadTypeList.index( self.type ) ]
                                        if ( OK == bool( file_path ) ) and os.path.exists( file_path ):
                                            extractor.copy_inside_dir( file_path, destination )
                                    else:
                                        # Cas des scripts et plugins
                                        # --------------------------
                                        # Recuperons le nom du repertorie a l'interieur de l'archive:
                                        dirName = ""
                                        if ( OK == bool( file_path ) ) and os.path.exists( file_path ):
                                            dirName = os.path.basename( file_path )#self.extracter.getDirName( archive )
                                            destination = os.path.join( self.localdirList[ self.downloadTypeList.index( self.type ) ], os.path.basename( file_path ) )

                                        if dirName == "":
                                            installError = _( 139 ) % archive
                                            logger.LOG( logger.LOG_ERROR, "Erreur durant l'extraction de %s - impossible d'extraire le nom du repertoire", archive )
                                        else:
                                            #destination = os.path.join( self.localdirList[ self.downloadTypeList.index( self.type ) ], dirName )
                                            logger.LOG( logger.LOG_NOTICE, destination )
                                            if os.path.exists( destination ):
                                                # Repertoire déja présent
                                                # On demande a l'utilisateur ce qu'il veut faire
                                                if self.processOldDownload( destination ):
                                                    try:
                                                        #logger.LOG( logger.LOG_NOTICE, "Extraction de %s vers %s", archive, self.localdirList[ self.downloadTypeList.index( self.type ) ] )
                                                        #self.extracter.extract( archive, self.localdirList[ self.downloadTypeList.index( self.type ) ] )
                                                        if ( OK == bool( file_path ) ) and os.path.exists( file_path ):
                                                            extractor.copy_dir( file_path, destination )
                                                    except:
                                                        process_error = True
                                                else:
                                                    installCancelled = True
                                                    logger.LOG( logger.LOG_WARNING, "L'installation de %s a ete annulee par l'utilisateur", downloadItem  )
                                            else:
                                                # Le Repertoire n'est pas present localement -> on peut deplacer le repertoire depuis cache
                                                try:
                                                    #logger.LOG( logger.LOG_NOTICE, "Extraction de %s vers %s", archive, self.localdirList[ self.downloadTypeList.index( self.type ) ] )
                                                    #self.extracter.extract( archive, self.localdirList[ self.downloadTypeList.index( self.type ) ] )
                                                    if ( OK == bool( file_path ) ) and os.path.exists( file_path ):
                                                        extractor.copy_dir( file_path, destination )
                                                except:
                                                    process_error = True

                                    del extractor
                                    # Close the Loading Window
                                    #dialogUI.close()

                                    if process_error:
                                        installError = _( 140 ) % archive
                                        logger.LOG( logger.LOG_ERROR, "Exception durant l'extraction de %s", archive )
                                        logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )

                                    if installCancelled == False and installError == None:
                                        self._save_downloaded_property()
                                        xbmcgui.Dialog().ok( _( 141 ), _( 142 ) % downloadItem, _( 143 ) )
                                    else:
                                        if installError != None:
                                            # Erreur durant l'install ( meme si on a annule )
                                            xbmcgui.Dialog().ok( _( 144 ), installError, _( 145 ) )
                                        elif installCancelled == True:
                                            # Install annulee
                                            xbmcgui.Dialog().ok( _( 146 ), _( 147 ) % downloadItem )
                                        else:
                                            # Install annulee
                                            xbmcgui.Dialog().ok( _( 144 ), _( 148 ), _( 145 ) )
                                else:
                                    # On remet a la bonne valeur initiale self.localdirList
                                    self.localdirList[ self.downloadTypeList.index( self.type ) ] = self.targetDir

                            # Close the Loading Window
                            dp.close()

            else:
                self._on_action_control( controlID )

        except:
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )

    def _load_downloaded_property( self ):
        try:
            file_path = os.path.join( logger.DIRECTORY_DATA, "downloaded.txt" )
            self.downloaded_property = eval( file( file_path, "r" ).read() )
        except:
            logger.EXC_INFO( logger.LOG_DEBUG, sys.exc_info(), self )
            self.downloaded_property = set()

    def _save_downloaded_property( self ):
        try:
            self._load_downloaded_property()
            selected_label = self.getControl( self.CONTROL_MAIN_LIST ).getSelectedItem().getLabel()
            self.downloaded_property.update( [ md5.new( selected_label ).hexdigest() ] )
            file_path = os.path.join( logger.DIRECTORY_DATA, "downloaded.txt" )
            file( file_path, "w" ).write( repr( self.downloaded_property ) )
        except:
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )
        else:
            self.getControl( self.CONTROL_MAIN_LIST ).getSelectedItem().setProperty( "Downloaded", "isDownloaded" )

    def updateProgress_cb( self, percent, dp=None ):
        """
        Met a jour la barre de progression
        """
        #TODO Dans le futur, veut t'on donner la responsabilite a cette fonction le calcul du pourcentage????
        try:
            dp.update( percent )
        except:
            percent = 100
            dp.update( percent )

    def updateList( self ):
        """
        Mise a jour de la liste affichee
        """
        self._load_downloaded_property()
        if not xbmc.getCondVisibility( "Window.IsActive(progressdialog)" ):
            DIALOG_PROGRESS.create( _( 0 ), _( 104 ), _( 110 ) )
        # On verifie self.type qui correspond au type de liste que l'on veut afficher
        if ( self.type == "racine" ):
            #liste virtuelle des sections
            #del self.curDirList[ : ] # on vide la liste
            self.curDirList = self.racineDisplayList

        elif ( self.type == "Plugins" ):
            #liste virtuelle des sections
            self.curDirList = self.pluginDisplayList
        #elif ( self.type == "Plugins Musique" ) or ( self.type == "Plugins Images" ) or ( self.type == "Plugins Programmes" ) or ( self.type == "Plugins Vidéos" ):
        elif "Plugins " in self.type:
            self.curDirList = self.passionFTPCtrl.getDirList( self.remotedirList[ self.pluginDisplayList[ self.index ] ] )
        else:
            #liste virtuelle des sections
            #del self.curDirList[ : ] # on vide la liste

            #liste physique d'une section sur le ftp
            self.curDirList = self.passionFTPCtrl.getDirList( self.remotedirList[ self.index ] )

        xbmcgui.lock()

        # Clear all ListItems in this control list
        self.getControl( self.CONTROL_MAIN_LIST ).reset()

        # Calcul du nombre d'elements de la liste
        itemnumber = len( self.curDirList )

        # On utilise la fonction range pour faire l'iteration sur index
        for j in range( itemnumber ):
            imagePath = ""
            if ( self.type == "racine" ):
                # Nom de la section
                sectionName = self.downloadTypeList[ self.racineDisplayList[ j ] ] # On utilise le filtre
                # Met a jour le titre:
                self.setProperty( "Category", _( 10 ) )

                # Affichage de la liste des sections
                # -> On compare avec la liste affichee dans l'interface
                if sectionName == self.downloadTypeList[ 0 ]:
                    # Theme
                    imagePath = "icone_theme.png"
                    sectionLocTitle = _( 11 )
                elif sectionName == self.downloadTypeList[ 1 ]:
                    # Scraper
                    imagePath = "icone_scrapper.png"
                    sectionLocTitle = _( 12 )
                elif sectionName == self.downloadTypeList[ 2 ]:
                    # Script
                    imagePath = "icone_script.png"
                    sectionLocTitle = _( 13 )
                elif sectionName == self.downloadTypeList[ 3 ]:
                    # Plugin
                    imagePath = "icone_script.png"
                    sectionLocTitle = _( 14 )

                displayListItem = xbmcgui.ListItem( sectionLocTitle, "", thumbnailImage = imagePath )
                displayListItem.setProperty( "Downloaded", "" )
                self.getControl( self.CONTROL_MAIN_LIST ).addItem( displayListItem )
                
            elif ( self.type == "Plugins" ):
                # Nom de la section
                sectionName = self.downloadTypeList[ self.pluginDisplayList[ j ] ] # On utilise le filtre
                # Met a jour le titre:
                self.setProperty( "Category", _( 14 ) )
            
                if sectionName == self.downloadTypeList[ 4 ]:  
                    # Music
                    imagePath = "passion-icone-music.png"
                    sectionLocTitle = _( 15 )
                elif sectionName == self.downloadTypeList[ 5 ]: 
                    # Pictures
                    imagePath = "passion-icone-pictures.png"
                    sectionLocTitle = _( 16 )
                elif sectionName == self.downloadTypeList[ 6 ]: 
                    # Programs
                    imagePath = "passion-icone-programs.png"
                    sectionLocTitle = _( 17 )
                elif sectionName == self.downloadTypeList[ 7 ]: 
                    # Video
                    imagePath = "passion-icone-video.png"
                    sectionLocTitle = _( 18 )

                displayListItem = xbmcgui.ListItem( sectionLocTitle, "", thumbnailImage = imagePath )
                displayListItem.setProperty( "Downloaded", "" )
                self.getControl( self.CONTROL_MAIN_LIST ).addItem( displayListItem )
            
            
            #elif ( self.type == "Plugins Musique" ) or ( self.type == "Plugins Images" ) or ( self.type == "Plugins Programmes" ) or ( self.type == "Plugins Vidéos" ):
            elif "Plugins " in self.type:
                # Element de la liste
                ItemListPath = self.curDirList[ j ]

                lenindex = len( self.remotedirList[ self.pluginDisplayList[ self.index ] ] ) # on a tjrs besoin de connaitre la taille du chemin de base pour le soustraire/retirer du chemin global plus tard

                # Met a jour le titre et les icones:
                if self.type == self.downloadTypeList[ 4 ]:  
                    # Music
                    self.setProperty( "Category", _( 15 ) )
                    imagePath = "passion-icone-music.png"
                elif self.type == self.downloadTypeList[ 5 ]: 
                    # Pictures
                    self.setProperty( "Category", _( 16 ) )
                    imagePath = "passion-icone-pictures.png"
                elif self.type == self.downloadTypeList[ 6 ]:
                    # Programs
                    self.setProperty( "Category", _( 17 ) )
                    imagePath = "passion-icone-programs.png"
                elif self.type == self.downloadTypeList[ 7 ]:
                    # Video
                    self.setProperty( "Category", _( 18 ) )
                    imagePath = "passion-icone-video.png"

                # nettoyage du nom: replace les souligner pas un espace et enleve l'extension
                try: item2download = os.path.splitext( ItemListPath[ lenindex: ] )[ 0 ].replace( "_", " " )
                except: item2download = ItemListPath[ lenindex: ]

                if self.downloaded_property.__contains__( md5.new( item2download ).hexdigest() ):
                    already_downloaded = "true"
                else:
                    already_downloaded = ""

                displayListItem = xbmcgui.ListItem( item2download, "", thumbnailImage = imagePath )
                displayListItem.setProperty( "Downloaded", already_downloaded )
                self.getControl( self.CONTROL_MAIN_LIST ).addItem( displayListItem )

            else:
                # Element de la liste
                ItemListPath = self.curDirList[ j ]

                #affichage de l'interieur d'une section
                #self.numindex = self.index
                lenindex = len( self.remotedirList[ self.index ] ) # on a tjrs besoin de connaitre la taille du chemin de base pour le soustraire/retirer du chemin global plus tard

                # Met a jour le titre et les icones:
                if self.type == self.downloadTypeList[ 0 ]: #Themes
                    self.setProperty( "Category", _( 11 ) )
                    imagePath = "icone_theme.png"
                elif self.type == self.downloadTypeList[ 1 ]: #Scrapers
                    self.setProperty( "Category", _( 12 ) )
                    imagePath = "icone_scrapper.png"
                elif self.type == self.downloadTypeList[ 2 ]: #Scripts
                    self.setProperty( "Category", _( 13 ) )
                    imagePath = "icone_script.png"

                # nettoyage du nom: replace les souligner pas un espace et enleve l'extension
                try: item2download = os.path.splitext( ItemListPath[ lenindex: ] )[ 0 ].replace( "_", " " )
                except: item2download = ItemListPath[ lenindex: ]

                if self.downloaded_property.__contains__( md5.new( item2download ).hexdigest() ):
                    already_downloaded = "true"
                else:
                    already_downloaded = ""

                displayListItem = xbmcgui.ListItem( item2download, "", thumbnailImage = imagePath )
                displayListItem.setProperty( "Downloaded", already_downloaded )
                self.getControl( self.CONTROL_MAIN_LIST ).addItem( displayListItem )
        xbmcgui.unlock()

        DIALOG_PROGRESS.close()

    def deleteDir( self, path ):
        """
        Efface un repertoire et tout son contenu ( le repertoire n'a pas besoin d'etre vide )
        retourne True si le repertoire est effece False sinon
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
                    logger.LOG( logger.LOG_DEBUG, "deleteDir: Exception la suppression du reperoire: %s", path )
                    logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )
            # Suppression du repertoire pere
            try:
                os.rmdir( path )
            except:
                result = False
                logger.LOG( logger.LOG_DEBUG, "deleteDir: Exception la suppression du reperoire: %s", path )
                logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )
        else:
            logger.LOG( logger.LOG_DEBUG, "deleteDir: %s n'est pas un repertoire", path )
            result = False

        return result

    def delDirContent( self, path ):
        """
        Efface tous le contenu d'un repertoire ( fichiers  et sous-repertoires )
        mais pas le repertoire lui meme
        folder: chemin du repertpoire local
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
                    logger.LOG( logger.LOG_DEBUG, "delDirContent: Exception la suppression du contenu du reperoire: %s", path )
                    logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )
        else:
            logger.LOG( logger.LOG_ERROR, "delDirContent: %s n'est pas un repertoire", path )
            result = False

        return result


    def verifrep( self, folder ):
        """
        Source: myCine
        Verifie l'existance  d'un repertoire et le cree si besoin
        """
        try:
            if not os.path.exists( folder ):
                os.makedirs( folder )
        except:
            logger.LOG( logger.LOG_DEBUG, "verifrep - Exception durant la creation du repertoire: %s", folder )
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )
            pass

    def linux_chmod( self, path ):
        """
        Effectue un chmod sur un repertoire pour ne plus etre bloque par les droits root sur plateforme linux
        """
        Wtest = os.access( path, os.W_OK )
        if Wtest == True:
            self.rightstest = True
            logger.LOG( logger.LOG_NOTICE, "linux chmod rightest OK" )
        else:
            xbmcgui.Dialog().ok( _( 19 ), _( 20 ) )
            keyboard = xbmc.Keyboard( "", _( 21 ), True )
            keyboard.doModal()
            if keyboard.isConfirmed():
                password = keyboard.getText()
                PassStr = "echo %s | "%password
                ChmodStr = "sudo -S chmod 777 -R %s"%path
                try:
                    os.system( PassStr + ChmodStr )
                    self.rightstest = True
                except:
                    self.rightstest = False
                    logger.LOG( logger.LOG_ERROR, "erreur CHMOD %s", path )
                    logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )
            else:
                self.rightstest = False

    def processOldDownload( self, localAbsDirPath ):
        """
        Traite les ancien download suivant les desirs de l'utilisateur
        retourne True si le download peut continuer.
        """
        continueDownload = True

        # Verifie se on telecharge un repertoire ou d'un fichier
        if os.path.isdir( localAbsDirPath ):
            # Repertoire
            menuList = [ _( 150 ), _( 151 ), _( 152 ), _( 153 ) ]
            dialog = xbmcgui.Dialog()
            chosenIndex = dialog.select( _( 149 ) % os.path.basename( localAbsDirPath ), menuList )
            if chosenIndex == 0:
                # Supprimer
                self.deleteDir( localAbsDirPath )
            elif chosenIndex == 1: # Renommer
                # Suppression du repertoire
                keyboard = xbmc.Keyboard( os.path.basename( localAbsDirPath ), _( 154 ) )
                keyboard.doModal()
                if ( keyboard.isConfirmed() ):
                    inputText = keyboard.getText()
                    os.rename( localAbsDirPath, localAbsDirPath.replace( os.path.basename( localAbsDirPath ), inputText ) )
                    xbmcgui.Dialog().ok( _( 155 ), localAbsDirPath.replace( os.path.basename( localAbsDirPath ), inputText ) )
                del keyboard
            elif chosenIndex == 2: # Ecraser
                pass
            else:
                continueDownload = False
        else:
            # Fichier
            logger.LOG( logger.LOG_ERROR, "processOldDownload: Fichier : %s - ce cas n'est pas encore traite", localAbsDirPath )
            #TODO: cas a implementer

        return continueDownload



########
#
# Main
#
########



def go():
    #Fonction de demarrage
    file_xml = "passion-main.xml"
    #depuis la revision 14811 on a plus besoin de mettre le chemin complet, la racine suffit
    dir_path = ROOTDIR
    #recupere le nom du skin et si force_fallback est vrai, il va chercher les images du defaultSkin.
    current_skin, force_fallback = getUserSkin()

    w = MainWindow( file_xml, dir_path, current_skin, force_fallback )
    #w = MainWindow()
    w.doModal()
    del w

##############################################################################
#                   Initialisation conf.cfg                                  #
##############################################################################
fichier = os.path.join( ROOTDIR, "resources", "conf.cfg" )
config = ConfigParser.ConfigParser()
config.read( fichier )

##############################################################################
#                   Initialisation parametres locaux                         #
##############################################################################
CACHEDIR = config.get( 'InstallPath', 'CacheDir' )
themesDir = config.get( 'InstallPath', 'ThemesDir' )
scriptDir = config.get( 'InstallPath', 'ScriptsDir' )
scraperDir = config.get( 'InstallPath', 'ScraperDir' )
pluginDir = config.get( 'InstallPath', 'PluginDir' )
pluginMusDir = config.get( 'InstallPath', 'PluginMusDir' )
pluginPictDir = config.get( 'InstallPath', 'PluginPictDir' )
pluginProgDir = config.get( 'InstallPath', 'PluginProgDir' )
pluginVidDir = config.get( 'InstallPath', 'PluginVidDir' )
userdatadir = config.get( 'InstallPath', 'UserDataDir' )
USRPath = config.getboolean( 'InstallPath', 'USRPath' )
if USRPath == True:
    PMIIIDir = config.get( 'InstallPath', 'PMIIIDir' )
RACINE = True

##############################################################################
#                   Initialisation parametres serveur                        #
##############################################################################
host = config.get( 'ServeurID', 'host' )
user = config.get( 'ServeurID', 'user' )
rssfeed = config.get( 'ServeurID', 'rssfeed' )
password = config.get( 'ServeurID', 'password' )


downloadTypeLst = [ "Themes", "Scrapers", "Scripts", "Plugins", "Plugins Musique", "Plugins Images", "Plugins Programmes", "Plugins Vidéos" ]
#TODO: mettre les chemins des rep sur le serveur dans le fichier de conf
remoteDirLst = [ "/.passionxbmc/Themes/", "/.passionxbmc/Scraper/", "/.passionxbmc/Scripts/", "/.passionxbmc/Plugins/", "/.passionxbmc/Plugins/Music/", "/.passionxbmc/Plugins/Pictures/", "/.passionxbmc/Plugins/Programs/", "/.passionxbmc/Plugins/Videos/" ]
localDirLst = [ themesDir, scraperDir, scriptDir, pluginDir, pluginMusDir, pluginPictDir, pluginProgDir, pluginVidDir ]

racineDisplayLst = [ 0, 1, 2, 3 ] # Liste de la racine: Cette liste est un filtre ( utilisant l'index ) sur les listes ci-dessus
pluginDisplayLst = [ 4, 5, 6, 7 ] # Liste des plugins : Cette liste est un filtre ( utilisant l'index ) sur les listes ci-dessus

##############################################################################
#                   Version et auteurs                                       #
##############################################################################
version = config.get( 'Version', 'version' )
author = 'Seb & Temhil'
graphicdesigner = 'Jahnrik'

##############################################################################
#                   Verification parametres locaux et serveur                #
##############################################################################
#les infos auteur, version et graphic, etc sont deja dans le LOG et dans le future dans le "dialog_credits.py + passion-dialog_credits.xml"
#logger.LOG( logger.LOG_DEBUG, "===================================================================" )
#logger.LOG( logger.LOG_DEBUG, "Installer Passion-XBMC %s STARTS".center( 85 ), __version__ )
#logger.LOG( logger.LOG_DEBUG, "Auteurs : %s".center( 85 ), __author__ )
#logger.LOG( logger.LOG_DEBUG, "===================================================================" )

#logger.LOG( logger.LOG_DEBUG, "FTP host: %s", host )
#logger.LOG( logger.LOG_DEBUG, "Chemin ou les themes seront telecharges: %s", themesDir )

if __name__ == "__main__":
    #ici on pourrait faire des action si le script était lancé en tant que programme
    logger.LOG( logger.LOG_INFO, "demarrage du script INSTALLEUR.py en tant que programme" )
    go()
else:
    #ici on est en mode librairie importée depuis un programme
    pass
