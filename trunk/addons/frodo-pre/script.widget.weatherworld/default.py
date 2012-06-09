
import sys
import time
import random
from threading import Timer
from traceback import print_exc
from datetime import datetime, timedelta

import xbmc
import xbmcgui
import xbmcvfs

import weatherworld
from geometry import Rect

LangXBMC = xbmc.getLocalizedString  # XBMC strings
USER_TIME_FORMAT = xbmc.getRegion( "time" ).replace( ':%S', '', 1 )

DAY_ID_SHORT = {
    "mon": 41,
    "tue": 42,
    "wed": 43,
    "thu": 44,
    "fri": 45,
    "sat": 46,
    "sun": 47,
    }

def translate_day( str_day ):
    id = DAY_ID_SHORT.get( str_day.lower() )
    if id: str_day = LangXBMC( id ) or str_day
    return str_day


def time_took( t ):
    t = ( time.time() - t )
    return str( timedelta( seconds=t ) ).split( "." )[ 0 ]


def fahrenheit2celsius( F, unit ):
    celsius, unit = F, unit
    if unit[ -1 ].lower() == "f":
        try: celsius, unit = str( ( int( F ) - 32 ) * 5 / 9 ), "°C"
        except: celsius, unit = F, unit
    return celsius, unit


def trim_time( str_time ):
    if str_time.startswith( "0" ):
        str_time = str_time[ 1: ]
    return str_time


def get_user_time_format( str_time="5:31 PM" ):
    #f_time = time()
    str_day, str_time = str_time.split( " ", 1 )
    try:
        str_dt = str_time.lower().replace( "-", "" ).replace( "<br>", "" ).split()
        if str_dt[ -1 ] not in [ "pm", "am" ]:
            T, P = str_dt + [ "" ]
        else:
            T, P = str_dt
        if T.count( ":" ) == 1:
            H, M = T.split( ":" )
        else:
            H, M, S = T.split( ":" )

        dt = datetime.now()
        dt = dt.replace( hour=int( H ), minute=int( M ), second=0, microsecond=0 )

        hour = ( dt.hour, dt.hour+12 )[ P == "pm" ]
        hour = ( hour, dt.hour-12 )[ P == "am" ]
        try: dt = dt.replace( hour=hour )
        except ValueError: pass

        #17:31
        str_time = dt.strftime( USER_TIME_FORMAT )
        #convert a datetime object into a Unix time stamp
        #f_time = mktime( dt.timetuple() ) + 1e-6 * dt.microsecond
    except:
        if str_time:
            print "str_time: %r" % str_time
            print_exc()
    return translate_day( str_day ) + " " + trim_time( str_time )


