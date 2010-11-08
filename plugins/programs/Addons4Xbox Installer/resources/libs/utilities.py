"""
Module de partage des fonctions et des constantes

"""

#En gros seul les fonctions et variables de __all__ vont etre importees lors du "import *"
#The public names defined by a module are determined by checking the module's namespace
#for a variable named __all__; if defined, it must be a sequence of strings which are names defined
#or imported by that module. The names given in __all__ are all considered public and are required to exist.
#If __all__ is not defined, the set of public names includes all names found in the module's namespace
#which do not begin with an underscore character ("_"). __all__ should contain the entire public API.
#It is intended to avoid accidentally exporting items that are not part of the API (such as library modules
#which were imported and used within the module).
__all__ = [
    # public names
    "copy_dir",
    "copy_inside_dir",
    "SYSTEM_PLATFORM",
    "readURL",
    "add_pretty_color",
    "bold_text",
    "italic_text",
    "set_xbmc_carriage_return",
    "unescape",
    "strip_off",
    "get_infos_path",
    "replaceStrs",
    "set_cache_thumb_name",
    ]

#Modules general
import os
import re
import sys
import time
import htmllib
import urllib

from traceback import print_exc

#modules XBMC
import xbmc
import xbmcgui

# Modules Custom
import shutil2


#REPERTOIRE RACINE ( default.py )
CWD = os.getcwd().rstrip( ";" )

BASE_SETTINGS_PATH = os.path.join( sys.modules[ "__main__" ].SPECIAL_SCRIPT_DATA, "settings.txt" )
RSS_FEEDS_XML = os.path.join( CWD, "resources", "RssFeeds.xml" )

BASE_THUMBS_PATH = os.path.join( sys.modules[ "__main__" ].SPECIAL_SCRIPT_DATA, "Thumbnails" )


def copy_dir( dirname, destination, overwrite=True ):
    if not overwrite and os.path.isdir( destination ):
        shutil2.rmtree( destination )
    shutil2.copytree( dirname, destination, overwrite=overwrite )


def copy_inside_dir( dirname, destination, overwrite=True ):
    list_dir = os.listdir( dirname )
    for file in list_dir:
        src = os.path.join( dirname, file )
        dst = os.path.join( destination, file )
        if os.path.isfile( src ):
            if not os.path.isdir( os.path.dirname( dst ) ):
                os.makedirs( os.path.dirname( dst ) )
            if not overwrite and os.path.isfile( dst ):
                os.unlink( dst )
            shutil2.copyfile( src, dst, overwrite=overwrite )
        elif os.path.isdir( src ):
            if not overwrite and os.path.isdir( dst ):
                shutil2.rmtree( dst )
            shutil2.copytree( src, dst, overwrite=overwrite )


def readURL( url, save=False, localPath=None ):
    print"readURL() url=%s"%url
    urlData = ""
    if url:
        try:
            urlData = urllib.urlopen(url).read()
            if ( "404 Not Found" in urlData ):
                print "readURL() 404, Not found"
                urlData = ""
            if save:
                open(localPath,"w").write(urlData)
        except:
            print("readURL() %s" % sys.exc_info()[ 1 ])
    return urlData




def set_cache_thumb_name( path ):
    try:
        fpath = path
        # make the proper cache filename and path so duplicate caching is unnecessary
        filename = xbmc.getCacheThumbName( fpath )
        thumbnail = os.path.join( BASE_THUMBS_PATH, filename[ 0 ], filename )
        preview_pic = os.path.join( BASE_THUMBS_PATH, "originals", filename[ 0 ], filename )
        # if the cached thumbnail does not exist check for dir does not exist create dir
        if not os.path.isdir( os.path.dirname( preview_pic ) ):
            os.makedirs( os.path.dirname( preview_pic ) )
        if not os.path.isdir( os.path.dirname( thumbnail ) ):
            os.makedirs( os.path.dirname( thumbnail ) )
        return thumbnail, preview_pic
    except:
        print_exc()
        return "", ""

def get_system_platform():
    """ fonction: pour recuperer la platform que xbmc tourne """
    platform = "unknown"
    if xbmc.getCondVisibility( "system.platform.linux" ):
        platform = "linux"
    elif xbmc.getCondVisibility( "system.platform.xbox" ):
        platform = "xbox"
    elif xbmc.getCondVisibility( "system.platform.windows" ):
        platform = "windows"
    elif xbmc.getCondVisibility( "system.platform.osx" ):
        platform = "osx"
    return platform

SYSTEM_PLATFORM = get_system_platform()


#NOTE: CE CODE PEUT ETRE REMPLACER PAR UN CODE MIEUX FAIT
def add_pretty_color( word, start="all", end=None, color=None ):
    """ FONCTION POUR METTRE EN COULEUR UN MOT OU UNE PARTIE """
    try:
        if color and start == "all":
            pretty_word = "[COLOR=" + color + "]" + word + "[/COLOR]"
        else:
            pretty_word = []
            for letter in word:
                if color and letter == start:
                    pretty_word.append( "[COLOR=" + color + "]" )
                elif color and letter == end:
                    pretty_word.append( letter )
                    pretty_word.append( "[/COLOR]" )
                    continue
                pretty_word.append( letter )
            pretty_word = "".join( pretty_word )
        return pretty_word
    except:
        print_exc()
        return word


