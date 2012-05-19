
import os
import time

#try:
#    from xml.etree.cElementTree import *
#    from xml.etree.ElementTree import _raise_serialization_error, _escape_attrib, _escape_cdata, _encode, fixtag, XMLTreeBuilder
#except ImportError:
from elementtree.ElementTree import *


ENCODING = ( "", "ISO-8859-1", "UTF-8", )[ 2 ]


from utilities import time_took


class Parser( XMLTreeBuilder ):
    """ Reading processing instructions and comments with ElementTree

        The following is an alternative XML parser that adds Comment and ProcessingInstruction elements to the element
        tree. Since such elements can appear outside the XML document proper, it wraps the entire document in an extra document element.

        Note that this uses undocumented and unsupported parts of the ElementTree interface. It does work with
        ElementTree 1.2.X, but may not work with future versions.

        Source: http://effbot.org/zone/element-pi.htm
    """
    def __init__( self ):
        XMLTreeBuilder.__init__( self )
        # assumes ElementTree 1.2.X
        self._parser.CommentHandler = self.handle_comment
        self._parser.ProcessingInstructionHandler = self.handle_pi
        self._parser.XmlDeclHandler = self.xml_decl_handler
        #self._target.start( "strings", {} )

        self._root = None
        # default xml handler
        self.version = '1.0'
        self.encoding = ENCODING
        #hack for standalone attribute, etree doesn't support DOM3
        self.standalone = True

    def xml_decl_handler( self, version, encoding, standalone ):
        self.version = version
        self.encoding = encoding
        # This is still a little ugly, thanks to the pyexpat API. ;-(
        if standalone >= 0: self.standalone = bool( standalone )

    def close( self ):
        #self._target.end( "strings" )
        return XMLTreeBuilder.close( self )

    def handle_comment( self, data ):
        self._target.start( Comment, {} )
        self._target.data( data )
        self._target.end( Comment )

    def handle_pi( self, target, data ):
        self._target.start( PI, {} )
        self._target.data( target + " " + data )
        self._target.end( PI )

    def write( self, file, comments=[], encoding=None, standalone=False ):
        assert self._root is not None
        if not hasattr( file, "write" ):
            file = open( file, "wb" )
        encoding = encoding or self.encoding
        standalone = standalone or self.standalone
        if not encoding:
            encoding = "us-ascii"
        elif ( not standalone ) and ( encoding != "utf-8" ) and ( encoding != "us-ascii" ):
            file.write( '<?xml version="1.0" encoding="%s"?>\n' % ( encoding, ) )
        elif standalone:
            file.write( '<?xml version="1.0" encoding="%s" standalone="yes"?>\n' % ( encoding.upper(), ) )

        for comment in comments:
            file.write( "<!-- %s -->\n" % _encode( comment, encoding ) )
        self._write( file, self._root, encoding, {} )

    def _write( self, file, node, encoding, namespaces ):
        # write XML to file
        tag = node.tag
        if tag is Comment:
            file.write( "<!-- %s -->" % _encode( node.text.strip(), encoding ) )
        elif tag is ProcessingInstruction:
            file.write( "<?%s?>" % _escape_cdata( node.text, encoding ) )
        else:
            items = node.items()
            xmlns_items = [] # new namespaces in this scope
            try:
                if isinstance( tag, QName ) or tag[ :1 ] == "{":
                    tag, xmlns = fixtag( tag, namespaces )
                    if xmlns: xmlns_items.append( xmlns )
            except TypeError:
                _raise_serialization_error( tag )
            file.write( "<" + _encode( tag, encoding ) )
            if items or xmlns_items:
                items.sort() # lexical order
                for k, v in items:
                    try:
                        if isinstance( k, QName ) or k[ :1 ] == "{":
                            k, xmlns = fixtag( k, namespaces )
                            if xmlns: xmlns_items.append( xmlns )
                    except TypeError:
                        _raise_serialization_error( k )
                    try:
                        if isinstance( v, QName ):
                            v, xmlns = fixtag( v, namespaces )
                            if xmlns: xmlns_items.append( xmlns )
                    except TypeError:
                       _raise_serialization_error( v )
                    file.write( " %s=\"%s\"" % ( _encode( k, encoding ),
                                                 _escape_attrib( v, encoding ) ) )
                for k, v in xmlns_items:
                    file.write( " %s=\"%s\"" % ( _encode( k, encoding ),
                                                 _escape_attrib( v, encoding ) ) )
            if node.text or len( node ):
                file.write( ">" )
                if node.text:
                    line = _escape_cdata( node.text, encoding )
                    if line.strip( " \n" ) and ( "\n" in line ):
                        line = line.replace( "\n", "&#10;" )
                    file.write( line )
                for n in node:
                    self._write( file, n, encoding, namespaces )
                #file.write( "</" + _encode( tag, encoding ) + ">" )
            else:
                file.write( ">" )
                #file.write( " />" )
            file.write( "</" + _encode( tag, encoding ) + ">" )
            for k, v in xmlns_items:
                del namespaces[ v ]
        if node.tail:
            file.write( _escape_cdata( node.tail, encoding ) )


