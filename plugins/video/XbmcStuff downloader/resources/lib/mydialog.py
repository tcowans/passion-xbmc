# -- coding: cp1252 -*-

import os
import sys
from traceback import print_exc

import xbmc
import xbmcgui


CWD = os.getcwd().rstrip( ";" )

SPECIAL_PROFILE_DIR = xbmc.translatePath( "special://profile/" )

BASE_CACHE_PATH = os.path.join( SPECIAL_PROFILE_DIR, "Thumbnails", "Video" )


def reduced_path( fpath ):
    try:
        list_path = fpath.split( os.sep )
        for pos in list_path[ 1:-2 ]:
            list_path[ list_path.index( pos ) ] = ".."
        return os.sep.join( list_path )
    except:
        print_exc()
        return fpath

def get_thumbnail( path ):
    try:
        fpath = path
        # make the proper cache filename and path so duplicate caching is unnecessary
        filename = xbmc.getCacheThumbName( fpath )
        thumbnail = os.path.join( BASE_CACHE_PATH, filename[ 0 ], filename )
        # if the cached thumbnail does not exist check for a tbn file
        if ( not os.path.isfile( thumbnail ) ):
            # create filepath to a local tbn file
            thumbnail = os.path.splitext( path )[ 0 ] + ".tbn"
            try: thumbnail = thumbnail.encode( "utf-8" )
            except: pass
            # if there is no local tbn file leave blank
            if ( not os.path.isfile( thumbnail ) ):
                thumbnail = ""
        return thumbnail
    except:
        print_exc()
        return ""


#get cached xbmc thumb
try: LIST_ITEM_THUMB = xbmc.translatePath( xbmc.getInfoImage( "ListItem.Thumb" ) ) or get_thumbnail( sys.argv[ 0 ] + sys.argv[ 2 ] )
except:
    LIST_ITEM_THUMB = ""
    print_exc()
if not LIST_ITEM_THUMB:
    LIST_ITEM_THUMB = "DefaultPicture.png"


class MainGui( xbmcgui.WindowXMLDialog ):
    def __init__( self, *args, **kwargs ):
        xbmcgui.WindowXMLDialog.__init__( self, *args, **kwargs )

        #set heading, picture, type, line, yes, no
        self.heading = kwargs.get( "heading", "No title" )
        self.picture = kwargs.get( "picture", "DefaultPicture.png" )
        self.type = kwargs.get( "type", "" ) or self.heading
        self.line_label = kwargs.get( "line", "" )
        self.label_button_1 = kwargs.get( "yes", "Yes" )
        self.label_button_2 = kwargs.get( "no", "No" )

    def onInit( self ):
        try:
            # contorl label et image qui se trouve dans le xml
            self.getControl( 1 ).setLabel( self.heading )
            self.getControl( 2 ).setLabel( self.line_label )
            self.getControl( 10 ).setLabel( self.label_button_2 )
            self.getControl( 11 ).setLabel( self.label_button_1 )

            if LIST_ITEM_THUMB and self.picture.startswith( "http://" ):
                #print "LIST_ITEM_THUMB", LIST_ITEM_THUMB
                self.getControl( 9 ).setImage( LIST_ITEM_THUMB )
            else:
                #print "self.picture", self.picture
                self.getControl( 9 ).setImage( self.picture )
        except:
            print_exc()

    def onFocus( self, controlID ):
        pass

    def onClick( self, controlID ):
        try:
            if controlID == 10:
                # button_2
                self.close()
            elif controlID == 11:
                # button_1
                #c'est ici que tu ecrie ta fonction progressbar du DL 
                self.close()
                success = sys.modules[ "__main__" ].current_show.get_image( self.type, self.picture )
                if success:
                    line1 = "Image downloaded successfully!"
                    line2 = "Dir: %s" % reduced_path( os.path.dirname( success ) )
                    line3 = "File: %s" % os.path.basename( success )
                    #clear thumbnail cache for tv_show
                    if self.type == "TVthumbs":
                        try: os.remove(get_thumbnail( sys.modules[ "__main__" ].current_show.path ))
                        except: print_exc()
                else:
                    line1 = "Error while downloading image"
                    line2 = ""
                    line3 = ""
                    
                xbmcgui.Dialog().ok( self.heading, line1, line2, line3 )
        except:
            print_exc()

    def onAction( self, action ):
        # si action previous et back on ferme le dialog
        if action in ( 9, 10 ):
            self.close()


def getUserSkin():
    current_skin = xbmc.getSkinDir()
    force_fallback = os.path.exists( os.path.join( CWD, "resources", "skins", current_skin ) )
    if not force_fallback: current_skin = "Default"
    return current_skin, force_fallback


def MyDialog( heading, picture, type="", line="Do you want to download this image?", yes="Yes", no="No" ):
    current_skin, force_fallback = getUserSkin()
    #"MyDialog.xml", CWD, current_skin, force_fallback sert a ouvrir le xml du script
    w = MainGui( "MyDialog.xml", CWD, current_skin, force_fallback,
        heading=heading, picture=picture, type=type, line=line, yes=yes, no=no )
    w.doModal()
    del w


def test():
    MyDialog( "xbmc media center", "special://xbmc/media/icon.png" )
