
__all__ = [ "get_browse_dialog", "Browser", "MovieSetInfo", "showInfo" ]

# Modules general
import os
import md5
import sys
import urllib
from re import findall

# Modules XBMC
import xbmc
import xbmcgui
from xbmcaddon import Addon

# Modules Custom
from utils import *
from database import Database, TBN

database = Database()

# constants
ADDON      = Addon( "script.moviesets" )
ADDON_NAME = ADDON.getAddonInfo( "name" )
ADDON_DIR  = ADDON.getAddonInfo( "path" )

__string__ = xbmc.getLocalizedString # XBMC strings
__language__ = ADDON.getLocalizedString # ADDON strings


def _unicode( text, encoding="utf-8" ):
    try: text = unicode( text, encoding )
    except: pass
    return text


def _delete_files( files ):
    for dl in files:
        try:
            if os.path.exists( dl ):
                log.warning.LOG( "%s, FileDelete(%s)", xbmc.executehttpapi( "FileDelete(%s)" % dl ).replace( "<li>", "" ), dl )
            if os.path.exists( dl ):
                os.remove( dl )
        except:
            log.debug.exc_info( sys.exc_info() )


def get_browse_dialog( default="", heading="", dlg_type=3, shares="files", mask="", use_thumbs=False, treat_as_folder=False ):
    """ shows a browse dialog and returns a value
        - 0 : ShowAndGetDirectory
        - 1 : ShowAndGetFile
        - 2 : ShowAndGetImage
        - 3 : ShowAndGetWriteableDirectory
    """
    dialog = xbmcgui.Dialog()
    value = dialog.browse( dlg_type, heading, shares, mask, use_thumbs, treat_as_folder, default )
    return value


