
import time
START_TIME = time.time()

import os
import sys
from threading import Lock, Thread
from traceback import print_exc

import xbmc
import xbmcgui

from database import Database
from file_item import Thumbnails


DB = Database()
TBN = Thumbnails()


def getMovieSets():
    # get movie sets
    movie_sets = DB.fetch( DB.sql_movie_sets, DB.key_movie_sets )
    yield len( movie_sets )

    # set dymmy listitem label: container title , label2: total movie sets
    listitem = xbmcgui.ListItem( "Movie Sets", str( len( movie_sets ) ) )
    #
    moviesets = {}
    yield listitem, moviesets

    # enum movie sets
    for countset, movieset in enumerate( movie_sets ):
        try:
            # get list of movieset
            movies = DB.fetch( DB.sql_movie_by_idset % movieset[ "idSet" ], DB.key_movie_by_idset )
            # set base variables
            genres = set()
            total_movies = len( movies )
            watched, unwatched = 0, total_movies
            # get saga icon
            icon = TBN.get_cached_saga_thumb( movieset[ "idSet" ] )
            icon = ( "", icon )[ os.path.exists( icon ) ]
            # set movieset listitem
            listitem = xbmcgui.ListItem( movieset[ "strSet" ], movieset[ "idSet" ], icon )
            listitem.setPath( "ActivateWindow(10025,videodb://1/7/%s/)" % movieset[ "idSet" ] )
            plotset = ""
            Fanart_Image = ""
            fanartsets = set()
            # enum movie[ "idMovie", "strTitle", "strSort", "strGenre", "strPlot", "playCount", "strPath", "strFileName" ]
            for count, movie in enumerate( movies ):
                try:
                    # set watched count
                    if movie[ "playCount" ]: watched += 1
                    # update genres
                    genres.update( movie[ "strGenre" ].split( " / " ) )
                    # add plot movie to plotset
                    plotset += "[B]%(strTitle)s (%(strYear)s)[/B][CR]%(strPlot)s[CR][CR]" % movie
                    # set movie properties
                    b_property = "movie.%i." % ( count + 1 )
                    # strings property
                    listitem.setProperty( b_property + "Title",     movie[ "strTitle" ] )
                    listitem.setProperty( b_property + "sortTitle", movie[ "strSort" ] )
                    listitem.setProperty( b_property + "Filename",  movie[ "strFileName" ] )
                    listitem.setProperty( b_property + "Path",      movie[ "strPath" ] )
                    listitem.setProperty( b_property + "Plot",      movie[ "strPlot" ] )
                    # images property
                    c_icon = TBN.get_cached_video_thumb( movie[ "strPath" ] + movie[ "strFileName" ] )
                    icon = ( "", c_icon )[ os.path.exists( c_icon ) ]
                    if not icon: # check auto-
                        _path, _file = os.path.split( c_icon )
                        a_icon = os.path.join( _path, "auto-" + _file )
                        icon = ( "", a_icon )[ os.path.exists( a_icon ) ]
                    listitem.setProperty( b_property + "Icon", icon )
                    fanart = TBN.get_cached_fanart_thumb( movie[ "strPath" ] + movie[ "strFileName" ], "video" )
                    fanart = ( "", fanart )[ os.path.exists( fanart ) ]
                    listitem.setProperty( b_property + "Fanart", fanart )
                    if fanart and not Fanart_Image: Fanart_Image = fanart
                    # set extrafanart: if not exists set empty
                    extrafanart = movie[ "strPath" ] + "extrafanart"
                    extrafanart = ( "", extrafanart )[ os.path.exists( extrafanart ) ]
                    listitem.setProperty( b_property + "ExtraFanart", extrafanart )
                    # add possible path for folder fanartset
                    #print movie[ "strPath" ] + "extrafanart"
                    #print os.path.dirname( os.path.dirname( movie[ "strPath" ] ) ) + "/extrafanart"
                    fanartsets.add( os.path.dirname( os.path.dirname( movie[ "strPath" ] ) ) )
                except:
                    xbmc.log( "MovieSets::getMovieSets:enumerate( movies ): %s" % repr( movie ), xbmc.LOGERROR )
                    print_exc()

            # set movieset properties
            listitem.setProperty( "HasMovieSets",    "true" )
            listitem.setProperty( "WatchedMovies",   str( watched ) )
            listitem.setProperty( "UnWatchedMovies", str( unwatched - watched ) )
            listitem.setProperty( "TotalMovies",     str( total_movies ) )
            listitem.setProperty( "Fanart_Image",    Fanart_Image )
            listitem.setProperty( "ExtraFanart",     "" )
            # set extrafanart for movieset if exists set first found
            for fanartset in fanartsets:
                fanartset += ( "/", "\\" )[ not fanartset.count( "/" ) ] + "extrafanart"
                if os.path.exists( fanartset ):
                    listitem.setProperty( "ExtraFanart", fanartset )
                    break

            # set total duration info
            duration = DB.fetch( DB.sql_duration_by_idset % movieset[ "idSet" ], index=0 )
            if duration: duration = "".join( duration ).split( "." )[ 0 ]
            else: duration = ""
            # set RatingAndVotes info
            rating, votes = 0.0, ""
            RatingAndVotes = DB.fetch( DB.sql_ratingandvotes_by_idset % movieset[ "idSet" ], index=0 )
            if RatingAndVotes: rating, votes = float( RatingAndVotes[ 0 ] or "0.0" ), RatingAndVotes[ 1 ]
            # set listitem info
            infoslabels = {
                "title": movieset[ "strSet" ],
                "genre": " / ".join( sorted( genres ) ),
                "plot": plotset,
                "duration": duration,
                "rating": rating,
                "votes": votes
                }
            listitem.setInfo( "video", infoslabels )

            #context menu
            #c_items = [ ( "Info Movie Sets", "XBMC.Action(Info)" ) ]
            #listitem.addContextMenuItems( c_items )

            #
            moviesets[ movieset[ "strSet" ] ] = countset + 1
            yield listitem, moviesets
        except:
            xbmc.log( "MovieSets::getMovieSets:enumerate( movie_sets ): %s" % repr( movieset ), xbmc.LOGERROR )
            print_exc()

        # debug
        #print movieset[ "strSet" ]
        #print "Movies: %i (%i Watched / %i UnWatched)" % ( total_movies, watched, unwatched - watched )
        #print "%s Minutes" % duration
        #print "-"*100


