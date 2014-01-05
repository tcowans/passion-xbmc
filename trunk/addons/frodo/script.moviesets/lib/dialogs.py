
# Modules general
import os
import re
import sys
import time
import urllib

if sys.version >= "2.5":
    from hashlib import md5 as _hash
else:
    from md5 import new as _hash

# Modules XBMC
import xbmc
import xbmcgui
from xbmcaddon import Addon

# Modules Custom
from utils.mgr_utils import *
from database import getContainerMovieSets, Database, TBN, quote_plus
DATABASE = Database()

# constants
ADDON      = Addon( "script.moviesets" )
ADDON_DIR  = ADDON.getAddonInfo( "path" )
ADDON_DATA = ADDON.getAddonInfo( "profile" )

Language = ADDON.getLocalizedString # ADDON strings
LangXBMC = xbmc.getLocalizedString # XBMC strings

MOVIESET_CACHED_THUMB = xbmc.translatePath( "%sThumbnails/%s.tbn" % ( ADDON_DATA, "%s" ) )
TEMP_DIR = xbmc.translatePath( "%stemp/" % ADDON.getAddonInfo( "profile" ) )
if not path_exists( TEMP_DIR ): os.makedirs( TEMP_DIR )

DIALOG_PROGRESS = xbmcgui.DialogProgress()

#https://raw.github.com/xbmc/xbmc/master/xbmc/guilib/Key.h
ACTION_PARENT_DIR    =   9
ACTION_PREVIOUS_MENU =  10
ACTION_NAV_BACK      =  92
ACTION_CONTEXT_MENU  = 117
CLOSE_DIALOG         = [ ACTION_PARENT_DIR, ACTION_PREVIOUS_MENU, ACTION_NAV_BACK, ACTION_CONTEXT_MENU ]


def _unicode( text, encoding="utf-8" ):
    try: text = unicode( text, encoding )
    except: pass
    return text


