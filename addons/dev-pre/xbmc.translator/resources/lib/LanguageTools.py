
import re
import time
import urllib2
from urllib import urlencode
from traceback import print_exc

from utilities import time_took
from convert import htmlentitydecode


USER_AGENT = "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; .NET CLR 1.1.4322; .NET CLR 2.0.50727)"

# base google url
urlGG = "http://translate.google.com/translate_t"
# base babelfish url
urlBF = "http://babelfish.yahoo.com/translate_txt"

countriesGG = {
  'Afrikaans': 'af',
  'Albanian': 'sq',
  'Arabic': 'ar',
  'Armenian': 'hy',
  'Azerbaijani': 'az',
  'Basque': 'eu',
  'Belarusian': 'be',
  'Bulgarian': 'bg',
  'Catalan': 'ca',
  'Chinese': 'zh-CN',
  'Croatian': 'hr',
  'Czech': 'cs',
  'Danish': 'da',
  'Dutch': 'nl',
  'English': 'en',
  'Estonian': 'et',
  #'Esperanto': 'eo', # not supported
  'Filipino': 'tl',
  'Finnish': 'fi',
  'French': 'fr',
  'Galician': 'gl',
  'Georgian': 'ka',
  'German': 'de',
  'Greek': 'el',
  'Haitian Creole': 'ht',
  'Hebrew': 'iw',
  'Hindi': 'hi',
  'Hungarian': 'hu',
  'Icelandic': 'is',
  'Indonesian': 'id',
  'Irish': 'ga',
  'Italian': 'it',
  'Japanese': 'ja',
  'Korean': 'ko',
  'Latin': 'la',
  'Latvian': 'lv',
  'Lithuanian': 'lt',
  'Macedonian': 'mk',
  'Malay': 'ms',
  'Maltese': 'mt',
  'Norwegian': 'no',
  'Persian': 'fa',
  'Polish': 'pl',
  'Portuguese': 'pt',
  'Romanian': 'ro',
  'Russian': 'ru',
  'Serbian': 'sr',
  'Slovak': 'sk',
  'Slovenian': 'sl',
  'Spanish': 'es',
  'Swahili': 'sw',
  'Swedish': 'sv',
  'Thai': 'th',
  'Turkish': 'tr',
  'Ukrainian': 'uk',
  'Urdu': 'ur',
  'Vietnamese': 'vi',
  'Welsh': 'cy',
  'Yiddish': 'yi',
  }

countriesBF = {
  'Chinese (Simple)': 'en_zh',
  'Chinese (Traditional)': 'en_zt',
  'Dutch': 'en_nl',
  'French': 'en_fr',
  'German': 'en_de',
  'German (Austria)': 'en_de',
  'Greek': 'en_el',
  'Italian': 'en_it',
  'Japanese': 'en_ja',
  'Korean': 'en_ko',
  'Portuguese': 'en_pt',
  'Portuguese (Brazil)': 'en_pt',
  'Russian': 'en_ru',
  'Spanish': 'en_es',
  'Spanish (Mexico)': 'en_es',
  }


def get_country_id( lang, site="google" ):
    if site == "babelfish":
        id = countriesBF.get( lang )
    else:
        id = countriesGG.get( lang.split( " (" )[ 0 ] )
    return ( id or "" )


def get_html_source( url, data={} ):
    """ fetch html source """
    source = ""
    try:
        # request url
        request = urllib2.Request( url, urlencode( data ), { 'User-Agent': USER_AGENT } )
        # open requested url
        sock = urllib2.urlopen( request )
        # read source
        source = sock.read()
        # close socket
        sock.close()
    except:
        print_exc()
    if source:
        # fix unicode
        try: source = unicode( source, "UTF-8" )
        except: pass
    return source


def translate_text( text="", lang="French", site="google" ):
    """ fetch translated text """
    t1 = time.time()
    translated = ""
    try:
        if site == "babelfish":
            # translate with babelfish
            lp = get_country_id( lang, "babelfish" )
            if lp:
                # data dictionary
                data = { "ei": "UTF-8", "doit": "done", "fr": "bf-home", "intl": "1", "tt": "urltext", "trtext": text.replace( "\n", "[_]" ), "lp": lp, "btnTrTxt": "Translate" }
                # get html source
                source = get_html_source( urlBF, data )
                # find translated text
                result = "".join( re.findall( "<div id=\"result\"><div style=\"[^\"]+\">([^<]+)", source ) )
                translated = result.replace( " [_] ", "\n" ).replace( "[_]", "\n" )
            if not translated:
                site += " and google"

        if not translated or ( site == "google" ):
            # translate with google
            tl = get_country_id( lang, "google" )
            # data dictionary
            data = { "hl": "", "ie": "UTF-8", "text": text, "sl": "en", "tl": tl }
            # get html source
            source = get_html_source( urlGG, data )
            # find translated text
            result_box = "".join( re.compile( "(<span id=result_box.*?)</div></div>", re.S ).findall( source ) )
            translated = "".join( re.findall( "<span title.*?>(.*?)</span>", result_box ) ).replace( "<br>", "\n" )
    except:
        print_exc()
    if translated:
        # fix entity
        translated = htmlentitydecode( translated )
    print "Translate text %r into %r with %s took %s" % ( text, lang, site, time_took( t1 ) )
    return translated



if ( __name__ == "__main__" ):
    t = "Select your XBMC user Profile[CR]to login and continue".replace( "[CR]", "\n" )
    l = "Arabic"

    print translate_text( t, l, "google" )
    print
    print translate_text( t, l, "babelfish" )
