
# if debug, write file "strings_test.xml"
DEBUG = True

import os
from re import sub
from time import strftime
from traceback import print_exc

from xml.dom.minidom import parseString

import xbmcvfs
from xbmcgui import ListItem
from xbmc import getInfoLabel, translatePath


from utilities import fixe_line_return


class Language:
    def __init__( self, *args, **kwargs ):
        self.main = args[ 0 ]

        self.english_xml = "%s/%s/strings.xml" % ( self.main.FolderLanguage, self.main.DefaultLanguage )
        self.current_xml = "%s/%s/strings.xml" % ( self.main.FolderLanguage, self.main.CurrentLanguage )

        # get current_xml source
        temp_strings = {}
        try:
            # parse source
            dom = self.parseSource( self.current_xml )
            strings = dom.getElementsByTagName( "string" )
            for string in strings:
                if not string.hasChildNodes(): text = ""
                else: text = string.firstChild.nodeValue
                temp_strings[ string.getAttribute( "id" ) ] = fixe_line_return( text )
            # cleanup
            dom.unlink()
        except:
            print_exc()

        # get english_xml source
        self.listitems = []
        try:
            # parse source
            self.dom = self.parseSource( self.english_xml )
            strings = self.dom.getElementsByTagName( "string" )

            for count, string in enumerate( strings ):
                if not string.hasChildNodes(): label2 = ""
                else: label2 = string.firstChild.nodeValue
                id = string.getAttribute( "id" )
                label1 = temp_strings.get( id ) or ""
                label2 = fixe_line_return( label2 )
                UnTranslated = ( label1 and not label2 ) or ( label2 and not label1 ) or ( temp_strings.get( id ) is None )

                listitem = ListItem( label1, label2 )
                listitem.setProperty( "id", id )
                listitem.setProperty( "IsModified", "" )
                listitem.setProperty( "DefaultString", label1 )
                listitem.setProperty( "Position", str( count ) )
                listitem.setProperty( "CurrentLanguage", self.main.CurrentLanguage )
                listitem.setProperty( "DefaultLanguage", self.main.DefaultLanguage )
                listitem.setProperty( "UnTranslated", repr( UnTranslated ).lower() )
                self.listitems.append( listitem )
        except:
            print_exc()
        del temp_strings

    def parseSource( self, xml_file ):
        # get source
        f = open( translatePath( xml_file ) )
        xml = f.read()
        f.close()
        # return parsed source
        return parseString( xml )

    def createComments( self ):
        comments = [ self.dom.createComment( 'Language file translated with Add-on XBMC Translator ' + self.main.Addon.getAddonInfo( "version" ) ) ]

        username = self.main.Addon.getSetting( "username" )
        if username: comments += [ self.dom.createComment( 'Translator: ' + username ) ]
        usermail = self.main.Addon.getSetting( "usermail" )
        if usermail: comments += [ self.dom.createComment( 'Email: ' + usermail ) ]

        version_based = 'version ' + getInfoLabel( 'System.BuildVersion' )
        if ( self.main.DefaultFolderLanguage.rstrip( "/" ) != self.main.FolderLanguage ):
            from xbmcaddon import Addon
            # get addon version
            apath = translatePath( self.main.FolderLanguage.replace( "/resources", "" ).replace( "/language", "" ) )
            addon = Addon( os.path.basename( apath.rstrip( os.sep ) ) )
            version_based = "add-on %s version %s" % ( addon.getAddonInfo( "name" ), addon.getAddonInfo( "version" ) )
        comments += [ self.dom.createComment( 'Date of translation: ' + strftime( '%x %X' ) ),
                      self.dom.createComment( 'Based on english strings ' +  version_based ),
                      ]

        refChild = self.dom.documentElement
        for comment in comments:
            self.dom.insertBefore( comment, refChild )

    def save_strings( self ):
        """ save strings """
        OK = False
        try:
            from convert import htmlentitydecode
            self.createComments()
            # get current strings in listitems
            current_strings = {}
            for li in self.listitems:
                current_strings[ li.getProperty( "id" ) ] = fixe_line_return( li.getLabel(), True )

            # set strings based on default english structure
            for string in self.dom.getElementsByTagName( "string" ):
                text = current_strings.get( string.getAttribute( "id" ) )
                if bool( text ) and string.firstChild is not None:
                    string.firstChild.nodeValue = text.replace( "\n", "&#10;" ).decode( "utf-8" )
                elif string.parentNode is not None:
                    # remove this ( is not translated or default is empty ) no need to add these to our language files
                    string.parentNode.removeChild( string )

            xml = self.dom.toxml( "utf-8" )
            #hack for standalone attribute, minidom doesn't support DOM3
            xml = xml.replace( "?>", ' standalone="yes"?>\n', 1 )
            # fixe multi-line return and entity
            xml = sub( "  \n", "\n", xml )
            xml = sub( "\n\n\n", "\n", xml )
            xml = sub( "\n\n\n", "\n\n", xml )
            xml = xml.replace( "&amp;#", "&#" )
            xml = xml.replace( "&quot;", "\"" )
            # Remove "$Revision$" Obsolete On Git version
            xml = xml.replace( '<!--$Revision$-->', "", 1 )
            #fixe comments
            xml = xml.replace( "--><!--", "-->\n<!--" )
            xml = xml.replace( "--><strings>", "-->\n<strings>" )

            OK = self.writeXML( xml )
        except:
            OK = False
            print locals()
            print_exc()
        return OK

    def writeXML( self, xml ):
        OK = False
        temp_xml = "special://temp/strings.xml"

        # write temp xml
        f = open( translatePath( temp_xml ), "w" )
        f.write( xml )
        f.close()

        # first create backup of original file and copy temp xml to self.current_xml
        backup = "%s/%s/backup/%s_strings.xml" % ( self.main.FolderLanguage, self.main.CurrentLanguage, strftime( '%Y-%m-%d-%H%M' ) )
        if xbmcvfs.copy( self.current_xml, backup ):
            # copy temp xml to self.current_xml
            xml = "%s/%s/strings.xml" % ( self.main.FolderLanguage, self.main.CurrentLanguage )
            if DEBUG: xml = xml.replace( "strings.xml", "strings_test.xml" )
            OK = xbmcvfs.copy( temp_xml, xml )

        return OK
