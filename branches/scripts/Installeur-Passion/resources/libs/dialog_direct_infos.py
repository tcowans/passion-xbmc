
#Modules general
import os
import sys
import urllib

import elementtree.ElementTree as ET

#modules XBMC
import xbmc
import xbmcgui

#modules custom
from utilities import *


DIRECT_INFOS = "http://passion-xbmc.org%s/?action=.xml;type=rss"

#REPERTOIRE RACINE ( default.py )
CWD = os.getcwd().rstrip( ";" )

#FONCTION POUR RECUPERER LES LABELS DE LA LANGUE.
_ = sys.modules[ "__main__" ].__language__

#COULEUR POUR TITRE DES TOPICS
TITLE_COLOR = "FFFFCC00"


def load_infos( filename ):
    try:
        feed = urllib.urlopen( filename )
        tree = ET.parse( feed )
        feed.close()

        # if you need the root element, use getroot
        root = tree.findall( "channel" )#tree.getroot()

        # delete
        del tree
        return root
    except:
        EXC_INFO( LOG_ERROR, sys.exc_info() )


class LIST_CONTAINER_150( dict ):
    def __init__( self ):
        self[ 0 ]  = DIRECT_INFOS % ( "", )
        self[ 1 ]  = DIRECT_INFOS % ( "/releases-et-nouvelles", )
        self[ 2 ]  = DIRECT_INFOS % ( "/xbmc", )
        self[ 3 ]  = DIRECT_INFOS % ( "/skins", )
        self[ 4 ]  = DIRECT_INFOS % ( "/fiches-des-skins", )
        self[ 5 ]  = DIRECT_INFOS % ( "/le-coin-des-utilisateurs", )
        self[ 6 ]  = DIRECT_INFOS % ( "/le-coin-des-developpeurs", )
        self[ 7 ]  = DIRECT_INFOS % ( "/telechargement-download", )#
        self[ 8 ]  = DIRECT_INFOS % ( "/xbmc-live-cd", )
        self[ 9 ]  = DIRECT_INFOS % ( "/b121", )#
        self[ 10 ] = DIRECT_INFOS % ( "/ubuntu", )
        self[ 11 ] = DIRECT_INFOS % ( "/tutos-ubuntu-et-xbmc", )
        self[ 12 ] = DIRECT_INFOS % ( "/usb-creator-pour-ubuntu", )
        self[ 13 ] = DIRECT_INFOS % ( "/windows", )
        self[ 14 ] = DIRECT_INFOS % ( "/usb-creator-pour-windows", )
        self[ 15 ] = DIRECT_INFOS % ( "/telechargement-download-118", )#
        self[ 16 ] = DIRECT_INFOS % ( "/xbox", )
        self[ 17 ] = DIRECT_INFOS % ( "/support-modification-consoles", )
        self[ 18 ] = DIRECT_INFOS % ( "/telechargement-download-119", )#
        self[ 19 ] = DIRECT_INFOS % ( "/mac-osx-(-leopard-et-tiger)", )
        self[ 20 ] = DIRECT_INFOS % ( "/usb-creator-pour-mac-intel", )
        self[ 21 ] = DIRECT_INFOS % ( "/usb-creator-pour-apple-tv", )
        self[ 22 ] = DIRECT_INFOS % ( "/telechargement-download-120", )#
        self[ 23 ] = DIRECT_INFOS % ( "/forks", )
        self[ 24 ] = DIRECT_INFOS % ( "/le-site", )
        self[ 25 ] = DIRECT_INFOS % ( "/cafe", )
        self[ 26 ] = DIRECT_INFOS % ( "/membres", )
        self[ 27 ] = DIRECT_INFOS % ( "/vos-configs", )
        self[ 28 ] = DIRECT_INFOS % ( "/films-et-musique", )
        self[ 29 ] = DIRECT_INFOS % ( "/livres-et-bd", )
        self[ 30 ] = DIRECT_INFOS % ( "/corbeille", )


class DirectInfos( xbmcgui.WindowXML ):
    def __init__( self, *args, **kwargs ):
        self.list_container_150 = LIST_CONTAINER_150()

    def onInit( self ):
        try: 
            self.getControl( 100 ).setLabel( _( 32199 ) )
            self.set_list_container_150()
            self.text = self._get_text()
            self._set_text()
        except:
            EXC_INFO( LOG_ERROR, sys.exc_info(), self )

    def _set_text( self ):
        xbmcgui.lock()
        try:
            self.getControl( 5 ).reset()
            self.getControl( 5 ).setText( self.text )
        except:
            EXC_INFO( LOG_ERROR, sys.exc_info(), self )
        xbmcgui.unlock()
        self.getControl( 9000 ).setVisible( 0 )

    def _get_text( self, rss=0 ):
        self.getControl( 9000 ).setVisible( 1 )
        full_text = ""
        try:
            root = load_infos( self.list_container_150[ rss ] )
            for elems in root[ 0 ].findall( "item" ):
                category = CONVERT( elems.findtext( "category" ) ).entity_or_charref
                title = CONVERT( bold_text( add_pretty_color( elems.findtext( "title" ), color=TITLE_COLOR ) ) ).entity_or_charref
                pubDate = CONVERT( elems.findtext( "pubDate" ) ).entity_or_charref
                description = strip_off( set_pretty_formatting( elems.findtext( "description" ) ) ).strip( "\n\t" )
                description = CONVERT( description ).entity_or_charref
                try:
                    # "[CR]" est le retour de ligne d'xbmc
                    full_text += "\n".join( [ title, category, pubDate, description ] )
                    full_text += "[CR][CR]".replace( "\n\n", "[CR]" ).replace( "\n", "[CR]" ).replace( "\r\r", "[CR]" ).replace( "\r", "[CR]" )
                except:
                    #EXC_INFO( LOG_ERROR, sys.exc_info(), self )
                    pass
            self.getControl( 100 ).setLabel( "%s - %s" % ( _( 32199 ), _( 32200 + rss ), ) )
            if not root or not full_text:
                return bold_text( _( 32231 ) )
        except:
            EXC_INFO( LOG_ERROR, sys.exc_info(), self )
            return bold_text( _( 32232 ) )
        return full_text

    def set_list_container_150( self ):
        list_container = sorted( self.list_container_150.items(), key=lambda id: id[ 0 ] )
        label2 = ""#not used
        for key, value in list_container:
            label1 = _( 32200 + key )
            self.getControl( 150 ).addItem( xbmcgui.ListItem( label1, label2, "", "" ) )

    def onFocus( self, controlID ):
        #cette fonction n'est pas utiliser ici, mais dans les XML si besoin
        pass

    def onClick( self, controlID ):
        try:
            if controlID == 150:
                pos = self.getControl( 150 ).getSelectedPosition()
                if pos >= 0:
                    self.text = self._get_text( pos )
                    self._set_text()
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


def show_direct_infos():
    file_xml = "passion-DirectInfos.xml"
    #depuis la revision 14811 on a plus besoin de mettre le chemin complet, la racine suffit
    dir_path = CWD #xbmc.translatePath( os.path.join( CWD, "resources" ) ) 
    #recupere le nom du skin et si force_fallback est vrai, il va chercher les images du defaultSkin.
    current_skin, force_fallback = getUserSkin()

    w = DirectInfos( file_xml, dir_path, current_skin, force_fallback )
    w.doModal()
    del w
