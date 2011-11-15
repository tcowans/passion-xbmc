
import re
import unicodedata
import htmlentitydefs


__doc__ = u"""illegal_characters:
    les caractères codés de &#128; à &#159; - propres à Windows, mais invalides selon les spécifications HTML 4+ et XHTML  .

    Encodés incorrectement comme dans la première colonne de résultat du tableau ci-dessous, ces caractères ne seront pas
    restitués correctement sur d'autres plates-formes que Windows (Linux...), où, au mieux,
    un caractère générique sera affiché (fréquemment un carré vide).

    Ils doivent donc être remplacés par leur équivalent en entités numériques ou entités caractères qui, elles, sont valides et
    seront correctement restituées.

    Ces deux solutions ne sont toutefois pas équivalentes :
        * aucune des entités caractères ne s'affiche dans Netscape 4 ;
        * le résultat obtenu avec les références numériques est indépendant du Character Encoding (ISO-8859-1 ou UTF-8),
        puisque ces codes relèvent du Character Set ISO-10646 utilisé en HTML et en XHTML.

    More :
        * Internal -- convert entity or character reference
        * http://www.trans4mind.com/personal_development/HTMLGuide/specialCharacters.htm
        * http://www.toutimages.com/codes_caracteres.htm
        * http://openweb.eu.org/articles/caracteres_illegaux/
"""


illegal_characters = {
    '#128': '&#8364;', # Euro
    '#129': '', #
    '#130': '&#8218;', # apostrophe anglaise basse
    '#131': '&#402;', # florin, forte musical
    '#132': '&#8222;', # guillemet anglais bas
    '#133': '&#8230;', # points de suspension
    '#134': '&#8224;', # obèle, dague, croix (renvoi de notes de bas de page)
    '#135': '&#8225;', # double croix
    '#136': '&#710;', # accent circonflexe
    '#137': '&#8240;', # pour mille
    '#138': '&#352;', # S majuscule avec caron (accent circonflexe inversé) utilisé en tchèque
    '#139': '&#8249;', # guillemet simple allemand et suisse, parenthèse angulaire ouvrante
    '#140': '&#338;', # Ligature o-e majuscule (absente de la norme ISO-8859-1 pour une raison aberrante…)
    '#141': '', #
    '#142': '&#381;', # Z majuscule avec caron (accent circonflexe inversé) utilisé en tchèque. Présent dans le Character Encoding  ISO-8859-2
    '#143': '', #
    '#144': '', #
    '#145': '&#8216;', # guillemet anglais simple ouvrant(utilisé dans les guillemets doubles)
    '#146': '&#8217;', # guillemet anglais simple fermant(utilisé dans les guillemets doubles)
    '#147': '&#8220;', # guillemets anglais doubles ouvrants
    '#148': '&#8221;', # guillemets anglais doubles fermants
    '#149': '&#8226;', # boulet, utiliser plutôt des listes à puces
    '#150': '&#8211;', # tiret demi-cadratin (incise), voir The Trouble With EM 'n EN
    '#151': '&#8212;', # tiret cadratin (dialogue), voir The Trouble With EM 'n EN
    '#152': '&#732;', # tilde
    '#153': '&#8482;', # marque déposée
    '#154': '&#353;', # s minuscule avec caron (accent circonflexe inversé) utilisé en tchèque
    '#155': '&#8250;', # guillemet simple allemand et suisse, parenthèse angulaire fermante
    '#156': '&#339;', # Ligature o-e minscule (absente de la norme ISO-8859-1 pour une raison aberrante…)
    '#157': '', #
    '#158': '&#382;', # z minuscule avec caron (accent circonflexe inversé) utilisé en tchèque. Présent dans le Character Encoding  ISO-8859-2
    '#159': '&#376;' # Y majuscule avec trema, présent en français dans quelques noms propres (PDF).
    }


