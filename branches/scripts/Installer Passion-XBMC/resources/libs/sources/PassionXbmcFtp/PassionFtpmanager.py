"""
FTP Manager: this module manager FTP connection, browsing, download ...
"""
# Modules general
import os
import sys
import ftplib
from traceback import print_exc

# Modules XBMC
import xbmc
import xbmcgui

# Module custom
import Item

try:
    from ItemInstaller import cancelRequest
except:
    print_exc()
#FONCTION POUR RECUPERER LES LABELS DE LA LANGUE.
_ = sys.modules[ "__main__" ].__language__

class GDDFTP( ftplib.FTP ):
    """
    Gere la reconnexion au serveur FTP quand la connexion est perdu au moment de l'execution de la requete.
    Cette classe herite de ftplib.FTP qui gere le client FTP.
    Credit: Guigui_
    Source: http://python.developpez.com/faq/?page=FTP#FTPAllTimeConnect
    """
    def __init__( self, adresse, port, user, password ):
        ftplib.FTP.__init__( self, '' )
        self.adresse  = adresse
        self.port     = port
        self.user     = user
        self.password = password

    def reconnect( self ):
        """
        Permet la ( re )connexion au serveur
        """
        self.connect( self.adresse, self.port ) # Recherche FTP
        self.login( self.user, self.password )  # Connexion

    def command( self, command, *args ):
        """
        Execute la requete command avec la liste de parametres donnes par *args en se reconnectant si necessaire au serveur
        """
        try: return command( *args )
        except:
            self.reconnect()
            #print_exc()
            return command( *args )

    def quit(self):
        """
        Ferme la connexion FTP
        """
        #on se deconnecte du serveur pour etre plus propre
        try:
            #self.quit()
            self.close()
        except:
            print "Exception durant la fermeture de la connection FTP"
            print_exc()
        else:
            # la fermeture a reussi avec succes
            print "Connection avec le serveur FTP fermee"
    

class FtpDownloadCtrl:
    """
    Controleur de download via FTP
    Cette classe gere les download via FTP de fichiers et repertoire
    """
    #def __init__( self, host, user, password, remotedirList, localdirList, typeList, cacheDir ):
    def __init__( self, host, user, password, remotedirList, cacheDir ):
        """
        Fonction d'init de la classe FtpDownloadCtrl
        Initialise toutes les variables et lance la connection au serveur FTP
        """

        #Initialise les attributs de la classe FtpDownloadCtrl avec les parametres donnes au constructeur
        self.host             = host
        self.user             = user
        self.port             = 21
        self.password         = password
        self.remotedirList    = remotedirList
        #self.localdirList     = localdirList
        #self.downloadTypeList = typeList
        self.CACHEDIR         = cacheDir

        self.connected = False # status de la connection ( inutile pour le moment )
        self.curLocalDirRoot = ""
        self.curRemoteDirRoot = ""

        print "host = %s" % self.host
        print "user = %s" % self.user

        #Connection au serveur FTP
        self.openConnection()

    def openConnection( self ):
        """
        Ouvre la connexion FTP
        """
        #Connection au serveur FTP
        try:
            #self.ftp = ftplib.FTP( self.host, self.user, self.password ) # on se connecte
            self.ftp = GDDFTP( self.host, self.port, self.user, self.password ) 
            
            # on se connecte
            self.ftp.reconnect()

            # DEBUG: Seulement pour le dev
            #self.ftp.set_debuglevel( 2 )

            self.connected = True
            print "Connecte au serveur FTP"

        except:
            print "Exception durant la connection, mpossible de se connecter au serveur FTP: %s" % self.host
            print_exc()

    def closeConnection( self ):
        """
        Ferme la connexion FTP
        """
        #on se deconnecte du serveur pour etre plus propre
        try:
            self.ftp.quit()
        except:
            print "Exception durant la fermeture de la connection FTP"
            print_exc()
        else:
            # la fermeture a reussi avec succes
            print "Connection avec le serveur FTP fermee"

    def getDirList( self, remotedir ):
        """
        Retourne la liste des elements d'un repertoire sur le serveur
        """
        curDirList = []

        # Recuperation de la liste
        try:
            #curDirList = self.ftp.nlst( remotedir )
            print "remotedir = %s" % remotedir
            curDirList = self.ftp.command( self.ftp.nlst, remotedir )
        except:
            print "Exception durant la recuperation de la liste des fichiers du repertoire: %s" % remotedir
            print_exc()

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
            self.ftp.command( self.ftp.cwd, pathsrc ) # c'est cette commande qui genere l'exception dans le cas d'un fichier
            # Pas d'excpetion => il s'agit d'un dossier
            print "isDir: %s EST un DOSSIER" % pathsrc
        except:
            print "isDir: %s EST un FICHIER" % pathsrc
            isDir = False
        return isDir

