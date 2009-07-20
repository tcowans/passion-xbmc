
#Modules general
import os
import re
import sys
import urllib
from traceback import print_exc

#Modules XBMC
import xbmc
import xbmcgui
import xbmcplugin

from utilities import SPECIAL_PLUGIN_CACHE


_ = xbmc.getLocalizedString

DIALOG_PROGRESS = xbmcgui.DialogProgress()


def search2( name="" ):
    # faut mettre cette fonction dans allocine
    result = []
    try:
        search_url = "http://www.allocine.fr/recherche/?motcle=%s&rub=1&page=1"
        html = urllib.urlopen( search_url % name.replace( " ", "+" ) ).read()
        regexp = '<h1 style=".*?">Recherche : <b>(.*?)</b></h1>(.*?)</tr></table><br /></td></tr></table>'
        films = re.compile( regexp, re.DOTALL ).findall( html )
        for film in re.findall( '<a href="/film/fichefilm_gen_cfilm=(\d+).html">(.*?)</tr>', films[ 0 ][ 1 ] ):
            try:
                infos = re.findall( '<h4.*?>(.*?)</h4>', film[ 1 ] )
                if infos:
                    ID = film[ 0 ]
                    thumb = re.findall( '<img src="(.*?)"', film[ 1 ] )[ 0 ]
                    title = "".join( re.findall( '>(.*?)<', infos[ 0 ] ) )
                    if len( infos ) >= 2:
                        title = "%s, (%s)" % ( title, infos[ 1 ] )
                    h5 = re.findall( '<h5.*?>(.*?)</h5>', film[ 1 ] )
                    extra = []
                    for h in h5:
                        if "</a>" in h:
                            extra.append( "".join( re.findall( '>(.*?)<', h ) ).replace( "&nbsp;", "" ) )
                        else:
                            extra.append( h )
                    result.append( ( ID, title, thumb, "[CR]".join( extra ) ) )
            except:
                print_exc()
        name = films[ 0 ][ 0 ]
    except:
        print_exc()
    return name, result


def bold_name_match( name="", title="" ):
    try:
        name = name.lower()
        title = title.lower().replace( name, "[B]%s[/B]" % name ).title()
        romains = [ "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII", "XIII", "XIV", "XV", "XVI", "XVII", "XVIII", "XIX", "XX" ]
        for romain in romains:
            title = re.sub( "\\b%s\\b" % romain.title(), romain, title )
    except:
        print_exc()
    return title.replace( "[B]", "[COLOR=a0e2ff43][B]" ).replace( "[/B]" , "[/B][/COLOR]")


def get_thumbnail( path ):
    try:
        fpath = path
        if "novignette" in fpath: return ""
        # make the proper cache filename and path so duplicate caching is unnecessary
        filename = xbmc.getCacheThumbName( fpath )
        thumbnail = os.path.join( SPECIAL_PLUGIN_CACHE, filename[ 0 ], filename )
        if not os.path.isdir( os.path.dirname( thumbnail ) ):
            os.makedirs( os.path.dirname( thumbnail ) )
        # if the cached thumbnail does not exist check for a tbn file
        if ( not os.path.isfile( thumbnail ) ):
            #DIALOG_PROGRESS.update( -1, fpath, thumbnail )
            urllib.urlretrieve( fpath, thumbnail )
        if ( not os.path.isfile( thumbnail ) ):
            thumbnail = ""
        return thumbnail
    except:
        print_exc()
        return ""


class ENTITY_OR_CHARREF:
    def __init__( self, strvalue="" ):
        # Internal -- convert entity or character reference
        # http://www.toutimages.com/codes_caracteres.htm

        self.entitydefs = { 'lt': '<', 'gt': '>', 'amp': '&', 'quot': '"', 'apos': '\'' }

        self.entity_or_charref = re.compile( '&(?:'
            '([a-zA-Z][-.a-zA-Z0-9]*)|#([0-9]+)'
            ')(;?)' ).sub( self._convert_ref, strvalue )

    def _convert_ref( self, match ):
        if match.group( 2 ):
            return self.convert_charref( match.group( 2 ) ) or ( '&#%s%s' % match.groups( )[ 1: ] )
        elif match.group( 3 ):
            return self.convert_entityref( match.group( 1 ) ) or ( '&%s;' % match.group( 1 ) )
        else:
            return '&%s' % match.group( 1 )

    def convert_charref( self, name ):
        """Convert character reference, may be overridden."""
        try:
            n = int( name )
        except ValueError:
            return
        if not 0 <= n <= 255:
            return
        return self.convert_codepoint( n )

    def convert_codepoint( self, codepoint ):
        return chr( codepoint )

    def convert_entityref( self, name ):
        """Convert entity references.

        As an alternative to overriding this method; one can tailor the
        results by setting up the self.entitydefs mapping appropriately.
        """
        table = self.entitydefs
        if name in table:
            return table[ name ]
        else:
            return


