
# Modules general
import os
import sys
from traceback import print_exc


def RUN_PERFORMANCE():
    try:
        # replace standard stdout and stderr, modified by import custom_sys_stdout_stderr in __main__
        sys.stdout = sys.stdout.terminal
        sys.stderr = sys.stderr.terminal
    except:
        print_exc()
    try:
        import profile, pstats
        report_file = os.path.join( os.getcwd(), "MainPerform.profile.log" )
        profile.run( 'sys.modules[ "__main__" ].MAIN()', report_file )
        pstats.Stats( report_file ).sort_stats( "time", "name" ).print_stats()
    except:
        print_exc()


def RUN_UNIT_TEST():
    try:
        DIALOG_PROGRESS = sys.modules[ "__main__" ].DIALOG_PROGRESS
        __language__ = sys.modules[ "__main__" ].__language__
        # LOADING CONF
        print "bypass_debug: Starting UNIT TESTS"
        import CONF
        config = CONF.ReadConfig()

        DIALOG_PROGRESS.update( -1, __language__( 101 ), __language__( 110 ) )
        if not config.getboolean( 'InstallPath', 'pathok' ):
            CONF.SetConfiguration()
        config = CONF.ReadConfig()
        del CONF

        # UNIT TEST
        
        # Write your unit tests Here
        # ...
        # ...
        print "bypass_debug: Tests done"
    except:
        print "bypass_debug: Tests error..."
        print_exc()
    DIALOG_PROGRESS.close()