def parseSource( source, full=False ):
    t1 = time.time()
    if full: # parse xml with processing instructions and comments
        parser = Parser()
        tree = parse( source, parser )
        parser._root = tree._root
        tree.write = parser.write
    else:
        # speed up with cElementTree ;-) and not custom parser
        tree = parse( source )
    print "Parsing file took %s [%s]" % ( time_took( t1 ), source )
    return tree


def writeXML( filename, comments, new_strings ):
    # get english language for default layout
    englishfile = os.path.join( os.path.dirname( os.path.dirname( filename ) ), "english", "strings.xml" )
    root = parseSource( englishfile, True )

    t1 = time.time()
    for string in root.findall( "string" ):
        id = string.attrib.get( "id" )
        string.text = ( new_strings.get( id ) or "" )

    root.write( filename, comments, ENCODING )
    print "Writing file took %s [%s]" % ( time_took( t1 ), filename )


def getComments( version_based, user_name="", user_mail="", api_ver="1.0.0" ):
    comments = [ 'Language file translated with Add-on XBMC Translator %s' % api_ver ]

    if user_name: comments += [ 'Translator: %s' % user_name ]
    if user_mail: comments += [ 'Email: %s' % user_mail ]

    comments += [ 'Date of translation: %s' % time.strftime( '%x %X' ),
                  'Based on english strings under XBMC %s' % version_based ]

    return comments


def getTempStrings( filename ):
    temp = {}
    root = parseSource( filename )
    for string in root.findall( "string" ):
        temp[ string.attrib.get( "id" ) ] = string.text
    del root
    return temp


if ( __name__ == "__main__" ):

    filename = r"C:\Program Files\XBMC\language\french\strings.xml"
    temp_strings = getTempStrings( filename )

    defaultfile = r"C:\Program Files\XBMC\language\english\strings.xml"
    root = parseSource( defaultfile )
    print "-"*100

    comments = getComments( "PRE-11.0 Git:20110617-085ec3f", "Frost", "frost@passion-xbmc.org" )
    writeXML( filename+".xml", comments, temp_strings )
    print "-"*100

    #"""
    START_TIME = time.time()
    for lang in os.listdir( r"C:\Program Files\XBMC\language" ):
        #if lang.lower() != "french": continue
        filename = r"C:\Program Files\XBMC\language\%s\strings.xml" % lang
        root = parseSource( filename )

        #t1 = time.time()
        print lang
        #strings = root.findall( "string" )
        #print len( strings )
        #for string in strings:
        #    print string.attrib.get( "id" ), ( string.text or "" )

        #for elem in root.getroot():#.find( "strings" ):
            #if elem.tag != "string" and elem.tag is Comment:
            #    print "Comment", elem.text
            #    print
            #if not elem.text or not elem.text.strip( " \n" ):
            #    print elem.attrib.get( "id" )
            #   root._root.remove( elem )
            #for e in elem.getiterator( ):
            #    print e

        #comments = getComments( "PRE-11.0 Git:20110617-085ec3f", "Frost", "frost@passion-xbmc.org" )
        #root.write( filename + ".xml", comments )
        #print time_took( t1 )
        print "-"*100
        #break
    #"""
    print time_took( START_TIME )