class PluginSelect:
    def __init__( self, *args, **kwargs ):
        self.selected = -1
        self.name_search = ENTITY_OR_CHARREF( kwargs.get( "name", "" ) ).entity_or_charref
        self.films = kwargs.get( "films" )
        self.fpath = kwargs.get( "fpath" )
        self.onNFO()

    def onNFO( self ):
        OK = True
        try:
            #( ID, title, thumb, extra )
            for film in self.films:
                tbn = get_thumbnail( film[ 2 ] ) or "DefaultVideo.png"
                title = bold_name_match( self.name_search.strip( '"' ), film[ 1 ] )
                DIALOG_PROGRESS.update( -1, _( 1040 ), title )
                listitem = xbmcgui.ListItem( title, "[COLOR=a0e2ff43]ID:[/COLOR] " + film[ 0 ], tbn, tbn )
                c_items = [ ( _( 30009 ), "XBMC.Action(Info)", ) ]
                c_items += [ ( _( 654 ), "XBMC.ActivateWindow(scriptsdebuginfo)" ) ]
                listitem.addContextMenuItems( c_items, replaceItems=True )
                plot = "[COLOR=a0e2ff43]ID:[/COLOR] %s[CR]%s" % ( film[ 0 ], film[ 3 ] )
                listitem.setInfo( type="Video", infoLabels={ "title": title, "plot": plot } )
                url = "%s?path=%s&show_id=%s" % ( sys.argv[ 0 ], repr( urllib.quote_plus( self.fpath ) ), repr( film[ 0 ] ), )
                OK = xbmcplugin.addDirectoryItem( handle=int( sys.argv[ 1 ] ), url=url, listitem=listitem, isFolder=True, totalItems=len( self.films ) )
            try: cat = _( 283 ) + ":[CR]" + self.name_search
            except: cat = _( 283 ) + ":[CR]" + self.name_search.decode( "iso-8859-1" )
            xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category=cat )
        except:
            print_exc()
        self._set_Content( OK )

    def _set_Content( self, OK ):
        if ( OK ):
            content = ( "files", "movies", "tvshows", "episodes", )[ 1 ]
            xbmcplugin.setContent( handle=int( sys.argv[ 1 ] ), content=content )
        self._add_sort_methods( OK )

    def _add_sort_methods( self, OK ):
        if ( OK ):
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_NONE )
        self._end_of_directory( OK )

    def _end_of_directory( self, OK ):
        xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=OK )


class _Info:
    def __init__( self, *args, **kwargs ):
        self.__dict__.update( kwargs )


def Main():
    try:
        exec "args = _Info(%s)" % ( sys.argv[ 2 ][ 1 : ].replace( "&", ", " ), )
        args.path = urllib.unquote_plus( args.path )
        temp_search = ""
        name, films = "", ""
        while True:
            if temp_search or not args.path:
                keyboard = xbmc.Keyboard( temp_search, _( 30002 ) )
                keyboard.doModal()
                if keyboard.isConfirmed():
                    search = keyboard.getText()
                else:
                    name, films = "", ""
                    break
            else:
                search = os.path.splitext( os.path.basename( args.path ) )[ 0 ]
                if search.lower() == "video_ts":
                    dir = os.path.dirname( args.path )
                    if re.search( "video", os.path.basename( dir ).lower() ):
                        search = os.path.basename( os.path.dirname( dir ) )
                    else:
                        search = os.path.basename( dir )
            name, films = search2( search )
            if bool( films ):
                break
            else:
                temp_search = search

        if name and films:
            PluginSelect( name=name, films=films, fpath=args.path )
    except:
        print_exc()

