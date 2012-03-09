
import os
import sys
from traceback import print_exc

import xbmc
import xbmcgui
import xbmcvfs
from xbmcaddon import Addon

Addon = Addon( "script.xbmc.intro.movie" )


class DialogSelect( xbmcgui.WindowXMLDialog ):
    def __init__( self, *args, **kwargs ):
        pass

    def onInit( self ):
        self.getControl( 1 ).setLabel( "XBMC Intro Movie" )
        try:
            self.control_list = self.getControl( 6 )
            self.getControl( 5 ).setNavigation( self.control_list, self.control_list, self.control_list, self.control_list )
            self.getControl( 3 ).setEnabled( 0 )
            self.getControl( 3 ).setVisible( 0 )
        except:
            self.control_list = self.getControl( 3 )
            print_exc()

        try: self.getControl( 5 ).setLabel( "Cancel" )
        except: print_exc()

        intros_dir   = os.path.join( Addon.getAddonInfo( "path" ), "resources", "intros" )
        previews_dir = os.path.join( Addon.getAddonInfo( "path" ), "resources", "previews" )

        listitems = []
        cur = Addon.getSetting( "intro" )
        for intro in os.listdir( intros_dir ):
            name, ext = os.path.splitext( intro )
            listitem = xbmcgui.ListItem( intro, "", "DefaultVideo.png" )
            if cur == intro: listitem.setProperty( "Addon.Summary", "Current Intro" )
            preview = os.path.join( previews_dir, name + ".jpg" )
            if xbmcvfs.exists( preview ): listitem.setIconImage( preview )
            listitems.append( listitem )

        listitem = xbmcgui.ListItem( "Random", "", "DefaultAddonVisualization.png" )
        if cur == "Random": listitem.setProperty( "Addon.Summary", "Current Intro" )
        listitems.append( listitem )

        self.control_list.reset()
        self.control_list.addItems( listitems )
        self.setFocus( self.control_list )

    def onClick( self, controlID ):
        try:
            if controlID in [ 3, 6 ]:
                intro = self.control_list.getSelectedItem().getLabel()
                if intro: Addon.setSetting( "intro", intro )
                self._close_dialog()

            elif controlID == 5:
                self._close_dialog()
        except:
            print_exc()

    def onFocus( self, controlID ):
        pass

    def onAction( self, action ):
        if action == 92:
            self._close_dialog()

    def _close_dialog( self ):
        self.close()
        xbmc.sleep( 500 )


def toggle_splash( toggle ):
    from xml.dom.minidom import parseString
    try:
        advancedsettings = xbmc.translatePath( "special://userdata/advancedsettings.xml" )

        try: str_xml = open( advancedsettings ).read()
        except: str_xml = "<advancedsettings></advancedsettings>"

        if "<splash>" not in str_xml:
            str_xml = str_xml.replace( "ettings>", "ettings>\n  <splash>false</splash>\n", 1 )

        # parse source
        dom = parseString( str_xml )

        splash = dom.getElementsByTagName( "splash" )
        if splash:
            splash = splash[ 0 ]
            toggle = ( "true", "false" )[ toggle == "true" ]
            splash.firstChild.nodeValue = toggle

        str_xml = dom.toxml( "UTF-8"  ).replace( "?>", ' standalone="yes"?>\n', 1 )
        dom.unlink()

        bak = advancedsettings + ".bak"
        file( bak, "w" ).write( str_xml )
        OK = xbmcvfs.copy( bak, advancedsettings )
    except:
        print_exc()
    return toggle


def Main( settingID=None ):
    setfocusid = 200
    if settingID == "splash":
        toggle = toggle_splash( Addon.getSetting( "splash" ) )
        Addon.setSetting( "splash", toggle )
        xbmc.sleep( 500 )
        setfocusid = ( 107, 108 )[ toggle == "false" ]

    elif settingID == "intro":
        w = DialogSelect( "DialogSelect.xml", Addon.getAddonInfo( "path" ) )
        w.doModal()
        del w
        setfocusid = 101

    xbmc.executebuiltin( "Addon.openSettings(script.xbmc.intro.movie)" )
    xbmc.executebuiltin( "SetFocus(200)" )
    xbmc.executebuiltin( "SetFocus(%i)" % setfocusid )


def service():
    from xml.dom.minidom import parseString
    has_splash = "true"
    dom = None
    try:
        dom = parseString( open( xbmc.translatePath( "special://userdata/advancedsettings.xml" ) ).read() )
        has_splash = dom.getElementsByTagName( "splash" )[ 0 ].firstChild.nodeValue
    except:
        print_exc()
    if dom: dom.unlink()
    if Addon.getSetting( "splash" ) != has_splash:
        Addon.setSetting( "splash", has_splash )



if __name__=="__main__":
    service()
