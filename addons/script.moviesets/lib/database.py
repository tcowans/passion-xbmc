"""
    Database module
"""

#Modules general
from re import DOTALL, findall
from traceback import print_exc
from urllib import quote_plus

#modules XBMC
from xbmc import executehttpapi as xbmcdb


class Query:
    """ all sql statments. http://wiki.xbmc.org/index.php?title=Database"""

    def __init__( self ):
        # sql statement for sets and keys
        self.key_movie_sets = [ "idSet", "strSet" ]
        self.sql_movie_sets = "SELECT * FROM sets"

        # sql statement for list movies of set and keys
        self.key_movie_by_idset = [ "idMovie", "strTitle", "strSort", "strGenre", "strPlot", "strYear", "playCount", "strPath", "strFileName" ]
        self.sql_movie_by_idset = """
            SELECT movieview.idMovie AS idMovie,
                   c00 AS strTitle,
                   c10 AS strSort,
                   c14 AS strGenre,
                   c01 AS strPlot,
                   c07 AS strYear,
                   playCount,
                   strPath,
                   strFileName
            FROM movieview JOIN setlinkmovie ON movieview.idMovie=setlinkmovie.idMovie
            WHERE setlinkmovie.idSet="%s" ORDER BY strSort
            """

        # sql statement for total Duration of set
        self.key_duration_by_idset = [ "totalDuration" ] # (optional)
        self.sql_duration_by_idset = """
            SELECT ROUND(SUM(iVideoDuration)/60.0) AS totalDuration
            FROM movieview JOIN setlinkmovie ON movieview.idMovie=setlinkmovie.idMovie
            JOIN streamdetails ON movieview.idFile=streamdetails.idFile
            WHERE setlinkmovie.idSet="%s"
            """

        # sql statement for RatingAndVotes of set
        self.key_ratingandvotes_by_idset = [ "rating", "votes" ] # (optional)
        self.sql_ratingandvotes_by_idset = """
            SELECT SUM(movieview.c05)/COUNT(*) AS rating,
            SUM(REPLACE(movieview.c04,",","")) AS votes
            FROM movieview JOIN setlinkmovie ON movieview.idMovie=setlinkmovie.idMovie
            WHERE setlinkmovie.idSet="%s"
            """

        # sql statement for moviesets playcount by idset and keys
        #self.key_watched_by_idset = [ "idMovie" ] # (optional)
        #self.sql_watched_by_idset = """
        #    SELECT movieview.idMovie AS idMovie
        #    FROM movieview JOIN setlinkmovie
        #    ON movieview.idMovie=setlinkmovie.idMovie
        #    WHERE setlinkmovie.idSet="%s"
        #    AND playCount IS NOT NULL
        #    """


class Records( Query ):
    """ fetch records """

    def __init__( self ):
        Query.__init__( self )

    def _set_records_format( self ):
        # format our records start and end
        xbmcdb( "SetResponseFormat()" )
        xbmcdb( "SetResponseFormat(OpenRecord,<records>)" )
        xbmcdb( "SetResponseFormat(CloseRecord,</records>)" )

    def fetch( self, sql, keys=None, index=None ):
        records = []
        try:
            records_xml = xbmcdb( "QueryVideoDatabase(%s)" % quote_plus( sql ), )
            records = findall( "<records>(.+?)</records>", records_xml, DOTALL )
        except:
            print_exc()
        return self.parseFields( records, keys, index )

    def parseFields( self, records, keys=None, index=None ):
        fields = []
        try:
            for record in records:
                record = findall( "<field>(.*?)</field>", record, DOTALL )
                if keys:
                    if len( record ) != len( keys ):
                        print keys, record
                        print records
                    record = dict( zip( keys, record ) )
                fields.append( record )
            if fields and index is not None:
                fields = fields[ index ]
        except:
            print_exc()
        return fields


class Database( Records ):
    """ Main database class """

    def __init__( self, *args, **kwargs ):
        Records.__init__( self )
        self._set_records_format()
