"""
Recoded with ElementTree by Frost, 
result more fast, use less memory
and automatic encoding for 'Codes->ASCII,ISO,HTML at symbols'.
"""

import os, traceback
from elementtree import ElementTree

SCRIPT_PATH = os.getcwd().rstrip(';')
if os.path.ismount(SCRIPT_PATH+os.sep): SCRIPT_PATH += os.sep

class Language:
    """ Language Class: creates a dictionary of localized strings { int: string } """
    def __init__( self, *args, **kwargs ):
        """ initializer """
        self.defScriptLang = kwargs.get('defscriptlang', "french")
        base_path = os.path.join( SCRIPT_PATH, "language" )
        language = self._get_language( base_path )
        self._create_localized_dict( base_path, language )

    def _get_language( self, base_path ):
        """ returns the current language if a strings.xml file exists else returns self.defScriptLang """
        #try:
        #    import autoLanguage
        #    language = autoLanguage.autoLanguage(base_path, self.defScriptLang ).get_Language()
        #    del autoLanguage
        #except:
        #    traceback.print_exc()
        import xbmc
        language = xbmc.getLanguage()
        del xbmc
        if ( not os.path.isfile( os.path.join( base_path, language, "strings.xml" ) ) ):
            language = self.defScriptLang
        return language

    def _create_localized_dict( self, base_path, language ):
        """ initializes self.strings and calls _parse_strings_file """
        self.strings = {}
        self._parse_strings_file( os.path.join( base_path, language, "strings.xml" ) )
        if ( language != self.defScriptLang ):
            self._parse_strings_file( os.path.join( base_path, self.defScriptLang, "strings.xml" ) )
        if self.strings == {}: raise

    def _parse_strings_file( self, language_path ):
        """ adds localized strings to self.strings dictionary """
        try:
            tree = ElementTree.ElementTree()
            tree.parse(language_path)
            root = tree.getroot()
            for i in root.findall('string'):
                s, id = i.text, i.attrib.get('id')
                if id and s and s != '-':
                    if not self.strings.get(int(id)):
                        self.strings.update( { int(id): s } )
        except:
            print "ERROR: Language file %s can't be parsed" % ( language_path, )
            traceback.print_exc()

    def localized( self, code ):
        """ returns the localized string if it exists """
        return self.strings.get( int( code ), 'id="%s" : No string set' % ( str( code ), ) )
