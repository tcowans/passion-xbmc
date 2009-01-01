
import os
import sys
from time import strftime
import elementtree.ElementTree as ET

#from convert import ENTITY_OR_CHARREF#, translate_string

ENCODING = ( "", "iso-8859-1", "UTF-8", )[ 2 ]


try: from plugin_log import *
except:
    LOG_ERROR = 0
    from traceback import print_exc
    def EXC_INFO( *args ): print_exc()
    LOG = EXC_INFO
    #EXC_INFO( LOG_ERROR, sys.exc_info() )


def load_infos( filename ):
    try:
        tree = ET.parse( filename )
        #print tree.getiterator()

        # the tree root is the toplevel ??? element
        #print eval( tree.findtext( "screens" ) )

        # if you need the root element, use getroot
        root = tree.getroot()
        #print root.findtext( "title" )

        # delete
        del tree
        return root
    except:
        EXC_INFO( LOG_ERROR, sys.exc_info() )


def save_infos( filename, kwargs, isgame=True ):
    try:
        if kwargs and isinstance( kwargs, dict ):
            #setup variables
            if isgame:
                str_root = "game_informations"
                unsorted = [ "ID", "title", "platform", "tbn", "urlsource" ]
            else:
                str_root = "platform_informations"
                unsorted = [ "ID", "platform", "tbn", "urlsource" ]

            # build a tree structure
            root = ET.Element( str_root )
            root.text = "\n  "
            #root.tail = "\n"

            #optional Comment with current date and time
            c = ET.Comment( "File created: %s" % ( strftime( "%d-%m-%Y | %H:%M:%S" ), ) )
            c.tail = "\n  "
            root.append( c )

            # build first sub element
            for key in unsorted:
                sub_elem = ET.SubElement( root, key )
                sub_elem.text = kwargs[ key ]
                sub_elem.tail = "\n  "
                del kwargs[ key ]
                del sub_elem
                del key

            # build others sub element
            for key, value in sorted( kwargs.items(), key=lambda k: k[ 0 ] ):#, reverse=True ):
                sub_elem = ET.SubElement( root, key )
                if not value: value = ""
                if isinstance( value, str ): sub_elem.text = value.replace( "\n", "[CR]" )
                else: sub_elem.text = repr( value )
                sub_elem.tail = "\n  "

            try: sub_elem.tail = "\n"
            except: root.text = "\n"

            # wrap it in an ElementTree instance, and save as XML
            tree = ET.ElementTree( root )
            tree.write( filename, ENCODING )

            #If not error, return path filename.
            return filename
    except:
        EXC_INFO( LOG_ERROR, sys.exc_info() )
        #None reponse is returned


def update_infos( filename, attr_dict={} ):
    try:
        # ...manipulate tree...
        tree = ET.parse( filename )
        for elem in tree.getroot():
            for key, value in attr_dict.items():
                if elem.tag == key:
                    if not value: value = ""
                    if isinstance( value, str ): elem.text = value
                    elif isinstance( value, dict ): elem.attrib = value
                    else: elem.text = repr( value )
        tree.write( filename )#, ENCODING )
        #If not error, return path filename.
        return filename
    except:
        EXC_INFO( LOG_ERROR, sys.exc_info() )
        #None reponse is returned



if ( __name__ == "__main__" ):
    test = { 'support_phone': '', 'buttons_listed': ['T0'], 'tbn': 'http://www.allgame.com/img/nogame_large.gif', 'screens': [], 'included_package': '', 'credits_listed': [], 'amg_rating': '', 'year': 2008, 'genre': 'Shooter', 'extra_credits': '', 'ID': '53502', 'developer': 'Gearbox Software', 'publisher': '2K Games', 'style': 'Squad-Based Shooter', 'controls_listed': [], 'title': 'Borderlands', 'support_url': '', 'review': '', 'controls': '', 'support_email': '', 'platform': 'Xbox 360', 'synopsis': '', 'esrb_rating': '', 'flags': '', 'esrb_rating_img': '', 'supports': '', 'urlsource': 'http://www.allgame.com/cg/agg.dll?p=agg&sql=1:53502', 'system_requirements': [] }

    #make base directory if not exists
    base_dir = ""
    dir_path = os.path.join( base_dir, "games", test[ "platform" ].replace( "/", "_" ) )
    if not os.path.isdir( dir_path ): os.makedirs( dir_path )
    filename = os.path.join( dir_path, "%s.xml" % ( test[ "ID" ], ) )

    print "Is saved =", save_infos( filename, test.copy() )
    #print "Is updated =", update_infos( filename, attr_dict={ 'support_phone': '(666) 666-6666' } )
    #print "Is updated =", update_infos( filename, attr_dict={ 'screens': [ "test update" ] } )
    #not used for moment, but it posible to add ATTRIB on any tag
    #print "Is updated =", update_infos( filename, attr_dict={ 'support_phone': { 'country': 'CA' } } )

    root = load_infos( filename )#"allgame_com/games/Pokemon Mini/41025.xml" )
    for elem in root:
        print '        self[ "%s" ] = ""' % ( elem.tag )
    print repr( root.findtext( "title" ) )
    print isinstance( root.findtext( "title" ), unicode )
    print root.findtext( "urlsource" )
    print root.findtext( "support_phone" )
    screens = root.findtext( "screens" ) or '[]'
    print screens