def _delete_files( files ):
    for dl in files:
        try:
            if path_exists( dl ):
                xbmcvfs.delete( dl )
            if path_exists( dl ):
                os.remove( dl )
        except:
            LOGGER.error.print_exc()
        if not path_exists( dl ):
            LOGGER.warning.LOG( "OK, FileDelete(%s)", dl )
        else:
            LOGGER.error.LOG( "ERROR, FileDelete(%s)", dl )


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
        self.idset           = kwargs[ "idset" ]
        self.heading         = kwargs[ "heading" ]
        self.thumb_type      = kwargs[ "type" ]
        self.listitems       = []
        self.delete_files    = set()
        self.select_all      = False
        self.movieset_update = False

        self.art = {}
        self.get_thumbs_fanarts()

    def get_thumbs_fanarts( self ):
        movieset, self.art = DATABASE.getThumbsOfSet( self.idset )
        indexItem = 1
        for movie in movieset:
            sorttitle = movie[ "strSortTitle" ] or movie[ "strTitle" ]
            if self.thumb_type == "thumb":
                fanart_url = ""
                images = re.findall( '<thumb preview="(.*?)">(.*?)</thumb>', movie[ "strThumbs" ] )
                base_label = LangXBMC( 20015 )
            elif self.thumb_type == "fanart":
                fanart_url = "".join( re.findall( '<fanart url="(.*?)">', movie[ "strFanarts" ] ) )
                images = re.findall( '<thumb.*?preview="(.*?)">(.*?)</thumb>', movie[ "strFanarts" ] )
                base_label = LangXBMC( 20441 )
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
                if self.art: preview = "image://" + quote_plus( preview )
                listitem = xbmcgui.ListItem( label, label2, preview )#, "DefaultPicture.png" )
                listitem.setProperty( "indexItem", str( indexItem ) )
                indexItem +=1
                # add listitem
                self.listitems.append( listitem )

    def onInit( self ):
        try:
            # set controls label
            self.getControl( self.CONTROL_HEADING ).setLabel( self.heading )
            label = ( Language( 32121 ), Language( 32131 ) )[ self.thumb_type == "thumb" ]
            self.getControl( self.CONTROL_LABEL_PATH ).setLabel( label )#"Select one %s or more for extra%s"
            #self.getControl( self.CONTROL_RADIOBUTTON ).setLabel( LangXBMC( 13206 ) )#"Overwrite"
            #print ( self.thumb_type == "fanart" ) and not self.art
            if self.art: self.getControl( self.CONTROL_RADIOBUTTON ).setVisible( 0 ) # hmmm! setEnabled not work on frodo!
            else: self.getControl( self.CONTROL_RADIOBUTTON ).setEnabled( self.thumb_type == "fanart" )
            
            self.getControl( self.CONTROL_BUTTON_CREATE ).setLabel( LangXBMC( 188 ) )#"Select All"

            # get control list
            self.control_list = self.getControl( self.CONTROL_LIST_450 )
            self.control_list.reset()
            
            # add listitem current thumb or current fanart
            if not self.art:
                icon = TBN.get_cached_saga_thumb( self.idset, self.thumb_type == "fanart" )
                if not path_exists( icon ): icon = "DefaultVideoCover.png"
                else: icon = self.get_cached_thumb( icon )
            else:
                icon = self.art[ self.thumb_type ]

            label = ( LangXBMC( 20440 ), LangXBMC( 20016 ) )[ self.thumb_type == "thumb" ]
            listitem = xbmcgui.ListItem( label, "current", "DefaultVideoCover.png", icon )
            self.control_list.addItem( listitem )

            # add listitems
            self.control_list.addItems( self.listitems )
            # add listitem browse
            self.control_list.addItem( xbmcgui.ListItem( LangXBMC( 20153 ), "browse", "DefaultFolder.png" ) )
            self.setFocus( self.control_list )

            # desable controls
            try: self.getControl( self.CONTROL_LIST_451 ).setEnabled( 0 )
            except: pass
            try: self.getControl( self.CONTROL_LIST_451 ).setVisible( 0 )
            except: pass
        except:
            LOGGER.error.print_exc()

    def onFocus( self, controlID ):
        pass

    def onClick( self, controlID ):
        try:
            if controlID == self.CONTROL_LIST_450:
                listitem = self.control_list.getSelectedItem()
                l2 = listitem.getLabel2()
                if l2 == "browse":
                    heading = ( LangXBMC( 20019 ), LangXBMC( 20437 ) )[ self.thumb_type == "fanart" ]
                    ipath = xbmc.translatePath( get_browse_dialog( heading=heading, dlg_type=2 ) )

                    if ipath and path_exists( ipath ):
                        listitem = self.control_list.getListItem( 0 )
                        listitem.setThumbnailImage( "DefaultVideoCover.png" )
                        if not self.art:
                            # Eden
                            dpath = TBN.get_cached_saga_thumb( self.idset, self.thumb_type == "fanart" )
                            OK = xbmcvfs.copy( ipath, dpath )
                            LOGGER.notice.LOG( "%s, FileCopy(%s,%s)", repr( OK ), ipath, dpath )
                            if path_exists( dpath ):
                                if self.getControl( self.CONTROL_RADIOBUTTON ).isSelected():
                                    dpath = flip_fanart( dpath, ADDON.getSetting( "flipquality" ) )
                                listitem.setThumbnailImage( self.get_cached_thumb( dpath ) )
                                self.movieset_update = True
                        else:
                            # Frodo
                            DATABASE.setArtForItem( self.idset, "set", self.thumb_type, ipath )
                            listitem.setThumbnailImage( "image://" + quote_plus( ipath ) )
                            self.movieset_update = True

                elif l2 == "current":
                    listitem.select( True )
                    if not self.art:
                        # Eden
                        icon = TBN.get_cached_saga_thumb( self.idset, self.thumb_type == "fanart" )
                        if not path_exists( icon ): icon = ""
                        ipath = icon.split( "userdata" )[ -1 ].replace( "\\", "/" ).strip( "/" )
                        if icon and xbmcgui.Dialog().yesno( LangXBMC( 122 ), LangXBMC( 125 ), ipath ):
                            try:
                                os.remove( icon )
                                listitem.setThumbnailImage( "DefaultVideoCover.png" )
                            except: LOGGER.error.print_exc()
                    else:
                        # Frodo
                        if xbmcgui.Dialog().yesno( LangXBMC( 122 ), LangXBMC( 125 ) ):
                            listitem.setThumbnailImage( "DefaultVideoCover.png" )
                            DATABASE.setArtForItem( self.idset, "set", self.thumb_type, "" )
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
            LOGGER.error.print_exc()

    def _download( self ):
        try:
            selected = [ l for l in self.listitems if l.isSelected() ]
            t_selected, t_movies = len( selected ), len( self.listitems )
            if selected and xbmcgui.Dialog().yesno( self.heading, Language( 32122 ), Language( 32123 ) % ( t_selected, t_movies ), Language( 32124 ) ):
                is_cached_thumb = False
                if t_selected > 1:
                    # if multi download to user folder
                    heading = Language( 32126 ) + ( Language( 32127 ), Language( 32128 ) )[ self.thumb_type == "thumb" ]
                    dpath = xbmc.translatePath( get_browse_dialog( heading=heading ) )
                    if not dpath and not path_exists( dpath ): return
                    overwrite = xbmcgui.Dialog().yesno( Language( 32135 ), Language( 32136 ) )
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
                    if is_cached_thumb: dest = TEMP_DIR + os.path.basename( url )
                    else: dest = _unicode( os.path.join( dpath, os.path.basename( url ) ) )
                    percent += diff
                    if not overwrite:
                        if self.art.get( self.thumb_type ) or path_exists( dest ):
                            listitem.select( False )
                            continue
                    # Frodo
                    if self.art and count == 0:
                        DATABASE.setArtForItem( self.idset, "set", self.thumb_type, url )
                        listitem.select( False )
                        if t_selected == 1: break

                    line1 = Language( 32125 ) % ( count+1, t_selected, percent )
                    DIALOG_PROGRESS.update( 0, line1, url, dest )
                    # Eden or for extra: download file
                    try:
                        fp, h = urllib.urlretrieve( url, dest, lambda nb, bs, fs: _pbhook( nb, bs, fs ) )
                        if "denied.png" in h.get( "Content-Disposition", "" ): raise
                    except:
                        self.delete_files.add( dest )
                        LOGGER.error.LOG( dest )
                        dest = None
                        LOGGER.error.print_exc()
                    listitem.select( False )
                    if DIALOG_PROGRESS.iscanceled():
                        break
                    #flip source
                    if dest and flipfanart:
                        dest = flip_fanart( dest, ADDON.getSetting( "flipquality" ) )

                    if is_cached_thumb and dest:
                        self.delete_files.add( dest )
                        OK = xbmcvfs.copy( dest, dpath )
                        LOGGER.notice.LOG( "%s, FileCopy(%s,%s)", repr( OK ), dest, dpath )
                        #filecopy = "FileCopy(%s,%s)" % ( dest, dpath )
                        #LOGGER.notice.LOG( "%s, %s", xbmc.executehttpapi( filecopy ).replace( "<li>", "" ), filecopy )
                        if path_exists( dpath ):
                            listitem = self.control_list.getListItem( 0 )
                            listitem.setThumbnailImage( self.get_cached_thumb( dpath ) )
                            self.movieset_update = True

                #DIALOG_PROGRESS.update( 100 )
            _delete_files( self.delete_files )
        except:
            LOGGER.error.print_exc()

        if xbmc.getCondVisibility( "Window.IsVisible(progressdialog)" ):
            xbmc.executebuiltin( "Dialog.Close(progressdialog)" )
        #try: DIALOG_PROGRESS.close()
        #except: pass

    def get_cached_thumb( self, fpath ):
        try:
            # fixe me: xbmc not change/reload/refresh image if path is same
            rpath = translatePath( fpath )
            filename = _hash( repr( rpath ) + open( rpath ).read( 250 ) ).hexdigest()
            temp = MOVIESET_CACHED_THUMB % filename
            if not path_exists( temp ):
                #xbmc.executehttpapi( "FileCopy(%s,%s)" % ( fpath, temp ) ).replace( "<li>", "" )
                xbmcvfs.copy( fpath, temp )
            return ( fpath, temp )[ path_exists( temp ) ]
        except:
            return fpath

    def onAction( self, action ):
        if action in CLOSE_DIALOG:
            self._close_dialog()

    def _close_dialog( self ):
        _delete_files( self.delete_files )
        self.close()


