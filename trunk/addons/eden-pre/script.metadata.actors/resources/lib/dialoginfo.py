
# Modules General
from random import shuffle
from threading import Timer
from collections import deque
from traceback import print_exc

# Modules XBMC
import xbmc
import xbmcgui
import xbmcvfs
from xbmcaddon import Addon

# Modules Custom
import utils
import actorsdb
import tmdbAPI
import dialogs


# Constants
ADDON    = utils.ADDON
Language = utils.Language  # ADDON strings
LangXBMC = utils.LangXBMC  # XBMC strings
ACTORS   = utils.getXBMCActors()
TBN      = utils.Thumbnails()
CONTAINER_REFRESH     = False
RELOAD_ACTORS_BACKEND = False



class DialogSelect( xbmcgui.WindowXMLDialog ):
    def __init__( self, *args, **kwargs ):
        self.actor = {}
        self.add_plus = False
        self.main = kwargs.get( "main" )
        self.listing = kwargs.get( "listing" ) or []
        self.profile_path = self.main.config[ "base_url" ] + self.main.config[ "profile_sizes" ][ 2 ]

        self.refresh = kwargs[ "refresh" ]
        self.page = 1

        if self.main.actor_search.isdigit():
            self._add_actor( self.main.actor_search )
        else:
            self._search_person()

        # if not refresh and just one item, use this
        if not self.refresh and len( self.listing ) == 1:
            self._add_actor( self.listing[ 0 ][ "id" ] )

    def _search_person( self ):
        #first search person
        xbmc.executebuiltin( 'ActivateWindow(busydialog)' )
        js_search = tmdbAPI.search_person( self.main.actor_search, self.page )
        xbmc.executebuiltin( 'Dialog.Close(busydialog,true)' )
        self.listing += js_search[ "results" ]
        self.add_plus = js_search[ "results" ] and js_search[ "page" ] < js_search[ "total_pages" ]

    def _add_actor( self, ID ):
        # active busy
        xbmc.executebuiltin( 'ActivateWindow(busydialog)' )
        try:
            json_object = tmdbAPI.full_person_info( ID, ADDON.getSetting( "language" ).lower() )
            self.actor = {}
            if json_object:
                if self.main.actor_name:
                    json_object[ "name" ] = unicode( self.main.actor_name, 'utf-8', errors='ignore' )
                update_id = -1
                if str( self.main.actor.get( "id" ) ).isdigit():
                    update_id = int( self.main.actor[ "id" ] )
                #print repr( str( update_id ) )
                self.actor = actorsdb.save_actor( json_object, self.profile_path, update_id, TBN )
                globals().update( { "RELOAD_ACTORS_BACKEND": True } )
        except:
            print_exc()
        xbmc.executebuiltin( 'Dialog.Close(busydialog,true)' )

    def onInit( self ):
        if bool( self.actor ):
            self._close_dialog( 0 )
        try: self.getControl( 1 ).setLabel( Language( 32034 ) % unicode( self.main.actor_search, 'utf-8', errors='ignore' ) )
        except: self.getControl( 1 ).setLabel( 'Person results for "%s"' % self.main.actor_search )
        try:
            self.control_list = self.getControl( 6 )
            self.getControl( 3 ).setVisible( False )
            self.getControl( 5 ).controlUp( self.control_list )
        except:
            self.control_list = self.getControl( 3 )
            print_exc()
        try: self.getControl( 5 ).setLabel( LangXBMC( 413 ) )
        except: print_exc()

        if self.listing:
            try: self.setContainer()
            except: print_exc()
        elif not bool( self.actor ):
            try: self.onClick( 5 )
            except: print_exc()

    def setContainer( self, selectItem=0 ):
        listitems = []
        for actor in self.listing :
            label2 = ": ".join( [ Language( 32015 ), LangXBMC( ( 106, 107 )[ str( actor.get( "adult" ) ).lower() == "true" ] ) ] )
            listitem = xbmcgui.ListItem( actor[ "name" ], label2, "DefaultActor.png" )
            listitem.setProperty( "Addon.Summary", label2 )
            if actor[ "profile_path" ]:
                listitem.setIconImage( self.profile_path + actor[ "profile_path" ] )
            listitems.append( listitem )

        if self.add_plus:
            self.add_plus = False
            listitem = xbmcgui.ListItem( LangXBMC( 21452 ), "", "DefaultFolder.png" )
            listitem.setProperty( "nextpage", "true" )
            listitems.append( listitem )

        self.control_list.reset()
        self.control_list.addItems( listitems )
        self.control_list.selectItem( selectItem )
        self.setFocus( self.control_list )
        if not listitems:
            self.setFocusId( 5 )

    def onClick( self, controlID ):
        try:
            if controlID in [ 3, 6 ]:
                selected = self.control_list.getSelectedPosition()
                item = self.control_list.getSelectedItem()
                if item.getProperty( "nextpage" ) == "true":
                    self.page += 1
                    self._search_person()
                    self.setContainer( selected )

                else:
                    if selected > -1:
                        # get id for fetching info
                        try: ID = self.listing[ selected ][ "id" ]
                        except IndexError: pass
                        else:
                            self._add_actor( ID )
                            if bool( self.actor ):
                                self._close_dialog()

            elif controlID == 5:
                # show keyboard
                new_name = utils.keyboard( self.main.actor_search )
                if new_name and new_name != self.main.actor_search:
                    self.main.actor_search = new_name
                    self.page = 1
                    self.listing = []
                    if self.main.actor_search.isdigit():
                        self._add_actor( self.main.actor_search )
                        if bool( self.actor ):
                            self._close_dialog( 0 )
                            return
                    self._search_person()
                    self.setContainer()
        except:
            print_exc()

    def onFocus( self, controlID ):
        pass

    def onAction( self, action ):
        try:
            if self.getFocusId() == 0:
                if self.listing:
                    self.setFocus( self.control_list )
                else:
                    self.setFocusId( 5 )
        except:
            self.setFocus( self.control_list )
        if action in utils.CLOSE_SUB_DIALOG:
            self.actor = {}
            self._close_dialog()

    def _close_dialog( self, t=500 ):
        self.close()
        if t: xbmc.sleep( t )


