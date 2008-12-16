
#Modules general
import os
import re
import sys
import urllib

import elementtree.HTMLTreeBuilder as HTB
from StringIO import StringIO


#modules XBMC
import xbmc
import xbmcgui

#modules custom
from utilities import *
from convert_utc_time import set_local_time

#module logger
try:
    logger = sys.modules[ "__main__" ].logger
except:
    import script_log as logger


DIALOG_PROGRESS = xbmcgui.DialogProgress()

#FONCTION POUR RECUPERER LES LABELS DE LA LANGUE.
_ = sys.modules[ "__main__" ].__language__

DIRECT_INFOS = "http://passion-xbmc.org%s/?action=.xml;type=rss;limit="

EXCLUDE_IMGS = re.compile( "smiley|imagesonboard" ).search


def load_infos( url ):
    try:
        html = urllib.urlopen( url )
        source = re.sub( "<!\[CDATA\[|\]\]>", "", html.read() )
        html.close()
        return HTB.parse( StringIO( source ), "utf-8"  ).findall( "channel" )[ 0 ]
    except:
        logger.EXC_INFO( logger.LOG_DEBUG, sys.exc_info() )


class LIST_CONTAINER_150( dict ):
    def __init__( self ):
        self[ 0 ]  = DIRECT_INFOS % ( "", ), "bar.png"
        self[ 1 ]  = DIRECT_INFOS % ( "/releases-et-nouvelles", ), "news.png"
        self[ 2 ]  = DIRECT_INFOS % ( "/xbmc", ), "xbmc.png"
        self[ 3 ]  = DIRECT_INFOS % ( "/scraper-alocine", ), "xbmc.png"
        self[ 4 ]  = DIRECT_INFOS % ( "/pilotage-telecommande", ), "xbmc.png"
        self[ 5 ]  = DIRECT_INFOS % ( "/skins", ), "skin.png"
        self[ 6 ]  = DIRECT_INFOS % ( "/service-importation", ), "skin.png"
        self[ 7 ]  = DIRECT_INFOS % ( "/fiches-des-skins", ), "skin.png"
        self[ 8 ]  = DIRECT_INFOS % ( "/skins-en-projets-et-skins-abandonnes", ), "skin.png"
        self[ 9 ]  = DIRECT_INFOS % ( "/le-coin-des-utilisateurs", ), "script.png"
        self[ 10 ] = DIRECT_INFOS % ( "/le-coin-des-developpeurs", ), "script.png"
        self[ 11 ] = DIRECT_INFOS % ( "/xbmc-live-cd", ), "livecd.png"
        self[ 12 ] = DIRECT_INFOS % ( "/ubuntu", ), "ubuntu.png"
        self[ 13 ] = DIRECT_INFOS % ( "/tutos-ubuntu-et-xbmc", ), "ubuntu.png"
        self[ 14 ] = DIRECT_INFOS % ( "/usb-creator-pour-ubuntu", ), "ubuntu.png"
        self[ 15 ] = DIRECT_INFOS % ( "/windows", ), "windows.png"
        self[ 16 ] = DIRECT_INFOS % ( "/usb-creator-pour-windows", ), "windows.png"
        self[ 17 ] = DIRECT_INFOS % ( "/xbox", ), "xbox.png"
        self[ 18 ] = DIRECT_INFOS % ( "/support-modification-consoles", ), "xbox.png"
        self[ 19 ] = DIRECT_INFOS % ( "/mac-osx-(-leopard-et-tiger)", ), "mac.png"
        self[ 20 ] = DIRECT_INFOS % ( "/usb-creator-pour-mac-intel", ), "mac.png"
        self[ 21 ] = DIRECT_INFOS % ( "/usb-creator-pour-apple-tv", ), "mac.png"
        self[ 22 ] = DIRECT_INFOS % ( "/forks", ), "fork.png"
        self[ 23 ] = DIRECT_INFOS % ( "/plex-pour-mac", ), "fork.png"
        self[ 24 ] = DIRECT_INFOS % ( "/boxeetv", ), "fork.png"
        self[ 25 ] = DIRECT_INFOS % ( "/le-site", ), "site.png"
        self[ 26 ] = DIRECT_INFOS % ( "/charte", ), "site.png"
        self[ 27 ] = DIRECT_INFOS % ( "/cafe", ), "cafe.png"
        self[ 28 ] = DIRECT_INFOS % ( "/membres", ), "membre.png"
        self[ 29 ] = DIRECT_INFOS % ( "/vos-configs", ), "config.png"
        self[ 30 ] = DIRECT_INFOS % ( "/films-et-musique", ), "video.png"
        self[ 31 ] = DIRECT_INFOS % ( "/livres-et-bd", ), "book.png"
        self[ 32 ] = DIRECT_INFOS % ( "/corbeille", ), "trash.png"
        #self[ 33 ] = "http://trac.passion-xbmc.org/index.php?type=rss;action=.xml", "bar.png"


