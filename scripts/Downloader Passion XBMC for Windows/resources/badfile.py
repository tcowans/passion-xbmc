
import os
import sys
import xbmc
import xbmcgui
from traceback import print_exc


def remove_file( filepath, remove_tries=3 ):
    try:
        while remove_tries and os.path.isfile( filepath ):
            try:
                os.remove( filepath )
                print "File Removed: [%s]" % filepath
            except:
                #print_exc()
                remove_tries -= 1
                xbmc.sleep( 1000 )
    except:
        print_exc()


def Main():
    try:
        """ { 'filepath': stackpath or filepath, 'remove_tries': 3 is default } """
        args = dict( [ arg.split( "=" ) for arg in sys.argv[ 1 ].split( "&&" ) ] )
        remove_tries = int( args.get( "remove_tries", "3" ) )
        filepath = args.get( "filepath", "" ).strip().replace( "stack://", "" ).split( " , " )
        print "Removing File: [%s]" % repr( args )
        diff = ( 100.0 / len( filepath ) )
        plsw = xbmc.getLocalizedString( 20186 )
        xbmc.sleep( 600 )
        for count, file in enumerate( filepath ):
            percent = ( ( count + 1 ) * diff )
            if file:
                remove_file( file, remove_tries )
                DIALOG_PROGRESS.update( int( percent ), file, plsw )
            DIALOG_PROGRESS.update( int( percent ) )
    except:
        print_exc()


if __name__ == "__main__":
    DIALOG_PROGRESS = xbmcgui.DialogProgress()
    DIALOG_PROGRESS.create( "Badfile..." )
    Main()
    DIALOG_PROGRESS.close()
