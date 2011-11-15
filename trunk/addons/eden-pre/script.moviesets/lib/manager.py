
import time
START_TIME = time.time()

# Modules General
import os
import sys
from glob import glob

# Modules XBMC
import xbmc
import xbmcgui
import xbmcvfs
from xbmcaddon import Addon


# Modules Custom
from utils.log import logAPI
from database import Database, TBN


# Constants
LOGGER   = logAPI()
DATABASE = Database()
DB_PATHS = glob( xbmc.translatePath( "special://Database/MyVideos*.db" ) )[ -1: ]

# constants
ADDON      = Addon( "script.moviesets" )
ADDON_DIR  = ADDON.getAddonInfo( "path" )

Language = ADDON.getLocalizedString # ADDON strings
LangXBMC = xbmc.getLocalizedString # XBMC strings

#https://raw.github.com/xbmc/xbmc/master/xbmc/guilib/Key.h
ACTION_PARENT_DIR    = 9
ACTION_PREVIOUS_MENU = 10
ACTION_NAV_BACK      = 92
ACTION_CONTEXT_MENU  = 117
KEYBOARD_A_BUTTON    = 61505
CLOSE_MANAGER        = [ ACTION_PARENT_DIR, ACTION_PREVIOUS_MENU, ACTION_NAV_BACK ]
CLOSE_DIALOG         = [ ACTION_CONTEXT_MENU ] + CLOSE_MANAGER


def _unicode( text, encoding="utf-8" ):
    try: text = unicode( text, encoding )
    except: pass
    return text


def path_exists( filename ):
    # first use os.path.exists and if not exists, test for share with xbmcvfs.
    return os.path.exists( filename ) or xbmcvfs.exists( filename )


def time_took( t ):
    t = ( time.time() - t )
    if t >= 60: return "%.3fm" % ( t / 60.0 )
    return "%.3fs" % ( t )



class DialogContextMenu( xbmcgui.WindowXMLDialog ):
    CONTROLS_BUTTON = range( 1001, 1012 )

    def __init__( self, *args, **kwargs ):
        self.buttons  = kwargs[ "buttons" ]
        self.selected = -1
        self.doModal()

    def onInit( self ):
        try:
            for control in self.CONTROLS_BUTTON:
                try:
                    self.getControl( control ).setLabel( "" )
                    self.getControl( control ).setVisible( False )
                except:
                    pass
            for count, button in enumerate( self.buttons ):
                try:
                    self.getControl( 1001 + count ).setLabel( button )
                    self.getControl( 1001 + count ).setVisible( True )
                except:
                    pass
            self.setFocusId( 1001 )
        except:
            LOGGER.error.exc_info( sys.exc_info(), self )

    def onFocus( self, controlID ):
        pass

    def onClick( self, controlID ):
        try:
            self.selected = ( controlID - 1001 )
            if self.selected < 0: self.selected = -1
        except:
            self.selected = -1
            LOGGER.error.exc_info( sys.exc_info(), self )
        self._close_dialog()

    def onAction( self, action ):
        if action in CLOSE_DIALOG:
            self.selected = -1
            self._close_dialog()

    def _close_dialog( self ):
        self.close()