def bold_text( text ):
    """ FONCTION POUR METTRE UN MOT GRAS """
    return "[B]%s[/B]" % ( text, )


def italic_text( text ):
    """ FONCTION POUR METTRE UN MOT ITALIQUE """
    return "[I]%s[/I]" % ( text, )


def set_xbmc_carriage_return( text ):
    """ only for xbmc """
    text = text.replace( "\r\n", "[CR]" )
    text = text.replace( "\n\n", "[CR]" )
    text = text.replace( "\n",   "[CR]" )
    text = text.replace( "\r\r", "[CR]" )
    text = text.replace( "\r",   "[CR]" )
    text = text.replace( "</br>",   "[CR]" )
    return text


def strip_off( text, by="", xbmc_labels_formatting=False ):
    """ FONCTION POUR RECUPERER UN TEXTE D'UN TAG """
    if xbmc_labels_formatting:
        #text = re.sub( "\[url[^>]*?\]|\[/url\]", by, text )
        text = text.replace( "[", "<" ).replace( "]", ">" )
    return re.sub( "(?s)<[^>]*>", by, text )

def unescape(s):
    """
    remplace les sequences d'echappement par leurs caracteres equivalent
    """
    p = htmllib.HTMLParser(None)
    p.save_bgn()
    p.feed(s)
    return p.save_end()

def replaceStrs( s, *args ): 
    """
    Replace all ``(frm, to)`` tuples in `args` in string `s`.
    By Alexander Schmolck ( http://markmail.org/message/r67z77skcqcbo5nr )
    replaceStrs("nothing is better than warm beer", ... ('nothing','warm beer'), ('warm beer','nothing')) 'warm beer is better than nothing'
    """ 
    if args == (): 
        return s 
    mapping = dict([(frm, to) for frm, to in args]) 
    return re.sub("|".join(map(re.escape, mapping.keys())), lambda match:mapping[match.group(0)], s)
    


def get_infos_path( path, get_size=False, report_progress=None ):
    # Return the system's ctime which, on some systems (like Unix) is the time of the last change, and, on others (like Windows), is the creation time for path. The return value is a number giving the number of seconds since the epoch (see the time module). Raise os.error if the file does not exist or is inaccessible. New in version 2.3.
    try: c_time = time.strftime( DATE_TIME_FORMAT, time.localtime( os.path.getctime( path ) ) )#.replace( " | 0", " |  " )
    except: c_time = ""

    # Return the time of last access of path. The return value is a number giving the number of seconds since the epoch (see the time module). Raise os.error if the file does not exist or is inaccessible. New in version 1.5.2. Changed in version 2.3: If os.stat_float_times() returns True, the result is a floating point number.
    try: last_access = time.strftime( DATE_TIME_FORMAT, time.localtime( os.path.getatime( path ) ) )#.replace( " | 0", " |  " )
    except: last_access = ""

    # Return the time of last modification of path. The return value is a number giving the number of seconds since the epoch (see the time module). Raise os.error if the file does not exist or is inaccessible. New in version 1.5.2. Changed in version 2.3: If os.stat_float_times() returns True, the result is a floating point number.
    try: last_modification = time.strftime( DATE_TIME_FORMAT, time.localtime( os.path.getmtime( path ) ) )#.replace( " | 0", " |  " )
    except: last_modification = ""

    # Return the size, in bytes, of path. Raise os.error if the file does not exist or is inaccessible. New in version 1.5.2.
    # calculate dir size "os.walk( path, topdown=False )"
    try:
        size = 0
        if os.access( path, os.R_OK ):
            if os.path.isfile( path ):
                try:
                    size += os.path.getsize( path )
                    if report_progress:
                        #print "Size: %s", path
                        report_progress.update( -1, sys.modules[ "__main__" ].__language__( 186 ), path, sys.modules[ "__main__" ].__language__( 361 ) + " %00s KB" % round( size / 1024.0, 2 ) )
                except: pass
            elif get_size:
                for root, dirs, files in os.walk( path ):#, topdown=False ):
                    for file in files:
                        try:
                            fpath = os.path.join( root, file )
                            if os.access( fpath, os.R_OK ):
                                size += os.path.getsize( fpath )
                                if report_progress:
                                    #print "Size: %s", fpath
                                    report_progress.update( -1, sys.modules[ "__main__" ].__language__( 186 ), fpath, sys.modules[ "__main__" ].__language__( 361 ) + " %00s KB" % round( size / 1024.0, 2 ) )
                        except:
                            print "Size: %s" % fpath
        if size <= 0:
            size = ""#"0.0 KB"
        elif size <= ( 1024.0 * 1024.0 ):
            size = "%00s KB" % round( size / 1024.0, 2 )
        elif size >= ( 1024.0 * 1024.0 ):
            size = "%00s MB" % round( size / 1024.0 / 1024.0, 2 )
        else:
            size = "%00s Bytes" % size
    except:
        print_exc()
        size = "0.0 KB"

    return size, c_time, last_access, last_modification
