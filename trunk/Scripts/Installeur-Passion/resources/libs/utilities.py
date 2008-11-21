"""
Module de partage des fonctions et des constantes

"""

#Modules general
import os
import re
import sys

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
    EXC_INFO( LOG_ERROR, sys.exc_info() )


#REPERTOIRE RACINE ( default.py )
CWD = os.getcwd().rstrip( ";" )


def getUserSkin():
    """ FONCTION POUR RECUPERER LE THEME UTILISE PAR L'UTILISATEUR """
    current_skin = xbmc.getSkinDir()
    force_fallback = os.path.exists( os.path.join( CWD, "resources", "skins", current_skin ) )
    if not force_fallback: current_skin = "Default"
    return current_skin, force_fallback


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
        EXC_INFO( LOG_ERROR, sys.exc_info() )
        return word


def bold_text( text ):
    """ FONCTION POUR METTRE UN MOT GRAS """
    return "[B]%s[/B]" % ( text, )


def italic_text( text ):
    """ FONCTION POUR METTRE UN MOT ITALIQUE """
    return "[I]%s[/I]" % ( text, )


def set_pretty_formatting( text, bold_links=False ):
    """ FONCTION POUR RENDRE COMPATIBLE LES TAGS HTML POUR XBMC """
    text = text.replace( "<br />", "\n" )#.replace( "<br />", "[CR]" )
    text = text.replace( "<i>", "[I]" ).replace( "</i>", "[/I]" )
    text = text.replace( "<b>", "[B]" ).replace( "</b>", "[/B]" )
    if bold_links:
        text = re.sub( "(?s)</[^>]*>", "[/B]", text )
        text = re.sub( "(?s)<[^>]*>", "[B]", text )
    return text


def strip_off( text, by="", xbmc_labes_formatting=False ):
    """ FONCTION POUR RECUPERER UN TEXTE D'UN TAG """
    if xbmc_labes_formatting:
        text = text.replace( "[", "<" ).replace( "]", ">" )
    return re.sub( "(?s)<[^>]*>", by, text )


class CONVERT:
    def __init__( self, strvalue="" ):
        # Internal -- convert entity or character reference
        # http://www.toutimages.com/codes_caracteres.htm
        strvalue = self._replace_html_to_iso( strvalue )

        self.entitydefs = { 'lt': '<', 'gt': '>', 'amp': '&', 'quot': '"', 'apos': '\'' }

        self.entity_or_charref = re.compile( '&(?:'
            '([a-zA-Z][-.a-zA-Z0-9]*)|#([0-9]+)'
            ')(;?)' ).sub( self._convert_ref, strvalue )

    def _replace_html_to_iso( self, strvalue ):
        strvalue = strvalue.replace( "&#160;", '&nbsp;' )
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
