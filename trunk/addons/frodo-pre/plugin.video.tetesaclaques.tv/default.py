# -*- coding: utf-8 -*-

import os
import sys
from traceback import print_exc

import xbmcgui
import xbmcvfs
from xbmcaddon import Addon

ADDON   = Addon( "plugin.video.tetesaclaques.tv" )
FANART  = ADDON.getAddonInfo( "fanart" )
FANART2 = FANART.replace( ".jpg", "2.jpg" )
ICON_TV = ADDON.getAddonInfo( "icon" ).replace( ".png", "2.png" )

SUBTITLES = xbmc.translatePath( "special://subtitles/" )
if not xbmcvfs.exists( SUBTITLES ): SUBTITLES = xbmc.translatePath( ADDON.getAddonInfo( "profile" ) )
SUBTITLES = SUBTITLES.replace( "\\", "/" ).rstrip( "/" ) + "/"
try: os.makedirs( SUBTITLES )
except: xbmcvfs.mkdir( SUBTITLES )


b_infoLabels = {
    "genre":       "Animation / Humour",
    "studio":      "Salambo Productions inc.",
    "writer":      "Michel Beaudet",
    "director":    "Michel Beaudet",
    "castandrole": [ ( "Michel Beaudet", "" ) ],
    }

class Info:
    def __init__( self, *args, **kwargs ):
        # update dict with our formatted argv
        try: exec "self.__dict__.update(%s)" % ( sys.argv[ 2 ][ 1: ].replace( "&", ", " ), )
        except: print_exc()
        # update dict with custom kwargs
        self.__dict__.update( kwargs )

    def __getattr__( self, namespace ):
        return self[ namespace ]

    def __getitem__( self, namespace ):
        return self.get( namespace )

    def __setitem__( self, key, default="" ):
        self.__dict__[ key ] = default

    def get( self, key, default="" ):
        return self.__dict__.get( key, default )#.lower()

    def isempty( self ):
        return not bool( self.__dict__ )

    def IsTrue( self, key, default="false" ):
        return ( self.get( key, default ).lower() == "true" )
PARAMS = Info()


def add_categories():
    import xbmcplugin
    #
    listitem = xbmcgui.ListItem( "Série télé", "", "DefaultTVShows.png", ICON_TV )
    listitem.setProperty( "fanart_image", FANART2 )
    plot = "Au pays des Têtes à claques[CR]Au fil des épisodes, on retrouve tous les personnages rendus célèbres sur le web, auxquels viennent se greffer de nouveaux protagonistes créés spécialement pour l’occasion. Ainsi, les Raoul, Monique, Lucien, Oncle Tom, Gabriel, Samuel, Yvon, le pilote et plusieurs autres font face à de nouvelles situations, toujours amusantes, souvent risibles et rarement banales."
    infoLabels = { 'title': "Série télé", 'plot': plot, "genre": "Animation / Humour" }
    #infoLabels.update( b_infoLabels )
    listitem.setInfo( 'video', infoLabels )
    url = '%s?category="tvshow"' % ( sys.argv[ 0 ] )
    ok = xbmcplugin.addDirectoryItem( int( sys.argv[ 1 ] ), url, listitem, True )
    #
    listitem = xbmcgui.ListItem( "Les clips", "", "DefaultMovies.png" )
    listitem.setProperty( "fanart_image", FANART )
    plot = "«Têtes à claques» est une série québécoise humoristique dont le principe est l'incrustation des yeux et de la bouche du créateur dans des figurines. Vous allez faire connaissance avec les personnages les plus délirants et les expressions québécoises les plus incompréhensibles du net !."
    listitem.setInfo( 'video', { 'title': "Les clips", 'plot': plot, "genre": "Animation / Humour" } )
    url = '%s?category="collection"&page="1"' % ( sys.argv[ 0 ] )
    ok = xbmcplugin.addDirectoryItem( int( sys.argv[ 1 ] ), url, listitem, True )
    #
    from random import choice
    from resources.lib.scraper import fanarts
    fanart = 'http://www.tetesaclaques.tv/public/images/wallpapers/' + choice( fanarts.values() )
    listitem = xbmcgui.ListItem( "Personnages", "", "DefaultActor.png" )
    listitem.setProperty( "fanart_image", fanart )
    listitem.setInfo( 'video', { 'title': "Personnages", 'plot': "Clips des personnages les plus populaires des Têtes à claques.", "genre": "Animation / Humour" } )
    url = '%s?category="personnages"' % ( sys.argv[ 0 ] )
    ok = xbmcplugin.addDirectoryItem( int( sys.argv[ 1 ] ), url, listitem, True )
    #
    listitem = xbmcgui.ListItem( "Extras", "", "DefaultMovies.png" )
    listitem.setProperty( "fanart_image", FANART )
    listitem.setInfo( 'video', { 'title': "Extras", 'plot': "Bandes annonces, Extras clips, Musique et Publicités.", "genre": "Animation / Humour" } )
    url = '%s?category="extras"' % ( sys.argv[ 0 ] )
    ok = xbmcplugin.addDirectoryItem( int( sys.argv[ 1 ] ), url, listitem, True )
    #
    xbmcplugin.setContent( int( sys.argv[ 1 ] ), "movies" )
    xbmcplugin.addSortMethod( int( sys.argv[ 1 ] ), xbmcplugin.SORT_METHOD_UNSORTED )
    xbmcplugin.endOfDirectory( int( sys.argv[ 1 ] ), ok )