class Browser( xbmcgui.WindowXMLDialog ):
    # constants
    CONTROL_LIST_450      = 450 # Directory list
    CONTROL_LIST_451      = 451 # List of available thumbnails
    CONTROL_HEADING       = 411 # Heading label
    CONTROL_LABEL_PATH    = 412 # label Path of the selected item
    CONTROL_BUTTON_OK     = 413 # OK button
    CONTROL_BUTTON_CANCEL = 414 # Cancel button
    CONTROL_BUTTON_CREATE = 415 # Create folder
    CONTROL_RADIOBUTTON   = 416 # Flip Image horizontally

    def __init__( self, *args, **kwargs ):
        xbmcgui.WindowXMLDialog.__init__( self, *args, **kwargs )

        self.movieset_update = False
        self.idset = kwargs[ "idset" ]
        self.heading = kwargs[ "heading" ]
        self.thumb_type = kwargs[ "type" ]

        self.delete_files = set()
        self.listitems = []
        self.select_all = False
        self.get_thumbs_fanarts()

    def get_thumbs_fanarts( self ):
        movieset = database.getThumbsOfSet( self.idset )
        indexItem = 1
        for movie in movieset:
            sorttitle = movie[ "strSortTitle" ]
            if self.thumb_type == "thumb":
                fanart_url = ""
                images = findall( '<thumb preview="(.*?)">(.*?)</thumb>', movie[ "strThumbs" ] )
                base_label = __string__( 20015 )
            elif self.thumb_type == "fanart":
                fanart_url = "".join( findall( '<fanart url="(.*?)">', movie[ "strFanarts" ] ) )
                images = findall( '<thumb.*?preview="(.*?)">(.*?)</thumb>', movie[ "strFanarts" ] )
                base_label = __string__( 20441 )
            else:
                images = []
            for preview, thumb in images:
                preview = preview or thumb
                label2 = thumb or preview
                if fanart_url:
                    preview = fanart_url + preview
                    label2 = fanart_url + label2
                label = "%s - [%s]" % ( base_label, _unicode( sorttitle ) )#, os.path.basename( preview ) )
                # set listitem
                listitem = xbmcgui.ListItem( label, label2, preview )#, "DefaultPicture.png" )
                listitem.setProperty( "indexItem", str( indexItem ) )
                indexItem +=1
                # add listitem
                self.listitems.append( listitem )

    def onInit( self ):
        try:
            # set controls label
            self.getControl( self.CONTROL_HEADING ).setLabel( self.heading )
            label = ( __language__( 32121 ), __language__( 32131 ) )[ self.thumb_type == "thumb" ]
            self.getControl( self.CONTROL_LABEL_PATH ).setLabel( label )#"Select one %s or more for extra%s"
            #self.getControl( self.CONTROL_RADIOBUTTON ).setLabel( __string__( 13206 ) )#"Overwrite"
            self.getControl( self.CONTROL_RADIOBUTTON ).setEnabled( self.thumb_type == "fanart" )
            self.getControl( self.CONTROL_BUTTON_CREATE ).setLabel( __string__( 188 ) )#"Select All"

            # get control list
            self.control_list = self.getControl( self.CONTROL_LIST_450 )
            self.control_list.reset()
            # add listitem current thumb or current fanart
            icon = TBN.get_cached_saga_thumb( self.idset, self.thumb_type == "fanart" )
            if not os.path.exists( icon ): icon = "DefaultVideoCover.png"
            else: icon = self.get_cached_thumb( icon )
            label = ( __string__( 20440 ), __string__( 20016 ) )[ self.thumb_type == "thumb" ]
            listitem = xbmcgui.ListItem( label, "current", "DefaultVideoCover.png", icon )
            self.control_list.addItem( listitem )
            # add listitems
            self.control_list.addItems( self.listitems )
            # add listitem browse
            self.control_list.addItem( xbmcgui.ListItem( __string__( 20153 ), "browse", "DefaultFolder.png" ) )

            # desable controls
            #self.getControl( self.CONTROL_LIST_451 ).setEnabled( 0 )
            try: self.getControl( self.CONTROL_LIST_451 ).setVisible( 0 )
            except: pass
        except:
            log.error.exc_info( sys.exc_info(), self )

    def onFocus( self, controlID ):
        pass

    def onClick( self, controlID ):
        try:
            if controlID == self.CONTROL_LIST_450:
                listitem = self.control_list.getSelectedItem()
                l2 = listitem.getLabel2()
                if l2 == "browse":
                    dpath = TBN.get_cached_saga_thumb( self.idset, self.thumb_type == "fanart" )
                    heading = ( __string__( 20019 ), __string__( 20437 ) )[ self.thumb_type == "fanart" ]
                    ipath = xbmc.translatePath( get_browse_dialog( heading=heading, dlg_type=2 ) )
                    if ipath and os.path.exists( ipath ):
                        listitem = self.control_list.getListItem( 0 )
                        listitem.setThumbnailImage( "DefaultVideoCover.png" )
                        filecopy = "FileCopy(%s,%s)" % ( ipath, dpath )
                        log.notice.LOG( "%s, %s", xbmc.executehttpapi( filecopy ).replace( "<li>", "" ), filecopy )
                        if os.path.exists( dpath ):
                            if self.getControl( self.CONTROL_RADIOBUTTON ).isSelected():
                                dpath = flip_fanart( dpath )
                            listitem.setThumbnailImage( self.get_cached_thumb( dpath ) )
                            self.movieset_update = True
                elif l2 == "current":
                    listitem.select( True )
                    icon = TBN.get_cached_saga_thumb( self.idset, self.thumb_type == "fanart" )
                    if not os.path.exists( icon ): icon = ""
                    ipath = icon.split( "userdata" )[ -1 ].replace( "\\", "/" ).strip( "/" )
                    if icon and xbmcgui.Dialog().yesno( __string__( 122 ), __string__( 125 ), ipath ):
                        try:
                            os.remove( icon )
                            listitem.setThumbnailImage( "DefaultVideoCover.png" )
                        except: log.error.exc_info( sys.exc_info(), self )
                    listitem.select( False )
                else:
                    listitem.select( not listitem.isSelected() )

            elif controlID == self.CONTROL_BUTTON_CREATE:
                self.select_all = not self.select_all
                for listitem in self.listitems:
                    listitem.select( self.select_all )

            elif controlID == self.CONTROL_BUTTON_CANCEL:
                self._close_dialog()

            elif controlID == self.CONTROL_BUTTON_OK:
                self._download()

        except:
            log.error.exc_info( sys.exc_info(), self )

    def _download( self ):
        DIALOG_PROGRESS = xbmcgui.DialogProgress()
        try:
            selected = [ l for l in self.listitems if l.isSelected() ]
            t_selected, t_movies = len( selected ), len( self.listitems )
            if selected and xbmcgui.Dialog().yesno( self.heading, __language__( 32122 ), __language__( 32123 ) % ( t_selected, t_movies ), __language__( 32124 ) ):
                is_cached_thumb = False
                if t_selected > 1:
                    # if multi download to user folder
                    heading = __language__( 32126 ) + ( __language__( 32127 ), __language__( 32128 ) )[ self.thumb_type == "thumb" ]
                    dpath = xbmc.translatePath( get_browse_dialog( heading=heading ) )
                    if not dpath and not os.path.exists( dpath ): return
                    overwrite = xbmcgui.Dialog().yesno( __language__( 32135 ), __language__( 32136 ) )
                else:
                    # otherwise, download to cached thumb
                    overwrite = True
                    is_cached_thumb = True
                    dpath = TBN.get_cached_saga_thumb( self.idset, self.thumb_type == "fanart" )
                    self.control_list.getListItem( 0 ).setThumbnailImage( "DefaultVideoCover.png" )
                def _pbhook( numblocks, blocksize, filesize, ratio=1.0 ):
                    try: pct = int( min( ( numblocks * blocksize * 100 ) / filesize, 100 ) * ratio )
                    except: pct = 100
                    DIALOG_PROGRESS.update( pct )
                    if DIALOG_PROGRESS.iscanceled():
                        raise IOError
                DIALOG_PROGRESS.create( self.heading )
                diff = 100.0 / t_selected
                percent = 0

                flipfanart = self.getControl( self.CONTROL_RADIOBUTTON ).isSelected()

                for count, listitem in enumerate( selected ):
                    self.control_list.selectItem( int( listitem.getProperty( "indexItem" ) ) )
                    url = listitem.getLabel2()
                    if is_cached_thumb: dest = "special://temp/" + os.path.basename( url )
                    else: dest = os.path.join( dpath, os.path.basename( url ) )
                    percent += diff
                    line1 = __language__( 32125 ) % ( count+1, t_selected, percent )
                    DIALOG_PROGRESS.update( 0, line1, url, dest )
                    if not overwrite and os.path.exists( dest ):
                        listitem.select( False )
                        continue
                    # download file
                    try: 
                        fp, h = urllib.urlretrieve( url, dest, lambda nb, bs, fs: _pbhook( nb, bs, fs ) )
                        if "denied.png" in h.get( "Content-Disposition", "" ): raise
                    except:
                        self.delete_files.add( dest )
                        log.error.LOG( dest )
                        dest = None
                        log.error.exc_info( sys.exc_info(), self )
                    listitem.select( False )
                    if DIALOG_PROGRESS.iscanceled():
                        break
                    #flip source
                    if dest and flipfanart:
                        dest = flip_fanart( dest )

                    if is_cached_thumb and dest:
                        self.delete_files.add( dest )
                        filecopy = "FileCopy(%s,%s)" % ( dest, dpath )
                        log.notice.LOG( "%s, %s", xbmc.executehttpapi( filecopy ).replace( "<li>", "" ), filecopy )
                        if os.path.exists( dpath ):
                            listitem = self.control_list.getListItem( 0 )
                            listitem.setThumbnailImage( self.get_cached_thumb( dpath ) )
                            self.movieset_update = True

                DIALOG_PROGRESS.update( 100 )
        except:
            log.error.exc_info( sys.exc_info(), self )
        _delete_files( self.delete_files )
        try: DIALOG_PROGRESS.close()
        except: pass

    def get_cached_thumb( self, fpath ):
        # fixe me: xbmc not change/reload/refresh image if path is same
        fpath = xbmc.translatePath( fpath )
        filename = md5.new( open( fpath ).read( 250 ) ).hexdigest()
        temp = "special://temp/moviesets/%s.tbn" % filename
        if not os.path.exists( temp ): xbmc.executehttpapi( "FileCopy(%s,%s)" % ( fpath, temp ) ).replace( "<li>", "" )
        return ( fpath, temp )[ os.path.exists( temp ) ]

    def onAction( self, action ):
        if action in [ 9, 10, 117 ]:
            self._close_dialog()

    def _close_dialog( self ):
        _delete_files( self.delete_files )
        self.close()


