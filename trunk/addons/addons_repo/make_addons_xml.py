
import os
import md5
import time
import datetime
from traceback import print_exc

import elementtree.HTMLTreeBuilder as ET

ENCODING = ( "", "iso-8859-1", "UTF-8", )[ 2 ]

try:
    # ...manipulate tree...
    import elementtree.ElementTree as etree
    # build a tree structure
    root = etree.Element( "addons" )
    root.text = "\n"
    root.tail = "\n"
    for addon in os.listdir( "../" ):
        if os.path.exists( "../%s/addon.xml" % addon ):
            tree2 = etree.parse(  "../%s/addon.xml" % addon )
            tree2.getroot().tail = "\n"
            root.append( tree2.getroot() )
    tree = etree.ElementTree( root )
    tree.write( "addons.xml", ENCODING )
except:
    print_exc()

try:
    timestamp = str( datetime.datetime.fromtimestamp( time.time() ) )
    addons_md5 = md5.new( timestamp ).hexdigest()
    file( "addons.xml.md5", "w" ).write( "%s\n" % addons_md5 )
except:
    print_exc()
