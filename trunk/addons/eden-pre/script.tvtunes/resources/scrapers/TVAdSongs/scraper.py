
__all__ = [ "scraper_name", "base_url", "getTunes" ]

import os
import re
import sys
import urllib

try:
    from utils.log import logAPI
except ImportError:
    # In debug/test and scraper is __main__
    sys.path.insert( 0, "../../lib/utils" )
    from log import logAPI

LOGGER = logAPI()

# constants
scraper_name = "TVAdSongs.com"
base_url     = "http://tvadsongs.com/"
search_url   = base_url + "search.php?searWords=%s&Send=Search"
download_url = base_url + "download.php?f=%s"


HTTP_USER_AGENT = "Mozilla/5.0 (Windows NT 5.1; rv:7.0.1) Gecko/20100101 Firefox/7.0.1" #"Mozilla/5.0 (Windows; U; Windows NT 5.1; fr; rv:1.9.0.1) Gecko/2008070208 Firefox/3.6"
# actually xbmc not support this, require little patch in XBPython.cpp "HTTP_USER_AGENT=" + g_settings.m_userAgent.c_str(); "XBMC/PRE-11.0 Git:Unknown (Windows NT 5.1; http://www.xbmc.org)"
HTTP_USER_AGENT = os.environ.get( "HTTP_USER_AGENT", HTTP_USER_AGENT )

class AppURLopener( urllib.FancyURLopener ):
    version = HTTP_USER_AGENT
urllib._urlopener = AppURLopener()



def get_html_source( url ):
    """ fetch the html source """
    htmlsource = ""
    try:
        #urllib.urlcleanup()
        sock = urllib.urlopen( url )
        htmlsource = sock.read()
        sock.close()
    except:
        LOGGER.error.print_exc( "ERROR opening page %s", url )
    return htmlsource


def clean_string( value, deletechars=""",*=|<>?;:"+""" ):
    # on nettoie le nom des caract pas cool (type ": , ; , ...")
    #for c in deletechars: value = value.replace( c, '' )
    value = re.sub( '[%s]' % deletechars, '', value )
    return value


def getTunes( showname, max=0 ):
    """
        showname    : string or unicode
        max         : int (default=0 no limite) (used with user setting)
    """

    LOGGER.info.LOG( "Search for %s", showname )
    url = search_url % urllib.quote_plus( clean_string( showname ) )
    nextpage = ""
    theme_list = []
    while True:
        # on recup le result de la recherche
        LOGGER.info.LOG( "Search url: %s", url + nextpage )
        html = get_html_source( url + nextpage )

        #on parse la recherche pour renvoyer une liste de dico
        match = re.search( r"1\.&nbsp;(.*)<br>", html )
        if match:
            tunes = re.findall( '<a href="(.*?)">(.*?)</a>', match.group( 1 ) )
            for uri, name in tunes:
                uri = download_url % os.path.basename( uri ).replace( ".html" , "" )
                theme_list.append( { "url": uri, "name": name } )
                if max and max == len( theme_list ):
                    break
        else:
            LOGGER.info.LOG( "no theme found for %s", showname )
            break

        if max and max == len( theme_list ):
            break

        # get next page and if not next break
        match = re.search( r'&search=Search(&page=\d)"><b>Next</b>', html )
        if not match: break
        nextpage = match.group( 1 )

    return theme_list


if ( __name__ == "__main__" ):
    print len( getTunes( "star trek", 50 ) )