class MovieSetInfo( xbmcgui.WindowXMLDialog ):
    def __init__( self, *args, **kwargs ):
        self.setfocus = kwargs.get( "setfocus" )
        self.idset = kwargs[ "idset" ]
        self.movieset_update = False

        try:
            #actors_lib = os.path.join( Addon( "script.metadata.actors" ).getAddonInfo( "path" ), "resources", "lib" )
            actors_lib = xbmc.translatePath( "special://home/addons/script.metadata.actors/resources/lib" )
            sys.path.append( actors_lib )
            import common
            self.actorsdb = common.actorsdb
            self.setActorProperties = common.setActorProperties
            self.clean_bio = common.metautils.clean_bio
        except:
            self.actorsdb = None
            def _setActorProperties( listitem, actor ): return listitem
            self.setActorProperties = _setActorProperties
            def _clean_bio( bio ): return bio
            self.clean_bio = _clean_bio
            LOGGER.error.print_exc()
        #print dir( self.actorsdb )

    def onInit( self ):
        try:
            self.listitem = getContainerMovieSets( self.idset )[ 0 ]
            if not self.listitem:
                self._close_dialog()
            else:
                self.listitem = self.listitem[ 0 ]
                self.addItem( self.listitem )
                self.getControl( 50 ).setVisible( 0 )

                self.getControl( 6 ).setLabel( "Manager" )
                self.getControl( 12 ).setLabel( LangXBMC( 20413 ) )

                #desable trailer button 15 xbmc bug !!! if user click
                try: self.getControl( 15 ).setEnabled( 0 )
                except: pass

                con = cur = None
                if self.actorsdb:
                    con, cur = self.actorsdb.getConnection()
                try:
                    self.getControl( 150 ).setVisible( 0 )
                    listitems = []
                    for idActor, cast, role, movie in DATABASE.getCastAndRoleOfSet( self.idset ):
                        try:
                            # cast est role dans movie
                            label = " ".join( [ _unicode( cast ), LangXBMC( 20347 ), _unicode( role ), LangXBMC( 1405 ), _unicode( movie ) ] )
                            art = DATABASE.getArtForItem( idActor, "actor" )
                            icon = ""
                            if art:
                                icon = art.get( "thumb" )
                                if icon: icon = "image://" + quote_plus( icon )
                            icon = icon or TBN.get_cached_actor_thumb( cast )

                            listitem = xbmcgui.ListItem( label, "", icon, icon )
                            if cur:
                                actor = self.actorsdb.getActor( cur, strActor=cast )
                                bio   = self.clean_bio( actor.get( "biography" ) or "" )
                                listitem.setInfo( "video", { "title": cast, "plot": bio } )
                                if actor:
                                    actor[ "biography" ] = bio
                                    listitem = self.setActorProperties( listitem, actor )
                                    #print actor
                            listitems.append( listitem )
                        except:
                            LOGGER.error.print_exc()
                    self.getControl( 150 ).addItems( listitems )
                except:
                    LOGGER.error.print_exc()
                    self.getControl( 5 ).setEnabled( 0 )
                if hasattr( con, "close" ):
                    con.close()

                if self.setfocus:
                    self.setFocusId( self.setfocus )
        except:
            LOGGER.error.print_exc()
            self._close_dialog()

    def onFocus( self, controlID ):
        pass

    def onClick( self, controlID ):
        try:
            if controlID == 5:
                if self.getControl( 5 ).getLabel() == LangXBMC( 207 ):
                    self.getControl( 5 ).setLabel( LangXBMC( 206 ) )
                    self.getControl( 150 ).setVisible( 0 )
                else:
                    self.getControl( 5 ).setLabel( LangXBMC( 207 ) )
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
                #title = "%s (%s)" % ( xbmc.getInfoLabel( "ListItem.Label" ), LangXBMC( 20410 ) )
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
                    title = "%s (%s)" % ( title, LangXBMC( 20410 ) )
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
                self.setfocus = controlID
                # **attrs: Set movieset fanart or Set movieset thumb
                self.browser_attrs = {
                    "idset": self.idset,
                    "heading": xbmc.getInfoLabel( "ListItem.Label" ),
                    "type": ( "fanart", "thumb" )[ self.setfocus == 10 ]
                    }
                self._close_dialog()

            elif controlID == 150:
                actor_name = xbmc.getInfoLabel( "Container(150).ListItem.Title" )
                if actor_name:
                    xbmc.executebuiltin( "RunScript(script.metadata.actors,%s)" % actor_name )
        except:
            LOGGER.error.print_exc()

    def onAction( self, action ):
        if action in CLOSE_DIALOG:
            self._close_dialog()
        #else:
        #    print action.getId()

    def _close_dialog( self ):
        self.close()


