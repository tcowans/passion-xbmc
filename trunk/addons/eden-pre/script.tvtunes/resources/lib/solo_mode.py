# -*- coding: utf-8 -*-

import time
START_TIME = time.time()

import urllib

# General Import's
from common import *
from utils import remote_utils


scrap_dir = os.path.join( xbmc.translatePath( AddonPath ), "resources", "scrapers", Addon.getSetting( "scraper" ) )
if not path_exists( scrap_dir ): scrap_dir = scrap_dir.replace( Addon.getSetting( "scraper" ), "TelevisionTunes" )
sys.path.append( scrap_dir )
import scraper

addon_temp = xbmc.translatePath( AddonData + 'temp' )
if not path_exists( addon_temp ): os.makedirs( addon_temp )

DIALOG_PROGRESS = xbmcgui.DialogProgress()

# set params and get sys.argv
params = Info()
g_TVShowTitle     = xbmc.getInfoLabel( "ListItem.TVShowTitle" )
g_FilenameAndPath = xbmc.getInfoLabel( "ListItem.FilenameAndPath" ) or xbmc.getInfoLabel( "ListItem.Path" ) # get ListItem.Path probably solo mode called from contextmenu

formatting       = IsTrue( Addon.getSetting( "formatting" ) )
upper_formatting = IsTrue( Addon.getSetting( "upper_formatting" ) )
style_formatting = Addon.getSetting( "style_formatting" )
color_formatting = Addon.getSetting( "color_formatting" )
def setPrettyFormatting( text, text2 ):
    # set matching name, if user prefer this
    try:
        if formatting:
            user_prefer = text
            # set bold text
            if style_formatting in [ "1", "3" ]:
                user_prefer = "[B]%s[/B]" % ( user_prefer, )

            # set italic text
            if style_formatting in [ "2", "3" ]:
                user_prefer = "[I]%s[/I]" % ( user_prefer, )

            # set text to uppercase
            if upper_formatting:
                user_prefer = "[UPPERCASE]%s[/UPPERCASE]" % ( user_prefer, )

            #set colored text
            if color_formatting != "Default" and "COLOR=" in color_formatting:
                user_prefer = "%s]%s[/COLOR]" % ( color_formatting.split( "]" )[ 0 ], user_prefer, )

            # set Formatting
            txt = "%s" % "|".join( [ text, text.lower(), text.upper(), text.title() ] )
            text2 = re.sub( txt, user_prefer, text2 )
    except:
        LOGGER.error.print_exc()
    return text2


def isRemovedSong( path ):
    #from tagger import ID3v1
    #id3 = ID3v1( path )
    isRemoved = False
    #if id3.tag_exists():
    #    #print id3.artist
    #    isRemoved = ( id3.songname == "Removed Song" )
    #del id3, ID3v1
    try: isRemoved = "Removed Song" in open( path, "rb+" ).read()
    except: LOGGER.error.print_exc()
    return isRemoved


def closeDialogProgress():
    #Don't raise SystemError: Error: Window is NULL, this is not possible :-)
    if xbmc.getCondVisibility( "Window.IsVisible(progressdialog)" ):
        xbmc.executebuiltin( "Close.Dialog(progressdialog)" )
        #DIALOG_PROGRESS.close()


def dialog_help_site():
    if IsTrue( Addon.getSetting( "showhelpsite" ) ):
        if xbmcgui.Dialog().yesno( Language( 32115 ), Language( 32116 ), scraper.base_url, "", Language( 32118 ), Language( 32117 ) ):
            xbmc.executebuiltin( "RunScript(%s/viewer.py,webbrowser,%s)" % ( sys.path[ 0 ], scraper.base_url ) )


def FileCopy( src, dst ):
    cmd = "FileCopy(%s,%s)" % ( src, dst )
    LOGGER.notice.LOG( cmd )
    if dst.lower().startswith( "ftp://" ):
        return remote_utils.copy_to_ftp( src, dst )
    else:
        return xbmcvfs.copy( src, dst )