def add_tvshow():
    import xbmcplugin
    from resources.lib.scraper import getEpisodes
    ok = True
    for ep in getEpisodes():
        #
        listitem = xbmcgui.ListItem( ep[ "title" ], "", "DefaultTVShows.png", ep[ "icon" ] )
        #
        listitem.setProperty( "id",       ep[ "id" ] )
        listitem.setProperty( "url",      ep[ "url" ] )
        listitem.setProperty( "subtitle", ep[ "subtitle" ] )
        listitem.setProperty( "playpath", ep[ "playpath" ] )
        listitem.setProperty( "fanart_image", FANART2 )
        #
        infoLabels = {
            "tvshowtitle": "Au pays des Têtes à claques",
            "season":      1,
            "year":        2012,
            "title":       ep[ "title" ],
            "plot":        ep[ "plot" ],
            "episode":     int( ep[ "episode" ] ),
            "Aired":       ep[ "aired" ],
            "rating":      ep[ "rate" ],
            "duration":    "23",
            }
        infoLabels.update( b_infoLabels )
        listitem.setInfo( "Video", infoLabels )
        
        if hasattr( listitem, "addStreamInfo" ):
            listitem.addStreamInfo( 'audio', { 'Codec': 'aac', 'language': 'fr', 'channels': 2 } )
            listitem.addStreamInfo( 'video', { 'Codec': 'h264', 'Width': 1230, 'height': 680 } )
            listitem.addStreamInfo( 'subtitle', { 'language': 'fr' } )

        url = '%s?playpath="true"' % ( sys.argv[ 0 ] )
        # add ContextMenuitems
        c_items = [ ( "Play with Subtitle", 'RunPlugin(%s)' % url ),
            ( "Visit Episode", 'RunPlugin(%s?webbrowser="%s")' % ( sys.argv[ 0 ], ep[ "url" ] ) ) ]
        listitem.addContextMenuItems( c_items )
        #
        url = ep[ "playpath" ]
        ok = xbmcplugin.addDirectoryItem( int( sys.argv[ 1 ] ), url, listitem, False )

    xbmcplugin.setContent( int( sys.argv[ 1 ] ), "episodes" )
    xbmcplugin.addSortMethod( int( sys.argv[ 1 ] ), xbmcplugin.SORT_METHOD_UNSORTED )
    xbmcplugin.endOfDirectory( int( sys.argv[ 1 ] ), ok )


