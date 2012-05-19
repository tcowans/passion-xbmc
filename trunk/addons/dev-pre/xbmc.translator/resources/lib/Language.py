
# if debug, write file = "strings_test.xml"
# if not debug, overwrite file = "strings.xml"
DEBUG = True

import os
from re import sub
from time import strftime
from traceback import print_exc

import xbmc
import xbmcvfs
from xbmcgui import ListItem


import etreeAPI as ET
from utilities import fixe_line_return


class Language:
    def __init__( self, *args, **kwargs ):
        self.main = args[ 0 ]

        self.english_xml = "%s/%s/strings.xml" % ( self.main.FolderLanguage, self.main.DefaultLanguage )
        self.current_xml = "%s/%s/strings.xml" % ( self.main.FolderLanguage, self.main.CurrentLanguage )

        # get current_xml source
        temp_strings = ET.getTempStrings( xbmc.translatePath( self.current_xml ) )

        # get english_xml source
        self.listitems = []
        try:
            # parse source
            root = ET.parseSource( xbmc.translatePath( self.english_xml ) )
            strings = root.findall( "string" )

            for count, string in enumerate( strings ):
                id = string.attrib.get( "id" )
                label1 = fixe_line_return( ( temp_strings.get( id ) or "" ) )
                label2 = fixe_line_return( ( string.text or "" ) )

                UnTranslated = ( temp_strings.get( id ) is None )
                UnTranslated = UnTranslated or ( label1 and not label2 ) or ( label2 and not label1 )

                listitem = ListItem( label1, label2 )
                listitem.setProperty( "DefaultString", label1 )
                listitem.setProperty( "id", id )
                listitem.setProperty( "Position", str( count ) )

                listitem.setProperty( "IsModified", "" )
                listitem.setProperty( "UnTranslated", repr( UnTranslated ).lower() )
                
                listitem.setProperty( "CurrentLanguage", self.main.CurrentLanguage )
                listitem.setProperty( "DefaultLanguage", self.main.DefaultLanguage )

                self.listitems.append( listitem )
        except:
            print_exc()
        del temp_strings

    def createComments( self ):
        version_based = 'version ' + xbmc.getInfoLabel( 'System.BuildVersion' )
        if ( self.main.DefaultFolderLanguage.rstrip( "/" ) != self.main.FolderLanguage ):
            from xbmcaddon import Addon
            # get addon version
            apath = xbmc.translatePath( self.main.FolderLanguage.replace( "/resources", "" ).replace( "/language", "" ) )
            addon = Addon( os.path.basename( apath.rstrip( os.sep ) ) )
            version_based = "add-on %s version %s" % ( addon.getAddonInfo( "name" ), addon.getAddonInfo( "version" ) )

        return ET.getComments( version_based,
               self.main.Addon.getSetting( "username" ),
               self.main.Addon.getSetting( "usermail" ),
               self.main.Addon.getAddonInfo( "version" )
               )

    def save_strings( self ):
        """ save strings """
        OK = False
        try:
            comments = self.createComments()
            print comments

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
        f = open( xbmc.translatePath( temp_xml ), "w" )
        f.write( xml )
        f.close()

        # first create backup of original file and copy temp xml to self.current_xml
        backup = "%s/%s/backup/%s_strings.xml" % ( self.main.FolderLanguage, self.main.CurrentLanguage, strftime( '%Y-%m-%d-%H%M' ) )
        if xbmcvfs.copy( self.current_xml, backup ):
            # copy temp xml to self.current_xml
            xml = "%s/%s/strings.xml" % ( self.main.FolderLanguage, self.main.CurrentLanguage )
            #
            if DEBUG: xml = xml.replace( "strings.xml", "strings_test.xml" )
            OK = xbmcvfs.copy( temp_xml, xml )

        return OK