#    def isAlreadyDownloaded( self, pathsrc, rootdirsrc, typeIndex ):
#        """
#        Verifie si un repertoire local correspondanf au rootdirsrc existe dans dans pathsrc
#        Pour le moment on verifie la meme chose pour un fichier ais cela ne couvre pas encore le cas
#        d'un archive extraite localement
#        retourne True si c'est le cas, False sinon
#        """
#        isDownloaded = False
#        curLocalDirRoot = self.localdirList[ typeIndex ]
#        curRemoteDirRoot = rootdirsrc
#        localAbsDirPath = None
#
#        #TODO: couvrir le cas d'une archive?
#
#        # Cree le chemin du repertorie local
#        # Extrait le chemin relatif: soustrait au chemin remote le chemin de base: par exemple on veut retirer du chemin; /Themes
#        remoteRelDirPath = pathsrc.replace( curRemoteDirRoot, '' )
#
#        # On remplace dans le chemin sur le serveur FTP les '/' par le separateur de l'OS sur lequel on est
#        localRelDirPath = remoteRelDirPath.replace( '/', os.sep )
#
#        # Cree le chemin local ( ou on va sauver )
#        localAbsDirPath = os.path.join( curLocalDirRoot, localRelDirPath )
#
#        # Verifie se on telecharge un repertoire ou d'un fichier
#        if self.isDir( pathsrc ):
#            # cas d'un repertoire
#            isDownloaded = os.path.isdir( localAbsDirPath )
#        else:
#            # Cas d'un fichier
#            isDownloaded = os.path.exists( localAbsDirPath )
#        return isDownloaded, localAbsDirPath

    #def download( self, pathsrc, rootdirsrc, typeIndex, progressbar_cb=None, dialogProgressWin=None ):
    def download( self, pathsrc, type, progressbar_cb=None, dialogProgressWin=None ):
        """
        Telecharge les elements a un chemin specifie ( repertoires, sous repertoires et fichiers )
        a dans un repertorie local dependant du type de telechargement ( theme, scraper, script ... )
        pathsrc     : chemin sur le serveur de l'element a telecharger
        rootdirsrc  : Repertoire root sur le server ( correspondant a un type de download ) - Exemple : "/Scraper/" pour les scrapers
        typeIndex   : Index correspondant au type de telechargement, permet notamment de definir le repertorie local de telechargement
        Renvoi le status du download:
            - ( -1 ) pour telechargement annule
            - ( 1 )  pour telechargement OK
        """

        typeIndex = Item.get_type_index(type)
        #self.curLocalDirRoot = self.localdirList[ typeIndex ]
        self.curLocalDirRoot = self.CACHEDIR # Downloading in cache directory first
        #self.curRemoteDirRoot = rootdirsrc
        self.curRemoteDirRoot = self.remotedirList[ typeIndex ]

        #if typeIndex == "Themes":
        if typeIndex == Item.TYPE_SKIN:
            isSingleFile = False
        else:
            isSingleFile = True

        # Appel de la fonction privee en charge du download - on passe en parametre l'index correspondant au type
        status = self._download( self.curRemoteDirRoot+pathsrc, isSingleFile, progressbar_cb, dialogProgressWin, 0, 1 )

        #TODO: disconenct form server once big downlaod is done
        #self.closeConnection()
        print "FtpDownloadCtrl - download - status: %s"%status
        return  status # retour du status du download recupere


    def _download( self, pathsrc, isSingleFile=False, progressbar_cb=None, dialogProgressWin=None, curPercent=0, coeff=1 ):
        """
        Fonction privee ( ne pouvant etre appelee que par la classe FtpDownloadCtrl elle meme )
        Telecharge un element sur le server FTP
        Renvoi le status du download:
            - ( -1 ) pour telechargement annule
            - ( 1 )  pour telechargement OK
        """
        status     = "OK" # Status of download :[OK | ERROR | CANCELED]
        #result = 1 # 1 pour telechargement OK
        # Liste le repertoire
        #curDirList = self.ftp.nlst( pathsrc ) #TODO: ajouter try/except
        curDirList = self.ftp.command( self.ftp.nlst, pathsrc ) #TODO: ajouter try/except
        curDirListSize = len( curDirList ) # Defini le nombre d'elements a telecharger correspondant a 100% - pour le moment on ne gere que ce niveau de granularite pour la progressbar

        for i in curDirList:
            if dialogProgressWin.iscanceled():
                print "Telechargement annuler par l'utilisateur"
                # Sortie de la boucle via return
                #result = -1 # -1 pour telechargement annule
                status = "CANCELED"
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
                    print "download - Exception calling UI callback for download"
                    print_exc()

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
                    print "download - Exception calling UI callback for download"
                    print_exc()

        # Calcul pourcentage final
        percent = min( curPercent + int( 100/( coeff ) ), 100 )
        try:
            #Mise a jour de la barre de progression ( via callback )
            dialogProgressWin.update( 100, _( 123 ) % percent, i )
        except:
            print "download - Exception calling UI callback for download"
            print_exc()

        # verifie si on a annule le telechargement
        if dialogProgressWin.iscanceled():
            print "Telechargement annule par l'utilisateur"

            # Sortie de la boucle via return
            #result = -1 # -1 pour telechargement annule
            status = "CANCELED"

        #return result
        return status

    def _downloaddossier( self, dirsrc, progressbar_cb=None, dialogProgressWin=None, curPercent=0, coeff=1 ):
        """
        Fonction privee ( ne pouvant etre appelee que par la classe FtpDownloadCtrl elle meme )
        Telecharge un repertoire sur le server FTP
        Note: fait un appel RECURSIF sur _download
        """
        emptydir = False
        try:
            #dirContent = self.ftp.nlst( dirsrc )
            dirContent = self.ftp.command( self.ftp.nlst, dirsrc )
            print "dirContent: %s" % repr( dirContent )
        except Exception, e:
            # Repertoire non vide -> il faut telecharger les elementss de ce repertoire
            emptydir = True

        # Cree le chemin du repertorie local
        # Extrait le chemin relatif: soustrait au chemin remote le chemin de base: par exemple on veut retirer du chemin; /Themes
        remoteRelDirPath = dirsrc.replace( self.curRemoteDirRoot, '' )

        # On remplace dans le chemin sur le serveur FTP les '/' par le separateur de l'OS sur lequel on est
        localRelDirPath = remoteRelDirPath.replace( '/', os.sep )

        # Cree le chemin local ( ou on va sauver )
        localAbsDirPath = os.path.join( self.curLocalDirRoot, localRelDirPath )

        # Cree le dossier
        try:
            if not os.path.isdir( localAbsDirPath ):
                os.makedirs( localAbsDirPath )
        except:
            print "_downloaddossier: Exception - Impossible de creer le dossier: %s" % localAbsDirPath
            print_exc()
        if ( emptydir == False ):
            # Repertoire non vide - lancement du download ( !!!APPEL RECURSIF!!! )
            self._download( dirsrc, dialogProgressWin=dialogProgressWin, curPercent=curPercent, coeff=coeff )

    def _downloadfichier( self, filesrc, isSingleFile=False, dialogProgressWin=None, curPercent=0, coeff=1 ):
        """
        Fonction privee ( ne pouvant etre appelee que par la classe FtpDownloadCtrl elle meme )
        Telecharge un fichier sur le server FTP
        """
        print "_downloadfichier - filesrc:"
        print filesrc
        # Recupere la taille du fichier
        remoteFileSize = 1
        block_size = 4096

        # Recuperation de la taille du fichier
        try:
            #self.ftp.sendcmd( 'TYPE I' )
            self.ftp.command( self.ftp.sendcmd, 'TYPE I' )
            #remoteFileSize = int( self.ftp.size( filesrc ) )
            remoteFileSize = int( self.ftp.command( self.ftp.size, filesrc ) )
            if remoteFileSize <= 0:
                # Dans le cas ou un fichier n'a pas une taille valide ou corrompue
                remoteFileSize = 1
        except Exception, e:
            print "_downloadfichier: Exception - Impossible de recuperer la taille du fichier: %s" % filesrc
            print_exc()

        # Cree le chemin du repertorie local
        # Extraction du chemin relatif: soustrait au chemin remote le chemin de base: par exemple on veut retirer du chemin; /Themes
        remoteRelFilePath = filesrc.replace( self.curRemoteDirRoot, '' )

        # On remplace dans le chemin sur le serveur FTP les '/' par le separateur de l'OS sur lequel on est
        localRelFilePath = remoteRelFilePath.replace( '/', os.sep )

        # Creation du chemin local ( ou on va sauver )
        localAbsFilePath = xbmc.translatePath( os.path.join( self.curLocalDirRoot, localRelFilePath ) )
        #localFileName = os.path.basename( localAbsFilePath )

        print "_downloadfichier - localAbsFilePath:"
        print localAbsFilePath
        localFile = open( localAbsFilePath, "wb" )
        try:
            # Creation de la fonction callback appele a chaque block_size telecharge
            ftpCB = FtpCallback( remoteFileSize, localFile, filesrc, dialogProgressWin, curPercent, coeff*remoteFileSize, isSingleFile=isSingleFile )

            # Telecahrgement ( on passe la CB en parametre )
            # !!NOTE!!: on utilise un implemenation locale et non celle de ftplib qui ne supporte pas l'interuption d'un telechargement
            result = self.retrbinary( 'RETR ' + filesrc, ftpCB, block_size )
            print "Response Server FTP sur retrieve: %s" % repr( result )
        except:
            print "_downloadfichier: Exception - Impossible de telecharger le fichier: %s" % filesrc
            print_exc()
        # On ferme le fichier
        localFile.close()

    def retrbinary( self, cmd, callback, blocksize=8192, rest=None ):
        """
        Cette version de retrbinary permet d'interompte un telechargement en cours alors que la version de ftplib ne le permet pas
        Inspiree du code dispo a http://www.archivum.info/python-bugs-list@python.org/2007-03/msg00465.html
        """
        abort = False
        #self.ftp.voidcmd( 'TYPE I' )
        self.ftp.command( self.ftp.voidcmd, 'TYPE I' )
        #conn = self.ftp.transfercmd( cmd, rest )
        conn = self.ftp.command( self.ftp.transfercmd, cmd, rest )
        fp = conn.makefile( 'rb' )
        while 1:
            data = fp.read( blocksize )
            if not data:
                break
            try:
                callback( data )
            except cancelRequest:
                abort = True
                print "retrbinary: Download ARRETE par l'utilisateur"
                print_exc()
                break
        fp.close()
        conn.close()
        if abort:
            self.ftp.command( self.ftp.abort ) # Afin d'eviter un blockage dans le cas d'un cancel et puis d'un self.ftp.voidresp
        #return self.ftp.voidresp()
        return self.ftp.command( self.ftp.voidresp )

    def downloadImage( self, source, dest ):
        """
        Download picture from the server, save it, create the thumbnail and return path of it
        """
        print "_downloadImage %s"%source
        result = False
        try:
        
            print "source"
            print source

            #ftp = ftplib.FTP( self.host, self.user, self.password )
            #self.passionFTPCtrl.openConnection()
            localFile = open( dest, "wb" )
            try:
                #ftp.retrbinary( 'RETR ' + source, localFile.write )
                self.ftp.command( self.ftp.retrbinary, 'RETR ' + source, localFile.write )
                result = True
                #self.passionFTPCtrl.retrbinary( self, 'RETR ' + filetodlUrl, callback, blocksize=8192, rest=None )
            except:
                print "downloadImage: Exception - Impossible to download picture: %s" % source
                print_exc()
            localFile.close()
            #ftp.quit()
        except Exception, e:
            print "downloadImage: Exception - Impossible to download the picture: %s" % source
            print_exc()
        return result


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
                print "User pressed CANCEL button"
                raise cancelRequest, "User pressed CANCEL button"
        self.localfile.write( data )
        self.received += len( data )
        try:
            percent = min( ( self.received*100 )/self.filesize, 100 )
        except:
            print "FtpCallback - Exception during percent computing AND update"
            print_exc()
            percent = 100

        if self.isSingleFile:
            self.curPercent = percent
        if self.dp != None:
            self.dp.update( percent, _( 123 ) % self.curPercent, self.srcName )