def add_personnages():
    import xbmcplugin
    from resources.lib.scraper import getPersonnages
    ok = True
    for person in getPersonnages():
        #
        listitem = xbmcgui.ListItem( person[ "title" ], "", "DefaultActor.png", person[ "icon" ] )
        listitem.setProperty( "fanart_image", person[ "fanart" ] )

        infoLabels = {
            "title":    person[ "title" ],
            #"episode": int( person[ "clips" ] ),
            "duration": person[ "duration" ],
            "plot": "%s Clips[CR]%s Minutes" % ( person[ "clips" ], person[ "duration" ] ),
            }
        infoLabels.update( b_infoLabels )
        listitem.setInfo( "Video", infoLabels )
        
        url = '%s?personclips="%s"' % ( sys.argv[ 0 ], person[ "url" ] )
        ok = xbmcplugin.addDirectoryItem( int( sys.argv[ 1 ] ), url, listitem, True )

    xbmcplugin.setContent( int( sys.argv[ 1 ] ), "movies" )
    xbmcplugin.addSortMethod( int( sys.argv[ 1 ] ), xbmcplugin.SORT_METHOD_UNSORTED )
    xbmcplugin.endOfDirectory( int( sys.argv[ 1 ] ), ok )


def add_clips():
    cmd = None
    if bool( PARAMS.personclips ):
        url = PARAMS.personclips
        from resources.lib.scraper import getPersonnageClips as cmd
    elif PARAMS.category == "collection":
        url = PARAMS.page or "1"
        from resources.lib.scraper import getCollection as cmd
    if not cmd: raise

    import xbmcplugin
    ok = True
    for clip in cmd( url ):
        if clip.has_key( "nextpage" ):
            if clip[ "nextpage" ]:
                listitem = xbmcgui.ListItem( "Next Page (%s)" % clip[ "nextpage" ], "", "DefaultNextFolder.png" )
                listitem.setProperty( "fanart_image", FANART )
                url = '%s?category="collection"&page="%s"' % ( sys.argv[ 0 ], clip[ "nextpage" ] )
                ok = xbmcplugin.addDirectoryItem( int( sys.argv[ 1 ] ), url, listitem, True )
            continue
        #
        listitem = xbmcgui.ListItem( clip[ "title" ], "", "DefaultMovies.png", clip[ "icon" ] )
        #
        listitem.setProperty( "id",       clip[ "id" ] )
        listitem.setProperty( "url",      clip[ "url" ] )
        listitem.setProperty( "subtitle", clip[ "subtitle" ] )
        listitem.setProperty( "playpath", clip[ "playpath" ] )
        listitem.setProperty( "fanart_image", FANART )
        #
        infoLabels = {
            "title":    clip[ "title" ],
            "plot":     clip[ "plot" ],
            "Aired":    clip[ "aired" ],
            "rating":   clip[ "rate" ],
            #"duration": "23",
            }
        infoLabels.update( b_infoLabels )
        listitem.setInfo( "Video", infoLabels )
        
        if hasattr( listitem, "addStreamInfo" ):
            vcodec = os.path.splitext( clip[ "playpath" ] )[ -1 ].strip( "." )
            listitem.addStreamInfo( 'audio', { 'Codec': 'mp3', 'language': 'fr', 'channels': 1 } )
            listitem.addStreamInfo( 'video', { 'Codec': vcodec, 'Width': 610, 'height': 338 } )
            listitem.addStreamInfo( 'subtitle', { 'language': 'fr' } )

        url = '%s?playpath="true"' % ( sys.argv[ 0 ] )
        # add ContextMenuitems
        c_items = [ ( "Play with Subtitle", 'RunPlugin(%s)' % url ),
            ( "Visit Clip", 'RunPlugin(%s?webbrowser="%s")' % ( sys.argv[ 0 ], clip[ "url" ] ) ) ]
        listitem.addContextMenuItems( c_items )
        #
        url = clip[ "playpath" ]
        ok = xbmcplugin.addDirectoryItem( int( sys.argv[ 1 ] ), url, listitem, False )

    xbmcplugin.setContent( int( sys.argv[ 1 ] ), "movies" )
    xbmcplugin.addSortMethod( int( sys.argv[ 1 ] ), xbmcplugin.SORT_METHOD_UNSORTED )
    xbmcplugin.endOfDirectory( int( sys.argv[ 1 ] ), ok )


