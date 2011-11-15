
# Modules general
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

LOGGER   = logAPI()
DATABASE = Database()
DB_PATHS = glob( xbmc.translatePath( "special://Database/MyVideos*.db" ) )

# constants
ADDON    = Addon( "script.moviesets" )

Language = ADDON.getLocalizedString # ADDON strings
LangXBMC = xbmc.getLocalizedString # XBMC strings


def _unicode( text, encoding="utf-8" ):
    try: text = unicode( text, encoding )
    except: pass
    return text


def path_exists( filename ):
    # first use os.path.exists and if not exists, test for share with xbmcvfs.
    return os.path.exists( filename ) or xbmcvfs.exists( filename )


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
        self.heading = Language( 32001 ) #"Manager Movie Sets"
        buttons, choices = [], []

        if self.IS_CONTENT_MOVIES and not self.PATH:
            if DATABASE.getSet( self.CURRENT_LABEL ):
                self.IS_CONTENT_SETS = True

        if self.IS_CONTENT_SETS:
            # on set
            self.idSet, self.strSet = DATABASE.getSet( self.CURRENT_LABEL )
            self.heading = ( self.strSet or self.CURRENT_LABEL )
            pre_heading = Language( 32003 )#"[Set] "
            if ( self.idSet > -1 ):
                buttons = [ 1000, 1001, 1002, 1003, 1004 ]
                #choices = [ "Add Movie", "Remove Movie", "Set movieset fanart", "Set movieset thumb", "Remove this movieset [%s]" % self.strSet ]
                choices = [ Language( 32100 ), Language( 32110 ), Language( 32120 ),
                    Language( 32130 ), Language( 32140 ) % _unicode( self.strSet ) ]

        elif self.IS_CONTENT_MOVIES:
            # on movie
            self.idMovie, self.strTitle, self.strSortTitle = DATABASE.getMovie( self.PATH+self.FILENAME, self.CURRENT_LABEL )
            self.heading = ( self.strTitle or self.CURRENT_LABEL )
            pre_heading = Language( 32004 )#"[Movie] "
            if ( self.idMovie > -1 ):
                self.idSet, self.strSet = DATABASE.getSetByIdMovie( self.idMovie )
                if ( self.idSet == -1 ):
                     # add to movieset
                    buttons.append( 2000 )
                    choices.append( Language( 32200 ) )#"Add to movieset"
                else:
                    # remove from movieset
                    buttons.append( 2001 )
                    choices.append( Language( 32210 ) % _unicode( self.strSet ) )#"Remove movie of set [%s]"
                    #
                    buttons.append( 2002 )
                    button1008 = ( " [%s]" % self.strSortTitle, "" )[ not self.strSortTitle ]
                    choices.append( Language( 32220 ) + _unicode( button1008 ) )#"Edit sorttitle movie%s"

        # defaults buttons for all view
        buttons += [ 3000, 3001, 3002, 3003 ]
        #choices += [ "Add movies to existing movieset", "Remove movies to existing movieset", "Remove existing movieset", "Create new movieset" ]
        choices += [ Language( 32300 ), Language( 32310 ), Language( 32320 ), Language( 32330 ) ]

        while True:
            selected = xbmcgui.Dialog().select( pre_heading + _unicode( self.heading ), choices )
            if selected == -1: break

            button = buttons[ selected ]
            if button in [ 1002, 1003 ]:
                # Set movieset fanart or Set movieset thumb
                self.browse( ( "fanart", "thumb" )[ button - 1002 ] )

            elif button == 1004:
                # Remove this movieset "Remove movieset from library"
                if xbmcgui.Dialog().yesno( Language( 32141 ), LangXBMC( 433 ) % self.heading ):
                    if DATABASE.deleteSet( self.idSet ):
                        pre_heading, self.heading = "", Language( 32001 )#"Manager Movie Sets"
                        self.idSet, self.strSet = -1, ""
                        buttons = buttons[ -4: ]
                        choices = choices[ -4: ]

            elif button == 3002:
                # Remove existing movieset
                idSet, strSet = self.selectSet( Language( 32321 ) )#"Select movieset to remove"
                if ( idSet > 0 ) and xbmcgui.Dialog().yesno( Language( 32141 ), LangXBMC( 433 ) % strSet ):
                    OK = DATABASE.deleteSet( idSet )

            elif button == 1001:
                # Remove movie to current movieset
                idMovie, strTitle, strSortTitle = self.selectMovieOfSet( self.idSet, Language( 32111 ) % _unicode( self.strSet ) )#"Remove movie of set [%s]"
                if ( idMovie > 0 ) and xbmcgui.Dialog().yesno( Language( 32112 ), LangXBMC( 750 ), Language( 32113 ) % _unicode( strTitle ), Language( 32114 ) % _unicode( self.strSet ) ):
                    OK = DATABASE.deleteMovieOfSet( idMovie, self.idSet )

            elif button == 3003:
                # Create new movieset
                strSet = self.keyboard( self.heading, Language( 32331 ) )#'Enter title of set'#.replace( Language( 32001 ), "" )
                if strSet:
                    idSet = DATABASE.addSet( strSet )

            elif button == 2001:
                # Remove movie of movieset
                if xbmcgui.Dialog().yesno( Language( 32112 ), LangXBMC( 750 ), Language( 32113 ) % _unicode( self.strTitle ), Language( 32114 ) % _unicode( self.strSet ) ):
                    OK = DATABASE.deleteMovieOfSet( self.idMovie, self.idSet )
                    if OK:
                        self.idSet, self.strSet = -1, ""
                        try:
                            buttons[ 0 ] = 2000
                            choices[ 0 ] = Language( 32200 )#"Add to movieset"
                            if buttons[ 1 ] == 2002:
                                del buttons[ 1 ], choices[ 1 ]
                        except: LOGGER.error.exc_info( sys.exc_info(), self )

            elif button == 3001:
                # Remove movies to existing movieset
                while True:
                    idSet, strSet = self.selectSet( Language( 32311 ), True )#"Select movieset"
                    if idSet == -1: break
                    while True:
                        idMovie, strTitle, strSortTitle = self.selectMovieOfSet( idSet, Language( 32210 ) % _unicode( strSet ) )#"Remove movie of set [%s]"
                        if idMovie == -1: break
                        if ( idMovie > 0 ) and xbmcgui.Dialog().yesno( Language( 32112 ), LangXBMC( 750 ), Language( 32113 ) % _unicode( strTitle ), Language( 32114 ) % _unicode( strSet ) ):
                            OK = DATABASE.deleteMovieOfSet( idMovie, idSet )

            elif button == 2000:
                # Add to movieset
                idSet, strSet = self.selectSet( Language( 32201 ) % _unicode( self.heading ), create=self.heading )#"Select movieset for [%s]"
                if ( idSet > 0 ) and xbmcgui.Dialog().yesno( Language( 32102 ), LangXBMC( 750 ), Language( 32103 ) % _unicode( self.heading ), Language( 32104 ) % _unicode( strSet ) ):
                    if DATABASE.addSetToMovie( self.idMovie, idSet ):
                        self.idSet, self.strSet = idSet, strSet
                        try:
                            buttons[ 0 ] = 2001
                            choices[ 0 ] = Language( 32111 ) % _unicode( self.strSet )#"Remove movie of set [%s]"
                            if buttons[ 1 ] != 2002:
                                buttons.insert( 1, 2002 )
                                button1008 = ( " [%s]" % self.strSortTitle, "" )[ not self.strSortTitle ]
                                choices.insert( 1, Language( 32220 ) + _unicode( button1008 ) )#"Edit sorttitle movie%s"
                        except: LOGGER.error.exc_info( sys.exc_info(), self )
                        #
                        sortTitle = self.strSortTitle or self.strTitle
                        newSortTitle = self.keyboard( sortTitle, Language( 32220 ) )#"Edit sorttitle movie"
                        if newSortTitle is not None and newSortTitle != self.strSortTitle:
                            OK = DATABASE.editMovieSortTitle( newSortTitle, self.idMovie )
                            if OK:
                                self.strSortTitle = newSortTitle
                                button1008 = ( " [%s]" % self.strSortTitle, "" )[ not self.strSortTitle ]
                                try: choices[ 1 ] = Language( 32220 ) + _unicode( button1008 )#"Edit sorttitle movie%s"
                                except: LOGGER.error.exc_info( sys.exc_info(), self )

            elif button == 2002:
                # Edit sorttitle movie
                sortTitle = self.strSortTitle or self.strTitle
                newSortTitle = self.keyboard( sortTitle, Language( 32220 ) )#"Edit sorttitle movie"
                if newSortTitle is not None and newSortTitle != self.strSortTitle:
                    OK = DATABASE.editMovieSortTitle( newSortTitle, self.idMovie )
                    if OK:
                        self.strSortTitle = newSortTitle
                        button1008 = ( " [%s]" % self.strSortTitle, "" )[ not self.strSortTitle ]
                        try: choices[ 1 ] = Language( 32220 ) + _unicode( button1008 )#"Edit sorttitle movie%s"
                        except: LOGGER.error.exc_info( sys.exc_info(), self )

            elif button == 1000:
                # Add Movie to current movieset
                idMovie, strTitle, strSortTitle = self.selectMovie( Language( 32101 ) % _unicode( self.strSet ) )#"Select movie for set [%s]"
                if ( idMovie > 0 ) and xbmcgui.Dialog().yesno( Language( 32102 ), LangXBMC( 750 ), Language( 32103 ) % _unicode( strTitle ), Language( 32104 ) % _unicode( self.strSet ) ):
                    #
                    if DATABASE.addSetToMovie( idMovie, self.idSet ):
                        #
                        sortTitle = strSortTitle or strTitle
                        newSortTitle = self.keyboard( sortTitle, Language( 32220 ) )#"Edit sorttitle movie"
                        if newSortTitle is not None and newSortTitle != strSortTitle:
                            OK = DATABASE.editMovieSortTitle( newSortTitle, idMovie )

            elif button == 3000:
                # Add movies to existing movieset
                idMovie, strTitle, strSortTitle = self.selectMovie( Language( 32301 ) )#"Select movie"
                if ( idMovie > 0 ):
                    idSet, strSet = self.selectSet( Language( 32302 ) % _unicode( strTitle ), create=strTitle )#"Select movieset for movie [%s]"
                    if ( idSet > 0 ) and xbmcgui.Dialog().yesno( Language( 32102 ), LangXBMC( 750 ), Language( 32103 ) % _unicode( strTitle ), Language( 32104 ) % _unicode( strSet ) ):
                        #
                        if DATABASE.addSetToMovie( idMovie, idSet ):
                            #
                            strSortTitle = strSortTitle or strTitle
                            newSortTitle = self.keyboard( strSortTitle, Language( 32220 ) )#"Edit sorttitle movie"
                            if newSortTitle is not None and newSortTitle != strSortTitle:
                                OK = DATABASE.editMovieSortTitle( newSortTitle, idMovie )

    def browse( self, type ):
        from dialogs import browser
        self.movieset_update = browser( heading=self.heading, idset=self.idSet, type=type )#self.movieset_update or w.movieset_update
        xbmc.sleep( 100 )
        xbmc.executebuiltin( "Action(ParentDir)" )
        del browser

    def keyboard( self, default="", heading=LangXBMC( 528 ) ):
        kb = xbmc.Keyboard( default, heading )
        kb.doModal()
        if kb.isConfirmed():
            return kb.getText()

    def selectMovie( self, heading ):
        try:
            movies = DATABASE.getMovies()
            choice = [ c0 for i, c0, c1 in movies ]
            selected = xbmcgui.Dialog().select( heading, choice )
            if selected != -1:
                movie = movies[ selected ]
                return int( movie[ 0 ] ), movie[ 1 ], movie[ 2 ]
        except:
            LOGGER.error.exc_info( sys.exc_info(), self )
        return -1, "", ""

    def selectMovieOfSet( self, idSet, heading ):
        try:
            movies = DATABASE.getMovies( idSet, True )
            choice = [ movie[ "strTitle" ] for movie in movies ]
            selected = xbmcgui.Dialog().select( heading, choice )
            if selected != -1:
                movie = movies[ selected ]
                return int( movie[ "idMovie" ] ), movie[ "strTitle" ], movie[ "strSort" ]
        except:
            LOGGER.error.exc_info( sys.exc_info(), self )
        return -1, "", ""

    def selectSet( self, heading, showCount=False, create="" ):
        try:
            if showCount:
                moviesets = DATABASE.getSets( True, True )
                choice = [ "[%s] %s" % ( c, s ) for i, s, c in moviesets ]
            else:
                moviesets = DATABASE.getSets( True )
                choice = [ s for i, s in moviesets ]

            if create: choice.append( "[B]%s[/B]" % Language( 32330 ) )#"Create new movieset"
            while True:
                selected = xbmcgui.Dialog().select( heading, choice )
                if selected == -1: break
                if create and selected >= len( moviesets ):
                    # Create new movieset
                    strSet = self.keyboard( create, Language( 32331 ) )#'Enter title of set'
                    if not strSet: continue
                    if DATABASE.addSet( strSet ) > -1:
                        return self.selectSet( heading, showCount, create )
                else:
                    idSet, strSet = moviesets[ selected ][ :2 ]
                    return int( idSet ), strSet
                break
        except:
            LOGGER.error.exc_info( sys.exc_info(), self )
        return -1, ""


def Main():
    xbmc.executebuiltin( "Skin.Reset(MovieSets.Sleep)" )
    xbmc.executebuiltin( "Skin.SetBool(MovieSets.Sleep)" )
    try:
        mtime = sum( [ os.path.getmtime( db ) for db in DB_PATHS ] )
        if Manager().movieset_update:
            try: xbmcgui.Window( 10025 ).setProperty( "MovieSets.Update", "true" )
            except: xbmc.executebuiltin( "SetProperty(MovieSets.Update,true)" )
        if sum( [ os.path.getmtime( db ) for db in DB_PATHS ] ) > mtime:
            xbmc.executebuiltin( "Container.Refresh" )
    except:
        LOGGER.error.exc_info( sys.exc_info() )
    xbmc.executebuiltin( "Skin.Reset(MovieSets.Sleep)" )



if ( __name__ == "__main__" ):
    Main()