class DirectInfos( xbmcgui.WindowXML ):
    # control id's
    CONTROL_RSS_LIST = 150
    CONTROL_FEEDS_LIST = 191

    def __init__( self, *args, **kwargs ):
        xbmcgui.WindowXML.__init__( self, *args, **kwargs )
        self.list_container_150 = LIST_CONTAINER_150()
        self.mainwin = kwargs[ "mainwin" ]
        self.is_started = True

    def onInit( self ):
        try:
            self._get_settings()
            self._set_skin_colours()
            if self.is_started:
                self.is_started = False

                self.set_list_container_150()
                self.set_list_container_191()
        except:
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )

    def _get_settings( self, defaults=False ):
        """ reads settings """
        self.settings = Settings().get_settings( defaults=defaults )
        #voir les settings il a une erreur avec ~~
        self.topics_limit = self.settings[ "topics_limit" ]
        if ( self.topics_limit == "00" ) or ( "~" in self.topics_limit ):
            self.topics_limit = "500"

    def _set_skin_colours( self ):
        #xbmcgui.lock()
        try:
            self.setProperty( "style_PMIII.HD", ( "", "true" )[ ( self.settings[ "skin_colours_path" ] == "style_PMIII.HD" ) ] )
            self.setProperty( "Skin-Colours-path", self.settings[ "skin_colours_path" ] )
            self.setProperty( "Skin-Colours", ( self.settings[ "skin_colours" ] or get_default_hex_color() ) )
        except:
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )
        #xbmcgui.unlock()

    def set_list_container_150( self ):
        list_container = sorted( self.list_container_150.items(), key=lambda id: id[ 0 ] )
        label2 = ""#not used
        for key, value in list_container:
            label1 = _( 200 + key )
            icone = value[ 1 ]
            self.getControl( self.CONTROL_RSS_LIST ).addItem( xbmcgui.ListItem( label1, label2, icone, icone ) )

    def set_list_container_191( self, rss=0 ):
        self.category = _( 200 + rss )
        DIALOG_PROGRESS.create( _( 199 ), self.category, _( 239 ), _( 110 ) )
        try:
            url, icone = self.list_container_150[ rss ]
            url += self.topics_limit
            root = load_infos( url )
            if root is not None:
                items = root.findall( "item" )

                self.list_infos = list()
                total_items = len( items ) or 1
                diff = ( 100.0 / total_items )
                percent = 0

                self.getControl( self.CONTROL_FEEDS_LIST ).reset()
                for count, item in enumerate( items ):
                    percent += diff
                    imgs = set()
                    slideshow = ""
                    try:
                        title = item.findtext( "title" ).replace( u'\xa0', " " )
                        pubdate = set_local_time( item.findtext( "pubdate" ) )
                        guid = item.findtext( "guid" )
                        _desc = item.find( "description" )
                        description = " ".join( [ ( _desc.text or "" ), ( _desc.tail or "" ) ] ).replace( '&nbsp;', "    " ).replace( "\t", "" ).strip()

                        for txt in _desc.getchildren():
                            _text = " ".join( [ ( txt.text or "" ), ( txt.tail or "" ) ] ).replace( '&nbsp;', "    " ).replace( "\t", "" ).strip()
                            if txt.tag == "br":
                                if txt.text == txt.tail: _text = "\n"
                                else: _text = "\n" + _text
                            elif txt.tag == "b":
                                _text = bold_text( _text )
                            elif txt.tag == "i":
                                _text = italic_text( _text )
                            elif txt.tag in ( "img", "a" ):
                                img = txt.attrib.get( "src", "" ) or txt.attrib.get( "href", "" )
                                if not EXCLUDE_IMGS( img.lower() ) and is_playable_media( img ):
                                    imgs.update( [ img ] )
                                    slideshow = "true"

                            description += _text
                        description = set_xbmc_carriage_return( description.strip( "\r\n" ) )
                        if ( rss == 0 ):
                            # pour la page general seulement
                            description = bold_text( item.findtext( "category" ) ) + "[CR]" + description
                    except:
                        logger.EXC_INFO( logger.LOG_DEBUG, sys.exc_info(), self )
                    else:
                        DIALOG_PROGRESS.update( int( percent ), "Topic: %i / %i" % ( count + 1, total_items, ), title )
                        listitem = xbmcgui.ListItem( title, pubdate, icone, icone )
                        listitem.setProperty( "Topic", description )
                        listitem.setProperty( "Slideshow", slideshow )
                        self.getControl( self.CONTROL_FEEDS_LIST ).addItem( listitem )
                        self.list_infos.append( ( guid, list( imgs ) ) )

                self.setProperty( "Category", self.category )
            else:
                xbmcgui.Dialog().ok( _( 199 ), self.category, _( 240 ) )
        except:
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )
            xbmcgui.Dialog().ok( _( 199 ), self.category, _( 241 ) )
        DIALOG_PROGRESS.close()

    def onFocus( self, controlID ):
        #cette fonction n'est pas utiliser ici, mais dans les XML si besoin
        pass

    def onClick( self, controlID ):
        try:
            if controlID == self.CONTROL_RSS_LIST:
                pos = self.getControl( self.CONTROL_RSS_LIST ).getSelectedPosition()
                if pos >= 0:
                    self.set_list_container_191( pos )
            elif controlID == self.CONTROL_FEEDS_LIST:
                pos = self.getControl( self.CONTROL_FEEDS_LIST ).getSelectedPosition()
                if pos >= 0:
                    self._url_launcher( self.list_infos[ pos ][ 0 ] )
            else:
                pass
        except:
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )

    def _url_launcher( self, url ):
        if ( not SYSTEM_PLATFORM in ( "windows", "linux", "osx" ) ):
            logger.LOG( logger.LOG_INFO, "Unsupported platform: %s", SYSTEM_PLATFORM )
            return
        try:
            if not self.settings[ "web_navigator" ]:
                web_navigator = set_web_navigator( self.settings[ "web_navigator" ] )
                if web_navigator:
                    self.settings[ "web_title" ] = web_navigator[ 0 ] # utiliser dans le dialog settings
                    self.settings[ "web_navigator" ] = web_navigator[ 1 ]
                    OK = Settings().save_settings( self.settings )

            if self.settings[ "win32_exec_wait" ] and ( SYSTEM_PLATFORM == "windows" ):
                # Execute shell commands and freezes XBMC until shell is closed
                cmd = "System.ExecWait"
            else:
                # cette commande semble fonctionel pour linux, osx and windows
                # Execute shell commands
                cmd = "System.Exec"

            command = None
            if ( SYSTEM_PLATFORM == "windows" ):
                command = '%s("%s" "%s")' % ( cmd, self.settings[ "web_navigator" ], url, )
            else:#if ( SYSTEM_PLATFORM == "linux" ):
                # sous linux la vigule pose probleme. pas trouver de solution e.g.:
                # original: http://passion-xbmc.org/index.php/topic,1491.msg10804.html#msg10804
                # ouvert avec linux: http://passion-xbmc.org/index.php/topic
                command = '%s(%s %s)' % ( cmd, self.settings[ "web_navigator" ], url, )

            if command is not None:
                logger.LOG( logger.LOG_DEBUG, "Url Launcher: %s", command )
                selected_label = self._unicode( self.getControl( self.CONTROL_FEEDS_LIST ).getSelectedItem().getLabel() )
                if xbmcgui.Dialog().yesno( self.settings[ "web_title" ], _( 236 ), selected_label, url.split( "/" )[ -1 ], _( 237 ), _( 238 ) ):
                    try:
                        xbmc.executebuiltin( command )
                    except:
                        os.system( "%s %s" % ( web_navigator, url, ) )

            #self._close_dialog()
            #self.mainwin._close_script()

        except:
            logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )

    def _unicode( self, s, encoding="utf-8" ):
        try: s = unicode( s, encoding )
        except: pass
        return s

    def onAction( self, action ):
        #( ACTION_PARENT_DIR, ACTION_PREVIOUS_MENU, ACTION_CONTEXT_MENU, )
        if action in ( 9, 10, 117, ): self._close_dialog()
        # show settings dialog
        if action == 117: self.mainwin._on_action_control( action )
        # show slideshow
        if action == 11:
            try:
                pos = self.getControl( self.CONTROL_FEEDS_LIST ).getSelectedPosition()
                if pos >= 0:
                    Slideshow().playSlideshow( self.list_infos[ pos ][ 1 ] )
            except:
                logger.EXC_INFO( logger.LOG_ERROR, sys.exc_info(), self )

    def _close_dialog( self ):
        #xbmc.sleep( 100 )
        self.close()


def show_direct_infos( mainwin ):
    file_xml = "passion-DirectInfos.xml"
    dir_path = os.getcwd().rstrip( ";" )
    #recupere le nom du skin et si force_fallback est vrai, il va chercher les images du defaultSkin.
    current_skin, force_fallback = getUserSkin()

    w = DirectInfos( file_xml, dir_path, current_skin, force_fallback, mainwin=mainwin )
    w.doModal()
    del w
