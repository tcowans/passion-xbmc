
class MovieSetDetails( dict ):
    def __init__( self, default={} ):
        # base details
        self[ "fanart" ]    = ""
        self[ "label" ]     = ""
        self[ "playcount" ] = 0
        self[ "setid" ]     = -1
        self[ "thumbnail" ] = ""
        self[ "title" ]     = ""
        self[ "movies" ]    = []

        # extra base details
        self[ "cast" ]           = []
        self[ "country" ]        = set() #countries
        self[ "date" ]           = ""
        self[ "director" ]       = []
        self[ "file" ]           = ""
        self[ "genre" ]          = set() #genres
        self[ "imdbnumber" ]     = ""
        self[ "lastplayed" ]     = ""
        self[ "mpaa" ]           = set()
        self[ "originaltitle" ]  = []
        self[ "plot" ]           = "" #plotset
        self[ "plotoutline" ]    = ""
        self[ "premiered" ]      = ""
        self[ "productioncode" ] = ""
        self[ "rating" ]         = 0
        self[ "resume" ]         = { "position":  0, "total":  0 }
        self[ "runtime" ]        = 0
        #self[ "set" ]            = []
        self[ "showlink" ]       = ""
        self[ "studio" ]         = set() #studios
        self[ "tagline" ]        = ""
        self[ "top250" ]         = 0
        self[ "trailer" ]        = ""
        self[ "votes" ]          = 0
        self[ "writer" ]         = []
        self[ "year" ]           = 0 #

        # streamdetails
        self[ "sdv_duration" ] = 0
        self[ "sdv_width" ]    = 0
        self[ "sdv_height" ]   = 0
        self[ "sdv_aspect" ]   = 0.0
        self[ "sdv_codecs" ]   = []
        self[ "sda_codecs" ]   = []
        self[ "sda_channels" ] = []
        self[ "sda_langs" ]    = []

        # more details
        self[ "years" ]        = set()
        self[ "watched" ]      = 0
        self[ "unwatched" ]    = 0
        self[ "total_movies" ] = 0
        self[ "nfofile" ]      = ""
        self[ "stacktrailer" ] = []
        self[ "stackpath" ]    = []

        self.update( default )

    def setItem( self, key, value ):
        self.update( { key: value } )
        return self[ key ]