def FileDelete( filename ):
    cmd = "FileDelete(%s)" % ( filename )
    LOGGER.warning.LOG( cmd )
    if filename.lower().startswith( "ftp://" ):
        return remote_utils.delete_to_ftp( filename )
    else:
        return xbmcvfs.delete( filename )


class TvTunes:
    def __init__( self, solo ):
        self.ERASE = not solo
        if solo: self._solo()

    def _solo( self ):
        try:
            params.tvname = params.tvname or g_TVShowTitle
            params.tvpath = params.tvpath or g_FilenameAndPath
            #params.tvpath = params.tvpath or xbmc.getInfoLabel( "ListItem.Path" )
            #print repr( params.tvname ), repr( params.tvpath  )
            # fix path
            params.tvpath = fix_path( params.tvpath )
            self.current_theme = self.getDestination( params.tvpath, params.tvname )
            #print repr( params.tvname ), repr( params.tvpath  )
            LOGGER.notice.LOG( "initialized solo mode took %s", time_took( START_TIME ) )
            xbmc.sleep( 500 )
            self.ERASE = path_exists( self.current_theme )
            #print self.ERASE, self.current_theme
            self.ERASE = not self.ERASE or xbmcgui.Dialog().yesno( Language( 32103 ), Language( 32104 ) )
            self.scan( params.tvname, params.tvpath )
            dialog_help_site()
        except:
            LOGGER.error.print_exc( "%r", locals() )

    def playTune( self, name, path ):
        DIALOG_PROGRESS.update( 0, LangXBMC( 13350 ), name )
        listitem = xbmcgui.ListItem (name )
        listitem.setInfo( 'music', { 'title': name } )
        time.sleep( .1 )
        xbmc.Player().play( path, listitem )

    def scan( self, cur_name="", cur_path="" ):
        DIALOG_PROGRESS.create( Language( 32105 ), Language( 32106 ) )
        try:
            if cur_name and cur_path:
                if not self.ERASE: # and path_exists( os.path.join( cur_path, THEME_FILE ) ):
                    LOGGER.debug.LOG( "%r already exists, ERASE is set to False", self.current_theme )
                else:
                    theme_url = ""
                    DIALOG_PROGRESS.update( 0, Language( 32107 ), cur_name )
                    theme_list = self.search_theme_list( cur_name )
                    LOGGER.debug.LOG( "theme_list = %r", theme_list )
                    if len( theme_list ) == 1 and not IsTrue( Addon.getSetting( "select_one_tune" ) ):
                        theme_url = theme_list[ 0 ][ "url" ]
                        self.playTune( theme_list[ 0 ][ "name" ], theme_url )
                        if not xbmcgui.Dialog().yesno( Language( 32103 ), Language( 32114 ), theme_list[ 0 ][ "name" ] ):
                            theme_url = False
                            xbmc.executebuiltin('PlayerControl(Stop)')
                    else:
                        theme_url = self.get_user_choice( theme_list, cur_name )

                    if theme_url:
                        OK, tune = self.download( theme_url, cur_path, params.tvname )
        except:
            LOGGER.error.print_exc()
        closeDialogProgress()

    def getDestination( self, path, tvshowtitle ):
        # default dest
        destination = os.path.join( path, THEME_FILE )
        # if user prefer local path set this
        if not IsTrue( Addon.getSetting( "savetuneintvshowfolder" ) ):
            path2 = Addon.getSetting( "customtunesfolder" )
            if not path_exists( path2 ): path2 = ""
            if path2 and tvshowtitle:
                # normalize the path (win32 support / as path separators) and make sure endswith by /
                path2 = path2.replace( "\\", "/" ).rstrip( "/" ) + "/" # setting "customtunesfolder"
                # set normalized title
                tvshowtitle = normalize_string( tvshowtitle )
                if IsTrue( Addon.getSetting( "saveinseparatefolder" ) ):
                    destination = path2 + tvshowtitle + "/" + THEME_FILE
                    if not path_exists( path2 + tvshowtitle ):
                        #make path
                        #xbmcvfs.mkdir( path2 + tvshowtitle )
                        os.makedirs( path2 + tvshowtitle )
                else:
                    destination = path2 + tvshowtitle + ".mp3"
        return destination

    def download( self, theme_url, path, tvshowtitle="" ):
        OK = False
        LOGGER.debug.LOG( "download: %r", theme_url )
        tmpdestination = os.path.join( addon_temp, THEME_FILE )
        destination = self.getDestination( path, tvshowtitle )
        try:
            if not path_exists( path ):
                LOGGER.debug.LOG( "problem with path: %s", path )
                return

            def _report_hook( count, blocksize, totalsize ):
                percent = int( float( count * blocksize * 100 ) / totalsize )
                DIALOG_PROGRESS.update( percent, Language( 32121 ),
                    Language( 32110 ) + ' ' + theme_url.decode( "utf-8" ),
                    Language( 32111 ) + ' ' + tmpdestination.decode( "utf-8" )
                    )

            fp, h = urllib.urlretrieve( theme_url, tmpdestination, _report_hook )
            LOGGER.debug.LOG( str( h ).replace( "\r", "" ) )
            #from tagger import ID3v2
            #id3 = ID3v2( tmpdestination )
            #if not id3.tag_exists(): print "No ID3 Tag Found"
            #else:
            if "audio" in str( h[ "Content-Type" ] ).lower():
                isRemoved = isRemovedSong( tmpdestination )
                if isRemoved:
                    LOGGER.warning.LOG( "songname = 'Removed Song' for this tune %s", theme_url )
                else:
                    DIALOG_PROGRESS.update( 100, Language( 32122 ),
                        Language( 32110 ) + ' ' + tmpdestination.decode( "utf-8" ),
                        Language( 32111 ) + ' ' + destination.decode( "utf-8" )
                        )
                    OK = FileCopy( tmpdestination, destination )
                    LOGGER.debug.LOG( "download " + ( "failed", "successful" )[ OK ] )
            #del id3, ID3v2
            FileDelete( tmpdestination )
        except:
            LOGGER.error.print_exc( "Theme download Failed !!!" )
        return OK, destination

    def get_user_choice( self, theme_list, showname ):
        #on cree la liste de choix de theme
        theme_url = False
        searchname = showname.decode( "utf-8" )
        searchdic = { "name": Language( 32113 ) }
        theme_list.insert( 0, searchdic )
        while theme_url == False:
            if len( theme_list ) == 1:
                selected = 0
            else:
                selected = xbmcgui.Dialog().select( Language( 32112 ) + ' ' + searchname,
                    [ setPrettyFormatting( searchname, theme[ "name" ] ) for theme in theme_list ] )
            if selected == -1:
                LOGGER.debug.LOG( "Canceled by user" )
                #xbmcgui.Dialog().ok( "Canceled", "Download canceled by user" )
                return False
            else:
                if selected == 0:
                    kb = xbmc.Keyboard( showname, Language( 32113 ), False )
                    kb.doModal()
                    if kb.isConfirmed():
                        result = kb.getText()
                        if result == showname:
                            continue
                        searchname = result
                        theme_list = self.search_theme_list( searchname )
                        theme_list.insert( 0, searchdic )
                    else:
                        break
                else:
                    name = theme_list[ selected ][ "name" ]
                    theme_url = theme_list[ selected ][ "url" ]
                    LOGGER.debug.LOG( "%s", theme_url )
                    self.playTune( name, theme_url )
                    if not xbmcgui.Dialog().yesno( Language( 32103 ), Language( 32114 ), name ):
                        theme_url = False
                        xbmc.executebuiltin( 'PlayerControl(Stop)' )

        return theme_url

    def search_theme_list( self, showname ):
        # max 0 = no limite
        try: max = "0|20|40|80|160|320|640|1000".split( "|" )[ int( Addon.getSetting( "tuneslimite" ) ) ]
        except: max = "0"
        return scraper.getTunes( showname, int( max ) )
