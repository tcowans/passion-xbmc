
# script constants
__script__       = "Skins Nightly Builds"
__author__       = "Frost"
__url__          = "http://code.google.com/p/passion-xbmc/"
__svn_url__      = "http://passion-xbmc.googlecode.com/svn/trunk/scripts/"
__credits__      = "Team XBMC, http://xbmc.org/"
__platform__     = "xbmc media center, [LINUX, OS X, WIN32, XBOX]"
__date__         = "07-08-2009"
__version__      = "1.0.0-beta1"
__svn_revision__  = "$Revision$"
__XBMC_Revision__ = "20000" #XBMC Babylon


import os
import re
import glob
import urllib
from traceback import print_exc

import xbmc
import xbmcgui


CWD = os.getcwd().rstrip( ";" )
CACHE_DIR = os.path.join( CWD, "cache" )
try:
    if xbmc.Settings( CWD ).getSetting( "mode" ) == "1":
        CACHE_DIR = xbmc.translatePath( "special://profile/script_data/%s/cache/" % __script__ )
except:
    print_exc()
if not os.path.isdir( CACHE_DIR ):
    os.makedirs( CACHE_DIR )

skin_path = xbmc.translatePath( "special://skin/" )
cur_skin = os.path.basename( os.path.dirname( skin_path ) )
skins_path = os.path.dirname( os.path.dirname( skin_path )  )

GET_LOCALIZED_STRING = xbmc.Language( CWD ).getLocalizedString

DIALOG_PROGRESS = xbmcgui.DialogProgress()

base_url = "http://www.sshcs.com"
skins_url = base_url + "/xbmc/inc/eva.asp?mode=Skins"

aeon_passion = {
    "name": "aeon-passion",
    "build": "Build r.OnClick",
    "hit": "",
    "rate": "10 / 10",
    "thumbs": os.path.join( CACHE_DIR, "Aeon" ),
    "dl": "http://github.com/Imaginos/aeon-passion/zipball/master",
    "type": ".zip"
    }



class pDialogCanceled( Exception ):
    def __init__( self, errmsg="Downloading was canceled by user!" ):
        self.msg = errmsg


def getUserSkin():
    current_skin = xbmc.getSkinDir()
    force_fallback = os.path.exists( os.path.join( CWD, "resources", "skins", current_skin ) )
    if not force_fallback: current_skin = "Default"
    return current_skin, force_fallback


def get_browse_dialog( default="", heading="", dlg_type=3, shares="files", mask="", use_thumbs=False, treat_as_folder=False ):
    """ shows a browse dialog and returns a value
        - 0 : ShowAndGetDirectory
        - 1 : ShowAndGetFile
        - 2 : ShowAndGetImage
        - 3 : ShowAndGetWriteableDirectory
    """
    dialog = xbmcgui.Dialog()
    value = dialog.browse( dlg_type, heading, shares, mask, use_thumbs, treat_as_folder, default )
    return value


def dl_build( heading, url, destination ):
    DIALOG_PROGRESS.create( heading, GET_LOCALIZED_STRING( 32890 ) )
    filepath = ""
    try:
        def _report_hook( count, blocksize, totalsize ):
            _line3_ = ""
            if totalsize > 0:
                _line3_ += GET_LOCALIZED_STRING( 32840 ) % ( ( ( count * blocksize ) / 1024.0 / 1024.0 ), ( totalsize / 1024.0 / 1024.0  ), )
            else:
                _line3_ += GET_LOCALIZED_STRING( 32841 ) % ( ( ( count * blocksize ) / 1024.0 / 1024.0 ), )
            percent = int( float( count * blocksize * 100 ) / totalsize )
            strProgressBar = str( percent )
            if ( percent <= 0 ) or not strProgressBar: strPercent = "0%"
            else: strPercent = "%s%%" % ( strProgressBar, )
            _line3_ += " | %s" % ( strPercent, )
            #DIALOG_PROGRESS.update( percent, url, destination, _line3_ )
            DIALOG_PROGRESS.update( percent, _line3_, destination, GET_LOCALIZED_STRING( 32890 ) )
            if ( DIALOG_PROGRESS.iscanceled() ):
                raise pDialogCanceled()
        fp, h = urllib.urlretrieve( url, destination, _report_hook )
        if h:
            #print h
            try:
                if "text" in h[ "Content-Type" ]:
                    os.unlink( destination )
            except:
                print_exc()
        filepath = fp
    except pDialogCanceled, error:
        print error.msg
        filepath = ""
    except:
        print_exc()
        filepath = ""
    DIALOG_PROGRESS.close()
    return filepath