def add_extras():
    import xbmcplugin
    from resources.lib.scraper import getExtras
    ok = True
    for ex in getExtras():
        #
        listitem = xbmcgui.ListItem( ex[ "title" ], "", "DefaultMovies.png", ex[ "icon" ] )
        #
        listitem.setProperty( "url",      ex[ "url" ] )
        listitem.setProperty( "subtitle", ex[ "subtitle" ] )
        listitem.setProperty( "playpath", ex[ "playpath" ] )
        listitem.setProperty( "fanart_image", FANART )
        #
        infoLabels = {
            "genre":       ex[ "genre" ],
            "title":       ex[ "title" ],
            "plot":        ex[ "plot" ],
            "rating":      ex[ "rate" ],
            }
        listitem.setInfo( "Video", infoLabels )
        
        if hasattr( listitem, "addStreamInfo" ):
            vcodec = os.path.splitext( ex[ "playpath" ] )[ -1 ].strip( "." )
            listitem.addStreamInfo( 'audio', { 'Codec': 'mp3', 'language': 'fr', 'channels': 1 } )
            listitem.addStreamInfo( 'video', { 'Codec': vcodec, 'Width': 610, 'height': 338 } )
            listitem.addStreamInfo( 'subtitle', { 'language': 'fr' } )

        # add ContextMenuitems
        c_items = []
        if ex[ "mp3" ]:
            c_items += [ ( "Play Song", 'PlayMedia(%s)' % ex[ "mp3" ] ) ]
        else:
            url = '%s?playpath="true"' % ( sys.argv[ 0 ] )
            c_items += [ ( "Play with Subtitle", 'RunPlugin(%s)' % url ) ]
        c_items += [ ( "Visit Extra", 'RunPlugin(%s?webbrowser="%s")' % ( sys.argv[ 0 ], ex[ "url" ] ) ) ]
        listitem.addContextMenuItems( c_items )
        #
        url = ex[ "playpath" ]
        ok = xbmcplugin.addDirectoryItem( int( sys.argv[ 1 ] ), url, listitem, False )

    xbmcplugin.setContent( int( sys.argv[ 1 ] ), "movies" )
    xbmcplugin.addSortMethod( int( sys.argv[ 1 ] ), xbmcplugin.SORT_METHOD_GENRE )
    xbmcplugin.endOfDirectory( int( sys.argv[ 1 ] ), ok )


def playClip():
    import xbmc
    title   = unicode( xbmc.getInfoLabel( "ListItem.Title" ), "utf-8" )
    thumb   = unicode( xbmc.getInfoImage( "ListItem.Thumb" ), "utf-8" )
    plot    = unicode( xbmc.getInfoLabel( "ListItem.Plot" ), "utf-8" )
    episode = int( xbmc.getInfoImage( "ListItem.episode" ) or "-1" )
    srt     = xbmc.getInfoLabel( "ListItem.Property(subtitle)" )
    media   = xbmc.getInfoLabel( "ListItem.Property(playpath)" )
    #
    listitem = xbmcgui.ListItem( title, '', 'DefaultVideo.png', thumb )
    infoLabels = { 'title': title, 'plot': plot, "episode": episode }
    infoLabels.update( b_infoLabels )
    listitem.setInfo( 'video', infoLabels )
    #
    xbmc.Player().play( media, listitem )
    print "playClip(%r)" % media
    #
    from resources.lib.scraper import getSubtitle
    srt = getSubtitle( srt, os.path.splitext( os.path.basename( media ) )[ 0 ] )
    if not xbmc.Player().isPlaying(): xbmc.sleep( 5000 )
    print "setSubtitles(%r)"% srt
    xbmc.Player().setSubtitles( srt )
    #xbmc.Player().showSubtitles( True )


if ( __name__ == "__main__" ):
    if PARAMS.isempty():
        add_categories()
        
    elif PARAMS.IsTrue( "playpath" ):
        playClip()
        
    elif PARAMS.category == "tvshow":
        add_tvshow()
        
    elif PARAMS.category == "personnages":
        add_personnages()

    elif PARAMS.category == "extras":
        add_extras()

    elif bool( PARAMS.webbrowser ):
        import webbrowser
        webbrowser.open( PARAMS.webbrowser )

    else:
        add_clips()
