
#Modules general
import os
from os.path import join
from traceback import print_exc

#Modules XBMC
import xbmc
import xbmcgui


DIALOG_PROGRESS = xbmcgui.DialogProgress()


def clear( cache_path, excludes=[], t_file=0, t_dir=0 ):
    try:
        DIALOG_PROGRESS.update( -1, xbmc.getLocalizedString( 30650 ) % cache_path )
        for root, dirs, files in os.walk( cache_path, topdown=False ):
            for file in files:
                fpath = join( root, file )
                exclude = False
                for ex in excludes:
                    ex = join( cache_path, ex )
                    if ( not ex.endswith( "/" ) ) and ( ex in fpath ):
                        exclude = True
                        break
                if not exclude:
                    t_file += 1
                    DIALOG_PROGRESS.update( -1, xbmc.getLocalizedString( 30651 ) % ( t_file, t_dir, ), xbmc.getLocalizedString( 30652 ) % root, xbmc.getLocalizedString( 30653 ) % file )
                    try:
                        os.remove( fpath )
                        print fpath
                    except:
                        print_exc()

            for dir in dirs:
                dpath = join( root, dir )
                exclude = False
                for ex in excludes:
                    ex = join( cache_path, ex )
                    if ( ex.strip( "/" ) in dpath ):
                        exclude = True
                        break
                if not exclude:
                    t_dir += 1
                    DIALOG_PROGRESS.update( -1, xbmc.getLocalizedString( 30651 ) % ( t_file, t_dir, ), xbmc.getLocalizedString( 30652 ) % root, xbmc.getLocalizedString( 30653 ) % dir )
                    try:
                        os.rmdir( dpath )
                        print dpath
                    except:
                        print_exc()
    except:
        print_exc()
    return t_file, t_dir


def Main():
    cache_list = [
        xbmc.getLocalizedString( 30654 ),
        xbmc.getLocalizedString( 30655 ),
        xbmc.getLocalizedString( 30656 ) % xbmc.translatePath( "special://temp/" ),
        xbmc.getLocalizedString( 30656 ) % xbmc.translatePath( "special://profile/cache/" ) ]
    if os.environ.get( "OS", "xbox" ) == "xbox":
        cache_list += [
            xbmc.getLocalizedString( 30657 ),
            xbmc.getLocalizedString( 30658 ) ]
    selected = xbmcgui.Dialog().select( xbmc.getLocalizedString( 30552 ), cache_list )

    if selected != -1:
        t_file, t_dir = 0, 0
        excludes = [ "weather", "temp/" ]
        DIALOG_PROGRESS.create( xbmc.getLocalizedString( 30659 ) )
        if selected in [ 0, 1, 2 ]:
            t_file, t_dir = clear( xbmc.translatePath( "special://temp/" ), excludes, t_file, t_dir )

        if selected in [ 0, 1, 3 ]:
            t_file, t_dir = clear( xbmc.translatePath( "special://profile/cache/" ), [], t_file, t_dir )

        if os.environ.get( "OS", "xbox" ) == "xbox":
            if selected in [ 0, 4 ]:
                t_file, t_dir = clear( "E:\\CACHE\\", [], t_file, t_dir )

            if selected in [ 0, 5 ]:
                t_file, t_dir = clear( "X:\\", [], t_file, t_dir )
                t_file, t_dir = clear( "Y:\\", [], t_file, t_dir )
                t_file, t_dir = clear( "Z:\\", excludes, t_file, t_dir )
        DIALOG_PROGRESS.close()
        xbmcgui.Dialog().ok( xbmc.getLocalizedString( 30552 ), cache_list[ selected ], xbmc.getLocalizedString( 30651 ) % ( t_file, t_dir, ) )



if ( __name__ == "__main__" ):
    Main()
