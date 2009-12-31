
from traceback import print_exc
import elementtree.ElementTree as ET

try: import xbmc
except ImportError:
    xbmc = None


if xbmc: XML_PATH = 'special://userdata/RssFeeds.xml'
else: XML_PATH = r'C:\Program Files\XBMC\userdata\RssFeeds.xml'

ENCODING = ( "", "ISO-8859-1", "UTF-8", )[ 2 ]

def refresh_rss():
    """ Reload RSS feeds from RSSFeeds.xml """
    if xbmc:
        xbmc.executebuiltin( "RefreshRSS()" )
        xbmc.sleep( 1000 )
        print 'xbmc.executebuiltin( "RefreshRSS()" )'
    else: print "RefreshRSS"


def parse_xml():
    """ fonction: pour parser le fichier RssFeeds.xml """
    feeds = {}
    try:
        source = open( XML_PATH )
        tree = ET.parse( source )
        source.close()
        for elems in tree.getroot():
            setid = elems.attrib.get( "id" )
            if setid:
                feed = []
                feedstag = elems.findall( "feed" )
                for feedtag in feedstag:
                    feed.append( { "updateinterval": feedtag.attrib.get( "updateinterval", "30" ), "feed": feedtag.text } )

                rtl = elems.attrib.get( "rtl", "false" )
                feeds[ setid ] = { "rtl": rtl, "feed": feed }
        del tree
    except:
        print_exc()
        feeds = {}
    return feeds


def save_xml( kwargs, filename="" ):
    """ fonction: pour ecrire le fichier RssFeeds.xml, a partir d'une dico """
    try:
        if not filename: filename = XML_PATH
        if kwargs and isinstance( kwargs, dict ):
            # build a tree structure
            root = ET.Element( "rssfeeds" )
            root.text = "\n  "

            #optional Comment
            c1 = ET.Comment( 'RSS feeds. To have multiple feeds, just add a feed to the set. You can also have multiple sets.' )
            c2 = ET.Comment( 'To use different sets in your skin, each must be called from skin with a unique id.' )
            c1.tail = "\n  "; root.append( c1 )
            c2.tail = "\n  "; root.append( c2 )

            #optional Comment writed in set tag id 100 only
            c3 = ET.Comment( "Rss Feed : passion-xbmc.org; created and used by script Installer Passion-XBMC" )
            c3.tail = "\n    "

            # build elements and sub elements
            for key, value in sorted( kwargs.items(), key=lambda k: int( k[ 0 ] ) ):
                set_elem = ET.SubElement( root, "set" )
                set_elem.attrib.update( { "id": key, "rtl": value.get( "rtl", "false" ) } )
                set_elem.text = "\n    "
                set_elem.tail = "\n  "
                if key == "100": set_elem.append( c3 )
                for feed in value[ "feed" ]:
                    feed_elem = ET.SubElement( set_elem, "feed" )
                    feed_elem.attrib.update( { "updateinterval": feed.get( "updateinterval", "30" ) } )
                    feed_elem.text = feed.get( "feed", "http://passion-xbmc.org/scraper/?forumrss=1" )
                    feed_elem.tail = "\n    "

                try: feed_elem.tail = "\n  "
                except: set_elem.text = ""
                if not value[ "feed" ]:
                    set_elem.text = ""

            try: set_elem.tail = "\n"
            except: root.text = "\n"

            # wrap it in an ElementTree instance, and save as XML
            tree = ET.ElementTree( root )
            # frost: I modified ElementTree.write for write standalone
            tree.write( filename, ENCODING, True )

            #If not error, refresh_rss and return filename path.
            refresh_rss()
            return filename
    except:
        print_exc()
        #None reponse is returned



if __name__  == "__main__":
    add = {'100': {'feed': [{'feed': 'http://code.google.com/feeds/p/passion-xbmc/updates/basic', 'updateinterval': '30'}], 'rtl': 'false'}}
    rss = parse_xml()
    rss.update( add )
    print save_xml( rss, "test_rss.xml" )