def select( main, refresh=False ):
    xbmc.executebuiltin( "SetProperty(actorsselect,1)" )
    w = DialogSelect( "DialogSelect.xml", utils.ADDON_DIR, main=main, refresh=refresh )
    if not w.actor:
        w.doModal()
    actor = w.actor
    del w
    xbmc.executebuiltin( "ClearProperty(actorsselect)" )
    return actor


class ActorInfo( xbmcgui.WindowXMLDialog ):
    def __init__( self, *args, **kwargs ):
        self.tbn_added = False
        self.multiimage_thread = None
        # get configuration: images path and sizes
        self.config = tmdbAPI.configuration()
        # set our person image path
        self.profile_path = self.config[ "base_url" ] + self.config[ "profile_sizes" ][ 2 ]
        # set our movie image path
        self.poster_path  = self.config[ "base_url" ] + self.config[ "poster_sizes" ][ 2 ]

        self.videodb = kwargs.get( "videodb" )
        # set our person name
        self.actor_name = kwargs.get( "actor_name" ) or ""

        # fix name if called from dialogvideoinfo.xml actor and role
        _as_ = " %s " % LangXBMC( 20347 )
        try: actor, role = self.actor_name.split( _as_.encode( "utf-8" ) )
        except:
            try: actor, role = self.actor_name.split( _as_ )
            except:
                _as_ = utils.re.search( "(.*?)%s(.*?)" % _as_, self.actor_name )
                if _as_: actor, role = _as_.groups()
                else: actor, role = "", ""
        #xbmcgui.Dialog().ok( LangXBMC( 20347 ), actor, role )
        self.actor_name = actor or self.actor_name

        # if not name, show keyboard
        self.actor_search = self.actor_name or utils.select_actor_from_xbmc( ACTORS )
        # Manque un actor_search = "manual"
        if self.actor_search == "manual":
            self.actor_search = utils.keyboard()
        self.actor_search = self.actor_search

        # if not again name, call error
        if not self.actor_search:
            raise Exception( "No search person: Canceled..." )

        # search in database
        con, cur = actorsdb.getConnection()
        if self.actor_search.isdigit():
            self.actor = actorsdb.getActor( cur, idTMDB=self.actor_search )
        else:
            self.actor = actorsdb.getActor( cur, strActor=self.actor_search )
        con.close()
        OK = bool( self.actor )

        if not OK:
            # if not actor, select choices
            self.actor = select( self )
            OK = bool( self.actor )

        # if not again name, call error
        if not OK:
            raise Exception( "No search person name %r" % self.actor_search )

        self.timeperimage = int( float( ADDON.getSetting( "timeperimage" ) ) )

    def copyThumb( self, tbn2="", ignore_errors=0, force=False ):
        ok = False
        try:
            tbn1 = "".join( TBN.get_thumb( self.actor[ "name" ] ) )
            tbn2 = tbn2 or TBN.BASE_THUMB_PATH + self.actor[ "thumbs" ][ 0 ]
            force = force or ( not xbmcvfs.exists( tbn1 ) )
            if tbn1 and force and xbmcvfs.exists( tbn2 ):
                ok = xbmcvfs.copy( tbn2, tbn1 )
                print "%r xbmcvfs.copy( %r, %r )" % ( ok, tbn2, tbn1 )
        except:
            if not ignore_errors:
                print_exc()
        if ok: globals().update( { "CONTAINER_REFRESH": True } )
        return ok

    def onInit( self ):
        xbmc.executebuiltin( "ClearProperty(actorsselect)" )
        self.setContainer()

    def multiimage( self ):
        try:
            self.listitem.setIconImage( self.profile_path + self.multiimages[ 0 ] )
            self.multiimages.rotate( -1 )

            self._stop_multiimage_thread()
            self.multiimage_thread = Timer( self.timeperimage, self.multiimage, () )
            self.multiimage_thread.start()
        except:
            print_exc()

    def _stop_multiimage_thread( self ):
        try: self.multiimage_thread.cancel()
        except: pass

    def setContainer( self, refresh=False ):
        try:
            self.videodb = utils.getActorPaths( self.actor[ "name" ], ACTORS )
            self.getControl( 8 ).setEnabled( bool( self.videodb ) )

            # actor key: ( "idactor", "id", "name", "biography", "biooutline", "birthday", "deathday", "place_of_birth", "also_known_as", "homepage", "adult", "cachedthumb" )
            # actor.thumbs list: [ cachedUrl, strUrl, strThumb=json_string ]
            # actor.castandcrew list: [ strCast=json_string, strCrew=json_string ]

            self.actor[ "castandcrew" ] = map( utils.load_db_json_string, self.actor[ "castandcrew" ] )
            try: self.images = utils.load_db_json_string( self.actor[ "thumbs" ][ 2 ] )
            except: self.images = []
            # Shuffle items in place
            if ADDON.getSetting( "randomize" ) == "true": shuffle( self.images )
            self.multiimages = deque( a[ "file_path" ] for a in self.images )
            try: self.timeperimage = int( ADDON.getSetting( "timeperimage" ) )
            except: self.timeperimage = 10

            listitem = xbmcgui.ListItem( self.actor[ "name" ], "", "DefaultActor.png" )
            for fanart in TBN.get_fanarts( self.actor[ "name" ] ):
                if xbmcvfs.exists( fanart ):
                    listitem.setProperty( "Fanart_Image", fanart )
                    break

            cached_actor_thumb = "special://thumbnails/Actors/" + self.actor[ "name" ] + "/"
            for extra in [ "extrafanart", "extrathumb" ]:
                if xbmcvfs.exists( cached_actor_thumb + extra ):
                    listitem.setProperty( extra, cached_actor_thumb + extra )

            self.tbn_added = False
            if self.actor[ "thumbs" ]:
                icon = self.actor[ "thumbs" ][ 1 ]
                if icon:
                    listitem.setIconImage( self.profile_path + icon )
                    self.tbn_added = True
                    self.copyThumb()

                if ADDON.getSetting( "usemultiimage" ) == "true" and len( self.multiimages ) > 1:
                    # active multiimage thread
                    self.multiimage_thread = Timer( self.timeperimage, self.multiimage, () )
                    self.multiimage_thread.start()
                    self.tbn_added = True

            if not self.tbn_added:
                cachedthumb = "".join( TBN.get_thumb( self.actor[ "name" ] ) )
                if xbmcvfs.exists( cachedthumb ): listitem.setIconImage( cachedthumb )

            self.actor[ "biography" ] = utils.clean_bio( self.actor[ "biography" ] or "" )
            listitem.setProperty( "Biography",    self.actor[ "biography" ] )
            listitem.setProperty( "Biooutline",   self.actor[ "biooutline" ] or "" )
            listitem.setProperty( "Homepage",     self.actor[ "homepage" ]   or "" )
            listitem.setProperty( "PlaceOfBirth", self.actor[ "place_of_birth" ] or "" )
            listitem.setProperty( "AlsoKnownAs",  self.actor[ "also_known_as" ]  or "" )

            if int( ADDON.getSetting( "showlabeladult" ) ):
                adult = LangXBMC( ( 106, 107 )[ str( self.actor[ "adult" ] ).lower() == "true" ] )
                if int( ADDON.getSetting( "showlabeladult" ) ) == 2 and adult == LangXBMC( 106 ): adult = ""
                listitem.setProperty( "Adult", adult )

            format = ( "datelong", "dateshort" )[ int( ADDON.getSetting( "datelongshort" ) ) ]
            birthday = utils.get_user_date_format( ( self.actor[ "birthday" ] or "" ), format )
            deathday = utils.get_user_date_format( ( self.actor[ "deathday" ] or "" ), format )
            format = ( "long", "short" )[ ADDON.getSetting( "fulldatelong" ) == "false" ]
            listitem.setProperty( "Birthday",     utils.translate_date( birthday, format ) )
            listitem.setProperty( "Deathday",     utils.translate_date( deathday, format ) )

            actuel_age, dead_age, dead_since = utils.get_ages( self.actor[ "birthday" ], self.actor[ "deathday" ] )
            listitem.setProperty( "Age",          actuel_age )
            listitem.setProperty( "Deathage",     dead_age )
            listitem.setProperty( "AgeLong",      "" )
            listitem.setProperty( "DeathageLong", "" )
            if actuel_age: listitem.setProperty( "AgeLong",      Language( 32020 ) % actuel_age )
            if dead_since: listitem.setProperty( "DeathageLong", Language( 32021 ) % dead_since )
            elif dead_age: listitem.setProperty( "DeathageLong", Language( 32020 ) % dead_age )

            listitem.setInfo( "video", { "title": self.actor[ "name" ], "plot": self.actor[ "biography" ] } )

            self.listitem = listitem
            self.clearList()
            self.addItem( self.listitem )
            self.getControl( 50 ).setVisible( 0 )

            movies_id = self.setContainer150()
            self.setContainer250()

            if refresh:
                # del trailer id's
                trailers = utils.load_trailers()
                for id in movies_id:
                    if trailers.get( str( id ) ):
                        del trailers[ str( id ) ]
                f = xbmc.translatePath( utils.ADDON_DATA + "trailers.json" )
                file( f, "w" ).write( utils.json.dumps( trailers ) )
        except:
            print_exc()
            self._close_dialog()
        xbmc.executebuiltin( "ClearProperty(actorsselect)" )

    def setContainer150( self ):
        movies_id = []
        try:
            self.getControl( 150 ).reset()
            self.getControl( 150 ).setVisible( 0 )
            keeporiginaltitle = ( ADDON.getSetting( "keeporiginaltitle" ) == "true" )
            listitems = []
            pretty_movie = {}
            non_dated = {}
            movies_library = utils.get_movies_library()
            for movie in self.actor[ "castandcrew" ][ 0 ] + self.actor[ "castandcrew" ][ 1 ]:
                if movie[ "id" ] not in movies_id: movies_id.append( movie[ "id" ] )
                year = str( movie[ "release_date" ] or "0" )[ :4 ]
                dict = ( pretty_movie, non_dated )[ year == "0" ]
                m = dict.get( movie[ "id" ] ) or [ "", "", [], [] ]

                title = ( movie[ "title" ], movie[ "original_title" ] )[ keeporiginaltitle ]
                m[ 0 ] = " ".join( [ unicode( year ), "  ", title ] )
                if movie.get( "character" ): m[ 2 ].append( movie[ "character" ] )
                if movie.get( "job" ):       m[ 3 ].append( movie[ "job" ] )
                if movie[ "poster_path" ]:   m[ 1 ] = self.poster_path + movie[ "poster_path" ]
                #
                m.append( utils.library_has_movie( movies_library, movie[ "title" ], movie[ "original_title" ] ) )
                #
                dict[ movie[ "id" ] ] = m

            movies = sorted( pretty_movie.items(), key=lambda x: x[ 1 ][ 0 ], reverse=True ) + sorted( non_dated.items(), key=lambda x: x[ 1 ][ 0 ] )
            for id, movie in movies:
                label = movie[ 0 ]
                year, title = label.split( "    ", 1 )
                if label.startswith( "0" ):
                    label = label.replace( "0", "?", 1 )
                if movie[ 2 ] or movie[ 3 ]:
                    label += "    [" + unicode( " / ".join( sorted( movie[ 2 ] ) + sorted( movie[ 3 ] ) )  ) + "]"
                li = xbmcgui.ListItem( label, "", "DefaultMovies.png" )
                if movie[ 1 ]: li.setIconImage( movie[ 1 ] )
                li.setProperty( "id", str( id ) )
                if movie[ 4 ]:
                    li.setProperty( "LibraryHasMovie", "1" )
                    li.setProperty( "PlayCount", str( movie[ 4 ].get( "playcount" ) or "0" ) )
                    li.setProperty( "file", movie[ 4 ].get( "file" ) or "" )
                li.setInfo( "video", { "title": title, "year": int( year ) } )
                listitems.append( li )
            self.getControl( 150 ).addItems( listitems )
        except:
            print_exc()
            self.getControl( 5 ).setEnabled( 0 )

        self.listitem.setProperty( "TotalMovies",  str( len( movies_id ) ) )
        self.getControl( 5 ).setEnabled( bool( movies_id ) )
        self.getControl( 5 ).setLabel( Language( 32010 ) )

        return movies_id

    def setContainer250( self ):
        try:
            listitems = []
            for img in self.images:
                label = "%ix%i" % ( img[ "width" ], img[ "height" ], )
                li = xbmcgui.ListItem( label, "", self.profile_path + img[ "file_path" ] )
                li.setProperty( "aspect_ratio", "%.2f" % img[ "aspect_ratio" ] )
                listitems.append( li )
            self.getControl( 250 ).reset()
            self.getControl( 250 ).addItems( listitems )
        except:
            print_exc()
        # set icon or fanart
        #self.getControl( 20 ).setEnabled( 0 )
        #self.getControl( 10 ).setEnabled( bool( self.images ) )

    def onFocus( self, controlID ):
        pass

    def getLabelSize( self, w, h, to ):
        if   to[ 0 ] == "h": size = "%ix%s" % ( round( int( w ) * int( to[ 1: ] ) / int( h ) ), to[ 1: ] )
        elif to[ 0 ] == "w": size = "%sx%i" % ( to[ 1: ], round( int( h ) * int( to[ 1: ] ) / int( w ) ) )
        else: size = w + "x" + h
        return "%s  (%s)" % ( to.title(), size )

    def onClick( self, controlID ):
        try:
            if controlID == 250:
                icon = xbmc.getInfoLabel( "Container(250).ListItem.Icon" )
                w, h = xbmc.getInfoLabel( "Container(250).ListItem.Label" ).split( "x" )
                choices = [ self.getLabelSize( w, h, to ) for to in self.config[ "profile_sizes" ][ ::-1 ] ] + [ LangXBMC( 21452 ), LangXBMC( 222 ) ]
                selected = xbmcgui.Dialog().select( Language( 32040 ), choices )
                if selected > -1:
                    if choices[ selected ] == LangXBMC( 21452 ):
                        #browse thumb
                        if dialogs.browser( search_name=self.actor_search, type="thumb" ):
                            globals().update( { "CONTAINER_REFRESH": True } )
                            self.setContainer()

                    elif choices[ selected ] != LangXBMC( 222 ):
                        icon = icon.split( "/" )
                        icon[ icon.index( self.config[ "profile_sizes" ][ 2 ] ) ] = self.config[ "profile_sizes" ][ ::-1 ][ selected ]
                        new_icon = tmdbAPI.download( "/".join( icon ), xbmc.translatePath( "special://temp" ) )
                        ok = False
                        if new_icon:
                            ok = self.copyThumb( new_icon, force=True )
                            if not ok:
                                import shutil
                                try: shutil.copy( new_icon, xbmc.translatePath( "".join( TBN.get_thumb( self.actor[ "name" ] ) ) ) )
                                except: pass
                                else: ok = True
                                del shutil
                        if ok:
                            self.tbn_added = False
                            msg = Language( 32041 )
                            globals().update( { "CONTAINER_REFRESH": True } )
                        else:
                            msg = Language( 32042 )
                        xbmcgui.Dialog().ok( xbmc.getInfoLabel( "ListItem.Title" ), msg )

            elif controlID == 150:
                listitem = self.getControl( 150 ).getSelectedItem()
                movie_id = listitem.getProperty( "id" )
                if not movie_id: return
                LibraryHasMovie = listitem.getProperty( "LibraryHasMovie" ) == "1"

                listitem.select( 1 )
                buttons = [ Language( 32051 ), LangXBMC( 13346 ), Language( 32050 ) ]
                if LibraryHasMovie: buttons.insert( 0, LangXBMC( 208 ) )
                selected = dialogs.contextmenu( buttons )
                listitem.select( 0 )

                if selected == 0 and LibraryHasMovie:
                    file = listitem.getProperty( "file" )
                    if file: xbmc.executebuiltin( "PlayMedia(%s)" % file )
                    return

                if LibraryHasMovie:
                    selected -= 1

                if selected == 0:
                    trailers = utils.load_trailers()
                    if trailers.get( movie_id ):
                        trailers, lang = trailers[ movie_id ]
                    else:
                        xbmc.executebuiltin( 'ActivateWindow(busydialog)' )
                        trailers, lang = tmdbAPI.get_movie_trailers( movie_id, ADDON.getSetting( "language" ).lower() )
                        utils.save_trailers( trailers, lang )
                        xbmc.executebuiltin( 'Dialog.Close(busydialog,true)' )

                    trailers = trailers.get( "youtube" )
                    if trailers:
                        selected = -1
                        if len( trailers ) == 1: selected = 0
                        else: selected = xbmcgui.Dialog().select( "%s [%s]" % ( Language( 32051 ), lang.upper() ), [ "%s (%s)" % ( trailer[ "name" ], trailer[ "size" ] ) for trailer in trailers ] )
                        if selected > -1:
                            url = "plugin://plugin.video.youtube/?action=play_video&videoid=%s" % trailers[ selected ][ "source" ]
                            self._close_dialog()
                            xbmc.executebuiltin( "ClearProperty(script.metadata.actors.isactive)" )
                            xbmc.executebuiltin( 'Dialog.Close(all,true)' )
                            xbmc.Player().play( url, listitem )
                    else:
                        #no trailers found
                        utils.notification( listitem.getLabel(), Language( 32052 ).encode( "utf-8" ) )

                elif selected == 1:
                    xbmcgui.Dialog().ok( utils.ADDON.getAddonInfo( "name" ), "Coming Soon!" )

                elif selected == 2:
                    import webbrowser
                    url = "http://www.themoviedb.org/movie/%s?language=%s" % ( movie_id, ADDON.getSetting( "language" ).lower() )
                    webbrowser.open( url )
                    del webbrowser

            elif controlID == 5:
                # toggle button Filmography/Biography
                if self.getControl( 5 ).getLabel() == LangXBMC( 21887 ):
                    label, visible = Language( 32010 ), 0
                else:
                    label, visible = LangXBMC( 21887 ), 1
                self.getControl( 5 ).setLabel( label )
                self.getControl( 150 ).setVisible( visible )

            elif controlID == 6:
                # refresh button
                actor = select( self, True )
                if actor:
                    self.actor = actor
                    self.setContainer( True )

            elif controlID == 8:
                # show user movies acting, tvshows acting, movies directing, discography
                if self.videodb:
                    if len( self.videodb ) == 1:
                        selected = 0
                    else:
                        selected = xbmcgui.Dialog().select( self.actor[ "name" ], [ i[ 0 ] for i in self.videodb ] )

                    if selected > -1:
                        path_db = self.videodb[ selected ][ 1 ]
                        if utils.LIBRARY_TYPE:
                            command = "Container.Update(%s,replace)" % path_db
                        else:
                            window = ( "Videos", "MusicLibrary" ) [ "musicdb" in path_db ]
                            command = "ActivateWindow(%s,%s,return)" % ( window, path_db )
                        self._close_dialog()
                        xbmc.executebuiltin( command )

            elif controlID == 11:
                #  edit profile from site
                if xbmcgui.Dialog().yesno( "themoviedb.org", Language( 32035 ), Language( 32036 ), "", LangXBMC( 222 ), LangXBMC( 21435 ).strip( "- " ) ):
                    import webbrowser
                    webbrowser.open( "http://www.themoviedb.org/person/%i" % self.actor[ "id" ] )
                    del webbrowser

            elif controlID in [ 10, 20 ]:
                #browse fanart or thumb
                type = ( "thumb", "fanart" )[ controlID == 20 ]
                if type == "thumb" and self.getControl( 250 ).size():
                    self.setFocusId( 250 )

                elif dialogs.browser( search_name=self.actor_search, type=type ):
                    globals().update( { "CONTAINER_REFRESH": True } )
                    self.setContainer()

            elif controlID == 25:
                # show addon settings
                self._close_dialog()
                ADDON.openSettings()
                from sys import argv
                xbmc.executebuiltin( 'RunScript(%s)' % ",".join( argv ) )
        except:
            print_exc()

    def onAction( self, action ):
        if action == utils.ACTION_CONTEXT_MENU and xbmc.getCondVisibility( "Control.HasFocus(150)" ):
            try: self.onClick( 150 )
            except: pass

        elif action in utils.CLOSE_DIALOG:
            self._close_dialog()

    def _close_dialog( self ):
        self._stop_multiimage_thread()
        if self.tbn_added:
            self.copyThumb( ignore_errors=1 )
        xbmc.executebuiltin( "ClearProperty(actorsselect)" )
        self.close()
        xbmc.sleep( 500 )


def Main( actor_name="" ):
    w = ActorInfo( "script-Actors-DialogInfo.xml", utils.ADDON_DIR, actor_name=actor_name )
    w.doModal()
    #a = w.actor
    del w

    if CONTAINER_REFRESH:
        if xbmc.getCondVisibility( "![Window.IsVisible(movieinformation) | Window.IsVisible(musicinformation)]" ):
            xbmc.executebuiltin( "ClearProperty(script.metadata.actors.isactive)" )
            xbmc.executebuiltin( 'Container.Refresh' )

    if RELOAD_ACTORS_BACKEND or CONTAINER_REFRESH:
        # send message to backend for reload actors
        xbmcgui.Window( 10025 ).setProperty( "reload.actors.backend", "1" )


if __name__=="__main__":
    Main()