def htmlentitydecode( s ):
    # First1 convert numerical illegal_characters (such as &#128;-&#159;)
    def illegal( m ):
        entity = m.group( 1 )
        if entity in illegal_characters.keys():
            return u""+illegal_characters[ entity ] or u'&%s;' % entity#u'&#39;&#168;&#39;'#
        return  u'&%s;' % entity
    t = re.sub( u'&(%s);' % u'|'.join( illegal_characters ), illegal, s )
    t = t.replace( "\t", "&#8212;" ).replace( "&nbsp;", "&#8212;" )

    # First2 convert alpha entities (such as &eacute;)
    def entity2char( m ):
        entity = m.group( 1 )
        if entity in htmlentitydefs.name2codepoint:
            return unichr( htmlentitydefs.name2codepoint[ entity ] )# or '&%s;' % entity
        return u" "  # Unknown entity: We replace with a space.
    t = re.sub( u'&(%s);' % u'|'.join( htmlentitydefs.name2codepoint ), entity2char, t )

    # Then convert numerical entities (such as &#233;)
    t = re.sub( u'&#(\d+);', lambda x: unichr( int( x.group( 1 ) ) ), t )

    # Then convert hexa entities (such as &#x00E9;)
    return re.sub( u'&#x(\w+);', lambda x: unichr( int( x.group( 1 ), 16 ) ), t )


def normalize_string( text ):
    return unicodedata.normalize( 'NFKD', text ).encode( 'ascii', 'ignore' )


def set_pretty_formatting( text ):
    text = text.replace( "<br />", "\n" )
    text = text.replace( "<hr />", ( "_" * 150 ) + "\n" )
    text = text.replace( "<p>", "" ).replace( "</p>", "" )
    text = text.replace( "<i>", "[I]" ).replace( "</i>", "[/I]" )
    text = text.replace( "<em>", "[I]" ).replace( "</em>", "[/I]" )
    text = text.replace( "<b>", "[B]" ).replace( "</b>", "[/B]" )
    text = text.replace( "<strong>", "[B]" ).replace( "</strong>", "[/B]" )
    return text.strip()


def set_quote_and_code_in_color( text ):
    for color, txt in re.findall( '<span style="color: (.*?)">(.*?)</span>', text ):
        try:
            search_for = r'<span style="color: %s">%s</span>' % ( color, txt )
            color = color.split( ";" )[ 0 ].strip( "# " ).replace( "black", "FFFFFF" )
            replace_by = '[COLOR=FF%s]%s[/COLOR]' % ( color, txt )
            text = re.sub( search_for, replace_by, text )
        except Exception, e:
            print e
            print repr( replace_by )
            print repr( search_for )
            print #text
    match = re.search( r'<div class="codeheader">Code</div><pre class="(.*?)" style="font-family:monospace;"><div style="border-bottom : 1px solid gray; margin-bottom: 0.3em;">(.*?)</div>', text )
    if match:
        s =r'<div class="codeheader">Code</div><pre class="%s" style="font-family:monospace;"><div style="border-bottom : 1px solid gray; margin-bottom: 0.3em;">%s</div>' % ( match.group( 1 ), match.group( 2 ) )
        b = "Code %s\n %s\n" % ( match.group( 2 ), ( u"_" * 150 ) )
        text = text.replace( s, b )
        text = text.replace( "</pre>", ( "_" * 150 ) + "\n" )

    text = text.replace( '<div class="quoteheader">', "[COLOR=99FFFFFF]" )
    text = text.replace( '<div class="quote">', "\n[COLOR=88FFFFFF]" )
    if "COLOR=" in text: text = text.replace( "</div>", "[/COLOR]" )
    else: text = text.replace( "</div>", "" )
    return text.strip()