class MovieSetInfo( xbmcgui.WindowXMLDialog ):
    def __init__( self, *args, **kwargs ):
        xbmcgui.WindowXMLDialog.__init__( self, *args, **kwargs )

        self.reload = False
        self.setfocus = kwargs.get( "setfocus" )
        self.idset = kwargs[ "idset" ]
        self.movieset_update = False

    def onInit( self ):
        try:
            self.listitem = database.getContainerMovieSets( self.idset )[ 0 ]
            if not self.listitem:
                self._close_dialog()
            else:
                self.listitem = self.listitem[ 0 ]
                self.addItem( self.listitem )
                self.getControl( 50 ).setVisible( 0 )

                self.getControl( 6 ).setLabel( "Manager" )
                self.getControl( 12 ).setLabel( __string__( 20413 ) )

                #desable trailer button 15 xbmc bug !!! if user click
                try: self.getControl( 15 ).setEnabled( 0 )
                except: pass

                try:
                    self.getControl( 150 ).setVisible( 0 )
                    listitems = []
                    for cast, role, movie in database.getCastAndRoleOfSet( self.idset ):
                        label = " ".join( [ _unicode( cast ), __string__( 20347 ), _unicode( role ), __string__( 1405 ), _unicode( movie ) ] )
                        icon = TBN.get_cached_actor_thumb( cast )
                        listitems.append( xbmcgui.ListItem( label, "", icon, icon ) )
                    self.getControl( 150 ).addItems( listitems )
                except:
                    log.error.exc_info( sys.exc_info(), self )
                    self.getControl( 5 ).setEnabled( 0 )

                if self.setfocus:
                    self.setFocusId( self.setfocus )
        except:
            log.error.exc_info( sys.exc_info(), self )
            self._close_dialog()

    def onFocus( self, controlID ):
        pass

    def onClick( self, controlID ):
        try:
            if controlID == 5:
                if self.getControl( 5 ).getLabel() == __string__( 207 ):
                    self.getControl( 5 ).setLabel( __string__( 206 ) )
                    self.getControl( 150 ).setVisible( 0 )
                else:
                    self.getControl( 5 ).setLabel( __string__( 207 ) )
                    self.getControl( 150 ).setVisible( 1 )

            elif controlID == 6:
                self._close_dialog()
                xbmc.executebuiltin( "RunScript(script.moviesets,manager)" )

            elif controlID == 8:
                self._close_dialog()
                xbmc.executebuiltin( "Container.Update(videodb://1/7/%s/,replace)" % self.idset )

            elif controlID == 11:
                # create our playlist
                playlist = xbmc.PlayList( xbmc.PLAYLIST_VIDEO )
                # clear any possible entries
                playlist.clear()
                # set title
                #title = "%s (%s)" % ( xbmc.getInfoLabel( "ListItem.Label" ), __string__( 20410 ) )
                #self.listitem.setInfo( "video", { "title": title } )
                # enum trailers
                #for trailer in xbmc.getInfoLabel( "ListItem.Trailer" ).replace( "stack://", "" ).split( " , " ):
                #    # add item to our playlist
                #    playlist.add( trailer, self.listitem )
                # get trailers
                for i in range( 1, 11 ):
                    title = _unicode( xbmc.getInfoLabel( "ListItem.Property(movie.%i.Title)" % i ) )
                    if not title: break
                    trailer = xbmc.getInfoLabel( "ListItem.Property(movie.%i.Trailer)" % i )
                    if not trailer: continue
                    title = "%s (%s)" % ( title, __string__( 20410 ) )
                    # update title
                    self.listitem.setInfo( "video", { "title": title } )
                    # add item to our playlist
                    playlist.add( trailer, self.listitem )
                # if movie in playlist play item
                if playlist.size():
                    self._close_dialog()
                    # play item
                    xbmc.Player( xbmc.PLAYER_CORE_AUTO ).play( playlist )

            elif controlID in [ 10, 12 ]:
                self.reload = True
                self.setfocus = controlID
                self._close_dialog() # win32 if not close XBMC freezzze !!! :(
                # Set movieset fanart or Set movieset thumb
                self.browse( ( "fanart", "thumb" )[ controlID == 10 ] )
        except:
            log.error.exc_info( sys.exc_info(), self )

    def browse( self, type ):
        w = Browser( "FileBrowser.xml", ADDON_DIR, heading=xbmc.getInfoLabel( "ListItem.Label" ), idset=self.idset, type=type )
        w.doModal()
        _delete_files( w.delete_files )
        self.movieset_update = w.movieset_update
        del w

    def onAction( self, action ):
        if action in [ 9, 10, 117 ]:
            self._close_dialog()

    def _close_dialog( self ):
        self.close()


def showInfo( idset ):
    movieset_update = False
    try:
        xbmc.executebuiltin( "Skin.Reset(MovieSets.Sleep)" )
        xbmc.executebuiltin( "Skin.SetBool(MovieSets.Sleep)" )
        xbmc.executebuiltin( "Dialog.Close(busydialog)" )
        loop = True
        setfocus = None
        while loop:
            w = MovieSetInfo( "DialogVideoInfo.xml", ADDON_DIR, idset=idset, setfocus=setfocus )
            w.doModal()
            movieset_update = movieset_update or w.movieset_update
            setfocus = w.setfocus
            loop = w.reload
        del w
    except:
        log.error.exc_info( sys.exc_info() )
    xbmc.executebuiltin( "Skin.Reset(MovieSets.Sleep)" )
    xbmc.executebuiltin( "Dialog.Close(busydialog)" )
    return movieset_update
