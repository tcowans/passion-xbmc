import xbmc
from xbmcgui import Window
from urllib import quote_plus, unquote_plus
import urllib
import re
import sys
import os
from traceback import print_exc
#import random
__useragent__ = "Mozilla/5.0 (Windows; U; Windows NT 5.1; fr; rv:1.9.0.1) Gecko/2008070208 Firefox/3.6"

class Main:
    # grab the home window
    WINDOW = Window( 10000 )

    def _clear_properties( self ):
        # we enumerate thru and clear individual properties in case other scripts set window properties
        for count in range( self.LIMIT ):
            # we clear title for visible condition
            self.WINDOW.clearProperty( "RecentlyWatchedMovie.%d.Title" % ( count + 1, ) )
            self.WINDOW.clearProperty( "RecentlyWatchedEpisode.%d.ShowTitle" % ( count + 1, ) )
            self.WINDOW.clearProperty( "MostWatchedMovie.%d.Title" % ( count + 1, ) )
            self.WINDOW.clearProperty( "MostWatchedEpisode.%d.ShowTitle" % ( count + 1, ) )

    def _get_media( self, path, file ):
        # set default values
        play_path = fanart_path = thumb_path = path + file
        # we handle stack:// media special
        if ( file.startswith( "stack://" ) ):
            play_path = fanart_path = file
            thumb_path = file[ 8 : ].split( " , " )[ 0 ]
        # we handle rar:// and zip:// media special
        if ( file.startswith( "rar://" ) or file.startswith( "zip://" ) ):
            play_path = fanart_path = thumb_path = file
        # return media info
        return xbmc.getCacheThumbName( thumb_path ), xbmc.getCacheThumbName( fanart_path ), play_path

    def _parse_argv( self ):
        try:
            # parse sys.argv for params
            params = dict( arg.split( "=" ) for arg in sys.argv[ 1 ].split( "&" ) )
        except:
            # no params passed
            params = {}
        # set our preferences
        self.LIMIT = int( params.get( "limit", "5" ) )
        self.ACTOR_LIMIT  = int( params.get( "actorlimit", "25" ) )
#         self.ALBUMS = params.get( "albums", "" ) == "True"
#         self.UNPLAYED = params.get( "unplayed", "" ) == "True"
        self.PLAY_TRAILER = params.get( "trailer", "" ) == "True"
