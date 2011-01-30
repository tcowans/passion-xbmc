
# Modules general
import os
import sys

# Modules XBMC
import xbmc
import xbmcgui
from xbmcaddon import Addon

# Modules Custom
from database import Database, TBN
from log import logAPI

log = logAPI()

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


class Manager:
    # get and set required infos
    IS_CONTENT_MOVIES = xbmc.getCondVisibility( "Container.Content(Movies)" )
    IS_CONTENT_SETS = xbmc.getCondVisibility( "StringCompare(Container.FolderPath,videodb://1/7/)" )

    CURRENT_LABEL = xbmc.getInfoLabel( "Container.ListItem.Label" )
    PATH, FILENAME = os.path.split( xbmc.getInfoLabel( "Container.ListItem.FilenameAndPath" ) )
    if PATH: PATH += ( "/", "\\" )[ not PATH.count( "/" ) ]

    def __init__( self, *args, **kwargs ):
        self.movieset_update = False
        # add dialog select, GUI manager is not started :)

        pre_heading = ""
        self.heading = __language__( 32001 ) #"Manager Movie Sets"
        buttons, choices = [], []

        if self.IS_CONTENT_MOVIES and not self.PATH:
            if database.getSet( self.CURRENT_LABEL ):
                self.IS_CONTENT_SETS = True

        if self.IS_CONTENT_SETS:
            # on set
            self.idSet, self.strSet = database.getSet( self.CURRENT_LABEL )
            self.heading = ( self.strSet or self.CURRENT_LABEL )
            pre_heading = __language__( 32003 )#"[Set] "
            if ( self.idSet > -1 ):
                buttons = [ 1000, 1001, 1002, 1003, 1004 ]
                #choices = [ "Add Movie", "Remove Movie", "Set movieset fanart", "Set movieset thumb", "Remove this movieset [%s]" % self.strSet ]
                choices = [ __language__( 32100 ), __language__( 32110 ), __language__( 32120 ),
                    __language__( 32130 ), __language__( 32140 ) % _unicode( self.strSet ) ]

        elif self.IS_CONTENT_MOVIES:
            # on movie
            self.idMovie, self.strTitle, self.strSortTitle = database.getMovie( self.PATH+self.FILENAME, self.CURRENT_LABEL )
            self.heading = ( self.strTitle or self.CURRENT_LABEL )
            pre_heading = __language__( 32004 )#"[Movie] "
            if ( self.idMovie > -1 ):
                self.idSet, self.strSet = database.getSetByIdMovie( self.idMovie )
                if ( self.idSet == -1 ):
                     # add to movieset
                    buttons.append( 2000 )
                    choices.append( __language__( 32200 ) )#"Add to movieset"
                else:
                    # remove from movieset
                    buttons.append( 2001 )
                    choices.append( __language__( 32210 ) % _unicode( self.strSet ) )#"Remove movie of set [%s]"
                    #
                    buttons.append( 2002 )
                    button1008 = ( " [%s]" % self.strSortTitle, "" )[ not self.strSortTitle ]
                    choices.append( __language__( 32220 ) + _unicode( button1008 ) )#"Edit sorttitle movie%s"

        # defaults buttons for all view
        buttons += [ 3000, 3001, 3002, 3003 ]
        #choices += [ "Add movies to existing movieset", "Remove movies to existing movieset", "Remove existing movieset", "Create new movieset" ]
        choices += [ __language__( 32300 ), __language__( 32310 ), __language__( 32320 ), __language__( 32330 ) ]

        xbmc.executebuiltin( "Dialog.Close(busydialog)" )
        while True:
            selected = xbmcgui.Dialog().select( pre_heading + _unicode( self.heading ), choices )
            if selected == -1: break

            button = buttons[ selected ]
            if button in [ 1002, 1003 ]:
                # Set movieset fanart or Set movieset thumb
                self.browse( ( "fanart", "thumb" )[ button - 1002 ] )

            elif button == 1004:
                # Remove this movieset "Remove movieset from library"
                if xbmcgui.Dialog().yesno( __language__( 32141 ), __string__( 433 ) % self.heading ):
                    if database.deleteSet( self.idSet ):
                        pre_heading, self.heading = "", __language__( 32001 )#"Manager Movie Sets"
                        self.idSet, self.strSet = -1, ""
                        buttons = buttons[ -4: ]
                        choices = choices[ -4: ]

            elif button == 3002:
                # Remove existing movieset
                idSet, strSet = self.selectSet( __language__( 32321 ) )#"Select movieset to remove"
                if ( idSet > 0 ) and xbmcgui.Dialog().yesno( __language__( 32141 ), __string__( 433 ) % strSet ):
                    OK = database.deleteSet( idSet )

            elif button == 1001:
                # Remove movie to current movieset
                idMovie, strTitle, strSortTitle = self.selectMovieOfSet( self.idSet, __language__( 32111 ) % _unicode( self.strSet ) )#"Remove movie of set [%s]"
                if ( idMovie > 0 ) and xbmcgui.Dialog().yesno( __language__( 32112 ), __string__( 750 ), __language__( 32113 ) % _unicode( strTitle ), __language__( 32114 ) % _unicode( self.strSet ) ):
                    OK = database.deleteMovieOfSet( idMovie, self.idSet )

            elif button == 3003:
                # Create new movieset
                strSet = self.keyboard( self.heading, __language__( 32331 ) )#'Enter title of set'#.replace( __language__( 32001 ), "" )
                if strSet:
                    idSet = database.addSet( strSet )

            elif button == 2001:
                # Remove movie of movieset
                if xbmcgui.Dialog().yesno( __language__( 32112 ), __string__( 750 ), __language__( 32113 ) % _unicode( self.strTitle ), __language__( 32114 ) % _unicode( self.strSet ) ):
                    OK = database.deleteMovieOfSet( self.idMovie, self.idSet )
                    if OK:
                        self.idSet, self.strSet = -1, ""
                        try:
                            buttons[ 0 ] = 2000
                            choices[ 0 ] = __language__( 32200 )#"Add to movieset"
                            if buttons[ 1 ] == 2002:
                                del buttons[ 1 ], choices[ 1 ]
                        except: log.error.exc_info( sys.exc_info(), self )

            elif button == 3001:
                # Remove movies to existing movieset
                while True:
                    idSet, strSet = self.selectSet( __language__( 32311 ), True )#"Select movieset"
                    if idSet == -1: break
                    while True:
                        idMovie, strTitle, strSortTitle = self.selectMovieOfSet( idSet, __language__( 32210 ) % _unicode( strSet ) )#"Remove movie of set [%s]"
                        if idMovie == -1: break
                        if ( idMovie > 0 ) and xbmcgui.Dialog().yesno( __language__( 32112 ), __string__( 750 ), __language__( 32113 ) % _unicode( strTitle ), __language__( 32114 ) % _unicode( strSet ) ):
                            OK = database.deleteMovieOfSet( idMovie, idSet )
                
            elif button == 2000:
                # Add to movieset
                idSet, strSet = self.selectSet( __language__( 32201 ) % _unicode( self.heading ), create=self.heading )#"Select movieset for [%s]"
                if ( idSet > 0 ) and xbmcgui.Dialog().yesno( __language__( 32102 ), __string__( 750 ), __language__( 32103 ) % _unicode( self.heading ), __language__( 32104 ) % _unicode( strSet ) ):
                    if database.addSetToMovie( self.idMovie, idSet ):
                        self.idSet, self.strSet = idSet, strSet
                        try:
                            buttons[ 0 ] = 2001
                            choices[ 0 ] = __language__( 32111 ) % _unicode( self.strSet )#"Remove movie of set [%s]"
                            if buttons[ 1 ] != 2002:
                                buttons.insert( 1, 2002 )
                                button1008 = ( " [%s]" % self.strSortTitle, "" )[ not self.strSortTitle ]
                                choices.insert( 1, __language__( 32220 ) + _unicode( button1008 ) )#"Edit sorttitle movie%s"
                        except: log.error.exc_info( sys.exc_info(), self )
                        #
                        sortTitle = self.strSortTitle or self.strTitle
                        newSortTitle = self.keyboard( sortTitle, __language__( 32220 ) )#"Edit sorttitle movie"
                        if newSortTitle is not None and newSortTitle != self.strSortTitle:
                            OK = database.editMovieSortTitle( newSortTitle, self.idMovie )
                            if OK:
                                self.strSortTitle = newSortTitle
                                button1008 = ( " [%s]" % self.strSortTitle, "" )[ not self.strSortTitle ]
                                try: choices[ 1 ] = __language__( 32220 ) + _unicode( button1008 )#"Edit sorttitle movie%s"
                                except: log.error.exc_info( sys.exc_info(), self )

            elif button == 2002:
                # Edit sorttitle movie
                sortTitle = self.strSortTitle or self.strTitle
                newSortTitle = self.keyboard( sortTitle, __language__( 32220 ) )#"Edit sorttitle movie"
                if newSortTitle is not None and newSortTitle != self.strSortTitle:
                    OK = database.editMovieSortTitle( newSortTitle, self.idMovie )
                    if OK:
                        self.strSortTitle = newSortTitle
                        button1008 = ( " [%s]" % self.strSortTitle, "" )[ not self.strSortTitle ]
                        try: choices[ 1 ] = __language__( 32220 ) + _unicode( button1008 )#"Edit sorttitle movie%s"
                        except: log.error.exc_info( sys.exc_info(), self )

            elif button == 1000:
                # Add Movie to current movieset
                idMovie, strTitle, strSortTitle = self.selectMovie( __language__( 32101 ) % _unicode( self.strSet ) )#"Select movie for set [%s]"
                if ( idMovie > 0 ) and xbmcgui.Dialog().yesno( __language__( 32102 ), __string__( 750 ), __language__( 32103 ) % _unicode( strTitle ), __language__( 32104 ) % _unicode( self.strSet ) ):
                    #
                    if database.addSetToMovie( idMovie, self.idSet ):
                        #
                        sortTitle = strSortTitle or strTitle
                        newSortTitle = self.keyboard( sortTitle, __language__( 32220 ) )#"Edit sorttitle movie"
                        if newSortTitle is not None and newSortTitle != strSortTitle:
                            OK = database.editMovieSortTitle( newSortTitle, idMovie )

            elif button == 3000:
                # Add movies to existing movieset
                idMovie, strTitle, strSortTitle = self.selectMovie( __language__( 32301 ) )#"Select movie"
                if ( idMovie > 0 ):
                    idSet, strSet = self.selectSet( __language__( 32302 ) % _unicode( strTitle ), create=strTitle )#"Select movieset for movie [%s]"
                    if ( idSet > 0 ) and xbmcgui.Dialog().yesno( __language__( 32102 ), __string__( 750 ), __language__( 32103 ) % _unicode( strTitle ), __language__( 32104 ) % _unicode( strSet ) ):
                        #
                        if database.addSetToMovie( idMovie, idSet ):
                            #
                            strSortTitle = strSortTitle or strTitle
                            newSortTitle = self.keyboard( strSortTitle, __language__( 32220 ) )#"Edit sorttitle movie"
                            if newSortTitle is not None and newSortTitle != strSortTitle:
                                OK = database.editMovieSortTitle( newSortTitle, idMovie )

    def browse( self, type ):
        from dialogs import Browser
        w = Browser( "FileBrowser.xml", ADDON_DIR, heading=self.heading, idset=self.idSet, type=type )
        w.doModal()
        self._delete_files( w.delete_files )
        self.movieset_update = self.movieset_update or w.movieset_update
        del w, Browser

    def _delete_files( self, files ):
        for dl in files:
            try:
                if os.path.exists( dl ):
                    log.warning.LOG( "%s, FileDelete(%s)", xbmc.executehttpapi( "FileDelete(%s)" % dl ).replace( "<li>", "" ), dl )
                if os.path.exists( dl ):
                    os.remove( dl )
            except:
                log.error.exc_info( sys.exc_info(), self )

    def keyboard( self, default="", heading=__string__( 528 ) ):
        kb = xbmc.Keyboard( default, heading )
        kb.doModal()
        if kb.isConfirmed():
            return kb.getText()

    def selectMovie( self, heading ):
        try:
            movies = database.getMovies()
            choice = [ c0 for i, c0, c1 in movies ]
            selected = xbmcgui.Dialog().select( heading, choice )
            if selected != -1:
                movie = movies[ selected ]
                return int( movie[ 0 ] ), movie[ 1 ], movie[ 2 ]
        except:
            log.error.exc_info( sys.exc_info(), self )
        return -1, "", ""

    def selectMovieOfSet( self, idSet, heading ):
        try:
            movies = database.getMovies( idSet, True )
            choice = [ movie[ "strTitle" ] for movie in movies ]
            selected = xbmcgui.Dialog().select( heading, choice )
            if selected != -1:
                movie = movies[ selected ]
                return int( movie[ "idMovie" ] ), movie[ "strTitle" ], movie[ "strSort" ]
        except:
            log.error.exc_info( sys.exc_info(), self )
        return -1, "", ""

    def selectSet( self, heading, showCount=False, create="" ):
        try:
            if showCount:
                moviesets = database.getSets( True, True )
                choice = [ "[%s] %s" % ( c, s ) for i, s, c in moviesets ]
            else:
                moviesets = database.getSets( True )
                choice = [ s for i, s in moviesets ]

            if create: choice.append( "[B]%s[/B]" % __language__( 32330 ) )#"Create new movieset"
            while True:
                selected = xbmcgui.Dialog().select( heading, choice )
                if selected == -1: break
                if create and selected >= len( moviesets ):
                    # Create new movieset
                    strSet = self.keyboard( create, __language__( 32331 ) )#'Enter title of set'
                    if not strSet: continue
                    if database.addSet( strSet ) > -1:
                        return self.selectSet( heading, showCount, create )
                else:
                    idSet, strSet = moviesets[ selected ][ :2 ]
                    return int( idSet ), strSet
                break
        except:
            log.error.exc_info( sys.exc_info(), self )
        return -1, ""


def Main():
    xbmc.executebuiltin( "Skin.Reset(MovieSets.Sleep)" )
    xbmc.executebuiltin( "Skin.SetBool(MovieSets.Sleep)" )
    try:
        mtime = os.path.getmtime( "special://Database/MyVideos34.db" )
        if Manager().movieset_update:
            xbmc.executebuiltin( "SetProperty(MovieSets.Update,true)" )
        if os.path.getmtime( "special://Database/MyVideos34.db" ) > mtime:
            xbmc.executebuiltin( "Container.Refresh" )
    except:
        log.error.exc_info( sys.exc_info() )
    xbmc.executebuiltin( "Skin.Reset(MovieSets.Sleep)" )
    xbmc.executebuiltin( "Dialog.Close(busydialog)" )



if ( __name__ == "__main__" ):
    Main()