def get_nightly_skins():
    results = []
    try:
        asp = urllib.urlopen( skins_url, "r" ).read()
        skins = re.compile( '<div class="thumbnails" style="float:left;">(.*?)<hr />', re.DOTALL ).findall( asp )
        for count, skin in enumerate( skins ):
            try:
                infos, dl = re.findall( '<span class="cleanlinks">&nbsp;&nbsp;&nbsp;(.*?)<a href="(.*?)">Download</a>', skin )[ 0 ]
                name, build, hit = infos.strip( " |" ).split( " | " )
                dl = base_url + dl
                rate = str( re.findall( '<img src="(.*?)" border="0" />', skin ).count( "/xbmc/img/goldstar.png" ) ) + " / 10"
                thumbs = [ base_url + uri for uri in re.findall( '<a href="(.*?)" class="floatbox" title=".*?" rev=".*?">', skin ) ]
                results.append( { "name": name, "build": build, "hit": hit, "rate": rate, "thumbs": thumbs, "dl": dl } )
            except:
                print_exc()
    except:
        print_exc()
    return results


class nightly( xbmcgui.WindowXML ):
    def __init__( self, *args, **kwargs ):
        xbmcgui.WindowXML.__init__( self, *args, **kwargs )
        self.save_dir = ""

        DIALOG_PROGRESS.create( __script__, GET_LOCALIZED_STRING( 32890 ) )
        DIALOG_PROGRESS.update( 100, GET_LOCALIZED_STRING( 32890 ) )
        try:
            self.skins = get_nightly_skins()
            self.skins.append( aeon_passion )
            #trie la liste selon la valeur de rate eval( "10 / 10") va donner 1
            try: self.skins.sort( key=lambda s: eval( s[ "rate" ] ), reverse=True )
            except: pass
        except:
            print_exc()
            DIALOG_PROGRESS.close()
            raise
        DIALOG_PROGRESS.close()

    def onInit( self ):
        #DIALOG_PROGRESS.create( __script__, GET_LOCALIZED_STRING( 32890 ) )
        #DIALOG_PROGRESS.update( 100, GET_LOCALIZED_STRING( 32890 ) )
        try:
            xbmcgui.lock()
            #self.skins = get_nightly_skins()
            #self.skins.append( aeon_passion )
            #trie la liste selon la valeur de rate eval( "10 / 10") va donner 1
            #try: self.skins.sort( key=lambda s: eval( s[ "rate" ] ), reverse=True )
            #except: pass
            total_items = len( self.skins )
            try: diff = int( 100.0 / total_items )
            except: diff = 100
            percent = 0
            for count, skin in enumerate( self.skins ):
                # { "name": name, "build": build, "hit": hit, "rate": rate, "thumbs": thumbs, "dl": dl }
                #name = " | ".join( [ skin[ "name" ], skin[ "build" ], skin[ "hit" ], skin[ "rate" ]  ] )
                percent += diff
                #DIALOG_PROGRESS.update( percent, "Skins: %i / %i" % ( count+1, total_items ), skin[ "name" ] )

                listitem = xbmcgui.ListItem( skin[ "name" ] )

                listitem.setProperty( "build", skin[ "build" ] )
                listitem.setProperty( "hit", skin[ "hit" ] )
                listitem.setProperty( "rate", skin[ "rate" ] )

                thumbs = self.get_thumbnails( skin[ "name" ], skin[ "thumbs" ] )
                listitem.setProperty( "thumbs", thumbs )

                self.getControl( 450 ).addItem( listitem )
        except:
            print_exc()
        #DIALOG_PROGRESS.close()
        xbmcgui.unlock()

    def get_thumbnails( self, skin, thumbs=[] ):
        local_dir = ""
        try:
            if thumbs == aeon_passion.get( "thumbs" ):
                return thumbs
            for thumb in thumbs:
                dname = os.path.basename( os.path.dirname( thumb ) )
                fname = os.path.basename( thumb )
                local_dir = os.path.join( CACHE_DIR, dname )
                if not os.path.isdir( local_dir ):
                    os.makedirs( local_dir )
                fpath = os.path.join( local_dir, fname )
                if ( not os.path.isfile( fpath ) ):
                    DIALOG_PROGRESS.update( -1, skin, os.path.join( dname, fname ), GET_LOCALIZED_STRING( 32890 ) )
                    urllib.urlretrieve( thumb, fpath )
        except:
            print_exc()
        return local_dir

    def onFocus( self, controlID ):
        pass

    def onClick( self, controlID ):
        try:
            if controlID == 450:
                pos = self.getControl( 450 ).getSelectedPosition()
                url = self.skins[ pos ][ "dl" ]
                heading = ", ".join( [ self.skins[ pos ][ "name" ], self.skins[ pos ][ "build" ] ] )
                dpath = get_browse_dialog( default=self.save_dir, heading=GET_LOCALIZED_STRING( 32100 ) )
                if dpath:
                    ext = self.skins[ pos ].get( "type", ".rar" )
                    fpath = os.path.join( dpath, self.skins[ pos ][ "name" ] + ext )
                    if xbmcgui.Dialog().yesno( heading, GET_LOCALIZED_STRING( 32130 ), GET_LOCALIZED_STRING( 32140 ), fpath ):
                        filename = dl_build( heading, url, fpath )#fpath
                        if filename and ( not self.skins[ pos ][ "name" ] in ( cur_skin, xbmc.getSkinDir() ) ):# or ( os.environ.get( "OS", "xbox" ) != "xbox" ):
                            xbmcgui.Dialog().ok( GET_LOCALIZED_STRING( 32200 ), GET_LOCALIZED_STRING( 32210 ), GET_LOCALIZED_STRING( 32220 ) % xbmc.getFreeMem(), GET_LOCALIZED_STRING( 32230 ) % ( ( os.path.getsize( filename ) / 1024.0 / 1024.0 ) * 1.5 ) )
                            if xbmc.getFreeMem() >= ( ( os.path.getsize( filename ) / 1024.0 / 1024.0 ) * 1.5 ):
                                DIALOG_PROGRESS.create( heading, "Extracting...", filename, skins_path )
                                xbmc.executebuiltin( 'XBMC.Extract(%s,%s)' % ( filename, skins_path, ) )
                                DIALOG_PROGRESS.close()
                                skin_name = self.skins[ pos ][ "name" ]
                                if skin_name == "aeon-passion":
                                     new_name = self.set_aeon_passion()
                                     if new_name: skin_name = new_name
                                xbmcgui.Dialog().ok( __script__, GET_LOCALIZED_STRING( 32110 ), skins_path, skin_name )
                            else:
                                xbmcgui.Dialog().ok( GET_LOCALIZED_STRING( 32200 ), GET_LOCALIZED_STRING( 32210 ), GET_LOCALIZED_STRING( 32220 ) % xbmc.getFreeMem(), GET_LOCALIZED_STRING( 32230 ) % ( ( os.path.getsize( filename ) / 1024.0 / 1024.0 ) * 1.5 ) )
                self.save_dir = dpath
        except:
            print_exc()

    def onAction( self, action ):
        if action in ( 9, 10 ):
            self.close()

    def set_aeon_passion( self ):
        new_name = ""
        try:
            last_aeon_passion = sorted( glob.glob( os.path.join( skins_path, "Imaginos-aeon-passion-*" ) ),
                key=lambda s: os.path.getmtime( s ), reverse=True )
            last_aeon_passion = ( last_aeon_passion or [ "" ] )[ 0 ]
            if last_aeon_passion and os.path.exists( last_aeon_passion ):
                if not os.path.exists( os.path.join( skins_path, "aeon-passion" ) ):
                    base = "aeon-passion"
                else:
                    base = os.path.basename( last_aeon_passion )
                while True:
                    new_name = ""
                    keyboard = xbmc.Keyboard( base, GET_LOCALIZED_STRING( 32120 ) )
                    keyboard.doModal()
                    if keyboard.isConfirmed():
                        new_name = keyboard.getText()
                        fpath = os.path.join( skins_path, new_name )
                        if ( new_name != os.path.basename( last_aeon_passion ) ) and not os.path.exists( fpath ):
                            #print last_aeon_passion
                            #print fpath
                            os.rename( last_aeon_passion, fpath )
                            break
                        new_name = ""
                    else:
                        print "set_aeon_passion:name:canceled!"
                        break
                if not new_name:
                    new_name = base
        except:
            print_exc()
        return new_name



if  __name__ == "__main__":
    current_skin, force_fallback = getUserSkin()
    w = nightly( "nightly.xml", CWD, current_skin, force_fallback )
    w.doModal()
    del w