class Main:
    def __init__( self ):
        self.args = dict( zip( [ "addonId", "containerId", "windowId", "busy" ], sys.argv ) )

        self.containerId = int( self.args.get( "containerId" ) or "7000" )
        empty = xbmc.getInfoLabel( "Container(%i).NumItems" % self.containerId ) == "0"
        #print empty
        if empty: self.initialize()

    def initialize( self ):
        try:
            self.windowId = int( self.args.get( "windowId" ) or "10025" )
            self.window = xbmcgui.Window( self.windowId )
            self.container = self.window.getControl( self.containerId )
            self.setContent()

            self.windowCond = "Window.IsVisible(%i)" % self.windowId
            self.containerLabel = "Container(%i).ListItem.Label" % self.containerId

            self.busydialog = self.args.get( "busy" ) == "busy"
            self.backend = Backend( self, Lock() )
            self.backend.setDaemon( True )
            self.backend.start()
        except:
            xbmc.log( "MovieSets::Main:initialize: %s" % repr( locals() ), xbmc.LOGERROR )
            print_exc()
        print "MovieSets: initialized took %.3fs" % ( time.time() - START_TIME )

    def setContent( self ):
        self.window.setProperty( "MovieSets.IsAlive", "true" )
        if xbmc.getInfoLabel( "Container.FolderPath" ) == "videodb://1/7/":
            self.window.setProperty( "Content.MovieSets", "true" )
        else:
            self.window.clearProperty( "Content.MovieSets" )

    def setContainer( self ):
        db_start_time = time.time()
        self.moviesets_db = getMovieSets() # generator type
        if not bool( self.moviesets_db.next() ):
            self.moviesets_db.close() # stop generator
            return 0
        #self.container.reset()
        listitems = []
        for listitem, moviesets in self.moviesets_db:
            if not xbmc.getCondVisibility( self.windowCond ):
                self.moviesets_db.close() # stop generator
                listitems = []
                break
            self.moviesets = moviesets
            #self.container.addItem( listitem )
            listitems.append( listitem )
            self.setContent()
            #self.setSaga()
        if listitems:
            self.container.reset()
            self.container.addItems( listitems )
        print "MovieSetsInfoScanner: Finished scan. Scanning for moviesets info took %.3fs" % ( time.time() - db_start_time )
        return self.container.size()

    def setSaga( self ):
        try:
            current_label = xbmc.getInfoLabel( "Container.ListItem.Label" )
            if current_label and current_label != xbmc.getInfoLabel( self.containerLabel ):
                newpos = self.moviesets.get( current_label, 0 ) or 0
                pos = self.container.getSelectedPosition()
                if ( newpos != pos and pos != -1 ):
                    self.container.selectItem( newpos )
                    #print "current_label %i %s" % ( newpos, current_label )
                    #print "container_label %i %s" % ( pos, xbmc.getInfoLabel( self.containerLabel ), )
                    #print "MovieSetsSelectItem: self.container.selectItem( %i )" % newpos
        except:
            xbmc.log( "MovieSets::Main:setSaga: %s" % repr( locals() ), xbmc.LOGERROR )
            print_exc()


class Backend( Thread ):
    def __init__( self, main, lock ):
        Thread.__init__( self, name="Thread-MovieSets" )
        self.lock = lock
        self.main = main
        self._stop = False
        self.last_mtime = 0

    def run( self ):
        try:
            self.lock.acquire()
            while not self._stop:
                if not xbmc.getCondVisibility( self.main.windowCond ):
                    self.stop()
                    break
                self.updates()
                time.sleep( .05 )
        except:
            xbmc.log( "MovieSets::Backend:run: %s" % repr( locals() ), xbmc.LOGERROR )
            print_exc()
            self.stop()

    def stop( self ):
        self.busy( True )
        self.main.window.clearProperty( "MovieSets.IsAlive" )
        self.main.window.clearProperty( "Content.MovieSets" )
        self._stop = True
        self.lock.release()
        print "MovieSetsBackend: Finished Thread. Running moviesets took %.3fs" % ( time.time() - START_TIME )

    def updates( self ):
        s1 = os.path.getmtime( "special://Database/MyVideos34.db" )
        if s1 > self.last_mtime:
            self.last_mtime = s1
            self.busy()
            if not self.main.setContainer(): return self.stop()
            self.busy( True )
            print "MovieSetsMyVideos_db: last modification is %s" % time.strftime( "%Y-%m-%d %H:%M:%S", time.localtime( s1 ) )
        self.main.setSaga()
        self.main.setContent()

    def busy( self, close=False ):
        if self.main.busydialog:
            if close: xbmc.executebuiltin( "Dialog.Close(busydialog)" )
            else: xbmc.executebuiltin( "ActivateWindow(busydialog)" )