class Manager( xbmcgui.WindowXMLDialog ):
    CONTAINER_MOVIESETS_ID      = 151
    CONTAINER_MOVIES_IN_SET_ID  = 251
    CONTAINER_ALL_MOVIES_ID     = 351
    ID_MOVIE_IN_SET             = "Container(251).ListItem.Property(idMovie)"
    COND_SYNCHRONIZE_CONTAINERS = "StringCompare(Container(151).ListItem.Property(idSet),Container(251).ListItem.Property(idSet))"

    def __init__( self, *args, **kwargs ):
        self.idSetOnLoad = ( xbmc.getInfoLabel( "Container(%s).ListItem.Property(idSet)" % ADDON.getSetting( "containerId" ) ) or "0" )

    def onFocus( self, controlID ):
        pass

    def onInit( self ):
        self.container_moviesets     = self.getControl( self.CONTAINER_MOVIESETS_ID )
        self.container_movies_in_set = self.getControl( self.CONTAINER_MOVIES_IN_SET_ID )
        self.container_all_movies    = self.getControl( self.CONTAINER_ALL_MOVIES_ID )
        self.setContainers( self.idSetOnLoad  )

    def setIconFanartImages( self, idSet, listitem ):
        try:
            fanart = TBN.get_cached_saga_thumb( idSet, True )
            fanart = ( "", fanart )[ path_exists( fanart ) ]
            listitem.setProperty( "fanart_image", fanart )
        except:
            LOGGER.error.exc_info( sys.exc_info(), self )
        try:
            icon = TBN.get_cached_saga_thumb( idSet )
            icon = ( "", icon )[ path_exists( icon ) ]
            listitem.setIconImage( icon )
        except:
            LOGGER.error.exc_info( sys.exc_info(), self )

    def getMoviesInSet( self, idSet ):
        movieset = []
        try:
            for movie in DATABASE.getMovies( idSet, True ):
                li = xbmcgui.ListItem( movie[ "strTitle" ], movie[ "strSort" ] )
                li.setProperty( "idMovie", movie[ "idMovie" ] )
                li.setProperty( "idSet", str( idSet ) )
                movieset.append( li )
        except:
            LOGGER.error.exc_info( sys.exc_info(), self )
        return movieset

    def setContainers( self, select_idSet="0" ):
        try:
            moviesets = DATABASE.getSets( True )
            if not moviesets:
                if not self.createNewSet( False ):
                    self._close_dialog()
                    return
            moviesets = DATABASE.getSets( True )

            self.listitems = []
            self.moviesets = {}
            #
            selectitem = 0
            for count, set in enumerate( moviesets ):
                idSet, strSet = set[ 0 ], set[ 1 ]
                # for test next page
                #self.listitems.append( xbmcgui.ListItem( strSet, str( idSet ) )

                li = xbmcgui.ListItem( strSet, str( idSet ) )
                li.setProperty( "idSet", str( idSet ) )
                self.setIconFanartImages( idSet, li )

                movieset = self.getMoviesInSet( idSet )
                self.moviesets[ str( idSet ) ] = movieset

                li.setProperty( "TotalMovies", str( len( movieset ) ) )
                self.listitems.append( li )
                if int( idSet ) == int( select_idSet ):
                    selectitem = count
            #
            self.container_moviesets.reset()
            self.container_moviesets.addItems( self.listitems )
            self.container_moviesets.selectItem( selectitem )
            self.setFocusId( self.CONTAINER_MOVIESETS_ID )
            #
            self.container_all_movies.reset()
            #
            idMovie = xbmc.getInfoLabel( self.ID_MOVIE_IN_SET ) or "0"
            self.setContainerMoviesInSet( self.moviesets[ self.listitems[ selectitem ].getLabel2() ], idMovie )
        except:
            LOGGER.error.exc_info( sys.exc_info(), self )
        LOGGER.notice.LOG( "Manager initialized took %s", time_took( START_TIME ) )

    def setContainerMoviesInSet( self, movieset, select_idMovie="0" ):
        try:
            selectitem = 0
            if select_idMovie != "0":
                try:
                    for count, movie in enumerate( movieset ):
                        if int( movie.getProperty( "idMovie" ) ) == int( select_idMovie ):
                            selectitem = count
                            break
                except:
                    LOGGER.error.exc_info( sys.exc_info(), self )

            self.container_movies_in_set.reset()
            self.container_movies_in_set.addItems( movieset )
            self.container_movies_in_set.selectItem( selectitem )
        except:
            LOGGER.error.exc_info( sys.exc_info(), self )

    def setContainerAllMovies( self, idSet ):
        try:
            # Add Container for All Movies
            list_movies = []
            movies_in_set = [ l.getProperty( "idMovie" ) for l in self.moviesets[ idSet ] ]
            for idMovie, strTitle, strSort in DATABASE.getMovies():
                li = xbmcgui.ListItem( strTitle, strSort )
                li.setProperty( "idMovie", idMovie )
                SetHasMovie = ( "", "true" )[ ( idMovie in movies_in_set ) ]
                li.setProperty( "SetHasMovie", SetHasMovie )
                list_movies.append( li )

            self.container_all_movies.reset()
            self.container_all_movies.addItems( list_movies )
            self.setFocusId( self.CONTAINER_ALL_MOVIES_ID )

        except:
            LOGGER.error.exc_info( sys.exc_info(), self )

    def sendClick( self, controlID ):
        try: self.onClick( controlID )
        except: LOGGER.error.exc_info( sys.exc_info(), self )

    def onClick( self, controlID ):
        try:
            if controlID in [ self.CONTAINER_MOVIESETS_ID, self.CONTAINER_MOVIES_IN_SET_ID ]:
                item = self.getControl( controlID ).getSelectedItem()
                self.onContextMenu( controlID, item )

            elif controlID == self.CONTAINER_ALL_MOVIES_ID:
                OK = False
                item = self.container_all_movies.getSelectedItem()
                item.select( 1 )
                strTitle = item.getLabel()
                strSet   = self.container_moviesets.getSelectedItem().getLabel()
                if item.getProperty( "SetHasMovie" ) == "true":
                    # Remove Movie to current movie set
                    if xbmcgui.Dialog().yesno( Language( 32112 ), LangXBMC( 750 ), Language( 32113 ) % _unicode( strTitle ), Language( 32114 ) % _unicode( strSet ) ):
                        idSet   = self.container_moviesets.getSelectedItem().getProperty( "idSet" )
                        idMovie = item.getProperty( "idMovie" )
                        OK = DATABASE.deleteMovieOfSet( idMovie, idSet )
                        if OK:
                            item.setProperty( "SetHasMovie", "" )
                            self.moviesets[ str( idSet ) ] = self.getMoviesInSet( idSet )
                            self.setContainerMoviesInSet( self.moviesets[ str( idSet ) ], idMovie )
                else:
                    # Add New Movie to current movie set
                    if xbmcgui.Dialog().yesno( Language( 32102 ), LangXBMC( 750 ), Language( 32103 ) % _unicode( strTitle ), Language( 32104 ) % _unicode( strSet ) ):
                        idSet   = self.container_moviesets.getSelectedItem().getProperty( "idSet" )
                        idMovie = item.getProperty( "idMovie" )
                        OK = DATABASE.addSetToMovie( idMovie, idSet )
                        if OK:
                            item.setProperty( "SetHasMovie", "true" )
                            self.moviesets[ str( idSet ) ] = self.getMoviesInSet( idSet )
                            self.setContainerMoviesInSet( self.moviesets[ str( idSet ) ], idMovie )
                item.select( 0 )
        except:
            LOGGER.error.exc_info( sys.exc_info(), self )

    def onContextMenu( self, controlID, listItem ):
        listItem.select( 1 )
        try:
            buttons = []
            selected = -1
            if controlID == self.CONTAINER_MOVIESETS_ID:
                buttons += [ Language( 32100 ), Language( 32221 ), LangXBMC( 646 ), Language( 32330 ),
                             Language( 32120 ), Language( 32130 ) ]

            elif controlID == self.CONTAINER_MOVIES_IN_SET_ID:
                buttons += [ Language( 32100 ), Language( 32220 ), Language( 32110 ), Language( 32330 ) ]

            on_all_movies = self.container_all_movies.size()
            if buttons:
                if on_all_movies: del buttons[ 0 ]
                cm = DialogContextMenu( "script-MovieSets-ContextMenu.xml", ADDON_DIR, buttons=buttons )
                selected = cm.selected
                del cm
                heading = buttons[ selected ]
                if selected >= 0 and on_all_movies:
                    selected += 1

            if selected == 0:
                # Add Container for All Movies
                self.setContainerAllMovies( listItem.getProperty( "idSet" ) )

            elif selected == 1:
                # Edit Set title or Edit movie sorttitle
                title = ""
                if controlID == self.CONTAINER_MOVIESETS_ID:
                    title = listItem.getLabel()
                elif controlID == self.CONTAINER_MOVIES_IN_SET_ID:
                    title = listItem.getLabel2()

                new_title = self.keyboard( title, heading )
                if new_title and new_title != title:
                    if xbmcgui.Dialog().yesno( heading, "Old: %s" % _unicode( title ), "New: %s" % _unicode( new_title ), "", LangXBMC( 222 ), LangXBMC( 186 ) ):
                        if controlID == self.CONTAINER_MOVIESETS_ID:
                            idSet = listItem.getProperty( "idSet" )
                            OK = DATABASE.editMovieSetTitle( new_title, idSet )
                            if OK:
                                # don't reload containers, set label only :)
                                listItem.setLabel( new_title )

                        if controlID == self.CONTAINER_MOVIES_IN_SET_ID:
                            idMovie = listItem.getProperty( "idMovie" )
                            OK = DATABASE.editMovieSortTitle( new_title, idMovie )
                            if OK:
                                idSet = listItem.getProperty( "idSet" )
                                self.moviesets[ str( idSet ) ] = self.getMoviesInSet( idSet )
                                self.setContainerMoviesInSet( self.moviesets[ str( idSet ) ], idMovie )

            elif selected == 2:
                # Remove current movieset
                if controlID == self.CONTAINER_MOVIESETS_ID:
                    strSet = listItem.getLabel()
                    if xbmcgui.Dialog().yesno( Language( 32141 ), LangXBMC( 433 ) % _unicode( strSet ) ):
                        idSet = listItem.getProperty( "idSet" )
                        OK = DATABASE.deleteSet( idSet )
                        if OK:
                            self.setContainers( "0" )

                # Remove movie to current movieset
                if controlID == self.CONTAINER_MOVIES_IN_SET_ID:
                    strTitle = listItem.getLabel()
                    strSet   = self.container_moviesets.getSelectedItem().getLabel()
                    if xbmcgui.Dialog().yesno( Language( 32112 ), LangXBMC( 750 ), Language( 32113 ) % _unicode( strTitle ), Language( 32114 ) % _unicode( strSet ) ):
                        idSet   = listItem.getProperty( "idSet" )
                        idMovie = listItem.getProperty( "idMovie" )
                        OK = DATABASE.deleteMovieOfSet( idMovie, idSet )
                        if OK:
                            self.moviesets[ str( idSet ) ] = self.getMoviesInSet( idSet )
                            self.setContainerMoviesInSet( self.moviesets[ str( idSet ) ], "0" )

            elif selected == 3:
                # Create new movieset
                self.createNewSet()

            elif selected in [ 4, 5 ]:
                # Set movieset fanart or Set movieset thumb
                listItem.setIconImage( "" )
                listItem.setProperty( "fanart_image", "" )
                xbmc.sleep( 500 )
                #time.sleep( .5 )
                from dialogs import browser
                self.movieset_update = browser( notaction=True,
                    heading=listItem.getLabel(),
                    idset=listItem.getProperty( "idSet" ),
                    type=( "fanart", "thumb" )[ selected - 4 ]
                    )
                del browser
                self.setIconFanartImages( listItem.getProperty( "idSet" ), listItem )
        except:
            LOGGER.error.exc_info( sys.exc_info(), self )
        try: listItem.select( 0 )
        except: pass

    def createNewSet( self, LibraryHasMovieSets=True ):
        OK = False
        try:
            # Create new movieset
            while True:
                OK = False
                new_set = self.keyboard( "", Language( 32330 ) )
                if new_set and new_set.isdigit():
                    xbmcgui.Dialog().ok( "Hmmm!!!", "Don't use only digit number!" )
                    continue

                if new_set:
                    if xbmcgui.Dialog().yesno( Language( 32330 ), "New Set: %s" % _unicode( new_set ), "", "", LangXBMC( 222 ), LangXBMC( 186 ) ):
                        idSet = DATABASE.addSet( new_set )
                        if idSet != -1:
                            if not LibraryHasMovieSets: OK = True
                            else: self.setContainers( idSet )
                break
        except:
            LOGGER.error.exc_info( sys.exc_info(), self )
        return OK

    def keyboard( self, default="", heading=LangXBMC( 528 ) ):
        kb = xbmc.Keyboard( default, heading )
        kb.doModal()
        if kb.isConfirmed():
            return kb.getText()

    def synchronize( self ):
        try:
            if not xbmc.getCondVisibility( self.COND_SYNCHRONIZE_CONTAINERS ):
                movieset = self.moviesets[ self.container_moviesets.getSelectedItem().getLabel2() ]
                self.container_movies_in_set.reset()
                self.container_movies_in_set.addItems( movieset )
        except:
            LOGGER.error.exc_info( sys.exc_info(), self )

    def onAction( self, action ):
        self.synchronize()

        try: toggle_container = ( action.getButtonCode() == KEYBOARD_A_BUTTON )
        except: toggle_container = False
        if toggle_container:
            try:
                if not self.container_all_movies.size():
                    # Add Container for All Movies
                    idSet = self.container_moviesets.getSelectedItem().getProperty( "idSet" )
                    self.setContainerAllMovies( idSet )
                else:
                    xbmc.executebuiltin( "Action(ParentDir)" )
            except:
                LOGGER.error.exc_info( sys.exc_info(), self )

        elif action == ACTION_CONTEXT_MENU:
            try: self.sendClick( self.getFocusId() )
            except: LOGGER.error.exc_info( sys.exc_info(), self )

        elif action in CLOSE_MANAGER:
            try:
                if self.container_all_movies.size():
                    self.container_all_movies.reset()
                    self.setFocusId( self.CONTAINER_MOVIESETS_ID )
                else:
                    self._close_dialog()
            except:
                LOGGER.error.exc_info( sys.exc_info(), self )
                self.close()

    def _close_dialog( self ):
        self.close()



if ( __name__ == "__main__" ):
    mtime = sum( [ os.path.getmtime( db ) for db in DB_PATHS ] )

    w = Manager( "script-MovieSets-Manager.xml", ADDON_DIR )
    w.doModal()
    del w

    if ADDON.getSetting( "exporting" ) == "true" and sum( [ os.path.getmtime( db ) for db in DB_PATHS ] ) > mtime:
        if xbmcgui.Dialog().yesno( "Movie Sets changed...", "If you want save your change in NFO files.", LangXBMC( 647 ), "", LangXBMC( 222 ), LangXBMC( 650 ) ):
            xbmc.executebuiltin( "ActivateWindow(VideosSettings)" )
            # set Library button
            xbmc.executebuiltin( "SetFocus(-100)" )
            # set Export video library button
            xbmc.executebuiltin( "SetFocus(-73)" )
            # select Export video library
            xbmc.executebuiltin( "Action(Select)" )
