
import re
import unicodedata
import htmlentitydefs


illegal_characters = {
  '#128': '&#8364;', # Euro
  '#129': '',        #
  '#130': '&#8218;', # apostrophe anglaise basse
  '#131': '&#402;',  # florin, forte musical
  '#132': '&#8222;', # guillemet anglais bas
  '#133': '&#8230;', # points de suspension
  '#134': '&#8224;', # obèle, dague, croix (renvoi de notes de bas de page)
  '#135': '&#8225;', # double croix
  '#136': '&#710;',  # accent circonflexe
  '#137': '&#8240;', # pour mille
  '#138': '&#352;',  # S majuscule avec caron (accent circonflexe inversé) utilisé en tchèque
  '#139': '&#8249;', # guillemet simple allemand et suisse, parenthèse angulaire ouvrante
  '#140': '&#338;',  # Ligature o-e majuscule (absente de la norme ISO-8859-1 pour une raison aberrante…)
  '#141': '',        #
  '#142': '&#381;',  # Z majuscule avec caron (accent circonflexe inversé) utilisé en tchèque. Présent dans le Character Encoding  ISO-8859-2
  '#143': '',        #
  '#144': '',        #
  '#145': '&#8216;', # guillemet anglais simple ouvrant(utilisé dans les guillemets doubles)
  '#146': '&#8217;', # guillemet anglais simple fermant(utilisé dans les guillemets doubles)
  '#147': '&#8220;', # guillemets anglais doubles ouvrants
  '#148': '&#8221;', # guillemets anglais doubles fermants
  '#149': '&#8226;', # boulet, utiliser plutôt des listes à puces
  '#150': '&#8211;', # tiret demi-cadratin (incise), voir The Trouble With EM 'n EN
  '#151': '&#8212;', # tiret cadratin (dialogue), voir The Trouble With EM 'n EN
  '#152': '&#732;',  # tilde
  '#153': '&#8482;', # marque déposée
  '#154': '&#353;',  # s minuscule avec caron (accent circonflexe inversé) utilisé en tchèque
  '#155': '&#8250;', # guillemet simple allemand et suisse, parenthèse angulaire fermante
  '#156': '&#339;',  # Ligature o-e minscule (absente de la norme ISO-8859-1 pour une raison aberrante…)
  '#157': '',        #
  '#158': '&#382;',  # z minuscule avec caron (accent circonflexe inversé) utilisé en tchèque. Présent dans le Character Encoding  ISO-8859-2
  '#159': '&#376;'   # Y majuscule avec trema, présent en français dans quelques noms propres (PDF).
  }


def htmlentitydecode( s ):
    t = s
    # Pre-First convert numerical illegal_characters (such as &#128;-&#159;)
    try:
        def illegal( m ):
            entity = m.group( 1 )
            if entity in illegal_characters.keys():
                return u"" + illegal_characters[ entity ] or u'&%s;' % entity #u'&#39;&#168;&#39;'#
            return  u'&%s;' % entity
        t = re.sub( u'&(%s);' % u'|'.join( illegal_characters ), illegal, s )
    except:
        pass
    t = t.replace( "\t", "&#8212;" ).replace( "&nbsp;", "&#8212;" )

    # First convert alpha entities (such as &eacute;)
    try:
        def entity2char( m ):
            entity = m.group( 1 )
            if entity in htmlentitydefs.name2codepoint:
                return unichr( htmlentitydefs.name2codepoint[ entity ] )# or '&%s;' % entity
            return u" " # Unknown entity: We replace with a space.
        t = re.sub( u'&(%s);' % u'|'.join( htmlentitydefs.name2codepoint ), entity2char, t )
    except:
        pass

    # Then convert numerical entities (such as &#233;)
    try: t = re.sub( u'&#(\d+);', lambda x: unichr( int( x.group( 1 ) ) ), t )
    except: pass

    # Then convert hexa entities (such as &#x00E9;)
    try: t = re.sub( u'&#x(\w+);', lambda x: unichr( int( x.group( 1 ), 16 ) ), t )
    except: pass
    return t


def normalize_string( text, setunicode=False ):
    t = text
    if setunicode:
        try: t = unicode( text, "utf-8" ).lower()
        except: pass

    try: text = unicodedata.normalize( 'NFKD', t ).encode( 'ascii', 'ignore' )
    except: pass
    return text
