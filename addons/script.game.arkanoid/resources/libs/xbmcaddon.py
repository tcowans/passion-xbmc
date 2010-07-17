"""
   Module xbmcaddon for XBox
"""

__addonID__ = "xbmc4xbox.addon.library"
__script__  = "xbmcaddon library"
__version__ = "1.0.0"
__author__  = "Frost"


import os
import re
import sys
import __builtin__
from locale import getdefaultlocale

try: lang = getdefaultlocale()[ 0 ][ :2 ].lower()
except: lang = "en"


class Addon( __builtin__.object ):
    """Addon class.

    Addon(id) -- Creates a new Addon class.
    id          : string - id of the addon.
    *Note, You can use the above as a keyword.
    example:
     - self.Addon = xbmcaddon.Addon(id='script.recentlyadded')
    """

    def __init__( self, id=None ):
        self.cwd = os.getcwd()
        self.id = id or os.path.basename( self.cwd )

        try: self.addon_xml = file( os.path.join( self.cwd, "addon.xml" ) ).read()
        except Exception, e: self.addon_xml = "%s\n %s" % ( str( e ), os.path.join( self.cwd, "addon.xml" ) )

        # set type based on extension point or install path
        tp = re.search( 'point="xbmc\.python\.(pluginsource|script|weather|subtitles|lyrics|library)"', self.addon_xml )
        if tp:
            if tp.group( 1 ) == "pluginsource":
                self.type = "plugin"
            else:
                self.type = "script"
        else:
            if "scripts" in self.cwd.lower().replace( "\\", "/" ).split( "/" ):
                self.type = "script"
            elif "plugins" in self.cwd.lower().replace( "\\", "/" ).split( "/" ):
                self.type = "plugin"

        # set plugin type based on install path and set settings builtin
        self.pluginType = None
        self.Settings = None
        if self.type == "plugin":
            spath = self.cwd.lower().replace( "\\", "/" ).split( "/" )
            if "music" in spath:
                self.pluginType = "music"
            elif "pictures" in spath:
                self.pluginType = "plugin_data"
            elif "programs" in spath:
                self.pluginType = "programs"
            elif "video" in spath:
                self.pluginType = "video"
            elif "weather" in spath:
                self.pluginType = "weather"

            import xbmcplugin
            self.Settings = xbmcplugin
        else:
            from xbmc import Settings
            try: self.Settings = Settings( os.getcwd() )
            except Exception, e: print self.id + ": " + str( e )

    def getAddonInfo( self, property ):
        """getAddonInfo(id) -- Returns the value of an addon property as a string.
        id        : string - id of the property that the module needs to access.
        *Note, choices are (author, changelog, description, disclaimer, fanart. icon, id, name, path
                          profile, stars, summary, type, version)
             You can use the above as keywords for arguments.
        example:
         - version = self.Addon.getAddonInfo('version')
        """
        if ( property == "author" ):
            author = re.search( 'provider-name="(.*?)"', self.addon_xml )
            if author: return author.group( 1 )
            if hasattr( sys.modules[ "__main__" ], "__author__" ):
                return sys.modules[ "__main__" ].__author__
        elif ( property == "changelog" ) and os.path.exists( os.path.join( self.cwd, "changelog.txt" ) ):
            return os.path.join( self.cwd, "changelog.txt" )
        elif (property == "description" ):
            desc = re.search( '<description lang="%s">(.*?)</description>' % lang, self.addon_xml, re.S )
            if desc: return desc.group( 1 )
            desc = re.search( '<description>(.*?)</description>', self.addon_xml, re.S )
            if desc: return desc.group( 1 )
        elif ( property == "disclaimer" ):
            disc = re.search( '<disclaimer lang="%s">(.*?)</disclaimer>' % lang, self.addon_xml, re.S )
            if disc: return disc.group( 1 )
            disc = re.search( '<disclaimer>(.*?)</disclaimer>', self.addon_xml, re.S )
            if disc: return disc.group( 1 )
        elif ( property == "fanart" ) and os.path.exists( os.path.join( self.cwd, "fanart.jpg" ) ):
            return os.path.join( self.cwd, "fanart.ipg" )
        elif ( property == "icon" ):
            if os.path.exists( os.path.join( self.cwd, "icon.png" ) ):
                return os.path.join( self.cwd, "icon.png" )
            if os.path.exists( os.path.join( self.cwd, "default.tbn" ) ):
                return os.path.join( self.cwd, "default.tbn" )
        elif ( property == "id" ):
            ID = re.search( 'id="(.*?)"', self.addon_xml )
            if ID: return ID.group( 1 )
            if hasattr( sys.modules[ "__main__" ], "__addonID__" ):
                return sys.modules[ "__main__" ].__addonID__
        elif ( property == "name" ):
            name = re.search( ' name="(.*?)"', self.addon_xml )
            if name: return name.group( 1 )
            if hasattr( sys.modules[ "__main__" ], "__script__" ):
                return sys.modules[ "__main__" ].__script__
        elif ( property == "path" ):
            return self.cwd
        elif ( property == "profile" ):
            path = "special://profile/"
            if self.type == "script":
                path += "script_data/"
            elif self.type == "plugin":
                path += "plugin_data/%s/" % self.pluginType
            else:
                path += "addon_data/"
            path += "%s/" % os.path.basename( self.cwd )
            return path
        elif ( property == "stars" ):
            return 0
        elif ( property == "summary" ):
            summ = re.search( '<summary lang="%s">(.*?)</summary>' % lang, self.addon_xml, re.S )
            if summ: return summ.group( 1 )
            summ = re.search( '<summary>(.*?)</summary>', self.addon_xml, re.S )
            if summ: return summ.group( 1 )
        elif ( property == "type" ):
            type = re.search( 'point="(.*?)"', self.addon_xml )
            if type: return type.group( 1 )
            else: return self.type.title()
        elif ( property == "version" ):
            version = re.search( '<addon.*?version="(.*?)"', self.addon_xml, re.S )
            if version: return version.group( 1 )
            if hasattr( sys.modules[ "__main__" ], "__version__" ):
                return sys.modules[ "__main__" ].__version__

        return ""

    def getLocalizedString( self, str_id ):
        """getLocalizedString(id) -- Returns an addon's localized 'unicode string'.
        id             : integer - id# for string you want to localize.
        *Note, You can use the above as keywords for arguments.
        example:
         - locstr = self.Addon.getLocalizedString(id=6)
        """
        locstr = ""
        try: locstr = xbmc.Language( self.cwd ).getLocalizedString( str_id )
        except: pass
        if not bool( locstr ):
            locstr = xbmc.getLocalizedString( str_id )
        return locstr

    def getSetting( self, key ):
        """getSetting(id) -- Returns the value of a setting as a unicode string.
        id        : string - id of the setting that the module needs to access.
        *Note, You can use the above as a keyword.
        example:
          - apikey = self.Addon.getSetting('apikey')
        """
        if self.Settings:
            return self.Settings.getSetting( key )

    def openSettings( self ):
        """openSettings() -- Opens this scripts settings dialog.
        example:
          - self.Settings.openSettings()
        """
        if self.Settings:
            try: self.Settings.openSettings( sys.argv[ 0 ] )
            except: self.Settings.openSettings()

    def setSetting( self, key, value ):
        """setSetting(id, value) -- Sets a script setting.
        id        : string - id of the setting that the module needs to access.
        value     : string or unicode - value of the setting.
        *Note, You can use the above as keywords for arguments.
        example:
          - self.Settings.setSetting(id='username', value='teamxbmc')
        """
        if self.Settings:
            self.Settings.setSetting( key, value )



if  __name__ == "__main__":
    __addon__ = Addon( id=__addonID__ )
    print __addon__.getLocalizedString( 6 )
    print repr( __addon__.getSetting( 'apikey' ) ), __addon__.Settings
    for property in ("author", "changelog", "description", "disclaimer", "fanart", "icon", "id", "name", "path", "profile", "stars", "summary", "type", "version"):
        print property + ": " + str( __addon__.getAddonInfo( property ) )
