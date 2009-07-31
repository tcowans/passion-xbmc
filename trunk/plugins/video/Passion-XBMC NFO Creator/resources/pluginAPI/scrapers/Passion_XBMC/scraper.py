
import os
import re
import time
import urllib


ALLOCINE_DOMAIN = "http://www.allocine.fr"

MOVIE_URL = "/film/fichefilm_gen_cfilm=%s.html"


def download_html( url ):
    try:
        sock = urllib.urlopen( url )
        html = sock.read()
        sock.close()
    except:
        html = "Not found!"

    return html


def get_video_url( mediaID="18791182", quality=None ):
    return None


  
class Movie:
    u"""Movie object instance."""
    def __init__ ( self, IDmovie ):

        self.ID=IDmovie
        self.HTML = download_html( "http://passion-xbmc.org/scraper/index.php?id=%s" % self.ID )
        self.TITLE = ""
        self.ORIGINAL_TITLE = ""
        self.DATE = ""
        self.DIRECTOR = tuple()
        self.NATIONALITY = ""
        self.INFOS = ""
        self.SYNOPSIS = ""
        self.HAS_VIDEOS = False
        self.HAS_CASTING = False
        self.PHOTOS = []
        self.HAS_PHOTOS = False
        self.CASTING = dict()
        self.PICurl = ""
        self.MEDIAS = []

    def isvalid( self ):
        pass
        
    def director( self ):
        pass

    def nationality( self ):
        pass

    def infos( self ):
        pass

    def title( self ):
        pass

    def date( self ):
        pass

    def year( self ):
        pass

    def rate_and_vote( self ):
        pass

    def fiche_tech( self ):
        pass

    def tagline( self ):
        pass

    def studio( self ):
        pass
        
    def get_genre( self ):
        pass

    def get_runtime( self ):
        pass

    def get_outline( self ):
        pass

    def synopsis( self ):
        pass

    def has_videos( self ):
        return None

    def has_casting( self ):
        return None
    
    def has_photos( self ):
        return None

    def pictureURL( self ):
        pass

    def get_photos( self ):
        pass

    def get_casting( self ):
        pass

    def get_mediaIDs( self ):
        pass

    def BAurl( self, maxi=0 ):
        pass

    def XML( self, fpath="", passion_fanart=False, clear_actor="false", clear_genre="false", clear_studio="false", clear_credits="false", clear_director="false" ):
        #f.write( "\t<>" +  + "</>\n" )
        nfo_file = os.path.join( fpath, "%s.xml" % self.ID )
        if re.search( "<details>|<movie>", self.HTML ):
            f = open( nfo_file, "w" )
            f.write( "<!-- NFO Creator Online: Video nfo File created on: %s -->\n" % ( time.strftime( "%d-%m-%Y | %H:%M:%S" ) ) )
            f.write( self.set_pretty_formatting( self.HTML ) )
            f.close()

            return nfo_file
        else:
            return ""

    def set_pretty_formatting( self, text, by="" ):
        text = text.replace( "<br />", "\n" )
        text = text.replace( "<i>", "[I]" ).replace( "</i>", "[/I]" )
        text = text.replace( "<b>", "[B]" ).replace( "</b>", "[/B]" )
        return text

    def __repr__( self ):
        return "< NFO Creator Online movie object ID#%s >" % self.ID



if __name__ == "__main__":
    film = Movie( "110096" )
    print film.XML( passion_fanart=True )
