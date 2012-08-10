
# Modules general
import os
import re
import sys
import time
import urllib

# Modules XBMC
import xbmc
import xbmcgui
import xbmcvfs
from xbmcaddon import Addon

try:
    import json
    # test json
    json.loads( "[null]" )
except:
    import simplejson as json

# Modules Custom
import xbmcart
from log import logAPI
LOGGER = logAPI()


# constants
ADDON      = Addon( "plugin.moviesets" )
ADDON_DIR  = ADDON.getAddonInfo( "path" )

Language = ADDON.getLocalizedString # ADDON strings
LangXBMC = xbmc.getLocalizedString # XBMC strings

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


def path_exists( filename ):
    # first use os.path.exists and if not exists, test for share with xbmcvfs.
    return os.path.exists( filename ) or xbmcvfs.exists( filename )


class _urlopener( urllib.FancyURLopener ):
    version = "Mozilla/5.0 (Windows NT 5.1; rv:14.0) Gecko/20100101 Firefox/14.0.1"
urllib._urlopener = _urlopener()

def getMoreOnGooglePlus( uri ):
    """ fetch the json source """
    o_json = []
    try:
        # set cached filename
        c_filename = xbmc.translatePath( ADDON.getAddonInfo( 'profile' ) + uri + '.json' )
        if path_exists( c_filename ):
            expired = time.time() >= ( os.path.getmtime( c_filename ) + ( 24 * 60**2 ) )
            if not expired:
                f = xbmcvfs.File( c_filename )
                b = f.read().strip( "\x00" )
                f.close()
                #print repr( b )
                #o_json = eval( b )
                o_json = json.loads( b )

        if not o_json:
            url = "https://plus.google.com/u/0/photos/106515162496698823082/albums/" + uri
            sock = urllib.urlopen( url )
            html = sock.read()
            sock.close()
            s = re.compile( '<script>AF_initDataCallback[(]({key: \'27\'.*?)[)];</script>', re.S ).findall( html )
            s = "".join( s ).replace( "false", "'false'" )
            while s.count( ",," ): s = s.replace( ",,", "," )

            key = data = isError = None
            o_json = eval( s )[ data ][ 2 ][ 1: ]

            if o_json:
                b = json.dumps( o_json )
                f = xbmcvfs.File( c_filename, 'w' )
                f.write( b )#repr( o_json ) )
                f.close()
    except:
        try: xbmcvfs.delete( c_filename )
        except: pass
        LOGGER.error.print_exc()
    return o_json


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
        self.select_all      = False
        self.movieset_update = False

        self.art = {}
        self.get_thumbs_fanarts()

    def get_thumbs_fanarts( self ):
        from videolibrary import getArtsOfSet
        arts, self.art = getArtsOfSet( self.idset, self.thumb_type )

        re_fanart_url = re.compile( '<fanart url="(.*?)">' ).findall
        re_thumb = re.compile( '<thumb.*?preview="(.*?)">(.*?)</thumb>' ).findall
        self.indexItem = 1
        base_label = LangXBMC( ( 20015, 20441 )[ self.thumb_type == "fanart" ] ) + " - "
        for title, year, art in arts:
            fanart_url = ""
            if self.thumb_type == "fanart":
                fanart_url = "".join( re_fanart_url( art ) )
            #
            title += "  (%i)" % int( year )
            for preview, thumb in re_thumb( art ):
                url = thumb
                if fanart_url:
                    url = fanart_url + thumb
                
                #print ( title, thumb )
                label = base_label + title
                # set listitem
                #if self.art: thumb = "image://" + urllib.quote_plus( thumb )
                listitem = xbmcgui.ListItem( label, "", "DefaultVideoCover.png", thumb )
                listitem.setProperty( "indexItem", str( self.indexItem ) )
                listitem.setProperty( "url", url )
                self.indexItem +=1
                # add listitem
                self.listitems.append( listitem )

    def onInit( self ):
        try:
            # desable controls
            try: self.getControl( self.CONTROL_LIST_451 ).setEnabled( 0 )
            except: pass
            try: self.getControl( self.CONTROL_LIST_451 ).setVisible( 0 )
            except: pass

            # set controls label
            self.getControl( self.CONTROL_HEADING ).setLabel( self.heading )
            label = ( Language( 32121 ), Language( 32131 ) )[ self.thumb_type == "thumb" ]
            self.getControl( self.CONTROL_LABEL_PATH ).setLabel( label ) #"Select one %s or more for extra%s"

            #self.getControl( self.CONTROL_RADIOBUTTON ).setVisible( 0 )
            self.getControl( self.CONTROL_RADIOBUTTON ).setEnabled( 0 ) #self.thumb_type == "fanart" )
            
            self.getControl( self.CONTROL_BUTTON_CREATE ).setLabel( LangXBMC( 188 ) ) #"Select All"

            # get control list
            self.control_list = self.getControl( self.CONTROL_LIST_450 )
            self.control_list.reset()
            
            # add listitem current thumb or current fanart
            label = ( LangXBMC( 20440 ), LangXBMC( 20016 ) )[ self.thumb_type == "thumb" ]
            listitem = xbmcgui.ListItem( label, "", "DefaultVideoCover.png" )
            listitem.setProperty( "url", "current" )
            if self.art.get( self.thumb_type ):
                listitem.setThumbnailImage( self.art[ self.thumb_type ] )
            self.control_list.addItem( listitem )

            # add listitems
            self.control_list.addItems( self.listitems )

            # add listitem browse
            listitem = xbmcgui.ListItem( LangXBMC( 20153 ), "", "DefaultFolder.png" )
            listitem.setProperty( "url", "browse" )
            self.control_list.addItem( listitem )
            
            # add listitem more
            if self.thumb_type == "thumb":
                listitem = xbmcgui.ListItem( LangXBMC( 22082 ), "", ADDON.getAddonInfo( "icon" ) )
                listitem.setProperty( "url", "more" )
                self.control_list.addItem( listitem )
 
            self.setFocus( self.control_list )
        except:
            LOGGER.error.print_exc()

    def onFocus( self, controlID ):
        pass

    def onClick( self, controlID ):
        try:
            if controlID == self.CONTROL_LIST_450:
                listitem = self.control_list.getSelectedItem()
                l2 = listitem.getProperty( "url" )
                if l2 == "browse":
                    heading = ( LangXBMC( 20019 ), LangXBMC( 20437 ) )[ self.thumb_type == "fanart" ]
                    ipath = xbmc.translatePath( get_browse_dialog( heading=heading, dlg_type=2 ) )

                    if ipath and path_exists( ipath ):
                        listitem = self.control_list.getListItem( 0 )
                        listitem.setThumbnailImage( "DefaultVideoCover.png" )
                        # Frodo
                        ok = xbmcart.setArt( self.idset, "set", self.thumb_type, ipath )
                        listitem.setThumbnailImage( "image://" + urllib.quote_plus( ipath ) )
                        self.movieset_update = ok

                elif l2 == "current":
                    listitem.select( True )
                    # Frodo
                    if xbmcgui.Dialog().yesno( LangXBMC( 122 ), LangXBMC( 125 ) ):
                        listitem.setThumbnailImage( "DefaultVideoCover.png" )
                        ok = xbmcart.setArt( self.idset, "set", self.thumb_type, "" )
                        self.movieset_update = ok
                    listitem.select( False )

                elif l2 == "more":
                    uris = [
                        "5666565996413149985",
                        "5666567085447739761",
                        "5666592955527206641",
                        "5666593860416415425",
                        "5666611392669713825",
                        "5680591064557830705",
                        ]
                    choice = [
                        "Movie Boxset 3D (0 - M)",
                        "Movie Boxset 3D (N - Z)",
                        "Movie Boxset Clearcase (0 - M)",
                        "Movie Boxset Clearcase (N - Z)",
                        "Movie Boxset Diamond (0 - M)",
                        "Movie Boxset Diamond (N - Z)",
                        ]
                    selected = xbmcgui.Dialog().select( "Movie Sets Arts", choice )
                    if selected == -1: return

                    xbmc.executebuiltin( 'ActivateWindow(busydialog)' )
                    o_json = getMoreOnGooglePlus( uris[ selected ] )
                    xbmc.executebuiltin( 'Dialog.Close(busydialog,true)' )

                    lis = []
                    selectItem = 0
                    for i, s in enumerate( o_json ):
                        iconimage = s[ 2 ][ 0 ]
                        name = urllib.unquote_plus( urllib.unquote_plus( os.path.basename( iconimage )[ :-4 ] ) )
                        li = xbmcgui.ListItem( name, "", "DefaultPicture.png", iconimage )
                        li.setProperty( "url", iconimage )
                        lis.append( li )
                        l1, l2 = li.getLabel().lower(), self.heading.lower()
                        if l2 == l1 or l2 in l1 or l1 in l2: selectItem = i

                    # toggle list control
                    self.control_list.setEnabled( 0 )
                    self.control_list.setVisible( 0 )
                    self.getControl( self.CONTROL_LIST_451 ).reset()
                    self.getControl( self.CONTROL_LIST_451 ).addItems( lis )
                    self.getControl( self.CONTROL_LIST_451 ).setEnabled( 1 )
                    self.getControl( self.CONTROL_LIST_451 ).setVisible( 1 )
                    self.getControl( self.CONTROL_LIST_451 ).selectItem( selectItem )
                    self.setFocus( self.getControl( self.CONTROL_LIST_451 ) )
                    self.getControl( self.CONTROL_BUTTON_CREATE ).setEnabled( 0 )
                    self.getControl( self.CONTROL_BUTTON_OK ).setEnabled( 0 )

                else:
                    listitem.select( not listitem.isSelected() )

            if controlID == self.CONTROL_LIST_451:
                listitem = self.getControl( self.CONTROL_LIST_451 ).getSelectedItem()
                listitem.setProperty( "indexItem", str( self.indexItem ) )
                label = " - ".join( [ LangXBMC( 22082 ).strip( "." ).strip(), listitem.getLabel() ] )
                listitem.setLabel( label )
                self.listitems.append( listitem )
                self.control_list.addItem( listitem )
                self.control_list.selectItem( self.indexItem+2 )
                self.indexItem +=1

                # toggle list control
                self.getControl( self.CONTROL_LIST_451 ).reset()
                self.getControl( self.CONTROL_LIST_451 ).setEnabled( 0 )
                self.getControl( self.CONTROL_LIST_451 ).setVisible( 0 )
                self.control_list.setEnabled( 1 )
                self.control_list.setVisible( 1 )
                self.setFocus( self.control_list )
                self.getControl( self.CONTROL_BUTTON_CREATE ).setEnabled( 1 )
                self.getControl( self.CONTROL_BUTTON_OK ).setEnabled( 1 )

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
        if xbmc.getCondVisibility( "Window.IsVisible(busydialog)" ):
            xbmc.executebuiltin( 'Dialog.Close(busydialog,true)' )

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
                    dpath = ""
                    self.control_list.getListItem( 0 ).setThumbnailImage( "DefaultVideoCover.png" )

                DIALOG_PROGRESS.create( self.heading )
                diff = 100.0 / t_selected
                percent = 0

                for count, listitem in enumerate( selected ):
                    self.control_list.selectItem( int( listitem.getProperty( "indexItem" ) ) )
                    url = listitem.getProperty( "url" )
                    dest = ""
                    if not is_cached_thumb:
                        dest = _unicode( os.path.join( dpath, os.path.basename( url ) ) )
                    percent += diff
                    if not overwrite:
                        if self.art.get( self.thumb_type ) or ( dest and path_exists( dest ) ):
                            listitem.select( False )
                            continue

                    line1 = Language( 32125 ) % ( count+1, t_selected, percent )
                    DIALOG_PROGRESS.update( int( percent ), line1, url, dest )

                    if is_cached_thumb:
                        print ( "image://" + urllib.quote_plus( url ) )
                        ok = xbmcart.setArt( self.idset, "set", self.thumb_type, url )
                        if ok:
                            c_art = xbmcart.copyArtToCache( url )
                            self.control_list.getListItem( 0 ).setThumbnailImage( "image://" + urllib.quote_plus( url ) )
                            self.movieset_update = True
                        listitem.select( False )
                        break

                    # download file for extra thumbs or fanarts
                    try:
                        ok = xbmcvfs.copy( url, dest )
                        print "%r xbmcvfs.copy( %r, %r )" % ( ok, url, dest )
                    except:
                        LOGGER.error.LOG( url )
                        dest = None
                        LOGGER.error.print_exc()

                    listitem.select( False )
                    if DIALOG_PROGRESS.iscanceled():
                        break
                self._close_dialog()
        except:
            LOGGER.error.print_exc()

        if xbmc.getCondVisibility( "Window.IsVisible(progressdialog)" ):
            xbmc.executebuiltin( "Dialog.Close(progressdialog)" )
        self.select_all = False
        #try: DIALOG_PROGRESS.close()
        #except: pass

    def onAction( self, action ):
        if action in CLOSE_DIALOG:
            if xbmc.getCondVisibility( "Control.IsVisible(451)" ):
                # toggle list control
                self.getControl( self.CONTROL_LIST_451 ).reset()
                self.getControl( self.CONTROL_LIST_451 ).setEnabled( 0 )
                self.getControl( self.CONTROL_LIST_451 ).setVisible( 0 )
                self.control_list.setEnabled( 1 )
                self.control_list.setVisible( 1 )
                self.setFocus( self.control_list )
                self.getControl( self.CONTROL_BUTTON_CREATE ).setEnabled( 1 )
                self.getControl( self.CONTROL_BUTTON_OK ).setEnabled( 1 )
            else:
                self._close_dialog()

    def _close_dialog( self, t=500 ):
        self.close()
        if t: xbmc.sleep( t )



def browser( **kwargs ):
    #wb = Browser( "script-MovieSets-Browser.xml", ADDON_DIR, **kwargs )
    wb = Browser( "FileBrowser.xml", ADDON_DIR, **kwargs )
    xbmc.executebuiltin( 'Dialog.Close(busydialog,true)' )
    wb.doModal()
    movieset_update = wb.movieset_update
    del wb

    return movieset_update

