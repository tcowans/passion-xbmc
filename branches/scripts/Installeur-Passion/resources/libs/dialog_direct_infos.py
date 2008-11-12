
#Modules general
import os
import re
import sys
import urllib

import elementtree.ElementTree as ET

#modules XBMC
import xbmc
import xbmcgui

#modules custom
try: from script_log import *
except:
    LOG_ERROR = 0
    from traceback import print_exc
    def EXC_INFO( *args ): print_exc()
    LOG = EXC_INFO
    #EXC_INFO( LOG_ERROR, sys.exc_info() )


DIRECT_INFOS = "http://passion-xbmc.org/.xml/?type=rss"

#REPERTOIRE RACINE ( default.py )
CWD = os.getcwd().rstrip( ";" )

#FONCTION POUR RECUPERER LES LABELS DE LA LANGUE.
_ = sys.modules[ "__main__" ].__language__


#FONCTION POUR RECUPERER LE THEME UTILISE PAR L'UTILISATEUR.
def getUserSkin():
    current_skin = xbmc.getSkinDir()
    force_fallback = os.path.exists( os.path.join( CWD, "resources", "skins", current_skin ) )
    if not force_fallback: current_skin = "Default"
    return current_skin, force_fallback


def set_pretty_formatting( text ):
    text = text.replace( "<br />", "\n" )
    text = text.replace( "<i>", "[I]" ).replace( "</i>", "[/I]" )
    text = text.replace( "<b>", "[B]" ).replace( "</b>", "[/B]" )
    #text = re.sub( "(?s)</[^>]*>", "[/B]", text )
    #text = re.sub( "(?s)<[^>]*>", "[B]", text )
    return text


def strip_off( text, by="" ):
    #text = text.replace( "[", "<" ).replace( "]", ">" )
    return re.sub( "(?s)<[^>]*>", by, text )


def load_infos( filename ):
    try:
        feed = urllib.urlopen( filename )
        tree = ET.parse( feed )
        feed.close()

        # if you need the root element, use getroot
        root = tree.findall( "channel" )#tree.getroot()

        # delete
        del tree
        return root
    except:
        EXC_INFO( LOG_ERROR, sys.exc_info() )


class ENTITY_OR_CHARREF:
    def __init__( self, strvalue="" ):
        # Internal -- convert entity or character reference
        # http://www.toutimages.com/codes_caracteres.htm
        strvalue = self._replace_html_to_iso( strvalue )

        self.entitydefs = { 'lt': '<', 'gt': '>', 'amp': '&', 'quot': '"', 'apos': '\'' }

        self.entity_or_charref = re.compile( '&(?:'
            '([a-zA-Z][-.a-zA-Z0-9]*)|#([0-9]+)'
            ')(;?)' ).sub( self._convert_ref, strvalue )

    def _replace_html_to_iso( self, strvalue ):
        # NO CONFORM
        html_to_iso = {
            '&#8211;': "-",
            '&#8217;': "'",
            '&euro;': "&#128;",
            '&ldquo;': "&#147;",
            '&rdquo;': "&#148;",
            '&nbsp;': "&#32;", #'&nbsp;':   "&#160;",
            '&hellip;': "&#133;", '&Hellip;': "&#133;",
            '&agrave;': "&#224;", '&Agrave;': "&#192;",
            '&acirc;':  "&#226;", '&Acirc;':  "&#194;",
            '&ccedil;': "&#231;", '&Ccedil;': "&#199;",
            '&egrave;': "&#232;", '&Egrave;': "&#200;",
            '&eacute;': "&#233;", '&Eacute;': "&#201;",
            '&ecirc;':  "&#234;", '&Ecirc;':  "&#202;",
            '&icirc;':  "&#238;", '&Icirc;':  "&#206;",
            '&iuml;':   "&#239;", '&Iuml;':   "&#207;",
            '&ocirc;':  "&#244;", '&Ocirc;':  "&#212;",
            '&ugrave;': "&#249;", '&Ugrave;': "&#217;",
            '&ucirc;':  "&#251;", '&Ucirc;':  "&#219;"
            }
        for key, value in html_to_iso.items():
            strvalue = strvalue.replace( key, value )
        return strvalue

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


def add_pretty_color( word, start=None, end=None, color=None ):
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
        EXC_INFO( LOG_ERROR, sys.exc_info() )
        return word


class DirectInfos( xbmcgui.WindowXML ):
    def __init__( self, *args, **kwargs ):
        pass

    def onInit( self ):
        self._set_text()

    def _set_text( self ):
        xbmcgui.lock()
        try: 
            self.getControl( 5 ).reset()
            self.getControl( 5 ).setText( self._get_text() )
        except:
            EXC_INFO( LOG_ERROR, sys.exc_info(), self )
        xbmcgui.unlock()

    def _get_text( self ):
        full_text = ""
        try:
            root = load_infos( DIRECT_INFOS )
            for elems in root[ 0 ].findall( "item" ):
                category = elems.findtext( "category" )
                title = add_pretty_color( elems.findtext( "title" ), "all", "", "FFe2ff43" )
                pubDate = elems.findtext( "pubDate" )
                description = ENTITY_OR_CHARREF( strip_off( set_pretty_formatting( elems.findtext( "description" ) ) ).strip( "\t" ).strip( "\n" ) ).entity_or_charref
                # "[CR]" est le retour de ligne d'xbmc
                full_text += "[CR]".join( [ title, category, pubDate, description ] ).replace( "\n", "[CR]" ).replace( "\r", "[CR]" )
                full_text += "[CR][CR]"
        except:
            EXC_INFO( LOG_ERROR, sys.exc_info(), self )
        return full_text

    def onFocus( self, controlID ):
        #cette fonction n'est pas utiliser ici, mais dans les XML si besoin
        pass

    def onClick( self, controlID ):
        pass

    def onAction( self, action ):
        #( ACTION_PARENT_DIR, ACTION_PREVIOUS_MENU, ACTION_CONTEXT_MENU, )
        if action in ( 9, 10, 117 ): self._close_dialog()

    def _close_dialog( self ):
        xbmc.sleep( 100 )
        self.close()


def show_direct_infos():
    file_xml = "passion-DirectInfos.xml"
    #depuis la revision 14811 on a plus besoin de mettre le chemin complet, la racine suffit
    dir_path = CWD #xbmc.translatePath( os.path.join( CWD, "resources" ) ) 
    #recupere le nom du skin et si force_fallback est vrai, il va chercher les images du defaultSkin.
    current_skin, force_fallback = getUserSkin()

    w = DirectInfos( file_xml, dir_path, current_skin, force_fallback )
    w.doModal()
    del w


if ( __name__ == "__main__" ):
    root = load_infos( DIRECT_INFOS )
    for elems in root[ 0 ].findall( "item" ):
        print elems.findtext( "category" )
        print elems.findtext( "title" )
        print elems.findtext( "pubDate" )
        print ENTITY_OR_CHARREF( strip_off( set_pretty_formatting( elems.findtext( "description" ) ) ).strip( "\t" ).rstrip( "\n" ) ).entity_or_charref
        print str( "-" * 85 )