def browser( **kwargs ):
    xbmcgui.Dialog().ok( "Manager Broken", "The manager is broken, due to API change!", "Sorry!" )
    return
    #xbmc.executebuiltin( "SetFocus(50)" )
    #xbmc.executebuiltin( "Action(contextmenu)" )
    #xbmc.executebuiltin( "sendclick(10106,1008)" )#1007
    #time.sleep( 1 )
    #return
    notaction = kwargs.get( "notaction" )
    if not notaction:
        # prevent if user change image, because main container not refresh if img is same path
        xbmc.executebuiltin( "Action(Select)" )
        time.sleep( .1 )
        if not xbmc.getInfoLabel( "ListItem.Label" ).strip( "." ):
            xbmc.executebuiltin( "Action(Down)" )
            #xbmc.executebuiltin( "Control.Move(50,1)" )

    wb = Browser( "script-MovieSets-Browser.xml", ADDON_DIR, **kwargs )
    wb.doModal()
    _delete_files( wb.delete_files )
    movieset_update = wb.movieset_update
    del wb

    if not notaction:
        xbmc.executebuiltin( "Action(ParentDir)" )
    return movieset_update


def showInfo( idset, update=False, setfocus=None ):
    xbmc.executebuiltin( "Skin.Reset(MovieSets.Sleep)" )
    xbmc.executebuiltin( "Skin.SetBool(MovieSets.Sleep)" )
    w = None
    try:
        w = MovieSetInfo( "script-MovieSets-DialogInfo.xml", ADDON_DIR, idset=idset, setfocus=setfocus )
        w.doModal()
        setfocus = w.setfocus
        browser_attrs = None
        if hasattr( w, "browser_attrs" ):
            browser_attrs = w.browser_attrs
        del w
        w = None

        if browser_attrs is not None:
            up = browser( **browser_attrs )
            update = update or up
            showInfo( idset, update, setfocus )
    except:
        LOGGER.error.print_exc()
    del w

    xbmc.executebuiltin( "Skin.Reset(MovieSets.Sleep)" )
    return update



if ( __name__ == "__main__" ):
    try:
        idset = None
        strListItem = "Container(%s).ListItem" % ADDON.getSetting( "containerId" )
        if IsTrue( xbmc.getInfoLabel( "%s.Property(IsSet)" % strListItem ) ):
            idset = xbmc.getInfoLabel( "%s.Label2" % strListItem )

        elif xbmc.getInfoLabel( "ListItem.Path" ).startswith( "videodb://1/7" ):
            #test path videodb://1/7/1/
            from re import search
            i = search( "videodb://1/7/(.*?)/", xbmc.getInfoLabel( "ListItem.Path" ) )
            if i: idset = i.group( 1 )

        if idset is not None:
            if showInfo( idset ):
                try: xbmcgui.Window( 10025 ).setProperty( "MovieSets.Update", "true" )
                except: xbmc.executebuiltin( "SetProperty(MovieSets.Update,true)" )
    except:
        LOGGER.error.print_exc()