class WeatherWorld:
    def __init__( self ):
        self._thread = None
        self.listimages = {}
        self.listicons  = {}
        self.remove_cities = []
        self._stop = xbmc.abortRequested
        if not self._stop:
            self.setParams()
            self.run()

    def setParams( self ):
        params = {}
        # parse argv (time, limit, mapsize, tilesize, window, condition)
        try: params = dict( [ arg.split( "=" ) for arg in sys.argv[ 1 ].replace( "&amp;", "&" ).split( "&" ) ] )
        except: print "Error to parse argv: %r" % repr( sys.argv )

        self.colorDiffuse = params.get( "citycolordiffuse" ) or "FFFFFFFF"
        self.wait    = int( params.get( "time" )   or "10" )
        self.LIMIT   = int( params.get( "limit" )  or "6" )
        self.winID   = int( params.get( "window" ) ) #or "10000"
        self.subCond = params.get( "condition" )   or "Window.IsVisible(%i)" % self.winID

        self.stopCond = "!Window.IsVisible(%i)" % self.winID # | System.IdleTime(7200)"
        self.window  = xbmcgui.Window( self.winID )
        windowback = params.get( "windowback" )
        if windowback: self.windowback = xbmcgui.Window( int( windowback ) )
        else: self.windowback = self.window
        #
        self.getControls()
        #
        mapwidth, mapheight   = ( params.get( "mapsize" ) or "1280x720" ).split( "x" )
        tilewidth, tileheight = ( params.get( "tilesize" ) or "360x60" ).split( "x" )
        self.mapwidth   = int( mapwidth )
        self.mapheight  = int( mapheight )
        self.tilewidth  = int( tilewidth )
        self.tileheight = int( tileheight )

    def getControls( self ):
        self.controls = {}
        for id in range( 1, self.LIMIT+1 ):
            try: control =  self.window.getControl( 2600 + id )
            except: control = None
            self.controls[ 2600 + id ] = control

    def run( self ):
        try:
            START_TIME = time.time()
            self.window.setProperty( "runningtime", time_took( START_TIME ) )
            self.getCities()
            self.setCities()

            while not self._stop:
                self._stop = xbmc.abortRequested
                if xbmc.getCondVisibility( self.stopCond ):
                    self.stop()

                if xbmc.getCondVisibility( "StringCompare(Window.Property(refreshcities),1)" ):
                    self.window.setProperty( "refreshcities", "" )
                    START_TIME = time.time()
                    self.refresh()

                if not self._thread and xbmc.getCondVisibility( self.subCond ):
                    self._thread = Timer( self.wait, self.setCities, () )
                    self._thread.start()

                time.sleep( .25 )
                self.window.setProperty( "runningtime", time_took( START_TIME ) )
        except SystemExit:
            print "SystemExit!"
            self.stop()
        except:
            print_exc()
        self.stop()

    def refresh( self ):
        weatherworld.save_cities( [] )
        self._stop_thread()
        self.getCities()
        self.setCities()

    def _stop_thread( self ):
        try: self._thread.cancel()
        except: pass
        self._thread = None

    def stop( self ):
        self._stop_thread()
        self._stop = True

    def getPosition( self, lat, long, width, height ):
        # set our pos y
        height = height / 2.0
        y = str( lat * height / 90 ).strip( "-" )
        if lat > 0: y = height - float( y )
        else: y = height + float( y )
        # set our pos x
        width = width / 2.0
        x = str( long * width / 180 ).strip( "-" )
        if long < 0: x = width - float( x )
        else: x = width + float( x )
        # return values
        return int( x ), int( y )

    def setCityProperty( self, id, city, tiles=[] ):
        self._stop = xbmc.abortRequested
        if self._stop: return
        #[u'city', u'outlook', u'temp', u'url', u'country', u'coords', u'time', u'unit', u'icon']
        ok = False
        try:
            b_prop = "weatherworld.city.%i." % id

            lat  = float( city[ "coords" ][ "lat" ][ 1 ] )
            long = float( city[ "coords" ][ "long" ][ 1 ] )
            posx, posy = self.getPosition( lat, long, self.mapwidth, self.mapheight )

            rect = Rect( posx, posy, self.tilewidth, self.tileheight )
            flipx, flipy = 0, 0
            offsetx, offsety = 0, 0
            if rect.right > self.mapwidth:   flipx, offsetx = 1, -self.tilewidth
            if rect.bottom > self.mapheight: flipy, offsety = 1, -self.tileheight
            if offsetx or offsety: rect.move( posx+offsetx, posy+offsety )

            collide = False
            for tile in tiles:
                collide = rect.colliderect( tile ) is not None
                if collide: break
            if collide:
                self.window.setProperty( b_prop + "name", "" )
                return ok, tiles

            tiles.append( rect )
            self.window.setProperty( b_prop + "flipx", str( flipx ) )
            self.window.setProperty( b_prop + "flipy", str( flipy ) )

            try: localtime = get_user_time_format( city[ "time" ] )
            except: localtime = city[ "time" ]

            self.window.setProperty( b_prop + "name",        city[ "city" ] + ", " + city[ "country" ] )
            self.window.setProperty( b_prop + "outlook",     city[ "outlook" ] )

            celsius, unit = fahrenheit2celsius( city[ "temp" ], city[ "unit" ] )
            self.window.setProperty( b_prop + "temperature", celsius )
            self.window.setProperty( b_prop + "unit",        unit )

            self.window.setProperty( b_prop + "localtime",   localtime )
            self.window.setProperty( b_prop + "icon",        city[ "icon" ] )
            self.window.setProperty( b_prop + "latitude",    city[ "coords" ][ "lat" ][ 0 ] )
            self.window.setProperty( b_prop + "longitude",   city[ "coords" ][ "long" ][ 0 ] )

            # get old pos
            oldx, oldy = self.window.getProperty( b_prop + "posx" ), self.window.getProperty( b_prop + "posy" )
            self.window.setProperty( b_prop + "posx",        str( posx ) )
            self.window.setProperty( b_prop + "posy",        str( posy ) )
            start = "0,0"
            if oldx.isdigit() and oldy.isdigit():
                start = "%s,%s" % ( oldx, oldy )

            control = self.controls[ 2600 + id ]
            if control:
                control.setAnimations( [ ( 'conditional', 'condition=true effect=slide start=%s end=%i,%i time=500 easing=inout tween=easing' % ( start, posx, posy ) ) ] )

                ok = True
        except:
            ok = "error"
            print_exc()
        return ok, tiles

    def getCities( self ):
        self.cities = weatherworld.load_cities()
        self.addCitiesPosition( self.cities )

    def setCities( self ):
        self._stop = xbmc.abortRequested
        if self._stop:
            self._stop_thread()
            return
        self.removeCities()
        if not self.cities:
            self.getCities()
        self.window.setProperty( "totals", str( len( self.cities ) ) )
        cities2 = sorted( self.cities )

        count = 0
        tiles = []
        while count < self.LIMIT and not self._stop:
            self._stop = xbmc.abortRequested
            if not cities2: break

            city = random.choice( cities2 )
            if self.controls[ 2600 + count + 1 ] is None:
                count += 1
                continue
            cities2.remove( city )

            ok, tiles = self.setCityProperty( ( count + 1 ), city, tiles )
            if ok == "error":
                self.remove_cities.append( city )
            elif ok:
                self.remove_cities.append( city )
                count += 1
            #print ( count, len( cities2 ) )

        self._stop = xbmc.abortRequested
        if count < self.LIMIT and not self._stop:
            for id in range( count+1, self.LIMIT+1 ):
                self.window.setProperty( "weatherworld.city.%i.name" % id, "" )

        self._stop = xbmc.abortRequested
        self._stop_thread()

    def removeCities( self ):
        if self.remove_cities:
            for rem in self.remove_cities:
                try: self.cities.remove( rem )
                except: pass
                if self.listimages:
                    try:
                        imgId = rem[ "coords" ][ "lat" ][ 1 ] + rem[ "coords" ][ "long" ][ 1 ]
                        image = self.listimages.pop( imgId )
                        if image: self.windowback.removeControl( image )
                        icon = self.listicons.pop( imgId )
                        if icon: self.windowback.removeControl( icon )
                    except:
                        pass
            weatherworld.save_cities( self.cities )
        self.remove_cities = []

    def addCitiesPosition( self, cities ):
        oldimages = self.listimages.values()
        if oldimages:
            try: self.windowback.removeControls( oldimages )
            except:
                for image in oldimages:
                    try: self.windowback.removeControl( image )
                    except: pass
        oldicons = self.listicons.values()
        if oldicons:
            try: self.windowback.removeControls( oldicons )
            except:
                for icon in oldicons:
                    try: self.windowback.removeControl( icon )
                    except: pass


        self.listimages = {}
        self.listicons  = {}
        showcities = xbmc.getCondVisibility( "StringCompare(Window.Property(showcitieslayout),1)" )
        if showcities:
            rects = {}
            for city in cities:
                try:
                    lat, long = city[ "coords" ][ "lat" ][ 1 ], city[ "coords" ][ "long" ][ 1 ]
                    posx, posy = self.getPosition( float( lat ), float( long ), self.mapwidth, self.mapheight )
                    self.listimages[ lat+long ] = xbmcgui.ControlImage( posx-4, posy-4, 8, 8, "radiobutton-focus.png", colorDiffuse="0x"+self.colorDiffuse )

                    layout = ( posx-10, posy-10, 20, 20 )
                    rect = Rect( *layout )
                    if not rect.collidedictall( rects ):
                        self.listicons[ lat+long ] = xbmcgui.ControlImage( *layout, filename=city[ "icon" ] )
                        rects[ lat+long ] = rect
                except:
                    pass


        if self.listicons:
            icons = self.listicons.values()
            try:
                self.windowback.addControls( icons )
                for icon in icons:
                    icon.setVisibleCondition( "StringCompare(Window.Property(showcitiesicons),1)" )
            except:
                for icon in icons:
                    try:
                        self.windowback.addControl( icons )
                        icon.setVisibleCondition( "StringCompare(Window.Property(showcitiesicons),1)" )
                    except: pass
        if self.listimages:
            images = self.listimages.values()
            try:
                self.windowback.addControls( images )
                for image in images:
                    image.setVisibleCondition( "StringCompare(Window.Property(showcities),1)" )
            except:
                for image in images:
                    try:
                        self.windowback.addControl( image )
                        image.setVisibleCondition( "StringCompare(Window.Property(showcities),1)" )
                    except: pass



WeatherWorld()