if ( __name__ == "__main__" ):
    try: import xbmcgui
    except: xbmcgui = None

    #print __doc__.encode( "ISO-8859-1" )
    #print "-"*100
    #print "normalize_string::%s" % normalize_string( __doc__ )
    #print "-"*100

    html_to_iso = {
        '&#8211;':  "&#8211;",
        '&#8217;':  "&#8217;",
        '&euro;':   "&#128;",
        '&rsquo;':  "&#146;",
        '&ldquo;':  "&#147;",
        '&rdquo;':  "&#148;",
        '&ndash;':  "&#150;",
        '&nbsp;':   "&#32;", #'&nbsp;':   "&#160;",
        '&hellip;': "&#133;",# '&Hellip;': "&#133;",
        '&agrave;': "&#224;", '&Agrave;': "&#192;",
        '&acirc;':  "&#226;", '&Acirc;':  "&#194;",
        '&ccedil;': "&#231;", '&Ccedil;': "&#199;",
        '&egrave;': "&#232;", '&Egrave;': "&#200;",
        '&eacute;': "&#233;", '&Eacute;': "&#201;",
        '&ecirc;':  "&#234;", '&Ecirc;':  "&#202;",
        '&euml;':   "&#235;", '&Euml;':   "&#203;",
        '&icirc;':  "&#238;", '&Icirc;':  "&#206;",
        '&iuml;':   "&#239;", '&Iuml;':   "&#207;",
        '&ocirc;':  "&#244;", '&Ocirc;':  "&#212;",
        '&ugrave;': "&#249;", '&Ugrave;': "&#217;",
        '&ucirc;':  "&#251;", '&Ucirc;':  "&#219;"
        }
    l = []
    l.append( " | ".join( [ "xbmc invalible = &#39;&#168;&#39;", htmlentitydecode( "&#39;&#168;&#39;" ), "&#39;&#39;", htmlentitydecode( "&#39;&#39;" ) ] ) )
    l.append( " | ".join( [ "&reg;", htmlentitydecode( "&reg;" ) ] ) )
    l.append( " | ".join( [ "&pi;", htmlentitydecode( "&pi;" ) ] ) )
    l.append( " | ".join( [ "&#8730;", htmlentitydecode( "&#8730;" ) ] ) )
    l.append( " | ".join( [ "&radic;", htmlentitydecode( "&radic;" ) ] ) )
    l.append( " | ".join( [ "&#8734;", htmlentitydecode( "&#8734;" ) ] ) )
    l.append( " | ".join( [ "&infin;", htmlentitydecode( "&infin;" ) ] ) )
    l.append( " | ".join( [ "&#8212;", htmlentitydecode( "&#8212;" ) ] ) )
    l.append( " | ".join( [ "&larr;", htmlentitydecode( "&larr;" ) ] ) )
    l.append( " | ".join( [ "&#174;", htmlentitydecode( "&#174;" ) ] ) )
    l.append( " | ".join( [ "&#169;", htmlentitydecode( "&#169;" ) ] ) )
    #l.append( " | ".join( [ "", htmlentitydecode( "" ) ] ) )
    #l.append( " | ".join( [ "", htmlentitydecode( "" ) ] ) )
    #l.append( " | ".join( [ "", htmlentitydecode( "" ) ] ) )

    for key, value in html_to_iso.items():
        l.append( " | ".join( [ key, htmlentitydecode( key ) ] ) )
        l.append( " | ".join( [ value, htmlentitydecode( value ) ] ) )
        #if xbmcgui is None:
        #    print key, htmlentitydecode( key )
        #    print value, htmlentitydecode( value )
        #    print "-"*100

    test = "&#169; | &#188; | &#189; | &#174; | &#181; |&#168; | &mdash; | &#129; | &#142; | &lt;&#128;-&ccedil;&#45;&Ucirc;-&euro;&gt; | &#8364; | &#382;"
    l.append( " | ".join( [ test, htmlentitydecode( test ) ] ) )

    l.append( " | ".join( [ test, normalize_string( htmlentitydecode( test ) ) ] ) )
    if xbmcgui is None:
        print test
        print htmlentitydecode( test )
        print normalize_string( htmlentitydecode( test ) )
        print "-"*100
        print '&#198; | 32&#176; | Un&#239;ted St&#228;tes | &#182; | &#165;Yen | PmWiki&#8482;'
        print htmlentitydecode('&#198; | 32&#176; | Un&#239;ted St&#228;tes | &#182; | &#165;Yen | PmWiki&#8482;')
        print "-"*100

    for c, items in enumerate( sorted( illegal_characters.items(), key=lambda x: x[ 0 ] ) ):
        invalide, valide = items[ 0 ], items[ 1 ]#[ 0 ], items[ 1 ][ 1 ]
        #print invalide
        l.append( " | ".join( [ invalide, htmlentitydecode( u'&%s;' % invalide  ), normalize_string( htmlentitydecode( u'&%s;' % invalide ) ) ] ) )
        if xbmcgui is None:
        #    print c+1
        #    print items
        #    print valide
            print invalide, htmlentitydecode( u'&%s;' % invalide  ), normalize_string( htmlentitydecode( u'&%s;' % invalide ) )
        #    #print numeric, htmlentitydecode( numeric )
        #    print
        #    print "-"*100

    if xbmcgui is not None:
        ret = xbmcgui.Dialog().select( "htmlentitydecode", l )

