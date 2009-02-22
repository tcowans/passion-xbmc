
import os
import sys
import xml.dom.minidom
from traceback import print_exc

import xbmc

try:
    DIRECTORY_DATA = sys.modules[ "__main__" ].SPECIAL_SCRIPT_DATA
except:
    DIRECTORY_DATA = os.path.join( xbmc.translatePath( "P:\\script_data" ), os.path.basename( os.getcwd() ) )
    if not os.path.isdir( DIRECTORY_DATA ): os.makedirs( DIRECTORY_DATA )


class Settings:
    DEFAULT_SETTINGS = os.path.join( os.getcwd(), "resources", "settings.xml" )
    BASE_SETTINGS_PATH = os.path.join( DIRECTORY_DATA, "settings.xml" )

    def __init__( self ):
        """ initializer """
        self.encoding = None
        # create settings dictionary
        self._create_localized_dict()

    def getDefaultsSettings( self, clear_all=False ):
        # create settings dictionary with defaults settings
        if clear_all:
            try: os.remove( self.BASE_SETTINGS_PATH )
            except: pass
        self._create_localized_dict( True )

    def _create_localized_dict( self, defaults=False ):
        """ initializes self.settings and calls _parse_settings_file """
        # settings dictionary
        self.settings = {}
        # add settings
        self._parse_settings_file( self.DEFAULT_SETTINGS )

        # fill-in missing settings with default settings
        if os.path.isfile( self.BASE_SETTINGS_PATH ):
            self._parse_settings_file( self.BASE_SETTINGS_PATH, defaults=defaults )
            if defaults:
                # change settings 
                self.setSetting( "gen-rss_feed", ( "1", "0", )[ ( xbmc.getLanguage().lower() != "french" ) ] )
                self.setSetting( "skin-thumb_size", ( "512", "192" )[ ( os.environ.get( "OS", "xbox" ).lower() == "xbox" ) ] )
        else:
            # change settings 
            self.setSetting( "gen-rss_feed", ( "1", "0", )[ ( xbmc.getLanguage().lower() != "french" ) ] )
            self.setSetting( "skin-thumb_size", ( "512", "192" )[ ( os.environ.get( "OS", "xbox" ).lower() == "xbox" ) ] )
            # copy required file
            #xbmc.executehttpapi( "FileCopy(%s,%s)" % ( self.DEFAULT_SETTINGS, self.BASE_SETTINGS_PATH.encode( "utf-8" ), ) )
            # save default settings
            self.save_settings()

    def _parse_settings_file( self, settings_path, defaults=False ):
        """ adds settings to self.settings dictionary """
        try:
            # load and parse settings.xml file
            doc = xml.dom.minidom.parse( settings_path )
            # set self.encoding for newdoc.writexml( ... ) in save_settings
            if not self.encoding and doc.encoding:
                self.encoding = doc.encoding
            # make sure this is a valid <settings> xml file
            root = doc.documentElement
            if ( not root or root.tagName != "settings" ): raise
            # parse and resolve each <setting id="#" value="#" /> tag
            settings = root.getElementsByTagName( "setting" )
            for setting in settings:
                try:
                    setting_id = setting.getAttribute( "id" ).lower().encode()
                    setting_value = setting.getAttribute( "value" ).encode()
                except:
                    setting_id = repr( setting.getAttribute( "id" ).lower() ).strip( "u'" )
                    setting_value = repr( setting.getAttribute( "value" ) ).strip( "u'" ).replace( "//", "/" ).replace( "\\\\", "\\" )
                # if a valid id add it to self.settings dictionary
                if ( setting_id not in self.settings and setting_value ):
                    self.settings[ setting_id ] = setting_value
                elif not defaults and setting.hasAttribute( "value" ):
                    self.settings[ setting_id ] = setting_value
        except:
            # print the error message to the log and debug window
            xbmc.output( "ERROR: Settings file %s can't be parsed!" % ( settings_path, ) )
            print_exc()
            #if self.BASE_SETTINGS_PATH == settings_path:
            #    try: os.remove( self.BASE_SETTINGS_PATH )
            #    except: pass
            #    self.save_settings()
        # clean-up document object
        try: doc.unlink()
        except: pass

    def save_settings( self ):
        """ save settings """
        try:
            impl = xml.dom.minidom.getDOMImplementation()
            newdoc = impl.createDocument( None, "settings", None )
            top_element = newdoc.documentElement

            for key, value in sorted( self.settings.items(), key=lambda id: id[ 0 ] ):
                tag = newdoc.createElement( "setting" )
                tag.setAttribute( "id", key.lower() )
                tag.setAttribute( "value", value )
                top_element.appendChild( tag )

            try: os.remove( self.BASE_SETTINGS_PATH )
            except: pass
            f = open( self.BASE_SETTINGS_PATH, "w" )
            newdoc.writexml( f, addindent="  ", newl="\n", encoding=self.encoding )
            f.close()
            return True
        except:
            # print the error message to the log and debug window
            xbmc.output( "ERROR: Settings file %s can't be saved!" % ( self.BASE_SETTINGS_PATH, ) )
            print_exc()
            return False

    def setSetting( self, key, value="", save=False ):
        """ set new value setting or create new setting """
        self.settings[ key.lower() ] = value
        if save:
            return self.save_settings()

    def getSetting( self, key, default="Invalid Setting" ):
        """ returns the setting if it exists """
        return self.settings.get( key.lower(), default )
