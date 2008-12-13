"""
slideshow du plugin All Game

frost
"""

import os
import xbmc


def clearPlayList( m3u ):
    #xbmc.PlayList(0).clear()
    #xbmc.PlayList(1).clear()
    try: os.unlink( m3u )
    except: pass


def playSlideshow( screens=[] ):
    if not screens: return
    elif len( screens ) == 1:
        xbmc.executehttpapi( "ShowPicture(%s)" % ( screens[ 0 ], ) )
    else:
        #Clears the slideshow playlist.
        #print xbmc.executehttpapi( "ClearSlideshow" )

        #AddToSlideshow(media;[mask];[recursive])
        #Adds a file or folder (media is either a file or a folder) to the slideshow playlist. To specify a file mask use mask e.g. .jpg|.bmp
        #[Added 4 Jan 08] If recursive = "1" and media is a folder then all appropriate media within subfolders beneath media will be added otherwise only media within the folder media
        #will be added. Default behaviour is to be recursive. [Added 5 Jan 08] mask can now also be set to one of the
        #following values [music], [video], [pictures], [files] in which case XBMC's current set of file extensions for the
        #type specified will be used as the mask. (Note it only makes much sense for this command to use a value of [pictures].

        m3u = os.path.join( xbmc.translatePath( "Z:\\" ), "passion_slideshow.m3u" )
        #clearPlayList is not very necessary, because next line "w" is used. "w" == write new file.
        clearPlayList( m3u )

        file = open( m3u, "w+" )
        file.write( "#EXTM3U" )
        for count, screen in enumerate( screens ):
            #thumb = xbmc.getCacheThumbName( screen )
            #print thumb
            file.write( "\n#EXTINF:0,%i - %s\n%s" % ( ( count + 1 ), os.path.basename( screen ), screen, ) )
            #print xbmc.executehttpapi( "AddToSlideshow(%s)" % ( screen, ) )
        file.close()

        #PlaySlideshow([directory];[recursive])
        #Starts the slideshow. Directory specifies a folder of images to add to the slideshow playlist.
        #If recursive has a value of True then all directories beneath directory are searched for images and added to the slideshow playlist.
        xbmc.executehttpapi( "PlaySlideshow(%s;false)" % ( m3u, ) )
