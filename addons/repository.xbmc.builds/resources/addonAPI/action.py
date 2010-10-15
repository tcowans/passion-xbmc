
#Modules General
import os
import sys
from traceback import print_exc


def startfile( filepath, operation="" ):
    """startfile(...)
        startfile(filepath [, operation]) - Start a file with its associated application.

        When operation is not specified or 'open', this acts like
        double-clicking the file in Windows Explorer, or giving the file name as an
        argument to the start command from the interactive command shell:
        the file is opened with whatever application (if any) its extension is associated.

        When another operation is given, it must be a ''command verb'' that specifies what
        should be done with the file. Common verbs documented by Microsoft are 'print' and 'edit'
        (to be used on files) as well as 'explore' and 'find' (to be used on directories).

        startfile() returns as soon as the associated application is launched.
        There is no option to wait for the application to close, and no way to
        retrieve the application's exit status. The path parameter is relative to
        the current directory. If you want to use an absolute path, make sure the first character
        is not a slash ("/"); the underlying Win32 ShellExecute() function doesn't work if it is.
        Use the os.path.normpath() function to ensure that the path is properly encoded for Win32.
        Availability: Windows. New in version 2.0. New in version 2.5: The operation parameter.
    """
    if sys.platform == "win32":
        #WINDOWS ONLY
        if sys.version[ :3 ] < "2.5":
            os.startfile( filepath )
        else:
            os.startfile( filepath, operation )
    else:
        if sys.platform == "darwin":
            # MAC
            command = [ "open", ]
            def raise_error( code ):
                # XXX
                # need implemented
                raise OSError
        else:
            # LINUX
            command = [ "xdg-open", ]
            def raise_error( code ):
                err = {
                    1: errno.EINVAL,
                    2: errno.ENOENT,
                    3: errno.ENOEXEC,
                    # XXX
                    4: errno.ENOEXEC,
                    5: errno.EACCES,
                    6: errno.EACCES,
                    }[ code ]
                raise OSError( err, strerror( err ) )
        if operation:
            command.append( operation )
        command.append( filepath )
        import subprocess
        retcode = subprocess.call( command )
        if retcode:
            raise_error( retcode )


def start_file( filepath, operation="", kill_xbmc=False ):
    """startfile(...)
        start_file(filepath [, operation, kill_xbmc]) - Start a file with its associated application.
        operation: string - use print os.startfile.__doc__ or help(os.startfile) for more infos...
        kill_xbmc: bool - default=False ( kill xbmc process )
    """
    try:
        # launch any file
        startfile( filepath, operation )
        #force close xbmc kill this
        if kill_xbmc:
            if sys.platform == "win32":
                #windows command kill process
                #print os.path.basename( sys.executable )
                os.system( "TaskKill /IM:XBMC.exe /F" )
            elif sys.platform == "darwin":
                #mac command
                xbmc.executebuiltin( "Quit" )
            else:
                #linux command
                pass
                xbmc.executebuiltin( "Quit" )
    except:
        print_exc()


def get_browse_dialog( default="", heading="", dlg_type=1, shares="files", mask="", use_thumbs=False, treat_as_folder=False ):
    """ shows a browse dialog and returns a value
        - 0 : ShowAndGetDirectory
        - 1 : ShowAndGetFile
        - 2 : ShowAndGetImage
        - 3 : ShowAndGetWriteableDirectory
    """
    import xbmcgui
    dialog = xbmcgui.Dialog()
    value = dialog.browse( dlg_type, heading, shares, mask, use_thumbs, treat_as_folder, default )
    return value


class _Info:
    def __init__( self, *args, **kwargs ):
        # update dict with our formatted argv
        try: exec "self.__dict__.update(%s)" % ( sys.argv[ 2 ][ 1: ].replace( "&", ", " ), )
        except: print_exc()
        # update dict with custom kwargs
        self.__dict__.update( kwargs )

    def get( self, key, default="" ):
        return self.__dict__.get( key, default )

    def isempty( self ):
        return not bool( self.__dict__ )


def Main():
    import xbmc
    import xbmcgui
    try:
        #xbmcgui.lock()
        args = _Info()

        fpath = None
        kill_xbmc = False

        if ( args.get( "action" ) == "DL" ):
            #run downloader
            dlpath = xbmc.getInfoLabel( "ListItem.Property(Addon.Path)" )
            filename = xbmc.getInfoLabel( "ListItem.Property(filename)" )
            print "DL: %s" % dlpath
            try:
                script = os.path.join( os.getcwd(), "resources", "addonAPI", "downloader.py" )
                xbmc.executebuiltin( "RunScript(%s,%s,%s)" % ( script, dlpath, filename ) )
            except:
                print_exc()

        elif ( args.get( "action" ) == "browse" ):
            #browse for custom setup install
            fpath = get_browse_dialog( heading="Update from custom build", mask=( "", ".exe|.bat" )[ sys.platform == "win32" ] )
            if fpath:
                fpath = fpath
                kill_xbmc = True
            print "Custom file: %s" % fpath

        elif ( args.get( "action" ) == "open" ):
            # open file with default web navigator
            fpath = xbmc.getInfoLabel( "ListItem.Property(Addon.Path)" )

        elif ( args.get( "action" ) == "visitrepo" ):
            # visit repo with default web navigator
            from repo import repo_url as fpath

        elif ( args.get( "action" ) == "visitunorepo" ):
            fpath = "http://www.sshcs.com/xbmc/"

        #if kill_xbmc:
            #xbmcgui.unlock()
        if fpath:
            start_file( fpath.decode( "utf-8" ), kill_xbmc=kill_xbmc )
    except:
        print_exc()
    #xbmcgui.unlock()

if ( __name__ == "__main__" ):
    start_file( "special://home/xbmc.log" )
