
#Modules General
import time
import threading
from traceback import print_exc

import xbmc
import xbmcgui

# Modules Custom
import utils
from actorsdb import get_actors_for_backend


STR_AGE_LONG       = utils.Language( 32020 )
STR_DEAD_SINCE     = utils.Language( 32021 )
STR_DEATH_AGE_LONG = utils.Language( 32020 )
TBN                = utils.Thumbnails()




class Backend( threading.Thread ):
    def __init__( self ):
        threading.Thread.__init__( self )
        self._stop = False
        self.current_actor = None
        # get actors from actors1.db
        self.get_actors()
        # start thread
        self.start()

    def get_actors( self ):
        self.ACTORS = get_actors_for_backend()
        xbmcgui.Window( 10025 ).clearProperty( "reload.actors.backend" )

    def clearProperties( self ):
        window = xbmcgui.Window( 10025 )
        for prt in [ "name", "biography", "biooutline", "birthday", "deathday", "placeofbirth", "alsoknownas", "homepage", "adult", "age", "deathage", "agelong", "deathagelong", "fanart", "icon" ]:
            window.clearProperty( "current.actor." + prt )

    def run( self ):
        try:
            while not self._stop:
                if not xbmc.getCondVisibility( "Window.IsVisible(10025)" ): self.stop()      #destroy threading

                # actor/director/writer
                if xbmc.getCondVisibility( "SubString(Container.FolderPath,videodb://1/4/) | SubString(Container.FolderPath,videodb://1/5/) | SubString(Container.FolderPath,videodb://2/4/)" ):

                    if xbmcgui.Window( 10025 ).getProperty( "reload.actors.backend" ) == "1": self.get_actors()
                    temp_actor = self.ACTORS.get( unicode( xbmc.getInfoLabel( "ListItem.Label" ), "utf-8" ) )
                    if temp_actor != self.current_actor:
                        self.current_actor = temp_actor
                        self.clearProperties()
                        #
                        if self.current_actor:
                            #( "idactor", "id", "name", "biography", "biooutline", "birthday", "deathday", "placeofbirth", "alsoknownas", "homepage", "adult", "cachedthumb" )
                            window = xbmcgui.Window( 10025 )
                            window.setProperty( "current.actor.name",         self.current_actor[ 2 ]  or "" )
                            window.setProperty( "current.actor.biography",    utils.clean_bio( self.current_actor[ 3 ] or "" ) )
                            window.setProperty( "current.actor.biooutline",   self.current_actor[ 4 ]  or "" )
                            window.setProperty( "current.actor.birthday",     self.current_actor[ 5 ]  or "" )
                            window.setProperty( "current.actor.deathday",     self.current_actor[ 6 ]  or "" )
                            window.setProperty( "current.actor.placeofbirth", self.current_actor[ 7 ]  or "" )
                            window.setProperty( "current.actor.alsoknownas",  self.current_actor[ 8 ]  or "" )
                            window.setProperty( "current.actor.homepage",     self.current_actor[ 9 ]  or "" )
                            window.setProperty( "current.actor.adult",        self.current_actor[ 10 ] or "" )

                            actuel_age, dead_age, dead_since = utils.get_ages( self.current_actor[ 5 ], self.current_actor[ 6 ] )
                            window.setProperty( "current.actor.age",      actuel_age )
                            window.setProperty( "current.actor.deathage", dead_age )
                            if actuel_age: window.setProperty( "current.actor.agelong",      STR_AGE_LONG % actuel_age )
                            if dead_since: window.setProperty( "current.actor.deathagelong", STR_DEAD_SINCE % dead_since )
                            elif dead_age: window.setProperty( "current.actor.deathagelong", STR_DEATH_AGE_LONG % dead_age )

                            fanart = TBN.get_fanarts( self.current_actor[ 2 ] )[ 0 ]
                            window.setProperty( "current.actor.fanart", fanart )
                            icon = "".join( TBN.get_thumb( self.current_actor[ 2 ] ) )
                            window.setProperty( "current.actor.icon",   icon )

                time.sleep( .3 )
        except SystemExit:
            print "SystemExit!"
            self.stop()
        except:
            print_exc()
            self.stop()

    def stop( self ):
        self.clearProperties()
        self._stop = True


Backend()
