
#Modules general
import os
import re
import sys
import urllib

import elementtree.ElementTree as ET

#modules XBMC
import xbmc
import xbmcgui

#modules custom
from utilities import *
from convert_utc_time import set_local_time


DIALOG_PROGRESS = xbmcgui.DialogProgress()

DIRECT_INFOS = "http://passion-xbmc.org%s/?action=.xml;type=rss;limit="

#REPERTOIRE RACINE ( default.py )
CWD = os.getcwd().rstrip( ";" )

#FONCTION POUR RECUPERER LES LABELS DE LA LANGUE.
_ = sys.modules[ "__main__" ].__language__

'''
def load_infos( url ):
    """
    a verifier plus tard, autre chose a faire :) frost 20-11-08
    ERROR: in parse, 'tree = ET.parse( feed )' - undefined entity &ecirc;: line XX, column XX
    """
    try:
        feed = urllib.urlopen( url )
        tree = ET.parse( feed )
        feed.close()

        # if you need the root element, use getroot
        root = tree.findall( "channel" )#tree.getroot()

        # delete
        del tree
        return root
    except:
        EXC_INFO( LOG_ERROR, sys.exc_info() )
'''
def load_infos( url, general=False ):
    list_infos = list()
    html = get_html_source( url )
    items = re.compile( "<item>(.*?)</item>", re.DOTALL ).findall( html )
    total_items = len( items ) or 1
    percent = 0
    diff = int( 100.0 / total_items )
    for count, item in enumerate( items ):
        try:
            title = re.findall( "<title>.*\\[(.*?)\\].*</title>", item )[ 0 ]
            pubDate = re.findall( "<pubDate>(.*?)</pubDate>", item )[ 0 ]
            category = re.findall( "<category>.*\\[(.*?)\\].*</category>", item )[ 0 ]
            description = re.findall( "<description>.*\\[(.*?)\\].*</description>", item, re.DOTALL )[ 0 ]
            percent += diff
        except:
            EXC_INFO( LOG_ERROR, sys.exc_info() )
        else:
            DIALOG_PROGRESS.update( percent, "RSS: %i / %i" % ( count + 1, total_items, ), title )
            try:
                category = bold_text( CONVERT( category ).entity_or_charref ) + "[CR]"
                title = CONVERT( title ).entity_or_charref #bold_text( )
                pubDate = CONVERT( pubDate ).entity_or_charref
                description = strip_off( set_pretty_formatting( description ) ).strip( "\n\t" )
                description = CONVERT( description ).entity_or_charref
                if not general: item = ( title, pubDate, description )
                else:  item = ( title, pubDate, category + description )
                list_infos.append( item )
            except:
                EXC_INFO( LOG_ERROR, sys.exc_info() )
    return list_infos


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
        self.rss_feed = kwargs[ "mainwin" ].rss_feed
        self.list_container_150 = LIST_CONTAINER_150()
        self.feeds_limit = "5"

    def onInit( self ):
        try:
            self._get_settings()
            self._set_skin_colours()
            self.set_list_container_150()
            self.set_list_container_191()
        except:
            EXC_INFO( LOG_ERROR, sys.exc_info(), self )

    def _get_settings( self, defaults=False ):
        """ reads settings """
        self.settings = Settings().get_settings( defaults=defaults )
        self.feeds_limit = self.settings[ "feeds_limit" ]
        if self.feeds_limit == "00": self.feeds_limit = "500"

    def _set_skin_colours( self ):
        xbmcgui.lock()
        try:
            #sa marche lol :o trop cool on pourra faire une fonction dans les settings pour couleurs du theme
            self.setProperty( "Skin-Colours-path", self.settings[ "skin_colours_path" ] )
            self.setProperty( "Skin-Colours", ( self.settings[ "skin_colours" ] or self._get_default_hex_color() ) )
            #print xbmc.getInfoLabel( "Container.Property(Skin-Colours)" )
        except:
            EXC_INFO( LOG_ERROR, sys.exc_info(), self )
        xbmcgui.unlock()

    def _get_default_hex_color( self ):
        try:
            default_hex_color = dict( getSkinColors() ).get( "default", "FFFFFFFF" )
        except:
            EXC_INFO( LOG_ERROR, sys.exc_info(), self )
            default_hex_color = "FFFFFFFF"
        return default_hex_color

    def _unicode( self, s, encoding="utf-8" ):
        try: s = unicode( s, encoding )
        except: pass
        return s

    def set_list_container_191( self, rss=0 ):
        #xbmcgui.lock()
        self.category = _( 200 + rss )
        DIALOG_PROGRESS.create( _( 0 ), "RSS: 0 / %s" % ( self.feeds_limit, ), self.category )
        try:
            url, icone = self.list_container_150[ rss ]
            url += self.feeds_limit
            list_infos = load_infos( url, ( rss == 0 ) )
            self.getControl( self.CONTROL_FEEDS_LIST ).reset()
            for title, pubDate, description in list_infos:
                title = self._unicode( set_xbmc_carriage_return( title ) )
                pubDate = set_local_time( pubDate )
                description = self._unicode( set_xbmc_carriage_return( description ) )
                try:
                    #icone = os.path.join(os.getcwd().replace( ";", "" ), "default.tbn")
                    listitem = xbmcgui.ListItem( title, pubDate, icone, icone )
                    listitem.setProperty( "Topic", description )
                    self.getControl( self.CONTROL_FEEDS_LIST ).addItem( listitem )
                except:
                    #EXC_INFO( LOG_ERROR, sys.exc_info(), self )
                    pass
            self.setProperty( "Category", self.category )
        except:
            EXC_INFO( LOG_ERROR, sys.exc_info(), self )
        #xbmcgui.unlock()
        DIALOG_PROGRESS.close()

    def set_list_container_150( self ):
        list_container = sorted( self.list_container_150.items(), key=lambda id: id[ 0 ] )
        label2 = ""#not used
        for key, value in list_container:
            label1 = _( 200 + key )
            icone = value[ 1 ]
            self.getControl( self.CONTROL_RSS_LIST ).addItem( xbmcgui.ListItem( label1, label2, icone, icone ) )

    def onFocus( self, controlID ):
        #cette fonction n'est pas utiliser ici, mais dans les XML si besoin
        pass

    def onClick( self, controlID ):
        try:
            if controlID == self.CONTROL_RSS_LIST:
                pos = self.getControl( self.CONTROL_RSS_LIST ).getSelectedPosition()
                if pos >= 0:
                    self.set_list_container_191( pos )
            else:
                pass
        except:
            EXC_INFO( LOG_ERROR, sys.exc_info(), self )

    def onAction( self, action ):
        #( ACTION_PARENT_DIR, ACTION_PREVIOUS_MENU, ACTION_CONTEXT_MENU, )
        if action in ( 9, 10, 117 ): self._close_dialog()

    def _close_dialog( self ):
        xbmc.sleep( 100 )
        self.close()


def show_direct_infos( mainwin ):
    file_xml = "passion-DirectInfos.xml"
    #depuis la revision 14811 on a plus besoin de mettre le chemin complet, la racine suffit
    dir_path = CWD #xbmc.translatePath( os.path.join( CWD, "resources" ) ) 
    #recupere le nom du skin et si force_fallback est vrai, il va chercher les images du defaultSkin.
    current_skin, force_fallback = getUserSkin()

    w = DirectInfos( file_xml, dir_path, current_skin, force_fallback, mainwin=mainwin )
    w.doModal()
    del w