#         self.RANDOM_ORDER = "True"

    def __init__( self ):
        # parse argv for any preferences
        self._parse_argv()
        print "### limit: %s" % self.LIMIT
        # clear properties
        self._clear_properties()
        # format our records start and end
        xbmc.executehttpapi( "SetResponseFormat()" )
        xbmc.executehttpapi( "SetResponseFormat(OpenRecord,%s)" % ( "<record>", ) )
        xbmc.executehttpapi( "SetResponseFormat(CloseRecord,%s)" % ( "</record>", ) )
        # fetch media info
        self._fetch_movie_info()
        self._fetch_tvshow_info()
        self._fetch_actors_info()
        print "END RECENTLY WATCHED SCRIPT"
    
    def _fetch_movie_info( self ):
        # sql statement for most watched        
        print "### MOST WATCHED MOVIE"
        sql_movies = "select * from movieview where playCount is not null order by playCount DESC limit %d" % (self.LIMIT, ) 
        # query the database
        movies_xml = xbmc.executehttpapi( "QueryVideoDatabase(%s)" % quote_plus( sql_movies ), )
        # separate the records
        movies = re.findall( "<record>(.+?)</record>", movies_xml, re.DOTALL )
        # enumerate thru our records and set our properties
        for count, movie in enumerate( movies ):
            # separate individual fields
            fields = re.findall( "<field>(.*?)</field>", movie, re.DOTALL )
            # set properties
            print "### %s - %s" % (fields[ 2 ] ,fields[ 26 ])
            self.WINDOW.setProperty( "MostWatchedMovie.%d.Title" % ( count + 1, ), fields[ 2 ] )
            self.WINDOW.setProperty( "MostWatchedMovie.%d.Rating" % ( count + 1, ), fields[ 7 ] )
            self.WINDOW.setProperty( "MostWatchedMovie.%d.Year" % ( count + 1, ), fields[ 9 ] )
            self.WINDOW.setProperty( "MostWatchedMovie.%d.Plot" % ( count + 1, ), fields[ 3 ] )
            self.WINDOW.setProperty( "MostWatchedMovie.%d.RunningTime" % ( count + 1, ), fields[ 13 ] )
            self.WINDOW.setProperty( "MostWatchedMovie.%d.WatchCount" % ( count + 1, ), fields[ 26 ] )
            # get cache names of path to use for thumbnail/fanart and play path
            thumb_cache, fanart_cache, play_path = self._get_media( fields[ 25 ], fields[ 24 ] )
            if os.path.isfile("%s.dds" % (xbmc.translatePath( "special://profile/Thumbnails/Video/%s/%s" % ( "Fanart", os.path.splitext(fanart_cache)[0],) ) )):
                fanart_cache = "%s.dds" % (os.path.splitext(fanart_cache)[0],)
            self.WINDOW.setProperty( "MostWatchedMovie.%d.Path" % ( count + 1, ), ( play_path, fields[ 21 ], )[ fields[ 21 ] != "" and self.PLAY_TRAILER ] )
            self.WINDOW.setProperty( "MostWatchedMovie.%d.Trailer" % ( count + 1, ), fields[ 21 ] )
            self.WINDOW.setProperty( "MostWatchedMovie.%d.Fanart" % ( count + 1, ), "special://profile/Thumbnails/Video/%s/%s" % ( "Fanart", fanart_cache, ) )
            # initial thumb path
            thumb = "special://profile/Thumbnails/Video/%s/%s" % ( thumb_cache[ 0 ], thumb_cache, )
            # if thumb does not exist use an auto generated thumb path
            if ( not os.path.isfile( xbmc.translatePath( thumb ) ) ):
                thumb = "special://profile/Thumbnails/Video/%s/auto-%s" % ( thumb_cache[ 0 ], thumb_cache, )
            self.WINDOW.setProperty( "MostWatchedMovie.%d.Thumb" % ( count + 1, ), thumb )

        # sql statement for recently watched 
        print "### RECENTLY WATCHED MOVIE"
        sql_movies = "select * from movieview where lastPlayed is not null order by lastPlayed DESC limit %d" % (self.LIMIT, ) 
        # query the database
        movies_xml = xbmc.executehttpapi( "QueryVideoDatabase(%s)" % quote_plus( sql_movies ), )
        # separate the records
        movies = re.findall( "<record>(.+?)</record>", movies_xml, re.DOTALL )
        # enumerate thru our records and set our properties
        for count, movie in enumerate( movies ):
            # separate individual fields
            fields = re.findall( "<field>(.*?)</field>", movie, re.DOTALL )
            # set properties            
            print "### %s - %s" % (fields[ 2 ] ,fields[ 27 ])
            self.WINDOW.setProperty( "RecentlyWatchedMovie.%d.Title" % ( count + 1, ), fields[ 2 ] )
            self.WINDOW.setProperty( "RecentlyWatchedMovie.%d.Rating" % ( count + 1, ), fields[ 7 ] )
            self.WINDOW.setProperty( "RecentlyWatchedMovie.%d.Year" % ( count + 1, ), fields[ 9 ] )
            self.WINDOW.setProperty( "RecentlyWatchedMovie.%d.Plot" % ( count + 1, ), fields[ 3 ] )
            self.WINDOW.setProperty( "RecentlyWatchedMovie.%d.RunningTime" % ( count + 1, ), fields[ 13 ] )
            self.WINDOW.setProperty( "RecentlyWatchedMovie.%d.LastPlayed" % ( count + 1, ), fields[ 27 ] )
            # get cache names of path to use for thumbnail/fanart and play path
            thumb_cache, fanart_cache, play_path = self._get_media( fields[ 25 ], fields[ 24 ] )
            if os.path.isfile("%s.dds" % (xbmc.translatePath( "special://profile/Thumbnails/Video/%s/%s" % ( "Fanart", os.path.splitext(fanart_cache)[0],) ) )):
                fanart_cache = "%s.dds" % (os.path.splitext(fanart_cache)[0],)
            self.WINDOW.setProperty( "RecentlyWatchedMovie.%d.Path" % ( count + 1, ), ( play_path, fields[ 21 ], )[ fields[ 21 ] != "" and self.PLAY_TRAILER ] )
            self.WINDOW.setProperty( "RecentlyWatchedMovie.%d.Trailer" % ( count + 1, ), fields[ 21 ] )
            self.WINDOW.setProperty( "RecentlyWatchedMovie.%d.Fanart" % ( count + 1, ), "special://profile/Thumbnails/Video/%s/%s" % ( "Fanart", fanart_cache, ) )
            # initial thumb path
            thumb = "special://profile/Thumbnails/Video/%s/%s" % ( thumb_cache[ 0 ], thumb_cache, )
            # if thumb does not exist use an auto generated thumb path
            if ( not os.path.isfile( xbmc.translatePath( thumb ) ) ):
                thumb = "special://profile/Thumbnails/Video/%s/auto-%s" % ( thumb_cache[ 0 ], thumb_cache, )
            self.WINDOW.setProperty( "RecentlyWatchedMovie.%d.Thumb" % ( count + 1, ), thumb )

    def _fetch_tvshow_info( self ):
        # sql statement for most watched
        print "### MOST WATCHED EPISODE"
        sql_episodes = "select * from episodeview where playCount is not null order by playCount DESC limit %d" % ( self.LIMIT, )
        # query the database
        episodes_xml = xbmc.executehttpapi( "QueryVideoDatabase(%s)" % quote_plus( sql_episodes ), )
        # separate the records
        episodes = re.findall( "<record>(.+?)</record>", episodes_xml, re.DOTALL )
        # enumerate thru our records and set our properties
        for count, episode in enumerate( episodes ):
            # separate individual fields
            fields = re.findall( "<field>(.*?)</field>", episode, re.DOTALL )
            # set properties  
            print "### %s - %s - %s" % (fields[ 28 ] ,fields[ 2 ] ,fields[ 26 ])      
            self.WINDOW.setProperty( "MostWatchedEpisode.%d.ShowTitle" % ( count + 1, ), fields[ 28 ] )
            self.WINDOW.setProperty( "MostWatchedEpisode.%d.EpisodeTitle" % ( count + 1, ), fields[ 2 ] )
            self.WINDOW.setProperty( "MostWatchedEpisode.%d.EpisodeNo" % ( count + 1, ), "s%02de%02d" % ( int( fields[ 14 ] ), int( fields[ 15 ] ), ) )
            self.WINDOW.setProperty( "MostWatchedEpisode.%d.EpisodeSeason" % ( count + 1, ), fields[ 14 ] )
            self.WINDOW.setProperty( "MostWatchedEpisode.%d.EpisodeNumber" % ( count + 1, ), fields[ 15 ] )
            self.WINDOW.setProperty( "MostWatchedEpisode.%d.Rating" % ( count + 1, ), fields[ 5 ] )
            self.WINDOW.setProperty( "MostWatchedEpisode.%d.Plot" % ( count + 1, ), fields[ 3 ] )
            self.WINDOW.setProperty( "MostWatchedEpisode.%d.WatchCount" % ( count + 1, ), fields[ 26 ] )
            # get cache names of path to use for thumbnail/fanart and play path
            thumb_cache, fanart_cache, play_path = self._get_media( fields[ 25 ], fields[ 24 ] )
            if ( not os.path.isfile( xbmc.translatePath( "special://profile/Thumbnails/Video/%s/%s" % ( "Fanart", fanart_cache, ) ) ) ):
                fanart_cache = xbmc.getCacheThumbName(os.path.join(os.path.split(os.path.split(fields[ 25 ])[0])[0], ""))
            if os.path.isfile("%s.dds" % (xbmc.translatePath( "special://profile/Thumbnails/Video/%s/%s" % ( "Fanart", os.path.splitext(fanart_cache)[0],) ) )):
                fanart_cache = "%s.dds" % (os.path.splitext(fanart_cache)[0],)
            self.WINDOW.setProperty( "MostWatchedEpisode.%d.Path" % ( count + 1, ), play_path )
            self.WINDOW.setProperty( "MostWatchedEpisode.%d.Fanart" % ( count + 1, ), "special://profile/Thumbnails/Video/%s/%s" % ( "Fanart", fanart_cache, ) )
            # initial thumb path
            thumb = "special://profile/Thumbnails/Video/%s/%s" % ( thumb_cache[ 0 ], thumb_cache, )
            # if thumb does not exist use an auto generated thumb path
            if ( not os.path.isfile( xbmc.translatePath( thumb ) ) ):
                thumb = "special://profile/Thumbnails/Video/%s/auto-%s" % ( thumb_cache[ 0 ], thumb_cache, )
            self.WINDOW.setProperty( "MostWatchedEpisode.%d.Thumb" % ( count + 1, ), thumb )
            
        # sql statement for recently watched
        print "### RECENTLY WATCHED EPISODE"
        sql_episodes = "select * from episodeview where lastPlayed is not null order by lastPlayed DESC limit %d" % ( self.LIMIT, )
        # query the database
        episodes_xml = xbmc.executehttpapi( "QueryVideoDatabase(%s)" % quote_plus( sql_episodes ), )
        # separate the records
        episodes = re.findall( "<record>(.+?)</record>", episodes_xml, re.DOTALL )
        # enumerate thru our records and set our properties
        for count, episode in enumerate( episodes ):
            # separate individual fields
            fields = re.findall( "<field>(.*?)</field>", episode, re.DOTALL )
            # set properties  
            print "### %s - %s - %s" % (fields[ 28 ] ,fields[ 2 ] ,fields[ 27 ])      
            self.WINDOW.setProperty( "RecentlyWatchedEpisode.%d.ShowTitle" % ( count + 1, ), fields[ 28 ] )
            self.WINDOW.setProperty( "RecentlyWatchedEpisode.%d.EpisodeTitle" % ( count + 1, ), fields[ 2 ] )
            self.WINDOW.setProperty( "RecentlyWatchedEpisode.%d.EpisodeNo" % ( count + 1, ), "s%02de%02d" % ( int( fields[ 14 ] ), int( fields[ 15 ] ), ) )
            self.WINDOW.setProperty( "RecentlyWatchedEpisode.%d.EpisodeSeason" % ( count + 1, ), fields[ 14 ] )
            self.WINDOW.setProperty( "RecentlyWatchedEpisode.%d.EpisodeNumber" % ( count + 1, ), fields[ 15 ] )
            self.WINDOW.setProperty( "RecentlyWatchedEpisode.%d.Rating" % ( count + 1, ), fields[ 5 ] )
            self.WINDOW.setProperty( "RecentlyWatchedEpisode.%d.Plot" % ( count + 1, ), fields[ 3 ] )
            self.WINDOW.setProperty( "RecentlyWatchedEpisode.%d.LastWatched" % ( count + 1, ), fields[ 27 ] )
            # get cache names of path to use for thumbnail/fanart and play path
            thumb_cache, fanart_cache, play_path = self._get_media( fields[ 25 ], fields[ 24 ] )
            if ( not os.path.isfile( xbmc.translatePath( "special://profile/Thumbnails/Video/%s/%s" % ( "Fanart", fanart_cache, ) ) ) ):
                fanart_cache = xbmc.getCacheThumbName(os.path.join(os.path.split(os.path.split(fields[ 25 ])[0])[0], ""))
            if os.path.isfile("%s.dds" % (xbmc.translatePath( "special://profile/Thumbnails/Video/%s/%s" % ( "Fanart", os.path.splitext(fanart_cache)[0],) ) )):
                fanart_cache = "%s.dds" % (os.path.splitext(fanart_cache)[0],)
            self.WINDOW.setProperty( "RecentlyWatchedEpisode.%d.Path" % ( count + 1, ), play_path )
            self.WINDOW.setProperty( "RecentlyWatchedEpisode.%d.Fanart" % ( count + 1, ), "special://profile/Thumbnails/Video/%s/%s" % ( "Fanart", fanart_cache, ) )
            # initial thumb path
            thumb = "special://profile/Thumbnails/Video/%s/%s" % ( thumb_cache[ 0 ], thumb_cache, )
            # if thumb does not exist use an auto generated thumb path
            if ( not os.path.isfile( xbmc.translatePath( thumb ) ) ):
                thumb = "special://profile/Thumbnails/Video/%s/auto-%s" % ( thumb_cache[ 0 ], thumb_cache, )
            self.WINDOW.setProperty( "RecentlyWatchedEpisode.%d.Thumb" % ( count + 1, ), thumb )

    def _fetch_actors_info( self ):
        print "### MOST REPRESENTED ACTOR"
        # sql statement for actors
        #sql_actors ="SELECT COUNT(actorlinkmovie.idActor), actorlinkmovie.idActor, actors.strActor, actors.strThumb FROM actorlinkmovie INNER JOIN actors ON actorlinkmovie.idActor=actors.idActor GROUP BY actorlinkmovie.idActor order by RANDOM() DESC LIMIT %s" % ( self.ACTOR_LIMIT, ) #order by  COUNT(actorlinkmovie.idActor)
        sql_actors ="SELECT COUNT(actorlinkmovie.idActor), actorlinkmovie.idActor, actors.strActor, actors.strThumb FROM actorlinkmovie INNER JOIN actors ON actorlinkmovie.idActor=actors.idActor GROUP BY actorlinkmovie.idActor order by COUNT(actorlinkmovie.idActor) DESC LIMIT %s" % ( self.ACTOR_LIMIT, ) #
        # query the database
        actors_xml = xbmc.executehttpapi( "QueryVideoDatabase(%s)" % quote_plus( sql_actors ), ) 
        # separate the records
        actors = re.findall( "<record>(.+?)</record>", actors_xml, re.DOTALL )
        # enumerate thru our records and set our properties
        all_actors = []
        for actor in actors :
            # separate individual fields
            fields = re.findall( "<field>(.*?)</field>", actor, re.DOTALL )
            # set properties
            print "### %s %s - %s" % (fields [ 1 ], fields[ 2 ] ,fields[ 0 ] )
            actor_data = self._get_actor_page( fields[ 2 ], fields[ 1 ] )
            all_actors.append(actor_data)
			
            
        for gencount , i in enumerate(all_actors):
            self.WINDOW.setProperty( "ActorStuff.%d.name" % ( gencount + 1, ), i.get("name", "" ) ) 
            self.WINDOW.setProperty( "ActorStuff.%d.ID" % ( gencount + 1, ), i.get("actorID", "" ) )
            print "### DJP!! %s" % i.get("actorID", "" )
            if len(i.get("images", "" )) >> 1:
                for count, image in enumerate( i.get("images", "" ) ): self.WINDOW.setProperty( "ActorStuff.%d.images%d" % ( gencount + 1, count + 1 ), image )
            elif len(i.get("images", "" )) == 1: self.WINDOW.setProperty( "ActorStuff.%d.images1" % ( gencount + 1, ), i.get("images", "" )[0] )
            else: self.WINDOW.setProperty( "ActorStuff.%d.images1" % ( gencount + 1, ), "" )
            self.WINDOW.setProperty( "ActorStuff.%d.bio" % ( gencount + 1, ), i.get("bio", "" ) )
            if i.get("bloc", False):
                for count , info  in enumerate( i["bloc"].keys()):
                    print "%s/%s : %s" % ( count , info , i["bloc"][info] )
                    self.WINDOW.setProperty( "ActorStuff.%d.info%d" % ( gencount + 1, count + 1 ), info + ":" + i["bloc"][info] )
            print "######################"
     
    def _get_actor_page( self, actorname, actorID ):
        lang = "en"
        url = "http://%s.wikipedia.org/wiki/" % lang + actorname.replace(" " , "_" )
        data = self.get_html_source(url)
        
        result = re.findall(r'(?s)<tr class="">\s+<th scope="row" style="text-align:left;">(.*?)</th>\s+<td class=".*?" style="">(.*?)</td>\s+</tr>', data)
        actor_dic = {}
        actor_dic["name"] = actorname
        actor_dic["actorID"] = actorID
        block_dic = {}
        for item in result:
            try:
                cherche1 = re.findall( '(<.*?>)', item[0] )
                for i in cherche1: item[0] = item[0].replace( i , '' )
                cherche2 = re.findall( '(<.*?>)', item[1] )
                test = item[1]
                for k in cherche2: test = test.replace( k , '' )
                block_dic[item[0]] = test
            except:
                print "error in blocks"
                print_exc()
        actor_dic["bloc"] = block_dic
        test = re.findall( '</table>\s<p>(.*?).</p>', data, re.DOTALL )
        try:
            bio = test[0]
            #print bio
            cherche = re.findall( '(<.*?>)', bio )
            for i in cherche: bio = bio.replace( i , "" )
            #print bio
            actor_dic["bio"] = bio
        except: 
            print_exc()
            print "error in bio"
        
        pics = re.findall('src="(.*%s.*\.jpg)" width=".*?" height=".*?"' % actorname.replace(" " , "_" ), data)
        if not pics: pics = re.findall('src="(.*%s.*\.jpg)" width=".*?" height=".*?"' % actorname.replace(" " , "" ).replace("-" , "" ), data, re.IGNORECASE)                 
        if pics:
            cleaned_pics = []
            for pic in pics:
                cleaned_pics.append(pic.split(".jpg")[0].replace("/thumb", "" ) + ".jpg")
            actor_dic["images"] = cleaned_pics
        #else: print "error no pics found"
        return actor_dic
        
    def get_html_source( self, url ):
        """ fetch the html source """
        class AppURLopener(urllib.FancyURLopener):
            version = __useragent__
        try:
            urllib._urlopener = AppURLopener()
            urllib.urlcleanup()
            sock = urllib.urlopen( url )
            htmlsource = sock.read()
            return htmlsource
        except: return ""
if ( __name__ == "__main__" ):
    Main()
