
# Modules General
import re
import sys
import urllib
from StringIO import StringIO
from traceback import print_exc

import elementtree.HTMLTreeBuilder as HTB

#modules custom
from utilities import add_pretty_color, set_xbmc_carriage_return, strip_off


#FONCTION POUR RECUPERER LES LABELS DE LA LANGUE.
_ = sys.modules[ "__main__" ].__language__


class rssReader:
    """
    Class responsable de la recuperation du flux RSS et de l'extraction des infos RSS
    """
    def __init__( self, rss_title, rssUrl, titlecolor="ffffffff", textcolor="ffffffff" ):
        self.rss_title = rss_title
        self.titlecolor = titlecolor
        self.textcolor = textcolor
        #self.tags = ( [ "feed", "entry", "content" ], [ "channel", "item", "title" ] )[ ( not "code.google" in rssUrl ) ]
        self.tags = ( [ "feed", "entry", "title" ], [ "channel", "item", "title" ] )[ ( not "code.google" in rssUrl ) ]
        self.rssPage = self.load_feeds_infos( rssUrl )

    def load_feeds_infos( self, url ):
        try:
            html = urllib.urlopen( url )
            if "code.google" in url:
                source = html.read()
                parsed = HTB.parse( StringIO( source ), "utf-8"  ).findall( self.tags[ 1 ] )
            else:
                source = re.sub( "<!\[CDATA\[|\]\]>", "", html.read() )
                parsed = HTB.parse( StringIO( source ), "utf-8"  ).findall( self.tags[ 0 ] )[ 0 ].findall( self.tags[ 1 ] )
            html.close()
            return parsed
        except:
            print_exc()
            # si on arrive ici le retour est automatiquement None

    def GetRssInfo( self ):
        try:
            if self.rssPage is None: raise
            items_listed = self.rssPage[ :10 ]
            if not self.rss_title: maintitle = _( 107 )
            else: maintitle = self.rss_title
            items = add_pretty_color( maintitle + ": ", color=self.titlecolor )
            item_sep = add_pretty_color( " - ", color=self.textcolor )
            item_end = len( items_listed )
            for count, item in enumerate( items_listed ):
                try:
                    items += item.findtext( self.tags[ 2 ] ).replace( u'\xa0', " " )
                except:
                    print_exc()
                    continue
                if ( ( count + 1 ) < item_end ):
                    items += item_sep

            if self.tags[ 1 ] == "entry":
                items = strip_off( set_xbmc_carriage_return( items ).replace( "[CR]", " " ) )
            return maintitle, items.replace( "&quot;", '"' ).replace( "&#39;", "'" )
        except:
            print_exc()
            return "", ( add_pretty_color( _( 107 ), color=self.titlecolor ) + _( 108 ) )

