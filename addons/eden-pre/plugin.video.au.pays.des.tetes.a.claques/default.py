# -*- coding: utf-8 -*-

import os
import sys
from traceback import print_exc

import xbmcgui
import xbmcvfs
from xbmcaddon import Addon

ADDON  = Addon( "plugin.video.au.pays.des.tetes.a.claques" )
FANART = ADDON.getAddonInfo( "fanart" )

SUBTITLES = xbmc.translatePath( "special://subtitles/" )
if not xbmcvfs.exists( SUBTITLES ): SUBTITLES = xbmc.translatePath( ADDON.getAddonInfo( "profile" ) )
SUBTITLES = SUBTITLES.replace( "\\", "/" ).rstrip( "/" ) + "/"


b_infoLabels = {
    "tvshowtitle": ADDON.getAddonInfo( "name" ),
    "genre":       "Animation / Humour",
    "season":      1,
    "year":        2012,
    "studio":      "Salambo Productions inc.",
    "writer":      "Michel Beaudet",
    "director":    "Michel Beaudet",
    }



def add_container():
    import xbmcplugin
    from resources.lib.scraper import getEpisodes, S01_AIRED
    ok = True
    count = 0
    for ep in getEpisodes( ADDON.getSetting( "getplot" ) == "true", ADDON.getSetting( "full" ) == "true" ):
        #
        listitem = xbmcgui.ListItem( ep[ "title" ], "", "DefaultTVShows.png", ep[ "icon" ] )
        #
        listitem.setProperty( "id",      ep[ "id" ] )
        listitem.setProperty( "url",     ep[ "url" ] )
        listitem.setProperty( "srt_url", ep[ "srt_url" ] )
        listitem.setProperty( "hd_url",  ep[ "hd_url" ] )
        listitem.setProperty( "sd_url",  ep[ "sd_url" ] )
        listitem.setProperty( "fanart_image", FANART )
        #
        infoLabels = {
            "title":       ep[ "title" ],
            "plot":        ep[ "plot" ],
            "episode":     int( ep[ "episode" ] ),
            "Aired":       ep[ "aired" ],
            "mpaa":        ep[ "rate" ],
            "duration":    "23",
            "castandrole": [],
            }
        infoLabels.update( b_infoLabels )
        listitem.setInfo( "Video", infoLabels )
        #
        if ep[ "hd_url" ] or ep[ "sd_url" ]:
            url = ( ep[ "hd_url" ], ep[ "sd_url" ] )[ int( ADDON.getSetting( "quality" ) ) ]
        else:
            url = '%s?ID="%s"' % ( sys.argv[ 0 ], ep[ "id" ] )
        ok = xbmcplugin.addDirectoryItem( int( sys.argv[ 1 ] ), url, listitem, False )
        count += 1
    #
    try:
        icon = "http://tetesaclaques.tv/public/images/serie_tele_preview_QC.jpg"
        listitem = xbmcgui.ListItem( "Épisode %i disponible le %s" % ( count+1, S01_AIRED[ count ] ) )
        listitem.setThumbnailImage( icon )
        listitem.setProperty( "fanart_image", icon )
        url = '%s?webbrowser=1' % ( sys.argv[ 0 ] )
        ok = xbmcplugin.addDirectoryItem( int( sys.argv[ 1 ] ), url, listitem, False )
    except:
        pass
    xbmcplugin.setContent( int( sys.argv[ 1 ] ), "episodes" )
    xbmcplugin.addSortMethod( int( sys.argv[ 1 ] ), xbmcplugin.SORT_METHOD_UNSORTED )
    xbmcplugin.endOfDirectory( int( sys.argv[ 1 ] ), ok )


def playClip():
    import xbmc
    title = unicode( xbmc.getInfoLabel( "ListItem.Title" ), "utf-8" )
    thumb = unicode( xbmc.getInfoImage( "ListItem.Thumb" ), "utf-8" )
    #
    listitem = xbmcgui.ListItem( title, '', 'DefaultVideo.png', thumb )
    #
    infoLabels = {
        'title': title,
        'plot': unicode( xbmc.getInfoLabel( "ListItem.Plot" ), "utf-8" ),
        "episode": int( xbmc.getInfoImage( "ListItem.episode" ) or "-1" ),
        }
    infoLabels.update( b_infoLabels )
    listitem.setInfo( 'video', infoLabels )
    #
    if ADDON.getSetting( "full" ) == "false":
        from resources.lib.scraper import getClip
        srt, hd, sd = getClip( xbmc.getInfoLabel( "ListItem.Property(id)" ) )
    else:
        srt, hd, sd = xbmc.getInfoLabel( "ListItem.Property(srt_url)" ), xbmc.getInfoLabel( "ListItem.Property(hd_url)" ), xbmc.getInfoLabel( "ListItem.Property(sd_url)" )
    #
    media = ( hd, sd )[ int( ADDON.getSetting( "quality" ) ) ]
    #
    xbmc.Player().play( media, listitem )
    #
    print "playClip(%r)" % media
    #
    if ADDON.getSetting( "subtitle" ) == "true":
        from resources.lib.scraper import getSubtitle
        srt = getSubtitle( srt, os.path.splitext( os.path.basename( media ) )[ 0 ] )
        if not xbmc.Player().isPlaying():
            xbmc.sleep( 5000 )
        xbmc.Player().setSubtitles( srt )
        xbmc.Player().showSubtitles( True )



if ( __name__ == "__main__" ):
    if "ID=" in  sys.argv[ 2 ]:
        playClip()
    elif "webbrowser" in  sys.argv[ 2 ]:
        import webbrowser
        webbrowser.open( "http://tetesaclaques.tv/serietele" )
    else:
        add_container()
