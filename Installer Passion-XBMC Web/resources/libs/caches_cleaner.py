
# Modules general
import os
from traceback import print_exc

# Modules XBMC
import xbmc
import xbmcgui

# Modules custom
import custom_sys_stdout_stderr as output


DIALOG_PROGRESS = xbmcgui.DialogProgress()


par_dir = "../../"
home_dir = os.sep.join( os.getcwd().split( os.sep )[ :-par_dir.count( "../" ) ] )


def clear( cache_path, excludes=[], t_file=0, t_dir=0 ):
    try:
        DIALOG_PROGRESS.update( -1, xbmc.getLocalizedString( 32650 ) % cache_path )
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
                    DIALOG_PROGRESS.update( -1, xbmc.getLocalizedString( 32651 ) % ( t_file, t_dir, ), xbmc.getLocalizedString( 32652 ) % root, xbmc.getLocalizedString( 32653 ) % file )
                    try:
                        os.remove( fpath )
                        xbmc.log( "[SCRIPT IPX] Caches Cleaner::clear: '%s'" % fpath, xbmc.LOGDEBUG )
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
                    DIALOG_PROGRESS.update( -1, xbmc.getLocalizedString( 32651 ) % ( t_file, t_dir, ), xbmc.getLocalizedString( 32652 ) % root, xbmc.getLocalizedString( 32653 ) % dir )
                    try:
                        os.rmdir( dpath )
                        xbmc.log( "[SCRIPT IPX] Caches Cleaner::clear: '%s'" % dpath, xbmc.LOGDEBUG )
                    except:
                        print_exc()
    except:
        print_exc()
    return t_file, t_dir


def Main():
    cache_list = [
        xbmc.getLocalizedString( 32654 ),
        xbmc.getLocalizedString( 32662 ),
        xbmc.getLocalizedString( 32655 ),
        xbmc.getLocalizedString( 32656 ) % xbmc.translatePath( "special://temp/" ),
        xbmc.getLocalizedString( 32656 ) % xbmc.translatePath( "special://profile/cache/" ) ]
    if os.environ.get( "OS", "xbox" ) == "xbox":
        cache_list += [
            xbmc.getLocalizedString( 32657 ),
            xbmc.getLocalizedString( 32658 ) ]
    selected = xbmcgui.Dialog().select( xbmc.getLocalizedString( 32660 ), cache_list )

    if selected != -1:
        t_file, t_dir = 0, 0
        excludes = [ "weather", "temp/" ]
        DIALOG_PROGRESS.create( xbmc.getLocalizedString( 32659 ) )
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
        xbmcgui.Dialog().ok( xbmc.getLocalizedString( 32660 ), cache_list[ selected ], xbmc.getLocalizedString( 32651 ) % ( t_file, t_dir, ) )



if ( __name__ == "__main__" ):
    Main()

    # replace standard stdout and stderr, modified by import custom_sys_stdout_stderr
    #sys.stdout = sys.stdout.terminal
    #sys.stderr = sys.stderr.terminal
