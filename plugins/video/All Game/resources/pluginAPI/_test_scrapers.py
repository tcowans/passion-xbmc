
try:
    try:
        import psyco
    except:
        import os, sys
        sys.path.append( os.sep.join( os.getcwd().rstrip( ";" ).split( os.sep )[ :-2 ] ) )
        import psyco
    psyco.full()
except:
    from traceback import print_exc
    print_exc()

import time
from scrapers.platforms_scrapers import *
from scrapers.games_scrapers import *
from etree_utilities import *


GAME_PLATFORMS = "IBM PC Compatible"
MAX_PLATFORMS_INFO = 150 # 0 = GAME_PLATFORMS ONLY
MAX_GAMES_INFO = 1 # 100 = 1 complet page

SEPARATOR = str( "-" * 100 )

BASE_DIR = "allgame_com"
if os.environ.get( "OS" ) == "xbox":
    BASE_DIR = "Z:\\" + BASE_DIR

GAMES_DIR_PATH = os.path.join( BASE_DIR, "games" )
PLATFORMS_DIR_PATH = os.path.join( BASE_DIR, "platforms" )
if not os.path.isdir( GAMES_DIR_PATH ): os.makedirs( GAMES_DIR_PATH )
if not os.path.isdir( PLATFORMS_DIR_PATH ): os.makedirs( PLATFORMS_DIR_PATH )


if ( __name__ == "__main__" ):
    t1 = time.ctime()
    listed = get_platforms_listed( PLATFORMS_URL )
    for count, item in enumerate( listed ):
        if item[ "platform" ] != GAME_PLATFORMS and not MAX_PLATFORMS_INFO: continue
        print ( count + 1 ), item[ "platform" ]
        urlsource = urljoin( PLATFORMS_URL, item[ "urlsource" ] )
        tbn, description = get_platform_overview( urlsource )
        tbn = ( "", urljoin( PLATFORMS_URL, tbn ) )[ tbn != "" ]
        item.update( { "tbn": tbn, "description": description, "urlsource": urlsource } )

        filename = os.path.join( PLATFORMS_DIR_PATH, "%s.xml" % ( item[ "ID" ], ) )
        print save_infos( filename, item.copy(), isgame=False )

        #for k, v in item.items():
        #    print k, "=", v
        #    print
        #print SEPARATOR
        #print
        #continue

        pages_listed, games_listed = get_games_listed( urlsource + "~T1" )
        #print "total pages =", len( pages_listed )
        #print SEPARATOR
        #print

        for count2, game in enumerate( games_listed ):
            print ( count2 + 1 ), game[ "title" ]
            game_infos = get_game_overview( game[ "urlsource" ] )
            game.update( game_infos )
            other_infos = get_other_game_infos( game[ "buttons_listed" ], game[ "urlsource" ] )
            game.update( other_infos )

            platform_games_dir_path = os.path.join( GAMES_DIR_PATH, game[ "platform" ].replace( "/", "_" ) )
            if not os.path.isdir( platform_games_dir_path ): os.makedirs( platform_games_dir_path )
            filename = os.path.join( platform_games_dir_path, "%s.xml" % ( game[ "ID" ], ) )
            print save_infos( filename, game.copy() )

            #for k, v in game.items():
            #    print k, "=", v
            #    print
            #print SEPARATOR
            if ( count2 + 1 ) == MAX_GAMES_INFO: break
        print SEPARATOR
        #print
        if ( ( count + 1 ) == MAX_PLATFORMS_INFO ) and ( MAX_PLATFORMS_INFO != 0 ): break
    print t1
    print time.ctime()
