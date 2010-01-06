
# Modules general
import os
import sys
from traceback import print_exc

# Modules XBMC
import xbmc
import xbmcgui


#FONCTION POUR RECUPERER LES LABELS DE LA LANGUE.
_ = sys.modules[ "__main__" ].__language__

DIALOG_PROGRESS = xbmcgui.DialogProgress()


#par_dir = "../../"
home_dir = os.getcwd()#os.sep.join( os.getcwd().split( os.sep )[ :-par_dir.count( "../" ) ] )


def clear( cache_path, excludes=[], t_file=0, t_dir=0 ):
    try:
        DIALOG_PROGRESS.update( -1, _( 32650 ) % cache_path )
        for root, dirs, files in os.walk( cache_path, topdown=False ):
            for file in files:
                fpath = os.path.join( root, file )
                exclude = False
                for ex in excludes:
                    ex = os.path.join( cache_path, ex )
                    if ( not ex.endswith( "/" ) ) and ( ex in fpath ):
                        exclude = True
                        break
                if not exclude:
                    t_file += 1
                    DIALOG_PROGRESS.update( -1, _( 32651 ) % ( t_file, t_dir, ), _( 32652 ) % root, _( 32653 ) % file )
                    try:
                        os.remove( fpath )
                        print "[SCRIPT IPX] Caches Cleaner::clear: '%s'" % fpath
                    except:
                        print_exc()

            for dir in dirs:
                dpath = os.path.join( root, dir )
                exclude = False
                for ex in excludes:
                    ex = os.path.join( cache_path, ex )
                    if ( ex.strip( "/" ) in dpath ):
                        exclude = True
                        break
                if not exclude:
                    t_dir += 1
                    DIALOG_PROGRESS.update( -1, _( 32651 ) % ( t_file, t_dir, ), _( 32652 ) % root, _( 32653 ) % dir )
                    try:
                        os.rmdir( dpath )
                        print "[SCRIPT IPX] Caches Cleaner::clear: '%s'" % dpath
                    except:
                        print_exc()
    except:
        print_exc()
    return t_file, t_dir


def Main():
    cache_list = [_ ( 32654 ), _( 32662 ), _( 32655 ),
        _( 32656 ) % xbmc.translatePath( "special://temp/" ),
        _( 32656 ) % xbmc.translatePath( "special://profile/cache/" ) ]
    if os.environ.get( "OS", "xbox" ) == "xbox":
        cache_list += [ _( 32657 ), _( 32658 ) ]
    selected = xbmcgui.Dialog().select( _( 32660 ), cache_list )

    if selected != -1:
        t_file, t_dir = 0, 0
        excludes = [ "weather", "temp/" ]
        DIALOG_PROGRESS.create( _( 32659 ) )
        if selected in [ 0, 1 ]:
            t_file, t_dir = clear( os.path.join( home_dir, "~" ), [], t_file, t_dir )
            t_file, t_dir = clear( os.path.join( home_dir, "cache" ), [], t_file, t_dir )
            t_file, t_dir = clear( xbmc.translatePath( "special://profile/script_data/Installer Passion-XBMC/" ), [], t_file, t_dir )
            t_file, t_dir = clear( xbmc.translatePath( "special://profile/script_data/Installer Passion-XBMC Web/" ), [], t_file, t_dir )

        if selected in [ 0, 2, 3 ]:
            t_file, t_dir = clear( xbmc.translatePath( "special://temp/" ), excludes, t_file, t_dir )

        if selected in [ 0, 2, 4 ]:
            t_file, t_dir = clear( xbmc.translatePath( "special://profile/cache/" ), [], t_file, t_dir )

        if os.environ.get( "OS", "xbox" ) == "xbox":
            if selected in [ 0, 5 ]:
                t_file, t_dir = clear( "E:\\CACHE\\", [], t_file, t_dir )

            if selected in [ 0, 6 ]:
                t_file, t_dir = clear( "X:\\", [], t_file, t_dir )
                t_file, t_dir = clear( "Y:\\", [], t_file, t_dir )
                t_file, t_dir = clear( "Z:\\", excludes, t_file, t_dir )
        DIALOG_PROGRESS.close()
        xbmcgui.Dialog().ok( _( 32660 ), cache_list[ selected ], _( 32651 ) % ( t_file, t_dir, ) )



if ( __name__ == "__main__" ):
    Main()
